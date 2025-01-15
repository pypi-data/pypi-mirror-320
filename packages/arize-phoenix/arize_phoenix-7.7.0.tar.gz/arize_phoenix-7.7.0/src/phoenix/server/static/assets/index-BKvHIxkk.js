import{r as c,j as e,dL as v,l as n,U as F,R as w,D as E,bq as L,dM as S,dN as R,dO as a,dP as k,t as I,dQ as A}from"./vendor-DvC8cT4X.js";import{k as C,Q as _,D as j,Y as z}from"./vendor-arizeai-Do1793cv.js";import{E as O,L as T,R as D,r as N,b as G,F as M,A as U,c as q,d as B,P as J,h as K,M as Q,e as m,D as V,f as W,g as H,i as Y,j as $,k as X,l as Z,p as ee,n as h,o as ae,S as re,s as te,q as oe,t as g,v as ne,w as u,x as b,y as se,z as le,B as ie,C as de,G as ce,H as x,I as pe,J as me,K as he,N as ge,O as ue,Q as be,U as xe,V as fe}from"./pages-CUi2xCVQ.js";import{V as Pe,d0 as ye,at as ve,ab as Fe,d1 as we,d2 as Ee}from"./components-Cy9nwIvF.js";import"./vendor-three-DwGkEfCM.js";import"./vendor-codemirror-BzwZPyJM.js";import"./vendor-shiki-Cl9QBraO.js";import"./vendor-recharts-_Jb7JjhG.js";(function(){const s=document.createElement("link").relList;if(s&&s.supports&&s.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))d(t);new MutationObserver(t=>{for(const o of t)if(o.type==="childList")for(const l of o.addedNodes)l.tagName==="LINK"&&l.rel==="modulepreload"&&d(l)}).observe(document,{childList:!0,subtree:!0});function i(t){const o={};return t.integrity&&(o.integrity=t.integrity),t.referrerPolicy&&(o.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?o.credentials="include":t.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function d(t){if(t.ep)return;t.ep=!0;const o=i(t);fetch(t.href,o)}})();const f="arize-phoenix-feature-flags",p={__RESET__:!1};function Le(){const r=localStorage.getItem(f);if(!r)return p;try{const s=JSON.parse(r);return Object.assign({},p,s)}catch{return p}}const P=c.createContext(null);function Se(){const r=w.useContext(P);if(r===null)throw new Error("useFeatureFlags must be used within a FeatureFlagsProvider");return r}function Re(r){const[s,i]=c.useState(Le()),d=t=>{localStorage.setItem(f,JSON.stringify(t)),i(t)};return e(P.Provider,{value:{featureFlags:s,setFeatureFlags:d},children:e(ke,{children:r.children})})}function ke(r){const{children:s}=r,{featureFlags:i,setFeatureFlags:d}=Se(),[t,o]=c.useState(!1);return v("ctrl+shift+f",()=>o(!0)),n(F,{children:[s,e(j,{type:"modal",isDismissable:!0,onDismiss:()=>o(!1),children:t&&e(C,{title:"Feature Flags",children:e(Pe,{height:"size-1000",padding:"size-100",children:Object.keys(i).map(l=>e(_,{isSelected:i[l],onChange:y=>d({...i,[l]:y}),children:l},l))})})})]})}function Ie(){return e(L,{styles:E`
        body {
          background-color: var(--ac-global-color-grey-75);
          color: var(--ac-global-text-color-900);
          font-family: "Roboto";
          font-size: var(--ac-global-font-size-s);
          margin: 0;
          overflow: hidden;
          #root,
          #root > div[data-overlay-container="true"],
          #root > div[data-overlay-container="true"] > .ac-theme {
            height: 100vh;
          }
        }

        /* Remove list styling */
        ul {
          display: block;
          list-style-type: none;
          margin-block-start: none;
          margin-block-end: 0;
          padding-inline-start: 0;
          margin-block-start: 0;
        }

        /* A reset style for buttons */
        .button--reset {
          background: none;
          border: none;
          padding: 0;
        }
        /* this css class is added to html via modernizr @see modernizr.js */
        .no-hiddenscroll {
          /* Works on Firefox */
          * {
            scrollbar-width: thin;
            scrollbar-color: var(--ac-global-color-grey-300)
              var(--ac-global-color-grey-400);
          }

          /* Works on Chrome, Edge, and Safari */
          *::-webkit-scrollbar {
            width: 14px;
          }

          *::-webkit-scrollbar-track {
            background: var(--ac-global-color-grey-100);
          }

          *::-webkit-scrollbar-thumb {
            background-color: var(--ac-global-color-grey-75);
            border-radius: 8px;
            border: 1px solid var(--ac-global-color-grey-300);
          }
        }

        :root {
          --px-section-background-color: #2f353d;

          /** The color of shadows on menus etc. */
          --px-overlay-shadow-color: rgba(0, 0, 0, 0.4);

          /* An item is a typically something in a list */
          --px-item-background-color: #1d2126;
          --px-item-border-color: #282e35;

          --px-font-weight-heavy: 600;

          --px-gradient-bar-height: 8px;

          --px-nav-collapsed-width: 45px;
          --px-nav-expanded-width: 200px;

          --ac-global-opacity-disabled: 0.6;

          /* Text */
          --ac-global-font-size-xxs: 10px;
          --ac-global-font-size-xs: 12px;
          --ac-global-font-size-s: 14px;
          --ac-global-font-size-m: 16px;
          --ac-global-font-size-l: 18px;
          --ac-global-font-size-xl: 24px;
          --ac-global-font-size-xxl: 32px;

          --ac-global-line-height-xxs: 12px;
          --ac-global-line-height-xs: 16px;
          --ac-global-line-height-s: 20px;
          --ac-global-line-height-m: 24px;
          --ac-global-line-height-l: 28px;
          --ac-global-line-height-xl: 36px;
          --ac-global-line-height-xxl: 48px;

          /* Fields */
          --ac-global-input-field-min-width: 200px;
        }

        .ac-theme--dark {
          --px-primary-color: #9efcfd;
          --px-primary-color--transparent: rgb(158, 252, 253, 0.2);
          --px-reference-color: #baa1f9;
          --px-reference-color--transparent: #baa1f982;
          --px-corpus-color: #92969c;
          --px-corpus-color--transparent: #92969c63;
        }
        .ac-theme--light {
          --px-primary-color: #00add0;
          --px-primary-color--transparent: rgba(0, 173, 208, 0.2);
          --px-reference-color: #4500d9;
          --px-reference-color--transparent: rgba(69, 0, 217, 0.2);
          --px-corpus-color: #92969c;
          --px-corpus-color--transparent: #92969c63;
        }
      `})}const Ae=S(R(n(a,{path:"/",errorElement:e(O,{}),children:[e(a,{path:"/login",element:e(T,{})}),e(a,{path:"/reset-password",element:e(D,{}),loader:N}),e(a,{path:"/reset-password-with-token",element:e(G,{})}),e(a,{path:"/forgot-password",element:e(M,{})}),e(a,{element:e(U,{}),loader:q,children:n(a,{element:e(B,{}),children:[e(a,{path:"/profile",handle:{crumb:()=>"profile"},element:e(J,{})}),e(a,{index:!0,loader:K}),n(a,{path:"/model",handle:{crumb:()=>"model"},element:e(Q,{}),children:[e(a,{index:!0,element:e(m,{})}),e(a,{element:e(m,{}),children:e(a,{path:"dimensions",children:e(a,{path:":dimensionId",element:e(V,{}),loader:W})})}),e(a,{path:"embeddings",children:e(a,{path:":embeddingDimensionId",element:e(H,{}),loader:Y,handle:{crumb:r=>r.embedding.name}})})]}),n(a,{path:"/projects",handle:{crumb:()=>"projects"},element:e($,{}),children:[e(a,{index:!0,element:e(X,{})}),n(a,{path:":projectId",element:e(Z,{}),loader:ee,handle:{crumb:r=>r.project.name},children:[e(a,{index:!0,element:e(h,{})}),n(a,{element:e(h,{}),children:[e(a,{path:"traces/:traceId",element:e(ae,{})}),e(a,{path:"sessions/:sessionId",element:e(re,{}),loader:te})]})]})]}),n(a,{path:"/datasets",handle:{crumb:()=>"datasets"},children:[e(a,{index:!0,element:e(oe,{})}),n(a,{path:":datasetId",loader:g,handle:{crumb:r=>r.dataset.name},children:[n(a,{element:e(ne,{}),loader:g,children:[e(a,{index:!0,element:e(u,{}),loader:b}),e(a,{path:"experiments",element:e(u,{}),loader:b}),e(a,{path:"examples",element:e(se,{}),loader:le,children:e(a,{path:":exampleId",element:e(ie,{})})})]}),e(a,{path:"compare",handle:{crumb:()=>"compare"},loader:de,element:e(ce,{})})]})]}),n(a,{path:"/playground",handle:{crumb:()=>"Playground"},children:[e(a,{index:!0,element:e(x,{})}),e(a,{path:"datasets/:datasetId",element:e(x,{}),children:e(a,{path:"examples/:exampleId",element:e(pe,{})})}),e(a,{path:"spans/:spanId",element:e(me,{}),loader:he,handle:{crumb:r=>r.span.__typename==="Span"?`span ${r.span.context.spanId}`:"span unknown"}})]}),e(a,{path:"/apis",element:e(ge,{}),handle:{crumb:()=>"APIs"}}),e(a,{path:"/support",element:e(ue,{}),handle:{crumb:()=>"Support"}}),e(a,{path:"/settings",element:e(be,{}),handle:{crumb:()=>"Settings"}})]})})]})),{basename:window.Config.basename});function Ce(){return e(k,{router:Ae})}function _e(){return e(xe,{children:e(ye,{children:e(je,{})})})}function je(){const{theme:r}=ve();return e(z,{theme:r,children:n(I.RelayEnvironmentProvider,{environment:Fe,children:[e(Ie,{}),e(Re,{children:e(we,{children:e(fe,{children:e(c.Suspense,{children:e(Ee,{children:e(Ce,{})})})})})})]})})}const ze=document.getElementById("root"),Oe=A.createRoot(ze);Oe.render(e(_e,{}));
