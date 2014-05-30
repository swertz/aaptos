from SerialConnection import SerialConnection

class AgilentInstrument(SerialConnection):
  """Generic SCPI interface to Agilent power supply instruments. The SCPI commands below are handled.

     MEASure
       :CURRent[:DC]?
       [:VOLTage][:DC]?
     [SOURce]
       :CURRent[:LEVel][:IMMediate][:AMPLitude] {<current>|MIN|MAX}
       :CURRent[:LEVel][:IMMediate][:AMPLitude]? [MIN|MAX]
       :CURRent[:LEVel]:TRIGgered[AMPLitude] {<current>|MIN|MAX}
       :CURRent[:LEVel]:TRIGgered[:AMPLitude]? [MIN|MAX]
       :VOLTage[:LEVel][:IMMediate][:AMPLitude] {<voltage>|MIN|MAX}
       :VOLTage[:LEVel][IMMediate][:AMPLitude]?[MIN:MAX]
       :VOLTage[:LEVel]:TRIGgered[:AMPLitude] {<voltage>|MIN|MAX}
       :VOLTage[:LEVel]:TRIGgered[:AMPLitude]?[MIN|MAX]
  """

  def __init__(self, index=0, label="", connection=None):
    self.index_ = index
    self.label_ = label
    self.isCurrent_ = (index==0)
    if not isinstance(connection,SerialConnection):
      raise TypeError("Error: AgilentInstrument must be instantiated from an existing SerialConnection")
    self.serial = connection.serial

  def __copy__(self):
    raise copy.error("AgilentInstrument cannot be copied")

  def __deepcopy__(self,memo):
    raise copy.error("AgilentInstrument cannot be copied")

  def isCurrent(self):
    return self.isCurrent_

  def makeCurrent(self):
    if not self.isCurrent():
      self.write("INSTRUMENT:NSELECT "+str(self.index_))
      self.isCurrent_ = True

  def getMeasuredCurrent(self):
    """This command queries the current measured at the output terminals of the power supply"""
    return self.question("MEASURE:CURRENT? " + self.label_)

  def getMeasuredVoltage(self):
    """This command queries the voltage measured at the output terminals of the power supply"""
    return self.question("MEASURE:VOLTAGE? " + self.label_)

  def setCurrentLimit(self, current, triggered=False):
    """This command directly programs the current level of the power supply"""
    self.makeCurrent()
    if triggered:
      self.write("SOURCE:CURRENT:LEVEL:TRIGGERED:AMPLITUDE "+str(current))
    else:
      self.write("SOURCE:CURRENT:LEVEL:IMMEDIATE:AMPLITUDE "+str(current))

  def getCurrentLimit(self, triggered=False):
    """This query returns the presently programmed current limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:CURRENT:LEVEL:TRIGGERED:AMPLITUDE?")
    else:
      return self.question("SOURCE:CURRENT:LEVEL:IMMEDIATE:AMPLITUDE?")

  def getMinCurrentLimit(self, triggered=False):
    """This query returns the minimum programmable current limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:CURRENT:LEVEL:TRIGGERED:AMPLITUDE? MIN")
    else:
      return self.question("SOURCE:CURRENT:LEVEL:IMMEDIATE:AMPLITUDE? MIN")

  def getMaxCurrentLimit(self, triggered=False):
    """This query returns the maximum programmable current limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:CURRENT:LEVEL:TRIGGERED:AMPLITUDE? MAX")
    else:
      return self.question("SOURCE:CURRENT:LEVEL:IMMEDIATE:AMPLITUDE? MAX")

  def setVoltage(self, voltage, triggered=False):
    """This command directly programs the voltage level of the power supply"""
    self.makeCurrent()
    if triggered:
      self.write("SOURCE:VOLTAGE:LEVEL:TRIGGERED:AMPLITUDE "+str(voltage))
    else:
      self.write("SOURCE:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE "+str(voltage))

  def getVoltage(self, triggered=False):
    """This query returns the presently programmed voltage limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:VOLTAGE:LEVEL:TRIGGERED:AMPLITUDE?")
    else:
      return self.question("SOURCE:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE?")

  def getMinVoltage(self, triggered=False):
    """This query returns the minimum programmable voltage limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:VOLTAGE:LEVEL:TRIGGERED:AMPLITUDE? MIN")
    else:
      return self.question("SOURCE:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE? MIN")

  def getMaxVoltage(self, triggered=False):
    """This query returns the minimum programmable voltage limit level of the selected output"""
    self.makeCurrent()
    if triggered:
      return self.question("SOURCE:VOLTAGE:LEVEL:TRIGGERED:AMPLITUDE? MAX")
    else:
      return self.question("SOURCE:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE? MAX")

#TODO: calibration commands
