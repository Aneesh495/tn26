# Annotated Bibliography and Literature Review: Computational Social Science and Indian Political Economy

**Document Version:** 1.0.0  
**Repository:** `Aneesh495/tn26`  

---

## 1. Electoral Systems, Political Realignment, and Indian Democracy

- **Chhibber, Pradeep, and Irfan Nooruddin (2004).** *Do Party Systems Count? The Number of Parties and Government Performance in the Indian States.* Comparative Political Studies, 37(2), 152-185.
  - *Annotation:* Foundational text establishing how multi-party fragmentation in Indian states alters fiscal allocations and democratic accountability under First-Past-The-Post rules.

- **Duverger, Maurice (1954).** *Political Parties: Their Organization and Activity in the Modern State.* New York: Wiley.
  - *Annotation:* Formulates Duverger's Law, positing that single-member simple-plurality systems favor two-party competition; critical for understanding Tamil Nadu's sixty-year duopoly.

- **Key, V.O. (1955).** *A Theory of Critical Elections.* The Journal of Politics, 17(1), 3-18.
  - *Annotation:* Classic definition of critical realignment elections where enduring partisan loyalties are shattered by sharp, durable electoral shifts.

- **Riker, William H. (1962).** *The Theory of Political Coalitions.* New Haven: Yale University Press.
  - *Annotation:* Formulates the Size Principle and Minimal Winning Coalition (MWC) theory utilized in our legislative bargaining models.

- **Subramanian, Narendra (1999).** *Ethnicity and Populist Mobilization: Political Parties, Citizens and Democracy in South India.* Oxford University Press.
  - *Annotation:* Definitive academic treatment of Dravidian political culture, tracing the organizational evolution of the DMK and AIADMK and their populist welfare contracts.

- **Wyatt, Andrew (2010).** *Party System Change in South India: Political Entrepreneurs, Patterns and Processes.* Routledge.
  - *Annotation:* Analyzes third-force insurgencies (PMK, MDMK, DMDK) in Tamil Nadu and explains why previous third fronts failed to displace the two Dravidian giants.

---

## 2. Econometrics and Causal Inference

- **Abadie, Alberto, Alexis Diamond, and Jens Hainmueller (2010).** *Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program.* Journal of the American Statistical Association, 105(490), 493-505.
  - *Annotation:* Primary methodological foundation for our evaluation of the causal vote retention effect of the Kalaignar Magalir Urimai Thogai direct cash transfers.

- **Abadie, Alberto (2021).** *Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects.* Journal of Economic Literature, 59(2), 391-425.
  - *Annotation:* Outlines diagnostic requirements, donor pool selection rules, and placebo inference protocols implemented in `tn26.models.causal_synthetic_control`.

- **Angrist, Joshua D., and Jorn-Steffen Pischke (2009).** *Mostly Harmless Econometrics: An Empiricist's Companion.* Princeton University Press.
  - *Annotation:* Guides our two-way fixed effects (TWFE) Difference-in-Differences panel regression models and cluster-robust standard error derivations.

---

## 3. Spatial Statistics and Econometrics

- **Anselin, Luc (1988).** *Spatial Econometrics: Methods and Models.* Dordrecht: Kluwer Academic Publishers.
  - *Annotation:* Establishes maximum likelihood estimation for the Spatial Autoregressive (SAR) lag and spatial error models deployed in `tn26.models.spatial_error_autoregression`.

- **LeSage, James, and R. Kelley Pace (2009).** *Introduction to Spatial Econometrics.* CRC Press.
  - *Annotation:* Provides theoretical justification for scalar summary measures of spatial impacts: direct, indirect (spillover), and total multipliers.

---

## 4. Bayesian Statistics and Polling Forensics

- **Gelman, Andrew, and Gary King (1993).** *Why Are American Presidential Election Campaign Polls So Variable When Votes Are So Predictable?* British Journal of Political Science, 23(4), 409-451.
  - *Annotation:* Core theoretical inspiration for analyzing non-response bias and campaign information shocks.

- **Jackman, Simon (2005).** *Pooling the Polls Over an Election Campaign.* Australian Journal of Political Science, 40(4), 499-517.
  - *Annotation:* Outlines state-space Bayesian house-effect calibration models adapted in `tn26.models.poll_bias_forensics`.

- **King, Gary (1997).** *A Solution to the Ecological Inference Problem: Reconstructing Individual Behavior from Aggregate Data.* Princeton University Press.
  - *Annotation:* Foundational text for our ecological inference Markov voter transition probability matrix between the 2021 and 2026 elections.

---

## 5. Cooperative Game Theory

- **Banzhaf, John F. (1965).** *Weighted Voting Doesn't Work: A Mathematical Analysis.* Rutgers Law Review, 19, 317-343.
  - *Annotation:* Formulates the Banzhaf Power Index measuring legislative pivotality in multi-party legislatures.

- **Shapley, Lloyd S. (1953).** *A Value for n-Person Games.* Annals of Mathematics Studies, 28, 307-317.
  - *Annotation:* Classic axiomatic derivation of the Shapley Value, utilized to quantify post-election government formation leverage.

---

## 6. Political Communication and Natural Language Processing

- **Entman, Robert M. (1993).** *Framing: Toward Clarification of a Fractured Paradigm.* Journal of Communication, 43(4), 51-58.
  - *Annotation:* Theoretical framework for our 5-class automated frame extraction pipeline analyzing leader addresses and social media discourse.

- **Grimmer, Justin, and Brandon M. Stewart (2013).** *Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts.* Political Analysis, 21(3), 267-297.
  - *Annotation:* Informs our text pre-processing, Tamil-English tokenization, and stylometric validation routines.
