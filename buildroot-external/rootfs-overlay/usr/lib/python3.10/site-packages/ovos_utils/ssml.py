import re


class SSMLBuilder:
    def __init__(self, ssml_tag=False, speak_tag=False):
        self.text = ""
        self.ssml_tags = ["speak", "ssml", "phoneme", "voice", "audio", "sub",
                          "prosody", "break", "whisper", "p", "s", "w",
                          "emphasis"]
        self.speak_tag = speak_tag
        self.ssml_tag = ssml_tag

    def sub(self, alias=None, word=None):
        if alias is None:
            raise TypeError('Parameter alias must not be None')
        if word is None:
            raise TypeError('Parameter word must not be None')
        if len(word.strip()) == 0:
            raise ValueError('Parameter word must not be empty')
        self.text += "<sub alias='" + alias + "'>" + word + "</sub> "
        return self

    def emphasis(self, level=None, word=None):
        if level is None:
            raise TypeError('Parameter level must not be None')
        if word is None:
            raise TypeError('Parameter word must not be None')
        if len(word.strip()) == 0:
            raise ValueError('Parameter word must not be empty')
        level = level.lower().strip()
        self.text += "<emphasis level='" + level + "'>" + word + "</emphasis> "
        return self

    def parts_of_speech(self, word=None, role=None):
        """Special considerations when speaking word include usage or role of word"""
        if word is None:
            raise TypeError('Parameter word must not be None')
        if role is None:
            raise TypeError('Parameter role must not be None')
        self.text += "<w role='" + role + "'>" + word + "</w> "
        return self

    def pause_by_strength(self, strength=None):
        if strength is None:
            raise TypeError('Parameter strength must not be None')
        try:
            strength = strength.lower().strip()
        except AttributeError:
            raise AttributeError('Parameter strength must be a string')

        self.text += "<break strength=" + strength + "/>"
        return self

    def sentence(self, text=None):
        """Wrap text with <s> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<s>" + text + "</s> "
        return self

    def say_emphasis(self, text=None):
        self.emphasis("strong", text)
        return self

    def say_strong(self, text=None):
        """Wrap text with <s> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<amazon:effect vocal-tract-length=\"+20%\">" + text\
                     + "</amazon:effect>"
        return self

    def say_weak(self, text=None):
        """Wrap text with <s> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<amazon:effect vocal-tract-length=\"-20%\">" + text\
                     + "</amazon:effect> "
        return self

    def say_softly(self, text=None):
        """Wrap text with <s> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<amazon:effect phonation=\"soft\">" + text + "</amazon:effect> "
        return self

    def say_auto_breaths(self, text=None):
        """Wrap text with <s> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<amazon:auto-breaths>" + text + "</amazon:auto-breaths>"
        return self

    def paragraph(self, text=None):
        """Wrap text with <p> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<p>" + text + "</p> "
        return self

    def audio(self, audio_file=None, text=None):
        if audio_file is None:
            raise TypeError('Parameter audio_file must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += '<audio src=' + audio_file + '>' + text + '</audio>'
        return self

    def pause(self, time=0, unit="ms"):
        if unit not in ["s", "ms"]:
            raise TypeError("time must be in seconds or miliseconds")
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        if time > 0:
            self.text += "<break time=" + str(time) + unit + "/>"
        else:
            self.text += "<break />"
        return self

    def prosody(self, attribute=None, text=None):
        if attribute is None:
            raise TypeError('Parameter attribute must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody " + attribute + ">" + text + "</prosody> "
        return self

    def pitch(self, pitch=None, text=None):
        if pitch is None:
            raise TypeError('Parameter pitch must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody pitch='" + str(
            pitch) + "'>" + text + "</prosody> "
        return self

    def volume(self, volume=None, text=None):
        if volume is None:
            raise TypeError('Parameter volume must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody volume='" + volume + "'>" + text + "</prosody> "
        return self

    def rate(self, rate=None, text=None):
        if rate is None:
            raise TypeError('Parameter rate must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody rate='" + str(rate) + "'>" + text + \
                     "</prosody>"
        return self

    def say(self, text=None):
        """Add normal speed text to SSML"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.rate("1", text)
        return self

    def say_loud(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.volume("1.6", text)
        return self

    def say_slow(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.rate("0.4", text)
        return self

    def say_fast(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.rate("1.6", text)
        return self

    def say_low_pitch(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.pitch("-10%", text)
        return self

    def say_high_pitch(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        self.pitch("+10%", text)
        return self

    def say_whispered(self, text=None):
        self.whisper(text)
        return self

    def phoneme(self, ph=None, text=None):
        if ph is None:
            raise TypeError('Parameter ph must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<phoneme ph=" + ph + ">" + text + "</phoneme> "
        return self

    def voice(self, voice=None, text=None):
        if voice is None:
            raise TypeError('Parameter voice must not be None')
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<voice name=" + voice + ">" + text + "</voice> "
        return self

    def whisper(self, text=None):
        if text is None:
            raise TypeError('Parameter text must not be None')
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<whispered>" + text + "</whispered> "
        return self

    def build(self):
        self.text = self.text.strip()
        if self.speak_tag:
            self.text = "<speak>\n" + self.text + "\n</speak>"
        if self.ssml_tag:
            self.text = "<ssml>\n" + self.text + "\n</ssml>"
        return self.text

    @staticmethod
    def remove_ssml(text):
        return re.sub('<[^>]*>', '', text).replace('  ', ' ')

    @staticmethod
    def extract_ssml_tags(text):
        # find ssml tags in string
        return re.findall('<[^>]*>', text)
