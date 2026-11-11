"""
Etapa 2: atualizador incremental dos resultados oficiais.

Este primeiro esqueleto NÃO altera o CSV. A extração automática dos PDFs
será habilitada depois de validar os diferentes layouts dos documentos,
inclusive páginas em que dois números de sorteio aparecem na mesma linha.
"""
from pathlib import Path
import pandas as pd

BASE = Path("data/resultados_nota_fiscal_goiana.csv")
CHAVE = ["sorteio", "posicao", "bilhete"]

def main():
    if not BASE.exists():
        raise FileNotFoundError(f"Base não encontrada: {BASE}")
    df = pd.read_csv(BASE, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    print(f"Base carregada: {len(df)} registros")
    print(f"Último número de sorteio na base: {pd.to_numeric(df['sorteio'], errors='coerce').max()}")
    print("Atualizador em modo seguro: nenhuma alteração foi feita.")
    print("Próxima etapa: descoberta dos PDFs, extração e validação antes da gravação.")

if __name__ == "__main__":
    main()
