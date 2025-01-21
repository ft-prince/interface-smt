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


import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def chat_message(self, event):
        message = event['message']
        
        # Format the message based on its type/content
        formatted_message = self.format_message(message)
        
        # Send formatted message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': formatted_message,
            'raw_data': message  # Include raw data for advanced frontend handling
        }))

    def format_message(self, message):
        """Format different types of messages"""
        if isinstance(message, str):
            return message
            
        try:
            if 'alert_type' in message:
                if message['alert_type'] == 'control_chart_alert':
                    return self.format_control_chart_message(message)
                elif message['alert_type'] == 'daily_checklist_alert':
                    return self.format_checklist_message(message)
                elif message['alert_type'] == 'p_chart_alert':
                    return self.format_pchart_message(message)
                # Add more alert types as needed
            return json.dumps(message, indent=2)  # Fallback formatting
        except Exception as e:
            return f"Error formatting message: {str(e)}"

    def format_control_chart_message(self, message):
        return f"""Control Chart Alert:
Location: {message.get('machine_location')}
Date: {message.get('date')}
Violations: {', '.join(message.get('violations', []))}
Severity: {message.get('severity', 'unknown')}"""

    def format_checklist_message(self, message):
        checkpoint = message.get('checkpoint', {})
        return f"""Checklist Alert:
Location: {message.get('machine_location')}
Checkpoint {checkpoint.get('number')}: {checkpoint.get('name')}
Status: {'Not OK' if checkpoint.get('status') == '✘' else 'OK'}
Action Required: {message.get('needs_attention', False)}"""

    def format_pchart_message(self, message):
        return f"""P-Chart Alert:
Location: {message.get('location')}
Part: {message.get('part_info')}
Issues: {', '.join(message.get('violations', []))}
Severity: {message.get('severity', 'unknown')}"""