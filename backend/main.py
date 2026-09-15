from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from rembg import remove, new_session
from PIL import Image, ImageOps

import os
import uuid
import time
from io import BytesIO


# =========================================================
# APP
# =========================================================

app = FastAPI(title="Background Remover API")


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# SETTINGS
# =========================================================

UPLOAD_FOLDER = "uploads"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

FILE_EXPIRY = 60 * 60  # 1 hour


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# AI MODEL
# =========================================================

# Fast + good quality model
session = new_session("isnet-general-use")


# =========================================================
# CLEAN OLD FILES
# =========================================================

def cleanup_old_files():
    current_time = time.time()

    for filename in os.listdir(UPLOAD_FOLDER):

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if os.path.isfile(file_path):

            file_age = (
                current_time
                - os.path.getmtime(file_path)
            )

            if file_age > FILE_EXPIRY:

                try:
                    os.remove(file_path)

                except Exception as e:
                    print(
                        f"Cleanup error: {e}"
                    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "Background Remover API is running"
    }


# =========================================================
# REMOVE BACKGROUND
# =========================================================

@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    quality: str = Query("standard")
):

    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------

    cleanup_old_files()


    # -----------------------------------------------------
    # ALLOWED FILE TYPES
    # -----------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }


    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed"
        )


    # -----------------------------------------------------
    # QUALITY VALIDATION
    # -----------------------------------------------------

    if quality not in {
        "low",
        "standard",
        "high"
    }:

        raise HTTPException(
            status_code=400,
            detail="Quality must be low, standard or high"
        )


    # -----------------------------------------------------
    # READ FILE
    # -----------------------------------------------------

    input_data = await file.read()


    if not input_data:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )


    # -----------------------------------------------------
    # FILE SIZE
    # -----------------------------------------------------

    if len(input_data) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 10 MB"
        )


    # -----------------------------------------------------
    # VALIDATE IMAGE
    # -----------------------------------------------------

    try:

        test_image = Image.open(
            BytesIO(input_data)
        )

        test_image.verify()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )


    # -----------------------------------------------------
    # FILE NAMES
    # -----------------------------------------------------

    file_id = str(uuid.uuid4())


    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_input"
    )


    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_output.png"
    )


    try:

        # -------------------------------------------------
        # SAVE ORIGINAL TEMPORARILY
        # -------------------------------------------------

        with open(
            input_path,
            "wb"
        ) as f:

            f.write(input_data)


        # -------------------------------------------------
        # OPEN ORIGINAL IMAGE
        # -------------------------------------------------

        image = Image.open(
            BytesIO(input_data)
        )


        # -------------------------------------------------
        # FIX EXIF ORIENTATION
        # -------------------------------------------------

        image = ImageOps.exif_transpose(
            image
        )


        # -------------------------------------------------
        # CONVERT TO RGBA
        # -------------------------------------------------

        image = image.convert("RGBA")


        # -------------------------------------------------
        # ORIGINAL SIZE
        # -------------------------------------------------

        original_size = image.size


        # -------------------------------------------------
        # QUALITY SETTINGS
        # -------------------------------------------------

        if quality == "low":

            max_dimension = 768


        elif quality == "standard":

            max_dimension = 1280


        else:

            # HIGH
            # No resize before AI
            max_dimension = None


        # -------------------------------------------------
        # PROCESSING COPY
        # -------------------------------------------------

        processing_image = image.copy()


        width, height = processing_image.size

        largest_side = max(
            width,
            height
        )


        # -------------------------------------------------
        # RESIZE FOR LOW / STANDARD
        # -------------------------------------------------

        if (
            max_dimension is not None
            and largest_side > max_dimension
        ):

            scale = (
                max_dimension
                / largest_side
            )


            processing_size = (
                int(width * scale),
                int(height * scale)
            )


            processing_image = processing_image.resize(
                processing_size,
                Image.Resampling.LANCZOS
            )


        # -------------------------------------------------
        # CONVERT TO PNG BYTES
        # -------------------------------------------------

        temp_buffer = BytesIO()


        processing_image.save(
            temp_buffer,
            format="PNG"
        )


        processed_input = (
            temp_buffer.getvalue()
        )


        # -------------------------------------------------
        # START TIMER
        # -------------------------------------------------

        processing_start = (
            time.perf_counter()
        )


        # -------------------------------------------------
        # AI BACKGROUND REMOVAL
        # -------------------------------------------------

        output_data = remove(
            processed_input,
            session=session
        )


        # -------------------------------------------------
        # END TIMER
        # -------------------------------------------------

        processing_time = (
            time.perf_counter()
            - processing_start
        )


        # -------------------------------------------------
        # LOG
        # -------------------------------------------------

        print(
            f"Quality: {quality} | "
            f"Original: {original_size} | "
            f"AI Input: {processing_image.size} | "
            f"Processing time: "
            f"{processing_time:.2f}s"
        )


        # -------------------------------------------------
        # OPEN AI RESULT
        # -------------------------------------------------

        result_image = Image.open(
            BytesIO(output_data)
        ).convert("RGBA")


        # -------------------------------------------------
        # RESTORE ORIGINAL CANVAS
        # -------------------------------------------------

        if result_image.size != original_size:

            result_image = result_image.resize(
                original_size,
                Image.Resampling.LANCZOS
            )


        # -------------------------------------------------
        # SAVE FINAL TRANSPARENT PNG
        # -------------------------------------------------

        result_image.save(
            output_path,
            format="PNG"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Background removed successfully",

            "file_id":
                file_id,

            "quality":
                quality,

            "original_size": {
                "width": original_size[0],
                "height": original_size[1]
            },

            "ai_input_size": {
                "width": processing_image.size[0],
                "height": processing_image.size[1]
            },

            "processing_time":
                round(
                    processing_time,
                    2
                ),

            "download_url":
                (
                    "http://127.0.0.1:8000"
                    f"/download/{file_id}"
                )
        }


    # =====================================================
    # ERROR
    # =====================================================

    except Exception as e:

        print(
            "ERROR:",
            repr(e)
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "Background removal failed: "
                f"{str(e)}"
            )
        )


    # =====================================================
    # REMOVE ORIGINAL TEMP FILE
    # =====================================================

    finally:

        if os.path.exists(input_path):

            try:

                os.remove(input_path)

            except Exception as e:

                print(
                    f"Input cleanup error: {e}"
                )


# =========================================================
# DOWNLOAD RESULT
# =========================================================

@app.get("/download/{file_id}")
def download_result(file_id: str):

    output_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_output.png"
    )


    if not os.path.exists(output_path):

        raise HTTPException(
            status_code=404,
            detail="Processed image not found"
        )


    return FileResponse(
        output_path,
        media_type="image/png",
        filename="background-removed.png"
    )