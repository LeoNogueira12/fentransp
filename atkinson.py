# atkinson.py
import numpy as np

# =======================
# Constantes físicas
# =======================
R = 287.0
gamma = 1.4
cv = R / (gamma - 1)

def ciclo_atkinson_ideal(P1, T1, r_comp, r_exp, alpha, V_total, Ncyl):
    """
    Ciclo Atkinson: expansão maior que compressão
    r_comp: taxa de compressão real
    r_exp: taxa de expansão (maior que r_comp)
    """
    Vd = (V_total / 1000) / Ncyl
    Vc = Vd / (r_comp - 1)
    V1 = Vd + Vc
    V2 = Vc
    V4 = V1 * (r_exp / r_comp)  # Volume no final da expansão (maior!)
    
    m = (P1 * V1) / (R * T1)
    
    # Compressão (1->2)
    T2 = T1 * r_comp**(gamma-1)
    P2 = P1 * r_comp**gamma
    
    # Combustão (2->3) - volume constante
    # Atkinson usa alpha menor (combustão menos intensa + otimizado para eficiência)
    alpha_atkinson = alpha * 0.82  # 18% menor que Otto
    T3 = alpha_atkinson * T2
    P3 = P2 * alpha_atkinson
    
    # Expansão (3->4) - MAIOR que no Otto!
    T4 = T3 / r_exp**(gamma-1)
    P4 = P3 / r_exp**gamma
    
    # Calor e trabalho
    Qin = m * cv * (T3 - T2)
    Qout = m * cv * (T4 - T1)
    W = Qin - Qout
    
    # Eficiência teórica do Atkinson (CORRIGIDA)
    # η = 1 - (T4 - T1)/(T3 - T2)
    # Simplificando: η = 1 - (1/r_exp^(γ-1))
    eta = 1 - (1 / r_exp**(gamma-1))
    
    # NÃO aplicar perdas extras aqui, o W já reflete a realidade
    
    estados = {
        "1": (P1, V1, T1),
        "2": (P2, V2, T2),
        "3": (P3, V2, T3),
        "4": (P4, V4, T4)
    }
    
    return estados, Qin, Qout, W, eta, r_exp


def gerar_curvas_atkinson(estados, r_comp, r_exp):
    """Gera curvas P-V e T para o ciclo Atkinson"""
    P1, V1, T1 = estados["1"]
    P2, V2, T2 = estados["2"]
    P3, _, T3 = estados["3"]
    P4, V4, T4 = estados["4"]
    
    gamma = 1.4
    
    # Admissão (0->1) - pressão constante
    v_admissao = np.linspace(V4 * 0.3, V1, 30)
    p_admissao = np.full_like(v_admissao, P1)
    t_admissao = np.full_like(v_admissao, T1)
    
    # Compressão (1->2)
    v12 = np.linspace(V1, V2, 50)
    p12 = P1 * (V1 / v12) ** gamma
    t12 = T1 * (V1 / v12) ** (gamma - 1)
    
    # Combustão (2->3) - volume constante
    v23 = np.full(20, V2)
    p23 = np.linspace(P2, P3, 20)
    t23 = np.linspace(T2, T3, 20)
    
    # Expansão (3->4) - MAIOR que compressão
    v34 = np.linspace(V2, V4, 60)
    p34 = P3 * (V2 / v34) ** gamma
    t34 = T3 * (V2 / v34) ** (gamma - 1)
    
    # Exaustão (4->1) - volume constante
    v41 = np.full(20, V4)
    p41 = np.linspace(P4, P1, 20)
    t41 = np.linspace(T4, T1, 20)
    
    # Exaustão final (fechando o ciclo)
    v_exh_final = np.linspace(V4, V4 * 0.3, 20)
    p_exh_final = np.full_like(v_exh_final, P1)
    t_exh_final = np.full_like(v_exh_final, T1)
    
    v = np.concatenate([v_admissao, v12, v23, v34, v41, v_exh_final])
    p = np.concatenate([p_admissao, p12, p23, p34, p41, p_exh_final])
    T = np.concatenate([t_admissao, t12, t23, t34, t41, t_exh_final])
    
    return v, p, T
