# Image Relocator

This project provides a back-end service for relocating on-line images to [Imgur](https://imgur.com/).

It communicates to Imgur via the official [API](https://apidocs.imgur.com/).
To get it work, [`config.ini`](./config.ini) has to be updated accordingly.

## Submit images for relocation

Submits a request to relocate a set of images to Imgur.
The images will be uploaded by the configured Imgur client, publicly visible.

### Request

    POST /v1/images/upload

The request is just a JSON body, no query parameters.

##### Request body

Attributes:

* urls: An array of URLs to images that are to be relocated. Duplicates are stripped out.

Example:

    {
    "urls": [
        "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
        "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg"
        ]
    }

### Response

On success, returns the job id.

##### Response body

Attributes:

* jobId: The id of the relocation job that was just submitted.

Example:

    {
    "jobId": "55355b7c-9b86-4a1a-b32e-6cdd6db07183",
    }

## Get relocation job status

Gets the status of a job.

### Request

    GET /v1/images/upload/:jobId

The request has no body and no query parameters. :jobId is an ID returned from the POST
API above.

##### Request body

None

### Response

The status of the job.

#### Response body

Attributes:

* id: The id of the relocation job.

* created: When job was created. In ISO8601 format (YYYY-MM-DDTHH:mm:ss.sssZ) for
GMT.

* finished: When job was completed. In the same format as created. `null` if status is not
`complete`.

* status: The status of the entire relocation job. Is one of:

    * `pending`: indicates job has not started processing.

    * `in-progress`: job has started processing.

    * `complete`: job is complete.

* uploaded: An object of arrays categorizing the set of submitted URLs by the status of the relocation, i.e. pending, complete and failed.

Example:

    {
    "id": "55355b7c-9b86-4a1a-b32e-6cdd6db07183",
    "created": "2017-12-22T16:48:29+00:00",
    "finished": null,
    "status": "in-progress",
    "uploaded": {
        "pending": [
            "https://www.factslides.com/imgs/black-cat.jpg",
            ],
        "complete": [
            "https://i.imgur.com/gAGub9k.jpg",
            "https://i.imgur.com/skSpO.jpg"
            ],
        "failed": [
            ]
        }
    }

## Get a list of all relocated images

Gets the links of all images uploaded to Imgur.

### Request

    GET /v1/images

The request has no body and no query parameters.

#### Request body

None

### Response

An array of the Imgur links to the successfully uploaded images.

#### Response body

Attributes:

* uploaded: An array of the Imgur links to the uploaded images.

Example:

    {
    "uploaded": [
        "https://i.imgur.com/gAGub9k.jpg",
        "https://i.imgur.com/skSpO.jpg"
        ]
    }
