# -*- coding: utf-8 -*-

import os
import json


__all__ = ['FirmwareMaker']


class FirmwareMaker(object):

    DEF_OUTPUT_PATH = "firmware"
    DEF_OUTPUT_FILE = "firmware.bin"
    DEF_SETTING_PATH = "settings.json"
    ESSENTIAL_FILE_LIST = ["bootstrap", "kernel", "rootfs"]
    DEFAULT_FILE_LIST = ["bootstrap", "u-boot", "u-boot env", "dtb", "kernel", "rootfs"]

    @staticmethod
    def generate_configure(file_list):
        """Generate default configure file

        :param file_list: firmware file lists
        :return: success return true else false
        """
        offset = 0x0
        size = 0x100000

        if not isinstance(file_list, list):
            print "Parameter must be a string list!"
            return False

        default_settings = []

        # Write to settings
        for file_name in file_list:
            # Make sure file is in the list
            if file_name not in FirmwareMaker.DEFAULT_FILE_LIST:
                print "Unknown file:", file_name
                return False

            # Generate default setting
            default_settings.append({file_name: {
                "offset": "{0:x}".format(offset),
                "size": "{0:x}".format(size),
                "path": "{0:s}.bin".format(file_name)}})

            # Update offset
            offset += size

        # Write settings to json file
        with open(FirmwareMaker.DEF_SETTING_PATH, "w") as fp:
            json.dump(default_settings, fp, indent=4)

        print "Setting file:{0:s} is generated, include{1:s}".format(FirmwareMaker.DEF_SETTING_PATH, file_list)
        return True

    @staticmethod
    def load_configure(file_path):
        """Load settings.json to memory

        :param file_path: settings file path
        :return: (result,setting list)
        """
        setting = []

        try:

            with open(file_path) as fp:
                setting = json.load(fp)

        except(ValueError, IOError), e:

            print "Load settings error:", e
            return False, setting

        return True, setting

    @staticmethod
    def check_configure(setting, verbose=True):
        """Check settings

        :param setting: setting data
        :param verbose: Debug message output control
        :return: result, error-message
        """

        err_msg = str()

        try:
            # Type check
            if not isinstance(setting, list):
                err_msg = "Invalid settings!"
                return False, err_msg

            # Get setting names
            setting_name = [item.keys()[0] for item in setting]

            # Make sure essential file is exist
            for name in FirmwareMaker.ESSENTIAL_FILE_LIST:
                if name not in setting_name:
                    err_msg = "Essential file:{0:s} is not exist!".format(name)
                    return False, err_msg

            # Check each file offset and size
            current_offset = 0
            for name, data in zip(setting_name, setting):
                # print name, data

                path = data.get(name).get("path")
                size = int(data.get(name).get("size"), 16)
                offset = int(data.get(name).get("offset"), 16)

                # Offset must grate than or equal to current_offset
                if offset < current_offset:
                    err_msg = "[{0:s}] offset: 0x{1:x} invalid, current offset: 0x{2:x}".\
                        format(name, offset, current_offset)
                    return False, err_msg

                # Check file path is exist
                if not os.path.isfile(path):
                    err_msg = "[{0:s}]: {1:s} is not exist!".format(name, path)
                    return False, err_msg

                # Check file size
                if os.path.getsize(path) > size:
                    err_msg = "[{0:s}]: {1:s} is to large, actual size: 0x{2:x}, reserved size: 0x{3:x}".\
                        format(name, path, os.path.getsize(path), size)
                    return False, err_msg

                # Update current offset
                current_offset = offset + size

                # Debug message output
                if verbose:
                    print "File:{0:s}\toffset:0x{1:x}\treserved size\t0x{2:x}".format(name, offset, size)

        except ValueError, e:

            err_msg = e
            return False, err_msg

        finally:

            if len(err_msg):
                print err_msg

        return True, ""

    @staticmethod
    def make_firmware(setting, output, verbose=True):
        """Firmware make

        :param setting: settings
        :param output:firmware output file name
        :param verbose: debug output options
        :return:
        """
        try:

            if not os.path.isdir(FirmwareMaker.DEF_OUTPUT_PATH):
                os.makedirs(FirmwareMaker.DEF_OUTPUT_PATH)

            with open(output, "wb") as fw:
                for data in setting:
                    name = data.keys()[0]
                    path = data.get(name).get("path")
                    size = os.path.getsize(path)
                    offset = int(data.get(name).get("offset"), 16)

                    # Set offset
                    fw.seek(offset, os.SEEK_SET)
                    fw.write(open(path, "rb").read())

                    # Debug output
                    if verbose:
                        print "Write:{0:s}(0x{1:x}) to {2:s} offset: 0x{3:x}".\
                            format(name, size, os.path.basename(output), offset)

        except(IOError, ValueError, OSError), e:

            print "Maker firmware error:", e
            return False

        return True
