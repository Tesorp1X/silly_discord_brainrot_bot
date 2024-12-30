class QueueItem:
    def __init__(self, video_title: str, video_yt_link: str, video_url: str):
        self.__item_tuple = (video_title, video_yt_link, video_url)

    def get(self):
        return self.__item_tuple

    def get_title(self):
        return self.__item_tuple[0]

    def get_yt_link(self):
        return self.__item_tuple[1]

    def get_video_url(self):
        return self.__item_tuple[2]


class MusicQueue:
    def __init__(self):
        self.__queue = {}

    def add_item(self, guild_id, video_title: str, video_yt_link: str, video_url: str):
        try:
            item = QueueItem(video_title, video_yt_link, video_url)
        except Exception as e:
            return "Type error: Cannot add item."
        if guild_id in self.__queue:
            self.__queue[guild_id].append(item)
            return len(self.__queue[guild_id]) + 1

        self.__queue[guild_id] = []
        self.__queue[guild_id].append(item)
        return len(self.__queue[guild_id]) + 1

    def get(self, guild_id):
        if guild_id in self.__queue:
            return self.__queue[guild_id]
        return "Error: No queue for given guild_id: " + guild_id

    def pop(self, guild_id, index=0):
        if guild_id in self.__queue:
            queue: list = self.get(guild_id)
            if type(queue) == list:
                item = queue.pop(index)
                print(queue)
                return item

            return "Error: No queue for given guild_id: " + guild_id

    def length(self, guild_id) -> int:
        if guild_id in self.__queue:
            return len(self.__queue[guild_id])
        return -1