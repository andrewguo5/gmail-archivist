import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from typing import List
from itertools import batched
import random
import click

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
BATCH_LOWER_LIMIT = 100
BATCH_UPPER_LIMIT = 1000 # As per Google API

def discover_starred_messages(service):
    # A starred message or a message in a thread containing at least 1 star

    # 1. Get all starred messages with pagination
    messages = []
    nextPageToken = None

    while True:
        results = (
            service.users().messages().list(
                userId="me",
                labelIds=["STARRED"],
                pageToken=nextPageToken,
            ).execute()
        )

        messages.extend(results.get("messages", []))
        nextPageToken = results.get("nextPageToken", None)

        if not nextPageToken:
            break

    # 2: For each starred message, get the thread_id
    thread_ids = set()
    for message in messages:
        msg = (
            service.users().messages().get(userId="me", id=message["id"]).execute()
        )
        thread_ids.add(msg["threadId"])

    # 3: For each thread, get all message IDs in that thread
    starred_ids = []
    for thread in thread_ids:
        thread = (
            service.users().threads().get(userId="me", id=thread).execute()
        )
        # 4: Extract the message_ids from messages[]
        thread_messages = thread.get("messages", [])
        for thread_message in thread_messages:
            # 5. Append all of these together and return the expanded_starred_list
            starred_ids.append(thread_message["id"])

    return starred_ids

def discover_archive_targets(service, ttl: str = "3d", max_iter: int = 1000, max_results: int = 500) -> List[str]:
    # Iterates through all INBOX messages which are past a certain age
    # and returns their message ids
    query = f"in:inbox older_than:{ttl}"
    nextPageToken = None
    all_ids = []
    i = 0
    done = False

    try:
        while i < max_iter and not done:
            i += 1

            results = (
                service.users().messages().list(
                    userId="me", 
                    q=query,
                    labelIds=["INBOX"],
                    maxResults=max_results,
                    pageToken=nextPageToken,
                ).execute()
            )
            # Extract from results
            messages = results.get("messages", [])
            if not messages:
                print(f"No messages found.")
                break

            nextPageToken=results.get("nextPageToken", None)

            for message in messages:
                all_ids.append(message["id"])

            # Check if nextPageToken exists
            if not nextPageToken:
                print(f"All messages found. Done.")
                done = True

        if nextPageToken:
            print(f"Max iterations reached.")
    except:
        # We conduct on a best-efforts basis, and return
        # the id's collected so far.
        return all_ids
    
    return all_ids

def batch_archive_messages(service, all_ids):
    # Split into batches
    total_batches = (len(all_ids) + BATCH_UPPER_LIMIT - 1) // BATCH_UPPER_LIMIT
    batch_num = 0
    batches = batched(all_ids, BATCH_UPPER_LIMIT)

    for batch in batches:
        batch_num += 1
        ids = list(batch)
        print(f"Processing batch {batch_num}/{total_batches} ({len(ids)} messages)...")

        body = {
            "ids": ids,
            "removeLabelIds": ["INBOX"],
        }
        service.users().messages().batchModify(
            userId="me",
            body=body,
        ).execute()

        print(f"Batch {batch_num}/{total_batches} completed.")

    return True

def archive_messages(service, all_ids):
    # Iterates through all_ids one at a time and calls modify
    for id in all_ids:
        # construct body
        body = {
            "removeLabelIds": ["INBOX"],
        }
        # modify
        results = service.users().messages().modify(
            userId="me",
            id=id,
            body=body
        ).execute()

def validate_archive_success(service, all_ids, samples: int = 10):
    # Get the labels for one id
    sample_size = min(samples, len(all_ids))
    for id in random.sample(all_ids, sample_size):
        msg = service.users().messages().get(
            userId="me",
            id=id
        ).execute()
        assert "INBOX" not in msg["labelIds"]

@click.command()
@click.option('--ttl', default='3d', help='TTL threshold for archive (e.g., 3d, 1w, 2m)')
@click.option('--max-iter', default=1000, help='Maximum number of search iterations')
@click.option('--max-results', default=500, help='Maximum emails to search for per iteration')
def main(ttl, max_iter, max_results):
    """
    Archive Gmail messages older than the specified time to live (TTL).
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Build service
        service = build("gmail", "v1", credentials=creds)

        # Discover all IDs (if this fails, then do best efforts)
        starred_ids = discover_starred_messages(service)
        all_ids = discover_archive_targets(
            service, ttl=ttl, max_iter=max_iter, max_results=max_results
        )
        if not all_ids:
            print(f"No messages to archive were found. Your inbox is clean!")
        else:
            print(f"{len(all_ids)} found. First: {all_ids[0]}")

        # Remove starred_ids from all_ids
        filtered_ids = [id for id in all_ids if id not in starred_ids]

        # Display summary
        print(f"\n=== Archive Summary ===")
        print(f"Total messages found: {len(all_ids)}")
        print(f"Starred messages (skipped): {len(starred_ids)}")
        print(f"Messages to archive: {len(filtered_ids)}")
        print(f"=======================\n")

        if not filtered_ids:
            print(f"No messages to archive after filtering. Done!")
        else:
            # Display batching information if applicable
            if len(filtered_ids) >= BATCH_LOWER_LIMIT:
                total_batches = (len(filtered_ids) + BATCH_UPPER_LIMIT - 1) // BATCH_UPPER_LIMIT
                print(f"Operation will be batched:")
                print(f"  Batch size: {BATCH_UPPER_LIMIT} messages per batch")
                print(f"  Total batches: {total_batches}\n")
                confirmation = input(f"Will now archive {len(filtered_ids)} emails in {total_batches} batches. Continue? (y/n): ").strip().lower()
            else:
                print(f"Operation will process messages individually.\n")
                confirmation = input(f"Will now archive {len(filtered_ids)} emails. Continue? (y/n): ").strip().lower()
            if confirmation != 'y':
                print("Archive operation cancelled.")
                return
            # See if we want to batch or not
            if len(filtered_ids) >= BATCH_LOWER_LIMIT:
                print(f"Messages to process over batch limit. Batching...")
                # Batch update function
                batch_archive_messages(service, filtered_ids)
            else:
                print(f"Archiving...")
                # Lightweight update function
                archive_messages(service, filtered_ids)

            # Verify the results of the actions
            validate_archive_success(service, filtered_ids)
            print(f"Success! {len(filtered_ids)} emails archived.")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()