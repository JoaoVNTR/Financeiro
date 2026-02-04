import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Painel Executivo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Painel Executivo")
st.markdown("### Análise Consolidada de Performance")
st.markdown("---")

# ===============================
# 1️⃣ Base de dados
# ===============================
if 'df_original' not in st.session_state:
    st.error("❌ Dados não carregados. Retorne à página principal.")
    st.stop()

df = st.session_state['df_original'].copy()

# ===============================
# 2️⃣ Filtros da página (INDEPENDENTES)
# ===============================
with st.sidebar:
    st.markdown("## 🎛️ Filtros – Painel Executivo")
    st.markdown("---")

    meses = sorted(df['Mês de Competência'].unique())
    meses_sel = st.multiselect(
        "📅 Mês de Competência",
        meses,
        default=meses,
        key="executivo_mes"
    )

    geradores = sorted(df['Gerador'].unique())
    geradores_sel = st.multiselect(
        "🏭 Gerador",
        geradores,
        default=geradores,
        key="executivo_gerador"
    )

    usinas = sorted(df['Usina'].unique())
    usinas_sel = st.multiselect(
        "⚡ Usina",
        usinas,
        default=usinas,
        key="executivo_usina"
    )

    st.markdown("---")
    if st.button("🔄 Resetar filtros", key="executivo_reset"):
        st.rerun()

# ===============================
# 3️⃣ Aplicação dos filtros
# ===============================
if meses_sel:
    df = df[df['Mês de Competência'].isin(meses_sel)]

if geradores_sel:
    df = df[df['Gerador'].isin(geradores_sel)]

if usinas_sel:
    df = df[df['Usina'].isin(usinas_sel)]

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ===============================
# 4️⃣ KPIs
# ===============================
col1, col2, col3, col4 = st.columns(4)

faturamento_total = df['Valor a Pagar para Gerador (R$)'].sum()
receita_gestao = df['Valor da Gestão (R$)'].sum()
total_clientes = df['Cliente Final'].nunique()
total_usinas = df['Usina'].nunique()

with col1:
    st.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")

with col2:
    margem = (receita_gestao / faturamento_total * 100) if faturamento_total else 0
    st.metric("💵 Receita Gestão", f"R$ {receita_gestao:,.2f}", f"{margem:.1f}%")

with col3:
    st.metric("👥 Clientes", total_clientes, f"{total_usinas} usinas")

with col4:
    ticket = faturamento_total / total_clientes if total_clientes else 0
    st.metric("🎯 Ticket Médio", f"R$ {ticket:,.2f}")

st.markdown("---")

# ===============================
# 5️⃣ Gráficos
# ===============================
col_l, col_r = st.columns(2)

with col_l:
    st.markdown("#### 📈 Evolução Mensal")

    evolucao = df.groupby('Mês de Competência').agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum'
    }).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=evolucao['Mês de Competência'],
        y=evolucao['Valor a Pagar para Gerador (R$)'],
        name="Faturamento",
        marker_color="#071D49"
    )
    fig.add_scatter(
        x=evolucao['Mês de Competência'],
        y=evolucao['Valor da Gestão (R$)'],
        name="Receita Gestão",
        secondary_y=True,
        line=dict(color="green")
    )

    fig.update_layout(height=400, template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("#### 🏭 Top 5 Geradores por Faturamento")

    top = (
        df.groupby('Gerador')['Valor a Pagar para Gerador (R$)']
        .sum()
        .sort_values(ascending=True)
        .tail(5)
    )

    max_valor = top.max() * 1.15  # folga no eixo X

    fig_top = go.Figure()

    fig_top.add_bar(
    x=top.values,
    y=top.index,
    orientation='h',
    text=[f"R$ {v:,.2f}" for v in top.values],
    textposition='outside',
    cliponaxis=False,
    marker=dict(color="#1f77b4"),
    hovertemplate="<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>"
)


    fig_top.update_layout(
        height=400,
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title="Faturamento (R$)",
            range=[0, max_valor],
            showgrid=False,
            tickprefix="R$ ",
            tickformat=",.0f"
        ),
        yaxis=dict(
            title="",
            showgrid=False
        )
    )

    st.plotly_chart(fig_top, use_container_width=True)



st.markdown("---")

# ===============================
# 6️⃣ Tabela resumo
# ===============================
st.markdown("#### 📋 Resumo por Gerador")

resumo = df.groupby('Gerador').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    'Usina': 'nunique',
    'Cliente Final': 'nunique',
    '% Gestão': 'mean'
}).reset_index()

resumo['Margem %'] = (
    resumo['Valor da Gestão (R$)'] /
    resumo['Valor a Pagar para Gerador (R$)'] * 100
).round(2)

# Formatação em R$ (padrão brasileiro)
resumo['Valor a Pagar para Gerador (R$)'] = resumo['Valor a Pagar para Gerador (R$)'] \
    .map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

resumo['Valor da Gestão (R$)'] = resumo['Valor da Gestão (R$)'] \
    .map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.dataframe(resumo, use_container_width=True, height=320)
