import streamlit as st
import pandas as pd

# ==============================
# Configuração da Page
# ==============================
st.set_page_config(page_title="Relatório de Repasse", layout="wide")
st.title("📊 Relatório de Repasse")

# ==============================
# Importação do Excel Base
# ==============================
excel_path = "Repasse.xlsx"

try:
    df = pd.read_excel(excel_path)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo Excel: {e}")
    st.stop()

# ==============================
# Ajuste de nomes de colunas
# ==============================
df.columns = [col.strip().upper() for col in df.columns]

df = df.rename(columns={
    "GERADOR": "Gerador",
    "USINA": "Usina",
    "CLIENTE FINAL": "Cliente Final",
    "MÊS DE COMPETÊNCIA": "Mês de Competência",
    "FATURAMENTO": "Faturamento do Cliente Final",
    "DESCONTO GESTÃO": "Desconto de Gestão",
    "DESCONTO NFS-E": "Desconto NFS-e",
    "TOTAL Á PAGAR": "Total a Pagar"
})

# ==============================
# Tratamento de Data
# ==============================
df["Mês de Competência"] = pd.to_datetime(
    df["Mês de Competência"],
    errors="coerce"
)

df["Ano"] = df["Mês de Competência"].dt.year
df["Mes_Num"] = df["Mês de Competência"].dt.month

meses_abrev = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
    5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

df["Mes_Ano"] = (
    df["Mes_Num"].map(meses_abrev) + "/" + df["Ano"].astype(str)
)

# ==============================
# Configuração de Percentuais
# ==============================
st.sidebar.header("Configurações de Percentuais")
percentual_gestao = st.sidebar.number_input("Percentual de Gestão (%)", 0.0, 100.0, 10.0, 0.1)
aliquota_nfse = st.sidebar.number_input("Alíquota NFS-e (%)", 0.0, 100.0, 11.33, 0.1)

# ==============================
# Cálculos Automáticos
# ==============================
df["Desconto de Gestão"] = df["Faturamento do Cliente Final"].fillna(0) * (percentual_gestao / 100)
df["Desconto NFS-e"] = df["Faturamento do Cliente Final"].fillna(0) * (aliquota_nfse / 100)
df["Total a Pagar"] = df["Faturamento do Cliente Final"].fillna(0) - df["Desconto de Gestão"] - df["Desconto NFS-e"]

# ==============================
# Filtros
# ==============================
st.sidebar.header("Filtros")
filtro_mes = st.sidebar.multiselect(
    "Mês de Competência",
    df.sort_values(["Ano", "Mes_Num"])["Mes_Ano"].dropna().unique()
)

filtro_usina = st.sidebar.multiselect("Usina", df["Usina"].dropna().unique())
filtro_cliente = st.sidebar.multiselect("Cliente Final", df["Cliente Final"].dropna().unique())

df_filtrado = df.copy()
if filtro_mes:
    df_filtrado = df_filtrado[df_filtrado["Mes_Ano"].isin(filtro_mes)]
if filtro_usina:
    df_filtrado = df_filtrado[df_filtrado["Usina"].isin(filtro_usina)]
if filtro_cliente:
    df_filtrado = df_filtrado[df_filtrado["Cliente Final"].isin(filtro_cliente)]

# ==============================
# Formatação de Valores
# ==============================
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

df_display = df_filtrado.copy()

# Substituir exibição da data pelo formato Jan/2026
df_display["Mês de Competência"] = df_display["Mes_Ano"]

for col in ["Faturamento do Cliente Final", "Desconto de Gestão", "Desconto NFS-e", "Total a Pagar"]:
    df_display[col] = df_display[col].apply(format_currency)


# ==============================
# Exibição da Tabela
# ==============================
st.subheader("Tabela Consolidada")
st.dataframe(df_display, use_container_width=True)

# ==============================
# Totais Consolidados com Layout Estilizado
# ==============================
st.subheader("Totais Consolidados")

# Cálculo dos totais
total_faturamento = df_filtrado["Faturamento do Cliente Final"].sum()
total_gestao = df_filtrado["Desconto de Gestão"].sum()
total_nfse = df_filtrado["Desconto NFS-e"].sum()
total_pagar = df_filtrado["Total a Pagar"].sum()

# Exibição em colunas
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Faturamento Total", format_currency(total_faturamento))
col2.metric("📉 Desc. Gestão", format_currency(total_gestao))
col3.metric("📉 Desc. NFS-e", format_currency(total_nfse))
col4.metric("✅ Total a Pagar", format_currency(total_pagar))

# Explicação dos percentuais aplicados
with st.expander("ℹ️ Percentuais Aplicados"):
    st.markdown(f"""
    • **Desconto de Gestão:** {percentual_gestao:.2f}% sobre o faturamento  
    • **Desconto NFS-e:** {aliquota_nfse:.2f}% sobre o faturamento  
    • **Fórmula:**  
      `Total a Pagar = Faturamento - Desconto Gestão - Desconto NFS-e`
    """)
