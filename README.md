# 🏗️ Validador Catastral - Resolución 1040 del IGAC

**Plugin para QGIS 3.x** que permite validar si las áreas de predios catastrales cumplen con los márgenes de tolerancia establecidos por la **Resolución 1040 de 2023** del Instituto Geográfico Agustín Codazzi (IGAC) de Colombia.

---

## 📋 ¿Qué hace este plugin?

En los procesos de conservación catastral (mutaciones, englobes, desenglobes, actualizaciones), es obligatorio verificar que la diferencia entre el **área jurídica** (registrada en escritura o certificado de tradición) y el **área geométrica** (medida directamente sobre la cartografía) no supere un porcentaje máximo de tolerancia.

Este plugin automatiza esa verificación aplicando los rangos de la **Tabla 3** de la Resolución 1040:

### Zona Urbana (o rural con comportamiento urbano)

| Rango de Área | Tolerancia (%) |
|---|---|
| ≤ 80 m² | 7% |
| > 80 m² y ≤ 250 m² | 6% |
| > 250 m² y ≤ 500 m² | 4% |
| > 500 m² | 3% |

### Zona Rural (sin comportamiento urbano)

| Rango de Área | Tolerancia (%) |
|---|---|
| ≤ 2.000 m² | 10% |
| > 2.000 m² y ≤ 1 Ha | 9% |
| > 1 Ha y ≤ 10 Ha | 7% |
| > 10 Ha y ≤ 50 Ha | 4% |
| > 50 Ha | 2% |

---

## 🚀 Funcionalidades

### 🔹 Validación Individual
- Selecciona **un polígono** en el lienzo de QGIS.
- Ingresa manualmente el **Área Jurídica** (en m² o hectáreas).
- Escoge el **tipo de zona** (Urbano / Rural).
- El plugin calcula automáticamente el **área geométrica** usando el motor elipsoidal de QGIS.
- Muestra en pantalla:
  - Área geométrica calculada.
  - Diferencia absoluta entre ambas áreas.
  - Margen de tolerancia permitido (en m² y %).
  - **Dictamen final**: ✅ *"Cumple con el margen de tolerancia"* o ❌ *"Está por fuera del margen de tolerancia – No procede"*.

### 🔹 Procesamiento Múltiple (Masivo)
- Selecciona el **campo de la tabla de atributos** que contiene el área jurídica.
- Escoge si deseas procesar:
  - **Solo los objetos seleccionados** (ideal para englobes o grupos específicos de predios).
  - **Toda la capa completa**.
- El plugin recorre cada predio y agrega automáticamente **3 nuevas columnas** a la tabla de atributos:
  - `area_geom`: Área geométrica calculada (m²).
  - `dif_m2`: Diferencia absoluta respecto al área jurídica (m²).
  - `cumple_10`: Resultado → `"CUMPLE"` o `"NO CUMPLE"`.
- Incluye **barra de progreso** en tiempo real.

---

## 📦 Instalación

### Opción 1: Instalación manual
1. Descarga o clona este repositorio.
2. Copia la carpeta completa del plugin en el directorio de plugins de QGIS:
   ```
   %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
   ```
3. Reinicia QGIS.
4. Ve a **Complementos → Administrar e instalar complementos** y activa **"Validador Catastral 1040"**.

### Opción 2: Desde ZIP
1. Descarga el repositorio como archivo ZIP.
2. En QGIS, ve a **Complementos → Administrar e instalar complementos → Instalar a partir de ZIP**.
3. Selecciona el archivo descargado e instala.

---

## 🖥️ Requisitos

- **QGIS 3.0** o superior.
- Python 3 (incluido con QGIS).
- No requiere dependencias externas adicionales.

---

## 🎯 Caso de Uso Típico

> *"Tengo un predio con escritura que dice 350 m² en zona urbana. Al medirlo en QGIS, el polígono da 338 m². ¿Pasa la validación catastral?"*

1. Abre el plugin → Pestaña **Validación Individual**.
2. Selecciona el polígono del predio en el mapa.
3. Ingresa `350` en Área Jurídica, selecciona `m²`, zona `Urbano`.
4. Clic en **Calcular y Validar**.
5. El plugin calcula:
   - Diferencia: `12 m²`
   - Tolerancia permitida (4% de 350): `14 m²`
   - ✅ **Cumple** (12 < 14).

---

## 📁 Estructura del Proyecto

```
ValidadorCatastral1040/
├── __init__.py                  # Inicializador del plugin
├── metadata.txt                 # Metadatos para QGIS
├── icon.png                     # Ícono del plugin
├── validador_catastral.py       # Clase principal (menú, toolbar)
├── validador_dialog.py          # Controlador de la interfaz
├── validador_dialog_base.ui     # Diseño de la ventana (Qt Designer)
├── validador_processor.py       # Lógica matemática (Res 1040)
└── README.md                    # Este archivo
```

---

## 📜 Marco Normativo

- **Resolución 1040 de 2023** – Instituto Geográfico Agustín Codazzi (IGAC).
- Tabla 3: *"Rangos de área catastral de terreno y porcentajes de tolerancia"*.

---

## 👤 Autor

**Juan Hernández** – Ingeniero de Sistemas  
🔗 [GitHub](https://github.com/juanheco12) · [LinkedIn](https://www.linkedin.com/in/juan-hern%C3%A1ndez-690bb7252/)

---

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y profesionales en el ámbito catastral colombiano.
