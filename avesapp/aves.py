from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, current_app
from werkzeug.exceptions import abort
from wtforms import Form, StringField, validators, HiddenField, SelectField, IntegerField, TextAreaField, MultipleFileField

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

import os




from werkzeug.utils import secure_filename


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

    estado = query_db(
        'select * from estado_iucn where cod=? limit 1;', ( ave['estado_iucn'], ), fetchone=True )
    estado_loc = query_db(
        'select * from estado_iucn where cod=? limit 1;', ( ave['estado_iucn_sp'], ), fetchone=True )    

    return render_template( 'ave_detalhe.html', ave_class=ave_class, ave=ave, build_media_path=build_media_path, ave_descrs=ave_descrs, estado=estado, estado_loc=estado_loc )




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

    thumbnail = FileField( 'Foto de Capa' )

    midia_extra = MultipleFileField( 'Mídia Extra' )

    conserv_int = SelectField( 'Internacional' )
    conserv_loc = SelectField( 'Em São Paulo' )

    frequencia_ocorrencia = IntegerField( 'Frequência de Ocorrência' )
    abundancia_relativa = StringField( 'Abundancia Relativa' )

    descricao = TextAreaField( 'Descrição' )


    



    
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

        f = request.files.get('thumbnail' )
        if f:
            fname = secure_filename( f.filename )
            f.save( os.path.join(
                current_app.root_path, 'static/media/', fname            
            ))
        else:
            fname = None
        
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
            'thumbnail': fname,
            'descricao': request.form.get( 'descricao' ),
        }



        query_db( "insert into ave ( familia_id, especie, autor, nome_popular, nome_ingles, estado_iucn, estado_iucn_sp, frequencia_ocorrencia, abundancia_relativa, descricao, thumbnail ) values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );", (a['familia_id'], a['especie'], a['autor'], a['nome_popular'], a['nome_ingles'], a['estado_iucn'], a['estado_iucn_sp'], a['frequencia_ocorrencia'], a['abundancia_relativa'], a['descricao'], a['thumbnail'] ))
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
    ordem = None
    if familia:
        ordem = query_db( 'select * from ordem where id=?;', ( familia[ 'ordem_id' ], ), fetchone=True )

    conserv_int = query_db( 'select * from estado_iucn where cod=?;', ( ave_row[ 'estado_iucn' ], ), fetchone=True )
    conserv_loc = query_db( 'select * from estado_iucn where cod=?;', ( ave_row[ 'estado_iucn_sp' ], ), fetchone=True )    


    if request.method == 'GET':
        form.ave_id.data = ave_row[ 'id' ]
        form.nome_cientifico.data = ave_row[ 'especie' ]

        if ave_row['descricao'] and ave_row['descricao'].strip() != '':
            form.descricao.data = ave_row['descricao']

        if ave_row[ 'autor' ] and ave_row['autor'].strip != '':
            form.autor.data = ave_row[ 'autor' ]
        if ave_row[ 'nome_popular' ] and ave_row['nome_popular'].strip() != '':        
            form.nome_popular.data = ave_row[ 'nome_popular' ]
        if ave_row[ 'nome_ingles' ] and ave_row['nome_ingles'].strip() != '':            
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

        thumb = ave_row['thumbnail']



    if request.method == 'POST':
        f = request.files.get('thumbnail' )
        if f and f != '':
            fname = secure_filename( f.filename )
            f.save( os.path.join(
                current_app.root_path, 'static/media/', fname            
            ))
        else:
            fname = ave_row['thumbnail']
            
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
            'thumbnail': fname,
            'descricao': request.form.get( 'descricao' )
        }

        ave_t = query_db( 'select * from ave where especie=?;', ( a['especie'], ), fetchone=True )

        if (not (ave_t is None)) and (int( ave_t['id'] ) != int( a['id'])):
            flash( f"Ave \"{a['especie']}\" já existe.", "error" )
            return redirect( url_for( 'aves.aves_index' ))
        
        
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
        abundancia_relativa=?,
        descricao=?,
        thumbnail=?
    where id=?;""",
                  ( a['familia_id'], a['especie'], a['autor'], a['nome_popular'], a['nome_ingles'], a['estado_iucn'], a['estado_iucn_sp'], a['frequencia_ocorrencia'], a['abundancia_relativa'],  a['descricao'], a['thumbnail'], a['id'] ))
        
        get_db().commit()

        flash( f"Ave \"{a['especie']}\" alterada com sucesso.", "success" )        
        
        return redirect( url_for( 'aves.aves_index' ))

    

    if thumb:
        thumb = os.path.join( '/static/media/', thumb )
    return render_template( 'ave_novo2.html', form=form, edit_form=True, thumb=thumb )
    









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

        familias = query_db( 'select * from familia where ordem_id=? order by nome;', ( ordem_row[ 'id'], ) )

    if (ext_familia := request.args.get( 'ext-familia' )):
        fam_id = query_db( "select * from familia where id=? limit 1;", ( ext_familia, ), fetchone=True )
        fam_nome = query_db( "select * from familia where nome=? limit 1;", ( ext_familia, ), fetchone=True )
        return jsonify(( not (fam_id is None) ) or ( not (fam_nome is None) ))            

    else:
        familias = query_db( 'select * from familia nome;' )

        return jsonify( dict_from_query( familias ))






@avesbp.route( '/api/ordens' )
def ave_ordens():
    if (ext_ordem := request.args.get( 'ext-ordem' )):
        ord_id = query_db( "select * from ordem where id=? limit 1;", ( ext_ordem, ), fetchone=True )
        ord_nome = query_db( "select * from ordem where nome=? limit 1;", ( ext_ordem, ), fetchone=True )
        return jsonify(( not (ord_id is None) ) or ( not (ord_nome is None) ))
    
    ordens = query_db( 'select * from ordem order by nome;' )
    return jsonify( dict_from_query( ordens ) )


@avesbp.route( '/api/is-parent' )
def aves_is_parent():
    familia_id = request.args.get( 'familia-id' )
    ordem_id = request.args.get( 'ordem-id' )

    familia_nome = request.args.get( 'familia' )
    ordem = request.args.get( 'ordem' )

    if not ( familia_id is None ):
        familia_row = query_db( "select * from familia where id=?;", ( familia_id, ), fetchone=True )
    else:
        familia_row = query_db( "select * from familia where nome=?;", ( familia, ), fetchone=True )

    if not ( ordem_id is None ):
        ordem_row = query_db( "select * from ordem where id=?;", ( ordem_id, ), fetchone=True )
    else:
        ordem_row = query_db( "select * from ordem where nome=?;", ( ordem, ), fetchone=True )

    if ( not ( familia_row is None ) ) and ( ordem_row is None ):
        return jsonify( False )

    if not familia_row or not ordem_row:
        return jsonify( False )

    if familia_row[ 'ordem_id' ] == ordem[ 'id' ]:
        return jsonify( True )
        




class OrdemFamiliaForm( FlaskForm ):
    ordem = StringField( 'Ordem' )
    familia = StringField( 'Familia' )

    

@avesbp.route( '/classifi', methods=( 'GET', 'POST' ))
def ave_classifi():
    form = OrdemFamiliaForm( request.form )

    if request.method == 'POST' and form.validate():
        return jsonify( dict( form ))

    ordens = query_db( "select * from ordem order by nome asc" )
    familias = query_db( "select * from familia order by nome asc" )

    return render_template( 'classifi.html', form=form, ordens=ordens, familias=familias )



def get_ordem_id( id ):
    return query_db( 'select * from ordem where id=?', ( id, ), fetchone=True )

def get_ordem_id( id ):
    return query_db( 'select * from familia where id=?', ( id, ), fetchone=True )    

def get_ordem( nome ):
    return query_db( 'select * from ordem where nome=?', ( nome, ), fetchone=True )

def get_familia( nome ):
    return query_db( 'select * from familia where nome=?', ( nome, ), fetchone=True )    



@avesbp.route( '/ordem_nova', methods=( 'POST', ))
def ordem_nova():
    ordemf = request.form.get( 'ordem' )
    if ordemf is None or ordemf == '':
        return abort( 404, f"Sem ordem especificada" )

    query_db( 'insert into ordem (nome) values ( ? );', ( ordemf, ) )
    get_db().commit()

    flash( f"Ordem \"{ordemf}\" inserida com sucesso.", 'success' )
    
    return redirect( url_for( 'aves.ave_classifi' ))




@avesbp.route( '/ordem_remove', methods=( 'POST', ))
def ordem_remove():
    ordemf = request.form.get( 'ordem' )
    if ordemf is None or ordemf == '':
        return abort( 404, f"Sem ordem especificada" )
    if (ordem := get_ordem( ordemf )) is None:
        return abort( 404, f"Ordem {ordemf} não cadastrada" )

    query_db( 'delete from ordem where id=?;', ( ordem[ 'id' ], ) )
    get_db().commit()

    flash( f"Ordem \"{ordemf}\" removida com sucesso.", 'success' )
    
    return redirect( url_for( 'aves.ave_classifi' ))



@avesbp.route( '/familia_nova', methods=( 'POST', ))
def familia_nova():
    familiaf = request.form.get( 'familia' )
    if familiaf is None or familiaf == '':
        return abort( 404, f"Sem familia especificada" )

    ordem_id = None
    if (ordemf := request.form.get( 'familia' )):
        if (ordem := get_ordem( ordemf )):
            ordem_id = ordem[ 'id' ]
        


    query_db( 'insert into familia (nome, ordem_id) values ( ?, ? );', ( familiaf, ordem_id ) )
    get_db().commit()

    flash( f"Família \"{familiaf}\" inserida com sucesso.", 'success' )
    
    return redirect( url_for( 'aves.ave_classifi' ))    



@avesbp.route( '/familia_remove', methods=( 'POST', ))
def familia_remove():
    familiaf = request.form.get( 'familia' )
    if familiaf is None or familiaf == '':
        return abort( 404, f"Sem familia especificada" )
    if (familia := get_familia( familiaf )) is None:
        return abort( 404, f"Ordem {familiaf} não cadastrada" )

    query_db( 'delete from familia where id=?;', ( familia[ 'id' ], ) )
    get_db().commit()

    flash( f"familia \"{familiaf}\" removida com sucesso.", 'success' )
    
    return redirect( url_for( 'aves.ave_classifi' ))


@avesbp.route( '/muda_parente', methods=( 'POST', ))
def muda_parente():
    familiaf = request.form.get( 'familia' )
    if familiaf is None or familiaf == '':
        return abort( 404, f"Sem família especificada" ) 
    if (familia := get_familia( familiaf )) is None:
        return abort( 404, f"Ordem {familiaf} não cadastrada" )

    ordemf = request.form.get( 'ordem' )
    if ordemf is None or ordemf == '':
        return abort( 404, f"Sem ordem especificada" )
    if (ordem := get_ordem( ordemf )) is None:
        return abort( 404, f"Ordem {ordemf} não cadastrada" )

    query_db( "update familia set ordem_id=? where id=?;", ( ordem[ 'id' ], familia[ 'id' ] ))
    get_db().commit()

    flash( f"Família {familiaf} agora pertence à ordem {ordemf}.", "success" )

    return redirect( url_for( 'aves.ave_classifi' ))    

@avesbp.route( '/ambos', methods=( 'POST', ))
def ambos():
    familiaf = request.form.get( 'familia' )
    if familiaf is None or familiaf == '':
        return abort( 404, f"Sem família especificada" ) 
    if not ( (familia := get_familia( familiaf )) is None):
        return abort( 404, f"Ordem {familiaf} já cadastrada" )

    ordemf = request.form.get( 'ordem' )
    if ordemf is None or ordemf == '':
        return abort( 404, f"Sem ordem especificada" )
    if not ( (ordem := get_ordem( ordemf )) is None):
        return abort( 404, f"Ordem {ordemf} já cadastrada" )

    query_db( 'insert into ordem( nome ) values ( ? );', ( ordemf, ))
    get_db().commit()
    ordemnew = get_ordem( ordemf )

    query_db( 'insert into familia( nome, ordem_id ) values ( ?, ? );', ( familiaf, ordemnew[ 'id' ] ))
    get_db().commit()

    flash( f"Família \"{familiaf}\" e ordem \"{ordemf}\" inseridas.", 'success' )

    return redirect( url_for( 'aves.ave_classifi' ))
    




