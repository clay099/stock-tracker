let loc = location.href;
let ALL_STOCKS = [];

let BASE_URL = "https://cw-stock-tracker.herokuapp.com";
let BASE_URL_API = `${BASE_URL}/api`;
if (loc.includes("localhost")) {
	BASE_URL = "http://localhost:5000";
	BASE_URL_API = `${BASE_URL}/api`;
} else if (loc.includes("127")) {
	BASE_URL = "http://127.0.0.1:5000";
	BASE_URL_API = `${BASE_URL}/api`;
}

$(document).ready(function () {
	let loc = location.href;
	if (loc === `${BASE_URL}/`) {
		$("#home").addClass("active");
	} else if (loc === `${BASE_URL}/user`) {
		$("#portfolio").addClass("active");
	} else if (loc === `${BASE_URL}/user/settings`) {
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
	let d = newsArticle.datetime;
	return `
    <div class="col mb-4 ">
        <div class="card shadow-sm mb-5 bg-white rounded mx-auto">
            <img src="${newsArticle.image}" class="card-img-top"
            onerror="this.onerror=null;this.src='/static/images/image-not-provided.jpg';" alt="image not provided">
            <div class="card-body">
                <h5 class="card-title">${newsArticle.headline}</h5>
                <small class="text-muted">Last updated ${new Date(
					d * 1000
				).toLocaleDateString()}</small>
                <p class="card-text">
                    ${newsArticle.summary}
                </p>
                <a href="${newsArticle.url}" target="_blank" class="card-link">See Full Article</a>
            </div>
        </div>
    </div>
    `;
}

// make variable empty string
let $searchVal = "";
// send request to
async function generateAutoComplete(name) {
	let resp = await axios.get(`${BASE_URL_API}/_stock-autocomplete`, {
		params: {
			name,
		},
	});
	ALL_STOCKS = resp.data;
	console.log(ALL_STOCKS);
}

$("#search-company").on("keyup", () => {
	let $searchComp = $("#search-company");
	$searchVal = $searchComp.val().toUpperCase();
	if ($searchVal.length == 2) {
		generateAutoComplete($searchVal);
	}
	// fix this function
	$searchComp.autocomplete({
		minLength: 3,
		source: function (req, res) {
			res(
				$.map(ALL_STOCKS, (obj, key) => {
					return {
						label: obj.description,
						val: obj.symbol,
					};
				})
			);
		},
	});
	//
});
