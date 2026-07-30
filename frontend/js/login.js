const formLogin = document.getElementById("form-login");
const formCadastro = document.getElementById("form-cadastro");
const aviso = document.getElementById("aviso");

function trocarAba(mostrarCadastro) {
  formLogin.classList.toggle("hidden", mostrarCadastro);
  formCadastro.classList.toggle("hidden", !mostrarCadastro);
  document.getElementById("tab-login").className = mostrarCadastro ? "btn btn-outline" : "btn";
  document.getElementById("tab-cadastro").className = mostrarCadastro ? "btn" : "btn btn-outline";
  aviso.classList.add("hidden");
}

document.getElementById("tab-login").onclick = () => trocarAba(false);
document.getElementById("tab-cadastro").onclick = () => trocarAba(true);
if (location.hash === "#cadastro") trocarAba(true);

// Depois de autenticar, manda cada perfil para o seu painel.
function entrar(resposta) {
  auth.login(resposta.token, resposta.user);
  location.href = resposta.user.is_host ? "painel.html" : "index.html";
}

formLogin.onsubmit = async (ev) => {
  ev.preventDefault();
  try {
    entrar(
      await api.post("/auth/login/", {
        username: document.getElementById("l-user").value,
        password: document.getElementById("l-senha").value,
      })
    );
  } catch (e) {
    mostrarMensagem(aviso, e.message);
  }
};

formCadastro.onsubmit = async (ev) => {
  ev.preventDefault();
  try {
    entrar(
      await api.post("/auth/register/", {
        first_name: document.getElementById("c-nome").value,
        username: document.getElementById("c-user").value,
        email: document.getElementById("c-email").value,
        password: document.getElementById("c-senha").value,
        is_host: document.getElementById("c-host").checked,
      })
    );
  } catch (e) {
    mostrarMensagem(aviso, e.message);
  }
};
