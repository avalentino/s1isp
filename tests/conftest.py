"""Common fixtures."""

import json
import pathlib

import numpy as np
import pytest

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
    data = np.load(filename, allow_pickle=True)
    return {k: v.item() if "header" in k else v for k, v in data.items()}


@pytest.fixture
def noise_data():
    filename = DATAROOT / "000000-noise.dat"
    with open(filename, "rb") as fd:
        return fd.read()


@pytest.fixture
def noise_ref_data():
    # keys: "primary_header", "secondary_header", "udf"
    filename = DATAROOT / "000000-noise.npz"
    data = np.load(filename, allow_pickle=True)
    return {k: v.item() if "header" in k else v for k, v in data.items()}


@pytest.fixture
def echo_data():
    filename = DATAROOT / "000408-echo.dat"
    with open(filename, "rb") as fd:
        return fd.read()


@pytest.fixture
def echo_ref_data():
    # keys: "primary_header", "secondary_header", "udf"
    filename = DATAROOT / "000408-echo.npz"
    data = np.load(filename, allow_pickle=True)
    return {k: v.item() if "header" in k else v for k, v in data.items()}


@pytest.fixture
def fdbaq_reconstruction_lut():
    filename = DATAROOT / "reconstruction-lut.json"
    with open(filename) as fd:
        return json.load(fd)
