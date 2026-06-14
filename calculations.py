import math

def get_basic_props(b, h, cov, C, F):
    d = h - cov
    dt = d / 100
    chk = (b / 100) * (h / 100) * 2400
    bat = 0.85
    Lol = 0.85 * bat * (C / F) * (6120 / (6120 + F))
    LoMax = 0.75 * Lol
    return d, dt, chk, LoMax

def get_rho_req(moment, F, C, b, d):
    if moment <= 0: return 0.0
    R = (100 * moment) / (0.9 * b * d**2)
    calc_lo = 14 / F
    m = F / (0.85 * C)
    Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
    while Rn < R:
        calc_lo += 0.0005
        Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
        if calc_lo > 0.05: break
    return calc_lo

def get_provided_steel(dia, n, b, d):
    AStu = n * (math.pi * (dia / 10)**2 / 4)
    lotu = AStu / (b * d) if d > 0 else 0.0
    return AStu, lotu

def get_shear_concrete(d, C, b):
    # คืนค่าเป็นกำลังที่คอนกรีตรับได้หลังคูณเซฟตี้ (phi Vc)
    return 0.85 * 0.53 * math.sqrt(C) * b * d

def get_stirrup_req(Vu, phi_Vc, b, d, C, Fv, dia_v):
    """กรณีให้โปรแกรมคำนวณระยะแอด (@) ให้"""
    phi = 0.85
    Av = 2 * (math.pi * (dia_v / 10)**2 / 4)
    Vs_max_limit = 2.12 * math.sqrt(C) * b * d
    Vs_req = (Vu - phi_Vc) / phi if Vu > phi_Vc else 0.0
    
    if Vu > phi_Vc + (phi * Vs_max_limit):
        return "หน้าตัดเล็กเกินไป (Vu มากเกินขีดจำกัด)", 0.0, Vs_req
        
    if Vu <= phi_Vc / 2:
        s_calc = min(d / 2, 60.0) 
        status = "คอนกรีตรับไหว (ใส่เหล็กปลอกกันร้าว)"
    else:
        if Vu <= phi_Vc:
            s_calc = (Av * Fv) / (3.5 * b)
            status = "ใช้เหล็กปลอกขั้นต่ำ (Minimum Shear Rebar)"
        else:
            s_calc = (Av * Fv * d) / Vs_req
            status = "จัดเหล็กปลอกเพื่อรับแรงเฉือน"
            
    if Vu > phi_Vc and Vs_req > 1.06 * math.sqrt(C) * b * d:
        s_max = min(d / 4, 30.0)
    else:
        s_max = min(d / 2, 60.0)
        
    s_final = math.floor(min(s_calc, s_max))
    return status, s_final, Vs_req

def check_custom_stirrup(Vu, phi_Vc, b, d, C, Fv, dia_v, s_custom):
    """กรณีผู้ใช้งานกำหนดระยะแอด (@) เองเพื่อตรวจเช็ค"""
    phi = 0.85
    Av = 2 * (math.pi * (dia_v / 10)**2 / 4)
    Vs_max_limit = 2.12 * math.sqrt(C) * b * d
    Vs_req = (Vu - phi_Vc) / phi if Vu > phi_Vc else 0.0
    
    if Vu > phi_Vc + (phi * Vs_max_limit):
        return "หน้าตัดคานระเบิด!", False, Vs_req, 0.0
        
    Vs_prov = (Av * Fv * d) / s_custom if s_custom > 0 else 0.0
    
    if Vu > phi_Vc and Vs_req > 1.06 * math.sqrt(C) * b * d:
        s_max = min(d / 4, 30.0)
    else:
        s_max = min(d / 2, 60.0)
        
    if Vs_prov < Vs_req:
        return f"เหล็กปลอกรับแรงไม่พอ!", False, Vs_req, Vs_prov
    if s_custom > s_max:
        return f"ระยะแอดห่างเกินไป (ห้ามเกิน {s_max:.0f} cm)", False, Vs_req, Vs_prov
        
    return "ระยะแอดปลอดภัย", True, Vs_req, Vs_prov

def get_yield(AStu, F, C, b, d):
    if AStu <= 0: return 0.0, 0.0
    aa = (AStu * F) / (0.85 * C * b)
    x = aa / 0.85
    es = (0.003 * (d - x)) / x if x > 0 else 0.0
    ey = F / (2.04 * 10**6)
    return es, ey