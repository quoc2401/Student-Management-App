drop trigger if exists change_class_size;
DELIMITER $$
create trigger change_class_size
after update on student for each row
begin
	declare old_size int;
	declare new_size int;

	set old_size = (select count(s.id)
				from student s, class_room c
				where s.class_id = c.id and c.id = old.class_id
                group by old.class_id);
	set new_size = (select count(s.id)
				from student s, class_room c
				where s.class_id = c.id and c.id = new.class_id
                group by new.class_id);

	update class_room
	set total = new_size
	where id = new.class_id;

	update class_room
	set total = old_size
	where id = old.class_id;
end
$$