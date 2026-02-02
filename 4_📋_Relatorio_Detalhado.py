import streamlit as st
import pandas as pd

st.set_page_config(page_title="Relatório Detalhado", page_icon="📋", layout="wide")

st.title("📋 Relatório Detalhado")
st.markdown("### Tabela Completa com Drill-Down")
st.markdown("---")

# Verificar dados
if 'df_filtrado' not in st.session_state:
    st.error("❌ Dados não encontrados. Por favor, retorne à página inicial.")
    st.stop()

df = st.session_state['df_filtrado'].copy()

if df.empty:
    st.warning("⚠️ Nenhum dado disponível com os filtros aplicados.")
    st.stop()

# Informações do Relatório
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total de Registros", f"{len(df):,}")

with col2:
    total_fat = df['Valor a Pagar para Gerador (R$)'].sum()
    st.metric("💰 Faturamento Total", f"R$ {total_fat:,.2f}")

with col3:
    total_rec = df['Valor da Gestão (R$)'].sum()
    st.metric("💵 Receita Total", f"R$ {total_rec:,.2f}")

with col4:
    st.metric("🏭 Geradores", f"{df['Gerador'].nunique()}")

st.markdown("---")

# Opções de Visualização
st.markdown("### ⚙️ Opções de Visualização")

col1, col2 = st.columns(2)

with col1:
    nivel_agregacao = st.selectbox(
        "Nível de Agregação:",
        ["Detalhado (Todos os Registros)", "Por Gerador", "Por Usina", "Por Cliente", "Por Mês"]
    )

with col2:
    ordenar_por = st.selectbox(
        "Ordenar por:",
        ["Valor a Pagar para Gerador (R$)", "Valor da Gestão (R$)", "% Gestão", "Gerador", "Usina", "Cliente Final"]
    )

ordem_crescente = st.checkbox("Ordem Crescente", value=False)

st.markdown("---")

# Processar agregação
if nivel_agregacao == "Detalhado (Todos os Registros)":
    df_display = df[[
        'Gerador', 'Usina', 'Cliente Final', 'Mês de Competência',
        'Valor a Pagar para Gerador (R$)', '% Gestão', 'Valor da Gestão (R$)'
    ]].copy()
    
elif nivel_agregacao == "Por Gerador":
    df_display = df.groupby('Gerador').agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum',
        '% Gestão': 'mean',
        'Usina': 'nunique',
        'Cliente Final': 'nunique'
    }).reset_index()
    df_display.columns = ['Gerador', 'Faturamento Total (R$)', 'Receita Gestão (R$)', 
                          '% Gestão Médio', 'Nº Usinas', 'Nº Clientes']
    
elif nivel_agregacao == "Por Usina":
    df_display = df.groupby(['Gerador', 'Usina']).agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum',
        '% Gestão': 'mean',
        'Cliente Final': 'nunique'
    }).reset_index()
    df_display.columns = ['Gerador', 'Usina', 'Faturamento Total (R$)', 
                          'Receita Gestão (R$)', '% Gestão Médio', 'Nº Clientes']
    
elif nivel_agregacao == "Por Cliente":
    df_display = df.groupby(['Gerador', 'Usina', 'Cliente Final']).agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum',
        '% Gestão': 'mean'
    }).reset_index()
    df_display.columns = ['Gerador', 'Usina', 'Cliente Final', 
                          'Faturamento Total (R$)', 'Receita Gestão (R$)', '% Gestão Médio']
    
else:  # Por Mês
    df_display = df.groupby(['Mês de Competência', 'Gerador']).agg({
        'Valor a Pagar para Gerador (R$)': 'sum',
        'Valor da Gestão (R$)': 'sum',
        '% Gestão': 'mean',
        'Usina': 'nunique',
        'Cliente Final': 'nunique'
    }).reset_index()
    df_display.columns = ['Mês', 'Gerador', 'Faturamento Total (R$)', 
                          'Receita Gestão (R$)', '% Gestão Médio', 'Nº Usinas', 'Nº Clientes']

# Ordenar
if ordenar_por in df_display.columns:
    df_display = df_display.sort_values(ordenar_por, ascending=ordem_crescente)

# Exibir tabela
st.markdown(f"### 📊 Visualização: {nivel_agregacao}")
st.dataframe(df_display, use_container_width=True, height=500)

st.markdown("---")

# Estatísticas
st.markdown("### 📈 Estatísticas do Relatório Atual")

col1, col2, col3 = st.columns(3)

with col1:
    if 'Faturamento Total (R$)' in df_display.columns:
        total = df_display['Faturamento Total (R$)'].sum()
    else:
        total = df_display['Valor a Pagar para Gerador (R$)'].sum()
    st.metric("💰 Total Faturamento", f"R$ {total:,.2f}")

with col2:
    if 'Receita Gestão (R$)' in df_display.columns:
        total_rec = df_display['Receita Gestão (R$)'].sum()
    else:
        total_rec = df_display['Valor da Gestão (R$)'].sum()
    st.metric("💵 Total Receita Gestão", f"R$ {total_rec:,.2f}")

with col3:
    margem = (total_rec / total * 100) if total > 0 else 0
    st.metric("📊 Margem Geral", f"{margem:.2f}%")

