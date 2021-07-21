var sm = document.querySelector("#sum");
sm.addEventListener('keydown', (e)=>{
	if('1234567890'.split('').includes(e.key) || e.key == 'Backspace'){
		if(sm.innerHTML == 0 && e.key != 'Backspace') 
			sm.innerHTML = "";
		else if(sm.innerHTML == 0 && e.key == 'Backspace')
			e.preventDefault()
		else if(sm.innerHTML.length == 1 && e.key == 'Backspace'){
			e.preventDefault()
			sm.innerHTML = 0;
		}
		else if(sm.innerHTML.length >= 5 && e.key !='Backspace')
			e.preventDefault()
	}else if(e.key == 'Enter'){
		e.preventDefault()
		document.querySelector("#submit").click()
	}else{
		e.preventDefault()
	}
})
sm.addEventListener('keyup', (e)=>{
	if(sm.innerHTML == 0){
		sm.innerHTML = 0;
		var range = document.createRange()
		var sel = window.getSelection()
			
		range.setStart(sm, 1)
		range.collapse(true)
		
		sel.removeAllRanges()
		sel.addRange(range)
	}
})
sm.addEventListener('click', (e)=>{
	if(sm.innerHTML == 0){
		sm.innerHTML = 0;
		var range = document.createRange()
		var sel = window.getSelection()
			
		range.setStart(sm, 1)
		range.collapse(true)
		
		sel.removeAllRanges()
		sel.addRange(range)
	}
})


const createQR = (data) => {
    let template = `<img src='https://chart.googleapis.com/chart?cht=qr&chl=${data}&chs=70x70&choe=UTF-8&chld=L|2' alt='qr code' id='qr-image'>`
    return template;
}

const create = () =>{
	let time = new Date() - 0
    let data = {
        sum:document.querySelector("#sum").innerHTML - 0,
        date: time,
    }
	console.log(window.location.origin + "/api/create/"+time)
	console.log(window.location.origin + "/api/react/"+time)
	console.log(window.location.origin + "/api/response/"+time)
	console.log(window.location.origin + "/api/cancel/"+time)

    document.querySelector("main").innerHTML = `
	<div id="qr">
		<center>
			<br>
			<h1>QR на ${data.sum} ₸</h1>
			${createQR(JSON.stringify(data)) + script(data.date)}
		</center>
	</div>
	`
	fetch("/api/create/"+time)
}

const script = (id) =>{
	var q = 1
	let template = `const interval = setInterval(()=>{
			findFile("${id}")
			.then(json => {
				console.log(json)
				if(json.status == "ok" && json.data == "")
					console.log("good")
				else if(json.status == "ok" && json.data == 0 && q == 1) {
					loading()
					q--;
				}
				else if(json.status == "ok" && json.data == 1){
					clearInterval(interval); 
					qrfound(${document.querySelector("#sum").innerHTML - 0})
				}
				else if(json.status == "ok" && json.data == 2){
					clearInterval(interval); 
					qrcanceled()
				}
				else console.log("not found")
			})
		}, 2000)`;
	eval(template)
	return `<script>${template}</script>`
}

const findFile = async (id) =>{
	return await fetch("/ids/" + id)
	.then(res => res.json())
}

const cashback = (s) => {
	let coef = [0.06, 0.11]
    let res = 0
    
	if(s >= 5000)
		res = coef[1]
    else if(s >= 3000)
		res = coef[0]
    return res * s
}


const qrfound = (s)=>{
	s = s || "";

    document.querySelector("main").innerHTML = `
	<div id="qr-found">
		<center>
			<h1>Кешбэк Начислен</h1>
			${(s!="")?`<h1>${Math.floor(cashback(s))} ₸</h1>`:""}
			<svg xml:space="preserve" viewBox="0 0 100 100" y="0" x="0" xmlns="http://www.w3.org/2000/svg" id="圖層_1" version="1.1" width="200px" height="200px"><g class="ldl-scale" style="transform-origin: 50% 50%; transform: rotate(0deg);"><g class="ldl-ani"><g class="ldl-layer"><g class="ldl-ani" style="transform-origin: 50px 50px; animation: 1.11111s linear -0.833333s infinite normal forwards running static-56f88607-cb0b-42f6-81ec-1c50b6a84277;"><circle stroke-miterlimit="10" stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" style="stroke: rgb(51, 51, 51);"></circle></g></g><g class="ldl-layer"><g class="ldl-ani"><g><g class="ldl-layer"><g class="ldl-ani" style="transform-origin: 50px 50px; animation: 1.11111s linear -1.11111s infinite normal forwards running static-56f88607-cb0b-42f6-81ec-1c50b6a84277;"><path fill="#abbd81" d="M47.3 66.4L73.7 40c1.8-1.8 1.8-4.6 0-6.4-1.8-1.8-4.6-1.8-6.4 0L44.1 56.8 32.7 45.4c-1.8-1.8-4.6-1.8-6.4 0-1.8 1.8-1.8 4.6 0 6.4l14.6 14.6c.9.9 2 1.3 3.2 1.3s2.3-.5 3.2-1.3z" style="fill: rgb(171, 189, 129);"></path></g></g></g></g></g></g></g></svg>
			<p><a href="/">Вернуться обратно</a></p>
		</center>
	</div>`
	
	setTimeout(() => {
		window.location.href = "/"
	}, 5000)
}

const loading = ()=>{
    document.querySelector("main").innerHTML = `
	<div id="qr-read">
		<center>
			<h1>QR прочитан</h1>
			<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin:auto;background:#fff;display:block;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid"><circle stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" stroke-dasharray="164.93361431346415 56.97787143782138"><animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" dur="1s" values="0 50 50;360 50 50" keyTimes="0;1"></animateTransform></circle></svg>
		</center>
	</div>`
}

const qrcanceled = () =>{
	document.querySelector("main").innerHTML = `
	<div id="qr-canceled">
		<center>
			<h1>QR отменен</h1>
			<svg xml:space="preserve" viewBox="0 0 100 100" y="0" x="0" xmlns="http://www.w3.org/2000/svg" id="圖層_1" version="1.1" width="200px" height="200px"><g class="ldl-scale" style="transform-origin: 50% 50%; transform: rotate(0deg);"><g class="ldl-ani"><g class="ldl-layer"><g class="ldl-ani" style="transform-origin: 50px 50px; animation: 1.11111s linear -0.833333s infinite normal forwards running static-56f88607-cb0b-42f6-81ec-1c50b6a84277;"><circle stroke-miterlimit="10" stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" style="stroke: rgb(51, 51, 51);"></circle></g></g><g class="ldl-layer"><g class="ldl-ani"><path fill="#e15b64" d="M68.536 38.536L57.065 50.007l11.458 11.458a5 5 0 1 1-7.072 7.071L49.993 57.078 39.205 67.867c-.977.976-2.256 1.464-3.536 1.464s-2.559-.488-3.536-1.464a5 5 0 0 1 0-7.071l10.789-10.789-11.458-11.458a5 5 0 1 1 7.071-7.071l11.458 11.458 11.471-11.471a5.001 5.001 0 0 1 7.072 7.071z" style="fill: rgb(225, 91, 100);"></path></g></g></g></g></g></g></g></svg>
		</center>
	</div>`

	setTimeout(() => {
		window.location.href = "/qr"
	}, 1000)
}