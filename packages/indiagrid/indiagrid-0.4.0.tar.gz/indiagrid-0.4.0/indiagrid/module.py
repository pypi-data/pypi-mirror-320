import math

# Utility function to pad a number to 7 digits, ensuring it is rounded to the nearest integer.
def pad(num):
    return str(int(round(num))).zfill(7)

# Converts from degrees to radians.
def radians(degrees):
    return degrees * math.pi / 180

# Converts from radians to degrees.
def degrees(radians):
    return radians * 180 / math.pi

# Converts latitude and longitude in WGS84 to the Indian grid system.
def wgs84_to_igs(lat, lon, esterr=0, ntherr=0):
    """
    Converts WGS84 coordinates (latitude, longitude) to the Indian Grid System.

    Parameters:
        lat (float): Latitude in decimal degrees.
        lon (float): Longitude in decimal degrees.
        esterr (float): Optional easting error adjustment.
        ntherr (float): Optional northing error adjustment.

    Returns:
        dict: A dictionary containing:
            - 'Easting': Easting coordinate in the Indian grid system.
            - 'Northing': Northing coordinate in the Indian grid system.
            - 'Grid': The grid region (e.g., 'I', 'IIA', etc.).
    """
    # Convert latitude and longitude to radians.
    si = radians(lat)
    lamda = radians(lon)

    # Indian grid system constants.
    FE = 2743195.5  # False Easting
    FN = 914398.5   # False Northing
    k0 = 0.99878641 # Scale factor
    a = 6377301.243 # Semi-major axis of the ellipsoid
    f = 1 / 300.8017 # Flattening
    e = math.sqrt(2 * f - f * f) # Eccentricity

    # Determine grid zone and central meridian based on latitude and longitude.
    if 28 <= lat <= 35.55 and 70.33 <= lon <= 97.45:
        si0 = radians(32.5)
        lamda0 = radians(68.0)
        InGrid = "I"
    elif 21 <= lat < 28 and 68.1 <= lon <= 82:
        si0 = radians(26.0)
        lamda0 = radians(74.0)
        InGrid = "IIA"
    elif 21 <= lat <= 29.33 and 82 < lon <= 97.45:
        si0 = radians(26.0)
        lamda0 = radians(90.0)
        InGrid = "IIB"
    elif 8 <= lat <= 15 and 73.9 <= lon <= 80.4:
        si0 = radians(12.0)
        lamda0 = radians(80.0)
        InGrid = "IVA"
    elif 15 < lat < 21:
        si0 = radians(19.0)
        lamda0 = radians(80.0)
        InGrid = "IIIA"
    else:
        # Raise an error if coordinates are out of bounds.
        raise ValueError("Coordinates out of bounds. Provide latitudes between 8 and 35.55 and longitudes between 70.33 and 97.45.")

    # Intermediate calculations for grid conversion.
    n = math.sin(si0)
    m0 = math.cos(si0) / math.sqrt(1 - e * e * n**2)
    t0 = math.tan(math.pi / 4 - si0 / 2) / ((1 - e * n) / (1 + e * n))**(e / 2)
    t1 = math.tan(math.pi / 4 - si / 2) / ((1 - e * math.sin(si)) / (1 + e * math.sin(si)))**(e / 2)
    F = m0 / (n * t0**n)
    theta = n * (lamda - lamda0)

    # Compute radial distances and final coordinates.
    r0 = a * F * t0**n * k0
    r = a * F * t1**n * k0

    # Calculate Easting and Northing, incorporating errors if provided.
    E = FE + r * math.sin(theta) + esterr
    N = FN + r0 - r * math.cos(theta) + ntherr

    return {"Easting": round(E,2), "Northing": round(N,2), "Grid": InGrid}

# Converts Indian grid system coordinates back to WGS84 latitude and longitude.
def igs_to_wgs84(Eth, Nth, grid, esterr=0, ntherr=0):
    """
    Converts Indian grid system coordinates to WGS84 (latitude, longitude).

    Parameters:
        Eth (float): Easting in the Indian grid system.
        Nth (float): Northing in the Indian grid system.
        grid (str): The grid region (e.g., 'I', 'IIA', etc.).
        esterr (float): Optional easting error adjustment.
        ntherr (float): Optional northing error adjustment.

    Returns:
        dict: A dictionary containing:
            - 'latitude': Latitude in decimal degrees.
            - 'longitude': Longitude in decimal degrees.
    """
    # Constants for the Indian grid system.
    FE = 2743195.5  # False Easting
    FN = 914398.5   # False Northing
    k0 = 0.99878641 # Scale factor
    a = 6377301.243 # Semi-major axis
    f = 1 / 300.8017 # Flattening
    e = math.sqrt(2 * f - f * f) # Eccentricity

    # Determine the central meridian for the specified grid.
    if grid == "I":
        si0 = radians(32.5)
        lamda0 = radians(68.0)
    elif grid == "IIA":
        si0 = radians(26.0)
        lamda0 = radians(74.0)
    elif grid == "IIB":
        si0 = radians(26.0)
        lamda0 = radians(90.0)
    elif grid == "IVA":
        si0 = radians(12.0)
        lamda0 = radians(80.0)
    elif grid == "IIIA":
        si0 = radians(19.0)
        lamda0 = radians(80.0)
    else:
        raise ValueError("Invalid grid type. Use one of: 'I', 'IIA', 'IIB', 'IVA', 'IIIA'.")

    # Adjust coordinates for provided errors.
    N = Nth - ntherr
    E = Eth - esterr

    # Intermediate calculations for reverse conversion.
    n = math.sin(si0)
    m0 = math.cos(si0) / math.sqrt(1 - e * e * n**2)
    t0 = math.tan(math.pi / 4 - si0 / 2) / ((1 - e * n) / (1 + e * n))**(e / 2)
    F = m0 / (n * t0**n)
    r0 = a * F * t0**n * k0

    thetaP = math.atan((E - FE) / (r0 - (N - FN)))
    rP = math.sqrt((E - FE)**2 + (r0 - (N - FN))**2)
    if rP * n < 0:
        rP = -rP

    tP = (rP / (a * k0 * F))**(1 / n)
    latx = math.pi / 2 - 2 * math.atan(tP)
    
    # Perform iterative refinement of latitude for convergence.
    for _ in range(7):
        latx = math.pi / 2 - 2 * math.atan(tP * ((1 - e * math.sin(latx)) / (1 + e * math.sin(latx)))**(e / 2))

    lon = thetaP / n + lamda0

    return {"latitude": degrees(latx), "longitude": degrees(lon)}
