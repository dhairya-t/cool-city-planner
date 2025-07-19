# FFmpeg Setup Guide for CoolCity Planner

## Why FFmpeg?
FFmpeg provides superior video quality and compression for converting satellite images to videos that TwelveLabs can analyze. While OpenCV fallback works, FFmpeg produces:
- Better video quality
- Smaller file sizes  
- Faster processing
- Better TwelveLabs compatibility

## Windows Installation

### Option 1: Download Pre-built Binary (Recommended)
1. Go to https://www.gyan.dev/ffmpeg/builds/
2. Download the **release** build (full)
3. Extract the ZIP file to `C:\ffmpeg`
4. Add `C:\ffmpeg\bin` to your Windows PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\ffmpeg\bin`
   - Click "OK" to save
5. Open a new Command Prompt and test: `ffmpeg -version`

### Option 2: Using Chocolatey
```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg
```

### Option 3: Using Scoop
```powershell
# Install Scoop first (if not installed)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install FFmpeg
scoop install ffmpeg
```

## macOS Installation
```bash
# Using Homebrew
brew install ffmpeg
```

## Linux Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## Verify Installation
After installation, verify FFmpeg is working:
```bash
ffmpeg -version
```

You should see version information and available codecs.

## Testing with CoolCity Planner
Run the video converter test to verify everything works:
```bash
cd backend
python test_video_converter.py
```

You should see "✅ FFmpeg detected on system" instead of the OpenCV fallback message.

## Benefits for TwelveLabs
With FFmpeg installed, your satellite image analysis will have:
- **Higher video quality**: Better compression maintains image details
- **Faster processing**: Optimized encoding reduces conversion time
- **Better compatibility**: Industry-standard formats work best with TwelveLabs
- **Smaller uploads**: Efficient compression reduces API transfer times

## Troubleshooting

### "FFmpeg not found" error
- Make sure FFmpeg is in your system PATH
- Restart your terminal/command prompt after installation
- Try running `ffmpeg -version` to verify installation

### Permission errors on Windows
- Run Command Prompt as Administrator when adding to PATH
- Make sure the FFmpeg folder has proper permissions

### Performance issues
- Use the default settings in the video converter
- For large images (>4K), consider resizing before conversion
- Monitor CPU usage during conversion

## Alternative: Docker Approach
If you prefer containerization:
```dockerfile
FROM python:3.11
RUN apt-get update && apt-get install -y ffmpeg
# ... rest of your Dockerfile
```

## Support
If you encounter issues:
1. Check the console output for specific error messages
2. Verify FFmpeg installation with `ffmpeg -version`
3. Run the video converter test script
4. The system will automatically fall back to OpenCV if needed
