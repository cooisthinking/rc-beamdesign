import streamlit as st
import math
from fpdf import FPDF
import os

st.set_page_config(page_title="RC Beam Design", layout="wide")

st.title("🏗️ โปรแกรมออกแบบคานคอนกรีตเสริมเหล็ก (เต็มรูปแบบ)")
st.markdown("---")

# ==========================================
# 1. ข้อมูลหน้าตัดและวัสดุ
# ==========================================
st.header("📐 1. ข้อมูลหน้าตัดและวัสดุ (Section & Material)")
with st.form("form_sec1"):
    col1, col2 = st.columns(2)
    with col1:
        b = st.number_input("ความกว้าง b (cm)", min_value=10.0, value=20.0, step=1.0)
        h = st.number_input("ความลึกรวม h (cm)", min_value=10.0, value=40.0, step=1.0)
        cov = st.number_input("ระยะหุ้ม cover (cm)", min_value=1.0, value=3.0, step=0.5)
    with col2:
        C = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=100.0, value=240.0, step=10.0)
        fy_choices = ["SD40 (fy=4000)", "SD30 (fy=3000)", "SD50 (fy=5000)", "SR24 (fy=2400)", "กำหนดเอง"]
        fy_sel = st.selectbox("ชั้นคุณภาพเหล็กเสริม (fy)", fy_choices)
        
        if fy_sel == "กำหนดเอง":
            F = st.number_input("กำลังครากเหล็กเสริม fy (ksc)", min_value=2000.0, value=4000.0, step=100.0)
        else:
            F = float(fy_sel.split("=")[1].replace(")", ""))
            
    submit_sec1 = st.form_submit_button("✅ ยืนยันข้อมูลหน้าตัดและวัสดุ")

# คำนวณเบื้องต้น (อยู่นอกฟอร์มเพื่อให้อัปเดตค่าเสมอเวลากดปุ่ม)
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
with st.form("form_mpos"):
    col3, col4 = st.columns(2)
    with col3:
        MaxP = st.number_input("โมเมนต์บวกสูงสุด Mmax+ (Ton-m)", min_value=0.0, value=1.5, step=0.1)

        if MaxP > 0:
            R = (100 * MaxP) / (0.9 * b * d**2)
            calc_lo = 14 / F
            m = F / (0.85 * C)
            Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
            while Rn < R:
                calc_lo += 0.0005
                Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
                if calc_lo > 0.05: # เบรกฉุกเฉิน
                    break
        else:
            calc_lo = 0.0
        
        st.write(f"💡 Rho ที่ต้องการจากการคำนวณ: **{calc_lo:.5f}**")
        use_custom_rho = st.checkbox("กำหนดค่า Rho เอง (M+)", key="chk_rho_pos")
        lo = st.number_input("ใส่ค่า Rho ที่ต้องการ (M+)", min_value=0.0, value=float(calc_lo), step=0.001, format="%.5f") if use_custom_rho else calc_lo

        ASq = lo * b * d
        st.write(f"⚠️ ความต้องการพื้นที่เหล็กเสริม **(As req)**: {ASq:.2f} sq.cm")

    with col4:
        st.markdown("**เลือกเหล็กเสริม (As Provided M+)**")
        rebar_choices = ["DB12", "DB16", "DB20", "DB25", "DB28", "DB32", "RB6", "RB9", "RB12", "กำหนดขนาดเอง"]
        rebar_m_pos = st.selectbox("ขนาดเหล็กเสริม M+", rebar_choices)
        
        dia_m_pos = st.number_input("เส้นผ่านศูนย์กลาง (mm) M+", min_value=6.0, value=12.0) if rebar_m_pos == "กำหนดขนาดเอง" else float(rebar_m_pos.replace("DB", "").replace("RB", ""))
            
        n_m_pos = st.number_input("จำนวนเส้น M+", min_value=1, value=2, step=1)
        AStu = n_m_pos * (math.pi * (dia_m_pos/10)**2 / 4)
        
    submit_mpos = st.form_submit_button("✅ คำนวณ M+")

# แสดงผลและแจ้งเตือนนอกฟอร์ม
is_rb_pos = "RB" in rebar_m_pos or (rebar_m_pos == "กำหนดขนาดเอง" and dia_m_pos < 10)
if is_rb_pos and F != 2400:
    st.warning("⚠️ **แจ้งเตือน:** เลือกเหล็ก (RB) โปรดปรับชั้นคุณภาพเป็น 'SR24'")
if AStu < ASq:
    st.error(f"❌ **NOT OK:** พื้นที่เหล็กที่จัดให้ ({AStu:.2f} sq.cm) น้อยกว่าที่ต้องการ ({ASq:.2f} sq.cm)")
else:
    st.success(f"✅ **OK:** พื้นที่เหล็กที่จัดให้ ({AStu:.2f} sq.cm) เพียงพอ")

lotu = AStu / (b * d) if d > 0 else 0
st.markdown("---")

# ==========================================
# 3. ออกแบบโมเมนต์ลบ (M-)
# ==========================================
st.header("📉 3. ออกแบบรับโมเมนต์ลบ (M-)")
calc_m_neg = st.checkbox("คลิกเพื่อคำนวณโมเมนต์ลบ (M-) ด้วย")
MaxP_neg, ASq_neg, AStu_neg, lotu_neg, lo_neg = 0, 0, 0, 0, 0
rebar_m_neg, n_m_neg = "", 0

if calc_m_neg:
    with st.form("form_mneg"):
        col5, col6 = st.columns(2)
        with col5:
            MaxP_neg = st.number_input("โมเมนต์ลบสูงสุด Mmax- (Ton-m)", min_value=0.0, value=1.0, step=0.1)
            
            if MaxP_neg > 0:
                R_neg = (100 * MaxP_neg) / (0.9 * b * d**2)
                calc_lo_neg = 14 / F
                m = F / (0.85 * C)
                Rn_neg = calc_lo_neg * F * (1 - (0.5 * calc_lo_neg * m))
                while Rn_neg < R_neg:
                    calc_lo_neg += 0.0005  # ปรับสเต็ปให้เท่ากับ M+
                    Rn_neg = calc_lo_neg * F * (1 - (0.5 * calc_lo_neg * m))
                    if calc_lo_neg > 0.05:
                        break
            else:
                calc_lo_neg = 0.0
                
            st.write(f"💡 Rho ที่ต้องการจากการคำนวณ: **{calc_lo_neg:.5f}**")
            use_custom_rho_neg = st.checkbox("กำหนดค่า Rho เอง (M-)", key="chk_rho_neg")
            lo_neg = st.number_input("ใส่ค่า Rho ที่ต้องการ (M-)", min_value=0.0, value=float(calc_lo_neg), step=0.001, format="%.5f") if use_custom_rho_neg else calc_lo_neg

            ASq_neg = lo_neg * b * d
            st.write(f"⚠️ ความต้องการพื้นที่เหล็กเสริม **(As req)** สำหรับ M-: {ASq_neg:.2f} sq.cm")
        
        with col6:
            st.markdown("**เลือกเหล็กเสริม (As Provided M-)**")
            rebar_m_neg = st.selectbox("ขนาดเหล็กเสริม M-", rebar_choices)
            
            dia_m_neg = st.number_input("เส้นผ่านศูนย์กลาง (mm) M-", min_value=6.0, value=12.0) if rebar_m_neg == "กำหนดขนาดเอง" else float(rebar_m_neg.replace("DB", "").replace("RB", ""))
                
            n_m_neg = st.number_input("จำนวนเส้น M-", min_value=1, value=2, step=1)
            AStu_neg = n_m_neg * (math.pi * (dia_m_neg/10)**2 / 4)
            
        submit_mneg = st.form_submit_button("✅ คำนวณ M-")

    # แสดงผลแจ้งเตือน M-
    is_rb_neg = "RB" in rebar_m_neg or (rebar_m_neg == "กำหนดขนาดเอง" and dia_m_neg < 10)
    if is_rb_neg and F != 2400:
        st.warning("⚠️ **แจ้งเตือน:** เลือกเหล็ก (RB) โปรดปรับชั้นคุณภาพเป็น 'SR24'")
    if AStu_neg < ASq_neg:
        st.error(f"❌ **NOT OK:** พื้นที่เหล็กที่จัดให้ ({AStu_neg:.2f} sq.cm) น้อยกว่าที่ต้องการ ({ASq_neg:.2f} sq.cm)")
    else:
        st.success(f"✅ **OK:** พื้นที่เหล็กที่จัดให้ ({AStu_neg:.2f} sq.cm) เพียงพอ")
            
    lotu_neg = AStu_neg / (b * d) if d > 0 else 0

st.markdown("---")

# ==========================================
# 4. แรงเฉือน (Shear)
# ==========================================
st.header("✂️ 4. ออกแบบรับแรงเฉือน (Shear)")
with st.form("form_shear"):
    col7, col8 = st.columns(2)
    with col7:
        VMax = st.number_input("แรงเฉือนสูงสุด Vmax (kg)", min_value=0.0, value=2000.0, step=100.0)
    with col8:
        Len = st.number_input("ระยะ V (m)", min_value=0.1, value=4.0, step=0.1)

    submit_shear = st.form_submit_button("✅ คำนวณแรงเฉือน")

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
    pdf.cell(0, 7, f'Provided As = {n_m_pos:.0f}-{rebar_m_pos} (Area = {AStu:.2f} sq.cm, Actual Rho = {lotu:.5f})', 0, 1)
    
    if AStu >= ASq and lotu <= LoMax:
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 7, f'Check: As_prov >= As_req & Rho <= Rho_max ---> OK!', 0, 1)
    else:
        pdf.set_text_color(255, 0, 0)
        if AStu < ASq:
            pdf.cell(0, 7, f'Check As: {AStu:.2f} < {ASq:.3f} (As_req) ---> NOT OK!', 0, 1)
        if lotu > LoMax:
            pdf.cell(0, 7, f'Check Rho: {lotu:.5f} > {LoMax:.4f} (Rho_max) ---> NOT OK!', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # 3. M-
    if calc_m_neg:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '3. Negative Moment Design (M-)', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'Design Moment (Mmax-) = {MaxP_neg:.3f} Ton-m', 0, 1)
        pdf.cell(0, 7, f'Required As = {ASq_neg:.3f} sq.cm', 0, 1)
        pdf.cell(0, 7, f'Provided As = {n_m_neg:.0f}-{rebar_m_neg} (Area = {AStu_neg:.2f} sq.cm, Actual Rho = {lotu_neg:.5f})', 0, 1)
        
        if AStu_neg >= ASq_neg and lotu_neg <= LoMax:
            pdf.set_text_color(0, 100, 0)
            pdf.cell(0, 7, f'Check: As_prov >= As_req & Rho <= Rho_max ---> OK!', 0, 1)
        else:
            pdf.set_text_color(255, 0, 0)
            if AStu_neg < ASq_neg:
                pdf.cell(0, 7, f'Check As: {AStu_neg:.2f} < {ASq_neg:.3f} (As_req) ---> NOT OK!', 0, 1)
            if lotu_neg > LoMax:
                pdf.cell(0, 7, f'Check Rho: {lotu_neg:.5f} > {LoMax:.4f} (Rho_max) ---> NOT OK!', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # 4. Shear
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '4. Shear Design', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f'Ultimate Shear (Vu) = {Vu:.2f} kg', 0, 1)
    pdf.cell(0, 7, f'Concrete Capacity (0.85Vc) = {Vc:.2f} kg', 0, 1)
    pdf.ln(5)
    
    # 5. Yield Check
    if check_yield:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, '5. Yield Check', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f'Strain in Steel (Es) = {es:.5f}, Yield Strain (Ey) = {ey:.5f}', 0, 1)
        if es >= ey:
            pdf.set_text_color(0, 100, 0)
            pdf.cell(0, 7, 'Result: Tension Controlled (Steel Yields) ---> OK!', 0, 1)
        else:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 7, 'Result: Compression Controlled ---> NOT OK!', 0, 1)

    temp_pdf_name = "Temp_Report.pdf"
    pdf.output(temp_pdf_name)
    
    with open(temp_pdf_name, "rb") as f:
        pdf_bytes = f.read()
        
    st.success("✅ สร้างรายการคำนวณเสร็จสมบูรณ์! กดปุ่มด้านล่างเพื่อดาวน์โหลดไฟล์ PDF ได้เลยครับ")
    
    st.download_button(
        label="⬇️ ดาวน์โหลดไฟล์รายการคำนวณ (PDF)",
        data=pdf_bytes,
        file_name="RC_Design_Report.pdf",
        mime="application/pdf"
    )