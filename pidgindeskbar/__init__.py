import logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
        filename="/tmp/pidgin_deskbar.log",
        filemode='a')

__all__ = [ "buddy", "contact", "pidgin_blist_action", "pidgin_blist_match",
        "pidgin_blist_module", "pidgin" ]
