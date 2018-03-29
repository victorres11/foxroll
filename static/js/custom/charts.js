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
