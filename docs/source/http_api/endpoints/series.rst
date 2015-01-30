***************
Retrieve Series
***************

.. http:get:: /series/

    Retrieve series by ID, including all talks

    **Example request**:

    .. sourcecode:: http

      GET /api/series/series-id
      Host: talks.ox.ac.uk
      Accept: application/json

    **Example response**

      .. sourcecode:: xml

        <root>
        <id>1</id>
          <title>A conference</title>
          <description>A conference featuring a diverse array of groups</description>
          <department_organiser/>
          <events>
            <list-item>
              <slug>
               deformation-and-melts-litosphere-astenosphere-boundary
              </slug>
              <url>
                /talks/id/deformation-and-melts-litosphere-astenosphere-boundary/
              </url>
              <title>
                Feedbacks between deformation and melts in the lithosphere-asthenosphere boundary
              </title>
              <start>2014-12-10T12:00:00Z</start>
              <end>2014-12-10T14:00:00Z</end>
              <description>Geo sciences</description>
              <formatted_date>10 December 2014, 12:00</formatted_date>
              <formatted_time>12:00</formatted_time>
              <speakers>
                <list-item>
                  <id>3</id>
                  <name>Dr Andrea Tommasi</name>
                  <bio>Geosciences Montpellier</bio>
                  <title>Dr Andrea Tommasi, Geosciences Montpellier</title>
                </list-item>
              </speakers>
            <organisers/>
            <hosts/>
            <happening_today>False</happening_today>
            <audience>oxonly</audience>
            <api_location>...</api_location>
            <api_organisation>...</api_organisation>
            <api_topics>...</api_topics>
            <class_name>Event</class_name>
            </list-item>
          </events>
        </root>

    :param id: The unique slug identifier for the series
    :type id: string

    :statuscode 200: Series found
    :statuscode 404: Series not found
    :statuscode 503: Service not available
