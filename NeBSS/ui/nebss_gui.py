#!/bin/python
import os
import json
import shlex
import subprocess
import sys
try:
    import wx
#    import wxPython.lib.scrolledpanel as scrolled
except ImportError:
    raise ImportError,"wxPython module is required."

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

local_path = determine_path()

class Top_Panel(wx.Panel):

    def __init__(self,parent):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.frame = parent

        box = wx.StaticBox(self, -1, "NeBSS")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizer = wx.GridBagSizer(2, 2)

#------------------------------------------------------------------------#
        narrow_sizer = wx.GridBagSizer(2,2)

        pid_label = wx.StaticText(self, -1, label=u"PID")
        self.pid_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)

        narrow_sizer.Add(pid_label, (0,0), (1,1),
                        wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        narrow_sizer.Add(self.pid_field,(0,1),(1,1),
                        wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        pca_label = wx.StaticText(self, -1, label=u"PCA (Weeks)")
        self.pca_field = wx.TextCtrl(self, -1, value="",
                                        style=wx.TE_PROCESS_ENTER)

        narrow_sizer.Add(pca_label, (0,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        narrow_sizer.Add(self.pca_field, (0,3), (1,1),
                        wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        albert_groups = ['<27','27-30','30-36','Term']

        albert_group_label = wx.StaticText(self, -1, label=u"Albert Group (GA)")
        self.albert_group_field = wx.ComboBox(self, choices=albert_groups,
                                              style=wx.CB_READONLY)


        narrow_sizer.Add(albert_group_label,(0,4), (1,1),
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        narrow_sizer.Add(self.albert_group_field, (0,5), (1,1),
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        box_sizer.Add(narrow_sizer,0, wx.ALIGN_CENTER_HORIZONTAL, 0)


#------------------------------------------------------------------------#
        parent_dir_label = wx.StaticText(self, -1, label =u"Parent Dir")
        self.parent_dir_field = wx.TextCtrl(self, -1, value="",
                                                 style=wx.TE_PROCESS_ENTER)
        parent_dir_button = wx.Button(self, -1, label=u"...")
        sizer.Add(parent_dir_label, (1,0), (1,1),
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,5)
        sizer.Add(self.parent_dir_field, (1,1), (1,1),
                                             wx.EXPAND|wx.ALIGN_LEFT,0)
        sizer.Add(parent_dir_button, (1,2), (1,1),
                    wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        self.Bind(wx.EVT_BUTTON, self.OnParDirButtonClick, parent_dir_button)

#---------------------------------------------------------------------------#
        T1_label = wx.StaticText(self, -1, label =u"Struct T1")
        sizer.Add(T1_label, (2,0), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        self.T1_field = wx.TextCtrl(self, -1, value="",
                                    style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.T1_field, (2,1), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        T1_button = wx.Button(self, -1, label=u"...")
        sizer.Add(T1_button, (2,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        self.Bind(wx.EVT_BUTTON, self.OnT1ButtonClick, T1_button)

        T1_crop_label= wx.StaticText(self, -1, label=u"T1 Crop Box")
        sizer.Add(T1_crop_label, (3,1), (1,1),
                                             wx.EXPAND|wx.ALIGN_LEFT,0)

        T1_crop_x1_label = wx.StaticText(self, -1, label=u"X\u2081 ")
        self.T1_crop_x1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T1_crop_x2_label = wx.StaticText(self, -1, label=u"X\u2082 ")
        self.T1_crop_x2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)

        T1_crop_y1_label = wx.StaticText(self, -1, label=u" Y\u2081 ")
        self.T1_crop_y1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T1_crop_y2_label = wx.StaticText(self, -1, label=u" Y\u2082 ")
        self.T1_crop_y2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)

        T1_crop_z1_label = wx.StaticText(self, -1, label=u" Z\u2081 ")
        self.T1_crop_z1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T1_crop_z2_label = wx.StaticText(self, -1, label=u" Z\u2082 ")
        self.T1_crop_z2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)


        coord_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        coord_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)

        coord_sizer_1.Add(T1_crop_x1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_1.Add(self.T1_crop_x1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_2.Add(T1_crop_x2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_2.Add(self.T1_crop_x2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_1.Add(T1_crop_y1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_1.Add(self.T1_crop_y1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_2.Add(T1_crop_y2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_2.Add(self.T1_crop_y2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_1.Add(T1_crop_z1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_1.Add(self.T1_crop_z1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_2.Add(T1_crop_z2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_2.Add(self.T1_crop_z2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)


        sizer.Add(coord_sizer_1, (4,1), (1,1),
                                           wx.ALIGN_CENTER_VERTICAL,0)
        sizer.Add(coord_sizer_2, (5,1), (1,1),
                                           wx.ALIGN_CENTER_VERTICAL,0)

#---------------------------------------------------------------------------#
        T2_label = wx.StaticText(self, -1, label =u"Struct T2")
        sizer.Add(T2_label, (6,0), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        self.T2_field = wx.TextCtrl(self, -1, value="",
                                    style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.T2_field, (6,1), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        T2_button = wx.Button(self, -1, label=u"...")
        sizer.Add(T2_button, (6,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        self.Bind(wx.EVT_BUTTON, self.OnT2ButtonClick, T2_button)

        T2_crop_label= wx.StaticText(self, -1, label=u"T2 Crop Box")
        sizer.Add(T2_crop_label, (7,1), (1,1),
                                             wx.EXPAND|wx.ALIGN_LEFT,0)

        T2_crop_x1_label = wx.StaticText(self, -1, label=u"X\u2081 ")
        self.T2_crop_x1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T2_crop_x2_label = wx.StaticText(self, -1, label=u"X\u2082 ")
        self.T2_crop_x2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)

        T2_crop_y1_label = wx.StaticText(self, -1, label=u" Y\u2081 ")
        self.T2_crop_y1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T2_crop_y2_label = wx.StaticText(self, -1, label=u" Y\u2082 ")
        self.T2_crop_y2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)

        T2_crop_z1_label = wx.StaticText(self, -1, label=u" Z\u2081 ")
        self.T2_crop_z1_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)
        T2_crop_z2_label = wx.StaticText(self, -1, label=u" Z\u2082 ")
        self.T2_crop_z2_field = wx.TextCtrl(self, -1, value="",
                                                    style=wx.TE_PROCESS_ENTER)


        coord_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        coord_sizer_4 = wx.BoxSizer(wx.HORIZONTAL)

        coord_sizer_3.Add(T2_crop_x1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_3.Add(self.T2_crop_x1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_4.Add(T2_crop_x2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_4.Add(self.T2_crop_x2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_3.Add(T2_crop_y1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_3.Add(self.T2_crop_y1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_4.Add(T2_crop_y2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_4.Add(self.T2_crop_y2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_3.Add(T2_crop_z1_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_3.Add(self.T2_crop_z1_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)

        coord_sizer_4.Add(T2_crop_z2_label,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)
        coord_sizer_4.Add(self.T2_crop_z2_field,0,
                         wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,5)


        sizer.Add(coord_sizer_3, (8,1), (1,1),
                                           wx.ALIGN_CENTER_VERTICAL,0)
        sizer.Add(coord_sizer_4, (9,1), (1,1),
                                           wx.ALIGN_CENTER_VERTICAL,0)
        FSE_label = wx.StaticText(self, -1, label =u"T2 FSE")
        sizer.Add(FSE_label, (10,0), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        self.FSE_field = wx.TextCtrl(self, -1, value="",
                                    style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.FSE_field, (10,1), (1,1), wx.EXPAND|wx.ALIGN_LEFT,0)

        FSE_button = wx.Button(self, -1, label=u"...")
        sizer.Add(FSE_button, (10,2), (1,1),
                       wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,0)
        self.Bind(wx.EVT_BUTTON, self.OnFSEButtonClick, FSE_button)

        sizer.AddGrowableCol(1)
        box_sizer.Add(sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        self.SetSizer(box_sizer)


    def OnParDirButtonClick(self, event):
            dir_picker = wx.DirDialog(self,
                    u"Choose dir", self.frame.default_dir)
            if dir_picker.ShowModal() == wx.ID_OK:
                self.parent_dir_field.SetValue(dir_picker.GetPath())
                self.parent_dir_field.SetFocus()
                self.frame.default_dir = dir_picker.GetPath()
            dir_picker.Destroy()

    def OnT1ButtonClick(self, event):
            wildcard = "NIFTI image {*.nii*}|*.nii*|"\
                              "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose T1 Struct", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
                self.T1_field.SetValue(file_picker.GetPath())
                self.T1_field.SetFocus()
            file_picker.Destroy()

    def OnFSEButtonClick(self, event):
            wildcard = "NIFTI image {*.nii*}|*.nii*|"\
                              "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose FSE", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
                self.FSE_field.SetValue(file_picker.GetPath())
                self.FSE_field.SetFocus()
            file_picker.Destroy()

    def OnT2ButtonClick(self, event):
            wildcard = "NIFTI image {*.nii*}|*.nii*|"\
                              "All files {*.*}|*.*"
            file_picker = wx.FileDialog(self, "Choose T2 Struct", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
            if file_picker.ShowModal() == wx.ID_OK:
                self.T2_field.SetValue(file_picker.GetPath())
                self.T2_field.SetFocus()
            file_picker.Destroy()




class Control_Panel(wx.Panel):

    def __init__(self,parent,top_panel):
        wx.Panel.__init__(self,parent,style=wx.NO_BORDER)
        self.frame = parent
        self.top = top_panel

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.load = wx.Button(self,  label=u"Load Config")
        self.save = wx.Button(self,  label=u"Save Config")

        buttons_sizer.Add(self.load, 1, wx.ALIGN_RIGHT, 5)
        buttons_sizer.Add(self.save, 1, wx.ALIGN_RIGHT, 5)

        self.Bind(wx.EVT_BUTTON, self.OnLoad, self.load)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)

        self.SetSizerAndFit(buttons_sizer)

    def OnLoad(self, event):
        wildcard = "Config file {*.json}|*.json|"\
                       "All files {*.*}|*.*"
        file_picker = wx.FileDialog(self, "Choose file", self.frame.default_dir,
                                                "", wildcard, wx.FD_OPEN)
        if file_picker.ShowModal() == wx.ID_OK:
            config_file = file_picker.GetPath()
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
            self.top.pid_field.SetValue(config['pid'])
            self.top.pca_field.SetValue(config['pca'])
            self.top.parent_dir_field.SetValue(config['parent_dir'])
            self.top.albert_group_field.SetValue(str(config['albert_group']))
            self.top.T1_field.SetValue(config['T1_struct'])
            self.top.FSE_field.SetValue(config['FSE'])
            self.top.T2_field.SetValue(config['T2_struct'])
            self.top.T1_crop_x1_field.SetValue(str(config['T1_crop_box'][0]))
            self.top.T1_crop_x2_field.SetValue(str(config['T1_crop_box'][1]))
            self.top.T1_crop_y1_field.SetValue(str(config['T1_crop_box'][2]))
            self.top.T1_crop_y2_field.SetValue(str(config['T1_crop_box'][3]))
            self.top.T1_crop_z1_field.SetValue(str(config['T1_crop_box'][4]))
            self.top.T1_crop_z2_field.SetValue(str(config['T1_crop_box'][5]))
            self.top.T2_crop_x1_field.SetValue(str(config['T2_crop_box'][0]))
            self.top.T2_crop_x2_field.SetValue(str(config['T2_crop_box'][1]))
            self.top.T2_crop_y1_field.SetValue(str(config['T2_crop_box'][2]))
            self.top.T2_crop_y2_field.SetValue(str(config['T2_crop_box'][3]))
            self.top.T2_crop_z1_field.SetValue(str(config['T2_crop_box'][4]))
            self.top.T2_crop_z2_field.SetValue(str(config['T2_crop_box'][5]))

        file_picker.Destroy()


    def OnSave(self, event):
        config = {}
        pid = self.top.pid_field.GetValue()
        pca = self.top.pca_field.GetValue()
        parent_dir = self.top.parent_dir_field.GetValue()
        albert_group = self.top.albert_group_field.GetValue()
        T1_struct = self.top.T1_field.GetValue()
        T1_crop_box = [self.top.T1_crop_x1_field.GetValue(),
                       self.top.T1_crop_x2_field.GetValue(),
                       self.top.T1_crop_y1_field.GetValue(),
                       self.top.T1_crop_y2_field.GetValue(),
                       self.top.T1_crop_z1_field.GetValue(),
                       self.top.T1_crop_z2_field.GetValue()]
        T1_crop_box = [int(x) if x else 0 for x in T1_crop_box]

        T1x = (T1_crop_box[1] - T1_crop_box[0])/2
        T1y = (T1_crop_box[3] - T1_crop_box[2])/2
        T1z = (T1_crop_box[5] - T1_crop_box[4])/2
        T1_center = [T1x, T1y, T1z]
        FSE = self.top.FSE_field.GetValue()
        T2_struct = self.top.T2_field.GetValue()
        T2_crop_box = [self.top.T2_crop_x1_field.GetValue(),
                       self.top.T2_crop_x2_field.GetValue(),
                       self.top.T2_crop_y1_field.GetValue(),
                       self.top.T2_crop_y2_field.GetValue(),
                       self.top.T2_crop_z1_field.GetValue(),
                       self.top.T2_crop_z2_field.GetValue()]
        T2_crop_box = [int(x) if x else 0 for x in T2_crop_box]

        T2x = (T2_crop_box[1] - T2_crop_box[0])/2
        T2y = (T2_crop_box[3] - T2_crop_box[2])/2
        T2z = (T2_crop_box[5] - T2_crop_box[4])/2
        T2_center = [T2x, T2y, T2z]


        if os.path.isdir(parent_dir):
            config['pid'] = pid
            config['pca'] = pca
            config['parent_dir'] = parent_dir
            config['albert_group'] = albert_group
            config['T1_struct'] = T1_struct
            config['T2_struct'] = T2_struct
            config['FSE'] = FSE
            config['T1_crop_box'] = T1_crop_box
            config['T2_crop_box'] = T2_crop_box
            config['T1_center'] = T1_center
            config['T2_center'] = T2_center


            if os.path.isfile(parent_dir+'/'+pid+'_config.json'):

                file_overwrite = wx.MessageDialog(self, "Overwrite Config?",
                                                "Config File Exists",  wx.YES_NO)
                if file_overwrite.ShowModal() == wx.ID_YES:
                    with open(parent_dir+'/'+pid+'_config.json', 'w') as f:
                        json.dump(config, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))
            else:
                with open(parent_dir+'/'+pid+'_config.json', 'w') as f:
                        json.dump(config, f,sort_keys=True,ensure_ascii=False,
                                           indent=4,separators=(',',': '))


        else:
            print "Parent directory does not exist!"


class Run_Buttons(wx.Panel):
    def __init__(self,parent, top):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.frame = parent
        self.top = top
        self.isTest = False

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.seg_T1 = wx.Button(self,  label=u"Seg T1")
        sizer.Add(self.seg_T1, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnSegT1, self.seg_T1)

        self.FSEreg = wx.Button(self,  label=u"Reg FSE")
        sizer.Add(self.FSEreg, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnReg, self.FSEreg)

        self.seg_T2 = wx.Button(self,  label=u"Seg T2")
        sizer.Add(self.seg_T2, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnSegT2, self.seg_T2)

        self.view = wx.Button(self,  label=u"View")
        sizer.Add(self.view, 0, wx.CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnView, self.view)

        self.checkBox = wx.CheckBox(self, label=u'Test', pos = (0,0))
        sizer.Add(self.checkBox, 0, wx.CENTER|wx.ALL,5)
        self.Bind(wx.EVT_CHECKBOX, self.whenChecked)

        self.SetSizerAndFit(sizer)

    def whenChecked(self, e):
        cb = e.GetEventObject()
        isTest = cb.GetValue()
        self.isTest = isTest

    def printTest():
        print self.isTest  

    def OnSegT1(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        config_file = parent+'/'+pid+'_config.json'
        if os.path.isfile(config_file):
            env = os.environ.copy()
            env['nebss_config'] = config_file
            env['nebss_test'] = str(self.isTest)
            reg = os.path.abspath(local_path+'/../struct/segment_T1.py')
            cmd = 'ipython '+ reg
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
            print "Segmentation done!\n"+\
            'Please check:\n'+\
            parent + '/SegT1/Outputs/OutFiles.nii.gz\n'+\
            'For any registration errors'
        else:
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'

    def OnReg(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()
        T1 = self.top.T1_field.GetValue()
        FSE = self.top.FSE_field.GetValue()
        out = parent+'/FSEregT1.nii.gz'
        omat = parent+'/FSEregT1.mat'
        env = os.environ.copy()
        cmd = 'flirt -in '+ FSE +' -ref '+ T1 +\
            ' -out '+ out + ' -omat ' + omat +\
            ' -bins 256 -cost corratio -searchrx -90 90 -searchry -90 -90'+\
            ' -searchrz -90 -90 -dof 6 -interp trilinear'
        print cmd
        task = shlex.split(cmd)
        subprocess.call(task, env=env)
        print "FSE to T1 reg done"

    def OnSegT2(self, event):
        parent = self.top.parent_dir_field.GetValue()
        pid = self.top.pid_field.GetValue()	
        config_file = parent+'/'+pid+'_config.json'
        print config_file
        if os.path.isfile(config_file):
            env = os.environ.copy()
            env['nebss_config'] = config_file
            env['nebss_test'] = str(self.isTest)
            reg = os.path.abspath(local_path+'/../struct/segment_T2.py')
            cmd = 'ipython '+ reg
            task = shlex.split(cmd)
            subprocess.call(task, env=env)
            print "Segmentation done!\n"+\
            'Please check:\n'+\
            parent + '/SegT2/Outputs/OutFiles.nii.gz\n'+\
            'For any registration errors'
        else:
            print 'config file: \n'+\
                     config_file+\
                     '\n Not Found!'

    def OnView(self, event):

        cmd = 'fslview'
        env = os.environ.copy()
        task = shlex.split(cmd)
        subprocess.call(task, env=env)



class SplashScreen(wx.SplashScreen):
    def __init__(self, parent=None):
        splash_bit = wx.Image(name=local_path+'/Splash.png').ConvertToBitmap()
        splash_style = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splash_duration = 1500
        wx.SplashScreen.__init__(self, splash_bit, splash_style,
                                 splash_duration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, evt):
        self.Hide()
        frame = fDM_Frame()
        frame.Show(True)
        evt.Skip()

class fDM_Frame(wx.Frame):

   def __init__(self):
        wx.Frame.__init__(self, parent=None, title="NeBSS GUI")
        self.default_dir = os.path.expanduser("~")
        self.frame_sizer = wx.GridBagSizer(5,5)

        top = Top_Panel(self)
        controls = Control_Panel(self, top)
        run_buttons = Run_Buttons(self, top)

        self.frame_sizer.Add(top,(0,0),wx.DefaultSpan,
                             wx.ALL|wx.EXPAND,5)
        self.frame_sizer.Add(controls, (1,0), wx.DefaultSpan,
                           wx.ALL|wx.EXPAND,5)
        self.frame_sizer.Add(run_buttons,(0,1),(3,1),
                             wx.ALL|wx.EXPAND,5)

        self.frame_sizer.AddGrowableCol(0)
        self.frame_sizer.AddGrowableRow(2)

        self.SetSizerAndFit(self.frame_sizer)
        self.Show()


def start():
    app = wx.App(False)
    frame = SplashScreen()
    app.MainLoop()


if __name__ ==  "__main__":
    start()
