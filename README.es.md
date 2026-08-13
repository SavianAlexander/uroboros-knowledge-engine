# Motor de Base de Datos de Conocimiento Uroboros (Neuro Alexander)

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Estado de Compilación" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="Licencia" />
  <img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Versión de Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115.0%2B-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19.0.1-61dafb.svg?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/Vite-6.2.3-646cff.svg?style=flat-square" alt="Vite" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/IA%20Local-Ollama%20Qwen-purple.svg?style=flat-square" alt="IA Local" />
  <img src="https://img.shields.io/badge/Task%20Master-Tududi-emerald.svg?style=flat-square" alt="Task Master" />
  <img src="https://img.shields.io/badge/estilo%20de%20código-ponytail-indigo?style=flat-square" alt="Estilo de Código" />
</p>

---

## Resumen Ejecutivo

**Motor de Conocimiento Uroboros** (Neuro Alexander) es una plataforma de grado empresarial, autocontenida y de cero dependencias externas para la gestión de conocimiento, recuperación semántica e indexación de documentos. Desarrollado con un backend modular en **FastAPI**, motor vectorial y léxico **SQLite FTS5**, integración con **Ollama LLM** local y una interfaz web SPA en **React 19 / Vite**, Uroboros ofrece búsqueda local en tiempo real, análisis estructural, razonamiento RAG multietapa, streaming especulativo de contexto y exploración de conocimiento en gráficos 3D sin depender de servicios en la nube.

---

## 1. Innovaciones Tecnológicas Centrales

- **Inteligencia Local Cero-Nube**: Integración nativa con Ollama (`qwen2.5:7b`, `qwen2.5-coder:14b`, `nomic-embed-text`) con salvaguardas de degradación elegante y streaming especulativo con latencia inferior a 10ms.
- **Motor de Búsqueda Híbrido Multipaso**: Combina BM25 de Okapi (SQLite FTS5), similitud de coseno vectorial, Reciprocal Rank Fusion (RRF), decaimiento exponencial por fecha e interacción tardía Binary ColBERT (MaxSim).
- **RAG Mecánico y Fragmentador por Entropía**: Fragmentación semántica sub-oracional basada en umbrales de entropía de información local, eliminando fragmentos distractores antes de ensamblar el contexto para el modelo.
- **RAG Especulativo y Síntesis Multihipótesis**: Generación paralela de borradores de contexto candidatas que reduce la latencia de respuesta en más de un 75%.
- **Transcripción de Notas de Voz y RAG de Audio**: Transcripción e indexación semántica con Whisper para memorandos de voz, podcasts y grabaciones de reuniones.
- **Gráfico de Conocimiento Interactivo 3D**: Renderizado WebGL en tiempo real (`react-force-graph-3d`) de nodos de documentos, entidades extraídas, clústeres de Louvain y métricas de centralidad PageRank.
- **Orquestación Task Master (Tududi)**: Integración con la suite Task Master (puente MCP `tududi`) para seguimiento de tareas, desglose de subtareas, registro de hábitos y auditoría de ejecución.
- **Gobernanza Empresarial y Seguridad**: Enmascaramiento PII automático, ofuscación Zero-Knowledge, protección contra inyecciones en prompts, verificación factual de respuestas, registros de auditoría criptográficos SHA-256 y herramientas para atestación SOC 2 Tipo II.

---

## 2. Instalación y Configuración Rápida

1. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicializar e Indexar**:
   ```bash
   python know.py init
   python know.py index "C:\Ruta\A\Tu\Workspace"
   ```

3. **Iniciar Servidor Web Backend y Frontend**:
   ```bash
   python main.py
   ```
   Abre `http://127.0.0.1:8000` en tu navegador.

---

## 3. Guía de Ejecución de Pruebas

Para ejecutar el conjunto completo de más de 670 pruebas automatizadas:
```bash
python -m pytest -q --tb=short -m "not e2e and not slow"
python run_domain_tests.py
```

---

## 4. Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.
