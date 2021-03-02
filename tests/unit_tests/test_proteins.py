"""Test that we can parse a FASTA file correctly"""
import pytest
from mokapot import FastaProteins


@pytest.fixture
def missing_fasta(tmp_path):
    """Create a fasta file with a missing entry"""
    out_file = tmp_path / "missing.fasta"
    with open(out_file, "w+") as fasta_ref:
        fasta_ref.write(
            ">sp|test_1|test_1\n"
            ">sp|test_2|test_2\n"
            "TKDIPIIFLSAVNIDKRFITKGYNSGGADY"
        )

    return out_file


@pytest.fixture
def target_fasta(tmp_path):
    """A simple target FASTA"""
    out_file = tmp_path / "target.fasta"
    with open(out_file, "w+") as fasta_ref:
        fasta_ref.write(
            ">wf|target1\n"
            "MABCDEFGHIJKLMNOPQRSTUVWXYZKAAAAABRAAABKAAB\n"
            ">wf|target2\n"
            "MZYXWVUTSRQPONMLKJIHGFEDCBAKAAAAABRABABKAAB\n"
            ">wf|target3\n"
            "A" + "".join(["AB"] * 24) + "AK\n"
            ">wf|target4\n"
            "MABCDEFGHIJK"
        )

    return out_file


@pytest.fixture
def decoy_fasta(tmp_path):
    """A simple decoy FASTA"""
    out_file = tmp_path / "decoy.fasta"
    with open(out_file, "w+") as fasta_ref:
        fasta_ref.write(
            ">decoy_wf|target1\n"
            "MAFGHDCBEIJKLPMQNORSUYTVXWZKAAAABARAABAKABA\n"
            ">decoy_wf|target2\n"
            "MZYSVUXWTRQMPOLNKJGIFHBEDCAKAAAABARABBAKABA\n"
            ">wf|target3\n"
            "A" + "".join(["BA"] * 24) + "AK\n"
            ">decoy_wf|target4\n"
            "MAFGHDCBEIJK"
        )

    return out_file


def test_fasta_with_missing(missing_fasta):
    """Test that a fasta file can be parsed with missing entries

    See https://github.com/wfondrie/mokapot/issues/13
    """
    FastaProteins(missing_fasta)


def test_target_fasta(target_fasta):
    """Test that a FASTA file with only targets works"""
    long_pep = "A" + "".join(["AB"] * 24) + "AK"
    short_pep = "AAABK"

    # First the default parameters
    prot = FastaProteins(target_fasta)
    assert prot.decoy_prefix == "decoy_"
    assert not prot.has_decoys

    # Check the peptide_map
    # 0 missed cleavages
    assert "MABCDEFGHIJK" in prot.peptide_map.keys()
    # 1 missed cleavage
    assert "MABCDEFGHIJKLMNOPQR" in prot.peptide_map.keys()
    # 2 missed cleavages
    assert "MABCDEFGHIJKLMNOPQRSTUVWXYZK" in prot.peptide_map.keys()
    # too short
    assert short_pep not in prot.peptide_map.keys()
    # too long
    assert long_pep not in prot.peptide_map.keys()

    # Check the protein map:
    protein_map = {
        "wf|target1": "decoy_wf|target1",
        "wf|target2": "decoy_wf|target2",
        "wf|target4": "decoy_wf|target4",
    }
    assert prot.protein_map == protein_map

    # Check shared peptides:
    assert prot.shared_peptides == {"AAAAABR"}


def test_parameters(target_fasta):
    """Test that changing the parameters actually changes things."""
    long_pep = "A" + "".join(["AB"] * 24) + "AK"
    short_pep = "AAABK"

    prot = FastaProteins(
        target_fasta,
        missed_cleavages=0,
        clip_nterm_methionine=True,
        min_length=3,
        max_length=60,
        decoy_prefix="rev_",
    )
    assert prot.decoy_prefix == "rev_"
    assert not prot.has_decoys

    # Check the peptide_map
    # 0 missed cleavages
    assert "MABCDEFGHIJK" in prot.peptide_map.keys()
    assert "ABCDEFGHIJK" in prot.peptide_map.keys()
    # 1 missed cleavage
    assert "ABCDEFGHIJKLMNOPQR" not in prot.peptide_map.keys()
    # 2 missed cleavages
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZK" not in prot.peptide_map.keys()
    # too short
    assert short_pep in prot.peptide_map.keys()
    # too long
    assert long_pep in prot.peptide_map.keys()
    # grouped protein:
    assert "wf|target1, wf|target4" in prot.peptide_map.values()

    # Check the protein map:
    protein_map = {
        "wf|target1": "rev_wf|target1",
        "wf|target2": "rev_wf|target2",
        "wf|target3": "rev_wf|target3",
        "wf|target4": "rev_wf|target4",
    }
    assert prot.protein_map == protein_map

    # Check shared peptides:
    assert prot.shared_peptides == {"AAAAABR", "AAB"}


def test_decoy_fasta(target_fasta, decoy_fasta):
    """Test decoys can be provided and used."""
    # Try without targets:
    with pytest.raises(ValueError) as msg:
        FastaProteins(decoy_fasta)
        assert str(msg).startswith("Only decoy proteins were found")

    # Now do with both:
    prot = FastaProteins([target_fasta, decoy_fasta])

    # Check the peptide_map
    # A target sequence
    assert "MABCDEFGHIJK" in prot.peptide_map.keys()
    # A decoy sequence
    assert "MZYSVUXWTRQMPOLNK" in prot.peptide_map.keys()

    # Check the protein map:
    protein_map = {
        "wf|target1": "decoy_wf|target1",
        "wf|target2": "decoy_wf|target2",
        "wf|target4": "decoy_wf|target4",
    }
    assert prot.protein_map == protein_map