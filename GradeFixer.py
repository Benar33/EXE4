from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QSpinBox,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QVBoxLayout, QHBoxLayout, QFrame
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import os
from About import AboutWindow


def load_stylesheet(app):
    qss_path = os.path.join(os.path.dirname(__file__), 'modern.qss')
    with open(qss_path, 'r', encoding='utf-8') as qss_file:
        stylesheet = qss_file.read()
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

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ''

        self.about_window = AboutWindow()
        self.setWindowTitle('Grade Corrector')
        self.setMinimumSize(720, 820)
        self.setObjectName('mainWindow')

        title = QLabel('GRADE CONTROL', self)
        title.setObjectName('appTitle')
        subtitle = QLabel('CSV GRADING SYSTEM', self)
        subtitle.setObjectName('appSubtitle')

        self.load_button = QPushButton('Choose CSV File', self)
        self.load_button.setObjectName('primaryButton')
        self.load_button.clicked.connect(self.load_file)

        self.file_label = QLabel('No file selected', self)
        self.file_label.setObjectName('fileLabel')
        self.file_label.setMinimumHeight(38)

        self.table = QTableWidget(50, 3, self)
        self.table.setMinimumHeight(300)
        table_card = QFrame(self)
        table_card.setObjectName('card')
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(10, 10, 10, 10)
        table_card_layout.addWidget(self.table)
        self.table.setHorizontalHeaderLabels(
            ['ID', 'Original Grades', 'Corrected Grades']
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self.bonus_label = QLabel('Bonus points:', self)
        self.bonus_label.setObjectName('bonusLabel')

        self.bonus_input = QSpinBox(self)
        self.bonus_input.setRange(0, 100)
        self.bonus_input.setMinimumWidth(140)
        self.bonus_input.editingFinished.connect(self.correct_grades)
        self.bonus_input.setEnabled(False)

        self.about_button = QPushButton('About Me', self)
        self.about_button.clicked.connect(self.show_about_window)

        self.update_button = QPushButton('Update File', self)
        self.update_button.setObjectName('primaryButton')
        self.update_button.clicked.connect(self.update_file)
        self.update_button.setEnabled(False)

        self.message = QLabel('', self)
        self.message.setObjectName('messageLabel')
        self.message.setMinimumHeight(38)

        self.figure = Figure()
        self.figure.patch.set_facecolor(chart_color('chart-background'))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(chart_color('chart-plot'))
        self.ax.tick_params(colors=chart_color('chart-tick'))
        self.ax.title.set_color(chart_color('chart-title'))
        self.ax.xaxis.label.set_color(chart_color('chart-axis-label'))
        self.ax.yaxis.label.set_color(chart_color('chart-axis-label'))
        for spine in self.ax.spines.values():
            spine.set_color(chart_color('chart-grid'))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setParent(self)
        chart_card = QFrame(self)
        chart_card.setObjectName('card')
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        chart_layout.addWidget(self.canvas)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(14)

        heading = QVBoxLayout()
        heading.setSpacing(2)
        heading.addWidget(title)
        heading.addWidget(subtitle)

        file_row = QHBoxLayout()
        file_row.setSpacing(12)
        file_row.addLayout(heading)
        file_row.addStretch()
        file_row.addWidget(self.load_button)
        file_row.addWidget(self.file_label, 1)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        action_row.addWidget(self.bonus_label)
        action_row.addWidget(self.bonus_input)
        action_row.addStretch()
        action_row.addWidget(self.about_button)
        action_row.addWidget(self.update_button)

        root.addLayout(file_row)
        root.addWidget(table_card)
        root.addLayout(action_row)
        root.addWidget(self.message)
        root.addWidget(chart_card, 1)
        self.update_histogram(False)

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Select a grades file', '', 'CSV files (*.csv)'
        )

        if filename == '':
            return

        self.selected_file = filename
        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []

        with open(self.selected_file, 'r') as f:
            next(f)
            for line in f:
                student_id, grade = line.strip().split(',')
                grade = int(grade)
                self.student_ids.append(student_id)
                self.original_grades.append(grade)
                self.corrected_grades.append(grade)

        self.update_table()
        self.update_histogram(False)
        self.file_label.setText(filename.rsplit('/', 1)[-1])
        self.bonus_input.setValue(0)
        self.bonus_input.setEnabled(True)
        self.update_button.setEnabled(True)
        self.message.setText('Grades loaded. Enter bonus points to preview.')

    def update_table(self):
        self.table.clearContents()

        for i in range(len(self.student_ids)):
            self.table.setItem(i, 0, QTableWidgetItem(self.student_ids[i]))
            self.table.setItem(i, 1, QTableWidgetItem(str(self.original_grades[i])))
            self.table.setItem(i, 2, QTableWidgetItem(str(self.corrected_grades[i])))

    def correct_grades(self):
        bonus = self.bonus_input.value()

        for i in range(len(self.original_grades)):
            grade = self.original_grades[i] + bonus
            if grade > 100:
                grade = 100
            self.corrected_grades[i] = grade

        self.update_table()
        self.update_histogram(True)
        self.message.setText('Preview updated. Click Update File to save.')

    def update_histogram(self, show_corrected):
        ax = self.ax
        ax.clear()

        ax.set_title('Grade Distribution')
        ax.set_xlabel('Grade Range')
        ax.set_ylabel('Number of Students')
        ax.set_xlim(0, 100)
        ax.set_axisbelow(True)
        ax.set_facecolor(chart_color('chart-plot'))
        ax.tick_params(colors=chart_color('chart-tick'))
        ax.title.set_color(chart_color('chart-title'))
        ax.xaxis.label.set_color(chart_color('chart-axis-label'))
        ax.yaxis.label.set_color(chart_color('chart-axis-label'))
        ax.grid(
            axis='y', linestyle='--', linewidth=0.5,
            color=chart_color('chart-grid')
        )

        if len(self.original_grades) == 0:
            ax.set_yticks([0, 1])
            self.figure.tight_layout()
            self.canvas.draw()
            return

        ax.hist(
            self.original_grades, bins=10, range=(0, 100),
            color=chart_color('chart-original'),
            edgecolor=chart_color('chart-original-edge'),
            label='Original grades'
        )

        if show_corrected:
            ax.hist(
                self.corrected_grades, bins=10, range=(0, 100),
                color=chart_color('chart-corrected'),
                edgecolor=chart_color('chart-corrected-edge'),
                alpha=0.55,
                label='Corrected grades'
            )

        original_average = sum(self.original_grades) / len(self.original_grades)
        ax.axvline(
            original_average, color=chart_color('chart-original-average'), linewidth=2,
            label=f'Original average: {original_average:.1f}'
        )

        if show_corrected:
            corrected_average = sum(self.corrected_grades) / len(self.corrected_grades)
            ax.axvline(
                corrected_average,
                color=chart_color('chart-corrected-average'),
                linestyle='--',
                linewidth=2, label=f'Corrected average: {corrected_average:.1f}'
            )

        top = int(ax.get_ylim()[1])
        ax.set_yticks(range(0, top + 1))
        legend = ax.legend(loc='upper left')
        legend.get_frame().set_facecolor(chart_color('chart-legend-background'))
        legend.get_frame().set_edgecolor(chart_color('chart-legend-border'))
        for text in legend.get_texts():
            text.set_color(chart_color('chart-legend-text'))
        self.figure.tight_layout()
        self.canvas.draw()

    def update_file(self):
        with open(self.selected_file, 'r') as f:
            header = next(f).strip()

        with open(self.selected_file, 'w') as f:
            f.write(header)

            for i in range(len(self.student_ids)):
                student_id = self.student_ids[i]
                grade = self.corrected_grades[i]
                f.write(f'\n{student_id},{grade}')

        os.startfile(self.selected_file)
        self.message.setText('Grades saved.')

    def show_about_window(self):
        self.about_window.show()


if __name__ == '__main__':
    app = QApplication()
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    app.exec()