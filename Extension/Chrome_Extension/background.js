/**
 * Make an map of tabId:BotId
 * Check if the tabId closed exists in the map key and if yes send the leave request for the bot to the server.
 */

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
	if (tab.url && tab.url.includes("youtube.com/")) {

		const ytUrl = tab.url;
		console.log("YT Url to be sent ", ytUrl);
		console.log("CHANGE INFO : ", changeInfo);

		if (changeInfo.status === "complete" && tab.url!=="https://www.youtube.com/") {
			console.log("Content script trigerred");
			setTimeout(() => {
				chrome.tabs.sendMessage(tabId, {
					type: "NEW",
					ytUrl: ytUrl,
				});
			}, 3000);
		}

	}
});
