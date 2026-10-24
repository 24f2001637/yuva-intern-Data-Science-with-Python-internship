"""Reproducible Week 4 classification experiment; run from any directory."""
from pathlib import Path
import hashlib
import json
import platform
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, brier_score_loss, confusion_matrix,
    ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from titanic_data import load_raw, RAW
OUT = Path(__file__).parent / 'outputs'
SEED = 42
FEATURES = ['age', 'log_fare', 'pclass', 'sex', 'embarked', 'family_group']

def make_features(raw):
    x = raw[['age', 'fare', 'pclass', 'sex', 'embarked']].copy()
    x['log_fare'] = np.log1p(x.pop('fare'))
    size = raw.sibsp + raw.parch + 1
    x['family_group'] = pd.cut(size, [0, 1, 4, np.inf],
        labels=['Solo', 'Small 2 to 4', 'Large 5 or more']).astype(str)
    return x[FEATURES]

def make_pipeline(model):
    numeric = Pipeline([('impute', SimpleImputer(strategy='median', add_indicator=True)),
                        ('scale', StandardScaler())])
    categorical = Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
        ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    prep = ColumnTransformer([('numeric', numeric, ['age', 'log_fare']),
        ('categorical', categorical, ['pclass', 'sex', 'embarked', 'family_group'])])
    return Pipeline([('prepare', prep), ('model', model)])

def metrics(y, p):
    pred = (p >= .5).astype(int)
    return dict(accuracy=accuracy_score(y, pred),
        balanced_accuracy=balanced_accuracy_score(y, pred),
        precision=precision_score(y, pred, zero_division=0),
        recall=recall_score(y, pred), f1=f1_score(y, pred),
        roc_auc=roc_auc_score(y, p), average_precision=average_precision_score(y, p),
        brier=brier_score_loss(y, p))

def main():
    OUT.mkdir(exist_ok=True)
    raw = load_raw()
    x, y = make_features(raw), raw.survived
    train, test = train_test_split(raw.index, test_size=.2,
        stratify=y, random_state=SEED)
    assert set(train).isdisjoint(test)
    models = {
        'Majority baseline': DummyClassifier(strategy='prior'),
        'Logistic regression': LogisticRegression(C=1., max_iter=2000, random_state=SEED),
        'Decision tree': DecisionTreeClassifier(max_depth=4, min_samples_leaf=10,
                                              random_state=SEED)}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    scores, fitted, rows = {}, {}, []
    for name, model in models.items():
        pipe = make_pipeline(model)
        result = cross_validate(pipe, x.loc[train], y.loc[train], cv=cv,
            scoring={'auc': 'roc_auc', 'accuracy': 'accuracy', 'f1': 'f1'},
            return_train_score=True)
        scores[name] = {k: v.tolist() for k, v in result.items()
                        if k not in ('fit_time', 'score_time')}
        fitted[name] = clone(pipe).fit(x.loc[train], y.loc[train])
    # Selection is fixed by development CV, before test probabilities are inspected.
    selected = max(models, key=lambda n: np.mean(scores[n]['test_auc']))
    probabilities = {}
    for name, pipe in fitted.items():
        p = pipe.predict_proba(x.loc[test])[:, 1]
        probabilities[name] = p
        rows.append({'model': name,
            'cv_auc_mean': np.mean(scores[name]['test_auc']),
            'cv_auc_sd': np.std(scores[name]['test_auc'], ddof=1),
            'cv_train_auc': np.mean(scores[name]['train_auc']),
            **metrics(y.loc[test], p)})
    results = pd.DataFrame(rows)
    results.to_csv(OUT / 'model_metrics.csv', index=False)
    pred = pd.DataFrame({'row_id': test, 'actual': y.loc[test].to_numpy(),
        'sex': raw.loc[test, 'sex'].to_numpy(), 'pclass': raw.loc[test, 'pclass'].to_numpy()})
    for name, p in probabilities.items(): pred[name] = p
    pred['selected_prediction'] = (probabilities[selected] >= .5).astype(int)
    pred.to_csv(OUT / 'test_predictions.csv', index=False)
    pd.DataFrame({'row_id': raw.index,
        'split': np.where(raw.index.isin(train), 'train', 'test')}).to_csv(OUT / 'split.csv', index=False)
    subgroup = []
    for col in ['sex', 'pclass']:
        for label, g in pred.groupby(col):
            tn, fp, fn, tp = confusion_matrix(g.actual, g.selected_prediction, labels=[0, 1]).ravel()
            subgroup.append(dict(group=f'{col}={label}', n=len(g), survivors=int(g.actual.sum()),
                accuracy=accuracy_score(g.actual, g.selected_prediction),
                recall=tp/(tp+fn) if tp+fn else None,
                false_positive_rate=fp/(tn+fp) if tn+fp else None,
                tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp)))
    pd.DataFrame(subgroup).to_csv(OUT / 'subgroup_metrics.csv', index=False)
    # Conditional uncertainty for the already-selected, already-fitted model.
    rng = np.random.default_rng(SEED)
    yt, pt = y.loc[test].to_numpy(), probabilities[selected]
    boot = []
    for _ in range(2000):
        ii = rng.integers(0, len(test), len(test))
        if len(np.unique(yt[ii])) == 2:
            boot.append([accuracy_score(yt[ii], pt[ii] >= .5), roc_auc_score(yt[ii], pt[ii])])
    ci = np.quantile(boot, [.025, .975], axis=0)
    summary = dict(selected_model=selected, selection_metric='mean development CV ROC AUC',
        seed=SEED, threshold=.5, train_n=len(train), test_n=len(test),
        train_survivors=int(y.loc[train].sum()), test_survivors=int(yt.sum()),
        features=FEATURES, excluded=['alive', 'class', 'who', 'adult_male', 'alone', 'deck'],
        dataset_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
        cv=scores, metrics=rows,
        confusion_matrix=confusion_matrix(yt, pt >= .5).tolist(),
        bootstrap={'replicates':len(boot), 'accuracy_ci':ci[:,0].tolist(),
                   'roc_auc_ci':ci[:,1].tolist()},
        versions={'python':platform.python_version(), 'sklearn':sklearn.__version__,
                  'pandas':pd.__version__, 'numpy':np.__version__})
    (OUT / 'results.json').write_text(json.dumps(summary, indent=2)+'\n')
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    fig, ax = plt.subplots(figsize=(7.2, 4))
    xx = np.arange(len(results))
    ax.bar(xx-.18, results.cv_auc_mean, width=.36, color='#31688e', label='Development CV',
           yerr=results.cv_auc_sd, capsize=4)
    ax.bar(xx+.18, results.roc_auc, width=.36, color='#35a18a', label='Test')
    ax.set(xticks=xx, xticklabels=['Baseline','Logistic regression','Decision tree'],
           ylim=(0,1), ylabel='ROC AUC', title='Model comparison: CV chooses the final model')
    ax.legend(); fig.tight_layout(); fig.savefig(OUT/'01_model_comparison.png',dpi=170); plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(9,3.8))
    for ax, name in zip(axes, ['Logistic regression','Decision tree']):
        ConfusionMatrixDisplay.from_predictions(yt, probabilities[name]>=.5,
            display_labels=['Did not survive','Survived'], ax=ax, colorbar=False, cmap='Blues')
        ax.set_title(name+(' (selected)' if name==selected else ''))
    fig.tight_layout(); fig.savefig(OUT/'02_confusion_matrices.png',dpi=170); plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(9,3.8))
    for name,p in probabilities.items():
        RocCurveDisplay.from_predictions(yt,p,name=name,ax=axes[0])
        PrecisionRecallDisplay.from_predictions(yt,p,name=name,ax=axes[1])
    axes[0].plot([0,1],[0,1],'k--',lw=.7)
    axes[0].set_title('Test ROC curves'); axes[1].set_title('Test precision–recall curves')
    for ax in axes: ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(OUT/'03_roc_pr.png',dpi=170); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.2,3.8))
    g = pd.DataFrame(subgroup)
    ax.bar(g.group,g.recall,color='#31688e')
    for i,row in g.iterrows(): ax.text(i,row.recall+.025,f'n={row.n}\nsurvivors={row.survivors}',ha='center',fontsize=8)
    ax.set(ylim=(0,1.15),ylabel='Recall among actual survivors',title='Selected model: descriptive subgroup errors')
    fig.tight_layout();fig.savefig(OUT/'04_subgroups.png',dpi=170);plt.close(fig)
    print(results.to_string(index=False))
    print('Selected:',selected,'; confusion matrix:',summary['confusion_matrix'])

if __name__ == '__main__':
    main()
