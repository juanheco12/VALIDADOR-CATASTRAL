# -*- coding: utf-8 -*-
from qgis.core import QgsDistanceArea, QgsCoordinateReferenceSystem, QgsProject, QgsField, edit
from qgis.PyQt.QtCore import QVariant

class ValidadorProcessor:
    @staticmethod
    def get_tolerancia_porcentaje(area_juridica_m2, zona_index):
        if zona_index == 0:
            if area_juridica_m2 <= 80:
                return 7.0
            elif area_juridica_m2 <= 250:
                return 6.0
            elif area_juridica_m2 <= 500:
                return 4.0
            else:
                return 3.0
        elif zona_index == 1:
            if area_juridica_m2 <= 2000:
                return 10.0
            elif area_juridica_m2 <= 10000: # 1 Ha
                return 9.0
            elif area_juridica_m2 <= 100000: # 10 Ha
                return 7.0
            elif area_juridica_m2 <= 500000: # 50 Ha
                return 4.0
            else:
                return 2.0
        return 0.0

    @staticmethod
    def calcular_area_geometrica(feature):
        geom = feature.geometry()
        if geom.isNull():
            return 0.0
            
        da = QgsDistanceArea()
        da.setEllipsoid(QgsProject.instance().ellipsoid())
        da.setSourceCrs(QgsProject.instance().crs(), QgsProject.instance().transformContext())
        
        area_m2 = da.measureArea(geom)
        return area_m2

    @staticmethod
    def validar(area_juridica_m2, area_geometrica_m2, zona_index):
        porcentaje = ValidadorProcessor.get_tolerancia_porcentaje(area_juridica_m2, zona_index)
        margen_permitido = area_juridica_m2 * (porcentaje / 100.0)
        
        diferencia = abs(area_juridica_m2 - area_geometrica_m2)
        
        cumple = diferencia <= margen_permitido
        
        return {
            'area_geometrica': area_geometrica_m2,
            'diferencia': diferencia,
            'margen_permitido': margen_permitido,
            'porcentaje_aplicado': porcentaje,
            'cumple': cumple
        }

    @staticmethod
    def procesar_capa_masivo(layer, campo_area_idx, unidad_index, zona_index, solo_seleccionados, progress_callback=None):
        """
        Procesa la capa (completa o seleccionados), calculando y añadiendo campos con resultados.
        """
        # Añadir campos si no existen
        campos_nuevos = []
        nombres_campos = [field.name() for field in layer.fields()]
        
        if 'area_geom' not in nombres_campos:
            campos_nuevos.append(QgsField('area_geom', QVariant.Double))
        if 'dif_m2' not in nombres_campos:
            campos_nuevos.append(QgsField('dif_m2', QVariant.Double))
        if 'cumple_10' not in nombres_campos: # Abreviado a cumple_10 por limites en shapefiles (10 chars máx)
            campos_nuevos.append(QgsField('cumple_10', QVariant.String, len=20))

        if campos_nuevos:
            layer.dataProvider().addAttributes(campos_nuevos)
            layer.updateFields()

        idx_area_geom = layer.fields().lookupField('area_geom')
        idx_dif_m2 = layer.fields().lookupField('dif_m2')
        idx_cumple = layer.fields().lookupField('cumple_10')

        if idx_area_geom == -1 or idx_dif_m2 == -1 or idx_cumple == -1:
            raise Exception("No se pudieron crear los campos en la capa. Verifica que tengas permisos de escritura o no sea un formato restringido.")

        features_to_process = layer.selectedFeatures() if solo_seleccionados else list(layer.getFeatures())
        total = len(features_to_process)
        if total == 0:
            raise Exception("No hay predios para procesar.")

        count = 0

        # Bloque de edición segura
        with edit(layer):
            for feature in features_to_process:
                count += 1
                if progress_callback:
                    progress_callback(count, total)

                # Obtener área jurídica
                area_val = feature.attributes()[campo_area_idx]
                try:
                    area_juridica = float(area_val)
                    if area_juridica <= 0:
                        continue
                except (ValueError, TypeError):
                    continue

                area_juridica_m2 = area_juridica if unidad_index == 0 else area_juridica * 10000.0
                
                # Calcular y validar
                area_geometrica_m2 = ValidadorProcessor.calcular_area_geometrica(feature)
                resultado = ValidadorProcessor.validar(area_juridica_m2, area_geometrica_m2, zona_index)

                # Actualizar atributos
                feature[idx_area_geom] = round(resultado['area_geometrica'], 2)
                feature[idx_dif_m2] = round(resultado['diferencia'], 2)
                feature[idx_cumple] = "CUMPLE" if resultado['cumple'] else "NO CUMPLE"
                
                layer.updateFeature(feature)
