from typing import Literal, TypedDict

__all__ = ["SKPars", "Path", "DatFiles", "FitPars"]


class DatFiles(TypedDict):
    subFname: str | None | float
    outFname: str | None | float


# class ExpFiles(TypedDict):


class FitPars(TypedDict):
    x_type: Literal["wls", "e"]
    lpFileName: str
    model_type: Literal["c", "t"]
    shift_type: Literal["i", "g"]
    mod_pars_interact: bool
    single_or_diff:Literal["s","d"]
    incident_angle:float
    centers_in: list[float]
    amplitudes_in: list[float]
    broadenings_in: list[float]
    putin_type: Literal["wls", "e"]


class SKPars(TypedDict):
    Vppi0: float  ##  Default -2700
    Vpps0: float  ##  Default 480
    delta0coeff: float  ##  Default 0.184


Path = Literal["K_t", "K_b", "M", "Gamma"]
