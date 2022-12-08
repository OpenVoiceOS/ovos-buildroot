import re
import operator
import stopwordsiso


class Rake:
    def __init__(self, lang="en", stop_words_path=None):
        if stop_words_path:
            self.__stop_words_pattern = self.build_stop_word_regex_from_file(
                stop_words_path)
        else:
            stoplist = stopwordsiso.stopwords(lang)
            if not stopwordsiso.has_lang(lang):
                lang2 = lang.split("-")[0].lower()
                if not stopwordsiso.has_lang(lang2):
                    raise ValueError("No bundled stopword list available for {lang}, "
                                     "initialize Rake with stop_words_path "
                                     "argument".format(lang=lang))
                stoplist = stopwordsiso.stopwords(lang2)

            self.__stop_words_pattern = self.build_stop_word_regex(stoplist)

    @staticmethod
    def generate_candidate_keyword_scores(phrase_list, word_score):
        keyword_candidates = {}
        for phrase in phrase_list:
            keyword_candidates.setdefault(phrase, 0)
            word_list = Rake.separate_words(phrase, 0)
            candidate_score = 0
            for word in word_list:
                candidate_score += word_score[word]
            keyword_candidates[phrase] = candidate_score
        return keyword_candidates

    @staticmethod
    def calculate_word_scores(phrase_list):
        word_frequency = {}
        word_degree = {}
        for phrase in phrase_list:
            word_list = Rake.separate_words(phrase, 0)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1
            # if word_list_degree > 3: word_list_degree = 3 #exp.
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                word_degree.setdefault(word, 0)
                word_degree[word] += word_list_degree  # orig.
                # word_degree[word] += 1/(word_list_length*1.0) #exp.
        for item in word_frequency:
            word_degree[item] = word_degree[item] + word_frequency[item]

        # Calculate Word scores = deg(w)/frew(w)
        word_score = {}
        for item in word_frequency:
            word_score.setdefault(item, 0)
            word_score[item] = word_degree[item] / (
                    word_frequency[item] * 1.0)  # orig.
        # word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
        return word_score

    @staticmethod
    def is_number(s):
        try:
            float(s) if '.' in s else int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def load_stop_words(stop_word_file):
        """
        Utility function to load stop words from a file and return as a list of words
        @param stop_word_file Path and file name of a file containing stop words.
        @return list A list of stop words.
        """
        stop_words = []
        for line in open(stop_word_file):
            if line.strip()[0:1] != "#":
                for word in line.split():  # in case more than one per line
                    stop_words.append(word)
        return stop_words

    @staticmethod
    def separate_words(text, min_word_return_size):
        """
        Utility function to return a list of all words that are have a length greater than a specified number of characters.
        @param text The text that must be split in to words.
        @param min_word_return_size The minimum no of characters a word must have to be included.
        """
        splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            # leave numbers in phrase, but don't count as words,
            # since they tend to invalidate scores of their phrases
            if len(current_word) > min_word_return_size and \
                    current_word != '' and \
                    not Rake.is_number(current_word):
                words.append(current_word)
        return words

    @staticmethod
    def split_sentences(text):
        """
        Utility function to return a list of sentences.
        @param text The text that must be split in to sentences.
        """
        sentence_delimiters = re.compile(
            u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences

    @staticmethod
    def build_stop_word_regex(stop_word_list):
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list),
                                       re.IGNORECASE)
        return stop_word_pattern

    @staticmethod
    def build_stop_word_regex_from_file(stop_word_file_path):
        stop_word_list = Rake.load_stop_words(stop_word_file_path)
        return Rake.build_stop_word_regex(stop_word_list)

    @staticmethod
    def generate_candidate_keywords(sentence_list, stopword_pattern):
        phrase_list = []
        for s in sentence_list:
            tmp = re.sub(stopword_pattern, '|', s.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "":
                    phrase_list.append(phrase)
        return phrase_list

    def extract_keywords(self, text):
        sentence_list = self.split_sentences(text)

        phrase_list = self.generate_candidate_keywords(
            sentence_list, self.__stop_words_pattern)

        word_scores = self.calculate_word_scores(phrase_list)

        keyword_candidates = self.generate_candidate_keyword_scores(
            phrase_list, word_scores)

        sorted_keywords = sorted(iter(keyword_candidates.items()),
                                 key=operator.itemgetter(1), reverse=True)
        return sorted_keywords
