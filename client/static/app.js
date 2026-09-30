"use strict";

const select = document.getElementById("tool-select");
const description = document.getElementById("tool-description");
const form = document.getElementById("tool-form");
const runBtn = document.getElementById("run-btn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

let tools = [];

function fieldFor(name, schema) {
  const wrap = document.createElement("div");
  wrap.className = "field";

  const label = document.createElement("label");
  label.textContent = name;
  label.htmlFor = `field-${name}`;
  wrap.appendChild(label);

  let input;
  if (schema.type === "boolean") {
    input = document.createElement("input");
    input.type = "checkbox";
    input.checked = Boolean(schema.default);
  } else if (schema.type === "integer" || schema.type === "number") {
    input = document.createElement("input");
    input.type = "number";
    if (schema.default !== undefined) input.value = schema.default;
  } else if (name === "sql" || name === "url" || (schema.default && String(schema.default).length > 40)) {
    input = document.createElement("textarea");
    input.rows = name === "sql" ? 3 : 2;
    if (schema.default !== undefined) input.value = schema.default;
  } else {
    input = document.createElement("input");
    input.type = "text";
    if (schema.default !== undefined) input.value = schema.default;
  }
  input.id = `field-${name}`;
  input.dataset.name = name;
  input.dataset.type = schema.type || "string";
  wrap.appendChild(input);
  return wrap;
}

function renderForm(tool) {
  form.innerHTML = "";
  description.textContent = tool.description || "";
  const props = (tool.inputSchema && tool.inputSchema.properties) || {};
  Object.entries(props).forEach(([name, schema]) => form.appendChild(fieldFor(name, schema)));
}

function collectArguments() {
  const args = {};
  form.querySelectorAll("[data-name]").forEach((input) => {
    const name = input.dataset.name;
    const type = input.dataset.type;
    if (type === "boolean") {
      args[name] = input.checked;
    } else if (type === "integer") {
      if (input.value !== "") args[name] = parseInt(input.value, 10);
    } else if (type === "number") {
      if (input.value !== "") args[name] = parseFloat(input.value);
    } else if (input.value !== "") {
      args[name] = input.value;
    }
  });
  return args;
}

async function loadTools() {
  statusEl.textContent = "Loading tools from the MCP server…";
  try {
    const res = await fetch("/api/tools");
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    tools = data.tools;
    select.innerHTML = "";
    tools.forEach((tool) => {
      const opt = document.createElement("option");
      opt.value = tool.name;
      opt.textContent = tool.name;
      select.appendChild(opt);
    });
    if (tools.length) renderForm(tools[0]);
    statusEl.textContent = `${tools.length} tool(s) available.`;
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
    runBtn.disabled = true;
  }
}

select.addEventListener("change", () => {
  const tool = tools.find((t) => t.name === select.value);
  if (tool) renderForm(tool);
});

runBtn.addEventListener("click", async () => {
  const name = select.value;
  if (!name) return;
  runBtn.disabled = true;
  statusEl.textContent = `Calling ${name} via MCP…`;
  resultEl.textContent = "";
  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, arguments: collectArguments() }),
    });
    const data = await res.json();
    resultEl.textContent = data.ok ? data.result : `Error: ${data.error}`;
    statusEl.textContent = data.ok ? "Done." : "Tool call failed.";
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
    statusEl.textContent = "Request failed.";
  } finally {
    runBtn.disabled = false;
  }
});

loadTools();
