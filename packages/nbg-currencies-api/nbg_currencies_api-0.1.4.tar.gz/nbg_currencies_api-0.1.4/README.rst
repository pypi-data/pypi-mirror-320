|PyPI version| |codecov| # NBG Currency Service

``NBGCurrencyService`` is a Python library designed to fetch and
normalize currency exchange rates from the National Bank of Georgia
(NBG) API. It provides both synchronous and asynchronous functionality,
making it suitable for various applications.

--------------

Features
--------

-  Fetch exchange rates for the current date or a specific date.
-  Retrieve rates for all currencies or a specific currency.
-  Supports both synchronous and asynchronous modes.
-  Easy-to-use interface with well-structured data models.

--------------

Installation
------------

Install the package
~~~~~~~~~~~~~~~~~~~

.. code:: bash

   pip install nbg-currency-api

For Asynchronous Support
~~~~~~~~~~~~~~~~~~~~~~~~

To enable async mode, install with the optional ``aiohttp`` dependency:

.. code:: bash

   pip install nbg-currency-api[async]

--------------

Usage
-----

Synchronous Mode
~~~~~~~~~~~~~~~~

Fetch rates for all currencies on the current date:

.. code:: python

   from nbg_currency_api import NBGCurrencyService

   service = NBGCurrencyService()
   data = service.fetch()
   print(data)

Fetch rates for a specific currency on a specific date:

.. code:: python

   from datetime import datetime
   from nbg_currency_api import NBGCurrencyService, CurrencyEnum

   service = NBGCurrencyService(
       date=datetime(2023, 12, 25), currency=CurrencyEnum.USD
   )
   data = service.fetch()
   print(data)

--------------

Asynchronous Mode
~~~~~~~~~~~~~~~~~

Fetch rates asynchronously for a specific currency:

.. code:: python

   import asyncio
   from nbg_currency_api import NBGCurrencyService, CurrencyEnum, ClientModeEnum

   async def main():
       service = NBGCurrencyService(currency=CurrencyEnum.EUR, mode=ClientModeEnum.ASYNC)
       data = await service.afetch()
       print(data)

   asyncio.run(main())

--------------

Data Models
-----------

``CurrencyDataResponse``
~~~~~~~~~~~~~~~~~~~~~~~~

This is the structured response returned by the service after fetching
and normalizing data.

+-----------------+------------------+--------------------------------+
| Field           | Type             | Description                    |
+=================+==================+================================+
| ``date``        | ``datetime``     | The date for the rates         |
+-----------------+------------------+--------------------------------+
| ``currencies``  | ``List[Cur       | List of currency rate items    |
|                 | rencyRateItem]`` |                                |
+-----------------+------------------+--------------------------------+

``CurrencyRateItem``
~~~~~~~~~~~~~~~~~~~~

Represents details of a single currency rate.

================= ============ ===========================
Field             Type         Description
================= ============ ===========================
``code``          ``str``      ISO code of the currency
``quantity``      ``int``      Quantity for the rate
``rateFormated``  ``str``      Formatted rate string
``diffFormated``  ``str``      Formatted difference string
``rate``          ``float``    Exchange rate
``name``          ``str``      Currency name
``diff``          ``float``    Rate difference
``date``          ``datetime`` Date of the rate
``validFromDate`` ``datetime`` Start date for the rate
================= ============ ===========================

--------------

Configuration
-------------

Supported Currencies
~~~~~~~~~~~~~~~~~~~~

The ``CurrencyEnum`` includes all ISO codes of supported currencies,
such as: - ``CurrencyEnum.USD`` - ``CurrencyEnum.EUR`` -
``CurrencyEnum.GBP``

Modes
~~~~~

-  **``SYNC``** (default): Use synchronous requests with the ``fetch``
   method.
-  **``ASYNC``**: Use asynchronous requests with the ``afetch`` method.

--------------

Example Output
--------------

Fetching exchange rates for USD:

.. code:: python

   from nbg_currency_api import NBGCurrencyService, CurrencyEnum

   service = NBGCurrencyService(currency=CurrencyEnum.USD)
   data = service.fetch()

   print(data)

Sample output:

.. code:: python

   CurrencyDataResponse(
       date=datetime.datetime(2025, 1, 7, 0, 0),
       currencies=[
           CurrencyRateItem(
               code='USD',
               quantity=1,
               rateFormated='3.20',
               diffFormated='+0.02',
               rate=3.2,
               name='US Dollar',
               diff=0.02,
               date=datetime.datetime(2025, 1, 7, 0, 0),
               validFromDate=datetime.datetime(2025, 1, 6, 0, 0)
           )
       ]
   )

--------------

License
-------

This project is licensed under the MIT License. See the
`LICENSE <LICENSE>`__ file for more details.

.. |PyPI version| image:: https://img.shields.io/pypi/v/nbg-currencies-api?color=blue&label=PyPI&logo=python&logoColor=white
.. |codecov| image:: https://codecov.io/github/zelnkup/nbg-currencies-api/graph/badge.svg?token=M4R1VT9PFU
   :target: https://codecov.io/github/zelnkup/nbg-currencies-api
