
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples/ExperimentCoupling/Experiment:Coupling-vs-diameter.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_ExperimentCoupling_Experiment:Coupling-vs-diameter.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_ExperimentCoupling_Experiment:Coupling-vs-diameter.py:


Coupling vs Diameter
====================

.. GENERATED FROM PYTHON SOURCE LINES 5-53

.. code-block:: default


    # sphinx_gallery_thumbnail_path = '../images/Experiment:Coupling-vs-diameter.png'

    def run(Plot, Save):
        import numpy as np
        from PyMieSim            import Material
        from PyMieSim.Scatterer  import Sphere
        from PyMieSim.Source     import PlaneWave
        from PyMieSim.Detector   import Photodiode
        from PyMieSim.Experiment import ScatSet, SourceSet, Setup, DetectorSet

        scatKwargs   = { 'Diameter'    : np.linspace(400e-9, 2000e-9, 200),
                         'Material'    : Material('BK7'),
                         'nMedium'     : [1] }

        sourceKwargs = { 'Wavelength'   : 1e-6,
                         'Polarization' : [0,30,60,90]}

        detecKwargs  = { 'NA'           : 0.2,
                         'Sampling'     : 300,
                         'GammaOffset'  : 70,
                         'PhiOffset'    : [0],
                         'CouplingMode' : 'Centered'}


        detecSet   = DetectorSet(Detector = Photodiode, kwargs = detecKwargs)

        scatSet    = ScatSet(Scatterer = Sphere,  kwargs = scatKwargs )

        sourceSet  = SourceSet(Source = PlaneWave, kwargs = sourceKwargs )

        Experiment = Setup(ScattererSet = scatSet,
                           SourceSet    = sourceSet,
                           DetectorSet  = detecSet)

        Data = Experiment.Get('Coupling')

        if Plot:
            Data.Plot(y='Coupling', x='Diameter')

        if Save:
            from pathlib import Path
            dir = f'docs/images/{Path(__file__).stem}'
            Data.SaveFig(Directory=dir, y='Coupling', x='Diameter')


    if __name__ == '__main__':
        run(Plot=True, Save=False)


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  0.000 seconds)


.. _sphx_glr_download_auto_examples_ExperimentCoupling_Experiment:Coupling-vs-diameter.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: Experiment:Coupling-vs-diameter.py <Experiment:Coupling-vs-diameter.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: Experiment:Coupling-vs-diameter.ipynb <Experiment:Coupling-vs-diameter.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
