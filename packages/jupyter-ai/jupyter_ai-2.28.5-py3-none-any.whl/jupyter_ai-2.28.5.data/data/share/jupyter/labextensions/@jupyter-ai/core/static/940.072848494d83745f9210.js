"use strict";(self.webpackChunk_jupyter_ai_core=self.webpackChunk_jupyter_ai_core||[]).push([[940],{6216:(e,t,n)=>{n.d(t,{c:()=>a});var c=n(7172),r=n(9036),o=(n(6512),n(8872)),u=n(7704),s=n(7e3);const i=["theme"];function a(e){let{theme:t}=e,n=(0,r.c)(e,i);const a=t[u.c];return(0,s.jsx)(o.c,(0,c.c)({},n,{themeId:a?u.c:void 0,theme:a||t}))}},7264:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(9700).c},9860:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(9840).c},8048:(e,t,n)=>{n.r(t),n.d(t,{capitalize:()=>r.c,createChainedFunction:()=>o.c,createSvgIcon:()=>u.c,debounce:()=>s.c,deprecatedPropType:()=>i,isMuiElement:()=>a.c,ownerDocument:()=>l.c,ownerWindow:()=>d.c,requirePropFactory:()=>f,setRef:()=>m,unstable_ClassNameGenerator:()=>x,unstable_useEnhancedEffect:()=>h.c,unstable_useId:()=>v.c,unsupportedProp:()=>p,useControlled:()=>y.c,useEventCallback:()=>E.c,useForkRef:()=>b.c,useIsFocusVisible:()=>w.c});var c=n(1384),r=n(7836),o=n(7264),u=n(200),s=n(9860);const i=function(e,t){return()=>null};var a=n(6816),l=n(1560),d=n(6400);n(7172);const f=function(e,t){return()=>null},m=n(6136).c;var h=n(4020),v=n(28);const p=function(e,t,n,c,r){return null};var y=n(8636),E=n(5004),b=n(376),w=n(8680);const x={configure:e=>{c.c.configure(e)}}},6816:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(5376).c},1560:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(368).c},6400:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(8996).c},8636:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(7920).c},4020:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(9632).c},5004:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(2376).c},376:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(2252).c},28:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(7984).c},8680:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(80).c},2816:(e,t,n)=>{n.d(t,{c:()=>c});const c=n(6512).createContext(null)},8096:(e,t,n)=>{n.d(t,{c:()=>o});var c=n(6512),r=n(2816);function o(){return c.useContext(r.c)}},8872:(e,t,n)=>{n.d(t,{c:()=>h});var c=n(7172),r=n(6512),o=n(8096),u=n(2816);const s="function"==typeof Symbol&&Symbol.for?Symbol.for("mui.nested"):"__THEME_NESTED__";var i=n(7e3);const a=function(e){const{children:t,theme:n}=e,a=(0,o.c)(),l=r.useMemo((()=>{const e=null===a?n:function(e,t){return"function"==typeof t?t(e):(0,c.c)({},e,t)}(a,n);return null!=e&&(e[s]=null!==a),e}),[n,a]);return(0,i.jsx)(u.c.Provider,{value:l,children:t})};var l=n(8640),d=n(2788);const f={};function m(e,t,n,o=!1){return r.useMemo((()=>{const r=e&&t[e]||t;if("function"==typeof n){const u=n(r),s=e?(0,c.c)({},t,{[e]:u}):u;return o?()=>s:s}return e?(0,c.c)({},t,{[e]:n}):(0,c.c)({},t,n)}),[e,t,n,o])}const h=function(e){const{children:t,theme:n,themeId:c}=e,r=(0,d.c)(f),u=(0,o.c)()||f,s=m(c,r,n),h=m(c,u,n,!0);return(0,i.jsx)(a,{theme:h,children:(0,i.jsx)(l.ThemeContext.Provider,{value:s,children:t})})}},7856:(e,t,n)=>{n.d(t,{c:()=>m});var c=n(7172),r=n(9036),o=n(6512),u=n(3816),s=n(6184),i=n(6852),a=n(8100),l=n(7280),d=n(7e3);const f=["className","component"];function m(e={}){const{themeId:t,defaultTheme:n,defaultClassName:m="MuiBox-root",generateClassName:h}=e,v=(0,s.cp)("div",{shouldForwardProp:e=>"theme"!==e&&"sx"!==e&&"as"!==e})(i.c);return o.forwardRef((function(e,o){const s=(0,l.c)(n),i=(0,a.c)(e),{className:p,component:y="div"}=i,E=(0,r.c)(i,f);return(0,d.jsx)(v,(0,c.c)({as:y,ref:o,className:(0,u.c)(p,h?h(m):m),theme:t&&s[t]||s},E))}))}},8100:(e,t,n)=>{n.d(t,{c:()=>a});var c=n(7172),r=n(9036),o=n(4320),u=n(6764);const s=["sx"],i=e=>{var t,n;const c={systemProps:{},otherProps:{}},r=null!=(t=null==e||null==(n=e.theme)?void 0:n.unstable_sxConfig)?t:u.c;return Object.keys(e).forEach((t=>{r[t]?c.systemProps[t]=e[t]:c.otherProps[t]=e[t]})),c};function a(e){const{sx:t}=e,n=(0,r.c)(e,s),{systemProps:u,otherProps:a}=i(n);let l;return l=Array.isArray(t)?[u,...t]:"function"==typeof t?(...e)=>{const n=t(...e);return(0,o.o)(n)?(0,c.c)({},u,n):u}:(0,c.c)({},u,t),(0,c.c)({},a,{sx:l})}},9700:(e,t,n)=>{function c(...e){return e.reduce(((e,t)=>null==t?e:function(...n){e.apply(this,n),t.apply(this,n)}),(()=>{}))}n.d(t,{c:()=>c})},9840:(e,t,n)=>{function c(e,t=166){let n;function c(...c){clearTimeout(n),n=setTimeout((()=>{e.apply(this,c)}),t)}return c.clear=()=>{clearTimeout(n)},c}n.d(t,{c:()=>c})},5376:(e,t,n)=>{n.d(t,{c:()=>r});var c=n(6512);function r(e,t){var n,r;return c.isValidElement(e)&&-1!==t.indexOf(null!=(n=e.type.muiName)?n:null==(r=e.type)||null==(r=r._payload)||null==(r=r.value)?void 0:r.muiName)}},368:(e,t,n)=>{function c(e){return e&&e.ownerDocument||document}n.d(t,{c:()=>c})},8996:(e,t,n)=>{n.d(t,{c:()=>r});var c=n(368);function r(e){return(0,c.c)(e).defaultView||window}},6136:(e,t,n)=>{function c(e,t){"function"==typeof e?e(t):e&&(e.current=t)}n.d(t,{c:()=>c})},7920:(e,t,n)=>{n.d(t,{c:()=>r});var c=n(6512);function r({controlled:e,default:t,name:n,state:r="value"}){const{current:o}=c.useRef(void 0!==e),[u,s]=c.useState(t);return[o?e:u,c.useCallback((e=>{o||s(e)}),[])]}},9632:(e,t,n)=>{n.d(t,{c:()=>r});var c=n(6512);const r="undefined"!=typeof window?c.useLayoutEffect:c.useEffect},2376:(e,t,n)=>{n.d(t,{c:()=>o});var c=n(6512),r=n(9632);const o=function(e){const t=c.useRef(e);return(0,r.c)((()=>{t.current=e})),c.useRef(((...e)=>(0,t.current)(...e))).current}},2252:(e,t,n)=>{n.d(t,{c:()=>o});var c=n(6512),r=n(6136);function o(...e){return c.useMemo((()=>e.every((e=>null==e))?null:t=>{e.forEach((e=>{(0,r.c)(e,t)}))}),e)}},7984:(e,t,n)=>{n.d(t,{c:()=>u});var c=n(6512);let r=0;const o=c["useId".toString()];function u(e){if(void 0!==o){const t=o();return null!=e?e:t}return function(e){const[t,n]=c.useState(e),o=e||t;return c.useEffect((()=>{null==t&&(r+=1,n(`mui-${r}`))}),[t]),o}(e)}},80:(e,t,n)=>{n.d(t,{c:()=>f});var c=n(6512),r=n(5288);let o=!0,u=!1;const s=new r.S,i={text:!0,search:!0,url:!0,tel:!0,email:!0,password:!0,number:!0,date:!0,month:!0,week:!0,time:!0,datetime:!0,"datetime-local":!0};function a(e){e.metaKey||e.altKey||e.ctrlKey||(o=!0)}function l(){o=!1}function d(){"hidden"===this.visibilityState&&u&&(o=!0)}function f(){const e=c.useCallback((e=>{var t;null!=e&&((t=e.ownerDocument).addEventListener("keydown",a,!0),t.addEventListener("mousedown",l,!0),t.addEventListener("pointerdown",l,!0),t.addEventListener("touchstart",l,!0),t.addEventListener("visibilitychange",d,!0))}),[]),t=c.useRef(!1);return{isFocusVisibleRef:t,onFocus:function(e){return!!function(e){const{target:t}=e;try{return t.matches(":focus-visible")}catch(e){}return o||function(e){const{type:t,tagName:n}=e;return!("INPUT"!==n||!i[t]||e.readOnly)||"TEXTAREA"===n&&!e.readOnly||!!e.isContentEditable}(t)}(e)&&(t.current=!0,!0)},onBlur:function(){return!!t.current&&(u=!0,s.start(100,(()=>{u=!1})),t.current=!1,!0)},ref:e}}},5288:(e,t,n)=>{n.d(t,{S:()=>u,c:()=>s});var c=n(6512);const r={},o=[];class u{constructor(){this.currentId=0,this.clear=()=>{0!==this.currentId&&(clearTimeout(this.currentId),this.currentId=0)},this.disposeEffect=()=>this.clear}static create(){return new u}start(e,t){this.clear(),this.currentId=setTimeout((()=>{this.currentId=0,t()}),e)}}function s(){const e=function(e,t){const n=c.useRef(r);return n.current===r&&(n.current=e(void 0)),n}(u.create).current;var t;return t=e.disposeEffect,c.useEffect(t,o),e}}}]);