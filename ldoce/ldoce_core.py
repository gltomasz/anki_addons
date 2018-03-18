import json
#import urllib
#import urllib.request
#import urllib2
import urllib
from urllib.request import urlopen
import logging
from aqt.utils import showInfo

results = []
dictionary = 'ldoce5'
baseurl = 'http://api.pearson.com/'
audioExaUrl = 'https://ldoceonline.com/media/english/exaProns/'
audioDefUrl = 'https://ldoceonline.com/media/english/ameProns/'

def find_word_in_dictionary(word):
    global results
    url = baseurl + 'v2/dictionaries/' + dictionary + '/entries?headword=' + word
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    content = json.load(urllib.request.urlopen(request))
    results = []
    for result in content['results']:
        #if result['headword'] == word:
        results.append(result)

    if len(results) == 0:
        showInfo("Word wasn't found in the LDOCE dictionary")
        return False
    # try:
    #     id = next(x['id'] for x in result if x['headword'] == word)
    # except StopIteration as e:
    #     #showInfo("Word wasn't found in the LDOCE dictionary")
    #     return False
    # # url = baseurl + 'v2/dictionaries/' + '/entries/' + id
    # # request = urllib2.Request(url, headers={"Accept": "application/json"})
    # # content = json.load(urllib2.urlopen(request))['result']
    return True


def get_headword(result):
    return result['headword']


def get_part_of_speech(result):
    if 'part_of_speech' not in result:
        return None
    return result['part_of_speech']


def get_word_url(result):
    return result['url']


def get_words():
    words = []
    for result in results:
        word = Word()
        word.pronunciation = get_pronunciation(result)
        word.headword = get_headword(result)
        word.part_of_speech = get_part_of_speech(result)
        word.url = get_word_url(result)
        if result['senses'] is None: continue
        for sense in result['senses']:
            sense_object = Sense()
            word.senses.append(sense_object)
            if 'definition' in sense:
                for definition in sense['definition']:
                    sense_object.add_definition(Definition(definition))
            if 'examples' in sense:
                for example in sense['examples']:
                    example_object = Example(example['text'])
                    if 'audio' in example:
                        example_object.audio = get_audio_from_example(example)
                    sense_object.add_example(example_object)
            if 'collocation_examples' in sense:
                for col_example in sense['collocation_examples']:
                    example = col_example['example']
                    text = '' if 'text' not in example else example['text']
                    example_object = CollocationExample(text, col_example['collocation'])
                    if 'audio' in example:
                        example_object.audio = get_audio_from_example(example)
                    sense_object.add_example(example_object)
            if 'gramatical_examples' in sense:
                for gr_example in sense['gramatical_examples']:
                    for example in gr_example['examples']:
                        text = '' if 'text' not in example else example['text']
                        pattern = '' if 'pattern' not in gr_example else gr_example['pattern']
                        example_object = GrammaticalExample(text, pattern)
                        if 'audio' in example:
                            example_object.audio = get_audio_from_example(example)
                        sense_object.add_example(example_object)
        words.append(word)
    return words


def get_audio_from_example(example):
    url = audioExaUrl + get_file_from_url(example['audio'][0]['url'])
    audio = Audio(url)
    audio.type = example['audio'][0]['type']
    return audio


def get_pronunciation(content):
    if 'pronunciations' not in content:
        return None
    ipa = content['pronunciations'][0]['ipa']
    url = audioDefUrl + get_file_from_url(content['pronunciations'][-1]['audio'][-1]['url'])
    audio = Audio(url)
    audio.type = 'pronunciation'
    return Pronunciation(ipa, audio)


def get_file_from_url(url):
    return url.split("/")[-1]


class Word(object):
    def __init__(self):
        self.headword = ''
        self.part_of_speech = ''
        self.url = ''
        self.pronunciation = None
        self.senses = []

    def add_sense(self, sense):
        self.senses.append(sense)


class Sense(object):
    def __init__(self):
        self.examples = []
        self.definitions = []

    def add_example(self, example):
        self.examples.append(example)

    def add_definition(self, definition):
        self.definitions.append(definition)


class Definition(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Example(object):
    def __init__(self, text):
        self.text = text
        self.audio = None

    def __str__(self):
        return ('%s %s' % (self.text, self.audio.get_anki_sound())) #.encode('utf-8')


class CollocationExample(Example):
    def __init__(self, text, collocation):
        Example.__init__(self, text)
        self.collocation = collocation

    def __str__(self):
        return ('%s %s <br><i>collocations: %s</i>' % (self.text, self.audio.get_anki_sound(), self.collocation)) #.encode('utf-8')


class GrammaticalExample(Example):
    def __init__(self, text, pattern):
        Example.__init__(self, text)
        self.pattern = pattern

    def __str__(self):
        return ('%s %s <br><i>pattern: %s</i>' % (self.text, self.audio.get_anki_sound(), self.pattern)) #.encode('utf-8')


class Pronunciation(object):
    def __init__(self, ipa, audio):
        self.ipa = ipa
        self.audio = audio

    def __str__(self):
        return 'ipa: %s audio: %s' % (self.ipa,self.audio)


class Audio(object):
    def __init__(self, file_url):
        self.file_url = file_url
        self.file_name = self.get_audio_file_name()
        self.type = ''

    def __str__(self):
        return 'url: ' + self.file_url + ' file_name: ' + self.file_name

    def get_audio_file_name(self):
        return self.file_url.split('/')[-1:][0]

    def get_anki_sound(self):
        return '[sound:' + self.file_name + ']'

    def save(self):
        testfile = urllib.URLopener()
        urllib.request.urlretrieve(self.file_url, self.file_name)


def debug():
    logging.basicConfig(level=logging.INFO)
    find_word_in_dictionary('compress')

    words = get_words()

    for word in words:
        logging.info('%s %s %s %s', word.headword, word.pronunciation, word.part_of_speech, word.url)
        for sense in word.senses:
            logging.info('sense:')
            for definition in sense.definitions:
                logging.info(' |-- def: %s', str(definition))
            for example in sense.examples:
                logging.info(' |-- sen: %s', str(example))


#debug()
