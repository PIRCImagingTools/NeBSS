from threading import Thread
import subprocess,shlex,os

def bet_T1(in_file):
    cmd = 'bet '+in_file+ '.nii '+in_file+'_brain.nii '+\
        '-R -f 0.55 -g 0'
    print cmd
    env = os.environ.copy()
    task = shlex.split(cmd)
    subprocess.call(task, env=env)

def bet_T2(in_file):
    cmd = 'bet '+in_file+ '.nii '+in_file+'_brain.nii '+\
        '-R -f 0.20 -g 0'
    print cmd
    env = os.environ.copy()
    task = shlex.split(cmd)
    subprocess.call(task, env=env)

def main_T1():

    T1_list = ['{0:0>2d}_T1'.format(x+1) for x in range(20)]

    for T1 in T1_list:
        t = Thread(target=bet_T1, args=(T1,))
        t.start()

def main_T2():

    T2_list = ['{0:0>2d}_T2'.format(x+1) for x in range(20)]

    for T2 in T2_list:
        t = Thread(target=bet_T2, args=(T2,))
        t.start()

if __name__ == '__main__':
    main_T1()
    main_T2()
