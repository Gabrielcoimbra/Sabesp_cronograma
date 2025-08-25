# streamlit_app.py
import io
import os
import glob
import unicodedata
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import plotly.io as pio

# =========================
# Paleta 2Neuron (fixa)
# =========================
cores_2neuron = ['#6A0DAD', '#8A2BE2', '#9370DB', '#D8BFD8', '#4B0082']
COR_BG = "#F8F8FF"
COR_TXT = "#2D2D2D"
COR_PRI = cores_2neuron[0]
COR_SEC = cores_2neuron[1]
COR_ALERTA = "#E76F51"
GRID = "#E6E6F0"
ZERO = "#D0D0DF"
AXIS = "#B0B0C0"
BASE_FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"

pio.templates.default = None
st.set_page_config(page_title="Instalações 2Neuron | Sabesp", layout="wide")
st.markdown(
    f"""
    <style>
      :root {{ color-scheme: light; }}
      html, body, [data-testid="stAppViewContainer"] {{
        background: {COR_BG} !important;
        font-family: {BASE_FONT};
      }}
      .block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Utils
# =========================
BASE_LAYOUT = dict(
    paper_bgcolor=COR_BG,
    plot_bgcolor=COR_BG,
    font=dict(color=COR_TXT, size=14, family=BASE_FONT),
    margin=dict(l=50, r=20, t=60, b=60)
)

def axes_style(fig):
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=ZERO,
                   linecolor=AXIS, linewidth=1, mirror=True, ticks="outside"),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=ZERO,
                   linecolor=AXIS, linewidth=1, mirror=True, ticks="outside")
    )

def fig_to_png(fig, width=1100, height=420, scale=3):
    fig.update_layout(template=None)
    img = fig.to_image(format="png", width=width, height=height, scale=scale)  # requer kaleido
    return Image.open(io.BytesIO(img))

def show(fig, width=1100, height=420):
    try:
        st.image(fig_to_png(fig, width=width, height=height), use_container_width=True)
    except Exception:
        st.plotly_chart(fig, use_container_width=True, theme="none")

def table_png(df: pd.DataFrame, title: str, max_h_px: int = 760):
    df = df.astype(str)
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), fill_color="#FFFFFF",
                    line_color="#DDDDDD", align="left",
                    font=dict(color=COR_TXT, size=13, family=BASE_FONT), height=32),
        cells=dict(values=[df[c] for c in df.columns], fill_color="#FFFFFF",
                   line_color="#EEEEEE", align="left",
                   font=dict(color=COR_TXT, size=12, family=BASE_FONT), height=28)
    )])
    fig.update_layout(title=title, **BASE_LAYOUT)
    h = min(max_h_px, 120 + len(df) * 28)
    show(fig, width=1200, height=h)

# =========================
# Leitura da planilha (raiz do repo ou uploader)
# =========================
ALVO_BASE = "SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3)"

def normalizar_col(col: str) -> str:
    c = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode("ASCII")
    c = c.replace("\n", " ").replace("\r", " ")
    c = " ".join(c.split())
    return c.upper()

def localizar_arquivo_base():
    padrões = [f"./{ALVO_BASE}.*", f"./{ALVO_BASE}*.*"]
    candidatos = []
    for p in padrões:
        candidatos.extend(glob.glob(p))
    preferencia = [".xlsx", ".xls", ".csv", ".parquet"]
    if candidatos:
        candidatos.sort(key=lambda x: (preferencia.index(os.path.splitext(x)[1].lower())
                                       if os.path.splitext(x)[1].lower() in preferencia else 99))
        return candidatos[0]
    return None

def ler_planilha(caminho: str | None) -> pd.DataFrame:
    if caminho and os.path.exists(caminho):
        ext = os.path.splitext(caminho)[1].lower()
        if ext in [".xlsx", ".xls"]:
            return pd.read_excel(caminho)
        if ext == ".csv":
            try:
                return pd.read_csv(caminho, sep=";")
            except Exception:
                return pd.read_csv(caminho)
        if ext == ".parquet":
            return pd.read_parquet(caminho)
        return pd.read_excel(caminho)

    st.info("Arquivo não encontrado na raiz. Envie a planilha pelo uploader abaixo.")
    up = st.file_uploader("Envie o arquivo (xlsx/xls/csv/parquet)", type=["xlsx","xls","csv","parquet"])
    if up is None:
        st.stop()
    ext = os.path.splitext(up.name)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(up)
    if ext == ".csv":
        try:
            return pd.read_csv(up, sep=";")
        except Exception:
            return pd.read_csv(up)
    if ext == ".parquet":
        return pd.read_parquet(up)
    return pd.read_excel(up)

def preparar_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    m = {c: normalizar_col(c) for c in df_raw.columns}
    df = df_raw.rename(columns=m).copy()

    # Aliases mínimos para garantir as colunas principais solicitadas
    alias = {
        "LOCAL": ["LOCAL"],
        "CIDADE": ["CIDADE"],
        "MÓDULO": ["MODULO","SERIE","MÓDULO/ SÉRIE","SERIE/MODULO"],
        "GATEWAY": ["GATEWAY"],
        "DATA INSTALAÇÃO ULTRONLINE": ["DATA INSTALACAO ULTRONLINE","DATA INSTALACAO","DATA INSTALAÇÃO"],
        "DATA PLANEJADA": ["DATA PLANEJADA","DATA PREVISTA"]
    }

    # Mapear nomes canônicos
    canon = {}
    for alvo, opcoes in alias.items():
        for o in opcoes:
            if o in df.columns:
                canon[alvo] = o
                break

    # Garantir colunas mesmo se ausentes
    for k in alias.keys():
        if k not in canon:
            df[k] = pd.NA
            canon[k] = k

    # Renomear p/ canônico
    df = df.rename(columns={canon[k]: k for k in canon})

    # Tipos
    for dcol in ["DATA INSTALAÇÃO ULTRONLINE", "DATA PLANEJADA"]:
        df[dcol] = pd.to_datetime(df[dcol], errors="coerce")

    # Strings chave
    for scol in ["LOCAL","CIDADE","MÓDULO","GATEWAY"]:
        df[scol] = df[scol].astype(str).str.strip()

    # Status online simples (com base em gateway)
    df["ONLINE"] = True
    df.loc[df["GATEWAY"].str.lower().eq("sem gateway"), "ONLINE"] = False

    return df

# =========================
# Registros (somente texto/log – não afeta contagens)
# =========================
registros = [
    {"data":"2025-08-11","cidade":"São Paulo","local":"EEE Alvarenga Mãe",
     "obs":"U2N000283 (TC 35→24 mm), U2N000282 (com gateway), U2N000287, U2N000270."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"EEE Lavapés",
     "obs":"U2N000269 e U2N000288; conexões confirmadas."},
    # … mantenha/adapte livremente
]
df_reg = pd.DataFrame(registros)
if not df_reg.empty:
    df_reg["data"] = pd.to_datetime(df_reg["data"], errors="coerce")

# =========================
# Carregar & preparar
# =========================
caminho = localizar_arquivo_base()
df_raw = ler_planilha(caminho)
df = preparar_dataframe(df_raw)

# =========================
# MÉTRICAS (usando APENAS planilha)
# =========================
# 1) INSTALADO (real): conta MÓDULO distinto por DATA INSTALAÇÃO ULTRONLINE
instalado = (df.dropna(subset=["MÓDULO","DATA INSTALAÇÃO ULTRONLINE"])
               .groupby("DATA INSTALAÇÃO ULTRONLINE", as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA INSTALAÇÃO ULTRONLINE":"DATA","MÓDULO":"INSTALADOS_DIA"})
             )
instalado = instalado.sort_values("DATA")
instalado["ACUMULADO"] = instalado["INSTALADOS_DIA"].cumsum()
instalado["DATA_STR"] = instalado["DATA"].dt.strftime("%d/%m/%Y")

# 2) PLANEJADO (para visão futura, se quiser)
planejado = (df.dropna(subset=["MÓDULO","DATA PLANEJADA"])
               .groupby("DATA PLANEJADA", as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA PLANEJADA":"DATA","MÓDULO":"PLANEJADOS_DIA"})
            ).sort_values("DATA")
if not planejado.empty:
    planejado["ACUM_PLANEJADO"] = planejado["PLANEJADOS_DIA"].cumsum()
    planejado["DATA_STR"] = planejado["DATA"].dt.strftime("%d/%m/%Y")

# 3) Distribuição por cidade (módulos únicos)
by_city = (df.dropna(subset=["MÓDULO"])
             .groupby("CIDADE", as_index=False)["MÓDULO"]
             .nunique()
             .rename(columns={"MÓDULO":"QTD"}))

# 4) Online/Offline (baseado em gateway)
total_series = df["MÓDULO"].nunique(dropna=True)
total_online = int(df.dropna(subset=["MÓDULO"])["ONLINE"].sum())
total_offline = max(0, total_series - total_online)

# =========================
# Header + KPIs
# =========================
st.markdown(
    f"""
    <div style="color:{COR_TXT} !important;">
      <h1 style="margin:0 0 6px 0; font-size:44px; line-height:1.15; font-weight:800; color:{COR_TXT} !important;">
        Instalações 2Neuron na Sabesp
      </h1>
      <div style="opacity:.9; margin:0 0 18px 0; font-size:15px; color:{COR_TXT} !important;">
        Base: <b>{os.path.basename(caminho) if caminho else "upload manual"}</b> — módulos únicos: {total_series}
      </div>
      <div style="display:flex; gap:28px; flex-wrap:wrap;">
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px;">Instalados (reais)</div>
          <div style="font-size:36px; font-weight:700;">{int(instalado['INSTALADOS_DIA'].sum()) if not instalado.empty else 0}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px;">Online</div>
          <div style="font-size:36px; font-weight:700;">{total_online}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px;">Offline</div>
          <div style="font-size:36px; font-weight:700;">{total_offline}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Gráficos (baseados na PLANILHA)
# =========================
def fig_instalados_por_dia():
    if instalado.empty:
        fig = go.Figure()
        fig.update_layout(title="Ultronlines instalados por dia — sem dados de instalação", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Bar(
        x=instalado["DATA_STR"],
        y=instalado["INSTALADOS_DIA"],
        text=instalado["INSTALADOS_DIA"],
        textposition="auto",
        marker=dict(color=COR_PRI)
    ))
    fig.update_layout(title="Ultronlines instalados por dia (real)",
                      xaxis_title="Data de instalação", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_instalados_acumulado():
    if instalado.empty:
        fig = go.Figure()
        fig.update_layout(title="Acumulado de Ultronlines instalados — sem dados", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Scatter(
        x=instalado["DATA_STR"],
        y=instalado["ACUMULADO"],
        mode="lines+markers",
        line=dict(width=3, color=COR_SEC),
        marker=dict(size=8, color=COR_SEC)
    ))
    fig.update_layout(title="Acumulado de Ultronlines instalados (real)",
                      xaxis_title="Data de instalação", yaxis_title="Acumulado", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_planejado_por_dia():
    if planejado.empty:
        fig = go.Figure()
        fig.update_layout(title="Ultronlines planejados por dia — sem dados", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Bar(
        x=planejado["DATA_STR"],
        y=planejado["PLANEJADOS_DIA"],
        text=planejado["PLANEJADOS_DIA"],
        textposition="auto",
        marker=dict(color="#9AA0A6")
    ))
    fig.update_layout(title="Ultronlines planejados por dia",
                      xaxis_title="Data planejada", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_cidade():
    if by_city.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribuição por Cidade — sem dados", **BASE_LAYOUT)
        axes_style(fig); return fig
    colors = [cores_2neuron[i % len(cores_2neuron)] for i in range(len(by_city))]
    fig = go.Figure(go.Bar(
        x=by_city["CIDADE"], y=by_city["QTD"],
        text=by_city["QTD"], textposition="auto",
        marker=dict(color=colors)
    ))
    fig.update_layout(title="Distribuição por Cidade (módulos distintos)",
                      xaxis_title="Cidade", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_status():
    fig = go.Figure(go.Pie(
        labels=["Online","Offline"], values=[total_online, total_offline],
        marker=dict(colors=[COR_PRI, COR_ALERTA]), hole=0.5, sort=False,
        textfont=dict(color=COR_TXT, family=BASE_FONT)
    ))
    fig.update_layout(title="Status (módulos únicos) — baseado em Gateway", **BASE_LAYOUT)
    return fig

# Mostra
c1, c2 = st.columns(2)
with c1: show(fig_instalados_por_dia())
with c2: show(fig_instalados_acumulado())

c3, c4 = st.columns(2)
with c3: show(fig_planejado_por_dia())
with c4: show(fig_status())

show(fig_cidade())

# =========================
# Tabelas (derivadas da planilha)
# =========================
# 1) Cronograma real por LOCAL/CIDADE/DATA INSTALAÇÃO (conta módulos únicos)
cron_real = (df.dropna(subset=["DATA INSTALAÇÃO ULTRONLINE"])
               .groupby(["DATA INSTALAÇÃO ULTRONLINE","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={
                   "DATA INSTALAÇÃO ULTRONLINE":"Data Instalação",
                   "CIDADE":"Cidade",
                   "LOCAL":"Local",
                   "MÓDULO":"Módulos"}
               )
            ).sort_values(["Data Instalação","Cidade","Local"])
table_png(cron_real, "Cronograma (REAL) — módulos instalados por dia/local")

# 2) Cronograma planejado por LOCAL/CIDADE/DATA PLANEJADA (conta módulos únicos)
cron_plan = (df.dropna(subset=["DATA PLANEJADA"])
               .groupby(["DATA PLANEJADA","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={
                   "DATA PLANEJADA":"Data Planejada",
                   "CIDADE":"Cidade",
                   "LOCAL":"Local",
                   "MÓDULO":"Módulos"}
               )
            ).sort_values(["Data Planejada","Cidade","Local"])
table_png(cron_plan, "Cronograma (PLANEJADO) — módulos por dia/local")

# 3) Séries e status (usando apenas planilha)
series_view = (df.loc[:, ["MÓDULO","ONLINE","DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA","CIDADE","LOCAL","GATEWAY"]]
                 .rename(columns={
                     "MÓDULO":"Série",
                     "ONLINE":"Status Online",
                     "DATA INSTALAÇÃO ULTRONLINE":"Data Instalação",
                     "DATA PLANEJADA":"Data Planejada",
                     "CIDADE":"Cidade",
                     "LOCAL":"Local",
                     "GATEWAY":"Gateway"
                 }))
series_view["Status Online"] = series_view["Status Online"].map({True:"Online", False:"Offline"})
series_view = series_view.sort_values(["Status Online","Data Instalação","Série"], ascending=[False, True, True])
table_png(series_view, "Séries (da planilha) e status")

# 4) Log textual dos seus registros (opcional — não usado nos cálculos)
if not df_reg.empty:
    df_reg_v = df_reg.rename(columns={"data":"Data","cidade":"Cidade","local":"Local","obs":"Observações"})
    df_reg_v = df_reg_v.sort_values(["Data","Cidade","Local"])
    table_png(df_reg_v, "Registros de campo (log textual – não interfere nos números)")

# Nota final
st.markdown(
    f"<div style='color:{COR_TXT} !important; opacity:.85;'>"
    "Todos os números de dias e quantidades de Ultronlines são calculados diretamente da <b>planilha</b>:<br>"
    "<b>REAL</b> = contagem de <i>módulos distintos</i> por <i>DATA INSTALAÇÃO ULTRONLINE</i>.<br>"
    "<b>PLANEJADO</b> = contagem de <i>módulos distintos</i> por <i>DATA PLANEJADA</i>.<br>"
    "O bloco de <i>registros</i> é apenas um log textual para observações e não altera os gráficos/kpis."
    "</div>",
    unsafe_allow_html=True
)
