const BASE_URL = "http://localhost:5000/api";

// ************company details functions****************
// company details modal
$("#portfolio-table").on("click", "tr", async function (evt) {
	// show edit form modal
	if (evt.target.classList.contains("fas")) {
		return;
	} else if (evt.target.nodeName === "TH") {
		return;
	} else if (this.classList.contains("text-white")) {
		return;
	} else {
		let stock_symbol = $(this).closest("tr")[0].id;
		const returnedDetails = await axios.post(`${BASE_URL}/company-details`, { stock_symbol });
		fillCompanyDetails(returnedDetails);
		$("#company-details").modal("show");
	}
});

// fill company details modal
function fillCompanyDetails(data) {
	const base = data.data.stock;
	$("#country").text(base.country);
	$("#currency").text(base.currency);
	$("#exchange").text(base.exchange);
	$("#ipo").text(FormateDate(base.ipo));
	$("#m-cap").text(formatCurrency(base.marketCapitalization));
	$("#c-name").text(base.name);
	$("#c-symbol").text(base.stock_symbol);
	$("#c-web").text(base.weburl);
	$("#c-web").attr("href", base.weburl);
	$("#logo").attr("src", base.logo);
	$("#industry").text(base.finnhubIndustry);
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

// ************edit stock functions****************
// edit stock modal
$("#portfolio-table").on("click", "th", function (evt) {
	// show edit form modal
	if (evt.target.classList.contains("fas")) {
		return;
	} else if (evt.target.parentElement.parentElement.nodeName === "THEAD") {
		return;
	} else if (this.classList.contains("text-white")) {
		return;
	} else {
		$("#edit-stock").modal("show");
		// change input value to the stock symbol of row selected. This input value is read only and the user cannot change this value
		$("#edit-stock").find("input[name=stock_symbol]").val(evt.currentTarget.parentElement.id);
		$("#edit-stock")
			.find("input[name=stock_num]")
			.val($(evt.target.parentElement).find("td.stock_num").text());
	}
});

// change trash color
$(".trash").hover(
	function () {
		$(this).toggleClass("far fas");
	},
	function () {
		$(this).toggleClass("far fas");
	}
);

// delete stock modal
$("#portfolio-table").on("click", ".fa-trash-alt", function (evt) {
	// show delete stock form modal
	$("#delete-stock").modal("show");
	$("#symbol").text(evt.target.closest("tr").id);
	$("input[name=stock_symbol]").val(evt.target.closest("tr").id);
});

// sort table
$("#portfolio-table").on("click", ".fa-sort", function (evt) {
	val = evt.target.closest("th").innerText;
	sorted = $(evt.target.closest("th")).hasClass("ascending");
	let $table = $("table > tbody > tr");
	let arr = [];
	fillArray($table, arr);
	if (val === "Stock Symbol ") {
		let identification = "id";
		sortSymbol(evt, sorted, arr, identification);
	} else if (val === "Change % ") {
		let identification = "percent";
		sortChangePercent(evt, sorted, arr, identification);
	} else if (val === "Change $ ") {
		let identification = "currency";
		sortChangeDol(evt, sorted, arr, identification);
	}
	arr = [];
});

function fillArray($table, arr) {
	$table.each(function (i, row) {
		let $row = $(row);

		if ($row.hasClass("sort")) {
			arr.push($row);
		}
	});
}

function sortSymbol(evt, sorted, arr, identification) {
	if (sorted === false) {
		smallSort(arr, identification);
		$(evt.target.closest("th")).addClass("ascending");
	} else {
		largeSort(arr, identification);
		$(evt.target.closest("th")).removeClass("ascending");
	}
}

function sortChangePercent(evt, sorted, arr, identification) {
	if (sorted === false) {
		smallSort(arr, identification);
		$(evt.target.closest("th")).addClass("ascending");
	} else {
		largeSort(arr, identification);
		$(evt.target.closest("th")).removeClass("ascending");
	}
}

function sortChangeDol(evt, sorted, arr, identification) {
	if (sorted === false) {
		smallSort(arr, identification);
		$(evt.target.closest("th")).addClass("ascending");
	} else {
		largeSort(arr, identification);
		$(evt.target.closest("th")).removeClass("ascending");
	}
}

function smallSort(arr, identification) {
	arr.sort(function (a, b) {
		let A;
		let B;
		if (identification === "id") {
			A = $(a)[0].id;
			B = $(b)[0].id;
		} else if (identification === "percent") {
			A = $(a)[0].children[8].textContent;
			A = A.replace(/\%/g, "");
			A = A.trim();
			B = $(b)[0].children[8].textContent;
			B = B.replace(/\%/g, "");
			B = B.trim();
		} else if (identification === "currency") {
			A = $(a)[0].children[9].textContent;
			A = A.trim();
			A = parseFloat(A.replace(/\$|,/g, ""));
			B = $(b)[0].children[9].textContent;
			B = B.trim();
			B = parseFloat(B.replace(/\$|,/g, ""));
		} else {
			return;
		}

		if (A > B) {
			return 1;
		}
		if (A < B) {
			return -1;
		}
		return 0;
	});
	$.each(arr, function (index, row) {
		$(row).insertBefore($("table > tbody tr.bg-info").closest("tr"));
	});
}

function largeSort(arr, identification) {
	arr.sort(function (a, b) {
		let A;
		let B;
		if (identification === "id") {
			A = $(a)[0].id;
			B = $(b)[0].id;
		} else if (identification === "percent") {
			A = $(a)[0].children[8].textContent;
			A = A.replace(/\%/g, "");
			A = A.trim();
			B = $(b)[0].children[8].textContent;
			B = B.replace(/\%/g, "");
			B = B.trim();
		} else if (identification === "currency") {
			A = $(a)[0].children[9].textContent;
			A = A.trim();
			A = parseFloat(A.replace(/\$|,/g, ""));
			B = $(b)[0].children[9].textContent;
			B = B.trim();
			B = parseFloat(B.replace(/\$|,/g, ""));
		} else {
			return;
		}

		if (A < B) {
			return 1;
		}
		if (A > B) {
			return -1;
		}
		return 0;
	});
	$.each(arr, function (index, row) {
		$(row).insertBefore($("table > tbody tr.bg-info").closest("tr"));
	});
}

function negativeValues() {
	let $table = $("table > tbody > tr");

	$table.each((i, row) => {
		let $row = $(row),
			$startPrice = $row.find(".start_stock_price")[0],
			$currPrice = $row.find(".curr_stock_price")[0],
			$startVal = $row.find(".start_stock_value")[0],
			$currVal = $row.find(".curr_stock_value")[0],
			$percentChange = $row.find(".percent_change")[0],
			$dolChange = $row.find(".dol_change")[0];

		let selected = [$startPrice, $currPrice, $startVal, $currVal, $percentChange, $dolChange];

		tableLoop(selected);
		portfolioVal();
	});
}

function tableLoop(arr) {
	if (arr[0] != undefined)
		if (arr[0].innerText > arr[1].innerText) {
			arr.forEach((cell) => {
				let $cell = $(cell);
				$cell.addClass("negativeValue");
			});
		}
}

function portfolioVal() {
	let start = $("#total_start_val")[0].innerText;
	let curr = $("#total_curr_val")[0].innerText;
	start = parseFloat(start.replace(/\$|,/g, ""));
	curr = parseFloat(curr.replace(/\$|,/g, ""));
	if (start > curr) {
		$("#portfolio_val").addClass("negativeValue");
	}
}

$(document).ready(function () {
	negativeValues();
});
