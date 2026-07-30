// ---------------------------------------------------------------------------
// Configuração e comunicação com a API
// ---------------------------------------------------------------------------

const API = "http://localhost:8000/api";

// --- token / usuário guardados no navegador --------------------------------

const auth = {
  get token() {
    return localStorage.getItem("token");
  },
  get user() {
    return JSON.parse(localStorage.getItem("user") || "null");
  },
  login(token, user) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
  },
  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    location.href = "index.html";
  },
};

// --- wrapper do fetch ------------------------------------------------------

async function request(caminho, opcoes = {}) {
  const headers = { "Content-Type": "application/json", ...opcoes.headers };
  if (auth.token) headers["Authorization"] = `Token ${auth.token}`;

  const resposta = await fetch(API + caminho, { ...opcoes, headers });

  // Token guardado que o servidor não reconhece mais (ex.: banco recriado).
  // Descarta e refaz a chamada como visitante — o auth.token some, então
  // esta condição não se repete e não há risco de laço infinito.
  if (resposta.status === 401 && auth.token) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    montarMenu();
    return request(caminho, opcoes);
  }

  if (resposta.status === 204) return null;

  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(mensagemDeErro(dados));
  return dados;
}

// A API do DRF devolve erros como {campo: ["mensagem"]}; junta tudo num texto.
function mensagemDeErro(dados) {
  if (typeof dados === "string") return dados;
  if (dados.detail) return dados.detail;
  return (
    Object.values(dados)
      .flat()
      .join(" ") || "Não foi possível completar a operação."
  );
}

const api = {
  get: (caminho) => request(caminho),
  post: (caminho, corpo) =>
    request(caminho, { method: "POST", body: JSON.stringify(corpo) }),
  patch: (caminho, corpo) =>
    request(caminho, { method: "PATCH", body: JSON.stringify(corpo) }),
  delete: (caminho) => request(caminho, { method: "DELETE" }),
};

// --- utilidades usadas em várias páginas -----------------------------------

const dinheiro = (valor) =>
  Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

const dataBR = (iso) => new Date(iso + "T00:00:00").toLocaleDateString("pt-BR");

function mostrarMensagem(elemento, texto, tipo = "error") {
  elemento.className = `msg ${tipo}`;
  elemento.textContent = texto;
  elemento.classList.remove("hidden");
}

// Monta os links do cabeçalho conforme quem está logado.
function montarMenu() {
  const nav = document.getElementById("nav");
  if (!nav) return;
  const u = auth.user;

  if (!u) {
    nav.innerHTML = `<a href="login.html">Entrar</a>
      <a href="login.html#cadastro"><button class="btn btn-sm">Cadastrar</button></a>`;
    return;
  }

  const painel = u.is_host
    ? `<a href="painel.html">Painel do anfitrião</a>`
    : `<a href="reservas.html">Minhas reservas</a>`;

  nav.innerHTML = `${painel}
    <span class="muted">Olá, ${u.first_name || u.username}</span>
    <button class="btn btn-outline btn-sm" id="sair">Sair</button>`;
  document.getElementById("sair").onclick = () => auth.logout();
}

document.addEventListener("DOMContentLoaded", montarMenu);
