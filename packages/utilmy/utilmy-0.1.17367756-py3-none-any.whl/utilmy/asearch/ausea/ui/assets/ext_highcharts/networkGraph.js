//*********** DOM Content Loaded Event Listener ***********
document.addEventListener("DOMContentLoaded", () => {
    //*********** Retry Logic for Initial Load ***********
    waitForElement(".chart-network-container", () => {
        // Initialize pre-existing network graph containers
        initializeNetworkGraph(document.querySelectorAll(".chart-network-container"));
    });

    //*********** Set Up MutationObserver for Dynamically Added Containers ***********
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            const addedNodes = Array.from(mutation.addedNodes);
            addedNodes.forEach((node) => {
                // Check if the added node or its children are chart-network-container
                const newNetworkContainers = node.classList?.contains("chart-network-container") ? [node] : Array.from(node.querySelectorAll?.(".chart-network-container") || []);

                if (newNetworkContainers.length > 0) {
                    initializeNetworkGraph(newNetworkContainers);
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

function calculateCircularCoordinates(nodeCount, radius, centerX = 0, centerY = 0) {
    const coordinates = [];
    const angleStep = (2 * Math.PI) / nodeCount;

    for (let i = 0; i < nodeCount; i++) {
        const angle = i * angleStep;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        coordinates.push({x, y});
    }

    return coordinates;
}

//*********** Initialize chart-network-container ***********
function initializeNetworkGraph(newNetworkContainers) {
    newNetworkContainers.forEach((container) => {
        if (!container.id) {
            console.error("newNetworkContainers container must have a unique ID:", container);
            return;
        }

        if (!container.hasAttribute("data-initialized")) {
            //*********** Read Data from Inner Child ***********
            const rawData = document.querySelector("#chart-network-data")?.textContent;
            const sanitizedData = rawData
                .replace(/'/g, '"')
                .replace(/\bTrue\b/g, 'true')
                .replace(/\bFalse\b/g, 'false');
            const data = sanitizedData ? JSON.parse(sanitizedData) : {};
            // *********** Initialize Highchart with Histogram Only ***********
            if (data?.data?.edges !== undefined) {
                Highcharts.addEvent(Highcharts.Series, 'afterSetOptions', function (e) {
                    const nodes = {};
                    const coordinates = calculateCircularCoordinates(data.data.sourceNodes.length, 200, this.chart.plotWidth / 2, this.chart.plotHeight * 0.33)
                    if (this instanceof Highcharts.Series.types.networkgraph && e.options.id === 'lang-tree') {

                        const nodes = [];

                        [...data.data.sourceNodes].forEach((node, index) => {
                            const {x, y} = coordinates[index]
                            nodes.push({
                                id: node.id, name: node.name, marker: {
                                    radius: 30, symbol: `url(${node.logo})`, width: 30, height: 30

                                }, isSourceNode: true, dataLabels: {
                                    verticalAlign: 'bottom', enabled: true, textPath: {
                                        enabled: true
                                    }, linkFormat: '', allowOverlap: true, style: {
                                        "fontSize": "0.6rem", "fontWeight": "normal"
                                    }
                                },

                                custom: {
                                    activityCounts: node.activityCounts || []
                                }, plotX: x, plotY: y, fixedPosition: {x, y}
                            });
                        });

                        [...data.data.targetNodes].forEach((node, index) => {
                            nodes.push({
                                id: node.id, name: node.name, marker: {
                                    radius: 30, width: 30, height: 30, symbol: `url(${node.logo})`,

                                }, dataLabels: {
                                    enabled: true, textPath: {
                                        enabled: true
                                    }, linkFormat: '', allowOverlap: true, "style": {
                                        "fontSize": "0.6rem", "fontWeight": "normal"
                                    }
                                },

                                custom: {
                                    activityCounts: node.activityCounts || []
                                }
                            });
                        });

                        e.options.nodes = Object.keys(nodes).map((id) => nodes[id]);
                    }
                });


                const links = [];
                data.data.edges.forEach((edge) => {
                    links.push([edge.source, edge.target]);
                });

                data.series[0].data = links

            }

            Highcharts.chart(container.id, data);
            container.setAttribute("data-initialized", "true");
        } else {
            console.log(`Highchart already initialized for container ID: ${container.id}`);
        }
    });
}

