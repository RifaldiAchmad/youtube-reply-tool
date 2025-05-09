import requests


API_KEY = "AIzaSyBHwQKmfheRUOkC3eWTPMYWj4lKy5ElJc4" 


def search_videos(query, max_results=10):
    """Mencari video berdasarkan query keyword."""
    search_url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])

    return [{
        "video_id": item["id"]["videoId"],
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "published_at": item["snippet"]["publishedAt"],
        "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
    } for item in items if "videoId" in item["id"]]


def get_comments(video_id, token):
    """Mengambil komentar dari video tertentu. Jika komentar dinonaktifkan, akan dilewati."""
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "part": "snippet,replies",
        "videoId": video_id,
        "maxResults": 100,
        "textFormat": "plainText"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Tangani error 403 dengan pengecekan pesan error spesifik
        if response.status_code == 403:
            try:
                error_json = response.json()
                reason = error_json.get("error", {}).get("errors", [{}])[0].get("reason", "")
                if reason in ["commentsDisabled", "forbidden", "videoNotFound"]:
                    print(f"[INFO] Komentar tidak tersedia untuk video ID: {video_id} ({reason})")
                    return []  # Skip dan kembalikan list kosong
            except Exception:
                pass  # Jika tidak bisa parsing error json, teruskan error
        raise e

    data = response.json()
    comments = []

    for item in data.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "comment_id": item["id"],
            "comment": snippet["textDisplay"],
            "author": snippet["authorDisplayName"],
            "published_at": snippet["publishedAt"],
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
            "is_reply": False
        })

    return comments


def reply_to_comment(parent_id, reply_text, access_token):
    """Membalas komentar YouTube dengan OAuth token."""
    url = "https://www.googleapis.com/youtube/v3/comments?part=snippet"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "snippet": {
            "parentId": parent_id,
            "textOriginal": reply_text
        }
    }

    return requests.post(url, headers=headers, json=data)
