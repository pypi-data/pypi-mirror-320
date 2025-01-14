document.addEventListener("DOMContentLoaded", () => {
    const waitForElement = (selector, callback) => {
        const element = document.querySelector(selector);
        if (element) {
            callback(element);
        } else {
            setTimeout(() => waitForElement(selector, callback), 100);
        }
    };

    const createSuggestionsContainer = () => {
        const container = document.createElement("div");
        Object.assign(container.style, {
            position: "absolute",
            border: "1px solid #ccc",
            background: "#fff",
            zIndex: "1000",
            display: "none",
            maxHeight: "200px",
            overflowY: "auto",
            overflowX: "hidden",
        });
        document.body.appendChild(container);
        return container;
    };

    const fetchSuggestions = async () => {
        try {
            const response = await fetch("assets/ext_autocomplete/suggestions.json");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.suggestionsData;
        } catch (error) {
            console.error("Error fetching suggestions:", error);
            return [];
        }
    };

    const filterSuggestions = (suggestions, query) => {
        return suggestions.filter((item) => item.toLowerCase().includes(query));
    };

    const updateSuggestionsContainer = (
        container,
        suggestions,
        inputElement,
        completeSuggestion
    ) => {
        container.innerHTML = "";
        container.style.display = "none";

        if (suggestions.length) {
            const inputRect = inputElement.getBoundingClientRect();
            Object.assign(container.style, {
                top: `${inputRect.bottom + window.scrollY}px`,
                left: `${inputRect.left + window.scrollX}px`,
                width: `${inputRect.width * 0.8}px`,
                display: "block",
            });

            suggestions.forEach((suggestion, index) => {
                const suggestionItem = document.createElement("div");
                suggestionItem.textContent = suggestion;
                Object.assign(suggestionItem.style, {
                    padding: "8px",
                    cursor: "pointer",
                    borderBottom: "1px solid #eee",
                });

                suggestionItem.addEventListener("mouseover", () => {
                    suggestionItem.style.background = "#f0f0f0";
                });
                suggestionItem.addEventListener("mouseout", () => {
                    suggestionItem.style.background = "#fff";
                });

                suggestionItem.addEventListener("click", () => {
                    completeSuggestion(suggestion);
                });

                container.appendChild(suggestionItem);
            });
        }
    };

    const highlightSuggestion = (items, index) => {
        items.forEach((item, idx) => {
            item.style.background = idx === index ? "#f0f0f0" : "#fff";
        });
    };

    const completeSuggestion = (
        inputElement,
        container,
        selectedText,
        lastSegment
    ) => {
        const inputValue = inputElement.value;
        const newValue =
            inputValue.slice(0, inputValue.length - lastSegment.length) +
            selectedText;
        inputElement.value = newValue;

        const event = new Event("input", {bubbles: true});
        inputElement.dispatchEvent(event);

        inputElement.focus();
        inputElement.setSelectionRange(newValue.length, newValue.length);
        container.style.display = "none";
    };

    waitForElement("#user-input", async (inputElement) => {
        const suggestionsContainer = createSuggestionsContainer();
        const suggestions = await fetchSuggestions();
        let selectedIndex = -1;

        inputElement.addEventListener("input", function () {
            const inputValue = this.value.toLowerCase();

            selectedIndex = -1;
            suggestionsContainer.innerHTML = "";
            suggestionsContainer.style.display = "none";

            const segments = inputValue.split(/[\s.,!?]+/).filter(Boolean);
            const lastSegment = segments[segments.length - 1] || "";

            if (lastSegment.length < 3) {
                return;
            }

            const matches = filterSuggestions(suggestions, lastSegment);
            updateSuggestionsContainer(
                suggestionsContainer,
                matches,
                inputElement,
                (selectedText) => {
                    completeSuggestion(
                        inputElement,
                        suggestionsContainer,
                        selectedText,
                        lastSegment
                    );
                }
            );
        });

        inputElement.addEventListener("keydown", function (e) {
            const suggestionItems = suggestionsContainer.querySelectorAll("div");

            if (e.key === "ArrowDown") {
                e.preventDefault();
                if (suggestionItems.length > 0) {
                    selectedIndex = (selectedIndex + 1) % suggestionItems.length;
                    highlightSuggestion(suggestionItems, selectedIndex);
                }
            }

            if (e.key === "ArrowUp") {
                e.preventDefault();
                if (suggestionItems.length > 0) {
                    selectedIndex =
                        (selectedIndex - 1 + suggestionItems.length) %
                        suggestionItems.length;
                    highlightSuggestion(suggestionItems, selectedIndex);
                }
            }

            if (e.key === "Enter" && selectedIndex !== -1) {
                e.preventDefault();
                const selectedText = suggestionItems[selectedIndex].textContent;
                const segments = inputElement.value.split(/[\s.,!?]+/);
                const lastSegment = segments[segments.length - 1] || "";
                completeSuggestion(
                    inputElement,
                    suggestionsContainer,
                    selectedText,
                    lastSegment
                );
            }

            if (e.key === "Escape") {
                suggestionsContainer.style.display = "none";
                selectedIndex = -1;
            }
        });

        document.addEventListener("click", (e) => {
            if (
                !suggestionsContainer.contains(e.target) &&
                e.target !== inputElement
            ) {
                suggestionsContainer.style.display = "none";
                selectedIndex = -1;
            }
        });
    });
});
