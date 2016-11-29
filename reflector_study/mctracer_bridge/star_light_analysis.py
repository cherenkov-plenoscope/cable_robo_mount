import numpy as np
import matplotlib.pyplot as plt


config = {
    'photons_per_square_meter': 1000,
    'sensor': {
        'bin_width_deg': 0.001,
        'region_of_interest_deg': 1 
    },
    'ground': {
        'bin_width_m': 0.1
    }
}


def read_sensor_response(path):
    # 0     x: [m], intersection on screen
    # 1     y: [m], intersection on screen
    # 2     cos_x: [1], x component of inverse incident direction
    # 3     cos_y: [1], y component of inverse incident direction
    #             inverse_incident = (cos_x, cos_y, sqrt(1 - cos_x^2 - cos_y^2))^T
    # 4     wavelength: [m]
    # 5     arrival_time: [s]
    # 6     simulation_truth_id [1]
    response = np.genfromtxt(path)
    return {
        'x': response[:,0],
        'y': response[:,1],
        #'cos_x': response[:,2],
        #'cos_y': response[:,3],
        #'wavelength': response[:,4],
        'arrival_time': response[:,5],
        #'id': response[:,6],
        'number_of_photons': response.shape[0]
    }


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


def full_width_half_mean(image):
    hist = image['histogram']
    bin_width = (image['bins'][-1] - image['bins'][0])/image['bins'].shape[0]
    max_intensity = hist.max()
    above_half_intensity = hist > 0.5*max_intensity
    number_of_pixels_above_half_intensity = above_half_intensity.sum()

    area_above_half_intensity = number_of_pixels_above_half_intensity*bin_width*bin_width

    diameter_of_disc_like_area_above_half_intensity = 2.0*np.sqrt(area_above_half_intensity/np.pi)
    return diameter_of_disc_like_area_above_half_intensity