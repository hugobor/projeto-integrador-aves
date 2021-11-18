from flask import Flask, render_template

import os

##https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
def create_app( test_config=None ):
    app = Flask( __name__, instance_relative_config=True )

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join( app.instance_path, 'aves_pi.db' ),
    )

    if test_config is None:
        app.config.from_pyfile( 'config.py', silent=True )
    else:
        app.config.from_mapping( test_config )

    try:
        os.makedirs( app.instance_path )
    except OSError:
        pass

    from . import db
    db.init_app( app )

    from . import aves
    app.register_blueprint( aves.avesbp )
    
    @app.route( '/' )
    def index():
        """Página inicial"""
        return render_template( "index.html" )

    return app













