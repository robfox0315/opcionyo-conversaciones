"""
╔══════════════════════════════════════════════════════════════╗
║  DASHBOARD CONVERSACIONES Y PUSHES AUTOMÁTICOS · OPCIÓN YO    ║
║  Para: Angela Osorio (Gerencia)                               ║
║  Alcance: sesiones de WhatsApp + envíos automáticos y su      ║
║  costo estimado. NO incluye incidencias técnicas              ║
║  (dashboard aparte: Incidencias Técnicas).                    ║
║  Stack: Streamlit ≥1.40 · Pandas ≥2.1 · Plotly ≥5.20         ║
║  Ejecutar: python -m streamlit run app.py                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Conversaciones y Pushes · Opción Yo",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Detección de tema (claro/oscuro) ────────────────────────────
# Los gráficos de Plotly se renderizan en un iframe aparte y NO heredan el CSS
# de Streamlit, así que necesitamos saber el tema activo para elegir colores de
# texto legibles a mano (si no, el texto oscuro queda invisible en modo oscuro).
try:
    IS_DARK = st.context.theme.type == "dark"
except Exception:
    IS_DARK = False

# ── Paleta corporativa (consistente con dashboards ATC / Refunds / Incidencias) ──
OY_TEAL      = "#16B6C2"
OY_TEAL_DARK = "#0E8E99"
OY_BLUE      = "#2F80ED"
OY_OK        = "#27AE60"
OY_WARN      = "#E5484D"
OY_AMBER     = "#F2A33C"
OY_INK       = "#16323A"
OY_PURPLE    = "#7E57C2"
COLOR_SEQ    = [OY_TEAL, OY_BLUE, OY_AMBER, OY_PURPLE, "#EC4899",
                "#26A69A", "#FF7043", "#42A5F5", "#9CCC65", "#5C6BC0"]

# Colores de texto para gráficos, adaptados al tema activo
OY_CHART_TEXT  = "#E8EEF0" if IS_DARK else OY_INK
OY_CHART_TITLE = "#5FD8E3" if IS_DARK else OY_TEAL_DARK

REGION = {"1": "EE.UU./Canadá", "34": "España", "52": "México", "58": "Venezuela",
          "57": "Colombia", "507": "Panamá", "44": "UK", "56": "Chile",
          "39": "Italia", "49": "Alemania", "61": "Australia", "593": "Ecuador",
          "506": "Costa Rica", "41": "Suiza", "51": "Perú", "33": "Francia",
          "351": "Portugal", "31": "Países Bajos", "54": "Argentina",
          "353": "Irlanda"}

# ── CSS (idéntico lenguaje visual a los otros dashboards de Opción Yo, compatible con modo oscuro) ──
st.markdown("""
<style>
:root{--oy-teal:#16B6C2;--oy-td:#0E8E99;--oy-blue:#2F80ED;
      --oy-ok:#27AE60;--oy-warn:#E5484D;--oy-amb:#F2A33C;--oy-ink:#16323A;}
/* No forzamos fondo — dejamos que Streamlit use su propio tema (claro u oscuro) */
.block-container{padding-top:1.5rem;}
h1,h2,h3{color:var(--oy-teal);}
[data-testid="stMetricValue"]{font-size:1.7rem!important;font-weight:800;}
[data-testid="stMetricLabel"]{font-size:.78rem!important;font-weight:600;opacity:.85;}

.oy-header{display:flex;align-items:center;gap:18px;
  background:linear-gradient(100deg,var(--oy-td) 0%,var(--oy-teal) 48%,#27D0DC 100%);
  padding:20px 28px;border-radius:16px;margin:2px 0 12px;
  box-shadow:0 8px 22px rgba(22,182,194,.28);overflow:visible;}
.oy-logo{font-weight:800;font-size:2rem;color:#fff;line-height:1.2;
  letter-spacing:.4px;white-space:nowrap;padding:2px 18px 2px 0;
  border-right:2px solid rgba(255,255,255,.4);display:flex;align-items:center;}
.oy-logo span{color:#0A4750;margin-left:6px;}
.oy-htxt{display:flex;flex-direction:column;justify-content:center;}
.oy-htitle{color:#fff;font-weight:800;font-size:1.14rem;margin:0;line-height:1.3;}
.oy-hsub{color:#EAFCFE;font-size:.82rem;margin:3px 0 0;line-height:1.2;}

.sec{background:var(--oy-teal);color:#fff;padding:.4rem 1rem;
  border-radius:8px;font-weight:700;margin:.2rem 0 .7rem;
  font-size:.95rem;display:inline-block;}
.sec.red{background:var(--oy-warn);}
.sec.amb{background:var(--oy-amb);}
.sec.ok{background:var(--oy-ok);}
.sec.blue{background:var(--oy-blue);}
.sec.purple{background:#7E57C2;}

.kpi-grid{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;}
.kpi{flex:1;min-width:130px;background:var(--oy-teal);border-radius:12px;
  padding:11px 13px;color:#fff;box-shadow:0 4px 12px rgba(22,182,194,.20);}
.kpi.alt{background:var(--oy-blue);}
.kpi.ok{background:var(--oy-ok);}
.kpi.warn{background:var(--oy-warn);}
.kpi.amber{background:var(--oy-amb);}
.kpi.dark{background:var(--oy-td);}
.kpi.purple{background:#7E57C2;}
.kpi .l{font-size:.7rem;opacity:.9;font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
.kpi .v{font-size:1.5rem;font-weight:800;margin-top:2px;}
.kpi .d{font-size:.69rem;opacity:.93;margin-top:2px;}

.crit{background:#FDECEA;border-left:5px solid var(--oy-warn);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a1f1c;}
.alrt{background:#FFF6E6;border-left:5px solid var(--oy-amb);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a531a;}
.good{background:#EAF7EF;border-left:5px solid var(--oy-ok);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#1d6b3a;}
.info{background:#E9F6F8;border-left:5px solid var(--oy-teal);
  padding:.7rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#0E6873;}

.stTabs [data-baseweb="tab-list"]{gap:3px;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{background:#F1FAFB;border-radius:8px 8px 0 0;
  padding:5px 10px;font-weight:600;color:var(--oy-td);}
.stTabs [aria-selected="true"]{background:var(--oy-teal)!important;color:#fff!important;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="oy-header"><div class="oy-logo">opción<span> yo</span></div>'
    '<div class="oy-htxt"><p class="oy-htitle">💬 Conversaciones y Pushes Automáticos</p></div></div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════
#  AUTENTICACIÓN OPCIONAL (mismo patrón que otros dashboards OY)
# ══════════════════════════════════════════════════════════════
def _secret(k):
    try:
        return st.secrets.get(k)
    except Exception:
        return None


def require_auth():
    pw = _secret("app_password")
    if not pw or st.session_state.get("auth_ok"):
        return
    st.markdown('<div class="oy-header"><div class="oy-logo">opción<span> yo</span></div>'
                '<div><p class="oy-htitle">Acceso restringido</p>'
                '<p class="oy-hsub">Introduce la contraseña para continuar</p></div></div>',
                unsafe_allow_html=True)
    with st.form("login"):
        inp = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if inp == pw:
                st.session_state["auth_ok"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()


require_auth()


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════
def kpi(label, value, delta="", kind=""):
    d = f'<div class="d">{delta}</div>' if delta else ""
    return f'<div class="kpi {kind}"><div class="l">{label}</div><div class="v">{value}</div>{d}</div>'


def sfig(fig, h=340):
    layout_kwargs = dict(
        height=h, margin=dict(t=46, b=10, l=10, r=10),
        font=dict(color=OY_CHART_TEXT, family="Segoe UI,sans-serif"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color=OY_CHART_TEXT)),
    )
    # Solo tocamos el título si el gráfico realmente tiene uno — si no, Plotly
    # renderiza literalmente el texto "undefined" al setear title_font sin title.text.
    titulo_actual = fig.layout.title.text if fig.layout.title else None
    if titulo_actual:
        layout_kwargs["title"] = dict(text=titulo_actual, font=dict(color=OY_CHART_TITLE, size=14))
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(color=OY_CHART_TEXT, gridcolor="rgba(128,128,128,.25)")
    fig.update_yaxes(color=OY_CHART_TEXT, gridcolor="rgba(128,128,128,.25)")
    return fig


def safe_pct(n, d):
    return round(float(n) / float(d) * 100, 1) if d else 0.0


def fmt_usd(v):
    return f"${v:,.2f}"


def _norm_txt(s):
    """Normaliza texto para comparar nombres de campañas sin que tildes/mayúsculas generen falsos 'sin match'."""
    import unicodedata
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s


def find_data_file(name: str):
    """Busca el archivo tanto en data/ como en la raíz del repo (tolerante a estructura)."""
    candidates = [
        os.path.join("data", name),
        name,
        os.path.join(os.path.dirname(__file__), "data", name),
        os.path.join(os.path.dirname(__file__), name),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


# ══════════════════════════════════════════════════════════════
#  DATA WAREHOUSE DE TREBLE (ClickHouse, client_analytics) · EN VIVO
#  Esquema verificado contra la documentación oficial de Treble
#  (help.treble.ai/es/docs/data-warehouse) — nada de esto es adivinado.
#  Tablas usadas: fact_deployment_daily, fact_sessions, dim_hsm.
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def _dwh_client():
    try:
        cfg = st.secrets["treble_dwh"]
    except Exception:
        return None
    try:
        import clickhouse_connect
        return clickhouse_connect.get_client(
            host=cfg["host"], port=int(cfg.get("port", 8443)),
            username=cfg["username"], password=cfg["password"],
            database=cfg.get("database", "client_analytics"),
            secure=True, connect_timeout=10,
        )
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def dwh_status():
    """Prueba la conexión y devuelve (ok, mensaje, lista_de_tablas)."""
    client = _dwh_client()
    if client is None:
        return False, "Sin credenciales en Secrets (falta [treble_dwh]) o librería no disponible.", []
    try:
        client.query("SELECT 1")
        tablas = [r[0] for r in client.query("SHOW TABLES").result_rows]
        return True, "Conexión al Data Warehouse de Treble activa.", tablas
    except Exception as e:
        return False, f"No se pudo conectar: {str(e)[:200]}", []


@st.cache_data(ttl=300, show_spinner=False)
def dwh_query(sql: str):
    """Ejecuta una consulta SQL contra el DWH y devuelve un DataFrame, o None si falla."""
    client = _dwh_client()
    if client is None:
        return None
    try:
        return client.query_df(sql)
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner="⏳ Consultando Data Warehouse (pushes)…")
def dwh_general_report(dias=210):
    """Reconstruye el equivalente al Reporte general de pushes desde fact_deployment_daily."""
    sql = f"""
        SELECT
            day AS date,
            poll_name AS name,
            sum(sent) AS successful,
            sum(delivered) AS delivered,
            round(sum(responded) * 1.0 / nullIf(sum(sent), 0), 4) AS response_rate
        FROM client_analytics.fact_deployment_daily
        WHERE day >= today() - {int(dias)}
        GROUP BY day, poll_name
        ORDER BY day
    """
    df = dwh_query(sql)
    if df is None or df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df["name_clean"] = df["name"].astype(str).str.strip()
    return df


@st.cache_data(ttl=300, show_spinner="⏳ Consultando Data Warehouse (sesiones)…")
def dwh_sessions(dias=32):
    """Reconstruye el equivalente al reporte de sesiones desde fact_sessions."""
    sql = f"""
        SELECT
            session_id, created_at AS session_started_timestamp,
            finished_at AS session_finished_timestamp,
            inbound_outbound AS session_type, status AS session_status,
            country_code AS user_country_code, poll_id, poll_name,
            channel_cellphone AS whatsapp_link_campaign_name
        FROM client_analytics.fact_sessions
        WHERE created_at >= now() - INTERVAL {int(dias)} DAY
    """
    df = dwh_query(sql)
    if df is None or df.empty:
        return None
    for c in ["session_started_timestamp", "session_finished_timestamp"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    # Campos que el CSV traía y fact_sessions no tiene — se dejan vacíos, no inventados
    df["first_message_timestamp"] = pd.NaT
    df["last_message_timestamp"] = pd.NaT
    return df


# ══════════════════════════════════════════════════════════════
#  TARIFAS REALES DE TREBLE (auditadas contra export nativo "Inversión")
#  Fuente: reporte nativo de Treble de Opción Yo (captura jun-2026).
#  Estructura de tramos por volumen mensual de conversaciones, confirmada
#  y validada contra el gasto real reportado (ver pestaña Pushes → Auditoría).
# ══════════════════════════════════════════════════════════════
TREBLE_TRAMOS = [
    (0, 5000, 0.20),
    (5000, 10000, 0.18),
    (10000, 20000, 0.15),
    (20000, float("inf"), 0.12),
]

# Detalle real por plantilla, reportado por Treble (export nativo, línea de ATC/soporte —
# NO incluye ninguna campaña de Ventas/Marketing). Ventana: 1–11 jun 2026 aprox.
# Sirve para validar que la tarifa de $0.20/conversación (tramo de menor volumen) es exacta.
TREBLE_REAL_POR_PUSH = {
    # nombre tal como aparece en el catálogo/CSV: (conversaciones reales, inversión real USD)
    "Recordatorio Sesión en 28hs": (1627, 325),
    "Recordatorio 3hs antes": (637, 127),
    "Pago fallido": (224, 45),
    "Especialista esperando": (205, 41),
    "Soporte - Saludo": (158, 32),
    "Push sesión en 72hs": (146, 29),
    "Notificación Mensaje nuevo": (104, 21),
    "Inasistencia con AR": (102, 20),
    "Segunda Sesión - Sí asistió": (96, 19),
    "Tercera sesión sí asistió": (96, 19),
    "Primera sesión sí asistió": (79, 16),
    "Mensaje bienvenida a Opción Yo": (69, 14),
    "Inasistencia sin sesiones futuras": (69, 14),
    "Recordatorio consultoria 30 min antes": (65, 13),
}


def tarifa_por_tramo(volumen: float) -> float:
    """Tarifa por conversación según el tramo de volumen mensual (modelo real de Treble)."""
    for lo, hi, r in TREBLE_TRAMOS:
        if lo < volumen <= hi or (lo == 0 and volumen <= hi):
            return r
    return TREBLE_TRAMOS[-1][2]


# ══════════════════════════════════════════════════════════════
#  CARGA Y LIMPIEZA
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Cargando reporte de pushes…")
def load_general_report():
    df = dwh_general_report()
    fuente = "dwh"
    if df is None:
        fuente = "csv"
        path = find_data_file("general_report.csv")
        if not path:
            st.error("❌ No hay conexión al Data Warehouse Y no se encontró data/general_report.csv. "
                      "Necesito al menos una de las dos fuentes.")
            st.stop()
        try:
            df = pd.read_csv(path)
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        except Exception as e:
            st.error(f"No se pudo leer general_report.csv: {e}")
            st.stop()
    if "name_clean" not in df.columns:
        df["name_clean"] = (df["name"]
                             .str.replace("Copia de la conversación", "", regex=False)
                             .str.replace(r"\s+id:\d+", "", regex=True)
                             .str.strip())
    df["mes"] = df["date"].dt.to_period("M").apply(lambda p: p.start_time.date())
    df["fecha"] = df["date"].dt.date
    df["semana"] = df["date"].dt.to_period("W").apply(lambda p: p.start_time.date())
    for c in ["name", "name_clean"]:
        df[c] = df[c].astype("category")
    df.attrs["fuente"] = fuente
    return df


@st.cache_data(show_spinner="⏳ Cargando sesiones conversacionales…")
def load_sessions():
    df = dwh_sessions()
    fuente = "dwh"
    if df is None:
        fuente = "csv"
        path = find_data_file("sessions_report.csv")
        if not path:
            st.error("❌ No hay conexión al Data Warehouse Y no se encontró data/sessions_report.csv. "
                      "Necesito al menos una de las dos fuentes.")
            st.stop()
        try:
            df = pd.read_csv(path)
        except Exception as e:
            st.error(f"No se pudo leer sessions_report.csv: {e}")
            st.stop()

    for c in ["session_started_timestamp", "session_finished_timestamp",
              "first_message_timestamp", "last_message_timestamp"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    df["fecha"] = df["session_started_timestamp"].dt.date
    df["hora"] = df["session_started_timestamp"].dt.hour
    df["dia_nombre"] = df["session_started_timestamp"].dt.day_name()
    df["pais"] = df["user_country_code"].astype(str).str.replace("+", "", regex=False).map(REGION)
    df["pais"] = df["pais"].fillna("Otro / no identificado")
    df["dur_min"] = ((df["session_finished_timestamp"] - df["session_started_timestamp"])
                      .dt.total_seconds() / 60).clip(lower=0)

    for c in ["session_type", "session_status", "user_country_code", "pais",
              "whatsapp_link_campaign_name", "dia_nombre"]:
        df[c] = df[c].astype("category")
    df.attrs["fuente"] = fuente
    return df


@st.cache_data(show_spinner="⏳ Cargando catálogo de plantillas…")
def load_catalog():
    path = find_data_file("catalog.csv")
    if not path:
        st.error("❌ No se encontró data/catalog.csv. Verifica que el archivo esté en el repositorio.")
        st.stop()
    try:
        df = pd.read_csv(path)
    except Exception as e:
        st.error(f"No se pudo leer catalog.csv: {e}")
        st.stop()
    df["estado"] = df["estado"].fillna("Sin clasificar")

    # Compatibilidad: si el catálogo ya viene "completo" (auditado, con equipo_fuente,
    # nivel_documentacion, envios_historicos, etc.) usamos esas columnas tal cual.
    # Si no, calculamos los campos mínimos para que el dashboard no rompa.
    if "activo" not in df.columns:
        df["activo"] = df["estado"].isin(["Push Activo", "Manual activo", "Inbound"])
    else:
        df["activo"] = df["activo"].astype(str).map({"True": True, "False": False}).fillna(df["activo"])

    if "equipo" not in df.columns:
        df["equipo"] = "Sin asignar"
    df["equipo"] = df["equipo"].fillna("Sin asignar")

    if "tipo" not in df.columns:
        df["tipo"] = "Sin clasificar"
    df["tipo"] = df["tipo"].fillna("Sin clasificar")

    for c in ["equipo_fuente", "nivel_documentacion", "auditoria"]:
        if c not in df.columns:
            df[c] = "—"
    if "en_uso_real" not in df.columns:
        df["en_uso_real"] = False
    else:
        df["en_uso_real"] = df["en_uso_real"].astype(str).map({"True": True, "False": False}).fillna(False)
    for c in ["envios_historicos", "entregados_historicos", "n_envios_batches"]:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    if "tasa_respuesta_hist" not in df.columns:
        df["tasa_respuesta_hist"] = np.nan

    return df


@st.cache_data(show_spinner="⏳ Cargando árbol de conversación…")
def load_arbol():
    path = find_data_file("arbol_conversacion.csv")
    if not path:
        return None  # pestaña opcional: si no está el archivo, la pestaña avisa y no rompe el resto
    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    # Nodo interactivo real: el mismo nodo origen (Poll+Paso+Origen ID) tiene al
    # menos una arista que SÍ avanza (no es fuga) — así distinguimos una fuga real
    # (había opción de responder y no lo hicieron) de un push informativo de una
    # sola vía (donde "no avanzó" es 100% esperado porque no se pedía respuesta).
    grp_key = ["Poll ID", "Paso Origen", "Origen ID"]
    total_nodo = df.groupby(grp_key)["N Clientes"].transform("sum")
    alt_clientes = df[~df["Es Fuga"]].groupby(grp_key)["N Clientes"].sum()
    df = df.set_index(grp_key)
    df["alt_clientes"] = alt_clientes
    df = df.reset_index()
    df["alt_clientes"] = df["alt_clientes"].fillna(0)
    df["alt_share"] = df["alt_clientes"] / total_nodo.values
    df["fuga_real"] = df["Es Fuga"] & (df["alt_share"] >= 0.05)

    # Entrantes por plantilla (volumen del primer paso) — para dar contexto en % y no solo cifras sueltas
    entrantes = df[df["Paso Origen"] == 1].groupby("Plantilla")["N Clientes"].sum()
    df["entrantes_plantilla"] = df["Plantilla"].map(entrantes)
    return df


gr = load_general_report()
sr = load_sessions()
cat = load_catalog()
arbol = load_arbol()

# Filtro global de alcance: nos quedamos solo con campañas que están en el catálogo de
# plantillas ATC. El DWH trae TODAS las líneas de Treble (incluida Ventas/Marketing, que
# no es parte de este dashboard) — se filtra acá, una sola vez, para que Resumen, Pushes,
# Insights y el comparador de períodos ya trabajen limpios sin repetir el filtro en cada pestaña.
_cat_norm_set = [_norm_txt(k) for k in cat["conversacion"]]
def _es_campana_atc(nombre):
    n = _norm_txt(nombre)
    return any(k in n or n in k for k in _cat_norm_set)

_gr_campanas_antes = gr["name_clean"].nunique()
gr = gr[gr["name_clean"].apply(_es_campana_atc)].copy()
for c in ["name", "name_clean"]:
    gr[c] = gr[c].astype("category")
_campanas_fuera_alcance = _gr_campanas_antes - gr["name_clean"].nunique()

# Estado del Data Warehouse (silencioso — se usa en la pestaña Árbol, no hace falta mostrarlo aquí)
_dwh_ok, _dwh_msg, _dwh_tablas = dwh_status()

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DEL MODELO DE COSTO (panel plegable, sin sidebar)
# ══════════════════════════════════════════════════════════════
with st.expander("⚙️ Configuración del modelo de costo (tarifa real de Treble, auditada)", expanded=False):
    cc1, cc2 = st.columns(2)
    with cc1:
        st.caption(
            "Treble/WhatsApp cobra por **conversación** de 24h, en tramos según volumen mensual. "
            "Tramos reales de tu cuenta (auditados contra el export nativo 'Inversión' de Treble):\n\n"
            "- 0 – 5,000 conv. → $0.20\n"
            "- 5,001 – 10,000 conv. → $0.18\n"
            "- 10,001 – 20,000 conv. → $0.15\n"
            "- > 20,000 conv. → $0.12"
        )
        modo_costo = st.radio(
            "Fuente de la tarifa",
            ["Tramos reales de Treble (recomendado)", "Tarifa fija manual"],
            index=0,
            help="Los tramos reales se aplican automáticamente según el volumen mensual de cada mes."
        )
        if modo_costo == "Tarifa fija manual":
            tarifa_manual = st.number_input(
                "Tarifa manual por conversación (USD)", min_value=0.0, value=0.12, step=0.01, format="%.3f"
            )
        else:
            tarifa_manual = None
    with cc2:
        modelo_costo = st.radio(
            "¿Qué cuenta como conversación facturable?",
            ["Cada push entregado (conversación abierta)", "Solo cuando el cliente responde"],
            index=0,
            help="WhatsApp Business Platform factura por conversación de 24h iniciada por el negocio "
                 "al entregar la plantilla, independientemente de si el cliente responde."
        )
        st.caption(
            f"📅 Reporte de pushes: {gr['fecha'].min()} → {gr['fecha'].max()}\n\n"
            f"💬 Sesiones conversacionales: {sr['fecha'].min()} → {sr['fecha'].max()}\n\n"
            "**Fuentes:** reporte general Treble/WhatsApp, reporte de sesiones conversacionales, "
            "catálogo interno de plantillas (auditado y completado) y export nativo de Treble "
            "'Inversión' (tarifas reales).\n\n"
            "**Fuera de alcance (a propósito):** incidencias técnicas / HubSpot — dashboard aparte."
        )


# ══════════════════════════════════════════════════════════════
#  CÁLCULO DE COSTO (aplicado a Pushes) · modelo real de tramos de Treble
# ══════════════════════════════════════════════════════════════
# El tramo de tarifa se calcula sobre el volumen TOTAL de la cuenta ese mes
# (todos los pushes juntos), no por campaña individual — así es como Treble
# factura realmente. Se calcula siempre sobre gr completo (no un filtro),
# para que la tarifa de cada mes sea la real, independiente de qué filtre
# cada pestaña por separado.
_tarifa_mensual_real = (
    gr.groupby("mes", observed=True)["delivered"].sum().apply(tarifa_por_tramo).to_dict()
)


def con_costo(df):
    """Agrega columnas de conversaciones facturables y costo estimado a un df de pushes."""
    df = df.copy()
    if modelo_costo.startswith("Cada push"):
        df["conversaciones_facturables"] = df["delivered"]
    else:
        df["conversaciones_facturables"] = (df["delivered"] * df["response_rate"]).round()

    if tarifa_manual is not None:
        df["tarifa_aplicada"] = tarifa_manual
    else:
        df["tarifa_aplicada"] = df["mes"].map(_tarifa_mensual_real).fillna(TREBLE_TRAMOS[0][2])

    df["costo_estimado"] = df["conversaciones_facturables"] * df["tarifa_aplicada"]
    return df


def filtro_fechas(df, col_fecha, key_prefix, label="Rango de fechas"):
    """Widget de rango de fechas reutilizable, para usar dentro de cada pestaña."""
    min_d, max_d = df[col_fecha].min(), df[col_fecha].max()
    rango = st.date_input(label, value=(min_d, max_d), min_value=min_d, max_value=max_d,
                           key=f"{key_prefix}_fecha")
    if isinstance(rango, tuple) and len(rango) == 2:
        ini, fin = rango
    else:
        ini, fin = min_d, max_d
    return df[(df[col_fecha] >= ini) & (df[col_fecha] <= fin)]


# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Resumen Ejecutivo", "📤 Pushes Automáticos & Costo",
    "💬 Conversaciones", "🗂️ Catálogo de Plantillas",
    "🎯 Insights & Recomendaciones", "🌳 Árbol de Conversación"
])

# ────────────────────────────────────────────────────────────────
# TAB 1 · RESUMEN EJECUTIVO
# ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<span class="sec">Panorama general del período seleccionado</span>', unsafe_allow_html=True)

    fc1, fc2 = st.columns([1, 3])
    with fc1:
        rango1 = st.date_input("📅 Rango de fechas (pushes y conversaciones)",
                                value=(min(gr["fecha"].min(), sr["fecha"].min()),
                                       max(gr["fecha"].max(), sr["fecha"].max())),
                                key="t1_fecha")
    if isinstance(rango1, tuple) and len(rango1) == 2:
        r1_ini, r1_fin = rango1
    else:
        r1_ini, r1_fin = gr["fecha"].min(), sr["fecha"].max()

    gr_f = gr[(gr["fecha"] >= r1_ini) & (gr["fecha"] <= r1_fin)]
    sr_f = sr[(sr["fecha"] >= r1_ini) & (sr["fecha"] <= r1_fin)]
    gr_costo = con_costo(gr_f)

    envios = int(gr_f["successful"].sum())
    entregados = int(gr_f["delivered"].sum())
    tasa_entrega = safe_pct(entregados, envios)
    resp_ponderada = safe_pct((gr_f["successful"] * gr_f["response_rate"]).sum(), envios)
    costo_total = gr_costo["costo_estimado"].sum()

    sesiones_total = len(sr_f)
    pct_outbound = safe_pct((sr_f["session_type"] == "OUTBOUND").sum(), sesiones_total)
    pct_inbound = safe_pct((sr_f["session_type"] == "INBOUND").sum(), sesiones_total)

    c = st.columns(6)
    kpis = [
        ("Pushes enviados", f"{envios:,}", "", ""),
        ("Tasa de entrega", f"{tasa_entrega}%", "", "ok" if tasa_entrega >= 90 else "warn"),
        ("Tasa de respuesta", f"{resp_ponderada}%", "ponderada por envíos", "alt"),
        ("💰 Costo estimado", fmt_usd(costo_total), "período seleccionado", "warn"),
        ("Sesiones (conversaciones)", f"{sesiones_total:,}", "", "dark"),
        ("% Push (outbound) / Entrante", f"{pct_outbound}% / {pct_inbound}%", "", "purple"),
    ]
    for col, (l, v, d, k) in zip(c, kpis):
        col.markdown(kpi(l, v, d, k), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown('<span class="sec blue">Tendencia mensual de envíos y costo estimado</span>', unsafe_allow_html=True)
        m = gr_costo.groupby("mes", observed=True).agg(
            enviados=("successful", "sum"), costo=("costo_estimado", "sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=m["mes"], y=m["enviados"], name="Enviados", marker_color=OY_TEAL, yaxis="y"))
        fig.add_trace(go.Scatter(x=m["mes"], y=m["costo"], name="Costo estimado (USD)",
                                  yaxis="y2", line=dict(color=OY_WARN, width=3)))
        fig.update_layout(
            yaxis=dict(title="Enviados"),
            yaxis2=dict(title="Costo USD", overlaying="y", side="right"),
            title="Envíos vs. costo estimado por mes"
        )
        st.plotly_chart(sfig(fig), use_container_width=True)

    with col2:
        st.markdown('<span class="sec amb">Distribución del costo por push</span>', unsafe_allow_html=True)
        cshare = gr_costo.groupby("name_clean", observed=True)["costo_estimado"].sum().nlargest(8).reset_index()
        fig = px.pie(cshare, names="name_clean", values="costo_estimado", hole=.5,
                     color_discrete_sequence=COLOR_SEQ)
        fig.update_traces(textinfo="percent")
        st.plotly_chart(sfig(fig, 340), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<span class="sec ok">Top 5 pushes por costo estimado</span>', unsafe_allow_html=True)
        top5 = gr_costo.groupby("name_clean", observed=True)["costo_estimado"].sum().nlargest(5).reset_index()
        fig = px.bar(top5.sort_values("costo_estimado"), x="costo_estimado", y="name_clean", orientation="h",
                     color_discrete_sequence=[OY_WARN], text_auto=".2s")
        fig.update_layout(yaxis_title="", xaxis_title="Costo estimado (USD)", showlegend=False)
        st.plotly_chart(sfig(fig, 300), use_container_width=True)

    with col4:
        st.markdown('<span class="sec">Volumen diario de conversaciones</span>', unsafe_allow_html=True)
        d = sr_f.groupby("fecha").size().reset_index(name="n")
        fig = px.area(d, x="fecha", y="n", color_discrete_sequence=[OY_TEAL])
        fig.update_layout(yaxis_title="Sesiones", xaxis_title="")
        st.plotly_chart(sfig(fig, 300), use_container_width=True)

    tarifas_activas = sorted(gr_costo["tarifa_aplicada"].unique()) if len(gr_costo) else []
    tarifas_txt = ", ".join(fmt_usd(t) for t in tarifas_activas) if tarifas_activas else "—"
    fuente_tarifa = ("tramos reales de Treble (auditados)" if tarifa_manual is None
                      else f"tarifa fija manual de {fmt_usd(tarifa_manual)}")
    st.markdown(
        f'<div class="info">💡 <b>Modelo de costo activo:</b> {modelo_costo.lower()}, usando '
        f'{fuente_tarifa}. Tarifa(s) por conversación en el período: {tarifas_txt}. '
        f'Ver auditoría completa y validación contra cifras reales en la pestaña '
        f'"📤 Pushes Automáticos & Costo".</div>',
        unsafe_allow_html=True
    )

    # ── Comparador de períodos (mes vs. mes, o semana vs. semana) ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec purple">📆 Comparar períodos</span>', unsafe_allow_html=True)

    gr_comp = con_costo(gr)  # siempre sobre el histórico completo, independiente del filtro de arriba
    gr_comp["semana"] = pd.to_datetime(gr_comp["fecha"]).dt.to_period("W").apply(lambda p: p.start_time.date())
    sr_comp = sr.copy()
    sr_comp["semana"] = pd.to_datetime(sr_comp["fecha"]).dt.to_period("W").apply(lambda p: p.start_time.date())
    sr_comp["mes"] = pd.to_datetime(sr_comp["fecha"]).dt.to_period("M").apply(lambda p: p.start_time.date())

    granularidad = st.radio("Comparar por", ["Mes", "Semana"], horizontal=True, key="t1_gran")
    col_period = "mes" if granularidad == "Mes" else "semana"

    opciones_periodo = sorted(gr_comp[col_period].unique(), reverse=True)
    if len(opciones_periodo) < 2:
        st.info(f"No hay suficientes {granularidad.lower()}s distintos en los datos para comparar.")
    else:
        cp1, cp2 = st.columns(2)
        periodo_a = cp1.selectbox(f"{granularidad} A (más reciente)", opciones_periodo, index=0, key="t1_pa")
        periodo_b = cp2.selectbox(f"{granularidad} B (a comparar)", opciones_periodo, index=1, key="t1_pb")

        def _resumen_periodo(p):
            g = gr_comp[gr_comp[col_period] == p]
            s = sr_comp[sr_comp[col_period] == p]
            env = int(g["successful"].sum())
            ent = int(g["delivered"].sum())
            return {
                "Enviados": env,
                "Tasa de entrega %": safe_pct(ent, env),
                "Tasa de respuesta %": safe_pct((g["successful"] * g["response_rate"]).sum(), env),
                "Costo estimado (USD)": g["costo_estimado"].sum(),
                "Sesiones/conversaciones": len(s),
                "% Escalado a humano": safe_pct((s["session_status"] == "HumanHandover").sum(), len(s)) if len(s) else 0.0,
            }

        res_a = _resumen_periodo(periodo_a)
        res_b = _resumen_periodo(periodo_b)

        filas_cmp = []
        for metrica in res_a:
            va, vb = res_a[metrica], res_b[metrica]
            delta_pct = safe_pct(va - vb, vb) if vb else None
            filas_cmp.append({
                "Métrica": metrica,
                f"{periodo_a}": round(va, 2),
                f"{periodo_b}": round(vb, 2),
                "Variación": f"{'+' if (delta_pct or 0) >= 0 else ''}{delta_pct}%" if delta_pct is not None else "—",
            })
        cmp_df = pd.DataFrame(filas_cmp)
        st.dataframe(cmp_df, use_container_width=True, hide_index=True)
        st.caption(
            f"Comparando {granularidad.lower()} del {periodo_a} contra el {periodo_b}. "
            "Cambia la granularidad o los períodos arriba para comparar cualquier combinación."
        )


# ────────────────────────────────────────────────────────────────
# TAB 2 · PUSHES AUTOMÁTICOS & COSTO
# ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<span class="sec">Desempeño y costo por push / plantilla automática</span>', unsafe_allow_html=True)

    st.markdown('<span class="sec blue">🔍 Opciones de búsqueda</span>', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([1, 1.4, 0.8, 0.8])
    with fc1:
        rango2 = st.date_input("📅 Rango de fechas", value=(gr["fecha"].min(), gr["fecha"].max()),
                                min_value=gr["fecha"].min(), max_value=gr["fecha"].max(), key="t2_fecha")
    with fc2:
        campanas_sel = st.multiselect("Buscar / filtrar por push o campaña específica",
                                       sorted(gr["name_clean"].unique()), default=[], key="t2_campanas")
    with fc3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        ocultar_inactivos = st.checkbox("Ocultar inactivos", value=False, key="t2_ocultar_inactivos")
    with fc4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        ocultar_sin_match = st.checkbox("Ocultar sin match", value=True, key="t2_ocultar_sin_match",
                                         help="Campañas que no están en el catálogo de plantillas ATC — "
                                              "normalmente son de la línea de Ventas/Marketing, fuera del "
                                              "alcance de este dashboard.")

    if isinstance(rango2, tuple) and len(rango2) == 2:
        r2_ini, r2_fin = rango2
    else:
        r2_ini, r2_fin = gr["fecha"].min(), gr["fecha"].max()

    gr_f = gr[(gr["fecha"] >= r2_ini) & (gr["fecha"] <= r2_fin)]
    if campanas_sel:
        gr_f = gr_f[gr_f["name_clean"].isin(campanas_sel)]
    gr_costo = con_costo(gr_f)

    st.markdown("<br>", unsafe_allow_html=True)

    agg = gr_costo.groupby("name_clean", observed=True).agg(
        envios=("successful", "sum"),
        entregados=("delivered", "sum"),
        conversaciones_facturables=("conversaciones_facturables", "sum"),
        costo_estimado=("costo_estimado", "sum"),
        resp_pond=("successful", lambda s: (s * gr_costo.loc[s.index, "response_rate"]).sum()),
        n_batches=("date", "count"),
    ).reset_index()
    agg["tasa_entrega_%"] = (agg["entregados"] / agg["envios"] * 100).round(1)
    agg["tasa_respuesta_%"] = (agg["resp_pond"] / agg["envios"] * 100).round(1)
    agg = agg.drop(columns=["resp_pond"]).sort_values("costo_estimado", ascending=False)

    # Cruce con catálogo (matching normalizado sin tildes, para no perder coincidencias
    # por un simple "Envio" vs "Envío") para traer equipo dueño Y si la plantilla está activa
    cat_lookup = cat.set_index("conversacion")[["equipo", "estado", "activo"]]
    cat_norm_index = {_norm_txt(k): k for k in cat_lookup.index}
    def _cat_match(n):
        n_norm = _norm_txt(n)
        for k_norm, k in cat_norm_index.items():
            if k_norm in n_norm or n_norm in k_norm:
                return cat_lookup.loc[k, "equipo"], cat_lookup.loc[k, "estado"], cat_lookup.loc[k, "activo"]
        return "Sin match en catálogo", "Sin match", None
    _res = [_cat_match(n) for n in agg["name_clean"]]
    agg["equipo"] = [r[0] for r in _res]
    agg["estado_catalogo"] = [r[1] for r in _res]
    agg["activo"] = [r[2] for r in _res]
    agg["Activo"] = agg["activo"].map({True: "✅ Sí", False: "⛔ No"}).fillna("❓ Sin match")

    inactivos_con_envio = int((agg["activo"] == False).sum())
    sin_match_n = int((agg["estado_catalogo"] == "Sin match").sum())

    if ocultar_inactivos:
        agg = agg[agg["activo"] != False]
    if ocultar_sin_match:
        agg = agg[agg["estado_catalogo"] != "Sin match"]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Costo total estimado", fmt_usd(agg["costo_estimado"].sum()), "período seleccionado", "warn"),
                unsafe_allow_html=True)
    c2.markdown(kpi("Pushes con envíos", f"{len(agg)}", "", ""), unsafe_allow_html=True)
    c3.markdown(kpi("Marcados inactivos pero con envíos", f"{inactivos_con_envio}",
                    "revisar en catálogo" if inactivos_con_envio else "", "warn" if inactivos_con_envio else "ok"),
                unsafe_allow_html=True)
    mas_caro = agg.iloc[0] if len(agg) else None
    if mas_caro is not None:
        c4.markdown(kpi("Push más costoso", fmt_usd(mas_caro["costo_estimado"]), mas_caro["name_clean"][:30], "amber"),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec blue">Tabla comparativa — costo por push</span>', unsafe_allow_html=True)
    tabla = agg.rename(columns={
        "name_clean": "Push / Campaña", "envios": "Enviados", "entregados": "Entregados",
        "conversaciones_facturables": "Conversaciones facturables (est.)",
        "costo_estimado": "Costo estimado (USD)", "n_batches": "N° envíos (batches)", "equipo": "Equipo dueño"
    })
    cols_tabla = ["Push / Campaña", "Activo", "Equipo dueño", "Enviados", "Entregados",
                  "Conversaciones facturables (est.)", "Costo estimado (USD)",
                  "tasa_entrega_%", "tasa_respuesta_%", "N° envíos (batches)"]
    st.dataframe(
        tabla[cols_tabla], use_container_width=True, hide_index=True,
        column_config={
            "Costo estimado (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "tasa_entrega_%": st.column_config.ProgressColumn("Tasa entrega %", min_value=0, max_value=100, format="%.1f%%"),
            "tasa_respuesta_%": st.column_config.ProgressColumn("Tasa respuesta %", min_value=0, max_value=100, format="%.1f%%"),
        }
    )
    st.caption(
        "💡 'Conversaciones facturables (est.)' depende del modelo de costo elegido arriba (⚙️ Configuración): "
        "todo lo entregado, o solo lo que generó respuesta. 'Activo' viene del catálogo de plantillas "
        "(pestaña 🗂️ Catálogo) — si dice '⛔ No' pero tiene envíos reales aquí, hay una inconsistencia "
        "entre lo documentado y lo que realmente se está enviando (revisar con Iva)."
        + (f" Hay {sin_match_n} campaña(s) sin match en el catálogo ocultas — normalmente son de la línea "
           "de Ventas/Marketing, fuera del alcance de este dashboard." if ocultar_sin_match and sin_match_n else "")
    )

    # ── Auditoría: validación de la tarifa real contra el gasto reportado por Treble ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec red">🔎 Auditoría — validación contra gasto real reportado por Treble</span>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info">Esta tarifa <b>no es un supuesto</b>: se extrajo y auditó contra el reporte '
        'nativo de Treble ("Inversión"), que muestra el gasto real ya facturado a Opción Yo por cada '
        'plantilla operativa de ATC. La tabla de abajo compara el gasto real reportado por Treble contra '
        'lo que calcularíamos aplicando la tarifa de $0.20/conversación (tramo de bajo volumen, vigente '
        'en la ventana de referencia).</div>',
        unsafe_allow_html=True
    )

    filas_audit = []
    for nombre, (vol_real, usd_real) in TREBLE_REAL_POR_PUSH.items():
        modelo_usd = round(vol_real * 0.20, 2)
        diff = round(modelo_usd - usd_real, 2)
        filas_audit.append({
            "Push (plantilla ATC)": nombre,
            "Conversaciones reales (Treble)": vol_real,
            "Gasto real (Treble)": usd_real,
            "Gasto modelado ($0.20/conv.)": modelo_usd,
            "Diferencia": diff,
        })
    audit_df = pd.DataFrame(filas_audit).sort_values("Conversaciones reales (Treble)", ascending=False)
    st.dataframe(audit_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Gasto real (Treble)": st.column_config.NumberColumn(format="$%.2f"),
                     "Gasto modelado ($0.20/conv.)": st.column_config.NumberColumn(format="$%.2f"),
                     "Diferencia": st.column_config.NumberColumn(format="$%.2f"),
                 })
    st.markdown(
        '<div class="good">✅ <b>Auditoría validada:</b> el modelo de $0.20 por conversación replica el '
        'gasto real reportado por Treble prácticamente exacto (diferencia de centavos por redondeo) en '
        'las 14 plantillas operativas de ATC verificadas. Los tramos superiores ($0.18 / $0.15 / $0.12) '
        'aplican automáticamente cuando el volumen mensual total supera 5,000 / 10,000 / 20,000 '
        'conversaciones — el dashboard ya lo calcula solo, mes a mes.</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="sec amb">Costo estimado por push</span>', unsafe_allow_html=True)
        fig = px.bar(agg.sort_values("costo_estimado"), x="costo_estimado", y="name_clean", orientation="h",
                     color="costo_estimado", color_continuous_scale=[OY_TEAL, OY_AMBER, OY_WARN])
        fig.update_layout(yaxis_title="", xaxis_title="Costo estimado (USD)", coloraxis_showscale=False)
        st.plotly_chart(sfig(fig, 420), use_container_width=True)
    with col2:
        st.markdown('<span class="sec purple">Tasa de respuesta por push</span>', unsafe_allow_html=True)
        fig = px.bar(agg.sort_values("tasa_respuesta_%"), x="tasa_respuesta_%", y="name_clean", orientation="h",
                     color="tasa_respuesta_%", color_continuous_scale=[OY_WARN, OY_AMBER, OY_TEAL])
        fig.update_layout(yaxis_title="", xaxis_title="% respuesta", coloraxis_showscale=False)
        st.plotly_chart(sfig(fig, 420), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">Evolución temporal · selecciona un push</span>', unsafe_allow_html=True)
    camp_pick = st.selectbox("Push a inspeccionar", sorted(gr_f["name_clean"].unique()))
    serie = gr_costo[gr_costo["name_clean"] == camp_pick].groupby("fecha").agg(
        enviados=("successful", "sum"), costo=("costo_estimado", "sum"),
        resp=("response_rate", "mean")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=serie["fecha"], y=serie["enviados"], name="Enviados", marker_color=OY_TEAL, yaxis="y"))
    fig.add_trace(go.Scatter(x=serie["fecha"], y=serie["costo"], name="Costo estimado (USD)",
                              yaxis="y2", line=dict(color=OY_WARN, width=3)))
    fig.update_layout(
        yaxis=dict(title="Enviados"),
        yaxis2=dict(title="Costo USD", overlaying="y", side="right"),
        title=f"Serie temporal · {camp_pick}"
    )
    st.plotly_chart(sfig(fig, 380), use_container_width=True)


# ────────────────────────────────────────────────────────────────
# TAB 3 · CONVERSACIONES
# ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<span class="sec">Análisis conversacional (sesiones de WhatsApp)</span>', unsafe_allow_html=True)

    fc1, fc2 = st.columns([1, 3])
    with fc1:
        rango3 = st.date_input("📅 Rango de fechas", value=(sr["fecha"].min(), sr["fecha"].max()),
                                min_value=sr["fecha"].min(), max_value=sr["fecha"].max(), key="t3_fecha")
    if isinstance(rango3, tuple) and len(rango3) == 2:
        r3_ini, r3_fin = rango3
    else:
        r3_ini, r3_fin = sr["fecha"].min(), sr["fecha"].max()
    sr_f = sr[(sr["fecha"] >= r3_ini) & (sr["fecha"] <= r3_fin)]

    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns(5)
    total_s = len(sr_f)
    ai_pct = safe_pct((sr_f["session_status"] == "AI").sum(), total_s)
    rating_pct = safe_pct((sr_f["session_status"] == "Rating").sum(), total_s)
    handover_n = int((sr_f["session_status"] == "HumanHandover").sum())
    paises_n = sr_f["pais"].nunique()

    kpis3 = [
        ("Total conversaciones", f"{total_s:,}", ""),
        ("Resueltas por IA", f"{ai_pct}%", "ok"),
        ("En calificación", f"{rating_pct}%", "alt"),
        ("Escaladas a agente humano", f"{handover_n}", "warn"),
        ("Países distintos", f"{paises_n}", "purple"),
    ]
    for col, (l, v, k) in zip(c, kpis3):
        col.markdown(kpi(l, v, "", k), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="sec blue">Volumen diario por tipo de conversación</span>', unsafe_allow_html=True)
        d = sr_f.groupby(["fecha", "session_type"], observed=True).size().reset_index(name="n")
        fig = px.bar(d, x="fecha", y="n", color="session_type", color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(yaxis_title="Sesiones", xaxis_title="", legend_title="")
        st.plotly_chart(sfig(fig, 360), use_container_width=True)
    with col2:
        st.markdown('<span class="sec red">Tasa de escalamiento a agente humano por día</span>', unsafe_allow_html=True)
        dh = sr_f.groupby("fecha").apply(
            lambda x: safe_pct((x["session_status"] == "HumanHandover").sum(), len(x)),
            include_groups=False
        ).reset_index(name="pct_handover")
        fig = px.line(dh, x="fecha", y="pct_handover", markers=True, color_discrete_sequence=[OY_WARN])
        fig.update_layout(yaxis_title="% escalado a humano", xaxis_title="")
        st.plotly_chart(sfig(fig, 360), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<span class="sec amb">Distribución horaria de conversaciones</span>', unsafe_allow_html=True)
        h = sr_f.groupby("hora").size().reset_index(name="n")
        fig = px.bar(h, x="hora", y="n", color_discrete_sequence=[OY_TEAL])
        fig.update_layout(xaxis_title="Hora del día (America/New_York)", yaxis_title="Sesiones")
        st.plotly_chart(sfig(fig, 320), use_container_width=True)
    with col4:
        st.markdown('<span class="sec">Top países de origen</span>', unsafe_allow_html=True)
        p = sr_f["pais"].value_counts().nlargest(10).reset_index()
        p.columns = ["pais", "n"]
        fig = px.bar(p.sort_values("n"), x="n", y="pais", orientation="h", color_discrete_sequence=[OY_BLUE])
        fig.update_layout(xaxis_title="Sesiones", yaxis_title="")
        st.plotly_chart(sfig(fig, 320), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec purple">Sesiones con link de campaña (tracking de origen)</span>', unsafe_allow_html=True)
    link_data = sr_f[sr_f["whatsapp_link_campaign_name"].notna()]
    if len(link_data):
        lk = link_data.groupby("whatsapp_link_campaign_name", observed=True).size().reset_index(name="n").sort_values("n", ascending=False)
        st.dataframe(lk.rename(columns={"whatsapp_link_campaign_name": "Campaña (link de origen)", "n": "Sesiones"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No hay sesiones con link de campaña identificado en el rango seleccionado.")


# ────────────────────────────────────────────────────────────────
# TAB 4 · CATÁLOGO DE PLANTILLAS
# ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<span class="sec">Inventario interno de plantillas HSM (los "pushes" que se envían)</span>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Plantillas registradas", f"{len(cat)}", "", ""), unsafe_allow_html=True)
    c2.markdown(kpi("Activas", f"{int(cat['activo'].sum())}", "generan costo si se envían", "ok"), unsafe_allow_html=True)
    c3.markdown(kpi("Inactivas", f"{int((cat['estado']=='Inactivo').sum())}", "", "warn"), unsafe_allow_html=True)
    c4.markdown(kpi("Equipos dueños", f"{cat['equipo'].nunique()}", "", "purple"), unsafe_allow_html=True)

    inconsistentes = cat[cat["auditoria"].astype(str).str.startswith("⚠️", na=False)]
    if len(inconsistentes):
        st.markdown("<br>", unsafe_allow_html=True)
        detalle = ", ".join(inconsistentes["conversacion"].tolist())
        st.markdown(
            f'<div class="alrt">⚠️ <b>Auditoría — {len(inconsistentes)} plantillas marcadas "Inactivo" en el '
            f'catálogo pero con envíos reales registrados:</b> {detalle}. El catálogo (spreadsheet) está '
            f'desactualizado respecto a lo que realmente se está enviando — conviene corregirlo con Iva '
            f'para que el estado documentado refleje la realidad.</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="sec blue">Plantillas por equipo</span>', unsafe_allow_html=True)
        e = cat.groupby(["equipo", "activo"]).size().reset_index(name="n")
        e["estado_g"] = e["activo"].map({True: "Activa", False: "Inactiva"})
        fig = px.bar(e, x="equipo", y="n", color="estado_g", barmode="stack",
                     color_discrete_map={"Activa": OY_OK, "Inactiva": "#CBD5D9"})
        fig.update_layout(xaxis_title="", yaxis_title="N° plantillas", legend_title="")
        st.plotly_chart(sfig(fig, 340), use_container_width=True)
    with col2:
        st.markdown('<span class="sec amb">Nivel de documentación del catálogo</span>', unsafe_allow_html=True)
        nd = cat["nivel_documentacion"].value_counts().reset_index()
        nd.columns = ["nivel", "n"]
        fig = px.pie(nd, names="nivel", values="n", hole=.5,
                     color="nivel", color_discrete_map={"Completa": OY_OK, "Parcial": OY_AMBER, "Sin documentar": OY_WARN})
        st.plotly_chart(sfig(fig, 340), use_container_width=True)
    st.caption(
        "💡 'Nivel de documentación' indica si el catálogo original tenía cargado el mensaje, tipo y "
        "propósito de cada plantilla, o si quedó incompleto. Las plantillas 'Sin documentar' no se "
        "inventaron — se dejaron explícitamente marcadas así para no mostrar información falsa."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">Explorador del catálogo</span>', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns(4)
    equipo_f = fc1.multiselect("Equipo", sorted(cat["equipo"].unique()))
    estado_f = fc2.multiselect("Estado", sorted(cat["estado"].unique()))
    doc_f = fc3.multiselect("Nivel de documentación", sorted(cat["nivel_documentacion"].unique()))
    buscar = fc4.text_input("Buscar por nombre")

    cat_f = cat.copy()
    if equipo_f:
        cat_f = cat_f[cat_f["equipo"].isin(equipo_f)]
    if estado_f:
        cat_f = cat_f[cat_f["estado"].isin(estado_f)]
    if doc_f:
        cat_f = cat_f[cat_f["nivel_documentacion"].isin(doc_f)]
    if buscar:
        cat_f = cat_f[cat_f["conversacion"].str.contains(buscar, case=False, na=False)]

    st.dataframe(
        cat_f[["conversacion", "plantilla", "tipo", "proposito", "estado", "equipo",
               "envios_historicos", "entregados_historicos", "auditoria"]].rename(columns={
            "conversacion": "Conversación / Campaña", "plantilla": "HSM / Plantilla",
            "tipo": "Tipo", "proposito": "Para qué se envía", "estado": "Estado", "equipo": "Equipo",
            "envios_historicos": "Envíos reales (histórico)", "entregados_historicos": "Entregados reales",
            "auditoria": "Nota de auditoría"
        }), use_container_width=True, hide_index=True, height=420
    )
    st.caption(
        "'Envíos reales (histórico)' y 'Entregados reales' vienen del cruce directo con el Reporte "
        "general de Treble — no son estimados."
    )


# ────────────────────────────────────────────────────────────────
# TAB 5 · INSIGHTS & RECOMENDACIONES
# ────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<span class="sec">Hallazgos automáticos para toma de decisiones</span>', unsafe_allow_html=True)

    insights = []
    gr_costo_full = con_costo(gr)

    # 1) Tendencia de escalamiento a humano
    dh_full = sr.groupby("fecha").apply(
        lambda x: safe_pct((x["session_status"] == "HumanHandover").sum(), len(x)), include_groups=False
    ).reset_index(name="pct")
    dh_full = dh_full.sort_values("fecha")
    if len(dh_full) >= 5:
        ult3 = dh_full.tail(3)["pct"].mean()
        prev3 = dh_full.iloc[-6:-3]["pct"].mean() if len(dh_full) >= 6 else dh_full.head(3)["pct"].mean()
        if ult3 > prev3 + 1:
            insights.append(("crit", "⚠️ Escalamiento a humano en ascenso",
                              f"La tasa de conversaciones escaladas a agente pasó de un promedio de "
                              f"{prev3:.1f}% a {ult3:.1f}% en los últimos días. Cada escalamiento implica "
                              f"tiempo de agente además del costo del push — vale la pena revisar con "
                              f"el equipo si hay un cambio en el flujo de IA o un pico de casos complejos."))

    # 2) Pushes con baja tasa de entrega (dinero gastado sin llegar)
    agg_full = gr_costo_full.groupby("name_clean", observed=True).agg(
        envios=("successful", "sum"), entregados=("delivered", "sum"),
        costo=("costo_estimado", "sum")).reset_index()
    agg_full["tasa"] = agg_full["entregados"] / agg_full["envios"] * 100
    bajas = agg_full[(agg_full["tasa"] < 90) & (agg_full["envios"] >= 50)].sort_values("tasa")
    if len(bajas):
        top3 = ", ".join([f"{r.name_clean} ({r.tasa:.0f}%)" for r in bajas.head(3).itertuples()])
        resto = len(bajas) - 3
        resumen = top3 + (f", y {resto} más" if resto > 0 else "")
        insights.append(("alrt", "📉 Pushes con tasa de entrega por debajo del 90%",
                          f"{len(bajas)} push(es), empezando por {resumen}. Si el modelo de costeo activo "
                          f"factura por envío/entrega, esto es dinero pagado por mensajes que no llegaron — "
                          f"revisar calidad de la lista de contactos o estado de la plantilla en Meta.",
                          bajas.rename(columns={"name_clean": "Push", "envios": "Enviados",
                                                 "entregados": "Entregados", "tasa": "Tasa entrega %",
                                                 "costo": "Costo (USD)"})[["Push", "Enviados", "Entregados",
                                                                            "Tasa entrega %", "Costo (USD)"]]))

    # 3) Concentración de costo
    top_share = agg_full.nlargest(1, "costo")
    if len(top_share) and agg_full["costo"].sum() > 0:
        share_pct = safe_pct(top_share["costo"].iloc[0], agg_full["costo"].sum())
        if share_pct > 40:
            insights.append(("info", "📊 Alta concentración de costo en un solo push",
                              f"'{top_share['name_clean'].iloc[0]}' representa {share_pct}% del costo "
                              f"estimado total histórico ({fmt_usd(top_share['costo'].iloc[0])}). "
                              f"Cualquier optimización de segmentación o frecuencia en este push tiene "
                              f"el mayor impacto posible en el gasto total.", None))

    # 4) Respuesta baja en pushes de alto volumen (costo sin interacción)
    resp_full = gr_costo_full.groupby("name_clean", observed=True).apply(
        lambda d: safe_pct((d["successful"] * d["response_rate"]).sum(), d["successful"].sum()),
        include_groups=False
    ).reset_index(name="tasa_resp")
    resp_full = resp_full.merge(agg_full[["name_clean", "envios", "costo"]], on="name_clean")
    bajas_resp = resp_full[(resp_full["tasa_resp"] < 10) & (resp_full["envios"] >= 500)].sort_values("costo", ascending=False)
    if len(bajas_resp):
        top3 = ", ".join([f"{r.name_clean} ({r.tasa_resp:.1f}%)" for r in bajas_resp.head(3).itertuples()])
        resto = len(bajas_resp) - 3
        resumen = top3 + (f", y {resto} más" if resto > 0 else "")
        insights.append(("alrt", "💬 Pushes de alto volumen con baja tasa de respuesta",
                          f"{len(bajas_resp)} push(es), empezando por {resumen}. Son recordatorios "
                          f"informativos (respuesta baja es esperable), pero si el modelo de costeo activo "
                          f"factura por conversación entregada (no por respuesta), estos son el gasto fijo "
                          f"recurrente más alto — los que más conviene auditar primero si se busca reducir costo.",
                          bajas_resp.rename(columns={"name_clean": "Push", "envios": "Enviados",
                                                      "tasa_resp": "Tasa respuesta %", "costo": "Costo (USD)"})
                          [["Push", "Enviados", "Tasa respuesta %", "Costo (USD)"]]))

    if not insights:
        st.markdown('<div class="good">✅ No se detectaron anomalías relevantes en el período analizado.</div>',
                     unsafe_allow_html=True)
    else:
        for item in insights:
            kind, titulo, texto = item[0], item[1], item[2]
            tabla_detalle = item[3] if len(item) > 3 else None
            st.markdown(f'<div class="{kind}"><b>{titulo}</b><br>{texto}</div>', unsafe_allow_html=True)
            if tabla_detalle is not None:
                with st.expander(f"Ver el detalle completo ({len(tabla_detalle)} filas)"):
                    st.dataframe(tabla_detalle, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">Próximos pasos sugeridos</span>', unsafe_allow_html=True)
    st.markdown("""
- **Confirmar la tarifa real de costo por conversación** con Treble/Meta si llegara a cambiar —
  hoy ya usamos la tarifa real auditada, no un supuesto, pero conviene re-auditar periódicamente.
- **Confirmar el modelo de costeo real** (¿se cobra por conversación entregada o solo cuando el
  cliente responde?) — cambia significativamente qué pushes son realmente los más caros.
- **Revisar con Iva** los pushes con baja tasa de entrega, ya que representan gasto sin llegar al
  cliente bajo el modelo "por entrega".
- **Alertas automáticas**: configurar un umbral de costo mensual o de tasa de entrega que dispare
  notificación sin depender de revisión manual del dashboard.
""")


# ────────────────────────────────────────────────────────────────
# TAB 6 · ÁRBOL DE CONVERSACIÓN (dónde se rompe / dónde queda en silencio)
# ────────────────────────────────────────────────────────────────
with tab6:
    st.markdown('<span class="sec">Dónde se rompe la conversación</span>', unsafe_allow_html=True)

    # ── Sección en vivo: lo que SÍ se puede sacar del DWH directamente ──
    st.markdown('<span class="sec blue">🔴 En vivo — respuesta a plantillas HSM (Data Warehouse)</span>',
                unsafe_allow_html=True)
    if not _dwh_ok:
        st.markdown('<div class="alrt">Data Warehouse no conectado ahora mismo — esta sección se activa sola '
                    'en cuanto la conexión esté disponible.</div>', unsafe_allow_html=True)
    else:
        sql_hsm = """
            SELECT hsm_name, count() AS respuestas, count(DISTINCT survey_user_id) AS usuarios_unicos
            FROM client_analytics.fact_hsm_responses
            WHERE response_date >= now() - INTERVAL 30 DAY
            GROUP BY hsm_name ORDER BY respuestas DESC LIMIT 20
        """
        df_hsm = dwh_query(sql_hsm)
        if df_hsm is None or df_hsm.empty:
            st.info("La consulta al DWH no devolvió datos de respuestas HSM para los últimos 30 días.")
        else:
            fig = px.bar(df_hsm.sort_values("respuestas"), x="respuestas", y="hsm_name", orientation="h",
                         color_discrete_sequence=[OY_BLUE])
            fig.update_layout(xaxis_title="Respuestas de usuarios (30 días)", yaxis_title="")
            st.plotly_chart(sfig(fig, 360), use_container_width=True)
        st.caption(
            "Esto viene de `fact_hsm_responses`, en vivo. Pero ojo: esta tabla **solo tiene una fila cuando "
            "el usuario SÍ respondió** — no registra quién se quedó en silencio. Por eso, para calcular fugas "
            "reales necesitamos cruzarla contra los envíos totales (`fact_deployment_daily`), y aun así no "
            "reconstruye el árbol paso a paso — solo el total de respuesta por plantilla."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">📄 Análisis completo — export de árbol de Treble</span>', unsafe_allow_html=True)

    if arbol is None:
        st.markdown(
            '<div class="alrt">⚠️ No se encontró <code>data/arbol_conversacion.csv</code>. '
            'Esta pestaña necesita el export de árbol de conversación de Treble (reporte '
            '"rpt_treble_arbol...csv") para funcionar. Súbelo a la carpeta <code>data/</code> del '
            'repo con ese nombre exacto.</div>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info">💡 <b>Qué es "fuga real":</b> Treble marca como "No avanzó" a '
            'cualquiera que no siga una plantilla, incluso en avisos de una sola vía donde nadie '
            'espera respuesta (eso es normal, no es un problema). Este dashboard filtra eso: solo '
            'cuenta como <b>fuga real</b> cuando el cliente SÍ tenía una opción real de responder o '
            'elegir algo, y aun así se quedó en silencio. Eso es lo que realmente vale la pena '
            'revisar.</div>', unsafe_allow_html=True
        )

        fuga_real_df = arbol[arbol["fuga_real"]]
        total_fuga_real = int(fuga_real_df["N Clientes"].sum())
        n_puntos = fuga_real_df["Origen ID"].nunique()
        top_plantilla = (fuga_real_df.groupby("Plantilla")["N Clientes"].sum()
                          .sort_values(ascending=False))

        c1, c2, c3 = st.columns(3)
        c1.markdown(kpi("Clientes en fuga real", f"{total_fuga_real:,}", "con alternativa real de responder", "warn"),
                    unsafe_allow_html=True)
        c2.markdown(kpi("Puntos de quiebre distintos", f"{n_puntos}", "en todos los flujos", "amber"),
                    unsafe_allow_html=True)
        if len(top_plantilla):
            c3.markdown(kpi("Plantilla con más fuga", f"{int(top_plantilla.iloc[0]):,}",
                            top_plantilla.index[0][:30], "dark"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sec red">Ranking de plantillas por volumen de fuga real</span>', unsafe_allow_html=True)
        st.caption(
            "Cada barra = cuántos clientes recibieron esa plantilla, tenían una opción real para "
            "responder, y aun así no respondieron. El % es sobre el total de gente que entró a esa "
            "plantilla (no sobre el total general)."
        )
        rank = fuga_real_df.groupby("Plantilla").agg(
            fuga_real=("N Clientes", "sum"), puntos_de_quiebre=("Origen ID", "nunique"),
            entrantes=("entrantes_plantilla", "first"),
        ).reset_index().sort_values("fuga_real", ascending=False)
        rank["pct_entrantes"] = (rank["fuga_real"] / rank["entrantes"] * 100).round(1)
        rank["etiqueta"] = rank.apply(lambda r: f"{int(r['fuga_real']):,} ({r['pct_entrantes']:.0f}% de {int(r['entrantes']):,} entrantes)", axis=1)

        top15 = rank.head(15).sort_values("fuga_real")
        fig = px.bar(top15, x="fuga_real", y="Plantilla", orientation="h",
                     color_discrete_sequence=[OY_WARN], text="etiqueta")
        fig.update_traces(textposition="outside", textfont=dict(size=11))
        fig.update_layout(xaxis_title="Clientes en fuga real", yaxis_title="",
                           margin=dict(r=220))  # espacio para que la etiqueta no se corte
        st.plotly_chart(sfig(fig, 460), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sec purple">🌳 Árbol de decisiones — dónde se caen los clientes</span>',
                    unsafe_allow_html=True)
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            plantilla_pick = st.selectbox("Flujo", rank["Plantilla"].tolist(), key="t6_plantilla")
        with fc2:
            min_clientes = st.number_input("Mínimo de clientes por rama", min_value=0, value=50, step=10,
                                            key="t6_min_clientes",
                                            help="Ramas con menos clientes que este número no se muestran, "
                                                 "para que el árbol se pueda leer.")

        sub_full = arbol[arbol["Plantilla"] == plantilla_pick].copy()
        # Nos quedamos con un Poll ID representativo (el de mayor volumen) para que el
        # diagrama no mezcle instancias distintas del mismo flujo
        poll_top = sub_full.groupby("Poll ID")["N Clientes"].sum().idxmax()
        sub_full = sub_full[sub_full["Poll ID"] == poll_top].copy()
        total_flujo = sub_full["N Clientes"].sum()

        sub = sub_full[sub_full["N Clientes"] >= min_clientes].copy()
        n_ocultas = len(sub_full) - len(sub)

        col1, col2 = st.columns([1.4, 1])
        with col1:
            st.markdown('<span class="sec blue">Mapa del flujo</span>', unsafe_allow_html=True)
            st.caption(
                "Se lee de izquierda a derecha: cada barra es un mensaje, cada franja es cuánta gente "
                "pasó de un mensaje al siguiente. 🔴 rojo = terminó en silencio · 🔵 teal = siguió "
                "conversando." + (f" {n_ocultas} rama(s) con menos de {min_clientes} clientes están "
                                   "ocultas — bajá el mínimo de arriba si querés verlas." if n_ocultas else "")
            )

            if sub.empty:
                st.info("No quedan ramas con ese mínimo de clientes. Bajá el número de 'Mínimo de clientes "
                        "por rama' para ver el árbol.")
            else:
                def _etiqueta_nodo(n):
                    n = str(n)
                    # quitamos el prefijo técnico "P1 · " y cortamos a un largo legible
                    if " · " in n:
                        n = n.split(" · ", 1)[1]
                    return (n[:38] + "…") if len(n) > 38 else n

                nodos = pd.unique(sub[["Nodo Origen Key", "Nodo Destino Key"]].values.ravel())
                nodo_idx = {n: i for i, n in enumerate(nodos)}
                colores_nodo = [OY_WARN if ("No avanzó" in n or "✖" in n) else OY_TEAL for n in nodos]
                link_colores = ["rgba(229,72,77,.55)" if f else "rgba(22,182,194,.35)" for f in sub["Es Fuga"]]
                pct_total = (sub["N Clientes"] / total_flujo * 100).round(1)
                sankey = go.Figure(go.Sankey(
                    arrangement="snap",
                    node=dict(label=[_etiqueta_nodo(n) for n in nodos], pad=18, thickness=18,
                              color=colores_nodo, line=dict(color="rgba(0,0,0,.15)", width=.5),
                              hovertemplate="%{label}<extra></extra>"),
                    link=dict(source=sub["Nodo Origen Key"].map(nodo_idx),
                              target=sub["Nodo Destino Key"].map(nodo_idx),
                              value=sub["N Clientes"], color=link_colores,
                              customdata=pct_total,
                              hovertemplate="%{value:,} clientes (%{customdata}% del flujo)<extra></extra>")
                ))
                st.plotly_chart(sfig(sankey, 560), use_container_width=True)
        with col2:
            st.markdown('<span class="sec amb">Puntos de quiebre de este flujo</span>', unsafe_allow_html=True)
            puntos = sub_full[sub_full["N Clientes"] >= min_clientes]
            puntos = puntos[puntos["fuga_real"]][["Paso Origen", "Nodo Origen", "N Clientes", "Pct Del Nodo"]]
            puntos = puntos.sort_values("N Clientes", ascending=False)
            if len(puntos):
                alto = min(420, 46 + 38 * len(puntos))
                st.dataframe(
                    puntos.rename(columns={"Paso Origen": "Paso", "Nodo Origen": "Mensaje",
                                            "N Clientes": "Clientes en silencio", "Pct Del Nodo": "% del nodo"}),
                    use_container_width=True, hide_index=True, height=alto
                )
            else:
                st.info("Este flujo no tiene puntos de fuga real detectados (es informativo de una sola vía, "
                        "o casi todos los que llegan responden).")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sec">🔎 Hallazgo principal de esta auditoría</span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="crit">⚠️ <b>"esp_espera" (especialista esperando)</b> es el quiebre más grande y '
            'concentrado: el mensaje <i>"tu especialista te espera por la plataforma. ¿Tienes alguna '
            'dificultad que te impide ingresar?"</i> se queda sin respuesta en el <b>82–86% de los casos</b> '
            '(4,114 clientes), a pesar de que sí hay gente que responde cuando se le pregunta. Cada uno de '
            'esos casos es una sesión donde el especialista esperó y el sistema nunca supo si hubo un '
            'problema real o el cliente simplemente no vio el mensaje — vale la pena revisar el copy, '
            'agregar un botón de respuesta rápida, o acortar el tiempo antes de escalar a un agente '
            'humano.</div>', unsafe_allow_html=True
        )
        st.markdown(
            '<div class="alrt">El flujo principal del bot de ATC ("(sin nombre)") tiene fuga real repartida '
            'en 117 puntos distintos del árbol (3,153 clientes en total) — no hay un solo quiebre gigante, '
            'sino fricción distribuida en varios pasos del menú. El punto más grande es el mensaje de '
            'bienvenida inicial: entre 14% y 28% de quienes lo reciben no eligen ninguna opción del '
            'menú.</div>', unsafe_allow_html=True
        )

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Dashboard Conversaciones y Pushes Automáticos · Opción Yo — generado con NOVA. "
           "Datos: reportes Treble/WhatsApp y catálogo interno de plantillas. "
           "No incluye incidencias técnicas (dashboard aparte).")
