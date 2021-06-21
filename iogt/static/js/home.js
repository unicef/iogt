
const displayBanner =()=> {
if (confirm("Do you want to save changes?") === true) {
   console.log("PWA saved successfully!")
   cache()
} else {
  console.log("PWA not downloaded!")
}
}