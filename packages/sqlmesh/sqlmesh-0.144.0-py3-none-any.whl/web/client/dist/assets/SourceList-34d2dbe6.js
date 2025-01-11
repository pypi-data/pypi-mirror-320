import{r as f,i as V,I as q,j as s,c as v,m as y,B as A,l as G,D as H,v as J}from"./index-4a39458b.js";import{I as L}from"./Input-409169a4.js";import{u as K}from"./index-8e84c8dc.js";function W({items:c=[],keyId:d="id",keyName:N="",keyDescription:x="",to:T="",disabled:S=!1,withCounter:$=!0,withFilter:B=!0,types:a,className:F,isActive:m,listItem:h}){var R;const O=f.useRef(null),[r,C]=f.useState(""),j=f.useRef(null),[o,u]=f.useMemo(()=>{let t=-1;const e=[];return c.forEach((l,p)=>{const w=n(l[d]),g=n(l[x]),Y=n(l[N]),k=n(a==null?void 0:a[w]);(Y.includes(r)||g.includes(r)||k.includes(r))&&e.push(l),V(m)&&m(l[d])&&(t=p)}),[t,e]},[c,r,m]),i=K({count:u.length,getScrollElement:()=>j.current,estimateSize:()=>32+(x.length>0?16:0)}),b=({itemIndex:t,isSmoothScroll:e=!0})=>{i.scrollToIndex(t,{align:"center",behavior:e?"smooth":"auto"})},E=({itemIndex:t,range:e})=>V(e)&&(e.startIndex>t||(e==null?void 0:e.endIndex)<t),M=q(r)&&o>-1&&E({range:i.range,itemIndex:o});f.useEffect(()=>{o>-1&&E({range:i.range,itemIndex:o})&&b({itemIndex:o,isSmoothScroll:!1})},[o]);const z=i.getVirtualItems(),I=i.getTotalSize();return s.jsxs("div",{ref:O,className:v("flex flex-col w-full h-full text-sm text-neutral-600 dark:text-neutral-300",F),style:{contain:"strict"},children:[B&&s.jsxs("div",{className:"p-1 w-full flex justify-between",children:[s.jsx(L,{className:"w-full !m-0",size:y.sm,children:({className:t})=>s.jsx(L.Textfield,{className:v(t,"w-full"),value:r,placeholder:"Filter items",type:"search",onInput:e=>{C(e.target.value)}})}),$&&s.jsx("div",{className:"ml-1 px-3 bg-primary-10 text-primary-500 rounded-full text-xs flex items-center",children:u.length})]}),s.jsxs("div",{className:"w-full h-full relative p-1",children:[M&&s.jsx(A,{className:"absolute left-[50%] translate-x-[-50%] -top-2 z-10 text-ellipsis !block overflow-hidden no-wrap max-w-[90%] !border-neutral-20 shadow-md !bg-theme !hover:bg-theme text-neutral-500 dark:text-neutral-300 !focus:ring-2 !focus:ring-theme-500 !focus:ring-offset-2 !focus:ring-offset-theme-50 !focus:ring-opacity-50 !focus:outline-none !focus:ring-offset-transparent !focus:ring-offset-0 !focus:ring",onClick:()=>b({itemIndex:o}),size:y.sm,variant:G.Secondary,children:"Scroll to selected"}),s.jsx("div",{ref:j,className:"w-full h-full relative overflow-hidden overflow-y-auto hover:scrollbar scrollbar--horizontal scrollbar--vertical",style:{contain:"strict"},children:s.jsx("div",{className:"relative w-full",style:{height:I>0?`${I}px`:"100%"},children:s.jsxs("ul",{className:"w-full absolute top-0 left-0",style:{transform:`translateY(${((R=z[0])==null?void 0:R.start)??0}px)`},children:[H(u)&&s.jsx("li",{className:"px-2 py-0.5 text-center whitespace-nowrap overflow-ellipsis overflow-hidden",children:r.length>0?"No Results Found":"Empty List"},"not-found"),z.map(t=>{const e=u[t.index],l=n(e[d]),p=n(e[x]),w=n(e[N]),g=n(a==null?void 0:a[l]);return s.jsx("li",{"data-index":t.index,ref:i.measureElement,className:v("font-normal w-full",S&&"cursor-not-allowed"),tabIndex:l===r?-1:0,children:h==null?void 0:h({id:l,to:`${T}/${l}`,name:w,description:p,text:g,disabled:S,item:u[t.index]})},t.key)})]})})})]})]})}function n(c){return J(c)?"":String(c)}export{W as S};
