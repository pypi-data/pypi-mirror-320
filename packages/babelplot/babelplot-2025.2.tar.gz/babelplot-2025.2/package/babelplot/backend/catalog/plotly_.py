"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

from __future__ import annotations

import typing as h
from pathlib import Path as path_t

import numpy as nmpy
import plotly.figure_factory as fcry  # noqa
import plotly.graph_objects as plly  # noqa
from babelplot.backend.specification.backend import backend_e
from babelplot.specification.plot import (
    UNDEFINED_PARAMETER,
    PlotsFromTemplate,
    plot_e,
    plot_type_h,
)
from babelplot.task.show_pyqt6 import Show
from babelplot.type.figure import figure_t as base_figure_t
from babelplot.type.frame import frame_t as base_frame_t
from babelplot.type.plot import plot_t as base_plot_t
from plotly.basedatatypes import BasePlotlyType as backend_plot_t  # noqa
from plotly.graph_objects import Figure as backend_figure_t  # noqa
from plotly.subplots import make_subplots as NewMultiAxesFigure  # noqa

NAME = backend_e.PLOTLY.value


array_t = nmpy.ndarray
backend_frame_h = h.TypeVar("backend_frame_h")


_FIGURE_CONFIG = {
    "toImageButtonOptions": {  # TODO: Does not work: no PNG export produced
        "filename": str(path_t.home() / "plotly_figure"),
        "height": None,
        "width": None,
    },
    "modeBarButtonsToAdd": ("drawclosedpath",),
}


def _NewPlot(
    _: backend_frame_h,
    type_: plot_type_h | type[backend_plot_t],
    plot_function: (
        type[backend_plot_t] | h.Callable[..., backend_plot_t | h.Any] | None
    ),
    *args,
    title: str | None = None,  # If _, then it is swallowed by kwargs!
    **kwargs,
) -> tuple[
    backend_plot_t | h.Any,
    type[backend_plot_t] | h.Callable[..., backend_plot_t | h.Any],
]:
    """"""
    if plot_function is None:
        if hasattr(plly, type_):
            plot_function = getattr(plly, type_)
        else:
            raise ValueError(f"{type_}: Unknown {NAME} graph object.")

    return plot_function(*args, **kwargs), plot_function


def _NewFrame(*_, **__) -> backend_frame_h:
    """"""
    return None


def _AdjustLayout(figure: figure_t, /) -> None:
    """"""
    title_postfix = ""

    n_rows, n_cols = figure.shape
    if (n_rows > 1) or (n_cols > 1):
        frame_titles = (n_rows * n_cols) * [""]
        arranged_plots = [n_cols * [None] for _ in range(n_rows)]
        for frame, (row, col) in zip(figure.frames, figure.locations):
            if frame.title is not None:
                frame_titles[row * n_cols + col] = frame.title
            for plot in frame.plots:
                if plot.title is not None:
                    plot.backend.update(name=plot.title)
            arranged_plots[row][col] = [_plt.backend for _plt in frame.plots]

        frame_types = [n_cols * [{}] for _ in range(n_rows)]
        for row, plot_row in enumerate(arranged_plots):
            for col, plot_cell in enumerate(plot_row):
                frame_types[row][col] = {"type": plot_cell[0].type}

        raw_figure = NewMultiAxesFigure(
            rows=n_rows, cols=n_cols, specs=frame_types, subplot_titles=frame_titles
        )
        for row, plot_row in enumerate(arranged_plots, start=1):
            for col, plot_cell in enumerate(plot_row, start=1):
                for plot in plot_cell:
                    raw_figure.add_trace(plot, row=row, col=col)
        figure.backend = raw_figure
    else:
        raw_figure = figure.backend

        frame = figure.frames[0]
        if frame.title is not None:
            title_postfix = f" - {frame.title}"

        for plot in frame.plots:
            raw_plot = plot.backend
            raw_figure.add_trace(raw_plot)
            if plot.title is not None:
                raw_plot.update(name=plot.title)

    if figure.title is not None:
        raw_figure.update_layout(title_text=figure.title + title_postfix)


def _AsHTML(figure: figure_t, /) -> str:
    """
    Note on include_plotlyjs:
        - "cdn": works but must be online.
        - True => blank figure if using
          PySide6.QtWebEngineWidgets.QWebEngineView.setHtml because of html size limit.
            See note in babelplot.task.html.Show.
    """
    return figure.backend.to_html(include_plotlyjs=True, config=_FIGURE_CONFIG)


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
        "NewBackendFigure": backend_figure_t,
        "NewBackendFrame": staticmethod(_NewFrame),
        "AdjustLayout": _AdjustLayout,
        "BackendShow": Show,
        "AsHTML": _AsHTML,
    },
)


def _Scatter2(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter(x=x, y=y, mode="markers", **kwargs)


def _Scatter3(x: array_t, y: array_t, z: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter3d(x=x, y=y, z=z, mode="markers", **kwargs)


def _Polyline2(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter(x=x, y=y, mode="lines", **kwargs)


def _Polyline3(x: array_t, y: array_t, z: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Scatter3d(x=x, y=y, z=z, mode="lines", **kwargs)


def _Polygon(x: array_t, y: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    x = nmpy.concatenate((x, [x[0]]))
    y = nmpy.concatenate((y, [y[0]]))

    return plly.Scatter(x=x, y=y, mode="lines", fill="toself", **kwargs)


def _Arrows2(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 2:
        u, v = args
        x, y = u.shape
    else:
        x, y, u, v = args

    if isinstance(x, int):
        x, y = nmpy.meshgrid(range(x), range(y), indexing="ij")

    return fcry.create_quiver(
        x.ravel(), y.ravel(), u.ravel(), v.ravel(), **kwargs
    ).data[0]


def _Arrows3(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 3:
        u, v, w = args
        x, y, z = u.shape
    else:
        x, y, z, u, v, w = args

    if isinstance(x, int):
        x, y, z = nmpy.meshgrid(range(x), range(y), range(z), indexing="ij")

    return plly.Cone(
        x=x.ravel(),
        y=y.ravel(),
        z=z.ravel(),
        u=u.ravel(),
        v=v.ravel(),
        w=w.ravel(),
        **kwargs,
    )


def _ElevationSurface(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        elevation = args[0]
        x, y = nmpy.meshgrid(
            range(elevation.shape[0]), range(elevation.shape[1]), indexing="ij"
        )
    else:
        x, y, elevation = args

    return plly.Surface(contours={}, x=x, y=y, z=elevation, **kwargs)


def _IsoContour(*args, **kwargs) -> backend_plot_t:
    """"""
    parameters = {
        "contours_coloring": "lines",
        "line_width": 2,
    }

    if args.__len__() == 2:
        values, value = args
    else:
        x, y, values, value = args
        parameters["x"] = x
        parameters["y"] = y
    parameters["z"] = values
    parameters["contours"] = {
        "start": value,
        "end": value,
        "size": 1,
        "showlabels": True,
    }

    parameters.update(kwargs)

    return plly.Contour(**parameters)


def _IsoSurface(values: array_t, value: float, *args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 3:
        x, y, z = args
    else:
        x, y, z = nmpy.meshgrid(
            range(values.shape[0]),
            range(values.shape[1]),
            range(values.shape[2]),
            indexing="ij",
        )

    parameters = {
        "surface": {"count": 1},
        "caps": {"x_show": False, "y_show": False, "z_show": False},
    }
    parameters.update(kwargs)

    return plly.Isosurface(
        x=x.ravel(),
        y=y.ravel(),
        z=z.ravel(),
        value=values.ravel(),
        isomin=value,
        isomax=value,
        **parameters,
    )


def _Mesh(triangles: array_t, vertices: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=triangles[:, 0],
        j=triangles[:, 1],
        k=triangles[:, 2],
        **kwargs,
    )


def _BarH(*args, **kwargs) -> backend_plot_t:
    """"""
    return _BarV(*args, orientation="h", **kwargs)


def _BarV(*args, **kwargs) -> backend_plot_t:
    """"""
    if args.__len__() == 1:
        counts = args[0]
        positions = tuple(range(counts.__len__()))
    else:
        positions, counts = args
    if kwargs.get("orientation") == "h":
        positions, counts = counts, positions

    return plly.Bar(x=positions, y=counts, **kwargs)


def _Pie(values: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    return plly.Pie(values=values, **kwargs)


def _Image(image: array_t, *_, **kwargs) -> backend_plot_t:
    """"""
    if image.ndim == 2:
        return plly.Heatmap(z=image, **kwargs)

    return plly.Image(z=image, **kwargs)


def _Text2(text: str, x: float, y: float, *_, **kwargs) -> backend_plot_t:
    """"""
    parameters = {"textposition": "top right"}
    parameters.update(kwargs)

    return plly.Scatter(x=[x], y=[y], text=[text], mode="text", **parameters)


def _Text3(text: str, x: float, y: float, z: float, *_, **kwargs) -> backend_plot_t:
    """"""
    parameters = {"textposition": "top right"}
    parameters.update(kwargs)

    return plly.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        text=[text],
        mode="text",
        **parameters,
    )


PLOTS = PlotsFromTemplate()

PLOTS[plot_e.SCATTER][1] = _Scatter2
PLOTS[plot_e.POLYLINE][1] = _Polyline2
PLOTS[plot_e.POLYGON][1] = _Polygon
PLOTS[plot_e.ARROWS][1] = _Arrows2
PLOTS[plot_e.ISOSET][1] = _IsoContour
PLOTS[plot_e.BARH][1] = _BarH
PLOTS[plot_e.BARV][1] = _BarV
PLOTS[plot_e.PIE][1] = _Pie
PLOTS[plot_e.IMAGE][1] = _Image
PLOTS[plot_e.TEXT][1] = _Text2

PLOTS[plot_e.SCATTER][2] = _Scatter3
PLOTS[plot_e.POLYLINE][2] = _Polyline3
PLOTS[plot_e.ARROWS][2] = _Arrows3
PLOTS[plot_e.ELEVATION][2] = _ElevationSurface
PLOTS[plot_e.ISOSET][2] = _IsoSurface
PLOTS[plot_e.MESH][2] = _Mesh
PLOTS[plot_e.TEXT][2] = _Text3


TRANSLATIONS = {
    "alpha": "opacity",
    "color_face": "surfacecolor",
    (_IsoSurface, "color_face"): UNDEFINED_PARAMETER,
}


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
