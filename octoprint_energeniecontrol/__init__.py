# coding=utf-8
from __future__ import absolute_import



import octoprint.plugin

import time,os,stat

class GPIO:
    _SYS_PATH="/sys/class/gpio"
    _EXPORT_FILE=_SYS_PATH+"/export"
    _UNEXPORT_FILE=_SYS_PATH+"/unexport"
    exported_channels=[]
    warnings=True

    @classmethod
    def _gpio_root_path(cls,channel):
        return cls._SYS_PATH+"/gpio"+str(channel)

    @classmethod
    def _gpio_dir_file(cls,channel):
        return cls._gpio_root_path(channel)+"/direction"

    @classmethod
    def _gpio_value_file(cls,channel):
        return cls._gpio_root_path(channel)+"/value"

    BCM=0
    BOARD=1
    mode=BCM
    @classmethod
    def setmode(cls,mode):
        if mode==cls.BOARD:
            raise ValueError('Not supported')
        cls.mode=mode

    @classmethod
    def setwarnings(cls,warnings):
        cls.warnings=warnings

    # direction
    OUT=0
    IN=1
    @classmethod
    def setup(cls,channel,direction,initial=0):
        cls.exported_channels.append(channel)
        try:
            with open(cls._EXPORT_FILE ,'r+') as f:
                f.write(str(channel))
        except IOError:
            if cls.warnings:
                print("Warning, pin ",channel," was in use already")
        # for some reason, this sometimes takes a while
        for attempt in range(10):
            try:
                with open(cls._gpio_dir_file(channel),'r+') as f:
                    f.write('in' if direction==cls.IN else 'out')
            except:
                time.sleep(0.05)
            else:
                break
        else:
            raise IOError("Couldn't set GPIO pin direction")
        if direction==GPIO.OUT:
            cls.output(channel,initial)

    @classmethod
    def input(cls,channel):
        with open(cls._gpio_value_file(channel),'r') as f:
            value=int(f.read(1))
        return value

    # state
    LOW=0
    HIGH=1
    @classmethod
    def output(cls,channel,state):
        if state==True:
            state=1
        if state==False:
            state=0
        with open(cls._gpio_value_file(channel),'r+') as f:
            f.write(str(state))

    @classmethod
    def cleanup(cls):
        for channel in cls.exported_channels:
            with open(cls._UNEXPORT_FILE,'r+') as f:
                f.write(str(channel))
        cls.exported_channels=[]


# The GPIO pins for the Energenie module
BIT1 = 17
BIT2 = 22
BIT3 = 23
BIT4 = 27

ON_OFF_KEY = 24
ENABLE = 25

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(BIT1, GPIO.OUT)
    GPIO.setup(BIT2, GPIO.OUT)
    GPIO.setup(BIT3, GPIO.OUT)
    GPIO.setup(BIT4, GPIO.OUT)

    GPIO.setup(ON_OFF_KEY, GPIO.OUT)
    GPIO.setup(ENABLE, GPIO.OUT)

    GPIO.output(ON_OFF_KEY, False)
    GPIO.output(ENABLE, False)

    GPIO.output(BIT1, False)
    GPIO.output(BIT2, False)
    GPIO.output(BIT3, False)
    GPIO.output(BIT4, False)

# Codes for switching on and off the sockets
#       all     1       2       3       4
ON = ['1011', '1111', '1110', '1101', '1100']
OFF = ['0011', '0111', '0110', '0101', '0100']


def change_plug_state(socket, on_or_off):
    state = on_or_off[socket][3] == '1'
    GPIO.output(BIT1, state)
    state = on_or_off[socket][2] == '1'
    GPIO.output(BIT2, state)
    state = on_or_off[socket][1] == '1'
    GPIO.output(BIT3, state)
    state = on_or_off[socket][0] == '1'
    GPIO.output(BIT4, state)
    time.sleep(0.1)
    GPIO.output(ENABLE, True)
    time.sleep(0.25)
    GPIO.output(ENABLE, False)


def on(socket=0):
    change_plug_state(socket, ON)


def off(socket=0):
    change_plug_state(socket, OFF)



class EnergeniecontrolPlugin(octoprint.plugin.EventHandlerPlugin):
    def on_event(self, event, payload):
        if event == octoprint.events.Events.CONNECTED:
            init()
            on()
            GPIO.cleanup()
        elif event == octoprint.events.Events.DISCONNECTED:
            init()
            off()
            GPIO.cleanup()
    def get_update_information(*args, **kwargs):
        return dict(
            energeniecontrolplugin=dict(
                diplayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="arlohb",
                repo="OctoPrint-EnergenieControl",

                pip="https://github.com/arlohb/OctoPrint-EnergenieControl/archive/main.zip"
            )
        )

__plugin_name__ = "Energenie Control Plugin"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = EnergeniecontrolPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

