"""Test that parsing Percolator input files (parquet) works correctly"""

import pandas as pd
import pyarrow.parquet as pq
import pytest

import mokapot


@pytest.fixture
def std_parquet(tmp_path):
    """Create a standard pin file"""
    out_file = tmp_path / "std_pin.parquet"
    df = pd.DataFrame([
        {
            "sPeCid": "DefaultDirection",
            "LaBel": "0",
            "pepTide": "-",
            "sCore": "-",
            "scanNR": "1",
            "pRoteins": "-",
        },
        {
            "sPeCid": "a",
            "LaBel": "1",
            "pepTide": "ABC",
            "sCore": "5",
            "scanNR": "2",
            "pRoteins": "protein1",
        },
        {
            "sPeCid": "b",
            "LaBel": "-1",
            "pepTide": "CBA",
            "sCore": "10",
            "scanNR": "3",
            "pRoteins": "decoy_protein1",
        },
    ])
    df.to_parquet(out_file, index=False)
    return out_file


def test_parquet_parsing(std_parquet):
    """Test pin parsing"""
    datasets = mokapot.read_pin(
        std_parquet,
        max_workers=4,
    )
    df = pq.read_table(std_parquet).to_pandas()
    assert len(datasets) == 1

    pd.testing.assert_frame_equal(
        df.loc[:, ("sCore",)], df.loc[:, datasets[0].feature_columns]
    )
    pd.testing.assert_series_equal(
        df.loc[:, "sPeCid"], df.loc[:, datasets[0].specId_column]
    )
    pd.testing.assert_series_equal(
        df.loc[:, "pRoteins"], df.loc[:, datasets[0].protein_column]
    )
    pd.testing.assert_frame_equal(
        df.loc[:, ("scanNR",)], df.loc[:, datasets[0].spectrum_columns]
    )
