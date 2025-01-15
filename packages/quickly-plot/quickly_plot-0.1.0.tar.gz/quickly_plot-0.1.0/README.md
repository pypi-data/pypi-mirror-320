# Quickly 📊

A fluent interface for matplotlib that makes plotting as simple as writing a sentence.

## Installation

```bash
pip install quickly-plot
```

## Usage

```python
from quickly import Quickly
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'age': range(20, 60),
    'income': range(30000, 70000, 1000)
})

# Create different types of plots
Quickly.using(df).x("age").y("income").line.plt()
Quickly.using(df).x("age").y("income").scatter.plt()
Quickly.using(df).x("age").y("income").bar.plt()

# Add customization
Quickly.using(df) \
    .x("age") \
    .y("income") \
    .scatter \
    .color("blue") \
    .title("Age vs Income") \
    .plt()

# Plot with confidence intervals
Quickly.using(df) \
    .x("age", conf=0.95) \
    .y("income") \
    .line \
    .plt()
```

## Features

- Fluent interface with method chaining
- Multiple plot types (line, scatter, bar, histogram, box, violin)
- Built-in confidence intervals
- Easy customization (colors, styles, titles)
- Seaborn integration

## License

MIT License