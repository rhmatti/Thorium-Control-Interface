#Thorium Control Interface
#Author: Richard Mattish
#Last Updated: 02/01/2024


#Function:  This program provides a graphical user interface for setting
#           and monitoring trap electrode voltages for the Thorium Project


#Import General Tools
import sys
import os
import platform
import time
from turtle import bgcolor
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
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import scipy as sp
from decimal import Decimal

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

#Initializes the program
def startProgram(root=None, reactor=None):
    instance = Thorium()
    #instance.connect_no_yield()
    instance.makeGui(root)
    #instance.reactor.run()


#This is the EBIT class object, which contains everything related to the GUI control interface
class Thorium:
    def __init__(self, reactor=None):

        #Dictionary which will store actual voltages of bender electrodes, as read from server
        #All voltages are initialized as zero upon program start, but will be read by data reader
        self.actual_voltages = {"U_TR_bender":0, 
                           "U_TL_bender":0, 
                           "U_BL_bender":0, 
                           "U_BR_bender":0, 
                           "U_TL_plate":0,
                           "U_TR_plate":0, 
                           "U_BL_plate":0, 
                           "U_BR_plate":0, 
                           "U_L_ablation":0, 
                           "U_R_ablation":0}
        

        #Dictionary which will store set voltages of bender electrodes, as specified by user in program
        #All set voltages are initialized as zero upon program start
        self.set_voltages = {"U_TR_bender":0, 
                           "U_TL_bender":0, 
                           "U_BL_bender":0, 
                           "U_BR_bender":0, 
                           "U_TL_plate":0,
                           "U_TR_plate":0, 
                           "U_BL_plate":0, 
                           "U_BR_plate":0, 
                           "U_L_ablation":0, 
                           "U_R_ablation":0}
        

        #Dictionary which will store voltages that user has typed into entry boxes
        #These are not necessarily the same as set voltages, since power buttons, etc. may be switched
        self.entry_voltages = {"U_TR_bender":0, 
                           "U_TL_bender":0, 
                           "U_BL_bender":0, 
                           "U_BR_bender":0, 
                           "U_TL_plate":0,
                           "U_TR_plate":0, 
                           "U_BL_plate":0, 
                           "U_BR_plate":0, 
                           "U_L_ablation":0, 
                           "U_R_ablation":0}

        #Location (server, channel) of electrode voltages on power supplies
        self.v_location = {"U_TR_bender":("b", 15), 
                           "U_TL_bender":("b", 12), 
                           "U_BL_bender":("b", 13), 
                           "U_BR_bender":("l", 15), 
                           "U_TL_plate":("l", 14),
                           "U_TR_plate":("b", 16), 
                           "U_BL_plate":("l", 16), 
                           "U_BR_plate":("l", 12), 
                           "U_L_ablation":("l", 13), 
                           "U_R_ablation":("b", 14)}
        

        self.U_bender = 0
        
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


    def data_reader_no_yield(self):

        self.connect_no_yield()

        while True:
            self.updateSetV()

            for v in self.v_location:
                self.actual_voltages[v] = self.getVoltage(v)

                print(f'{v} = {self.actual_voltages[v]}')

                if abs(self.actual_voltages[v] - self.set_voltages[v]) > 0.2:
                    self.setVoltage(v)

                self.updateActualV(v)
        
            time.sleep(0.1)


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


    def updateSetV(self):
        quad_names = ['U_TL_bender', 'U_TR_bender', 'U_BL_bender', 'U_BR_bender']
        extraction_names = ['U_TL_plate', 'U_TR_plate', 'U_BL_plate', 'U_BR_plate', 'U_L_ablation', 'U_L_ablation']

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

        if self.U_extraction_bool:
            for name in extraction_names:
                self.set_voltages[name] = self.entry_voltages[name]
        else:
            for name in extraction_names:
                self.set_voltages[name] = 0



    def click_button(self, button, type, variable, text=None):
        if type == 'power':
            self.update_button_var(variable, True)
            button.config(bg='#50E24B', command=lambda: self.declick_button(button, type, variable), activebackground='#50E24B')

        elif type == 'mode':
            self.update_button_var(variable, True)
            button.config(bg='#50E24B', text='Operate Poles\nTogether', command=lambda: self.declick_button(button, type, variable, text), activebackground='#50E24B')




    def declick_button(self, button, type, variable, text=None):
        self.update_button_var(variable, False)
        if type == 'power':
            button.config(bg='grey90', command=lambda: self.click_button(button, type, variable), activebackground='grey90')
        elif type == 'mode':
            button.config(bg='#1AA5F6', text='Operate Poles\nSeparately', command=lambda: self.click_button(button, type, variable, text), activebackground='#1AA5F6')

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
    
    #Opens About Window with description of software
    def About(self):
        name = "Thorium Control Center"
        version = 'Version: 1.0.0'
        date = 'Date: 02/01/2024'
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
                print('No icons will be used')

        try:
            image = Image.open('images/power-button.png')
        except:
            image = Image.open('C:/Users/Dirac/Downloads/Thorium-Control-Interface-main/images/power-button.png')
        image = image.resize((30,32))
        self.power_button = ImageTk.PhotoImage(image)

        self.createMenus(menu)
        self.createTabs()

        self.quad_bender_controls(0.4, 0.245)

        self.extraction_controls(0.15, 0.295)

        multiThreading(self.data_reader_no_yield)
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
        
#startProgram()
