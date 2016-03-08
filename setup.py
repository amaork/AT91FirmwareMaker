from distutils.core import setup
import py2exe
import os

# Get git version and release date
sub_version = int(os.popen("git log --pretty=format:'' | wc -l", 'r').read())
release_date = os.popen('git log -1 --pretty=format:'
                        '"%ad" --date=iso | tr -d - | tr -d : | tr " " "-" | cut -c 3-15').read().strip()


def get_file_list(path):
    """Get path directory all file list

    :param path:
    :return: file list
    """

    flist = []

    if os.path.isdir(path):
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)

            if os.path.isdir(full_path):
                continue

            flist.append(os.path.join(path, filename))

    return flist


setup(
    zipfile=None,
    console=[{"script": "firmwareMaker.py"}],

    options={
        "py2exe": {"includes": ["sip"],
                   "dll_excludes": ["MSVCP90.dll", "w9xpopen.exe"],
                   "bundle_files": 1, "compressed": 1, "optimize": 2}
    },

    data_files=[("example", get_file_list("example")), ],

    name="AT91 Firmware Maker",
    description="ATMEL SOC Firmware Maker tools",
    version="%.1f" % (sub_version / 10.0),
    author="amaork"
)
