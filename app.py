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
PALETA_REDES = [AZUL, VERDE, "#FF9F00", "#808080", "#8C564B", "#9467BD"] # Cores para o comparativo

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
st.sidebar.title("⚙️ Filtros Principais")

etapa = st.sidebar.selectbox("Etapa de Ensino", list(bases.keys()))
df_completo = bases[etapa] # Mantém a base sem filtro de rede para a aba de comparativo

if "Rede" in df_completo.columns:
    rede = st.sidebar.selectbox("Rede (Visão Geral)", sorted(df_completo["Rede"].dropna().unique()))
    df = df_completo[df_completo["Rede"] == rede]
else:
    rede = "Todas"
    df = df_completo

st.sidebar.markdown("---")
st.sidebar.info("**Fonte**\n\nINEP\n\nIDEB 2025")

# =====================================================
# IDENTIFICA COLUNA MAIS RECENTE E ANOS
# =====================================================
colunas_ideb = [c for c in df.columns if "IDEB" in c]
coluna_atual = colunas_ideb[-1]
anos = [c.replace("IDEB", "").strip() for c in colunas_ideb]

# =====================================================
# KPIs E PREPARAÇÃO DO RANKING DOS ESTADOS
# =====================================================
sergipe = df[df["Estado"] == "Sergipe"]

# Lista de regiões para excluir da contagem de posição do ranking
regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

# Cria o ranking SOMENTE com os estados e sem notas nulas
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
aba1, aba2, aba3, aba4 = st.tabs([
    "🇧🇷 Ranking Brasil", 
    "🌵 Ranking Nordeste", 
    "📈 Série Histórica",
    "🏛️ Comparativo por Rede"
])

# =====================================================
# ABA 1 - RANKING BRASIL
# =====================================================
with aba1:
    st.subheader(f"🇧🇷 Ranking Nacional • {etapa} ({rede})")
    
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

# =====================================================
# ABA 2 - RANKING NORDESTE
# =====================================================
with aba2:
    st.subheader(f"🌵 Ranking Nordeste • {etapa} ({rede})")
    
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

# =====================================================
# ABA 3 - SÉRIE HISTÓRICA (CORRIGIDA)
# =====================================================
with aba3:
    st.subheader(f"📈 Evolução do IDEB - Sergipe ({rede})")
    
    if not sergipe.empty:
        valores = sergipe[colunas_ideb].iloc[0].astype(float).values
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=anos,
            y=valores,
            mode="lines+markers+text",
            line=dict(color=AZUL, width=5),
            marker=dict(size=14, color=AMARELO, line=dict(color=AZUL, width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,39,118,0.10)",
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores],
            textposition="top center",
            cliponaxis=False # Evita que as bordas cortem os pontos e textos
        ))
        
        # Calcula o topo do gráfico dinamicamente para os rótulos não sumirem
        max_val = max([v for v in valores if pd.notna(v)] + [0])
        
        fig3.update_layout(
            template="plotly_white",
            height=550,
            showlegend=False,
            xaxis_title="Ano",
            yaxis_title="Nota IDEB",
            xaxis=dict(
                type="category",
                range=[-0.5, len(anos) - 0.5] # Adiciona respiro nas bordas laterais
            ),
            yaxis=dict(
                range=[0, max_val + 1.5] # Adiciona respiro no topo
            ),
            margin=dict(l=40, r=40, t=40, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Não existem dados históricos para Sergipe nesta rede.")

# =====================================================
# ABA 4 - COMPARATIVO POR REDE (NOVA FUNCIONALIDADE)
# =====================================================
with aba4:
    st.subheader(f"🏛️ Comparativo de Redes em Sergipe • {etapa}")
    
    # Filtra apenas os dados de Sergipe usando a base completa (antes do filtro lateral)
    df_se_todas_redes = df_completo[df_completo["Estado"] == "Sergipe"]
    
    if not df_se_todas_redes.empty and "Rede" in df_se_todas_redes.columns:
        redes_disponiveis = sorted(df_se_todas_redes["Rede"].dropna().unique())
        
        # Seleção padrão sugerida: Estadual, Municipal, Privada (se existirem)
        redes_padrao = [r for r in ["Estadual", "Municipal", "Privada", "Pública"] if r in redes_disponiveis][:3]
        if not redes_padrao:
            redes_padrao = redes_disponiveis[:2]
            
        redes_selecionadas = st.multiselect(
            "Selecione as Redes para comparar a evolução histórica:",
            options=redes_disponiveis,
            default=redes_padrao
        )
        
        if redes_selecionadas:
            fig4 = go.Figure()
            max_val_comp = 0
            
            for i, rede_nome in enumerate(redes_selecionadas):
                df_r = df_se_todas_redes[df_se_todas_redes["Rede"] == rede_nome]
                if not df_r.empty:
                    valores_r = df_r[colunas_ideb].iloc[0].astype(float).values
                    
                    # Atualiza o valor máximo para ajeitar o eixo Y
                    max_local = max([v for v in valores_r if pd.notna(v)] + [0])
                    if max_local > max_val_comp:
                        max_val_comp = max_local
                        
                    fig4.add_trace(go.Scatter(
                        x=anos,
                        y=valores_r,
                        mode="lines+markers+text",
                        name=rede_nome,
                        line=dict(width=4, color=PALETA_REDES[i % len(PALETA_REDES)]),
                        marker=dict(size=12),
                        text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores_r],
                        textposition="top center",
                        cliponaxis=False
                    ))
                    
            fig4.update_layout(
                template="plotly_white",
                height=550,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis_title="Ano",
                yaxis_title="Nota IDEB",
                xaxis=dict(
                    type="category",
                    range=[-0.5, len(anos) - 0.5]
                ),
                yaxis=dict(
                    range=[0, max_val_comp + 1.5]
                ),
                margin=dict(l=40, r=40, t=60, b=20)
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Selecione pelo menos uma rede acima para visualizar o comparativo.")
    else:
        st.warning("Não há dados de diferentes redes para Sergipe nesta base.")

# =====================================================
# COMPARAÇÃO BRASIL x NORDESTE x SERGIPE
# =====================================================
st.divider()
st.subheader(f"📊 Comparativo Consolidado ({rede})")

comparacao = []
# Puxa os dados direto do dataframe original `df` que ainda contém as regiões
for estado_regiao in ["Brasil", "Nordeste", "Sergipe"]:
    temp = df[df["Estado"] == estado_regiao]
    if not temp.empty:
        comparacao.append(dict(Local=estado_regiao, Nota=temp.iloc[0][coluna_atual]))

if len(comparacao) > 0:
    comp = pd.DataFrame(comparacao)
    
    cores_comp = []
    for x in comp["Local"]:
        if x == "Sergipe":
            cores_comp.append(AZUL)
        elif x == "Nordeste":
            cores_comp.append(VERDE)
        else:
            cores_comp.append(CINZA)
            
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=comp["Local"],
        y=comp["Nota"],
        marker_color=cores_comp,
        text=comp["Nota"].round(1),
        textposition="outside"
    ))
    
    fig5.update_layout(
        template="plotly_white",
        height=450,
        showlegend=False,
        yaxis_title="Nota IDEB"
    )
    st.plotly_chart(fig5, use_container_width=True)

# =====================================================
# MELHORES E PIORES
# =====================================================
st.divider()
c1, c2 = st.columns(2)

if not ranking.empty:
    with c1:
        melhor = ranking.iloc[0]
        st.success(f"🏆 **Melhor colocado ({rede})**\n\n**{melhor['Estado']}**\n\nNota: **{melhor[coluna_atual]:.1f}**")
    with c2:
        pior = ranking.iloc[-1]
        st.error(f"📉 **Último colocado ({rede})**\n\n**{pior['Estado']}**\n\nNota: **{pior[coluna_atual]:.1f}**")

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
