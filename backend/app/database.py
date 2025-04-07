"""
Modified init_db function to fix SQLAlchemy initialization issues
"""
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base

def init_db(app):
    """Initialize the database with the application context"""
    engine = create_engine(app.config['DATABASE_URI'])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    app.db_session = Session()
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if hasattr(app, 'db_session'):
            app.db_session.close()
