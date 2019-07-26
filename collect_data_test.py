# General test file for checking functionality of packages/modules.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

module_path = os.path.abspath(os.path.join('mod'))
sys.path = [x[0] for x in os.walk(module_path)] + sys.path
from stockxsdk import Stockx
from emailsdk import login, get_emails, order_df_creator


def main():
    stockx = Stockx()

    username = 'sneaks.and.supreme.88@gmail.com'
    password = '8363Espie'

    mail = login(username, password)
    email_bodies = get_emails(mail, 'ALL')
    # for item in email_bodies:
    #     print(item + '\n\n\n')
    # df = order_df_creator(email_bodies)
    # print(df)

    # stockx.authenticate('clone.arctrooper@gmail.com', 'LigmaBalls69~')

    # product_id = stockx.get_first_product_id('AJ1H-TS')

    # bids = stockx.get_bids(product_id, size=9)
    # print(len(bids))
    # all_prices = [i.order_price for i in bids]

    # print(all_prices)


if __name__ == '__main__':
    main()