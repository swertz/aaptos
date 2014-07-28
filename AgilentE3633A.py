import serial

AaptosDummyMode = False

if AaptosDummyMode:
  from DummySCPI import DummySCPI as AgilentSCPI
  from DummyInstrument import DummyInstrument as AgilentInstrument
else:
  from AgilentSCPI import AgilentSCPI
  from AgilentInstrument import AgilentInstrument


class AgilentE3633A(AgilentSCPI):
  """Agilent E3633A Triple Output DC Power Supply"""

  def __init__(self,port='/dev/usb/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS):
    AgilentSCPI.__init__(self,port,baudrate,parity,bytesize)
    self.setRemote()
    self.reset()
    assert "E3633A" in self.identity(), "Error: improper device: "+self.identity()+"\n Expecting E3633A"
    self.instruments_ = { "P20V":AgilentInstrument(0,"P20V",self) }
    self.labels_ = { 0:"P20V" }
    self.currentInstrument_ = None
    self.enableDisplay()
    self.displayMessage("AAPTOS READY")
    self.beep()
    self.selectInstrument(index=0)

  def selectInstrument(self, label=None, index=None):
    """This command selects the output to be programmed among three outputs"""
    self.getInstrument(label,index).makeCurrent()
    return self.currentInstrument_

  def getCurrentInstrument(self):
    """Returns the current instrument"""
    return self.currentInstrument_

  def getInstrument(self, label=None, index=None):
    if label in self.instruments_:
      return self.instruments_[label]
    elif index in self.labels_:
      return self.instruments_[self.labels_[index]]
    else:
      raise Exception("No such instrument:",label, index)

  def getSelected(self):
    """This query returns the currently selected output by the INSTrument"""
    return self.labels_[0]

  def setRemote(self, locked=False):
    self.setLocal() # needed to eventually unlock 
    if(locked):
      self.write("SYSTEM:RWLOCK")
    else:
      self.write("SYSTEM:REMOTE")

  def setLocal(self):
    self.write("SYSTEM:LOCAL")

  def applySettings(self,instrument,voltage,current):
    """The values of voltage and the current of the specified output are changed as soon as the command is executed"""
    self.write("APPLY "+str(voltage)+", "+str(current))

  def readSettings(self,instrument):
    """This command queries the power supply's present voltage and current values for each output and returns a quoted string"""
    return map(float,self.question("APPLY? "+instrument)[1:-1].split(","))

  def couple(self,instrumentList=[]):
    """This command defines a coupling between various logical outputs of the power supply"""
    if len(intrumentList)==0: instruments = "NONE"
    elif set(instrumentList)==set(labels_.values()): instruments = "ALL"
    else: instruments = reduce(lambda s,t: s+","+t,set(instrumentList))
    self.write("INSTRUMENT:COUPLE:TRIGGER "+instruments)

  def getCoupledOutputs(self):
    """This query returns the currently coupled output. Returns "ALL", "NONE", or a list"""
    return self.question("INSTRUMENT:COUPLE:TRIGGER?")

  def setTrackState(self, state=True):
    """This command enables or disables the power supply to operate in the track mode"""
    if state:
      self.write("OUTPUT:TRACK:STATE ON")
    else:
      self.write("OUTPUT:TRACK:STATE OFF")

  def trackState(self):
    """This command queries the track mode state of the power supply"""
    return self.question("OUTPUT:TRACK:STATE?")

