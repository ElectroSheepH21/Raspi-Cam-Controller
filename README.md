# Raspi-Cam-Controller

## Usage
### Configure Raspberry interface
To enable I2C you have to open the Raspberry Pi configuration tool:

    sudo raspi-config
    
Navigate in this menu to "Interface Options" and enable I2C

### Installing from PyPI

Install adafruit-blinka:

    sudo python3 -m pip install --force-reinstall adafruit-blinka
    
Install adafruit-motorkit:

    sudo pip3 install adafruit-circuitpython-motorkit

### Clone git repository
Clone the repository for needed files:

    git clone https://github.com/ElectroSheepH21/Raspi-Cam-Controller.git
  
You have to clone this repository on your Raspberry and on your local computer.
After cloning this repository, you have to start the raspi_server.py file.
You can access the server with the gui_client.py file on your local computer.

### Install motionEye(optional)

Official Website: [moitionEye](https://github.com/ccrisan/motioneye)

Follow the installation instructions for your OS
