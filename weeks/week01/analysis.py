"""Reconstructed Week 1 acquisition, cleaning and EDA with documented fixes."""
from pathlib import Path
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src'))
from titanic_data import load_raw, clean_for_eda

raw = load_raw()
df = clean_for_eda(raw)
out = Path(__file__).resolve().parent / 'outputs'
out.mkdir(exist_ok=True)
processed = REPO / 'data/processed/titanic_eda.csv'
processed.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(processed, index=False)
raw.describe(include='all').to_csv(out / 'raw_summary.csv')
raw.isna().sum().rename('missing_count').to_csv(out / 'missing_values.csv')
audit = {'raw_rows': len(raw), 'retained_rows': len(df),
         'raw_duplicate_profiles': int(raw.duplicated().sum()),
         'rows_removed': 0, 'missing_ages': int(raw.age.isna().sum()),
         'survivors': int(raw.survived.sum()),
         'survival_rate': float(raw.survived.mean()),
         'policy': 'Identical profiles are not verified duplicate passengers.'}
(out / 'audit.json').write_text(json.dumps(audit, indent=2))
sns.set_theme(style='whitegrid')
COLORS = {0: '#B34A45', 1: '#28855D'}
def save(name):
    plt.tight_layout()
    plt.savefig(out / name, dpi=160, bbox_inches='tight')
    plt.close()
plt.figure(figsize=(11, 4))
sns.heatmap(raw.isna(), cbar=False, yticklabels=False, cmap=['#f4f4f4', '#35668B'])
plt.title('Missing values in the raw passenger data')
save('01_missing_values.png')
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=raw, x='pclass', hue='survived', palette=COLORS, ax=ax[0])
rates = raw.groupby('pclass').survived.mean().mul(100)
ax[1].bar(rates.index, rates, color='#35668B')
ax[1].set(xticks=[1,2,3], ylabel='Survived (%)', xlabel='Passenger class', ylim=(0,100))
ax[0].set_title('Survival counts by class'); ax[1].set_title('Survival percentages by class')
save('02_survival_by_class.png')
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
sns.histplot(data=raw, x='age', hue='survived', palette=COLORS, bins=25, ax=ax[0])
sns.histplot(data=raw.assign(log_fare=np.log1p(raw.fare)), x='log_fare',
             hue='survived', palette=COLORS, bins=25, ax=ax[1])
ax[0].set_title('Recorded ages only'); ax[1].set_title('Fare transformed with log1p')
save('03_age_and_fare.png')
cols = ['survived','pclass','age','sibsp','parch','fare','family_size']
plt.figure(figsize=(8, 6))
corr = df[cols].corr()
sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool)), annot=True,
            fmt='.2f', cmap='RdBu_r', vmin=-1, vmax=1)
plt.title('Numeric correlations using imputed ages for EDA')
save('04_correlations.png')
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(data=raw, x='pclass', y='age', hue='sex', ax=ax[0])
sns.boxplot(data=raw, x='pclass', y='fare', hue='survived', palette=COLORS, ax=ax[1])
ax[0].set_title('Observed age by class and sex'); ax[1].set_title('Fare outliers retained')
save('05_boxplots.png')
print('Week 1 complete:', audit)
