import json
import os
import uuid
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(
    page_title="Tigrão Distribuidora",
    page_icon="🐯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_DIR = "dados_tigrao"
DB_FILE = os.path.join(DATA_DIR, "banco.json")
os.makedirs(DATA_DIR, exist_ok=True)

STATUS = ["Pendente", "Faturado", "Entregue", "Cancelado"]

INITIAL_PRODUCTS = [
    {"id": "prod-1", "name": "Cerveja Heineken Long Neck 330ml", "sku": "HEI-001", "price": 8.50, "stock": 120, "category": "Cervejas", "commissionRate": 3},
    {"id": "prod-2", "name": "Cigarro Rothmans Red Box", "sku": "ROT-002", "price": 9.75, "stock": 450, "category": "Tabacaria", "commissionRate": 5},
    {"id": "prod-3", "name": "Refrigerante Coca-Cola 2L", "sku": "COC-003", "price": 11.90, "stock": 250, "category": "Refrigerantes", "commissionRate": 4},
    {"id": "prod-4", "name": "Energético Monster Energy 473ml", "sku": "MON-004", "price": 10.50, "stock": 180, "category": "Energéticos", "commissionRate": 4},
    {"id": "prod-5", "name": "Água Mineral Sem Gás 500ml", "sku": "AGU-005", "price": 2.50, "stock": 600, "category": "Águas", "commissionRate": 2},
    {"id": "prod-6", "name": "Cerveja Amstel Lata 350ml", "sku": "AMS-006", "price": 4.20, "stock": 320, "category": "Cervejas", "commissionRate": 3},
    {"id": "prod-7", "name": "Vodka Smirnoff 998ml", "sku": "SMI-007", "price": 39.90, "stock": 65, "category": "Destilados", "commissionRate": 4},
    {"id": "prod-8", "name": "Whisky Johnnie Walker Red Label 1L", "sku": "JWL-008", "price": 99.90, "stock": 40, "category": "Destilados", "commissionRate": 4},
]

INITIAL_CLIENTS = [
    {"id": "cli-1", "name": "nelson das galaxie", "document": "123.456.789-00", "email": "nelson@galaxie.com", "phone": "(11) 98888-7777", "city": "São Paulo", "state": "SP"},
    {"id": "cli-2", "name": "Distribuidora Silva & Silva", "document": "98.765.432/0001-11", "email": "silva@distribuidora.com", "phone": "(11) 3245-8899", "city": "Campinas", "state": "SP"},
    {"id": "cli-3", "name": "Mercadinho do Bairro Ltda", "document": "45.123.789/0001-44", "email": "contato@mercadinhobairro.com", "phone": "(21) 97777-6666", "city": "Rio de Janeiro", "state": "RJ"},
    {"id": "cli-4", "name": "Adega Central", "document": "55.666.777/0001-88", "email": "adega.central@outlook.com", "phone": "(19) 99122-3344", "city": "Piracicaba", "state": "SP"},
]

INITIAL_SALES = [
    {"id": "sales-1", "name": "Vendedor", "email": "vendedor@tigrao.com", "active": True, "cpf": "111.111.111-11", "phone": "(11) 91111-1111", "address": "Rua Principal, 100", "password": "123", "passwordIsTemporary": True},
    {"id": "sales-2", "name": "Carlos Souza", "email": "carlos@tigrao.com", "active": True, "cpf": "222.222.222-22", "phone": "(11) 92222-2222", "address": "Avenida Brasil, 250", "password": "123", "passwordIsTemporary": False},
    {"id": "sales-3", "name": "Fernanda Lima", "email": "fernanda@tigrao.com", "active": True, "cpf": "333.333.333-33", "phone": "(11) 93333-3333", "address": "Praça das Flores, 15", "password": "123", "passwordIsTemporary": False},
]

INITIAL_ORDERS = [
    {"id": "ord-0", "orderNumber": 0, "date": "2026-06-30T17:34:36", "salespersonId": "sales-1", "salespersonName": "Vendedor", "clientId": "cli-1", "clientName": "nelson das galaxie", "items": [{"productId": "prod-8", "productName": "Whisky Johnnie Walker Red Label 1L", "quantity": 20, "price": 99.90}, {"productId": "prod-7", "productName": "Vodka Smirnoff 998ml", "quantity": 30, "price": 39.90}], "total": 3195.00, "commissionRate": 7, "commissionAmount": 223.65, "status": "Faturado"},
]


def seed():
    return {"app": "Tigrão Distribuidora", "systemName": "TIGRÃO", "commissionRate": 7, "products": INITIAL_PRODUCTS, "clients": INITIAL_CLIENTS, "salespeople": INITIAL_SALES, "orders": INITIAL_ORDERS}


@st.cache_data(show_spinner=False)
def load_db_cached(file_mtime: float):
    if not os.path.exists(DB_FILE):
        return seed()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_db():
    if not os.path.exists(DB_FILE):
        save_db(seed())
    return load_db_cached(os.path.getmtime(DB_FILE))


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    load_db_cached.clear()


def money(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def uid(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def today_br():
    return datetime.now().strftime("%d/%m/%Y")


def normalizar(txt):
    txt = str(txt or "").lower().strip()
    troca = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
    for a, b in troca.items():
        txt = txt.replace(a, b)
    return txt


def css():
    st.markdown(
        """
        <style>
        header, footer, [data-testid="stSidebar"] {display:none!important;}
        .block-container{max-width:520px!important;padding:12px 18px 18px!important;}
        .stApp{background:#fff!important;color:#222!important;}
        *{font-family:Arial, Helvetica, sans-serif;}
        .android-bar{height:42px;background:#5f6368;color:white;margin:-12px -18px 22px;padding:10px 14px 0;font-size:17px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:8px;}
        .android-logo{background:#f97316;color:white;width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:18px;}
        .home-head{text-align:center;margin-top:34px;margin-bottom:58px;color:#333;line-height:1.25;}
        .home-head .user{font-size:24px;font-weight:500;}
        .home-head .company{font-size:24px;font-weight:500;}
        .home-head .date{font-size:23px;font-weight:500;}
        .page-title{text-align:center;font-size:38px;font-weight:400;margin:26px 0 22px;color:#333;}
        .footer-info{position:fixed;bottom:42px;left:0;right:0;text-align:center;color:#777;font-size:13px;line-height:1.35;}
        .bottom-select{position:fixed;bottom:0;left:0;right:0;background:#d1d5db;height:38px;color:#333;padding:8px 14px;font-size:18px;border-top:1px solid #aaa;}
        .card{background:white;border:1px solid #eee;border-radius:18px;padding:14px;margin:10px 0;box-shadow:0 4px 14px rgba(0,0,0,.04);}
        .metric{background:#111;color:#fff;border-radius:18px;padding:14px;margin:10px 0;}
        .stButton>button{background:#d1d5db!important;color:#374151!important;border:0!important;border-radius:8px!important;min-height:66px!important;font-size:17px!important;font-weight:700!important;line-height:1.15!important;white-space:pre-line!important;box-shadow:none!important;width:100%!important;}
        .stButton>button:active{transform:scale(.98)!important;background:#c4c9d1!important;}
        .small-btn button{min-height:46px!important;font-size:15px!important;}
        .stTextInput input,.stNumberInput input{border-radius:8px!important;min-height:46px!important;}
        div[data-baseweb="select"]>div{border-radius:8px!important;min-height:46px!important;}
        .stDownloadButton>button{background:#d1d5db!important;color:#374151!important;border:0!important;border-radius:8px!important;min-height:56px!important;font-weight:700!important;width:100%!important;}
        [data-testid="stExpander"]{border:1px solid #ddd!important;border-radius:8px!important;box-shadow:none!important;margin-bottom:8px!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def android_bar():
    st.markdown('<div class="android-bar"><span class="android-logo">🐾</span><span>TIGRÃO DISTRIBUIDORA</span></div>', unsafe_allow_html=True)


def set_page(page):
    st.session_state.page = page
    st.rerun()


def back_button(dest="home"):
    st.markdown('<div class="small-btn">', unsafe_allow_html=True)
    if st.button("VOLTAR", key=f"voltar_{st.session_state.get('page','')}_{dest}"):
        set_page(dest)
    st.markdown('</div>', unsafe_allow_html=True)


def grid_buttons(buttons, prefix):
    for i in range(0, len(buttons), 2):
        c1, c2 = st.columns(2, gap="medium")
        label, dest = buttons[i]
        if c1.button(label, key=f"{prefix}_{i}"):
            if dest == "logout":
                st.session_state.clear()
                st.rerun()
            else:
                set_page(dest)
        if i + 1 < len(buttons):
            label2, dest2 = buttons[i + 1]
            if c2.button(label2, key=f"{prefix}_{i+1}"):
                if dest2 == "logout":
                    st.session_state.clear()
                    st.rerun()
                else:
                    set_page(dest2)


def home_page(db):
    st.markdown(
        f"""
        <div class="home-head">
            <div class="user">{st.session_state.get('user_name','VENDEDOR').upper()}</div>
            <div class="company">TIGRÃO DISTRIBUIDORA</div>
            <div class="date">{today_br()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    buttons = [
        ("PEDIDOS", "orders"),
        ("CLIENTES", "clientes_menu"),
        ("CONSULTAS", "consultas_menu"),
        ("CONFIGURAÇÕES", "config_menu"),
        ("TREINAMENTO", "treinamento"),
        ("COMUNICAÇÃO", "comunicacao"),
        ("SAIR", "logout"),
    ]
    grid_buttons(buttons, "home")
    st.markdown(
        '<div class="footer-info">TIGRÃO DISTRIBUIDORA<br>Comércio e Indústria de Produtos Naturais<br>Rio de Janeiro - RJ<br>Versão 1.0.1</div><div class="bottom-select">TIGRÃO DISTRIBUIDORA ▾</div>',
        unsafe_allow_html=True,
    )


def login(db):
    st.markdown('<div style="height:55px"></div><div style="text-align:center;font-size:60px">🐯</div><h1 style="text-align:center">TIGRÃO</h1><h3 style="text-align:center">Acesso ao sistema</h3>', unsafe_allow_html=True)
    with st.form("login"):
        perfil = st.radio("Perfil", ["Admin", "Vendedor"], horizontal=True)
        usuario = st.text_input("Usuário / e-mail", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        ok = st.form_submit_button("ENTRAR")
    if ok:
        usuario_limpo = usuario.lower().strip()
        if perfil == "Admin" and usuario_limpo in ["admin", "administrador", ""] and senha == "admin123":
            st.session_state.auth = True
            st.session_state.role = "admin"
            st.session_state.sales_id = ""
            st.session_state.user_name = "JOSE"
            st.session_state.page = "home"
            st.rerun()
        sellers = [s for s in db["salespeople"] if s.get("active")]
        seller = next((s for s in sellers if usuario_limpo in [s["email"].lower(), s["name"].lower()] and senha == s.get("password", "123")), None)
        if perfil == "Vendedor" and seller:
            st.session_state.auth = True
            st.session_state.role = "vendedor"
            st.session_state.sales_id = seller["id"]
            st.session_state.user_name = seller["name"].upper()
            st.session_state.page = "home"
            st.rerun()
        st.error("Login ou senha inválidos")
    st.info("Admin: admin / admin123   |   Vendedor: vendedor@tigrao.com / 123")


def filtered_orders(db):
    orders = db["orders"]
    if st.session_state.get("role") == "vendedor":
        orders = [o for o in orders if o.get("salespersonId") == st.session_state.get("sales_id")]
    return orders


def pedidos_menu(db):
    # Mantido apenas por compatibilidade; agora o botão PEDIDOS abre direto a lista.
    set_page("orders")


def clientes_menu(db):
    st.markdown('<div class="page-title">Clientes</div>', unsafe_allow_html=True)
    buttons = [("CADASTRAR\nCLIENTE", "clients"), ("CONSULTAR\nCLIENTES", "clients"), ("IMPORTAR\nCLIENTES", "import_clientes"), ("VOLTAR", "home")]
    grid_buttons(buttons, "clientes_menu")


def consultas_menu(db):
    st.markdown('<div class="page-title">Consultas</div>', unsafe_allow_html=True)
    buttons = [
        ("PREÇOS E ESTOQUES", "products"),
        ("PEDIDOS FATURADOS", "pedidos_faturados"),
        ("VENDAS POR CLIENTE", "vendas_cliente"),
        ("COMISSÃO", "comissao"),
        ("CONTAS A RECEBER", "contas_receber"),
        ("VENDAS POR PRODUTO", "vendas_produto"),
        ("OBJETIVOS\nPOR FORNECEDOR", "objetivos_fornecedor"),
        ("OBJETIVOS\nPOR PRODUTO", "objetivos_produto"),
        ("CORTES", "cortes"),
        ("ITINERÁRIO", "itinerario"),
        ("ENTREGA FUTURA", "entrega_futura"),
        ("DEVOLUÇÕES", "devolucoes"),
        ("VENDAS POR DIVISÃO", "vendas_divisao"),
        ("VOLTAR", "home"),
    ]
    grid_buttons(buttons, "consultas_menu")


def config_menu(db):
    st.markdown('<div class="page-title">Configurações</div>', unsafe_allow_html=True)
    buttons = [("VENDEDORES", "vendedores"), ("IMPORTAR\nPRODUTOS", "import_produtos"), ("IMPORTAR\nCLIENTES", "import_clientes"), ("BACKUP", "backup"), ("VOLTAR", "home")]
    grid_buttons(buttons, "config_menu")


def new_order(db):
    st.markdown('<div class="page-title">Novo Pedido</div>', unsafe_allow_html=True)
    clients = db["clients"]
    products = db["products"]
    sales = db["salespeople"]
    with st.form("order_form"):
        c = st.selectbox("Cliente", clients, format_func=lambda x: f"{x['name']} — {x['document']}", key="pedido_cliente")
        if st.session_state.get("role") == "admin":
            s = st.selectbox("Vendedor", [x for x in sales if x.get("active")], format_func=lambda x: x["name"], key="pedido_vendedor")
        else:
            s = next(x for x in sales if x["id"] == st.session_state.sales_id)
        st.write("Produtos")
        items = []
        for i in range(1, 7):
            col1, col2 = st.columns([3, 1])
            p = col1.selectbox(f"Produto {i}", [None] + products, format_func=lambda x: "Selecione" if x is None else f"{x['sku']} - {x['name']} ({money(x['price'])})", key=f"p{i}")
            q = col2.number_input("Qtd", min_value=0, step=1, key=f"q{i}")
            if p and q > 0:
                items.append({"productId": p["id"], "productName": p["name"], "quantity": int(q), "price": float(p["price"]), "commissionRate": p.get("commissionRate", db["commissionRate"])})
        salvar = st.form_submit_button("SALVAR PEDIDO")
    if salvar:
        if not items:
            st.error("Adicione pelo menos 1 produto")
        else:
            total = sum(it["quantity"] * it["price"] for it in items)
            rate = float(db["commissionRate"])
            maxnum = max([o["orderNumber"] for o in db["orders"]], default=-1) + 1
            db["orders"].insert(0, {"id": uid("ord"), "orderNumber": maxnum, "date": datetime.now().isoformat(timespec="seconds"), "salespersonId": s["id"], "salespersonName": s["name"], "clientId": c["id"], "clientName": c["name"], "items": items, "total": total, "commissionRate": rate, "commissionAmount": round(total * rate / 100, 2), "status": "Pendente"})
            for it in items:
                for p in db["products"]:
                    if p["id"] == it["productId"]:
                        p["stock"] = max(0, int(p.get("stock", 0)) - it["quantity"])
            save_db(db)
            st.success("Pedido salvo com sucesso")
            st.session_state.page = "orders"
            st.rerun()
    back_button("pedidos_menu")


def gerar_pdf_pedido(db, pedido):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.2 * cm, leftMargin=1.2 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    elems = []
    cliente = next((c for c in db.get("clients", []) if c.get("id") == pedido.get("clientId")), {})
    elems.append(Paragraph("<b>TIGRÃO DISTRIBUIDORA</b>", styles["Title"]))
    elems.append(Paragraph(f"Pedido #{pedido.get('orderNumber','')}", styles["Heading2"]))
    elems.append(Spacer(1, 8))
    info = [["Cliente", pedido.get("clientName", "")], ["Documento", cliente.get("document", "")], ["Telefone", cliente.get("phone", "")], ["Cidade", f"{cliente.get('city','')} / {cliente.get('state','')}"], ["Vendedor", pedido.get("salespersonName", "")], ["Data", str(pedido.get("date", "")).replace("T", " ")], ["Status", pedido.get("status", "")]]
    t = Table(info, colWidths=[3.2 * cm, 13 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("PADDING", (0, 0), (-1, -1), 6)]))
    elems.append(t)
    elems.append(Spacer(1, 14))
    dados = [["Produto", "Qtd", "Preço", "Total"]]
    for it in pedido.get("items", []):
        qtd = float(it.get("quantity", 0)); preco = float(it.get("price", 0)); total = qtd * preco
        dados.append([it.get("productName", ""), str(int(qtd) if qtd.is_integer() else qtd), money(preco), money(total)])
    dados.append(["", "", "TOTAL", money(pedido.get("total", 0))])
    tab = Table(dados, colWidths=[9.2 * cm, 2 * cm, 2.7 * cm, 2.7 * cm])
    tab.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")), ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"), ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fff7ed")), ("PADDING", (0, 0), (-1, -1), 6)]))
    elems.append(tab)
    elems.append(Spacer(1, 18))
    elems.append(Paragraph("Obrigado pela preferência.", styles["Normal"]))
    doc.build(elems)
    buffer.seek(0)
    return buffer.getvalue()


def status_envio_pedido(o):
    status = str(o.get("status", "Pendente")).strip().lower()
    if status == "pendente":
        return "Não enviado"
    return "Enviado"


def orders_page(db, only_status=None, title="Pedidos"):
    st.markdown(
        """
        <style>
        .orders-title {
            text-align: center;
            font-size: 38px;
            font-weight: 400;
            margin: 4px 0 8px;
            color: #222;
        }
        .orders-filter div[data-baseweb="select"] > div {
            background: #e5e7eb !important;
            border: 0 !important;
            border-radius: 0 !important;
            min-height: 54px !important;
            font-size: 18px !important;
        }
        .pedido-linha {
            position: relative;
            min-height: 150px;
            padding: 28px 145px 22px 22px;
            border-bottom: 1px solid #d4d4d4;
            background: #fff;
            color: #222;
        }
        .pedido-cliente,
        .pedido-valor,
        .pedido-data {
            font-size: 17px;
            line-height: 1.7;
        }
        .pedido-numero {
            position: absolute;
            top: 26px;
            right: 18px;
            font-size: 17px;
        }
        .pedido-status {
            position: absolute;
            top: 68px;
            right: 18px;
            min-width: 105px;
            padding: 8px 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
        }
        .pedido-status-pendente {
            background: #ffb800;
            color: #111;
        }
        .pedido-status-enviado {
            background: #41b94e;
            color: #fff;
        }
        .novo-pedido-area {
            background: #e5e7eb;
            padding: 14px 20px;
            margin-top: 0;
        }
        .st-key-btn_novo_pedido_lista button {
            display: block !important;
            width: 44% !important;
            margin: auto !important;
            min-height: 58px !important;
            border-radius: 14px !important;
            background: #c9c9c9 !important;
            color: #111 !important;
            font-size: 18px !important;
            border: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="orders-title">{title}</div>', unsafe_allow_html=True)

    if only_status:
        filtro = "Todos"
    else:
        st.markdown('<div class="orders-filter">', unsafe_allow_html=True)
        filtro = st.selectbox(
            "Filtro",
            ["Todos", "Enviados", "Não Enviado"],
            index=2,
            key="filtro_envio_pedidos",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    lista = sorted(
        filtered_orders(db),
        key=lambda x: int(x.get("orderNumber", 0)),
        reverse=True,
    )

    if only_status:
        lista = [o for o in lista if o.get("status") == only_status]
    elif filtro == "Não Enviado":
        lista = [o for o in lista if str(o.get("status", "")).strip().lower() == "pendente"]
    elif filtro == "Enviados":
        lista = [o for o in lista if str(o.get("status", "")).strip().lower() != "pendente"]

    if not lista:
        st.info("Nenhum pedido encontrado.")

    for o in lista:
        status_original = str(o.get("status", "Pendente")).strip()
        nao_enviado = status_original.lower() == "pendente"
        status_texto = "Pendente" if nao_enviado else "Enviado"
        status_classe = "pedido-status-pendente" if nao_enviado else "pedido-status-enviado"

        try:
            data_pedido = datetime.fromisoformat(str(o.get("date", ""))).strftime("%d/%m/%Y %H:%M")
        except Exception:
            data_pedido = str(o.get("date", "")).replace("T", " ")[:16]

        st.markdown(
            f"""
            <div class="pedido-linha">
                <div class="pedido-cliente">Cliente:&nbsp; {o.get("clientName", "").upper()}</div>
                <div class="pedido-valor">Valor:&nbsp; {money(o.get("total", 0))}</div>
                <div class="pedido-data">Data:&nbsp; {data_pedido}</div>
                <div class="pedido-numero">Pedido:&nbsp; {o.get("orderNumber", "")}</div>
                <div class="pedido-status {status_classe}">{status_texto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"ABRIR PEDIDO {o.get('orderNumber', '')}", expanded=False):
            st.write("Cliente:", o.get("clientName", ""))
            st.write("Vendedor:", o.get("salespersonName", ""))
            st.write("Data:", data_pedido)
            st.write("Status:", status_original)
            st.write("Valor:", money(o.get("total", 0)))
            st.dataframe(pd.DataFrame(o.get("items", [])), use_container_width=True, hide_index=True)
            st.write("Comissão:", money(o.get("commissionAmount", 0)))

            if st.button("GERAR PDF DO PEDIDO", key="gerar_pdf_" + o["id"]):
                st.session_state["pdf_pedido_aberto"] = o["id"]
                st.rerun()

            if st.session_state.get("pdf_pedido_aberto") == o["id"]:
                pdf = gerar_pdf_pedido(db, o)
                st.download_button(
                    "BAIXAR / COMPARTILHAR PDF",
                    data=pdf,
                    file_name=f"pedido_{o['orderNumber']}_tigrao.pdf",
                    mime="application/pdf",
                    key="pdf_" + o["id"],
                )

            if st.session_state.get("role") == "admin":
                ns = st.selectbox(
                    "Status",
                    STATUS,
                    index=STATUS.index(status_original) if status_original in STATUS else 0,
                    key="st" + o["id"],
                )
                col1, col2 = st.columns(2)
                if col1.button("ATUALIZAR", key="up" + o["id"]):
                    o["status"] = ns
                    save_db(db)
                    st.rerun()
                if col2.button("EXCLUIR PEDIDO", key="del" + o["id"]):
                    db["orders"] = [x for x in db["orders"] if x["id"] != o["id"]]
                    save_db(db)
                    st.rerun()

    st.markdown('<div class="novo-pedido-area">', unsafe_allow_html=True)
    if st.button("NOVO PEDIDO", key="btn_novo_pedido_lista"):
        set_page("new_order")
    st.markdown("</div>", unsafe_allow_html=True)

    back_button("consultas_menu" if title != "Pedidos" else "home")

def clients_page(db):
    st.markdown('<div class="page-title">Clientes</div>', unsafe_allow_html=True)
    with st.expander("Cadastrar cliente"):
        with st.form("cli"):
            n = st.text_input("Nome", key="cliente_nome")
            doc = st.text_input("CPF/CNPJ", key="cliente_doc")
            em = st.text_input("E-mail", key="cliente_email")
            ph = st.text_input("Telefone", key="cliente_tel")
            city = st.text_input("Cidade", key="cliente_cidade")
            uf = st.text_input("Estado", key="cliente_estado")
            if st.form_submit_button("SALVAR CLIENTE") and n:
                db["clients"].insert(0, {"id": uid("cli"), "name": n, "document": doc, "email": em, "phone": ph, "city": city, "state": uf})
                save_db(db)
                st.rerun()
    busca = st.text_input("Pesquisar por nome, documento ou cidade", key="busca_clientes")
    for c in db["clients"]:
        if busca and busca.lower() not in json.dumps(c, ensure_ascii=False).lower():
            continue
        st.markdown(f'<div class="card"><b>{c["name"]}</b><br>{c["document"]}<br>{c["phone"]} • {c["city"]}/{c["state"]}</div>', unsafe_allow_html=True)
    back_button("clientes_menu")


def products_page(db):
    st.markdown('<div class="page-title">Preços e Estoques</div>', unsafe_allow_html=True)
    if st.session_state.get("role") == "admin":
        with st.expander("Cadastrar produto"):
            with st.form("prod"):
                sku = st.text_input("Código/SKU", key="prod_sku")
                n = st.text_input("Nome", key="prod_nome")
                cat = st.text_input("Categoria", key="prod_categoria")
                price = st.number_input("Preço", min_value=0.0, step=.01, key="prod_preco")
                stock = st.number_input("Estoque", min_value=0, step=1, key="prod_estoque")
                cr = st.number_input("Comissão %", min_value=0.0, value=float(db["commissionRate"]), step=.5, key="prod_comissao")
                if st.form_submit_button("SALVAR PRODUTO") and n:
                    db["products"].insert(0, {"id": uid("prod"), "name": n, "sku": sku, "price": price, "stock": stock, "category": cat, "commissionRate": cr})
                    save_db(db)
                    st.rerun()
    busca = st.text_input("Pesquisar produto por código, nome ou categoria", key="busca_produtos")
    busca_norm = normalizar(busca)
    for p in db["products"]:
        texto = normalizar(json.dumps(p, ensure_ascii=False))
        if busca_norm and busca_norm not in texto:
            continue
        st.markdown(f'<div class="card"><b>{p["sku"]} — {p["name"]}</b><br>{p["category"]}<br><h3>{money(p["price"])}</h3>Estoque: {p["stock"]} • Comissão: {p.get("commissionRate", db["commissionRate"])}%</div>', unsafe_allow_html=True)
    back_button("consultas_menu")


def _col(df, names):
    lower = {str(c).strip().lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def _str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()


def _float(v, default=0.0):
    try:
        if pd.isna(v):
            return default
        if isinstance(v, str):
            v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(v)
    except Exception:
        return default


def _int(v, default=0):
    try:
        if pd.isna(v):
            return default
        if isinstance(v, str):
            v = v.replace(".", "").replace(",", ".").strip()
        return int(float(v))
    except Exception:
        return default


def importar_produtos_excel(db, arquivo):
    df = pd.read_excel(arquivo)
    c_sku = _col(df, ["sku", "codigo", "código", "cod", "referencia", "referência"])
    c_nome = _col(df, ["nome", "produto", "descricao", "descrição", "name"])
    c_cat = _col(df, ["categoria", "category", "grupo", "fornecedor"])
    c_preco = _col(df, ["preco", "preço", "valor", "price", "venda"])
    c_estoque = _col(df, ["estoque", "stock", "quantidade", "qtd"])
    c_com = _col(df, ["comissao", "comissão", "commissionRate", "comissao %", "comissão %"])
    if not c_nome:
        raise ValueError("A planilha de produtos precisa ter uma coluna Nome ou Produto.")
    existentes = {_str(p.get("sku")).lower(): p for p in db["products"] if _str(p.get("sku"))}
    adicionados = 0
    atualizados = 0
    for _, r in df.iterrows():
        nome = _str(r.get(c_nome))
        if not nome:
            continue
        sku = _str(r.get(c_sku)) if c_sku else ""
        if not sku:
            sku = f"PROD-{len(db['products']) + adicionados + 1}"
        item = {"id": uid("prod"), "name": nome, "sku": sku, "price": _float(r.get(c_preco), 0), "stock": _int(r.get(c_estoque), 0), "category": _str(r.get(c_cat)) if c_cat else "", "commissionRate": _float(r.get(c_com), float(db.get("commissionRate", 7)))}
        k = sku.lower()
        if k in existentes:
            existentes[k].update({x: item[x] for x in ["name", "sku", "price", "stock", "category", "commissionRate"]})
            atualizados += 1
        else:
            db["products"].insert(0, item)
            existentes[k] = item
            adicionados += 1
    return adicionados, atualizados


def importar_clientes_excel(db, arquivo):
    df = pd.read_excel(arquivo)
    c_nome = _col(df, ["nome", "cliente", "razao social", "razão social", "name"])
    c_doc = _col(df, ["cpf/cnpj", "cnpj", "cpf", "documento", "document"])
    c_email = _col(df, ["email", "e-mail"])
    c_tel = _col(df, ["telefone", "celular", "phone", "tel"])
    c_city = _col(df, ["cidade", "city", "municipio", "município"])
    c_uf = _col(df, ["estado", "uf", "state"])
    if not c_nome:
        raise ValueError("A planilha de clientes precisa ter uma coluna Nome ou Cliente.")
    existentes = {_str(c.get("document")).lower(): c for c in db["clients"] if _str(c.get("document"))}
    adicionados = 0
    atualizados = 0
    for _, r in df.iterrows():
        nome = _str(r.get(c_nome))
        if not nome:
            continue
        doc = _str(r.get(c_doc)) if c_doc else ""
        item = {"id": uid("cli"), "name": nome, "document": doc, "email": _str(r.get(c_email)) if c_email else "", "phone": _str(r.get(c_tel)) if c_tel else "", "city": _str(r.get(c_city)) if c_city else "", "state": _str(r.get(c_uf)) if c_uf else ""}
        k = doc.lower()
        if k and k in existentes:
            existentes[k].update({x: item[x] for x in ["name", "document", "email", "phone", "city", "state"]})
            atualizados += 1
        else:
            db["clients"].insert(0, item)
            if k:
                existentes[k] = item
            adicionados += 1
    return adicionados, atualizados


@st.cache_data(show_spinner=False)
def modelo_excel_download():
    modelo = BytesIO()
    with pd.ExcelWriter(modelo, engine="openpyxl") as writer:
        pd.DataFrame(columns=["codigo", "nome", "categoria", "preco", "estoque", "comissao"]).to_excel(writer, index=False, sheet_name="produtos")
        pd.DataFrame(columns=["nome", "cpf/cnpj", "email", "telefone", "cidade", "estado"]).to_excel(writer, index=False, sheet_name="clientes")
    return modelo.getvalue()


def import_produtos_page(db):
    st.markdown('<div class="page-title">Importar Produtos</div>', unsafe_allow_html=True)
    st.download_button("BAIXAR MODELO EXCEL", data=modelo_excel_download(), file_name="modelo_importacao_tigrao.xlsx", key="download_modelo_prod")
    up_prod = st.file_uploader("Importar produtos Excel", type=["xlsx", "xls"], key="upload_produtos_excel_page")
    if up_prod and st.button("CADASTRAR PRODUTOS DA PLANILHA", key="btn_importar_produtos_excel_page"):
        try:
            add, upd = importar_produtos_excel(db, up_prod)
            save_db(db)
            st.success(f"Produtos importados: {add} novos e {upd} atualizados.")
        except Exception as e:
            st.error(str(e))
    back_button("config_menu")


def import_clientes_page(db):
    st.markdown('<div class="page-title">Importar Clientes</div>', unsafe_allow_html=True)
    st.download_button("BAIXAR MODELO EXCEL", data=modelo_excel_download(), file_name="modelo_importacao_tigrao.xlsx", key="download_modelo_cli")
    up_cli = st.file_uploader("Importar clientes Excel", type=["xlsx", "xls"], key="upload_clientes_excel_page")
    if up_cli and st.button("CADASTRAR CLIENTES DA PLANILHA", key="btn_importar_clientes_excel_page"):
        try:
            add, upd = importar_clientes_excel(db, up_cli)
            save_db(db)
            st.success(f"Clientes importados: {add} novos e {upd} atualizados.")
        except Exception as e:
            st.error(str(e))
    back_button("config_menu")


def backup_page(db):
    st.markdown('<div class="page-title">Backup</div>', unsafe_allow_html=True)
    st.download_button("BAIXAR BACKUP JSON", data=json.dumps(db, ensure_ascii=False, indent=2).encode("utf-8"), file_name="tigrao_backup.json", key="download_backup_json")
    if st.button("GERAR EXCEL PARA EXPORTAÇÃO", key="btn_gerar_excel_exportacao"):
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            for k, v in {"produtos": pd.DataFrame(db["products"]), "clientes": pd.DataFrame(db["clients"]), "vendedores": pd.DataFrame(db["salespeople"]), "pedidos": pd.DataFrame(db["orders"])}.items():
                v.to_excel(writer, index=False, sheet_name=k)
        st.session_state["excel_exportacao"] = out.getvalue()
    if st.session_state.get("excel_exportacao"):
        st.download_button("EXPORTAR EXCEL", data=st.session_state["excel_exportacao"], file_name="tigrao_export.xlsx", key="download_excel")
    up = st.file_uploader("Importar backup JSON", type=["json"], key="upload_backup_json")
    if up and st.button("IMPORTAR AGORA", key="btn_importar_backup"):
        new = json.loads(up.read().decode("utf-8"))
        save_db(new)
        st.success("Importado")
        st.rerun()
    col1, col2 = st.columns(2)
    if col1.button("RESTAURAR EXEMPLO", key="btn_restaurar_exemplo"):
        save_db(seed())
        st.rerun()
    if col2.button("LIMPAR BANCO", key="btn_limpar_banco"):
        save_db({"app": "Tigrão Distribuidora", "systemName": "TIGRÃO", "commissionRate": 7, "products": [], "clients": [], "salespeople": INITIAL_SALES[:1], "orders": []})
        st.rerun()
    back_button("config_menu")


def vendedores_page(db):
    st.markdown('<div class="page-title">Vendedores</div>', unsafe_allow_html=True)
    with st.expander("Cadastrar vendedor"):
        with st.form("sales"):
            n = st.text_input("Nome", key="vend_nome")
            em = st.text_input("E-mail", key="vend_email")
            cpf = st.text_input("CPF", key="vend_cpf")
            ph = st.text_input("Telefone", key="vend_tel")
            pw = st.text_input("Senha", value="123", key="vend_senha")
            if st.form_submit_button("SALVAR VENDEDOR") and n:
                db["salespeople"].append({"id": uid("sales"), "name": n, "email": em, "active": True, "cpf": cpf, "phone": ph, "address": "", "password": pw, "passwordIsTemporary": False})
                save_db(db)
                st.rerun()
    for s in db["salespeople"]:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{s['name']}** — {s['email']} — {'Ativo' if s.get('active') else 'Inativo'}")
        if col2.button("ATIVAR\nINATIVAR", key="a" + s["id"]):
            s["active"] = not s.get("active")
            save_db(db)
            st.rerun()
    back_button("config_menu")


def simple_report(db, title, text="Tela em desenvolvimento."):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.info(text)
    back_button("consultas_menu")


def comissao_page(db):
    st.markdown('<div class="page-title">Comissão</div>', unsafe_allow_html=True)
    orders = filtered_orders(db)
    total_com = sum(float(o.get("commissionAmount", 0)) for o in orders)
    st.markdown(f'<div class="metric">Comissão total<br><b>{money(total_com)}</b></div>', unsafe_allow_html=True)
    for o in orders:
        st.markdown(f'<div class="card"><b>Pedido #{o.get("orderNumber")}</b><br>{o.get("clientName")}<br>{money(o.get("commissionAmount", 0))}</div>', unsafe_allow_html=True)
    back_button("consultas_menu")


def vendas_produto_page(db):
    st.markdown('<div class="page-title">Vendas por Produto</div>', unsafe_allow_html=True)
    resumo = {}
    for o in filtered_orders(db):
        for it in o.get("items", []):
            nome = it.get("productName", "")
            resumo.setdefault(nome, {"qtd": 0, "total": 0})
            resumo[nome]["qtd"] += int(it.get("quantity", 0))
            resumo[nome]["total"] += float(it.get("quantity", 0)) * float(it.get("price", 0))
    for nome, r in resumo.items():
        st.markdown(f'<div class="card"><b>{nome}</b><br>Qtd: {r["qtd"]}<br>Total: {money(r["total"])}</div>', unsafe_allow_html=True)
    back_button("consultas_menu")


def vendas_cliente_page(db):
    st.markdown('<div class="page-title">Vendas por Cliente</div>', unsafe_allow_html=True)
    resumo = {}
    for o in filtered_orders(db):
        nome = o.get("clientName", "")
        resumo[nome] = resumo.get(nome, 0) + float(o.get("total", 0))
    for nome, total in resumo.items():
        st.markdown(f'<div class="card"><b>{nome}</b><br>Total: {money(total)}</div>', unsafe_allow_html=True)
    back_button("consultas_menu")


def treinamento_page(db):
    st.markdown('<div class="page-title">Treinamento</div>', unsafe_allow_html=True)
    st.info("Área para vídeos, manuais e orientações dos vendedores.")
    back_button("home")


def comunicacao_page(db):
    st.markdown('<div class="page-title">Comunicação</div>', unsafe_allow_html=True)
    st.info("Área para comunicados internos da distribuidora.")
    back_button("home")


css()
db = load_db()
if "auth" not in st.session_state:
    st.session_state.auth = False
if "page" not in st.session_state:
    st.session_state.page = "home"

if not st.session_state.auth:
    login(db)
    st.stop()

android_bar()

routes = {
    "home": home_page,
    "pedidos_menu": pedidos_menu,
    "clientes_menu": clientes_menu,
    "consultas_menu": consultas_menu,
    "config_menu": config_menu,
    "new_order": new_order,
    "orders": lambda d: orders_page(d, title="Pedidos"),
    "pedidos_faturados": lambda d: orders_page(d, only_status="Faturado", title="Pedidos Faturados"),
    "clients": clients_page,
    "products": products_page,
    "import_produtos": import_produtos_page,
    "import_clientes": import_clientes_page,
    "backup": backup_page,
    "vendedores": vendedores_page,
    "comissao": comissao_page,
    "vendas_produto": vendas_produto_page,
    "vendas_cliente": vendas_cliente_page,
    "contas_receber": lambda d: simple_report(d, "Contas a Receber", "Em breve: títulos em aberto e vencimentos."),
    "objetivos_fornecedor": lambda d: simple_report(d, "Objetivos por Fornecedor", "Em breve: metas por fornecedor."),
    "objetivos_produto": lambda d: simple_report(d, "Objetivos por Produto", "Em breve: metas por produto."),
    "cortes": lambda d: simple_report(d, "Cortes", "Em breve: produtos cortados/faltantes."),
    "itinerario": lambda d: simple_report(d, "Itinerário", "Em breve: rota de visitas e entregas."),
    "entrega_futura": lambda d: simple_report(d, "Entrega Futura", "Em breve: pedidos com entrega futura."),
    "devolucoes": lambda d: simple_report(d, "Devoluções", "Em breve: controle de devoluções."),
    "vendas_divisao": lambda d: simple_report(d, "Vendas por Divisão", "Em breve: relatório por divisão."),
    "treinamento": treinamento_page,
    "comunicacao": comunicacao_page,
}

page = st.session_state.get("page", "home")
routes.get(page, home_page)(db)
