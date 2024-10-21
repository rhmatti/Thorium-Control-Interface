import serial
import serial.tools.list_ports

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
        self.vlim = 500
        self.IDN = None

    def initServer(self):
        if self.port == None:
            print('No port specified')
            print('Available ports:')
            print([comport.device for comport in serial.tools.list_ports.comports()])
        else:
            self.ser = establishConnection(self.port, self.baudrate)
            self.IDN = self.get_ID()
            print(f'IDN: {self.IDN}')

    def channel_to_str(self, channel):
        _channel = str(channel)
        if len(_channel) > 1:
            return _channel
        else:
            return "0" + _channel

    def voltage_to_kw(self, v):
        x = (v+500)/1000
        return f'{x:.6f}'

    def voltage_to_hex(self, v, ch):
        x = (v+500)/1000
        DAC = int(x*self.span[ch]*62500 + self.offset[ch]*65535)
        return f'{DAC:0x}'.upper()

    @setting(1, returns="s")
    def get_ID(self, c):
        """
        Returns device identification number e.g. 'HV264 500 16 b'.
        First string 'HV264' is the IDN necessary to address device.
        """
        yield self.ser.write("IDN\r")
        recv = yield self.ser.read_line()
        return recv

    @setting(2, channel="i", returns='v')
    def get_voltage(self, c, channel):
        """
        Disclaimer: reading is digitized to 10s of mV.

        Args:
            channel: int, channel between 1 and 16.

        Returns:
            float, voltage in volts.
        """
        ch_str = self.channel_to_str(channel)
        yield self.ser.write(self.IDN+" Q"+ch_str+"\r")
        recv = yield self.ser.read_line()

        # exception to catch serial overload
        if recv[:-1] != '':
            return float(recv[:-1])
        else:
            return 99999 # will not update client

    @setting(3, channel="i", voltage='v')
    def set_voltage(self, c, channel, voltage):
        """
        Sets voltage on the specified channel.

        Args:
            channel: int, channel between 1 and 16.
            voltage: float, voltage in volts.
        """
        if voltage > self.vlim or voltage < -self.vlim:
            raise ValueError("Voltage setpoint out of bounds.")
        else:
            ch_str = self.channel_to_str(channel)
            volt_str = self.voltage_to_kw(voltage)
            yield self.ser.write(self.IDN+" CH"+ch_str+" "+volt_str+"\r")
            yield self.ser.read_line()

    @setting(4, channel="i")
    def get_calibration(self, c, channel):
        """
        Gets calibration on the specified channel as "span +/-offset".

        Args:
            channel: int, channel between 1 and 16.
        """
        ch_str = self.channel_to_str(channel)
        yield self.ser.write(self.IDN+" RCORR"+ch_str+"\r")
        recv = yield self.ser.read_line()
        return(recv[:-1])

    @setting(5, voltages='*v')
    def set_all_voltages(self, c, voltages):
        """
        Sets all voltages quickly.

        Args:
            voltages: array of floats, voltages in volts.
        """
        voltage_str = ""
        ch = 1

        for voltage in voltages:
            if voltage > self.vlim or voltage < -self.vlim:
                raise ValueError("Voltage setpoint out of bounds.")
            else:
                voltage_str += self.voltage_to_hex(voltage, ch)
                ch += 1

        yield self.ser.write(self.IDN+" A "+voltage_str+"\r")
        yield self.ser.read_line()

    @setting(6)
    def get_all_voltages(self, c):
        """
        Gets all voltages quickly.

        Returns:
            voltages: array of floats, voltages in volts.
        """
        yield self.ser.write(self.IDN+" U00"+"\r")
        recv = yield self.ser.read_line()
        return [float(value.strip("V")) for value in recv.split(",")]
