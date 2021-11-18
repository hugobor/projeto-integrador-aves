"""
Cria o banco de dados em 'schema.sql' e carrega o conteúdo de avesPEFI.csv.
"""

import os


import csv
import sqlite3
import pprint


db_filename = 'aves_pi.db'
pp = pprint.PrettyPrinter( indent=4, width=80 )

def main():
    con = sqlite3.connect( db_filename )
    con.row_factory = sqlite3.Row
    
    c = con.cursor()

    with open( 'schema.sql', encoding='utf8' ) as f_schema:
        c.executescript( f_schema.read() )

    con.commit()

    with open( 'avesPEFI.csv', encoding='utf8' ) as f_aves_pefi:
        csv_reader = csv.DictReader( f_aves_pefi, delimiter=';', quotechar='"' )
        for row in csv_reader:
            #pp.pprint( row )

            # Separa nome ciêntifico
            nc_row = row[ 'Nomes científicos' ]
            nome_cientifico = nc_row.strip()
            autor = ''
            nome_comp = nome_cientifico
            if ( autor_pos := nc_row.find( '(' ) ) >= 0:
                nome_cientifico = nc_row[ 0 : autor_pos ].strip()
                autor = nc_row[ autor_pos : ].replace( '(', '' ).replace( ')', '' )
                nome_comp = f"{nome_cientifico} ({autor})"

            #print( 'Nome cinetífico:', nome_cientifico, end='; ' )
            #print( 'Autor:', autor, end='; ' )
            #print( 'Nome comp:', nome_comp, end='; ' )
            #print( )

            #insere tudo em Aves
            aves_classe_id = c.execute( "SELECT id FROM classe WHERE nome='Aves' LIMIT 1;" ).fetchone()[ 'id' ]

            # Seleciona ordem, insere se não existir
            ordem_nome = row[ 'Ordem' ].strip().capitalize()
            ordem_row = c.execute( "SELECT id FROM ordem WHERE nome=? LIMIT 1;", ( ordem_nome, )).fetchone()
            if ordem_row is None:
                c.execute( "INSERT INTO ordem ( classe_id, nome ) VALUES ( ?, ? );",
                           ( aves_classe_id, ordem_nome ))
                con.commit()
                ordem_row = c.execute( "SELECT id FROM ordem WHERE nome=? LIMIT 1;", ( ordem_nome, )).fetchone()
            ordem_id = ordem_row[ 'id' ]

            # Seleciona família, insere se não existir                
            familia_nome = row[ 'Família' ].strip().capitalize()
            familia_row = c.execute( "SELECT id FROM familia WHERE nome=? LIMIT 1;", ( familia_nome, )).fetchone()
            if familia_row is None:
                c.execute( "INSERT INTO familia ( ordem_id, nome ) VALUES ( ?, ? );",
                           ( ordem_id, familia_nome ))
                con.commit()
                familia_row = c.execute( "SELECT id FROM familia WHERE nome=? LIMIT 1;", ( familia_nome, )).fetchone()
            familia_id = familia_row[ 'id' ]

            #print( f"familia_nome:{familia_nome}; familia_id:{familia_id}" )
            

            c.execute( "INSERT INTO ave ( familia_id, especie, autor, nome_popular, nome_ingles, estado_conservacao, altura, frequencia_ocorrencia, abundancia_relativa )"
                       "    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? );",
                       ( familia_id, nome_cientifico, autor, row[ 'Nomes populares' ], None, row[ 'Status' ], None, row[ 'FO' ], row[ 'AL' ] ));
            con.commit()


        print( f"{con.total_changes} modificações no banco de dados." )

                

    







    
if __name__ == '__main__':
    main()
