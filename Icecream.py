from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
import numpy as np

from About import AboutWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.temperatures = []
        self.profits = []

        self.setWindowTitle('Ice Cream Sales')
        self.resize(720, 520)

        self.load_button = QPushButton('Choose CSV File', self)
        self.load_button.clicked.connect(self.load_file)

        self.about_window = AboutWindow()
        self.about_button = QPushButton('About Me', self)
        self.about_button.clicked.connect(self.show_about_window)

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.load_button)
        layout.addWidget(self.about_button)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

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
        self.ax.clear()
        self.ax.scatter(self.temperatures, self.profits, s=1)

        if len(set(self.temperatures)) >= 2:
            m, b = np.polyfit(self.temperatures, self.profits, 1)

            x_line = [min(self.temperatures), max(self.temperatures)]
            y_line = [m * x_line[0] + b, m * x_line[1] + b]

            self.ax.plot(
                x_line, y_line,
                color='red',
                label=f'y = {m:.2f}x {b:+.2f}'
            )
            
            self.ax.legend()

        self.ax.set_title('Ice Cream Profit vs. Temperature')
        self.ax.set_xlabel('Temperature')
        self.ax.set_ylabel('Profit')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.figure.tight_layout()
        self.canvas.draw()

    def show_about_window(self):
        self.about_window.show()


if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()