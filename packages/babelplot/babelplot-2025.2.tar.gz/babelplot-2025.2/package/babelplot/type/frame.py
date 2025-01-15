"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as dtcl
import difflib as diff
import typing as h

from babelplot.backend.specification.runtime import BackendPlots, BackendTranslations
from babelplot.specification.dimension import FRAME_DIM_FOR_DATA_DIM, dim_e
from babelplot.specification.plot import (
    KNOWN_PLOT_TYPES,
    TranslatedArguments,
    plot_type_h,
)
from babelplot.type.base import babelplot_element_t as base_frame_t
from babelplot.type.base import backend_frame_h, backend_plot_h
from babelplot.type.plot import BackendPlotFromAny, plot_t

plot_type_w_pbe_h = plot_type_h | type[backend_plot_h]


@dtcl.dataclass(repr=False, eq=False)
class frame_t(base_frame_t):
    title: str | None = None
    dim: dim_e | None = None
    frame_dim: int | None = dtcl.field(init=False, default=None)
    plot_class: type[plot_t] | None = dtcl.field(init=False, default=None)
    plots: list[plot_t] = dtcl.field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """"""
        self.frame_dim = FRAME_DIM_FOR_DATA_DIM[self.dim]

    def AddPlot(
        self,
        type_: plot_type_w_pbe_h,
        *args,
        title: str | None = None,
        **kwargs,
    ) -> plot_t:
        """"""
        if isinstance(type_, str):
            closest = diff.get_close_matches(type_.lower(), KNOWN_PLOT_TYPES, n=1)
            if closest.__len__() == 0:
                raise ValueError(
                    f"{type_}: Unknown plot type. Valid options: "
                    f"{str(KNOWN_PLOT_TYPES)[1:-1]}."
                )

            type_ = closest[0]

        plot_function = BackendPlotFromAny(
            type_, self.frame_dim, self.pbe, BackendPlots(self.pbe)
        )
        args, kwargs = TranslatedArguments(
            plot_function, args, kwargs, BackendTranslations(self.pbe)
        )
        plot = self.plot_class(
            title=title,
            property=kwargs.copy(),
            pbe=self.pbe,
        )
        plot.backend, plot.backend_type = self.NewBackendPlot(
            self.backend, type_, plot_function, *args, title=title, **kwargs
        )
        if hasattr(plot, "BackendDefaultProperties"):
            for name, value in plot.BackendDefaultProperties(plot.backend_type).items():
                if name not in plot.property:
                    plot.property[name] = value

        self.plots.append(plot)

        return plot

    def RemovePlot(self, plot: plot_t, /) -> None:
        """"""
        self.plots.remove(plot)
        self.RemoveBackendPlot(plot.backend, self.backend)

    def Clear(self) -> None:
        """"""
        # Do not use a for-loop since self.plots will be modified during looping
        while self.plots.__len__() > 0:
            plot = self.plots[0]
            self.RemovePlot(plot)

    def NewBackendPlot(
        self,
        _: backend_frame_h,
        type_: plot_type_w_pbe_h,
        plot_function: (
            type[backend_plot_h] | h.Callable[..., backend_plot_h | h.Any] | None
        ),
        *args,
        title: str | None = None,
        **kwargs,
    ) -> tuple[
        backend_plot_h | h.Any,
        type[backend_plot_h] | h.Callable[..., backend_plot_h | h.Any],
    ]:
        """
        The returned object should be backend_plot_h. However, some backends might not
        have a specific class for each plot type. For example, Matplotlib returns an
        instance of matplotlib.collections.PathCollection when making a scatter plot
        with matplotlib.axes.Axes.scatter.
        """
        raise NotImplemented(
            f"{frame_t.NewBackendPlot.__name__}: Not provided by backend."
        )

    @staticmethod
    def RemoveBackendPlot(plot: backend_plot_h, frame: backend_frame_h, /) -> None:
        """"""
        raise NotImplemented(
            f"{frame_t.RemoveBackendPlot.__name__}: Not provided by backend."
        )


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
