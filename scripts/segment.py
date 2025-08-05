import cv2
import os
import argparse

def extract_frames(video_path, output_folder):
    # Create the folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Load the video
    cap = cv2.VideoCapture(video_path)
    
    ##Check if video loaded successfully
    if not cap.isOpened():
        print("Error: Unable to load the video. Check the path!")
        return False
    
    # Frame extraction loop
    frame_count =0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        #Generate frame file name
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        
    # Save the frame as an image
        cv2.imwrite(frame_filename,frame)
        
        frame_count += 1
    
    # Release video capture
    cap.release()
    print(f"{frame_count} frames have been generated and stored in '{output_folder}' folder.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract frames from a video file')
    parser.add_argument('--video_path', type=str, required=True , help='Path to the input video file')
    parser.add_argument('--output_folder', type=str,required=True, help='Folder to store extracted frames')
    
    args = parser.parse_args()
    extract_frames(args.video_path, args.output_folder)
