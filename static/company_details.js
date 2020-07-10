const BASE_URL = "http://localhost:5000/api";
let stock_symbol = $("h1").attr("id");

// base company details
async function basicCompanyDetails() {
	const returnedDetails = await axios.post(`${BASE_URL}/company-details`, { stock_symbol });
	// see stock_details.js
	fillCompanyDetails(returnedDetails.data.stock);
}

async function advancedCompanyDetails() {
	const returnedDetails = await axios.post(`${BASE_URL}/advanced-company-details`, {
		stock_symbol,
	});
	fillBasicFinancial(returnedDetails.data.stock);
	fillRecommendation(returnedDetails.data.stock);
	fillPeers(returnedDetails.data.peers);
}

async function companyNews() {
	// let stock_symbol = $("h1").attr("id");
	const returnedDetails = await axios.post(`${BASE_URL}/company-details/news`, { stock_symbol });
	for (let article of returnedDetails.data.news) {
		let newArticle = $(generateNewsHTML(article));
		$("#articles").append(newArticle);
	}
}

function generateNewsHTML(newsArticle) {
	return `
    <div class="col mb-4 ">
        <div class="card shadow-sm mb-5 bg-white rounded mx-auto">
            <img src="${newsArticle.image}" class="card-img-top"
            onerror="this.onerror=null;this.src='/static/images/image-not-provided.jpg';" alt="image not provided">
            <div class="card-body">
                <h5 class="card-title">${newsArticle.headline}</h5>
                <p class="card-text">
                    ${newsArticle.summary}
                </p>
                <a href="${newsArticle.url}" class="card-link">See Full Article</a>
            </div>
        </div>
    </div>
    `;
}
function fillPeers(peersList) {
	for (peerIndex in peersList) {
		let peer = peersList[peerIndex];
		let newPeer = $(generatePeerHTML(peer));
		$("#peers").append(newPeer);
	}
}

function generatePeerHTML(symbol) {
	return `
        <li class="list-inline-item">
            <a class="peers-symbol" href="/company-details/${symbol}">${symbol}</a>
        </li>
        `;
}

// ******fill tables******
// fill basic financial details table
function fillBasicFinancial(data) {
	$("#yearly-high").text(formatCurrency(data.yearlyHigh));
	$("#yearly-high-date").text(FormateDate(data.yearlyHighDate));
	$("#yearly-low").text(formatCurrency(data.yearlyLow));
	$("#yearly-low-date").text(FormateDate(data.yearlyLowDate));
	$("#beta").text(data.beta);
}

// fill recommendation table
function fillRecommendation(data) {
	$("#r-date").text(FormateDate(data.lastUpdated));
	$("#s-buy").text(data.strongBuy);
	$("#buy").text(data.buy);
	$("#hold").text(data.hold);
	$("#sell").text(data.sell);
	$("#s-sell").text(data.strongSell);
	$("#h-target").text(formatCurrency(data.targetHigh));
	$("#l-target").text(formatCurrency(data.targetLow));
	$("#target-mean").text(formatCurrency(data.targetMean));
	$("#target-median").text(formatCurrency(data.targetMedian));
}

basicCompanyDetails();
advancedCompanyDetails();
companyNews();
