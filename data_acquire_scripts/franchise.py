import pandas as pd
import re
from rapidfuzz import fuzz

INPUT_CSV = "steam_games.csv"
OUTPUT_CSV = "steam_games_with_franchise.csv"

# ---------------------------------------------------
# Normalização para análise
# ---------------------------------------------------

def normalize(text):
    text = str(text)

    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)

    text = re.sub(
        r"(game of the year edition|goty edition|definitive edition|ultimate edition|complete edition|remastered|redux)",
        "",
        text,
        flags=re.I
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------
# Extrai candidato a franquia
# ---------------------------------------------------

ROMAN_NUMERALS = (
    "i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv"
)

def extract_franchise(title):

    original = normalize(title)

    # Mass Effect: Andromeda
    if ":" in original:
        return original.split(":")[0].strip()

    # Halo - Reach
    if " - " in original:
        return original.split(" - ")[0].strip()

    # Civilization VI
    candidate = re.sub(
        rf"\s+({ROMAN_NUMERALS})$",
        "",
        original,
        flags=re.I
    )

    # Fallout 4
    candidate = re.sub(
        r"\s+\d+$",
        "",
        candidate
    )

    candidate = re.sub(
        rf"\s+({ROMAN_NUMERALS}|\d+):.*$",
        "",
        original,
        flags=re.I
    )
    
    if candidate != original:
        return candidate.strip()


# ---------------------------------------------------
# Carregar CSV
# ---------------------------------------------------

df = pd.read_csv(INPUT_CSV)

df = df[df["name"].notna()]

df["franchise_candidate"] = df["name"].apply(extract_franchise)

# ---------------------------------------------------
# Agrupar candidatos semelhantes
# ---------------------------------------------------

canonical = {}

franchises = (
    df["franchise_candidate"]
    .dropna()
    .unique()
)

franchises = sorted(
    franchises,
    key=len,
    reverse=True
)

for franchise in franchises:

    matched = False

    for canon in canonical:

        score = fuzz.ratio(
            franchise.lower(),
            canon.lower()
        )

        if score >= 95:
            canonical[franchise] = canon
            matched = True
            break

    if not matched:
        canonical[franchise] = franchise

df["Franchise"] = (
    df["franchise_candidate"]
    .map(canonical)
)

# ---------------------------------------------------
# Salvar resultado final
# ---------------------------------------------------

result = df[
    ["appid", "name", "Franchise"]
].rename(
    columns={
        "name": "Title"
    }
)

result.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print(f"Arquivo salvo: {OUTPUT_CSV}")
print(f"Total de registros: {len(result):,}")