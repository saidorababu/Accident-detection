import cv2
import requests
import tkinter as tk
from tkinter import messagebox
import time
import numpy as np

#for current time
from datetime import datetime

#for SMS
from twilio.rest import Client

# Video capture
cap = cv2.VideoCapture('acc1.mp4')

# SMS SENDING CODE
# Replace these with your actual Twilio credentials
account_sid = 'AC380aa36dae5312520f308255945f2d5c'
auth_token = '7fc7124cce8319593b61362c51a19681'  # Replace with your actual auth token
twilio_phone_number = '+12056145127'  # Replace with your Twilio phone number

client = Client(account_sid, auth_token)


# Sentisight.ai API details
sentisight_token = "aftd1hqumrmpkaui6nafne4ee8"
project_id = "56828"
model_name = "accident-detection-model"
api_url = 'https://platform.sentisight.ai/api/predict/{}/{}/'.format(project_id, model_name)
headers = {"X-Auth-token": sentisight_token, "Content-Type": "application/octet-stream"}

foundAccident = False

# Function to show alert window
def show_alert_window(time_str):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Accident Detected", f"An accident has been detected!\nTime: {time_str}")

delay = 0
while(delay):
    _, img = cap.read()
    delay -= 1
c = 0
while True and not foundAccident:
    delay = 6
    while(delay):
        _, img = cap.read()
        delay -= 1
    if img is None:
        break
    # Send the frame to Sentisight.ai for accident detection
    _, encoded_frame = cv2.imencode('.jpg', img)  # Encode the frame as JPEG
    r = requests.post(api_url, headers=headers, data=encoded_frame.tobytes())

    if r.status_code == 200:
        result = r.json()
        print("API Response:", result)
        print(result[0].get('label'));
    
        # Check if 'accident' is present and greater than 50%
        if isinstance(result, list) and result and result[0].get('label') == 'vehicledamaged' and result[0].get('score') > 80:
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0))
            c+=1;
            if(c < 6):pass
            else:
                print(f"Accident Detected at {formatted_time} in the video! Showing Alert Window...")
                foundAccident = True
                show_alert_window(formatted_time)
                # Get the current time
                current_time = datetime.now().time()

                # Format and print the current time
                formatted_time = current_time.strftime("%H:%M:%S")
                print("Accident happend at :", formatted_time , " IST")
                
                message = client.messages.create(
                    from_=twilio_phone_number,
                    body='EMERGENCY : MAJOR ROAD ACCIDENT DETECTED at Camera ID: 1542 , NH652 , near Orion ,National Institute Of Technology, Tiruchirappalli at '+formatted_time,
                    to='+919515375670'  # Replace with the recipient's phone number
                )

                print(f"Message SID: {message.sid}")

    cv2.imshow('Image', img)
    key = cv2.waitKey(1)
    if key == 27 or cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()