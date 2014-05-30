import serial

class SerialConnection:
  """RS-232 connection to the Agilent power supply"""
  def __init__(self, port='/dev/usb/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS):
    """Initialize the connection"""
    self.serial = serial.Serial(port=port, baudrate=baudrate, parity=parity, bytesize=bytesize, stopbits=serial.STOPBITS_TWO, dsrdtr=True, timeout=1)

  def write(self, data):
    """Send one command to the device"""
    self.serial.write(data+'\n')

  def readline(self):
    """Read one line from the device"""
    return self.serial.readLine()

  def question(self, data):
    """Send one query to the device and returns the answer"""
    self.write(data)
    return self.readline()

  def open(self):
    """Open the connection"""
    self.serial.open()

  def close(self):
    """Close the connection"""
    self.serial.close()
    
  def isOpen(self):
    """Check if the port is opened."""
    return self.serial.isOpen()

