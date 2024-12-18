import asyncio
import os
from dotenv import load_dotenv
from typing import Final

from discord import Intents, Message, FFmpegOpusAudio
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from discord.utils import get

from yt_dlp import YoutubeDL

from responses import get_response


load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


intents: Intents = Intents.all()
intents.message_content = True # NOQA
bot: Bot = commands.Bot(command_prefix='.', intents=intents)

queues = {}



async def send_message(message: Message, user_message: str) -> None:
  if not user_message:
    print('Message was empty: intents probably..')
    return

  try:
    response: str = get_response(user_message)
    await message.channel.send(response)
  except Exception as e:
    print(e)


@bot.event
async def on_ready() -> None:
  print(f'{bot.user} is now operational')

async def play_next(ctx: Context) -> None:
  if queues[ctx.guild.id]:
    next_song_url = queues[ctx.guild.id].pop(0)
    await play(ctx, url=next_song_url)

@bot.command(name="play")
async def play(ctx: Context, url: str) -> None:
  ydl_opts = {
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
  ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                 'options': '-vn -filter:a "volume=0.25"'}

  ffmpeg_path = os.getenv("FFMPEG_PATH")
  channel = ctx.message.author.voice.channel
  voice = get(bot.voice_clients, guild=ctx.guild)

  if voice and voice.is_connected():
    await voice.move_to(channel)
  else:
    voice = await channel.connect()


  with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    video_url = info.get('url')
    voice.play(FFmpegOpusAudio(source=video_url, **ffmpeg_opts),
               after=lambda a:  asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
    if voice.is_playing():
      await ctx.send(f":fire: Playing {info['title']}")



@bot.command(name="stop")
async def stop(ctx: Context):
  voice = get(bot.voice_clients, guild=ctx.guild)

  if voice.is_playing():
    voice.stop()
    await ctx.voice_client.disconnect()
    await ctx.send(":fire: Music Stopped...")
  else:
    voice.stop()
    await ctx.voice_client.disconnect()

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

@play.before_invoke
async def ensure_voice(ctx: Context):
  if ctx.voice_client is None:
    if ctx.author.voice:
      await ctx.author.voice.channel.connect()
    else:
      await ctx.send("You are not connected to a voice channel.")
      raise commands.CommandError("Author not connected to a voice channel.")
  elif ctx.voice_client.is_playing():
    ctx.voice_client.stop()

@bot.command(name="add")
async def add_to_queue(ctx: Context, url: str):
  if ctx.guild.id not in queues:
    queues[ctx.guild.id] = []
  queues[ctx.guild.id].append(url)
  print(queues)
  await ctx.send("Added to queue!")

@bot.command(name="clear_queue")
async def clear_queue(ctx: Context):
  if ctx.guild.id in queues:
    queues[ctx.guild.id].clear()
    await ctx.send("Queue cleared!")
  else:
    await ctx.send("Queue is already empty!")

@bot.command(name="skip")
async def skip_song(ctx: Context) -> None:
  if queues[ctx.guild.id]:
    await ctx.send("Skipping song...")
    await pause(ctx)
    await play_next(ctx)
  else:
    await stop(ctx)
    await ctx.send("That was the last one.")


def main() -> None:
  bot.run(token=TOKEN)

if __name__ == '__main__':
  main()