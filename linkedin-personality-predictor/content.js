chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "dummyAction") {
      sendResponse({ status: "Content script not in use for this project." });
  }
});


chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (
      changeInfo.status === "complete" &&
      tab.url &&
      tab.url.includes("linkedin.com/in/")
  ) {
      // Show a browser action popup when a LinkedIn profile is detected
      chrome.action.openPopup();
  }
});
