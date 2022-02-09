# Raspi-Cam-Controller

## Usage
### Configure Raspberry
To configure the Raspberry, you have to open the configuration tool:

    sudo raspi-config
    
- Enable I2C(needed for PCA9685):

  Interface Options --> I2C

- Enable camera(recommended):

  Interface Options --> Legacy Camera

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


