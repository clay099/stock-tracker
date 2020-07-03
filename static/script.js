$(".table").on("click", "tr", function (evt) {
	console.log(evt);
	// show edit form modal
	$("#edit-stock").modal("show");
	// change input value to the stock symbol of row selected. This input value is read only and the user cannot change this value
	$("input[name=stock_symbol]").val(evt.currentTarget.id);
	$("input[name=stock_num]").val($(this).find("td.stock_num").text());
});
