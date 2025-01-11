import{r as y,R as J,a as O,j as e,l as I,s as Me,b as T,B as le,v as E,m as P,c as g,M as ke,f as V,I as ze,J as re,i as M,K as Q,g as H,T as Fe,H as oe,P as he,C as Le,q as Ue,A as L,L as $e,d as Ve,k as Ge,o as He,p as qe,Q as Ke,U as Ye,e as Ze}from"./index-4a39458b.js";import{a as Je,b as Qe,H as We,M as Xe,u as Y,S as es,A as ss,c as ve,d as R,E as A,P as U,e as as}from"./SelectEnvironment-0fe1604d.js";import{u as j,a as Z,E as z}from"./plan-d8735386.js";import{B as S}from"./Banner-f18b661d.js";import{v as $,M as ge,P as ye}from"./PlusCircleIcon-858f124c.js";import{D as ns,I as ts,y as ls,o as ie,z as is,p as rs,c as os,b as cs,R as ds,X as Re,v as ms,r as Pe,x as ee}from"./transition-a8e1d9f0.js";import{I as q}from"./Input-409169a4.js";import{T as us,p as ps}from"./ListboxShow-0137dbde.js";import{p as fs}from"./pluralize-451f0df4.js";import{u as Ee}from"./project-89a86d21.js";import{E as xe}from"./context-a9c80ac3.js";import"./ModelLineage-5782ca7d.js";import"./editor-1d351a08.js";import"./file-314b3444.js";import"./SearchList-0ba5ce2e.js";import"./help-68063aae.js";import"./ChevronDownIcon-4178a652.js";import"./_commonjs-dynamic-modules-302442b1.js";import"./SourceList-34d2dbe6.js";import"./index-8e84c8dc.js";function hs({title:s,titleId:a,...t},r){return y.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor","aria-hidden":"true",ref:r,"aria-labelledby":a},t),s?y.createElement("title",{id:a},s):null,y.createElement("path",{fillRule:"evenodd",d:"M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z",clipRule:"evenodd"}))}const xs=y.forwardRef(hs),W=xs;let we=y.createContext(null);we.displayName="GroupContext";let js=y.Fragment;function vs(s){var a;let[t,r]=y.useState(null),[l,i]=We(),[c,m]=Xe(),o=y.useMemo(()=>({switch:t,setSwitch:r,labelledby:l,describedby:c}),[t,r,l,c]),d={},u=s;return J.createElement(m,{name:"Switch.Description"},J.createElement(i,{name:"Switch.Label",props:{htmlFor:(a=o.switch)==null?void 0:a.id,onClick(n){t&&(n.currentTarget.tagName==="LABEL"&&n.preventDefault(),t.click(),t.focus({preventScroll:!0}))}}},J.createElement(we.Provider,{value:o},Re({ourProps:d,theirProps:u,defaultTag:js,name:"Switch.Group"}))))}let gs="button";function ys(s,a){let t=ts(),{id:r=`headlessui-switch-${t}`,checked:l,defaultChecked:i=!1,onChange:c,name:m,value:o,form:d,...u}=s,n=y.useContext(we),x=y.useRef(null),p=ls(x,a,n===null?null:n.setSwitch),[f,h]=us(l,c,i),C=ie(()=>h==null?void 0:h(!f)),B=ie(_=>{if(ms(_.currentTarget))return _.preventDefault();_.preventDefault(),C()}),F=ie(_=>{_.key===Pe.Space?(_.preventDefault(),C()):_.key===Pe.Enter&&ps(_.currentTarget)}),b=ie(_=>_.preventDefault()),N=y.useMemo(()=>({checked:f}),[f]),w={id:r,ref:p,role:"switch",type:is(s,x),tabIndex:0,"aria-checked":f,"aria-labelledby":n==null?void 0:n.labelledby,"aria-describedby":n==null?void 0:n.describedby,onClick:B,onKeyUp:F,onKeyPress:b},D=rs();return y.useEffect(()=>{var _;let te=(_=x.current)==null?void 0:_.closest("form");te&&i!==void 0&&D.addEventListener(te,"reset",()=>{h(i)})},[x,h]),J.createElement(J.Fragment,null,m!=null&&f&&J.createElement(os,{features:cs.Hidden,...ds({as:"input",type:"checkbox",hidden:!0,readOnly:!0,form:d,checked:f,name:m,value:o})}),Re({ourProps:w,theirProps:u,slot:N,defaultTag:gs,name:"Switch"}))}let ws=ns(ys),bs=vs,fe=Object.assign(ws,{Group:bs,Label:Je,Description:Qe});function Ns(){const s=O(a=>a.environment);return e.jsx("div",{className:"flex flex-col px-4 py-2 w-full",children:e.jsx(S,{variant:I.Warning,children:e.jsx($,{defaultOpen:!1,children:({open:a})=>e.jsxs(e.Fragment,{children:[e.jsxs($.Button,{className:"w-full flex items-center justify-between",children:[e.jsx(S.Label,{className:"w-full",children:s.isInitialProd?"Initializing Prod Environment":"Prod Environment"}),s.isInitialProd&&e.jsx(e.Fragment,{children:a?e.jsx(ge,{className:"w-5 text-warning-500"}):e.jsx(ye,{className:"w-5 text-warning-500"})})]}),s.isInitialProd&&e.jsx($.Panel,{className:"px-2 text-sm mt-2",children:e.jsx(S.Description,{children:"Prod will be completely backfilled in order to ensure there are no data gaps. After this is applied, it is recommended to validate further changes in a dev environment before deploying to production."})})]})})})})}function ks(s=0){return y.useCallback(a=>{setTimeout(()=>{a==null||a.focus()},s)},[s])}function Ps({run:s,apply:a,cancel:t,reset:r}){const l=Me(),{change_categorization:i}=Y(),c=O(k=>k.modules),m=O(k=>k.environment),o=O(k=>k.environments),d=O(k=>k.addConfirmation),u=O(k=>k.setShowConfirmation),n=j(k=>k.planAction),x=j(k=>k.planOverview),p=j(k=>k.planApply),f=j(k=>k.planCancel),h=ks();function C(k){k.stopPropagation(),r()}function B(k){k.stopPropagation(),t()}function F(k){k.stopPropagation(),l(-1)}function b(k){k.stopPropagation();const Oe=m.isProd&&T(m.isInitial),Ne=Array.from(i.values()).some(Ie=>E(Ie.category));Oe?d({headline:"Applying Plan Directly On Prod Environment!",tagline:"Safer choice will be to select or add new environment first.",description:"Are you sure you want to apply your changes directly on prod?",yesText:`Yes, Run ${m.name}`,noText:"No, Cancel",action:a,details:Ne?["ATTENTION!","[Breaking Change] category will be applied to all uncategorized changes"]:void 0,children:e.jsxs("div",{className:"mt-5 pt-4",children:[e.jsx("h4",{className:"mb-2",children:`${o.size>1?"Select or ":""}Add Environment`}),e.jsxs("div",{className:"flex items-center relative",children:[o.size>1&&e.jsx(es,{className:"mr-2",showAddEnvironment:!1,onSelect:()=>{u(!1)},size:P.md}),e.jsx(ss,{className:"w-full",size:P.md,onAdd:()=>{u(!1)}})]})]})}):Ne?d({headline:"Some changes are missing categorization!",description:"Are you sure you want to proceed?",details:["[Breaking Change] category will be applied to all uncategorized changes"],yesText:"Yes, Apply",noText:"No, Cancel",action:a}):a()}function N(k){k.stopPropagation(),s()}const w=x.isFailed||p.isFailed||f.isSuccessful,D=T(n.isCancelling)&&T(n.isDone)&&(n.isProcessing?T(f.isSuccessful):!0)&&T(w),_=n.isApplying||f.isCancelling||p.isRunning&&x.isFinished,te=w||T(n.isProcessing)&&T(n.isRun)&&T(n.isDone),_e=c.showHistoryNavigation;return e.jsx(e.Fragment,{children:e.jsxs("div",{className:"flex justify-between pt-2 pl-4 pr-2 pb-2",children:[e.jsx("div",{className:"flex w-full items-center",children:e.jsx(ee,{appear:!0,show:D,enter:"transition ease duration-300 transform",enterFrom:"opacity-0 scale-95",enterTo:"opacity-100 scale-100",leave:"transition ease duration-300 transform",leaveFrom:"opacity-100 scale-100",leaveTo:"opacity-0 scale-95",className:"trasition-all duration-300 ease-in-out",children:D&&e.jsx(le,{disabled:n.isProcessing||f.isSuccessful||n.isDone,onClick:n.isRun?N:f.isSuccessful?void 0:b,ref:h,variant:f.isSuccessful?I.Danger:I.Primary,autoFocus:!0,className:"trasition-all duration-300 ease-in-out",children:e.jsx("span",{children:Z.getActionDisplayName(n,f.isSuccessful?[]:[z.RunningTask,z.Running,z.Run,z.Applying,z.ApplyBackfill,z.ApplyVirtual,z.ApplyChangesAndBackfill,z.ApplyMetadata],f.isSuccessful?"Canceled":"Done")})})})}),e.jsxs("div",{className:"flex items-center",children:[_&&e.jsx(le,{onClick:B,variant:I.Danger,disabled:n.isCancelling||n.isProcessing&&f.isSuccessful,children:Z.getActionDisplayName(n,n.isProcessing&&T(f.isSuccessful)?[z.Cancelling]:[],f.isSuccessful?"Finishing Cancellation...":"Cancel")}),te&&e.jsx(le,{onClick:C,variant:I.Info,disabled:n.isCancelling||n.isProcessing&&f.isSuccessful,children:"Start Over"}),_e&&e.jsx(le,{onClick:F,variant:I.Info,children:"Go Back"})]})]})})}function Ts({label:s,enabled:a,setEnabled:t,a11yTitle:r,size:l=P.md,disabled:i=!1,className:c}){return e.jsxs(fe.Group,{as:"div",className:"m-1",children:[e.jsxs(fe,{checked:i?!1:a,onChange:t,className:g("flex relative border-secondary-30 rounded-full m-0","shrink-0 focus:outline-none ring-secondary-300 ring-opacity-60 ring-offset ring-offset-secondary-100 focus:border-secondary-500 focus-visible:ring-opacity-75","transition duration-200 ease-in-out",a?"bg-secondary-500":"bg-secondary-20",c,i?"opacity-50 cursor-not-allowed":"cursor-pointer",l===P.sm&&"h-[14px] w-6 focus:ring-1 border",l===P.md&&"h-5 w-10 focus:ring-2 border-2",l===P.lg&&"h-7 w-14 focus:ring-4 border-2"),disabled:i,children:[e.jsx("span",{className:"sr-only",children:r}),e.jsx("span",{"aria-hidden":"true",className:g("pointer-events-none inline-block transform rounded-full shadow-md transition duration-200 ease-in-out","bg-light",l===P.sm&&"h-3 w-3",l===P.md&&"h-4 w-4",l===P.lg&&"h-6 w-6",a&&l===P.sm&&"translate-x-[10px]",a&&l===P.md&&"translate-x-5",a&&l===P.lg&&"translate-x-7")})]}),s!=null&&e.jsx(fe.Label,{className:g("text-xs font-light ml-1 text-neutral-600 dark:text-neutral-400"),children:s})]})}function K({label:s,info:a,enabled:t,disabled:r=!1,setEnabled:l,className:i}){return e.jsxs("div",{className:g("flex justify-between",i),children:[e.jsxs("label",{className:"block mb-1 px-3 text-sm font-bold",children:[s,e.jsx("small",{className:"block text-xs text-neutral-500",children:a})]}),e.jsx(Ts,{disabled:r,enabled:t,setEnabled:l,size:P.lg})]})}function Cs({disabled:s=!1,className:a}){const t=ve(),{start:r,end:l,isInitialPlanRun:i}=Y();return e.jsxs("div",{className:g("flex w-full flex-wrap md:flex-nowrap",a),children:[e.jsx(q,{className:"w-full md:w-[50%]",label:"Start Date (UTC)",info:"The start datetime of the interval",disabled:s||i,children:({disabled:c,className:m})=>e.jsx(q.Textfield,{className:g(m,"w-full"),disabled:c,placeholder:"2023-12-13",value:r,onInput:o=>{o.stopPropagation(),t({type:R.DateStart,start:o.target.value})}})}),e.jsx(q,{className:"w-full md:w-[50%]",label:"End Date (UTC)",info:"The end datetime of the interval",disabled:s||i,children:({disabled:c,className:m})=>e.jsx(q.Textfield,{className:g(m,"w-full"),disabled:c,placeholder:"2022-12-13",value:l,onInput:o=>{o.stopPropagation(),t({type:R.DateEnd,end:o.target.value})}})})]})}function As(){const s=ve(),{skip_tests:a,no_gaps:t,skip_backfill:r,forward_only:l,auto_apply:i,no_auto_categorization:c,restate_models:m,isInitialPlanRun:o,create_from:d,include_unmodified:u}=Y(),n=y.useRef(null),x=j(b=>b.planAction),p=j(b=>b.planOverview),f=j(b=>b.planApply),h=O(b=>b.environment),C=O(b=>b.environments),B=ke.getOnlyRemote(Array.from(C));y.useEffect(()=>{s({type:R.PlanOptions,...p.plan_options,skip_tests:!1})},[]);const F=x.isProcessing||x.isDone||f.isFinished||p.isLatest&&T(x.isRun)||p.isVirtualUpdate;return y.useEffect(()=>{var b;E(n.current)||x.isProcessing&&n.current.classList.contains("--is-open")&&((b=n.current)==null||b.click())},[n,x]),e.jsxs("form",{className:"w-full",children:[e.jsx("fieldset",{className:g(F&&"opacity-50 cursor-not-allowed"),children:e.jsx(Cs,{className:g(F&&"pointer-events-none")})}),e.jsx("fieldset",{className:"my-2",children:e.jsx(S,{children:e.jsx($,{defaultOpen:x.isRun,children:({open:b})=>e.jsxs(e.Fragment,{children:[e.jsxs($.Button,{ref:n,className:g("w-full flex items-center",b&&"--is-open"),children:[e.jsxs(S.Label,{className:"mr-2 text-sm w-full",children:[e.jsx("span",{children:"Additional Options"}),F&&e.jsx("span",{className:"ml-1",children:"(Read Only)"})]}),b?e.jsx(ge,{className:"h-5 w-5 text-neutral-400"}):e.jsx(ye,{className:"h-5 w-5 text-neutral-400"})]}),e.jsxs($.Panel,{unmount:!1,className:g("py-4 text-sm text-neutral-500",F&&"opacity-50 cursor-not-allowed"),children:[e.jsx("div",{className:g(F&&"pointer-events-none"),children:e.jsxs("div",{className:"flex flex-wrap md:flex-nowrap",children:[T(h.isProd)&&e.jsx(q,{className:"w-full",label:"Create From Environment",info:"The environment to base the plan on rather than local files",disabled:B.length<2,children:({className:N,disabled:w})=>e.jsx(q.Selector,{className:g(N,"w-full"),list:ke.getOnlyRemote(Array.from(C)).filter(D=>D!==h).map(D=>({value:D.name,text:D.name})),onChange:D=>{s({type:R.PlanOptions,create_from:D})},value:d,disabled:w})}),e.jsx(q,{className:"w-full",label:"Restate Models",info:`Restate data for specified models and models
                    downstream from the one specified. For production
                    environment, all related model versions will have
                    their intervals wiped, but only the current
                    versions will be backfilled. For development
                    environment, only the current model versions will
                    be affected`,children:({className:N})=>e.jsx(q.Textfield,{className:g(N,"w-full"),placeholder:"project.model1, project.model2",disabled:o,value:m??"",onInput:w=>{w.stopPropagation(),s({type:R.PlanOptions,restate_models:w.target.value})}})})]})}),e.jsxs("div",{className:g("flex flex-wrap md:flex-nowrap w-full mt-3",F&&"pointer-events-none"),children:[e.jsxs("div",{className:"w-full md:mr-2",children:[e.jsx("div",{className:"block my-2",children:e.jsx(K,{label:"Skip Tests",info:`Skip tests prior to generating the plan if they
              are defined`,enabled:!!a,setEnabled:N=>{s({type:R.PlanOptions,skip_tests:N})}})}),e.jsx("div",{className:"block my-2",children:e.jsx(K,{label:"No Gaps",info:`Ensure that new snapshots have no data gaps when
              comparing to existing snapshots for matching
              models in the target environment`,enabled:!!t||!!r&&h.isInitialProd||h.isInitialProd,disabled:o||!!r&&h.isInitialProd||h.isInitialProd,setEnabled:N=>{s({type:R.PlanOptions,no_gaps:N})}})}),e.jsx("div",{className:"block my-2",children:e.jsx(K,{label:"Skip Backfill",info:"Skip the backfill step",enabled:!!r,disabled:o||h.isInitialProd,setEnabled:N=>{s({type:R.PlanOptions,skip_backfill:N})}})})]}),e.jsxs("div",{className:"w-full md:ml-2",children:[e.jsxs("div",{className:"block my-2",children:[e.jsx(K,{label:"Include Unmodified",info:"Indicates whether to create views for all models in the target development environment or only for modified ones",enabled:!!u,disabled:o||h.isInitialProd,setEnabled:N=>{s({type:R.PlanOptions,include_unmodified:N})}}),e.jsx(K,{label:"Forward Only",info:"Create a plan for forward-only changes",enabled:!!l,disabled:o||h.isInitialProd,setEnabled:N=>{s({type:R.PlanOptions,forward_only:N})}})]}),e.jsx("div",{className:"block my-2",children:e.jsx(K,{label:"Auto Apply",info:"Automatically apply the plan after it is generated",enabled:!!i,setEnabled:N=>{s({type:R.PlanOptions,auto_apply:N})}})}),e.jsx("div",{className:"block my-2",children:e.jsx(K,{label:"No Auto Categorization",info:"Set category manually",enabled:!!c,disabled:o||h.isInitialProd,setEnabled:N=>{s({type:R.PlanOptions,no_auto_categorization:N})}})})]})]})]})]})},String(x.isRun))})})]})}function Ss(s){const{start:a,end:t,skip_tests:r,no_gaps:l,skip_backfill:i,forward_only:c,include_unmodified:m,no_auto_categorization:o,restate_models:d,auto_apply:u,create_from:n,change_categorization:x}=Y(),p=O(F=>F.environment),f=E(p==null?void 0:p.isDefault)||V(p==null?void 0:p.isDefault),h=y.useMemo(()=>{if(!p.isProd)return{start:a,end:f&&ze(d)?void 0:t}},[p,a,t,f,d]),C=y.useMemo(()=>p.isInitialProd?{include_unmodified:!0,no_gaps:!0,skip_tests:r,auto_apply:u}:{skip_tests:r,no_gaps:l,skip_backfill:i,forward_only:c,create_from:n,no_auto_categorization:o,restate_models:d,include_unmodified:m,auto_apply:u},[p,l,i,c,m,n,o,r,d,u]),B=y.useMemo(()=>Array.from(x.values()).reduce((F,{category:b,change:N})=>(F[N.displayName]=(b==null?void 0:b.value)??re.NUMBER_1,F),{}),[x]);return{planOptions:{...C,...s},planDates:h,categories:B}}function Ds(){const{start:s,end:a,skip_tests:t,no_gaps:r,skip_backfill:l,forward_only:i,include_unmodified:c,no_auto_categorization:m,restate_models:o,create_from:d,change_categorization:u}=Y(),n=O(h=>h.environment),x=E(n==null?void 0:n.isDefault)||V(n==null?void 0:n.isDefault),p=y.useMemo(()=>{if(!x)return{start:s,end:a}},[s,a,x]),f=y.useMemo(()=>Array.from(u.values()).reduce((h,{category:C,change:B})=>(h[B.displayName]=(C==null?void 0:C.value)??re.NUMBER_1,h),{}),[u]);return{planDates:p,planOptions:{no_gaps:r,skip_backfill:l,forward_only:i,include_unmodified:c,create_from:d,no_auto_categorization:m,skip_tests:t,restate_models:o},categories:f}}function X(s,a,t){var c;const r=(s.isFinished&&(a.isLatest||a.isRunning)||t.isFinished||T((c=s.overview)==null?void 0:c.isFailed))&&M(s.overview),l=r?s.overview:a,i=r?s:a;return{meta:i.meta,start:i.start,end:i.end,hasChanges:l.hasChanges,hasBackfills:l.hasBackfills,backfills:i.backfills??[],added:i.added??[],removed:i.removed??[],direct:i.direct??[],indirect:i.indirect??[],metadata:i.metadata??[],plan_options:i.plan_options,stageValidation:i.stageValidation,stageBackfills:i.stageBackfills,stageChanges:i.stageChanges,isFailed:l.isFailed||t.isFailed||s.isFailed}}const Te=3;function se({progress:s=0,delay:a=0,duration:t=0,startFromZero:r=!0,className:l}){return T(r)&&(s=s<Te?Te:s),e.jsx("div",{className:g("w-full h-1 bg-neutral-30 overflow-hidden flex items-center rounded-lg my-1",l),children:e.jsx("div",{className:"transition-[width] h-full bg-success-500 rounded-lg",style:{width:`${s}%`,transitionDelay:`${a}ms`,transitionDuration:`${t}ms`}})})}const v=function({children:a,setRefTasksOverview:t,tasks:r}){const{models:l,taskCompleted:i,taskTotal:c,batchesTotal:m,batchesCompleted:o}=y.useMemo(()=>{const d=Object.values(r),u=d.length;let n=0,x=0,p=0;return d.forEach(f=>{n=f.completed===f.total?n+1:n,x+=f.total,p+=f.completed}),{models:d,taskCompleted:n,taskTotal:u,batchesTotal:x,batchesCompleted:p}},[r]);return e.jsx("div",{className:"text-prose",ref:t,children:a({models:l,completed:i,total:c,totalBatches:m,completedBatches:o})})};function Fs({className:s,headline:a,environment:t,completed:r,total:l,updatedAt:i,updateType:c,completedBatches:m,totalBatches:o}){return e.jsx(be,{className:s,children:e.jsxs(ce,{children:[e.jsxs(de,{children:[e.jsx(me,{children:e.jsx(Be,{headline:a,environment:t})}),e.jsxs(ue,{children:[e.jsx(ae,{completed:r,total:l,unit:"task"}),e.jsx(ne,{}),e.jsx(ae,{completed:m,total:o,unit:"batches"}),e.jsx(ne,{}),e.jsx(pe,{completed:m,total:o})]})]}),e.jsx(se,{progress:Q(m,o)}),M(i)&&e.jsx(Es,{updatedAt:i,updateType:c})]})})}function Rs({models:s,className:a,added:t,removed:r,direct:l,indirect:i,metadata:c,showBatches:m=!0,showProgress:o=!0,showVirtualUpdate:d=!1,queue:u}){return e.jsxs(e.Fragment,{children:[e.jsx(ee,{show:H(u),enter:"transition ease duration-300 transform",enterFrom:"opacity-0 scale-95",enterTo:"opacity-100 scale-100",leave:"transition ease duration-300 transform",leaveFrom:"opacity-100 scale-100",leaveTo:"opacity-0 scale-95",className:"trasition-all duration-300 ease-in-out",children:e.jsxs("div",{className:"px-4 pt-3 pb-2 mt-4 shadow-lg rounded-lg",children:[e.jsx(Fe,{text:"Currently in proccess"}),e.jsx(je,{models:u,children:n=>e.jsxs(ce,{children:[e.jsxs(de,{children:[e.jsxs(me,{children:[H(n.interval)&&e.jsx(Ce,{start:n.interval[0],end:n.interval[1]}),e.jsx(Se,{modelName:n.displayViewName,changeType:De({modelName:n.name,added:t,removed:r,direct:l,indirect:i,metadata:c})})]}),e.jsxs(ue,{children:[m&&e.jsx(ae,{completed:n.completed,total:n.total,unit:"batch"}),e.jsx(ne,{}),o&&e.jsx(e.Fragment,{children:E(n.end)||E(n.start)?e.jsx(pe,{total:n.total,completed:n.completed}):e.jsx(Ae,{start:n.start,end:n.end})}),d&&e.jsx("span",{className:"inline-block whitespace-nowrap font-bold ml-2",children:"Updated"})]})]}),o?e.jsx(se,{startFromZero:!1,progress:Q(n.completed,n.total)}):e.jsx(oe,{className:"my-1 border-neutral-200 opacity-50"})]})})]})}),e.jsx(be,{className:a,children:e.jsx(je,{models:s,children:n=>e.jsxs(ce,{children:[e.jsxs(de,{children:[e.jsxs(me,{children:[H(n.interval)&&e.jsx(Ce,{start:n.interval[0],end:n.interval[1]}),e.jsx(Se,{modelName:n.displayViewName,changeType:De({modelName:n.name,added:t,removed:r,direct:l,indirect:i,metadata:c})})]}),e.jsxs(ue,{children:[m&&e.jsx(ae,{completed:n.completed,total:n.total,unit:"batch"}),e.jsx(ne,{}),o&&e.jsx(e.Fragment,{children:E(n.end)||E(n.start)?e.jsx(pe,{total:n.total,completed:n.completed}):e.jsx(Ae,{start:n.start,end:n.end})}),d&&e.jsx("span",{className:"inline-block whitespace-nowrap font-bold ml-2",children:"Updated"})]})]}),o?e.jsx(se,{progress:Q(n.completed,n.total),startFromZero:u.findIndex(x=>x.name===n.name)===-1}):e.jsx(oe,{className:"my-1 border-neutral-200 opacity-50"})]})})})]})}function be({className:s,children:a}){return e.jsx("div",{className:g("max-h-[50vh] overflow-auto hover:scrollbar scrollbar--vertical scrollbar--horizontal",s),children:a})}function ce({className:s,children:a}){return e.jsx("div",{className:g("px-2",s),children:a})}function je({className:s,models:a,children:t}){return e.jsx("ul",{className:g("rounded-lg pt-4 overflow-auto text-prose hover:scrollbar scrollbar--vertical scrollbar--horizontal",s),children:a.map(r=>e.jsx("li",{className:"mb-2",children:t(r)},r.name))})}function de({className:s,children:a}){return e.jsx("div",{className:g("flex sm:justify-between sm:items-baseline text-xs",s),children:a})}function Be({className:s,headline:a,environment:t}){return e.jsxs("span",{className:g("flex items-center",s),children:[e.jsx("span",{className:"block whitespace-nowrap text-sm font-medium",children:a}),M(t)&&e.jsx("small",{className:"inline-block ml-1 px-2 py-[0.125rem] text-xs font-bold bg-neutral-10 rounded-md",children:t})]})}function me({className:s,children:a}){return e.jsx("div",{className:g("flex mr-6 w-full sm:w-auto overflow-hidden",s),children:a})}function ue({className:s,children:a}){return e.jsx("div",{className:g("flex items-center",s),children:a})}function Ce({className:s,start:a,end:t}){return e.jsxs("span",{className:g("inline-block mr-2 whitespace-nowrap font-mono",s),children:[a," – ",t]})}function ae({className:s,total:a,completed:t,unit:r}){return e.jsxs("span",{className:g("inline-block whitespace-nowrap",s),children:[t," of ",a," ",fs(r,a)]})}function ne({className:s}){return e.jsx("span",{className:g("inline-block mx-2",s),children:"|"})}function pe({className:s,total:a,completed:t}){return e.jsxs("span",{className:g("inline-block whitespace-nowrap font-bold",s),children:[Math.ceil(Q(t,a)),"%"]})}function Ae({className:s,start:a,end:t}){return e.jsx("span",{className:g("inline-block whitespace-nowrap font-bold",s),children:`${Math.floor((t-a)/6e4)}:${String(Math.ceil((t-a)/1e3%60)).padStart(2,"0")}`})}function Es({updateType:s,updatedAt:a}){return e.jsxs("div",{className:"flex justify-between mt-1",children:[e.jsxs("small",{className:"text-xs",children:[e.jsx("b",{children:"Update Type:"}),e.jsx("span",{className:"inline-block ml-1",children:s})]}),e.jsxs("small",{className:"text-xs",children:[e.jsx("b",{children:"Last Update:"}),e.jsx("span",{className:"inline-block ml-1",children:he(new Date(a),"yyyy-mm-dd hh-mm-ss",!1)})]})]})}function Se({className:s,modelName:a,changeType:t}){return e.jsx("span",{className:g("font-bold whitespace-nowrap",t===A.Add&&"text-success-600  dark:text-success-500",t===A.Remove&&"text-danger-500",t===A.Direct&&"text-secondary-500 dark:text-primary-500",t===A.Indirect&&"text-warning-500",t===A.Default&&"text-prose",s),children:a})}v.Block=be;v.Summary=Fs;v.Details=Rs;v.DetailsProgress=ue;v.Task=ce;v.Tasks=je;v.TaskDetails=de;v.TaskProgress=pe;v.TaskSize=ae;v.TaskDivider=ne;v.TaskInfo=me;v.TaskHeadline=Be;function De({modelName:s,added:a,removed:t,direct:r,indirect:l,metadata:i}){return a.some(c=>c.name===s)?A.Add:t.some(c=>c.name===s)?A.Remove:r.some(c=>c.name===s)?A.Direct:l.some(c=>c.name===s)?A.Indirect:i.some(c=>c.name===s)?A.Metadata:A.Default}function Bs({report:s}){var a;return e.jsxs("div",{children:[e.jsxs("div",{className:"py-2",children:[e.jsxs("p",{children:["Total: ",s.total]}),e.jsxs("p",{children:["Succeeded: ",s.successful]}),e.jsxs("p",{children:["Failed: ",s.failures]}),e.jsxs("p",{children:["Errors: ",s.errors]}),e.jsxs("p",{children:["Dialect: ",s.dialect]})]}),e.jsx("ul",{children:(a=s.details)==null?void 0:a.map(t=>e.jsxs("li",{className:"flex mb-1",children:[e.jsx("span",{className:"inline-block mr-4",children:"—"}),e.jsxs("div",{className:"overflow-hidden",children:[e.jsx("span",{className:"inline-block mb-2",children:t.message}),e.jsx("code",{className:"inline-block max-h-[50vh] bg-theme py-2 px-4 rounded-lg w-full overflow-auto hover:scrollbar scrollbar--vertical scrollbar--horizontal",children:e.jsx("pre",{children:t.details})})]})]},t.message))})]})}function _s(){var f;const s=Ee(h=>h.tests),a=j(h=>h.planApply),t=j(h=>h.planOverview),r=j(h=>h.planCancel),l=j(h=>h.planAction),{plan_options:i,hasChanges:c,hasBackfills:m,isFailed:o}=X(a,t,r),d=M(s)&&!!s.total,u=M(s)&&!!s.message&&T(d),n=M(s)&&(!!s.failures||!!s.errors),x=T(l.isProcessing)&&T(l.isDone)&&T(r.isFinished),p=o&&[n,d,c,m].every(Le);return e.jsx(ee,{appear:!0,show:T(l.isRun),enter:"transition ease duration-300 transform",enterFrom:"opacity-0 scale-95",enterTo:"opacity-100 scale-100",leave:"transition ease duration-300 transform",leaveFrom:"opacity-100 scale-100",leaveTo:"opacity-0 scale-95",className:g("my-2 rounded-xl",o&&"bg-danger-5"),children:p?e.jsxs(S,{className:"flex items-center",size:P.sm,variant:I.Danger,children:[e.jsx(xe,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"Plan Failed"})]}):e.jsxs(e.Fragment,{children:[o&&e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,variant:I.Danger,children:[e.jsx(xe,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"Plan Failed"})]}),V(i==null?void 0:i.skip_tests)?e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,hasBackground:!1,children:[e.jsx(W,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"Tests Skipped"})]}):d?e.jsx(zs,{isOpen:!0,report:s}):u?e.jsx(Ms,{report:s}):e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,hasBackground:!1,children:[e.jsx(W,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"No Tests"})]}),T(n)&&e.jsxs(e.Fragment,{children:[e.jsx(Os,{isOpen:x}),e.jsx(Is,{isOpen:x}),e.jsx(Hs,{}),a.shouldShowEvaluation&&e.jsxs(Ls,{start:a.evaluationStart,end:a.isFinished?a.evaluationEnd??((f=r.meta)==null?void 0:f.end):void 0,children:[e.jsx(Us,{}),e.jsx($s,{}),e.jsx(Vs,{}),e.jsx(Gs,{})]})]})]})})}function Os({isOpen:s=!1}){var d;const a=j(u=>u.planApply),t=j(u=>u.planOverview),r=j(u=>u.planCancel),{meta:l,stageChanges:i,hasChanges:c}=X(a,t,r),m=(i==null?void 0:i.meta)??l;return Ue([L.init,L.fail],(d=i==null?void 0:i.meta)==null?void 0:d.status)||V(c)?e.jsx(G,{meta:m,states:["Changes","Failed Getting Changes","Getting Changes..."],isOpen:s&&V(c),panel:e.jsx(qs,{})}):e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,hasBackground:!1,children:[e.jsx(W,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"No Changes"})]})}function Is({isOpen:s=!1}){const{change_categorization:a}=Y(),t=j(p=>p.planApply),r=j(p=>p.planOverview),l=j(p=>p.planCancel),{meta:i,stageBackfills:c,backfills:m,hasBackfills:o}=X(t,r,l),d=(c==null?void 0:c.meta)??i,u=y.useMemo(()=>Array.from(a.values()).reduce((p,{category:f,change:h})=>{var C;return(f==null?void 0:f.value)!==re.NUMBER_3&&p.add(h.name),(E(f)||f.value===re.NUMBER_1)&&((C=h.indirect)==null||C.forEach(B=>p.add(B.name))),p},new Set),[a]),n=y.useMemo(()=>a.size>0?m.filter(p=>u.has(p.name)):m,[m,u]);return((d==null?void 0:d.status)===L.init||V(o))&&(a.size>0?n.length>0:!0)?e.jsx(G,{meta:d,states:["Backfills","Failed Getting Backfills","Getting Backfills..."],isOpen:s&&V(o),panel:e.jsx(U,{headline:`Models ${n.length}`,type:A.Default,children:e.jsx(U.Default,{type:A.Default,changes:n})})}):e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,hasBackground:!1,children:[e.jsx(W,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"No Backfills"})]})}function Ms({report:s}){return e.jsx(G,{meta:{status:L.success,...s},states:["Tests Completed","Failed Tests","Running Tests..."],children:s.message})}function zs({report:s,isOpen:a=!1}){return e.jsx(G,{variant:I.Danger,meta:{status:L.fail,...s},isOpen:a,states:["Tests Failed","One or More Tests Failed","Running Tests..."],shouldCollapse:!1,children:e.jsx(Bs,{report:s})})}function Ls({start:s,end:a,children:t}){const r=y.useRef(null);return y.useEffect(()=>{setTimeout(()=>{var l;(l=r.current)==null||l.scrollIntoView({behavior:"smooth",block:"start"})},500)},[]),E(s)?e.jsx(e.Fragment,{}):e.jsxs("div",{ref:r,className:"pt-4 pb-2 text-xs",children:[e.jsxs("span",{className:"text-neutral-500 block px-4 mb-1",children:["Evaluation started at"," ",he(new Date(s),"yyyy-mm-dd hh-mm-ss")]}),e.jsx(oe,{}),e.jsx("div",{className:"py-2",children:t}),M(a)&&e.jsxs(e.Fragment,{children:[e.jsx(oe,{}),e.jsxs("span",{className:"text-neutral-500 block px-4 mt-1",children:["Evaluation stopped at"," ",he(new Date(a),"yyyy-mm-dd hh-mm-ss")]})]})]})}function Us({isOpen:s}){var t;const a=j(r=>r.planApply);return E(a.stageCreation)?e.jsx(e.Fragment,{}):e.jsx(G,{meta:(t=a.stageCreation)==null?void 0:t.meta,states:["Snapshot Tables Created","Snapshot Tables Creation Failed","Creating Snapshot Tables..."],isOpen:s,children:e.jsx(v.Block,{children:e.jsxs(v.Task,{children:[e.jsxs(v.TaskDetails,{children:[e.jsx(v.TaskInfo,{children:e.jsx(v.TaskHeadline,{headline:"Snapshot Tables"})}),e.jsxs(v.DetailsProgress,{children:[e.jsx(v.TaskSize,{completed:a.stageCreation.num_tasks,total:a.stageCreation.total_tasks,unit:"task"}),e.jsx(v.TaskDivider,{}),e.jsx(v.TaskProgress,{completed:a.stageCreation.num_tasks,total:a.stageCreation.total_tasks})]})]}),e.jsx(se,{progress:Q(a.stageCreation.num_tasks,a.stageCreation.total_tasks)})]})})})}function $s(){var a;const s=j(t=>t.planApply);return E(s.stageRestate)?e.jsxs(S,{className:"flex items-center mb-1",size:P.sm,hasBackground:!1,children:[e.jsx(W,{className:"w-4 mr-2"}),e.jsx(S.Label,{className:"mr-2 text-sm",children:"No Models To Restate"})]}):e.jsx(G,{meta:(a=s.stageRestate)==null?void 0:a.meta,states:["Restate Models","Restate Models Failed","Restating Models..."]})}function Vs(){const s=j(d=>d.planApply),a=j(d=>d.planAction),t=j(d=>d.planOverview),r=j(d=>d.planCancel),l=s.environment,i=s.stageBackfill,{backfills:c}=X(s,t,r),m=y.useMemo(()=>Object.values(s.tasks).reduce((d,u)=>{const n=c.find(x=>x.name===u.name);return u.interval=(n==null?void 0:n.interval)??[],d[u.name]=u,d},{}),[c,s.tasks]);return M(i)&&M(l)?e.jsx(G,{meta:i.meta,states:["Backfilled","Backfilling Failed","Backfilling Intervals..."],showDetails:!0,isOpen:!0,shouldCollapse:!1,children:e.jsx(v,{tasks:m,children:({total:d,completed:u,models:n,completedBatches:x,totalBatches:p})=>e.jsxs(e.Fragment,{children:[e.jsx(v.Summary,{headline:"Target Environment",environment:l,completed:u,total:d,completedBatches:x,totalBatches:p,updateType:a.isApplyVirtual?"Virtual":"Backfill"}),M(n)&&e.jsx(v.Details,{models:n,added:s.added,removed:s.removed,direct:s.direct,indirect:s.indirect,metadata:s.metadata,queue:s.queue,showBatches:!0,showVirtualUpdate:a.isApplyVirtual,showProgress:!0})]})})}):e.jsx(e.Fragment,{})}function Gs(){var a;const s=j(t=>t.planApply);return E(s.stagePromote)?e.jsx(e.Fragment,{}):e.jsx("div",{children:e.jsx(G,{meta:(a=s.stagePromote)==null?void 0:a.meta,states:["Environment Promoted","Promotion Failed","Promoting Environment..."],children:e.jsx(v.Block,{children:e.jsxs(v.Task,{children:[e.jsxs(v.TaskDetails,{children:[e.jsx(v.TaskInfo,{children:e.jsx(v.TaskHeadline,{headline:`Promote Environment: ${s.stagePromote.target_environment}`})}),e.jsxs(v.DetailsProgress,{children:[e.jsx(v.TaskSize,{completed:s.stagePromote.num_tasks,total:s.stagePromote.total_tasks,unit:"task"}),e.jsx(v.TaskDivider,{}),e.jsx(v.TaskProgress,{completed:s.stagePromote.num_tasks,total:s.stagePromote.total_tasks})]})]}),e.jsx(se,{progress:Q(s.stagePromote.num_tasks,s.stagePromote.total_tasks)})]})})})})}function Hs(){var m;const{virtualUpdateDescription:s}=Y(),a=j(o=>o.planApply),t=j(o=>o.planOverview),r=j(o=>o.planCancel),{isFailed:l}=X(a,t,r),i=((m=a.overview)==null?void 0:m.isVirtualUpdate)??t.isVirtualUpdate,c=V(a.isFinished);return i&&T(l)?e.jsx(G,{meta:{status:L.success,done:c},states:[c?"Virtual Update Completed":"Virtual Update","Virtual Update Failed","Applying Virtual Update..."],children:s}):e.jsx(e.Fragment,{})}function qs(){const s=j(n=>n.planAction),a=j(n=>n.planOverview),t=j(n=>n.planApply),r=j(n=>n.planCancel),{hasChanges:l,added:i,removed:c,direct:m,indirect:o,metadata:d}=X(t,a,r),u=s.isProcessing||s.isDone||t.isFinished||a.isLatest&&T(s.isRun)||a.isVirtualUpdate;return e.jsx("div",{className:"w-full my-2",children:V(l)&&e.jsxs(e.Fragment,{children:[H(i)&&e.jsx(U,{className:"w-full my-2",headline:"Added Models",type:A.Add,children:e.jsx(U.Default,{type:A.Add,changes:i})}),H(c)&&e.jsx(U,{className:"w-full my-2",headline:"Removed Models",type:A.Remove,children:e.jsx(U.Default,{type:A.Remove,changes:c})}),H(m)&&e.jsx(U,{className:"my-2 w-full",headline:"Modified Directly",type:A.Direct,children:e.jsx(U.Direct,{changes:m,disabled:u})}),H(o)&&e.jsx(U,{className:"my-2 w-full",headline:"Modified Indirectly",type:A.Indirect,children:e.jsx(U.Indirect,{changes:o})}),H(d)&&e.jsx(U,{className:"my-2 w-full",headline:"Modified Metadata",type:A.Default,children:e.jsx(U.Default,{type:A.Default,changes:d})})]})})}function G({meta:s,states:a=["Success","Failed","Running"],isOpen:t=!1,trigger:r,panel:l,children:i,showDetails:c=!0,shouldCollapse:m=!0}){const o=y.useRef(null),d=j(D=>D.planOverview),u=j(D=>D.planApply),n=(s==null?void 0:s.status)!==L.fail&&M(l)||M(i),[x,p]=y.useState(t);y.useEffect(()=>{var D;E(o.current)||m&&(u.isFinished||d.isLatest)&&o.current.classList.contains("--is-open")&&((D=o.current)==null||D.click())},[o,d,u,m]),y.useEffect(()=>{p(t&&n)},[t,n]);const f=(s==null?void 0:s.status)===L.fail,h=(s==null?void 0:s.status)===L.success,C=(s==null?void 0:s.status)===L.init,B=h?I.Success:f?I.Danger:I.Info,[F,b,N]=a,w=h?F:f?b:N;return e.jsx(ee,{appear:!0,show:M(s),enter:"transition ease duration-300 transform",enterFrom:"opacity-0 scale-95",enterTo:"opacity-100 scale-100",leave:"transition ease duration-300 transform",leaveFrom:"opacity-100 scale-100",leaveTo:"opacity-0 scale-95",className:"my-2",children:e.jsxs($,{children:[e.jsx(S,{className:"mb-1",variant:B,size:P.sm,hasBackground:!1,hasBackgroundOnHover:n,children:e.jsx($.Button,{ref:o,className:g("w-full flex flex-col",x&&"--is-open",T(n)&&"cursor-default"),onClick:()=>p(D=>!D),children:E(r)?e.jsxs(e.Fragment,{children:[C&&e.jsx($e,{text:w,hasSpinner:!0,size:P.sm,variant:I.Primary,className:"w-full"}),T(C)&&e.jsxs("div",{className:"flex items-center h-full",children:[c&&n?e.jsx(e.Fragment,{children:x?e.jsx(ge,{className:"w-4 mr-2"}):e.jsx(ye,{className:"w-4 mr-2"})}):e.jsxs(e.Fragment,{children:[(s==null?void 0:s.status)===L.success&&e.jsx(W,{className:"min-w-4 max-w-4 mr-2"}),(s==null?void 0:s.status)===L.fail&&e.jsx(xe,{className:"min-w-4 max-w-4 mr-2"})]}),e.jsx(S.Label,{className:"mr-2 text-sm",children:e.jsx(Fe,{text:w,size:P.sm,variant:B})})]})]}):r})}),e.jsx(ee,{appear:!0,show:x,enter:"transition ease duration-300 transform",enterFrom:"opacity-0 scale-95",enterTo:"opacity-100 scale-100",leave:"transition ease duration-300 transform",leaveFrom:"opacity-100 scale-100",leaveTo:"opacity-0 scale-95",className:"trasition-all duration-300 ease-in-out",children:e.jsxs($.Panel,{static:!0,className:"px-2 text-xs mb-2",children:[M(i)&&e.jsx("div",{className:g("p-4 rounded-md",B===I.Danger?"bg-danger-5 text-danger-500":"bg-neutral-5"),children:i}),(s==null?void 0:s.status)!==L.fail&&l]})})]})})}function Ks(){const s=ve(),{clearErrors:a}=Ve(),t=O(w=>w.environment),r=j(w=>w.planAction),l=j(w=>w.setPlanAction),i=j(w=>w.resetPlanTrackers),c=j(w=>w.resetPlanCancel),m=j(w=>w.clearPlanApply),o=Ee(w=>w.setTests),d=Ss(),u=Ds(),{refetch:n,cancel:x}=Ge(t.name,d),{refetch:p,cancel:f}=He(t.name,u),{refetch:h}=qe();function C(){a(),s([{type:R.ResetPlanDates},{type:R.ResetPlanOptions},{type:R.ResetTestsReport},{type:R.ResetCategories}])}function B(){l(new Z({value:z.Run})),m(),C(),setTimeout(()=>i(),500)}function F(){l(new Z({value:z.Cancelling})),c(),s([{type:R.ResetTestsReport}]);let w;r.isApplying?w=x:w=f,w(),h()}function b(){l(new Z({value:z.Applying})),m(),s([{type:R.ResetTestsReport}]),p().catch(console.log)}function N(){l(new Z({value:z.Running})),i(),o(void 0),s([{type:R.ResetTestsReport}]),n().catch(console.log)}return e.jsxs("div",{className:"flex flex-col w-full h-full max-w-[80rem]",children:[t.isProd&&e.jsx(Ns,{}),e.jsxs("div",{className:"relative w-full h-full flex flex-col pt-2 pl-4 pr-2 overflow-y-scroll hover:scrollbar scrollbar--vertical",children:[e.jsx(As,{}),e.jsx(_s,{})]}),e.jsx(Ps,{apply:b,run:N,cancel:F,reset:B})]})}function fa(){const{environmentName:s}=Ke(),a=O(l=>l.environment),t=O(l=>l.environments),r=O(l=>l.setEnvironment);return y.useEffect(()=>{if(a.isInitialProd||s===a.name)return;const l=Array.from(t).find(i=>i.name===s);E(l)||r(l)},[s]),e.jsx(as,{children:E(a)?e.jsx(Ye,{link:Ze.Plan,description:E(s)?void 0:`Environment ${s} Does Not Exist`,message:"Back To Data Catalog"}):e.jsx(Ks,{})})}export{fa as default};
