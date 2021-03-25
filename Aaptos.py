#!/usr/bin/env python

import time
import sys
from threading import Thread, Event
from optparse import OptionParser
from Daemon import Daemon
import AaptosDb
import AaptosSOAP
import AaptosCli
import AaptosSettings

class serverThread(Thread):
  def __init__(self, group=None, target=None, name=None, SOAPServer=None, SOAPPort=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.SOAPServer = SOAPServer if SOAPServer else AaptosSettings.SOAPServer
    self.SOAPPort = SOAPPort if SOAPPort else AaptosSettings.SOAPPort
  def run(self):
    server = AaptosSOAP.SOAPServer((self.SOAPServer, self.SOAPPort))
    server.registerObject(AaptosSOAP.aaptos())
    print "AAPTOS SOAP server started."
    self.serverRunning.set()
    server.serve_forever()

class loggerThread(Thread):
  def __init__(self, group=None, target=None, name=None, SOAPServer=None, SOAPPort=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.enabled = kwargs["loggerEnabled"]
    self.SOAPServer = SOAPServer if SOAPServer else AaptosSettings.SOAPServer
    self.SOAPPort = SOAPPort if SOAPPort else AaptosSettings.SOAPPort
  def run(self):
    self.serverRunning.wait()
    aaptos = AaptosSOAP.SOAPProxy("http://%s:%d/"%(self.SOAPServer, self.SOAPPort))
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
  def __init__(self, group=None, target=None, name=None, SOAPServer=None, SOAPPort=None, args=(), kwargs={}, daemon=False):
    Thread.__init__(self,group=group, target=target, name=name, args=args, kwargs=kwargs)
    self.setDaemon(daemon)
    self.serverRunning = kwargs["serverRunning"]
    self.loggerEnabled = kwargs["loggerEnabled"]
    self.SOAPServer = SOAPServer if SOAPServer else AaptosSettings.SOAPServer
    self.SOAPPort = SOAPPort if SOAPPort else AaptosSettings.SOAPPort
  def run(self):
    self.serverRunning.wait()
    aaptos =  AaptosSOAP.SOAPProxy("http://%s:%d/"%(self.SOAPServer, self.SOAPPort))
    cli_app = AaptosCli.MyAaptosCliApp(soapProxy=aaptos,loggerEnabled=self.loggerEnabled)
    cli_app.run()

class AaptosDaemon(Daemon):
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', withDb=False):
    Daemon.__init__(self,pidfile,stdin,stdout,stderr)
    self.withDb = withDb

  def run(self):
    serverRunning = Event()
    loggerEnabled = Event()
    loggerEnabled.set()
    serverThread(name="SOAPServer",daemon=False, kwargs = {"serverRunning":serverRunning}).start()
    if self.withDb:
      loggerThread(name="DBLogger",daemon=True, kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()

def main():
  # pidfile
  pidfile = "/tmp/daemon-aaptos.pid"
  # options handling
  usage="""%prog [options] [start|stop|restart]"""
  description="""The Aaptos daemon.
It can be started either as a deamon, or interactively, with or without db and cli components."""
  parser = ArgumentParser(usage=usage,add_help_option=True,description=description)
  parser.add_argument("command", choices=["start", "stop", "restart"],
                      help="Daemon command")
  parser.add_argument("-D", "--daemon", action="store_true", default=False,
                      help="start as a daemon. Requires additional start/stop/restart argument.")
  parser.add_argument("-c", "--cli", action="store_true", dest="withCli", default=False,
                      help="also start the client.")
  parser.add_argument("-l", "--log", action="store_true", dest="withDb", default=False,
                      help="also start the database logger.")
  parser.add_argument("-s", "--server", default="localhost",
                      help="IP address of machine running the Aaptos SOAP server (default is localhost")
  parser.add_argument("-p", "--port", type=int, default=8080,
                      help="Port of Aaptos SOAP server (default is 8080")
  args = parser.parse_args()
  if args.daemon:
    if not args.command:
      parser.error("Daemon mode requires an additional start/stop/restart argument.")
    else:
      mode = args.command
  else:
    if args.command:
      parser.error("%s is intended for daemon mode. Use together with --daemon"%args.command)
  if args.withCli:
    if args.daemon:
      parser.error("--cli is incompatible with --daemon.")

  # start Aaptos
  if args.daemon:
    # daemon mode
    daemon = AaptosDaemon(pidfile, withDb=args.withDb)
    getattr(daemon,mode)()
  else:
    # non-deamon mode
    daemon = AaptosDaemon(pidfile)
    if daemon.getpid():
      sys.stderr.write("pidfile %s already exist. Already running as a daemon?\n"%pidfile)
      sys.exit(1)
    serverRunning = Event()
    loggerEnabled = Event()
    loggerEnabled.set()
    s = serverThread(name="SOAPServer", SOAPServer=args.server, SOAPPort=args.port, daemon=True, kwargs = {"serverRunning":serverRunning})
    if args.withDb:
      loggerThread(name="DBLogger",daemon=True, kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()
    if args.withCli:
      s.start()
      cliThread(name="CLIent", SOAPServer=args.server, SOAPPort=args.port, kwargs = {"serverRunning":serverRunning, "loggerEnabled":loggerEnabled}).start()
    else:
      try:
        s.run()
      except KeyboardInterrupt:
        pass
    print "\nAAPTOS SOAP server stopped."

if __name__ == '__main__':
  main()

