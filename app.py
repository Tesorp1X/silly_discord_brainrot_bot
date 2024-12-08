import os
from dotenv import load_dotenv
from typing import Final

from discord import Intents, Client, Message
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord.utils import get
from discord import FFmpegPCMAudio

from yt_dlp import YoutubeDL

from responses import get_response


load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


intents: Intents = Intents.all()
intents.message_content = True # NOQA
bot: Bot = commands.Bot(command_prefix='.', intents=intents)


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

@bot.command()
async def play(ctx, url) -> None:
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
  ffmpeg_opts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
  }
  ffmpeg_path = 'E:\\ffmpeg-2024-12-04-git-2f95bc3cb3-full_build\\bin\\ffmpeg.exe'
  channel = ctx.message.author.voice.channel
  voice = get(bot.voice_clients, guild=ctx.guild)

  if voice and voice.is_connected():
    await voice.move_to(channel)
  else:
    voice = await channel.connect()

  if not voice.is_playing():
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      video_url = info.get('url')
      voice.play(FFmpegPCMAudio(executable=ffmpeg_path, source=video_url, **ffmpeg_opts))
      voice.is_playing()
      await ctx.send(f":fire: Playing {info['title']}")
  else:
    await ctx.send(":fire: Music is already Playing...")
    return


@bot.command()
async def stop(ctx):
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

# Pause the Music
@bot.command()
async def pause(ctx):
  voice = get(bot.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
    await ctx.send(":fire: Music Paused...")

# Resume the Music
@bot.command()
async def resume(ctx):
  voice = get(bot.voice_clients, guild=ctx.guild)
  if not voice.is_playing():
    voice.resume()
    await ctx.send(":fire: Music Resumed...")

# Volume Controll
@bot.command()
async def volume(ctx, volume: int):
  volume = int(volume)
  if ctx.voice_client is None:
    return await ctx.send("Not connected to a voice channel.")

  ctx.voice_client.source.volume = volume / 100
  await ctx.send(f":fire: Changed volume to {volume}%")

# Checks users connectivity
@play.before_invoke
async def ensure_voice(ctx):
  if ctx.voice_client is None:
    if ctx.author.voice:
      await ctx.author.voice.channel.connect()
    else:
      await ctx.send("You are not connected to a voice channel.")
      raise commands.CommandError("Author not connected to a voice channel.")
  elif ctx.voice_client.is_playing():
    ctx.voice_client.stop()

def main() -> None:
  bot.run(token=TOKEN)

if __name__ == '__main__':
  main()