bora zerar mesmo — aqui vai um **app Streamlit mínimo** que **só**:

1. lê **exatamente** `./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx`
2. plota **um único gráfico**: Ultronlines instalados por dia (contando **MÓDULO** distinto por `DATA INSTALAÇÃO ULTRONLINE`)

> `requirements.txt`: `streamlit`, `pandas`, `plotly`, `openpyxl`

```python
# app_min.py
import os, unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Teste rápido — leitura + 1 gráfico", layout="wide")
st.title("Teste: leitura do Excel + 1 gráfico")

# === caminho EXATO do arquivo ===
EXCEL_PATH = "./SABESP - Gestão Contrato Sabesp 00248-25 - 112 Ultronline (3).xlsx"

# --- checagens básicas ---
if not os.path.exists(EXCEL_PATH):
    st.error(f"Arquivo não encontrado na raiz: {EXCEL_PATH}")
    st.stop()

try:
    import openpyxl  # engine para .xlsx
except Exception as e:
    st.error(
        "Pacote `openpyxl` ausente. Adicione ao requirements.txt ou instale: pip install openpyxl\n"
        f"Detalhe: {e}"
    )
    st.stop()

# --- ler excel (primeira planilha) ---
try:
    df_raw = pd.read_excel(EXCEL_PATH, engine="openpyxl")
except Exception as e:
    st.error(f"Falha ao ler o Excel com openpyxl: {e}")
    st.stop()

# --- normalizar nomes de colunas ---
def norm_col(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ASCII", "ignore").decode("ASCII")
    return " ".join(c.replace("\n"," ").replace("\r"," ").split()).upper()

df = df_raw.rename(columns={c: norm_col(c) for c in df_raw.columns}).copy()

# --- localizar colunas (aliases) ---
COL_MOD  = next((c for c in ["MÓDULO","MODULO","SERIE","SÉRIE","MÓDULO/ SÉRIE","SERIE/MODULO"] if c in df.columns), None)
COL_DATA = next((c for c in ["DATA INSTALAÇÃO ULTRONLINE","DATA INSTALACAO ULTRONLINE","DATA INSTALAÇÃO","DATA INSTALACAO"] if c in df.columns), None)

if COL_MOD is None or COL_DATA is None:
    st.error(
        "Colunas obrigatórias não encontradas na planilha após normalização.\n"
        f"Necessárias: MÓDULO (ou aliases) e DATA INSTALAÇÃO ULTRONLINE (ou aliases).\n\n"
        f"Colunas disponíveis: {', '.join(df.columns)}"
    )
    st.stop()

# --- preparar dados ---
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce")
df = df.dropna(subset=[COL_MOD, COL_DATA])

# contar módulos distintos por dia
agg = (
    df.drop_duplicates(subset=[COL_MOD, COL_DATA])
      .groupby(COL_DATA, as_index=False)[COL_MOD]
      .nunique()
      .rename(columns={COL_DATA:"DATA", COL_MOD:"INSTALADOS_DIA"})
      .sort_values("DATA")
)
agg["DATA_STR"] = agg["DATA"].dt.strftime("%d/%m/%Y")

# --- 1 gráfico (somente) ---
fig = px.bar(agg, x="DATA_STR", y="INSTALADOS_DIA", title="Ultronlines instalados por dia (teste)")
st.plotly_chart(fig, use_container_width=True)
```

Se isso rodar, a leitura está ok. Depois a gente incrementa o dash.
