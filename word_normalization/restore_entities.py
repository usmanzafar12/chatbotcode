"""Restore extracted entities into their respective places."""


def restore_entities(entities, text):
    """Take extracted entities and translated text as input."""
    """Replace place holders with actual entities."""
    import distance
    import re
    for n, ent in enumerate(entities):
        match_index = re.search("\{[A-Za-z]*\s*[A-Za-z]*\}", text)

        try:
            # print match_index.span()
            entity_matched = text[match_index.span()[0]: match_index.span()[1]]
            replacement = sorted(distance.ilevenshtein(entity_matched, entities, max_dist=100))
            replacement = list(replacement[0])[1]
            text = text[: match_index.span()[0]] + replacement + text[match_index.span()[1]:]
        except AttributeError:
            pass
    return text


if __name__ == "__main__":
    text = "mera {hbl} ka {creditcard} gum gya hai"
    print "input is:\n"
    print text
    entities = ['hbl', 'creditcard']
    print "entities are:\n"
    print entities
    sentence = restore_entities(entities, text)
    print "Output Sentence:\n", sentence
