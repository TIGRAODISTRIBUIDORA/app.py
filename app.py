import json, os, uuid
from datetime import datetime
from io import BytesIO
import pandas as pd
import streamlit as st

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
 {'id':'cli-1','name':'nelson das galaxie','document':'123.456.789-00','email':'nelson@galaxie.com','phone':'(11) 98888-7777','city':'São Paulo','state':'SP'},
 {'id':'cli-2','name':'Distribuidora Silva & Silva','document':'98.765.432/0001-11','email':'silva@distribuidora.com','phone':'(11) 3245-8899','city':'Campinas','state':'SP'},
 {'id':'cli-3','name':'Mercadinho do Bairro Ltda','document':'45.123.789/0001-44','email':'contato@mercadinhobairro.com','phone':'(21) 97777-6666','city':'Rio de Janeiro','state':'RJ'},
 {'id':'cli-4','name':'Adega Central','document':'55.666.777/0001-88','email':'adega.central@outlook.com','phone':'(19) 99122-3344','city':'Piracicaba','state':'SP'},
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

def normalizar(txt):
 txt=str(txt or '').lower().strip()
 troca={'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c'}
 for a,b in troca.items():
  txt=txt.replace(a,b)
 return txt

def comeca_com(texto, busca):
 busca=normalizar(busca)
 texto=normalizar(texto)
 if not busca:
  return True
 partes=texto.replace('-',' ').replace('/',' ').replace('.',' ').replace(',',' ').split()
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

 with st.form('order_form'):
  busca_cliente=st.text_input('Pesquisar cliente', key='pedido_busca_cliente', placeholder='Digite as primeiras letras do cliente')
  clientes_filtrados=sugestoes_inicio(clients, ['name','document','city','phone'], busca_cliente, limite=20) if busca_cliente else clients[:20]
  if not clientes_filtrados:
   clientes_filtrados=clients[:1]
   st.warning('Nenhum cliente encontrado. Cadastre o cliente ou ajuste a pesquisa.')

  c=st.selectbox('Cliente', clientes_filtrados, format_func=lambda x:f"{x['name']} — {x['document']}", key='pedido_cliente')

  if st.session_state.role=='admin':
   s=st.selectbox('Vendedor', [x for x in sales if x.get('active')], format_func=lambda x:x['name'], key='pedido_vendedor')
  else:
   s=next(x for x in sales if x['id']==st.session_state.sales_id)

  st.write('Produtos')
  items=[]

  for i in range(1,7):
   busca_prod=st.text_input(f'Pesquisar produto {i}', key=f'busca_p{i}', placeholder='Digite código, nome, fornecedor ou categoria')
   produtos_filtrados=sugestoes_inicio(products, ['sku','name','supplier','category'], busca_prod, limite=20) if busca_prod else products[:20]

   if not produtos_filtrados:
    st.warning(f'Produto {i}: nenhuma sugestão encontrada.')
    produtos_filtrados=[]

   col1,col2=st.columns([3,1])
   p=col1.selectbox(
    f'Produto {i}',
    [None]+produtos_filtrados,
    format_func=lambda x:'Selecione' if x is None else f"{x['sku']} - {x['name']} ({money(x['price'])})",
    key=f'p{i}'
   )
   q=col2.number_input('Qtd', min_value=0, step=1, key=f'q{i}')

   if p and q>0:
    items.append({'productId':p['id'],'productName':p['name'],'quantity':int(q),'price':float(p['price']),'commissionRate':p.get('commissionRate',db['commissionRate'])})

  salvar=st.form_submit_button('Salvar pedido')

 if salvar:
  if not items:
   st.error('Adicione pelo menos 1 produto')
  else:
   total=sum(it['quantity']*it['price'] for it in items); rate=float(db['commissionRate']); maxnum=max([o['orderNumber'] for o in db['orders']], default=-1)+1
   db['orders'].insert(0,{'id':uid('ord'),'orderNumber':maxnum,'date':datetime.now().isoformat(timespec='seconds'),'salespersonId':s['id'],'salespersonName':s['name'],'clientId':c['id'],'clientName':c['name'],'items':items,'total':total,'commissionRate':rate,'commissionAmount':round(total*rate/100,2),'status':'Pendente'})
   for it in items:
    for p in db['products']:
     if p['id']==it['productId']:
      p['stock']=max(0,int(p.get('stock',0))-it['quantity'])
   save_db(db); st.success('Pedido salvo com sucesso'); st.session_state.tab='orders'; st.rerun()

def orders_page(db):
 st.subheader('📦 Pedidos')
 busca=st.text_input('Pesquisar pedido, cliente ou vendedor por início', key='busca_pedidos')
 for o in sorted(filtered_orders(db),key=lambda x:x['orderNumber'],reverse=True):
  campos=[o.get('orderNumber',''),o.get('clientName',''),o.get('salespersonName',''),o.get('status','')]
  if busca and not combina_inicio(campos, busca):
   continue
  with st.expander(f"#{o['orderNumber']} — {o['clientName']} — {money(o['total'])} — {o['status']}"):
   st.write('Vendedor:',o['salespersonName']); st.write('Data:',o['date'])
   st.dataframe(pd.DataFrame(o['items']), use_container_width=True, hide_index=True)
   st.write('Comissão:', money(o.get('commissionAmount',0)))
   if st.session_state.role=='admin':
    ns=st.selectbox('Status', STATUS, index=STATUS.index(o['status']), key='st'+o['id'])
    col1,col2=st.columns(2)
    if col1.button('Atualizar', key='up'+o['id']): o['status']=ns; save_db(db); st.rerun()
    if col2.button('Excluir pedido', key='del'+o['id']): db['orders']=[x for x in db['orders'] if x['id']!=o['id']]; save_db(db); st.rerun()

def clients_page(db):
 st.subheader('👥 Clientes')
 with st.expander('Cadastrar cliente'):
  with st.form('cli'):
   n=st.text_input('Nome', key='cliente_nome'); doc=st.text_input('CPF/CNPJ', key='cliente_doc'); em=st.text_input('E-mail', key='cliente_email'); ph=st.text_input('Telefone', key='cliente_tel'); city=st.text_input('Cidade', key='cliente_cidade'); uf=st.text_input('Estado', key='cliente_estado')
   if st.form_submit_button('Salvar cliente') and n:
    db['clients'].insert(0,{'id':uid('cli'),'name':n,'document':doc,'email':em,'phone':ph,'city':city,'state':uf}); save_db(db); st.rerun()

 busca=st.text_input('Pesquisar cliente por iniciais, nome, documento ou cidade', key='busca_clientes')

 if busca:
  encontrados=sugestoes_inicio(db['clients'], ['name','document','city','state','phone'], busca, limite=50)
  if encontrados:
   st.caption('Sugestões encontradas')
  else:
   st.warning('Nenhum cliente encontrado com esse início.')
 else:
  encontrados=db['clients']

 for c in encontrados:
  st.markdown(f'<div class="card"><b>{c["name"]}</b><br>{c["document"]}<br>{c["phone"]} • {c["city"]}/{c["state"]}</div>', unsafe_allow_html=True)

def products_page(db):
 st.subheader('🛒 Produtos')

 if st.session_state.role=='admin':
  with st.expander('Cadastrar produto'):
   with st.form('prod'):
    sku=st.text_input('Código/SKU', key='prod_sku')
    n=st.text_input('Nome', key='prod_nome')
    cat=st.text_input('Categoria', key='prod_categoria')
    supplier=st.text_input('Fornecedor', key='prod_fornecedor')
    price=st.number_input('Preço',min_value=0.0,step=.01,key='prod_preco')
    stock=st.number_input('Estoque',min_value=0,step=1,key='prod_estoque')
    cr=st.number_input('Comissão %',min_value=0.0,value=float(db['commissionRate']),step=.5,key='prod_comissao')

    if st.form_submit_button('Salvar produto') and n:
     db['products'].insert(0,{'id':uid('prod'),'name':n,'sku':sku,'price':price,'stock':stock,'category':cat,'supplier':supplier,'commissionRate':cr})
     save_db(db)
     st.rerun()

 fornecedores = sorted(list(set([p.get('supplier','Sem fornecedor') or 'Sem fornecedor' for p in db['products']])))
 fornecedor_filtro = st.selectbox('Filtrar por fornecedor', ['Todos'] + fornecedores, key='filtro_fornecedor_produtos')

 busca=st.text_input('Pesquisar produto por iniciais, código, nome, categoria ou fornecedor', key='busca_produtos')

 produtos_filtrados=[]
 for p in db['products']:
  fornecedor_produto = p.get('supplier','Sem fornecedor') or 'Sem fornecedor'

  if fornecedor_filtro != 'Todos' and fornecedor_produto != fornecedor_filtro:
   continue

  if busca and not combina_inicio([p.get('sku',''),p.get('name',''),p.get('category',''),fornecedor_produto], busca):
   continue

  produtos_filtrados.append(p)

 if busca and not produtos_filtrados:
  st.warning('Nenhum produto encontrado com esse início.')
 elif busca:
  st.caption('Sugestões encontradas')

 for p in produtos_filtrados:
  fornecedor_produto = p.get('supplier','Sem fornecedor') or 'Sem fornecedor'
  st.markdown(f'<div class="card"><b>{p["sku"]} — {p["name"]}</b><br>{p["category"]}<br>Fornecedor: {fornecedor_produto}<br><h3>{money(p["price"])}</h3>Estoque: {p["stock"]} • Comissão: {p.get("commissionRate",db["commissionRate"])}%</div>', unsafe_allow_html=True)

def more_page(db):
 st.subheader('☰ Mais')
 if st.button('Sair', key='btn_sair'): st.session_state.clear(); st.rerun()
 if st.session_state.role!='admin': return
 st.markdown('### Vendedores')
 with st.expander('Cadastrar vendedor'):
  with st.form('sales'):
   n=st.text_input('Nome', key='vend_nome'); em=st.text_input('E-mail', key='vend_email'); cpf=st.text_input('CPF', key='vend_cpf'); ph=st.text_input('Telefone', key='vend_tel'); pw=st.text_input('Senha',value='123', key='vend_senha')
   if st.form_submit_button('Salvar vendedor') and n:
    db['salespeople'].append({'id':uid('sales'),'name':n,'email':em,'active':True,'cpf':cpf,'phone':ph,'address':'','password':pw,'passwordIsTemporary':False}); save_db(db); st.rerun()
 for s in db['salespeople']:
  col1,col2=st.columns([3,1]); col1.write(f"**{s['name']}** — {s['email']} — {'Ativo' if s.get('active') else 'Inativo'}")
  if col2.button('Ativar/Inativar', key='a'+s['id']): s['active']=not s.get('active'); save_db(db); st.rerun()
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
