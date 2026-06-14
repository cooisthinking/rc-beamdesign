from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'RC Beam Design Calculation Sheet', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(5)

def create_pdf(b, h, cov, d, C, F, LoMax, MaxP, ASq, n_m_pos, rebar_m_pos, AStu, lotu, calc_m_neg, MaxP_neg, ASq_neg, n_m_neg, rebar_m_neg, AStu_neg, lotu_neg, Vu, Vc, check_yield, es, ey):
    """ฟังก์ชันรับค่าทั้งหมดมาเพื่อวาดลงบนหน้ากระดาษ PDF"""
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

    # เซฟและอ่านไฟล์ส่งกลับไปให้หน้าเว็บ
    temp_pdf_name = "Temp_Report.pdf"
    pdf.output(temp_pdf_name)
    with open(temp_pdf_name, "rb") as f:
        pdf_bytes = f.read()
        
    return pdf_bytes