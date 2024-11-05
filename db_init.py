from models import db, User
from app import app

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        new_user = User(
            username='admin', 
            email='admin@admin.com', 
            full_name='admin', 
            password='123', 
            role='admin', 
            profile_picture="https://static.thenounproject.com/png/5572537-200.png", 
            about="Hakkında içeriğinizi düzenleyebilirsiniz."
        )
        db.session.add(new_user)
        db.session.commit()