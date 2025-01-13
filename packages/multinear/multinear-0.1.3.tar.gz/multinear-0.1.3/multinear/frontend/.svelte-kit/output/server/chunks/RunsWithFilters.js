import { a1 as getContext, Q as setContext, P as push, a3 as fallback, _ as slot, S as store_get, X as unsubscribe_stores, Y as bind_props, R as pop, a2 as rest_props, a4 as spread_attributes, $ as sanitize_props, W as escape_html, Z as spread_props, a8 as element, a7 as invalid_default_snippet, a5 as copy_payload, a6 as assign_payload, T as attr, V as stringify, a0 as ensure_array_like } from "./index.js";
import "./client.js";
import { C as Card, E as ErrorDisplay } from "./ErrorDisplay.js";
import { u as usePortal, m as useFloating, o as overridable, t as toWritableStores, n as generateIds, p as getPortalDestination, q as createLabel, v as generateId$1, c as createBitAttrs, r as removeUndefined, g as getOptionUpdater, w as getPositioningUpdater, C as Card_content, L as Label, I as Input, T as Table, b as Table_header, d as Table_row, e as Table_head, f as Table_body, h as Table_cell, R as Root$1, i as TimeAgo, x as Trigger, y as Tooltip_content } from "./TimeAgo.js";
import "clsx";
import { d as cn, f as flyAndScale, s as selectedProjectId } from "./projects.js";
import { tv } from "tailwind-variants";
import { dequal } from "dequal";
import { i as isHTMLElement, n as noop, b as isBrowser, w as withGet, g as getElementByMeltId, c as isElement, f as isHTMLLabelElement, u as useEscapeKeydown, e as executeCallbacks, h as addEventListener, o as omit, j as createElHelpers, l as isObject, p as stripValues, m as makeElement, d as disabledAttr, a as addMeltEventListener, k as kbd, q as isHTMLButtonElement, t as tick, F as FIRST_LAST_KEYS, r as isElementDisabled, s as styleToString, v as effect, x as createHiddenInput, y as safeOnMount, z as isHTMLInputElement } from "./index3.js";
import { d as derived, w as writable, g as get, a as readonly } from "./index2.js";
import { createFocusTrap as createFocusTrap$1 } from "focus-trap";
import { nanoid } from "nanoid/non-secure";
import { formatDuration, intervalToDuration } from "date-fns";
import { a as Loading } from "./Loading.js";
import { I as Icon } from "./Icon.js";
import { C as Check } from "./check.js";
function back(array, index, increment, loop = true) {
  const previousIndex = index - increment;
  if (previousIndex <= 0) {
    return loop ? array[array.length - 1] : array[0];
  }
  return array[previousIndex];
}
function forward(array, index, increment, loop = true) {
  const nextIndex = index + increment;
  if (nextIndex > array.length - 1) {
    return loop ? array[0] : array[array.length - 1];
  }
  return array[nextIndex];
}
function next(array, index, loop = true) {
  if (index === array.length - 1) {
    return loop ? array[0] : array[index];
  }
  return array[index + 1];
}
function prev(array, currentIndex, loop = true) {
  if (currentIndex <= 0) {
    return loop ? array[array.length - 1] : array[0];
  }
  return array[currentIndex - 1];
}
function last(array) {
  return array[array.length - 1];
}
function wrapArray(array, startIndex) {
  return array.map((_, index) => array[(startIndex + index) % array.length]);
}
function toggle(item, array, compare = dequal) {
  const itemIdx = array.findIndex((innerItem) => compare(innerItem, item));
  if (itemIdx !== -1) {
    array.splice(itemIdx, 1);
  } else {
    array.push(item);
  }
  return array;
}
function addHighlight(element2) {
  element2.setAttribute("data-highlighted", "");
}
function removeHighlight(element2) {
  element2.removeAttribute("data-highlighted");
}
function getOptions(el) {
  return Array.from(el.querySelectorAll('[role="option"]:not([data-disabled])')).filter((el2) => isHTMLElement(el2));
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
function debounce(fn, wait = 500) {
  let timeout = null;
  return function(...args) {
    const later = () => {
      timeout = null;
      fn(...args);
    };
    timeout && clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
const isDom = () => typeof window !== "undefined";
function getPlatform() {
  const agent = navigator.userAgentData;
  return agent?.platform ?? navigator.platform;
}
const pt = (v) => isDom() && v.test(getPlatform().toLowerCase());
const isTouchDevice = () => isDom() && !!navigator.maxTouchPoints;
const isMac = () => pt(/^mac/) && !isTouchDevice();
const isApple = () => pt(/mac|iphone|ipad|ipod/i);
const isIos = () => isApple() && !isMac();
const LOCK_CLASSNAME = "data-melt-scroll-lock";
function assignStyle(el, style) {
  if (!el)
    return;
  const previousStyle = el.style.cssText;
  Object.assign(el.style, style);
  return () => {
    el.style.cssText = previousStyle;
  };
}
function setCSSProperty(el, property, value) {
  if (!el)
    return;
  const previousValue = el.style.getPropertyValue(property);
  el.style.setProperty(property, value);
  return () => {
    if (previousValue) {
      el.style.setProperty(property, previousValue);
    } else {
      el.style.removeProperty(property);
    }
  };
}
function getPaddingProperty(documentElement) {
  const documentLeft = documentElement.getBoundingClientRect().left;
  const scrollbarX = Math.round(documentLeft) + documentElement.scrollLeft;
  return scrollbarX ? "paddingLeft" : "paddingRight";
}
function removeScroll(_document) {
  const doc = document;
  const win = doc.defaultView ?? window;
  const { documentElement, body } = doc;
  const locked = body.hasAttribute(LOCK_CLASSNAME);
  if (locked)
    return noop;
  body.setAttribute(LOCK_CLASSNAME, "");
  const scrollbarWidth = win.innerWidth - documentElement.clientWidth;
  const setScrollbarWidthProperty = () => setCSSProperty(documentElement, "--scrollbar-width", `${scrollbarWidth}px`);
  const paddingProperty = getPaddingProperty(documentElement);
  const scrollbarSidePadding = win.getComputedStyle(body)[paddingProperty];
  const setStyle = () => assignStyle(body, {
    overflow: "hidden",
    [paddingProperty]: `calc(${scrollbarSidePadding} + ${scrollbarWidth}px)`
  });
  const setIOSStyle = () => {
    const { scrollX, scrollY, visualViewport } = win;
    const offsetLeft = visualViewport?.offsetLeft ?? 0;
    const offsetTop = visualViewport?.offsetTop ?? 0;
    const restoreStyle = assignStyle(body, {
      position: "fixed",
      overflow: "hidden",
      top: `${-(scrollY - Math.floor(offsetTop))}px`,
      left: `${-(scrollX - Math.floor(offsetLeft))}px`,
      right: "0",
      [paddingProperty]: `calc(${scrollbarSidePadding} + ${scrollbarWidth}px)`
    });
    return () => {
      restoreStyle?.();
      win.scrollTo(scrollX, scrollY);
    };
  };
  const cleanups = [setScrollbarWidthProperty(), isIos() ? setIOSStyle() : setStyle()];
  return () => {
    cleanups.forEach((fn) => fn?.());
    body.removeAttribute(LOCK_CLASSNAME);
  };
}
function derivedVisible(obj) {
  const { open, forceVisible, activeTrigger } = obj;
  return derived([open, forceVisible, activeTrigger], ([$open, $forceVisible, $activeTrigger]) => ($open || $forceVisible) && $activeTrigger !== null);
}
function handleRovingFocus(nextElement) {
  if (!isBrowser)
    return;
  sleep(1).then(() => {
    const currentFocusedElement = document.activeElement;
    if (!isHTMLElement(currentFocusedElement) || currentFocusedElement === nextElement)
      return;
    currentFocusedElement.tabIndex = -1;
    if (nextElement) {
      nextElement.tabIndex = 0;
      nextElement.focus();
    }
  });
}
const ignoredKeys = /* @__PURE__ */ new Set(["Shift", "Control", "Alt", "Meta", "CapsLock", "NumLock"]);
const defaults$1 = {
  onMatch: handleRovingFocus,
  getCurrentItem: () => document.activeElement
};
function createTypeaheadSearch(args = {}) {
  const withDefaults = { ...defaults$1, ...args };
  const typed = withGet(writable([]));
  const resetTyped = debounce(() => {
    typed.update(() => []);
  });
  const handleTypeaheadSearch = (key, items) => {
    if (ignoredKeys.has(key))
      return;
    const currentItem = withDefaults.getCurrentItem();
    const $typed = get(typed);
    if (!Array.isArray($typed)) {
      return;
    }
    $typed.push(key.toLowerCase());
    typed.set($typed);
    const candidateItems = items.filter((item) => {
      if (item.getAttribute("disabled") === "true" || item.getAttribute("aria-disabled") === "true" || item.hasAttribute("data-disabled")) {
        return false;
      }
      return true;
    });
    const isRepeated = $typed.length > 1 && $typed.every((char) => char === $typed[0]);
    const normalizeSearch = isRepeated ? $typed[0] : $typed.join("");
    const currentItemIndex = isHTMLElement(currentItem) ? candidateItems.indexOf(currentItem) : -1;
    let wrappedItems = wrapArray(candidateItems, Math.max(currentItemIndex, 0));
    const excludeCurrentItem = normalizeSearch.length === 1;
    if (excludeCurrentItem) {
      wrappedItems = wrappedItems.filter((v) => v !== currentItem);
    }
    const nextItem = wrappedItems.find((item) => item?.innerText && item.innerText.toLowerCase().startsWith(normalizeSearch.toLowerCase()));
    if (isHTMLElement(nextItem) && nextItem !== currentItem) {
      withDefaults.onMatch(nextItem);
    }
    resetTyped();
  };
  return {
    typed,
    resetTyped,
    handleTypeaheadSearch
  };
}
function createClickOutsideIgnore(meltId) {
  return (e) => {
    const target = e.target;
    const triggerEl = getElementByMeltId(meltId);
    if (!triggerEl || !isElement(target))
      return false;
    const id = triggerEl.id;
    if (isHTMLLabelElement(target) && id === target.htmlFor) {
      return true;
    }
    if (target.closest(`label[for="${id}"]`)) {
      return true;
    }
    return false;
  };
}
function createFocusTrap(config = {}) {
  let trap;
  const { immediate, ...focusTrapOptions } = config;
  const hasFocus = writable(false);
  const isPaused = writable(false);
  const activate = (opts) => trap?.activate(opts);
  const deactivate = (opts) => {
    trap?.deactivate(opts);
  };
  const pause = () => {
    if (trap) {
      trap.pause();
      isPaused.set(true);
    }
  };
  const unpause = () => {
    if (trap) {
      trap.unpause();
      isPaused.set(false);
    }
  };
  const useFocusTrap = (node) => {
    trap = createFocusTrap$1(node, {
      ...focusTrapOptions,
      onActivate() {
        hasFocus.set(true);
        config.onActivate?.();
      },
      onDeactivate() {
        hasFocus.set(false);
        config.onDeactivate?.();
      }
    });
    if (immediate) {
      activate();
    }
    return {
      destroy() {
        deactivate();
        trap = void 0;
      }
    };
  };
  return {
    useFocusTrap,
    hasFocus: readonly(hasFocus),
    isPaused: readonly(isPaused),
    activate,
    deactivate,
    pause,
    unpause
  };
}
const visibleModals = [];
const useModal = (node, config) => {
  let unsubInteractOutside = noop;
  function removeNodeFromVisibleModals() {
    const index = visibleModals.indexOf(node);
    if (index >= 0) {
      visibleModals.splice(index, 1);
    }
  }
  function update(config2) {
    unsubInteractOutside();
    const { open, onClose, shouldCloseOnInteractOutside, closeOnInteractOutside } = config2;
    sleep(100).then(() => {
      if (open) {
        visibleModals.push(node);
      } else {
        removeNodeFromVisibleModals();
      }
    });
    function isLastModal() {
      return last(visibleModals) === node;
    }
    function closeModal() {
      if (isLastModal() && onClose) {
        onClose();
        removeNodeFromVisibleModals();
      }
    }
    function onInteractOutsideStart(e) {
      const target = e.target;
      if (!isElement(target))
        return;
      if (target && isLastModal()) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
    }
    function onInteractOutside(e) {
      if (shouldCloseOnInteractOutside?.(e) && isLastModal()) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        closeModal();
      }
    }
    unsubInteractOutside = useInteractOutside(node, {
      onInteractOutsideStart,
      onInteractOutside: closeOnInteractOutside ? onInteractOutside : void 0,
      enabled: open
    }).destroy;
  }
  update(config);
  return {
    update,
    destroy() {
      removeNodeFromVisibleModals();
      unsubInteractOutside();
    }
  };
};
const defaultConfig = {
  floating: {},
  focusTrap: {},
  modal: {},
  escapeKeydown: {},
  portal: "body"
};
const usePopper = (popperElement, args) => {
  popperElement.dataset.escapee = "";
  const { anchorElement, open, options } = args;
  if (!anchorElement || !open || !options) {
    return { destroy: noop };
  }
  const opts = { ...defaultConfig, ...options };
  const callbacks = [];
  if (opts.portal !== null) {
    callbacks.push(usePortal(popperElement, opts.portal).destroy);
  }
  callbacks.push(useFloating(anchorElement, popperElement, opts.floating).destroy);
  if (opts.focusTrap !== null) {
    const { useFocusTrap } = createFocusTrap({
      immediate: true,
      escapeDeactivates: false,
      allowOutsideClick: true,
      returnFocusOnDeactivate: false,
      fallbackFocus: popperElement,
      ...opts.focusTrap
    });
    callbacks.push(useFocusTrap(popperElement).destroy);
  }
  if (opts.modal !== null) {
    callbacks.push(useModal(popperElement, {
      onClose: () => {
        if (isHTMLElement(anchorElement)) {
          open.set(false);
          anchorElement.focus();
        }
      },
      shouldCloseOnInteractOutside: (e) => {
        if (e.defaultPrevented)
          return false;
        if (isHTMLElement(anchorElement) && anchorElement.contains(e.target)) {
          return false;
        }
        return true;
      },
      ...opts.modal
    }).destroy);
  }
  if (opts.escapeKeydown !== null) {
    callbacks.push(useEscapeKeydown(popperElement, {
      enabled: open,
      handler: () => {
        open.set(false);
      },
      ...opts.escapeKeydown
    }).destroy);
  }
  const unsubscribe = executeCallbacks(...callbacks);
  return {
    destroy() {
      unsubscribe();
    }
  };
};
const useInteractOutside = (node, config) => {
  let unsub = noop;
  let unsubClick = noop;
  let isPointerDown = false;
  let isPointerDownInside = false;
  let ignoreEmulatedMouseEvents = false;
  function update(config2) {
    unsub();
    unsubClick();
    const { onInteractOutside, onInteractOutsideStart, enabled } = config2;
    if (!enabled)
      return;
    function onPointerDown(e) {
      if (onInteractOutside && isValidEvent(e, node)) {
        onInteractOutsideStart?.(e);
      }
      const target = e.target;
      if (isElement(target) && isOrContainsTarget(node, target)) {
        isPointerDownInside = true;
      }
      isPointerDown = true;
    }
    function triggerInteractOutside(e) {
      onInteractOutside?.(e);
    }
    const documentObj = getOwnerDocument(node);
    if (typeof PointerEvent !== "undefined") {
      const onPointerUp = (e) => {
        unsubClick();
        const handler = (e2) => {
          if (shouldTriggerInteractOutside(e2)) {
            triggerInteractOutside(e2);
          }
          resetPointerState();
        };
        if (e.pointerType === "touch") {
          unsubClick = addEventListener(documentObj, "click", handler, {
            capture: true,
            once: true
          });
          return;
        }
        handler(e);
      };
      unsub = executeCallbacks(addEventListener(documentObj, "pointerdown", onPointerDown, true), addEventListener(documentObj, "pointerup", onPointerUp, true));
    } else {
      const onMouseUp = (e) => {
        if (ignoreEmulatedMouseEvents) {
          ignoreEmulatedMouseEvents = false;
        } else if (shouldTriggerInteractOutside(e)) {
          triggerInteractOutside(e);
        }
        resetPointerState();
      };
      const onTouchEnd = (e) => {
        ignoreEmulatedMouseEvents = true;
        if (shouldTriggerInteractOutside(e)) {
          triggerInteractOutside(e);
        }
        resetPointerState();
      };
      unsub = executeCallbacks(addEventListener(documentObj, "mousedown", onPointerDown, true), addEventListener(documentObj, "mouseup", onMouseUp, true), addEventListener(documentObj, "touchstart", onPointerDown, true), addEventListener(documentObj, "touchend", onTouchEnd, true));
    }
  }
  function shouldTriggerInteractOutside(e) {
    if (isPointerDown && !isPointerDownInside && isValidEvent(e, node)) {
      return true;
    }
    return false;
  }
  function resetPointerState() {
    isPointerDown = false;
    isPointerDownInside = false;
  }
  update(config);
  return {
    update,
    destroy() {
      unsub();
      unsubClick();
    }
  };
};
function isValidEvent(e, node) {
  if ("button" in e && e.button > 0)
    return false;
  const target = e.target;
  if (!isElement(target))
    return false;
  const ownerDocument = target.ownerDocument;
  if (!ownerDocument || !ownerDocument.documentElement.contains(target)) {
    return false;
  }
  return node && !isOrContainsTarget(node, target);
}
function isOrContainsTarget(node, target) {
  return node === target || node.contains(target);
}
function getOwnerDocument(el) {
  return el?.ownerDocument ?? document;
}
const INTERACTION_KEYS = [kbd.ARROW_LEFT, kbd.ESCAPE, kbd.ARROW_RIGHT, kbd.SHIFT, kbd.CAPS_LOCK, kbd.CONTROL, kbd.ALT, kbd.META, kbd.ENTER, kbd.F1, kbd.F2, kbd.F3, kbd.F4, kbd.F5, kbd.F6, kbd.F7, kbd.F8, kbd.F9, kbd.F10, kbd.F11, kbd.F12];
const defaults = {
  positioning: {
    placement: "bottom",
    sameWidth: true
  },
  scrollAlignment: "nearest",
  loop: true,
  defaultOpen: false,
  closeOnOutsideClick: true,
  preventScroll: true,
  closeOnEscape: true,
  forceVisible: false,
  portal: void 0,
  builder: "listbox",
  disabled: false,
  required: false,
  name: void 0,
  typeahead: true,
  highlightOnHover: true,
  onOutsideClick: void 0
};
const listboxIdParts = ["trigger", "menu", "label"];
function createListbox(props) {
  const withDefaults = { ...defaults, ...props };
  const activeTrigger = withGet(writable(null));
  const highlightedItem = withGet(writable(null));
  const selectedWritable = withDefaults.selected ?? writable(withDefaults.defaultSelected);
  const selected = overridable(selectedWritable, withDefaults?.onSelectedChange);
  const highlighted = derived(highlightedItem, ($highlightedItem) => $highlightedItem ? getOptionProps($highlightedItem) : void 0);
  const openWritable = withDefaults.open ?? writable(withDefaults.defaultOpen);
  const open = overridable(openWritable, withDefaults?.onOpenChange);
  const options = toWritableStores({
    ...omit(withDefaults, "open", "defaultOpen", "builder", "ids"),
    multiple: withDefaults.multiple ?? false
  });
  const { scrollAlignment, loop, closeOnOutsideClick, closeOnEscape, preventScroll, portal, forceVisible, positioning, multiple, arrowSize, disabled, required, typeahead, name: nameProp, highlightOnHover, onOutsideClick } = options;
  const { name, selector } = createElHelpers(withDefaults.builder);
  const ids = toWritableStores({ ...generateIds(listboxIdParts), ...withDefaults.ids });
  const { handleTypeaheadSearch } = createTypeaheadSearch({
    onMatch: (element2) => {
      highlightedItem.set(element2);
      element2.scrollIntoView({ block: scrollAlignment.get() });
    },
    getCurrentItem() {
      return highlightedItem.get();
    }
  });
  function getOptionProps(el) {
    const value = el.getAttribute("data-value");
    const label2 = el.getAttribute("data-label");
    const disabled2 = el.hasAttribute("data-disabled");
    return {
      value: value ? JSON.parse(value) : value,
      label: label2 ?? el.textContent ?? void 0,
      disabled: disabled2 ? true : false
    };
  }
  const setOption = (newOption) => {
    selected.update(($option) => {
      const $multiple = multiple.get();
      if ($multiple) {
        const optionArr = Array.isArray($option) ? [...$option] : [];
        return toggle(newOption, optionArr, (itemA, itemB) => dequal(itemA.value, itemB.value));
      }
      return newOption;
    });
  };
  function selectItem(item) {
    const props2 = getOptionProps(item);
    setOption(props2);
  }
  async function openMenu() {
    open.set(true);
    const triggerEl = document.getElementById(ids.trigger.get());
    if (!triggerEl)
      return;
    if (triggerEl !== activeTrigger.get())
      activeTrigger.set(triggerEl);
    await tick();
    const menuElement = document.getElementById(ids.menu.get());
    if (!isHTMLElement(menuElement))
      return;
    const selectedItem = menuElement.querySelector("[aria-selected=true]");
    if (!isHTMLElement(selectedItem))
      return;
    highlightedItem.set(selectedItem);
  }
  function closeMenu() {
    open.set(false);
    highlightedItem.set(null);
  }
  const isVisible = derivedVisible({ open, forceVisible, activeTrigger });
  const isSelected = derived([selected], ([$selected]) => {
    return (value) => {
      if (Array.isArray($selected)) {
        return $selected.some((o) => dequal(o.value, value));
      }
      if (isObject(value)) {
        return dequal($selected?.value, stripValues(value, void 0));
      }
      return dequal($selected?.value, value);
    };
  });
  const isHighlighted = derived([highlighted], ([$value]) => {
    return (item) => {
      return dequal($value?.value, item);
    };
  });
  const trigger = makeElement(name("trigger"), {
    stores: [open, highlightedItem, disabled, ids.menu, ids.trigger, ids.label],
    returned: ([$open, $highlightedItem, $disabled, $menuId, $triggerId, $labelId]) => {
      return {
        "aria-activedescendant": $highlightedItem?.id,
        "aria-autocomplete": "list",
        "aria-controls": $menuId,
        "aria-expanded": $open,
        "aria-labelledby": $labelId,
        // autocomplete: 'off',
        id: $triggerId,
        role: "combobox",
        disabled: disabledAttr($disabled),
        type: withDefaults.builder === "select" ? "button" : void 0
      };
    },
    action: (node) => {
      const isInput = isHTMLInputElement(node);
      const unsubscribe = executeCallbacks(
        addMeltEventListener(node, "click", () => {
          node.focus();
          const $open = open.get();
          if ($open) {
            closeMenu();
          } else {
            openMenu();
          }
        }),
        // Handle all input key events including typing, meta, and navigation.
        addMeltEventListener(node, "keydown", (e) => {
          const $open = open.get();
          if (!$open) {
            if (INTERACTION_KEYS.includes(e.key)) {
              return;
            }
            if (e.key === kbd.TAB) {
              return;
            }
            if (e.key === kbd.BACKSPACE && isInput && node.value === "") {
              return;
            }
            if (e.key === kbd.SPACE && isHTMLButtonElement(node)) {
              return;
            }
            openMenu();
            tick().then(() => {
              const $selectedItem = selected.get();
              if ($selectedItem)
                return;
              const menuEl = document.getElementById(ids.menu.get());
              if (!isHTMLElement(menuEl))
                return;
              const enabledItems = Array.from(menuEl.querySelectorAll(`${selector("item")}:not([data-disabled]):not([data-hidden])`)).filter((item) => isHTMLElement(item));
              if (!enabledItems.length)
                return;
              if (e.key === kbd.ARROW_DOWN) {
                highlightedItem.set(enabledItems[0]);
                enabledItems[0].scrollIntoView({ block: scrollAlignment.get() });
              } else if (e.key === kbd.ARROW_UP) {
                highlightedItem.set(last(enabledItems));
                last(enabledItems).scrollIntoView({ block: scrollAlignment.get() });
              }
            });
          }
          if (e.key === kbd.TAB) {
            closeMenu();
            return;
          }
          if (e.key === kbd.ENTER && !e.isComposing || e.key === kbd.SPACE && isHTMLButtonElement(node)) {
            e.preventDefault();
            const $highlightedItem = highlightedItem.get();
            if ($highlightedItem) {
              selectItem($highlightedItem);
            }
            if (!multiple.get()) {
              closeMenu();
            }
          }
          if (e.key === kbd.ARROW_UP && e.altKey) {
            closeMenu();
          }
          if (FIRST_LAST_KEYS.includes(e.key)) {
            e.preventDefault();
            const menuElement = document.getElementById(ids.menu.get());
            if (!isHTMLElement(menuElement))
              return;
            const itemElements = getOptions(menuElement);
            if (!itemElements.length)
              return;
            const candidateNodes = itemElements.filter((opt) => !isElementDisabled(opt) && opt.dataset.hidden === void 0);
            const $currentItem = highlightedItem.get();
            const currentIndex = $currentItem ? candidateNodes.indexOf($currentItem) : -1;
            const $loop = loop.get();
            const $scrollAlignment = scrollAlignment.get();
            let nextItem;
            switch (e.key) {
              case kbd.ARROW_DOWN:
                nextItem = next(candidateNodes, currentIndex, $loop);
                break;
              case kbd.ARROW_UP:
                nextItem = prev(candidateNodes, currentIndex, $loop);
                break;
              case kbd.PAGE_DOWN:
                nextItem = forward(candidateNodes, currentIndex, 10, $loop);
                break;
              case kbd.PAGE_UP:
                nextItem = back(candidateNodes, currentIndex, 10, $loop);
                break;
              case kbd.HOME:
                nextItem = candidateNodes[0];
                break;
              case kbd.END:
                nextItem = last(candidateNodes);
                break;
              default:
                return;
            }
            highlightedItem.set(nextItem);
            nextItem?.scrollIntoView({ block: $scrollAlignment });
          } else if (typeahead.get()) {
            const menuEl = document.getElementById(ids.menu.get());
            if (!isHTMLElement(menuEl))
              return;
            handleTypeaheadSearch(e.key, getOptions(menuEl));
          }
        })
      );
      let unsubEscapeKeydown = noop;
      const escape = useEscapeKeydown(node, {
        handler: closeMenu,
        enabled: derived([open, closeOnEscape], ([$open, $closeOnEscape]) => {
          return $open && $closeOnEscape;
        })
      });
      if (escape && escape.destroy) {
        unsubEscapeKeydown = escape.destroy;
      }
      return {
        destroy() {
          unsubscribe();
          unsubEscapeKeydown();
        }
      };
    }
  });
  const menu = makeElement(name("menu"), {
    stores: [isVisible, ids.menu],
    returned: ([$isVisible, $menuId]) => {
      return {
        hidden: $isVisible ? void 0 : true,
        id: $menuId,
        role: "listbox",
        style: styleToString({ display: $isVisible ? void 0 : "none" })
      };
    },
    action: (node) => {
      let unsubPopper = noop;
      const unsubscribe = executeCallbacks(
        // Bind the popper portal to the input element.
        effect([isVisible, portal, closeOnOutsideClick, positioning, activeTrigger], ([$isVisible, $portal, $closeOnOutsideClick, $positioning, $activeTrigger]) => {
          unsubPopper();
          if (!$isVisible || !$activeTrigger)
            return;
          tick().then(() => {
            unsubPopper();
            const ignoreHandler = createClickOutsideIgnore(ids.trigger.get());
            unsubPopper = usePopper(node, {
              anchorElement: $activeTrigger,
              open,
              options: {
                floating: $positioning,
                focusTrap: null,
                modal: {
                  closeOnInteractOutside: $closeOnOutsideClick,
                  onClose: closeMenu,
                  open: $isVisible,
                  shouldCloseOnInteractOutside: (e) => {
                    onOutsideClick.get()?.(e);
                    if (e.defaultPrevented)
                      return false;
                    const target = e.target;
                    if (!isElement(target))
                      return false;
                    if (target === $activeTrigger || $activeTrigger.contains(target)) {
                      return false;
                    }
                    if (ignoreHandler(e))
                      return false;
                    return true;
                  }
                },
                escapeKeydown: null,
                portal: getPortalDestination(node, $portal)
              }
            }).destroy;
          });
        })
      );
      return {
        destroy: () => {
          unsubscribe();
          unsubPopper();
        }
      };
    }
  });
  const { elements: { root: labelBuilder } } = createLabel();
  const { action: labelAction } = get(labelBuilder);
  const label = makeElement(name("label"), {
    stores: [ids.label, ids.trigger],
    returned: ([$labelId, $triggerId]) => {
      return {
        id: $labelId,
        for: $triggerId
      };
    },
    action: labelAction
  });
  const option = makeElement(name("option"), {
    stores: [isSelected],
    returned: ([$isSelected]) => (props2) => {
      const selected2 = $isSelected(props2.value);
      return {
        "data-value": JSON.stringify(props2.value),
        "data-label": props2.label,
        "data-disabled": disabledAttr(props2.disabled),
        "aria-disabled": props2.disabled ? true : void 0,
        "aria-selected": selected2,
        "data-selected": selected2 ? "" : void 0,
        id: generateId$1(),
        role: "option"
      };
    },
    action: (node) => {
      const unsubscribe = executeCallbacks(addMeltEventListener(node, "click", (e) => {
        if (isElementDisabled(node)) {
          e.preventDefault();
          return;
        }
        selectItem(node);
        if (!multiple.get()) {
          closeMenu();
        }
      }), effect(highlightOnHover, ($highlightOnHover) => {
        if (!$highlightOnHover)
          return;
        const unsub = executeCallbacks(addMeltEventListener(node, "mouseover", () => {
          highlightedItem.set(node);
        }), addMeltEventListener(node, "mouseleave", () => {
          highlightedItem.set(null);
        }));
        return unsub;
      }));
      return { destroy: unsubscribe };
    }
  });
  const group = makeElement(name("group"), {
    returned: () => {
      return (groupId) => ({
        role: "group",
        "aria-labelledby": groupId
      });
    }
  });
  const groupLabel = makeElement(name("group-label"), {
    returned: () => {
      return (groupId) => ({
        id: groupId
      });
    }
  });
  const hiddenInput = createHiddenInput({
    value: derived([selected], ([$selected]) => {
      const value = Array.isArray($selected) ? $selected.map((o) => o.value) : $selected?.value;
      return typeof value === "string" ? value : JSON.stringify(value);
    }),
    name: readonly(nameProp),
    required,
    prefix: withDefaults.builder
  });
  const arrow = makeElement(name("arrow"), {
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
  safeOnMount(() => {
    if (!isBrowser)
      return;
    const menuEl = document.getElementById(ids.menu.get());
    const triggerEl = document.getElementById(ids.trigger.get());
    if (triggerEl) {
      activeTrigger.set(triggerEl);
    }
    if (!menuEl)
      return;
    const selectedEl = menuEl.querySelector("[data-selected]");
    if (!isHTMLElement(selectedEl))
      return;
  });
  effect([highlightedItem], ([$highlightedItem]) => {
    if (!isBrowser)
      return;
    const menuElement = document.getElementById(ids.menu.get());
    if (!isHTMLElement(menuElement))
      return;
    getOptions(menuElement).forEach((node) => {
      if (node === $highlightedItem) {
        addHighlight(node);
      } else {
        removeHighlight(node);
      }
    });
  });
  effect([open], ([$open]) => {
    if (!isBrowser)
      return;
    let unsubScroll = noop;
    if (preventScroll.get() && $open) {
      unsubScroll = removeScroll();
    }
    return () => {
      unsubScroll();
    };
  });
  return {
    ids,
    elements: {
      trigger,
      group,
      option,
      menu,
      groupLabel,
      label,
      hiddenInput,
      arrow
    },
    states: {
      open,
      selected,
      highlighted,
      highlightedItem
    },
    helpers: {
      isSelected,
      isHighlighted,
      closeMenu
    },
    options
  };
}
function createSelect(props) {
  const listbox = createListbox({ ...props, builder: "select" });
  const selectedLabel = derived(listbox.states.selected, ($selected) => {
    if (Array.isArray($selected)) {
      return $selected.map((o) => o.label).join(", ");
    }
    return $selected?.label ?? "";
  });
  return {
    ...listbox,
    elements: {
      ...listbox.elements
    },
    states: {
      ...listbox.states,
      selectedLabel
    }
  };
}
function generateId() {
  return nanoid(10);
}
function arraysAreEqual(arr1, arr2) {
  if (arr1.length !== arr2.length) {
    return false;
  }
  return arr1.every((value, index) => value === arr2[index]);
}
function getSelectData() {
  const NAME = "select";
  const GROUP_NAME = "select-group";
  const ITEM_NAME = "select-item";
  const PARTS = [
    "arrow",
    "content",
    "group",
    "item",
    "indicator",
    "input",
    "label",
    "trigger",
    "value"
  ];
  return {
    NAME,
    GROUP_NAME,
    ITEM_NAME,
    PARTS
  };
}
function getCtx() {
  const { NAME } = getSelectData();
  return getContext(NAME);
}
function setCtx(props) {
  const { NAME, PARTS } = getSelectData();
  const getAttrs = createBitAttrs(NAME, PARTS);
  const select = {
    ...createSelect({ ...removeUndefined(props), forceVisible: true }),
    getAttrs
  };
  setContext(NAME, select);
  return {
    ...select,
    updateOption: getOptionUpdater(select.options)
  };
}
function setGroupCtx() {
  const { GROUP_NAME } = getSelectData();
  const id = generateId();
  setContext(GROUP_NAME, id);
  const { elements: { group }, getAttrs } = getCtx();
  return { group, id, getAttrs };
}
function setItemCtx(value) {
  const { ITEM_NAME } = getSelectData();
  const select = getCtx();
  setContext(ITEM_NAME, value);
  return select;
}
function getItemIndicator() {
  const { ITEM_NAME } = getSelectData();
  const { helpers: { isSelected }, getAttrs } = getCtx();
  const value = getContext(ITEM_NAME);
  return {
    value,
    isSelected,
    getAttrs
  };
}
function updatePositioning(props) {
  const defaultPlacement = {
    side: "bottom",
    align: "center",
    sameWidth: true
  };
  const withDefaults = { ...defaultPlacement, ...props };
  const { options: { positioning } } = getCtx();
  const updater = getPositioningUpdater(positioning);
  updater(withDefaults);
}
function Select($$payload, $$props) {
  push();
  var $$store_subs;
  let required = fallback($$props["required"], () => void 0, true);
  let disabled = fallback($$props["disabled"], () => void 0, true);
  let preventScroll = fallback($$props["preventScroll"], () => void 0, true);
  let loop = fallback($$props["loop"], () => void 0, true);
  let closeOnEscape = fallback($$props["closeOnEscape"], () => void 0, true);
  let closeOnOutsideClick = fallback($$props["closeOnOutsideClick"], () => void 0, true);
  let portal = fallback($$props["portal"], () => void 0, true);
  let name = fallback($$props["name"], () => void 0, true);
  let multiple = fallback($$props["multiple"], false);
  let selected = fallback($$props["selected"], () => void 0, true);
  let onSelectedChange = fallback($$props["onSelectedChange"], () => void 0, true);
  let open = fallback($$props["open"], () => void 0, true);
  let onOpenChange = fallback($$props["onOpenChange"], () => void 0, true);
  let items = fallback($$props["items"], () => [], true);
  let onOutsideClick = fallback($$props["onOutsideClick"], () => void 0, true);
  let typeahead = fallback($$props["typeahead"], () => void 0, true);
  const {
    states: { open: localOpen, selected: localSelected },
    updateOption,
    ids
  } = setCtx({
    required,
    disabled,
    preventScroll,
    loop,
    closeOnEscape,
    closeOnOutsideClick,
    portal,
    name,
    onOutsideClick,
    multiple,
    forceVisible: true,
    defaultSelected: Array.isArray(selected) ? [...selected] : selected,
    defaultOpen: open,
    onSelectedChange: ({ next: next2 }) => {
      if (Array.isArray(next2)) {
        if (!Array.isArray(selected) || !arraysAreEqual(selected, next2)) {
          onSelectedChange?.(next2);
          selected = next2;
          return next2;
        }
        return next2;
      }
      if (selected !== next2) {
        onSelectedChange?.(next2);
        selected = next2;
      }
      return next2;
    },
    onOpenChange: ({ next: next2 }) => {
      if (open !== next2) {
        onOpenChange?.(next2);
        open = next2;
      }
      return next2;
    },
    items,
    typeahead
  });
  const idValues = derived([ids.menu, ids.trigger, ids.label], ([$menuId, $triggerId, $labelId]) => ({
    menu: $menuId,
    trigger: $triggerId,
    label: $labelId
  }));
  open !== void 0 && localOpen.set(open);
  selected !== void 0 && localSelected.set(Array.isArray(selected) ? [...selected] : selected);
  updateOption("required", required);
  updateOption("disabled", disabled);
  updateOption("preventScroll", preventScroll);
  updateOption("loop", loop);
  updateOption("closeOnEscape", closeOnEscape);
  updateOption("closeOnOutsideClick", closeOnOutsideClick);
  updateOption("portal", portal);
  updateOption("name", name);
  updateOption("multiple", multiple);
  updateOption("onOutsideClick", onOutsideClick);
  updateOption("typeahead", typeahead);
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
    required,
    disabled,
    preventScroll,
    loop,
    closeOnEscape,
    closeOnOutsideClick,
    portal,
    name,
    multiple,
    selected,
    onSelectedChange,
    open,
    onOpenChange,
    items,
    onOutsideClick,
    typeahead
  });
  pop();
}
function Select_content$1($$payload, $$props) {
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
  let side = fallback($$props["side"], "bottom");
  let align = fallback($$props["align"], "center");
  let sideOffset = fallback($$props["sideOffset"], 0);
  let alignOffset = fallback($$props["alignOffset"], 0);
  let collisionPadding = fallback($$props["collisionPadding"], 8);
  let avoidCollisions = fallback($$props["avoidCollisions"], true);
  let collisionBoundary = fallback($$props["collisionBoundary"], () => void 0, true);
  let sameWidth = fallback($$props["sameWidth"], true);
  let fitViewport = fallback($$props["fitViewport"], false);
  let strategy = fallback($$props["strategy"], "absolute");
  let overlap = fallback($$props["overlap"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { menu },
    states: { open },
    ids,
    getAttrs
  } = getCtx();
  const attrs = getAttrs("content");
  if (id) {
    ids.menu.set(id);
  }
  builder = store_get($$store_subs ??= {}, "$menu", menu);
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
function Select_group($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "el"]);
  push();
  var $$store_subs;
  let builder;
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const { group, id, getAttrs } = setGroupCtx();
  const attrs = getAttrs("group");
  builder = store_get($$store_subs ??= {}, "$group", group)(id);
  Object.assign(builder, attrs);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!----></div>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, el });
  pop();
}
function Select_item$1($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "value",
    "disabled",
    "label",
    "asChild",
    "el"
  ]);
  push();
  var $$store_subs;
  let builder, isSelected;
  let value = $$props["value"];
  let disabled = fallback($$props["disabled"], () => void 0, true);
  let label = fallback($$props["label"], () => void 0, true);
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { option: item },
    helpers: { isSelected: isSelectedStore },
    getAttrs
  } = setItemCtx(value);
  const attrs = getAttrs("item");
  builder = store_get($$store_subs ??= {}, "$item", item)({ value, disabled, label });
  Object.assign(builder, attrs);
  isSelected = store_get($$store_subs ??= {}, "$isSelectedStore", isSelectedStore)(value);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder, isSelected }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<div${spread_attributes({ ...builder, ...$$restProps })}><!---->`;
    slot($$payload, $$props, "default", { builder, isSelected }, () => {
      $$payload.out += `${escape_html(label || value)}`;
    });
    $$payload.out += `<!----></div>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { value, disabled, label, asChild, el });
  pop();
}
function Select_item_indicator($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "el"]);
  push();
  var $$store_subs;
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const { isSelected, value, getAttrs } = getItemIndicator();
  const attrs = getAttrs("indicator");
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot(
      $$payload,
      $$props,
      "default",
      {
        attrs,
        isSelected: store_get($$store_subs ??= {}, "$isSelected", isSelected)(value)
      },
      null
    );
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<div${spread_attributes({ ...$$restProps, ...attrs })}>`;
    if (store_get($$store_subs ??= {}, "$isSelected", isSelected)(value)) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<!---->`;
      slot(
        $$payload,
        $$props,
        "default",
        {
          attrs,
          isSelected: store_get($$store_subs ??= {}, "$isSelected", isSelected)(value)
        },
        null
      );
      $$payload.out += `<!---->`;
    } else {
      $$payload.out += "<!--[!-->";
    }
    $$payload.out += `<!--]--></div>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, el });
  pop();
}
function Select_trigger$1($$payload, $$props) {
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
function Select_value($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["placeholder", "asChild", "el"]);
  push();
  var $$store_subs;
  let label;
  let placeholder = fallback($$props["placeholder"], "");
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const { states: { selectedLabel }, getAttrs } = getCtx();
  const attrs = getAttrs("value");
  label = store_get($$store_subs ??= {}, "$selectedLabel", selectedLabel);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { label, attrs }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<span${spread_attributes({
      ...$$restProps,
      ...attrs,
      "data-placeholder": !label ? "" : void 0
    })}>${escape_html(label || placeholder)}</span>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { placeholder, asChild, el });
  pop();
}
function Chevron_down($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "m6 9 6 6 6-6" }]];
  Icon($$payload, spread_props([
    { name: "chevron-down" },
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
function X($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M18 6 6 18" }],
    ["path", { "d": "m6 6 12 12" }]
  ];
  Icon($$payload, spread_props([
    { name: "x" },
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
function Table_caption($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  $$payload.out += `<caption${spread_attributes({
    class: cn("text-muted-foreground mt-4 text-sm", className),
    ...$$restProps
  })}><!---->`;
  slot($$payload, $$props, "default", {}, null);
  $$payload.out += `<!----></caption>`;
  bind_props($$props, { class: className });
  pop();
}
const alertVariants = tv({
  base: "[&>svg]:text-foreground relative w-full rounded-lg border p-4 [&:has(svg)]:pl-11 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4",
  variants: {
    variant: {
      default: "bg-background text-foreground",
      destructive: "border-destructive/50 text-destructive text-destructive dark:border-destructive [&>svg]:text-destructive"
    }
  },
  defaultVariants: {
    variant: "default"
  }
});
function Badge($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "href", "variant"]);
  push();
  let className = fallback($$props["class"], void 0);
  let href = fallback($$props["href"], void 0);
  let variant = fallback($$props["variant"], "default");
  const $$tag = href ? "a" : "span";
  element(
    $$payload,
    $$tag,
    () => {
      $$payload.out += `${spread_attributes({
        href,
        class: cn(badgeVariants({ variant, className })),
        ...$$restProps
      })}`;
    },
    () => {
      $$payload.out += `<!---->`;
      slot($$payload, $$props, "default", {}, null);
      $$payload.out += `<!---->`;
    }
  );
  bind_props($$props, { class: className, href, variant });
  pop();
}
const badgeVariants = tv({
  base: "focus:ring-ring inline-flex select-none items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground hover:bg-primary/80 border-transparent",
      secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 border-transparent",
      destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/80 border-transparent",
      outline: "text-foreground",
      warning: "border-transparent bg-yellow-200 text-yellow-800 dark:bg-yellow-400/20 dark:text-yellow-400",
      success: "border-transparent bg-green-200 text-green-800 dark:bg-green-400/20 dark:text-green-400"
    }
  },
  defaultVariants: {
    variant: "default"
  }
});
function Select_item($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "value", "label", "disabled"]);
  push();
  let className = fallback($$props["class"], void 0);
  let value = $$props["value"];
  let label = fallback($$props["label"], void 0);
  let disabled = fallback($$props["disabled"], void 0);
  Select_item$1($$payload, spread_props([
    {
      value,
      disabled,
      label,
      class: cn("data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className)
    },
    $$restProps,
    {
      children: ($$payload2) => {
        $$payload2.out += `<span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">`;
        Select_item_indicator($$payload2, {
          children: ($$payload3) => {
            Check($$payload3, { class: "h-4 w-4" });
          },
          $$slots: { default: true }
        });
        $$payload2.out += `<!----></span> <!---->`;
        slot($$payload2, $$props, "default", {}, () => {
          $$payload2.out += `${escape_html(label || value)}`;
        });
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
  bind_props($$props, { class: className, value, label, disabled });
  pop();
}
function cubic_out(t) {
  const f = t - 1;
  return f * f * f + 1;
}
function scale(node, { delay = 0, duration = 400, easing = cubic_out, start = 0, opacity = 0 } = {}) {
  const style = getComputedStyle(node);
  const target_opacity = +style.opacity;
  const transform = style.transform === "none" ? "" : style.transform;
  const sd = 1 - start;
  const od = target_opacity * (1 - opacity);
  return {
    delay,
    duration,
    easing,
    css: (_t, u) => `
			transform: ${transform} scale(${1 - sd * u});
			opacity: ${target_opacity - od * u}
		`
  };
}
function Select_content($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "sideOffset",
    "inTransition",
    "inTransitionConfig",
    "outTransition",
    "outTransitionConfig",
    "class"
  ]);
  push();
  let sideOffset = fallback($$props["sideOffset"], 4);
  let inTransition = fallback($$props["inTransition"], flyAndScale);
  let inTransitionConfig = fallback($$props["inTransitionConfig"], void 0);
  let outTransition = fallback($$props["outTransition"], scale);
  let outTransitionConfig = fallback($$props["outTransitionConfig"], () => ({ start: 0.95, opacity: 0, duration: 50 }), true);
  let className = fallback($$props["class"], void 0);
  Select_content$1($$payload, spread_props([
    {
      inTransition,
      inTransitionConfig,
      outTransition,
      outTransitionConfig,
      sideOffset,
      class: cn("bg-popover text-popover-foreground relative z-50 min-w-[8rem] overflow-hidden rounded-md border shadow-md outline-none", className)
    },
    $$restProps,
    {
      children: ($$payload2) => {
        $$payload2.out += `<div class="w-full p-1"><!---->`;
        slot($$payload2, $$props, "default", {}, null);
        $$payload2.out += `<!----></div>`;
      },
      $$slots: { default: true }
    }
  ]));
  bind_props($$props, {
    sideOffset,
    inTransition,
    inTransitionConfig,
    outTransition,
    outTransitionConfig,
    class: className
  });
  pop();
}
function Select_trigger($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class"]);
  push();
  let className = fallback($$props["class"], void 0);
  Select_trigger$1($$payload, spread_props([
    {
      class: cn("border-input bg-background ring-offset-background focus-visible:ring-ring aria-[invalid]:border-destructive data-[placeholder]:[&>span]:text-muted-foreground flex h-10 w-full items-center justify-between rounded-md border px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1", className)
    },
    $$restProps,
    {
      children: invalid_default_snippet,
      $$slots: {
        default: ($$payload2, { builder }) => {
          $$payload2.out += `<!---->`;
          slot($$payload2, $$props, "default", { builder }, null);
          $$payload2.out += `<!----> <div>`;
          Chevron_down($$payload2, { class: "h-4 w-4 opacity-50" });
          $$payload2.out += `<!----></div>`;
        }
      }
    }
  ]));
  bind_props($$props, { class: className });
  pop();
}
const Root = Select;
const Group = Select_group;
const Value = Select_value;
function RunsWithFilters($$payload, $$props) {
  push();
  var $$store_subs;
  let modelVersions, codeRevisions, filteredRuns;
  let runsList = $$props["runsList"];
  let isLoading = $$props["isLoading"];
  let loadingError = $$props["loadingError"];
  let showFilters = fallback($$props["showFilters"], false);
  let showViewAll = fallback($$props["showViewAll"], false);
  let initialSearchTerm = fallback($$props["initialSearchTerm"], "");
  const dateRanges = [
    "",
    ...[
      "Today",
      "This Week",
      "This Month",
      "Custom Range"
    ]
  ];
  let selectedDateRange = { value: "", label: "" };
  let selectedModelVersion = { value: "", label: "" };
  let selectedCodeRevision = { value: "", label: "" };
  let searchTerm = initialSearchTerm;
  modelVersions = [
    "",
    ...new Set(runsList.map((run) => run.model))
  ];
  codeRevisions = [
    "",
    ...new Set(runsList.map((run) => run.revision))
  ];
  {
    if (initialSearchTerm) {
      searchTerm = initialSearchTerm;
    }
  }
  filteredRuns = runsList.filter((run) => {
    if (selectedDateRange?.value) {
      const runDate = new Date(run.created_at);
      const today = /* @__PURE__ */ new Date();
      switch (selectedDateRange.value) {
        case "today":
          if (runDate.toDateString() !== today.toDateString()) return false;
          break;
        case "this week":
          const weekAgo = new Date(today.setDate(today.getDate() - 7));
          if (runDate < weekAgo) return false;
          break;
        case "this month":
          const monthAgo = new Date(today.setMonth(today.getMonth() - 1));
          if (runDate < monthAgo) return false;
          break;
      }
    }
    if (selectedModelVersion?.value && run.model !== selectedModelVersion.value) return false;
    if (selectedCodeRevision?.value && run.revision !== selectedCodeRevision.value) return false;
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return run.id.toLowerCase().includes(searchLower) || run.model.toLowerCase().includes(searchLower) || run.revision.toLowerCase().includes(searchLower);
    }
    return true;
  });
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    if (showFilters) {
      $$payload2.out += "<!--[-->";
      Card($$payload2, {
        children: ($$payload3) => {
          Card_content($$payload3, {
            class: "flex flex-wrap gap-4",
            children: ($$payload4) => {
              $$payload4.out += `<div class="flex flex-col space-y-1.5">`;
              Label($$payload4, {
                for: "date-range",
                children: ($$payload5) => {
                  $$payload5.out += `<!---->Date Range`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----> `;
              Root($$payload4, {
                selected: selectedDateRange,
                onSelectedChange: (v) => {
                  if (v) selectedDateRange = { value: v.value, label: v.label };
                  else selectedDateRange = { value: "", label: "" };
                },
                children: ($$payload5) => {
                  Select_trigger($$payload5, {
                    class: "w-[180px]",
                    id: "date-range",
                    children: ($$payload6) => {
                      Value($$payload6, { placeholder: "Select date range" });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!----> `;
                  Select_content($$payload5, {
                    children: ($$payload6) => {
                      Group($$payload6, {
                        children: ($$payload7) => {
                          const each_array = ensure_array_like(dateRanges);
                          $$payload7.out += `<!--[-->`;
                          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
                            let range = each_array[$$index];
                            Select_item($$payload7, {
                              value: range.toLowerCase(),
                              label: range,
                              class: "min-h-[32px]",
                              children: ($$payload8) => {
                                $$payload8.out += `<!---->${escape_html(range)}`;
                              },
                              $$slots: { default: true }
                            });
                          }
                          $$payload7.out += `<!--]-->`;
                        },
                        $$slots: { default: true }
                      });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!---->`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----></div> <div class="flex flex-col space-y-1.5">`;
              Label($$payload4, {
                for: "model-version",
                children: ($$payload5) => {
                  $$payload5.out += `<!---->Model Version`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----> `;
              Root($$payload4, {
                selected: selectedModelVersion,
                onSelectedChange: (v) => {
                  if (v) selectedModelVersion = { value: v.value, label: v.label };
                  else selectedModelVersion = { value: "", label: "" };
                },
                children: ($$payload5) => {
                  Select_trigger($$payload5, {
                    class: "w-[180px]",
                    id: "model-version",
                    children: ($$payload6) => {
                      Value($$payload6, { placeholder: "Select model version" });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!----> `;
                  Select_content($$payload5, {
                    children: ($$payload6) => {
                      Group($$payload6, {
                        children: ($$payload7) => {
                          const each_array_1 = ensure_array_like(modelVersions);
                          $$payload7.out += `<!--[-->`;
                          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
                            let version = each_array_1[$$index_1];
                            Select_item($$payload7, {
                              value: version,
                              label: version,
                              class: "min-h-[32px]",
                              children: ($$payload8) => {
                                $$payload8.out += `<!---->${escape_html(version)}`;
                              },
                              $$slots: { default: true }
                            });
                          }
                          $$payload7.out += `<!--]-->`;
                        },
                        $$slots: { default: true }
                      });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!---->`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----></div> <div class="flex flex-col space-y-1.5">`;
              Label($$payload4, {
                for: "code-revision",
                children: ($$payload5) => {
                  $$payload5.out += `<!---->Code Revision`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----> `;
              Root($$payload4, {
                selected: selectedCodeRevision,
                onSelectedChange: (v) => {
                  if (v) selectedCodeRevision = { value: v.value, label: v.label };
                  else selectedCodeRevision = { value: "", label: "" };
                },
                children: ($$payload5) => {
                  Select_trigger($$payload5, {
                    class: "w-[180px]",
                    id: "code-revision",
                    children: ($$payload6) => {
                      Value($$payload6, { placeholder: "Select code revision" });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!----> `;
                  Select_content($$payload5, {
                    children: ($$payload6) => {
                      Group($$payload6, {
                        children: ($$payload7) => {
                          const each_array_2 = ensure_array_like(codeRevisions);
                          $$payload7.out += `<!--[-->`;
                          for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
                            let revision = each_array_2[$$index_2];
                            Select_item($$payload7, {
                              value: revision,
                              label: revision,
                              class: "min-h-[32px]",
                              children: ($$payload8) => {
                                $$payload8.out += `<!---->${escape_html(revision)}`;
                              },
                              $$slots: { default: true }
                            });
                          }
                          $$payload7.out += `<!--]-->`;
                        },
                        $$slots: { default: true }
                      });
                    },
                    $$slots: { default: true }
                  });
                  $$payload5.out += `<!---->`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----></div>  <div class="flex flex-col space-y-1.5 flex-grow">`;
              Label($$payload4, {
                for: "search",
                children: ($$payload5) => {
                  $$payload5.out += `<!---->Search`;
                },
                $$slots: { default: true }
              });
              $$payload4.out += `<!----> <div class="relative">`;
              Input($$payload4, {
                id: "search",
                placeholder: "Search by Run ID, name, or metadata",
                get value() {
                  return searchTerm;
                },
                set value($$value) {
                  searchTerm = $$value;
                  $$settled = false;
                }
              });
              $$payload4.out += `<!----> `;
              if (searchTerm) {
                $$payload4.out += "<!--[-->";
                $$payload4.out += `<button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full bg-gray-100 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">`;
                X($$payload4, { class: "h-4 w-4 text-gray-500" });
                $$payload4.out += `<!----></button>`;
              } else {
                $$payload4.out += "<!--[!-->";
              }
              $$payload4.out += `<!--]--></div></div>`;
            },
            $$slots: { default: true }
          });
        },
        $$slots: { default: true }
      });
    } else {
      $$payload2.out += "<!--[!-->";
    }
    $$payload2.out += `<!--]--> `;
    Card($$payload2, {
      children: ($$payload3) => {
        if (isLoading) {
          $$payload3.out += "<!--[-->";
          Loading($$payload3, { message: "Loading recent runs..." });
        } else {
          $$payload3.out += "<!--[!-->";
          if (loadingError) {
            $$payload3.out += "<!--[-->";
            ErrorDisplay($$payload3, { errorMessage: loadingError, onRetry: () => {
            } });
          } else {
            $$payload3.out += "<!--[!-->";
            Table($$payload3, {
              children: ($$payload4) => {
                if (showViewAll) {
                  $$payload4.out += "<!--[-->";
                  Table_caption($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<a${attr("href", `/experiments#${stringify(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId))}`)}>View all runs</a>`;
                    },
                    $$slots: { default: true }
                  });
                } else {
                  $$payload4.out += "<!--[!-->";
                }
                $$payload4.out += `<!--]--> `;
                Table_header($$payload4, {
                  children: ($$payload5) => {
                    Table_row($$payload5, {
                      children: ($$payload6) => {
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Run ID`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Date &amp; Time`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Duration`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Code Revision`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Model Version`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Total Tests`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Evaluation Score`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!----> `;
                        Table_head($$payload6, {
                          children: ($$payload7) => {
                            $$payload7.out += `<!---->Test Results`;
                          },
                          $$slots: { default: true }
                        });
                        $$payload6.out += `<!---->`;
                      },
                      $$slots: { default: true }
                    });
                  },
                  $$slots: { default: true }
                });
                $$payload4.out += `<!----> `;
                Table_body($$payload4, {
                  children: ($$payload5) => {
                    const each_array_3 = ensure_array_like(filteredRuns);
                    $$payload5.out += `<!--[-->`;
                    for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
                      let run = each_array_3[$$index_3];
                      Table_row($$payload5, {
                        class: "group cursor-pointer",
                        children: ($$payload6) => {
                          Table_cell($$payload6, {
                            class: "font-medium",
                            children: ($$payload7) => {
                              Root$1($$payload7, {
                                children: ($$payload8) => {
                                  Trigger($$payload8, {
                                    children: ($$payload9) => {
                                      $$payload9.out += `<!---->${escape_html(run.id.slice(-8))}`;
                                    },
                                    $$slots: { default: true }
                                  });
                                  $$payload8.out += `<!----> `;
                                  Tooltip_content($$payload8, {
                                    children: ($$payload9) => {
                                      $$payload9.out += `<p>Run ID: ${escape_html(run.id)}</p>`;
                                    },
                                    $$slots: { default: true }
                                  });
                                  $$payload8.out += `<!---->`;
                                },
                                $$slots: { default: true }
                              });
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              TimeAgo($$payload7, { date: run.created_at });
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              if (run.finished_at) {
                                $$payload7.out += "<!--[-->";
                                $$payload7.out += `${escape_html(formatDuration(
                                  intervalToDuration({
                                    start: new Date(run.created_at),
                                    end: new Date(run.finished_at)
                                  }),
                                  { format: ["minutes", "seconds"] }
                                ))}`;
                              } else {
                                $$payload7.out += "<!--[!-->";
                                $$payload7.out += `-`;
                              }
                              $$payload7.out += `<!--]-->`;
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              $$payload7.out += `<!---->${escape_html(run.revision.slice(-8))}`;
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              $$payload7.out += `<!---->${escape_html(run.model)}`;
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              $$payload7.out += `<!---->${escape_html(run.totalTests)}`;
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            children: ($$payload7) => {
                              Badge($$payload7, {
                                variant: run.score >= 0.9 ? "success" : run.score >= 0.7 ? "warning" : "destructive",
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->${escape_html(run.score.toFixed(2))}`;
                                },
                                $$slots: { default: true }
                              });
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!----> `;
                          Table_cell($$payload6, {
                            class: "w-[300px]",
                            children: ($$payload7) => {
                              Root$1($$payload7, {
                                children: ($$payload8) => {
                                  Trigger($$payload8, {
                                    class: "w-full",
                                    children: ($$payload9) => {
                                      $$payload9.out += `<div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 overflow-hidden flex">`;
                                      if (run.pass > 0) {
                                        $$payload9.out += "<!--[-->";
                                        $$payload9.out += `<div class="bg-green-600 h-4 min-w-[5px]"${attr("style", `width: ${stringify(run.pass / run.totalTests * 100)}%`)}></div>`;
                                      } else {
                                        $$payload9.out += "<!--[!-->";
                                      }
                                      $$payload9.out += `<!--]--> `;
                                      if (run.fail > 0) {
                                        $$payload9.out += "<!--[-->";
                                        $$payload9.out += `<div class="bg-red-600 h-4 min-w-[5px]"${attr("style", `width: ${stringify(run.fail / run.totalTests * 100)}%`)}></div>`;
                                      } else {
                                        $$payload9.out += "<!--[!-->";
                                      }
                                      $$payload9.out += `<!--]--> `;
                                      if (run.regression > 0) {
                                        $$payload9.out += "<!--[-->";
                                        $$payload9.out += `<div class="bg-yellow-400 h-4 min-w-[5px]"${attr("style", `width: ${stringify(run.regression / run.totalTests * 100)}%`)}></div>`;
                                      } else {
                                        $$payload9.out += "<!--[!-->";
                                      }
                                      $$payload9.out += `<!--]--></div>`;
                                    },
                                    $$slots: { default: true }
                                  });
                                  $$payload8.out += `<!----> `;
                                  Tooltip_content($$payload8, {
                                    children: ($$payload9) => {
                                      $$payload9.out += `<div class="space-y-1"><div class="flex items-center gap-2"><div class="w-3 h-3 bg-green-600 rounded-full"></div> <span>Pass: ${escape_html(run.pass)} <span class="text-gray-400">(${escape_html((run.pass / run.totalTests * 100).toFixed(1))}%)</span></span></div> <div class="flex items-center gap-2"><div class="w-3 h-3 bg-red-600 rounded-full"></div> <span>Fail: ${escape_html(run.fail)} <span class="text-gray-400">(${escape_html((run.fail / run.totalTests * 100).toFixed(1))}%)</span></span></div> `;
                                      if (run.regression > 0) {
                                        $$payload9.out += "<!--[-->";
                                        $$payload9.out += `<div class="flex items-center gap-2"><div class="w-3 h-3 bg-yellow-400 rounded-full"></div> <span>Regression: ${escape_html(run.regression)} <span class="text-gray-400">(${escape_html((run.regression / run.totalTests * 100).toFixed(1))}%)</span></span></div>`;
                                      } else {
                                        $$payload9.out += "<!--[!-->";
                                      }
                                      $$payload9.out += `<!--]--> <div class="pt-1 border-t"><span>Total: ${escape_html(run.totalTests)}</span></div></div>`;
                                    },
                                    $$slots: { default: true }
                                  });
                                  $$payload8.out += `<!---->`;
                                },
                                $$slots: { default: true }
                              });
                            },
                            $$slots: { default: true }
                          });
                          $$payload6.out += `<!---->`;
                        },
                        $$slots: { default: true }
                      });
                    }
                    $$payload5.out += `<!--]-->`;
                  },
                  $$slots: { default: true }
                });
                $$payload4.out += `<!---->`;
              },
              $$slots: { default: true }
            });
          }
          $$payload3.out += `<!--]-->`;
        }
        $$payload3.out += `<!--]-->`;
      },
      $$slots: { default: true }
    });
    $$payload2.out += `<!---->`;
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, {
    runsList,
    isLoading,
    loadingError,
    showFilters,
    showViewAll,
    initialSearchTerm
  });
  pop();
}
export {
  RunsWithFilters as R,
  alertVariants as a
};
