
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





# In[6]:


if __name__ == "__main__":
    text = "I hav lst my crdt crd"
    print "Input sentence: ", text
    text = eng_word_correction(text)
    print "Output sentence: ", text
