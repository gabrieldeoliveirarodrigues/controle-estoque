import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

st.title("📦 Sistema de Controle de Estoque - Web")

# Sessões para armazenar dados durante a execução
if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=[
        "Produto Técnico", "Tipo", "Medida", "Marca/Grupo", "Quantidade", "Unidade"])

if "historico" not in st.session_state:
    st.session_state.historico = []

# Seção para importar base de dados
st.sidebar.header("📁 Importar Base de Dados")
arquivo = st.sidebar.file_uploader("Selecione um arquivo Excel (.xlsx)", type=["xlsx"])
if arquivo:
    df_importado = pd.read_excel(arquivo)

    import re
    def processar_estrutura(row):
        descricao = row['ESTRUTURAS']
        estoque_raw = row['ESTOQUE']

        match_qtd = re.match(r"(\d+)\s+(\w+)", str(estoque_raw))
        qtd = int(match_qtd.group(1)) if match_qtd else None
        unid = match_qtd.group(2) if match_qtd else None

        produto = descricao.upper().strip()
        tipo = medida = marca = "-"

        if "TRILHO" in produto:
            tipo = "Trilho"
            medida_search = re.search(r"(\d+[,.]?\d*)", produto)
            if medida_search:
                medida = medida_search.group(1).replace(",", ".") + " m"
        elif "PARAFUSO" in produto:
            tipo = "Parafuso Estrutural"
            medida_search = re.search(r"(M\d+\s?X\s?\d+)", produto.replace(" ", "").upper())
            if medida_search:
                medida = medida_search.group(1).replace("X", " x ")
        elif "GANCHO" in produto:
            tipo = "Gancho"
        elif "FIM DE CURSO" in produto:
            tipo = "Fim de Curso"
        elif "INTERMEDIARIO" in produto:
            tipo = "Intermediário"
        elif "JUNÇÃO" in produto:
            tipo = "JUNÇÃO"
        elif "TELHA" in produto:
            tipo = "L de Fixação"
        else:
            tipo = "Componente"

        if "2P" in produto:
            marca = "2P GROUP"
        elif "IZI" in produto:
            marca = "IZI"
        elif "SOLAR GROUP" in produto or "THUNDER" in produto:
            marca = "SOLAR GROUP"
        elif "MADEIRA" in produto:
            marca = "2P MADEIRA"
        elif "METAL" in produto:
            marca = "2P METAL"

        return pd.Series({
            "Produto Técnico": produto.title(),
            "Tipo": tipo,
            "Medida": medida,
            "Marca/Grupo": marca,
            "Quantidade": qtd,
            "Unidade": unid
        })

    st.session_state.estoque = df_importado.apply(processar_estrutura, axis=1)
    st.success("Dados importados com sucesso!")

# Mostrar estoque atual
st.subheader("📊 Estoque Atual")
if not st.session_state.estoque.empty:
    st.dataframe(st.session_state.estoque, use_container_width=True)
else:
    st.info("Nenhum dado de estoque disponível. Importe uma planilha para começar.")

# Registrar movimentação
st.markdown("---")
st.subheader("➕➖ Registrar Movimentação")

if st.session_state.estoque.empty:
    st.warning("Importe dados primeiro para registrar movimentações.")
else:
    produto = st.selectbox("Produto", st.session_state.estoque["Produto Técnico"])
    tipo = st.radio("Tipo de Movimentação", ["Entrada", "Saída"])
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    data_mov = st.date_input("Data", value=datetime.date.today())
    obs = st.text_input("Observação (opcional)")

    if st.button("Registrar"):
        idx = st.session_state.estoque[st.session_state.estoque["Produto Técnico"] == produto].index[0]
        if tipo == "Entrada":
            st.session_state.estoque.at[idx, "Quantidade"] += quantidade
        else:
            if st.session_state.estoque.at[idx, "Quantidade"] >= quantidade:
                st.session_state.estoque.at[idx, "Quantidade"] -= quantidade
            else:
                st.error("Quantidade insuficiente em estoque.")
                st.stop()

        st.session_state.historico.append({
            "Data": data_mov,
            "Produto": produto,
            "Tipo": tipo,
            "Quantidade": quantidade,
            "Observação": obs
        })
        st.success("Movimentação registrada com sucesso!")

# Histórico
st.markdown("---")
st.subheader("📜 Histórico de Movimentações")

if st.session_state.historico:
    hist_df = pd.DataFrame(st.session_state.historico)
    st.dataframe(hist_df.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Nenhuma movimentação registrada ainda.")