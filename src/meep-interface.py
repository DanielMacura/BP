import meep as mp
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from copy import deepcopy

# Simulation parameters
dimensions = 2          # 2D simulation
resolution = 100           # grid points per μm (>=10 per smallest λ)
sx = 3.0                  # x-width (μm) of cell (thin periodic domain)
sy = 20.0                 # y-height (μm) of cell
dpml = 3.0                # PML thickness (μm)
wvl_min = 0.2           # min wavelength
wvl_max = 0.8           # max wavelength
fmin = 1/wvl_max        # min frequency
fmax = 1/wvl_min        # max frequency
fcen = 0.5*(fmin+fmax)  # center frequency
df = fmax-fmin          # frequency width
nfreq = 1000            # number of frequency bins
eps = 25.0

n1 = 1.0  # refractive index of air
n2 = eps**0.5  # refractive index of block
n3 = 1.0 

# Geometry: dielectric block
block_height = 0.3
block_center = 0
source_height = 6


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

              mp.PML(dpml, direction=mp.Z, side=mp.Low),
              mp.PML(dpml, direction=mp.Z, side=mp.High)]
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy, sx),
                    geometry=[],
                    sources=sources,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    dimensions=dimensions)

flux_y = -4  # μm (just above bottom PML)
tran_flux = sim.add_flux(fcen, df, nfreq, 
                         mp.FluxRegion(center=mp.Vector3(0, flux_y, 0), size=mp.Vector3(sx,0,sx)))
# Reference (empty) simulation for incident power
sim.run(until=50)  # run until fields decay (adjust time as needed)
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
                    dimensions=dimensions)
tran_flux = sim.add_flux(fcen, df, nfreq, 
                         mp.FluxRegion(center=mp.Vector3(0, flux_y, 0), size=mp.Vector3(sx,0,sx)))
sim.run(until=50)
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


data = """freq=1.250 (1/μm), T=0.267745
freq=1.263 (1/μm), T=0.328311
freq=1.275 (1/μm), T=0.415433
freq=1.288 (1/μm), T=0.538970
freq=1.301 (1/μm), T=0.702957
freq=1.313 (1/μm), T=0.882051
freq=1.326 (1/μm), T=0.994279
freq=1.338 (1/μm), T=0.955754
freq=1.351 (1/μm), T=0.797884
freq=1.364 (1/μm), T=0.619117
freq=1.376 (1/μm), T=0.473619
freq=1.389 (1/μm), T=0.368513
freq=1.402 (1/μm), T=0.295217
freq=1.414 (1/μm), T=0.244264
freq=1.427 (1/μm), T=0.208646
freq=1.439 (1/μm), T=0.183698
freq=1.452 (1/μm), T=0.166413
freq=1.465 (1/μm), T=0.154887
freq=1.477 (1/μm), T=0.147941
freq=1.490 (1/μm), T=0.144911
freq=1.503 (1/μm), T=0.145517
freq=1.515 (1/μm), T=0.149819
freq=1.528 (1/μm), T=0.158227
freq=1.540 (1/μm), T=0.171577
freq=1.553 (1/μm), T=0.191284
freq=1.566 (1/μm), T=0.219618
freq=1.578 (1/μm), T=0.260152
freq=1.591 (1/μm), T=0.318408
freq=1.604 (1/μm), T=0.402516
freq=1.616 (1/μm), T=0.522637
freq=1.629 (1/μm), T=0.684467
freq=1.641 (1/μm), T=0.866724
freq=1.654 (1/μm), T=0.990219
freq=1.667 (1/μm), T=0.963356
freq=1.679 (1/μm), T=0.808417
freq=1.692 (1/μm), T=0.626754
freq=1.705 (1/μm), T=0.477752
freq=1.717 (1/μm), T=0.370206
freq=1.730 (1/μm), T=0.295461
freq=1.742 (1/μm), T=0.243691
freq=1.755 (1/μm), T=0.207619
freq=1.768 (1/μm), T=0.182420
freq=1.780 (1/μm), T=0.164997
freq=1.793 (1/μm), T=0.153391
freq=1.806 (1/μm), T=0.146399
freq=1.818 (1/μm), T=0.143340
freq=1.831 (1/μm), T=0.143930
freq=1.843 (1/μm), T=0.148230
freq=1.856 (1/μm), T=0.156656
freq=1.869 (1/μm), T=0.170059
freq=1.881 (1/μm), T=0.189890
freq=1.894 (1/μm), T=0.218480
freq=1.907 (1/μm), T=0.259521
freq=1.919 (1/μm), T=0.318746
freq=1.932 (1/μm), T=0.404632
freq=1.944 (1/μm), T=0.527748
freq=1.957 (1/μm), T=0.693543
freq=1.970 (1/μm), T=0.877606
freq=1.982 (1/μm), T=0.994199
freq=1.995 (1/μm), T=0.953012
freq=2.008 (1/μm), T=0.788781
freq=2.020 (1/μm), T=0.606487
freq=2.033 (1/μm), T=0.460734
freq=2.045 (1/μm), T=0.356862
freq=2.058 (1/μm), T=0.285133
freq=2.071 (1/μm), T=0.235638
freq=2.083 (1/μm), T=0.201253
freq=2.096 (1/μm), T=0.177322
freq=2.109 (1/μm), T=0.160879
freq=2.121 (1/μm), T=0.150063
freq=2.134 (1/μm), T=0.143745
freq=2.146 (1/μm), T=0.141306
freq=2.159 (1/μm), T=0.142516
freq=2.172 (1/μm), T=0.147496
freq=2.184 (1/μm), T=0.156743
freq=2.197 (1/μm), T=0.171222
freq=2.210 (1/μm), T=0.192558
freq=2.222 (1/μm), T=0.223367
freq=2.235 (1/μm), T=0.267802
freq=2.247 (1/μm), T=0.332327
freq=2.260 (1/μm), T=0.426382
freq=2.273 (1/μm), T=0.560951
freq=2.285 (1/μm), T=0.737908
freq=2.298 (1/μm), T=0.918433
freq=2.311 (1/μm), T=0.999976
freq=2.323 (1/μm), T=0.913496
freq=2.336 (1/μm), T=0.731139
freq=2.348 (1/μm), T=0.554532
freq=2.361 (1/μm), T=0.420896
freq=2.374 (1/μm), T=0.327710
freq=2.386 (1/μm), T=0.263856
freq=2.399 (1/μm), T=0.219919
freq=2.412 (1/μm), T=0.189477
freq=2.424 (1/μm), T=0.168416
freq=2.437 (1/μm), T=0.154147
freq=2.449 (1/μm), T=0.145068
freq=2.462 (1/μm), T=0.140234
freq=2.475 (1/μm), T=0.139168
freq=2.487 (1/μm), T=0.141771
freq=2.500 (1/μm), T=0.148308"""



fig, ax = plt.subplots(figsize=(4, 10))

# Plot PML regions
ax.axhspan(-sy/2, -sy/2 + dpml, color='gray', alpha=0.3, label='PML')
ax.axhspan(sy/2 - dpml, sy/2, color='gray', alpha=0.3)

# Plot dielectric block
block_bottom = block_center - block_height/2
block_top = block_center + block_height/2
ax.fill_between([-sx/2, sx/2], block_bottom, block_top, color='blue', alpha=0.4, label='Dielectric block')

# Plot source
ax.axhline(y=source_height, color='red', linestyle='--', linewidth=1.5, label='Source')

# Plot flux monitor
ax.axhline(y=flux_y, color='green', linestyle=':', linewidth=2, label='Flux Monitor')

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