from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Con RC Beam Design Sheet', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(5)

def create_pdf(b, h, cov, d, C, F, LoMax, MaxP, ASq, n_m_pos, rebar_m_pos, AStu, lotu, calc_m_neg, MaxP_neg, ASq_neg, n_m_neg, rebar_m_neg, AStu_neg, lotu_neg, Vu,phi_Vc, Vs_req, rebar_v, spacing, es, ey, img_path):
    pdf = PDF()
    pdf.add_page()
    left_w = 110 
    
    # 1. Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(left_w, 8, '1. Section and Material Properties', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(left_w, 7, f'Width (b) = {b:.0f} cm, Total Depth (h) = {h:.0f} cm', 0, 1)
    pdf.cell(left_w, 7, f'Covering = {cov:.1f} cm, Effective Depth (d) = {d:.0f} cm', 0, 1)
    pdf.cell(left_w, 7, f'Concrete (fc) = {C:.0f} ksc, Yield (fy) = {F:.0f} ksc', 0, 1)
    pdf.cell(left_w, 7, f'Rho_max = {LoMax:.4f}', 0, 1)
    pdf.ln(5)

    # 2. M+
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(left_w, 8, '2. Positive Moment Design (M+)', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(left_w, 7, f'Design Moment (Mmax+) = {MaxP:.3f} Ton-m', 0, 1)
    pdf.cell(left_w, 7, f'Required As = {ASq:.3f} sq.cm', 0, 1)
    pdf.cell(left_w, 7, f'Provided = {n_m_pos:.0f}-{rebar_m_pos} (As = {AStu:.2f} sq.cm)', 0, 1)
    
    if AStu >= ASq and lotu <= LoMax:
        pdf.set_text_color(0, 100, 0)
        pdf.cell(left_w, 7, f'Check: OK!', 0, 1)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(left_w, 7, f'Check: NOT OK!', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # 3. M-
    if calc_m_neg:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(left_w, 8, '3. Negative Moment Design (M-)', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(left_w, 7, f'Design Moment (Mmax-) = {MaxP_neg:.3f} Ton-m', 0, 1)
        pdf.cell(left_w, 7, f'Required As = {ASq_neg:.3f} sq.cm', 0, 1)
        pdf.cell(left_w, 7, f'Provided = {n_m_neg:.0f}-{rebar_m_neg} (As = {AStu_neg:.2f} sq.cm)', 0, 1)
        
        if AStu_neg >= ASq_neg and lotu_neg <= LoMax:
            pdf.set_text_color(0, 100, 0)
            pdf.cell(left_w, 7, f'Check: OK!', 0, 1)
        else:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(left_w, 7, f'Check: NOT OK!', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # 4. Shear
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(left_w, 8, '4. Shear Design', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(left_w, 7, f'Ultimate Shear (Vu) = {Vu:.2f} kg', 0, 1)
    pdf.cell(left_w, 7, f'Concrete Capacity (phi Vc) = {phi_Vc:.2f} kg', 0, 1)
    if Vs_req > 0:
        pdf.cell(left_w, 7, f'Req. Stirrup Force (Vs req) = {Vs_req:.2f} kg', 0, 1)
    pdf.cell(left_w, 7, f'Stirrup Provided = {rebar_v} @ {spacing:.0f} cm', 0, 1)
    pdf.ln(5)
    
    # 5. Yield
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(left_w, 8, '5. Yield Check', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(left_w, 7, f'Strain (Es) = {es:.5f}, Yield (Ey) = {ey:.5f}', 0, 1)
    if es >= ey:
        pdf.set_text_color(0, 100, 0)
        pdf.cell(left_w, 7, 'Result: Tension Controlled -> OK!', 0, 1)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(left_w, 7, 'Result: Compression Controlled -> NOT OK!', 0, 1)

    if os.path.exists(img_path):
        pdf.image(img_path, x=130, y=40, w=75)

    temp_pdf_name = "Temp_Report.pdf"
    pdf.output(temp_pdf_name)
    with open(temp_pdf_name, "rb") as f:
        pdf_bytes = f.read()
        
    return pdf_bytes