
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_examples/CreatingDetectors/Coupling:LPMode.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_CreatingDetectors_Coupling:LPMode.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_CreatingDetectors_Coupling:LPMode.py:


LP Mode
=======

.. GENERATED FROM PYTHON SOURCE LINES 5-35

.. code-block:: default


    # sphinx_gallery_thumbnail_path = '../images/Coupling:LPMode.png'

    def run(Plot, Save):
        from PyMieSim.Source   import PlaneWave
        from PyMieSim.Detector import LPmode


        Source = PlaneWave(Wavelength   = 450e-9,
                          Polarization = 0,
                          E0           = 0)

        Detector = LPmode(Mode         = (1, 1),
                         Rotation     = 0.,
                         Sampling     = 201,
                         NA           = 0.4,
                         GammaOffset  = 0,
                         PhiOffset    = 40,
                         CouplingMode = 'Centered')

        if Plot:
            Detector.Plot()

        if Save:
            from pathlib import Path
            dir = f'docs/images/{Path(__file__).stem}'
            Detector.SaveFig(dir)

    if __name__ == '__main__':
        run(Plot=True, Save=False)


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  0.000 seconds)


.. _sphx_glr_download_auto_examples_CreatingDetectors_Coupling:LPMode.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: Coupling:LPMode.py <Coupling:LPMode.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: Coupling:LPMode.ipynb <Coupling:LPMode.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
