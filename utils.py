import datetime
import string
import unicodedata
import tqdm

from discord import AudioSource

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255
_base = datetime.datetime.strptime("00:00:00", '%H:%M:%S')


def unpack_HHMMSS(hhmmss: str):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(hhmmss.split(':'))))


def pack_HHMMSS(time: float):
    mon, sec = divmod(time, 60)
    hr, mon = divmod(mon, 60)
    return f'{int(hr):02d}:{int(mon):02d}:{int(sec):02d}'


class Termlesstqdm(tqdm.tqdm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self, s, file=None, end="\n", nolock=False):
        pass

    @staticmethod
    def status_printer(file):
        def print_status(s):
            pass

        return print_status

    def update(self, n=1):
        raise Exception("No dont.")


class SourcePlaybackCounter(AudioSource):
    def __init__(self, source, duration: float, frames_read=0):
        self._source = source
        self.frames_read = frames_read
        self.duration = duration
        self.tqdm = Termlesstqdm(total=self.duration, ncols=40, nrows=40,
                                 bar_format="{percentage:3.0f}% |{bar}|",
                                 ascii=" #")

    def is_opus(self):
        return self._source.is_opus

    def get_bar(self):
        return str(self.tqdm)

    def read(self):
        res = self._source.read()
        if res:
            self.frames_read += 1
        return res

    def get_progress(self):
        self.tqdm.n = self.frames_read * 0.02
        return self.frames_read * 0.02

    def cleanup(self):
        self.tqdm.close()
        self._source.cleanup()


def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print(
            "Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]
