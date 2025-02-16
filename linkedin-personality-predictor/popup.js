

document.getElementById("predict-button").addEventListener("click", async () => {
    const apiUrl = "http://127.0.0.1:5000/scrape"; // Flask backend URL
    const currentTab = await getCurrentTab();

    if (currentTab && currentTab.url.includes("linkedin.com/in/")) {
        try {
            // Show loading message
            document.getElementById("summary").innerText = "Loading insights...";
            document.getElementById("output").innerHTML = "";

            // Fetch data from backend
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: currentTab.url }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Save data to Chrome local storage for persistence
            chrome.storage.local.set({ insights: data }, () => {
                console.log("Insights saved to local storage.");
            });

            // Display insights on the frontend
            displayInsights(data);

        } catch (error) {
            document.getElementById("summary").innerText = "Error: Failed to load insights.";
            document.getElementById("output").innerHTML = `<p>Error: ${error.message}</p>`;
        }
    } else {
        document.getElementById("summary").innerText = "Please navigate to a LinkedIn profile.";
    }
});

// Function to display insights dynamically
function displayInsights(data) {
    document.getElementById("summary").innerText = data.Profile_Summary || "Profile Summary not available.";



    const outputHtml = `
        <h2>DISC Personality Type</h2>
        <p>${data.DISC_Personality_Type || "Not available"}</p>
          <h2>Personality Traits</h2>
        <p>${data.Personality_Diagram || "Not available"}</p>

        <h2>Key Traits</h2>
        <ul>
            ${data.Key_Traits ? data.Key_Traits.map(trait => `<li>${trait}</li>`).join('') : "<li>Not available</li>"}
        </ul>
      
        <h2>Do's</h2>
        <ul>
            ${data.Dos ? data.Dos.map(doItem => `<li>${doItem}</li>`).join('') : "<li>Not available</li>"}
        </ul>
        <h2>Don'ts</h2>
        <ul>
            ${data.Donts ? data.Donts.map(dontItem => `<li>${dontItem}</li>`).join('') : "<li>Not available</li>"}
        </ul>
    `;
    document.getElementById("output").innerHTML = outputHtml;
}

// Retrieve saved insights when the popup reopens
document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get("insights", (result) => {
        if (chrome.runtime.lastError) {
            console.error("Error accessing storage:", chrome.runtime.lastError);
            return;
        }

        if (result.insights) {
            console.log("Loaded insights from local storage.");
            displayInsights(result.insights);
        } else {
            document.getElementById("output").innerText = "No data found. Please generate insights.";
        }
    });
});

// Helper function to get the current tab
async function getCurrentTab() {
    const queryOptions = { active: true, lastFocusedWindow: true };
    const [tab] = await chrome.tabs.query(queryOptions);
    return tab;
}
