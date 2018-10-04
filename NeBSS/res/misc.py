import os
import sys


def determine_path():
    """
    determines the local path of the module on the OS
    """
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        print("No __file__ variable")
        print("Problem with installation?")
        sys.exit()


def get_albert_labels():
    local_path = determine_path()
    albert_labels = os.path.join(local_path,
                                 "../../ALBERT_Labels.txt")
    return albert_labels

