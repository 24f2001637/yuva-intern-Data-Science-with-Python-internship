# Week 3 — Statistical analysis and hypothesis testing

The report documents five main tests: sex, class, mean age, child group and family group. Categorical comparisons use Pearson chi-square tests; mean age uses Welch's t-test. The five p-values receive Holm adjustment. The analysis reports effect sizes, a Welch confidence interval, Wilson intervals, expected counts and limitations.

Run from the repository root: `python weeks/week03/analysis.py`.

The script writes `outputs/results.json` and four figures. It also performs two exploratory logistic likelihood-ratio follow-ups and an imputed-age sensitivity check. Exploratory follow-up p-values are not part of the five-test Holm family.

The script is adapted from the complete code embedded in the Word report so all weeks share `data/raw/titanic.csv`. Its statistical calculations are unchanged. The Word report remains a standalone deliverable.
