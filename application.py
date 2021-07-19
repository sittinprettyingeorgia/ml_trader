
# file in apps root directory that serves as entry point for our flask application

from flaskr import init_app

application = init_app()

if __name__ == "__main__":
    application.run()
