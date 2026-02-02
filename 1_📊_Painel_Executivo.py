import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Painel Executivo", page_icon="📊", layout="wide")

st.title("📊 Painel Executivo")
st.markdown("### Análise Consolidada de Performance")
st.markdown("---")

# Verificar dados no session_state
if 'df_filtrado' not in st.session_state:
    st.error("❌ Dados não encontrados. Por favor, retorne à página inicial.")
    st.stop()

df = st.session_state['df_filtrado']

if df.empty:
    st.warning("⚠️ Nenhum dado disponível com os filtros aplicados.")
    st.stop()

# KPIs Resumidos
col1, col2, col3, col4 = st.columns(4)

with col1:
    faturamento_total = df['Valor a Pagar para Gerador (R$)'].sum()
    st.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")

with col2:
    receita_gestao = df['Valor da Gestão (R$)'].sum()
    margem = (receita_gestao / faturamento_total * 100) if faturamento_total > 0 else 0
    st.metric("💵 Receita Gestão", f"R$ {receita_gestao:,.2f}", f"{margem:.1f}%")

with col3:
    total_clientes = df['Cliente Final'].nunique()
    total_usinas = df['Usina'].nunique()
    st.metric("👥 Clientes", f"{total_clientes}", f"{total_usinas} usinas")

with col4:
    ticket_medio = faturamento_total / total_clientes if total_clientes > 0 else 0
    st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:,.2f}")

st.markdown("---")

# Dashboard em 2 colunas
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 📈 Evolução Mensal Comparativa")
    
    evolucao = df.groupby('Mês de Competência').agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum'
    }).reset_index()
    
    fig_evolucao = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_evolucao.add_trace(
        go.Bar(
            x=evolucao['Mês de Competência'],
            y=evolucao['Valor a Pagar para Gerador (R$)'],
            name='Faturamento',
            marker_color='#1f77b4',
            hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig_evolucao.add_trace(
        go.Scatter(
            x=evolucao['Mês de Competência'],
            y=evolucao['Valor da Gestão (R$)'],
            name='Receita Gestão',
            line=dict(color='#ff7f0e', width=3),
            mode='lines+markers',
            hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig_evolucao.update_xaxes(title_text="Mês")
    fig_evolucao.update_yaxes(title_text="Faturamento (R$)", secondary_y=False)
    fig_evolucao.update_yaxes(title_text="Receita Gestão (R$)", secondary_y=True)
    fig_evolucao.update_layout(height=400, template="plotly_white", hovermode='x unified')
    
    st.plotly_chart(fig_evolucao, use_container_width=True)

with col_right:
    st.markdown("#### 🏭 Top 5 Geradores por Receita")
    
    top_geradores = df.groupby('Gerador').agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum'
    }).sort_values('Valor a Pagar para Gerador (R$)', ascending=False).head(5)
    
    fig_top_ger = go.Figure()
    
    fig_top_ger.add_trace(go.Bar(
        y=top_geradores.index,
        x=top_geradores['Valor a Pagar para Gerador (R$)'],
        name='Faturamento',
        orientation='h',
        marker_color='#2ecc71',
        hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig_top_ger.add_trace(go.Bar(
        y=top_geradores.index,
        x=top_geradores['Valor da Gestão (R$)'],
        name='Receita Gestão',
        orientation='h',
        marker_color='#e74c3c',
        hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig_top_ger.update_layout(
        barmode='group',
        height=400,
        template="plotly_white",
        xaxis_title="Valor (R$)",
        yaxis_title="Gerador"
    )
    
    st.plotly_chart(fig_top_ger, use_container_width=True)

st.markdown("---")

# Segunda linha de gráficos
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.markdown("#### ⚡ Distribuição por Usinas (Top 10)")
    
    top_usinas = df.groupby('Usina')['Valor a Pagar para Gerador (R$)'].sum().sort_values(ascending=False).head(10)
    
    fig_usinas = px.bar(
        x=top_usinas.values,
        y=top_usinas.index,
        orientation='h',
        labels={'x': 'Faturamento (R$)', 'y': 'Usina'},
        color=top_usinas.values,
        color_continuous_scale='Blues'
    )
    
    fig_usinas.update_traces(
        hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
    )
    
    fig_usinas.update_layout(
        height=400,
        template="plotly_white",
        showlegend=False
    )
    
    st.plotly_chart(fig_usinas, use_container_width=True)

with col_right2:
    st.markdown("#### 📊 Percentual de Gestão Aplicado")
    
    # Calcular percentual médio por gerador
    perc_gestao = df.groupby('Gerador').agg({
        '% Gestão': 'mean',
        'Valor a Pagar para Gerador (R$)': 'sum'
    }).reset_index()
    
    perc_gestao = perc_gestao[perc_gestao['% Gestão'] > 0].sort_values('% Gestão', ascending=False)
    
    fig_perc = go.Figure()
    
    fig_perc.add_trace(go.Bar(
        x=perc_gestao['Gerador'],
        y=perc_gestao['% Gestão'],
        marker=dict(
            color=perc_gestao['% Gestão'],
            colorscale='Reds',
            showscale=True
        ),
        hovertemplate='<b>%{x}</b><br>% Gestão: %{y:.2f}%<extra></extra>'
    ))
    
    fig_perc.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Gerador",
        yaxis_title="% Gestão Médio",
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_perc, use_container_width=True)

st.markdown("---")

# Tabela Resumo por Gerador
st.markdown("#### 📋 Resumo Consolidado por Gerador")

resumo_gerador = df.groupby('Gerador').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum',
    'Usina': 'nunique',
    'Cliente Final': 'nunique',
    '% Gestão': 'mean'
}).reset_index()

resumo_gerador.columns = ['Gerador', 'Faturamento Total (R$)', 'Receita Gestão (R$)', 
                           'Nº Usinas', 'Nº Clientes', '% Gestão Médio']

resumo_gerador['Margem %'] = (resumo_gerador['Receita Gestão (R$)'] / 
                               resumo_gerador['Faturamento Total (R$)'] * 100).round(2)

# Formatar valores
resumo_gerador['Faturamento Total (R$)'] = resumo_gerador['Faturamento Total (R$)'].apply(lambda x: f"R$ {x:,.2f}")
resumo_gerador['Receita Gestão (R$)'] = resumo_gerador['Receita Gestão (R$)'].apply(lambda x: f"R$ {x:,.2f}")
resumo_gerador['% Gestão Médio'] = resumo_gerador['% Gestão Médio'].apply(lambda x: f"{x:.2f}%")
resumo_gerador['Margem %'] = resumo_gerador['Margem %'].apply(lambda x: f"{x:.2f}%")

st.dataframe(resumo_gerador, use_container_width=True, height=300)

# Download
csv = resumo_gerador.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Resumo (CSV)",
    data=csv,
    file_name="resumo_executivo_geradores.csv",
    mime="text/csv"
)
