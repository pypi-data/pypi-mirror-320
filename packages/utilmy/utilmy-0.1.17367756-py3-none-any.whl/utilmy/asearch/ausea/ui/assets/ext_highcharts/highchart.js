//*********** DOM Content Loaded Event Listener ***********
document.addEventListener("DOMContentLoaded", () => {
    //*********** Retry Logic for Initial Load ***********
    waitForElement(".chart-container", () => {
        // Initialize pre-existing chart containers
        initializeCharts(document.querySelectorAll(".chart-container"));
    });

    //*********** Set Up MutationObserver for Dynamically Added Containers ***********
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            const addedNodes = Array.from(mutation.addedNodes);
            addedNodes.forEach((node) => {
                // Check if the added node or its children are chart containers
                const newChartContainers = node.classList?.contains("chart-container")
                    ? [node]
                    : Array.from(node.querySelectorAll?.(".chart-container") || []);

                if (newChartContainers.length > 0) {
                    initializeCharts(newChartContainers);
                }
            });
        });
    });

    //*********** Start Observing the DOM for Changes ***********
    observer.observe(document.body, {childList: true, subtree: true});
});

//*********** Wait for Element Utility Function ***********
function waitForElement(selector, callback) {
    const element = document.querySelector(selector);
    if (element) {
        callback();
    } else {
        setTimeout(() => waitForElement(selector, callback), 100);
    }
}

//*********** Initialize Charts ***********
function initializeCharts(chartContainers) {
    chartContainers.forEach((container) => {
        if (!container.id) {
            console.error("Chart container must have a unique ID:", container);
            return;
        }

        if (!container.hasAttribute("data-initialized")) {
            //*********** Read Data from Inner Child ***********
            const rawData = document.querySelector("#chart-data")?.textContent;
            console.log(rawData)
            const sanitizedData = rawData
                .replace(/'/g, '"')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false');
            const data = sanitizedData ? JSON.parse(sanitizedData) : {};
            //*********** Initialize Highchart with Histogram Only ***********
            Highcharts.chart(container.id, data);
            container.setAttribute("data-initialized", "true");
        } else {
            console.log(`Highchart already initialized for container ID: ${container.id}`);
        }
    });
}

