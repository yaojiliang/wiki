from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def test(request):

    return JsonResponse({'code':200,'data':{}})
