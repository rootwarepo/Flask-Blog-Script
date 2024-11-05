from app import app
from routes import *
from db_init import *

if __name__ == '__main__':
    app.run(debug=True)