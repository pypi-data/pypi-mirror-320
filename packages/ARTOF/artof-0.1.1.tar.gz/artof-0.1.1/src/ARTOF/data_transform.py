import numpy as np
from scipy.interpolate import RectBivariateSpline

def transform(raw_data, metadata, load_as, x0=None, y0=None, t0=None):
    """
    Transform raw data to desired representation.

    Args:
        raw_data (list): 2D list of raw data points (x, y, t ticks).
        metadata (@dataclass Metadata): Metadata class containing all metadata for current measurement.
        load_as (str): Desired representation to transform to (options: 'raw', 'raw_SI', 'cylindrical', 'spherical').
        x0 (int, optional): x offset in ticks (default: from the acquisition.cfg file).
        t0 (int, optional): y offset in ticks (default: from the acquisition.cfg file).
        t0 (int, optional): t offset in ticks (default: from the acquisition.cfg file).

    Returns:
        list, list, list: 3 lists: 2D list of transformed data, list of variable names, and list of default bin edges for given transformation.
    """
    match load_as:
        case 'raw':
            return raw_data, ['x_ticks', 'y_ticks', 't_ticks'], [[-1500, 1500, 101], [-1500, 1500, 101],[12000, 18000, 201]]
        case 'raw_SI':
            x, y, t = ticks_to_SI(raw_data, metadata, x0, y0, t0)

            data = np.stack([x, y, t], -1)
            return data, ['x_m', 'y_m', 't_s'], [[-0.027, 0.027, 101], [-0.027, 0.027, 101],[0.3e-6, .4e-6, 201]]
        case 'cylindrical':
            x, y, t = ticks_to_SI(raw_data, metadata, x0, y0, t0)
            r, phi = xy_to_polar(x,y)

            data = np.stack([r, phi, t], -1)
            return data, ['r_m', 'phi_rad', 't_s'], [[0, 0.027, 101], [-np.pi, np.pi, 201],[0.3e-6, .4e-6, 201]]
        case 'spherical':
            x, y, t = ticks_to_SI(raw_data, metadata, x0, y0, t0)
            r, phi = xy_to_polar(x,y)
            E, theta = tr_to_Etheta(t, r, metadata)

            data = np.stack([E, phi, theta],-1)
            begin_energy, end_energy = metadata.general.spectrumBeginEnergy, metadata.general.spectrumEndEnergy
            theta_max = metadata.lensmode.maxTheta
            return data, ['E_eV', 'phi_rad', 'theta_rad'], [[begin_energy, end_energy, 101], [-np.pi, np.pi, 201],[0, theta_max, 201]] 
        case _:
            print(f'Did not recognize transformation of type {load_as}. Using raw data')
            return raw_data, ['x_ticks', 'y_ticks', 't_ticks'], [[-1500, 1500, 101], [-1500, 1500, 101],[12000, 18000, 201]]

def ticks_to_SI(raw_data, metadata, x0=None, y0=None, t0=None):
    """
    Transform x, y, and t from ticks to SI units using transformation matrices and tdcResolution from acquisition.cfg file.

    Args:
        raw_data (list): 2D list of raw data points (x, y, t ticks).
        metadata (@dataclass Metadata): Metadata class containing all metadata for current measurement.
        x0 (int, optional): x offset in ticks (default: from the acquisition.cfg file).
        t0 (int, optional): y offset in ticks (default: from the acquisition.cfg file).
        t0 (int, optional): t offset in ticks (default: from the acquisition.cfg file).

    Returns:
        list, list, list: 3 lists containing x, y, and t values in SI units.
    """
    # convert x and y ticks to radius in m and phi in radians
    detector = metadata.detector
    x0 = detector.x0 if x0 is None else x0
    y0 = detector.y0 if y0 is None else y0
    x = matrix_transform(raw_data[:,0], raw_data[:,1], x0, y0, detector.transformXVector, detector.transformYVector, detector.transformXMatrix)
    y = matrix_transform(raw_data[:,0], raw_data[:,1], x0, y0, detector.transformXVector, detector.transformYVector, detector.transformYMatrix)

    # transform time ticks to time in seconds
    t0 = detector.t0 if t0 is None else t0
    t = transform_time(raw_data[:,2], t0, detector.tdcResolution)

    return x, y, t

def xy_to_polar(x, y):
    """
    Transform x and y in SI units to polar coordinates. The function arctan2(y, x) is used.

    Args:
        x (float): x value in meters (SI).
        y (float): y value in meters (SI).

    Returns:
        float, float: r in meters and phi in radians.
    """
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return r, phi

def tr_to_Etheta(t, r, metadata):
    """
    Transform t and r in SI units to E and theta. The transformation matrices from the acquisition.cfg file are used.

    Args:
        t (float): Time of flight values in seconds (SI).
        r (float): Radius in meters (SI).
        metadata (@dataclass Metadata): Metadata class containing all metadata for current measurement.

    Returns:
        float, float: E in eV and theta in radians.
    """
    lensmode = metadata.lensmode
    # scale energy matrix and tof vector with energy scale centerEnergy/eKinRef
    energy_scale = metadata.general.centerEnergy/lensmode.eKinRef
    t_vector = lensmode.tofVector/np.sqrt(energy_scale)
    r_vector = lensmode.radiusVector
    energy_matrix = lensmode.energyMatrix*energy_scale
    theta_matrix = lensmode.thetaMatrix

    E = matrix_transform(t, r, 0, 0, t_vector, r_vector, energy_matrix)
    theta = matrix_transform(t, r, 0, 0, t_vector, r_vector, theta_matrix)
    return E, theta

def transform_time(t_ticks, t0, tdcResolution):
    """
    Transform time from ticks to seconds.

    Args:
        t_ticks (int): Time in ticks.
        t0 (int): Time offset in ticks.
        tdcResolution (float): Resolutions of time to digital converter (tdc); number of events per second.

    Returns:
        float: Time in seconds.
    """
    return (t_ticks - t0) * 1 / tdcResolution 

def matrix_transform(p1, p2, p1_0, p2_0, p1_vec, p2_vec, trans_mat):
    """
    Transform 2D data point using a given matrix using interpolation through a bivariate spline.

    Args:
        p1 (int): First component of data point.
        p2 (int): Second component of data point.
        p1_0 (int): Offset of p1.
        p2_0 (int): Offset of p2.
        p1_vec (list): Vector corresponding to p1 and the columns of the matrix.
        p2_vec (list): Vector corresponding to p2 and the rows of the matrix.
        trans_mat (list): 2D list representing the transformation matrix.

    Returns:
        list: 2D data point after transformation.
    """
    interp = RectBivariateSpline(p2_vec-p2_0, p1_vec-p1_0, trans_mat)
    return interp.ev(p2, p1)
