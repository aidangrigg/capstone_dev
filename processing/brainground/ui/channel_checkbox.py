from PySide6.QtWidgets import QCheckBox

class Channel(QCheckBox):
    def __init__(self, id: int):
        QCheckBox.__init__(self, f"Ch {id}")
        self.id = id
