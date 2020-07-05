$(".table").on("click", "tr", function (evt) {
    // show edit form modal
    console.log(evt);
    if (evt.target.classList.contains("fas")) {
        return;
    } else {
        $("#edit-stock").modal("show");
        // change input value to the stock symbol of row selected. This input value is read only and the user cannot change this value
        $("input[name=stock_symbol]").val(evt.currentTarget.id);
        $("input[name=stock_num]").val($(this).find("td.stock_num").text());
    }
});

// $(".trash").hover(
//     function () {
//         $(".trash").toggleClass("far fas");
//     },
//     function () {
//         $(".trash").toggleClass("far fas");
//     }
// );

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
