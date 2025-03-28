"""
These tests verify that the dataset classes are functioning properly.
"""

import numpy as np
import pandas as pd

from mokapot import LinearPsmDataset, OnDiskPsmDataset
from mokapot.dataset.base import update_labels


def test_linear_init(psm_df_6):
    """Test that a LinearPsm Dataset initializes correctly"""
    dat = psm_df_6.copy()
    dset = LinearPsmDataset(
        psms=dat,
        target_column="target",
        spectrum_columns=["spectrum"],
        peptide_column="peptide",
        feature_columns=None,
        copy_data=True,
    )

    # pd.testing.assert_frame_equal(dset.data, psm_df_6)
    # RN they are not equal bc I am adding a colum to denote the unique id
    # that is now required for the confidence estimation.
    # - jspp 2024-12-06

    # Verify that changing the original dataframe does not change the
    # the LinearPsmDataset object.
    dat["target"] = [1, 0] * 3
    pd.testing.assert_series_equal(dset.data["target"], psm_df_6["target"])

    # Check the public attributes
    _features = ["feature_1", "feature_2"]
    _metadata = ["target", "spectrum", "peptide", "protein"]

    # TODO: decide what the API should be here ... and re-make this test using
    # the on disk psm dataset
    # pd.testing.assert_frame_equal(
    #     dset.spectra_dataframe,
    #     psm_df_6.loc[:, ["spectrum"]],
    # )
    # pd.testing.assert_series_equal(dset.peptides, psm_df_6.loc[:, "peptide"])
    # pd.testing.assert_frame_equal(dset.features, psm_df_6.loc[:, features])
    # pd.testing.assert_frame_equal(dset.metadata, psm_df_6.loc[:, metadata])
    # assert dset.columns == psm_df_6.columns.tolist()
    # assert np.array_equal(dset.targets, psm_df_6["target"].values)
    # assert not dset.has_proteins


def test_update_labels(psm_df_6):
    """Test that the _update_labels() methods are working"""
    scores = np.array([6, 5, 3, 3, 2, 1])
    real_labs = np.array([1, 1, 0, -1, -1, -1])
    new_labs = update_labels(scores, psm_df_6["target"], eval_fdr=0.5)
    assert np.array_equal(real_labs, new_labs)


def test_hash_row():
    # Q: what is this meant to test? Only that hashing is constant?
    # It would be good to have this test (or another) check that its
    # consistent from the parsing time.
    x = np.array(
        ["test.mzML", 870, 5902.639978936955, 890.522815122875], dtype=object
    )
    assert OnDiskPsmDataset._hash_row(x) == 4196757312

    x = np.array(
        [
            "test.mzML",
            np.int64(870),
            np.float64(5902.639978936955),
            np.float64(890.522815122875),
        ],
        dtype=object,
    )
    assert OnDiskPsmDataset._hash_row(x) == 4196757312
