"""
Exploralytics
------------

A Python toolkit for data exploration and visualization.

Quick Start:
    from exploralytics import Visualizer
    
    viz = Visualizer()
    viz.plot_histograms(df, title='My Analysis')
    viz.plot_correlation(df)

Main features:
- Simple interface for common data visualizations
- Consistent styling across all plots
- Built on Plotly for interactive plots
- Smart defaults with easy customization

For examples and documentation:
https://github.com/JpCurada/exploralytics
"""

from .visualize import Visualizer

__version__ = '1.0.1'  # Updated version
__author__ = 'John Paul Curada'
__email__ = 'johncurada.work@gmail.com'

__all__ = ['Visualizer']