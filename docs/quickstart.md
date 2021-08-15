# Python version

Python-3.6

# Create venv, install requirements and start app

```
$ cd ~
$ mkdir venv
$ cd venv
$ virtualenv -p python3.6 san_exporter

$ cd ~/git
$ git clone https://github.com/vCloud-DFTBA/san_exporter

$ source /venv/san_exporter/bin/activate

$ cd git/san_exporter
$ pip install -r requirements.txt
```

# Setup the 3parclient for simulator 3par Storage

```
$ cd ~/git
$ git clone https://github.com/hpe-storage/python-3parclient.git
$ cd ~/venv
$ virtualenv -p python3.6 3parclient
$ source ~/venv/3parclient/bin/active
$ cd ~/git/python-3parclient
$ pip install -r requirements.txt

# Simulator 3par Storage
$ cd ~/git/python-3parclient
$ python test/HPE3ParMockServer_flask.py -port 5001 -user hpe3par_admin -password hpe3par_password -debug
```

# Start app
```
$ sudo python3 /git/san-exporter/manage.py

# Go to the address "http://localhost:8888" to see the metrics

```

