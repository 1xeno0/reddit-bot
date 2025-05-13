import requests

response = requests.post("http://localhost:5000/generate_video", 
    json={"story_filename": "0_2025-01-21-04-21-.json", "video_filename": "video1.json"})

print(response.content)