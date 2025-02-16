// background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "fetchProfileData") {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: "extractProfile" }, (response) => {
          sendResponse(response);
        });
      });
      return true; // Required to use sendResponse asynchronously
    }
  });
  
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (
        changeInfo.status === "complete" &&
        tab.url &&
        tab.url.includes("linkedin.com/in/")
    ) {
        chrome.action.openPopup();
    }
});
