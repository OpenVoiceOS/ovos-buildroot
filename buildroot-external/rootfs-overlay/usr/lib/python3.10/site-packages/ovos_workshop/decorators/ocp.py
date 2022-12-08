from functools import wraps
from ovos_workshop.decorators.layers import IntentLayers
from ovos_plugin_common_play.ocp import *
from ovos_plugin_common_play.ocp.status import *


def ocp_search():
    """
    Decorator for adding a method as a common play search handler.
    Decorated methods should either yield or return a list of dict results:
    {
      "media_type": <MediaType>,
      "playback": <PlaybackType>,
      "image": <(optional) str image/cover art URI>,
      "skill_icon": <(optional) str skill icon URI>,
      "bg_image": <(optional) str background image URI>,
      "uri": <str media URI>,
      "title": <str media title>,
      "artist": <str media artist/author>,
      "length": <(optional) int media length in milliseconds>,
      "match_confidence": <int 0-100 confidence this result matches request>
    }
    """

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_search_handler'):
            func.is_ocp_search_handler = True

        return func

    return real_decorator


def ocp_play():
    """Decorator for adding a method as an common play search handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_playback_handler'):
            func.is_ocp_playback_handler = True

        return func

    return real_decorator


def ocp_previous():
    """Decorator for adding a method as an common play prev handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_prev_handler'):
            func.is_ocp_prev_handler = True

        return func

    return real_decorator


def ocp_next():
    """Decorator for adding a method as an common play  next handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_next_handler'):
            func.is_ocp_next_handler = True

        return func

    return real_decorator


def ocp_pause():
    """Decorator for adding a method as an common play pause handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_pause_handler'):
            func.is_ocp_pause_handler = True

        return func

    return real_decorator


def ocp_resume():
    """Decorator for adding a method as an common play resume handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_resume_handler'):
            func.is_ocp_resume_handler = True

        return func

    return real_decorator


def ocp_featured_media():
    """Decorator for adding a method as an common play search handler."""

    def real_decorator(func):
        # Store the flag inside the function
        # This will be used later to identify the method
        if not hasattr(func, 'is_ocp_featured_handler'):
            func.is_ocp_featured_handler = True

        return func

    return real_decorator
