# Final Model Selection Justification

## 1. The Decision (Validation-Based)
Based on the leave-one-province-out cross-validation (LOPO CV) metrics across the 60 training provinces, **Ridge Regression** is selected as the final model for deployment and official test-set evaluation.

### Validation Evidence (Mixup 3x augmentation)
| Model | RMSE (Primary) | MAE | R² |
|---|---|---|---|
| **Ridge Regression** | **0.6669** | 0.5405 | **0.3865** |
| Random Forest | 0.6838 | **0.5385** | 0.3548 |
| LightGBM | 0.6912 | 0.5443 | 0.3409 |
| Linear Regression (Baseline) | 0.6681 | 0.5414 | 0.3842 |

### Justification
1. **Primary Metric Performance:** RMSE was pre-registered as the primary metric to penalize large provincial misses. Ridge achieves the lowest pooled OOF RMSE (0.6669) and the highest R² (0.3865) among the three required models.
2. **Interpretability:** Unlike Random Forest and LightGBM, Ridge Regression provides linear coefficients. In the context of agricultural policy and provincial yield analysis, understanding the direction and magnitude of feature impacts (e.g., fertilizer application vs. climate variables) is a critical requirement that outweighs marginal performance differences.
3. **Robustness:** Ridge demonstrates a tighter error profile (RMSE 0.6669 vs MAE 0.5405) compared to Random Forest, indicating fewer extreme outliers in its predictions.
4. **Baseline Context:** Ridge performs nearly identically to the unregularized Linear Regression baseline (RMSE 0.6681). This confirms that our feature engineering (stratified mixup, log1p transformation, standard scaling) successfully stabilized the feature space, while Ridge's L2 regularization provides the optimal guard against multicollinearity without unnecessary complexity.

*(Note: The test set has not yet been evaluated. The following section will record the one-time test metrics.)*

---

## 2. Official Test Set Evaluation
### Final Results (Sealed Test Set: 58 rows, 16 unseen provinces)
- **RMSE:** 0.7022
- **MAE:** 0.4747
- **R²:** 0.2818

*(See `docs/figures/test_set_residuals.png` for actual-vs-predicted and residual diagnostic plots.)*