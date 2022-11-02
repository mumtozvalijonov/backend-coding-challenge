# Getting started
## Prerequisites
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* [Make](https://www.gnu.org/software/make/)

## Installation
1. Clone the repository
2. Run `make run` to start the application

## Usage
1. Make POST request to http://localhost:8000/api/v1/search with body:
```json
{
    "username": "<username>",
    "pattern": "<pattern>"
}
```
2. To stop the application run `make stop`

## Testing
1. Run `make test` to run tests
