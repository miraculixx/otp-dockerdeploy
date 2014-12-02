otp-dockerdeploy
================

OTP Docker deployment

This project has a Dockerfile to deploy an opentripplanner instance, with the GTFS for Switzerland built in. There is also a unittest script to run the instance and check if everything is working.

Running the container
---------------------

First pull the Docker container from the repo (the repo might change):

`docker pull pablokbs/opentripplanner` 

Now you can run it (note the **-s** switch, to run the server):

`docker run -p 80:8080 -i -t pablokbs/opentripplanner:latest /bin/bash -s -v`

That will run a simple ubuntu instance, will download the dependencies and run the server, it might take a few minutes to start. After starting, you can browse the ip of the server, that will be redirected to the 8080 port on the container.

Unit testing
------------

We've implemented a script that has the ability to both run and test if the container is working as expected. In order to run it, we will need some dependencies on the server:

`apt-get install python-pip && pip -q install docker-py`

That's it! That's all we need to run the test. Remember that Docker version > 1.3 is required.

To run the test:

`./unittest.py pablokbs/opentripplanner:latest`

This is an example output:

```
2014-12-02 10:54:52,157 - unittest.py - INFO - Creating container.
2014-12-02 10:54:52,301 - unittest.py - INFO - Starting container.
2014-12-02 10:54:52,444 - unittest.py - INFO - Sleeping for 5 seconds to allow the container to start up
2014-12-02 11:01:17,805 - unittest.py - INFO - Begin test.
2014-12-02 11:01:17,930 - urllib3.connectionpool - INFO - Starting new HTTP connection (1): 172.17.0.2
2014-12-02 11:01:30,375 - unittest.py - INFO - Asserting origin data (47.37731,8.51612).
2014-12-02 11:01:30,377 - unittest.py - INFO - Origin data is OK.
2014-12-02 11:01:30,378 - unittest.py - INFO - Asserting destination data (47.35371, 8.55835).
2014-12-02 11:01:30,379 - unittest.py - INFO - Destination data is OK.
2014-12-02 11:01:30,379 - unittest.py - INFO - All assertions passed!
2014-12-02 11:01:30,380 - unittest.py - INFO - Everything looks OK. Exiting
```

As you can see, it creates the container, starts it, and tests a little search.
