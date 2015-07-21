**********************
Retrieve Series via ID 
**********************

Endpoint to retrieve information about all talks in a series

All the responses conform to the `HAL specification <http://stateless.co/hal_specification.html>`_.


.. http:get:: /series/(string:id)

    Retrieve series by unique slug identifier, including all talks

    **Example request**:

    .. sourcecode:: http

      GET /api/series/d95be2ef-10bb-43d3-a46c-99dccf7151a0
      Host: talks.ox.ac.uk
      Accept: application/json

    **Example response**

      .. sourcecode:: http

        {
            "_links": {
                "self": {
                    "href": "/api/series/d95be2ef-10bb-43d3-a46c-99dccf7151a0"
                },
                "talks_page": {
                    "href": "/talks/series/id/d95be2ef-10bb-43d3-a46c-99dccf7151a0"
                }
            },
            "title": "ChemBio Hub Events",
            "description": "",
            "occurence": "",
            "_embedded": {
                "talks": [{
                    "_links": {
                        "self": {
                            "href": "/api/talks/88ba512b-8ac1-4191-a86e-340f8f3fed1d"
                        },
                        "talks_page": {
                            "href": "/talks/id/88ba512b-8ac1-4191-a86e-340f8f3fed1d/"
                        }
                    },
                    "title_display": "Current expertise and future directions in drug discovery: an Oxford-Industry conversation",
                    "slug": "88ba512b-8ac1-4191-a86e-340f8f3fed1d",
                    "start": "2015-07-31T09:00:00Z",
                    "end": "2015-07-31T19:00:00Z",
                    "formatted_date": "31 July 2015, 9:00",
                    "formatted_time": "09:00",
                    "description": "This event showcases top chemical biology research from labs at Oxford. ...",
                    "location_details": "",
                    "location_summary": null,
                    "series": {
                        "slug": "d95be2ef-10bb-43d3-a46c-99dccf7151a0",
                        "title": "ChemBio Hub Events"
                    },
                    "_embedded": {
                        "speakers": [],
                        "venue": null,
                        "organising_department": {
                            "address": "off South Parks Road OX1 3QU",
                            "_links": {
                                "self": {
                                    "href": "//api.m.ox.ac.uk/places/oxpoints:23232534"
                                }
                            },
                            "name": "Department of Biochemistry",
                            "map_link": "//maps.ox.ac.uk/#/places/oxpoints:23232534"
                        },
                        "topics": []
                    },
                    "organiser_email": ""
                }]
            }
        }

    :param id: The unique slug identifier for the series
    :type id: string

    :statuscode 200: Series found
    :statuscode 404: Series not found
    :statuscode 503: Service not available
