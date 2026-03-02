xanax
=====

**xanax** is a multi-source media API client for Python. Typed access to images,
photos, and video across multiple platforms — with both sync and async interfaces.

.. code-block:: python

   from xanax import Wallhaven
   from xanax.sources.wallhaven.params import SearchParams

   client = Wallhaven(api_key="your-api-key")
   for wallpaper in client.iter_media(SearchParams(query="nature")):
       client.download(wallpaper, path=f"{wallpaper.id}.jpg")

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/authentication
   guide/searching
   guide/pagination
   guide/async
   guide/downloading
   guide/collections
   guide/error-handling

.. toctree::
   :maxdepth: 2
   :caption: Sources

   sources/wallhaven
   sources/unsplash
   sources/reddit

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/clients
   api/search
   api/models
   api/enums
   api/errors
   api/sources

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog
