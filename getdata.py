import oauth2 as oauth
import urllib2 as urllib
import sys
import simplejson as json
import csv
import time
from datetime import datetime

# See Assignment 1 instructions or README for how to get these credentials
access_token_key = ""
access_token_secret = ""

consumer_key = ""
consumer_secret = ""

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response

def fetchsamples():
    url = "https://api.twitter.com/1.1/users/search.json?page={0}&q={1}&count=20"
    parameters = [] 
    twitter_users = []
    current_day = datetime.utcnow()
    num_pages = 1
    if len(sys.argv) > 2:
        num_pages = int(sys.argv[2]) 

    for i in range(0,num_pages):
        print 'getting ' + str(i+1) + 'th set of twitter users'
        response = twitterreq(url.format(str(i+1),sys.argv[1]), "GET", parameters)
        for line in response:
            #print line.strip()
            js = json.loads(line)
            for user in js:
                account = []
                try:
                    account.append(user.get('screen_name').encode('utf-8')) # twitter handle
                    account.append(user.get('name').encode('utf-8'))        # full name
                    account.append((current_day - datetime.strptime(user.get('created_at'), '%a %b %d %H:%M:%S +0000 %Y')).days)  # age in days
                    account.append(user.get('statuses_count')) # number of tweets
                    account.append(0 if user.get('default_profile') else 1) # has a profile been specified
                    account.append(0 if user.get('default_profile_image') else 1) # has a profile pic been specified
                    account.append(user.get('friends_count'))  # number of twitter accounts this user is following
                    account.append(user.get('favourites_count')) # number of tweets this user has favorited
                    account.append(user.get('listed_count'))     # number of lists this user is in
                    account.append(user.get('followers_count')) #followers
                    twitter_users.append(account)
                except AttributeError:
                    print str(type(user))
                    print str(user)
                    print str(js)
                    

    
    with open('twitter_user_data.csv', 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(['handle','name','age','num_of_tweets','has_profile','has_pic','num_following',
            'num_of_favorites','num_of_lists','num_of_followers'])
        writer.writerows(twitter_users)


if __name__ == '__main__':
  fetchsamples()
