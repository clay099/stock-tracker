$(".table").on("click", "tr", function (evt) {
	// show edit form modal
	console.log(evt);
	if (evt.target.classList.contains("fas")) {
		return;
	} else if (evt.target.nodeName === "TH") {
		return;
	} else if (this.classList.contains("text-white")) {
		return;
	} else {
		$("#edit-stock").modal("show");
		// change input value to the stock symbol of row selected. This input value is read only and the user cannot change this value
		$("input[name=stock_symbol]").val(evt.currentTarget.id);
		$("input[name=stock_num]").val($(this).find("td.stock_num").text());
	}
});

$(".trash").hover(
	function () {
		$(this).toggleClass("far fas");
	},
	function () {
		$(this).toggleClass("far fas");
	}
);

$(".table").on("click", ".fas", function (evt) {
	// show edit form modal
	$("#delete-stock").modal("show");
	$("#symbol").text(evt.target.closest("tr").id);
	$("input[name=stock_symbol]").val(evt.target.closest("tr").id);
});

$(document).ready(function () {
	negativeValues();
});

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
