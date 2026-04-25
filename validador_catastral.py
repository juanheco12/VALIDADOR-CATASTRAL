# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .validador_dialog import ValidadorDialog

class ValidadorCatastral1040:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = u'&Validador Res 1040'
        self.dlg = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        if not os.path.exists(icon_path):
            icon_path = ':/images/themes/default/mActionCalculateField.svg'
            
        self.action = QAction(QIcon(icon_path), u"Validar Área (Res 1040)", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        self.iface.removePluginMenu(self.menu, self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dlg:
            self.dlg = ValidadorDialog(self.iface)
            self.dlg.setWindowTitle("Validación Catastral - Res 1040")
        
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
