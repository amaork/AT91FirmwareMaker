import os
import sys
import getopt
from fwmaker import FirmwareMaker


def usage():
    print "\n{0:s}\n".format(os.path.basename(sys.argv[0]))
    print "\t-h\tshow this help menu"
    print "\t-v\toutput verbose message"
    print "\t-o\tspecify output file name, otherwise using default name:{0:s}".format(FirmwareMaker.DEF_OUTPUT_FILE)
    print "\t-c\tspecify settings file, otherwise using default settings:{0:s}".format(FirmwareMaker.DEF_SETTING_PATH)
    print "\t-e\tgenerate essential settings include {0:s}".format(FirmwareMaker.ESSENTIAL_FILE_LIST)
    print "\t-d\tgenerate default settings include {0:s}".format(FirmwareMaker.DEFAULT_FILE_LIST)


if __name__ == '__main__':

    try:

        # Default args setting
        verbose = False
        conf = FirmwareMaker.DEF_SETTING_PATH
        output = FirmwareMaker.DEF_OUTPUT_FILE

        # Resolve arguments
        opts, args = getopt.getopt(sys.argv[1:], "ho:c:edv", ["help", "output=", "conf=",
                                                              "essential", "default", "verbose"])
        # print opts

        for option, argument in opts:
            if option in ("-h", "--help"):
                usage()
                sys.exit()
            elif option in ("-o", "--output") and len(argument):
                output = argument
            elif option in ("-c", "--conf") and len(argument):
                if os.path.isfile(argument):
                    conf = argument
                else:
                    print "Configure file:{0:s} is not exist!".format(argument)
                    sys.exit()
            elif option in ("-e", "--essential"):
                FirmwareMaker.generate_def_configure(FirmwareMaker.ESSENTIAL_FILE_LIST)
                sys.exit()
            elif option in ("-d", "--default"):
                FirmwareMaker.generate_def_configure(FirmwareMaker.DEFAULT_FILE_LIST)
                sys.exit()
            elif option in ("-v", "--verbose"):
                verbose = True
            else:
                usage()
                sys.exit()

        if verbose:
            print "Settings:\t", conf
            print "Firmware:\t", output

        # Load setting
        ret, settings = FirmwareMaker.load_configure(conf)
        if not ret:
            print "Load settings file:{0:s} error!".format(conf)
            sys.exit()

        # Check setting
        ret, err = FirmwareMaker.check_configure(settings, verbose)
        if not ret:
            print "Invalid settings:{0:s}".format(conf)
            sys.exit()

        # Make firmware
        ret, err_or_md5 = FirmwareMaker.make_firmware(settings, output, verbose)
        if not ret:
            print "Generate firmware error:{0:s}".format(err_or_md5)
            sys.exit()

        print "Success, {0:s} ===> {1:s}, md5: {2:s}".format(conf, output, err_or_md5)

    except getopt.GetoptError, error:

        print "Error:", error
        usage()
        sys.exit(0)
