from .ldoce_core import *
# import the main window object (mw) from aqt
from aqt import mw
from aqt.utils import tooltip, getOnlyText, showInfo, chooseList, downArrow
import aqt
from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import wrap, addHook
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def find_word_by_definition(words, definition):
    for word in words:
        for sense in word.senses:
            for definit in sense.definitions:
                if definit == definition:
                    return word


def find_examples_by_definition(words, definition):
    for word in words:
        for sense in word.senses:
            for definit in sense.definitions:
                if definit == definition:
                    return sense.examples


def get_definition(editor, word_name):
    editor.loadNote()
    editor.web.setFocus()
    editor.web.eval("focusField(0);")
    editor.web.eval("caretToEnd();")
    editor_fields = editor.note.fields

    if not find_word_in_dictionary(word_name):
        return

    words_to_choose_from_as_strings = []
    definitions = []
    words = get_words()
    for word in words:
        for sense in word.senses:
            for definition in sense.definitions:
                words_to_choose_from_as_strings.append('%s | %s | %s' % (word.headword, word.part_of_speech, definition))
                definitions.append(definition)
    chosen_index = chooseList('Choose definition', words_to_choose_from_as_strings)

    word = find_word_by_definition(words, definitions[chosen_index])
    examples = find_examples_by_definition(words, definitions[chosen_index])

    # set sentences
    editor_fields[0] = ''
    for example in examples:
        editor_fields[0] += str(example) + "<br>\n"
    # set definition
    audio = word.pronunciation.audio.get_anki_sound() if word.pronunciation is not None else ''
    ipa = '\\%s\\' % word.pronunciation.ipa if word.pronunciation is not None else ''
    editor_fields[1] = '%s, <i>%s</i>, %s %s <br>\n' % (word.headword, word.part_of_speech, ipa, audio)
    editor_fields[1] += definitions[chosen_index].text

    refresh_fields(editor)

    # download media
    if word.pronunciation is not None:
        urllib.request.urlretrieve(word.pronunciation.audio.file_url, word.pronunciation.audio.file_name)
        #editor.urlToLink(word.pronunciation.audio.file_url)
    for example in examples:
        urllib.request.urlretrieve(example.audio.file_url, example.audio.file_name)
        #editor.urlToLink(example.audio.file_url)


def refresh_fields(editor):
    editor.loadNote()
    editor.web.eval("focusField(0);")
    editor.web.eval("focusField(1);")
    editor.web.eval("focusField(0);")


def button_pressed(self):
    text = getOnlyText('Word definition')
    get_definition(self, text)


def mySetupButtons(buttons, self):
    self._addButton("AutoDefine", lambda s=self: button_pressed(self),
                    text="D" + downArrow(), tip="AutoDefine Word (Ctrl+E)", key="Ctrl+e")


def addMyButton(buttons, editor):
    editor._links['strike'] = button_pressed
    return buttons + [editor._addButton(
        "iconname", # "/full/path/to/icon.png",
        "strike", # link name
        "tooltip")]

addHook("setupEditorButtons", addMyButton)
