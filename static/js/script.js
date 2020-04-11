window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const attachClickHandler = (classSelector, fn) => {
  const el = document.querySelector(classSelector);
  if (!el) return;
  console.log(el)
  return el.addEventListener("click", fn);
}

const handleDelete = (resource) => {
  return fetch(resource, {
    method: "Delete",
  })
    .then(response => {
      console.log(response)
      response.json()
    })
    .catch(error => {
      console.error(error)
    })
}

window.onload = () => {
  if (window.location.pathname.includes("artist")) {
    let url = window.location.pathname.replace("/edit", "")
    attachClickHandler(".delete-artist", (e) => {
      e.preventDefault()
      handleDelete(url)
    })
  } else if (window.location.pathname.includes("venue")){
    let url = window.location.pathname.replace("/edit", "")
    attachClickHandler(".delete-venue", (e) => {
      e.preventDefault()
      handleDelete(url)
    })
    
  }
}