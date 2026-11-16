"""
Atualizador incremental da Nota Fiscal Goiana.

Exemplo:
    python scripts_atualizar_sorteios.py --sorteios 85 86
    python scripts_atualizar_sorteios.py --sorteios 121
    python scripts_atualizar_sorteios.py --sorteios 85 86 --dry-run

Os PDFs devem estar em data/raw/ e seguir o padrão:
    Resultado_Sorteio_85.pdf
    Resultado_Sorteio_86.pdf
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parent
BASE_PADRAO = ROOT / "data" / "resultados_nota_fiscal_goiana.csv"
RAW_PADRAO = ROOT / "data" / "raw"
COLUNAS = [
    "indice", "sorteio", "data_sorteio", "posicao",
    "bilhete", "nome", "municipio", "valor",
]
CHAVE = ["sorteio", "posicao", "bilhete"]


def limpar_texto(valor: object) -> str:
    if valor is None:
        return ""
    return re.sub(r"\s+", " ", str(valor)).strip()


def extrair_data(pdf: pdfplumber.PDF) -> str:
    """Obtém a data do cabeçalho do PDF, sem estimar datas."""
    for pagina in pdf.pages:
        texto = pagina.extract_text() or ""
        match = re.search(
            r"(\d{2}/\d{2}/\d{4})", texto
        )
        if match:
            data = datetime.strptime(match.group(1), "%d/%m/%Y")
            return data.strftime("%d/%m/%Y")
    raise ValueError("Não foi possível identificar a data no cabeçalho do PDF.")


def extrair_registros(pdf_path: Path, numero_sorteio: int) -> pd.DataFrame:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    registros = []
    with pdfplumber.open(pdf_path) as pdf:
        data_sorteio = extrair_data(pdf)
        for pagina_num, pagina in enumerate(pdf.pages, start=1):
            for tabela in pagina.extract_tables():
                for linha in tabela:
                    if not linha or len(linha) < 5:
                        continue

                    posicao_txt = limpar_texto(linha[0])
                    if not posicao_txt.isdigit():
                        continue

                    posicao = int(posicao_txt)
                    bilhete = re.sub(r"\D", "", limpar_texto(linha[1]))
                    nome = limpar_texto(linha[2]).upper()
                    municipio = limpar_texto(linha[3]).upper()
                    valor_txt = limpar_texto(linha[4])

                    if not bilhete or not nome or not municipio or not valor_txt:
                        raise ValueError(
                            f"Linha incompleta no sorteio {numero_sorteio}, "
                            f"página {pagina_num}, posição {posicao}."
                        )

                    # Mantém o padrão brasileiro no CSV (ex.: 1.000,00).
                    valor_num = float(
                        valor_txt.replace(".", "").replace(",", ".")
                    )
                    if valor_num <= 0:
                        raise ValueError(
                            f"Valor inválido no sorteio {numero_sorteio}, "
                            f"posição {posicao}: {valor_txt}"
                        )
                    valor_formatado = f"{valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    registros.append({
                        "sorteio": str(numero_sorteio),
                        "data_sorteio": data_sorteio,
                        "posicao": str(posicao),
                        "bilhete": bilhete,
                        "nome": nome,
                        "municipio": municipio,
                        "valor": valor_formatado,
                    })

    if not registros:
        raise ValueError(f"Nenhum registro foi extraído do PDF {pdf_path.name}.")

    df = pd.DataFrame(registros)
    df = df.sort_values("posicao", key=lambda s: s.astype(int)).reset_index(drop=True)

    posicoes = df["posicao"].astype(int).tolist()
    esperadas = list(range(1, len(posicoes) + 1))
    if posicoes != esperadas:
        raise ValueError(
            f"Sorteio {numero_sorteio}: posições ausentes ou duplicadas. "
            f"Encontradas: {len(posicoes)} linhas; sequência não contínua."
        )

    if df.duplicated(["sorteio", "posicao", "bilhete"]).any():
        raise ValueError(f"Sorteio {numero_sorteio}: há chaves duplicadas no PDF.")

    return df


def ler_base(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(
            f"Base CSV não encontrada: {caminho}\n"
            "Confirme se o arquivo está em data/resultados_nota_fiscal_goiana.csv."
        )

    df = pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    faltantes = [col for col in COLUNAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"A base não contém as colunas obrigatórias: {faltantes}")

    return df[COLUNAS].copy()


def atualizar(base: pd.DataFrame, novos: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    base = base.copy()
    novos = novos.copy()

    for coluna in CHAVE:
        base[coluna] = base[coluna].astype(str).str.strip()
        novos[coluna] = novos[coluna].astype(str).str.strip()

    chaves_existentes = set(map(tuple, base[CHAVE].to_numpy()))
    mascara_novos = [
        tuple(linha) not in chaves_existentes
        for linha in novos[CHAVE].to_numpy()
    ]
    somente_novos = novos.loc[mascara_novos].copy()

    # Se a chave já existe, mas os demais dados divergem, não sobrescreve:
    # sinaliza para conferência manual.
    existentes_por_chave = base.drop_duplicates(CHAVE).set_index(CHAVE)
    for _, linha in novos.iterrows():
        chave = tuple(linha[c] for c in CHAVE)
        if chave in existentes_por_chave.index:
            antigo = existentes_por_chave.loc[chave]
            for campo in ["data_sorteio", "nome", "municipio", "valor"]:
                if str(antigo[campo]).strip() != str(linha[campo]).strip():
                    raise ValueError(
                        f"Conflito para a chave {chave}: campo '{campo}' "
                        f"difere entre PDF e CSV. Nada foi gravado."
                    )

    if somente_novos.empty:
        return base, 0

    maior_indice = pd.to_numeric(base["indice"], errors="coerce").max()
    proximo_indice = int(maior_indice) + 1 if pd.notna(maior_indice) else 1
    somente_novos.insert(
        0, "indice",
        [str(i) for i in range(proximo_indice, proximo_indice + len(somente_novos))]
    )

    resultado = pd.concat([base, somente_novos[COLUNAS]], ignore_index=True)
    return resultado[COLUNAS], len(somente_novos)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrai sorteios de PDFs oficiais e atualiza o CSV histórico."
    )
    parser.add_argument(
        "--sorteios", nargs="+", type=int, required=True,
        help="Um ou mais números de sorteio. Ex.: --sorteios 85 86",
    )
    parser.add_argument(
        "--base", type=Path, default=BASE_PADRAO,
        help="Caminho do CSV (padrão: data/resultados_nota_fiscal_goiana.csv).",
    )
    parser.add_argument(
        "--pdf-dir", type=Path, default=RAW_PADRAO,
        help="Pasta dos PDFs (padrão: data/raw).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Valida e mostra o resultado sem alterar o CSV.",
    )
    args = parser.parse_args()

    numeros = sorted(set(args.sorteios))
    if any(n <= 0 for n in numeros):
        parser.error("Os números dos sorteios devem ser positivos.")

    try:
        base = ler_base(args.base)
        extraidos = []

        # Extrai e valida TODOS os PDFs antes de qualquer gravação.
        for numero in numeros:
            pdf_path = args.pdf_dir / f"Resultado_Sorteio_{numero}.pdf"
            df_sorteio = extrair_registros(pdf_path, numero)
            extraidos.append(df_sorteio)
            print(
                f"Sorteio {numero}: {len(df_sorteio)} registros extraídos "
                f"(data {df_sorteio['data_sorteio'].iloc[0]})."
            )

        novos = pd.concat(extraidos, ignore_index=True)
        if novos.duplicated(CHAVE).any():
            raise ValueError("Há chaves duplicadas entre os PDFs informados.")

        atualizada, quantidade = atualizar(base, novos)
        print(f"\nBase atual: {len(base):,} registros.")
        print(f"Registros novos: {quantidade:,}.")
        print(f"Registros já existentes/ignorados: {len(novos) - quantidade:,}.")
        print(f"Total após atualização: {len(atualizada):,}.")

        if args.dry_run:
            print("\nDRY-RUN: validação concluída. Nenhum arquivo foi alterado.")
            return 0

        args.base.parent.mkdir(parents=True, exist_ok=True)
        backup_dir = args.base.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{args.base.stem}_{timestamp}{args.base.suffix}"
        shutil.copy2(args.base, backup_path)

        # Grava em arquivo temporário e substitui o CSV só após concluir a escrita.
        temporario = args.base.with_suffix(args.base.suffix + ".tmp")
        atualizada.to_csv(
            temporario, index=False, encoding="utf-8-sig",
            lineterminator="\n"
        )
        temporario.replace(args.base)

        print(f"\nCSV atualizado com sucesso: {args.base}")
        print(f"Backup criado: {backup_path}")
        return 0

    except Exception as erro:
        print(f"\nERRO: {erro}", file=sys.stderr)
        print("A base CSV não foi alterada.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())