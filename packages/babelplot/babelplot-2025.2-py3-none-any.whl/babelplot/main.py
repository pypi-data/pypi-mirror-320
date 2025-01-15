"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import importlib as mprt
import sys as sstm
import typing as h
from pathlib import Path as path_t

from babelplot.backend.specification.backend import backend_e
from babelplot.backend.specification.runtime import AddBackendSpecification
from babelplot.constant.backend import BACKEND_FOLDER_PY
from babelplot.specification.dimension import dim_e
from babelplot.specification.plot import TranslatedArguments, plot_type_h
from babelplot.type.base import backend_plot_h
from babelplot.type.figure import figure_t
from babelplot.type.frame import frame_t
from babelplot.type.plot import plot_t
from logger_36 import LOGGER


def NewFigure(
    *args,
    title: str | None = None,
    offline_version: bool = False,
    pbe: str | path_t | backend_e | None = None,
    **kwargs,
) -> figure_t | None:
    """
    pbe: str=installed module, path_t=path to module, backend_e=implemented backend.
    """
    if pbe is None:
        pbe = backend_e.MATPLOTLIB
    elif isinstance(pbe, str) and backend_e.IsValid(pbe):
        pbe = backend_e.NewFromName(pbe)

    if isinstance(pbe, str):
        module = mprt.import_module(pbe)
    elif isinstance(pbe, path_t):
        module_name = pbe.stem
        spec = mprt.util.spec_from_file_location(module_name, pbe)
        module = mprt.util.module_from_spec(spec)
        sstm.modules[module_name] = module
        spec.loader.exec_module(module)
    else:
        try:
            module = mprt.import_module(f"{BACKEND_FOLDER_PY}.{pbe.value}_")
        except ModuleNotFoundError:
            LOGGER.error(
                f"{pbe.value}: Unusable backend. "
                f"Might be due to backend not being installed "
                f"or implementation error in backend."
            )
            return None

    translations = getattr(module, "TRANSLATIONS", None)
    AddBackendSpecification(module.NAME, module.PLOTS, translations)

    instance = module.figure_t(
        title=title,
        offline_version=offline_version,
        pbe=module.NAME,
    )
    args, kwargs = TranslatedArguments("NewBackendFigure", args, kwargs, translations)
    backend_figure = instance.NewBackendFigure(*args, **kwargs)
    instance.backend = backend_figure

    return instance


def NewPlot(
    type_: plot_type_h | type[backend_plot_h],
    *plt_args,
    fig_args=(),
    frm_args=(),
    fig_kwargs: dict[str, h.Any] | None = None,
    frm_kwargs: dict[str, h.Any] | None = None,
    fig_title: str | None = None,
    frm_title: str | None = None,
    plt_title: str | None = None,
    dim: str | dim_e = dim_e.XY,
    pbe: str | path_t | backend_e | None = None,
    should_show: bool = True,
    modal: bool = True,
    **plt_kwargs,
) -> tuple[figure_t, frame_t, plot_t] | None:
    """"""
    if fig_kwargs is None:
        fig_kwargs = {}
    if frm_kwargs is None:
        frm_kwargs = {}
    if plt_kwargs is None:
        plt_kwargs = {}

    figure = NewFigure(
        *fig_args,
        title=fig_title,
        pbe=pbe,
        **fig_kwargs,
    )
    frame = figure.AddFrame(
        *frm_args,
        title=frm_title,
        dim=dim,
        **frm_kwargs,
    )
    plot = frame.AddPlot(
        type_,
        *plt_args,
        title=plt_title,
        **plt_kwargs,
    )

    if should_show:
        figure.Show(modal=modal)

    if should_show and modal:
        return None

    return figure, frame, plot


# def CloseFigure(figure: figure_t, /)->None:
#     """"""


# def CloseAllFigures()->None:
#     """"""


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
