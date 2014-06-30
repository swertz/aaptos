import SOAPpy
import AaptosSettings
from AgilentE3631A import AgilentE3631A
from AgilentE3633A import AgilentE3633A

SOAPpy.Config.simplify_objects=1


class aaptos:
  def __init__(self):
    # devices
    self.devices = {}
    for dev in AaptosSettings.Devices:
      module = __import__(dev[1])
      class_ = getattr(module, dev[1])
      setattr(self,dev[0],class_(port=dev[2]))
      self.devices[dev[0]] = getattr(self,dev[0])
    # instruments
    self.instruments = {}
    for devname,dev in self.devices.iteritems():
      for label,inst in dev.instruments_.iteritems():
        setattr(self,"%s_%s"%(devname,label),inst)
        self.instruments["%s_%s"%(devname,label)] = getattr(self,"%s_%s"%(devname,label))
    
  def getStatus(self):
    result = {}
    for label,i in self.instruments.iteritems():
      result[label] = (i.getMeasuredVoltage(), i.getMeasuredCurrent())
    return result

  def configureInstrument(self,instrument,V,I, triggered=False):
    getattr(self,instrument).setVoltage(V, triggered)
    getattr(self,instrument).setCurrentLimit(I, triggered)

  def getInstrumentConfiguration(self,instrument, triggered=False):
    instr = getattr(self,instrument)
    return (instr.getVoltage(triggered), instr.getCurrentLimit(triggered))
    
  def recall(self, memory):
    for device in self.devices.values():
      device.recall(memory)

  def save(self,memory):
    for device in self.devices.values():
      device.save(memory)
  
  def turnOn(self):
    for device in self.devices.values():
      device.enable()
      device.displayMessage("AAPTOS ON")

  def turnOff(self):
    for device in self.devices.values():
      device.disable()
      device.displayMessage("AAPTOS OFF")

  def isOn(self):
    output = True
    for device in self.devices.values():
      output &= int(device.state())
    return output

  def lock(self, yesno):
    for device in self.devices.values():
      device.setRemote(locked=yesno) 

class SOAPServer(SOAPpy.SOAPServer): pass

class SOAPProxy(SOAPpy.SOAPProxy): pass


def main():
  # Start the server
  server = SOAPServer((AaptosSettings.SOAPServer, AaptosSettings.SOAPPort))
  server.registerObject(aaptos())
  #aaptos_instance = aaptos()
  #server.registerObject(aaptos_instance, namespace="aaptos")
  #server.registerObject(aaptos_instance.E3631A, namespace="E3631A")
  #server.registerObject(aaptos_instance.E3633A, namespace="E3633A")
  #server.registerObject(aaptos_instance.P6V, namespace="P6V")
  #server.registerObject(aaptos_instance.P25V, namespace="P25V")
  #server.registerObject(aaptos_instance.N25V, namespace="N25V")
  #server.registerObject(aaptos_instance.P20V, namespace="P20V")
  server.serve_forever()

if __name__ == '__main__':
    main()

