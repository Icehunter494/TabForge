import sys
import json

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QLineEdit,
    QToolBar
)

from PySide6.QtCore import Qt

from reportlab.pdfgen import canvas


STRINGS = ["E", "B", "G", "D", "A", "E"]
COLUMNS = 64


class TabEditor(QTableWidget):

    def __init__(self):
        super().__init__(6, COLUMNS)

        self.setVerticalHeaderLabels(STRINGS)

        for col in range(COLUMNS):
            self.setColumnWidth(col, 35)

        self.setAlternatingRowColors(True)

    def get_data(self):
        data = []

        for row in range(6):
            row_data = []

            for col in range(COLUMNS):
                item = self.item(row, col)

                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")

            data.append(row_data)

        return data

    def load_data(self, data):

        self.clearContents()

        for row in range(min(6, len(data))):
            for col in range(min(COLUMNS, len(data[row]))):

                value = data[row][col]

                if value != "":
                    self.setItem(
                        row,
                        col,
                        QTableWidgetItem(value)
                    )


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TabForge v0.1")
        self.resize(1400, 500)

        self.current_file = None

        self.setup_ui()

    def setup_ui(self):

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        new_btn = QPushButton("New")
        save_btn = QPushButton("Save")
        open_btn = QPushButton("Open")
        pdf_btn = QPushButton("Export PDF")
        play_btn = QPushButton("Play")

        toolbar.addWidget(new_btn)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addWidget(pdf_btn)
        toolbar.addWidget(play_btn)

        new_btn.clicked.connect(self.new_project)
        open_btn.clicked.connect(self.open_project)
        save_btn.clicked.connect(self.save_project)
        pdf_btn.clicked.connect(self.export_pdf)
        play_btn.clicked.connect(self.play_song)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        central.setLayout(layout)

        title_row = QHBoxLayout()

        title_row.addWidget(QLabel("Song Title:"))

        self.title_edit = QLineEdit()
        self.title_edit.setText("Untitled Song")

        title_row.addWidget(self.title_edit)

        layout.addLayout(title_row)

        self.editor = TabEditor()

        layout.addWidget(self.editor)

    def new_project(self):

        self.title_edit.setText("Untitled Song")
        self.editor.clearContents()
        self.current_file = None

    def save_project(self):

        if not self.current_file:

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Project",
                "",
                "TabForge Files (*.tabforge)"
            )

            if not filename:
                return

            self.current_file = filename

        data = {
            "title": self.title_edit.text(),
            "grid": self.editor.get_data()
        }

        with open(self.current_file, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(
            self,
            "Saved",
            "Project saved successfully."
        )

    def open_project(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "TabForge Files (*.tabforge)"
        )

        if not filename:
            return

        with open(filename, "r") as f:
            data = json.load(f)

        self.title_edit.setText(
            data.get("title", "Untitled Song")
        )

        self.editor.load_data(
            data.get("grid", [])
        )

        self.current_file = filename

    def export_pdf(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not filename:
            return

        pdf = canvas.Canvas(filename)

        pdf.setFont("Courier", 12)

        y = 800

        pdf.drawString(
            50,
            y,
            self.title_edit.text()
        )

        y -= 40

        grid = self.editor.get_data()

        for row in range(6):

            line = STRINGS[row] + "|"

            for col in range(COLUMNS):

                value = grid[row][col]

                if value == "":
                    line += "--"
                else:
                    line += value

            pdf.drawString(
                50,
                y,
                line
            )

            y -= 20

        pdf.save()

        QMessageBox.information(
            self,
            "Export Complete",
            "PDF exported successfully."
        )

    def play_song(self):

        QMessageBox.information(
            self,
            "Playback",
            "Playback engine coming in next version."
        )


def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()