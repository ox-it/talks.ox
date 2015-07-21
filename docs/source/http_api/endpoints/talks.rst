*********************
Retrieve Talks via ID
*********************

Endpoint to retrieve information about talks

All the responses conform to the `HAL specification <http://stateless.co/hal_specification.html>`_.

.. http:get:: /talks/(string:id)

    Retrieve talk by ID

    **Example request**:

    .. sourcecode:: http

      GET /api/talks/fa67d13a-f17d-471d-b8cc-33b3d7759956
      Host: talks.ox.ac.uk
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "_links": {
                "self": {
                    "href": "/api/talks/fa67d13a-f17d-471d-b8cc-33b3d7759956"
                },
                "talks_page": {
                    "href": "/talks/id/fa67d13a-f17d-471d-b8cc-33b3d7759956/"
                }

            },
            "title": "What can babies with Down syndrome possibly tell us about Alzheimer's dementia in adults?",
            "start": "2015-01-29T18:00:00Z",
            "end": "2015-01-29T19:00:00Z",
            "formatted_date": "29 January 2015, 18:00",
            "formatted_time": "18:00",
            "description": "It may seem paradoxical to focus on babies ...",
            "_embedded":
            {
                "speakers": [ ],
                "venue": {
                    "_links": {
                        "self": {
                            "href": "//api.m.ox.ac.uk/places/oxpoints:50009121"
                        }
                    },
                    "name": "Mary Gray Allen Building",
                    "map_link": "//maps.ox.ac.uk/#/places/oxpoints:50009121"

                },
                "organising_department": null,
                "topics": [
                    {
                        "uri": "http://id.worldcat.org/fast/806532",
                        "label": "Alzheimer's disease"
                    }, {
                        "uri": "http://id.worldcat.org/fast/890050",
                        "label": "Dementia"
                    }
                ]
            }
        }

    :param id: The unique slug identifier for the talk
    :type id: string

    :statuscode 200: Talk found
    :statuscode 404: Talk not found
    :statuscode 503: Service not available


