# Benchmark

Suite de evaluación del pipeline de trazabilidad de [Speclink](https://github.com/lacatu5/speclink). Evalúa clasificadores LLM, rerankers y el pipeline completo contra un ground truth, y genera las figuras de la memoria.

## Proyecto de evaluación (`code/`)

Aplicación de gestión de tareas en Python (Flask) + React (frontend) con 20 archivos fuente y 5 archivos de documentación. Diseñada para ejercitar ambos extractores de tree-sitter con patrones realistas:

- **`api.md`**: Trazabilidad a nivel de endpoint (ruta → handler → modelo).
- **`architecture.md`**: Preocupaciones transversales (flujo de autenticación que cruza backend y frontend).
- **`cli.md`**: Mapeo entre comandos e implementación.
- **`code-snippets.md`**: Ejemplos de código → archivo fuente.
- **`getting-started.md`**: Instrucciones de configuración → archivos de configuración.

Incluye relaciones uno-a-muchos, muchos-a-uno y flujos transversales.

## Ground truth

El ground truth (`data/ground-truth.csv`) contiene 75 enlaces positivos verificados manualmente sobre 1100 pares (sección, archivo). Criterio de clasificación:

- **TRUE**: El archivo define el esquema de datos, implementa la lógica central o contiene la fuente autorizada del comportamiento descrito.
- **FALSE**: El archivo solo conecta componentes, consume una funcionalidad o referencia identificadores sin definir comportamiento.

## Selección de modelos

Todos los modelos evaluados son **no-reasoning**. La tarea de clasificación de trazabilidad es una decisión binaria por par (sección, archivo) que no requiere descomposición lógica multi-paso. Los resultados muestran que modelos pequeños y económicos alcanzan F1 competitivos frente a modelos más grandes.

## Estructura

```
benchmark/
├── code/                          # Proyecto evaluado
│   ├── backend/                   # Python (Flask): modelos, servicios, auth
│   ├── frontend/                  # React/JS: componentes, hooks, cliente API
│   └── docs/                      # 5 archivos Markdown
├── data/                          # Datasets de evaluación
│   ├── ground-truth.csv           # Ground truth manual (75 enlaces positivos)
│   ├── baseline.csv               # Baseline todos-positivos
│   ├── dspy-dataset.csv           # Pares de entrenamiento DSPy (score > 0.5)
│   └── model_costs.csv            # Precios por modelo
├── experiments/                   # Resultados de experimentos
│   ├── classifier/                # 12 modelos LLM × 3 ejecuciones
│   ├── reranker/                  # 5 rerankers (3 API, 2 locales)
│   ├── ablation/                  # Baseline, solo clasificación, solo reranker, pipeline completo
│   └── dspy/                      # Baseline vs optimizado (GPT-4o-mini, Grok)
├── evaluation/                    # Framework de evaluación
│   ├── core.py                    # Carga GT, cálculo P/R/F1, agregación
│   ├── collect.py                 # Procesamiento y recolección de resultados
│   ├── report.py                  # Informe por consola
│   ├── write_data.py              # Exportación CSV/JSON
│   └── dspy_optimizer.py          # Optimización de prompts con DSPy/MIPROv2
├── plots/                         # Visualización
│   ├── classifiers.py             # F1 por modelo, desglose de errores
│   ├── ablation.py                # Comparación de ablación
│   ├── heatmap.py                 # Heatmap por documento
│   ├── threshold.py               # Curvas de sensibilidad del umbral
│   └── cost.py                    # Dispersión coste vs F1
├── results/                       # Figuras generadas (PNG) y datos (CSV)
└── eval.py                        # Punto de entrada CLI
```

## Instalación

Requiere Python 3.12+.

```bash
git clone https://github.com/lacatu5/speclink-benchmark.git
cd speclink-benchmark
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
# Evaluación completa (procesa experimentos, genera informe + figuras)
python eval.py

# Evaluar un experimento específico
python eval.py experiments/classifier/gpt-5-nano

# Sin generar figuras
python eval.py --no-plots

# Optimización de prompts con DSPy
python -m evaluation.dspy_optimizer --model openai/gpt-4o-mini
```

## Métricas

Para cada par (sección, archivo) el clasificador produce TRUE/FALSE. Se calculan:

- **Precision**: TP / (TP + FP) — de los enlaces predichos, cuántos son correctos.
- **Recall**: TP / (TP + FN) — de los enlaces reales, cuántos se detectan.
- **F1**: Media armónica de P y R.

El baseline todos-positivos (1100 pares → TRUE) da F1 = 0.128, estableciendo el mínimo de referencia.

## Licencia

MIT
