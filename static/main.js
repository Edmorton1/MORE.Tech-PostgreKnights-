let showModal = true;

const buttonOpenModal = document.getElementById("open-modal");
buttonOpenModal.addEventListener("click", () => {
  const modalWrapper = document.getElementById("modal-wrapper");
  modalWrapper.style.display = "block";
});

const modalWrapper = document.getElementById("modal-wrapper");
modalWrapper.addEventListener("click", () => {
  modalWrapper.style.display = "none";
});

const modal = document.getElementById("modal");
modal.addEventListener("click", (event) => {
  event.stopPropagation();
});

const form = document.getElementById("form-input");
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const data = { query: formData.get("query") };

  console.log(data);

  /**@type {AnalyzeResult} */
  const response = await fetch("http://localhost:3000", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((data) => data.json())
    .catch((err) => console.error(err));

  console.log(response);
  modal.innerHTML = `<div>
      <div>Анализ запроса ${response.post_analyze.query}</div>
      <div>Время: ${response.post_analyze.time}</div>
      <div>Стоимость: ${response.post_analyze.total_cost}</div>
      <div>Объём сканируемых данных: ${response.post_analyze.volume}</div>
      <div>Пре-анализ запроса</div>
			${response.pre_analyze.map(
        (e) =>
          `<div>
        <div>Тяжесть: ${e.severity}</div>
        <div>Проблема: ${e.problem}</div>
        <div>Рекомендация ${e.recommendation}</div>
      </div>`
      )}
			<div>Пост-анализ запроса: </div>
      ${response.post_analyze.issues.map(
        (e) =>
          `<div>
        <div>Тяжесть: ${e.severity}</div>
        <div>Проблема: ${e.problem}</div>
        <div>Рекомендация ${e.recommendation}</div>
      </div>`
      )}
    </div>`;
});
