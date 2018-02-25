import time
from datetime import timedelta, datetime
from nltk import word_tokenize
import pandas as pd
import re

def get_timestamp(timestamp):
    msg_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))
    msg_time = datetime.strptime(msg_time, "%Y-%m-%d %H:%M:%S")
    return msg_time

def load_dictionary():
    df = pd.read_csv("standard.csv", sep=',')
    dictionary = dict(zip(df.iloc[:,0], df.iloc[:,1]))
    return dictionary

def normalize(string, dictionary):
    informal_sent = word_tokenize(string)
    informal_list = set(dictionary.keys())
    temp = []
    for word in informal_sent:
        if word in informal_list:
            temp.append(dictionary[word])
        else:
            temp.append(word)
    return ' '.join(temp)


def ner(text):
    """To extract named entities and replace them with placeholders
    in given input text, and .txt flat file containing standard entities."""

    entities = ['hbl', 'creditcard', 'debitcard', 'atm']
    text = text.lower()
    words = text.replace(" ", "")
    entity = []

    for word in entities:
        out = re.search(word, words)
        if out:
            start_index = out.span()[0]
            end_index = out.span()[1]
            entity.append(words[start_index:end_index])

    if entity:
        for word in entity:
            replacement = "{0/}"
            words = words.replace(word, replacement)

    wordlist = text.split()
    word = []
    result, remainder = maxmatch(words, wordlist, word)

    output = " ".join(result)
    for n, ent in enumerate(entity):
        index = re.search("{.[0-9]./.}", output)
        output = output[: index.span()[0]] + output[index.span()[0]: \
                index.span()[1]].replace(" ", "") + output[index.span()[1]:]
    return output

def maxmatch(sentence, wordlist, words):
    """Algorithm to tokenize words from unstructured sentence."""

    if sentence == []:
        print("Nothing to parse")
        return []
    else:
        for n, letter in enumerate(sentence):
            if sentence in wordlist:
                words.append(sentence)
                remainder = ""
                return words, maxmatch(remainder, wordlist, words)
            index = -n - 1
            firstword = sentence[0:index]
            remainder = sentence[index:]
            if firstword in wordlist:
                words.append(firstword)
                return words, maxmatch(remainder, wordlist, words)

        if not sentence:
            return []
        firstword = sentence[0]
        remainder = sentence[1:]
        words.append(firstword)
        return words, maxmatch(remainder, wordlist, words)
