from flask import Flask, request, Blueprint
import pymongo 
import jwt

app = Flask(__name__)
key = "uvbpeArr1h3S6b-dJtw9__oTotYctlm3BCFcTx1Un6c"
books_blueprint: Blueprint = Blueprint("books", __name__)


@books_blueprint.route('/save', methods=['POST'])
def save_book():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    data = request.json.copy()
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    books = db['books']
    if not {'id', 'author', 'country', 'pages', 'title', 'year'}.issubset(set(data.keys())):
	    return dict(message='Mandatory Fields Missing.')
    book_json = {
        'id': data['id'],
        'author': data['author'],
        'country': data['country'],
        'language': data.get('language', "English"),
        'link': data.get('link', ""),
        'pages': int(data['pages']),
        'title': data['title'],
        'year': int(data['year'])
    }
    save = books.insert_one(document=book_json)
    return dict(_id=str(save.inserted_id), meassage='Saved Book Successfully.')


@books_blueprint.route('/list', methods=['GET'])
def list_books():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    books = db['books']
    pipeline = [
        {
            '$addFields': {
                '_id': {
                    '$toString': '$_id'
                }
            }
        }
    ]
    books = list(books.aggregate(pipeline=pipeline))
    return dict(books=books)


@books_blueprint.route('/delete', methods=['DELETE'])
def delete_book():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    from bson import ObjectId
    _id = request.args.get("_id")
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    books = db['books']
    if not books.find_one(filter={'_id': ObjectId(_id)}):
        return dict(message='Book Not Found.')
    books.delete_one(filter={'_id': ObjectId(_id)})
    return dict(message='Deleted SuccessFully.')


@books_blueprint.route('/update', methods=['PUT'])
def update_book():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    data = request.json.copy()
    if not {'_id'}.issubset(set(data.keys())):
	    return dict(message='Mandatory Fields Missing.')
    _id = data.pop('_id')
    from bson import ObjectId
    _id = request.args.get("_id")
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    books = db['books']
    book = books.find_one(filter={'_id': ObjectId(_id)})
    if not book:
        return dict(message='Book Not Found.')
    book.pop('_id')
    book.update(data)
    books.update_one(filter={'_id': ObjectId(_id)}, update=book)
    return dict(message='Updated SuccessFully.')


@app.route('/auth/register', methods=['PUT'])
def register():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    data = request.get_json(force=True)
    if not {'username', 'password1', 'password2', 'email'}.issubset(set(data.keys())):
	    return dict(message='Mandatory Fields Missing.')
    if data['password1'] != data['password2']:
        return dict(message='Password not matching.')
    data.pop('password1')
    data['password'] = data.pop('password2')
    print(data)
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    users = db['users']
    if users.find_one({"username": data['username']}):
        return dict(message=f'User with username {data["username"]} already exists.')
    users = users.insert_one(data)
    return dict(message='Registered SuccessFully.')


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        encoded_jwt = request.headers.get('Authorization')
        decoded = jwt.decode(encoded_jwt, key, algorithms="HS256")
    except:
        return dict(message='Unauthorized to call this api. Either missing or error in JWT token sent.')
    data = request.get_json(force=True)
    if not {'username', 'password'}.issubset(set(data.keys())):
	    return dict(message='Missing username or password.')
    
    username = data['username']
    password = data['password']
    
    client = pymongo.MongoClient("mongodb+srv://dbUser:dbUserPassword@cst-anchalpreet-flask.wfjxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['anchalpreet']
    users = db['users']
    user = users.find_one({"username": data['username']})
    if user and user['password'] == password:
        return dict(message='Logged in SuccessFully.')    
    else:
        return dict(message='Incorrect username or password')    





app.register_blueprint(books_blueprint, url_prefix="/books")

# if __name__ == "__main__":
#     app.run(debug=True)
