from sanic import Sanic, Request, HTTPResponse, json
from sanic.handlers import ErrorHandler
from user.views import bp as ur
from settings import settings
from neomodel import config
from neomodel.core import install_all_labels
from sanic_ext import Config
from note.views import bp as nr


class ExceptionHandler(ErrorHandler):

    def default(self, request: Request, exception: Exception) -> HTTPResponse:
        status_code = getattr(exception, 'status_code', 500)
        return json({'message': str(exception), 'status': status_code}, status=status_code)


app = Sanic('fundoo')

app.error_handler = ExceptionHandler()
config.DATABASE_URL = settings.neo_uri
app.extend(config=Config(oas_url_prefix='',
                         oas_uri_to_swagger='/docs',
                         oas_ui_swagger_html_title='Fundoo',
                         api_title='Fundoo',
                         swagger_ui_configuration={'docExpansion': 'list'},
                         oas_ui_default='swagger'
                         ))

app.ext.openapi.add_security_scheme(
    "authorization",
    "http",
    scheme="bearer",
    bearer_format="JWT",
)

app.blueprint(ur)
app.blueprint(nr)
