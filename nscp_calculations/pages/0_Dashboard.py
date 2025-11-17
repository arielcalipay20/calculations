# pages/0_Dashboard.py
import streamlit as st
from src.auth.guard import require_auth, logout_and_redirect

st.set_page_config(layout="wide", page_title="Dashboard - NSCP")

st.session_state["last_page"] = "pages/0_Dashboard.py"

# 🔒 AUTH GUARD
session_state, cm, sess = require_auth("Home.py")

# Hide auth pages from sidebar
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] li:first-child,
    [data-testid="stSidebarNav"] li:last-child {
        display: none;
    }
    
    /* Custom styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Card styling */
    .nav-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .nav-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .nav-card-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .nav-card-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin: 0;
    }
    
    .nav-card-desc {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Welcome section */
    .welcome-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #666;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.write(f"### 👤 {session_state.get('username', '')}")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout_and_redirect(cm, redirect_to="Home.py")

# Welcome Section
st.markdown(f"""
    <div class="welcome-section">
        <h1 class="welcome-title">Welcome Back, {session_state.get('username', '')}! 👋</h1>
        <p class="welcome-subtitle">Choose a module to start your structural calculations</p>
    </div>
""", unsafe_allow_html=True)

# Navigation Cards
st.markdown("### 🎯 Quick Access")
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊", key="loads", help="Loads Analysis", use_container_width=True):
        st.switch_page("pages/1_Loads.py")
    st.markdown("""
        <div style='text-align: center; margin-top: -10px;'>
            <h3 style='margin: 0; color: #667eea;'>Loads</h3>
            <p style='font-size: 0.9rem; color: #666;'>Dead, Live & Wind Loads</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🏗️", key="concrete", help="Concrete Design", use_container_width=True):
        st.switch_page("pages/2_Concrete.py")
    st.markdown("""
        <div style='text-align: center; margin-top: -10px;'>
            <h3 style='margin: 0; color: #667eea;'>Concrete</h3>
            <p style='font-size: 0.9rem; color: #666;'>Reinforced Concrete Design</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("⚙️", key="steel", help="Steel Design", use_container_width=True):
        st.switch_page("pages/3_Steel.py")
    st.markdown("""
        <div style='text-align: center; margin-top: -10px;'>
            <h3 style='margin: 0; color: #667eea;'>Steel</h3>
            <p style='font-size: 0.9rem; color: #666;'>Structural Steel Members</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

col4, col5, col6 = st.columns([1, 1, 1])

with col4:
    if st.button("🌲", key="wood", help="Wood Design", use_container_width=True):
        st.switch_page("pages/4_Wood.py")
    st.markdown("""
        <div style='text-align: center; margin-top: -10px;'>
            <h3 style='margin: 0; color: #667eea;'>Wood</h3>
            <p style='font-size: 0.9rem; color: #666;'>Timber Structures</p>
        </div>
    """, unsafe_allow_html=True)

with col5:
    if st.button("🧱", key="masonry", help="Masonry Design", use_container_width=True):
        st.switch_page("pages/5_Masonry.py")
    st.markdown("""
        <div style='text-align: center; margin-top: -10px;'>
            <h3 style='margin: 0; color: #667eea;'>Masonry</h3>
            <p style='font-size: 0.9rem; color: #666;'>Masonry Wall Design</p>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.empty()

# Stats Section
st.markdown("---")
st.markdown("### 📈 Your Statistics")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.markdown("""
        <div class="stat-card">
            <div class="stat-number">12</div>
            <div class="stat-label">Total Projects</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown("""
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Active Designs</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown("""
        <div class="stat-card">
            <div class="stat-number">7</div>
            <div class="stat-label">Completed</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col4:
    st.markdown("""
        <div class="stat-card">
            <div class="stat-number">98%</div>
            <div class="stat-label">Success Rate</div>
        </div>
    """, unsafe_allow_html=True)