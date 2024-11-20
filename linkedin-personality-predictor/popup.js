document.getElementById("predict-button").addEventListener("click", async () => {
    const apiUrl = "http://127.0.0.1:5000/scrape"; // Flask backend URL
    const currentTab = await getCurrentTab();

    if (currentTab && currentTab.url.includes("linkedin.com/in/")) {
        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: currentTab.url }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();
            document.getElementById("output").innerText = data.insights || data.error;
        } catch (error) {
            document.getElementById("output").innerText = `Error: ${error.message}`;
        }
    } else {
        document.getElementById("output").innerText =
            "Please navigate to a LinkedIn profile.";
    }
});

// Helper function to get the current active tab
async function getCurrentTab() {
    const queryOptions = { active: true, lastFocusedWindow: true };
    const [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}
