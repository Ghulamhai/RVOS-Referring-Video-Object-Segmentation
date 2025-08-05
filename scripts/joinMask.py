import cv2
import os
import argparse

def create_video_from_frames(input_dir, output_video, fps=30):
    image_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
    
    if not image_files:
        raise ValueError("No image files found in the directory.")
    
    first_image_path = os.path.join(input_dir, image_files[0])
    first_image = cv2.imread(first_image_path)
    height, width, _ = first_image.shape
    
    fourcc =cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    for image_file in image_files:
        image_path =os.path.join(input_dir, image_file)
        frame = cv2.imread(image_path)
        out.write(frame)
    
    out.release()
    print(f"Video saved as {output_video}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create video from segmented frames')
    parser.add_argument('--input_dir', type=str, required=True, help = 'Directory containing segmented frames')
    parser.add_argument('--output_video',type=str, required=True, help='Path to save the output video')
    parser.add_argument('--fps', type=int, default=30, help= 'Frames per second for the output video')
    
    args = parser.parse_args()
    create_video_from_frames(args.input_dir, args.output_video, args.fps)
