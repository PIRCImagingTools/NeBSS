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
    except NameError:
        print("No __file__ variable")
        print("Problem with installation?")
        sys.exit()


def get_albert_labels():
    local_path = determine_path()
    albert_labels = os.path.join(local_path,
                                 "../../ALBERT_Labels.txt")
    with open(albert_labels, 'rb') as f:
        f.readline()
        labels = f.readlines()

    label_dict = {}
    for line in labels:
        line = line.strip('\n').split('\t')
        label_dict[line[0]] = line[-1]
    return label_dict


def get_albert_colors():
    local_path = determine_path()
    albert_labels = os.path.join(local_path,
                                 "../../ALBERT_Labels.txt")
    with open(albert_labels, 'rb') as f:
        f.readline()
        labels = f.readlines()

    color_list = []
    for line in labels:
        line = line.strip('\n').split('\t')
        color_list.append((float(line[1])/255,
                           float(line[2])/255,
                           float(line[3])/255))
    return color_list
