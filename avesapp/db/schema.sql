drop table if exists ave;
drop table if exists ordem;
drop table if exists familia;


--- Classificação Ciêntifica
drop table if exists reino;
create table reino (
       id integer primary key,
       nome text not null unique
);
drop index if exists idx_reino_nome;
create index idx_reino_nome on reino( nome );


drop table if exists filo;
create table filo (
       id integer primary key,
       reino_id integer,
       nome text not null unique,
       
       foreign key( reino_id ) references reino( id )
       	       on delete cascade
);
drop index if exists idx_filo_nome;
create index idx_filo_nome on filo( nome );


drop table if exists classe;
create table classe (
       id integer primary key,
       filo_id integer,
       nome text not null unique,
       
       foreign key( filo_id ) references filo( id )
       	       on delete cascade
);
drop index if exists idx_classe_nome;
create index idx_classe_nome on classe( nome );


drop table if exists ordem;
create table ordem (
       id integer primary key,
       classe_id integer,
       nome text not null unique,

       foreign key( classe_id ) references classe( id )
       	       on delete cascade
);
drop index if exists idx_ordem_nome;
create index idx_ordem_nome on ordem( nome );


drop table if exists familia;
create table familia (
       id integer primary key,
       ordem_id integer,
       nome text not null unique,
       
       foreign key( ordem_id ) references ordem( id )
       	       on delete cascade
);
drop index if exists idx_familia_nome;
create index idx_familia_nome on ordem( nome );


drop table if exists ave;
create table ave (
       id integer primary key,
       
       familia_id integer,
       
       especie text not null unique,
       autor text,

       nome_popular text,
       nome_ingles text,
       estado_conservacao text,

       altura decimal,

       frequencia_ocorrencia integer,
       abundancia_relativa integer,

       foreign key( familia_id ) references familia( id )
       	       on delete cascade
);
drop index if exists idx_ave_especie;
drop index if exists idx_ave_nome_popular;
create index idx_ave_especie on ave( especie );
create index idx_ave_nome_popular on  ave( nome_popular );


-- !!!Gambiarra iminente!!!!
drop view if exists ave_nome_cientifico;
create view ave_nome_cientifico as
select ave.id as id,
       ( substr( trim( ave.especie ), 0, instr( trim( ave.especie ), ' ' ))) as genero, -- Primeira palavra do nome
       ( upper( substr( trim( ave.especie ), 1, 1 ) )
         || '.'
	 || ( substr( trim( ave.especie ), instr( trim( ave.especie ), ' '), length( trim( ave.especie ))))) as nome_especie, -- Primeira letra da primeira palavra + . + segunda palavra
       trim( ave.especie ) as nome_cientifico,
       '(' || autor || ')' as nome_autor
       from ave;




--Testinho do patinho
insert into reino values ( 1, 'Animalia' );
insert into filo values ( 1, 1, 'Chordata' );
insert into classe values ( 1, 1, 'Aves' );
insert into ordem values ( 1, 1, 'Anseriformes' );
insert into familia values ( 1, 1, 'Anatidae' );

insert into ave( familia_id, especie, autor, nome_popular, nome_ingles ) values
( 1, 'Dendrocygna bicolor', 'Vieillot, 1816', 'Marreca-caneleira', 'Fulvous Whistling-Duck' );
--saída
--sqlite> select * from ave_nome_cientifico;
--id|genero|nome_especie|nome_cientifico|nome_autor
--1|Dendrocygna|D. bicolor|Dendrocygna bicolor|(Vieillot, 1816)



drop view if exists ave_classificacao;
create view ave_classificacao as
       select reino.nome  		as reino,
       	      filo.nome     		as filo,
	      classe.nome    		as classe,
              ordem.nome     		as ordem,
  	      familia.nome   		as familia,
	      av_cien.genero 		as subfamilia,
	      av_cien.nome_especie	as especie,
	      ave.especie    		as nome_cientifico,
	      av_cien.nome_autor 	as autor,
	      ave.nome_popular 		as nome_popular,
	      ave.nome_ingles 		as nome_ingles
	      from ave
	      join familia on ave.familia_id=familia.id
	      join ordem on familia.ordem_id=ordem.id
	      join classe on ordem.classe_id=classe.id
	      join filo on classe.filo_id=filo.id
	      join reino on filo.reino_id=reino.id
	      join ave_nome_cientifico av_cien on av_cien.id=ave.id;
	      
