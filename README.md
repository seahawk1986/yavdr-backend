# yavdr-backend
A prototype for a (mostly) RESTful API to control yaVDR.
## Requirements
For Ubuntu 18.04 you need to install the following packages (in addition to a [yavdr-ansible installation using the bionic branch](https://github.com/yavdr/yavdr-ansible/tree/bionic)):
```
sudo apt-get install python3-flask python3-flask-restful pydbus2vdr
```

## Starting the development server
To start the development server on Port 5000 run the included `run.sh` script.
