# Registro de decisiones

Cada decisión metodológica o de alcance del observatorio, con fecha, motivo y alternativas descartadas.
**Regla:** no se borra nada. Si una decisión cambia, se agrega una entrada nueva que la reemplaza y se marca la anterior como "Reemplazada por D-XX".

Formato de cada entrada: **ID · fecha · decisión · motivo · alternativas descartadas · impacto · responsable · estado**.

---

## Alcance y pregunta

### D-01 · 2026-11-19 · Cambio de línea de investigación
- **Decisión:** se abandona BacheAr y se adopta "El fútbol argentino como exportador de talento".
- **Motivo:** el grupo se redujo; se priorizó una línea con fuentes públicas ya disponibles y verificables.
- **Impacto:** se rehízo el Desafío 1.
- **Responsable:** equipo · **Estado:** aprobada por el profesor (2026-11-19).

### D-02 · 2026-11-19 · Usuario principal
- **Decisión:** clubes formadores (dirigencia y secretaría técnica).
- **Descartado:** jugadores y representantes, o clubes del interior, como usuario principal (quedan como secundarios).
- **Motivo:** son quienes toman la decisión de vender y conservan porcentajes de reventa y el 5% del mecanismo de solidaridad FIFA.
- **Estado:** vigente.

### D-03 · 2026-11-19 · Categorías incluidas
- **Decisión:** Primera (Liga Profesional / Copa de la Liga), Primera Nacional y Primera B Metro.
- **Descartado:** Federal A, Primera C, Primera D, Reserva y Promocional (para una etapa posterior).
- **Motivo:** concentran las ventas al exterior; el cupo gratuito de API-Football (100 consultas/día) no alcanzaba para todas en un día.
- **Estado:** vigente.

### D-04 · 2026-11-19 · Período y seguimiento
- **Decisión:** salidas de 2012 a 2026; "seguimiento completo de 3 años" = salida hasta el 2023-07-06 (los datos de Transfermarkt llegan al 2026-07-06).
- **Estado:** vigente.

### D-05 · 2026-11-19 · Unidad de análisis
- **Decisión:** una fila = un jugador en su **primera** salida a un club del exterior.
- **Descartado:** todas las salidas (un mismo jugador pesaría varias veces).
- **Estado:** vigente.

## Fuentes

### D-06 · 2026-11-19 · Fuentes de datos
- **Decisión:** API-Football (plan gratuito) para pases desde clubes argentinos + Transfermarkt Datasets (Kaggle, CC0) para edad, valor de mercado y minutos.
- **Descartado:** FBref (perdió las estadísticas avanzadas en enero de 2026); FootyStats (la descarga de CSV de Argentina requiere plan pago); scraping directo de transfermarkt.com (condiciones de uso).
- **Impacto:** todo el proyecto usa solo fuentes públicas y gratuitas.
- **Estado:** vigente.

## Limpieza e integración

### D-07 · 2026-11-19 · Clasificación de destinos (Argentina / exterior)
- **Decisión:** club argentino si figura en los listados de equipos de las ligas argentinas de API-Football (192 clubes); el resto se clasifica a mano por país, empezando por los 320 destinos más frecuentes (`data/processed/clasificacion_manual_destinos.csv`).
- **Descartado:** cruce automático por nombre con los clubes de Transfermarkt: daba falsos positivos (ej.: "San Luis" → México en vez de Chile; "Barcelona SC" → España en vez de Ecuador).
- **Impacto:** 90% de las salidas clasificadas; 9 clubes marcados REVISAR; ~9% sin clasificar (declarado como limitación).
- **Estado:** vigente. Pendiente: resolver los 9 REVISAR (etapa 3).

### D-08 · 2026-11-19 · Emparejamiento entre fuentes
- **Decisión:** dos métodos, en orden:
  1. **Pase (confianza alta):** mismo apellido e inicial (o nombre completo si la API lo trae), pase en ±60 días y al menos una palabra en común en el club de origen o destino.
  2. **Nombre (confianza media):** contra la tabla de jugadores de Transfermarkt; candidato único, nacido o con ciudadanía en un país de CONMEBOL.
  En ambos: edad al salir entre 16 y 40 años; un jugador de Transfermarkt nunca se asigna a dos filas.
- **Descartado:** emparejar solo por pase (22% de cobertura: Transfermarkt guarda el historial de pases solo de jugadores activos recientes).
- **Impacto:** 36% de los jugadores emparejados (19% alta, 17% media). En una muestra de 25 de confianza media se halló 1 error.
- **Estado:** vigente. Pendiente: validar una muestra de 30 (criterio de cierre: error ≤ 5%).

### D-09 · 2026-11-19 · Ventanas para el valor de mercado
- **Decisión:** valor al salir = última valuación entre 365 días antes y 30 días después de la salida; valor a 1 año = la más cercana a +365 días (±120); valor a 3 años = la más cercana a +1.095 días (±180).
- **Estado:** vigente.

## Variables y análisis

### D-10 · 2026-11-19 · Variable principal de resultado
- **Decisión:** variación del valor de mercado a 3 años.
- **Descartado como principal:** "consolidación" (≥ 1.500 minutos de liga en alguno de los 3 años): solo se puede medir en el 6% de los casos.
- **Estado:** vigente.

### D-11 · 2026-11-19 · Agrupación de destinos e hipótesis H2
- **Decisión:** la comparación principal es Sudamérica vs. Europa vs. México y EE. UU./Canadá.
- **Descartado:** "Europa intermedia vs. 5 grandes ligas" como comparación principal: solo 12 casos con valor a 3 años.
- **Estado:** vigente.

### D-12 · 2026-11-19 · Métodos estadísticos y reglas de publicación
- **Decisión:** pruebas sobre medianas (Kruskal–Wallis, Spearman) y regresión del log del valor a 3 años sobre el valor al salir, controlando edad y posición; intervalos por bootstrap.
- **No se publica:** grupos con menos de 30 jugadores (clubes: menos de 15); diferencias que desaparecen con controles; rankings individuales de juveniles; conclusiones sobre minutos; frases causales.
- **Estado:** vigente.

## Validación, producto y organización

### D-13 · 2026-11-19 · Validación de valor sin entrevistas
- **Decisión:** evidencia pública + encuesta en Google Forms + consulta a periodistas y al profesor.
- **Motivo:** no hay posibilidad de entrevistas presenciales.
- **Hipótesis de valor:** ≥ 6 de cada 10 encuestados califican el tablero con 4 o 5, y ≥ 3 piden una demo.
- **Estado:** vigente.

### D-14 · 2026-11-19 · Herramienta del tablero
- **Decisión:** Looker Studio.
- **Descartado:** Power BI (publicar online requiere cuenta institucional) y Streamlit (más trabajo de programación).
- **Estado:** vigente.

### D-15 · 2026-11-19 · Calendario y roles
- **Decisión:** entrega final supuesta el viernes 4 de diciembre de 2026. Roles: Wenceslao Villegas (datos y tablero), Julio Robinson (análisis), Rodrigo Toledo (validación y divulgación). Cada uno revisa el trabajo de otro.
- **Estado:** supuesto; confirmar fecha con la cátedra.

---

## Plantilla para nuevas decisiones

### D-XX · AAAA-MM-DD · Título
- **Decisión:**
- **Motivo:**
- **Descartado:**
- **Impacto:**
- **Responsable:**
- **Estado:** vigente / reemplazada por D-XX
