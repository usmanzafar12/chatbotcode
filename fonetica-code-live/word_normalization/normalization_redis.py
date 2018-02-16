
# coding: utf-8

# In[1]:


### WORD NORMALIZATION CODE STARTS HERE ###
def eng_word_candidates(word):
    """Take input word, return list of most likely words using Language Model."""
#     print 'start fetching wordlist'
    import operator
#     import redis
    
#     r = redis.Redis(host='localhost', port=6379, db=0)

    r = load_redis()
    scores = r.hgetall(word)
    sorted_names = sorted(scores.items(), key=lambda x: int(x[1]), reverse=True)
    res_list = []
    
    for word in sorted_names:
        res_list.append(word[0])
#     print 'end fetching wordlist'
    return res_list


# In[2]:


def load_redis():
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r


# In[3]:


def dmeta_wordlist(word):
    """Load double metaphones dictionary from Redis."""
    from metaphone import doublemetaphone
    code = doublemetaphone(word)
#     r = redis.Redis(host='localhost', port=6379, db=0)
    r = load_redis()
    dmeta = r.hmget('dmeta',code)

    try:
        wordlist = dmeta[0].split(",")
    except AttributeError:
        wordlist = []

    return wordlist


# In[4]:


def eng_word_correction(text):
    """Detect and correct error words with enchant library and trained LM."""
    import enchant
    d = enchant.Dict("en_US")   # create dictionary for US English
#     language_model = load_lm('bigrams.pkl')
    text = "<s> " + text + " </s>"
    text = text.split()

    for n, m in enumerate(text):
        if m != "<s>" and m != "</s>":
            if not d.check(m):
#                 print "\nError word is:"
#                 print m
                lm_wordlist = eng_word_candidates(text[n-1])
#   #              lm_wordlist = eng_word_candidates(text[n-1], language_model)
#                 print "\nLanguage Model Suggested list for the word %s:" %text[n-1]
#                 print lm_wordlist
                med_words = d.suggest(m)
                dmeta_words = dmeta_wordlist(m)
#                 print "\nSuggested list by Enchant Library:"
#                 print med_words
#                 print "\nSuggested list by Double Metaphone:"
#                 print dmeta_words
# #                match = set(lm_wordlist) & set(med_words)
                match = []
                for word in lm_wordlist:
                    if word in med_words:
                        match.append(word)
                match2 = set(match) & set(dmeta_words)
#                 print "\nFirst LIST OF MATCHED WORDS"
#                 print match
#                 print "\nSecond List of Matched words: "
#                 print match2
                try:
                    text[n] = list(match2)[0]
                except IndexError:
                    try:
                        text[n] = list(match)[0]
                    except IndexError:
                        try:
                            match3 = set(med_words) & set(dmeta_words)
                            text[n] = list(match3)[0]
                        except IndexError:
                            try:
                                text[n] = med_words[0]
                            except IndexError:
                                text[n] = m
#                 print "\nReplaced word: ", text[n]
    text = text[1:-1]
    text = " ".join(text)
    return text


# In[6]:


if __name__ == "__main__":
    text = "I hav lst my crdt crd"
    print "Input sentence: ", text
    text = eng_word_correction(text)
    print "Output sentence: ", text

