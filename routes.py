from flask import Blueprint, request, jsonify, redirect
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, Book, User
from auth import admin_required

api_bp = Blueprint('api', __name__)
api = Api(api_bp, version='1.0', title='Book API', description='A simple Book API')

@api_bp.route('/')
def index():
    return redirect('/api/')

ns = api.namespace('books', description='Book operations')

book_model = api.model('Book', {
    'id': fields.Integer(readonly=True),
    'title': fields.String(required=True),
    'author': fields.String(required=True),
    'publication_year': fields.Integer,
    'isbn': fields.String(required=True)
})

@ns.route('/')
class BookList(Resource):
    @ns.doc('list_books')
    @ns.marshal_list_with(book_model)
    def get(self):
        """List all books"""
        return Book.query.all()

    @ns.doc('create_book')
    @ns.expect(book_model)
    @ns.marshal_with(book_model, code=201)
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new book"""
        data = request.json
        new_book = Book(
            title=data['title'],
            author=data['author'],
            publication_year=data.get('publication_year'),
            isbn=data['isbn']
        )
        db.session.add(new_book)
        db.session.commit()
        return new_book, 201

@ns.route('/<int:id>')
@ns.response(404, 'Book not found')
@ns.param('id', 'The book identifier')
class BookItem(Resource):
    @ns.doc('get_book')
    @ns.marshal_with(book_model)
    def get(self, id):
        """Fetch a book given its identifier"""
        book = Book.query.get_or_404(id)
        return book

    @ns.doc('update_book')
    @ns.expect(book_model)
    @ns.marshal_with(book_model)
    @jwt_required()
    @admin_required
    def put(self, id):
        """Update a book given its identifier"""
        book = Book.query.get_or_404(id)
        data = request.json
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.publication_year = data.get('publication_year', book.publication_year)
        book.isbn = data.get('isbn', book.isbn)
        db.session.commit()
        return book

    @ns.doc('delete_book')
    @ns.response(204, 'Book deleted')
    @jwt_required()
    @admin_required
    def delete(self, id):
        """Delete a book given its identifier"""
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return '', 204

auth_ns = api.namespace('auth', description='Authentication operations')

user_model = api.model('User', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/register')
class UserRegistration(Resource):
    @ns.expect(user_model)
    def post(self):
        """Register a new user"""
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400
        
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        
        return {'message': 'User created successfully'}, 201

@auth_ns.route('/login')
class UserLogin(Resource):
    def post(self):
        """Login and receive an access token"""
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200
        
        return {'message': 'Invalid username or password'}, 401
