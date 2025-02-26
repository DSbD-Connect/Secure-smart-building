# Import flask module
from flask import Flask,redirect,request
import subprocess, threading, os

nmap_result = ''
def set_nmap_result(x):
    global nmap_result
    nmap_result_new = '<html><head><meta http-equiv="refresh" content="5"></head><body><a href="/">main page</a><br><hr style="width:25%;text-align:left;margin-left:0">'
    nmap_result_new = nmap_result_new+x
    nmap_result_new = nmap_result_new+'</body></html>'
    nmap_result = nmap_result_new
set_nmap_result('No scan done')

main_page = """
<!DOCTYPE html>
<html>
<body>
<div style="padding:10px; border: thin solid black;width: max-content">
<h3>CyberHive Connect</h3>
<form action="connect_on">
<button type="submit">Connect On</button>
</form>
<br>
<form action="connect_off">
<button type="submit">Connect Off</button>
</form>
<br>
</div><br>
<div style="padding:10px; border: thin solid black;width: max-content">
<h3>Network scanning</h3>
<form action="run_scan">
    <button type="submit">Run nmap scan</button>
</form>
<br>
<a href="results">Scan results</a>
<br>
</div><br>
<div style="padding:10px; border: thin solid black;width: max-content">
<h3>Smart bulb control</h3>
<p>Current target IP: ===TIP===</p>
<form action="set_ip" method="POST">
<button type="submit">Set target IP</button>
<input type="text" name="ip_addr">
</form>
<br>
<form action="turn_on" style="float:left">
<button type="submit">On</button>
</form>
<form action="turn_off" style="float:left;padding-left:10px">
<button type="submit">Off</button>
</form>
<br>
</div><br>
</body>
</html>
"""

app = Flask(__name__)

def nmap_scan():
    set_nmap_result('Scanning 192.168.38.0/24 ...')
    # We add the route to the subnet with the smart devices
    # because this will not be known by default
    os.system('ip route add  192.168.38.0/24 via 192.168.37.200 dev eth0')
    x = subprocess.run(['nmap','192.168.38.0/24'],
                       capture_output = True,
                       text = True)
    y = x.stdout.replace('\n','<br>')
    set_nmap_result(y)

ip_addr = ''
@app.route('/set_ip',methods=('GET', 'POST'))
def set_ip():
    global ip_addr
    ip_addr = request.form['ip_addr']
    return redirect('/')

@app.route('/connect_on')
def connect_on():
    os.system('./switch-mode on')
    return redirect('/')

@app.route('/connect_off')
def connect_off():
    os.system('./switch-mode off')
    return redirect('/')

@app.route('/turn_on')
def turn_on():
    os.system('./tplink_smartplug.py -t '+ip_addr+' -c on')
    return redirect('/')

@app.route('/turn_off')
def turn_off():
    os.system('./tplink_smartplug.py -t '+ip_addr+' -c off')
    return redirect('/')

@app.route('/')
def index():
    return main_page.replace('===TIP===',ip_addr)

@app.route('/results')
def results():
    return nmap_result

@app.route('/run_scan')
def run_scan():
    thread = threading.Thread(target=nmap_scan,args=())
    thread.start()
    return redirect('results')

# main driver function
if __name__ == "__main__":
    app.run()


