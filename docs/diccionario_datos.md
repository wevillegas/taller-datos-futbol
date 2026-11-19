# Diccionario de datos

## `data/analytical/salidas_exterior.csv`

**Unidad de análisis:** una fila = un jugador en su **primera salida al exterior** desde un club de Primera, Primera Nacional o Primera B Metro (2012–2026).
**Origen de cada columna:** API = API-Football · TM = Transfermarkt Datasets · CALC = calculada en `03_integrar_fuentes.py` · MANUAL = revisión humana.

| Columna | Tipo | Origen | Descripción |
|---|---|---|---|
| player_id_api | entero | API | Identificador del jugador en API-Football. Clave única de la tabla. |
| player_id_tm | entero | TM | Identificador del jugador en Transfermarkt (vacío si no se pudo emparejar). |
| nombre_api / nombre_tm | texto | API / TM | Nombre del jugador en cada fuente (sirve para validar el emparejamiento). |
| fecha_nacimiento | fecha | TM | Fecha de nacimiento. |
| pais_nacimiento | categórica | TM | País de nacimiento. |
| posicion / sub_posicion | categórica | TM | Posición general (Goalkeeper, Defender, Midfield, Attack) y específica. |
| pie | categórica | TM | Pie hábil. |
| altura_cm | numérica | TM | Altura en centímetros. |
| partidos_seleccion | numérica | TM | Partidos con la selección mayor (a la fecha de descarga). |
| fecha_salida | fecha | API | Fecha de la primera transferencia a un club del exterior. |
| anio_salida | entero | CALC | Año de la salida. |
| edad_salida | numérica | CALC | Edad en años al momento de la salida (fecha_salida − fecha_nacimiento). |
| franja_edad | categórica | CALC | menos de 20 · 20-22 · 23-25 · 26 o más. |
| tipo_pase | texto | API | Tipo informado por la API: Loan (préstamo), Free (libre), monto, etc. |
| es_prestamo | booleana | CALC | Verdadero si tipo_pase indica préstamo. |
| monto_pase_eur | numérica | TM | Monto del pase en euros según Transfermarkt (0 o vacío = no informado o libre). |
| club_origen_id / club_origen | entero / texto | API | Club argentino desde el que sale. |
| categoria_origen | categórica | CALC | Primera · Primera Nacional · Primera B Metro (categoría del club en la temporada 2024). |
| club_destino_id / club_destino | entero / texto | API | Club del exterior al que llega. |
| pais_destino | categórica | MANUAL | País del club de destino (clasificación manual en `clasificacion_manual_destinos.csv`). |
| region_destino | categórica | CALC | 5 grandes ligas · Europa intermedia (Portugal, Países Bajos, Bélgica) · Resto de Europa y otros · Sudamérica · México y EE. UU./Canadá · Centroamérica y Caribe · Asia y Medio Oriente. |
| valor_salida_eur | numérica | TM | Último valor de mercado entre 365 días antes y 30 días después de la salida. |
| valor_1a_eur | numérica | TM | Valor de mercado más cercano a 1 año después (ventana ±120 días). |
| valor_3a_eur | numérica | TM | Valor de mercado más cercano a 3 años después (ventana ±180 días). |
| valor_max_3a_eur | numérica | TM | Valor máximo alcanzado en los 3 años posteriores. |
| var_valor_1a_pct / var_valor_3a_pct | numérica | CALC | Variación % del valor respecto del valor al salir. **Variable objetivo de la pregunta central.** |
| minutos_cubiertos | booleana | CALC | Verdadero si la liga de destino estaba cubierta por Transfermarkt en el primer año (minutos medibles). |
| minutos_liga_a1, _a2, _a3 | numérica | TM | Minutos de liga en el 1.º, 2.º y 3.º año posterior a la salida (vacío si no medible). |
| consolidado | booleana | CALC | ≥ 1.500 minutos de liga en alguno de los 3 años (solo si minutos_cubiertos). |
| regreso_argentina_3a | booleana | API | Volvió a un club argentino dentro de los 3 años. |
| cambios_club_3a | entero | API | Cantidad de transferencias en los 3 años posteriores. |
| seguimiento_3a_completo | booleana | CALC | La salida es anterior a julio de 2023 (hay 3 años de datos posteriores). |
| emparejado_tm | booleana | CALC | Se encontró al jugador en Transfermarkt. |
| metodo_emparejamiento / confianza_emparejamiento | categórica | CALC | "pase (nombre + fecha)" = alta · "nombre (tabla de jugadores)" = media. |
| dias_dif_emparejamiento | entero | CALC | Diferencia en días entre la fecha del pase en cada fuente (solo método por pase). |
| metodo_clasificacion_destino | categórica | CALC | "manual" o "lista_api" (cómo se determinó el país de destino). |

## `data/analytical/valuaciones_post_salida.csv`
Serie larga de valores de mercado de los jugadores emparejados: `player_id_api`, `player_id_tm`, `fecha_valuacion`, `dias_desde_salida` (negativo = antes de salir), `valor_eur`. Sirve para graficar trayectorias de valor.

## `data/analytical/resumen_clubes_origen.csv`
Una fila por club de origen: jugadores exportados, edad mediana al salir, valor total al salir, monto total de pases, % que fue a Europa y % que volvió en 3 años (pregunta P4).

## Tablas intermedias (`data/processed/`)
- `apifootball_transfers.csv`: todas las transferencias de los clubes descargados (API-Football, sin filtrar).
- `salidas_clasificadas.csv`: salidas 2012–2026 desde las 3 categorías, con país de destino y si es exterior.
- `primeras_salidas_exterior.csv`: primera salida al exterior por jugador (antes de sumar Transfermarkt).
- `clasificacion_manual_destinos.csv`: país de los 320 clubes de destino más frecuentes (revisión humana; 9 marcados REVISAR).
