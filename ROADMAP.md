# ROADMAP

```bat
@echo off
for /f "tokens=2 delims==; " %%a in (' wmic process call create "notepad.exe" ^| find "ProcessId" ') do set PID=%%a
echo "%PID%"
pause
```

```bat
start "" "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" -P "ABC" -no-remote
for /F "TOKENS=1,2,*" %%a in ('tasklist /FI "IMAGENAME eq firefox.exe"') do set MyPID=%%b    
PING 127.0.0.1 -n 10 -w 1000 >NUL
taskkill /PID %MyPID% /T
```


# см. `pp-conf.py` с одним из вариантов хранилища конфигов

* https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c/42699779

```python
from flask import request
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
```

```python
from multiprocessing import Process

server = Process(target=app.run)
server.start()
# ...
server.terminate()
server.join()
```

```python
from werkzeug.serving import make_server

class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        log.info('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

def start_server():
    global server
    app = flask.Flask('myapp')
    ...
    server = ServerThread(app)
    server.start()
    log.info('server started')

def stop_server():
    global server
    server.shutdown()
```

```python
import requests
from threading import Timer
import time

LAST_REQUEST_MS = 0
@app.before_request
def update_last_request_ms():
    global LAST_REQUEST_MS
    LAST_REQUEST_MS = time.time() * 1000


@app.route('/seriouslykill', methods=['POST'])
def seriouslykill():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."


@app.route('/kill', methods=['POST'])
def kill():
    last_ms = LAST_REQUEST_MS
    def shutdown():
        if LAST_REQUEST_MS <= last_ms:  # subsequent requests abort shutdown
            requests.post('http://localhost:5000/seriouslykill')
        else:
            pass

    Timer(1.0, shutdown).start()  # wait 1 second
    return "Shutting down..."
```

# ---
```python
def shutdown():
    raise RuntimeError("Server going down")
```

```python
# ...
try:
    app.run(host="0.0.0.0")
except RuntimeError, msg:
    if str(msg) == "Server going down":
        pass # or whatever you want to do when the server goes down
    else:
        # appropriate handling/logging of other runtime errors
# and so on
# ...
```

```python
from flask import request

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# ...
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
```
