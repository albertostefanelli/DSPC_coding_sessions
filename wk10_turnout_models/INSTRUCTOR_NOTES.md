# Week 10 teaching and verification notes

The student notebook introduces concepts before code, then uses one real North Carolina voter-file extract to fit and assess a turnout model. The separate solutions notebook repeats the same teaching cells and prompts, with worked code, outputs and short substantive answers added only in the solution sections.

## Scope and sources for the instructor

The theoretical scope follows `class_slides/wk10_slides.pdf`: propensity and LPM (pp. 6–10), prediction timing and new voters (pp. 11–12), the free answer and confusion metrics (pp. 13–19), calibration and overfitting (pp. 20–23), and support versus contact effects (pp. 24–26). There is no Brier score, logistic-regression lesson, odds-ratio interpretation, third validation set, or AI-agent exercise.

The presentation follows the theory–demonstration–exercise structure of the Week 8 and Week 9 coding sessions. The supplied Week 10 live coding and problem set supply the familiar `sample`/`drop` split, formula-based OLS, `predict`, thresholding, Boolean confusion counts, and `pd.cut`/`groupby` calibration. Trimming and complete bin coverage are retained. A row split tests other retained people in the same election; it does not establish later-election performance.

The 2024 presidential target is deliberate. Three securely covered previous elections are available in the current official history window. The notebook does not manufacture 2012/2014 records, label a 2024 fit a validated 2026 midterm model, or infer contact effects from ordinary voter-file data. Administrative preparation choices and limitations are described in `data/README.md` and its audit.

## Teaching sequence and timing

Allow approximately 75 minutes: 15 minutes for definitions and simple examples, 35 for the data walkthrough, and 25 for exercises and discussion. The age-group check is the natural optional demonstration if discussion runs long.

1. Define a score and build one from hypothetical coefficients.
2. Explain held-out testing, the free answer, confusion metrics, and calibration.
3. Inspect the dated real cohort, split it, fit one LPM, predict and evaluate.
4. Interpret errors and distinguish turnout from support or responsiveness.
5. Complete four short exercises, emphasizing interpretation over syntax.

## Original exercises

The prior exam informed the short code-reading and justified-answer style only. The exercises do not reuse its substantive questions or the case's highest/middle/lowest contact-list decision.

| Exercise | Primary reasoning objective | Coding already demonstrated |
|---|---|---|
| Unseen-voter audit | Explain why training-row evaluation answers the wrong question, without assuming the corrected number must fall. | `predict`, clipping, threshold, comparison, mean, free answer. |
| Fictional profile comparison | Interpret a prediction gap without claiming causation or reading a reason into a recorded zero. | `DataFrame`, named row lookup, `predict`, subtraction. |
| Same calls, different probabilities | Explain why accuracy cannot establish calibration. | Threshold comparisons and grouped means. |
| Correct the turnout report | Distinguish turnout levels from turnout added by contact; name the needed experiment. | Fixed score-band filter, counts and means. |

## Figures

The three conceptual images are original hypothetical illustrations. Their coefficients, counts and relationships are not estimates from the North Carolina data. The additive example produces 0.69. The two confusion matrices both have 70% accuracy but different precision/recall. The calibration illustration shows a 20-percentage-point overprediction. The approved empirical calibration plot is generated from the held-out North Carolina records.

Figure generation code is in `assets/build_concept_figures.py`. The preview files were reviewed for arithmetic, text layout and consistency with the notebook definitions before inclusion approval. Keep numerical data charts distinguishable from hypothetical concept figures.

## Verification

The local `VALIDATION.md` report records actual execution status and remaining limitations. Checks include two fresh kernels, exact shared-cell/prompt consistency, student answer separation, split separation, sample and bin coverage, probability bounds, independent NumPy least-squares verification, exercise calculations, and cloud payload identity. HTML exports are produced for checking notebook presentation. Direct Google Colab execution is not performed.

Timestamped backups preserve the pre-revision notebook and data notes, plus checkpoints before later writes. The legacy robocall CSV and supplied reference PDFs are unchanged.
