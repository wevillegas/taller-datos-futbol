"""Integra API-Football (salidas clasificadas) con Transfermarkt (edad, valor, minutos).
Salida principal: data/analytical/salidas_exterior.csv  (1 fila = primera salida al exterior de un jugador)
Salidas extra:    data/analytical/valuaciones_post_salida.csv (serie de valor de mercado alrededor de la salida)
                  data/analytical/resumen_clubes_origen.csv
"""
import os, glob, json, re, unicodedata
import numpy as np
import pandas as pd

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
TM = os.path.join(D, "raw", "transfermarkt", "archive")
CORTE_TM = pd.Timestamp("2026-07-06")            # última fecha con datos en Transfermarkt
CORTE_SEGUIMIENTO = CORTE_TM - pd.Timedelta(days=3 * 365)   # salidas con 3 años completos de seguimiento

def norm(s):
    """minúsculas, sin acentos ni signos"""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]+", " ", s).split()

# ---------------------------------------------------------------- 1. API-Football: salidas clasificadas
sal = pd.read_csv(os.path.join(D, "processed", "salidas_clasificadas.csv"), parse_dates=["fecha"])
teams = glob.glob(os.path.join(D, "raw", "api_football", "**", "teams_*.json"), recursive=True)
cat_origen, arg_ids = {}, set()
etiqueta = {"1032": "Primera", "128": "Primera", "129": "Primera Nacional", "131": "Primera B Metro"}
for f in teams:
    liga = os.path.basename(f).split("_")[1]
    for e in json.load(open(f))["response"]:
        arg_ids.add(e["team"]["id"])
        if liga in etiqueta:
            cat_origen.setdefault(e["team"]["id"], etiqueta[liga])

ext = sal[sal.es_exterior].sort_values("fecha")
base = ext.drop_duplicates("player_id", keep="first").copy()          # primera salida al exterior
base = base.rename(columns={"player_id": "player_id_api", "player_name": "nombre_api", "fecha": "fecha_salida",
                            "tipo": "tipo_pase", "club_salida": "club_origen", "club_salida_id": "club_origen_id",
                            "club_llegada": "club_destino", "club_llegada_id": "club_destino_id"})
base["categoria_origen"] = base.club_origen_id.map(cat_origen)

# regreso a Argentina y cantidad de clubes en los 3 años posteriores (con todas las transferencias API)
todas = pd.read_csv(os.path.join(D, "processed", "apifootball_transfers.csv"), parse_dates=["fecha"])
todas = todas[~todas.club_llegada.isin(["Without Club", "Retired", "Unknown"])]
def post3(row):
    t = todas[(todas.player_id == row.player_id_api) & (todas.fecha > row.fecha_salida) &
              (todas.fecha <= row.fecha_salida + pd.Timedelta(days=1095))]
    return pd.Series({"regreso_argentina_3a": bool(t.club_llegada_id.isin(arg_ids).any()),
                      "cambios_club_3a": len(t)})
base[["regreso_argentina_3a", "cambios_club_3a"]] = base.apply(post3, axis=1)

# ---------------------------------------------------------------- 2. Transfermarkt
tr = pd.read_csv(os.path.join(TM, "transfers.csv"), parse_dates=["transfer_date"])
pl = pd.read_csv(os.path.join(TM, "players.csv"), parse_dates=["date_of_birth"])
tr["apellido"] = tr.player_name.map(lambda s: " ".join(norm(s)[1:]) if len(norm(s)) > 1 else " ".join(norm(s)))
tr["ultimo"] = tr.player_name.map(lambda s: (norm(s) or [""])[-1])
tr["inicial"] = tr.player_name.map(lambda s: (norm(s) or [" "])[0][0])

def api_partes(nombre):
    p = norm(nombre)
    if len(p) >= 2 and len(p[0]) == 1:                  # formato "L. Acuña"
        return p[0], " ".join(p[1:]), p[-1]
    return (p[0][0] if p else ""), " ".join(p[1:]) if len(p) > 1 else " ".join(p), (p[-1] if p else "")
base[["inicial", "apellido", "ultimo"]] = base.nombre_api.apply(lambda s: pd.Series(api_partes(s)))
base["primer_nombre"] = base.nombre_api.map(lambda s: (norm(s) or [""])[0])      # "l" si viene "L. Acuña"
tr["primer_nombre"] = tr.player_name.map(lambda s: (norm(s) or [""])[0])

PALABRAS_GENERICAS = {"club", "ca", "cd", "fc", "sc", "atletico", "atl", "deportivo", "de", "del", "la", "el",
                      "u", "ii", "reserve", "sporting", "union", "real", "san", "santa", "futbol", "cf", "ac"}
def tokens_club(s):
    return {t for t in norm(s) if t not in PALABRAS_GENERICAS and len(t) > 2}

def apellido_compatible(a, b):
    """Los tokens de un apellido están contenidos en los del otro (ej.: 'acuna' vs 'acuna maciel')."""
    ta, tb = set(a.split()), set(b.split())
    return bool(ta) and bool(tb) and (ta <= tb or tb <= ta)

def nombre_compatible(primer_api, primer_tm):
    """Si la API trae solo inicial, alcanza con la inicial; si trae el nombre, tiene que coincidir."""
    return primer_api[:1] == primer_tm[:1] if len(primer_api) == 1 else primer_api == primer_tm

# 2a. Emparejamiento: mismo último apellido + misma inicial + pase en ±60 días
cand = base[["player_id_api", "fecha_salida", "inicial", "apellido", "ultimo", "primer_nombre", "club_origen", "club_destino"]].merge(
    tr[["player_id", "transfer_date", "ultimo", "inicial", "apellido", "primer_nombre", "transfer_fee",
        "market_value_in_eur", "from_club_name", "to_club_name"]],
    on=["ultimo", "inicial"], suffixes=("", "_tm"))
cand["dif_dias"] = (cand.transfer_date - cand.fecha_salida).dt.days.abs()
cand = cand[cand.dif_dias <= 60]
cand = cand[[apellido_compatible(a, b) for a, b in zip(cand.apellido, cand.apellido_tm)]]
cand = cand[[nombre_compatible(a, b) for a, b in zip(cand.primer_nombre, cand.primer_nombre_tm)]]
# el club de origen o el de destino tiene que coincidir en al menos una palabra significativa
cand = cand[[bool(tokens_club(o) & tokens_club(fo)) or bool(tokens_club(d) & tokens_club(td))
             for o, fo, d, td in zip(cand.club_origen, cand.from_club_name, cand.club_destino, cand.to_club_name)]]
cand = cand.merge(pl[["player_id", "date_of_birth"]], on="player_id", how="left")
cand = cand[((cand.fecha_salida - cand.date_of_birth).dt.days / 365.25).between(16, 40)]
cand = cand.sort_values(["player_id_api", "dif_dias"])
# descartar ambigüedades: un jugador API que empareja con 2+ jugadores TM distintos
amb = cand.groupby("player_id_api").player_id.nunique()
cand = cand[cand.player_id_api.isin(amb[amb == 1].index)].drop_duplicates("player_id_api")
cand = cand.drop_duplicates("player_id", keep="first")                # un jugador TM no puede ser dos API
match = cand.set_index("player_id_api")[["player_id", "transfer_fee", "market_value_in_eur", "dif_dias"]]
match.columns = ["player_id_tm", "monto_pase_eur", "valor_tm_en_pase_eur", "dias_dif_emparejamiento"]
match["metodo_emparejamiento"] = "pase (nombre + fecha)"
base = base.join(match, on="player_id_api")

# 2a-bis. Segundo intento para los que no emparejaron: por nombre contra la tabla de jugadores.
# (Transfermarkt guarda el historial de pases solo de jugadores activos recientes.)
# Reglas: misma inicial + mismo último apellido + apellido compatible, candidato ÚNICO,
#         preferentemente nacido en Argentina, y edad al salir entre 16 y 38 años.
pl["ultimo"] = pl.name.map(lambda s: (norm(s) or [""])[-1])
pl["inicial"] = pl.name.map(lambda s: (norm(s) or [" "])[0][0])
pl["apellido"] = pl.name.map(lambda s: " ".join(norm(s)[1:]) if len(norm(s)) > 1 else " ".join(norm(s)))
pl["primer_nombre"] = pl.name.map(lambda s: (norm(s) or [""])[0])
usados = set(base.player_id_tm.dropna())
falt = base[base.player_id_tm.isna()][["player_id_api", "fecha_salida", "inicial", "apellido", "ultimo", "primer_nombre"]]
c2 = falt.merge(pl[["player_id", "inicial", "ultimo", "apellido", "primer_nombre", "date_of_birth", "country_of_birth",
                    "country_of_citizenship"]], on=["inicial", "ultimo"], suffixes=("", "_tm"))
c2 = c2[[apellido_compatible(a, b) for a, b in zip(c2.apellido, c2.apellido_tm)]]
c2 = c2[[nombre_compatible(a, b) for a, b in zip(c2.primer_nombre, c2.primer_nombre_tm)]]
c2 = c2[~c2.player_id.isin(usados)]
edad = (c2.fecha_salida - c2.date_of_birth).dt.days / 365.25
c2 = c2[edad.between(16, 40)]
CONMEBOL = {"Argentina", "Uruguay", "Paraguay", "Chile", "Bolivia", "Peru", "Ecuador", "Colombia", "Venezuela", "Brazil"}
c2 = c2[c2.country_of_birth.isin(CONMEBOL) | c2.country_of_citizenship.isin(CONMEBOL)]   # solo jugadores sudamericanos
c2["arg"] = (c2.country_of_birth == "Argentina") | (c2.country_of_citizenship == "Argentina")
def elegir(g):
    g2 = g[g.arg] if g.arg.any() else g
    return g2.iloc[0] if g2.player_id.nunique() == 1 else None
elegidos = [r for _, g in c2.groupby("player_id_api") if (r := elegir(g)) is not None]
m2 = pd.DataFrame(elegidos)
if len(m2):
    m2 = m2.drop_duplicates("player_id", keep=False).set_index("player_id_api")   # TM usado por 2 API: descartar ambos
    sel = base.player_id_api.isin(m2.index)
    base.loc[sel, "player_id_tm"] = base.loc[sel, "player_id_api"].map(m2.player_id)
    base.loc[sel, "metodo_emparejamiento"] = "nombre (tabla de jugadores)"

# 2b. Datos del jugador
pl_cols = pl.set_index("player_id")[["name", "date_of_birth", "position", "sub_position", "foot", "height_in_cm",
                                     "country_of_birth", "international_caps"]]
pl_cols.columns = ["nombre_tm", "fecha_nacimiento", "posicion", "sub_posicion", "pie", "altura_cm",
                   "pais_nacimiento", "partidos_seleccion"]
base = base.join(pl_cols, on="player_id_tm")
base["edad_salida"] = ((base.fecha_salida - base.fecha_nacimiento).dt.days / 365.25).round(1)
base["franja_edad"] = pd.cut(base.edad_salida, [0, 20, 23, 26, 100], right=False,
                             labels=["menos de 20", "20-22", "23-25", "26 o más"])

# 2c. Valor de mercado alrededor de la salida
val = pd.read_csv(os.path.join(TM, "player_valuations.csv"), parse_dates=["date"])
val = val[val.player_id.isin(base.player_id_tm.dropna())][["player_id", "date", "market_value_in_eur"]]
v = val.merge(base[["player_id_api", "player_id_tm", "fecha_salida"]], left_on="player_id", right_on="player_id_tm")
v["dias_desde_salida"] = (v.date - v.fecha_salida).dt.days
def valor_cerca(dias_obj, ventana):
    w = v[(v.dias_desde_salida - dias_obj).abs() <= ventana].copy()
    w["dist"] = (w.dias_desde_salida - dias_obj).abs()
    return w.sort_values("dist").drop_duplicates("player_id_api").set_index("player_id_api").market_value_in_eur
pre = v[(v.dias_desde_salida >= -365) & (v.dias_desde_salida <= 30)].sort_values("dias_desde_salida")
base["valor_salida_eur"] = base.player_id_api.map(pre.drop_duplicates("player_id_api", keep="last").set_index("player_id_api").market_value_in_eur)
base["valor_1a_eur"] = base.player_id_api.map(valor_cerca(365, 120))
base["valor_3a_eur"] = base.player_id_api.map(valor_cerca(1095, 180))
w3 = v[(v.dias_desde_salida > 0) & (v.dias_desde_salida <= 1095)]
base["valor_max_3a_eur"] = base.player_id_api.map(w3.groupby("player_id_api").market_value_in_eur.max())
base["var_valor_1a_pct"] = ((base.valor_1a_eur / base.valor_salida_eur - 1) * 100).round(1)
base["var_valor_3a_pct"] = ((base.valor_3a_eur / base.valor_salida_eur - 1) * 100).round(1)
v[["player_id_api", "player_id_tm", "date", "dias_desde_salida", "market_value_in_eur"]].rename(
    columns={"date": "fecha_valuacion", "market_value_in_eur": "valor_eur"}).to_csv(
    os.path.join(D, "analytical", "valuaciones_post_salida.csv"), index=False)

# 2d. Minutos de liga en los 3 años posteriores (solo ligas que cubre Transfermarkt)
comp = pd.read_csv(os.path.join(TM, "competitions.csv"))
ligas = comp[comp.type == "domestic_league"].competition_id
games = pd.read_csv(os.path.join(TM, "games.csv"), usecols=["competition_id", "date"], parse_dates=["date"])
cob = games[games.competition_id.isin(ligas)].groupby("competition_id").date.agg(["min", "max"])
app = pd.read_csv(os.path.join(TM, "appearances.csv"), usecols=["player_id", "date", "competition_id", "minutes_played"],
                  parse_dates=["date"])
app = app[app.player_id.isin(base.player_id_tm.dropna()) & app.competition_id.isin(ligas)]
a = app.merge(base[["player_id_api", "player_id_tm", "fecha_salida"]], left_on="player_id", right_on="player_id_tm")
a["anio_post"] = ((a.date - a.fecha_salida).dt.days // 365) + 1
a = a[a.anio_post.between(1, 3)]
mins = a.pivot_table(index="player_id_api", columns="anio_post", values="minutes_played", aggfunc="sum")
for k in [1, 2, 3]:
    base[f"minutos_liga_a{k}"] = base.player_id_api.map(mins[k]) if k in mins else np.nan
# ¿la liga de destino estaba cubierta por Transfermarkt durante el seguimiento?
pais_liga = {"México": "MEX1", "Brasil": "BRA1", "Estados Unidos": "MLS1", "Canadá": "MLS1", "Colombia": "COL1",
             "España": "ES1", "Italia": "IT1", "Inglaterra": "GB1", "Alemania": "L1", "Francia": "FR1",
             "Portugal": "PO1", "Países Bajos": "NL1", "Bélgica": "BE1", "Grecia": "GR1", "Rusia": "RU1",
             "Turquía": "TR1", "Ucrania": "UKR1", "Arabia Saudita": "SA1", "Japón": "JAP1", "Rumania": "RO1",
             "Escocia": "SC1", "Polonia": "PL1", "Suiza": "C1", "Croacia": "KR1", "Dinamarca": "DK1",
             "Serbia": "SER1", "Austria": "A1", "Noruega": "NO1", "Suecia": "SE1", "República Checa": "TS1",
             "Corea del Sur": "RSK1", "Australia": "AUS1"}
def cubierta(row):
    c = pais_liga.get(row.pais_destino)
    if c is None or c not in cob.index:
        return False
    return cob.loc[c, "min"] <= row.fecha_salida and row.fecha_salida + pd.Timedelta(days=365) <= cob.loc[c, "max"]
base["minutos_cubiertos"] = base.apply(cubierta, axis=1) & base.player_id_tm.notna()
for k in [1, 2, 3]:
    base.loc[base.minutos_cubiertos & base[f"minutos_liga_a{k}"].isna(), f"minutos_liga_a{k}"] = 0
    base.loc[~base.minutos_cubiertos, f"minutos_liga_a{k}"] = np.nan
mx = base[["minutos_liga_a1", "minutos_liga_a2", "minutos_liga_a3"]].max(axis=1)
base["consolidado"] = np.where(base.minutos_cubiertos, mx >= 1500, np.nan)

# ---------------------------------------------------------------- 3. Categorías y banderas
region = {"Inglaterra": "5 grandes ligas", "España": "5 grandes ligas", "Italia": "5 grandes ligas",
          "Alemania": "5 grandes ligas", "Francia": "5 grandes ligas",
          "Portugal": "Europa intermedia", "Países Bajos": "Europa intermedia", "Bélgica": "Europa intermedia",
          "Chile": "Sudamérica", "Uruguay": "Sudamérica", "Paraguay": "Sudamérica", "Ecuador": "Sudamérica",
          "Colombia": "Sudamérica", "Brasil": "Sudamérica", "Perú": "Sudamérica", "Bolivia": "Sudamérica",
          "Venezuela": "Sudamérica", "México": "México y EE. UU./Canadá", "Estados Unidos": "México y EE. UU./Canadá",
          "Canadá": "México y EE. UU./Canadá", "Honduras": "Centroamérica y Caribe", "Costa Rica": "Centroamérica y Caribe",
          "Guatemala": "Centroamérica y Caribe", "República Dominicana": "Centroamérica y Caribe",
          "Emiratos Árabes": "Asia y Medio Oriente", "China": "Asia y Medio Oriente", "Malasia": "Asia y Medio Oriente",
          "Arabia Saudita": "Asia y Medio Oriente", "Japón": "Asia y Medio Oriente"}
base["region_destino"] = base.pais_destino.map(region).fillna("Resto de Europa y otros")
base["anio_salida"] = base.fecha_salida.dt.year
base["seguimiento_3a_completo"] = base.fecha_salida <= CORTE_SEGUIMIENTO
base["emparejado_tm"] = base.player_id_tm.notna()
base["confianza_emparejamiento"] = base.metodo_emparejamiento.map(
    {"pase (nombre + fecha)": "alta", "nombre (tabla de jugadores)": "media"})
base["es_prestamo"] = base.tipo_pase.fillna("").str.contains("loan", case=False)

cols = ["player_id_api", "player_id_tm", "nombre_api", "nombre_tm", "fecha_nacimiento", "pais_nacimiento", "posicion",
        "sub_posicion", "pie", "altura_cm", "partidos_seleccion",
        "fecha_salida", "anio_salida", "edad_salida", "franja_edad", "tipo_pase", "es_prestamo", "monto_pase_eur",
        "club_origen_id", "club_origen", "categoria_origen", "club_destino_id", "club_destino", "pais_destino",
        "region_destino", "valor_salida_eur", "valor_1a_eur", "valor_3a_eur", "valor_max_3a_eur",
        "var_valor_1a_pct", "var_valor_3a_pct", "minutos_cubiertos", "minutos_liga_a1", "minutos_liga_a2",
        "minutos_liga_a3", "consolidado", "regreso_argentina_3a", "cambios_club_3a", "seguimiento_3a_completo",
        "emparejado_tm", "metodo_emparejamiento", "confianza_emparejamiento", "dias_dif_emparejamiento", "metodo"]
out = base[cols].rename(columns={"metodo": "metodo_clasificacion_destino"}).sort_values("fecha_salida")
out.to_csv(os.path.join(D, "analytical", "salidas_exterior.csv"), index=False)

# ---------------------------------------------------------------- 4. Resumen por club de origen (P4)
g = out.groupby(["club_origen_id", "club_origen", "categoria_origen"], dropna=False)
res = g.agg(jugadores_exportados=("player_id_api", "count"),
            edad_mediana_salida=("edad_salida", "median"),
            valor_total_salida_eur=("valor_salida_eur", "sum"),
            monto_total_pases_eur=("monto_pase_eur", "sum"),
            pct_a_europa=("region_destino", lambda s: round(100 * s.isin(["5 grandes ligas", "Europa intermedia", "Resto de Europa y otros"]).mean(), 1)),
            pct_regreso_3a=("regreso_argentina_3a", lambda s: round(100 * s.mean(), 1))).reset_index()
res.sort_values("jugadores_exportados", ascending=False).to_csv(os.path.join(D, "analytical", "resumen_clubes_origen.csv"), index=False)

print("Filas:", len(out), "| emparejadas con TM:", out.emparejado_tm.sum(),
      f"({out.emparejado_tm.mean():.0%})")
print("Con valor al salir:", out.valor_salida_eur.notna().sum(), "| con valor a 3 años:", out.valor_3a_eur.notna().sum(),
      "| con ambos y seguimiento completo:", (out.valor_salida_eur.notna() & out.valor_3a_eur.notna() & out.seguimiento_3a_completo).sum())
print("Con minutos cubiertos:", out.minutos_cubiertos.sum())
print(out.region_destino.value_counts().to_string())
