//<script>
//function setNotificationPref(choice) {
//    alert(choice)
//  fetch("{% url 'save_notification_preference' %}", {
//    method: "POST",
//    headers: {
//      "X-CSRFToken": "{{ csrf_token }}",
//      "Content-Type": "application/json",
//    },
//    body: JSON.stringify({ choice: choice }),
//  }).then((res) => {
//    if (res.ok) {
//        console.log('response', res)
//      document.getElementById("notif-banner").style.display = "none";
//    }
//  });
//}
//</script>