# app_sabesp.py
# Lê EXATAMENTE: ./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx
# e constrói o dashboard 100% a partir das colunas da planilha.

import os, unicodedata
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ===== Aparência =====
pio.templates.default = None
COR_BG, COR_TXT = "#F8F8FF", "#2D2D2D"
COR_PRI, COR_SEC, COR_ALERTA = "#6A0DAD", "#8A2BE2", "#E76F51"
GRID, ZERO, AXIS = "#E6E6F0", "#D0D0DF", "#B0B0C0"
BASE_FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
st.set_page_config(page_title="Instalações 2Neuron | Sabesp — Planilha", layout="wide")
st.markdown(f"""
<style>
:root {{ color-scheme: light; }}
html, body, [data-testid="stAppViewContainer"] {{ background:{COR_BG} !important; font-family:{BASE_FONT}; }}
.block-container {{ padding-top: 1rem; padding-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

def axes_style(fig):
    fig.update_layout(
        paper_bgcolor=COR_BG, plot_bgcolor=COR_BG,
        font=dict(color=COR_TXT, size=14, family=BASE_FONT),
        margin=dict(l=50, r=20, t=60, b=60),
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=ZERO,
                   linecolor=AXIS, linewidth=1, mirror=True, ticks="outside"),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=ZERO,
                   linecolor=AXIS, linewidth=1, mirror=True, ticks="outside")
    )

# ===== 1) Caminho EXATO do Excel =====
EXCEL_PATH = "./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx"

# ===== 2) Leitura do Excel (engine explícito) =====
def ler_excel_xlsx(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        st.error(
            "Arquivo Excel não encontrado na raiz do projeto:\n\n"
            f"**{path}**\n\n"
            "Confirme que o arquivo está comitado no repositório, no diretório raiz."
        ); st.stop()
    try:
        import openpyxl  # garante dependência
    except Exception as e:
        st.error(
            "Dependência ausente para .xlsx: **openpyxl**.\n"
            "No requirements.txt adicione:  `openpyxl`\n"
            "Ou instale localmente:         `pip install openpyxl`\n\n"
            f"Detalhe: {e}"
        ); st.stop()
    try:
        return pd.read_excel(path, engine="openpyxl")  # primeira planilha
    except Exception as e:
        st.error(f"Falha ao ler o Excel com openpyxl: {e}"); st.stop()

# ===== 3) Normalização e validação de colunas =====
def norm_col(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ASCII", "ignore").decode("ASCII")
    return " ".join(c.replace("\n"," ").replace("\r"," ").split()).upper()

def preparar(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.rename(columns={c: norm_col(c) for c in df_raw.columns}).copy()
    # aliases -> nomes canônicos
    alias = {
        "LOCAL": ["LOCAL"],
        "CIDADE": ["CIDADE"],
        "MÓDULO": ["MODULO","SERIE","SÉRIE","MÓDULO/ SÉRIE","SERIE/MODULO"],
        "GATEWAY": ["GATEWAY"],
        "DATA INSTALAÇÃO ULTRONLINE": ["DATA INSTALACAO ULTRONLINE","DATA INSTALAÇÃO","DATA INSTALACAO"],
        "DATA PLANEJADA": ["DATA PLANEJADA","DATA PREVISTA"]
    }
    mapa = {}
    for alvo, opts in alias.items():
        for o in opts:
            if o in df.columns:
                mapa[alvo] = o; break

    obrig = ["LOCAL","CIDADE","MÓDULO","GATEWAY","DATA INSTALAÇÃO ULTRONLINE"]
    faltam = [c for c in obrig if c not in mapa]
    if faltam:
        st.error(
            "Colunas obrigatórias ausentes na planilha (após normalização): "
            + ", ".join(faltam)
            + "\n\nColunas encontradas: "
            + ", ".join(df.columns)
        ); st.stop()

    df = df.rename(columns={mapa[k]: k for k in mapa})

    # tipos e limpeza
    df["DATA INSTALAÇÃO ULTRONLINE"] = pd.to_datetime(df["DATA INSTALAÇÃO ULTRONLINE"], errors="coerce")
    if "DATA PLANEJADA" in df.columns:
        df["DATA PLANEJADA"] = pd.to_datetime(df["DATA PLANEJADA"], errors="coerce")

    for c in ["LOCAL","CIDADE","MÓDULO","GATEWAY"]:
        df[c] = df[c].astype(str).str.strip()

    # status via gateway
    df["ONLINE"] = ~df["GATEWAY"].str.lower().eq("sem gateway")
    return df

# ===== 4) Carrega SOMENTE da planilha e calcula métricas =====
df_raw = ler_excel_xlsx(EXCEL_PATH)
df = preparar(df_raw)

# Instalados reais (conta MÓDULO distinto por dia de instalação)
instalado = (
    df.dropna(subset=["MÓDULO","DATA INSTALAÇÃO ULTRONLINE"])
      .drop_duplicates(subset=["MÓDULO","DATA INSTALAÇÃO ULTRONLINE"])
      .groupby("DATA INSTALAÇÃO ULTRONLINE", as_index=False)["MÓDULO"]
      .nunique()
      .rename(columns={"DATA INSTALAÇÃO ULTRONLINE":"DATA","MÓDULO":"INSTALADOS_DIA"})
      .sort_values("DATA")
)
instalado["ACUMULADO"] = instalado["INSTALADOS_DIA"].cumsum()
instalado["DATA_STR"] = instalado["DATA"].dt.strftime("%d/%m/%Y")

# Planejado (opcional, se existir)
planejado = pd.DataFrame()
if "DATA PLANEJADA" in df.columns:
    planejado = (
        df.dropna(subset=["MÓDULO","DATA PLANEJADA"])
          .drop_duplicates(subset=["MÓDULO","DATA PLANEJADA"])
          .groupby("DATA PLANEJADA", as_index=False)["MÓDULO"]
          .nunique()
          .rename(columns={"DATA PLANEJADA":"DATA","MÓDULO":"PLANEJADOS_DIA"})
          .sort_values("DATA")
    )
    if not planejado.empty:
        planejado["ACUM_PLANEJADO"] = planejado["PLANEJADOS_DIA"].cumsum()
        planejado["DATA_STR"] = planejado["DATA"].dt.strftime("%d/%m/%Y")

# Por cidade (módulos distintos)
by_city = (
    df.dropna(subset=["MÓDULO"])
      .groupby("CIDADE", as_index=False)["MÓDULO"]
      .nunique()
      .rename(columns={"MÓDULO":"QTD"})
      .sort_values("QTD", ascending=False)
)

# Status
total_series = df["MÓDULO"].nunique(dropna=True)
total_online  = int(df.dropna(subset=["MÓDULO"])["ONLINE"].sum())
total_offline = max(0, total_series - total_online)

# ===== 5) KPIs =====
st.markdown(
    f"""
    <div style="color:{COR_TXT}">
      <h1 style="margin:0 0 6px 0; font-size:44px; line-height:1.15; font-weight:800;">
        Instalações 2Neuron na Sabesp — Planilha
      </h1>
      <div style="opacity:.9; margin:0 0 18px 0; font-size:15px;">
        Base: <b>{os.path.basename(EXCEL_PATH)}</b> — módulos únicos: {total_series}
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

# ===== 6) Gráficos =====
def fig_instalados_por_dia():
    fig = go.Figure()
    if not instalado.empty:
        fig.add_bar(x=instalado["DATA_STR"], y=instalado["INSTALADOS_DIA"],
                    text=instalado["INSTALADOS_DIA"], textposition="auto",
                    marker=dict(color=COR_PRI))
    fig.update_layout(title="Ultronlines instalados por dia (real)",
                      xaxis_title="Data de instalação", yaxis_title="Quantidade")
    axes_style(fig); return fig

def fig_instalados_acum():
    fig = go.Figure()
    if not instalado.empty:
        fig.add_scatter(x=instalado["DATA_STR"], y=instalado["ACUMULADO"],
                        mode="lines+markers",
                        line=dict(width=3, color=COR_SEC),
                        marker=dict(size=8, color=COR_SEC))
    fig.update_layout(title="Acumulado de Ultronlines instalados (real)",
                      xaxis_title="Data de instalação", yaxis_title="Acumulado")
    axes_style(fig); return fig

def fig_planejado_por_dia():
    fig = go.Figure()
    if not planejado.empty:
        fig.add_bar(x=planejado["DATA_STR"], y=planejado["PLANEJADOS_DIA"],
                    text=planejado["PLANEJADOS_DIA"], textposition="auto",
                    marker=dict(color="#9AA0A6"))
    fig.update_layout(title="Ultronlines planejados por dia",
                      xaxis_title="Data planejada", yaxis_title="Quantidade")
    axes_style(fig); return fig

def fig_status():
    fig = go.Figure(go.Pie(labels=["Online","Offline"],
                           values=[total_online, total_offline],
                           marker=dict(colors=[COR_PRI, COR_ALERTA]),
                           hole=0.5, sort=False))
    fig.update_layout(title="Status (módulos únicos) — baseado em Gateway")
    return fig

def fig_cidade():
    fig = go.Figure()
    if not by_city.empty:
        pal = ["#6A0DAD","#8A2BE2","#9370DB","#D8BFD8","#4B0082"]
        fig.add_bar(x=by_city["CIDADE"], y=by_city["QTD"],
                    text=by_city["QTD"], textposition="auto",
                    marker=dict(color=[pal[i % len(pal)] for i in range(len(by_city))]))
    fig.update_layout(title="Distribuição por Cidade (módulos distintos)",
                      xaxis_title="Cidade", yaxis_title="Quantidade")
    axes_style(fig); return fig

c1, c2 = st.columns(2)
with c1: st.plotly_chart(fig_instalados_por_dia(), use_container_width=True, theme="none")
with c2: st.plotly_chart(fig_instalados_acum(), use_container_width=True, theme="none")

c3, c4 = st.columns(2)
with c3: st.plotly_chart(fig_planejado_por_dia(), use_container_width=True, theme="none")
with c4: st.plotly_chart(fig_status(), use_container_width=True, theme="none")

st.plotly_chart(fig_cidade(), use_container_width=True, theme="none")

# ===== 7) Tabelas =====
cron_real = (
    df.dropna(subset=["DATA INSTALAÇÃO ULTRONLINE"])
      .groupby(["DATA INSTALAÇÃO ULTRONLINE","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
      .nunique()
      .rename(columns={"DATA INSTALAÇÃO ULTRONLINE":"Data Instalação","MÓDULO":"Módulos"})
      .sort_values(["Data Instalação","CIDADE","LOCAL"])
)
st.dataframe(cron_real, use_container_width=True)

if "DATA PLANEJADA" in df.columns:
    cron_plan = (
        df.dropna(subset=["DATA PLANEJADA"])
          .groupby(["DATA PLANEJADA","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
          .nunique()
          .rename(columns={"DATA PLANEJADA":"Data Planejada","MÓDULO":"Módulos"})
          .sort_values(["Data Planejada","CIDADE","LOCAL"])
    )
    if not cron_plan.empty:
        st.dataframe(cron_plan, use_container_width=True)

cols_visao = [c for c in ["LOCAL","CIDADE","MÓDULO","GATEWAY","DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA","ONLINE"] if c in df.columns]
st.dataframe(df[cols_visao].copy(), use_container_width=True)
