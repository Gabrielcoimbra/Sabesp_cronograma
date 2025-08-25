# streamlit_app.py
import io
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

# Plotly sem template para não herdar nada
pio.templates.default = None

st.set_page_config(page_title="Instalações 2Neuron | Sabesp", layout="wide")

# Fundo fixo (apenas layout; texto será definido inline nos elementos)
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

# ---------- Utils: Plotly -> PNG (imutável no cliente) ----------
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
        # fallback se kaleido faltar
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

# ============================================================
# DADOS (inventário técnico conhecido)
# ============================================================
inv_rows = [
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000287","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000270","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000282","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000283","GW000103"),
    ("EEE ETE LAVAPÉS","São José dos Campos","Trav. Constantino Pintus - Santana - SJC - SP - 12245-810","23°09'37.5\"S 45°52'09.4\"W","CLARO / VIVO","75","","94","440","","862","","","1","Inversor","U2N000269","GW000104"),
    ("EEE ETE LAVAPÉS","São José dos Campos","Trav. Constantino Pintus - Santana - SJC - SP - 12245-810","23°09'37.5\"S 45°52'09.4\"W","CLARO / VIVO","150","","188","440","","840","","","1","Inversor","U2N000288","GW000104"),
    ("EEE INTERLAGOS 3","São José dos Campos","Rua João Miacci - Pq. Interlagos - SJC - SP","23°16'33.1\"S 45°52'39.6\"W","CLARO / VIVO","75","","185","220","","1737","","","1","Soft Starter","U2N000278","GW000105"),
    ("EEE INTERLAGOS 2","São José dos Campos","Rua Alexandre Teodoro Eras - Pq. Interlagos - SJC - SP","23°16'25.1\"S 45°52'04.2\"W","CLARO / VIVO","40","","103","220","","1737","","","1","Soft Starter","U2N000286","GW000106"),
    ("EEE DAVIDE","São Paulo","Rua Davide Perez - Pedreira - São Paulo - SP - 04470-080","23°42'23.7\"S 46°39'13.3\"W","", "50","37","65","440","","1778","","12","1","Soft Starter","U2N000272","GW000108"),
    ("EEE DAVIDE","São Paulo","Rua Davide Perez - Pedreira - São Paulo - SP - 04470-080","", "50","37","65","440","","1778","","12","1","Soft Starter","U2N000285","GW000108"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000279","GW000110"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000268","GW000110"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000277","GW000110"),
    ("EEE IPORÃ","São Paulo","Estr. Ecoturística de Parelheiros - Jardim Iporã - São Paulo - SP - 04864-050","", "150","110","177,1","440","","1749","","","1","Soft Starter","U2N000271","GW000102"),
    ("EEE IPORÃ","São Paulo","Estr. Ecoturística de Parelheiros - Jardim Iporã - São Paulo - SP - 04864-050","", "150","110","177,1","440","","1749","","","1","Soft Starter","U2N000274","GW000102"),
    ("EEE VARGEM GRANDE","São Paulo","Rua Coqueiros - Vargem Grande - São Paulo - SP - 04896-260","", "120","90","145","440","","1770","","12","1","Soft Starter","U2N000275","GW000109"),
    ("EEE CAULIM","São Paulo","Av. Hideo Tiba - Sul Brasil - SP - 18180-000","", "83","61","240","440","","1750","","15","1","Soft Starter","U2N000276","GW000107"),
    ("EEE RIVIERA","São Paulo","Riviera - Bertioga - SP - 11262-015","", "180","132","211","440","","1760","","","1","Soft Starter","U2N000280","GW000111"),
    ("EEE RIVIERA","São Paulo","Riviera - Bertioga - SP - 11262-015","", "180","132","211","440","","1760","","","1","Soft Starter","U2N000281","GW000111"),
    ("EEE EUSÉBIO","Franco da Rocha","Av. Israel, 7A - Vila Bela - Franco da Rocha - SP - 07847-200","", "","200","312","440","","1180","","","2","Inversor","U2N000293","GW000112"),
    ("EEE ÁGUA PRETA 1","Pindamonhangaba","Est. Benedicta Amélia Baptista - Água Preta - Pinda - SP","", "45","","64","380","","1770","","","1","Soft Starter","U2N000311","GW000114"),
    ("EEE ÁGUA PRETA 1","Pindamonhangaba","Est. Benedicta Amélia Baptista - Água Preta - Pinda - SP","", "45","","64","380","","1770","","","1","Soft Starter","U2N000297","GW000114"),
    ("EEE CONVENTO","Tremembé","Rua Pindamonhangaba - Pq. das Araucárias - Tremembé - SP","", "85","","125","380","","1172","","","1","Soft Starter","U2N000307","GW000116"),
    ("EEE CONVENTO","Tremembé","Rua Pindamonhangaba - Pq. das Araucárias - Tremembé - SP","", "85","","125","380","","1172","","","1","Soft Starter","U2N000310","GW000116"),
    ("EEE DA PONTE","São Luiz do Paraitinga","Rua Pedro Cascardi - SLP - SP","", "23","","74","220","","1750","","","1","Soft Starter","U2N000300","GW000115"),
    ("EEE CRISTO","Ubatuba","Rua Raimundo Corrêa - Itaguá - Ubatuba - SP - 11688-622","", "100","","100","440","","1790","","","1","Inversor","U2N000295","GW000113"),
    ("EEE CRISTO","Ubatuba","Rua Raimundo Corrêa - Itaguá - Ubatuba - SP - 11688-622","", "100","","100","440","","1790","","","1","Inversor","U2N000290","GW000113"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","", "","75","125","440","","1173","","","1","Inversor","U2N000301","GW000118"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","", "","55","95","440","","1166","","","1","Inversor","U2N000304","GW000118"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","", "","55","98","440","","696","","","1","Inversor","U2N000309","GW000118"),
    ("EEE FINAL PORTO NOVO","Caraguatatuba","Rua Ângela Maria Ferreira e Santos - Barranco Alto - Caraguatatuba - SP - 11660-497","", "150","110","215","440","","1160","","","1","Inversor","U2N000312","GW000121"),
    ("EEE FINAL PORTO NOVO","Caraguatatuba","Rua Ângela Maria Ferreira e Santos - Barranco Alto - Caraguatatuba - SP - 11660-497","", "100","75","129","440","","1160","","","1","Inversor","U2N000298","GW000121"),
    ("EEE JARDIM IKEDA","Suzano","Rua Flores de Narciso - Jardim Ikeda - Suzano - SP - 08613-035","", "CLARO","","110","185,45","440","","1776","","","1","Inversor","U2N000308","Sem Gateway"),
    ("EEE PLANALTO","Suzano","Estr. da Boracéia - Jardim Ikeda - Suzano - SP - 08640-115","", "","132","211,2","440","","1776","","","1","Inversor","U2N000306","GW000120"),
    ("EEE SUZANO 1","Suzano","(não informado)","", "","","","","","","","","","","Inversor","U2N000302",""),
    ("EEE VILA RAMOS","Franco da Rocha","Praça Antônio Teixeira - Vila Ramos - Franco da Rocha - SP - 07859-340","", "60","45","88","380","","1775","","","1","Inversor","U2N000292","GW000119"),
    ("EEE VILA RAMOS","Franco da Rocha","Praça Antônio Teixeira - Vila Ramos - Franco da Rocha - SP - 07859-340","", "60","","82","380","","1775","","","1","Inversor","U2N000305","GW000119"),
]
df_inv = pd.DataFrame(inv_rows, columns=[
    "Local","Cidade","Endereço","Coordenadas","Operadora","Potência (cv)","Potência (kW)","Corrente (A)","Tensão (V)",
    "Relação TP","Rotação (RPM)","Seção Cabo (mm²)","Diâm. externo (mm)","Cabos/fase","Acionamento","Série","Gateway"
])
series_offline = {"U2N000277","U2N000308"}
df_inv["Online"] = ~df_inv["Série"].isin(series_offline)

# ============================================================
# CRONOGRAMA (11/08 a 25/08) — agora com 25/08 Guarujá
# ============================================================
registros = [
    {"data":"2025-08-11","cidade":"São Paulo","local":"EEE Alvarenga Mãe","ultronlines":4,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000283 (TC 35→24 mm), U2N000282 (com gateway), U2N000287, U2N000270."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"EEE Lavapés","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000269 e U2N000288; conexões confirmadas."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"Interlagos 3","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000278; problema de alimentação resolvido."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"Interlagos 2","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000286; conectado e funcionando."},
    {"data":"2025-08-13","cidade":"São Paulo","local":"EEE Davide","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000272, U2N000285 (272 ficou desligado inicialmente)."},
    {"data":"2025-08-13","cidade":"São Paulo","local":"EEE Talamanca","ultronlines":3,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000268, U2N000277 (instalado e desligado; aguardando nova bomba), U2N000279."},
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Iporã","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 4; 1 bomba inexistente e 1 em manutenção (instalados U2N000271 e U2N000274)."},
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Vargem Grande (G2)","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 2; G1 em manutenção (instalado U2N000275)."},
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Caulim","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 4 (corrigido p/2); um vandalizado (instalado U2N000276)."},
    {"data":"2025-08-15","cidade":"—","local":"EEE Riviera","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000280 e U2N000281."},
    {"data":"2025-08-15","cidade":"Franco da Rocha","local":"EEE Eusébio","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000293; elevatória com 1 bomba."},
    {"data":"2025-08-18","cidade":"Pindamonhangaba","local":"EEE Água Preta 1","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000311 e U2N000297 (U2N000284 com defeito para troca)."},
    {"data":"2025-08-18","cidade":"Tremembé","local":"EEE Convento","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000307 (sem bomba no momento) e U2N000310."},
    {"data":"2025-08-18","cidade":"São Luiz do Paraitinga","local":"EEE da Ponte","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000300."},
    {"data":"2025-08-19","cidade":"Ubatuba","local":"EEE Cristo","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000295 e U2N000290 (previstos 3; instalados 2)."},
    {"data":"2025-08-20","cidade":"Caraguatatuba","local":"EEE Final Porto Novo","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000298 e U2N000312."},
    {"data":"2025-08-20","cidade":"Caraguatatuba","local":"EEE Tinga Poiares","ultronlines":3,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000301, U2N000304, U2N000309."},
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Jardim Ikeda","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000308 instalado, mas sem gateway (sinal Vivo ruim). Sabesp sugeriu Claro. ⇒ offline."},
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Planalto","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000306 (previstos 2; ficou 1)."},
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Suzano 1","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000302 (ponto realocado)."},
    {"data":"2025-08-22","cidade":"Franco da Rocha","local":"EEE Vila Ramos","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000292 e U2N000305."},
    # ---- Novos (25/08) ----
    {"data":"2025-08-25","cidade":"Guarujá","local":"EEE Enseada","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos: U2N000291 e U2N000289 (GW000124)."},
    {"data":"2025-08-25","cidade":"Guarujá","local":"EEE Morrinhos Central","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previsto: U2N000299 (GW000122)."},
    {"data":"2025-08-25","cidade":"Guarujá","local":"EEE Maluf","ultronlines":0,"ultronlinks":0,"gateways_extra":0,
     "obs":"Sem séries informadas no quadro; aguardando confirmação."},
]
df = pd.DataFrame(registros)
df["data"] = pd.to_datetime(df["data"])

# Mapa de datas por série (para inventário/visão série x data)
date_map = {
    "U2N000283":"2025-08-11","U2N000282":"2025-08-11","U2N000287":"2025-08-11","U2N000270":"2025-08-11",
    "U2N000269":"2025-08-12","U2N000288":"2025-08-12","U2N000278":"2025-08-12","U2N000286":"2025-08-12",
    "U2N000272":"2025-08-13","U2N000285":"2025-08-13","U2N000268":"2025-08-13","U2N000277":"2025-08-13","U2N000279":"2025-08-13",
    "U2N000271":"2025-08-14","U2N000274":"2025-08-14","U2N000275":"2025-08-14","U2N000276":"2025-08-14",
    "U2N000280":"2025-08-15","U2N000281":"2025-08-15","U2N000293":"2025-08-15",
    "U2N000311":"2025-08-18","U2N000297":"2025-08-18","U2N000307":"2025-08-18","U2N000310":"2025-08-18","U2N000300":"2025-08-18",
    "U2N000295":"2025-08-19","U2N000290":"2025-08-19",
    "U2N000298":"2025-08-20","U2N000312":"2025-08-20","U2N000301":"2025-08-20","U2N000304":"2025-08-20","U2N000309":"2025-08-20",
    "U2N000308":"2025-08-21","U2N000306":"2025-08-21","U2N000302":"2025-08-21",
    "U2N000292":"2025-08-22","U2N000305":"2025-08-22",
    # Séries de 25/08 ainda não cadastradas no inventário técnico acima:
    # "U2N000291":"2025-08-25","U2N000289":"2025-08-25","U2N000299":"2025-08-25",
}
df_series = (
    df_inv[["Série","Cidade","Local","Gateway"]]
    .assign(Data=lambda x: x["Série"].map(date_map),
            Online=lambda x: ~x["Série"].isin(series_offline))
)
df_series["Data"] = pd.to_datetime(df_series["Data"], errors="coerce")

TOTAL_INSTALADOS = len(df_series)                 # segue 37 (inventário conhecido)
TOTAL_ONLINE     = int(df_series["Online"].sum()) # 35
TOTAL_OFFLINE    = TOTAL_INSTALADOS - TOTAL_ONLINE # 2

# =========================
# Cabeçalho e KPIs
# =========================
st.markdown(
    f"""
    <div style="color:{COR_TXT} !important;">
      <h1 style="margin:0 0 6px 0; font-size:44px; line-height:1.15; font-weight:800; color:{COR_TXT} !important;">
        Instalações 2Neuron na Sabesp (11–25/Ago/2025)
      </h1>
      <div style="opacity:.9; margin:0 0 18px 0; font-size:15px; color:{COR_TXT} !important;">
        Cronograma consolidado (inclui planejados até 25/08) e inventário técnico conhecido: {TOTAL_INSTALADOS} instalados, {TOTAL_ONLINE} online e {TOTAL_OFFLINE} offline.
      </div>

      <div style="display:flex; gap:28px; flex-wrap:wrap;">
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Instalados (inventário)</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{TOTAL_INSTALADOS}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Online</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{TOTAL_ONLINE}</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E9E9EF; border-radius:12px; padding:14px 18px; min-width:220px;">
          <div style="font-size:13px; opacity:.75; margin-bottom:6px; color:{COR_TXT} !important;">Offline</div>
          <div style="font-size:36px; font-weight:700; color:{COR_TXT} !important;">{TOTAL_OFFLINE}</div>
          <div style="font-size:12px; opacity:.7; margin-top:2px; color:{COR_TXT} !important;">277 (Talamanca) e 308 (Jardim Ikeda)</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Gráficos (PNG)
# =========================
dia = (df.groupby("data", as_index=False)["ultronlines"].sum()
         .rename(columns={"ultronlines":"ultronlines_dia"}))
dia["data_str"] = dia["data"].dt.strftime("%d/%m/%Y")
dia_sorted = dia.sort_values("data")
dia_sorted["acumulado"] = dia_sorted["ultronlines_dia"].cumsum()

cidade_dist = (df_inv.groupby("Cidade", as_index=False)["Série"].count()
               .rename(columns={"Série":"Ultronlines"}))

def fig_barras_por_dia():
    fig = go.Figure(go.Bar(
        x=dia_sorted["data_str"], y=dia_sorted["ultronlines_dia"],
        text=dia_sorted["ultronlines_dia"], textposition="auto",
        marker=dict(color=COR_PRI, line=dict(color=AXIS, width=0))
    ))
    fig.update_layout(title="Ultronlines (cronograma) por dia",
                      xaxis_title="Data", yaxis_title="Quantidade", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_acumulado():
    fig = go.Figure(go.Scatter(
        x=dia_sorted["data_str"], y=dia_sorted["acumulado"],
        mode="lines+markers", line=dict(width=3, color=COR_SEC),
        marker=dict(size=8, color=COR_SEC)
    ))
    fig.update_layout(title="Acumulado (cronograma) de Ultronlines",
                      xaxis_title="Data", yaxis_title="Acumulado", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_cidade():
    colors = [cores_2neuron[i % len(cores_2neuron)] for i in range(len(cidade_dist))]
    fig = go.Figure(go.Bar(
        x=cidade_dist["Cidade"], y=cidade_dist["Ultronlines"],
        text=cidade_dist["Ultronlines"], textposition="auto",
        marker=dict(color=colors)
    ))
    fig.update_layout(title="Distribuição por Cidade (inventário técnico)",
                      xaxis_title="Cidade", yaxis_title="Ultronlines", **BASE_LAYOUT)
    axes_style(fig); return fig

def fig_status():
    fig = go.Figure(go.Pie(
        labels=["Online","Offline"], values=[TOTAL_ONLINE, TOTAL_OFFLINE],
        marker=dict(colors=[COR_PRI, COR_ALERTA]), hole=0.5, sort=False,
        textfont=dict(color=COR_TXT, family=BASE_FONT)
    ))
    fig.update_layout(title=f"Status dos Ultronlines (inventário: {TOTAL_INSTALADOS})", **BASE_LAYOUT)
    return fig

g1, g2 = st.columns(2)
with g1: show(fig_barras_por_dia())
with g2: show(fig_acumulado())

g3, g4 = st.columns(2)
with g3: show(fig_cidade())
with g4: show(fig_status(), height=430)

# =========================
# Tabelas (PNG)
# =========================
df_crono = (df[["data","cidade","local","ultronlines","ultronlinks","gateways_extra","obs"]]
            .sort_values(["data","cidade","local"])
            .rename(columns={"data":"Data","cidade":"Cidade","local":"Local",
                             "ultronlines":"Ultronlines","ultronlinks":"Ultronlinks",
                             "gateways_extra":"Gateways extra","obs":"Observações"}))
table_png(df_crono, "Detalhamento diário (cronograma até 25/08)")

df_series_view = (df_series
                  .sort_values(["Online","Data","Série"], ascending=[False, True, True])
                  .assign(Status=lambda x: x["Online"].map({True:"Online", False:"Offline"}))
                  [["Série","Status","Data","Cidade","Local","Gateway"]])
table_png(df_series_view, "Séries instaladas e status (inventário técnico)")

df_inv_view = (df_inv.rename(columns={
    "Potência (cv)":"Pot (cv)","Potência (kW)":"Pot (kW)","Corrente (A)":"Corr (A)",
    "Tensão (V)":"Tensão (V)","Rotação (RPM)":"RPM","Seção Cabo (mm²)":"Seção (mm²)",
    "Diâm. externo (mm)":"Diâm (mm)","Cabos/fase":"Cabos/fase"
})[["Local","Cidade","Série","Gateway","Operadora","Acionamento","Pot (cv)","Pot (kW)","Corr (A)","Tensão (V)","RPM","Seção (mm²)","Diâm (mm)","Cabos/fase","Endereço","Coordenadas","Online"]])
table_png(df_inv_view, "Inventário técnico (campos principais)")

# Observação final (HTML inline)
st.markdown(
    f"<div style='color:{COR_TXT} !important; opacity:.85;'>"
    "Cronograma inclui Guarujá em 25/08 (Enseada ×2, Morrinhos Central ×1; Maluf aguardando séries). "
    "Inventário técnico permanece com 37 séries cadastradas."
    "</div>",
    unsafe_allow_html=True
)
