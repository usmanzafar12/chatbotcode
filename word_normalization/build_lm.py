"""The code contain various functions used to build word normalization process."""


def add_sent_marker(corp):
    """To add sentence markers to nltk corpora."""
    out = []
    for sent in corp:
        sent = ['<s>'] + sent + ['</s>']
        for word in sent:
            out.append(word)
    return out


def get_corpus():
    """To get nltk corpora."""
    from nltk.corpus import brown
    from nltk.corpus import reuters

    corpus = add_sent_marker(brown.sents())
    corpus = corpus + add_sent_marker(reuters.sents())
    corpus = add_sent_marker(corpus)
    return corpus


def add_domain_data(filename, corpus):
    """To add other data(from flatfile) to nltk corpora."""
    """This data has sentence markers already."""
    # with open("lm_corpus.txt", "r") as thefile:
    with open(filename, "r") as thefile:
        x = thefile.read().splitlines()
        corpus = corpus + x
    return corpus


def remove_punctuation(corpus):
    """To remove punctuation from corpus."""
    import re

    result = []
    print len(corpus)

    for n in corpus:
        n = n.encode('utf-8')
        x = re.sub('\.', '', n)
        x = re.sub('\?', '', x)
        x = re.sub('\#', '', x)
        x = re.sub('\!', '', x)
        x = re.sub("''", '', x)
        x = re.sub('""', '', x)
        if x != '':
            result.append(x)
    print len(result)
    return result


def build_lm(corpus):
    """Build and save language model(pickle & redis DB). Return language model."""
    from cpickle import pickle
    import nltk
    import redis
    language_model = nltk.ConditionalFreqDist(nltk.bigrams(corpus))

    f = open('language_model.pkl', 'w')
    pickle.dump(language_model, f)
    f.close()

    r = redis.Redis(host='localhost', port=6379, db=0)
    temp = language_model.keys()
    for value in temp:
        values = dict(language_model[value].most_common())
        for dummy in values.iteritems():
            temp2 = {dummy[0]: int(dummy[1])}
            r.hmset(value, temp2)

    return language_model


def create_data(filename, corpus):
    """To create and save data by User Input."""
    """Takes target filename and corpus as input."""
    x = ""
    while x != "quit":
        x = raw_input("Enter Sentence:\n")
        if x != "quit":
            x = '<s> ' + x
            x = x + ' </s>'
            y = x.split()
            corpus = corpus + y

#    with open("lm_corpus.txt", "w") as thefile:
    with open(filename, "w") as thefile:
        for n in corpus[-93:]:
            thefile.write("%s\n" % n)
    thefile.close()

    return corpus


corpus = get_corpus()
corpus = add_domain_data(corpus)
corpus = remove_punctuation(corpus)
language_model = build_lm(corpus)
