import streamlit as st
from googleapiclient.discovery import build
import random

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

# ========== STREAMLIT UI ==========

st.title("💬 Custom Keyword-Based YouTube Comment Responder")

video_id = st.text_input("🎥 Enter YouTube Video ID", value="E-sFqGTpcNE")

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

if st.button("Fetch Comments and Suggest Replies"):
    if not keyword_reply_dict:
        st.warning("Please enter at least one valid keyword and reply pair.")
    else:
        with st.spinner("Fetching YouTube comments..."):
            try:
                comments = get_comments(video_id)
                st.success(f"✅ Fetched {len(comments)} comments")

                suggestions = match_and_suggest(comments, keyword_reply_dict)

                st.info(f"💡 Found {len(suggestions)} matching comments")
                if suggestions:
                    for i, (comment, reply) in enumerate(suggestions, 1):
                        st.markdown(f"**Comment {i}:** {comment}")
                        st.markdown(f"👉 **Your Reply:** {reply}")
                        st.markdown("---")
                else:
                    st.warning("No comments matched your keywords.")

            except Exception as e:
                st.error(f"❌ Error: {e}")
