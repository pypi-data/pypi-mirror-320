import numpy as np
from scipy.interpolate import RectBivariateSpline


class ARTOFTransformer:
    """Class to transform raw artof data"""

    def __init__(self, metadata, x0=None, y0=None, t0=None):
        """Initializer ARTOFTransform class"""
        
        self.x_transform, self.y_transform, self.t_transform = self.ticks_to_SI_transform(metadata, x0, y0, t0)
                
        self.E_transform, self.theta_transform = self.tr_to_Etheta_transform(metadata)

    def transform(self, raw_data, load_as):
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
                data = raw_data
            case 'raw_SI':
                x = self.x_transform.ev(raw_data[:,1], raw_data[:,0])
                y = self.y_transform.ev(raw_data[:,1], raw_data[:,0])
                t = self.t_transform(raw_data[:,2])

                data = np.stack([x, y, t], -1)
            case 'cylindrical':
                x = self.x_transform.ev(raw_data[:,1], raw_data[:,0])
                y = self.y_transform.ev(raw_data[:,1], raw_data[:,0])
                t = self.t_transform(raw_data[:,2])
                r, phi = self.xy_to_polar(x,y)

                data = np.stack([r, phi, t], -1)
            case 'spherical':
                x = self.x_transform.ev(raw_data[:,1], raw_data[:,0])
                y = self.y_transform.ev(raw_data[:,1], raw_data[:,0])
                t = self.t_transform(raw_data[:,2])
                r, phi = self.xy_to_polar(x,y)
                E = self.E_transform.ev(r, t)
                theta = self.theta_transform.ev(r, t)

                data = np.stack([E, phi, theta],-1)
            case _:
                print(f'Did not recognize transformation of type {load_as}. Using raw data')
                data = raw_data
        return data

    def get_axis_and_bins(self, load_as, metadata):
        match load_as:
            case 'raw':
                return ['x_ticks', 'y_ticks', 't_ticks'], [[-1500, 1500, 101], [-1500, 1500, 101],[12000, 18000, 201]]
            case 'raw_SI':
                return ['x_m', 'y_m', 't_s'], [[-0.027, 0.027, 101], [-0.027, 0.027, 101],[0.3e-6, .4e-6, 201]]
            case 'cylindrical':
                return ['r_m', 'phi_rad', 't_s'], [[0, 0.027, 101], [-np.pi, np.pi, 201],[0.3e-6, .4e-6, 201]]
            case 'spherical':
                begin_energy, end_energy = metadata.general.spectrumBeginEnergy, metadata.general.spectrumEndEnergy
                theta_max = metadata.lensmode.maxTheta
                return ['E_eV', 'phi_rad', 'theta_rad'], [[begin_energy, end_energy, 101], [-np.pi, np.pi, 201],[0, theta_max, 201]] 

    def ticks_to_SI_transform(self, metadata, x0=None, y0=None, t0=None):
        """
        Transform x, y, and t from ticks to SI units using transformation matrices and tdcResolution from acquisition.cfg file.

        Args:
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
        x_transform = self.create_matrix_transform(x0, y0, detector.transformXVector, detector.transformYVector, detector.transformXMatrix)
        y_transform = self.create_matrix_transform(x0, y0, detector.transformXVector, detector.transformYVector, detector.transformYMatrix)

        # transform time ticks to time in seconds
        t0 = detector.t0 if t0 is None else t0
        t_transform = lambda t:  self.transform_time(t, t0, detector.tdcResolution)

        return x_transform, y_transform, t_transform


    def xy_to_polar(self, x,y):    
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


    def tr_to_Etheta_transform(self, metadata):
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

        E = self.create_matrix_transform(0, 0, t_vector, r_vector, energy_matrix)
        theta = self.create_matrix_transform(0, 0, t_vector, r_vector, theta_matrix)
        return E, theta


    def transform_time(self, t_ticks, t0, tdcResolution):
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


    def create_matrix_transform(self, p1_0, p2_0, p1_vec, p2_vec, trans_mat):
        """
        Transform 2D data point using a given matrix using interpolation through a bivariate spline.

        Args:
            p1_0 (int): Offset of p1.
            p2_0 (int): Offset of p2.
            p1_vec (list): Vector corresponding to p1 and the columns of the matrix.
            p2_vec (list): Vector corresponding to p2 and the rows of the matrix.
            trans_mat (list): 2D list representing the transformation matrix.

        Returns:
            RectBivariateSpline: Interpolation for given matrix.
        """
        interp = RectBivariateSpline(p2_vec-p2_0, p1_vec-p1_0, trans_mat)
        return interp