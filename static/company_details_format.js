// fill company details modal
function fillCompanyDetails(data) {
	$("#country").text(data.country);
	$("#currency").text(data.currency);
	$("#exchange").text(data.exchange);
	$("#ipo").text(FormateDate(data.ipo));
	$("#m-cap").text(formatCurrency(data.marketCapitalization));
	$("#c-name").text(data.name);
	$("#c-symbol").text(data.stock_symbol);
	$("#c-web").text(data.weburl);
	$("#c-web").attr("href", data.weburl);
	$("#logo").attr("src", data.logo);
	$("#industry").text(data.finnhubIndustry);
}

// format currency
function formatCurrency(currencyString) {
	let currency = parseFloat(currencyString).toFixed(0);
	let withCommas = Number(currency).toLocaleString("en");
	let finalformat = `\$${withCommas}M`;
	return finalformat;
}

// format date
function FormateDate(date) {
	let p = date.split(/\D/g);
	return [p[1], p[2], p[0]].join("/");
}
