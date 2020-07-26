import discord, os, server, math, time, replitdb, asyncio, random, threading, sys, requests
from discord.ext import commands


client = discord.Client()

client = commands.Bot(command_prefix='=', help_command=None, case_insensitive=True)

db = replitdb.AsyncClient()

#-------------------------------------------------------
#							Status/On Ready
#-------------------------------------------------------

@client.event
async def on_ready():
	print('Good Morning')
	activity = discord.Activity(name='For =help', type=discord.ActivityType.watching)
	await client.change_presence(activity=activity)
	print('In ' + str(len(client.guilds)) + ' servers')
	for i in client.guilds:
		print(i)
	
	names = []
	for x in str(await db.view("score")).split("\n"):
		if x != '':
			names.append(x.split("=")[0] + "=" + str(client.get_user(int(x.split("=")[0]))))
	await db.add(names="\n".join(names))
	#print(await db.view('shop'))
	#print(await db.view('score'))
	#print(await db.view('growth'))
	set_interval(perSec, 60)
	global uptime
	uptime = time.time()

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
		embed.add_field(name='info', value='Info about the bot, also it\'s invite link.', inline=False)
		embed.add_field(name='prof', value='See your profile (stats).')
		embed.add_field(name='grow', value='Grow and try to become a big cactus!')
		embed.add_field(name='shop', value='Trade in some of your height for increases in height per growth.')
		embed.add_field(name='buy', value='Buy an item from the shop\nIn the form: `=buy item`.')
		embed.add_field(name='idle-shop', value='Trade in some of your height for increases in height per minute.')
		embed.add_field(name='idle-buy', value='Buy an item from the idle shop\nIn the form: `=idle-buy item`.')
		embed.add_field(name='habitats', value='Look at the habitats that you could move to (habitats increase multiplier).')
		embed.add_field(name='change-habitat', value='Move to a new habitat (increases multplier).')
		embed.add_field(name='daily-reward', value='Collect your daily reward.')
		embed.add_field(name='leaderboard', value='View leaderboard.')
		embed.add_field(name='feedback', value='Send feedback on how to improve this bot.\ne.g. new item for the shops.')
		embed.add_field(name='bug', value='Report a bug (please be specific).')
		embed.set_footer(text='Prefix is \'=\'')
		await ctx.send(embed=embed)
		
#-------------------------------------------------------
#						Functions
#-------------------------------------------------------
def commas(i):
	s,i="",str(i)
	for x in range(len(i)//3):s=","+i[-3:]+s;i=i[:-3]
	if i=="":s=s[1:]
	return(i+s)

def bold(i):
	return '**'+i+'**'

async def playerExist(user):
	lst = []
	exist = False
	
	f = str(await db.view('score')).split('\n')
	for x in f:
		lst.append(x.replace('\n',''))

	for i in range(len(lst)):
		if lst[i].split('=')[0] == user:
			exist = True
	return exist



async def addUser(user):
	await db.add(score=str(await db.view('score')) + '\n' + user + '=0')
	await db.add(growth=str(await db.view('growth')) + '\n' + user + '=2')
	await db.add(times=str(await db.view('times')) + '\n' + user + '=0')
	await db.add(daily=str(await db.view('daily')) + '\n' + user + '=0')
	await db.add(idle=str(await db.view('idle')) + '\n' + user + '=0')
	await db.add(names=str(await db.view('names')) + '\n' + user + '=' + str(client.get_user(int(user))))

	lst = str(await db.view('shop')).split('\n')
	new = '\n' + user + '='
	for x in lst:
		new += '1,'
	new = new[:-1]
	await db.add(bought=str(await db.view('bought')) + new)

	lst2 = str(await db.view('idleShop')).split('\n')
	new = '\n' + user + '='
	for x in lst2:
		new += '1,'
	new = new[:-1]
	await db.add(idleBought=str(await db.view('idleBought')) + new)

	lst3 = str(await db.view('habitats')).split('\n')
	new = '\n' + user + '=1,'
	for x in lst3:
		new += '0,'
	new = new[:-3]
	await db.add(habitatsBought=str(await db.view('habitatsBought')) + new)
		
		


async def getScore(user):
	lst = []
	lst2 = []
	f = str(await db.view('score')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	return lst[lst2.index(user)].split('=')[1]



async def getGrowth(user):
	lst = []
	lst2 = []
	f = str(await db.view('growth')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	return lst[lst2.index(user)].split('=')[1]



async def getTime(user):
	lst = []
	lst2 = []
	f = str(await db.view('times')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	return float(lst[lst2.index(user)].split('=')[1])



async def updateScore(user, score):
	lst = []
	lst2 = []
	f = str(await db.view('score')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(user)] = lst[lst2.index(user)].split('=')[0] + '=' + str(score)
	
	await db.add(score='\n'.join(lst))



async def updateHPG(user, hpg):
	lst = []
	lst2 = []
	f = str(await db.view('growth')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(user)] = lst[lst2.index(user)].split('=')[0] + '=' + str(hpg)
	await db.add(growth='\n'.join(lst))


async def getIdle(user):
	lst = []
	lst2 = []
	f = str(await db.view('idle')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	return lst[lst2.index(user)].split('=')[1]


async def updateIdle(user, score):
	lst = []
	lst2 = []
	f = str(await db.view('idle')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(user)] = lst[lst2.index(user)].split('=')[0] + '=' + str(score)
	
	await db.add(idle='\n'.join(lst))


async def updateBought(user, item):
	amountBought = []
	userIDs = []
	items = []
	f = str(await db.view('bought')).split('\n')
	for i in f:
		amountBought.append(i.replace('\n',''))
		userIDs.append(i.split('=')[0].replace('\n',''))
	f2 = str(await db.view('shop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])

	itemNum = items.index(item)

	newAmount = int(amountBought[userIDs.index(user)].split('=')[1].split(',')[items.index(item)]) + 1
	preAmount = amountBought[userIDs.index(user)].split('=')[1].split(',')[:items.index(item)]
	postAmount = amountBought[userIDs.index(user)].split('=')[1].split(',')[items.index(item)+1:]

	if itemNum == 0:
		strPreAmount = '='
		for q in preAmount:
			strPreAmount += q.replace('\n', '') + ','
		strPostAmount = ''
		for w in postAmount:
			strPostAmount += w.replace('\n', '') + ','
	else:
		strPreAmount = ''
		newAmount = ',' + str(newAmount)
		for q in preAmount:
			strPreAmount += q.replace('\n', '') + ','
		strPostAmount = ''
		for w in postAmount:
			strPostAmount += ',' + w.replace('\n', '')
		strPostAmount = strPostAmount[1:] + ','	
	
	strPreAmount = strPreAmount[:-1]
	strPostAmount = strPostAmount[:-1]
	comma = ','
	if itemNum == len(amountBought[userIDs.index(user)].split('=')[1].split(',')) - 1:
		comma = ''

	amountBought[userIDs.index(user)] =  amountBought[userIDs.index(user)].split('=')[0] + '=' + strPreAmount + str(newAmount) + comma + strPostAmount
	await db.add(bought='\n'.join(amountBought))


async def idleUpdateBought(user, item):
	amountBought = []
	userIDs = []
	items = []
	f = str(await db.view('idleBought')).split('\n')
	for i in f:
		amountBought.append(i.replace('\n',''))
		userIDs.append(i.split('=')[0].replace('\n',''))
	f2 = str(await db.view('idleShop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])

	itemNum = items.index(item)

	newAmount = int(amountBought[userIDs.index(user)].split('=')[1].split(',')[items.index(item)]) + 1
	preAmount = amountBought[userIDs.index(user)].split('=')[1].split(',')[:items.index(item)]
	postAmount = amountBought[userIDs.index(user)].split('=')[1].split(',')[items.index(item)+1:]

	if itemNum == 0:
		strPreAmount = '='
		for q in preAmount:
			strPreAmount += q.replace('\n', '') + ','
		strPostAmount = ''
		for w in postAmount:
			strPostAmount += w.replace('\n', '') + ','
	else:
		strPreAmount = ''
		newAmount = ',' + str(newAmount)
		for q in preAmount:
			strPreAmount += q.replace('\n', '') + ','
		strPostAmount = ''
		for w in postAmount:
			strPostAmount += ',' + w.replace('\n', '')
		strPostAmount = strPostAmount[1:] + ','	
	
	strPreAmount = strPreAmount[:-1]
	strPostAmount = strPostAmount[:-1]
	comma = ','
	if itemNum == len(amountBought[userIDs.index(user)].split('=')[1].split(',')) - 1:
		comma = ''

	amountBought[userIDs.index(user)] =  amountBought[userIDs.index(user)].split('=')[0] + '=' + strPreAmount + str(newAmount) + comma + strPostAmount
	await db.add(idleBought='\n'.join(amountBought))



async def updateTime(user):
	lst = []
	lst2 = []
	f = str(await db.view('times')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	
	lst[lst2.index(user)] = lst[lst2.index(user)].split('=')[0] + '=' + str(time.time())
	await db.add(times='\n'.join(lst))



def enoughMoney(score, price):
	if int(score) >= int(price):
		return True
	else:
		return False



async def realItem(item):
	real = False
	items = []
	f = str(await db.view('shop')).split('\n')
	for i in f:
		items.append(i.split('=')[0])
	if item in items:
		real = True	
	return real

async def idleRealItem(item):
	real = False
	items = []
	f = str(await db.view('idleShop')).split('\n')
	for i in f:
		items.append(i.split('=')[0])
	if item in items:
		real = True	
	return real


async def getPrice(item, user):
	items = []
	userIDs = []
	lst = []
	prices = {}
	f = str(await db.view('bought')).split('\n')
	for q in f:
		lst.append(q)
		userIDs.append(q.split('=')[0])
	f2 = str(await db.view('shop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])
		prices[i.split('=')[0]] = i.split('=')[1].split(',')[0]
	return round(int(prices[item]) * int(lst[userIDs.index(user)].split('=')[1].split(',')[items.index(item)]) * 1.5)

async def idleGetPrice(item, user):
	items = []
	userIDs = []
	lst = []
	prices = {}
	f = str(await db.view('idleBought')).split('\n')
	for q in f:
		lst.append(q)
		userIDs.append(q.split('=')[0])
	f2 = str(await db.view('idleShop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])
		prices[i.split('=')[0]] = i.split('=')[1].split(',')[0]
	return round(int(prices[item]) * int(lst[userIDs.index(user)].split('=')[1].split(',')[items.index(item)]) * 1.5)


async def getHPG(item):
	hpg = {}
	f = str(await db.view('shop')).split('\n')
	for i in f:
		hpg[i.split('=')[0]] = i.split('=')[1].split(',')[1]
	return int(hpg[item])

async def getIdleItem(item):
	hpg = {}
	f = str(await db.view('idleShop')).split('\n')
	for i in f:
		hpg[i.split('=')[0]] = i.split('=')[1].split(',')[1]
	return int(hpg[item])



async def idlePageItems(num, user):
	items = []
	amountBought = []
	userIDs = []
	prices = {}
	hpg = {}
	pages ={}
	f = str(await db.view('idleBought')).split('\n')
	for i in f:
		amountBought.append(i.replace('\n',''))
		userIDs.append(i.replace('\n','').split('=')[0])
	f2 = str(await db.view('idleShop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])
		prices[i.split('=')[0]] = i.split('=')[1].split(',')[0]
		hpg[i.split('=')[0]] = i.split('=')[1].split(',')[1]

	
	pageContent = []
	for x in range(math.ceil(len(items)/4)):
		for q in range(4):
			if x*4+q < len(items):
				item = items[x*4+q]
				pageContent.append('\n' + item.title() + ':\nCost: ' + commas(str(round(int(prices[item]) * int(amountBought[userIDs.index(user)].split('=')[1].split(',')[x*4+q]) * 1.5))) + ' cm\nIncrease in cm per minute: ' + commas(hpg[item]) + '\n')
		pages['page'+str(x+1)] = pageContent
		pageContent = []

	try:
		return pages['page'+num]
	except KeyError:
		return ['Page \'' + num + '\' not found']



async def pageItems(num, user):
	items = []
	amountBought = []
	userIDs = []
	prices = {}
	hpg = {}
	pages ={}
	f = str(await db.view('bought')).split('\n')
	for i in f:
		amountBought.append(i.replace('\n',''))
		userIDs.append(i.replace('\n','').split('=')[0])
	f2 = str(await db.view('shop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])
		prices[i.split('=')[0]] = i.split('=')[1].split(',')[0]
		hpg[i.split('=')[0]] = i.split('=')[1].split(',')[1]

	pageContent = []
	for x in range(math.ceil(len(items)/4)):
		for q in range(4):
			if x*4+q < len(items):
				item = items[x*4+q]
				pageContent.append('\n' + item.title() + ':\nCost: ' + commas(str(round(int(prices[item]) * int(amountBought[userIDs.index(user)].split('=')[1].split(',')[x*4+q]) * 1.5))) + ' cm\nIncrease in cm per growth: ' + commas(hpg[item]) + '\n')
		pages['page'+str(x+1)] = pageContent
		pageContent = []

	try:
		return pages['page'+num]
	except KeyError:
		return ['Page \'' + num + '\' not found']



async def amountBought(user, item):
	lst = []
	items = []
	f = str(await db.view('bought')).split('\n')
	for i in f:
		lst.append(i)
	f2 = str(await db.view('shop')).split('\n')
	for i in f2:
		items.append(i.split('=')[0])
	return int(lst.split('=')[1].split(',')[items.index(item)])



async def getNumPages():
	items = []
	f = str(await db.view('shop')).split('\n')
	for i in f:
		items.append(i.replace('\n','').split('=')[0])	
	return math.ceil(len(items)/4)

async def idleGetNumPages():
	items = []
	f = str(await db.view('idleShop')).split('\n')
	for i in f:
		items.append(i.replace('\n','').split('=')[0])	
	return math.ceil(len(items)/4)



async def removeMessageFromFile(msgID):
	lst = []
	lst2 =[]
	f = str(await db.view('messages')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(msgID)] = ''
	string = ''
	for x in range(len(lst)):
		if lst[x].replace('\n','') != '':
			string += '\n' + lst[x]
	await db.add(messages='\n'.join(lst))

async def idleRemoveMessageFromFile(msgID):
	lst = []
	lst2 =[]
	f = str(await db.view('idleMessages')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(msgID)] = ''
	string = ''
	for x in range(len(lst)):
		if lst[x].replace('\n','') != '':
			string += '\n' + lst[x]
	await db.add(idleMessages='\n'.join(lst))

async def leadRemoveMessageFromFile(msgID):
	lst = []
	lst2 =[]
	f = str(await db.view('leadMessages')).split('\n')
	for i in f:
		lst.append(i.replace('\n',''))
		lst2.append(i.replace('\n','').split('=')[0])
	lst[lst2.index(msgID)] = ''
	string = ''
	for x in range(len(lst)):
		if lst[x].replace('\n','') != '':
			string += '\n' + lst[x]
	await db.add(leadMessages='\n'.join(lst))

def realNum(num):
	try:
		if int(num) >= 0:
			return True
		else:
			return False
	except ValueError:
		return False



async def getDailyTime(user):
	lst = str(await db.view('daily')).split('\n')
	for i in lst:
		if i.split('=')[0] == user:
			return float(i.split('=')[1])



async def updateDailyTime(user):
	lst = str(await db.view('daily')).split('\n')
	for i in range(len(lst)):
		if lst[i].split('=')[0] == user:
			index = i
	lst[index] = lst[index].split('=')[0] + '=' + str(time.time())
	await db.add(daily='\n'.join(lst))


async def resetBought(user):
	lst = []
	boughtStuff = str(await db.view('bought')).split('\n')
	for i in boughtStuff:
		if i.split('=')[0] != user:
			lst.append(i)
	await db.add(bought='\n' + '\n'.join(lst))
	lst2 = str(await db.view('shop')).split('\n')
	new = '\n' + user + '='
	for x in lst2:
		new += '1,'
	new = new[:-1]
	await db.add(bought=str(await db.view('bought')) + new)

async def idleResetBought(user):
	lst = []
	boughtStuff = str(await db.view('idleBought')).split('\n')
	for i in boughtStuff:
		if i.split('=')[0] != user:
			lst.append(i)
	await db.add(idleBought='\n' + '\n'.join(lst))
	lst2 = str(await db.view('idleShop')).split('\n')
	new = '\n' + user + '='
	for x in lst2:
		new += '1,'
	new = new[:-1]
	await db.add(idleBought=str(await db.view('idleBought')) + new)

async def getHabitats():
	f = str(await db.view('habitats')).split('\n')
	lst = []
	for i in f:
		lst.append(i.split('=')[0])
	return lst

async def getHabitatsBought(user):
	f = str(await db.view('habitatsBought')).split('\n')
	for i in f:
		if i.split('=')[0] == user:
			return i.split('=')[1].split(',')

async def getHabitatPrice(item):
	f = str(await db.view('habitats')).split('\n')
	for i in f:
		if i.split('=')[0] == item:
			return i.split('=')[1].split(',')[0]

async def getHabitatMultiplier(item):	
	f = str(await db.view('habitats')).split('\n')
	for i in f:
		if i.split('=')[0] == item:
			return i.split('=')[1].split(',')[1]


async def updateHabitatBought(user, item):
	f = str(await db.view('habitatsBought')).split('\n')
	f2 = str(await db.view('habitats')).split('\n')
	f3 = []
	for x in f2:
		f3.append(x.split('=')[0])
	lst = []
	index = f3.index(item)
	for i in f:
		if i.split('=')[0] == user:
			lst.append(i.split('=')[0] + '=' + '2,' * len(i.split('=')[1].split(',')[:index]) + '1' + ',0' * len(i.split('=')[1].split(',')[index+1:]))
		else:
			lst.append(i)
	await db.add(habitatsBought='\n'.join(lst))

async def getMultplier(user):
	f = str(await db.view('habitatsBought')).split('\n')
	f2 = []
	f3 = []
	h = str(await db.view('habitats')).split('\n')
	h2 = []
	for x in f:
		if x != '':
			f2.append(x.split('=')[1])
			f3.append(x.split('=')[0])
	for i in h:
		h2.append(i.split('=')[1].split(',')[1])
	f4 = f2[f3.index(user)].split(',')
	return h2[f4.index('1')]


async def resetHabitat(user):
	f = str(await db.view('habitatsBought')).split('\n')
	f2 = str(await db.view('habitats')).split('\n')
	lst = []
	extra = ''
	for x in range(len(f2)-1):
		extra += ',0'
	for i in f:
		if i.split('=')[0] == user:
			lst.append(i.split('=')[0] + '=1' + extra)
		else:
			lst.append(i)
	await db.add(habitatsBought='\n' + '\n'.join(lst))


async def getLeadersLen():
	total = 0
	f = str(await db.view('score')).split('\n')
	for i in f:
		if i != '':
			total += 1
	return math.ceil(total/10)


async def shopPage(page, userID):
	items = await pageItems(page, userID)
	description = 'Your Height: ' + await getScore(userID) + ' cm\n'
	description += 'Page ' + page + '/' + str(await getNumPages()) + '\n```'
	
	for i in items:
		description += i
	description += '```'

	embed = discord.Embed(title='Shop (' + str(client.get_user(int(userID))) + ')', color=0x00ff00, description=description)
	embed.set_footer(text='You can do \'=shop [pageNum]\' to go straight to a certain page.')
	return embed


async def idleShopPage(page, userID):
	items = await idlePageItems(page, userID)
	description = 'Your Height: ' + bold(commas(await getScore(userID))) + ' cm\n'
	description += 'Page ' + page + '/' + str(await idleGetNumPages()) + '\n```'					
	for i in items:
		description += i
	description += '```'
	embed = discord.Embed(title='Idle Shop (' + str(client.get_user(int(userID))) + ')', color=0x00ff00, description=description)
	embed.set_footer(text='You can do \'=idle-shop [pageNum]\' to go straight to a certain page.')
	return embed


async def showLeaderboard(page):
	scores = []
	players = []
	orderedScores = []
	f = str(await db.view('score')).split('\n')
	for i in f:
		if i.replace('\n','') != '' and i.replace('\n','').split('=')[0] != '691576874261807134':
			scores.append(int(i.replace('\n','').split('=')[1]))
			orderedScores.append(int(i.replace('\n','').split('=')[1]))
			players.append(int(i.replace('\n','').split('=')[0]))
	orderedScores.sort(reverse=True)
	orderedPlayers = []
	for x in orderedScores:
		orderedPlayers.append(players[scores.index(x)])
		scores[scores.index(x)] = ''
	description = 'Page ' + str(page) + '/' + str(await getLeadersLen()) + '```'
	loops = 10 * page
	start = (page-1)*10
	if start <= len(orderedPlayers):
		if len(scores) < loops:
			loops = len(scores)
		for a in range(start, loops):
			description += str(a+1) + '. ' + str(client.get_user(orderedPlayers[a])) + ': ' + commas(str(orderedScores[a])) + 'cm\n'
	else:
		description += 'No more users :('
	return discord.Embed(color=0x00ff00,title='Leaderboard', description=description+'```')
	

async def changePage(fName, reaction, user):
	messages = []
	pages = []
	users = []
	page = 0
	doStuff = False
	f = str(await db.view(fName)).split('\n')	
	for i in f:
		if i.replace('\n','') != '':
			messages.append(i.replace('\n','').split('=')[0])
			pages.append(i.replace('\n','').split('=')[1].split(',')[0])
			users.append(i.replace('\n','').split('=')[1].split(',')[1])
		msgID = str(reaction.message.id)
	if msgID in messages:
		index = messages.index(msgID)
		if fName == 'messages':
			numPages = await getNumPages()
		elif fName == 'idleMessages':
			numPages = await idleGetNumPages()
		elif fName == 'leadMessages':
			numPages = await getLeadersLen()
		if str(user.id) == users[index]:
			if str(reaction) in ['⬅️','➡️']:
				doStuff = False
				if str(reaction) == '⬅️' and int(pages[index]) > 1:
					page = str(int(pages[index]) - 1)
					doStuff = True
				
				elif str(reaction) == '➡️' and int(pages[index]) < numPages:
					page = str(int(pages[index]) + 1)
					doStuff = True
	return [doStuff, page, msgID]


async def db_ban(user):
	lst = str(await db.view('banned')).split('\n')
	lst.append(user)
	await db.add(banned='\n'.join(lst))

async def get_banned():
	return str(await db.view('banned')).split('\n')

async def db_unban(user):
	lst = str(await db.view('banned')).split('\n')
	lst2 = []
	for i in lst:
		if i != user:
			lst2.append(i)
	await db.add(banned='\n'.join(lst2))

async def perSec():
	stuff = str(await db.view('idle')).split('\n')
	change = []
	userIds = []
	for i in stuff:
		if i != '' and i.split('=')[1] != '0':
			change.append(i.split('=')[1])
			userIds.append(i.split('=')[0])
	for i in userIds:
		multiplier = int(await getMultplier(i))
		await updateScore(i, int(await getScore(i)) + (int(change[userIds.index(i)]) * multiplier))

def set_interval(func, sec):
	def func_wrapper():
		set_interval(perSec, 60)
		asyncio.run(perSec())
	t = threading.Timer(sec, func_wrapper)
	t.start()
	return t


#-------------------------------------------------------
#						Commands
#-------------------------------------------------------
@client.command(aliases=['info','uptime','source','source-code','prefix'])
async def invite(ctx):
	now = time.time()
	diff = now - uptime
	hrs = str(round(diff // 3600))
	mins = str(round((diff - int(hrs) * 3600) // 60))
	secs = str(round(diff - int(hrs) *3600 - int(mins) * 60))
	timestr = bold(hrs + 'hrs ' + mins + 'mins ' + secs + 'secs')
	embed = discord.Embed(color=0x00ff00,title='Info',description='Prefix: `=`\nSource Code: https://repl.it/@CodingCactus/Cactus-Bot-2\nInvite Link: https://discordapp.com/oauth2/authorize?client_id=700051830394060801&scope=bot&permissions=0\nUptime: ' + timestr)
	await ctx.send(embed=embed)

@client.command()
async def servers(ctx):
	total = 0
	for i in client.guilds:
		total += len(i.members)
	embed = discord.Embed(color=0x00ff00,description='This bot is in ' + bold(str(len(client.guilds))) + ' servers.\nTotal members: ' + bold(str(total)))
	await ctx.send(embed=embed)


@client.command()
async def lines(ctx):
	files = ['main.py', 'static/style.css', 'templates/index.html', 'templates/base.html', 'templates/leaderboard.html', 'server.py']
	numLines = 0
	for x in files:
		with open(x) as txt:
			lines=txt.read().splitlines()
		numLines += len(lines)-lines.count("")
	
	embed = discord.Embed(color=0x00ff00, description='Total number of lines of code to make me: ' + str(numLines))
	await ctx.send(embed=embed)



@client.command(aliases=['profile','stats', 'height','size', 'cmpg', 'hpg'])
async def prof(ctx, *, member: discord.Member=None):
	if member == None:
		user = str(ctx.message.author.id)
	else:
		user = str(member.id)
	exist = await playerExist(user)
	if exist:
		growth = await getGrowth(user)
		score = await getScore(user)
		idle = await getIdle(user)
		dailyTime = await getDailyTime(user)
		multiplier = await getMultplier(user)
		timeNow = time.time()
		difference = timeNow - dailyTime
		difference2 = 3600*22 - difference
		if difference >= 3600 * 22:
			msg = 'Ready!'
		else:
			hrs = str(round(difference2 // 3600))
			mins = str(round((difference2 - int(hrs) * 3600) // 60))
			secs = str(round(difference2 - int(hrs) *3600 - int(mins) * 60))
			msg='Ready in: ' + bold(hrs) + 'hrs ' + bold(mins) + 'mins ' + bold(secs) + 'secs'


		embed = discord.Embed(color=0x00ff00,title=str(client.get_user(int(user))) + '\'s Profile', description='Height (cm): ' + bold(commas(score)) + '\ncm per growth: ' + bold(commas(growth)) + '\ncm per minute: ' + bold(commas(idle)) + '\nMultiplier: ' + bold(multiplier + 'x') + '\n\nDaily Reward Status:\n' + msg)
		await ctx.send(embed=embed)
	else:
		embed = discord.Embed(color=0xff0000, description='You haven\'t played yet!')
		await ctx.send(embed=embed)


@client.command()
async def grow(ctx):
	user = str(ctx.author.id)
	cooldown= int(await db.view('cooldown'))
	allow = False
	timeNow = time.time()
	if not await playerExist(user):
		await addUser(user)
		allow = True	
	userTime = await getTime(user)
	if round(timeNow - userTime) >= cooldown:
		allow = True

	if allow:
	
		growth = int(await getGrowth(user))
		score = int(await getScore(user))
		multiplier = int(await getMultplier(user))
		newScore = score + (growth * multiplier)

		embed = discord.Embed(color=0x00ff00, description='You grew ' + bold(commas(str(growth * multiplier))) + ' cm!\nYou are now ' + bold(commas(str(newScore))) + ' cm tall!')
		await ctx.send(embed=embed)		
		await updateScore(user, newScore)
		await updateTime(user)
	else:
		if cooldown - round(timeNow - userTime) == 1:
			s = ''
		else:
			s = 's'
		embed = discord.Embed(color=0xff0000, description='You are still tired from the last time that you grew.\nPlease wait **' + str(cooldown - round(timeNow - userTime)) + '** second' + s + '.')
		await ctx.send(embed=embed)

@client.command()
async def shop(ctx, mssg=None):
	user = str(ctx.message.author.id)
	if not await playerExist(user):
		await addUser(user)

	if mssg == None:
		page = '1'
	else:
		page = mssg

	items = await pageItems(page, user)
	description = 'Your Height: ' + bold(commas(await getScore(user))) + ' cm\n'
	description += 'Page ' + page + '/' + str(await getNumPages()) + '\n```'
	
	for i in items:
		description += i
	description += '```'

	embed = discord.Embed(title='Shop (' + str(client.get_user(int(user))) + ')', color=0x00ff00, description=description)
	embed.set_footer(text='You can do \'=shop [pageNum]\' to go straight to a certain page.')
	msg = await ctx.send(embed=embed)

	await msg.add_reaction('⬅️')
	await msg.add_reaction('➡️')

	await db.add(messages=str(await db.view('messages')) + '\n' + str(msg.id) + '=' + page + ',' + user)

	lst = str(await db.view('messages')).split('\n')
	lst2 = []
	if len(lst) >= 75:
		for l in lst:
			if l != '':
				lst2.append(l)
		await db.add(messages='\n' + '\n'.join(lst2[32:]))



@client.command(aliases=['ishop','i-shop','idle-shop'])
async def idle_shop(ctx, mssg=None):
	user = str(ctx.message.author.id)
	if not await playerExist(user):
		await addUser(user)

	if mssg == None:
		page = '1'
	else:
		page = mssg

	items = await idlePageItems(page, user)
	description = 'Your Height: ' + bold(commas(await getScore(user))) + ' cm\n'
	description += 'Page ' + page + '/' + str(await idleGetNumPages()) + '\n```'
	
	for i in items:
		description += i
	description += '```'

	embed = discord.Embed(title='Shop (' + str(client.get_user(int(user))) + ')', color=0x00ff00, description=description)
	embed.set_footer(text='You can do \'=shop [pageNum]\' to go straight to a certain page.')
	msg = await ctx.send(embed=embed)

	await msg.add_reaction('⬅️')
	await msg.add_reaction('➡️')

	await db.add(idleMessages=str(await db.view('idleMessages')) + '\n' + str(msg.id) + '=' + page + ',' + user)

	lst = str(await db.view('idleMessages')).split('\n')
	lst2 = []
	if len(lst) >= 75:
		for l in lst:
			if l != '':
				lst2.append(l)
		await db.add(idleMessages='\n' + '\n'.join(lst2[32:]))


@client.command()
async def buy(ctx,*, mssg=None):
	user = str(ctx.message.author.id)
	if not await playerExist(user):
		await addUser(user)

	if mssg == None:
		embed = discord.Embed(color=0xff0000, description='Please enter in the form `=buy item`')
		await ctx.send(embed=embed)
	else:
		item = mssg.lower()
		

		if await realItem(item):
			score = await getScore(user)
			hpg = await getGrowth(user)
			price = await getPrice(item, user)

			if enoughMoney(int(score), price):
				multiplier = int(await getMultplier(user))
				await updateHPG(user, int(hpg)+await getHPG(item))

				embed = discord.Embed(color=0x00ff00, title='Bought successfully!', description='You now grow ' + bold(commas(str(int(await getGrowth(user)) * multiplier))) + ' cm per growth!')
				await ctx.send(embed=embed)

				await updateBought(user, item)
				await updateScore(user, int(score)-price)
			else:
				embed = discord.Embed(color=0xff0000, description='You need to be ' + bold(commas(str(price - int(score)))) + ' cm taller to buy that!')
				await ctx.send(embed=embed)
			
		else:
			embed = discord.Embed(color=0xff0000, description='Unkown item: \''+item+'\'')
			await ctx.send(embed=embed)


@client.command(aliases=['ibuy', 'idle-buy'])
async def idle_buy(ctx,*, mssg=None):
	user = str(ctx.message.author.id)
	if not await playerExist(user):
		await addUser(user)

	if mssg == None:
		embed = discord.Embed(color=0xff0000, description='Please enter in the form `=idle-buy item`')
		await ctx.send(embed=embed)
	else:
		item = mssg.lower()
		

		if await idleRealItem(item):
			score = await getScore(user)
			idle = await getIdle(user)
			price = await idleGetPrice(item, user)

			if enoughMoney(int(score), price):
				multiplier = int(await getMultplier(user))				
				await updateIdle(user, int(idle) + await getIdleItem(item))

				embed = discord.Embed(color=0x00ff00, title='Bought successfully!', description='You now grow ' + bold(commas(str(int(await getIdle(user)) * multiplier))) + ' cm per minute!')
				await ctx.send(embed=embed)
				await idleUpdateBought(user, item)
				await updateScore(user, int(score)-price)
			else:
				embed = discord.Embed(color=0xff0000, description='You need to be ' + bold(commas(str(price - int(score)))) + ' cm taller to buy that!')
				await ctx.send(embed=embed)
			
		else:
			embed = discord.Embed(color=0xff0000, description='Unkown item: \''+item+'\'')
			await ctx.send(embed=embed)


@client.event
async def on_reaction_add(reaction, user):
	lst = await changePage('messages', reaction, user)
	doStuff = lst[0]
	page = lst[1]
	msgID = lst[2]
	if doStuff:
		embed = await shopPage(page, str(user.id))					
		msg = await reaction.message.channel.send(embed=embed)
		await removeMessageFromFile(msgID)
		await reaction.message.delete()
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		await db.add(messages=str(await db.view('messages')) + '\n' + str(msg.id) + '=' + page + ',' + str(user.id))

	lst = await changePage('idleMessages', reaction, user)
	doStuff = lst[0]
	page = lst[1]
	msgID = lst[2]
	if doStuff:
		embed = await idleShopPage(page, str(user.id))
		msg = await reaction.message.channel.send(embed=embed)
		await idleRemoveMessageFromFile(msgID)
		await reaction.message.delete()
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		await db.add(idleMessages=str(await db.view('idleMessages')) + '\n' + str(msg.id) + '=' + page + ',' + str(user.id))

	lst = await changePage('leadMessages', reaction, user)
	doStuff = lst[0]
	page = int(lst[1])
	msgID = lst[2]
	if doStuff:
		embed = await showLeaderboard(page)
		msg = await reaction.message.channel.send(embed=embed)
		await leadRemoveMessageFromFile(msgID)
		await reaction.message.delete()
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		await db.add(leadMessages=str(await db.view('leadMessages')) + '\n' + str(msg.id) + '=' + str(page) + ',' + str(user.id))


@client.command(aliases=['habitat'])
async def habitats(ctx):
	user = str(ctx.author.id)
	if not await playerExist(user):
		addUser(user)

	f = str(await db.view('habitats')).split('\n')
	f2 = str(await db.view('habitatsBought')).split('\n')
	places = []
	prices = []
	multipliers =[]
	for x in f2:
		if x.split('=')[0] == user:
			bought = x.split('=')[1].split(',')
	for i in range(len(f)):
		if bought[i] == '1':
				prices.append('Current Location')
		elif bought[i] == '2':			
				prices.append('Cannot go back here')
		else:
			prices.append(commas(f[i].split('=')[1].split(',')[0]) + ' cm')
		places.append(f[i].split('=')[0])
		multipliers.append(f[i].split('=')[1].split(',')[1])
	message = '```'
	for x in range(len(places)):
		message += '\n' + places[x].title().replace("'S","'s") + ':\nPrice: ' + prices[x] + '\nMultiplier: ' + multipliers[x] + '\n'
	message += '```'
	embed = discord.Embed(color=0x00ff00,title=str(client.get_user(int(user))),description='Your height: ' + bold(commas(await getScore(user))) + ' cm\n' + message)
	await ctx.send(embed=embed)


@client.command(aliases=['change-habitat'])
async def change_habitat(ctx, mssg=None):
	user = str(ctx.author.id)
	if mssg != None:
		if not await playerExist(user):
			await addUser(user)

		choice = ctx.message.content.lower().replace('=change-habitat ','')
		habitats = await getHabitats()
		if choice in habitats:
			bought = await getHabitatsBought(user)
			if bought[habitats.index(choice)] != '1':
				if bought[habitats.index(choice)] != '2':
					score = await getScore(user)
					price = await getHabitatPrice(choice)
					if enoughMoney(score, price):
						multiplier = await getHabitatMultiplier(choice)
						embed = discord.Embed(color=0x00ff00,description='Congratulations! You now live in a ' + choice.title() + '!\nYour multiplier is now ' + bold(multiplier))
						await ctx.send(embed=embed)
						await updateScore(user, str(int(score) - int(price)))
						await updateHabitatBought(user, choice)
					else:
						embed = discord.Embed(color=0xff0000,description='You aren\'t tall enough for that!')
						await ctx.send(embed=embed)
				else:
					embed = discord.Embed(color=0xff0000,description='You have already lived there, you can\'t go back!')
					await ctx.send(embed=embed)
			else:
				embed = discord.Embed(color=0xff0000,description='You are already there!')
				await ctx.send(embed=embed)
					
		else:
			embed = discord.Embed(color=0xff0000,description='Unkown habitat \'' + choice +'\'')
			await ctx.send(embed=embed)

	else:
		embed = discord.Embed(color=0xff0000,description='You didn\'t enter anything.')
		await ctx.send(embed=embed)


					
@client.command(aliases=['leaders', 'ranks', 'ranking'])
async def leaderboard(ctx, mssg=None):
	user = str(ctx.author.id)
	if mssg == None:
		page = 1
	else:
		try:
			page = int(mssg)
		except ValueError:
			page = 1
	embed = await showLeaderboard(page)
	msg = await ctx.send(embed=embed)

	await msg.add_reaction('⬅️')
	await msg.add_reaction('➡️')

	await db.add(leadMessages=str(await db.view('leadMessages')) + '\n' + str(msg.id) + '=' + str(page) + ',' + user)


@client.command(aliases=['daily-reward','daily_reward', 'daily'])
async def dailyreward(ctx):
	user = str(ctx.message.author.id)
	if not await playerExist(user):
		await addUser(user)

	dailyTime = await getDailyTime(user)
	timeNow = time.time()
	difference = timeNow - dailyTime
	difference2 = 3600*22 - difference
	if difference >= 3600 * 22:
		multiplier = int(await getMultplier(user))
		reward = int(await getGrowth(user)) * multiplier * 50
		embed = discord.Embed(color=0x00ff00,description='Here is your daily reward:\n' + str(reward) + ' cm!')
		await ctx.send(embed=embed)
		await updateScore(user, str(int(await getScore(user)) + reward))
		await updateDailyTime(user)
	else:
		hrs = str(round(difference2 // 3600))
		mins = str(round((difference2 - int(hrs) * 3600) // 60))
		secs = str(round(difference2 - int(hrs) *3600 - int(mins) * 60))
		embed = discord.Embed(color=0xff0000,description='Your daily gift isn\'t ready yet!\nIt will be ready in ' + hrs + 'hrs ' + mins + 'mins ' + secs + 'secs')
		await ctx.send(embed=embed)



@client.command(aliases=['bugs','report','bug_report','bug-report'])
async def bug(ctx, *, mssg=None):
	user2 = str(ctx.author)
	if mssg==None:
		embed = discord.Embed(color=0xff0000,description='You didn\'t say anything')
		await ctx.send(embed=embed)
	else:
		if len(mssg) < 1900:
			channel = client.get_channel(727123726990049291)
			location = '\nhttps://discordapp.com/channels/'+str(ctx.guild.id)+'/'+str(ctx.channel.id)+'/'+str(ctx.message.id)
			footer = 'Channel id: ' + str(ctx.channel.id) + '\nUser id: ' + str(ctx.author.id)
			embed = discord.Embed(color=0x00ff00,description=user2 + ' said:\n```' + mssg + '```\nHere:' + location)
			embed.set_footer(text=footer)
			await channel.send(embed=embed)
			embed2 = discord.Embed(color=0x00ff00,description='Sent successfully\nThanks for reporting!')
			await ctx.send(embed=embed2)
		else:
			embed = discord.Embed(color=0xff0000,description='Sorry, but your message needs to be less that 1900 characters')
			await ctx.send(embed=embed)


@client.command(aliases=['suggestion','suggestions'])
async def feedback(ctx, *, mssg=None):
	user2 = str(ctx.author)
	if mssg==None:
		embed = discord.Embed(color=0xff0000,description='You didn\'t say anything')
		await ctx.send(embed=embed)
	else:
		if len(mssg) < 1900:
			channel = client.get_channel(727865599467978849)
			location = '\nhttps://discordapp.com/channels/'+str(ctx.guild.id)+'/'+str(ctx.channel.id)+'/'+str(ctx.message.id)
			footer = 'Channel id: ' + str(ctx.channel.id) + '\nUser id: ' + str(ctx.author.id)
			embed = discord.Embed(color=0x00ff00,description=user2 + ' said:\n```' + mssg + '```\nHere:' + location)
			embed.set_footer(text=footer)
			await channel.send(embed=embed)
			embed2 = discord.Embed(color=0x00ff00,description='Sent successfully\nThanks for your feedback!')
			await ctx.send(embed=embed2)
		else:
			embed = discord.Embed(color=0xff0000,description='Sorry, but your message needs to be less that 1900 characters')
			await ctx.send(embed=embed)


@client.event
async def on_message(message):
	if 'cactus' in message.clean_content.lower():
		await message.add_reaction('🌵')
	if str(message.author.id) not in await get_banned():
		await client.process_commands(message)


@client.command()
async def hug(ctx):
	await ctx.send(random.choice(['https://tenor.com/view/red-panda-tackle-surprised-hug-cute-gif-12661024','https://tenor.com/view/cat-love-huge-hug-big-gif-11990658']))

@client.command()
async def cactus(ctx):
	r=requests.get("https://gallery.codingcactus.codes/api/random").json()
	cactus_name=r["name"]
	cactus_url=r["url"]

	embed=discord.Embed(color=0x00ff00, title=cactus_name)
	embed.set_image(url=cactus_url)

	await ctx.send(embed=embed)



#-------------------------------------------------------
#						Admin Commands
#-------------------------------------------------------

@client.command()
async def cooldown(ctx, mssg=None):
	if ctx.message.author.id == 691576874261807134:
		if mssg ==None:
			embed = discord.Embed(color=0xff0000, description='No time entered.')
			await ctx.send(embed=embed)
		else:
			cooldownNum = ctx.message.content.replace('=cooldown ','')
			if realNum(cooldownNum):
				await db.add(cooldown=cooldownNum)
				embed = discord.Embed(color=0x00ff00, description='Cooldown set to ' + bold(cooldownNum))
				await ctx.send(embed=embed)
			else:
				embed = discord.Embed(color=0xff0000, description='Invalid number entered.')
				await ctx.send(embed=embed)
	else:
		embed = discord.Embed(color=0xff0000, description='You are not my creator!\nOnly he can use this command!')
		await ctx.send(embed=embed)



@client.command()
async def additem(ctx, mssg=None):
	if ctx.message.author.id == 691576874261807134:
		if mssg == None:
			embed = discord.Embed(color=0xff0000,description='You didn\'t write anything')
			await ctx.send(embed=embed)
		else:
			await db.add(shop=str(await db.view('shop')) + '\n' + ctx.message.content.lower().replace('=additem ',''))
			lst = []
			boughtStuff = str(await db.view('bought')).split('\n')
			for i in boughtStuff:
				if i.replace('\n','') != '':
					add = ',1'
				else:
					add = ''
				lst.append(i + add)
			await db.add(bought='\n'.join(lst))
	else:
		embed = discord.Embed(color=0xff0000,description='You are not my creator!\nOnly they can use this command!')
		await ctx.send(embed=embed)

@client.command()
async def addidleitem(ctx, mssg=None):
	if ctx.message.author.id == 691576874261807134:
		if mssg == None:
			embed = discord.Embed(color=0xff0000,description='You didn\'t write anything')
			await ctx.send(embed=embed)
		else:
			await db.add(idleShop=str(await db.view('idleShop')) + '\n' + ctx.message.content.lower().replace('=addidleitem ',''))
			lst = []
			boughtStuff = str(await db.view('idleBought')).split('\n')
			for i in boughtStuff:
				if i.replace('\n','') != '':
					add = ',1'
				else:
					add = ''
				lst.append(i + add)
			await db.add(idleBought='\n'.join(lst))
	else:
		embed = discord.Embed(color=0xff0000,description='You are not my creator!\nOnly they can use this command!')
		await ctx.send(embed=embed)

@client.command(aliases=['admin-set'])
async def admin_set(ctx):
	user = str(ctx.message.author.id)
	if user == '691576874261807134':
		await updateScore(user,'100000000000')
		await updateHPG(user,'100000000000')
		embed = discord.Embed(color=0x00ff00,description='Successfully set your stats master.')
		await ctx.send(embed=embed)

	else:
		embed = discord.Embed(color=0xff0000,description='You aren\'t my creator!\nOnly he can do that!')
		await ctx.send(embed=embed)



@client.command(aliases=['admin-reset'])
async def admin_all(ctx):
	user = str(ctx.message.author.id)
	if user == '691576874261807134':
		await updateScore(user,'0')
		await updateHPG(user,'2')
		await resetBought(user)
		await resetHabitat(user)
		await updateIdle(user, '0')
		await idleResetBought(user)
		embed = discord.Embed(color=0x00ff00,description='Successfully reset your stats master.')
		await ctx.send(embed=embed)
	else:
		embed = discord.Embed(color=0xff0000,description='You aren\'t my creator!\nOnly he can do that!')
		await ctx.send(embed=embed)

@client.command(aliases=['bug-reply'])
async def reply(ctx, *, mssg):
	user = str(ctx.author.id)
	if user == '691576874261807134':
		channel = int(mssg.split(' ')[0])
		mentionID = str(mssg.split(' ')[1]).replace('\n','')
		reply = ' '.join(mssg.split(' ')[2:])

		await client.get_channel(channel).send('<@' + mentionID + '\n> ' + reply)

		embed = discord.Embed(color=0x00ff00,description='Sent successfully\nYou said:```<@' + mentionID + '\n> ' + reply + '```')
		await ctx.send(embed=embed)

@client.command()
async def ban(ctx, mssg=None):
	user = str(ctx.author.id)
	if user == '691576874261807134':
		if mssg == None:
			embed = discord.Embed(color=0xff0000, description='You didn\'t say anyone!')
			await ctx.send(embed=embed)
		elif mssg not in await get_banned():
			embed = discord.Embed(color=0x00ff00, description=mssg + ' (' + str(client.get_user(int(mssg))) + ') is now BANNED!')
			await ctx.send(embed=embed)
			await db_ban(mssg)
		else:
			embed = discord.Embed(color=0xf00f00, description=mssg + ' (' + str(client.get_user(int(mssg))) + ') is ALREADY banned!')
			await ctx.send(embed=embed)

@client.command(aliases=['see-bans'])
async def see_bans(ctx):
	user = str(ctx.author.id)
	if user == '691576874261807134':
		lst = await get_banned()
		string = ''
		for i in lst:
			string += '\n' + i + str(client.get_user(int(i)))
		embed = discord.Embed(color=0x00ff00, description='```' + string + '```')
		await ctx.send(embed=embed)

@client.command()
async def unban(ctx, mssg=None):
	user = str(ctx.author.id)
	if user == '691576874261807134':
		if mssg == None:
			embed = discord.Embed(color=0xff0000, description='You didn\'t say anyone!')
			await ctx.send(embed=embed)
		elif mssg in await get_banned():
			embed = discord.Embed(color=0x00ff00, description=mssg + ' (' + str(client.get_user(int(mssg))) + ') is now NOT banned!')
			await ctx.send(embed=embed)
			await db_unban(mssg)
		else:
			embed = discord.Embed(color=0xf00f00, description=mssg + ' (' + str(client.get_user(int(mssg))) + ') was NOT banned!')
			await ctx.send(embed=embed)


@client.command()
@commands.is_owner()
async def restart(ctx):
  embed=discord.Embed(color=0x00ff00,title=":white_check_mark:",description="Successfully Restarted")
  await ctx.send(embed=embed)
  os.system("clear")
  os.execv(sys.executable, ['python'] + sys.argv)

server.s()
client.run(os.getenv('TOKEN'))