from nltk import word_tokenize

def keywords(string,words):
    
    keys_found = []
    
    for word in word_tokenize(string):
        if word.upper() in words:
            keys_found.append(word.upper())
            
    return keys_found