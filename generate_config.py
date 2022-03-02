import json
import os, sys
from nipype.interfaces.fsl import BET as bet
import nipype.interfaces.fsl.maths as fslmaths
import re
from nipy import load_image
import numpy as np
from os.path import join
import shutil

def generate_config(path, subj_id, subj_pma):
    #setup names
    file_dir, file_base = os.path.split(path)
    data_folder = '/data'

    p = re.compile('\.nii.*')
    m = p.search(file_base)

    contrast = determine_contrast(path)

    file_name = file_base[: m.start()]
    file_suffix = file_base[m.start():]
    out_file = os.path.join(data_folder, file_name + '_bet_' + file_suffix)
    out_file_bin = os.path.join(data_folder, file_name + '__bet_bin__' + file_suffix)
    json_outfile = join(data_folder, subj_id +  '_config.json')


    if (not os.path.isfile(out_file)):
        b = bet()
        b.inputs.in_file = path
        b.inputs.out_file = out_file
        _ = b.run()

    if (not os.path.isfile(out_file_bin)):
        fm = fslmaths.UnaryMaths()
        fm.inputs.in_file = out_file
        fm.inputs.operation = 'bin'
        fm.inputs.out_file = out_file_bin
        _ = fm.run()

    t1_struc = ''
    t1_coord = tuple()
    t2_struc = ''
    t2_coord = tuple()



    if contrast == 'T1':
        t1_struc = join(data_folder,file_base)
        t1_coord = get_coords(out_file_bin)
        t2_struc = ""
        t2_coord = get_coords(t2_struc)
    elif contrast == 'T2': #if contrast == 'Und' guess T2
        t1_struc = ""
        t1_coord = get_coords(t1_struc)
        t2_struc = join(data_folder,file_base)
        t2_coord = get_coords(out_file_bin)

    parent_dir = data_folder
    t1_center = get_centers(t1_coord)
    t2_center = get_centers(t2_coord)
    group = get_albert_group(int(subj_pma))


    config = {
    "FSE": "",
    "T1_center": t1_center,
    "T1_crop_box": t1_coord,
    "T1_struct": t1_struc,
    "T2_center": t2_center,
    "T2_crop_box": t2_coord,
    "T2_struct": t2_struc,
    "albert_group": group,
    "parent_dir": parent_dir,
    "pca": subj_pma,
    "pid": subj_id
    }

    with open(json_outfile, "w") as outfile:
        json.dump(config, outfile, sort_keys = True, indent = 4)

    os.remove(out_file)
    os.remove(out_file_bin)


def determine_contrast(path):
    isT2 = False
    isT1 = False
    p = re.compile('T2', re.I)
    q = re.compile('T1', re.I)
    for i in reversed(path.split('/')):
        try:
            subj_id = p.search(i).group()
            isT2 = True
            break
        except Exception:
            pass
        try:
            subj_id = q.search(i).group()
            isT1 = True
            break
        except Exception:
            pass
    if isT2:
        return 'T2'
    elif isT1:
        return 'T1'
    else:
        #T2 segmenation on NeBSS is fairly good and will work even with T1 
        # marked as T2. 
        return 'T2' 


def get_coords(path=None):
    if path is None or path == "":
        return [0, 0, 0, 0, 0, 0]

    img = load_image(path)
    data = img.get_data()
    max_list = data.shape

    x_arr = np.nonzero(data.sum(axis=2).sum(axis=1))[0]
    y_arr = np.nonzero(data.sum(axis=2).sum(axis=0))[0]
    z_arr = np.nonzero(data.sum(axis=0).sum(axis=0))[0]

    x_min = x_arr[0]
    x_max = x_arr[-1]

    y_min = y_arr[0]
    y_max = y_arr[-1]

    z_min = z_arr[0]
    z_max = z_arr[-1]

    coords = [x_min, x_max, y_min, y_max, z_min, z_max]

    coords = increase_bounding_box(coords, max_list)

    # necessary to convert from np.int64 to python int for convert to json
    for i in range(0, len(coords)):
        coords[i] = int(coords[i])

    return coords


def increase_bounding_box(coords, max_list, pixel_num = 10):
    for index in [0, 2, 4]:
        if coords[index] - pixel_num <= 0:
            coords[index] = 0
        else:
            coords[index] = coords[index] - pixel_num
    
    for index, max_dim in zip([1, 3, 5], max_list):
        if coords[index] + pixel_num >= max_dim:
            coords[index] = max_dim
        else:
            coords[index] = coords[index] + pixel_num

    return coords

def get_centers(coord_list):
    loops = len(coord_list)//2
    centers = []

    for i in range(0, loops):
        a = coord_list[i*2]
        b = coord_list[i*2 + 1]
        c = (a+b)//2
        centers.append(c)

    return centers

def get_albert_group(subj_pma):
    albert_group = ''
    albert_tops = [27, 30, 36, float('inf')]
    albert_groups = ['<27','27-30','30-36','Term']
    for age, group in zip(albert_tops, albert_groups):
        if subj_pma < age:
            albert_group = group
            break
    
    return albert_group



def get_input_type(arg_type, prompt):
    loops = 0
    expected_types = ['str', 'int', 'float']
    types = [str, int, float]
    run = True

    for arg, type_obj in zip(expected_types, types):
        if arg == arg_type:
            while run:
                try:
                    user_input = type_obj(raw_input(prompt))
                    if isinstance(user_input, type_obj):
                        return user_input
                except KeyboardInterrupt:
                    run = False
                except Exception as e:
                    pass
                finally:
                    loops+=1
                if loops > 5:
                    run = False
            break

    if arg_type == 'bool':
        while run:
            try:
                user_input = raw_input(prompt)
                if user_input.lower() == 'true':
                    return True
                elif user_input.lower() == 'false':
                    return False
            except KeyboardInterrupt:
                run = False
            except Exception as e:
                pass
            finally:
                loops+=1
            if loops > 5:
                run = False



if __name__ == '__main__':
    arg_num = len(sys.argv)
    try:
        if arg_num == 2:
            subj_id = get_input_type('str', "Enter name: ")
            subj_pma = get_input_type('float', "Enter PMA: ")
            generate_config(sys.argv[1], subj_id, subj_pma)
        elif arg_num == 4:
            generate_config(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    except:
        pass


"""
            subj_id = raw_input("Enter name: ")
            subj_pma = float(raw_input("Enter PMA: " ))


"""