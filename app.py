import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob

st.set_page_config(
    page_title="Social Sentiment Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Social Media Sentiment Analyzer")

keyword = st.text_input(
    "Keyword",
    placeholder="contoh: wildlife conservation"
)

jumlah = st.slider(
    "Jumlah posting",
    10,
    100,
    30
)

if st.button("Analyze"):

    if not keyword:
        st.warning("Masukkan keyword")
        st.stop()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = (
        f"https://www.reddit.com/search.json"
        f"?q={keyword}&limit={jumlah}"
    )

    try:

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if r.status_code != 200:

            st.error(
                f"Gagal mengambil data ({r.status_code})"
            )

            st.stop()

        posts = r.json()["data"]["children"]

        data = []

        positif = 0
        negatif = 0
        netral = 0

        for post in posts:

            p = post["data"]

            title = p.get(
                "title",
                ""
            )

            text = p.get(
                "selftext",
                ""
            )

            full_text = (
                title + " " + text
            )

            score = TextBlob(
                full_text
            ).sentiment.polarity

            if score > 0.1:

                sentiment = "Positive"
                positif += 1

            elif score < -0.1:

                sentiment = "Negative"
                negatif += 1

            else:

                sentiment = "Neutral"
                netral += 1

            data.append({

                "Title": title,

                "Score": round(
                    score,
                    3
                ),

                "Sentiment": sentiment,

                "URL": (
                    "https://reddit.com"
                    + p.get(
                        "permalink",
                        ""
                    )
                )

            })

        df = pd.DataFrame(
            data
        )

        st.success(
            f"{len(df)} posting ditemukan"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Positive",
            positif
        )

        col2.metric(
            "Neutral",
            netral
        )

        col3.metric(
            "Negative",
            negatif
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "⬇ Download CSV",
            csv,
            "sentiment_results.csv",
            "text/csv"
        )

    except Exception as e:

        st.error(str(e))
