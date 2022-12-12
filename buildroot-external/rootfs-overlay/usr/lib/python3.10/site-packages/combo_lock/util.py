from memory_tempfile import MemoryTempfile
import os


def get_ram_directory(folder):
    tempfile = MemoryTempfile(fallback=True)
    path = os.path.join(tempfile.gettempdir(), folder)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

