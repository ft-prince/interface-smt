from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Station, ProductMedia,Refresher


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
    # Get the first Refresher object's time_duration or default to 3 minutes
    refresh_duration = Refresher.objects.first().time_duration if Refresher.objects.exists() else 3
    
    return render(request, 'station_slider.html', {
        'station': station,
        'refresh_duration': refresh_duration
    })




from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.http import condition
from django.conf import settings
from wsgiref.util import FileWrapper
import os
import mimetypes
import time
import json

from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
import os
import json

def stream_video(request, video_path):
    # Remove any leading slashes and 'media' from the path
    clean_path = video_path.lstrip('/').replace('media/', '', 1)
    path = os.path.join(settings.MEDIA_ROOT, clean_path)
    
    range_header = request.META.get('HTTP_RANGE', '').strip()
    size = os.path.getsize(path)
    
    if range_header:
        range_s, range_e = range_header.split('=')[-1].split('-')
        range_start = int(range_s)
        range_end = int(range_e) if range_e else size - 1
        length = range_end - range_start + 1

        response = StreamingHttpResponse(
            file_iterator(path, offset=range_start, length=length),
            status=206,
            content_type='video/mp4'
        )
        response['Content-Range'] = f'bytes {range_start}-{range_end}/{size}'
    else:
        response = StreamingHttpResponse(
            file_iterator(path),
            content_type='video/mp4'
        )
    
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(size)
    return response

def stream_pdf(request, pdf_path):
    # Remove any leading slashes and 'media' from the path
    clean_path = pdf_path.lstrip('/').replace('media/', '', 1)
    path = os.path.join(settings.MEDIA_ROOT, clean_path)
    
    chunk_size = 8192
    response = StreamingHttpResponse(
        file_iterator(path, chunk_size=chunk_size),
        content_type='application/pdf'
    )
    response['Content-Length'] = os.path.getsize(path)
    return response

def file_iterator(path, chunk_size=8192, offset=0, length=None):
    with open(path, 'rb') as f:
        if offset:
            f.seek(offset)
        remaining = length if length is not None else None
        while True:
            if remaining is not None:
                chunk_size = min(chunk_size, remaining)
            data = f.read(chunk_size)
            if not data:
                break
            if remaining is not None:
                remaining -= len(data)
            yield data
            if remaining == 0:
                break

def stream_pdf(request, pdf_path):
    path = os.path.join(settings.MEDIA_ROOT, pdf_path)
    chunk_size = 8192
    
    response = StreamingHttpResponse(
        file_iterator(path, chunk_size=chunk_size),
        content_type='application/pdf'
    )
    response['Content-Length'] = os.path.getsize(path)
    return response

def file_iterator(path, chunk_size=8192, offset=0, length=None):
    with open(path, 'rb') as f:
        if offset:
            f.seek(offset)
        remaining = length if length is not None else None
        while True:
            if remaining is not None:
                chunk_size = min(chunk_size, remaining)
            data = f.read(chunk_size)
            if not data:
                break
            if remaining is not None:
                remaining -= len(data)
            yield data
            if remaining == 0:
                break

def get_station_media_updates(request, station_id):
    def event_stream():
        last_check = time.time()
        while True:
            station = Station.objects.get(pk=station_id)
            media = station.selected_media.all()
            
            media_data = [{
                'url': m.file.url,
                'type': m.file.name.split('.')[-1].lower(),
                'duration': m.duration
            } for m in media]
            
            yield f"data: {json.dumps(media_data)}\n\n"
            time.sleep(60)  # Check for updates every minute
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response