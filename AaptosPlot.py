from datetime import datetime,timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import AaptosDb
import AaptosSOAP
import AaptosSettings

def main_live():
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
      if len(t)>60: #TODO: this should be a cfg on the command line
        t = np.delete(t,0)
        v = np.delete(v,0)
        c = np.delete(c,0)
      voltagePlot.set_data(t,v)
      currentPlot.set_data(t,c)
      # update view
      ax = plt.subplot(len(status),2,index*2+1) # voltage
      plt.ylim((np.amin(v),np.amax(v)))
      plt.xlim((np.amin(t),np.amax(t)))
      ax = plt.subplot(len(status),2,index*2+2) # current
      plt.ylim((np.amin(c),np.amax(c)))
      plt.xlim((np.amin(t),np.amax(t)))
    plt.draw()
    plt.pause(AaptosSettings.PoolDelay)

def main_db():
  dbstore = AaptosDb.DbStore()
  timerange = (datetime(2014, 7, 30, 14, 30, 00),datetime(2014, 7, 30, 16, 30, 00)) # TODO: from cfg
  # get readings and create plots
  readings = dbstore.find(AaptosDb.supplyReadings, AaptosDb.supplyReadings.reading_time>timerange[0], AaptosDb.supplyReadings.reading_time<timerange[1] ) 
  devices = set([ reading.instrument for reading in readings ])
  fig = plt.figure(1)
  voltages = {}
  currents = {}
  for index,device in enumerate(devices):
    devicereadings = readings.find(AaptosDb.supplyReadings.instrument==device)
    v = [ reading.voltage for reading in devicereadings ]
    c = [ reading.current for reading in devicereadings ]
    t = [ reading.reading_time for reading in devicereadings ]
    plt.subplot(len(devices),2,(index*2)+1) # voltage
    voltages[device] = plt.plot_date(t, v, fmt="b-")[0]
    plt.subplot(len(devices),2,(index*2)+2) # current
    currents[device] = plt.plot_date(t, c, fmt="b-")[0]
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

def main(): #TODO: add a switch as a cfg (command line)
  #main_live()
  main_db()

if __name__ == '__main__':
    main()

