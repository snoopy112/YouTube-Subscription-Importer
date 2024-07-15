import os
import sys
import csv
import httplib2

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the authenticated user's account
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is missing
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

# The name of the file used to store the already subscribed to chanell ids
STORED_CHANNEL_FILE_NAME = "channels_subscribed.txt"


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_READ_WRITE_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))


def get_channels_list():
    stored_file_txt = ""
    channel_ids = []

    if os.path.exists(STORED_CHANNEL_FILE_NAME):
        with open(STORED_CHANNEL_FILE_NAME, mode="r", encoding="utf-8") as ids_file:
            stored_file_txt = ids_file.read()

    # Parse the channel id's from the csv file
    with open(args.csv) as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if i == 0:
                continue  # skip header
            else:
                if line:
                    channel_id = line[0]
                    if channel_id not in stored_file_txt:
                        channel_ids.append(channel_id)
                    else:
                        print("Skip channel:", channel_id)

    return channel_ids


# This method calls the API's youtube.subscriptions.insert method to add a
# subscription to the specified channel
def add_subscription(youtube, channel_id):
    add_subscription_response = youtube.subscriptions().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                resourceId=dict(
                    kind="youtube#channel",  # Edited on 13/3/2020 as youtube api changes
                    channelId=channel_id
                )
            )
        )).execute()

    # When a subscription is added, add the channel id into a file
    # this file will be used to not subscribe to the same channel again
    with open(STORED_CHANNEL_FILE_NAME, mode="a+", encoding="utf-8") as ids_file:
        # Write info message for file if not already written
        if os.path.getsize(STORED_CHANNEL_FILE_NAME) == 0:
            ids_file.write(
                "This file is used to keep track of channels that have already been subscribed."
                "\nIf you would like to restart fresh or on a new account. Delete this file.\n\n"
            )
        # Write channel id to file
        ids_file.write(f"{channel_id}\n")

    return add_subscription_response["snippet"]["title"]


if __name__ == "__main__":
    argparser.add_argument("--csv", help="Path to the CSV file containing the subscriptions",
                           default="subscriptions.csv")
    args = argparser.parse_args()

    youtube = get_authenticated_service(args)

    channel_ids = get_channels_list()

    # We have all channel ids, lets subscribe now
    for channel_id in channel_ids:
        try:
            channel_title = add_subscription(youtube, channel_id)
        except HttpError as e:
            error_domain = eval(e.content.decode("utf-8"))["error"]["errors"][0]["domain"]
            if error_domain == "youtube.subscription":
                print("\nSubscription quota has been reached.\n"
                      "All subscribed channels were saved to channels_subscribed.txt.\n"
                      "Try again at a later time...")
                exit(0)
            else:
                print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
                exit(1)
        else:
            print(f"A subscription to {channel_title} was added.")

    print("Finished subscribing to all channels!")
