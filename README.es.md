# Motor de Base de Datos de Conocimiento Uroboros (Neuro Alexander)

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Estado de Compilación" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="Licencia" />
  <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Versión de Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19.0.1-61dafb.svg?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/Innovaciones%20RAG-21-purple.svg?style=flat-square" alt="21 Innovaciones RAG" />
  <img src="https://img.shields.io/badge/M%C3%B3dulos%20de%20Dominio-134-indigo.svg?style=flat-square" alt="134 Módulos de Dominio" />
  <img src="https://img.shields.io/badge/Pruebas%20Aprobadas-100%25-brightgreen.svg?style=flat-square" alt="Pruebas Aprobadas" />
</p>

---

## Resumen Ejecutivo

**Motor de Conocimiento Uroboros** (Neuro Alexander) es una plataforma de grado empresarial, autocontenida y de cero dependencias externas para la gestión de conocimiento, recuperación semántica e indexación de documentos. Desarrollado con un backend modular en **FastAPI**, motor vectorial y léxico **SQLite FTS5**, integración con **Ollama LLM** local y una interfaz web SPA en **React 19 / Vite**, Uroboros ofrece búsqueda local en tiempo real, análisis estructural, razonamiento RAG multietapa, streaming especulativo de contexto y exploración de conocimiento en gráficos 3D sin depender de servicios en la nube.

Con **21 Innovaciones RAG de Nodo Único**, **134 Módulos de Dominio** y **65 Suites de Pruebas Automatizadas**, Uroboros supera a los servicios en la nube (como Microsoft Azure AI Search) al ofrecer resolución de contradicciones, precaché predictivo, borradores especulativos, monitoreo de deriva conceptual y filtrado de alucinaciones directamente en hardware local.

---

## Tabla de Contenidos

- [1. Fundamentos Matemáticos y Algoritmos](#1-fundamentos-matemáticos-y-algoritmos)
- [2. Las 21 Innovaciones RAG de Nodo Único](#2-las-21-innovaciones-rag-de-nodo-único)
- [3. Arquitectura del Pipeline de Procesamiento](#3-arquitectura-del-pipeline-de-procesamiento)
- [4. Estructura Completa del Código Fuente](#4-estructura-completa-del-código-fuente)
- [5. Arquitectura de Routers de API (`src/app/routers/`)](#5-arquitectura-de-routers-de-api-srcapprouters)
- [6. Taxonomía Completa de los 134 Módulos de Dominio (`src/domain/`)](#6-taxonomía-completa-de-los-134-módulos-de-dominio-srcdomain)
- [7. Esquema Relacional de Base de Datos SQLite DDL](#7-esquema-relacional-de-base-de-datos-sqlite-ddl)
- [8. Referencia Completa de Endpoints REST API y Ejemplos Curl](#8-referencia-completa-de-endpoints-rest-api-y-ejemplos-curl)
- [9. Enrutamiento de Modelos LLM Locales y Aislamiento de Procesos](#9-enrutamiento-de-modelos-llm-locales-y-aislamiento-de-procesos)
- [10. Evaluaciones de Rendimiento y SLA](#10-evaluaciones-de-rendimiento-y-sla)
- [11. Referencia de la Interfaz de Línea de Comandos (CLI)](#11-referencia-de-la-interfaz-de-línea-de-comandos-cli)
- [12. Arquitectura Frontend React 19 SPA](#12-arquitectura-frontend-react-19-spa)
- [13. Guía de Instalación y Despliegue](#13-guía-de-instalación-y-despliegue)
- [14. Seguridad Empresarial, Redacción PII y SOC 2](#14-seguridad-empresarial-redacción-pii-y-soc-2)
- [15. Control de Calidad y Pruebas Automatizadas](#15-control-de-calidad-y-pruebas-automatizadas)
- [16. Licencia](#16-licencia)

---

## 1. Fundamentos Matemáticos y Algoritmos

### 1.1 Clasificación Léxica Okapi BM25
La puntuación de relevancia probabilística del documento $D$ para la consulta $Q = \{q_1, q_2, \dots, q_n\}$ se calcula como:

$$Score_{BM25}(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$

### 1.2 Fusión de Rango Recíproco (RRF)
$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

### 1.3 Decaimiento Exponencial Temporal
$$Score_{Final}(d) = Score_{RRF}(d) \cdot e^{-\lambda \cdot \Delta t}$$

---

## 2. Las 21 Innovaciones RAG de Nodo Único

| # | Pilar de Innovación | Archivo | Endpoint REST | Ventaja Competitiva |
|---| :--- | :--- | :--- | :--- |
| **1** | **RAG Especulativo** | [`speculative_rag.py`](file:///C:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_rag.py) | `POST /api/search/speculative-rag` | Sintetiza 3 borradores paralelos, reduciendo latencia en **~78%**. |
| **2** | **Linaje Temporal** | [`temporal_rag_lineage.py`](file:///C:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/temporal_rag_lineage.py) | `GET/POST /api/knowledge/temporal-lineage` | Rastra el historial de versiones a lo largo del tiempo ($t_0 \to t_1 \to t_2$). |
| **3** | **Filtro de Alucinaciones** | [`hallucination_guard.py`](file:///C:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/hallucination_guard.py) | `POST /api/search/hallucination-guard` | Calcula el nivel de confianza y rechaza consultas dudosas ($< 0.65$). |
| **4** | **Resolución de Contradicciones** | [`conflict_resolver.py`](file:///C:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/conflict_resolver.py) | `POST /api/knowledge/resolve-conflicts` | Reconcilia fechas y datos opuestos entre documentos. |
| **5** | **Precaché Predictivo** | [`predictive_precacher.py`](file:///C:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/precache-context) | `POST /api/search/precache-context` | Precalcula vecindarios de wikilinks para respuestas en 0ms. |

---

## 3. Arquitectura del Pipeline de Procesamiento

```mermaid
flowchart TD
    User[Cliente / Aplicación] --> API[Backend FastAPI]
    API --> Intent[Clasificador de Intención y PII]
    Intent --> Bandit[Enrutador Bandit]
    
    subgraph Motores de Búsqueda
        Bandit --> FTS[FTS5 Léxico (BM25)]
        Bandit --> Vector[Vectores Ollama Nomic]
        Bandit --> HyDE[Expansión Contextual HyDE]
        Bandit --> Graph[GraphRAG Wikilinks]
    end

    FTS --> RRF[Fusión RRF y Decaimiento]
    Vector --> RRF
    HyDE --> RRF
    Graph --> RRF

    RRF --> Response[Respuesta + Citas de Líneas de Código]
    Response --> User
```

---

## 4. Estructura Completa del Código Fuente

```
c:\Users\Administrator\Desktop\Neuro Alexander
├── src/
│   ├── app/routers/                   # Routers REST de FastAPI
│   ├── core/                          # Servicios centralizados y enrutamiento LLM
│   ├── domain/                        # 134 Módulos de Inteligencia
│   └── infrastructure/                # Base de datos SQLite y Parsers
├── frontend/                          # Aplicación React 19 + Vite
├── tests/                             # 65 Suites de Pruebas
├── know.py                            # CLI Principal e Indexador
└── README.es.md
```

---

## 13. Guía de Instalación y Despliegue

```bash
# 1. Instalar dependencias de Python
pip install -r requirements.txt

# 2. Compilar Frontend React 19
cd frontend
npm install
npm run build
cd ..

# 3. Iniciar el servidor
python main.py
```

---

## 16. Licencia

Este proyecto está bajo la Licencia MIT - consulte el archivo [`LICENSE`](LICENSE) para obtener más detalles.
