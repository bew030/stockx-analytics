#!/usr/bin/env python
# coding: utf-8

# In[176]:


import imaplib
import numpy as np
import pandas as pd
import email
from datetime import datetime
import getpass


# In[ ]:


# methods 
def login(email,password):
    '''
    Method used to login to email with orders. Requires email and password in string format. ONLY GMAIL CURRENTLY WORKS
    Email should primarily be filled with forwarded emails (forwarded from main source, all emails going to this email
    would lead to suspicions of multiple orders)
    parameters: email (string representation of email, includes @__.com), password (string representation of password)
    returns: string that shows whether login was successful or not 
    '''
    smtp_server = "imap.gmail.com"
    smtp_port = 993 
    mail = imaplib.IMAP4_SSL(smtp_server)
    result, authentification = mail.login(email, password)
    print('Login: '+result)
    return mail

def get_emails(mail):
    '''
    Method used to get the email body of ALL emails in inbox. Requires the mail object created from the login method. 
    parameters: mail (an imaplib.IMAP4_SSL object, created from login)
    returns: email_bodies (a list of the raw text of the bodies of all the emails)
    '''
    status, messages = mail.select('INBOX') 
    result, data = mail.uid('search', None, "ALL")
    email_uids = latest_email_uid = data[0].split()
    email_bodies = []
    for i in email_uids:
        result, data = mail.uid('fetch', i, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        if email_message.is_multipart():
            email_bodies.append(email_message.get_payload()[0].get_payload())
        else:
            email_bodies.append(email_message.get_payload())
    return email_bodies

# prepped up for supreme, stockx, and adidas 
def order_df_creator(email_bodies):
    '''
    Method that creates a df from the raw email bodies. 
    parameters: email_bodies (a list of raw text of the bodies of all emails you're trying to make a df from)
    returns: df (dataframe of orders; includes Date, Source, Order #, Item, Size, and Price)
    
    IMPROVEMENTS: needs to be able to read items that are not forwarded emails, does NOT deal with foot sites, 
    currently still does not support stockx and adidas and nike orders. Also would be more efficient if it didn't have
    to read every email, maybe save previous orders as a csv and just update. 
    '''
    source = [] 
    order = [] 
    item = [] 
    size = [] 
    price = [] 
    date = []
    for i in email_bodies: 
        item_source = i.split('\n')[1].split()[1] # primarily reads forwarded emails 
        if item_source.lower() == 'supreme': # sometimes orders will have more than one item 
            add_order, add_item, add_size, add_price, add_source, add_date = supreme_reader(i)
            '''
        elif item_source.lower() == 'stockx':
            order.append('')
        elif item_source.lower() == 'adidas':
            order.append('')
        elif item_source.lower() == 'nike':
            order.append('')
        else: 
            print('unknown source')
            '''
        source = source + add_source
        order = order + add_order
        item = item + add_item
        size = size + add_size
        price = price + add_price
        date = date + add_date
    df = pd.DataFrame({'Date':date,'Source':source,'Order':order,'Item':item,'Size':size,'Price':price})
    size_subs = {'Small':'S','Medium':'M','Large':'L','XLarge':'XL'}
    df['Size']=[size_subs.get(item,item)  for item in df['Size']]
    return df

def supreme_reader(raw_email):
    '''
    Method for specifically reading Supreme orders. 
    '''
    source = [] 
    date = [] 
    order = [] 
    item_name = [] 
    size = [] 
    price = []
    # important information is split into columns divided by '...'
    dots = np.where(['.......' in x for x in raw_email.split('\n')])[0]
    begin_order = np.where(['order #' in x.lower() for x in raw_email.split('\n')])[0][0]
    items_in_order = [x for x in dots if x>begin_order]
    potential_items = []
    iteration_item = len(items_in_order)-2
    for i in range(iteration_item):
        potential_items.append(raw_email.split('\n')[items_in_order[i]+1:items_in_order[i+1]])    
    cost_info = raw_email.split('\n')[items_in_order[iteration_item]+1:items_in_order[iteration_item+1]]
    shipping_handling_cost = int(cost_info[1].strip().split()[3][1:])
    sales_tax = 0 
    if len(cost_info) == 4: 
        sales_tax = float(cost_info[2].strip().split()[2][1:])
    total_cost = np.round(shipping_handling_cost+sales_tax, decimals = 2)
    additional_cost_per_item = np.round(total_cost/len(potential_items),decimals = 2)
    # comment that you're removing trademark stuff
    for k in potential_items:
        order.append(raw_email.split('\n')[begin_order].split()[1])
        price.append(float(k[-1:][0].split()[1][1:])+additional_cost_per_item)
        source.append('Supreme')
        real_date = datetime.strptime(raw_email.split('\n')[dots[0]+1][:11], '%b %d %Y')
        date.append(real_date)
        if 'skateboard' in k[0].lower():
            item_name.append(k[0].strip().replace('=C2=AE','').replace('=E2=84=A2','')+' '+k[1].split()[len(k[1].split())-1].strip())
            size.append(np.nan)
        else:
            if (k[0].lower()=='shoulder bag\r') or (k[0].lower()=='waist bag\r') or (k[0].lower()=='backpack\r'):
                if (2 <= real_date.month <=7):
                    item_name.append(k[0].strip().replace('=C2=AE','').replace('=E2=84=A2','')+' '+'ss'+str(real_date.year)[-2:]
                                     +' '+k[1].split()[1].strip())
                else:
                    item_name.append(k[0].strip().replace('=C2=AE','').replace('=E2=84=A2','')+' '+'fw'+str(real_date.year)[-2:]
                                     +' '+k[1].split()[1].strip())
            else: 
                item_name.append(k[0].strip().replace('=C2=AE','').replace('=E2=84=A2','')+' '+k[1].split()[1].strip())
            if len(k) == 3:
                size.append(np.nan)
            elif len(k) == 4:
                if (k[2].strip().split()[0] == 'Quantity:'):
                    size.append(np.nan)
                else:
                    size.append(k[2].strip().split()[1])
            else: 
                print('error: CHECK CODE FOR SUPREME')
    return order, item_name, size, price, source, date


# In[197]:


org_email = input()


# In[198]:


from_pwd = getpass.getpass()


# In[199]:


mail = login(org_email,from_pwd)


# In[180]:


email_bodies = get_emails(mail)


# In[206]:


df = order_df_creator(email_bodies)
df


# # STOCKX STUFF

# In[321]:


from stockxsdk import Stockx
from time import sleep


# In[348]:


# methods 

def stockx_df_creator(df):
    item = [] 
    sizes = [] 
    highest_bid = [] 
    lowest_ask = [] 
    failed_items = []
    for i in range(len(df)):
        product_name = df.iloc[i]['Item']
        size = df.iloc[i]['Size']
        interested_product = product_name
        if len(stockx.search(interested_product)) == 0:
            failed_items.append(product_name)
        else:
            interested_product_id = stockx.search(interested_product)[0]['ticker_symbol']
            product_id = stockx.get_first_product_id(interested_product_id)
            print(product_name) # should this be included?
            item.append(product_name)
            sizes.append(size)
            if size != size:
                highest_bid.append(stockx.get_highest_bid(product_id)[0])
                lowest_ask.append(stockx.get_lowest_ask(product_id)[0])
            else:
                highest_bid.append(stockx.get_highest_bid(product_id,size)[0])
                lowest_ask.append(stockx.get_lowest_ask(product_id,size)[0])
    bids_df = pd.DataFrame({'Item':item,'Size':sizes,'Highest Bid':highest_bid,'Lowest Ask':lowest_ask})
    final = pd.merge(df, bids_df, on = ['Item','Size'])
    percentage = (stockx.rewards()['data'][0]['attributes']['lifetime']['rates'][0]['fee'])/100
    transaction = .03 
    final['Payout Highest Bid'] = np.round((1-percentage-transaction)*final['Highest Bid'],2)
    final['Payout Lowest Ask'] = np.round((1-percentage-transaction)*final['Lowest Ask'],2)
    final['Profit Highest Bid'] = final['Payout Highest Bid']-final['Price']
    final['Profit Lowest Ask'] = final['Payout Lowest Ask']-final['Price']
    return final, failed_items

# DOESN'T RETURNED FAILED SEARCHUP LIST YET; FIX THAT SHIT 
def df_converter(df,time_delay = .5):
    length = len(df)
    array_indexes = [20*x for x in range(length//20+1)]
    array_indexes.append(length)
    start, start_failed = stockx_df_creator(df[0:20]) 
    # print(start_failed)
    for i in range(1,len(array_indexes)-1):
        time.sleep(time_delay)
        new, new_failed = stockx_df_creator(df[array_indexes[i]:array_indexes[i+1]])
        start = pd.concat([start,new],ignore_index=True)
        start_failed = start_failed+new_failed
    return start, start_failed

def colorizer(df):
    def highlight_greaterthan_1(s):
        if s['Profit Lowest Ask'] > 0.0:
            return ['background-color: Aquamarine']*12
        else:
            return ['background-color: LightPink']*12

    df = df.style.apply(highlight_greaterthan_1, axis=1)
    return df


# In[322]:


stockx = Stockx()


# In[324]:


email = input()


# In[325]:


password = getpass.getpass()


# In[341]:


stockx.authenticate(email,password)


# In[346]:


final_df, final_failed = df_converter(df)


# In[349]:


colorizer(final_df)


# # STOCKX PURCHASING ANALYSIS

# In[ ]:


def initial_df_creator(string_interest):
    shoes = re.findall('\(([^)]+)\)', shoes_of_interest)
    split_shoes = [x.split(',') for x in shoes]
    shoe_name = [x[0].strip() for x in split_shoes] 
    shoe_size = [x[1].strip() for x in split_shoes] 
    return pd.DataFrame({'Item':shoe_name,'Size':shoe_size})

def stockx_purchase_df_creator(df):
    item = [] 
    stockx_item = [] 
    sizes = [] 
    lowest_ask = [] 
    for i in range(len(df)):
        product_name = df.iloc[i]['Item']
        size = df.iloc[i]['Size']
        if len(stockx.search(product_name)) == 0: 
            item.append('error for '+product_name+'; change name or check if StockX has item')
            stockx_item.append(np.nan)
            sizes.append(size)
            lowest_ask.append(np.nan)
        else: 
            interested_product_id = stockx.search(product_name)[0]['ticker_symbol']
            stockx_name = stockx.search(product_name)[0]['name']
            product_id = stockx.get_first_product_id(interested_product_id)
            if (size =='all'):
                dictionary_asks = stockx.organize_asks(product_id)
                all_expanded = list(dictionary_asks.keys())
                all_expanded.sort()
                sizes = sizes + all_expanded
                for i in all_expanded: 
                    item.append(product_name)
                    stockx_item.append(stockx_name)
                    lowest_ask.append(min(dictionary_asks[i]))
            else: 
                item.append(product_name)
                stockx_item.append(stockx_name)
                sizes.append(size)
                lowest_ask.append(stockx.get_lowest_ask(product_id,size)[0])
    df = pd.DataFrame({'Item':item,'StockX Name':stockx_item,'Size':sizes,'Lowest Ask':lowest_ask})
    df['Break Even Point'] = df['Lowest Ask']/.88
    return df

def organize_by_size(df):
    def size_step1_dictionary(x):
        dictionary_stuff = {'S':-13,'M':-12,'L':-11,'XL':-10}
        if x in dictionary_stuff.keys():
            return dictionary_stuff[x]
        else:
            return x
    def size_step2_dictionary(x):
        dictionary_stuff = {'S':-13,'M':-12,'L':-11,'XL':-10}
        inv_map = {v: k for k, v in dictionary_stuff.items()}
        if x in inv_map.keys():
            return inv_map[x]
        else:
            return x
    df['Size'] = df['Size'].apply(size_step1_dictionary)
    df['Size'] = df['Size'].astype(float)
    df = df.sort_values(['Item','Size'])
    df['Size'] = df['Size'].apply(size_step2_dictionary)
    return df


# In[372]:


import re


# In[375]:


input_string = '(travis scott high, 9), (travis scott low, all), (yeezy 350 black non-reflective,7)'


# In[510]:


# format: (item1,size1), (item2,size2), (item3,size3) ...
# clothing must be S, M, L, XL

shoes_of_interest = input()


# In[533]:


input_df = initial_df_creator(shoes_of_interest)


# In[534]:


test = stockx_purchase_df_creator(input_df)


# In[535]:


test.head()


# In[536]:


organize_by_size(test)

