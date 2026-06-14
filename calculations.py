import math

def get_basic_props(b, h, cov, C, F):
    """คำนวณคุณสมบัติเบื้องต้นของหน้าตัด"""
    d = h - cov
    dt = d / 100
    chk = (b / 100) * (h / 100) * 2400
    bat = 0.85
    Lol = 0.85 * bat * (C / F) * (6120 / (6120 + F))
    LoMax = 0.75 * Lol
    return d, dt, chk, LoMax

def get_rho_req(moment, F, C, b, d):
    """คำนวณหาค่า Rho ขั้นต่ำที่ต้องการ"""
    if moment <= 0:
        return 0.0
    R = (100 * moment) / (0.9 * b * d**2)
    calc_lo = 14 / F
    m = F / (0.85 * C)
    Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
    while Rn < R:
        calc_lo += 0.0005
        Rn = calc_lo * F * (1 - (0.5 * calc_lo * m))
        if calc_lo > 0.05: # เบรกฉุกเฉิน
            break
    return calc_lo

def get_provided_steel(dia, n, b, d):
    """คำนวณพื้นที่เหล็กที่จัดให้จริง (As Provided)"""
    AStu = n * (math.pi * (dia / 10)**2 / 4)
    if d > 0:
        lotu = AStu / (b * d)
    else:
        lotu = 0.0
    return AStu, lotu

def get_shear(VMax, Len, d, C, b):
    """คำนวณแรงเฉือน Vu และ Vc"""
    dt = d / 100
    if Len > 0:
        Vu = (VMax / Len) * (Len - dt)
    else:
        Vu = 0.0
    Vc = 0.85 * 0.53 * math.sqrt(C) * b * d
    return Vu, Vc

def get_yield(AStu, F, C, b, d):
    """ตรวจสอบสถานะการครากของเหล็ก (Yield Check)"""
    if AStu <= 0:
        return 0.0, 0.0
    aa = (AStu * F) / (0.85 * C * b)
    x = aa / 0.85
    if x > 0:
        es = (0.003 * (d - x)) / x
    else:
        es = 0.0
    ey = F / (2.04 * 10**6)
    return es, ey