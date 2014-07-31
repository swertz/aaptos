import time
from datetime import datetime,timedelta
import AaptosSOAP
import AaptosSettings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
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
      
if __name__ == '__main__':
    main()

#TODO: add an option to read from db
