class PhoneField { constructor(a, b = '+7(   )   –  –  ', c = ' ') { this.handler = a, this.mask = b, this.placeholder = c, this.setLength(), this.setValue(), this.start = this.placeHolderPosition() - 1, this.handler.addEventListener('focusin', () => { this.focused() }), this.handler.addEventListener('keydown', d => { this.input(d) }) } focused() { let a = this.placeHolderPosition(); this.handler.selectionStart = a, this.handler.selectionEnd = a } input(a) { if (this.isDirectionKey(a.key) || a.preventDefault(), this.isNum(a.key)) this.changeChar(a.key); else if (this.isDeletionKey(a.key)) if ('Backspace' === a.key) { let b = this.start; this.changeChar(this.placeholder, -1, b) } else this.changeChar(this.placeholder) } setLength() { this.handler.maxLength = this.mask.length } setValue() { this.handler.value = this.mask } isNum(a) { return !isNaN(a) && parseInt(+a) == a && !isNaN(parseInt(a, 10)) } isDeletionKey(a) { return 'Delete' === a || 'Backspace' === a } isDirectionKey(a) { return 'ArrowUp' === a || 'ArrowDown' === a || 'ArrowRight' === a || 'ArrowLeft' === a || 'Tab' === a } isPlaceholder(a) { return a == this.placeholder } placeHolderPosition() { return this.handler.value.indexOf(this.placeholder) } changeChar(a, b = 1, c = this.mask.length) { let d = this.handler.value, f; f = 0 < b ? this.handler.selectionStart : this.handler.selectionStart - 1; let g = ''; if (f === c) return !1; if (!this.isNum(d[f]) && !this.isPlaceholder(d[f])) do if (f += b, f === c) return !1; while (!this.isNum(d[f]) && !this.isPlaceholder(d[f])); g = this.replaceAt(d, f, a), this.handler.value = g, 0 < b && (f += b), this.handler.selectionStart = f, this.handler.selectionEnd = f } replaceAt(a, b, c) { return a.substring(0, b) + c + a.substring(++b) }}

function setCaretPosition(ctrl, pos) {
	// Modern browsers
	if (ctrl.setSelectionRange) {
		ctrl.focus();
		ctrl.setSelectionRange(pos, pos);
	
	// IE8 and below
	} else if (ctrl.createTextRange) {
		var range = ctrl.createTextRange();
		range.collapse(true);
		range.moveEnd('character', pos);
		range.moveStart('character', pos);
		range.select();
	}
}
var click = 0;

var ph = document.getElementById('phone');

ph.addEventListener("click", () =>{
	if(click == 0){
		let a = document.querySelector("#phone")
		a.classList.remove("new")
		new PhoneField(a, a.dataset.phonemask, a.dataset.placeholder)
	}
	click++;


	place = (ph.value.indexOf(" ") != -1)?ph.value.indexOf(" ") : ph.value.length
	setCaretPosition(ph, place);
})

ph.addEventListener("keyup", (e)=>{
	phone = ph.value.split(" ").join("").split("(").join("").split(")").join("").split("–").join("")
	if(e.key == "Enter"){
		sm.focus()
	}

	if(phone.length == 12){
		fetch(`/mongodb/phone/${phone}`)
		.then(r => {
			if(r.ok) return r.text()
			else return ""
		})
		.then(t => {
			if(t != ""){
				document.querySelector("#name").innerText = t;
				document.querySelector("#name").style.display = "block";
			}else{
				document.querySelector("#name").style.display = "none";
			}
		})
		.catch((err) => {
			document.querySelector("#name").innerText = "";
			document.querySelector("#name").style.display = "none";
		})
	}
	else{
		document.querySelector("#name").style.display = "none";
	}
})

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


const sendCashback = () => {
	
	document.querySelector("#submit").disabled = true;

	phone = document.querySelector("#phone").value.split(" ").join("").split("(").join("").split(")").join("").split("–").join("")
	var sum = document.querySelector("#sum").innerText


	if(phone.length == 12){
		url = `/mongodb/phone/${phone}/${sum}`
		console.log(url)
		loading()
		fetch(url)
		.then(r => r.text())
		.then(r =>{
			if(r == 'good')
				phonefound(sum)
			else
				error('Произошла Ошибка','', 'достигнут лимит начисления кешбэка')
		})
	}
	else
		error('Неверный Телефон')
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


const phonefound = (s)=>{
	s = s || "";
    document.querySelector("main").innerHTML = `
	<div id="phone-found">
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
	<div id="phone-read">
		<center>
			<h1>Поиск Телефона</h1>
			<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin:auto;background:#fff;display:block;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid"><circle stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" stroke-dasharray="164.93361431346415 56.97787143782138"><animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" dur="1s" values="0 50 50;360 50 50" keyTimes="0;1"></animateTransform></circle></svg>
		</center>
	</div>`
}

const error = (e1, e2, e3) =>{
	e1 = e1 || 'Произошла Ошибка'
	e2 = e2 || ''
	e3 = e3 || ''

	document.querySelector("main").innerHTML = `
	<div id="error">
		<center>
			${(e1!="")?`<h1>${e1}</h1>`:""}
			${(e2!="")?`<h2>${e2}</h2>`:""}
			${(e3!="")?`<h3>${e3}</h3>`:""}
			<svg xml:space="preserve" viewBox="0 0 100 100" y="0" x="0" xmlns="http://www.w3.org/2000/svg" id="圖層_1" version="1.1" width="200px" height="200px"><g class="ldl-scale" style="transform-origin: 50% 50%; transform: rotate(0deg);"><g class="ldl-ani"><g class="ldl-layer"><g class="ldl-ani" style="transform-origin: 50px 50px; animation: 1.11111s linear -0.833333s infinite normal forwards running static-56f88607-cb0b-42f6-81ec-1c50b6a84277;"><circle stroke-miterlimit="10" stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" style="stroke: rgb(51, 51, 51);"></circle></g></g><g class="ldl-layer"><g class="ldl-ani"><path fill="#e15b64" d="M68.536 38.536L57.065 50.007l11.458 11.458a5 5 0 1 1-7.072 7.071L49.993 57.078 39.205 67.867c-.977.976-2.256 1.464-3.536 1.464s-2.559-.488-3.536-1.464a5 5 0 0 1 0-7.071l10.789-10.789-11.458-11.458a5 5 0 1 1 7.071-7.071l11.458 11.458 11.471-11.471a5.001 5.001 0 0 1 7.072 7.071z" style="fill: rgb(225, 91, 100);"></path></g></g></g></g></g></g></g></svg>
		</center>
	</div>`

	setTimeout(() => {
		window.location.href = "/phone"
	}, 3000)
}