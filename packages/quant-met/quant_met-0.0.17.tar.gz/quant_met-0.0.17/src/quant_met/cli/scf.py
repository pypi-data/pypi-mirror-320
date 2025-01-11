# SPDX-FileCopyrightText: 2024 Tjark Sievers
#
# SPDX-License-Identifier: MIT

"""Functions to run self-consistent calculation for the order parameter."""

import logging
from pathlib import Path

from quant_met import mean_field
from quant_met.parameters import Parameters

from ._utils import _hamiltonian_factory

logger = logging.getLogger(__name__)


def scf(parameters: Parameters) -> None:
    """Self-consistent calculation for the order parameter.

    Parameters
    ----------
    parameters: Parameters
        An instance of Parameters containing control settings, the model,
        and k-point specifications for the self-consistency calculation.
    """
    result_path = Path(parameters.control.outdir)
    result_path.mkdir(exist_ok=True, parents=True)

    h = _hamiltonian_factory(parameters=parameters.model, classname=parameters.model.name)

    solved_h = mean_field.self_consistency_loop(
        h=h,
        k_space_grid=h.lattice.generate_bz_grid(
            ncols=parameters.k_points.nk1, nrows=parameters.k_points.nk2
        ),
        epsilon=parameters.control.conv_treshold,
        max_iter=parameters.control.max_iter,
    )

    logger.info("Self-consistency loop completed successfully.")
    logger.debug("Obtained delta values: %s", solved_h.delta_orbital_basis)

    result_file = result_path / f"{parameters.control.prefix}.hdf5"
    solved_h.save(filename=result_file)
    logger.info("Results saved to %s", result_file)
