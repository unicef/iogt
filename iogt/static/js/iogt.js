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

!function () {
	var e = document.querySelectorAll(".js-select"),
		t = document.querySelector(".js-search-btn"),
		c = document.querySelector(".js-search-close"),
		s = document.querySelector(".js-dark-overlay"),
		n = document.querySelector(".js-search-result");
	e.forEach((function (e) {
		var t = e.querySelectorAll(".select__option");
		e.addEventListener("click", (function () {
			this.classList.toggle("active");
		})), t.forEach((function (c) {
			c.addEventListener("click", (function () {
				e.querySelector(".select__selected p").innerText = this.innerText, t.forEach((function (e) {
					e.classList.remove("select__option--selected");
				})), this.classList.add("select__option--selected");
			}));
		}));
	})), t.addEventListener("click", (function (e) {
		e.preventDefault(), this.parentElement.classList.add("active"), s.classList.add("active"), n.classList.add("active");
	})), c.addEventListener("click", (function (e) {
		e.preventDefault(), this.parentElement.classList.remove("active"), s.classList.remove("active"), n.classList.remove("active");
	}));
}();
