# app_sabesp.py
import os
import unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

# Limpar cache
try:
    st.cache_data.clear()
    st.cache_resource.clear()
except Exception:
    pass

st.set_page_config(page_title="Diagnóstico Excel + Gráfico", layout="wide")
st.title("🔧 Diagnóstico: leitura do Excel")

# --- PASSO 1: Listar arquivos no diretório ---
st.subheader("1. Arquivos no diretório atual")
try:
    arquivos = os.listdir(".")
    st.write(arquivos)
    xlsx_files = [f for f in arquivos if f.lower().endswith(".xlsx")]
    st.info(f"Arquivos .xlsx encontrados: {xlsx_files}")
except Exception as e:
    st.error(f"Erro ao listar arquivos: {e}")

# --- PASSO 2: Definir caminho ---
EXCEL_PATH = "./SABESP_Ultronline.xlsx"  # ← Mude se o nome for diferente
st.subheader("2. Procurando arquivo")
st.write(f"Procurando: `{EXCEL_PATH}`")

if not os.path.exists(EXCEL_PATH):
    st.error(f"❌ Arquivo não encontrado: `{EXCEL_PATH}`")
    st.stop()
else:
    st.success(f"✅ Arquivo encontrado: `{EXCEL_PATH}`")

# --- PASSO 3: Verificar openpyxl ---
st.subheader("3. Verificando openpyxl")
try:
    import openpyxl
    st.success("✅ openpyxl importado com sucesso")
except ImportError as e:
    st.error(f"""
    ❌ Falta o pacote `openpyxl`.

    Adicione ao `requirements.txt`:
    ```
    openpyxl
    ```
    Erro: {e}
    """)
    st.stop()

# --- PASSO 4: Ler Excel ---
st.subheader("4. Tentando ler o Excel")
try:
    df_raw = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    st.success(f"✅ Excel lido com sucesso! ({len(df_raw)} linhas)")
    st.session_state['df_raw'] = df_raw  # opcional: guardar
except Exception as e:
    st.error(f"""
    ❌ Falha ao ler o Excel:

    - Verifique se o arquivo é um `.xlsx` válido
    - Pode estar corrompido
    - Ou tem planilha protegida

    Erro: `{e}`
    """)
    st.stop()

# --- PASSO 5: Normalizar colunas ---
st.subheader("5. Colunas encontradas")
def norm_col(c: str) -> str:
    c = unicodedata.normalize("NFKD", c).encode("ASCII", "ignore").decode("ASCII")
    return " ".join(c.replace("\n", " ").replace("\r", " ").split()).upper()

df = df_raw.rename(columns={col: norm_col(str(col)) for col in df_raw.columns}).copy()
st.write("Colunas normalizadas:", list(df.columns))

# --- PASSO 6: Procurar colunas chave ---
COL_MOD = next((c for c in ["MODULO", "SERIE", "SERIE/MODULO", "MÓDULO", "SÉRIE"] if c in df.columns), None)
COL_DATA = next((c for c in [
    "DATA INSTALACAO ULTRONLINE",
    "DATA INSTALACAO",
    "DATA INSTALACAO ULTRONLINE",
    "DATA INSTALACAO ULTRONLINE"
] if c in df.columns), None)

if not COL_MOD:
    st.warning("⚠️ Coluna de MÓDULO não encontrada")
if not COL_DATA:
    st.warning("⚠️ Coluna de DATA não encontrada")

if not COL_MOD or not COL_DATA:
    st.error("❌ Não foi possível identificar colunas necessárias.")
    st.stop()
else:
    st.success(f"✅ Usando: Módulo='{COL_MOD}', Data='{COL_DATA}'")

# --- PASSO 7: Preparar dados ---
try:
    df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce")
    base = df.dropna(subset=[COL_MOD, COL_DATA]).drop_duplicates(subset=[COL_MOD, COL_DATA])

    agg = (base.groupby(COL_DATA, as_index=False)[COL_MOD]
           .nunique()
           .rename(columns={COL_DATA: "DATA", COL_MOD: "INSTALADOS_DIA"})
           .sort_values("DATA"))
    agg["DATA_STR"] = agg["DATA"].dt.strftime("%d/%m/%Y")

    # --- Gráfico ---
    st.subheader("6. Gráfico: Ultronlines instalados por dia")
    fig = px.bar(
        agg,
        x="DATA_STR",
        y="INSTALADOS_DIA",
        title="Ultronlines instalados por dia",
        labels={"DATA_STR": "Data", "INSTALADOS_DIA": "Módulos distintos"},
        text="INSTALADOS_DIA"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # --- Exibir dados ---
    with st.expander("Ver dados brutos (primeiras 20 linhas)"):
        st.dataframe(df.head(20), use_container_width=True)

except Exception as e:
    st.error(f"Erro no processamento: {e}")
