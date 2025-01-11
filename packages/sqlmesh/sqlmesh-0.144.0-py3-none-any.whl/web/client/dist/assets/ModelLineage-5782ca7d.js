import{r as o,R as a,j as e,c as D,B as Q,aA as ie,l as ee,m as G,g as ce,v as I,b as _,i as V,V as de,Y as me,aB as ue,t as he,L as te,S as se,D as X,H as pe}from"./index-4a39458b.js";import{d as fe,e as ne,s as ae,f as O,P as oe,h as P,b as F,i as ge,j as W,R as we,k as xe,l as ve,m as be,n as Y,o as Z,p as J,q as Ne,r as ye,t as je,v as Ee}from"./context-a9c80ac3.js";import{W as Ce}from"./editor-1d351a08.js";import{X as Me,L as ze}from"./ListboxShow-0137dbde.js";import{S as Se}from"./SearchList-0ba5ce2e.js";import{z as ke}from"./Input-409169a4.js";import{w as T}from"./transition-a8e1d9f0.js";import"./_commonjs-dynamic-modules-302442b1.js";import"./file-314b3444.js";import"./project-89a86d21.js";import"./help-68063aae.js";import"./SourceList-34d2dbe6.js";import"./index-8e84c8dc.js";function Le({title:t,titleId:s,...n},c){return o.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",fill:"currentColor","aria-hidden":"true",ref:c,"aria-labelledby":s},n),t?o.createElement("title",{id:s},t):null,o.createElement("path",{fillRule:"evenodd",d:"M10.5 3.75a6.75 6.75 0 100 13.5 6.75 6.75 0 000-13.5zM2.25 10.5a8.25 8.25 0 1114.59 5.28l4.69 4.69a.75.75 0 11-1.06 1.06l-4.69-4.69A8.25 8.25 0 012.25 10.5z",clipRule:"evenodd"}))}const Ae=o.forwardRef(Le),Ie=Ae;function Be(){return a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 32 32"},a.createElement("path",{d:"M32 18.133H18.133V32h-4.266V18.133H0v-4.266h13.867V0h4.266v13.867H32z"}))}function He(){return a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 32 5"},a.createElement("path",{d:"M0 0h32v4.2H0z"}))}function De(){return a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 32 30"},a.createElement("path",{d:"M3.692 4.63c0-.53.4-.938.939-.938h5.215V0H4.708C2.13 0 0 2.054 0 4.63v5.216h3.692V4.631zM27.354 0h-5.2v3.692h5.17c.53 0 .984.4.984.939v5.215H32V4.631A4.624 4.624 0 0027.354 0zm.954 24.83c0 .532-.4.94-.939.94h-5.215v3.768h5.215c2.577 0 4.631-2.13 4.631-4.707v-5.139h-3.692v5.139zm-23.677.94c-.531 0-.939-.4-.939-.94v-5.138H0v5.139c0 2.577 2.13 4.707 4.708 4.707h5.138V25.77H4.631z"}))}function Re(){return a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 25 32"},a.createElement("path",{d:"M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0 8 0 4.571 3.429 4.571 7.619v3.048H3.048A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047zm4.724-13.866H7.467V7.619c0-2.59 2.133-4.724 4.723-4.724 2.591 0 4.724 2.133 4.724 4.724v3.048z"}))}function _e(){return a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 25 32"},a.createElement("path",{d:"M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0c-4.114 1.828-1.37 2.133.305 2.438 1.676.305 4.42 2.59 4.42 5.181v3.048H3.047A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047z"}))}const R=({children:t,className:s,...n})=>a.createElement("button",{type:"button",className:P(["react-flow__controls-button",s]),...n},t);R.displayName="ControlButton";const Fe=t=>({isInteractive:t.nodesDraggable||t.nodesConnectable||t.elementsSelectable,minZoomReached:t.transform[2]<=t.minZoom,maxZoomReached:t.transform[2]>=t.maxZoom}),le=({style:t,showZoom:s=!0,showFitView:n=!0,showInteractive:c=!0,fitViewOptions:u,onZoomIn:l,onZoomOut:r,onFitView:h,onInteractiveChange:p,className:f,children:i,position:N="bottom-left"})=>{const g=fe(),[M,E]=o.useState(!1),{isInteractive:w,minZoomReached:x,maxZoomReached:d}=ne(Fe,ae),{zoomIn:v,zoomOut:j,fitView:m}=O();if(o.useEffect(()=>{E(!0)},[]),!M)return null;const k=()=>{v(),l==null||l()},C=()=>{j(),r==null||r()},S=()=>{m(u),h==null||h()},b=()=>{g.setState({nodesDraggable:!w,nodesConnectable:!w,elementsSelectable:!w}),p==null||p(!w)};return a.createElement(oe,{className:P(["react-flow__controls",f]),position:N,style:t,"data-testid":"rf__controls"},s&&a.createElement(a.Fragment,null,a.createElement(R,{onClick:k,className:"react-flow__controls-zoomin",title:"zoom in","aria-label":"zoom in",disabled:d},a.createElement(Be,null)),a.createElement(R,{onClick:C,className:"react-flow__controls-zoomout",title:"zoom out","aria-label":"zoom out",disabled:x},a.createElement(He,null))),n&&a.createElement(R,{className:"react-flow__controls-fitview",onClick:S,title:"fit view","aria-label":"fit view"},a.createElement(De,null)),c&&a.createElement(R,{className:"react-flow__controls-interactive",onClick:b,title:"toggle interactivity","aria-label":"toggle interactivity"},w?a.createElement(_e,null):a.createElement(Re,null)),i)};le.displayName="Controls";var Ve=o.memo(le),z;(function(t){t.Lines="lines",t.Dots="dots",t.Cross="cross"})(z||(z={}));function $e({color:t,dimensions:s,lineWidth:n}){return a.createElement("path",{stroke:t,strokeWidth:n,d:`M${s[0]/2} 0 V${s[1]} M0 ${s[1]/2} H${s[0]}`})}function Ue({color:t,radius:s}){return a.createElement("circle",{cx:s,cy:s,r:s,fill:t})}const We={[z.Dots]:"#91919a",[z.Lines]:"#eee",[z.Cross]:"#e2e2e2"},Te={[z.Dots]:1,[z.Lines]:1,[z.Cross]:6},Ge=t=>({transform:t.transform,patternId:`pattern-${t.rfId}`});function re({id:t,variant:s=z.Dots,gap:n=20,size:c,lineWidth:u=1,offset:l=2,color:r,style:h,className:p}){const f=o.useRef(null),{transform:i,patternId:N}=ne(Ge,ae),g=r||We[s],M=c||Te[s],E=s===z.Dots,w=s===z.Cross,x=Array.isArray(n)?n:[n,n],d=[x[0]*i[2]||1,x[1]*i[2]||1],v=M*i[2],j=w?[v,v]:d,m=E?[v/l,v/l]:[j[0]/l,j[1]/l];return a.createElement("svg",{className:P(["react-flow__background",p]),style:{...h,position:"absolute",width:"100%",height:"100%",top:0,left:0},ref:f,"data-testid":"rf__background"},a.createElement("pattern",{id:N+t,x:i[0]%d[0],y:i[1]%d[1],width:d[0],height:d[1],patternUnits:"userSpaceOnUse",patternTransform:`translate(-${m[0]},-${m[1]})`},E?a.createElement(Ue,{color:g,radius:v/l}):a.createElement($e,{dimensions:j,color:g,lineWidth:u})),a.createElement("rect",{x:"0",y:"0",width:"100%",height:"100%",fill:`url(#${N+t})`}))}re.displayName="Background";var Oe=o.memo(re);function Pe({handleSelect:t}){const{models:s,lineage:n,mainNode:c,connectedNodes:u}=F(),[l,r]=o.useState(!1),[h,p]=o.useState([]),[f,i]=o.useState(!1);o.useEffect(()=>{p([])},[c,s,n]);function N(){r(!0)}function g(){r(!1)}function M(E){E.length<1||ce(h)||I(c)||I(n)||(i(!0),setTimeout(()=>{const w=Array.from(ge(n,c));p(Object.keys(n).map(x=>{var d;return{name:x,displayName:((d=s.get(x))==null?void 0:d.displayName)??decodeURI(x),description:`${w.includes(x)?"Upstream":"Downstream"} | ${u.has(x)?"Directly":"Indirectly"} Connected`}})),i(!1)},300))}return e.jsxs("div",{className:D("w-full",l?"block absolute top-0 left-0 right-0 z-10 pr-10 bg-light dark:bg-dark @[40rem]:items-end @[40rem]:justify-end @[40rem]:flex @[40rem]:static @[40rem]:pr-0":"items-end justify-end flex"),children:[e.jsx(Q,{shape:ie.Circle,className:D("flex @[40rem]:hidden !py-1 border-transparent",l?"hidden":"flex"),variant:ee.Alternative,size:G.sm,"aria-label":"Show search",onClick:N,children:e.jsx(Ie,{className:"w-3 h-3 text-primary-500"})}),e.jsx(Se,{list:h,placeholder:"Find",searchBy:"displayName",displayBy:"displayName",direction:"top",descriptionBy:"description",showIndex:!1,size:G.sm,onSelect:t,isLoading:f,className:D("w-full @sm:min-w-[12rem] @[40rem]:flex",l?"flex max-w-none":"hidden max-w-[20rem]"),isFullWidth:!0,onInput:M}),e.jsx("button",{className:D("flex @[40rem]:hidden bg-none border-none px-2 py-1 absolute right-0 top-0",l?"flex":"hidden"),"aria-label":"Hide search",onClick:g,children:e.jsx(Me,{className:"w-6 h-6 text-primary-500"})})]})}function K({nodes:t=[]}){const{setCenter:s}=O(),{activeNodes:n,models:c,mainNode:u,nodesMap:l,selectedNodes:r,setSelectedNodes:h,withImpacted:p,connectedNodes:f,lineageCache:i,setActiveEdges:N,setConnections:g,setLineage:M,setLineageCache:E}=F(),w=I(u)?void 0:c.get(u),x=n.size>0?n.size:f.size,d=r.size,v=f.size-1,j=t.filter(b=>b.hidden).length,m=t.filter(b=>_(b.hidden)&&(b.data.type===W.external||b.data.type===W.seed)).length,k=t.filter(b=>_(b.hidden)&&b.data.type===W.cte).length,C=x>0&&x!==v+1;function S(){if(I(u))return;const b=l[u];I(b)||setTimeout(()=>{s(b.position.x,b.position.y,{zoom:.5,duration:0})},200)}return e.jsxs(e.Fragment,{children:[V(w)&&e.jsx("a",{className:"mr-2 w-full whitespace-nowrap text-ellipsis overflow-hidden @lg:block font-bold text-neutral-600 dark:text-neutral-400 cursor-pointer hover:underline",onClick:S,children:de(w.displayName,50,25)}),e.jsxs("span",{className:"bg-neutral-5 px-2 py-0.5 flex rounded-full mr-2",children:[e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"All:"})," ",t.length]}),j>0&&e.jsxs("span",{className:"whitespace-nowrap block mr-2",children:[e.jsx("b",{children:"Hidden:"})," ",j]}),d>0&&e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"Selected:"})," ",d]}),C&&e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"Active:"})," ",x]}),(C||d>0||V(i))&&e.jsx(Q,{size:G.xs,variant:ee.Neutral,format:me.Ghost,className:"!m-0 px-1",onClick:()=>{N(new Map),g(new Map),h(new Set),V(i)&&(M(i),E(void 0))},children:"Reset"})]}),m>0&&e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"Sources"}),": ",m]}),_(C)&&p&&d===0&&v>0&&e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"Upstream/Downstream:"})," ",v]}),k>0&&e.jsxs("span",{className:"mr-2 whitespace-nowrap block",children:[e.jsx("b",{children:"CTEs:"})," ",k]})]})}const qe=30;function ct({model:t,highlightedNodes:s}){const{setActiveNodes:n,setActiveEdges:c,setConnections:u,setLineage:l,handleError:r,setSelectedNodes:h,setMainNode:p,setWithColumns:f,setHighlightedNodes:i,setNodeConnections:N,setLineageCache:g,setUnknownModels:M,models:E,unknownModels:w}=F(),{refetch:x,isFetching:d,cancel:v}=ue(t.name),{isFetching:j}=he(),[m,k]=o.useState(!1),[C,S]=o.useState(void 0);o.useEffect(()=>{const y=Ce();return y.addEventListener("message",b),x().then(({data:L})=>{S(L),!I(L)&&(k(!0),y.postMessage({topic:"lineage",payload:{currentLineage:{},newLineage:L,mainNode:t.fqn}}))}).catch(L=>{r==null||r(L)}).finally(()=>{n(new Set),c(new Map),u(new Map),h(new Set),g(void 0),p(t.fqn)}),()=>{v==null||v(),y.removeEventListener("message",b),y.terminate(),l({}),N({}),p(void 0),i({})}},[t.name,t.hash]),o.useEffect(()=>{Object.keys(C??{}).forEach(y=>{y=encodeURI(y),_(E.has(y))&&_(w.has(y))&&w.add(y)}),M(new Set(w))},[C,E]),o.useEffect(()=>{i(s??{})},[s]);function b(y){var L;y.data.topic==="lineage"&&(k(!1),N(y.data.payload.nodesConnections),l(y.data.payload.lineage),Object.values(((L=y.data.payload)==null?void 0:L.lineage)??{}).length>qe&&f(!1)),y.data.topic==="error"&&(r==null||r(y.data.error),k(!1))}const B=d||j||m;return e.jsxs("div",{className:"relative h-full w-full overflow-hidden",children:[B&&e.jsxs("div",{className:"absolute top-0 left-0 z-10 flex justify-center items-center w-full h-full",children:[e.jsx("span",{className:"absolute w-full h-full z-10 bg-transparent-20 backdrop-blur-lg"}),e.jsxs(te,{className:"inline-block z-10",children:[e.jsx(se,{className:"w-3 h-3 border border-neutral-10 mr-4"}),e.jsx("h3",{className:"text-md whitespace-nowrap",children:B?"Loading Model's Lineage...":"Merging Model's..."})]})]}),e.jsx(we,{children:e.jsx(Xe,{})})]})}function Xe(){const{withColumns:t,lineage:s,mainNode:n,selectedEdges:c,selectedNodes:u,withConnected:l,withImpacted:r,withSecondary:h,hasBackground:p,activeEdges:f,connectedNodes:i,connections:N,nodesMap:g,showControls:M,handleError:E,setActiveNodes:w}=F(),{setCenter:x}=O(),[d,v]=o.useState(!1),j=o.useMemo(()=>({model:xe}),[]),m=o.useMemo(()=>ve(s),[s]),k=o.useMemo(()=>be(s),[s]),[C,S]=o.useState([]),[b,B]=o.useState([]);o.useEffect(()=>{if(X(m)||I(n))return;v(!0);const A=Y(m,f,c,g),$=Z(Object.values(g),A,n,i,u,N,l,r,h),U=J(m,N,f,A,c,u,i,l,r,h),q=Ne({nodesMap:g,nodes:$,edges:U});return q.create().then(H=>{B(H.edges),S(H.nodes)}).catch(H=>{E==null||E(H),B([]),S([])}).finally(()=>{const H=I(n)?void 0:g[n];V(H)&&x(H.position.x,H.position.y,{zoom:.5,duration:0}),setTimeout(()=>{v(!1)},100)}),()=>{q.terminate(),B([]),S([])}},[f,g,k]),o.useEffect(()=>{if(I(n)||X(C))return;const A=Y(m,f,c,g),$=Z(C,A,n,i,u,N,l,r,h),U=J(m,N,f,A,c,u,i,l,r,h);B(U),S($),w(A)},[N,g,m,f,u,c,i,l,r,h,t,n]);function y(A){S(je(A,C))}function L(A){B(Ee(A,b))}return e.jsxs(e.Fragment,{children:[d&&e.jsxs("div",{className:"absolute top-0 left-0 z-10 flex justify-center items-center w-full h-full",children:[e.jsx("span",{className:"absolute w-full h-full z-10 bg-transparent-20 backdrop-blur-lg"}),e.jsxs(te,{className:"inline-block z-10",children:[e.jsx(se,{className:"w-3 h-3 border border-neutral-10 mr-4"}),e.jsx("h3",{className:"text-md whitespace-nowrap",children:"Building Lineage..."})]})]}),e.jsxs(ye,{nodes:C,edges:b,nodeTypes:j,onNodesChange:y,onEdgesChange:L,nodeOrigin:[.5,.5],minZoom:.05,maxZoom:1.5,snapGrid:[16,16],snapToGrid:!0,children:[M&&e.jsxs(oe,{position:"top-right",className:"bg-theme !m-0 w-full !z-10",children:[e.jsx(Ye,{nodes:C}),e.jsx(pe,{})]}),e.jsx(Ve,{className:"bg-light p-1 rounded-md !border-none !shadow-lg"}),e.jsx(Oe,{variant:z.Cross,gap:32,size:4,className:D(p?"opacity-100 stroke-neutral-200 dark:stroke-neutral-800":"opacity-0")})]})]})}function Ye({nodes:t=[]}){const{withColumns:s,mainNode:n,selectedNodes:c,withConnected:u,withImpacted:l,withSecondary:r,hasBackground:h,activeNodes:p,highlightedNodes:f,setSelectedNodes:i,setWithColumns:N,setWithConnected:g,setWithImpacted:M,setWithSecondary:E,setHasBackground:w}=F(),x=o.useRef(null),d=o.useMemo(()=>Object.values(f??{}).flat(),[f]);function v(j){d.includes(j.name)||n===j.name||i(m=>(m.has(j.name)?m.delete(j.name):m.add(j.name),new Set(m)))}return e.jsxs("div",{className:"px-2 flex items-center text-xs text-neutral-400 @container",children:[e.jsxs("div",{className:"contents",children:[e.jsxs(T,{className:"flex @lg:hidden bg-none border-none","aria-label":"Show lineage node details",children:[e.jsxs(T.Button,{ref:x,className:"flex items-center relative w-full cursor-pointer bg-primary-10 text-xs rounded-full text-primary-500 py-1 px-3 text-center focus:outline-none focus-visible:border-accent-500 focus-visible:ring-2 focus-visible:ring-light focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-brand-300 border-1 border-transparent",children:["Details",e.jsx(ke,{className:"ml-2 h-4 w-4","aria-hidden":"true"})]}),e.jsx(T.Panel,{className:"absolute left-2 right-2 flex-col z-50 mt-8 transform flex px-4 py-3 bg-theme-lighter shadow-xl focus:ring-2 ring-opacity-5 rounded-lg",children:e.jsx(K,{nodes:t})})]}),e.jsx("div",{className:"hidden @lg:contents w-full",children:e.jsx(K,{nodes:t})})]}),e.jsxs("div",{className:"flex w-full justify-end items-center",children:[e.jsx(Pe,{handleSelect:v}),e.jsx(ze,{options:{Background:w,Columns:p.size>0&&c.size===0?void 0:N,Connected:p.size>0?void 0:g,"Upstream/Downstream":p.size>0?void 0:M,All:p.size>0?void 0:E},value:[s&&"Columns",h&&"Background",u&&"Connected",l&&"Upstream/Downstream",r&&"All"].filter(Boolean)})]})]})}export{ct as default};
