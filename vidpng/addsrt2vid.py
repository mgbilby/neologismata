#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def create_srt_filter(subtitle_path):
    """
    Create subtitle filter string. 
    Alignment 2 is bottom-center. MarginV controls height from bottom.
    """
    # FFmpeg requires escaping colons in paths for the subtitles filter
    path_str = str(subtitle_path).replace(':', '\\:')
    return (
        f"subtitles='{path_str}':"
        f"force_style='FontName=Arial,FontSize=18,PrimaryColour=&HFFFFFF,"
        f"Alignment=2,MarginV=20,OutlineWeight=1,Shadow=1'"
    )

def add_subtitles_to_video(video_path, subtitle_path, output_path):
    """
    Takes an existing video and 'burns in' subtitles from an SRT file.
    """
    if not subtitle_path.exists():
        print(f"Error: Subtitle file not found at {subtitle_path}")
        sys.exit(1)

    # Determine hardware acceleration/encoder based on OS
    video_encoder = "h264_videotoolbox" if sys.platform == "darwin" else "libx264"
    
    # Build the FFmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),          # Single input: The video file
        "-vf", create_srt_filter(subtitle_path), # Apply subtitle filter
        "-c:v", video_encoder,          # Re-encode video to burn in text
        "-b:v", "5M",                   # High quality bitrate
        "-c:a", "copy",                 # Copy original audio (no re-encoding)
        str(output_path)
    ]

    print(f"Processing: {video_path.name}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"\nFFmpeg Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_video.mp4|.mov> <subtitles.srt> <output.mp4>")
        sys.exit(1)

    video_in = Path(sys.argv[1])
    subs_in = Path(sys.argv[2])
    video_out = Path(sys.argv[3])

    if not video_in.exists():
        print(f"Error: Video file not found: {video_in}")
        sys.exit(1)

    add_subtitles_to_video(video_in, subs_in, video_out)