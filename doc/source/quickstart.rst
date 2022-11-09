****************
Quick Start
****************


Basic Usage
================

Creating an HTML report from a Jupyter notebook, is as simple as loading the
data to a Pandas DataFrame and instantiating :brand:`tslumen`'s ``HtmlReport``
class. A few conditions need to be met:

 - Index must be of type ``DatetimeIndex`` and have a recognizable frequency (``df.index.inferred_freq``)
 - Each column should represent a single time series
 - Column names need to be strings

Any non-numeric data included in the dataframe is discarded before processing.

.. code-block:: python

    import pandas as pd
    from tslumen import HtmlReport

    # create/read data into a data frame
    df = pd.DataFrame(...)

    # generate the report
    HtmlReport(
        df,                  # the timeseries dataframe
        meta={               # optional: dictionary with the metadata
            'frame': {...},  # <key: str>: <value: str>
            'series': {...}, # <column name: str>: <series description: str>
        }
    )




Adjusting the profiler's parameters
====================================

A lot of thought has gone into designing the profiling functions in such a
way that they require little to no adjusting, with the defaults working well in
most cases. Nevertheless, we still want to offer the ability to fine tune all
parameters, so that you're fully in control. Simple to use, yet completely
configurable.

To manually define the parameters of a given profiling function, simply supply
the desired overrides in dictionary format to ``HtmlReport``'s
``profiler_config`` parameter. Example:


.. code-block:: python

    HtmlReport(
        df,
        profiler_config={
            'kpss_stationarity': {'confidence_level': 0.1},
            'adfuller_stationarity': {'confidence_level': 0.1},
        }
    )


As illustrated in the example, ``profiler_config`` is a 2-level dictionary,
with the first level indexed by function name, and the second by parameter. To
find out exactly what profiling functions are available, their parameters and
acceptable values, refer to :doc:`the API documentation <index_api>`.
Alternatively, the full dictionary can be copied from a rendered version of
``HtmlReport`` under the "Execution" tab.



Run from the command line
===============================

:brand:`tslumen` leverages `Hydra <https://hydra.cc/>`_ for managing
configurations and exposing through a CLI. Essentially there are 5 classes of
arguments exposed by the interface:

 - ``input`` path to the input file [mandatory]
 - ``output`` path to the output file [defaults to ``stdout``]
 - ``reader`` for configuring how to parse the input file into a Pandas
   DataFrame.
 - ``profiler`` equivalent to the ``profiler_config`` parameter in
   ``HtmlReport``
 - ``scheduler`` to override the scheduler's configurations

For details on each of these, refer to :doc:`the API documentation<index_api>`.

A few examples.

Getting help -- notice the use of a pager, reason being the number of options
is quite large.

.. code-block:: bash

    tslumen --help | less

Processing a nicely formatted csv file, where the first column contains the
datetimes in an interpretable format and the data is separated by commas:

.. code-block:: bash

    tslumen input=my_dataset.csv output=tslumen-my_dataset.html
    # or
    tslumen input=my_dataset.csv > tslumen-my_dataset.html


Overriding a profiling function's parameter:

.. code-block:: bash

    tslumen input=my_dataset.csv profiler.kpss_stationarity.confidence_level=0.01 > out.html


To understand in more detail how applications built on Hydra work refer to
`their documentation <https://hydra.cc/docs/intro>`_.


Running the interactive dashboard
==================================

To produce an interactive dashboard, a ``Dashboard`` object should be used
instead of ``HtmlReport``. Once instantiated, a server needs to be spawned by
invoking the object's ``run_server`` method. Common arguments to override
include ``mode``, ``host`` and ``port``.

.. code-block:: python

    import pandas as pd
    from tslumen import Dashboard

    # create/read data into a data frame
    df = pd.DataFrame(...)

    # instantiate the Dashboard
    dashboard  = Dashboard(
        df,                  # the timeseries dataframe
        meta={               # optional: dictionary with the metadata
            'frame': {...},  # <key: str>: <value: str>
            'series': {...}, # <column name: str>: <series description: str>
        }
    )

    # run the server
    dashboard.run_server(mode="inline", host="localhost", port='8000', debug=True)

Refer to `JupyterDash's documentation
<https://medium.com/plotly/introducing-jupyterdash-811f1f57c02e>`_ for more
details.


.. note::

    In order to run the interactive dashboard all extra dependencies need to
    be installed. See :doc:`installation`.
