

class InvalidGuildIdException(Exception):
    """Exception raised for errors in handling queues. If provided guild_id
    is not to be found in queue, then this exception must be raised.
    Attributes:
        guild_id - that caused error
        message -- explanation of the error
    """
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.message = f"Invalid guild id: {guild_id} has no queue right now."
        super().__init__(self.message)

class InvalidQueueItemAttributeException(Exception):
    """Exception raised for errors in handling QueueItems attributes.
    If provided values are invalid, then this exception must be raised.
        Attributes:
            attribute_name -- in which error occurred
            value -- that caused error
            message -- explanation of the error
        """
    def __init__(self, attribute_name: str, value, expected_str: str):
        self.attribute_name = attribute_name
        self.value = value
        self.message = f"In attribute {self.attribute_name} given value {value} caused error: " + expected_str
        super().__init__(self.message)