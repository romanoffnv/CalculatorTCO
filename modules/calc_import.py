from pprint import pprint
def calc_import(supplier_data):
    sup_num = supplier_data["Поставщик #"]
    total_cost = supplier_data["Общая стоимость товаров/услуг (руб.) *"]
    product_vol = supplier_data["Объем товара (м³) *"]
    customs_toll = supplier_data["Таможенная пошлина (руб.) *"]
    transportation_cost = supplier_data["Транспортные расходы (руб.) *"]
    insurance_cost = supplier_data["Стоимость страховки (руб.)"]
    customs_clearance = supplier_data["Стоимость таможенного оформления (руб.)"]
    min_purchase_vol = supplier_data["Минимальный объем закупки (руб.)"]
    payment_delay = supplier_data["Отсрочка платежа (дней)"]
    retro_bonus = supplier_data["Ретро-бонус (%)"]
    returnable = supplier_data["Возвратный товар"]
    risk_costs = supplier_data["Риски и доп. издержки (руб.)"]

    
    
    
    print(f"calc_import, Поставщик #: {sup_num}")
    pprint(supplier_data)        

    if returnable:
        formula =  total_cost + product_vol + customs_toll + transportation_cost + insurance_cost + customs_clearance + min_purchase_vol + payment_delay + risk_costs + retro_bonus
    else:
        formula =  total_cost + product_vol + customs_toll + transportation_cost + insurance_cost + customs_clearance + min_purchase_vol + payment_delay + risk_costs + retro_bonus

    return formula