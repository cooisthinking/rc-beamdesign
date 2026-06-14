import streamlit as st
import calculations as calc  # ดึงไฟล์สมการคณิตศาสตร์
import pdf_report            # ดึงไฟล์วาด PDF 
import math

st.set_page_config(page_title="RC Beam Design", layout="wide")
st.title("🏗️ Cooper's RC Beam Dashboard")
st.markdown("---")

col_left, col_right = st.columns([1.5, 1], gap="large")

# ==========================================
# [ฝั่งขวา - ส่วนที่ 1] ข้อมูลหน้าตัดและวัสดุ
# ==========================================
with col_right:
    st.header("⚙️ ส่วนควบคุมหลัก (Global Controls)")
    with st.container(border=True):
        st.subheader("📐 1. ข้อมูลหน้าตัดและวัสดุ")
        with st.form("form_sec1"):
            c1, c2 = st.columns(2)
            with c1:
                b = st.number_input("ความกว้าง b (cm)", min_value=10.0, value=20.0, step=1.0)
                h = st.number_input("ความลึกรวม h (cm)", min_value=10.0, value=40.0, step=1.0)
                cov = st.number_input("ระยะหุ้ม cover (cm)", min_value=1.0, value=3.0, step=0.5)
            with c2:
                C = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=100.0, value=240.0, step=10.0)
                fy_choices = ["SD40 (fy=4000)", "SD30 (fy=3000)", "SD50 (fy=5000)", "SR24 (fy=2400)", "กำหนดเอง"]
                fy_sel = st.selectbox("ชั้นคุณภาพเหล็กเสริม (fy)", fy_choices)
                if fy_sel == "กำหนดเอง":
                    F = st.number_input("กำลังครากเหล็กเสริม fy (ksc)", min_value=2000.0, value=4000.0, step=100.0)
                else:
                    F = float(fy_sel.split("=")[1].replace(")", ""))
            submit_sec1 = st.form_submit_button("✅ ยืนยันข้อมูลหน้าตัดและวัสดุ")

    d, dt, chk, LoMax = calc.get_basic_props(b, h, cov, C, F)
    st.info(f"**ระยะลึกประสิทธิผล (d)** = {d:.1f} cm | **น้ำหนักคานเบื้องต้น** = {chk:.0f} kg/m | **Rho_max** = {LoMax:.4f}")

# ==========================================
# [ฝั่งซ้าย] ส่วนของการออกแบบคำนวณคาน
# ==========================================
with col_left:
    st.header("🚀 ส่วนคำนวณออกแบบ (Design Analysis)")

    # --- M+ ---
    with st.container(border=True):
        st.subheader("📈 2. ออกแบบรับโมเมนต์บวก (M+)")
        with st.form("form_mpos"):
            m_col, rebar_col = st.columns(2)
            with m_col:
                MaxP = st.number_input("โมเมนต์บวกสูงสุด Mmax+ (Ton-m)", min_value=0.0, value=1.5, step=0.1)
                calc_lo = calc.get_rho_req(MaxP, F, C, b, d)
                st.write(f"💡 Rho ที่ต้องการจากการคำนวณ: **{calc_lo:.5f}**")
                
                use_custom_rho = st.checkbox("กำหนดค่า Rho เอง (M+)", key="chk_rho_pos")
                lo = st.number_input("ใส่ค่า Rho ที่ต้องการ (M+)", min_value=0.0, value=float(calc_lo), step=0.001, format="%.5f") if use_custom_rho else calc_lo
                ASq = lo * b * d
                st.write(f"⚠️ ความต้องการพื้นที่เหล็กเสริม **(As req)**: {ASq:.2f} sq.cm")

            with rebar_col:
                st.markdown("**เลือกเหล็กเสริม (As Provided M+)**")
                rebar_choices = ["DB12", "DB16", "DB20", "DB25", "DB28", "DB32", "RB6", "RB9", "RB12", "กำหนดขนาดเอง"]
                rebar_m_pos = st.selectbox("ขนาดเหล็กเสริม M+", rebar_choices)
                dia_m_pos = st.number_input("เส้นผ่านศูนย์กลาง (mm) M+", min_value=6.0, value=12.0) if rebar_m_pos == "กำหนดขนาดเอง" else float(rebar_m_pos.replace("DB", "").replace("RB", ""))
                n_m_pos = st.number_input("จำนวนเส้น M+", min_value=1, value=2, step=1)
                
                AStu, lotu = calc.get_provided_steel(dia_m_pos, n_m_pos, b, d)
            submit_mpos = st.form_submit_button("✅ คำนวณ M+")

        is_rb_pos = "RB" in rebar_m_pos or (rebar_m_pos == "กำหนดขนาดเอง" and dia_m_pos < 10)
        if is_rb_pos and F != 2400: st.warning("⚠️ **แจ้งเตือน:** เลือกเหล็ก (RB) โปรดปรับชั้นคุณภาพเป็น 'SR24'")

        if AStu < ASq: st.error(f"❌ **NOT OK:** พื้นที่เหล็กที่จัดให้ ({AStu:.2f} sq.cm) น้อยกว่าที่ต้องการ ({ASq:.2f} sq.cm)")
        elif lotu > LoMax: st.error(f"❌ **NOT OK:** อัตราส่วนเหล็กเสริมจริง ({lotu:.5f}) เกิน Rho_max ({LoMax:.4f})")
        else: st.success(f"✅ **OK:** พื้นที่เหล็กที่จัดให้ ({AStu:.2f} sq.cm) เพียงพอ และไม่เกิน Rho_max")

    st.markdown("---")

    # --- M- ---
    st.subheader("📉 3. ออกแบบรับโมเมนต์ลบ (M-)")
    calc_m_neg = st.checkbox("คลิกเพื่อคำนวณโมเมนต์ลบ (M-) ด้วย")
    MaxP_neg, ASq_neg, AStu_neg, lotu_neg, lo_neg, rebar_m_neg, n_m_neg = 0.0, 0.0, 0.0, 0.0, 0.0, "", 0

    if calc_m_neg:
        with st.form("form_mneg"):
            col5, col6 = st.columns(2)
            with col5:
                MaxP_neg = st.number_input("โมเมนต์ลบสูงสุด Mmax- (Ton-m)", min_value=0.0, value=1.0, step=0.1)
                calc_lo_neg = calc.get_rho_req(MaxP_neg, F, C, b, d)
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
                AStu_neg, lotu_neg = calc.get_provided_steel(dia_m_neg, n_m_neg, b, d)
                
            submit_mneg = st.form_submit_button("✅ คำนวณ M-")

        if AStu_neg < ASq_neg: st.error(f"❌ **NOT OK:** พื้นที่เหล็กที่จัดให้ ({AStu_neg:.2f} sq.cm) น้อยกว่าที่ต้องการ ({ASq_neg:.2f} sq.cm)")
        elif lotu_neg > LoMax: st.error(f"❌ **NOT OK:** อัตราส่วนเหล็กเสริมจริง ({lotu_neg:.5f}) เกิน Rho_max ({LoMax:.4f})")
        else: st.success(f"✅ **OK:** พื้นที่เหล็กที่จัดให้ ({AStu_neg:.2f} sq.cm) เพียงพอ และไม่เกิน Rho_max")

    st.markdown("---")

    # --- Shear ---
    with st.container(border=True):
        st.subheader("✂️ 4. ออกแบบรับแรงเฉือน (Shear)")
        with st.form("form_shear"):
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                VMax = st.number_input("แรงเฉือนสูงสุด Vmax (kg)", min_value=0.0, value=2000.0, step=100.0)
            with v_col2:
                Len = st.number_input("ระยะ V (m)", min_value=0.1, value=4.0, step=0.1)
            submit_shear = st.form_submit_button("✅ คำนวณแรงเฉือน")

        Vu, Vc = calc.get_shear(VMax, Len, d, C, b)
        st.write(f"**Ultimate Shear (Vu):** {Vu:.2f} kg | **Concrete Capacity (0.85Vc):** {Vc:.2f} kg")

# ==========================================
# [ฝั่งขวา - ส่วนที่ 2] Yield Check และสร้าง PDF
# ==========================================
with col_right:
    st.markdown("---")
    
    st.subheader("🔍 5. ตรวจสอบการคราก (Yield Check)")
    check_yield = st.checkbox("คลิกเพื่อตรวจสอบ Yield ของเหล็กเสริม (คำนวณจาก M+)")
    es, ey = 0.0, 0.0
    
    if check_yield:
        if AStu > 0:
            es, ey = calc.get_yield(AStu, F, C, b, d)
            st.write(f"**Strain in Steel (Es):** {es:.5f} | **Yield Strain (Ey):** {ey:.5f}")
            if es >= ey: st.success("✅ Tension Controlled (Steel Yields) -> ผ่าน!")
            else: st.error("❌ Compression Controlled (Steel NOT Yields) -> ต้องปรับแก้การออกแบบ!")
        else:
            st.warning("⚠️ โปรดคำนวณจัดเหล็กเสริมที่ฝั่งซ้ายก่อนตรวจเช็ค")

    # ------------------------------------------
    # 🔗 ส่วนเรียกใช้งานระบบวาด PDF
    # ------------------------------------------
    st.subheader("📄 6. สรุปรายการคำนวณและสร้าง PDF")
    if st.button("ประมวลผลและสร้างไฟล์ PDF", type="primary", use_container_width=True):
        
        # โยนค่าทั้งหมดไปให้ไฟล์ pdf_report.py จัดการวาดหน้ากระดาษให้
        pdf_bytes = pdf_report.create_pdf(
            b, h, cov, d, C, F, LoMax, 
            MaxP, ASq, n_m_pos, rebar_m_pos, AStu, lotu, 
            calc_m_neg, MaxP_neg, ASq_neg, n_m_neg, rebar_m_neg, AStu_neg, lotu_neg, 
            Vu, Vc, check_yield, es, ey
        )
            
        st.success("✅ สร้างรายการคำนวณเสร็จสมบูรณ์!")
        st.download_button(
            label="⬇️ ดาวน์โหลดไฟล์ PDF",
            data=pdf_bytes,
            file_name="RC_Design_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )