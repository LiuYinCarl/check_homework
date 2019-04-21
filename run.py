from app import create_app

_app = create_app()

_app.secret_key = 'squirrel'


@_app.before_first_request
def create_db():
    from app.models import db, User
    db.drop_all()
    db.create_all()

    admin = User(password='root', email='admin@example.com')
    db.session.add(admin)

    guestes = [User(password='guest1', email='guest1@example.com'),
               User(password='guest2', email='guest2@example.com'),
               User(password='aaa', email='1427518212@qq.com')]
    db.session.add_all(guestes)
    db.session.commit()


if __name__ == "__main__":
    _app.run(debug=_app.config['DEBUG'])
