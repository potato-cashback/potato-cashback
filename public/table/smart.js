var c1 = 0

document.querySelector("#smart")
.addEventListener('input', () => {
	let simple = document.querySelector('#simple')
    let advanced = document.querySelector('#advanced')
	let root = document.querySelector(":root");
    
    simple.style.display = (c1)?"inline":"none";
    advanced.style.display = (!c1)?"inline":"none";
	root.style.setProperty("--date", (!c1)?"table-cell":"none");

	if(!c1) updateTableAccordingToFilters()
	else {
		let date = document.querySelector("#date").value.split("-").reverse().join("/")
		tableFilterise([(o) => o["Дата"] == date])
	}

    c1 = !c1
});

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
	}else 
		filtered_data = [...data]

	if(filtered_data.length == 0)
		return [{"Нет данных":"за этот день"}]

	filtered_data.forEach(od => {
		cash_sum += new Number(od["Сумма"])
		cashback_sum += new Number(od["Кешбэк"])
	})
	filtered_data = filtered_data.sort(compare)
	filtered_data.push({
		"Имя":"",
		"Телефон":"",
		"Дата":" ",
		"Время":"Итого",
		"Сумма":cash_sum,
		"Кешбэк":cashback_sum
	},{
		"Имя":"",
		"Телефон":"",
		"Дата":" ",
		"Время":"Среднее",
		"Сумма":Math.round(cash_sum / filtered_data.length),
		"Кешбэк":Math.round(cashback_sum / filtered_data.length)
	})

	return filtered_data
}

const deleteElement = (qS) =>{
	el = document.querySelector(qS)
	el.parentNode.removeChild(el)
}





/////////

document.querySelectorAll(".option").forEach(row => {
	row.querySelector("input[type='checkbox']").addEventListener("change", (e) => {
		let parent = e.path[4]
		
		state = e.target.checked

		parent.querySelectorAll("td > input").forEach(input => {
			input.disabled = !state;
		})
		parent.style.color = (state)?"black":"#9b9b9b";
	})

	row.querySelector("input[type='checkbox']").click()
	row.querySelector("input[type='checkbox']").click()
})

const updateTableAccordingToFilters = () => {
	const newFilters = []
	document.querySelectorAll(".option").forEach(row =>{
		if(row.querySelector("input[type='checkbox']").checked){
			row.querySelectorAll("td > input").forEach((input, i) => {
				if(input.value){
					c = row.querySelector("td").innerText
					o = (i != 0)?"<=":">=";
					v = input.value

					if(c == 'Дата'){
						v = `${v.split("-").join("/")}`
						x = eval(`((o) => (o["${c}"]+"").split("/").reverse().join("/") ${o} "${v}")`)
					}else{
						v = `${v}`
						x = eval(`(o) => (o["${c}"]) ${o} "${v}"`)
					}
					if((v + "").length > 0)
						newFilters.push(x)
				}
			})
		}
	})

	tableFilterise(newFilters);
	return newFilters
}

document.querySelector("#adv_set").querySelectorAll("input").forEach(el => el.addEventListener("change", 
	() =>{
		updateTableAccordingToFilters()
	})
)