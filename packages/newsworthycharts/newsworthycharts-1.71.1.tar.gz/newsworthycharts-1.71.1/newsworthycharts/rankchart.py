"""
A chart showing ranking over time (like ”most popular baby names”)
"""
from .serialchart import SerialChart


class BumpChart(SerialChart):
    """Plot a rank chart

        Data should be a list of iterables of (rank, date string) tuples, eg:
    `[ [("2010-01-01", 2), ("2011-01-01", 3)] ]`, combined with a list of
    labels in the same order
    """

    def __init__(self, *args, **kwargs):
        super(BumpChart, self).__init__(*args, **kwargs)

        if self.line_width is None:
            self.line_width = 0.9
        self.label_placement = 'line'
        self.type = "line"
        self.decimals = 0
        self.revert_value_axis = True
        self.ymin = 1
        self.allow_broken_y_axis = False
        self.grid = False
        self.accentuate_baseline = False

        self.line_marker = "o-"
        self.line_marker_size = 5

    def _get_line_colors(self, i, *args):
        if not self.data:
            # Don't waste time
            return None
        if self.highlight and self.highlight in self.labels and i == self.labels.index(self.highlight):
            return self._nwc_style["strong_color"]
        elif self.colors and i < len(self.colors):
            return self.colors[i]
        return self._nwc_style["neutral_color"]
