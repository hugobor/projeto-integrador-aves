from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from wtforms import Form, StringField, validators, HiddenField, SelectField, IntegerField, FileField, MultipleFileField

import copy


from avesapp.db import get_db, query_db, dict_from_row, dict_from_query

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
def ave_detalhe( ave_id ):

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




class AveForm( Form ):
    """Formulário de ave."""
    
    ave_id = HiddenField()
    nome_cientifico = StringField( 'Nome Científico', [ validators.DataRequired() ] )
    autor = StringField( 'Autor do Nome' )
    nome_popular = StringField( 'Nome em Popular' )    
    nome_ingles = StringField( 'Nome em Inglês' )

    ordem_id = HiddenField()
    ordem = SelectField( 'Ordem' )
    familia_id = HiddenField()
    familia = SelectField( 'Família' )

    foto_capa = FileField( 'Foto de Capa' )

    midia_extra = MultipleFileField( 'Mídia Extra' )

    conserv_int = SelectField( 'Internacional' )
    conserv_loc = SelectField( 'Em São Paulo' )

    frequencia_ocorrencia = IntegerField( 'Frequência de Ocorrência' )
    abundancia_relativa = StringField( 'Abundancia Relativa' )
    



    
@avesbp.route( '/nova', methods=( 'GET', 'POST' ))
def ave_novo():
    form = AveForm( request.form )        
    
    estados_iucn = query_db( 'select cod, nome_pt, nome_en from estado_iucn order by rowid;' )
    estados = [ ('', "—") ] + [ ( estado[ 'cod' ], f"{estado[ 'cod' ]} — {estado[ 'nome_pt' ]} — {estado[ 'nome_en' ]}" ) for estado in estados_iucn ]
    form.conserv_int.choices = estados
    form.conserv_loc.choices = estados

    if request.method == 'POST':
        ave_t = query_db( 'select * from ave where especie=?;', ( form.nome_cientifico.data, ), fetchone=True)
        if not ave_t is None:
            flash( f"Ave \"{form.nome_cientifico.data}\" já cadastrada.", "error" )
            return redirect( url_for( 'aves.ave_novo' ))

        a = {
            'familia_id': form.familia.data,
            'especie': form.nome_cientifico.data,
            'autor': form.autor.data,
            'nome_popular': form.nome_popular.data,
            'nome_ingles': form.nome_ingles.data,
            'estado_iucn': form.conserv_int.data,
            'estado_iucn_sp': form.conserv_loc.data,
            'frequencia_ocorrencia': form.frequencia_ocorrencia.data,
            'abundancia_relativa': form.abundancia_relativa.data,            
            'thumbnail': '',
            'descricao': '',
        }

        query_db( "insert into ave ( familia_id, especie, autor, nome_popular, nome_ingles, estado_iucn, estado_iucn_sp, frequencia_ocorrencia, abundancia_relativa ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ? );", (a['familia_id'], a['especie'], a['autor'], a['nome_popular'], a['nome_ingles'], a['estado_iucn'], a['estado_iucn_sp'], a['frequencia_ocorrencia'], a['abundancia_relativa'] ))
        get_db().commit()

        flash( f"Ave \"{a['especie']}\" cadastrada com sucesso.", 'success' )
                  

        return redirect( url_for( 'aves.aves_index' ))
            
    
    return render_template( 'ave_novo2.html', form=form )




@avesbp.route( '/edit/<int:ave_id>', methods=( 'GET', 'POST' ))
def ave_edit( ave_id ):
    ave_row = query_db( 'select * from ave where id=?;', ( ave_id, ), fetchone=True )

    if ave_row is None:
        return abort( 404, f"Ave id {ave_id} não cadastrada." )

    
    form = AveForm( request.form )
    estados_iucn = query_db( 'select cod, nome_pt, nome_en from estado_iucn order by rowid;' )
    estados = [ ('', "—") ] + [ ( estado[ 'cod' ], f"{estado[ 'cod' ]} — {estado[ 'nome_pt' ]} — {estado[ 'nome_en' ]}" ) for estado in estados_iucn ]
    form.conserv_int.choices = estados
    form.conserv_loc.choices = estados
    

    ave_class = query_db( 'select * from ave_classificacao where ave_id=?;', ( ave_id, ), fetchone=True )

    descrs = query_db( 'select * from ave_descr where ave_id=?;', ( ave_id, ), fetchone=True )

    familia = query_db( 'select * from familia where id=?;', ( ave_row[ 'familia_id'], ), fetchone=True )    
    ordem = query_db( 'select * from ordem where id=?;', ( familia[ 'ordem_id' ], ), fetchone=True )

    conserv_int = query_db( 'select * from estado_iucn where cod=?;', ( ave_row[ 'estado_iucn' ], ), fetchone=True )
    conserv_loc = query_db( 'select * from estado_iucn where cod=?;', ( ave_row[ 'estado_iucn_sp' ], ), fetchone=True )    

    form.ave_id.data = ave_row[ 'id' ]
    form.nome_cientifico.data = ave_row[ 'especie' ]


    if request.method == 'GET':
        if ave_row[ 'autor' ]:
            form.autor.data = ave_row[ 'autor' ]
        if ave_row[ 'nome_popular' ]:        
            form.nome_popular.data = ave_row[ 'nome_popular' ]
        if ave_row[ 'nome_ingles' ]:            
            form.nome_ingles.data = ave_row[ 'nome_ingles' ]

        ordens = query_db( 'select * from ordem;' )
        form.ordem.choices = [ (ordem[ 'id' ], ordem[ 'nome' ]) for ordem in ordens ]
        
        if not ordem is None:
            print( ordem[ 'id' ] )

        if not familia is None:
            if not ordem is None:
                familias = query_db( 'select * from familia where ordem_id=?;', ( ordem[ 'id' ], ))
                form.familia.choices = [ (f[ 'id' ], f[ 'nome' ]) for f in familias ]
                form.familia.data = familia[ 'id' ]
                form.ordem.data = familia[ 'ordem_id' ]

        if not conserv_int is None:
            form.conserv_int.data = conserv_int[ 'cod' ]
        if not conserv_loc is None:        
            form.conserv_loc.data = conserv_loc[ 'cod' ]


        if ave_row[ 'frequencia_ocorrencia' ]:
            form.frequencia_ocorrencia.data = ave_row[ 'frequencia_ocorrencia' ]

        if ave_row[ 'abundancia_relativa' ]:
            form.abundancia_relativa.data = ave_row[ 'abundancia_relativa' ]
        
    if request.method == 'POST':
        a = {
            'id': form.ave_id.data,
            'familia_id': form.familia.data,
            'especie': form.nome_cientifico.data,
            'autor': form.autor.data,
            'nome_popular': form.nome_popular.data,
            'nome_ingles': form.nome_ingles.data,
            'estado_iucn': form.conserv_int.data,
            'estado_iucn_sp': form.conserv_loc.data,
            'frequencia_ocorrencia': form.frequencia_ocorrencia.data,
            'abundancia_relativa': form.abundancia_relativa.data,            
            'thumbnail': '',
            'descricao': '',
        }

        ave_t = query_db( 'select * from ave where especie=?;', ( a['especie'], ), fetchone=True )

        if ave_t is None:
            flash( f"Ave \"{a['especie']}\" já existe", "error" )
        
        
        query_db( """
update ave
    set familia_id=?,
        especie=?,
        autor=?,
        nome_popular=?,
        nome_ingles=?,
        estado_iucn=?,
        estado_iucn_sp=?,
        frequencia_ocorrencia=?,
        abundancia_relativa=?
    where id=?;""",
                  ( a['familia_id'], a['especie'], a['autor'], a['nome_popular'], a['nome_ingles'], a['estado_iucn'], a['estado_iucn_sp'], a['frequencia_ocorrencia'], a['abundancia_relativa'], a['id'] ))
        
        get_db().commit()

        flash( f"Ave \"{a['especie']}\" alterada com sucesso.", "success" )        
        
        return redirect( url_for( 'aves.aves_index' ))


    return render_template( 'ave_novo2.html', form=form, edit_form=True )
    









@avesbp.route( '/remove/<int:ave_id>', methods=( 'GET', 'POST' ) )
def ave_remove( ave_id ):
    ave_row = query_db( 'select * from ave where id=?;', ( ave_id, ), fetchone=True )
    if ave_row is None:
        abort( 404, f"Ave id \"{ave_id}\" não cadastrada." )

    esp = ave_row['especie']
    query_db( "delete from ave where id=?;", ( ave_id, ))
    get_db().commit()


    flash( f"Ave \"{esp}\" removida.", "success" )
    return redirect( url_for( 'aves.aves_index' ))





@avesbp.route( '/api/familias' )
def ave_familias():
    if ( ordem := request.args.get( 'ordem' ) ):
        ordem_row  = query_db( 'select * from ordem where nome=?;', ( ordem, ), fetchone=True )
        if ordem_row is None:
            ordem_row = query_db( 'select * from ordem where id=?;', ( ordem, ), fetchone=True )
            if ordem_row is None:
                return abort( 404, f"Ordem {ordem} não cadastrada." )
        
        familias = query_db( 'select * from familia where ordem_id=? order by nome;', ( ordem_row[ 'id' ], ) )
    else:
        familias = query_db( 'select * from familia nome;' )

    return jsonify( dict_from_query( familias ))



@avesbp.route( '/api/ordens' )
def ave_ordens():
    ordens = query_db( 'select * from ordem order by nome;' )
    return jsonify( dict_from_query( ordens ) )





class OrdemFamiliaForm( Form ):
    ordem = StringField( 'Ordem' )
    ordem_id = HiddenField()
    familia = StringField( 'Familia' )
    familia_id = HiddenField()    

    

@avesbp.route( '/classifi', methods=( 'GET', 'POST' ))
def ave_classifi():
    form = OrdemFamiliaForm( request.form )

    if request.method == 'POST' and form.validate():
        return jsonify( dict( form ))

    return render_template( 'classifi.html', form=form )
