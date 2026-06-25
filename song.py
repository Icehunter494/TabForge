import json


class TabNote:
    def __init__(
        self,
        string,
        fret,
        tick,
        duration=4
    ):
        self.string = string
        self.fret = fret
        self.tick = tick
        self.duration = duration

    def to_dict(self):
        return {
            "string": self.string,
            "fret": self.fret,
            "tick": self.tick,
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            string=data["string"],
            fret=data["fret"],
            tick=data["tick"],
            duration=data.get("duration", 1)
        )


class Song:
    def __init__(self):
        self.title = "Untitled Song"
        self.artist = ""
        self.bpm = 120
        self.time_signature_top = 4
        self.time_signature_bottom = 4

        self.notes = []

    def add_note(self, string, fret, tick, duration=1):
        note = TabNote(
            string=string,
            fret=fret,
            tick=tick,
            duration=duration
        )

        self.notes.append(note)

        self.notes.sort(key=lambda n: n.tick)

        return note

    def remove_note(self, note):
        if note in self.notes:
            self.notes.remove(note)

    def clear(self):
        self.notes.clear()

    def get_notes_at_tick(self, tick):
        return [
            note
            for note in self.notes
            if note.tick == tick
        ]

    def get_max_tick(self):
        if not self.notes:
            return 0

        return max(
            note.tick + note.duration
            for note in self.notes
        )

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "bpm": self.bpm,
            "time_signature_top": self.time_signature_top,
            "time_signature_bottom": self.time_signature_bottom,
            "notes": [
                note.to_dict()
                for note in self.notes
            ]
        }

    @classmethod
    def from_dict(cls, data):
        song = cls()

        song.title = data.get(
            "title",
            "Untitled Song"
        )

        song.artist = data.get(
            "artist",
            ""
        )

        song.bpm = data.get(
            "bpm",
            120
        )

        song.time_signature_top = data.get(
            "time_signature_top",
            4
        )

        song.time_signature_bottom = data.get(
            "time_signature_bottom",
            4
        )

        for note_data in data.get(
            "notes",
            []
        ):
            song.notes.append(
                TabNote.from_dict(note_data)
            )

        return song

    def save(self, filename):
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.to_dict(),
                f,
                indent=4
            )

    @classmethod
    def load(cls, filename):
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        return cls.from_dict(data)