import os
import torch
import numpy as np
from PIL import Image
from pathlib import Path
import argparse
from transformers import CLIPSegForImageSegmentation, AutoProcessor, AutoTokenizer

def get_available_device():
    """Automatically select available GPU or fallback to CPU"""
    if torch.cuda.is_available():
        try:
            # Get list of visible devices from environment
            visible_devices = list(map(int, os.environ.get("CUDA_VISIBLE_DEVICES", "0").split(',')))
            device_id = visible_devices[0] if visible_devices else 0
            device = f"cuda:{device_id}"
            
         # Test device availability
            _ = torch.tensor([1]).to(device)  # Simple test tensor
            print(f"Using GPU {device_id} ({torch.cuda.get_device_name(device_id)})")
            return torch.device(device)
        except Exception as e:
            print(f"GPU error: {str(e)}, falling back to CPU")
    return torch.device("cpu")

def process_images(
    input_dir,
    output_dir,
    text_prompt,
    threshold=0.35,
    overlay_color=(0, 255,0),
    alpha= 0.4
):
    device = get_available_device()
    
    # Load model components
    tokenizer = AutoTokenizer.from_pretrained("CIDAS/clipseg-rd64-refined")
    processor = AutoProcessor.from_pretrained("CIDAS/clipseg-rd64-refined", use_fast=True)
    model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined").to(device)

# Process all images
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for img_file in Path(input_dir).glob("*"):
        if img_file.suffix.lower() not in ['.jpg', '.jpeg','.png']:
            continue
            
        try:
            #Process image
            image = Image.open(img_file).convert("RGB")
            original_size = image.size

            # Prepare inputs
            text_inputs = tokenizer(
                text_prompt,
                padding= "max_length",
                max_length=77,
                truncation= True,
                return_tensors="pt"
            ).to(device)
            
            image_inputs =processor(
                images=image,
                return_tensors ="pt"
            ).to(device)

         ##Generate mask
            with torch.no_grad():
                outputs = model(
                    input_ids= text_inputs.input_ids,
                    attention_mask=text_inputs.attention_mask,
                    pixel_values= image_inputs.pixel_values
                )

            # Process mask
            mask = outputs.logits.squeeze()
            mask = torch.sigmoid(mask).cpu().numpy()
            mask_uint8 =(mask *255).astype(np.uint8)
            mask_pil = Image.fromarray(mask_uint8).resize(original_size)
            mask_resized =np.array(mask_pil)
            binary_mask = mask_resized > (threshold * 255)

            # Create overlay
            overlay = np.array(image.copy())
            overlay[binary_mask] = (overlay[binary_mask] *(1 -alpha) + 
                                   np.array(overlay_color) * alpha).astype(np.uint8)

            #Save result
            output_path =  Path(output_dir) / f"segmented_{img_file.name}"
            Image.fromarray(overlay).save(output_path)
            print(f"Processed {img_file.name} -> {output_path.name}")

        except Exception as e:
            print(f"Error processing {img_file.name}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Segment objects in images using text prompts')
    parser.add_argument('--input_dir', type=str, required=True, help= 'Directory containing input frames ')
    parser.add_argument('--output_dir',type=str, required=True,help='Directory to save segmented frames' )
    parser.add_argument('--text_prompt', type=str, required=True, help='Text description of object to segment')
    parser.add_argument('--threshold', type=float,default=0.35, help= 'Segmentation threshold(0-1)')
    
    args = parser.parse_args()
    
    process_images(
        input_dir= args.input_dir,
        output_dir= args.output_dir,
        text_prompt=args.text_prompt,
        threshold= args.threshold,
        overlay_color =(0,255, 0),
        alpha=0.4
    )
