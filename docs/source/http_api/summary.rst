*******
Summary
*******

Response
********

All responses conform to the `HAL specification <http://stateless.co/hal_specification.html>`_.

Formats
=======

JSON, XML

The API is able to return either XML or JSON, depending on the ‘Accept’ header in the request. By default a web browser will specify XML in the request. Note curl doesn’t specify any preference, so the API will respond with json.

To ensure you get xml back, add an Accept header to your request::

   curl https://new.talks.ox.ac.uk/api/series/041a5cc6-d65a-4dec-967d-3adc5162cea3 -H "Accept: application/xml"
   
Fields
======

Most fields should be self-explanatory but special note should be taken of date and time fields.

start : date / time string (ISO8601)
     * Start date and time for the talk `in Coordinated Universal Time (UTC) <https://www.w3.org/TR/NOTE-datetime>`_
     * Example: :code:`2016-04-08T10:00:00Z`
     * The Z time zone designator indicates UTC and the time should be converted to the local time zone of the talk before displaying
     * At present the location of all talks is assumed to be the UK and the local time zone is therefore GMT/BST
     
end : date / time string (ISO8601)
     * End date and time for the talk `in Coordinated Universal Time (UTC) <https://www.w3.org/TR/NOTE-datetime>`_
     * Example: :code:`2016-04-08T11:00:00Z`
     * The Z time zone designator indicates UTC and the time should be converted to the local time zone of the talk before displaying
     * At present the location of all talks is assumed to be the UK and the local time zone is therefore GMT/BST     
     
formatted_date : string (:code:`'d M yyyy mm:ss'`)
      * Start date and time for the talk formatted for display
      * Example: :code:`8 April 2016, 11:00`
      * The time has been converted to the local time zone (GMT/BST)
      
formatted_time : string (:code:`'mm:ss'`)
      * Start time for the talk formatted for display
      * Example: :code:`11:00` 
      * The time has been converted to the local time zone (GMT/BST)
       


For a more detailed example of the API in use, see the :ref:`JavaScript widget documentation <widget:widget-index>`.


