"use strict";

import { addQuery } from "./indexdb.js";
import { modalQuery } from "./modal.js";
import { setModalContent } from "./record-query.js";

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

  const { open, modal } = modalQuery;
  open();

  setModalContent(modal, response);
});
