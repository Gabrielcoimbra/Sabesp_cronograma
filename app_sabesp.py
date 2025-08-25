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
# Paleta 2Neuron (fixa e imutável)
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

# Plotly sem template p/ não herdar nada do cliente
pio.templates.default = None

st.set_page_config(page_title="Instalações 2Neuron | Sabesp", layout="wide")

# CSS estático (cores e fontes travadas)
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
# Utils de layout/figura
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
    # precisa de kaleido instalado
    img = fig.to_image(format="png", width=width, height=height, scale=scale)
    return Image.open(io.BytesIO(img))

def show(fig, width=1100, height=420):
    try:
        st.image(fig_to_png(fig, width=width, height=height), use_container_width=True)
    except Exception:
        # fallback se kaleido não estiver disponível
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
# Carregamento da planilha
# =========================
ALVO_BASE = "SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3)"

def normalizar_col(col: str) -> str:
    # Remove acentos, quebra de linha, múltiplos espaços e padroniza
    c = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode("ASCII")
    c = c.replace("\n", " ").replace("\r", " ")
    c = " ".join(c.split())
    return c.upper()

def localizar_arquivo_base():
    # Procura na raiz do projeto por qualquer extensão comum
    padrões = [f"./{ALVO_BASE}.*", f"./{ALVO_BASE}*.*"]
    candidatos = []
    for p in padrões:
        candidatos.extend(glob.glob(p))
    # Prioriza Excel
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
            df = pd.read_excel(caminho)
        elif ext == ".csv":
            # tenta ; e , automaticamente
            try:
                df = pd.read_csv(caminho, sep=";")
            except Exception:
                df = pd.read_csv(caminho)
        elif ext == ".parquet":
            df = pd.read_parquet(caminho)
        else:
            st.warning(f"Extensão não reconhecida ({ext}). Tentando ler como Excel.")
            df = pd.read_excel(caminho)
        return df

    # Fallback: uploader
    st.info("Arquivo não encontrado na raiz. Envie a planilha pelo uploader abaixo.")
    up = st.file_uploader("Envie o arquivo da planilha (xlsx/xls/csv/parquet)", type=["xlsx","xls","csv","parquet"])
    if up is None:
        st.stop()
    ext = os.path.splitext(up.name)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(up)
    elif ext == ".csv":
        try:
            return pd.read_csv(up, sep=";")
        except Exception:
            return pd.read_csv(up)
    elif ext == ".parquet":
        return pd.read_parquet(up)
    else:
        return pd.read_excel(up)

def preparar_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    # padroniza nomes
    m = {c: normalizar_col(c) for c in df_raw.columns}
    df = df_raw.rename(columns=m).copy()

    # Mapeia colunas esperadas (flexível a variações)
    alias = {
        "SEQUÊNCIA": ["SEQUENCIA", "SEQ"],
        "DATA INICIAL": ["DATA INICIAL"],
        "DATA PLANEJADA": ["DATA PLANEJADA"],
        "DIA SEMANA": ["DIA SEMANA", "DIA DA SEMANA"],
        "MÁQUINA": ["MAQUINA"],
        "IDENTIFICAÇÃO (TAG/ID)": ["IDENTIFICACAO (TAG/ID)", "TAG", "ID", "IDENTIFICACAO"],
        "MÁQUINA ACOPLADA": ["MAQUINA ACOPLADA"],
        "LOCAL": ["LOCAL"],
        "CIDADE": ["CIDADE"],
        "ENDEREÇO": ["ENDERECO"],
        "COORDENADAS": ["COORDENADAS"],
        "MELHOR OPERADORA DE CELULAR EEE": ["MELHOR OPERADORA DE CELULAR EEE", "OPERADORA"],
        'POTÊNCIA (CV)': ['"POTENCIA (CV)"', "POTENCIA (CV)", "POTENCIA CV", "POTENCIA  (CV)"],
        'POTÊNCIA (KW)': ['"POTENCIA (KW)"', "POTENCIA (KW)", "POTENCIA KW", "POTENCIA  (KW)"],
        'CORRENTE (A)': ['"CORRENTE (A)"', "CORRENTE (A)", "CORRENTE"],
        'TENSÃO (V)': ['"TENSAO (V)"', "TENSAO (V)", "TENSAO", "TENSÃO (V)"],
        'RELAÇÃO DE TRANSFORMAÇÃO TP (SE HOUVER)': ["RELACAO DE TRANSFORMACAO TP (SE HOUVER)", "RELACAO TP", "TP"],
        'ROTAÇÃO (RPM)': ["ROTACAO (RPM)", "RPM"],
        'SEÇÃO DO CABO (MM²)': ["SECAO DO CABO (MM2)", "SECAO DO CABO (MM²)"],
        'DIÂMETRO EXTERNO DO CABO (MM)': ["DIAMETRO EXTERNO DO CABO (MM)"],
        'NÚMERO DE CABOS POR FASE': ["NUMERO DE CABOS POR FASE", "CABOS POR FASE"],
        'ACIONAMENTO (DIRETA, INVERSOR, SOFT)': ["ACIONAMENTO (DIRETA, INVERSOR, SOFT)", "ACIONAMENTO"],
        "MÓDULO": ["MODULO", "SERIE", "MÓDULO/ SÉRIE", "SERIE/MODULO"],
        "GATEWAY": ["GATEWAY"],
        "TC": ["TC"],
        "DATA INSTALAÇÃO ULTRONLINE": ["DATA INSTALACAO ULTRONLINE", "DATA INSTALACAO", "DATA INSTALAÇÃO"],
        "OBSERVAÇÃO": ["OBSERVACAO", "OBS"],
        "REALOCAÇÃO?": ["REALOCAO?", "REALOCAO", "REALOCAÇÃO"],
        "NOVA INSTALAÇÃO": ["NOVA INSTALACAO"],
        "ÁREA SABESP": ["AREA SABESP"],
        "GESTÃO": ["GESTAO"],
        "NOME": ["NOME", "RESPONSAVEL"]
    }

    # cria mapa final de nomes canônicos -> coluna existente
    final_cols = {}
    for alvo, opcoes in alias.items():
        for o in [alvo] + opcoes:
            if o in df.columns:
                final_cols[alvo] = o
                break

    # garante existência de colunas chave mesmo que ausentes (evita erros downstream)
    essenciais = ["LOCAL","CIDADE","MÓDULO","GATEWAY","DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA",
                  "OBSERVAÇÃO","REALOCAÇÃO?","NOVA INSTALAÇÃO","ÁREA SABESP","GESTÃO","NOME"]
    for k in essenciais:
        if k not in final_cols:
            # cria vazia
            df[k] = pd.NA
            final_cols[k] = k

    # recorta/renomeia para canônico
    df = df.rename(columns={final_cols[k]: k for k in final_cols.keys()})

    # Tipos e limpeza
    # datas
    for dcol in ["DATA INSTALAÇÃO ULTRONLINE", "DATA PLANEJADA", "DATA INICIAL"]:
        if dcol in df.columns:
            df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
    # números (suporta "177,1" etc)
    def to_float(s):
        if pd.isna(s): return pd.NA
        if isinstance(s, (int,float)): return float(s)
        s = str(s).replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return pd.NA

    for ncol in ['POTÊNCIA (CV)','POTÊNCIA (KW)','CORRENTE (A)','TENSÃO (V)','ROTAÇÃO (RPM)']:
        if ncol in df.columns:
            df[ncol] = df[ncol].apply(to_float)

    # coluna "DATA BASE" para análise (usa instalação; se vazia, usa planejada)
    df["DATA BASE"] = df["DATA INSTALAÇÃO ULTRONLINE"].fillna(df["DATA PLANEJADA"])

    # padroniza strings chaves
    for scol in ["LOCAL","CIDADE","MÓDULO","GATEWAY","OBSERVAÇÃO","ACIONAMENTO (DIRETA, INVERSOR, SOFT)"]:
        if scol in df.columns:
            df[scol] = df[scol].astype(str).str.strip()

    return df

# =========================
# Inventário / Status online
# =========================
# Série(s) offline conhecidas — mantenha/atualize aqui conforme necessário
series_offline = {"U2N000277", "U2N000308"}

def marcar_status_online(df: pd.DataFrame) -> pd.DataFrame:
    if "MÓDULO" not in df.columns:
        df["MÓDULO"] = pd.NA
    df["ONLINE"] = ~df["MÓDULO"].isin(series_offline)
    # Se Gateway explicitamente "Sem Gateway", força offline
    if "GATEWAY" in df.columns:
        df.loc[df["GATEWAY"].astype(str).str.strip().str.lower() == "sem gateway", "ONLINE"] = False
    return df

# =========================
# Bloco de registros (mensagens) — você atualiza à vontade
# =========================
registros = [
    # Exemplo de como manter atualizações do dia a dia
    {"data":"2025-08-11","cidade":"São Paulo","local":"EEE Alvarenga Mãe",
     "ultronlines":4,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000283 (TC 35→24 mm), U2N000282 (com gateway), U2N000287, U2N000270."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"EEE Lavapés",
     "ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000269 e U2N000288; conexões confirmadas."},
    # ... (mantenha/edite conforme seu cronograma)
]
df_reg = pd.DataFrame(registros)
if not df_reg.empty and "data" in df_reg.columns:
    df_reg["data"] = pd.to_datetime(df_reg["data"], errors="coerce")

# =========================
# Carrega dados e prepara
# =========================
caminho = localizar_arquivo_base()
df_raw = ler_planilha(caminho)
df = preparar_dataframe(df_raw)
df = marcar_status_online(df)

# =========================
# KPIs
# =========================
TOTAL_LINHAS = len(df.index)
# séries distintas (módulos)
total_series = df["MÓDULO"].nunique(dropna=True)
total_online = int(df.dropna(subset=["MÓDULO"])["ONLINE"].sum()) if total_series else 0
total_offline = int(max(0, (total_series - total_online)))

st.markdown(
    f"""
    <div style="color:{COR_TXT} !important;">
      <h1 style="margin:0 0 6px 0; font-size:44px; line-height:1.15; font-weight:800; color:{COR_TXT} !important;">
        Instalações 2Neuron na Sabesp
      </h1>
      <div style="opacity:.9; margin:0 0 18px 0; font-size:15px; color:{COR_TXT} !important;">
        Base: <b>{os.path.basename(caminho) if caminho else "upload manual"}</b> — linhas: {TOTAL_LINHAS}, módulos únicos: {total_series}
      </div>

      <div style="display:flex; gap:28px; flex-wrap:wrap;">
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Módulos (séries) distintos</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{total_series}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Online</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{total_online}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Offline</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{total_offline}</div>
          <div style="font-size:12px; opacity:.7; margin-top:2px; color:{COR_TXT} !important;">Forçado p/ séries: {", ".join(sorted(series_offline)) if series_offline else "—"}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Agregações para gráficos
# =========================
# 1) Distribuição por cidade (conta de módulos distintos por cidade)
by_city = (df.dropna(subset=["MÓDULO"])
             .groupby("CIDADE", as_index=False)["MÓDULO"]
             .nunique()
             .rename(columns={"MÓDULO": "QTD"}))

# 2) Status online/offline
status_vals = [total_online, total_offline]

# 3) Linha do tempo por data base (instalação/planejada)
serie_por_data = (df.dropna(subset=["MÓDULO","DATA BASE"])
                    .groupby("DATA BASE", as_index=False)["MÓDULO"]
                    .nunique()
                    .rename(columns={"MÓDULO":"INSTALADOS_DIA"}))
serie_por_data = serie_por_data.sort_values("DATA BASE")
serie_por_data["ACUMULADO"] = serie_por_data["INSTALADOS_DIA"].cumsum()
serie_por_data["DATA_STR"] = serie_por_data["DATA BASE"].dt.strftime("%d/%m/%Y")

# 4) Potência instalada por cidade (se disponível)
if "POTÊNCIA (KW)" in df.columns:
    pot_por_cidade = (df.groupby("CIDADE", as_index=False)["POTÊNCIA (KW)"]
                        .sum(min_count=1)
                        .rename(columns={"POTÊNCIA (KW)":"POT_KW_TOTAL"}))
else:
    pot_por_cidade = pd.DataFrame(columns=["CIDADE","POT_KW_TOTAL"])

# =========================
# Gráficos
# =========================
def fig_barras_por_dia():
    if serie_por_data.empty:
        fig = go.Figure()
        fig.update_layout(title="Ultronlines por dia — sem dados de data", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Bar(
        x=serie_por_data["DATA_STR"], y=serie_por_data["INSTALADOS_DIA"],
        text=serie_por_data["INSTALADOS_DIA"], textposition="auto",
        marker=dict(color=COR_PRI, line=dict(color=AXIS, width=0))
    ))
    fig.update_layout(title="Ultronlines por dia (Instalação/Planejada)",
                      xaxis_title="Data", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_acumulado():
    if serie_por_data.empty:
        fig = go.Figure()
        fig.update_layout(title="Acumulado — sem dados de data", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Scatter(
        x=serie_por_data["DATA_STR"], y=serie_por_data["ACUMULADO"],
        mode="lines+markers", line=dict(width=3, color=COR_SEC),
        marker=dict(size=8, color=COR_SEC)
    ))
    fig.update_layout(title="Acumulado de Ultronlines",
                      xaxis_title="Data", yaxis_title="Acumulado", **BASE_LAYOUT)
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
        labels=["Online","Offline"], values=status_vals,
        marker=dict(colors=[COR_PRI, COR_ALERTA]), hole=0.5, sort=False,
        textfont=dict(color=COR_TXT, family=BASE_FONT)
    ))
    fig.update_layout(title="Status dos Ultronlines (módulos únicos)", **BASE_LAYOUT)
    return fig

def fig_potencia_cidade():
    if pot_por_cidade.empty or pot_por_cidade["POT_KW_TOTAL"].isna().all():
        fig = go.Figure()
        fig.update_layout(title="Potência instalada por cidade — dados indisponíveis", **BASE_LAYOUT)
        axes_style(fig); return fig
    fig = go.Figure(go.Bar(
        x=pot_por_cidade["CIDADE"], y=pot_por_cidade["POT_KW_TOTAL"],
        text=[f"{v:.0f}" if pd.notna(v) else "" for v in pot_por_cidade["POT_KW_TOTAL"]],
        textposition="auto",
        marker=dict(color=COR_PRI)
    ))
    fig.update_layout(title="Potência (kW) instalada por cidade",
                      xaxis_title="Cidade", yaxis_title="kW", **BASE_LAYOUT)
    axes_style(fig); return fig

# Layout dos gráficos
c1, c2 = st.columns(2)
with c1: show(fig_barras_por_dia())
with c2: show(fig_acumulado())

c3, c4 = st.columns(2)
with c3: show(fig_cidade())
with c4: show(fig_status())

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
show(fig_potencia_cidade(), height=450)

# =========================
# Tabelas principais (sem coluna de COORDENADAS nos prints)
# =========================
# Cronograma derivado (instalação/planejada) + seus "registros" manuais
if not df_reg.empty:
    df_crono_reg = (df_reg[["data","cidade","local","ultronlines","ultronlinks","gateways_extra","obs"]]
                    .rename(columns={
                        "data":"Data","cidade":"Cidade","local":"Local",
                        "ultronlines":"Ultronlines","ultronlinks":"Ultronlinks",
                        "gateways_extra":"Gateways extra","obs":"Observações"
                    })
                    .sort_values(["Data","Cidade","Local"]))
    table_png(df_crono_reg, "Detalhamento diário (registros manuais)")

# Cronograma a partir da base (módulos distintos por Local/Data Base)
df_base_crono = (df.dropna(subset=["DATA BASE"])
                   .groupby(["DATA BASE","CIDADE","LOCAL"], as_index=False)["MÓDULO"]
                   .nunique()
                   .rename(columns={"DATA BASE":"Data","CIDADE":"Cidade","LOCAL":"Local","MÓDULO":"Módulos"}))
df_base_crono = df_base_crono.sort_values(["Data","Cidade","Local"])
table_png(df_base_crono, "Cronograma (derivado da planilha)")

# Séries e status
df_series_view = (df.dropna(subset=["MÓDULO"])
                    .loc[:, ["MÓDULO","ONLINE","DATA INSTALAÇÃO ULTRONLINE","DATA PLANEJADA","CIDADE","LOCAL","GATEWAY"]]
                    .rename(columns={
                        "MÓDULO":"Série",
                        "ONLINE":"Status Online",
                        "DATA INSTALAÇÃO ULTRONLINE":"Data Instalação",
                        "DATA PLANEJADA":"Data Planejada",
                        "CIDADE":"Cidade",
                        "LOCAL":"Local",
                        "GATEWAY":"Gateway"
                    })
             )
df_series_view["Status Online"] = df_series_view["Status Online"].map({True:"Online", False:"Offline"})
df_series_view = df_series_view.sort_values(["Status Online","Data Instalação","Série"], ascending=[False, True, True])
table_png(df_series_view, "Séries e status")

# Inventário técnico (principais campos) — removendo COORDENADAS do print
cols_inv = ["LOCAL","CIDADE","MÓDULO","GATEWAY","MELHOR OPERADORA DE CELULAR EEE",
            "ACIONAMENTO (DIRETA, INVERSOR, SOFT)","POTÊNCIA (CV)","POTÊNCIA (KW)","CORRENTE (A)",
            "TENSÃO (V)","ROTAÇÃO (RPM)","SEÇÃO DO CABO (MM²)","DIÂMETRO EXTERNO DO CABO (MM)",
            "NÚMERO DE CABOS POR FASE","ENDEREÇO","ONLINE"]
cols_inv = [c for c in cols_inv if c in df.columns]
df_inv_view = (df.loc[:, cols_inv]
                 .rename(columns={
                     "LOCAL":"Local","CIDADE":"Cidade","MÓDULO":"Série","GATEWAY":"Gateway",
                     "MELHOR OPERADORA DE CELULAR EEE":"Operadora",
                     "ACIONAMENTO (DIRETA, INVERSOR, SOFT)":"Acionamento",
                     "POTÊNCIA (CV)":"Pot (cv)","POTÊNCIA (KW)":"Pot (kW)","CORRENTE (A)":"Corr (A)",
                     "TENSÃO (V)":"Tensão (V)","ROTAÇÃO (RPM)":"RPM","SEÇÃO DO CABO (MM²)":"Seção (mm²)",
                     "DIÂMETRO EXTERNO DO CABO (MM)":"Diâm (mm)","NÚMERO DE CABOS POR FASE":"Cabos/fase",
                     "ENDEREÇO":"Endereço","ONLINE":"Online"
                 }))
table_png(df_inv_view, "Inventário técnico (campos principais)")

# Observação final
st.markdown(
    f"<div style='color:{COR_TXT} !important; opacity:.85;'>"
    "Obs.: O dashboard usa <b>DATA INSTALAÇÃO ULTRONLINE</b> quando disponível; se ausente, usa <b>DATA PLANEJADA</b> como base de data. "
    "As cores e fontes são fixas no código para garantir consistência em qualquer computador."
    "</div>",
    unsafe_allow_html=True
)
