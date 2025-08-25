# streamlit_app.py
import os, glob, unicodedata, io
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import plotly.io as pio

# -------------------- Aparência fixa --------------------
cores_2neuron = ['#6A0DAD', '#8A2BE2', '#9370DB', '#D8BFD8', '#4B0082']
COR_BG, COR_TXT = "#F8F8FF", "#2D2D2D"
COR_PRI, COR_SEC, COR_ALERTA = cores_2neuron[0], cores_2neuron[1], "#E76F51"
GRID, ZERO, AXIS = "#E6E6F0", "#D0D0DF", "#B0B0C0"
BASE_FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
pio.templates.default = None
st.set_page_config(page_title="Instalações 2Neuron | Sabesp", layout="wide")
st.markdown(f"""
<style>
:root {{ color-scheme: light; }}
html, body, [data-testid="stAppViewContainer"] {{
  background:{COR_BG} !important; font-family:{BASE_FONT};
}}
.block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

BASE_LAYOUT = dict(
    paper_bgcolor=COR_BG, plot_bgcolor=COR_BG,
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
def show(fig): st.plotly_chart(fig, use_container_width=True, theme="none")

# -------------------- Leitura dura da planilha --------------------
ALVO = "SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3)"

def normalizar_col(col: str) -> str:
    c = unicodedata.normalize("NFKD", col).encode("ASCII","ignore").decode("ASCII")
    c = " ".join(c.replace("\n"," ").replace("\r"," ").split())
    return c.upper()

def listar_arquivos():
    # raiz do projeto
    cand = []
    for pad in (f"./{ALVO}.*", f"./{ALVO}*.*"):
        cand += glob.glob(pad)
    # mantém apenas tipos comuns
    exts_ok = {".xlsx",".xls",".csv",".parquet"}
    cand = [p for p in cand if os.path.splitext(p)[1].lower() in exts_ok]
    # ordena (prioriza Excel)
    prioridade = [".xlsx",".xls",".csv",".parquet"]
    cand.sort(key=lambda p: prioridade.index(os.path.splitext(p)[1].lower()))
    return cand

def ler_arquivo(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx",".xls"]:
        return pd.read_excel(path)
    if ext == ".csv":
        # tenta ; e ,
        try:   return pd.read_csv(path, sep=";")
        except Exception: return pd.read_csv(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    # fallback
    return pd.read_excel(path)

def preparar(df_raw: pd.DataFrame) -> pd.DataFrame:
    # normaliza cabeçalhos
    df = df_raw.rename(columns={c: normalizar_col(c) for c in df_raw.columns}).copy()

    # mapeamento de aliases -> nomes canônicos obrigatórios
    alias = {
        "LOCAL": ["LOCAL"],
        "CIDADE": ["CIDADE"],
        "MÓDULO": ["MODULO","SERIE","MÓDULO/ SÉRIE","SERIE/MODULO"],
        "GATEWAY": ["GATEWAY"],
        "DATA INSTALAÇÃO ULTRONLINE": ["DATA INSTALACAO ULTRONLINE","DATA INSTALAÇÃO","DATA INSTALACAO"],
        "DATA PLANEJADA": ["DATA PLANEJADA","DATA PREVISTA"]
    }

    # encontra as colunas
    mapa = {}
    for alvo, opts in alias.items():
        for o in opts:
            if o in df.columns:
                mapa[alvo] = o
                break

    # valida obrigatórias
    obrig = ["LOCAL","CIDADE","MÓDULO","GATEWAY","DATA INSTALAÇÃO ULTRONLINE"]
    faltam = [c for c in obrig if c not in mapa]
    if faltam:
        st.error(
            "Colunas obrigatórias ausentes na planilha (depois da normalização): "
            + ", ".join(faltam)
            + ".\n\nColunas que encontrei: "
            + ", ".join(df.columns)
        )
        st.stop()

    # renomeia para canônicos
    df = df.rename(columns={mapa[k]: k for k in mapa})

    # tipos
    for dcol in ["DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA"]:
        if dcol in df.columns:
            df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
    for scol in ["LOCAL","CIDADE","MÓDULO","GATEWAY"]:
        df[scol] = df[scol].astype(str).str.strip()

    # status online simples via gateway
    df["ONLINE"] = ~df["GATEWAY"].str.lower().eq("sem gateway")
    return df

# -------------------- Seletor/força de arquivo --------------------
st.sidebar.markdown("### Arquivo da planilha")
arquivos = listar_arquivos()
if not arquivos:
    st.sidebar.error("Não encontrei o arquivo na raiz do projeto com o nome alvo.")
    up = st.sidebar.file_uploader("Envie a planilha (xlsx/xls/csv/parquet)", type=["xlsx","xls","csv","parquet"])
    if up is None:
        st.stop()
    tmp_path = f"./__upload__{up.name}"
    with open(tmp_path, "wb") as f: f.write(up.getbuffer())
    arquivos = [tmp_path]

arq_escolhido = st.sidebar.selectbox("Selecione o arquivo encontrado:", arquivos, index=0)
st.sidebar.success(f"Usando: {os.path.basename(arq_escolhido)}")

# -------------------- Lê e prepara (obrigatório) --------------------
df_raw = ler_arquivo(arq_escolhido)
df = preparar(df_raw)

# -------------------- Métricas e agregações (da planilha!) --------------------
# Instalados (reais): módulos distintos por dia de instalação
instalado = (df.dropna(subset=["MÓDULO","DATA INSTALAÇÃO ULTRONLINE"])
               .groupby("DATA INSTALAÇÃO ULTRONLINE", as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA INSTALAÇÃO ULTRONLINE":"DATA","MÓDULO":"INSTALADOS_DIA"})
            ).sort_values("DATA")
instalado["ACUMULADO"] = instalado["INSTALADOS_DIA"].cumsum()
instalado["DATA_STR"] = instalado["DATA"].dt.strftime("%d/%m/%Y")

# Planejado (opcional)
planejado = (df.dropna(subset=["MÓDULO","DATA PLANEJADA"])
               .groupby("DATA PLANEJADA", as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA PLANEJADA":"DATA","MÓDULO":"PLANEJADOS_DIA"})
            ).sort_values("DATA")
if not planejado.empty:
    planejado["ACUM_PLANEJADO"] = planejado["PLANEJADOS_DIA"].cumsum()
    planejado["DATA_STR"] = planejado["DATA"].dt.strftime("%d/%m/%Y")

# Cidade
by_city = (df.dropna(subset=["MÓDULO"])
             .groupby("CIDADE", as_index=False)["MÓDULO"]
             .nunique()
             .rename(columns={"MÓDULO":"QTD"}))

# Status
total_series = df["MÓDULO"].nunique(dropna=True)
total_online = int(df.dropna(subset=["MÓDULO"])["ONLINE"].sum())
total_offline = max(0, total_series - total_online)

# -------------------- Header/KPIs --------------------
st.markdown(
    f"""
    <div style="color:{COR_TXT}">
      <h1 style="margin:0 0 6px 0; font-size:44px; line-height:1.15; font-weight:800;">
        Instalações 2Neuron na Sabesp — **Planilha**
      </h1>
      <div style="opacity:.9; margin:0 0 18px 0; font-size:15px;">
        Base: <b>{os.path.basename(arq_escolhido)}</b> — módulos únicos: {total_series}
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

# -------------------- Gráficos (só da planilha) --------------------
def fig_instalados_por_dia():
    fig = go.Figure()
    if not instalado.empty:
        fig.add_bar(x=instalado["DATA_STR"], y=instalado["INSTALADOS_DIA"],
                    text=instalado["INSTALADOS_DIA"], textposition="auto",
                    marker=dict(color=COR_PRI))
    fig.update_layout(title="Ultronlines instalados por dia (real)",
                      xaxis_title="Data de instalação", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_instalados_acumulado():
    fig = go.Figure()
    if not instalado.empty:
        fig.add_scatter(x=instalado["DATA_STR"], y=instalado["ACUMULADO"],
                        mode="lines+markers",
                        line=dict(width=3, color=COR_SEC),
                        marker=dict(size=8, color=COR_SEC))
    fig.update_layout(title="Acumulado de Ultronlines instalados (real)",
                      xaxis_title="Data de instalação", yaxis_title="Acumulado", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_planejado_por_dia():
    fig = go.Figure()
    if not planejado.empty:
        fig.add_bar(x=planejado["DATA_STR"], y=planejado["PLANEJADOS_DIA"],
                    text=planejado["PLANEJADOS_DIA"], textposition="auto",
                    marker=dict(color="#9AA0A6"))
    fig.update_layout(title="Ultronlines planejados por dia",
                      xaxis_title="Data planejada", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_cidade():
    fig = go.Figure()
    if not by_city.empty:
        fig.add_bar(x=by_city["CIDADE"], y=by_city["QTD"],
                    text=by_city["QTD"], textposition="auto",
                    marker=dict(color=[cores_2neuron[i % len(cores_2neuron)] for i in range(len(by_city))]))
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

c1, c2 = st.columns(2)
with c1: show(fig_instalados_por_dia())
with c2: show(fig_instalados_acumulado())

c3, c4 = st.columns(2)
with c3: show(fig_planejado_por_dia())
with c4: show(fig_status())

show(fig_cidade())

# -------------------- Tabelas derivadas (somente planilha) --------------------
cron_real = (df.dropna(subset=["DATA INSTALAÇÃO ULTRONLINE"])
               .groupby(["DATA INSTALAÇÃO ULTRONLINE","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA INSTALAÇÃO ULTRONLINE":"Data Instalação","MÓDULO":"Módulos"})
            ).sort_values(["Data Instalação","CIDADE","LOCAL"])
st.dataframe(cron_real, use_container_width=True)

cron_plan = (df.dropna(subset=["DATA PLANEJADA"])
               .groupby(["DATA PLANEJADA","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
               .nunique()
               .rename(columns={"DATA PLANEJADA":"Data Planejada","MÓDULO":"Módulos"})
            ).sort_values(["Data Planejada","CIDADE","LOCAL"])
st.dataframe(cron_plan, use_container_width=True)

series_view = (df.loc[:, ["MÓDULO","ONLINE","DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA","CIDADE","LOCAL","GATEWAY"]]
                 .rename(columns={"MÓDULO":"Série","ONLINE":"Online",
                                  "DATA INSTALAÇÃO ULTRONLINE":"Data Instalação",
                                  "DATA PLANEJADA":"Data Planejada",
                                  "CIDADE":"Cidade","LOCAL":"Local","GATEWAY":"Gateway"}))
series_view["Online"] = series_view["Online"].map({True:"Online", False:"Offline"})
series_view = series_view.sort_values(["Online","Data Instalação","Série"], ascending=[False, True, True])
st.dataframe(series_view, use_container_width=True)
