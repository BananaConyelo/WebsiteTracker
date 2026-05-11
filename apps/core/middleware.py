import uuid
import requests
from django.utils import timezone
from django.conf import settings
from apps.visitors.models import Visitor
from apps.sessions.models import Session
from apps.pages.models import PageView
from user_agents import parse

class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only track if path doesn't start with /admin/ or /static/
        if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
            self.track_request(request)

        response = self.get_response(request)
        return response

    def track_request(self, request):
        ip_address = self.get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        
        # 1. Handle Visitor
        visitor_uuid_str = request.COOKIES.get('visitor_uuid')
        visitor = None
        
        if visitor_uuid_str:
            try:
                visitor = Visitor.objects.filter(visitor_uuid=visitor_uuid_str).first()
            except ValueError:
                pass
                
        if not visitor:
            # Create new visitor
            visitor = Visitor(ip_address=ip_address)
            visitor.device_type = 'Mobile' if user_agent.is_mobile else ('Tablet' if user_agent.is_tablet else 'Desktop')
            visitor.browser_type = user_agent.browser.family
            visitor.operating_system = user_agent.os.family
            visitor.save()
            
            # Note: The cookie setting needs to happen on the response, 
            # so we attach it to request to be processed later, or we just rely on session.
            # Actually, we can use the Django session to store visitor_uuid instead of setting cookie directly.
            request.session['visitor_uuid'] = str(visitor.visitor_uuid)
            
            # Simple Location lookup (mock or external API)
            # In a real production environment, use a local GeoIP database to avoid blocking the request
            try:
                # This is a synchronous request, which is bad for perf, but okay for a small prototype
                # We should catch exceptions to avoid failing the main request
                # A better approach is to do this async via Celery
                response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        visitor.country = data.get('country')
                        visitor.city = data.get('city')
                        visitor.save()
            except Exception:
                pass
        
        elif 'visitor_uuid' not in request.session:
            request.session['visitor_uuid'] = str(visitor.visitor_uuid)

        # 2. Handle Session
        if not request.session.session_key:
            request.session.create()
            
        session_key = request.session.session_key
        
        tracker_session = Session.objects.filter(session_key=session_key).first()
        if not tracker_session:
            referrer = request.META.get('HTTP_REFERER', '')
            is_social = any(domain in referrer.lower() for domain in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com'])
            is_search = any(domain in referrer.lower() for domain in ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com'])
            
            tracker_session = Session.objects.create(
                session_key=session_key,
                visitor=visitor,
                referrer=referrer,
                is_social=is_social,
                is_search=is_search
            )
        
        # 3. Handle PageView
        PageView.objects.create(
            session=tracker_session,
            path=request.path
        )
        
        # Update session end time
        tracker_session.end_time = timezone.now()
        tracker_session.save()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
