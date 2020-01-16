# redditRecommends
aggregating reddit comments and using NLP to sift through various recommendations

## Idea and feature set:

I frequently find myself googling "best \<insert item type, restaurant, thing to do here\> reddit" and so to expedite that, something to aggregate google results of reddit comments and do some data extraction to return top results would be useful.

So, when I'm using reddit to search for testimonials or recommendations on a topic, I want to know what reddit thinks - how will I ask it questions (as in what forms/categories of questions are possible)?

Given the prompt - `What does reddit think about ___`? A few very simple question structures come to mind:

`Food/Activity/Thing` **IN** `Place` ex. `Ramen in Nyc` - yields places, landmarks, restaurants

`Superlative` `Object` ex. `Best 4k TV` - yields objects, links, shopping sites

 *Lots more*

**Fetch data**

(using https://github.com/abenassi/Google-Search-API) and praw (https://github.com/praw-dev/praw)


**Normalization**

using nltk - https://github.com/nltk/nltk and implemented in `commentfilter.py`

Named Entity Recognition doesn't make use of much normalization, but other downstream tasks *might*

**Extraction**

using spaCy - https://github.com/explosion/spaCy and implemented in `spacyner.py`

Currently using the built in entity extraction, eventually I'd like to build upon this more to not only get the sent of entites but also an entire set of text analysis - something similar to:

Example sentence:

`Ippudo is overhyped in my book. My go to is Hide Chan, their East side location is the best imo`

Extracted data:
    
    {
    entities: ["Ippudo", "Hide-Chan", "East"],
    nounPhrases:[...],
    entitySentiment:[...],
    and probably more...
    }

I'm currently still unsure of what exactly would be useful...
    

# Usage

Add your reddit credentials to `search.py` as shown [here](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps)

    CLIENT_ID = 'your id'
    CLIENT_SECRET = 'Your secret'
    USER_AGENT = 'script:redditRecommends:v0.0.1 '
    

Build using [docker](https://www.docker.com/): `docker build -t searchReddit .`

Run using: `docker run -p 4000:8080 searchReddit`

A service is launched at port `4000`, which you can curl to: 

`curl -i -H "Content-Type: application/json" -X POST -d '{"search":"ramen nyc"}' http://localhost:4000/search`

(the run command maps port 8080 in the container to 4000 on your local machine, the port can be specified in dockerfile `ENV PORT 8080`

# Output

A jsonified dataframe to be parsed by the [front end](https://github.com/jliang117/redditRecommendsVue)

Demo: https://redrec.herokuapp.com (url to hopefully change soon...)

