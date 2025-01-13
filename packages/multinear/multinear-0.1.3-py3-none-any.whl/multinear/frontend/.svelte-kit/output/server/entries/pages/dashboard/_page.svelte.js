import { Z as spread_props, _ as slot, $ as sanitize_props, a2 as rest_props, a3 as fallback, a4 as spread_attributes, Y as bind_props, R as pop, P as push, a8 as element, S as store_get, W as escape_html, T as attr, V as stringify, a0 as ensure_array_like, X as unsubscribe_stores } from "../../../chunks/index.js";
import { C as Card, a as Card_header, b as Card_title, E as ErrorDisplay, c as Card_description, d as Card_footer } from "../../../chunks/ErrorDisplay.js";
import { j as getJobStatus, s as startExperiment, k as startSingleTask, C as Card_content, l as getRecentRuns } from "../../../chunks/TimeAgo.js";
import "../../../chunks/index3.js";
import { d as cn, B as Button, s as selectedProjectId, c as projects, p as projectsLoading, b as projectsError } from "../../../chunks/projects.js";
import { a as alertVariants, R as RunsWithFilters } from "../../../chunks/RunsWithFilters.js";
import { w as writable, g as get } from "../../../chunks/index2.js";
import "../../../chunks/client.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { L as Loader_circle } from "../../../chunks/Loading.js";
import { P as Play } from "../../../chunks/play.js";
import "clsx";
function Circle_alert($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "circle",
      { "cx": "12", "cy": "12", "r": "10" }
    ],
    [
      "line",
      {
        "x1": "12",
        "x2": "12",
        "y1": "8",
        "y2": "12"
      }
    ],
    [
      "line",
      {
        "x1": "12",
        "x2": "12.01",
        "y1": "16",
        "y2": "16"
      }
    ]
  ];
  Icon($$payload, spread_props([
    { name: "circle-alert" },
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
function Circle_check($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "circle",
      { "cx": "12", "cy": "12", "r": "10" }
    ],
    ["path", { "d": "m9 12 2 2 4-4" }]
  ];
  Icon($$payload, spread_props([
    { name: "circle-check" },
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
function Circle_x($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "circle",
      { "cx": "12", "cy": "12", "r": "10" }
    ],
    ["path", { "d": "m15 9-6 6" }],
    ["path", { "d": "m9 9 6 6" }]
  ];
  Icon($$payload, spread_props([
    { name: "circle-x" },
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
function Alert($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "variant"]);
  push();
  let className = fallback($$props["class"], void 0);
  let variant = fallback($$props["variant"], "default");
  $$payload.out += `<div${spread_attributes({
    class: cn(alertVariants({ variant }), className),
    ...$$restProps,
    role: "alert"
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></div>`;
  bind_props($$props, { class: className, variant });
  pop();
}
function Alert_description($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<div${spread_attributes({
    class: cn("text-sm [&_p]:leading-relaxed", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></div>`;
  bind_props($$props, { class: className });
  pop();
}
function Alert_title($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "level"]);
  push();
  let className = fallback($$props["class"], void 0);
  let level = fallback($$props["level"], "h5");
  element(
    $$payload,
    level,
    () => {
      $$payload.out += `${spread_attributes({
        class: cn("mb-1 font-medium leading-none tracking-tight", className),
        ...$$restProps
      })}`;
    },
    () => {
      $$payload.out += `<!---->`;
      slot($$payload, $$props, "default", {}, null);
      $$payload.out += `<!---->`;
    }
  );
  bind_props($$props, { class: className, level });
  pop();
}
const pendingRunStore = writable(null);
const jobStore = writable({
  currentJob: null,
  jobStatus: null,
  jobDetails: null,
  taskStatusCounts: {}
});
async function pollJobStatus(projectId, jobId, reloadRecentRuns) {
  let status = "started";
  while (!["completed", "failed", "not_found"].includes(status)) {
    await new Promise((r) => setTimeout(r, 1e3));
    try {
      const statusData = await getJobStatus(projectId, jobId);
      status = statusData.status;
      let counts = {};
      if (statusData.task_status_map && Object.keys(statusData.task_status_map).length > 0) {
        counts = Object.values(statusData.task_status_map).reduce((acc, status2) => {
          acc[status2] = (acc[status2] || 0) + 1;
          return acc;
        }, {});
      }
      jobStore.set({
        currentJob: jobId,
        jobStatus: status,
        jobDetails: statusData,
        taskStatusCounts: counts
      });
      if (status === "completed") {
        await reloadRecentRuns();
      } else if (status === "failed") {
        break;
      }
    } catch (error) {
      console.error("Error polling job status:", error);
      break;
    }
  }
}
async function executePendingRun(reloadRecentRuns) {
  const pendingRun = get(pendingRunStore);
  if (!pendingRun) return;
  try {
    const data = pendingRun.type === "experiment" ? await startExperiment(pendingRun.projectId) : await startSingleTask(pendingRun.projectId, pendingRun.challengeId);
    const jobId = data.job_id;
    jobStore.update((state) => ({
      ...state,
      currentJob: jobId,
      jobStatus: "started",
      jobDetails: null,
      taskStatusCounts: {}
    }));
    await pollJobStatus(pendingRun.projectId, jobId, reloadRecentRuns);
  } catch (error) {
    console.error("Error executing pending run:", error);
    jobStore.update((state) => ({
      ...state,
      jobStatus: "error"
    }));
  } finally {
    pendingRunStore.set(null);
  }
}
function JobStatus($$payload, $$props) {
  push();
  var $$store_subs;
  if (store_get($$store_subs ??= {}, "$jobStore", jobStore).currentJob) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="border rounded-lg p-4 bg-gray-50"><div class="flex items-center gap-4"><span class="font-medium">Latest Run:</span> <span>${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).currentJob.slice(-8))}</span> <span${attr("class", `${stringify(`text-gray-500 ${store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus === "failed" ? "text-red-500" : ""}`)} svelte-i2gyqw`)}>Status: ${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus)}</span></div> `;
    if (store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<div class="mt-2">`;
      if ((!store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.task_status_map || Object.keys(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.task_status_map).length === 0) && !store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus) {
        $$payload.out += "<!--[-->";
        Alert($$payload, {
          variant: "destructive",
          class: "mt-2",
          children: ($$payload2) => {
            Circle_alert($$payload2, { class: "h-4 w-4" });
            $$payload2.out += `<!----> `;
            Alert_title($$payload2, {
              children: ($$payload3) => {
                $$payload3.out += `<!---->Experiment Failed`;
              },
              $$slots: { default: true }
            });
            $$payload2.out += `<!----> `;
            Alert_description($$payload2, {
              children: ($$payload3) => {
                $$payload3.out += `<!---->No task status information available. The experiment may have failed to start properly.`;
              },
              $$slots: { default: true }
            });
            $$payload2.out += `<!---->`;
          },
          $$slots: { default: true }
        });
      } else {
        $$payload.out += "<!--[!-->";
        $$payload.out += `<div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 relative overflow-hidden"><div class="h-4 transition-all duration-300 bg-blue-600 relative overflow-hidden progress-stripe rounded-r-sm svelte-i2gyqw"${attr("style", `width: ${stringify(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus === "completed" ? "100" : store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.current_task / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks * 100)}%;`)}></div> `;
        if (store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.task_status_map) {
          $$payload.out += "<!--[-->";
          const each_array = ensure_array_like(Object.entries(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.task_status_map));
          $$payload.out += `<!--[-->`;
          for (let index = 0, $$length = each_array.length; index < $$length; index++) {
            let [taskId, status] = each_array[index];
            if (status === "failed") {
              $$payload.out += "<!--[-->";
              $$payload.out += `<div class="absolute top-0 h-4 bg-red-500"${attr("style", `width: ${stringify(100 / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks)}%; left: ${stringify(index / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks * 100)}%`)}></div>`;
            } else {
              $$payload.out += "<!--[!-->";
              if (status === "evaluating") {
                $$payload.out += "<!--[-->";
                $$payload.out += `<div class="absolute top-0 h-4 bg-yellow-500 progress-stripe svelte-i2gyqw"${attr("style", `width: ${stringify(100 / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks)}%; left: ${stringify(index / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks * 100)}%`)}></div>`;
              } else {
                $$payload.out += "<!--[!-->";
                if (status === "completed") {
                  $$payload.out += "<!--[-->";
                  $$payload.out += `<div class="absolute top-0 h-4 bg-green-600"${attr("style", `width: ${stringify(100 / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks)}%; left: ${stringify(index / store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.total_tasks * 100)}%`)}></div>`;
                } else {
                  $$payload.out += "<!--[!-->";
                }
                $$payload.out += `<!--]-->`;
              }
              $$payload.out += `<!--]-->`;
            }
            $$payload.out += `<!--]-->`;
          }
          $$payload.out += `<!--]-->`;
        } else {
          $$payload.out += "<!--[!-->";
        }
        $$payload.out += `<!--]--></div> <div class="flex justify-between mt-1 text-sm text-gray-500"><div class="flex">`;
        if (store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails.task_status_map) {
          $$payload.out += "<!--[-->";
          const each_array_1 = ensure_array_like(Object.entries(store_get($$store_subs ??= {}, "$jobStore", jobStore).taskStatusCounts));
          $$payload.out += `<div class="text-sm text-gray-500 flex flex-wrap gap-2"><!--[-->`;
          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
            let [status, count] = each_array_1[$$index_1];
            if (count > 0) {
              $$payload.out += "<!--[-->";
              $$payload.out += `<span class="inline-flex items-center gap-1"><div${attr("class", `w-2 h-2 rounded-full ${stringify(status === "completed" ? "bg-green-500" : status === "running" ? "bg-blue-500" : status === "evaluating" ? "bg-yellow-500" : status === "failed" ? "bg-red-500" : "bg-gray-500")}`)}></div> ${escape_html(status)}: ${escape_html(count)}</span>`;
            } else {
              $$payload.out += "<!--[!-->";
            }
            $$payload.out += `<!--]-->`;
          }
          $$payload.out += `<!--]--></div>`;
        } else {
          $$payload.out += "<!--[!-->";
        }
        $$payload.out += `<!--]--></div> <div class="flex gap-8"><span>${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails?.current_task || 0)} / ${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails?.total_tasks || 0)}</span> <span>${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus === "completed" ? "100" : Math.round((store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails?.current_task || 0) / (store_get($$store_subs ??= {}, "$jobStore", jobStore).jobDetails?.total_tasks || 1) * 100))}%</span></div></div>`;
      }
      $$payload.out += `<!--]--></div>`;
    } else {
      $$payload.out += "<!--[!-->";
    }
    $$payload.out += `<!--]--></div>`;
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
function JobControls($$payload, $$props) {
  push();
  var $$store_subs;
  let reloadRecentRuns = $$props["reloadRecentRuns"];
  $$payload.out += `<div>`;
  if (store_get($$store_subs ??= {}, "$jobStore", jobStore).currentJob && store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus && !["completed", "failed", "error"].includes(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus)) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="flex items-center gap-2">`;
    Loader_circle($$payload, { class: "h-4 w-4 animate-spin" });
    $$payload.out += `<!----> <span class="text-gray-500">${escape_html(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus)}</span></div>`;
  } else {
    $$payload.out += "<!--[!-->";
    Button($$payload, {
      variant: "primary",
      class: "flex items-center gap-2",
      children: ($$payload2) => {
        Play($$payload2, { class: "h-4 w-4" });
        $$payload2.out += `<!----> Run Experiment`;
      },
      $$slots: { default: true }
    });
  }
  $$payload.out += `<!--]--></div>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { reloadRecentRuns });
  pop();
}
function KeyAlerts($$payload, $$props) {
  push();
  let alerts = fallback($$props["alerts"], () => [], true);
  if (alerts.length > 0) {
    $$payload.out += "<!--[-->";
    Card($$payload, {
      children: ($$payload2) => {
        Card_header($$payload2, {
          children: ($$payload3) => {
            Card_title($$payload3, {
              children: ($$payload4) => {
                $$payload4.out += `<!---->Key Alerts and Notifications`;
              },
              $$slots: { default: true }
            });
          },
          $$slots: { default: true }
        });
        $$payload2.out += `<!----> `;
        Card_content($$payload2, {
          class: "space-y-4",
          children: ($$payload3) => {
            const each_array = ensure_array_like(alerts);
            $$payload3.out += `<!--[-->`;
            for (let index = 0, $$length = each_array.length; index < $$length; index++) {
              let alert = each_array[index];
              Alert($$payload3, {
                variant: alert.type === "improvement" ? "default" : "destructive",
                children: ($$payload4) => {
                  if (alert.type === "regression") {
                    $$payload4.out += "<!--[-->";
                    Circle_alert($$payload4, { class: "h-4 w-4" });
                  } else {
                    $$payload4.out += "<!--[!-->";
                    if (alert.type === "security") {
                      $$payload4.out += "<!--[-->";
                      Circle_x($$payload4, { class: "h-4 w-4" });
                    } else {
                      $$payload4.out += "<!--[!-->";
                      if (alert.type === "improvement") {
                        $$payload4.out += "<!--[-->";
                        Circle_check($$payload4, { class: "h-4 w-4" });
                      } else {
                        $$payload4.out += "<!--[!-->";
                      }
                      $$payload4.out += `<!--]-->`;
                    }
                    $$payload4.out += `<!--]-->`;
                  }
                  $$payload4.out += `<!--]--> `;
                  Alert_title($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<!---->${escape_html(alert.type.charAt(0).toUpperCase() + alert.type.slice(1))}`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload4.out += `<!----> `;
                  Alert_description($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<!---->${escape_html(alert.message)}`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload4.out += `<!---->`;
                },
                $$slots: { default: true }
              });
            }
            $$payload3.out += `<!--]-->`;
          },
          $$slots: { default: true }
        });
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    });
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]-->`;
  bind_props($$props, { alerts });
  pop();
}
function _page($$payload, $$props) {
  push();
  var $$store_subs;
  let currentProject;
  let recentRuns = [];
  let recentRunsError = null;
  let recentRunsLoading = false;
  let totalRuns = 0;
  async function loadRecentRuns() {
    recentRunsLoading = true;
    recentRunsError = null;
    try {
      const response = await getRecentRuns(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId));
      recentRuns = response.runs;
      totalRuns = response.total;
    } catch (error) {
      console.error("Error loading recent runs:", error);
      recentRunsError = error instanceof Error ? error.message : "Unknown error";
    } finally {
      recentRunsLoading = false;
    }
  }
  async function startPollingIfRunning() {
    if (store_get($$store_subs ??= {}, "$jobStore", jobStore).currentJob && store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus && !["completed", "failed", "error"].includes(store_get($$store_subs ??= {}, "$jobStore", jobStore).jobStatus)) {
      await pollJobStatus(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId), store_get($$store_subs ??= {}, "$jobStore", jobStore).currentJob, loadRecentRuns);
    }
  }
  async function handlePendingRun() {
    if (store_get($$store_subs ??= {}, "$pendingRunStore", pendingRunStore)) {
      await executePendingRun(loadRecentRuns);
    }
  }
  const alerts = [];
  currentProject = store_get($$store_subs ??= {}, "$projects", projects).find((p) => p.id === store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId));
  if (currentProject) {
    loadRecentRuns();
    startPollingIfRunning();
    handlePendingRun();
  }
  $$payload.out += `<div class="container mx-auto p-4 space-y-6">`;
  if (store_get($$store_subs ??= {}, "$projectsLoading", projectsLoading)) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="flex items-center justify-center h-[50vh] text-gray-500"><div class="flex items-center gap-2">`;
    Loader_circle($$payload, { class: "h-6 w-6 animate-spin" });
    $$payload.out += `<!----> <span>Loading project details...</span></div></div>`;
  } else {
    $$payload.out += "<!--[!-->";
    if (store_get($$store_subs ??= {}, "$projectsError", projectsError)) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<div class="flex items-center justify-center h-[50vh] text-gray-500">`;
      ErrorDisplay($$payload, {
        errorMessage: `${store_get($$store_subs ??= {}, "$projectsError", projectsError)} - Check if API is running`,
        onRetry: () => window.location.reload(),
        className: "w-96"
      });
      $$payload.out += `<!----></div>`;
    } else {
      $$payload.out += "<!--[!-->";
      if (!currentProject) {
        $$payload.out += "<!--[-->";
        $$payload.out += `<div class="flex items-center justify-center h-[50vh] text-gray-500">`;
        Card($$payload, {
          class: "border-yellow-200 bg-yellow-50 w-96 space-y-4",
          children: ($$payload2) => {
            Card_header($$payload2, {
              children: ($$payload3) => {
                Card_title($$payload3, {
                  class: "text-yellow-800",
                  children: ($$payload4) => {
                    $$payload4.out += `<!---->Project Not Found`;
                  },
                  $$slots: { default: true }
                });
                $$payload3.out += `<!----> `;
                Card_description($$payload3, {
                  class: "text-yellow-600 pt-2",
                  children: ($$payload4) => {
                    $$payload4.out += `<!---->The project "${escape_html(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId))}" could not be found.`;
                  },
                  $$slots: { default: true }
                });
                $$payload3.out += `<!---->`;
              },
              $$slots: { default: true }
            });
            $$payload2.out += `<!----> `;
            Card_footer($$payload2, {
              class: "flex justify-end",
              children: ($$payload3) => {
                Button($$payload3, {
                  variant: "outline",
                  class: "border-yellow-200 text-yellow-800 hover:bg-yellow-100",
                  children: ($$payload4) => {
                    $$payload4.out += `<!---->Go Back`;
                  },
                  $$slots: { default: true }
                });
              },
              $$slots: { default: true }
            });
            $$payload2.out += `<!---->`;
          },
          $$slots: { default: true }
        });
        $$payload.out += `<!----></div>`;
      } else {
        $$payload.out += "<!--[!-->";
        $$payload.out += `<div class="flex justify-between items-center"><h1 class="text-3xl font-bold -mb-2 -mt-2">${escape_html(currentProject.name)}</h1> `;
        JobControls($$payload, { reloadRecentRuns: loadRecentRuns });
        $$payload.out += `<!----></div> `;
        JobStatus($$payload);
        $$payload.out += `<!----> <div class="grid grid-cols-1 md:grid-cols-3 gap-4">`;
        Card($$payload, {
          children: ($$payload2) => {
            Card_content($$payload2, {
              class: "flex items-center justify-between py-4",
              children: ($$payload3) => {
                $$payload3.out += `<span class="text-md font-medium">Total Runs</span> <div class="text-2xl font-bold">${escape_html(totalRuns)}</div>`;
              },
              $$slots: { default: true }
            });
          },
          $$slots: { default: true }
        });
        $$payload.out += `<!----></div> `;
        RunsWithFilters($$payload, {
          runsList: recentRuns,
          isLoading: recentRunsLoading,
          loadingError: recentRunsError,
          showViewAll: true
        });
        $$payload.out += `<!----> `;
        KeyAlerts($$payload, { alerts });
        $$payload.out += `<!---->`;
      }
      $$payload.out += `<!--]-->`;
    }
    $$payload.out += `<!--]-->`;
  }
  $$payload.out += `<!--]--></div>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _page as default
};
