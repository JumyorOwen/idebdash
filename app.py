import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
# CORES / IDENTIDADE VISUAL
# =====================================================
AZUL = "#002776"
AZUL_CLARO = "#1E4FA3"
VERDE = "#009C3B"
AMARELO = "#FFDF00"
CINZA = "#C9CED6"
CINZA_ESCURO = "#5B6472"
FUNDO = "#F4F6FA"
PALETA_REDES = [AZUL, VERDE, "#FF9F00", "#8C564B", "#9467BD", "#17A2B8"]

# =====================================================
# CSS
# =====================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.main {{
    background: {FUNDO};
}}
.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}}

h1 {{
    color: {AZUL};
    font-weight: 800;
    letter-spacing: -0.5px;
}}
h2, h3 {{
    color: {AZUL};
    font-weight: 700;
}}

[data-testid="stSidebar"] {{
    background: #FFFFFF;
    border-right: 1px solid #EAECF0;
}}
[data-testid="stSidebar"] h1 {{
    font-size: 1.1rem;
}}

/* Cards de KPI */
div[data-testid="stMetric"] {{
    background: #FFFFFF;
    padding: 18px 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(0, 39, 118, 0.06);
    border: 1px solid #EEF0F4;
}}
div[data-testid="stMetricLabel"] {{
    color: {CINZA_ESCURO};
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
div[data-testid="stMetricValue"] {{
    color: {AZUL};
    font-weight: 800;
}}

/* Tabs */
button[data-baseweb="tab"] {{
    font-weight: 600;
    color: {CINZA_ESCURO};
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {AZUL};
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {AZUL};
}}

/* Divisores mais discretos */
hr {{
    margin: 1.6rem 0;
    opacity: 0.15;
}}

/* Caption */
[data-testid="stCaptionContainer"] {{
    color: {CINZA_ESCURO};
}}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CABEÇALHO
# =====================================================
col_titulo, col_badge = st.columns([5, 1])
with col_titulo:
    st.title("📊 Painel Estratégico IDEB")
    st.caption("Indicadores da Educação Básica  •  Fonte: INEP")

st.divider()

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

        if "Rede" in df.columns:
            df["Rede"] = df["Rede"].astype(str).str.replace(r"\s*\(\d+\)", "", regex=True).str.strip()

        colunas_ideb = [c for c in df.columns if "IDEB" in c]
        for c in colunas_ideb:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df["Nordeste"] = df["Estado"].isin(nordeste)
        bases[nome] = df

    return bases


try:
    bases = carregar()
except FileNotFoundError:
    st.error("⚠️ Arquivo **BASE 1 IDEB BRASIL.xlsx** não encontrado. Verifique se ele está na mesma pasta do app.")
    st.stop()

# =====================================================
# SIDEBAR — FILTROS
# =====================================================
st.sidebar.title("⚙️ Filtros")

etapa = st.sidebar.selectbox("Etapa de Ensino", list(bases.keys()))
df_completo = bases[etapa]

if "Rede" in df_completo.columns:
    rede = st.sidebar.selectbox("Rede", sorted(df_completo["Rede"].dropna().unique()))
    df = df_completo[df_completo["Rede"] == rede]
else:
    rede = "Todas"
    df = df_completo

colunas_ideb = [c for c in df.columns if "IDEB" in c]
anos = [c.replace("IDEB", "").strip() for c in colunas_ideb]

ano_ref = st.sidebar.selectbox("Ano de Referência", anos, index=len(anos) - 1)
coluna_atual = colunas_ideb[anos.index(ano_ref)]

# Ano anterior disponível, para calcular variação nos KPIs
idx_atual = anos.index(ano_ref)
coluna_anterior = colunas_ideb[idx_atual - 1] if idx_atual > 0 else None

st.sidebar.markdown("---")
st.sidebar.info(f"**Fonte:** INEP\n\n**Etapa:** {etapa}\n\n**Ano:** {ano_ref}")

# =====================================================
# RANKINGS
# =====================================================
regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

ESTADO_PRIORIDADE = "Sergipe"


def montar_ranking(df_base, coluna_valor):
    """Ordena por nota (desc). Em caso de empate, ESTADO_PRIORIDADE vem primeiro."""
    tmp = df_base.dropna(subset=[coluna_valor]).copy()
    tmp["_prioridade"] = (tmp["Estado"] != ESTADO_PRIORIDADE).astype(int)
    tmp = tmp.sort_values(
        by=[coluna_valor, "_prioridade"],
        ascending=[False, True]
    ).drop(columns="_prioridade").reset_index(drop=True)
    tmp["Posição"] = tmp.index + 1
    return tmp


ranking = montar_ranking(df[~df["Estado"].isin(regioes)], coluna_atual)
ranking_ne = montar_ranking(df[(~df["Estado"].isin(regioes)) & (df["Nordeste"])], coluna_atual)

sergipe = df[df["Estado"] == "Sergipe"]

if not sergipe.empty and pd.notna(sergipe.iloc[0][coluna_atual]):
    nota = float(sergipe.iloc[0][coluna_atual])

    nota_anterior = None
    if coluna_anterior and pd.notna(sergipe.iloc[0][coluna_anterior]):
        nota_anterior = float(sergipe.iloc[0][coluna_anterior])

    try:
        posicao_br = int(ranking.loc[ranking["Estado"] == "Sergipe", "Posição"].iloc[0])
    except IndexError:
        posicao_br = None

    try:
        posicao_ne = int(ranking_ne.loc[ranking_ne["Estado"] == "Sergipe", "Posição"].iloc[0])
    except IndexError:
        posicao_ne = None
else:
    nota = None
    nota_anterior = None
    posicao_br = None
    posicao_ne = None

# =====================================================
# KPIs
# =====================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_nota = f"{nota - nota_anterior:+.1f}" if nota is not None and nota_anterior is not None else None
    st.metric("IDEB Sergipe", f"{nota:.1f}" if nota is not None else "—", delta=delta_nota)
with c2:
    st.metric("Ranking Brasil", f"{posicao_br}º" if posicao_br else "—")
with c3:
    st.metric("Ranking Nordeste", f"{posicao_ne}º" if posicao_ne else "—")
with c4:
    st.metric("Rede", rede)

st.divider()


# =====================================================
# FUNÇÃO REUTILIZÁVEL — GRÁFICO DE RANKING (BARRAS HORIZONTAIS)
# =====================================================
def grafico_ranking(df_rank, coluna_valor, destaque="Sergipe",
                     cor_destaque=AZUL, cor_padrao=CINZA, altura=600):
    dados = df_rank.copy()
    dados["Label"] = dados["Posição"].astype(str) + "º  " + dados["Estado"]
    cores = [cor_destaque if estado == destaque else cor_padrao for estado in dados["Estado"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dados[coluna_valor],
        y=dados["Label"],
        orientation="h",
        marker=dict(color=cores, line=dict(width=0)),
        text=dados[coluna_valor].round(1),
        textposition="outside",
        textfont=dict(size=12, color=CINZA_ESCURO),
        hovertemplate="<b>%{y}</b><br>Nota: %{x}<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_white",
        height=altura,
        margin=dict(l=10, r=30, t=10, b=20),
        showlegend=False,
        font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
        xaxis_title="Nota IDEB",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4 = st.tabs([
    "🇧🇷 Ranking Brasil",
    "🌵 Ranking Nordeste",
    "📈 Série Histórica",
    "🏛️ Comparativo por Rede"
])

# ---------- ABA 1 ----------
with aba1:
    st.subheader(f"Ranking Nacional • {etapa} ({rede}) • {ano_ref}")
    fig = grafico_ranking(ranking, coluna_atual, altura=900)
    st.plotly_chart(fig, use_container_width=True)

# ---------- ABA 2 ----------
with aba2:
    st.subheader(f"Ranking Nordeste • {etapa} ({rede}) • {ano_ref}")
    fig2 = grafico_ranking(ranking_ne, coluna_atual, cor_padrao=VERDE, altura=600)
    st.plotly_chart(fig2, use_container_width=True)

# ---------- ABA 3 ----------
with aba3:
    st.subheader(f"Evolução do IDEB — Sergipe ({rede})")

    if not sergipe.empty:
        valores = sergipe[colunas_ideb].iloc[0].astype(float).values

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=anos,
            y=valores,
            mode="lines+markers+text",
            line=dict(color=AZUL, width=5, shape="spline"),
            marker=dict(size=13, color=AMARELO, line=dict(color=AZUL, width=2)),
            fill="tozeroy",
            fillcolor="rgba(0,39,118,0.08)",
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores],
            textposition="top center",
            textfont=dict(size=13, color=AZUL),
            cliponaxis=False
        ))

        max_val = max([v for v in valores if pd.notna(v)] + [0])

        fig3.update_layout(
            template="plotly_white",
            height=550,
            showlegend=False,
            font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
            xaxis_title="Ano",
            yaxis_title="Nota IDEB",
            xaxis=dict(type="category", range=[-0.5, len(anos) - 0.5]),
            yaxis=dict(range=[0, max_val + 1.5]),
            margin=dict(l=40, r=40, t=30, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Não existem dados históricos para Sergipe nesta rede.")

# ---------- ABA 4 ----------
with aba4:
    st.subheader(f"Comparativo de Redes em Sergipe • {etapa}")

    df_se_todas_redes = df_completo[df_completo["Estado"] == "Sergipe"]

    if not df_se_todas_redes.empty and "Rede" in df_se_todas_redes.columns:
        redes_disponiveis = sorted(df_se_todas_redes["Rede"].dropna().unique())

        redes_padrao = [r for r in ["Estadual", "Municipal", "Privada", "Pública"] if r in redes_disponiveis][:3]
        if not redes_padrao:
            redes_padrao = redes_disponiveis[:2]

        redes_selecionadas = st.multiselect(
            "Selecione as redes para comparar a evolução histórica:",
            options=redes_disponiveis,
            default=redes_padrao
        )

        if redes_selecionadas:
            fig4 = go.Figure()
            max_val_comp = 0

            for i, rede_nome in enumerate(redes_selecionadas):
                df_r = df_se_todas_redes[df_se_todas_redes["Rede"] == rede_nome]
                if df_r.empty:
                    continue

                valores_r = df_r[colunas_ideb].iloc[0].astype(float).values
                max_local = max([v for v in valores_r if pd.notna(v)] + [0])
                max_val_comp = max(max_val_comp, max_local)

                fig4.add_trace(go.Scatter(
                    x=anos,
                    y=valores_r,
                    mode="lines+markers+text",
                    name=rede_nome,
                    line=dict(width=4, color=PALETA_REDES[i % len(PALETA_REDES)], shape="spline"),
                    marker=dict(size=11),
                    text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores_r],
                    textposition="top center",
                    cliponaxis=False
                ))

            fig4.update_layout(
                template="plotly_white",
                height=550,
                font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_title="Ano",
                yaxis_title="Nota IDEB",
                xaxis=dict(type="category", range=[-0.5, len(anos) - 0.5]),
                yaxis=dict(range=[0, max_val_comp + 1.5]),
                margin=dict(l=40, r=40, t=60, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Selecione pelo menos uma rede acima para visualizar o comparativo.")
    else:
        st.warning("Não há dados de diferentes redes para Sergipe nesta base.")

# =====================================================
# COMPARATIVO CONSOLIDADO — BRASIL x NORDESTE x SERGIPE
# =====================================================
st.divider()
st.subheader(f"Comparativo Consolidado ({rede}) • {ano_ref}")

comparacao = []
for estado_regiao in ["Brasil", "Nordeste", "Sergipe"]:
    temp = df[df["Estado"] == estado_regiao]
    if not temp.empty:
        comparacao.append(dict(Local=estado_regiao, Nota=temp.iloc[0][coluna_atual]))

if comparacao:
    comp = pd.DataFrame(comparacao)
    cores_comp = [AZUL if x == "Sergipe" else VERDE if x == "Nordeste" else CINZA for x in comp["Local"]]

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=comp["Local"],
        y=comp["Nota"],
        marker=dict(color=cores_comp),
        text=comp["Nota"].round(1),
        textposition="outside",
        textfont=dict(size=13, color=CINZA_ESCURO)
    ))
    fig5.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False,
        font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
        yaxis_title="Nota IDEB",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
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
        st.success(f"🏆 **Melhor colocado ({rede})**\n\n**{melhor['Estado']}**  •  Nota: **{melhor[coluna_atual]:.1f}**")
    with c2:
        pior = ranking.iloc[-1]
        st.error(f"📉 **Último colocado ({rede})**\n\n**{pior['Estado']}**  •  Nota: **{pior[coluna_atual]:.1f}**")

# =====================================================
# TABELA COMPLETA + DOWNLOAD
# =====================================================
st.divider()
st.subheader("📋 Base utilizada")

mostrar = st.checkbox("Mostrar tabela completa")
if mostrar:
    st.dataframe(ranking, use_container_width=True, hide_index=True)

    csv = ranking.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar tabela (CSV)",
        data=csv,
        file_name=f"ideb_{etapa}_{rede}_{ano_ref}.csv".replace(" ", "_"),
        mime="text/csv"
    )

# =====================================================
# RODAPÉ
# =====================================================
st.divider()
st.caption("Painel desenvolvido em Streamlit  •  Fonte: INEP  •  Atualização automática da base.")
