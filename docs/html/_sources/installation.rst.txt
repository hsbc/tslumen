*************
Installation
*************


From PyPI
=====================


.. code-block:: bash

    pip install -U tslumen



From a local file
==================

If you have access to a wheel or egg, save it to a local directory and run:

.. code-block:: bash

    pip install -U tslumen --find-links <package location>



From source
==============

To install :brand:`tslumen` from source, download the code (e.g. by cloning the
repository), change to the proper directory and execute:

.. code-block:: bash

    python setup.py install
    # or
    make install



Extra dependencies
===================

To install the extra dependencies and be able to use the interactive
functionality (see :class:`tslumen.Dashboard`):

.. code-block:: bash

    pip install -U tslumen[extras]



Known issues
==============

In some cases it might be required to manually enable the widgets. If an
`ImportError` is thrown, referencing ipywidgets, execute the following code:

.. code-block:: bash

    jupyter nbextension enable --py widgetsnbextension

