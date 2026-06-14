import streamlit as st
import calculations as calc  
import pdf_report            
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="RC Beam Design", layout="wide")
st.title("🏗️ Con RC Beam Dashboard")
st.markdown("---")

def draw_cross_section(b, h, cov, n_pos, dia_pos, n_neg, dia_neg, rebar_v, spacing, figsize=(3, 5)):
    # ตัวแปร figsize เอาไว้ปรับขนาดรูปให้เล็ก/ใหญ่ได้ตามใจชอบ
    fig, ax = plt.subplots(figsize=figsize)
    
    # 1. วาดกรอบคอนกรีต
    ax.add_patch(patches.Rectangle((0, 0), b, h, fill=True, facecolor='#fdfdfd', edgecolor='black', lw=2))
    
    # 2. เขียนตัวเลขบอกขนาด (กว้าง x ลึก)
    ax.text(b/2, h + 2, f"{b/100:.2f} m.", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(-4, h/2, f"{h/100:.2f} m.", ha='right', va='center', fontsize=10, fontweight='bold', rotation=90)
    
    # 3. วาดเหล็กปลอก
    sx, sy = cov, cov
    sw, sh = b - 2*cov, h - 2*cov
    ax.add_patch(patches.Rectangle((sx, sy), sw, sh, fill=False, edgecolor='black', lw=1.5))
    
    # 4. ฟังก์ชันย่อยสำหรับวาดเหล็กแกนพร้อมชี้บอกชื่อ
    def draw_bars(n, dia, y_level, label_prefix):
        if n <= 0: return
        d_cm = dia / 10.0
        x_start = cov + d_cm/2
        x_end = b - cov - d_cm/2
        x_coords = [b/2] if n == 1 else [x_start + i*(x_end - x_start)/(n - 1) for i in range(int(n))]
        
        for x in x_coords:
            ax.add_patch(patches.Circle((x, y_level), d_cm/2, fill=True, color='black'))
            
        # ลากเส้นชี้บอกรายละเอียดเหล็ก (Annotation)
        label = f"{int(n)}-{label_prefix}{int(dia)}mm."
        ax.annotate(label, xy=(x_coords[-1], y_level), xytext=(b + 8, y_level),
                    arrowprops=dict(arrowstyle="-", lw=1), fontsize=9, va='center')

    # เรียกใช้วาดเหล็กบน (M-) และเหล็กล่าง (M+)
    draw_bars(n_neg, dia_neg, h - cov - (dia_neg/20), "DB" if dia_neg >= 10 else "RB")
    draw_bars(n_pos, dia_pos, cov + (dia_pos/20), "DB" if dia_pos >= 10 else "RB")
    
    # ลากเส้นชี้บอกเหล็กปลอก
    v_label = f"Stirrup-{rebar_v} @ {spacing:.0f} cm."
    ax.annotate(v_label, xy=(b-cov, h/2), xytext=(b + 8, h/2),
                arrowprops=dict(arrowstyle="-", lw=1), fontsize=9, va='center')

    # ขยายขอบเขตภาพให้เห็นข้อความที่ชี้ออกไปด้านขวา
    ax.set_xlim(-10, b + 35) 
    ax.set_ylim(-5, h + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

col_left, col_right = st.columns([1.5, 1], gap="large")

with col_right:
    st.header("⚙️ ส่วนควบคุมหลัก (Global Controls)")
    with st.container(border=True):
        st.subheader("📐 1. ข้อมูลหน้าตัดและวัสดุ")
        c1, c2 = st.columns(2)
        with c1:
            b = st.number_input("ความกว้าง b (cm)", min_value=10.0, value=20.0, step=5.0)
            h = st.number_input("ความลึกรวม h (cm)", min_value=10.0, value=40.0, step=5.0)
            cov = st.number_input("ระยะหุ้ม cover (cm)", min_value=1.0, value=3.0, step=0.5)
        with c2:
            C = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=100.0, value=240.0, step=10.0)
            fy_choices = ["SD30 (fy=3000)","SD40 (fy=4000)", "SD50 (fy=5000)", "SR24 (fy=2400)", "กำหนดเอง"]
            fy_sel = st.selectbox("ชั้นคุณภาพเหล็ก (fy)", fy_choices)
            if fy_sel == "กำหนดเอง":
                F = st.number_input("กำลังครากเหล็ก fy (ksc)", min_value=2000.0, value=4000.0, step=100.0)
            else:
                F = float(fy_sel.split("=")[1].replace(")", ""))

    d, dt, chk, LoMax = calc.get_basic_props(b, h, cov, C, F)
    st.info(f"**d** = {d:.1f} cm | **น้ำหนัก** = {chk:.0f} kg/m | **Rho_max** = {LoMax:.4f}")

    st.subheader("🎨 หน้าตัดคาน (Cross Section)")
    drawing_placeholder = st.empty()

with col_left:
    st.header("🚀 ส่วนคำนวณออกแบบ (Design Analysis)")

    # --- M+ ---
    with st.container(border=True):
        st.subheader("📈 2. ออกแบบรับโมเมนต์บวก (M+)")
        m_col, rebar_col = st.columns(2)
        with m_col:
            MaxP = st.number_input("Mmax+ (Ton-m)", min_value=0.0, value=1.5, step=0.1)
            calc_lo = calc.get_rho_req(MaxP, F, C, b, d)
            st.write(f"💡 Rho ที่ต้องการ: **{calc_lo:.5f}**")
            use_custom_rho = st.checkbox("กำหนดค่า Rho เอง (M+)")
            lo = st.number_input("Rho (M+)", min_value=0.0, value=float(calc_lo), step=0.001, format="%.5f") if use_custom_rho else calc_lo
            ASq = lo * b * d
            st.write(f"⚠️ As req: **{ASq:.2f} sq.cm**")

        with rebar_col:
            rebar_choices = ["DB12", "DB16", "DB20", "DB25", "DB28", "DB32", "RB6", "RB9", "RB12", "กำหนดขนาดเอง"]
            rebar_m_pos = st.selectbox("ขนาดเหล็ก M+", rebar_choices)
            dia_m_pos = st.number_input("Dia (mm) M+", min_value=6.0, value=12.0) if rebar_m_pos == "กำหนดขนาดเอง" else float(rebar_m_pos.replace("DB", "").replace("RB", ""))
            n_m_pos = st.number_input("จำนวนเส้น M+", min_value=1, value=2, step=1)
            AStu, lotu = calc.get_provided_steel(dia_m_pos, n_m_pos, b, d)
            st.info(f"📏 พื้นที่เหล็กใส่จริง: **{AStu:.2f} sq.cm**")

        if AStu < ASq: st.error(f"❌ NOT OK: As จัดให้ ({AStu:.2f}) < As ต้องการ ({ASq:.2f})")
        elif lotu > LoMax: st.error(f"❌ NOT OK: Rho ({lotu:.5f}) > Rho_max ({LoMax:.4f})")
        else: st.success("✅ OK: เหล็กเสริมรับแรงดึงเพียงพอ")

    st.markdown("---")

    # --- M- ---
    st.subheader("📉 3. ออกแบบรับโมเมนต์ลบ (M-)")
    calc_m_neg = st.checkbox("คลิกเพื่อคำนวณโมเมนต์ลบ (M-) ด้วย")
    MaxP_neg, ASq_neg, AStu_neg, lotu_neg, rebar_m_neg, n_m_neg, dia_m_neg = 0.0, 0.0, 0.0, 0.0, "ไม่มี", 0, 0.0

    if calc_m_neg:
        col5, col6 = st.columns(2)
        with col5:
            MaxP_neg = st.number_input("Mmax- (Ton-m)", min_value=0.0, value=1.0, step=0.1)
            calc_lo_neg = calc.get_rho_req(MaxP_neg, F, C, b, d)
            st.write(f"💡 Rho ที่ต้องการ: **{calc_lo_neg:.5f}**")
            use_custom_rho_neg = st.checkbox("กำหนดค่า Rho เอง (M-)")
            lo_neg = st.number_input("Rho (M-)", min_value=0.0, value=float(calc_lo_neg), step=0.001, format="%.5f") if use_custom_rho_neg else calc_lo_neg
            ASq_neg = lo_neg * b * d
            st.write(f"⚠️ As req: **{ASq_neg:.2f} sq.cm**")
        
        with col6:
            rebar_m_neg = st.selectbox("ขนาดเหล็ก M-", rebar_choices)
            dia_m_neg = st.number_input("Dia (mm) M-", min_value=6.0, value=12.0) if rebar_m_neg == "กำหนดขนาดเอง" else float(rebar_m_neg.replace("DB", "").replace("RB", ""))
            n_m_neg = st.number_input("จำนวนเส้น M-", min_value=1, value=2, step=1)
            AStu_neg, lotu_neg = calc.get_provided_steel(dia_m_neg, n_m_neg, b, d)
            st.info(f"📏 พื้นที่เหล็กใส่จริง: **{AStu_neg:.2f} sq.cm**")

        if AStu_neg < ASq_neg: st.error("❌ NOT OK")
        elif lotu_neg > LoMax: st.error("❌ NOT OK")
        else: st.success("✅ OK")

    st.markdown("---")

    # --- Shear (เหล็กปลอกสุดเทพ) ---
    with st.container(border=True):
        st.subheader("✂️ 4. ออกแบบรับแรงเฉือน (Shear)")
        
        # ✅ ระบบเลือกกรอก Vmax หรือ Vu
        shear_mode = st.radio("วิธีระบุแรงเฉือน:", ["คำนวณจากน้ำหนัก (Vmax)", "กำหนดค่า Vu โดยตรง"], horizontal=True)
        
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            if shear_mode == "คำนวณจากน้ำหนัก (Vmax)":
                VMax = st.number_input("แรงเฉือนสูงสุด Vmax (kg)", min_value=0.0, value=2000.0, step=100.0)
                Len = st.number_input("ระยะเคลียร์คาน L (m)", min_value=0.1, value=4.0, step=0.1)
                Vu = (VMax / Len) * (Len - d/100) if Len > 0 else 0.0
            else:
                Vu = st.number_input("แรงเฉือนประลัย Vu (kg)", min_value=0.0, value=1500.0, step=100.0)
                
        with v_col2:
            rebar_v_choices = ["RB6", "RB9", "DB10", "DB12"]
            rebar_v = st.selectbox("ขนาดเหล็กปลอก", rebar_v_choices)
            dia_v = float(rebar_v.replace("DB", "").replace("RB", ""))
            Fv = st.number_input("fy ปลอก (ksc)", min_value=2400.0, value=2400.0, step=100.0)
            
        phi_Vc = calc.get_shear_concrete(d, C, b)
        st.write(f"**แรงเฉือนที่กระทำ (Vu):** {Vu:.2f} kg | **คอนกรีตรับได้เอง (\u03c6Vc):** {phi_Vc:.2f} kg")

        st.markdown("---")
        # ✅ ระบบเลือกให้โปรแกรมคำนวณ หรือกรอกเอง
        spacing_mode = st.radio("การจัดระยะเหล็กปลอก:", ["ให้โปรแกรมจัดให้ (@)", "กรอกระยะแอดเพื่อเช็คเอง"], horizontal=True)
        
        if spacing_mode == "ให้โปรแกรมจัดให้ (@)":
            shear_status, spacing, Vs_req = calc.get_stirrup_req(Vu, phi_Vc, b, d, C, Fv, dia_v)
            if Vs_req > 0:
                st.write(f"⚠️ แรงเฉือนที่เหล็กปลอกต้องรับภาระแทน **(Vs req)** = {Vs_req:.2f} kg")
                
            if "หน้าตัดเล็กเกินไป" in shear_status:
                st.error(f"❌ {shear_status}")
            else:
                st.info(f"📏 ระยะแอดแนะนำ: **{rebar_v} @ {spacing:.0f} cm**")
                st.success(f"✅ {shear_status}")
        else:
            s_custom = st.number_input("ใส่ระยะแอด @ (cm)", min_value=2.0, value=15.0, step=1.0)
            spacing = s_custom
            shear_status, is_ok, Vs_req, Vs_prov = calc.check_custom_stirrup(Vu, phi_Vc, b, d, C, Fv, dia_v, s_custom)
            
            if Vs_req > 0:
                st.write(f"⚠️ เหล็กปลอกต้องรับภาระ **(Vs req)** = {Vs_req:.2f} kg | 🛡️ ปลอกที่ใส่รับได้ **(Vs prov)** = {Vs_prov:.2f} kg")
            
            if is_ok:
                st.info(f"📏 ระยะแอดใช้งาน: **{rebar_v} @ {spacing:.0f} cm**")
                st.success(f"✅ {shear_status}")
            else:
                st.error(f"❌ {shear_status}")

# วาดภาพหน้าตัดคาน
# ==========================================
# ประมวลผลภาพวาดหน้าตัดและแสดงผลสดๆ ทางฝั่งขวา
# ==========================================
# ✅ เพิ่ม spacing และกำหนดขนาด figsize ให้เล็กลง (กว้าง 2.5 นิ้ว, สูง 4 นิ้ว)
fig = draw_cross_section(b, h, cov, n_m_pos, dia_m_pos, n_m_neg, dia_m_neg, rebar_v, spacing, figsize=(2.5, 4))

with drawing_placeholder.container():
    st.pyplot(fig)

# บันทึกรูปภาพชั่วคราวเพื่อรอส่งฝังลง PDF (เซฟด้วยความละเอียดสูง DPI=300 จะได้คมกริบใน PDF)
img_path = "cross_section.png"
fig.savefig(img_path, bbox_inches='tight', dpi=300)
# ==========================================
# [ฝั่งขวา - ส่วนที่ 2] Yield Check และสร้าง PDF
# ==========================================
with col_right:
    st.markdown("---")
    
    # ✅ เอาปุ่ม Checkbox กลับมาให้ตามคำขอครับ!
    st.subheader("🔍 5. ตรวจสอบการคราก (Yield Check)")
    check_yield = st.checkbox("คลิกเพื่อตรวจสอบ Yield ของเหล็กเสริม (คำนวณจาก M+)")
    es, ey = 0.0, 0.0
    
    if check_yield:
        if AStu > 0:
            es, ey = calc.get_yield(AStu, F, C, b, d)
            st.write(f"**Strain in Steel (Es):** {es:.5f} | **Yield Strain (Ey):** {ey:.5f}")
            if es >= ey: st.success("✅ Tension Controlled (Steel Yields) -> ผ่าน!")
            else: st.error("❌ Compression Controlled (Steel NOT Yields) -> ต้องแก้หน้าตัด!")
        else:
            st.warning("⚠️ โปรดระบุจำนวนเหล็กเสริม M+ ที่ฝั่งซ้ายก่อนตรวจเช็ค")

    st.subheader("📄 6. ออกรายงาน")
    if st.button("ประมวลผลและสร้างไฟล์ PDF", type="primary", use_container_width=True):
        Vs_req = calc.get_stirrup_req(Vu, phi_Vc, b, d, C, Fv, dia_v)[2] if spacing_mode == "ให้โปรแกรมจัดให้ (@)" else calc.check_custom_stirrup(Vu, phi_Vc, b, d, C, Fv, dia_v, spacing)[2]
        
        # ✅ ลบตัวแปร check_yield ออกจากวงเล็บด้านล่างนี้ครับ
        pdf_bytes = pdf_report.create_pdf(
            b, h, cov, d, C, F, LoMax, MaxP, ASq, n_m_pos, rebar_m_pos, AStu, lotu, 
            calc_m_neg, MaxP_neg, ASq_neg, n_m_neg, rebar_m_neg, AStu_neg, lotu_neg, 
            Vu, phi_Vc, Vs_req, rebar_v, spacing, es, ey, img_path
        )
        st.success("✅ เสร็จสมบูรณ์!")
        st.download_button("⬇️ ดาวน์โหลด PDF", data=pdf_bytes, file_name="RC_Design.pdf", mime="application/pdf", use_container_width=True)