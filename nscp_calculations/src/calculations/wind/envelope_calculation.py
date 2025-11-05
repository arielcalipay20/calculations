# ----------------------------
# Helper Functions
# ----------------------------
def get_Kz(exposure: str, z: float) -> float:
    """Compute Kz based on exposure category and height."""
    if z < 5:
        z = 5.0
    if exposure == "B":
        return round(2.01 * (z / 9.14) ** 0.15, 3)
    elif exposure == "C":
        return round(2.01 * (z / 9.14) ** 0.20, 3)
    elif exposure == "D":
        return round(2.01 * (z / 9.14) ** 0.25, 3)
    return 0.85


def calculate_qz(V: float, Kz: float, Kzt: float, Kd: float, I: float) -> float:
    """Calculate velocity pressure qz per NSCP 2015."""
    return 0.613 * Kz * Kzt * Kd * (V ** 2) * I


def calculate_pressure(qz: float, G: float, Cp: float, GCpi: float) -> tuple:
    """Return positive and negative design pressures (N/m²)."""
    p_pos = qz * (G * Cp - GCpi)
    p_neg = qz * (G * Cp + GCpi)
    return p_pos, p_neg