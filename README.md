RVOS - Referring Video Object Segmentation
Find and highlight anything in a video just by typing what you're looking for.

1. What is this?
Ever wanted to automatically highlight a specific person, car, or object throughout a video? RVOS makes it easy.

You just upload a video, type a simple description like "the person in the red shirt" or "the black dog", and RVOS will process the video and create a new one with that object highlighted for you. It's a simple web app that combines the power of natural language with computer vision.

2. Features
Segment with Words: Simply describe the object you want to find in plain English.
Simple Web Interface: No command line needed. A clean interface for uploading videos and seeing the results.
Process in the Background: Upload your video and let the app work its magic. You can track the progress.
GPU Accelerated: Automatically uses your GPU if you have one (NVIDIA CUDA) for a 3-5x speed boost, but falls back to your CPU if not.
Download or Stream: Once it's done, you can download the final video or stream it directly in your browser.

3.  Getting Started (Quick Start)
Ready to try it out? Here’s how to get it running in a few steps.

Clone the project: 
git clone https://github.com/Ghulamhai/RVOS-Referring-Video-Object-Segmentation.git
cd RVOS-Referring-Video-Object-Segmentation-
Set up a virtual environment (recommended)

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
Install the dependencies

Bash

pip install flask torch torchvision transformers opencv-python Pillow numpy werkzeug
Note: This might take a few minutes, especially for PyTorch.

Create the necessary folders

# For macOS/Linux
mkdir -p backend/uploads backend/results

# For Windows, you can create these folders manually inside the `backend` directory.
Run the app!

cd backend
python app.py
You should see a message that the server is running on http://localhost:5001.

4. How to Use
Open your web browser and go to http://localhost:5001.

Click "Choose File" to upload a video.
In the text box, describe the object you want to find (e.g., "a blue car", "a woman walking", "the soccer ball").
Hit Submit and wait for the processing to finish.
Once it's done, you can view or download your new video!

Example Prompts
"a person"
"red car"
"dog walking on the grass"
"the man wearing a hat"
5.  Technology Stack
Backend: Flask (Python)

AI/ML: CLIPSeg from Hugging Face 
Computer Vision: OpenCV
Deep Learning: PyTorch
Frontend: Plain HTML & JavaScript

6. Configuration
Want to tweak the results? You can edit the scripts/mask.py file to change how the highlight looks.

threshold: How sensitive the detection is. (Default: 0.35)

overlay_color: The color of the highlight. (Default: Green)

alpha: How transparent the highlight is. (Default: 0.4)

7. Troubleshooting
"CUDA out of memory" error?
This means your GPU ran out of memory. Try using a lower-resolution video. The app will automatically use your CPU if it can't use the GPU.

Model download is slow or fails?
The first time you run the app, it needs to download the pre-trained AI model (~600MB). Make sure you have a stable internet connection. It will be cached for all future runs!

Video processing fails?
Make sure your video format is compatible (MP4 is best) and that you have enough disk space in the backend/uploads and backend/results folders.


8. Acknowledgments
This project wouldn't be possible without the amazing work from:
The CLIPSeg team for their incredible segmentation model.
Hugging Face for making these models so accessible.
