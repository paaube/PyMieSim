import numpy as np
from ai import cs


from PyMieSim.utils import PlotUnstructureData, Angle2Direct
from PyMieSim.Representations import Footprint
from PyMieSim._Coupling import IntensityPointCoupling, AmplitudePointCoupling, IntensityMeanCoupling, AmplitudeMeanCoupling

""" Coupling Reference: Estimation of Coupling Efficiency of Optical Fiber by Far-Field Method """



def GetFootprint(Detector, Scatterer, Num):

    Footprin = Footprint(Scatterer = Scatterer, Detector = Detector, Num=200)

    return Footprin



def PyCoupling(Scatterer, Detector):
    if Detector.Filter.Radian == None:
        ParaFiltering = 1; PerpFiltering = 1
    else:
        ParaFiltering = np.cos(Detector.Filter.Radian); PerpFiltering = np.sin(Detector.Filter.Radian)

    if Detector.CouplingMode[1] == 'Centered':

        if Detector.CouplingMode[0] == "Intensity":
            Para = Detector.Scalar * Scatterer.Parallel(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian)
            Para = (Para * Detector.Mesh.SinMesh * Detector.Mesh.dOmega.Radian).__abs__()**2
            Para = Para.sum() * ParaFiltering**2

            Perp = Detector.Scalar * Scatterer.Perpendicular(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian)
            Perp = (Perp * Detector.Mesh.SinMesh * Detector.Mesh.dOmega.Radian).__abs__()**2
            Perp = Perp.sum() * PerpFiltering**2


        if Detector.CouplingMode[0] == "Amplitude":
            Para = (Detector.Scalar * Scatterer.Parallel(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian))
            Para = Para * Detector.Mesh.SinMesh * Detector.Mesh.dOmega.Radian
            Para = Para.sum().__abs__()**2 * ParaFiltering**2

            Perp = (Detector.Scalar * Scatterer.Perpendicular(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian))
            Perp = Perp * Detector.Mesh.SinMesh * Detector.Mesh.dOmega.Radian
            Perp = Perp.sum().__abs__()**2 * PerpFiltering**2

        return Para + Perp

    if Detector.CouplingMode[1] == 'Mean':
        if Detector.CouplingMode[0] == "Intensity":
            Para = np.sum( np.abs( Detector.Scalar * Scatterer.Parallel(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian) )**2 *  Detector.Mesh.dOmega.Radian) / Detector.Mesh.Omega.Radian
            Perp = np.sum( np.abs( Detector.Scalar * Scatterer.Perpendicular(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian) )**2 *  Detector.Mesh.dOmega.Radian) / Detector.Mesh.Omega.Radian

        if Detector.CouplingMode[0] == "Amplitude":
            Para = np.sum( np.abs( Detector.Scalar * Scatterer.Parallel(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian) )**2 *  Detector.Mesh.dOmega.Radian) / Detector.Mesh.Omega.Radian
            Perp = np.sum( np.abs( Detector.Scalar * Scatterer.Perpendicular(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian) )**2 *  Detector.Mesh.dOmega.Radian) / Detector.Mesh.Omega.Radian

        return Para + Perp



def Coupling(Scatterer, Detector):
    FarFieldPara, FarFieldPerp = Scatterer._FarField(Detector.Mesh.Phi.Radian, Detector.Mesh.Theta.Radian)

    if Detector.CouplingMode[1] == 'Centered':
        if Detector.CouplingMode[0] == "Intensity":
            Para, Perp = IntensityPointCoupling(Scalar0       = Detector.Scalar,
                                                Parallel      = FarFieldPara,
                                                Perpendicular = FarFieldPerp,
                                                SinMesh       = Detector.Mesh.SinMesh,
                                                dOmega        = Detector.Mesh.dOmega.Radian,
                                                Filter        = Detector.Filter.Radian)

            return Para + Perp

        if Detector.CouplingMode[0] == "Amplitude":
            Para, Perp = AmplitudePointCoupling(Scalar0       = Detector.Scalar,
                                                Parallel      = FarFieldPara,
                                                Perpendicular = FarFieldPerp,
                                                SinMesh       = Detector.Mesh.SinMesh,
                                                dOmega        = Detector.Mesh.dOmega.Radian,
                                                Filter        = Detector.Filter.Radian)

            return Para + Perp


    if Detector.CouplingMode[1] == 'Mean':

        if Detector.CouplingMode[0] == "Intensity":

            Para, Perp = IntensityMeanCoupling(Scalar0      = Detector.Scalar,
                                              Parallel      = FarFieldPara,
                                              Perpendicular = FarFieldPerp,
                                              SinMesh       = Detector.Mesh.SinMesh,
                                              dOmega        = Detector.Mesh.dOmega.Radian,
                                              Omega         = Detector.Mesh.Omega.Radian,
                                              Filter        = Detector.Filter.Radian)

            return Para + Perp

        if Detector.CouplingMode[0] == "Amplitude":
            Para, Perp = AmplitudeMeanCoupling(Scalar0       = Detector.Scalar,
                                               Parallel      = FarFieldPara,
                                               Perpendicular = FarFieldPerp,
                                               SinMesh       = Detector.Mesh.SinMesh,
                                               dOmega        = Detector.Mesh.dOmega.Radian,
                                               Omega         = Detector.Mesh.Omega.Radian,
                                              Filter        = Detector.Filter.Radian)

            return Para + Perp