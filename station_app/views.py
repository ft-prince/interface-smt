from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Station, ProductMedia


def get_product_media(request):
    product_ids = request.GET.getlist('products[]')
    media = ProductMedia.objects.filter(product__in=product_ids)
    
    media_list = [
        {
            'id': media.id,
            'url': media.file.url,
            'type': media.file.name.split('.')[-1].lower(),
            'duration': media.duration
        }
        for media in media
    ]
    
    return JsonResponse({'media': media_list})

def get_station_media(request, station_id):
    station = Station.objects.get(pk=station_id)
    selected_media = station.selected_media.all()
    
    media_data = [
        {
            'url': m.file.url,
            'type': m.file.name.split('.')[-1].lower(),
            'duration': m.duration
        }
        for m in selected_media
    ]

    return JsonResponse({'media': media_data})

def station_media_slider(request, station_id):
    station = get_object_or_404(Station, pk=station_id)
    return render(request, 'station_slider.html', {'station': station})