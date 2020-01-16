import pandas as pd
import spacy
import jellyfish as jf
from loguru import logger


NLP = None

# entity comparison
ENTITYSET = set()
JW_SCORE_THRESHOLD = float(.90)


def loadSpacy():
    global NLP
    if NLP is None:
        NLP = spacy.load('en')
        return NLP
    else:
        return NLP



def spacyTagging(sents):
    nlp = loadSpacy()
    doc = nlp(sents)
    return [ent.text for ent in doc.ents]
    # return consolidateEntities(doc.ents) 


def spacyValues(df):
    entityDf = pd.DataFrame()
    for index, row in df.iterrows():
        currDf = spacyTagging(row['body'])
        entityDf = entityDf.append(currDf)
    print(entityDf['Entity'].value_counts())


def spacyIdNounPhrases(sents):
    nlp = loadSpacy()
    doc = nlp(sents)
    return [chunk.text for chunk in doc.noun_chunks]


# break each comment into individual sentences
def tokenizeSentences(sents):
    import nltk
    return nltk.sent_tokenize(sents)


"""
simple fuzzy matching using jaro winker score
can be extended to use a combination of techniques, to using certain matchers based on search input

Useful for removing extraneous entites that clog up results:
    With a typical search being "<JJ>food <LOC>", we can detect <LOC> within the search, 
    store it and match on <LOC> entities that are similar and remove them

RETURNs a list of strings that
"""
def consolidateEntities(listOfEnts):
    logger.debug(f'Entities in set:{ENTITYSET}')
    logger.debug(f'Checking entities:{listOfEnts}')
    retList = []
    if all(isinstance(ele, str) for ele in listOfEnts) is not True:
        listOfEnts = [span.text for span in listOfEnts]

    for i in range(len(listOfEnts)):
        ent = listOfEnts[i]
        if ent not in ENTITYSET:
            for val in ENTITYSET:
                jaroWScore = jf.jaro_winkler(ent, val)
                if jaroWScore > JW_SCORE_THRESHOLD:
                    logger.info(f'Found match between ent:{ent}, and val:{val}')
                    ent = val
            # jaro = jf.jaro_distance(ent, val)
            # hammingD = jf.hamming_distance(ent, val)
            # dlD = jf.damerau_levenshtein_distance(ent, val)
            # logger.debug(f'COMPARING ent:{ent} and val:{val}')
            # logger.info(f'Jaro Winkler:{jaroWScore}')
            # logger.info(f'Jaro:{jaro}')
            # logger.info(f'hamming_distance:{hammingD}')
            # logger.info(f'damerau_levenshtein_distance:{dlD}')
        ENTITYSET.add(ent)
        retList.append(ent)
    return retList


def createExtractedColumn(df, consolidate=True):
    import time
    start = time.time()
    df['extracted'] = df['body'].apply(lambda text: spacyTagging(text))
    logger.info(f'apply took:{time.time() - start} seconds')
    startv = time.time()
