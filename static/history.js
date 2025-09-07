import { getAllQueries } from "./indexdb.js";
import { modalHistory } from "./modal.js";
import { setModalContent } from "./record-query.js";

const repeat = async (modal) => {
  modal.innerHTML = "";

  const queries = await getAllQueries();

  queries.forEach(({ query, data }) => {
    const btn = document.createElement("button");
    btn.innerText = query;
    btn.addEventListener("click", () => {
      console.log(query);
      modal.innerHTML = "";
      setModalContent(modal, data);
      const back_btn = document.createElement("button");
      back_btn.innerText = "Назад";
      back_btn.addEventListener("click", () => repeat(modal));
      modal.appendChild(back_btn);
    });
    modal.appendChild(btn);
  });
};

modalHistory({ onOpen: repeat, onClose: (modal) => (modal.innerHTML = "") });
