from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
API_KEY = os.getenv('API_KEY')

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
        return pd.DataFrame()  # Return an empty DataFrame on failure

def graficar_datos(datos):
    datos['Adj Close'].plot(title="Evolución del precio de GOOGL")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.show()

def monitorear_accion(intervalo=60):
    print("Iniciando monitoreo de las acciones de Google (GOOGL)...")
    while True:
        datos = obtener_datos_google()
        if datos.empty:
            print("Error: No se pudieron obtener datos de Alpha Vantage. Reintentando...")
        else:
            ultimo_precio = datos['Adj Close'].iloc[-1]  # Use .iloc for positional indexing
            print(f"Último precio: ${ultimo_precio:.2f}")
            graficar_datos(datos)
        time.sleep(intervalo)

if __name__ == "__main__":
    # Ejecutar monitoreo con intervalo de 5 minutos (300 segundos)
    monitorear_accion(intervalo=300)