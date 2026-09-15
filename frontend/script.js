const fileInput = document.getElementById("fileInput");
const removeBtn = document.getElementById("removeBtn");
const qualitySelect = document.getElementById("quality");

const statusText = document.getElementById("status");

const resultContainer =
    document.getElementById("resultContainer");

const originalPreview =
    document.getElementById("originalPreview");

const resultImage =
    document.getElementById("resultImage");

const processingInfo =
    document.getElementById("processingInfo");

const downloadBtn =
    document.getElementById("downloadBtn");

const comparisonSlider =
    document.getElementById("comparisonSlider");

const resultLayer =
    document.getElementById("resultLayer");

const sliderLine =
    document.getElementById("sliderLine");

const API_URL =
    "http://127.0.0.1:8000";


// ======================================================
// SHOW ORIGINAL IMAGE WHEN USER SELECTS FILE
// ======================================================

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (!file) {
        return;
    }

    const imageURL =
        URL.createObjectURL(file);

    originalPreview.src = imageURL;

    statusText.textContent =
        "Image selected. Choose quality and remove background.";

    resultContainer.style.display = "none";

    comparisonSlider.value = 50;

    updateComparison();
});


// ======================================================
// REMOVE BACKGROUND
// ======================================================

removeBtn.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {

        statusText.textContent =
            "Please select an image first.";

        return;
    }


    const quality =
        qualitySelect.value;


    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    // Disable button while processing
    removeBtn.disabled = true;


    statusText.textContent =
        "Removing background...";


    resultContainer.style.display =
        "none";


    try {

        const response =
            await fetch(
                `${API_URL}/remove-background?quality=${quality}`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        // API error
        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong."
            );
        }


        // Background removal error
        if (!data.success) {

            throw new Error(
                data.message ||
                "Background removal failed."
            );
        }


        // ==================================================
        // ORIGINAL IMAGE
        // ==================================================

        originalPreview.src =
            URL.createObjectURL(file);


        // ==================================================
        // PROCESSED IMAGE
        // ==================================================

        resultImage.src =
            `${data.download_url}?t=${Date.now()}`;


        // ==================================================
        // DOWNLOAD
        // ==================================================

        downloadBtn.href =
            data.download_url;


        // ==================================================
        // PROCESSING INFO
        // ==================================================

        processingInfo.textContent =
            `${data.quality.toUpperCase()} quality • ` +
            `${data.processing_time} seconds`;


        // ==================================================
        // SHOW RESULT
        // ==================================================

        resultContainer.style.display =
            "block";


        statusText.textContent =
            "Background removed successfully!";


        // ==================================================
        // RESET SLIDER
        // ==================================================

        comparisonSlider.value = 50;

        updateComparison();


        // ==================================================
        // WAIT UNTIL BOTH IMAGES ARE LOADED
        // ==================================================

        await waitForImage(
            originalPreview
        );

        await waitForImage(
            resultImage
        );


        // Make sure comparison starts exactly at 50%
        updateComparison();


    } catch (error) {

        console.error(
            "Background removal error:",
            error
        );


        statusText.textContent =
            `Error: ${error.message}`;


    } finally {

        removeBtn.disabled = false;

    }

});


// ======================================================
// LIVE BEFORE / AFTER SLIDER
// ======================================================

comparisonSlider.addEventListener(
    "input",
    updateComparison
);


// ======================================================
// UPDATE COMPARISON
// ======================================================

function updateComparison() {

    const value =
        Number(
            comparisonSlider.value
        );


    // Reveal processed image
    // from the left side
    resultLayer.style.clipPath =
        `inset(0 ${100 - value}% 0 0)`;


    // Move vertical divider
    sliderLine.style.left =
        `${value}%`;
}


// ======================================================
// WAIT FOR IMAGE TO LOAD
// ======================================================

function waitForImage(imageElement) {

    return new Promise((resolve) => {

        if (imageElement.complete) {

            resolve();
            return;
        }


        imageElement.addEventListener(
            "load",
            resolve,
            {
                once: true
            }
        );


        imageElement.addEventListener(
            "error",
            resolve,
            {
                once: true
            }
        );

    });

}


// ======================================================
// INITIAL SLIDER POSITION
// ======================================================

comparisonSlider.value = 50;

updateComparison();