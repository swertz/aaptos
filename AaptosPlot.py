from datetime import datetime,timedelta
import dateutil.parser
from optparse import OptionParser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import AaptosDb
import AaptosSOAP
import AaptosSettings

def main_live(bufferDepth, pollingTime):
  """AAPTOS SOAP client for plotting of readings"""
  plt.ion()
  aaptos = AaptosSOAP.SOAPProxy("http://%s:%d/"%(AaptosSettings.SOAPServer,AaptosSettings.SOAPPort))
  # get first readings and create plots
  status = aaptos.getStatus()
  fig = plt.figure(1)
  voltages = {}
  currents = {}
  for index,(device,values) in enumerate(status.iteritems()):
    mytime = mdates.date2num([ datetime.now() ])
    plt.subplot(len(status),2,(index*2)+1) # voltage
    voltages[device] = plt.plot_date(mytime, [values[0]], fmt="b-")[0]
    plt.subplot(len(status),2,(index*2)+2) # current
    currents[device] = plt.plot_date(mytime, [values[1]], fmt="b-")[0]
  # formating
  fig.autofmt_xdate()
  for index,(device,values) in enumerate(status.iteritems()):
    ax = plt.subplot(len(status),2,(index*2)+1) # voltage
    ax.fmt_xdata = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.title('%s voltage'%device)
    ax = plt.subplot(len(status),2,(index*2)+2) # current
    ax.fmt_xdata = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.title('%s current'%device)
  fig.subplots_adjust(left=0.075, bottom=0.10, right=0.95, top=0.95, wspace=0.175, hspace=0.30)
  # iterate and update live plots
  while True:
    status = aaptos.getStatus()
    now = mdates.date2num(datetime.now())
    for index,(device,values) in enumerate(status.iteritems()):
      # update graphs
      voltagePlot = voltages[device]
      currentPlot = currents[device]
      t,v = voltagePlot.get_data()
      c = currentPlot.get_ydata()
      t = np.append(t,now)
      v = np.append(v,values[0])
      c = np.append(c,values[1])
      if len(t)>bufferDepth:
        t = np.delete(t,0)
        v = np.delete(v,0)
        c = np.delete(c,0)
      voltagePlot.set_data(t,v)
      currentPlot.set_data(t,c)
      # update view
      ax = plt.subplot(len(status),2,index*2+1) # voltage
      plt.ylim((np.amin(v)-0.1*abs(np.amin(v)-np.amax(v)),np.amax(v)+0.1*abs(np.amin(v)-np.amax(v))))
      plt.xlim((np.amin(t),np.amax(t)))
      ax = plt.subplot(len(status),2,index*2+2) # current
      plt.ylim((np.amin(c)-0.1*abs(np.amin(c)-np.amax(c)),np.amax(c)+0.1*abs(np.amin(c)-np.amax(c))))
      plt.xlim((np.amin(t),np.amax(t)))
    plt.draw()
    plt.pause(pollingTime)

def main_db(t0,t1):
  dbstore = AaptosDb.DbStore()
  timerange = (t0,t1)
  # get readings and create plots
  readings = dbstore.find(AaptosDb.supplyReadings, AaptosDb.supplyReadings.reading_time>timerange[0], AaptosDb.supplyReadings.reading_time<timerange[1] ) 
  devices = set([ reading.instrument for reading in readings ])
  fig = plt.figure(1)
  for index,device in enumerate(devices):
    devicereadings = readings.find(AaptosDb.supplyReadings.instrument==device)
    v = [ reading.voltage for reading in devicereadings ]
    c = [ reading.current for reading in devicereadings ]
    t = [ reading.reading_time for reading in devicereadings ]
    plt.subplot(len(devices),2,(index*2)+1) # voltage
    plt.plot_date(t, v, fmt="b-")[0]
    plt.subplot(len(devices),2,(index*2)+2) # current
    plt.plot_date(t, c, fmt="b-")[0]
  # formating
  fig.autofmt_xdate()
  for index,device in enumerate(devices):
    ax = plt.subplot(len(devices),2,(index*2)+1) # voltage
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.title('%s voltage'%device)
    ax = plt.subplot(len(devices),2,(index*2)+2) # current
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.title('%s current'%device)
  fig.subplots_adjust(left=0.075, bottom=0.10, right=0.95, top=0.95, wspace=0.175, hspace=0.30)
  plt.show()

def main():
  # options handling
  usage="""%prog [options]"""
  description="""A simple script to display voltage/current from aaptos devices.
Support for both live stream (from the SOAP server) or database inspection."""
  parser = OptionParser(usage=usage,add_help_option=True,description=description)
  parser.add_option("-l", "--live", action="store_true", dest="live", default=False, 
                    help="use the live stream from the SOAP server")
  parser.add_option("-f", "--from", action="store", type="string", dest="beginning", 
                    help="beginning of the period to plot, in ISO 8601 format, YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]")
  parser.add_option("-t", "--to", action="store", type="string", dest="end", 
                    help="end of the period to plot, in ISO 8601 format, YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]")
  parser.add_option("-b", "--buffer", action="store", type="int", dest="bufferdepth", default=500,
                    help="in live mode, depth of the value buffer. When exceeded, first values will be dropped from the display")
  parser.add_option("-p", "--poll", action="store", type="int", dest="pollingTime", default=AaptosSettings.PoolDelay,
                    help="polling time in seconds")
  (options, args) = parser.parse_args()
  if options.live:
    if options.beginning is not None or options.end is not None:
      parser.error("options --from and --to are incompatible with --live")
    main_live(options.bufferdepth, options.pollingTime)
  else:
    if options.beginning is None or options.end is None:
      parser.error("options --from and --to are both mandatory to access the database")
    try:
      initialTime = dateutil.parser.parse(options.beginning)
    except ValueError:
      parser.error("--from: unknown string format")
    try:
      finalTime = dateutil.parser.parse(options.end)
    except ValueError:
      parser.error("--from: unknown string format")
    main_db(initialTime,finalTime)

if __name__ == '__main__':
    main()

