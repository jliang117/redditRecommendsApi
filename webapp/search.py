import sys
import json
import re

# external
import praw
from serpapi import GoogleSearch
import pandas as pd
from loguru import logger

from multiprocessing import Pool as CPUThreadPool
from multiprocessing.dummy import Pool as IOThreadPool
import time

# local
import spacyner

GOOGLE_PAGE_LIMIT = 1
GOOGLE_THREAD_LINK_LIMIT = 5
REPLACE_MORE_LIMIT= 3
SEARCH_REDDIT = ' site:reddit.com'

# TODO REMOVE ON COMMIT - also find a more automatic solution
CLIENT_ID = 'TGx9s4azwjK2wQ'
CLIENT_SECRET = 'C39wISck0di0SdxYBQLbqeFTwCo'
USER_AGENT = 'script:redditRecommends:v0.0.1'
SERP_API_KEY = '0bc291ac1aea924d662e8b406ab2daac5cb9f2f5f45367ef93a99cbb574dc2d3'


# global vars for csv column names
AUTHOR = 'author'
BODY = 'body'
CREATED = 'created_utc'
PERMALINK = 'permalink'
SUBREDDIT = 'subreddit'
SCORE = 'score'

# match on reddit links only
LINK_REGEX = 'https:\/\/www\.reddit\.(com)\/(.?)\/(.*)\/comments'


def initRedditClient():
    logger.add("log/file_{time}.log", level="TRACE", rotation="100 MB")
    return praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)


def createIOThreadPool(num=None):
    return IOThreadPool(processes=num)


def createCPUThreadPool(num=None):
    return CPUThreadPool(processes=num)


def getGoogleResultsFromSearch(searchString, googlePageLimit=GOOGLE_PAGE_LIMIT):
    search = GoogleSearch({
        "q": f"${searchString} site:www.reddit.com",
        "api_key": SERP_API_KEY
    })
    result = search.get_dict()
    links = list(map(lambda result: result["link"], result["organic_results"]))
    return links


def convertSearchResultsToDataframe(googleResults):
    googleResults = [result for result in googleResults if isResultValidLink(result)]
    logger.info(googleResults)
    commentsFromResult = []
    commentsFromResult = resultsToCommentListParallel(googleResults)
    logger.info(commentsFromResult)
    df = pd.DataFrame(data=commentsFromResult)

    return df


def isResultValidLink(result):
    if re.search(LINK_REGEX, result) is None:
        logger.warning(f'bad link averted:{result}')
        return False
    return True


def resultsToCommentListParallel(googleResults):
    results = []
    reddit = initRedditClient()
    pool = createIOThreadPool()
    pool.starmap_async(convertResultToCommentList, [(result, reddit) for result in googleResults],callback=lambda r:results.extend(r))
    pool.close()
    pool.join()
    # somehow starmapping returns a list of a list of comments for each result
    return [commentRow for listOfComments in results for commentRow in listOfComments]


def convertResultToCommentList(result, reddit):
    resultData = []
    try:
        submission = reddit.submission(url=result)
        submission.comments.replace_more(REPLACE_MORE_LIMIT)
        for comment in submission.comments.list():
            if(filterCommentForRelevancy(comment)):
                resultData.extend(buildRowFromComment(comment))
    except praw.exceptions.ClientException:
        logger.warn("Google search returned non submission:" + result)
    return resultData


def buildRowFromComment(comment):
    redditName = checkCommentAuthor(comment)
    subredditName = comment.subreddit.display_name
    builtRow = [{
        AUTHOR: redditName,
        BODY: comment.body,
        CREATED: comment.created_utc,
        SCORE: comment.score,
        PERMALINK: comment.permalink,
        SUBREDDIT: subredditName}]
    return builtRow


def checkCommentAuthor(comment):
    return comment.author.name if comment.author is not None else ''




def filterCommentForRelevancy(comment):
    return len(comment.body) > 3
    # potentially do preprocessing here as well


def sanitize(value):

    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    """
    import re
    re.sub('[^\w\-_\. ]', '_', value)
    value = value.replace(" ", "_")
    logger.debug(f'Saving file with sanitized name: {value}')
    return value


def searchAndExtract(argv):
    logger.info(f'Search string: {argv}')

    t = time.time()
    googleResults = getGoogleResultsFromSearch(argv + SEARCH_REDDIT)
    logger.info(googleResults)
    logger.info(f'get Google Results took {time.time()-t} seconds')
    df = convertSearchResultsToDataframe(googleResults)
    logger.info(df.head())
    logger.info(f'convert Results to Dataframe took {time.time()-t} seconds')
    spacyner.createExtractedColumn(df)
    logger.info(f'Extracting results took {time.time()-t} seconds')
    json = df.to_json()
    logger.info(f'total time took {time.time()-t} seconds')
    return json
