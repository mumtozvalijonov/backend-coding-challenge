1. Q: Can we use a database? What for? SQL or NoSQL?
   A: We can use a database to store the data mostly as a cashing layer. This will help us to reduce the number of requests to the API. We can use a database like MongoDB or MySQL. However NoSQL databases are a better choice due to partition tolerance for big data storage.
2. Q: How can we protect the api from abusing it?
   A: We can use a rate limiter to limit the number of requests per time. We can also use a captcha to protect the api from bots.
3. How can we deploy the application in a cloud environment?
   We can use a docker and/or Kubernetes to deploy the application in a cloud environment.
4. Q: How can we be sure the application is alive and works as expected when deployed into a cloud environment?
   A: We can use a monitoring tool like Prometheus to monitor the application and alert us if something goes wrong.
5. Q: Any other topics you may find interesting and/or important to cover
   A: Ideally I would use an asynchronous framework like FastAPI or Starlette for this purpose as it is more scalable and faster than Flask.