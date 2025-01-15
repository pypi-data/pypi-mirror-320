import numpy as np
    
def get_bin_edges(data, bin_config, data_id="unknown"):
    """
    Create bin edges (limits) for given bin config.

    Args:
        data (list): 1D list of data values.
        bin_config (list): Bin config consisting of three values: [bin_min, bin_max, bin_number].
        data_id (str, optional): Identifier to raise error message with identifier.

    Returns:
        list: List of bin edges.
    """
    bin_min, bin_max, bin_number = bin_config
    if type(bin_number) != int:
        raise Exception(f"The number of bins for {data_id} needs given as an int")
    # set min and max if not already given in bin_config
    if bin_min == None:
        bin_min = min(data)
    if bin_max == None:
        # ensuring that the highest values are not omitted
        bin_max = max(data)

    return np.linspace(bin_min, bin_max, bin_number+1)



    
def project_data(data, axes, ranges):
    """
    Plot loaded data in given projection. Projections are possible in 1 or 2 dimensions.

    Args:
        data (list): 3D data to be transformed.
        axes (list): List containing all axes onto which the projection is performed, e.g., [0,1].
        ranges (list): List of ranges for each axis.

    Returns:
        list: 1 or 2D list containing the projection.
    """

    if data is None:
        raise Exception('Load the data before projecting the data.')         
    if len(axes) not in [1,2]:
        raise Exception(f'A projection onto {len(axes)} axes is not possible.')
    
    # determine ranges (None is entire range)
    start_1, end_1 = (0, data.shape[0]) if ranges[0] is None else (ranges[0][0], ranges[0][1])
    start_2, end_2 = (0, data.shape[1]) if ranges[1] is None else (ranges[1][0], ranges[1][1])
    start_3, end_3 = (0, data.shape[2]) if ranges[2] is None else (ranges[2][0], ranges[2][1])

    proj_data = data[start_1:end_1,start_2:end_2,start_3:end_3]
    
    if len(axes) == 2: # project data onto 2 axes
        # determine the projection axis
        proj_axis = 3 - sum(axes)
        # switch order of array if needed
        if axes[0] < axes[1]:
            proj_data = np.swapaxes(proj_data, axes[0], axes[1])
        proj_data = proj_data[:,:,:].sum(axis=proj_axis)
    elif len(axes) == 1: # project data onto 1 axis
        # get axes to project along
        proj_axes = [0,1,2]
        proj_axes.remove(axes[0])
        # project along axes
        proj_data = proj_data.sum(axis=tuple(proj_axes))


    return proj_data