import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Painel Operacional", page_icon="⚡", layout="wide")

st.title("⚡ Painel Operacional por Usina")
st.markdown("### Performance e Análise Operacional")
st.markdown("---")

# Verificar dados
if 'df_filtrado' not in st.session_state:
    st.error("❌ Dados não encontrados. Por favor, retorne à página inicial.")
    st.stop()

df = st.session_state['df_filtrado']

if df.empty:
    st.warning("⚠️ Nenhum dado disponível com os filtros aplicados.")
    st.stop()

# KPIs Operacionais
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_usinas = df['Usina'].nunique()
    st.metric("⚡ Total de Usinas", f"{total_usinas}")

with col2:
    total_geradores = df['Gerador'].nunique()
    st.metric("🏭 Total de Geradores", f"{total_geradores}")

with col3:
    media_clientes_usina = df.groupby('Usina')['Cliente Final'].nunique().mean()
    st.metric("👥 Média Clientes/Usina", f"{media_clientes_usina:.1f}")

with col4:
    faturamento_medio_usina = df.groupby('Usina')['Valor a Pagar para Gerador (R$)'].sum().mean()
    st.metric("💰 Faturamento Médio/Usina", f"R$ {faturamento_medio_usina:,.2f}")

st.markdown("---")

# Performance por Usina
st.markdown("### 📊 Performance por Usina (Top 20)")

perf_usina = df.groupby('Usina').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    'Cliente Final': 'nunique'
}).sort_values('Valor a Pagar para Gerador (R$)', ascending=False).head(20)

col1, col2 = st.columns(2)

with col1:
    fig_usina_fat = px.bar(
        x=perf_usina['Valor a Pagar para Gerador (R$)'],
        y=perf_usina.index,
        orientation='h',
        title="Faturamento por Usina",
        labels={'x': 'Faturamento (R$)', 'y': 'Usina'},
        color=perf_usina['Valor a Pagar para Gerador (R$)'],
        color_continuous_scale='Blues'
    )
    
    fig_usina_fat.update_traces(
        hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
    )
    
    fig_usina_fat.update_layout(
        height=600,
        template="plotly_white",
        showlegend=False
    )
    
    st.plotly_chart(fig_usina_fat, use_container_width=True)

with col2:
    fig_usina_rec = px.bar(
        x=perf_usina['Valor da Gestão (R$)'],
        y=perf_usina.index,
        orientation='h',
        title="Receita de Gestão por Usina",
        labels={'x': 'Receita Gestão (R$)', 'y': 'Usina'},
        color=perf_usina['Valor da Gestão (R$)'],
        color_continuous_scale='Greens'
    )
    
    fig_usina_rec.update_traces(
        hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>'
    )
    
    fig_usina_rec.update_layout(
        height=600,
        template="plotly_white",
        showlegend=False
    )
    
    st.plotly_chart(fig_usina_rec, use_container_width=True)

st.markdown("---")

# Análise por Gerador e Usina
st.markdown("### 🏭 Distribuição Gerador x Usina")

gerador_usina = df.groupby(['Gerador', 'Usina']).agg({
    'Valor a Pagar para Gerador (R$)': 'sum'
}).reset_index()

fig_treemap = px.treemap(
    gerador_usina,
    path=['Gerador', 'Usina'],
    values='Valor a Pagar para Gerador (R$)',
    title="Mapa Hierárquico: Gerador → Usina"
)

fig_treemap.update_traces(
    hovertemplate='<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<extra></extra>'
)

fig_treemap.update_layout(
    height=500,
    template="plotly_white"
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")

# Comparativo Usinas por Gerador
st.markdown("### 📈 Comparativo de Usinas por Gerador")

gerador_selecionado = st.selectbox(
    "Selecione um Gerador:",
    options=sorted(df['Gerador'].unique())
)

df_gerador = df[df['Gerador'] == gerador_selecionado]

usinas_gerador = df_gerador.groupby('Usina').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    'Cliente Final': 'nunique'
}).reset_index()

usinas_gerador = usinas_gerador.sort_values('Valor a Pagar para Gerador (R$)', ascending=False)

fig_comp = go.Figure()

fig_comp.add_trace(go.Bar(
    x=usinas_gerador['Usina'],
    y=usinas_gerador['Valor a Pagar para Gerador (R$)'],
    name='Faturamento',
    marker_color='#3498db',
    hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
))

fig_comp.add_trace(go.Bar(
    x=usinas_gerador['Usina'],
    y=usinas_gerador['Valor da Gestão (R$)'],
    name='Receita Gestão',
    marker_color='#e74c3c',
    hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>'
))

fig_comp.update_layout(
    title=f"Usinas do Gerador: {gerador_selecionado}",
    barmode='group',
    height=400,
    xaxis_title="Usina",
    yaxis_title="Valor (R$)",
    xaxis_tickangle=-45,
    template="plotly_white"
)

st.plotly_chart(fig_comp, use_container_width=True)

# Tabela de Detalhes
st.markdown(f"#### 📋 Detalhes das Usinas - {gerador_selecionado}")

usinas_gerador_display = usinas_gerador.copy()
usinas_gerador_display.columns = ['Usina', 'Faturamento (R$)', 'Receita Gestão (R$)', 'Nº Clientes']
usinas_gerador_display['Faturamento (R$)'] = usinas_gerador_display['Faturamento (R$)'].apply(lambda x: f"R$ {x:,.2f}")
usinas_gerador_display['Receita Gestão (R$)'] = usinas_gerador_display['Receita Gestão (R$)'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(usinas_gerador_display, use_container_width=True)

st.markdown("---")

# Concentração de Clientes
st.markdown("### 👥 Distribuição de Clientes por Usina")

clientes_usina = df.groupby('Usina')['Cliente Final'].nunique().sort_values(ascending=False).head(15)

fig_clientes = px.bar(
    x=clientes_usina.index,
    y=clientes_usina.values,
    title="Top 15 Usinas por Número de Clientes",
    labels={'x': 'Usina', 'y': 'Número de Clientes'},
    color=clientes_usina.values,
    color_continuous_scale='Oranges'
)

fig_clientes.update_traces(
    hovertemplate='<b>%{x}</b><br>Clientes: %{y}<extra></extra>'
)

fig_clientes.update_layout(
    height=400,
    xaxis_tickangle=-45,
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(fig_clientes, use_container_width=True)
