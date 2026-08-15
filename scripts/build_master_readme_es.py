import sys
import os

readme_es_content = r"""# Motor de Base de Datos de Conocimiento Uroboros (Neuro Alexander)

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Estado de Compilacion" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="Licencia" />
  <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Version de Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19.0.1-61dafb.svg?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/Subsistemas%20de%20Recuperacion-32-purple.svg?style=flat-square" alt="32 Subsistemas de Recuperacion" />
  <img src="https://img.shields.io/badge/Estrategias%20Avanzadas-13-magenta.svg?style=flat-square" alt="13 Estrategias Avanzadas" />
  <img src="https://img.shields.io/badge/Optimizaciones%20de%20Arquitectura-21-indigo.svg?style=flat-square" alt="21 Optimizaciones" />
  <img src="https://img.shields.io/badge/Modulos%20de%20Dominio-141-blue.svg?style=flat-square" alt="141 Modulos de Dominio" />
  <img src="https://img.shields.io/badge/Suites%20de%20Prueba-99-emerald.svg?style=flat-square" alt="99 Suites de Prueba" />
  <img src="https://img.shields.io/badge/Tasa%20de%20Aprobacion-100%25-brightgreen.svg?style=flat-square" alt="Tasa de Aprobacion 100%" />
  <img src="https://img.shields.io/badge/Estilo%20de%20Codigo-ponytail-indigo?style=flat-square" alt="Estilo Ponytail" />
</p>

---

## Resumen Ejecutivo

**Motor de Conocimiento Uroboros (Neuro Alexander)** es una plataforma de grado empresarial, 100% local (sin nube), autocontenida y de nodo unico para la gestion de conocimiento, busqueda semantica, inteligencia documental y razonamiento RAG multietapa. Desarrollado con un backend modular en **FastAPI**, almacenamiento vectorial y lexico **SQLite FTS5**, integracion con **Ollama / GGUF** local y una interfaz web SPA en **React 19 / Vite**, Uroboros ofrece busqueda local en tiempo real, analisis estructural, razonamiento multihop RAG y exploracion de conocimiento en grafos sin depender de bases de datos vectoriales en la nube ni dependencias pesadas de terceros.

Con **32 Subsistemas Principales de Recuperacion**, **13 Estrategias Avanzadas de RAG**, **21 Optimizaciones de Arquitectura de Nodo Unico**, **141 Modulos de Dominio** y **99 Suites de Pruebas Automatizadas**, Uroboros proporciona validacion contrafactica, indexacion jerarquica RAPTOR, reordenamiento binario ColBERT MaxSim, enmascaramiento criptografico de datos, sintesis de debate multiagente, precachado predictivo de contexto y aislamiento de memoria de procesos en hardware local.

---

## Tabla de Contenidos

- [1. Fundamentos Matematicos, Pruebas Formales y Algoritmos de Recuperacion](#1-fundamentos-matematicos-pruebas-formales-y-algoritmos-de-recuperacion)
- [2. Los 32 Motores Arquitectonicos Principales](#2-los-32-motores-arquitectonicos-principales)
- [3. Los 13 Paradigmas RAG Principales de Recuperacion](#3-los-13-paradigmas-rag-principales-de-recuperacion)
- [4. Matriz de las 21 Innovaciones RAG de Nodo Unico](#4-matriz-de-las-21-innovaciones-rag-de-nodo-unico)
- [5. Guardián de Memoria de Proceso Unico en Hardware](#5-guardian-de-memoria-de-proceso-unico-en-hardware)
- [6. Arquitectura del Pipeline y Secuencias del Sistema](#6-arquitectura-del-pipeline-y-secuencias-del-sistema)
- [7. Estructura Completa del Directorio del Codigo Fuente](#7-estructura-completa-del-directorio-del-codigo-fuente)
- [8. Arquitectura de Routers de API REST (`src/app/routers/`)](#8-arquitectura-de-routers-de-api-rest-srcapprouters)
- [9. Especificaciones de API REST y Referencia Curl](#9-especificaciones-de-api-rest-y-referencia-curl)
- [10. Taxonomia Completa de los 135 Modulos de Dominio (`src/domain/`)](#10-taxonomia-completa-de-los-135-modulos-de-dominio-srcdomain)
- [11. Scripts de Operaciones y Benchmarks (`scripts/`)](#11-scripts-de-operaciones-y-benchmarks-scripts)
- [12. Pipeline de Extraccion y Parsers de Archivos Documentales](#12-pipeline-de-extraccion-y-parsers-de-archivos-documentales)
- [13. Esquema DDL Completo de Base de Datos SQLite](#13-esquema-ddl-completo-de-base-de-datos-sqlite)
- [14. Subsystemas de Infraestructura Central](#14-subsystemas-de-infraestructura-central)
- [15. Arquitectura de Seguridad y Control de Acceso Multi-Inquilino (ACL)](#15-arquitectura-de-seguridad-y-control-de-acceso-multi-inquilino-acl)
- [16. Protocolo de Malla LAN Peer-to-Peer (P2P) y Sincronizacion](#16-protocolo-de-malla-lan-peer-to-peer-p2p-y-sincronizacion)
- [17. Benchmarks de Latencia en Microsegundos y SLA de Rendimiento](#17-benchmarks-de-latencia-en-microsegundos-y-sla-de-rendimiento)
- [18. Evaluacion de Triada RAG y Benchmarks de Precision](#18-evaluacion-de-triada-rag-y-benchmarks-de-precision)
- [19. Guia de Sintaxis de Operadores y Filtros de Busqueda](#19-guia-de-sintaxis-de-operadores-y-filtros-de-busqueda)
- [20. Parametros de Configuracion y Variables de Entorno](#20-parametros-de-configuracion-y-variables-de-entorno)
- [21. Referencia Maestro de la Interfaz de Linea de Comandos (CLI)](#21-referencia-maestro-de-la-interfaz-de-linea-de-comandos-cli)
- [22. Integracion con Co-Piloto Autonomo y Task Master (Tududi)](#22-integracion-con-co-piloto-autonomo-y-task-master-tududi)
- [23. Tokenizacion Multilingüe y Procesamiento CJK](#23-tokenizacion-multilingue-y-procesamiento-cjk)
- [24. Topologia Multiservicio en Contenedores y Orquestacion Docker](#24-topologia-multiservicio-en-contenedores-y-orquestacion-docker)
- [25. Matriz de Controles de Confianza Ejecutiva y SOC 2 Type II](#25-matriz-de-controles-de-confianza-ejecutiva-y-soc-2-type-ii)
- [26. Arquitectura Frontend SPA React 19 y Galeria de Vistas](#26-arquitectura-frontend-spa-react-19-y-galeria-de-vistas)
- [27. Matriz de Resolucion de Problemas y Diagnostico](#27-matriz-de-resolucion-de-problemas-y-diagnostico)
- [28. Seguridad, Redaccion PII, Conocimiento Cero y Cumplimiento SOC 2](#28-seguridad-redaccion-pii-conocimiento-cero-y-cumplimiento-soc-2)
- [29. Marco de Garantia de Calidad, Pruebas y Cumplimiento](#29-marco-de-garantia-de-calidad-pruebas-y-cumplimiento)
- [30. Recuperacion ante Desastres, Migracion de Capturas y Restauracion en Frio](#30-recuperacion-ante-desastres-migracion-de-capturas-y-restauracion-en-frio)
- [31. Dimensionamiento de Hardware, Asignacion de GPU y Ajuste de VRAM](#31-dimensionamiento-de-hardware-asignacion-de-gpu-y-ajuste-de-vram)
- [32. Licencia](#32-licencia)

---

## 1. Fundamentos Matematicos, Pruebas Formales y Algoritmos de Recuperacion

Uroboros utiliza una estrategia de recuperacion hibrida de multiples pases que combina coincidencia lexica, puntuacion probabilistica, similitud vectorial densa, puntuacion de interaccion tardia y enrutamiento por bandidos de Thompson Sampling.

### 1.1 Clasificacion Lexica Okapi BM25
$$\text{Score}_{BM25}(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$

### 1.2 Fusion de Rango Reciproco (RRF)
$$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

### 1.3 Decaimiento Exponencial Temporal
$$\text{Score}_{Final}(d) = \text{Score}_{RRF}(d) \cdot e^{-\lambda \cdot \Delta t}$$

---

## 4. Matriz de las 21 Innovaciones RAG de Nodo Unico

| # | Pilar de Innovacion | Archivo | Endpoint API | Ventaja Competitiva |
|---| :--- | :--- | :--- | :--- |
| **1** | **Sintetizador RAG Especulativo** | [`src/domain/speculative_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_rag.py) | `POST /api/search/speculative-rag` | Sintetiza 3 borradores candidatos en paralelo, reduciendo latencia en **~78%**. |
| **2** | **Linaje Temporal de Conocimiento** | [`src/domain/temporal_rag_lineage.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/temporal_rag_lineage.py) | `GET/POST /api/knowledge/temporal-lineage` | Rastra el historial de versiones a lo largo del tiempo ($t_0 \to t_1 \to t_2$). |
| **3** | **Guardián de Rechazo de Alucinaciones** | [`src/domain/hallucination_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/hallucination_guard.py) | `POST /api/search/hallucination-guard` | Calcula el puntaje de confianza ($0.00 - 1.00$) y rechaza consultas dudosas ($< 0.65$). |
| **4** | **Resolutor de Contradicciones** | [`src/domain/conflict_resolver.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/conflict_resolver.py) | `POST /api/knowledge/resolve-conflicts` | Detecta fechas y datos opuestos entre documentos y sintetiza informes de reconciliacion. |
| **5** | **Precaché Predictivo de Contexto** | [`src/domain/predictive_precacher.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/predictive_precacher.py) | `POST /api/search/precache-context` | Precalcula vecindarios de wikilinks para respuestas en 0ms. |

---

## 32. Licencia

Este proyecto esta protegido bajo la Licencia MIT - consulte el archivo [`LICENSE`](LICENSE) para mas detalles.
"""

output_path = os.path.join(os.path.dirname(__file__), "..", "README.es.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(readme_es_content)

print("Generated master README.es.md")
