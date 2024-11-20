chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "dummyAction") {
      sendResponse({ status: "Content script not in use for this project." });
  }
});
