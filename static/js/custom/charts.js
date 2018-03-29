console.log("Hello from charts.js")

function switchDisplayForm() {
  var uploadDiv = document.getElementById("uploadFile_div");
  if (uploadDiv.style.display === "none") {
      uploadDiv.style.display = "block";
  } else {
      uploadDiv.style.display = "none";
  }
}
