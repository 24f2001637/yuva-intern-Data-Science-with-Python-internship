# Week 2 — Visualisation and storytelling

The Word report is the original supplied submission. `analysis.py` reconstructs six visualisations using the same dataset and corrects unsupported interpretations without rewriting the report.

Run from the repository root: `python weeks/week02/analysis.py`.

Figures cover sex with class, age groups, family size, age/fare/family size, embarkation with class composition, and pairwise numeric patterns. Four CSV tables make chart calculations inspectable. Recorded-age plots exclude missing ages, and port plots exclude missing ports.

The narrative supported by these outputs is that survival rates differ across groups, with overlapping associations. The plots do not establish causal mechanisms or prove that class fully explains port differences. See `docs/analysis_notes.md` and the Week 3 report for the formal follow-up.
