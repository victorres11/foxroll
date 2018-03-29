function makeCsvActive() {
  var uploadCsvDiv = document.getElementById("uploadCsvFile_div");
  var uploads3Div = document.getElementById("uploadS3File_div");

  uploadCsvDiv.style.display = "block"
  uploads3Div.style.display = "none"
}

function makeS3Active() {
  var uploadCsvDiv = document.getElementById("uploadCsvFile_div");
  var uploads3Div = document.getElementById("uploadS3File_div");

  uploadCsvDiv.style.display = "none"
  uploads3Div.style.display = "block"
}

function processFile() {
  // This processes the file upon upload instead of requiring a separate
  // to do it.
  document.getElementById("uploadFile").submit();
}
