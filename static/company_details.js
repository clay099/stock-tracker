const BASE_URL = "http://localhost:5000/api";

// base company details
async function basicCompanyDetails() {
	let stock_symbol = $("h1").attr("id");
	const returnedDetails = await axios.post(`${BASE_URL}/company-details`, { stock_symbol });
	// see stock_details.js
	fillCompanyDetails(returnedDetails.data.stock);
}

basicCompanyDetails();
