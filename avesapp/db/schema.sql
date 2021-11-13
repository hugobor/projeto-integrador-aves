drop table if exists ave;
drop table if exists ordem;
drop table if exists familia;


create table ordem (
       id integer primary key,
       nome text not null unique
);
create index idx_ordem_nome on ordem( nome );


create table familia (
       id integer primary key,
       ordem_id integer,
       nome text not null unique,
       
       foreign key( ordem_id ) references ordem( id )
       	       on delete cascade
);
create index idx_familia_nome on ordem( nome );


create table ave (
       id integer primary key,
       
       familia_id integer,
       
       genero text not null,
       especie text not null unique,

       nome_popular text,
       estado_conservacao text,

       altura decimal,

       frequencia_ocorrencia integer,
       abundancia_relativa integer,

       foreign key( familia_id ) references familia( id )
       	       on delete cascade
);

