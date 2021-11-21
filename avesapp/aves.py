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
    
    
    return render_template( 'ave_detalhe.html', ave_class=ave_class, ave=ave, build_media_path=build_media_path )
