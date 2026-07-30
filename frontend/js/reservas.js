// Painel do hóspede: acompanha o status de cada solicitação.

const conteudo = document.getElementById("conteudo");

async function carregar() {
  let reservas;
  try {
    reservas = await api.get("/reservations/");
  } catch (e) {
    conteudo.innerHTML = `<p class="msg error">${e.message}</p>`;
    return;
  }

  if (!reservas.length) {
    conteudo.innerHTML = `<p class="empty">
      Você ainda não solicitou nenhuma reserva. <a href="index.html"><u>Buscar imóveis</u></a></p>`;
    return;
  }

  conteudo.innerHTML = `
    <table>
      <thead>
        <tr><th>Imóvel</th><th>Período</th><th>Hóspedes</th><th>Total</th><th>Status</th></tr>
      </thead>
      <tbody>
        ${reservas
          .map(
            (r) => `
          <tr>
            <td><a href="imovel.html?id=${r.property}"><strong>${r.property_detail.title}</strong></a><br>
                <span class="muted">${r.property_detail.city}</span></td>
            <td>${dataBR(r.check_in)} → ${dataBR(r.check_out)}<br>
                <span class="muted">${r.nights} diária(s)</span></td>
            <td>${r.guests_count}</td>
            <td>${dinheiro(r.total_price)}</td>
            <td><span class="badge ${r.status}">${r.status_display}</span></td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>`;
}

if (!auth.token) location.href = "login.html";
else carregar();
