import streamlit as st
import pandas as pd
from datetime import date
from modules.youtube_auth import get_authenticated_service
from modules.youtube_api import search_videos, get_comments, reply_to_comment

st.set_page_config(page_title="YouTube Comment Tool", layout="wide")
st.title("YouTube")

search_query = st.text_input("Masukkan kata kunci pencarian video:")

if search_query:
    videos = search_videos(search_query, max_results=25)
    tabs = st.tabs(["📺 Video", "💬 Komentar"])

    with tabs[0]:
        for video in videos:
            st.markdown(f"""
                **{video['title']}**  
                Channel: {video['channel']}  
                Published At: {video['published_at']}  
                [Link ke Video]({video['video_url']})
            """)
            st.markdown("---")

    with tabs[1]:
        creds = get_authenticated_service()
        token = creds.token

        all_comments = []
        for video in videos:
            all_comments.extend(get_comments(video["video_id"], token))

        if all_comments:
            df = pd.DataFrame(all_comments)
            df["published_at"] = pd.to_datetime(df["published_at"])

            col1, col2, col3 = st.columns([1.5, 1.5, 2])

            with col1:
                keyword_filter = st.text_input("🔑 Kata Kunci", key="filter_keyword")
            with col2:
                author_filter = st.text_input("👤 Nama Pengguna", key="filter_author")
            with col3:
                use_date_filter = st.checkbox("Aktifkan Filter Tanggal")
                start_date = None
                if use_date_filter:
                    start_date = st.date_input("📅 Mulai dari tanggal:", key="filter_date")

            # Filter DataFrame
            filtered_df = df.copy()

            if keyword_filter:
                filtered_df = filtered_df[filtered_df["comment"].str.contains(keyword_filter, case=False, na=False)]
            if author_filter:
                filtered_df = filtered_df[filtered_df["author"].str.contains(author_filter, case=False, na=False)]
            if start_date:
                start_date = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df["published_at"].dt.tz_convert(None) >= start_date]


            top_comments = filtered_df[filtered_df["is_reply"] == False]

            if not top_comments.empty:
                for _, row in top_comments.iterrows():
                    st.markdown(f"""
                        **{row['author']}** komentar di [video ini]({row['video_url']}):  
                        > {row['comment']}  
                        {row['published_at'].strftime('%Y-%m-%d %H:%M:%S')}
                    """)
                    text_area_key = f"response_{row['comment_id']}"
                    user_reply = st.text_area("Balasan otomatis:", height=100, key=text_area_key, value="Terima kasih atas komentarnya!")
                    if st.button(f"Kirim Balasan ke {row['author']}", key=f"btn_{row['comment_id']}"):
                        creds = get_authenticated_service()
                        token = creds.token
                        result = reply_to_comment(row["comment_id"], user_reply, token)
                        if result.status_code == 200:
                            st.success("Balasan berhasil dikirim.")
                        else:
                            st.error(f"Gagal mengirim balasan: {result.text}")
                    st.markdown("---")
            else:
                st.info("Tidak ada komentar sesuai filter.")
        else:
            st.info("Tidak ada komentar ditemukan.")
