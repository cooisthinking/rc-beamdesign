import streamlit as st
import beam_ui
import slab_ui
import project_ui  # 🆕 ดึงไฟล์ระบบจัดการโปรเจกต์รวมเข้ามา

# 🌟 กฎเหล็ก: ประกาศตั้งค่าหน้าจอเป็นบรรทัดแรกสุดที่นี่ที่เดียว
st.set_page_config(page_title="ConRC Design Suite Pro", layout="wide")
# 🌟 กฎเหล็ก: ประกาศตั้งค่าหน้าจอเป็นบรรทัดแรกสุดที่นี่ที่เดียว
# st.set_page_config(page_title="ConRC Design Suite Pro", layout="wide")


# ==========================================
# 📌 ฝัง CSS เพื่อล็อคแท็บ (อัปเดตแบบบังคับ !important)
# ==========================================
st.markdown(
    """
    <style>
    /* บังคับให้แถบกด Tabs ล็อคติดขอบจอบนสุดเสมอ */
    div[data-testid="stTabs"] > div:first-child,
    .stTabs > div:first-child {
        position: sticky !important;
        top: 0px !important; 
        z-index: 9999 !important;
        background-color: var(--background-color) !important;
        padding-top: 10px !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    /* 2. ขยายขนาดตัวอักษรบนแท็บ */
    button[data-baseweb="tab"] p {
        font-size: 22px !important;  /* 👈 แก้ความใหญ่ตรงนี้ครับ (ค่าปกติของเว็บคือ 14px) */
        font-weight: bold !important; /* 👈 ทำให้ตัวหนังสือหนาขึ้น จะได้อ่านง่ายๆ */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- 🧠 เริ่มระบบความจำระยะยาวของตัวแอป (Global Session State) ---
# ... (โค้ดเดิมของคุณต่อจากนี้) ...
# --- 🧠 เริ่มระบบความจำระยะยาวของตัวแอป (Global Session State) ---
if "project_name" not in st.session_state:
    st.session_state.project_name = "My_Building_Project"
if "beam_library" not in st.session_state:
    st.session_state.beam_library = {}  # จะเก็บข้อมูล { "B1": {...}, "B2": {...} }
if "slab_library" not in st.session_state:
    st.session_state.slab_library = {}  # จะเก็บข้อมูลอนาคต { "S1": {...}, "S2": {...} }
if "pdf_queue" not in st.session_state:
    st.session_state.pdf_queue = []
st.title("🏢 ConRC: Structural Design Suite")
st.subheader(f"📁 โปรเจกต์ปัจจุบัน: {st.session_state.project_name}")
st.markdown("---")

# 🗂️ เพิ่มแท็บจัดการโปรเจกต์รวมมาไว้เป็นอันแรกสุด
import pdf_ui  # 👈 อย่าลืม import ไฟล์ใหม่ที่เรากำลังจะสร้างด้านบนสุดด้วยนะครับ

# 🗂️ เพิ่มแท็บ iLovePDF (PDF Manager) เข้าไป
tab_proj, tab_beam, tab_slab, tab_pdf = st.tabs([
    "📁  Project Hub  ", 
    "🏗️  RC Beam  ", 
    "🔲  RC Slab  ",
    "📑  PDF Manager  "  # 👈 แท็บใหม่
])

# ... (โค้ดเรียก tab_proj, tab_beam, tab_slab เดิม) ...

with tab_pdf:
    pdf_ui.show_pdf_manager()

# เรียกใช้งานแต่ละโมดูลหน้าจอ
with tab_proj:
    project_ui.show_project_hub()

with tab_beam:
    beam_ui.show_beam_dashboard()

with tab_slab:
    slab_ui.show_slab_dashboard()

# ==========================================
# Footer (แสดงผลด้านล่างสุดของทุกหน้า)
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; padding: 20px 0; font-size: 14px;'>
        <strong>Designed & Developed by</strong> Natdanai Khannark <br>
        <span style='font-size: 12px;'>Civil Engineering Software Recheck Dashboard | Version 2.0 (Developer Version) </span>
    </div>
    """, 
    unsafe_allow_html=True
)