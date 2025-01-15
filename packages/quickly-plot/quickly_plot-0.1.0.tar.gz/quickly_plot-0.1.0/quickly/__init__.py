"""
Quickly
=========================================

A Python library providing builder-pattern interface for creating matplotlib plots quickly and intuitively.

Basic Usage:
-----------
```python
from quickly import Quickly

# Create a basic line plot
Quickly.using(df).x("age").y("income").plt()

# Create a scatter plot with customization
Quickly.using(df).x("age").y("income").scatter.color("blue").title("Age vs Income").plt()

# Create a line plot with confidence intervals
Quickly.using(df).x("age", conf=0.95).y("income").line.plt()
```
"""

from quickly.core import Quickly, QuicklyPlot
from quickly.version import __version__

__all__ = ["Quickly", "QuicklyPlot"]

# Set default plotting style
import seaborn as sns

sns.set_theme(style="whitegrid")
