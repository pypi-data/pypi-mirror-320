//*********** DOM Content Loaded Event Listener ***********
document.addEventListener("DOMContentLoaded", () => {
  //*********** Wait for #submit-button Element ***********
  waitForElement("#submit-button", () => {
    //*********** Initialize Submit Button Logic ***********
    initializeSubmitButton();

    //*********** Set Up MutationObserver for Dynamically Added Submit Buttons ***********
    const observer = new MutationObserver(() => {
      initializeSubmitButton(); // Reinitialize if new buttons are added dynamically
    });

    //*********** Start Observing the DOM for Changes ***********
    observer.observe(document.body, { childList: true, subtree: true });
  });
});

//*********** Wait for Element Utility Function ***********
function waitForElement(selector, callback) {
  const element = document.querySelector(selector);
  if (element) {
    callback(); // Execute callback if element is found
  } else {
    setTimeout(() => waitForElement(selector, callback), 100); // Retry after 100ms
  }
}

//*********** Initialize Submit Button Logic ***********
function initializeSubmitButton() {
  //*********** Select All #submit-button Elements ***********
  const buttons = document.querySelectorAll("#submit-button");

  buttons.forEach((button) => {
    //*********** Check if Button is Already Initialized ***********
    if (!button.dataset.initialized) {
      //*********** Mark Button as Initialized ***********
      button.dataset.initialized = "true";

      const messages = [
        "Step 1: Analyzing question...",
        "Step 2: Fetching results...",
        "Step 3: Filtering results...",
        "Step 4: Summarizing results...",
        "Step 5: Generating answer...",

      ];

      const messageElement = document.getElementById("loading-message");
      const loaderContainer = document.getElementById("loader-container");
      const chatOutput = document.getElementById("chat-output");
      let messageInterval;
      let currentIndex = 0;
      let contentLoaded = false;

      //*********** Function to Update Loading Message ***********
      const updateMessage = () => {
        if (contentLoaded) {
          clearInterval(messageInterval);
          return;
        }

        if (currentIndex < messages.length) {
          messageElement.textContent = messages[currentIndex];
          currentIndex++;
        } else {
          messageElement.textContent = "Processing complete!";
          clearInterval(messageInterval);
        }
      };

      //*********** Function to Scroll Chat Output to the Top ***********
      const scrollToTop = () => {
        if (chatOutput) {
          chatOutput.scrollTop = 0;
          chatOutput.setAttribute("data-scrollbar", "0");
        }
      };

      //*********** Add Click Event Listener to Submit Button ***********
      button.addEventListener("click", () => {
        console.log("Submit button clicked!");
        currentIndex = 0;
        contentLoaded = false;
        updateMessage();

        //*********** Start Updating Messages Every 5000ms ***********
        messageInterval = setInterval(updateMessage, 8000);

        //*********** Show Loader ***********
        loaderContainer.style.display = "flex";
        messageElement.style.display = "flex";
      });

      //*********** Observe Changes in chat-output ***********
      const observer = new MutationObserver(() => {
        contentLoaded = true;
        clearInterval(messageInterval);

        //*********** Hide Loader ***********
        loaderContainer.style.display = "none";
        messageElement.style.display = "none";

        //*********** Scroll to the Top of chat-output ***********
        scrollToTop();
      });

      observer.observe(chatOutput, { childList: true, subtree: true });
    }
  });
}