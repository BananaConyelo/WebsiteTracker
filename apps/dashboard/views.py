import json
from django.views.generic import TemplateView
from apps.reports.services import (
    TrafficAnalyticsService,
    LocationAnalyticsService,
    DeviceAnalyticsService,
    BehaviorAnalyticsService,
    EventAnalyticsService
)

class DashboardHomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = 30
        
        # Core Metrics
        context['summary'] = TrafficAnalyticsService.get_summary_metrics(days)
        
        # Charts Data
        context['traffic_sources_json'] = json.dumps(TrafficAnalyticsService.get_traffic_sources(days))
        context['devices_json'] = json.dumps(DeviceAnalyticsService.get_device_types(days))
        context['traffic_trend_json'] = json.dumps(TrafficAnalyticsService.get_daily_traffic(days))
        context['peak_hours_json'] = json.dumps(TrafficAnalyticsService.get_peak_hours(days))
        
        # Tables Data
        context['countries'] = LocationAnalyticsService.get_countries(days)
        context['top_pages'] = BehaviorAnalyticsService.get_top_pages(days)
        context['least_pages'] = TrafficAnalyticsService.get_least_visited_pages(days)
        
        return context

class AudienceView(TemplateView):
    template_name = 'dashboard/audience.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = 30
        
        context['browsers_json'] = json.dumps(DeviceAnalyticsService.get_browsers(days))
        context['os_json'] = json.dumps(DeviceAnalyticsService.get_operating_systems(days))
        
        # Map requires an array of {feature: 'country_name/code', value: count}
        countries = LocationAnalyticsService.get_countries(days)
        # Using the country name directly for chartjs-geo 
        map_data = [{"feature": c['country'], "value": c['count']} for c in countries if c['country']]
        context['map_data_json'] = json.dumps(map_data)
        
        context['cities'] = LocationAnalyticsService.get_cities(days)
        
        return context

class BehaviorView(TemplateView):
    template_name = 'dashboard/behavior.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = 30
        
        context['landing_pages'] = BehaviorAnalyticsService.get_landing_pages(days)
        context['exit_pages'] = BehaviorAnalyticsService.get_exit_pages(days)
        context['avg_scroll'] = BehaviorAnalyticsService.get_average_scroll_depth(days)
        
        return context

class EventsView(TemplateView):
    template_name = 'dashboard/events.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = 30
        
        summary = EventAnalyticsService.get_event_summary(days)
        context['events_summary_json'] = json.dumps(summary)
        context['recent_events'] = EventAnalyticsService.get_recent_events(limit=50)
        
        return context

class TimeBasedView(TemplateView):
    template_name = 'dashboard/time_based.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = 90

        context['daily_traffic_json'] = json.dumps(TrafficAnalyticsService.get_daily_traffic(days))
        context['weekly_traffic_json'] = json.dumps(TrafficAnalyticsService.get_weekly_traffic(days))
        context['monthly_traffic_json'] = json.dumps(TrafficAnalyticsService.get_monthly_traffic(days))
        context['peak_hours_json'] = json.dumps(TrafficAnalyticsService.get_peak_hours(days))
        context['peak_days_json'] = json.dumps(TrafficAnalyticsService.get_peak_days(days))

        return context
