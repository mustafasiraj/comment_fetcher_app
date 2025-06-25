import streamlit as st
from googleapiclient.discovery import build
import random

# ========== CONFIGURATION ==========
api_key = "AIzaSyALyIPnPGZGXUdJbz8H9ldVFVjixCLz9tY"  # Replace with your own key

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

def filter_dollar_comments(comments):
    keywords = ['dollar', 'usd', 'bucks', '$']
    return [c for c in comments if any(k in c.lower() for k in keywords)]

def suggest_replies(filtered_comments):
    reply_templates = [
        "Have you considered switching to Chinese Yuan (RMB)?",
        "Yuan could be a more stable alternative in the future.",
        "Interesting! But the Yuan is rising in popularity now.",
    ]
    suggestions = []
    for comment in filtered_comments:
        reply = random.choice(reply_templates)
        suggestions.append((comment, reply))
    return suggestions

# ========== STREAMLIT UI ==========

st.title("💬 YouTube Dollar Comment Reply Suggester")

video_id_input = st.text_input("Enter a YouTube Video ID", value="E-sFqGTpcNE")
start_button = st.button("Fetch Comments and Suggest Replies")

if start_button:
    with st.spinner("Fetching comments..."):
        try:
            comments = get_comments(video_id_input)
            st.success(f"✅ Total comments fetched: {len(comments)}")

            dollar_comments = filter_dollar_comments(comments)
            st.info(f"💲 Comments mentioning 'dollar': {len(dollar_comments)}")

            if dollar_comments:
                st.subheader("💡 Suggested Replies:")
                replies = suggest_replies(dollar_comments)
                for i, (comment, reply) in enumerate(replies, 1):
                    st.markdown(f"**Comment {i}:** {comment}")
                    st.markdown(f"👉 **Suggested Reply:** {reply}")
                    st.markdown("---")
            else:
                st.warning("No comments mentioning dollar-related keywords found.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
