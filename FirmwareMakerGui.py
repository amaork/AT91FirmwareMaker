# -*- coding: utf-8 -*-

import os
import sys
import json
import icon_rc
from PySide.QtGui import *
from PySide.QtCore import *
from fwmaker import FirmwareMaker
from PyAppFramework.gui.container import ComponentManager


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
        group.setProperty("name", "components")
        group.setLayout(QGridLayout())

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(group)
        self.setLayout(layout)

        # Create component manager
        self.uiManager = ComponentManager(self)

        self.def_width = 600
        self.def_height = 120
        self.setFixedSize(self.def_width, self.def_height)
        self.setWindowTitle("AT91 FirmwareMaker")
        self.setWindowIcon(QIcon(":/icon/icon.ico"))

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
            group = self.uiManager.getByValue("name", "components")
            for item in self.uiManager.getAllComponents(group):
                layout = self.uiManager.getParentLayout(item)
                if isinstance(layout, QLayout):
                    layout.removeWidget(item)
                    item.setHidden(True)
                    del item

            for idx in range(self.component_list.count()):
                self.component_list.removeItem(0)

            self.components = list()
            self.component_list.addItems(self.fwmaker.DEFAULT_FILE_LIST)

            # According configure add new elements
            for component in configure:
                name = component.keys()[0].encode("utf-8")
                setting = component.get(name)
                for idx in range(self.component_list.count()):
                    if self.component_list.itemText(idx) == name:
                        self.component_list.setCurrentIndex(idx)
                        break

                # Create ui elements
                self.slot_add_component()

                # Setting ui data
                if not self.__set_component_setting(name, setting):
                    print "Setting {0:s} setting error".format(name)

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

    def __get_component_setting(self, component):
        if component not in self.components:
            return None

        setting = self.uiManager.getData(component)

        if setting.get("size"):
            setting["size"] = "{0:s}k".format(setting.get("size"))
        else:
            return None

        if setting.get("offset"):
            setting["offset"] = "{0:s}k".format(setting.get("offset"))
        else:
            return None

        return setting

    def __set_component_setting(self, component, setting):
        if component not in self.components:
            return False

        if not isinstance(setting, dict):
            return False

        if "size" in setting.keys() and "offset" in setting.keys() and "path" in setting.keys():
            setting["size"] = self.fwmaker.str2number(setting.get("size")) / 1024
            setting["offset"] = self.fwmaker.str2number(setting.get("offset")) / 1024
        else:
            return False

        return self.uiManager.setData(component, setting)

    def __get_current_setting(self):
        configure = list()

        # Get component configure data
        for component in self.components:
            setting = self.__get_component_setting(component)
            if not setting:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please check {0:s} setting".format(component)))
                return None

            if not setting.get("path"):
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select {0:s} files first".format(component)))
                return None

            configure.append({component: setting})

        # Check configure data
        result, error = self.fwmaker.check_configure(configure)
        if not result:
            QMessageBox.critical(self, self.tr("Error"), self.tr(error))
            return None

        return configure

    def slot_add_component(self):
        groups = self.uiManager.getByValue("name", "components")
        if not groups:
            return

        components_layout = groups.layout()
        if not isinstance(components_layout, QGridLayout):
            return

        row = components_layout.rowCount()
        component = self.component_list.currentText().encode("utf-8")

        file_label = QLabel(component[0].upper() + component[1:])

        file_path = QLineEdit()
        file_path.setDisabled(True)
        file_path.setHidden(True)
        file_path.setProperty(component, "path")

        file_size = QSpinBox()
        file_size.setProperty(component, "size")
        file_size.setRange(1, self.SINGLE_FILE_MAXSIZE)
        size_label = QLabel("size (KB):")

        file_offset = QSpinBox()
        file_offset.setProperty(component, "offset")
        file_offset.setMaximum(self.SINGLE_FILE_MAXSIZE * row)
        offset_label = QLabel("offset (KB)")

        select_file = QPushButton("Select file")
        select_file.clicked.connect(self.slot_get_select_file_path)
        select_file.setProperty("name", component)

        remove_file = QPushButton("Remove")
        remove_file.clicked.connect(self.slot_remove_component)
        remove_file.setProperty("name", component)

        for column, element in enumerate((file_label, file_path,
                                          size_label, file_size,
                                          offset_label, file_offset,
                                          select_file, remove_file)):
            components_layout.addWidget(element, row, column)

        self.components.append(component)
        self.__flush_ui()

    def slot_remove_component(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        # Get component name and elements
        name = sender.property("name").encode("utf-8")
        layout = self.uiManager.getParentLayout(sender)
        elements = self.uiManager.findRowSibling(sender)

        if not name or not elements:
            return

        # First remove ui element
        for element in elements:
            element.setHidden(True)
            layout.removeWidget(element)

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

        name = sender.property("name").encode("utf-8")
        elements = self.uiManager.findRowSibling(sender)

        if not name or not elements:
            return

        # Get file path and size
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Select {0:s}".format(name)), "", self.tr("All (*)"))
        if not os.path.isfile(path):
            return
        else:
            size = (os.path.getsize(path) / 1024) + 1

        # Set file path and size
        if not self.uiManager.setData(name, {"path": path, "size": size}):
            print "Set {0:s} size and path error".format(name)

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
