import pandas as pd
import matplotlib.pyplot as plt
import io, base64
from flask import Flask, request, render_template
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    error = None
    plot_url = None
    forecast_table = None

    if request.method == 'POST':
        try:
            # Загружаем файл
            file = request.files['data_file']
            if not file:
                error = "Загрузите файл с данными."
            else:
                # Чтение CSV или Excel
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                # Проверяем столбцы
                if 'date' not in df.columns or 'demand' not in df.columns:
                    error = "Файл должен содержать столбцы: date, demand"
                else:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')

                    model_type = request.form.get('model_type', 'arima')

                    if model_type == 'arima':
                        # ARIMA модель
                        series = pd.Series(df['demand'].values, index=df['date'])
                        model = ARIMA(series, order=(2, 1, 2))
                        model_fit = model.fit()
                        forecast_values = model_fit.forecast(steps=14)

                        forecast_df = pd.DataFrame({
                            "date": pd.date_range(df['date'].iloc[-1] + pd.Timedelta(days=1), periods=14),
                            "forecast": forecast_values
                        })

                    else:  # Prophet
                        prophet_df = df.rename(columns={'date': 'ds', 'demand': 'y'})
                        model = Prophet()
                        model.fit(prophet_df)

                        future = model.make_future_dataframe(periods=14)
                        forecast = model.predict(future)
                        forecast_df = forecast[['ds', 'yhat']].tail(14).rename(columns={'ds': 'date', 'yhat': 'forecast'})

                    # Рисуем график
                    plt.figure(figsize=(10, 6))
                    plt.plot(df['date'], df['demand'], label="История")
                    plt.plot(forecast_df['date'], forecast_df['forecast'], '--', label="Прогноз")
                    plt.xlabel("Дата")
                    plt.ylabel("Спрос")
                    plt.title(f"Прогноз спроса ({model_type.upper()})")
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

    return render_template('forecast.html',
                           error=error,
                           plot_url=plot_url,
                           forecast_table=forecast_table)
