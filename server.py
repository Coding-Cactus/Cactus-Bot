import flask, os
from easypydb import DB
from threading import Thread


app = flask.Flask('')

dbTOKEN = os.getenv('dbTOKEN')
userDB = DB('userDB', dbTOKEN)
pfpDB = DB('pfpDB', dbTOKEN)

def commas(i):
	s,i="",str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	return(i+s)

def ranking():
	scores = []
	users = []
	for i in userDB.data:
		if i != '691576874261807134':
			scores.append(userDB[i]['score'])
	scores.sort(reverse=True)
	for s in scores:
		for u in userDB.data:
			if userDB[u]['score'] == s and u not in users:
				users.append(u)
				break

	for x in range(len(users)):
		users[x] = [pfpDB['stuff'][users[x]]['name'], users[x]]


	return [scores, users]


@app.route('/')
def main():
	return flask.render_template('index.html')
	
@app.route('/leaderboard')
def leaders():
	userDB.load()
	pfpDB.load()
	ranks = ranking()
	orderedScores = ranks[0]
	orderedPlayers = ranks[1]
	
	for a in range(len(orderedScores)):
		orderedScores[a] = commas(orderedScores[a])

	return flask.render_template('leaderboard.html', players=orderedPlayers[:50], scores=orderedScores[:50], len=lambda a:len(a))

@app.route('/user/<ID>')
def profile(ID):
	userDB.load()
	pfpDB.load()
	if ID in userDB.data:
		pfp = pfpDB['stuff'][ID]['pfp']
		stats = userDB[ID]
		stats['name'] = pfpDB['stuff'][ID]['name']
		ranks = ranking()[1]
		for i in range(len(ranks)):
			if str(ranks[i][1]) == ID:
				stats['rank'] = str(i + 1)
				break		

		return flask.render_template("profile.html", user=stats, pfp=pfp, commas=lambda i: commas(i))
	else:
		return flask.render_template("notfound.html", user=ID)
	
@app.route('/search')
def show_search():
	return flask.render_template("search.html", found=False)
		
@app.route('/search', methods=['GET', 'POST'])
def search():
	userDB.load()
	pfpDB.load()
	search = flask.request.form['name']
	found = False
	results = []
	for i in userDB.data:
		if search in i or search.lower() in pfpDB['stuff'][i]['name'].lower():
			results.append({'id':i,'tag':pfpDB['stuff'][i]['name']})
			found = True
	
	return flask.render_template('search.html', found=found, results=results)


@app.route("/stats")
def stats():
	userDB.load()
	pfpDB.load()
	ranks = ranking()
	orderedScores = ranks[0]
	orderedPlayers = ranks[1]
	orderedNames = [name[0] for name in orderedPlayers]
	return flask.render_template("stats.html", orderedScores=orderedScores, orderedPlayers=orderedPlayers, orderedNames=orderedNames)


@app.route("/favicon.ico")
def favicon():
  return flask.send_file("favicon.ico")

def run():
	app.run('0.0.0.0')

def s():
	server = Thread(target=run)
	server.start()