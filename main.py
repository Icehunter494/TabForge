import sys
import json
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog,
    QLabel, QLineEdit, QMessageBox,
    QToolBar
)

from PySide6.QtGui import QShortcut, QKeySequence

from song import Song
from tab_canvas import TabCanvas
from audio_engine import play_fret, set_guitar_type


#main
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TabForge V3 - Guitar Editor")
        self.resize(1300, 700)

        self.song = Song()
        self.current_file = None

        self.setup_ui()

    # ui
    def setup_ui(self):

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # file
        btn_new = QPushButton("New")
        btn_open = QPushButton("Open")
        btn_save = QPushButton("Save")
        btn_play = QPushButton("Play")

        # vroom vroom zoom
        btn_zoom_in = QPushButton("+")
        btn_zoom_out = QPushButton("-")

        # el guitar
        btn_clean = QPushButton("Clean")
        btn_jazz = QPushButton("Jazz")
        btn_drive = QPushButton("Drive")
        btn_metal = QPushButton("Metal")

        toolbar.addWidget(btn_new)
        toolbar.addWidget(btn_open)
        toolbar.addWidget(btn_save)
        toolbar.addWidget(btn_play)

        toolbar.addSeparator()

        toolbar.addWidget(btn_zoom_in)
        toolbar.addWidget(btn_zoom_out)

        toolbar.addSeparator()

        toolbar.addWidget(btn_clean)
        toolbar.addWidget(btn_jazz)
        toolbar.addWidget(btn_drive)
        toolbar.addWidget(btn_metal)

        # file action
        btn_new.clicked.connect(self.new_file)
        btn_open.clicked.connect(self.open_file)
        btn_save.clicked.connect(self.save_file)
        btn_play.clicked.connect(self.play_song)

        # more zoomies
        btn_zoom_in.clicked.connect(self.zoom_in)
        btn_zoom_out.clicked.connect(self.zoom_out)

        # el dos guitar
        btn_clean.clicked.connect(lambda: set_guitar_type("clean"))
        btn_jazz.clicked.connect(lambda: set_guitar_type("jazz"))
        btn_drive.clicked.connect(lambda: set_guitar_type("overdrive"))
        btn_metal.clicked.connect(lambda: set_guitar_type("metal"))

        # crank that up
        shortcut = QShortcut(QKeySequence("Space"), self)
        shortcut.activated.connect(self.play_song)

        # widget
        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout()
        container.setLayout(layout)

        top = QHBoxLayout()

        top.addWidget(QLabel("Song:"))

        self.title = QLineEdit("Untitled Song")

        top.addWidget(self.title)

        layout.addLayout(top)

        # 🎸 CANVAS
        self.canvas = TabCanvas(self.song)
        layout.addWidget(self.canvas)

    # -da save system

    def new_file(self):

        self.song = Song()
        self.canvas.song = self.song
        self.canvas.selected_note = None
        self.canvas.redraw()

        self.title.setText("Untitled Song")
        self.current_file = None

    def save_file(self):

        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save TabForge File",
                "",
                "TabForge (*.tab)"
            )
            if not path:
                return
            self.current_file = path

        data = {
            "title": self.title.text(),
            "song": self.song.to_dict()
        }

        with open(self.current_file, "w") as f:
            json.dump(data, f, indent=2)

        QMessageBox.information(
            self,
            "Saved",
            "Song saved successfully"
        )

    def open_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open TabForge File",
            "",
            "TabForge (*.tab)"
        )

        if not path:
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.song = Song.from_dict(data.get("song", {}))

        self.title.setText(data.get("title", "Untitled Song"))

        self.canvas.song = self.song
        self.canvas.selected_note = None
        self.canvas.redraw()

        self.current_file = path

    # playback

    def play_song(self):

        if not self.song.notes:
            return

        bpm = self.song.bpm
        step = 60 / bpm / 4  # 16th note resolution

        max_tick = self.song.get_max_tick()

        for tick in range(max_tick + 1):

            for note in self.song.get_notes_at_tick(tick):

                play_fret(
                    note.string,
                    note.fret,
                    duration=note.duration * step
                )

            self.canvas.set_playhead_tick(tick)

            QApplication.processEvents()
            time.sleep(step)

    # zoom the trilogy

    def zoom_in(self):
        self.canvas.zoom_in()

    def zoom_out(self):
        self.canvas.zoom_out()


# run it
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())