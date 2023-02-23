#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import seaborn as sns


# 
# # Upload de tabelas

# In[8]:


#df0 = base crua, recém extraída
#df  = base manipulada com criação de colunas 
#df1 = base de verificações estatísticas
#df2 = base para aprendizado

df0 = pd.read_excel('base_crua.xlsx')
#df0.dtypes
#df0.head(2)


# In[21]:


# Bases de variação de acessos e lojas

# O ifood permite que o mesmo acesso gerencie diversos restaurantes. Dados de acesso são inputados em dois arquivos colaborativos no Google Drive


df_senhas = pd.read_excel(r'G:\Meu Drive\Dgrowth\Igrowth\Scripts\base_clientes.xlsx', sheet_name = 'Acessos')
#df_acessos = pd.read_excel(r'G:\.shortcut-targets-by-id\1AbfWV8EXGuVrNv2sW5VAQivaY9qitEnB\Igrowth\Scripts\base_clientes.xlsx', sheet_name = 'Lojas')

k1 = 0          #identifica em que linha está na base de acessos
k2 = 0          #identifica em que linha está na base de LOJAS


# # Classificando os dados
# 
# 1   ID DO PEDIDO: número de identificação único para cada pedido         (obj) 
# 
# 2   Nº DO PEDIDO: nº do pedido nem um determinado período de tempo       (obj)
# 
# 3   DATA: data do pedido                                                 (date)
# 
# 4   RESTAURANTE: nome do restaurante do qual o pedido foi feito          (obj)          # pode ser mutável
# 
# 5   ID DO RESTAURANTE número de referência único para cada restaurante   (obj)
# 
# 6   TAXA DE ENTREGA: Valor pago pelo restaurante para o ifood            (int)          # pode ser negativo 
# 
# 7   VALOR DOS ITENS: Total pago pelo cliente                             (int)
# 
# 8   INCENTIVO PROMOCIONAL IFOOD: Valor pago po ifood em promoções        (int)
# 
# 9   INCENTIVO PROMOCIONAL DA LOJA: Valor pago pela loja em promoções     (int)
# 
# 10  TAXA DE SERVIÇO: Taxa de serviço cobrada pelo ifood                  (int)
# 
# 11  TOTAL DO PARCEIRO: Total a ser recebido pelo restaurante             (int)          # constantemente errado
# 
# 12  TOTAL DO PEDIDO: Valor pago pelo cliente                             (int)
# 
# 13  FORMAS DE PAGAMENTO: Tipo de pagamento                               (obj)
# 
# 14  DATA DO CANCELAMENTO: Data em que o pedido foi cancelado             (date)
# 
# 15  ORIGEM DO CANCELAMENTO: responsável pelo cancelamento                (obj)    
# 
# 16  MOTIVO DO CANCELAMENTO: Motivos padrão                               (obj)
# 
# 17  CANCELAMENTO É CONTESTÁVEL?:                                         (obj)         #constantemente errado
# 
# 18  MOTIVO DA IMPOSSIBILIDADE DE CONTESTAR:                              (obj)         #constantemente errado
# 
# 19  DATA LIMITE DE CONTESTAÇÃO:                                          (obj)         #constantemente variável
# 
# 20  CONFIRMADO: Status do pedido                                         (obj)
# 
# 21  DATA DO AGENDAMENTO:                                                 (date)
# 
# 22  TIPO DE PEDIDO: Variação entre entrega e retirada no local           (obj)
# 
# 23  AGENDADO:                                                            (date)
# 
# 24  CANAL DE VENDA:                                                      (obj)
# 
# 25  TEM CANCELAMENTO PARCIAL:                                            (obj)

# # Normatizando e corrigindo tabelas

# In[5]:


# Ajustando formato de dados

# Criando colunas de datas isoladas e ajustando a variável 'DATA'
df = df0
df['DATA'] = pd.to_datetime(df['DATA'])
df['YEAR'] = (df['DATA'].dt.year)
df['MONTH'] = (df['DATA'].dt.month)
df['DAY'] = (df['DATA'].dt.day)

# Definindo a coluna de data no índica do df
df.set_index('DATA', inplace = True)


# In[8]:


# Ajustar formatos num novo dataframe

# Substituir colunas numeric
df[['TAXA DE ENTREGA','VALOR DOS ITENS', 'INCENTIVO PROMOCIONAL DO IFOOD','INCENTIVO PROMOCIONAL DA LOJA','TAXA DE SERVIÇO','TOTAL DO PARCEIRO','TOTAL DO PEDIDO']].apply(pd.to_numeric)

# Substituir colunas object 
df[['ID DO PEDIDO', 'N° PEDIDO', 'RESTAURANTE', 'ID DO RESTAURANTE', 'FORMAS DE PAGAMENTO', 'ORIGEM DO CANCELAMENTO', 'MOTIVO DO CANCELAMENTO', 'CANCELAMENTO É CONTESTÁVEL', 'MOTIVO DA IMPOSSIBILIDADE DE CONTESTAR', 'CONFIRMADO','TIPO DE PEDIDO', 'AGENDADO','CANAL DE VENDA', 'TEM CANCELAMENTO PARCIAL']].astype(object)
                
# Substituir colunas date
df[['DATA DO CANCELAMENTO','DATA LIMITE DE CONTESTAÇÃO','DATA DE AGENDAMENTO']].apply(pd.to_datetime)

#df.dtypes
df.head(2)


# In[9]:


# Análise de vazios

na_tot = df.isnull().sum().sort_values(ascending=False)
na_perc = ((df.isna().sum()/df.shape[0]).sort_values(ascending=False)).round(4)*100
na = pd.DataFrame({"na_+":na_tot, "na_%":na_perc})
print(na)

# foi verificado em análises anteriores a presença de linhas duplicadas
#df = df.drop_duplicates()


# ## Estruturação de faturamentos (Bruto e Líquido)
# 

# O faturamento obrito na plataforma não é o faturamneto real do restaurante.                             
# Diversas taxas só são aplicadas nos últimos cálculos de repasse da plataforma, impossibilitando a auditoria de valores.                                                                            
# 
# #### Variações encontradas no cálculo de faturamentos (Bruto e Líquido)                      
# Taxa de serviço................................................(taxa fixa estável)                     
# Taxa de 1 semana...............................................(taxa de repasse da plataforma)                                  
# Taxa forma de pagamento......................................(taxa variável relacionada à forma de pagamento)                                                             
# Valor de cancelamentos.........................................(taxa variável por tipo de cancelamento)                                                         
# Valore de incentivo do restaurante.............................(taxa variável por presença em promoções)                                                     
# Taxa "padrão"..................................................(taxa fixa dependente da negociação com a plataforma)                                                                                         
# Valores por taxa de entrega....................................(valor cobrado pela plataforma quando a entrega é por logística ifood)

# In[28]:


# Criaremos a "TAXA EXTRA" para identificar o somatório das taxas

# Taxa de serviço é um valor fixo localizado na base de dados [k1]
#df['TAXA DE SERVIÇO'] = df_senhas['TAXA'][k1]
# Taxa de repasse é um valor variável na negociação com a plataforma de acordo com o período para repasse
#df['TAXA EXTRA'] = (df_senhas['TAXA DE TRANSAÇÃO'][k1] + df_senhas['TAXA DE 1 SEMANA'][k1])/100


# # Aqui começa o caos_______________________________

# In[31]:


# Taxa de forma de pagamento
# Criando um df paralelo para normatizar tipos de pagamento

fdp00 = {
    'Forma de pagamento': ['Vale-refeição (Sodexo) via loja',
                           'Vale-refeição (Ifood meal voucher) Merchant ifood beneficios',
                           'Vale-refeição (VR Benefícios) via loja',
                           'Vale-refeição (Alelo) via loja',
                           'Vale-refeição (Alelo refeição) via loja',
                           'Vale-refeição (Vr online) via loja',
                           'Vale-refeição (Sodexo refeição) via adquirente da loja',
                           'Vale-refeição (Alelo refeição) via adquirente da loja',
                           'Vale-refeição (VR refeição) via adquirente da loja',
                           'Vale-refeição (Ticket) via adquirente da loja',
                           'Débito (Elo) via loja',
                           'Crédito (Mastercard) via loja',
                           'Débito (Visa) via loja',
                           'Crédito (Visa) via loja',
                           'Débito (Mastercard) via loja',
                           'Crédito (Elo) via loja'
                          ],
    'Taxa de transação': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'Taxa extra': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'Taxa de serviço': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
}

# Criando o DataFrame a partir do dicionário de dados
fdp0 = pd.DataFrame(fdp00)


# In[32]:


# Valor de cancelamento
# identificando o tipo de entrega na base 'df_senhas' e calculando o total do pedido em df

df.loc[df['DATA DO CANCELAMENTO'].isnull(), 0] = 1
    if df_senhas['ENTREGA PARCEIRA'][k1] == 'NÃO':
        df['TOTAL DO PEDIDO'] = df['VALOR DOS ITENS'] + df['TAXA DE ENTREGA'] + df['TAXA DE SERVIÇO']
    else:
        df['TOTAL DO PEDIDO'] = df['VALOR DOS ITENS']


# In[37]:


# Incentivo promocional do Ifood e do Restaurante


# In[ ]:


# Taxa de Transação e Taxa de 1 semana

df['VALOR DE TAXA DE TRANSAÇÃO'] = (df_senhas['TAXA DE TRANSAÇÃO'][k1]*df['TOTAL DO PEDIDO'])/100
df['VALOR DE TAXA DE 1 SEMANA'] = (df_senhas['TAXA DE 1 SEMANA'][k1]*df['TOTAL DO PEDIDO'])/100


# In[ ]:


# Base de cálculo e Faturamento líquido

i = 0 
df['BASE DE CALCULO'] = 0
df['FATURAMENTO'] = 0

for item in df['TOTAL DO PEDIDO']:
    df['BASE DE CALCULO'][i] = df['TOTAL DO PEDIDO'][i] - df['INCENTIVO PROMOCIONAL DO IFOOD'][i]
    df['FATURAMENTO'][i] = df['BASE DE CALCULO'][i] - df['TAXA EXTRA'][i]*df['BASE DE CALCULO'][i] - df['TAXA DE SERVIÇO'][i]*df['BASE DE CALCULO'][i]
    
    
    #_____________________?___________________#
            j = 0
        try:
            for item in df['FATURAMENTO']:
                if (df['Aux'][j] != 1):
                    df['FATURAMENTO'][j] = df['FATURAMENTO'][j]*(-1) 
                j = j + 1
                
                
Faturamento = df[['DATA', 'RESTAURANTE', 'TOTAL DO PEDIDO', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['VALOR DOS ITENS'] = df[['DATA', 'RESTAURANTE', 'VALOR DOS ITENS', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['INCENTIVO IFOOD'] = df[['DATA', 'RESTAURANTE', 'INCENTIVO PROMOCIONAL DO IFOOD', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['INCENTIVO LOJA'] = df[['DATA', 'RESTAURANTE', 'INCENTIVO PROMOCIONAL DA LOJA', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['FATURAMENTO LÍQUIDO'] = df[['DATA', 'RESTAURANTE', 'FATURAMENTO', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['VALOR DE TAXA DE TRANSAÇÃO'] = df[['DATA', 'RESTAURANTE', 'VALOR DE TAXA DE TRANSAÇÃO', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['VALOR DE TAXA DE 1 SEMANA'] = df[['DATA', 'RESTAURANTE', 'VALOR DE TAXA DE 1 SEMANA', 'MÊS', 'ANO', 'DIA']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['NÚMERO DE PEDIDOS'] = df[['DATA', 'RESTAURANTE', 'MÊS', 'ANO', 'DIA', 'Aux']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).count()
        Faturamento['NÚMERO DE CANCELAMENTOS'] = df[['DATA', 'RESTAURANTE', 'MÊS', 'ANO', 'DIA', 'Aux']].groupby(['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA']).sum()
        Faturamento['NÚMERO DE CANCELAMENTOS'] = Faturamento['NÚMERO DE PEDIDOS'] - Faturamento['NÚMERO DE CANCELAMENTOS']
        Faturamento = Faturamento.reset_index(level = ['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA'])


# In[ ]:


k = df[['DATA', 'RESTAURANTE', 'Aux', 'FATURAMENTO', 'VALOR DOS ITENS', 'TOTAL DO PEDIDO']].loc[df['Aux'] != 1 ].groupby(['RESTAURANTE', 'DATA']).sum()
 k = k.reset_index(level = ['DATA', 'RESTAURANTE'])

 Faturamento['VALOR BRUTO CANCELADO NA PLATAFORMA'] = 0
 Faturamento['VALOR LÍQUIDO CANCELADO NA PLATAFORMA'] = 0
 i = 0
 j = 0
 try:
     for Loja in Faturamento['RESTAURANTE']: 
         if (k['DATA'][i] == Faturamento['DATA'][j])&(k['RESTAURANTE'][i] == Faturamento['RESTAURANTE'][j]):
             Faturamento['VALOR LÍQUIDO CANCELADO NA PLATAFORMA'][j] = k['FATURAMENTO'][i]*(-1)
             Faturamento['VALOR BRUTO CANCELADO NA PLATAFORMA'][j] = k['TOTAL DO PEDIDO'][i]
             i = i + 1
         j = j + 1
 except:
     pass
 df['Aux'] = 0
 df.loc[df['DATA DO CANCELAMENTO'].isnull(), 'Aux'] = 1
 df3 = df[['DATA', 'RESTAURANTE', 'TAXA DE ENTREGA']].groupby(['RESTAURANTE', 'DATA']).sum()
 df3 = df3.reset_index(level = ['RESTAURANTE', 'DATA'])
 df4 = df[['DATA', 'RESTAURANTE', 'VALOR DOS ITENS']].groupby(['RESTAURANTE', 'DATA']).sum()
 df4 = df4.reset_index(level = ['RESTAURANTE', 'DATA'])
 Faturamento['TAXA DE ENTREGA'] = df3['TAXA DE ENTREGA']
 Faturamento['FATURAMENTO BRUTO'] = df4['VALOR DOS ITENS'] + Faturamento['TAXA DE ENTREGA']
 Faturamento['CANCELAMENTO(%)'] = Faturamento['VALOR LÍQUIDO CANCELADO NA PLATAFORMA']/Faturamento['FATURAMENTO BRUTO']
 x = df[['DATA', 'RESTAURANTE', 'VALOR DOS ITENS', 'FATURAMENTO', 'ORIGEM DO CANCELAMENTO', 'Aux']].loc[((df['ORIGEM DO CANCELAMENTO'] =='CONSUMER')|(df['ORIGEM DO CANCELAMENTO'] =='cliente')|(df['ORIGEM DO CANCELAMENTO'] =='CONSUMER_VIA_OPERATION')|(df['ORIGEM DO CANCELAMENTO'] =='Cliente vía operação'))].groupby([ 'RESTAURANTE', 'DATA']).sum('VALOR DOS ITENS')
 x = x.reset_index(level = ['RESTAURANTE', 'DATA'])
 Faturamento['CANCELAMENTO PELO CLIENTE'] = 0
 i = 0
 j = 0
 try:
     for loja in Faturamento['RESTAURANTE']: 
         if (x['DATA'][i] == Faturamento['DATA'][j])&(x['RESTAURANTE'][i] == Faturamento['RESTAURANTE'][j]):
             Faturamento['CANCELAMENTO PELO CLIENTE'][j] = x['FATURAMENTO'][i]*(-1)
             i = i + 1
         j = j + 1
 except: 
     pass
 Faturamento['CANCELAMENTO PELO CLIENTE (%)'] = Faturamento['CANCELAMENTO PELO CLIENTE']/Faturamento['VALOR LÍQUIDO CANCELADO NA PLATAFORMA']
 x = df[['DATA', 'RESTAURANTE', 'VALOR DOS ITENS', 'FATURAMENTO', 'ORIGEM DO CANCELAMENTO', 'Aux']].loc[((df['ORIGEM DO CANCELAMENTO'] !='CONSUMER')&(df['ORIGEM DO CANCELAMENTO'] !='cliente')&(df['ORIGEM DO CANCELAMENTO'] !='CONSUMER_VIA_OPERATION')&(df['ORIGEM DO CANCELAMENTO'] !='Cliente vía operação')&(df['Aux'] == 0))].groupby([ 'RESTAURANTE', 'DATA']).sum('VALOR DOS ITENS')
 x = x.reset_index(level = ['RESTAURANTE', 'DATA'])
 Faturamento['CANCELAMENTO PELO RESTAURANTE'] = 0
 i = 0
 j = 0
 for loja in Faturamento['RESTAURANTE']:
     try:
         if (x['DATA'][i] == Faturamento['DATA'][j])&(x['RESTAURANTE'][i] == Faturamento['RESTAURANTE'][j]):
             Faturamento['CANCELAMENTO PELO RESTAURANTE'][j] = x['FATURAMENTO'][i]*(-1)
             i = i + 1
         j = j + 1
     except:
         pass
 Faturamento['CANCELAMENTO PELO RESTAURANTE (%)'] = Faturamento['CANCELAMENTO PELO RESTAURANTE']/Faturamento['VALOR LÍQUIDO CANCELADO NA PLATAFORMA']
 Faturamento['FATURAMENTO REAL'] = Faturamento['FATURAMENTO LÍQUIDO'] - Faturamento['INCENTIVO LOJA'] 
 Faturamento['TICKET MÉDIO'] = Faturamento['FATURAMENTO BRUTO']/Faturamento['NÚMERO DE PEDIDOS']
 Faturamento['TICKET MÉDIO REAL'] = Faturamento['FATURAMENTO LÍQUIDO']/Faturamento['NÚMERO DE PEDIDOS']
 Faturamento['INCENTIVO (%)'] = Faturamento['INCENTIVO LOJA']/Faturamento['FATURAMENTO BRUTO']
 Faturamento['TAXA EFETIVA'] = (1 - (Faturamento['FATURAMENTO REAL']/Faturamento['FATURAMENTO BRUTO']))
 Faturamento['MARGEM'] = Faturamento['FATURAMENTO REAL']/Faturamento['FATURAMENTO BRUTO']
 Faturamento['TAXA DE CANCELAMENTO'] = Faturamento['NÚMERO DE CANCELAMENTOS']/Faturamento['NÚMERO DE PEDIDOS']
 loja = df2['LOJAS'][k2]
 Faturamento['RESTAURANTE'] = loja
 sleep(10)
 os.remove(r'C:\Users\Matheus Costa\Downloads\lista-de-pedidos.xlsx')
    except:
 Faturamento = pd.DataFrame(columns = ['RESTAURANTE', 'DATA', 'MÊS', 'ANO', 'DIA', 'TOTAL DO PEDIDO',
'VALOR DOS ITENS', 'INCENTIVO IFOOD', 'INCENTIVO LOJA',
'FATURAMENTO LÍQUIDO', 'VALOR DE TAXA DE TRANSAÇÃO',
'VALOR DE TAXA DE 1 SEMANA', 'VALOR BRUTO CANCELADO NA PLATAFORMA',
'VALOR LÍQUIDO CANCELADO NA PLATAFORMA', 'NÚMERO DE CANCELAMENTOS',
'TAXA DE ENTREGA', 'FATURAMENTO BRUTO', 'CANCELAMENTO(%)',
'CANCELAMENTO PELO CLIENTE', 'CANCELAMENTO PELO CLIENTE (%)',
'CANCELAMENTO PELO RESTAURANTE', 'CANCELAMENTO PELO RESTAURANTE (%)',
'FATURAMENTO REAL', 'NÚMERO DE PEDIDOS', 'TICKET MÉDIO',
'TICKET MÉDIO REAL', 'INCENTIVO (%)', 'TAXA EFETIVA', 'MARGEM',
'TAXA DE CANCELAMENTO', 'NPS MÉDIO', 'NÚMERO DE COMENTÁRIOS',
'NÚMERO DE AVALIAÇÕES'] )
 Faturamento['DATA'] = [ontem]


# In[45]:


# O banco de dados alimentado em um mês tem o seguinte resultado

df1_financeiro = pd.read_excel('base_git.xlsx', sheet_name = 'Finalidade' )
df1_avaliações = pd.read_excel('base_git.xlsx', sheet_name = 'Avaliações' )
df1_disponibilidade = pd.read_excel('base_git.xlsx', sheet_name = 'Disponibilidade' )
df1_listas = pd.read_excel('base_git.xlsx', sheet_name = 'Listas' )
df1_metas = pd.read_excel('base_git.xlsx', sheet_name = 'Metas' )
df1_promo = pd.read_excel('base_git.xlsx', sheet_name = 'Promo' )
df1_tempo = pd.read_excel('base_git.xlsx', sheet_name = 'Tempo' )

df1_financeiro.head(2)


# ## Novas colunas criadas
# 
# 1. 
# 2. 
# 3. 

# # Analisando correlações estatísticas
# 

# 1. Análise de faturamentos para gerar faturamento real

# In[ ]:





# # Visualizações iniciais

# In[ ]:




