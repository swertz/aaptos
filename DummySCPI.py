import serial

class DummySCPI:

  def __init__(self, port='/dev/usb/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS):
    self.td = 0
    self.ts = "BUS"
    self.ds = True
    self.message = ""
    self.state_ = False

  def beep(self):
    pass

  def getErrors(self):
    return []

  def version(self):
    return "1995.0"

  def identity(self):
    return self.__class__.__name__

  def reset(self):
    pass

  def selfTest(self):
    return 0
   
  def setTriggerDelay(self, delay=0):
    self.td = delay

  def getTriggerDelay(self):
    return self.td

  def setTriggerSource(self, source="BUS"):
    self.ts = source

  def getTriggerSource(self):
    return self.ts

  def initiateTrigger(self, immediate=True):
    pass

  def enableDisplay(self):
    self.ds = True

  def disableDisplay(self):
    self.ds = False

  def getDisplayState(self):
    return self.ds

  def displayMessage(self,message):
    self.message = message

  def getDisplayMessage(self):
    return self.message

  def clearDisplayMessage(self,dummy=None):
    self.message = ""

  def enable(self):
    self.state_ = True

  def disable(self):
    self.state_ = False

  def state(self):
    return self.state_

  def save(self, index=1):
    pass

  def recall(self, index=1):
    pass

  def write(self,s): 
    pass

  def question(self,s): 
    return "1"

