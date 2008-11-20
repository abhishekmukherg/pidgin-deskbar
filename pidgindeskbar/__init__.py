import logging
logger = logging.getLogger("pidginDeskbar")
logger.setLevel(logging.DEBUG)

file = logging.FileHandler('/tmp/pidgin_deskbar', 'a')
logger.addHandler(file)

__all__ = [ "buddy", "contact", "pidgin_blist_action", "pidgin_blist_match",
        "pidgin_blist_module", "pidgin" ]
