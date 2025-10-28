from pprint import pprint
def calc_WH(supplier_data):
    sup_num = supplier_data["Поставщик #"]
    item_price = supplier_data["Цена за единицу (руб.) *"]
    item_vol = supplier_data["Объём единицы (м³) *"]
    min_batch = supplier_data["Минимальная партия (ед.) *"]
    logistics_cost = supplier_data['Логистические расходы (руб.)']
    storage_term = supplier_data['Срок хранения (дни) *']
    payment_delay = supplier_data["Отсрочка платежа (дней)"]
    retro_bonus = supplier_data["Ретро-бонус (%)"]
    returnable = supplier_data["Возвратный товар"]
    risk_costs = supplier_data["Риски и доп. издержки (руб.)"]


    print(f"calc_WH, Поставщик №: {sup_num}")
    pprint(supplier_data)        

    if returnable:
        formula =  item_price + item_vol + min_batch + logistics_cost + storage_term + payment_delay + retro_bonus + risk_costs
    else:
        formula =  item_price + item_vol + min_batch + logistics_cost + storage_term + payment_delay + retro_bonus + risk_costs

    return formula