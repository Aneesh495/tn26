# System Architecture and Mathematical Specifications: The tn26 Research Platform

**Document Version:** 1.0.0  
**Status:** Production / Academic Release  
**Repository:** `Aneesh495/tn26`  

---

## 1. System Overview

The `tn26` software platform is a production-grade, modular computational framework designed for high-throughput electoral modeling, econometric causal identification, spatial statistics, and forensic survey analysis.

```
                           TN26 SYSTEM ARCHITECTURE DIAGRAM
 ====================================================================================
 [ DATA INGESTION & AUDITING SUBSYSTEM ]
   * eci_parser.py           : ECI 234 AC Margins & Candidate Returns Parser
   * poll_harvester.py       : Opinion & Exit Poll Microdata Ingestion
   * welfare_loader.py       : AC Socioeconomic, Census & Scheme Integration
   * speech_loader.py        : Leader Transcripts & Tamil Tokenization
   * social_loader.py        : Multi-Platform Digital Signals Processor
 ------------------------------------------------------------------------------------
                                          |
                                          v
 [ FEATURE FACTORY & GEOSPATIAL PIPELINES ]
   * swing_elasticity.py     : Uniform & Proportional FPTP Swing Simulators
   * anti_incumbency.py      : Multi-Tier MLA & Regime Penalty Decomposition
   * welfare_saturation.py   : Net Fiscal Surplus / TASMAC Extraction Burden
   * spatial_lag_features.py : 234 x 234 Queen Adjacency Spatial Weights & Moran's I
 ------------------------------------------------------------------------------------
                                          |
                                          v
 [ CORE ECONOMETRIC & MACHINE LEARNING ENGINES ]
   1. bayesian_multinomial.py : Hierarchical Dirichlet-Multinomial (Laplace / MCMC)
   2. spatial_error_autoreg.py: Spatial Autoregressive (SAR) Lag Maximum Likelihood
   3. causal_synthetic_ctrl.py: Constrained Quadratic Synthetic Control (Abadie et al.)
   4. diff_in_diff.py         : Panel TWFE with Clustered Standard Errors
   5. voter_transition.py     : King's Ecological Inference Quadratic Programming
   6. alliance_game_theory.py : Cooperative Bargaining: Exact Shapley & Banzhaf Indices
   7. poll_bias_forensics.py  : Bayesian House Effects & Dispersion Herding Detector
   8. ensemble_predictor.py   : Multi-Model Stacking Ensemble Predictor
 ------------------------------------------------------------------------------------
                                          |
                                          v
 [ SIMULATION, EVALUATION & DISSEMINATION ]
   * monte_carlo_seat_engine.py : 100,000 Correlated Realizations (Cholesky Covariance)
   * coalition_arithmetic.py    : Legislative Floor Tests & Confidence-and-Supply Pacts
   * speech_counterfactual.py   : Turning Point Sensitivity Schedules
   * metrics.py & scorecard.py  : Multiclass Brier Scores, MAE, & Agency Grading
   * FastAPI (/api/*) & CLI     : REST Endpoints & Terminal Research Dashboard
   * Visualization Suite        : Publication-Grade PNG/SVG Generation (300 DPI)
 ====================================================================================
```

---

## 2. Formal Mathematical Formulations

### 2.1 Hierarchical Dirichlet-Multinomial Bayesian Regression
For each assembly constituency $i \in \{1, \dots, 234\}$, let $Y_i = [y_{i1}, \dots, y_{iK}]$ denote the vector of votes cast across $K = 5$ competing political blocs (TVK, DMK-led, AIADMK-led, NTK, Other), with total ballots $N_i = \sum_{k=1}^K y_{ik}$.

$$Y_i \sim \text{Multinomial}(N_i, \pi_i)$$
$$\pi_i \sim \text{Dirichlet}(\alpha_i)$$

The concentration parameter vector $\alpha_i = [\alpha_{i1}, \dots, \alpha_{iK}]$ is parameterized via log-linear regression:

$$\log \alpha_{ik} = \mu_k + X_i \beta_k + \gamma_{r[i], k}$$

where:
- $X_i$ is a standardized vector of demographic, socioeconomic, and welfare predictors.
- $\beta_k$ are party-specific regression coefficients.
- $\gamma_{r[i], k}$ is a regional random intercept for geopolitical region $r[i] \in \{1, \dots, 6\}$.
- Reference category normalization is enforced by fixing $\mu_K = 0, \beta_K = 0, \gamma_{r, K} = 0$.

### 2.2 Spatial Autoregressive (SAR) Model
To account for spatial spillover effects across contiguous constituencies, the spatial lag model is formulated as:

$$y = \rho W y + X \beta + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2 I_N)$$

where:
- $W$ is the $234 \times 234$ row-standardized Queen spatial adjacency matrix ($\sum_j w_{ij} = 1$).
- $\rho \in (-1, 1)$ is the spatial autoregressive parameter.
- The reduced-form expectation is:
  $$\mathbb{E}[y] = (I_N - \rho W)^{-1} X \beta$$
- The total spatial multiplier matrix is given by:
  $$S = (I_N - \rho W)^{-1}$$
  with average direct effect equal to $\frac{1}{N} \text{tr}(S)$ and average total effect equal to $\frac{1}{N} \mathbf{1}^T S \mathbf{1}$.

### 2.3 Synthetic Control Quadratic Program
For treated constituency $i$ and donor pool $J$:

$$\min_{W} (X_{1} - X_{0} W)^T V (X_{1} - X_{0} W)$$

subject to:
$$\sum_{j=1}^{J} w_j = 1, \quad w_j \ge 0 \quad \forall j$$

The causal treatment effect at post-treatment period $T$ is:

$$\hat{\tau} = Y_{1, T} - \sum_{j=1}^J w_j^* Y_{j, T}$$

### 2.4 Difference-in-Differences Panel Model
For constituency $i$ in period $t \in \{0, 1\}$:

$$Y_{it} = \alpha_i + \lambda_t + \delta (\text{TreatedCluster}_i \times \text{Post}_t) + X_{it} \beta + \epsilon_{it}$$

where standard errors are clustered at the district level using the White-Arellano sandwich covariance estimator:

$$\widehat{\text{Var}}(\hat{\delta}) = (X^T X)^{-1} \left( \sum_{g=1}^G X_g^T \hat{u}_g \hat{u}_g^T X_g \right) (X^T X)^{-1}$$

### 2.5 Cooperative Game Theory: Shapley Value
For simple voting game $(N, v)$ with majority threshold $q = 118$:

$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|! (|N| - |S| - 1)!}{|N|!} [v(S \cup \{i\}) - v(S)]$$

### 2.6 Monte Carlo Correlated Realizations
To simulate 100,000 elections, we draw correlated multivariate normal shocks:

$$\epsilon_d = L Z_d, \quad Z_d \sim \mathcal{N}(0, I_N)$$

where $L$ is the lower triangular Cholesky factor of the regional covariance matrix $\Sigma = L L^T$, with intra-regional correlation $\rho_{\text{intra}} = 0.55$.

---

## 3. Software Architecture and API Endpoints

The package is organized under the top-level namespace `tn26`:

```
tn26/
├── config.py              # Constants, paths, color maps
├── data_ingestion/        # ECI, polls, speech, social, demographics loaders
├── features/              # Elasticity, anti-incumbency, welfare, spatial lags
├── models/                # Bayesian, SAR, DiD, Synthetic Control, Game Theory
├── simulation/            # Monte Carlo, coalition arithmetic, speech shocks
├── evaluation/            # Scoring rules, backtesting, scorecards
├── visualization/         # Maps, flows, diagnostic plots, styling
├── api/                   # FastAPI application & Pydantic schemas
└── dashboard/             # Interactive terminal research console
```

### Primary REST API Endpoints
- `GET /api/seats` : Return official ECI seat tallies and alliance breakdowns.
- `GET /api/constituencies` : List 234 assembly constituencies with regional filters.
- `GET /api/constituency/{ac_no}` : Return complete returns and demographic indicators for an AC.
- `POST /api/simulate/swing` : Execute real-time counterfactual uniform vote swing.
- `GET /api/polls/forensics` : Return forensic error decomposition of polling agencies.
- `GET /api/speeches` : Return leader speech stylometrics and framing scores.
- `GET /api/coalition/stability` : Return Shapley values and viable governing coalitions.
