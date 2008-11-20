#!/usr/bin/env python
"""
Pidgin deskbar Plugin
    Searches through Pidgin contacts and opens conversations
"""

import dbus
import subprocess
from time import sleep

import logging
LOGGER = logging.getLogger("pidginDeskbar")

DEBUG = True

PURPLE_CONV_TYPE_IM = 1
PIDGIN = None

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
        global PIDGIN

        if PIDGIN != None:
            return PIDGIN

        PIDGIN = Pidgin.service()
        if PIDGIN == None and force_open:
            Pidgin.start()
            i = 0
            while PIDGIN == None and i < 5:
                sleep(i)
                PIDGIN = Pidgin.service()
                break
            else:
                assert False, "Could not bring up pidgin after 10 seconds"
        return PIDGIN

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
        LOGGER.debug("Starting pidgin")
        subprocess.Popen(["pidgin"])
