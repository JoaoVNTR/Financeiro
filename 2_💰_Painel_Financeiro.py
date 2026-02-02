import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Painel Financeiro", page_icon="💰", layout="wide")

st.title("💰 Painel Financeiro")
st.markdown("### Análise Detalhada de Receitas e Margens")
st.markdown("---")

# Verificar dados
if 'df_filtrado' not in st.session_state:
    st.error("❌ Dados não encontrados. Por favor, retorne à página inicial.")
    st.stop()

df = st.session_state['df_filtrado']

if df.empty:
    st.warning("⚠️ Nenhum dado disponível com os filtros aplicados.")
    st.stop()

# KPIs Financeiros
col1, col2, col3, col4 = st.columns(4)

with col1:
    faturamento_total = df['Valor a Pagar para Gerador (R$)'].sum()
    st.metric("💰 Faturamento Bruto", f"R$ {faturamento_total:,.2f}")

with col2:
    receita_gestao = df['Valor da Gestão (R$)'].sum()
    st.metric("💵 Receita Líquida (Gestão)", f"R$ {receita_gestao:,.2f}")

with col3:
    margem_media = (receita_gestao / faturamento_total * 100) if faturamento_total > 0 else 0
    st.metric("📊 Margem Média", f"{margem_media:.2f}%")

with col4:
    valor_medio_transacao = df['Valor a Pagar para Gerador (R$)'].mean()
    st.metric("💳 Valor Médio/Transação", f"R$ {valor_medio_transacao:,.2f}")

st.markdown("---")

# Análise de Margem por Gerador
st.markdown("### 📈 Análise de Margens por Gerador")

margem_gerador = df.groupby('Gerador').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    '% Gestão': 'mean'
}).reset_index()

margem_gerador['Margem Realizada %'] = (
    margem_gerador['Valor da Gestão (R$)'] / 
    margem_gerador['Valor a Pagar para Gerador (R$)'] * 100
).fillna(0)

margem_gerador = margem_gerador.sort_values('Valor da Gestão (R$)', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_receita = go.Figure(go.Bar(
        y=margem_gerador['Gerador'],
        x=margem_gerador['Valor da Gestão (R$)'],
        orientation='h',
        marker_color='#27ae60',
        hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig_receita.update_layout(
        title="Receita de Gestão por Gerador",
        height=400,
        xaxis_title="Receita (R$)",
        yaxis_title="Gerador",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_receita, use_container_width=True)

with col2:
    fig_margem = go.Figure(go.Scatter(
        x=margem_gerador['% Gestão'],
        y=margem_gerador['Margem Realizada %'],
        mode='markers+text',
        marker=dict(
            size=margem_gerador['Valor da Gestão (R$)'] / 100,
            color=margem_gerador['Margem Realizada %'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Margem %")
        ),
        text=margem_gerador['Gerador'],
        textposition="top center",
        hovertemplate='<b>%{text}</b><br>% Gestão: %{x:.2f}%<br>Margem: %{y:.2f}%<extra></extra>'
    ))
    
    fig_margem.update_layout(
        title="Margem Realizada vs % Gestão",
        height=400,
        xaxis_title="% Gestão",
        yaxis_title="Margem Realizada %",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_margem, use_container_width=True)

st.markdown("---")

# Análise por Cliente
st.markdown("### 👥 Análise de Receita por Cliente Final")

receita_cliente = df.groupby('Cliente Final').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum'
}).sort_values('Valor da Gestão (R$)', ascending=False).head(15)

fig_clientes = go.Figure()

fig_clientes.add_trace(go.Bar(
    x=receita_cliente.index,
    y=receita_cliente['Valor a Pagar para Gerador (R$)'],
    name='Faturamento',
    marker_color='#3498db',
    hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
))

fig_clientes.add_trace(go.Bar(
    x=receita_cliente.index,
    y=receita_cliente['Valor da Gestão (R$)'],
    name='Receita Gestão',
    marker_color='#e74c3c',
    hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>'
))

fig_clientes.update_layout(
    title="Top 15 Clientes por Receita",
    barmode='group',
    height=500,
    xaxis_title="Cliente Final",
    yaxis_title="Valor (R$)",
    xaxis_tickangle=-45,
    template="plotly_white"
)

st.plotly_chart(fig_clientes, use_container_width=True)

st.markdown("---")

# Evolução Financeira Mensal
st.markdown("### 📅 Evolução Financeira Mensal")

evolucao_mensal = df.groupby('Mês de Competência').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum'
}).reset_index()

evolucao_mensal['Margem %'] = (
    evolucao_mensal['Valor da Gestão (R$)'] / 
    evolucao_mensal['Valor a Pagar para Gerador (R$)'] * 100
)

fig_evolucao = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Receitas Mensais', 'Margem Mensal %'),
    vertical_spacing=0.15
)

# Gráfico 1: Receitas
fig_evolucao.add_trace(
    go.Bar(
        x=evolucao_mensal['Mês de Competência'],
        y=evolucao_mensal['Valor a Pagar para Gerador (R$)'],
        name='Faturamento',
        marker_color='#1f77b4',
        hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
    ),
    row=1, col=1
)

fig_evolucao.add_trace(
    go.Bar(
        x=evolucao_mensal['Mês de Competência'],
        y=evolucao_mensal['Valor da Gestão (R$)'],
        name='Receita Gestão',
        marker_color='#ff7f0e',
        hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>'
    ),
    row=1, col=1
)

# Gráfico 2: Margem
fig_evolucao.add_trace(
    go.Scatter(
        x=evolucao_mensal['Mês de Competência'],
        y=evolucao_mensal['Margem %'],
        mode='lines+markers',
        name='Margem %',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Margem: %{y:.2f}%<extra></extra>'
    ),
    row=2, col=1
)

fig_evolucao.update_layout(
    height=700,
    template="plotly_white",
    showlegend=True
)

fig_evolucao.update_xaxes(title_text="Mês", row=2, col=1)
fig_evolucao.update_yaxes(title_text="Valor (R$)", row=1, col=1)
fig_evolucao.update_yaxes(title_text="Margem (%)", row=2, col=1)

st.plotly_chart(fig_evolucao, use_container_width=True)

st.markdown("---")

# Tabela Financeira Detalhada
st.markdown("### 📋 Resumo Financeiro Detalhado")

resumo_financeiro = df.groupby(['Gerador', 'Usina']).agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    'Cliente Final': 'nunique',
    '% Gestão': 'mean'
}).reset_index()

resumo_financeiro.columns = ['Gerador', 'Usina', 'Faturamento (R$)', 
                             'Receita Gestão (R$)', 'Nº Clientes', '% Gestão Médio']

resumo_financeiro['Margem %'] = (
    resumo_financeiro['Receita Gestão (R$)'] / 
    resumo_financeiro['Faturamento (R$)'] * 100
).round(2)

resumo_financeiro = resumo_financeiro.sort_values('Receita Gestão (R$)', ascending=False)

# Formatar
resumo_financeiro['Faturamento (R$)'] = resumo_financeiro['Faturamento (R$)'].apply(lambda x: f"R$ {x:,.2f}")
resumo_financeiro['Receita Gestão (R$)'] = resumo_financeiro['Receita Gestão (R$)'].apply(lambda x: f"R$ {x:,.2f}")
resumo_financeiro['% Gestão Médio'] = resumo_financeiro['% Gestão Médio'].apply(lambda x: f"{x:.2f}%")
resumo_financeiro['Margem %'] = resumo_financeiro['Margem %'].apply(lambda x: f"{x:.2f}%")

st.dataframe(resumo_financeiro, use_container_width=True, height=400)

# Download
csv = resumo_financeiro.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Resumo Financeiro (CSV)",
    data=csv,
    file_name="resumo_financeiro.csv",
    mime="text/csv"
)
