from pprint import pprint
def calc_inzak(supplier_data):
    sup_num = supplier_data["Поставщик №"]
    logistics_cost = supplier_data['Логистические расходы (руб.)']
    total_cost = supplier_data["Общая стоимость товаров/услуг (руб.)"]
    logistics_cost = supplier_data["Логистические расходы (руб.)"]
    product_vol = supplier_data["Объем товара (м³)"]
    shipment_type = supplier_data["Тип отгрузки"]
    shipment_term = supplier_data["Срок поставки (дней)"]
    partial_downpayment = supplier_data["Частичная предоплата"]
    payment_delay = supplier_data["Отсрочка платежа (дней)"]
    retro_bonus = supplier_data["Ретро-бонус (%)"]
    returnable = supplier_data["Возвратный товар"]
    risk_costs = supplier_data["Риски и доп. издержки (руб.)"]

    print(f"calc_inzak, Поставщик №: {sup_num}")
    pprint(supplier_data)        

    if returnable:
        formula =  total_cost + logistics_cost + product_vol + shipment_term + payment_delay + retro_bonus + risk_costs
    elif partial_downpayment:
        formula =  total_cost + logistics_cost + product_vol + shipment_term + payment_delay + retro_bonus + risk_costs
    elif shipment_type == "Прямая отгрузка":
        formula =  total_cost + logistics_cost + product_vol + shipment_term + payment_delay + retro_bonus + risk_costs
    else:
        formula =  total_cost + logistics_cost + product_vol + shipment_term + payment_delay + retro_bonus + risk_costs

    return formula