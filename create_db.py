from app import db, app  # adjust import if your db is in another file

with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")
