"""Clasifica el destino de cada salida (Argentina / exterior) y arma la tabla de salidas al exterior.
Entradas: raw/api_football (teams_*.json), processed/apifootball_transfers.csv,
          processed/clasificacion_manual_destinos.csv (revisión humana)
Salidas:  processed/salidas_clasificadas.csv, processed/primeras_salidas_exterior.csv
"""
import json, glob, os
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")   # carpeta data del proyecto
RAW = glob.glob(os.path.join(BASE, "raw", "api_football", "**", "teams_*.json"), recursive=True)

# 1) Clubes argentinos conocidos: todos los equipos de las ligas argentinas descargadas
arg = {}                                                   # id de club -> nombre
for f in RAW:
    for e in json.load(open(f))["response"]:
        arg[e["team"]["id"]] = e["team"]["name"]

# 2) Clubes de origen: Primera, Primera Nacional y B Metro (ids 1032/128, 129, 131)
origen = set()
for f in RAW:
    liga = os.path.basename(f).split("_")[1]               # teams_<liga>_<año>.json
    if liga in {"1032", "128", "129", "131"}:
        origen |= {e["team"]["id"] for e in json.load(open(f))["response"]}

# 3) Clasificación manual (revisión humana de los destinos más frecuentes)
manual = pd.read_csv(os.path.join(BASE, "processed", "clasificacion_manual_destinos.csv"))
manual = dict(zip(manual.club_id, manual.pais))

# 4) Transferencias
df = pd.read_csv(os.path.join(BASE, "processed", "apifootball_transfers.csv"))
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
sal = df[df.club_salida_id.isin(origen) & df.fecha.dt.year.between(2012, 2026)].copy()   # salidas de las 3 categorías
sal = sal[sal.club_salida_id != sal.club_llegada_id]                                      # descartar registros raros

def pais_destino(row):
    if row.club_llegada_id in arg:                         # club argentino conocido (automático)
        return "Argentina", "lista_api"
    if row.club_llegada_id in manual:                      # clasificado a mano
        return manual[row.club_llegada_id], "manual"
    return "SIN CLASIFICAR", "pendiente"

sal[["pais_destino", "metodo"]] = sal.apply(lambda r: pd.Series(pais_destino(r)), axis=1)
sal["es_exterior"] = ~sal.pais_destino.isin(["Argentina", "SIN CLASIFICAR", "REVISAR"])
sal.to_csv(os.path.join(BASE, "processed", "salidas_clasificadas.csv"), index=False)

# 5) Primera salida al exterior de cada jugador
ext = sal[sal.es_exterior].sort_values("fecha")
primeras = ext.drop_duplicates("player_id", keep="first")
primeras.to_csv(os.path.join(BASE, "processed", "primeras_salidas_exterior.csv"), index=False)

# 6) Resumen
print("Salidas 2012-2026 desde Primera / Nacional / B Metro:", len(sal))
print(sal.pais_destino.where(sal.pais_destino.isin(["Argentina", "SIN CLASIFICAR", "REVISAR"]), "Exterior").value_counts().to_string())
print("\nJugadores con al menos una salida al exterior:", len(primeras))
print("\nPrimera salida al exterior, por país de destino:")
print(primeras.pais_destino.value_counts().head(15).to_string())
print("\nPrimeras salidas por año:")
print(primeras.groupby(primeras.fecha.dt.year).size().to_string())
