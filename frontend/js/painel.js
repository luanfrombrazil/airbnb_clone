// Painel do anfitrião: responde solicitações e gerencia os próprios imóveis.

const podeUsar = auth.token && auth.user.is_host;
if (!auth.token) location.href = "login.html";
else if (!auth.user.is_host) location.href = "reservas.html";

const divSolicitacoes = document.getElementById("solicitacoes");
const divImoveis = document.getElementById("imoveis");
const formWrap = document.getElementById("form-wrap");
const form = document.getElementById("form-imovel");
const aviso = document.getElementById("aviso");

// --- solicitações recebidas ------------------------------------------------

async function carregarSolicitacoes() {
  let reservas;
  try {
    reservas = await api.get("/reservations/");
  } catch (e) {
    divSolicitacoes.innerHTML = `<p class="msg error">${e.message}</p>`;
    return;
  }

  if (!reservas.length) {
    divSolicitacoes.innerHTML = `<p class="empty">Nenhuma solicitação recebida ainda.</p>`;
    return;
  }

  divSolicitacoes.innerHTML = `
    <table>
      <thead>
        <tr><th>Imóvel</th><th>Hóspede</th><th>Período</th><th>Total</th><th>Status</th><th></th></tr>
      </thead>
      <tbody>
        ${reservas
          .map(
            (r) => `
          <tr>
            <td>${r.property_detail.title}</td>
            <td>${r.guest.first_name || r.guest.username}<br>
                <span class="muted">${r.guests_count} hóspede(s)</span></td>
            <td>${dataBR(r.check_in)} → ${dataBR(r.check_out)}</td>
            <td>${dinheiro(r.total_price)}</td>
            <td><span class="badge ${r.status}">${r.status_display}</span></td>
            <td>${
              r.status === "PENDING"
                ? `<button class="btn btn-sm btn-green" data-aprovar="${r.id}">Aprovar</button>
                   <button class="btn btn-sm btn-gray" data-recusar="${r.id}">Recusar</button>`
                : ""
            }</td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>`;

  divSolicitacoes.querySelectorAll("[data-aprovar]").forEach((b) => {
    b.onclick = () => responder(b.dataset.aprovar, "approve");
  });
  divSolicitacoes.querySelectorAll("[data-recusar]").forEach((b) => {
    b.onclick = () => responder(b.dataset.recusar, "reject");
  });
}

async function responder(id, acao) {
  try {
    await api.post(`/reservations/${id}/${acao}/`, {});
    carregarSolicitacoes();
  } catch (e) {
    alert(e.message);
  }
}

// --- meus imóveis ----------------------------------------------------------

async function carregarImoveis() {
  let imoveis;
  try {
    imoveis = await api.get("/properties/mine/");
  } catch (e) {
    divImoveis.innerHTML = `<p class="msg error">${e.message}</p>`;
    return;
  }

  if (!imoveis.length) {
    divImoveis.innerHTML = `<p class="empty">Você ainda não cadastrou imóveis.</p>`;
    return;
  }

  divImoveis.innerHTML = `
    <table>
      <thead><tr><th>Imóvel</th><th>Cidade</th><th>Diária</th><th>Hóspedes</th><th></th></tr></thead>
      <tbody>
        ${imoveis
          .map(
            (im) => `
          <tr>
            <td><a href="imovel.html?id=${im.id}"><strong>${im.title}</strong></a></td>
            <td>${im.city}</td>
            <td>${dinheiro(im.price_per_night)}</td>
            <td>${im.max_guests}</td>
            <td>
              <button class="btn btn-sm btn-outline" data-editar="${im.id}">Editar</button>
              <button class="btn btn-sm btn-gray" data-excluir="${im.id}">Excluir</button>
            </td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>`;

  divImoveis.querySelectorAll("[data-editar]").forEach((b) => {
    b.onclick = () => abrirFormulario(imoveis.find((i) => i.id == b.dataset.editar));
  });
  divImoveis.querySelectorAll("[data-excluir]").forEach((b) => {
    b.onclick = async () => {
      if (!confirm("Excluir este imóvel?")) return;
      await api.delete(`/properties/${b.dataset.excluir}/`);
      carregarImoveis();
    };
  });
}

// --- formulário ------------------------------------------------------------

function abrirFormulario(imovel = null) {
  formWrap.classList.remove("hidden");
  aviso.classList.add("hidden");
  document.getElementById("form-titulo").textContent = imovel ? "Editar imóvel" : "Novo imóvel";

  document.getElementById("i-id").value = imovel?.id || "";
  document.getElementById("i-title").value = imovel?.title || "";
  document.getElementById("i-description").value = imovel?.description || "";
  document.getElementById("i-city").value = imovel?.city || "";
  document.getElementById("i-address").value = imovel?.address || "";
  document.getElementById("i-price").value = imovel?.price_per_night || "";
  document.getElementById("i-guests").value = imovel?.max_guests || 2;
  document.getElementById("i-amenities").value = (imovel?.amenities || []).join(", ");
  document.getElementById("i-fotos").value = (imovel?.images || []).map((i) => i.url).join("\n");

  formWrap.scrollIntoView({ behavior: "smooth" });
}

document.getElementById("novo").onclick = () => abrirFormulario();
document.getElementById("cancelar").onclick = () => formWrap.classList.add("hidden");

form.onsubmit = async (ev) => {
  ev.preventDefault();

  const id = document.getElementById("i-id").value;

  const dados = {
    title: document.getElementById("i-title").value,
    description: document.getElementById("i-description").value,
    city: document.getElementById("i-city").value,
    address: document.getElementById("i-address").value,
    price_per_night: document.getElementById("i-price").value,
    max_guests: Number(document.getElementById("i-guests").value),
    amenities: document
      .getElementById("i-amenities")
      .value.split(",")
      .map((a) => a.trim())
      .filter(Boolean),
  };

  try {
    const imovel = id
      ? await api.patch(`/properties/${id}/`, dados)
      : await api.post("/properties/", dados);

    // Fotos: recria a lista a partir do textarea
    const urls = document
      .getElementById("i-fotos")
      .value.split("\n")
      .map((u) => u.trim())
      .filter(Boolean);

    for (const antiga of imovel.images || []) {
      await api.delete(`/property-images/${antiga.id}/`);
    }
    for (const url of urls) {
      await api.post("/property-images/", { property: imovel.id, url });
    }

    formWrap.classList.add("hidden");
    carregarImoveis();
  } catch (e) {
    mostrarMensagem(aviso, e.message);
  }
};

if (podeUsar) {
  carregarSolicitacoes();
  carregarImoveis();
}
