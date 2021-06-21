
function displayBanner() {
if (confirm("Install this website as an app on your device?") === true) {
  const res= cache()
  if(res) {
    console.log(res)
    alert("Your app is now ready to install. If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen. If using Android choose 'Add to home screen' and you should be all set!")
  }
  else {
    alert('Something went wrong. Can you try again using the download website button?')
  }
} 
}