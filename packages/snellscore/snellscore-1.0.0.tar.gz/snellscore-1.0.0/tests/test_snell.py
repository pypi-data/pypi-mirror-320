#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2024-2025 Igor Loschinin.
# Distributed under the lgplv3 software license, see the accompanying
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.

__author__ = "Igor Loschinin (igor.loschinin@gmail.com)"

import pytest
import pandas as pd

from .. import Snell


@pytest.fixture
def example_table():
    """Fixture providing a sample frequency table for testing."""

    data = {
        "Category A": [10, 20, 30],
        "Category B": [15, 25, 35],
        "Category C": [20, 30, 40]
    }
    return pd.DataFrame(data, index=["Group 1", "Group 2", "Group 3"])


@pytest.fixture
def snell_instance():
    """Fixture providing a Snell instance."""

    return Snell(standard=True)


def test_initialize_snell(snell_instance):
    """Test initialization of the Snell object."""

    assert snell_instance._standard is True
    assert snell_instance._score is None
    assert snell_instance._score_std is None


def test_build_cumprob(example_table):
    """Test the _build_cumprob static method."""

    noncum_probabilities = example_table.div(example_table.sum(axis=1), axis=0)
    expected = noncum_probabilities.cumsum(axis=1)
    result = Snell._build_cumprob(noncum_probabilities)
    pd.testing.assert_frame_equal(result, expected)


def test_calc_pairwise_adjusted_probs(example_table):
    """Test the _calc_pairwise_adjusted_probs static method."""

    noncum_probabilities = example_table.div(example_table.sum(axis=1), axis=0)
    cum_probabilities = Snell._build_cumprob(noncum_probabilities)
    expected = (
            (example_table.iloc[:, :-1] + example_table.iloc[:, 1:].values)
            * cum_probabilities.iloc[:, :-1]
    ).sum(axis=0)
    result = Snell._calc_pairwise_adjusted_probs(
        example_table, cum_probabilities
    )
    pd.testing.assert_series_equal(result, expected)


def test_run(example_table, snell_instance):
    """Test the main run method of the Snell class."""

    snell_instance.run(example_table)
    # Ensure scores and standardized scores are calculated
    assert snell_instance.score is not None
    assert snell_instance.score_standard is not None

    # Verify the scores have the correct length
    assert len(snell_instance.score) == example_table.shape[1]
    assert len(snell_instance.score_standard) == example_table.shape[1]


def test_standardization():
    """Test the _standardization static method."""

    scores = pd.Series([0, 1, 2, 3, 4])
    expected = pd.Series([0, 25, 50, 75, 100], dtype="Int16")
    result = Snell._standardization(scores)
    pd.testing.assert_series_equal(result, expected)


def test_calc_scores(example_table, snell_instance):
    """Test the _calc_scores method."""

    noncum_probabilities = example_table.div(example_table.sum(axis=1), axis=0)
    cum_probabilities = Snell._build_cumprob(noncum_probabilities)
    pairwise_adjusted_probs = Snell._calc_pairwise_adjusted_probs(
        example_table, cum_probabilities
    )
    ranges = snell_instance._ranges(
        example_table.sum(axis=0), pairwise_adjusted_probs
    )
    boundaries = snell_instance._boundaries(ranges)

    result = snell_instance._calc_scores(
        boundaries, noncum_probabilities, example_table.sum(axis=0)
    )

    assert len(result) == len(example_table.columns)
    assert isinstance(result, pd.Series)

    # Further validation can involve checking ranges, boundaries, and
    # deflection computations.
