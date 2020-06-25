import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import json
from random import randint
import random as r
from numpy import random
import matplotlib.pyplot as plt
import math
from time import gmtime, strftime

font = {'family': 'trebuchet ms',
        'weight': 'bold',
        'size': 14}
plt.rc('font', **font)
plt.rcParams["legend.fontsize"] = 11
plt.rcParams['axes.facecolor'] = '#36393F'
plt.rcParams["savefig.facecolor"] = '#36393F'
plt.rcParams['text.color'] = '#ffffff'
plt.rcParams['axes.labelcolor'] = '#ffffff'
plt.rcParams["figure.edgecolor"] = '#ACACAF'
plt.rc('axes', edgecolor='#ACACAF')
plt.rcParams["legend.facecolor"] = '#2c2f33'
plt.rcParams['xtick.color'] = '#ACACAF'
plt.rcParams['ytick.color'] = '#ACACAF'
plt.rcParams['legend.loc'] = 'upper left'
plt.rcParams['axes.labelsize'] = 16

with open('stockList.json') as f:
    stockList = json.load(f)

with open('users.json') as f:
    users = json.load(f)

with open('servers.json') as f:
    servers = json.load(f)

AdjAlpha = ['Adventurous', 'Beneficial', 'Careful', 'Decisive', 'Elaborate',
            'Fearless', 'Green', 'Healthy', 'Impressive', 'Jovial', 'Key',
            'Lean', 'Masterful', 'Nautical', 'Official', 'Pleasing', 'Quiet',
            'Radiant', 'Sharp', 'Tempting', 'Useful', 'Vacant', 'Warm', 'Yellow',
            'Zany']
NAlpha = ['Accounting', 'Bank', 'Corp.', 'Derivatives', 'Enterprises',
          'Finances', 'Gold', 'Households', 'Investments', 'Judiciaries', 'King',
          'Lemonade', 'Management', 'Nauticals', 'Offshoring', 'Politics',
          'Quality', 'Real Estate', 'Semiconductors', 'Technologies', 'Utilities',
          'Visions', 'Workers', 'Yeahs', 'Zoologists']


client = commands.Bot(command_prefix = "")

@client.event
async def on_ready():
    global stockList
    global users
    while True:
        while True:
            with open('stockList.json') as f:
                stockList = json.load(f)
            await asyncio.sleep(10)
            if len(stockList) < 6:
                await newStock()
            for stock in stockList:
                recentPrices = stockList[stock]['pastPrices']
                oldPrice = stockList[stock]['price']
                newPrice = await YSELoop(stock, oldPrice,
                                         stockList[stock]['randomX'],
                                         stockList[stock]['randomY'])
                if newPrice == -500:
                    break

                stockList[stock]['pastPrices'].append(oldPrice)
                stockList[stock]['price'] = newPrice

                try:
                    x = stockList[stock]['pastPrices'][50]
                    del stockList[stock]['pastPrices'][0]
                except:
                    pass

                if random.randint(1,1000) > 990:
                    print("crash")
                    print(stock)
                    stockList[stock]['randomX'] = -6
                    stockList[stock]['randomY'] = round(random.triangular(0.1,1,
                                                                          10),2)
                if random.randint(1,1000) > 950:
                    print(stock)
                    stockList[stock]['randomX'] = round(random.triangular(-5,1,
                                                                          5),2)
                    stockList[stock]['randomY'] = round(random.triangular(0.1,1,10),2)
                    print(stockList[stock]['randomX'])

                ### uses matplotlib to create plot

                plt.figure()
                plt.ylabel('Cost')
                plt.xlabel('Time')

                plt.title('Stock Market', fontsize=20)

                for stock in stockList:
                    plt.plot(stockList[stock]['pastPrices'], label = stock,
                             linewidth = 2.5, alpha=0.80)
                plt.legend(framealpha=0.5)
                plt.tight_layout()

                plt.savefig('recentchart.png', transparent=True, dpi = 200)

                plt.close('all')

                if len(stockList) < 6:
                    await newStock()

            for server in servers:
                try:
                    await displayStocks(servers[server]['channel'])
                except:
                    pass

@client.event
async def on_member_join(member):
    global users

    await update_data(users,member)

@client.event
async def on_guild_join(guild):
    global servers
    channel = guild.text_channels[0]
    for c in guild.text_channels:
        if not c.permissions_for(guild.me).send_messages:
            continue
        channel = c
        break
    await channel.send('Hello! Use **stock help** to see my commands. Set a default channel for a stock feed with the command **stock set channel #channel**. Only the server owner may use this command.')

@client.event
async def on_message(message):
    global users
    global stockList
    global alreadySent
    global servers

    await update_data(users, message.author)

    userID = str(message.author.id)


    if '$' in message.content.lower():

        if message.author.id != 491431308644319252:
            await add_money(users, message.author, 50)
        
    if message.content.lower().startswith("stock set channel"):
        await addServer(message.guild, message.channel_mentions[0])
        
        
    if message.content.lower().startswith("stock"):
        messageWords = message.content.lower().split()
        userMoney = str(users[str(message.author.id)]['money'])

        if len(messageWords) >= 2:
            word3 = str(messageWords[1])
            word4 = ''
            word5 = ''

            if len(messageWords) >= 3:
                word4 = str(messageWords[2])

                if len(messageWords) == 4:
                    word5 = str(messageWords[3])
        if word3 == "info":
            await displayStocks(message.channel.id)
            return
        if word4 == 'buy':
            stockName = word3.upper()
            stockCost = stockList[stockName.upper()]['price']
            try:
                amount = int(word5)
            except:
                if word5.lower() == "all":
                    amount = math.floor(float(userMoney)/stockCost)
                pass

            totalCost = math.ceil(amount * stockCost)

            if amount <= 0:
                await message.channel.send("You must buy more than 0 stocks.")
            elif stockCost > 0:
                if totalCost > float(userMoney):
                    await message.channel.send("You don't have enough money to buy that many stocks.")
                if totalCost <= float(userMoney):
                    await message.channel.send(":dollar: Success! You have purchased " + str(round(amount,2)) + " stock(s) of " + stockName + " for $" + str(round(totalCost,2)) + ". :dollar:")
                    await add_stocks(message.author, stockName, amount)
                    await add_money(users, message.author, -1*totalCost)


                    blank = str(stockList[stockName.upper()]['buyers'][str(message.author.id)]['stocks'])
                    await message.channel.send(":moneybag: Now you have " + blank + " stock(s) of " + str(stockName) + " and $" + str(round(users[str(message.author.id)]['money'])) + ". :moneybag:")

            return

        if word4 == 'sell':


            stockName = word3.upper()
            stockCost = stockList[stockName.upper()]['price']
            stocksOwned = stockList[stockName.upper()]["buyers"][str(message.author.id)]["stocks"]
            try:
                amount = int(word5)
            except:
                if word5 == "all":
                    amount = stocksOwned
            totalProfit = amount * stockCost

            if amount <= 0:
                await message.channel.send("You must sell more than 0 stocks.")
            elif stockCost > 0:
                if amount > int(stocksOwned):
                    await message.channel.send("You don't have that many stocks to sell.")
                if amount <= int(stocksOwned):

                    await message.channel.send(":dollar: Success! You have sold " + str(round(amount,2)) + " stock(s) of " + stockName + " for $" + str(round(totalProfit,2)) + ". :dollar:")
                    await add_stocks(message.author, stockName, -1*amount)
                    await add_money(users, message.author, 1*totalProfit)

                    blank = str(stockList[stockName.upper()]['buyers'][str(message.author.id)]['stocks'])
                    await message.channel.send(":moneybag: Now you have " + blank + " stock(s) of " + stockName + " and $" + str(round(users[str(message.author.id)]['money'],2)) + ". :moneybag:")

            return
    if message.content.lower() == "my stocks":

        embed = discord.Embed(title="YOUR STOCKS", color=0x49382e)
        money = users[str(message.author.id)]['money']
        netWorth = 0
        netWorth += money
        embed.add_field(name= "Uninvested Money", value= round(money,2))
        for stock in stockList:
            stockName = stock
            stockValue = stockList[stock]['price']
            try:
                stocksOwned = stockList[stock]['buyers'][str(message.author.id)]['stocks']
            except:
                stocksOwned = 0
                pass
            embed.add_field(name=stockName, value= str(stocksOwned) + " ($" + str(round(stocksOwned * stockValue,2)) + ")")
            netWorth += stocksOwned * stockValue
        embed.add_field(name="Net Worth", value= round(netWorth,2))
        await message.channel.send( embed = embed)
        return

    if message.content.lower() == "my money":

        await message.channel.send( ":money_mouth: You have $" + str(round(users[str(message.author.id)]['money'],2)) + " :money_mouth: ")
        return

    if message.content.lower() == "stock help":
        embed = discord.Embed(title="STOCK COMMANDS", color=0x49382e)
        embed.add_field(name="$", value=f"Sending a message containing '$' gives $50")
        embed.add_field(name="My Money", value=f"Displays the amount of money that you have.")
        embed.add_field(name="Flip (Bet Amount) (Heads or Tails)", value=f"Coin flip to win (or lose) money.")
        embed.add_field(name="Leaderboards", value=f"Displays the 5 people with the most money.")
        embed.add_field(name="Give (Recipient) (Amount)", value=f"Transfers money to another person.")
        embed.add_field(name="Stock (Stock Abbreviation) Buy/Sell (Amount)", value= "Command for buying or selling stocks. Example: 'stocks ABC buy 1'")
        embed.add_field(name="Stock Info", value="Gives you the current graph and values of all stocks.")
        embed.add_field(name="My Stocks", value="Displays the amount of stocks you own from each company and the combined value of all of your stocks.")
        embed.add_field(name="Stock Set Channel #channel", value="Owner only command to set a channel for a stock feed.")
        await message.channel.send( embed = embed)
        return

    if message.content.lower().startswith("give"):

        userMoney = str(users[str(message.author.id)]['money'])
        messageWords = message.content.lower().split()
        amount = messageWords[2]
        reciever = message.mentions[0]
        if float(amount) > 0:
            if float(amount) <= float(userMoney):
                await message.channel.send( ":grin: " + str(message.author.mention) + " has given " + str(reciever.mention) + " $" + amount + "!")
                await add_money(users, message.author, -1 * int(amount))
                await add_money(users, reciever, int(amount))


    if message.content.lower() == "leaderboards":
        topSet = []
        
        for player in users:
            t = [users[player]["user"], users[player]["money"]]
            topSet.append(t)

        sortedTopSet = sorted(topSet, key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title="LEADERBOARD", color=0x49382e)

        limit = 5
        
        if len(users) < 5:
            limit = len(users)
            
        for x in range(limit):

            userID = str(sortedTopSet[x][0])
            userMoney = str(round(sortedTopSet[x][1],2))
            embed.add_field(name= userID, value= "$"+userMoney)

        await message.channel.send(embed = embed)

    if message.content.lower().startswith('flip'):
        userMoney = int(users[str(message.author.id)]['money'])
        messageWords = message.content.lower().split()

        try:
            betAmount = int(messageWords[1])
        except:
            pass

        try:
            choice = str(messageWords[2])
        except:
            choice = ""

        if choice != "tails":
            choice = "heads"

        if str(messageWords[1]) == "all":
            betAmount = userMoney
        if betAmount <= 0:
            await message.channel.send( "You have to bet more than 0!")

        if betAmount > userMoney:
            await message.channel.send( "Your bet is too high!")

        if betAmount <= userMoney and betAmount > 0:

            await message.channel.send( "You pick **" + choice + "**!")
            flip = randint(1,2)
            botChoice = ""

            if flip == 1:
                botChoice = "heads"
                await message.channel.send( "The coin lands on...")
                await message.channel.send( "**" + botChoice + "**!")
            if flip == 2:
                botChoice = "tails"
                await message.channel.send( "The coin lands on...")
                await message.channel.send( "**" + botChoice + "**!")
            if botChoice == choice:
                await message.channel.send( ":moneybag: You win $" + str(betAmount) + "! :moneybag:")
                await add_money(users, message.author, betAmount)


            elif botChoice != choice:
                await message.channel.send( ":rage: HAHAHA You LOSE!! NO!! :rage:")
                await add_money(users, message.author, betAmount*-1)

        return

async def update_data(users, user):
    if not str(user.id) in users:    
        users[str(user.id)] = {}
        users[str(user.id)]['money'] = 0
        users[str(user.id)]['user'] = str(user)
        users[str(user.id)]['netWorth'] = 0

    with open('users.json', 'w') as f:
        json.dump(users,f)

async def add_money(users,user,money):

    users[str(user.id)]['money'] += money
    with open('users.json', 'w') as f:
        json.dump(users,f)

async def newStock():
    global users
    global stockList
    ## A. Names the stock (newStock)
    adj1 = str(r.choice(AdjAlpha))
    adj2 = str(r.choice(AdjAlpha))
    # ensures no repeats in adjectives
    while adj1 == adj2:
        adj2 = str(r.choice(AdjAlpha))
    newStock = adj1 + ' ' + adj2 + ' ' + str(r.choice(NAlpha))

    ## B. Creates the Ticker symbol (newTicker)
    pullTicker = [char for char in newStock if char.isupper()]
    newTicker = ''

    for char in pullTicker:
        newTicker += str(char)

    initialPrice = round(random.triangular(1,25,625),2)

    ### i. Creates the initial mean and stdev for the growth rate
    randomX = round(random.triangular(-5,1,5),2)
    randomY = round(random.triangular(0.1,1,10),2)

    #opens json file and adds the ticker and the price under the stock name
    if not newTicker in stockList:
        stockList2 = stockList.copy()
        stockList2[newTicker] = {}
        stockList2[newTicker]['stockName'] = newStock
        stockList2[newTicker]['initialPrice'] = initialPrice
        stockList2[newTicker]['price'] = initialPrice
        stockList2[newTicker]['randomX'] = randomX
        stockList2[newTicker]['randomY'] = randomY
        stockList2[newTicker]['buyers'] = {}
        stockList2[newTicker]['pastPrices'] = []
        
    with open('stockList.json', 'w') as f:
        json.dump(stockList2,f)

# B. This is the growth model, which takes a rate from a normal distribution using the mean and stdef from above

async def YSELoop(stock, price, randomX, randomY):

    global users
    global stockList

    if len(stockList[stock]['pastPrices']) == 50:

        if stockList[stock]['pastPrices'][49] <= 5:
            returnValue = stockList[stock]['pastPrices'][49] - 1
            if stockList[stock]['pastPrices'][49] <= 0:
                print("stock dies")

                for server in servers:
                    try:
                        await client.get_channel(servers[server]['channel']).send(":tired_face: :chart_with_downwards_trend: :chart_with_downwards_trend: :chart_with_downwards_trend: :tired_face: NO!!!!!! **" + stock + "** HAS CRASHED AND ALL SHAREHOLDERS OF **" + stock + "** HAVE LOST THEIR MONEY INVESTED!")
                    except:
                        pass
                del stockList[stock]
                with open('stockList.json', 'w') as f:
                    json.dump(stockList,f)

                return -500
            return returnValue

    growthRate = random.normal(randomX, randomY)/75
    price = price + price*growthRate
    if price <= 0:
        price = 0

    with open('stockList.json', 'w') as f:
        json.dump(stockList,f)


    return round(price,2)

async def displayStocks(serverID):
    global users
    global stockList
    await client.get_channel(serverID).send(file=discord.File('recentchart.png'))

    embed = discord.Embed(title="STOCK MARKET | " + strftime("%H:%M:%S"), color=0x49382e)
    for stock in stockList:
        name = stockList[stock]['stockName']
        stockPrice = stockList[stock]['price']
        embed.add_field(name=name, value=round(stockPrice,2))
    await client.get_channel(serverID).send(embed = embed)

async def addServer(guild, channel):
    print("adding server")
    global servers
    if not str(guild.id) in servers:    
        servers[str(guild.id)] = {}
        servers[str(guild.id)]['channel'] = channel.id
    else:
        servers[str(guild.id)]['channel'] = channel.id

    with open('servers.json', 'w') as f:
        json.dump(servers,f)


async def add_stocks(username, stockname, number):
    global users
    global stockList
    
    if not str(username.id) in stockList[stockname]['buyers']:

        stockList[stockname]['buyers'][str(username.id)] = {}
        stockList[stockname]['buyers'][str(username.id)]['username'] = str(username)
        stockList[stockname]['buyers'][str(username.id)]['stocks'] = 0
    stockList[stockname]['buyers'][str(username.id)]['stocks'] += number
    stockList[stockname]['buyers'][str(username.id)]['stocks']
    with open('stockList.json', 'w') as f:
        json.dump(stockList,f)


async def playAudio(audioName, message):
        try:
            server = message.server
            voice_client = client.voice_client_in(server)
            await voice_client.disconnect()
        except:
            pass
        channel = message.author.voice_channel
        join = await client.join_voice_channel(channel)
        play = join.create_ffmpeg_player(audioName)
        play.start()

client.run("insert key here")
