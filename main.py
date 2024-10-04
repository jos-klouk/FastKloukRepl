from app import create_app
from flask import redirect, url_for

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('api.doc'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
