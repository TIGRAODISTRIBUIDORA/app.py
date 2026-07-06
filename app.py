import json, os, uuid
from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st
import requests

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered", initial_sidebar_state="collapsed")

DATA_DIR='dados_tigrao'
DB_FILE=os.path.join(DATA_DIR,'banco.json')
os.makedirs(DATA_DIR, exist_ok=True)

STATUS=['Pendente','Faturado','Entregue','Cancelado']

INITIAL_PRODUCTS=[
 {'id':'prod-1','name':'Cerveja Heineken Long Neck 330ml','sku':'HEI-001','price':8.50,'stock':120,'category':'Cervejas','supplier':'Heineken','commissionRate':3},
 {'id':'prod-2','name':'Cigarro Rothmans Red Box','sku':'ROT-002','price':9.75,'stock':450,'category':'Tabacaria','supplier':'Souza Cruz','commissionRate':5},
 {'id':'prod-3','name':'Refrigerante Coca-Cola 2L','sku':'COC-003','price':11.90,'stock':250,'category':'Refrigerantes','supplier':'Coca-Cola','commissionRate':4},
 {'id':'prod-4','name':'Energético Monster Energy 473ml','sku':'MON-004','price':10.50,'stock':180,'category':'Energéticos','supplier':'Monster','commissionRate':4},
 {'id':'prod-5','name':'Água Mineral Sem Gás 500ml','sku':'AGU-005','price':2.50,'stock':600,'category':'Águas','supplier':'Fornecedor Geral','commissionRate':2},
 {'id':'prod-6','name':'Cerveja Amstel Lata 350ml','sku':'AMS-006','price':4.20,'stock':320,'category':'Cervejas','supplier':'Heineken','commissionRate':3},
 {'id':'prod-7','name':'Vodka Smirnoff 998ml','sku':'SMI-007','price':39.90,'stock':65,'category':'Destilados','supplier':'Diageo','commissionRate':4},
 {'id':'prod-8','name':'Whisky Johnnie Walker Red Label 1L','sku':'JWL-008','price':99.90,'stock':40,'category':'Destilados','supplier':'Diageo','commissionRate':4},
]
INITIAL_CLIENTS=[
 {'id':'cli-1','code':'001','name':'nelson das galaxie','document':'123.456.789-00','email':'nelson@galaxie.com','phone':'(11) 98888-7777','city':'São Paulo','state':'SP'},
 {'id':'cli-2','code':'002','name':'Distribuidora Silva & Silva','document':'98.765.432/0001-11','email':'silva@distribuidora.com','phone':'(11) 3245-8899','city':'Campinas','state':'SP'},
 {'id':'cli-3','code':'003','name':'Mercadinho do Bairro Ltda','document':'45.123.789/0001-44','email':'contato@mercadinhobairro.com','phone':'(21) 97777-6666','city':'Rio de Janeiro','state':'RJ'},
 {'id':'cli-4','code':'004','name':'Adega Central','document':'55.666.777/0001-88','email':'adega.central@outlook.com','phone':'(19) 99122-3344','city':'Piracicaba','state':'SP'},
]
INITIAL_SALES=[
 {'id':'sales-1','name':'Vendedor','email':'vendedor@tigrao.com','active':True,'cpf':'111.111.111-11','phone':'(11) 91111-1111','address':'Rua Principal, 100','password':'123','passwordIsTemporary':True},
 {'id':'sales-2','name':'Carlos Souza','email':'carlos@tigrao.com','active':True,'cpf':'222.222.222-22','phone':'(11) 92222-2222','address':'Avenida Brasil, 250','password':'123','passwordIsTemporary':False},
 {'id':'sales-3','name':'Fernanda Lima','email':'fernanda@tigrao.com','active':True,'cpf':'333.333.333-33','phone':'(11) 93333-3333','address':'Praça das Flores, 15','password':'123','passwordIsTemporary':False},
]
INITIAL_ORDERS=[
 {'id':'ord-0','orderNumber':0,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':20,'price':99.90},{'productId':'prod-7','productName':'Vodka Smirnoff 998ml','quantity':30,'price':39.90},{'productId':'prod-1','productName':'Cerveja Heineken Long Neck 330ml','quantity':43,'price':8.50},{'productId':'prod-5','productName':'Água Mineral Sem Gás 500ml','quantity':15,'price':2.50}], 'total':3564.40,'commissionRate':7,'commissionAmount':249.51,'status':'Faturado'},
 {'id':'ord-1','orderNumber':1,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':20,'price':99.90},{'productId':'prod-7','productName':'Vodka Smirnoff 998ml','quantity':30,'price':39.90}], 'total':3564.40,'commissionRate':7,'commissionAmount':249.51,'status':'Faturado'},
 {'id':'ord-2','orderNumber':2,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':20,'price':99.90}], 'total':3564.40,'commissionRate':7,'commissionAmount':249.51,'status':'Faturado'},
 {'id':'ord-3','orderNumber':3,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':20,'price':99.90}], 'total':3564.40,'commissionRate':7,'commissionAmount':249.51,'status':'Entregue'},
 {'id':'ord-4','orderNumber':4,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':20,'price':99.90}], 'total':3564.40,'commissionRate':7,'commissionAmount':249.51,'status':'Entregue'},
 {'id':'ord-5','orderNumber':5,'date':'2026-06-30T17:34:36','salespersonId':'sales-1','salespersonName':'Vendedor','clientId':'cli-1','clientName':'nelson das galaxie','items':[{'productId':'prod-8','productName':'Whisky Johnnie Walker Red Label 1L','quantity':25,'price':99.90}], 'total':4061.15,'commissionRate':7,'commissionAmount':284.28,'status':'Entregue'},
]

def seed():
    return {'app':'Tigrão Distribuidora','systemName':'TIGRÃO','commissionRate':7,'products':INITIAL_PRODUCTS,'clients':INITIAL_CLIENTS,'salespeople':INITIAL_SALES,'orders':INITIAL_ORDERS}

def load_db():
    if not os.path.exists(DB_FILE): save_db(seed())
    with open(DB_FILE,'r',encoding='utf-8') as f: return json.load(f)

def save_db(db):
    with open(DB_FILE,'w',encoding='utf-8') as f: json.dump(db,f,ensure_ascii=False,indent=2)

def money(v): return f"R$ {float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X','.')
def uid(prefix): return f"{prefix}-{uuid.uuid4().hex[:8]}"

def proximo_codigo(lista, campo='code'):
 nums=[]
 for item in lista:
  valor=item.get(campo) or item.get('codigo') or ''
  n=so_numeros(valor)
  if n:
   try:
    nums.append(int(n))
   except:
    pass
 return str(max(nums, default=0)+1)

def proximo_pedido(orders):
 nums=[]
 for o in orders:
  try:
   nums.append(int(o.get('orderNumber',0)))
  except:
   pass
 return max(nums, default=0)+1


def cliente_duplicado(db, documento):
 doc=so_numeros(documento)
 if not doc:
  return False
 for c in db.get('clients',[]):
  if so_numeros(c.get('document','')) == doc:
   return True
 return False

def produto_duplicado(db, nome, codigo=''):
 nome_norm=normalizar(nome)
 codigo_norm=normalizar(codigo)
 for p in db.get('products',[]):
  nome_existente=normalizar(p.get('name',''))
  codigo_existente=normalizar(p.get('sku','') or p.get('code',''))
  if nome_norm and nome_existente == nome_norm:
   return True
  if codigo_norm and codigo_existente == codigo_norm:
   return True
 return False



def normalizar(txt):
 txt=str(txt or '').lower().strip()
 troca={'á':'a','à':'a','ã':'a','â':'a','é':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}
 for a,b in troca.items():
  txt=txt.replace(a,b)
 return txt

def so_numeros(txt):
 return ''.join(ch for ch in str(txt or '') if ch.isdigit())

def comeca_com(texto, busca):
 busca=normalizar(busca)
 texto=normalizar(texto)
 if not busca:
  return True

 busca_num=so_numeros(busca)
 texto_num=so_numeros(texto)

 # Para código, pedido, CPF/CNPJ e telefone, aceita início ou trecho numérico.
 if busca_num and busca_num in texto_num:
  return True

 partes=texto.replace('-',' ').replace('/',' ').replace('.',' ').replace(',',' ').replace('&',' ').split()
 return any(p.startswith(busca) for p in partes)

def combina_inicio(campos, busca):
 busca=normalizar(busca)
 if not busca:
  return True
 for campo in campos:
  if comeca_com(campo, busca):
   return True
 return False

def sugestoes_inicio(lista, campos, busca, limite=8):
 busca=normalizar(busca)
 if not busca:
  return []
 achados=[]
 for item in lista:
  textos=[str(item.get(c,'')) for c in campos]
  if combina_inicio(textos, busca):
   achados.append(item)
 return achados[:limite]

def codigo_cliente(c):
 return c.get('code') or c.get('codigo') or c.get('id','').replace('cli-','')

def campos_cliente(c):
 return [codigo_cliente(c), c.get('name',''), c.get('document','')]

def campos_produto(p):
 return [p.get('sku',''), p.get('code',''), p.get('barcode',''), p.get('name','')]

def cliente_por_id(db, client_id):
 return next((c for c in db.get('clients',[]) if c.get('id')==client_id), {})

def buscar_cnpj_internet(cnpj):
 cnpj_limpo=so_numeros(cnpj)
 if len(cnpj_limpo)!=14:
  return None, 'CNPJ inválido. Digite 14 números.'

 try:
  url=f'https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}'
  r=requests.get(url, timeout=10)

  if r.status_code!=200:
   return None, 'CNPJ não encontrado ou serviço indisponível.'

  d=r.json()

  telefone=''
  if d.get('ddd_telefone_1'):
   telefone=d.get('ddd_telefone_1')
  elif d.get('telefone'):
   telefone=d.get('telefone')

  dados={
   'document':cnpj_limpo,
   'name':d.get('nome_fantasia') or d.get('razao_social') or '',
   'email':d.get('email') or '',
   'phone':telefone,
   'city':d.get('municipio') or '',
   'state':d.get('uf') or ''
  }

  return dados, None

 except Exception as e:
  return None, 'Erro ao buscar CNPJ. Verifique a internet e tente novamente.'


def css():
 st.markdown('''<style>
 header, footer, [data-testid="stSidebar"] {display:none!important}

 .block-container{
   max-width:520px!important;
   padding:14px 14px 86px!important;
 }

 .stApp{
   background:#fafafa;
   color:#171717;
 }

 *{
   font-family:Inter,Arial,sans-serif;
 }

 .top{
   background:#111;
   color:#fff;
   border-radius:0 0 28px 28px;
   padding:22px;
   margin:-14px -14px 14px;
 }

 .brand{
   display:flex;
   gap:12px;
   align-items:center;
 }

 .logo{
   width:48px;
   height:48px;
   background:#f97316;
   border-radius:18px;
   display:flex;
   align-items:center;
   justify-content:center;
   font-size:28px;
 }

 .title{
   font-size:26px;
   font-weight:900;
 }

 .sub{
   color:#fb923c;
   font-size:11px;
   font-weight:900;
   letter-spacing:2px;
 }

 .card{
   background:white;
   border:1px solid #eee;
   border-radius:24px;
   padding:16px;
   margin:10px 0;
   box-shadow:0 8px 24px rgba(0,0,0,.05);
 }

 .metric{
   background:#111;
   color:#fff;
   border-radius:22px;
   padding:12px 16px;
   min-height:86px;
 }

 .metric b{
   font-size:22px;
   line-height:1.1;
 }

 .pill{
   border-radius:999px;
   padding:6px 10px;
   background:#fff7ed;
   color:#ea580c;
   font-weight:900;
   font-size:11px;
 }

 .status{
   font-weight:900;
   border-radius:999px;
   padding:4px 8px;
   font-size:11px;
 }

 .stButton>button{
   border-radius:16px!important;
   font-weight:900!important;
   min-height:44px;
 }

 .stTextInput input,
 .stNumberInput input,
 .stSelectbox div{
   border-radius:14px!important;
 }

 h2, h3{
   margin-top:12px!important;
 }

 @media (max-width:640px){
   .block-container{
     max-width:100%!important;
     padding:12px 14px 86px!important;
   }

   .top{
     padding:20px;
     margin:-12px -14px 12px;
   }

   .metric{
     padding:10px 16px!important;
     min-height:78px!important;
     border-radius:20px!important;
     margin-bottom:8px!important;
   }

   .metric b{
     font-size:20px!important;
   }

   h2, h3{
     margin-top:8px!important;
     margin-bottom:8px!important;
   }

   [data-testid="stVerticalBlock"]{
     gap:.35rem!important;
   }
 }
 </style>''', unsafe_allow_html=True)

def header(db):
 user=st.session_state.get('user_name','')
 st.markdown(f'''<div class="top"><div class="brand"><div class="logo">🐯</div><div><div class="sub">DISTRIBUIDORA</div><div class="title">{db.get('systemName','TIGRÃO')}</div><div style="color:#aaa;font-size:12px">{user}</div></div></div></div>''', unsafe_allow_html=True)

def nav():
 tabs=[('dashboard','🏠','Início'),('newOrder','➕','Pedido'),('orders','📦','Pedidos'),('clients','👥','Clientes'),('products','🛒','Produtos'),('more','☰','Mais')]

 st.markdown('''
 <style>
 .st-key-bottom_nav{
   position:fixed!important;
   left:0!important;
   right:0!important;
   bottom:0!important;
   z-index:999999!important;
   background:#111!important;
   height:72px!important;
   padding:5px 3px calc(5px + env(safe-area-inset-bottom)) 3px!important;
   border-top:1px solid #222!important;
   overflow:hidden!important;
 }

 .st-key-bottom_nav [data-testid="stHorizontalBlock"]{
   width:100%!important;
   max-width:520px!important;
   height:62px!important;
   margin:0 auto!important;
   display:grid!important;
   grid-template-columns:repeat(6, 1fr)!important;
   gap:2px!important;
   align-items:center!important;
 }

 .st-key-bottom_nav [data-testid="column"]{
   width:100%!important;
   min-width:0!important;
   max-width:none!important;
   padding:0!important;
   flex:none!important;
 }

 .st-key-bottom_nav [data-testid="column"] > div{
   width:100%!important;
   min-width:0!important;
 }

 .st-key-bottom_nav .stButton{
   width:100%!important;
   min-width:0!important;
 }

 .st-key-bottom_nav .stButton > button{
   width:100%!important;
   min-width:0!important;
   height:56px!important;
   min-height:56px!important;
   border:0!important;
   border-radius:15px!important;
   background:#111!important;
   color:#eee!important;
   font-size:10px!important;
   font-weight:900!important;
   padding:2px 0!important;
   line-height:1.05!important;
   white-space:pre-line!important;
   overflow:hidden!important;
   text-align:center!important;
 }

 .st-key-bottom_nav .stButton > button[kind="primary"]{
   background:#f97316!important;
   color:#111!important;
 }

 @media (max-width:640px){
   .st-key-bottom_nav{
     height:70px!important;
     padding:4px 2px calc(4px + env(safe-area-inset-bottom)) 2px!important;
   }

   .st-key-bottom_nav [data-testid="stHorizontalBlock"]{
     width:100vw!important;
     max-width:100vw!important;
     height:60px!important;
     grid-template-columns:repeat(6, minmax(0, 1fr))!important;
     gap:1px!important;
   }

   .st-key-bottom_nav .stButton > button{
     height:56px!important;
     min-height:56px!important;
     border-radius:14px!important;
     font-size:9px!important;
     padding:1px 0!important;
   }
 }

 @media (max-width:390px){
   .st-key-bottom_nav .stButton > button{
     font-size:8px!important;
   }
 }
 </style>
 ''', unsafe_allow_html=True)

 with st.container(key='bottom_nav'):
  cols=st.columns(6)
  for col,(key,ico,label) in zip(cols,tabs):
   active = st.session_state.get('tab','dashboard') == key
   if col.button(f'{ico}\n{label}', key=f'nav_{key}', type='primary' if active else 'secondary'):
    st.session_state.tab=key
    st.rerun()

def login(db):
 st.markdown('<div style="height:40px"></div><div class="card" style="text-align:center"><div style="font-size:64px">🐯</div><h1>TIGRÃO</h1><b>Acesso ao sistema</b></div>', unsafe_allow_html=True)
 with st.form('login'):
  perfil=st.radio('Perfil',['Admin','Vendedor'], horizontal=True)
  usuario=st.text_input('Usuário / e-mail', key='login_usuario')
  senha=st.text_input('Senha', type='password', key='login_senha')
  ok=st.form_submit_button('Entrar')
 if ok:
  if perfil=='Admin' and usuario.lower() in ['admin','administrador',''] and senha=='admin123':
   st.session_state.auth=True; st.session_state.role='admin'; st.session_state.sales_id=''; st.session_state.user_name='Administrador'; st.rerun()
  sellers=[s for s in db['salespeople'] if s.get('active')]
  seller=next((s for s in sellers if usuario.lower() in [s['email'].lower(), s['name'].lower()] and senha==s.get('password','123')),None)
  if perfil=='Vendedor' and seller:
   st.session_state.auth=True; st.session_state.role='vendedor'; st.session_state.sales_id=seller['id']; st.session_state.user_name=seller['name']; st.rerun()
  st.error('Login ou senha inválidos')
 st.info('Admin: admin / admin123   |   Vendedor: vendedor@tigrao.com / 123')

def filtered_orders(db):
 orders=db['orders']
 if st.session_state.role=='vendedor': orders=[o for o in orders if o['salespersonId']==st.session_state.sales_id]
 return orders

def dashboard(db):
 orders=filtered_orders(db); total=sum(o['total'] for o in orders); com=sum(o.get('commissionAmount',0) for o in orders)
 c1,c2=st.columns(2)
 c1.markdown(f'<div class="metric">Vendas<br><b>{money(total)}</b></div>',unsafe_allow_html=True)
 c2.markdown(f'<div class="metric">Comissão<br><b>{money(com)}</b></div>',unsafe_allow_html=True)
 c1,c2,c3=st.columns(3); c1.metric('Pedidos',len(orders)); c2.metric('Clientes',len(db['clients'])); c3.metric('Produtos',len(db['products']))
 st.subheader('Últimos pedidos')
 for o in sorted(orders,key=lambda x:x['orderNumber'],reverse=True)[:10]:
  st.markdown(f'<div class="card"><b>#{o["orderNumber"]} — {o["clientName"]}</b><br>{o["salespersonName"]} • {o["status"]}<br><h3>{money(o["total"])}</h3></div>',unsafe_allow_html=True)

def new_order(db):
 st.subheader('➕ Novo Pedido')
 clients=db['clients']; products=db['products']; sales=db['salespeople']

 if 'pedido_itens_temp' not in st.session_state:
  st.session_state.pedido_itens_temp=[]

 st.markdown('### Cliente')
 busca_cliente=st.text_input('Pesquisar cliente por nome, código ou CNPJ/CPF', key='pedido_busca_cliente')
 clientes_filtrados=[c for c in clients if combina_inicio(campos_cliente(c), busca_cliente)] if busca_cliente else clients[:20]

 if not clientes_filtrados:
  st.warning('Nenhum cliente encontrado.')
  clientes_filtrados=clients[:1]

 c=st.selectbox('Cliente', clientes_filtrados, format_func=lambda x:x['name'], key='pedido_cliente')

 if st.session_state.role=='admin':
  s=st.selectbox('Vendedor', [x for x in sales if x.get('active')], format_func=lambda x:x['name'], key='pedido_vendedor')
 else:
  s=next(x for x in sales if x['id']==st.session_state.sales_id)

 col_desc,col_prazo=st.columns([1,2])
 desconto=col_desc.text_input('Desconto', key='pedido_desconto', placeholder='Ex: 5%')
 prazo_pagamento=col_prazo.text_input('Prazo de pagamento', key='pedido_prazo_pagamento', placeholder='Ex: 7 dias')

 st.markdown('### Produto')
 busca_prod=st.text_input('Pesquisar produto por nome ou código', key='pedido_busca_produto')
 produtos_filtrados=[p for p in products if combina_inicio(campos_produto(p), busca_prod)][:20] if busca_prod else []

 if busca_prod and not produtos_filtrados:
  st.warning('Nenhum produto encontrado.')

 if produtos_filtrados:
  p=st.selectbox('Produto encontrado', produtos_filtrados, format_func=lambda x:x['name'], key='pedido_produto_unico')
  colq,colb=st.columns([1,2])
  qtd=colq.number_input('Qtd', min_value=1, step=1, key='pedido_qtd_unica')
  if colb.button('Adicionar ao pedido', key='btn_add_produto_pedido'):
   item={
    'productId':p['id'],
    'productName':p['name'],
    'quantity':int(qtd),
    'price':float(p['price']),
    'commissionRate':p.get('commissionRate',db['commissionRate'])
   }
   st.session_state.pedido_itens_temp.append(item)
   st.rerun()

 st.markdown('### Itens do pedido')

 if not st.session_state.pedido_itens_temp:
  st.info('Nenhum produto adicionado ainda.')
 else:
  total_temp=sum(it['quantity']*it['price'] for it in st.session_state.pedido_itens_temp)

  for idx,it in enumerate(st.session_state.pedido_itens_temp):
   subtotal=it['quantity']*it['price']
   col1,col2=st.columns([4,1])
   col1.markdown(f'<div class="card"><b>{it["productName"]}</b><br>Qtd: {it["quantity"]} • Unitário: {money(it["price"])}<br><b>Subtotal: {money(subtotal)}</b></div>', unsafe_allow_html=True)
   if col2.button('Excluir', key=f'excluir_item_temp_{idx}'):
    st.session_state.pedido_itens_temp.pop(idx)
    st.rerun()

  st.markdown(f'<div class="metric">Total do pedido<br><b>{money(total_temp)}</b></div>', unsafe_allow_html=True)

 col1,col2=st.columns(2)

 if col1.button('Salvar pedido', key='btn_salvar_pedido_final'):
  items=st.session_state.pedido_itens_temp

  if not items:
   st.error('Adicione pelo menos 1 produto.')
  else:
   total=sum(it['quantity']*it['price'] for it in items)
   rate=float(db['commissionRate'])
   maxnum=proximo_pedido(db['orders'])

   db['orders'].insert(0,{
    'id':uid('ord'),
    'orderNumber':maxnum,
    'date':datetime.now().isoformat(timespec='seconds'),
    'salespersonId':s['id'],
    'salespersonName':s['name'],
    'clientId':c['id'],
    'clientName':c['name'],
    'items':items,
    'total':total,
    'discount':desconto,
    'paymentTerm':prazo_pagamento,
    'commissionRate':rate,
    'commissionAmount':round(total*rate/100,2),
    'status':'Pendente'
   })

   for it in items:
    for prod in db['products']:
     if prod['id']==it['productId']:
      prod['stock']=max(0,int(prod.get('stock',0))-it['quantity'])

   save_db(db)
   st.session_state.pedido_itens_temp=[]
   st.success('Pedido salvo com sucesso')
   st.session_state.tab='orders'
   st.rerun()

 if col2.button('Limpar pedido', key='btn_limpar_pedido_temp'):
  st.session_state.pedido_itens_temp=[]
  st.rerun()

def orders_page(db):
 st.subheader('📦 Pedidos')
 busca=st.text_input('Pesquisar pedido por número, cliente, código ou CNPJ/CPF', key='busca_pedidos')
 for o in sorted(filtered_orders(db),key=lambda x:x['orderNumber'],reverse=True):
  cli=cliente_por_id(db, o.get('clientId',''))
  campos=[o.get('orderNumber',''),o.get('clientName',''),codigo_cliente(cli),cli.get('document','')]
  if busca and not combina_inicio(campos, busca):
   continue
  with st.expander(f"#{o['orderNumber']} — {o['clientName']} — {money(o['total'])} — {o['status']}"):
   st.write('Vendedor:',o['salespersonName']); st.write('Data:',o['date'])
   if cli:
    st.write('Cliente:', f"{codigo_cliente(cli)} — {cli.get('document','')}")
   st.dataframe(pd.DataFrame(o['items']), use_container_width=True, hide_index=True)
   st.write('Desconto:', o.get('discount',''))
   st.write('Prazo de pagamento:', o.get('paymentTerm',''))
   st.write('Comissão:', money(o.get('commissionAmount',0)))
   if st.session_state.role=='admin':
    ns=st.selectbox('Status', STATUS, index=STATUS.index(o['status']), key='st'+o['id'])
    col1,col2=st.columns(2)
    if col1.button('Atualizar', key='up'+o['id']): o['status']=ns; save_db(db); st.rerun()
    if col2.button('Excluir pedido', key='del'+o['id']): db['orders']=[x for x in db['orders'] if x['id']!=o['id']]; save_db(db); st.rerun()

def clients_page(db):
 st.subheader('👥 Clientes')

 with st.expander('Cadastrar cliente'):
  st.markdown('#### Buscar dados pelo CNPJ')
  cnpj_busca=st.text_input('CNPJ', key='cliente_cnpj_busca', placeholder='Digite o CNPJ para buscar automaticamente')

  if st.button('Buscar dados do CNPJ', key='btn_buscar_cnpj_cliente'):
   dados, erro=buscar_cnpj_internet(cnpj_busca)
   if erro:
    st.error(erro)
   else:
    st.session_state['cliente_doc']=dados.get('document','')
    st.session_state['cliente_nome']=dados.get('name','')
    st.session_state['cliente_email']=dados.get('email','')
    st.session_state['cliente_tel']=dados.get('phone','')
    st.session_state['cliente_cidade']=dados.get('city','')
    st.session_state['cliente_estado']=dados.get('state','')
    st.success('Dados encontrados. Confira e clique em Salvar cliente.')

  codigo_auto=proximo_codigo(db['clients'])
  st.info(f'Código automático do próximo cliente: {codigo_auto}')

  with st.form('cli'):
   n=st.text_input('Nome / Razão social', key='cliente_nome')
   doc=st.text_input('CNPJ/CPF', key='cliente_doc')
   em=st.text_input('E-mail', key='cliente_email')
   ph=st.text_input('Telefone', key='cliente_tel')
   city=st.text_input('Cidade', key='cliente_cidade')
   uf=st.text_input('Estado', key='cliente_estado')

   if st.form_submit_button('Salvar cliente') and n:
    if cliente_duplicado(db, doc):
     st.error('Cliente já cadastrado com esse CNPJ/CPF.')
    else:
     codigo=proximo_codigo(db['clients'])
     db['clients'].insert(0,{'id':uid('cli'),'code':codigo,'name':n,'document':doc,'email':em,'phone':ph,'city':city,'state':uf})
     save_db(db)
     st.rerun()

 busca=st.text_input('Pesquisar cliente por nome, código ou CNPJ/CPF', key='busca_clientes')
 encontrados=[c for c in db['clients'] if combina_inicio(campos_cliente(c), busca)] if busca else db['clients']

 if busca and not encontrados:
  st.warning('Nenhum cliente encontrado.')

 for c in encontrados:
  cod=codigo_cliente(c)
  with st.expander(f'{cod} — {c["name"]}'):
   st.write('CNPJ/CPF:', c.get('document',''))
   st.write('Telefone:', c.get('phone',''))
   st.write('Cidade/Estado:', f'{c.get("city","")}/{c.get("state","")}')

   col1,col2=st.columns(2)
   editar=col1.button('Editar', key='edit_cli_'+c['id'])
   excluir=col2.button('Excluir', key='del_cli_'+c['id'])

   if excluir:
    usado=any(o.get('clientId')==c.get('id') for o in db.get('orders',[]))
    if usado:
     st.error('Não é possível excluir: esse cliente possui pedidos cadastrados.')
    else:
     db['clients']=[x for x in db['clients'] if x['id']!=c['id']]
     save_db(db)
     st.rerun()

   if editar or st.session_state.get('editando_cliente')==c['id']:
    st.session_state['editando_cliente']=c['id']
    with st.form('form_edit_cliente_'+c['id']):
     novo_nome=st.text_input('Nome / Razão social', value=c.get('name',''), key='edit_cli_nome_'+c['id'])
     novo_doc=st.text_input('CNPJ/CPF', value=c.get('document',''), key='edit_cli_doc_'+c['id'])
     novo_email=st.text_input('E-mail', value=c.get('email',''), key='edit_cli_email_'+c['id'])
     novo_tel=st.text_input('Telefone', value=c.get('phone',''), key='edit_cli_tel_'+c['id'])
     nova_cidade=st.text_input('Cidade', value=c.get('city',''), key='edit_cli_cidade_'+c['id'])
     novo_estado=st.text_input('Estado', value=c.get('state',''), key='edit_cli_estado_'+c['id'])
     salvar=st.form_submit_button('Salvar edição')
     cancelar=st.form_submit_button('Cancelar')

    if salvar:
     doc_repetido=False
     for outro in db['clients']:
      if outro['id']!=c['id'] and so_numeros(outro.get('document',''))==so_numeros(novo_doc) and so_numeros(novo_doc):
       doc_repetido=True

     if doc_repetido:
      st.error('Já existe outro cliente com esse CNPJ/CPF.')
     else:
      c['name']=novo_nome
      c['document']=novo_doc
      c['email']=novo_email
      c['phone']=novo_tel
      c['city']=nova_cidade
      c['state']=novo_estado
      save_db(db)
      st.session_state.pop('editando_cliente', None)
      st.rerun()

    if cancelar:
     st.session_state.pop('editando_cliente', None)
     st.rerun()

def products_page(db):
 st.subheader('🛒 Produtos')
 if st.session_state.role=='admin':
  with st.expander('Cadastrar produto'):
   codigo_auto=proximo_codigo(db['products'], campo='sku')
   st.info(f'Código automático do próximo produto: {codigo_auto}')

   with st.form('prod'):
    n=st.text_input('Nome', key='prod_nome')
    cat=st.text_input('Categoria', key='prod_categoria')
    supplier=st.text_input('Fornecedor', key='prod_fornecedor')
    price=st.number_input('Preço',min_value=0.0,step=.01,key='prod_preco')
    stock=st.number_input('Estoque',min_value=0,step=1,key='prod_estoque')
    cr=st.number_input('Comissão %',min_value=0.0,value=float(db['commissionRate']),step=.5,key='prod_comissao')
    if st.form_submit_button('Salvar produto') and n:
     if produto_duplicado(db, n):
      st.error('Produto já cadastrado com esse nome.')
     else:
      sku=proximo_codigo(db['products'], campo='sku')
      db['products'].insert(0,{'id':uid('prod'),'code':sku,'name':n,'sku':sku,'price':price,'stock':stock,'category':cat,'supplier':supplier,'commissionRate':cr})
      save_db(db); st.rerun()

 fornecedores=sorted(list(set([p.get('supplier','Sem fornecedor') or 'Sem fornecedor' for p in db['products']])))
 fornecedor_filtro=st.selectbox('Filtrar por fornecedor', ['Todos']+fornecedores, key='filtro_fornecedor_produtos')
 busca=st.text_input('Pesquisar produto por nome ou código', key='busca_produtos')

 produtos_filtrados=[]
 for p in db['products']:
  fornecedor_produto=p.get('supplier','Sem fornecedor') or 'Sem fornecedor'
  if fornecedor_filtro!='Todos' and fornecedor_produto!=fornecedor_filtro: continue
  if busca and not combina_inicio(campos_produto(p), busca): continue
  produtos_filtrados.append(p)

 if busca and not produtos_filtrados:
  st.warning('Nenhum produto encontrado.')

 for p in produtos_filtrados:
  fornecedor_produto=p.get('supplier','Sem fornecedor') or 'Sem fornecedor'
  codigo=p.get('sku') or p.get('code') or ''
  with st.expander(f'{codigo} — {p["name"]}'):
   st.write('Categoria:', p.get('category',''))
   st.write('Fornecedor:', fornecedor_produto)
   st.write('Preço:', money(p.get('price',0)))
   st.write('Estoque:', p.get('stock',0))
   st.write('Comissão:', f'{p.get("commissionRate",db["commissionRate"])}%')

   if st.session_state.role=='admin':
    col1,col2=st.columns(2)
    editar=col1.button('Editar', key='edit_prod_'+p['id'])
    excluir=col2.button('Excluir', key='del_prod_'+p['id'])

    if excluir:
     usado=False
     for o in db.get('orders',[]):
      for it in o.get('items',[]):
       if it.get('productId')==p.get('id'):
        usado=True
     if usado:
      st.error('Não é possível excluir: esse produto já foi usado em pedido.')
     else:
      db['products']=[x for x in db['products'] if x['id']!=p['id']]
      save_db(db)
      st.rerun()

    if editar or st.session_state.get('editando_produto')==p['id']:
     st.session_state['editando_produto']=p['id']
     with st.form('form_edit_prod_'+p['id']):
      novo_nome=st.text_input('Nome', value=p.get('name',''), key='edit_prod_nome_'+p['id'])
      nova_cat=st.text_input('Categoria', value=p.get('category',''), key='edit_prod_cat_'+p['id'])
      novo_forn=st.text_input('Fornecedor', value=p.get('supplier',''), key='edit_prod_forn_'+p['id'])
      novo_preco=st.number_input('Preço', min_value=0.0, value=float(p.get('price',0)), step=.01, key='edit_prod_preco_'+p['id'])
      novo_estoque=st.number_input('Estoque', min_value=0, value=int(p.get('stock',0)), step=1, key='edit_prod_estoque_'+p['id'])
      nova_comissao=st.number_input('Comissão %', min_value=0.0, value=float(p.get('commissionRate',db['commissionRate'])), step=.5, key='edit_prod_comissao_'+p['id'])
      salvar=st.form_submit_button('Salvar edição')
      cancelar=st.form_submit_button('Cancelar')

     if salvar:
      repetido=False
      for outro in db['products']:
       if outro['id']!=p['id'] and normalizar(outro.get('name',''))==normalizar(novo_nome):
        repetido=True

      if repetido:
       st.error('Já existe outro produto com esse nome.')
      else:
       p['name']=novo_nome
       p['category']=nova_cat
       p['supplier']=novo_forn
       p['price']=novo_preco
       p['stock']=novo_estoque
       p['commissionRate']=nova_comissao
       save_db(db)
       st.session_state.pop('editando_produto', None)
       st.rerun()

     if cancelar:
      st.session_state.pop('editando_produto', None)
      st.rerun()

def more_page(db):
 st.subheader('☰ Mais')
 if st.button('Sair', key='btn_sair'): st.session_state.clear(); st.rerun()
 if st.session_state.role!='admin': return

 st.markdown('### Vendedores')
 with st.expander('Cadastrar vendedor'):
  with st.form('sales'):
   n=st.text_input('Nome', key='vend_nome')
   em=st.text_input('E-mail', key='vend_email')
   cpf=st.text_input('CPF', key='vend_cpf')
   ph=st.text_input('Telefone', key='vend_tel')
   pw=st.text_input('Senha',value='123', key='vend_senha')
   if st.form_submit_button('Salvar vendedor') and n:
    email_repetido=any(normalizar(v.get('email',''))==normalizar(em) and em for v in db['salespeople'])
    if email_repetido:
     st.error('Já existe vendedor com esse e-mail.')
    else:
     db['salespeople'].append({'id':uid('sales'),'name':n,'email':em,'active':True,'cpf':cpf,'phone':ph,'address':'','password':pw,'passwordIsTemporary':False})
     save_db(db); st.rerun()

 for s in db['salespeople']:
  with st.expander(f"{s['name']} — {s['email']} — {'Ativo' if s.get('active') else 'Inativo'}"):
   st.write('CPF:', s.get('cpf',''))
   st.write('Telefone:', s.get('phone',''))

   col1,col2,col3=st.columns(3)
   editar=col1.button('Editar', key='edit_vend_'+s['id'])
   if col2.button('Ativar/Inativar', key='a'+s['id']):
    s['active']=not s.get('active')
    save_db(db)
    st.rerun()
   excluir=col3.button('Excluir', key='del_vend_'+s['id'])

   if excluir:
    usado=any(o.get('salespersonId')==s.get('id') for o in db.get('orders',[]))
    if usado:
     st.error('Não é possível excluir: esse vendedor possui pedidos cadastrados.')
    else:
     db['salespeople']=[x for x in db['salespeople'] if x['id']!=s['id']]
     save_db(db)
     st.rerun()

   if editar or st.session_state.get('editando_vendedor')==s['id']:
    st.session_state['editando_vendedor']=s['id']
    with st.form('form_edit_vendedor_'+s['id']):
     novo_nome=st.text_input('Nome', value=s.get('name',''), key='edit_vend_nome_'+s['id'])
     novo_email=st.text_input('E-mail', value=s.get('email',''), key='edit_vend_email_'+s['id'])
     novo_cpf=st.text_input('CPF', value=s.get('cpf',''), key='edit_vend_cpf_'+s['id'])
     novo_tel=st.text_input('Telefone', value=s.get('phone',''), key='edit_vend_tel_'+s['id'])
     nova_senha=st.text_input('Senha', value=s.get('password','123'), key='edit_vend_senha_'+s['id'])
     ativo=st.checkbox('Ativo', value=bool(s.get('active',True)), key='edit_vend_ativo_'+s['id'])
     salvar=st.form_submit_button('Salvar edição')
     cancelar=st.form_submit_button('Cancelar')

    if salvar:
     email_repetido=False
     for outro in db['salespeople']:
      if outro['id']!=s['id'] and normalizar(outro.get('email',''))==normalizar(novo_email) and novo_email:
       email_repetido=True

     if email_repetido:
      st.error('Já existe outro vendedor com esse e-mail.')
     else:
      s['name']=novo_nome
      s['email']=novo_email
      s['cpf']=novo_cpf
      s['phone']=novo_tel
      s['password']=nova_senha
      s['active']=ativo
      save_db(db)
      st.session_state.pop('editando_vendedor', None)
      st.rerun()

    if cancelar:
     st.session_state.pop('editando_vendedor', None)
     st.rerun()

 st.markdown('### Comissão')
 rate=st.number_input('Comissão geral %',min_value=0.0,value=float(db['commissionRate']),step=.5,key='comissao_geral')
 if st.button('Salvar comissão', key='btn_salvar_comissao'): db['commissionRate']=rate; save_db(db); st.success('Salvo')

 st.markdown('### Backup / Importação')
 st.download_button('Baixar backup JSON', data=json.dumps(db,ensure_ascii=False,indent=2).encode('utf-8'), file_name='tigrao_backup.json', key='download_backup_json')
 sheets={'produtos':pd.DataFrame(db['products']),'clientes':pd.DataFrame(db['clients']),'vendedores':pd.DataFrame(db['salespeople']),'pedidos':pd.DataFrame(db['orders'])}
 out=BytesIO()
 with pd.ExcelWriter(out,engine='openpyxl') as writer:
  for k,v in sheets.items(): v.to_excel(writer,index=False,sheet_name=k)
 st.download_button('Exportar Excel', data=out.getvalue(), file_name='tigrao_export.xlsx', key='download_excel')
 up=st.file_uploader('Importar backup JSON', type=['json'], key='upload_backup_json')
 if up and st.button('Importar agora', key='btn_importar_backup'):
  new=json.loads(up.read().decode('utf-8')); save_db(new); st.success('Importado'); st.rerun()
 col1,col2=st.columns(2)
 if col1.button('Restaurar exemplo', key='btn_restaurar_exemplo'): save_db(seed()); st.rerun()
 if col2.button('Limpar banco', key='btn_limpar_banco'): save_db({'app':'Tigrão Distribuidora','systemName':'TIGRÃO','commissionRate':7,'products':[],'clients':[],'salespeople':INITIAL_SALES[:1],'orders':[]}); st.rerun()

css(); db=load_db()
if 'auth' not in st.session_state: st.session_state.auth=False
if 'tab' not in st.session_state: st.session_state.tab='dashboard'
if not st.session_state.auth: login(db); st.stop()
header(db); nav()
{'dashboard':dashboard,'newOrder':new_order,'orders':orders_page,'clients':clients_page,'products':products_page,'more':more_page}[st.session_state.tab](db)
