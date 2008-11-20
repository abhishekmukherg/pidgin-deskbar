#!/usr/bin/env python
"""
Pidgin deskbar Plugin
    Searches through Pidgin contacts and opens conversations
"""

import dbus
import subprocess
from time import sleep

DEBUG = True

PURPLE_CONV_TYPE_IM = 1

class Pidgin(object):
    """
    Connection to a pidgin service
    """
    @staticmethod
    def singleton(force_open=False):
        """
        returns a dbus connection to pidgin or None if one is not available. If
        force_open is True, we will create an instance
        """
        pidgin = Pidgin.service()
        if pidgin == None and force_open:
            Pidgin.start()
            i = 0
            while pidgin == None and i < 5:
                sleep(i)
                pidgin = Pidgin.service()
            assert pidgin != None, "Could not bring up pidgin after 10 seconds"
        return pidgin

    @staticmethod
    def service():
        """
        Open a connection to a running pidgin service. If pidgin is not
        running, this will return None
        """
        try:
            bus = dbus.SessionBus()
            obj = bus.get_object("im.pidgin.purple.PurpleService",
                    "/im/pidgin/purple/PurpleObject")
            pidgin = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
            return pidgin
        except dbus.exceptions.DBusException:
            LOGGER.warning("Pidgin service not started")
            pidgin = None
            return None
    
    @staticmethod
    def start():
        """
        Start a pidgin instance
        """
        subprocess.Popen(["pidgin"])
