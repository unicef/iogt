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
