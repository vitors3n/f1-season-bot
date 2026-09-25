const telegram = window.Telegram?.WebApp;
telegram?.ready();
telegram?.expand();

const status = document.querySelector("#status");
const content = document.querySelector("#race-content");
const scheduleSection = document.querySelector("#schedule-section");
const schedule = document.querySelector("#schedule");
const user = document.querySelector("#user");
const top5Section = document.querySelector("#top5-section");
const top5Form = document.querySelector("#top5-form");
const top5Fields = document.querySelector("#top5-fields");
const top5Deadline = document.querySelector("#top5-deadline");
const top5Feedback = document.querySelector("#top5-feedback");
const top5Submit = document.querySelector("#top5-submit");
const top5Points = document.querySelector("#top5-points");
const adminSection = document.querySelector("#admin-section");
const adminTitle = document.querySelector("#admin-title");
const adminForm = document.querySelector("#admin-form");
const adminFields = document.querySelector("#admin-fields");
const adminFeedback = document.querySelector("#admin-feedback");
const historySection = document.querySelector("#history-section");
const historyContainer = document.querySelector("#history");
const adminTab = document.querySelector("#admin-tab");
const tabs = document.querySelectorAll("[data-tab]");
const panels = document.querySelectorAll("[data-panel]");
let abaAtiva = "dashboard";

function mostrarAba(nome) {
  abaAtiva = nome;
  panels.forEach((painel) => { painel.hidden = painel.dataset.panel !== nome; });
  tabs.forEach((aba) => {
    const ativa = aba.dataset.tab === nome;
    aba.classList.toggle("active", ativa);
    aba.setAttribute("aria-selected", ativa);
  });
}

tabs.forEach((aba) => aba.addEventListener("click", () => mostrarAba(aba.dataset.tab)));

async function autenticarTelegram() {
  if (!telegram?.initData) {
    throw new Error("Abra o dashboard pelo botão no chat privado com o bot.");
  }
  const response = await fetch("api/auth/telegram", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ init_data: telegram.initData }),
  });
  const dados = await response.json();
  if (!response.ok) throw new Error(dados.erro);
  user.textContent = `Olá, ${dados.usuario.first_name}`;
  user.hidden = false;
}

async function carregarProximaCorrida() {
  try {
    await autenticarTelegram();
    const response = await fetch("api/proxima-corrida");
    const dados = await response.json();
    if (!response.ok) throw new Error(dados.erro);
    document.querySelector("#race-name").textContent = dados.nome;
    document.querySelector("#circuit").textContent = dados.circuito;
    document.querySelector("#race-date").textContent = dados.data;
    dados.sessoes.forEach((sessao) => {
      const item = document.createElement("li");
      const nome = document.createElement("strong");
      const data = document.createElement("span");
      nome.textContent = sessao.nome; data.textContent = sessao.data;
      item.append(nome, data); schedule.append(item);
    });
    status.hidden = true; content.hidden = false; scheduleSection.hidden = false;
    await carregarTop5();
    await carregarHistorico();
    await carregarAdmin();
  } catch (erro) { status.textContent = erro.message || "Não foi possível carregar a próxima corrida."; }
}

function formatarData(data) {
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(data));
}

function renderizarTop5(dados) {
  top5Fields.replaceChildren();
  dados.previsao.forEach((piloto, indice) => adicionarCampoTop5(indice + 1, dados.pilotos, piloto));
  for (let posicao = dados.previsao.length + 1; posicao <= 5; posicao += 1) adicionarCampoTop5(posicao, dados.pilotos);
  top5Submit.disabled = !dados.aberto;
  top5Points.textContent = `Pontuação total: ${dados.pontuacao_total} pontos`;
  top5Deadline.textContent = dados.aberto
    ? `Você pode alterar sua previsão até ${formatarData(dados.fechamento)}.`
    : "As previsões estão fechadas desde 30 minutos antes da corrida.";
  mostrarAba(abaAtiva);
}

function adicionarCampoTop5(posicao, pilotos, selecionado = "") {
  const label = document.createElement("label");
  const ordem = document.createElement("span");
  const select = document.createElement("select");
  ordem.textContent = `${posicao}º`;
  select.name = `top-${posicao}`;
  select.required = true;
  select.append(new Option("Escolha um piloto", ""));
  pilotos.forEach((piloto) => select.append(new Option(`${piloto.nome}${piloto.codigo ? ` (${piloto.codigo})` : ""}`, piloto.id, false, piloto.id === selecionado)));
  label.append(ordem, select); top5Fields.append(label);
}

async function carregarTop5() {
  const response = await fetch("api/top5");
  const dados = await response.json();
  if (!response.ok) throw new Error(dados.erro);
  renderizarTop5(dados);
}

function nomePiloto(driverId) {
  return driverId.replaceAll("_", " ").replace(/\b\w/g, (letra) => letra.toUpperCase());
}

async function carregarHistorico() {
  const response = await fetch("api/historico");
  const dados = await response.json();
  if (!response.ok) throw new Error(dados.erro);
  if (!dados.historico.length) return;
  historyContainer.replaceChildren();
  dados.historico.forEach((item) => {
    const card = document.createElement("article");
    const titulo = document.createElement("h3");
    const previsao = document.createElement("p");
    const pontos = document.createElement("p");
    titulo.textContent = `${item.corrida} — ${item.data.split("-").reverse().join("/")}`;
    previsao.textContent = `Top 5: ${item.previsao.map(nomePiloto).join(", ")}`;
    pontos.textContent = item.pontos === null ? "Aguardando resultado oficial" : `${item.pontos} pontos`;
    card.append(titulo, previsao, pontos); historyContainer.append(card);
  });
  historySection.hidden = false;
}

function adicionarCampoAdmin(posicao, pilotos, selecionado = "") {
  const label = document.createElement("label");
  const ordem = document.createElement("span");
  const select = document.createElement("select");
  ordem.textContent = `${posicao}º`;
  select.required = true;
  select.append(new Option("Escolha um piloto", ""));
  pilotos.forEach((piloto) => select.append(new Option(`${piloto.nome}${piloto.codigo ? ` (${piloto.codigo})` : ""}`, piloto.id, false, piloto.id === selecionado)));
  label.append(ordem, select); adminFields.append(label);
}

function renderizarAdmin(dados) {
  adminFields.replaceChildren();
  dados.resultado.forEach((piloto, indice) => adicionarCampoAdmin(indice + 1, dados.pilotos, piloto));
  for (let posicao = dados.resultado.length + 1; posicao <= 5; posicao += 1) adicionarCampoAdmin(posicao, dados.pilotos);
  adminTitle.textContent = `Resultado oficial — ${dados.corrida.nome}`;
  adminTab.hidden = false;
  mostrarAba(abaAtiva);
}

async function carregarAdmin() {
  const response = await fetch("api/admin/top5");
  if (response.status === 403) return;
  const dados = await response.json();
  if (!response.ok) throw new Error(dados.erro);
  renderizarAdmin(dados);
}

top5Form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const pilotos = [...top5Form.querySelectorAll("select")].map((campo) => campo.value);
  if (new Set(pilotos).size !== 5 || pilotos.includes("")) {
    top5Feedback.textContent = "Escolha cinco pilotos diferentes.";
    return;
  }
  top5Submit.disabled = true;
  try {
    const response = await fetch("api/top5", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pilotos }),
    });
    const dados = await response.json();
    if (!response.ok) throw new Error(dados.erro);
    renderizarTop5(dados);
    top5Feedback.textContent = "Previsão salva com sucesso.";
    await carregarHistorico();
  } catch (erro) {
    top5Feedback.textContent = erro.message || "Não foi possível salvar a previsão.";
    top5Submit.disabled = false;
  }
});

adminForm.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const pilotos = [...adminForm.querySelectorAll("select")].map((campo) => campo.value);
  if (new Set(pilotos).size !== 5 || pilotos.includes("")) {
    adminFeedback.textContent = "Escolha cinco pilotos diferentes.";
    return;
  }
  try {
    const response = await fetch("api/admin/top5", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pilotos }),
    });
    const dados = await response.json();
    if (!response.ok) throw new Error(dados.erro);
    renderizarAdmin(dados);
    adminFeedback.textContent = "Resultado oficial salvo.";
  } catch (erro) {
    adminFeedback.textContent = erro.message || "Não foi possível salvar o resultado.";
  }
});
mostrarAba("dashboard");
carregarProximaCorrida();
