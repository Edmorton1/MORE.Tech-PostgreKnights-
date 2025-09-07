const openRequest = indexedDB.open("queries", 1);

openRequest.onerror = (ev) => console.error(ev);

openRequest.onupgradeneeded = (ev) => {
  const db = ev.target.result;
  if (!db.objectStoreNames.contains("queries")) {
    db.createObjectStore("queries", { keyPath: "query" });
  }
};

const dbReady = new Promise((res, rej) => {
  openRequest.onsuccess = (ev) => {
    const db = ev.target.result;
    console.log(db);
    res(db);
  };
  openRequest.onerror = (ev) => rej(ev);
});

export const addQuery = async (query, data) => {
  const db = await dbReady;

  console.log("GET ALL QUERY", query);

  const tx = db.transaction("queries", "readwrite");
  const store = tx.objectStore("queries");
  store.put({ query, data });
};

export const getAllQueries = async () => {
  const db = await dbReady;

  console.log("GET ALL QUERY");

  return new Promise((res, rej) => {
    const tx = db.transaction("queries", "readwrite");
    const store = tx.objectStore("queries");
    const request = store.getAll();

    return (request.onsuccess = () => {
      // const result = request.result.map((item) => item.data);
      const result = request.result;
      console.log(result);
      res(result);
    });
  });
};
