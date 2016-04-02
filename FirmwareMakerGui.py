# -*- coding: utf-8 -*-

import sys
from PySide.QtGui import *
from PySide.QtCore import *
from fwmaker import FirmwareMaker


class FirmwareMakerGui(QWidget):
    def __init__(self, parent=None):
        super(FirmwareMakerGui, self).__init__(parent)
        self.fwmaker = FirmwareMaker()

        self.data = dict()
        self.__init_ui()
        self.__init_signal_slots()

    def __init_ui(self):
        self.component = QComboBox()
        self.component.addItems(self.fwmaker.DEFAULT_FILE_LIST)
        self.add = QPushButton("Add component")
        self.generate = QPushButton("Generate firmware")

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Components"))
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.component)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.add)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.generate)

        self.layout = QGridLayout()

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(self.layout)
        self.setLayout(layout)

        self.def_width = 600
        self.def_height = 80
        self.setFixedSize(self.def_width, self.def_height)
        self.setWindowTitle("AT91 FirmwareMaker")

    def __flush_ui(self, key=None):

        if isinstance(key, str):
            self.component.addItem(key)
        else:
            self.component.removeItem(self.component.currentIndex())

        if self.component.count() == 0:
            self.add.setDisabled(True)
            self.component.setDisabled(True)
        else:
            self.add.setEnabled(True)
            self.component.setEnabled(True)

        self.setFixedSize(self.def_width, self.def_height + 40 * (6 - self.component.count()))

    def __init_signal_slots(self):
        self.add.clicked.connect(self.slot_add_component)
        self.generate.clicked.connect(self.slot_generate_firmware)

    def slot_add_component(self):
        elements = list()
        row = self.layout.rowCount()
        component = self.component.currentText().encode("ascii")

        file_label = QLabel(component[0].upper() + component[1:])
        file_size = QSpinBox()
        size_label = QLabel("size (KB):")

        file_offset = QSpinBox()
        offset_label = QLabel("offset (KB)")

        select_file = QPushButton("Select file")
        select_file.clicked.connect(self.slot_get_select_file_path)
        remove_file = QPushButton("Remove")
        remove_file.clicked.connect(self.slot_remove_component)

        for column, element in enumerate((file_label,
                                          size_label, file_size,
                                          offset_label, file_offset,
                                          select_file, remove_file)):
            elements.append(element)
            self.layout.addWidget(element, row, column)

        self.data[component] = elements
        self.__flush_ui()

    def slot_remove_component(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        # Compare which component will remove
        for key, value in self.data.items():
            if sender != value[-1]:
                continue

            # First remove ui element
            for element in value:
                element.setHidden(True)
                self.layout.removeWidget(element)

            # Re add component to component list
            self.__flush_ui(key)

    def slot_get_select_file_path(self):
        pass

    def slot_generate_firmware(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = FirmwareMakerGui()
    widget.show()
    sys.exit(app.exec_())
