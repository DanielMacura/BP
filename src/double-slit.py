# All credits go to the original author
# https://humaticlabs.com/blog/meep-double-slit/

import h5py
import matplotlib.pyplot as plt
import meep as mp
import numpy as np
import os

from matplotlib.colors import LinearSegmentedColormap

# Increase the default resolution for images
plt.rcParams['figure.dpi'] = 600
plt.rcParams['savefig.dpi'] = 600

# Custom colormap for dielectric structures (black with transparency)
cmap_alpha = LinearSegmentedColormap.from_list(
    'custom_alpha', [[0, 0, 0, 0], [0, 0, 0, 1]]  # Transparent to black
)

def label_plot(ax, title=None, xlabel=None, ylabel=None, elapsed=None):
    if title:
        ax.set_title(title)
    elif elapsed is not None:
        ax.set_title(f'{elapsed:0.1f} fs')
    if xlabel is not False:
        ax.set_xlabel('x (μm)' if xlabel is None else xlabel)
    if ylabel is not False:
        ax.set_ylabel('y (μm)' if ylabel is None else ylabel)

def plot_eps_data(eps_data, domain, ax=None, **kwargs):
    ax = ax or plt.gca()
    ax.imshow(eps_data.T, cmap=cmap_alpha, extent=domain, origin='lower')
    label_plot(ax, **kwargs)

def plot_ez_data(ez_data, domain, ax=None, vmax=None, aspect=None, **kwargs):
    ax = ax or plt.gca()
    img = ax.imshow(
        np.abs(ez_data.T),
        interpolation='spline36',
        cmap='viridis',  # Academic-friendly colormap
        extent=domain,
        vmax=vmax,
        aspect=aspect,
        origin='lower',
    )
    label_plot(ax, **kwargs)

def plot_pml(pml_thickness, domain, ax=None):
    ax = ax or plt.gca()
    x_start = domain[0] + pml_thickness
    x_end = domain[1] - pml_thickness
    y_start = domain[2] + pml_thickness
    y_end = domain[3] - pml_thickness
    rect = plt.Rectangle(
        (x_start, y_start),
        x_end - x_start,
        y_end - y_start,
        fill=None,
        color='k',  # Black color for visibility
        linestyle='dashed',
    )
    ax.add_patch(rect)

    # The speed of light in μm/fs
SOL = 299792458e-9

# 2D spatial domain measured in μm
domain = [0, 30, -10, 10]
center = mp.Vector3(
    (domain[1] + domain[0]) / 2,
    (domain[3] + domain[2]) / 2,
    )
cell_size = mp.Vector3(
    domain[1] - domain[0],
    domain[3] - domain[2],
    )

# Dimensions of wall with two apertures
wall_position = 10
wall_thickness = 0.5
aperture_width = 1
inner_wall_len = 4  # wall separating the apertures
outer_wall_len = (
    cell_size[1]
    - 2*aperture_width
    - inner_wall_len
    ) / 2

# Define a wall material with high dielectric constant,
# effectively blocking light and reflecting it instead
material = mp.Medium(epsilon=1e6)

# Define the wall as an array of 3 blocks arranged vertically
geometry = [
    mp.Block(
        mp.Vector3(wall_thickness, outer_wall_len, mp.inf),
        center=mp.Vector3(
            wall_position - center.x,
            domain[3] - outer_wall_len / 2),
        material=material),
    mp.Block(
        mp.Vector3(wall_thickness, outer_wall_len, mp.inf),
        center=mp.Vector3(
            wall_position - center.x,
            domain[2] + outer_wall_len / 2),
        material=material),
    mp.Block(
        mp.Vector3(wall_thickness, inner_wall_len, mp.inf),
        center=mp.Vector3(wall_position - center.x, 0),
        material=material),
    ]

# Perfectly matched layer of thickness 1
pml_thickness = 1
pml_layers = [mp.PML(pml_thickness)]

# Light wavelength, frequency, and beam width
source_lambda = 0.47  # in μm
source_frequency = 1 / source_lambda
source_beam_width = 6

# A method to return a complex-valued plane wave in the x-direction
def plane_wave(x):
    return np.exp(2j * np.pi / source_lambda * x)

# Plot the plane wave
xarr = np.linspace(0, 10*source_lambda, 1000)
wave = plane_wave(xarr)


# A method to compute the Gaussian profile in the y-direction
def gaussian_profile(y):
    return np.exp(-y**2 / (2 * (source_beam_width / 2)**2))

# Plot the Guassian profile
yarr = np.linspace(domain[2], domain[3], 200)
prof = gaussian_profile(yarr)



def amp_func(pos):
    return plane_wave(pos[0]) * gaussian_profile(pos[1])

source = mp.Source(
    src=mp.ContinuousSource(
        frequency=source_frequency,
        is_integrated=True,
        ),
    component=mp.Ez,
    center= mp.Vector3(1, 0, 0) - center,  # positioned far-left, excluding PML
    size=mp.Vector3(y=cell_size[1]),       # span entire height, including PML
    amp_func=amp_func,
    )


# Define resolution in terms of smallest component
smallest_length = min(
    source_lambda,
    wall_thickness,
    aperture_width,
    inner_wall_len,
)
pixel_count = 20
resolution = int(np.ceil(pixel_count / smallest_length))
print('Simulation resolution:', resolution)



# Convenience method to extract Ez and dielectric data
def get_data(sim, cell_size):
    ez_data = sim.get_array(
        center=mp.Vector3(), size=cell_size, component=mp.Ez)
    eps_data = sim.get_array(
        center=mp.Vector3(), size=cell_size, component=mp.Dielectric)
    return ez_data, eps_data
    

# Sim duration and number of snapshots
sim_time = 120  # in fs
n_frames = 6

# Where to save the results
sim_path = 'simulation.h5'

# Simulation object
sim = mp.Simulation(
    cell_size=cell_size,
    sources=[source],
    boundary_layers=pml_layers,
    geometry=geometry,
    resolution=resolution,
    force_complex_fields=True,
    )

def simulate(sim, sim_path, sim_time, n_frames):
    
    # Remove previous sim file, if any
    if os.path.exists(sim_path):
        os.remove(sim_path)

    # Time delta (in fs) between snapshots. Note that
    # we subtract 1 because we include the initial state
    # as the first frame.
    fs_delta = sim_time / (n_frames - 1)
    
    # Save data to an HDF5 binary file
    with h5py.File(sim_path, 'a') as f:
    
        # Save simulation params for future reference
        f.attrs['sim_time'] = sim_time
        f.attrs['n_frames'] = n_frames
        f.attrs['fs_delta'] = fs_delta
        f.attrs['resolution'] = sim.resolution
        
        # Save initial state as first frame
        sim.init_sim()
        ez_data, eps_data = get_data(sim, cell_size)
        f.create_dataset(
            'ez_data',
            shape=(n_frames, *ez_data.shape),
            dtype=ez_data.dtype,
            )
        f.create_dataset(
            'eps_data',
            shape=eps_data.shape,
            dtype=eps_data.dtype,
            )
        f['ez_data'][0]  = ez_data
        f['eps_data'][:] = eps_data
    
        # Simulate and capture remaining snapshots
        for i in range(1, n_frames):
    
            # Run until the next frame time
            sim.run(until=SOL * fs_delta)
    
            # Capture electral field data    
            ez_data, _ = get_data(sim, cell_size)
            f['ez_data'][i]  = ez_data

simulate(sim, sim_path, sim_time, n_frames)


fig_rows = 3
fig_cols = 2
n_subplots = fig_rows * fig_cols
fig, ax = plt.subplots(
    fig_rows,
    fig_cols,
    figsize=(9, 12),
    sharex=False,
    sharey=True,
)

# Set figure and axes background to white
fig.patch.set_facecolor('white')
for i in range(fig_rows):
    for j in range(fig_cols):
        ax[i][j].set_facecolor('white')

with h5py.File(sim_path, 'r') as f:
    for k in range(n_subplots):
        i, j = int(k / fig_cols), (k % fig_cols)
        _ax = ax[i][j]
        ez_data = f['ez_data'][k]
        eps_data = f['eps_data'][:]
        elapsed = k * f.attrs['fs_delta']
        vmax = 0.6  # Consistent brightness
        plot_ez_data(ez_data, domain, ax=_ax, vmax=vmax, elapsed=elapsed)
        plot_eps_data(eps_data, domain, ax=_ax)
        plot_pml(pml_thickness, domain, ax=_ax)

fig.savefig('foo.pdf', bbox_inches='tight', facecolor='white')
