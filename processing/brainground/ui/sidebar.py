
from PySide6.QtCore import QAbstractListModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListView, QMessageBox, QPushButton, QVBoxLayout, QWidget

from biomarker.base import Biomarker, BiomarkerIdentifier
from biomarker.types import BiomarkerTypes

class BiomarkerListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: list[BiomarkerIdentifier] = []

    def add(self, iden: BiomarkerIdentifier):
        # iden.name_changed.connect(self.layoutChanged.emit)
        row = len(self.items)
        self.beginInsertRows(QModelIndex(), row, row)
        self.items.append(iden)
        self.endInsertRows()

    def removeRows(self, row: int, count: int, /, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> bool:
        if parent.isValid():
            return False

        if row < 0 or count <= 0 or (row + count) > len(self.items):
            return False

        self.beginRemoveRows(parent, row, row + count - 1)

        for _ in range(count):
            del self.items[row]

        self.endRemoveRows()
        return True

    def rowCount(self, /, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.items)

    def getIden(self, index: QModelIndex | QPersistentModelIndex) -> BiomarkerIdentifier:
        return self.items[index.row()]

    def data(self, index: QModelIndex | QPersistentModelIndex, /, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            name = self.items[index.row()].name()
            return name

class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        form = QFormLayout()

        self.name = "Biomarker"
        name_field = QLineEdit(self.name)
        form.addRow("Name", name_field)

        name_field.textChanged.connect(self.on_name_changed)

        self.type = BiomarkerTypes.BANDPOWER

        type_field = QComboBox()
        type_field.addItems([e.name.capitalize() for e in BiomarkerTypes])
        type_field.setCurrentText(self.type.name.capitalize())
        type_field.currentTextChanged.connect(self.on_type_changed)

        form.addRow("Type", type_field)

        btn = QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        buttons = QDialogButtonBox(btn)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.setLayout(form)
        self.adjustSize()

    def on_name_changed(self, text: str):
        self.name = text

    def on_type_changed(self, text: str):
        for t in BiomarkerTypes:
            if t.name.lower() == text.lower():
                self.type = t
                return

# Signal out that new thing has been made (name, type)
# Connect to signal of BiomarkerIdentifier

class Sidebar(QWidget):
    biomarker_added = Signal(BiomarkerTypes, str)
    biomarker_deleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.bm_model = BiomarkerListModel()

        bm_label = QLabel("Biomarkers")
        self.bm_view = QListView()
        self.bm_view.setModel(self.bm_model)

        layout.addWidget(bm_label)
        layout.addWidget(self.bm_view)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.pressed.connect(self.spawn_add_dialog)

        remove_button = QPushButton("Remove")
        remove_button.pressed.connect(self.spawn_remove_dialog)

        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)

        layout.addLayout(button_layout)

    def add_biomarker(self, iden: BiomarkerIdentifier):
        self.bm_model.add(iden)

    def remove_biomarker(self, id: int):
        for i in range(self.bm_model.rowCount()):
            idx = self.bm_model.index(i)
            iden = self.bm_model.getIden(idx)

            if iden.id() == id:
                self.bm_model.removeRow(i)

    def spawn_add_dialog(self):
        dialog = AddDialog()

        if dialog.exec_():
            print(f"Sidebar add signal: {(dialog.type, dialog.name)}")
            self.biomarker_added.emit(dialog.type, dialog.name)

    def spawn_remove_dialog(self):
        idxs = self.bm_view.selectedIndexes()

        if len(idxs) == 1:
            iden = self.bm_model.getIden(idxs[0])

            button = QMessageBox.critical(
                self,
                "Delete confirmation",
                f"Are you sure you would like to delete \"{iden.name()}\"",
                buttons=QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                defaultButton=QMessageBox.StandardButton.Discard,
            )

            if button == QMessageBox.StandardButton.Discard:
                self.biomarker_deleted.emit(iden.id())
                self.remove_biomarker(iden.id())
