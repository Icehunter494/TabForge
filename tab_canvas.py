from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QInputDialog,
    QMenu
)

from PySide6.QtGui import (
    QPen,
    QColor,
    QFont,
    QPainter
)

from PySide6.QtCore import Qt


STRING_SPACING = 40
TOP_MARGIN = 100

TICK_WIDTH = 30
NUM_STRINGS = 6

BEATS_PER_MEASURE = 4
TICKS_PER_BEAT = 4

MEASURE_WIDTH = (
    BEATS_PER_MEASURE *
    TICKS_PER_BEAT *
    TICK_WIDTH
)


class TabCanvas(QGraphicsView):

    def __init__(self, song):
        super().__init__()

        self.song = song

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.selected_note = None
        self.playhead_tick = 0

        self.zoom_factor = 1.0

        self.setRenderHint(QPainter.Antialiasing)

        self.scene.setSceneRect(
            0,
            0,
            2000,
            500
        )

        self.redraw()

    # core

    def redraw(self):

        self.update_scene_bounds()

        self.scene.clear()

        self.draw_strings()
        self.draw_measures()
        self.draw_notes()
        self.draw_playhead()

    # dynamic time

    def update_scene_bounds(self):

        if not self.song.notes:
            return

        max_tick = max(
            note.tick + note.duration
            for note in self.song.notes
        )

        width = max_tick * TICK_WIDTH + 500

        current = self.scene.sceneRect()

        if width > current.width():

            self.scene.setSceneRect(
                0,
                0,
                width,
                current.height()
            )

    # draw

    def draw_strings(self):

        pen = QPen(QColor(180, 180, 180))

        for string in range(NUM_STRINGS):

            y = (
                TOP_MARGIN +
                string * STRING_SPACING
            )

            self.scene.addLine(
                0,
                y,
                self.scene.width(),
                y,
                pen
            )

    def draw_measures(self):

        pen = QPen(QColor(120, 120, 120))

        for x in range(
            0,
            int(self.scene.width()),
            MEASURE_WIDTH
        ):

            self.scene.addLine(
                x,
                TOP_MARGIN - 20,
                x,
                TOP_MARGIN + 220,
                pen
            )

    def draw_notes(self):

        font = QFont()
        font.setPointSize(12)

        for note in self.song.notes:

            x = note.tick * TICK_WIDTH

            y = (
                TOP_MARGIN +
                note.string * STRING_SPACING
            )

            duration_width = note.duration * TICK_WIDTH

            pen = QPen(QColor(80, 80, 80))

            self.scene.addLine(
                x,
                y,
                x + duration_width,
                y,
                pen
            )

            text = self.scene.addText(
                str(note.fret),
                font
            )

            text.setPos(
                x - 8,
                y - 14
            )

            if note == self.selected_note:
                text.setDefaultTextColor(QColor(255, 0, 0))

    def draw_playhead(self):

        x = self.playhead_tick * TICK_WIDTH

        view_right = (
            self.horizontalScrollBar().value()
            + self.viewport().width()
        )

        if x > view_right - 200:
            self.horizontalScrollBar().setValue(
                x - self.viewport().width() + 200
            )

        pen = QPen(QColor(255, 50, 50))
        pen.setWidth(2)

        self.scene.addLine(
            x,
            TOP_MARGIN - 40,
            x,
            TOP_MARGIN + 250,
            pen
        )

    # ---------------- NOTE DETECTION ----------------

    def find_note(self, mouse_x, mouse_y):

        for note in self.song.notes:

            note_x = note.tick * TICK_WIDTH

            note_y = (
                TOP_MARGIN +
                note.string * STRING_SPACING
            )

            duration_width = note.duration * TICK_WIDTH

            if (
                mouse_x >= note_x - 15 and
                mouse_x <= note_x + duration_width + 15 and
                abs(mouse_y - note_y) < 20
            ):
                return note

        return None

    # input

    def mousePressEvent(self, event):

        scene_pos = self.mapToScene(event.pos())

        x = scene_pos.x()
        y = scene_pos.y()

        clicked = self.find_note(x, y)

        if clicked:
            self.selected_note = clicked
            self.redraw()
            return

        string = round((y - TOP_MARGIN) / STRING_SPACING)

        if string < 0 or string >= NUM_STRINGS:
            return

        tick = int(x / TICK_WIDTH)

        fret, ok = QInputDialog.getInt(
            self,
            "Add Note",
            "Fret:",
            0,
            0,
            36
        )

        if not ok:
            return

        self.song.add_note(
            string,
            fret,
            tick,
            duration=4
        )

        self.redraw()

    def contextMenuEvent(self, event):

        scene_pos = self.mapToScene(event.pos())

        note = self.find_note(scene_pos.x(), scene_pos.y())

        if not note:
            return

        menu = QMenu(self)

        edit_fret = menu.addAction("Edit Fret")
        edit_duration = menu.addAction("Edit Duration")
        delete_note = menu.addAction("Delete Note")

        action = menu.exec(event.globalPos())

        if action == edit_fret:
            self.change_fret(note)

        elif action == edit_duration:
            self.change_duration(note)

        elif action == delete_note:
            self.delete_note(note)

    # editing

    def change_fret(self, note):

        fret, ok = QInputDialog.getInt(
            self,
            "Edit Fret",
            "Fret:",
            note.fret,
            0,
            36
        )

        if ok:
            note.fret = fret
            self.redraw()

    def change_duration(self, note):

        duration, ok = QInputDialog.getInt(
            self,
            "Edit Duration",
            "Duration (ticks):",
            note.duration,
            1,
            64
        )

        if ok:
            note.duration = duration
            self.redraw()

    def delete_note(self, note):

        self.song.remove_note(note)

        if self.selected_note == note:
            self.selected_note = None

        self.redraw()

    # util

    def set_playhead_tick(self, tick):
        self.playhead_tick = tick
        self.redraw()

    def delete_selected(self):

        if self.selected_note:
            self.song.remove_note(self.selected_note)
            self.selected_note = None
            self.redraw()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:
            self.delete_selected()
            return

        super().keyPressEvent(event)

    def wheelEvent(self, event):

        delta = event.angleDelta().y()

        scroll_speed = 1.2

        if delta > 0:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(30 * scroll_speed)
            )
        else:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + int(30 * scroll_speed)
            )