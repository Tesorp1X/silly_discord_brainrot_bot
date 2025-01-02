import MusicQueue

def get_default_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'you\'ve got to say something'
    elif 'hello' in lowered or 'привет' in lowered:
        return 'ohayo!'

    return ("Команды бота: \n * `.play <url>` - воспроизвести трек\n * `.add <url>` - добавить песню в очередь.\n" +
            "* `.pause` - поставить воспроизведение на паузу.\n* `.skip` - пропустить текущий трек.\n" +
            "* `.stop` - закончить прослушиваеие (очередь удалится).\n" +
            "* `.queue` - показать очередь")



def now_playing_response(song_title: str, yt_link: str, next_song_title="Nothing...") -> str:

    now_playing_text = f"**Сейчас играет: [{song_title}]({yt_link})**"
    next_song_text = f"**Следующая песня:** *{next_song_title}*"
    help_text = "* `.pause` - поставить воспроизведение на паузу.\n* `.skip` - пропустить текущий трек.\n" +\
                "* `.stop` - закончить прослушиваеие (очередь удалится).\n* `.add <url>` - добавить песню в очередь.\n"
    return now_playing_text + '\n' + next_song_text + '\n' + help_text



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

    return next_in_queue_txt + "\n" + list_txt + "\n" + "* `.play_all` - чтобы воспрозвести все.\n"

def empty_queue_response():
    return "Нечего играть. Сначала добавьте песни в очередь при помощи `.add <url>` или воспроизведите песню с помощью `.play <url>`"



def song_added_response(song_name: str) -> str:
    return (f"{song_name} успешно добавлена в очередь!\n" +
            "* `.play_all` - чтобы воспрозвести все.\n" +
            "* `.add <url>` - чтобы добавить еще одну песню.\n * `.queue` - чтобы посмотреть что сейчас в очереди.")


def queue_cleared_response() -> str:
    return "Очередь успешно очещена!"

def help_response(command="None") -> str:
    if command == 'play':
        text = "`.play <url>` - воспроизвести трек."
    elif command == 'add':
        text = "`.add <url>` - добавить песню в очередь."
    elif command == 'play_all':
        text = "`.play_all` - воспроизвести все песни из очереди."
    elif command == 'pause':
        text = ".pause` - поставить воспроизведение на паузу."
    elif command == 'resume':
        text = "`.resume` - продолжить воиспроизведение."
    elif command == 'skip':
        text = "`.skip` - пропустить текущий трек."
    elif command == 'clear':
        text = "`.clear` - очистить очередь."
    elif command == 'stop':
        text = "`.stop` - закончить прослушиваеие (очередь удалится)."
    elif command == 'queue':
        text = "`.queue` - показать очередь."
    else:
        text = ("Команды бота: \n" +
                "* `.play <url>` - воспроизвести трек.\n" +
                "* `.add <url>` - добавить песню в очередь.\n" +
                "* `.play_all` - воспроизвести все песни из очереди.\n"
                "* `.pause` - поставить воспроизведение на паузу.\n" +
                "* `.resume` - продолжить воиспроизведение.\n"
                "* `.skip` - пропустить текущий трек.\n" +
                "* `.clear` - очистить очередь.\n" +
                "* `.stop` - закончить прослушиваеие (очередь удалится).\n" +
                "* `.queue` - показать очередь.\n")

    return text

def queue_ended() -> str:
    return "**Очередь окончена.**"

def play_error():
    return "Произошла ошибка. Возможно, видео невозможно вопроизвести в данном формате."