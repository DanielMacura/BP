import matplotlib.pyplot as plt
import re

# Raw data as a string
data = """freq=1.250 (1/μm), T=0.525901
freq=1.263 (1/μm), T=0.525987
freq=1.275 (1/μm), T=0.526064
freq=1.288 (1/μm), T=0.526115
freq=1.301 (1/μm), T=0.526156
freq=1.313 (1/μm), T=0.526214
freq=1.326 (1/μm), T=0.526285
freq=1.338 (1/μm), T=0.526360
freq=1.351 (1/μm), T=0.526437
freq=1.364 (1/μm), T=0.526519
freq=1.376 (1/μm), T=0.526609
freq=1.389 (1/μm), T=0.526698
freq=1.402 (1/μm), T=0.526784
freq=1.414 (1/μm), T=0.526867
freq=1.427 (1/μm), T=0.526951
freq=1.439 (1/μm), T=0.527039
freq=1.452 (1/μm), T=0.527127
freq=1.465 (1/μm), T=0.527215
freq=1.477 (1/μm), T=0.527304
freq=1.490 (1/μm), T=0.527394
freq=1.503 (1/μm), T=0.527485
freq=1.515 (1/μm), T=0.527576
freq=1.528 (1/μm), T=0.527667
freq=1.540 (1/μm), T=0.527760
freq=1.553 (1/μm), T=0.527854
freq=1.566 (1/μm), T=0.527948
freq=1.578 (1/μm), T=0.528041
freq=1.591 (1/μm), T=0.528136
freq=1.604 (1/μm), T=0.528232
freq=1.616 (1/μm), T=0.528328
freq=1.629 (1/μm), T=0.528426
freq=1.641 (1/μm), T=0.528525
freq=1.654 (1/μm), T=0.528626
freq=1.667 (1/μm), T=0.528727
freq=1.679 (1/μm), T=0.528828
freq=1.692 (1/μm), T=0.528931
freq=1.705 (1/μm), T=0.529035
freq=1.717 (1/μm), T=0.529138
freq=1.730 (1/μm), T=0.529244
freq=1.742 (1/μm), T=0.529349
freq=1.755 (1/μm), T=0.529455
freq=1.768 (1/μm), T=0.529561
freq=1.780 (1/μm), T=0.529669
freq=1.793 (1/μm), T=0.529778
freq=1.806 (1/μm), T=0.529887
freq=1.818 (1/μm), T=0.529998
freq=1.831 (1/μm), T=0.530110
freq=1.843 (1/μm), T=0.530223
freq=1.856 (1/μm), T=0.530336
freq=1.869 (1/μm), T=0.530449
freq=1.881 (1/μm), T=0.530563
freq=1.894 (1/μm), T=0.530679
freq=1.907 (1/μm), T=0.530796
freq=1.919 (1/μm), T=0.530914
freq=1.932 (1/μm), T=0.531032
freq=1.944 (1/μm), T=0.531152
freq=1.957 (1/μm), T=0.531271
freq=1.970 (1/μm), T=0.531392
freq=1.982 (1/μm), T=0.531514
freq=1.995 (1/μm), T=0.531636
freq=2.008 (1/μm), T=0.531760
freq=2.020 (1/μm), T=0.531885
freq=2.033 (1/μm), T=0.532010
freq=2.045 (1/μm), T=0.532136
freq=2.058 (1/μm), T=0.532264
freq=2.071 (1/μm), T=0.532393
freq=2.083 (1/μm), T=0.532520
freq=2.096 (1/μm), T=0.532650
freq=2.109 (1/μm), T=0.532781
freq=2.121 (1/μm), T=0.532913
freq=2.134 (1/μm), T=0.533045
freq=2.146 (1/μm), T=0.533180
freq=2.159 (1/μm), T=0.533315
freq=2.172 (1/μm), T=0.533449
freq=2.184 (1/μm), T=0.533585
freq=2.197 (1/μm), T=0.533723
freq=2.210 (1/μm), T=0.533862
freq=2.222 (1/μm), T=0.534003
freq=2.235 (1/μm), T=0.534142
freq=2.247 (1/μm), T=0.534283
freq=2.260 (1/μm), T=0.534425
freq=2.273 (1/μm), T=0.534565
freq=2.285 (1/μm), T=0.534709
freq=2.298 (1/μm), T=0.534852
freq=2.311 (1/μm), T=0.534995
freq=2.323 (1/μm), T=0.535139
freq=2.336 (1/μm), T=0.535283
freq=2.348 (1/μm), T=0.535430
freq=2.361 (1/μm), T=0.535575
freq=2.374 (1/μm), T=0.535725
freq=2.386 (1/μm), T=0.535880
freq=2.399 (1/μm), T=0.536031
freq=2.412 (1/μm), T=0.536196
freq=2.424 (1/μm), T=0.536353
freq=2.437 (1/μm), T=0.536516
freq=2.449 (1/μm), T=0.536685
freq=2.462 (1/μm), T=0.536854
freq=2.475 (1/μm), T=0.537015
freq=2.487 (1/μm), T=0.537188
freq=2.500 (1/μm), T=0.537343"""

# Parse the data using regular expressions
freqs = []
transmissions = []

for match in re.finditer(r"freq=([\d.]+) \(1/μm\), T=([\d.]+)", data):
    freq = float(match.group(1))
    T = float(match.group(2))
    freqs.append(freq)
    transmissions.append(T)

# Convert frequency (1/μm) to wavelength (μm)
wavelengths = [1 / f for f in freqs]

# Optional Fresnel line value (change this if needed)
eps = 30
n1=1
n2 = eps**0.5 
T_fresnel = (4*n1*n2)/((n1+n2)**2)

# Plotting
plt.figure()
plt.plot(wavelengths, transmissions, label='Meep', color='blue')
plt.axhline(y=T_fresnel, color='red', linestyle='--', label='Fresnel')
# set y to 0 to 1
plt.ylim(0, 1)
plt.xlabel('Wavelength (μm)')
plt.ylabel('Transmission')
plt.title('Transmission Spectrum')
plt.legend()
plt.grid()
plt.show()