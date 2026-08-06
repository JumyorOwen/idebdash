import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Painel IDEB - Sergipe em Foco", layout="wide")
st.title("📊 Painel de Consulta IDEB 2025")
st.markdown("Acompanhamento estratégico dos indicadores da educação básica.")

# Paleta de cores da Identidade Visual
COR_SERGIPE = "#002776" # Azul (Destaque principal)
COR_OUTROS = "#009C3B"  # Verde (Demais estados)
COR_LINHA = "#FFDF00"   # Amarelo (Evolução histórica)
COR_FUNDO = "#FFFFFF"

# 2. Carregamento dos Dados (Lendo todas as abas do Excel)
@st.cache_data
def carregar_dados():
    # O parâmetro sheet_name=None faz o pandas ler todas as abas e retornar um dicionário
    arquivo = "BASE 1 IDEB BRASIL_3.xlsx"
    dict_abas = pd.read_excel(arquivo, sheet_name=None)
    
    dict_tratado = {}
    nordeste = ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 'Piauí', 'Rio Grande do Norte', 'Sergipe']
    
    # Tratando cada aba individualmente
    for nome_aba, df in dict_abas.items():
        # Renomeia a coluna para padronizar, caso esteja como Região/UF
        if 'Região/\nUnidade da Federação' in df.columns:
            df = df.rename(columns={'Região/\nUnidade da Federação': 'Estado'})
        elif 'UF' in df.columns:
             df = df.rename(columns={'UF': 'Estado'})
             
        # Criando a marcação de estados do Nordeste
        if 'Estado' in df.columns:
            df['Regiao_Nordeste'] = df['Estado'].apply(lambda x: 'Sim' if x in nordeste else 'Não')
            
        dict_tratado[nome_aba] = df
        
    return dict_tratado

# Carrega o dicionário com as bases de cada etapa
bases = carregar_dados()
lista_etapas = list(bases.keys())

# 3. Menu Lateral (Filtros)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Bandeira_de_Sergipe.svg/1200px-Bandeira_de_Sergipe.svg.png", width=150)
st.sidebar.header("Filtros Estratégicos")

# Seleção da aba (Etapa de Ensino) e da Rede
etapa_selecionada = st.sidebar.selectbox("Etapa de Ensino", lista_etapas)
df_etapa = bases[etapa_selecionada]

# Verifica se a coluna Rede existe para criar o filtro
if 'Rede' in df_etapa.columns:
    redes_disponiveis = df_etapa['Rede'].dropna().unique().tolist()
    rede_selecionada = st.sidebar.selectbox("Rede de Ensino", redes_disponiveis)
    df_filtrado = df_etapa[df_etapa['Rede'] == rede_selecionada]
else:
    df_filtrado = df_etapa

# 4. Construção das Abas Visuais
aba1, aba2, aba3 = st.tabs(["🌎 Ranking Nacional (2025)", "☀️ Ranking Nordeste (2025)", "📈 Série Histórica (Sergipe)"])

coluna_foco = 'IDEB 2025'

# Proteção caso a coluna de 2025 não esteja exata (ajuste se necessário)
if coluna_foco not in df_filtrado.columns:
    # Tenta pegar a última coluna que contém "IDEB"
    colunas_ideb = [col for col in df_filtrado.columns if 'IDEB' in col]
    if colunas_ideb:
        coluna_foco = colunas_ideb[-1]

with aba1:
    st.subheader(f"Ranking Nacional - {etapa_selecionada}")
    
    # Ordena e remove valores nulos
    df_br = df_filtrado.dropna(subset=[coluna_foco]).sort_values(by=coluna_foco, ascending=True)
    
    # Aplica a cor de destaque apenas em Sergipe
    cores_br = [COR_SERGIPE if estado == 'Sergipe' else COR_OUTROS for estado in df_br['Estado']]
    
    fig_br = go.Figure(go.Bar(
        x=df_br[coluna_foco], y=df_br['Estado'], orientation='h',
        marker_color=cores_br, text=df_br[coluna_foco], textposition='auto'
    ))
    fig_br.update_layout(xaxis_title=f"Nota {coluna_foco}", yaxis_title="", template="plotly_white", height=700)
    st.plotly_chart(fig_br, use_container_width=True)

with aba2:
    st.subheader(f"Ranking Nordeste - {etapa_selecionada}")
    
    df_ne = df_filtrado[df_filtrado['Regiao_Nordeste'] == 'Sim'].dropna(subset=[coluna_foco]).sort_values(by=coluna_foco, ascending=True)
    cores_ne = [COR_SERGIPE if estado == 'Sergipe' else COR_OUTROS for estado in df_ne['Estado']]
    
    fig_ne = go.Figure(go.Bar(
        x=df_ne[coluna_foco], y=df_ne['Estado'], orientation='h',
        marker_color=cores_ne, text=df_ne[coluna_foco], textposition='auto'
    ))
    fig_ne.update_layout(xaxis_title=f"Nota {coluna_foco}", yaxis_title="", template="plotly_white", height=500)
    st.plotly_chart(fig_ne, use_container_width=True)

with aba3:
    st.subheader(f"Série Histórica do IDEB - Sergipe ({etapa_selecionada})")
    
    # Isolando Sergipe
    df_se = df_filtrado[df_filtrado['Estado'] == 'Sergipe']
    colunas_anos = [col for col in df_se.columns if 'IDEB' in col]
    
    if not df_se.empty and len(colunas_anos) > 0:
        valores_se = df_se[colunas_anos].iloc[0].values
        # Limpa o texto das colunas para manter apenas o ano no eixo X
        anos = [str(col).replace('IDEB', '').strip() for col in colunas_anos]
        
        fig_hist = go.Figure()
        
        # Linha e marcadores
        fig_hist.add_trace(go.Scatter(
            x=anos, y=valores_se, mode='lines+markers+text',
            line=dict(color=COR_SERGIPE, width=4), # Usando azul para a linha
            marker=dict(size=12, color=COR_LINHA, line=dict(width=2, color=COR_SERGIPE)), # Amarelo nos pontos
            text=valores_se, textposition='top center',
            textfont=dict(color=COR_SERGIPE, size=14)
        ))
        
        fig_hist.update_layout(
            xaxis_title="Ano", 
            yaxis_title="Nota IDEB", 
            template="plotly_white",
            height=500
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("Dados históricos de Sergipe não encontrados para este filtro.")
