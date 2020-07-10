// fill company details
function fillCompanyDetails(data) {
	$("#country").text(data.country);
	$("#currency").text(data.currency);
	$("#exchange").text(data.exchange);
	$("#ipo").text(FormateDate(data.ipo));
	$("#m-cap").text(formatCurrencyB(data.marketCapitalization));
	$("#c-name").text(data.name);
	$("#c-symbol").text(data.stock_symbol);
	$("#c-web").text(data.weburl);
	$("#c-web").attr("href", data.weburl);
	$("#logo").attr("src", data.logo);
	$("#industry").text(data.finnhubIndustry);
}

// format currency
function formatCurrency(currencyString) {
	let format = Number(currencyString).toLocaleString("en-IN", {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});
	let finalformat = `$${format}`;
	return finalformat;
}

function formatCurrencyB(currencyString) {
	let value = currencyString * 1000;
	let billions = (value / 1000000).toLocaleString(undefined, {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});
	let finalformat = `$${billions}B`;
	return finalformat;
}

// format date
function FormateDate(date) {
	let p = date.split(/\D/g);
	return [p[1], p[2], p[0]].join("/");
}
