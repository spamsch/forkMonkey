#!/usr/bin/env python3
"""
GIF Assembly Script for Fork Monkey (Fixed Version)
Converts generated PNG frames into animated GIFs with proper transparency
Matches VS Code Pets quality standards
"""

import os
from PIL import Image
import glob

# Configuration
FRAMES_DIR = "/home/ubuntu/forkmonkey-assets/frames"
GIFS_DIR = "/home/ubuntu/forkmonkey-assets/gifs"
TARGET_SIZE = (111, 101)  # VS Code Pets standard size
FPS = 4  # VS Code Pets uses 4 FPS (not 8!)
FRAME_DURATION = int(1000 / FPS)  # 250ms per frame
COLOR = "brown"  # Fork monkey color variant

# Animation definitions
ANIMATIONS = {
    'idle': 4,
    'walk': 6,
    'run': 8,
    'swipe': 5,
    'with_ball': 4
}

def process_frame_for_gif(image_path, target_size):
    """
    Process a single frame with proper transparency handling
    """
    print(f"    Processing: {os.path.basename(image_path)}")
    
    # Load image
    img = Image.open(image_path)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get the bounding box of non-transparent pixels
    # This helps us crop to actual content
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    # Calculate scaling to fit within target size while maintaining aspect ratio
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Create a new transparent image of exact target size
    final_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
    
    # Calculate position to center the image
    x = (target_size[0] - img.width) // 2
    y = (target_size[1] - img.height) // 2
    
    # Paste the image onto the transparent background
    final_img.paste(img, (x, y), img)
    
    return final_img

def create_gif_with_transparency(animation_name, frame_count, output_path):
    """
    Create an animated GIF with proper transparency handling
    Uses the same method as VS Code Pets
    """
    print(f"\n🎬 Creating {animation_name} animation...")
    print(f"   Frames: {frame_count}")
    
    # Find all frames for this animation
    frame_files = []
    for i in range(1, frame_count + 1):
        frame_path = os.path.join(FRAMES_DIR, f"{animation_name}_frame_{i:02d}.png")
        if os.path.exists(frame_path):
            frame_files.append(frame_path)
        else:
            print(f"   ⚠️  Warning: Frame {i} not found")
    
    if not frame_files:
        print(f"   ❌ No frames found for {animation_name}")
        return False
    
    print(f"   Found {len(frame_files)} frames")
    
    # Process all frames
    frames = []
    for frame_file in frame_files:
        frame = process_frame_for_gif(frame_file, TARGET_SIZE)
        frames.append(frame)
    
    # Save as animated GIF with proper settings
    print(f"   💾 Saving to: {output_path}")
    
    # Save with transparency
    # Use 'P' mode (palette) with transparency
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,  # 250ms per frame (4 FPS)
        loop=0,  # Loop forever
        disposal=2,  # Restore to background (important for transparency!)
        optimize=True,  # Optimize palette
        transparency=0,  # First color in palette is transparent
        background=0  # Background color index
    )
    
    # Get file size
    file_size = os.path.getsize(output_path)
    print(f"   ✅ Created! Size: {file_size / 1024:.1f} KB")
    
    # Verify dimensions
    with Image.open(output_path) as verify_img:
        print(f"   📏 Verified: {verify_img.size[0]}x{verify_img.size[1]}")
    
    return True

def main():
    print("="*60)
    print("🎞️  FORK MONKEY GIF ASSEMBLY (FIXED VERSION)")
    print("="*60)
    print(f"Target: {TARGET_SIZE[0]}x{TARGET_SIZE[1]} @ {FPS} FPS")
    print(f"Frame duration: {FRAME_DURATION}ms")
    print()
    
    # Create output directory
    os.makedirs(GIFS_DIR, exist_ok=True)
    print(f"📁 Output directory: {GIFS_DIR}")
    
    # Process each animation
    success_count = 0
    for anim_name, frame_count in ANIMATIONS.items():
        output_filename = f"{COLOR}_{anim_name}_8fps.gif"
        output_path = os.path.join(GIFS_DIR, output_filename)
        
        if create_gif_with_transparency(anim_name, frame_count, output_path):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"✅ COMPLETE! {success_count}/{len(ANIMATIONS)} animations created")
    print(f"📁 Output directory: {GIFS_DIR}")
    print("="*60)
    
    # List all created GIFs with details
    print("\n📋 Created GIFs:")
    total_size = 0
    for gif_file in sorted(glob.glob(os.path.join(GIFS_DIR, "*.gif"))):
        size = os.path.getsize(gif_file)
        total_size += size
        
        # Get frame count
        with Image.open(gif_file) as img:
            try:
                frame_count = 0
                while True:
                    frame_count += 1
                    img.seek(frame_count)
            except EOFError:
                pass
        
        print(f"   • {os.path.basename(gif_file)}: {size / 1024:.1f} KB ({frame_count} frames)")
    
    print(f"\n   Total size: {total_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
