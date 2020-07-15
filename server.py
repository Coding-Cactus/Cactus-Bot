from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return 'Cactus Bot Online! 🌵🌵🌵'

def run():
   app.run(host='0.0.0.0', port=8080)

def s():
  server = Thread(target=run)
  server.start()