import{s as u,Q as c,a as m,v as a,j as s,e as f}from"./index-4a39458b.js";import{L as g}from"./context-a9c80ac3.js";import x from"./ModelLineage-5782ca7d.js";import"./_commonjs-dynamic-modules-302442b1.js";import"./Input-409169a4.js";import"./editor-1d351a08.js";import"./file-314b3444.js";import"./project-89a86d21.js";import"./help-68063aae.js";import"./SourceList-34d2dbe6.js";import"./index-8e84c8dc.js";import"./transition-a8e1d9f0.js";import"./ListboxShow-0137dbde.js";import"./SearchList-0ba5ce2e.js";function Q(){const l=u(),{modelName:t}=c(),i=m(e=>e.models),o=m(e=>e.lastSelectedModel),r=a(t)||t===(o==null?void 0:o.name)?o:i.get(encodeURI(t));function d(e){const n=i.get(e);a(n)||l(f.LineageModels+"/"+n.name)}function p(e){console.log(e==null?void 0:e.message)}return s.jsx("div",{className:"flex overflow-hidden w-full h-full",children:s.jsx(g,{showColumns:!0,handleClickModel:d,handleError:p,children:s.jsx(x,{model:r})})})}export{Q as default};
