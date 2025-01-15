"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as dtcl
import typing as h

from babelplot.specification.plot import (
    UNAVAILABLE_for_this_DIM,
    backend_plots_h,
    plot_e,
    plot_type_h,
)
from babelplot.type.base import babelplot_element_t as base_plot_t
from babelplot.type.base import backend_plot_h


@dtcl.dataclass(repr=False, eq=False)
class plot_t(base_plot_t):
    title: str | None = None
    # See babelplot.type.frame.NewBackendPlot for an explanation
    backend_type: type[backend_plot_h] | None = dtcl.field(init=False, default=None)


def BackendPlotFromPlotE(
    plot: plot_e, frame_dim: int, backend: str, backend_plots: backend_plots_h, /
) -> h.Callable:
    """
    Returns the plot type callable for the given plot_e member and the dimension passed
    as "frame_dim". The available callables are passed as "backend_plots". The name of
    the backend, passed as "backend", is only used in error messages.
    """
    if plot in backend_plots:
        description = backend_plots[plot]
        if description.__len__() <= frame_dim - 1:
            raise ValueError(
                f"{plot.value}: Invalid {backend} plotting object for a {frame_dim}-dimensional frame."
            )

        description = description[frame_dim - 1]
        if description is UNAVAILABLE_for_this_DIM:
            raise ValueError(
                f"{plot.value}: Unavailable {backend} plotting object for a {frame_dim}-dimensional frame."
            )

        return description

    raise ValueError(f"{plot.value}: Unknown {backend} plotting object.")


def BackendPlotFromAny(
    spec: plot_type_h | type[backend_plot_h],
    frame_dim: int,
    backend: str,
    backend_plots: backend_plots_h,
    /,
) -> h.Callable | None:
    """"""
    if isinstance(spec, str):
        if plot_e.IsValid(spec):
            spec = plot_e.NewFromName(spec)
            output = BackendPlotFromPlotE(spec, frame_dim, backend, backend_plots)
        else:
            output = None
    elif isinstance(spec, plot_e):
        output = BackendPlotFromPlotE(spec, frame_dim, backend, backend_plots)
    else:
        output = spec

    return output


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
