
# ----------------------------
# Helper Functions
# ----------------------------
def get_Kz(exposure: str, z: float) -> float:
    """Compute Kz based on NSCP exposure category and height."""
    if z < 5:  # below 5m, assume minimum
        z = 5.0

    if exposure == "B":
        # Urban/suburban terrain
        return round(2.01 * (z / 9.14) ** 0.15, 3)
    elif exposure == "C":
        # Open terrain
        return round(2.01 * (z / 9.14) ** 0.20, 3)
    elif exposure == "D":
        # Flat, unobstructed coastal
        return round(2.01 * (z / 9.14) ** 0.25, 3)
    else:
        return 0.85  # default
