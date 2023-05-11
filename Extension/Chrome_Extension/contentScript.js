/**	A lot of things need fixing i suppose */

(() => {
	/** TODO:
	 *  Use this waiting function in place of setTimeout
	 */

	let ytId = "";
	function waitForElmToLoad(selector) {
		return new Promise((resolve) => {
			if (document.querySelector(selector)) {
				return resolve(document.querySelector(selector));
			}

			const observer = new MutationObserver((mutations) => {
				if (document.querySelector(selector)) {
					resolve(document.querySelector(selector));
					observer.disconnect();
				}
			});

			observer.observe(document.body, {
				childList: true,
				subtree: true,
			});
		});
	}

	const getSummaryData = async (ytId) => {
		let obj = { videoId: ytId };
		const data = JSON.stringify(obj);
		const response = await fetch(
			"https://ytgpt.airinterview.live/api/v1/summarize",
			{
				method: "POST",
				headers: {
					Accept: "application/json",
					"Content-Type": "application/json",
				},
				body: data,
			}
		);

		if (response.status !== 200) {
			return "Could not retrive summary";
		}

		let responseData = await response.json();
		console.log("DATA is : ", responseData);
		return responseData.summary;
	};



	/**
	 * TODO: 
	 * Add clickbait detection api call
	 * Add Chat socket connections
	 */
	
	chrome.runtime.onMessage.addListener((obj, sender, response) => {
		const { type, ytUrl } = obj;

		const url = new URL(ytUrl);
		ytId = url.searchParams.get("v");
		if (type === "NEW") {
			onYtPageLoad();
		}
	});

	const onYtPageLoad = () => {
		console.log("YT Page is loaded");

		document.getElementById("YtGptSummaryBtn")?.remove();

		//check if there is an existing sdiv due to yts lazy loading
		document.getElementById("sDiv")?.remove();

		//Add clickbait detection UI
		let ytActionsDiv = document.getElementById("actions-inner");
		let innerActionDiv = ytActionsDiv.getElementsByClassName(
			"style-scope ytd-watch-metadata"
		)[0].childNodes[0];
		let summaryBtn = document.createElement("button");
		summaryBtn.innerText = "Summary";
		summaryBtn.id = "YtGptSummaryBtn";
		innerActionDiv.prepend(summaryBtn);

		clickHandler(summaryBtn);
	};

	const clickHandler = async (summaryBtn) => {
		let html = await fetch(chrome.runtime.getURL("app.html"));

		summaryBtn.addEventListener("click", async () => {
			if (document.getElementById("sDiv")) {
				let sDiv = document.getElementById("sDiv");
				sDiv.style.display === "none"
					? (sDiv.style.display = "block")
					: (sDiv.style.display = "none");
				return;
			}

			// Add chat feature  UI @Divyansh
			let ytSidePannel = document.getElementById("secondary-inner");
			let summaryDiv = document.createElement("div");
			summaryDiv.id = "sDiv";
			summaryDiv.innerHTML = await html.text();
			ytSidePannel.prepend(summaryDiv);

			let summaryData = await getSummaryData(ytId);
			let textDiv = await waitForElmToLoad('[id="summaryText"]');
			textDiv.querySelector(".loader").style.display = "none";
			textDiv.innerText = summaryData;
		});

		let closeBtn = await waitForElmToLoad('[id="closeSummary"]');
		closeBtn.addEventListener("click", () => {
			document.getElementById("sDiv").style.display = "none";
		});
	};
})();
