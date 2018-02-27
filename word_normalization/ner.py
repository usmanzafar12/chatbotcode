"""To extract named entities."""


def load_redis(db):
    """To load Redis db, argument 'db' is integer number of db."""
    import redis
    r = redis.Redis(host='localhost', port=6379, db=db)
    return r


def get_entities():
    """To get entities from Redis db."""
    r = load_redis(1)
    entities = r.lrange('all_entities', 0, -1)
    return entities


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


def extract_entities(text, entities):
    """To extract list of entities present in text."""
    import re

    text = text.lower()
    words = text.replace(" ", "")
    entity = []

    for word in entities:
        out = re.search(word, words)
        if out:
            start_index = out.span()[0]
            end_index = out.span()[1]
            entity.append(words[start_index: end_index])
    return entity, words


def convert_entities(text, words, entities):
    """To replace entities with placeholders. To wrap them in curly brackets."""
    import re

    if entities:
        for word in entities:
            replacement = "{" + word + "}"
            words = words.replace(word, replacement)

    text = text.lower()
    wordlist = text.split()
    word = []
    result, remainder = maxmatch(words, wordlist, word)
    output = " ".join(result)
    for n, ent in enumerate(entities):
        index = re.search("\{\s[a-z]*\s*[a-z]*\s\}", output)
        output = output[: index.span()[0]] + output[index.span()[0]: index.span()[1]].replace(" ", "") + output[index.span()[1] :]
    return output


def ner(text):
    """To extract entities from text. With reference to provided Entity Dictionary."""
    entity_list = get_entities()
    entities, words = extract_entities(text, entity_list)
    output = convert_entities(text, words, entities)
    return entities, output

if __name__ == "__main__":
    text = raw_input("\nEnter sentence in Roman Urdu here:\n")
    named_entity, sentence = ner(text)
    print "Extracted entities:\n", named_entity
    print "Output Sentence:\n", sentence
