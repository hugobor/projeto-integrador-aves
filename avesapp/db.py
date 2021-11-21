import sqlite3

import os
import csv
import click
from flask import current_app, g
from flask.cli import with_appcontext


## https://flask.palletsprojects.com/en/2.0.x/patterns/sqlite3/

def get_db():
    '''Conexão com o banco de dados SQLite'''

    # cria conexão caso não exista
    if ( db := g.get( 'db' ) ) is None:
        g.db = sqlite3.connect(
            current_app.config[ 'DATABASE' ],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db( exc=None ):
    """Fecha conexão. Chamada com teardown_app_context."""
    if ( db := g.get( 'db' ) ) is not None:
        db.close()



def init_db():
    """Inicializa o banco de dados.
    Comando 'flask init-db'."""
    
    db = get_db()
    c = db.cursor()

    with current_app.open_resource( 'db/schema.sql', mode='r' ) as f_schema:
        c.executescript( f_schema.read() )
    
    read_avesPEFI( db )

    with current_app.open_resource( 'db/test_data.sql', mode='r' ) as f_schema:
        c.executescript( f_schema.read() )            

    print( f"{db.total_changes} modificações no banco de dados." )
    


def read_avesPEFI( db ):
    """Carrega arquivo csv avesPEFI.csv"""
    
    con = db
    c = db.cursor()

    db.commit()

    with current_app.open_resource( 'db/avesPEFI.csv', mode='r' ) as f_aves_pefi:
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
                       ( familia_id, nome_cientifico, autor, row[ 'Nomes populares' ].capitalize(), None, row[ 'Status' ], None, row[ 'FO' ], row[ 'AL' ] ));
            con.commit()

    

@click.command( 'init-db' )
@with_appcontext
def init_db_command():
    init_db()
    click.echo( 'Banco de dados inicializado' )


def init_app( app ):
    app.teardown_appcontext( close_db )
    app.cli.add_command( init_db_command )



#https://flask.palletsprojects.com/en/2.0.x/patterns/sqlite3/
def query_db( query, args=(), fetchone=False ):
    """Consulta no banco de dados."""
    
    cur = get_db().execute( query, args )

    r = cur.fetchone() if fetchone else cur.fetchall()
    
    cur.close()

    if r is None:
        return None

    return r
