import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.sessions.models import Session
from apps.pages.models import PageView
from apps.events.models import Event

@method_decorator(csrf_exempt, name='dispatch')
class TrackEventView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            session_key = request.session.session_key
            
            if not session_key:
                return JsonResponse({'status': 'error', 'message': 'No active session'}, status=400)
                
            session = Session.objects.filter(session_key=session_key).first()
            if not session:
                return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)
            
            path = data.get('path')
            
            # Find the most recent page view for this path and session
            page_view = PageView.objects.filter(session=session, path=path).order_by('-timestamp').first()
            
            # Handle scroll depth update
            scroll_depth = data.get('scroll_depth')
            if scroll_depth is not None and page_view:
                if scroll_depth > page_view.scroll_depth_max:
                    page_view.scroll_depth_max = min(100, max(0, scroll_depth))
                    page_view.save()
            
            # Handle events
            events = data.get('events', [])
            for evt in events:
                Event.objects.create(
                    session=session,
                    page_view=page_view,
                    event_type=evt.get('type', 'custom'),
                    element_id=evt.get('element_id', '')[:100],
                    custom_data=evt.get('data', {})
                )
                
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
