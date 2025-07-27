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

# Get the API key from the environment
API_KEY = os.getenv('API_KEY')
password = os.getenv('EMAIL_PASSWORD')

if not API_KEY:
    raise ValueError("API_KEY not found. Please set it in the .env file.")

def obtener_datos_google():
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    try:
        # Fetch intraday data for GOOGL with a 60-minute interval
        data, meta_data = ts.get_intraday(symbol='GOOGL', interval='60min', outputsize='compact')
        data.rename(columns={'4. close': 'Adj Close'}, inplace=True)  # Rename column for compatibility
        return data
    except Exception as e:
        print(f"Error al obtener datos de Alpha Vantage: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

def graficar_datos(datos):
    plt.figure(figsize=(10, 5))
    plt.plot(datos['Adj Close'], label='Adjusted Close Price')
    plt.title('Google (GOOGL) Stock Price')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid()
    plt.show()

# Function to send an email alert
def enviar_alerta_email(precio_actual):
    # Email configuration
    sender_email = "jcreforme@gmail.com"
    receiver_email = "jcreforme@gmail.com"
    password = os.getenv('EMAIL_PASSWORD')

    # Email content
    subject = "Stock Price Alert: GOOGL"
    body = f"The stock price of GOOGL has reached ${precio_actual:.2f}!"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Monitoring function
def monitorear_accion(intervalo=60):
    print("Iniciando monitoreo de las acciones de Google (GOOGL)...")
    while True:
        datos = obtener_datos_google()
        if datos.empty:
            print("Error: No se pudieron obtener datos de Alpha Vantage. Reintentando...")
        else:
            ultimo_precio = datos['Adj Close'].iloc[-1]  # Use .iloc for positional indexing
            print(f"Último precio: ${ultimo_precio:.2f}")
            
            # Check if the price equals or exceeds $170
            if ultimo_precio >= 170:
                print("⚠️ ALERTA: El precio ha alcanzado o superado los $170!")
                enviar_alerta_email(ultimo_precio)  # Send email alert
            
            graficar_datos(datos)
        time.sleep(intervalo)

# Start monitoring
if __name__ == "__main__":
    monitorear_accion(intervalo=60)