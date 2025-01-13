import { Q as setContext, a1 as getContext, a2 as rest_props, P as push, a3 as fallback, S as store_get, a4 as spread_attributes, X as unsubscribe_stores, Y as bind_props, R as pop, $ as sanitize_props, _ as slot, Z as spread_props, W as escape_html, a5 as copy_payload, a6 as assign_payload, a0 as ensure_array_like, V as stringify, T as attr } from "../../../chunks/index.js";
import { E as ErrorDisplay, C as Card, a as Card_header, c as Card_description } from "../../../chunks/ErrorDisplay.js";
import { t as toWritableStores, o as overridable, c as createBitAttrs, r as removeUndefined, g as getOptionUpdater, i as TimeAgo, z as getRunDetails, L as Label, I as Input, C as Card_content, T as Table, b as Table_header, d as Table_row, e as Table_head, f as Table_body, h as Table_cell } from "../../../chunks/TimeAgo.js";
import "clsx";
import { o as omit, m as makeElement, d as disabledAttr, e as executeCallbacks, a as addMeltEventListener, k as kbd, s as styleToString, j as createElHelpers } from "../../../chunks/index3.js";
import { B as Button, d as cn, g as selectedRunId } from "../../../chunks/projects.js";
import { intervalToDuration, formatDuration } from "date-fns";
import { f as filterTasks, g as getStatusCounts, S as StatusFilter, a as getTaskStatus, t as truncateInput, b as StatusBadge } from "../../../chunks/tasks.js";
import "../../../chunks/client.js";
import { a as Loading } from "../../../chunks/Loading.js";
import { marked } from "marked";
import "dequal";
import { w as writable } from "../../../chunks/index2.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { P as Play } from "../../../chunks/play.js";
function html(value) {
  var html2 = String(value ?? "");
  var open = "<!---->";
  return open + html2 + "<!---->";
}
const defaults = {
  defaultChecked: false,
  disabled: false,
  required: false,
  name: "",
  value: ""
};
const { name } = createElHelpers("switch");
function createSwitch(props) {
  const propsWithDefaults = { ...defaults, ...props };
  const options = toWritableStores(omit(propsWithDefaults, "checked"));
  const { disabled, required, name: nameStore, value } = options;
  const checkedWritable = propsWithDefaults.checked ?? writable(propsWithDefaults.defaultChecked);
  const checked = overridable(checkedWritable, propsWithDefaults?.onCheckedChange);
  function toggleSwitch() {
    if (disabled.get())
      return;
    checked.update((prev) => !prev);
  }
  const root = makeElement(name(), {
    stores: [checked, disabled, required],
    returned: ([$checked, $disabled, $required]) => {
      return {
        "data-disabled": disabledAttr($disabled),
        disabled: disabledAttr($disabled),
        "data-state": $checked ? "checked" : "unchecked",
        type: "button",
        role: "switch",
        "aria-checked": $checked ? "true" : "false",
        "aria-required": $required ? "true" : void 0
      };
    },
    action(node) {
      const unsub = executeCallbacks(addMeltEventListener(node, "click", () => {
        toggleSwitch();
      }), addMeltEventListener(node, "keydown", (e) => {
        if (e.key !== kbd.ENTER && e.key !== kbd.SPACE)
          return;
        e.preventDefault();
        toggleSwitch();
      }));
      return {
        destroy: unsub
      };
    }
  });
  const input = makeElement(name("input"), {
    stores: [checked, nameStore, required, disabled, value],
    returned: ([$checked, $name, $required, $disabled, $value]) => {
      return {
        type: "checkbox",
        "aria-hidden": true,
        hidden: true,
        tabindex: -1,
        name: $name,
        value: $value,
        checked: $checked,
        required: $required,
        disabled: disabledAttr($disabled),
        style: styleToString({
          position: "absolute",
          opacity: 0,
          "pointer-events": "none",
          margin: 0,
          transform: "translateX(-100%)"
        })
      };
    }
  });
  return {
    elements: {
      root,
      input
    },
    states: {
      checked
    },
    options
  };
}
function getSwitchData() {
  const NAME = "switch";
  const PARTS = ["root", "input", "thumb"];
  return {
    NAME,
    PARTS
  };
}
function setCtx(props) {
  const { NAME, PARTS } = getSwitchData();
  const getAttrs = createBitAttrs(NAME, PARTS);
  const Switch2 = { ...createSwitch(removeUndefined(props)), getAttrs };
  setContext(NAME, Switch2);
  return {
    ...Switch2,
    updateOption: getOptionUpdater(Switch2.options)
  };
}
function getCtx() {
  const { NAME } = getSwitchData();
  return getContext(NAME);
}
function Switch_input($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["el"]);
  push();
  var $$store_subs;
  let inputValue;
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { input },
    options: { value, name: name2, disabled, required }
  } = getCtx();
  inputValue = store_get($$store_subs ??= {}, "$value", value) === void 0 || store_get($$store_subs ??= {}, "$value", value) === "" ? "on" : store_get($$store_subs ??= {}, "$value", value);
  $$payload.out += `<input${spread_attributes({
    ...store_get($$store_subs ??= {}, "$input", input),
    name: store_get($$store_subs ??= {}, "$name", name2),
    disabled: store_get($$store_subs ??= {}, "$disabled", disabled),
    required: store_get($$store_subs ??= {}, "$required", required),
    value: inputValue,
    ...$$restProps
  })}>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { el });
  pop();
}
function Switch$1($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "checked",
    "onCheckedChange",
    "disabled",
    "name",
    "value",
    "includeInput",
    "required",
    "asChild",
    "inputAttrs",
    "el"
  ]);
  push();
  var $$store_subs;
  let builder, attrs;
  let checked = fallback($$props["checked"], () => void 0, true);
  let onCheckedChange = fallback($$props["onCheckedChange"], () => void 0, true);
  let disabled = fallback($$props["disabled"], () => void 0, true);
  let name2 = fallback($$props["name"], () => void 0, true);
  let value = fallback($$props["value"], () => void 0, true);
  let includeInput = fallback($$props["includeInput"], true);
  let required = fallback($$props["required"], () => void 0, true);
  let asChild = fallback($$props["asChild"], false);
  let inputAttrs = fallback($$props["inputAttrs"], () => void 0, true);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { root },
    states: { checked: localChecked },
    updateOption,
    getAttrs
  } = setCtx({
    disabled,
    name: name2,
    value,
    required,
    defaultChecked: checked,
    onCheckedChange: ({ next }) => {
      if (checked !== next) {
        onCheckedChange?.(next);
        checked = next;
      }
      return next;
    }
  });
  checked !== void 0 && localChecked.set(checked);
  updateOption("disabled", disabled);
  updateOption("name", name2);
  updateOption("value", value);
  updateOption("required", required);
  builder = store_get($$store_subs ??= {}, "$root", root);
  attrs = {
    ...getAttrs("root"),
    "data-checked": checked ? "" : void 0
  };
  Object.assign(builder, attrs);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<button${spread_attributes({ ...builder, type: "button", ...$$restProps })}><!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!----></button>`;
  }
  $$payload.out += `<!--]--> `;
  if (includeInput) {
    $$payload.out += "<!--[-->";
    Switch_input($$payload, spread_props([inputAttrs]));
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, {
    checked,
    onCheckedChange,
    disabled,
    name: name2,
    value,
    includeInput,
    required,
    asChild,
    inputAttrs,
    el
  });
  pop();
}
function Switch_thumb($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "el"]);
  push();
  var $$store_subs;
  let attrs;
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const { states: { checked }, getAttrs } = getCtx();
  attrs = {
    ...getAttrs("thumb"),
    "data-state": store_get($$store_subs ??= {}, "$checked", checked) ? "checked" : "unchecked",
    "data-checked": store_get($$store_subs ??= {}, "$checked", checked) ? "" : void 0
  };
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot(
      $$payload,
      $$props,
      "default",
      {
        attrs,
        checked: store_get($$store_subs ??= {}, "$checked", checked)
      },
      null
    );
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<span${spread_attributes({ ...$$restProps, ...attrs })}></span>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, el });
  pop();
}
function Chevron_right($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "m9 18 6-6-6-6" }]];
  Icon($$payload, spread_props([
    { name: "chevron-right" },
    $$sanitized_props,
    {
      iconNode,
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {}, null);
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
}
function RunHeader($$payload, $$props) {
  push();
  let runDetails = $$props["runDetails"];
  let showExportButton = fallback($$props["showExportButton"], true);
  if (runDetails) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="flex justify-between items-center mb-4"><div class="flex gap-12 items-center"><h1 class="text-3xl font-bold">Run: ${escape_html(runDetails.id.slice(-8))}</h1> `;
    if (runDetails) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<span class="text-xl text-gray-500">`;
      TimeAgo($$payload, { date: runDetails.date });
      $$payload.out += `<!----></span>`;
    } else {
      $$payload.out += "<!--[!-->";
    }
    $$payload.out += `<!--]--></div> `;
    if (showExportButton) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<div class="flex gap-4 items-center"><div class="flex gap-2 items-center"><span class="text-sm text-gray-500">Project</span> <span class="text-md text-gray-800">${escape_html(runDetails.project.name)}</span></div> `;
      Button($$payload, {
        variant: "outline",
        class: "text-sm",
        children: ($$payload2) => {
          $$payload2.out += `<!---->Export`;
        },
        $$slots: { default: true }
      });
      $$payload.out += `<!----></div>`;
    } else {
      $$payload.out += "<!--[!-->";
      $$payload.out += `<div class="flex gap-2 items-center"><span class="text-sm text-gray-500">Project</span> <span class="text-md text-gray-800">${escape_html(runDetails.project.name)}</span></div>`;
    }
    $$payload.out += `<!--]--></div>`;
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]-->`;
  bind_props($$props, { runDetails, showExportButton });
  pop();
}
function Switch($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "checked"]);
  push();
  let className = fallback($$props["class"], void 0);
  let checked = fallback($$props["checked"], void 0);
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    Switch$1($$payload2, spread_props([
      {
        get checked() {
          return checked;
        },
        set checked($$value) {
          checked = $$value;
          $$settled = false;
        },
        class: cn("focus-visible:ring-ring focus-visible:ring-offset-background data-[state=checked]:bg-primary data-[state=unchecked]:bg-input peer inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50", className)
      },
      $$restProps,
      {
        children: ($$payload3) => {
          Switch_thumb($$payload3, {
            class: cn("bg-background pointer-events-none block h-5 w-5 rounded-full shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0")
          });
        },
        $$slots: { default: true }
      }
    ]));
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  bind_props($$props, { class: className, checked });
  pop();
}
function _page($$payload, $$props) {
  push();
  var $$store_subs;
  let filteredTasks, statusCounts;
  let runId = null;
  let runDetails = null;
  let loading = true;
  let error = null;
  let expandedTaskId = null;
  let showOutputMarkdown = false;
  let showPromptMarkdown = false;
  async function loadRunDetails(id) {
    loading = true;
    error = null;
    try {
      runDetails = await getRunDetails(id);
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load run details";
      console.error(e);
    } finally {
      loading = false;
    }
  }
  let statusFilter = "";
  let searchTerm = "";
  function formatTimeInterval(start, end) {
    const duration = intervalToDuration({
      start: new Date(start),
      end: new Date(end)
    });
    if (duration.minutes || duration.seconds) {
      return formatDuration(duration, { format: ["minutes", "seconds"] });
    }
    return "<1 second";
  }
  {
    if (store_get($$store_subs ??= {}, "$selectedRunId", selectedRunId)) loadRunDetails(store_get($$store_subs ??= {}, "$selectedRunId", selectedRunId));
  }
  filteredTasks = filterTasks(runDetails?.tasks || [], statusFilter, searchTerm);
  statusCounts = getStatusCounts(runDetails?.tasks || []);
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    $$payload2.out += `<div class="container mx-auto p-4">`;
    if (runDetails) {
      $$payload2.out += "<!--[-->";
      RunHeader($$payload2, { runDetails, showExportButton: true });
    } else {
      $$payload2.out += "<!--[!-->";
    }
    $$payload2.out += `<!--]--> `;
    if (loading) {
      $$payload2.out += "<!--[-->";
      Loading($$payload2, { message: "Loading run details..." });
    } else {
      $$payload2.out += "<!--[!-->";
      if (error) {
        $$payload2.out += "<!--[-->";
        ErrorDisplay($$payload2, {
          errorMessage: error,
          onRetry: () => loadRunDetails(runId)
        });
      } else {
        $$payload2.out += "<!--[!-->";
        if (runDetails) {
          $$payload2.out += "<!--[-->";
          $$payload2.out += `<div class="space-y-6">`;
          Card($$payload2, {
            class: "pb-4",
            children: ($$payload3) => {
              Card_header($$payload3, {
                children: ($$payload4) => {
                  Card_description($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<div class="grid grid-cols-2 md:grid-cols-4 gap-4"><div class="space-y-1"><div class="text-sm text-gray-500">Status</div> <div class="font-semibold">${escape_html(runDetails.status)}</div></div> <div class="space-y-1"><div class="text-sm text-gray-500">Total Tasks</div> <div class="font-semibold">${escape_html(runDetails.tasks.length)}</div></div> <div class="space-y-1"><div class="text-sm text-gray-500">Model</div> <div class="font-semibold">${escape_html(runDetails.details.model || "N/A")}</div></div> <div class="space-y-1">`;
                      Label($$payload5, {
                        for: "search",
                        children: ($$payload6) => {
                          $$payload6.out += `<!---->Search`;
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!----> `;
                      Input($$payload5, {
                        id: "search",
                        placeholder: "Search tasks...",
                        get value() {
                          return searchTerm;
                        },
                        set value($$value) {
                          searchTerm = $$value;
                          $$settled = false;
                        }
                      });
                      $$payload5.out += `<!----></div></div> <div class="flex gap-8 items-end mt-4">`;
                      if (runDetails.tasks.length >= 5) {
                        $$payload5.out += "<!--[-->";
                        StatusFilter($$payload5, {
                          get statusFilter() {
                            return statusFilter;
                          },
                          set statusFilter($$value) {
                            statusFilter = $$value;
                            $$settled = false;
                          },
                          statusCounts,
                          totalCount: runDetails.tasks.length
                        });
                      } else {
                        $$payload5.out += "<!--[!-->";
                      }
                      $$payload5.out += `<!--]--></div>`;
                    },
                    $$slots: { default: true }
                  });
                },
                $$slots: { default: true }
              });
            },
            $$slots: { default: true }
          });
          $$payload2.out += `<!----> `;
          Card($$payload2, {
            children: ($$payload3) => {
              Card_content($$payload3, {
                children: ($$payload4) => {
                  Table($$payload4, {
                    class: "-mt-4",
                    children: ($$payload5) => {
                      Table_header($$payload5, {
                        children: ($$payload6) => {
                          Table_row($$payload6, {
                            children: ($$payload7) => {
                              Table_head($$payload7, {});
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Task ID`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Started`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Duration`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Model`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Input`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Status`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Score`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!---->`;
                            },
                            $$slots: { default: true }
                          });
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!----> `;
                      Table_body($$payload5, {
                        children: ($$payload6) => {
                          const each_array = ensure_array_like(filteredTasks);
                          $$payload6.out += `<!--[-->`;
                          for (let $$index_4 = 0, $$length = each_array.length; $$index_4 < $$length; $$index_4++) {
                            let task = each_array[$$index_4];
                            const isExpanded = expandedTaskId === task.id;
                            const { isPassed, statusClass } = getTaskStatus(task);
                            Table_row($$payload6, {
                              "data-task-id": task.id,
                              class: `cursor-pointer ${statusClass}`,
                              children: ($$payload7) => {
                                Table_cell($$payload7, {
                                  class: "w-4",
                                  children: ($$payload8) => {
                                    Button($$payload8, {
                                      variant: "ghost",
                                      size: "sm",
                                      class: "h-4 w-4 p-0",
                                      children: ($$payload9) => {
                                        Chevron_right($$payload9, {
                                          class: `h-4 w-4 transition-transform duration-200 text-gray-400
                                                ${stringify(isExpanded ? "rotate-90" : "")}`
                                        });
                                      },
                                      $$slots: { default: true }
                                    });
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  class: "font-medium font-mono",
                                  children: ($$payload8) => {
                                    $$payload8.out += `<!---->${escape_html(task.id.slice(-8))}`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    TimeAgo($$payload8, { date: task.created_at });
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    if (task.finished_at) {
                                      $$payload8.out += "<!--[-->";
                                      $$payload8.out += `${escape_html(formatTimeInterval(task.created_at, task.finished_at))}`;
                                    } else {
                                      $$payload8.out += "<!--[!-->";
                                      $$payload8.out += `-`;
                                    }
                                    $$payload8.out += `<!--]-->`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    $$payload8.out += `<!---->${escape_html(task.task_details?.model || "-")}`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  class: "max-w-xs",
                                  children: ($$payload8) => {
                                    $$payload8.out += `<!---->${escape_html(truncateInput(task.task_input))}`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    StatusBadge($$payload8, { status: task.status });
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    $$payload8.out += `<div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 overflow-hidden flex"><div${attr("class", `h-4 min-w-[5px] ${stringify(isPassed ? "bg-green-600" : "bg-red-600")}`)}${attr("style", `width: ${stringify((task.eval_score * 100).toFixed(0))}%`)}></div></div> <div class="text-center text-xs font-medium">${escape_html((task.eval_score * 100).toFixed(0))}%</div>`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!---->`;
                              },
                              $$slots: { default: true }
                            });
                            $$payload6.out += `<!----> `;
                            if (isExpanded) {
                              $$payload6.out += "<!--[-->";
                              Table_row($$payload6, {
                                class: "bg-gray-50 hover:bg-gray-50",
                                children: ($$payload7) => {
                                  Table_cell($$payload7, {
                                    colspan: 8,
                                    class: "border-t border-gray-100",
                                    children: ($$payload8) => {
                                      $$payload8.out += `<div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-6"><div class="space-y-4 pr-12 border-r border-gray-200"><div class="flex items-center mb-2"><h4 class="font-semibold text-lg">Task Details <span class="text-sm font-normal text-gray-800 ml-2">`;
                                      if (task.finished_at) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `(time: ${escape_html(formatTimeInterval(task.created_at, task.finished_at))})`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                        $$payload8.out += `-`;
                                      }
                                      $$payload8.out += `<!--]--></span></h4></div> `;
                                      if (task.task_input) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `<div><h5 class="text-sm font-semibold mb-2">Input</h5> <div class="bg-white p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">${escape_html(typeof task.task_input === "object" && "str" in task.task_input ? task.task_input.str : JSON.stringify(task.task_input, null, 2))}</div></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.task_output) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `<div><div class="flex justify-between items-center mb-1"><h5 class="text-sm font-semibold">Output</h5> <div class="flex items-center gap-4"><div class="flex items-center space-x-2">`;
                                        Switch($$payload8, {
                                          id: "output-markdown",
                                          get checked() {
                                            return showOutputMarkdown;
                                          },
                                          set checked($$value) {
                                            showOutputMarkdown = $$value;
                                            $$settled = false;
                                          }
                                        });
                                        $$payload8.out += `<!----> `;
                                        Label($$payload8, {
                                          for: "output-markdown",
                                          class: "text-sm",
                                          children: ($$payload9) => {
                                            $$payload9.out += `<!---->Markdown`;
                                          },
                                          $$slots: { default: true }
                                        });
                                        $$payload8.out += `<!----></div> `;
                                        Button($$payload8, {
                                          variant: "outline",
                                          size: "sm",
                                          class: "text-sm bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors",
                                          children: ($$payload9) => {
                                            $$payload9.out += `<!---->Cross-Compare`;
                                          },
                                          $$slots: { default: true }
                                        });
                                        $$payload8.out += `<!----></div></div> <div class="bg-white p-4 rounded border border-gray-200">`;
                                        if (showOutputMarkdown) {
                                          $$payload8.out += "<!--[-->";
                                          $$payload8.out += `<div class="markdown-content">${html(marked(typeof task.task_output === "object" && "str" in task.task_output ? task.task_output.str : JSON.stringify(task.task_output, null, 2)))}</div>`;
                                        } else {
                                          $$payload8.out += "<!--[!-->";
                                          $$payload8.out += `<div class="whitespace-pre-wrap font-mono text-xs">${escape_html(typeof task.task_output === "object" && "str" in task.task_output ? task.task_output.str : JSON.stringify(task.task_output, null, 2))}</div>`;
                                        }
                                        $$payload8.out += `<!--]--></div></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.task_details) {
                                        $$payload8.out += "<!--[-->";
                                        const each_array_1 = ensure_array_like(Object.entries(task.task_details));
                                        $$payload8.out += `<div><h5 class="text-sm font-semibold mb-2">Details</h5> <div class="grid grid-cols-1 sm:grid-cols-2 gap-3"><!--[-->`;
                                        for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
                                          let [key, value] = each_array_1[$$index];
                                          if (key !== "prompt") {
                                            $$payload8.out += "<!--[-->";
                                            $$payload8.out += `<div><div class="text-sm font-medium text-gray-600 mb-1">${escape_html(key)}</div> <div class="bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">${escape_html(typeof value === "string" ? value : JSON.stringify(value, null, 2))}</div></div>`;
                                          } else {
                                            $$payload8.out += "<!--[!-->";
                                          }
                                          $$payload8.out += `<!--]-->`;
                                        }
                                        $$payload8.out += `<!--]--></div></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.task_details?.prompt) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `<div><h5 class="text-sm font-semibold mb-2">Prompt</h5> <details class="bg-white rounded border border-gray-200"><summary class="px-4 py-2 cursor-pointer hover:bg-gray-50 flex justify-between items-center"><span>View Prompt</span> <div class="flex items-center space-x-2">`;
                                        Switch($$payload8, {
                                          id: "prompt-markdown",
                                          get checked() {
                                            return showPromptMarkdown;
                                          },
                                          set checked($$value) {
                                            showPromptMarkdown = $$value;
                                            $$settled = false;
                                          }
                                        });
                                        $$payload8.out += `<!----> `;
                                        Label($$payload8, {
                                          for: "prompt-markdown",
                                          class: "text-sm",
                                          children: ($$payload9) => {
                                            $$payload9.out += `<!---->Markdown`;
                                          },
                                          $$slots: { default: true }
                                        });
                                        $$payload8.out += `<!----></div></summary> <div class="p-4">`;
                                        if (showPromptMarkdown) {
                                          $$payload8.out += "<!--[-->";
                                          $$payload8.out += `<div class="markdown-content">${html(marked(typeof task.task_details.prompt === "string" ? task.task_details.prompt : JSON.stringify(task.task_details.prompt, null, 2)))}</div>`;
                                        } else {
                                          $$payload8.out += "<!--[!-->";
                                          $$payload8.out += `<div class="whitespace-pre-wrap font-mono text-xs">${escape_html(typeof task.task_details.prompt === "string" ? task.task_details.prompt : JSON.stringify(task.task_details.prompt, null, 2))}</div>`;
                                        }
                                        $$payload8.out += `<!--]--></div></details></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.task_logs) {
                                        $$payload8.out += "<!--[-->";
                                        const each_array_2 = ensure_array_like(task.task_logs.logs);
                                        $$payload8.out += `<div><h5 class="text-sm font-semibold mb-2">Logs</h5> <details class="bg-white rounded border border-gray-200"><summary class="px-4 py-2 cursor-pointer hover:bg-gray-50">View Logs</summary> <table class="w-full text-sm"><thead class="bg-gray-50 border-y border-gray-200"><tr><th class="px-4 py-2 text-left w-32">Info</th><th class="px-4 py-2 text-left">Message</th></tr></thead><tbody class="divide-y divide-gray-100"><!--[-->`;
                                        for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
                                          let log = each_array_2[$$index_1];
                                          $$payload8.out += `<tr class="hover:bg-gray-50"><td class="px-4 py-2"><div class="text-xs text-gray-500">${escape_html(log.level)}</div> <div class="text-sm">${escape_html(new Date(log.timestamp * 1e3).toLocaleString())}</div></td><td class="px-4 py-2">${escape_html(log.message)}</td></tr>`;
                                        }
                                        $$payload8.out += `<!--]--></tbody></table></details></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--></div> <div class="space-y-4 pl-4"><div class="flex items-center mb-2"><h4 class="font-semibold text-lg">Evaluation <span class="text-sm font-normal text-gray-800 ml-2">`;
                                      if (task.evaluated_at) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `(time: ${escape_html(formatTimeInterval(task.executed_at, task.evaluated_at))})`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                        $$payload8.out += `-`;
                                      }
                                      $$payload8.out += `<!--]--></span></h4> <div class="flex items-center gap-4 ml-auto"><div class="text-sm text-gray-800">Score: ${escape_html((task.eval_score * 100).toFixed(0))}%</div> <div${attr("class", `px-4 py-1 rounded-lg font-semibold
                                                                ${task.eval_passed ? "status-completed" : "status-failed"}`)}>${escape_html(task.eval_passed ? "PASSED" : "FAILED")}</div> `;
                                      Button($$payload8, {
                                        variant: "primary",
                                        size: "sm",
                                        class: "flex items-center gap-2 text-sm transition-colors",
                                        children: ($$payload9) => {
                                          Play($$payload9, { class: "h-3 w-3" });
                                          $$payload9.out += `<!----> Re-run`;
                                        },
                                        $$slots: { default: true }
                                      });
                                      $$payload8.out += `<!----></div></div> `;
                                      if (task.eval_details?.evaluations) {
                                        $$payload8.out += "<!--[-->";
                                        const each_array_3 = ensure_array_like(task.eval_details.evaluations);
                                        $$payload8.out += `<div><h4 class="font-semibold text-lg mb-3">Evaluation Results</h4> <div class="space-y-4 divide-y divide-gray-100"><!--[-->`;
                                        for (let $$index_2 = 0, $$length2 = each_array_3.length; $$index_2 < $$length2; $$index_2++) {
                                          let ev = each_array_3[$$index_2];
                                          $$payload8.out += `<div class="pt-4 first:pt-0"><div class="flex items-center gap-3"><div${attr("class", `flex-none flex items-center justify-center w-9 h-9 rounded-full border ${stringify(ev.score >= 1 ? "status-completed status-completed-border" : ev.score > 0 ? "status-default status-default-border" : "status-failed status-failed-border")}`)}><span class="text-xs font-medium leading-none">${escape_html((ev.score * 100).toFixed(0))}%</span></div> <div class="text-sm font-medium flex-1">${escape_html(ev.criterion)}</div></div> <div class="mt-1 text-sm text-gray-600">${escape_html(ev.rationale)}</div></div>`;
                                        }
                                        $$payload8.out += `<!--]--></div></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.eval_details) {
                                        $$payload8.out += "<!--[-->";
                                        const each_array_4 = ensure_array_like(Object.entries(task.eval_details));
                                        $$payload8.out += `<div><h5 class="font-semibold mb-2">Details</h5> <div class="grid grid-cols-1 sm:grid-cols-2 gap-3"><!--[-->`;
                                        for (let $$index_3 = 0, $$length2 = each_array_4.length; $$index_3 < $$length2; $$index_3++) {
                                          let [key, value] = each_array_4[$$index_3];
                                          if (key !== "evaluations") {
                                            $$payload8.out += "<!--[-->";
                                            $$payload8.out += `<div><div class="text-sm font-medium text-gray-600 mb-1">${escape_html(key)}</div> <div class="bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">${escape_html(typeof value === "string" ? value : JSON.stringify(value, null, 2))}</div></div>`;
                                          } else {
                                            $$payload8.out += "<!--[!-->";
                                          }
                                          $$payload8.out += `<!--]-->`;
                                        }
                                        $$payload8.out += `<!--]--></div></div>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--></div></div>`;
                                    },
                                    $$slots: { default: true }
                                  });
                                },
                                $$slots: { default: true }
                              });
                            } else {
                              $$payload6.out += "<!--[!-->";
                            }
                            $$payload6.out += `<!--]-->`;
                          }
                          $$payload6.out += `<!--]-->`;
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!---->`;
                    },
                    $$slots: { default: true }
                  });
                },
                $$slots: { default: true }
              });
            },
            $$slots: { default: true }
          });
          $$payload2.out += `<!----></div>`;
        } else {
          $$payload2.out += "<!--[!-->";
          $$payload2.out += `<div class="text-center text-gray-500">No run found</div>`;
        }
        $$payload2.out += `<!--]-->`;
      }
      $$payload2.out += `<!--]-->`;
    }
    $$payload2.out += `<!--]--></div>`;
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _page as default
};
