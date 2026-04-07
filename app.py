"""
app.py — Main Entry Point
AI Resume Analyzer — Landing Page
Particle Background Animation + Liquid Glass UI
"""

import streamlit as st
import os

# ---- Page Config (MUST be first Streamlit call) ----
st.set_page_config(
    page_title="AI Resume Analyzer | Land Your Dream Job",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a Bug": None,
        "About": "AI Resume Analyzer — Built with ❤️ using Streamlit & Google Gemini",
    },
)

# ---- Shared Sidebar Theme Toggle ----
with st.sidebar:
    st.markdown("<div style='font-family: Outfit, sans-serif; font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; margin: 0.5rem 0 0.75rem;'>🌈 Theme</div>", unsafe_allow_html=True)
    
    # Store theme in session state explicitly so it persists
    if "theme_toggle_val" not in st.session_state:
        st.session_state.theme_toggle_val = False

    def sync_theme():
        st.session_state.theme_toggle_val = st.session_state.theme_toggle

    theme_on = st.toggle("🌙 Dark / ☀️ Light Mode", key="theme_toggle", value=st.session_state.theme_toggle_val, on_change=sync_theme)

    import streamlit.components.v1 as components
    components.html(f"""
        <script>
            const body = window.parent.document.body;
            const container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if ({str(theme_on).lower()}) {{
                body.classList.add('light-theme');
                if(container) container.classList.add('light-theme');
            }} else {{
                body.classList.remove('light-theme');
                if(container) container.classList.remove('light-theme');
            }}
        </script>
    """, height=0, width=0)


# ---- Theme Sync ----
import streamlit.components.v1 as components
theme_on = st.session_state.get("theme_toggle", False)
components.html(f"""
    <script>
        const body = window.parent.document.body;
        const container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if ({str(theme_on).lower()}) {{
            body.classList.add('light-theme');
            if(container) container.classList.add('light-theme');
        }} else {{
            body.classList.remove('light-theme');
            if(container) container.classList.remove('light-theme');
        }}
    </script>
""", height=0, width=0)


# ---- Background Video via Static File Serving ----
# Video is served from /app/static/bg_video.mp4 (enabled via config.toml)
st.markdown("""
<!-- Background Image Element -->
<img id="bgImage" style="position: fixed; top: 50%; left: 50%;
              min-width: 100%; min-height: 100%;
              width: auto; height: auto;
              transform: translate(-50%, -50%);
              z-index: -2;
              object-fit: cover;
              pointer-events: none;"
     src="./app/static/bg_img.png">

<!-- Dark cinematic overlay for readability -->
<div id="videoOverlay" style="
    position: fixed; inset: 0;
    background:
        linear-gradient(180deg,
            rgba(0,0,0,0.65) 0%,
            rgba(0,0,0,0.50) 40%,
            rgba(0,0,0,0.72) 100%);
    z-index: -1;
    pointer-events: none;
"></div>

<style>
/* Ensure container is transparent for image beneath */
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}
[data-testid="stAppViewContainer"]::before {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---- Load Custom CSS ----
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---- Particle Background + Glass UI Animations ----
st.markdown("""
<canvas id="particleCanvas" style="
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
    display: block;
"></canvas>

<script>
(function() {
    // Wait for DOM
    function initParticles() {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) { setTimeout(initParticles, 100); return; }
        const ctx = canvas.getContext('2d');

        let W = canvas.width = window.innerWidth;
        let H = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            W = canvas.width = window.innerWidth;
            H = canvas.height = window.innerHeight;
        });

        // Particle system
        const PARTICLE_COUNT = 120;
        const particles = [];

        // Color palette: deep purple + amber gold (matching Pinterest inspo)
        const colors = [
            'rgba(196, 181, 253, ',   // lavender purple
            'rgba(167, 139, 250, ',   // medium purple
            'rgba(124, 58, 237, ',    // deep purple
            'rgba(255, 191, 0, ',     // amber gold (Pinterest pin 1)
            'rgba(255, 167, 38, ',    // warm amber
            'rgba(255, 255, 255, ',   // white sparkle
            'rgba(233, 213, 255, ',   // pale purple
        ];

        function randomColor() {
            return colors[Math.floor(Math.random() * colors.length)];
        }

        function createParticle(forceBottom) {
            const x = Math.random() * W;
            const y = forceBottom ? H + 10 : Math.random() * H;
            const size = Math.random() * 2.5 + 0.5;
            const speedY = -(Math.random() * 0.8 + 0.2);
            const speedX = (Math.random() - 0.5) * 0.4;
            const life = Math.random() * 0.7 + 0.3;
            const decay = Math.random() * 0.003 + 0.001;
            const color = randomColor();
            const twinkle = Math.random() > 0.6;
            const type = Math.random() > 0.85 ? 'spark' : 'dot'; // some are sparkle shapes

            return { x, y, size, speedY, speedX, life, decay, color, twinkle, type };
        }

        // Initialize particles spread across screen
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            particles.push(createParticle(false));
        }

        // Central radial glow (the "sun/moon" from Pinterest pin 1 reference)
        function drawAmberGlow() {
            // Subtle amber glow in upper-right, matching the Pinterest reference
            const grd = ctx.createRadialGradient(W * 0.82, H * 0.15, 0, W * 0.82, H * 0.15, W * 0.28);
            grd.addColorStop(0, 'rgba(255, 191, 0, 0.06)');
            grd.addColorStop(0.4, 'rgba(255, 140, 0, 0.03)');
            grd.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = grd;
            ctx.fillRect(0, 0, W, H);

            // Purple glow (left side)
            const grd2 = ctx.createRadialGradient(W * 0.08, H * 0.5, 0, W * 0.08, H * 0.5, W * 0.25);
            grd2.addColorStop(0, 'rgba(124, 58, 237, 0.08)');
            grd2.addColorStop(0.5, 'rgba(124, 58, 237, 0.03)');
            grd2.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = grd2;
            ctx.fillRect(0, 0, W, H);
        }

        function drawSpark(p) {
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(Date.now() * 0.002);
            const alpha = p.life;
            // Draw a 4-pointed star spark
            ctx.fillStyle = p.color + alpha + ')';
            ctx.shadowColor = p.color + '0.8)';
            ctx.shadowBlur = 6;
            const s = p.size;
            ctx.beginPath();
            for (let i = 0; i < 4; i++) {
                const angle = (i / 4) * Math.PI * 2;
                const x1 = Math.cos(angle) * s * 2.5;
                const y1 = Math.sin(angle) * s * 2.5;
                const x2 = Math.cos(angle + Math.PI / 4) * s * 0.8;
                const y2 = Math.sin(angle + Math.PI / 4) * s * 0.8;
                if (i === 0) ctx.moveTo(x1, y1);
                else ctx.lineTo(x1, y1);
                ctx.lineTo(x2, y2);
            }
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }

        function drawDot(p) {
            const alpha = p.twinkle
                ? p.life * (0.5 + 0.5 * Math.sin(Date.now() * 0.004 + p.x))
                : p.life;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color + alpha + ')';
            ctx.shadowColor = p.color + alpha + ')';
            ctx.shadowBlur = p.size * 4;
            ctx.fill();
        }

        // Vertical light streak (inspired by left-side particle stream in Pinterest pin 1)
        let streakTime = 0;
        function drawVerticalStreak() {
            streakTime += 0.01;
            // Animated vertical amber streak on the far left
            const streakX = W * 0.03;
            const streakAlpha = 0.2 + 0.15 * Math.sin(streakTime);
            const grd = ctx.createLinearGradient(streakX - 2, 0, streakX + 2, H);
            grd.addColorStop(0, 'rgba(255, 191, 0, 0)');
            grd.addColorStop(0.3, `rgba(255, 191, 0, ${streakAlpha})`);
            grd.addColorStop(0.7, `rgba(255, 167, 38, ${streakAlpha * 0.7})`);
            grd.addColorStop(1, 'rgba(255, 191, 0, 0)');
            ctx.fillStyle = grd;
            ctx.fillRect(streakX - 1.5, 0, 3, H);

            // Floating streak particles along the streak
            const sparksY = (Date.now() * 0.08) % H;
            for (let i = 0; i < 3; i++) {
                const sy = (sparksY + i * (H/3)) % H;
                ctx.beginPath();
                ctx.arc(streakX + (Math.random()-0.5) * 6, sy, Math.random() * 1.5 + 0.5, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 191, 0, ${0.4 + Math.random() * 0.3})`;
                ctx.shadowColor = 'rgba(255, 191, 0, 0.8)';
                ctx.shadowBlur = 8;
                ctx.fill();
            }
        }

        function animate() {
            ctx.clearRect(0, 0, W, H);

            // Draw background glows
            drawAmberGlow();
            drawVerticalStreak();

            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.speedX;
                p.y += p.speedY;
                p.life -= p.decay;

                if (p.life <= 0 || p.y < -20) {
                    particles[i] = createParticle(true);
                    continue;
                }

                ctx.save();
                if (p.type === 'spark') {
                    drawSpark(p);
                } else {
                    drawDot(p);
                }
                ctx.restore();
            }

            requestAnimationFrame(animate);
        }

        animate();
    }

    // Start after a short delay to ensure canvas is in DOM
    setTimeout(initParticles, 300);
})();
</script>

<style>
/* Ensure canvas sits behind everything */
#particleCanvas {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 0 !important;
    pointer-events: none !important;
}

/* UI entrance animations */
.stMainBlockContainer > div:first-child {
    animation: fadeInUp 0.7s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Glass hover shimmer effect for interactive elements */
.stButton > button::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.15) 50%, transparent 60%);
    transition: left 0.5s ease;
    pointer-events: none;
}

.stButton > button:hover::after {
    left: 150%;
}

.stButton > button {
    position: relative !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ---- Initialize Session State ----
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "last_analysis" not in st.session_state:
    st.session_state["last_analysis"] = None


# ---- Sidebar ----
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; padding: 1.2rem 0 1.8rem;'>
            <div style='font-size: 2.8rem; filter: drop-shadow(0 0 16px rgba(196,181,253,0.7));
                        animation: float 4s ease-in-out infinite;'>🚀</div>
            <div style='font-family: Outfit, sans-serif; font-size: 1.2rem; font-weight: 800;
                        background: linear-gradient(135deg, #a78bfa, var(--text-primary), #e9d5ff);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        margin-top: 0.5rem; letter-spacing: -0.01em;'>
                AI Resume Analyzer
            </div>
            <div style='font-size: 0.72rem; color: rgba(100,116,139,0.8); margin-top: 6px;
                        letter-spacing: 0.06em; text-transform: uppercase;'>
                Powered by Google Gemini
            </div>
        </div>
        <style>
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # User status
    if st.session_state.get("logged_in"):
        username = st.session_state.get("username", "User")
        st.markdown(
            f"""
            <div style='background: rgba(124,58,237,0.1); backdrop-filter: blur(12px);
                        border: 1px solid var(--card-border);
                        border-radius: 14px; padding: 0.85rem; margin-bottom: 1rem;
                        box-shadow: 0 4px 16px rgba(124,58,237,0.15);'>
                <div style='font-size: 0.7rem; color: rgba(100,116,139,0.8); text-transform: uppercase;
                            letter-spacing: 0.06em;'>Logged in as</div>
                <div style='font-weight: 700; color: var(--text-primary); margin-top: 2px;'>👤 {username}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("👤 Guest Mode — Log in to save your analyses", icon="ℹ️")

    st.markdown(
        """<div style='font-family: Outfit, sans-serif; font-size: 0.8rem; font-weight: 700;
                       color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em;
                       margin: 0.5rem 0 0.75rem;'>📱 Navigation</div>""",
        unsafe_allow_html=True,
    )
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_📄_Resume_Analysis.py", label="Resume Analysis", icon="📄")
    st.page_link("pages/2_💼_Job_Matching.py", label="Job Matching", icon="💼")
    st.page_link("pages/3_📊_Analytics.py", label="Analytics", icon="📊")
    st.page_link("pages/4_💬_AI_Chat.py", label="AI Chat Coach", icon="💬")
    st.page_link("pages/5_🔐_Authentication.py", label="Account", icon="🔐")
    st.divider()

    

    # API Key setup
    with st.expander("⚙️ AI Settings", expanded=False):
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            placeholder="AIzaSy...",
            help="Get your free API key at aistudio.google.com",
        )
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            st.success("✅ API key saved for this session!")
        else:
            st.caption("Running in demo mode (mock AI responses)")

        st.caption("[Get free Gemini API key →](https://aistudio.google.com/)")

    st.divider()
    st.caption("v1.0.0 · Built with Streamlit")


# ============================================================
# ---- MAIN LANDING PAGE ----
# ============================================================

# Hero Section — Liquid Glass Card
st.markdown(
    """
    <div class="hero-card animate-fade-in">
        <div class="glass-shimmer"></div>
        <div class="hero-title">🚀 AI Resume Analyzer</div>
        <div class="hero-subtitle">
            Get your ATS score, AI feedback, and land your dream job faster.<br>
            Powered by Google Gemini AI · 100% Free to Use
        </div>
        <div style='display: flex; gap: 0.75rem; flex-wrap: wrap; position: relative; z-index: 1;'>
            <div class="badge-pill">✅ ATS Score Analysis</div>
            <div class="badge-pill">🤖 AI-Powered Feedback</div>
            <div class="badge-pill">💼 Job Matching</div>
            <div class="badge-pill">📊 Skill Gap Analysis</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Stats Row — Glass metric cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        """<div class="metric-card animate-fade-in-delay-1">
            <div class="metric-value animate-counter-glow">50K+</div>
            <div class="metric-label">Resumes Analyzed</div>
        </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """<div class="metric-card animate-fade-in-delay-2">
            <div class="metric-value animate-counter-glow">95%</div>
            <div class="metric-label">ATS Accuracy</div>
        </div>""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """<div class="metric-card animate-fade-in-delay-3">
            <div class="metric-value animate-counter-glow">15+</div>
            <div class="metric-label">Job Roles</div>
        </div>""",
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        """<div class="metric-card animate-fade-in-delay-3">
            <div class="metric-value animate-counter-glow">⚡ AI</div>
            <div class="metric-label">Gemini Powered</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Quick Start CTA — Glass Panel
st.markdown(
    """
    <div class="cta-box animate-fade-in">
        <div style='font-family: Outfit, sans-serif; font-size: 1.25rem; font-weight: 800;
                    color: var(--text-primary); margin-bottom: 0.5rem; letter-spacing: -0.01em;'>
            🎯 Get Started in 3 Steps
        </div>
        <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1.25rem;'>
            <div style='text-align: center;'>
                <div style='font-size: 2rem; filter: drop-shadow(0 0 12px rgba(196,181,253,0.5));'>📤</div>
                <div style='font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.4rem;
                            font-weight: 600; letter-spacing: 0.03em;'>1. Upload Resume</div>
            </div>
            <div style='color: rgba(124,58,237,0.8); font-size: 1.8rem; display: flex;
                        align-items: center; text-shadow: 0 0 12px rgba(124,58,237,0.6);'>→</div>
            <div style='text-align: center;'>
                <div style='font-size: 2rem; filter: drop-shadow(0 0 12px rgba(196,181,253,0.5));'>🔍</div>
                <div style='font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.4rem;
                            font-weight: 600; letter-spacing: 0.03em;'>2. Get AI Analysis</div>
            </div>
            <div style='color: rgba(124,58,237,0.8); font-size: 1.8rem; display: flex;
                        align-items: center; text-shadow: 0 0 12px rgba(124,58,237,0.6);'>→</div>
            <div style='text-align: center;'>
                <div style='font-size: 2rem; filter: drop-shadow(0 0 12px rgba(196,181,253,0.5));'>✨</div>
                <div style='font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.4rem;
                            font-weight: 600; letter-spacing: 0.03em;'>3. Improve & Apply</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Go to analysis button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🚀 Analyze My Resume Now", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📄_Resume_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)

# ---- Feature Cards ----
st.markdown(
    '<div class="section-header">✨ What You Get</div>',
    unsafe_allow_html=True,
)

features = [
    {
        "icon": "📄",
        "title": "ATS Resume Scoring",
        "desc": "Get a comprehensive ATS compatibility score with detailed breakdown across 8 key categories.",
        "page": "pages/1_📄_Resume_Analysis.py",
    },
    {
        "icon": "💼",
        "title": "Job Description Matching",
        "desc": "Paste any job description and instantly see your compatibility score, missing skills, and keyword gaps.",
        "page": "pages/2_💼_Job_Matching.py",
    },
    {
        "icon": "📊",
        "title": "Skills Analytics",
        "desc": "Visual charts showing your skill distribution, gaps, and how you compare to role requirements.",
        "page": "pages/3_📊_Analytics.py",
    },
    {
        "icon": "💬",
        "title": "AI Chat Coach",
        "desc": "Ask any resume or career question. Get personalized, context-aware advice from your AI coach.",
        "page": "pages/4_💬_AI_Chat.py",
    },
    {
        "icon": "🔐",
        "title": "Secure Account",
        "desc": "Create a free account to save your analyses, track improvements over time, and download reports.",
        "page": "pages/5_🔐_Authentication.py",
    },
    {
        "icon": "📁",
        "title": "Analysis History",
        "desc": "Review past analyses, download PDF reports, and track your resume improvement journey.",
        "page": "pages/6_📁_History.py",
    },
]

cols = st.columns(3)
for i, feature in enumerate(features):
    with cols[i % 3]:
        st.markdown(
            f"""
            <div class="feature-card animate-fade-in">
                <div class="feature-icon">{feature['icon']}</div>
                <div class="feature-title">{feature['title']}</div>
                <div class="feature-desc">{feature['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

# ---- How It Works ----
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div class="section-header">🔬 How It Works</div>',
    unsafe_allow_html=True,
)

col_l, col_r = st.columns(2)
with col_l:
    st.markdown(
        """
        <div class="how-panel animate-fade-in">
            <h4 style='font-family: Outfit, sans-serif; color: var(--text-primary); margin-top: 0;
                       font-size: 1.05rem; letter-spacing: -0.01em;'>🤖 AI Analysis Engine</h4>
            <p style='color: var(--text-secondary); font-size: 0.88rem; line-height: 1.7; margin-bottom: 0.75rem;'>
                Our multi-layered analysis pipeline combines:
            </p>
            <ul style='color: var(--text-secondary); font-size: 0.85rem; line-height: 2.2; padding-left: 1.25rem;'>
                <li><b style='color: var(--text-primary);'>TF-IDF Vectorization</b> — Keyword extraction & similarity scoring</li>
                <li><b style='color: var(--text-primary);'>ATS Algorithm</b> — 8-category compliance check</li>
                <li><b style='color: var(--text-primary);'>Google Gemini AI</b> — Deep semantic analysis & suggestions</li>
                <li><b style='color: var(--text-primary);'>Skills Taxonomy DB</b> — 200+ skills mapped to industry roles</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_r:
    st.markdown(
        """
        <div class="how-panel animate-fade-in">
            <h4 style='font-family: Outfit, sans-serif; color: var(--text-primary); margin-top: 0;
                       font-size: 1.05rem; letter-spacing: -0.01em;'>📋 ATS Score Categories</h4>
            <div style='display: flex; flex-direction: column; gap: 0.6rem;'>
        """,
        unsafe_allow_html=True,
    )

    categories = [
        ("Contact Information", 10),
        ("Section Structure", 15),
        ("Content Length", 10),
        ("Action Verbs", 10),
        ("Quantified Achievements", 15),
        ("Skills Section", 15),
        ("Education", 10),
        ("Work Experience", 15),
    ]

    for cat, weight in categories:
        bar_width = weight * 5  # scale for visual
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 0.75rem;'>
                <div style='width: 165px; font-size: 0.78rem; color: var(--text-secondary);
                            flex-shrink: 0;'>{cat}</div>
                <div style='flex: 1; background: rgba(26,26,46,0.5); border-radius: 6px; height: 6px;
                            border: 1px solid rgba(255,255,255,0.05); overflow: hidden;'>
                    <div style='width: {bar_width}%; height: 100%;
                                background: linear-gradient(90deg, #7C3AED, #a78bfa, var(--text-primary));
                                border-radius: 6px; box-shadow: 0 0 8px rgba(124,58,237,0.5);'>
                    </div>
                </div>
                <div style='font-size: 0.78rem; color: #a78bfa; font-weight: 700; width: 30px;'>{weight}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---- Footer ----
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; padding: 1.75rem;
                border-top: 1px solid rgba(255,255,255,0.06);
                background: rgba(255,255,255,0.02);
                backdrop-filter: blur(12px);
                border-radius: 16px;
                box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset;'>
        <div style='color: rgba(100,116,139,0.7); font-size: 0.82rem; letter-spacing: 0.02em;'>
            Made with ❤️ using Streamlit &amp; Google Gemini AI &nbsp;·&nbsp;
            <a href='#' style='color: rgba(167,139,250,0.8); text-decoration: none;
                               transition: color 0.2s;'>Privacy Policy</a> &nbsp;·&nbsp;
            <a href='#' style='color: rgba(167,139,250,0.8); text-decoration: none;'>Terms of Service</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
