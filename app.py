import re
import unicodedata
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Painel Educacional • IDEB",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CORES / IDENTIDADE VISUAL
# =====================================================
AZUL = "#1E3A8A"
AZUL_CLARO = "#3B82F6"
VERDE = "#059669"
AMARELO = "#F59E0B"
ROXO = "#7C3AED"
ROSA = "#DB2777"
CIANO = "#0891B2"
VERMELHO = "#DC2626"
CINZA = "#CBD5E1"
CINZA_ESCURO = "#64748B"
FUNDO = "#F1F5F9"
BRANCO = "#FFFFFF"

SIDEBAR_BG = "#0B1330"
SIDEBAR_CARD = "#141B3C"
SIDEBAR_TEXT = "#E7EAF6"
SIDEBAR_MUTED = "#8891B5"

PALETA_REDES = [AZUL, VERDE, AMARELO, ROXO, ROSA, CIANO]

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
    max-width: 1350px;
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

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG};
    border-right: none;
}}
[data-testid="stSidebar"] * {{
    color: {SIDEBAR_TEXT} !important;
}}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    color: {SIDEBAR_TEXT} !important;
}}
[data-testid="stSidebar"] label {{
    color: {SIDEBAR_MUTED} !important;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {{
    background-color: {SIDEBAR_CARD} !important;
    border: 1px solid #2B355E !important;
    border-radius: 10px !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] * {{
    background-color: transparent !important;
    color: {SIDEBAR_TEXT} !important;
    -webkit-text-fill-color: {SIDEBAR_TEXT} !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] svg {{
    fill: {SIDEBAR_TEXT} !important;
}}
/* Lista de opções do dropdown é renderizada fora da sidebar (portal) */
[data-baseweb="popover"] li {{
    color: #1E293B !important;
}}
[data-baseweb="popover"] li:hover {{
    background-color: #EAF0FF !important;
}}
[data-testid="stSidebar"] .stAlert {{
    background: {SIDEBAR_CARD} !important;
    border-radius: 12px;
    border: 1px solid #262E52;
}}
[data-testid="stSidebar"] hr {{
    border-color: #262E52;
    opacity: 1;
}}
.sidebar-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0 18px 0;
}}
.sidebar-logo-badge {{
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, {AZUL_CLARO}, {AZUL});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}}
.sidebar-logo-title {{
    font-weight: 800;
    font-size: 1.02rem;
    line-height: 1.15;
    color: {SIDEBAR_TEXT};
}}
.sidebar-logo-sub {{
    font-size: 0.72rem;
    color: {SIDEBAR_MUTED};
    letter-spacing: 0.5px;
}}
.sidebar-section-title {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: {SIDEBAR_MUTED};
    text-transform: uppercase;
    margin: 10px 0 2px 0;
}}

/* ---------- HEADER ---------- */
.header-badge {{
    width: 46px;
    height: 46px;
    border-radius: 14px;
    background: linear-gradient(135deg, {AZUL_CLARO}, {AZUL});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}}

/* ---------- KPI CARDS ---------- */
div[data-testid="stMetric"] {{
    background: {BRANCO};
    padding: 18px 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(15, 23, 42, 0.06);
    border: 1px solid #EEF0F4;
}}
div[data-testid="stMetricLabel"] {{
    color: {CINZA_ESCURO};
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
div[data-testid="stMetricValue"] {{
    color: {AZUL};
    font-weight: 800;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    font-size: 1.5rem !important;
    line-height: 1.25 !important;
    word-break: break-word;
}}

/* ---------- TABS (estilo "pill") ---------- */
div[data-testid="stTabs"] button[data-baseweb="tab"] {{
    font-weight: 600;
    color: {CINZA_ESCURO};
    background: {BRANCO};
    border-radius: 10px 10px 0 0;
    padding: 10px 18px;
}}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
    color: {AZUL};
    background: #EAF0FF;
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {AZUL};
}}
div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{
    display: none;
}}
div[data-testid="stTabs"] {{
    background: {BRANCO};
    border-radius: 16px;
    padding: 12px 16px 20px 16px;
    box-shadow: 0px 4px 16px rgba(15, 23, 42, 0.05);
    border: 1px solid #EEF0F4;
}}

/* ---------- Divisores mais discretos ---------- */
hr {{
    margin: 1.6rem 0;
    opacity: 0.15;
}}

/* ---------- Caption ---------- */
[data-testid="stCaptionContainer"] {{
    color: {CINZA_ESCURO};
}}

/* ---------- Info / success / error boxes ---------- */
div[data-testid="stAlert"] {{
    border-radius: 14px;
}}
</style>
""", unsafe_allow_html=True)

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

MUNICIPIO_PRIORIDADE = "Sergipe"  # nome do estado, mantém compatibilidade com o restante do código


# =====================================================
# HELPERS DE LIMPEZA
# =====================================================
def limpar_rede(serie):
    return serie.astype(str).str.replace(r"\s*\(\d+\)", "", regex=True).str.strip()


def normalizar_colunas_ideb(df):
    """Renomeia colunas tipo 'IDEB\\n2021\\n(N x P)' para 'IDEB 2021', corrigindo o typo '20211' -> '2021'."""
    ren = {}
    for c in df.columns:
        if str(c).strip().upper().startswith("IDEB"):
            m = re.search(r"(\d{4,5})", str(c))
            if m:
                ano = m.group(1)
                if ano == "20211":
                    ano = "2021"
                ren[c] = f"IDEB {ano}"
    return df.rename(columns=ren)


def colunas_e_anos_ideb(df):
    colunas_ideb = [c for c in df.columns if str(c).startswith("IDEB ")]
    colunas_ideb = sorted(colunas_ideb, key=lambda c: int(c.replace("IDEB", "").strip()))
    anos = [c.replace("IDEB", "").strip() for c in colunas_ideb]
    return colunas_ideb, anos


def coluna_para_ano(colunas_ideb, anos, ano_desejado):
    """Retorna a coluna IDEB correspondente ao ano desejado; se não existir, usa a mais recente disponível."""
    if ano_desejado in anos:
        return colunas_ideb[anos.index(ano_desejado)]
    return colunas_ideb[-1] if colunas_ideb else None


def normalizar_chave(s):
    """Maiúsculas e sem acento, para casar nomes de abas mesmo com pequenas diferenças entre as bases
    (ex.: 'ENSINO MÉDIO' vs 'ENSINO MEDIO')."""
    s = str(s).strip().upper()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s


def obter_aba_normalizada(bases_dict, chave_referencia):
    """Busca a aba correspondente em bases_dict cujo nome normalizado bate com chave_referencia."""
    alvo = normalizar_chave(chave_referencia)
    for k, v in bases_dict.items():
        if normalizar_chave(k) == alvo:
            return v
    return None


# =====================================================
# CARREGAMENTO — BASE 1 (ESTADOS / BRASIL)
# =====================================================
@st.cache_data
def carregar_estados():
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
            df["Rede"] = limpar_rede(df["Rede"])

        colunas_ideb = [c for c in df.columns if "IDEB" in str(c)]
        for c in colunas_ideb:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df["Nordeste"] = df["Estado"].isin(nordeste)
        bases[nome] = df

    return bases


try:
    bases = carregar_estados()
    estados_ok = True
except FileNotFoundError:
    bases = {}
    estados_ok = False

if not estados_ok:
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
            df["Rede"] = limpar_rede(df["Rede"])

        colunas_ideb = [c for c in df.columns if "IDEB" in str(c)]
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
# CARREGAMENTO — BASE 3 (ESCOLAS DE SERGIPE)
# =====================================================
@st.cache_data
def carregar_escolas():
    arquivo = "BASE ESCOLAS.xlsx"
    abas = pd.read_excel(arquivo, sheet_name=None)

    bases_esc = {}
    for nome, df in abas.items():
        if "Nome do Município" not in df.columns or "Nome da Escola" not in df.columns:
            continue

        df = df.rename(columns={"Nome do Município": "Município", "Nome da Escola": "Escola"})
        df["Município"] = df["Município"].astype(str).str.strip()
        df["Escola"] = df["Escola"].astype(str).str.strip()

        if "Rede" in df.columns:
            df["Rede"] = limpar_rede(df["Rede"])

        df = normalizar_colunas_ideb(df)

        colunas_ideb = [c for c in df.columns if str(c).startswith("IDEB ")]
        colunas_saeb_fluxo = [c for c in df.columns if ("SAEB" in str(c)) or str(c).startswith("FLUXO")]
        for c in colunas_ideb + colunas_saeb_fluxo:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        bases_esc[nome] = df

    return bases_esc


try:
    bases_esc = carregar_escolas()
    escolas_ok = True
except FileNotFoundError:
    bases_esc = {}
    escolas_ok = False

# =====================================================
# FUNÇÕES REUTILIZÁVEIS
# =====================================================
def montar_ranking(df_base, coluna_valor, coluna_nome, prioridade=None):
    """Ordena por nota (desc). Em caso de empate, 'prioridade' vem primeiro (se informado)."""
    tmp = df_base.dropna(subset=[coluna_valor]).copy()
    if prioridade is not None:
        tmp["_p"] = (tmp[coluna_nome] != prioridade).astype(int)
        tmp = tmp.sort_values(by=[coluna_valor, "_p"], ascending=[False, True]).drop(columns="_p").reset_index(drop=True)
    else:
        tmp = tmp.sort_values(by=coluna_valor, ascending=False).reset_index(drop=True)
    tmp["Posição"] = tmp.index + 1
    return tmp


def grafico_ranking(df_rank, coluna_valor, coluna_nome, destaque=None,
                     cor_destaque=AZUL, cor_padrao=CINZA, altura=600):
    dados = df_rank.copy()
    dados["Label"] = dados["Posição"].astype(str) + "º  " + dados[coluna_nome]
    cores = [cor_destaque if v == destaque else cor_padrao for v in dados[coluna_nome]]

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


def grafico_evolucao(anos, valores, cor_linha=AZUL, cor_preenchimento="rgba(30,58,138,0.08)", altura=520):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos,
        y=valores,
        mode="lines+markers+text",
        line=dict(color=cor_linha, width=5, shape="spline"),
        marker=dict(size=13, color=AMARELO, line=dict(color=cor_linha, width=2)),
        fill="tozeroy",
        fillcolor=cor_preenchimento,
        text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores],
        textposition="top center",
        textfont=dict(size=13, color=cor_linha),
        cliponaxis=False
    ))
    max_val = max([v for v in valores if pd.notna(v)] + [0])
    fig.update_layout(
        template="plotly_white",
        height=altura,
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
    return fig


def grafico_comparativo_redes(anos, series_por_rede):
    """series_por_rede: lista de tuplas (nome_rede, valores)"""
    fig = go.Figure()
    max_val = 0
    for i, (rede_nome, valores) in enumerate(series_por_rede):
        max_local = max([v for v in valores if pd.notna(v)] + [0])
        max_val = max(max_val, max_local)
        fig.add_trace(go.Scatter(
            x=anos,
            y=valores,
            mode="lines+markers+text",
            name=rede_nome,
            line=dict(width=4, color=PALETA_REDES[i % len(PALETA_REDES)], shape="spline"),
            marker=dict(size=11),
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in valores],
            textposition="top center",
            cliponaxis=False
        ))
    fig.update_layout(
        template="plotly_white",
        height=520,
        font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Ano",
        yaxis_title="Nota IDEB",
        xaxis=dict(type="category", range=[-0.5, len(anos) - 0.5]),
        yaxis=dict(range=[0, max_val + 1.5]),
        margin=dict(l=40, r=40, t=60, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def melhor_pior(ranking_df, coluna_valor, coluna_nome, rotulo):
    c1, c2 = st.columns(2)
    if not ranking_df.empty:
        with c1:
            melhor = ranking_df.iloc[0]
            st.success(f"🏆 **Melhor colocado ({rotulo})**\n\n**{melhor[coluna_nome]}**  •  Nota: **{melhor[coluna_valor]:.1f}**")
        with c2:
            pior = ranking_df.iloc[-1]
            st.error(f"📉 **Último colocado ({rotulo})**\n\n**{pior[coluna_nome]}**  •  Nota: **{pior[coluna_valor]:.1f}**")


def tabela_e_download(ranking_df, chave, nome_arquivo):
    st.divider()
    st.subheader("📋 Base utilizada")
    mostrar = st.checkbox("Mostrar tabela completa", key=f"mostrar_{chave}")
    if mostrar:
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
        csv = ranking_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Baixar tabela (CSV)",
            data=csv,
            file_name=nome_arquivo.replace(" ", "_"),
            mime="text/csv",
            key=f"download_{chave}"
        )


GEOJSON_ESTADOS_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
GEOJSON_MUNICIPIOS_SE_URL = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-28-mun.json"


@st.cache_data
def carregar_geojson(url):
    import requests
    resposta = requests.get(url, timeout=15)
    resposta.raise_for_status()
    return resposta.json()


# =====================================================
# CABEÇALHO
# =====================================================
col_badge, col_titulo = st.columns([0.06, 0.94])
with col_badge:
    st.markdown('<div class="header-badge">🎓</div>', unsafe_allow_html=True)
with col_titulo:
    st.markdown("### Painel Educacional")
    st.caption("Acompanhe os indicadores de qualidade da educação em Sergipe  •  Fonte: INEP")

st.divider()

# =====================================================
# SIDEBAR — NAVEGAÇÃO / FILTROS
# =====================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-badge">🎓</div>
        <div>
            <div class="sidebar-logo-title">Painel<br>Educacional</div>
            <div class="sidebar-logo-sub">IDEB</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">🔎 Filtros de navegação</div>', unsafe_allow_html=True)

    etapa = st.selectbox("Etapa de Ensino", list(bases.keys()))
    df_completo = bases[etapa]
    colunas_ideb = [c for c in df_completo.columns if "IDEB" in str(c)]
    anos = [c.replace("IDEB", "").strip() for c in colunas_ideb]
    ano_ref = st.selectbox("Ano de Referência", anos, index=len(anos) - 1)

    municipio_sel = None
    escola_sel = None

    df_mun_side = obter_aba_normalizada(bases_mun, etapa) if municipios_ok else None
    if df_mun_side is not None:
        municipios_disponiveis = sorted(df_mun_side["Município"].dropna().unique())
        idx_padrao = municipios_disponiveis.index("Aracaju") if "Aracaju" in municipios_disponiveis else 0
        municipio_sel = st.selectbox("Município em destaque", municipios_disponiveis, index=idx_padrao)

    df_esc_side = obter_aba_normalizada(bases_esc, etapa) if escolas_ok else None
    if df_esc_side is not None and municipio_sel is not None:
        escolas_municipio = sorted(df_esc_side[df_esc_side["Município"] == municipio_sel]["Escola"].dropna().unique())
        if escolas_municipio:
            escola_sel = st.selectbox("Escola em destaque", escolas_municipio)
        else:
            st.caption("Nenhuma escola cadastrada para este município nesta etapa.")

    st.markdown("---")
    st.info(f"**Fonte:** INEP\n\n**Etapa:** {etapa}\n\n**Ano:** {ano_ref}")

    if not municipios_ok:
        st.warning("⚠️ **BASE 2 IDEB BRASIL.xlsx** não encontrada. A aba de Municípios ficará indisponível.")
    if not escolas_ok:
        st.warning("⚠️ **BASE ESCOLAS.xlsx** não encontrada. A aba de Escolas ficará indisponível.")

    st.caption("Desenvolvido em Streamlit  •  Atualização automática da base")

# =====================================================
# ABAS PRINCIPAIS
# =====================================================
tab_estado, tab_municipio, tab_escola = st.tabs([
    "📊 Panorama Estadual",
    "🏙️ Raio-X Municipal",
    "🎓 Perfil da Escola"
])

# =====================================================
# TAB 1 — PANORAMA ESTADUAL (BASE 1)
# =====================================================
with tab_estado:
    if "Rede" in df_completo.columns:
        rede = st.selectbox("Rede", sorted(df_completo["Rede"].dropna().unique()), key="rede_estado_sel")
        df = df_completo[df_completo["Rede"] == rede]
    else:
        rede = "Todas"
        df = df_completo

    coluna_atual = coluna_para_ano(colunas_ideb, anos, ano_ref)
    idx_atual = anos.index(ano_ref) if ano_ref in anos else len(anos) - 1
    coluna_anterior = colunas_ideb[idx_atual - 1] if idx_atual > 0 else None

    regioes = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

    ranking = montar_ranking(df[~df["Estado"].isin(regioes)], coluna_atual, "Estado", MUNICIPIO_PRIORIDADE)
    ranking_ne = montar_ranking(df[(~df["Estado"].isin(regioes)) & (df["Nordeste"])], coluna_atual, "Estado", MUNICIPIO_PRIORIDADE)

    sergipe = df[df["Estado"] == "Sergipe"]

    if not sergipe.empty and pd.notna(sergipe.iloc[0][coluna_atual]):
        nota = float(sergipe.iloc[0][coluna_atual])
        nota_anterior = float(sergipe.iloc[0][coluna_anterior]) if coluna_anterior and pd.notna(sergipe.iloc[0][coluna_anterior]) else None
        try:
            posicao_br = int(ranking.loc[ranking["Estado"] == "Sergipe", "Posição"].iloc[0])
        except IndexError:
            posicao_br = None
        try:
            posicao_ne = int(ranking_ne.loc[ranking_ne["Estado"] == "Sergipe", "Posição"].iloc[0])
        except IndexError:
            posicao_ne = None
    else:
        nota = nota_anterior = posicao_br = posicao_ne = None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_nota = f"{nota - nota_anterior:+.1f}" if nota is not None and nota_anterior is not None else None
        st.metric("🎯 IDEB Sergipe", f"{nota:.1f}" if nota is not None else "—", delta=delta_nota)
    with c2:
        st.metric("🇧🇷 Ranking Brasil", f"{posicao_br}º" if posicao_br else "—")
    with c3:
        st.metric("🌵 Ranking Nordeste", f"{posicao_ne}º" if posicao_ne else "—")
    with c4:
        st.metric("🏛️ Rede", rede)

    st.markdown("")

    sub1, sub2, sub3, sub4, sub5 = st.tabs([
        "🇧🇷 Ranking Brasil", "🌵 Ranking Nordeste", "📈 Série Histórica",
        "🏛️ Comparativo por Rede", "🗺️ Mapa Brasil"
    ])

    with sub1:
        st.caption(f"{etapa} • {rede} • {ano_ref}")
        st.plotly_chart(grafico_ranking(ranking, coluna_atual, "Estado", destaque="Sergipe", altura=900), use_container_width=True)

    with sub2:
        st.caption(f"{etapa} • {rede} • {ano_ref}")
        st.plotly_chart(grafico_ranking(ranking_ne, coluna_atual, "Estado", destaque="Sergipe", cor_padrao=VERDE, altura=600), use_container_width=True)

    with sub3:
        st.caption(f"Evolução do IDEB — Sergipe ({rede})")
        if not sergipe.empty:
            valores = sergipe[colunas_ideb].iloc[0].astype(float).values
            st.plotly_chart(grafico_evolucao(anos, valores), use_container_width=True)
        else:
            st.warning("Não existem dados históricos para Sergipe nesta rede.")

    with sub4:
        st.caption(f"Comparativo de redes em Sergipe • {etapa}")
        df_se_todas_redes = df_completo[df_completo["Estado"] == "Sergipe"]
        if not df_se_todas_redes.empty and "Rede" in df_se_todas_redes.columns:
            redes_disponiveis = sorted(df_se_todas_redes["Rede"].dropna().unique())
            redes_padrao = [r for r in ["Estadual", "Municipal", "Privada", "Pública"] if r in redes_disponiveis][:3] or redes_disponiveis[:2]
            redes_selecionadas = st.multiselect("Selecione as redes:", options=redes_disponiveis, default=redes_padrao, key="redes_estado")
            if redes_selecionadas:
                series = []
                for rede_nome in redes_selecionadas:
                    df_r = df_se_todas_redes[df_se_todas_redes["Rede"] == rede_nome]
                    if not df_r.empty:
                        series.append((rede_nome, df_r[colunas_ideb].iloc[0].astype(float).values))
                st.plotly_chart(grafico_comparativo_redes(anos, series), use_container_width=True)
            else:
                st.info("Selecione pelo menos uma rede acima.")
        else:
            st.warning("Não há dados de diferentes redes para Sergipe nesta base.")

    with sub5:
        st.caption(f"Mapa do Brasil • {etapa} ({rede}) • {ano_ref}")
        df_mapa = ranking.copy()
        try:
            geojson = carregar_geojson(GEOJSON_ESTADOS_URL)
            fig6 = px.choropleth(
                df_mapa, geojson=geojson, locations="Estado", featureidkey="properties.name",
                color=coluna_atual, color_continuous_scale=[CINZA, AZUL_CLARO, AZUL],
                hover_name="Estado", hover_data={coluna_atual: ":.1f", "Posição": True, "Estado": False},
            )
            fig6.update_traces(marker_line_color="white", marker_line_width=0.8)
            fig6.update_geos(fitbounds="locations", visible=False)
            fig6.update_layout(template="plotly_white", height=650, margin=dict(l=0, r=0, t=10, b=0),
                                font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                                coloraxis_colorbar=dict(title="Nota IDEB"))
            st.plotly_chart(fig6, use_container_width=True)
            st.caption("Passe o mouse sobre um estado para ver a nota e a posição no ranking.")
        except Exception as e:
            st.warning("⚠️ Não foi possível carregar o contorno geográfico dos estados (é necessária conexão com a internet na primeira execução).")
            st.caption(f"Detalhe técnico: {e}")

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
        fig5.add_trace(go.Bar(x=comp["Local"], y=comp["Nota"], marker=dict(color=cores_comp),
                               text=comp["Nota"].round(1), textposition="outside",
                               textfont=dict(size=13, color=CINZA_ESCURO)))
        fig5.update_layout(template="plotly_white", height=400, showlegend=False,
                            font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                            yaxis_title="Nota IDEB", plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    melhor_pior(ranking, coluna_atual, "Estado", rede)
    tabela_e_download(ranking, "estado", f"ideb_{etapa}_{rede}_{ano_ref}.csv")

# =====================================================
# TAB 2 — RAIO-X MUNICIPAL (BASE 2)
# =====================================================
with tab_municipio:
    df_mun_completo = obter_aba_normalizada(bases_mun, etapa) if municipios_ok else None

    if not municipios_ok:
        st.error("⚠️ Arquivo **BASE 2 IDEB BRASIL.xlsx** não encontrado. Coloque-o na mesma pasta do app.")
    elif df_mun_completo is None:
        st.warning(f"Não há dados de municípios para a etapa **{etapa}**.")
    else:
        if "Rede" in df_mun_completo.columns:
            rede_mun = st.selectbox("Rede", sorted(df_mun_completo["Rede"].dropna().unique()), key="rede_mun_sel")
            df_mun = df_mun_completo[df_mun_completo["Rede"] == rede_mun]
        else:
            rede_mun = "Todas"
            df_mun = df_mun_completo

        colunas_ideb_mun, anos_mun = colunas_e_anos_ideb(df_mun)
        coluna_atual_mun = coluna_para_ano(colunas_ideb_mun, anos_mun, ano_ref)
        idx_atual_mun = anos_mun.index(coluna_atual_mun.replace("IDEB", "").strip())
        coluna_anterior_mun = colunas_ideb_mun[idx_atual_mun - 1] if idx_atual_mun > 0 else None

        municipios_disponiveis = sorted(df_mun["Município"].dropna().unique())
        municipio_foco = municipio_sel if municipio_sel in municipios_disponiveis else (municipios_disponiveis[0] if municipios_disponiveis else None)

        ranking_mun = montar_ranking(df_mun, coluna_atual_mun, "Município", municipio_foco)
        alvo = df_mun[df_mun["Município"] == municipio_foco] if municipio_foco else pd.DataFrame()

        if not alvo.empty and pd.notna(alvo.iloc[0][coluna_atual_mun]):
            nota_mun = float(alvo.iloc[0][coluna_atual_mun])
            nota_mun_anterior = float(alvo.iloc[0][coluna_anterior_mun]) if coluna_anterior_mun and pd.notna(alvo.iloc[0][coluna_anterior_mun]) else None
            try:
                posicao_mun = int(ranking_mun.loc[ranking_mun["Município"] == municipio_foco, "Posição"].iloc[0])
            except IndexError:
                posicao_mun = None
        else:
            nota_mun = nota_mun_anterior = posicao_mun = None

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            delta_mun = f"{nota_mun - nota_mun_anterior:+.1f}" if nota_mun is not None and nota_mun_anterior is not None else None
            st.metric(f"🎯 IDEB {municipio_foco}", f"{nota_mun:.1f}" if nota_mun is not None else "—", delta=delta_mun)
        with mc2:
            st.metric("📊 Ranking entre Municípios/SE", f"{posicao_mun}º" if posicao_mun else "—")
        with mc3:
            st.metric("🏙️ Total de Municípios", f"{len(municipios_disponiveis)}")
        with mc4:
            st.metric("🏛️ Rede", rede_mun)

        st.markdown("")

        msub1, msub2, msub3, msub4 = st.tabs([
            "📊 Ranking dos Municípios", "📈 Série Histórica", "🏛️ Comparativo por Rede", "🗺️ Mapa de Sergipe"
        ])

        with msub1:
            st.caption(f"{etapa} • {rede_mun} • {ano_ref}")
            st.plotly_chart(
                grafico_ranking(ranking_mun, coluna_atual_mun, "Município", destaque=municipio_foco, altura=1400),
                use_container_width=True
            )

        with msub2:
            st.caption(f"Evolução do IDEB — {municipio_foco} ({rede_mun})")
            if not alvo.empty:
                valores_mun = alvo[colunas_ideb_mun].iloc[0].astype(float).values
                st.plotly_chart(
                    grafico_evolucao(anos_mun, valores_mun, cor_linha=VERDE, cor_preenchimento="rgba(5,150,105,0.08)"),
                    use_container_width=True
                )
            else:
                st.warning(f"Não existem dados históricos para {municipio_foco} nesta rede.")

        with msub3:
            st.caption(f"Comparativo de redes em {municipio_foco} • {etapa}")
            df_mun_todas_redes = df_mun_completo[df_mun_completo["Município"] == municipio_foco]
            if not df_mun_todas_redes.empty and "Rede" in df_mun_todas_redes.columns:
                redes_mun_disponiveis = sorted(df_mun_todas_redes["Rede"].dropna().unique())
                redes_mun_padrao = [r for r in ["Estadual", "Municipal", "Federal", "Pública"] if r in redes_mun_disponiveis][:3] or redes_mun_disponiveis[:2]
                redes_mun_selecionadas = st.multiselect("Selecione as redes:", options=redes_mun_disponiveis, default=redes_mun_padrao, key="redes_municipio")
                if redes_mun_selecionadas:
                    series = []
                    for rede_nome in redes_mun_selecionadas:
                        df_r_mun = df_mun_todas_redes[df_mun_todas_redes["Rede"] == rede_nome]
                        if not df_r_mun.empty:
                            series.append((rede_nome, df_r_mun[colunas_ideb_mun].iloc[0].astype(float).values))
                    st.plotly_chart(grafico_comparativo_redes(anos_mun, series), use_container_width=True)
                else:
                    st.info("Selecione pelo menos uma rede acima.")
            else:
                st.warning(f"Não há dados de diferentes redes para {municipio_foco} nesta base.")

        with msub4:
            st.caption(f"Mapa de Sergipe • {etapa} ({rede_mun}) • {ano_ref}")
            df_mapa_mun = ranking_mun.copy()
            try:
                geojson_mun = carregar_geojson(GEOJSON_MUNICIPIOS_SE_URL)
                fig_mapa_mun = px.choropleth(
                    df_mapa_mun, geojson=geojson_mun, locations="Município", featureidkey="properties.name",
                    color=coluna_atual_mun, color_continuous_scale=[CINZA, VERDE, "#064E3B"],
                    hover_name="Município", hover_data={coluna_atual_mun: ":.1f", "Posição": True, "Município": False},
                )
                fig_mapa_mun.update_traces(marker_line_color="white", marker_line_width=0.8)
                fig_mapa_mun.update_geos(fitbounds="locations", visible=False)
                fig_mapa_mun.update_layout(template="plotly_white", height=650, margin=dict(l=0, r=0, t=10, b=0),
                                            font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                                            coloraxis_colorbar=dict(title="Nota IDEB"))
                st.plotly_chart(fig_mapa_mun, use_container_width=True)
                st.caption("Passe o mouse sobre um município para ver a nota e a posição no ranking.")
            except Exception as e:
                st.warning("⚠️ Não foi possível carregar o contorno geográfico dos municípios (é necessária conexão com a internet na primeira execução).")
                st.caption(f"Detalhe técnico: {e}")

        st.divider()
        melhor_pior(ranking_mun, coluna_atual_mun, "Município", rede_mun)
        tabela_e_download(ranking_mun, "municipio", f"ideb_municipios_se_{etapa}_{rede_mun}_{ano_ref}.csv")

# =====================================================
# TAB 3 — PERFIL DA ESCOLA (BASE 3)
# =====================================================
with tab_escola:
    df_esc_etapa = obter_aba_normalizada(bases_esc, etapa) if escolas_ok else None

    if not escolas_ok:
        st.error("⚠️ Arquivo **BASE ESCOLAS.xlsx** não encontrado. Coloque-o na mesma pasta do app.")
    elif df_esc_etapa is None:
        st.warning(f"Não há dados de escolas para a etapa **{etapa}**.")
    elif municipio_sel is None:
        st.info("Selecione um município na barra lateral para ver o raio-x das escolas.")
    else:
        df_esc_municipio = df_esc_etapa[df_esc_etapa["Município"] == municipio_sel]

        if df_esc_municipio.empty:
            st.warning(f"Não há escolas cadastradas em **{municipio_sel}** para a etapa **{etapa}**.")
        else:
            colunas_ideb_esc, anos_esc = colunas_e_anos_ideb(df_esc_municipio)
            coluna_atual_esc = coluna_para_ano(colunas_ideb_esc, anos_esc, ano_ref)
            idx_atual_esc = anos_esc.index(coluna_atual_esc.replace("IDEB", "").strip())
            coluna_anterior_esc = colunas_ideb_esc[idx_atual_esc - 1] if idx_atual_esc > 0 else None

            escolas_disponiveis = sorted(df_esc_municipio["Escola"].dropna().unique())
            escola_foco = escola_sel if escola_sel in escolas_disponiveis else escolas_disponiveis[0]

            ranking_esc = montar_ranking(df_esc_municipio, coluna_atual_esc, "Escola", escola_foco)
            alvo_esc = df_esc_municipio[df_esc_municipio["Escola"] == escola_foco]

            if not alvo_esc.empty and pd.notna(alvo_esc.iloc[0][coluna_atual_esc]):
                nota_esc = float(alvo_esc.iloc[0][coluna_atual_esc])
                nota_esc_anterior = float(alvo_esc.iloc[0][coluna_anterior_esc]) if coluna_anterior_esc and pd.notna(alvo_esc.iloc[0][coluna_anterior_esc]) else None
                try:
                    posicao_esc = int(ranking_esc.loc[ranking_esc["Escola"] == escola_foco, "Posição"].iloc[0])
                except IndexError:
                    posicao_esc = None
            else:
                nota_esc = nota_esc_anterior = posicao_esc = None

            rede_escola = alvo_esc.iloc[0]["Rede"] if not alvo_esc.empty and "Rede" in alvo_esc.columns else "—"

            saeb_mat_2025 = alvo_esc.iloc[0].get("NOTA SAEB 2025 - Matemática") if not alvo_esc.empty else None
            saeb_port_2025 = alvo_esc.iloc[0].get("NOTA SAEB 2025 - Língua Portuguesa") if not alvo_esc.empty else None
            fluxo_2025 = alvo_esc.iloc[0].get("FLUXO 2025") if not alvo_esc.empty else None

            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                delta_esc = f"{nota_esc - nota_esc_anterior:+.1f}" if nota_esc is not None and nota_esc_anterior is not None else None
                st.metric("🎯 IDEB da Escola", f"{nota_esc:.1f}" if nota_esc is not None else "—", delta=delta_esc)
            with ec2:
                st.metric("📊 Ranking no Município", f"{posicao_esc}º" if posicao_esc else "—")
            with ec3:
                st.metric("🏛️ Rede", rede_escola)

            ec4, ec5 = st.columns(2)
            with ec4:
                st.metric("🔢 Matemática (SAEB 2025)", f"{saeb_mat_2025:.1f}" if pd.notna(saeb_mat_2025) else "—")
            with ec5:
                st.metric("📚 Português (SAEB 2025)", f"{saeb_port_2025:.1f}" if pd.notna(saeb_port_2025) else "—")

            st.markdown("")

            esub1, esub2, esub3, esub4 = st.tabs([
                "📊 Ranking de Escolas", "📈 Evolução Histórica", "🧮 Desempenho SAEB", "🔁 Fluxo Escolar"
            ])

            with esub1:
                st.caption(f"Escolas de {municipio_sel} • {etapa} • {ano_ref}")
                altura_rank_esc = max(400, 32 * len(ranking_esc))
                st.plotly_chart(
                    grafico_ranking(ranking_esc, coluna_atual_esc, "Escola", destaque=escola_foco,
                                     cor_padrao=ROXO, altura=altura_rank_esc),
                    use_container_width=True
                )

            with esub2:
                st.caption(f"Evolução do IDEB — {escola_foco}")
                if not alvo_esc.empty:
                    valores_esc = alvo_esc[colunas_ideb_esc].iloc[0].astype(float).values
                    st.plotly_chart(
                        grafico_evolucao(anos_esc, valores_esc, cor_linha=ROXO, cor_preenchimento="rgba(124,58,237,0.08)"),
                        use_container_width=True
                    )
                else:
                    st.warning("Não existem dados históricos de IDEB para esta escola.")

            with esub3:
                st.caption(f"Notas do SAEB — {escola_foco}")
                ano_saeb = st.radio("Ano do SAEB", ["2025", "2023"], horizontal=True, key="ano_saeb_sel")
                col_mat = f"NOTA SAEB {ano_saeb} - Matemática" if ano_saeb == "2025" else f"NOTA SAEB {ano_saeb} -Matemática"
                col_port = f"NOTA SAEB {ano_saeb} - Língua Portuguesa" if ano_saeb == "2025" else f"NOTA SAEB {ano_saeb} -Língua Portuguesa"

                if col_mat in alvo_esc.columns and col_port in alvo_esc.columns and not alvo_esc.empty:
                    mat_val = alvo_esc.iloc[0][col_mat]
                    port_val = alvo_esc.iloc[0][col_port]
                    if pd.notna(mat_val) or pd.notna(port_val):
                        fig_saeb = go.Figure()
                        fig_saeb.add_trace(go.Bar(
                            x=["Matemática", "Língua Portuguesa"],
                            y=[mat_val, port_val],
                            marker=dict(color=[AZUL_CLARO, ROXO]),
                            text=[f"{v:.1f}" if pd.notna(v) else "—" for v in [mat_val, port_val]],
                            textposition="outside",
                            textfont=dict(size=14, color=CINZA_ESCURO)
                        ))
                        fig_saeb.update_layout(
                            template="plotly_white", height=420, showlegend=False,
                            font=dict(family="Inter, sans-serif", color=CINZA_ESCURO),
                            yaxis_title="Nota SAEB", plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(fig_saeb, use_container_width=True)
                    else:
                        st.info(f"Não há notas de SAEB {ano_saeb} disponíveis para esta escola.")
                else:
                    st.info(f"Não há dados de SAEB {ano_saeb} disponíveis para esta etapa.")

            with esub4:
                st.caption(f"Índice de Fluxo 2025 — {escola_foco}")
                if pd.notna(fluxo_2025):
                    fig_fluxo = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=round(float(fluxo_2025) * 100, 1),
                        number={"suffix": "%", "font": {"color": VERDE, "size": 40}},
                        gauge={
                            "axis": {"range": [0, 100], "tickcolor": CINZA_ESCURO},
                            "bar": {"color": VERDE},
                            "bgcolor": "white",
                            "borderwidth": 0,
                            "steps": [
                                {"range": [0, 50], "color": "#FEE2E2"},
                                {"range": [50, 80], "color": "#FEF3C7"},
                                {"range": [80, 100], "color": "#D1FAE5"},
                            ],
                        }
                    ))
                    fig_fluxo.update_layout(height=350, margin=dict(l=30, r=30, t=30, b=10),
                                             font=dict(family="Inter, sans-serif", color=CINZA_ESCURO))
                    st.plotly_chart(fig_fluxo, use_container_width=True)
                    st.caption("O índice de fluxo mede a proporção de aprovação/progressão dos estudantes, componente P do cálculo do IDEB.")
                else:
                    st.info("Não há dado de fluxo 2025 disponível para esta escola.")

            st.divider()
            melhor_pior(ranking_esc, coluna_atual_esc, "Escola", f"{municipio_sel} • {etapa}")
            tabela_e_download(ranking_esc, "escola", f"ideb_escolas_{municipio_sel}_{etapa}_{ano_ref}.csv")

# =====================================================
# RODAPÉ
# =====================================================
st.divider()
st.caption("Painel desenvolvido em Streamlit  •  Fonte: INEP  •  Atualização automática da base.")
