Livescraper Python Library
==========================

The library provides convenient access to the `Livescraper API <https://livescraper.com/api-doc.html>`_ from applications written in the Python language. It allows using `Livescraper’s services <https://livescraper.com/services>`_ from your code.

API Docs
--------

Find the full documentation here:
`API Documentation <https://livescraper.com/api-doc.html>`_

Installation
------------

Python 3+ is required.

To install the package, use the following command:

.. code:: bash

   pip install livescraper

For more details, visit:
`Livescraper on PyPI <https://pypi.org/project/livescraper/>`_

Initialization
--------------

To initialize the scraper with your API key:

.. code:: python

   from livescraper import ApiClient

   scraper = livescraper(api_key)

Create your API key here:
`Create API Key <https://app.livescraper.com/user-profile>`_

Scrape Google Maps (Places)
===========================

To search for businesses in specific locations:

.. code:: python

   results = scraper.google_maps_search(
        queries=["Restaurants in Alakanuk, AK, United States"], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="True", 
        fields=["business_website", "business_phone"]
   )

Scrape Google Maps Reviews
==========================

To get reviews of a specific place:

.. code:: python

   results = scraper.google_review_search(
        queries=["real estate agents in Los Angeles, CA"], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="True", 
        fields=["query", "business_name"]
   )

Scrape Emails and Contacts
==========================

To get emails and contacts from a URL:

.. code:: python

   results = scraper.google_email_search(
        queries=["https://en.wikipedia.org/wiki/SA"], 
        language="en", 
        region="DE", 
        dropduplicates="True", 
        enrichment="False", 
        fields=["serial"]
   )