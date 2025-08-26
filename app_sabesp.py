# app_sabesp.py
# Lê EXATAMENTE: ./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx
# Plota 1 gráfico: Ultronlines instalados por dia (MÓDULO distinto por DATA INSTALAÇÃO ULTRONLINE)

import os, unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

# ---- desativa/limpa qualquer resquício de cache (por segurança) ----
try:
    st.cache_data.clear()
    st.cache_resource.clear()
except Exception:
    pass

st.set_page_config(page_title="Teste — Excel + 1 gráfico", layout="wide")
st.title("Teste: leitura do Excel + 1 gráfico")

# -------- caminho EXATO do arquivo --------
EXCEL_PATH = "./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx"

# -------- checagens simples --------
if not os.path.exists(EXCEL_PATH):
    st.error(f"Arquivo não encontrado na raiz: {EXCEL_PATH}")
    st.stop()

# -------- engine obrigatório para .xlsx/.xlsm --------
try:
    import openpyxl  # garante presença do pacote
except Exception as e:
    st.error(
        "Pacote **openpyxl** não está instalado e é necessário para ler .xlsx.\n"
        "No requirements.txt inclua:  openpyxl\n"
        "Ou instale localmente:       pip install openpyxl\n\n"
        f"Detalhe: {e}"
    )
    st.stop()

# -------- ler excel (primeira planilha) COM ENGINE EXPLÍCITO --------
try:
    df_raw = pd.read_excel(EXCEL_PATH, engine="openpyxl")
except Exception as e:
    st.error(f"Falha ao ler o Excel com openpyxl: {e}")
    st.stop()

# -------- normalizar nomes de colunas --------
def norm_col(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ASCII", "ignore").decode("ASCII")
    return " ".join(c.replace("\n"," ").replace("\r"," ").split()).upper()

df = df_raw.rename(columns={c: norm_col(c) for c in df_raw.columns}).copy()

# -------- identificar colunas necessárias --------
COL_MOD  = next((c for c in ["MÓDULO","MODULO","SERIE","SÉRIE","MÓDULO/ SÉRIE","SERIE/MODULO"] if c in df.columns), None)
COL_DATA = next((c for c in ["DATA INSTALAÇÃO ULTRONLINE","DATA INSTALACAO ULTRONLINE","DATA INSTALAÇÃO","DATA INSTALACAO"] if c in df.columns), None)

if COL_MOD is None or COL_DATA is None:
    st.error(
        "Colunas obrigatórias não encontradas após normalização.\n"
        "Necessárias: MÓDULO e DATA INSTALAÇÃO ULTRONLINE (ou aliases).\n\n"
        "Colunas disponíveis:\n- " + "\n- ".join(df.columns)
    )
    st.stop()

# -------- preparar dados --------
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce")
base = df.dropna(subset=[COL_MOD, COL_DATA]).drop_duplicates(subset=[COL_MOD, COL_DATA])

agg = (
    base.groupby(COL_DATA, as_index=False)[COL_MOD]
        .nunique()
        .rename(columns={COL_DATA: "DATA", COL_MOD: "INSTALADOS_DIA"})
        .sort_values("DATA")
)
agg["DATA_STR"] = agg["DATA"].dt.strftime("%d/%m/%Y")

# -------- 1 gráfico --------
fig = px.bar(
    agg, x="DATA_STR", y="INSTALADOS_DIA",
    title="Ultronlines instalados por dia (dados da planilha)",
    labels={"DATA_STR": "Data de instalação", "INSTALADOS_DIA": "Qtd (módulos distintos)"},
    text="INSTALADOS_DIA"
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# (opcional) visualizar primeiras linhas para confirmar leitura
with st.expander("Ver primeiras linhas da planilha (normalizada)"):
    st.dataframe(df.head(20), use_container_width=True)
