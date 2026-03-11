from PySide6.QtWidgets import QCheckBox

class FrequencyBand(QCheckBox):
    def __init__(self, name: str, start: float, end: float):
        QCheckBox.__init__(self, name)
        self.name = name;
        self.start = start
        self.end = end

