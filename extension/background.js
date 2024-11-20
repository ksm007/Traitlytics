// background.js
chrome.action.onClicked.addListener((tab) => {
    if (tab.url.includes("linkedin.com/in/")) {
        console.log("LinkedIn profile detected, sending URL to backend:", tab.url); // Log the URL

        fetch("http://localhost:5000/scrape", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: tab.url })
        })
        .then(response => response.json())
        .then(data => {
            if (data.traits) {
                console.log("Received data from backend:", data); // Log the received data
                chrome.storage.local.set({ personalityTraits: data.traits });
            } else if (data.error) {
                console.error("Backend Error:", data.error);
                chrome.storage.local.set({ personalityTraits: { error: data.error } });
            }
        })
        .catch(error => {
            console.error("Fetch Error:", error);
            chrome.storage.local.set({ personalityTraits: { error: error.toString() } });
        });
    } else {
        console.error("Not on a LinkedIn profile page.");
    }
});
