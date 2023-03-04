import discord, os, time, math, threading, sys, asyncio, server, pymongo
from discord.ext import commands


myclient = pymongo.MongoClient(os.getenv("mongourl"))
mydb = myclient["cactusbot"]
userDB = mydb["users"]
generalDB = mydb["general"]

BANNED = generalDB.find_one({"name": "banned"})['banned']

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix='=', help_command=None, case_insensitive=True, intents=intents)



#-------------------------------------------------------
#							Status/On Ready
#-------------------------------------------------------

@client.event
async def on_ready():
	print('Good Morning')
	activity = discord.Activity(name='for =help', type=discord.ActivityType.watching)
	await client.change_presence(activity=activity)
	print('In ' + str(len(client.guilds)) + ' servers')
	global uptime
	uptime = time.time()
	set_interval(perMin, 60)

#-------------------------------------------------------
#						Errors
#-------------------------------------------------------

@client.event
async def on_command_error(ctx, error):
	channel = client.get_channel(730420490296098846)
	embed1 = discord.Embed(color=0xff0000,title='ERROR', description=str(error))
	embed2 = discord.Embed(color=0xff0000,title='ERROR', description='```' + str(ctx.message.content) + '```' + str(error))
	embed2.set_footer(text='Author:\n' + str(ctx.author) + '\n' + str(ctx.author.id) + '\n\nChannel:\n' + str(ctx.channel) + '\n' + str(ctx.channel.id) + '\n\nServer:\n' + str(ctx.guild) + '\n' + str(ctx.guild.id))

	msg = await ctx.send(embed=embed1)
	await channel.send(embed=embed2)
	await asyncio.sleep(5)
	await msg.delete()

#-------------------------------------------------------
#						Help
#-------------------------------------------------------

@client.command()
async def help(ctx, command=None):
	if not command:
		embed=discord.Embed(title="Commands", color=0x00ff00)
		embed.add_field(name='info', value='Info about the bot, also its invite link.', inline=False)
		embed.add_field(name='prof', value='See your profile (stats).')
		embed.add_field(name='grow', value='Grow and try to become a big cactus!')
		embed.add_field(name='shop', value='View the shop where you can trade in some of your height for increases in height per growth.')
		embed.add_field(name='buy', value='Buy an item from the shops\nIn the form: `=buy item ammount`(amount is optional (write max if you you want the max)).')
		embed.add_field(name='idle-shop', value='View the shop where you can trade in some of your height for increases in height per minute.')
		embed.add_field(name='habitats', value='Look at the habitats that you could move to (habitats increase multiplier).')
		embed.add_field(name='change-habitat', value='Move to a new habitat (increases multplier).')
		embed.add_field(name='daily-reward', value='Collect your daily reward.')
		embed.add_field(name='leaderboard', value='View leaderboard.')
		embed.add_field(name='feedback', value='Send feedback on how to improve this bot.\ne.g. new item for the shops.')
		embed.add_field(name='bug', value='Report a bug (please be specific).')
		embed.add_field(name='hug', value='Give your cactus a hug, :).')
		embed.set_footer(text='Prefix is \'=\'')
		await ctx.send(embed=embed)


#-------------------------------------------------------
#						Functions
#-------------------------------------------------------

bold = lambda a: '**'+str(a)+'**'

def units(num):
	l=len(num.split(","))
	u=["", "k", "M", "G", "T", "P", "E", "Y"]
	return num.split(",")[0]+"."+num.split(",")[1]+" "+u[l-1]

def commas(i,u=True):
	if u:
		if len(i)<3:return i+" c"
		if len(i)<6:return str(int(i)/100)+" "
	s=""
	if u:i=str(round(int(i)/100))
	else:i=str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	if u:return units(i+s)
	else:return i+s+" c" 

async def send_embed(ctx, t, d, good):
	if good:
		colour = 0x00fff00
	else:
		colour = 0xff0000
	embed = discord.Embed(
		title=t,
		description=d,
		color=colour
	)
	await ctx.send(embed=embed)

def userExists(userID):	
	return userDB.find_one({"user_id": userID}) != None

def addUser(userID):
	newBought = lambda shopType: [0 for i in generalDB.find_one({"name": shopType})[shopType]]

	userDB.insert_one({
		"user_id": userID,
		'score':0,
		'hpg':2,
		'hpm':0,
		'multiplier':1,
		'bought': newBought('shop'),
		'idleBought': newBought('idleShop'),
		'dailyTime':0,
		'growTime':0,
	})

def dailyCalc(now, last):
	difference = now - last
	difference2 = 3600*22 - difference
	if difference >= 3600 * 22:
		msg = 'Ready!'
	else:
		hrs = str(round(difference2 // 3600))
		mins = str(round((difference2 - int(hrs) * 3600) // 60))
		secs = str(round(difference2 - int(hrs) *3600 - int(mins) * 60))
		msg='Ready in: ' + bold(hrs) + 'hrs ' + bold(mins) + 'mins ' + bold(secs) + 'secs'
	return msg

def getShopPage(user, page, shopType):
	if shopType == 'shop':
		increase = 'hpg'
	elif shopType == 'idleShop':
		increase = 'hpm'
	shop = generalDB.find_one({"name": shopType})[shopType]
	msg = '\n```\n'
	items = []
	incs = []
	for a in shop:
		incs.append(shop[a][increase])
	incs.sort()
	for p in incs:
		for s in shop:
			if shop[s][increase] == p:
				items.append(s)
				break

	numPages = math.ceil(len(shop) / 5)
	if page < 1:
		page = 1
	if page < numPages:
		items = items[(page-1)*5:page*5]
	elif page == numPages:
		items = items[(page-1)*5:]
	else:
		items = ''
	if items != '':
		for i in items:
			msg += '\n' + i.title() + '\nPrice: ' + commas(str(fullPrice(i, user, 1, shopType))) + 'm\nIncrease in ' + increase + ': ' + commas(str(shop[i][increase])) + 'm\n'
	else:
		msg = "\n```Page '" + str(page) + "' not found."
	return msg + '```'

def fullPrice(item, user, num, shopType):
	if shopType == 'shop':
		bought = 'bought'
	elif shopType == 'idleShop':
		bought = 'idleBought'
	index = 0
	shop = generalDB.find_one({"name": shopType})[shopType]
	for i in shop:
		if i == item:
			break
		else:
			index += 1
	total = 0
	for n in range(0,num):
		total += round(shop[item]['price'] * 1.138 ** (userDB.find_one({"user_id": user})[bought][index] + n))
	return total

def findMax(item, userID, shopType):
	doc = userDB.find_one({"user_id": userID})
	loops = 0
	score = doc['score']
	price = generalDB.find_one({"name": shopType})[shopType][item]['price']
	if shopType == 'shop':
		bought = 'bought'
	elif shopType == 'idleShop':
		bought = 'idleBought'
	boughtLst = doc[bought]
	index = 0
	for i in generalDB.find_one({"name": shopType})[shopType]:
		if i == item:
			break
		else:
			index += 1
	startBought = boughtLst[index]
	total = round(price * 1.138 ** startBought)
	while score >= total:
		loops += 1
		total += round(price * 1.138 ** (startBought + loops))
	return loops


def showHabitats(user):
	multiplier = userDB.find_one({"user_id": user})['multiplier']
	habitats = generalDB.find_one({"name": "habitats"})["habitats"]
	desc = '\n```\n'
	for i in habitats:
		desc += '\n' + i.title() + '\nPrice: '
		mult = habitats[i]['multiplier']
		if mult < multiplier:
			desc += "You can't go back here"
		elif mult == multiplier:
			desc += "Current Location"
		else:
			desc += commas(str(habitats[i]['price'])) + 'm'
		desc += '\nMultiplier: ' + str(mult) + 'x\n'
	return desc + '```'

def showLeaderboard(page):
	users = list(userDB.find(
		{
			"user_id": {"$ne": 691576874261807134}
		}
	).sort("score", -1))

	numPages = math.ceil(len(users) / 10)

	if page < 1:
		page = 1
	if page > numPages:
		page = numPages
	if page < numPages:
		scores = [i["score"] for i in users[(page-1) * 10: page * 10]]
		users = [i["user_id"] for i in users[(page-1) * 10: page * 10]]
	else:
		scores = [i["score"] for i in users[(page-1) * 10:]]
		users = [i["user_id"] for i in users[(page-1) * 10:]]
	desc ='\n```\n'
	for x in range(len(scores)):
		desc += str((page-1)*10+x+1) + '. ' + str(client.get_user(users[x])) +': ' + commas(str(scores[x])) + 'm\n'
	return desc + '```'


def perMin():
	for i in userDB.find():
		stats = i
		increase = i['hpm']
		stats['score'] += increase * stats['multiplier']
		userDB.update_one({"user_id": i["user_id"]}, {"$set": stats})

def set_interval(func, sec):
	def func_wrapper():
		set_interval(func, sec)
		perMin()
	t = threading.Timer(sec, func_wrapper)
	t.start()
	return t

#-------------------------------------------------------
#						Commands
#-------------------------------------------------------

@client.command()
async def ping(ctx):
	embed = discord.Embed(
		title='PING!',
		description='',
		color=0xcc0000
	)
	start = time.time()
	msg = await ctx.send(embed=embed)
	end = time.time() - start
	embed2 = discord.Embed(
		title='PING!',
		description=str(end) + ' seconds.',
		color=0x00cc00
	)
	await msg.edit(embed=embed2)


@client.command(aliases=['info','uptime','source','source-code','prefix'])
async def invite(ctx):
	now = time.time()
	diff = now - uptime
	hrs = str(round(diff // 3600))
	mins = str(round((diff - int(hrs) * 3600) // 60))
	secs = str(round(diff - int(hrs) *3600 - int(mins) * 60))
	timestr = bold(hrs + 'hrs ' + mins + 'mins ' + secs + 'secs')
	embed = discord.Embed(color=0x00ff00,title='Info',description='Prefix: `=`\nSource Code: https://github.com/Coding-Cactus/Cactus-Bot\nInvite Link: https://discordapp.com/oauth2/authorize?client_id=700051830394060801&scope=bot&permissions=0\nUptime: ' + timestr)
	await ctx.send(embed=embed)

@client.command(aliases=['users'])
async def servers(ctx):
	total = 0
	users = 0
	for i in client.guilds:
		total += len(i.members)
	for i in userDB.find():
		users += 1
	embed = discord.Embed(color=0x00ff00,description='This bot is in ' + bold(str(len(client.guilds))) + ' servers.\nTotal members: ' + bold(str(total)) + '\nTotal Users: ' + bold(str(users)))
	await ctx.send(embed=embed)

@client.command()
async def lines(ctx):
	files = ['main.py', 'static/style.css', 'templates/index.html', 'templates/base.html', 'templates/leaderboard.html', 'templates/notfound.html', 'templates/profile.html', 'templates/search.html', 'templates/stats.html', 'server.py']
	numLines = 0
	for x in files:
		with open(x) as txt:
			lines=txt.read().splitlines()
			numLines += len(lines)-lines.count("")
	embed = discord.Embed(color=0x00ff00, description='Total number of lines of code to make me: ' + str(numLines))
	await ctx.send(embed=embed)

@client.command(aliases=['leaders', 'ranks', 'ranking', 'lb', 'lbd'])
async def leaderboard(ctx, mssg=None):
	user = ctx.author.id
	if mssg == None:
		page = 1
	else:
		try:
			page = int(mssg)
		except ValueError:
			page = 1
	total = 0
	for i in userDB.find():
		total += 1
	numPages = math.ceil((total-1)/10)
	if page > numPages:
		page = numPages
	desc = showLeaderboard(page)
	sent = await ctx.send(
		embed=discord.Embed(
			title='leaderboard',
			description='Page: ' + str(page) + '/' + str(numPages) + desc,
			color=0x00ff00
		)
	)
	await sent.add_reaction('⬅️')
	await sent.add_reaction('➡️')
	msgs = generalDB.find_one({"name": "leadMessages"})['leadMessages']
	msgs[str(sent.id)] = {'user':user,'page':page}
	generalDB.update_one({"name": 'leadMessages'}, {"$set": {"leadMessages": msgs}})


@client.command(aliases=['profile','stats', 'height','size', 'cmpg', 'hpg'])
async def prof(ctx, *, user: discord.User=None):
	if user == None:
		name = str(ctx.author)
		user = ctx.author.id
	else:
		name = str(user)
		user = user.id
	if userExists(user):
		stats = userDB.find_one({"user_id": user})
		desc = 'Height: ' + bold(commas(str(stats['score']), False) + 'm') + '\nHeight per Growth: ' + bold(commas(str(stats['hpg']), False) + 'm') + '\nGrowth per Minute: ' + bold(commas(str(stats['hpm']), False)+ 'm') + '\nMultiplier: ' + bold(str(stats['multiplier']) + 'x') + '\nDaily Reward: ' + dailyCalc(time.time(), stats['dailyTime'])
		await send_embed(
			ctx,
			name + "'s profile",
			desc,
			True
		)
	else:
		await send_embed(
			ctx,
			None,
			'User has never played :(',
			False
		)





@client.command()
async def grow(ctx):
	userID = ctx.author.id
	if not userExists(userID):
		addUser(userID)

	userStats = userDB.find_one({"user_id": userID})
	timeNow = time.time()
	if timeNow - userStats['growTime'] >= generalDB.find_one({"name": "cooldown"})['cooldown']:
		await send_embed(
			ctx,
			'GROW!',
			'You grew ' + bold(commas(str(userStats['hpg']*userStats['multiplier'])) + 'm') + '\nYou are now ' + bold(commas(str(userStats['score'] + userStats['hpg'] * userStats['multiplier'])) + 'm') + '!',
			True
		)
		userStats['score'] += userStats['hpg'] * userStats['multiplier']
		userStats['growTime'] = timeNow
		userDB.update_one({"user_id": userID}, {"$set": userStats})
	else:
		await send_embed(
			ctx,
			'Too tired :(',
			'You are too tired from the last time you grew.\nYou will be ready again in ' + bold(str(math.ceil(generalDB.find_one({"name": "cooldown"})['cooldown'] - (timeNow - userStats['growTime']))) + ' second(s).'),
			False
		)





@client.command(aliases=['store'])
async def shop(ctx, mssg=None):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	if mssg == None:
		page = 1
	else:
		try:
			page = int(mssg)
		except ValueError:
			page = 1
	desc = getShopPage(user, page, 'shop')
	embed = discord.Embed(
		title='Shop (' + str(client.get_user(user)) + ')',
		description='Height: ' + bold(commas(str(userDB.find_one({"user_id": user})['score'])) + 'm') + '\nPage: ' + str(page)  + '/' + str(math.ceil(len(generalDB.find_one({"name": "shop"})['shop']) / 5)) + desc,
		color=0x00ff00
	)
	sent = await ctx.send(embed=embed)
	await sent.add_reaction('⬅️')
	await sent.add_reaction('➡️')
	msgs = generalDB.find_one({"name": "shopMessages"})['shopMessages']
	msgs[str(sent.id)] = {'user':user,'page':page}
	generalDB.update_one({"name": "shopMessages"}, {"$set": {'shopMessages': msgs}})





@client.command(aliases=['ishop', 'idle-shop', 'i-shop'])
async def idle_shop(ctx, mssg=None):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	if mssg == None:
		page = 1
	else:
		try:
			page = int(mssg)
		except ValueError:
			page = 1
	desc = getShopPage(user, page, 'idleShop')
	embed = discord.Embed(
		title='Shop (' + str(client.get_user(user)) + ')',
		description='Height: ' + bold(commas(str(userDB.find_one({"user_id": user})['score'])) + 'm') + '\nPage: ' + str(page) + '/' + str(math.ceil(len(generalDB.find_one({"name": "idleShop"})['idleShop']) / 5)) + desc,
		color=0x00ff00
	)
	sent = await ctx.send(embed=embed)
	await sent.add_reaction('⬅️')
	await sent.add_reaction('➡️')
	msgs = generalDB.find_one({"name": "idleShopMessages"})['idleShopMessages']
	msgs[str(sent.id)] = {'user':user,'page':page}
	generalDB.update_one({"name": "idleShopMessages"}, {"$set": {'idleShopMessages': msgs}})





@client.command(aliases=['ibuy', 'i-buy', 'idle-buy', 'purchase'])
async def buy(ctx, *, mssg=None):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	if mssg == None:
		await send_embed(
			ctx,
			None,
			"You didn't say anything, please say what you wanto to buy in the form: `=buy item` (replace `item` with the item that you want)",
			False
		)
	else:
		item = mssg.lower()
		try:
			num = int(item.split(' ')[-1])
			item = ' '.join(item.split(' ')[:-1])
			maxBuy = False
		except ValueError:
			if item.split(' ')[-1] == 'max':
				item = ' '.join(item.split(' ')[:-1])
				maxBuy = True
			else:
				num = 1
				maxBuy = False
		items = generalDB.find_one({"name": "shop"})['shop']
		real = False
		if item in items:
			shopType = 'shop'
			real = True
			increase = 'hpg'
			bought = 'bought'
		else:
			items = generalDB.find_one({"name": "idleShop"})['idleShop']
			if item in items:
				shopType = 'idleShop'
				real = True
				increase = 'hpm'
			bought = 'idleBought'
		if real:				
			if maxBuy:
				num = findMax(item, user, shopType)				
			if num > 0:
				stats = userDB.find_one({"user_id": user})
				score = stats['score']
				realPrice = fullPrice(item, user, num, shopType)
				if realPrice <= score:
					new = stats[increase] + items[item][increase] * num
					await send_embed(
						ctx,
						'Bought Successfully',
						"'" + item + "'[x" + str(num) + "] bought successfully!\nYour " + increase + ' is now: ' + bold(commas(str(new * stats['multiplier'])) + 'm') + " !\nYou are now " + bold(commas(str(stats['score']-realPrice)) + 'm') + ' tall.',
						True
					)
					stats['score'] -= realPrice
					stats[increase] = new
					index = 0
					for i in items:
						if i == item:
							break
						else:
							index += 1
					stats[bought][index] += num
					userDB.update_one({"user_id": user}, {"$set": stats})
				else:
					await ctx.send(
						embed=discord.Embed(
							description="You aren't tall enogh for that.\nYou need to grow another " + bold(commas(str(realPrice - stats['score'])) + 'm!'),
							color=0xff0000
						)
					)
			else:
				await send_embed(
					ctx,
					None,
					"Can't buy less that one of an item",
					False
				)
		else:
			await send_embed(
				ctx,
				None,
				"Item '" + item + "' not found.",
				False
				)


@client.command(aliases=['habitat'])
async def habitats(ctx):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	desc = showHabitats(user)
	await send_embed(
		ctx,
		'Habitats (' + str(ctx.author) + ')',
		'Height: ' + bold(commas(str(userDB.find_one({"user_id": user})['score'])) + 'm') + desc,
		True
	)

@client.command(aliases=['change-habitat'])
async def change_habitat(ctx, *, mssg=None):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	if mssg != None:
		habitat = mssg.lower()
		habitats = generalDB.find_one({"name": "habitats"})['habitats']
		if habitat in habitats:
			stats = userDB.find_one({"user_id": user})
			userMult = stats['multiplier']
			habMult = habitats[habitat]['multiplier']
			if habMult > userMult:
				score = stats['score']
				price = habitats[habitat]['price']
				if score >= price:
					await send_embed(
						ctx,
						None,
						"Congratulations on moving to " + bold(habitat) + "!\nYour multiplier is now " + bold(str(habitats[habitat]['multiplier']) + 'x') + '.',
						True
					)
					stats['multiplier'] = habitats[habitat]['multiplier']
					userDB.update_one({"user_id": user}, {"$set": stats})
				else:
					await send_embed(
						ctx,
						None,
						"You aren't tall enogh to move there.",
						False
					)
			elif habMult == userMult:
				await send_embed(
					ctx,
					None,
					'You are already here!',
					False
				)
			else:
				await send_embed(
					ctx,
					None,
					"You can't go back there!",
					False
				)
		else:
			await send_embed(
				ctx,
				None,
				"Could not find: '" + habitat + "'",
				False
			)
	else:
		await send_embed(
			ctx,
			None,
			"You didn't say where you wanted to move to!",
			False
		)
		

@client.command(aliases=['daily-reward','dailyreward', 'daily'])
async def daily_reward(ctx):
	user = ctx.author.id
	if not userExists(user):
		addUser(user)
	now = time.time()
	doc = userDB.find_one({"user_id": user})
	status = dailyCalc(now, doc['dailyTime'])
	if status == 'Ready!':
		stats = doc
		multiplier = stats['multiplier']
		reward = stats['hpg'] * multiplier * 50
		await send_embed(
			ctx,
			None,
			'Here is your daily reward:\n' + bold(commas(str(reward)) + 'm') + '!',
			True
			)
		stats['score'] += reward
		stats['dailyTime'] = now
		userDB.update_one({"user_id": user}, {"$set": stats})
	else:
		await send_embed(
			ctx,
			"Not ready yet!",
			status,
			False
		)


@client.command(aliases=['bug','bugs','suggestion','suggestions','report','bug_report','bug-report'])
async def feedback(ctx, *, mssg=None):
	user = ctx.author.id
	if mssg == None:
		await send_embed(
			ctx,
			None,
			"You didn't say anything",
			False
		)
	else:
		await send_embed(
			ctx,
			"Feedback sent!",
			"Thank you for your feedback!\nYou said:\n```\n" + mssg + "```",
			True
		)
		channel = client.get_channel(727865599467978849)
		location = '\nhttps://discordapp.com/channels/'+str(ctx.guild.id)+'/'+str(ctx.channel.id)+'/'+str(ctx.message.id)
		footer = 'Channel id: ' + str(ctx.channel.id) + '\nUser id: ' + str(user)
		await channel.send(
			embed=discord.Embed(
				description=str(ctx.author) + ' said:\n```\n' + mssg + '```\nhere: ' + location
			).set_footer(
				text=footer
			)
		)

@client.command()
async def hug(ctx):
    await ctx.send('You give your cactus a hug, :)')

@client.command()
async def settings(ctx):
	await ctx.send('This is a work in progress.')

@client.event
async def on_reaction_add(reaction, user):
	if user.id != 700051830394060801:
		if str(reaction) in ['⬅️','➡️']:
			shopType = ''
			shopTypes = ['shop','idleShop']
			messageID = str(reaction.message.id)
			for i in shopTypes:
				messages = generalDB.find_one({"name": i+"Messages"})[i+"Messages"]
				for x in messages:
					if x == messageID:
						shopType = i
						break
				if shopType != '':
					break
			if shopType != '':
				shop = generalDB.find_one({"name": shopType+"Messages"})[shopType+"Messages"]
				page = shop[messageID]['page']
				if str(reaction) == '⬅️':
					page-=1
				else:
					page += 1
				if page < 1: page = 1
				if page > math.ceil(len(shop) / 5): page = math.ceil(len(shop) / 5)
				user1 = user.id
				if user1 == shop[messageID]['user']:
					desc = getShopPage(user1, page, shopType)
					embed = discord.Embed(
						title='Shop (' + str(client.get_user(user1)) + ')',
						description='Height: ' + bold(commas(str(userDB.find_one({"user_id": user1})['score'])) + 'm') + '\nPage: ' + str(page) + '/' + str(math.ceil(len(shop) / 5)) + desc,
						color=0x00ff00
					)
					await reaction.message.delete()
					sent = await reaction.message.channel.send(embed=embed)
					await sent.add_reaction('⬅️')
					await sent.add_reaction('➡️')
					new = shop
					del new[messageID]
					new[str(sent.id)] = {'page':page,'user':user1}
					generalDB.update_one({"name": shopType+"Messages"}, {"$set": {shopType + 'Messages': new}})
			else:
				leaders = generalDB.find_one({"name": "leadMessages"})['leadMessages']
				if messageID in leaders:
					info = leaders[messageID]
					page = info['page']
					if str(reaction) == '⬅️':
						page -= 1
					else:
						page += 1
					total = 0
					for i in userDB.find():
						total += 1
					numPages = math.ceil((total-1)/10)
					if page < 1:
						page = 1
					elif page > numPages:
						page = numPages
					user1 = user.id
					if user1 == info['user']:
						desc = showLeaderboard(page)
						await reaction.message.delete()
						sent = await reaction.message.channel.send(
							embed=discord.Embed(
								title='leaderboard',
								description='Page: ' + str(page) + '/' + str(numPages) + desc,
								color=0x00ff00
							)
						)
						await sent.add_reaction('⬅️')
						await sent.add_reaction('➡️')
						new = leaders
						del new[messageID]
						new[str(sent.id)] = {'page':page,'user':user1}
						generalDB.update_one({"name": "leadMessages"}, {"$set": {'leadMessages': new}})


@client.command(aliases=['role'])
async def roles(ctx, *, role: discord.Role=None):
	if role == None:
		await ctx.send(
			embed=discord.Embed(
				description='You didn\'t sepcify a role',
				color=0xcc0000
			)
		)
	else:
		people = ''
		for i in ctx.guild.members:
			if role in i.roles:
				people += '- ' + str(i) + '\n'
		await ctx.send(
			embed=discord.Embed(
				title=str(role),
				description=people,
				color=0x00cc00
			)
		)

@client.event
async def on_message(message):
	if 'cactus' in message.clean_content.lower():
		await message.add_reaction('🌵')
	if str(message.author.id) not in BANNED:
		await client.process_commands(message)



#-------------------------------------------------------
#						Admin
#-------------------------------------------------------

@client.command()
@commands.is_owner()
async def cooldown(ctx, mssg):
	await send_embed(
		ctx,
		None,
		'Cooldown set to ' + mssg,
		True
	)
	generalDB.update_one({"name": "cooldown"}, {"$set": {'cooldown': int(mssg)}})

@client.command(aliases=['addidleitem'])
@commands.is_owner()
async def additem(ctx, *, mssg=None):
	if mssg == None:
		await send_embed(
			ctx,
			None,
			"You didn't say anything.",
			False
		)
	else:
		if 'idle' in ctx.message.content.split(' ')[0].lower():
			increase = 'hpm'
			shopType = 'idleShop'
			bought = 'idleBought'
		else:
			increase = 'hpg'
			shopType = 'shop'
			bought = 'bought'
		new = {'price':int(mssg.split('=')[1].split(',')[0]),increase:int(mssg.split('=')[1].split(',')[1])}
		shop = generalDB.find_one({"name": shopType})[shopType]
		shop[mssg.split('=')[0].lower()] = new
		generalDB.update_one({"name": shopType}, {"$set": {shopType: shop}})
		await send_embed(
			ctx,
			None,
			str({mssg.split('=')[0]:new}),
			True
		)
		for i in userDB.find():
			stats = i
			stats[bought].append(0)
			userDB.update_one({"user_id": i["user_id"]}, {"$set": stats})

@client.command()
@commands.is_owner()
async def addhabitat(ctx, *, mssg=None):
	if mssg == None:
		await send_embed(
			ctx,
			None,
			"You didn't say anything.",
			False
		)
	else:
		generalDB.find_one({"name": "habitats"})["habitats"][mssg.split("=")[0].lower()] = {"price":int(mssg.split("=")[1].split(",")[0]),"multiplier":int(mssg.split("=")[1].split(",")[1])}
		await send_embed(
			ctx,
			None,
			str({mssg.split('=')[0]:{"price":mssg.split("=")[1].split(",")[0],"multiplier":mssg.split("=")[1].split(",")[1]}}),
			True
		)


@client.command(aliases=['admin-set'])
@commands.is_owner()
async def admin_set(ctx):
	user = 691576874261807134
	stats = userDB.find_one({"user_id": user})
	stats['score'] = 1000000000
	stats['hpg'] = 1000000000
	stats['hpm'] = 1000000000
	for i in range(len(stats['bought'])):
		stats['bought'][i] = 0
	for x in range(len(stats['idleBought'])):
		stats['idleBought'][x] = 0
	stats['multiplier'] = 7
	userDB.update_one({"user_id": user}, {"$set": stats})
	await send_embed(
		ctx,
		'SET!',
		"Succesfully made you op!",
		True
	)

@client.command(aliases=['admin-reset'])
@commands.is_owner()
async def admin_reset(ctx):
	user = 691576874261807134
	stats = userDB.find_one({"user_id": user})
	stats['score'] = 0
	stats['hpg'] = 2
	stats['hpm'] = 0
	for i in range(len(stats['bought'])):
		stats['bought'][i] = 0
	for x in range(len(stats['idleBought'])):
		stats['idleBought'][x] = 0
	stats['multiplier'] = 1
	userDB.update_one({"user_id": user}, {"$set": stats})
	await send_embed(
		ctx,
		'RESET!',
		"Succesfully made you a noob!",
		True
	)

@client.command()
@commands.is_owner()
async def reply(ctx, *, mssg=None):
	if mssg != None:
		channel = int(mssg.split(' ')[0])
		mentionID = str(mssg.split(' ')[1]).replace('\n','')
		reply = ' '.join(mssg.split(' ')[2:])

		await client.get_channel(channel).send('<@' + mentionID + '\n> ' + reply)
		embed = discord.Embed(color=0x00ff00,description='Sent successfully\nYou said:```<@' + mentionID + '\n> ' + reply + '```')
		await ctx.send(embed=embed)

@client.command()
@commands.is_owner()
async def ban(ctx, mssg=None):
	if mssg != None:
		if mssg not in BANNED:
			BANNED.append(mssg)
			await send_embed(
				ctx,
				'BANNED',
				str(client.get_user(int(mssg))) + ' has been banned.',
				True
			)
			generalDB.update_one({"name": "banned"}, {"$set": {'banned': BANNED}})
		else:
			await send_embed(
				ctx,
				None,
				'User is already banned',
				False
			)

@client.command()
@commands.is_owner()
async def unban(ctx, mssg=None):
	if mssg != None:
		if mssg in BANNED:
			newLst = []
			for i in BANNED:
				if i != mssg:
					newLst.append(i)
			generalDB.update_one({"name": "banned"}, {"$set": {'banned': newLst}})
			await send_embed(
				ctx,
				'UNBANNED',
				str(client.get_user(int(mssg))) + ' is now allowed to use the bot.',
				True
			)
		else:
			await send_embed(
				ctx,
				None,
				"User already isn't banned.",
				False
			)

@client.command(aliases=['see-bans','banned','seebans'])
@commands.is_owner()
async def see_bans(ctx):
	desc = '```'
	for i in BANNED:
		desc += '\n' + str(client.get_user(int(i))) + ': ' + i
	await send_embed(
		ctx,
		'Banned users',
		desc + '```',
		True
	)


@client.command(aliases=['r'])
@commands.is_owner()
async def restart(ctx):
  embed=discord.Embed(color=0x00ff00,title=":white_check_mark:",description="Successfully Restarted")
  await ctx.send(embed=embed)
  os.system("clear")
  os.execv(sys.executable, ['python'] + sys.argv)


#server.s(client)
#client.run(os.getenv('TOKEN'))
