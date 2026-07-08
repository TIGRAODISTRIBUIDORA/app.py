import base64
import json
import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Tigrão Distribuidora",
    page_icon="🐯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_DIR = "dados_tigrao"
DB_FILE = os.path.join(DATA_DIR, "banco.json")
os.makedirs(DATA_DIR, exist_ok=True)

STATUS = ["Pendente", "Faturado", "Entregue", "Cancelado", "Com inconsistência"]

INITIAL_PRODUCTS = [
    {"id": "prod-1", "name": "Cerveja Heineken Long Neck 330ml", "sku": "HEI-001", "price": 8.50, "stock": 120, "category": "Cervejas", "supplier": "Heineken", "commissionRate": 3},
    {"id": "prod-2", "name": "Cigarro Rothmans Red Box", "sku": "ROT-002", "price": 9.75, "stock": 450, "category": "Tabacaria", "supplier": "Souza Cruz", "commissionRate": 5},
    {"id": "prod-3", "name": "Refrigerante Coca-Cola 2L", "sku": "COC-003", "price": 11.90, "stock": 250, "category": "Refrigerantes", "supplier": "Coca-Cola", "commissionRate": 4},
    {"id": "prod-4", "name": "Energético Monster Energy 473ml", "sku": "MON-004", "price": 10.50, "stock": 180, "category": "Energéticos", "supplier": "Monster", "commissionRate": 4},
    {"id": "prod-5", "name": "Água Mineral Sem Gás 500ml", "sku": "AGU-005", "price": 2.50, "stock": 600, "category": "Águas", "supplier": "Fornecedor Geral", "commissionRate": 2},
    {"id": "prod-6", "name": "Cerveja Amstel Lata 350ml", "sku": "AMS-006", "price": 4.20, "stock": 320, "category": "Cervejas", "supplier": "Heineken", "commissionRate": 3},
    {"id": "prod-7", "name": "Vodka Smirnoff 998ml", "sku": "SMI-007", "price": 39.90, "stock": 65, "category": "Destilados", "supplier": "Diageo", "commissionRate": 4},
    {"id": "prod-8", "name": "Whisky Johnnie Walker Red Label 1L", "sku": "JWL-008", "price": 99.90, "stock": 40, "category": "Destilados", "supplier": "Diageo", "commissionRate": 4},
]

INITIAL_CLIENTS = [
    {"id": "cli-1", "code": "001", "name": "nelson das galaxie", "document": "123.456.789-00", "email": "nelson@galaxie.com", "phone": "(11) 98888-7777", "city": "São Paulo", "state": "SP", "address": "", "district": "", "zip": ""},
    {"id": "cli-2", "code": "002", "name": "Distribuidora Silva & Silva", "document": "98.765.432/0001-11", "email": "silva@distribuidora.com", "phone": "(11) 3245-8899", "city": "Campinas", "state": "SP", "address": "", "district": "", "zip": ""},
    {"id": "cli-3", "code": "003", "name": "Mercadinho do Bairro Ltda", "document": "45.123.789/0001-44", "email": "contato@mercadinhobairro.com", "phone": "(21) 97777-6666", "city": "Rio de Janeiro", "state": "RJ", "address": "", "district": "", "zip": ""},
    {"id": "cli-4", "code": "004", "name": "Adega Central", "document": "55.666.777/0001-88", "email": "adega.central@outlook.com", "phone": "(19) 99122-3344", "city": "Piracicaba", "state": "SP", "address": "", "district": "", "zip": ""},
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
    return {
        "app": "Tigrão Distribuidora",
        "systemName": "TIGRÃO",
        "commissionRate": 7,
        "products": INITIAL_PRODUCTS,
        "clients": INITIAL_CLIENTS,
        "salespeople": INITIAL_SALES,
        "orders": INITIAL_ORDERS,
        "deleted_orders": [],
    }


def load_db():
    if not os.path.exists(DB_FILE):
        save_db(seed())
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def money(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def money_pdf(v):
    return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def uid(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def normalizar(txt):
    txt = str(txt or "").lower().strip()
    troca = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
    for a, b in troca.items():
        txt = txt.replace(a, b)
    return txt


def so_numeros(txt):
    return "".join(ch for ch in str(txt or "") if ch.isdigit())


def data_br(valor):
    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except Exception:
        return str(valor or "")[:10]


def vencimento_br(valor, prazo):
    try:
        dt = datetime.fromisoformat(str(valor))
        nums = so_numeros(prazo)
        dias = int(nums) if nums else 30
        return (dt + timedelta(days=dias)).strftime("%d/%m/%Y")
    except Exception:
        return ""


def status_card_style(status):
    status = str(status or "").lower()
    if "pendente" in status:
        return "background:#fef3c7;border:1px solid #fde68a;color:#92400e;"
    if "faturado" in status:
        return "background:#dbeafe;border:1px solid #93c5fd;color:#1e3a8a;"
    if "entregue" in status:
        return "background:#dcfce7;border:1px solid #86efac;color:#166534;"
    return "background:white;border:1px solid #eee;color:#171717;"


def proximo_codigo(lista, campo="code"):
    nums = []
    for item in lista:
        n = so_numeros(item.get(campo) or item.get("codigo") or "")
        if n:
            try:
                nums.append(int(n))
            except Exception:
                pass
    return f"{max(nums, default=0) + 1:03d}"


def proximo_pedido(orders):
    nums = []
    for o in orders:
        try:
            nums.append(int(o.get("orderNumber", 0)))
        except Exception:
            pass
    return max(nums, default=0) + 1


def comeca_com(texto, busca):
    busca = normalizar(busca)
    texto = normalizar(texto)
    if not busca:
        return True
    busca_num = so_numeros(busca)
    texto_num = so_numeros(texto)
    if busca_num and busca_num in texto_num:
        return True
    partes = texto.replace("-", " ").replace("/", " ").replace(".", " ").replace(",", " ").replace("&", " ").split()
    return any(p.startswith(busca) for p in partes)


def combina_inicio(campos, busca):
    if not normalizar(busca):
        return True
    return any(comeca_com(campo, busca) for campo in campos)


def codigo_cliente(c):
    cod = c.get("code") or c.get("codigo") or c.get("id", "").replace("cli-", "")
    n = so_numeros(cod)
    return f"{int(n):03d}" if n else cod


def campos_cliente(c):
    return [codigo_cliente(c), c.get("name", ""), c.get("document", "")]


def campos_produto(p):
    return [p.get("sku", ""), p.get("code", ""), p.get("barcode", ""), p.get("name", "")]


def cliente_por_id(db, client_id):
    return next((c for c in db.get("clients", []) if c.get("id") == client_id), {})


def cliente_duplicado(db, documento):
    doc = so_numeros(documento)
    return bool(doc and any(so_numeros(c.get("document", "")) == doc for c in db.get("clients", [])))


def produto_duplicado(db, nome, codigo=""):
    nome_norm = normalizar(nome)
    codigo_norm = normalizar(codigo)
    for p in db.get("products", []):
        if nome_norm and normalizar(p.get("name", "")) == nome_norm:
            return True
        if codigo_norm and normalizar(p.get("sku", "") or p.get("code", "")) == codigo_norm:
            return True
    return False


def buscar_cnpj_internet(cnpj):
    cnpj_limpo = so_numeros(cnpj)
    if len(cnpj_limpo) != 14:
        return None, "CNPJ inválido. Digite 14 números."
    try:
        r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
        if r.status_code != 200:
            return None, "CNPJ não encontrado ou serviço indisponível."
        d = r.json()
        telefone = d.get("ddd_telefone_1") or d.get("telefone") or ""
        return {
            "document": cnpj_limpo,
            "name": d.get("nome_fantasia") or d.get("razao_social") or "",
            "email": d.get("email") or "",
            "phone": telefone,
            "city": d.get("municipio") or "",
            "state": d.get("uf") or "",
            "address": d.get("logradouro") or "",
            "district": d.get("bairro") or "",
            "zip": d.get("cep") or "",
        }, None
    except Exception:
        return None, "Erro ao buscar CNPJ. Verifique a internet e tente novamente."


def garantir_lixeira(db):
    if "deleted_orders" not in db:
        db["deleted_orders"] = []


def excluir_pedido_com_motivo(db, pedido_id, motivo):
    garantir_lixeira(db)
    pedido = next((o for o in db.get("orders", []) if o.get("id") == pedido_id), None)
    if not pedido:
        return False
    pedido_excluido = dict(pedido)
    pedido_excluido["deletedAt"] = datetime.now().isoformat(timespec="seconds")
    pedido_excluido["deletedBy"] = st.session_state.get("user_name", "")
    pedido_excluido["deleteReason"] = motivo
    pedido_excluido["originalStatus"] = pedido.get("status", "")
    db["deleted_orders"].insert(0, pedido_excluido)
    db["orders"] = [o for o in db.get("orders", []) if o.get("id") != pedido_id]
    save_db(db)
    return True


def draw_text(c, x, y, text, size=8, bold=False):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, str(text or ""))


def line(c, x1, y1, x2, y2, width=1):
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def gerar_pdf_pedido(o, cli):
    """Gera pedido em PDF no modelo romaneio/controle interno igual ao exemplo enviado."""
    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    w, h = A4

    left, right = 36, w - 36
    y = h - 42
    total_pedido = float(o.get("total", 0))
    pedido_num = f"{int(o.get('orderNumber', 0)):06d}"
    cliente_cod = codigo_cliente(cli) if cli else "00000"
    vendedor_nome = str(o.get("salespersonName", "")).upper()
    vendedor_cod = so_numeros(o.get("salespersonId", ""))[-3:] or "007"
    data_pedido = data_br(o.get("date", ""))
    prazo = o.get("paymentTerm", "BOLETO - 30 DD") or "BOLETO - 30 DD"
    vencimento = vencimento_br(o.get("date", ""), prazo)
    telefone = cli.get("phone", "") if cli else ""
    cidade = str(cli.get("city", "") if cli else "").upper()
    estado = str(cli.get("state", "") if cli else "").upper()
    cliente_nome = str(o.get("clientName", "") or (cli.get("name", "") if cli else "")).upper()
    fantasia = str(cli.get("fantasy", "") or cli.get("name", "") or o.get("clientName", "")).upper()
    endereco = str(cli.get("address", "") or "").upper()
    bairro = str(cli.get("district", "") or "").upper()
    cep = so_numeros(cli.get("zip", "") if cli else "")
    documento = so_numeros(cli.get("document", "") if cli else "")

    draw_text(c, 100, y, "TIGRAO DISTRIBUIDORA DE PRODUTOS NATURAL", 10, True)
    draw_text(c, 420, y, "Pagina:", 10)
    draw_text(c, 485, y, "1", 10)
    draw_text(c, 515, y, "/", 10)
    draw_text(c, 540, y, "1", 10)
    y -= 14
    draw_text(c, 100, y, "R JERÔNIMO DE LEMOS, 339 - VILA ISABEL.  RIO DE JANEIRO - RJ", 7)
    draw_text(c, 335, y, "21967208370", 7)
    y -= 8
    line(c, left, y, right, y, 1.1)
    y -= 14
    draw_text(c, 225, y, "***DOCUMENTO SEM VALOR FISCAL***", 9, True)
    y -= 18

    col_a, col_b, col_c = 40, 285, 430
    draw_text(c, col_a, y, "Romaneio:", 7, True); draw_text(c, col_a + 50, y, "00000", 7)
    draw_text(c, col_a + 95, y, "Repres.:", 7); draw_text(c, col_a + 135, y, vendedor_cod, 7); draw_text(c, col_a + 160, y, vendedor_nome[:18], 7)
    draw_text(c, col_b - 15, y, "Cel.:", 7)
    draw_text(c, col_c - 25, y, "Pedido:", 7); draw_text(c, col_c + 25, y, pedido_num, 7)
    draw_text(c, col_c + 80, y, "Data:", 7); draw_text(c, col_c + 113, y, data_pedido, 7)
    draw_text(c, col_c + 173, y, "Operação:", 7); draw_text(c, col_c + 223, y, "VENDA DE MERCADORIA", 7)
    y -= 15
    draw_text(c, col_a + 10, y, "Cliente:", 8); draw_text(c, col_a + 65, y, cliente_cod, 8); draw_text(c, col_a + 145, y, cliente_nome[:30], 8)
    draw_text(c, col_b + 10, y, "Cpf/Cnpj:", 8); draw_text(c, col_b + 65, y, documento, 8)
    draw_text(c, col_c + 135, y, "Insc.Est.:", 8); draw_text(c, col_c + 188, y, cli.get("state_registration", "") if cli else "", 8)
    y -= 15
    draw_text(c, col_a + 10, y, "Fantasia:", 8); draw_text(c, col_a + 65, y, fantasia[:28], 8)
    draw_text(c, col_b + 10, y, "Fone:", 8); draw_text(c, col_b + 65, y, telefone, 8)
    y -= 15
    draw_text(c, col_a + 10, y, "Endereço:", 8); draw_text(c, col_a + 65, y, endereco[:32], 8)
    draw_text(c, col_b + 10, y, "Bairro:", 8); draw_text(c, col_b + 65, y, bairro[:20], 8)
    draw_text(c, col_c + 95, y, "Complemento:", 8); draw_text(c, col_c + 170, y, "", 8)
    y -= 15
    draw_text(c, col_a + 10, y, "Cidade:", 8); draw_text(c, col_a + 65, y, cidade[:28], 8)
    draw_text(c, col_b + 10, y, "Estado:", 8); draw_text(c, col_b + 65, y, estado, 8)
    draw_text(c, col_b + 115, y, "Cep:", 8); draw_text(c, col_b + 150, y, cep, 8)
    y -= 10
    line(c, left, y, right, y, 1.1)
    y -= 17

    draw_text(c, col_a + 10, y, "Forma Pagto:", 8); draw_text(c, col_a + 85, y, prazo.upper(), 8)
    draw_text(c, col_c + 85, y, "Valor Parcela:", 8); draw_text(c, col_c + 165, y, money_pdf(total_pedido), 8)
    y -= 20
    draw_text(c, col_a + 10, y, "Vencimentos:", 8); draw_text(c, col_a + 85, y, vencimento, 8)
    y -= 12
    line(c, left, y, right, y, .8)
    y -= 12

    headers = [(40, "Quant"), (72, "Un"), (96, "Código"), (128, "Descrição do produto"), (280, "Qtd.Emb"), (340, "Apresentação"), (410, "Tabela"), (450, "Preço"), (493, "% Desc"), (537, "Prunit"), (574, "Total")]
    for x, txt in headers:
        draw_text(c, x, y, txt, 7, True)
    y -= 6
    line(c, left, y, right, y, .8)
    y -= 12

    c.setFont("Helvetica", 7)
    for it in o.get("items", []):
        qtd = float(it.get("quantity", 0))
        preco = float(it.get("price", 0))
        desc_txt = str(it.get("discount", "") or "0").replace("%", "") or "0"
        try:
            desc = float(desc_txt.replace(",", "."))
        except Exception:
            desc = 0.0
        pr_unit = preco * (1 - desc / 100)
        total = qtd * pr_unit
        prod_code = str(it.get("sku") or it.get("productCode") or it.get("productId", "")).replace("prod-", "")[-5:].zfill(5)
        nome = str(it.get("productName", "")).upper()[:32]
        if y < 275:
            break
        draw_text(c, 44, y, str(int(qtd)), 7)
        draw_text(c, 73, y, "UN", 7)
        draw_text(c, 98, y, prod_code, 7)
        draw_text(c, 128, y, nome, 7)
        draw_text(c, 415, y, "A", 7)
        draw_text(c, 450, y, money_pdf(preco), 7)
        draw_text(c, 495, y, money_pdf(desc), 7)
        draw_text(c, 538, y, money_pdf(pr_unit), 7)
        draw_text(c, 573, y, money_pdf(total), 7)
        y -= 13

    y -= 2
    line(c, left, y, right, y, 1.0)
    y -= 18
    draw_text(c, 45, y, "Obs:", 10, True)
    y -= 22
    draw_text(c, 405, y, "Total dos produtos:", 10, True); draw_text(c, 545, y, money_pdf(total_pedido), 10)
    y -= 20
    draw_text(c, 405, y, "Total do Pedido:", 10, True); draw_text(c, 545, y, money_pdf(total_pedido), 10)

    y = 250
    c.setDash(3, 2)
    line(c, left, y, 265, y, .8)
    line(c, 355, y, right, y, .8)
    c.setDash()
    draw_text(c, 280, y - 3, "CONTROLE INTERNO", 8)
    y -= 22
    draw_text(c, 38, y, "Romaneio:", 7, True); draw_text(c, 90, y, "00000", 7)
    draw_text(c, 135, y, "Pedido:", 7); draw_text(c, 180, y, pedido_num, 7)
    draw_text(c, 230, y, "Data:", 7); draw_text(c, 265, y, data_pedido, 7)
    draw_text(c, 330, y, "Representante:", 7); draw_text(c, 405, y, vendedor_cod, 7); draw_text(c, 430, y, vendedor_nome[:18], 7)
    draw_text(c, 500, y, "Operação:", 7); draw_text(c, 550, y, "VENDA DE MERCADORIA", 7)
    y -= 16
    draw_text(c, 55, y, "Cliente:", 7); draw_text(c, 105, y, cliente_cod, 7); draw_text(c, 150, y, cliente_nome[:30], 7)
    draw_text(c, 315, y, "Fantasia:", 7); draw_text(c, 370, y, fantasia[:25], 7)
    y -= 16
    draw_text(c, 55, y, "Cidade:", 7); draw_text(c, 105, y, cidade[:25], 7)
    draw_text(c, 250, y, "Estado:", 7); draw_text(c, 290, y, estado, 7)
    draw_text(c, 470, y, "Telefone:", 7); draw_text(c, 525, y, telefone, 7)
    y -= 14
    line(c, left, y, right, y, .8)
    y -= 20
    draw_text(c, 40, y, "Forma Pagto:", 8); draw_text(c, 105, y, prazo.upper(), 8)
    draw_text(c, 410, y, "Valor Parcela:", 8); draw_text(c, 495, y, money_pdf(total_pedido), 8)
    y -= 20
    draw_text(c, 40, y, "Vencimentos:", 8); draw_text(c, 105, y, vencimento, 8)
    y -= 10
    line(c, left, y, right, y, .8)
    y -= 18
    draw_text(c, 265, y, "Total dos produtos:", 10, True); draw_text(c, 390, y, money_pdf(total_pedido), 10)
    draw_text(c, 455, y, "Total do Pedido:", 10, True); draw_text(c, 555, y, money_pdf(total_pedido), 10)
    y -= 60
    line(c, 330, y, right - 5, y, .8)
    y -= 14
    draw_text(c, 390, y, cliente_nome[:35], 10)

    c.save()
    out.seek(0)
    return out.getvalue()


def pdf_preview(pdf_bytes, height=760):
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    components.html(
        f'''
        <iframe src="data:application/pdf;base64,{b64}#toolbar=0&navpanes=0&scrollbar=1" 
                width="100%" height="{height}" style="border:1px solid #eee;border-radius:14px;background:white;"></iframe>
        ''',
        height=height + 20,
    )


def link_whatsapp_pedido(o, cli):
    pedido_num = f"{int(o.get('orderNumber', 0)):06d}"
    texto = (
        f"Olá! Segue o pedido #{pedido_num} da Tigrão Distribuidora.\n"
        f"Cliente: {o.get('clientName', '')}\n"
        f"Total: {money(o.get('total', 0))}\n\n"
        "Vou anexar o PDF do pedido nesta conversa."
    )
    return "https://wa.me/?text=" + quote(texto)


def visualizar_pdf_area(o, cli):
    pdf = gerar_pdf_pedido(o, cli)
    c1, c2 = st.columns(2)
    c1.download_button("📄 Baixar PDF", data=pdf, file_name=f"pedido_{o.get('orderNumber','')}.pdf", mime="application/pdf", key="baixar_pdf_" + o["id"])
    c2.link_button("📲 Abrir WhatsApp", link_whatsapp_pedido(o, cli), use_container_width=True)
    st.caption("O WhatsApp abre com a mensagem pronta. Depois toque no clipe/anexo e envie o PDF baixado.")
    pdf_preview(pdf)


def css():
    st.markdown(
        '''<style>
 header, footer, [data-testid="stSidebar"] {display:none!important}
 .block-container{max-width:520px!important;padding:8px 18px 122px!important}.stApp{background:#fff!important;color:#171717}*{font-family:Inter,Arial,sans-serif}.top{background:#050505!important;color:#fff;border-radius:0 0 26px 26px!important;padding:20px;margin:-8px -18px 18px}.brand{display:flex;gap:12px;align-items:center}.logo{width:48px;height:48px;background:#f97316;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:28px}.title{font-size:26px;font-weight:900}.sub{color:#fb923c;font-size:11px;font-weight:900;letter-spacing:2px}.card{background:white;border:1px solid #eee;border-radius:24px;padding:16px;margin:10px 0;box-shadow:0 8px 24px rgba(0,0,0,.05)}.metric{background:#111;color:#fff;border-radius:22px;padding:12px 16px;min-height:78px}.metric b{font-size:20px}.stButton>button{min-height:52px!important;border-radius:18px!important;font-size:16px!important;font-weight:900!important}.stTextInput input,.stNumberInput input{background:#fff!important;color:#111!important;border:1.8px solid #fb923c!important;border-radius:16px!important;min-height:56px!important;font-size:17px!important}div[data-baseweb="select"]>div{background:#fff!important;border:1.8px solid #fb923c!important;border-radius:16px!important;min-height:56px!important;color:#111!important}.stSelectbox label,.stTextInput label,.stNumberInput label{font-size:18px!important;font-weight:800!important;color:#111!important}.st-key-btn_salvar_pedido_final button,.st-key-btn_buscar_cnpj_cliente button{background:#fb923c!important;color:#fff!important;border:0!important;width:100%!important}.st-key-btn_add_produto_pedido button{background:#fdba74!important;color:#111!important;border:0!important}div[class*="st-key-excluir_item_temp_"] button,div[class*="st-key-del_"] button{background:#ef4444!important;color:#fff!important;border:0!important;width:100%!important}div[class*="st-key-edit_"] button{background:#2563eb!important;color:#fff!important;border:0!important;width:100%!important}div[class*="st-key-a"] button{background:#f59e0b!important;color:#111!important;border:0!important;width:100%!important}[data-testid="stExpander"]{background:#fff!important;border:1px solid #eee!important;border-radius:18px!important;overflow:hidden!important;box-shadow:0 4px 18px rgba(0,0,0,.03)!important;margin-bottom:10px!important}[data-testid="stExpander"] details summary{background:#fff!important;color:#111!important;min-height:52px!important;padding:12px 14px!important;font-size:16px!important;font-weight:800!important}.st-key-bottom_nav{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:999999!important;background:#111!important;height:70px!important;padding:4px 2px calc(4px + env(safe-area-inset-bottom)) 2px!important;border-top:1px solid #222!important;overflow:hidden!important}.st-key-bottom_nav [data-testid="stHorizontalBlock"]{width:100vw!important;max-width:100vw!important;height:60px!important;margin:0 auto!important;display:grid!important;grid-template-columns:repeat(6,minmax(0,1fr))!important;gap:1px!important;align-items:center!important}.st-key-bottom_nav [data-testid="column"]{width:100%!important;min-width:0!important;max-width:none!important;padding:0!important;flex:none!important}.st-key-bottom_nav .stButton>button{width:100%!important;min-width:0!important;height:56px!important;min-height:56px!important;border:0!important;border-radius:14px!important;background:#111!important;color:#eee!important;font-size:9px!important;font-weight:900!important;padding:1px 0!important;line-height:1.05!important;white-space:pre-line!important;overflow:hidden!important;text-align:center!important}.st-key-bottom_nav .stButton>button[kind="primary"]{background:#f97316!important;color:#111!important}.stDownloadButton>button{background:#fb923c!important;color:#111!important;border:0!important;width:100%!important;border-radius:18px!important;font-weight:900!important;min-height:56px!important}.stLinkButton>a{background:#25D366!important;color:#111!important;border:0!important;width:100%!important;border-radius:18px!important;font-weight:900!important;min-height:56px!important;display:flex!important;align-items:center!important;justify-content:center!important;text-decoration:none!important}.pdf-box{background:white;border-radius:24px;padding:12px;border:1px solid #eee;box-shadow:0 8px 24px rgba(0,0,0,.05)}
 </style>''',
        unsafe_allow_html=True,
    )


def header(db):
    user = st.session_state.get("user_name", "")
    st.markdown(f'''<div class="top"><div class="brand"><div class="logo">🐯</div><div><div class="sub">DISTRIBUIDORA</div><div class="title">{db.get('systemName','TIGRÃO')}</div><div style="color:#aaa;font-size:12px">{user}</div></div></div></div>''', unsafe_allow_html=True)


def tigrinho_salvo():
    if not st.session_state.get("show_tigrinho_salvo"):
        return
    components.html('''<div id="tigrinho" style="position:fixed;top:28px;right:22px;z-index:999999999;background:white;border:3px solid #fb923c;border-radius:24px;padding:12px 16px;box-shadow:0 10px 35px rgba(0,0,0,.25);text-align:center;font-family:Arial,sans-serif;animation:entraSai 1.8s ease-in-out forwards;"><div style="font-size:58px;line-height:1">🐯</div><div style="font-size:15px;font-weight:900;color:#111;margin-top:4px">Pedido salvo!</div></div><style>@keyframes entraSai{0%{opacity:0;transform:translateY(-25px) scale(.8)}15%{opacity:1;transform:translateY(0) scale(1)}75%{opacity:1;transform:translateY(0) scale(1)}100%{opacity:0;transform:translateY(-25px) scale(.8)}}</style>''', height=0)
    st.session_state.show_tigrinho_salvo = False


def nav():
    tabs = [("dashboard", "🏠", "Início"), ("newOrder", "➕", "Novo"), ("orders", "📦", "Pedidos"), ("clients", "👥", "Cliente"), ("products", "🛒", "Prod."), ("more", "•••", "Mais")]
    with st.container(key="bottom_nav"):
        cols = st.columns(6)
        for col, (key, ico, label) in zip(cols, tabs):
            active = st.session_state.get("tab", "dashboard") == key
            if col.button(f"{ico}\n{label}", key=f"nav_{key}", type="primary" if active else "secondary"):
                st.session_state.tab = key
                st.rerun()


def login(db):
    st.markdown('<div style="height:28px"></div><div class="card login-card" style="text-align:center"><div style="font-size:64px">🐯</div><h1>TIGRÃO</h1><b>Acesso ao sistema</b></div>', unsafe_allow_html=True)
    with st.form("login"):
        usuario = st.text_input("Usuário / e-mail", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        ok = st.form_submit_button("Entrar")
    if ok:
        usuario_limpo = usuario.lower().strip()
        if usuario_limpo in ["admin", "administrador"] and senha == "admin123":
            st.session_state.auth = True
            st.session_state.role = "admin"
            st.session_state.sales_id = ""
            st.session_state.user_name = "Administrador"
            st.rerun()
        sellers = [s for s in db["salespeople"] if s.get("active")]
        seller = next((s for s in sellers if usuario_limpo in [s.get("email", "").lower(), s.get("name", "").lower()] and senha == s.get("password", "123")), None)
        if seller:
            st.session_state.auth = True
            st.session_state.role = "vendedor"
            st.session_state.sales_id = seller["id"]
            st.session_state.user_name = seller["name"]
            st.rerun()
        st.error("Login ou senha inválidos")


def filtered_orders(db):
    orders = db.get("orders", [])
    if st.session_state.get("role") == "vendedor":
        orders = [o for o in orders if o.get("salespersonId") == st.session_state.get("sales_id", "")]
    return orders


def dashboard(db):
    orders = filtered_orders(db)
    total = sum(float(o.get("total", 0)) for o in orders)
    com = sum(float(o.get("commissionAmount", 0)) for o in orders)
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="metric">Vendas<br><b>{money(total)}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric">Comissão<br><b>{money(com)}</b></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pedidos", len(orders))
    c2.metric("Clientes", len(db["clients"]))
    c3.metric("Produtos", len(db["products"]))
    st.subheader("Últimos pedidos")
    for o in sorted(orders, key=lambda x: x.get("orderNumber", 0), reverse=True)[:10]:
        st.markdown(f'<div class="card" style="{status_card_style(o.get("status", ""))}"><b>#{o.get("orderNumber", "")} — {o.get("clientName", "")}</b><br>{o.get("salespersonName", "")} • {o.get("status", "")}<br><h3>{money(o.get("total", 0))}</h3></div>', unsafe_allow_html=True)


def new_order(db):
    st.markdown("## ➕ Novo Pedido")
    clients = db["clients"]
    products = db["products"]
    sales = db["salespeople"]
    st.session_state.setdefault("pedido_itens_temp", [])
    st.session_state.setdefault("pedido_cliente_id", "")

    st.markdown("### Cliente")
    busca_cliente = st.text_input("Buscar cliente", key="pedido_busca_cliente_digitavel", placeholder="Digite nome, código ou CNPJ")
    clientes_encontrados = [c for c in clients if busca_cliente and combina_inicio(campos_cliente(c), busca_cliente)][:8]
    if busca_cliente and not clientes_encontrados:
        st.warning("Nenhum cliente encontrado.")
    for c_item in clientes_encontrados:
        if st.button(f'{codigo_cliente(c_item)} — {c_item["name"]}', key="selecionar_cliente_" + c_item["id"]):
            st.session_state.pedido_cliente_id = c_item["id"]
            st.rerun()
    c = next((cli for cli in clients if cli.get("id") == st.session_state.get("pedido_cliente_id", "")), None)
    if c:
        st.markdown(f'<div class="card"><b>Cliente selecionado</b><br>{codigo_cliente(c)} — {c["name"]}<br>{c.get("document", "")}</div>', unsafe_allow_html=True)
    else:
        st.info("Digite e selecione um cliente para continuar.")

    if st.session_state.role == "admin":
        s = st.selectbox("Vendedor", [x for x in sales if x.get("active")], format_func=lambda x: x["name"], key="pedido_vendedor")
    else:
        s = next(x for x in sales if x["id"] == st.session_state.sales_id)

    prazo_pagamento = st.text_input("Prazo de pagamento *", key="pedido_prazo_pagamento", placeholder="Obrigatório: Ex: BOLETO - 30 DD, À vista, 7 dias")

    st.markdown("### Produto")
    p = st.selectbox("Produto", [None] + products, format_func=lambda x: "Selecione o produto" if x is None else x["name"], key="pedido_produto_unico")
    if p:
        colq, cold, colb = st.columns([1, 1, 2])
        qtd = colq.number_input("Qtd", min_value=1, step=1, key="pedido_qtd_unica")
        desconto = cold.text_input("Desconto", key="pedido_desconto", placeholder="Ex: 5%")
        if colb.button("Adicionar ao pedido", key="btn_add_produto_pedido"):
            st.session_state.pedido_itens_temp.append({"productId": p["id"], "productName": p["name"], "productCode": p.get("sku", ""), "quantity": int(qtd), "price": float(p["price"]), "discount": desconto, "commissionRate": p.get("commissionRate", db["commissionRate"])})
            st.rerun()

    st.markdown("### Itens do pedido")
    if not st.session_state.pedido_itens_temp:
        st.info("Nenhum produto adicionado ainda.")
    else:
        total_temp = sum(it["quantity"] * it["price"] for it in st.session_state.pedido_itens_temp)
        for idx, it in enumerate(st.session_state.pedido_itens_temp):
            subtotal = it["quantity"] * it["price"]
            desc = it.get("discount", "")
            col1, col2 = st.columns([4, 1])
            col1.markdown(f'<div class="card"><b>{it["productName"]}</b><br>Qtd: {it["quantity"]} • Unitário: {money(it["price"])}<br>{"Desconto: " + desc + "<br>" if desc else ""}<b>Subtotal: {money(subtotal)}</b></div>', unsafe_allow_html=True)
            if col2.button("Excluir", key=f"excluir_item_temp_{idx}"):
                st.session_state.pedido_itens_temp.pop(idx)
                st.rerun()
        st.markdown(f'<div class="metric">Total do pedido<br><b>{money(total_temp)}</b></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("Salvar pedido", key="btn_salvar_pedido_final"):
        items = st.session_state.pedido_itens_temp
        if not c:
            st.error("Selecione um cliente.")
        elif not items:
            st.error("Adicione pelo menos 1 produto.")
        elif not prazo_pagamento.strip():
            st.error("Informe o prazo de pagamento antes de salvar o pedido.")
        else:
            total = sum(it["quantity"] * it["price"] for it in items)
            rate = float(db["commissionRate"])
            maxnum = proximo_pedido(db["orders"])
            db["orders"].insert(0, {"id": uid("ord"), "orderNumber": maxnum, "date": datetime.now().isoformat(timespec="seconds"), "salespersonId": s["id"], "salespersonName": s["name"], "clientId": c["id"], "clientName": c["name"], "items": items, "total": total, "discount": ", ".join([it.get("discount", "") for it in items if it.get("discount", "")]), "paymentTerm": prazo_pagamento, "commissionRate": rate, "commissionAmount": round(total * rate / 100, 2), "status": "Pendente"})
            for it in items:
                for prod in db["products"]:
                    if prod["id"] == it["productId"]:
                        prod["stock"] = max(0, int(prod.get("stock", 0)) - it["quantity"])
            save_db(db)
            st.session_state.pedido_itens_temp = []
            st.session_state.pedido_cliente_id = ""
            st.session_state.show_tigrinho_salvo = True
            st.session_state.tab = "orders"
            st.rerun()
    if col2.button("Limpar pedido", key="btn_limpar_pedido_temp"):
        st.session_state.pedido_itens_temp = []
        st.session_state.pedido_cliente_id = ""
        st.rerun()


def render_itens_pedido(o):
    for it in o.get("items", []):
        subtotal = float(it.get("quantity", 0)) * float(it.get("price", 0))
        st.markdown(f'''<div class="card"><b>{it.get("productName", "")}</b><br>Qtd: {it.get("quantity", 0)} • Unitário: {money(it.get("price", 0))}<br><b>Total: {money(subtotal)}</b></div>''', unsafe_allow_html=True)


def orders_page(db):
    st.subheader("📦 Pedidos")
    busca = st.text_input("Pesquisar pedido por número, cliente, código ou CNPJ/CPF", key="busca_pedidos")
    for o in sorted(filtered_orders(db), key=lambda x: x.get("orderNumber", 0), reverse=True):
        cli = cliente_por_id(db, o.get("clientId", ""))
        campos = [o.get("orderNumber", ""), o.get("clientName", ""), codigo_cliente(cli), cli.get("document", "")]
        if busca and not combina_inicio(campos, busca):
            continue
        st.markdown(f'<div class="card" style="{status_card_style(o.get("status", ""))}"><b>#{o.get("orderNumber", "")} — {o.get("clientName", "")}</b><br>{money(o.get("total", 0))} • {o.get("status", "")}</div>', unsafe_allow_html=True)
        with st.expander(f"Ver detalhes do pedido #{o.get('orderNumber', '')}"):
            st.write("Vendedor:", o.get("salespersonName", ""))
            st.write("Data:", o.get("date", ""))
            if cli:
                st.write("Cliente:", f"{codigo_cliente(cli)} — {cli.get('document', '')}")

            if st.button("👁️ Visualizar Pedido (PDF)", key="visualizar_pdf_" + o["id"]):
                st.session_state["pdf_aberto"] = o["id"]
                st.rerun()

            if st.session_state.get("pdf_aberto") == o["id"]:
                st.markdown("### Visualizar Pedido (PDF)")
                visualizar_pdf_area(o, cli)
                if st.button("Fechar visualização", key="fechar_pdf_" + o["id"]):
                    st.session_state.pop("pdf_aberto", None)
                    st.rerun()

            render_itens_pedido(o)
            st.write("Desconto:", o.get("discount", ""))
            st.write("Prazo de pagamento:", o.get("paymentTerm", ""))
            st.write("Comissão:", money(o.get("commissionAmount", 0)))
            if st.session_state.get("role") != "admin":
                st.caption("Você está visualizando apenas os seus pedidos.")
            if st.session_state.role == "admin":
                ns = st.selectbox("Status", STATUS, index=STATUS.index(o.get("status", "Pendente")) if o.get("status", "Pendente") in STATUS else 0, key="st" + o["id"])
                col1, col2 = st.columns(2)
                if col1.button("Atualizar", key="up" + o["id"]):
                    o["status"] = ns
                    save_db(db)
                    st.rerun()
                if col2.button("Excluir pedido", key="del" + o["id"]):
                    st.session_state["pedido_para_excluir"] = o["id"]
                    st.rerun()
                if st.session_state.get("pedido_para_excluir") == o["id"]:
                    st.markdown("#### Confirmar exclusão")
                    motivo = st.text_area("Motivo da exclusão", key="motivo_exclusao_" + o["id"], placeholder="Informe o motivo da exclusão do pedido")
                    confirmado = True
                    if o.get("status") == "Faturado":
                        confirmado = st.checkbox("Confirmo que desejo excluir este pedido faturado", key="confirma_excluir_faturado_" + o["id"])
                        st.warning("Pedido faturado exige segunda confirmação para exclusão.")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirmar exclusão", key="confirmar_exclusao_" + o["id"]):
                        if not motivo.strip():
                            st.error("Informe o motivo da exclusão.")
                        elif not confirmado:
                            st.error("Confirme a exclusão do pedido faturado.")
                        else:
                            excluir_pedido_com_motivo(db, o["id"], motivo.strip())
                            st.session_state.pop("pedido_para_excluir", None)
                            st.rerun()
                    if c2.button("Cancelar exclusão", key="cancelar_exclusao_" + o["id"]):
                        st.session_state.pop("pedido_para_excluir", None)
                        st.rerun()


def clients_page(db):
    st.subheader("👥 Clientes")
    with st.expander("Cadastrar cliente"):
        st.markdown("#### Buscar dados pelo CNPJ")
        cnpj_busca = st.text_input("CNPJ", key="cliente_cnpj_busca", placeholder="Digite o CNPJ para buscar automaticamente")
        if st.button("Buscar dados do CNPJ", key="btn_buscar_cnpj_cliente"):
            dados, erro = buscar_cnpj_internet(cnpj_busca)
            if erro:
                st.error(erro)
            else:
                for k, v in {"cliente_doc": dados.get("document", ""), "cliente_nome": dados.get("name", ""), "cliente_email": dados.get("email", ""), "cliente_tel": dados.get("phone", ""), "cliente_cidade": dados.get("city", ""), "cliente_estado": dados.get("state", ""), "cliente_endereco": dados.get("address", ""), "cliente_bairro": dados.get("district", ""), "cliente_cep": dados.get("zip", "")}.items():
                    st.session_state[k] = v
                st.success("Dados encontrados. Confira e clique em Salvar cliente.")
        st.info(f'Código automático do próximo cliente: {proximo_codigo(db["clients"])}')
        with st.form("cli"):
            n = st.text_input("Nome / Razão social", key="cliente_nome")
            doc = st.text_input("CNPJ/CPF", key="cliente_doc")
            em = st.text_input("E-mail", key="cliente_email")
            ph = st.text_input("Telefone", key="cliente_tel")
            city = st.text_input("Cidade", key="cliente_cidade")
            uf = st.text_input("Estado", key="cliente_estado")
            address = st.text_input("Endereço", key="cliente_endereco")
            district = st.text_input("Bairro", key="cliente_bairro")
            zip_code = st.text_input("CEP", key="cliente_cep")
            if st.form_submit_button("Salvar cliente") and n:
                if cliente_duplicado(db, doc):
                    st.error("Cliente já cadastrado com esse CNPJ/CPF.")
                else:
                    db["clients"].insert(0, {"id": uid("cli"), "code": proximo_codigo(db["clients"]), "name": n, "document": doc, "email": em, "phone": ph, "city": city, "state": uf, "address": address, "district": district, "zip": zip_code})
                    save_db(db)
                    st.rerun()

    busca = st.text_input("Pesquisar cliente", key="busca_clientes", placeholder="Nome, código ou CNPJ/CPF")
    encontrados = [c for c in db["clients"] if combina_inicio(campos_cliente(c), busca)] if busca else db["clients"]
    if busca and not encontrados:
        st.warning("Nenhum cliente encontrado.")
    for c in encontrados:
        with st.expander(f'{codigo_cliente(c)} — {c["name"]}'):
            st.write("CNPJ/CPF:", c.get("document", ""))
            st.write("Telefone:", c.get("phone", ""))
            st.write("Cidade/Estado:", f'{c.get("city", "")}/{c.get("state", "")}')
            col1, col2 = st.columns(2)
            editar = col1.button("Editar", key="edit_cli_" + c["id"])
            excluir = col2.button("Excluir", key="del_cli_" + c["id"])
            if excluir:
                if any(o.get("clientId") == c.get("id") for o in db.get("orders", [])):
                    st.error("Não é possível excluir: esse cliente possui pedidos cadastrados.")
                else:
                    db["clients"] = [x for x in db["clients"] if x["id"] != c["id"]]
                    save_db(db)
                    st.rerun()
            if editar or st.session_state.get("editando_cliente") == c["id"]:
                st.session_state["editando_cliente"] = c["id"]
                with st.form("form_edit_cliente_" + c["id"]):
                    novo_nome = st.text_input("Nome / Razão social", value=c.get("name", ""), key="edit_cli_nome_" + c["id"])
                    novo_doc = st.text_input("CNPJ/CPF", value=c.get("document", ""), key="edit_cli_doc_" + c["id"])
                    novo_email = st.text_input("E-mail", value=c.get("email", ""), key="edit_cli_email_" + c["id"])
                    novo_tel = st.text_input("Telefone", value=c.get("phone", ""), key="edit_cli_tel_" + c["id"])
                    nova_cidade = st.text_input("Cidade", value=c.get("city", ""), key="edit_cli_cidade_" + c["id"])
                    novo_estado = st.text_input("Estado", value=c.get("state", ""), key="edit_cli_estado_" + c["id"])
                    novo_endereco = st.text_input("Endereço", value=c.get("address", ""), key="edit_cli_endereco_" + c["id"])
                    novo_bairro = st.text_input("Bairro", value=c.get("district", ""), key="edit_cli_bairro_" + c["id"])
                    novo_cep = st.text_input("CEP", value=c.get("zip", ""), key="edit_cli_cep_" + c["id"])
                    salvar = st.form_submit_button("Salvar edição")
                    cancelar = st.form_submit_button("Cancelar")
                if salvar:
                    repetido = any(outro["id"] != c["id"] and so_numeros(outro.get("document", "")) == so_numeros(novo_doc) and so_numeros(novo_doc) for outro in db["clients"])
                    if repetido:
                        st.error("Já existe outro cliente com esse CNPJ/CPF.")
                    else:
                        c.update({"name": novo_nome, "document": novo_doc, "email": novo_email, "phone": novo_tel, "city": nova_cidade, "state": novo_estado, "address": novo_endereco, "district": novo_bairro, "zip": novo_cep})
                        save_db(db)
                        st.session_state.pop("editando_cliente", None)
                        st.rerun()
                if cancelar:
                    st.session_state.pop("editando_cliente", None)
                    st.rerun()


def products_page(db):
    st.subheader("🛒 Produtos")
    if st.session_state.role == "admin":
        with st.expander("Cadastrar produto"):
            st.info(f'Código automático do próximo produto: {proximo_codigo(db["products"], campo="sku")}')
            with st.form("prod"):
                n = st.text_input("Nome", key="prod_nome")
                cat = st.text_input("Categoria", key="prod_categoria")
                supplier = st.text_input("Fornecedor", key="prod_fornecedor")
                price = st.number_input("Preço", min_value=0.0, step=.01, key="prod_preco")
                stock = st.number_input("Estoque", min_value=0, step=1, key="prod_estoque")
                cr = st.number_input("Comissão %", min_value=0.0, value=float(db["commissionRate"]), step=.5, key="prod_comissao")
                if st.form_submit_button("Salvar produto") and n:
                    if produto_duplicado(db, n):
                        st.error("Produto já cadastrado com esse nome.")
                    else:
                        sku = proximo_codigo(db["products"], campo="sku")
                        db["products"].insert(0, {"id": uid("prod"), "code": sku, "name": n, "sku": sku, "price": price, "stock": stock, "category": cat, "supplier": supplier, "commissionRate": cr})
                        save_db(db)
                        st.rerun()
    fornecedores = sorted(list(set([p.get("supplier", "Sem fornecedor") or "Sem fornecedor" for p in db["products"]])))
    fornecedor_filtro = st.selectbox("Filtrar por fornecedor", ["Todos"] + fornecedores, key="filtro_fornecedor_produtos")
    busca = st.text_input("Pesquisar produto por nome ou código", key="busca_produtos")
    produtos_filtrados = [p for p in db["products"] if (fornecedor_filtro == "Todos" or (p.get("supplier", "Sem fornecedor") or "Sem fornecedor") == fornecedor_filtro) and (not busca or combina_inicio(campos_produto(p), busca))]
    if busca and not produtos_filtrados:
        st.warning("Nenhum produto encontrado.")
    for p in produtos_filtrados:
        codigo = p.get("sku") or p.get("code") or ""
        with st.expander(f'{codigo} — {p["name"]}'):
            st.write("Categoria:", p.get("category", ""))
            st.write("Fornecedor:", p.get("supplier", "Sem fornecedor") or "Sem fornecedor")
            st.write("Preço:", money(p.get("price", 0)))
            st.write("Estoque:", p.get("stock", 0))
            st.write("Comissão:", f'{p.get("commissionRate", db["commissionRate"])}%')
            if st.session_state.role == "admin":
                col1, col2 = st.columns(2)
                editar = col1.button("Editar", key="edit_prod_" + p["id"])
                excluir = col2.button("Excluir", key="del_prod_" + p["id"])
                if excluir:
                    usado = any(it.get("productId") == p.get("id") for o in db.get("orders", []) for it in o.get("items", []))
                    if usado:
                        st.error("Não é possível excluir: esse produto já foi usado em pedido.")
                    else:
                        db["products"] = [x for x in db["products"] if x["id"] != p["id"]]
                        save_db(db)
                        st.rerun()
                if editar or st.session_state.get("editando_produto") == p["id"]:
                    st.session_state["editando_produto"] = p["id"]
                    with st.form("form_edit_prod_" + p["id"]):
                        novo_nome = st.text_input("Nome", value=p.get("name", ""), key="edit_prod_nome_" + p["id"])
                        nova_cat = st.text_input("Categoria", value=p.get("category", ""), key="edit_prod_cat_" + p["id"])
                        novo_forn = st.text_input("Fornecedor", value=p.get("supplier", ""), key="edit_prod_forn_" + p["id"])
                        novo_preco = st.number_input("Preço", min_value=0.0, value=float(p.get("price", 0)), step=.01, key="edit_prod_preco_" + p["id"])
                        novo_estoque = st.number_input("Estoque", min_value=0, value=int(p.get("stock", 0)), step=1, key="edit_prod_estoque_" + p["id"])
                        nova_comissao = st.number_input("Comissão %", min_value=0.0, value=float(p.get("commissionRate", db["commissionRate"])), step=.5, key="edit_prod_comissao_" + p["id"])
                        salvar = st.form_submit_button("Salvar edição")
                        cancelar = st.form_submit_button("Cancelar")
                    if salvar:
                        repetido = any(outro["id"] != p["id"] and normalizar(outro.get("name", "")) == normalizar(novo_nome) for outro in db["products"])
                        if repetido:
                            st.error("Já existe outro produto com esse nome.")
                        else:
                            p.update({"name": novo_nome, "category": nova_cat, "supplier": novo_forn, "price": novo_preco, "stock": novo_estoque, "commissionRate": nova_comissao})
                            save_db(db)
                            st.session_state.pop("editando_produto", None)
                            st.rerun()
                    if cancelar:
                        st.session_state.pop("editando_produto", None)
                        st.rerun()


def more_page(db):
    st.subheader("☰ Mais")
    if st.button("Sair", key="btn_sair"):
        st.session_state.clear()
        st.rerun()
    if st.session_state.role != "admin":
        st.info("Área administrativa disponível somente para o administrador.")
        return

    st.markdown("### Vendedores")
    with st.expander("Cadastrar vendedor"):
        with st.form("sales"):
            n = st.text_input("Nome", key="vend_nome")
            em = st.text_input("E-mail", key="vend_email")
            cpf = st.text_input("CPF", key="vend_cpf")
            ph = st.text_input("Telefone", key="vend_tel")
            pw = st.text_input("Senha", value="123", key="vend_senha")
            senha_provisoria = st.checkbox("Senha provisória", value=True, key="vend_senha_provisoria")
            if st.form_submit_button("Salvar vendedor") and n:
                if any(normalizar(v.get("email", "")) == normalizar(em) and em for v in db["salespeople"]):
                    st.error("Já existe vendedor com esse e-mail.")
                else:
                    db["salespeople"].append({"id": uid("sales"), "name": n, "email": em, "active": True, "cpf": cpf, "phone": ph, "address": "", "password": pw, "passwordIsTemporary": senha_provisoria})
                    save_db(db)
                    st.rerun()

    for s in db["salespeople"]:
        with st.expander(f"{s['name']} — {s['email']} — {'Ativo' if s.get('active') else 'Inativo'}"):
            st.write("CPF:", s.get("cpf", ""))
            st.write("Telefone:", s.get("phone", ""))
            st.write("Senha:", "Provisória" if s.get("passwordIsTemporary") else "Definitiva")
            col1, col2, col3 = st.columns(3)
            editar = col1.button("Editar", key="edit_vend_" + s["id"])
            if col2.button("Ativar/Inativar", key="a" + s["id"]):
                s["active"] = not s.get("active")
                save_db(db)
                st.rerun()
            excluir = col3.button("Excluir", key="del_vend_" + s["id"])
            if excluir:
                if any(o.get("salespersonId") == s.get("id") for o in db.get("orders", [])):
                    st.error("Não é possível excluir: esse vendedor possui pedidos cadastrados.")
                else:
                    db["salespeople"] = [x for x in db["salespeople"] if x["id"] != s["id"]]
                    save_db(db)
                    st.rerun()
            if editar or st.session_state.get("editando_vendedor") == s["id"]:
                st.session_state["editando_vendedor"] = s["id"]
                with st.form("form_edit_vendedor_" + s["id"]):
                    novo_nome = st.text_input("Nome", value=s.get("name", ""), key="edit_vend_nome_" + s["id"])
                    novo_email = st.text_input("E-mail", value=s.get("email", ""), key="edit_vend_email_" + s["id"])
                    novo_cpf = st.text_input("CPF", value=s.get("cpf", ""), key="edit_vend_cpf_" + s["id"])
                    novo_tel = st.text_input("Telefone", value=s.get("phone", ""), key="edit_vend_tel_" + s["id"])
                    nova_senha = st.text_input("Senha", value=s.get("password", "123"), key="edit_vend_senha_" + s["id"])
                    ativo = st.checkbox("Ativo", value=bool(s.get("active", True)), key="edit_vend_ativo_" + s["id"])
                    senha_provisoria_edit = st.checkbox("Senha provisória", value=bool(s.get("passwordIsTemporary", False)), key="edit_vend_senha_provisoria_" + s["id"])
                    salvar = st.form_submit_button("Salvar edição")
                    cancelar = st.form_submit_button("Cancelar")
                if salvar:
                    repetido = any(outro["id"] != s["id"] and normalizar(outro.get("email", "")) == normalizar(novo_email) and novo_email for outro in db["salespeople"])
                    if repetido:
                        st.error("Já existe outro vendedor com esse e-mail.")
                    else:
                        s.update({"name": novo_nome, "email": novo_email, "cpf": novo_cpf, "phone": novo_tel, "password": nova_senha, "passwordIsTemporary": senha_provisoria_edit, "active": ativo})
                        save_db(db)
                        st.session_state.pop("editando_vendedor", None)
                        st.rerun()
                if cancelar:
                    st.session_state.pop("editando_vendedor", None)
                    st.rerun()

    st.markdown("### Pedidos excluídos")
    garantir_lixeira(db)
    if not db.get("deleted_orders"):
        st.info("Nenhum pedido excluído.")
    else:
        for o in db.get("deleted_orders", []):
            with st.expander(f"#{o.get('orderNumber','')} — {o.get('clientName','')} — {money(o.get('total',0))}"):
                st.write("Status original:", o.get("originalStatus", o.get("status", "")))
                st.write("Excluído em:", o.get("deletedAt", ""))
                st.write("Excluído por:", o.get("deletedBy", ""))
                st.write("Motivo:", o.get("deleteReason", ""))
                st.write("Vendedor:", o.get("salespersonName", ""))
                render_itens_pedido(o)

    st.markdown("### Comissão")
    rate = st.number_input("Comissão geral %", min_value=0.0, value=float(db["commissionRate"]), step=.5, key="comissao_geral")
    if st.button("Salvar comissão", key="btn_salvar_comissao"):
        db["commissionRate"] = rate
        save_db(db)
        st.success("Salvo")

    st.markdown("### Backup / Importação")
    st.download_button("Baixar backup JSON", data=json.dumps(db, ensure_ascii=False, indent=2).encode("utf-8"), file_name="tigrao_backup.json", key="download_backup_json")
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        for k, v in {"produtos": pd.DataFrame(db["products"]), "clientes": pd.DataFrame(db["clients"]), "vendedores": pd.DataFrame(db["salespeople"]), "pedidos": pd.DataFrame(db["orders"])}.items():
            v.to_excel(writer, index=False, sheet_name=k)
    st.download_button("Exportar Excel", data=out.getvalue(), file_name="tigrao_export.xlsx", key="download_excel")
    up = st.file_uploader("Importar backup JSON", type=["json"], key="upload_backup_json")
    if up and st.button("Importar agora", key="btn_importar_backup"):
        new = json.loads(up.read().decode("utf-8"))
        save_db(new)
        st.success("Importado")
        st.rerun()
    col1, col2 = st.columns(2)
    if col1.button("Restaurar exemplo", key="btn_restaurar_exemplo"):
        save_db(seed())
        st.rerun()
    if col2.button("Limpar banco", key="btn_limpar_banco"):
        save_db({"app": "Tigrão Distribuidora", "systemName": "TIGRÃO", "commissionRate": 7, "products": [], "clients": [], "salespeople": INITIAL_SALES[:1], "orders": [], "deleted_orders": []})
        st.rerun()


css()
db = load_db()
garantir_lixeira(db)
if "auth" not in st.session_state:
    st.session_state.auth = False
if "tab" not in st.session_state:
    st.session_state.tab = "dashboard"
if not st.session_state.auth:
    login(db)
    st.stop()
header(db)
nav()
tigrinho_salvo()
{"dashboard": dashboard, "newOrder": new_order, "orders": orders_page, "clients": clients_page, "products": products_page, "more": more_page}[st.session_state.tab](db)
