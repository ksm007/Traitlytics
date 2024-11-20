function scrapeLinkedInProfile() {
    const name = document.querySelector('.text-heading-xlarge')?.innerText;
    const title = document.querySelector('.text-body-medium')?.innerText;
    const summary = document.querySelector('.pv-about__summary-text')?.innerText;
    const experience = Array.from(document.querySelectorAll('.pv-position-entity'))
      .map(el => el.innerText)
      .join("\n");
  
    return { name, title, summary, experience };
  }
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scrapeProfile") {
      const profileData = scrapeLinkedInProfile();
      sendResponse(profileData);
    }
  });
  