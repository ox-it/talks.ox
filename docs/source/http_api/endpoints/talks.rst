**************
Retrieve event
**************

Endpoint to retrieve a specific event by id

All the responses conform to the `HAL specification <http://stateless.co/hal_specification.html>`_.

.. http:get:: /events/(string:id)

    Retrieve event by ID

    **Example request**:

    .. sourcecode:: http

      GET /api/events/example-event-id
      Host: talks.ox.ac.uk
      Accept: application/json

    **Example response**:

    .. sourcecode:: xml

      <root>
        <slug>complete-regeneration-of-skin</slug>
        <url>/talks/id/complete-regeneration-of-skin/</url>
        <title>Complete Regeneration of Skin</title>
        <start>2015-01-30T23:00:00Z</start>
        <end>2015-01-31T00:00:00Z</end>
        <description>Skin</description>
        <formatted_date>30 January 2015, 23:00</formatted_date>
        <formatted_time>23:00</formatted_time>
        <speakers>
          <list-item>
          <id>2</id>
          <name>Professor Kazuo Kishi</name>
          <bio>
            Professor of Department of Reconstructive & Plastic Surgery, Keio University, Tokyo
          </bio>
          <title>
          Professor Kazuo Kishi, Professor of Department of Reconstructive & Plastic Surgery, Keio University, Tokyo
          </title>
          </list-item>
        </speakers>
        <organisers/>
        <hosts/>
        <happening_today>False</happening_today>
        <audience>oxonly</audience>

    :param id: The unique slug identifier for the talk
    :type id: string

    :statuscode 200: Talk found
    :statuscode 404: Talk not found
    :statuscode 503: Service not available
