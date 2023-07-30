import requests
import json
import nltk
from textblob import TextBlob


import requests

# Set the base URL for the API
base_url = "https://api.stocktwits.com/api/2/streams/symbol/"

# Set the symbol you want to get sentiment for
symbol = "AAPL"

# Make the API request
response = requests.get(base_url + symbol + ".json")

# Get the messages data from the response
messages = response.json()['messages']

# Iterate through the messages and print the sentiment of each
for message in messages:
    print("Sentiment:", message['entities']['sentiment']['basic'])















# def check_abnormal_activity(ticker):
#     # Set the base URL for the Stocktwits API
#     base_url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json".format(ticker)
#
#     # Set the parameters for the API call
#     params = {
#         "limit": 1000,
#         "sort": "volume"
#     }
#
#     # Make the API call
#     response = requests.get(base_url, params=params)
#
#     # Parse the JSON data
#     data = json.loads(response.text)
#
#     # Get the message volume
#     volume = len(data["messages"])
#
#     # Check if the volume is very high
#     if volume > 1000:
#         print("Ticker {} has high volume on Stocktwits".format(ticker))
#
#     # Initialize variable for overall sentiment
#     overall_sentiment = 0
#     for message in data['messages']:
#         # Get the sentiment
#         sentiment = TextBlob(message['body']).sentiment.polarity
#         overall_sentiment += sentiment
#
#         print(sentiment, message['body'])
#
#     overall_sentiment = overall_sentiment/volume
#
#     print(data)
#     print(volume)
#     print(overall_sentiment)
#
#     if overall_sentiment>0:
#         print("Ticker {} has overall bullish sentiment on Stocktwits".format(ticker))
#     elif overall_sentiment<0:
#         print("Ticker {} has overall bearish sentiment on Stocktwits".format(ticker))
#     else:
#         print("Ticker {} has overall neutral sentiment on Stocktwits".format(ticker))
#
#
# check_abnormal_activity('AAPL')