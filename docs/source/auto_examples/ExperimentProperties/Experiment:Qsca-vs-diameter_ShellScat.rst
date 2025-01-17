
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples/ExperimentProperties/Experiment:Qsca-vs-diameter_ShellScat.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_ExperimentProperties_Experiment:Qsca-vs-diameter_ShellScat.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_ExperimentProperties_Experiment:Qsca-vs-diameter_ShellScat.py:


Qsca vs Diameter Shell Scat
===========================

.. GENERATED FROM PYTHON SOURCE LINES 5-63

.. code-block:: default


    def run(Plot, Save):
        import numpy as np
        from PyMieSim            import Material
        from PyMieSim.Scatterer  import ShellSphere
        from PyMieSim.Source     import PlaneWave
        from PyMieSim.Detector   import Photodiode
        from PyMieSim.Experiment import ScatSet, SourceSet, Setup, DetectorSet

        scatKwargs   = { 'CoreDiameter'     : np.geomspace(10e-09, 600e-9, 500),
                         'ShellWidth'       : [200e-9, 400e-9],
                         'CoreIndex'        : [1],
                         'ShellIndex'       : [1.3],
                         'nMedium'          : 1 }

        sourceKwargs = { 'Wavelength'   : [200e-9],
                         'Polarization' : [0]}

        scatSet   = ScatSet(Scatterer = ShellSphere,  kwargs = scatKwargs )

        sourceSet = SourceSet(Source = PlaneWave, kwargs = sourceKwargs )

        Experiment = Setup(ScattererSet = scatSet,
                           SourceSet    = sourceSet)

        Data = Experiment.Get(Input=['Qsca', 'Qback'])

        print(Data)

        if Plot:
            Data.Plot(y=['Qsca'], x='Core diameter', Scale='lin')

        if Save:
            from pathlib import Path
            dir = f'docs/images/{Path(__file__).stem}'
            Data.SaveFig(Directory=dir, y=['Qsca'], x='Core diameter', Scale='lin')

    if __name__ == '__main__':
        run(Plot=True, Save=False)




    #___________________________OUTPUT___________________________________
    #
    # PyMieArray
    # Variable: ['qsca', 'qback']
    # ==========================================================================================
    # Parameter
    # ------------------------------------------------------------------------------------------
    # wavelength                           | dimension =  0                        | size =  1
    # polarization                         | dimension =  1                        | size =  1
    # corediameter                         | dimension =  2                        | size = 500
    # shellwidth                           | dimension =  3                        | size =  2
    # coreindex                            | dimension =  4                        | size =  1
    # shellindex                           | dimension =  5                        | size =  1
    # nmedium                              | dimension =  6                        | size =  1
    # ==========================================================================================


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  0.000 seconds)


.. _sphx_glr_download_auto_examples_ExperimentProperties_Experiment:Qsca-vs-diameter_ShellScat.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: Experiment:Qsca-vs-diameter_ShellScat.py <Experiment:Qsca-vs-diameter_ShellScat.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: Experiment:Qsca-vs-diameter_ShellScat.ipynb <Experiment:Qsca-vs-diameter_ShellScat.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
