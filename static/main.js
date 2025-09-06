const form = document.getElementById("form-input");

let showModal = 

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const data = { query: formData.get("query") };

  console.log(data);
  const response = await fetch("http://localhost:3000", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((data) => data.json())
    .catch((err) => console.error(err));

  console.log(response);
});
