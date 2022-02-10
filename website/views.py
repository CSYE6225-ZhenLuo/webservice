from django.http import JsonResponse

def healthy(request):
    data = {
        'code' : '200',
        'message' : 'server responds with 200 OK if it is healhty.',
    }
    return JsonResponse(data=data)