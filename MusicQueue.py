from numpy.matlib import empty

import BotExceptions

class QueueItem:
    """
    Is a tuple of three: (video_title, video_yt_link, video_url).

    """
    def __init__(self, video_title: str, video_yt_link: str, video_url: str):
        if video_title is None or video_title == "":
            raise BotExceptions.InvalidQueueItemAttributeException(attribute_name="video_title",
                                                                   value=video_title,
                                                                   expected_str="Expected str, but None or Empty str was given.")
        if video_yt_link is None or video_yt_link == "":
            raise BotExceptions.InvalidQueueItemAttributeException(attribute_name="video_yt_link",
                                                                   value=video_yt_link,
                                                                   expected_str="Expected str, but None or Empty str was given.")
        if video_url is None or video_url == "":
            raise BotExceptions.InvalidQueueItemAttributeException(attribute_name="video_url",
                                                                   value=video_url,
                                                                   expected_str="Expected str, but None or Empty str was given.")
        self.__item_tuple = (video_title, video_yt_link, video_url)

    def get(self):
        """

        :return: a tuple: (video_title, video_yt_link, video_url)
        """
        return self.__item_tuple

    def get_title(self):
        """

        :return: video_title
        """
        return self.__item_tuple[0]

    def get_yt_link(self):
        """

        :return: video_yt_link
        """
        return self.__item_tuple[1]

    def get_video_url(self):
        """

        :return: video_url
        """
        return self.__item_tuple[2]


class MusicQueue:
    """
    queue -- is a set of all queues, that bot has at the moment. Key is guild_id (server id)
    and value is a list of QueueItem's objects.
    list example: [QueueItem_obj_1, QueueItem_obj_2, ...]
    is_shuffled -- is a set of bool values for given guild_id, indicating is that queue shuffled or not.
    """
    def __init__(self):
        self.__queue = {}
        self.__is_shuffled = {}

    def add_item(self, guild_id, video_title: str, video_yt_link: str, video_url: str) -> int:

        item = QueueItem(video_title, video_yt_link, video_url)

        if guild_id in self.__queue:
            self.__queue[guild_id].append(item)
            return len(self.__queue[guild_id])

        self.__queue[guild_id] = []
        self.__queue[guild_id].append(item)
        self.__is_shuffled[guild_id] = False
        return len(self.__queue[guild_id])

    def get(self, guild_id) -> list[QueueItem]:
        if guild_id in self.__queue:
            return self.__queue[guild_id]
        raise BotExceptions.InvalidGuildIdException(guild_id)

    def pop(self, guild_id, index=0) -> QueueItem:
        if guild_id in self.__queue:
            queue: list = self.get(guild_id)
            if type(queue) == list:
                item = queue.pop(index)
                print(queue)
                return item

            raise BotExceptions.InvalidGuildIdException(guild_id)

    def length(self, guild_id) -> int:
        """
        Returns length of list with QueueItems. If there is no queue for given guild_id, then 0 is return
        :param guild_id: server id.
        :return: length of list with QueueItems.
        """
        if guild_id in self.__queue:
            return len(self.__queue[guild_id])
        return 0

    def is_empty(self, guild_id) -> bool:
        """
        If no value for given guild_id, then it means queue is empty.
        :param guild_id:
        :return: 'True' if queue is empty or doesn't exist, 'False' if not empty.
        """
        if guild_id in self.__queue:
            if len(self.__queue[guild_id]) > 0:
                return False
        return True

    def is_shuffled(self, guild_id) -> bool:
        if guild_id in self.__is_shuffled:
            return self.__is_shuffled[guild_id]
        raise BotExceptions.InvalidGuildIdException(guild_id)

    def shuffle_queue(self, guild_id) -> None:
        if guild_id in self.__is_shuffled:
            self.__is_shuffled[guild_id] = True
        raise BotExceptions.InvalidGuildIdException(guild_id)

    def deshuffle_queue(self, guild_id) -> None:
        if guild_id in self.__is_shuffled:
            self.__is_shuffled[guild_id] = False
        raise BotExceptions.InvalidGuildIdException(guild_id)

    def get_next_song_title(self, guild_id) -> str:
        if guild_id in self.__queue:
            if not self.is_shuffled(guild_id):
                if len(self.__queue[guild_id]) > 0:
                    return self.__queue[guild_id][0].get_title()
                return "Очередь закончилась"
            return "Очередь перемешана!"
        raise BotExceptions.InvalidGuildIdException(guild_id)

    def remove_queue(self, guild_id):
        if guild_id in self.__queue:
            self.__queue.pop(guild_id)
            self.__is_shuffled.pop(guild_id)
        raise BotExceptions.InvalidGuildIdException(guild_id)
