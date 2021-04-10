#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy  as np
import pandas as pd
from beartype           import beartype
from typing             import Union
from multiprocessing    import Process
from scipy.optimize     import minimize

from PyMieSim.Source    import PlaneWave
from PyMieSim.NdArray   import PMSArray, Opt5DArray
from PyMieSim.Detector  import LPmode, Photodiode
from PyMieSim.Scatterer import Sphere, WMSample

from PyMieSim.DataFrame import ( ExperimentalDataFrame,
                                 S1S2DataFrame,
                                 EfficiencesDF,
                                 ExperimentDF)

from PyMieSim.Config    import ( MetricList,
                                 DetectorParamList,
                                 SourceParamList,
                                 DefaultConfig,
                                 DefaultConfigEff )


OUTPUTTYPE = ['optimizer','numpy', 'pymiesim', 'dataframe']
exList = Union[list, np.ndarray]
exfloat = Union[bool, int, float]
exArg = Union[float, int, list, np.ndarray]

class ScatSet(object):

    @beartype
    def __init__(self,
                 DiameterList  :  exList,
                 IndexList     :  exList,
                 nMedium       :  exfloat    = 1.0,
                 ScattererType :  str        = 'Sphere'):

        self._Diameter, self._Index = None, None

        self.Diameter, self.Index = DiameterList, IndexList

        self.nMedium = nMedium

        self.shape = np.shape(self.Diameter) + np.shape(self.Index)


    @property
    def Diameter(self):
        return self._Diameter

    @Diameter.setter
    def Diameter(self, val):
        if not isinstance(val, (list, np.ndarray)): val = [val]
        self._Diameter = val

    @property
    def Index(self):
        return self._Index

    @Index.setter
    def Index(self, val):
        if not isinstance(val, (list, np.ndarray)): val = [val]
        self._Index = val

    def Generator(self, Source):
        for diameter in self.Diameter:
            for RI in self.Index:
                yield Sphere(Diameter  = diameter,
                             Source    = Source,
                             Index     = RI,
                             nMedium   = self.nMedium,
                             MuSphere  = 1.0,
                             MuMedium  = 1.0)


class SourceSet(object):

    @beartype
    def __init__(self,
                 WavelengthList   :   exArg,
                 PolarizationList :   exArg = [0],
                 SourceType       :   str   = 'PlaneWave'):


        self._Wavelength, self._Polarization = None, None

        self.Wavelength = WavelengthList

        self.Polarization = PolarizationList

        self.SourceType = SourceType

        self.shape = np.shape(self.Wavelength) + np.shape(self.Polarization)


    @property
    def Wavelength(self):
        return self._Wavelength

    @Wavelength.setter
    def Wavelength(self, val):
        if not isinstance(val, (list, np.ndarray)): val = [val]
        self._Wavelength = val

    @property
    def Polarization(self):
        return self._Polarization

    @Polarization.setter
    def Polarization(self, val):
        if not isinstance(val, (list, np.ndarray)): val = [val]
        self._Polarization = val


    def Generator(self):
        for wavelength in self.Wavelength:
            for polarization in self.Polarization:
                yield PlaneWave(Wavelength   = wavelength,
                                Polarization = polarization,
                                E0           = 1)


class Setup(object):

    @beartype
    def __init__(self,
                 ScattererSet : ScatSet            = None,
                 SourceSet    : SourceSet          = None,
                 DetectorSet  : Union[tuple, list] = None):


        self.MetricList   = MetricList

        self.DetectorSet  = DetectorSet

        self.SourceSet    = SourceSet

        self.ScattererSet = ScattererSet

        self.DetectorSetName = []
        for nd, dectector in enumerate(self.DetectorSet):
            self.DetectorSetName.append( f"Detector {nd}" )


    def Efficiencies(self, AsType='numpy'):
        """Methode generate a Pandas Dataframe of scattering efficiencies
        (Qsca) vs. scatterer diameter vs. scatterer refractive index.

        Returns
        -------
        :class:`pandas.DataFrame`
            Dataframe containing Qsca vs. Wavelength, Diameter vs. Index.

        """

        assert AsType.lower() in OUTPUTTYPE, \
        f'Invalid type {AsType}, valid choices are {OUTPUTTYPE}'

        config = DefaultConfigEff

        config['dimension'] = { 'wavelength'   : self.SourceSet.Wavelength,
                                'polarization' : self.SourceSet.Polarization,
                                'diameter'     : self.ScattererSet.Diameter,
                                'ri'           : self.ScattererSet.Index}


        self.GetShape(config)

        Array = np.empty(config['size']*3)


        i = 0
        for source in self.SourceSet.Generator():
            for scat in self.ScattererSet.Generator(Source=source):
                Qsca, Qext, Qabs = scat.GetEfficiencies()
                Array[i]   = Qsca
                Array[i+1] = Qext
                Array[i+2] = Qabs
                i+=3

        return self.ReturnType(Array     = Array.reshape([3]+config['shape']),
                               AsType    = AsType,
                               conf      = config)


    def Coupling(self, AsType='numpy'):
        """Property method which return a n by m by l OptArray array, n being the
        number of detectors, m is the point evaluated for the refractive index,
        l is the nomber of point evaluted for the scatterers diameters.

        Returns
        -------
        OptArray
            Raw array of detectors coupling.

        """


        assert AsType.lower() in OUTPUTTYPE, \
        f'Invalid type {AsType}, valid choices are {OUTPUTTYPE}'

        config = DefaultConfig

        config['dimension'] = { 'detector'     : self.DetectorSetName,
                                'wavelength'   : self.SourceSet.Wavelength,
                                'polarization' : self.SourceSet.Polarization,
                                'diameter'     : self.ScattererSet.Diameter,
                                'ri'           : self.ScattererSet.Index}

        self.GetShape(config)

        Array = np.empty(config['size'])

        i = 0
        for nd, detector in enumerate(self.DetectorSet):
            for source in self.SourceSet.Generator():
                for scat in self.ScattererSet.Generator(Source=source):

                    Array[i] = detector.Coupling(Scatterer = scat)
                    i += 1;

        return self.ReturnType(Array     = Array.reshape(config['shape']),
                               AsType    = AsType,
                               conf      = config)


    def ReturnType(self, Array, AsType, conf):

        if AsType.lower() == 'optimizer':
            return Opt5DArray(Array)

        elif AsType.lower() == 'numpy':
            return Array

        elif AsType.lower() == 'pymiesim':
            return PMSArray(array = Array, conf = conf)

        elif AsType.lower() == 'dataframe':
            return self.MakeDF(conf, Array)


    def MakeDF(self, conf, Array):

        MI = pd.MultiIndex.from_product(list(conf['dimension'].values()),
                                        names = list(conf['dimension'].keys()))

        if conf['name'].lower() == 'efficiencies':
            return EfficiencesDF(Array.reshape([conf['size'],3]),
                                 index   = MI,
                                 columns = ['Qsca', 'Qext', 'Qabs'])


        elif  conf['name'].lower() == 'coupling':
            return ExperimentDF(Array.flatten(),
                                index   = MI,
                                columns = ['Coupling'])


    def GetShape(self, conf):
        shape = []
        size  = 1
        for item in conf['dimension'].values():
            shape += [len(item)]
            size  *= len(item)

        conf['shape'] = shape
        conf['size']  = size


    def Optimize(self, *args, **kwargs):
        return Optimizer(Setup = self, *args, **kwargs)


class Optimizer:

    @beartype
    def __init__(self,
                 Setup         : Setup,
                 Metric        : str,
                 Parameter     : list,
                 X0            : list,
                 WhichDetector : int,
                 MinVal        : list,
                 MaxVal        : list,
                 Optimum       : str,
                 FirstStride   : Union[float, int],
                 MaxIter       : int               = 50,
                 Tol           : Union[float, int] = 1e-10):

        assert Metric.lower() in MetricList, f"Metric {Metric} not in the MetricList \n{MetricList}"
        assert all(len(x)==len(Parameter) for x in [X0, MinVal, MaxVal ]  ), f'Lenght of parameters, X0, MinVal, MaxVal not equal'

        self.Setup           = Setup
        self.Metric          = Metric
        self.Parameters      = Parameter
        self.X0              = X0
        self.WhichDetector   = WhichDetector
        self.MinVal          = MinVal
        self.MaxVal          = MaxVal
        self.FirstStride     = FirstStride
        self.MaxIter         = MaxIter
        self.Tol             = Tol

        if Optimum.lower()   == 'maximum': self.sign = -1
        elif Optimum.lower() == 'minimum': self.sign = 1

        self.Result = self.Run()


    def ComputePenalty(self, Parameters, x, MaxVal, MinVal, factor=100):
        Penalty = 0
        for n in range(len(Parameters)):
            if MinVal[n] and x[0]< MinVal[n]:
                Penalty += np.abs( x[0]*factor );
                x[0]     = self.MinVal[n]

            if MinVal[n] and x[0]> MaxVal[n]:
                Penalty += np.abs( x[0]*factor );
                x[0]     = self.MaxVal[n]

        return Penalty


    def UpdateConfiguration(self, Parameters, x, WhichDetector):

        for n in range(len(Parameters)):
            if Parameters[n] in DetectorParamList:
                setattr(self.Setup.DetectorSet[WhichDetector], Parameters[0], x[0])

            elif Parameters[n] in SourceParamList:
                setattr(self.Setup.SourceSet.Source, Parameters[0], x[0])


    def Run(self):

        def EvalFunc(x):
            Penalty = self.ComputePenalty(self.Parameters, x, self.MaxVal, self.MinVal, factor=100)

            self.UpdateConfiguration(self.Parameters, x, self.WhichDetector)

            Cost = self.Setup.Coupling(AsType='Optimizer').Cost(self.Metric)

            return self.sign * np.abs(Cost) + Penalty

        Minimizer = Caller(EvalFunc, ParameterName = self.Parameters)

        return minimize(fun      = Minimizer.optimize,
                        x0       = self.X0,
                        method   = 'COBYLA',
                        tol      = self.Tol,
                        options  = {'maxiter': self.MaxIter, 'rhobeg':self.FirstStride})


class Caller:
    def __init__(self, function, ParameterName: list):
        self.ParameterName = ParameterName
        self.f = function # actual objective function
        self.num_calls = 0 # how many times f has been called
        self.callback_count = 0 # number of times callback has been called, also measures iteration count
        self.list_calls_inp = [] # input of all calls
        self.list_calls_res = [] # result of all calls
        self.decreasing_list_calls_inp = [] # input of calls that resulted in decrease
        self.decreasing_list_calls_res = [] # result of calls that resulted in decrease
        self.list_callback_inp = [] # only appends inputs on callback, as such they correspond to the iterations
        self.list_callback_res = [] # only appends results on callback, as such they correspond to the iterations

    def optimize(self, x):
        """Executes the actual simulation and returns the result, while
        updating the lists too. Pass to optimizer without arguments or
        parentheses."""
        result = self.f(x) # the actual evaluation of the function
        if not self.num_calls: # first call is stored in all lists
            self.decreasing_list_calls_inp.append(x)
            self.decreasing_list_calls_res.append(result)
            self.list_callback_inp.append(x)
            self.list_callback_res.append(result)
        elif result < self.decreasing_list_calls_res[-1]:
            self.decreasing_list_calls_inp.append(x)
            self.decreasing_list_calls_res.append(result)
        self.list_calls_inp.append(x)
        self.list_calls_res.append(result)
        self.num_calls += 1


        if len(self.ParameterName) == 1:

            text = """ \
            Call Number : {0} \
            \t {1}: {2:.5e} \
            \t Cost+Penalty: {3:.10e} \
            """.format(self.num_calls,
                       self.ParameterName[0],
                       x[0],
                       result)

        if len(self.ParameterName) == 2:
            text = """ \
            Call Number : {0} \
            \t {1}: {2:.5e} \
            \t {3}: {4:.5e} \
            \t Cost+Penalty: {5:.10e} \
            """.format(self.num_calls,
                       self.ParameterName[0],
                       x[0],
                       self.ParameterName[1],
                       x[1],
                       result)

        print(text)
        return result


class SampleSet(object):

    def __init__(self,
                 gList:           list,
                 LcList:          list,
                 D:               float,
                 Nc:              float,
                 Detector:        Photodiode,
                 Source:          PlaneWave,
                 Npts:            int = 201,
                 ):

        self.gList, self.LcList = gList, LcList

        self.D = D; self.Nc = Nc

        self.Detector, self.Source = Detector, Source



    @property
    def DataFrame(self):
        """Property method which return pandas.DataFrame of the scattering-
        detector coupling for the different diameter and refracive index
        evaluated.
        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame of detectors coupling.
        """
        MI = pd.MultiIndex.from_product([range(len(self.Detectors)), self.ScattererSet.DiameterList, self.ScattererSet.RIList],
                                        names=['Detectors','Diameter','RI',])


        df = ExperimentalDataFrame(index = MI, columns = ['Coupling'])

        df.attrs['Detectors'] = self.Detectors

        for nr, RI in enumerate( self.ScattererSet.RIList ):

            for nd, Diameter in enumerate(self.ScattererSet.DiameterList):

                for nDetector, Detector in enumerate(self.Detectors):

                    Scat = Sample(g           = g,
                                  lc          = lc,
                                  D           = self.D,
                                  Nc          = self.Nc,
                                  Source      = LightSource,
                                  Meshes      = self.Detector.Meshes)

                    Coupling = Detector.Coupling(Scatterer = Scat)

                    df.at[(nDetector, Diameter, RI),'Coupling'] = Coupling

        df.Coupling = df.Coupling.astype(float)

        df['Mean'] = df.groupby(['Detectors','Diameter']).Coupling.transform('mean')

        df['STD'] = df.groupby(['Detectors','Diameter']).Coupling.transform('std')

        return df




    @property
    def Coupling(self):
        """Property method which return a n by m by l OptArray array, n being the
        number of detectors, m is the point evaluated for the refractive index,
        l is the nomber of point evaluted for the scatterers diameters.
        Returns
        -------
        OptArray
            Raw array of detectors coupling.
        """
        temp = np.empty( [len(self.Detectors), len(self.ScattererSet.RIList), len(self.ScattererSet.DiameterList) ] )

        for nDetector, Detector in enumerate(self.Detectors):

            for nIndex, RI in enumerate(self.ScattererSet.RIList):
                for nDiameter, Diameter in enumerate(self.ScattererSet.DiameterList):

                    Samp = Sample(g           = g,
                                  lc          = lc,
                                  D           = self.D,
                                  Nc          = self.Nc,
                                  Source      = self.Source,
                                  Meshes      = self.Detector.Meshes)

                    Coupling = Detector.Coupling(Scatterer = Samp)

                    temp[nDetector, nIndex, nDiameter] = Coupling

        return OptArray(temp)


# -
