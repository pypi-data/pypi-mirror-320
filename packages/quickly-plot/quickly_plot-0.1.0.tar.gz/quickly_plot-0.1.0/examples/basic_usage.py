"""Basic usage examples for quickly package."""

import numpy as np
import pandas as pd

from quickly import Quickly

# Create sample data
df = pd.DataFrame(
    {
        "age": range(20, 60),
        "income": np.random.normal(50000, 10000, 40),
        "satisfaction": np.random.normal(7, 2, 40),
    }
)

# Basic line plot
Quickly.using(df).x("age").y("income").line.plt()

# Scatter plot with customization
Quickly.using(df).x("age").y("income").scatter.color("blue").title(
    "Age vs Income"
).plt()

# Multiple metrics
Quickly.using(df).x("age").y(["income", "satisfaction"]).line.title(
    "Multiple Metrics"
).plt()

# With confidence intervals
Quickly.using(df).x("age", conf=0.95).y("income").line.title(
    "Income by Age (95% CI)"
).plt()
