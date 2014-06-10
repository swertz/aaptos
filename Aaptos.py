import time
from threading import Thread, Event
import AaptosDb
import AaptosSOAP
import AaptosCli
import AaptosSettings

class serverThread(Thread):
  def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
  def run(self):
    server = AaptosSOAP.SOAPServer((AaptosSettings.SOAPServer, AaptosSettings.SOAPPort))
    server.registerObject(AaptosSOAP.aaptos())
    print "AAPTOS SOAP server started."
    self.serverRunning.set()
    server.serve_forever()

class loggerThread(Thread):
  def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.enabled = kwargs["loggerEnabled"]
  def run(self):
    self.serverRunning.wait()
    aaptos = AaptosSOAP.SOAPProxy("http://%s:%d/"%(AaptosSettings.SOAPServer,AaptosSettings.SOAPPort))
    dbstore = AaptosDb.DbStore()
    print "AAPTOS SOAP client for db logging started"
    while True:
      self.enabled.wait()
      status = aaptos.getStatus()
      for device,values in status.iteritems():
        readings = AaptosDb.supplyReadings()
        readings.instrument = unicode(device)
        readings.voltage = values[0]
        readings.current = values[1]
        dbstore.add(readings)
      dbstore.commit()
      time.sleep(AaptosSettings.PoolDelay)

class cliThread(Thread):
  def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.loggerEnabled = kwargs["loggerEnabled"]
  def run(self):
    self.serverRunning.wait()
    aaptos =  AaptosSOAP.SOAPProxy("http://%s:%d/"%(AaptosSettings.SOAPServer,AaptosSettings.SOAPPort))
    cli_app = AaptosCli.MyAaptosCliApp(soapProxy=aaptos,loggerEnabled=self.loggerEnabled)
    cli_app.run()

def main():

  serverRunning = Event()
  loggerEnabled = Event()
  loggerEnabled.set()
  
  serverThread(name="SOAPServer",daemon=True, kwargs = {"serverRunning":serverRunning}).start()
  loggerThread(name="DBLogger",daemon=True, kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()
  cliThread(name="CLIent", kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()

if __name__ == '__main__':
  main()

