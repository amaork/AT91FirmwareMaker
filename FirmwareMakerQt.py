# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui
from fwmaker import FirmwareMaker


class FirmwareMakerGui(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FirmwareMakerGui, self).__init__(parent)
        self.fwmaker = FirmwareMaker()

        self.data = dict()
        self.__init_ui()
        self.__init_signal_slots()

    def __init_ui(self):
        self.component = QtGui.QComboBox()
        self.component.addItems(self.fwmaker.DEFAULT_FILE_LIST)
        self.add = QtGui.QPushButton("Add component")
        self.generate = QtGui.QPushButton("Generate firmware")

        top_layout = QtGui.QHBoxLayout()
        top_layout.addWidget(QtGui.QLabel("Components"))
        top_layout.addWidget(self.component)
        top_layout.addWidget(QtGui.QSplitter())
        top_layout.addWidget(self.add)
        top_layout.addWidget(self.generate)

        self.layout = QtGui.QGridLayout()

        layout = QtGui.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(self.layout)
        self.setLayout(layout)

        self.setWindowTitle("AT91 FirmwareMaker")

    def __init_signal_slots(self):
        self.add.clicked.connect(self.__slot_add_component)
        self.generate.clicked.connect(self.__slot_generate_firmware)

    def __slot_add_component(self):
        print self.sender() == self.add
        items = dict()
        row = self.layout.rowCount()
        component = self.component.currentText().encode("ascii")
        component = component[0].upper() + component[1:] + ":"

        file_label = QtGui.QLabel(component)
        file_size = QtGui.QSpinBox()
        size_label = QtGui.QLabel("size (KB):")

        file_offset = QtGui.QSpinBox()
        offset_label = QtGui.QLabel("offset (KB)")

        select_file = QtGui.QPushButton("Select file")
        select_file.clicked.connect(self.__slot_get_select_file_path)
        remove_file = QtGui.QPushButton("Remove")
        remove_file.clicked.connect(self.__slot_remove_component)

        self.data.setdefault(component, (file_size, file_offset, select_file, remove_file))

        for column, element in enumerate((file_label,
                                          size_label, file_size,
                                          offset_label, file_offset,
                                          select_file, remove_file)):
            self.layout.addWidget(element, row, column)

        # Remove already added component
        self.component.removeItem(self.component.currentIndex())

        # All added disable add
        if self.component.count() == 0:
            self.add.setDisabled(True)
            self.component.setDisabled(True)

    def __slot_remove_component(self):
        sender = self.sender()
        print self.sender()
        if not isinstance(sender, QtGui.QPushButton):
            return

        for key, value in self.data.items():
            print key, value

    def __slot_get_select_file_path(self):
        pass

    def __slot_generate_firmware(self):
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = FirmwareMakerGui()
    widget.show()
    sys.exit(app.exec_())
