from logging import NullHandler
from numbers import Number
import discord
from discord import integrations
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from replit import db
import time
import random
from datetime import datetime
import keep_live
import os

fishing_rod = {
  "poop_rod":{"Durability":1,"Value":10,"Level":1,"Vietsub":"cần câu shit"},
  "wooden_rod":{"Durability":50,"Value":10,"Level":1,"Vietsub":"cần câu gỗ"},
}

fish_level = {
  "fish1":{"Level":1,"Rarity":10,"Value":1},
  "fish2":{"Level":1,"Rarity":10,"Value":2},
  "fish3":{"Level":1,"Rarity":50,"Value":3},
}

fish_list =  {}


for i in range(3):
  fish_list[i]={}
  for key, inner_dict in fish_level.items():
    fishtab={}
    if inner_dict["Level"] <= i:
      fishtab[key] = inner_dict["Rarity"]

    rarities = [fish for fish in fishtab.values()]
    fish_list[i][key]=rarities

def random_rod(depth):
  chossetab=fish_list[depth]
  fish_names = list(chossetab.keys())
  rarities = [fish[0] for fish in chossetab.values()]
  print(fish_names,rarities)
  selected_fish = random.choices(fish_names, weights=rarities, k=1)[0]
  return selected_fish

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_db(id,choosesave):
  if f"{id}-{choosesave}" in db:
    return db[f"{id}-{choosesave}"]
  else:
    new=False
    if choosesave == "Rod":
      new=True

    if new == True:
      db[f"{id}-{choosesave}"]="None"
      return db[f"{id}-{choosesave}"]
    else:
      db[f"{id}-{choosesave}"]=0
      return db[f"{id}-{choosesave}"]
      
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name="ping", description="Check the bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency is {latency}ms")


@bot.tree.command(name="shop", description="mua cần câu")
async def shop(ctx : Interaction):
  embed = discord.Embed(
    title="Shop",
    description="cần câu đê mại dô mại dô \n mua bằng cách ```/buy <item>```",
    color=discord.Color.blue()
  )
  for key, inner_dict in fishing_rod.items():
    embed.add_field(name=f"{inner_dict['Vietsub']} <{key}> ", value=f"Giá: {inner_dict['Value']}$", inline=False)
  
  await ctx.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="chọn cần câu mua")
async def buy(ctx : Interaction,item: str):
  if item in fishing_rod:
    if get_db(ctx.user.id,"Rod") == item:
      await ctx.response.send_message("```bạn đã mua cần câu này rồi```")
    elif get_db(ctx.user.id,"Coin") >= fishing_rod[item]["Value"]:
      db[f"{ctx.user.id}-Rod"]=item
      db[f"{ctx.user.id}-Durability"]=(fishing_rod[item]["Durability"])
      db[f"{ctx.user.id}-Coin"]-=(fishing_rod[item]["Value"])
      await ctx.response.send_message(item)
    else:
       await ctx.response.send_message("```bạn đéo đủ tiền```")
  else:
    await ctx.response.send_message("```Chúng tôi không thể tìm thấy cần cậu bạn muốn mua```")

@bot.tree.command(name="taixiu", description="đặt cược số tiền thắng nhận 1:0.5")
async def taixiu(ctx : Interaction,ou : str,tien : int):
  if tien <= get_db(ctx.user.id,"Coin") and (ou == "tai" or ou == "xiu"):
    random_vanmay=random.randint(1,6)
    random_vanmay2=random.randint(1,6)
    random_vanmay3=random.randint(1,6)
    cong_tru=False
    if random_vanmay+random_vanmay2+random_vanmay3 >= 3 and random_vanmay+random_vanmay2+random_vanmay3 <= 10:
      if ou == "xiu":
        cong_tru=True
    if random_vanmay+random_vanmay2+random_vanmay3 >= 11 and random_vanmay+random_vanmay2+random_vanmay3 <= 18:
      if ou == "tai":
        cong_tru=True
    if cong_tru == True:
      db[f"{ctx.user.id}-Coin"]+=tien*0.5
      await ctx.response.send_message(f"```Chúc mừng bạn thắng {tien*0.5}$ ```")
    else:
      db[f"{ctx.user.id}-Coin"]-=tien
      await ctx.response.send_message(f"```Chúc mừng bạn thua {tien}$ ```")
  else:
    await ctx.response.send_message("```Bạn éo đủ tiền hoặc viết sai chữ 'tai' hoặc 'xiu'```")
@bot.tree.command(name="fishing", description="câu cá")
async def fishing(ctx : Interaction):
  if get_db(ctx.user.id,"Rod") != "None":
    if db[f"{ctx.user.id}-Durability"] == 0:
      db[f"{ctx.user.id}-Rod"]="None"
      await ctx.response.send_message("```Cần câu bạn hỏng rồi```")
    else:
      selected_fish = random_rod(fishing_rod[get_db(ctx.user.id,"Rod")]["Level"])
      embed = discord.Embed(
        title= f"Cá",
        description=f"{ctx.user.mention} ```đã câu được {selected_fish}```",
        color=discord.Color.blue()
      )
      db[f"{ctx.user.id}-{selected_fish}"]=get_db(ctx.user.id,selected_fish)+1
      await ctx.response.send_message(embed=embed)
      db[f"{ctx.user.id}-Durability"]-=1
  else:
    await ctx.response.send_message(f"```Bạn éo có cần câu```")

@bot.tree.command(name="reward", description="nhận tiền nè cưng")
async def reward(ctx : Interaction):
  current_time_seconds = time.time()
  if current_time_seconds-get_db(ctx.user.id,"Timereward")  >= 1:
    db[f"{ctx.user.id}-Timereward"]=current_time_seconds
    tien_nhan=random.randint(50,100)
    db[f"{ctx.user.id}-Coin"]=db[f"{ctx.user.id}-Coin"]+tien_nhan
    await ctx.response.send_message(f"```số tiền nhần được ({tien_nhan}) nhận tiền nè cưng```")
  else:
    current_datetime = datetime.fromtimestamp(3600-((current_time_seconds%(24*3600))-get_db(ctx.user.id,"Timereward")))
    formatted_datetime = current_datetime.strftime("%H giờ %M phút %S giây")

    await ctx.response.send_message(f"```Quay lại sau {formatted_datetime} ```")

@bot.tree.command(name="sell", description="bán cá")
async def sell(ctx : Interaction,ca: str):
  if ca =="all":
    money_get=0
    for key,inner_dict in fish_level.items():
      money_get+=get_db(ctx.user.id,key)*fish_level[key]["Value"]
      db[f"{ctx.user.id}-{key}"]=0
    db[f"{ctx.user.id}-Coin"]+=money_get  
    await ctx.response.send_message(f"Chúc mừng bạn bán được {money_get}$")
  elif ca in fish_level:
    money_get=get_db(ctx.user.id,ca)*fish_level[ca]["Value"]
    db[f"{ctx.user.id}-Coin"]+=money_get
    db[f"{ctx.user.id}-{ca}"]=0
    await ctx.response.send_message(f"Chúc mừng bạn bán được {money_get}$")
  else:
    await ctx.response.send_message("Sai tên cá")
@bot.tree.command(name="inventory", description="xem kho đồ của bạn")
async def inventory(ctx : Interaction):
  embed = discord.Embed(
    title= f"{ctx.user.name} Inventory",
    description=f"```Tiền Hiện có : {get_db(ctx.user.id,'Coin')}```",
    color=discord.Color.blue()
  )
  abc="```"
  for key, inner_dict in fish_level.items():
    abc=f"{abc}{key}:{get_db(ctx.user.id,key)}\n"

  abc=f"{abc}```"
  embed.add_field(name="Các loại đồ bạn có :", value=abc, inline=False)
  
  await ctx.response.send_message(embed=embed)

keep_live.keep_alive()
bot.run(os.environ['TOKEN'])
