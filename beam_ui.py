import streamlit as st
import calculations as calc  
import pdf_report            
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import io

# ✅ เพิ่มบรรทัดนี้เข้าไป เพื่อบังคับให้รูปภาพอ่านภาษาไทยได้ครับ!
# ==========================================
# 📐 ตั้งค่าฟอนต์สไตล์วิศวกรรม (Engineering Font)
# ==========================================
plt.rcParams['font.family'] = 'Cordia New'  # ฟอนต์มาตรฐานสไตล์ AutoCAD/แบบก่อสร้าง
plt.rcParams['font.size'] = 14              # เพิ่มขนาดขึ้นนิดนึงให้เส้นตัวอักษรชัดเจน

def draw_cross_section(b, h, cov, n_pos, dia_pos, n_neg, dia_neg, rebar_v, spacing, figsize=(3, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    
    # 1. วาดกรอบคอนกรีต
    ax.add_patch(patches.Rectangle((0, 0), b, h, fill=True, facecolor='#fdfdfd', edgecolor='black', lw=2))
    
    # 2. วาดเส้นบอกระยะ (Dimension Lines)
    dim_y = h + 8
    ax.plot([0, b], [dim_y, dim_y], color='black', lw=1)
    ax.plot([0, 0], [h+2, dim_y+4], color='black', lw=0.5)
    ax.plot([b, b], [h+2, dim_y+4], color='black', lw=0.5)
    ax.plot([-3, 3], [dim_y-3, dim_y+3], color='black', lw=1)
    ax.plot([b-3, b+3], [dim_y-3, dim_y+3], color='black', lw=1)
    ax.text(b/2, dim_y + 2, f"{b/100:.2f}", ha='center', va='bottom', fontsize=10)
    
    dim_x = -8
    ax.plot([dim_x, dim_x], [0, h], color='black', lw=1)
    ax.plot([dim_x-4, -2], [0, 0], color='black', lw=0.5)
    ax.plot([dim_x-4, -2], [h, h], color='black', lw=0.5)
    ax.plot([dim_x-3, dim_x+3], [-3, 3], color='black', lw=1)
    ax.plot([dim_x-3, dim_x+3], [h-3, h+3], color='black', lw=1)
    ax.text(dim_x - 3, h/2, f"{h/100:.2f}", ha='right', va='center', fontsize=10, rotation=90)
    
    # 3. วาดเหล็กปลอก
    sx, sy = cov, cov
    sw, sh = b - 2*cov, h - 2*cov
    ax.add_patch(patches.Rectangle((sx, sy), sw, sh, fill=False, edgecolor='black', lw=1.5))
    
    # 4. ฟังก์ชันย่อยสำหรับวาดเหล็กแกน
    def draw_bars(n, dia, y_level, label_prefix):
        if n <= 0: return
        d_cm = dia / 10.0
        x_start = cov + d_cm/2
        x_end = b - cov - d_cm/2
        x_coords = [b/2] if n == 1 else [x_start + i*(x_end - x_start)/(n - 1) for i in range(int(n))]
        
        for x in x_coords:
            ax.add_patch(patches.Circle((x, y_level), d_cm/2, fill=True, color='black'))
            
        label = f"{int(n)}-{label_prefix}{int(dia)}mm."
        ax.text(b + 5, y_level, label, ha='left', va='center', fontsize=10)

    # เรียกใช้วาดเหล็กบน (M-) และเหล็กล่าง (M+)
    draw_bars(n_neg, dia_neg, h - cov - (dia_neg/20), "DB" if dia_neg >= 10 else "RB")
    draw_bars(n_pos, dia_pos, cov + (dia_pos/20), "DB" if dia_pos >= 10 else "RB")
    
    rebar_type = "DB" if "DB" in rebar_v else "RB"
    rebar_dia = rebar_v.replace("DB", "").replace("RB", "")
    v_label = f"ป.-{rebar_type} {rebar_dia}mm.@{spacing/100:.2f}m."
    ax.text(b + 5, h/2, v_label, ha='left', va='center', fontsize=10)

    ax.set_xlim(-15, b + 45) 
    ax.set_ylim(-10, h + 15)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

def show_beam_dashboard():
    st.header("🏗️ ConRC:Beam for Recheck")
    
    # ==========================================
    # แผงเรียกดูและดึงข้อมูลคานจากคลังรวมประจำตึก
    # ==========================================
    st.markdown("### 💾 ระบบจัดการคลังข้อมูลคานประจำโปรเจกต์")
    beam_options = ["+ ออกแบบคานใหม่ / เพิ่มประเภทคาน"] + list(st.session_state.beam_library.keys())
    selected_beam_opt = st.selectbox("เลือกประเภทคานเพื่อเรียกข้อมูลเดิมขึ้นมาดูหรือแก้ไข:", beam_options)
    
    # กำหนดค่ามาตรฐานเริ่มต้นสำหรับกรณีสร้างคานใหม่
    val_b, val_h, val_cov, val_C, val_fy = 20.0, 40.0, 3.0, 240.0, "SD40 (fy=4000)"
    val_Mpos, val_rebar_pos, val_n_pos = 1.5, "DB12", 2
    val_Mneg, val_rebar_neg, val_n_neg, val_calc_m_neg = 1.0, "DB12", 2, False
    val_Vmax, val_rebar_v, val_spacing = 2000.0, "RB6", 15.0
    
    # ดึงข้อมูลมาเติมกรณีเลือกคานเดิมจากคลัง
    if selected_beam_opt != "+ ออกแบบคานใหม่ / เพิ่มประเภทคาน":
        b_stored = st.session_state.beam_library[selected_beam_opt]
        val_b = b_stored.get("b", 20.0)
        val_h = b_stored.get("h", 40.0)
        val_cov = b_stored.get("cover", 3.0)
        val_C = b_stored.get("fc", 240.0)
        val_fy = b_stored.get("fy_label", "SD40 (fy=4000)")
        val_Mpos = b_stored.get("MaxP", 1.5)
        val_rebar_pos = b_stored.get("rebar_m_pos", "DB12")
        val_n_pos = b_stored.get("n_m_pos", 2)
        
        # ดึงค่าโมเมนต์ลบกลับมาจากเซฟเดิม
        val_calc_m_neg = b_stored.get("calc_m_neg", False)
        val_Mneg = b_stored.get("MaxP_neg", 1.0)
        val_rebar_neg = b_stored.get("rebar_m_neg", "DB12")
        val_n_neg = b_stored.get("n_m_neg", 2)
        
        val_Vmax = b_stored.get("VMax", 2000.0)
        val_rebar_v = b_stored.get("rebar_v", "RB6")
        val_spacing = b_stored.get("spacing", 15.0)
        st.info(f"📂 เรียกข้อมูลของคาน **{selected_beam_opt}** ขึ้นมาแสดงผลแล้ว")
        
    st.markdown("---")
    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_right:
        st.header(" ส่วนควบคุมหลัก (Global Controls)")
        with st.container(border=True):
            st.subheader("📐 ข้อมูลหน้าตัดและวัสดุ")
            c1, c2 = st.columns(2)
            with c1:
                b = st.number_input("ความกว้าง b (cm)", min_value=10.0, value=float(val_b), step=5.0)
                h = st.number_input("ความลึกรวม h (cm)", min_value=10.0, value=float(val_h), step=5.0)
                cov = st.number_input("ระยะหุ้ม cover (cm)", min_value=1.0, value=float(val_cov), step=0.5)
            with c2:
                C = st.number_input("กำลังอัดคอนกรีต fc' (ksc)", min_value=100.0, value=float(val_C), step=10.0)
                fy_choices = ["SD30 (fy=3000)","SD40 (fy=4000)", "SD50 (fy=5000)", "SR24 (fy=2400)", "กำหนดเอง"]
                
                try: fy_idx = fy_choices.index(val_fy)
                except: fy_idx = 4
                fy_sel = st.selectbox("ชั้นคุณภาพเหล็ก (fy)", fy_choices, index=fy_idx)
                if fy_sel == "กำหนดเอง":
                    F = st.number_input("กำลังครากเหล็ก fy (ksc)", min_value=2000.0, value=4000.0, step=100.0)
                else:
                    F = float(fy_sel.split("=")[1].replace(")", ""))

        d, dt, chk, LoMax = calc.get_basic_props(b, h, cov, C, F)
        st.info(f"**d** = {d:.1f} cm | **น้ำหนัก** = {chk:.0f} kg/m | **Rho_max** = {LoMax:.4f}")

        st.subheader(" หน้าตัดคาน (Cross Section)")
        
        # 🪄 1. ฝัง CSS ขั้นเด็ดขาด ซ่อนตัวเลข Slider ทุกรูปแบบ
        st.markdown(
            """
            <style>
            /* ซ่อนตัวเลขที่ลอยอยู่บนปุ่มเลื่อน (Thumb Value) ทุกเวอร์ชั่น */
            div[data-testid="stThumbValue"],
            div[data-testid="stSliderThumbValue"],
            .stSlider div[data-baseweb="slider"] [role="slider"] + div {
                display: none !important;
                opacity: 0 !important;
                visibility: hidden !important;
            }
            
            /* ซ่อนตัวเลข Min/Max หัวท้าย (Tick Bar) ทุกเวอร์ชั่น */
            div[data-testid="stTickBar"],
            div[data-testid="stSliderTickBar"],
            .stSlider div[data-baseweb="slider"] + div {
                display: none !important;
                opacity: 0 !important;
                visibility: hidden !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # 🎚️ 2. แถบเลื่อนแบบมินิมอล (เหลือแต่เส้น)
        zoom_w = st.slider("🔍", min_value=150, max_value=1200, value=500, step=25, label_visibility="collapsed")
        
        drawing_placeholder = st.empty()

    with col_left:
        st.header(" ส่วนคำนวณออกแบบ (Design Analysis)")

        # --- M+ ---
        with st.container(border=True):
            st.subheader(" ออกแบบรับ Moment(M+)")
            m_col, rebar_col = st.columns(2)
            with m_col:
                MaxP = st.number_input("Mmax+ (Ton-m)", min_value=0.0, value=float(val_Mpos), step=0.1)
                calc_lo = calc.get_rho_req(MaxP, F, C, b, d)
                st.write(f"💡 Rho ที่ต้องการ: **{calc_lo:.5f}**")
                use_custom_rho = st.checkbox("กำหนดค่า Rho เอง (M+)")
                lo = st.number_input("Rho (M+)", min_value=0.0, value=float(calc_lo), step=0.001, format="%.5f") if use_custom_rho else calc_lo
                ASq = lo * b * d
                st.write(f"⚠️ As req: **{ASq:.2f} sq.cm**")

            with rebar_col:
                rebar_choices = ["DB12", "DB16", "DB20", "DB25", "DB28", "DB32", "RB6", "RB9", "RB12", "กำหนดขนาดเอง"]
                try: rb_idx = rebar_choices.index(val_rebar_pos)
                except: rb_idx = 0
                rebar_m_pos = st.selectbox("ขนาดเหล็ก M+", rebar_choices, index=rb_idx)
                dia_m_pos = st.number_input("Dia (mm) M+", min_value=6.0, value=12.0) if rebar_m_pos == "กำหนดขนาดเอง" else float(rebar_m_pos.replace("DB", "").replace("RB", ""))
                n_m_pos = st.number_input("จำนวนเส้น M+", min_value=1, value=int(val_n_pos), step=1)
                AStu, lotu = calc.get_provided_steel(dia_m_pos, n_m_pos, b, d)
                st.info(f"📏 พื้นที่เหล็กใส่จริง: **{AStu:.2f} sq.cm**")

            if AStu < ASq: st.error(f"❌ NOT OK: As จัดให้ ({AStu:.2f}) < As ต้องการ ({ASq:.2f})")
            elif lotu > LoMax: st.error(f"❌ NOT OK: Rho ({lotu:.5f}) > Rho_max ({LoMax:.4f})")
            else: st.success("✅ OK: เหล็กเสริมรับแรงดึงเพียงพอ")

        st.markdown("---")

        # --- M- (กู้กลับคืนชีพมาให้แล้วครับ!) ---
        st.subheader(" ออกแบบรับ Moment(M-)")
        calc_m_neg = st.checkbox("คลิกเพื่อคำนวณโมเมนต์ลบ (M-) ด้วย", value=val_calc_m_neg)
        MaxP_neg, ASq_neg, AStu_neg, lotu_neg, rebar_m_neg, n_m_neg, dia_m_neg = 0.0, 0.0, 0.0, 0.0, "ไม่มี", 0, 0.0

        if calc_m_neg:
            col5, col6 = st.columns(2)
            with col5:
                MaxP_neg = st.number_input("Mmax- (Ton-m)", min_value=0.0, value=float(val_Mneg), step=0.1)
                calc_lo_neg = calc.get_rho_req(MaxP_neg, F, C, b, d)
                st.write(f"💡 Rho ที่ต้องการ: **{calc_lo_neg:.5f}**")
                use_custom_rho_neg = st.checkbox("กำหนดค่า Rho เอง (M-)")
                lo_neg = st.number_input("Rho (M-)", min_value=0.0, value=float(calc_lo_neg), step=0.001, format="%.5f") if use_custom_rho_neg else calc_lo_neg
                ASq_neg = lo_neg * b * d
                st.write(f"⚠️ As req: **{ASq_neg:.2f} sq.cm**")
            
            with col6:
                try: rb_neg_idx = rebar_choices.index(val_rebar_neg)
                except: rb_neg_idx = 0
                rebar_m_neg = st.selectbox("ขนาดเหล็ก M-", rebar_choices, index=rb_neg_idx)
                dia_m_neg = st.number_input("Dia (mm) M-", min_value=6.0, value=12.0) if rebar_m_neg == "กำหนดขนาดเอง" else float(rebar_m_neg.replace("DB", "").replace("RB", ""))
                n_m_neg = st.number_input("จำนวนเส้น M-", min_value=1, value=int(val_n_neg), step=1)
                AStu_neg, lotu_neg = calc.get_provided_steel(dia_m_neg, n_m_neg, b, d)
                st.info(f"📏 พื้นที่เหล็กใส่จริง: **{AStu_neg:.2f} sq.cm**")

            if AStu_neg < ASq_neg: st.error("❌ NOT OK: พื้นที่เหล็กไม่พอ")
            elif lotu_neg > LoMax: st.error("❌ NOT OK: Rho เกิน Rho_max")
            else: st.success("✅ OK: เหล็กเสริมรับแรงกดเพียงพอ")

        st.markdown("---")

        # --- Shear ---
        with st.container(border=True):
            st.subheader(" ออกแบบรับแรงเฉือน (Shear)")
            
            shear_mode = st.radio("วิธีระบุแรงเฉือน:", ["คำนวณจากน้ำหนัก (Vmax)", "กำหนดค่า Vu โดยตรง"], horizontal=True)
            
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                if shear_mode == "คำนวณจากน้ำหนัก (Vmax)":
                    VMax = st.number_input("แรงเฉือนสูงสุด Vmax (kg)", min_value=0.0, value=float(val_Vmax), step=100.0)
                    Len = st.number_input("ระยะเคลียร์คาน L (m)", min_value=0.1, value=4.0, step=0.1)
                    Vu = (VMax / Len) * (Len - d/100) if Len > 0 else 0.0
                else:
                    Vu = st.number_input("แรงเฉือนประลัย Vu (kg)", min_value=0.0, value=float(val_Vmax), step=100.0)
                    VMax = Vu
                    
            with v_col2:
                rebar_v_choices = ["RB6", "RB9", "DB10", "DB12"]
                try: rb_v_idx = rebar_v_choices.index(val_rebar_v)
                except: rb_v_idx = 0
                rebar_v = st.selectbox("ขนาดเหล็กปลอก", rebar_v_choices, index=rb_v_idx)
                dia_v = float(rebar_v.replace("DB", "").replace("RB", ""))
                Fv = st.number_input("fy ปลอก (ksc)", min_value=2400.0, value=2400.0, step=100.0)
                
            phi_Vc = calc.get_shear_concrete(d, C, b)
            st.write(f"**แรงเฉือนที่กระทำ (Vu):** {Vu:.2f} kg | **คอนกรีตรับได้เอง (\u03c6Vc):** {phi_Vc:.2f} kg")

            st.markdown("---")
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
                s_custom = st.number_input("ใส่ระยะแอด @ (cm)", min_value=2.0, value=float(val_spacing), step=1.0)
                spacing = s_custom
                shear_status, is_ok, Vs_req, Vs_prov = calc.check_custom_stirrup(Vu, phi_Vc, b, d, C, Fv, dia_v, s_custom)
                
                if Vs_req > 0:
                    st.write(f"⚠️ เหล็กปลอกต้องรับภาระ **(Vs req)** = {Vs_req:.2f} kg | 🛡️ ปลอกที่ใส่รับได้ **(Vs prov)** = {Vs_prov:.2f} kg")
                
                if is_ok:
                    st.info(f"📏 ระยะแอดใช้งาน: **{rebar_v} @ {spacing:.0f} cm**")
                    st.success(f"✅ {shear_status}")
                else:
                    st.error(f"❌ {shear_status}")

    # ประมวลผลภาพวาดหน้าตัดคาน (เหล็กบนเหล็กล่างจะแสดงผลสอดคล้องกันอย่างสมบูรณ์)
    fig = draw_cross_section(b, h, cov, n_m_pos, dia_m_pos, n_m_neg, dia_m_neg, rebar_v, spacing, figsize=(2.5, 4))

    with drawing_placeholder.container():
        buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    
    with drawing_placeholder.container():
        st.image(buf, width=zoom_w)

    img_path = "cross_section.png"

    with col_right:
        st.markdown("---")
        st.subheader(" ตรวจสอบการคราก (Yield Check)")
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

        st.subheader("📄 ออกรายการคำนวน")
        
        # ยุบรวมเหลือปุ่มเดียว: ประมวลผล สร้างไฟล์ และเก็บลงคิวในคลิกเดียว
        if st.button("📥 ประมวลผลและเก็บลงตะกร้า (Generate & Add to Queue)", type="primary", use_container_width=True):
            
            # 1. บันทึกรูปและคำนวณค่าต่างๆ ก่อน
            fig.savefig(img_path, bbox_inches='tight', dpi=300)
            Vs_req = calc.get_stirrup_req(Vu, phi_Vc, b, d, C, Fv, dia_v)[2] if spacing_mode == "ให้โปรแกรมจัดให้ (@)" else calc.check_custom_stirrup(Vu, phi_Vc, b, d, C, Fv, dia_v, spacing)[2]
            
            # 2. สร้างไฟล์ PDF 
            pdf_bytes = pdf_report.create_pdf(
                b, h, cov, d, C, F, LoMax, MaxP, ASq, n_m_pos, rebar_m_pos, AStu, lotu, 
                calc_m_neg, MaxP_neg, ASq_neg, n_m_neg, rebar_m_neg, AStu_neg, lotu_neg, 
                Vu, phi_Vc, Vs_req, rebar_v, spacing, es, ey, img_path
            )
            
            # 3. นำข้อมูลเก็บลงตะกร้า
            doc_name = f"Beam_Report_{st.session_state.get('project_name', 'Doc')}_{b}x{h}.pdf"
            
            st.session_state.pdf_queue.append({
                "id": len(st.session_state.pdf_queue) + 1,
                "name": doc_name,
                "bytes": pdf_bytes  # ตอนนี้มีข้อมูลส่งมาแล้ว ไม่ Error แน่นอน!
            })
            
            st.success(f"✅ สร้างรายงานและนำ '{doc_name}' เก็บลงตะกร้าเรียบร้อย! ไปที่แท็บ PDF Manager เพื่อรวมไฟล์ได้เลย")

        st.markdown("---")
        st.subheader("💾 7. บันทึกคานนี้เก็บเข้าคลัง")
        default_b_name = selected_beam_opt if selected_beam_opt != "+ ออกแบบคานใหม่ / เพิ่มประเภทคาน" else "B1"
        save_name = st.text_input("ตั้งชื่อเรียกคานตัวนี้ (เช่น B1, B2, GB1):", value=default_b_name)
        
        if st.button(f"💾 บันทึกสเปคคาน [{save_name}] เข้าคลังตึก", use_container_width=True):
            # บันทึกข้อมูลคานโดยเก็บชุดตัวแปร M- ลงไปด้วย เพื่อให้อัปเดตเชื่อมโยงกันครบวงจร
            st.session_state.beam_library[save_name] = {
                "b": b, "h": h, "cover": cov, "fc": C, "fy_label": fy_sel,
                "calc_m_neg": calc_m_neg, "MaxP_neg": MaxP_neg, "rebar_m_neg": rebar_m_neg, "n_m_neg": n_m_neg,
                "MaxP": MaxP, "rebar_m_pos": rebar_m_pos, "n_m_pos": n_m_pos,
                "VMax": VMax, "rebar_v": rebar_v, "spacing": spacing
            }
            st.success(f"✅ บันทึกสเปคคาน {save_name} เข้าคลังโปรเจกต์สำเร็จแล้ว!")
            st.rerun()