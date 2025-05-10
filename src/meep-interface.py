import meep as mp
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from copy import deepcopy

# Simulation parameters
dimensions = 2            # 2D simulation
resolution = 25           # grid points per μm (>=10 per smallest λ)
sx = 3.0                  # x-width (μm) of cell (thin periodic domain)
sy = 20.0                 # y-height (μm) of cell
dpml = 3.0                # PML thickness (μm)
wvl_min = 0.4           # min wavelength
wvl_max = 0.8           # max wavelength
fmin = 1/wvl_max        # min frequency
fmax = 1/wvl_min        # max frequency
fcen = 0.5*(fmin+fmax)  # center frequency
df = fmax-fmin          # frequency width
nfreq = 1000            # number of frequency bins
eps = 3**2

n1 = 1.0  # refractive index of air
n2 = eps**0.5  # refractive index of block
n3 = eps**0.5

# Geometry: dielectric block
block_height = 10
block_center = -5
source_height = 5


###########################################################################
###########################################################################
###########################################################################
geometry = [mp.Block(size=mp.Vector3(sx, block_height, sx),
                     center=mp.Vector3(0, block_center, 0),
                     material=mp.Medium(epsilon=eps))]
# Sources: broadband Gaussian plane wave
sources = [mp.Source(mp.GaussianSource(frequency=fcen, fwidth=df, is_integrated=True),
                     component=mp.Ex,
                     size=mp.Vector3(sx,0,sx),  # extent across whole width
                     center=mp.Vector3(0, source_height),
                     )]
# Boundary conditions: PML top/bottom, periodic sides
pml_layers = [mp.PML(dpml, direction=mp.Y, side=mp.Low),
              mp.PML(dpml, direction=mp.Y, side=mp.High),
]
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy, sx),
                    geometry=[],
                    sources=sources,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    dimensions=dimensions,
                    k_point=mp.Vector3(0, 1, 0)
                    )

flux_y = -source_height  # μm (just above bottom PML)
tran_flux = sim.add_flux(fcen, df, nfreq, 
                         mp.FluxRegion(center=mp.Vector3(0, flux_y, 0), size=mp.Vector3(sx,0,sx)))
# Reference (empty) simulation for incident power
sim.run(until=200)  # run until fields decay (adjust time as needed)
flux_empty = mp.get_fluxes(tran_flux)
flux_freqs = mp.get_flux_freqs(tran_flux)
# Save flux data for normalization
empty_flux = deepcopy(flux_empty)

# Simulation with dielectric
sim.reset_meep()
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy, sx),
                    geometry=geometry,
                    sources=sources,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    dimensions=dimensions,
                    k_point=mp.Vector3(0, 1, 0)
                    )
tran_flux = sim.add_flux(fcen, df, nfreq, 
                         mp.FluxRegion(center=mp.Vector3(0, flux_y, 0), size=mp.Vector3(sx,0,sx)))
sim.run(until=200)
flux_block = mp.get_fluxes(tran_flux)
print("flux_block=", flux_block)

# Transmission spectrum (power) = transmitted / incident
T_sim = [fb/fi for fb,fi in zip(flux_block, empty_flux)]
# Optionally print or save T_sim vs frequency (1/λ)
for freq, T in zip(flux_freqs, T_sim):
    print("freq=%.3f (1/$\mu m$), T=%.6f" % (freq, T))
average_T = sum(T_sim)/len(T_sim)
print("Average T = %.6f" % average_T)


wavelengths = np.linspace(wvl_min, wvl_max, nfreq)  

# Fresnel coefficients at normal incidence
r01 = (n1 - n2) / (n1 + n2)
r12 = (n2 - n3) / (n2 + n3)

# Phase difference
delta = (2 * np.pi * n2 * block_height) / wavelengths
print("delta=", delta)
print("r01=", r01)
print("r12=", r12)

# Complex reflection amplitude
numerator = r01 + r12 * np.exp(2j * delta)
denominator = 1 + r01 * r12 * np.exp(2j * delta)
r_total = numerator / denominator

# Reflectance
R = np.abs(r_total) ** 2

# Transmitance
T = np.abs(1-R)

# # --- Plot simulation layout including PML, dielectric block, source, and flux monitor ---


# Plotting
plt.style.use('science')

f = plt.figure()
plt.plot([1/f for f in flux_freqs], T_sim, label='Meep', color='blue')
plt.plot(wavelengths,T, color='red', linestyle='--', label='Fresnel')
plt.xlabel('Wavelength ($\mu m$)')
plt.ylabel('Transmission')
plt.title(f'Transmission Spectrum at {resolution} grid points/$\mu m$')
#set size of figure, keep aspect ratio
plt.gcf().set_size_inches(5*1.5, 4*1.5)
plt.gca().set_aspect('auto', adjustable='box')
plt.xlim(wvl_min, wvl_max)
plt.ylim(0, 1)
plt.legend()
plt.grid()
plt.show()

f.savefig(f"Transmission_eps{eps}_h{block_height}_r{resolution}.pdf", bbox_inches='tight')




fig, ax = plt.subplots(figsize=(4, 10))

# Plot PML regions
ax.axhspan(-sy/2, -sy/2 + dpml, color='gray', alpha=0.3, label='PML')
ax.axhspan(sy/2 - dpml, sy/2, color='gray', alpha=0.3)

# Plot dielectric block
block_bottom = block_center - block_height/2
block_top = block_center + block_height/2
ax.fill_between([-sx/2, sx/2], block_bottom, block_top, color='blue', alpha=0.4, label='Dielectric block')

# Plot source
ax.axhline(y=source_height, color='red', linestyle='--', linewidth=3, label='Source')

# Plot flux monitor
ax.axhline(y=flux_y, color='green', linestyle=':', linewidth=3, label='Flux Monitor')

# Format the plot
ax.set_xlim(-sx/2, sx/2)
ax.set_ylim(-sy/2, sy/2)
ax.set_xlabel('x ($\mu m$)')
ax.set_ylabel('y ($\mu m$)')
ax.set_title('Simulation Layout')
ax.legend(loc='lower right')
ax.grid(True)
plt.tight_layout()
plt.show()