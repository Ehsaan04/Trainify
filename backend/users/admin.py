from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser,
    TrainerProfile,
    ClientProfile,
    MealPlan,
    WorkoutPlan,
    WorkoutPlanDay,
    Appointment,
    PTRequest,
    Leaderboard,
    WeightProgress,
    WorkoutPlanRating,
    Season,
    SavedWorkout
)

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_trainer', 'is_client', 'is_staff')
    list_filter = ('is_trainer', 'is_client', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type', {'fields': ('is_trainer', 'is_client')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_trainer', 'is_client')}
         ),
    )

# TrainerProfile admin
@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age_display', 'date_of_birth', 'goal', 'trainer', 'dietary_preference', 'priority_muscles_display')
    search_fields = ('user__username', 'user__email', 'trainer__username')
    raw_id_fields = ('user', 'trainer')

    def age_display(self, obj):
        return obj.age
    age_display.short_description = 'Age'

    def priority_muscles_display(self, obj):
        return ", ".join(obj.priority_muscles) if obj.priority_muscles else "None"
    priority_muscles_display.short_description = 'Priority Muscles'

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('client', 'meal_number', 'food_name', 'calories', 'protein', 'carbs', 'fats')
    list_filter = ('meal_number',)
    search_fields = ('client__user__username', 'food_name')

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('client', 'training_frequency', 'created_at')
    search_fields = ('client__user__username',)

@admin.register(WorkoutPlanDay)
class WorkoutPlanDayAdmin(admin.ModelAdmin):
    list_display = ('workout_plan', 'day_number')
    raw_id_fields = ('workout_plan',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'client', 'start', 'end')
    search_fields = ('trainer__user__username', 'client__user__username')

@admin.register(PTRequest)
class PTRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'trainer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('client__user__username', 'trainer__user__username')

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('client', 'trainer', 'points', 'updated_at')
    search_fields = ('client__user__username', 'trainer__user__username')

@admin.register(WeightProgress)
class WeightProgressAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'weight')
    search_fields = ('client__user__username',)

@admin.register(WorkoutPlanRating)
class WorkoutPlanRatingAdmin(admin.ModelAdmin):
    list_display = ('client', 'workout_plan', 'rating', 'workout_name')
    list_filter = ('rating',)
    search_fields = ('client__user__username', 'workout_plan__id')

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'trainer__user__username')
    ordering = ('-start_date',)

@admin.register(SavedWorkout)
class SavedWorkoutAdmin(admin.ModelAdmin):
    list_display = ('client', 'workout_plan', 'saved_at')
    search_fields = ('client__user__username', 'workout_plan__id')
    list_filter = ('saved_at',)
