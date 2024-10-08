import microdot 
from microdot import send_file

app = microdot.Microdot()

@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/<dir>/<file>')
def styles(request,dir,file):
    return send_file("/"+dir+"/"+file)
app.run(port=80)

