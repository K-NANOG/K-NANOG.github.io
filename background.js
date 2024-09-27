chrome.action.onClicked.addListener(function(tab) {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    var activeTab = tabs[0];
    var url = activeTab.url;
    sendLinkToLocalServer(url);
  });
});

function sendLinkToLocalServer(url) {
  fetch('http://127.0.0.1:5000/process_url', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ 'url': url })
  })
  .then(response => response.text())
  .then(data => console.log('Réponse du serveur :', data))
  .catch(error => console.error('Erreur :', error));
}
