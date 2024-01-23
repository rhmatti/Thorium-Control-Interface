#Thorium Trap Controls
#Author: Richard Mattish
#Last Updated: 01/23/2024


#Function:  This program provides a graphical user interface for setting
#           and monitoring trap electrode voltages for the Thorium Project.


#Import General Tools
import sys
import os
import platform
import time
from turtle import bgcolor
import webbrowser
import threading

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
def startProgram(root=None):
    instance = Thorium()
    instance.makeGui(root)


#This is the EBIT class object, which contains everything related to the GUI control interface
class Thorium:
    def __init__(self):

        #Defines global variables
        self.canvas = None
        self.fig = None
        self.ax = None
        self.toolbar = None
        self.filename = None
        self.work_dir = None

    
    def quitProgram(self):
        print('quit')
        self.root.quit()
        self.root.destroy()
    
    #Opens About Window with description of software
    def About(self):
        name = "Thorium Control Center"
        version = 'Version: 1.0.0'
        date = 'Date: 01/23/2024'
        support = 'Support: '
        url = 'https://github.com/rhmatti/CUEBIT-Control-Interface'
        copyrightMessage ='Copyright © 2023 Richard Mattish All Rights Reserved.'
        t = Toplevel(self.root)
        t.wm_title("About")
        t.geometry("400x300")
        t.resizable(False, False)
        t.configure(background='white')
        if platform.system() == 'Windows':
            try:
                t.iconbitmap("icons/CSA.ico")
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
        l5 = Label(t, text = 'https://github.com/rhmatti/\nCUEBIT-Control-Interface', bg = 'white', fg = 'blue', font=font_12)
        l5.place(relx = 0.31, rely=0.48, anchor = W)
        l5.bind("<Button-1>", lambda e:
        callback(url))
        messageVar = Message(t, text = copyrightMessage, bg='white', font = font_12, width = 600)
        messageVar.place(relx = 0.5, rely = 1, anchor = S)


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
        self.operation_tab = ttk.Frame(self.tabControl)
        self.source_tab = ttk.Frame(self.tabControl)
        self.slit_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.operation_tab, text='Bender')
        self.tabControl.add(self.source_tab, text='Loading Trap')
        self.tabControl.add(self.slit_tab, text='Precision Trap')
        self.tabControl.pack(expand=1, fill='both')
        #self.tabControl.place(relx=0.5, rely=0, anchor=N)


    def makeGui(self, root=None):
        if root == None:
            self.root = Tk()
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
                self.root.iconbitmap("icons/CSA.ico")
            except TclError:
                print('Program started remotely by another program...')
                print('No icons will be used')

        try:
            image = Image.open('images/power-button.png')
        except:
            image = Image.open('C:/Users/cuebit-control/Downloads/CUEBIT-Control-Interface-main/images/power-button.png')
        image = image.resize((30,32))
        self.power_button = ImageTk.PhotoImage(image)

        self.createMenus(menu)
        self.createTabs()

        #multiThreading(self.data_reader)
        self.root.mainloop()


startProgram()