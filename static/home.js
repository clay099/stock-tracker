async function companyNews() {
	const returnedDetails = await axios.post(
		`${BASE_URL_API}/company-details/news`
	);
	for (let article of returnedDetails.data.news) {
		let newArticle = $(generateNewsHTML(article));
		$("#articles").append(newArticle);
	}
}

companyNews();
