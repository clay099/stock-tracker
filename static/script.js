const BASE_URL = "http://localhost:5000/api";

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

function generateNewsHTML(newsArticle) {
	return `
    <div class="col mb-4 ">
        <div class="card shadow-sm mb-5 bg-white rounded mx-auto">
            <img src="${newsArticle.image}" class="card-img-top"
            onerror="this.onerror=null;this.src='/static/images/image-not-provided.jpg';" alt="image not provided">
            <div class="card-body">
                <h5 class="card-title">${newsArticle.headline}</h5>
                <p class="card-text">
                    ${newsArticle.summary}
                </p>
                <a href="${newsArticle.url}" class="card-link">See Full Article</a>
            </div>
        </div>
    </div>
    `;
}
