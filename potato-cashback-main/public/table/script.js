let t = new Date()
let maxT = t.getFullYear() + "-" + (""+(t.getMonth()+ 1)).padStart(2, '0') + "-" + (""+t.getDate()).padStart(2, '0')
document.querySelector("#date").max = maxT
document.querySelector("#date").value = maxT


const compare = (a, b) =>{
	checkbox = 2* document.querySelector("#sort").checked - 1
	return a["Время"].localeCompare(b["Время"]) * (-checkbox)
}


const makeTable = (data) =>{
	let output = ""

	output += ("<table border==\"1\"><tr>");
	for (key in data[0]) {
		if(key != "Телефон")
			output += ('<td>' + key + '</td>');
	}
	output += ("</tr>");


	for (let i = 0; i < data.length; i++) {
		output += ('<tr>');
		for (key in data[i]) {
			if(key == "Сумма" || key == "Кешбэк"){
				output += `<td>${data[i][key].toLocaleString('ru')}</td>`;
			}else if(key == "Имя" && i != data.length-2 && i!=data.length-1){
				output += `
				<td class="name">
					${data[i][key]}
					<div class="phone">
						${data[i]["Телефон"]}
					</div>
				</td>`;
			}else if(key != "Телефон"){
				output += `<td>${data[i][key]}</td>`;
			}
		}
		output += ('</tr>');
	}
	output += ("</table>");
	
	return output;
}

const filter_data = (data, date) => {
	let cash_sum = 0;
	let cashback_sum = 0;

	if(date != null){ 
		filtered_data = data.filter(o => {
			// compare dates
			return date == o["Дата"]
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



const dope = fetch("/mongodb")
.then(res => res.text())
.then(res => res.split("False").join("false").split("True").join("true").split("'").join('"').split("None").join('"None"').split(/ObjectId\("\S*"\)/gm).join('""'))
.then(JSON.parse)
.then(r =>{
	console.log(r)
	let output = [];
	r.forEach(person =>{
		person.operations.forEach(operation =>{
			if(operation.details == "кешбэк"){
				output.push({
					"Имя":person.name || person.phone,
					"Телефон":person.phone,
					"Дата":operation.date,
					"Время":operation.time,
					"Сумма":operation.sum,
					"Кешбэк":operation.cashback + (operation.cashback < 0)
				})
			}
		})   
	})

	clone = JSON.parse(JSON.stringify(output))

	let date = document.querySelector("#date").value.split("-").reverse().join("/")
	document.querySelector("center").innerHTML = makeTable(filter_data(clone, date))

	return output
}).catch((err) =>{
	console.log(err)

	document.querySelector("main").innerHTML = `
	<div id="error">
		<center>
			<h1>Произошла Ошибка</h1>
			<svg xml:space="preserve" viewBox="0 0 100 100" y="0" x="0" xmlns="http://www.w3.org/2000/svg" id="圖層_1" version="1.1" width="200px" height="200px"><g class="ldl-scale" style="transform-origin: 50% 50%; transform: rotate(0deg);"><g class="ldl-ani"><g class="ldl-layer"><g class="ldl-ani" style="transform-origin: 50px 50px; animation: 1.11111s linear -0.833333s infinite normal forwards running static-56f88607-cb0b-42f6-81ec-1c50b6a84277;"><circle stroke-miterlimit="10" stroke-width="8" stroke="#333" fill="none" r="40" cy="50" cx="50" style="stroke: rgb(51, 51, 51);"></circle></g></g><g class="ldl-layer"><g class="ldl-ani"><path fill="#e15b64" d="M68.536 38.536L57.065 50.007l11.458 11.458a5 5 0 1 1-7.072 7.071L49.993 57.078 39.205 67.867c-.977.976-2.256 1.464-3.536 1.464s-2.559-.488-3.536-1.464a5 5 0 0 1 0-7.071l10.789-10.789-11.458-11.458a5 5 0 1 1 7.071-7.071l11.458 11.458 11.471-11.471a5.001 5.001 0 0 1 7.072 7.071z" style="fill: rgb(225, 91, 100);"></path></g></g></g></g></g></g></g></svg>
			<details>
				<summary>
					Описание Ошибки
				</summary>
				<code>
					${err}
				</code>
			</details>
		</center>
	</div>`	
})

document.querySelector("#date")
.addEventListener('input', async () => {
	let date = document.querySelector("#date").value.split("-").reverse().join("/")
	let dataS = await dope;
	
	clone = JSON.parse(JSON.stringify(dataS))

	document.querySelector("center").innerHTML = makeTable(filter_data(clone, date))
});

document.querySelector("#sort")
.addEventListener('input', async () => {
	let date = document.querySelector("#date").value.split("-").reverse().join("/")
	let dataS = await dope;
	
	clone = JSON.parse(JSON.stringify(dataS))

	document.querySelector("center").innerHTML = makeTable(filter_data(clone, date))
});