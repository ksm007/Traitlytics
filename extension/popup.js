// popup.js
document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get("personalityTraits", (data) => {
        const traitsDiv = document.getElementById("traits");
        if (data.personalityTraits) {
            if (data.personalityTraits.error) {
                traitsDiv.innerText = `Error: ${data.personalityTraits.error}`;
            } else {
                console.log("Traits found in storage:", data.personalityTraits); // Debug log
                traitsDiv.innerText = `Predicted Traits: ${JSON.stringify(data.personalityTraits, null, 2)}`;
            }
        } else {
            traitsDiv.innerText = "No traits found. Visit a LinkedIn profile and click the icon.";
        }
    });
});
