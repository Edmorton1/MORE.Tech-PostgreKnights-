"use strict";

export const setModalEventListener = (id, params) => {
  const modalWrapper = document.getElementById(id);

  const modal = modalWrapper.firstElementChild;
  modal.addEventListener("click", (event) => {
    event.stopPropagation();
  });

  const openModal = () => {
    if (params && params.hasOwnProperty("onOpen")) {
      params.onOpen(modal);
    }
    modalWrapper.style.display = "block";
  };

  const btnOpenModal = document.getElementById("open-" + id);
  btnOpenModal.addEventListener("click", openModal);

  const closeModal = () => {
    if (params && params.hasOwnProperty("onClose")) {
      params.onClose(modal);
    }
    modalWrapper.style.display = "none";
  };

  modalWrapper.addEventListener("click", closeModal);

  return { open: openModal, modal };
};

export const modalQuery = setModalEventListener("modal-query");

/**
 * @param {ModalParams} params
 */
export const modalHistory = (params) =>
  setModalEventListener("modal-history", params);
