#!/usr/bin/env python

import xml.dom.minidom
import pidgindeskbar.pidgin_blist_module

m = pidgindeskbar.pidgin_blist_module.PidginBlistModule()
m.initialize()
m.query("jared")
