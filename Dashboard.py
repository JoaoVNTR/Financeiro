import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard GD - Faturamento",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #00000;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric label {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    .stMetric .metric-value {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding-top: 20px;
    }
    .filtro-container {
        background-color: ##FFB549;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def carregar_dados():
    """Carrega os dados do Excel"""
    try:
        df = pd.read_excel('fat.xlsx', sheet_name='FATURAMENTO Á RECEBER')
        
        # Limpeza e preparação dos dados
        df.columns = df.columns.str.strip()
        
        # Converter colunas numéricas
        df['Valor a Pagar para Gerador (R$)'] = pd.to_numeric(df['Valor a Pagar para Gerador (R$)'], errors='coerce')
        df['% Gestão'] = pd.to_numeric(df['% Gestão'], errors='coerce')
        df['Valor da Gestão (R$)'] = pd.to_numeric(df['Valor da Gestão (R$)'], errors='coerce')
        
        # Preencher valores nulos
        df.fillna(0, inplace=True)
        
        # Garantir que Mês de Competência seja string
        df['Mês de Competência'] = df['Mês de Competência'].astype(str)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Função para aplicar filtros
def aplicar_filtros(df, meses, geradores, usinas, clientes):
    """Aplica filtros combinados ao DataFrame"""
    df_filtrado = df.copy()
    
    if meses and len(meses) > 0:
        df_filtrado = df_filtrado[df_filtrado['Mês de Competência'].isin(meses)]
    
    if geradores and len(geradores) > 0:
        df_filtrado = df_filtrado[df_filtrado['Gerador'].isin(geradores)]
    
    if usinas and len(usinas) > 0:
        df_filtrado = df_filtrado[df_filtrado['Usina'].isin(usinas)]
    
    if clientes and len(clientes) > 0:
        df_filtrado = df_filtrado[df_filtrado['Cliente Final'].isin(clientes)]
    
    return df_filtrado

# Carregar dados
df = carregar_dados()

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique o arquivo Excel.")
    st.stop()

# Armazenar dados no session_state
if 'df_original' not in st.session_state:
    st.session_state['df_original'] = df

# Título Principal
st.title("⚡ Dashboard Executivo - Geração Distribuída")
st.markdown("---")

# Sidebar com filtros
with st.sidebar:
    st.image("https://via.placeholder.com/250x80/1f77b4/ffffff?text=GD+Analytics", use_container_width=True)
    st.markdown("## 🎛️ Filtros Interativos")
    st.markdown("---")
    
    # Filtro de Mês
    meses_disponiveis = sorted(df['Mês de Competência'].unique().tolist())
    meses_selecionados = st.multiselect(
        "📅 Mês de Competência",
        options=meses_disponiveis,
        default=meses_disponiveis,
        help="Selecione um ou mais meses"
    )
    
    # Filtro de Gerador
    geradores_disponiveis = sorted(df['Gerador'].unique().tolist())
    geradores_selecionados = st.multiselect(
        "🏭 Gerador",
        options=geradores_disponiveis,
        default=geradores_disponiveis,
        help="Selecione um ou mais geradores"
    )
    
    # Filtro de Usina
    usinas_disponiveis = sorted(df['Usina'].unique().tolist())
    usinas_selecionadas = st.multiselect(
        "⚡ Usina",
        options=usinas_disponiveis,
        default=usinas_disponiveis,
        help="Selecione uma ou mais usinas"
    )
    
    # Filtro de Cliente Final
    clientes_disponiveis = sorted(df['Cliente Final'].unique().tolist())
    clientes_selecionados = st.multiselect(
        "👥 Cliente Final",
        options=clientes_disponiveis,
        default=[],
        help="Selecione clientes específicos (opcional)"
    )
    
    st.markdown("---")
    
    # Botão para resetar filtros
    if st.button("🔄 Resetar Filtros", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Informações do Dataset")
    st.info(f"""
    **Total de Registros:** {len(df):,}  
    **Período:** {', '.join(meses_disponiveis)}  
    **Última Atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """)

# Aplicar filtros
df_filtrado = aplicar_filtros(df, meses_selecionados, geradores_selecionados, 
                               usinas_selecionadas, clientes_selecionados)

# Armazenar dados filtrados no session_state
st.session_state['df_filtrado'] = df_filtrado

# Verificar se há dados após filtros
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados. Ajuste os filtros na barra lateral.")
    st.stop()

# KPIs Principais
st.markdown("## 📈 Indicadores Principais")

col1, col2, col3 = st.columns(3)

with col1:
    faturamento_total = df_filtrado['Valor a Pagar para Gerador (R$)'].sum()
    st.metric(
        label="💰 Faturamento Total",
        value=f"R$ {faturamento_total:,.2f}",
        delta=f"{len(df_filtrado)} registros"
    )

with col2:
    receita_gestao = df_filtrado['Valor da Gestão (R$)'].sum()
    st.metric(
        label="💵 Receita de Gestão",
        value=f"R$ {receita_gestao:,.2f}",
        delta=f"{(receita_gestao/faturamento_total*100) if faturamento_total > 0 else 0:.1f}% do faturamento"
    )

with col3:
    total_clientes = df_filtrado['Cliente Final'].nunique()
    st.metric(
        label="👥 Clientes Atendidos",
        value=f"{total_clientes}",
        delta="Únicos"
    )

col4, col5, col6 = st.columns(3)

with col4:
    ticket_medio = faturamento_total / total_clientes if total_clientes > 0 else 0
    st.metric(
        label="🎯 Ticket Médio por Cliente",
        value=f"R$ {ticket_medio:,.2f}",
        delta="Por cliente final"
    )

with col5:
    total_usinas = df_filtrado['Usina'].nunique()
    receita_media_usina = faturamento_total / total_usinas if total_usinas > 0 else 0
    st.metric(
        label="⚡ Receita Média por Usina",
        value=f"R$ {receita_media_usina:,.2f}",
        delta=f"{total_usinas} usinas ativas"
    )

with col6:
    total_geradores = df_filtrado['Gerador'].nunique()
    st.metric(
        label="🏭 Geradores Ativos",
        value=f"{total_geradores}",
        delta=f"{total_usinas} usinas"
    )

st.markdown("---")

# Gráficos Principais
st.markdown("## 📊 Análise Visual")

# Evolução Mensal
st.markdown("### 📈 Evolução do Faturamento Mensal")

evolucao_mensal = df_filtrado.groupby('Mês de Competência').agg({
    'Valor a Pagar para Gerador (R$)': 'sum',
    'Valor da Gestão (R$)': 'sum'
}).reset_index()

fig_evolucao = go.Figure()

fig_evolucao.add_trace(go.Scatter(
    x=evolucao_mensal['Mês de Competência'],
    y=evolucao_mensal['Valor a Pagar para Gerador (R$)'],
    mode='lines+markers',
    name='Faturamento Total',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=10),
    hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
))

fig_evolucao.add_trace(go.Scatter(
    x=evolucao_mensal['Mês de Competência'],
    y=evolucao_mensal['Valor da Gestão (R$)'],
    mode='lines+markers',
    name='Receita de Gestão',
    line=dict(color='#ff7f0e', width=3),
    marker=dict(size=10),
    hovertemplate='<b>%{x}</b><br>Receita Gestão: R$ %{y:,.2f}<extra></extra>'
))

fig_evolucao.update_layout(
    height=400,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_title="Mês de Competência",
    yaxis_title="Valor (R$)",
    template="plotly_white"
)

st.plotly_chart(fig_evolucao, use_container_width=True)

# Análise por Gerador
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏭 Faturamento por Gerador")
    
    faturamento_gerador = df_filtrado.groupby('Gerador')['Valor a Pagar para Gerador (R$)'].sum().sort_values(ascending=True)
    
    fig_gerador_bar = go.Figure(go.Bar(
        x=faturamento_gerador.values,
        y=faturamento_gerador.index,
        orientation='h',
        marker=dict(color='#1f77b4'),
        hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig_gerador_bar.update_layout(
        height=400,
        xaxis_title="Faturamento (R$)",
        yaxis_title="Gerador",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_gerador_bar, use_container_width=True)

with col2:
    st.markdown("### 📊 Participação por Gerador")
    
    fig_gerador_pie = px.pie(
        values=faturamento_gerador.values,
        names=faturamento_gerador.index,
        hole=0.4
    )
    
    fig_gerador_pie.update_traces(
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
    )
    
    fig_gerador_pie.update_layout(
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig_gerador_pie, use_container_width=True)

st.markdown("---")

# Informações de Navegação
st.info("""
📌 **Navegue pelas páginas do dashboard:**
- **📊 Painel Executivo** (Página atual): Visão geral consolidada
- **💰 Painel Financeiro**: Análise detalhada de receitas e margens
- **⚡ Painel Operacional**: Performance por usina e gerador
- **📋 Relatório Detalhado**: Tabela completa com drill-down

Use os filtros na barra lateral para refinar sua análise!
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p><b>Dashboard de Faturamento - Geração Distribuída</b></p>
    <p>Desenvolvido com Streamlit & Plotly | © 2024</p>
</div>
""", unsafe_allow_html=True)
