"""
A simplified PurpleContact for use in pidgin deskbar
"""

import xml.dom.minidom
from .buddy import Buddy
from .pidgin import Pidgin

class Contact(object):
    def __init__(self, element):
        assert element != None
        self.buddies = []
        self.contact = None
        self._make_buddies(element)
        assert len(self.buddies) > 0

    def _make_buddies(self, element):
        for buddy in element.getElementsByTagName("buddy"):
            self.buddies.append(Buddy(buddy))

        if (self.contact == None and len(self.buddies) > 0 and
                self.buddies[0].buddy):
            pidgin = Pidgin.singleton()
            if pidgin != None:
                self.contact = pidgin.PurpleBuddyGetContact(
                        self.buddies[0].buddy)

    def __unicode__(self):
        return u'<Contact %s>'%' '.join((unicode(bud) for bud in self.buddies))
    def __str__(self):
        return str(unicode(self))

    def is_online(self):
        return any(buddy.is_online for buddy in self.buddies)

    def chat(self):
        try:
            online_acct = (buddy for buddy in self.buddies
                                if buddy.is_online).next()
        except StopIteration:
            online_acct = self.buddies[0]

        online_acct.open_chat()

    def query(self, text):
        assert text == text.lower()
        def names(obj):
            yield obj.alias()
            for buddy in obj.buddies:
                yield buddy.name
                yield buddy.alias
        if any(text in name.lower() for name in names(self)):
            return True
        return False

    def alias(self):
        pidgin = Pidgin.singleton()
        if pidgin == None:
            return self._buddies[0].alias
        if self.contact == None:
            self.contact = pidgin.PurpleBuddyGetContact(self.buddies[0].buddy)
            assert self.contact != None, ("Could not get a contact id but"+
                                          " pidgin is running")
        return pidgin.PurpleContactGetAlias(self.contact)
