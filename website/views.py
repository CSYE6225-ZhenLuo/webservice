from sre_parse import State
from telnetlib import STATUS
from django.http import JsonResponse, HttpResponse

def healthy(request):
    return HttpResponse()