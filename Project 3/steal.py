begin atomic
declare changed_ smallint default 1;

while changed_ <> 0 do
    set changed_ = 0;

    for S as
        with
			recipient (day, realm, theme, login) as (
				select day, realm, theme, min(login) as login
				from Actor
				where (day, realm, theme, login) not in (
				    select day, realm, theme, login
				    from Loot
				)
				group by day, realm, theme
				order by day, realm, theme
			),

		    Haul (day, realm, theme, login, #prize, worth) as (
		        select L.day, L.realm, L.theme, L.login, count(*), sum(T.sql)
		        from Loot L, Treasure T
		        where L.treasure = T.treasure and login is not null
		        group by day, realm, theme, login
		        having count(*) > 1
		    ),

		    Donor (day, realm, theme, login, #prize, worth) as (
		        select day, realm, theme, login, #prize, worth
		        from Haul H
		        where not exists (
		            select *
		            from Haul J
		            where H.day = J.day and H.realm = J.realm and H.theme = J.theme
		                and ((J.#prize > H.#prize)
		                    or
		                    (J.#prize = H.#prize and J.worth > H.worth)
		                    or
		                    (J.#prize = H.#prize
		                        and J.worth = H.worth
		                        and J.login > H.login))
		        )
		    ),

		    Donation (day, realm, theme, login, loot#, treasure, sql) as (
		        select D.day, D.realm, D.theme, D.login, L.loot#, L.treasure, T.sql
		        from Donor D, Loot L, Treasure T
		        where D.day = L.day
		            and D.realm = L.realm
		            and D.theme = L.theme
		            and D.login = L.login
		            and L.treasure = T.treasure
		            and not exists (
		                select *
		                from Loot M, Treasure S
		                where M.day   = L.day
		                    and M.realm = L.realm
		                    and M.theme = L.theme
		                    and M.login = L.login
		                    and M.treasure = S.treasure
		                    and ((S.sql < T.sql)
		                        or
		                        (S.sql = T.sql and S.treasure > T.treasure)
		                        or
		                        (S.sql = T.sql
		                            and S.treasure = T.treasure
		                            and M.loot# > L.loot#))
		            )
		    )
		    
		select r.day, r.realm, r.theme, r.login as recipient, d.login as donor, d.loot#, d.treasure, d.sql
		from recipient as r, Donation as d
		where r.day = d.day and r.realm = d.realm and r.theme = d.theme
		order by r.realm, r.theme

    do
		-- Here is where the changes are made with Loot and the realm, theme, login, loot and treasure are updated
        update Loot as l
        set l.login = S.recipient
        where l.day = S.day
        	and l.realm = S.realm
        	and l.theme = S.theme
        	and l.login = S.donor
        	and l.loot# = S.loot#
        	and l.treasure = S.treasure;

        set changed_ = 1;

    end for;

end while;

end!
