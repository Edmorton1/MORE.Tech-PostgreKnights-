"use strict";

const modalWrapper = document.getElementById("modal-wrapper");

export const openModal = () => {
  modalWrapper.style.display = "block";
};

modalWrapper.addEventListener("click", () => {
  modalWrapper.style.display = "none";
});

const buttonOpenModal = document.getElementById("open-modal");
buttonOpenModal.addEventListener("click", openModal);

const modal = document.getElementById("modal");
modal.addEventListener("click", (event) => {
  event.stopPropagation();
});
