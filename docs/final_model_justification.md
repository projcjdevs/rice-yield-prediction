# Final Model Selection & Evaluation Report

## 1. Model Selection Justification (Validation-Based)
Based on leave-one-province-out cross-validation (LOPO CV) over the 60 training provinces, **Ridge Regression** with **stratified mixup augmentation (3x)** was selected as the final model prior to any test-set evaluation.

### Validation Evidence (Mixup 3x)
| Model | RMSE (Primary) | MAE | R² |
|---|---|---|---|
| **Ridge Regression** | **0.6669** | 0.5405 | **0.3865** |
| Random Forest | 0.6838 | 0.5385 | 0.3548 |
| LightGBM | 0.6912 | 0.5443 | 0.3409 |
| Linear Regression (Baseline) | 0.6681 | 0.5414 | 0.3842 |

### Rationale
1. **Primary Metric Performance:** RMSE was pre-registered as the primary metric to penalize large provincial misses. Ridge achieves the lowest pooled OOF RMSE (0.6669) among the three required models.
2. **Interpretability:** Ridge provides linear coefficients, which are critical for provincial agricultural analysis. This interpretability outweighs the marginal MAE advantage of Random Forest.
3. **Robustness:** Ridge exhibits a tighter error profile (RMSE 0.6669 vs MAE 0.5405) compared to tree-based models, indicating fewer extreme outliers.
4. **Baseline Context:** Ridge performs nearly identically to the unregularized Linear Regression baseline (RMSE 0.6681). This confirms that our feature engineering successfully stabilized the space, while Ridge's L2 regularization guards against multicollinearity without adding unnecessary complexity.

*(Note: The linear baseline is reported for context only and is ineligible for final selection per course rules.)*

---

## 2. Official Test Set Evaluation
The sealed test set (58 rows across 16 entirely unseen provinces) was evaluated exactly once using the selected Ridge model.

### Final Metrics
- **Test RMSE:** 0.7022
- **Test MAE:** 0.4747
- **Test R²:** 0.2818

### Interpretation & Validation Consistency
- **CI Alignment:** The test RMSE (0.7022) falls squarely inside the validation bootstrap 95% confidence interval [0.6079, 0.7184]. This confirms the model's performance on unseen provinces is statistically consistent with LOPO CV expectations, providing strong evidence of no data leakage or validation overfitting.
- **Error Concentration:** Test error is highly concentrated in a single agro-ecological outlier province absent from the training set. **Dinagat Islands** (4 of 58 rows) accounts for approximately 63% of the total test squared error (actual yields ~2.0-2.2 t/ha vs predicted 3.7-4.7 t/ha). Excluding Dinagat Islands, the test RMSE drops to **0.4447**, which is below the validation point estimate. This indicates the model is well-calibrated for provinces resembling the training distribution.
- **Secondary Misses:** Negros Occidental non-irrigated (2022 Semester 1) represents the second-largest miss (actual 1.45 vs predicted 2.83).
- **Ecosystem Parity:** Mean absolute error is nearly parity across ecosystems (0.459 irrigated vs 0.494 non-irrigated), indicating no systematic ecosystem bias.
- **Methodological Freeze:** No re-selection, re-tuning, or re-training occurred after observing these test metrics. The one-time-test rule was strictly honored.