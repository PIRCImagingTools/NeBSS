from __future__ import unicode_literals
import os, shlex, subprocess, json, sys, re
"""
Usage:
    add to bash config:
        alias NeBSS_cl="python /path/to/NeBSS/NeBSS_cl.py"

    Run with:
        NeBSS_cl /path/to/config.json

"""

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
        print "No __file__ variable"
        print "Problem with installation?"
        sys.exit()


def LoadConfig(config_file):
        if os.path.isfile(config_file):
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
                return config
        else:
            print("Config file not found")

def Segment(config):
    config = LoadConfig(config_file)
    local_path = determine_path()
    parent =  config["parent_dir"]
    env = os.environ.copy()
    env['nebss_config'] = config_file
    # If we ever decide to run test parameters from command line
    # change this part.
    env['nebss_test'] = "False"

    try:
        if 'T2_struct' in config and config['T2_struct'] != "":
            reg = os.path.abspath(local_path+'/NeBSS/struct/segment_T2.py')
            contrast='T2'
        elif 'T1_struct' in config and config['T1_struct'] != "":
            reg = os.path.abspath(local_path+'/NeBSS/struct/segment_T1.py')
            contrast='T1'

    
        cmd = 'python '+ reg
        task = shlex.split(cmd)
        print(task)
        subprocess.call(task, env=env)
        print ('Finished Running\n Please check:\n' + parent + \
            '/Seg' + contrast + '/Outputs/OutFiles.nii.gz\n'+ \
            'For any registration errors')
    except NameError:
        print("\n\tUnknown which contrast version to run")
        print("\tPlease check config and rerun\n")
    except Exception as e:
        print("Error Occured:\n{}".format(str(e)))

if __name__ == "__main__":

    config_file = os.path.abspath(sys.argv[1])
    Segment(config_file)


