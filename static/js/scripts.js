$( document ).ready(function() {

  var jqxhr = $.getJSON( window.location.origin + "/getAllMsg", function(data) {
    $('#msg_txt_1').val(data.firstAutomatedMsg);
    $('#msg_txt_2').val(data.positiveRes);
    $('#msg_txt_3').val(data.negativeRes);
  })

});

$(function() {
  $('#sendForm').on('submit', function(e){
    sendMessage();
    e.preventDefault();
  });
});

function updateMsg(position) {
  msgName = ["firstAutomatedMsg", "positiveRes", "negativeRes"]
  data = {
    "msgName" : msgName[position - 1],
    "message" : $('#msg_txt_'+position.toString()).val()
  }

  $.ajax({
    type: "POST",
    url: window.location.origin + "/updateMsg",
    data: JSON.stringify(data),
    success: function(res) {console.log(res)},
		dataType: "json",
		contentType: "application/json"
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
    updateMsg(position)
    $(but_id).text("Edit");
    $(txt_id).removeClass("form-control");
    $(txt_id).addClass("form-control-plaintext");
  }

}

function sendMessage() {

  phoneNumber = $('#phoneNumber').val().replace(/\s/g,'').replace(/-/g,'');
  productType = $('input[name=options]:checked').val();
  custName = $('#custName').val();
  data = {
    "phoneNumber": phoneNumber,
    "productType": productType,
    "custName": custName
  }

  $.ajax({
    type: "POST",
    url: window.location.origin + "/sendMsg",
    data: JSON.stringify(data),
    success: function(res) {alert(res.message);},
		dataType: "json",
		contentType: "application/json"
  }).then(function(res){
    // alert("Message was sent")
    console.log(res)
  });
}
