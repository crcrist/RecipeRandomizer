import streamlit as st
import json
import random
from typing import List, Dict, Optional
import time

# Set page config for a wider layout
st.set_page_config(
    page_title="Gourmet Recipe Selector",
    page_icon="🍳",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 1rem;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    .recipe-card {
        padding: 2rem;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        text-align: center;
    }
    .ingredient-list {
        list-style-type: none;
        padding-left: 0;
    }
    .direction-step {
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .cuisine-tag {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        background-color: #e9ecef;
        display: inline-block;
        margin: 0.2rem;
    }
    h1 {
        color: #1e1e1e;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def load_recipes(file_path: str) -> List[Dict]:
    """Load recipes from JSON file"""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data['recipes']
    except FileNotFoundError:
        st.error(f"Recipe file not found: {file_path}")
        return []
    except json.JSONDecodeError:
        st.error("Error decoding recipe file. Please check the JSON format.")
        return []

def filter_recipes(
    recipes: List[Dict],
    cost: Optional[str] = None,
    cuisine: Optional[str] = None,
    max_time: Optional[int] = None
) -> List[Dict]:
    """Filter recipes based on given criteria"""
    filtered = recipes
    
    if cost:
        filtered = [r for r in filtered if r["cost"] == cost]
    if cuisine:
        filtered = [r for r in filtered if r["cuisine"].lower() == cuisine.lower()]
    if max_time:
        filtered = [r for r in filtered if r["cooking_time"] <= max_time]
        
    return filtered

def get_cost_emoji(cost: str) -> str:
    """Convert cost string to emoji representation"""
    return {
        "$": "💰",
        "$$": "💰💰",
        "$$$": "💰💰💰"
    }.get(cost, "")

def get_time_emoji(cooking_time: int) -> str:
    """Get appropriate emoji for cooking time"""
    if cooking_time <= 30:
        return "⚡"  # Fast
    elif cooking_time <= 60:
        return "⏰"  # Medium
    else:
        return "🕰️"  # Long

def display_recipe(recipe: Dict):
    """Display a recipe with enhanced styling"""
    # Create a card for the recipe
    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
    
    # Recipe title and cuisine tag
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# {recipe['name']}")
    with col2:
        st.markdown(f"<div class='cuisine-tag'>{recipe['cuisine']}</div>", unsafe_allow_html=True)
    
    # Key metrics in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Cost {get_cost_emoji(recipe['cost'])}</h3>
                <p>{recipe['cost']}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Time {get_time_emoji(recipe['cooking_time'])}</h3>
                <p>{recipe['cooking_time']} minutes</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>Cuisine 🌍</h3>
                <p>{recipe['cuisine']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Ingredients and Directions in tabs
    tab1, tab2 = st.tabs(["📝 Ingredients", "👩‍🍳 Directions"])
    
    with tab1:
        st.markdown("### What You'll Need:")
        for ingredient in recipe["ingredients"]:
            st.markdown(f"- {ingredient}")
    
    with tab2:
        st.markdown("### Steps to Follow:")
        for i, step in enumerate(recipe["directions"], 1):
            st.markdown(f"""
                <div class='direction-step'>
                    <strong>Step {i}</strong>: {step}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Title with emoji
    st.markdown("# 🍳 Gourmet Recipe Selector")
    st.markdown("---")
    
    # Create two columns for layout
    main_col, sidebar_col = st.columns([3, 1])
    
    with sidebar_col:
        st.markdown("### 🎯 Filter Your Recipe")
        
        # Cost filter with emojis
        cost_options = {
            "Any": None,
            "Budget 💰": "$",
            "Moderate 💰💰": "$$",
            "Luxury 💰💰💰": "$$$"
        }
        cost_filter = st.selectbox(
            "Budget Level",
            options=list(cost_options.keys())
        )
        selected_cost = cost_options[cost_filter]
        
        # Load recipes and get unique cuisines
        recipes = load_recipes('recipes.json')
        cuisines = sorted(list(set(r["cuisine"] for r in recipes)))
        
        # Cuisine filter with emoji
        cuisine_filter = st.selectbox(
            "Cuisine Type 🌍",
            options=["Any"] + cuisines,
            format_func=lambda x: "Any Cuisine" if x == "Any" else x
        )
        selected_cuisine = None if cuisine_filter == "Any" else cuisine_filter
        
        # Time filter with slider and emoji
        max_possible_time = max(r["cooking_time"] for r in recipes)
        time_filter = st.slider(
            "Maximum Cooking Time ⏰",
            min_value=15,
            max_value=max_possible_time,
            value=max_possible_time,
            step=15,
            format="%d mins"
        )
        
        # Filter recipes
        filtered_recipes = filter_recipes(
            recipes,
            cost=selected_cost,
            cuisine=selected_cuisine,
            max_time=time_filter
        )
        
        # Show matching recipes count
        st.markdown(f"### 📊 Matching Recipes: {len(filtered_recipes)}")
        
        # Random recipe button with loading animation
        if st.button("🎲 Surprise Me!", key="random_recipe"):
            if not filtered_recipes:
                st.error("No recipes match your criteria. Try adjusting the filters!")
            else:
                with st.spinner("Finding the perfect recipe..."):
                    time.sleep(0.5)  # Add a small delay for effect
                    selected_recipe = random.choice(filtered_recipes)
                    with main_col:
                        display_recipe(selected_recipe)

    # Initial message in main column
    with main_col:
        if "random_recipe" not in st.session_state:
            st.markdown("""
                ### 👋 Welcome to the Gourmet Recipe Selector!
                
                Use the filters on the right to find your perfect recipe:
                1. Choose your budget level 💰
                2. Select a cuisine type 🌍
                3. Set maximum cooking time ⏰
                4. Click 'Surprise Me!' for a random recipe! 🎲
            """)

if __name__ == "__main__":
    main()