**********************
Retrieve List via ID
**********************

Endpoint to retrieve information about all talks collected together in a Public List

All the responses conform to the `HAL specification <http://stateless.co/hal_specification.html>`_.


.. http:get:: /collections/id/(string:id)

    Retrieve list by unique slug identifier, including all talks

    **Example request**:

    .. sourcecode:: http

	    GET api/collections/id/f6e6d9e6-d166-47d9-a894-35bc2f4a4580
	    Host: talks.ox.ac.uk
	    Accept: application/json

    **Example response**

    .. sourcecode:: http

		    HTTP/1.1 200 OK
		    Content-Type: application/json

		    {
		        "_embedded": {
		            "talks": [
		                {
		                    "_links": {
		                        "self": {
		                            "href": "/api/talks/52360e07-9b8b-477d-8bc7-8a25995e5ef8"
		                        },
		                        "talks_page": {
		                            "href": "/talks/id/52360e07-9b8b-477d-8bc7-8a25995e5ef8/"
		                        }
		                    },
		                    "description": "",
		                    "end": "2015-10-06T10:45:00Z",
		                    "formatted_date": "6 October 2015, 11:00",
		                    "formatted_time": "11:00",
		                    "location_details": "Seminar room",
		                    "location_summary": "Weatherall Institute of Molecular Medicine (WIMM), Seminar room, Headington OX3 9DS",
		                    "organiser_email": "liz.rose@imm.ox.ac.uk",
		                    "series": {
		                        "slug": "f204e37e-640e-4e1a-a3ef-dfb48c45630a",
		                        "title": "WIMM Occasional Seminars"
		                    },
		                    "slug": "52360e07-9b8b-477d-8bc7-8a25995e5ef8",
		                    "start": "2015-10-06T10:00:00Z",
		                    "title_display": "Ameliorating \u03b2-thalassaemia by manipulating expression of the \u03b1-globin gene"
		                }
		            ]
		        },
		        "_links": {
		            "talks_page": {
		                "href": "/user/lists/id/f6e6d9e6-d166-47d9-a894-35bc2f4a4580/"
		            }
		        },
		        "description": "Talks about Athena Swan",
		        "title": "Athena Swan Talks"
		    }

    :param id: The unique slug identifier for the list
    :type id: string

    :statuscode 200: List found
    :statuscode 404: List not found
    :statuscode 503: Service not available
