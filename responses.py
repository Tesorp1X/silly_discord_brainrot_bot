from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio

from youtube_dl import YoutubeDL
import MusicQueue

def get_default_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'you\'ve got to say something'
    elif 'hello' in lowered:
        return 'ohayo!'
    else:
        return 'chippi chippi chapa chapa'

"""
    Discord Markdown Format:
    -Italics	*italics* or _italics_	Underline italics	__*underline italics*__
    -Bold	**bold**	Underline bold	__**underline bold**__
    -Bold Italics	***bold italics***	underline bold italics	__***underline bold italics***__
    -Underline	__underline__	Strikethrough	 ~~Strikethrough~~
    -Headers # ## ###
    -Masked Links [Text](link)
    -Lists - *
    -Code block `code here`
"""

def now_playing_response(song_title: str, yt_link: str, next_song_title="Nothing...") -> str:

    now_playing_text = f"**Сейчас играет: [{song_title}]({yt_link})**"
    next_song_text = f"**Следующая песня:** *{next_song_title}*"
    return now_playing_text + '\n' + next_song_text



def queue_list_response(queue: list[MusicQueue.QueueItem]) -> str:
    next_in_queue_txt = "**Очередь:**"
    if len(queue) == 0:
        return "Очередь пуста!"
    list_txt = ""
    item_no = 0
    for item in queue:
        item_no += 1
        song_name = item.get_title()
        yt_link = item.get_yt_link()
        if list_txt != "":
            list_txt = list_txt + '\n' + \
                        f"* {item_no}. [{song_name}](<{yt_link}>)"
        else:
            list_txt = f"* {item_no}. [{song_name}](<{yt_link}>)"

    return next_in_queue_txt + "\n" + list_txt

def empty_queue_response():
    return "Нечего играть. Сначала добавьте песни в очередь при помощи `.add <url>` или воспроизведите песню с помощью `.play <url>`"



def song_added_response(song_name: str) -> str:
    return f"{song_name} успешно добавлена в очередь!"


def queue_cleared_response() -> str:
    return "Очередь успешно очещена!"