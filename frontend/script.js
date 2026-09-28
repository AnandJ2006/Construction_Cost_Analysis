let dashboardData = [];
let filteredData = [];

let costComparisonChart = null;
let categoryChart = null;
let durationChart = null;
let locationChart = null;


// ======================================================
// LOAD DASHBOARD DATA
// ======================================================

async function loadDashboard() {

    try {

        const response =
            await fetch("../backend/dashboard_data.json");

        if (!response.ok) {
            throw new Error(
                "dashboard_data.json could not be loaded"
            );
        }

        dashboardData = await response.json();

        console.log(
            "Dashboard data loaded:",
            dashboardData.length
        );

        console.log(
            "First project:",
            dashboardData[0]
        );

        filteredData = [...dashboardData];

        populateFilters();

        updateDashboard();

    } catch (error) {

        console.error(error);

        alert(
            "Unable to load dashboard data. " +
            "Check the browser console."
        );
    }
}


// ======================================================
// NUMBER HELPER
// ======================================================

function number(value) {

    const n = Number(value);

    return Number.isFinite(n) ? n : 0;
}


// ======================================================
// CURRENCY
// ======================================================

function formatCurrency(value) {

    return "₹" +
        number(value).toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 0
            }
        );
}


// ======================================================
// FILTERS
// ======================================================

function populateFilters() {

    const locationSelect =
        document.getElementById(
            "locationFilter"
        );

    const sizeSelect =
        document.getElementById(
            "sizeFilter"
        );


    const locations =
        [
            ...new Set(
                dashboardData
                    .map(item => item.Location)
                    .filter(Boolean)
            )
        ]
        .sort();


    const sizes =
        [
            ...new Set(
                dashboardData
                    .map(item => item.Project_Size)
                    .filter(value =>
                        value !== null &&
                        value !== undefined &&
                        value !== ""
                    )
            )
        ]
        .sort(
            (a, b) =>
                number(a) - number(b)
        );


    locationSelect.innerHTML =
        `<option value="All">
            All Locations
        </option>`;


    locations.forEach(location => {

        locationSelect.innerHTML +=
            `<option value="${location}">
                ${location}
            </option>`;

    });


    sizeSelect.innerHTML =
        `<option value="All">
            All Sizes
        </option>`;


    sizes.forEach(size => {

        sizeSelect.innerHTML +=
            `<option value="${size}">
                ${size}
            </option>`;

    });
}


// ======================================================
// APPLY FILTERS
// ======================================================

function applyFilters() {

    const location =
        document.getElementById(
            "locationFilter"
        ).value;


    const size =
        document.getElementById(
            "sizeFilter"
        ).value;


    const budget =
        document.getElementById(
            "budgetFilter"
        ).value;


    filteredData =
        dashboardData.filter(item => {

            const locationMatch =
                location === "All" ||
                String(item.Location) ===
                String(location);


            const sizeMatch =
                size === "All" ||
                String(item.Project_Size) ===
                String(size);


            let budgetMatch = true;


            if (budget === "Over") {

                budgetMatch =
                    number(
                        item.Total_Cost_Variance
                    ) > 0;

            }


            if (budget === "Under") {

                budgetMatch =
                    number(
                        item.Total_Cost_Variance
                    ) <= 0;

            }


            return (
                locationMatch &&
                sizeMatch &&
                budgetMatch
            );

        });


    console.log(
        "Filtered projects:",
        filteredData.length
    );


    updateDashboard();
}


// ======================================================
// UPDATE EVERYTHING
// ======================================================

function updateDashboard() {

    updateKPIs();

    updateCostComparison();

    updateCategoryChart();

    updateDurationChart();

    updateLocationChart();

    updateTable();
}


// ======================================================
// KPI
// ======================================================

function updateKPIs() {

    const totalProjects =
        filteredData.length;


    const planned =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Planned_Total_Cost
                ),
            0
        );


    const actual =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Actual_Total_Cost
                ),
            0
        );


    const variance =
        actual - planned;


    const variancePercent =
        planned === 0
            ? 0
            : (variance / planned) * 100;


    document.getElementById(
        "totalProjects"
    ).textContent =
        totalProjects;


    document.getElementById(
        "plannedCost"
    ).textContent =
        formatCurrency(planned);


    document.getElementById(
        "actualCost"
    ).textContent =
        formatCurrency(actual);


    document.getElementById(
        "variance"
    ).textContent =
        formatCurrency(variance);


    document.getElementById(
        "variancePercent"
    ).textContent =
        `${variancePercent.toFixed(2)}%`;
}


// ======================================================
// PLANNED VS ACTUAL
// ======================================================

function updateCostComparison() {

    const planned =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Planned_Total_Cost
                ),
            0
        );


    const actual =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Actual_Total_Cost
                ),
            0
        );


    const ctx =
        document.getElementById(
            "costComparisonChart"
        );


    if (costComparisonChart) {

        costComparisonChart.destroy();

    }


    costComparisonChart =
        new Chart(ctx, {

            type: "bar",

            data: {

                labels: [
                    "Planned Cost",
                    "Actual Cost"
                ],

                datasets: [

                    {
                        label: "Cost",

                        data: [
                            planned,
                            actual
                        ],

                        borderRadius: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }

        });
}


// ======================================================
// COST CATEGORY
// ======================================================

function updateCategoryChart() {

    const labour =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Labour_Variance
                ),
            0
        );


    const material =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Material_Variance
                ),
            0
        );


    const equipment =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Equipment_Cost
                ),
            0
        );


    const subcontracting =
        filteredData.reduce(
            (sum, item) =>
                sum +
                number(
                    item.Subcontracting_Cost
                ),
            0
        );


    const ctx =
        document.getElementById(
            "categoryChart"
        );


    if (categoryChart) {

        categoryChart.destroy();

    }


    categoryChart =
        new Chart(ctx, {

            type: "bar",

            data: {

                labels: [
                    "Labour",
                    "Material",
                    "Equipment",
                    "Subcontracting"
                ],

                datasets: [

                    {
                        label: "Cost",

                        data: [
                            labour,
                            material,
                            equipment,
                            subcontracting
                        ],

                        borderRadius: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }

        });
}


// ======================================================
// DURATION VS VARIANCE
// ======================================================

function updateDurationChart() {

    const data =
        filteredData
            .map(item => ({

                x: number(
                    item.Duration
                ),

                y: number(
                    item.Total_Cost_Variance
                )

            }))
            .filter(point =>
                Number.isFinite(point.x) &&
                Number.isFinite(point.y)
            );


    console.log(
        "Scatter chart points:",
        data.length
    );


    const ctx =
        document.getElementById(
            "durationChart"
        );


    if (durationChart) {

        durationChart.destroy();

    }


    durationChart =
        new Chart(ctx, {

            type: "scatter",

            data: {

                datasets: [

                    {

                        label:
                            "Projects",

                        data: data,

                        pointRadius: 5,

                        pointHoverRadius: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    x: {

                        type: "linear",

                        title: {

                            display: true,

                            text:
                                "Project Duration"

                        }

                    },

                    y: {

                        title: {

                            display: true,

                            text:
                                "Cost Variance"

                        }

                    }

                }

            }

        });
}


// ======================================================
// LOCATION
// ======================================================

function updateLocationChart() {

    const locationMap = {};


    filteredData.forEach(item => {

        const location =
            String(
                item.Location ||
                "Unknown"
            );


        if (!locationMap[location]) {

            locationMap[location] = 0;

        }


        locationMap[location] +=
            number(
                item.Total_Cost_Variance
            );

    });


    const locations =
        Object.keys(locationMap);


    const values =
        Object.values(locationMap);


    console.log(
        "Locations:",
        locations
    );


    const ctx =
        document.getElementById(
            "locationChart"
        );


    if (locationChart) {

        locationChart.destroy();

    }


    locationChart =
        new Chart(ctx, {

            type: "bar",

            data: {

                labels: locations,

                datasets: [

                    {

                        label:
                            "Cost Variance",

                        data: values,

                        borderRadius: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    y: {

                        beginAtZero: true

                    }

                }

            }

        });
}


// ======================================================
// TABLE
// ======================================================

function updateTable() {

    const table =
        document.getElementById(
            "projectTable"
        );


    table.innerHTML = "";


    if (filteredData.length === 0) {

        table.innerHTML = `

            <tr>

                <td colspan="8"
                    style="text-align:center;padding:30px">

                    No projects found.

                </td>

            </tr>

        `;

        return;

    }


    filteredData.forEach(item => {

        const variance =
            number(
                item.Total_Cost_Variance
            );


        const status =
            variance > 0
                ? "Over Budget"
                : "Under Budget";


        const statusClass =
            variance > 0
                ? "over-budget"
                : "under-budget";


        table.innerHTML += `

            <tr>

                <td>
                    ${item.Project_ID}
                </td>

                <td>
                    ${item.Location}
                </td>

                <td>
                    ${Number(
                        item.Project_Size
                    ).toLocaleString("en-IN")}
                </td>

                <td>
                    ${item.Duration} days
                </td>

                <td>
                    ${formatCurrency(
                        item.Planned_Total_Cost
                    )}
                </td>

                <td>
                    ${formatCurrency(
                        item.Actual_Total_Cost
                    )}
                </td>

                <td>
                    ${formatCurrency(
                        variance
                    )}
                </td>

                <td>

                    <span
                        class="status-badge ${statusClass}"
                    >

                        ${status}

                    </span>

                </td>

            </tr>

        `;

    });
}


// ======================================================
// START
// ======================================================

loadDashboard();