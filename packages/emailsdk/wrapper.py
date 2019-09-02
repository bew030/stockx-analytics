import pandas as pd
import numpy as np
import email
import imaplib
from datetime import datetime

class Ereader():
    # methods
    def login(email, password):
        '''
        Method used to login to email with orders. Requires email and password in string format. ONLY GMAIL CURRENTLY WORKS
        Email should primarily be filled with forwarded emails (forwarded from main source, all emails going to this email
        would lead to suspicions of multiple orders)
        
        Parameters:
            email:
                An email (string representation of email, includes @__.com), password (string representation of password)
            password:
                The associated password with the aforementioned email
        
        Returns:
            An imaplib.IMAP4_SSL object representing the mailbox logged into.
        '''
        smtp_server = "imap.gmail.com"
        smtp_port = 993 
        mail = imaplib.IMAP4_SSL(smtp_server)
        result, authentification = mail.login(email, password)
        print('Login: ' + result)
        print(type(mail))
        return mail


    def get_emails(mail, criterion='(UNSEEN)'):
        '''
        Method used to get the email body of emails in inbox. Only checks for unread emails by default. Requires the mail object created from the login method. 
        
        Parameters:
            mail:
                An imaplib.IMAP4_SSL object, created from login

        Optional Parameters:
            get_all:
                False by default. If true, returns all emails in the inbox.
        
        Returns:
            A list of the raw text of the bodies of all the emails
        '''
        _, messages = mail.select('INBOX')
        _, data = mail.uid('search', None, criterion)
        email_uids = latest_email_uid = data[0].split()
        email_bodies = []
        for i in email_uids:
            _, data = mail.uid('fetch', i, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            email_message = process_forward(email_message)
            if email_message.is_multipart():
                email_bodies.append(email_message.get_payload()[0].get_payload())
            else:
                email_bodies.append(email_message.get_payload())
        return email_bodies


    def process_forward(message):
        strmsg = ''
        if message.is_multipart():
            strmsg = message.get_payload()[0].get_payload()
        else:
            strmsg = message.get_payload()
        print(strmsg)
        return message


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