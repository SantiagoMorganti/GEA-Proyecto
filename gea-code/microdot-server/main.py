import microdot 
from microdot import send_file

app = microdot.Microdot()

# Inicializar los canales ADC
adc0 = ADC(Pin(26))  # ADC canal 0 (GPIO 26) - para otra señal
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

# Ruta para la página principal
@app.route('/')
def index(request):
    # Leer valores de los ADC
    adc0_value = adc0.read_u16()  # Valor bruto en el rango de 0 a 65535
    adc1_value = adc1.read_u16()
    
    # Convertir el valor ADC a voltaje para el canal 1 (seguidor de tensión)
    tension_adc1 = map_adc_to_voltage(adc1_value, adc_min_voltage, adc_max_voltage)

@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/<dir>/<file>')
def styles(request,dir,file):
    return send_file("/"+dir+"/"+file)
app.run(port=80)

