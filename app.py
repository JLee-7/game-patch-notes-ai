"""Streamlit app: Game Patch Notes AI"""

import os

import streamlit as st
from dotenv import load_dotenv

from src.steam_client import SteamClient
from src.nerf_client import NerfRadarClient
from src.ai import AIClient
from src.game_store import GameStore

load_dotenv()

st.set_page_config(page_title="Game Patch Notes AI", page_icon="🎮", layout="wide")

st.title("🎮 Game Patch Notes with AI")
st.caption("Fetch new patch notes/updates for games you select, then let AI summarize and explain them.")

# Sidebar: favorites + settings
with st.sidebar:
    st.header("Selected Games")
    store = GameStore()
    favorites = store.load()

    if favorites:
        for g in favorites:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{g['name']}**")
            with col2:
                if st.button("✕", key=f"rm_{g['appid']}"):
                    store.remove(g["appid"])
                    st.rerun()
    else:
        st.info("No selected games yet. Search and add some below.")

    st.divider()
    st.header("AI Settings")
    api_key = st.text_input("OpenAI-compatible API Key", type="password", value="")
    base_url = st.text_input(
        "API URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

# Main area
tab_search, tab_notes, tab_chat = st.tabs(["Search Games", "Latest Notes", "Chat with Notes"])

steam = SteamClient()
nerf = NerfRadarClient()

with tab_search:
    st.subheader("Find a game")
    query = st.text_input("Search Steam", placeholder="e.g. Counter-Strike 2, Elden Ring, Valorant")
    if query:
        with st.spinner("Searching Steam..."):
            results = steam.search_games(query)
        if results:
            for r in results[:8]:
                cols = st.columns([1, 4, 1])
                with cols[0]:
                    if r.get("tiny_image"):
                        st.image(r["tiny_image"], width=80)
                with cols[1]:
                    st.markdown(f"**{r['name']}**  \nAppID: `{r['appid']}`")
                with cols[2]:
                    if st.button("Add", key=f"add_{r['appid']}"):
                        store.add(r["appid"], r["name"])
                        st.success(f"Added {r['name']}")
                        st.rerun()
        else:
            st.warning("No results.")

with tab_notes:
    st.subheader("Fetch latest notes/updates")
    if not favorites:
        st.info("Add some games from the Search tab first.")
    else:
        selected = st.selectbox(
            "Choose a game",
            options=favorites,
            format_func=lambda g: g["name"],
        )
        if selected and st.button("Load latest patch notes/Updates", type="primary"):
            with st.spinner("Fetching from Steam..."):
                notes = steam.get_news(selected["appid"], count=5)

            if notes:
                latest = notes[0]
                st.markdown(f"### {latest['title']}")
                st.caption(f"{latest['date']} • {latest.get('feedlabel', '')}")
                if latest.get("url"):
                    st.link_button("Open original", latest["url"])

                st.markdown("#### Raw notes")
                st.text_area("Raw", value=latest["contents"][:8000], height=250, disabled=True)

                if api_key:
                    ai = AIClient(api_key=api_key, base_url=base_url)
                    ai.model = model
                    with st.spinner("Generating AI summary..."):
                        summary = ai.summarize_patch(latest["title"], latest["contents"])
                    st.markdown("#### AI Summary")
                    st.markdown(summary)
                else:
                    st.info("Enter an API key in the sidebar to generate an AI summary.")
            else:
                st.warning("No recent notes or updates found for this game.")

with tab_chat:
    st.subheader("Ask questions about the latest notes")
    if not favorites or not api_key:
        st.info("Add a game and provide an API key to chat.")
    else:
        selected = st.selectbox(
            "Game for chat",
            options=favorites,
            format_func=lambda g: g["name"],
            key="chat_game",
        )
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Load context once
        if "current_context" not in st.session_state or st.button("Refresh notes context"):
            with st.spinner("Loading notes..."):
                notes = steam.get_news(selected["appid"], count=1)
                st.session_state.current_context = notes[0]["contents"] if notes else ""

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about the patch notes..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            ai = AIClient(api_key=api_key, base_url=base_url)
            ai.model = model
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = ai.chat_about_patch(
                        st.session_state.get("current_context", ""),
                        prompt,
                        st.session_state.chat_history[:-1],
                    )
                    st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
