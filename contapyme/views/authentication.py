from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from contapyme.functions.login.login import login

@csrf_exempt
def authentication(request):
    if request.method == 'POST':
        try:
            db_name = request.db_name
            # Get authentication
            keyagent = login(db_name)
            if keyagent:
                return JsonResponse(keyagent, safe=False, status=200)
            else:
                return JsonResponse({'Error': 'User authentication failed'}, safe=False, status=401)
            
        # If there is an error    
        except Exception as e:
            return JsonResponse({'Error': str(e)}, safe=False, status=500)