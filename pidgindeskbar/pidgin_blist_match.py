import deskbar.interfaces.Match
from .pidgin_blist_action import PidginBlistAction

class PidginBlistMatch(deskbar.interfaces.Match):
    def __init__(self, contact):
        deskbar.interfaces.Match.__init__(self,
                name=contact.alias(),
                category='conversations')
        for buddy in contact.buddies:
            self.add_action(PidginBlistAction(buddy))

    def get_hash(self):
        return self.get_name()
