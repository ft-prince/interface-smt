import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
   
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))


from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db import models
from channels.layers import get_channel_layer
import json

class NotificationConsumer(WebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    Manages connection, disconnection, and message broadcasting.
    """
    
    def connect(self):
        """Establish WebSocket connection and add to notification group."""
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        """Handle WebSocket disconnection and cleanup."""
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def chat_message(self, event):
        """
        Process and broadcast notification messages.
        Ensures consistent message structure and severity levels.
        """
        message = event['message']
        
        if isinstance(message, dict) and 'alert_type' in message:
            if 'severity' not in message:
                message['severity'] = self._calculate_severity(message)

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    def _calculate_severity(self, message):
        """
        Calculate notification severity based on alert type and content.
        Returns 'high', 'medium', or 'normal' based on predefined rules.
        """
        alert_type = message.get('alert_type')
        severity_rules = {
            'fixture_cleaning_alert': self._get_fixture_cleaning_severity,
            'daily_checklist_alert': self._get_checklist_severity,
            'weekly_checklist_alert': self._get_checklist_severity,
            'monthly_checklist_alert': self._get_checklist_severity,
            'control_chart_alert': self._get_control_chart_severity,
            'p_chart_alert': self._get_pchart_severity,
            'soldering_bit_alert': self._get_soldering_bit_severity  # Add this line
            
        }
        
        severity_func = severity_rules.get(alert_type)
        return severity_func(message) if severity_func else 'normal'

    def _get_fixture_cleaning_severity(self, message):
        """Calculate severity for fixture cleaning alerts."""
        issues = message.get('issues', [])
        return 'high' if len(issues) > 2 else 'medium'

    def _get_checklist_severity(self, message):
        """Calculate severity for checklist-related alerts."""
        checkpoint = message.get('checkpoint', {})
        if checkpoint.get('status') == '✘' and message.get('needs_attention'):
            return 'high'
        return 'medium'

    def _get_control_chart_severity(self, message):
        """Calculate severity for control chart alerts."""
        violations = message.get('violations', [])
        return 'high' if any('critical' in v.lower() for v in violations) else 'medium'

    def _get_pchart_severity(self, message):
        """Calculate severity for p-chart alerts."""
        violations = message.get('violations', [])
        return 'high' if len(violations) > 1 else 'medium'

    def _get_soldering_bit_severity(self, message):
        """Calculate severity for soldering bit alerts based on remaining life."""
        bit_life_remaining = message.get('bit_life_remaining', 0)
        warning_threshold = message.get('warning_threshold', 0)
        
        if bit_life_remaining <= 0:
            return 'high'  # Critical - bit needs immediate replacement
        elif bit_life_remaining <= warning_threshold:
            return 'medium'  # Warning - bit approaching end of life
        return 'normal'  # Bit life is within acceptable range








from channels.generic.http import AsyncHttpConsumer
from asgiref.sync import sync_to_async
from station_app.models import Station
import json
import asyncio
import os
from django.conf import settings
import aiofiles

from channels.generic.http import AsyncHttpConsumer
from asgiref.sync import sync_to_async
from station_app.models import Station
import json
import asyncio

class MediaUpdatesConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        headers = [
            (b"Cache-Control", b"no-cache"),
            (b"Content-Type", b"text/event-stream"),
            (b"Connection", b"keep-alive"),
            (b"X-Accel-Buffering", b"no")
        ]
        
        await self.send_headers(headers=headers)
        
        try:
            station_id = self.scope['url_route']['kwargs']['station_id']
            
            while True:
                try:
                    station = await sync_to_async(Station.objects.get)(pk=station_id)
                    media = await sync_to_async(list)(station.selected_media.all())
                    
                    media_data = [{
                        'url': m.file.url,
                        'type': m.file.name.split('.')[-1].lower(),
                        'duration': m.duration
                    } for m in media]
                    
                    # Send the media data
                    await self.send_body(f"data: {json.dumps(media_data)}\n\n".encode('utf-8'))
                    
                    # Send a single heartbeat and wait
                    await asyncio.sleep(30)
                    await self.send_body(b": heartbeat\n\n")
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    await self.send_body(f"event: error\ndata: {str(e)}\n\n".encode('utf-8'))
                    await asyncio.sleep(5)
                    
        except Exception as e:
            await self.send_body(f"event: error\ndata: {str(e)}\n\n".encode('utf-8'))
        finally:
            await self.send_body(b"", more_body=False)
            
                        
class StreamVideoConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        video_path = self.scope['url_route']['kwargs']['video_path']
        path = os.path.join(settings.MEDIA_ROOT, video_path)
        
        if not os.path.exists(path):
            await self.send_response(404, b"Video not found")
            return
            
        range_header = self.scope['headers'].get(b'range', b'').decode()
        
        try:
            file_size = os.path.getsize(path)
            
            if range_header:
                range_s, range_e = range_header.replace('bytes=', '').split('-')
                range_start = int(range_s)
                range_end = int(range_e) if range_e else file_size - 1
                content_length = range_end - range_start + 1
                
                headers = [
                    (b"Content-Type", b"video/mp4"),
                    (b"Accept-Ranges", b"bytes"),
                    (b"Content-Length", str(content_length).encode()),
                    (b"Content-Range", f"bytes {range_start}-{range_end}/{file_size}".encode()),
                ]
                await self.send_headers(headers=headers, status=206)
            else:
                headers = [
                    (b"Content-Type", b"video/mp4"),
                    (b"Accept-Ranges", b"bytes"),
                    (b"Content-Length", str(file_size).encode()),
                ]
                await self.send_headers(headers=headers)
            
            async with aiofiles.open(path, 'rb') as f:
                if range_header:
                    await f.seek(range_start)
                    remaining = content_length
                    while remaining > 0:
                        chunk_size = min(8192, remaining)
                        chunk = await f.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        await self.send_body(chunk, more_body=(remaining > 0))
                else:
                    while chunk := await f.read(8192):
                        await self.send_body(chunk, more_body=True)
                    await self.send_body(b"", more_body=False)
                    
        except Exception as e:
            await self.send_response(500, str(e).encode())

class StreamPDFConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        file_path = self.scope['url_route']['kwargs']['file_path']
        path = os.path.join(settings.MEDIA_ROOT, file_path.lstrip('/'))
        
        if not os.path.exists(path):
            await self.send_response(404, b"PDF not found")
            return
            
        try:
            file_size = os.path.getsize(path)
            headers = [
                (b"Content-Type", b"application/pdf"),
                (b"Content-Length", str(file_size).encode()),
                (b"Content-Disposition", b"inline"),
            ]
            
            await self.send_headers(headers=headers)
            
            async with aiofiles.open(path, 'rb') as f:
                while chunk := await f.read(8192):
                    await self.send_body(chunk, more_body=True)
                await self.send_body(b"", more_body=False)
                
        except Exception as e:
            await self.send_response(500, str(e).encode())