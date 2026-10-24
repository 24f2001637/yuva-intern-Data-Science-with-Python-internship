# Data provenance

- Source repository: https://github.com/mwaskom/seaborn-data
- Source file: https://github.com/mwaskom/seaborn-data/blob/master/titanic.csv
- Download URL: https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv
- Snapshot retrieved for this project: 24 October 2026.
- Shape: 891 rows and 15 original columns.
- SHA256: `81787d320d7f7b03df935e91de8bd19e11d45c5bbcab86ef4d4a76dc91b7d4f2`.

The repository branch is mutable. The hash, not the branch name alone, identifies the analysed bytes. A snapshot is included for reproducibility. The loader refuses a different hash instead of silently changing the analysis.

This is Seaborn's example Titanic dataset, not a complete manifest of everyone aboard. Original columns are `survived`, `pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`, `class`, `who`, `adult_male`, `deck`, `embark_town`, `alive`, `alone`.

The supplied reports and upstream dataset retain their existing rights. This repository does not assert a new license or claim ownership of the data. Review upstream terms before redistribution beyond the internship context.

## Statistical references

- SciPy chi-square test: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
- SciPy independent t-test: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
- Statsmodels multiple-testing correction: https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html
- Statsmodels proportion intervals: https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html

Python and package versions used for the statistical execution are saved in `weeks/week03/outputs/results.json`.
