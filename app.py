import asyncio
import os
from dotenv import load_dotenv
from typing import Final
from random import randint

from discord import Intents, Message, FFmpegOpusAudio
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from discord.utils import get
from discord import Game

from yt_dlp import YoutubeDL

import BotExceptions
import responses
from BotExceptions import InvalidGuildIdException
from MusicQueue import MusicQueue, QueueItem


load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


intents: Intents = Intents.all()
intents.message_content = True # NOQA
bot: Bot = commands.Bot(command_prefix='.', intents=intents)
music_queue_obj = MusicQueue()

YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': True,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
    }
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                 'options': '-vn -filter:a "volume=0.25"'}



async def send_message(message: Message, user_message: str) -> None:
  if not user_message:
    print('Message was empty: intents probably..')
    return
  response: str = responses.get_default_response(user_message)
  await message.channel.send(response)



@bot.event
async def on_ready() -> None:
  print(f'{bot.user} is now operational')



async def play_next(ctx: Context) -> None:
  if not music_queue_obj.is_empty(guild_id=ctx.guild.id):
    if music_queue_obj.is_shuffled(ctx.guild.id):
      rand_index = randint(0, music_queue_obj.length(guild_id=ctx.guild.id))
      song_item = music_queue_obj.pop(guild_id=ctx.guild.id, index=rand_index)
      next_song_url = song_item.get_video_url()
      next_song_yt_link = song_item.get_yt_link()
      next_song_title = song_item.get_title()
    else:
      song_item = music_queue_obj.pop(guild_id=ctx.guild.id)
      next_song_url = song_item.get_video_url()
      next_song_yt_link = song_item.get_yt_link()
      next_song_title = song_item.get_title()
    await play_song(ctx, yt_link=next_song_yt_link, video_link=next_song_url, video_title=next_song_title)
  else:
    await ctx.send(responses.queue_ended())
    await stop(ctx)



@bot.command(name="play_all")
async def play_all(ctx: Context) -> None:
  if not music_queue_obj.is_empty(ctx.guild.id):
    await play_next(ctx)
  else:
    await ctx.send(responses.empty_queue_response())



@bot.command(name="play")
async def play(ctx: Context) -> None:
  url: str = ctx.message.content
  with YoutubeDL(YDL_OPTS) as ydl:
    info = ydl.extract_info(url, download=False)
    video_link = info.get('url') #direct link, that is going to be used by FFMPEG
    video_title = info.get('title')
    await play_song(ctx, yt_link=url, video_title=video_title, video_link=video_link)



async def play_song(ctx: Context, yt_link: str, video_title: str, video_link) -> None:
  channel = ctx.message.author.voice.channel
  voice = get(bot.voice_clients, guild=ctx.guild)

  if voice and voice.is_connected():
    await voice.move_to(channel)
  else:
    voice = await channel.connect()

  voice.play(FFmpegOpusAudio(source=video_link, **FFMPEG_OPTS),
             after=lambda a: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
  await bot.change_presence(activity=Game(name=video_title))


  if music_queue_obj.is_empty(guild_id=ctx.guild.id):
    await ctx.send(responses.now_playing_response(song_title=video_title, yt_link=yt_link))
  else:
    next_song = music_queue_obj.get_next_song_title(guild_id=ctx.guild.id)
    await ctx.send(responses.now_playing_response(song_title=video_title, yt_link=yt_link, next_song_title=next_song))



@bot.command(name="stop")
async def stop(ctx: Context) -> None:
  voice = get(bot.voice_clients, guild=ctx.guild)

  if voice.is_playing():
    voice.stop()
    await ctx.voice_client.disconnect()
    await ctx.send(":fire: Music Stopped...")
  else:
    voice.stop()
    await ctx.voice_client.disconnect()
  await bot.change_presence(activity=None)
  music_queue_obj.remove_queue(guild_id=ctx.guild.id)



@bot.command(name="pause")
async def pause(ctx: Context):
  voice = get(bot.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
    await ctx.send(":fire: Music Paused...")



@bot.command(name="resume")
async def resume(ctx: Context):
  voice = get(bot.voice_clients, guild=ctx.guild)
  if not voice.is_playing():
    voice.resume()
    await ctx.send(":fire: Music Resumed...")



@bot.command(name="volume")
async def volume(ctx: Context, volume: int):
  volume = int(volume)
  if ctx.voice_client is None:
    return await ctx.send("Not connected to a voice channel.")

  ctx.voice_client.source.volume = volume / 100
  await ctx.send(f":fire: Changed volume to {volume}%")



@bot.command(name="add")
async def add_to_queue(ctx: Context, url: str) -> str:
  with YoutubeDL(YDL_OPTS) as ydl:
    info = ydl.extract_info(url, download=False)
    video_url = info.get('url')
    video_title = info.get('title')
    try:
      music_queue_obj.add_item(guild_id=ctx.guild.id,
                               video_title=video_title,
                               video_url=video_url,
                               video_yt_link=url)
      await ctx.send(responses.song_added_response(song_name=video_title))
    except BotExceptions.InvalidQueueItemAttributeException as e:
      #TODO Error response
      await ctx.send(e.message)



@bot.command(name="queue")
async def show_queue(ctx: Context) -> None:
  queue_list = music_queue_obj.get(guild_id=ctx.guild.id)
  response = responses.queue_list_response(queue_list)
  await ctx.send(response)



@bot.command(name="clear_queue")
async def clear_queue(ctx: Context) -> None:
  try:
    music_queue_obj.remove_queue(guild_id=ctx.guild.id)
    await ctx.send(responses.queue_cleared_response())
  except BotExceptions.InvalidGuildIdException as e:
    await ctx.send("Очередь уже пуста!")



@bot.command(name="skip")
async def skip_song(ctx: Context) -> None:
  if music_queue_obj.is_empty(guild_id=ctx.guild.id):
    await stop(ctx)
    await ctx.send("Это была последняя песня...")
  else:
    await pause(ctx)
    await play_next(ctx)



@play.before_invoke
async def ensure_voice(ctx: Context) -> None:
  if ctx.voice_client is None:
    if ctx.author.voice:
      await ctx.author.voice.channel.connect()
    else:
      await ctx.send("You are not connected to a voice channel.")
      raise commands.CommandError("Author not connected to a voice channel.")
  elif ctx.voice_client.is_playing():
    ctx.voice_client.stop()



@bot.event
async def on_message(message: Message) -> None:
  if message.author == bot.user:
    return

  username: str = str(message.author)
  user_message: str = message.content
  channel: str = str(message.channel)

  print(f'[{channel}] {username}: {user_message}')
  if not user_message[0] == '.':
    await send_message(message, user_message)
  await bot.process_commands(message)



def main() -> None:
  bot.run(token=TOKEN)

if __name__ == '__main__':
  main()