from datetime import datetime
from threading import Thread
from time import sleep
import socket
import npyscreen
import AaptosSOAP
import AaptosSettings
import logging
logging.basicConfig(filename='AaptosCli.log',level=logging.DEBUG)
        
#####################################################
## Widgets - to be used: PowerBox
#####################################################

class GaugeWidget(npyscreen.Slider):
    """A slider with custom label"""
    def __init__(self, screen, *args, **keywords):
      self.negativeValue = False
      super(GaugeWidget, self).__init__(screen, *args, **keywords)
      self.levels = (0,50,100, 100.1)
      self.unit = "a.u."
      if 'levels' in keywords:
        self.levels = keywords['levels']
      if 'unit' in keywords:
        self.unit = keywords['unit']

    def translate_value(self):
      if self.negativeValue:
         stri = "-%6.3f %s" % (self.value, self.unit)
      else:
         stri = "%6.3f %s" % (self.value, self.unit)
      return stri

    def set_levels(self,levels):
      self.lowest = abs(levels[0])
      self.warning = abs(levels[1])
      self.maximum = abs(levels[2])
      self.out_of = abs(levels[3])
      #self.step   = self.out_of/10.
      if self.__value < self.levels[1] :
          self.color = "SAFE"
      elif self.__value < self.levels[2]:
          self.color = "WARNING"
      else:
          self.color = "DANGER"

    def get_levels(self):
        return (self.lowest, self.warning, self.maximum, self.out_of)

    levels = property(get_levels, set_levels)

    def set_value(self, val):
        #"We can only represent ints or floats, and must be less than what we are out of..."
        if val is None: val = 0
        if not isinstance(val, int) and not isinstance(val, float):
            raise TypeError("GaugeWidget value must be int or float")

        else:
            self.__value = abs(val)

        if self.__value > self.out_of: raise ValueError("GaugeWidget value out of bound: %f > %f"%(self.__value,self.out_of))
        if hasattr(self, 'levels'):
          if abs(val) < self.levels[1] :
            self.color = "SAFE"
          elif abs(val) < self.levels[2]:
            self.color = "WARNING"
          else:
            self.color = "DANGER"
        self.negativeValue = (val<0)

    def get_value(self):
          return float(self.__value)

    value = property(get_value, set_value)


class TitleGauge(npyscreen.TitleText):
    _entry_type = GaugeWidget

    def set_levels(self,levels):
      self.entry_widget.set_levels(levels)

    def get_levels(self):
      return self.entry_widget.get_levels()

    levels = property(get_levels, set_levels)


class PowerBox(npyscreen.BoxBasic):
    """A widget combining Voltage and Current gauges"""

    def __init__(self, screen, *args, **keywords):
        """Initialize the widget. Relevant parameters are name, values, and levels.
           Levels is a pair of triplet (min, warning, max)."""
        super(PowerBox, self).__init__(screen, *args, **keywords)
        if 'levels' in keywords:
            self.levels_ = keywords['levels']
        else:
            self.levels_ = [(0,5,5,5), (0,0.5,1,2)]
        self.make_contained_widgets()
        if 'values' in keywords:
            self.values = keywords['values']
    
    def make_contained_widgets(self):
        self._my_widgets = []
        labels = ["Voltage","Current"]
        units  = ["V","A"]
        contained_widgets = [ TitleGauge, TitleGauge ]
        for i,w in enumerate(contained_widgets):
          self._my_widgets.append(w(self.parent, rely=self.rely+1+i, relx = self.relx+2, 
                                    max_width=self.width-4, max_height=self.height-2, name = labels[i], unit=units[i], levels=self.levels_[i]))
          self._my_widgets[-1].editable=False
          self._my_widgets[-1].scroll_exit=False
          self._my_widgets[-1].slow_scroll=False
            
    def update(self, clear=True):
        if self.hidden and clear:
            self.clear()
            return False
        elif self.hidden:
            return False
        super(PowerBox, self).update(clear=clear)
        for w in self._my_widgets:
            w.update(clear=clear)
            
    def resize(self):
        super(PowerBox, self).resize()
        for w in self._my_widgets:
            w.resize()
    
    def edit(self):
        self.editing=True
        self.display()
        self.editing=False
        self.display()
        
    def get_values(self):
        if hasattr(self, '_my_widgets'): 
            return [self._my_widgets[0].value, self._my_widgets[1].value ]
        elif hasattr(self, '__tmp_values'):
            return self.__tmp_values
        else:
            return None

    def set_values(self, values):
        if hasattr(self, '_my_widgets'): 
            self._my_widgets[0].value = values[0]
            self._my_widgets[1].value = values[1]
        elif hasattr(self, '__tmp_values'):
            # probably trying to set the value before the textarea is initialised
            self.__tmp_values = values

    def del_values(self):
        del self._my_widgets[0].value
        del self._my_widgets[1].value

    values = property(get_values, set_values, del_values)
    
    def get_levels(self):
        if hasattr(self, '_my_widgets'): 
            return [self._my_widgets[0].get_levels(), self._my_widgets[1].get_levels() ]
        elif hasattr(self, '__tmp_levels'):
            return self.__tmp_levels
        else:
            return None

    def set_levels(self, levels):
        if hasattr(self, '_my_widgets'): 
            self._my_widgets[0].set_levels(levels[0])
            self._my_widgets[1].set_levels(levels[1])
        elif hasattr(self, '__tmp_levels'):
            # probably trying to set the value before the textarea is initialised
            self.__tmp_levels = levels

    levels = property(get_levels, set_levels)

    def get_editable(self):
        return False

    def set_editable(self, value):
        pass

    def del_editable(self):
        pass

    editable = property(get_editable, set_editable, del_editable)

class activeCheckBox(npyscreen.RoundCheckBox):
  def when_value_edited(self):
    self.parent.reactToChange(self)

class activeFormControlCheckbox(npyscreen.FormControlCheckbox):
  def when_value_edited(self):
    self.parent.reactToChange(self)

class activeTitleSlider(npyscreen.TitleSlider):
  def when_value_edited(self):
    self.parent.reactToChange(self)

class ConfirmCancelPopup(npyscreen.ActionPopup):
    def on_ok(self):
        self.value = True
    def on_cancel(self):
        self.value = False

#####################################################
## App and Forms
#####################################################

class MyAaptosCliApp(npyscreen.NPSAppManaged):
    """This application class serves as a wrapper for the initialization of curses
       and also manages the actual forms of the application"""

    keypress_timeout_default = 10

    def __init__(self,soapProxy=None,loggerEnabled=None):
        super(MyAaptosCliApp, self).__init__()
        self.soapProxy=soapProxy
        self.loggerEnabled=loggerEnabled

    def onStart(self):
        # the SOAP client
        if self.soapProxy is None:
          self.soapProxy = AaptosSOAP.SOAPProxy("http://%s:%d/"%(AaptosSettings.SOAPServer,AaptosSettings.SOAPPort))
        # the forms
        self.addForm("MAIN", MainForm , name = "Welcome to Aaptos", minimum_lines=20, columns=108)
        for instr in self.instruments():
          self.addFormClass("SETTINGS%s"%instr, SettingsForm, name = "%s Settings"%instr, minimum_lines=20, columns=108)

    def instruments(self):
        # Fetch and cache the instruments. 
        # Caching is made to enforce consistency.
        if not hasattr(self,"instruments_"):
          instruments_ = list(self.soapProxy.getStatus().keys())
        return instruments_

class SettingsForm(npyscreen.ActionForm):

   def create(self):
     aaptos = self.parentApp.soapProxy
     psunit = self.name.split()[0]
     logging.debug('creating SettingsForm with name %s => psunit = %s'%(self.name,psunit))
     try:
       (V,I) = aaptos.getInstrumentConfiguration(psunit)
     except socket.error:
       (V,I) = (0,0) # no error... it will anyway come if we try to save
     logging.debug('instrument configuration: V:%d I:%d'%(V,I))
     self.voltage      = self.add(npyscreen.TitleText, name  = "Voltage (V):", value = str(V))
     self.currentLimit = self.add(npyscreen.TitleText, name  = "Current (A):", value = str(I))
     self.nextrely += 2

     #levels are, for each instrument, min, max, warning, danger
     #min and max are fixed by the hardware, warning and danger are just for display

     levels = getattr(self.parentApp.getForm("MAIN"),psunit).get_levels()
     logging.debug('levels: %s'%str(levels))
     try:
       curMin = aaptos.invoke("%s.getMinCurrentLimit"%psunit,[])
       curMax = aaptos.invoke("%s.getMaxCurrentLimit"%psunit,[])
       voltMin = aaptos.invoke("%s.getMinVoltage"%psunit,[])
       voltMax = aaptos.invoke("%s.getMaxVoltage"%psunit,[])
       logging.debug('got levels from device: %s'%str((voltMin,voltMax,curMin,curMax)))
     except socket.error:
       curMin = levels[1][0]
       curMax = levels[1][3]
       voltMin= levels[0][0]
       voltMax= levels[0][3]
       logging.debug('got exception while retrieving levels')

     self.voltageWarning = self.add(TitleGauge, name = "Voltage Warning Level", unit="V", step=0.1, 
                                                levels=(voltMin,voltMin,voltMax,voltMax), value=levels[0][1])
     self.voltageDanger  = self.add(TitleGauge, name = "Voltage Danger Level",  unit="V", step=0.1,
                                                levels=(voltMin,voltMin,voltMin,voltMax), value=levels[0][2])
     self.currentWarning = self.add(TitleGauge, name = "Current Warning Level", unit="A", step=0.01,
                                                levels=(curMin,curMin,curMax,curMax), value=levels[1][1])
     self.currentDanger  = self.add(TitleGauge, name = "Current Danger Level",  unit="A", step=0.01,
                                                levels=(curMin,curMin,curMin,curMax), value=levels[1][2])

   def on_ok(self):
     psunit = self.name.split()[0]
     logging.debug('about to save settings to psunit = %s'%psunit)
     # set the warning/danger levels
     volt_tmp = self.voltageWarning.get_levels()
     curr_tmp = self.currentWarning.get_levels()
     getattr(self.parentApp.getForm("MAIN"),psunit).set_levels([(volt_tmp[0],self.voltageWarning.value,self.voltageDanger.value,volt_tmp[3]),
                                                                (curr_tmp[0],self.currentWarning.value,self.currentDanger.value,curr_tmp[3])])
     
     # set the I,V values to the hardware     
     aaptos = self.parentApp.soapProxy
     try:
       aaptos.configureInstrument(psunit,V=float(self.voltage.value), I=float(self.currentLimit.value))
     except socket.error as e:
       npyscreen.notify_wait("[Errno %s] %s"%(e.errno,e.strerror), title="Error", form_color='STANDOUT', wrap=True, wide=False)
       self.editing = False
       self.parentApp.switchFormPrevious()
     except ValueError as e:
       npyscreen.notify_wait(e.message,title="Error", form_color='STANDOUT', wrap=True, wide=False)
     else:
       self.editing = False
       self.parentApp.switchFormPrevious()

   def on_cancel(self):
     self.editing = False
     self.parentApp.switchFormPrevious()


class MainForm(npyscreen.FormBaseNewWithMenus):
    """This form class defines the display that will be presented to the user."""

    def update_clock(self):
       self.date_widget.value = datetime.now().strftime("%b %d %Y %H:%M:%S")
       self.display()

    def update_values(self):  #TODO: is that thread-safe?
       aaptos = self.parentApp.soapProxy
       while(1):
         try:
           # update V,I for each PS
           self.values = aaptos.getStatus()
         except socket.error:
           self.setStatus(False)
         else:
           self.setStatus(True)
         sleep(10)

    def update_fields(self):
       aaptos = self.parentApp.soapProxy
       try:
         # update V,I for each PS
         values = aaptos.getStatus()   #TODO: this is "very" slow and should run in the background. update_fields should just pick the last readings
         #values = self.values
         for key,value in dict(values).items():
           getattr(self,key).values=list(value)
         # on/off state
         self.enablePower.value = aaptos.isOn()
       except socket.error:
         self.setStatus(False)
       else:
         self.setStatus(True)

       # logger status
       if self.parentApp.loggerEnabled is not None:
         self.dblog.value = self.parentApp.loggerEnabled.isSet()
         self.lograte.update(clear=True)
       self.lograte.value = AaptosSettings.PoolDelay

    def check_errors(self):
       aaptos = self.parentApp.soapProxy
       try:
         for device,errors in aaptos.getErrors().items():
           errorMessages = ["[Errno %s] %s"%(error[0],error[1]) for error in errors]
           if len(errorMessages):
              message = "\n".join(errorMessages)
              npyscreen.notify_confirm(message, title="Error on device %s"%device, editw=1)
       except socket.error:
         self.setStatus(False)
       else:
         self.setStatus(True)
       
    def while_waiting(self):
       self.update_clock()
       self.update_fields()
       self.check_errors()

    def reactToChange(self, widget):
        aaptos = self.parentApp.soapProxy
        if widget.name=="Log values":
          if self.parentApp.loggerEnabled is not None:
            if self.dblog.value:
              self.parentApp.loggerEnabled.set()
            else:
              self.parentApp.loggerEnabled.clear()
        elif widget.name=="Enabled":
          try:
            if self.enablePower.value:
              aaptos.turnOn()
              self.hideDisplay.value = True
            else:
              aaptos.turnOff()
              self.hideDisplay.value = True
          except socket.error:
            self.setStatus(False)
          else:
            self.setStatus(True)
        elif widget.name=="Lock front panel":
          try:
            aaptos.lock(self.remoteLock.value)
          except socket.error:
            self.setStatus(False)
          else:
            self.setStatus(True)
        elif widget.name=="Period":
          AaptosSettings.PoolDelay = self.lograte.value
        elif widget.name=="Hide device displays":
          try:
            devices = aaptos.getDevices()
            for dev in devices: 
              if not self.hideDisplay.value:
                aaptos.invoke("%s.clearDisplayMessage"%dev,None)
              elif self.enablePower.value:
                aaptos.invoke("%s.displayMessage"%dev,"AAPTOS ON")
              else:
                aaptos.invoke("%s.displayMessage"%dev,"AAPTOS OFF")
          except socket.error:
            self.setStatus(False)
          else:
            self.setStatus(True)

    def getDefaultLevels(self,instrument):
        aaptos = self.parentApp.soapProxy
        try:
          curMin = float(aaptos.invoke("%s.getMinCurrentLimit"%instrument,[]))
          curMax = float(aaptos.invoke("%s.getMaxCurrentLimit"%instrument,[]))
          voltMin = float(aaptos.invoke("%s.getMinVoltage"%instrument,[]))
          voltMax = float(aaptos.invoke("%s.getMaxVoltage"%instrument,[]))
        except socket.error:
          curMin = 0.
          curMax = 1.
          voltMin= 0.
          voltMax= 25.
          self.setStatus(False)
        else:
          self.setStatus(True)
        return [(voltMin,(voltMax-voltMin)/3.,2.*(voltMax-voltMin)/3.,voltMax),(curMin,(curMax-curMin)/3.,2*(curMax-curMin)/3.,curMax)]

    def setStatus(self,online):
        if online:
          self.status_widget.color="GOOD"
          self.status_widget.value="ONLINE"
        else:
          self.status_widget.color="CRITICAL"
          self.status_widget.value="OFFLINE"

    def create(self):
        # time info on top
        self.date_widget = self.add(npyscreen.FixedText, value=datetime.now().strftime("%b %d %Y %H:%M:%S"), editable=False)
        self.nextrely -= 1

        # a marker ONLINE/OFFLINE
        self.status_widget = self.add(npyscreen.FixedText, value="OFFLINE", editable=False, color="CRITICAL", relx=96)
        self.nextrely += 1

        # name, voltage, current
        #self.values = None
        #t = Thread(target=self.update_values) #TODO: is this correct?
        #t.setDaemon(True)
        #t.start()
        logging.debug("setting initial gauges")
        aaptos = self.parentApp.soapProxy
        try:
          values = aaptos.getStatus()
        except socket.error as e:
          values = { }
          self.setStatus(False)
        else:
          self.setStatus(True)
        logging.debug("status: %s"%str(values))
        rely = self.nextrely
        relx = 3
        for instr,vals in values.items():
          setattr(self,instr,self.add(PowerBox, name=instr, levels=self.getDefaultLevels(instr),
                                                values=vals, width=50, height=4, relx=relx, rely=rely))
          if relx==55:
            relx = 3
            rely = self.nextrely
          else:
            relx = 55
        self.nextrely += 2

        # options
        logging.debug("setting options")
        self.enablePower = self.add(activeCheckBox, value=False, name="Enabled", width=50)
        self.remoteLock  = self.add(activeCheckBox, value=False, name="Lock front panel", width=50)
        self.hideDisplay = self.add(activeCheckBox, value=True, name="Hide device displays", width=50)
        self.dblog       = self.add(activeFormControlCheckbox, value=False, name="Log values", color = "NO_EDIT", width=50)
        self.lograte     = self.add(activeTitleSlider, width=50, relx=5, lowest=1, out_of=60, name="Period")
        self.dblog.addVisibleWhenSelected(self.lograte)
        if self.parentApp.loggerEnabled is not None:
          self.dblog.value = self.parentApp.loggerEnabled.isSet()
          self.lograte.value = AaptosSettings.PoolDelay
          self.dblog.updateDependents()
        else:
          self.dblog.name = "Log values (Not available)"
          self.dblog.color = "NO_EDIT"
          self.dblog.editable=False
          self.dblog.value = False
          self.dblog.updateDependents()

        # The menus are created here.
        self.menu = self.add_menu(name="File", shortcut="^F")
        self.menu.addItemsFromList([ ("Recall",self.do_recall,"^R"),
                                     ("Save",self.do_save,"^S") ] )
        self.m1s1 = self.menu.addNewSubmenu("Settings", "^E")
        for instr in self.parentApp.instruments():
          self.m1s1.addItem("%s settings"%instr, self.do_settings, None, None, (instr,))
        self.m1s1.addItem("Set SOAP server",self.do_soapServer,"^S")
        self.menu.addItem("Quit",self.do_quit,"^Q")
        #TODO: for now, settings = V,I for each instrument. More could be done with the devices themselves.

        # The logo.
        self.logo = self.add(npyscreen.MultiLineEdit, rely=self.nextrely-3, relx=75, value="""
          WWWWWW
        WW  W  W
       WW  WW W
      WW   WWW
      W    W
     WW   W W W
     WW   WWWWW
     WW     WW
     WW    WW
     WWWWWWW
      WWWW
                 """, editable=False )
 
    def do_recall(self):
      F = ConfirmCancelPopup(name="Memory to load settings from:", color="STANDOUT")
      F.preserve_selected_widget = True
      mlw = F.add(npyscreen.SelectOne,max_height=3, value = [0,], values = ["Memory 1","Memory 2","Memory 3"], scroll_exit=True)
      mlw_width = mlw.width-1
      F.editw = 1
      F.edit()
      if F.value:
        try:
          aaptos = self.parentApp.soapProxy
          aaptos.recall(mlw.value[0]+1)
        except socket.error as e:
          npyscreen.notify_wait("[Errno %s] %s"%(e.errno,e.strerror), title="Error", form_color='STANDOUT', wrap=True, wide=False)

    def do_save(self):
      F = ConfirmCancelPopup(name="Memory to save settings to:", color="STANDOUT")
      F.preserve_selected_widget = True
      mlw = F.add(npyscreen.SelectOne,max_height=3, value = [0,], values = ["Memory 1","Memory 2","Memory 3"], scroll_exit=True)
      mlw_width = mlw.width-1
      F.editw = 1
      F.edit()
      if F.value:
        try:
          aaptos = self.parentApp.soapProxy
          aaptos.save(mlw.value[0]+1)
        except socket.error as e:
          npyscreen.notify_wait("[Errno %s] %s"%(e.errno,e.strerror), title="Error", form_color='STANDOUT', wrap=True, wide=False)

    def do_settings(self, psunit):
      logging.debug('do_settings for psunit = %s'%psunit)
      self.parentApp.switchForm('SETTINGS'+psunit)
      
    def do_soapServer(self):
      aaptos = self.parentApp.soapProxy
      F = ConfirmCancelPopup(name="SOAP server URL:", color="STANDOUT")
      F.preserve_selected_widget = True
      mlw = F.add(npyscreen.TitleText, name  = "URL:", value = str(aaptos.proxy))
      mlw_width = mlw.width-1
      F.editw = 1
      F.edit()
      if F.value:
        aaptos.proxy = mlw.value

    def do_quit(self):
      if npyscreen.notify_ok_cancel("Quit the AAPTOS client?", title="Confirm", form_color='STANDOUT', wrap=True, editw = 1):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()

if __name__ == '__main__':
    TA = MyAaptosCliApp()
    TA.run()

