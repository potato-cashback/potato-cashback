let user = document.querySelector("#username")
let pass = document.querySelector("#password")
let subm = document.querySelector("#submit")

const login = () => {
	u = user.innerText
	p = pass.innerText

	window.location.href = `/admin/${u}/${p}/menu`;
}

user.addEventListener("keydown",(e)=>{
	if(e.key == 'Enter'){
		e.preventDefault()
		pass.focus()
	}
})
pass.addEventListener("keydown",(e)=>{
	if(e.key == 'Enter'){
		e.preventDefault()
		subm.click()
	}
})