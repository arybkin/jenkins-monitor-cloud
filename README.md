# Jenkins Monitor

[WIP] Current service is used for publishing all jenkins jobs information to DB.

## Technologies
Here were used next things:
* Python - as program language
* Flask - as web framework
* Postgres Sql
* Jenkins blue ocean api - for getting data from jenkins jobs

## Common user flow
Basically expected next flow:
* After job is completed on Jenkins, we call post action with Rest API like:
{"Jenkins":"Name_of_jenkins",
"pipeline_name":"Name_of_Job",
"run_id":"number_of_build"
}
* Service builds from configs connections to Jenkins and Postgres
* Service transfers data from Jenkins job to database

Synthetic methods:
* [GET] duration_pause_nodes - returns how many time nodes of jobs was waiting for free agents
* [GET] duration_pause_runs - returns how many time jobs was waiting for free agents
* [GET] / - returns just message



