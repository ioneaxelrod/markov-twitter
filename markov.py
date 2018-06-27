"""A Markov chain generator that can tweet random messages."""

import os
import sys
from random import choice
import twitter
import json
import re


def place_to_end(text_string):
    words = text_string.split()
    return (words[-3], words[-2])


def open_and_read_file(filenames):
    """Take list of files. Open them, read them, and return one long string."""

    body = ""

    for filename in filenames:
        text_file = open(filename)
        body = body + " " + text_file.read() 
        text_file.close()

    return body


def make_chains(text_string):
    """Take input text as string; return dictionary of Markov chains."""

    chains = {}

    words = text_string.split()

    for i in range(len(words) - 2):
        key = (words[i], words[i + 1])
        value = words[i + 2]

        chains.setdefault(key, []).append(value)

    return chains


def make_text(chains):
    """Take dictionary of Markov chains; return random text."""

    keys = list(chains.keys())
    key = choice(keys)
    words = [key[0], key[1]]
    while key in chains:
        # Keep looping until we have a key that isn't in the chains
        # (which would mean it was the end of our original text).
        #
        # Note that for long texts (like a full book), this might mean
        # it would run for a very long time.

        word = choice(chains[key])
        words.append(word)
        key = (key[1], word)

    new_tweet = " ".join(words)
    if len(new_tweet) < 280:
        return new_tweet

    return make_text(chains)


def tweet(filenames):
    """Create a tweet and send it to the Internet."""

    while True:
        chains = make_text(make_chains(open_and_read_file(filenames)))
        print(chains)
        print()
        print("Would you like to print this tweet? [y/n/q]")
        user_input = input("> ").lower()
        print()
        if user_input == 'q':
            break
        elif user_input == 'y':
            api = twitter.Api(
                consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                access_token_key=os.environ["TWITTER_ACCESS_TOKEN_KEY"],
                access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"])

            print(api.VerifyCredentials())

            new_tweet = api.PostUpdate(chains)
        else:
            continue


def get_tweets(search_criteria):
    api = twitter.Api(
                consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                access_token_key=os.environ["TWITTER_ACCESS_TOKEN_KEY"],
                access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
                tweet_mode="extended")

    search = api.GetUserTimeline(screen_name=search_criteria, count=100)
    print(search)
    tweets = [item.AsDict() for item in search]
    tweets = [re.sub(r'http\S+', '', tweet["full_text"]) for tweet in tweets]

    return tweets


def save_tweets_to_text_file(tweets):
    with open("tweets.txt", "a") as file:
        for tweet in tweets:
            file.write(tweet)


filenames = sys.argv[1:]

# Open the files and turn them into one long string
# Your task is to write a new function tweet, that will take chains as input
# tweet(filenames)
tweet(filenames)


