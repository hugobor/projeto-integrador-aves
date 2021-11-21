from flask import Flask, render_template, url_for, send_from_directory, current_app

import os


DATABASE_PATH = 'aves_pi.db'
MEDIA_PATH = '/static/media/'
ALLOWED_EXTENSIONS_IMG = { 'png', 'jpeg', 'jpg', 'gif', 'webp' }
ALLOWED_EXTENSIONS_VID = { 'webm', 'ogg', 'ogv', 'mp4', 'mpg', 'm4v', 'm4p', '3gp', 'mpeg' }
ALLOWED_EXTENSIONS_AUD = { '3gp', 'mpg', 'mpeg', 'mp4', 'mpa', 'ogg', 'oga', 'opus' }
ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS_IMG.union( ALLOWED_EXTENSIONS_IMG ).union( ALLOWED_EXTENSIONS_AUD )


##https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
def create_app( test_config=None ):
    app = Flask( __name__, instance_relative_config=True )

    app.config.from_mapping(
        SECRET_KEY='dev-dev-dev',
        DATABASE=os.path.join( app.instance_path, DATABASE_PATH ),
        MEDIA_FOLDER=os.path.join( app.root_path, MEDIA_PATH ),
    )

    if test_config is None:
        app.config.from_pyfile( 'config.py', silent=True )
    else:
        app.config.from_mapping( test_config )

    try:
        os.makedirs( app.instance_path )
        os.makedirs( app.config[ 'MEDIA_FOLDER' ] )
    except OSError:
        pass

    from . import db
    db.init_app( app )

    from . import aves
    app.register_blueprint( aves.avesbp )


    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'media/favicon.png' )
    
    @app.route( '/' )
    def index():
        """Página inicial"""

        con = db.get_db()
        tauato_miudo = con.execute( "select * from ave where lower( nome_popular ) = lower( 'tauató-miúdo' );" ).fetchone()
        return render_template( "index.html", img_path=tauato_miudo[ 'thumbnail' ],
                                file_join=build_media_path )



    return app


    return os.path.join( MEDIA_FOLDER, file_path )


def build_media_path( file_path ):
    if file_path is None:
        file_path = ''
    return os.path.join( MEDIA_PATH, file_path )









