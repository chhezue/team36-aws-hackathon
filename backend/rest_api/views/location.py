from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from local_data.models import Location

@csrf_exempt
def get_districts(request):
    districts = Location.objects.values_list('gu', flat=True).distinct()
    return JsonResponse({'districts': list(districts)})