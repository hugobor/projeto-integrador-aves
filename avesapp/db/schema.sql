drop table if exists ave;
drop table if exists ordem;
drop table if exists familia;


--- Classificação Ciêntifica
drop table if exists ordem;
create table ordem (
       id integer primary key,
       nome text not null unique
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



drop table if exists estado_iucn;
create table estado_iucn (
       cod text not null primary key,
       nome_pt text not null,
       nome_en text not null,
       img text not null
);


--https://oeco.org.br/dicionario-ambiental/27904-entenda-a-classificacao-da-lista-vermelha-da-iucn/#comments
insert into estado_iucn values
( 'LC', 'Pouco Preocupante', 'Least Concern', '/static/iucn/LC.png' ),
( 'NT', 'Quase Ameaçada', 'Near Threatened', '/static/iucn/NT.png' ),
( 'VU', 'Vulnerável', 'Vulnerable', '/static/iucn/VU.png' ),
( 'EN', 'Em Perigo', 'Endangered', '/static/iucn/EN.png' ),
( 'CR', 'Criticamente em Perigo', 'Critically Endangered', '/static/iucn/CR.png' ),
( 'EW', 'Extinta na Natureza', 'Extinct in The Wild', '/static/iucn/EW.png' ),
( 'EX', 'Extinta', 'Extinct', '/static/iucn/EX.png' ),
( 'DD', 'Dados Insuficientes', 'Data Deficient', '/static/iucn/DD.png' ),
( 'NE', 'Não Avaliada', 'Not Evaluated', '/static/iucn/NE.png' );       


drop table if exists ave;
create table ave (
       id integer primary key,
       
       familia_id integer,
       
       especie text not null unique,
       autor text,

       nome_popular text,
       nome_ingles text,
       estado_iucn text,
       estado_iucn_sp text,

       estado_conservacao text,

       altura decimal,

       frequencia_ocorrencia integer,
       abundancia_relativa integer,

       thumbnail text,
       
       descricao text,

       foreign key( familia_id ) references familia( id )
       	       on delete cascade,
       foreign key( estado_iucn ) references estado_iucn( cod )
               on delete set null,
       foreign key( estado_iucn_sp ) references estado_iucn( cod )
               on delete set null	       
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
insert into ordem values ( 1, 'Anseriformes' );
insert into familia values ( 1, 1, 'Anatidae' );

--insert into ave( familia_id, especie, autor, nome_popular, nome_ingles ) values
--( 1, 'Dendrocygna bicolor', 'Vieillot, 1816', 'Marreca-caneleira', 'Fulvous Whistling-Duck' );
--saída
--sqlite> select * from ave_nome_cientifico;
--id|genero|nome_especie|nome_cientifico|nome_autor
--1|Dendrocygna|D. bicolor|Dendrocygna bicolor|(Vieillot, 1816)



drop view if exists ave_classificacao;
create view ave_classificacao as
       select ave.id                    as ave_id,
              ordem.nome     		as ordem,
  	      familia.nome   		as familia,
	      av_cien.genero 		as subfamilia,
	      av_cien.nome_especie	as especie,
	      ave.especie    		as nome_cientifico,
	      av_cien.nome_autor 	as autor,
	      ave.nome_popular 		as nome_popular,
	      ave.nome_ingles 		as nome_ingles
	      from ave
	      left join familia on ave.familia_id=familia.id
	      left join ordem on familia.ordem_id=ordem.id
	      left join ave_nome_cientifico av_cien on av_cien.id=ave.id;
	      


drop table if exists midia_tipo;
create table midia_tipo (
       id text primary key,
       midia text not null unique
);

insert into midia_tipo values
( 'I', 'Imagem' ),
( 'V', 'Video' ),
( 'A', 'Audio' );


drop table if exists ave_midia;
create table ave_midia (
       id integer primary key,
       ave_id integer,

       arquivo_caminho text not null,

       foreign key ( ave_id ) references ave( id )
              on delete cascade
);
drop index if exists idx_ave_midia_ave_id;
create index idx_ave_midia_ave_id on ave_midia( ave_id );


drop table if exists ave_descr;
create table ave_descr (
       id integer primary key,
       sequ integer default 0,
       
       ave_id integer not null,

       titulo text not null,
       conteudo text not null,

       foreign key ( ave_id )references ave( id )
       	       on delete cascade
);

     
