import streamlit as st
import os
import json

# ---------- Paths ----------
BASE_DIR = os.path.dirname(__file__)
WORLDS_DIR = os.path.join(BASE_DIR, "worlds")
os.makedirs(WORLDS_DIR, exist_ok=True)

# ---------- Utility Functions ----------
def list_worlds():
    return [f.replace(".json", "") for f in os.listdir(WORLDS_DIR) if f.endswith(".json")]

def load_world_data(world_name):
    path = os.path.join(WORLDS_DIR, f"{world_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_world_data(world_name, data):
    path = os.path.join(WORLDS_DIR, f"{world_name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def trigger_rerun():
    st.session_state._rerun = True

# ---------- Session Init ----------
if "current_world" not in st.session_state:
    st.session_state.current_world = None
if "world_elements" not in st.session_state:
    st.session_state.world_elements = []
if "_rerun" in st.session_state:
    del st.session_state["_rerun"]
    st.rerun()

# ---------- Sidebar: World Selection ----------
st.sidebar.title("🌍 World Selector")

worlds = list_worlds()
new_world = st.sidebar.text_input("➕ Create New World")

if new_world:
    if new_world not in worlds:
        st.session_state.current_world = new_world
        st.session_state.world_elements = []
        save_world_data(new_world, [])
        trigger_rerun()
    else:
        st.sidebar.warning("World already exists!")

selected_world = st.sidebar.selectbox("🌐 Select Existing World", ["-- Select --"] + worlds)

if selected_world != "-- Select --" and selected_world != st.session_state.current_world:
    st.session_state.current_world = selected_world
    st.session_state.world_elements = load_world_data(selected_world)
    trigger_rerun()

# ---------- Main UI ----------
if not st.session_state.current_world:
    st.title("🌍 A.R. Worldbuilder")
    st.info("Please select or create a world from the sidebar to get started.")
    st.stop()

# ---------- Sidebar Navigation ----------
page = st.sidebar.radio("📂 Navigate", ["📘 View World", "📝 Add Entry", "⚙️ Save & Export"])
st.title(f"🌍 {st.session_state.current_world}")

# ---------- View World ----------
if page == "📘 View World":
    st.subheader("All Entries")
    if st.session_state.world_elements:
        for element in st.session_state.world_elements:
            st.markdown(f"### {element['name']}  \n**Type:** {element['type']}")
            st.markdown(element['description'])
            st.markdown("---")
    else:
        st.info("This world has no entries yet.")

# ---------- Add Entry ----------
elif page == "📝 Add Entry":
    st.subheader("Add New Entry")

    name = st.text_input("Name", key="new_name")
    categories = [
        "Location", "Character", "Faction", "Event",
        "Object", "Scene", "Belief System", "Concept", "Note / Wildcard"
    ]
    type_selected = st.selectbox("Category", categories, key="new_type")
    description = st.text_area("Description", height=150, key="new_desc")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Save Entry"):
            if name and description:
                new_element = {
                    "name": name,
                    "type": type_selected,
                    "description": description
                }
                st.session_state.world_elements.append(new_element)
                save_world_data(st.session_state.current_world, st.session_state.world_elements)
                st.success(f"Saved '{name}' under {type_selected}!")
                trigger_rerun()
            else:
                st.warning("Please enter both name and description.")
    with col2:
        if st.button("❌ Cancel"):
            trigger_rerun()

# ---------- Settings / Export ----------
elif page == "⚙️ Save & Export":
    st.subheader("Save & Export")

    if st.button("💾 Save Now"):
        save_world_data(st.session_state.current_world, st.session_state.world_elements)
        st.success(f"Saved {len(st.session_state.world_elements)} entries to '{st.session_state.current_world}.json'.")

    st.download_button(
        label="⬇️ Download World File",
        data=json.dumps(st.session_state.world_elements, indent=4),
        file_name=f"{st.session_state.current_world}.json",
        mime="application/json"
    )
