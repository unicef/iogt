function validateFileUpload(fileInput, file_size_threshold) {
  if (!fileInput.files || !fileInput.files[0])
    return true;
  else {
    var file = fileInput.files[0];
    if (Math.round(file.size / 1024 / 1024) >= file_size_threshold)
      return confirm('The file you have uploaded exceeds ' + file_size_threshold + 'mb. This will ' +
          'prohibit access to the file in a low bandwidth setting, may restrict feature phone access, or violate ' +
          'your mobile network operator agreements. To reduce file size, try resizing and compressing your file. ' +
          'Do you want to continue?');
  }

  return true;
}
