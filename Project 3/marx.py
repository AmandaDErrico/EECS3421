CREATE TABLE Reassigned (
    donor varchar(20) not null,
    recipient varchar(20) not null,
    day       date        not null,
    realm     varchar(20) not null,
    theme     varchar(20) not null,
    loot#     smallint    not null, 
    treasure  varchar(20) not null,
    sql       integer     not null
);


CREATE TRIGGER Marx 
after update of login on Loot
REFERENCING 
	old row as old 
	new row as new
for each row
when (old.login <> new.login) 

		
INSERT INTO Reassigned (donor, recipient, day, realm, theme, loot#, treasure, sql) VALUES
	(old.login, new.login, old.day, old.realm, old.theme, old.loot#, old.treasure, 
(SELECT sql
	From Treasure T
	Where T.treasure = old.treasure)
)
;	
 
                    
