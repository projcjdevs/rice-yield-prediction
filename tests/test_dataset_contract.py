from pathlib import Path

import pandas as pd

from src.data.merge import build_merged_dataset


EXPECTED_COLUMNS = [
    'season_period',
    'ecosystem',
    'province',
    'island_group',
    'yield_mt_ha',
    'area_harvested_ha',
    'n_application_rate',
    'p_application_rate',
    'k_application_rate',
    'grade_ammophos_16_20_0_kg_ha',
    'grade_ammosul_21_0_0_kg_ha',
    'grade_complete_14_14_14_kg_ha',
    'grade_mop_0_0_60_kg_ha',
    'grade_urea_46_0_0_kg_ha',
    'total_fertilizer_kg_ha',
    'fertilizer_diversification_index',
    'rainfall_mm',
    'temp_max_c',
    'temp_min_c',
    'solar_radiation_mj_m2',
    'soil_ph',
]


def test_contract_1_dataset_is_complete_and_valid():
    df = build_merged_dataset(
        data_dir=Path('data/raw'),
        output_path=Path('data/processed/merged_rice_yield_dataset.csv'),
        write_output=False,
    )

    assert list(df.columns) == EXPECTED_COLUMNS
    assert len(df) == 287
    assert df['yield_mt_ha'].notna().all()
    assert df['soil_ph'].between(5.0, 6.5).all()
    assert df['province'].notna().all()
    assert df.groupby(['province', 'ecosystem'])['soil_ph'].nunique().eq(1).all()
    assert df['island_group'].isin(['Luzon', 'Visayas', 'Mindanao']).all()
