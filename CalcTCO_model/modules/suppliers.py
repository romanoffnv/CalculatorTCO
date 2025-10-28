class Supplier:
    def __init__(self):
        # Common menu items Test
        # self.returnable = 1
        # self.payment_delay = 1
        # self.retro_bonus = 10.0
        # self.risk_costs = 100.0
        
        # Common menu items
        while True:    
            self.returnable = int(input("Возвратный товар: 1 - Да, 0 - Нет "))
            if self.returnable in [0, 1]:
                break
            
        self.payment_delay = int(input("Отсрочка платежа (кол-во дней): "))
        self.retro_bonus = float(input("Ретро-бонус (%): "))
        self.risk_costs = float(input("Риски и доп. издержки (руб.) *: "))


class SupplierInzak(Supplier):
    def __init__(self, sup_num):
        self.sup_num = sup_num
        # SupplierInzak menu items Test
        # self.total_cost = 1.0 
        # self.logistics_cost = 1.0 
        # self.product_vol = 1.0 
        # self.shipment_type = 1
        # self.shipment_term = 1
        # self.partial_downpayment = 1
        
        # SupplierInzak menu items
        print(f"Поставщик #{self.sup_num}")
        self.total_cost = float(input("Общая стоимость товаров/услуг (руб.) *: "))
        self.logistics_cost = float(input("Логистические расходы (руб.) *: "))
        self.product_vol = float(input("Объем товара (м³) *: "))
        while True:
            self.shipment_type = int(input("Тип отгрузки *: 1 - Прямая отгрузка, 2 - Отгрузка с ЦС "))
            if self.shipment_type in [1, 2]:
                break
        self.shipment_term = int(input("Срок поставки (дней) *: "))
        while True:
            self.partial_downpayment = int(input("Частичная предоплата: 1 - Да, 0 - Нет "))
            if self.partial_downpayment in [0, 1]:
                break

        # Supplier class inheritance
        super().__init__()

    def vars(self):
        return {
            "Поставщик #": self.sup_num,
            "Общая стоимость товаров/услуг (руб.)": self.total_cost, 
            "Логистические расходы (руб.)": self.logistics_cost,
            "Объем товара (м³)": self.product_vol, 
            "Тип отгрузки": "Прямая отгрузка" if self.shipment_type == 1 else "Отгрузка с ЦC",
            "Срок поставки (дней)": self.shipment_term,
            "Частичная предоплата": True if self.partial_downpayment else False,
            "Отсрочка платежа (дней)": self.payment_delay,
            "Ретро-бонус (%)": self.retro_bonus,
            "Возвратный товар": True if self.returnable else False,
            "Риски и доп. издержки (руб.)": self.risk_costs
        }


class SupplierWH(Supplier):
    def __init__(self, sup_num):
        self.sup_num = sup_num
                
        # SupplierWH specific menu items Test
        # self.item_price = 2.0
        # self.item_vol = 2
        # self.min_batch = 2
        # self.logistics_cost = 200.0
        # self.storage_term = 2
        
        # SupplierWH specific menu items
        print(f"Поставщик #{self.sup_num}")
        self.item_price = float(input("Цена за единицу (руб.) *: "))
        self.item_vol = float(input("Объём единицы (м³) *: "))
        self.min_batch = int(input("Минимальная партия (ед.) *: "))
        self.logistics_cost = float(input("Логистические расходы (руб.) *: "))
        self.storage_term = int(input("Срок хранения (дни) *: "))
        # Supplier inheritance
        super().__init__()
        

    # SupplierWH specific class printouts
    def vars(self):
        return {
                    "Поставщик #": self.sup_num,
                    "Цена за единицу (руб.) *" : self.item_price, 
                    "Объём единицы (м³) *" : self.item_vol,
                    "Минимальная партия (ед.) *" : self.min_batch,
                    "Логистические расходы (руб.)" : self.logistics_cost,
                    "Срок хранения (дни) *" : self.storage_term,
                    "Отсрочка платежа (дней)" : self.payment_delay, 
                    "Ретро-бонус (%)" : self.retro_bonus, 
                    "Возвратный товар": True if self.returnable else False,
                    "Риски и доп. издержки (руб.)": self.risk_costs
        }
    

class SupplierImport(Supplier):
    def __init__(self, sup_num):
        self.sup_num = sup_num

        # SupplierImport specific props Test
        # self.total_cost = 300.0
        # self.product_vol = 33.4
        # self.customs_toll = 345.0
        # self.transportation_cost = 3456.77
        # self.insurance_cost = 34156.0
        # self.customs_clearance = 3333.0
        # self.min_purchase_vol = 3.5
        
        # SupplierImport specific props
        print(f"Поставщик #{self.sup_num}")
        self.total_cost = float(input("Общая стоимость товаров/услуг (руб.) *: "))
        self.product_vol = float(input("Объем товара (м³) *: "))
        self.customs_toll = float(input("Таможенная пошлина (руб.) *"))
        self.transportation_cost = float(input("Транспортные расходы (руб.) *: "))
        self.insurance_cost = float(input("Стоимость страховки (руб.): "))
        self.customs_clearance = float(input("Стоимость таможенного оформления (руб.): "))
        self.min_purchase_vol = float(input("Минимальный объем закупки (руб.): "))

        # Supplier inheritance
        super().__init__()


    # SupplierImport specific class printouts
    def vars(self):
        return {
                "Поставщик #": self.sup_num,
                "Общая стоимость товаров/услуг (руб.) *": self.total_cost,
                "Объем товара (м³) *" : self.product_vol,
                "Таможенная пошлина (руб.) *": self.customs_toll,
                "Транспортные расходы (руб.) *": self.transportation_cost,
                "Стоимость страховки (руб.)": self.insurance_cost,
                "Стоимость таможенного оформления (руб.)": self.customs_clearance,
                "Минимальный объем закупки (руб.)": self.min_purchase_vol,
                "Отсрочка платежа (дней)": self.payment_delay, 
                "Ретро-бонус (%)": self.retro_bonus, 
                "Возвратный товар": True if self.returnable else False,
                "Риски и доп. издержки (руб.)": self.risk_costs      
            }