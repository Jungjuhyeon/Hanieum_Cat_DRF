import logging
import sys
sys.path.insert(0, 'dj_pr')


import azure.functions as func
from dj_pr.wsgi import application

wsgi = func.WsgiMiddleware(app=application)


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    print("Starting request processing...")
    result= wsgi.main(req, context)
    print("Request processing completed.") 
    return result