import praw
import pandas as pd
from datetime import datetime, timedelta
import json

from utils import keywords

if __name__ == "__main__":

    # Accessing the Reddit API
    with open('api_login.json') as f: 
        login = json.load(f)
    
    reddit = praw.Reddit(client_id = login["client_id"],          # your client id
                         client_secret = login["client_secret"],  # your client secret
                         user_agent = login["user_agent"],        # your user agent name
                         username = login["username"],            # your reddit username
                         password = login["password"])            # your reddit password

    sub = login["target"] #Target subreddit
    
    print("[",datetime.now(),"]:","Scraping r/"+sub,"for new posts...")
    
    subreddit = reddit.subreddit(sub)

    relevant_terms = pd.read_csv('Data/valid_coins.csv')['0'].to_list() # Get relevant coins

    current = pd.read_csv("Data/3d-posts.csv",index_col="Unnamed: 0") # Read in current data
    
    # Remove data that is 3 days old
    
    cutoff = (datetime.now()-timedelta(days=3)).timestamp()
    
    current = current.loc[current['created_utc']>cutoff]
    
    # Get new scrape
    out_dict = {"id":[],
               "author":[],
               "created_utc":[],
               "upvote_ratio":[],
               "title":[],
               "body":[],
               "title_keywords":[],
               "body_keywords":[]}

    for idx,post in enumerate(subreddit.new(limit=1000)):
        
        out_dict['id'].append(post.id)
        out_dict['author'].append(post.author)
        out_dict['created_utc'].append(post.created_utc)
        out_dict['upvote_ratio'].append(post.upvote_ratio)
        out_dict['title'].append(post.title)
        out_dict['body'].append(post.selftext)
        out_dict['title_keywords'].append("|".join(keywords(post.title,relevant_terms)))     
        out_dict['body_keywords'].append("|".join(keywords(post.selftext,relevant_terms)))
        
    # Check new scrape list against current list, reject duplicates
    test_array = pd.DataFrame(out_dict)
    test_array = test_array.loc[~test_array["id"].isin(current['id'].to_list())]
        
    msg = len(test_array)

    test_array = test_array.append(current)
        
    test_array.to_csv("Data/3d-posts.csv")
    
    print("[",datetime.now(),"]:","r/"+sub,"scraped for",msg,"new posts")
