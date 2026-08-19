class PublisherError(Exception):
    """Expected, user-facing publishing error."""


class ContentError(PublisherError):
    pass


class WordPressError(PublisherError):
    pass
