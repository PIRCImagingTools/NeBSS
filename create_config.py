import os, sys, json


def get_int(input_prompt):
    while True:
        user_input = raw_input(input_prompt)
        try:
            typed = int(user_input)
        except ValueError:
            print("not an integer")
        else:
            return typed
            break


def get_albert_group():
    print("Select Albert group:\n(By Gestational Age)\n\
1: <27\n2: 27-30\n3: 30-36\n4: Term")
    while True:
        user_input = raw_input("Select number from list: ")
        if user_input == "1":
            return "<27"
        elif user_input == "2":
            return "27-30"
        elif user_input == "3":
            return "30-36"
        elif user_input == "4":
            return "Term"
        else:
            print("Not an option")


def yesno(input_prompt):
    while True:
        user_input = raw_input(input_prompt)
        if user_input == "y" or user_input == "Y":
            return True
        elif user_input == "n" or user_input == "N":
            return False
        else:
            print("Please answer Y/N")


def save_dict(dct, filename):
    with open(filename, 'w') as f:
        json.dump(dct, f, sort_keys=True, ensure_ascii=False,
                  indent=4, separators=(',', ': '))


if __name__ == "__main__":
    infile = sys.argv[1]
    if not os.path.isfile(os.path.abspath(infile)):
        print("File: {0} does not exist. Are you in the correct directory?".format(
        infile))
    else:
        out_config = {}
        print("Creating config file for input image:\n{0}".format(infile))
        out_config["pid"] = raw_input("PID: ")
        if yesno("T2 Weighted? (Y/N): "):
            print("Configuring for T2 image")
            out_config["T2_struct"] = "/data/"+infile
            T2_x0 = get_int("T2 Crop X0: ")
            T2_x1 = get_int("T2 Crop X1: ")
            T2_y0 = get_int("T2 Crop Y0: ")
            T2_y1 = get_int("T2 Crop Y1: ")
            T2_z0 = get_int("T2 Crop Z0: ")
            T2_z1 = get_int("T2 Crop Z1: ")
            out_config["T2_crop_box"] = [T2_x0, T2_x1,
                                         T2_y0, T2_y1,
                                         T2_z0, T2_z1]
            T2_center_x = get_int("T2 Image Center (X): ")
            T2_center_y = get_int("T2 Image Center (Y): ")
            T2_center_z = get_int("T2 Image Center (Z): ")
            out_config["T2_center"] = [T2_center_x,
                                       T2_center_y,
                                       T2_center_z]
        else:
            print("Configuring for T1 image")
            out_config["T1_struct"] = "/data/"+infile
            T1_x0 = get_int("T1 Crop X0: ")
            T1_x1 = get_int("T1 Crop X1: ")
            T1_y0 = get_int("T1 Crop Y0: ")
            T1_y1 = get_int("T1 Crop Y1: ")
            T1_z0 = get_int("T1 Crop Z0: ")
            T1_z1 = get_int("T1 Crop Z1: ")
            out_config["T1_crop_box"] = [T1_x0, T1_x1,
                                         T1_y0, T1_y1,
                                         T1_z0, T1_z1]
            T1_center_x = get_int("T1 Image Center (X): ")
            T1_center_y = get_int("T1 Image Center (Y): ")
            T1_center_z = get_int("T1 Image Center (Z): ")
            out_config["T1_center"] = [T1_center_x,
                                       T1_center_y,
                                       T1_center_z]

        out_config["albert_group"] = get_albert_group()
        out_config["parent_dir"] = "/data"
        out_config["pca"] = str(get_int("PCA (integer): "))
        outfile = out_config["pid"]+"_config.json"
        if os.path.isfile(outfile):
            if yesno("Config file already exists. Overwrite? (y/n): "):
                save_dict(out_config, outfile)
            else:
                new_filename = raw_input("Give new file name: ")
                save_dict(out_config, new_filename+"_config.json")
        else:
            save_dict(out_config, outfile)


