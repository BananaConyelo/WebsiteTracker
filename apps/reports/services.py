from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, ExtractHour, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from apps.visitors.models import Visitor
from apps.sessions.models import Session
from apps.pages.models import PageView
from apps.events.models import Event

class TrafficAnalyticsService:
    @staticmethod
    def get_summary_metrics(days=30):
        start_date = timezone.now() - timedelta(days=days)
        now = timezone.now()

        sessions = Session.objects.filter(start_time__gte=start_date)
        unique_visitors = sessions.values('visitor_id').distinct().count()
        returning_visitors = Visitor.objects.filter(
            sessions__start_time__gte=start_date
        ).annotate(
            recent_sessions=Count('sessions', filter=Q(sessions__start_time__gte=start_date))
        ).filter(recent_sessions__gt=1).distinct().count()

        active_threshold = now - timedelta(minutes=5)
        active_users = Session.objects.filter(end_time__gte=active_threshold).values('visitor_id').distinct().count()

        total_sessions = sessions.count()
        total_pageviews = PageView.objects.filter(timestamp__gte=start_date).count()
        avg_duration = Session.objects.filter(start_time__gte=start_date, end_time__isnull=False).annotate(
            duration=F('end_time') - F('start_time')
        ).aggregate(avg_duration=Avg('duration'))['avg_duration']
        bounce_sessions = sessions.annotate(pageview_count=Count('page_views')).filter(pageview_count=1).count()

        return {
            'unique_visitors': unique_visitors,
            'returning_visitors': returning_visitors,
            'active_users': active_users,
            'total_sessions': total_sessions,
            'total_pageviews': total_pageviews,
            'pages_per_session': round(total_pageviews / total_sessions, 2) if total_sessions > 0 else 0,
            'avg_session_duration': round(avg_duration.total_seconds() / 60, 1) if avg_duration else 0,
            'bounce_rate': round((bounce_sessions / total_sessions) * 100, 1) if total_sessions > 0 else 0,
        }

    @staticmethod
    def get_traffic_sources(days=30):
        start_date = timezone.now() - timedelta(days=days)
        sessions = Session.objects.filter(start_time__gte=start_date)

        social_count = sessions.filter(is_social=True).count()
        search_count = sessions.filter(is_search=True).count()
        direct_count = sessions.filter(Q(referrer__isnull=True) | Q(referrer__exact='')).count()
        referral_count = sessions.exclude(Q(referrer__isnull=True) | Q(referrer__exact='') | Q(is_social=True) | Q(is_search=True)).count()

        return {
            'Social': social_count,
            'Search': search_count,
            'Direct': direct_count,
            'Referral': referral_count if referral_count > 0 else 0
        }

    @staticmethod
    def get_daily_traffic(days=30):
        start_date = timezone.now() - timedelta(days=days)
        daily = PageView.objects.filter(timestamp__gte=start_date).annotate(day=TruncDay('timestamp')).values('day').annotate(count=Count('id')).order_by('day')
        return [{'label': item['day'].strftime('%Y-%m-%d'), 'count': item['count']} for item in daily]

    @staticmethod
    def get_weekly_traffic(days=90):
        start_date = timezone.now() - timedelta(days=days)
        weekly = PageView.objects.filter(timestamp__gte=start_date).annotate(week=TruncWeek('timestamp')).values('week').annotate(count=Count('id')).order_by('week')
        return [{'label': item['week'].strftime('%Y-%m-%d'), 'count': item['count']} for item in weekly]

    @staticmethod
    def get_monthly_traffic(days=365):
        start_date = timezone.now() - timedelta(days=days)
        monthly = PageView.objects.filter(timestamp__gte=start_date).annotate(month=TruncMonth('timestamp')).values('month').annotate(count=Count('id')).order_by('month')
        return [{'label': item['month'].strftime('%Y-%m'), 'count': item['count']} for item in monthly]

    @staticmethod
    def get_peak_hours(days=30):
        start_date = timezone.now() - timedelta(days=days)
        hourly = Session.objects.filter(start_time__gte=start_date).annotate(hour=ExtractHour('start_time')).values('hour').annotate(count=Count('id')).order_by('hour')
        return [{'hour': item['hour'], 'count': item['count']} for item in hourly]

    @staticmethod
    def get_peak_days(days=30):
        start_date = timezone.now() - timedelta(days=days)
        weekday = Session.objects.filter(start_time__gte=start_date).annotate(day=ExtractWeekDay('start_time')).values('day').annotate(count=Count('id')).order_by('day')
        return [{'day': item['day'], 'count': item['count']} for item in weekday]

    @staticmethod
    def get_most_visited_pages(days=30, limit=10):
        start_date = timezone.now() - timedelta(days=days)
        return list(PageView.objects.filter(timestamp__gte=start_date).values('path').annotate(count=Count('id')).order_by('-count')[:limit])

    @staticmethod
    def get_least_visited_pages(days=30, limit=10):
        start_date = timezone.now() - timedelta(days=days)
        return list(PageView.objects.filter(timestamp__gte=start_date).values('path').annotate(count=Count('id')).order_by('count')[:limit])

class LocationAnalyticsService:
    @staticmethod
    def get_countries(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(Visitor.objects.filter(created_at__gte=start_date)
            .values('country')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
            
    @staticmethod
    def get_cities(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(Visitor.objects.filter(created_at__gte=start_date)
            .exclude(city__isnull=True).exclude(city='')
            .values('city', 'country')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])

class DeviceAnalyticsService:
    @staticmethod
    def get_device_types(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(Visitor.objects.filter(created_at__gte=start_date)
            .values('device_type')
            .annotate(count=Count('id'))
            .order_by('-count'))
            
    @staticmethod
    def get_browsers(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(Visitor.objects.filter(created_at__gte=start_date)
            .values('browser_type')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
            
    @staticmethod
    def get_operating_systems(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(Visitor.objects.filter(created_at__gte=start_date)
            .values('operating_system')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])

class BehaviorAnalyticsService:
    @staticmethod
    def get_top_pages(days=30):
        start_date = timezone.now() - timedelta(days=days)
        return list(PageView.objects.filter(timestamp__gte=start_date)
            .values('path')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
            
    @staticmethod
    def get_average_scroll_depth(days=30):
        start_date = timezone.now() - timedelta(days=days)
        result = PageView.objects.filter(timestamp__gte=start_date).aggregate(avg_scroll=Avg('scroll_depth_max'))
        return round(result['avg_scroll'] or 0, 1)

    @staticmethod
    def get_landing_pages(days=30):
        start_date = timezone.now() - timedelta(days=days)
        sessions = Session.objects.filter(start_time__gte=start_date).prefetch_related('page_views')
        landing_counts = {}
        for session in sessions:
            first_page = session.page_views.order_by('timestamp').first()
            if first_page:
                landing_counts[first_page.path] = landing_counts.get(first_page.path, 0) + 1
        return [{'path': k, 'count': v} for k, v in sorted(landing_counts.items(), key=lambda item: item[1], reverse=True)[:10]]

    @staticmethod
    def get_exit_pages(days=30):
        start_date = timezone.now() - timedelta(days=days)
        sessions = Session.objects.filter(start_time__gte=start_date).prefetch_related('page_views')
        exit_counts = {}
        for session in sessions:
            last_page = session.page_views.order_by('-timestamp').first()
            if last_page:
                exit_counts[last_page.path] = exit_counts.get(last_page.path, 0) + 1
        return [{'path': k, 'count': v} for k, v in sorted(exit_counts.items(), key=lambda item: item[1], reverse=True)[:10]]

class EventAnalyticsService:
    @staticmethod
    def get_event_summary(days=30):
        start_date = timezone.now() - timedelta(days=days)
        events = Event.objects.filter(timestamp__gte=start_date)
        return {
            'clicks': events.filter(event_type='click').count(),
            'forms': events.filter(event_type='form').count(),
            'custom': events.filter(event_type='custom').count(),
        }
        
    @staticmethod
    def get_recent_events(limit=20):
        return Event.objects.select_related('session').order_by('-timestamp')[:limit]
