*******
Summary
*******

Formats: JSON, XML

The API is able to return either XML or JSON, depending on the ‘Accept’ header in the request. By default a web browser will specify XML in the request. Note curl doesn’t specify any preference, so the API will respond with json.

To ensure you get xml back, add an Accept header to your request::

   curl https://new.talks.ox.ac.uk/api/series/041a5cc6-d65a-4dec-967d-3adc5162cea3 -H "Accept: application/xml"

For a more detailed example of the API in use, see the :ref:`JavaScript widget documentation <widget:widget-index>`.


