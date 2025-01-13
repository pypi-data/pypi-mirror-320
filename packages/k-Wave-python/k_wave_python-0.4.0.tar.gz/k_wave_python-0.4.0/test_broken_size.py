import numpy as np
from kwave.kgrid import kWaveGrid
from kwave.kmedium import kWaveMedium
from kwave.ksensor import kSensor
from kwave.ksource import kSource
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
from kwave.options.simulation_options import SimulationOptions
from kwave.options.simulation_execution_options import SimulationExecutionOptions
from copy import deepcopy

# Define grid size
Nx, Ny, Nz = 20, 20, 20  # Small grid for testing

# Set grid spacing
dx, dy, dz = 1e-3, 1e-3, 1e-3  # Grid spacing in meters

# Create k-Wave grid
kgrid = kWaveGrid([Nx, Ny, Nz], [dx, dy, dz])

# Set up time stepping
source_f0 = 500e3  # Source frequency in Hz
ppw = 6  # Points per wavelength
cfl = 0.1  # CFL number
ppp = round(ppw / cfl)  # Points per period
dt = 1 / (ppp * source_f0)  # Time step in seconds
t_end = 10e-6  # Total simulation time in seconds
Nt = int(np.ceil(t_end / dt)) + 1  # Number of time steps
kgrid.setTime(Nt, dt)

# Set up medium properties
medium_sound_speed = 1500  # Sound speed in m/s
medium_density = 1000  # Density in kg/m^3
medium = kWaveMedium(sound_speed=medium_sound_speed, density=medium_density)

# Set up source
source = kSource()
source.p_mask = np.zeros((Nx, Ny, Nz))
source.p_mask[Nx // 2, Ny // 2, Nz // 2] = 1
source_signal = np.sin(2 * np.pi * source_f0 * kgrid.t_array)
source.p = source_signal

# Set up sensor
sensor = kSensor()
sensor.mask = np.ones((Nx, Ny, Nz))  # Full grid sensor mask
sensor.record = ['p_max_all']

# Simulation options
simulation_options = SimulationOptions(
    pml_auto=True,
    data_recast=True,
    save_to_disk=True,  # Required for CPU simulation
    save_to_disk_exit=False,
    pml_inside=False,
    data_cast='single'
)

execution_options = SimulationExecutionOptions(
    is_gpu_simulation=False,
    delete_data=False,
    verbose_level=1
)

# Run the simulation
try:
    sensor_data = kspaceFirstOrder3D(
        medium=deepcopy(medium),
        kgrid=deepcopy(kgrid),
        source=deepcopy(source),
        sensor=deepcopy(sensor),
        simulation_options=simulation_options,
        execution_options=execution_options
    )
except Exception as e:
    print(f"Simulation failed with error: {e}")

# Check and reshape p_max_all
if 'p_max_all' in sensor_data:
    p_max_all = sensor_data['p_max_all']  # Should be of shape (total_grid_points,)
    print(f"p_max_all size: {p_max_all.size}")
    print(f"Expected grid size: {Nx},{Ny},{Nz}")
    
    # Attempt to reshape p_max_all
    try:
        p_max_all = p_max_all.reshape((Nx, Ny, Nz), order='F')
    except ValueError as ve:
        print(f"Error reshaping p_max_all: {ve}")
else:
    print("p_max_all not found in sensor_data")