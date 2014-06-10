import serial

AaptosDummyMode = True
 
if AaptosDummyMode:
  from DummySCPI import DummySCPI as AgilentSCPI
  from DummyInstrument import DummyInstrument as AgilentInstrument
else:
  from AgilentSCPI import AgilentSCPI
  from AgilentInstrument import AgilentInstrument


class AgilentE3631A(AgilentSCPI):
  """Agilent E3631A Triple Output DC Power Supply"""

  def __init__(self,port='/dev/usb/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS):
    AgilentSCPI.__init__(self,port,baudrate,parity,bytesize)
    self.setRemote()
    self.reset()
    assert "E3631A" in self.identity(), "Error: improper device: "+self.identity()+"\n Expecting E3631A"
    self.instruments_ = { "P6V":AgilentInstrument(1,"P6V",self), "P25V":AgilentInstrument(2,"P25V",self), "M25V":AgilentInstrument(3,"M25V",self) }
    self.labels_ = { 1:"P6V", 2:"P25V", 3:"M25V" }
    self.currentInstrument_ = None
    self.enableDisplay()
    self.displayMessage("AAPTOS ONLINE...")
    self.beep()
    self.selectInstrument(index=1)

  def selectInstrument(self, label=None, index=None):
    """This command selects the output to be programmed among three outputs"""
    self.currentInstrument_ = self.getInstrument(label,index)
    self.currentInstrument_.makeCurrent()
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
    currentInstrument = self.question("INSTRUMENT:SELECT?")
    assert currentInstrument in self.instruments_, "Error: unknown current instrument"
    assert self.instruments_[currentInstrument].isCurrent(), "Error: current instrument mismatch"
    return currentInstrument

  def setRemote(self, locked=False):
    if(locked):
      self.write("SYSTEM:RWLOCK")
    else:
      self.write("SYSTEM:REMOTE")

  def setLocal(self):
    self.write("SYSTEM:LOCAL")

  def applySettings(self,instrument,voltage,current):
    """The values of voltage and the current of the specified output are changed as soon as the command is executed"""
    self.write("APPLY "+instrument+", "+str(voltage)+", "+str(current))

  def readSettings(self,instrument):
    """This command queries the power supply's present voltage and current values for each output and returns a quoted string"""
    return self.question("APPLY? "+instrument)

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

