"""Common fixtures."""

import json
import pathlib

import pytest
import numpy as np


DATAROOT = pathlib.Path(__file__).parent / "data"


@pytest.fixture
def txcal_data():
    filename = DATAROOT / "000008-txcal.dat"
    with open(filename, "rb") as fd:
        return fd.read()


@pytest.fixture
def txcal_ref_data():
    # keys: "primary_header", "secondary_header", "udf"
    filename = DATAROOT / "000008-txcal.npz"
    return dict(np.load(filename, allow_pickle=True))


@pytest.fixture
def noise_data():
    filename = DATAROOT / "000000-noise.dat"
    with open(filename, "rb") as fd:
        return fd.read()


@pytest.fixture
def noise_ref_data():
    # keys: "primary_header", "secondary_header", "udf"
    filename = DATAROOT / "000000-noise.npz"
    return dict(np.load(filename, allow_pickle=True))


@pytest.fixture
def fdbaq_reconstruction_lut():
    filename = DATAROOT / "reconstruction-lut.json"
    with open(filename) as fd:
        return json.load(fd)
