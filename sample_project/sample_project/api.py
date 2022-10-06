import orjson
from typing import Any, Optional, Tuple

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

from ninja import NinjaAPI
from ninja.renderers import BaseRenderer
from ninja.parser import Parser
from ninja.errors import ValidationError

 
from the_user.api import router as user_router

from the_system.api import router as system_router





class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)

 

api = NinjaAPI(urls_namespace="api",
                title ="sample app",
                description ="sample app apis",
                docs_decorator=login_required,
                docs_url="/docs/",
                csrf=True,
              
                renderer=ORJSONRenderer()  ,
                parser=ORJSONParser())


 
api.add_router("/", user_router)
api.add_router("/", system_router)


# @api.exception_handler(ValidationError)
# def validation_errors(request, exc):
#     return HttpResponse(f"Invalid input {exc}", status=422)