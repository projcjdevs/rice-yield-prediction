# Copula-based synthetic rows for the rice yield project.

import numpy as np
import pandas as pd


def _build_synthesizer(df):
    """Version-tolerant construction: sdv changed its metadata API in 1.x.
    Note: sdv calls the Gaussian marginal 'norm' (maps to GaussianUnivariate)."""
    from sdv.single_table import GaussianCopulaSynthesizer

    try:
        from sdv.metadata import Metadata
        try:
            metadata = Metadata.detect_from_dataframe(data=df, table_name="fold")
        except TypeError:
            metadata = Metadata()
            metadata.detect_from_dataframe(df, table_name="fold")
    except Exception:
        from sdv.metadata import SingleTableMetadata
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(df)

    num_cols = [c for c in df.columns if df[c].dtype.kind == "f"]
    try:
        return GaussianCopulaSynthesizer(metadata, default_distribution="norm")
    except TypeError:
        return GaussianCopulaSynthesizer(
            metadata, numerical_distributions={c: "norm" for c in num_cols}
        )

def copula_augment(df_fold, multiplier, random_state=None, synth_weight=0.5):
    """Return (synthetic_raw_df, synthetic_weights) for a raw fold dataframe
    that contains the 14 feature columns PLUS yield_mt_ha."""
    n = len(df_fold)
    k = int(round((multiplier - 1) * n))
    cols = list(df_fold.columns)

    if k <= 0:
        return df_fold.iloc[0:0].copy(), np.full(0, synth_weight)

    synthesizer = _build_synthesizer(df_fold)
    synthesizer.fit(df_fold)

    if random_state is not None:
        np.random.seed(random_state)

    df_s = synthesizer.sample(num_rows=k)

    num_cols = [c for c in cols if df_fold[c].dtype.kind == "f"]
    for c in num_cols:
        df_s[c] = df_s[c].clip(df_fold[c].min(), df_fold[c].max())

    return df_s[cols].reset_index(drop=True), np.full(k, synth_weight)