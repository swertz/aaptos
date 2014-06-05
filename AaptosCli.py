import npyscreen
import AaptosSOAP
from datetime import datetime
import threading
import time
import types
import socket
        
#####################################################
## Widgets - to be used: PowerBox
#####################################################

class GaugeWidget(npyscreen.Slider):
    """A slider with custom label"""
    def __init__(self, screen, *args, **keywords):
      super(GaugeWidget, self).__init__(screen, *args, **keywords)
      self.levels = (0,50,100, 100.1)
      self.unit = "a.u."
      if 'levels' in keywords:
        self.levels = keywords['levels']
      if 'unit' in keywords:
        self.unit = keywords['unit']

    def translate_value(self):
      stri = "%6.3f %s" % (self.value, self.unit)
      return stri

    def set_levels(self,levels):
      self.lowest = levels[0]
      self.warning = levels[1]
      self.maximum = levels[2]
      self.out_of = levels[3]
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
            raise ValueError

        else:
            self.__value = val

        if self.__value > self.out_of: raise ValueError
        if hasattr(self, 'levels'):
          if val < self.levels[1] :
            self.color = "SAFE"
          elif val < self.levels[2]:
            self.color = "WARNING"
          else:
            self.color = "DANGER"

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
          self.soapProxy = AaptosSOAP.SOAPProxy("http://localhost:8080/")
        # the forms
        self.addForm("MAIN", MainForm , name = "Welcome to Aaptos", minimum_lines=20, columns=108)
        self.addFormClass("SETTINGSP6V",  SettingsForm, name = "P6V Settings" , minimum_lines=20, columns=108)
        self.addFormClass("SETTINGSP25V", SettingsForm, name = "P25V Settings", minimum_lines=20, columns=108)
        self.addFormClass("SETTINGSM25V", SettingsForm, name = "M25V Settings", minimum_lines=20, columns=108)
        self.addFormClass("SETTINGSP20V", SettingsForm, name = "P20V Settings", minimum_lines=20, columns=108)


class SettingsForm(npyscreen.ActionForm):

   def create(self):
     aaptos = self.parentApp.soapProxy
     psunit = self.name.split()[0]
     try:
       (V,I) = aaptos.getInstrumentConfiguration(psunit)
     except socket.error:
       (V,I) = (0,0) # no error... it will anyway come if we try to save
     self.voltage      = self.add(npyscreen.TitleText, name  = "Voltage (V):", value = str(V))
     self.currentLimit = self.add(npyscreen.TitleText, name  = "Current (A):", value = str(I))
     self.nextrely += 2

     #levels are, for each instrument, min, max, warning, danger
     #min and max are fixed by the hardware, warning and danger are just for display

     levels = getattr(self.parentApp.getForm("MAIN"),psunit).get_levels()
     try:
       curMin = aaptos.invoke("%s.getMinCurrentLimit"%psunit,[])
       curMax = aaptos.invoke("%s.getMaxCurrentLimit"%psunit,[])
       voltMin = aaptos.invoke("%s.getMinVoltage"%psunit,[])
       voltMax = aaptos.invoke("%s.getMaxVoltage"%psunit,[])
       #curMin = getattr(aaptos,"%s.getMinCurrentLimit"%psunit)()
       #curMax = getattr(aaptos,"%s.getMaxCurrentLimit"%psunit)()
       #voltMin = getattr(aaptos,"%s.getMinVoltage"%psunit)()
       #voltMax = getattr(aaptos,"%s.getMaxVoltage"%psunit)()
     except socket.error:
       curMin = levels[1][0]
       curMax = levels[1][3]
       voltMin= levels[0][0]
       voltMax= levels[0][3]

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

    def update_fields(self):
       aaptos = self.parentApp.soapProxy
       try:
         # update V,I for each PS
         values = aaptos.getStatus()
         for key,value in dict(values).iteritems():
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

    def while_waiting(self):
        self.update_clock()
        self.update_fields()

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
            else:
              aaptos.turnOff()
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

    def getDefaultLevels(self,instrument):
        aaptos = self.parentApp.soapProxy
        try:
          curMin = aaptos.invoke("%s.getMinCurrentLimit"%instrument,[])
          curMax = aaptos.invoke("%s.getMaxCurrentLimit"%instrument,[])
          voltMin = aaptos.invoke("%s.getMinVoltage"%instrument,[])
          voltMax = aaptos.invoke("%s.getMaxVoltage"%instrument,[])
          #curMin = getattr(aaptos,"%s.getMinCurrentLimit"%instrument)()
          #curMax = getattr(aaptos,"%s.getMaxCurrentLimit"%instrument)()
          #voltMin = getattr(aaptos,"%s.getMinVoltage"%instrument)()
          #voltMax = getattr(aaptos,"%s.getMaxVoltage"%instrument)()
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
        rely = self.nextrely
        aaptos = self.parentApp.soapProxy
        try:
          values = aaptos.getStatus()
        except socket.error as e:
          values = { "P6V":[0,0], "P25V":[0,0], "M25V":[0,0], "P20V":[0,0] }
          self.setStatus(False)
        else:
          self.setStatus(True)
        self.P6V  = self.add(PowerBox, name="P6V",  levels=self.getDefaultLevels("P6V"),  
                                       values=values["P6V"], width=50, height=4, rely=rely)
        self.P25V = self.add(PowerBox, name="P25V", levels=self.getDefaultLevels("P25V"), 
                                       values=values["P25V"], width=50, height=4, rely=rely, relx=55)
        rely = self.nextrely
        self.M25V = self.add(PowerBox, name="M25V", levels=self.getDefaultLevels("M25V"), 
                                       values=values["M25V"], width=50, height=4, rely=rely)
        self.P20V = self.add(PowerBox, name="P20V", levels=self.getDefaultLevels("P20V"), 
                                       values=values["P20V"], width=50, height=4, rely=rely, relx=55)
        self.nextrely += 2

        # options
        self.enablePower = self.add(activeCheckBox, value=False, name="Enabled")
        self.remoteLock  = self.add(activeCheckBox, value=False, name="Lock front panel")
        self.dblog       = self.add(activeCheckBox, value=False, name="Log values", color = "NO_EDIT")
        if self.parentApp.loggerEnabled is not None:
          self.dblog.value = self.parentApp.loggerEnabled.isSet()
        else:
          self.dblog.name = "Log values (Not available)"
          self.dblog.color = "NO_EDIT"
          self.dblog.editable=False

        # The menus are created here.
        self.menu = self.add_menu(name="File", shortcut="^F")
        self.menu.addItemsFromList([ ("Recall",self.do_recall,"^R"),
                                     ("Save",self.do_save,"^S") ] )
        self.m1s1 = self.menu.addNewSubmenu("Settings", "^E")
        self.m1s1.addItemsFromList([ ("P6V settings",  self.do_settings, None, None, ("P6V",)),
                                     ("P25V settings", self.do_settings, None, None, ("P25V",)),
                                     ("M25V settings", self.do_settings, None, None, ("M25V",)),
                                     ("P20V settings", self.do_settings, None, None, ("P20V",)),
                                     ("Set SOAP server",self.do_soapServer,"^S") ] )
        self.menu.addItemsFromList([ ("Quit",self.do_quit,"^Q") ] )
        #note: for now, settings = V,I for each instrument. More could be done with the devices themselves.
 
    def do_recall(self):
      F = ConfirmCancelPopup(name="Memory to load settings from:", color="STANDOUT")
      F.preserve_selected_widget = True
      mlw = F.add(npyscreen.SelectOne,max_height=3, value = [0,], values = ["Memory 1","Memory 2","Memory 3"], scroll_exit=True)
      mlw_width = mlw.width-1
      F.editw = 1
      F.edit()
      if F.value:
        try:
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
          aaptos.save(mlw.value[0]+1)
        except socket.error as e:
          npyscreen.notify_wait("[Errno %s] %s"%(e.errno,e.strerror), title="Error", form_color='STANDOUT', wrap=True, wide=False)

    def do_settings(self, psunit):
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
