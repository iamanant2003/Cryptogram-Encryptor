$(document).ready(function () {
  
  const toggleSwitch = $("#darkModeToggle");
  const body = $("body");

  toggleSwitch.change(function () {
    body.toggleClass("dark-mode");
  });
  $("input[name='action']").change(function () {
    $("#fileSelection").show();
  });

  $("input[name='file_type']").change(function () {
    $("#fileUpload").show();
  });

  $("form").submit(function (event) {
    event.preventDefault();

    let action = $("input[name='action']:checked").val();
    let fileType = $("input[name='file_type']:checked").val();
    let algorithm = $("#algorithm").val();
    let file = $("#file")[0].files[0];

    if (!file) {
      alert("Please select a file.");
      return;
    }

    let formData = new FormData();
    formData.append("action", action);
    formData.append("file_type", fileType);
    formData.append("algorithm", algorithm);
    formData.append("file", file);

    $.ajax({
      url: "/process_file",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        $("#result").show();
        $("#downloadLink").attr("href", response);
      },
      error: function (error) {
        console.log("Error:", error);
      }
    });
  });
  Dropzone.autoDiscover = false;

  $("#fileUpload").dropzone({
    url: "/process_file",
    paramName: "file",
    maxFilesize: 10,
    acceptedFiles: ".txt,.png,.jpg,.jpeg,.gif,.pdf",
    dictDefaultMessage: "Drag & drop your file here, or click to select",
    init: function () {
      this.on("addedfile", function (file) {
        console.log("File added:", file.name);
      });
      this.on("success", function (file, response) {
        $("#result").show();
        $("#downloadLink").attr("href", response);
      });
      this.on("error", function (file, response) {
        console.log("Error during file upload:", response);
      });
    }
  });
});
