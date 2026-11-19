"""Genera docs/reporte_calidad.md a partir del dataset analítico (Desafío 2, punto 4: calidad)."""
import os
import pandas as pd

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
o = pd.read_csv(os.path.join(R, "data", "analytical", "salidas_exterior.csv"), parse_dates=["fecha_salida"])
L = []
w = L.append
w("# Reporte de calidad – salidas_exterior.csv\n")
w(f"Generado automáticamente por `notebooks/04_reporte_calidad.py` el {pd.Timestamp.now():%Y-%m-%d}.\n")
w("## Tamaño y unicidad\n")
w(f"- Filas: **{len(o)}** (una por jugador, en su primera salida al exterior).")
w(f"- Jugadores duplicados (player_id_api): **{o.player_id_api.duplicated().sum()}**.")
w(f"- Jugadores de Transfermarkt asignados a más de una fila: **{o.player_id_tm.dropna().duplicated().sum()}**.")
w(f"- Período de salidas: {o.fecha_salida.min():%Y-%m-%d} a {o.fecha_salida.max():%Y-%m-%d}.\n")
w("## Cobertura por fuente\n")
w("| Indicador | Filas | % |\n| --- | --- | --- |")
def fila(nombre, mask):
    w(f"| {nombre} | {int(mask.sum())} | {100 * mask.mean():.0f}% |")
fila("Emparejadas con Transfermarkt", o.emparejado_tm)
fila("  · confianza alta (pase nombre + fecha + club)", o.confianza_emparejamiento.eq("alta"))
fila("  · confianza media (nombre, jugador sudamericano único)", o.confianza_emparejamiento.eq("media"))
fila("Con edad al salir", o.edad_salida.notna())
fila("Con valor de mercado al salir", o.valor_salida_eur.notna())
fila("Con valor de mercado a 1 año", o.valor_1a_eur.notna())
fila("Con valor de mercado a 3 años", o.valor_3a_eur.notna())
fila("Con monto de pase informado (> 0)", o.monto_pase_eur.fillna(0).gt(0))
fila("Con minutos de liga medibles (liga cubierta)", o.minutos_cubiertos)
fila("Con 3 años completos de seguimiento", o.seguimiento_3a_completo)
fila("Muestra para la pregunta central (valor al salir + a 3 años + seguimiento completo)",
     o.valor_salida_eur.notna() & o.valor_3a_eur.notna() & o.seguimiento_3a_completo)
w("")
w("## Faltantes por columna\n")
w("| Columna | % faltante |\n| --- | --- |")
for c, p in (o.isna().mean() * 100).round(0).sort_values(ascending=False).items():
    if p > 0:
        w(f"| {c} | {p:.0f}% |")
w("")
w("## Cobertura por región de destino\n")
g = o.groupby("region_destino").agg(filas=("player_id_api", "count"), emparejadas=("emparejado_tm", "mean"),
                                    con_valor_3a=("valor_3a_eur", lambda s: s.notna().mean()))
w("| Región | Filas | % emparejadas con TM | % con valor a 3 años |\n| --- | --- | --- | --- |")
for r, x in g.sort_values("filas", ascending=False).iterrows():
    w(f"| {r} | {int(x.filas)} | {100 * x.emparejadas:.0f}% | {100 * x.con_valor_3a:.0f}% |")
w("")
w("## Rangos y valores atípicos\n")
e = o.edad_salida.dropna()
w(f"- Edad al salir: mínimo {e.min()}, mediana {e.median()}, máximo {e.max()} (filtro de validez: 16 a 40 años).")
v = o.valor_salida_eur.dropna()
w(f"- Valor al salir: mediana € {v.median():,.0f}; máximo € {v.max():,.0f}.")
vv = o.var_valor_3a_pct.dropna()
w(f"- Variación de valor a 3 años: mediana {vv.median():.0f}%; percentil 5 {vv.quantile(.05):.0f}%; percentil 95 {vv.quantile(.95):.0f}%. "
  "Valores extremos esperables en valores bajos de partida: usar mediana o log del ratio, no promedio.")
w("")
w("## Sesgos y limitaciones conocidas\n")
w("- **Sesgo de cobertura:** el emparejamiento con Transfermarkt es mucho mayor para destinos europeos y México/EE. UU. "
  "que para Sudamérica. Las conclusiones sobre revalorización valen para jugadores que Transfermarkt sigue, no para todos los exportados.")
w("- **Sesgo de supervivencia:** Transfermarkt tiene más información de jugadores que siguieron activos en ligas cubiertas.")
w("- **Valor de mercado = estimación** de la comunidad de Transfermarkt, no precio de pase.")
w("- **Minutos:** solo medibles en ligas cubiertas por Transfermarkt y en los años de cobertura (varias ligas americanas solo desde 2024).")
w("- **Destinos sin clasificar (~9% de las salidas):** si la verdadera primera salida fue a uno de esos clubes, el jugador figura con una salida posterior.")
w("- **Emparejamiento por nombre (confianza media):** puede tener errores; validar a mano una muestra de 30 filas antes de publicar.")
open(os.path.join(R, "docs", "reporte_calidad.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
