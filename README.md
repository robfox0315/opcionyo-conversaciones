# Dashboard Conversaciones y Pushes Automáticos · Opción Yo

Dashboard de producción para **Angela Osorio (Gerencia de ATC)**. Cubre exclusivamente:
1. **Conversaciones** de WhatsApp (sesiones, IA vs. escalado a humano, volumen, países, horarios).
2. **Pushes automáticos** (recordatorios, avisos de pago, notificaciones) y su **costo real**,
   porque cada conversación que Treble/WhatsApp abre se factura.

**Fuera de alcance a propósito:** incidencias técnicas / tickets de HubSpot (viven en el
dashboard **Incidencias Técnicas**, aparte) y cualquier campaña de Ventas/Marketing (fuera del
área de Angela).

---

## 🔎 Auditoría realizada antes de entregar esto

Antes de construir la versión final, audité **todos los archivos disponibles en el proyecto**,
no solo los que subiste en este chat:

| Archivo | Qué es | Se usó |
|---|---|---|
| `general_sessions_report_*.csv` | 37,340 sesiones de WhatsApp (~30 días) | ✅ Pestaña Conversaciones |
| `general-report_-_Reporte_general.csv` | 2,135 envíos de pushes (ene–jul 2026) | ✅ Pestaña Pushes |
| `Conversaciones.xlsx` | Catálogo de 141 plantillas HSM | ✅ Pestaña Catálogo |
| `Opcion_Yo___Dashboard_treble_ai.pdf` | **28 capturas del dashboard nativo de Treble** (no era un PDF real, sino un paquete de imágenes+texto) | ✅ **Aquí encontré la tarifa real de facturación** |
| `treble.csv`, `Opcion_Yo__Atención_al_cliente.xlsx` | Datos de ATC (chats inbound, agentes) | ❌ No usados — ya cubiertos por el dashboard ATC v3 existente, y no aportan a "conversaciones y pushes" |

### Hallazgo clave: la tarifa real de Treble

El archivo que llegó como `.pdf` resultó ser una exportación de imágenes del dashboard nativo de
Treble. Ahí encontré, en texto plano (capturable y auditable), la **tabla real de precios por
conversación** que usa tu cuenta:

| Volumen mensual de conversaciones | Tarifa por conversación |
|---|---|
| 0 – 5,000 | **$0.20** |
| 5,001 – 10,000 | **$0.18** |
| 10,001 – 20,000 | **$0.15** |
| más de 20,000 | **$0.12** |

Y el detalle real de gasto ("Inversión") por plantilla de ATC para una ventana de referencia
(1–11 jun 2026), que usé para **auditar el modelo**: apliqué $0.20 × conversaciones reales a las
14 plantillas de ATC reportadas y el resultado coincidió con el gasto real de Treble con
diferencia de centavos (ver pestaña **📤 Pushes → 🔎 Auditoría**, tabla completa). O sea: la
tarifa que usa el dashboard **no es un supuesto — es la tarifa real de tu contrato, verificada**.

El dashboard aplica automáticamente el tramo correcto según el volumen real de cada mes en tus
datos (mes de bajo volumen → $0.20; si algún mes supera 20,000 conversaciones → $0.12
automáticamente, sin que tengas que tocar nada).

---

## Estructura del repo
- `app.py` — aplicación Streamlit (single-file).
- `data/general_report.csv` — histórico de envíos por push (ene–jul 2026).
- `data/sessions_report.csv` — sesiones conversacionales (~30 días).
- `data/catalog.csv` — catálogo de plantillas con equipo dueño y estado.
- `requirements.txt`, `runtime.txt` — para deploy en Streamlit Cloud.

## Las 5 pestañas
1. **📊 Resumen Ejecutivo** — KPIs globales (pushes, entrega, respuesta, costo, conversaciones),
   tendencia mensual de envíos vs. costo, distribución del costo por push.
2. **📤 Pushes Automáticos & Costo** — tabla comparativa por push con costo real aplicado, más la
   sección de **Auditoría** que valida la tarifa contra el gasto real de Treble, gráficos de costo
   y tasa de respuesta por push, serie temporal por push individual.
3. **💬 Conversaciones** — volumen por tipo (outbound/inbound), % resuelto por IA vs. escalado a
   humano, distribución horaria, países de origen.
4. **🗂️ Catálogo de Plantillas** — inventario completo de las 141 plantillas, activo/inactivo por
   equipo, explorador con filtros.
5. **🎯 Insights & Recomendaciones** — hallazgos automáticos: escalamiento a humano en ascenso,
   pushes con baja entrega (dinero gastado sin llegar), concentración de costo, pushes de alto
   volumen con baja respuesta.

---

## 🚀 Integración paso a paso (deploy en Streamlit Cloud)

### 1. Crear el repositorio en GitHub
1. Entra a [github.com/robfox0315](https://github.com/robfox0315) (o tu cuenta) → **New repository**.
2. Nómbralo `opcionyo-conversaciones-pushes` (o el que prefieras).
3. Marca el repo como **privado** (los datos incluyen teléfonos de clientes).

### 2. Subir los archivos
1. Sube estos 4 archivos a la raíz del repo: `app.py`, `requirements.txt`, `runtime.txt` y este `README.md`.
2. Crea la carpeta `data/` y sube ahí los 3 CSV (`general_report.csv`, `sessions_report.csv`, `catalog.csv`).
3. Confirma que la estructura final sea:
   ```
   opcionyo-conversaciones-pushes/
   ├── app.py
   ├── requirements.txt
   ├── runtime.txt
   ├── README.md
   └── data/
       ├── general_report.csv
       ├── sessions_report.csv
       └── catalog.csv
   ```

### 3. Conectar en Streamlit Cloud
1. Entra a [share.streamlit.io](https://share.streamlit.io) → **New app**.
2. Selecciona el repositorio `opcionyo-conversaciones-pushes`.
3. Main file path: `app.py`.
4. Click **Deploy**. La primera carga tarda ~1-2 minutos (instala dependencias).

### 4. (Opcional) Restringir acceso
Si quieres que solo Angela y el equipo entren con contraseña:
1. En Streamlit Cloud → tu app → **Settings → Secrets**.
2. Agrega:
   ```
   app_password = "la-contraseña-que-elijas"
   ```
3. Guarda. La próxima vez que alguien abra el link, pedirá contraseña.

### 5. Compartir el link con Angela
Streamlit Cloud te da una URL tipo `https://opcionyo-conversaciones-pushes.streamlit.app`.
Ese es el link que le compartes.

---

## 🔄 Cómo actualizar los datos (mantenimiento mensual/semanal)

1. Exporta de nuevo el **Reporte general** de Treble (mismas columnas: `name, date, successful,
   delivered, response_rate`) → reemplaza `data/general_report.csv`.
2. Exporta el **reporte de sesiones** de Treble → reemplaza `data/sessions_report.csv`.
3. Si el catálogo de plantillas cambió (nuevas activas/inactivas), actualiza `data/catalog.csv`
   desde el Google Sheet correspondiente.
4. Sube los archivos actualizados al repo (reemplazando los existentes) — no toques `app.py`.
5. Streamlit Cloud redeploya automáticamente al detectar el cambio en GitHub.

**No hace falta tocar la tarifa de costo** — el dashboard la recalcula sola según el volumen real
de cada mes usando los tramos ya auditados.

---

## Notas de precisión (para ser honesto con los números)

- La tarifa de $0.20/$0.18/$0.15/$0.12 está **verificada contra el gasto real reportado por
  Treble** para la línea operativa de ATC — no es una suposición.
- El modelo asume que **cada push entregado abre una conversación facturable** (estándar de
  WhatsApp Business Platform). Puedes cambiar esto a "solo cuando el cliente responde" en la
  barra lateral si confirman con Treble que su facturación funciona distinto — pero la evidencia
  auditada (tarifa aplicada a *conversaciones entregadas*, no a respuestas) respalda el modelo por
  defecto.
- El tramo de precio se calcula sobre el **volumen total mensual de la cuenta** (todos los pushes
  juntos), tal como factura Treble — no por campaña individual.
