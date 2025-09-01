from django.views.decorators.csrf import csrf_exempt
import secrets
from django.http.response import JsonResponse

from settings.models.config import Config

@csrf_exempt
def get_apikey(request):

    if request.method == 'GET': 

        try:
            db_name = request.GET.get('database')

            c = Config()
            apikey  = c.get_config(db_name, 'apikey')['apikey']

            return JsonResponse({"apikey" : apikey}, safe=False, status=200)
        
        except Exception as e:

            return JsonResponse({'error': str(e)}, safe=False, status=500)


