from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from avesapp.db import get_db, query_db

from . import build_media_path


avesbp = Blueprint( 'aves', __name__, url_prefix='/aves' )


@avesbp.route( '/' )
def aves_index():
    db = get_db()
    aves = query_db(
        'SELECT * FROM ave_classificacao c'
        '    JOIN ave a ON c.ave_id=a.id'
        '    ORDER BY nome_cientifico ASC;' )

    return render_template( "aves_index.html", aves=aves )


@avesbp.route( '/detalhe/<int:ave_id>' )
def aves_detalhe( ave_id ):

    ave = query_db(
        'select * from ave where id=?', ( ave_id ,),
        fetchone=True )

    if ave is None:
        abort( 404, f"Ave id {ave_id} não cadastrada." )
        
    
    ave_class = query_db(
        'select * from ave_classificacao where ave_id=?;', ( ave[ 'id' ] ,),
        fetchone=True )

    ave_descrs = query_db(
        'select * from ave_descr where ave_id=? order by sequ;',
        ( ave[ 'id' ] ,) )

    estado_iucn = query_db(
        'select * from estado_iucn order by rowid;' )

    return render_template( 'ave_detalhe.html', ave_class=ave_class, ave=ave, build_media_path=build_media_path, ave_descrs=ave_descrs, estado_iucn=estado_iucn )





@avesbp.route( '/novo', methods=( 'GET', 'POST' ))
def ave_novo():
    
    if request.method == 'POST':

        form = request.form

        nome_cientifico = form.get( 'nome-cientifico' )

        if not query_db( 'select * from ave where especie=?', ( nome_cientifico ,)) is None:
            flash( f"Espécie {nome_cientifico} já cadastrada." )
        
        if nome_cientifico is None:
            flash( 'Nome Científico nescessário.' )

            
        familia_text = form.get( 'familia' )
        if familia_text == '':
            familia_id = None
        else:
            familia_row = query_db(
                'select * from familia where nome=? limit 1;', ( familia_text, ), fetchone=True )
            if familia_row is None:
                query_db( 'insert into familia ( nome ) values ( ? );', ( familia_text, ))
                familia_row = query_db(
                    'select * from familia where nome=? limit 1;', ( familia_text, ), fetchone=True )            
            familia_id = familia_row[ 'id' ]
            
        db = get_db()
        db.execute(
            'insert into ave ( familia_id, especie, autor, nome_popular, nome_ingles, estado_iucn, estado_iucn_sp, frequencia_ocorrencia, abundancia_relativa ) values'
            '    ( ?, ?, ?, ?, ?, ?, ?, ?, ? );',
            ( familia_id, form.get( 'nome-cientifico' ), form.get( 'autor' ), form.get( 'nome-popular' ), form.get( 'nome-ingles' ),
              form.get( 'estado-iunc' ), form.get( 'estado-iunc-sp' ),
              form.get( 'frequencia-ocorrencia' ), form.get( 'abundancia-relativa' )))
        db.commit()
        return redirect( url_for( 'aves.aves_index' ))

        

        

    familias = query_db( 'select * from familia;' )
    
    estado_iucn = query_db(
        'select * from estado_iucn order by rowid;' )    

    return render_template( 'ave_novo.html', familias=familias, estado_iucn=estado_iucn )
