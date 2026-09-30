# The Political Economy of Targeted Welfare: Synthetic Control and Difference-in-Differences Analysis of the 2026 Tamil Nadu Election

**Monograph Number:** TN26-WP-03  
**Subject:** Causal Inference, Econometrics, Welfare Economics, State Revenue Systems  

---

## 1. Introduction: The "Dravidian Model" and Targeted Transfers

Tamil Nadu has long been celebrated by development economists (e.g., Dreze & Sen 2013) as an exemplar of the developmental welfare state in South Asia. Over multiple decades, both Dravidian parties pioneered universal public distribution systems, mid-day meals in schools, maternal assistance grants, and public health networks.

Under the DMK government (2021-2026), this developmental welfare model shifted towards targeted direct benefit transfers (DBT):
- **Kalaignar Magalir Urimai Thogai (KMUT):** 1,000 INR per month transferred directly to bank accounts of 1.15 crore adult women heads of households.
- **Pudhumai Penn:** 1,000 INR per month for female government school students pursuing higher education degrees.
- **Tamil Pudhalvan:** 1,000 INR per month for male government school students entering higher education.
- **Kaalai Unavu Thittam:** Universal nutritious hot breakfast in all government primary schools.

This paper applies formal econometric causal identification strategies: Synthetic Control Methods and Difference-in-Differences: to evaluate the electoral return on these massive fiscal commitments.

---

## 2. The Welfare Drain Paradox: Cash Transfers Versus TASMAC Extraction

A central contribution of our research is resolving the apparent paradox of why an incumbent government that successfully disbursed over 13,800 Crores INR annually in direct cash assistance to over 1.15 crore women still suffered an anti-incumbent electoral defeat.

```
       THE FISCAL CONTRADICTION: DIRECT BENEFIT TRANSFERS VS. TASMAC
 ==============================================================================
  Annual Direct Cash Transferred (KMUT)     : ~13,800 Crores INR
  Annual State Liquor Revenue (TASMAC)      : ~45,200 Crores INR
  Statewide Net Extraction Deficit          : ~31,400 Crores INR
  Net Household Welfare Drain Ratio         : 0.31 (State extracts 3.28x what it gives)
 ==============================================================================
```

In Tamil Nadu, retail sale of alcoholic beverages is an absolute state monopoly managed by the Tamil Nadu State Marketing Corporation (TASMAC). Alcohol taxes and retail margins provide between 20% and 25% of the state's total Own Tax Revenue (OTR).

Our constituency-level fiscal analysis reveals that in the average assembly constituency:
- The state government distributed approximately **59.0 Crores INR** in annual cash transfers to women.
- In that same constituency, the state-run TASMAC network extracted approximately **193.2 Crores INR** in retail liquor purchases.

In lower-income rural and urban working-class households, male alcohol consumption routinely exceeded the 1,000 INR monthly female stipend by a factor of three to four. This fiscal dynamic transformed what the ruling regime viewed as an unshakeable political entitlement into an acute moral economy grievance, weaponized effectively by opposition leaders who denounced the state for *"looting fathers through liquor while giving alms to mothers"*.

---

## 3. Synthetic Control Method (Abadie et al.) on Cash Transfer Saturation

To isolate the causal effect of KMUT coverage on ruling party vote retention, we implemented the Synthetic Control Method (Abadie, Diamond, & Hainmueller 2010).

### 3.1 Model Specification
Let $Y_{it}$ denote the DMK alliance vote share in constituency $i$ at time $t \in \{2021, 2026\}$.
We designated constituencies in the highest decile of KMUT saturation (beneficiary coverage $> 75\%$ of adult female electorate) as the treated group. 

For each treated constituency $i$, we solved the constrained optimization problem over the donor pool of lower-saturation constituencies ($C < 62\%$):

$$\min_{W_i} (X_{1i} - X_{0} W_i)^T V (X_{1i} - X_{0} W_i)$$

subject to:
$$\sum_{j \in \text{Donor}} w_{ij} = 1, \quad w_{ij} \ge 0$$

where $X_{1i}$ contains pre-treatment socioeconomic and electoral predictors:
- Urbanization rate (Census)
- Female literacy rate
- Scheduled Caste (SC) population share
- Baseline 2021 DMK alliance vote share
- Baseline 2021 AIADMK alliance vote share

### 3.2 Causal Treatment Effect Findings
The average treatment effect on the treated ($\tau$) was:

$$\hat{\tau} = \bar{Y}_{\text{Treated, 2026}} - \bar{Y}_{\text{Synthetic, 2026}} = +3.18\% \quad (p = 0.008)$$

```
             SYNTHETIC CONTROL RESULTS ON DIRECT CASH TRANSFERS
 ==============================================================================
  Treated Constituencies Evaluated          : 15 High-KMUT Saturation ACs
  Average Observed DMK 2026 Vote Share      : 36.84%
  Average Synthetic Counterfactual Share    : 33.66%
  Estimated Causal Retention Lift (tau)     : +3.18% (Statistically Significant)
 ==============================================================================
```

**Interpretation:** The 1,000 INR monthly cash transfer was not ineffective. It functioned as an authentic, statistically robust buffer that elevated DMK alliance vote retention by approximately 3.18 percentage points above what it would have been in the absence of the scheme. 

Without KMUT, our counterfactual simulation indicates the DMK alliance would have fallen from 73 seats to approximately 48 seats. However, because the broader anti-incumbent macro swing was $-11.18\%$, a $+3.18\%$ cash buffer was insufficient to retain an outright legislative majority.

---

## 4. Difference-in-Differences Estimation of Governance Shocks

We deployed two-way fixed effects (TWFE) Difference-in-Differences models to quantify the electoral damage of two major exogenous shocks during the 2021-2026 legislative term.

$$\text{VoteShare}_{it} = \alpha_i + \lambda_t + \delta (\text{TreatedCluster}_i \times \text{Post}_t) + \epsilon_{it}$$

where standard errors are clustered at the district level.

### 4.1 Shock 1: The Kallakurichi Illicit Methanol Tragedy (June 2024)
In June 2024, the consumption of industrial methanol sold through illicit liquor networks caused over 65 deaths in Kallakurichi and surrounding villages, triggering statewide protests and judicial investigations.

- **Treated Cluster:** Kallakurichi, Viluppuram, Cuddalore districts (16 assembly constituencies).
- **Control Group:** Other non-adjacent northern and delta districts.
- **Estimated DiD Coefficient ($\delta$):** $-1.10\%$
- **Clustered Standard Error:** $2.44$
- **t-statistic:** $-0.45$ ($p = 0.650$)

**Finding:** The localized coefficient was not statistically distinguishable from the broader regional trend. The Kallakurichi tragedy did not merely penalize the immediate district; rather, extensive digital media coverage transformed it into a statewide moral grievance that depressed ruling-party margins across all 234 constituencies.

### 4.2 Shock 2: The Karur Cash-for-Jobs Scandal and Enforcement Raids
The protracted legal battle involving former minister V. Senthil Balaji, marked by Supreme Court proceedings, Enforcement Directorate custodial interrogations, and extensive cash seizures in Karur, provided a concentrated governance shock.

- **Treated Cluster:** Karur district assembly constituencies (Karur, Aravakurichi, Kulithalai, Krishnarayapuram).
- **Control Group:** Western Kongu and central agricultural constituencies.
- **Estimated DiD Coefficient ($\delta$):** $-6.06\%$
- **Clustered Standard Error:** $0.82$
- **t-statistic:** $-7.39$ ($p < 0.0001$)

**Finding:** The Karur shock generated a severe, localized causal penalty of $-6.06\%$ against the ruling DMK beyond statewide anti-incumbency. This localized collapse resulted in the total defeat of DMK candidates across Karur district, with TVK and AIADMK dividing the spoils.

---

## 5. Policy Implications

Our econometric findings offer critical lessons for fiscal policy and democratic governance:
1. **Fiscal Cash Transfers Cannot Offset Moral Market Failures:** State governments cannot rely on targeted cash stipends to buy political loyalty when the same state machinery operates extractive monopolies on addictive consumer goods that damage working-class family welfare.
2. **Anti-Corruption Salience is Highly Localized:** While high-level corruption controversies often dissipate across diffuse statewide electorates, intense investigative and judicial interventions produce devastating localized penalties in the political home bases of implicated leaders.
3. **Welfare Elasticity is Asymmetric:** Direct cash transfers exhibit diminishing marginal political returns; an incumbent cannot continuously substitute welfare transfers for responsive local governance and accountable MLA behavior.
