# Week 1 — Acquisition, cleaning and EDA

The Word report is the original supplied submission. `analysis.py` reconstructs the acquisition and cleaning workflow with five visualisations and documented fixes. It retains all passenger rows, preserves original age information and writes `data/processed/titanic_eda.csv`.

Run from the repository root: `python weeks/week01/analysis.py`.

Outputs include missing-value counts, raw summary statistics, an audit JSON, a missingness map, class survival charts, age/fare histograms, a correlation heatmap and boxplots. Read `docs/analysis_notes.md` for differences from the original report. The script does not rewrite that report.
