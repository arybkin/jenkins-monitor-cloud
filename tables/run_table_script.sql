create table if not exists runs(
actions VARCHAR (255),
artifactsZipFile VARCHAR (255),
causes UUID unique,
description VARCHAR (255),
durationInMillis bigint,
endTime TIMESTAMP,
enQueueTime TIMESTAMP,
estimatedDurationInMillis bigint,
id int not null,
name VARCHAR (255),
organization VARCHAR (255),
pipeline VARCHAR (255) not null,
replayable bool,
result VARCHAR (255),
runSummary VARCHAR (255),
startTime TIMESTAMP,
state VARCHAR (255),
type VARCHAR (255),
changeSet UUID unique,
branch VARCHAR (255),
commitId VARCHAR (255),
commitUrl VARCHAR (255),
pullRequest bool,

run_uuid UUID unique,
job_name VARCHAR (255) not null,

 primary key (run_uuid)

)