import { p as parser$1, f as flowDb } from "./flowDb-d35e309a-svJ8JnmG.js";
import { f as flowRendererV2, g as flowStyles } from "./styles-7383a064-D3KVQB4O.js";
import { t as setConfig } from "./index-BiGH9Fvs.js";
import "./graph-Dld2jo6Z.js";
import "./layout-SnILG7IU.js";
import "./index-8fae9850-D2TmJB1s.js";
import "./clone-DRduvL4Y.js";
import "./edges-d417c7a0-C65QYQQ5.js";
import "./createText-423428c9-7nnlwn9I.js";
import "./line-BqFhxa5n.js";
import "./array-DgktLKBx.js";
import "./path-Cp2qmpkd.js";
import "./channel-Cpv5hWkG.js";
const diagram = {
  parser: parser$1,
  db: flowDb,
  renderer: flowRendererV2,
  styles: flowStyles,
  init: (cnf) => {
    if (!cnf.flowchart) {
      cnf.flowchart = {};
    }
    cnf.flowchart.arrowMarkerAbsolute = cnf.arrowMarkerAbsolute;
    setConfig({ flowchart: { arrowMarkerAbsolute: cnf.arrowMarkerAbsolute } });
    flowRendererV2.setConf(cnf.flowchart);
    flowDb.clear();
    flowDb.setGen("gen-2");
  }
};
export {
  diagram
};
//# sourceMappingURL=flowDiagram-v2-49332944-CXps_8aB.js.map
