#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pprint import pprint
from modules.suppliers import SupplierInzak, SupplierWH, SupplierImport
from modules.calc_inzak import calc_inzak
from modules.calc_WH import calc_WH
from modules.calc_import import calc_import
from modules.assessment import assess_sup


# In[2]:


def get_assort_type():
    # Assortment type selection menu
    while True:
        assort_type = int(input(""" 
                                    Выберите тип ассортимента:
                                    1. ИНЗАК
                                    2. Складской ассортимент
                                    3. ИМПОРТ
                                """))

        if assort_type in [1, 2, 3]:
            return assort_type
        else:
            print("Ошибка: тип ассортимента должен быть 1, 2 или 3")


# In[3]:


def get_suppliers_num():
    # Suppliers number menu
    while True:
        suppliers_num = int(input("""Выберите количество поставщиков (2-3):"""))

        if suppliers_num in [2, 3]:
            return suppliers_num
        else:
            print("Ошибка: количество поставщиков - 2 или 3.")


# In[ ]:


def get_suppliers(assort_type, suppliers_num):
    # Getting suppliers objects off from suppliers classes
    if assort_type == 1:
        print(f"Тип ассортимента: ИНЗАК")
        suppliers = [SupplierInzak(i) for i in range(1, suppliers_num + 1)]
    elif assort_type == 2:
        print(f"Тип ассортимента: Складской ассортимент")
        suppliers = [SupplierWH(i) for i in range(1, suppliers_num + 1)]
    else:
        print(f"Тип ассортимента: ИМПОРТ")
        suppliers = [SupplierImport(i) for i in range(1, suppliers_num + 1)]

    if suppliers_num == 2:
        return suppliers[:2]

    return suppliers[:]


# In[ ]:


def get_calc(sups, assort_type):
    # Sending suppliers objects to the relative calculation modules
    sup_cnt = 0
    sups_rating = {}
    for sup in sups:
        sup_cnt += 1
        if assort_type == 1:
            formula = calc_inzak(sup.vars())
            sups_rating[f"Поставщик {sup_cnt}"] = formula
        elif assort_type == 2:
            formula = calc_WH(sup.vars())
            sups_rating[f"Поставщик {sup_cnt}"] = formula
        else:
            formula = calc_import(sup.vars())
            sups_rating[f"Поставщик {sup_cnt}"] = formula

    return sups_rating


# In[6]:


def main():
    try:
        assort_type = get_assort_type()
        suppliers_num = get_suppliers_num()

        sups = get_suppliers(assort_type, suppliers_num)
        sups_rating = get_calc(sups, assort_type)

        assessment = assess_sup(sups_rating)
        pprint(assessment)



    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    main()

