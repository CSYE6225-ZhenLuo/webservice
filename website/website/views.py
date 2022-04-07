from sre_parse import State
from telnetlib import STATUS
from django.http import JsonResponse, HttpResponse
import statsd

def healthy(request):
    counter = statsd.Counter('APICounter')
    counter.increment('HealthyCall')
    counter.increment('TotalCall')
    return HttpResponse()