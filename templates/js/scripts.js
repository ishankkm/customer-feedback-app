$( document ).ready(function() {

  var jqxhr = $.getJSON( "http://127.0.0.1:5000/getAllMsg", function(data) {
    $('#msg_txt_1').val(data.firstAutomatedMsg);
    $('#msg_txt_2').val(data.positiveRes);
    $('#msg_txt_3').val(data.negativeRes);
  })

});

function updateMsg(position) {
  $.ajax({
  type: "POST",
  url: "http://127.0.0.1:5000/updateMsg",
  data: data,
  success: function() {console.log("success")},
  dataType: "json"
});
}





function toggleEditable(position) {

  var txt_id = "#msg_txt_" + position.toString()
  var but_id = "#msg_but_" + position.toString()

  if($(but_id).text() == "Edit") {
    $(but_id).text("Done");
    $(txt_id).removeClass("form-control-plaintext");
    $(txt_id).addClass("form-control");
  } else if($(but_id).text() == "Done") {
    $(but_id).text("Edit");
    $(txt_id).removeClass("form-control");
    $(txt_id).addClass("form-control-plaintext");
  }

}
