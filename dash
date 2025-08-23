import pandas as pd
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
import plotly.graph_objects as go
import webbrowser
from threading import Timer

# =========================
# Paleta 2Neuron
# =========================
cores_2neuron = ['#6A0DAD', '#8A2BE2', '#9370DB', '#D8BFD8', '#4B0082']
COR_BG = "#F8F8FF"
COR_TXT = "#2D2D2D"
COR_PRI = cores_2neuron[0]
COR_SEC = cores_2neuron[1]

# ============================================================
# INVENTÁRIO TÉCNICO (37 instalados) — baseado na planilha enviada
# (campos simplificados: preencha mais se quiser)
# ============================================================
inv_rows = [
    # Local, Cidade, Endereço, Coordenadas, Operadora, Pot(cv), Pot(kW), Corr(A), Tensão(V), Rotação(RPM), Seção(mm²), Diâm(mm), Nº cabos/fase, Acionamento, Módulo, Gateway
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000287","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000270","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000282","GW000103"),
    ("EEE ALVARENGA MÃE","São Paulo","Praça Clóvis Beviláqua - Glicério - São Paulo - SP - 01018-001","23°41'43.5\"S 46°39'06.2\"W","", "120","88","145","440","","1764","","22","1","Soft Starter","U2N000283","GW000103"),
    ("EEE ETE LAVAPÉS","São José dos Campos","Trav. Constantino Pintus - Santana - SJC - SP - 12245-810","23°09'37.5\"S 45°52'09.4\"W","CLARO / VIVO","75","","94","440","","862","","","1","Inversor","U2N000269","GW000104"),
    ("EEE ETE LAVAPÉS","São José dos Campos","Trav. Constantino Pintus - Santana - SJC - SP - 12245-810","23°09'37.5\"S 45°52'09.4\"W","CLARO / VIVO","150","","188","440","","840","","","1","Inversor","U2N000288","GW000104"),
    ("EEE INTERLAGOS 3","São José dos Campos","Rua João Miacci - Pq. Interlagos - SJC - SP","23°16'33.1\"S 45°52'39.6\"W","CLARO / VIVO","75","","185","220","","1737","","","1","Soft Starter","U2N000278","GW000105"),
    ("EEE INTERLAGOS 2","São José dos Campos","Rua Alexandre Teodoro Eras - Pq. Interlagos - SJC - SP","23°16'25.1\"S 45°52'04.2\"W","CLARO / VIVO","40","","103","220","","1737","","","1","Soft Starter","U2N000286","GW000106"),
    ("EEE DAVIDE","São Paulo","Rua Davide Perez - Pedreira - São Paulo - SP - 04470-080","23°42'23.7\"S 46°39'13.3\"W","", "50","37","65","440","","1778","","12","1","Soft Starter","U2N000272","GW000108"),
    ("EEE DAVIDE","São Paulo","Rua Davide Perez - Pedreira - São Paulo - SP - 04470-080","23°42'23.7\"S 46°39'13.3\"W","", "50","37","65","440","","1778","","12","1","Soft Starter","U2N000285","GW000108"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","23°41'26.9\"S 46°44'57.0\"W","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000279","GW000110"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","23°41'26.9\"S 46°44'57.0\"W","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000268","GW000110"),
    ("EEE TALAMANCA","São Paulo","Rua Talamanca - Jardim São Luís - São Paulo - SP - 04917-080","23°41'26.9\"S 46°44'57.0\"W","", "250","183","324","440","","1750","","","2","Soft Starter","U2N000277","GW000110"),
    ("EEE IPORÃ","São Paulo","Estr. Ecoturística de Parelheiros - Jardim Iporã - São Paulo - SP - 04864-050","23°46'51.6\"S 46°43'30.2\"W","", "150","110","177,1","440","","1749","","","1","Soft Starter","U2N000271","GW000102"),
    ("EEE IPORÃ","São Paulo","Estr. Ecoturística de Parelheiros - Jardim Iporã - São Paulo - SP - 04864-050","23°46'51.6\"S 46°43'30.2\"W","", "150","110","177,1","440","","1749","","","1","Soft Starter","U2N000274","GW000102"),
    ("EEE VARGEM GRANDE","São Paulo","Rua Coqueiros - Vargem Grande - São Paulo - SP - 04896-260","23°51'48.1\"S 46°42'25.3\"W","", "120","90","145","440","","1770","","12","1","Soft Starter","U2N000275","GW000109"),
    ("EEE CAULIM","São Paulo","Av. Hideo Tiba - Sul Brasil - SP - 18180-000","23°47'35.9\"S 46°43'49.7\"W","", "83","61","240","440","","1750","","15","1","Soft Starter","U2N000276","GW000107"),
    ("EEE RIVIERA","São Paulo","Riviera - Bertioga - SP - 11262-015","23°41'53.6\"S 46°45'21.2\"W","", "180","132","211","440","","1760","","","1","Soft Starter","U2N000280","GW000111"),
    ("EEE RIVIERA","São Paulo","Riviera - Bertioga - SP - 11262-015","23°41'53.6\"S 46°45'21.2\"W","", "180","132","211","440","","1760","","","1","Soft Starter","U2N000281","GW000111"),
    ("EEE EUSÉBIO","Franco da Rocha","Av. Israel, 7A - Vila Bela - Franco da Rocha - SP - 07847-200","23°19'57.7\"S 46°43'40.6\"W","", "","200","312","440","","1180","","","2","Inversor","U2N000293","GW000112"),
    ("EEE ÁGUA PRETA 1","Pindamonhangaba","Est. Benedicta Amélia Baptista - Água Preta - Pinda - SP","22°54'45.2\"S 45°25'22.2\"W","CLARO / VIVO","45","","64","380","","1770","","","1","Soft Starter","U2N000311","GW000114"),
    ("EEE ÁGUA PRETA 1","Pindamonhangaba","Est. Benedicta Amélia Baptista - Água Preta - Pinda - SP","22°54'45.2\"S 45°25'22.2\"W","CLARO / VIVO","45","","64","380","","1770","","","1","Soft Starter","U2N000297","GW000114"),
    ("EEE CONVENTO","Tremembé","Rua Pindamonhangaba - Pq. das Araucárias - Tremembé - SP","-22.990850, -45.553036","CLARO / VIVO","85","","125","380","","1172","","","1","Soft Starter","U2N000307","GW000116"),
    ("EEE CONVENTO","Tremembé","Rua Pindamonhangaba - Pq. das Araucárias - Tremembé - SP","-22.990850, -45.553036","CLARO / VIVO","85","","125","380","","1172","","","1","Soft Starter","U2N000310","GW000116"),
    ("EEE DA PONTE","São Luiz do Paraitinga","Rua Pedro Cascardi - SLP - SP","-23.236783, -45.305113","CLARO / VIVO","23","","74","220","","1750","","","1","Soft Starter","U2N000300","GW000115"),
    ("EEE CRISTO","Ubatuba","Rua Raimundo Corrêa - Itaguá - Ubatuba - SP - 11688-622","23°27'19.3\"S 45°04'00.6\"W","CLARO / VIVO","100","","100","440","","1790","","","1","Inversor","U2N000295","GW000113"),
    ("EEE CRISTO","Ubatuba","Rua Raimundo Corrêa - Itaguá - Ubatuba - SP - 11688-622","23°27'19.3\"S 45°04'00.6\"W","CLARO / VIVO","100","","100","440","","1790","","","1","Inversor","U2N000290","GW000113"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","23°38'19.1\"S 45°26'15.6\"W","CLARO / VIVO","","75","125","440","","1173","","","1","Inversor","U2N000301","GW000118"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","23°38'19.1\"S 45°26'15.6\"W","CLARO / VIVO","","55","95","440","","1166","","","1","Inversor","U2N000304","GW000118"),
    ("EEE TINGA POIARES","Caraguatatuba","Av. Mal. Floriano Peixoto - Poiares - Caraguatatuba - SP - 11660-497","23°38'19.1\"S 45°26'15.6\"W","CLARO / VIVO","","55","98","440","","696","","","1","Inversor","U2N000309","GW000118"),
    ("EEE FINAL PORTO NOVO","Caraguatatuba","Rua Ângela Maria Ferreira e Santos - Barranco Alto - Caraguatatuba - SP - 11660-497","23°38'19.1\"S 45°26'15.6\"W","CLARO / VIVO","150","110","215","440","","1160","","","1","Inversor","U2N000312","GW000121"),
    ("EEE FINAL PORTO NOVO","Caraguatatuba","Rua Ângela Maria Ferreira e Santos - Barranco Alto - Caraguatatuba - SP - 11660-497","23°38'19.1\"S 45°26'15.6\"W","CLARO / VIVO","100","75","129","440","","1160","","","1","Inversor","U2N000298","GW000121"),
    ("EEE JARDIM IKEDA","Suzano","Rua Flores de Narciso - Jardim Ikeda - Suzano - SP - 08613-035","","CLARO","","110","185,45","440","","1776","","","1","Inversor","U2N000308","Sem Gateway"),
    ("EEE PLANALTO","Suzano","Estr. da Boracéia - Jardim Ikeda - Suzano - SP - 08640-115","23°38'05.9\"S 46°19'17.3\"","","","132","211,2","440","","1776","","","1","Inversor","U2N000306","GW000120"),
    ("EEE SUZANO 1","Suzano","(não informado)","","","","","","","","","","","Inversor","U2N000302",""),
    ("EEE VILA RAMOS","Franco da Rocha","Praça Antônio Teixeira - Vila Ramos - Franco da Rocha - SP - 07859-340","23°19'57.9\"S 46°42'44.3\"W","","60","45","88","380","","1775","","","1","Inversor","U2N000292","GW000119"),
    ("EEE VILA RAMOS","Franco da Rocha","Praça Antônio Teixeira - Vila Ramos - Franco da Rocha - SP - 07859-340","23°19'57.9\"S 46°42'44.3\"W","","60","","82","380","","1775","","","1","Inversor","U2N000305","GW000119"),
]
df_inv = pd.DataFrame(inv_rows, columns=[
    "Local","Cidade","Endereço","Coordenadas","Operadora","Potência (cv)","Potência (kW)","Corrente (A)","Tensão (V)",
    "Relação TP","Rotação (RPM)","Seção Cabo (mm²)","Diâm. externo (mm)","Cabos/fase","Acionamento","Série","Gateway"
])

# Status online/offline
series_offline = {"U2N000277","U2N000308"}
df_inv["Online"] = ~df_inv["Série"].isin(series_offline)

# ============================================================
# CRONOGRAMA (37 instalados) — corrigido
# 11/08 = 4 (inclui 270); 12/08 = 4 (sem duplicar 269)
# ============================================================
registros = [
    # 11/08 — 4
    {"data":"2025-08-11","cidade":"São Paulo","local":"EEE Alvarenga Mãe","ultronlines":4,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000283 (TC 35→24 mm), U2N000282 (ligado c/ gateway), U2N000287, U2N000270."},

    # 12/08 — 4
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"EEE Lavapés","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000269 e U2N000288; conexões confirmadas."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"Interlagos 3","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000278; problema de alimentação resolvido."},
    {"data":"2025-08-12","cidade":"São José dos Campos","local":"Interlagos 2","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000286; conectado e funcionando."},

    # 13/08 — 5
    {"data":"2025-08-13","cidade":"São Paulo","local":"EEE Davide","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000272, U2N000285 (272 ficou desligado inicialmente)."},
    {"data":"2025-08-13","cidade":"São Paulo","local":"EEE Talamanca","ultronlines":3,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000268, U2N000277 (instalado e desligado; aguardando nova bomba), U2N000279."},

    # 14/08 — 4
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Iporã","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 4; 1 bomba inexistente e 1 em manutenção (instalados U2N000271 e U2N000274)."},
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Vargem Grande (G2)","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 2; G1 em manutenção (instalado U2N000275)."},
    {"data":"2025-08-14","cidade":"São Paulo","local":"EEE Caulim","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"Previstos 4 (corrigido p/2); um vandalizado (instalado U2N000276)."},

    # 15/08 — 3
    {"data":"2025-08-15","cidade":"—","local":"EEE Riviera","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000280 e U2N000281."},
    {"data":"2025-08-15","cidade":"Franco da Rocha","local":"EEE Eusébio","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000293; elevatória com 1 bomba."},

    # 18/08 — 5
    {"data":"2025-08-18","cidade":"Pindamonhangaba","local":"EEE Água Preta 1","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000311 e U2N000297 (U2N000284 com defeito para troca)."},
    {"data":"2025-08-18","cidade":"Tremembé","local":"EEE Convento","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000307 (sem bomba no momento) e U2N000310."},
    {"data":"2025-08-18","cidade":"São Luiz do Paraitinga","local":"EEE da Ponte","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000300."},

    # 19/08 — 2
    {"data":"2025-08-19","cidade":"Ubatuba","local":"EEE Cristo","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000295 e U2N000290 (previstos 3; instalados 2)."},

    # 20/08 — 5
    {"data":"2025-08-20","cidade":"Caraguatatuba","local":"EEE Final Porto Novo","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000298 e U2N000312."},
    {"data":"2025-08-20","cidade":"Caraguatatuba","local":"EEE Tinga Poiares","ultronlines":3,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000301, U2N000304, U2N000309."},

    # 21/08 — 3
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Jardim Ikeda","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000308 instalado, mas sem gateway (sinal Vivo ruim). Sabesp sugeriu Claro. ⇒ offline."},
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Planalto","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000306 (previstos 2; ficou 1)."},
    {"data":"2025-08-21","cidade":"Suzano","local":"EEE Suzano 1","ultronlines":1,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000302 (ponto realocado)."},

    # 22/08 — 2
    {"data":"2025-08-22","cidade":"Franco da Rocha","local":"EEE Vila Ramos","ultronlines":2,"ultronlinks":0,"gateways_extra":0,
     "obs":"U2N000292 e U2N000305."},
]
df = pd.DataFrame(registros)
df["data"] = pd.to_datetime(df["data"])

# ============================================================
# SÉRIES / STATUS / DATAS
# (datas associadas conforme cronograma)
# ============================================================
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
}

# construir df_series unindo INVENTÁRIO (para Cidade/Local/Gateway) + datas + status
df_series = (
    df_inv[["Série","Cidade","Local","Gateway"]]
    .assign(Data=lambda x: x["Série"].map(date_map),
            Online=lambda x: ~x["Série"].isin(series_offline))
)
df_series["Data"] = pd.to_datetime(df_series["Data"], errors="coerce")

TOTAL_INSTALADOS = len(df_series)            # 37
TOTAL_ONLINE     = int(df_series["Online"].sum())  # 35
TOTAL_OFFLINE    = TOTAL_INSTALADOS - TOTAL_ONLINE # 2

# ============================================================
# Agregações para gráficos
# ============================================================
dia = (df.groupby("data", as_index=False)["ultronlines"].sum()
         .rename(columns={"ultronlines":"ultronlines_dia"}))
dia["data_str"] = dia["data"].dt.strftime("%d/%m/%Y")
dia_sorted = dia.sort_values("data")
dia_sorted["acumulado"] = dia_sorted["ultronlines_dia"].cumsum()

# Distribuição por cidade (usando inventário real, sem '—')
cidade_dist = (df_inv.groupby("Cidade", as_index=False)["Série"].count()
               .rename(columns={"Série":"Ultronlines"}))

# ============================================================
# Gráficos
# ============================================================
def fig_barras_por_dia():
    fig = go.Figure(go.Bar(
        x=dia_sorted["data_str"],
        y=dia_sorted["ultronlines_dia"],
        text=dia_sorted["ultronlines_dia"],
        textposition="auto",
        marker_color=COR_PRI
    ))
    fig.update_layout(
        title="Ultronlines Instalados por Dia",
        xaxis_title="Data", yaxis_title="Quantidade",
        plot_bgcolor=COR_BG, paper_bgcolor=COR_BG, font=dict(color=COR_TXT, size=14)
    )
    return fig

def fig_acumulado():
    fig = go.Figure(go.Scatter(
        x=dia_sorted["data_str"], y=dia_sorted["acumulado"],
        mode="lines+markers", line=dict(width=3), marker=dict(size=8),
    ))
    fig.update_traces(line_color=COR_SEC)
    fig.update_layout(
        title="Acumulado de Ultronlines Instalados",
        xaxis_title="Data", yaxis_title="Acumulado",
        plot_bgcolor=COR_BG, paper_bgcolor=COR_BG, font=dict(color=COR_TXT, size=14)
    )
    return fig

def fig_cidade():
    colors = [cores_2neuron[i % len(cores_2neuron)] for i in range(len(cidade_dist))]
    fig = go.Figure(go.Bar(
        x=cidade_dist["Cidade"], y=cidade_dist["Ultronlines"],
        text=cidade_dist["Ultronlines"], textposition="auto", marker_color=colors
    ))
    fig.update_layout(
        title="Distribuição por Cidade (Inventário)", xaxis_title="Cidade", yaxis_title="Ultronlines",
        plot_bgcolor=COR_BG, paper_bgcolor=COR_BG, font=dict(color=COR_TXT, size=14)
    )
    return fig

def fig_status():
    fig = go.Figure(go.Pie(
        labels=["Online","Offline"], values=[TOTAL_ONLINE, TOTAL_OFFLINE],
        marker=dict(colors=[COR_PRI, "#E76F51"]), hole=0.5
    ))
    fig.update_layout(title="Status dos Ultronlines (37 instalados)")
    return fig

# ============================================================
# Helpers de UI
# ============================================================
def kpi_card(titulo, valor, subtitulo=None, cor_borda=COR_PRI):
    return dbc.Card(
        dbc.CardBody([
            html.Div(titulo, style={"fontSize":"0.85rem","color":COR_TXT,"opacity":0.8}),
            html.Div(str(valor), style={"fontSize":"1.8rem","fontWeight":"700","color":COR_TXT}),
            html.Div(subtitulo or "", style={"fontSize":"0.8rem","color":COR_TXT,"opacity":0.7})
        ]),
        style={"borderLeft": f"6px solid {cor_borda}", "borderRadius":"12px", "boxShadow":"0 2px 10px rgba(0,0,0,0.05)"}
    )

def make_table(df_table, page_size=10, height="auto"):
    return DataTable(
        columns=[{"name": c, "id": c} for c in df_table.columns],
        data=df_table.to_dict("records"),
        page_size=page_size,
        style_table={"overflowX": "auto", "height": height},
        style_header={"backgroundColor": "#EFEAF9", "fontWeight": "bold", "color": COR_TXT},
        style_cell={"padding": "8px", "whiteSpace": "normal", "height": "auto"},
    )

# ============================================================
# Layout
# ============================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Instalações 2Neuron | Sabesp"

app.layout = dbc.Container([
    html.H2("Instalações 2Neuron na Sabesp (11–22/Ago/2025)",
            className="mt-4 mb-1", style={"color": COR_PRI, "fontWeight":"800"}),

    html.P("Consolida cronograma (37 instalados), status (35 online / 2 offline), inventário técnico e observações.",
           style={"color": COR_TXT, "opacity": 0.8, "marginBottom":"0.5rem"}),

    dbc.Row([
        dbc.Col(kpi_card("Instalados (total)", TOTAL_INSTALADOS, "Confirmado pelas fontes"), md=3),
        dbc.Col(kpi_card("Online", TOTAL_ONLINE, "Enviando dados"), md=3),
        dbc.Col(kpi_card("Offline", TOTAL_OFFLINE, "277 (Talamanca) e 308 (Jardim Ikeda)", cor_borda="#E76F51"), md=6),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_barras_por_dia()), md=6),
        dbc.Col(dcc.Graph(figure=fig_acumulado()), md=6),
    ], className="my-2"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_cidade()), md=6),
        dbc.Col(dcc.Graph(figure=fig_status()), md=6),
    ], className="my-2"),

    html.H4("Detalhamento diário (cronograma)", style={"color": COR_PRI, "marginTop":"1rem"}),
    make_table(
        df[["data","cidade","local","ultronlines","ultronlinks","gateways_extra","obs"]]
          .sort_values(["data","cidade","local"])
          .rename(columns={
              "data":"Data","cidade":"Cidade","local":"Local",
              "ultronlines":"Ultronlines","ultronlinks":"Ultronlinks","gateways_extra":"Gateways extra",
              "obs":"Observações"
          }),
        page_size=10
    ),

    html.H4("Séries instaladas e status (37)", style={"color": COR_PRI, "marginTop":"1.5rem"}),
    make_table(
        df_series.sort_values(["Online","Data","Série"], ascending=[False, True, True])
                 .assign(Status=lambda x: x["Online"].map({True:"Online", False:"Offline"}))
                 [["Série","Status","Data","Cidade","Local","Gateway"]],
        page_size=15
    ),

    html.H4("Inventário técnico (campos principais)", style={"color": COR_PRI, "marginTop":"1.5rem"}),
    make_table(
        df_inv.rename(columns={
            "Potência (cv)":"Pot (cv)","Potência (kW)":"Pot (kW)","Corrente (A)":"Corr (A)",
            "Tensão (V)":"Tensão (V)","Rotação (RPM)":"RPM","Seção Cabo (mm²)":"Seção (mm²)",
            "Diâm. externo (mm)":"Diâm (mm)","Cabos/fase":"Cabos/fase"
        })[["Local","Cidade","Série","Gateway","Operadora","Acionamento","Pot (cv)","Pot (kW)","Corr (A)","Tensão (V)","RPM","Seção (mm²)","Diâm (mm)","Cabos/fase","Endereço","Coordenadas","Online"]],
        page_size=12
    ),

    html.Br(),
    html.Div("Observação: 11/08 = 4 (inclui 270 em Alvarenga Mãe) • 12/08 = 4 (269 e 288 em Lavapés).",
             style={"color": COR_TXT, "opacity":0.75, "fontSize":"0.9rem", "marginBottom":"2rem"})
], fluid=True, style={"backgroundColor": COR_BG, "padding":"16px"})

# ============================================================
# Execução com abertura automática no navegador
# ============================================================
def _open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == "__main__":
    Timer(1, _open_browser).start()
    app.run_server(host="127.0.0.1", port=8050, debug=True)
