function validateFileUpload(fileInput, file_size_threshold) {
	if (!fileInput.files || !fileInput.files[0])
		return true;
	else {
		var file = fileInput.files[0];
		if (file.size >= file_size_threshold)
			return confirm('The file you have uploaded exceeds ' + Math.round(file_size_threshold / 1024 / 1024) + 'mb. ' +
				'This will prohibit access to the file in a low bandwidth setting, may restrict feature phone access, or ' +
				'violate your mobile network operator agreements. To reduce file size, try resizing and compressing your ' +
				'file. Do you want to continue?');
	}

	return true;
}

function validateFreeBasicsFileUpload(fileInput, file_size_threshold) {
	if (!fileInput.files || !fileInput.files[0])
		return true;
	else {
		var file = fileInput.files[0];
		if (file.size >= file_size_threshold)
			alert(`File size exceeds facebook free basics limit (${file_size_threshold / 1024}KB).`);
	}

	return true;
}

/** DOM Variables **/
const $selects = document.querySelectorAll('.js-select');
const $searchBtn = document.querySelector('.js-search-btn');
const $searchClose = document.querySelector('.js-search-close');
const $overlay = document.querySelector('.js-dark-overlay');
const $searchResult = document.querySelector('.js-search-result');


// $searchBtn.addEventListener('click', function (e) {
// 	e.preventDefault();
// 	this.parentElement.classList.add('active');
// 	$overlay.classList.add('active');
// 	$searchResult.classList.add('active');
// });

$searchClose.addEventListener('click', function (e) {
	e.preventDefault();
	this.parentElement.classList.remove('active');
	$overlay.classList.remove('active');
	$searchResult.classList.remove('active');
});


