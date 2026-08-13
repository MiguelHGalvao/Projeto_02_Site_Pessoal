from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_utils import (
    buscar_dados_ativo,
    buscar_historico,
    calcular_teto_bazin,
    calcular_teto_gordon,
    calcular_teto_graham,
    calcular_teto_medio,
    classificar_status,
    margem_seguranca,
)
from theme import (
    DEFAULT_MODO,
    DEFAULT_PALETA,
    MODOS,
    PALETAS,
    build_theme_css,
    get_active_accents,
)

try:
    import google.generativeai as genai
except ImportError: # biblioteca opcional
    genai = None

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# ==========================================
st.set_page_config(
    page_title="Plataforma de Análise Financeira",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


def carregar_css():
    try:
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo style.css não encontrado — usando estilo padrão do Streamlit.")


carregar_css()

st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("Painel de Controle")

# ==========================================
# SELETOR DE TEMA (cor de destaque + modo claro/escuro)
# ==========================================
if "tema_modo" not in st.session_state:
    st.session_state["tema_modo"] = DEFAULT_MODO
if "tema_paleta" not in st.session_state:
    st.session_state["tema_paleta"] = DEFAULT_PALETA
if "tema_personalizado" not in st.session_state:
    st.session_state["tema_personalizado"] = False

with st.sidebar.expander("Aparência", expanded=False):
    st.session_state["tema_modo"] = st.radio(
        "Modo", list(MODOS.keys()), horizontal=True, index=list(MODOS.keys()).index(st.session_state["tema_modo"])
    )
    st.session_state["tema_personalizado"] = st.checkbox(
        "Usar cor personalizada", value=st.session_state["tema_personalizado"]
    )

    accent_custom = None
    accent_strong_custom = None
    if st.session_state["tema_personalizado"]:
        c1, c2 = st.columns(2)
        accent_custom = c1.color_picker("Destaque", value="#38BDF8")
        accent_strong_custom = c2.color_picker("Destaque forte", value="#0284C7")
    else:
        st.session_state["tema_paleta"] = st.selectbox(
            "Paleta de cores",
            list(PALETAS.keys()),
            index=list(PALETAS.keys()).index(st.session_state["tema_paleta"]),
        )

# Injeta o CSS de tema DEPOIS do style.css base, para sobrescrever as variáveis via cascata
st.markdown(
    f"<style>{build_theme_css(st.session_state['tema_paleta'], st.session_state['tema_modo'], accent_custom, accent_strong_custom)}</style>",
    unsafe_allow_html=True,
)

CORES_ATIVAS = get_active_accents(st.session_state["tema_paleta"], accent_custom, accent_strong_custom)
ACCENT = CORES_ATIVAS["accent"]
ACCENT_STRONG = CORES_ATIVAS["accent_strong"]
PLOTLY_TEMPLATE_ATIVO = "plotly_dark" if st.session_state["tema_modo"] == "Escuro" else "plotly_white"

IMG_STOCK_MARKET = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=500&q=80"
IMG_ANALYTICS = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&q=80"
IMG_REAL_ESTATE = "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500&q=80"
IMG_GLOBAL = "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=500&q=80"

PLOTLY_CONFIG = {"displayModeBar": False}


def card_html(titulo: str, valor: str, subtexto: str = "", img: str | None = None) -> str:
    img_tag = f'<img src="{img}" class="card-image">' if img else ""
    return f"""
        <div class="card-container">
            {img_tag}
            <div class="card-content">
                <div class="card-title">{titulo}</div>
                <div class="card-value">{valor}</div>
                <div class="card-subtext">{subtexto}</div>
            </div>
        </div>
    """


# ==========================================
# SIDEBAR / NAVEGAÇÃO
# ==========================================
aba = st.sidebar.radio(
    "Selecione o Módulo:",
    [
        "Dashboard da Carteira",
        "Valuation Individual",
        "Comparador de Ativos",
        "Simulador de Aportes",
        "Análise via IA Gemini",
        "Guia do Usuário / Tutorial",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Integração IA")
gemini_api_key = st.sidebar.text_input(
    "Chave API Google Gemini:", type="password", help="Obtenha gratuitamente em aistudio.google.com/app/apikey"
)
st.sidebar.caption("Sua chave é usada apenas nesta sessão local e nunca é armazenada.")

st.sidebar.markdown("---")
st.sidebar.caption("Dados via Yahoo Finance (yfinance), com fallback para brapi.dev.")

# ==========================================
# ABA 1: DASHBOARD DA CARTEIRA
# ==========================================
if aba == "Dashboard da Carteira":
    st.title("Gestão e Consolidação de Carteira")
    st.write("Gerencie seus ativos, calcule margens de segurança e acompanhe a evolução patrimonial.")

    if "carteira_inicial" not in st.session_state:
        st.session_state["carteira_inicial"] = pd.DataFrame(
            [
                {"Ticker": "BBAS3", "Tipo": "Ação", "Quantidade": 100, "Preço Médio": 24.50},
                {"Ticker": "VALE3", "Tipo": "Ação", "Quantidade": 50, "Preço Médio": 62.00},
                {"Ticker": "MXRF11", "Tipo": "FII", "Quantidade": 300, "Preço Médio": 10.15},
                {"Ticker": "HGLG11", "Tipo": "FII", "Quantidade": 20, "Preço Médio": 160.00},
                {"Ticker": "AAPL34", "Tipo": "BDR", "Quantidade": 30, "Preço Médio": 42.00},
            ]
        )

    df_edit = st.data_editor(
        st.session_state["carteira_inicial"],
        num_rows="dynamic",
        use_container_width=True,
        key="editor_carteira",
        column_config={
            "Tipo": st.column_config.SelectboxColumn(options=["Ação", "FII", "BDR", "ETF"]),
            "Quantidade": st.column_config.NumberColumn(min_value=0, step=1),
            "Preço Médio": st.column_config.NumberColumn(min_value=0.0, format="R$ %.2f"),
        },
    )

    dy_alvo_dash = st.slider("DY Alvo (Método Bazin)", 2.0, 15.0, 6.0, 0.5, format="%.1f%%") / 100

    processar = st.button("Processar Carteira Completa", type="primary", use_container_width=True)

    if processar:
        resultados = []
        erros = []
        linhas = df_edit.dropna(subset=["Ticker"]).reset_index(drop=True)
        total = max(len(linhas), 1)
        barra = st.progress(0.0, text="Iniciando...")

        for i, row in linhas.iterrows():
            ticker = str(row["Ticker"]).upper().strip()
            if not ticker:
                continue

            barra.progress((i + 1) / total, text=f"Buscando {ticker}...")
            info = buscar_dados_ativo(ticker, row["Tipo"])

            if not info["ok"]:
                erros.append(f"{ticker}: {info.get('erro', 'erro desconhecido')}")
                continue

            preco = info["preco"]
            qtd = float(row["Quantidade"] or 0)
            pm = float(row["Preço Médio"] or 0)

            tot_investido = qtd * pm
            tot_atual = qtd * preco
            lucro_reais = tot_atual - tot_investido
            lucro_pct = (lucro_reais / tot_investido * 100) if tot_investido > 0 else 0.0

            teto_bazin = calcular_teto_bazin(info["div_12m"], dy_alvo_dash)
            teto_graham = calcular_teto_graham(info["lpa"], info["vpa"]) if row["Tipo"] == "Ação" else 0.0
            teto_medio = calcular_teto_medio(teto_bazin, teto_graham)
            status, css_class = classificar_status(preco, teto_medio if teto_medio > 0 else teto_bazin)

            resultados.append(
                {
                    "Ticker": ticker,
                    "Tipo": row["Tipo"],
                    "Qtd": qtd,
                    "P. Médio": pm,
                    "P. Atual": round(preco, 2),
                    "Total Investido": round(tot_investido, 2),
                    "Valor Atual": round(tot_atual, 2),
                    "Resultado ($)": round(lucro_reais, 2),
                    "Rentab. (%)": round(lucro_pct, 2),
                    "Div. 12M": round(info["div_12m"], 2),
                    "DY (%)": round(info["dy_pct"], 2),
                    "Teto Bazin": round(teto_bazin, 2),
                    "Teto Graham": round(teto_graham, 2) if row["Tipo"] == "Ação" else None,
                    "Margem Seg. (%)": round(margem_seguranca(preco, teto_medio if teto_medio > 0 else teto_bazin), 2),
                    "Status": status,
                }
            )

        barra.empty()
        if erros:
            st.warning("Não foi possível obter dados para: " + "; ".join(erros))

        if resultados:
            st.session_state["df_carteira"] = pd.DataFrame(resultados)
        elif not erros:
            st.info("Nenhum ativo válido informado.")

    if "df_carteira" in st.session_state:
        df_c = st.session_state["df_carteira"]

        tot_inv = df_c["Total Investido"].sum()
        tot_at = df_c["Valor Atual"].sum()
        lucro_tot = tot_at - tot_inv
        rent_tot = (lucro_tot / tot_inv * 100) if tot_inv > 0 else 0.0
        renda_anual_est = (df_c["Qtd"] * df_c["Div. 12M"]).sum()

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                card_html("Patrimônio Atual", f"R$ {tot_at:,.2f}", f"Rentabilidade: {rent_tot:.2f}%", IMG_STOCK_MARKET),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                card_html("Total Investido", f"R$ {tot_inv:,.2f}", "Custo Histórico", IMG_ANALYTICS),
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                card_html("Lucro / Prejuízo", f"R$ {lucro_tot:,.2f}", "Ganho de Capital", IMG_REAL_ESTATE),
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                card_html(
                    "Renda Passiva Anual",
                    f"R$ {renda_anual_est:,.2f}",
                    f"Média R$ {renda_anual_est / 12:,.2f}/mês",
                    IMG_GLOBAL,
                ),
                unsafe_allow_html=True,
            )

        st.subheader("Tabela de Ativos da Carteira")
        st.dataframe(
            df_c,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Margem Seg. (%)": st.column_config.ProgressColumn(
                    "Margem Seg. (%)", min_value=-30, max_value=30, format="%.1f%%"
                ),
                "Rentab. (%)": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

        csv_buffer = io.StringIO()
        df_c.to_csv(csv_buffer, index=False, sep=";", decimal=",")
        st.download_button(
            "Exportar carteira processada (CSV)",
            data=csv_buffer.getvalue(),
            file_name="carteira_processada.csv",
            mime="text/csv",
        )

        st.subheader("Visualização Gráfica")
        g1, g2 = st.columns(2)
        with g1:
            fig_pizza = px.pie(
                df_c,
                values="Valor Atual",
                names="Tipo",
                title="Distribuição de Patrimônio por Categoria",
                hole=0.45,
                template=PLOTLY_TEMPLATE_ATIVO,
                color_discrete_sequence=[ACCENT, ACCENT_STRONG, "#94A3B8", "#64748B", "#CBD5E1"],
            )
            fig_pizza.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pizza, use_container_width=True, config=PLOTLY_CONFIG)

        with g2:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_c["Ticker"], y=df_c["P. Atual"], name="Preço Atual", marker_color=ACCENT_STRONG))
            fig_bar.add_trace(go.Bar(x=df_c["Ticker"], y=df_c["Teto Bazin"], name="Teto Bazin", marker_color="#4ADE80"))
            fig_bar.update_layout(
                title="Preço Atual vs. Preço Teto Bazin",
                barmode="group",
                template=PLOTLY_TEMPLATE_ATIVO,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)

        st.subheader("Composição do Patrimônio por Ativo")
        fig_tree = px.treemap(
            df_c,
            path=["Tipo", "Ticker"],
            values="Valor Atual",
            color="Rentab. (%)",
            color_continuous_scale="RdYlGn",
            template=PLOTLY_TEMPLATE_ATIVO,
        )
        fig_tree.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, l=0, r=0, b=0))
        st.plotly_chart(fig_tree, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("Clique em **Processar Carteira Completa** para visualizar os indicadores.")

# ==========================================
# ABA 2: VALUATION INDIVIDUAL
# ==========================================
elif aba == "Valuation Individual":
    st.title("Valuation Individual de Ativos")
    st.write("Calcule modelos de precificação teto para decisões individuais de compra.")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker_in = st.text_input("Ticker do Ativo (ex: PETR4, MXRF11):", "BBAS3").upper().strip()
    with col2:
        tipo_in = st.selectbox("Categoria do Ativo:", ["Ação", "FII", "BDR", "ETF"])
    with col3:
        dy_alvo = st.number_input("DY Alvo Bazin (%):", min_value=1.0, value=6.0, step=0.5) / 100

    if st.button("Executar Valuation", type="primary"):
        with st.spinner("Buscando dados e aplicando modelos..."):
            d = buscar_dados_ativo(ticker_in, tipo_in)

        if not d["ok"]:
            st.error(f"Não foi possível obter dados para {ticker_in}: {d.get('erro')}")
        else:
            t_bazin = calcular_teto_bazin(d["div_12m"], dy_alvo)
            t_graham = calcular_teto_graham(d["lpa"], d["vpa"]) if tipo_in == "Ação" else 0.0
            t_gordon = calcular_teto_gordon(d["div_12m"])
            t_medio = calcular_teto_medio(t_bazin, t_graham, t_gordon)
            p_atual = d["preco"]
            status, _ = classificar_status(p_atual, t_medio if t_medio > 0 else t_bazin)

            st.markdown(f"### Análise Detalhada: **{d['nome']} ({ticker_in})** &nbsp; `{status}`")
            st.caption(f"Fonte dos dados: {d['fonte']}")

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.markdown(card_html("Preço Atual", f"R$ {p_atual:.2f}"), unsafe_allow_html=True)
            with m2:
                st.markdown(card_html(f"Teto Bazin ({dy_alvo * 100:.1f}%)", f"R$ {t_bazin:.2f}"), unsafe_allow_html=True)
            with m3:
                t_g_str = f"R$ {t_graham:.2f}" if tipo_in == "Ação" and t_graham > 0 else "N/A"
                st.markdown(card_html("Teto Graham", t_g_str), unsafe_allow_html=True)
            with m4:
                t_gd_str = f"R$ {t_gordon:.2f}" if t_gordon > 0 else "N/A"
                st.markdown(card_html("Teto Gordon", t_gd_str), unsafe_allow_html=True)
            with m5:
                st.markdown(card_html("Teto Médio", f"R$ {t_medio:.2f}" if t_medio > 0 else "N/A"), unsafe_allow_html=True)

            st.subheader("Indicadores Fundamentalistas")
            f1, f2, f3, f4, f5 = st.columns(5)
            f1.metric("P/L", f"{d['pl']:.2f}" if d["pl"] else "N/A")
            f2.metric("P/VP", f"{d['pvp']:.2f}" if d["pvp"] else "N/A")
            f3.metric("Dividend Yield", f"{d['dy_pct']:.2f}%")
            f4.metric("LPA", f"R$ {d['lpa']:.2f}")
            f5.metric("ROE", f"{d['roe']:.2f}%")

            st.subheader("Histórico de Preço (12 meses)")
            hist = buscar_historico(ticker_in, tipo_in, "1y")
            if hist is not None and not hist.empty:
                fig_hist = go.Figure()
                fig_hist.add_trace(
                    go.Scatter(x=hist.index, y=hist["Close"], name="Preço de Fechamento", line=dict(color=ACCENT))
                )
                if t_bazin > 0:
                    fig_hist.add_hline(y=t_bazin, line_dash="dash", line_color="#4ADE80", annotation_text="Teto Bazin")
                if t_graham > 0:
                    fig_hist.add_hline(y=t_graham, line_dash="dot", line_color="#FACC15", annotation_text="Teto Graham")
                fig_hist.update_layout(
                    template=PLOTLY_TEMPLATE_ATIVO,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, l=0, r=0, b=0),
                )
                st.plotly_chart(fig_hist, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("Histórico de preços indisponível para este ativo.")

# ==========================================
# ABA 3: COMPARADOR DE ATIVOS
# ==========================================
elif aba == "Comparador de Ativos":
    st.title("Comparador Multi-Ativos")
    st.write("Compare os múltiplos fundamentais e preços teto de múltiplos ativos lado a lado.")

    tickers_list = st.text_input("Lista de Tickers (separados por vírgula):", "BBAS3, ITSA4, SANB11, CXSE3")
    tipo_comp = st.selectbox("Categoria dos ativos informados:", ["Ação", "FII", "BDR", "ETF"], key="tipo_comparador")

    if st.button("Executar Comparação", type="primary"):
        lista = [t.strip().upper() for t in tickers_list.split(",") if t.strip()]
        dados_comparativos = []
        dados_radar = []

        barra = st.progress(0.0, text="Processando ativos...")
        for i, t in enumerate(lista):
            info = buscar_dados_ativo(t, tipo_comp)
            barra.progress((i + 1) / max(len(lista), 1), text=f"Processando {t}...")
            if not info["ok"]:
                continue

            t_bazin = calcular_teto_bazin(info["div_12m"], 0.06)
            t_graham = calcular_teto_graham(info["lpa"], info["vpa"]) if tipo_comp == "Ação" else 0.0
            margem = margem_seguranca(info["preco"], t_bazin)

            dados_comparativos.append(
                {
                    "Ticker": t,
                    "Preço Atual": f"R$ {info['preco']:.2f}",
                    "DY (%)": f"{info['dy_pct']:.2f}%",
                    "P/L": f"{info['pl']:.2f}" if info["pl"] else "N/A",
                    "P/VP": f"{info['pvp']:.2f}" if info["pvp"] else "N/A",
                    "ROE (%)": f"{info['roe']:.2f}%",
                    "Teto Bazin (6%)": f"R$ {t_bazin:.2f}",
                    "Teto Graham": f"R$ {t_graham:.2f}" if t_graham > 0 else "N/A",
                    "Margem Seg. (%)": round(margem, 2),
                }
            )
            dados_radar.append(
                {"Ticker": t, "DY": info["dy_pct"], "ROE": info["roe"], "P/L": info["pl"], "P/VP": info["pvp"]}
            )
        barra.empty()

        if dados_comparativos:
            df_comp = pd.DataFrame(dados_comparativos)
            st.dataframe(
                df_comp,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Margem Seg. (%)": st.column_config.ProgressColumn(min_value=-30, max_value=30, format="%.1f%%")
                },
            )

            st.subheader("Comparação de Dividend Yield")
            fig_dy = px.bar(
                pd.DataFrame(dados_radar),
                x="Ticker",
                y="DY",
                template=PLOTLY_TEMPLATE_ATIVO,
                color="DY",
                color_continuous_scale=[ACCENT_STRONG, ACCENT],
                labels={"DY": "Dividend Yield (%)"},
            )
            fig_dy.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_dy, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.error("Nenhum ativo pôde ser processado. Verifique os tickers informados.")

# ==========================================
# ABA 4: SIMULADOR DE APORTES
# ==========================================
elif aba == "Simulador de Aportes":
    st.title("Simulador de Aportes")
    st.write(
        "Distribui um novo aporte priorizando os ativos com maior margem de segurança "
        "(mais descontados em relação ao preço teto) já processados no Dashboard."
    )

    if "df_carteira" not in st.session_state:
        st.info("Processe sua carteira na aba **Dashboard da Carteira** primeiro.")
    else:
        df_c = st.session_state["df_carteira"].copy()
        valor_aporte = st.number_input("Valor do novo aporte (R$):", min_value=0.0, value=1000.0, step=100.0)

        elegiveis = df_c[df_c["Margem Seg. (%)"] > 0].sort_values("Margem Seg. (%)", ascending=False)

        if elegiveis.empty:
            st.warning("Nenhum ativo da carteira está abaixo do preço teto no momento. Considere aguardar.")
        else:
            peso_total = elegiveis["Margem Seg. (%)"].sum()
            elegiveis["Peso (%)"] = elegiveis["Margem Seg. (%)"] / peso_total * 100
            elegiveis["Valor Sugerido (R$)"] = (elegiveis["Peso (%)"] / 100 * valor_aporte).round(2)
            elegiveis["Qtd. Sugerida (aprox.)"] = (
                elegiveis["Valor Sugerido (R$)"] / elegiveis["P. Atual"]
            ).apply(lambda x: int(x) if x >= 1 else 0)

            st.subheader("Sugestão de Alocação")
            st.dataframe(
                elegiveis[
                    [
                        "Ticker",
                        "Tipo",
                        "P. Atual",
                        "Margem Seg. (%)",
                        "Peso (%)",
                        "Valor Sugerido (R$)",
                        "Qtd. Sugerida (aprox.)",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Peso (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                },
            )
            st.caption(
                "⚠️ Simulação simplificada baseada apenas na margem de segurança atual. "
                "Não considera diversificação-alvo, correlação entre ativos ou perfil de risco."
            )

            fig_aporte = px.pie(
                elegiveis,
                values="Valor Sugerido (R$)",
                names="Ticker",
                template=PLOTLY_TEMPLATE_ATIVO,
                hole=0.45,
                title="Distribuição Sugerida do Aporte",
            )
            fig_aporte.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_aporte, use_container_width=True, config=PLOTLY_CONFIG)

# ==========================================
# ABA 5: CONSULTORIA COM IA
# ==========================================
elif aba == "Análise via IA Gemini":
    st.title("Consultoria Financeira Automatizada via IA")

    if genai is None:
        st.error("A biblioteca `google-generativeai` não está instalada. Rode: pip install google-generativeai")
    elif "df_carteira" not in st.session_state:
        st.info("Processe sua carteira na aba **Dashboard da Carteira** para habilitar este módulo.")
    else:
        df_c = st.session_state["df_carteira"]
        st.write("Carteira selecionada para avaliação:")
        st.dataframe(
            df_c[["Ticker", "Tipo", "Valor Atual", "Rentab. (%)", "DY (%)", "Status"]],
            use_container_width=True,
            hide_index=True,
        )

        if st.button("Gerar Relatório Estratégico", type="primary"):
            if not gemini_api_key:
                st.error("Informe sua chave API do Google Gemini no painel lateral.")
            else:
                try:
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")

                    contexto = df_c.to_string(index=False)
                    prompt = f"""
                    Você é um analista financeiro sênior especializado no mercado brasileiro.
                    Avalie a seguinte carteira de investimentos:

                    {contexto}

                    Forneça um relatório estruturado em Markdown com:
                    1. Avaliação de Risco e Diversificação.
                    2. Melhores Oportunidades de Alocação (com base no Preço Teto).
                    3. Ativos que exigem Atenção/Acompanhamento.
                    4. Recomendações Práticas para os Próximos Aportes.

                    Deixe explícito ao final que esta análise é gerada por IA, tem caráter
                    exclusivamente educacional e NÃO constitui recomendação de investimento.
                    """

                    with st.spinner("Gerando diagnóstico analítico..."):
                        res = model.generate_content(prompt)
                        st.markdown(res.text)
                        st.session_state["ultima_analise_ia"] = res.text

                except Exception as e:
                    st.error(f"Erro na comunicação com a API Gemini: {e}")

        if "ultima_analise_ia" in st.session_state:
            st.download_button(
                "⬇️ Baixar relatório (Markdown)",
                data=st.session_state["ultima_analise_ia"],
                file_name="relatorio_ia.md",
                mime="text/markdown",
            )

# ==========================================
# ABA 6: GUIA DO USUÁRIO / TUTORIAL
# ==========================================
elif aba == "Guia do Usuário / Tutorial":
    st.title("Guia de Utilização da Plataforma")
    st.write("Aprenda a utilizar os recursos de valuation, gestão de carteira e análise inteligente.")

    st.markdown("---")

    st.markdown(
        """
        <div class="tutorial-box">
            <div class="tutorial-step">Passo 1 · Gestão e Consolidação de Carteira</div>
            Acesse o módulo <b>Dashboard da Carteira</b> para inserir e editar seus ativos na tabela interativa.
            Informe o Ticker (ex: BBAS3, MXRF11), Categoria, Quantidade e Preço Médio. Ao clicar em
            <b>Processar Carteira Completa</b>, o sistema busca automaticamente as cotações em tempo real e
            calcula o patrimônio consolidado, o ganho de capital e a projeção de renda passiva anual.
        </div>

        <div class="tutorial-box">
            <div class="tutorial-step">Passo 2 · Entendendo os Modelos de Valuation (Preço Teto)</div>
            A aplicação utiliza três metodologias reconhecidas no mercado financeiro:
            <ul>
                <li><b>Método Décio Bazin:</b> Preço Teto = Dividendo Anual ÷ DY desejado. Se o preço atual
                estiver abaixo do teto, o ativo é sinalizado como oportunidade de compra.</li>
                <li><b>Método Benjamin Graham:</b> Indicado para Ações — Preço Justo = √(22,5 × LPA × VPA).</li>
                <li><b>Modelo de Gordon:</b> Considera o crescimento constante dos dividendos no longo prazo.</li>
            </ul>
            O <b>Teto Médio</b> combina os modelos aplicáveis para uma referência mais robusta.
        </div>

        <div class="tutorial-box">
            <div class="tutorial-step">Passo 3 · Comparação Multi-Ativos</div>
            No módulo <b>Comparador de Ativos</b>, insira múltiplos tickers separados por vírgula para
            visualizar lado a lado P/L, P/VP, ROE, Dividend Yield e Preços Teto — útil para escolher o
            melhor ativo do mesmo setor para o próximo aporte.
        </div>

        <div class="tutorial-box">
            <div class="tutorial-step">Passo 4 · Simulador de Aportes</div>
            Informe o valor de um novo aporte e a plataforma sugere uma distribuição proporcional à
            margem de segurança de cada ativo já processado — priorizando os mais descontados.
        </div>

        <div class="tutorial-box">
            <div class="tutorial-step">Passo 5 · Consultoria de Investimentos com IA</div>
            Insira sua chave API do Google Gemini na barra lateral. Após processar sua carteira, use a
            aba <b>Análise via IA Gemini</b> para solicitar um relatório diagnóstico sobre diversificação,
            oportunidades e pontos de atenção.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption(
        "⚠️ Esta plataforma tem fins exclusivamente educacionais. As informações e cálculos apresentados "
        "não constituem recomendação de investimento. Consulte um profissional certificado antes de tomar "
        "decisões financeiras."
    )