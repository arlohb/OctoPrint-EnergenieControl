# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

import time

class EnergeniecontrolPlugin(octoprint.plugin.EventHandlerPlugin):
    # 0-3 are data, 4 is on/off, 5 is enable
    pins = [17, 22, 23, 27, 24, 25]

    path="/sys/class/gpio"

    def setupPins(self):
        for pin in self.pins:
            try:
                with open(self.path+"/export" ,'r+') as f:
                    f.write(str(pin))
            except IOError:
                print("Fail")
            # for some reason, this sometimes takes a while
            for attempt in range(10):
                try:
                    with open(self.path+"/gpio"+str(pin)+"/direction",'r+') as f:
                        f.write("out")
                except:
                    time.sleep(0.05)
                else:
                    break
            else:
                raise IOError("Couldn't set GPIO pin direction")
            
            self.output(pin, 0)
    
    def output(self, pin, state):
        with open(self.path+"/gpio"+str(pin)+"/value",'r+') as f:
            f.write(str(state))

    def cleanup(self):
        for pin in self.pins:
            with open(self.path+"/unexport",'r+') as f:
                f.write(str(pin))
    
    def write(self, data):
        self.setupPins()

        self.output(self.pins[0], data[0])
        self.output(self.pins[1], data[1])
        self.output(self.pins[2], data[2])
        self.output(self.pins[3], data[3])
        time.sleep(0.1)
        self.output(self.pins[5], 1)
        time.sleep(0.25)
        self.output(self.pins[5], 0)

        self.cleanup()

    def on_event(self, event, payload):
        if event == octoprint.events.Events.CONNECTED:
            self.write([1,1,0,1])
        elif event == octoprint.events.Events.DISCONNECTED:
            self.write([1,1,0,0])

    def get_update_information(self):
        return dict(
            energeniecontrol=dict(
                diplayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="arlohb",
                repo="OctoPrint-EnergenieControl",

                stable_branch=dict(
                    name="Stable",
                    branch="main",
                    commitish=["main"],
                ),

                pip="https://github.com/arlohb/OctoPrint-EnergenieControl/archive/{target_version}.zip"
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
