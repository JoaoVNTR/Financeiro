import streamlit as st
import pandas as pd

# ======================================================
# Função de formatação em Real (R$)
# ======================================================
def real_br(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# ======================================================
# Configuração
# ======================================================
st.set_page_config(
    page_title="Relatório Detalhado",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Relatório Detalhado")
st.markdown("### Tabela Completa com Drill-Down")
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
    st.markdown("## 🎛️ Filtros – Relatório")
    st.markdown("---")

    meses = sorted(df["Mês de Competência"].unique())
    meses_sel = st.multiselect(
        "📅 Mês de Competência",
        meses,
        default=meses,
        key="relatorio_mes"
    )

    geradores = sorted(df["Gerador"].unique())
    geradores_sel = st.multiselect(
        "🏭 Gerador",
        geradores,
        key="relatorio_gerador"
    )

    usinas = sorted(df["Usina"].unique())
    usinas_sel = st.multiselect(
        "⚡ Usina",
        usinas,
        key="relatorio_usina"
    )

    clientes = sorted(df["Cliente Final"].unique())
    clientes_sel = st.multiselect(
        "👥 Cliente Final",
        clientes,
        key="relatorio_cliente"
    )

    st.markdown("---")
    if st.button("🔄 Resetar filtros", key="relatorio_reset"):
        st.rerun()

# ======================================================
# 3️⃣ Aplicação dos filtros
# ======================================================
if meses_sel:
    df = df[df["Mês de Competência"].isin(meses_sel)]

if geradores_sel:
    df = df[df["Gerador"].isin(geradores_sel)]

if usinas_sel:
    df = df[df["Usina"].isin(usinas_sel)]

if clientes_sel:
    df = df[df["Cliente Final"].isin(clientes_sel)]

if df.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ======================================================
# 4️⃣ KPIs do relatório
# ======================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Registros", f"{len(df):,}")

with col2:
    total_fat = df["Valor a Pagar para Gerador (R$)"].sum()
    st.metric("💰 Faturamento", real_br(total_fat))

with col3:
    total_rec = df["Valor da Gestão (R$)"].sum()
    st.metric("💵 Receita Gestão", real_br(total_rec))

with col4:
    st.metric("🏭 Geradores", df["Gerador"].nunique())

st.markdown("---")

# ======================================================
# 5️⃣ Opções de visualização
# ======================================================
st.markdown("### ⚙️ Opções de Visualização")

col1, col2, col3 = st.columns(3)

with col1:
    nivel = st.selectbox(
        "Nível de Agregação",
        [
            "Detalhado",
            "Por Gerador",
            "Por Usina",
            "Por Cliente",
            "Por Mês"
        ],
        key="relatorio_nivel"
    )

with col2:
    ordenar_por = st.selectbox(
        "Ordenar por",
        df.columns.tolist(),
        key="relatorio_ordem"
    )

with col3:
    ordem_crescente = st.checkbox(
        "Ordem crescente",
        value=False,
        key="relatorio_crescente"
    )

st.markdown("---")

# ======================================================
# 6️⃣ Drill-down / agregações
# ======================================================
if nivel == "Detalhado":
    df_display = df[[
        "Gerador",
        "Usina",
        "Cliente Final",
        "Mês de Competência",
        "Valor a Pagar para Gerador (R$)",
        "% Gestão",
        "Valor da Gestão (R$)"
    ]].copy()

elif nivel == "Por Gerador":
    df_display = df.groupby("Gerador").agg({
        "Valor a Pagar para Gerador (R$)": "sum",
        "Valor da Gestão (R$)": "sum",
        "% Gestão": "mean",
        "Usina": "nunique",
        "Cliente Final": "nunique"
    }).reset_index()

elif nivel == "Por Usina":
    df_display = df.groupby(["Gerador", "Usina"]).agg({
        "Valor a Pagar para Gerador (R$)": "sum",
        "Valor da Gestão (R$)": "sum",
        "% Gestão": "mean",
        "Cliente Final": "nunique"
    }).reset_index()

elif nivel == "Por Cliente":
    df_display = df.groupby(
        ["Gerador", "Usina", "Cliente Final"]
    ).agg({
        "Valor a Pagar para Gerador (R$)": "sum",
        "Valor da Gestão (R$)": "sum",
        "% Gestão": "mean"
    }).reset_index()

else:  # Por Mês
    df_display = df.groupby(
        ["Mês de Competência", "Gerador"]
    ).agg({
        "Valor a Pagar para Gerador (R$)": "sum",
        "Valor da Gestão (R$)": "sum",
        "% Gestão": "mean",
        "Usina": "nunique",
        "Cliente Final": "nunique"
    }).reset_index()

# ======================================================
# 7️⃣ Ordenação
# ======================================================
if ordenar_por in df_display.columns:
    df_display = df_display.sort_values(
        ordenar_por,
        ascending=ordem_crescente
    )
def formato_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ======================================================
# 8️⃣ Exibição da tabela
# ======================================================
st.markdown(f"### 📊 Visualização — {nivel}")
colunas_reais = [
    "Valor a Pagar para Gerador (R$)",
    "Valor da Gestão (R$)"
]

df_styled = df_display.style.format({
    col: formato_real
    for col in colunas_reais
    if col in df_display.columns
})

st.dataframe(df_styled, use_container_width=True, height=500)


# ======================================================
# 9️⃣ Estatísticas do recorte atual
# ======================================================
st.markdown("---")
st.markdown("### 📈 Estatísticas do Relatório")

total_fat = df_display.filter(
    like="Valor a Pagar"
).sum(numeric_only=True).sum()

total_rec = df_display.filter(
    like="Valor da Gestão"
).sum(numeric_only=True).sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Faturamento", real_br(total_fat))

with col2:
    st.metric("💵 Total Receita", real_br(total_rec))

with col3:
    margem = (total_rec / total_fat * 100) if total_fat else 0
    st.metric("📊 Margem Geral", f"{margem:.2f}%")
