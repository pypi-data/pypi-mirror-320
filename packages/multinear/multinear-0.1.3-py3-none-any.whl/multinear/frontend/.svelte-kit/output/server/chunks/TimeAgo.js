import { a2 as rest_props, a3 as fallback, S as store_get, _ as slot, a4 as spread_attributes, X as unsubscribe_stores, Y as bind_props, R as pop, $ as sanitize_props, P as push, Q as setContext, a1 as getContext, Z as spread_props, W as escape_html } from "./index.js";
import { d as cn, f as flyAndScale } from "./projects.js";
import "dequal";
import { w as withGet, i as isHTMLElement, n as noop, t as tick, m as makeElement, a as addMeltEventListener, o as omit, e as executeCallbacks, h as addEventListener, A as isTouch, B as removeUndefined$1, s as styleToString, C as portalAttr, v as effect, j as createElHelpers, k as kbd, c as isElement, D as isDocument, b as isBrowser } from "./index3.js";
import { formatDistanceToNow } from "date-fns";
import { w as writable, d as derived } from "./index2.js";
import { nanoid } from "nanoid/non-secure";
import { flip, offset, shift, arrow, size, autoUpdate, computePosition } from "@floating-ui/dom";
import "clsx";
const overridable = (_store, onChange) => {
  const store = withGet(_store);
  const update = (updater, sideEffect) => {
    store.update((curr) => {
      const next = updater(curr);
      let res = next;
      if (onChange) {
        res = onChange({ curr, next });
      }
      sideEffect?.(res);
      return res;
    });
  };
  const set = (curr) => {
    update(() => curr);
  };
  return {
    ...store,
    update,
    set
  };
};
function generateId() {
  return nanoid(10);
}
function generateIds(args) {
  return args.reduce((acc, curr) => {
    acc[curr] = generateId();
    return acc;
  }, {});
}
function makeHull(points) {
  const newPoints = points.slice();
  newPoints.sort(POINT_COMPARATOR);
  return makeHullPresorted(newPoints);
}
function makeHullPresorted(points) {
  if (points.length <= 1)
    return points.slice();
  const upperHull = [];
  for (let i = 0; i < points.length; i++) {
    const p = points[i];
    while (upperHull.length >= 2) {
      const q = upperHull[upperHull.length - 1];
      const r = upperHull[upperHull.length - 2];
      if ((q.x - r.x) * (p.y - r.y) >= (q.y - r.y) * (p.x - r.x))
        upperHull.pop();
      else
        break;
    }
    upperHull.push(p);
  }
  upperHull.pop();
  const lowerHull = [];
  for (let i = points.length - 1; i >= 0; i--) {
    const p = points[i];
    while (lowerHull.length >= 2) {
      const q = lowerHull[lowerHull.length - 1];
      const r = lowerHull[lowerHull.length - 2];
      if ((q.x - r.x) * (p.y - r.y) >= (q.y - r.y) * (p.x - r.x))
        lowerHull.pop();
      else
        break;
    }
    lowerHull.push(p);
  }
  lowerHull.pop();
  if (upperHull.length == 1 && lowerHull.length == 1 && upperHull[0].x == lowerHull[0].x && upperHull[0].y == lowerHull[0].y)
    return upperHull;
  else
    return upperHull.concat(lowerHull);
}
function POINT_COMPARATOR(a, b) {
  if (a.x < b.x)
    return -1;
  else if (a.x > b.x)
    return 1;
  else if (a.y < b.y)
    return -1;
  else if (a.y > b.y)
    return 1;
  else
    return 0;
}
function getPointsFromEl(el) {
  const rect = el.getBoundingClientRect();
  return [
    { x: rect.left, y: rect.top },
    { x: rect.right, y: rect.top },
    { x: rect.right, y: rect.bottom },
    { x: rect.left, y: rect.bottom }
  ];
}
function makeHullFromElements(els) {
  const points = els.flatMap((el) => getPointsFromEl(el));
  return makeHull(points);
}
function pointInPolygon(point, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x;
    const yi = polygon[i].y;
    const xj = polygon[j].x;
    const yj = polygon[j].y;
    const intersect = yi > point.y !== yj > point.y && point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi;
    if (intersect)
      inside = !inside;
  }
  return inside;
}
function toWritableStores(properties) {
  const result = {};
  Object.keys(properties).forEach((key) => {
    const propertyKey = key;
    const value = properties[propertyKey];
    result[propertyKey] = withGet(writable(value));
  });
  return result;
}
function getPortalParent(node) {
  let parent = node.parentElement;
  while (isHTMLElement(parent) && !parent.hasAttribute("data-portal")) {
    parent = parent.parentElement;
  }
  return parent || "body";
}
function getPortalDestination(node, portalProp) {
  if (portalProp !== void 0)
    return portalProp;
  const portalParent = getPortalParent(node);
  if (portalParent === "body")
    return document.body;
  return null;
}
const defaultConfig = {
  strategy: "absolute",
  placement: "top",
  gutter: 5,
  flip: true,
  sameWidth: false,
  overflowPadding: 8
};
const ARROW_TRANSFORM = {
  bottom: "rotate(45deg)",
  left: "rotate(135deg)",
  top: "rotate(225deg)",
  right: "rotate(315deg)"
};
function useFloating(reference, floating, opts = {}) {
  if (!floating || !reference || opts === null)
    return {
      destroy: noop
    };
  const options = { ...defaultConfig, ...opts };
  const arrowEl = floating.querySelector("[data-arrow=true]");
  const middleware = [];
  if (options.flip) {
    middleware.push(flip({
      boundary: options.boundary,
      padding: options.overflowPadding
    }));
  }
  const arrowOffset = isHTMLElement(arrowEl) ? arrowEl.offsetHeight / 2 : 0;
  if (options.gutter || options.offset) {
    const data = options.gutter ? { mainAxis: options.gutter } : options.offset;
    if (data?.mainAxis != null) {
      data.mainAxis += arrowOffset;
    }
    middleware.push(offset(data));
  }
  middleware.push(shift({
    boundary: options.boundary,
    crossAxis: options.overlap,
    padding: options.overflowPadding
  }));
  if (arrowEl) {
    middleware.push(arrow({ element: arrowEl, padding: 8 }));
  }
  middleware.push(size({
    padding: options.overflowPadding,
    apply({ rects, availableHeight, availableWidth }) {
      if (options.sameWidth) {
        Object.assign(floating.style, {
          width: `${Math.round(rects.reference.width)}px`,
          minWidth: "unset"
        });
      }
      if (options.fitViewport) {
        Object.assign(floating.style, {
          maxWidth: `${availableWidth}px`,
          maxHeight: `${availableHeight}px`
        });
      }
    }
  }));
  function compute() {
    if (!reference || !floating)
      return;
    if (isHTMLElement(reference) && !reference.ownerDocument.documentElement.contains(reference))
      return;
    const { placement, strategy } = options;
    computePosition(reference, floating, {
      placement,
      middleware,
      strategy
    }).then((data) => {
      const x = Math.round(data.x);
      const y = Math.round(data.y);
      const [side, align] = getSideAndAlignFromPlacement(data.placement);
      floating.setAttribute("data-side", side);
      floating.setAttribute("data-align", align);
      Object.assign(floating.style, {
        position: options.strategy,
        top: `${y}px`,
        left: `${x}px`
      });
      if (isHTMLElement(arrowEl) && data.middlewareData.arrow) {
        const { x: x2, y: y2 } = data.middlewareData.arrow;
        const dir = data.placement.split("-")[0];
        arrowEl.setAttribute("data-side", dir);
        Object.assign(arrowEl.style, {
          position: "absolute",
          left: x2 != null ? `${x2}px` : "",
          top: y2 != null ? `${y2}px` : "",
          [dir]: `calc(100% - ${arrowOffset}px)`,
          transform: ARROW_TRANSFORM[dir],
          backgroundColor: "inherit",
          zIndex: "inherit"
        });
      }
      return data;
    });
  }
  Object.assign(floating.style, {
    position: options.strategy
  });
  return {
    destroy: autoUpdate(reference, floating, compute)
  };
}
function getSideAndAlignFromPlacement(placement) {
  const [side, align = "center"] = placement.split("-");
  return [side, align];
}
const usePortal = (el, target = "body") => {
  let targetEl;
  if (!isHTMLElement(target) && typeof target !== "string") {
    return {
      destroy: noop
    };
  }
  async function update(newTarget) {
    target = newTarget;
    if (typeof target === "string") {
      targetEl = document.querySelector(target);
      if (targetEl === null) {
        await tick();
        targetEl = document.querySelector(target);
      }
      if (targetEl === null) {
        throw new Error(`No element found matching css selector: "${target}"`);
      }
    } else if (target instanceof HTMLElement) {
      targetEl = target;
    } else {
      throw new TypeError(`Unknown portal target type: ${target === null ? "null" : typeof target}. Allowed types: string (CSS selector) or HTMLElement.`);
    }
    el.dataset.portal = "";
    targetEl.appendChild(el);
    el.hidden = false;
  }
  function destroy() {
    el.remove();
  }
  update(target);
  return {
    update,
    destroy
  };
};
function createLabel() {
  const root = makeElement("label", {
    action: (node) => {
      const mouseDown = addMeltEventListener(node, "mousedown", (e) => {
        if (!e.defaultPrevented && e.detail > 1) {
          e.preventDefault();
        }
      });
      return {
        destroy: mouseDown
      };
    }
  });
  return {
    elements: {
      root
    }
  };
}
const defaults = {
  positioning: {
    placement: "bottom"
  },
  arrowSize: 8,
  defaultOpen: false,
  closeOnPointerDown: true,
  openDelay: 1e3,
  closeDelay: 0,
  forceVisible: false,
  portal: void 0,
  closeOnEscape: true,
  disableHoverableContent: false,
  group: void 0
};
const { name } = createElHelpers("tooltip");
const groupMap = /* @__PURE__ */ new Map();
const tooltipIdParts = ["trigger", "content"];
function createTooltip(props) {
  const withDefaults = { ...defaults, ...props };
  const options = toWritableStores(omit(withDefaults, "open", "ids"));
  const { positioning, arrowSize, closeOnPointerDown, openDelay, closeDelay, forceVisible, portal, closeOnEscape, disableHoverableContent, group } = options;
  const openWritable = withDefaults.open ?? writable(withDefaults.defaultOpen);
  const open = overridable(openWritable, withDefaults?.onOpenChange);
  const openReason = writable(null);
  const ids = toWritableStores({ ...generateIds(tooltipIdParts), ...withDefaults.ids });
  let clickedTrigger = false;
  const getEl = (part) => {
    if (!isBrowser)
      return null;
    return document.getElementById(ids[part].get());
  };
  let openTimeout = null;
  let closeTimeout = null;
  function openTooltip(reason) {
    if (closeTimeout) {
      window.clearTimeout(closeTimeout);
      closeTimeout = null;
    }
    if (!openTimeout) {
      openTimeout = window.setTimeout(() => {
        open.set(true);
        openReason.update((prev) => prev ?? reason);
        openTimeout = null;
      }, openDelay.get());
    }
  }
  function closeTooltip(isBlur) {
    if (openTimeout) {
      window.clearTimeout(openTimeout);
      openTimeout = null;
    }
    if (isBlur && isMouseInTooltipArea) {
      openReason.set("pointer");
      return;
    }
    if (!closeTimeout) {
      closeTimeout = window.setTimeout(() => {
        open.set(false);
        openReason.set(null);
        if (isBlur)
          clickedTrigger = false;
        closeTimeout = null;
      }, closeDelay.get());
    }
  }
  const isVisible = derived([open, forceVisible], ([$open, $forceVisible]) => {
    return $open || $forceVisible;
  });
  const trigger = makeElement(name("trigger"), {
    stores: [ids.content, ids.trigger, open],
    returned: ([$contentId, $triggerId, $open]) => {
      return {
        "aria-describedby": $contentId,
        id: $triggerId,
        "data-state": $open ? "open" : "closed"
      };
    },
    action: (node) => {
      const keydownHandler = (e) => {
        if (closeOnEscape.get() && e.key === kbd.ESCAPE) {
          if (openTimeout) {
            window.clearTimeout(openTimeout);
            openTimeout = null;
          }
          open.set(false);
        }
      };
      const unsub = executeCallbacks(addMeltEventListener(node, "pointerdown", () => {
        const $closeOnPointerDown = closeOnPointerDown.get();
        if (!$closeOnPointerDown)
          return;
        open.set(false);
        clickedTrigger = true;
        if (openTimeout) {
          window.clearTimeout(openTimeout);
          openTimeout = null;
        }
      }), addMeltEventListener(node, "pointerenter", (e) => {
        if (isTouch(e))
          return;
        openTooltip("pointer");
      }), addMeltEventListener(node, "pointerleave", (e) => {
        if (isTouch(e))
          return;
        if (openTimeout) {
          window.clearTimeout(openTimeout);
          openTimeout = null;
        }
      }), addMeltEventListener(node, "focus", () => {
        if (clickedTrigger)
          return;
        openTooltip("focus");
      }), addMeltEventListener(node, "blur", () => closeTooltip(true)), addMeltEventListener(node, "keydown", keydownHandler), addEventListener(document, "keydown", keydownHandler));
      return {
        destroy: unsub
      };
    }
  });
  const content = makeElement(name("content"), {
    stores: [isVisible, open, portal, ids.content],
    returned: ([$isVisible, $open, $portal, $contentId]) => {
      return removeUndefined$1({
        role: "tooltip",
        hidden: $isVisible ? void 0 : true,
        tabindex: -1,
        style: $isVisible ? void 0 : styleToString({ display: "none" }),
        id: $contentId,
        "data-portal": portalAttr($portal),
        "data-state": $open ? "open" : "closed"
      });
    },
    action: (node) => {
      let unsubFloating = noop;
      let unsubPortal = noop;
      const unsubDerived = effect([isVisible, positioning, portal], ([$isVisible, $positioning, $portal]) => {
        unsubPortal();
        unsubFloating();
        const triggerEl = getEl("trigger");
        if (!$isVisible || !triggerEl)
          return;
        tick().then(() => {
          unsubPortal();
          unsubFloating();
          const portalDest = getPortalDestination(node, $portal);
          if (portalDest)
            unsubPortal = usePortal(node, portalDest).destroy;
          unsubFloating = useFloating(triggerEl, node, $positioning).destroy;
        });
      });
      function handleScroll(e) {
        if (!open.get())
          return;
        const target = e.target;
        if (!isElement(target) && !isDocument(target))
          return;
        const triggerEl = getEl("trigger");
        if (triggerEl && target.contains(triggerEl)) {
          closeTooltip();
        }
      }
      const unsubEvents = executeCallbacks(addMeltEventListener(node, "pointerenter", () => openTooltip("pointer")), addMeltEventListener(node, "pointerdown", () => openTooltip("pointer")), addEventListener(window, "scroll", handleScroll, { capture: true }));
      return {
        destroy() {
          unsubEvents();
          unsubPortal();
          unsubFloating();
          unsubDerived();
        }
      };
    }
  });
  const arrow2 = makeElement(name("arrow"), {
    stores: arrowSize,
    returned: ($arrowSize) => ({
      "data-arrow": true,
      style: styleToString({
        position: "absolute",
        width: `var(--arrow-size, ${$arrowSize}px)`,
        height: `var(--arrow-size, ${$arrowSize}px)`
      })
    })
  });
  let isMouseInTooltipArea = false;
  effect(open, ($open) => {
    const currentGroup = group.get();
    if (currentGroup === void 0 || currentGroup === false) {
      return;
    }
    if (!$open) {
      if (groupMap.get(currentGroup) === open) {
        groupMap.delete(currentGroup);
      }
      return;
    }
    const currentOpen = groupMap.get(currentGroup);
    currentOpen?.set(false);
    groupMap.set(currentGroup, open);
  });
  effect([open, openReason], ([$open, $openReason]) => {
    if (!$open || !isBrowser)
      return;
    return executeCallbacks(addEventListener(document, "mousemove", (e) => {
      const contentEl = getEl("content");
      const triggerEl = getEl("trigger");
      if (!contentEl || !triggerEl)
        return;
      const polygonElements = disableHoverableContent.get() ? [triggerEl] : [triggerEl, contentEl];
      const polygon = makeHullFromElements(polygonElements);
      isMouseInTooltipArea = pointInPolygon({
        x: e.clientX,
        y: e.clientY
      }, polygon);
      if ($openReason !== "pointer")
        return;
      if (!isMouseInTooltipArea) {
        closeTooltip();
      }
    }));
  });
  return {
    ids,
    elements: {
      trigger,
      content,
      arrow: arrow2
    },
    states: { open },
    options
  };
}
function createBitAttrs(bit, parts) {
  const attrs = {};
  parts.forEach((part) => {
    attrs[part] = {
      [`data-${bit}-${part}`]: ""
    };
  });
  return (part) => attrs[part];
}
function removeUndefined(obj) {
  const result = {};
  for (const key in obj) {
    const value = obj[key];
    if (value !== void 0) {
      result[key] = value;
    }
  }
  return result;
}
function getOptionUpdater(options) {
  return function(key, value) {
    if (value === void 0)
      return;
    const store = options[key];
    if (store) {
      store.set(value);
    }
  };
}
function getPositioningUpdater(store) {
  return (props = {}) => {
    return updatePositioning$1(store, props);
  };
}
function updatePositioning$1(store, props) {
  const defaultPositioningProps = {
    side: "bottom",
    align: "center",
    sideOffset: 0,
    alignOffset: 0,
    sameWidth: false,
    avoidCollisions: true,
    collisionPadding: 8,
    fitViewport: false,
    strategy: "absolute",
    overlap: false
  };
  const withDefaults = { ...defaultPositioningProps, ...props };
  store.update((prev) => {
    return {
      ...prev,
      placement: joinPlacement(withDefaults.side, withDefaults.align),
      offset: {
        ...prev.offset,
        mainAxis: withDefaults.sideOffset,
        crossAxis: withDefaults.alignOffset
      },
      gutter: 0,
      sameWidth: withDefaults.sameWidth,
      flip: withDefaults.avoidCollisions,
      overflowPadding: withDefaults.collisionPadding,
      boundary: withDefaults.collisionBoundary,
      fitViewport: withDefaults.fitViewport,
      strategy: withDefaults.strategy,
      overlap: withDefaults.overlap
    };
  });
}
function joinPlacement(side, align) {
  if (align === "center")
    return side;
  return `${side}-${align}`;
}
function getLabelData() {
  const NAME = "label";
  const PARTS = ["root"];
  const getAttrs = createBitAttrs(NAME, PARTS);
  return {
    NAME,
    getAttrs
  };
}
function Label$1($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "el"]);
  push();
  var $$store_subs;
  let builder;
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const { elements: { root } } = createLabel();
  const { getAttrs } = getLabelData();
  const attrs = getAttrs("root");
  builder = store_get($$store_subs ??= {}, "$root", root);
  Object.assign(builder, attrs);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<label${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!----></label>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, el });
  pop();
}
function getTooltipData() {
  const NAME = "tooltip";
  const PARTS = ["arrow", "content", "trigger"];
  return {
    NAME,
    PARTS
  };
}
function setCtx(props) {
  const { NAME, PARTS } = getTooltipData();
  const getAttrs = createBitAttrs(NAME, PARTS);
  const tooltip = {
    ...createTooltip({
      positioning: {
        placement: "top",
        gutter: 0
      },
      openDelay: 700,
      ...removeUndefined(props),
      forceVisible: true
    }),
    getAttrs
  };
  setContext(NAME, tooltip);
  return {
    ...tooltip,
    updateOption: getOptionUpdater(tooltip.options)
  };
}
function getCtx() {
  const { NAME } = getTooltipData();
  return getContext(NAME);
}
function updatePositioning(props) {
  const defaultPlacement = {
    side: "top",
    align: "center",
    sideOffset: 1
  };
  const withDefaults = { ...defaultPlacement, ...props };
  const { options: { positioning } } = getCtx();
  const updater = getPositioningUpdater(positioning);
  updater({ ...withDefaults });
}
function Tooltip($$payload, $$props) {
  push();
  var $$store_subs;
  let closeOnEscape = fallback($$props["closeOnEscape"], () => void 0, true);
  let portal = fallback($$props["portal"], () => void 0, true);
  let closeOnPointerDown = fallback($$props["closeOnPointerDown"], () => void 0, true);
  let openDelay = fallback($$props["openDelay"], () => void 0, true);
  let closeDelay = fallback($$props["closeDelay"], () => void 0, true);
  let open = fallback($$props["open"], () => void 0, true);
  let onOpenChange = fallback($$props["onOpenChange"], () => void 0, true);
  let disableHoverableContent = fallback($$props["disableHoverableContent"], () => void 0, true);
  let group = fallback($$props["group"], () => void 0, true);
  const {
    states: { open: localOpen },
    updateOption,
    ids
  } = setCtx({
    closeOnEscape,
    portal,
    closeOnPointerDown,
    openDelay,
    closeDelay,
    forceVisible: true,
    defaultOpen: open,
    disableHoverableContent,
    group,
    onOpenChange: ({ next }) => {
      if (open !== next) {
        onOpenChange?.(next);
        open = next;
      }
      return next;
    },
    positioning: { gutter: 0, offset: { mainAxis: 1 } }
  });
  const idValues = derived([ids.content, ids.trigger], ([$contentId, $triggerId]) => ({ content: $contentId, trigger: $triggerId }));
  open !== void 0 && localOpen.set(open);
  updateOption("closeOnEscape", closeOnEscape);
  updateOption("portal", portal);
  updateOption("closeOnPointerDown", closeOnPointerDown);
  updateOption("openDelay", openDelay);
  updateOption("closeDelay", closeDelay);
  updateOption("group", group);
  updateOption("disableHoverableContent", disableHoverableContent);
  $$payload.out += `<!---->`;
  slot(
    $$payload,
    $$props,
    "default",
    {
      ids: store_get($$store_subs ??= {}, "$idValues", idValues)
    },
    null
  );
  $$payload.out += `<!---->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, {
    closeOnEscape,
    portal,
    closeOnPointerDown,
    openDelay,
    closeDelay,
    open,
    onOpenChange,
    disableHoverableContent,
    group
  });
  pop();
}
function Tooltip_content$1($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "transition",
    "transitionConfig",
    "inTransition",
    "inTransitionConfig",
    "outTransition",
    "outTransitionConfig",
    "asChild",
    "id",
    "side",
    "align",
    "sideOffset",
    "alignOffset",
    "collisionPadding",
    "avoidCollisions",
    "collisionBoundary",
    "sameWidth",
    "fitViewport",
    "strategy",
    "overlap",
    "el"
  ]);
  push();
  var $$store_subs;
  let builder;
  let transition = fallback($$props["transition"], () => void 0, true);
  let transitionConfig = fallback($$props["transitionConfig"], () => void 0, true);
  let inTransition = fallback($$props["inTransition"], () => void 0, true);
  let inTransitionConfig = fallback($$props["inTransitionConfig"], () => void 0, true);
  let outTransition = fallback($$props["outTransition"], () => void 0, true);
  let outTransitionConfig = fallback($$props["outTransitionConfig"], () => void 0, true);
  let asChild = fallback($$props["asChild"], false);
  let id = fallback($$props["id"], () => void 0, true);
  let side = fallback($$props["side"], "top");
  let align = fallback($$props["align"], "center");
  let sideOffset = fallback($$props["sideOffset"], 0);
  let alignOffset = fallback($$props["alignOffset"], 0);
  let collisionPadding = fallback($$props["collisionPadding"], 8);
  let avoidCollisions = fallback($$props["avoidCollisions"], true);
  let collisionBoundary = fallback($$props["collisionBoundary"], () => void 0, true);
  let sameWidth = fallback($$props["sameWidth"], false);
  let fitViewport = fallback($$props["fitViewport"], false);
  let strategy = fallback($$props["strategy"], "absolute");
  let overlap = fallback($$props["overlap"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { content },
    states: { open },
    ids,
    getAttrs
  } = getCtx();
  const attrs = getAttrs("content");
  if (id) {
    ids.content.set(id);
  }
  builder = store_get($$store_subs ??= {}, "$content", content);
  Object.assign(builder, attrs);
  if (store_get($$store_subs ??= {}, "$open", open)) {
    updatePositioning({
      side,
      align,
      sideOffset,
      alignOffset,
      collisionPadding,
      avoidCollisions,
      collisionBoundary,
      sameWidth,
      fitViewport,
      strategy,
      overlap
    });
  }
  if (asChild && store_get($$store_subs ??= {}, "$open", open)) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    if (transition && store_get($$store_subs ??= {}, "$open", open)) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
      slot($$payload, $$props, "default", { builder }, null);
      $$payload.out += `<!----></div>`;
    } else {
      $$payload.out += "<!--[!-->";
      if (inTransition && outTransition && store_get($$store_subs ??= {}, "$open", open)) {
        $$payload.out += "<!--[-->";
        $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
        slot($$payload, $$props, "default", { builder }, null);
        $$payload.out += `<!----></div>`;
      } else {
        $$payload.out += "<!--[!-->";
        if (inTransition && store_get($$store_subs ??= {}, "$open", open)) {
          $$payload.out += "<!--[-->";
          $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
          slot($$payload, $$props, "default", { builder }, null);
          $$payload.out += `<!----></div>`;
        } else {
          $$payload.out += "<!--[!-->";
          if (outTransition && store_get($$store_subs ??= {}, "$open", open)) {
            $$payload.out += "<!--[-->";
            $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
            slot($$payload, $$props, "default", { builder }, null);
            $$payload.out += `<!----></div>`;
          } else {
            $$payload.out += "<!--[!-->";
            if (store_get($$store_subs ??= {}, "$open", open)) {
              $$payload.out += "<!--[-->";
              $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
              slot($$payload, $$props, "default", { builder }, null);
              $$payload.out += `<!----></div>`;
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
    }
    $$payload.out += `<!--]-->`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, {
    transition,
    transitionConfig,
    inTransition,
    inTransitionConfig,
    outTransition,
    outTransitionConfig,
    asChild,
    id,
    side,
    align,
    sideOffset,
    alignOffset,
    collisionPadding,
    avoidCollisions,
    collisionBoundary,
    sameWidth,
    fitViewport,
    strategy,
    overlap,
    el
  });
  pop();
}
function Tooltip_trigger($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "id", "el"]);
  push();
  var $$store_subs;
  let builder;
  let asChild = fallback($$props["asChild"], false);
  let id = fallback($$props["id"], () => void 0, true);
  let el = fallback($$props["el"], () => void 0, true);
  const { elements: { trigger }, ids, getAttrs } = getCtx();
  const attrs = getAttrs("trigger");
  if (id) {
    ids.trigger.set(id);
  }
  builder = store_get($$store_subs ??= {}, "$trigger", trigger);
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
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, id, el });
  pop();
}
const API_URL = "http://localhost:8000/api";
async function startExperiment(projectId) {
  const response = await fetch(`${API_URL}/jobs/${projectId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  });
  if (!response.ok) {
    throw new Error(`Failed to start experiment: ${response.statusText}`);
  }
  return response.json();
}
async function getJobStatus(projectId, jobId) {
  const response = await fetch(`${API_URL}/jobs/${projectId}/${jobId}/status`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch job status: ${response.statusText}`);
  }
  return response.json();
}
async function getRecentRuns(projectId, limit = 5, offset2 = 0) {
  const response = await fetch(
    `${API_URL}/runs/${projectId}?limit=${limit}&offset=${offset2}`,
    {
      headers: {
        "Content-Type": "application/json"
      }
    }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch recent runs: ${response.statusText}`);
  }
  return response.json();
}
async function getRunDetails(runId) {
  const response = await fetch(`${API_URL}/run-details/${runId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch run details: ${response.statusText}`);
  }
  return response.json();
}
async function getSameTasks(projectId, challengeId, limit = 10, offset2 = 0) {
  const response = await fetch(`${API_URL}/same-tasks/${projectId}/${challengeId}?limit=${limit}&offset=${offset2}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch same tasks: ${response.statusText}`);
  }
  return response.json();
}
async function startSingleTask(projectId, challengeId) {
  const response = await fetch(`${API_URL}/jobs/${projectId}/task/${challengeId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  });
  if (!response.ok) {
    throw new Error(`Failed to start task: ${response.statusText}`);
  }
  return response.json();
}
function Card_content($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<div${spread_attributes({
    class: cn("p-6", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></div>`;
  bind_props($$props, { class: className });
  pop();
}
function Table($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<div class="relative w-full overflow-auto"><table${spread_attributes({
    class: cn("w-full caption-bottom text-sm", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></table></div>`;
  bind_props($$props, { class: className });
  pop();
}
function Table_body($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<tbody${spread_attributes({
    class: cn("[&_tr:last-child]:border-0", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></tbody>`;
  bind_props($$props, { class: className });
  pop();
}
function Table_cell($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<td${spread_attributes({
    class: cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></td>`;
  bind_props($$props, { class: className });
  pop();
}
function Table_head($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<th${spread_attributes({
    class: cn("text-muted-foreground h-12 px-4 text-left align-middle font-medium [&:has([role=checkbox])]:pr-0", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></th>`;
  bind_props($$props, { class: className });
  pop();
}
function Table_header($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<thead${spread_attributes({
    class: cn("[&_tr]:border-b", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></thead>`;
  bind_props($$props, { class: className });
  pop();
}
function Table_row($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<tr${spread_attributes({
    class: cn("hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></tr>`;
  bind_props($$props, { class: className });
  pop();
}
function Label($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  Label$1($$payload, spread_props([
    {
      class: cn("text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70", className)
    },
    $$restProps,
    {
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {}, null);
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
  bind_props($$props, { class: className });
  pop();
}
function Input($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "value", "readonly"]);
  push();
  let className = fallback($$props["class"], void 0);
  let value = fallback($$props["value"], void 0);
  let readonly = fallback($$props["readonly"], void 0);
  $$payload.out += `<input${spread_attributes({
    class: cn("border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50", className),
    value,
    readonly,
    ...$$restProps
  })}>`;
  bind_props($$props, { class: className, value, readonly });
  pop();
}
function Tooltip_content($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "class",
    "sideOffset",
    "transition",
    "transitionConfig"
  ]);
  push();
  let className = fallback($$props["class"], void 0);
  let sideOffset = fallback($$props["sideOffset"], 4);
  let transition = fallback($$props["transition"], flyAndScale);
  let transitionConfig = fallback($$props["transitionConfig"], () => ({ y: 8, duration: 150 }), true);
  Tooltip_content$1($$payload, spread_props([
    {
      transition,
      transitionConfig,
      sideOffset,
      class: cn("bg-popover text-popover-foreground z-50 overflow-hidden rounded-md border px-3 py-1.5 text-sm shadow-md", className)
    },
    $$restProps,
    {
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {}, null);
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
  bind_props($$props, {
    class: className,
    sideOffset,
    transition,
    transitionConfig
  });
  pop();
}
const Root = Tooltip;
const Trigger = Tooltip_trigger;
function TimeAgo($$payload, $$props) {
  push();
  let timeAgo, fullDate;
  let date = $$props["date"];
  const dateObj = new Date(date);
  timeAgo = formatDistanceToNow(dateObj, { addSuffix: true }).replace("about ", "~").replace("less than a minute ago", "just now");
  fullDate = dateObj.toLocaleString(void 0, { dateStyle: "medium", timeStyle: "short" });
  Root($$payload, {
    children: ($$payload2) => {
      Trigger($$payload2, {
        class: "cursor-default",
        children: ($$payload3) => {
          $$payload3.out += `<!---->${escape_html(timeAgo)}`;
        },
        $$slots: { default: true }
      });
      $$payload2.out += `<!----> `;
      Tooltip_content($$payload2, {
        children: ($$payload3) => {
          $$payload3.out += `<p>${escape_html(fullDate)}</p>`;
        },
        $$slots: { default: true }
      });
      $$payload2.out += `<!---->`;
    },
    $$slots: { default: true }
  });
  bind_props($$props, { date });
  pop();
}
export {
  Card_content as C,
  Input as I,
  Label as L,
  Root as R,
  Table as T,
  getSameTasks as a,
  Table_header as b,
  createBitAttrs as c,
  Table_row as d,
  Table_head as e,
  Table_body as f,
  getOptionUpdater as g,
  Table_cell as h,
  TimeAgo as i,
  getJobStatus as j,
  startSingleTask as k,
  getRecentRuns as l,
  useFloating as m,
  generateIds as n,
  overridable as o,
  getPortalDestination as p,
  createLabel as q,
  removeUndefined as r,
  startExperiment as s,
  toWritableStores as t,
  usePortal as u,
  generateId as v,
  getPositioningUpdater as w,
  Trigger as x,
  Tooltip_content as y,
  getRunDetails as z
};
