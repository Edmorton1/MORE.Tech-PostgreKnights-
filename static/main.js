"use strict";

import "./form.js";
import "./history.js";

const textarea = document.getElementsByTagName("textarea");
textarea[0].addEventListener("keydown", function (event) {
  if (event.key === "Tab") {
    event.preventDefault();

    const start = this.selectionStart;
    const end = this.selectionEnd;

    this.value =
      this.value.substring(0, start) + "\t" + this.value.substring(end);

    this.selectionStart = this.selectionEnd = start + 1;
  }
});
