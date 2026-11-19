# Observatorio: el fútbol argentino como exportador de talento

Taller de Ciencia de Datos – UNSTA 2026 · Wenceslao José Villegas, Julio Esteban Robinson, Rodrigo Toledo.

¿Qué pasa con los futbolistas formados en clubes argentinos después de que los venden al exterior? ¿Qué edad y qué destino se asocian a que se revaloricen?

## Entregables (`desafios/`)
- **Desafío 1:** infografía de la propuesta de línea de investigación.
- **Desafío 2:** presentación del proyecto de datos + documento de validación a distancia (encuesta y mensajes).
- **Desafío 3:** presentación del Plan Maestro de Ejecución.

## Estructura
```
taller-datos-futbol/
├── data/
│   ├── raw/                      # datos tal cual se descargaron (NO editar)
│   │   ├── transfermarkt/archive/
│   │   └── api_football/
│   ├── processed/                # tablas intermedias + clasificación manual
│   └── analytical/               # tablas listas para analizar  ← empezar acá
├── notebooks/                    # pasos del proceso, en orden
├── docs/                         # diccionario, reporte de calidad y registro de decisiones
├── desafios/                     # entregables del taller (PDF / PNG)
├── FUENTES.md                    # ficha de cada fuente
└── README.md
```

Los datos crudos (`data/raw/`) y las tablas intermedias pesadas **no se suben al repositorio** (tamaño y condiciones de uso de las fuentes): se descargan siguiendo `FUENTES.md` y los pasos de abajo.

## Cómo reproducir todo (orden de ejecución)
1. **Transfermarkt:** descargar el ZIP de Kaggle y descomprimirlo en `data/raw/transfermarkt/archive/`.
2. **API-Football:** ejecutar `notebooks/descargar_api_football.ipynb` en Google Colab (necesita una clave gratuita). Bajar de Drive `data/raw/api_football/` y `data/processed/apifootball_transfers.csv`.
3. `python notebooks/02_clasificar_destinos.py` → clasifica destinos (Argentina / exterior) y arma las primeras salidas.
4. `python notebooks/03_integrar_fuentes.py` → une con Transfermarkt y genera `data/analytical/`.
5. `python notebooks/04_reporte_calidad.py` → regenera `docs/reporte_calidad.md`.

Si se corrige `data/processed/clasificacion_manual_destinos.csv`, volver a correr los pasos 3 a 5.

## Tablas para analizar (`data/analytical/`)
| Archivo | Una fila es… | Para qué pregunta |
|---|---|---|
| `salidas_exterior.csv` | un jugador en su primera salida al exterior | P1 a P5 |
| `valuaciones_post_salida.csv` | una valuación de mercado de un jugador | Trayectorias de valor (P2, P3) |
| `resumen_clubes_origen.csv` | un club argentino de origen | P4 |

Ver `docs/diccionario_datos.md` (qué es cada columna), `docs/reporte_calidad.md` (faltantes, sesgos y tamaños de muestra) y `docs/decisiones.md` (decisiones metodológicas y de alcance).

## Ejemplo de carga
```python
import pandas as pd
df = pd.read_csv("data/analytical/salidas_exterior.csv", parse_dates=["fecha_salida", "fecha_nacimiento"])
muestra = df[df.valor_salida_eur.notna() & df.valor_3a_eur.notna() & df.seguimiento_3a_completo]  # pregunta central
```
