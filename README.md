# Data Science with Python Internship

An eight-week internship workspace built around the **Titanic passenger dataset**. Weeks 1–3 cover data preparation, visual storytelling and statistical hypothesis testing. The repository brings together the Word reports, executable analysis, source data and generated results.

**Programme:** YuvaIntern Virtual Data Science with Python Apprenticeship  
**Data snapshot:** 891 passenger records, 342 survivors, 15 original columns  
**Tested runtime:** Python 3.12.14

## Weekly work

| Week | Topic | Status | Main files |
|---|---|---|---|
| 1 | Acquisition, cleaning and exploratory analysis | Original report included; reconstructed code executed | [Report](weeks/week01/Week1_Data_Acquisition_Cleaning_EDA.docx) · [Code](weeks/week01/analysis.py) · [Outputs](weeks/week01/outputs) |
| 2 | Advanced visualisation and storytelling | Original report included; reconstructed code executed | [Report](weeks/week02/Week2_Data_Visualization_Storytelling.docx) · [Code](weeks/week02/analysis.py) · [Outputs](weeks/week02/outputs) |
| 3 | Statistical analysis and hypothesis testing | Report and analysis completed | [Report](weeks/week03/Week3_Statistical_Analysis_Hypothesis_Testing.docx) · [Code](weeks/week03/analysis.py) · [Outputs](weeks/week03/outputs) |
| 4 | Machine learning development and evaluation | Task recorded; work pending | [Task brief](weeks/week04/README.md) |
| 5 | Project reporting and strategic recommendations | Task recorded; work pending | [Task brief](weeks/week05/README.md) |
| 6 | Task not supplied | Placeholder only | [Week 6](weeks/week06/README.md) |
| 7 | Task not supplied | Placeholder only | [Week 7](weeks/week07/README.md) |
| 8 | Task not supplied | Placeholder only | [Week 8](weeks/week08/README.md) |

The supplied Week 5 brief calls that week the final week, while the internship was described as eight weeks. The repository preserves the supplied topic and leaves Weeks 6–8 open until their tasks are available.

## Quick start

Extract the archive and open a terminal inside `internship-data-science`. Use Python 3.12 for the pinned environment.

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_all.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Linux, macOS or WSL**

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_all.py
.venv/bin/python -m unittest discover -s tests -v
```

No API key is required. The exact source CSV is included, so analysis runs offline after dependencies are installed. If the CSV is removed, the loader downloads it and checks its SHA256 before accepting it. A changed upstream snapshot requires explicit review rather than silently changing the results.

To run a single week, use the virtual environment's Python with its script, for example:

```bash
python weeks/week03/analysis.py
```

Replace `python` with `.venv/bin/python` or `.venv\Scripts\python.exe` if the virtual environment is not activated. Scripts resolve paths relative to their own locations, so they do not depend on the terminal's working directory.

## Repository contents

- `data/raw/titanic.csv`: exact source snapshot, never modified by analysis.
- `data/processed/titanic_eda.csv`: generated EDA table with imputed age and preserved original-age fields.
- `src/titanic_data.py`: shared loading, hash validation and EDA preprocessing.
- `weeks/week01/`: original Word report, reconstructed EDA script and five figures.
- `weeks/week02/`: original Word report, reconstructed storytelling script, six figures and summary tables.
- `weeks/week03/`: Week 3 Word report, executed statistical script, four figures and machine-readable results.
- `weeks/week04/` through `weeks/week08/`: pending task folders.
- `docs/analysis_notes.md`: corrections, definitions and interpretation limits.
- `docs/data_provenance.md`: source, snapshot hash and reuse information.
- `docs/github_setup.md`: instructions for uploading this project to GitHub.
- `tests/test_results.py`: dataset and statistical-result regression checks.
- `.github/workflows/analysis.yml`: reruns the analysis and checks on pushes and pull requests.

Generated CSVs, figures and result JSON files are intentionally tracked so a reviewer can inspect the work without running Python. `run_all.py` regenerates those outputs. It does **not** rewrite the submitted Word reports.

## Selected findings

![Survival by sex and class](weeks/week03/outputs/rates.png)

The Week 3 analysis found clear associations of survival with sex, passenger class and family size. The mean-age difference was small and sensitive to missing-value treatment. These are observational associations, not causal estimates.

| Week 3 test | Records | Holm-adjusted p-value | Interpretation under working assumptions |
|---|---:|---:|---|
| Sex and survival | 891 | 1.856e-58 | Evidence of association |
| Class and survival | 891 | 1.820e-22 | Evidence of association |
| Mean age by survival | 714 | 0.04119 | Small difference; sensitive to missingness |
| Under 13 status and survival | 714 | 0.004025 | Evidence of association |
| Family group and survival | 891 | 1.957e-16 | Evidence of association; within-family dependence matters |

The five-test family uses a significance threshold of 0.05 and Holm adjustment. The questions were informed by earlier exploration of the same data, so this remains exploratory work. Full-precision results, expected-cell checks and effect sizes are in [results.json](weeks/week03/outputs/results.json).

## Continuity and corrections

Weeks 1 and 2 were supplied as Word reports, without their original Python source files. Their scripts here are newly reconstructed implementations. They preserve the project themes while correcting identified issues. The original reports are retained unchanged as historical submissions, so some claims in them differ from the audited code and Week 3 report.

In particular, all 891 passenger records are retained; 107 repeated feature profiles do not establish duplicate people. Formal age tests use observed ages. The family-size pattern is non-linear and is an inverted U when grouped as solo, 2–4 and 5 or more. Class-only adjustment does not eliminate the port association in the specified Week 3 model. See [analysis notes](docs/analysis_notes.md) before interpreting the earlier reports.

## GitHub repository

Repository: https://github.com/24f2001637/yuva-intern-Data-Science-with-Python-internship

Clone this project with:

```bash
git clone https://github.com/24f2001637/yuva-intern-Data-Science-with-Python-internship.git
cd yuva-intern-Data-Science-with-Python-internship
```

Then follow the environment setup above. Completed work is in Weeks 1–3; remaining weeks are pending. The GitHub Actions workflow reruns the analysis and checks on pushes and pull requests.

## Sources and reuse

The Titanic CSV comes from the [Seaborn example-data repository](https://github.com/mwaskom/seaborn-data). Method references and the data hash are recorded in [data provenance](docs/data_provenance.md). No new license is assigned to the upstream dataset or the supplied reports. Choose an appropriate license for your own code before licensing the repository as a whole.
