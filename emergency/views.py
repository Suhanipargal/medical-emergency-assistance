from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .models import UserProfile
import json
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
from django.http import HttpResponseBadRequest

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        is_volunteer = request.POST.get('is_volunteer') == 'on'

        if pass1 != pass2:
            return HttpResponse("Passwords do not match!")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            UserProfile.objects.create(user=my_user, is_volunteer=is_volunteer)
            return redirect('login')

    return render(request, 'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        location = request.POST.get('location')  
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            # Update user profile with location
            profile = UserProfile.objects.get(user=user)
            profile.location = location
            profile.save()
            return redirect('home')
        else:
            return HttpResponse("Username or Password is incorrect!")

    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@login_required
def HelpMapPage(request):
    # Fetch the current user's location
    user_profile = UserProfile.objects.get(user=request.user)
    user_location = user_profile.location

    # Fetch all volunteer locations (excluding the current user if they are also a volunteer)
    volunteers = UserProfile.objects.filter(is_volunteer=True).exclude(user=request.user)

    volunteer_locations = []
    for volunteer in volunteers:
        location = volunteer.location
        if location:
            lat, lng = map(float, location.split(','))
            volunteer_locations.append({
                'name': volunteer.user.username,
                'latitude': lat,
                'longitude': lng
            })

    # Print volunteer locations to debug if they are fetched correctly
    print("Volunteers:", volunteer_locations)

    # Pass the user's location and volunteers' locations to the template
    context = {
    'user_latitude': user_location.split(',')[0] ,
    'user_longitude': user_location.split(',')[1] ,
    'volunteers': json.dumps(volunteer_locations)  # Convert to JSON string
}
    print("contextttttttttttttttttttttttt:",context)
    return render(request, 'help_map.html', context)

@csrf_exempt
def emergency(request):
    if request.method == 'GET':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            print("message",message)
            # Broadcast the message to all WebSocket clients
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'alerts_group',
                {
                    'type': 'send_alert',
                    'message': message
                }
            )
            return JsonResponse({'status': 'alert sent'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def provide_help(request):
    # Check if the logged-in user is a volunteer
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.is_volunteer:
            # Redirect the user if they are not a volunteer
            return redirect('home')
    except UserProfile.DoesNotExist:
        # Redirect if the user profile doesn't exist
        return redirect('home')

    # Extract latitude and longitude from the location field
    if user_profile.location:
        latitude, longitude = map(float, user_profile.location.split(','))
    else:
        # Handle the case where location is not available
        latitude, longitude = 0, 0

    # Pass any required information to the template
    return render(request, 'provide_help.html', {
        'volunteer_latitude': latitude,
        'volunteer_longitude': longitude
    })
@login_required
def show_route(request):
    try:
        # Extract parameters
        if request.method =='GET':
            print("fuck off")
            lat = float(request.GET.get('lat', ''))
            lng = float(request.GET.get('lng', ''))
            vol_lat = float(request.GET.get('vol_lat', ''))
            vol_lng = float(request.GET.get('vol_lng', ''))
            print(lat,lng,vol_lat,vol_lng)
    except IndexError:
        return HttpResponseBadRequest("Invalid location parameters")

    # Prepare the URL for Google Maps Directions API




    directions_url = (
        f'https://maps.googleapis.com/maps/api/directions/json?'
        f'origin={vol_lat},{vol_lng}&destination={lat},{lng}&key=AIzaSyChgkH33dCjI4JEWruw7exKq1-oTBQrb5E'
    )

    # Make the request to the Directions API
    response = requests.get(directions_url)
    
    if response.status_code == 200:
        directions_data = response.json()
        return render(request, 'show_route.html', {'directions_data': directions_data})
    else:
        return HttpResponseBadRequest("Failed to get directions")