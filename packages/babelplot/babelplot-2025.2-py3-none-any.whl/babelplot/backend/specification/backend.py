"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from enum import Enum as enum_t
from enum import unique

from babelplot.extension.enum_ import EnumMembers, EnumValues


@unique
class backend_e(enum_t):
    """
    Available plotting backends.
    """

    BOKEH = "bokeh"
    MATPLOTLIB = "matplotlib"
    PLOTLY = "plotly"
    VEDO = "vedo"

    @classmethod
    def FormattedBackends(cls) -> str:
        """"""
        as_members = str(EnumMembers(cls))[1:-1].replace("'", "")
        as_names = str(IMPLEMENTED_BACKENDS_AS_STR)[1:-1].replace("'", "")
        as_aliases = (f"{_als} -> {_pbe}" for _als, _pbe in BACKEND_FROM_ALIAS.items())

        output = (
            f"As {cls.__name__} members: {as_members}\n"
            f"As names: {as_names}\n"
            f"As aliases: {', '.join(as_aliases)}"
        )

        return output

    @staticmethod
    def IsValid(name: str, /) -> bool:
        """"""
        return (name in IMPLEMENTED_BACKENDS_AS_STR) or (name in BACKEND_FROM_ALIAS)

    @classmethod
    def NewFromName(cls, name: str, /) -> h.Self:
        """"""
        if name in IMPLEMENTED_BACKENDS_AS_STR:
            return cls(name)
        if name in BACKEND_FROM_ALIAS:
            return cls(BACKEND_FROM_ALIAS[name])

        raise ValueError(
            f"{name}: Invalid backend. Expected={IMPLEMENTED_BACKENDS_AS_STR+BACKEND_ALIASES_AS_STR}."
        )


IMPLEMENTED_BACKENDS_AS_STR = EnumValues(backend_e)


# Some backends may have an alias. Here they are:
BACKEND_FROM_ALIAS = {
    "mpl": backend_e.MATPLOTLIB,
    "v3do": backend_e.VEDO,
}
BACKEND_ALIASES_AS_STR = tuple(BACKEND_FROM_ALIAS.keys())


NEW_THREAD_ACCEPTED_BY = {
    backend_e.BOKEH: True,
    backend_e.MATPLOTLIB: False,
    backend_e.PLOTLY: True,
    backend_e.VEDO: True,
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
