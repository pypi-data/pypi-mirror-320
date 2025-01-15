"""Tests for quickly package."""

import numpy as np
import pandas as pd
import pytest

from quickly import Quickly


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({"x": range(10), "y": range(10)})


def test_basic_line_plot(sample_df):
    """Test creating a basic line plot."""
    plot = Quickly.using(sample_df).x("x").y("y").line.plt()
    assert plot is not None


def test_scatter_plot_with_customization(sample_df):
    """Test creating a customized scatter plot."""
    plot = (
        Quickly.using(sample_df)
        .x("x")
        .y("y")
        .scatter.color("blue")
        .title("Test Plot")
        .plt()
    )
    assert plot is not None


def test_invalid_column_name(sample_df):
    """Test handling of invalid column names."""
    with pytest.raises(ValueError):
        Quickly.using(sample_df).x("invalid_column").y("y").plt()
