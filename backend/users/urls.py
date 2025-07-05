from django.urls import path
from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/client/', views.client_signup, name='client_signup'),
    path('signup/trainer/', views.trainer_signup, name='trainer_signup'),
    path('logout/', views.logout_view, name='logout_view'),
    path('', views.home_page, name='home_page'),
    path('login/', CustomLoginView.as_view(), name='login_view'),
    path('api/getUserType', views.get_user_type, name='get_user_type'),
    path('api/getUserData', views.get_user_data, name='get_user_data'),
    path('api/updateWeight', views.update_weight, name='update_weight' ),
    path('api/getWeightProgress', views.get_weight_progress, name='get_weight_progress'),
    path('api/getClientWeightProgress/<int:client_id>/', views.get_client_weight_progress, name='get_client_weight_progress'),
    path('search_trainers/', views.search_trainers, name='search_trainers'),
    path('send_request/', views.send_request, name='send_request'),
    path('view_requests/', views.view_requests, name='view_requests'),
    path('respond_to_request/<int:request_id>/', views.respond_to_request, name='respond_to_request'),
    path('trainer/clients/', views.get_trainer_clients, name='trainer_clients'),
    path("get-client-saved-workouts/<int:client_id>/", views.get_client_saved_workouts, name="get_client_saved_workouts"),
    path("generate-meal-plan/<int:client_id>/", views.generate_meal_plan, name="generate_meal_plan"),
    path('regenerate-meal/<int:client_id>/<int:meal_number>/', views.regenerate_single_meal),
    path('get-saved-meal-plan/<int:client_id>/', views.get_saved_meal_plan, name='get_saved_meal_plan'),
    path('generate-workout-plan/<int:client_id>/', views.generate_workout_plan_view, name='generate_workout_plan'),
    path('save-workout-plan/<int:client_id>/', views.save_workout_plan, name='save_workout_plan'),
    path('get-saved-workout-plan/<int:client_id>/', views.get_saved_workout_plan, name='get-saved-workout-plan'),
    path('rate-workout-plan/', views.rate_workout_plan, name='rate_workout_plan'),
    path('get-workout-plan-rating/<int:plan_id>/', views.get_workout_plan_rating, name='get_workout_plan_rating'),
    path("get-recommended-workouts/", views.get_recommended_workouts, name="get_recommended_workouts"),
    path("save-recommended-workout/<int:plan_id>/", views.save_recommended_workout, name="save_recommended_workout"),
    path("get-saved-recommended-workouts/", views.get_saved_recommended_workouts, name="get_saved_recommended_workouts"),
    path("remove-saved-workout/<int:plan_id>/", views.remove_saved_workout, name="remove_saved_workout"),
    path("assign-saved-workout/<int:client_id>/<int:plan_id>/", views.assign_saved_workout, name="assign_saved_workout"),
    path("get-workout-plan-by-id/<int:plan_id>/", views.get_workout_plan_by_id, name="get-workout-plan-by-id"),
    path("create-season/", views.create_season, name="create_season"),
    path('assign-points/', views.assign_points, name='assign_points'),
    path('get-leaderboard/', views.get_leaderboard, name='get_leaderboard'),
    path('get-client-points/<int:client_id>/', views.get_client_points, name='get_client_points'),
    path('refresh-exercise/', views.refresh_exercise, name='refresh_exercise'),
    path('meal-plan-note/<int:client_id>/', views.get_meal_plan_note, name='get_meal_plan_note'),
    path('save-meal-plan-note/<int:client_id>/', views.save_meal_plan_note, name='save_meal_plan_note'),
    path('workout-plan-note/<int:client_id>/', views.get_workout_plan_note, name='get_workout_plan_note'),
    path('save-workout-plan-note/<int:client_id>/', views.save_workout_plan_note, name='save_workout_plan_note'),
    path('update-protein-multiplier/<int:client_id>/', views.update_protein_multiplier, name='update_protein_multiplier'),
    path('update-goal/<int:client_id>/', views.update_client_goal, name='update_client_goal'),
    path('unlink-client/<int:client_id>/', views.unlink_client, name='unlink-client'),









     

]
