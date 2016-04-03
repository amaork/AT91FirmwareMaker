# -*- coding: utf-8 -*-

import sys
import os
from PySide.QtGui import *
from PySide.QtCore import *
from fwmaker import FirmwareMaker


class FirmwareMakerGui(QWidget):

    SINGLE_FILE_MAXSIZE = 100 * 1024

    def __init__(self, parent=None):
        super(FirmwareMakerGui, self).__init__(parent)
        self.fwmaker = FirmwareMaker()

        self.components = list()
        self.__init_ui()
        self.__init_signal_slots()

    def __init_ui(self):
        self.component_list = QComboBox()
        self.component_list.addItems(self.fwmaker.DEFAULT_FILE_LIST)
        self.add = QPushButton("Add component")
        self.generate = QPushButton("Generate firmware")
        self.generate.setDisabled(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Components"))
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.component_list)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.add)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.generate)

        group = QGroupBox()
        self.layout = QGridLayout()
        group.setLayout(self.layout)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(group)
        self.setLayout(layout)

        self.def_width = 600
        self.def_height = 120
        self.setFixedSize(self.def_width, self.def_height)
        self.setWindowTitle("AT91 FirmwareMaker")

    def __flush_ui(self, key=None):

        if isinstance(key, str):
            self.component_list.addItem(key)
        else:
            self.component_list.removeItem(self.component_list.currentIndex())

        self.add.setEnabled(self.component_list.count())
        self.component_list.setEnabled(self.component_list.count())
        self.generate.setEnabled(self.component_list.count() != len(self.fwmaker.DEFAULT_FILE_LIST))
        self.setFixedSize(self.def_width, self.def_height + 40 * (6 - self.component_list.count()))

    def __get_element_id(self, row, column):
        return row * self.layout.columnCount() + column

    def __get_elements(self, element):
        for row in range(self.layout.rowCount()):
            for column in range(self.layout.columnCount()):
                item = self.layout.itemAt(self.__get_element_id(row, column))
                if not isinstance(item, QLayoutItem):
                    continue

                if item.widget() == element:
                    name = self.components[row]
                    elements = [self.layout.itemAt(self.__get_element_id(row, x)).widget()
                                for x in range(self.layout.columnCount())]

                    return name, elements

        return None, None

    def __get_component_setting(self, component):
        if component not in self.components:
            return None

        try:

            row = self.components.index(component)
            path = self.layout.itemAt(self.__get_element_id(row, 0)).widget().property("path")
            size = self.layout.itemAt(self.__get_element_id(row, 2)).widget().value() * 1024
            offset = self.layout.itemAt(self.__get_element_id(row, 4)).widget().value() * 1024

            return path, size, offset

        except AttributeError, e:

            print "Get component setting error:{0:s}".format(e)
            return None

    def __init_signal_slots(self):
        self.add.clicked.connect(self.slot_add_component)
        self.generate.clicked.connect(self.slot_generate_firmware)

    def slot_add_component(self):
        row = self.layout.rowCount()
        component = self.component_list.currentText().encode("ascii")

        file_label = QLabel(component[0].upper() + component[1:])
        file_size = QSpinBox()
        file_size.setRange(1, self.SINGLE_FILE_MAXSIZE)
        size_label = QLabel("size (KB):")

        file_offset = QSpinBox()
        file_offset.setMaximum(self.SINGLE_FILE_MAXSIZE * row)
        offset_label = QLabel("offset (KB)")

        select_file = QPushButton("Select file")
        select_file.clicked.connect(self.slot_get_select_file_path)
        remove_file = QPushButton("Remove")
        remove_file.clicked.connect(self.slot_remove_component)

        for column, element in enumerate((file_label,
                                          size_label, file_size,
                                          offset_label, file_offset,
                                          select_file, remove_file)):
            self.layout.addWidget(element, row, column)

        self.components.append(component)
        self.__flush_ui()

    def slot_remove_component(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        # Get component name and elements
        name, elements = self.__get_elements(sender)

        if not name or not elements:
            return

        # First remove ui element
        for element in elements:
            element.setHidden(True)
            self.layout.removeWidget(element)

        # Re add component to component list
        self.__flush_ui(name)
        self.components.remove(name)

    def slot_get_select_file_path(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        name, elements = self.__get_elements(sender)
        if not name or not elements:
            return

        path, _ = QFileDialog.getOpenFileName(self, self.tr("Select {0:s}".format(name)), "", self.tr("All (*)"))
        if not os.path.isfile(path):
            return

        label = elements[0]
        label.setProperty("path", path)

        file_size = (os.path.getsize(path) / 1024) + 1
        size = elements[2]
        size.setRange(file_size, file_size + self.SINGLE_FILE_MAXSIZE)
        size.setValue(file_size)

    def slot_generate_firmware(self):
        configure = list()

        # Get component configure data
        for component in self.components:
            setting = self.__get_component_setting(component)
            if not setting:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please check {0:s} setting".format(component)))
                return

            if not setting[0]:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select {0:s} files first".format(component)))
                return

            conf = self.fwmaker.generate_configure(component, setting[0], setting[1], setting[2])
            if not conf:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Generate {0:s} configure error".format(component)))
                return

            configure.append(conf)

        # Check configure data
        result, error = self.fwmaker.check_configure(configure)
        if not result:
            QMessageBox.critical(self, self.tr("Error"), self.tr(error))
            return

        # Start make firmware
        if not self.fwmaker.make_firmware(configure, "firmware.bin"):
            QMessageBox.critical(self, self.tr("Error"), self.tr(error))
            return
        else:
            QMessageBox.information(self, self.tr("Success"), self.tr("Firmware generate success!"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = FirmwareMakerGui()
    widget.show()
    sys.exit(app.exec_())
