"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

from __future__ import annotations

import typing as h

import vedo  # noqa
from babelplot.backend.specification.backend import backend_e
from babelplot.specification.dimension import dim_e
from babelplot.specification.plot import PlotsFromTemplate, plot_e, plot_type_h
from babelplot.type.base import backend_plot_h
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from numpy import ndarray as array_t
from vedo import Mesh as backend_plot_t  # noqa
from vedo import Plotter as backend_figure_t  # noqa
from vedo import Volume as volume_t  # noqa

NAME = backend_e.VEDO.value


backend_frame_t = backend_figure_t


def _NewPlot(
    frame: backend_frame_t,
    type_: plot_type_h | type[backend_plot_h],
    plot_function: (
        type[backend_plot_h] | h.Callable[..., backend_plot_h | h.Any] | None
    ),
    *args,
    title: str | None = None,  # If _, then it is swallowed by kwargs!
    **kwargs,
) -> tuple[
    backend_plot_h | h.Any,
    type[backend_plot_h] | h.Callable[..., backend_plot_h | h.Any],
]:
    """"""
    if plot_function is None:
        if hasattr(vedo, type_):
            plot_function = getattr(vedo, type_)
        else:
            raise ValueError(f"{type_}: Unknown {NAME} graph object.")

    output = plot_function(*args, **kwargs)
    frame.__iadd__(output)

    return output, type(output)


def _NewFrame(
    figure: backend_figure_t,
    _: int,
    __: int,
    *___,
    title: str | None = None,
    dim: dim_e = dim_e.XY,  # If _, then it is swallowed by kwargs!
    **____,
) -> backend_frame_t:
    """"""
    return figure


def _Show(
    figure: figure_t,
    /,
) -> None:
    """"""
    figure.backend.show().close()


# noinspection PyTypeChecker
plot_t: type[base_plot_t] = type("plot_t", (base_plot_t,), {})
# noinspection PyTypeChecker
frame_t: type[base_frame_t] = type(
    "frame_t",
    (base_frame_t,),
    {"plot_class": plot_t, "NewBackendPlot": staticmethod(_NewPlot)},
)
# noinspection PyTypeChecker
figure_t: type[base_figure_t] = type(
    "figure_t",
    (base_figure_t,),
    {
        "frame_class": frame_t,
        "NewBackendFigure": staticmethod(backend_figure_t),
        "NewBackendFrame": staticmethod(_NewFrame),
        "BackendShow": _Show,
    },
)


def _IsoSurface(volume: array_t, iso_value: float, *_, **kwargs) -> backend_plot_t:
    """"""
    return volume_t(volume).isosurface(value=[iso_value], **kwargs)


PLOTS = PlotsFromTemplate()
PLOTS[plot_e.ISOSET][2] = _IsoSurface


TRANSLATIONS = {}


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
