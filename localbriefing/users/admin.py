from django.contrib import admin
from .models import Location, User, RawData, Briefing, DistrictAnnouncement, RestaurantInfo

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['gu', 'gu_code', 'created_at']
    search_fields = ['gu']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'location', 'is_active', 'date_joined']
    list_filter = ['location', 'is_active']
    search_fields = ['username', 'email']

@admin.register(RawData)
class RawDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'category', 'title', 'processed', 'collected_at']
    list_filter = ['category', 'processed', 'location']
    search_fields = ['title', 'content']

@admin.register(Briefing)
class BriefingAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'date', 'status', 'created_at']
    list_filter = ['status', 'location', 'date']
    search_fields = ['user__username']

@admin.register(DistrictAnnouncement)
class DistrictAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['location', 'title', 'board_type', 'view_count', 'created_at']
    list_filter = ['location', 'board_type']
    search_fields = ['title', 'content']

@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'business_type', 'location', 'business_status_name']
    list_filter = ['business_type', 'location', 'business_status_name']
    search_fields = ['business_name', 'road_address']
