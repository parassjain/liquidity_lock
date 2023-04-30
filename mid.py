"""
Assumptions
1. one who orders first will get execued first in case of insufficier=t buyers/sellers
2. trimming numbers to 2 decimal places

"""

import pandas as pd
import numpy
import csv

df = pd.read_excel(r"ProblemSetData.xlsx")
# print(df)
col_list = df.values.T.tolist()
# col_list
row_list = df.values.tolist()
row_list

list_of_unique_product = list(set(col_list[1]))
list_of_unique_product


def get_product_wise_data(row_list, list_of_unique_product):
    product_wise_data = {}
    for p in list_of_unique_product:
        product_wise_data[p] = list()
    for id, row in enumerate(row_list):
        product_wise_data[row[1]].append(row)
    return product_wise_data


def get_trade_quantity(values):
    buy_sell_quantity = [[x[2], x[3]] for x in values]  # parsing list of ["Direction","Quantity"]
    buy, sell = 0, 0
    for i in buy_sell_quantity:
        if i[0] == "Buy":
            buy += i[1]
        else:
            sell += i[1]
    return min(buy, sell)


def get_trade_price(values):
    quantity_price = [[x[3], x[4]] for x in values]  # quantity_price is a 2d list with [quantity,price] as sublist
    total_quantity_price_sum = sum([x * y for x, y in quantity_price])  # parsing list of ["Quantity","Price"]
    total_quantity_sum = sum(map(lambda x: x[1], quantity_price))
    return round(total_quantity_price_sum / total_quantity_sum, 2)  # assuming total_quantity_sum!=0


# these queue for a single product
def generate_buy_sell_queue(all_trades_for_product):
    buy_queue, sell_queue = [], []
    for trade in all_trades_for_product:
        if trade[2] == "Buy":
            buy_queue.append(trade)
        else:
            sell_queue.append(trade)
    return buy_queue, sell_queue


def list_of_trade_bw_parties(p, buy_queue, sell_queue, trade_quantity, trade_price, w, transaction_log):
    while trade_quantity > 0:
        current_buyer, current_seller = buy_queue[0], sell_queue[0]
        transaction_quant = min(current_buyer[3], current_seller[3])

        current_trade = {
            "quantity": transaction_quant,
            "rate": trade_price,
            "seller": current_seller[0],
            "buyer": current_buyer[0],
            "sellers_profit": current_seller[4] * transaction_quant,
            "buyers_profit": current_buyer[4] * transaction_quant,
        }
        transaction_log.append(current_trade)
        # print(current_buyer,current_seller)
        # once we log the transaction, lets update the buy and the sell queue
        if current_buyer[3] == current_seller[3]:
            sell_queue.pop(0)
            buy_queue.pop(0)
        elif current_buyer[3] > current_seller[3]:
            sell_queue.pop(0)
            current_buyer[3] -= transaction_quant
        elif current_seller[3] > current_buyer[3]:
            buy_queue.pop(0)
            current_seller[3] -= transaction_quant
        print(current_trade)
        w.writerow(
            [
                current_trade["seller"],
                current_trade["buyer"],
                p,
                current_trade["quantity"],
                current_trade["rate"],
                current_trade["sellers_profit"],
                current_trade["buyers_profit"],
            ]
        )
        trade_quantity = trade_quantity - transaction_quant
    return transaction_log


with open("mid_results.csv", "w") as f:
    transaction_log = []
    w = csv.writer(f)
    w.writerow(
        [
            "seller",
            "buyer",
            "product",
            "quantity",
            "rate",
            "sellers_profit",
            "buyers_profit",
        ]
    )
    product_wise_data = get_product_wise_data(row_list, list_of_unique_product)
    for p, v in product_wise_data.items():
        print(p)

        trade_quantity = get_trade_quantity(v)
        print("total buy/sell quantity", trade_quantity)

        trade_price = get_trade_price(v)
        print("final trade rate", trade_price)

        # generate buy and sell queue here
        buy_queue, sell_queue = generate_buy_sell_queue(v)

        transaction_log = list_of_trade_bw_parties(
            p, buy_queue, sell_queue, trade_quantity, trade_price, w, transaction_log
        )
        print("---------all trades for product {} executed--------------------".format(p))
    print("all transactions completed and logged into mid_results.csv")
