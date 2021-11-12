from flask import Flask, render_template

##https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
def create_app( test_config=None ):
    app = Flask( __name__, instance_relative_config=True )

    app.config.from_mapping(
        SECRET_KEY='dev' )

    
    @app.route( '/' )
    def index():
        """Página inicial"""
        return render_template( "index.html" )

    return app













