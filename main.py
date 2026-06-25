import sys
import json
import os
import ctypes


from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog,
    QLabel, QLineEdit, QMessageBox,
    QToolBar
)

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import QTimer

from song import Song
from tab_canvas import TabCanvas
from audio_engine import play_fret, set_guitar_type


# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TabForge V3.2 - Real-Time Engine")
        self.resize(1300, 700)

        self.song = Song()
        self.current_file = None

        # playback state
        self.playing = False
        self.play_tick = 0
        self.step_time = 0.1

        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.play_step)

        self.setup_ui()

    # ---------------- UI ----------------

    def setup_ui(self):

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        btn_new = QPushButton("New")
        btn_open = QPushButton("Open")
        btn_save = QPushButton("Save")
        self.btn_play = QPushButton("Play")

        btn_zoom_in = QPushButton("+")
        btn_zoom_out = QPushButton("-")

        btn_clean = QPushButton("Clean")
        btn_jazz = QPushButton("Jazz")
        btn_drive = QPushButton("Drive")
        btn_metal = QPushButton("Metal")

        toolbar.addWidget(btn_new)
        toolbar.addWidget(btn_open)
        toolbar.addWidget(btn_save)
        toolbar.addWidget(self.btn_play)

        toolbar.addSeparator()

        toolbar.addWidget(btn_zoom_in)
        toolbar.addWidget(btn_zoom_out)

        toolbar.addSeparator()

        toolbar.addWidget(btn_clean)
        toolbar.addWidget(btn_jazz)
        toolbar.addWidget(btn_drive)
        toolbar.addWidget(btn_metal)

        # file actions
        btn_new.clicked.connect(self.new_file)
        btn_open.clicked.connect(self.open_file)
        btn_save.clicked.connect(self.save_file)

        # playback
        self.btn_play.clicked.connect(self.toggle_play)

        # zoom
        btn_zoom_in.clicked.connect(self.zoom_in)
        btn_zoom_out.clicked.connect(self.zoom_out)

        # guitar types
        btn_clean.clicked.connect(lambda: set_guitar_type("clean"))
        btn_jazz.clicked.connect(lambda: set_guitar_type("jazz"))
        btn_drive.clicked.connect(lambda: set_guitar_type("overdrive"))
        btn_metal.clicked.connect(lambda: set_guitar_type("metal"))

        # spacebar play
        shortcut = QShortcut(QKeySequence("Space"), self)
        shortcut.activated.connect(self.toggle_play)

        # central widget
        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout()
        container.setLayout(layout)

        top = QHBoxLayout()
        top.addWidget(QLabel("Song:"))

        self.title = QLineEdit("Untitled Song")
        top.addWidget(self.title)

        layout.addLayout(top)

        # canvas
        self.canvas = TabCanvas(self.song)
        layout.addWidget(self.canvas)

    # ---------------- FILE ----------------

    def new_file(self):

        self.stop_playback()

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

        self.stop_playback()

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

    # ---------------- PLAYBACK ENGINE ----------------

    def toggle_play(self):

        if self.playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):

        if not self.song.notes:
            return

        self.playing = True
        self.play_tick = 0

        self.step_time = 60 / self.song.bpm / 4

        self.play_timer.start(int(self.step_time * 1000))

        self.btn_play.setText("Stop")

    def stop_playback(self):

        self.playing = False
        self.play_timer.stop()
        self.play_tick = 0

        self.canvas.set_playhead_tick(0)

        self.btn_play.setText("Play")

    def play_step(self):

        if not self.playing:
            return

        max_tick = self.song.get_max_tick()

        if self.play_tick > max_tick:
            self.stop_playback()
            return

        for note in self.song.get_notes_at_tick(self.play_tick):

            play_fret(
                note.string,
                note.fret,
                duration=note.duration * self.step_time
            )

        self.canvas.set_playhead_tick(self.play_tick)

        self.play_tick += 1

    # ---------------- ZOOM ----------------

    def zoom_in(self):
        self.canvas.zoom_in()

    def zoom_out(self):
        self.canvas.zoom_out()


# ---------------- RUN ----------------
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())