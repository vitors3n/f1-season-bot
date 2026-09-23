const telegram = window.Telegram?.WebApp;
telegram?.ready();
telegram?.expand();

const status = document.querySelector("#status");
const content = document.querySelector("#race-content");
const scheduleSection = document.querySelector("#schedule-section");
const schedule = document.querySelector("#schedule");

async function carregarProximaCorrida() {
  try {
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
  } catch (erro) { status.textContent = erro.message || "Não foi possível carregar a próxima corrida."; }
}
carregarProximaCorrida();
