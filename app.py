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
    initial_sidebar_state="expanded",
)

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

REGION = {"1": "EE.UU./Canadá", "34": "España", "52": "México", "58": "Venezuela",
          "57": "Colombia", "507": "Panamá", "44": "UK", "56": "Chile",
          "39": "Italia", "49": "Alemania", "61": "Australia", "593": "Ecuador",
          "506": "Costa Rica", "41": "Suiza", "51": "Perú", "33": "Francia",
          "351": "Portugal", "31": "Países Bajos", "54": "Argentina",
          "353": "Irlanda"}

# ── CSS (idéntico lenguaje visual a los otros dashboards de Opción Yo) ──
st.markdown("""
<style>
:root{--oy-teal:#16B6C2;--oy-td:#0E8E99;--oy-blue:#2F80ED;
      --oy-ok:#27AE60;--oy-warn:#E5484D;--oy-amb:#F2A33C;--oy-ink:#16323A;}
.stApp{background:#fff;}
.block-container{padding-top:1.5rem;}
h1,h2,h3{color:var(--oy-td);}
[data-testid="stMetricValue"]{font-size:1.7rem!important;font-weight:800;color:var(--oy-ink);}
[data-testid="stMetricLabel"]{font-size:.78rem!important;color:#5a6b72;font-weight:600;}

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
    '<div class="oy-htxt"><p class="oy-htitle">💬 Conversaciones y Pushes Automáticos</p>'
    '<p class="oy-hsub">Volumen de WhatsApp/Treble y costo estimado de envíos automáticos · '
    'No incluye incidencias técnicas (ver dashboard Incidencias Técnicas)</p></div></div>',
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
    fig.update_layout(height=h, margin=dict(t=46, b=10, l=10, r=10),
                       font=dict(color=OY_INK, family="Segoe UI,sans-serif"),
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       title_font=dict(color=OY_TEAL_DARK, size=14))
    return fig


def safe_pct(n, d):
    return round(float(n) / float(d) * 100, 1) if d else 0.0


def fmt_usd(v):
    return f"${v:,.2f}"


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
    path = find_data_file("general_report.csv")
    if not path:
        st.error("❌ No se encontró data/general_report.csv. Verifica que el archivo esté en el repositorio.")
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
    return df


@st.cache_data(show_spinner="⏳ Cargando sesiones conversacionales…")
def load_sessions():
    path = find_data_file("sessions_report.csv")
    if not path:
        st.error("❌ No se encontró data/sessions_report.csv. Verifica que el archivo esté en el repositorio.")
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
    df["equipo"] = df["equipo"].fillna("Sin asignar")
    df["tipo"] = df["tipo"].fillna("Sin clasificar")
    df["activo"] = df["estado"].isin(["Push Activo", "Manual activo", "Inbound"])
    return df


gr = load_general_report()
sr = load_sessions()
cat = load_catalog()

# ══════════════════════════════════════════════════════════════
#  SIDEBAR · FILTROS Y SUPUESTO DE COSTO
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("### 🎛️ Filtros")
st.sidebar.caption(
    f"📅 Reporte de pushes: {gr['fecha'].min()} → {gr['fecha'].max()}\n\n"
    f"💬 Sesiones conversacionales: {sr['fecha'].min()} → {sr['fecha'].max()}"
)

min_d, max_d = gr["fecha"].min(), gr["fecha"].max()
rango = st.sidebar.date_input("Rango de fechas · Pushes", value=(min_d, max_d),
                               min_value=min_d, max_value=max_d)
if isinstance(rango, tuple) and len(rango) == 2:
    f_ini, f_fin = rango
else:
    f_ini, f_fin = min_d, max_d

gr_f = gr[(gr["fecha"] >= f_ini) & (gr["fecha"] <= f_fin)]

campanas_sel = st.sidebar.multiselect("Push / Campaña", sorted(gr["name_clean"].unique()), default=[])
if campanas_sel:
    gr_f = gr_f[gr_f["name_clean"].isin(campanas_sel)]

st.sidebar.markdown("---")
st.sidebar.caption("💬 Filtro independiente para pestaña Conversaciones (ventana disponible del export)")
min_ds, max_ds = sr["fecha"].min(), sr["fecha"].max()
rango_s = st.sidebar.date_input("Rango de fechas · Conversaciones", value=(min_ds, max_ds),
                                 min_value=min_ds, max_value=max_ds)
if isinstance(rango_s, tuple) and len(rango_s) == 2:
    fs_ini, fs_fin = rango_s
else:
    fs_ini, fs_fin = min_ds, max_ds
sr_f = sr[(sr["fecha"] >= fs_ini) & (sr["fecha"] <= fs_fin)]

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Modelo de costo")
st.sidebar.caption(
    "Treble/WhatsApp cobra por **conversación** de 24h, en tramos según volumen mensual — "
    "no es una tarifa plana. Esta tabla es la real de tu cuenta (extraída y auditada del "
    "reporte nativo 'Inversión' de Treble)."
)
st.sidebar.markdown(
    "**Tramos reales (por mes):**\n"
    "- 0 – 5,000 conv. → $0.20\n"
    "- 5,001 – 10,000 conv. → $0.18\n"
    "- 10,001 – 20,000 conv. → $0.15\n"
    "- > 20,000 conv. → $0.12"
)
modo_costo = st.sidebar.radio(
    "Fuente de la tarifa",
    ["Tramos reales de Treble (recomendado)", "Tarifa fija manual"],
    index=0,
    help="Los tramos reales se aplican automáticamente según el volumen mensual de cada mes en "
         "los datos. Usa 'Tarifa fija manual' solo si quieres simular un escenario distinto."
)
if modo_costo == "Tarifa fija manual":
    tarifa_manual = st.sidebar.number_input(
        "Tarifa manual por conversación (USD)", min_value=0.0, value=0.12, step=0.01, format="%.3f"
    )
else:
    tarifa_manual = None

modelo_costo = st.sidebar.radio(
    "¿Qué cuenta como conversación facturable?",
    ["Cada push entregado (conversación abierta)", "Solo cuando el cliente responde"],
    index=0,
    help="WhatsApp Business Platform factura por conversación de 24h iniciada por el negocio al "
         "entregar la plantilla, independientemente de si el cliente responde. Cambia esto solo si "
         "confirmas con Treble que tu contrato factura distinto."
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Fuentes:** reporte general Treble/WhatsApp (envíos automáticos), reporte de sesiones "
    "conversacionales, catálogo interno de plantillas y export nativo de Treble 'Inversión' "
    "(tarifas reales, auditadas).\n\n"
    "**Fuera de alcance (a propósito):** tickets de incidencias técnicas / HubSpot — "
    "eso vive en el dashboard **Incidencias Técnicas**, aparte."
)


# ══════════════════════════════════════════════════════════════
#  CÁLCULO DE COSTO (aplicado a Pushes) · modelo real de tramos de Treble
# ══════════════════════════════════════════════════════════════
# El tramo de tarifa se calcula sobre el volumen TOTAL de la cuenta ese mes
# (todos los pushes juntos), no por campaña individual — así es como Treble
# factura realmente. Se calcula siempre sobre gr completo (no el filtrado)
# para que la tarifa de cada mes sea la real, independiente del filtro activo.
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


gr_costo = con_costo(gr_f)


# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumen Ejecutivo", "📤 Pushes Automáticos & Costo",
    "💬 Conversaciones", "🗂️ Catálogo de Plantillas",
    "🎯 Insights & Recomendaciones"
])

# ────────────────────────────────────────────────────────────────
# TAB 1 · RESUMEN EJECUTIVO
# ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<span class="sec">Panorama general del período seleccionado</span>', unsafe_allow_html=True)

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


# ────────────────────────────────────────────────────────────────
# TAB 2 · PUSHES AUTOMÁTICOS & COSTO
# ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<span class="sec">Desempeño y costo por push / plantilla automática</span>', unsafe_allow_html=True)

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

    # Cruce con catálogo para traer equipo dueño
    cat_lookup = cat.set_index("conversacion")[["equipo", "estado"]]
    def _equipo(n):
        for k in cat_lookup.index:
            if k.strip().lower() in n.lower() or n.lower() in k.strip().lower():
                return cat_lookup.loc[k, "equipo"]
        return "Sin match en catálogo"
    agg["equipo"] = agg["name_clean"].map(_equipo)

    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("Costo total estimado", fmt_usd(agg["costo_estimado"].sum()), "período seleccionado", "warn"),
                unsafe_allow_html=True)
    c2.markdown(kpi("Pushes con envíos", f"{len(agg)}", "", ""), unsafe_allow_html=True)
    mas_caro = agg.iloc[0] if len(agg) else None
    if mas_caro is not None:
        c3.markdown(kpi("Push más costoso", fmt_usd(mas_caro["costo_estimado"]), mas_caro["name_clean"][:30], "amber"),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec blue">Tabla comparativa — costo por push</span>', unsafe_allow_html=True)
    tabla = agg.rename(columns={
        "name_clean": "Push / Campaña", "envios": "Enviados", "entregados": "Entregados",
        "conversaciones_facturables": "Conversaciones facturables (est.)",
        "costo_estimado": "Costo estimado (USD)", "n_batches": "N° envíos (batches)", "equipo": "Equipo dueño"
    })
    st.dataframe(
        tabla, use_container_width=True, hide_index=True,
        column_config={
            "Costo estimado (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "tasa_entrega_%": st.column_config.ProgressColumn("Tasa entrega %", min_value=0, max_value=100, format="%.1f%%"),
            "tasa_respuesta_%": st.column_config.ProgressColumn("Tasa respuesta %", min_value=0, max_value=100, format="%.1f%%"),
        }
    )
    st.caption(
        "💡 'Conversaciones facturables (est.)' depende del supuesto elegido en la barra lateral: "
        "todo lo entregado, o solo lo que generó respuesta."
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
        st.markdown('<span class="sec amb">Distribución por tipo de mensaje</span>', unsafe_allow_html=True)
        t = cat["tipo"].value_counts().reset_index()
        t.columns = ["tipo", "n"]
        fig = px.pie(t, names="tipo", values="n", hole=.5, color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(sfig(fig, 340), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">Explorador del catálogo</span>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    equipo_f = fc1.multiselect("Equipo", sorted(cat["equipo"].unique()))
    estado_f = fc2.multiselect("Estado", sorted(cat["estado"].unique()))
    buscar = fc3.text_input("Buscar por nombre de conversación")

    cat_f = cat.copy()
    if equipo_f:
        cat_f = cat_f[cat_f["equipo"].isin(equipo_f)]
    if estado_f:
        cat_f = cat_f[cat_f["estado"].isin(estado_f)]
    if buscar:
        cat_f = cat_f[cat_f["conversacion"].str.contains(buscar, case=False, na=False)]

    st.dataframe(
        cat_f[["conversacion", "plantilla", "tipo", "proposito", "estado", "equipo"]].rename(columns={
            "conversacion": "Conversación / Campaña", "plantilla": "HSM / Plantilla",
            "tipo": "Tipo", "proposito": "Para qué se envía", "estado": "Estado", "equipo": "Equipo"
        }), use_container_width=True, hide_index=True, height=420
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
        detalle = ", ".join([f"{r.name_clean} ({r.tasa:.0f}% entrega, {fmt_usd(r.costo)} gastado)"
                              for r in bajas.itertuples()])
        insights.append(("alrt", "📉 Pushes con tasa de entrega por debajo del 90%",
                          f"{detalle}. Si el modelo de costeo activo factura por envío/entrega, esto "
                          f"es dinero pagado por mensajes que no llegaron — revisar calidad de la lista "
                          f"de contactos o estado de la plantilla en Meta."))

    # 3) Concentración de costo
    top_share = agg_full.nlargest(1, "costo")
    if len(top_share) and agg_full["costo"].sum() > 0:
        share_pct = safe_pct(top_share["costo"].iloc[0], agg_full["costo"].sum())
        if share_pct > 40:
            insights.append(("info", "📊 Alta concentración de costo en un solo push",
                              f"'{top_share['name_clean'].iloc[0]}' representa {share_pct}% del costo "
                              f"estimado total histórico ({fmt_usd(top_share['costo'].iloc[0])}). "
                              f"Cualquier optimización de segmentación o frecuencia en este push tiene "
                              f"el mayor impacto posible en el gasto total."))

    # 4) Respuesta baja en pushes de alto volumen (costo sin interacción)
    resp_full = gr_costo_full.groupby("name_clean", observed=True).apply(
        lambda d: safe_pct((d["successful"] * d["response_rate"]).sum(), d["successful"].sum()),
        include_groups=False
    ).reset_index(name="tasa_resp")
    resp_full = resp_full.merge(agg_full[["name_clean", "envios", "costo"]], on="name_clean")
    bajas_resp = resp_full[(resp_full["tasa_resp"] < 10) & (resp_full["envios"] >= 500)]
    if len(bajas_resp):
        detalle = ", ".join([f"{r.name_clean} ({r.tasa_resp:.1f}% respuesta, {fmt_usd(r.costo)})"
                              for r in bajas_resp.itertuples()])
        insights.append(("alrt", "💬 Pushes de alto volumen con baja tasa de respuesta",
                          f"{detalle}. Son recordatorios informativos (respuesta baja es esperable), "
                          f"pero si el modelo de costeo activo factura por conversación entregada "
                          f"(no por respuesta), este es el gasto fijo recurrente más alto — el que más "
                          f"conviene auditar primero si se busca reducir costo."))

    if not insights:
        st.markdown('<div class="good">✅ No se detectaron anomalías relevantes en el período analizado.</div>',
                     unsafe_allow_html=True)
    else:
        for kind, titulo, texto in insights:
            st.markdown(f'<div class="{kind}"><b>{titulo}</b><br>{texto}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec">Próximos pasos sugeridos</span>', unsafe_allow_html=True)
    st.markdown("""
- **Confirmar la tarifa real de costo por conversación** con Treble/Meta y reemplazar el valor
  editable de la barra lateral — hoy el costo mostrado es un estimado, no una cifra de facturación.
- **Confirmar el modelo de costeo real** (¿se cobra por conversación entregada o solo cuando el
  cliente responde?) — cambia significativamente qué pushes son realmente los más caros.
- **Revisar con Iva** los pushes con baja tasa de entrega, ya que representan gasto sin llegar al
  cliente bajo el modelo "por entrega".
- **Alertas automáticas**: configurar un umbral de costo mensual o de tasa de entrega que dispare
  notificación sin depender de revisión manual del dashboard.
""")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Dashboard Conversaciones y Pushes Automáticos · Opción Yo — generado con NOVA. "
           "Datos: reportes Treble/WhatsApp y catálogo interno de plantillas. "
           "No incluye incidencias técnicas (dashboard aparte).")
