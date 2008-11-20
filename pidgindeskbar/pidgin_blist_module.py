from __future__ import absolute_import

import deskbar.core.Utils
import xml.dom.minidom
import os
from gettext import gettext as _

from .pidgin_blist_match import PidginBlistMatch
from .contact import Contact

import logging
LOGGER = logging.getLogger("pidginDeskbar")

BUDDY_LIST_FILE = os.path.expanduser(os.path.join('~', '.purple', 'blist.xml'))

class PidginBlistModule(deskbar.interfaces.Module):
    INFO = {'icon':deskbar.core.Utils.load_icon('pidgin'),
            'name': _("Pidgin Buddy List"),
            'description': _("Start conversations with buddies"),
            'version': "1.0"
            }
    def initialize(self):
        blist = xml.dom.minidom.parse(BUDDY_LIST_FILE)
        raw_contacts = blist.getElementsByTagName("contact")
        LOGGER.info("foo")
        try:
            self.contacts = [Contact(contact) for contact in raw_contacts]
        except dbus.exceptions.DBusException, e:
            LOGGER.exception(e)

    def query(self, qstring):
        qstringl = qstring.lower()
        results = []
        for contact in self.contacts:
            if contact.query(qstringl):
                results += [PidginBlistMatch(contact)]
        self._emit_query_ready(qstring, results)
        return results

