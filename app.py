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
# NOMES DE ESTADOS — CORREÇÃO DE ABREVIAÇÕES
# =====================================================
NOMES_CORRETOS = {
    "R. G. do Norte": "Rio Grande do Norte",
    "R.G. do Norte": "Rio Grande do Norte",
    "RG do Norte": "Rio Grande do Norte",
    "R. G. do Sul": "Rio Grande do Sul",
    "R.G. do Sul": "Rio Grande do Sul",
    "RG do Sul": "Rio Grande do Sul",
    "M. G. do Sul": "Mato Grosso do Sul",
    "M.G. do Sul": "Mato Grosso do Sul",
    "MG do Sul": "Mato Grosso do Sul",
}

# =====================================================
# CARREGAMENTO — BASE 1 (ESTADOS / BRASIL)
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
        df["Estado"] = df["Estado"].replace(NOMES_CORRETOS)

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
# CARREGAMENTO — BASE 2 (MUNICÍPIOS DE SERGIPE)
# =====================================================
@st.cache_data
def carregar_municipios():
    arquivo = "BASE 2 IDEB BRASIL.xlsx"
    abas = pd.read_excel(arquivo, sheet_name=None)

    bases_mun = {}

    for nome, df in abas.items():
        if "Município" not in df.columns:
            continue

        df["Município"] = df["Município"].astype(str).str.strip()

        if "Rede" in df.columns:
            df["Rede"] = df["Rede"].astype(str).str.replace(r"\s*\(\d+\)", "", regex=True).str.strip()

        colunas_ideb = [c for c in df.columns if "IDEB" in c]
        for c in colunas_ideb:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        bases_mun[nome] = df

    return bases_mun


try:
    bases_mun = carregar_municipios()
    municipios_ok = True
except FileNotFoundError:
    bases_mun = {}
    municipios_ok = False

# =====================================================
# SIDEBAR — FILTROS (ANÁLISE POR ESTADO)
# =====================================================
st.sidebar.title("⚙️ Filtros • Estados")

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

if not municipios_ok:
    st.sidebar.warning("⚠️ **BASE 2 IDEB BRASIL.xlsx** não encontrada. A aba de Municípios de Sergipe ficará indisponível.")

# =====================================================
# RANKINGS (ESTADOS)
# =====================================================
regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

ESTADO_PRIORIDADE = "Sergipe"


def montar_ranking(df_base, coluna_valor, coluna_nome="Estado", prioridade=None):
    """Ordena por nota (desc). Em caso de empate, 'prioridade' vem primeiro (se informado)."""
    tmp = df_base.dropna(subset=[coluna_valor]).copy()
    if prioridade is not None:
        tmp["_prioridade"] = (tmp[coluna_nome] != prioridade).astype(int)
        tmp = tmp.sort_values(
            by=[coluna_valor, "_prioridade"],
            ascending=[False, True]
        ).drop(columns="_prioridade").reset_index(drop=True)
    else:
        tmp = tmp.sort_values(by=coluna_valor, ascending=False).reset_index(drop=True)
    tmp["Posição"] = tmp.index + 1
    return tmp


ranking = montar_ranking(df[~df["Estado"].isin(regioes)], coluna_atual, "Estado", ESTADO_PRIORIDADE)
ranking_ne = montar_ranking(df[(~df["Estado"].isin(regioes)) & (df["Nordeste"])], coluna_atual, "Estado", ESTADO_PRIORIDADE)

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
# KPIs (ESTADOS)
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
def grafico_ranking(df_rank, coluna_valor, coluna_nome="Estado", destaque="Sergipe",
                     cor_destaque=AZUL, cor_padrao=CINZA, altura=600):
    dados = df_rank.copy()
    dados["Label"] = dados["Posição"].astype(str) + "º  " + dados[coluna_nome]
    cores = [cor_destaque if nome_local == destaque else cor_padrao for nome_local in dados[coluna_nome]]

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
# GEOJSON — CONTORNO DOS ESTADOS (PARA O MAPA)
# =====================================================
GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"


@st.cache_data
def carregar_geojson():
    import requests
    resposta = requests.get(GEOJSON_URL, timeout=15)
    resposta.raise_for_status()
    return resposta.json()


# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "🇧🇷 Ranking Brasil",
    "🌵 Ranking Nordeste",
    "📈 Série Histórica",
    "🏛️ Comparativo por Rede",
    "🗺️ Mapa Brasil",
    "🏙️ Municípios de Sergipe"
])

# ---------- ABA 1 ----------
with aba1:
    st.subheader(f"Ranking Nacional • {etapa} ({rede}) • {ano_ref}")
    fig = grafico_ranking(ranking, coluna_atual, "Estado", altura=900)
    st.plotly_chart(fig, use_container_width=True)

# ---------- ABA 2 ----------
with aba2:
    st.subheader(f"Ranking Nordeste • {etapa} ({rede}) • {ano_ref}")
    fig2 = grafico_ranking(ranking_ne, coluna_atual, "Estado", cor_padrao=VERDE, altura=600)
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
            default=redes_padrao,
            key="redes_estado"
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

# ---------- ABA 5 — MAPA ----------
with aba5:
    st.subheader(f"Mapa do Brasil • {etapa} ({rede}) • {ano_ref}")

    df_mapa = ranking.copy()  # já são só estados (sem regiões/Brasil), com nomes completos

    try:
        geojson = carregar_geojson()

        fig6 = px.choropleth(
            df_mapa,
            geojson=geojson,
            locations="Estado",
            featureidkey="properties.name",
            color=coluna_atual,
            color_continuous_scale=[CINZA, AZUL_CLARO, AZUL],
            hover_name="Estado",
            hover_data={coluna_atual: ":.1f", "Posição": True, "Estado": False},
        )
        fig6.update_traces(marker_line_color="white", marker_line_width=0.8)
        fig6.update_geos(fitbounds="locations", visible=False)
        fig6.update_layout(
            template="plotly_white",
            height=650,
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
            coloraxis_colorbar=dict(title="Nota IDEB"),
        )
        st.plotly_chart(fig6, use_container_width=True)
        st.caption("Passe o mouse sobre um estado para ver a nota e a posição no ranking.")
    except Exception as e:
        st.warning(
            "⚠️ Não foi possível carregar o contorno geográfico dos estados "
            "(é necessária conexão com a internet na primeira execução)."
        )
        st.caption(f"Detalhe técnico: {e}")

# ---------- ABA 6 — MUNICÍPIOS DE SERGIPE ----------
with aba6:
    st.subheader("Municípios de Sergipe")

    if not municipios_ok:
        st.error(
            "⚠️ Arquivo **BASE 2 IDEB BRASIL.xlsx** não encontrado. "
            "Coloque-o na mesma pasta do app para habilitar esta análise."
        )
    else:
        # ---------- filtros próprios da aba ----------
        fc1, fc2, fc3 = st.columns(3)

        with fc1:
            etapa_mun = st.selectbox("Etapa de Ensino", list(bases_mun.keys()), key="etapa_mun")

        df_mun_completo = bases_mun[etapa_mun]

        with fc2:
            if "Rede" in df_mun_completo.columns:
                rede_mun = st.selectbox(
                    "Rede", sorted(df_mun_completo["Rede"].dropna().unique()), key="rede_mun"
                )
                df_mun = df_mun_completo[df_mun_completo["Rede"] == rede_mun]
            else:
                rede_mun = "Todas"
                df_mun = df_mun_completo

        colunas_ideb_mun = [c for c in df_mun.columns if "IDEB" in c]
        anos_mun = [c.replace("IDEB", "").strip() for c in colunas_ideb_mun]

        with fc3:
            ano_ref_mun = st.selectbox(
                "Ano de Referência", anos_mun, index=len(anos_mun) - 1, key="ano_mun"
            )
        coluna_atual_mun = colunas_ideb_mun[anos_mun.index(ano_ref_mun)]

        idx_atual_mun = anos_mun.index(ano_ref_mun)
        coluna_anterior_mun = colunas_ideb_mun[idx_atual_mun - 1] if idx_atual_mun > 0 else None

        municipios_disponiveis = sorted(df_mun["Município"].dropna().unique())
        municipio_sel = st.selectbox(
            "Município em destaque",
            municipios_disponiveis,
            index=municipios_disponiveis.index("Aracaju") if "Aracaju" in municipios_disponiveis else 0,
            key="municipio_sel"
        )

        # ---------- ranking dos municípios ----------
        ranking_mun = montar_ranking(df_mun, coluna_atual_mun, "Município", municipio_sel)

        alvo = df_mun[df_mun["Município"] == municipio_sel]

        if not alvo.empty and pd.notna(alvo.iloc[0][coluna_atual_mun]):
            nota_mun = float(alvo.iloc[0][coluna_atual_mun])

            nota_mun_anterior = None
            if coluna_anterior_mun and pd.notna(alvo.iloc[0][coluna_anterior_mun]):
                nota_mun_anterior = float(alvo.iloc[0][coluna_anterior_mun])

            try:
                posicao_mun = int(
                    ranking_mun.loc[ranking_mun["Município"] == municipio_sel, "Posição"].iloc[0]
                )
            except IndexError:
                posicao_mun = None
        else:
            nota_mun = None
            nota_mun_anterior = None
            posicao_mun = None

        # ---------- KPIs ----------
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            delta_mun = (
                f"{nota_mun - nota_mun_anterior:+.1f}"
                if nota_mun is not None and nota_mun_anterior is not None else None
            )
            st.metric(f"IDEB {municipio_sel}", f"{nota_mun:.1f}" if nota_mun is not None else "—", delta=delta_mun)
        with mc2:
            st.metric("Ranking entre Municípios/SE", f"{posicao_mun}º" if posicao_mun else "—")
        with mc3:
            st.metric("Total de Municípios", f"{len(municipios_disponiveis)}")
        with mc4:
            st.metric("Rede", rede_mun)

        st.markdown("")

        sub1, sub2, sub3 = st.tabs(["📊 Ranking dos 75 Municípios", "📈 Série Histórica", "🏛️ Comparativo por Rede"])

        # ----- ranking -----
        with sub1:
            st.caption(f"{etapa_mun} • {rede_mun} • {ano_ref_mun}")
            fig_mun_rank = grafico_ranking(
                ranking_mun, coluna_atual_mun, "Município",
                destaque=municipio_sel, cor_padrao=CINZA, altura=1400
            )
            st.plotly_chart(fig_mun_rank, use_container_width=True)

        # ----- série histórica -----
        with sub2:
            st.caption(f"Evolução do IDEB — {municipio_sel} ({rede_mun})")

            if not alvo.empty:
                valores_mun = alvo[colunas_ideb_mun].iloc[0].astype(float).values

                fig_mun_hist = go.Figure()
                fig_mun_hist.add_trace(go.Scatter(
                    x=anos_mun,
                    y=valores_mun,
                    mode="lines+markers+text",
                    line=dict(color=VERDE, width=5, shape="spline"),
                    marker=dict(size=13, color=AMARELO, line=dict(color=VERDE, width=2)),
                    fill="tozeroy",
                    fillcolor="rgba(0,156,59,0.08)",
                    text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores_mun],
                    textposition="top center",
                    textfont=dict(size=13, color=VERDE),
                    cliponaxis=False
                ))

                max_val_mun = max([v for v in valores_mun if pd.notna(v)] + [0])

                fig_mun_hist.update_layout(
                    template="plotly_white",
                    height=500,
                    showlegend=False,
                    font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                    xaxis_title="Ano",
                    yaxis_title="Nota IDEB",
                    xaxis=dict(type="category", range=[-0.5, len(anos_mun) - 0.5]),
                    yaxis=dict(range=[0, max_val_mun + 1.5]),
                    margin=dict(l=40, r=40, t=30, b=20),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                )
                st.plotly_chart(fig_mun_hist, use_container_width=True)
            else:
                st.warning(f"Não existem dados históricos para {municipio_sel} nesta rede.")

        # ----- comparativo por rede -----
        with sub3:
            st.caption(f"Comparativo de redes em {municipio_sel} • {etapa_mun}")

            df_mun_todas_redes = df_mun_completo[df_mun_completo["Município"] == municipio_sel]

            if not df_mun_todas_redes.empty and "Rede" in df_mun_todas_redes.columns:
                redes_mun_disponiveis = sorted(df_mun_todas_redes["Rede"].dropna().unique())

                redes_mun_padrao = [
                    r for r in ["Estadual", "Municipal", "Federal", "Pública"] if r in redes_mun_disponiveis
                ][:3]
                if not redes_mun_padrao:
                    redes_mun_padrao = redes_mun_disponiveis[:2]

                redes_mun_selecionadas = st.multiselect(
                    "Selecione as redes para comparar a evolução histórica:",
                    options=redes_mun_disponiveis,
                    default=redes_mun_padrao,
                    key="redes_municipio"
                )

                if redes_mun_selecionadas:
                    fig_mun_comp = go.Figure()
                    max_val_mun_comp = 0

                    for i, rede_nome in enumerate(redes_mun_selecionadas):
                        df_r_mun = df_mun_todas_redes[df_mun_todas_redes["Rede"] == rede_nome]
                        if df_r_mun.empty:
                            continue

                        valores_r_mun = df_r_mun[colunas_ideb_mun].iloc[0].astype(float).values
                        max_local_mun = max([v for v in valores_r_mun if pd.notna(v)] + [0])
                        max_val_mun_comp = max(max_val_mun_comp, max_local_mun)

                        fig_mun_comp.add_trace(go.Scatter(
                            x=anos_mun,
                            y=valores_r_mun,
                            mode="lines+markers+text",
                            name=rede_nome,
                            line=dict(width=4, color=PALETA_REDES[i % len(PALETA_REDES)], shape="spline"),
                            marker=dict(size=11),
                            text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores_r_mun],
                            textposition="top center",
                            cliponaxis=False
                        ))

                    fig_mun_comp.update_layout(
                        template="plotly_white",
                        height=500,
                        font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis_title="Ano",
                        yaxis_title="Nota IDEB",
                        xaxis=dict(type="category", range=[-0.5, len(anos_mun) - 0.5]),
                        yaxis=dict(range=[0, max_val_mun_comp + 1.5]),
                        margin=dict(l=40, r=40, t=60, b=20),
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                    )
                    st.plotly_chart(fig_mun_comp, use_container_width=True)
                else:
                    st.info("Selecione pelo menos uma rede acima para visualizar o comparativo.")
            else:
                st.warning(f"Não há dados de diferentes redes para {municipio_sel} nesta base.")

        # ---------- melhores e piores municípios ----------
        st.divider()
        cm1, cm2 = st.columns(2)

        if not ranking_mun.empty:
            with cm1:
                melhor_mun = ranking_mun.iloc[0]
                st.success(
                    f"🏆 **Melhor colocado ({rede_mun})**\n\n"
                    f"**{melhor_mun['Município']}**  •  Nota: **{melhor_mun[coluna_atual_mun]:.1f}**"
                )
            with cm2:
                pior_mun = ranking_mun.iloc[-1]
                st.error(
                    f"📉 **Último colocado ({rede_mun})**\n\n"
                    f"**{pior_mun['Município']}**  •  Nota: **{pior_mun[coluna_atual_mun]:.1f}**"
                )

        # ---------- tabela completa + download ----------
        st.divider()
        st.subheader("📋 Base de Municípios utilizada")

        mostrar_mun = st.checkbox("Mostrar tabela completa dos municípios", key="mostrar_mun")
        if mostrar_mun:
            st.dataframe(ranking_mun, use_container_width=True, hide_index=True)

            csv_mun = ranking_mun.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ Baixar tabela (CSV)",
                data=csv_mun,
                file_name=f"ideb_municipios_se_{etapa_mun}_{rede_mun}_{ano_ref_mun}.csv".replace(" ", "_"),
                mime="text/csv",
                key="download_mun"
            )

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
# MELHORES E PIORES (ESTADOS)
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
# TABELA COMPLETA + DOWNLOAD (ESTADOS)
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
