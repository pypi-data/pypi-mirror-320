"use strict";(self.webpackChunk_jupyter_ai_core=self.webpackChunk_jupyter_ai_core||[]).push([[400],{792:(e,r,t)=>{function n(e){var r=Object.create(null);return function(t){return void 0===r[t]&&(r[t]=e(t)),r[t]}}t.d(r,{c:()=>n})},3132:(e,r,t)=>{t.d(r,{k:()=>m});var n={animationIterationCount:1,aspectRatio:1,borderImageOutset:1,borderImageSlice:1,borderImageWidth:1,boxFlex:1,boxFlexGroup:1,boxOrdinalGroup:1,columnCount:1,columns:1,flex:1,flexGrow:1,flexPositive:1,flexShrink:1,flexNegative:1,flexOrder:1,gridRow:1,gridRowEnd:1,gridRowSpan:1,gridRowStart:1,gridColumn:1,gridColumnEnd:1,gridColumnSpan:1,gridColumnStart:1,msGridRow:1,msGridRowSpan:1,msGridColumn:1,msGridColumnSpan:1,fontWeight:1,lineHeight:1,opacity:1,order:1,orphans:1,tabSize:1,widows:1,zIndex:1,zoom:1,WebkitLineClamp:1,fillOpacity:1,floodOpacity:1,stopOpacity:1,strokeDasharray:1,strokeDashoffset:1,strokeMiterlimit:1,strokeOpacity:1,strokeWidth:1},o=t(792),i=/[A-Z]|^ms/g,a=/_EMO_([^_]+?)_([^]*?)_EMO_/g,s=function(e){return 45===e.charCodeAt(1)},u=function(e){return null!=e&&"boolean"!=typeof e},l=(0,o.c)((function(e){return s(e)?e:e.replace(i,"-$&").toLowerCase()})),c=function(e,r){switch(e){case"animation":case"animationName":if("string"==typeof r)return r.replace(a,(function(e,r,t){return d={name:r,styles:t,next:d},r}))}return 1===n[e]||s(e)||"number"!=typeof r||0===r?r:r+"px"};function f(e,r,t){if(null==t)return"";if(void 0!==t.__emotion_styles)return t;switch(typeof t){case"boolean":return"";case"object":if(1===t.anim)return d={name:t.name,styles:t.styles,next:d},t.name;if(void 0!==t.styles){var n=t.next;if(void 0!==n)for(;void 0!==n;)d={name:n.name,styles:n.styles,next:d},n=n.next;return t.styles+";"}return function(e,r,t){var n="";if(Array.isArray(t))for(var o=0;o<t.length;o++)n+=f(e,r,t[o])+";";else for(var i in t){var a=t[i];if("object"!=typeof a)null!=r&&void 0!==r[a]?n+=i+"{"+r[a]+"}":u(a)&&(n+=l(i)+":"+c(i,a)+";");else if(!Array.isArray(a)||"string"!=typeof a[0]||null!=r&&void 0!==r[a[0]]){var s=f(e,r,a);switch(i){case"animation":case"animationName":n+=l(i)+":"+s+";";break;default:n+=i+"{"+s+"}"}}else for(var d=0;d<a.length;d++)u(a[d])&&(n+=l(i)+":"+c(i,a[d])+";")}return n}(e,r,t);case"function":if(void 0!==e){var o=d,i=t(e);return d=o,f(e,r,i)}}if(null==r)return t;var a=r[t];return void 0!==a?a:t}var d,v=/label:\s*([^\s;\n{]+)\s*(;|$)/g,m=function(e,r,t){if(1===e.length&&"object"==typeof e[0]&&null!==e[0]&&void 0!==e[0].styles)return e[0];var n=!0,o="";d=void 0;var i=e[0];null==i||void 0===i.raw?(n=!1,o+=f(t,r,i)):o+=i[0];for(var a=1;a<e.length;a++)o+=f(t,r,e[a]),n&&(o+=i[a]);v.lastIndex=0;for(var s,u="";null!==(s=v.exec(o));)u+="-"+s[1];var l=function(e){for(var r,t=0,n=0,o=e.length;o>=4;++n,o-=4)r=1540483477*(65535&(r=255&e.charCodeAt(n)|(255&e.charCodeAt(++n))<<8|(255&e.charCodeAt(++n))<<16|(255&e.charCodeAt(++n))<<24))+(59797*(r>>>16)<<16),t=1540483477*(65535&(r^=r>>>24))+(59797*(r>>>16)<<16)^1540483477*(65535&t)+(59797*(t>>>16)<<16);switch(o){case 3:t^=(255&e.charCodeAt(n+2))<<16;case 2:t^=(255&e.charCodeAt(n+1))<<8;case 1:t=1540483477*(65535&(t^=255&e.charCodeAt(n)))+(59797*(t>>>16)<<16)}return(((t=1540483477*(65535&(t^=t>>>13))+(59797*(t>>>16)<<16))^t>>>15)>>>0).toString(36)}(o)+u;return{name:l,styles:o,next:d}}},5864:(e,r,t)=>{t.d(r,{A:()=>i,k:()=>a});var n=t(6512),o=!!n.useInsertionEffect&&n.useInsertionEffect,i=o||function(e){return e()},a=o||n.useLayoutEffect},4432:(e,r,t)=>{function n(e,r,t){var n="";return t.split(" ").forEach((function(t){void 0!==e[t]?r.push(e[t]+";"):n+=t+" "})),n}t.d(r,{Up:()=>o,aE:()=>i,yI:()=>n});var o=function(e,r,t){var n=e.key+"-"+r.name;!1===t&&void 0===e.registered[n]&&(e.registered[n]=r.styles)},i=function(e,r,t){o(e,r,t);var n=e.key+"-"+r.name;if(void 0===e.inserted[r.name]){var i=r;do{e.insert(r===i?"."+n:"",i,e.sheet,!0),i=i.next}while(void 0!==i)}}}}]);