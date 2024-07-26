#Thorium Control Interface
#Author: Richard Mattish
#Last Updated: 07/26/2024


#Function:  This program provides a graphical user interface for setting
#           and monitoring trap electrode voltages for the Thorium Project


#Import General Tools
import os
import platform
import time
import webbrowser
import threading

#from twisted.internet import reactor, tksupport
#from twisted.internet.defer import inlineCallbacks

#Import GUI Tools
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image

#Import Math Tools
import numpy as np

#Defines location of the Desktop as well as font and text size for use in the software
desktop = os.path.expanduser("~\Desktop")
desktop = desktop.replace(os.sep, '/')
font_12 = ('Helvetica', 12)
font_14 = ('Helvetica', 14)
font_16 = ('Helvetica', 16)
font_18 = ('Helvetica', 18)
font_20 = ('Helvetica', 20)


class mySpinbox(Spinbox):
    def __init__(self, *args, **kwargs):
        Spinbox.__init__(self, *args, **kwargs)
        self.bind('<MouseWheel>', self.mouseWheel)
        self.bind('<Button-4>', self.mouseWheel)
        self.bind('<Button-5>', self.mouseWheel)

    def mouseWheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.invoke('buttondown')
        elif event.num == 4 or event.delta == 120:
            self.invoke('buttonup')

#Opens a url in a new tab in the default webbrowser
def callback(url):
    webbrowser.open_new_tab(url)

#Sorts all columns of a matrix by a single column
def orderMatrix(matrix, column):
    i = 0
    a = len(matrix)
    orderedMatrix = []
    while i < len(matrix):
        j = 0
        smallest = True
        while j < len(matrix) and smallest == True:
            if matrix[i][column] <= matrix[j][column]:
                smallest = True
                j = j + 1
            else:
                smallest = False
        if smallest == True:
            orderedMatrix.append(matrix.pop(i))
            i = 0
        else:
            i = i + 1
    return orderedMatrix

#Enables multi-threading so that function will not freeze main GUI
def multiThreading(function):
    t1=threading.Thread(target=function)
    t1.setDaemon(True)      #This is so the thread will terminate when the main program is terminated
    t1.start()


#This is the EBIT class object, which contains everything related to the GUI control interface
class Thorium:
    def __init__(self, reactor=None):

        #Dictionary which will store actual voltages of bender electrodes, as read from server
        #All voltages are initialized as zero upon program start, but will be read by data reader
        self.actual_voltages = {'U_TR_bender':0, 
                           'U_TL_bender':0, 
                           'U_BL_bender':0, 
                           'U_BR_bender':0, 
                           'U_TL_plate':0,
                           'U_TR_plate':0, 
                           'U_BL_plate':0, 
                           'U_BR_plate':0, 
                           'U_L_ablation':0, 
                           'U_R_ablation':0,        #This is the last line which contains a quadrupole bender electrode
                           'U_TR1_loading':0,       #This is the first line which contains a loading trap electrode
                           'U_TL1_loading':0,
                           'U_BL1_loading':0,
                           'U_BR1_loading':0,
                           'U_TR2_loading':0,
                           'U_TL2_loading':0,
                           'U_BL2_loading':0,
                           'U_BR2_loading':0,
                           'U_TR3_loading':0,
                           'U_TL3_loading':0,
                           'U_BL3_loading':0,
                           'U_BR3_loading':0,
                           'U_TR4_loading':0,
                           'U_TL4_loading':0,
                           'U_BL4_loading':0,
                           'U_BR4_loading':0,
                           'U_TR5_loading':0,
                           'U_TL5_loading':0,
                           'U_BL5_loading':0,
                           'U_BR5_loading':0,
                           'U_exit_bender':0,
                           'U_exit_loading':0}
        

        #Dictionary which will store set voltages of bender electrodes, as specified by user in program
        #All set voltages are initialized as zero upon program start
        self.set_voltages = self.actual_voltages.copy()

        #Dictionary which will store voltages that user has typed into entry boxes
        #These are not necessarily the same as set voltages, since power buttons, etc. may be switched
        self.entry_voltages = self.actual_voltages.copy()

        #Location (server, channel) of electrode voltages on power supplies
        self.v_location = {'U_TR_bender':('b', 11), 
                           'U_TL_bender':('b', 12), 
                           'U_BL_bender':('b', 13), 
                           'U_BR_bender':('b', 14), 
                           'U_TL_plate':('b', 7),
                           'U_TR_plate':('b', 10), 
                           'U_BL_plate':('b', 6), 
                           'U_BR_plate':('b', 9), 
                           'U_L_ablation':('b', 5), 
                           'U_R_ablation':('b', 8),        #This is the last line which contains a quadrupole bender electrode
                           'U_TR1_loading':('l', 10),      #This is the first line which contains a loading trap electrode
                           'U_TL1_loading':('l', 5),
                           'U_BL1_loading':('l', 15),
                           'U_BR1_loading':('b', 4),
                           'U_TR2_loading':('l', 9),
                           'U_TL2_loading':('l', 4),
                           'U_BL2_loading':('l', 14),
                           'U_BR2_loading':('b', 3),
                           'U_TR3_loading':('l', 8),
                           'U_TL3_loading':('l', 3),
                           'U_BL3_loading':('l', 13),
                           'U_BR3_loading':('b', 2),
                           'U_TR4_loading':('l', 7),
                           'U_TL4_loading':('l', 2),
                           'U_BL4_loading':('l', 12),
                           'U_BR4_loading':('b', 1),
                           'U_TR5_loading':('l', 6),
                           'U_TL5_loading':('l', 1),
                           'U_BL5_loading':('l', 11),
                           'U_BR5_loading':('l', 16),
                           'U_exit_bender':('b', 15),
                           'U_exit_loading':('l', 20)}
        

        
        self.U_bender = 0
        self.U_segment_1 = 0
        self.U_segment_2 = 0
        self.U_segment_3 = 0
        self.U_segment_4 = 0
        self.U_segment_5 = 0

        self.dU_segment_1 = 0
        self.dU_segment_2 = 0
        self.dU_segment_3 = 0
        self.dU_segment_4 = 0
        self.dU_segment_5 = 0
        
        self.reactor = reactor

        #Defines global variables
        self.canvas = None
        self.fig = None
        self.ax = None
        self.toolbar = None
        self.filename = None
        self.work_dir = None

        #Boolean button variables
        self.U_bender_bool = False
        self.bender_mode_bool = False
        self.U_extraction_bool = False
        self.U_segment_1_bool = False
        self.segment_1_mode_bool = False
        self.U_segment_2_bool = False
        self.segment_2_mode_bool = False
        self.U_segment_3_bool = False
        self.segment_3_mode_bool = False
        self.U_segment_4_bool = False
        self.segment_4_mode_bool = False
        self.U_segment_5_bool = False
        self.segment_5_mode_bool = False
        self.U_loading_plate_bool = False


        #self.connect()

    def quitProgram(self):
        print('quit')
        #self.reactor.stop()
        self.root.quit()
        self.root.destroy()


    # #Connects to Labrad
    # @inlineCallbacks
    # def connect(self):
    #     from labrad.wrappers import connectAsync
        
    #     self.cxn = yield connectAsync(name="Thorium Control Center")
       
    #     self.bender_server = yield self.cxn.hv500_bender_server
    #     self.loading_server = yield self.cxn.hv500_loading_server
    #     print('yup')

    #     multiThreading(self.data_reader())



    def connect_no_yield(self):
        import labrad

        self.cxn = labrad.connect()
        self.bender_server = self.cxn.hv500_bender_server
        self.loading_server = self.cxn.hv500_loading_server


    def getVoltages(self):
        try:
            bender_v = self.bender_server.get_all_voltages()
            loading_v = self.loading_server.get_all_voltages()

            for name, entry in self.v_location.items():
                if entry[0] == 'b':
                    self.actual_voltages[name] = bender_v[entry[1]-1]
                elif entry[0] == 'l':
                    self.actual_voltages[name] = loading_v[entry[1]-1]
        except:
            print('Error getting voltages')

        
                
            


    def getVoltage(self, name):
        supply = self.v_location[name][0]
        channel = self.v_location[name][1]
        if supply == 'b':
            voltage = self.bender_server.get_voltage(channel)
        elif supply == 'l':
            voltage = self.loading_server.get_voltage(channel)
        return voltage
    

    def setVoltage(self, name):
        supply = self.v_location[name][0]
        channel = self.v_location[name][1]
        if supply == 'b':
            self.bender_server.set_voltage(channel, self.set_voltages[name])
        elif supply == 'l':
            self.loading_server.set_voltage(channel, self.set_voltages[name])


    # #This function is run in a separate thread and runs continuously
    # #It reads values of all PLC variables and updates them in the display
    # @inlineCallbacks
    # def data_reader(self):
    #     while True:
    #         for v in self.v_location:
    #             supply = self.v_location[v][0]
    #             channel = self.v_location[v][1]
    #             if supply == 'b':
    #                 voltage = yield self.bender_server.get_voltage(channel)
    #             elif supply == 'l':
    #                 voltage = yield self.loading_server.get_voltage(channel)


    #             if v == 'U_TR_bender':
    #                 #self.U_TR_bender = self.getVoltage(self.v_location[v][0], self.v_location[v][1])
    #                 self.U_TR_bender = voltage
    #                 print(self.U_TR_bender)
        
    #         time.sleep(1)


    # This function is run in a separate thread and runs continuously
    # It reads values of all power supply voltages and updates them in the display
    def data_reader_no_yield(self):

        # Establishes connection to the LabRad server
        self.connect_no_yield()

        # Reads existing voltages and updates the set and entry voltages accordingly upon first time booting software
        self.getVoltages()
        self.set_voltages = self.actual_voltages.copy()
        self.entry_voltages = self.actual_voltages.copy()

        # Continuously loops to both read the voltage values from the supplies and also to update those values if the user has entered a new one
        while True:
            self.updateSetV()
            self.getVoltages()


            for v in self.v_location:
                if abs(self.actual_voltages[v] - self.set_voltages[v]) > 0.2:
                    self.setVoltage(v)

                self.updateActualV(v)
        
            time.sleep(0.5)


    # This function updates the actual voltage labels in the GUI
    def updateActualV(self, name):
        if name == 'U_TL_bender':
            self.TL_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR_bender':
            self.TR_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_BL_bender':
            self.BL_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BR_bender':
            self.BR_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_TL_plate':
            self.TLP_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR_plate':
            self.TRP_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL_plate':
            self.BLP_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BR_plate':
            self.BRP_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_L_ablation':
            self.LA_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_R_ablation':
            self.RA_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_TR1_loading':
            self.TR1_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_TL1_loading':
            self.TL1_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL1_loading':
            self.BL1_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_BR1_loading':
            self.BR1_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR2_loading':
            self.TR2_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TL2_loading':
            self.TL2_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL2_loading':
            self.BL2_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))
        
        elif name == 'U_BR2_loading':
            self.BR2_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR3_loading':
            self.TR3_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TL3_loading':
            self.TL3_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL3_loading':
            self.BL3_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BR3_loading':
            self.BR3_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR4_loading':
            self.TR4_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TL4_loading':
            self.TL4_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL4_loading':
            self.BL4_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BR4_loading':
            self.BR4_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TR5_loading':
            self.TR5_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_TL5_loading':
            self.TL5_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BL5_loading':
            self.BL5_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_BR5_loading':
            self.BR5_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))

        elif name == 'U_exit_loading':
            self.U_exit_loading_actual.config(text="{:.1f} V".format(self.actual_voltages[name]))


    
    # Updates the entry voltage values in the GUI
    def updateEntryV(self, name):
        if name == 'U_bender':
            self.U_bender = float(self.U_bender_entry.get())
            self.U_bender_entry.delete(0, END)
            self.U_bender_entry.insert(0, int(round(self.U_bender,0)))

        elif name == 'U_TL_bender':
            self.entry_voltages[name] = float(self.TL_entry.get())
            self.TL_entry.delete(0, END)
            self.TL_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TR_bender':
            self.entry_voltages[name] = float(self.TR_entry.get())
            self.TR_entry.delete(0, END)
            self.TR_entry.insert(0, int(round(self.entry_voltages[name],0)))
        
        elif name == 'U_BL_bender':
            self.entry_voltages[name] = float(self.BL_entry.get())
            self.BL_entry.delete(0, END)
            self.BL_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR_bender':
            self.entry_voltages[name] = float(self.BR_entry.get())
            self.BR_entry.delete(0, END)
            self.BR_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TL_plate':
            self.entry_voltages[name] = float(self.TLP_entry.get())
            self.TLP_entry.delete(0, END)
            self.TLP_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TR_plate':
            self.entry_voltages[name] = float(self.TRP_entry.get())
            self.TRP_entry.delete(0, END)
            self.TRP_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BL_plate':
            self.entry_voltages[name] = float(self.BLP_entry.get())
            self.BLP_entry.delete(0, END)
            self.BLP_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR_plate':
            self.entry_voltages[name] = float(self.BRP_entry.get())
            self.BRP_entry.delete(0, END)
            self.BRP_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_L_ablation':
            self.entry_voltages[name] = float(self.LA_entry.get())
            self.LA_entry.delete(0, END)
            self.LA_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_R_ablation':
            self.entry_voltages[name] = float(self.RA_entry.get())
            self.RA_entry.delete(0, END)
            self.RA_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_segment_1':
            self.U_segment_1 = float(self.U_segment_1_entry.get())
            self.U_segment_1_entry.delete(0, END)
            self.U_segment_1_entry.insert(0, int(round(self.U_segment_1,0)))

        elif name == 'dU_segment_1':
            self.dU_segment_1 = float(self.dU_segment_1_entry.get())
            self.dU_segment_1_entry.delete(0, END)
            self.dU_segment_1_entry.insert(0, int(round(self.dU_segment_1,0)))

        elif name == 'U_TR1_loading':
            self.entry_voltages[name] = float(self.TR1_entry.get())
            self.TR1_entry.delete(0, END)
            self.TR1_entry.insert(0, int(round(self.entry_voltages[name],0)))
        
        elif name == 'U_TL1_loading':
            self.entry_voltages[name] = float(self.TL1_entry.get())
            self.TL1_entry.delete(0, END)
            self.TL1_entry.insert(0, int(round(self.entry_voltages[name],0)))
        
        elif name == 'U_BL1_loading':
            self.entry_voltages[name] = float(self.BL1_entry.get())
            self.BL1_entry.delete(0, END)
            self.BL1_entry.insert(0, int(round(self.entry_voltages[name],0)))
        
        elif name == 'U_BR1_loading':
            self.entry_voltages[name] = float(self.BR1_entry.get())
            self.BR1_entry.delete(0, END)
            self.BR1_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_segment_2':
            self.U_segment_2 = float(self.U_segment_2_entry.get())
            self.U_segment_2_entry.delete(0, END)
            self.U_segment_2_entry.insert(0, int(round(self.U_segment_2,0)))

        elif name == 'dU_segment_2':
            self.dU_segment_2 = float(self.dU_segment_2_entry.get())
            self.dU_segment_2_entry.delete(0, END)
            self.dU_segment_2_entry.insert(0, int(round(self.dU_segment_2,0)))
        
        elif name == 'U_TR2_loading':
            self.entry_voltages[name] = float(self.TR2_entry.get())
            self.TR2_entry.delete(0, END)
            self.TR2_entry.insert(0, int(round(self.entry_voltages[name],0)))
        
        elif name == 'U_TL2_loading':
            self.entry_voltages[name] = float(self.TL2_entry.get())
            self.TL2_entry.delete(0, END)
            self.TL2_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BL2_loading':
            self.entry_voltages[name] = float(self.BL2_entry.get())
            self.BL2_entry.delete(0, END)
            self.BL2_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR2_loading':
            self.entry_voltages[name] = float(self.BR2_entry.get())
            self.BR2_entry.delete(0, END)
            self.BR2_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_segment_3':
            self.U_segment_3 = float(self.U_segment_3_entry.get())
            self.U_segment_3_entry.delete(0, END)
            self.U_segment_3_entry.insert(0, int(round(self.U_segment_3,0)))
        
        elif name == 'dU_segment_3':
            self.dU_segment_3 = float(self.dU_segment_3_entry.get())
            self.dU_segment_3_entry.delete(0, END)
            self.dU_segment_3_entry.insert(0, int(round(self.dU_segment_3,0)))

        elif name == 'U_TR3_loading':
            self.entry_voltages[name] = float(self.TR3_entry.get())
            self.TR3_entry.delete(0, END)
            self.TR3_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TL3_loading':
            self.entry_voltages[name] = float(self.TL3_entry.get())
            self.TL3_entry.delete(0, END)
            self.TL3_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR3_loading':
            self.entry_voltages[name] = float(self.BR3_entry.get())
            self.BR3_entry.delete(0, END)
            self.BR3_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BL3_loading':
            self.entry_voltages[name] = float(self.BL3_entry.get())
            self.BL3_entry.delete(0, END)
            self.BL3_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_segment_4':
            self.U_segment_4 = float(self.U_segment_4_entry.get())
            self.U_segment_4_entry.delete(0, END)
            self.U_segment_4_entry.insert(0, int(round(self.U_segment_4,0)))

        elif name == 'dU_segment_4':
            self.dU_segment_4 = float(self.dU_segment_4_entry.get())
            self.dU_segment_4_entry.delete(0, END)
            self.dU_segment_4_entry.insert(0, int(round(self.dU_segment_4,0)))

        elif name == 'U_TR4_loading':
            self.entry_voltages[name] = float(self.TR4_entry.get())
            self.TR4_entry.delete(0, END)
            self.TR4_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TL4_loading':
            self.entry_voltages[name] = float(self.TL4_entry.get())
            self.TL4_entry.delete(0, END)
            self.TL4_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR4_loading':
            self.entry_voltages[name] = float(self.BR4_entry.get())
            self.BR4_entry.delete(0, END)
            self.BR4_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BL4_loading':
            self.entry_voltages[name] = float(self.BL4_entry.get())
            self.BL4_entry.delete(0, END)
            self.BL4_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_segment_5':
            self.U_segment_5 = float(self.U_segment_5_entry.get())
            self.U_segment_5_entry.delete(0, END)
            self.U_segment_5_entry.insert(0, int(round(self.U_segment_5,0)))

        elif name == 'dU_segment_5':
            self.dU_segment_5 = float(self.dU_segment_5_entry.get())
            self.dU_segment_5_entry.delete(0, END)
            self.dU_segment_5_entry.insert(0, int(round(self.dU_segment_5,0)))

        elif name == 'U_TR5_loading':
            self.entry_voltages[name] = float(self.TR5_entry.get())
            self.TR5_entry.delete(0, END)
            self.TR5_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_TL5_loading':
            self.entry_voltages[name] = float(self.TL5_entry.get())
            self.TL5_entry.delete(0, END)
            self.TL5_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BR5_loading':
            self.entry_voltages[name] = float(self.BR5_entry.get())
            self.BR5_entry.delete(0, END)
            self.BR5_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_BL5_loading':
            self.entry_voltages[name] = float(self.BL5_entry.get())
            self.BL5_entry.delete(0, END)
            self.BL5_entry.insert(0, int(round(self.entry_voltages[name],0)))

        elif name == 'U_exit_loading':
            self.entry_voltages[name] = float(self.U_exit_loading_entry.get())
            self.U_exit_loading_entry.delete(0, END)
            self.U_exit_loading_entry.insert(0, int(round(self.entry_voltages[name],0)))


    # Updates the set voltage values
    def updateSetV(self):
        quad_names = ['U_TL_bender', 'U_TR_bender', 'U_BL_bender', 'U_BR_bender']
        extraction_names = ['U_TL_plate', 'U_TR_plate', 'U_BL_plate', 'U_BR_plate', 'U_L_ablation', 'U_L_ablation']
        segment_1_names = ['U_TR1_loading', 'U_TL1_loading', 'U_BR1_loading', 'U_BL1_loading']
        segment_2_names = ['U_TR2_loading', 'U_TL2_loading', 'U_BR2_loading', 'U_BL2_loading']
        segment_3_names = ['U_TR3_loading', 'U_TL3_loading', 'U_BR3_loading', 'U_BL3_loading']
        segment_4_names = ['U_TR4_loading', 'U_TL4_loading', 'U_BR4_loading', 'U_BL4_loading']
        segment_5_names = ['U_TR5_loading', 'U_TL5_loading', 'U_BR5_loading', 'U_BL5_loading']

        # Quadrupole bender button logic
        if self.U_bender_bool:
            if self.bender_mode_bool:
                for name in quad_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                self.set_voltages['U_TL_bender'] = -self.U_bender
                self.set_voltages['U_TR_bender'] = self.U_bender
                self.set_voltages['U_BL_bender'] = self.U_bender
                self.set_voltages['U_BR_bender'] = -self.U_bender
        else:
            for name in quad_names:
                self.set_voltages[name] = 0

        # Extraction electrode button logic
        if self.U_extraction_bool:
            for name in extraction_names:
                self.set_voltages[name] = self.entry_voltages[name]
        else:
            for name in extraction_names:
                self.set_voltages[name] = 0
        
        # Segment 1 button logic
        if self.U_segment_1_bool:
            if self.segment_1_mode_bool:
                for name in segment_1_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                i = 1
                for name in segment_1_names:
                    self.set_voltages[name] = self.U_segment_1 + (-1)**i*self.dU_segment_1
                    i = i + 1     
        else:
            for name in segment_1_names:
                self.set_voltages[name] = 0

        # Segment 2 button logic
        if self.U_segment_2_bool:
            if self.segment_2_mode_bool:
                for name in segment_2_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                i = 1
                for name in segment_2_names:
                    self.set_voltages[name] = self.U_segment_2 + (-1)**i*self.dU_segment_2
                    i = i + 1
        else:
            for name in segment_2_names:
                self.set_voltages[name] = 0

        # Segment 3 button logic
        if self.U_segment_3_bool:
            if self.segment_3_mode_bool:
                for name in segment_3_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                i = 1
                for name in segment_3_names:
                    self.set_voltages[name] = self.U_segment_3 + (-1)**i*self.dU_segment_3
                    i = i + 1
        else:
            for name in segment_3_names:
                self.set_voltages[name] = 0

        # Segment 4 button logic
        if self.U_segment_4_bool:
            if self.segment_4_mode_bool:
                for name in segment_4_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                i = 1
                for name in segment_4_names:
                    self.set_voltages[name] = self.U_segment_4 + (-1)**i*self.dU_segment_4
                    i = i + 1
        else:
            for name in segment_4_names:
                self.set_voltages[name] = 0
        
        # Segment 5 button logic
        if self.U_segment_5_bool:
            if self.segment_5_mode_bool:
                for name in segment_5_names:
                    self.set_voltages[name] = self.entry_voltages[name]
            else:
                i = 1
                for name in segment_5_names:
                    self.set_voltages[name] = self.U_segment_5 + (-1)**i*self.dU_segment_5
                    i = i + 1
        else:
            for name in segment_5_names:
                self.set_voltages[name] = 0

        if self.U_loading_plate_bool:
            self.set_voltages['U_exit_loading'] = self.entry_voltages['U_exit_loading']
        else:
            self.set_voltages['U_exit_loading'] = 0
                

    # Defines what should happen when a button is clicked
    def click_button(self, button, type, variable, text=None):
        if type == 'power':
            self.update_button_var(variable, True)
            button.config(bg='#50E24B', command=lambda: self.declick_button(button, type, variable), activebackground='#50E24B')

        elif type == 'mode':
            self.update_button_var(variable, True)
            button.config(bg='#50E24B', text='Operate Poles\nTogether', command=lambda: self.declick_button(button, type, variable, text), activebackground='#50E24B')



    # Defines what should happen when a button is declicked
    def declick_button(self, button, type, variable, text=None):
        self.update_button_var(variable, False)
        if type == 'power':
            button.config(bg='grey90', command=lambda: self.click_button(button, type, variable), activebackground='grey90')
        elif type == 'mode':
            button.config(bg='#1AA5F6', text='Operate Poles\nSeparately', command=lambda: self.click_button(button, type, variable, text), activebackground='#1AA5F6')

    # Updates the variables for the buttons
    def update_button_var(self, variable, value):
        if variable == 'U_bender':
            self.U_bender_bool = value
            print('Quadrupole Bender power button pressed')
        elif variable == 'bender_mode':
            self.bender_mode_bool = value
            print('Quadrupole Bender mode button pressed')
        elif variable == 'U_extraction':
            self.U_extraction_bool = value
            print('Ion Extraction power button pressed')
        elif variable == 'U_segment_1':
            self.U_segment_1_bool = value
            print('Segment 1 power button pressed')
        elif variable == 'segment_1_mode':
            self.segment_1_mode_bool = value
            print('Segment 1 mode button pressed')
        elif variable == 'U_segment_2':
            self.U_segment_2_bool = value
            print('Segment 2 power button pressed')
        elif variable == 'segment_2_mode':
            self.segment_2_mode_bool = value
            print('Segment 2 mode button pressed')
        elif variable == 'U_segment_3':
            self.U_segment_3_bool = value
            print('Segment 3 power button pressed')
        elif variable == 'segment_3_mode':
            self.segment_3_mode_bool = value
            print('Segment 3 mode button pressed')
        elif variable == 'U_segment_4':
            self.U_segment_4_bool = value
            print('Segment 4 power button pressed')
        elif variable == 'segment_4_mode':
            self.segment_4_mode_bool = value
            print('Segment 4 mode button pressed')
        elif variable == 'U_segment_5':
            self.U_segment_5_bool = value
            print('Segment 5 power button pressed')
        elif variable == 'segment_5_mode':
            self.segment_5_mode_bool = value
            print('Segment 5 mode button pressed')
        elif variable == 'U_loading_plate':
            self.U_loading_plate_bool = value
            print('Loading Plate power button pressed')
    
    #Opens About Window with description of software
    def About(self):
        name = "Thorium Control Center"
        version = 'Version: 1.0.0'
        date = 'Date: 07/26/2024'
        support = 'Support: '
        url = 'https://github.com/rhmatti/Thorium-Control-Interface'
        copyrightMessage ='Copyright © 2024 Richard Mattish All Rights Reserved.'
        t = Toplevel(self.root)
        t.wm_title("About")
        t.geometry("400x300")
        t.resizable(False, False)
        t.configure(background='white')
        if platform.system() == 'Windows':
            try:
                t.iconbitmap("icons/TCI.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        l1 = Label(t, text = name, bg='white', fg='blue', font=font_14)
        l1.place(relx = 0.15, rely = 0.14, anchor = W)
        l2 = Label(t, text = version, bg='white', font=font_12)
        l2.place(relx = 0.15, rely = 0.25, anchor = W)
        l3 = Label(t, text = date, bg='white', font=font_12)
        l3.place(relx = 0.15, rely = 0.35, anchor = W)
        l4 = Label(t, text = support, bg = 'white', font=font_12)
        l4.place(relx = 0.15, rely = 0.45, anchor = W)
        l5 = Label(t, text = 'https://github.com/rhmatti/\nThorium-Control-Interface', bg = 'white', fg = 'blue', font=font_12)
        l5.place(relx = 0.31, rely=0.48, anchor = W)
        l5.bind("<Button-1>", lambda e:
        callback(url))
        messageVar = Message(t, text = copyrightMessage, bg='white', font = font_12, width = 600)
        messageVar.place(relx = 0.5, rely = 1, anchor = S)

    def Instructions(self):
        instructions = Toplevel(self.root)
        instructions.geometry('1280x720')
        instructions.wm_title("User Instructions")
        instructions.configure(bg='white')
        if platform.system() == 'Windows':
            try:
                instructions.iconbitmap("icons/TCI.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')
        v = Scrollbar(instructions, orient = 'vertical')
        t = Text(instructions, font = font_12, bg='white', width = 100, height = 100, wrap = NONE, yscrollcommand = v.set)
        t.insert(END, "*********************************************************************************************************************\n")
        t.insert(END, "Program: Thorium Control Center\n")
        t.insert(END, "Author: Richard Mattish\n")
        t.insert(END, "Last Updated: 02/24/2022\n\n")
        t.insert(END, "Function:  This program provides a graphical user interface for setting\n")
        t.insert(END, "\tand monitoring the bender and trap electrode voltages for the Thorium\n")
        t.insert(END, "\tproject.\n")
        t.insert(END, "*********************************************************************************************************************\n\n\n\n")
        t.insert(END, "User Instructions\n-------------------------\n")
        t.insert(END, "Add Instructions Here Later")

        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)


    #Creates the Different Menus in the Main Window
    def createMenus(self, menu):
        #Creates File menu
        self.filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=self.filemenu)
        #filemenu.add_command(label="Import", command=lambda: self.askopenfile(), accelerator="Ctrl+I")
        #filemenu.add_command(label="Save", command=lambda: CSA.saveGraph(), accelerator="Ctrl+S")
        #filemenu.add_command(label='Settings', command=lambda: self.Settings())
        #filemenu.add_command(label='Calibrate', command=lambda: self.calibration())
        self.filemenu.add_separator()
        self.filemenu.add_command(label='New Window', command=lambda: startProgram(Toplevel(self.root)))
        self.filemenu.add_command(label='Exit', command=lambda: self.quitProgram())

        #Creates Help menu
        self.helpmenu = Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=self.helpmenu)
        self.helpmenu.add_command(label='Instructions', command= lambda: self.Instructions())
        self.helpmenu.add_command(label='About', command= lambda: self.About())


    #Creates Different Tabs in the Main Window
    def createTabs(self):
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=font_16)
        style.configure('TFrame', background='#96CAF2')
        #style.configure('TFrame', background='#F5974F')
        self.tabControl = ttk.Notebook(self.root)
        self.bender_tab = ttk.Frame(self.tabControl)
        self.loading_tab = ttk.Frame(self.tabControl)
        self.precision_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.bender_tab, text='Bender')
        self.tabControl.add(self.loading_tab, text='Loading Trap')
        self.tabControl.add(self.precision_tab, text='Precision Trap')
        self.tabControl.pack(expand=1, fill='both')
        #self.tabControl.place(relx=0.5, rely=0, anchor=N)


    #Creates the quadrupole bender electrode controls
    def quad_bender_controls(self, x, y):    
        self.quad_bender = Frame(self.bender_tab, width = 400, height = 350, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.quad_bender.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.quad_bender, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.5,anchor=CENTER)

        quadbenderLabel = Label(self.quad_bender, text = 'Quadrupole Bender', font = font_18, bg = 'grey90', fg = 'black')
        quadbenderLabel.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.quad_bender_button = Button(self.quad_bender, image=self.power_button, command=lambda: self.click_button(self.quad_bender_button, 'power', 'U_bender'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.quad_bender_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_bender_label1 = Label(self.quad_bender, text='U', font=font_14, bg = 'grey90', fg = 'black')
        U_bender_label1.place(relx=0.15, rely=0.2, anchor=CENTER)
        U_bender_label2 = Label(self.quad_bender, text='bender', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=5)
        U_bender_label2.place(relx=0.165, rely=0.23, anchor=W)

        U_bender_label3 = Label(self.quad_bender, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_bender_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_bender_entry = mySpinbox(self.quad_bender, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.U_bender_entry.delete(0,"end")
        self.U_bender_entry.insert(0,int(round(self.U_bender,0)))
        self.U_bender_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_bender_entry.bind("<Return>", lambda eff: self.updateEntryV('U_bender'))
        self.U_bender_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_bender'))

        U_bender_label4 = Label(self.quad_bender, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_bender_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        #Creates the bender operation mode button
        self.bender_mode_button = Button(self.quad_bender, text='Operate Poles\nSeparately', relief = 'raised', command=lambda: self.click_button(self.bender_mode_button, 'mode', 'bender_mode'), width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.bender_mode_button.place(relx=0.75, rely=0.2, anchor=CENTER)


        #Top Left Bender Electrode GUI
        TL_label1 = Label(self.quad_bender, text='Top Left', font=font_16, bg = 'grey90', fg = 'black')
        TL_label1.place(relx=0.25, rely=0.4, anchor=CENTER)

        TL_label2 = Label(self.quad_bender, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TL_label2.place(relx=0.17, rely=0.5, anchor=E)

        self.TL_entry = mySpinbox(self.quad_bender, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL_entry.delete(0,"end")
        self.TL_entry.insert(0,int(round(self.entry_voltages['U_TL_bender'],0)))
        self.TL_entry.place(relx=0.17, rely=0.5, anchor=W, width=70)
        self.TL_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL_bender'))
        self.TL_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL_bender'))

        TL_label3 = Label(self.quad_bender, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TL_label3.place(relx=0.37, rely=0.5, anchor=CENTER)

        TL_label4 = Label(self.quad_bender, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TL_label4.place(relx=0.2, rely=0.6, anchor=E)

        self.TL_actual = Label(self.quad_bender, text="{:.1f} V".format(self.actual_voltages['U_TL_bender']), font=font_14, bg = 'grey90', fg = 'black')
        self.TL_actual.place(relx=0.4, rely=0.6, anchor=E)


        #Top Right Bender Electrode GUI
        TR_label1 = Label(self.quad_bender, text='Top Right', font=font_16, bg = 'grey90', fg = 'black')
        TR_label1.place(relx=0.75, rely=0.4, anchor=CENTER)

        TR_label2 = Label(self.quad_bender, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TR_label2.place(relx=0.67, rely=0.5, anchor=E)

        self.TR_entry = mySpinbox(self.quad_bender, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR_entry.delete(0,"end")
        self.TR_entry.insert(0,int(round(self.entry_voltages['U_TR_bender'],0)))
        self.TR_entry.place(relx=0.67, rely=0.5, anchor=W, width=70)
        self.TR_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR_bender'))
        self.TR_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR_bender'))

        TR_label3 = Label(self.quad_bender, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TR_label3.place(relx=0.87, rely=0.5, anchor=CENTER)

        TR_label4 = Label(self.quad_bender, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TR_label4.place(relx=0.7, rely=0.6, anchor=E)

        self.TR_actual = Label(self.quad_bender, text="{:.1f} V".format(self.actual_voltages['U_TR_bender']), font=font_14, bg = 'grey90', fg = 'black')
        self.TR_actual.place(relx=0.9, rely=0.6, anchor=E)


        #Bottom Left Bender Electrode GUI
        BL_label1 = Label(self.quad_bender, text='Bottom Left', font=font_16, bg = 'grey90', fg = 'black')
        BL_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL_label2 = Label(self.quad_bender, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BL_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL_entry = mySpinbox(self.quad_bender, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL_entry.delete(0,"end")
        self.BL_entry.insert(0,int(round(self.entry_voltages['U_BL_bender'],0)))
        self.BL_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL_bender'))
        self.BL_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL_bender'))

        BL_label3 = Label(self.quad_bender, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BL_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL_label4 = Label(self.quad_bender, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BL_label4.place(relx=0.2, rely=0.95, anchor=E)

        self.BL_actual = Label(self.quad_bender, text="{:.1f} V".format(self.actual_voltages['U_BL_bender']), font=font_14, bg = 'grey90', fg = 'black')
        self.BL_actual.place(relx=0.4, rely=0.95, anchor=E)


        #Bottom Right Bender Electrode GUI
        BR_label1 = Label(self.quad_bender, text='Bottom Right', font=font_16, bg = 'grey90', fg = 'black')
        BR_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR_label2 = Label(self.quad_bender, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BR_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR_entry = mySpinbox(self.quad_bender, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR_entry.delete(0,"end")
        self.BR_entry.insert(0,int(round(self.entry_voltages['U_BR_bender'],0)))
        self.BR_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR_bender'))
        self.BR_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR_bender'))

        BR_label3 = Label(self.quad_bender, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BR_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR_label4 = Label(self.quad_bender, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BR_label4.place(relx=0.7, rely=0.95, anchor=E)

        self.BR_actual = Label(self.quad_bender, text="{:.1f} V".format(self.actual_voltages['U_BR_bender']), font=font_14, bg = 'grey90', fg = 'black')
        self.BR_actual.place(relx=0.9, rely=0.95, anchor=E)


    
    #Creates the ion extraction/ablation electrode controls
    def extraction_controls(self, x, y):    
        self.extraction = Frame(self.bender_tab, width = 400, height = 450, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.extraction.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.extraction, width=390, height=440, bg='grey90', highlightthickness=0)
        w.create_line(0, 55, 390, 55)
        w.create_line(10, 185, 380, 185, dash = (3,2))
        w.create_line(10, 320, 380, 320, dash = (3,2))
        w.create_line(195, 65, 195, 435, dash = (3, 2))
        w.place(relx=0.5,rely=0.5,anchor=CENTER)

        extractionLabel = Label(self.extraction, text = 'Ion Extraction', font = font_18, bg = 'grey90', fg = 'black')
        extractionLabel.place(relx=0.5, rely=0.062, anchor = CENTER)

        #Creates bender power button
        self.extraction_button = Button(self.extraction, image=self.power_button, command=lambda: self.click_button(self.extraction_button, 'power', 'U_extraction'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.extraction_button.place(relx=0.1, rely=0.062, anchor=CENTER)


        #Top Left Extraction Plate Electrode GUI
        TL_label1 = Label(self.extraction, text='Top Left Plate', font=font_16, bg = 'grey90', fg = 'black')
        TL_label1.place(relx=0.25, rely=0.2, anchor=CENTER)

        TL_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TL_label2.place(relx=0.17, rely=0.28, anchor=E)

        self.TLP_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TLP_entry.delete(0,"end")
        self.TLP_entry.insert(0,int(round(self.entry_voltages['U_TL_plate'],0)))
        self.TLP_entry.place(relx=0.17, rely=0.28, anchor=W, width=70)
        self.TLP_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL_plate'))
        self.TLP_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL_plate'))

        TL_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TL_label3.place(relx=0.37, rely=0.28, anchor=CENTER)

        TL_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TL_label4.place(relx=0.2, rely=0.36, anchor=E)

        self.TLP_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_TL_plate']), font=font_14, bg = 'grey90', fg = 'black')
        self.TLP_actual.place(relx=0.4, rely=0.36, anchor=E)


        #Top Right Extraction Plate Electrode GUI
        TR_label1 = Label(self.extraction, text='Top Right Plate', font=font_16, bg = 'grey90', fg = 'black')
        TR_label1.place(relx=0.75, rely=0.2, anchor=CENTER)

        TR_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TR_label2.place(relx=0.67, rely=0.28, anchor=E)

        self.TRP_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TRP_entry.delete(0,"end")
        self.TRP_entry.insert(0,int(round(self.entry_voltages['U_TR_plate'],0)))
        self.TRP_entry.place(relx=0.67, rely=0.28, anchor=W, width=70)
        self.TRP_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR_plate'))
        self.TRP_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR_plate'))

        TR_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TR_label3.place(relx=0.87, rely=0.28, anchor=CENTER)

        TR_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TR_label4.place(relx=0.7, rely=0.36, anchor=E)

        self.TRP_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_TR_plate']), font=font_14, bg = 'grey90', fg = 'black')
        self.TRP_actual.place(relx=0.9, rely=0.36, anchor=E)


        #Bottom Left Extraction Plate Electrode GUI
        BL_label1 = Label(self.extraction, text='Bottom Left Plate', font=font_16, bg = 'grey90', fg = 'black')
        BL_label1.place(relx=0.25, rely=0.5, anchor=CENTER)

        BL_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BL_label2.place(relx=0.17, rely=0.58, anchor=E)

        self.BLP_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BLP_entry.delete(0,"end")
        self.BLP_entry.insert(0,int(round(self.entry_voltages['U_BL_plate'],0)))
        self.BLP_entry.place(relx=0.17, rely=0.58, anchor=W, width=70)
        self.BLP_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL_plate'))
        self.BLP_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL_plate'))

        BL_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BL_label3.place(relx=0.37, rely=0.58, anchor=CENTER)

        BL_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BL_label4.place(relx=0.2, rely=0.66, anchor=E)

        self.BLP_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_BL_plate']), font=font_14, bg = 'grey90', fg = 'black')
        self.BLP_actual.place(relx=0.4, rely=0.66, anchor=E)


        #Bottom Right Extraction Plate Electrode GUI
        BR_label1 = Label(self.extraction, text='Bottom Right Plate', font=font_16, bg = 'grey90', fg = 'black')
        BR_label1.place(relx=0.75, rely=0.5, anchor=CENTER)

        BR_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BR_label2.place(relx=0.67, rely=0.58, anchor=E)

        self.BRP_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BRP_entry.delete(0,"end")
        self.BRP_entry.insert(0,int(round(self.entry_voltages['U_BR_plate'],0)))
        self.BRP_entry.place(relx=0.67, rely=0.58, anchor=W, width=70)
        self.BRP_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR_plate'))
        self.BRP_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR_plate'))

        BR_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BR_label3.place(relx=0.87, rely=0.58, anchor=CENTER)

        BR_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BR_label4.place(relx=0.7, rely=0.66, anchor=E)

        self.BRP_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_BR_plate']), font=font_14, bg = 'grey90', fg = 'black')
        self.BRP_actual.place(relx=0.9, rely=0.66, anchor=E)


        #Left Ablation Target Electrode GUI
        LA_label1 = Label(self.extraction, text='Left Ablation', font=font_16, bg = 'grey90', fg = 'black')
        LA_label1.place(relx=0.25, rely=0.8, anchor=CENTER)

        LA_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        LA_label2.place(relx=0.17, rely=0.88, anchor=E)

        self.LA_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.LA_entry.delete(0,"end")
        self.LA_entry.insert(0,int(round(self.entry_voltages['U_L_ablation'],0)))
        self.LA_entry.place(relx=0.17, rely=0.88, anchor=W, width=70)
        self.LA_entry.bind("<Return>", lambda eff: self.updateEntryV('U_L_ablation'))
        self.LA_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_L_ablation'))

        LA_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        LA_label3.place(relx=0.37, rely=0.88, anchor=CENTER)

        LA_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        LA_label4.place(relx=0.2, rely=0.96, anchor=E)

        self.LA_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_L_ablation']), font=font_14, bg = 'grey90', fg = 'black')
        self.LA_actual.place(relx=0.4, rely=0.96, anchor=E)


        #Right Ablation Target Electrode GUI
        RA_label1 = Label(self.extraction, text='Right Ablation', font=font_16, bg = 'grey90', fg = 'black')
        RA_label1.place(relx=0.75, rely=0.8, anchor=CENTER)

        RA_label2 = Label(self.extraction, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        RA_label2.place(relx=0.67, rely=0.88, anchor=E)

        self.RA_entry = mySpinbox(self.extraction, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.RA_entry.delete(0,"end")
        self.RA_entry.insert(0,int(round(self.entry_voltages['U_R_ablation'],0)))
        self.RA_entry.place(relx=0.67, rely=0.88, anchor=W, width=70)
        self.RA_entry.bind("<Return>", lambda eff: self.updateEntryV('U_R_ablation'))
        self.RA_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_R_ablation'))

        RA_label3 = Label(self.extraction, text='V', font=font_14, bg = 'grey90', fg = 'black')
        RA_label3.place(relx=0.87, rely=0.88, anchor=CENTER)

        RA_label4 = Label(self.extraction, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        RA_label4.place(relx=0.7, rely=0.96, anchor=E)

        self.RA_actual = Label(self.extraction, text="{:.1f} V".format(self.actual_voltages['U_R_ablation']), font=font_14, bg = 'grey90', fg = 'black')
        self.RA_actual.place(relx=0.9, rely=0.96, anchor=E)


    #Creates the loading trap electrode controls
    def segment_1_controls(self, x, y):    
        self.segment_1 = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.segment_1.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.segment_1, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        segment1Label = Label(self.segment_1, text = 'Segment 1', font = font_18, bg = 'grey90', fg = 'black')
        segment1Label.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.segment_1_button = Button(self.segment_1, image=self.power_button, command=lambda: self.click_button(self.segment_1_button, 'power', 'U_segment_1'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.segment_1_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_segment_1_label1 = Label(self.segment_1, text='U', font=font_14, bg = 'grey90', fg = 'black', width=1)
        U_segment_1_label1.place(relx=0.22, rely=0.2, anchor=E)
        U_segment_1_label2 = Label(self.segment_1, text='S1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_1_label2.place(relx=0.22, rely=0.23, anchor=W)

        U_segment_1_label3 = Label(self.segment_1, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_1_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_segment_1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.U_segment_1_entry.delete(0,"end")
        self.U_segment_1_entry.insert(0,int(round(self.U_segment_1,0)))
        self.U_segment_1_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_segment_1_entry.bind("<Return>", lambda eff: self.updateEntryV('U_segment_1'))
        self.U_segment_1_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_segment_1'))

        U_segment_1_label4 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_1_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        U_segment_1_label5 = Label(self.segment_1, text='dU', font=font_14, bg = 'grey90', fg = 'black', width=2)
        U_segment_1_label5.place(relx=0.22, rely=0.3, anchor=E)
        U_segment_1_label6 = Label(self.segment_1, text='S1', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_1_label6.place(relx=0.22, rely=0.33, anchor=W)

        U_segment_1_label7 = Label(self.segment_1, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_1_label7.place(relx=0.31, rely=0.3, anchor=E)

        self.dU_segment_1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.dU_segment_1_entry.delete(0,"end")
        self.dU_segment_1_entry.insert(0,int(round(self.dU_segment_1,0)))
        self.dU_segment_1_entry.place(relx=0.31, rely=0.3, anchor=W, width=70)
        self.dU_segment_1_entry.bind("<Return>", lambda eff: self.updateEntryV('dU_segment_1'))
        self.dU_segment_1_entry.bind("<Tab>", lambda eff: self.updateEntryV('dU_segment_1'))

        U_segment_1_label8 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_1_label8.place(relx=0.51, rely=0.3, anchor=CENTER)

        #Creates the bender operation mode button
        self.segment_1_mode_button = Button(self.segment_1, text='Operate Poles\nSeparately', relief = 'raised', command=lambda: self.click_button(self.segment_1_mode_button, 'mode', 'segment_1_mode'), width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.segment_1_mode_button.place(relx=0.75, rely=0.25, anchor=CENTER)


        #Top Left Loading Electrode GUI
        TL1_label1 = Label(self.segment_1, text='Top Left', font=font_16, bg = 'grey90', fg = 'black')
        TL1_label1.place(relx=0.25, rely=0.45, anchor=CENTER)

        TL1_label2 = Label(self.segment_1, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TL1_label2.place(relx=0.17, rely=0.55, anchor=E)

        self.TL1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL1_entry.delete(0,"end")
        self.TL1_entry.insert(0,int(round(self.entry_voltages['U_TL1_loading'],0)))
        self.TL1_entry.place(relx=0.17, rely=0.55, anchor=W, width=70)
        self.TL1_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL1_loading'))
        self.TL1_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL1_loading'))

        TL1_label3 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TL1_label3.place(relx=0.37, rely=0.55, anchor=CENTER)

        TL1_label4 = Label(self.segment_1, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TL1_label4.place(relx=0.2, rely=0.64, anchor=E)

        self.TL1_actual = Label(self.segment_1, text="{:.1f} V".format(self.actual_voltages['U_TL1_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TL1_actual.place(relx=0.4, rely=0.64, anchor=E)


        #Top Right Loading Electrode GUI
        TR1_label1 = Label(self.segment_1, text='Top Right', font=font_16, bg = 'grey90', fg = 'black')
        TR1_label1.place(relx=0.75, rely=0.45, anchor=CENTER)

        TR1_label2 = Label(self.segment_1, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TR1_label2.place(relx=0.67, rely=0.55, anchor=E)

        self.TR1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR1_entry.delete(0,"end")
        self.TR1_entry.insert(0,int(round(self.entry_voltages['U_TR1_loading'],0)))
        self.TR1_entry.place(relx=0.67, rely=0.55, anchor=W, width=70)
        self.TR1_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR1_loading'))
        self.TR1_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR1_loading'))

        TR1_label3 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TR1_label3.place(relx=0.87, rely=0.55, anchor=CENTER)

        TR1_label4 = Label(self.segment_1, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TR1_label4.place(relx=0.7, rely=0.64, anchor=E)

        self.TR1_actual = Label(self.segment_1, text="{:.1f} V".format(self.actual_voltages['U_TR1_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TR1_actual.place(relx=0.9, rely=0.64, anchor=E)


        #Bottom Left Loading Electrode GUI
        BL1_label1 = Label(self.segment_1, text='Bottom Left', font=font_16, bg = 'grey90', fg = 'black')
        BL1_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL1_label2 = Label(self.segment_1, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BL1_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL1_entry.delete(0,"end")
        self.BL1_entry.insert(0,int(round(self.entry_voltages['U_BL1_loading'],0)))
        self.BL1_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL1_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL1_loading'))
        self.BL1_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL1_loading'))

        BL1_label3 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BL1_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL1_label4 = Label(self.segment_1, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BL1_label4.place(relx=0.2, rely=0.94, anchor=E)

        self.BL1_actual = Label(self.segment_1, text="{:.1f} V".format(self.actual_voltages['U_BL1_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.BL1_actual.place(relx=0.4, rely=0.94, anchor=E)


        #Bottom Right Loading Electrode GUI
        BR1_label1 = Label(self.segment_1, text='Bottom Right', font=font_16, bg = 'grey90', fg = 'black')
        BR1_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR1_label2 = Label(self.segment_1, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BR1_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR1_entry = mySpinbox(self.segment_1, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR1_entry.delete(0,"end")
        self.BR1_entry.insert(0,int(round(self.entry_voltages['U_BR1_loading'],0)))
        self.BR1_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR1_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR1_loading'))
        self.BR1_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR1_loading'))

        BR1_label3 = Label(self.segment_1, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BR1_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR1_label4 = Label(self.segment_1, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BR1_label4.place(relx=0.7, rely=0.94, anchor=E)

        self.BR1_actual = Label(self.segment_1, text="{:.1f} V".format(self.actual_voltages['U_BR1_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.BR1_actual.place(relx=0.9, rely=0.94, anchor=E)



    def segment_2_controls(self, x, y):    
        self.segment_2 = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.segment_2.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.segment_2, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        segment2Label = Label(self.segment_2, text = 'Segment 2', font = font_18, bg = 'grey90', fg = 'black')
        segment2Label.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.segment_2_button = Button(self.segment_2, image=self.power_button, command=lambda: self.click_button(self.segment_2_button, 'power', 'U_segment_2'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.segment_2_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_segment_2_label1 = Label(self.segment_2, text='U', font=font_14, bg = 'grey90', fg = 'black', width=1)
        U_segment_2_label1.place(relx=0.22, rely=0.2, anchor=E)
        U_segment_2_label2 = Label(self.segment_2, text='S2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_2_label2.place(relx=0.22, rely=0.23, anchor=W)

        U_segment_2_label3 = Label(self.segment_2, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_2_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_segment_2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.U_segment_2_entry.delete(0,"end")
        self.U_segment_2_entry.insert(0,int(round(self.U_segment_2,0)))
        self.U_segment_2_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_segment_2_entry.bind("<Return>", lambda eff: self.updateEntryV('U_segment_2'))
        self.U_segment_2_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_segment_2'))

        U_segment_2_label4 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_2_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        U_segment_2_label5 = Label(self.segment_2, text='dU', font=font_14, bg = 'grey90', fg = 'black', width=2)
        U_segment_2_label5.place(relx=0.22, rely=0.3, anchor=E)
        U_segment_2_label6 = Label(self.segment_2, text='S2', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_2_label6.place(relx=0.22, rely=0.33, anchor=W)

        U_segment_2_label7 = Label(self.segment_2, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_2_label7.place(relx=0.31, rely=0.3, anchor=E)

        self.dU_segment_2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.dU_segment_2_entry.delete(0,"end")
        self.dU_segment_2_entry.insert(0,int(round(self.dU_segment_2,0)))
        self.dU_segment_2_entry.place(relx=0.31, rely=0.3, anchor=W, width=70)
        self.dU_segment_2_entry.bind("<Return>", lambda eff: self.updateEntryV('dU_segment_2'))
        self.dU_segment_2_entry.bind("<Tab>", lambda eff: self.updateEntryV('dU_segment_2'))

        U_segment_2_label8 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_2_label8.place(relx=0.51, rely=0.3, anchor=CENTER)

        #Creates the bender operation mode button
        self.segment_2_mode_button = Button(self.segment_2, text='Operate Poles\nSeparately', relief = 'raised', command=lambda: self.click_button(self.segment_2_mode_button, 'mode', 'segment_2_mode'), width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.segment_2_mode_button.place(relx=0.75, rely=0.25, anchor=CENTER)


        #Top Left Loading Electrode GUI
        TL2_label1 = Label(self.segment_2, text='Top Left', font=font_16, bg = 'grey90', fg = 'black')
        TL2_label1.place(relx=0.25, rely=0.45, anchor=CENTER)

        TL2_label2 = Label(self.segment_2, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TL2_label2.place(relx=0.17, rely=0.55, anchor=E)

        self.TL2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL2_entry.delete(0,"end")
        self.TL2_entry.insert(0,int(round(self.entry_voltages['U_TL2_loading'],0)))
        self.TL2_entry.place(relx=0.17, rely=0.55, anchor=W, width=70)
        self.TL2_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL2_loading'))
        self.TL2_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL2_loading'))

        TL2_label3 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TL2_label3.place(relx=0.37, rely=0.55, anchor=CENTER)

        TL2_label4 = Label(self.segment_2, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TL2_label4.place(relx=0.2, rely=0.64, anchor=E)

        self.TL2_actual = Label(self.segment_2, text="{:.1f} V".format(self.actual_voltages['U_TL2_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TL2_actual.place(relx=0.4, rely=0.64, anchor=E)


        #Top Right Loading Electrode GUI
        TR2_label1 = Label(self.segment_2, text='Top Right', font=font_16, bg = 'grey90', fg = 'black')
        TR2_label1.place(relx=0.75, rely=0.45, anchor=CENTER)

        TR2_label2 = Label(self.segment_2, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TR2_label2.place(relx=0.67, rely=0.55, anchor=E)

        self.TR2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR2_entry.delete(0,"end")
        self.TR2_entry.insert(0,int(round(self.entry_voltages['U_TR2_loading'],0)))
        self.TR2_entry.place(relx=0.67, rely=0.55, anchor=W, width=70)
        self.TR2_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR2_loading'))
        self.TR2_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR2_loading'))


        TR2_label3 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TR2_label3.place(relx=0.87, rely=0.55, anchor=CENTER)

        TR2_label4 = Label(self.segment_2, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TR2_label4.place(relx=0.7, rely=0.64, anchor=E)

        self.TR2_actual = Label(self.segment_2, text="{:.1f} V".format(self.actual_voltages['U_TR2_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TR2_actual.place(relx=0.9, rely=0.64, anchor=E)


        #Bottom Left Loading Electrode GUI
        BL2_label1 = Label(self.segment_2, text='Bottom Left', font=font_16, bg = 'grey90', fg = 'black')
        BL2_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL2_label2 = Label(self.segment_2, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BL2_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL2_entry.delete(0,"end")
        self.BL2_entry.insert(0,int(round(self.entry_voltages['U_BL2_loading'],0)))
        self.BL2_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL2_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL2_loading'))
        self.BL2_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL2_loading'))

        BL2_label3 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BL2_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL2_label4 = Label(self.segment_2, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BL2_label4.place(relx=0.2, rely=0.94, anchor=E)

        self.BL2_actual = Label(self.segment_2, text="{:.1f} V".format(self.actual_voltages['U_BL2_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.BL2_actual.place(relx=0.4, rely=0.94, anchor=E)


        #Bottom Right Loading Electrode GUI
        BR2_label1 = Label(self.segment_2, text='Bottom Right', font=font_16, bg = 'grey90', fg = 'black')
        BR2_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR2_label2 = Label(self.segment_2, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        BR2_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR2_entry = mySpinbox(self.segment_2, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR2_entry.delete(0,"end")
        self.BR2_entry.insert(0,int(round(self.entry_voltages['U_BR2_loading'],0)))
        self.BR2_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR2_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR2_loading'))
        self.BR2_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR2_loading'))

        BR2_label3 = Label(self.segment_2, text='V', font=font_14, bg = 'grey90', fg = 'black')
        BR2_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR2_label4 = Label(self.segment_2, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        BR2_label4.place(relx=0.7, rely=0.94, anchor=E)

        self.BR2_actual = Label(self.segment_2, text="{:.1f} V".format(self.actual_voltages['U_BR2_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.BR2_actual.place(relx=0.9, rely=0.94, anchor=E)


    def segment_3_controls(self, x, y):    
        self.segment_3 = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.segment_3.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.segment_3, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        segment3Label = Label(self.segment_3, text = 'Segment 3', font = font_18, bg = 'grey90', fg = 'black')
        segment3Label.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.segment_3_button = Button(self.segment_3, image=self.power_button, command=lambda: self.click_button(self.segment_3_button, 'power', 'U_segment_3'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.segment_3_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_segment_3_label1 = Label(self.segment_3, text='U', font=font_14, bg = 'grey90', fg = 'black', width=1)
        U_segment_3_label1.place(relx=0.22, rely=0.2, anchor=E)
        U_segment_3_label2 = Label(self.segment_3, text='S3', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_3_label2.place(relx=0.22, rely=0.23, anchor=W)

        U_segment_3_label3 = Label(self.segment_3, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_3_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_segment_3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.U_segment_3_entry.delete(0,"end")
        self.U_segment_3_entry.insert(0,int(round(self.U_segment_3,0)))
        self.U_segment_3_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_segment_3_entry.bind("<Return>", lambda eff: self.updateEntryV('U_segment_3'))
        self.U_segment_3_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_segment_3'))

        U_segment_3_label4 = Label(self.segment_3, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_3_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        U_segment_3_label5 = Label(self.segment_3, text='dU', font=font_14, bg = 'grey90', fg = 'black', width=2)
        U_segment_3_label5.place(relx=0.22, rely=0.3, anchor=E)
        U_segment_3_label6 = Label(self.segment_3, text='S3', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_3_label6.place(relx=0.22, rely=0.33, anchor=W)

        U_segment_3_label7 = Label(self.segment_3, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_3_label7.place(relx=0.31, rely=0.3, anchor=E)

        self.dU_segment_3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.dU_segment_3_entry.delete(0,"end")
        self.dU_segment_3_entry.insert(0,int(round(self.dU_segment_3,0)))
        self.dU_segment_3_entry.place(relx=0.31, rely=0.3, anchor=W, width=70)
        self.dU_segment_3_entry.bind("<Return>", lambda eff: self.updateEntryV('dU_segment_3'))
        self.dU_segment_3_entry.bind("<Tab>", lambda eff: self.updateEntryV('dU_segment_3'))

        U_segment_3_label8 = Label(self.segment_3, text='V', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_3_label8.place(relx=0.51, rely=0.3, anchor=CENTER)

        #Creates the bender operation mode button
        self.segment_3_mode_button = Button(self.segment_3, text='Operate Poles\nSeparately', relief = 'raised', command=lambda: self.click_button(self.segment_3_mode_button, 'mode', 'segment_3_mode'), width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        self.segment_3_mode_button.place(relx=0.75, rely=0.25, anchor=CENTER)


        #Top Left Loading Electrode GUI
        TL3_label1 = Label(self.segment_3, text='Top Left', font=font_16, bg = 'grey90', fg = 'black')
        TL3_label1.place(relx=0.25, rely=0.45, anchor=CENTER)

        TL3_label2 = Label(self.segment_3, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TL3_label2.place(relx=0.17, rely=0.55, anchor=E)

        self.TL3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL3_entry.delete(0,"end")
        self.TL3_entry.insert(0,int(round(self.entry_voltages['U_TL3_loading'],0)))
        self.TL3_entry.place(relx=0.17, rely=0.55, anchor=W, width=70)
        self.TL3_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL3_loading'))
        self.TL3_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL3_loading'))

        TL3_label3 = Label(self.segment_3, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TL3_label3.place(relx=0.37, rely=0.55, anchor=CENTER)

        TL3_label4 = Label(self.segment_3, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TL3_label4.place(relx=0.2, rely=0.64, anchor=E)

        self.TL3_actual = Label(self.segment_3, text="{:.1f} V".format(self.actual_voltages['U_TL3_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TL3_actual.place(relx=0.4, rely=0.64, anchor=E)


        #Top Right Loading Electrode GUI
        TR3_label1 = Label(self.segment_3, text='Top Right', font=font_16, bg = 'grey90', fg = 'black')
        TR3_label1.place(relx=0.75, rely=0.45, anchor=CENTER)

        TR3_label2 = Label(self.segment_3, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        TR3_label2.place(relx=0.67, rely=0.55, anchor=E)

        self.TR3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR3_entry.delete(0,"end")
        self.TR3_entry.insert(0,int(round(self.entry_voltages['U_TR3_loading'],0)))
        self.TR3_entry.place(relx=0.67, rely=0.55, anchor=W, width=70)
        self.TR3_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR3_loading'))
        self.TR3_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR3_loading'))

        TR3_label3 = Label(self.segment_3, text='V', font=font_14, bg = 'grey90', fg = 'black')
        TR3_label3.place(relx=0.87, rely=0.55, anchor=CENTER)

        TR3_label4 = Label(self.segment_3, text='Actual:', font=font_14, bg = 'grey90', fg = 'black')
        TR3_label4.place(relx=0.7, rely=0.64, anchor=E)

        self.TR3_actual = Label(self.segment_3, text="{:.1f} V".format(self.actual_voltages['U_TR3_loading']), font=font_14, bg = 'grey90', fg = 'black')
        self.TR3_actual.place(relx=0.9, rely=0.64, anchor=E)

        #Bottom Left Loading Electrode GUI
        BL3_label1 = Label(self.segment_3, text='Bottom Left', font=font_16, bg='grey90', fg='black')
        BL3_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL3_label2 = Label(self.segment_3, text='Set:', font=font_14, bg='grey90', fg='black')
        BL3_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL3_entry.delete(0, "end")
        self.BL3_entry.insert(0, int(round(self.entry_voltages['U_BL3_loading'], 0)))
        self.BL3_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL3_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL3_loading'))
        self.BL3_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL3_loading'))

        BL3_label3 = Label(self.segment_3, text='V', font=font_14, bg='grey90', fg='black')
        BL3_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL3_label4 = Label(self.segment_3, text='Actual:', font=font_14, bg='grey90', fg='black')
        BL3_label4.place(relx=0.2, rely=0.94, anchor=E)

        self.BL3_actual = Label(self.segment_3, text="{:.1f} V".format(self.actual_voltages['U_BL3_loading']), font=font_14, bg='grey90', fg='black')
        self.BL3_actual.place(relx=0.4, rely=0.94, anchor=E)

        #Bottom Right Loading Electrode GUI
        BR3_label1 = Label(self.segment_3, text='Bottom Right', font=font_16, bg='grey90', fg='black')
        BR3_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR3_label2 = Label(self.segment_3, text='Set:', font=font_14, bg='grey90', fg='black')
        BR3_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR3_entry = mySpinbox(self.segment_3, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR3_entry.delete(0, "end")
        self.BR3_entry.insert(0, int(round(self.entry_voltages['U_BR3_loading'], 0)))
        self.BR3_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR3_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR3_loading'))
        self.BR3_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR3_loading'))

        BR3_label3 = Label(self.segment_3, text='V', font=font_14, bg='grey90', fg='black')
        BR3_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR3_label4 = Label(self.segment_3, text='Actual:', font=font_14, bg='grey90', fg='black')
        BR3_label4.place(relx=0.7, rely=0.94, anchor=E)

        self.BR3_actual = Label(self.segment_3, text="{:.1f} V".format(self.actual_voltages['U_BR3_loading']), font=font_14, bg='grey90', fg='black')
        self.BR3_actual.place(relx=0.9, rely=0.94, anchor=E)

    def segment_4_controls(self, x, y):    
        self.segment_4 = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.segment_4.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.segment_4, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        segment4Label = Label(self.segment_4, text = 'Segment 4', font = font_18, bg = 'grey90', fg = 'black')
        segment4Label.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.segment_4_button = Button(self.segment_4, image=self.power_button, command=lambda: self.click_button(self.segment_4_button, 'power', 'U_segment_4'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.segment_4_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_segment_4_label1 = Label(self.segment_4, text='U', font=font_14, bg = 'grey90', fg = 'black', width=1)
        U_segment_4_label1.place(relx=0.22, rely=0.2, anchor=E)
        U_segment_4_label2 = Label(self.segment_4, text='S4', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_4_label2.place(relx=0.22, rely=0.23, anchor=W)

        U_segment_4_label3 = Label(self.segment_4, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_4_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_segment_4_entry = Entry(self.segment_4, font=font_14, justify=RIGHT)
        self.U_segment_4_entry.delete(0, "end")
        self.U_segment_4_entry.insert(0, int(round(self.U_segment_4, 0)))
        self.U_segment_4_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_segment_4_entry.bind("<Return>", lambda eff: self.updateEntryV('U_segment_4'))
        self.U_segment_4_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_segment_4'))

        U_segment_4_label4 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        U_segment_4_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        U_segment_4_label5 = Label(self.segment_4, text='dU', font=font_14, bg='grey90', fg='black', width=2)
        U_segment_4_label5.place(relx=0.22, rely=0.3, anchor=E)
        U_segment_4_label6 = Label(self.segment_4, text='S4', font=('Helvetica', 8), bg='grey90', fg='black', width=2)
        U_segment_4_label6.place(relx=0.22, rely=0.33, anchor=W)

        U_segment_4_label7 = Label(self.segment_4, text='=', font=font_14, bg='grey90', fg='black')
        U_segment_4_label7.place(relx=0.31, rely=0.3, anchor=E)
        
        self.dU_segment_4_entry = Entry(self.segment_4, font=font_14, justify=RIGHT)
        self.dU_segment_4_entry.delete(0, "end")
        self.dU_segment_4_entry.insert(0, int(round(self.dU_segment_4, 0)))
        self.dU_segment_4_entry.place(relx=0.31, rely=0.3, anchor=W, width=70)
        self.dU_segment_4_entry.bind("<Return>", lambda eff: self.updateEntryV('dU_segment_4'))
        self.dU_segment_4_entry.bind("<Tab>", lambda eff: self.updateEntryV('dU_segment_4'))

        U_segment_4_label8 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        U_segment_4_label8.place(relx=0.51, rely=0.3, anchor=CENTER)

        # Creates the bender operation mode button
        segment_4_mode_button = Button(self.segment_4, text='Operate Poles\nSeparately', relief='raised',
                           command=lambda: self.click_button(segment_4_mode_button, 'mode', 'segment_4_mode'),
                           width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        segment_4_mode_button.place(relx=0.75, rely=0.25, anchor=CENTER)

        # Top Left Loading Electrode GUI
        TL4_label1 = Label(self.segment_4, text='Top Left', font=font_16, bg='grey90', fg='black')
        TL4_label1.place(relx=0.25, rely=0.45, anchor=CENTER)

        TL4_label2 = Label(self.segment_4, text='Set:', font=font_14, bg='grey90', fg='black')
        TL4_label2.place(relx=0.17, rely=0.55, anchor=E)

        self.TL4_entry = mySpinbox(self.segment_4, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL4_entry.delete(0, "end")
        self.TL4_entry.insert(0, int(round(self.entry_voltages['U_TL4_loading'], 0)))
        self.TL4_entry.place(relx=0.17, rely=0.55, anchor=W, width=70)
        self.TL4_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL4_loading'))
        self.TL4_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL4_loading'))

        TL4_label3 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        TL4_label3.place(relx=0.37, rely=0.55, anchor=CENTER)

        TL4_label4 = Label(self.segment_4, text='Actual:', font=font_14, bg='grey90', fg='black')
        TL4_label4.place(relx=0.2, rely=0.64, anchor=E)

        self.TL4_actual = Label(self.segment_4, text="{:.1f} V".format(self.actual_voltages['U_TL4_loading']),
                   font=font_14, bg='grey90', fg='black')
        self.TL4_actual.place(relx=0.4, rely=0.64, anchor=E)

        # Top Right Loading Electrode GUI
        TR4_label1 = Label(self.segment_4, text='Top Right', font=font_16, bg='grey90', fg='black')
        TR4_label1.place(relx=0.75, rely=0.45, anchor=CENTER)

        TR4_label2 = Label(self.segment_4, text='Set:', font=font_14, bg='grey90', fg='black')
        TR4_label2.place(relx=0.67, rely=0.55, anchor=E)

        self.TR4_entry = mySpinbox(self.segment_4, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR4_entry.delete(0, "end")
        self.TR4_entry.insert(0, int(round(self.entry_voltages['U_TR4_loading'], 0)))
        self.TR4_entry.place(relx=0.67, rely=0.55, anchor=W, width=70)
        self.TR4_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR4_loading'))
        self.TR4_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR4_loading'))

        TR4_label3 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        TR4_label3.place(relx=0.87, rely=0.55, anchor=CENTER)

        TR4_label4 = Label(self.segment_4, text='Actual:', font=font_14, bg='grey90', fg='black')
        TR4_label4.place(relx=0.7, rely=0.64, anchor=E)

        self.TR4_actual = Label(self.segment_4, text="{:.1f} V".format(self.actual_voltages['U_TR4_loading']),
                   font=font_14, bg='grey90', fg='black')
        self.TR4_actual.place(relx=0.9, rely=0.64, anchor=E)

        # Bottom Left Loading Electrode GUI
        BL4_label1 = Label(self.segment_4, text='Bottom Left', font=font_16, bg='grey90', fg='black')
        BL4_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL4_label2 = Label(self.segment_4, text='Set:', font=font_14, bg='grey90', fg='black')
        BL4_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL4_entry = mySpinbox(self.segment_4, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL4_entry.delete(0, "end")
        self.BL4_entry.insert(0, int(round(self.entry_voltages['U_BL4_loading'], 0)))
        self.BL4_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL4_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL4_loading'))
        self.BL4_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL4_loading'))

        BL4_label3 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        BL4_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL4_label4 = Label(self.segment_4, text='Actual:', font=font_14, bg='grey90', fg='black')
        BL4_label4.place(relx=0.2, rely=0.94, anchor=E)

        self.BL4_actual = Label(self.segment_4, text="{:.1f} V".format(self.actual_voltages['U_BL4_loading']),
                   font=font_14, bg='grey90', fg='black')
        self.BL4_actual.place(relx=0.4, rely=0.94, anchor=E)

        # Bottom Right Loading Electrode GUI
        BR4_label1 = Label(self.segment_4, text='Bottom Right', font=font_16, bg='grey90', fg='black')
        BR4_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR4_label2 = Label(self.segment_4, text='Set:', font=font_14, bg='grey90', fg='black')
        BR4_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR4_entry = mySpinbox(self.segment_4, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR4_entry.delete(0, "end")
        self.BR4_entry.insert(0, int(round(self.entry_voltages['U_BR4_loading'], 0)))
        self.BR4_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR4_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR4_loading'))
        self.BR4_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR4_loading'))

        BR4_label3 = Label(self.segment_4, text='V', font=font_14, bg='grey90', fg='black')
        BR4_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR4_label4 = Label(self.segment_4, text='Actual:', font=font_14, bg='grey90', fg='black')
        BR4_label4.place(relx=0.7, rely=0.94, anchor=E)

        self.BR4_actual = Label(self.segment_4, text="{:.1f} V".format(self.actual_voltages['U_BR4_loading']),
                   font=font_14, bg='grey90', fg='black')
        self.BR4_actual.place(relx=0.9, rely=0.94, anchor=E)


    def segment_5_controls(self, x, y):    
        self.segment_5 = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.segment_5.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.segment_5, width=390, height=340, bg='grey90', highlightthickness=0)
        w.create_line(0, 101, 390, 101)
        w.create_line(10, 225, 380, 225, dash = (3,2))
        w.create_line(195, 111, 195, 335, dash = (3, 2))
        w.place(relx=0.5,rely=0.55,anchor=CENTER)

        segment5Label = Label(self.segment_5, text = 'Segment 5', font = font_18, bg = 'grey90', fg = 'black')
        segment5Label.place(relx=0.5, rely=0.08, anchor = CENTER)

        #Creates bender power button
        self.segment_5_button = Button(self.segment_5, image=self.power_button, command=lambda: self.click_button(self.segment_5_button, 'power', 'U_segment_5'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.segment_5_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        U_segment_5_label1 = Label(self.segment_5, text='U', font=font_14, bg = 'grey90', fg = 'black', width=1)
        U_segment_5_label1.place(relx=0.22, rely=0.2, anchor=E)
        U_segment_5_label2 = Label(self.segment_5, text='S5', font=('Helvetica', 8), bg = 'grey90', fg = 'black', width=2)
        U_segment_5_label2.place(relx=0.22, rely=0.23, anchor=W)

        U_segment_5_label3 = Label(self.segment_5, text='=', font=font_14, bg = 'grey90', fg = 'black')
        U_segment_5_label3.place(relx=0.31, rely=0.2, anchor=E)

        self.U_segment_5_entry = Entry(self.segment_5, font=font_14, justify=RIGHT)
        self.U_segment_5_entry.delete(0, "end")
        self.U_segment_5_entry.insert(0, int(round(self.U_segment_5, 0)))
        self.U_segment_5_entry.place(relx=0.31, rely=0.2, anchor=W, width=70)
        self.U_segment_5_entry.bind("<Return>", lambda eff: self.updateEntryV('U_segment_5'))
        self.U_segment_5_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_segment_5'))

        U_segment_5_label4 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        U_segment_5_label4.place(relx=0.51, rely=0.2, anchor=CENTER)

        U_segment_5_label5 = Label(self.segment_5, text='dU', font=font_14, bg='grey90', fg='black', width=2)
        U_segment_5_label5.place(relx=0.22, rely=0.3, anchor=E)
        U_segment_5_label6 = Label(self.segment_5, text='S5', font=('Helvetica', 8), bg='grey90', fg='black', width=2)
        U_segment_5_label6.place(relx=0.22, rely=0.33, anchor=W)

        U_segment_5_label7 = Label(self.segment_5, text='=', font=font_14, bg='grey90', fg='black')
        U_segment_5_label7.place(relx=0.31, rely=0.3, anchor=E)

        self.dU_segment_5_entry = Entry(self.segment_5, font=font_14, justify=RIGHT)
        self.dU_segment_5_entry.delete(0, "end")
        self.dU_segment_5_entry.insert(0, int(round(self.dU_segment_5, 0)))
        self.dU_segment_5_entry.place(relx=0.31, rely=0.3, anchor=W, width=70)
        self.dU_segment_5_entry.bind("<Return>", lambda eff: self.updateEntryV('dU_segment_5'))
        self.dU_segment_5_entry.bind("<Tab>", lambda eff: self.updateEntryV('dU_segment_5'))

        U_segment_5_label8 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        U_segment_5_label8.place(relx=0.51, rely=0.3, anchor=CENTER)

        # Creates the bender operation mode button
        segment_5_mode_button = Button(self.segment_5, text='Operate Poles\nSeparately', relief='raised',
                   command=lambda: self.click_button(segment_5_mode_button, 'mode', 'segment_5_mode'),
                   width=15, borderwidth=1, bg='#1AA5F6', activebackground='#1AA5F6')
        segment_5_mode_button.place(relx=0.75, rely=0.25, anchor=CENTER)

        # Top Left Loading Electrode GUI
        TL5_label1 = Label(self.segment_5, text='Top Left', font=font_16, bg='grey90', fg='black')
        TL5_label1.place(relx=0.25, rely=0.45, anchor=CENTER)

        TL5_label2 = Label(self.segment_5, text='Set:', font=font_14, bg='grey90', fg='black')
        TL5_label2.place(relx=0.17, rely=0.55, anchor=E)

        self.TL5_entry = mySpinbox(self.segment_5, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TL5_entry.delete(0, "end")
        self.TL5_entry.insert(0, int(round(self.entry_voltages['U_TL5_loading'], 0)))
        self.TL5_entry.place(relx=0.17, rely=0.55, anchor=W, width=70)
        self.TL5_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TL5_loading'))
        self.TL5_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TL5_loading'))

        TL5_label3 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        TL5_label3.place(relx=0.37, rely=0.55, anchor=CENTER)

        TL5_label4 = Label(self.segment_5, text='Actual:', font=font_14, bg='grey90', fg='black')
        TL5_label4.place(relx=0.2, rely=0.64, anchor=E)

        self.TL5_actual = Label(self.segment_5, text="{:.1f} V".format(self.actual_voltages['U_TL5_loading']),
               font=font_14, bg='grey90', fg='black')
        self.TL5_actual.place(relx=0.4, rely=0.64, anchor=E)

        # Top Right Loading Electrode GUI
        TR5_label1 = Label(self.segment_5, text='Top Right', font=font_16, bg='grey90', fg='black')
        TR5_label1.place(relx=0.75, rely=0.45, anchor=CENTER)

        TR5_label2 = Label(self.segment_5, text='Set:', font=font_14, bg='grey90', fg='black')
        TR5_label2.place(relx=0.67, rely=0.55, anchor=E)

        self.TR5_entry = mySpinbox(self.segment_5, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.TR5_entry.delete(0, "end")
        self.TR5_entry.insert(0, int(round(self.entry_voltages['U_TR5_loading'], 0)))
        self.TR5_entry.place(relx=0.67, rely=0.55, anchor=W, width=70)
        self.TR5_entry.bind("<Return>", lambda eff: self.updateEntryV('U_TR5_loading'))
        self.TR5_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_TR5_loading'))

        TR5_label3 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        TR5_label3.place(relx=0.87, rely=0.55, anchor=CENTER)

        TR5_label4 = Label(self.segment_5, text='Actual:', font=font_14, bg='grey90', fg='black')
        TR5_label4.place(relx=0.7, rely=0.64, anchor=E)

        self.TR5_actual = Label(self.segment_5, text="{:.1f} V".format(self.actual_voltages['U_TR5_loading']),
               font=font_14, bg='grey90', fg='black')
        self.TR5_actual.place(relx=0.9, rely=0.64, anchor=E)

        # Bottom Left Loading Electrode GUI
        BL5_label1 = Label(self.segment_5, text='Bottom Left', font=font_16, bg='grey90', fg='black')
        BL5_label1.place(relx=0.25, rely=0.75, anchor=CENTER)

        BL5_label2 = Label(self.segment_5, text='Set:', font=font_14, bg='grey90', fg='black')
        BL5_label2.place(relx=0.17, rely=0.85, anchor=E)

        self.BL5_entry = mySpinbox(self.segment_5, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BL5_entry.delete(0, "end")
        self.BL5_entry.insert(0, int(round(self.entry_voltages['U_BL5_loading'], 0)))
        self.BL5_entry.place(relx=0.17, rely=0.85, anchor=W, width=70)
        self.BL5_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BL5_loading'))
        self.BL5_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BL5_loading'))

        BL5_label3 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        BL5_label3.place(relx=0.37, rely=0.85, anchor=CENTER)

        BL5_label4 = Label(self.segment_5, text='Actual:', font=font_14, bg='grey90', fg='black')
        BL5_label4.place(relx=0.2, rely=0.94, anchor=E)

        self.BL5_actual = Label(self.segment_5, text="{:.1f} V".format(self.actual_voltages['U_BL5_loading']),
               font=font_14, bg='grey90', fg='black')
        self.BL5_actual.place(relx=0.4, rely=0.94, anchor=E)

        # Bottom Right Loading Electrode GUI
        BR5_label1 = Label(self.segment_5, text='Bottom Right', font=font_16, bg='grey90', fg='black')
        BR5_label1.place(relx=0.75, rely=0.75, anchor=CENTER)

        BR5_label2 = Label(self.segment_5, text='Set:', font=font_14, bg='grey90', fg='black')
        BR5_label2.place(relx=0.67, rely=0.85, anchor=E)

        self.BR5_entry = mySpinbox(self.segment_5, from_=-500, to=500, font=font_14, justify=RIGHT)
        self.BR5_entry.delete(0, "end")
        self.BR5_entry.insert(0, int(round(self.entry_voltages['U_BR5_loading'], 0)))
        self.BR5_entry.place(relx=0.67, rely=0.85, anchor=W, width=70)
        self.BR5_entry.bind("<Return>", lambda eff: self.updateEntryV('U_BR5_loading'))
        self.BR5_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_BR5_loading'))

        BR5_label3 = Label(self.segment_5, text='V', font=font_14, bg='grey90', fg='black')
        BR5_label3.place(relx=0.87, rely=0.85, anchor=CENTER)

        BR5_label4 = Label(self.segment_5, text='Actual:', font=font_14, bg='grey90', fg='black')
        BR5_label4.place(relx=0.7, rely=0.94, anchor=E)

        self.BR5_actual = Label(self.segment_5, text="{:.1f} V".format(self.actual_voltages['U_BR5_loading']),
               font=font_14, bg='grey90', fg='black')
        self.BR5_actual.place(relx=0.9, rely=0.94, anchor=E)


    def loading_plate_controls(self, x, y):
        self.loading_plate = Frame(self.loading_tab, width = 400, height = 400, background = 'grey90', highlightbackground = 'black', highlightcolor = 'black', highlightthickness = 1)
        self.loading_plate.place(relx = x, rely = y, anchor = CENTER)

        #Canvas for creating divider lines between controls
        w = Canvas(self.loading_plate, width=390, height=390, bg='grey90', highlightthickness=0)
        w.create_line(0, 55, 390, 55)
        w.create_line(0, 167, 390, 167)
        w.create_line(0, 278, 390, 278)
        w.place(relx=0.5,rely=0.5,anchor=CENTER)

        loadingPlateLabel = Label(self.loading_plate, text = 'Miscellaneous', font = font_18, bg = 'grey90', fg = 'black')
        loadingPlateLabel.place(relx=0.5, rely=0.08, anchor = CENTER)

        # Creates the loading plate power button
        self.loading_plate_button = Button(self.loading_plate, image=self.power_button, command=lambda: self.click_button(self.loading_plate_button, 'power', 'U_loading_plate'), borderwidth=0, bg='grey90', activebackground='grey90')
        self.loading_plate_button.place(relx=0.1, rely=0.08, anchor=CENTER)

        # Creates the loading exit plate title
        exitPlateLabel = Label(self.loading_plate, text = 'Loading Exit Plate', font = font_18, bg = 'grey90', fg = 'black')
        exitPlateLabel.place(relx=0.5, rely=0.2, anchor = CENTER)

        U_loading_plate_label3 = Label(self.loading_plate, text='Set:', font=font_14, bg = 'grey90', fg = 'black')
        U_loading_plate_label3.place(relx=0.15, rely=0.32, anchor=E)

        self.U_exit_loading_entry = Entry(self.loading_plate, font=font_14, justify=RIGHT)
        self.U_exit_loading_entry.delete(0, "end")
        self.U_exit_loading_entry.insert(0,int(round(self.entry_voltages['U_exit_loading'],0)))
        self.U_exit_loading_entry.place(relx=0.15, rely=0.32, anchor=W, width=70)
        self.U_exit_loading_entry.bind("<Return>", lambda eff: self.updateEntryV('U_exit_loading'))
        self.U_exit_loading_entry.bind("<Tab>", lambda eff: self.updateEntryV('U_exit_loading'))

        U_loading_plate_label4 = Label(self.loading_plate, text='V', font=font_14, bg='grey90', fg='black')
        U_loading_plate_label4.place(relx=0.35, rely=0.32, anchor=CENTER)

        U_loading_plate_label5 = Label(self.loading_plate, text='Actual:', font=font_14, bg='grey90', fg='black')
        U_loading_plate_label5.place(relx=0.65, rely=0.32, anchor=E)

        self.U_exit_loading_actual = Label(self.loading_plate, text="{:.1f} V".format(self.actual_voltages['U_exit_loading']), font=font_14, bg='grey90', fg='black')
        self.U_exit_loading_actual.place(relx=0.85, rely=0.32, anchor=E)



    #Creates the main GUI window
    def makeGui(self, root=None):
        if root == None:
            self.root = Tk()
            #tksupport.install(self.root)
        else:
            self.root = root

        menu = Menu(self.root)
        self.root.config(menu=menu)

        self.root.title("Thorium Control Center")
        self.root.geometry("1920x1050")
        self.root.configure(bg='white')
        self.root.protocol("WM_DELETE_WINDOW", self.quitProgram)
        if platform.system() == 'Windows':
            try:
                self.root.iconbitmap("icons/TCI.ico")
            except TclError:
                print('Program started remotely by another program...')
                self.root.iconbitmap("C:/Users/Dirac/code/thorium\control/clients/Thorium-Control-Interface-main/icons/TCI.ico")

        try:
            image = Image.open('images/power-button.png')
        except:
            image = Image.open('C:/Users/Dirac/code/thorium\control/clients/Thorium-Control-Interface-main/images/power-button.png')
        image = image.resize((30,32))
        self.power_button = ImageTk.PhotoImage(image)

        self.createMenus(menu)
        self.createTabs()

        self.quad_bender_controls(0.4, 0.245)

        self.extraction_controls(0.15, 0.295)

        self.segment_1_controls(0.15, 0.245)
        self.segment_2_controls(0.4, 0.245)
        self.segment_3_controls(0.65, 0.245)
        self.segment_4_controls(0.15, 0.7)
        self.segment_5_controls(0.4, 0.7)

        self.loading_plate_controls(0.65, 0.7)



        #multiThreading(self.data_reader_no_yield)
        #self.connect_no_yield()
        self.root.mainloop()
        #self.reactor.run()          #This line replaces self.root.mainloop() when using Tkinter with Twisted

        


# if __name__ == '__main__':
#     root = Tk()
#     tksupport.install(root)
#     app = Thorium(reactor)
#     app.makeGui(root)

#Initializes the program
if __name__ == '__main__':
    instance = Thorium()
    instance.makeGui()
