# diesel.py
import numpy as np

# =======================
# Constantes físicas
# =======================
R = 287.0
k = 1.35  
cv = R / (k - 1)

def ciclo_diesel_ideal(P1, T1, r, rc, V_total, Ncyl):
    """
    Ciclo Diesel: combustão a pressão constante
    r: taxa de compressão
    rc: razão de corte (cutoff ratio) - quanto o volume aumenta na combustão
    """
    Vd = (V_total / 1000) / Ncyl
    Vc = Vd / (r - 1)
    V1 = Vd + Vc
    V2 = Vc
    V3 = V2 * rc  # Volume aumenta durante combustão!
    
    m = (P1 * V1) / (R * T1)
    
    # Compressão adiabática (1->2)
    T2 = T1 * r**(k-1)
    P2 = P1 * r**k
    
    # Combustão a PRESSÃO CONSTANTE (2->3)
    P3 = P2  # Pressão constante!
    T3 = T2 * rc
    
    # Expansão adiabática (3->4)
    r_exp = V1 / V3
    T4 = T3 / r_exp**(k-1)
    P4 = P3 / r_exp**k
    
    # Calor e trabalho
    cp = k * cv
    Qin = m * cp * (T3 - T2)  
    Qout = m * cv * (T4 - T1)
    W = Qin - Qout
    
    # Eficiência Diesel
    eta = 1 - (1/r**(k-1)) * ((rc**k - 1)/(k * (rc - 1)))
    
    estados = {
        "1": (P1, V1, T1),
        "2": (P2, V2, T2),
        "3": (P3, V3, T3),
        "4": (P4, V1, T4)
    }
    
    return estados, Qin, Qout, W, eta, rc


def gerar_curvas_diesel(estados, rc):
    """Gera curvas P-V e T para o ciclo Diesel"""
    P1, V1, T1 = estados["1"]
    P2, V2, T2 = estados["2"]
    P3, V3, T3 = estados["3"]
    P4, _, T4 = estados["4"]
    
    k = 1.35
    
    # Admissão
    v_adm = np.linspace(V1*0.3, V1, 20)
    p_adm = np.full_like(v_adm, P1)
    t_adm = np.full_like(v_adm, T1)
    
    # Compressão (1->2)
    v12 = np.linspace(V1, V2, 50)
    p12 = P1 * (V1 / v12) ** k
    t12 = T1 * (V1 / v12) ** (k - 1)
    
    # Combustão a PRESSÃO CONSTANTE (2->3)
    v23 = np.linspace(V2, V3, 30)
    p23 = np.full_like(v23, P2)  # Pressão constante!
    t23 = np.linspace(T2, T3, 30)
    
    # Expansão (3->4)
    v34 = np.linspace(V3, V1, 50)
    p34 = P3 * (V3 / v34) ** k
    t34 = T3 * (V3 / v34) ** (k - 1)
    
    # Exaustão
    v_exh = np.full(20, V1)
    p_exh = np.linspace(P4, P1, 20)
    t_exh = np.linspace(T4, T1, 20)
    
    v = np.concatenate([v_adm, v12, v23, v34, v_exh])
    p = np.concatenate([p_adm, p12, p23, p34, p_exh])
    T = np.concatenate([t_adm, t12, t23, t34, t_exh])
    
    return v, p, T
