from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QFrame
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
import numpy as np

from About import AboutWindow


def load_stylesheet(app):
    qss_path = Path(__file__).with_name('ice_cream.qss')
    stylesheet = qss_path.read_text(encoding='utf-8')
    app.setStyleSheet(stylesheet)

    start = stylesheet.find('/* CHART_COLORS')
    end = stylesheet.find('*/', start)
    if start >= 0 and end >= 0:
        for line in stylesheet[start:end].splitlines():
            if ':' in line and not line.strip().startswith('/*'):
                name, value = line.split(':', 1)
                app.setProperty(name.strip(), value.strip())


def chart_color(name):
    app = QApplication.instance()
    if app is None:
        return None
    return app.property(name)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.temperatures = []
        self.profits = []

        self.setWindowTitle('Ice Cream Sales')
        self.setMinimumSize(720, 520)
        self.setObjectName('mainWindow')

        self.load_button = QPushButton('Choose CSV File', self)
        self.load_button.setObjectName('primaryButton')
        self.load_button.clicked.connect(self.load_file)

        self.about_window = AboutWindow()
        self.about_button = QPushButton('About Me', self)
        self.about_button.setObjectName('aboutButton')
        self.about_button.clicked.connect(self.show_about_window)

        title = QLabel('ICE CREAM SALES', self)
        title.setObjectName('appTitle')
        subtitle = QLabel('TEMPERATURE & PROFIT ANALYSIS', self)
        subtitle.setObjectName('appSubtitle')

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setObjectName('chartToolbar')

        heading = QVBoxLayout()
        heading.setSpacing(2)
        heading.addWidget(title)
        heading.addWidget(subtitle)

        header = QHBoxLayout()
        header.setSpacing(10)
        header.addLayout(heading)
        header.addStretch()
        header.addWidget(self.load_button)
        header.addWidget(self.about_button)

        chart_card = QFrame(self)
        chart_card.setObjectName('chartCard')
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(10, 8, 10, 10)
        chart_layout.setSpacing(6)
        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.canvas, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(14)
        layout.addLayout(header)
        layout.addWidget(chart_card, 1)

        self.update_graph()

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select Ice Cream CSV', '', 'CSV files (*.csv)')

        if filename == '':
            return

        self.temperatures = []
        self.profits = []

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                parts = line.strip().split(',')
                self.temperatures.append(float(parts[0]))
                self.profits.append(float(parts[1]))

        self.update_graph()

    def update_graph(self):
        self.figure.patch.set_facecolor(chart_color('chart-background'))
        self.ax.clear()
        self.ax.set_facecolor(chart_color('chart-plot'))
        self.ax.tick_params(colors=chart_color('chart-tick'))
        self.ax.grid(
            axis='both', linestyle='--', linewidth=0.5,
            color=chart_color('chart-grid')
        )
        self.ax.set_axisbelow(True)
        for spine in self.ax.spines.values():
            spine.set_color(chart_color('chart-grid'))
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.scatter(
            self.temperatures, self.profits, s=1,
            color=chart_color('chart-scatter')
        )

        if len(set(self.temperatures)) >= 2:
            m, b = np.polyfit(self.temperatures, self.profits, 1)

            x_line = [min(self.temperatures), max(self.temperatures)]
            y_line = [m * x_line[0] + b, m * x_line[1] + b]

            self.ax.plot(
                x_line, y_line,
                color=chart_color('chart-trendline'),
                label=f'y = {m:.2f}x {b:+.2f}'
            )

            legend = self.ax.legend()
            legend.get_frame().set_facecolor(
                chart_color('chart-legend-background')
            )
            legend.get_frame().set_edgecolor(
                chart_color('chart-legend-border')
            )
            for text in legend.get_texts():
                text.set_color(chart_color('chart-legend-text'))

        self.ax.set_title('Ice Cream Profit vs. Temperature')
        self.ax.set_xlabel('Temperature')
        self.ax.set_ylabel('Profit')
        self.ax.title.set_color(chart_color('chart-title'))
        self.ax.xaxis.label.set_color(chart_color('chart-axis-label'))
        self.ax.yaxis.label.set_color(chart_color('chart-axis-label'))

        self.figure.tight_layout()
        self.canvas.draw()

    def show_about_window(self):
        self.about_window.show()


if __name__ == '__main__':
    app = QApplication([])
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    app.exec()