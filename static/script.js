// look at the below for when about has been added
// $("nav").on("click", "#about", function (e) {
// 	$(this).tab("show");
// });

$(document).ready(function () {
	let loc = location.href;
	if (loc === `http://localhost:5000/`) {
		$("#home").addClass("active");
	} else if (loc === "http://localhost:5000/user") {
		$("#portfolio").addClass("active");
	} else if (loc === "http://localhost:5000/user/settings") {
		$("#settings").addClass("active");
	}
});

$(document).on("click", function () {
	$("#password").attr({ type: "password" });
});

$("#search-btn").click(function (evt) {
	evt.preventDefault();
	const stock_symbol = $("#search-company").val().toUpperCase();
	window.location.pathname = `/company-details/${stock_symbol}`;
});
