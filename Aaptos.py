import time
import AaptosDb
import AaptosSOAP
from threading import Thread

class serverThread(Thread):
  def __init__(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
    self.serverRunning = kwargs["serverRunning"]
  def run(self):
    server = AaptosSOAP.SOAPServer(("localhost", 8080))
    server.registerObject(aaptos())
    print "AAPTOS SOAP server started."
    self.serverRunning.set()
    server.serve_forever() #TODO: start this in a (sub)thread so that it can be shutdown with server.shutdown()

class loggerThread(Thread):
  def __init__(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.enabled = kwargs["loggerEnabled"]
  def run(self):
    self.serverRunning.wait()
    aaptos = AaptosSOAP.SOAPProxy("http://localhost:8080/")
    dbstore = AaptosDb.DbStore()
    print "AAPTOS SOAP client for db logging started"
    while True:
      self.enabled.wait()
      status = aaptos.getStatus()
      for device,values in status.iteritems():
        readings = AaptosDb.supplyReadings()
        readings.instrument = device
        readings.voltage = values[0]
        readings.current = values[1]
        dbstore.add(readings)
      dbstore.commit()
      time.sleep(AaptosDb.pooldelay)

class cliThread(Thread):
  def __init__(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.loggerEnabled = kwargs["loggerEnabled"]
  def run(self):
    self.serverRunning.wait()
    aaptos =  AaptosSOAP.SOAPProxy("http://localhost:8080/")
    cli_app = MyAaptosCliApp(soapProxy=aaptos,loggerEnabled=self.loggerEnabled)
    cli_app.run()

def main():

  serverRunning = threading.Event()
  loggerEnabled = threading.Event()
  loggerEnabled.set()
  
  serverThread(name="SOAPServer",daemon=True, kwargs = {"serverRunning":serverRunning}).start()
  loggerThread(name="DBLogger",daemon=True, kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()
  cliThread(name="CLIent", kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()

if __name__ == '__main__':
    main()

