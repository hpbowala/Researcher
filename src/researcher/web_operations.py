import os
from urllib.parse import (  # turn normal string into string that can be used in a url
    quote_plus,
)

import requests
from dotenv import load_dotenv
from snapshot_operations import download_snapshot, poll_snapshot_status
import logging

load_dotenv()


def _make_api_request(url: str, **kwargs):
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
       # print(url, headers, kwargs)
        response = requests.post(url, headers=headers, **kwargs)
        response.raise_for_status()  # raise an exception if the request is not successful

        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making API request")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(e)
        return None


def serp_search(query: str, engine="google"):
    if engine == "google":
        base_url = "https://www.google.com/search"
    elif engine == "bing":
        base_url = "https://www.bing.com/search"
    else:
        raise ValueError(f"Unknown engine: {engine}")

    url = "https://api.brightdata.com/request"

    payload = {
        "zone": "ai_agent2",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format": "raw",
    }

    full_response = _make_api_request(url, json=payload)

    if not full_response:
        print(f"No response from API: {engine}")
        return None

    extracted_data = {
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", []),
    }

    return extracted_data


# dataset id = gd_lvz8ah06191smkebj4


def _trigger_and_download_snapshot(
    trigger_url: str, params, data, operation_name="operation"
):
    trigger_result = _make_api_request(trigger_url, params=params, json=data)
    if not trigger_result:
        return None

    snapshot_id = trigger_result.get("snapshot_id")

    if not snapshot_id:
      print(f"No snapshot id found for operation: {operation_name}")
      return None

   # Todo : pull the snapshot data from the snapshot id
    if not poll_snapshot_status(snapshot_id):
      print(f"Snapshot {snapshot_id} is not ready")
      return None

    raw_data = download_snapshot(snapshot_id)
    return raw_data


def reddit_search(keyword, date="All time", sort_by="Hot", num_of_posts=10):
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger"

    params = {
        "dataset_id": "gd_lvz8ah06191smkebj4",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "keyword",
    }

    data = [
        {
            "keyword": keyword,
            "date": date,
            "sort_by": sort_by,
            "num_of_posts": num_of_posts,
        }
    ]

    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="reddit"
    )

    if not raw_data:
        print(f"No data found for keyword: {keyword}")
        return None

    parsed_data = []

    for post in raw_data:
        parsed_data.append({"title": post.get("title"), "url": post.get("url")})

    return {"parsed_posts": parsed_data, "total_found": len(parsed_data)}


def reddit_post_retrieval(url: str, days_back=10, load_all_replies=False, comment_limit=10):

    if not url:
      print(f"No post urls provided")
      return None

  
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger"

    params = {
        "dataset_id": "gd_lvzdpsdlw09j6t702", #dataset id for comments
        "include_errors": "true",
    }

    data = [
        {
            "url": url,
            "days_back": days_back,
            "load_all_replies": load_all_replies,
            "comment_limit": comment_limit,
        }
    ]
   
   
    raw_data = _trigger_and_download_snapshot(
        trigger_url, params, data, operation_name="reddit comments"
    )

    if not raw_data:
        print(f"No data found for post urls: {url}")
        return None

    parsed_data = []

    for comment in raw_data:
      parsed_data.append({
         "comment_id": comment.get("comment_id"),
         "content": comment.get("comment"),
         "date": comment.get("date_posted")
         
      })

    return {"comments": parsed_data, "total_retrieved": len(parsed_data)}