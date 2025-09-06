"use strict";

import { addQuery, getAllQueries } from "./indexdb.js";
import { openModal } from "./modal.js";

const form = document.getElementById("form-input");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const query = formData.get("query");
  const data = { query };

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

  addQuery(query, response);
  getAllQueries();

  openModal();

  const showIssues = (asd) =>
    asd.map(
      (issue) =>
        `<div>
        <div>Тяжесть: ${issue.severity}</div>
        <div>Проблема: ${issue.problem}</div>
        <div>Рекомендация ${issue.recommendation}</div>
      </div>`
    );

  modal.innerHTML = `<div>
      <div>Анализ запроса ${response.post_analyze.query}</div>
      <div>Время: ${response.post_analyze.time}</div>
      <div>Стоимость: ${response.post_analyze.total_cost}</div>
      <div>Объём сканируемых данных: ${response.post_analyze.volume}</div>
      <div>Пре-анализ запроса</div>
			${showIssues(response.pre_analyze)}
			<div>Пост-анализ запроса: </div>
      ${showIssues(response.post_analyze.issues)}
    </div>`;
});
