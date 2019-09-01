import datetime
import json
import requests
import re
import time
import pandas as pd
from stockxsdk.item import StockxItem
from stockxsdk.order import StockxOrder
from stockxsdk.product import StockxProduct


def now_plus_thirty():
    return (datetime.datetime.now() + datetime.timedelta(30)).strftime('%Y-%m-%d')


def now():
    return datetime.datetime.now().strftime('%Y-%m-%d')


class Stockx():
    API_BASE = 'https://stockx.com/api'

    def __init__(self):
        self.customer_id = None
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                        'cookie': '"tracker_device=1e35f08d-8593-4ea9-acee-9776289ea1a7; __cfduid=d05fcb748af2e6c8f7d58bf0825b9f01c1557191349; ajs_group_id=null; ajs_anonymous_id=%2218f080ab-7eb3-448e-8ff7-a1ca9b273599%22; _ALGOLIA=anonymous-0050e44a-a820-4452-87f8-b043cba2a28d; ajs_user_id=%224a55ac74-a9b5-11e9-8880-12deb909e97c%22; _pxhd=7d8daab02854a906fd314547ce31bc312f14848e7b1ae6696d9c785f517fd2ea:b01d7a01-a9b4-11e9-9898-d7228a3cbac8; cto_lwid=91b1b927-bf10-4a47-8301-d6d7563b6bae; _ga=GA1.2.528701073.1563807263; _gid=GA1.2.222162355.1563807263; _tl_duuid=278767c9-773b-41ce-94e4-88a0b0345242; _gcl_au=1.1.1888694694.1563807265; _scid=87f8e8b8-27bf-4bde-a0ef-a5f2d4ddc51e; _sctr=1|1563771600000; IR_gbd=stockx.com; _fbp=fb.1.1563807272792.154772747; rskxRunCookie=0; rCookie=pp701k72p8gcvd6b8blv6rjyeih2x3; _tl_uid=4a55ac74-a9b5-11e9-8880-12deb909e97c; stockx_product_visits=1; stockx_homepage=sneakers; _sp_ses.1a3e=*; _tl_csid=27d8c63e-29de-4f08-84ea-ae198ef90ec8; is_gdpr=false; stockx_selected_currency=USD; stockx_selected_locale=en_US; _sp_id.1a3e=575ad936-e80a-4473-b09a-5333704e4e98.1563807263.2.1563818022.1563812382.a42cae94-3471-4b97-9ad7-74c7ea340da7; tl_sopts_27d8c63e-29de-4f08-84ea-ae198ef90ec8_p_p_n=JTJG; tl_sopts_27d8c63e-29de-4f08-84ea-ae198ef90ec8_p_p_l_h=aHR0cHMlM0ElMkYlMkZzdG9ja3guY29tJTJG; tl_sopts_27d8c63e-29de-4f08-84ea-ae198ef90ec8_p_p_l_t=U3RvY2tYJTNBJTIwQnV5JTIwYW5kJTIwU2VsbCUyMFNuZWFrZXJzJTJDJTIwU3RyZWV0d2VhciUyQyUyMEhhbmRiYWdzJTJDJTIwV2F0Y2hlcw==; tl_sopts_27d8c63e-29de-4f08-84ea-ae198ef90ec8_p_p_l=JTdCJTIyaHJlZiUyMiUzQSUyMmh0dHBzJTNBJTJGJTJGc3RvY2t4LmNvbSUyRiUyMiUyQyUyMmhhc2glMjIlM0ElMjIlMjIlMkMlMjJzZWFyY2glMjIlM0ElMjIlMjIlMkMlMjJob3N0JTIyJTNBJTIyc3RvY2t4LmNvbSUyMiUyQyUyMnByb3RvY29sJTIyJTNBJTIyaHR0cHMlM0ElMjIlMkMlMjJwYXRobmFtZSUyMiUzQSUyMiUyRiUyMiUyQyUyMnRpdGxlJTIyJTNBJTIyU3RvY2tYJTNBJTIwQnV5JTIwYW5kJTIwU2VsbCUyMFNuZWFrZXJzJTJDJTIwU3RyZWV0d2VhciUyQyUyMEhhbmRiYWdzJTJDJTIwV2F0Y2hlcyUyMiU3RA==; tl_sopts_27d8c63e-29de-4f08-84ea-ae198ef90ec8_p_p_v_d=MjAxOS0wNy0yMlQxNyUzQTUzJTNBNDEuOTgzWg==; _pk_id.421.1a3e=97e2a3209dfd4c7e.1563807264.3.1563818024.1563818024.; _pk_ses.421.1a3e=*; stockx_user_logged_in=true; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdG9ja3guY29tIiwic3ViIjoic3RvY2t4LmNvbSIsImF1ZCI6IndlYiIsImFwcF9uYW1lIjoiSXJvbiIsImFwcF92ZXJzaW9uIjoiMi4wLjAiLCJpc3N1ZWRfYXQiOiIyMDE5LTA3LTIyIDE3OjUzOjQyIiwiY3VzdG9tZXJfaWQiOiI3OTc1MjMzIiwiZW1haWwiOiJjbG9uZS5hcmN0cm9vcGVyQGdtYWlsLmNvbSIsImN1c3RvbWVyX3V1aWQiOiI0YTU1YWM3NC1hOWI1LTExZTktODg4MC0xMmRlYjkwOWU5N2MiLCJmaXJzdE5hbWUiOiJCb2IiLCJsYXN0TmFtZSI6IkpvbmVzIiwiZ2Rwcl9zdGF0dXMiOm51bGwsImRlZmF1bHRfY3VycmVuY3kiOiJVU0QiLCJsYW5ndWFnZSI6ImVuLVVTIiwic2hpcF9ieV9kYXRlIjpudWxsLCJ2YWNhdGlvbl9kYXRlIjpudWxsLCJwcm9kdWN0X2NhdGVnb3J5Ijoic25lYWtlcnMiLCJpc19hZG1pbiI6IjAiLCJzZXNzaW9uX2lkIjoiMTMxMTgxNzA0MDQ4MjE1MzYyNTkiLCJleHAiOjE1NjQ0MjI4MjIsImFwaV9rZXlzIjpbXX0.jb5OGmNBTBJtKa4EYYxBuf6pHhb_N8UTAQH-01JspTA; _gat=1; IR_9060=1563818027855%7C0%7C1563818027855%7C%7C; IR_PI=9d8de178-ac90-11e9-b701-42010a246c04%7C1563904427855; show_all_as_number=false; brand_tiles_version=v1; show_bid_education=v2; show_bid_education_times=1; multi_edit_option=beatLowestAskBy; product_page_v2=watches%2Chandbags; show_watch_modal=true; lastRskxRun=1563818029225; intercom-session-h1d8fvw9=cXZSamdKR0pZazRzSllPb2Q4UEdMa3M1VGdTdCt5VGNaYWVoRGYwWC82SWkvYzZFd2piNUM1MHZoKzlzTHZZOS0tK1RybXI3RHM5MWREaDlPSlc2MUJDUT09--8bddce95b41f8d14f561b7a0cb57a949f5c3d99f; cookie_policy_accepted=true"',
                        'accept-language': 'en-US,en;q=0.9',
                        'cache-control': 'max-age=0',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
                        }

    def __api_query(self, request_type, command, data=None):
        endpoint = self.API_BASE + command
        response = None
        if request_type == 'GET':
            response = requests.get(endpoint, params=data, headers=self.headers)
        elif request_type == 'POST':
            response = requests.post(endpoint, json=data, headers=self.headers)
        elif request_type == 'DELETE':
            response = requests.delete(endpoint, json=data, headers=self.headers)
        return response.json()

    def __get(self, command, data=None):
        return self.__api_query('GET', command, data)

    def __post(self, command, data=None):
        return self.__api_query('POST', command, data)

    def __delete(self, command, data=None):
        return self.__api_query('DELETE', command, data)

    def authenticate(self, email, password):
        endpoint = self.API_BASE + '/login'
        payload = {
            'email': email,
            'password': password
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        customer = response.json().get('Customer', None)
        if customer is None:
            raise ValueError('Authentication failed, check username/password')
        self.customer_id = response.json()['Customer']['id']
        self.headers['JWT-Authorization'] = response.headers['jwt-authorization']
        return True

    def me(self):
        command = '/users/me'
        return self.__get(command)

    def selling(self):
        command = '/customers/{0}/selling'.format(self.customer_id)
        response = self.__get(command)
        return [StockxItem(item_json) for item_json in response['PortfolioItems']]

    def buying(self):
        command = '/customers/{0}/buying'.format(self.customer_id)
        response = self.__get(command)
        return [StockxItem(item_json) for item_json in response['PortfolioItems']]

    def rewards(self):
        command = '/users/me/rewards'
        return self.__get(command)

    def stats(self):
        command = '/customers/{0}/collection/stats'.format(self.customer_id)
        return self.__get(command)

    def add_product_to_follow(self, product_id):
        command = '/portfolio?a=1001'
        payload = {
            'timezone': 'America/Chicago',
            'PortfolioItem': {
                'amount': 0,
                'matchedWithDate': '',
                'condition': '2000',
                'skuUuid': product_id,
                'action': 1001
            }
        }
        response = self.__post(command, payload)
        success = response['PortfolioItem']['text'] == 'Following'
        return success

    # remember to underscore this
    def __get_activity(self, product_id, activity_type):
        command = '/products/{0}/activity?state={1}'.format(product_id, activity_type)
        return self.__get(command)

    def get_asks(self, product_id):
        return sorted([StockxOrder('bid', order) for order in self.__get_activity(product_id, 400)])
    
    def organize_asks(self, product_id):
        dictionary_asks = {} 
        for i in self.get_asks(product_id):
            if i.shoe_size not in dictionary_asks.keys():
                new_list = [i.order_price] 
                dictionary_asks[i.shoe_size] = new_list
            else:
                dictionary_asks[i.shoe_size].append(i.order_price)
        return dictionary_asks

    # mildly useless function, probably get rid of it 
    def get_lowest_ask(self, product_id, shoe_size = None):
        if shoe_size == None:
            #print('lowest ask overall:')
            return self.get_asks(product_id)[0].order_price, self.get_asks(product_id)[0].shoe_size
        else:
            if str(shoe_size) in list(self.organize_bids(product_id).keys()):
                return min(self.organize_asks(product_id)[str(shoe_size)]), shoe_size
            else:
                return -1, shoe_size

    def lowest_ask_df(self, product_id):
        test_df = pd.DataFrame([self.organize_asks(product_id)])
        test_df = test_df.T.reset_index()
        test_df.columns = ['Size','Asks']
        test_df['Min Ask'] = test_df['Asks'].apply(min) 
        return test_df
    
    def get_bids(self, product_id, size=None):
        return sorted([StockxOrder('bid', order) for order in self.__get_activity(product_id, 300)])

    def organize_bids(self, product_id):
        dictionary_bids = {} 
        for i in self.get_bids(product_id):
            if i.shoe_size not in dictionary_bids.keys():
                new_list = [i.order_price] 
                dictionary_bids[i.shoe_size] = new_list
            else:
                dictionary_bids[i.shoe_size].append(i.order_price)
        return dictionary_bids

    # mildly useless function, probably get rid of it 
    def get_highest_bid(self, product_id, shoe_size = None):
        if shoe_size == None:
            #print('highest bid overall:')
            return self.get_bids(product_id)[-1].order_price, self.get_bids(product_id)[-1].shoe_size
        else:
            if str(shoe_size) in list(self.organize_bids(product_id).keys()):
                return max(self.organize_bids(product_id)[str(shoe_size)]), shoe_size
            else:
                return 0, shoe_size
    
    def highest_bid_df(self, product_id):
        test_df = pd.DataFrame([self.organize_bids(product_id)])
        test_df = test_df.T.reset_index()
        test_df.columns = ['Size','Bids']
        test_df['Max Bid'] = test_df['Bids'].apply(max) 
        return test_df

    def overall_df(self, product_id):
        return pd.merge(self.highest_bid_df(product_id), self.lowest_ask_df(product_id), on ='Size')

    def search(self, query):
        endpoint = 'https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query'
        params = {
            'x-algolia-agent': 'Algolia for vanilla JavaScript 3.22.1',
            'x-algolia-application-id': 'XW7SBCT9V6',
            'x-algolia-api-key': '6bfb5abee4dcd8cea8f0ca1ca085c2b3'
        }
        payload = {
            'params': 'query={0}&hitsPerPage=20&facets=*'.format(query)
        }
        return requests.post(endpoint, json=payload, params=params).json()['hits']

    def get_first_product_id(self, query):
        return self.search(query)[0]['objectID']

    def initial_df_creator(self, string_interest):
        shoes = re.findall('\(([^)]+)\)', shoes_of_interest)
        split_shoes = [x.split(',') for x in shoes]
        shoe_name = [x[0].strip() for x in split_shoes] 
        shoe_size = [x[1].strip() for x in split_shoes] 
        return pd.DataFrame({'Item':shoe_name,'Size':shoe_size})

    def stockx_df_creator(self, df):
        item = [] 
        sizes = [] 
        highest_bid = [] 
        lowest_ask = [] 
        failed_items = []
        for i in range(len(df)):
            product_name = df.iloc[i]['Item']
            size = df.iloc[i]['Size']
            interested_product = product_name
            if len(self.search(interested_product)) == 0:
                failed_items.append(product_name)
            else:
                interested_product_id = self.search(interested_product)[0]['ticker_symbol']
                product_id = self.get_first_product_id(interested_product_id)
                print(product_name) # should this be included?
                item.append(product_name)
                sizes.append(size)
                if size != size:
                    highest_bid.append(self.get_highest_bid(product_id)[0])
                    lowest_ask.append(self.get_lowest_ask(product_id)[0])
                else:
                    highest_bid.append(self.get_highest_bid(product_id,size)[0])
                    lowest_ask.append(self.get_lowest_ask(product_id,size)[0])
        bids_df = pd.DataFrame({'Item':item,'Size':sizes,'Highest Bid':highest_bid,'Lowest Ask':lowest_ask})
        final = pd.merge(df, bids_df, on = ['Item','Size'])
        percentage = (self.rewards()['data'][0]['attributes']['lifetime']['rates'][0]['fee'])/100
        transaction = .03 
        final['Payout Highest Bid'] = np.round((1-percentage-transaction)*final['Highest Bid'],2)
        final['Payout Lowest Ask'] = np.round((1-percentage-transaction)*final['Lowest Ask'],2)
        final['Profit Highest Bid'] = final['Payout Highest Bid']-final['Price']
        final['Profit Lowest Ask'] = final['Payout Lowest Ask']-final['Price']
        return final, failed_items

    # DOESN'T RETURNED FAILED SEARCHUP LIST YET; FIX THAT SHIT 
    def df_converter(self, df, time_delay = .5):
        length = len(df)
        array_indexes = [20*x for x in range(length//20+1)]
        array_indexes.append(length)
        start, start_failed = self.stockx_df_creator(df[0:20]) 
        # print(start_failed)
        for i in range(1,len(array_indexes)-1):
            time.sleep(time_delay)
            new, new_failed = self.stockx_df_creator(df[array_indexes[i]:array_indexes[i+1]])
            start = pd.concat([start,new],ignore_index=True)
            start_failed = start_failed+new_failed
        return start, start_failed

    def colorizer(self, df):
        def highlight_greaterthan_1(s):
            if s['Profit Lowest Ask'] > 0.0:
                return ['background-color: Aquamarine']*12
            else:
                return ['background-color: LightPink']*12

        df = df.style.apply(highlight_greaterthan_1, axis=1)
        return df

    def stockx_purchase_df_creator(self, df):
        item = [] 
        stockx_item = [] 
        sizes = [] 
        lowest_ask = [] 
        for i in range(len(df)):
            product_name = df.iloc[i]['Item']
            size = df.iloc[i]['Size']
            if len(self.search(product_name)) == 0: 
                item.append('error for '+product_name+'; change name or check if StockX has item')
                stockx_item.append(np.nan)
                sizes.append(size)
                lowest_ask.append(np.nan)
            else: 
                interested_product_id = self.search(product_name)[0]['ticker_symbol']
                stockx_name = self.search(product_name)[0]['name']
                product_id = self.get_first_product_id(interested_product_id)
                if (size =='all'):
                    dictionary_asks = self.organize_asks(product_id)
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
                    lowest_ask.append(self.get_lowest_ask(product_id,size)[0])
        df = pd.DataFrame({'Item':item,'StockX Name':stockx_item,'Size':sizes,'Lowest Ask':lowest_ask})
        df['Break Even Point'] = df['Lowest Ask']/.88
        return df

    def organize_by_size(self, df):
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




