import requests
import csv
import time
import config


def format_amount(amount):
    if amount >= 0: formatted_amount = "+{} р.".format(abs(amount))
    else: formatted_amount = "-{} р.".format(abs(amount))
    return formatted_amount

def send_message(message):
    requests.get(f'https://api.telegram.org/bot{config.TOKEN}/sendMessage?chat_id={config.ADMIN_ID}&text={message}')

def get_data_csv ():

    data_all = []

    with open('data.csv', newline='') as f:
        reader = csv.reader(f)

        for idx, row in enumerate(reader):
            if idx != 0: data_all.append([i.split('/')[-2] for i in row])

    return data_all


def getInfoWB (products_ids=['163100410']):

    products_data = requests.get(f"https://card.wb.ru/cards/detail?appType=1&curr=rub&spp=31&nm={';'.join(products_ids[1:])}", timeout=5, verify=False).json()['data']['products']
    
    products_prices = []

    for i in products_data:
        products_prices.append((i['id'], i['salePriceU']//100, i['extended']['basicPriceU']))

    print('Success get data')

    return {products_ids[0]: products_prices}


def get_products_prices (data):

    result_data = []

    for i in data:
        result_data.append(getInfoWB(i))

    return result_data


def compare_arrays(arr1, arr2):
    changed_values = []

    for i in range(len(arr1)):

        if arr1[i] != arr2[i]:
            dict_id = list(arr1[i].keys())[0]
            
            el1 = arr1[i][dict_id]
            el2 = arr2[i][dict_id]
            
            for j in range(len(el1)):

                if el1[j][1] != el2[j][1]:
                    changed_values.append({
                        'key_our': f"https://www.wildberries.ru/catalog/{dict_id}/detail.aspx",
                        'key': f"https://www.wildberries.ru/catalog/{el1[j][0]}/detail.aspx",
                        'change': el2[j][1] - el1[j][1]
                    })
                
                if el1[j][2] != el2[j][2]:
                    changed_values.append({
                        'key_our': f"https://www.wildberries.ru/catalog/{dict_id}/detail.aspx",
                        'key': f"https://www.wildberries.ru/catalog/{el1[j][0]}/detail.aspx",
                        'change': el2[j][2] - el1[j][2]
                    })

    return changed_values



def watch_prices ():

    csv_data = get_data_csv()
    # print(csv_data)
    prices_last = get_products_prices(csv_data)

    while True:

        price_temp = get_products_prices(csv_data)

        changes = compare_arrays(price_temp, prices_last)

        if changes:
            for i in changes:
                send_message(f'Изменение цены!\nВаш товар: {i["key_our"]}\nТовар конкурента: {i["key"]}\nИзменение цены: {format_amount(i["change"])}')

        prices_last = price_temp
        
        time.sleep(60)
        


if __name__ == "__main__":
    watch_prices()