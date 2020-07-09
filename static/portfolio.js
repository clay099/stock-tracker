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
		// see stock_details.js
		fillCompanyDetails(returnedDetails.data.stock);
		$("#company-details").modal("show");
	}
});

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

// ************delete stock functions****************
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

// ************sort table functions****************
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

// ************edit stock color functions****************
// reviews table and turns cells text-color red if change in stock value is negative
function negativeValues() {
	let $table = $("table > tbody > tr");

	// for each row run the functions
	$table.each((i, row) => {
		// select values
		let $row = $(row),
			$startPrice = $row.find(".start_stock_price")[0],
			$currPrice = $row.find(".curr_stock_price")[0],
			$startVal = $row.find(".start_stock_value")[0],
			$currVal = $row.find(".curr_stock_value")[0],
			$percentChange = $row.find(".percent_change")[0],
			$dolChange = $row.find(".dol_change")[0];

		// create array of cells to change color
		let selected = [$startPrice, $currPrice, $startVal, $currVal, $percentChange, $dolChange];

		// push each rows array cells
		tableLoop(selected);
	});
	// runs for total portfolio value (last line)
	portfolioVal();
}

// runs for each row
function tableLoop(arr) {
	// checks if current val is less then initial val
	if (arr[0] != undefined)
		if (arr[0].innerText > arr[1].innerText) {
			// if less then initial val select cell and add class negative value (turns text red & bold)
			arr.forEach((cell) => {
				let $cell = $(cell);
				$cell.addClass("negativeValue");
			});
		}
}
// checks if current val is less then initial val
function portfolioVal() {
	let start = $("#total_start_val")[0].innerText;
	let curr = $("#total_curr_val")[0].innerText;
	start = parseFloat(start.replace(/\$|,/g, ""));
	curr = parseFloat(curr.replace(/\$|,/g, ""));
	if (start > curr) {
		$("#portfolio_val").addClass("negativeValue");
	}
}

// loads on page ready
$(document).ready(function () {
	negativeValues();
});

// **********see detailed company view functions****************
$("#dcv").click(function (evt) {
	evt.preventDefault();
	const stock_symbol = $("#c-symbol").text();
	window.location.pathname = `/company-details/${stock_symbol}`;
});
