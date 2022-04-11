from redbot.core import commands, Config
import random
import urllib.request
import urllib.parse as parse
import os
from PIL import Image, ImageOps
import io

LATEX_TEMPLATE="template.tex"

class BookBingo(commands.Cog):
    """Allows users to run a Google Books search in inline text"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1544112022)

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
                    "Any Stage/Screenplay",
                    "A book about military/war/politics",
                    "A book with people on the cover",
                    "A book about art",
                    "A book about music",
                    "A New York Times Bestseller",
                    "A book with a pretty cover",
                    "A book set in a dystopia",
                    "A book with less than 3 stars on Amazon/Goodreads",
                    "A book that won the Newberry Medal",
                    "A book that won the Pulitzer",
                    "A Book Club Book Of The Month"
                ]
            }
        }

        self.config.register_global(**default_global)

    @commands.command()
    async def newcard(self, message):
        data = await self.config.data()
        goallist = data["goals"]
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
        for i in range(1,5):
            for j in range(1,5):
                selectedgoal = goallist[random.randint(0, len(goallist)-1)]
                goallist.remove(selectedgoal)
                data["cards"][str(message.author.id)][str(i)][str(j)] = selectedgoal
        data["cards"][str(message.author.id)]["3"]["3"] = "!Free Space"
        await self.config.data.set(data)
        img = await self.makecard(str(message.author.id), data=data)
        await message.channel.send(content="Your Card:", file=img)

    def generate_image_online(self, userid, books=False, data=None):
        if(data == None):
            return
        latex = "\\begin\{table\}[]\n\\begin\{tabular\}\{|l|l|l|l|l|\}\n\\hline\n"
        carddata = data["cards"][userid]
        for i in range(1,5):
            for j in range(1,5):
                add = carddata[str(i)][str(j)]
                if(add.startswith("!")):
                    add = add[1:]
                    add = "\\color[HTML]\{32CB00\}" + add
                if(add.find("|") != -1):
                    if(books):
                        add = add[add.find("|"):]
                    else:
                        add = add[:add.find("|")]
                if(j != 5):
                    latex += add + " & "
                else:
                    latex += add + "\\\\ \\hline\n"
        latex += "\\end\{tabular\}\n\\end\{table\}"
        url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?'
        url += urllib.parse.quote(latex, safe='')
        fn = str(random.randint(0, 2 ** 31)) + '.png'
        urllib.request.urlretrieve(url, fn)
        return fn

    @commands.command()
    async def mycard(self, message):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        img = await self.makecard(userid=str(message.author.id), data=data)
        await message.channel.send(content="Your Card:", file=img)

    @commands.command()
    async def mybooks(self, message):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        img = await self.makecard(userid=str(message.author.id), books=True, data=data)
        await message.channel.send(content="Your Card:", file=img)

    @commands.command()
    async def complete(self, message):
        data = await self.config.data()
        if(str(message.author.id) not in data["cards"]):
            await message.channel.send("You don't have a card yet!")
            return
        carddata = data["cards"][str(message.author.id)]
        if(message.content.find(".") == -1):
            await message.channel.send("Invalid solution format!")
            return
        objhalf = message.content[:message.content.find(".")].lower()
        tcol = 0
        trow = 0
        for i in range(1,5):
            for j in range(1,5):
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
        carddata[str(trow)][str(tcol)] = "!" + carddata[str(trow)][str(tcol)] + "|" + message.content[message.content.find(".")+1:]
        data["cards"][str(message.author.id)] = carddata
        await self.config.data.set(data)
        await message.channel.send("You have claimed the space {0} with the book {1}!".format(carddata[str(trow)][str(tcol)], message.content[message.content.find(".")+1:]))

    def generate_image(self, userid, books=False, data=None):
        if(data == None):
            return
        latex = "\\begin\{table\}[]\n\\begin\{tabular\}\{|l|l|l|l|l|\}\n\\hline\n"
        carddata = data["cards"][userid]
        for i in range(1,5):
            for j in range(1,5):
                add = carddata[str(i)][str(j)]
                if(add.startswith("!")):
                    add = add[1:]
                    add = "\\color[HTML]\{32CB00\}" + add
                if(add.find("|") != -1):
                    if(books):
                        add = add[add.find("|"):]
                    else:
                        add = add[:add.find("|")]
                if(j != 5):
                    latex += add + " & "
                else:
                    latex += add + "\\\\ \\hline\n"
        latex += "\\end\{tabular\}\n\\end\{table\}"
        name = str(random.randint(0, 2 ** 31))
        latex_file = name + '.tex'
        dvi_file = name + '.dvi'
        png_file = name + '1.png'

        with open(LATEX_TEMPLATE, 'r') as textemplatefile:
            textemplate = textemplatefile.read()

            with open(latex_file, 'w') as tex:
                backgroundcolour = self.settings['latex']['background-colour']
                textcolour = self.settings['latex']['text-colour']
                latex = textemplate.replace('__DATA__', latex).replace('__BGCOLOUR__', backgroundcolour).replace('__TEXTCOLOUR__', textcolour)

                tex.write(latex)
                tex.flush()
                tex.close()

        imagedpi = self.settings['latex']['dpi']
        latexsuccess = os.system('latex -quiet -interaction=nonstopmode ' + latex_file)
        if latexsuccess == 0:
            os.system('dvipng -q* -D {0} -T tight '.format(imagedpi) + dvi_file)
            return png_file
        else:
            return ''

    async def makecard(self, userid, books=False, data=None):
        if(data == None):
            return
        latex = "\\begin\{table\}[]\n\\begin\{tabular\}\{|l|l|l|l|l|\}\n\\hline\n"
        carddata = data["cards"][userid]
        for i in range(1,5):
            for j in range(1,5):
                add = carddata[str(i)][str(j)]
                if(add.startswith("!")):
                    add = add[1:]
                    add = "\\color[HTML]\{32CB00\}" + add
                if(add.find("|") != -1):
                    if(books):
                        add = add[add.find("|"):]
                    else:
                        add = add[:add.find("|")]
                if(j != 5):
                    latex += add + " & "
                else:
                    latex += add + "\\\\ \\hline\n"
        latex += "\\end\{tabular\}\n\\end\{table\}"
        base_url = "https://latex.codecogs.com/gif.latex?%5Cbg_white%20%5CLARGE%20"
        equation = parse.quote(latex)
        url = f"{base_url}{equation}"

        try:
            async with self.session.get(url) as r:
                image = await r.read()
            image = Image.open(io.BytesIO(image)).convert("RGBA")
        except Exception as exc:
            image = None

        if not image:
            return

        image = ImageOps.expand(image, border=10, fill="white")
        image_file_object = io.BytesIO()
        image.save(image_file_object, format="png")
        image_file_object.seek(0)
        return image_file_object
