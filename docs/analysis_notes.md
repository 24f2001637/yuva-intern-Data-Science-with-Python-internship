# Analysis notes and corrections

## What was supplied and what was reconstructed

Weeks 1 and 2 arrived as Word documents. Their original standalone code and saved CSV files were not supplied. The repository keeps both Word documents byte-for-byte unchanged. Week 1 and Week 2 scripts are reconstructed, executed analyses, not recovered originals. The Week 3 script is the executed script underlying its report, adapted only to use the shared repository data path and an `outputs` folder.

## Passenger identity and repeated profiles

The 891-row raw CSV has 107 repeated profiles under `DataFrame.duplicated()`. It does not contain passenger names, ticket numbers or passenger IDs. Two passengers may share every exposed attribute. Automatically deleting these rows is not justified. The current pipeline keeps all rows.

Reproducing the Week 1 report's age/port imputation and deck removal before `drop_duplicates()` would remove 118 rows. This conflicts with the report's claim of no duplicates and continued use of 891 rows. That sequence is not used by this repository.

## Missing values

- Raw age has 177 missing values. Week 1 fills `age` with medians within class and sex for EDA, but also preserves `age_observed` and `age_missing`.
- The EDA table therefore intentionally contains 177 missing entries in `age_observed`. This is not failed cleaning: it preserves which ages were actually recorded.
- Week 2 age plots use recorded ages; other plots use all rows with the relevant variables present.
- Week 3 age and child tests use the 714 observed-age rows. The imputed-age test is explicitly a sensitivity check.
- Two missing ports are mode-filled in the EDA table. Week 2 port plots and the Week 3 port follow-up instead use the 889 recorded ports.
- Deck has 688 missing entries and is not used. The raw snapshot still retains it.

## Definitions

Family size is `sibsp + parch + 1`. Week 3 family categories are solo, 2–4 and 5 or more. Child status is age below 13. Week 2 age bins are half-open intervals: [0,13), [13,19), [19,31), [31,51), [51,infinity). Labels state their boundaries; fractional ages are handled explicitly.

## Interpretation corrections

- The family-size curve is non-monotonic; grouped results form an inverted U. The original Week 2 report called it a U curve and overstated zero survival in large families.
- The raw sex survival-rate ratio is about 3.93, rather than 3.7.
- Charts of class composition do not establish that class fully explains port differences. The Week 3 class-adjusted likelihood-ratio test still finds evidence of a port association in the specified model.
- Scatterplots do not establish independent predictor contributions. Interactions depend on the model scale; Week 3 tests sex by class on the log-odds scale.
- The `who` column is a derived age/sex classification, not a passenger-name field. The data contain no ticket-number or full cabin-number column; `deck` is a coarser field.
- Do not infer causes of missing data, historical evacuation mechanisms, modern customer loyalty or modern safety outcomes from these variables alone.

## Statistical limitations

The five main tests use Holm-adjusted p-values. Confidence intervals are pointwise. Family members can share outcomes, violating independent-observation assumptions. The selected historical dataset is not a random sample of modern passengers. Prior exploration informed the hypotheses, and no independent validation dataset was used for inference. Missing-age sensitivity changes the mean-age threshold decision. All conclusions should retain these qualifications.

## Future modelling

Do not feed the pre-imputed EDA table into a train/test experiment without reconsidering preprocessing. Start from raw data, split first, then fit imputation and encoding on training data only. Exclude `alive`, which directly encodes the target. Treat statistical evidence and held-out predictive performance as different questions.
