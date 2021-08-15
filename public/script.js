async function getJson() {
    let request = await fetch('admin/admin/admin/getJSON')
    let data;
    if (request.ok) {
        data = JSON.parse(await request.text())
    } else {
        alert("Couldn't retrive JSON")
    }
    return data
}

async function showQR() {
    let data = await getJson()
    console.log(data)
    let qr = document.querySelector("#qr");
    qr.style.display = (data['show_qr'] ? "block" : "none");
}
showQR()