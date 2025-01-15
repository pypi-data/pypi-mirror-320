import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, Union, Any, List, Tuple, Dict
import pandas as pd
from scipy import stats


class QuicklyPlot:
    """
    Main plotting class that implements the builder pattern for creating matplotlib plots.
    
    The QuicklyPlot class provides a fluent interface for creating various types of plots
    using matplotlib and seaborn. It supports multiple plot types, styling options,
    and advanced features like dual axes and subplots.
    
    Attributes:
        _data (pd.DataFrame): The input DataFrame containing the data to plot
        _x (str): Column name for x-axis
        _y (Union[str, List[str]]): Column name(s) for y-axis
        _x_conf (Optional[float]): Confidence interval level for x-axis
        _plot_type (str): Type of plot to create
        _figure (Optional[plt.Figure]): Matplotlib figure object
        _ax (Optional[plt.Axes]): Matplotlib axes object
        _ax2 (Optional[plt.Axes]): Secondary y-axis for dual axis plots
        _color (Optional[str]): Color for the plot
        _style (str): Style name from seaborn
        _title (str): Plot title
        _legend (bool): Whether to show legend
        _grid (bool): Whether to show grid
        _figsize (Tuple[int, int]): Figure size in inches
        _alpha (float): Transparency level
        _bins (Optional[int]): Number of bins for histograms
        _two_axis (bool): Whether to use dual y-axes for two variables
        _xlim (Optional[Tuple[float, float]]): X-axis limits
        _ylim (Optional[Tuple[float, float]]): Y-axis limits
        _rotation (Optional[float]): X-axis label rotation
        _horizontal (bool): Whether to plot bars horizontally
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize a new QuicklyPlot instance.
        
        Args:
            data: pandas DataFrame containing the data to plot
        """
        self._data = data
        self._x: str = ""
        self._y: Union[str, List[str]] = ""
        self._x_conf: Optional[float] = None
        self._plot_type: str = "line"
        self._figure: Optional[plt.Figure] = None
        self._ax: Optional[plt.Axes] = None
        self._ax2: Optional[plt.Axes] = None
        self._color: Optional[Union[str, List[str]]] = None
        self._color_is_data: bool = False
        self._style: str = "whitegrid"
        self._title: str = ""
        self._legend: bool = True
        self._legend_position: str = "best"
        self._grid: bool = True
        self._figsize: Tuple[int, int] = (10, 6)
        self._alpha: float = 1.0
        self._bins: Optional[int] = None
        self._two_axis: bool = True
        self._xlim: Optional[Tuple[float, float]] = None
        self._ylim: Optional[Tuple[float, float]] = None
        self._rotation: Optional[float] = None
        self._horizontal: bool = False
        self._log_scale: Dict[str, bool] = {"x": False, "y": False}
        self._colormap: str = "viridis"  # Default colormap for continuous colors
        self._xlabel: Optional[str] = None 
        self._ylabel: Optional[str] = None 

        
    def x(self, column: Union[str, None] = None, conf: Optional[float] = None) -> 'QuicklyPlot':
        """
        Set the x-axis column and optionally confidence interval.
        
        Args:
            column: Name of the column to use for x-axis. If None, use the DataFrame index.
            conf: Confidence interval level (0 to 1), e.g., 0.95 for 95% confidence
        
        Returns:
            self for method chaining
        
        Raises:
            ValueError: If the column name doesn't exist in the DataFrame (when column is specified)
        """
        if column is None:
            # Use index as x-axis
            self._x = self._data.index.name if self._data.index.name else "index"
        else:
            if column not in self._data.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {list(self._data.columns)}")
            self._x = column

        self._x_conf = conf
        return self

        
    def y(self, column: Union[str, List[str], None] = None) -> 'QuicklyPlot':
        """
        Set the y-axis column(s). If None, use the DataFrame index as the y-axis.
        
        Args:
            column: Name of the column(s) to use for y-axis. Can be a single column
                    name, a list of column names for multiple lines, or None to use the index.
        
        Returns:
            self for method chaining
        
        Raises:
            ValueError: If any column name doesn't exist in the DataFrame (when column is specified)
        """
        if column is None:
            # Use index as y-axis
            self._y = self._data.index.name if self._data.index.name else "index"
        else:
            columns = [column] if isinstance(column, str) else column
            for col in columns:
                if col not in self._data.columns:
                    raise ValueError(f"Column '{col}' not found in DataFrame. Available columns: {list(self._data.columns)}")
            self._y = column
        return self


    def xlabel(self, label: str) -> 'QuicklyPlot':
        """
        Set the x-axis label.
        
        Args:
            label: Label text for x-axis
            
        Returns:
            self for method chaining
        """
        self._xlabel = label
        return self

    def ylabel(self, label: str) -> 'QuicklyPlot':
        """
        Set the y-axis label.
        
        Args:
            label: Label text for y-axis
            
        Returns:
            self for method chaining
        """
        self._ylabel = label
        return self


    def two_axis(self, enabled: bool = True) -> 'QuicklyPlot':
        """Control whether to use two axes for two y variables."""
        self._two_axis = enabled
        return self

    def color(self, color: Union[str, List[str]]) -> 'QuicklyPlot':
        """
        Set the color for the plot. Accepts either:
        - A color name/hex code (e.g., "blue", "#FF0000")
        - A column name for color mapping (e.g., "department" for categorical, "income" for continuous)
        - A list of colors for manual color mapping
        
        Args:
            color: Color specification (color name, column name, or list of colors)
            
        Returns:
            self for method chaining
        """
        self._color = color
        self._color_is_data = isinstance(color, str) and color in self._data.columns
        return self

    def style(self, style: str) -> 'QuicklyPlot':
        """
        Set the plot style using seaborn styles.
        
        Args:
            style: Name of the style ('whitegrid', 'darkgrid', 'white', 'dark', 'ticks')
            
        Returns:
            self for method chaining
        """
        self._style = style
        sns.set_style(style)
        return self

    def title(self, title: str) -> 'QuicklyPlot':
        """
        Set the plot title.
        
        Args:
            title: Title text
            
        Returns:
            self for method chaining
        """
        self._title = title
        return self

    def size(self, width: int, height: int) -> 'QuicklyPlot':
        """
        Set the figure size (alias for figsize).
        
        Args:
            width: Width in inches
            height: Height in inches
            
        Returns:
            self for method chaining
        """
        self._figsize = (width, height)
        return self

    def subplot(self, ax: plt.Axes) -> 'QuicklyPlot':
        """
        Use an existing subplot axes for plotting.
        
        Args:
            ax: Matplotlib axes object to plot on
            
        Returns:
            self for method chaining
        """
        self._ax = ax
        self._figure = ax.figure
        return self

    def alpha(self, alpha: float) -> 'QuicklyPlot':
        """
        Set the transparency level.
        
        Args:
            alpha: Transparency level (0 to 1)
            
        Returns:
            self for method chaining
        """
        self._alpha = alpha
        return self

    def bins(self, bins: int) -> 'QuicklyPlot':
        """
        Set the number of bins for histogram plots.
        
        Args:
            bins: Number of bins
            
        Returns:
            self for method chaining
        """
        self._bins = bins
        return self

    def xlim(self, min_val: float, max_val: float) -> 'QuicklyPlot':
        """
        Set the x-axis limits.
        
        Args:
            min_val: Minimum x value
            max_val: Maximum x value
            
        Returns:
            self for method chaining
        """
        self._xlim = (min_val, max_val)
        return self

    def ylim(self, min_val: float, max_val: float) -> 'QuicklyPlot':
        """
        Set the y-axis limits.
        
        Args:
            min_val: Minimum y value
            max_val: Maximum y value
            
        Returns:
            self for method chaining
        """
        self._ylim = (min_val, max_val)
        return self

    def rotate_labels(self, degrees: float) -> 'QuicklyPlot':
        """
        Rotate x-axis labels.
        
        Args:
            degrees: Rotation angle in degrees
            
        Returns:
            self for method chaining
        """
        self._rotation = degrees
        return self

    def horizontal(self, enabled: bool = True) -> 'QuicklyPlot':
        """
        Enable horizontal orientation for bar plots.
        
        Args:
            enabled: Whether to plot bars horizontally
            
        Returns:
            self for method chaining
        """
        self._horizontal = enabled
        return self

    def log_x(self, enabled: bool = True) -> 'QuicklyPlot':
        """
        Enable logarithmic scale for x-axis.
        
        Args:
            enabled: Whether to use log scale
            
        Returns:
            self for method chaining
        """
        self._log_scale["x"] = enabled
        return self

    def log_y(self, enabled: bool = True) -> 'QuicklyPlot':
        """
        Enable logarithmic scale for y-axis.
        
        Args:
            enabled: Whether to use log scale
            
        Returns:
            self for method chaining
        """
        self._log_scale["y"] = enabled
        return self

    def legend(self, show: bool = True, position: str = "best") -> 'QuicklyPlot':
        """
        Configure the legend visibility and position.
        
        Args:
            show: Whether to show the legend (True/False)
            position: Legend position ('best', 'upper right', 'upper left', 
                    'lower left', 'lower right', 'right', 'center left',
                    'center right', 'lower center', 'upper center', 'center')
            
        Returns:
            self for method chaining
        """
        self._legend = show
        self._legend_position = position
        return self

    def colormap(self, cmap: str) -> 'QuicklyPlot':
        """
        Set the colormap for continuous color mapping.
        
        Args:
            cmap: Name of the matplotlib colormap
            
        Returns:
            self for method chaining
        """
        self._colormap = cmap
        return self
    
    @property
    def nogrid(self) -> 'QuicklyPlot':
        """Disable grid lines."""
        self._grid = False
        return self
    
    @property
    def noxlabel(self) -> 'QuicklyPlot':
        """Hide x-axis label."""
        self._xlabel = ""
        return self

    @property
    def noylabel(self) -> 'QuicklyPlot':
        """Hide y-axis label."""
        self._ylabel = ""
        return self

    @property
    def line(self) -> 'QuicklyPlot':
        """Set plot type to line."""
        self._plot_type = "line"
        return self
        
    @property
    def scatter(self) -> 'QuicklyPlot':
        """Set plot type to scatter."""
        self._plot_type = "scatter"
        return self
    
    @property
    def scatter_line(self) -> 'QuicklyPlot':
        """Set plot type to scatter with line."""
        self._plot_type = "scatter-line"
        return self
        
    @property
    def bar(self) -> 'QuicklyPlot':
        """Set plot type to bar."""
        self._plot_type = "bar"
        return self

    @property
    def hist(self) -> 'QuicklyPlot':
        """Set plot type to histogram."""
        self._plot_type = "histogram"
        self._x = "histogram_no_x_needed"  # Dummy x value to pass validation
        return self

    @property
    def box(self) -> 'QuicklyPlot':
        """Set plot type to box plot."""
        self._plot_type = "box"
        return self

    @property
    def violin(self) -> 'QuicklyPlot':
        """Set plot type to violin plot."""
        self._plot_type = "violin"
        return self

    def _create_figure(self):
        """Create a new figure if none exists."""
        if self._figure is None or self._ax is None:
            self._figure, self._ax = plt.subplots(figsize=self._figsize)

    def _plot_with_confidence(self):
        """Add confidence intervals if specified."""
        if self._x_conf is not None:
            # Calculate confidence intervals
            grouped = self._data.groupby(self._x)[self._y].agg(['mean', 'std', 'count'])
            confidence_interval = (
                grouped['std'] / np.sqrt(grouped['count']) 
                * stats.t.ppf((1 + self._x_conf) / 2, grouped['count'] - 1)
            )
            
            self._ax.fill_between(
                grouped.index,
                grouped['mean'] - confidence_interval,
                grouped['mean'] + confidence_interval,
                alpha=0.2,
                color=self._color
            )

    def _get_plot_colors(self, data_size: int) -> Union[str, List[str], None]:
        """Helper method to process color specifications."""
        if not self._color:
            return None
        
        if self._color_is_data:
            if pd.api.types.is_numeric_dtype(self._data[self._color]):
                # Continuous color mapping
                norm = plt.Normalize(self._data[self._color].min(), 
                                self._data[self._color].max())
                cmap = plt.get_cmap(self._colormap)
                return [cmap(norm(value)) for value in self._data[self._color]]
            else:
                # Categorical color mapping
                categories = self._data[self._color].unique()
                cmap = plt.get_cmap('tab10')
                color_dict = {cat: cmap(i/len(categories)) 
                            for i, cat in enumerate(categories)}
                plot_colors = [color_dict[cat] for cat in self._data[self._color]]
                # Add to legend if needed
                if self._legend:
                    handles = [plt.Line2D([0], [0], color=color_dict[cat], 
                            label=cat) for cat in categories]
                    self._ax.legend(handles=handles, loc=self._legend_position)
                return plot_colors
        
        return self._color

    def _plot_bars(self, y_col: str, plot_kwargs: dict):
        """Helper method for plotting bars with horizontal option."""
        if self._horizontal:
            self._ax.barh(self._data[self._x], self._data[y_col], label=y_col, **plot_kwargs)
        else:
            self._ax.bar(self._data[self._x], self._data[y_col], label=y_col, **plot_kwargs)

    def _plot_dual_axis(self, y_columns: List[str], plot_kwargs: dict):
        """Handle plotting with dual y-axes."""
        # Handle color list for dual axis
        colors = plot_kwargs.get('color', [None, None])
        if isinstance(colors, list):
            color1, color2 = colors
        else:
            color1 = colors
            color2 = plt.cm.get_cmap('tab10')(1)

        # Plot first y on primary axis
        kwargs1 = {**plot_kwargs, 'color': color1}
        if isinstance(color1, list):
            del kwargs1['color']  # Remove if it's a list of colors
        line1 = self._ax.plot(self._data[self._x], self._data[y_columns[0]], 
                            label=y_columns[0], **kwargs1)
        
        # Create secondary y-axis and plot second y
        self._ax2 = self._ax.twinx()
        kwargs2 = {**plot_kwargs, 'color': color2}
        line2 = self._ax2.plot(self._data[self._x], self._data[y_columns[1]], 
                            label=y_columns[1], **kwargs2)
        
        # Set labels
        self._ax.set_ylabel(y_columns[0])
        self._ax2.set_ylabel(y_columns[1])
        
        # Add legend for both lines
        if self._legend:
            lines = line1 + line2
            labels = [line.get_label() for line in lines]
            self._ax.legend(lines, labels, loc=self._legend_position)

    
    def _apply_common_styling(self):
        """Apply common styling elements to the plot."""
        if self._title:
            self._ax.set_title(self._title)
        
        if self._plot_type != "histogram":
            # Use custom xlabel if provided, otherwise use column name
            x_label = self._xlabel if self._xlabel is not None else self._x
            self._ax.set_xlabel(x_label)
            
            # Use custom ylabel if provided, otherwise use column name(s)
            if not isinstance(self._y, list) or len(self._y) <= 1 or not self._two_axis:
                y_label = self._ylabel if self._ylabel is not None else (
                    self._y if isinstance(self._y, str) else ', '.join(self._y)
                )
                self._ax.set_ylabel(y_label)
        
        # Explicitly handle grid visibility
        if self._grid:
            self._ax.grid(True, linestyle='--', alpha=0.7)
        else:
            self._ax.grid(False)  # Explicitly turn off grid
            # Remove background grid lines if they exist
            self._ax.set_axisbelow(False)
            
        if self._legend and isinstance(self._y, list) and (len(self._y) <= 1 or not self._two_axis):
            self._ax.legend(loc=self._legend_position)

        # Apply axis limits if set
        if self._xlim:
            self._ax.set_xlim(self._xlim)
        if self._ylim:
            self._ax.set_ylim(self._ylim)

        # Apply label rotation if set
        if self._rotation is not None:
            plt.xticks(rotation=self._rotation)

        # Apply log scale if enabled
        if self._log_scale["x"]:
            self._ax.set_xscale('log')
        if self._log_scale["y"]:
            self._ax.set_yscale('log')

    def plt(self, ignore_return: bool = False) -> plt.Figure:
        """Create and return the plot."""
        
        # Automatically set x and y if they are not specified
        if not self._x:
            self._x = self._data.index.name if self._data.index.name else "index"
        if not self._y:
            self._y = self._data.columns[0]  
        
        # Ensure y is set correctly if it's a single column or the index
        if isinstance(self._y, str):
            if self._y == "index":
                if "index" in self._data.columns:
                    print("Warning: using index column, not the index itself!")
                else:
                    self._y = self._data.index
            elif self._y not in self._data.columns:
                raise ValueError(f"Column '{self._y}' not found in DataFrame. Available columns: {list(self._data.columns)}")
        
        # Create figure if necessary
        if self._ax is None:
            self._create_figure()
        
        plot_kwargs = {'alpha': self._alpha}
        colors = self._get_plot_colors(len(self._data))
        
        # Special handling for categorical color mapping in line plots
        if self._color_is_data and not pd.api.types.is_numeric_dtype(self._data[self._color]):
            categories = self._data[self._color].unique()
            cmap = plt.get_cmap('tab10')
            color_dict = {cat: cmap(i/len(categories)) for i, cat in enumerate(categories)}
            
            y_columns = [self._y] if isinstance(self._y, str) else self._y
            for y_col in y_columns:
                for i, cat in enumerate(categories):
                    mask = self._data[self._color] == cat
                    self._ax.plot(self._data[self._x][mask], self._data[y_col][mask], 
                                label=cat, color=color_dict[cat], alpha=self._alpha)
            
            if self._legend:
                self._ax.legend(loc=self._legend_position)
                
        else:
            # Regular plotting logic
            if colors is not None:
                plot_kwargs['color'] = colors

            # Add colorbar if using continuous color mapping
            if self._color_is_data and pd.api.types.is_numeric_dtype(self._data[self._color]):
                sm = plt.cm.ScalarMappable(cmap=self._colormap, 
                    norm=plt.Normalize(self._data[self._color].min(), 
                                    self._data[self._color].max()))
                plt.colorbar(sm, ax=self._ax, label=self._color)

            y_columns = [self._y] if isinstance(self._y, str) else self._y
            
            # Get x values (either from index or column)
            x_values = self._data.index if self._x in ["index", self._data.index.name] else self._data[self._x]
            
            if len(y_columns) == 2 and self._plot_type == "line" and self._two_axis:
                self._plot_dual_axis(y_columns, plot_kwargs)
            else:
                for i, y_col in enumerate(y_columns):
                    current_kwargs = plot_kwargs.copy()
                    if isinstance(current_kwargs.get('color'), list):
                        if i < len(current_kwargs['color']):
                            current_kwargs['color'] = current_kwargs['color'][i]
                        else:
                            del current_kwargs['color']
                            
                    if self._plot_type == "line":
                        self._ax.plot(x_values, self._data[y_col], 
                                    label=y_col, **current_kwargs)
                    elif self._plot_type == "scatter":
                        self._ax.scatter(x_values, self._data[y_col], 
                                    label=y_col, **current_kwargs)
                    elif self._plot_type == "scatter-line":
                        self._ax.plot(x_values, self._data[y_col], 
                                    label=y_col, **current_kwargs)
                        self._ax.scatter(x_values, self._data[y_col], 
                                    label=y_col, **current_kwargs)
                    elif self._plot_type == "bar":
                        self._plot_bars(y_col, current_kwargs)
                    elif self._plot_type == "histogram":
                        if isinstance(colors, str):
                            current_kwargs['color'] = plt.cm.get_cmap('tab10')(i)
                        self._ax.hist(self._data[y_col], bins=self._bins or 'auto', 
                                    label=y_col, **current_kwargs)
                    elif self._plot_type == "box":
                        box_kwargs = {k: v for k, v in current_kwargs.items() if k != 'alpha'}
                        sns.boxplot(x=self._x, y=y_col, data=self._data, 
                                ax=self._ax, **box_kwargs)
                    elif self._plot_type == "violin":
                        sns.violinplot(x=self._x, y=y_col, data=self._data, 
                                    ax=self._ax, **current_kwargs)
        
        if self._x_conf is not None and self._plot_type == "line":
            self._plot_with_confidence()
            
        self._apply_common_styling()
        
        if ignore_return:
            return None

        return self._figure


class Quickly:
    """
    Static factory class for creating QuicklyPlot instances.
    
    This class provides a convenient entry point for creating plots using
    the QuicklyPlot builder pattern.
    
    Examples:
        >>> df = pd.DataFrame({'x': range(10), 'y': range(10)})
        >>> # Simple line plot
        >>> Quickly.using(df).x('x').y('y').line.plt()
        >>> 
        >>> # Multiple y-axes plot
        >>> Quickly.using(df).x('date').y(['price', 'volume']).line.plt()
        >>>
        >>> # Subplot example
        >>> fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        >>> Quickly.using(df).subplot(ax1).x('category').y('value1').bar.plt()
        >>> Quickly.using(df).subplot(ax2).x('category').y('value2').bar.plt()
        >>>
        >>> # Color mapping examples
        >>> Quickly.using(df).x('date').y('value').color('department').scatter.plt()
        >>> Quickly.using(df).x('date').y('value').color('score').colormap('viridis').scatter.plt()
    """
    
    @staticmethod
    def using(data: pd.DataFrame) -> QuicklyPlot:
        """
        Create a new QuicklyPlot instance with the given data.
        
        Args:
            data: pandas DataFrame containing the data to plot
            
        Returns:
            QuicklyPlot instance ready for configuration
        """
        return QuicklyPlot(data)