function validateFileUpload(fileInput) {
  if (!fileInput.files || !fileInput.files[0])
    return true;
  else {
    var file = fileInput.files[0];
    if (file.size >= 9437184)
      return confirm('The file you have uploaded exceeds 9mb. This will prohibit access to the file in a low ' +
          'bandwidth setting, may restrict feature phone access, or violate your mobile network operator ' +
          'agreements. To reduce file size, try resizing and compressing your file.');
  }

  return true;
}
