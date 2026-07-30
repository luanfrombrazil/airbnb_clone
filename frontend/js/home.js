// Página inicial: listagem ordenada por avaliação e filtros de busca.

const lista = document.getElementById("lista");
const vazio = document.getElementById("vazio");

async function carregar(filtros = {}) {
  const query = new URLSearchParams(
    Object.entries(filtros).filter(([, v]) => v !== "" && v != null)
  ).toString();

  lista.innerHTML = "<p class='empty'>Carregando...</p>";

  let imoveis;
  try {
    imoveis = await api.get(`/properties/${query ? "?" + query : ""}`);
  } catch (e) {
    lista.innerHTML = `<p class="msg error">Erro ao carregar: ${e.message}</p>`;
    return;
  }

  vazio.classList.toggle("hidden", imoveis.length > 0);
  lista.innerHTML = imoveis
    .map(
      (im) => `
      <a class="card" href="imovel.html?id=${im.id}">
        <img src="${im.images[0]?.url || "https://placehold.co/400x300?text=Sem+foto"}" alt="${im.title}">
        <h3>${im.title} <span class="rating">★ ${im.rating || "novo"}</span></h3>
        <p class="muted">${im.city}</p>
        <p class="muted">Até ${im.max_guests} hóspedes</p>
        <p class="price"><strong>${dinheiro(im.price_per_night)}</strong> a diária</p>
      </a>`
    )
    .join("");
}

document.getElementById("busca").onsubmit = (ev) => {
  ev.preventDefault();
  const filtros = {};
  ["city", "check_in", "check_out", "min_price", "max_price"].forEach(
    (campo) => (filtros[campo] = document.getElementById(campo).value)
  );
  document.getElementById("titulo").textContent = filtros.city
    ? `Imóveis em ${filtros.city}`
    : "Resultados da busca";
  carregar(filtros);
};

carregar();
