import deskbar.interfaces.Action
from gettext import gettext as _

class PidginBlistAction(deskbar.interfaces.Action):
    def __init__(self, buddy):
        deskbar.interfaces.Action.__init__(self, buddy.alias)
        self._buddy = buddy

    def activate(self, text=None):
        self._buddy.open_chat()

    def get_verb(self):
        return _("Chat with") + " <b>%(name)s</b> (%(status)s)"

    def get_hash(self):
        return self._buddy.name + self._buddy.account + self._buddy.protocol

    def get_icon(self):
        if self._buddy.protocol == 'prpl-aim':
            return 'im-aim'
        return None

    def get_name(self, text=None):
        if self._buddy.is_online:
            status = _(u"Online!")
        else:
            status = _(u"Offline")
        return {'name': self._name, 'status': status}
