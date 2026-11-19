# Registro de fuentes (ficha de fuente)

## 1. Transfermarkt Datasets (fuente principal para valor de mercado, edad y minutos)
- **Productor:** David Cariboo, a partir de datos públicos de transfermarkt.com
- **URL:** https://www.kaggle.com/datasets/davidcariboo/player-scores · https://github.com/dcaribou/transfermarkt-datasets
- **Fecha de descarga:** 2026-11-19
- **Archivos usados:** players, transfers, player_valuations, appearances, games, competitions, clubs
- **Cobertura:** 14 ligas europeas desde 2012; Argentina (ARG1), Brasil, México, MLS, Colombia, Arabia Saudita y otras solo desde 2024. Datos hasta el 2026-07-06.
- **Actualización:** pausada desde julio de 2026.
- **Licencia:** CC0-1.0.
- **Calidad conocida:** el valor de mercado es una estimación comunitaria; el historial de pases solo está completo para jugadores activos recientes.

## 2. API-Football (fuente principal para salidas desde clubes argentinos)
- **Productor:** API-Sports — https://www.api-football.com
- **Fecha de descarga:** 2026-11-19 (plan gratuito, 100 consultas/día)
- **Consultas:** `leagues?country=Argentina`; `teams` (temporada 2024) de Liga Profesional / Copa de la Liga, Primera Nacional, B Metro, Federal A, Primera C, Primera D, Reserva y Promocional Amateur; `transfers?team=` para los 89 clubes de Primera, Primera Nacional y B Metro.
- **Cobertura:** historia completa de transferencias de esos clubes (2012–2026 usada en el análisis).
- **Condiciones de uso:** cuenta individual; no redistribuir los datos crudos.
- **Calidad conocida:** casi no informa montos; no trae fecha de nacimiento en las transferencias.
- **Pendiente (opcional):** transferencias de Federal A, Primera C y D.

## 3. Revisión humana
- `data/processed/clasificacion_manual_destinos.csv`: país de los 320 clubes de destino más frecuentes (cubren ~75% de las salidas no argentinas). 9 clubes marcados `REVISAR`.

## 4. Fuentes de contraste (agregadas)
- CIES Football Observatory, Weekly Post 546 (mayo 2026): Argentina 3.ª exportadora (1.016 jugadores en el exterior).
- FIFA Global Transfer Report 2025: Argentina 2.ª en transferencias (1.207).
