import pandas as pd
import plotly.graph_objects as go

def identify_num_rows(
    columns: list[str], 
    desired_num_col: int
) -> int:
    """
    Calculate how many rows are needed to display a set of plots in a grid layout.

    Determines the number of rows needed to fit all plots when organizing them into 
    columns. Handles both when plots divide evenly into columns and when they don't.

    Parameters
    ----------
    columns : list
        List of items that need to be arranged in a grid
    desired_num_col : int
        Number of columns to arrange the plots into

    Returns
    -------
    int
        Number of rows needed for the grid layout
    """
    # If plots divide evenly into columns, use simple division
    if (len(columns) % desired_num_col) == 0:
        num_rows = len(columns) // desired_num_col
    # If plots don't divide evenly, add an extra row to fit remaining plots
    else:
        num_rows = (len(columns) // desired_num_col) + 1
    
    return num_rows

# Utility function for creating colors
def highlight_bars_colors(
    highlight_top_n: tuple, 
    highlight_low_n: tuple, 
    data_length: pd.DataFrame
):
    """
    Create color array for highlighted bars.

    Parameters
    ----------
    highlight_top_n : tuple or None
        (n, color) for top n bars
    highlight_low_n : tuple or None
        (n, color) for bottom n bars
    data_length : int
        Total number of bars

    Returns
    -------
    list
        List of colors for each bar
    """
    # Initialize with default grey color
    colors = ['#E5E4E2'] * data_length

    # Apply highlighting for top n if specified
    if highlight_top_n:
        n, color = highlight_top_n
        colors[:n] = [color] * min(n, data_length)

    # Apply highlighting for bottom n if specified
    if highlight_low_n:
        n, color = highlight_low_n
        colors[-n:] = [color] * min(n, data_length)

    return colors

def add_footer(
    fig: go.Figure,
    footer_text: str,
    footer_url: str = None,
    footer_font_size: int = 10,
    footer_color: str = "gray",
    y_offset: float = -0.19,
    x_offset: float = 0
) -> go.Figure:
    """
    Add a footer to a Plotly figure with optional clickable link.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure to add the footer to
    footer_text : str
        The text to display in the footer
    footer_url : str, optional
        URL to link to in the footer. If provided, makes footer clickable
    footer_font_size : int, optional
        Size of the footer text (default: 10)
    footer_color : str, optional
        Color of the footer text (default: "gray")
    y_offset : float, optional
        Vertical position of footer relative to plot (default: -0.20)
    x_offset : float, optional
        Horizontal position of footer relative to plot (default: 0)

    Returns
    -------
    plotly.graph_objects.Figure
        Figure with added footer
    """
    # Create footer text with link if URL provided
    if footer_url:
        footer_html = f'<a href="{footer_url}" style="color: {footer_color};">{footer_text}</a>'
    else:
        footer_html = footer_text

    # Add footer annotation
    fig.add_annotation(
        text=footer_html,
        x=x_offset,          # Center horizontally
        y=y_offset,          # Position below plot
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=footer_font_size,
            color=footer_color
        ),
        align="left",
        clicktoshow=False
    )
    
    return fig

