import flask
from threading import Thread

app = flask.Flask('')

@app.route('/')
def main():
	return flask.render_template('index.html')

@app.route("/favicon.ico")
def favicon():
  return flask.send_file("favicon.ico")

def run():
   app.run(host='0.0.0.0', port=8080)

def s():
  server = Thread(target=run)
  server.start()
