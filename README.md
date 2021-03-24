aaptos
======

Agilent APplicaTiOn Service

This application has multiple purposes. The goal is to implement all of these functionalities but the initial release will be much limited.
- access Agilent power supplies via RS-232
- read and log currents and voltages 
- remote control of the power supplies
- SOAP interface

Installation
------------

```
sudo yum install python-virtualenv
virtualenv --python=python2 venv-aaptos-py2
source venv-aaptos-py2/bin/activate
python -m pip install --upgrade pip
python -m pip install pyserial npyscreen SOAPpy storm
```

Running
-------

Start the daemon (once): `python Aaptos.py -D start`

As long as the daemon is running, the client can then be started simply as `python AaptosCli.py`
