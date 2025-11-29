from app import create_app
from waitress import serve

if __name__ == "__main__":
    #create_app().run(debug=False)
    serve(create_app())