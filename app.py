import streamlit as st
from googleapiclient.discovery import build
import random
import re

# ========== CONFIGURATION ==========
api_key = "AIzaSyALyIPnPGZGXUdJbz8H9ldVFVjixCLz9tY"  # Replace with your key

# ========== SETUP YOUTUBE API ==========
@st.cache_data
def get_youtube_client():
    return build('youtube', 'v3', developerKey=api_key)

youtube = get_youtube_client()

# ========== FUNCTIONS ==========

def get_comments(video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()

    for item in response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

def match_and_suggest(comments, keyword_reply_dict):
    suggestions = []
    for comment in comments:
        matched = False
        for keyword, reply in keyword_reply_dict.items():
            if keyword.lower() in comment.lower():
                suggestions.append((comment, reply))
                matched = True
                break  # Only first keyword match matters
        if not matched:
            continue
    return suggestions

def extract_video_id(link_or_id):
    """
    Extract YouTube video ID from full link or just the ID.
    Supports:
    - https://www.youtube.com/watch?v=UBqy7m1Ejc0
    - https://youtu.be/UBqy7m1Ejc0
    - https://youtube.com/shorts/UBqy7m1Ejc0
    - UBqy7m1Ejc0
    """
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, link_or_id)
        if match:
            return match.group(1)
    return None

# ========== STREAMLIT UI ==========

st.title("💬 YouTube Comment Reply Generator (Custom Keywords)")

# 📘 Quick Start Instructions
st.markdown("""
### 📘 Quick Start Example
- **Step 1:** From a YouTube link like:  
  `https://www.youtube.com/watch?v=**zAULhNrnuL8**`  
  👉 **Copy and paste the full link or just `zAULhNrnuL8`** below  
  ✅ Also supports links from YouTube app or shorts!

- **Step 2:** Enter keywords and replies like:  
  `Keyword: dollar` → `Reply: Try switching to Yuan?`  
  `Keyword: war` → `Reply: War impacts everything. Stay informed!`
""")
st.markdown("---")

# 🎥 User input: Full link or video ID
user_input_link = st.text_input("🎥 Paste YouTube link or video ID", value="https://youtu.be/zAULhNrnuL8")
video_id = extract_video_id(user_input_link)

# 🧠 Keyword → Reply input
st.markdown("### 🧠 Define Your Keyword → Reply Pairs")
num_pairs = st.number_input("How many keyword → reply pairs do you want?", min_value=1, max_value=10, value=3)

keyword_reply_dict = {}
for i in range(num_pairs):
    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input(f"Keyword {i+1}", key=f"kw_{i}")
    with col2:
        reply = st.text_input(f"Reply {i+1}", key=f"rp_{i}")
    
    if keyword and reply:
        keyword_reply_dict[keyword.strip().lower()] = reply.strip()

# 🔁 Process Comments
if st.button("Fetch Comments and Suggest Replies"):
    if not video_id:
        st.error("⚠️ Could not extract a valid YouTube video ID. Please check your link.")
    elif not keyword_reply_dict:
        st.warning("⚠️ Please enter at least one keyword and reply pair.")
    else:
        with st.spinner("🔄 Fetching comments..."):
            try:
                comments = get_comments(video_id)
                st.success(f"✅ Fetched {len(comments)} comments")

                suggestions = match_and_suggest(comments, keyword_reply_dict)

                st.info(f"💡 Found {len(suggestions)} matching comments")
                if suggestions:
                    st.subheader("🧠 Suggested Replies")
                    for i, (comment, reply) in enumerate(suggestions, 1):
                        st.markdown(f"**Comment {i}:** {comment}")
                        st.markdown(f"👉 **Your Reply:** {reply}")
                        st.markdown("---")
                else:
                    st.warning("No comments matched your keywords.")

            except Exception as e:
                st.error(f"❌ Error: {e}")
