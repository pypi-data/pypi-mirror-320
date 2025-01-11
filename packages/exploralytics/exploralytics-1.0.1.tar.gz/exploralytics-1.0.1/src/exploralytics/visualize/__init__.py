"""
Exploralytics Visualization Module
--------------------------------

A powerful toolkit for data exploration and visualization using Plotly.

Quick Start:
    from exploralytics import Visualizer

    # Initialize visualizer with custom settings
    viz = Visualizer(
        color="#94C973",
        height=768,
        width=1366,
        template="simple_white",
        title_bold=True
    )

    # Multiple histograms with statistics
    fig = viz.plot_histograms(
        df,
        title='Distribution Analysis',
        num_cols=2,
        show_mean=True,
        show_median=True
    )

    # Correlation heatmap
    fig = viz.plot_correlation_map(
        df,
        title='Feature Correlations'
    )

    # Horizontal bar plot with highlights
    fig = viz.plot_hbar(
        df,
        x_col='category',
        y_col='values',
        highlight_top_n=(3, "green"),
        highlight_low_n=(2, "red")
    )

    # Dot plot with reference line
    fig = viz.plot_dot(
        df,
        x_col='category',
        y_col='values',
        add_hline_at=('Target', 50)
    )

For more examples and documentation:
https://github.com/jpcurada/exploralytics
"""

from .visualizer import Visualizer
from .utils import (
    identify_num_rows,
    highlight_bars_colors,
    add_footer
)

__all__ = [
    # Main visualization class
    'Visualizer',

    # Utility functions
    'identify_num_rows',
    'highlight_bars_colors',
    'add_footer'
]