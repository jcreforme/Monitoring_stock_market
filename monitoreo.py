# -*- coding: utf-8 -*-
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive credentials
API_KEY = os.getenv('API_KEY')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

if not API_KEY:
    raise ValueError("❌ API_KEY not found. Please set it in the .env file.")
if not EMAIL_PASSWORD:
    raise ValueError("❌ EMAIL_PASSWORD not found. Please set it in the .env file.")

# Get stock data for GOOGL
def obtener_datos_google():
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    try:
        data, meta_data = ts.get_intraday(symbol='GOOGL', interval='60min', outputsize='compact')
        data.rename(columns={'4. close': 'Adj Close'}, inplace=True)
        return data
    except Exception as e:
        print(f"Error al obtener datos de Alpha Vantage: {e}")
        return pd.DataFrame()

# Plot the data
def graficar_datos(datos):
    plt.figure(figsize=(10, 5))
    plt.plot(datos['Adj Close'], label='Adjusted Close Price', color='blue')
    plt.title('Google (GOOGL) Stock Price')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Send alert via email
def enviar_alerta_email(precio_actual):
    sender_email = "jcreforme@gmail.com"
    receiver_email = "jcreforme@gmail.com"

    subject = "Stock Price Alert: GOOGL"
    body = f"The stock price of GOOGL has reached ${precio_actual:.2f}!"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, EMAIL_PASSWORD)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Analyze trend direction
def mostrar_tendencia(datos):
    recent_trend = datos['Adj Close'].tail(3).diff().sum()
    if recent_trend > 0:
        print("📈 Trend: Upward")
    elif recent_trend < 0:
        print("📉 Trend: Downward")
    else:
        print("➖ Trend: Flat")

# Monitor GOOGL stock price
def monitorear_accion(intervalo=60, umbral_alerta=170):
    print("🚀 Iniciando monitoreo de acciones de GOOGL...")
    while True:
        datos = obtener_datos_google()
        if datos.empty:
            print("⚠️ Datos no disponibles. Reintentando en breve...")
        else:
            ultimo_precio = datos['Adj Close'].iloc[-1]
            print(f"📊 Último precio: ${ultimo_precio:.2f}")
            mostrar_tendencia(datos)

            # Export to CSV log (optional)
            datos.to_csv('GOOGL_intraday_log.csv', mode='a', header=False)

            # Trigger email alert
            if ultimo_precio >= umbral_alerta:
                print("⚠️ ALERTA: El precio ha alcanzado el umbral establecido!")
                enviar_alerta_email(ultimo_precio)

            graficar_datos(datos)

        time.sleep(intervalo)

# Main entry point
if __name__ == "__main__":
    monitorear_accion(intervalo=3600, umbral_alerta=170)
