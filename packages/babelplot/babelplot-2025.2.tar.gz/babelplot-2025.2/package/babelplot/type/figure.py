"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as dtcl
import typing as h
from multiprocessing import Process as process_t

from babelplot.backend.specification.backend import backend_e
from babelplot.backend.specification.runtime import BackendTranslations
from babelplot.specification.dimension import dim_e
from babelplot.specification.plot import TranslatedArguments
from babelplot.type.base import babelplot_element_t as base_figure_t
from babelplot.type.base import backend_figure_h, backend_frame_h
from babelplot.type.frame import frame_t
from logger_36 import LOGGER

_un_shown_figures = []
_shown_figures = []


def _DefaultShape() -> list[int]:
    """
    Meant to be a mutable tuple[int, int].
    """
    return [0, 0]


@dtcl.dataclass(repr=False, eq=False)
class figure_t(base_figure_t):

    title: str | None = None
    offline_version: bool = False
    frame_class: type[frame_t] | None = dtcl.field(init=False, default=None)
    frames: list[frame_t] = dtcl.field(init=False, default_factory=list)
    locations: list[tuple[int, int]] = dtcl.field(init=False, default_factory=list)
    shape: list[int] = dtcl.field(init=False, default_factory=_DefaultShape)

    def __post_init__(self) -> None:
        """"""
        if not self.offline_version:
            _un_shown_figures.append(self)

    def AddFrame(
        self,
        *args,
        title: str | None = None,
        dim: str | dim_e = dim_e.XY,
        row: int = 0,
        col: int = 0,
        **kwargs,
    ) -> frame_t | None:
        """"""
        if isinstance(dim, str):
            dim = dim_e.NewFromName(dim)

        if (where := (row, col)) in self.locations:
            LOGGER.error(f"{where}: Frame grid cell already filled")
            return None
        if (row < 0) and (col < 0):
            LOGGER.error(f"{where}: Grid coordinates cannot be both negative")
            return None
        if row < 0:
            row = self.shape[0]
        elif col < 0:
            col = self.shape[1]

        frame = self.frame_class(
            title=title,
            dim=dim,
            pbe=self.pbe,
        )
        args, kwargs = TranslatedArguments(
            "AddFrame", args, kwargs, BackendTranslations(self.pbe)
        )
        frame.backend = self.NewBackendFrame(
            self.backend, row, col, *args, title=title, dim=dim, **kwargs
        )

        self.frames.append(frame)
        self.locations.append((row, col))
        self.shape[0] = max(self.shape[0], row + 1)
        self.shape[1] = max(self.shape[1], col + 1)

        return frame

    def LocationOfFrame(self, frame: frame_t, /) -> tuple[int, int] | None:
        """"""
        if frame not in self.frames:
            LOGGER.error(f"{frame}: Not a frame of the figure.")
            return None

        where = self.frames.index(frame)

        return self.locations[where]

    def FrameAtLocation(
        self,
        row: int,
        col: int,
        *,
        as_backend: bool = False,
    ) -> frame_t | None:
        """"""
        if (row < 0) or (col < 0) or (row >= self.shape[0]) or (col >= self.shape[1]):
            raise ValueError(
                f"({row},{col}): Out-of-bound cell coordinates. "
                f"Expected: 0≤row<{self.shape[0]} and 0≤col<{self.shape[1]}."
            )

        if (where := (row, col)) in self.locations:
            where = self.locations.index(where)
            output = self.frames[where]

            if as_backend:
                return output.backend
            else:
                return output

        return None

    def RemoveFrame(self, frame: frame_t | h.Sequence[int], /) -> None:
        """"""
        if isinstance(frame, h.Sequence):
            location = frame
            frame = self.FrameAtLocation(*location)
        else:
            location = self.LocationOfFrame(frame)

        self.frames.remove(frame)
        self.locations.remove(location)

        if self.frames.__len__() > 0:
            max_row = max(_row for _row, _ in self.locations)
            max_col = max(_col for _, _col in self.locations)
            self.shape = [max_row + 1, max_col + 1]
        else:
            self.shape = _DefaultShape()

        self.RemoveBackendFrame(frame.backend, self.backend)

    def AsHTML(self) -> str:
        """"""
        raise NotImplemented(f"{figure_t.AsHTML.__name__}: Not provided by backend.")

    def Clear(self) -> None:
        """"""
        # Do not use a for-loop since self.frames will be modified during looping
        while self.frames.__len__() > 0:
            frame = self.frames[0]
            self.RemoveFrame(frame)

    def AdjustLayout(self) -> None:
        """"""
        pass

    def Show(
        self,
        /,
        *,
        modal: bool = True,
    ) -> None:
        """"""
        if self not in _un_shown_figures:
            return
        if self.frames.__len__() == 0:
            return

        # /!\ Must be removed when closed
        _shown_figures.append(self)
        _un_shown_figures.remove(self)

        self.AdjustLayout()
        if modal:
            self.BackendShow()
        else:
            thread = process_t(target=lambda: self.BackendShow())
            thread.start()

    @staticmethod
    def NewBackendFrame(
        figure: backend_figure_h,
        row: int,
        col: int,
        *args,
        title: str | None = None,
        dim: dim_e = dim_e.XY,
        **kwargs,
    ) -> backend_frame_h:
        """"""
        raise NotImplemented(
            f"{figure_t.NewBackendFrame.__name__}: Not provided by backend."
        )

    @staticmethod
    def RemoveBackendFrame(frame: backend_frame_h, figure: backend_figure_h, /) -> None:
        """"""
        raise NotImplemented(
            f"{figure_t.RemoveBackendFrame.__name__}: Not provided by backend."
        )

    def BackendShow(self) -> None:
        """"""
        raise NotImplemented(
            f"{figure_t.BackendShow.__name__}: Not provided by backend."
        )


def ShowAllFigures(
    *,
    modal: bool = True,
) -> None:
    """"""
    if all(_fgr.pbe == backend_e.MATPLOTLIB.value for _fgr in _un_shown_figures):
        for figure in _un_shown_figures:
            figure.AdjustLayout()

        # /!\ Must be removed when closed
        _shown_figures.extend(_un_shown_figures)
        _un_shown_figures.clear()

        import matplotlib.pyplot as pypl  # noqa

        pypl.show()
    else:
        while _un_shown_figures.__len__() > 1:
            _un_shown_figures[0].Show(modal=False)
        if _un_shown_figures.__len__() > 0:
            _un_shown_figures[0].Show(modal=modal)


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
