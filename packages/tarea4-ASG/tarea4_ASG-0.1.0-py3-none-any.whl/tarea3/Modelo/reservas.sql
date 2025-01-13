BEGIN TRANSACTION;
DROP TABLE IF EXISTS "reservas";
CREATE TABLE IF NOT EXISTS "reservas" (
	"reserva_id"	INTEGER NOT NULL,
	"tipo_reserva_id"	INTEGER NOT NULL,
	"salon_id"	INTEGER NOT NULL,
	"tipo_cocina_id"	INTEGER NOT NULL,
	"persona"	varchar(255) NOT NULL,
	"telefono"	varchar(25) NOT NULL,
	"fecha"	date NOT NULL,
	"ocupacion"	INTEGER NOT NULL,
	"jornadas"	INTEGER NOT NULL,
	"habitaciones"	INTEGER NOT NULL DEFAULT '0',
	FOREIGN KEY("tipo_reserva_id") REFERENCES "tipos_reservas"("tipo_reserva_id"),
	FOREIGN KEY("tipo_cocina_id") REFERENCES "tipos_cocina"("tipo_cocina_id"),
	UNIQUE("salon_id","fecha"),
	PRIMARY KEY("reserva_id" AUTOINCREMENT),
	FOREIGN KEY("salon_id") REFERENCES "salones"("salon_id")
);
DROP TABLE IF EXISTS "tipos_reservas";
CREATE TABLE IF NOT EXISTS "tipos_reservas" (
	"tipo_reserva_id"	INTEGER NOT NULL,
	"nombre"	varchar(255) NOT NULL,
	"requiere_jornadas"	tinyint(1) NOT NULL DEFAULT '0',
	"requiere_habitaciones"	tinyint(1) NOT NULL DEFAULT '0',
	PRIMARY KEY("tipo_reserva_id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "tipos_cocina";
CREATE TABLE IF NOT EXISTS "tipos_cocina" (
	"tipo_cocina_id"	INTEGER NOT NULL,
	"nombre"	varchar(255) NOT NULL,
	PRIMARY KEY("tipo_cocina_id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "salones";
CREATE TABLE IF NOT EXISTS "salones" (
	"salon_id"	INTEGER NOT NULL UNIQUE,
	"nombre"	varchar(255) NOT NULL,
	PRIMARY KEY("salon_id" AUTOINCREMENT)
);
INSERT INTO "reservas" ("reserva_id","tipo_reserva_id","salon_id","tipo_cocina_id","persona","telefono","fecha","ocupacion","jornadas","habitaciones") VALUES (1,1,1,1,'David','600123456','20/12/2024',35,0,0),
 (2,2,2,2,'Juan','123456780','17/11/2024',2,0,0),
 (3,1,2,1,'Juan','123456789','16/11/2024',1,0,0),
 (4,2,2,1,'Perico','666778899','15/11/2024',3,0,0),
 (5,1,1,2,'David','111223344','20/11/2024',35,0,0),
 (6,1,1,1,'David','222334455','21/11/2024',3,0,0),
 (7,3,2,3,'Jacinto','333445566','21/12/2024',2,2,0),
 (8,1,1,1,'Jacinto','444556677','21/10/2024',1,0,0),
 (9,1,2,1,'Fernando','555667788','21/10/2024',1,0,0),
 (10,3,1,2,'Luis','645704341','1/12/2024',3,1,1),
 (11,2,1,2,'Azucena','345243654','1/10/2024',5,0,0),
 (12,2,1,2,'Azucena','345243654','2/10/2024',5,0,0);
INSERT INTO "tipos_reservas" ("tipo_reserva_id","nombre","requiere_jornadas","requiere_habitaciones") VALUES (1,'Banquete',0,0),
 (2,'Jornada',0,0),
 (3,'Congreso',1,1);
INSERT INTO "tipos_cocina" ("tipo_cocina_id","nombre") VALUES (1,'Bufé'),
 (2,'Carta'),
 (3,'Pedir cita con el chef'),
 (4,'No precisa');
INSERT INTO "salones" ("salon_id","nombre") VALUES (1,'Salón Habana'),
 (2,'Otro Salón');
DROP INDEX IF EXISTS "index_reservas";
CREATE UNIQUE INDEX IF NOT EXISTS "index_reservas" ON "reservas" (
	"fecha",
	"salon_id"
);
COMMIT;
