import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Painel IDEB 2025",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.main {
    background: #F5F7FA;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
h1 {
    color: #002776;
    font-weight: 700;
}
h2, h3 {
    color: #002776;
}
[data-testid="stSidebar"] {
    background: #FFFFFF;
}
.kpi {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 10px rgba(0,0,0,.08);
    text-align: center;
}
.kpi h1 {
    color: #002776;
    margin: 0;
}
.kpi p {
    color: #666;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CORES
# =====================================================
AZUL = "#002776"
VERDE = "#009C3B"
AMARELO = "#FFDF00"
CINZA = "#D9D9D9"

# =====================================================
# CABEÇALHO
# =====================================================
st.title("📊 Painel Estratégico IDEB 2025")
st.caption("Indicadores da Educação Básica • Fonte: INEP 2025")

# =====================================================
# CARREGAMENTO
# =====================================================
@st.cache_data
def carregar():
    arquivo = "BASE 1 IDEB BRASIL.xlsx"
    abas = pd.read_excel(arquivo, sheet_name=None)
    
    nordeste = [
        "Alagoas", "Bahia", "Ceará", "Maranhão", "Paraíba", 
        "Pernambuco", "Piauí", "Rio Grande do Norte", "Sergipe"
    ]
    
    bases = {}
    
    for nome, df in abas.items():
        if "Região/\nUnidade da Federação" in df.columns:
            df = df.rename(columns={"Região/\nUnidade da Federação": "Estado"})
            
        if "Estado" not in df.columns:
            continue
            
        df["Estado"] = df["Estado"].astype(str).str.strip()
        
        # Normaliza rede
        if "Rede" in df.columns:
            df["Rede"] = df["Rede"].astype(str).str.replace(r"\s*\(\d+\)", "", regex=True).str.strip()
            
        # Converte todas colunas IDEB
        colunas_ideb = [c for c in df.columns if "IDEB" in c]
        for c in colunas_ideb:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            
        df["Nordeste"] = df["Estado"].isin(nordeste)
        bases[nome] = df
        
    return bases

bases = carregar()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("⚙️ Filtros")

etapa = st.sidebar.selectbox("Etapa de Ensino", list(bases.keys()))
df = bases[etapa]

if "Rede" in df.columns:
    rede = st.sidebar.selectbox("Rede", sorted(df["Rede"].dropna().unique()))
    df = df[df["Rede"] == rede]
else:
    rede = "Todas"

st.sidebar.markdown("---")
st.sidebar.info("**Fonte**\n\nINEP\n\nIDEB 2025")

# =====================================================
# IDENTIFICA COLUNA MAIS RECENTE
# =====================================================
colunas_ideb = [c for c in df.columns if "IDEB" in c]
coluna_atual = colunas_ideb[-1]

# =====================================================
# KPIs E PREPARAÇÃO DO RANKING DOS ESTADOS
# =====================================================
sergipe = df[df["Estado"] == "Sergipe"]

# Lista de regiões para excluir da contagem de posição do ranking
regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

# Cria o ranking SOMENTE com os estados (sem regiões) e sem notas nulas
ranking = (
    df[~df["Estado"].isin(regioes)]
    .dropna(subset=[coluna_atual])
    .sort_values(coluna_atual, ascending=False)
    .reset_index(drop=True)
)
ranking["Posição"] = ranking.index + 1

if not sergipe.empty and pd.notna(sergipe.iloc[0][coluna_atual]):
    nota = float(sergipe.iloc[0][coluna_atual])
    
    try:
        posicao_br = int(ranking[ranking["Estado"] == "Sergipe"]["Posição"].iloc[0])
    except IndexError:
        posicao_br = "-"
        
    ranking_ne = ranking[ranking["Nordeste"]].reset_index(drop=True)
    ranking_ne["Posição"] = ranking_ne.index + 1
    
    try:
        posicao_ne = int(ranking_ne[ranking_ne["Estado"] == "Sergipe"]["Posição"].iloc[0])
    except IndexError:
        posicao_ne = "-"
else:
    nota = 0
    posicao_br = "-"
    posicao_ne = "-"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("IDEB", f"{nota:.1f}" if nota != 0 else "-")
with c2:
    st.metric("Ranking Brasil", f"{posicao_br}º" if posicao_br != "-" else "-")
with c3:
    st.metric("Ranking Nordeste", f"{posicao_ne}º" if posicao_ne != "-" else "-")
with c4:
    st.metric("Rede", rede)

st.divider()

# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3 = st.tabs(["🇧🇷 Ranking Brasil", "🌵 Ranking Nordeste", "📈 Série Histórica"])

# =====================================================
# ABA 1 - RANKING BRASIL
# =====================================================
with aba1:
    st.subheader(f"🇧🇷 Ranking Nacional • {etapa}")
    
    ranking_br = ranking.copy()
    ranking_br["Label"] = ranking_br["Posição"].astype(str) + "º  " + ranking_br["Estado"]
    
    cores = [AZUL if estado == "Sergipe" else "#C9CED6" for estado in ranking_br["Estado"]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ranking_br[coluna_atual],
        y=ranking_br["Label"],
        orientation="h",
        marker=dict(color=cores),
        text=ranking_br[coluna_atual].round(1),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Nota: %{x}<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_white",
        height=900,
        margin=dict(l=10, r=20, t=20, b=20),
        showlegend=False,
        xaxis_title="Nota IDEB",
        yaxis_title="",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(
        ranking_br[["Posição", "Estado", coluna_atual]],
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# ABA 2 - RANKING NORDESTE
# =====================================================
with aba2:
    st.subheader(f"🌵 Ranking Nordeste • {etapa}")
    
    ranking_ne = ranking[ranking["Nordeste"]].reset_index(drop=True)
    ranking_ne["Posição"] = ranking_ne.index + 1
    ranking_ne["Label"] = ranking_ne["Posição"].astype(str) + "º  " + ranking_ne["Estado"]
    
    cores = [AZUL if estado == "Sergipe" else VERDE for estado in ranking_ne["Estado"]]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=ranking_ne[coluna_atual],
        y=ranking_ne["Label"],
        orientation="h",
        marker=dict(color=cores),
        text=ranking_ne[coluna_atual].round(1),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Nota: %{x}<extra></extra>"
    ))
    
    fig2.update_layout(
        template="plotly_white",
        height=600,
        margin=dict(l=10, r=20, t=20, b=20),
        showlegend=False,
        xaxis_title="Nota IDEB",
        yaxis_title="",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.dataframe(
        ranking_ne[["Posição", "Estado", coluna_atual]],
        use_container_width=True,
        hide_index=True
    )

# =====================================================
# ABA 3 - SÉRIE HISTÓRICA
# =====================================================
with aba3:
    st.subheader(f"📈 Evolução do IDEB - Sergipe")
    
    df_se = df[df["Estado"] == "Sergipe"]
    
    if not df_se.empty:
        colunas_hist = [c for c in df.columns if "IDEB" in c]
        anos = [c.replace("IDEB", "").strip() for c in colunas_hist]
        valores = df_se[colunas_hist].iloc[0].astype(float).values
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=anos,
            y=valores,
            mode="lines+markers+text",
            line=dict(color=AZUL, width=5),
            marker=dict(size=14, color=AMARELO, line=dict(color=AZUL, width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,39,118,0.10)",
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores],
            textposition="top center"
        ))
        
        fig.update_layout(
            template="plotly_white",
            height=550,
            showlegend=False,
            xaxis_title="Ano",
            yaxis_title="Nota IDEB",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não existem dados históricos para Sergipe.")

# =====================================================
# COMPARAÇÃO BRASIL x NORDESTE x SERGIPE
# =====================================================
st.divider()
st.subheader("📊 Comparativo")

comparacao = []
# Puxa os dados direto do dataframe original `df` que ainda contém as regiões
for estado in ["Brasil", "Nordeste", "Sergipe"]:
    temp = df[df["Estado"] == estado]
    if not temp.empty:
        comparacao.append(dict(Local=estado, Nota=temp.iloc[0][coluna_atual]))

if len(comparacao) > 0:
    comp = pd.DataFrame(comparacao)
    
    cores = []
    for x in comp["Local"]:
        if x == "Sergipe":
            cores.append(AZUL)
        elif x == "Nordeste":
            cores.append(VERDE)
        else:
            cores.append("#BFBFBF")
            
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=comp["Local"],
        y=comp["Nota"],
        marker_color=cores,
        text=comp["Nota"],
        textposition="outside"
    ))
    
    fig.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False,
        yaxis_title="Nota IDEB"
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# MELHORES E PIORES
# =====================================================
st.divider()
c1, c2 = st.columns(2)

if not ranking.empty:
    with c1:
        melhor = ranking.iloc[0]
        st.success(f"🏆 **Melhor colocado**\n\n**{melhor['Estado']}**\n\nNota: **{melhor[coluna_atual]:.1f}**")
    with c2:
        pior = ranking.iloc[-1]
        st.error(f"📉 **Último colocado**\n\n**{pior['Estado']}**\n\nNota: **{pior[coluna_atual]:.1f}**")

# =====================================================
# TABELA COMPLETA
# =====================================================
st.divider()
st.subheader("📋 Base utilizada")

mostrar = st.checkbox("Mostrar tabela completa")
if mostrar:
    st.dataframe(ranking, use_container_width=True, hide_index=True)

# =====================================================
# RODAPÉ
# =====================================================
st.divider()
st.caption("Painel desenvolvido em Streamlit\n\nFonte: INEP • IDEB 2025\n\nAtualização automática da base.")
