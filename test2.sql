CREATE TABLE perf_test(
	id int,
	reason text COLLATE "C",
	annotation text COLLATE "C"
);

INSERT INTO perf_test(id, reason, annotation)
SELECT s.id, md5(random()::text), null
FROM generate_series(1, 10000000) AS s(id)
ORDER BY random();

UPDATE perf_test
SET annotation = UPPER(md5(random()::text))