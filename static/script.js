function togglePaymentOption() {
  var paymentMethod = document.getElementById("paymentMethod").value;
  var cardDetails = document.getElementById("cardDetails");
  var upiDetails = document.getElementById("upiDetails");

  if (paymentMethod === "card") {
      cardDetails.classList.add("active");
      upiDetails.classList.remove("active");
  } else if (paymentMethod === "upi") {
      cardDetails.classList.remove("active");
      upiDetails.classList.add("active");
  }
}