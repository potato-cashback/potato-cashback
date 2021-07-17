const login = () => {
	u = document.querySelector("#username").innerText
	p = document.querySelector("#password").innerText

	window.location.href = `/admin/${u}/${p}/menu`;
}