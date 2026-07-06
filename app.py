import streamlit as st
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("vendas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client TEXT,
    total REAL
)
""")

conn.commit()

# ---------------- UI ----------------
st.set_page_config(page_title="Força de Vendas", layout="wide")

st.title("🔥 Força de Vendas")

menu = st.sidebar.selectbox("Menu", ["Clientes", "Produtos", "Pedidos"])

# ---------------- CLIENTES ----------------
if menu == "Clientes":
    st.subheader("Cadastro de Clientes")

    name = st.text_input("Nome")
    phone = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        st.success("Cliente salvo!")

    st.write("### Lista de Clientes")
    data = cursor.execute("SELECT * FROM clients").fetchall()
    st.table(data)

# ---------------- PRODUTOS ----------------
if menu == "Produtos":
    st.subheader("Cadastro de Produtos")

    name = st.text_input("Produto")
    price = st.number_input("Preço", min_value=0.0)

    if st.button("Salvar Produto"):
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        st.success("Produto salvo!")

    st.write("### Lista de Produtos")
    data = cursor.execute("SELECT * FROM products").fetchall()
    st.table(data)

# ---------------- PEDIDOS ----------------
if menu == "Pedidos":
    st.subheader("Criar Pedido")

    client = st.text_input("Cliente")
    total = st.number_input("Total do Pedido", min_value=0.0)

    if st.button("Salvar Pedido"):
        cursor.execute("INSERT INTO orders (client, total) VALUES (?, ?)", (client, total))
        conn.commit()
        st.success("Pedido salvo!")

    st.write("### Lista de Pedidos")
    data = cursor.execute("SELECT * FROM orders").fetchall()
    st.table(data)
