# Reporte de calidad – salidas_exterior.csv

Generado automáticamente por `notebooks/04_reporte_calidad.py` el 2026-11-19.

## Tamaño y unicidad

- Filas: **2783** (una por jugador, en su primera salida al exterior).
- Jugadores duplicados (player_id_api): **0**.
- Jugadores de Transfermarkt asignados a más de una fila: **0**.
- Período de salidas: 2012-01-01 a 2026-09-09.

## Cobertura por fuente

| Indicador | Filas | % |
| --- | --- | --- |
| Emparejadas con Transfermarkt | 1004 | 36% |
|   · confianza alta (pase nombre + fecha + club) | 530 | 19% |
|   · confianza media (nombre, jugador sudamericano único) | 474 | 17% |
| Con edad al salir | 1004 | 36% |
| Con valor de mercado al salir | 725 | 26% |
| Con valor de mercado a 1 año | 637 | 23% |
| Con valor de mercado a 3 años | 510 | 18% |
| Con monto de pase informado (> 0) | 165 | 6% |
| Con minutos de liga medibles (liga cubierta) | 172 | 6% |
| Con 3 años completos de seguimiento | 1956 | 70% |
| Muestra para la pregunta central (valor al salir + a 3 años + seguimiento completo) | 414 | 15% |

## Faltantes por columna

| Columna | % faltante |
| --- | --- |
| consolidado | 94% |
| minutos_liga_a3 | 94% |
| minutos_liga_a2 | 94% |
| minutos_liga_a1 | 94% |
| partidos_seleccion | 86% |
| var_valor_3a_pct | 84% |
| monto_pase_eur | 82% |
| valor_3a_eur | 82% |
| dias_dif_emparejamiento | 81% |
| var_valor_1a_pct | 79% |
| valor_1a_eur | 77% |
| valor_salida_eur | 74% |
| valor_max_3a_eur | 73% |
| pie | 65% |
| nombre_tm | 64% |
| player_id_tm | 64% |
| pais_nacimiento | 64% |
| fecha_nacimiento | 64% |
| posicion | 64% |
| sub_posicion | 64% |
| franja_edad | 64% |
| edad_salida | 64% |
| metodo_emparejamiento | 64% |
| altura_cm | 64% |
| confianza_emparejamiento | 64% |
| tipo_pase | 18% |

## Cobertura por región de destino

| Región | Filas | % emparejadas con TM | % con valor a 3 años |
| --- | --- | --- | --- |
| Sudamérica | 2115 | 30% | 13% |
| México y EE. UU./Canadá | 295 | 53% | 28% |
| 5 grandes ligas | 142 | 70% | 54% |
| Resto de Europa y otros | 128 | 70% | 39% |
| Centroamérica y Caribe | 57 | 9% | 2% |
| Europa intermedia | 26 | 58% | 46% |
| Asia y Medio Oriente | 20 | 40% | 20% |

## Rangos y valores atípicos

- Edad al salir: mínimo 16.1, mediana 24.5, máximo 39.7 (filtro de validez: 16 a 40 años).
- Valor al salir: mediana € 900,000; máximo € 35,000,000.
- Variación de valor a 3 años: mediana 0%; percentil 5 -81%; percentil 95 1080%. Valores extremos esperables en valores bajos de partida: usar mediana o log del ratio, no promedio.

## Sesgos y limitaciones conocidas

- **Sesgo de cobertura:** el emparejamiento con Transfermarkt es mucho mayor para destinos europeos y México/EE. UU. que para Sudamérica. Las conclusiones sobre revalorización valen para jugadores que Transfermarkt sigue, no para todos los exportados.
- **Sesgo de supervivencia:** Transfermarkt tiene más información de jugadores que siguieron activos en ligas cubiertas.
- **Valor de mercado = estimación** de la comunidad de Transfermarkt, no precio de pase.
- **Minutos:** solo medibles en ligas cubiertas por Transfermarkt y en los años de cobertura (varias ligas americanas solo desde 2024).
- **Destinos sin clasificar (~9% de las salidas):** si la verdadera primera salida fue a uno de esos clubes, el jugador figura con una salida posterior.
- **Emparejamiento por nombre (confianza media):** puede tener errores; validar a mano una muestra de 30 filas antes de publicar.
