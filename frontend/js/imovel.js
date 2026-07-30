// Página de detalhe do imóvel: fotos, comodidades e pedido de reserva.

const id = new URLSearchParams(location.search).get("id");
const conteudo = document.getElementById("conteudo");

let imovel = null;

async function carregar() {
  try {
    imovel = await api.get(`/properties/${id}/`);
  } catch (e) {
    conteudo.innerHTML = `<p class="msg error">Imóvel não encontrado.</p>`;
    return;
  }
  desenhar();
}

function desenhar() {
  const fotos = imovel.images.map((i) => i.url);
  const principal = fotos[0] || "https://placehold.co/800x600?text=Sem+foto";
  const hoje = new Date().toISOString().slice(0, 10);

  conteudo.innerHTML = `
    <h1>${imovel.title}</h1>
    <p class="muted">★ ${imovel.rating || "novo"} · ${imovel.address}, ${imovel.city}</p>

    <div class="gallery">
      <img src="${principal}" alt="${imovel.title}">
      <div class="thumbs">
        ${fotos.slice(1, 3).map((f) => `<img src="${f}" alt="">`).join("")}
      </div>
    </div>

    <div class="detail">
      <div>
        <h2>Sobre o espaço</h2>
        <p>${imovel.description || "Sem descrição."}</p>
        <p class="muted" style="margin-top:10px">
          Até ${imovel.max_guests} hóspedes · Anfitrião: ${imovel.host.first_name || imovel.host.username}
        </p>

        <h2>Comodidades</h2>
        <div class="amenities">
          ${(imovel.amenities || []).map((a) => `<span class="tag">${a}</span>`).join("")
            || "<p class='muted'>Nenhuma informada.</p>"}
        </div>

        <h2>Datas já reservadas</h2>
        <div class="amenities">
          ${imovel.booked_dates.length
            ? imovel.booked_dates.map((d) => `<span class="tag">${dataBR(d)}</span>`).join("")
            : "<p class='muted'>Nenhuma. O imóvel está livre.</p>"}
        </div>
      </div>

      <aside>
        <div class="box">
          <p><strong style="font-size:20px">${dinheiro(imovel.price_per_night)}</strong>
             <span class="muted">a diária</span></p>

          <div class="row" style="margin-top:14px">
            <div class="field">
              <label for="in">Entrada</label>
              <input type="date" id="in" min="${hoje}">
            </div>
            <div class="field">
              <label for="out">Saída</label>
              <input type="date" id="out" min="${hoje}">
            </div>
          </div>

          <div class="field" style="margin-top:10px">
            <label for="guests_count">Hóspedes</label>
            <input type="number" id="guests_count" value="1" min="1" max="${imovel.max_guests}">
          </div>

          <div class="total hidden" id="total"></div>

          <button class="btn" id="reservar" style="width:100%;margin-top:14px" disabled>
            Selecione as datas
          </button>
          <div class="msg hidden" id="aviso"></div>
        </div>
      </aside>
    </div>`;

  document.getElementById("in").onchange = atualizarTotal;
  document.getElementById("out").onchange = atualizarTotal;
  document.getElementById("reservar").onclick = reservar;
}

// Calcula as diárias e libera o botão quando as duas datas fazem sentido.
function atualizarTotal() {
  const entrada = document.getElementById("in").value;
  const saida = document.getElementById("out").value;
  const total = document.getElementById("total");
  const botao = document.getElementById("reservar");

  // a saída nunca pode ser antes da entrada
  if (entrada) document.getElementById("out").min = entrada;

  if (!entrada || !saida || saida <= entrada) {
    total.classList.add("hidden");
    botao.disabled = true;
    botao.textContent = "Selecione as datas";
    return;
  }

  const noites = (new Date(saida) - new Date(entrada)) / 86400000;
  total.classList.remove("hidden");
  total.innerHTML = `<span>${noites} diária(s)</span>
    <span>${dinheiro(imovel.price_per_night * noites)}</span>`;
  botao.disabled = false;
  botao.textContent = "Solicitar reserva";
}

async function reservar() {
  const aviso = document.getElementById("aviso");

  if (!auth.token) {
    location.href = "login.html";
    return;
  }
  if (auth.user.is_host) {
    mostrarMensagem(aviso, "Contas de anfitrião não solicitam reservas.");
    return;
  }

  const botao = document.getElementById("reservar");
  botao.disabled = true;
  try {
    await api.post("/reservations/", {
      property: imovel.id,
      check_in: document.getElementById("in").value,
      check_out: document.getElementById("out").value,
      guests_count: Number(document.getElementById("guests_count").value),
    });
    mostrarMensagem(aviso, "Solicitação enviada! Acompanhe em 'Minhas reservas'.", "ok");
    setTimeout(() => (location.href = "reservas.html"), 1500);
  } catch (e) {
    mostrarMensagem(aviso, e.message);
    botao.disabled = false;
  }
}

carregar();
