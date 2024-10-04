from flask import Blueprint, request, jsonify, redirect, url_for
from flask_restx import Api, Resource, fields
from models import db, Book, User
from auth0 import requires_auth, AuthError
import requests
from config import Config

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
    @requires_auth
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
    @requires_auth
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
    @requires_auth
    def delete(self, id):
        """Delete a book given its identifier"""
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return '', 204

auth_ns = api.namespace('auth', description='Authentication operations')

@auth_ns.route('/login')
class Auth0Login(Resource):
    @api.doc(description='Redirect to Auth0 login page')
    def get(self):
        """Redirect to Auth0 login page"""
        return redirect(f'https://{Config.AUTH0_DOMAIN}/authorize?'
                        f'audience={Config.AUTH0_API_AUDIENCE}&'
                        f'response_type=code&'
                        f'client_id={Config.AUTH0_CLIENT_ID}&'
                        f'redirect_uri={request.url_root}api/auth/callback')

@auth_ns.route('/callback')
class Auth0Callback(Resource):
    @api.doc(description='Handle Auth0 callback')
    def get(self):
        """Handle Auth0 callback"""
        code = request.args.get('code')
        token_url = f'https://{Config.AUTH0_DOMAIN}/oauth/token'
        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': Config.AUTH0_CLIENT_ID,
            'client_secret': Config.AUTH0_CLIENT_SECRET,
            'code': code,
            'redirect_uri': f'{request.url_root}api/auth/callback'
        }
        token_headers = {'content-type': 'application/json'}
        token_response = requests.post(token_url, json=token_payload, headers=token_headers)
        
        if token_response.status_code != 200:
            return {'error': 'Failed to obtain access token'}, 400
        
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        
        return {'access_token': access_token}, 200

@api_bp.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
