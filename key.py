def key():
    from app import app
    with app.app_context():
        key = app.config['OPENAI_API_KEY']
    return key