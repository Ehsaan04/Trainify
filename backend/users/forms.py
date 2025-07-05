from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, ClientProfile, TrainerProfile

class ClientSignupForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=UserCreationForm.base_fields['password1'].help_text
    )

    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text=UserCreationForm.base_fields['password2'].help_text
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  
        required=True,
        help_text="Enter your date of birth."
    )

    gender = forms.ChoiceField(
        choices=ClientProfile.GENDER_CHOICES,
        required=True,
        help_text="Select your gender."
    )

    height = forms.FloatField(
        required=True,
        help_text="Enter your height in cm."
    )
    weight = forms.FloatField(
        required=True,
        help_text="Enter your weight in kg."
    )
    goal = forms.ChoiceField(
        choices=ClientProfile.WEIGHT_GOALS,
        required=True,
        help_text="Select your weight goal."
    )

    priority_muscles = forms.MultipleChoiceField(
        choices=ClientProfile.PRIORITY_MUSCLES_CHOICES,
        required=False,  
        widget=forms.CheckboxSelectMultiple,
        help_text="Select muscles you want to prioritize in your workouts."
    )

    activity_level = forms.ChoiceField(
        choices=ClientProfile.ACTIVITY_LEVELS,
        required=True,
        help_text="Select your activity level. This affects your workout and nutrition recommendations."
    )


    profile_picture = forms.ImageField(
        required=False,
        help_text="Upload a profile picture (optional)."
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username','email', 'password1', 'password2', 'date_of_birth','gender', 'height', 'weight', 'goal','priority_muscles','activity_level', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_client = True
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                height=self.cleaned_data['height'],
                weight=self.cleaned_data['weight'],
                goal=self.cleaned_data['goal'],
                priority_muscles=self.cleaned_data['priority_muscles'],
                activity_level=self.cleaned_data['activity_level'],
                profile_picture=self.cleaned_data.get('profile_picture')
            )
        return user

class TrainerSignupForm(UserCreationForm):
    bio = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Tell us about yourself (optional)."
    )
    profile_picture = forms.ImageField(
        required=False,
        help_text="Upload a profile picture (optional)."
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'bio', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        #User gets marked as a trainer
        user.is_trainer = True  
        if commit:
            user.save()
            #Corresponding TrainerProfile is created for user
            TrainerProfile.objects.create(
                user=user,
                bio=self.cleaned_data.get('bio'),
                profile_picture=self.cleaned_data.get('profile_picture')
            )
        return user
    
class CustomLoginForm(AuthenticationForm):
        username = forms.CharField(
            widget=forms.TextInput(attrs={
                'placeholder': 'Enter your username',
            }),
            required=True,
            max_length=150,
        )
        password = forms.CharField(
            widget=forms.PasswordInput(attrs={
                'placeholder': 'Enter your password',
            }),
            required=True,
        )