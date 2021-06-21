
const displayBanner =()=> {
if (confirm("Do you want to save changes?") === true) {
   console.log("PWA saved successfully!")
} else {
  console.log("PWA not downloaded!")
}
}