"""Shared dataset provenance and explicit Week 1 preprocessing."""
from pathlib import Path
import hashlib
import urllib.request
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / 'data/raw/titanic.csv'
URL = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
SHA256 = '81787d320d7f7b03df935e91de8bd19e11d45c5bbcab86ef4d4a76dc91b7d4f2'

def load_raw():
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=30) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest() != SHA256:
            raise ValueError('Upstream data changed. Review and version the new snapshot first.')
        RAW.write_bytes(payload)
    if hashlib.sha256(RAW.read_bytes()).hexdigest() != SHA256:
        raise ValueError('Local raw CSV differs from the documented snapshot.')
    df = pd.read_csv(RAW)
    if df.shape != (891, 15) or not df.survived.isin([0, 1]).all():
        raise ValueError('Unexpected Titanic data structure.')
    return df

def clean_for_eda(raw):
    """Retain all passengers; preserve observed ages for inference."""
    df = raw.drop(columns='deck').copy()
    df['age_observed'] = df['age']
    df['age_missing'] = df['age'].isna()
    medians = df.groupby(['pclass', 'sex'])['age'].transform('median')
    df['age'] = df['age'].fillna(medians).fillna(df['age'].median())
    for col in ['embarked', 'embark_town']:
        df[col] = df[col].fillna(df[col].mode()[0])
    df['family_size'] = df['sibsp'] + df['parch'] + 1
    # Do not drop repeated profiles: this source has no passenger identity fields.
    return df
