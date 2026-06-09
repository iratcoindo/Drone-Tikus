import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(
    page_title="News Sentiment Analyzer",
    page_icon="📰",
    layout="wide"
)

st.title("📰 News Sentiment Analyzer")

keyword = st.text_input(
    "Masukkan isu",
    placeholder="contoh: javan rhino conservation"
)

jumlah = st.slider(
    "Jumlah berita",
    10,
    100,
    30
)

if st.button("Analyze"):

    if not keyword:
        st.warning("Masukkan keyword terlebih dahulu")
        st.stop()

    rss_url = (
        "https://news.google.com/rss/search?q="
        + quote(keyword)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    try:

        response = requests.get(
            rss_url,
            timeout=20
        )

        if response.status_code != 200:

            st.error(
                f"Gagal mengambil RSS ({response.status_code})"
            )

            st.stop()

        soup = BeautifulSoup(
            response.content,
            "xml"
        )

        items = soup.find_all("item")

        data = []

        positif = 0
        netral = 0
        negatif = 0

        for item in items[:jumlah]:

            title = item.title.text

            link = item.link.text

            score = TextBlob(
                title
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
                "Sentiment": sentiment,
                "Score": round(score, 3),
                "Link": link
            })

        df = pd.DataFrame(data)

        st.success(
            f"Ditemukan {len(df)} berita"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Positive",
            positif
        )

        c2.metric(
            "Neutral",
            netral
        )

        c3.metric(
            "Negative",
            negatif
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        st.subheader(
            "Sentiment Distribution"
        )

        chart_df = pd.DataFrame({
            "Sentiment": [
                "Positive",
                "Neutral",
                "Negative"
            ],
            "Count": [
                positif,
                netral,
                negatif
            ]
        })

        st.bar_chart(
            chart_df.set_index(
                "Sentiment"
            )
        )

        csv = df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "⬇ Download CSV",
            csv,
            f"{keyword}_sentiment.csv",
            "text/csv"
        )

    except Exception as e:

        st.error(str(e))
