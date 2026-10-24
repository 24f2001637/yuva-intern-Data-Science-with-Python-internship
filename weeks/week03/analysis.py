from pathlib import Path
import hashlib, json, sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load the same public source as Weeks 1 and 2.
URL = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv'
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src'))
from titanic_data import load_raw, RAW
root = Path(__file__).resolve().parent / 'outputs'
root.mkdir(exist_ok=True)
path = RAW
df = load_raw()
assert df.shape == (891, 15)
assert df.survived.isin([0, 1]).all()
# Identical profiles are not verified duplicate people. Keep all rows.
df['family_size'] = df.sibsp + df.parch + 1
df['family_group'] = pd.cut(df.family_size, [0, 1, 4, 20],
    labels=['Solo', 'Small 2 to 4', 'Large 5 or more'])
known = df.dropna(subset=['age']).copy()
known['child'] = np.where(known.age < 13, 'Under 13', '13 or older')
results = []
cts = {}
def chi_test(name, data, col):
    tab = pd.crosstab(data[col], data.survived)
    chi, p, dof, expected = stats.chi2_contingency(tab, correction=False)
    v = np.sqrt(chi / (tab.to_numpy().sum() * min(tab.shape[0]-1, tab.shape[1]-1)))
    results.append(dict(test=name, n=len(data), statistic=chi, df=dof,
        p=p, effect=v, min_expected=expected.min()))
    cts[name] = tab.to_dict()
chi_test('Sex', df, 'sex')
chi_test('Class', df, 'pclass')
a = known.loc[known.survived == 1, 'age']
b = known.loc[known.survived == 0, 'age']
welch = stats.ttest_ind(a, b, equal_var=False)
ci = welch.confidence_interval()
pooled = np.sqrt(((len(a)-1)*a.var()+(len(b)-1)*b.var())/(len(a)+len(b)-2))
g = (1-3/(4*(len(a)+len(b))-9)) * (a.mean()-b.mean()) / pooled
results.append(dict(test='Mean age', n=len(known), statistic=welch.statistic,
    df=welch.df, p=welch.pvalue, effect=g, min_expected=None))
chi_test('Child group', known, 'child')
chi_test('Family group', df, 'family_group')
adjusted = multipletests([r['p'] for r in results], method='holm')[1]
for row, p in zip(results, adjusted): row['p_holm'] = p
# Exploratory comparisons of nested logistic models on identical rows.
ports = df.dropna(subset=['embarked']).copy()
base = smf.logit('survived ~ C(pclass)', ports).fit(disp=False)
port = smf.logit('survived ~ C(pclass) + C(embarked)', ports).fit(disp=False)
lr_port = 2*(port.llf-base.llf)
main = smf.logit('survived ~ C(sex) + C(pclass)', df).fit(disp=False)
inter = smf.logit('survived ~ C(sex) * C(pclass)', df).fit(disp=False)
lr_inter = 2*(inter.llf-main.llf)
# Sensitivity only: single imputation understates age uncertainty.
imputed = df.copy()
imputed.age = imputed.age.fillna(df.groupby(['pclass','sex']).age.transform('median'))
imp_test = stats.ttest_ind(imputed.loc[df.survived==1,'age'],
    imputed.loc[df.survived==0,'age'], equal_var=False)
legacy = imputed.drop(columns='deck').copy()
for col in ['embarked', 'embark_town']:
    legacy[col] = legacy[col].fillna(legacy[col].mode()[0])
summary = dict(results=results, counts=cts,
    age=dict(survivor_n=len(a), other_n=len(b), survivor_mean=a.mean(),
    other_mean=b.mean(), survivor_sd=a.std(), other_sd=b.std(),
    difference=a.mean()-b.mean(), ci=[ci.low,ci.high], hedges_g=g),
    duplicates=int(pd.read_csv(path).duplicated().sum()),
    legacy_removed=int(legacy.duplicated().sum()),
    imputed_age_p=imp_test.pvalue,
    port=dict(lr=lr_port,df=2,p=stats.chi2.sf(lr_port,2)),
    interaction=dict(lr=lr_inter,df=2,p=stats.chi2.sf(lr_inter,2)),
    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    versions=dict(python=sys.version.split()[0], numpy=np.__version__,
    pandas=pd.__version__,scipy=scipy.__version__,
    statsmodels=statsmodels.__version__,matplotlib=matplotlib.__version__))
(root/'results.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

# Wilson intervals describe uncertainty in each group rate.
plt.rcParams.update({'font.size':11, 'axes.spines.top':False,
    'axes.spines.right':False, 'figure.dpi':160})
def rate_plot(ax, data, col, title):
    grp = data.groupby(col, observed=True).survived.agg(['sum','count'])
    rate = grp['sum']/grp['count']
    lo, hi = proportion_confint(grp['sum'],grp['count'],method='wilson')
    ax.bar(range(len(grp)),rate*100,color='#35668B',width=.62)
    ax.errorbar(range(len(grp)),rate*100,
        yerr=np.array([rate-lo,hi-rate])*100,fmt='none',color='black',capsize=4)
    ax.set_xticks(range(len(grp)),grp.index.astype(str))
    ax.set_ylim(0,100); ax.set_ylabel('Survived (%)'); ax.set_title(title)
    for i, (s,n) in enumerate(grp.to_numpy()):
        ax.text(i,hi.iloc[i]*100+3,f'{100*s/n:.1f}%\n{s}/{n}',ha='center',fontsize=10)
    ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
fig,axs=plt.subplots(1,2,figsize=(10,4.1))
rate_plot(axs[0],df,'sex','Survival by recorded sex')
rate_plot(axs[1],df,'pclass','Survival by passenger class')
fig.tight_layout();fig.savefig(root/'rates.png');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4.1))
axs[0].hist([b,a],bins=np.arange(0,86,5),label=['Did not survive','Survived'],
    color=['#B34A45','#28855D'],density=True)
axs[0].set(xlabel='Recorded age in years',ylabel='Density',title='Age distributions overlap')
axs[0].legend(fontsize=9)
axs[1].errorbar([a.mean()-b.mean()],[0],xerr=[[a.mean()-b.mean()-ci.low],
    [ci.high-(a.mean()-b.mean())]],fmt='o',capsize=6,color='#35668B')
axs[1].axvline(0,color='gray',linestyle='--')
axs[1].set(yticks=[],xlabel='Survivor minus non survivor mean age',
    title='Mean difference and 95% Welch interval',xlim=(-5,1))
fig.tight_layout();fig.savefig(root/'age.png');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4.1))
rate_plot(axs[0],known,'child','Recorded ages only')
rate_plot(axs[1],df,'family_group','Family size groups')
axs[1].tick_params(axis='x',labelsize=9)
fig.tight_layout();fig.savefig(root/'groups.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.8))
for sex, color in [('female','#28855D'),('male','#35668B')]:
    sub=df[df.sex==sex].groupby('pclass').survived.agg(['sum','count'])
    rate=sub['sum']/sub['count']
    lo,hi=proportion_confint(sub['sum'],sub['count'],method='wilson')
    ax.errorbar(sub.index,rate*100,yerr=np.array([rate-lo,hi-rate])*100,
        fmt='o-',capsize=5,label=sex,color=color)
ax.set(xticks=[1,2,3],xlabel='Passenger class',ylabel='Survived (%)',ylim=(0,105))
ax.legend();ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(root/'interaction.png');plt.close(fig)
