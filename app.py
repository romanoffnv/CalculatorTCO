from flask import Flask, render_template, request, send_file, session
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import logging
import json
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Необходим для использования сессий

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Фиксированная ставка ЦБ
CBR_RATE = 0.25  # 25% годовых

# ==================== Функции расчёта TCO ====================

def calculate_tco(total_goods_cost, logistics, storage_cost, financing_cost, risks, retro_bonus, moq, returnable):
    """
    Рассчитывает TCO с учётом новых параметров.
    - Применяет ретро-бонус как скидку к стоимости товаров.
    - Добавляет MOQ к рискам (высокий MOQ увеличивает риски/затраты).
    - Если товар не возвратный, добавляет штраф (5% от стоимости товаров) к рискам.
    TCO = Прямые затраты + Финансирование + Скорректированные риски
    """
    # Применение ретро-бонуса
    discounted_goods_cost = total_goods_cost * (1 - retro_bonus / 100)

    direct_costs = discounted_goods_cost + logistics + storage_cost

    # Корректировка рисков
    adjusted_risks = risks + moq
    if not returnable:
        adjusted_risks += total_goods_cost * 0.05  # Штраф 5% за невозвратный товар

    tco = direct_costs + financing_cost + adjusted_risks
    return tco, direct_costs, adjusted_risks

def process_supplier_data(form_data, supplier_num, assortment_type):
    """
    Обрабатывает данные поставщика для TCO.
    - Учитывает тип ассортимента ('warehouse', 'inzak', 'import').
    - Рассчитывает стоимость хранения: для 'inzak' и 'cs' или 'warehouse' пропорционально дням (1200 * объём * (дни/30)).
    """
    logger.debug(f"Обработка поставщика {supplier_num}")
    prefix = f"supplier{supplier_num}_"

    # Получение имени поставщика
    name = form_data.get(f"{prefix}name", f"Поставщик {supplier_num}").strip()

    # Инициализация shipping_type
    shipping_type = "cs" if assortment_type == "warehouse" else form_data.get(f"{prefix}shipping_type", "direct").strip()

    # Обработка для типа 'import' (заглушка)
    if assortment_type == "import":
        total_goods_cost_str = form_data.get(f"{prefix}total_goods_cost", "").strip()
        product_volume_m3_str = form_data.get(f"{prefix}product_volume_m3", "").strip()
        customs_duty_str = form_data.get(f"{prefix}customs_duty", "").strip()
        transport_cost_str = form_data.get(f"{prefix}transport_cost", "").strip()
        insurance_cost_str = form_data.get(f"{prefix}insurance_cost", "").strip()
        customs_clearance_str = form_data.get(f"{prefix}customs_clearance", "").strip()
        moq_str = form_data.get(f"{prefix}moq", "").strip()
        payment_delay_str = form_data.get(f"{prefix}payment_delay", "").strip()
        retro_bonus_str = form_data.get(f"{prefix}retro_bonus", "").strip()
        risks_str = form_data.get(f"{prefix}risks", "").strip()
        returnable = form_data.get(f"{prefix}returnable", "Y").upper() == "Y"

        # Проверка обязательных полей
        required_fields = [total_goods_cost_str, product_volume_m3_str, customs_duty_str, transport_cost_str, payment_delay_str, risks_str]
        if not all(field for field in required_fields):
            logger.error(f"Отсутствуют обязательные поля для поставщика {supplier_num} (import)")
            return None

        try:
            total_goods_cost = float(total_goods_cost_str)
            product_volume_m3 = float(product_volume_m3_str)
            customs_duty = float(customs_duty_str)
            transport_cost = float(transport_cost_str)
            insurance_cost = float(insurance_cost_str) if insurance_cost_str else 0
            customs_clearance = float(customs_clearance_str) if customs_clearance_str else 0
            moq = float(moq_str) if moq_str else 0
            payment_delay = float(payment_delay_str)
            retro_bonus = float(retro_bonus_str) if retro_bonus_str else 0
            risks = float(risks_str)
        except ValueError as e:
            logger.error(f"Ошибка преобразования данных для поставщика {supplier_num} (import): {str(e)}")
            return None

        # Заглушка: возвращаем данные с нулевыми расчетами
        return {
            "name": name,
            "total_goods_cost": total_goods_cost,
            "logistics": transport_cost,  # Используем transport_cost как аналог logistics
            "storage_cost": 0,
            "financing_cost": 0,
            "risks": risks,
            "retro_bonus": retro_bonus,
            "moq": moq,
            "returnable": "Да" if returnable else "Нет",
            "direct_costs": total_goods_cost + customs_duty + transport_cost + insurance_cost + customs_clearance,
            "tco": 0,
            "shipping_type": "import",
            "storage_days": 0,
            "product_volume_m3": product_volume_m3
        }

    # Обработка для типа 'warehouse'
    if assortment_type == "warehouse":
        unit_price_str = form_data.get(f"{prefix}unit_price", "").strip()
        min_batch_str = form_data.get(f"{prefix}min_batch", "").strip()
        unit_volume_str = form_data.get(f"{prefix}unit_volume", "").strip()
        payment_delay_str = form_data.get(f"{prefix}payment_delay", "").strip()
        retro_bonus_str = form_data.get(f"{prefix}retro_bonus", "").strip()
        storage_days_str = form_data.get(f"{prefix}storage_days", "").strip()
        risks_str = form_data.get(f"{prefix}risks", "").strip()
        returnable = form_data.get(f"{prefix}returnable", "Y").upper() == "Y"

        # Проверка обязательных полей
        required_fields = [unit_price_str, min_batch_str, unit_volume_str, payment_delay_str, retro_bonus_str, storage_days_str, risks_str]
        if not all(field for field in required_fields):
            logger.error(f"Отсутствуют обязательные поля для поставщика {supplier_num} (warehouse)")
            return None

        try:
            unit_price = float(unit_price_str)
            min_batch = float(min_batch_str)
            total_goods_cost = unit_price * min_batch
            unit_volume = float(unit_volume_str)
            product_volume_m3 = unit_volume * min_batch
            moq = total_goods_cost  # MOQ равен общей стоимости товаров
            payment_delay = float(payment_delay_str)
            retro_bonus = float(retro_bonus_str)
            storage_days = float(storage_days_str)
            risks = float(risks_str)
        except ValueError as e:
            logger.error(f"Ошибка преобразования данных для поставщика {supplier_num} (warehouse): {str(e)}")
            return None
    else:  # inzak
        total_goods_cost_str = form_data.get(f"{prefix}total_goods_cost", "").strip()
        product_volume_m3_str = form_data.get(f"{prefix}product_volume_m3", "").strip()
        moq_str = form_data.get(f"{prefix}moq", "").strip()
        retro_bonus_str = form_data.get(f"{prefix}retro_bonus", "").strip()
        risks_str = form_data.get(f"{prefix}risks", "").strip()
        returnable = form_data.get(f"{prefix}returnable", "Y").upper() == "Y"

        # Проверка обязательных полей
        required_fields = [total_goods_cost_str, product_volume_m3_str, retro_bonus_str, risks_str]
        if shipping_type == "cs":
            required_fields.append(form_data.get(f"{prefix}storage_days", "").strip())
        if not all(field for field in required_fields):
            logger.error(f"Отсутствуют обязательные поля для поставщика {supplier_num} (inzak)")
            return None

        try:
            total_goods_cost = float(total_goods_cost_str)
            product_volume_m3 = float(product_volume_m3_str)
            moq = float(moq_str) if moq_str else 0
            retro_bonus = float(retro_bonus_str)
            risks = float(risks_str)
        except ValueError as e:
            logger.error(f"Ошибка преобразования данных для поставщика {supplier_num} (inzak): {str(e)}")
            return None

    try:
        logistics_str = form_data.get(f"{prefix}logistics", "").strip()
        if not logistics_str and assortment_type != "import":
            logger.error(f"Отсутствует поле логистики для поставщика {supplier_num}")
            return None
        logistics = float(logistics_str) if logistics_str else 0

        financing_cost = 0
        if assortment_type == "warehouse":
            payment_delay = float(payment_delay_str)
            financing_cost = (payment_delay / 365) * CBR_RATE * total_goods_cost
        elif assortment_type == "inzak":
            partial_prepayment = form_data.get(f"{prefix}partial_prepayment", "N").upper()
            payment_delay_str = form_data.get(f"{prefix}payment_delay", "").strip()
            if partial_prepayment == "Y":
                prepayment_percent_str = form_data.get(f"{prefix}prepayment_percent", "").strip()
                if not (prepayment_percent_str and payment_delay_str):
                    logger.error(f"Отсутствуют данные предоплаты для поставщика {supplier_num} (inzak)")
                    return None
                prepayment_percent = float(prepayment_percent_str)
                payment_delay = float(payment_delay_str)
                prepayment_amount = total_goods_cost * (prepayment_percent / 100)
                remaining_amount = total_goods_cost - prepayment_amount
                financing_cost = (payment_delay / 365) * CBR_RATE * remaining_amount
            else:
                if not payment_delay_str:
                    logger.error(f"Отсутствует отсрочка платежа для поставщика {supplier_num} (inzak, без предоплаты)")
                    return None
                payment_delay = float(payment_delay_str)
                financing_cost = (payment_delay / 365) * CBR_RATE * total_goods_cost

        # Расчёт стоимости хранения
        storage_cost = 0
        storage_days = 0
        if assortment_type == "warehouse" or (assortment_type == "inzak" and shipping_type == "cs"):
            storage_days_str = form_data.get(f"{prefix}storage_days", "").strip()
            if not storage_days_str:
                logger.error(f"Отсутствует срок хранения для поставщика {supplier_num}")
                return None
            storage_days = float(storage_days_str)
            storage_cost = 1200 * product_volume_m3 * (storage_days / 30)

        tco, direct_costs, adjusted_risks = calculate_tco(
            total_goods_cost, logistics, storage_cost, financing_cost, risks,
            retro_bonus, moq, returnable
        )

        return {
            "name": name,
            "total_goods_cost": total_goods_cost,
            "logistics": logistics,
            "storage_cost": storage_cost,
            "financing_cost": financing_cost,
            "risks": adjusted_risks,
            "retro_bonus": retro_bonus,
            "moq": moq,
            "returnable": "Да" if returnable else "Нет",
            "direct_costs": direct_costs,
            "tco": tco,
            "shipping_type": shipping_type,
            "storage_days": storage_days,
            "product_volume_m3": product_volume_m3
        }
    except ValueError as e:
        logger.error(f"Ошибка обработки данных поставщика {supplier_num}: {str(e)}")
        return None

# ==================== Маршруты Flask ====================

@app.route('/')
def index():
    return render_template('index.html', num_suppliers=2, assortment_type='inzak')

@app.route('/tco', methods=['POST'])
def tco():
    error = None
    results = []
    plot_url = None
    assortment_type = request.form.get('assortment_type', 'inzak')
    num_suppliers = int(request.form.get('num_suppliers', 2))

    try:
        for i in range(1, num_suppliers + 1):
            supplier_data = process_supplier_data(request.form, i, assortment_type)
            if supplier_data is None:
                error = f"Ошибка: Неверные или отсутствующие данные для поставщика {i}"
                return render_template('index.html', error=error, num_suppliers=num_suppliers, assortment_type=assortment_type)
            results.append(supplier_data)

        if not results:
            error = "Нет данных для расчёта."
        else:
            # Определение лучшего поставщика
            min_tco = min(res['tco'] for res in results)
            for res in results:
                res['recommendation'] = 'Лучший' if res['tco'] == min_tco else 'Допустимый'

            # Сохранение результатов в сессии для экспорта
            session['results'] = results
            session['assortment_type'] = assortment_type

            # Построение графика
            plt.figure(figsize=(10, 6))
            names = [res['name'] for res in results]
            tcos = [res['tco'] for res in results]
            plt.bar(names, tcos, color=['#10b981' if res['recommendation'] == 'Лучший' else '#3b82f6' for res in results])
            plt.xlabel('Поставщики')
            plt.ylabel('TCO (руб.)')
            plt.title('Сравнение TCO по поставщикам')
            plt.grid(True, axis='y')
            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close()

    except Exception as e:
        error = f"Ошибка: {str(e)}"
        logger.error(f"Ошибка в /tco: {str(e)}")

    return render_template('results.html', results=results, error=error, plot_url=plot_url, assortment_type=assortment_type)

@app.route('/export_excel', methods=['GET'])
def export_excel():
    try:
        # Получение данных из сессии
        results = session.get('results')
        assortment_type = session.get('assortment_type')

        if not results or not assortment_type:
            logger.error("Отсутствуют данные результатов или типа ассортимента в сессии")
            return render_template('results.html', error="Ошибка: Данные для экспорта недоступны. Пожалуйста, выполните расчёт заново.", results=[])

        if assortment_type not in ['inzak', 'warehouse']:
            logger.error(f"Экспорт не поддерживается для типа ассортимента: {assortment_type}")
            return render_template('results.html', error="Экспорт доступен только для типов ИНЗАК и Складской ассортимент", results=results)

        # Создание Excel файла
        wb = Workbook()
        ws = wb.active
        ws.title = "Результаты TCO"

        # Заголовки таблицы
        headers = [
            "Поставщик", "Общая стоимость товаров (руб.)", "Логистические расходы (руб.)",
            "Стоимость хранения (руб.)", "Стоимость отсрочки (руб.)", "Риски (руб.)",
            "Ретро-бонус (%)", "MOQ (руб.)", "Возвратный товар", "Прямые затраты (руб.)",
            "TCO (руб.)", "Рекомендация"
        ]
        ws.append(headers)

        # Заполнение данными
        for res in results:
            row = [
                res['name'],
                round(res['total_goods_cost'], 2),
                round(res['logistics'], 2),
                round(res['storage_cost'], 2),
                round(res['financing_cost'], 2),
                round(res['risks'], 2),
                round(res['retro_bonus'], 2),
                round(res['moq'], 2),
                res['returnable'],
                round(res['direct_costs'], 2),
                round(res['tco'], 2),
                res['recommendation']
            ]
            ws.append(row)

        # Сохранение файла в память
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Отправка файла пользователю
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"TCO_Results_{assortment_type}.xlsx"
        )
    except Exception as e:
        logger.error(f"Ошибка при экспорте в Excel: {str(e)}")
        return render_template('results.html', error=f"Ошибка при экспорте: {str(e)}", results=results or [])

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    error = None
    plot_url = None
    forecast_table = None

    if request.method == 'POST':
        try:
            file = request.files['data_file']
            if not file:
                error = "Загрузите файл с данными."
            else:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                if 'date' not in df.columns or 'demand' not in df.columns:
                    error = "Файл должен содержать столбцы: date, demand"
                else:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    series = pd.Series(df['demand'].values, index=df['date'])
                    model = ARIMA(series, order=(2, 1, 2))
                    model_fit = model.fit()
                    forecast_values = model_fit.forecast(steps=14)
                    forecast_df = pd.DataFrame({
                        "date": pd.date_range(df['date'].iloc[-1] + pd.Timedelta(days=1), periods=14),
                        "forecast": forecast_values
                    })
                    plt.figure(figsize=(10, 6))
                    plt.plot(df['date'], df['demand'], label="История")
                    plt.plot(forecast_df['date'], forecast_df['forecast'], '--', label="Прогноз")
                    plt.xlabel("Дата")
                    plt.ylabel("Спрос")
                    plt.title("Прогноз спроса (ARIMA)")
                    plt.legend()
                    plt.grid(True)
                    img = io.BytesIO()
                    plt.savefig(img, format='png', bbox_inches='tight')
                    img.seek(0)
                    plot_url = base64.b64encode(img.getvalue()).decode()
                    plt.close()
                    forecast_table = forecast_df.to_dict(orient='records')
        except Exception as e:
            error = f"Ошибка: {str(e)}"
            logger.error(f"Ошибка в /forecast: {str(e)}")

    return render_template('forecast.html',
                           error=error,
                           plot_url=plot_url,
                           forecast_table=forecast_table)

if __name__ == '__main__':
    app.run(debug=True)