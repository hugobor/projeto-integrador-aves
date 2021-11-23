update ave set thumbnail='tauató-miúdo.jpg'
where lower( nome_popular ) = lower( 'tauató-miúdo' );

insert into ave_descr( ave_id, titulo, conteudo ) values
( (select id from ave where nome_popular='Tauató-miúdo' limit 1),
  'Descrição',
  'Gavião pequeno e com asas relativamente curtas e arredondadas. Os adultos possuem o dorso cinza e com barras laranjas no ventre. Os imaturos são em geral mais marrons e com a cabeça menor. Note as rápidas batidas de asas. Reproduz em florestas extensas. Se alimenta principalmente de aves capturadas em voo.' );
