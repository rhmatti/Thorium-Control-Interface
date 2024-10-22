from Thorium_Control_Interface import *

supply1_port = 'COM15'      # COM port for the HV500 power supply labeled "Supply 1" (previously labeled "Loading")
supply2_port = 'COM16'      # COM port for the HV500 power supply labeled "Supply 2" (previously labeled "Bender")

#Initializes the program
if __name__ == '__main__':
    instance = Thorium()
    instance.connect(supply1_port, supply2_port)
    instance.makeGui()
    