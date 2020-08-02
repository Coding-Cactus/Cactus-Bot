import flask, replitdb, discord, os, asyncio, aiohttp, io
from threading import Thread

client = discord.Client()

db = replitdb.Client()

app = flask.Flask('')

def commas(i):
	s,i="",str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	return(i+s)
	
def ranking():
	scores = []
	players = []
	orderedScores = []
	f = str(db.view('score')).split('\n')
	for i in f:
		if i.replace('\n','') != '' and i.replace('\n','').split('=')[0] != '691576874261807134':
			scores.append(int(i.replace('\n','').split('=')[1]))
			orderedScores.append(int(i.replace('\n','').split('=')[1]))
			players.append(int(i.replace('\n','').split('=')[0]))
	orderedScores.sort(reverse=True)
	orderedPlayers = []
	ids = []
	tags = []
	for t in str(db.view('names')).split('\n'):
		ids.append(t.split('=')[0])
		tags.append(t.split('=')[1])
	for x in orderedScores:
		orderedPlayers.append([tags[ids.index(str(players[scores.index(x)]))],players[scores.index(x)]])
		scores[scores.index(x)] = ''
	return [orderedScores, orderedPlayers]


@app.route('/')
def main():
	return flask.render_template('index.html')
	
@app.route('/leaderboard')
def leaders():
	ranks = ranking()
	orderedScores = ranks[0]
	orderedPlayers = ranks[1]
	
	for a in range(len(orderedScores)):
		orderedScores[a] = commas(orderedScores[a])
	
	return flask.render_template('leaderboard.html', players=orderedPlayers, scores=orderedScores, length=len(orderedScores))

@app.route('/user/<ID>')
def profile(ID):
	pfps = str(db.view('pfps')).split('\n')
	names = str(db.view('names')).split('\n')
	tag = ''
	for n in names:
		if n.split('=')[0] == ID:
			tag = n.split('=')[1]
	if tag != '':
		for p in pfps:
			if p.split('=')[0] == ID:
				pfp = p.split('=')[1]
		stats = {}
		stats['name'] = tag
		scores = str(db.view('score')).split('\n')
		for s in scores:
			if s.split('=')[0] == ID:
				stats['height'] = commas(s.split('=')[1])
				break
		
		hpgs = str(db.view('growth')).split('\n')
		for h in hpgs:
			if h.split('=')[0] == ID:
				stats['hpg'] = commas(h.split('=')[1])
				break
				
		hpms = str(db.view('idle')).split('\n')
		for hpm in hpms:
			if hpm.split('=')[0] == ID:
				stats['hpm'] = commas(hpm.split('=')[1])
				break
		
		f = str(db.view('habitatsBought')).split('\n')
		f2 = []
		f3 = []
		h = str(db.view('habitats')).split('\n')
		h2 = []
		for x in f:
			if x != '':
				f2.append(x.split('=')[1])
				f3.append(x.split('=')[0])
		for i in h:
			h2.append(i.split('=')[1].split(',')[1])
		f4 = f2[f3.index(ID)].split(',')
		stats['mult'] = h2[f4.index('1')]
		
		ranks = ranking()[1]
		for i in range(len(ranks)):
			if str(ranks[i][1]) == ID:
				stats['rank'] = str(i + 1)
				break
		
		return flask.render_template("profile.html", user=stats, pfp=pfp)
	else:
		return flask.render_template("notfound.html", user=ID)
	
@app.route('/search')
def show_search():
	return flask.render_template("search.html", found=False)
		
@app.route('/search', methods=['GET', 'POST'])
def search():
	search = flask.request.form['name']
	found = False
	results = []
	names = str(db.view('names')).split('\n')
	for n in names:
		ID = n.split('=')[0]
		tag = n.split('=')[1]
		if search in ID or search.lower() in tag.lower():
			results.append({'id':ID,'tag':tag})
			found = True
	return flask.render_template('search.html', found=found, results=results)

@app.route("/favicon.ico")
def favicon():
  return flask.send_file("favicon.ico")

def run():
	app.run(host='0.0.0.0', port=8080)

def s():
	server = Thread(target=run)
	server.start()