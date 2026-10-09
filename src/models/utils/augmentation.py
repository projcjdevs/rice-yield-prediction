# stratified mixup augmentation for tabular data
import numpy as np


def stratified_mixup(X, y, strata, multiplier, random_state=None,
                     synth_weight=0.5, alpha=0.4):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    strata = np.asarray(strata)
    rng = np.random.default_rng(random_state)

    n_real = X.shape[0]
    n_synth_total = int(round((multiplier - 1) * n_real))

    if n_synth_total <= 0: 
        return X.copy(), y.copy(), np.ones(n_real)

    unique = np.unique(strata)
    sizes = np.array([(strata == s).sum() for s in unique])
    per_stratum = np.floor(sizes / sizes.sum() * n_synth_total).astype(int)
    leftover = n_synth_total - per_stratum.sum()
    order = np.argsort(-sizes)
    for k in range(leftover): 
        per_stratum[order[k % len(order)]] += 1

    X_s, y_s = [], []
    for s, m_s in zip(unique, per_stratum):
        idx = np.where(strata == s)[0]
        if m_s == 0 or len(idx) < 2:
            continue
        for _ in range(m_s):
            i, j = rng.choice(idx, size=2, replace=False)
            lam = rng.beta(alpha, alpha)
            X_s.append(lam * X[i] + (1 - lam) * X[j])
            y_s.append(lam * y[i] + (1 - lam) * y[j])

    X_s = np.vstack(X_s) if X_s else np.empty((0, X.shape[1]))
    y_s = np.asarray(y_s, dtype=float) if y_s else np.empty(0)

    X_aug = np.vstack([X, X_s])
    y_aug = np.concatenate([y, y_s])
    weights = np.concatenate([np.ones(n_real), np.full(len(y_s), synth_weight)])
    return X_aug, y_aug, weights