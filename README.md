Nysa Scheduler
----------

This project listen commands from the nysa-api-server and its sole purpose is to deploy configuration changes to AWS ECS using the desired state in a SQS message


Installation
------------

The project is available as a docker image simply run::

    $ docker run -e PROFILE=prod -e AWS_DEFAULT_REGION=us-east-1 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-scheduler


Configuration
-------------
nysa-scheduler its integrated with AWS Secret Manager for managing the secrets used during the application life cycle.
The only configuration that nysa expects as a environment variable is the PROFILE variable that indicates the desired configuration that will get from AWS Secret Manager

- ROLLBAR_KEY: A rollbar project key for sending application errors occurred
- NYSA_SCHEDULER_SQS_QUEUE: The SQS queue name for receiving deployment jobs from the api-server

Deploy new changes
------------

If you want to make some changes and then distribute the application you can build a docker image

    $ docker build -t 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-scheduler .

and then in the destination server you just need to pull this new image created

    $ docker pull 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-scheduler
