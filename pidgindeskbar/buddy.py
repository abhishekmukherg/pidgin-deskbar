from __future__ import absolute_import

from .pidgin import Pidgin

PURPLE_CONV_TYPE_IM = 1

class Buddy(object):
    """
    A pidgin buddy
    """
    def __init__(self, element):
        """
        Creates a pidgin buddy given an xml element
        """
        assert element
        self.element = element
        self.buddy = None
        self.account_id = None
        self._get_buddy()

    def _get_buddy(self):
        """
        Returns the buddy id for this buddy
        """
        pidgin = Pidgin.singleton()
        if pidgin:
            self.account_id = pidgin.PurpleAccountsFindAny(self.account, self.protocol)
            self.buddy = pidgin.PurpleFindBuddy(self.account_id, self.name)
        else:
            self.buddy = None


    def _get_name(self):
        """
        Returns a buddy's name
        """
        return self.element.getElementsByTagName("name")[0].firstChild.data

    def _get_alias_from_xml(self):
        """
        Returns the alias of this buddy
        """
        if self.element.getElementsByTagName("alias") > 0:
            return self.element.getElementsByTagName("alias")[0].firstChild.data
        else:
            return ""

    def _get_account(self):
        """
        Returns the account number to reach this buddy
        """
        return self.element.getAttribute("account")

    def _get_protocol(self):
        """
        Returns the protocol used to reach this buddy
        """
        return self.element.getAttribute("protocol")

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
            return pidgin.PurpleBuddyIsOnline(self.buddy) == 1
        else:
            return False

    def open_chat(self):
        """
        Opens a chat with this person
        forces open a pidgin instance
        """
        pidgin = Pidgin.singleton(True)
        pidgin.PurpleConversationNew(PURPLE_CONV_TYPE_IM, self.account_id, self.name)

    def resolved_alias(self):
        if self.buddy == None:
            self._get_buddy()
        pidgin = Pidgin.singleton()
        if pidgin == None or self.buddy == None:
            return self._get_alias_from_xml()
        else:
            return pidgin.PurpleBuddyGetAlias(self.buddy)

    def __unicode__(self):
        return u'<Buddy "%s" on "%s">' % (self.name, self.account)

    def __str__(self):
        return str(unicode(self))

    name = property(_get_name, None)
    alias = property(resolved_alias, None)
    account = property(_get_account, None)
    protocol = property(_get_protocol, None)
    is_online = property(_is_online, None)

