# Week 4 — Machine learning development and evaluation

Completed using the supplied Week 4 task.

- Report: [Week4_Machine_Learning_Development_Evaluation.docx](Week4_Machine_Learning_Development_Evaluation.docx)
- Run: `python weeks/week04/analysis.py` from the repository root.
- Outputs: four figures, CV/test metrics, predictions, subgroup errors and split manifest.
- Selected model: logistic regression by development CV ROC AUC.
- Internal test: 179 records, accuracy 82.1%, ROC AUC 0.845.

All preprocessing is fitted within training folds. A fixed threshold of 0.50 is used.
Earlier weeks explored the full dataset, and family identifiers are unavailable;
these limitations prevent treating this as independent external validation.
The report documents uneven subgroup errors and a proposed 32-hour workload, not
an actual time log. The complete script is executable without API keys.
