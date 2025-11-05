# ----------------------------
# Calculation Functions
# ----------------------------
def get_seismic_coefficients(Z: float, Na: float, Nv: float, Ca: float, Cv: float,
                             I: float, R: float, W: float, T: float) -> float:
    """
    Simplified base-shear computation per NSCP §208.
    V = (C_v I / R) × W for period T ≤ T_a
    Or V ≤ (2.5 C_a I) W (upper bound) for certain conditions. :contentReference[oaicite:2]{index=2}
    """
    V1 = (Cv * I / R) * W
    V2 = 2.5 * Ca * I * W
    return min(V1, V2)

def vertical_distribution(V: float, W_floors: list, h_floors: list) -> list:
    """
    Distribute base shear V vertically: F_i = V × (W_i h_i / Σ(W_j h_j))
    Reference NSCP §208.6.1. :contentReference[oaicite:3]{index=3}
    """
    sum_WH = sum(w*h for w, h in zip(W_floors, h_floors))
    results = []
    for w, h in zip(W_floors, h_floors):
        F_i = V * (w * h / sum_WH)
        results.append(F_i)
    return results