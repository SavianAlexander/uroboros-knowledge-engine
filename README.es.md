# Motor de Base de Datos de Conocimiento Uroboros

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Estado de Compilación" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="Licencia" />
  <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Versión de Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/código%20style-ponytail-indigo?style=flat-square" alt="Estilo de Código" />
</p>

---

## Acerca de Uroboros

Uroboros es un motor de base de datos ligero y autocontenido para la gestión, indexación y exploración semántica de archivos locales. Construido con componentes core minimalistas de cero dependencias, sirve como cerebro central para la búsqueda y extracción de texto en directorios de trabajo. Está diseñado para ingerir, observar, etiquetar y buscar documentos automáticamente sin requerir bases de datos vectoriales externas ni modelos pesados en tiempo de ejecución.

### Público Objetivo
- **Desarrolladores e Investigadores**: Búsqueda en bases de código locales, documentación técnica, papers de investigación y hojas de cálculo.
- **Equipos enfocados en Privacidad**: Procesamiento local de anotaciones, textos OCR e indexación de registros sin transmitir datos fuera de redes internas.
- **Ingenieros Minimalistas**: Uso de herramientas estándar de SQLite y pipelines locales para lograr velocidades extremas con bajo consumo de CPU.

---

## Arquitectura y Motores Centrales

### 1. Arquitectura de Búsqueda Híbrida
Uroboros integra un sistema de búsqueda híbrido de dos niveles:
- **Motor de Búsqueda Léxico/FTS5**: Indexa archivos, anotaciones y títulos en tablas FTS5 de SQLite, expandiendo dinámicamente sinónimos en las consultas.
- **MiniVectorEngine**: Un modelo de espacio vectorial (VSM) en Python puro que utiliza pesos TF-IDF y similitud de coseno para clasificar y rankear conceptos.

### 2. Bucle Observador de Directorios Activos
Un monitor de archivos en segundo plano vigila los estados de las rutas en tiempo real, ejecutando hilos concurrentes `ThreadPoolExecutor` para extraer contenido cuando ocurren cambios.

### 3. Reglas de Etiquetado Automatizado por Prioridad
Las rutas ingresadas se evalúan contra expresiones regulares ordenadas por nivel de prioridad, aplicando etiquetas personalizadas a los registros en la base de datos.

---

## Características Principales

- **Control de Umbral de Similitud**: Filtra los resultados semánticos dinámicamente mediante un slider de coincidencia de coseno (0-100%).
- **Filtros Multi-etiqueta Apilables**: Apila filtros usando lógica `AND` (intersección) u `OR` (unión).
- **Bookmarks y Macros**: Guarda consultas complejas y expansiones de macros directamente en SQLite.
- **Exportación PDF Personalizable**: Genera catálogos de ReportLab con títulos personalizados y paletas cromáticas (*Índigo*, *Carmesí*, *Esmeralda*, *Grafito*).
- **Copias de Seguridad Periódicas**: Programación de instantáneas automáticas de la base de datos.

---

## Guía Visual del Sistema

Aquí tienes una guía visual de las vistas y la interfaz de administración de Uroboros:

### 1. Vista del Panel Principal (Dashboard)
El centro de control principal que muestra el estado de la base de datos, el árbol de directorios activos, el gráfico de distribución de tipos de archivo, la línea de tiempo de indexación y la nube de etiquetas de frecuencia de palabras.

![Panel Principal](docs/screenshots/dashboard_view.png)

### 2. Búsqueda y Gráfico de Conexión de Etiquetas
Busca archivos con filtros de similitud, previsualiza documentos en tiempo real y visualiza el gráfico interactivo de conexiones de etiquetas de red.

![Búsqueda y Gráfico](docs/screenshots/search_results_view.png)

### 3. Configuración y Reglas Automatizadas
Configura reglas de etiquetado automático mediante expresiones regulares, sinónimos, favoritos de búsqueda, respaldos automáticos y nodos de sincronización LAN.

![Configuración de Reglas](docs/screenshots/config_rules_view.png)

### 4. Asistente Conversacional de LLM
Haz preguntas al asistente neuronal local sobre el conocimiento almacenado, estadísticas de consultas y resúmenes de documentos con enlaces de cita de fuentes automáticos.

![Asistente Conversacional](docs/screenshots/chat_view.png)

---

## Instalación y Configuración

1. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicializar y Escanear**:
   Crea las tablas SQLite e indexa la carpeta `dumps/`:
   ```bash
   python know.py init
   python know.py index dumps
   ```

3. **Iniciar Servidor**:
   ```bash
   python main.py
   ```
   Abre `http://127.0.0.1:8000` en tu navegador.

---

## Ejecución de Pruebas

Ejecuta el conjunto de pruebas automáticas de la API y base de datos:
```bash
pytest test_api.py test_db.py
```
