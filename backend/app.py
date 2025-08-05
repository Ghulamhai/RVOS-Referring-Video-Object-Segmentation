from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import subprocess
import uuid
import shutil
import time
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configure folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
SCRIPTS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'scripts')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Store job statuses
job_statuses = {}

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}),400
    
    video_file = request.files['video']
    text_prompt =request.form.get('prompt', 'a person')
    
    if video_file.filename == '':
        return jsonify({'error': 'No video selected'}), 400
    
    # Create unique ID for this processing job
    job_id = str(uuid.uuid4())
    job_folder = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_folder, exist_ok=True)
    
    # Save the uploaded video
    video_filename = secure_filename(video_file.filename)
    video_path = os.path.join(job_folder, video_filename)
    video_file.save(video_path)
    
    # Update job status
    job_statuses[job_id] = {
        'status': 'processing',
        'start_time': time.time(),
        'video_name': video_filename,
        'prompt': text_prompt
    }
    
    # Start processing in a separate thread
    thread = threading.Thread(target=process_video, args=(job_id, video_path, text_prompt))
    thread.daemon = True
    thread.start()
    
    #Return job ID immediately
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'Video processing started'
    })

def process_video(job_id, video_path, text_prompt):
    job_folder = os.path.join(UPLOAD_FOLDER, job_id)
    frames_folder = os.path.join(job_folder,"segmentedFrames1")
    output_folder =os.path.join(job_folder, "segmentedFrames")
    output_video = os.path.join(RESULTS_FOLDER, f"{job_id}.mp4")
    
    os.makedirs(frames_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Run frame extraction
        segment_script = os.path.join(SCRIPTS_FOLDER, "segment.py")
        subprocess.run([
            'python', segment_script,
            '--video_path', video_path,
            '--output_folder',frames_folder
        ], check=True)
        
        # Run segmentation
        mask_script = os.path.join(SCRIPTS_FOLDER, "mask.py")
        subprocess.run([
            'python',mask_script,
            '--input_dir', frames_folder,
            '--output_dir', output_folder,
            '--text_prompt', text_prompt
        ], check=True)
        
        # Create output video
        join_script = os.path.join(SCRIPTS_FOLDER, "joinMask.py")
        subprocess.run([
            'python', join_script,
            '--input_dir', output_folder,
            '--output_video', output_video
        ], check=True)
        
        # Update job status to completed
        job_statuses[job_id]['status'] = 'completed'
        job_statuses[job_id]['end_time'] = time.time()
        job_statuses[job_id]['output_path'] = output_video
        job_statuses[job_id]['output_filename'] = f"{job_id}.mp4"  # Store the filename
        
    except Exception as e:
        # Update job status to failed
        job_statuses[job_id]['status'] ='failed'
        job_statuses[job_id]['error'] = str(e)
        print(f"Error processing job {job_id}: {str(e)}")

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    if job_id not in job_statuses:
        return jsonify({'error': 'Job not found'}), 404
    
    status = job_statuses[job_id]['status']
    response = {'status': status}
    
    if status =='completed':
        response['video_url'] = f"/video/{job_statuses[job_id]['output_filename']}"
    elif status == 'failed' and 'error' in job_statuses[job_id]:
        response['error'] = job_statuses[job_id]['error']
    
    return jsonify(response)

# New route to serve videos directly from the results folder
@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(RESULTS_FOLDER, filename,mimetype='video/mp4')

@app.route('/api/video/<job_id>', methods=['GET'])
def get_video(job_id):
    if job_id not in job_statuses or job_statuses[job_id]['status'] != 'completed':
        return jsonify({'error': 'Video not ready or not found'}), 404
    
    video_path = job_statuses[job_id]['output_path']
    return send_file(video_path, mimetype='video/mp4')

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    if job_id not in job_statuses or job_statuses[job_id]['status'] != 'completed':
        return jsonify({'error': 'Video not ready or not found'}), 404
    
    video_path = job_statuses[job_id]['output_path']
    original_filename =job_statuses[job_id][ 'video_name']
    return send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f"segmented_{original_filename}"
    )

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
