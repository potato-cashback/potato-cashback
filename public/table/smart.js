var c1 = 0
var c2 = 0

document.querySelector("#smart")
.addEventListener('input', async () => {
    let simple = document.querySelector('#simple')
    let advanced = document.querySelector('#advanced')
    
    simple.style.display = (c1)?"inline":"none";
    advanced.style.display = (!c1)?"inline":"none";
    c1 = !c1
});

document.querySelector("#advanced > span").addEventListener("click", () => {
    let settings = document.querySelector('#adv_set')
	let root = document.querySelector(":root");

    settings.style.display = (!c2)?"block":"none";
	root.style.setProperty("--filter", (!c2)?"100%":"0");
    c2 = !c2
})

const filter = (data, filters) => {
	let cash_sum = 0;
	let cashback_sum = 0;

	if(filters.length != 0){ 
		filtered_data = data.filter(o => {
			// compare dates
            fit = true;
            filters.forEach(filter => {
                fit = fit && filter(o)
            })
			return fit
		})
		
		if(filtered_data.length == 0)
			return [{"Нет данных":"за этот день"}]

		filtered_data.forEach(od => {
			delete od["Дата"];
			cash_sum += new Number(od["Сумма"])
			cashback_sum += new Number(od["Кешбэк"])
		})
		filtered_data = filtered_data.sort(compare)
		filtered_data.push({
			"Имя":"",
			"Телефон":"",
			"Время":"Итого",
			"Сумма":cash_sum,
			"Кешбэк":cashback_sum
		},{
			"Имя":"",
			"Телефон":"",
			"Время":"Среднее",
			"Сумма":Math.round(cash_sum / filtered_data.length),
			"Кешбэк":Math.round(cashback_sum / filtered_data.length)
		})
	}else 
		filtered_data = data

	return filtered_data
}

var support = (function () {
	if (!window.DOMParser) return false;
	var parser = new DOMParser();
	try {
		parser.parseFromString('x', 'text/html');
	} catch(err) {
		return false;
	}
	return true;
})();

var stringToHTML = function (str) {

	// If DOMParser is supported, use it
	if (support) {
		var parser = new DOMParser();
		var doc = parser.parseFromString(str, 'text/html');
		return doc.body.childNodes[0];
	}

	// Otherwise, fallback to old-school method
	var dom = document.createElement('div');
	dom.innerHTML = str;
	return dom;

};

const addNewFilter = () => {
	const template =   `<div class="condition">
							<select name="column" class="column">
								<option value="" disabled selected>Свойство</option>
								<option>Сумма</option>
								<option>Кешбэк</option>
								<!-- <option>Дата</option>
								<option>Время</option> -->
							</select>
							<select name="operator" class="operator">
								<option value="==">равно</option>
								<option value=">=">более</option>
								<option value="<=">менее</option>
								<option value="!=">не равно</option>
							</select>
							<input type="number"></input>
							<button>
								<img src="https://img.icons8.com/fluent-systems-regular/24/000000/delete-sign--v1.png"/>
							</button>
						</div>`

	let el = document.querySelector("#adv_set > div.condition:nth-last-child(4)")
	el.after(stringToHTML(template))
}