import numpy as np
import matplotlib.pyplot as plt


def read_text_response(path):
    # 0     x: [m],
    # 1     y: [m],
    # 2     cos_x: [1], x
    # 3     cos_y: [1], y
    # 4     wavelength: [m]
    # 5     arrival_time: [s]
    # 6     simulation_truth_id [1]
    response = np.genfromtxt(path)
    return {
        'x': response[:,0],
        'y': response[:,1],
        'arrival_time': response[:,5],
        'number_of_photons': response.shape[0]}


def read_binary_response(path):
    # 0 simulation_truth_id
    # 1 wavelength
    # 2 arrival_time
    # 3 x_intersect
    # 4 y_intersect
    # 5 theta_x
    # 6 theta_y
    raw = np.fromfile(path, dtype=np.float32)
    phs = raw.reshape([raw.shape[0]//7, 7])
    return {
        'x': phs[:,3],
        'y': phs[:,4],
        'arrival_time': phs[:,2],
        'number_of_photons': phs.shape[0]}


def make_image_from_sensor_response(reflector, sensor_response, analysis_config):
    focal_length = reflector['geometry'].focal_length
    theta_x = 1e3*np.rad2deg(np.arctan(sensor_response['x']/focal_length))
    theta_y = 1e3*np.rad2deg(np.arctan(sensor_response['y']/focal_length))

    bin_width = 1e3*analysis_config['sensor']['bin_width_deg']
    roi = 1e3*analysis_config['sensor']['region_of_interest_deg']

    number_of_bins = int(roi/bin_width)
    roi = bin_width*number_of_bins
    bins = np.linspace(
        -0.5*roi,
        +0.5*roi,
        number_of_bins)
    image = np.histogram2d(
        x=theta_x,
        y=theta_y,
        bins=[bins, bins]
    )[0]
    return {
        'histogram': image,
        'bins': bins,
        'unit': 'mdeg'
    }


def make_image_from_ground_response(reflector, ground_response, analysis_config):
    reflector_radius = reflector['geometry'].max_outer_radius*1.25
    bin_width = analysis_config['ground']['bin_width_m']
    number_of_bins = int((2.0*reflector_radius)/bin_width)
    reflector_radius = 0.5*bin_width*number_of_bins
    bins = np.linspace(
        -reflector_radius,
        +reflector_radius,
        number_of_bins)
    image = np.histogram2d(
        x=ground_response['x'],
        y=ground_response['y'],
        bins=bins
    )[0]
    return {
        'histogram': image,
        'bins': bins,
        'unit': 'm'
    }


def add2ax_image(ax, image):
    bins = image['bins']
    im = ax.matshow(
        image['histogram'],
        interpolation='none',
        origin='low',
        extent=[bins[0], bins[-1], bins[0], bins[-1]],
        aspect='equal')
    im.set_cmap('viridis')
    ax.set_xlabel('x/'+image['unit'])
    ax.set_ylabel('y/'+image['unit'])


def plot_image(image):
    plt.figure()
    ax = plt.gca()
    add2ax_image(ax, image)
    plt.show()


def save_image(image, path):
    plt.figure(figsize=(10, 10))
    ax = plt.gca()
    add2ax_image(ax, image)
    plt.savefig(path, dpi=384//2)


def stddev_of_point_spread_function(sensor_response):
    """
    Returns the optical quality parameter of a point spread function found in a 
    sensor response.
    """
    x_stddev = sensor_response['x'].std()
    y_stddev = sensor_response['y'].std()
    return np.hypot(x_stddev, y_stddev)