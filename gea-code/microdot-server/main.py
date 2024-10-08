from machine import ADC, Pin
from time import sleep, ticks_us, ticks_diff
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

# Variables para calcular frecuencia
last_cross_time = ticks_us()  # Último tiempo de cruce por cero
frequency = 0  # Frecuencia de la señal
rpm = 0  # Revoluciones por minuto

def map_adc_to_voltage(adc_value, v_min, v_max):
    """Mapear valor ADC al rango de voltaje entre v_min y v_max."""
    return adc_value * (v_max - v_min) / adc_resolution + v_min

def calculate_rms_voltage(v_peak, v_peak_max=0.5, v_rms_max=220):
    """Convertir el valor de voltaje pico a voltaje eficaz."""
    return (v_peak / v_peak_max) * v_rms_max

def calculate_rpm():
    """Detectar cruce por cero y calcular la frecuencia y RPM."""
    global last_cross_time, frequency, rpm
    
    # Leer el valor del ADC y convertirlo a voltaje
    adc1_value = adc1.read_u16()
    tension_adc1 = map_adc_to_voltage(adc1_value, adc_min_voltage, adc_max_voltage)
    
    # Detectar el cruce por cero: cuando la señal cambia de positivo a negativo o viceversa
    if tension_adc1 - offset < 0.01 and tension_adc1 - offset > -0.01:  # Cerca del cruce por cero
        current_time = ticks_us()  # Obtener el tiempo actual
        period_us = ticks_diff(current_time, last_cross_time)  # Calcular el periodo en microsegundos
        if period_us > 0:
            frequency = 1_000_000 / (2 * period_us)  # Frecuencia en Hz (2 cruces por ciclo)
            rpm = frequency * 60  # Convertir a revoluciones por minuto (RPM)
        last_cross_time = current_time  # Actualizar el último cruce por cero

@app.route('/data')
def data(request):
    # Calcular la tensión eficaz
    adc1_value = adc1.read_u16()
    tension_adc1 = map_adc_to_voltage(adc1_value, adc_min_voltage, adc_max_voltage)
    tension_eficaz = calculate_rms_voltage(tension_adc1 - offset)
    
    # Calcular la frecuencia y RPM
    calculate_rpm()
    
    # Devolver los datos en formato JSON
    return {
        'tension_eficaz': f'{tension_eficaz:.2f}',
        'rpm': f'{rpm:.2f}'
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
