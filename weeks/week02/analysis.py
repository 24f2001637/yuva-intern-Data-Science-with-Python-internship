"""Six reproducible visualisations, with careful observational interpretations."""
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src'))
from titanic_data import load_raw
raw = load_raw()
df = raw.assign(family_size=raw.sibsp + raw.parch + 1)
out = Path(__file__).resolve().parent / 'outputs'
out.mkdir(exist_ok=True)
sns.set_theme(style='whitegrid')
colors = {0: '#B34A45', 1: '#28855D'}
def save(name):
    plt.tight_layout()
    plt.savefig(out/name, dpi=160, bbox_inches='tight')
    plt.close()
sex_class = df.groupby(['pclass','sex']).survived.agg(['sum','count','mean'])
sex_class.to_csv(out/'sex_class_rates.csv')
fig,ax=plt.subplots(figsize=(9,4.8))
sex_class['mean'].unstack().mul(100).plot.bar(ax=ax,color=['#28855D','#35668B'])
ax.set(ylabel='Survived (%)',ylim=(0,115),title='Sex and class jointly structure observed survival')
for container, sex in zip(ax.containers, ['female','male']):
    values=sex_class.xs(sex,level='sex')
    ax.bar_label(container,labels=[f'{100*row["mean"]:.1f}%\nn={int(row["count"])}'
                                  for _,row in values.iterrows()],fontsize=9,padding=3)
ax.tick_params(axis='x',rotation=0)
save('01_sex_class.png')
known=df.dropna(subset=['age']).copy()
# Half-open intervals avoid ambiguity for fractional ages.
known['age_group']=pd.cut(known.age,[0,13,19,31,51,np.inf],right=False,
    labels=['Under 13','13 to under 19','19 to under 31','31 to under 51','51 and over'])
age=known.groupby('age_group',observed=True).survived.agg(['sum','count','mean'])
age.to_csv(out/'age_group_rates.csv')
fig,ax=plt.subplots(figsize=(9,4.5))
ax.bar(age.index.astype(str),age['mean']*100,color='#35668B')
for i,row in enumerate(age.itertuples()):
    ax.text(i,row.mean*100+2,f'{row.mean*100:.1f}%\nn={row.count}',ha='center',fontsize=9)
ax.axhline(known.survived.mean()*100,ls='--',color='gray',label='Recorded-age subset overall')
ax.set(ylabel='Survived (%)',ylim=(0,85),title='Children have higher observed survival in recorded ages')
ax.legend();save('02_age_groups.png')
family=df.groupby('family_size').survived.agg(['sum','count','mean'])
family.to_csv(out/'family_size_rates.csv')
fig,ax=plt.subplots(figsize=(9,4.5))
ax.plot(family.index,family['mean']*100,'o-',color='#35668B')
for size,row in family.iterrows():
    ax.annotate(f'n={int(row["count"])}',(size,row['mean']*100),xytext=(0,9),
                textcoords='offset points',ha='center',fontsize=9)
ax.set(xlabel='Family size including passenger',ylabel='Survived (%)',ylim=(-3,105),
       xticks=family.index,title='Family size association is non-linear')
save('03_family_size.png')
fig,ax=plt.subplots(figsize=(9,5))
for outcome,label in [(0,'Did not survive'),(1,'Survived')]:
    sub=known[known.survived==outcome]
    ax.scatter(sub.age,np.log1p(sub.fare),s=sub.family_size*16,
               alpha=.45,color=colors[outcome],label=label)
ax.set(xlabel='Recorded age',ylabel='log(1 + fare)',title='Age, fare and family size overlap across outcomes')
ax.legend(title='Bubble area proportional to family size')
save('04_age_fare_family.png')
ports=df.dropna(subset=['embarked'])
port_rates=ports.groupby('embarked').survived.agg(['sum','count','mean'])
port_rates.to_csv(out/'port_rates.csv')
fig,axs=plt.subplots(1,2,figsize=(11,4.5))
port_rates['mean'].mul(100).plot.bar(ax=axs[0],color='#35668B')
for i,row in enumerate(port_rates.itertuples()):
    axs[0].text(i,row.mean*100+2,f'n={row.count}',ha='center')
axs[0].set(ylabel='Survived (%)',ylim=(0,100),title='Observed survival by embarkation port')
pd.crosstab(ports.embarked,ports.pclass,normalize='index').mul(100).plot.bar(
    stacked=True,ax=axs[1],color=['#35668B','#75A0BE','#D5E2EC'])
axs[1].set(ylabel='Passengers (%)',title='Class composition also differs')
for ax in axs: ax.tick_params(axis='x',rotation=0)
save('05_embarkation.png')
g=sns.pairplot(known[['age','fare','family_size','survived']],hue='survived',
    palette=colors,diag_kind='hist',plot_kws={'alpha':.4,'s':15},height=2.2)
g.fig.suptitle('Pairwise patterns among passengers with recorded ages',y=1.02)
g.savefig(out/'06_pairplot.png',dpi=140,bbox_inches='tight');plt.close(g.fig)
print('Week 2 complete: six figures and four source tables.')
