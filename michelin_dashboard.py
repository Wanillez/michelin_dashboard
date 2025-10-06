import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["text.usetex"] = False      #tää koska matplot luulee matikaks
mpl.rcParams["mathtext.default"] = "regular"
mpl.rcParams["text.parse_math"] = False  #tää just ku $ meni matplotti sekaisin

st.set_page_config(page_title="Michelin Dashboard", layout="wide")

### englanniksi koska mua ahistaa kun se on suomeksi se dashboardi :)
#otsikkooo
st.markdown(
    "<h1 style='text-align: center;'>Michelin Restaurants Explorer ⭐</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <h2 style='text-align: center; color: white;'>
        Welcome to the kitchen, chef! 
    </h2>
    <p style='font-size:18px; text-align: center;'>
        Explore the cities, cuisines and prices. <br> 
        Choose dataset below (★ / ★★ / ★★★) and dive right in.
    </p>
    <p style='font-size:16px; text-align: center; font-style: italic;'>
        Tip: click button below! 🍾
    </p>
    """,
    unsafe_allow_html=True
)

#ihan kuule random interaktiivinen juttu tipsei varten
import random

tips = [
    "Pro tip: Filter by city → compare price ranges 🔍",
    "Did you know? Top-20 cities reveal the true Michelin hotspots 🗺️",
    "Hint: Price categories look even tastier as a donut chart 🍩",
    "Chef’s wisdom: $$$$ doesn’t always mean better food – just smaller plates 😅",
    "Life hack: When the data looks messy → eat chocolate and try again 🍫",
    "Hidden tip: The balloons button works in any crisis 🎈"
]

col1, col2, col3 = st.columns([1,2,1])

with col2: 
    if st.button("👨‍🍳 Chef’s Tip", use_container_width=True):
        st.toast(random.choice(tips), icon="💡")


#raw urlit githubista
URLS = {
    "1★": "https://raw.githubusercontent.com/Wanillez/michelin_dashboard/refs/heads/main/one-star-michelin-restaurants.csv",
    "2★": "https://raw.githubusercontent.com/Wanillez/michelin_dashboard/refs/heads/main/two-stars-michelin-restaurants.csv",
    "3★": "https://raw.githubusercontent.com/Wanillez/michelin_dashboard/refs/heads/main/three-stars-michelin-restaurants.csv",
}

#lataa meinaa kaikki 3 tiedostoo kerralla omaan tabsiin
@st.cache_data
def load_csv(u: str):
    return pd.read_csv(u)

one_df = load_csv(URLS["1★"])
two_df = load_csv(URLS["2★"])
three_df = load_csv(URLS["3★"])

#kiva tämmönen metrics
def render_dashboard_for(df: pd.DataFrame, star_label: str):
    st.subheader(f"{star_label} Restaurants – table")
    st.dataframe(df, use_container_width=True)

    total = len(df)
    cities = df["city"].nunique() if "city" in df.columns else 0
    cuisines = df["cuisine"].nunique() if "cuisine" in df.columns else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("Restaurants", f"{total}")
    m2.metric("Cities", f"{cities}")
    m3.metric("Cuisines", f"{cuisines}")

    st.markdown("---")


    #top kaupungit ja top cuisinet 
    st.subheader("Top-20 cities and cuisines")
    col1, col2 = st.columns(2)

    with col1:
        if "city" in df.columns:
            counts = df["city"].dropna().value_counts().head(20)
            fig, ax = plt.subplots(figsize=(6, 4))
            counts.plot(kind="bar", ax=ax)
            ax.set_xlabel("City")
            ax.set_ylabel("number of restaurants")
            ax.set_title("Top-20 cities")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("bo 'city'-column.")

    with col2:
        if "cuisine" in df.columns:
            counts = df["cuisine"].dropna().value_counts().head(20)
            fig, ax = plt.subplots(figsize=(6, 4))
            counts.plot(kind="bar", ax=ax, color="orange")
            ax.set_xlabel("Cuisine")
            ax.set_ylabel("number of restaurants")
            ax.set_title("Top-20 cuisines")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No 'cuisine'-column.")

    st.markdown("---")


    #hinta jakaumat
    st.subheader("Price range – quantity and percentages")
    col1, col2 = st.columns(2)

    with col1:
        if "price" in df.columns:
            prices = df["price"].dropna().astype(str).str.strip()
            levels = prices.str.count(r"\$")
            counts = levels[levels > 0].value_counts().sort_index()
            if not counts.empty:
                labels = ["$" * k for k in counts.index]
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.bar(range(len(counts)), counts.values)
                ax.set_xticks(range(len(counts)))
                ax.set_xticklabels(labels, rotation=0)
                ax.set_xlabel("Price range ($ = cheap, $$$$ = expensive)")
                ax.set_ylabel("number of restaurants")
                ax.set_title("Price category distribution")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                st.info("Price category not found.")
        else:
            st.info("No 'price'-scolumn.")

    with col2:
        if "price" in df.columns:
            counts2 = df["price"].dropna().astype(str).str.strip().value_counts()
            counts2 = counts2.sort_index(key=lambda s: s.str.len()) 
            if not counts2.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(
                    counts2.values,
                    labels=counts2.index,
                    autopct="%1.1f%%",
                    startangle=90,
                    wedgeprops=dict(width=0.4), 
                )
                ax.set_aspect("equal")
                ax.set_title("Price range percentages")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                st.info("Price range not found")
        else:
            st.info("No 'price'-column.")

    st.markdown("---")


    #ihan random interaktiivinen kaupunnki ja rafla nimi selain
    st.subheader("Explore the cities🔎")
    if "city" in df.columns and "name" in df.columns:
        cities = sorted(df["city"].dropna().unique())
        if cities:
            selected_city = st.selectbox("Choose city", cities, key=f"city_{star_label}")
            city_df = df[df["city"] == selected_city]
            st.write(f"**{selected_city}** – {len(city_df)} restaurants")
            cols_to_show = [c for c in ["name", "cuisine", "price"] if c in city_df.columns]
            st.dataframe(city_df[cols_to_show], use_container_width=True)
        else:
            st.info("city not found.")
    else:
        st.info("Need 'city' and 'name' -column.")

    st.markdown("---")

    #basic kartta
    st.subheader(f"Map– {star_label}")
    lat_col, lon_col = "latitude", "longitude"
    if lat_col in df.columns and lon_col in df.columns:
        df_map = df.copy()
        df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors="coerce")
        df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors="coerce")
        geo = df_map[[lat_col, lon_col]].dropna()
        if not geo.empty:
            st.map(geo, zoom=2)
        else:
            st.info("Unable to display map: missing valid coordinates.")
    else:
        st.info("The 'latitude' and 'longitude' columns are needed for the map.")

    st.markdown("---")

    #wordcloudi näytti ihan kivalta en tiiä oliks tarpeen
    try:
        from wordcloud import WordCloud
        if "cuisine" in df.columns and df["cuisine"].dropna().size > 0:
            st.subheader("Most popular cuisine")
            text = " ".join(df["cuisine"].dropna().astype(str)).replace("-", " ")
            wc = WordCloud(width=800, height=400, background_color="white").generate(text)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            plt.tight_layout()

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(fig, use_container_width=False)
    except Exception:
        pass

#TABIT
t1, t2, t3 = st.tabs(["⭐", "⭐⭐", "⭐⭐⭐"])
with t1:
    render_dashboard_for(one_df, "1★")
with t2:
    render_dashboard_for(two_df, "2★")
with t3:
    render_dashboard_for(three_df, "3★")



#ihan kuule ku halusin laittaa streamlit sivulla oli tämmönen!!!
st.markdown("---")

st.subheader("🎉Thank you for visiting my dashboard 🎉")

col1, col2, col3 = st.columns([1,2,1]) 
with col2:
    if st.button("🎈 Thank you - Nancy out! 🎉", use_container_width=True):
        st.balloons()
