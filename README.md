# Raspi-Cam-Controller

Configure Raspberry interface
-----------------------------
Enable I2C:

    sudo raspi-config

In this menu you have to navigate to Interface Options and enable I2C

Installing from PyPI
--------------------

Install adafruit-blinka:

    sudo python3 -m pip install --force-reinstall adafruit-blinka
    
Install adafruit-motorkit:

    sudo pip3 install adafruit-circuitpython-motorkit

Usage
-----
Clone git repository:

    git clone ...
  
You have to clone this repository on your Raspberry and on your local computer.
After cloning this repository, you have to start the raspi_server.py file.
You can access the server with the gui_client.py file on your local computer.
