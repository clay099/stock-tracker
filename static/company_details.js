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
	console.log("finished");
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
            <img src="${newsArticle.image}" class="card-img-top" alt="Image failed to load">
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

basicCompanyDetails();
advancedCompanyDetails();
companyNews();
