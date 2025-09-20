from django.shortcuts import render
from django.http import JsonResponse

# MercadoLibre Views


class auth:
    @staticmethod
    def login(request):
        return JsonResponse({"message": "MercadoLibre login - Coming soon"}, status=200)

    @staticmethod
    def refresh_token(request):
        return JsonResponse({"message": "MercadoLibre refresh token - Coming soon"}, status=200)


class products:
    @staticmethod
    @staticmethod
    def update(request):
        return JsonResponse({"message": "MercadoLibre products update - Coming soon"}, status=200)


class orders:
    @staticmethod
    def sync(request):
        return JsonResponse({"message": "MercadoLibre orders sync - Coming soon"}, status=200)

    @staticmethod
    def update(request):
        return JsonResponse({"message": "MercadoLibre orders update - Coming soon"}, status=200)


class inventory:
    @staticmethod
    def update(request):
        return JsonResponse({"message": "MercadoLibre inventory update - Coming soon"}, status=200)
