from pathlib import Path
import cv2
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from .forms import VideoUploadForm

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def features(request):
    return render(request, "features.html")

def upload(request):
    return render(request, "upload.html")

def logout(request):
    auth.logout(request)
    return redirect('index')

def register(request):
    if request.method == "POST":
        first = request.POST['fname']
        last = request.POST['lname']
        uname = request.POST['uname']
        email = request.POST['Email']
        p1 = request.POST['pass']
        p2 = request.POST['cpass']

        if p1 == p2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Exists")
            elif User.objects.filter(username=uname).exists():
                messages.info(request, "Username available")
            else:
                user = User.objects.create_user(first_name=first, last_name=last, username=uname, email=email, password=p1)
                user.save()
                return redirect('login')
        else:
            messages.info(request, "Password not matched")
        return render(request, "register.html")
    return render(request, "register.html")

def login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        ps = request.POST['pass']
        user = auth.authenticate(username=uname, password=ps)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, "Invalid Credentials")
    return render(request, "login.html")


import cv2
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from .forms import VideoUploadForm
from pathlib import Path
import subprocess  # For FFmpeg execution
import os

def convert_video_to_mp4(input_video_path):
    """
    Converts the uploaded video to .mp4 format using FFmpeg if it's not already .mp4.
    """
    output_video_path = str(input_video_path).replace(input_video_path.suffix, '.mp4')
    
    if input_video_path.suffix != '.mp4':
        try:
            # FFmpeg command to convert video
            command = [
                'ffmpeg', '-i', str(input_video_path), 
                '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', 
                str(output_video_path)
            ]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in video conversion: {e}")
            raise ValueError("Video conversion failed. Please ensure the file is valid.")
    
    return Path(output_video_path)

import cv2
import dlib
import time
import math
import uuid  # Add this import at the beginning of your file
from django.conf import settings
from pathlib import Path
import os

# Set up video capture and Haar cascade
cascade_path = r'C:\Users\ADMIN\Desktop\Final\vehicle_speed_detection\haarCascade_cars.xml'

# Check if the cascade file exists
if not os.path.exists(cascade_path):
    raise FileNotFoundError(f"Cascade file not found: {cascade_path}")

carCascade = cv2.CascadeClassifier(cascade_path)

if carCascade.empty():
    raise ValueError("Failed to load cascade classifier.")

WIDTH = 1280
HEIGHT = 720

def estimate_speed(location1, location2):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    ppm = 8.8  # Pixels per meter
    d_meters = d_pixels / ppm
    fps = 18
    speed = d_meters * fps * 3.6  # Convert m/s to km/h
    speed=speed-40
    if(speed<5):
        speed=speed+40
    return speed

def process_video(full_video_path):
    cap = cv2.VideoCapture(str(full_video_path))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    currentCarID = 0
    carTracker = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000
    
    output_path = Path(settings.MEDIA_ROOT) / 'processed_video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, frame_rate, (WIDTH, HEIGHT))
    
    frameCounter = 0
    speed_limit = 60  # Define the speed limit (in km/h)
    unique_over_limit_vehicles = {}  # Dictionary to track unique over-speeding vehicles

    while cap.isOpened():
        ret, image = cap.read()
        if not ret:
            break

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        frameCounter += 1

        # Update trackers
        carIDtoDelete = []
        for carID in carTracker.keys():
            trackingQuality = carTracker[carID].update(image)
            if trackingQuality < 7:
                carIDtoDelete.append(carID)

        for carID in carIDtoDelete:
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        # Detect vehicles every 5 frames
        if frameCounter % 5 == 0:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for (_x, _y, _w, _h) in cars:
                x, y, w, h = int(_x), int(_y), int(_w), int(_h)
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                matchCarID = None

                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()
                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and
                        (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID

                if matchCarID is None:
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]
                    currentCarID += 1

        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()
            t_x, t_y, t_w, t_h = int(trackedPosition.left()), int(trackedPosition.top()), int(trackedPosition.width()), int(trackedPosition.height())
            carLocation2[carID] = [t_x, t_y, t_w, t_h]
            
            color = (0, 255, 0)  # Default color green
            [x1, y1, w1, h1] = carLocation1[carID]
            [x2, y2, w2, h2] = carLocation2[carID]
            carLocation1[carID] = [x2, y2, w2, h2]

            if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                if (speed[carID] is None or speed[carID] == 0) and y1 >= 275 and y1 <= 285:
                    speed[carID] = estimate_speed([x1, y1, w1, h1], [x2, y2, w2, h2])

                if speed[carID] is not None and speed[carID] > speed_limit:
                    color = (0, 0, 255)  # Red for vehicles exceeding the speed limit
                    if carID not in unique_over_limit_vehicles:  # Check if vehicle already recorded
                        unique_over_limit_vehicles[carID] = int(speed[carID])
                    
                    cv2.putText(resultImage, f"{int(speed[carID])} km/h (Over Limit)", 
                                (int(x1 + w1 / 2), int(y1 - 5)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                elif speed[carID] is not None:
                    cv2.putText(resultImage, f"{int(speed[carID])} km/h", 
                                (int(x1 + w1 / 2), int(y1 - 5)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), color, 4)
        out.write(resultImage)

    cap.release()
    out.release()
    return output_path, unique_over_limit_vehicles


def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data['video']
            unique_video_name = f"{Path(video.name).stem}_{uuid.uuid4().hex}{Path(video.name).suffix}"
            video_path = default_storage.save(unique_video_name, video)
            full_video_path = Path(settings.MEDIA_ROOT) / video_path
            
            try:
                processed_video_path, unique_over_limit_vehicles = process_video(full_video_path)
            except Exception as e:
                return render(request, 'upload_error.html', {'error': str(e)})

            try:
                h264_video_path = convert_video_to_h264(processed_video_path)
            except subprocess.CalledProcessError as e:
                return render(request, 'upload_error.html', {'error': 'Video conversion failed: ' + str(e)})

            video_url = f"{settings.MEDIA_URL}{os.path.basename(video_path)}"
            h264_video_url = f"{settings.MEDIA_URL}{os.path.basename(h264_video_path)}"
            
            return render(request, 'upload_success.html', {
                'video_path': video_url,
                'processed_video_path': h264_video_url,
                'over_limit_vehicles': unique_over_limit_vehicles.items()  # Pass unique vehicles and their speeds
            })
    else:
        form = VideoUploadForm()

    return render(request, 'upload.html', {'form': form})




def convert_video_to_h264(input_video_path):
    """
    Converts the video to H.264 format using FFmpeg.
    """
    unique_filename = f"{input_video_path.stem}_{uuid.uuid4().hex}.mp4"
    output_video_path = input_video_path.with_name(unique_filename)
    
    command = [
        'ffmpeg', '-i', str(input_video_path),
        '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
        str(output_video_path)
    ]

    subprocess.run(command, check=True)
    
    return output_video_path

