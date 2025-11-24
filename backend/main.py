from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
from typing import Optional, List
import io

# Initialize FastAPI app
app = FastAPI(title="Poster & Moodboard Generator API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
UPLOAD_DIR = "uploads"
BACKGROUND_DIR = "backgrounds"
OUTPUT_DIR = "outputs"

for directory in [UPLOAD_DIR, BACKGROUND_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)


# ============= UTILITY FUNCTIONS =============

def get_font(size: int):
    """
    Try to load a nice font, fallback to default if not available
    """
    try:
        # Try common font paths (works on most systems)
        return ImageFont.truetype("arial.ttf", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            # Fallback to default font
            return ImageFont.load_default()


def wrap_text(text: str, font, max_width: int):
    """
    Wraps text to fit within max_width
    Returns list of lines
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def add_text_to_image(
    image: Image.Image,
    text: str,
    font_size: int,
    color: str,
    alignment: str,
    orientation: str
):
    """
    Overlays text on an image with specified styling
    """
    # Rotate image if vertical orientation
    if orientation.lower() == "vertical":
        image = image.rotate(90, expand=True)
    
    draw = ImageDraw.Draw(image)
    font = get_font(font_size)
    
    # Calculate text wrapping
    max_width = int(image.width * 0.8)  # 80% of image width
    lines = wrap_text(text, font, max_width)
    
    # Calculate total text height
    line_heights = []
    for line in lines:
        bbox = font.getbbox(line)
        line_heights.append(bbox[3] - bbox[1])
    
    total_height = sum(line_heights) + (len(lines) - 1) * 10  # 10px line spacing
    
    # Starting Y position (centered vertically)
    y = (image.height - total_height) // 2
    
    # Draw each line
    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        
        # Calculate X position based on alignment
        if alignment.lower() == "center":
            x = (image.width - text_width) // 2
        elif alignment.lower() == "right":
            x = image.width - text_width - 50
        else:  # left
            x = 50
        
        # Draw text with shadow for better visibility
        draw.text((x + 2, y + 2), line, font=font, fill="black")  # Shadow
        draw.text((x, y), line, font=font, fill=color)  # Main text
        
        y += bbox[3] - bbox[1] + 10  # Move to next line
    
    return image


# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Poster & Moodboard Generator API",
        "status": "running",
        "endpoints": [
            "/generate-quote-poster",
            "/generate-moodboard",
            "/upload-background"
        ]
    }


@app.post("/upload-background")
async def upload_background(file: UploadFile = File(...)):
    """
    Upload a background image to be used later
    Returns the filename for reference
    """
    try:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(BACKGROUND_DIR, filename)
        
        # Save uploaded file
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "success": True,
            "filename": filename,
            "message": "Background uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-quote-poster")
async def generate_quote_poster(
    text: str = Form(...),
    font_size: int = Form(50),
    color: str = Form("#FFFFFF"),
    alignment: str = Form("center"),
    orientation: str = Form("horizontal"),
    background_file: Optional[UploadFile] = File(None),
    existing_background: Optional[str] = Form(None)
):
    """
    Generate a quote poster with text overlay
    
    Parameters:
    - text: The quote text to overlay
    - font_size: Size of the font (default: 50)
    - color: Text color in hex format (default: white)
    - alignment: left, center, or right
    - orientation: horizontal or vertical
    - background_file: Upload new background image
    - existing_background: Use existing background filename
    """
    try:
        # Load or create background image
        if background_file:
            # Use uploaded background
            image_bytes = await background_file.read()
            background = Image.open(io.BytesIO(image_bytes))
        elif existing_background:
            # Use existing background
            bg_path = os.path.join(BACKGROUND_DIR, existing_background)
            if not os.path.exists(bg_path):
                raise HTTPException(status_code=404, detail="Background not found")
            background = Image.open(bg_path)
        else:
            # Create a default gradient background
            background = Image.new('RGB', (1200, 800), color=(100, 100, 200))
        
        # Convert to RGB if needed
        if background.mode != 'RGB':
            background = background.convert('RGB')
        
        # Resize if too large
        max_size = (1920, 1080)
        background.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Add text overlay
        result_image = add_text_to_image(
            background, text, font_size, color, alignment, orientation
        )
        
        # Save output
        output_filename = f"quote_{uuid.uuid4()}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        result_image.save(output_path, quality=95)
        
        return {
            "success": True,
            "filename": output_filename,
            "download_url": f"/download/{output_filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating poster: {str(e)}")


@app.post("/generate-moodboard")
async def generate_moodboard(
    layout: str = Form(...),  # "4x4", "8-grid", "16-grid", etc.
    files: List[UploadFile] = File(...),
):
    """
    Generate a moodboard/vision board with multiple images
    
    Parameters:
    - layout: Grid layout (4x4, 8-grid, 16-grid, custom layouts)
    - files: List of images to include in moodboard
    """
    try:
        # Define layout configurations
        layout_configs = {
            "4x4": (2, 2, 1920, 1920),           # 2x2 grid, square
            "8-grid": (2, 4, 1920, 3840),        # 2x4 grid
            "16-grid": (4, 4, 1920, 1920),       # 4x4 grid
            "portrait-8": (2, 4, 1080, 1920),    # Portrait 2x4
            "portrait-16": (4, 4, 1080, 1920),   # Portrait 4x4
        }
        
        if layout not in layout_configs:
            raise HTTPException(status_code=400, detail="Invalid layout")
        
        cols, rows, canvas_width, canvas_height = layout_configs[layout]
        
        # Create blank canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        # Calculate cell dimensions
        cell_width = canvas_width // cols
        cell_height = canvas_height // rows
        
        # Process each uploaded image
        for idx, file in enumerate(files):
            if idx >= (cols * rows):
                break  # Don't exceed grid capacity
            
            # Calculate position in grid
            row = idx // cols
            col = idx % cols
            x = col * cell_width
            y = row * cell_height
            
            # Load and resize image to fit cell
            image_bytes = await file.read()
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to fit cell (crop to fit)
            img = img.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
            
            # Paste onto canvas
            canvas.paste(img, (x, y))
        
        # Save moodboard
        output_filename = f"moodboard_{uuid.uuid4()}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        canvas.save(output_path, quality=95)
        
        return {
            "success": True,
            "filename": output_filename,
            "download_url": f"/download/{output_filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating moodboard: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download generated poster/moodboard
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="image/png", filename=filename)


@app.get("/backgrounds")
async def list_backgrounds():
    """
    List all available background images
    """
    try:
        backgrounds = os.listdir(BACKGROUND_DIR)
        return {
            "success": True,
            "backgrounds": backgrounds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn main:app --reload