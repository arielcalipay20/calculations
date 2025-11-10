
# ----------------------------
# Helper functions
# ----------------------------
def get_Kz(exposure: str, h: float) -> float:
    """Estimate Kz based on exposure category and height."""
    if exposure == "B":
        return 0.7 + 0.0004 * h
    elif exposure == "C":
        return 0.85 + 0.0006 * h
    elif exposure == "D":
        return 1.03 + 0.0007 * h
    return 1.0

def calculate_qz(V: float, Kz: float, Kzt: float, Kd: float, I: float) -> float:
    """Velocity pressure q_z (N/m²)."""
    return 0.613 * Kz * Kzt * Kd * (V ** 2) * I

def calculate_p_other(qz: float, G: float, Cp: float, GCpi: float) -> (float, float):
    """Compute design pressures for other structures: positive & negative."""
    p_pos = qz * (G * Cp - GCpi)
    p_neg = qz * (G * Cp + GCpi)
    return p_pos, p_neg
