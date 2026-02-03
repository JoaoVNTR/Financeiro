import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================================================
# Configuração
# ======================================================
st.set_page_config(
    page_title="Painel Financeiro",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Painel Financeiro")
st.markdown("### Análise Detalhada de Receitas e Margens")
st.markdown("---")

# ======================================================
# 1️⃣ Base de dados
# ======================================================
if "df_original" not in st.session_state:
    st.error("❌ Dados não carregados. Retorne à página principal.")
    st.stop()

df = st.session_state["df_original"].copy()

# ======================================================
# 2️⃣ Filtros independentes
# ======================================================
with st.sidebar:
    st.markdown("## 🎛️ Filtros – Financeiro")
    st.markdown("---")

    meses = sorted(df["Mês de Competência"].unique())
    meses_sel = st.multiselect(
        "📅 Mês de Competência",
        meses,
        default=meses,
        key="financeiro_mes"
    )

    geradores = sorted(df["Gerador"].unique())
    geradores_sel = st.multiselect(
        "🏭 Gerador",
        geradores,
        default=geradores,
        key="financeiro_gerador"
    )

    clientes = sorted(df["Cliente Final"].unique())
    clientes_sel = st.multiselect(
        "👥 Cliente Final",
        clientes,
        key="financeiro_cliente"
    )

    st.markdown("---")
    if st.button("🔄 Resetar filtros", key="financeiro_reset"):
        st.rerun()

# ======================================================
# 3️⃣ Aplicação dos filtros
# ======================================================
if meses_sel:
    df = df[df["Mês de Competência"].isin(meses_sel)]

if geradores_sel:
    df = df[df["Gerador"].isin(geradores_sel)]

if clientes_sel:
    df = df[df["Cliente Final"].isin(clientes_sel)]

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ======================================================
# 4️⃣ KPIs Financeiros
# ======================================================
faturamento_total = df["Valor a Pagar para Gerador (R$)"].sum()
receita_gestao = df["Valor da Gestão (R$)"].sum()
margem_media = (receita_gestao / faturamento_total * 100) if faturamento_total else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Faturamento Bruto", f"R$ {faturamento_total:,.2f}")

with col2:
    st.metric("💵 Receita Gestão", f"R$ {receita_gestao:,.2f}")

with col3:
    st.metric("📊 Margem Média", f"{margem_media:.2f}%")

st.markdown("---")

# ======================================================
# 5️⃣ Margem por Gerador
# ======================================================
st.markdown("### 📈 Margem por Gerador")

margem_gerador = df.groupby("Gerador").agg({
    "Valor a Pagar para Gerador (R$)": "sum",
    "Valor da Gestão (R$)": "sum",
    "% Gestão": "mean"
}).reset_index()

margem_gerador["Margem Realizada %"] = (
    margem_gerador["Valor da Gestão (R$)"] /
    margem_gerador["Valor a Pagar para Gerador (R$)"] * 100
).fillna(0)

col_l, col_r = st.columns(2)

with col_l:
    fig_receita = px.bar(
        margem_gerador.sort_values("Valor da Gestão (R$)", ascending=False),
        y="Gerador",
        x="Valor da Gestão (R$)",
        orientation="h",
        labels={"Valor da Gestão (R$)": "Receita (R$)"}
    )
    st.plotly_chart(fig_receita, use_container_width=True)

with col_r:
    fig_margem = px.scatter(
        margem_gerador,
        x="% Gestão",
        y="Margem Realizada %",
        size="Valor da Gestão (R$)",
        color="Margem Realizada %",
        hover_name="Gerador",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_margem, use_container_width=True)

st.markdown("---")

# ======================================================
# 6️⃣ Receita por Cliente
# ======================================================
st.markdown("### 👥 Top Clientes por Receita")

top_clientes = (
    df.groupby("Cliente Final")
    .agg({
        "Valor a Pagar para Gerador (R$)": "sum",
        "Valor da Gestão (R$)": "sum"
    })
    .sort_values("Valor da Gestão (R$)", ascending=False)
    .head(15)
)

fig_clientes = go.Figure()
fig_clientes.add_bar(
    x=top_clientes.index,
    y=top_clientes["Valor a Pagar para Gerador (R$)"],
    name="Faturamento"
)
fig_clientes.add_bar(
    x=top_clientes.index,
    y=top_clientes["Valor da Gestão (R$)"],
    name="Receita Gestão"
)

fig_clientes.update_layout(
    barmode="group",
    height=500,
    template="plotly_white",
    xaxis_tickangle=-45
)

st.plotly_chart(fig_clientes, use_container_width=True)

st.markdown("---")

# ======================================================
# 7️⃣ Evolução Financeira
# ======================================================
st.markdown("### 📅 Evolução Financeira Mensal")

evolucao = df.groupby("Mês de Competência").agg({
    "Valor a Pagar para Gerador (R$)": "sum",
    "Valor da Gestão (R$)": "sum"
}).reset_index()

evolucao["Margem %"] = (
    evolucao["Valor da Gestão (R$)"] /
    evolucao["Valor a Pagar para Gerador (R$)"] * 100
)

fig_evo = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Receitas", "Margem %"),
    vertical_spacing=0.12
)

fig_evo.add_bar(
    x=evolucao["Mês de Competência"],
    y=evolucao["Valor a Pagar para Gerador (R$)"],
    row=1, col=1,
    name="Faturamento"
)
fig_evo.add_bar(
    x=evolucao["Mês de Competência"],
    y=evolucao["Valor da Gestão (R$)"],
    row=1, col=1,
    name="Receita Gestão"
)
fig_evo.add_scatter(
    x=evolucao["Mês de Competência"],
    y=evolucao["Margem %"],
    row=2, col=1,
    mode="lines+markers",
    name="Margem %"
)

fig_evo.update_layout(height=700, template="plotly_white")
st.plotly_chart(fig_evo, use_container_width=True)

st.markdown("---")

# ======================================================
# 8️⃣ Tabela Detalhada + Download
# ======================================================
st.markdown("### 📋 Resumo Financeiro Detalhado")

resumo = df.groupby(["Gerador", "Usina"]).agg({
    "Valor a Pagar para Gerador (R$)": "sum",
    "Valor da Gestão (R$)": "sum",
    "Cliente Final": "nunique",
    "% Gestão": "mean"
}).reset_index()

resumo["Margem %"] = (
    resumo["Valor da Gestão (R$)"] /
    resumo["Valor a Pagar para Gerador (R$)"] * 100
).round(2)

st.dataframe(resumo, use_container_width=True, height=400)

st.download_button(
    "📥 Download Resumo Financeiro (CSV)",
    resumo.to_csv(index=False).encode("utf-8"),
    "resumo_financeiro.csv",
    "text/csv"
)
