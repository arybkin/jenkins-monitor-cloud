create table if not exists nodes(
actions VARCHAR (255),
displayDescription VARCHAR (255),
displayName VARCHAR (255) not null,
durationInMillis bigint,
id varchar (255) not null,
input VARCHAR (255),
result VARCHAR (255),
startTime TIMESTAMP,
state VARCHAR (255),
type VARCHAR (255),
causeOfBlockage VARCHAR (255),
edges UUID unique,
firstParent VARCHAR (255),
restartable bool,


node_uuid UUID unique,
run_uuid UUID not null,

primary key (node_uuid),
foreign key (run_uuid)
	references runs (run_uuid)


)