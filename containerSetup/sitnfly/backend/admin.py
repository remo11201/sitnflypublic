# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Reservation, Flight, Seat, Payment, SessionLog


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'date_of_birth', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'address', 'date_of_birth', 'phone_number','password1', 'password2', 'role'),
        }),
    )
    list_display = ('email','date_joined', 'last_login','name','address','date_of_birth','phone_number', 'is_staff', 'role')
    search_fields = ('email', 'name', 'username', 'role')
    ordering = ('email',)

    def save_model(self, request, obj, form, change):
        if obj.role == 'Administrator':
            obj.is_staff = True
            obj.is_superuser = True
        super().save_model(request, obj, form, change)


    def delete_model(self, request, obj):
        super().delete_model(request, obj)


admin.site.register(User, CustomUserAdmin)



class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'reservation_status', 'booking_date', 'payment_status', 'user', 'flight')
    search_fields = ('reservation_id', 'user__email', 'flight__flight_number')
    list_filter = ('reservation_status', 'payment_status')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = 'Updated' if change else 'Created'

    def delete_model(self, request, obj):
        super().delete_model(request, obj)


class FlightAdmin(admin.ModelAdmin):
    list_display = (
    'flight_id', 'flight_number', 'departure_time', 'arrival_time', 'origin', 'destination', 'airline_name')
    search_fields = ('flight_number', 'origin', 'destination')
    list_filter = ('origin', 'destination', 'airline_name')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)


class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_id', 'seat_no', 'seat_class', 'availability', 'flight','price')
    search_fields = ('seat_no', 'seat_class', 'flight__flight_number')
    list_filter = ('seat_class', 'availability')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'payment_amount', 'payment_date', 'payment_method', 'reservation')
    search_fields = ('payment_id', 'reservation__reservation_id')
    list_filter = ('payment_date', 'payment_method')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'session_key', 'ip_address', 'user_agent', 'login_time', 'logout_time','created_at', 'is_active')
    search_fields = ('session_id', 'user__email', 'session_key', 'ip_address')
    list_filter = ('is_active', 'login_time', 'logout_time')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(SessionLog, SessionLogAdmin)

