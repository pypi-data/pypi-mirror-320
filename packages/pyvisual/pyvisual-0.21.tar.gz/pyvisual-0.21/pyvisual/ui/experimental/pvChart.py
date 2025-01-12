from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import numpy as np


class PvChart:
    def __init__(self, container, width=600, height=400, title="Chart", chart_type="line", data=None, **kwargs):
        """
        Chart widget for PyVisual.

        Args:
            container: The parent container to which the chart will be added.
            width (int): Width of the chart in pixels.
            height (int): Height of the chart in pixels.
            title (str): Title of the chart.
            chart_type (str): Type of chart ('line', 'bar', 'scatter', 'pie', 'histogram', 'area', 'heatmap', 'bubble').
            data (dict): Data required for the chart.
            kwargs: Additional keyword arguments for customization (colors, legend, etc.).
        """
        self.container = container
        self.width = width
        self.height = height
        self.title = title
        self.chart_type = chart_type
        self.data = data or {}
        self.kwargs = kwargs

        # Initialize Matplotlib figure and axis
        self.fig, self.ax = plt.subplots(figsize=(width / 100, height / 100))
        self.ax.set_title(self.title)
        self.ax.grid(True)

        # Add the Matplotlib figure to the PyVisual container
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        if container:
            container.add_widget(self.canvas_widget)

        # Render the chart initially
        self._render_chart()

    def _render_chart(self):
        """
        Automatically render the chart based on the chart type and provided data.
        """
        self.ax.clear()  # Clear the previous chart

        if self.chart_type == "line":
            self._plot_line(**self.data)
        elif self.chart_type == "bar":
            self._plot_bar(**self.data)
        elif self.chart_type == "scatter":
            self._plot_scatter(**self.data)
        elif self.chart_type == "pie":
            self._plot_pie(**self.data)
        elif self.chart_type == "histogram":
            self._plot_histogram(**self.data)
        elif self.chart_type == "area":
            self._plot_area(**self.data)
        elif self.chart_type == "heatmap":
            self._plot_heatmap(**self.data)
        elif self.chart_type == "bubble":
            self._plot_bubble(**self.data)
        else:
            raise ValueError(f"Unsupported chart type: {self.chart_type}")

        # Update the chart title and redraw the canvas
        self.ax.set_title(self.title)
        self.canvas_widget.draw()

    # Private plotting methods
    def _plot_line(self, x_data, y_data, line_color="blue", label=None):
        self.ax.plot(x_data, y_data, color=line_color, label=label)
        if label:
            self.ax.legend()

    def _plot_bar(self, x_data, y_data, bar_color="orange", label=None):
        self.ax.bar(x_data, y_data, color=bar_color, label=label)
        if label:
            self.ax.legend()

    def _plot_scatter(self, x_data, y_data, color="red", label=None):
        self.ax.scatter(x_data, y_data, color=color, label=label)
        if label:
            self.ax.legend()

    def _plot_pie(self, labels, values, colors=None):
        self.ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)

    def _plot_histogram(self, data, bins=10, color='blue'):
        self.ax.hist(data, bins=bins, color=color, edgecolor='black')
        self.ax.set_xlabel("Bins")
        self.ax.set_ylabel("Frequency")

    def _plot_area(self, x_data, y_data, color='skyblue', alpha=0.5):
        self.ax.fill_between(x_data, y_data, color=color, alpha=alpha)
        self.ax.plot(x_data, y_data, color='blue')
        self.ax.set_xlabel("X-Axis")
        self.ax.set_ylabel("Y-Axis")

    def _plot_heatmap(self, data, cmap='viridis', colorbar=True):
        heatmap = self.ax.imshow(data, cmap=cmap, aspect='auto')
        if colorbar:
            self.fig.colorbar(heatmap, ax=self.ax)

    def _plot_bubble(self, x_data, y_data, sizes, color='blue', alpha=0.5):
        self.ax.scatter(x_data, y_data, s=sizes, c=color, alpha=alpha)
        self.ax.set_xlabel("X-Axis")
        self.ax.set_ylabel("Y-Axis")

    # Setter and getter methods
    def set_title(self, title):
        """Set the chart title."""
        self.title = title
        self._render_chart()

    def get_title(self):
        """Get the chart title."""
        return self.title

    def set_data(self, data):
        """Set new data for the chart."""
        self.data = data
        self._render_chart()

    def get_data(self):
        """Get the current data."""
        return self.data

    def set_chart_type(self, chart_type):
        """Change the chart type."""
        self.chart_type = chart_type
        self._render_chart()

    def get_chart_type(self):
        """Get the current chart type."""
        return self.chart_type

    def set_options(self, **kwargs):
        """Set additional customization options."""
        self.kwargs.update(kwargs)
        self._render_chart()

    def get_options(self):
        """Get the current customization options."""
        return self.kwargs

    def clear(self):
        """Clear the current chart."""
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_title(self.title)
        self.canvas_widget.draw()


if __name__ == "__main__":
    import pyvisual as pv
    import random
    import numpy as np

    # Create a PyVisual window
    window = pv.PvWindow()

    # Line Chart
    line_chart = PvChart(
        container=window,
        width=800,
        height=600,
        title="Line Chart",
        chart_type="line",
        data={"x_data": [1, 2, 3, 4, 5], "y_data": [10, 15, 13, 20, 18], "line_color": "blue", "label": "Line Data"}
    )

    # Update line chart data
    line_chart.set_data({"x_data": [1, 2, 3, 4, 5], "y_data": [12, 18, 10, 22, 25], "line_color": "green", "label": "Updated Line"})

    # # Pie Chart
    # pie_chart = PvChart(
    #     container=window,
    #     width=800,
    #     height=600,
    #     title="Pie Chart",
    #     chart_type="pie",
    #     data={"labels": ["Apple", "Banana", "Cherry"], "values": [30, 40, 30], "colors": ["red", "yellow", "purple"]}
    # )
    # #
    # # Heatmap
    # heatmap_chart = PvChart(
    #     container=window,
    #     width=800,
    #     height=600,
    #     title="Heatmap",
    #     chart_type="heatmap",
    #     data={"data": np.random.rand(10, 10), "cmap": "plasma"}
    # )

    # Show the PyVisual window
    window.show()
