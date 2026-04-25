# -*- coding: utf-8 -*-
def classFactory(iface):
    from .validador_catastral import ValidadorCatastral1040
    return ValidadorCatastral1040(iface)
