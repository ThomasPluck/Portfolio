import praw
import json
import pandas as pd
from time import sleep
from utils import keywords
from datetime import datetime, timedelta
from tqdm import tqdm

if __name__ == "__main__":

    # Accessing the Reddit API
    with open('api_login.json') as f: 
        login = json.load(f)
    
    reddit = praw.Reddit(client_id = login["client_id"],          # your client id
                         client_secret = login["client_secret"],  # your client secret
                         user_agent = login["user_agent"],        # your user agent name
                         username = login["username"],            # your reddit username
                         password = login["password"])            # your reddit password
    
    post_list = pd.read_csv("Data/3d-posts.csv")["id"].to_list()
    
    sub = login["target"] #Target subreddit
    
    print("[",datetime.now(),"]:","Scraping r/"+sub,"for new comments...")
    
    subreddit = reddit.subreddit(sub)
    
    relevant_terms = pd.read_csv('Data/valid_coins.csv')['0'].to_list() # Get relevant coins

    current = pd.read_csv("Data/3d-comments.csv",index_col="Unnamed: 0") # Read in current data
    
    # Remove data that is 3 days old
    
    cutoff = (datetime.now()-timedelta(days=3)).timestamp()
    
    current = current.loc[current['created_utc']>cutoff]

    
    # Get new scrape
    out_dict = {"link_id":[],
                "id":[],
                "parent_id":[],
               "author":[],
               "created_utc":[],
               "upvotes":[],
               "title":[],
               "body":[],
               "keywords":[]}

    for p in tqdm(post_list):
        
        submission = reddit.submission(p)
        
        while True:
            try:
                submission.comments.replace_more(limit=None)
                break
            except Exception as e:
                print(e,"Handling replace_more exception")
                sleep(1)
                
        for c in submission.comments.list():
            out_dict["link_id"].append(c.link_id)
            out_dict["id"].append(c.id)
            out_dict["parent_id"].append(c.parent_id)
            out_dict["author"].append(c.author)
            out_dict["created_utc"].append(c.created_utc)
            out_dict["upvotes"].append(c.score)
            out_dict["body"].append(c.body)
            out_dict["keywords"].append("|".join(keywords(c.body,relevant_terms)))
            
    # Check new scrape list against current list, reject duplicates
    test_array = pd.DataFrame(out_dict)
    test_array = test_array.loc[~test_array["id"].isin(current['id'].to_list())]
        
    msg = len(test_array)

    test_array = test_array.append(current)
        
    test_array.to_csv("Data/3d-posts.csv")
    
    print("[",datetime.now(),"]:","r/"+sub,"scraped for",msg,"new comments")