# -*- coding: utf-8 -*-
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import QgsMapLayerProxyModel, QgsWkbTypes, QgsApplication
from .validador_processor import ValidadorProcessor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'validador_dialog_base.ui'))

class ValidadorDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(ValidadorDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        
        # Estilo oscuro con acentos teal
        dark_style = """
        QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; }
        QPushButton { background-color: #3a3f44; border: 1px solid #272b30; border-radius: 4px; padding: 6px; font-weight: bold; }
        QPushButton:hover { background-color: #008080; color: #ffffff; border: 1px solid #00aaaa; }
        QPushButton:pressed { background-color: #005959; }
        QLabel { font-weight: bold; color: #c8c8c8; }
        QLineEdit, QComboBox, QgsMapLayerComboBox, QgsFieldComboBox { background-color: #1e1e1e; border: 1px solid #444; color: #fff; padding: 4px; }
        QGroupBox { border: 1px solid #555; margin-top: 10px; padding-top: 15px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; color: #00aaaa; }
        QTabWidget::pane { border: 1px solid #444; background: #2b2b2b; }
        QTabBar::tab { background: #3a3f44; color: #aaa; padding: 8px 20px; border: 1px solid #444; border-bottom: none; }
        QTabBar::tab:selected { background: #2b2b2b; color: #00aaaa; font-weight: bold; }
        QProgressBar { border: 1px solid #444; text-align: center; color: white; }
        QProgressBar::chunk { background-color: #00aaaa; }
        QCheckBox { color: #fff; font-weight: bold; }
        """
        self.setStyleSheet(dark_style)

        # Configurar combobox de capa para mostrar solo polígonos
        self.cmbLayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        
        # Vincular el combobox de campos a la capa seleccionada
        self.cmbLayer.layerChanged.connect(self.actualizar_campos)
        self.actualizar_campos(self.cmbLayer.currentLayer())

        # Conectar botones
        self.btnValidarInd.clicked.connect(self.calcular_y_validar_ind)
        self.btnValidarMasivo.clicked.connect(self.calcular_y_validar_masivo)

    def actualizar_campos(self, layer):
        if layer:
            self.cmbCampoArea.setLayer(layer)

    def calcular_y_validar_ind(self):
        layer = self.cmbLayer.currentLayer()
        if not layer:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una capa de polígonos.")
            return

        selected_features = layer.selectedFeatures()
        if len(selected_features) != 1:
            QMessageBox.warning(self, "Atención", "Debes seleccionar exactamente un (1) predio en la capa activa para validar individualmente.")
            return
            
        feature = selected_features[0]

        texto_area = self.txtAreaJuridica.text().replace(',', '.')
        try:
            area_juridica = float(texto_area)
        except ValueError:
            QMessageBox.warning(self, "Error", "El valor del Área Jurídica no es un número válido.")
            return

        if area_juridica <= 0:
            QMessageBox.warning(self, "Error", "El Área Jurídica debe ser mayor a cero.")
            return

        unidad_index = self.cmbUnidadInd.currentIndex()
        area_juridica_m2 = area_juridica if unidad_index == 0 else area_juridica * 10000.0
        zona_index = self.cmbZonaInd.currentIndex()

        area_geometrica_m2 = ValidadorProcessor.calcular_area_geometrica(feature)
        resultado = ValidadorProcessor.validar(area_juridica_m2, area_geometrica_m2, zona_index)

        self.lblAreaGeometrica.setText(f"{resultado['area_geometrica']:,.2f} m²")
        self.lblDiferencia.setText(f"{resultado['diferencia']:,.2f} m²")
        self.lblTolerancia.setText(f"{resultado['margen_permitido']:,.2f} m² ({resultado['porcentaje_aplicado']}%)")

        if resultado['cumple']:
            self.lblResultado.setText("Cumple con el margen de tolerancia")
            self.lblResultado.setStyleSheet("color: #4CAF50; font-size: 14px;") # Verde
        else:
            self.lblResultado.setText("Está por fuera del margen de tolerancia – No procede")
            self.lblResultado.setStyleSheet("color: #F44336; font-size: 14px;") # Rojo

    def calcular_y_validar_masivo(self):
        layer = self.cmbLayer.currentLayer()
        if not layer:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una capa de polígonos.")
            return

        campo_area = self.cmbCampoArea.currentField()
        if not campo_area:
            QMessageBox.warning(self, "Error", "Debes seleccionar un campo que contenga el Área Jurídica.")
            return

        idx_campo = layer.fields().lookupField(campo_area)
        unidad_index = self.cmbUnidadMas.currentIndex()
        zona_index = self.cmbZonaMas.currentIndex()
        solo_seleccionados = self.chkSoloSeleccionados.isChecked()

        if solo_seleccionados and layer.selectedFeatureCount() == 0:
            QMessageBox.warning(self, "Atención", "Has elegido procesar sólo objetos seleccionados, pero no hay ninguno seleccionado en la capa.")
            return

        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)
        self.lblStatusMasivo.setText("Iniciando procesamiento múltiple...")
        self.lblStatusMasivo.setStyleSheet("color: #00aaaa;")

        def progress_callback(current, total):
            if total > 0:
                porcentaje = int((current / total) * 100)
                self.progressBar.setValue(porcentaje)
                self.lblStatusMasivo.setText(f"Procesando {current} de {total} predios...")
                QgsApplication.processEvents()

        try:
            ValidadorProcessor.procesar_capa_masivo(layer, idx_campo, unidad_index, zona_index, solo_seleccionados, progress_callback)
            self.lblStatusMasivo.setText("¡Procesamiento finalizado con éxito!")
            self.lblStatusMasivo.setStyleSheet("color: #4CAF50; font-weight: bold;")
            QMessageBox.information(self, "Éxito", "Se han calculado las áreas y se añadieron los campos (area_geom, dif_m2, cumple_10) a la tabla de atributos.")
        except Exception as e:
            self.lblStatusMasivo.setText("Error durante el procesamiento.")
            self.lblStatusMasivo.setStyleSheet("color: #F44336;")
            QMessageBox.critical(self, "Error", f"Ha ocurrido un error:\n{str(e)}")
        finally:
            self.progressBar.setVisible(False)
