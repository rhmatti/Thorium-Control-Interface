import serial
import serial.tools.list_ports
import numpy as np
import time

print('Available ports:')
print([comport.device for comport in serial.tools.list_ports.comports()])


#Attempts to establish a serial connection to the specified port
def establishConnection(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1, bytesize=serial.EIGHTBITS, parity='N', stopbits=serial.STOPBITS_ONE)
        return ser
    except:
        print('Could not establish connection to specified port')

class HV500Server():
    """Serial server for the HV500-16 low noise voltage supply."""

    def __init__(self):
        self.baudrate = 9600
        self.port = None
        self.ser = None
        self.vmax = 500
        self.IDN = None
        self.spans = None
        self.offsets = None

    def initServer(self):
        if self.port == None:
            print('No port specified')
            print('Available ports:')
            print([comport.device for comport in serial.tools.list_ports.comports()])
        else:
            self.ser = establishConnection(self.port, self.baudrate)
            self.get_ID()
            print(f'IDN: {self.IDN}')
            self.get_calibration(0)

    def channel_to_str(self, channel):
        _channel = str(channel)
        if len(_channel) > 1:
            return _channel
        else:
            return "0" + _channel 

    def voltage_to_kw(self, v):
        x = v/(2*self.vmax)+0.5
        return f'{x:.6f}'

    def voltage_to_hex(self, v, ch):
        x = v/(2*self.vmax)+0.5
        DAC = int(x*self.spans[ch]*62500 + self.offsets[ch]*65535)
        return f'{DAC:0x}'.upper()
    
    def voltages_to_hex(self, voltages):
        x = voltages/(2*self.vmax)+0.5
        DAC = (x*self.spans*62500 + self.offsets*65535).astype(int)
        DAC = np.array([f'{entry:0x}'.upper() for entry in DAC])
        DAC = ''.join(DAC)
        return DAC

    def get_ID(self):
        """
        Returns device identification number e.g. 'HV264 500 16 b'.
        First string 'HV264' is the IDN necessary to address device.
        """
        self.ser.write(b'IDN\r')
        response = self.ser.readline()
        print(response)
        self.IDN = repr(response).split(' ')[0].split("'")[1]

    def get_voltage(self, channel):
        """
        Disclaimer: reading is digitized to 10s of mV.

        Args:
            channel: int, channel between 1 and 16.

        Returns:
            float, voltage in volts.
        """
        ch_str = self.channel_to_str(channel)
        packet = f'{self.IDN} U{ch_str}\r'
        self.ser.write(packet.encode())
        response = self.ser.readline().decode().split('V')[0]

        # exception to catch serial overload
        if response != '':
            return float(response)
        else:
            return 99999 # will not update client

    def set_voltage_legacy(self, channel, voltage):
        """
        Sets voltage on the specified channel using the legacy command. 
        According to the manual, this 'CH' command should be used in combination with the 'DIS AUTO' command where a faster response from the device is required.
        Otherwise, the new 'SET' command should be used (i.e. set_voltage).

        Args:
            channel: int, channel between 1 and 16.
            voltage: float, voltage in volts.
        """
        if voltage > self.vmax or voltage < -self.vmax:
            raise ValueError("Voltage setpoint out of bounds.")
        else:
            ch_str = self.channel_to_str(channel)
            volt_str = self.voltage_to_kw(voltage)
            packet = f'{self.IDN} CH{ch_str} {volt_str}\r'
            self.ser.write(packet.encode())
            if self.ser.read(2) != b'\x06\r':
                print('Command not accepted')
    
    def set_voltage(self, channel, voltage):
        """
        Sets voltage on the specified channel.

        Args:
            channel: int, channel between 1 and 16.
            voltage: float, voltage in volts.
        """
        if voltage > self.vmax or voltage < -self.vmax:
            raise ValueError("Voltage setpoint out of bounds.")
        else:
            ch_str = self.channel_to_str(channel)
            packet = f'{self.IDN} SET{ch_str} {voltage}\r'
            self.ser.write(packet.encode())

            # Commented out this check because it costs 1 second to read back the 'ACK'
            if self.ser.read(2) != b'\x06\r':
                print('Command not accepted')

    def get_calibration(self, channel):
        """
        Gets calibration on the specified channel as "span +/-offset".

        Args:
            channel: int, channel between 1 and 16.
        """
        ch_str = self.channel_to_str(channel)
        packet = f'{self.IDN} RCORR{ch_str}\r'
        self.ser.write(packet.encode())
        response = self.ser.readline().decode().split(',')
        self.spans = []
        self.offsets = []
        for entry in response:
            self.spans.append(float(entry.split(' ')[0]))
            self.offsets.append(float(entry.split(' ')[1]))
        self.spans = np.array(self.spans)
        self.offsets = np.array(self.offsets)

    def set_all_voltages(self,voltages):
        """
        Sets all voltages quickly.

        Args:
            voltages: array of floats, voltages in volts.
        """
        mask = np.abs(voltages) > self.vmax
        if np.any(mask):
            raise ValueError("Voltage setpoint out of bounds.")
        else:
            voltage_str = self.voltages_to_hex(voltages)
        
        packet = f'{self.IDN} A {voltage_str}\r'

        self.ser.write(packet.encode())

        # Commented out this check because it costs 1 second to read back the 'ACK'
        if self.ser.read(2) != b'\x06\r':
            print('Command not accepted')

    def get_all_voltages(self):
        """
        Gets all voltages quickly.

        Returns:
            voltages: array of floats, voltages in volts.
        """
        packet = f'{self.IDN} U00\r'
        self.ser.write(packet.encode())
        reading = self.ser.readline()
        voltages = reading.decode().split(",")
        for i in range(0,len(voltages)):
            voltages[i] = float(voltages[i].split("V")[0])
        return voltages


if __name__ == "__main__":
    server1 = HV500Server()
    server1.port = "COM15"
    server1.initServer()
    server2 = HV500Server()
    server2.port = "COM16"
    server2.initServer()

    #voltages = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
    voltages = np.zeros(16)
    voltages = np.array([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
    voltages = np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
    t0 = time.time()
    server1.set_voltage(13, 3)
    server2.set_all_voltages(voltages)
    print(server2.get_all_voltages())
    # server1.set_voltage(1, 3.14)
    print(f'Elapsed time: {time.time()-t0}')
    # print(server1.get_voltage(1))