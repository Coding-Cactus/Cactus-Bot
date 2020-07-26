import flask, replitdb, discord
from threading import Thread

client = discord.Client()

db = replitdb.Client()

app = flask.Flask('')

def commas(i):
	s,i="",str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	return(i+s)

@app.route('/')
def main():
	return flask.render_template('index.html')
	
@app.route('/leaderboard')
def leaders():
	scores = []
	players = []
	orderedScores = []
	ids =[]
	tags = []
	f = str(db.view('score')).split('\n')
	for i in f:
		if i.replace('\n','') != '' and i.replace('\n','').split('=')[0] != '691576874261807134':
			scores.append(int(i.replace('\n','').split('=')[1]))
			orderedScores.append(int(i.replace('\n','').split('=')[1]))
			players.append(int(i.replace('\n','').split('=')[0]))
	for n in str(db.view("names")).split("\n"):
		ids.append(n.split("=")[0])
		tags.append(n.split("=")[1])
	orderedScores.sort(reverse=True)
	orderedPlayers = []
	for x in orderedScores:
		orderedPlayers.append(tags[ids.index(str(players[scores.index(x)]))])
		scores[scores.index(x)] = ''
		
	
	for a in range(len(orderedScores)):
		orderedScores[a] = commas(orderedScores[a])
	
	return flask.render_template('leaderboard.html', players=orderedPlayers, scores=orderedScores, length=len(orderedScores))

@app.route("/favicon.ico")
def favicon():
  return flask.send_file("favicon.ico")

def run():
   app.run(host='0.0.0.0', port=8080)

def s():
  server = Thread(target=run)
  server.start()