from machine import ADC, Pin
from time import sleep
from microdot import Microdot, send_file

app = Microdot()

# Inicializar los canales ADC
adc0 = ADC(Pin(26))  # ADC canal 0 (GPIO 26)
adc1 = ADC(Pin(27))  # ADC canal 1 (GPIO 27) - salida del seguidor de tensión ZMP101B

# Parámetros del seguidor de tensión
offset = 1.64  # Voltaje de offset en la salida del seguidor de tensión
vp_output = 0.5  # Voltaje pico máximo (500 mVp)
adc_min_voltage = 1.14  # Voltaje mínimo esperado (correspondiente a -500mVp)
adc_max_voltage = 2.14  # Voltaje máximo esperado (correspondiente a +500mVp)
adc_resolution = 65535  # Resolución del ADC de 16 bits

def map_adc_to_voltage(adc_value, v_min, v_max):
    """Mapear valor ADC al rango de voltaje entre v_min y v_max."""
    return adc_value * (v_max - v_min) / adc_resolution + v_min

def calculate_rms_voltage(v_peak, v_peak_max=0.5, v_rms_max=220):
    """Convertir el valor de voltaje pico a voltaje eficaz."""
    return (v_peak / v_peak_max) * v_rms_max

# Ruta para devolver los datos en formato JSON
@app.route('/data')
def data(request):
    # Leer valores de los ADC
    adc1_value = adc1.read_u16()
    
    # Convertir el valor ADC a voltaje para el canal 1 (seguidor de tensión)
    tension_adc1 = map_adc_to_voltage(adc1_value, adc_min_voltage, adc_max_voltage)
    
    # Calcular la tensión eficaz a partir del valor pico medido
    tension_eficaz = calculate_rms_voltage(tension_adc1 - offset)  # Restamos el offset
    
    # Devolver los datos en formato JSON
    return {
        'tension_eficaz': f'{tension_eficaz:.2f}'
    }

# Para servir el archivo estático HTML
@app.route('/')
def index(request):
    return send_file('index.html')

# Para servir los archivos estáticos (CSS, JS)
@app.route('/<dir>/<file>')
def static_files(request, dir, file):
    return send_file("/" + dir + "/" + file)

# Iniciar el servidor
app.run(debug=True, port=80)
