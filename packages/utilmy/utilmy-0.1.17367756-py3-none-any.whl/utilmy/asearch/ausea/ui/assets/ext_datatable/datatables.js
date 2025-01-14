//*********** DOM Content Loaded Event Listener ***********
document.addEventListener("DOMContentLoaded", () => {
    //*********** Wait for .data-table Element ***********
    waitForElement(".data-table", () => {
        //*********** Initialize Existing DataTables ***********
        initializeExistingTables();

        //*********** Set Up MutationObserver for Dynamically Added Tables ***********
        const observer = new MutationObserver(() => {
            initializeExistingTables(); // Initialize any newly added tables
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

//*********** Initialize Existing DataTables ***********
function initializeExistingTables() {
    //*********** Select All .data-table Elements ***********
    const tables = document.querySelectorAll(".data-table");

    tables.forEach((table) => {
        //*********** Check if DataTable is Already Initialized ***********
        if (!jQuery.fn.DataTable.isDataTable(table)) {

            //*********** Initialize DataTable with Configuration ***********
            const dataTable = new DataTable(table, {
                order: [],                 // Disable initial sort
                paging: true,               // Enable Pagination
                searching: true,            // Enable Search Functionality
                ordering: true,             // Enable Column Ordering
                //columnDefs: [{              // Customize Column Behavior
                //    targets: 0,             // Apply to the First Column
                //    orderable: false        // Disable Ordering for the First Column
                // }]
            });
        } else {
            console.log(`DataTable already initialized for table ID: ${table.id || "Unknown"}`);
        }
    });
}