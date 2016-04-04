# -*- coding: utf-8 -*-

import os
import sys
import json
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
        self.__init_data()
        self.__init_signal_slots()

    def __init_ui(self):
        self.component_list = QComboBox()
        self.component_list.addItems(self.fwmaker.DEFAULT_FILE_LIST)
        self.add = QPushButton("Add")
        self.load = QPushButton("Load")
        self.store = QPushButton("Save as")
        self.generate = QPushButton("Generate")
        self.generate.setDisabled(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Components"))
        top_layout.addWidget(self.component_list)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.add)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.load)
        top_layout.addWidget(QSplitter())
        top_layout.addWidget(self.store)
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

    def __init_data(self):
        # Load configure file
        result, configure = self.fwmaker.load_configure(self.fwmaker.DEF_SETTING_PATH)
        if not result:
            return

        # Check configure file
        result, error = self.fwmaker.check_configure(configure)
        if not result:
            print "Load default setting: {0:s}, error: {1:s}".format(self.fwmaker.DEF_SETTING_PATH, error)
            return

        # Sync ui
        self.__sync_ui(configure)

    def __init_signal_slots(self):
        self.add.clicked.connect(self.slot_add_component)
        self.load.clicked.connect(self.slot_load_configure)
        self.store.clicked.connect(self.slot_store_configure)
        self.generate.clicked.connect(self.slot_generate_firmware)

    def __sync_ui(self, configure):
        try:

            # Remove old elements from layout
            for idx in range(self.layout.count()):
                item = self.layout.itemAt(0)
                if isinstance(item, QLayoutItem):
                    widget_ = item.widget()
                    if isinstance(widget_, QWidget):
                        self.layout.removeWidget(widget_)
                        widget_.setHidden(True)
                        del widget_

            for idx in range(self.component_list.count()):
                self.component_list.removeItem(0)

            self.components = list()
            self.component_list.addItems(self.fwmaker.DEFAULT_FILE_LIST)

            # According configure add new elements
            for component in configure:
                name = component.keys()[0]
                setting = component.get(name)
                path = setting.get("path")
                size = setting.get("size")
                offset = setting.get("offset")
                size = size if isinstance(size, int) else self.fwmaker.str2number(size)
                offset = offset if isinstance(offset, int) else self.fwmaker.str2number(offset)

                for idx in range(self.component_list.count()):
                    if self.component_list.itemText(idx) == name:
                        self.component_list.setCurrentIndex(idx)
                        break

                # Create ui elements
                self.slot_add_component()

                # Setting ui data
                self.__set_component_setting(name, path, size, offset)

        except StandardError, e:
            print "Sync ui error:{0:s}".format(e)

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
        try:

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

        except StandardError, e:
            print "Get elements error:{0:s}".format(e)
            return None, None

        return None, None

    def __get_component_elements(self, component):
        if component not in self.components:
            return None

        row = self.components.index(component)
        return [self.layout.itemAt(self.__get_element_id(row, column)).widget()
                for column in range(self.layout.columnCount())]

    def __get_component_setting(self, component):
        if component not in self.components:
            return None

        try:

            path = None
            size = None
            offset = None
            for element in self.__get_component_elements(component):
                if isinstance(element, QObject):
                    tag = element.property("tag")
                    if tag == "path" and isinstance(element, QLabel):
                        path = element.property("path")
                    elif tag == "size" and isinstance(element, QSpinBox):
                        size = element.value() * 1024
                    elif tag == "offset" and isinstance(element, QSpinBox):
                        offset = element.value() * 1024

            return path, size, offset

        except StandardError, e:

            print "Get component setting error:{0:s}".format(e)
            return None

    def __set_component_setting(self, component, path, size, offset):
        try:

            for element in self.__get_component_elements(component):
                if isinstance(element, QObject):
                    tag = element.property("tag")
                    if tag == "path" and isinstance(element, QLabel):
                        element.setProperty("path", path)
                    elif tag == "size" and isinstance(element, QSpinBox):
                        element.setValue(size / 1024)
                    elif tag == "offset" and isinstance(element, QSpinBox):
                        element.setValue(offset / 1024)

        except StandardError, e:
            print "Set component setting error:{0:s}".format(e)
            return False

        return True

    def __get_current_setting(self):
        configure = list()

        # Get component configure data
        for component in self.components:
            setting = self.__get_component_setting(component)
            if not setting:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please check {0:s} setting".format(component)))
                return None

            if not setting[0]:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select {0:s} files first".format(component)))
                return None

            conf = self.fwmaker.generate_configure(component, setting[0], setting[1], setting[2])
            if not conf:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Generate {0:s} configure error".format(component)))
                return None

            configure.append(conf)

        # Check configure data
        result, error = self.fwmaker.check_configure(configure)
        if not result:
            QMessageBox.critical(self, self.tr("Error"), self.tr(error))
            return None

        return configure

    def slot_add_component(self):
        row = self.layout.rowCount()
        component = self.component_list.currentText().encode("ascii")

        file_label = QLabel(component[0].upper() + component[1:])
        file_label.setProperty("tag", "path")

        file_size = QSpinBox()
        file_size.setProperty("tag", "size")
        file_size.setRange(1, self.SINGLE_FILE_MAXSIZE)
        size_label = QLabel("size (KB):")

        file_offset = QSpinBox()
        file_offset.setProperty("tag", "offset")
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

    def slot_load_configure(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Select configure file"), "", self.tr("Json (*.json)"))
        if not os.path.isfile(path):
            return

        result, configure = self.fwmaker.load_configure(path)
        if not result:
            QMessageBox.critical(self, self.tr("Load error"), self.tr("Error:{0:s}".format(configure)))
            return

        result, error = self.fwmaker.check_configure(configure)
        if not result:
            QMessageBox.critical(self, self.tr("Check error"), self.tr("Error:{0:s}".format(error)))
            return

        # Sync ui
        self.__sync_ui(configure)

    def slot_store_configure(self):
        configure = self.__get_current_setting()
        if not configure:
            return

        save_path, _ = QFileDialog.getSaveFileName(self, self.tr("Select save as path"), "",
                                                self.tr("Json (*.json)"))

        if len(save_path) == 0:
            return

        with open(save_path, "wb") as fp:
            json.dump(configure, fp, indent=4)

        QMessageBox.information(self, self.tr("Success"), self.tr("Configure file save as success!"))

    def slot_get_select_file_path(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        name, elements = self.__get_elements(sender)
        if not name or not elements:
            return

        # Get file path and size
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Select {0:s}".format(name)), "", self.tr("All (*)"))
        if not os.path.isfile(path):
            return
        else:
            file_size = (os.path.getsize(path) / 1024) + 1

        # Set file path and size
        for element in elements:
            if isinstance(element, QObject):
                tag = element.property("tag")
                if tag == "path" and isinstance(element, QLabel):
                    element.setProperty("path", path)
                elif tag == "size" and isinstance(element, QSpinBox):
                    element.setRange(file_size, file_size + self.SINGLE_FILE_MAXSIZE)
                    element.setValue(file_size)

    def slot_generate_firmware(self):
        configure = self.__get_current_setting()
        if not configure:
            return

        # Select output path
        output, _ = QFileDialog.getSaveFileName(self, self.tr("Select firmware save path:"), "",
                                                self.tr("Firmware (*.bin)"))
        if len(output) == 0:
            return

        # Start make firmware
        result, err_or_md5 = self.fwmaker.make_firmware(configure, output)

        if not result:
            QMessageBox.critical(self, self.tr("Error"), self.tr(err_or_md5))
            return
        else:
            with open(self.fwmaker.DEF_SETTING_PATH, "wb") as fp:
                    json.dump(configure, fp, indent=4)

            QMessageBox.information(self, self.tr("Success"),
                                    self.tr("Firmware generate success!\nMd5: {0:s}".format(err_or_md5)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = FirmwareMakerGui()
    widget.show()
    sys.exit(app.exec_())
