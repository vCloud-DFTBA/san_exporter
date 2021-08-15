# Prepare

Python3

# Create venv, install requirements and start app

```
$ cd ~
$ mkdir venv
$ cd venv
$ virtualenv -p python3 san_exporter

$ cd ~
$ git clone git@github.com:vCloud-DFTBA/san_exporter.git
$ cd ~/san_exporter

$ source ~/venv/san_exporter/bin/activate

$ pip install -r requirements.txt
```

# Setup the 3parclient for simulator 3PAR storage

```
$ cd ~
$ git clone https://github.com/hpe-storage/python-3parclient.git
$ cd ~/venv
$ virtualenv -p python3 3parclient
$ source ~/venv/3parclient/bin/activate
$ cd ~/python-3parclient
$ pip install -r requirements.txt
$ python test/HPE3ParMockServer_flask.py -port 5001 -user hpe3par_admin -password hpe3par_password -debug
```

# Start app on the same machine
```
cd ~/san_exporter
$ cp examples/3par_config.yml config.yml
$ python3 manage.py

# Go to the address "http://localhost:8888" to see the metrics
```
