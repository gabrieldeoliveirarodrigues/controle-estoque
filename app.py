
import streamlit as st
import pandas as pd
import sqlite3
import io
import datetime
from matplotlib import pyplot as plt

# Conexão com banco de dados
conn = sqlite3.connect("estoque.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela de estoque se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    quantidade INTEGER,
    unidade TEXT,
    data TEXT,
    tipo TEXT
, ultima_modificacao TEXT)
""")
conn.commit()

# Função para inserir movimentação
def registrar_movimentacao(nome, quantidade, unidade, tipo, usuario="Desconhecido"):
    data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO estoque (nome, quantidade, unidade, data, tipo) VALUES (?, ?, ?, ?, ?)",
                   (nome, quantidade, unidade, data, tipo))
    conn.commit()

# Função para obter o estoque atual
def obter_estoque_atual():
    df = pd.read_sql_query("SELECT nome, unidade, SUM(CASE WHEN tipo = 'entrada' THEN quantidade ELSE -quantidade END) as saldo FROM estoque GROUP BY nome, unidade", conn)
    return df


# Verifica e adiciona coluna 'usuario' se necessário
try:
    cursor.execute("ALTER TABLE estoque ADD COLUMN usuario TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Coluna já existe

# Função modificada para incluir usuário
def registrar_movimentacao(nome, quantidade, unidade, tipo, usuario="Desconhecido"):
    data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO estoque (nome, quantidade, unidade, data, tipo, usuario) VALUES (?, ?, ?, ?, ?, ?)",
                   (nome, quantidade, unidade, data, tipo, usuario))
    conn.commit()

# Layout principal
st.set_page_config(page_title="Controle de Estoque", layout="wide")
st.title("📦 Controle de Estoque")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Entrada", "Saída", "Estoque Atual", "Histórico", "Exportar", "Gráficos", "Sugerir Melhorias", "Última Modificação"])

if menu == "Entrada":
    st.subheader("➕ Entrada de Produtos")
    with st.form("entrada_form"):
        nome = st.text_input("Nome do Produto")
        quantidade = st.number_input("Quantidade", min_value=1)
        unidade = st.selectbox("Unidade", ["un", "kg", "litro", "cx", "pc"])
        submitted = st.form_submit_button("Registrar Entrada")
        if submitted:
            registrar_movimentacao(nome, quantidade, unidade, "entrada", "Usuário")
            st.success(f"Entrada de {quantidade} {unidade} de {nome} registrada com sucesso!")

elif menu == "Saída":
    st.subheader("➖ Saída de Produtos")
    with st.form("saida_form"):
        nome = st.text_input("Nome do Produto")
        quantidade = st.number_input("Quantidade", min_value=1)
        unidade = st.selectbox("Unidade", ["un", "kg", "litro", "cx", "pc"])
        submitted = st.form_submit_button("Registrar Saída")
        if submitted:
            registrar_movimentacao(nome, quantidade, unidade, "saida", "Usuário")
            st.success(f"Saída de {quantidade} {unidade} de {nome} registrada com sucesso!")

elif menu == "Estoque Atual":
    st.subheader("📋 Estoque Atual")
    df = obter_estoque_atual()
    df["alerta"] = df["saldo"].apply(lambda x: "⚠️" if x <= 20 else "")
    st.dataframe(df)

elif menu == "Histórico":
    st.subheader("📜 Histórico de Movimentações")
    df = pd.read_sql_query("SELECT * FROM estoque ORDER BY data DESC", conn)
    st.dataframe(df)

elif menu == "Exportar":
    st.subheader("📄 Exportar Dados")
    df = pd.read_sql_query("SELECT * FROM estoque", conn)

    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar para CSV", data=csv, file_name="estoque.csv", mime="text/csv")

    with col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Estoque")
        st.download_button("⬇️ Exportar para Excel", data=excel_buffer, file_name="estoque.xlsx", mime="application/vnd.ms-excel")

elif menu == "Gráficos":
    st.subheader("📊 Gráfico de Movimentações")
    df = pd.read_sql_query("SELECT data, quantidade, tipo FROM estoque", conn)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"]).dt.date
        graf = df.groupby(["data", "tipo"])["quantidade"].sum().unstack().fillna(0)
        st.bar_chart(graf)
    else:
        st.info("Nenhuma movimentação registrada.")

elif menu == "Sugerir Melhorias":
    st.subheader("💡 Sugestão de Melhorias")
    sugestao = st.text_area("O que podemos melhorar?")
    if st.button("Enviar Sugestão"):
        with open("sugestoes.txt", "a", encoding="utf-8") as f:
            f.write(sugestao + "\n")
        st.success("Obrigado pela sugestão!")


elif menu == "Última Modificação":
    st.subheader("👤 Última Modificação")
    df = pd.read_sql_query("SELECT nome, usuario, MAX(data) as data FROM estoque GROUP BY nome", conn)
    st.dataframe(df)
