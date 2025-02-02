$(document).ready(function() {
    $('#encryptBtn').click(function() {
      $('#fileSelection').show();
      $('#decryptBtn').hide();
    });
  
    $('#decryptBtn').click(function() {
      $('#fileSelection').show();
      $('#encryptBtn').hide();
    });
  
    $('#textFileBtn').click(function() {
      $('#fileUpload').show();
      $('#fileSelection').hide();
      $('#processBtn').attr('data-action', 'encrypt').attr('data-type', 'text');
    });
  
    document.addEventListener("DOMContentLoaded", function () {
      const toggleSwitch = document.getElementById("darkModeToggle");
      const body = document.body;
  
      toggleSwitch.addEventListener("change", function () {
          body.classList.toggle("dark-mode");
      });
  });
  
  
    $('#imageFileBtn').click(function() {
      $('#fileUpload').show();
      $('#fileSelection').hide();
      $('#processBtn').attr('data-action', 'encrypt').attr('data-type', 'image');
    });
  
    $('#processBtn').click(function() {
      var action = $(this).data('action');
      var file_type = $(this).data('type');
      var file = $('#fileInput')[0].files[0];
  
      var formData = new FormData();
      formData.append('action', action);
      formData.append('file_type', file_type);
      formData.append('file', file);
  
      $.ajax({
        url: '/process_file',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
          $('#result').show();
          $('#downloadLink').attr('href', response);
        },
        error: function(error) {
          console.log(error);
        }
      });
    });
  });
  