from app import app,db 

if __name__ == "__main__":
    with app.app_context():
        #db.init_app(app)
        db.create_all()
        app.run(debug=True,port=5000)
