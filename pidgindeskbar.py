#!/usr/bin/env python
"""
A connection of pidgin to deskbar
"""

import logging
import os
import xml.dom.minidom
import deskbar.interfaces.Action
import deskbar.interfaces.Match
import deskbar.interfaces.Module
import deskbar.core.Utils
import dbus, dbus.exceptions
import subprocess
from time import sleep
from gettext import gettext as _

LOGGER = logging.getLogger("Pidgin Deskbar")
LOGGER_FILE = logging.FileHandler('/tmp/pidgin_deskbar', 'a')
LOGGER.addHandler(LOGGER_FILE)
LOGGER.setLevel(logging.DEBUG)

PURPLE_CONV_TYPE_IM = 1
BUDDY_LIST_FILE = os.path.expanduser(os.path.join('~', '.purple', 'blist.xml'))

HANDLERS = ["PidginBlistModule"]

class Buddy(object):
    """
    A pidgin buddy
    """
    def __init__(self, element):
        """
        Creates a pidgin buddy given an xml element
        """
        assert element
        self.name = element.getElementsByTagName("name")[0].firstChild.data
        self.account_id = None
        alias = element.getElementsByTagName("alias")
        if len(alias) > 0:
            alias_from_xml = alias[0].firstChild.data
        else:
            alias_from_xml = None
        self.alias_from_xml = alias_from_xml
        self.account = element.getAttribute("account")
        self.protocol = element.getAttribute("proto")
        self.buddy = None
        self._get_buddy()

    def _get_buddy(self):
        """
        Returns the buddy id for this buddy
        """
        assert self.buddy == None
        pidgin = Pidgin.singleton()
        if pidgin:
            try:
                self.account_id = pidgin.PurpleAccountsFindAny(self.account,
                                                                self.protocol)
                self.buddy = pidgin.PurpleFindBuddy(self.account_id, self.name)
            except dbus.exceptions.DBusException, exc:
                LOGGER.exception(exc)
                Pidgin.invalidate()
                self._get_buddy()
        else:
            self.buddy = None

    def _is_online(self):
        """
        Returns if we are online and the buddy is online
        """
        if self.buddy == None:
            self._get_buddy()
            if self.buddy == None:
                LOGGER.debug("Could not get buddy id")
                return False
        pidgin = Pidgin.singleton()
        if pidgin:
            try:
                return pidgin.PurpleBuddyIsOnline(self.buddy) == 1
            except dbus.exceptions.DBusException, exc:
                LOGGER.exception(exc)
                Pidgin.invalidate()
                return self._is_online()
        else:
            return False

    def open_chat(self):
        """
        Opens a chat with this person
        forces open a pidgin instance
        """
        pidgin = Pidgin.singleton(True)
        try:
            pidgin.PurpleConversationNew(PURPLE_CONV_TYPE_IM,
                                        self.account_id,
                                        self.name)
        except dbus.exceptions.DBusException, exc:
            LOGGER.exception(exc)
            Pidgin.invalidate()
            self.open_chat()

    def resolved_alias(self):
        """
        Returns the alias for this buddy. no matter what
        """
        if self.buddy == None:
            self._get_buddy()
        pidgin = Pidgin.singleton()
        if pidgin == None or self.buddy == None:
            return self.alias_from_xml()
        else:
            try:
                return pidgin.PurpleBuddyGetAlias(self.buddy)
            except dbus.exceptions.DBusException, exc:
                LOGGER.exception(exc)
                Pidgin.invalidate()
                self.resolved_alias()

    def __unicode__(self):
        return u'<Buddy "%s" on "%s">' % (self.name, self.account)

    def __str__(self):
        return str(unicode(self))

    alias = property(resolved_alias, None)
    is_online = property(_is_online, None)

class Contact(object):
    """
    A simplified PurpleContact for use in pidgin deskbar
    """
    def __init__(self, element):
        assert element != None
        self.buddies = []
        self.contact = None
        self._make_buddies(element)
        assert len(self.buddies) > 0

    def _make_buddies(self, element):
        """
        Fill buddies list for this contact
        """
        assert len(self.buddies) == 0, "Should not call this function twice"

        for buddy in element.getElementsByTagName("buddy"):
            self.buddies.append(Buddy(buddy))

        if (self.contact == None and len(self.buddies) > 0 and
                self.buddies[0].buddy):
            pidgin = Pidgin.singleton()
            if pidgin != None:
                try:
                    self.contact = pidgin.PurpleBuddyGetContact(
                            self.buddies[0].buddy)
                except dbus.exceptions.DBusException, exc:
                    LOGGER.exception(exc)
                    Pidgin.invalidate()
                    self._make_buddies(element)

    def __unicode__(self):
        return u'<Contact %s>' % ' '.join((unicode(bud)
                                            for bud in self.buddies))
    def __str__(self):
        return str(unicode(self))

    def is_online(self):
        """
        Returns True if this contact is currently online
        """
        return any(buddy.is_online for buddy in self.buddies)

    def chat(self):
        """
        Opens a conversation with this buddy and a protocol that they are
        logged on
        """
        try:
            online_acct = (buddy for buddy in self.buddies
                                if buddy.is_online).next()
        except StopIteration:
            online_acct = self.buddies[0]

        online_acct.open_chat()

    def query(self, text):
        """
        Checks if this buddy matches the query "text"
        """
        assert text == text.lower()
        def names(obj):
            "Generates a list of names for a Buddy"
            yield obj.alias()
            for buddy in obj.buddies:
                yield buddy.name
                yield buddy.alias
        return any(text in name.lower() for name in names(self))

    def alias(self):
        """
        Returns an alias for this buddy
        """
        pidgin = Pidgin.singleton()
        if pidgin == None:
            return self.buddies[0].alias

        try:
            if self.contact == None:
                self.contact = pidgin.PurpleBuddyGetContact(
                                                    self.buddies[0].buddy)
                assert self.contact != None, ("Could not get a contact id but"+
                                              " pidgin is running")
            return pidgin.PurpleContactGetAlias(self.contact)
        except dbus.exceptions.DBusException, exc:
            LOGGER.exception(exc)
            Pidgin.invalidate()
            self.alias()

class PidginBlistAction(deskbar.interfaces.Action):
    """
    An action for a buddy. Usually will be to a specific protocol
    """
    def __init__(self, buddy):
        deskbar.interfaces.Action.__init__(self, buddy.alias)
        self._buddy = buddy

    def activate(self, text=None):
        "Opens a chat with this Buddy"
        LOGGER.debug("PidginBlistAction was called with text: %s" % text)
        #TODO: Figure out what text is
        self._buddy.open_chat()

    def get_verb(self):
        "Returns a string for chatting with this buddy"
        return _("Chat with <b>%(name)s</b> on <b>%(screenname)s</b> "
                                                + "(%(status)s)")

    def get_hash(self):
        """
        A unique buddy is defined by having hte same name, account, and
        protocol
        """
        return self._buddy.name + self._buddy.account + self._buddy.protocol

    def get_icon(self):
        "Return the icon of the protocol"
        # FIXME: Does not currently work
        # TODO: other protocols?
        LOGGER.debug(u"Getting icon for %s, protocol %s" % (
                                                unicode(self._buddy),
                                                unicode(self._buddy.protocol)))
        if self._buddy.protocol == 'prpl-aim':
            LOGGER.info("Returning im-aim icon for %s" % str(self._buddy))
            return 'im-aim'
        return None

    def get_name(self, text=None):
        "Returns a dictionary of this buddy and his current status"
        if self._buddy.is_online:
            status = _(u"Online!")
        else:
            status = _(u"Offline")
        return {'name': self._name,
                'screenname': self._buddy.name,
                'status': status}
    # TODO: check if buddy is online

class PidginBlistMatch(deskbar.interfaces.Match):
    """
    A match grouping in deskbar. Will represent a Contact for us
    """
    def __init__(self, contact):
        deskbar.interfaces.Match.__init__(self,
                name=contact.alias(),
                category='conversations')
        for buddy in contact.buddies:
            self.add_action(PidginBlistAction(buddy))

    def get_hash(self):
        "A Match is defined by the contact name"
        return self.get_name()

class PidginBlistModule(deskbar.interfaces.Module):
    INFOS = {'icon': deskbar.core.Utils.load_icon("pidgin"),
            'name': _("Pidgin Buddy List"),
            'description': _("Start conversations with buddies"),
            'version': "1.0"
            }

    def __init__(self):
        deskbar.interfaces.Module.__init__(self)
        LOGGER.debug(str(self.INFOS))
        self.contacts = []

    def initialize(self):
        """
        Set up the instance. This will take some time
        """
        blist = xml.dom.minidom.parse(BUDDY_LIST_FILE)
        raw_contacts = blist.getElementsByTagName("contact")
        LOGGER.info("foo")
        try:
            self.contacts = [Contact(contact) for contact in raw_contacts]
        except dbus.exceptions.DBusException, exc:
            LOGGER.exception(exc)

    def query(self, qstring):
        " Find a buddy matching qstring "
        import pdb
        pdb.set_trace()
        qstringl = qstring.lower()
        results = []
        for contact in self.contacts:
            if contact.query(qstringl):
                results += [PidginBlistMatch(contact)]
        self._emit_query_ready(qstring, results)
        return results

    @staticmethod
    def has_requirements():
        return True

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

    @staticmethod
    def invalidate():
        """
        Invalidates the current pidgin handle
        """
        global PIDGIN
        LOGGER.warn("Invalidating current pidgin")
        PIDGIN = None
