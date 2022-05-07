from redbot.core import commands, Config
import random
from PIL import Image, ImageDraw, ImageFont
import random
import asyncio
import discord
from copy import deepcopy


class BookBingo(commands.Cog):
    """The Bingo Class"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1244572022)

        default_global = {
            "data": {
                "cards": {
                    "testcard": {
                        "1": {"1":"", "2":"", "3":"", "4":"", "5":""},
                        "2": {"1":"", "2":"", "3":"", "4":"", "5":""},
                        "3": {"1":"", "2":"", "3":"", "4":"", "5":""},
                        "4": {"1":"", "2":"", "3":"", "4":"", "5":""},
                        "5": {"1":"", "2":"", "3":"", "4":"", "5":""}
                    }
                },
                "goals": [
                    "Any Romance",
                    "Any Sci-Fi",
                    "Any Fantasy",
                    "Book under 100 pages",
                    "Any E-Book",
                    "Any Hardcover Book",
                    "Any Book Published in 2022",
                    "Any NonFiction",
                    "Something out of your comfort zone",
                    "One word title",
                    "Any Book Published Before 1900",
                    "Book to Movie",
                    "Banned Book",
                    "Woman Author",
                    "2nd book in a series",
                    "Any YA book",
                    "Any Comedy",
                    "Any Classic",
                    "Any Script or Screenplay",
                    "A book about the military, war, or politics",
                    "A book with people on the cover",
                    "A book about art",
                    "A book about music",
                    "A New York Times Bestseller",
                    "A book with a pretty cover",
                    "A book set in a dystopia",
                    "A book with less than 3 stars on Amazon or Goodreads",
                    "A book that won the Newberry Medal",
                    "A book that won the Pulitzer Prize",
                    "A Book Club Book Of The Month"
                ]
            }
        }

        self.config.register_global(**default_global)

    @commands.command()
    async def newcard(self, message):
        data = await self.config.data()
        goallist = deepcopy(data["goals"])
        if(str(message.author.id) in data["cards"]):
            await message.channel.send("You already have a card!")
            return
        data["cards"][str(message.author.id)] = {
            "1": {"1":"", "2":"", "3":"", "4":"", "5":""},
            "2": {"1":"", "2":"", "3":"", "4":"", "5":""},
            "3": {"1":"", "2":"", "3":"", "4":"", "5":""},
            "4": {"1":"", "2":"", "3":"", "4":"", "5":""},
            "5": {"1":"", "2":"", "3":"", "4":"", "5":""}
        }
        for i in range(1,6):
            for j in range(1,6):
                selectedgoal = goallist[random.randint(0, len(goallist)-1)]
                goallist.remove(selectedgoal)
                data["cards"][str(message.author.id)][str(i)][str(j)] = selectedgoal
        data["cards"][str(message.author.id)]["3"]["3"] = "!Free Space"
        await self.config.data.set(data)
        img = await self.makecard(str(message.author.id), data=data)
        img.save("bingo.png")
        await message.channel.send(content="Your Card:", file=discord.File("bingo.png"))

    @commands.command()
    async def debugdumpdict(self, message):
        data = await self.config.data()
        await message.channel.send(str(data))

    @commands.command()
    async def debugdumpcard(self, message):
        data = await self.config.data()
        del data["cards"][str(message.author.id)]
        await message.channel.send("Deleted card!")

    @commands.command()
    async def mycard(self, message):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        img = await self.makecard(userid=str(message.author.id), data=data)
        img.save("bingo.png")
        await message.channel.send(content="Your Card:", file=discord.File("bingo.png"))

    @commands.command()
    async def mybooks(self, message):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        img = await self.makecard(userid=str(message.author.id), books=True, data=data)
        img.save("bingo.png")
        await message.channel.send(content="Your Card:", file=discord.File("bingo.png"))

    @commands.command()
    async def complete(self, message, *, arg):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        carddata = data["cards"][str(message.author.id)]
        if(arg.find(".") == -1):
            await message.channel.send("Invalid solution format!")
            return
        objhalf = arg[:arg.find(".")].lower()
        tcol = 0
        trow = 0
        for i in range(1,6):
            for j in range(1,6):
                if(carddata[str(i)][str(j)].lower().find(objhalf) != -1):
                    tcol = j
                    trow = i
                    break
        if(tcol == 0 or trow == 0):
            await message.channel.send("Target not found!")
            return
        if(carddata[str(trow)][str(tcol)].startswith("!")):
            await message.channel.send("You already claimed this space!")
            return
        carddata[str(trow)][str(tcol)] = "!" + carddata[str(trow)][str(tcol)] + "|" + arg[arg.find(".")+1:]
        data["cards"][str(message.author.id)] = carddata
        await self.config.data.set(data)
        await message.channel.send("You have claimed the space {0} with the book {1}!".format(carddata[str(trow)][str(tcol)][:carddata[str(trow)][str(tcol)].find("|")][1:], arg[arg.find(".")+1:].lstrip()))

    async def makecard(self, userid, books=False, data=None):
        if(data == None):
            return
        carddata = data["cards"][userid]
        img = Image.new('RGB', (1000, 1000), color='white')
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("NotoMono-Regular.ttf", 20)
        for l in range(1, 5):
            d.line(((l*200, 0), (l*200), 1000), fill='black', width=10)
            d.line(((0, l*200),  (1000, l*200)), fill='black', width=10)
        for i in range(1, 6):
            for j in range(1,6):
                done = False
                temp = carddata[str(i)][str(j)]
                if(temp.startswith("!")):
                    temp = temp[1:]
                    done = True
                if(temp.find("|") != -1):
                    if(books):
                        temp = temp[temp.find("|")+1:].lstrip()
                    else:
                        temp = temp[:temp.find("|")]
                tempList = temp.split()
                temp = ""
                for k in range(0, len(tempList)):
                    if (k % 2 == 1):
                        temp += tempList[k] + "\n"
                    else:
                        temp += tempList[k] + " "
                if(done):
                    d.text(((i*200)-190, (j*200)-195), text=temp, fill='green', font=font)
                else:
                    d.text(((i*200)-190, (j*200)-195), text=temp, fill='black', font=font)
        return img

