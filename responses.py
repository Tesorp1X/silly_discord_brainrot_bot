from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio

from youtube_dl import YoutubeDL

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'you\'ve got to say something'
    elif 'hello' in lowered:
        return 'ohayo!'
    else:
        return 'chippi chippi chapa chapa'

