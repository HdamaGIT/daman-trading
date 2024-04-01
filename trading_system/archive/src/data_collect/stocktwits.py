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

