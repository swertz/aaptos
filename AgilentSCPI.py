import serial
from SerialConnection import SerialConnection

class AgilentSCPI(SerialConnection):
  """Generic SCPI interface to Agilent power supplies. The SCPI commands below are handled.

     DISPlay
       [:WINDow][:STATe] {OFF|ON}
       [:WINDow][:STATe]?
       [:WINDow]:TEXT[:DATA] <quoted string>
       [:WINDow]:TEXT[:DATA]?
       [:WINDow]:TEXT:CLEar
     OUTPUT
       [:STATe] {OFF/ON}
       [:STATE]?
     SYSTem
       :BEEPer[:IMMediate]
       :ERRor?
       :VERSion
     TRIGger
       [:SEQuence]:DELay {<seconds>|MIN|MAX}
       [:SEQuence]:DELay?
       [:SEQuence]:SOURce{BUS|IMM}
       [:SEQuence]:SOURce?
     INITiate[:IMMediate]
  """

  def __init__(self, port='/dev/usb/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS):
    """Initialize the connection to the device"""
    SerialConnection.__init__(port,baudrate,parity,bytesize) 

  def beep(self):
    """This command issues a single beep immediately"""
    self.write("SYSTEM:BEEPER:IMMEDIATE")

  def getErrors(self):
    """Reads one error from the error queue"""
    errors = []
    while True:
      error =  self.question("SYSTEM:ERROR?")
      errorcode = int(error.split(',')[0])
      errormessage = error.split(',')[1].lstrip()
      if errorcode==0: return errors
      errors.append((errorcode,errormessage))

  def version(self):
    """Returns a string in the form "YYYY.V" where the "Y's" represent the year of the 
       version, and the "V" represents a version number for that year (for example, 1995.0)"""
    return self.question("SYSTEM:VERSION?")

  def identity(self):
    """This query command reads the power supply's identification string"""
    return self.question("*IDN?")

  def reset(self):
    """This command resets the power supply to its power-on state and clear status registers"""
    return self.write("*RST; *CLS")

  def selfTest(self):
    """This query performs a complete self-test of the power supply.
       Returns 0 if it passes, 1 if it fails.
       If the self-test fails, an error message is also generated with additional information on why the test failed."""
    return self.question("*TST?")
   
  def setTriggerDelay(self, delay=0):
    """This command sets the time delay between the detection of an event on the specified 
       trigger source and the start of any corresponding trigger action on the power supply 
       output"""
    self.write("TRIGGER:SEQUENCE:DELAY "+str(delay))

  def getTriggerDelay(self):
    """This command queries the trigger delay"""
    return self.question("TRIGGER:SEQUENCE:DELAY?")

  def setTriggerSource(self, source="BUS"):
    """This command selects the source from which the power supply will accept a trigger"""
    assert source=="BUS" or source=="IMM", "trigger source is neither BUS or IMM"
    self.write("TRIGGER:SEQUENCE:SOURCE "+source)

  def getTriggerSource(self):
    """This command queries the present trigger source. Returns "BUS" or "IMM" """
    return self.question("TRIGGER:SEQUENCE:SOURCE?")

  def initiateTrigger(self, immediate=True):
    """This command causes the trigger system to initiate"""
    if immediate:
      self.write("INITIATE:IMMEDIATE")
    else:
      self.write("INITIATE")

  def enableDisplay(self):
    """This command turns the front-panel display on"""
    self.write("DISPLAY:STATE ON")

  def disableDisplay(self):
    """This command turns the front-panel display off"""
    self.write("DISPLAY:STATE OFF")

  def getDisplayState(self):
    """This command queries the front-panel display setting. Returns "0" (OFF) or "1" (ON)"""
    return self.question("DISPLAY:STATE?")

  def displayMessage(self,message):
    """This command displays a message on the front panel"""
    self.write("DISPLAY:WINDOW:TEXT:DATA "+str(message))

  def getDisplayMessage(self):
    """This command queries the message sent to the front panel and returns a quoted string"""
    return self.question("DISPLAY:WINDOW:TEXT:DATA?")

  def clearDisplayMessage(self):
    """This command clears the message displayed on the front panel"""
    self.write("DISPLAY:WINDOW:TEXT:CLEAR")

  def enable(self):
    """This command enables all outputs of the power supply"""
    self.write("OUTPUT:STATE ON")

  def disable(self):
    """This command disables all outputs of the power supply"""
    self.write("OUTPUT:STATE OFF")

  def save(self, index=1):
    """This command stores the present state of the power supply to the specified location in non-volatile memory"""
    self.write("*SAV "+str(index))

  def recall(self, index=1):
    """This command recalls a previously stored state"""
    self.write("*RCL "+str(index))


  #TODO: missing for now: registers (not critical)


