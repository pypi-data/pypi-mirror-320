import { a9 as head, R as pop, P as push } from "../../../../chunks/index.js";
import { a as Loading } from "../../../../chunks/Loading.js";
import "clsx";
import "../../../../chunks/index3.js";
function _page($$payload, $$props) {
  push();
  head($$payload, ($$payload2) => {
    $$payload2.out += `<style>
        @media screen {
            body {
                background: white;
                margin: 0;
                padding: 0;
            }
        }
        @media print {
            @page {
                margin: 1.5cm;
                size: A4;
            }
            body {
                margin: 0;
                padding: 0;
                color: black;
                background: white;
                font-size: 11pt;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .no-print {
                display: none !important;
            }
            /* Ensure backgrounds and colors are printed */
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            /* Enhance borders for better print visibility */
            .border {
                border-width: 1.5px !important;
            }
            .border-b {
                border-bottom-width: 1.5px !important;
            }
            /* Enhance text contrast for print */
            .text-gray-500 {
                color: #4a5568 !important;
            }
            .text-gray-600 {
                color: #2d3748 !important;
            }
        }
        /* Hide header and footer */
        nav, footer, header {
            display: none !important;
        }
    </style>`;
  });
  $$payload.out += `<div class="min-h-screen bg-white">`;
  {
    $$payload.out += "<!--[-->";
    Loading($$payload, { message: "Loading run details..." });
  }
  $$payload.out += `<!--]--></div>`;
  pop();
}
export {
  _page as default
};
