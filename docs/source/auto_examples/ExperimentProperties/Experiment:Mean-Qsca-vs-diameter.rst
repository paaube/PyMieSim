
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples/ExperimentProperties/Experiment:Mean-Qsca-vs-diameter.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_ExperimentProperties_Experiment:Mean-Qsca-vs-diameter.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_ExperimentProperties_Experiment:Mean-Qsca-vs-diameter.py:


Mean Qsca vs Diameter
=====================

.. GENERATED FROM PYTHON SOURCE LINES 5-58

.. code-block:: default


    def run(Plot, Save):
        import numpy as np
        from PyMieSim            import Material
        from PyMieSim.Scatterer  import Sphere
        from PyMieSim.Source     import PlaneWave
        from PyMieSim.Detector   import Photodiode
        from PyMieSim.Experiment import ScatSet, SourceSet, Setup, DetectorSet

        scatKwargs   = { 'Diameter' : np.geomspace(6.36e-09, 10000e-9, 500),
                         'Material' : [Material('Silver')],
                         'nMedium'  : [1] }

        sourceKwargs = { 'Wavelength'   : [400e-9, 900e-9, 1200e-9, 1600e-9],
                         'Polarization' : [0]}

        scatSet   = ScatSet(Scatterer = Sphere,  kwargs = scatKwargs )

        sourceSet = SourceSet(Source = PlaneWave, kwargs = sourceKwargs )

        Experiment = Setup(ScattererSet = scatSet,
                           SourceSet    = sourceSet)

        Data = Experiment.Get(Input=['Qsca', 'Qabs'])

        MeanData = Data.Mean('wavelength')

        print(MeanData)

        if Plot:
            Data.Plot(y='Qabs', x='diameter', Scale='log')

        if Save:
            from pathlib import Path
            dir = f'docs/images/{Path(__file__).stem}'
            Data.SaveFig(Directory=dir, y='Qabs', x='diameter', Scale='log')

    if __name__ == '__main__':
        run(Plot=True, Save=False)


    #___________________________OUTPUT___________________________________
    #
    # PyMieArray
    # Variable: ['qsca', 'qabs']
    # ========================================================================================================================
    # Parameter
    # ------------------------------------------------------------------------------------------------------------------------
    # Polarization [Degree]                                 | dimension = 0                        | size      = 1
    # Diameter [m]                                          | dimension = 1                        | size      = 500
    # Material refractive index [1]                         | dimension = 2                        | size      = 1
    # Medium refractive index [1]                           | dimension = 3                        | size      = 1
    # ========================================================================================================================


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  0.000 seconds)


.. _sphx_glr_download_auto_examples_ExperimentProperties_Experiment:Mean-Qsca-vs-diameter.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: Experiment:Mean-Qsca-vs-diameter.py <Experiment:Mean-Qsca-vs-diameter.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: Experiment:Mean-Qsca-vs-diameter.ipynb <Experiment:Mean-Qsca-vs-diameter.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
