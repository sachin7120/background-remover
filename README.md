# 🪄 Background Remover

An AI-powered image background remover built with **FastAPI, Python, rembg, ISNet, HTML, CSS, and JavaScript**.

Upload an image, automatically remove its background, compare the original and processed image with a live before/after slider, select processing quality, and download the result as a transparent PNG.

---

## ✨ Features

- 🖼️ Upload JPG, JPEG, PNG, and WEBP images
- 🤖 AI-powered background removal
- ⚡ Fast processing using `isnet-general-use`
- 🎚️ Three quality modes:
  - **Low** — fastest processing
  - **Standard** — balanced speed and quality
  - **High** — original-resolution processing
- 🔍 Live before/after comparison slider
- 📐 Preserves original image orientation
- 📏 Preserves original image dimensions
- 🧹 Automatic temporary-file cleanup
- 📥 Download processed image as PNG
- 🚫 Maximum upload size of 10 MB
- 🌐 Simple frontend with Poppins font
- 🔌 FastAPI REST API
- 📱 Responsive basic interface

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Poppins font

### Backend

- Python
- FastAPI
- Uvicorn
- rembg
- ONNX Runtime
- Pillow

### AI Model

The project currently uses:

```text
isnet-general-use


background-remover/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .venv/
│   └── uploads/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore
└── README.md


🚀 Getting Started
1. Clone the repository
git clone https://github.com/YOUR-USERNAME/background-remover.git

Enter the project folder:

cd background-remover
🐍 Backend Setup
2. Open the backend folder
cd backend
3. Create a virtual environment
Windows
python -m venv .venv

Activate it:

.venv\Scripts\activate
macOS / Linux
python3 -m venv .venv

Activate it:

source .venv/bin/activate
4. Install dependencies
pip install -r requirements.txt

If you are setting up the project for the first time and requirements.txt does not exist yet:

pip install fastapi uvicorn python-multipart pillow "rembg[cpu]"

Then:

pip freeze > requirements.txt
▶️ Start the Backend

From the backend directory:

python -m uvicorn main:app --reload

The API will run at:

http://127.0.0.1:8000
📚 API Documentation

FastAPI automatically provides interactive API documentation.

Open:

http://127.0.0.1:8000/docs

You can test all API endpoints directly from Swagger UI.

🌐 Start the Frontend

Open a second terminal.

Go to the frontend directory:

cd frontend

Start a local HTTP server:

python -m http.server 5500

Open:

http://127.0.0.1:5500
🔄 Application Flow
User
 │
 │ Upload Image
 ▼
Frontend
 │
 │ POST /remove-background
 ▼
FastAPI Backend
 │
 ▼
Image Validation
 │
 ▼
Quality Processing
 │
 ├── Low
 │
 ├── Standard
 │
 └── High
 │
 ▼
ISNet AI Model
 │
 ▼
Background Removed
 │
 ▼
Transparent PNG
 │
 ▼
Frontend Preview
 │
 ├── Before/After Slider
 │
 └── Download
🎚️ Quality Modes

The application provides three processing modes.

Low
Maximum processing dimension: 768px

Recommended when:

Speed is important
You need quick previews
Image details are not critical

Processing flow:

Original Image
      ↓
Resize for AI
      ↓
768px maximum dimension
      ↓
Background Removal
      ↓
Restore original canvas
Standard
Maximum processing dimension: 1280px

Recommended for normal usage.

It provides a balance between:

Speed
Quality
Edge accuracy

Processing flow:

Original Image
      ↓
Resize for AI
      ↓
1280px maximum dimension
      ↓
Background Removal
      ↓
Restore original canvas
High

High mode does not resize the input before AI processing.

Original Resolution
      ↓
AI Processing
      ↓
Transparent PNG

This provides the highest available input detail but can take significantly longer for large images, especially when running inference on CPU.

🖼️ Image Handling

The backend:

Validates the uploaded file.
Checks the file size.
Corrects EXIF orientation.
Converts the image to RGBA.
Stores the original dimensions.
Resizes the image for Low/Standard processing.
Runs AI background removal.
Restores the result to the original canvas dimensions.
Saves the result as a transparent PNG.

This allows vertical and horizontal images to maintain their original orientation and dimensions.

📐 Supported Images

Supported input formats:

JPG
JPEG
PNG
WEBP

Maximum file size:

10 MB

Output format:

PNG

The output PNG supports transparency.

🔌 API Endpoints
GET /

Checks whether the API is running.

Example response
{
  "success": true,
  "message": "Background Remover API is running"
}
POST /remove-background

Removes the background from an uploaded image.

Query parameter
quality

Accepted values:

low
standard
high

Example:

POST /remove-background?quality=standard
Request

Multipart form data:

file = image
Example response
{
  "success": true,
  "message": "Background removed successfully",
  "file_id": "example-file-id",
  "quality": "standard",
  "original_size": {
    "width": 1920,
    "height": 1080
  },
  "ai_input_size": {
    "width": 1280,
    "height": 720
  },
  "processing_time": 4.12,
  "download_url": "http://127.0.0.1:8000/download/example-file-id"
}
GET /download/{file_id}

Downloads the processed PNG.

Example:

GET /download/example-file-id
🎨 Frontend

The frontend is intentionally lightweight.

Current interface includes:

Background Remover

[ Choose Image ]

Quality:
[ Low ]
[ Standard ]
[ High ]

[ Remove Background ]

Processing status

Live Preview

Original  ←──────→  Removed Background

[ Download PNG ]
🔍 Live Preview

The application provides a before/after comparison slider.

The slider allows the user to move between:

Original Image

and:

Background Removed Image

The processed image uses a checkerboard background to indicate transparency.

The backend preserves the original canvas dimensions so the comparison remains aligned for:

Portrait images
Landscape images
Square images
Camera images with EXIF orientation
🧹 Temporary File Cleanup

Uploaded source images are stored temporarily during processing.

Processed files are automatically deleted after the configured expiry period.

Current expiry:

1 hour

Configuration:

FILE_EXPIRY = 60 * 60
🔐 Security Considerations

The current version includes basic protection:

File type validation
File size validation
Image validation
Unique UUID filenames
Temporary file cleanup
No user-controlled filesystem paths

For production deployment, additional security should be added:

Rate limiting
Authentication
Abuse protection
Cloud storage
Request limits
Logging
HTTPS
Content scanning
⚙️ Environment

The project is currently designed for local development.

Recommended environment:

Python 3.x
Windows / Linux / macOS
CPU inference

GPU acceleration can be added later for production deployments.

📦 Requirements

Typical backend dependencies include:

fastapi
uvicorn
python-multipart
Pillow
rembg
onnxruntime

Install them with:

pip install -r requirements.txt
🧪 Testing
Test the API

Start the backend:

python -m uvicorn main:app --reload

Then visit:

http://127.0.0.1:8000/docs

Test:

POST /remove-background

with:

Low
Standard
High
Test the frontend

Start:

python -m http.server 5500

Then open:

http://127.0.0.1:5500

Test:

JPG upload
PNG upload
WEBP upload
Portrait image
Landscape image
Square image
Low quality
Standard quality
High quality
Slider preview
PNG download
🐛 Troubleshooting
No onnxruntime backend found

Install CPU support:

pip install "rembg[cpu]"

Then restart the backend.

Frontend button does not work

Make sure both servers are running.

Backend
python -m uvicorn main:app --reload
Frontend
python -m http.server 5500

Open:

http://127.0.0.1:5500

Do not open the HTML file directly with:

file://
CORS error

The FastAPI backend includes CORS middleware for local development.

Check that the backend is running on:

http://127.0.0.1:8000