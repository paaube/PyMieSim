#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import copy
import matplotlib.pyplot as plt
from itertools import product

from PyMieSim.Config import MetricList
from PyMieSim.utils  import FormatStr, FormatString
from PyMieSim.Config import EFFTYPE



class PMSArray(object):

    def __init__(self, array, conf):
        self.data = array
        self.conf = conf


    @FormatStr
    def Cost(self, arg = 'max'):
        """Method return cost function evaluated as defined in the ___ section
        of the documentation.

        Parameters
        ----------
        arg : :class:`str`
            String representing the cost function.

        Returns
        -------
        :class:`float`
            The evaluated cost.

        """

        arg = arg.lower().split('+', 2)

        if len(arg) == 1:
            if   'max'  in arg : return np.max(self)
            elif 'min'  in arg : return np.min(self)
            elif 'mean' in arg : return np.mean(self)

        if len(arg) == 2:
            if   arg[0] == 'rsd'          : func = self.rsd
            elif arg[0] == 'monotonic'    : func = self.Monotonic

            if   arg[1] == 'ri'           : return np.mean( func(self.data, axis = 4) )
            elif arg[1] == 'diameter'     : return np.mean( func(self.data, axis = 3) )
            elif arg[1] == 'polarization' : return np.mean( func(self.data, axis = 2) )
            elif arg[1] == 'wavelength'   : return np.mean( func(self.data, axis = 1) )
            elif arg[1] == 'detector'     : return np.mean( func(self.data, axis = 0) )

        raise ValueError(f"Invalid metric input. \nList of metrics: {MetricList}")


    @FormatStr
    def Monotonic(self, axis):
        """Method compute and the monotonic value of specified axis.
        The method then return a new PMSArray daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`PMSArray`
            New PMSArray instance containing the monotonic metric value of axis.

        """
        axis = axis.lower()

        arr  = np.gradient(self.data,
                           axis = self.conf['order'][axis])\
                           .std( axis = self.conf['order'][axis])

        conf = self.UpdateConf(axis)

        return PMSArray(array=arr, conf=conf)


    @FormatStr
    def Mean(self, axis):
        """Method compute and the mean value of specified axis.
        The method then return a new PMSArray daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`PMSArray`
            New PMSArray instance containing the mean value of axis.

        """
        axis = axis.lower()

        arr  = np.mean(self.data, axis=self.conf['order'][axis] )

        conf = self.UpdateConf(axis)

        return PMSArray(array=arr, conf=conf)


    @FormatStr
    def Std(self, axis):
        """Method compute and the std value of specified axis.
        The method then return a new PMSArray daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`PMSArray`
            New PMSArray instance containing the std value of axis.

        """
        axis = axis.lower()

        arr  = np.std(self.data, axis=self.conf['order'][axis] )

        conf = self.UpdateConf(axis)

        return PMSArray(array=arr, conf=conf)


    @FormatStr
    def Rsd(self, axis):
        """Method compute and the rsd value of specified axis.
        The method then return a new PMSArray daughter object compressed in
        the said axis.
        rsd is defined as std/mean.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`PMSArray`
            New PMSArray instance containing the rsd value of axis.

        """
        axis = axis.lower()

        arr  = np.std(self.data, axis=self.conf['order'][axis] ) \
              /np.mean(self.data, axis=self.conf['order'][axis] )

        conf = self.UpdateConf(axis)

        return PMSArray(array=arr, conf=conf)


    def UpdateConf(self, axis):
        """Method update the configuration variable (config) in order to
        ouput a new :class:`PMSArray` instance.
        A new instance is created each time a reduction operation is applied,
        such as :func:`Mean`, :func:`Std`, :func:`Rsd`, :func:`Monotonic` .

        Parameters
        ----------
        axis : str
            Key vale of the self dict for which we apply a reduction opration.

        Returns
        -------
        type
            New instance of :class:`PMSArray` .

        """

        newConf = self.conf.copy()#copy.copy(self.conf)  <----- I don't like it!

        newConf['order'].pop(axis)
        newConf['dimension'].pop(axis)

        for n, key in enumerate(newConf['order'].keys()):
            newConf['order'][key] = n

        return newConf


    @FormatStr
    def Plot(self, x,  Scale = 'linear', *args, **kwargs):
        """Method plot the multi-dimensional array with the x key as abscissa.
        args and kwargs can be passed as standard input to matplotlib.pyplot.

        Parameters
        ----------
        x : str
            Key of the self dict which represent the abscissa.
        Scale : str
            Options allow to switch between log and linear scale ['log', 'linear'].

        """

        yLog = False; xLog = False

        if Scale in ['lin', 'linear']        : yLog = False; xLog = False;
        if Scale in ['log', 'logarithmic']   : yLog = True;  xLog = True;
        if Scale in ['xlog', 'xlogarithmic'] : yLog = False; xLog = True;
        if Scale in ['ylog', 'ylogarithmic'] : yLog = True;  xLog = False;

        figDict = {unit : plt.subplots(figsize=(8,4))
                   for unit in set(self.conf['y']['unit'].values())}

        DimSlicer, xval = self.GetSlicer(x)

        for idx in product(*DimSlicer):

            label  = self.GetLabels(x, idx)

            xlabel, ylabel, unit = self.GetAxesLabel(x, idx)

            figure, ax = figDict[unit]

            ax.plot(xval, self.data[idx], label  = label, *args, **kwargs)

            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(fontsize=6)

            if yLog: ax.set_yscale('log')
            if xLog: ax.set_xscale('log')

        for key, (fig,ax) in figDict.items():
            ax.grid()

        plt.show()


    def GetAxesLabel(self, axis, idx):
        VarIndex    = idx[-1]
        yname       = self.conf['y']['list'][VarIndex]
        unit        = self.conf['y']['unit'][yname]
        ylabel      = self.conf['y']['label'][yname] + ' ' + unit
        xlabel      = self.conf['label'][axis] + ' ' + self.conf['unit'][axis]

        return xlabel, ylabel, unit


    def GetLabels(self, axis, idx):
        """Method generate and return the legend text for the specific plot.

        Parameters
        ----------
        axis : :class:`str`
            Axis which is used for x-axis of the specific plot
        idx : :class:`tuple`
            Dimension indices of the specific plot

        Returns
        -------
        :class:`str`
            Text for the legend

        """

        Efficiency  = False
        label       = ''
        VarIndex    = idx[-1]
        yname       = self.conf['y']['list'][VarIndex]

        if yname in EFFTYPE:
            label       = f"{yname} | " + label
            Efficiency  = True

        for key in self.conf['order']:

            if axis != key.lower():

                index  = idx[self.conf['order'][key]]

                val = self.conf['dimension'][key][index]

                if key.lower() == 'material' :
                    val = val.__str__()

                format = self.conf['format'][key]

                if Efficiency and key == 'Detector':
                        continue

                label += f"{key}= {val:{format}} | "

        return label


    def GetSlicer(self, x):
        shape = list(self.data.shape)

        for key, order in self.conf['order'].items():

            if key.lower() == x.lower():
                shape[order] = None
                xval         = self.conf['dimension'][key]

        DimSlicer = [range(s) if s is not None else [slice(None)] for s in shape]

        return DimSlicer, xval


    def __getitem__(self, key):
        index = self.conf['y']['list'].index(key)
        return self.data[..., index].squeeze()


    def __str__(self):
        name = self.conf['y']['name']
        text =  f'PyMieArray \nVariable: {name}\n' + '='*90 + '\n'
        text += f"{'Parameter':13s}\n" + '-'*90 + '\n'
        for key, val in self.conf['order'].items():
            text += f"""{key:13s}\
                        | dimension = {val:2d}\
                        | size = {len(self.conf['dimension'][key]):2d}\
                         \n"""

        text += '='*90 + '\n'
        return text



class Opt5DArray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        this = np.array(*args, **kwargs, copy=False)
        this = np.asarray(this).view(cls)

        return this


    def __array_finalize__(self, obj):
        pass


    def __init__(self, arr, Name=''):
        self.Name         = Name

        self.dim = { 'detector'     : True,
                     'wavelength'   : True,
                     'polarization' : True,
                     'diameter'     : True,
                     'index'        : True}

    @FormatStr
    def DefineCostFunc(self, arg):
        arg = arg.lower().split('+', 2)

        if len(arg) == 1:
            if   'max'  in arg : self.CostFunc = np.max
            elif 'min'  in arg : self.CostFunc = np.min
            elif 'mean' in arg : self.CostFunc = np.mean

        if len(arg) == 2:
            if   arg[0] == 'rsd'       : func = self.rsd
            elif arg[0] == 'monotonic' : func = self.Monotonic
            elif arg[0] == 'max'       : func = np.max
            elif arg[0] == 'min'       : func = np.min
            elif arg[0] == 'mean'      : func = np.mean


            if   arg[1] == 'all'          : self.CostFunc = np.mean( func(self) )
            elif arg[1] == 'ri'           : self.CostFunc = np.mean( func(self, axis = 4) )
            elif arg[1] == 'diameter'     : self.CostFunc = np.mean( func(self, axis = 3) )
            elif arg[1] == 'polarization' : self.CostFunc = np.mean( func(self, axis = 2) )
            elif arg[1] == 'wavelength'   : self.CostFunc = np.mean( func(self, axis = 1) )
            elif arg[1] == 'detector'     : self.CostFunc = np.mean( func(self, axis = 0) )

            raise ValueError(f"Invalid metric input. \nList of metrics: {MetricList}")



    def Cost(self):

        return self.CostFunc(self)




    def Monotonic(self, axis):

        Grad = np.gradient(self, axis = axis)

        STD = Grad.std( axis = axis)

        return STD[0]


    def rsd(self, array, axis):
        return np.std(array, axis)/np.mean(array, axis)


    def RIMonotonic(self):

        Grad = np.gradient(self, axis = 0)

        STD = Grad.std( axis = 0)

        return STD[0]
