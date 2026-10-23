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

store = GameStore()
favorites = store.load()

# Sidebar: settings
with st.sidebar:
    st.title("PatchNotesAIv1.0")
    st.divider()
    st.header("AI Settings")
    api_key = st.text_input("OpenAI-compatible API Key", type="password", value="")
    base_url = st.text_input(
        "API URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

# Main area
tab_search, tab_notes = st.tabs(["Search Games", "Latest Notes"])

steam = SteamClient()
nerf = NerfRadarClient()

with tab_search:
    st.header("Find a game")
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

    st.subheader("Selected Games")
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
            st.session_state.latest_notes_appid = selected["appid"]
            st.session_state.latest_patch_note = notes[0] if notes else None
            st.session_state.pop("latest_patch_summary", None)

        if (
            selected
            and st.session_state.get("latest_notes_appid") == selected["appid"]
        ):
            latest = st.session_state.get("latest_patch_note")
            if latest:
                st.markdown(f"### {latest['title']}")
                st.caption(f"{latest['date']} • {latest.get('feedlabel', '')}")
                if latest.get("url"):
                    st.link_button("Open original", latest["url"])
                st.divider()

                if st.button(
                    "Generate AI summary",
                    type="primary",
                    disabled=not api_key,
                ):
                    ai = AIClient(api_key=api_key, base_url=base_url)
                    ai.model = model
                    with st.spinner("Generating AI summary..."):
                        st.session_state.latest_patch_summary = ai.summarize_patch(
                            latest["title"], latest["contents"]
                        )

                if not api_key:
                    st.info("Enter an API key in the sidebar to generate an AI summary.")
                if summary := st.session_state.get("latest_patch_summary"):
                    st.markdown("#### AI Summary")
                    st.markdown(summary)
            else:
                st.warning("No recent notes or updates found for this game.")

with tab_notes:
    st.subheader("Ask questions about the latest notes")
    if not favorites or not api_key:
        st.info("Enter an API key in the sidebar to chat.")
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
