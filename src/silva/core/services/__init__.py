# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf

silvaconf.extension_name('silva.core.services')
silvaconf.extension_title('Silva Core Services')
silvaconf.extension_system()

from .catalog import CatalogingTask
