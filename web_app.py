import streamlit as st
import math
from fpdf import FPDF
import os

# ตั้งค่าหน้าเว็บให้กว้างขึ้น
st.set_page_config(page_title="RC Beam Design", layout="wide")

st.title("🏗️ โปรแกรมออกแบบคานคอนกรีตเสริมเหล็ก (เต็มรูปแบบ)")
st.markdown("---")

# ==========================================
# 1. ข้อมูลหน้าตัดและวัสดุ
# ==========================================
st.header("📐 1. ข้อมูลหน้าตัดและวัสดุ (Section & Material)")
col1, col2 = st.columns(2)
with col1:
    b = st.number_input("ความกว้าง b (cm)", min_value=10.0, value=20.0, step=1.0)
    h = st.number_input("ความลึกรวม h (cm)", min_value=10.0, value=40.0, step=1.0)
    cov = st.number_input("ระยะหุ้ม cover (cm)", min_value=1.0, value=3.0, step=0.5)
with col2:
    C = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=100.0, value=240.0, step=10.0)
    F = st.number_input("กำลังครากเหล็กเสริม fy (ksc)", min_value=2000.0, value=4000.0, step=100.0)

# คำนวณเบื้องต้น
d = h - cov
bt, ht, dt = b/100, h/100, d/100
chk = bt * ht * 2400
bat = 0.85
Lol = 0.85 * bat * (C / F) * (6120 / (6120 + F))
LoMax = 0.75 * Lol

st.info(f"**ระยะลึกประสิทธิผล (d)** = {d:.1f} cm | **น้ำหนักคานเบื้องต้น** = {chk:.0f} kg/m | **Rho_max** = {LoMax:.4f}")
st.markdown("---")

# ==========================================
# 2. ออกแบบโมเมนต์บวก (M+)
# ==========================================
st.header("📈 2. ออกแบบรับโมเมนต์บวก (M+)")
col3, col4 = st.columns(2)
with col3:
    MaxP = st.number_input("โมเมนต์บวกสูงสุด Mmax+ (Ton-m)", min_value=0.0, value=1.5, step=0.1)

R = (100 * MaxP) / (0.9 * b * d**2) if MaxP > 0 else 0
lo = 14 / F
m = F / (0.85 * C)
Rn = lo * F * (1 - (0.5 * lo * m))

# วนลูปหาค่า Rho เหมือนใน MATLAB
if MaxP > 0:
    while Rn < R:
        lo += 0.0005
        Rn = lo * F * (1 - (0.5 * lo * m))

ASq = lo * b * d
st.write(f"⚠️ ความต้องการพื้นที่เหล็กเสริม **(As req)**: {ASq:.2f} sq.cm (คำนวณจาก Rho = {lo:.4f})")

with col4:
    AStu = st.number_input("พื้นที่เหล็กเสริมที่ใส่จริง As Provided (M+) (sq.cm)", min_value=0.0, value=float(math.ceil(ASq)), step=0.1)

lotu = AStu / (b * d) if d > 0 else 0
st.markdown("---")

# ==========================================
# 3. ออกแบบโมเมนต์ลบ (M-)
# ==========================================
st.header("📉 3. ออกแบบรับโมเมนต์ลบ (M-)")
calc_m_neg = st.checkbox("คลิกเพื่อคำนวณโมเมนต์ลบ (M-) ด้วย")
MaxP_neg, ASq_neg, AStu_neg, lotu_neg, lo_neg, R_neg, Rn_neg = 0, 0, 0, 0, 0, 0, 0

if calc_m_neg:
    col5, col6 = st.columns(2)
    with col5:
        MaxP_neg = st.number_input("โมเมนต์ลบสูงสุด Mmax- (Ton-m)", min_value=0.0, value=1.0, step=0.1)
    
    R_neg = (100 * MaxP_neg) / (0.9 * b * d**2) if MaxP_neg > 0 else 0
    lo_neg = 14 / F
    Rn_neg = lo_neg * F * (1 - (0.5 * lo_neg * m))
    
    if MaxP_neg > 0:
        while Rn_neg < R_neg:
            lo_neg += 0.001
            Rn_neg = lo_neg * F * (1 - (0.5 * lo_neg * m))
            
    ASq_neg = lo_neg * b * d
    st.write(f"⚠️ ความต้องการพื้นที่เหล็กเสริม **(As req)** สำหรับ M-: {ASq_neg:.2f} sq.cm")
    
    with col6:
        AStu_neg = st.number_input("พื้นที่เหล็กเสริมที่ใส่จริง As Provided (M-) (sq.cm)", min_value=0.0, value=float(math.ceil(ASq_neg)), step=0.1)
    lotu_neg = AStu_neg / (b * d) if d > 0 else 0

st.markdown("---")

# ==========================================
# 4. แรงเฉือน (Shear)
# ==========================================
st.header("✂️ 4. ออกแบบรับแรงเฉือน (Shear)")
col7, col8 = st.columns(2)
with col7:
    VMax = st.number_input("แรงเฉือนสูงสุด Vmax (kg)", min_value=0.0, value=2000.0, step=100.0)
with col8:
    Len = st.number_input("ระยะ V (m)", min_value=0.1, value=4.0, step=0.1)

Vu = (VMax / Len) * (Len - dt) if Len > 0 else 0
Vc = 0.85 * 0.53 * math.sqrt(C) * b * d
st.write(f"**Ultimate Shear (Vu):** {Vu:.2f} kg | **Concrete Capacity (0.85Vc):** {Vc:.2f} kg")

st.markdown("---")

# ==========================================
# 5. Yield Check
# ==========================================
st.header("🔍 5. ตรวจสอบการคราก (Yield Check)")
check_yield = st.checkbox("คลิกเพื่อตรวจสอบ Yield ของเหล็กเสริม (คำนวณจาก M+)")
es, ey = 0, 0
if check_yield and AStu > 0:
    aa = (AStu * F) / (0.85 * C * b)
    x = aa / 0.85
    if x > 0:
        es = (0.003 * (d - x)) / x
    ey = F / (2.04 * 10**6)
    st.write(f"**Strain in Steel (Es):** {es:.5f} | **Yield Strain (Ey):** {ey:.5f}")
    
    if es >= ey:
        st.success("✅ Tension Controlled (Steel Yields) -> ผ่าน!")
    else:
        st.error("❌ Compression Controlled (Steel NOT Yields) -> ต้องปรับแก้การออกแบบ!")

st.markdown("---")

# ==========================================
# 6. สร้างและดาวน์โหลด PDF
# ==========================================
st.header("📄 6. สรุปรายการคำนวณและสร้าง PDF")
if st.button("ประมวลผลและสร้างไฟล์ PDF", type="primary"):
    
    # --- เริ่มคำสั่งสร้าง PDF แบบละเอียด ---
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'RC Beam Design Calculation Sheet', 0, 1, 'C')
            self.line(10, 20, 200, 20)
            self.ln(5)
            
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 11)

    # 1. Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '1. Section and Material Properties', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f'Width (b) = {b:.0f} cm, Total Depth (h) = {h:.0f} cm', 0, 1)
    pdf.cell(0, 7, f'Covering = {cov:.1f} cm, Effective Depth (d) = {d:.0f} cm', 0, 1)
    pdf.cell(0, 7, f'Concrete Strength (fc) = {C:.0f} ksc, Yield Strength (fy) = {F:.0f} ksc', 0, 1)
    pdf.cell(0, 7, f'Max Reinforcement Ratio (Rho_max) = {LoMax:.4f}', 0, 1)
    pdf.ln(5)

    # 2. M+
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '2. Positive Moment Design (M+)', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f'Design Moment (Mmax+) = {MaxP:.3f} Ton-m', 0, 1)
    pdf.cell(0, 7, f'Required As = {ASq:.3f} sq.cm', 0, 1)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 7, f'Provided As = {AStu:.2f} sq.cm (Actual Rho = {lotu:.5f})', 0, 1)
    
    if lotu <= LoMax:
        pdf.cell(0, 7, f'Check Rho: {lotu:.5f} < {LoMax:.4f} (Rho_max) ---> OK!', 0, 1)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 7, f'Check Rho: {lotu:.5f} > {LoMax:.4f} (Rho_max) ---> REVISE!', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # 3. M-
    if calc_m_neg:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '3. Negative Moment Design (M-)', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'Design Moment (Mmax-) = {MaxP_neg:.3f} Ton-m', 0, 1)
        pdf.cell(0, 7, f'Required As = {ASq_neg:.3f} sq.cm', 0, 1)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 7, f'Provided As = {AStu_neg:.2f} sq.cm (Actual Rho = {lotu_neg:.5f})', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # 4. Shear
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '4. Shear Design', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f'Ultimate Shear (Vu) = {Vu:.2f} kg', 0, 1)
    pdf.cell(0, 7, f'Concrete Capacity (0.85Vc) = {Vc:.2f} kg', 0, 1)
    pdf.ln(5)
    
    # 5. Yield
    if check_yield:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '5. Yield Check', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'Strain in Steel (Es) = {es:.5f}, Yield Strain (Ey) = {ey:.5f}', 0, 1)
        if es >= ey:
            pdf.set_text_color(0, 0, 255)
            pdf.cell(0, 7, 'Result: Tension Controlled (Steel Yields) ---> OK!', 0, 1)
        else:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 7, 'Result: Compression Controlled ---> Revise Design!', 0, 1)

    # บันทึกไฟล์ชั่วคราวเพื่อส่งให้ปุ่มดาวน์โหลด
    temp_pdf_name = "Temp_Report.pdf"
    pdf.output(temp_pdf_name)
    
    with open(temp_pdf_name, "rb") as f:
        pdf_bytes = f.read()
        
    st.success("✅ สร้างรายการคำนวณเสร็จสมบูรณ์! กดปุ่มด้านล่างเพื่อดาวน์โหลดไฟล์ PDF ได้เลยครับ")
    
    # ปุ่มดาวน์โหลดไฟล์
    st.download_button(
        label="⬇️ ดาวน์โหลดไฟล์รายการคำนวณ (PDF)",
        data=pdf_bytes,
        file_name="RC_Design_Report.pdf",
        mime="application/pdf"
    )