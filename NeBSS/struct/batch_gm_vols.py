import os
import sys
from shutil import copyfile
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import fast_thresh


def get_volumes(outputs_dir):
    volume_file = os.path.join(outputs_dir, 'Albert_GM_Volumes.csv')
    with open(volume_file, 'rb') as f:
        header = f.readline()
        volumes = f.readline()
    return header, volumes


if __name__ == "__main__":
    """
    Takes as input:
        1) a CSV file listing subject ID and path to Outputs Directory
    -- Assumes that the csv file has a header row
        2) Path to folder for saving images and aggregate file

    """
    output_dir_list = os.path.abspath(sys.argv[1])
    save_dir = os.path.abspath(sys.argv[2])
    save_csv = os.path.join(save_dir, 'GM_Volumes.csv')
    with open(output_dir_list, 'rb') as f:
        f.readline()
        subjects = f.readlines()

    volumes = []

    for line in subjects:
        line = line.strip('\n').split(',')
        sid, path = line[0], line[1]
        fast_thresh.main(path)
        volume_data = get_volumes(path)
        volumes.append("{0}, {1}".format(sid, volume_data[1]))
        image = os.path.join(path, "Albert_GM_Volumes.png")
        image_out = os.path.join(save_dir, sid+".png")
        copyfile(image, image_out)
    # append header
    volumes.insert(0, "PID,"+volume_data[0])

    with open(save_csv, 'wb') as f:
        for line in volumes:
            f.write(line)
