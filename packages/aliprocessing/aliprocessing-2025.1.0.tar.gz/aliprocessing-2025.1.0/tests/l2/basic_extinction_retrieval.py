from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sasktran as sk
from ali_processing.legacy.instrument.simulator import ImagingSimulator
from ali_processing.legacy.retrieval.extinction import ExtinctionRetrieval
from ali_processing.legacy.util.config import Config
from ali_processing.legacy.util.geometry import optical_axis_from_geometry
from ali_processing.legacy.util.rt_options import simulation_rt_opts
from ali_processing.legacy.util.sensors import simulation_sensor

mpl.use("Qt5Agg")
plt.style.use(Config.MATPLOTLIB_STYLE_FILE)


def basic_extinction_retrieval(alts=(22.5,), mjd=54372, test_file: str | None = None):
    # ------------------------------ ATMOSPHERE ----------------------------- #
    # Create the atmosphere that is used to generate the synthetic measurement
    atmo_sim = sk.Atmosphere()
    atmo_sim["air"] = sk.Species(sk.Rayleigh(), sk.MSIS90())
    atmo_sim["ozone"] = sk.Species(sk.O3DBM(), sk.Labow())
    altitudes = np.arange(0.0, 45001.0, 200)  # retrieval altitudes
    aerosol = np.loadtxt(Config.AEROSOL_APRIORI_FILE)
    aerosol = np.interp(altitudes, aerosol[:, 0], aerosol[:, 1])
    atmo_sim["aerosol"] = sk.SpeciesAerosol(
        altitudes,
        {"SKCLIMATOLOGY_AEROSOL_CM3": aerosol},
        {
            "SKCLIMATOLOGY_LOGNORMAL_MODERADIUS_MICRONS": np.ones_like(aerosol) * 0.08,
            "SKCLIMATOLOGY_LOGNORMAL_MODEWIDTH": np.ones_like(aerosol) * 1.6,
        },
        "H2SO4",
    )

    geometry = sk.VerticalImage()
    geometry.from_sza_ssa(
        sza=60,
        ssa=90,
        lat=45.0,
        lon=0,
        tanalts_km=alts,
        mjd=mjd,
        locallook=0,
        satalt_km=500,
    )
    optical_geometry = optical_axis_from_geometry(geometry)

    # ------------------------------ SENSORS ----------------------------- #
    # Create the ALI sensors
    sensor_wavel = np.array([750.0, 1020.0, 1550.0])
    sensors = []
    opt_geom = []
    for wavel in sensor_wavel:
        sensor = simulation_sensor(
            wavelength_nm=[wavel], simulated_pixel_averaging=50, noisy=True
        )
        sensor.auto_exposure = True
        sensors.append(sensor)
        opt_geom.append(optical_geometry)

    # ------------------------------ SIMULATOR ----------------------------- #
    sim_opts = simulation_rt_opts(configure_for_cloud=False, two_dim=False)
    simulator = ImagingSimulator(
        sensors=sensors, optical_axis=opt_geom, atmosphere=atmo_sim, options=sim_opts
    )
    simulator.sun = geometry.sun
    simulator.grid_sampling = True
    simulator.group_scans = False
    simulator.num_vertical_samples = 512
    simulator.dual_polarization = True

    measurement_l1 = simulator.calculate_radiance()

    retrieval = ExtinctionRetrieval(sensors, opt_geom, measurement_l1)
    retrieval.aerosol_vector_wavelength = [750.0, 1020.0, 1550.0]
    retrieval.max_iterations = 5
    retrieval.vertical_samples = 512
    if test_file is None:
        test_file = "example_retrieval.nc"
    if Path(test_file).is_file():
        Path(test_file).unlink()
    retrieval.output_filename = test_file
    retrieval.simulation_atmosphere = atmo_sim
    retrieval.sun = geometry.sun
    retrieval.brdf = atmo_sim.brdf.albedo
    retrieval.couple_normalization_altitudes = False
    retrieval.use_cloud_for_lower_bound = False
    retrieval.tikhonov_factor *= 2
    retrieval.retrieve()
    fig, ax = retrieval.plot_results(test_file)


if __name__ == "__main__":
    basic_extinction_retrieval()
