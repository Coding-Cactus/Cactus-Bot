import flask, os, pymongo
from threading import Thread


app = flask.Flask('')

myclient = pymongo.MongoClient(os.getenv("mongourl"))
mydb = myclient["cactusbot"]
userDB = mydb["users"]

def commas(i):
	s,i="",str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	return(i+s)

def get_pfp(user):
	try:
		user2 = client.get_user(user)
		if user2.is_avatar_animated():
			format = "gif"
		else:
			format = "png"
		pfp = str(user2.avatar_url_as(format=format))
	except AttributeError:
		pfp = None
	return pfp

def ranking():
	users = list(userDB.find(
		{
			"user_id": {"$ne": 691576874261807134}
		}
	).sort("score", -1))

	for item in users:
		item["user_tag"] = str(client.get_user(item["user_id"]))

	return users

@app.route('/')
def main():
	return flask.render_template('index.html')
	
@app.route('/leaderboard')
def leaders():
	ranks = ranking()
	
	for a in range(len(ranks)):
		ranks[a]["score"] = commas(ranks[a]["score"])

	return flask.render_template('leaderboard.html', ranks=ranks, len=lambda a:len(a))

@app.route('/user/<ID>')
def profile(ID):
	ID = int(ID)
	doc = userDB.find_one({"user_id": ID})
	if doc != None:
		pfp = get_pfp(ID)
		stats = doc
		stats['name'] = str(client.get_user(ID))
		ranks = ranking()
		for i in range(len(ranks)):
			if ranks[i]["user_id"] == ID:
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
	search = flask.request.form['name']
	found = False
	results = []
	for i in userDB.find():
		if search in str(i["user_id"]) or search.lower() in str(client.get_user(i)).lower():
			results.append({'id':i,'tag':str(client.get_user(i))})
			found = True
	
	return flask.render_template('search.html', found=found, results=results)


@app.route("/stats")
def stats():
	ranks = ranking()
	orderedScores = [i["score"] for i in ranks]
	orderedPlayers = [i["user_id"] for i in ranks]
	orderedNames = [i["user_tag"] for i in ranks]
	return flask.render_template("stats.html", orderedScores=orderedScores, orderedPlayers=orderedPlayers, orderedNames=orderedNames)


@app.route("/favicon.ico")
def favicon():
	return flask.send_file("favicon.ico")

def run():
	app.run('0.0.0.0')

def s(_client):
	global client
	client = _client
	server = Thread(target=run)
	server.start()