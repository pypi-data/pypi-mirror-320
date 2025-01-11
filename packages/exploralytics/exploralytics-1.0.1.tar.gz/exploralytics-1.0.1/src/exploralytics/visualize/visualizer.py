import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
from plotly.subplots import make_subplots

from .utils import (
    identify_num_rows,
    highlight_bars_colors,
    add_footer
)

class Visualizer:
    """
    A class to create and customize data visualizations using Plotly.

    This class provides methods to generate various plots with consistent styling and formatting. It allows customization of plot colors, dimensions, and templates.

    Attributes
    ----------
    color : str
        Color code for plot elements (default: "#94C973")
    height : int
        Height of the plot in pixels (default: 768)
    width : int
        Width of the plot in pixels (default: 1366)
    template : str
        Plotly template name (default: "plotly_white")
    """

    def __init__(
        self, 
        color = "#94C973", 
        height = 768, width = 1366, 
        template = "simple_white", 
        colorscale=px.colors.diverging.Earth,
        texts_font_style: str = None,
        title_bold: bool = False, 
    ): 
        # Initialize visualization parameters
        self.color = color          # Set default color for plot elements
        self.height = height        # Set default plot height
        self.width = width          # Set default plot width
        self.template = template    # Set default plotly template
        self.colorscale = colorscale
        self.font_family = texts_font_style
        self.title_bold = title_bold
        
    def _get_base_layout_config(self, title: str, subtitle: str) -> dict:
        """
        Create a base layout configuration for Plotly figures.

        Args:
            title (str): title of the plot
            subtitle (str): subtitle of the plot

        Returns:
            dict: dictionary containing layout configuration
        """

        return dict(
            # Title configuration
            title_text=f"<b>{title}</b><br><sup>{subtitle}</sup>" if self.title_bold else f"{title}<br><sup>{subtitle}</sup>",  # Set title and subtitle text with optional bold
            title_x=0.5,  # Center title horizontally
            
            # General figure settings
            showlegend=False,  # Hide legend by default
            height=self.height,  # Set figure height from class attribute
            width=self.width,  # Set figure width from class attribute
            template=self.template,  # Use template defined in class
            
            # Hover label settings
            hoverlabel_font_family=self.font_family,  # Set font family for hover labels
            
            # X-axis settings
            xaxis_title_font_family=self.font_family,  # Set font family for x-axis title
            xaxis_tickfont_family=self.font_family,  # Set font family for x-axis tick labels
            xaxis_ticks="",  # Remove x-axis tick marks
            xaxis_showline=False,  # Remove x-axis line
            xaxis_ticklabelstandoff=10,  # Increase distance between tick labels and axis line
            xaxis_zeroline = False,  # Hide x-axis zero line
            
            # Y-axis settings
            yaxis_title_font_family=self.font_family,  # Set font family for y-axis title
            yaxis_tickfont_family=self.font_family,  # Set font family for y-axis tick labels
            yaxis_ticks="",  # Remove y-axis tick marks
            yaxis_showline=False,  # Remove x-axis line
            yaxis_ticklabelstandoff=10,  # Increase distance between tick labels and axis line
            yaxis_zeroline = False,  # Hide y-axis zero line
        )

    def plot_histograms(
        self, 
        df: pd.DataFrame, 
        specific_cols: list[str] = [], 
        num_cols: int = 1, 
        title: str = 'How distributed the numerical values are?', 
        subtitle: str = 'Histogram of each column with numerical data type',
        footer: str = None, 
        show_mean: bool = False, 
        show_median: bool = False,
    ) -> go.Figure:
        """
        Create multiple histogram subplots for numerical columns in a dataframe.

        Creates a grid of histograms showing the distribution of numerical data. Can optionally show mean and median lines on each histogram.

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataframe containing the data to plot
        specific_cols : list, optional
            List of specific columns to plot (default: empty list, plots all numerical columns)
        num_cols : int, optional
            Number of columns in the subplot grid (default: 1)
        title : str, optional
            Main title of the plot
        subtitle : str, optional
            Subtitle of the plot
        footer : str, optional
            Text to show at bottom of plot
        show_mean : bool, optional
            Whether to show mean line on histograms (default: False)
        show_median : bool, optional
            Whether to show median line on histograms (default: False)
        font_family : str, optional
            Font family for text elements (default: None)
        title_bold : bool, optional
            Whether to make title text bold (default: False)
        
        Returns
        -------
        plotly.graph_objects.Figure
            Figure containing the histogram subplots
        """

        # Select columns based on input: either use specific columns or all numerical columns
        if len(specific_cols) >= 1:
            numerical_columns = [column for column in specific_cols if df[column].dtypes in ['int64', 'float64']]
        else:
            numerical_columns = df.select_dtypes(include=np.number).columns.tolist()

        # Calculate number of rows needed based on number of columns and subplots
        num_rows = identify_num_rows(numerical_columns, desired_num_col=num_cols)
    
        # Create subplot grid
        fig = make_subplots(rows=num_rows,
                          cols=num_cols,
                          subplot_titles=numerical_columns,
                          )

        # Create histogram for each numerical column
        for index, col_name in enumerate(numerical_columns):
            # Calculate subplot position
            row = index // num_cols + 1    # Determine row number for current subplot
            col = index % num_cols + 1     # Determine column number for current subplot

            # Add histogram trace
            fig.add_trace(go.Histogram(x=df[col_name],
                                  autobinx=True,
                                  marker_color=self.color,
                                  name=col_name,
                                  hovertemplate="Interval: %{x}<br>Count: %{y}<extra></extra>"
                                  ),
                      row=row,
                      col=col)
          
            # Add mean line if requested
            if show_mean:
                fig.add_vline(x=df[col_name].mean(),
                            line_color="grey",  # Changed color for visibility
                            line_dash="solid",
                            line_width=2,      # Made line thicker
                            row=row,
                            col=col,
                          )
                
            # Add median line if requested
            if show_median:
                fig.add_vline(x=df[col_name].median(),
                            line_color="grey",  # Changed color for visibility
                            line_dash="dash",
                            line_width=2,      # Made line thicker
                            row=row,
                            col=col,
                          )

        # Apply the layout configuration
        fig.update_layout(
            # Title configuration
            title_text=f"<b>{title}</b><br><sup>{subtitle}</sup>" if self.title_bold else f"{title}<br><sup>{subtitle}</sup>",  # Set title and subtitle text with optional bold
            title_x=0.5,  # Center title horizontally
            
            # General figure settings
            showlegend=False,  # Hide legend by default
            height=self.height,  # Set figure height from class attribute
            width=self.width,  # Set figure width from class attribute
            template=self.template,  # Use template defined in class
            
            # Hover label settings
            hoverlabel_font_family=self.font_family,  # Set font family for hover labels
            
            # X-axis settings
            xaxis_title_font_family=self.font_family,  # Set font family for x-axis title
            xaxis_tickfont_family=self.font_family,  # Set font family for x-axis tick labels
        )

        # Add optional footer
        if footer is not None:
          add_footer(fig, footer, font_family=self.font_family)
        
        return fig
    
    def plot_correlation_map(
        self, 
        df: pd.DataFrame, 
        title: str = 'How correlated the numerical values are?',
        subtitle: str = 'Correlation matrix of columns with numerical data type',
        footer: str = None
    ) -> go.Figure:
        """
        Create a correlation matrix heatmap showing relationships between numerical columns.

        Generates a triangular heatmap visualization where each cell shows the correlation between two variables. 
        Only shows the lower triangle to avoid redundancy. 
        Includes hover text and annotations for correlation values.

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataframe containing the numerical columns to correlate
        title : str, optional
            Main title for the plot (default: 'How correlated the numerical values are?')
        subtitle : str, optional
            Subtitle to display below main title (default: 'Correlation matrix of columns with numerical data type')
        footer : str, optional
            Text to show at bottom of plot

        Returns
        -------
        plotly.graph_objects.Figure
            Figure containing the correlation heatmap
        """
        # Calculate correlation matrix and round values to 2 decimal places
        corr = df.corr().round(2)  
        
        # Create mask for upper triangle to avoid redundant information
        mask = np.triu(np.ones_like(corr, dtype=bool))
        
        # Apply mask to correlation matrix - sets upper triangle to NaN
        df_mask = corr.mask(mask)

        # Create custom hover text showing correlation between each pair of variables
        hovertext = [[f"{col1} vs {col2}<br>Correlation: {val:.2f}" 
                      if not pd.isna(val) else "" 
                      for col2, val in zip(df_mask.columns, row)]
                    for col1, row in zip(df_mask.index, df_mask.values)]

        # Create annotated heatmap with custom settings
        fig = ff.create_annotated_heatmap(
            z=df_mask.to_numpy(),           # Correlation values
            x=df_mask.columns.tolist(),     # Column names for x-axis
            y=df_mask.columns.tolist(),     # Column names for y-axis
            colorscale=self.colorscale,     # Color scheme for heatmap
            showscale=True,                 # Show color scale
            ygap=1,                         # Gap between y-axis cells
            xgap=1,                         # Gap between x-axis cells
            hoverongaps=False,              # Disable hover on empty cells
            hoverinfo='text',               # Use custom hover text
            text=hovertext                  # Custom hover text
        )

        # Add optional footer
        if footer is not None:
          add_footer(fig, footer, font_family=self.font_family)

        # Move x-axis labels to bottom of plot
        fig.update_xaxes(side="bottom")

        # Get the base configuration
        layout_config = self._get_base_layout_config(title, subtitle)

        # Add/update specific settings for this plot
        layout_config.update({
            'xaxis_showgrid': False,           # Hide x-axis gridlines
            'yaxis_showgrid': False,           # Hide y-axis gridlines
            'yaxis_autorange': 'reversed',     # Reverse y-axis order
            'xaxis_tickangle': 90,             # Rotate x-axis labels

        })

        # Apply the combined layout configuration
        fig.update_layout(**layout_config)
 
        # Format cell annotations - remove NaN values and format numbers
        for i in range(len(fig.layout.annotations)):
            if fig.layout.annotations[i].text == 'nan':
                fig.layout.annotations[i].text = ""    # Replace NaN with empty string
            else:
                try:
                    value = float(fig.layout.annotations[i].text)
                    fig.layout.annotations[i].text = f"{value:.2f}"    # Format to 2 decimal places
                except ValueError:
                    pass

        return fig

    def plot_correlation_with_target(
        self, 
        df: pd.DataFrame,
        target_column: str,
        title: str = 'How correlated the features are with the target?',
        subtitle: str = 'Correlation coefficient of each feature',
        footer: str = None
    ) -> go.Figure:
        """
        Create a horizontal bar chart showing how each feature correlates with a target variable.

        This visualization helps identify which features have strong positive or negative 
        relationships with the target variable. Positive correlations are shown in blue,
        negative in light red. Values range from -1 (perfect negative correlation) to 
        1 (perfect positive correlation).

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataframe containing numerical columns to analyze
        target_column : str
            Name of the column to compare other features against
        title : str, optional
            Main title for the plot (default: 'How correlated the features are with the target?')
        subtitle : str, optional
            Subtitle to display below main title (default: 'Correlation coefficient of each feature')
        footer : str, optional
            Text to show at bottom of plot

        Returns
        -------
        plotly.graph_objects.Figure
            Interactive bar chart showing correlation coefficients
        """
        # Calculate correlations with target and sort them
        correlations = df.corr()[target_column].sort_values()
        # Remove target column's correlation with itself (always 1)
        correlations = correlations.drop(target_column)  

        # Assign colors based on correlation direction:
        # Light red for negative correlations, blue for positive
        colors = ['#FF9999' if c < 0 else '#2E75B6' for c in correlations]

        # Initialize empty figure
        fig = go.Figure()

        # Add horizontal bar trace
        fig.add_trace(
            go.Bar(
                y=correlations.index,        # Feature names on y-axis
                x=correlations.values,       # Correlation values on x-axis
                orientation='h',             # Make bars horizontal
                marker_color=colors,         # Color bars based on correlation
                text=[f'{x:.2f}' for x in correlations.values],  # Show correlation values
                textposition='outside',      # Place text outside of bars
            )
        )

        # Add optional footer
        if footer is not None:
          add_footer(fig, footer, font_family=self.font_family)

        # Get the base configuration
        layout_config = self._get_base_layout_config(title, subtitle)

        # Update base configuration with specific settings
        layout_config.update({
            'height': max(400, len(correlations) * 30),  # Dynamic height
            'xaxis_title': 'Correlation Coefficient',
            'xaxis_gridwidth': 1,
            'xaxis_tickformat': '.2f',
            'yaxis_title': 'Features',
            'yaxis_autorange': "reversed"
        })

        # Apply the combined layout configuration
        fig.update_layout(**layout_config)
        return fig
    
    def plot_hbar(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str = None, 
        title: str = "How distributed are the categories?",
        subtitle: str = "Horizontal bar plot of categories", 
        footer: str = None,
        add_hline: bool = False,
        top_n: int = None,
        highlight_top_n: tuple[int, str] = None,  # (n, hex_color)
        highlight_low_n: tuple[int, str] = None   # (n, hex_color)
    ) -> go.Figure:
        """
        Create a horizontal bar plot with optional highlighting and statistics.

        Shows either value counts of a single column or relationship between two columns. 
        Can highlight top/bottom values and show mean line. Bars can be limited to show 
        only top N values.

        Parameters
        ----------
        df : pandas.DataFrame
            The data to plot
        x_col : str
            Name of column to show on y-axis of plot
        y_col : str, optional
            Name of column for bar lengths. If None, shows value counts of x_col
        title : str, optional
            Main title of plot (default: "How distributed are the categories?")
        subtitle : str, optional
            Subtitle shown below main title (default: "Horizontal bar plot of categories")
        footer : str, optional
            Text to show at bottom of plot
        top_n : int, optional
            Number of bars to show. If None, shows all
        add_hline : bool, optional
            Whether to add mean line (default: False)
        highlight_top_n : tuple, optional 
            Tuple of (n, color) to highlight top n bars
        highlight_low_n : tuple, optional
            Tuple of (n, color) to highlight bottom n bars

        Returns
        -------
        plotly.graph_objects.Figure
            Interactive horizontal bar plot
        """
        # Create empty figure canvas
        fig = go.Figure()

        if y_col is None:
            # Calculate frequency of each category in x_col
            value_counts = df[x_col].value_counts().rename_axis(x_col).reset_index(name='Count')
            
            # Limit to top N categories if specified
            plot_data = value_counts.head(top_n) if top_n else value_counts
            
            # Determine bar colors based on highlighting options
            colors = (highlight_bars_colors(highlight_top_n, highlight_low_n, len(plot_data)) 
                    if highlight_top_n or highlight_low_n else self.color)

            # Create bars with custom hover text
            fig.add_trace(
                go.Bar(
                    y=plot_data[x_col],
                    x=plot_data['Count'],
                    orientation='h',
                    marker_color=colors,
                    hovertemplate=(
                        f"<b>{x_col}</b>: " + "%{y}<br>" +
                        f"Count: " + "%{x:,.0f}<br>" +
                        "<extra></extra>"
                    )
                )
            )

        else:
            # Sort data by y_col values
            plot_data = df.sort_values(y_col, ascending=False)
            if top_n:
                plot_data = plot_data.head(top_n)
            
            # Determine bar colors based on highlighting options
            colors = (highlight_bars_colors(highlight_top_n, highlight_low_n, len(plot_data))
                    if highlight_top_n or highlight_low_n else self.color)

            # Create bars with custom hover text
            fig.add_trace(
                go.Bar(
                    y=plot_data[x_col],
                    x=plot_data[y_col],
                    orientation='h',
                    marker_color=colors,
                    hovertemplate=(
                        f"<b>{x_col}</b>: " + "%{y}<br>" +
                        f"{y_col}: " + "%{x:,.2f}<br>" +
                        "<extra></extra>"
                    )
                )
            )

        # Add mean reference line if requested
        if add_hline:
            mean_value = plot_data[y_col].mean() if y_col else plot_data['Count'].mean()
            fig.add_vline(
                x=mean_value,
                line_color="grey",
                line_dash="dash",
                line_width=2,
            )

        # Add optional footer
        if footer is not None:
          add_footer(fig, footer, font_family=self.font_family)

        # Get the base configuration
        layout_config = self._get_base_layout_config(title, subtitle)

        # Update base configuration with specific settings
        layout_config.update({
            'xaxis_title': y_col if y_col else "Count", # Set x-axis title to column name or default
            'yaxis_title': x_col,   # Set y-axis title to column name
            'yaxis_autorange': "reversed"  # Show categories from top to bottom
        })

        # Apply the combined layout configuration
        fig.update_layout(**layout_config)
        return fig
    
    def plot_dot(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "How are the categories distributed?",
        subtitle: str = "Dot plot of categories",
        footer: str = None,
        add_hline_at: tuple[str, float] = None,  # (label, value)
        top_n: int = None,
        highlight_top_n: tuple[int, str] = None,  # (n, hex_color)
        highlight_low_n: tuple[int, str] = None   # (n, hex_color)
    ) -> go.Figure:
        """
        Create a dot plot showing values as dots with connecting lines to x-axis.

        This plot shows values as dots above their categories, with vertical lines 
        connecting each dot to its category on the x-axis. Can highlight highest/lowest
        values with different colors and show a reference line at a specific value.

        Parameters
        ----------
        df : pandas.DataFrame
            Data to plot
        x_col : str
            Column name for categories on x-axis
        y_col : str
            Column name for values shown as dot heights
        title : str, optional
            Main title of plot
        subtitle : str, optional
            Subtitle shown below main title
        footer : str, optional
            Text to show at bottom of plot
        add_hline_at : tuple[str, float], optional
            Reference line (label, value) to add
        top_n : int, optional
            Number of dots to show, ordered by value
        highlight_top_n : tuple[int, str], optional
            (number, color) for highlighting highest values
        highlight_low_n : tuple[int, str], optional
            (number, color) for highlighting lowest values

        Returns
        -------
        plotly.graph_objects.Figure
            Interactive dot plot figure
        """
        # Sort values in descending order and limit to top_n if specified
        plot_data = df.sort_values(y_col, ascending=False)
        if top_n:
            plot_data = plot_data.head(top_n)
        
        # Get colors for dots based on highlighting options
        colors = (highlight_bars_colors(highlight_top_n, highlight_low_n, len(plot_data))
                if highlight_top_n or highlight_low_n else self.color)

        # Create figure and add dots with hover information
        fig = go.Figure()
        fig.add_trace(
          go.Scatter(
              x=plot_data[x_col],
              y=plot_data[y_col],
              mode='markers+text',
              marker=dict(
                  color=colors,
                  size=18
              ),
              text=plot_data[y_col].round(1),
              textposition='top center',
              hovertemplate=(
                  f"<b>{x_col}</b>: " + "%{x}<br>" +
                  f"{y_col}: " + "%{y:,.2f}<br>" +
                  "<extra></extra>"
              )
          )
        )

        # Add vertical connecting lines between dots and x-axis
        for i, row in plot_data.iterrows():
          fig.add_shape(
              type='line',
              x0=row[x_col],
              x1=row[x_col],
              y0=0,
              y1=row[y_col],
              line=dict(color='lightgrey', width=2),
              layer="below",
          )

        # Add optional reference line with label
        if add_hline_at is not None:
          fig.add_hline(
              y=add_hline_at[-1],
              line=dict(color='grey', dash='dot', width=0.5),
              annotation_text=f'{add_hline_at[0]}: {add_hline_at[-1]:.1f}',
              annotation_position='top right', 
              layer="below",
          )

        # Add optional footer
        if footer is not None:
          add_footer(fig, footer, font_family=self.font_family)
          
        # Get the base configuration
        layout_config = self._get_base_layout_config(title, subtitle)

        # Update base configuration with specific settings
        layout_config.update({
            'yaxis_title': "",
            'yaxis_visible': False,  # Hide y-axis
            'xaxis_title': "",
            'xaxis_showline': True,
            'xaxis_linecolor': 'lightgrey',
            'xaxis_linewidth': 2,
            'xaxis_type': 'category',
            'margin': dict(t=100, pad=0)  # Override base margin settings
        })

        # Apply the combined layout configuration
        fig.update_layout(**layout_config)
        return fig