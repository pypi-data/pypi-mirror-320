Livescraper Python Library
=========================

The library provides convenient access to the `Livescraper
API <https://livescraper.com/api-doc.html>`__ from applications written
in the Python language. Allows using `Livescraper’s
services <https://livescraper.com/services>`__ from your code.

`API Docs <https://livescraper.com/api-doc.html>`__

Installation
------------

Python 3+

.. code:: bash

   pip install livescraper

`Link to the python package
page <https://pypi.org/project/livescraper/>`__

Initialization
--------------

.. code:: python

   from livescraper import ApiClient

   scraper = livescraper(api_key)

`Link to the profile page to create the API
key <https://app.livescraper.com/user-profile>`__

Scrape Google Maps (Places)
---------------------------

.. code:: python

   # Search for businesses in specific locations:
   results = scraper.google_maps_search(
        queries=["Restaurants in Alakanuk, AK, United States"], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="True", 
        fields=["business_website","business_phone"]
    )

Scrape Google Maps Reviews
--------------------------

.. code:: python

   # Get reviews of the specific place
   results = scraper.google_review_search(
        queries=["real estate agents in Los Angeles, CA"], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="True", 
        fields=["query","business_name"]
    )


Scrape Emails And Contacts 
-------------------------

.. code:: python

   # Get emails and contacts 
   results = scraper.google_email_search(
        queries=["https://en.wikipedia.org/wiki/SA" ], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="False", 
        fields=["serial"]
    )
