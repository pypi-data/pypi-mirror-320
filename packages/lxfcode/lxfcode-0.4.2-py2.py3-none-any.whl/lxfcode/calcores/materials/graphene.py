from ..abc.abmoire import ABContiGraMoires, ABContiMoHa
from ..hamiltonians.tb_h import SLGHa
from ..bands.bands_cal import BandsCal
from ..bands.bands_plot import BandsPlot
from ..raman.raman_plot import RamanCal, RamanPlot
from typing import Literal, Type

__all__ = ["SLGra"]

class SLGra(ABContiGraMoires):
    mat_name = "SLG"

    def __init__(
        self,
        haClassType: Type[ABContiMoHa] = SLGHa,
        vFcoeff: float = 1,
        a0: float = 2.46,
    ) -> None:
        super().__init__(0, haClassType=haClassType, vFcoeff=vFcoeff, a0=a0)

    @property
    def renormed_BZ_K_side(self):
        return self.K0

    @property
    def epsilonM(self):
        return self.epsilonO

    @property
    def areaM(self):
        return self.areaO

    def bands(
        self,
        path: list[Literal["K_t", "K_b", "M", "Gamma"]] = ["K_t", "K_b", "Gamma", "M"],
        suffix="",
    ):
        bds_title = "Band structures of {} {}".format(self.mat_name, self.mat_name)
        h: ABContiMoHa = self.haClassType(self)

        bcals = BandsCal(h, path=path, suffix=suffix)
        bplot = BandsPlot(bcals)
        bplot.plot(title_name=bds_title)

    def raman(
        self,
        density=70,
        calcores=3,
        ffolder="",
        update_eles=False,
        bds_num=5,
        disable_elet=False,
        gamma=100,
    ) -> RamanPlot:
        h: ABContiMoHa = self.haClassType(self)
        rcals = RamanCal(
            h, density=density, cal_corenum=calcores, bds_num=bds_num, gamma=gamma
        )
        rplot = RamanPlot(rcals, ffolder=ffolder, disable_elet=disable_elet)

        r_intensity = rplot.plot(update_elet=update_eles)
        print(r_intensity / (density**2 * self.areaO) ** 2)
        return rplot
