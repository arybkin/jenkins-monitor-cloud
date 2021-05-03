create table if not exists steps(
actions VARCHAR (255),
displayDescription text,
displayName VARCHAR (255),
durationInMillis bigint,
id int not null,
input VARCHAR (255),
result VARCHAR (255),
startTime TIMESTAMP,
state VARCHAR (255),
type VARCHAR (255),
log text,


node_uuid UUID not null,

foreign key (node_uuid)
	references nodes (node_uuid)


)