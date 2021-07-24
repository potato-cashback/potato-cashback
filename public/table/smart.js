var count = 0

document.querySelector("#smart")
.addEventListener('input', async () => {
    let simple = document.querySelector('#simple')
    let advanced = document.querySelector('#advanced')
    
    simple.style.display = (count)?"inline":"none";
    advanced.style.display = (!count)?"inline":"none";
    count = !count
});

document.querySelector("#advanced").addEventListener("click", () => {
    console.log(1)
})