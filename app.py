import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime
import pytz

# Configuração inicial da página
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Chamados da Sprint")

# Caminhos dos arquivos
csv_path = "organizacao_chamados.csv"
log_path = "ultima_atualizacao.txt"

# Função para salvar a data de modificação no arquivo de log
def salvar_log_modificacao():
    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_brasil)
    with open(log_path, "w") as f:
        f.write(agora.strftime('%d/%m/%Y %H:%M:%S'))

# Função para ler a última data de modificação
def ler_log_modificacao():
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return f.read()
    else:
        return "Nunca atualizado"

# Mostrar última modificação registrada
ultima_atualizacao = ler_log_modificacao()
st.markdown(f"🕒 **Última atualização registrada:** {ultima_atualizacao}")

# Carregar dados
df = pd.read_csv(csv_path, sep=",", encoding="utf-8", quotechar='"', on_bad_lines='skip')
df.columns = df.columns.str.strip().str.upper()  # Padroniza os nomes das colunas

# Padroniza valores textuais
for col in ["STATUS", "MÓDULO", "ORDEM", "RESPONSÁVEL"]:
    df[col] = df[col].astype(str).str.strip().str.upper()

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    busca = st.text_input("Buscar por qualquer termo")

    ordem_filter = st.multiselect("Ordem de Prioridade", options=sorted(df["ORDEM"].unique()), default=sorted(df["ORDEM"].unique()))
    modulo_filter = st.multiselect("Módulo", options=sorted(df["MÓDULO"].unique()), default=sorted(df["MÓDULO"].unique()))
    status_filter = st.multiselect("Status", options=sorted(df["STATUS"].dropna().unique()), default=sorted(df["STATUS"].dropna().unique()))

# Aplicar filtros
df_filtrado = df[
    (df["ORDEM"].isin(ordem_filter)) &
    (df["MÓDULO"].isin(modulo_filter)) &
    (df["STATUS"].isin(status_filter))
]

# Aplicar busca (não sensível a maiúsculas)
if busca:
    busca = busca.lower()
    df_filtrado = df_filtrado[df_filtrado.apply(lambda row: row.astype(str).str.lower().str.contains(busca).any(), axis=1)]

# Exibir e editar dados filtrados
st.markdown("### ✏️ Editar Chamados")
edited_df = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "STATUS": st.column_config.TextColumn("Status"),
        "RESPONSÁVEL": st.column_config.TextColumn("Responsável")
    },
    disabled=["ID", "MÓDULO", "ORDEM"]
)

# Botão para salvar alterações
if st.button("💾 Salvar Alterações"):
    for _, row in edited_df.iterrows():
        match = (df["ID"] == row["ID"])
        df.loc[match, "STATUS"] = row["STATUS"]
        df.loc[match, "RESPONSÁVEL"] = row["RESPONSÁVEL"]

    df.to_csv(csv_path, index=False, encoding="utf-8", sep=",")
    salvar_log_modificacao()
    st.success("Alterações salvas com sucesso!")

# -----------------------------------------
# Gráficos customizados com plotly.graph_objects
# -----------------------------------------

# Gráfico - Quantidade por Status
st.subheader("📈 Quantidade de Chamados por Status")
status_counts = df_filtrado["STATUS"].value_counts().reset_index()
status_counts.columns = ["STATUS", "QUANTIDADE"]

fig_status = go.Figure(
    data=[go.Bar(
        x=status_counts["STATUS"],
        y=status_counts["QUANTIDADE"],
        text=status_counts["QUANTIDADE"],
        textposition="auto",
        marker_color="skyblue"
    )]
)
fig_status.update_layout(
    title="Distribuição de Chamados por Status",
    xaxis_title="",
    yaxis_title="Quantidade",
    showlegend=False
)
st.plotly_chart(fig_status, use_container_width=True)

# Gráfico - Quantidade por Módulo (Pizza)
st.subheader("📊 Quantidade de Chamados por Módulo")
modulo_counts = df_filtrado["MÓDULO"].value_counts().reset_index()
modulo_counts.columns = ["MÓDULO", "QUANTIDADE"]

fig_modulo = go.Figure(
    data=[go.Pie(
        labels=modulo_counts["MÓDULO"],
        values=modulo_counts["QUANTIDADE"],
        hole=0.4
    )]
)
fig_modulo.update_layout(title="Chamados por Módulo")
st.plotly_chart(fig_modulo, use_container_width=True)

# Gráfico - Quantidade por Ordem
st.subheader("📉 Quantidade de Chamados por Ordem de Prioridade")
ordem_counts = df_filtrado["ORDEM"].value_counts().reset_index()
ordem_counts.columns = ["ORDEM", "QUANTIDADE"]

fig_ordem = go.Figure(
    data=[go.Bar(
        x=ordem_counts["ORDEM"],
        y=ordem_counts["QUANTIDADE"],
        text=ordem_counts["QUANTIDADE"],
        textposition="auto",
        marker_color="orange"
    )]
)
fig_ordem.update_layout(
    title="Distribuição de Chamados por Ordem de Prioridade",
    xaxis_title="Ordem",
    yaxis_title="Quantidade",
    showlegend=False
)
st.plotly_chart(fig_ordem, use_container_width=True)
