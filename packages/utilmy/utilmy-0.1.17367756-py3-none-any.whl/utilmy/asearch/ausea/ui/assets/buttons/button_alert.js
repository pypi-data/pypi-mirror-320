//*********** DOM Content Loaded Event Listener ***********
document.addEventListener("DOMContentLoaded", () => {
    //*********** Wait for #copy-button Element ***********
    waitForElement("#copy-button", () => {
        //*********** Initialize ClipboardJS ***********
        initializeClipboard();

        //*********** Set Up MutationObserver for Dynamically Added Copy Buttons ***********
        const observer = new MutationObserver(() => {
            initializeClipboard(); // Reinitialize ClipboardJS for new buttons
        });

        //*********** Start Observing the DOM for Changes ***********
        observer.observe(document.body, { childList: true, subtree: true });
    });
});

//*********** Wait for Element Utility Function ***********
function waitForElement(selector, callback) {
    //*********** Check if Selector Exists in the DOM ***********
    const element = document.querySelector(selector);
    if (element) {
        callback(); //*********** Execute Callback if Element is Found ***********
    } else {
        //*********** Retry After 100ms if Element is Not Found ***********
        setTimeout(() => waitForElement(selector, callback), 100);
    }
}

//*********** Initialize ClipboardJS ***********
function initializeClipboard() {
    //*********** Select All #copy-button Elements ***********
    const buttons = document.querySelectorAll("#copy-button");

    buttons.forEach((button) => {
        //*********** Check if ClipboardJS is Already Initialized ***********
        if (!button.dataset.clipboardInitialized) {
            //*********** Mark Button as Initialized ***********
            button.dataset.clipboardInitialized = "true";

            //*********** Initialize ClipboardJS ***********
            const clipboard = new ClipboardJS(button, {
                text: () => {
                    const chatOutput = document.getElementById("chat-output");
                    return chatOutput ? chatOutput.innerText : "";
                }
            });

            //*********** Handle Clipboard Success Event ***********
            clipboard.on("success", () => {
                console.log( "Text successfully copied!")
                // triggerModal("Copied to Clipboard", "Text successfully copied!");
            });

            //*********** Handle Clipboard Error Event ***********
            clipboard.on("error", () => {
                console.log( "Unable to copy the text. Please try again.")
                // triggerModal("Copy Failed", "Unable to copy the text. Please try again.");
            });
        }
    });
}

//todo need to recheck this approach.
//*********** Trigger Modal Function ***********
function triggerModal(title, message) {
    //*********** Update Modal Content ***********
    const modalTitle = document.getElementById("modal-title");
    const modalBody = document.getElementById("modal-body");
    const modalElement = document.getElementById("alert_handler");
    if (modalTitle && modalBody && modalElement) {
        modalTitle.textContent = title;
        modalBody.textContent = message;

        //*********** Show the Modal Using Bootstrap's Modal API ***********
        const bootstrapModal = new bootstrap.Modal(modalElement);
        bootstrapModal.show();
    } else {
        //*********** Fallback: Log Warning if Modal is Not Available ***********
        console.warn("Modal elements not found. Check your modal structure.");
    }
}
