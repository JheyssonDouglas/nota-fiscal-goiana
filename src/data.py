import re
import unicodedata
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "indice", "sorteio", "data_sorteio", "posicao",
    "bilhete", "nome", "municipio", "valor"
]

def normalize_name(value):
    value = str(value or "").strip().upper()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value)

def parse_brazilian_number(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip().replace("R$", "").replace(" ", "")
    if not raw:
        return 0.0
    # Em caso de célula contaminada por texto, aproveita apenas o número final
    # para permitir a leitura e sinalizar a anomalia em uma etapa de qualidade.
    match = re.search(r"[-+]?[0-9][0-9.]*[,]?[0-9]*$", raw)
    if not match:
        raise ValueError(f"Valor monetário inválido: {value!r}")
    raw = match.group(0).replace(".", "").replace(",", ".")
    return float(raw)

def format_brl(value):
    formatted = f"{float(value):,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")

def load_data(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    df = df[REQUIRED_COLUMNS].copy()
    for col in ["indice", "sorteio", "posicao", "bilhete"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    df["valor"] = df["valor"].map(parse_brazilian_number)
    df["data_sorteio"] = pd.to_datetime(df["data_sorteio"], dayfirst=True, errors="coerce")
    df["nome"] = df["nome"].astype(str).str.strip()
    df["municipio"] = df["municipio"].astype(str).str.strip()
    df["nome_normalizado"] = df["nome"].map(normalize_name)
    return df
