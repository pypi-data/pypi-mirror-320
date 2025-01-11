# Exploralytics

[![PyPI Latest Release](https://img.shields.io/pypi/v/exploralytics.svg)](https://pypi.org/project/exploralytics/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue.svg)](https://www.linkedin.com/in/jpcurada/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black.svg)](https://github.com/JpCurada)

## What is it?
A Python toolkit that streamlines the creation of Plotly visualizations for exploratory data analysis (EDA). Built to simplify the visualization workflow, Exploralytics provides an intuitive interface for creating common EDA plots like histograms, correlation matrices, and bar charts with consistent styling and formatting.

 > I created this to simplify my own workflow, but other data professionals might find it useful too.

## Main Features
Create sophisticated data visualizations with minimal code. Key features include:

- **Histogram Grid**: Analyze distributions of multiple numerical variables
- **Correlation Analysis**: 
  - Full correlation matrix heatmap
  - Target-focused correlation analysis
- **Bar Charts**: 
  - Horizontal bar plots with customizable highlighting
  - Dot plots with connecting lines
- **Consistent Styling**: Unified look across all visualizations
- **Customization Options**: Colors, dimensions, templates, and more

## Installation

Requires Python 3.9 or newer.

Using pip:
```bash
pip install exploralytics
```

Or install from source:
```bash
git clone https://github.com/jpcurada/exploralytics.git
cd exploralytics
pip install -e .
```

## Usage Examples

### Basic Usage

```python
from exploralytics.visualize import Visualizer
import pandas as pd

# Initialize visualizer with custom styling
viz = Visualizer(
    color="#94C973",  # Custom color
    height=768,       # Plot height
    width=1366,       # Plot width
    template="simple_white"  # Plotly template
)

# Create histogram grid
fig = viz.plot_histograms(
    df,
    title='Distribution Analysis',
    subtitle='Histogram of numerical variables',
    num_cols=2,
    show_mean=True,
    show_median=True
)
fig.show()

# Create correlation heatmap
fig = viz.plot_correlation_map(
    df,
    title='Correlation Analysis',
    subtitle='Relationship between variables'
)
fig.show()
```

### Advanced Features

```python
# Target-specific correlation analysis
fig = viz.plot_correlation_with_target(
    df,
    target_column='sales',
    title='Feature Importance',
    subtitle='Correlation with sales'
)

# Horizontal bar plot with highlights
fig = viz.plot_hbar(
    df,
    x_col='category',
    y_col='value',
    highlight_top_n=(3, '#2E75B6'),  # Highlight top 3 in blue
    highlight_low_n=(2, '#FF9999')   # Highlight bottom 2 in red
)

# Dot plot with reference line
fig = viz.plot_dot(
    df,
    x_col='category',
    y_col='metric',
    add_hline_at=('Average', 75.5),
    top_n=10
)
```

## Customization Options

The `Visualizer` class accepts several parameters for customization:

```python
viz = Visualizer(
    color="#94C973",                    # Default color for plot elements
    height=768,                         # Plot height in pixels
    width=1366,                         # Plot width in pixels
    template="simple_white",            # Plotly template
    colorscale=px.colors.diverging.Earth,  # Color scale for heatmaps
    texts_font_style="Arial",           # Font family
    title_bold=True                     # Bold titles
)
```

## Dependencies
- pandas >= 1.3.0
- plotly >= 5.0.0
- numpy >= 1.20.0

## Development

Want to contribute? Here's how:

1. Fork the repository
2. Create a feature branch
```bash
git checkout -b feature/new-feature
```
3. Make your changes
4. Submit a pull request

## License
BSD License

## Support
For bugs, questions, or suggestions, please [open an issue](https://github.com/jpcurada/exploralytics/issues) on GitHub.

---
Created and maintained by John Paul Curada. Contributions welcome!

