fetch('http://127.0.0.1:5000/api/products/')
  .then(res => res.json())
  .then(data => {
    console.log(data);
    // aquí puedes renderizar la lista en el HTML
  })
  .catch(err => console.error(err));
