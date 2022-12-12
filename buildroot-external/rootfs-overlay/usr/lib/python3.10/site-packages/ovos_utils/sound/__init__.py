import subprocess
import time
from ovos_utils.log import LOG
from ovos_utils.signal import check_for_signal
from distutils.spawn import find_executable


def play_audio(uri, play_cmd=None):
    """ Play a audio file.

        Returns: subprocess.Popen object
    """
    sox_play = find_executable("play")
    pulse_play = find_executable("paplay")
    alsa_play = find_executable("aplay")
    mpg123_play = find_executable("mpg123")

    player = play_cmd

    # NOTE: some urls like youtube streams will cause extension detection to fail
    # let's handle it explicitly
    ext = uri.split("?")[0].split(".")[-1]
    # Replace file:// uri's with normal paths
    uri = uri.replace('file://', '')

    # sox should handle almost every format, but fails in some urls
    if sox_play:
        player = sox_play + f" --type {ext} %1"
    # determine best available player
    else:
        # wav file
        if 'wav' in ext:
            if pulse_play:
                player = pulse_play + " %1"
            elif alsa_play:
                player = alsa_play + " %1"
        # guess mp3
        elif mpg123_play:
            player = mpg123_play + " %1"

    if not player:
        LOG.error(f"Failed to play: No playback functionality available")
        return None

    play_cmd = player.split(" ")

    for index, cmd in enumerate(play_cmd):
        if cmd == "%1":
            play_cmd[index] = uri

    try:
        return subprocess.Popen(play_cmd)
    except Exception as e:
        LOG.error(f"Failed to play: {play_cmd}")
        LOG.exception(e)
        return None


def play_wav(uri, play_cmd="paplay %1"):
    """ Play a wav-file.

        Returns: subprocess.Popen object
    """
    play_wav_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_wav_cmd):
        if cmd == "%1":
            play_wav_cmd[index] = uri
    try:
        return subprocess.Popen(play_wav_cmd)
    except Exception as e:
        LOG.error("Failed to launch WAV: {}".format(play_wav_cmd))
        LOG.debug("Error: {}".format(repr(e)), exc_info=True)
        return None


def play_mp3(uri, play_cmd="mpg123 %1"):
    """ Play a mp3-file.

        Returns: subprocess.Popen object
    """
    play_mp3_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_mp3_cmd):
        if cmd == "%1":
            play_mp3_cmd[index] = uri
    try:
        return subprocess.Popen(play_mp3_cmd)
    except Exception as e:
        LOG.error("Failed to launch MP3: {}".format(play_mp3_cmd))
        LOG.debug("Error: {}".format(repr(e)), exc_info=True)
        return None


def play_ogg(uri, play_cmd="ogg123 -q %1"):
    """ Play a ogg-file.

        Returns: subprocess.Popen object
    """
    play_ogg_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_ogg_cmd):
        if cmd == "%1":
            play_ogg_cmd[index] = uri
    try:
        return subprocess.Popen(play_ogg_cmd)
    except Exception as e:
        LOG.error("Failed to launch OGG: {}".format(play_ogg_cmd))
        LOG.debug("Error: {}".format(repr(e)), exc_info=True)
        return None


def record(file_path, duration, rate, channels):
    if duration > 0:
        return subprocess.Popen(
            ["arecord", "-r", str(rate), "-c", str(channels), "-d",
             str(duration), file_path])
    else:
        return subprocess.Popen(
            ["arecord", "-r", str(rate), "-c", str(channels), file_path])


def is_speaking():
    """Determine if Text to Speech is occurring

    Returns:
        bool: True while still speaking
    """
    return check_for_signal("isSpeaking", -1)


def wait_while_speaking():
    """Pause as long as Text to Speech is still happening

    Pause while Text to Speech is still happening.  This always pauses
    briefly to ensure that any preceeding request to speak has time to
    begin.
    """
    time.sleep(0.3)  # Wait briefly in for any queued speech to begin
    while is_speaking():
        time.sleep(0.1)