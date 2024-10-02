from django.http import JsonResponse

def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/hives',
        'GET /api/hives/:id'
    ]

    return JsonResponse(routes, safe=False)