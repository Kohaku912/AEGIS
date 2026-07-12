var c_=s=>{throw TypeError(s)};var yd=(s,t,n)=>t.has(s)||c_("Cannot "+n);var j=(s,t,n)=>(yd(s,t,"read from private field"),n?n.call(s):t.get(s)),te=(s,t,n)=>t.has(s)?c_("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(s):t.set(s,n),zt=(s,t,n,a)=>(yd(s,t,"write to private field"),a?a.call(s,n):t.set(s,n),n),Ae=(s,t,n)=>(yd(s,t,"access private method"),n);var Mu=(s,t,n,a)=>({set _(l){zt(s,t,l,n)},get _(){return j(s,t,a)}});(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const l of document.querySelectorAll('link[rel="modulepreload"]'))a(l);new MutationObserver(l=>{for(const c of l)if(c.type==="childList")for(const f of c.addedNodes)f.tagName==="LINK"&&f.rel==="modulepreload"&&a(f)}).observe(document,{childList:!0,subtree:!0});function n(l){const c={};return l.integrity&&(c.integrity=l.integrity),l.referrerPolicy&&(c.referrerPolicy=l.referrerPolicy),l.crossOrigin==="use-credentials"?c.credentials="include":l.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function a(l){if(l.ep)return;l.ep=!0;const c=n(l);fetch(l.href,c)}})();function ky(s){return s&&s.__esModule&&Object.prototype.hasOwnProperty.call(s,"default")?s.default:s}var xd={exports:{}},zl={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var u_;function iE(){if(u_)return zl;u_=1;var s=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function n(a,l,c){var f=null;if(c!==void 0&&(f=""+c),l.key!==void 0&&(f=""+l.key),"key"in l){c={};for(var d in l)d!=="key"&&(c[d]=l[d])}else c=l;return l=c.ref,{$$typeof:s,type:a,key:f,ref:l!==void 0?l:null,props:c}}return zl.Fragment=t,zl.jsx=n,zl.jsxs=n,zl}var f_;function aE(){return f_||(f_=1,xd.exports=iE()),xd.exports}var D=aE(),Sd={exports:{}},se={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var h_;function sE(){if(h_)return se;h_=1;var s=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),n=Symbol.for("react.fragment"),a=Symbol.for("react.strict_mode"),l=Symbol.for("react.profiler"),c=Symbol.for("react.consumer"),f=Symbol.for("react.context"),d=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),m=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),v=Symbol.for("react.activity"),y=Symbol.iterator;function x(O){return O===null||typeof O!="object"?null:(O=y&&O[y]||O["@@iterator"],typeof O=="function"?O:null)}var E={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},b=Object.assign,M={};function _(O,nt,St){this.props=O,this.context=nt,this.refs=M,this.updater=St||E}_.prototype.isReactComponent={},_.prototype.setState=function(O,nt){if(typeof O!="object"&&typeof O!="function"&&O!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,O,nt,"setState")},_.prototype.forceUpdate=function(O){this.updater.enqueueForceUpdate(this,O,"forceUpdate")};function I(){}I.prototype=_.prototype;function N(O,nt,St){this.props=O,this.context=nt,this.refs=M,this.updater=St||E}var C=N.prototype=new I;C.constructor=N,b(C,_.prototype),C.isPureReactComponent=!0;var V=Array.isArray;function F(){}var P={H:null,A:null,T:null,S:null},G=Object.prototype.hasOwnProperty;function U(O,nt,St){var q=St.ref;return{$$typeof:s,type:O,key:nt,ref:q!==void 0?q:null,props:St}}function w(O,nt){return U(O.type,nt,O.props)}function H(O){return typeof O=="object"&&O!==null&&O.$$typeof===s}function ut(O){var nt={"=":"=0",":":"=2"};return"$"+O.replace(/[=:]/g,function(St){return nt[St]})}var ot=/\/+/g;function mt(O,nt){return typeof O=="object"&&O!==null&&O.key!=null?ut(""+O.key):nt.toString(36)}function ct(O){switch(O.status){case"fulfilled":return O.value;case"rejected":throw O.reason;default:switch(typeof O.status=="string"?O.then(F,F):(O.status="pending",O.then(function(nt){O.status==="pending"&&(O.status="fulfilled",O.value=nt)},function(nt){O.status==="pending"&&(O.status="rejected",O.reason=nt)})),O.status){case"fulfilled":return O.value;case"rejected":throw O.reason}}throw O}function z(O,nt,St,q,ft){var Tt=typeof O;(Tt==="undefined"||Tt==="boolean")&&(O=null);var Mt=!1;if(O===null)Mt=!0;else switch(Tt){case"bigint":case"string":case"number":Mt=!0;break;case"object":switch(O.$$typeof){case s:case t:Mt=!0;break;case g:return Mt=O._init,z(Mt(O._payload),nt,St,q,ft)}}if(Mt)return ft=ft(O),Mt=q===""?"."+mt(O,0):q,V(ft)?(St="",Mt!=null&&(St=Mt.replace(ot,"$&/")+"/"),z(ft,nt,St,"",function(re){return re})):ft!=null&&(H(ft)&&(ft=w(ft,St+(ft.key==null||O&&O.key===ft.key?"":(""+ft.key).replace(ot,"$&/")+"/")+Mt)),nt.push(ft)),1;Mt=0;var Ft=q===""?".":q+":";if(V(O))for(var Vt=0;Vt<O.length;Vt++)q=O[Vt],Tt=Ft+mt(q,Vt),Mt+=z(q,nt,St,Tt,ft);else if(Vt=x(O),typeof Vt=="function")for(O=Vt.call(O),Vt=0;!(q=O.next()).done;)q=q.value,Tt=Ft+mt(q,Vt++),Mt+=z(q,nt,St,Tt,ft);else if(Tt==="object"){if(typeof O.then=="function")return z(ct(O),nt,St,q,ft);throw nt=String(O),Error("Objects are not valid as a React child (found: "+(nt==="[object Object]"?"object with keys {"+Object.keys(O).join(", ")+"}":nt)+"). If you meant to render a collection of children, use an array instead.")}return Mt}function Z(O,nt,St){if(O==null)return O;var q=[],ft=0;return z(O,q,"","",function(Tt){return nt.call(St,Tt,ft++)}),q}function $(O){if(O._status===-1){var nt=O._result;nt=nt(),nt.then(function(St){(O._status===0||O._status===-1)&&(O._status=1,O._result=St)},function(St){(O._status===0||O._status===-1)&&(O._status=2,O._result=St)}),O._status===-1&&(O._status=0,O._result=nt)}if(O._status===1)return O._result.default;throw O._result}var Et=typeof reportError=="function"?reportError:function(O){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var nt=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof O=="object"&&O!==null&&typeof O.message=="string"?String(O.message):String(O),error:O});if(!window.dispatchEvent(nt))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",O);return}console.error(O)},At={map:Z,forEach:function(O,nt,St){Z(O,function(){nt.apply(this,arguments)},St)},count:function(O){var nt=0;return Z(O,function(){nt++}),nt},toArray:function(O){return Z(O,function(nt){return nt})||[]},only:function(O){if(!H(O))throw Error("React.Children.only expected to receive a single React element child.");return O}};return se.Activity=v,se.Children=At,se.Component=_,se.Fragment=n,se.Profiler=l,se.PureComponent=N,se.StrictMode=a,se.Suspense=p,se.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=P,se.__COMPILER_RUNTIME={__proto__:null,c:function(O){return P.H.useMemoCache(O)}},se.cache=function(O){return function(){return O.apply(null,arguments)}},se.cacheSignal=function(){return null},se.cloneElement=function(O,nt,St){if(O==null)throw Error("The argument must be a React element, but you passed "+O+".");var q=b({},O.props),ft=O.key;if(nt!=null)for(Tt in nt.key!==void 0&&(ft=""+nt.key),nt)!G.call(nt,Tt)||Tt==="key"||Tt==="__self"||Tt==="__source"||Tt==="ref"&&nt.ref===void 0||(q[Tt]=nt[Tt]);var Tt=arguments.length-2;if(Tt===1)q.children=St;else if(1<Tt){for(var Mt=Array(Tt),Ft=0;Ft<Tt;Ft++)Mt[Ft]=arguments[Ft+2];q.children=Mt}return U(O.type,ft,q)},se.createContext=function(O){return O={$$typeof:f,_currentValue:O,_currentValue2:O,_threadCount:0,Provider:null,Consumer:null},O.Provider=O,O.Consumer={$$typeof:c,_context:O},O},se.createElement=function(O,nt,St){var q,ft={},Tt=null;if(nt!=null)for(q in nt.key!==void 0&&(Tt=""+nt.key),nt)G.call(nt,q)&&q!=="key"&&q!=="__self"&&q!=="__source"&&(ft[q]=nt[q]);var Mt=arguments.length-2;if(Mt===1)ft.children=St;else if(1<Mt){for(var Ft=Array(Mt),Vt=0;Vt<Mt;Vt++)Ft[Vt]=arguments[Vt+2];ft.children=Ft}if(O&&O.defaultProps)for(q in Mt=O.defaultProps,Mt)ft[q]===void 0&&(ft[q]=Mt[q]);return U(O,Tt,ft)},se.createRef=function(){return{current:null}},se.forwardRef=function(O){return{$$typeof:d,render:O}},se.isValidElement=H,se.lazy=function(O){return{$$typeof:g,_payload:{_status:-1,_result:O},_init:$}},se.memo=function(O,nt){return{$$typeof:m,type:O,compare:nt===void 0?null:nt}},se.startTransition=function(O){var nt=P.T,St={};P.T=St;try{var q=O(),ft=P.S;ft!==null&&ft(St,q),typeof q=="object"&&q!==null&&typeof q.then=="function"&&q.then(F,Et)}catch(Tt){Et(Tt)}finally{nt!==null&&St.types!==null&&(nt.types=St.types),P.T=nt}},se.unstable_useCacheRefresh=function(){return P.H.useCacheRefresh()},se.use=function(O){return P.H.use(O)},se.useActionState=function(O,nt,St){return P.H.useActionState(O,nt,St)},se.useCallback=function(O,nt){return P.H.useCallback(O,nt)},se.useContext=function(O){return P.H.useContext(O)},se.useDebugValue=function(){},se.useDeferredValue=function(O,nt){return P.H.useDeferredValue(O,nt)},se.useEffect=function(O,nt){return P.H.useEffect(O,nt)},se.useEffectEvent=function(O){return P.H.useEffectEvent(O)},se.useId=function(){return P.H.useId()},se.useImperativeHandle=function(O,nt,St){return P.H.useImperativeHandle(O,nt,St)},se.useInsertionEffect=function(O,nt){return P.H.useInsertionEffect(O,nt)},se.useLayoutEffect=function(O,nt){return P.H.useLayoutEffect(O,nt)},se.useMemo=function(O,nt){return P.H.useMemo(O,nt)},se.useOptimistic=function(O,nt){return P.H.useOptimistic(O,nt)},se.useReducer=function(O,nt,St){return P.H.useReducer(O,nt,St)},se.useRef=function(O){return P.H.useRef(O)},se.useState=function(O){return P.H.useState(O)},se.useSyncExternalStore=function(O,nt,St){return P.H.useSyncExternalStore(O,nt,St)},se.useTransition=function(){return P.H.useTransition()},se.version="19.2.7",se}var d_;function um(){return d_||(d_=1,Sd.exports=sE()),Sd.exports}var pe=um();const rE=ky(pe);var Md={exports:{}},Il={},Ed={exports:{}},bd={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var p_;function oE(){return p_||(p_=1,(function(s){function t(z,Z){var $=z.length;z.push(Z);t:for(;0<$;){var Et=$-1>>>1,At=z[Et];if(0<l(At,Z))z[Et]=Z,z[$]=At,$=Et;else break t}}function n(z){return z.length===0?null:z[0]}function a(z){if(z.length===0)return null;var Z=z[0],$=z.pop();if($!==Z){z[0]=$;t:for(var Et=0,At=z.length,O=At>>>1;Et<O;){var nt=2*(Et+1)-1,St=z[nt],q=nt+1,ft=z[q];if(0>l(St,$))q<At&&0>l(ft,St)?(z[Et]=ft,z[q]=$,Et=q):(z[Et]=St,z[nt]=$,Et=nt);else if(q<At&&0>l(ft,$))z[Et]=ft,z[q]=$,Et=q;else break t}}return Z}function l(z,Z){var $=z.sortIndex-Z.sortIndex;return $!==0?$:z.id-Z.id}if(s.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var c=performance;s.unstable_now=function(){return c.now()}}else{var f=Date,d=f.now();s.unstable_now=function(){return f.now()-d}}var p=[],m=[],g=1,v=null,y=3,x=!1,E=!1,b=!1,M=!1,_=typeof setTimeout=="function"?setTimeout:null,I=typeof clearTimeout=="function"?clearTimeout:null,N=typeof setImmediate<"u"?setImmediate:null;function C(z){for(var Z=n(m);Z!==null;){if(Z.callback===null)a(m);else if(Z.startTime<=z)a(m),Z.sortIndex=Z.expirationTime,t(p,Z);else break;Z=n(m)}}function V(z){if(b=!1,C(z),!E)if(n(p)!==null)E=!0,F||(F=!0,ut());else{var Z=n(m);Z!==null&&ct(V,Z.startTime-z)}}var F=!1,P=-1,G=5,U=-1;function w(){return M?!0:!(s.unstable_now()-U<G)}function H(){if(M=!1,F){var z=s.unstable_now();U=z;var Z=!0;try{t:{E=!1,b&&(b=!1,I(P),P=-1),x=!0;var $=y;try{e:{for(C(z),v=n(p);v!==null&&!(v.expirationTime>z&&w());){var Et=v.callback;if(typeof Et=="function"){v.callback=null,y=v.priorityLevel;var At=Et(v.expirationTime<=z);if(z=s.unstable_now(),typeof At=="function"){v.callback=At,C(z),Z=!0;break e}v===n(p)&&a(p),C(z)}else a(p);v=n(p)}if(v!==null)Z=!0;else{var O=n(m);O!==null&&ct(V,O.startTime-z),Z=!1}}break t}finally{v=null,y=$,x=!1}Z=void 0}}finally{Z?ut():F=!1}}}var ut;if(typeof N=="function")ut=function(){N(H)};else if(typeof MessageChannel<"u"){var ot=new MessageChannel,mt=ot.port2;ot.port1.onmessage=H,ut=function(){mt.postMessage(null)}}else ut=function(){_(H,0)};function ct(z,Z){P=_(function(){z(s.unstable_now())},Z)}s.unstable_IdlePriority=5,s.unstable_ImmediatePriority=1,s.unstable_LowPriority=4,s.unstable_NormalPriority=3,s.unstable_Profiling=null,s.unstable_UserBlockingPriority=2,s.unstable_cancelCallback=function(z){z.callback=null},s.unstable_forceFrameRate=function(z){0>z||125<z?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):G=0<z?Math.floor(1e3/z):5},s.unstable_getCurrentPriorityLevel=function(){return y},s.unstable_next=function(z){switch(y){case 1:case 2:case 3:var Z=3;break;default:Z=y}var $=y;y=Z;try{return z()}finally{y=$}},s.unstable_requestPaint=function(){M=!0},s.unstable_runWithPriority=function(z,Z){switch(z){case 1:case 2:case 3:case 4:case 5:break;default:z=3}var $=y;y=z;try{return Z()}finally{y=$}},s.unstable_scheduleCallback=function(z,Z,$){var Et=s.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?Et+$:Et):$=Et,z){case 1:var At=-1;break;case 2:At=250;break;case 5:At=1073741823;break;case 4:At=1e4;break;default:At=5e3}return At=$+At,z={id:g++,callback:Z,priorityLevel:z,startTime:$,expirationTime:At,sortIndex:-1},$>Et?(z.sortIndex=$,t(m,z),n(p)===null&&z===n(m)&&(b?(I(P),P=-1):b=!0,ct(V,$-Et))):(z.sortIndex=At,t(p,z),E||x||(E=!0,F||(F=!0,ut()))),z},s.unstable_shouldYield=w,s.unstable_wrapCallback=function(z){var Z=y;return function(){var $=y;y=Z;try{return z.apply(this,arguments)}finally{y=$}}}})(bd)),bd}var m_;function lE(){return m_||(m_=1,Ed.exports=oE()),Ed.exports}var Td={exports:{}},In={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var g_;function cE(){if(g_)return In;g_=1;var s=um();function t(p){var m="https://react.dev/errors/"+p;if(1<arguments.length){m+="?args[]="+encodeURIComponent(arguments[1]);for(var g=2;g<arguments.length;g++)m+="&args[]="+encodeURIComponent(arguments[g])}return"Minified React error #"+p+"; visit "+m+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function n(){}var a={d:{f:n,r:function(){throw Error(t(522))},D:n,C:n,L:n,m:n,X:n,S:n,M:n},p:0,findDOMNode:null},l=Symbol.for("react.portal");function c(p,m,g){var v=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:l,key:v==null?null:""+v,children:p,containerInfo:m,implementation:g}}var f=s.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function d(p,m){if(p==="font")return"";if(typeof m=="string")return m==="use-credentials"?m:""}return In.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=a,In.createPortal=function(p,m){var g=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!m||m.nodeType!==1&&m.nodeType!==9&&m.nodeType!==11)throw Error(t(299));return c(p,m,null,g)},In.flushSync=function(p){var m=f.T,g=a.p;try{if(f.T=null,a.p=2,p)return p()}finally{f.T=m,a.p=g,a.d.f()}},In.preconnect=function(p,m){typeof p=="string"&&(m?(m=m.crossOrigin,m=typeof m=="string"?m==="use-credentials"?m:"":void 0):m=null,a.d.C(p,m))},In.prefetchDNS=function(p){typeof p=="string"&&a.d.D(p)},In.preinit=function(p,m){if(typeof p=="string"&&m&&typeof m.as=="string"){var g=m.as,v=d(g,m.crossOrigin),y=typeof m.integrity=="string"?m.integrity:void 0,x=typeof m.fetchPriority=="string"?m.fetchPriority:void 0;g==="style"?a.d.S(p,typeof m.precedence=="string"?m.precedence:void 0,{crossOrigin:v,integrity:y,fetchPriority:x}):g==="script"&&a.d.X(p,{crossOrigin:v,integrity:y,fetchPriority:x,nonce:typeof m.nonce=="string"?m.nonce:void 0})}},In.preinitModule=function(p,m){if(typeof p=="string")if(typeof m=="object"&&m!==null){if(m.as==null||m.as==="script"){var g=d(m.as,m.crossOrigin);a.d.M(p,{crossOrigin:g,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0})}}else m==null&&a.d.M(p)},In.preload=function(p,m){if(typeof p=="string"&&typeof m=="object"&&m!==null&&typeof m.as=="string"){var g=m.as,v=d(g,m.crossOrigin);a.d.L(p,g,{crossOrigin:v,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0,type:typeof m.type=="string"?m.type:void 0,fetchPriority:typeof m.fetchPriority=="string"?m.fetchPriority:void 0,referrerPolicy:typeof m.referrerPolicy=="string"?m.referrerPolicy:void 0,imageSrcSet:typeof m.imageSrcSet=="string"?m.imageSrcSet:void 0,imageSizes:typeof m.imageSizes=="string"?m.imageSizes:void 0,media:typeof m.media=="string"?m.media:void 0})}},In.preloadModule=function(p,m){if(typeof p=="string")if(m){var g=d(m.as,m.crossOrigin);a.d.m(p,{as:typeof m.as=="string"&&m.as!=="script"?m.as:void 0,crossOrigin:g,integrity:typeof m.integrity=="string"?m.integrity:void 0})}else a.d.m(p)},In.requestFormReset=function(p){a.d.r(p)},In.unstable_batchedUpdates=function(p,m){return p(m)},In.useFormState=function(p,m,g){return f.H.useFormState(p,m,g)},In.useFormStatus=function(){return f.H.useHostTransitionStatus()},In.version="19.2.7",In}var v_;function uE(){if(v_)return Td.exports;v_=1;function s(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(s)}catch(t){console.error(t)}}return s(),Td.exports=cE(),Td.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var __;function fE(){if(__)return Il;__=1;var s=lE(),t=um(),n=uE();function a(e){var i="https://react.dev/errors/"+e;if(1<arguments.length){i+="?args[]="+encodeURIComponent(arguments[1]);for(var r=2;r<arguments.length;r++)i+="&args[]="+encodeURIComponent(arguments[r])}return"Minified React error #"+e+"; visit "+i+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function c(e){var i=e,r=e;if(e.alternate)for(;i.return;)i=i.return;else{e=i;do i=e,(i.flags&4098)!==0&&(r=i.return),e=i.return;while(e)}return i.tag===3?r:null}function f(e){if(e.tag===13){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function d(e){if(e.tag===31){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function p(e){if(c(e)!==e)throw Error(a(188))}function m(e){var i=e.alternate;if(!i){if(i=c(e),i===null)throw Error(a(188));return i!==e?null:e}for(var r=e,o=i;;){var u=r.return;if(u===null)break;var h=u.alternate;if(h===null){if(o=u.return,o!==null){r=o;continue}break}if(u.child===h.child){for(h=u.child;h;){if(h===r)return p(u),e;if(h===o)return p(u),i;h=h.sibling}throw Error(a(188))}if(r.return!==o.return)r=u,o=h;else{for(var S=!1,T=u.child;T;){if(T===r){S=!0,r=u,o=h;break}if(T===o){S=!0,o=u,r=h;break}T=T.sibling}if(!S){for(T=h.child;T;){if(T===r){S=!0,r=h,o=u;break}if(T===o){S=!0,o=h,r=u;break}T=T.sibling}if(!S)throw Error(a(189))}}if(r.alternate!==o)throw Error(a(190))}if(r.tag!==3)throw Error(a(188));return r.stateNode.current===r?e:i}function g(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e;for(e=e.child;e!==null;){if(i=g(e),i!==null)return i;e=e.sibling}return null}var v=Object.assign,y=Symbol.for("react.element"),x=Symbol.for("react.transitional.element"),E=Symbol.for("react.portal"),b=Symbol.for("react.fragment"),M=Symbol.for("react.strict_mode"),_=Symbol.for("react.profiler"),I=Symbol.for("react.consumer"),N=Symbol.for("react.context"),C=Symbol.for("react.forward_ref"),V=Symbol.for("react.suspense"),F=Symbol.for("react.suspense_list"),P=Symbol.for("react.memo"),G=Symbol.for("react.lazy"),U=Symbol.for("react.activity"),w=Symbol.for("react.memo_cache_sentinel"),H=Symbol.iterator;function ut(e){return e===null||typeof e!="object"?null:(e=H&&e[H]||e["@@iterator"],typeof e=="function"?e:null)}var ot=Symbol.for("react.client.reference");function mt(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===ot?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case b:return"Fragment";case _:return"Profiler";case M:return"StrictMode";case V:return"Suspense";case F:return"SuspenseList";case U:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case E:return"Portal";case N:return e.displayName||"Context";case I:return(e._context.displayName||"Context")+".Consumer";case C:var i=e.render;return e=e.displayName,e||(e=i.displayName||i.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case P:return i=e.displayName||null,i!==null?i:mt(e.type)||"Memo";case G:i=e._payload,e=e._init;try{return mt(e(i))}catch{}}return null}var ct=Array.isArray,z=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,Z=n.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,$={pending:!1,data:null,method:null,action:null},Et=[],At=-1;function O(e){return{current:e}}function nt(e){0>At||(e.current=Et[At],Et[At]=null,At--)}function St(e,i){At++,Et[At]=e.current,e.current=i}var q=O(null),ft=O(null),Tt=O(null),Mt=O(null);function Ft(e,i){switch(St(Tt,i),St(ft,e),St(q,null),i.nodeType){case 9:case 11:e=(e=i.documentElement)&&(e=e.namespaceURI)?N0(e):0;break;default:if(e=i.tagName,i=i.namespaceURI)i=N0(i),e=L0(i,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}nt(q),St(q,e)}function Vt(){nt(q),nt(ft),nt(Tt)}function re(e){e.memoizedState!==null&&St(Mt,e);var i=q.current,r=L0(i,e.type);i!==r&&(St(ft,e),St(q,r))}function He(e){ft.current===e&&(nt(q),nt(ft)),Mt.current===e&&(nt(Mt),Nl._currentValue=$)}var ve,Je;function k(e){if(ve===void 0)try{throw Error()}catch(r){var i=r.stack.trim().match(/\n( *(at )?)/);ve=i&&i[1]||"",Je=-1<r.stack.indexOf(`
    at`)?" (<anonymous>)":-1<r.stack.indexOf("@")?"@unknown:0:0":""}return`
`+ve+e+Je}var Pn=!1;function me(e,i){if(!e||Pn)return"";Pn=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var o={DetermineComponentFrameRoot:function(){try{if(i){var _t=function(){throw Error()};if(Object.defineProperty(_t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(_t,[])}catch(lt){var it=lt}Reflect.construct(e,[],_t)}else{try{_t.call()}catch(lt){it=lt}e.call(_t.prototype)}}else{try{throw Error()}catch(lt){it=lt}(_t=e())&&typeof _t.catch=="function"&&_t.catch(function(){})}}catch(lt){if(lt&&it&&typeof lt.stack=="string")return[lt.stack,it.stack]}return[null,null]}};o.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var u=Object.getOwnPropertyDescriptor(o.DetermineComponentFrameRoot,"name");u&&u.configurable&&Object.defineProperty(o.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var h=o.DetermineComponentFrameRoot(),S=h[0],T=h[1];if(S&&T){var B=S.split(`
`),et=T.split(`
`);for(u=o=0;o<B.length&&!B[o].includes("DetermineComponentFrameRoot");)o++;for(;u<et.length&&!et[u].includes("DetermineComponentFrameRoot");)u++;if(o===B.length||u===et.length)for(o=B.length-1,u=et.length-1;1<=o&&0<=u&&B[o]!==et[u];)u--;for(;1<=o&&0<=u;o--,u--)if(B[o]!==et[u]){if(o!==1||u!==1)do if(o--,u--,0>u||B[o]!==et[u]){var dt=`
`+B[o].replace(" at new "," at ");return e.displayName&&dt.includes("<anonymous>")&&(dt=dt.replace("<anonymous>",e.displayName)),dt}while(1<=o&&0<=u);break}}}finally{Pn=!1,Error.prepareStackTrace=r}return(r=e?e.displayName||e.name:"")?k(r):""}function Se(e,i){switch(e.tag){case 26:case 27:case 5:return k(e.type);case 16:return k("Lazy");case 13:return e.child!==i&&i!==null?k("Suspense Fallback"):k("Suspense");case 19:return k("SuspenseList");case 0:case 15:return me(e.type,!1);case 11:return me(e.type.render,!1);case 1:return me(e.type,!0);case 31:return k("Activity");default:return""}}function Qt(e){try{var i="",r=null;do i+=Se(e,r),r=e,e=e.return;while(e);return i}catch(o){return`
Error generating stack: `+o.message+`
`+o.stack}}var Ie=Object.prototype.hasOwnProperty,Yt=s.unstable_scheduleCallback,L=s.unstable_cancelCallback,A=s.unstable_shouldYield,at=s.unstable_requestPaint,pt=s.unstable_now,bt=s.unstable_getCurrentPriorityLevel,vt=s.unstable_ImmediatePriority,jt=s.unstable_UserBlockingPriority,Dt=s.unstable_NormalPriority,Bt=s.unstable_LowPriority,Me=s.unstable_IdlePriority,Ct=s.log,Ht=s.unstable_setDisableYieldValue,Zt=null,qt=null;function Ot(e){if(typeof Ct=="function"&&Ht(e),qt&&typeof qt.setStrictMode=="function")try{qt.setStrictMode(Zt,e)}catch{}}var ne=Math.clz32?Math.clz32:Y,oe=Math.log,Ge=Math.LN2;function Y(e){return e>>>=0,e===0?32:31-(oe(e)/Ge|0)|0}var Rt=256,ht=262144,yt=4194304;function wt(e){var i=e&42;if(i!==0)return i;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Ut(e,i,r){var o=e.pendingLanes;if(o===0)return 0;var u=0,h=e.suspendedLanes,S=e.pingedLanes;e=e.warmLanes;var T=o&134217727;return T!==0?(o=T&~h,o!==0?u=wt(o):(S&=T,S!==0?u=wt(S):r||(r=T&~e,r!==0&&(u=wt(r))))):(T=o&~h,T!==0?u=wt(T):S!==0?u=wt(S):r||(r=o&~e,r!==0&&(u=wt(r)))),u===0?0:i!==0&&i!==u&&(i&h)===0&&(h=u&-u,r=i&-i,h>=r||h===32&&(r&4194048)!==0)?i:u}function ie(e,i){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&i)===0}function $e(e,i){switch(e){case 1:case 2:case 4:case 8:case 64:return i+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return i+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function _n(){var e=yt;return yt<<=1,(yt&62914560)===0&&(yt=4194304),e}function we(e){for(var i=[],r=0;31>r;r++)i.push(e);return i}function Rn(e,i){e.pendingLanes|=i,i!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function wi(e,i,r,o,u,h){var S=e.pendingLanes;e.pendingLanes=r,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=r,e.entangledLanes&=r,e.errorRecoveryDisabledLanes&=r,e.shellSuspendCounter=0;var T=e.entanglements,B=e.expirationTimes,et=e.hiddenUpdates;for(r=S&~r;0<r;){var dt=31-ne(r),_t=1<<dt;T[dt]=0,B[dt]=-1;var it=et[dt];if(it!==null)for(et[dt]=null,dt=0;dt<it.length;dt++){var lt=it[dt];lt!==null&&(lt.lane&=-536870913)}r&=~_t}o!==0&&jo(e,o,0),h!==0&&u===0&&e.tag!==0&&(e.suspendedLanes|=h&~(S&~i))}function jo(e,i,r){e.pendingLanes|=i,e.suspendedLanes&=~i;var o=31-ne(i);e.entangledLanes|=i,e.entanglements[o]=e.entanglements[o]|1073741824|r&261930}function qo(e,i){var r=e.entangledLanes|=i;for(e=e.entanglements;r;){var o=31-ne(r),u=1<<o;u&i|e[o]&i&&(e[o]|=i),r&=~u}}function ki(e,i){var r=i&-i;return r=(r&42)!==0?1:Cs(r),(r&(e.suspendedLanes|i))!==0?0:r}function Cs(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function _r(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function Wo(){var e=Z.p;return e!==0?e:(e=window.event,e===void 0?32:n_(e.type))}function Rs(e,i){var r=Z.p;try{return Z.p=e,i()}finally{Z.p=r}}var Di=Math.random().toString(36).slice(2),sn="__reactFiber$"+Di,wn="__reactProps$"+Di,ea="__reactContainer$"+Di,Yo="__reactEvents$"+Di,df="__reactListeners$"+Di,pf="__reactHandles$"+Di,hc="__reactResources$"+Di,ws="__reactMarker$"+Di;function R(e){delete e[sn],delete e[wn],delete e[Yo],delete e[df],delete e[pf]}function Q(e){var i=e[sn];if(i)return i;for(var r=e.parentNode;r;){if(i=r[ea]||r[sn]){if(r=i.alternate,i.child!==null||r!==null&&r.child!==null)for(e=H0(e);e!==null;){if(r=e[sn])return r;e=H0(e)}return i}e=r,r=e.parentNode}return null}function st(e){if(e=e[sn]||e[ea]){var i=e.tag;if(i===5||i===6||i===13||i===31||i===26||i===27||i===3)return e}return null}function rt(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e.stateNode;throw Error(a(33))}function K(e){var i=e[hc];return i||(i=e[hc]={hoistableStyles:new Map,hoistableScripts:new Map}),i}function xt(e){e[ws]=!0}var Nt=new Set,It={};function Pt(e,i){$t(e,i),$t(e+"Capture",i)}function $t(e,i){for(It[e]=i,e=0;e<i.length;e++)Nt.add(i[e])}var ae=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Kt={},Ee={};function De(e){return Ie.call(Ee,e)?!0:Ie.call(Kt,e)?!1:ae.test(e)?Ee[e]=!0:(Kt[e]=!0,!1)}function Qe(e,i,r){if(De(i))if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":e.removeAttribute(i);return;case"boolean":var o=i.toLowerCase().slice(0,5);if(o!=="data-"&&o!=="aria-"){e.removeAttribute(i);return}}e.setAttribute(i,""+r)}}function We(e,i,r){if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(i);return}e.setAttribute(i,""+r)}}function le(e,i,r,o){if(o===null)e.removeAttribute(r);else{switch(typeof o){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(r);return}e.setAttributeNS(i,r,""+o)}}function kt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function hn(e){var i=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(i==="checkbox"||i==="radio")}function Ue(e,i,r){var o=Object.getOwnPropertyDescriptor(e.constructor.prototype,i);if(!e.hasOwnProperty(i)&&typeof o<"u"&&typeof o.get=="function"&&typeof o.set=="function"){var u=o.get,h=o.set;return Object.defineProperty(e,i,{configurable:!0,get:function(){return u.call(this)},set:function(S){r=""+S,h.call(this,S)}}),Object.defineProperty(e,i,{enumerable:o.enumerable}),{getValue:function(){return r},setValue:function(S){r=""+S},stopTracking:function(){e._valueTracker=null,delete e[i]}}}}function Gn(e){if(!e._valueTracker){var i=hn(e)?"checked":"value";e._valueTracker=Ue(e,i,""+e[i])}}function na(e){if(!e)return!1;var i=e._valueTracker;if(!i)return!0;var r=i.getValue(),o="";return e&&(o=hn(e)?e.checked?"true":"false":e.value),e=o,e!==r?(i.setValue(e),!0):!1}function En(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Ds=/[\n"\\]/g;function _e(e){return e.replace(Ds,function(i){return"\\"+i.charCodeAt(0).toString(16)+" "})}function zn(e,i,r,o,u,h,S,T){e.name="",S!=null&&typeof S!="function"&&typeof S!="symbol"&&typeof S!="boolean"?e.type=S:e.removeAttribute("type"),i!=null?S==="number"?(i===0&&e.value===""||e.value!=i)&&(e.value=""+kt(i)):e.value!==""+kt(i)&&(e.value=""+kt(i)):S!=="submit"&&S!=="reset"||e.removeAttribute("value"),i!=null?yn(e,S,kt(i)):r!=null?yn(e,S,kt(r)):o!=null&&e.removeAttribute("value"),u==null&&h!=null&&(e.defaultChecked=!!h),u!=null&&(e.checked=u&&typeof u!="function"&&typeof u!="symbol"),T!=null&&typeof T!="function"&&typeof T!="symbol"&&typeof T!="boolean"?e.name=""+kt(T):e.removeAttribute("name")}function Vn(e,i,r,o,u,h,S,T){if(h!=null&&typeof h!="function"&&typeof h!="symbol"&&typeof h!="boolean"&&(e.type=h),i!=null||r!=null){if(!(h!=="submit"&&h!=="reset"||i!=null)){Gn(e);return}r=r!=null?""+kt(r):"",i=i!=null?""+kt(i):r,T||i===e.value||(e.value=i),e.defaultValue=i}o=o??u,o=typeof o!="function"&&typeof o!="symbol"&&!!o,e.checked=T?e.checked:!!o,e.defaultChecked=!!o,S!=null&&typeof S!="function"&&typeof S!="symbol"&&typeof S!="boolean"&&(e.name=S),Gn(e)}function yn(e,i,r){i==="number"&&En(e.ownerDocument)===e||e.defaultValue===""+r||(e.defaultValue=""+r)}function cn(e,i,r,o){if(e=e.options,i){i={};for(var u=0;u<r.length;u++)i["$"+r[u]]=!0;for(r=0;r<e.length;r++)u=i.hasOwnProperty("$"+e[r].value),e[r].selected!==u&&(e[r].selected=u),u&&o&&(e[r].defaultSelected=!0)}else{for(r=""+kt(r),i=null,u=0;u<e.length;u++){if(e[u].value===r){e[u].selected=!0,o&&(e[u].defaultSelected=!0);return}i!==null||e[u].disabled||(i=e[u])}i!==null&&(i.selected=!0)}}function yr(e,i,r){if(i!=null&&(i=""+kt(i),i!==e.value&&(e.value=i),r==null)){e.defaultValue!==i&&(e.defaultValue=i);return}e.defaultValue=r!=null?""+kt(r):""}function Xi(e,i,r,o){if(i==null){if(o!=null){if(r!=null)throw Error(a(92));if(ct(o)){if(1<o.length)throw Error(a(93));o=o[0]}r=o}r==null&&(r=""),i=r}r=kt(i),e.defaultValue=r,o=e.textContent,o===r&&o!==""&&o!==null&&(e.value=o),Gn(e)}function xr(e,i){if(i){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=i;return}}e.textContent=i}var Jx=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function wm(e,i,r){var o=i.indexOf("--")===0;r==null||typeof r=="boolean"||r===""?o?e.setProperty(i,""):i==="float"?e.cssFloat="":e[i]="":o?e.setProperty(i,r):typeof r!="number"||r===0||Jx.has(i)?i==="float"?e.cssFloat=r:e[i]=(""+r).trim():e[i]=r+"px"}function Dm(e,i,r){if(i!=null&&typeof i!="object")throw Error(a(62));if(e=e.style,r!=null){for(var o in r)!r.hasOwnProperty(o)||i!=null&&i.hasOwnProperty(o)||(o.indexOf("--")===0?e.setProperty(o,""):o==="float"?e.cssFloat="":e[o]="");for(var u in i)o=i[u],i.hasOwnProperty(u)&&r[u]!==o&&wm(e,u,o)}else for(var h in i)i.hasOwnProperty(h)&&wm(e,h,i[h])}function mf(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var $x=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),tS=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function dc(e){return tS.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function ia(){}var gf=null;function vf(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Sr=null,Mr=null;function Um(e){var i=st(e);if(i&&(e=i.stateNode)){var r=e[wn]||null;t:switch(e=i.stateNode,i.type){case"input":if(zn(e,r.value,r.defaultValue,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name),i=r.name,r.type==="radio"&&i!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll('input[name="'+_e(""+i)+'"][type="radio"]'),i=0;i<r.length;i++){var o=r[i];if(o!==e&&o.form===e.form){var u=o[wn]||null;if(!u)throw Error(a(90));zn(o,u.value,u.defaultValue,u.defaultValue,u.checked,u.defaultChecked,u.type,u.name)}}for(i=0;i<r.length;i++)o=r[i],o.form===e.form&&na(o)}break t;case"textarea":yr(e,r.value,r.defaultValue);break t;case"select":i=r.value,i!=null&&cn(e,!!r.multiple,i,!1)}}}var _f=!1;function Nm(e,i,r){if(_f)return e(i,r);_f=!0;try{var o=e(i);return o}finally{if(_f=!1,(Sr!==null||Mr!==null)&&(tu(),Sr&&(i=Sr,e=Mr,Mr=Sr=null,Um(i),e)))for(i=0;i<e.length;i++)Um(e[i])}}function Qo(e,i){var r=e.stateNode;if(r===null)return null;var o=r[wn]||null;if(o===null)return null;r=o[i];t:switch(i){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(o=!o.disabled)||(e=e.type,o=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!o;break t;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(a(231,i,typeof r));return r}var aa=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),yf=!1;if(aa)try{var Zo={};Object.defineProperty(Zo,"passive",{get:function(){yf=!0}}),window.addEventListener("test",Zo,Zo),window.removeEventListener("test",Zo,Zo)}catch{yf=!1}var Ba=null,xf=null,pc=null;function Lm(){if(pc)return pc;var e,i=xf,r=i.length,o,u="value"in Ba?Ba.value:Ba.textContent,h=u.length;for(e=0;e<r&&i[e]===u[e];e++);var S=r-e;for(o=1;o<=S&&i[r-o]===u[h-o];o++);return pc=u.slice(e,1<o?1-o:void 0)}function mc(e){var i=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&i===13&&(e=13)):e=i,e===10&&(e=13),32<=e||e===13?e:0}function gc(){return!0}function Om(){return!1}function Qn(e){function i(r,o,u,h,S){this._reactName=r,this._targetInst=u,this.type=o,this.nativeEvent=h,this.target=S,this.currentTarget=null;for(var T in e)e.hasOwnProperty(T)&&(r=e[T],this[T]=r?r(h):h[T]);return this.isDefaultPrevented=(h.defaultPrevented!=null?h.defaultPrevented:h.returnValue===!1)?gc:Om,this.isPropagationStopped=Om,this}return v(i.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=gc)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=gc)},persist:function(){},isPersistent:gc}),i}var Us={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},vc=Qn(Us),Ko=v({},Us,{view:0,detail:0}),eS=Qn(Ko),Sf,Mf,Jo,_c=v({},Ko,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:bf,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Jo&&(Jo&&e.type==="mousemove"?(Sf=e.screenX-Jo.screenX,Mf=e.screenY-Jo.screenY):Mf=Sf=0,Jo=e),Sf)},movementY:function(e){return"movementY"in e?e.movementY:Mf}}),Pm=Qn(_c),nS=v({},_c,{dataTransfer:0}),iS=Qn(nS),aS=v({},Ko,{relatedTarget:0}),Ef=Qn(aS),sS=v({},Us,{animationName:0,elapsedTime:0,pseudoElement:0}),rS=Qn(sS),oS=v({},Us,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),lS=Qn(oS),cS=v({},Us,{data:0}),zm=Qn(cS),uS={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},fS={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},hS={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function dS(e){var i=this.nativeEvent;return i.getModifierState?i.getModifierState(e):(e=hS[e])?!!i[e]:!1}function bf(){return dS}var pS=v({},Ko,{key:function(e){if(e.key){var i=uS[e.key]||e.key;if(i!=="Unidentified")return i}return e.type==="keypress"?(e=mc(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?fS[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:bf,charCode:function(e){return e.type==="keypress"?mc(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?mc(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),mS=Qn(pS),gS=v({},_c,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Im=Qn(gS),vS=v({},Ko,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:bf}),_S=Qn(vS),yS=v({},Us,{propertyName:0,elapsedTime:0,pseudoElement:0}),xS=Qn(yS),SS=v({},_c,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),MS=Qn(SS),ES=v({},Us,{newState:0,oldState:0}),bS=Qn(ES),TS=[9,13,27,32],Tf=aa&&"CompositionEvent"in window,$o=null;aa&&"documentMode"in document&&($o=document.documentMode);var AS=aa&&"TextEvent"in window&&!$o,Bm=aa&&(!Tf||$o&&8<$o&&11>=$o),Fm=" ",Hm=!1;function Gm(e,i){switch(e){case"keyup":return TS.indexOf(i.keyCode)!==-1;case"keydown":return i.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Vm(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Er=!1;function CS(e,i){switch(e){case"compositionend":return Vm(i);case"keypress":return i.which!==32?null:(Hm=!0,Fm);case"textInput":return e=i.data,e===Fm&&Hm?null:e;default:return null}}function RS(e,i){if(Er)return e==="compositionend"||!Tf&&Gm(e,i)?(e=Lm(),pc=xf=Ba=null,Er=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(i.ctrlKey||i.altKey||i.metaKey)||i.ctrlKey&&i.altKey){if(i.char&&1<i.char.length)return i.char;if(i.which)return String.fromCharCode(i.which)}return null;case"compositionend":return Bm&&i.locale!=="ko"?null:i.data;default:return null}}var wS={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function km(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i==="input"?!!wS[e.type]:i==="textarea"}function Xm(e,i,r,o){Sr?Mr?Mr.push(o):Mr=[o]:Sr=o,i=ou(i,"onChange"),0<i.length&&(r=new vc("onChange","change",null,r,o),e.push({event:r,listeners:i}))}var tl=null,el=null;function DS(e){A0(e,0)}function yc(e){var i=rt(e);if(na(i))return e}function jm(e,i){if(e==="change")return i}var qm=!1;if(aa){var Af;if(aa){var Cf="oninput"in document;if(!Cf){var Wm=document.createElement("div");Wm.setAttribute("oninput","return;"),Cf=typeof Wm.oninput=="function"}Af=Cf}else Af=!1;qm=Af&&(!document.documentMode||9<document.documentMode)}function Ym(){tl&&(tl.detachEvent("onpropertychange",Qm),el=tl=null)}function Qm(e){if(e.propertyName==="value"&&yc(el)){var i=[];Xm(i,el,e,vf(e)),Nm(DS,i)}}function US(e,i,r){e==="focusin"?(Ym(),tl=i,el=r,tl.attachEvent("onpropertychange",Qm)):e==="focusout"&&Ym()}function NS(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return yc(el)}function LS(e,i){if(e==="click")return yc(i)}function OS(e,i){if(e==="input"||e==="change")return yc(i)}function PS(e,i){return e===i&&(e!==0||1/e===1/i)||e!==e&&i!==i}var ri=typeof Object.is=="function"?Object.is:PS;function nl(e,i){if(ri(e,i))return!0;if(typeof e!="object"||e===null||typeof i!="object"||i===null)return!1;var r=Object.keys(e),o=Object.keys(i);if(r.length!==o.length)return!1;for(o=0;o<r.length;o++){var u=r[o];if(!Ie.call(i,u)||!ri(e[u],i[u]))return!1}return!0}function Zm(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Km(e,i){var r=Zm(e);e=0;for(var o;r;){if(r.nodeType===3){if(o=e+r.textContent.length,e<=i&&o>=i)return{node:r,offset:i-e};e=o}t:{for(;r;){if(r.nextSibling){r=r.nextSibling;break t}r=r.parentNode}r=void 0}r=Zm(r)}}function Jm(e,i){return e&&i?e===i?!0:e&&e.nodeType===3?!1:i&&i.nodeType===3?Jm(e,i.parentNode):"contains"in e?e.contains(i):e.compareDocumentPosition?!!(e.compareDocumentPosition(i)&16):!1:!1}function $m(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var i=En(e.document);i instanceof e.HTMLIFrameElement;){try{var r=typeof i.contentWindow.location.href=="string"}catch{r=!1}if(r)e=i.contentWindow;else break;i=En(e.document)}return i}function Rf(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i&&(i==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||i==="textarea"||e.contentEditable==="true")}var zS=aa&&"documentMode"in document&&11>=document.documentMode,br=null,wf=null,il=null,Df=!1;function tg(e,i,r){var o=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;Df||br==null||br!==En(o)||(o=br,"selectionStart"in o&&Rf(o)?o={start:o.selectionStart,end:o.selectionEnd}:(o=(o.ownerDocument&&o.ownerDocument.defaultView||window).getSelection(),o={anchorNode:o.anchorNode,anchorOffset:o.anchorOffset,focusNode:o.focusNode,focusOffset:o.focusOffset}),il&&nl(il,o)||(il=o,o=ou(wf,"onSelect"),0<o.length&&(i=new vc("onSelect","select",null,i,r),e.push({event:i,listeners:o}),i.target=br)))}function Ns(e,i){var r={};return r[e.toLowerCase()]=i.toLowerCase(),r["Webkit"+e]="webkit"+i,r["Moz"+e]="moz"+i,r}var Tr={animationend:Ns("Animation","AnimationEnd"),animationiteration:Ns("Animation","AnimationIteration"),animationstart:Ns("Animation","AnimationStart"),transitionrun:Ns("Transition","TransitionRun"),transitionstart:Ns("Transition","TransitionStart"),transitioncancel:Ns("Transition","TransitionCancel"),transitionend:Ns("Transition","TransitionEnd")},Uf={},eg={};aa&&(eg=document.createElement("div").style,"AnimationEvent"in window||(delete Tr.animationend.animation,delete Tr.animationiteration.animation,delete Tr.animationstart.animation),"TransitionEvent"in window||delete Tr.transitionend.transition);function Ls(e){if(Uf[e])return Uf[e];if(!Tr[e])return e;var i=Tr[e],r;for(r in i)if(i.hasOwnProperty(r)&&r in eg)return Uf[e]=i[r];return e}var ng=Ls("animationend"),ig=Ls("animationiteration"),ag=Ls("animationstart"),IS=Ls("transitionrun"),BS=Ls("transitionstart"),FS=Ls("transitioncancel"),sg=Ls("transitionend"),rg=new Map,Nf="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Nf.push("scrollEnd");function Ui(e,i){rg.set(e,i),Pt(i,[e])}var xc=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var i=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(i))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},yi=[],Ar=0,Lf=0;function Sc(){for(var e=Ar,i=Lf=Ar=0;i<e;){var r=yi[i];yi[i++]=null;var o=yi[i];yi[i++]=null;var u=yi[i];yi[i++]=null;var h=yi[i];if(yi[i++]=null,o!==null&&u!==null){var S=o.pending;S===null?u.next=u:(u.next=S.next,S.next=u),o.pending=u}h!==0&&og(r,u,h)}}function Mc(e,i,r,o){yi[Ar++]=e,yi[Ar++]=i,yi[Ar++]=r,yi[Ar++]=o,Lf|=o,e.lanes|=o,e=e.alternate,e!==null&&(e.lanes|=o)}function Of(e,i,r,o){return Mc(e,i,r,o),Ec(e)}function Os(e,i){return Mc(e,null,null,i),Ec(e)}function og(e,i,r){e.lanes|=r;var o=e.alternate;o!==null&&(o.lanes|=r);for(var u=!1,h=e.return;h!==null;)h.childLanes|=r,o=h.alternate,o!==null&&(o.childLanes|=r),h.tag===22&&(e=h.stateNode,e===null||e._visibility&1||(u=!0)),e=h,h=h.return;return e.tag===3?(h=e.stateNode,u&&i!==null&&(u=31-ne(r),e=h.hiddenUpdates,o=e[u],o===null?e[u]=[i]:o.push(i),i.lane=r|536870912),h):null}function Ec(e){if(50<Tl)throw Tl=0,kh=null,Error(a(185));for(var i=e.return;i!==null;)e=i,i=e.return;return e.tag===3?e.stateNode:null}var Cr={};function HS(e,i,r,o){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=i,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=o,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function oi(e,i,r,o){return new HS(e,i,r,o)}function Pf(e){return e=e.prototype,!(!e||!e.isReactComponent)}function sa(e,i){var r=e.alternate;return r===null?(r=oi(e.tag,i,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=i,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&65011712,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,i=e.dependencies,r.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r.refCleanup=e.refCleanup,r}function lg(e,i){e.flags&=65011714;var r=e.alternate;return r===null?(e.childLanes=0,e.lanes=i,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=r.childLanes,e.lanes=r.lanes,e.child=r.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=r.memoizedProps,e.memoizedState=r.memoizedState,e.updateQueue=r.updateQueue,e.type=r.type,i=r.dependencies,e.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext}),e}function bc(e,i,r,o,u,h){var S=0;if(o=e,typeof e=="function")Pf(e)&&(S=1);else if(typeof e=="string")S=jM(e,r,q.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case U:return e=oi(31,r,i,u),e.elementType=U,e.lanes=h,e;case b:return Ps(r.children,u,h,i);case M:S=8,u|=24;break;case _:return e=oi(12,r,i,u|2),e.elementType=_,e.lanes=h,e;case V:return e=oi(13,r,i,u),e.elementType=V,e.lanes=h,e;case F:return e=oi(19,r,i,u),e.elementType=F,e.lanes=h,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case N:S=10;break t;case I:S=9;break t;case C:S=11;break t;case P:S=14;break t;case G:S=16,o=null;break t}S=29,r=Error(a(130,e===null?"null":typeof e,"")),o=null}return i=oi(S,r,i,u),i.elementType=e,i.type=o,i.lanes=h,i}function Ps(e,i,r,o){return e=oi(7,e,o,i),e.lanes=r,e}function zf(e,i,r){return e=oi(6,e,null,i),e.lanes=r,e}function cg(e){var i=oi(18,null,null,0);return i.stateNode=e,i}function If(e,i,r){return i=oi(4,e.children!==null?e.children:[],e.key,i),i.lanes=r,i.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},i}var ug=new WeakMap;function xi(e,i){if(typeof e=="object"&&e!==null){var r=ug.get(e);return r!==void 0?r:(i={value:e,source:i,stack:Qt(i)},ug.set(e,i),i)}return{value:e,source:i,stack:Qt(i)}}var Rr=[],wr=0,Tc=null,al=0,Si=[],Mi=0,Fa=null,ji=1,qi="";function ra(e,i){Rr[wr++]=al,Rr[wr++]=Tc,Tc=e,al=i}function fg(e,i,r){Si[Mi++]=ji,Si[Mi++]=qi,Si[Mi++]=Fa,Fa=e;var o=ji;e=qi;var u=32-ne(o)-1;o&=~(1<<u),r+=1;var h=32-ne(i)+u;if(30<h){var S=u-u%5;h=(o&(1<<S)-1).toString(32),o>>=S,u-=S,ji=1<<32-ne(i)+u|r<<u|o,qi=h+e}else ji=1<<h|r<<u|o,qi=e}function Bf(e){e.return!==null&&(ra(e,1),fg(e,1,0))}function Ff(e){for(;e===Tc;)Tc=Rr[--wr],Rr[wr]=null,al=Rr[--wr],Rr[wr]=null;for(;e===Fa;)Fa=Si[--Mi],Si[Mi]=null,qi=Si[--Mi],Si[Mi]=null,ji=Si[--Mi],Si[Mi]=null}function hg(e,i){Si[Mi++]=ji,Si[Mi++]=qi,Si[Mi++]=Fa,ji=i.id,qi=i.overflow,Fa=e}var Dn=null,Ze=null,Ce=!1,Ha=null,Ei=!1,Hf=Error(a(519));function Ga(e){var i=Error(a(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw sl(xi(i,e)),Hf}function dg(e){var i=e.stateNode,r=e.type,o=e.memoizedProps;switch(i[sn]=e,i[wn]=o,r){case"dialog":xe("cancel",i),xe("close",i);break;case"iframe":case"object":case"embed":xe("load",i);break;case"video":case"audio":for(r=0;r<Cl.length;r++)xe(Cl[r],i);break;case"source":xe("error",i);break;case"img":case"image":case"link":xe("error",i),xe("load",i);break;case"details":xe("toggle",i);break;case"input":xe("invalid",i),Vn(i,o.value,o.defaultValue,o.checked,o.defaultChecked,o.type,o.name,!0);break;case"select":xe("invalid",i);break;case"textarea":xe("invalid",i),Xi(i,o.value,o.defaultValue,o.children)}r=o.children,typeof r!="string"&&typeof r!="number"&&typeof r!="bigint"||i.textContent===""+r||o.suppressHydrationWarning===!0||D0(i.textContent,r)?(o.popover!=null&&(xe("beforetoggle",i),xe("toggle",i)),o.onScroll!=null&&xe("scroll",i),o.onScrollEnd!=null&&xe("scrollend",i),o.onClick!=null&&(i.onclick=ia),i=!0):i=!1,i||Ga(e,!0)}function pg(e){for(Dn=e.return;Dn;)switch(Dn.tag){case 5:case 31:case 13:Ei=!1;return;case 27:case 3:Ei=!0;return;default:Dn=Dn.return}}function Dr(e){if(e!==Dn)return!1;if(!Ce)return pg(e),Ce=!0,!1;var i=e.tag,r;if((r=i!==3&&i!==27)&&((r=i===5)&&(r=e.type,r=!(r!=="form"&&r!=="button")||ad(e.type,e.memoizedProps)),r=!r),r&&Ze&&Ga(e),pg(e),i===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(a(317));Ze=F0(e)}else if(i===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(a(317));Ze=F0(e)}else i===27?(i=Ze,es(e.type)?(e=cd,cd=null,Ze=e):Ze=i):Ze=Dn?Ti(e.stateNode.nextSibling):null;return!0}function zs(){Ze=Dn=null,Ce=!1}function Gf(){var e=Ha;return e!==null&&($n===null?$n=e:$n.push.apply($n,e),Ha=null),e}function sl(e){Ha===null?Ha=[e]:Ha.push(e)}var Vf=O(null),Is=null,oa=null;function Va(e,i,r){St(Vf,i._currentValue),i._currentValue=r}function la(e){e._currentValue=Vf.current,nt(Vf)}function kf(e,i,r){for(;e!==null;){var o=e.alternate;if((e.childLanes&i)!==i?(e.childLanes|=i,o!==null&&(o.childLanes|=i)):o!==null&&(o.childLanes&i)!==i&&(o.childLanes|=i),e===r)break;e=e.return}}function Xf(e,i,r,o){var u=e.child;for(u!==null&&(u.return=e);u!==null;){var h=u.dependencies;if(h!==null){var S=u.child;h=h.firstContext;t:for(;h!==null;){var T=h;h=u;for(var B=0;B<i.length;B++)if(T.context===i[B]){h.lanes|=r,T=h.alternate,T!==null&&(T.lanes|=r),kf(h.return,r,e),o||(S=null);break t}h=T.next}}else if(u.tag===18){if(S=u.return,S===null)throw Error(a(341));S.lanes|=r,h=S.alternate,h!==null&&(h.lanes|=r),kf(S,r,e),S=null}else S=u.child;if(S!==null)S.return=u;else for(S=u;S!==null;){if(S===e){S=null;break}if(u=S.sibling,u!==null){u.return=S.return,S=u;break}S=S.return}u=S}}function Ur(e,i,r,o){e=null;for(var u=i,h=!1;u!==null;){if(!h){if((u.flags&524288)!==0)h=!0;else if((u.flags&262144)!==0)break}if(u.tag===10){var S=u.alternate;if(S===null)throw Error(a(387));if(S=S.memoizedProps,S!==null){var T=u.type;ri(u.pendingProps.value,S.value)||(e!==null?e.push(T):e=[T])}}else if(u===Mt.current){if(S=u.alternate,S===null)throw Error(a(387));S.memoizedState.memoizedState!==u.memoizedState.memoizedState&&(e!==null?e.push(Nl):e=[Nl])}u=u.return}e!==null&&Xf(i,e,r,o),i.flags|=262144}function Ac(e){for(e=e.firstContext;e!==null;){if(!ri(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Bs(e){Is=e,oa=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Un(e){return mg(Is,e)}function Cc(e,i){return Is===null&&Bs(e),mg(e,i)}function mg(e,i){var r=i._currentValue;if(i={context:i,memoizedValue:r,next:null},oa===null){if(e===null)throw Error(a(308));oa=i,e.dependencies={lanes:0,firstContext:i},e.flags|=524288}else oa=oa.next=i;return r}var GS=typeof AbortController<"u"?AbortController:function(){var e=[],i=this.signal={aborted:!1,addEventListener:function(r,o){e.push(o)}};this.abort=function(){i.aborted=!0,e.forEach(function(r){return r()})}},VS=s.unstable_scheduleCallback,kS=s.unstable_NormalPriority,dn={$$typeof:N,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function jf(){return{controller:new GS,data:new Map,refCount:0}}function rl(e){e.refCount--,e.refCount===0&&VS(kS,function(){e.controller.abort()})}var ol=null,qf=0,Nr=0,Lr=null;function XS(e,i){if(ol===null){var r=ol=[];qf=0,Nr=Qh(),Lr={status:"pending",value:void 0,then:function(o){r.push(o)}}}return qf++,i.then(gg,gg),i}function gg(){if(--qf===0&&ol!==null){Lr!==null&&(Lr.status="fulfilled");var e=ol;ol=null,Nr=0,Lr=null;for(var i=0;i<e.length;i++)(0,e[i])()}}function jS(e,i){var r=[],o={status:"pending",value:null,reason:null,then:function(u){r.push(u)}};return e.then(function(){o.status="fulfilled",o.value=i;for(var u=0;u<r.length;u++)(0,r[u])(i)},function(u){for(o.status="rejected",o.reason=u,u=0;u<r.length;u++)(0,r[u])(void 0)}),o}var vg=z.S;z.S=function(e,i){t0=pt(),typeof i=="object"&&i!==null&&typeof i.then=="function"&&XS(e,i),vg!==null&&vg(e,i)};var Fs=O(null);function Wf(){var e=Fs.current;return e!==null?e:Ye.pooledCache}function Rc(e,i){i===null?St(Fs,Fs.current):St(Fs,i.pool)}function _g(){var e=Wf();return e===null?null:{parent:dn._currentValue,pool:e}}var Or=Error(a(460)),Yf=Error(a(474)),wc=Error(a(542)),Dc={then:function(){}};function yg(e){return e=e.status,e==="fulfilled"||e==="rejected"}function xg(e,i,r){switch(r=e[r],r===void 0?e.push(i):r!==i&&(i.then(ia,ia),i=r),i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Mg(e),e;default:if(typeof i.status=="string")i.then(ia,ia);else{if(e=Ye,e!==null&&100<e.shellSuspendCounter)throw Error(a(482));e=i,e.status="pending",e.then(function(o){if(i.status==="pending"){var u=i;u.status="fulfilled",u.value=o}},function(o){if(i.status==="pending"){var u=i;u.status="rejected",u.reason=o}})}switch(i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Mg(e),e}throw Gs=i,Or}}function Hs(e){try{var i=e._init;return i(e._payload)}catch(r){throw r!==null&&typeof r=="object"&&typeof r.then=="function"?(Gs=r,Or):r}}var Gs=null;function Sg(){if(Gs===null)throw Error(a(459));var e=Gs;return Gs=null,e}function Mg(e){if(e===Or||e===wc)throw Error(a(483))}var Pr=null,ll=0;function Uc(e){var i=ll;return ll+=1,Pr===null&&(Pr=[]),xg(Pr,e,i)}function cl(e,i){i=i.props.ref,e.ref=i!==void 0?i:null}function Nc(e,i){throw i.$$typeof===y?Error(a(525)):(e=Object.prototype.toString.call(i),Error(a(31,e==="[object Object]"?"object with keys {"+Object.keys(i).join(", ")+"}":e)))}function Eg(e){function i(J,X){if(e){var tt=J.deletions;tt===null?(J.deletions=[X],J.flags|=16):tt.push(X)}}function r(J,X){if(!e)return null;for(;X!==null;)i(J,X),X=X.sibling;return null}function o(J){for(var X=new Map;J!==null;)J.key!==null?X.set(J.key,J):X.set(J.index,J),J=J.sibling;return X}function u(J,X){return J=sa(J,X),J.index=0,J.sibling=null,J}function h(J,X,tt){return J.index=tt,e?(tt=J.alternate,tt!==null?(tt=tt.index,tt<X?(J.flags|=67108866,X):tt):(J.flags|=67108866,X)):(J.flags|=1048576,X)}function S(J){return e&&J.alternate===null&&(J.flags|=67108866),J}function T(J,X,tt,gt){return X===null||X.tag!==6?(X=zf(tt,J.mode,gt),X.return=J,X):(X=u(X,tt),X.return=J,X)}function B(J,X,tt,gt){var Jt=tt.type;return Jt===b?dt(J,X,tt.props.children,gt,tt.key):X!==null&&(X.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Hs(Jt)===X.type)?(X=u(X,tt.props),cl(X,tt),X.return=J,X):(X=bc(tt.type,tt.key,tt.props,null,J.mode,gt),cl(X,tt),X.return=J,X)}function et(J,X,tt,gt){return X===null||X.tag!==4||X.stateNode.containerInfo!==tt.containerInfo||X.stateNode.implementation!==tt.implementation?(X=If(tt,J.mode,gt),X.return=J,X):(X=u(X,tt.children||[]),X.return=J,X)}function dt(J,X,tt,gt,Jt){return X===null||X.tag!==7?(X=Ps(tt,J.mode,gt,Jt),X.return=J,X):(X=u(X,tt),X.return=J,X)}function _t(J,X,tt){if(typeof X=="string"&&X!==""||typeof X=="number"||typeof X=="bigint")return X=zf(""+X,J.mode,tt),X.return=J,X;if(typeof X=="object"&&X!==null){switch(X.$$typeof){case x:return tt=bc(X.type,X.key,X.props,null,J.mode,tt),cl(tt,X),tt.return=J,tt;case E:return X=If(X,J.mode,tt),X.return=J,X;case G:return X=Hs(X),_t(J,X,tt)}if(ct(X)||ut(X))return X=Ps(X,J.mode,tt,null),X.return=J,X;if(typeof X.then=="function")return _t(J,Uc(X),tt);if(X.$$typeof===N)return _t(J,Cc(J,X),tt);Nc(J,X)}return null}function it(J,X,tt,gt){var Jt=X!==null?X.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return Jt!==null?null:T(J,X,""+tt,gt);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case x:return tt.key===Jt?B(J,X,tt,gt):null;case E:return tt.key===Jt?et(J,X,tt,gt):null;case G:return tt=Hs(tt),it(J,X,tt,gt)}if(ct(tt)||ut(tt))return Jt!==null?null:dt(J,X,tt,gt,null);if(typeof tt.then=="function")return it(J,X,Uc(tt),gt);if(tt.$$typeof===N)return it(J,X,Cc(J,tt),gt);Nc(J,tt)}return null}function lt(J,X,tt,gt,Jt){if(typeof gt=="string"&&gt!==""||typeof gt=="number"||typeof gt=="bigint")return J=J.get(tt)||null,T(X,J,""+gt,Jt);if(typeof gt=="object"&&gt!==null){switch(gt.$$typeof){case x:return J=J.get(gt.key===null?tt:gt.key)||null,B(X,J,gt,Jt);case E:return J=J.get(gt.key===null?tt:gt.key)||null,et(X,J,gt,Jt);case G:return gt=Hs(gt),lt(J,X,tt,gt,Jt)}if(ct(gt)||ut(gt))return J=J.get(tt)||null,dt(X,J,gt,Jt,null);if(typeof gt.then=="function")return lt(J,X,tt,Uc(gt),Jt);if(gt.$$typeof===N)return lt(J,X,tt,Cc(X,gt),Jt);Nc(X,gt)}return null}function Gt(J,X,tt,gt){for(var Jt=null,Ne=null,Xt=X,ue=X=0,Te=null;Xt!==null&&ue<tt.length;ue++){Xt.index>ue?(Te=Xt,Xt=null):Te=Xt.sibling;var Le=it(J,Xt,tt[ue],gt);if(Le===null){Xt===null&&(Xt=Te);break}e&&Xt&&Le.alternate===null&&i(J,Xt),X=h(Le,X,ue),Ne===null?Jt=Le:Ne.sibling=Le,Ne=Le,Xt=Te}if(ue===tt.length)return r(J,Xt),Ce&&ra(J,ue),Jt;if(Xt===null){for(;ue<tt.length;ue++)Xt=_t(J,tt[ue],gt),Xt!==null&&(X=h(Xt,X,ue),Ne===null?Jt=Xt:Ne.sibling=Xt,Ne=Xt);return Ce&&ra(J,ue),Jt}for(Xt=o(Xt);ue<tt.length;ue++)Te=lt(Xt,J,ue,tt[ue],gt),Te!==null&&(e&&Te.alternate!==null&&Xt.delete(Te.key===null?ue:Te.key),X=h(Te,X,ue),Ne===null?Jt=Te:Ne.sibling=Te,Ne=Te);return e&&Xt.forEach(function(rs){return i(J,rs)}),Ce&&ra(J,ue),Jt}function ee(J,X,tt,gt){if(tt==null)throw Error(a(151));for(var Jt=null,Ne=null,Xt=X,ue=X=0,Te=null,Le=tt.next();Xt!==null&&!Le.done;ue++,Le=tt.next()){Xt.index>ue?(Te=Xt,Xt=null):Te=Xt.sibling;var rs=it(J,Xt,Le.value,gt);if(rs===null){Xt===null&&(Xt=Te);break}e&&Xt&&rs.alternate===null&&i(J,Xt),X=h(rs,X,ue),Ne===null?Jt=rs:Ne.sibling=rs,Ne=rs,Xt=Te}if(Le.done)return r(J,Xt),Ce&&ra(J,ue),Jt;if(Xt===null){for(;!Le.done;ue++,Le=tt.next())Le=_t(J,Le.value,gt),Le!==null&&(X=h(Le,X,ue),Ne===null?Jt=Le:Ne.sibling=Le,Ne=Le);return Ce&&ra(J,ue),Jt}for(Xt=o(Xt);!Le.done;ue++,Le=tt.next())Le=lt(Xt,J,ue,Le.value,gt),Le!==null&&(e&&Le.alternate!==null&&Xt.delete(Le.key===null?ue:Le.key),X=h(Le,X,ue),Ne===null?Jt=Le:Ne.sibling=Le,Ne=Le);return e&&Xt.forEach(function(nE){return i(J,nE)}),Ce&&ra(J,ue),Jt}function Xe(J,X,tt,gt){if(typeof tt=="object"&&tt!==null&&tt.type===b&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case x:t:{for(var Jt=tt.key;X!==null;){if(X.key===Jt){if(Jt=tt.type,Jt===b){if(X.tag===7){r(J,X.sibling),gt=u(X,tt.props.children),gt.return=J,J=gt;break t}}else if(X.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Hs(Jt)===X.type){r(J,X.sibling),gt=u(X,tt.props),cl(gt,tt),gt.return=J,J=gt;break t}r(J,X);break}else i(J,X);X=X.sibling}tt.type===b?(gt=Ps(tt.props.children,J.mode,gt,tt.key),gt.return=J,J=gt):(gt=bc(tt.type,tt.key,tt.props,null,J.mode,gt),cl(gt,tt),gt.return=J,J=gt)}return S(J);case E:t:{for(Jt=tt.key;X!==null;){if(X.key===Jt)if(X.tag===4&&X.stateNode.containerInfo===tt.containerInfo&&X.stateNode.implementation===tt.implementation){r(J,X.sibling),gt=u(X,tt.children||[]),gt.return=J,J=gt;break t}else{r(J,X);break}else i(J,X);X=X.sibling}gt=If(tt,J.mode,gt),gt.return=J,J=gt}return S(J);case G:return tt=Hs(tt),Xe(J,X,tt,gt)}if(ct(tt))return Gt(J,X,tt,gt);if(ut(tt)){if(Jt=ut(tt),typeof Jt!="function")throw Error(a(150));return tt=Jt.call(tt),ee(J,X,tt,gt)}if(typeof tt.then=="function")return Xe(J,X,Uc(tt),gt);if(tt.$$typeof===N)return Xe(J,X,Cc(J,tt),gt);Nc(J,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,X!==null&&X.tag===6?(r(J,X.sibling),gt=u(X,tt),gt.return=J,J=gt):(r(J,X),gt=zf(tt,J.mode,gt),gt.return=J,J=gt),S(J)):r(J,X)}return function(J,X,tt,gt){try{ll=0;var Jt=Xe(J,X,tt,gt);return Pr=null,Jt}catch(Xt){if(Xt===Or||Xt===wc)throw Xt;var Ne=oi(29,Xt,null,J.mode);return Ne.lanes=gt,Ne.return=J,Ne}finally{}}}var Vs=Eg(!0),bg=Eg(!1),ka=!1;function Qf(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Zf(e,i){e=e.updateQueue,i.updateQueue===e&&(i.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Xa(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function ja(e,i,r){var o=e.updateQueue;if(o===null)return null;if(o=o.shared,(Pe&2)!==0){var u=o.pending;return u===null?i.next=i:(i.next=u.next,u.next=i),o.pending=i,i=Ec(e),og(e,null,r),i}return Mc(e,o,i,r),Ec(e)}function ul(e,i,r){if(i=i.updateQueue,i!==null&&(i=i.shared,(r&4194048)!==0)){var o=i.lanes;o&=e.pendingLanes,r|=o,i.lanes=r,qo(e,r)}}function Kf(e,i){var r=e.updateQueue,o=e.alternate;if(o!==null&&(o=o.updateQueue,r===o)){var u=null,h=null;if(r=r.firstBaseUpdate,r!==null){do{var S={lane:r.lane,tag:r.tag,payload:r.payload,callback:null,next:null};h===null?u=h=S:h=h.next=S,r=r.next}while(r!==null);h===null?u=h=i:h=h.next=i}else u=h=i;r={baseState:o.baseState,firstBaseUpdate:u,lastBaseUpdate:h,shared:o.shared,callbacks:o.callbacks},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=i:e.next=i,r.lastBaseUpdate=i}var Jf=!1;function fl(){if(Jf){var e=Lr;if(e!==null)throw e}}function hl(e,i,r,o){Jf=!1;var u=e.updateQueue;ka=!1;var h=u.firstBaseUpdate,S=u.lastBaseUpdate,T=u.shared.pending;if(T!==null){u.shared.pending=null;var B=T,et=B.next;B.next=null,S===null?h=et:S.next=et,S=B;var dt=e.alternate;dt!==null&&(dt=dt.updateQueue,T=dt.lastBaseUpdate,T!==S&&(T===null?dt.firstBaseUpdate=et:T.next=et,dt.lastBaseUpdate=B))}if(h!==null){var _t=u.baseState;S=0,dt=et=B=null,T=h;do{var it=T.lane&-536870913,lt=it!==T.lane;if(lt?(be&it)===it:(o&it)===it){it!==0&&it===Nr&&(Jf=!0),dt!==null&&(dt=dt.next={lane:0,tag:T.tag,payload:T.payload,callback:null,next:null});t:{var Gt=e,ee=T;it=i;var Xe=r;switch(ee.tag){case 1:if(Gt=ee.payload,typeof Gt=="function"){_t=Gt.call(Xe,_t,it);break t}_t=Gt;break t;case 3:Gt.flags=Gt.flags&-65537|128;case 0:if(Gt=ee.payload,it=typeof Gt=="function"?Gt.call(Xe,_t,it):Gt,it==null)break t;_t=v({},_t,it);break t;case 2:ka=!0}}it=T.callback,it!==null&&(e.flags|=64,lt&&(e.flags|=8192),lt=u.callbacks,lt===null?u.callbacks=[it]:lt.push(it))}else lt={lane:it,tag:T.tag,payload:T.payload,callback:T.callback,next:null},dt===null?(et=dt=lt,B=_t):dt=dt.next=lt,S|=it;if(T=T.next,T===null){if(T=u.shared.pending,T===null)break;lt=T,T=lt.next,lt.next=null,u.lastBaseUpdate=lt,u.shared.pending=null}}while(!0);dt===null&&(B=_t),u.baseState=B,u.firstBaseUpdate=et,u.lastBaseUpdate=dt,h===null&&(u.shared.lanes=0),Za|=S,e.lanes=S,e.memoizedState=_t}}function Tg(e,i){if(typeof e!="function")throw Error(a(191,e));e.call(i)}function Ag(e,i){var r=e.callbacks;if(r!==null)for(e.callbacks=null,e=0;e<r.length;e++)Tg(r[e],i)}var zr=O(null),Lc=O(0);function Cg(e,i){e=va,St(Lc,e),St(zr,i),va=e|i.baseLanes}function $f(){St(Lc,va),St(zr,zr.current)}function th(){va=Lc.current,nt(zr),nt(Lc)}var li=O(null),bi=null;function qa(e){var i=e.alternate;St(un,un.current&1),St(li,e),bi===null&&(i===null||zr.current!==null||i.memoizedState!==null)&&(bi=e)}function eh(e){St(un,un.current),St(li,e),bi===null&&(bi=e)}function Rg(e){e.tag===22?(St(un,un.current),St(li,e),bi===null&&(bi=e)):Wa()}function Wa(){St(un,un.current),St(li,li.current)}function ci(e){nt(li),bi===e&&(bi=null),nt(un)}var un=O(0);function Oc(e){for(var i=e;i!==null;){if(i.tag===13){var r=i.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||od(r)||ld(r)))return i}else if(i.tag===19&&(i.memoizedProps.revealOrder==="forwards"||i.memoizedProps.revealOrder==="backwards"||i.memoizedProps.revealOrder==="unstable_legacy-backwards"||i.memoizedProps.revealOrder==="together")){if((i.flags&128)!==0)return i}else if(i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return null;i=i.return}i.sibling.return=i.return,i=i.sibling}return null}var ca=0,ce=null,Ve=null,pn=null,Pc=!1,Ir=!1,ks=!1,zc=0,dl=0,Br=null,qS=0;function rn(){throw Error(a(321))}function nh(e,i){if(i===null)return!1;for(var r=0;r<i.length&&r<e.length;r++)if(!ri(e[r],i[r]))return!1;return!0}function ih(e,i,r,o,u,h){return ca=h,ce=i,i.memoizedState=null,i.updateQueue=null,i.lanes=0,z.H=e===null||e.memoizedState===null?fv:_h,ks=!1,h=r(o,u),ks=!1,Ir&&(h=Dg(i,r,o,u)),wg(e),h}function wg(e){z.H=gl;var i=Ve!==null&&Ve.next!==null;if(ca=0,pn=Ve=ce=null,Pc=!1,dl=0,Br=null,i)throw Error(a(300));e===null||mn||(e=e.dependencies,e!==null&&Ac(e)&&(mn=!0))}function Dg(e,i,r,o){ce=e;var u=0;do{if(Ir&&(Br=null),dl=0,Ir=!1,25<=u)throw Error(a(301));if(u+=1,pn=Ve=null,e.updateQueue!=null){var h=e.updateQueue;h.lastEffect=null,h.events=null,h.stores=null,h.memoCache!=null&&(h.memoCache.index=0)}z.H=hv,h=i(r,o)}while(Ir);return h}function WS(){var e=z.H,i=e.useState()[0];return i=typeof i.then=="function"?pl(i):i,e=e.useState()[0],(Ve!==null?Ve.memoizedState:null)!==e&&(ce.flags|=1024),i}function ah(){var e=zc!==0;return zc=0,e}function sh(e,i,r){i.updateQueue=e.updateQueue,i.flags&=-2053,e.lanes&=~r}function rh(e){if(Pc){for(e=e.memoizedState;e!==null;){var i=e.queue;i!==null&&(i.pending=null),e=e.next}Pc=!1}ca=0,pn=Ve=ce=null,Ir=!1,dl=zc=0,Br=null}function kn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return pn===null?ce.memoizedState=pn=e:pn=pn.next=e,pn}function fn(){if(Ve===null){var e=ce.alternate;e=e!==null?e.memoizedState:null}else e=Ve.next;var i=pn===null?ce.memoizedState:pn.next;if(i!==null)pn=i,Ve=e;else{if(e===null)throw ce.alternate===null?Error(a(467)):Error(a(310));Ve=e,e={memoizedState:Ve.memoizedState,baseState:Ve.baseState,baseQueue:Ve.baseQueue,queue:Ve.queue,next:null},pn===null?ce.memoizedState=pn=e:pn=pn.next=e}return pn}function Ic(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function pl(e){var i=dl;return dl+=1,Br===null&&(Br=[]),e=xg(Br,e,i),i=ce,(pn===null?i.memoizedState:pn.next)===null&&(i=i.alternate,z.H=i===null||i.memoizedState===null?fv:_h),e}function Bc(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return pl(e);if(e.$$typeof===N)return Un(e)}throw Error(a(438,String(e)))}function oh(e){var i=null,r=ce.updateQueue;if(r!==null&&(i=r.memoCache),i==null){var o=ce.alternate;o!==null&&(o=o.updateQueue,o!==null&&(o=o.memoCache,o!=null&&(i={data:o.data.map(function(u){return u.slice()}),index:0})))}if(i==null&&(i={data:[],index:0}),r===null&&(r=Ic(),ce.updateQueue=r),r.memoCache=i,r=i.data[i.index],r===void 0)for(r=i.data[i.index]=Array(e),o=0;o<e;o++)r[o]=w;return i.index++,r}function ua(e,i){return typeof i=="function"?i(e):i}function Fc(e){var i=fn();return lh(i,Ve,e)}function lh(e,i,r){var o=e.queue;if(o===null)throw Error(a(311));o.lastRenderedReducer=r;var u=e.baseQueue,h=o.pending;if(h!==null){if(u!==null){var S=u.next;u.next=h.next,h.next=S}i.baseQueue=u=h,o.pending=null}if(h=e.baseState,u===null)e.memoizedState=h;else{i=u.next;var T=S=null,B=null,et=i,dt=!1;do{var _t=et.lane&-536870913;if(_t!==et.lane?(be&_t)===_t:(ca&_t)===_t){var it=et.revertLane;if(it===0)B!==null&&(B=B.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),_t===Nr&&(dt=!0);else if((ca&it)===it){et=et.next,it===Nr&&(dt=!0);continue}else _t={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(T=B=_t,S=h):B=B.next=_t,ce.lanes|=it,Za|=it;_t=et.action,ks&&r(h,_t),h=et.hasEagerState?et.eagerState:r(h,_t)}else it={lane:_t,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(T=B=it,S=h):B=B.next=it,ce.lanes|=_t,Za|=_t;et=et.next}while(et!==null&&et!==i);if(B===null?S=h:B.next=T,!ri(h,e.memoizedState)&&(mn=!0,dt&&(r=Lr,r!==null)))throw r;e.memoizedState=h,e.baseState=S,e.baseQueue=B,o.lastRenderedState=h}return u===null&&(o.lanes=0),[e.memoizedState,o.dispatch]}function ch(e){var i=fn(),r=i.queue;if(r===null)throw Error(a(311));r.lastRenderedReducer=e;var o=r.dispatch,u=r.pending,h=i.memoizedState;if(u!==null){r.pending=null;var S=u=u.next;do h=e(h,S.action),S=S.next;while(S!==u);ri(h,i.memoizedState)||(mn=!0),i.memoizedState=h,i.baseQueue===null&&(i.baseState=h),r.lastRenderedState=h}return[h,o]}function Ug(e,i,r){var o=ce,u=fn(),h=Ce;if(h){if(r===void 0)throw Error(a(407));r=r()}else r=i();var S=!ri((Ve||u).memoizedState,r);if(S&&(u.memoizedState=r,mn=!0),u=u.queue,hh(Og.bind(null,o,u,e),[e]),u.getSnapshot!==i||S||pn!==null&&pn.memoizedState.tag&1){if(o.flags|=2048,Fr(9,{destroy:void 0},Lg.bind(null,o,u,r,i),null),Ye===null)throw Error(a(349));h||(ca&127)!==0||Ng(o,i,r)}return r}function Ng(e,i,r){e.flags|=16384,e={getSnapshot:i,value:r},i=ce.updateQueue,i===null?(i=Ic(),ce.updateQueue=i,i.stores=[e]):(r=i.stores,r===null?i.stores=[e]:r.push(e))}function Lg(e,i,r,o){i.value=r,i.getSnapshot=o,Pg(i)&&zg(e)}function Og(e,i,r){return r(function(){Pg(i)&&zg(e)})}function Pg(e){var i=e.getSnapshot;e=e.value;try{var r=i();return!ri(e,r)}catch{return!0}}function zg(e){var i=Os(e,2);i!==null&&ti(i,e,2)}function uh(e){var i=kn();if(typeof e=="function"){var r=e;if(e=r(),ks){Ot(!0);try{r()}finally{Ot(!1)}}}return i.memoizedState=i.baseState=e,i.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:ua,lastRenderedState:e},i}function Ig(e,i,r,o){return e.baseState=r,lh(e,Ve,typeof o=="function"?o:ua)}function YS(e,i,r,o,u){if(Vc(e))throw Error(a(485));if(e=i.action,e!==null){var h={payload:u,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(S){h.listeners.push(S)}};z.T!==null?r(!0):h.isTransition=!1,o(h),r=i.pending,r===null?(h.next=i.pending=h,Bg(i,h)):(h.next=r.next,i.pending=r.next=h)}}function Bg(e,i){var r=i.action,o=i.payload,u=e.state;if(i.isTransition){var h=z.T,S={};z.T=S;try{var T=r(u,o),B=z.S;B!==null&&B(S,T),Fg(e,i,T)}catch(et){fh(e,i,et)}finally{h!==null&&S.types!==null&&(h.types=S.types),z.T=h}}else try{h=r(u,o),Fg(e,i,h)}catch(et){fh(e,i,et)}}function Fg(e,i,r){r!==null&&typeof r=="object"&&typeof r.then=="function"?r.then(function(o){Hg(e,i,o)},function(o){return fh(e,i,o)}):Hg(e,i,r)}function Hg(e,i,r){i.status="fulfilled",i.value=r,Gg(i),e.state=r,i=e.pending,i!==null&&(r=i.next,r===i?e.pending=null:(r=r.next,i.next=r,Bg(e,r)))}function fh(e,i,r){var o=e.pending;if(e.pending=null,o!==null){o=o.next;do i.status="rejected",i.reason=r,Gg(i),i=i.next;while(i!==o)}e.action=null}function Gg(e){e=e.listeners;for(var i=0;i<e.length;i++)(0,e[i])()}function Vg(e,i){return i}function kg(e,i){if(Ce){var r=Ye.formState;if(r!==null){t:{var o=ce;if(Ce){if(Ze){e:{for(var u=Ze,h=Ei;u.nodeType!==8;){if(!h){u=null;break e}if(u=Ti(u.nextSibling),u===null){u=null;break e}}h=u.data,u=h==="F!"||h==="F"?u:null}if(u){Ze=Ti(u.nextSibling),o=u.data==="F!";break t}}Ga(o)}o=!1}o&&(i=r[0])}}return r=kn(),r.memoizedState=r.baseState=i,o={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Vg,lastRenderedState:i},r.queue=o,r=lv.bind(null,ce,o),o.dispatch=r,o=uh(!1),h=vh.bind(null,ce,!1,o.queue),o=kn(),u={state:i,dispatch:null,action:e,pending:null},o.queue=u,r=YS.bind(null,ce,u,h,r),u.dispatch=r,o.memoizedState=e,[i,r,!1]}function Xg(e){var i=fn();return jg(i,Ve,e)}function jg(e,i,r){if(i=lh(e,i,Vg)[0],e=Fc(ua)[0],typeof i=="object"&&i!==null&&typeof i.then=="function")try{var o=pl(i)}catch(S){throw S===Or?wc:S}else o=i;i=fn();var u=i.queue,h=u.dispatch;return r!==i.memoizedState&&(ce.flags|=2048,Fr(9,{destroy:void 0},QS.bind(null,u,r),null)),[o,h,e]}function QS(e,i){e.action=i}function qg(e){var i=fn(),r=Ve;if(r!==null)return jg(i,r,e);fn(),i=i.memoizedState,r=fn();var o=r.queue.dispatch;return r.memoizedState=e,[i,o,!1]}function Fr(e,i,r,o){return e={tag:e,create:r,deps:o,inst:i,next:null},i=ce.updateQueue,i===null&&(i=Ic(),ce.updateQueue=i),r=i.lastEffect,r===null?i.lastEffect=e.next=e:(o=r.next,r.next=e,e.next=o,i.lastEffect=e),e}function Wg(){return fn().memoizedState}function Hc(e,i,r,o){var u=kn();ce.flags|=e,u.memoizedState=Fr(1|i,{destroy:void 0},r,o===void 0?null:o)}function Gc(e,i,r,o){var u=fn();o=o===void 0?null:o;var h=u.memoizedState.inst;Ve!==null&&o!==null&&nh(o,Ve.memoizedState.deps)?u.memoizedState=Fr(i,h,r,o):(ce.flags|=e,u.memoizedState=Fr(1|i,h,r,o))}function Yg(e,i){Hc(8390656,8,e,i)}function hh(e,i){Gc(2048,8,e,i)}function ZS(e){ce.flags|=4;var i=ce.updateQueue;if(i===null)i=Ic(),ce.updateQueue=i,i.events=[e];else{var r=i.events;r===null?i.events=[e]:r.push(e)}}function Qg(e){var i=fn().memoizedState;return ZS({ref:i,nextImpl:e}),function(){if((Pe&2)!==0)throw Error(a(440));return i.impl.apply(void 0,arguments)}}function Zg(e,i){return Gc(4,2,e,i)}function Kg(e,i){return Gc(4,4,e,i)}function Jg(e,i){if(typeof i=="function"){e=e();var r=i(e);return function(){typeof r=="function"?r():i(null)}}if(i!=null)return e=e(),i.current=e,function(){i.current=null}}function $g(e,i,r){r=r!=null?r.concat([e]):null,Gc(4,4,Jg.bind(null,i,e),r)}function dh(){}function tv(e,i){var r=fn();i=i===void 0?null:i;var o=r.memoizedState;return i!==null&&nh(i,o[1])?o[0]:(r.memoizedState=[e,i],e)}function ev(e,i){var r=fn();i=i===void 0?null:i;var o=r.memoizedState;if(i!==null&&nh(i,o[1]))return o[0];if(o=e(),ks){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[o,i],o}function ph(e,i,r){return r===void 0||(ca&1073741824)!==0&&(be&261930)===0?e.memoizedState=i:(e.memoizedState=r,e=n0(),ce.lanes|=e,Za|=e,r)}function nv(e,i,r,o){return ri(r,i)?r:zr.current!==null?(e=ph(e,r,o),ri(e,i)||(mn=!0),e):(ca&42)===0||(ca&1073741824)!==0&&(be&261930)===0?(mn=!0,e.memoizedState=r):(e=n0(),ce.lanes|=e,Za|=e,i)}function iv(e,i,r,o,u){var h=Z.p;Z.p=h!==0&&8>h?h:8;var S=z.T,T={};z.T=T,vh(e,!1,i,r);try{var B=u(),et=z.S;if(et!==null&&et(T,B),B!==null&&typeof B=="object"&&typeof B.then=="function"){var dt=jS(B,o);ml(e,i,dt,hi(e))}else ml(e,i,o,hi(e))}catch(_t){ml(e,i,{then:function(){},status:"rejected",reason:_t},hi())}finally{Z.p=h,S!==null&&T.types!==null&&(S.types=T.types),z.T=S}}function KS(){}function mh(e,i,r,o){if(e.tag!==5)throw Error(a(476));var u=av(e).queue;iv(e,u,i,$,r===null?KS:function(){return sv(e),r(o)})}function av(e){var i=e.memoizedState;if(i!==null)return i;i={memoizedState:$,baseState:$,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:ua,lastRenderedState:$},next:null};var r={};return i.next={memoizedState:r,baseState:r,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:ua,lastRenderedState:r},next:null},e.memoizedState=i,e=e.alternate,e!==null&&(e.memoizedState=i),i}function sv(e){var i=av(e);i.next===null&&(i=e.alternate.memoizedState),ml(e,i.next.queue,{},hi())}function gh(){return Un(Nl)}function rv(){return fn().memoizedState}function ov(){return fn().memoizedState}function JS(e){for(var i=e.return;i!==null;){switch(i.tag){case 24:case 3:var r=hi();e=Xa(r);var o=ja(i,e,r);o!==null&&(ti(o,i,r),ul(o,i,r)),i={cache:jf()},e.payload=i;return}i=i.return}}function $S(e,i,r){var o=hi();r={lane:o,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},Vc(e)?cv(i,r):(r=Of(e,i,r,o),r!==null&&(ti(r,e,o),uv(r,i,o)))}function lv(e,i,r){var o=hi();ml(e,i,r,o)}function ml(e,i,r,o){var u={lane:o,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null};if(Vc(e))cv(i,u);else{var h=e.alternate;if(e.lanes===0&&(h===null||h.lanes===0)&&(h=i.lastRenderedReducer,h!==null))try{var S=i.lastRenderedState,T=h(S,r);if(u.hasEagerState=!0,u.eagerState=T,ri(T,S))return Mc(e,i,u,0),Ye===null&&Sc(),!1}catch{}finally{}if(r=Of(e,i,u,o),r!==null)return ti(r,e,o),uv(r,i,o),!0}return!1}function vh(e,i,r,o){if(o={lane:2,revertLane:Qh(),gesture:null,action:o,hasEagerState:!1,eagerState:null,next:null},Vc(e)){if(i)throw Error(a(479))}else i=Of(e,r,o,2),i!==null&&ti(i,e,2)}function Vc(e){var i=e.alternate;return e===ce||i!==null&&i===ce}function cv(e,i){Ir=Pc=!0;var r=e.pending;r===null?i.next=i:(i.next=r.next,r.next=i),e.pending=i}function uv(e,i,r){if((r&4194048)!==0){var o=i.lanes;o&=e.pendingLanes,r|=o,i.lanes=r,qo(e,r)}}var gl={readContext:Un,use:Bc,useCallback:rn,useContext:rn,useEffect:rn,useImperativeHandle:rn,useLayoutEffect:rn,useInsertionEffect:rn,useMemo:rn,useReducer:rn,useRef:rn,useState:rn,useDebugValue:rn,useDeferredValue:rn,useTransition:rn,useSyncExternalStore:rn,useId:rn,useHostTransitionStatus:rn,useFormState:rn,useActionState:rn,useOptimistic:rn,useMemoCache:rn,useCacheRefresh:rn};gl.useEffectEvent=rn;var fv={readContext:Un,use:Bc,useCallback:function(e,i){return kn().memoizedState=[e,i===void 0?null:i],e},useContext:Un,useEffect:Yg,useImperativeHandle:function(e,i,r){r=r!=null?r.concat([e]):null,Hc(4194308,4,Jg.bind(null,i,e),r)},useLayoutEffect:function(e,i){return Hc(4194308,4,e,i)},useInsertionEffect:function(e,i){Hc(4,2,e,i)},useMemo:function(e,i){var r=kn();i=i===void 0?null:i;var o=e();if(ks){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[o,i],o},useReducer:function(e,i,r){var o=kn();if(r!==void 0){var u=r(i);if(ks){Ot(!0);try{r(i)}finally{Ot(!1)}}}else u=i;return o.memoizedState=o.baseState=u,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:u},o.queue=e,e=e.dispatch=$S.bind(null,ce,e),[o.memoizedState,e]},useRef:function(e){var i=kn();return e={current:e},i.memoizedState=e},useState:function(e){e=uh(e);var i=e.queue,r=lv.bind(null,ce,i);return i.dispatch=r,[e.memoizedState,r]},useDebugValue:dh,useDeferredValue:function(e,i){var r=kn();return ph(r,e,i)},useTransition:function(){var e=uh(!1);return e=iv.bind(null,ce,e.queue,!0,!1),kn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,i,r){var o=ce,u=kn();if(Ce){if(r===void 0)throw Error(a(407));r=r()}else{if(r=i(),Ye===null)throw Error(a(349));(be&127)!==0||Ng(o,i,r)}u.memoizedState=r;var h={value:r,getSnapshot:i};return u.queue=h,Yg(Og.bind(null,o,h,e),[e]),o.flags|=2048,Fr(9,{destroy:void 0},Lg.bind(null,o,h,r,i),null),r},useId:function(){var e=kn(),i=Ye.identifierPrefix;if(Ce){var r=qi,o=ji;r=(o&~(1<<32-ne(o)-1)).toString(32)+r,i="_"+i+"R_"+r,r=zc++,0<r&&(i+="H"+r.toString(32)),i+="_"}else r=qS++,i="_"+i+"r_"+r.toString(32)+"_";return e.memoizedState=i},useHostTransitionStatus:gh,useFormState:kg,useActionState:kg,useOptimistic:function(e){var i=kn();i.memoizedState=i.baseState=e;var r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return i.queue=r,i=vh.bind(null,ce,!0,r),r.dispatch=i,[e,i]},useMemoCache:oh,useCacheRefresh:function(){return kn().memoizedState=JS.bind(null,ce)},useEffectEvent:function(e){var i=kn(),r={impl:e};return i.memoizedState=r,function(){if((Pe&2)!==0)throw Error(a(440));return r.impl.apply(void 0,arguments)}}},_h={readContext:Un,use:Bc,useCallback:tv,useContext:Un,useEffect:hh,useImperativeHandle:$g,useInsertionEffect:Zg,useLayoutEffect:Kg,useMemo:ev,useReducer:Fc,useRef:Wg,useState:function(){return Fc(ua)},useDebugValue:dh,useDeferredValue:function(e,i){var r=fn();return nv(r,Ve.memoizedState,e,i)},useTransition:function(){var e=Fc(ua)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:pl(e),i]},useSyncExternalStore:Ug,useId:rv,useHostTransitionStatus:gh,useFormState:Xg,useActionState:Xg,useOptimistic:function(e,i){var r=fn();return Ig(r,Ve,e,i)},useMemoCache:oh,useCacheRefresh:ov};_h.useEffectEvent=Qg;var hv={readContext:Un,use:Bc,useCallback:tv,useContext:Un,useEffect:hh,useImperativeHandle:$g,useInsertionEffect:Zg,useLayoutEffect:Kg,useMemo:ev,useReducer:ch,useRef:Wg,useState:function(){return ch(ua)},useDebugValue:dh,useDeferredValue:function(e,i){var r=fn();return Ve===null?ph(r,e,i):nv(r,Ve.memoizedState,e,i)},useTransition:function(){var e=ch(ua)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:pl(e),i]},useSyncExternalStore:Ug,useId:rv,useHostTransitionStatus:gh,useFormState:qg,useActionState:qg,useOptimistic:function(e,i){var r=fn();return Ve!==null?Ig(r,Ve,e,i):(r.baseState=e,[e,r.queue.dispatch])},useMemoCache:oh,useCacheRefresh:ov};hv.useEffectEvent=Qg;function yh(e,i,r,o){i=e.memoizedState,r=r(o,i),r=r==null?i:v({},i,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var xh={enqueueSetState:function(e,i,r){e=e._reactInternals;var o=hi(),u=Xa(o);u.payload=i,r!=null&&(u.callback=r),i=ja(e,u,o),i!==null&&(ti(i,e,o),ul(i,e,o))},enqueueReplaceState:function(e,i,r){e=e._reactInternals;var o=hi(),u=Xa(o);u.tag=1,u.payload=i,r!=null&&(u.callback=r),i=ja(e,u,o),i!==null&&(ti(i,e,o),ul(i,e,o))},enqueueForceUpdate:function(e,i){e=e._reactInternals;var r=hi(),o=Xa(r);o.tag=2,i!=null&&(o.callback=i),i=ja(e,o,r),i!==null&&(ti(i,e,r),ul(i,e,r))}};function dv(e,i,r,o,u,h,S){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(o,h,S):i.prototype&&i.prototype.isPureReactComponent?!nl(r,o)||!nl(u,h):!0}function pv(e,i,r,o){e=i.state,typeof i.componentWillReceiveProps=="function"&&i.componentWillReceiveProps(r,o),typeof i.UNSAFE_componentWillReceiveProps=="function"&&i.UNSAFE_componentWillReceiveProps(r,o),i.state!==e&&xh.enqueueReplaceState(i,i.state,null)}function Xs(e,i){var r=i;if("ref"in i){r={};for(var o in i)o!=="ref"&&(r[o]=i[o])}if(e=e.defaultProps){r===i&&(r=v({},r));for(var u in e)r[u]===void 0&&(r[u]=e[u])}return r}function mv(e){xc(e)}function gv(e){console.error(e)}function vv(e){xc(e)}function kc(e,i){try{var r=e.onUncaughtError;r(i.value,{componentStack:i.stack})}catch(o){setTimeout(function(){throw o})}}function _v(e,i,r){try{var o=e.onCaughtError;o(r.value,{componentStack:r.stack,errorBoundary:i.tag===1?i.stateNode:null})}catch(u){setTimeout(function(){throw u})}}function Sh(e,i,r){return r=Xa(r),r.tag=3,r.payload={element:null},r.callback=function(){kc(e,i)},r}function yv(e){return e=Xa(e),e.tag=3,e}function xv(e,i,r,o){var u=r.type.getDerivedStateFromError;if(typeof u=="function"){var h=o.value;e.payload=function(){return u(h)},e.callback=function(){_v(i,r,o)}}var S=r.stateNode;S!==null&&typeof S.componentDidCatch=="function"&&(e.callback=function(){_v(i,r,o),typeof u!="function"&&(Ka===null?Ka=new Set([this]):Ka.add(this));var T=o.stack;this.componentDidCatch(o.value,{componentStack:T!==null?T:""})})}function tM(e,i,r,o,u){if(r.flags|=32768,o!==null&&typeof o=="object"&&typeof o.then=="function"){if(i=r.alternate,i!==null&&Ur(i,r,u,!0),r=li.current,r!==null){switch(r.tag){case 31:case 13:return bi===null?eu():r.alternate===null&&on===0&&(on=3),r.flags&=-257,r.flags|=65536,r.lanes=u,o===Dc?r.flags|=16384:(i=r.updateQueue,i===null?r.updateQueue=new Set([o]):i.add(o),qh(e,o,u)),!1;case 22:return r.flags|=65536,o===Dc?r.flags|=16384:(i=r.updateQueue,i===null?(i={transitions:null,markerInstances:null,retryQueue:new Set([o])},r.updateQueue=i):(r=i.retryQueue,r===null?i.retryQueue=new Set([o]):r.add(o)),qh(e,o,u)),!1}throw Error(a(435,r.tag))}return qh(e,o,u),eu(),!1}if(Ce)return i=li.current,i!==null?((i.flags&65536)===0&&(i.flags|=256),i.flags|=65536,i.lanes=u,o!==Hf&&(e=Error(a(422),{cause:o}),sl(xi(e,r)))):(o!==Hf&&(i=Error(a(423),{cause:o}),sl(xi(i,r))),e=e.current.alternate,e.flags|=65536,u&=-u,e.lanes|=u,o=xi(o,r),u=Sh(e.stateNode,o,u),Kf(e,u),on!==4&&(on=2)),!1;var h=Error(a(520),{cause:o});if(h=xi(h,r),bl===null?bl=[h]:bl.push(h),on!==4&&(on=2),i===null)return!0;o=xi(o,r),r=i;do{switch(r.tag){case 3:return r.flags|=65536,e=u&-u,r.lanes|=e,e=Sh(r.stateNode,o,e),Kf(r,e),!1;case 1:if(i=r.type,h=r.stateNode,(r.flags&128)===0&&(typeof i.getDerivedStateFromError=="function"||h!==null&&typeof h.componentDidCatch=="function"&&(Ka===null||!Ka.has(h))))return r.flags|=65536,u&=-u,r.lanes|=u,u=yv(u),xv(u,e,r,o),Kf(r,u),!1}r=r.return}while(r!==null);return!1}var Mh=Error(a(461)),mn=!1;function Nn(e,i,r,o){i.child=e===null?bg(i,null,r,o):Vs(i,e.child,r,o)}function Sv(e,i,r,o,u){r=r.render;var h=i.ref;if("ref"in o){var S={};for(var T in o)T!=="ref"&&(S[T]=o[T])}else S=o;return Bs(i),o=ih(e,i,r,S,h,u),T=ah(),e!==null&&!mn?(sh(e,i,u),fa(e,i,u)):(Ce&&T&&Bf(i),i.flags|=1,Nn(e,i,o,u),i.child)}function Mv(e,i,r,o,u){if(e===null){var h=r.type;return typeof h=="function"&&!Pf(h)&&h.defaultProps===void 0&&r.compare===null?(i.tag=15,i.type=h,Ev(e,i,h,o,u)):(e=bc(r.type,null,o,i,i.mode,u),e.ref=i.ref,e.return=i,i.child=e)}if(h=e.child,!Dh(e,u)){var S=h.memoizedProps;if(r=r.compare,r=r!==null?r:nl,r(S,o)&&e.ref===i.ref)return fa(e,i,u)}return i.flags|=1,e=sa(h,o),e.ref=i.ref,e.return=i,i.child=e}function Ev(e,i,r,o,u){if(e!==null){var h=e.memoizedProps;if(nl(h,o)&&e.ref===i.ref)if(mn=!1,i.pendingProps=o=h,Dh(e,u))(e.flags&131072)!==0&&(mn=!0);else return i.lanes=e.lanes,fa(e,i,u)}return Eh(e,i,r,o,u)}function bv(e,i,r,o){var u=o.children,h=e!==null?e.memoizedState:null;if(e===null&&i.stateNode===null&&(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),o.mode==="hidden"){if((i.flags&128)!==0){if(h=h!==null?h.baseLanes|r:r,e!==null){for(o=i.child=e.child,u=0;o!==null;)u=u|o.lanes|o.childLanes,o=o.sibling;o=u&~h}else o=0,i.child=null;return Tv(e,i,h,r,o)}if((r&536870912)!==0)i.memoizedState={baseLanes:0,cachePool:null},e!==null&&Rc(i,h!==null?h.cachePool:null),h!==null?Cg(i,h):$f(),Rg(i);else return o=i.lanes=536870912,Tv(e,i,h!==null?h.baseLanes|r:r,r,o)}else h!==null?(Rc(i,h.cachePool),Cg(i,h),Wa(),i.memoizedState=null):(e!==null&&Rc(i,null),$f(),Wa());return Nn(e,i,u,r),i.child}function vl(e,i){return e!==null&&e.tag===22||i.stateNode!==null||(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),i.sibling}function Tv(e,i,r,o,u){var h=Wf();return h=h===null?null:{parent:dn._currentValue,pool:h},i.memoizedState={baseLanes:r,cachePool:h},e!==null&&Rc(i,null),$f(),Rg(i),e!==null&&Ur(e,i,o,!0),i.childLanes=u,null}function Xc(e,i){return i=qc({mode:i.mode,children:i.children},e.mode),i.ref=e.ref,e.child=i,i.return=e,i}function Av(e,i,r){return Vs(i,e.child,null,r),e=Xc(i,i.pendingProps),e.flags|=2,ci(i),i.memoizedState=null,e}function eM(e,i,r){var o=i.pendingProps,u=(i.flags&128)!==0;if(i.flags&=-129,e===null){if(Ce){if(o.mode==="hidden")return e=Xc(i,o),i.lanes=536870912,vl(null,e);if(eh(i),(e=Ze)?(e=B0(e,Ei),e=e!==null&&e.data==="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Fa!==null?{id:ji,overflow:qi}:null,retryLane:536870912,hydrationErrors:null},r=cg(e),r.return=i,i.child=r,Dn=i,Ze=null)):e=null,e===null)throw Ga(i);return i.lanes=536870912,null}return Xc(i,o)}var h=e.memoizedState;if(h!==null){var S=h.dehydrated;if(eh(i),u)if(i.flags&256)i.flags&=-257,i=Av(e,i,r);else if(i.memoizedState!==null)i.child=e.child,i.flags|=128,i=null;else throw Error(a(558));else if(mn||Ur(e,i,r,!1),u=(r&e.childLanes)!==0,mn||u){if(o=Ye,o!==null&&(S=ki(o,r),S!==0&&S!==h.retryLane))throw h.retryLane=S,Os(e,S),ti(o,e,S),Mh;eu(),i=Av(e,i,r)}else e=h.treeContext,Ze=Ti(S.nextSibling),Dn=i,Ce=!0,Ha=null,Ei=!1,e!==null&&hg(i,e),i=Xc(i,o),i.flags|=4096;return i}return e=sa(e.child,{mode:o.mode,children:o.children}),e.ref=i.ref,i.child=e,e.return=i,e}function jc(e,i){var r=i.ref;if(r===null)e!==null&&e.ref!==null&&(i.flags|=4194816);else{if(typeof r!="function"&&typeof r!="object")throw Error(a(284));(e===null||e.ref!==r)&&(i.flags|=4194816)}}function Eh(e,i,r,o,u){return Bs(i),r=ih(e,i,r,o,void 0,u),o=ah(),e!==null&&!mn?(sh(e,i,u),fa(e,i,u)):(Ce&&o&&Bf(i),i.flags|=1,Nn(e,i,r,u),i.child)}function Cv(e,i,r,o,u,h){return Bs(i),i.updateQueue=null,r=Dg(i,o,r,u),wg(e),o=ah(),e!==null&&!mn?(sh(e,i,h),fa(e,i,h)):(Ce&&o&&Bf(i),i.flags|=1,Nn(e,i,r,h),i.child)}function Rv(e,i,r,o,u){if(Bs(i),i.stateNode===null){var h=Cr,S=r.contextType;typeof S=="object"&&S!==null&&(h=Un(S)),h=new r(o,h),i.memoizedState=h.state!==null&&h.state!==void 0?h.state:null,h.updater=xh,i.stateNode=h,h._reactInternals=i,h=i.stateNode,h.props=o,h.state=i.memoizedState,h.refs={},Qf(i),S=r.contextType,h.context=typeof S=="object"&&S!==null?Un(S):Cr,h.state=i.memoizedState,S=r.getDerivedStateFromProps,typeof S=="function"&&(yh(i,r,S,o),h.state=i.memoizedState),typeof r.getDerivedStateFromProps=="function"||typeof h.getSnapshotBeforeUpdate=="function"||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(S=h.state,typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount(),S!==h.state&&xh.enqueueReplaceState(h,h.state,null),hl(i,o,h,u),fl(),h.state=i.memoizedState),typeof h.componentDidMount=="function"&&(i.flags|=4194308),o=!0}else if(e===null){h=i.stateNode;var T=i.memoizedProps,B=Xs(r,T);h.props=B;var et=h.context,dt=r.contextType;S=Cr,typeof dt=="object"&&dt!==null&&(S=Un(dt));var _t=r.getDerivedStateFromProps;dt=typeof _t=="function"||typeof h.getSnapshotBeforeUpdate=="function",T=i.pendingProps!==T,dt||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(T||et!==S)&&pv(i,h,o,S),ka=!1;var it=i.memoizedState;h.state=it,hl(i,o,h,u),fl(),et=i.memoizedState,T||it!==et||ka?(typeof _t=="function"&&(yh(i,r,_t,o),et=i.memoizedState),(B=ka||dv(i,r,B,o,it,et,S))?(dt||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount()),typeof h.componentDidMount=="function"&&(i.flags|=4194308)):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),i.memoizedProps=o,i.memoizedState=et),h.props=o,h.state=et,h.context=S,o=B):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),o=!1)}else{h=i.stateNode,Zf(e,i),S=i.memoizedProps,dt=Xs(r,S),h.props=dt,_t=i.pendingProps,it=h.context,et=r.contextType,B=Cr,typeof et=="object"&&et!==null&&(B=Un(et)),T=r.getDerivedStateFromProps,(et=typeof T=="function"||typeof h.getSnapshotBeforeUpdate=="function")||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(S!==_t||it!==B)&&pv(i,h,o,B),ka=!1,it=i.memoizedState,h.state=it,hl(i,o,h,u),fl();var lt=i.memoizedState;S!==_t||it!==lt||ka||e!==null&&e.dependencies!==null&&Ac(e.dependencies)?(typeof T=="function"&&(yh(i,r,T,o),lt=i.memoizedState),(dt=ka||dv(i,r,dt,o,it,lt,B)||e!==null&&e.dependencies!==null&&Ac(e.dependencies))?(et||typeof h.UNSAFE_componentWillUpdate!="function"&&typeof h.componentWillUpdate!="function"||(typeof h.componentWillUpdate=="function"&&h.componentWillUpdate(o,lt,B),typeof h.UNSAFE_componentWillUpdate=="function"&&h.UNSAFE_componentWillUpdate(o,lt,B)),typeof h.componentDidUpdate=="function"&&(i.flags|=4),typeof h.getSnapshotBeforeUpdate=="function"&&(i.flags|=1024)):(typeof h.componentDidUpdate!="function"||S===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||S===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),i.memoizedProps=o,i.memoizedState=lt),h.props=o,h.state=lt,h.context=B,o=dt):(typeof h.componentDidUpdate!="function"||S===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||S===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),o=!1)}return h=o,jc(e,i),o=(i.flags&128)!==0,h||o?(h=i.stateNode,r=o&&typeof r.getDerivedStateFromError!="function"?null:h.render(),i.flags|=1,e!==null&&o?(i.child=Vs(i,e.child,null,u),i.child=Vs(i,null,r,u)):Nn(e,i,r,u),i.memoizedState=h.state,e=i.child):e=fa(e,i,u),e}function wv(e,i,r,o){return zs(),i.flags|=256,Nn(e,i,r,o),i.child}var bh={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function Th(e){return{baseLanes:e,cachePool:_g()}}function Ah(e,i,r){return e=e!==null?e.childLanes&~r:0,i&&(e|=fi),e}function Dv(e,i,r){var o=i.pendingProps,u=!1,h=(i.flags&128)!==0,S;if((S=h)||(S=e!==null&&e.memoizedState===null?!1:(un.current&2)!==0),S&&(u=!0,i.flags&=-129),S=(i.flags&32)!==0,i.flags&=-33,e===null){if(Ce){if(u?qa(i):Wa(),(e=Ze)?(e=B0(e,Ei),e=e!==null&&e.data!=="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Fa!==null?{id:ji,overflow:qi}:null,retryLane:536870912,hydrationErrors:null},r=cg(e),r.return=i,i.child=r,Dn=i,Ze=null)):e=null,e===null)throw Ga(i);return ld(e)?i.lanes=32:i.lanes=536870912,null}var T=o.children;return o=o.fallback,u?(Wa(),u=i.mode,T=qc({mode:"hidden",children:T},u),o=Ps(o,u,r,null),T.return=i,o.return=i,T.sibling=o,i.child=T,o=i.child,o.memoizedState=Th(r),o.childLanes=Ah(e,S,r),i.memoizedState=bh,vl(null,o)):(qa(i),Ch(i,T))}var B=e.memoizedState;if(B!==null&&(T=B.dehydrated,T!==null)){if(h)i.flags&256?(qa(i),i.flags&=-257,i=Rh(e,i,r)):i.memoizedState!==null?(Wa(),i.child=e.child,i.flags|=128,i=null):(Wa(),T=o.fallback,u=i.mode,o=qc({mode:"visible",children:o.children},u),T=Ps(T,u,r,null),T.flags|=2,o.return=i,T.return=i,o.sibling=T,i.child=o,Vs(i,e.child,null,r),o=i.child,o.memoizedState=Th(r),o.childLanes=Ah(e,S,r),i.memoizedState=bh,i=vl(null,o));else if(qa(i),ld(T)){if(S=T.nextSibling&&T.nextSibling.dataset,S)var et=S.dgst;S=et,o=Error(a(419)),o.stack="",o.digest=S,sl({value:o,source:null,stack:null}),i=Rh(e,i,r)}else if(mn||Ur(e,i,r,!1),S=(r&e.childLanes)!==0,mn||S){if(S=Ye,S!==null&&(o=ki(S,r),o!==0&&o!==B.retryLane))throw B.retryLane=o,Os(e,o),ti(S,e,o),Mh;od(T)||eu(),i=Rh(e,i,r)}else od(T)?(i.flags|=192,i.child=e.child,i=null):(e=B.treeContext,Ze=Ti(T.nextSibling),Dn=i,Ce=!0,Ha=null,Ei=!1,e!==null&&hg(i,e),i=Ch(i,o.children),i.flags|=4096);return i}return u?(Wa(),T=o.fallback,u=i.mode,B=e.child,et=B.sibling,o=sa(B,{mode:"hidden",children:o.children}),o.subtreeFlags=B.subtreeFlags&65011712,et!==null?T=sa(et,T):(T=Ps(T,u,r,null),T.flags|=2),T.return=i,o.return=i,o.sibling=T,i.child=o,vl(null,o),o=i.child,T=e.child.memoizedState,T===null?T=Th(r):(u=T.cachePool,u!==null?(B=dn._currentValue,u=u.parent!==B?{parent:B,pool:B}:u):u=_g(),T={baseLanes:T.baseLanes|r,cachePool:u}),o.memoizedState=T,o.childLanes=Ah(e,S,r),i.memoizedState=bh,vl(e.child,o)):(qa(i),r=e.child,e=r.sibling,r=sa(r,{mode:"visible",children:o.children}),r.return=i,r.sibling=null,e!==null&&(S=i.deletions,S===null?(i.deletions=[e],i.flags|=16):S.push(e)),i.child=r,i.memoizedState=null,r)}function Ch(e,i){return i=qc({mode:"visible",children:i},e.mode),i.return=e,e.child=i}function qc(e,i){return e=oi(22,e,null,i),e.lanes=0,e}function Rh(e,i,r){return Vs(i,e.child,null,r),e=Ch(i,i.pendingProps.children),e.flags|=2,i.memoizedState=null,e}function Uv(e,i,r){e.lanes|=i;var o=e.alternate;o!==null&&(o.lanes|=i),kf(e.return,i,r)}function wh(e,i,r,o,u,h){var S=e.memoizedState;S===null?e.memoizedState={isBackwards:i,rendering:null,renderingStartTime:0,last:o,tail:r,tailMode:u,treeForkCount:h}:(S.isBackwards=i,S.rendering=null,S.renderingStartTime=0,S.last=o,S.tail=r,S.tailMode=u,S.treeForkCount=h)}function Nv(e,i,r){var o=i.pendingProps,u=o.revealOrder,h=o.tail;o=o.children;var S=un.current,T=(S&2)!==0;if(T?(S=S&1|2,i.flags|=128):S&=1,St(un,S),Nn(e,i,o,r),o=Ce?al:0,!T&&e!==null&&(e.flags&128)!==0)t:for(e=i.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Uv(e,r,i);else if(e.tag===19)Uv(e,r,i);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===i)break t;for(;e.sibling===null;){if(e.return===null||e.return===i)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(u){case"forwards":for(r=i.child,u=null;r!==null;)e=r.alternate,e!==null&&Oc(e)===null&&(u=r),r=r.sibling;r=u,r===null?(u=i.child,i.child=null):(u=r.sibling,r.sibling=null),wh(i,!1,u,r,h,o);break;case"backwards":case"unstable_legacy-backwards":for(r=null,u=i.child,i.child=null;u!==null;){if(e=u.alternate,e!==null&&Oc(e)===null){i.child=u;break}e=u.sibling,u.sibling=r,r=u,u=e}wh(i,!0,r,null,h,o);break;case"together":wh(i,!1,null,null,void 0,o);break;default:i.memoizedState=null}return i.child}function fa(e,i,r){if(e!==null&&(i.dependencies=e.dependencies),Za|=i.lanes,(r&i.childLanes)===0)if(e!==null){if(Ur(e,i,r,!1),(r&i.childLanes)===0)return null}else return null;if(e!==null&&i.child!==e.child)throw Error(a(153));if(i.child!==null){for(e=i.child,r=sa(e,e.pendingProps),i.child=r,r.return=i;e.sibling!==null;)e=e.sibling,r=r.sibling=sa(e,e.pendingProps),r.return=i;r.sibling=null}return i.child}function Dh(e,i){return(e.lanes&i)!==0?!0:(e=e.dependencies,!!(e!==null&&Ac(e)))}function nM(e,i,r){switch(i.tag){case 3:Ft(i,i.stateNode.containerInfo),Va(i,dn,e.memoizedState.cache),zs();break;case 27:case 5:re(i);break;case 4:Ft(i,i.stateNode.containerInfo);break;case 10:Va(i,i.type,i.memoizedProps.value);break;case 31:if(i.memoizedState!==null)return i.flags|=128,eh(i),null;break;case 13:var o=i.memoizedState;if(o!==null)return o.dehydrated!==null?(qa(i),i.flags|=128,null):(r&i.child.childLanes)!==0?Dv(e,i,r):(qa(i),e=fa(e,i,r),e!==null?e.sibling:null);qa(i);break;case 19:var u=(e.flags&128)!==0;if(o=(r&i.childLanes)!==0,o||(Ur(e,i,r,!1),o=(r&i.childLanes)!==0),u){if(o)return Nv(e,i,r);i.flags|=128}if(u=i.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),St(un,un.current),o)break;return null;case 22:return i.lanes=0,bv(e,i,r,i.pendingProps);case 24:Va(i,dn,e.memoizedState.cache)}return fa(e,i,r)}function Lv(e,i,r){if(e!==null)if(e.memoizedProps!==i.pendingProps)mn=!0;else{if(!Dh(e,r)&&(i.flags&128)===0)return mn=!1,nM(e,i,r);mn=(e.flags&131072)!==0}else mn=!1,Ce&&(i.flags&1048576)!==0&&fg(i,al,i.index);switch(i.lanes=0,i.tag){case 16:t:{var o=i.pendingProps;if(e=Hs(i.elementType),i.type=e,typeof e=="function")Pf(e)?(o=Xs(e,o),i.tag=1,i=Rv(null,i,e,o,r)):(i.tag=0,i=Eh(null,i,e,o,r));else{if(e!=null){var u=e.$$typeof;if(u===C){i.tag=11,i=Sv(null,i,e,o,r);break t}else if(u===P){i.tag=14,i=Mv(null,i,e,o,r);break t}}throw i=mt(e)||e,Error(a(306,i,""))}}return i;case 0:return Eh(e,i,i.type,i.pendingProps,r);case 1:return o=i.type,u=Xs(o,i.pendingProps),Rv(e,i,o,u,r);case 3:t:{if(Ft(i,i.stateNode.containerInfo),e===null)throw Error(a(387));o=i.pendingProps;var h=i.memoizedState;u=h.element,Zf(e,i),hl(i,o,null,r);var S=i.memoizedState;if(o=S.cache,Va(i,dn,o),o!==h.cache&&Xf(i,[dn],r,!0),fl(),o=S.element,h.isDehydrated)if(h={element:o,isDehydrated:!1,cache:S.cache},i.updateQueue.baseState=h,i.memoizedState=h,i.flags&256){i=wv(e,i,o,r);break t}else if(o!==u){u=xi(Error(a(424)),i),sl(u),i=wv(e,i,o,r);break t}else{switch(e=i.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Ze=Ti(e.firstChild),Dn=i,Ce=!0,Ha=null,Ei=!0,r=bg(i,null,o,r),i.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling}else{if(zs(),o===u){i=fa(e,i,r);break t}Nn(e,i,o,r)}i=i.child}return i;case 26:return jc(e,i),e===null?(r=X0(i.type,null,i.pendingProps,null))?i.memoizedState=r:Ce||(r=i.type,e=i.pendingProps,o=lu(Tt.current).createElement(r),o[sn]=i,o[wn]=e,Ln(o,r,e),xt(o),i.stateNode=o):i.memoizedState=X0(i.type,e.memoizedProps,i.pendingProps,e.memoizedState),null;case 27:return re(i),e===null&&Ce&&(o=i.stateNode=G0(i.type,i.pendingProps,Tt.current),Dn=i,Ei=!0,u=Ze,es(i.type)?(cd=u,Ze=Ti(o.firstChild)):Ze=u),Nn(e,i,i.pendingProps.children,r),jc(e,i),e===null&&(i.flags|=4194304),i.child;case 5:return e===null&&Ce&&((u=o=Ze)&&(o=NM(o,i.type,i.pendingProps,Ei),o!==null?(i.stateNode=o,Dn=i,Ze=Ti(o.firstChild),Ei=!1,u=!0):u=!1),u||Ga(i)),re(i),u=i.type,h=i.pendingProps,S=e!==null?e.memoizedProps:null,o=h.children,ad(u,h)?o=null:S!==null&&ad(u,S)&&(i.flags|=32),i.memoizedState!==null&&(u=ih(e,i,WS,null,null,r),Nl._currentValue=u),jc(e,i),Nn(e,i,o,r),i.child;case 6:return e===null&&Ce&&((e=r=Ze)&&(r=LM(r,i.pendingProps,Ei),r!==null?(i.stateNode=r,Dn=i,Ze=null,e=!0):e=!1),e||Ga(i)),null;case 13:return Dv(e,i,r);case 4:return Ft(i,i.stateNode.containerInfo),o=i.pendingProps,e===null?i.child=Vs(i,null,o,r):Nn(e,i,o,r),i.child;case 11:return Sv(e,i,i.type,i.pendingProps,r);case 7:return Nn(e,i,i.pendingProps,r),i.child;case 8:return Nn(e,i,i.pendingProps.children,r),i.child;case 12:return Nn(e,i,i.pendingProps.children,r),i.child;case 10:return o=i.pendingProps,Va(i,i.type,o.value),Nn(e,i,o.children,r),i.child;case 9:return u=i.type._context,o=i.pendingProps.children,Bs(i),u=Un(u),o=o(u),i.flags|=1,Nn(e,i,o,r),i.child;case 14:return Mv(e,i,i.type,i.pendingProps,r);case 15:return Ev(e,i,i.type,i.pendingProps,r);case 19:return Nv(e,i,r);case 31:return eM(e,i,r);case 22:return bv(e,i,r,i.pendingProps);case 24:return Bs(i),o=Un(dn),e===null?(u=Wf(),u===null&&(u=Ye,h=jf(),u.pooledCache=h,h.refCount++,h!==null&&(u.pooledCacheLanes|=r),u=h),i.memoizedState={parent:o,cache:u},Qf(i),Va(i,dn,u)):((e.lanes&r)!==0&&(Zf(e,i),hl(i,null,null,r),fl()),u=e.memoizedState,h=i.memoizedState,u.parent!==o?(u={parent:o,cache:o},i.memoizedState=u,i.lanes===0&&(i.memoizedState=i.updateQueue.baseState=u),Va(i,dn,o)):(o=h.cache,Va(i,dn,o),o!==u.cache&&Xf(i,[dn],r,!0))),Nn(e,i,i.pendingProps.children,r),i.child;case 29:throw i.pendingProps}throw Error(a(156,i.tag))}function ha(e){e.flags|=4}function Uh(e,i,r,o,u){if((i=(e.mode&32)!==0)&&(i=!1),i){if(e.flags|=16777216,(u&335544128)===u)if(e.stateNode.complete)e.flags|=8192;else if(r0())e.flags|=8192;else throw Gs=Dc,Yf}else e.flags&=-16777217}function Ov(e,i){if(i.type!=="stylesheet"||(i.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!Q0(i))if(r0())e.flags|=8192;else throw Gs=Dc,Yf}function Wc(e,i){i!==null&&(e.flags|=4),e.flags&16384&&(i=e.tag!==22?_n():536870912,e.lanes|=i,kr|=i)}function _l(e,i){if(!Ce)switch(e.tailMode){case"hidden":i=e.tail;for(var r=null;i!==null;)i.alternate!==null&&(r=i),i=i.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var o=null;r!==null;)r.alternate!==null&&(o=r),r=r.sibling;o===null?i||e.tail===null?e.tail=null:e.tail.sibling=null:o.sibling=null}}function Ke(e){var i=e.alternate!==null&&e.alternate.child===e.child,r=0,o=0;if(i)for(var u=e.child;u!==null;)r|=u.lanes|u.childLanes,o|=u.subtreeFlags&65011712,o|=u.flags&65011712,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)r|=u.lanes|u.childLanes,o|=u.subtreeFlags,o|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=o,e.childLanes=r,i}function iM(e,i,r){var o=i.pendingProps;switch(Ff(i),i.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Ke(i),null;case 1:return Ke(i),null;case 3:return r=i.stateNode,o=null,e!==null&&(o=e.memoizedState.cache),i.memoizedState.cache!==o&&(i.flags|=2048),la(dn),Vt(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(Dr(i)?ha(i):e===null||e.memoizedState.isDehydrated&&(i.flags&256)===0||(i.flags|=1024,Gf())),Ke(i),null;case 26:var u=i.type,h=i.memoizedState;return e===null?(ha(i),h!==null?(Ke(i),Ov(i,h)):(Ke(i),Uh(i,u,null,o,r))):h?h!==e.memoizedState?(ha(i),Ke(i),Ov(i,h)):(Ke(i),i.flags&=-16777217):(e=e.memoizedProps,e!==o&&ha(i),Ke(i),Uh(i,u,e,o,r)),null;case 27:if(He(i),r=Tt.current,u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(!o){if(i.stateNode===null)throw Error(a(166));return Ke(i),null}e=q.current,Dr(i)?dg(i):(e=G0(u,o,r),i.stateNode=e,ha(i))}return Ke(i),null;case 5:if(He(i),u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(!o){if(i.stateNode===null)throw Error(a(166));return Ke(i),null}if(h=q.current,Dr(i))dg(i);else{var S=lu(Tt.current);switch(h){case 1:h=S.createElementNS("http://www.w3.org/2000/svg",u);break;case 2:h=S.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;default:switch(u){case"svg":h=S.createElementNS("http://www.w3.org/2000/svg",u);break;case"math":h=S.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;case"script":h=S.createElement("div"),h.innerHTML="<script><\/script>",h=h.removeChild(h.firstChild);break;case"select":h=typeof o.is=="string"?S.createElement("select",{is:o.is}):S.createElement("select"),o.multiple?h.multiple=!0:o.size&&(h.size=o.size);break;default:h=typeof o.is=="string"?S.createElement(u,{is:o.is}):S.createElement(u)}}h[sn]=i,h[wn]=o;t:for(S=i.child;S!==null;){if(S.tag===5||S.tag===6)h.appendChild(S.stateNode);else if(S.tag!==4&&S.tag!==27&&S.child!==null){S.child.return=S,S=S.child;continue}if(S===i)break t;for(;S.sibling===null;){if(S.return===null||S.return===i)break t;S=S.return}S.sibling.return=S.return,S=S.sibling}i.stateNode=h;t:switch(Ln(h,u,o),u){case"button":case"input":case"select":case"textarea":o=!!o.autoFocus;break t;case"img":o=!0;break t;default:o=!1}o&&ha(i)}}return Ke(i),Uh(i,i.type,e===null?null:e.memoizedProps,i.pendingProps,r),null;case 6:if(e&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(typeof o!="string"&&i.stateNode===null)throw Error(a(166));if(e=Tt.current,Dr(i)){if(e=i.stateNode,r=i.memoizedProps,o=null,u=Dn,u!==null)switch(u.tag){case 27:case 5:o=u.memoizedProps}e[sn]=i,e=!!(e.nodeValue===r||o!==null&&o.suppressHydrationWarning===!0||D0(e.nodeValue,r)),e||Ga(i,!0)}else e=lu(e).createTextNode(o),e[sn]=i,i.stateNode=e}return Ke(i),null;case 31:if(r=i.memoizedState,e===null||e.memoizedState!==null){if(o=Dr(i),r!==null){if(e===null){if(!o)throw Error(a(318));if(e=i.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(a(557));e[sn]=i}else zs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Ke(i),e=!1}else r=Gf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=r),e=!0;if(!e)return i.flags&256?(ci(i),i):(ci(i),null);if((i.flags&128)!==0)throw Error(a(558))}return Ke(i),null;case 13:if(o=i.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(u=Dr(i),o!==null&&o.dehydrated!==null){if(e===null){if(!u)throw Error(a(318));if(u=i.memoizedState,u=u!==null?u.dehydrated:null,!u)throw Error(a(317));u[sn]=i}else zs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Ke(i),u=!1}else u=Gf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=u),u=!0;if(!u)return i.flags&256?(ci(i),i):(ci(i),null)}return ci(i),(i.flags&128)!==0?(i.lanes=r,i):(r=o!==null,e=e!==null&&e.memoizedState!==null,r&&(o=i.child,u=null,o.alternate!==null&&o.alternate.memoizedState!==null&&o.alternate.memoizedState.cachePool!==null&&(u=o.alternate.memoizedState.cachePool.pool),h=null,o.memoizedState!==null&&o.memoizedState.cachePool!==null&&(h=o.memoizedState.cachePool.pool),h!==u&&(o.flags|=2048)),r!==e&&r&&(i.child.flags|=8192),Wc(i,i.updateQueue),Ke(i),null);case 4:return Vt(),e===null&&$h(i.stateNode.containerInfo),Ke(i),null;case 10:return la(i.type),Ke(i),null;case 19:if(nt(un),o=i.memoizedState,o===null)return Ke(i),null;if(u=(i.flags&128)!==0,h=o.rendering,h===null)if(u)_l(o,!1);else{if(on!==0||e!==null&&(e.flags&128)!==0)for(e=i.child;e!==null;){if(h=Oc(e),h!==null){for(i.flags|=128,_l(o,!1),e=h.updateQueue,i.updateQueue=e,Wc(i,e),i.subtreeFlags=0,e=r,r=i.child;r!==null;)lg(r,e),r=r.sibling;return St(un,un.current&1|2),Ce&&ra(i,o.treeForkCount),i.child}e=e.sibling}o.tail!==null&&pt()>Jc&&(i.flags|=128,u=!0,_l(o,!1),i.lanes=4194304)}else{if(!u)if(e=Oc(h),e!==null){if(i.flags|=128,u=!0,e=e.updateQueue,i.updateQueue=e,Wc(i,e),_l(o,!0),o.tail===null&&o.tailMode==="hidden"&&!h.alternate&&!Ce)return Ke(i),null}else 2*pt()-o.renderingStartTime>Jc&&r!==536870912&&(i.flags|=128,u=!0,_l(o,!1),i.lanes=4194304);o.isBackwards?(h.sibling=i.child,i.child=h):(e=o.last,e!==null?e.sibling=h:i.child=h,o.last=h)}return o.tail!==null?(e=o.tail,o.rendering=e,o.tail=e.sibling,o.renderingStartTime=pt(),e.sibling=null,r=un.current,St(un,u?r&1|2:r&1),Ce&&ra(i,o.treeForkCount),e):(Ke(i),null);case 22:case 23:return ci(i),th(),o=i.memoizedState!==null,e!==null?e.memoizedState!==null!==o&&(i.flags|=8192):o&&(i.flags|=8192),o?(r&536870912)!==0&&(i.flags&128)===0&&(Ke(i),i.subtreeFlags&6&&(i.flags|=8192)):Ke(i),r=i.updateQueue,r!==null&&Wc(i,r.retryQueue),r=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),o=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(o=i.memoizedState.cachePool.pool),o!==r&&(i.flags|=2048),e!==null&&nt(Fs),null;case 24:return r=null,e!==null&&(r=e.memoizedState.cache),i.memoizedState.cache!==r&&(i.flags|=2048),la(dn),Ke(i),null;case 25:return null;case 30:return null}throw Error(a(156,i.tag))}function aM(e,i){switch(Ff(i),i.tag){case 1:return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 3:return la(dn),Vt(),e=i.flags,(e&65536)!==0&&(e&128)===0?(i.flags=e&-65537|128,i):null;case 26:case 27:case 5:return He(i),null;case 31:if(i.memoizedState!==null){if(ci(i),i.alternate===null)throw Error(a(340));zs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 13:if(ci(i),e=i.memoizedState,e!==null&&e.dehydrated!==null){if(i.alternate===null)throw Error(a(340));zs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 19:return nt(un),null;case 4:return Vt(),null;case 10:return la(i.type),null;case 22:case 23:return ci(i),th(),e!==null&&nt(Fs),e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 24:return la(dn),null;case 25:return null;default:return null}}function Pv(e,i){switch(Ff(i),i.tag){case 3:la(dn),Vt();break;case 26:case 27:case 5:He(i);break;case 4:Vt();break;case 31:i.memoizedState!==null&&ci(i);break;case 13:ci(i);break;case 19:nt(un);break;case 10:la(i.type);break;case 22:case 23:ci(i),th(),e!==null&&nt(Fs);break;case 24:la(dn)}}function yl(e,i){try{var r=i.updateQueue,o=r!==null?r.lastEffect:null;if(o!==null){var u=o.next;r=u;do{if((r.tag&e)===e){o=void 0;var h=r.create,S=r.inst;o=h(),S.destroy=o}r=r.next}while(r!==u)}}catch(T){Fe(i,i.return,T)}}function Ya(e,i,r){try{var o=i.updateQueue,u=o!==null?o.lastEffect:null;if(u!==null){var h=u.next;o=h;do{if((o.tag&e)===e){var S=o.inst,T=S.destroy;if(T!==void 0){S.destroy=void 0,u=i;var B=r,et=T;try{et()}catch(dt){Fe(u,B,dt)}}}o=o.next}while(o!==h)}}catch(dt){Fe(i,i.return,dt)}}function zv(e){var i=e.updateQueue;if(i!==null){var r=e.stateNode;try{Ag(i,r)}catch(o){Fe(e,e.return,o)}}}function Iv(e,i,r){r.props=Xs(e.type,e.memoizedProps),r.state=e.memoizedState;try{r.componentWillUnmount()}catch(o){Fe(e,i,o)}}function xl(e,i){try{var r=e.ref;if(r!==null){switch(e.tag){case 26:case 27:case 5:var o=e.stateNode;break;case 30:o=e.stateNode;break;default:o=e.stateNode}typeof r=="function"?e.refCleanup=r(o):r.current=o}}catch(u){Fe(e,i,u)}}function Wi(e,i){var r=e.ref,o=e.refCleanup;if(r!==null)if(typeof o=="function")try{o()}catch(u){Fe(e,i,u)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof r=="function")try{r(null)}catch(u){Fe(e,i,u)}else r.current=null}function Bv(e){var i=e.type,r=e.memoizedProps,o=e.stateNode;try{t:switch(i){case"button":case"input":case"select":case"textarea":r.autoFocus&&o.focus();break t;case"img":r.src?o.src=r.src:r.srcSet&&(o.srcset=r.srcSet)}}catch(u){Fe(e,e.return,u)}}function Nh(e,i,r){try{var o=e.stateNode;AM(o,e.type,r,i),o[wn]=i}catch(u){Fe(e,e.return,u)}}function Fv(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&es(e.type)||e.tag===4}function Lh(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||Fv(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&es(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Oh(e,i,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,i?(r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r).insertBefore(e,i):(i=r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r,i.appendChild(e),r=r._reactRootContainer,r!=null||i.onclick!==null||(i.onclick=ia));else if(o!==4&&(o===27&&es(e.type)&&(r=e.stateNode,i=null),e=e.child,e!==null))for(Oh(e,i,r),e=e.sibling;e!==null;)Oh(e,i,r),e=e.sibling}function Yc(e,i,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,i?r.insertBefore(e,i):r.appendChild(e);else if(o!==4&&(o===27&&es(e.type)&&(r=e.stateNode),e=e.child,e!==null))for(Yc(e,i,r),e=e.sibling;e!==null;)Yc(e,i,r),e=e.sibling}function Hv(e){var i=e.stateNode,r=e.memoizedProps;try{for(var o=e.type,u=i.attributes;u.length;)i.removeAttributeNode(u[0]);Ln(i,o,r),i[sn]=e,i[wn]=r}catch(h){Fe(e,e.return,h)}}var da=!1,gn=!1,Ph=!1,Gv=typeof WeakSet=="function"?WeakSet:Set,bn=null;function sM(e,i){if(e=e.containerInfo,nd=mu,e=$m(e),Rf(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else t:{r=(r=e.ownerDocument)&&r.defaultView||window;var o=r.getSelection&&r.getSelection();if(o&&o.rangeCount!==0){r=o.anchorNode;var u=o.anchorOffset,h=o.focusNode;o=o.focusOffset;try{r.nodeType,h.nodeType}catch{r=null;break t}var S=0,T=-1,B=-1,et=0,dt=0,_t=e,it=null;e:for(;;){for(var lt;_t!==r||u!==0&&_t.nodeType!==3||(T=S+u),_t!==h||o!==0&&_t.nodeType!==3||(B=S+o),_t.nodeType===3&&(S+=_t.nodeValue.length),(lt=_t.firstChild)!==null;)it=_t,_t=lt;for(;;){if(_t===e)break e;if(it===r&&++et===u&&(T=S),it===h&&++dt===o&&(B=S),(lt=_t.nextSibling)!==null)break;_t=it,it=_t.parentNode}_t=lt}r=T===-1||B===-1?null:{start:T,end:B}}else r=null}r=r||{start:0,end:0}}else r=null;for(id={focusedElem:e,selectionRange:r},mu=!1,bn=i;bn!==null;)if(i=bn,e=i.child,(i.subtreeFlags&1028)!==0&&e!==null)e.return=i,bn=e;else for(;bn!==null;){switch(i=bn,h=i.alternate,e=i.flags,i.tag){case 0:if((e&4)!==0&&(e=i.updateQueue,e=e!==null?e.events:null,e!==null))for(r=0;r<e.length;r++)u=e[r],u.ref.impl=u.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&h!==null){e=void 0,r=i,u=h.memoizedProps,h=h.memoizedState,o=r.stateNode;try{var Gt=Xs(r.type,u);e=o.getSnapshotBeforeUpdate(Gt,h),o.__reactInternalSnapshotBeforeUpdate=e}catch(ee){Fe(r,r.return,ee)}}break;case 3:if((e&1024)!==0){if(e=i.stateNode.containerInfo,r=e.nodeType,r===9)rd(e);else if(r===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":rd(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(a(163))}if(e=i.sibling,e!==null){e.return=i.return,bn=e;break}bn=i.return}}function Vv(e,i,r){var o=r.flags;switch(r.tag){case 0:case 11:case 15:ma(e,r),o&4&&yl(5,r);break;case 1:if(ma(e,r),o&4)if(e=r.stateNode,i===null)try{e.componentDidMount()}catch(S){Fe(r,r.return,S)}else{var u=Xs(r.type,i.memoizedProps);i=i.memoizedState;try{e.componentDidUpdate(u,i,e.__reactInternalSnapshotBeforeUpdate)}catch(S){Fe(r,r.return,S)}}o&64&&zv(r),o&512&&xl(r,r.return);break;case 3:if(ma(e,r),o&64&&(e=r.updateQueue,e!==null)){if(i=null,r.child!==null)switch(r.child.tag){case 27:case 5:i=r.child.stateNode;break;case 1:i=r.child.stateNode}try{Ag(e,i)}catch(S){Fe(r,r.return,S)}}break;case 27:i===null&&o&4&&Hv(r);case 26:case 5:ma(e,r),i===null&&o&4&&Bv(r),o&512&&xl(r,r.return);break;case 12:ma(e,r);break;case 31:ma(e,r),o&4&&jv(e,r);break;case 13:ma(e,r),o&4&&qv(e,r),o&64&&(e=r.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(r=pM.bind(null,r),OM(e,r))));break;case 22:if(o=r.memoizedState!==null||da,!o){i=i!==null&&i.memoizedState!==null||gn,u=da;var h=gn;da=o,(gn=i)&&!h?ga(e,r,(r.subtreeFlags&8772)!==0):ma(e,r),da=u,gn=h}break;case 30:break;default:ma(e,r)}}function kv(e){var i=e.alternate;i!==null&&(e.alternate=null,kv(i)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(i=e.stateNode,i!==null&&R(i)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var tn=null,Zn=!1;function pa(e,i,r){for(r=r.child;r!==null;)Xv(e,i,r),r=r.sibling}function Xv(e,i,r){if(qt&&typeof qt.onCommitFiberUnmount=="function")try{qt.onCommitFiberUnmount(Zt,r)}catch{}switch(r.tag){case 26:gn||Wi(r,i),pa(e,i,r),r.memoizedState?r.memoizedState.count--:r.stateNode&&(r=r.stateNode,r.parentNode.removeChild(r));break;case 27:gn||Wi(r,i);var o=tn,u=Zn;es(r.type)&&(tn=r.stateNode,Zn=!1),pa(e,i,r),wl(r.stateNode),tn=o,Zn=u;break;case 5:gn||Wi(r,i);case 6:if(o=tn,u=Zn,tn=null,pa(e,i,r),tn=o,Zn=u,tn!==null)if(Zn)try{(tn.nodeType===9?tn.body:tn.nodeName==="HTML"?tn.ownerDocument.body:tn).removeChild(r.stateNode)}catch(h){Fe(r,i,h)}else try{tn.removeChild(r.stateNode)}catch(h){Fe(r,i,h)}break;case 18:tn!==null&&(Zn?(e=tn,z0(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,r.stateNode),Kr(e)):z0(tn,r.stateNode));break;case 4:o=tn,u=Zn,tn=r.stateNode.containerInfo,Zn=!0,pa(e,i,r),tn=o,Zn=u;break;case 0:case 11:case 14:case 15:Ya(2,r,i),gn||Ya(4,r,i),pa(e,i,r);break;case 1:gn||(Wi(r,i),o=r.stateNode,typeof o.componentWillUnmount=="function"&&Iv(r,i,o)),pa(e,i,r);break;case 21:pa(e,i,r);break;case 22:gn=(o=gn)||r.memoizedState!==null,pa(e,i,r),gn=o;break;default:pa(e,i,r)}}function jv(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{Kr(e)}catch(r){Fe(i,i.return,r)}}}function qv(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Kr(e)}catch(r){Fe(i,i.return,r)}}function rM(e){switch(e.tag){case 31:case 13:case 19:var i=e.stateNode;return i===null&&(i=e.stateNode=new Gv),i;case 22:return e=e.stateNode,i=e._retryCache,i===null&&(i=e._retryCache=new Gv),i;default:throw Error(a(435,e.tag))}}function Qc(e,i){var r=rM(e);i.forEach(function(o){if(!r.has(o)){r.add(o);var u=mM.bind(null,e,o);o.then(u,u)}})}function Kn(e,i){var r=i.deletions;if(r!==null)for(var o=0;o<r.length;o++){var u=r[o],h=e,S=i,T=S;t:for(;T!==null;){switch(T.tag){case 27:if(es(T.type)){tn=T.stateNode,Zn=!1;break t}break;case 5:tn=T.stateNode,Zn=!1;break t;case 3:case 4:tn=T.stateNode.containerInfo,Zn=!0;break t}T=T.return}if(tn===null)throw Error(a(160));Xv(h,S,u),tn=null,Zn=!1,h=u.alternate,h!==null&&(h.return=null),u.return=null}if(i.subtreeFlags&13886)for(i=i.child;i!==null;)Wv(i,e),i=i.sibling}var Ni=null;function Wv(e,i){var r=e.alternate,o=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Kn(i,e),Jn(e),o&4&&(Ya(3,e,e.return),yl(3,e),Ya(5,e,e.return));break;case 1:Kn(i,e),Jn(e),o&512&&(gn||r===null||Wi(r,r.return)),o&64&&da&&(e=e.updateQueue,e!==null&&(o=e.callbacks,o!==null&&(r=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=r===null?o:r.concat(o))));break;case 26:var u=Ni;if(Kn(i,e),Jn(e),o&512&&(gn||r===null||Wi(r,r.return)),o&4){var h=r!==null?r.memoizedState:null;if(o=e.memoizedState,r===null)if(o===null)if(e.stateNode===null){t:{o=e.type,r=e.memoizedProps,u=u.ownerDocument||u;e:switch(o){case"title":h=u.getElementsByTagName("title")[0],(!h||h[ws]||h[sn]||h.namespaceURI==="http://www.w3.org/2000/svg"||h.hasAttribute("itemprop"))&&(h=u.createElement(o),u.head.insertBefore(h,u.querySelector("head > title"))),Ln(h,o,r),h[sn]=e,xt(h),o=h;break t;case"link":var S=W0("link","href",u).get(o+(r.href||""));if(S){for(var T=0;T<S.length;T++)if(h=S[T],h.getAttribute("href")===(r.href==null||r.href===""?null:r.href)&&h.getAttribute("rel")===(r.rel==null?null:r.rel)&&h.getAttribute("title")===(r.title==null?null:r.title)&&h.getAttribute("crossorigin")===(r.crossOrigin==null?null:r.crossOrigin)){S.splice(T,1);break e}}h=u.createElement(o),Ln(h,o,r),u.head.appendChild(h);break;case"meta":if(S=W0("meta","content",u).get(o+(r.content||""))){for(T=0;T<S.length;T++)if(h=S[T],h.getAttribute("content")===(r.content==null?null:""+r.content)&&h.getAttribute("name")===(r.name==null?null:r.name)&&h.getAttribute("property")===(r.property==null?null:r.property)&&h.getAttribute("http-equiv")===(r.httpEquiv==null?null:r.httpEquiv)&&h.getAttribute("charset")===(r.charSet==null?null:r.charSet)){S.splice(T,1);break e}}h=u.createElement(o),Ln(h,o,r),u.head.appendChild(h);break;default:throw Error(a(468,o))}h[sn]=e,xt(h),o=h}e.stateNode=o}else Y0(u,e.type,e.stateNode);else e.stateNode=q0(u,o,e.memoizedProps);else h!==o?(h===null?r.stateNode!==null&&(r=r.stateNode,r.parentNode.removeChild(r)):h.count--,o===null?Y0(u,e.type,e.stateNode):q0(u,o,e.memoizedProps)):o===null&&e.stateNode!==null&&Nh(e,e.memoizedProps,r.memoizedProps)}break;case 27:Kn(i,e),Jn(e),o&512&&(gn||r===null||Wi(r,r.return)),r!==null&&o&4&&Nh(e,e.memoizedProps,r.memoizedProps);break;case 5:if(Kn(i,e),Jn(e),o&512&&(gn||r===null||Wi(r,r.return)),e.flags&32){u=e.stateNode;try{xr(u,"")}catch(Gt){Fe(e,e.return,Gt)}}o&4&&e.stateNode!=null&&(u=e.memoizedProps,Nh(e,u,r!==null?r.memoizedProps:u)),o&1024&&(Ph=!0);break;case 6:if(Kn(i,e),Jn(e),o&4){if(e.stateNode===null)throw Error(a(162));o=e.memoizedProps,r=e.stateNode;try{r.nodeValue=o}catch(Gt){Fe(e,e.return,Gt)}}break;case 3:if(fu=null,u=Ni,Ni=cu(i.containerInfo),Kn(i,e),Ni=u,Jn(e),o&4&&r!==null&&r.memoizedState.isDehydrated)try{Kr(i.containerInfo)}catch(Gt){Fe(e,e.return,Gt)}Ph&&(Ph=!1,Yv(e));break;case 4:o=Ni,Ni=cu(e.stateNode.containerInfo),Kn(i,e),Jn(e),Ni=o;break;case 12:Kn(i,e),Jn(e);break;case 31:Kn(i,e),Jn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Qc(e,o)));break;case 13:Kn(i,e),Jn(e),e.child.flags&8192&&e.memoizedState!==null!=(r!==null&&r.memoizedState!==null)&&(Kc=pt()),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Qc(e,o)));break;case 22:u=e.memoizedState!==null;var B=r!==null&&r.memoizedState!==null,et=da,dt=gn;if(da=et||u,gn=dt||B,Kn(i,e),gn=dt,da=et,Jn(e),o&8192)t:for(i=e.stateNode,i._visibility=u?i._visibility&-2:i._visibility|1,u&&(r===null||B||da||gn||js(e)),r=null,i=e;;){if(i.tag===5||i.tag===26){if(r===null){B=r=i;try{if(h=B.stateNode,u)S=h.style,typeof S.setProperty=="function"?S.setProperty("display","none","important"):S.display="none";else{T=B.stateNode;var _t=B.memoizedProps.style,it=_t!=null&&_t.hasOwnProperty("display")?_t.display:null;T.style.display=it==null||typeof it=="boolean"?"":(""+it).trim()}}catch(Gt){Fe(B,B.return,Gt)}}}else if(i.tag===6){if(r===null){B=i;try{B.stateNode.nodeValue=u?"":B.memoizedProps}catch(Gt){Fe(B,B.return,Gt)}}}else if(i.tag===18){if(r===null){B=i;try{var lt=B.stateNode;u?I0(lt,!0):I0(B.stateNode,!1)}catch(Gt){Fe(B,B.return,Gt)}}}else if((i.tag!==22&&i.tag!==23||i.memoizedState===null||i===e)&&i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break t;for(;i.sibling===null;){if(i.return===null||i.return===e)break t;r===i&&(r=null),i=i.return}r===i&&(r=null),i.sibling.return=i.return,i=i.sibling}o&4&&(o=e.updateQueue,o!==null&&(r=o.retryQueue,r!==null&&(o.retryQueue=null,Qc(e,r))));break;case 19:Kn(i,e),Jn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Qc(e,o)));break;case 30:break;case 21:break;default:Kn(i,e),Jn(e)}}function Jn(e){var i=e.flags;if(i&2){try{for(var r,o=e.return;o!==null;){if(Fv(o)){r=o;break}o=o.return}if(r==null)throw Error(a(160));switch(r.tag){case 27:var u=r.stateNode,h=Lh(e);Yc(e,h,u);break;case 5:var S=r.stateNode;r.flags&32&&(xr(S,""),r.flags&=-33);var T=Lh(e);Yc(e,T,S);break;case 3:case 4:var B=r.stateNode.containerInfo,et=Lh(e);Oh(e,et,B);break;default:throw Error(a(161))}}catch(dt){Fe(e,e.return,dt)}e.flags&=-3}i&4096&&(e.flags&=-4097)}function Yv(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var i=e;Yv(i),i.tag===5&&i.flags&1024&&i.stateNode.reset(),e=e.sibling}}function ma(e,i){if(i.subtreeFlags&8772)for(i=i.child;i!==null;)Vv(e,i.alternate,i),i=i.sibling}function js(e){for(e=e.child;e!==null;){var i=e;switch(i.tag){case 0:case 11:case 14:case 15:Ya(4,i,i.return),js(i);break;case 1:Wi(i,i.return);var r=i.stateNode;typeof r.componentWillUnmount=="function"&&Iv(i,i.return,r),js(i);break;case 27:wl(i.stateNode);case 26:case 5:Wi(i,i.return),js(i);break;case 22:i.memoizedState===null&&js(i);break;case 30:js(i);break;default:js(i)}e=e.sibling}}function ga(e,i,r){for(r=r&&(i.subtreeFlags&8772)!==0,i=i.child;i!==null;){var o=i.alternate,u=e,h=i,S=h.flags;switch(h.tag){case 0:case 11:case 15:ga(u,h,r),yl(4,h);break;case 1:if(ga(u,h,r),o=h,u=o.stateNode,typeof u.componentDidMount=="function")try{u.componentDidMount()}catch(et){Fe(o,o.return,et)}if(o=h,u=o.updateQueue,u!==null){var T=o.stateNode;try{var B=u.shared.hiddenCallbacks;if(B!==null)for(u.shared.hiddenCallbacks=null,u=0;u<B.length;u++)Tg(B[u],T)}catch(et){Fe(o,o.return,et)}}r&&S&64&&zv(h),xl(h,h.return);break;case 27:Hv(h);case 26:case 5:ga(u,h,r),r&&o===null&&S&4&&Bv(h),xl(h,h.return);break;case 12:ga(u,h,r);break;case 31:ga(u,h,r),r&&S&4&&jv(u,h);break;case 13:ga(u,h,r),r&&S&4&&qv(u,h);break;case 22:h.memoizedState===null&&ga(u,h,r),xl(h,h.return);break;case 30:break;default:ga(u,h,r)}i=i.sibling}}function zh(e,i){var r=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),e=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(e=i.memoizedState.cachePool.pool),e!==r&&(e!=null&&e.refCount++,r!=null&&rl(r))}function Ih(e,i){e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&rl(e))}function Li(e,i,r,o){if(i.subtreeFlags&10256)for(i=i.child;i!==null;)Qv(e,i,r,o),i=i.sibling}function Qv(e,i,r,o){var u=i.flags;switch(i.tag){case 0:case 11:case 15:Li(e,i,r,o),u&2048&&yl(9,i);break;case 1:Li(e,i,r,o);break;case 3:Li(e,i,r,o),u&2048&&(e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&rl(e)));break;case 12:if(u&2048){Li(e,i,r,o),e=i.stateNode;try{var h=i.memoizedProps,S=h.id,T=h.onPostCommit;typeof T=="function"&&T(S,i.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(B){Fe(i,i.return,B)}}else Li(e,i,r,o);break;case 31:Li(e,i,r,o);break;case 13:Li(e,i,r,o);break;case 23:break;case 22:h=i.stateNode,S=i.alternate,i.memoizedState!==null?h._visibility&2?Li(e,i,r,o):Sl(e,i):h._visibility&2?Li(e,i,r,o):(h._visibility|=2,Hr(e,i,r,o,(i.subtreeFlags&10256)!==0||!1)),u&2048&&zh(S,i);break;case 24:Li(e,i,r,o),u&2048&&Ih(i.alternate,i);break;default:Li(e,i,r,o)}}function Hr(e,i,r,o,u){for(u=u&&((i.subtreeFlags&10256)!==0||!1),i=i.child;i!==null;){var h=e,S=i,T=r,B=o,et=S.flags;switch(S.tag){case 0:case 11:case 15:Hr(h,S,T,B,u),yl(8,S);break;case 23:break;case 22:var dt=S.stateNode;S.memoizedState!==null?dt._visibility&2?Hr(h,S,T,B,u):Sl(h,S):(dt._visibility|=2,Hr(h,S,T,B,u)),u&&et&2048&&zh(S.alternate,S);break;case 24:Hr(h,S,T,B,u),u&&et&2048&&Ih(S.alternate,S);break;default:Hr(h,S,T,B,u)}i=i.sibling}}function Sl(e,i){if(i.subtreeFlags&10256)for(i=i.child;i!==null;){var r=e,o=i,u=o.flags;switch(o.tag){case 22:Sl(r,o),u&2048&&zh(o.alternate,o);break;case 24:Sl(r,o),u&2048&&Ih(o.alternate,o);break;default:Sl(r,o)}i=i.sibling}}var Ml=8192;function Gr(e,i,r){if(e.subtreeFlags&Ml)for(e=e.child;e!==null;)Zv(e,i,r),e=e.sibling}function Zv(e,i,r){switch(e.tag){case 26:Gr(e,i,r),e.flags&Ml&&e.memoizedState!==null&&qM(r,Ni,e.memoizedState,e.memoizedProps);break;case 5:Gr(e,i,r);break;case 3:case 4:var o=Ni;Ni=cu(e.stateNode.containerInfo),Gr(e,i,r),Ni=o;break;case 22:e.memoizedState===null&&(o=e.alternate,o!==null&&o.memoizedState!==null?(o=Ml,Ml=16777216,Gr(e,i,r),Ml=o):Gr(e,i,r));break;default:Gr(e,i,r)}}function Kv(e){var i=e.alternate;if(i!==null&&(e=i.child,e!==null)){i.child=null;do i=e.sibling,e.sibling=null,e=i;while(e!==null)}}function El(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var o=i[r];bn=o,$v(o,e)}Kv(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)Jv(e),e=e.sibling}function Jv(e){switch(e.tag){case 0:case 11:case 15:El(e),e.flags&2048&&Ya(9,e,e.return);break;case 3:El(e);break;case 12:El(e);break;case 22:var i=e.stateNode;e.memoizedState!==null&&i._visibility&2&&(e.return===null||e.return.tag!==13)?(i._visibility&=-3,Zc(e)):El(e);break;default:El(e)}}function Zc(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var o=i[r];bn=o,$v(o,e)}Kv(e)}for(e=e.child;e!==null;){switch(i=e,i.tag){case 0:case 11:case 15:Ya(8,i,i.return),Zc(i);break;case 22:r=i.stateNode,r._visibility&2&&(r._visibility&=-3,Zc(i));break;default:Zc(i)}e=e.sibling}}function $v(e,i){for(;bn!==null;){var r=bn;switch(r.tag){case 0:case 11:case 15:Ya(8,r,i);break;case 23:case 22:if(r.memoizedState!==null&&r.memoizedState.cachePool!==null){var o=r.memoizedState.cachePool.pool;o!=null&&o.refCount++}break;case 24:rl(r.memoizedState.cache)}if(o=r.child,o!==null)o.return=r,bn=o;else t:for(r=e;bn!==null;){o=bn;var u=o.sibling,h=o.return;if(kv(o),o===r){bn=null;break t}if(u!==null){u.return=h,bn=u;break t}bn=h}}}var oM={getCacheForType:function(e){var i=Un(dn),r=i.data.get(e);return r===void 0&&(r=e(),i.data.set(e,r)),r},cacheSignal:function(){return Un(dn).controller.signal}},lM=typeof WeakMap=="function"?WeakMap:Map,Pe=0,Ye=null,ye=null,be=0,Be=0,ui=null,Qa=!1,Vr=!1,Bh=!1,va=0,on=0,Za=0,qs=0,Fh=0,fi=0,kr=0,bl=null,$n=null,Hh=!1,Kc=0,t0=0,Jc=1/0,$c=null,Ka=null,xn=0,Ja=null,Xr=null,_a=0,Gh=0,Vh=null,e0=null,Tl=0,kh=null;function hi(){return(Pe&2)!==0&&be!==0?be&-be:z.T!==null?Qh():Wo()}function n0(){if(fi===0)if((be&536870912)===0||Ce){var e=ht;ht<<=1,(ht&3932160)===0&&(ht=262144),fi=e}else fi=536870912;return e=li.current,e!==null&&(e.flags|=32),fi}function ti(e,i,r){(e===Ye&&(Be===2||Be===9)||e.cancelPendingCommit!==null)&&(jr(e,0),$a(e,be,fi,!1)),Rn(e,r),((Pe&2)===0||e!==Ye)&&(e===Ye&&((Pe&2)===0&&(qs|=r),on===4&&$a(e,be,fi,!1)),Yi(e))}function i0(e,i,r){if((Pe&6)!==0)throw Error(a(327));var o=!r&&(i&127)===0&&(i&e.expiredLanes)===0||ie(e,i),u=o?fM(e,i):jh(e,i,!0),h=o;do{if(u===0){Vr&&!o&&$a(e,i,0,!1);break}else{if(r=e.current.alternate,h&&!cM(r)){u=jh(e,i,!1),h=!1;continue}if(u===2){if(h=i,e.errorRecoveryDisabledLanes&h)var S=0;else S=e.pendingLanes&-536870913,S=S!==0?S:S&536870912?536870912:0;if(S!==0){i=S;t:{var T=e;u=bl;var B=T.current.memoizedState.isDehydrated;if(B&&(jr(T,S).flags|=256),S=jh(T,S,!1),S!==2){if(Bh&&!B){T.errorRecoveryDisabledLanes|=h,qs|=h,u=4;break t}h=$n,$n=u,h!==null&&($n===null?$n=h:$n.push.apply($n,h))}u=S}if(h=!1,u!==2)continue}}if(u===1){jr(e,0),$a(e,i,0,!0);break}t:{switch(o=e,h=u,h){case 0:case 1:throw Error(a(345));case 4:if((i&4194048)!==i)break;case 6:$a(o,i,fi,!Qa);break t;case 2:$n=null;break;case 3:case 5:break;default:throw Error(a(329))}if((i&62914560)===i&&(u=Kc+300-pt(),10<u)){if($a(o,i,fi,!Qa),Ut(o,0,!0)!==0)break t;_a=i,o.timeoutHandle=O0(a0.bind(null,o,r,$n,$c,Hh,i,fi,qs,kr,Qa,h,"Throttled",-0,0),u);break t}a0(o,r,$n,$c,Hh,i,fi,qs,kr,Qa,h,null,-0,0)}}break}while(!0);Yi(e)}function a0(e,i,r,o,u,h,S,T,B,et,dt,_t,it,lt){if(e.timeoutHandle=-1,_t=i.subtreeFlags,_t&8192||(_t&16785408)===16785408){_t={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:ia},Zv(i,h,_t);var Gt=(h&62914560)===h?Kc-pt():(h&4194048)===h?t0-pt():0;if(Gt=WM(_t,Gt),Gt!==null){_a=h,e.cancelPendingCommit=Gt(h0.bind(null,e,i,h,r,o,u,S,T,B,dt,_t,null,it,lt)),$a(e,h,S,!et);return}}h0(e,i,h,r,o,u,S,T,B)}function cM(e){for(var i=e;;){var r=i.tag;if((r===0||r===11||r===15)&&i.flags&16384&&(r=i.updateQueue,r!==null&&(r=r.stores,r!==null)))for(var o=0;o<r.length;o++){var u=r[o],h=u.getSnapshot;u=u.value;try{if(!ri(h(),u))return!1}catch{return!1}}if(r=i.child,i.subtreeFlags&16384&&r!==null)r.return=i,i=r;else{if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return!0;i=i.return}i.sibling.return=i.return,i=i.sibling}}return!0}function $a(e,i,r,o){i&=~Fh,i&=~qs,e.suspendedLanes|=i,e.pingedLanes&=~i,o&&(e.warmLanes|=i),o=e.expirationTimes;for(var u=i;0<u;){var h=31-ne(u),S=1<<h;o[h]=-1,u&=~S}r!==0&&jo(e,r,i)}function tu(){return(Pe&6)===0?(Al(0),!1):!0}function Xh(){if(ye!==null){if(Be===0)var e=ye.return;else e=ye,oa=Is=null,rh(e),Pr=null,ll=0,e=ye;for(;e!==null;)Pv(e.alternate,e),e=e.return;ye=null}}function jr(e,i){var r=e.timeoutHandle;r!==-1&&(e.timeoutHandle=-1,wM(r)),r=e.cancelPendingCommit,r!==null&&(e.cancelPendingCommit=null,r()),_a=0,Xh(),Ye=e,ye=r=sa(e.current,null),be=i,Be=0,ui=null,Qa=!1,Vr=ie(e,i),Bh=!1,kr=fi=Fh=qs=Za=on=0,$n=bl=null,Hh=!1,(i&8)!==0&&(i|=i&32);var o=e.entangledLanes;if(o!==0)for(e=e.entanglements,o&=i;0<o;){var u=31-ne(o),h=1<<u;i|=e[u],o&=~h}return va=i,Sc(),r}function s0(e,i){ce=null,z.H=gl,i===Or||i===wc?(i=Sg(),Be=3):i===Yf?(i=Sg(),Be=4):Be=i===Mh?8:i!==null&&typeof i=="object"&&typeof i.then=="function"?6:1,ui=i,ye===null&&(on=1,kc(e,xi(i,e.current)))}function r0(){var e=li.current;return e===null?!0:(be&4194048)===be?bi===null:(be&62914560)===be||(be&536870912)!==0?e===bi:!1}function o0(){var e=z.H;return z.H=gl,e===null?gl:e}function l0(){var e=z.A;return z.A=oM,e}function eu(){on=4,Qa||(be&4194048)!==be&&li.current!==null||(Vr=!0),(Za&134217727)===0&&(qs&134217727)===0||Ye===null||$a(Ye,be,fi,!1)}function jh(e,i,r){var o=Pe;Pe|=2;var u=o0(),h=l0();(Ye!==e||be!==i)&&($c=null,jr(e,i)),i=!1;var S=on;t:do try{if(Be!==0&&ye!==null){var T=ye,B=ui;switch(Be){case 8:Xh(),S=6;break t;case 3:case 2:case 9:case 6:li.current===null&&(i=!0);var et=Be;if(Be=0,ui=null,qr(e,T,B,et),r&&Vr){S=0;break t}break;default:et=Be,Be=0,ui=null,qr(e,T,B,et)}}uM(),S=on;break}catch(dt){s0(e,dt)}while(!0);return i&&e.shellSuspendCounter++,oa=Is=null,Pe=o,z.H=u,z.A=h,ye===null&&(Ye=null,be=0,Sc()),S}function uM(){for(;ye!==null;)c0(ye)}function fM(e,i){var r=Pe;Pe|=2;var o=o0(),u=l0();Ye!==e||be!==i?($c=null,Jc=pt()+500,jr(e,i)):Vr=ie(e,i);t:do try{if(Be!==0&&ye!==null){i=ye;var h=ui;e:switch(Be){case 1:Be=0,ui=null,qr(e,i,h,1);break;case 2:case 9:if(yg(h)){Be=0,ui=null,u0(i);break}i=function(){Be!==2&&Be!==9||Ye!==e||(Be=7),Yi(e)},h.then(i,i);break t;case 3:Be=7;break t;case 4:Be=5;break t;case 7:yg(h)?(Be=0,ui=null,u0(i)):(Be=0,ui=null,qr(e,i,h,7));break;case 5:var S=null;switch(ye.tag){case 26:S=ye.memoizedState;case 5:case 27:var T=ye;if(S?Q0(S):T.stateNode.complete){Be=0,ui=null;var B=T.sibling;if(B!==null)ye=B;else{var et=T.return;et!==null?(ye=et,nu(et)):ye=null}break e}}Be=0,ui=null,qr(e,i,h,5);break;case 6:Be=0,ui=null,qr(e,i,h,6);break;case 8:Xh(),on=6;break t;default:throw Error(a(462))}}hM();break}catch(dt){s0(e,dt)}while(!0);return oa=Is=null,z.H=o,z.A=u,Pe=r,ye!==null?0:(Ye=null,be=0,Sc(),on)}function hM(){for(;ye!==null&&!A();)c0(ye)}function c0(e){var i=Lv(e.alternate,e,va);e.memoizedProps=e.pendingProps,i===null?nu(e):ye=i}function u0(e){var i=e,r=i.alternate;switch(i.tag){case 15:case 0:i=Cv(r,i,i.pendingProps,i.type,void 0,be);break;case 11:i=Cv(r,i,i.pendingProps,i.type.render,i.ref,be);break;case 5:rh(i);default:Pv(r,i),i=ye=lg(i,va),i=Lv(r,i,va)}e.memoizedProps=e.pendingProps,i===null?nu(e):ye=i}function qr(e,i,r,o){oa=Is=null,rh(i),Pr=null,ll=0;var u=i.return;try{if(tM(e,u,i,r,be)){on=1,kc(e,xi(r,e.current)),ye=null;return}}catch(h){if(u!==null)throw ye=u,h;on=1,kc(e,xi(r,e.current)),ye=null;return}i.flags&32768?(Ce||o===1?e=!0:Vr||(be&536870912)!==0?e=!1:(Qa=e=!0,(o===2||o===9||o===3||o===6)&&(o=li.current,o!==null&&o.tag===13&&(o.flags|=16384))),f0(i,e)):nu(i)}function nu(e){var i=e;do{if((i.flags&32768)!==0){f0(i,Qa);return}e=i.return;var r=iM(i.alternate,i,va);if(r!==null){ye=r;return}if(i=i.sibling,i!==null){ye=i;return}ye=i=e}while(i!==null);on===0&&(on=5)}function f0(e,i){do{var r=aM(e.alternate,e);if(r!==null){r.flags&=32767,ye=r;return}if(r=e.return,r!==null&&(r.flags|=32768,r.subtreeFlags=0,r.deletions=null),!i&&(e=e.sibling,e!==null)){ye=e;return}ye=e=r}while(e!==null);on=6,ye=null}function h0(e,i,r,o,u,h,S,T,B){e.cancelPendingCommit=null;do iu();while(xn!==0);if((Pe&6)!==0)throw Error(a(327));if(i!==null){if(i===e.current)throw Error(a(177));if(h=i.lanes|i.childLanes,h|=Lf,wi(e,r,h,S,T,B),e===Ye&&(ye=Ye=null,be=0),Xr=i,Ja=e,_a=r,Gh=h,Vh=u,e0=o,(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,gM(Dt,function(){return v0(),null})):(e.callbackNode=null,e.callbackPriority=0),o=(i.flags&13878)!==0,(i.subtreeFlags&13878)!==0||o){o=z.T,z.T=null,u=Z.p,Z.p=2,S=Pe,Pe|=4;try{sM(e,i,r)}finally{Pe=S,Z.p=u,z.T=o}}xn=1,d0(),p0(),m0()}}function d0(){if(xn===1){xn=0;var e=Ja,i=Xr,r=(i.flags&13878)!==0;if((i.subtreeFlags&13878)!==0||r){r=z.T,z.T=null;var o=Z.p;Z.p=2;var u=Pe;Pe|=4;try{Wv(i,e);var h=id,S=$m(e.containerInfo),T=h.focusedElem,B=h.selectionRange;if(S!==T&&T&&T.ownerDocument&&Jm(T.ownerDocument.documentElement,T)){if(B!==null&&Rf(T)){var et=B.start,dt=B.end;if(dt===void 0&&(dt=et),"selectionStart"in T)T.selectionStart=et,T.selectionEnd=Math.min(dt,T.value.length);else{var _t=T.ownerDocument||document,it=_t&&_t.defaultView||window;if(it.getSelection){var lt=it.getSelection(),Gt=T.textContent.length,ee=Math.min(B.start,Gt),Xe=B.end===void 0?ee:Math.min(B.end,Gt);!lt.extend&&ee>Xe&&(S=Xe,Xe=ee,ee=S);var J=Km(T,ee),X=Km(T,Xe);if(J&&X&&(lt.rangeCount!==1||lt.anchorNode!==J.node||lt.anchorOffset!==J.offset||lt.focusNode!==X.node||lt.focusOffset!==X.offset)){var tt=_t.createRange();tt.setStart(J.node,J.offset),lt.removeAllRanges(),ee>Xe?(lt.addRange(tt),lt.extend(X.node,X.offset)):(tt.setEnd(X.node,X.offset),lt.addRange(tt))}}}}for(_t=[],lt=T;lt=lt.parentNode;)lt.nodeType===1&&_t.push({element:lt,left:lt.scrollLeft,top:lt.scrollTop});for(typeof T.focus=="function"&&T.focus(),T=0;T<_t.length;T++){var gt=_t[T];gt.element.scrollLeft=gt.left,gt.element.scrollTop=gt.top}}mu=!!nd,id=nd=null}finally{Pe=u,Z.p=o,z.T=r}}e.current=i,xn=2}}function p0(){if(xn===2){xn=0;var e=Ja,i=Xr,r=(i.flags&8772)!==0;if((i.subtreeFlags&8772)!==0||r){r=z.T,z.T=null;var o=Z.p;Z.p=2;var u=Pe;Pe|=4;try{Vv(e,i.alternate,i)}finally{Pe=u,Z.p=o,z.T=r}}xn=3}}function m0(){if(xn===4||xn===3){xn=0,at();var e=Ja,i=Xr,r=_a,o=e0;(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?xn=5:(xn=0,Xr=Ja=null,g0(e,e.pendingLanes));var u=e.pendingLanes;if(u===0&&(Ka=null),_r(r),i=i.stateNode,qt&&typeof qt.onCommitFiberRoot=="function")try{qt.onCommitFiberRoot(Zt,i,void 0,(i.current.flags&128)===128)}catch{}if(o!==null){i=z.T,u=Z.p,Z.p=2,z.T=null;try{for(var h=e.onRecoverableError,S=0;S<o.length;S++){var T=o[S];h(T.value,{componentStack:T.stack})}}finally{z.T=i,Z.p=u}}(_a&3)!==0&&iu(),Yi(e),u=e.pendingLanes,(r&261930)!==0&&(u&42)!==0?e===kh?Tl++:(Tl=0,kh=e):Tl=0,Al(0)}}function g0(e,i){(e.pooledCacheLanes&=i)===0&&(i=e.pooledCache,i!=null&&(e.pooledCache=null,rl(i)))}function iu(){return d0(),p0(),m0(),v0()}function v0(){if(xn!==5)return!1;var e=Ja,i=Gh;Gh=0;var r=_r(_a),o=z.T,u=Z.p;try{Z.p=32>r?32:r,z.T=null,r=Vh,Vh=null;var h=Ja,S=_a;if(xn=0,Xr=Ja=null,_a=0,(Pe&6)!==0)throw Error(a(331));var T=Pe;if(Pe|=4,Jv(h.current),Qv(h,h.current,S,r),Pe=T,Al(0,!1),qt&&typeof qt.onPostCommitFiberRoot=="function")try{qt.onPostCommitFiberRoot(Zt,h)}catch{}return!0}finally{Z.p=u,z.T=o,g0(e,i)}}function _0(e,i,r){i=xi(r,i),i=Sh(e.stateNode,i,2),e=ja(e,i,2),e!==null&&(Rn(e,2),Yi(e))}function Fe(e,i,r){if(e.tag===3)_0(e,e,r);else for(;i!==null;){if(i.tag===3){_0(i,e,r);break}else if(i.tag===1){var o=i.stateNode;if(typeof i.type.getDerivedStateFromError=="function"||typeof o.componentDidCatch=="function"&&(Ka===null||!Ka.has(o))){e=xi(r,e),r=yv(2),o=ja(i,r,2),o!==null&&(xv(r,o,i,e),Rn(o,2),Yi(o));break}}i=i.return}}function qh(e,i,r){var o=e.pingCache;if(o===null){o=e.pingCache=new lM;var u=new Set;o.set(i,u)}else u=o.get(i),u===void 0&&(u=new Set,o.set(i,u));u.has(r)||(Bh=!0,u.add(r),e=dM.bind(null,e,i,r),i.then(e,e))}function dM(e,i,r){var o=e.pingCache;o!==null&&o.delete(i),e.pingedLanes|=e.suspendedLanes&r,e.warmLanes&=~r,Ye===e&&(be&r)===r&&(on===4||on===3&&(be&62914560)===be&&300>pt()-Kc?(Pe&2)===0&&jr(e,0):Fh|=r,kr===be&&(kr=0)),Yi(e)}function y0(e,i){i===0&&(i=_n()),e=Os(e,i),e!==null&&(Rn(e,i),Yi(e))}function pM(e){var i=e.memoizedState,r=0;i!==null&&(r=i.retryLane),y0(e,r)}function mM(e,i){var r=0;switch(e.tag){case 31:case 13:var o=e.stateNode,u=e.memoizedState;u!==null&&(r=u.retryLane);break;case 19:o=e.stateNode;break;case 22:o=e.stateNode._retryCache;break;default:throw Error(a(314))}o!==null&&o.delete(i),y0(e,r)}function gM(e,i){return Yt(e,i)}var au=null,Wr=null,Wh=!1,su=!1,Yh=!1,ts=0;function Yi(e){e!==Wr&&e.next===null&&(Wr===null?au=Wr=e:Wr=Wr.next=e),su=!0,Wh||(Wh=!0,_M())}function Al(e,i){if(!Yh&&su){Yh=!0;do for(var r=!1,o=au;o!==null;){if(e!==0){var u=o.pendingLanes;if(u===0)var h=0;else{var S=o.suspendedLanes,T=o.pingedLanes;h=(1<<31-ne(42|e)+1)-1,h&=u&~(S&~T),h=h&201326741?h&201326741|1:h?h|2:0}h!==0&&(r=!0,E0(o,h))}else h=be,h=Ut(o,o===Ye?h:0,o.cancelPendingCommit!==null||o.timeoutHandle!==-1),(h&3)===0||ie(o,h)||(r=!0,E0(o,h));o=o.next}while(r);Yh=!1}}function vM(){x0()}function x0(){su=Wh=!1;var e=0;ts!==0&&RM()&&(e=ts);for(var i=pt(),r=null,o=au;o!==null;){var u=o.next,h=S0(o,i);h===0?(o.next=null,r===null?au=u:r.next=u,u===null&&(Wr=r)):(r=o,(e!==0||(h&3)!==0)&&(su=!0)),o=u}xn!==0&&xn!==5||Al(e),ts!==0&&(ts=0)}function S0(e,i){for(var r=e.suspendedLanes,o=e.pingedLanes,u=e.expirationTimes,h=e.pendingLanes&-62914561;0<h;){var S=31-ne(h),T=1<<S,B=u[S];B===-1?((T&r)===0||(T&o)!==0)&&(u[S]=$e(T,i)):B<=i&&(e.expiredLanes|=T),h&=~T}if(i=Ye,r=be,r=Ut(e,e===i?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o=e.callbackNode,r===0||e===i&&(Be===2||Be===9)||e.cancelPendingCommit!==null)return o!==null&&o!==null&&L(o),e.callbackNode=null,e.callbackPriority=0;if((r&3)===0||ie(e,r)){if(i=r&-r,i===e.callbackPriority)return i;switch(o!==null&&L(o),_r(r)){case 2:case 8:r=jt;break;case 32:r=Dt;break;case 268435456:r=Me;break;default:r=Dt}return o=M0.bind(null,e),r=Yt(r,o),e.callbackPriority=i,e.callbackNode=r,i}return o!==null&&o!==null&&L(o),e.callbackPriority=2,e.callbackNode=null,2}function M0(e,i){if(xn!==0&&xn!==5)return e.callbackNode=null,e.callbackPriority=0,null;var r=e.callbackNode;if(iu()&&e.callbackNode!==r)return null;var o=be;return o=Ut(e,e===Ye?o:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o===0?null:(i0(e,o,i),S0(e,pt()),e.callbackNode!=null&&e.callbackNode===r?M0.bind(null,e):null)}function E0(e,i){if(iu())return null;i0(e,i,!0)}function _M(){DM(function(){(Pe&6)!==0?Yt(vt,vM):x0()})}function Qh(){if(ts===0){var e=Nr;e===0&&(e=Rt,Rt<<=1,(Rt&261888)===0&&(Rt=256)),ts=e}return ts}function b0(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:dc(""+e)}function T0(e,i){var r=i.ownerDocument.createElement("input");return r.name=i.name,r.value=i.value,e.id&&r.setAttribute("form",e.id),i.parentNode.insertBefore(r,i),e=new FormData(e),r.parentNode.removeChild(r),e}function yM(e,i,r,o,u){if(i==="submit"&&r&&r.stateNode===u){var h=b0((u[wn]||null).action),S=o.submitter;S&&(i=(i=S[wn]||null)?b0(i.formAction):S.getAttribute("formAction"),i!==null&&(h=i,S=null));var T=new vc("action","action",null,o,u);e.push({event:T,listeners:[{instance:null,listener:function(){if(o.defaultPrevented){if(ts!==0){var B=S?T0(u,S):new FormData(u);mh(r,{pending:!0,data:B,method:u.method,action:h},null,B)}}else typeof h=="function"&&(T.preventDefault(),B=S?T0(u,S):new FormData(u),mh(r,{pending:!0,data:B,method:u.method,action:h},h,B))},currentTarget:u}]})}}for(var Zh=0;Zh<Nf.length;Zh++){var Kh=Nf[Zh],xM=Kh.toLowerCase(),SM=Kh[0].toUpperCase()+Kh.slice(1);Ui(xM,"on"+SM)}Ui(ng,"onAnimationEnd"),Ui(ig,"onAnimationIteration"),Ui(ag,"onAnimationStart"),Ui("dblclick","onDoubleClick"),Ui("focusin","onFocus"),Ui("focusout","onBlur"),Ui(IS,"onTransitionRun"),Ui(BS,"onTransitionStart"),Ui(FS,"onTransitionCancel"),Ui(sg,"onTransitionEnd"),$t("onMouseEnter",["mouseout","mouseover"]),$t("onMouseLeave",["mouseout","mouseover"]),$t("onPointerEnter",["pointerout","pointerover"]),$t("onPointerLeave",["pointerout","pointerover"]),Pt("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),Pt("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),Pt("onBeforeInput",["compositionend","keypress","textInput","paste"]),Pt("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Cl="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),MM=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(Cl));function A0(e,i){i=(i&4)!==0;for(var r=0;r<e.length;r++){var o=e[r],u=o.event;o=o.listeners;t:{var h=void 0;if(i)for(var S=o.length-1;0<=S;S--){var T=o[S],B=T.instance,et=T.currentTarget;if(T=T.listener,B!==h&&u.isPropagationStopped())break t;h=T,u.currentTarget=et;try{h(u)}catch(dt){xc(dt)}u.currentTarget=null,h=B}else for(S=0;S<o.length;S++){if(T=o[S],B=T.instance,et=T.currentTarget,T=T.listener,B!==h&&u.isPropagationStopped())break t;h=T,u.currentTarget=et;try{h(u)}catch(dt){xc(dt)}u.currentTarget=null,h=B}}}}function xe(e,i){var r=i[Yo];r===void 0&&(r=i[Yo]=new Set);var o=e+"__bubble";r.has(o)||(C0(i,e,2,!1),r.add(o))}function Jh(e,i,r){var o=0;i&&(o|=4),C0(r,e,o,i)}var ru="_reactListening"+Math.random().toString(36).slice(2);function $h(e){if(!e[ru]){e[ru]=!0,Nt.forEach(function(r){r!=="selectionchange"&&(MM.has(r)||Jh(r,!1,e),Jh(r,!0,e))});var i=e.nodeType===9?e:e.ownerDocument;i===null||i[ru]||(i[ru]=!0,Jh("selectionchange",!1,i))}}function C0(e,i,r,o){switch(n_(i)){case 2:var u=ZM;break;case 8:u=KM;break;default:u=pd}r=u.bind(null,i,r,e),u=void 0,!yf||i!=="touchstart"&&i!=="touchmove"&&i!=="wheel"||(u=!0),o?u!==void 0?e.addEventListener(i,r,{capture:!0,passive:u}):e.addEventListener(i,r,!0):u!==void 0?e.addEventListener(i,r,{passive:u}):e.addEventListener(i,r,!1)}function td(e,i,r,o,u){var h=o;if((i&1)===0&&(i&2)===0&&o!==null)t:for(;;){if(o===null)return;var S=o.tag;if(S===3||S===4){var T=o.stateNode.containerInfo;if(T===u)break;if(S===4)for(S=o.return;S!==null;){var B=S.tag;if((B===3||B===4)&&S.stateNode.containerInfo===u)return;S=S.return}for(;T!==null;){if(S=Q(T),S===null)return;if(B=S.tag,B===5||B===6||B===26||B===27){o=h=S;continue t}T=T.parentNode}}o=o.return}Nm(function(){var et=h,dt=vf(r),_t=[];t:{var it=rg.get(e);if(it!==void 0){var lt=vc,Gt=e;switch(e){case"keypress":if(mc(r)===0)break t;case"keydown":case"keyup":lt=mS;break;case"focusin":Gt="focus",lt=Ef;break;case"focusout":Gt="blur",lt=Ef;break;case"beforeblur":case"afterblur":lt=Ef;break;case"click":if(r.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":lt=Pm;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":lt=iS;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":lt=_S;break;case ng:case ig:case ag:lt=rS;break;case sg:lt=xS;break;case"scroll":case"scrollend":lt=eS;break;case"wheel":lt=MS;break;case"copy":case"cut":case"paste":lt=lS;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":lt=Im;break;case"toggle":case"beforetoggle":lt=bS}var ee=(i&4)!==0,Xe=!ee&&(e==="scroll"||e==="scrollend"),J=ee?it!==null?it+"Capture":null:it;ee=[];for(var X=et,tt;X!==null;){var gt=X;if(tt=gt.stateNode,gt=gt.tag,gt!==5&&gt!==26&&gt!==27||tt===null||J===null||(gt=Qo(X,J),gt!=null&&ee.push(Rl(X,gt,tt))),Xe)break;X=X.return}0<ee.length&&(it=new lt(it,Gt,null,r,dt),_t.push({event:it,listeners:ee}))}}if((i&7)===0){t:{if(it=e==="mouseover"||e==="pointerover",lt=e==="mouseout"||e==="pointerout",it&&r!==gf&&(Gt=r.relatedTarget||r.fromElement)&&(Q(Gt)||Gt[ea]))break t;if((lt||it)&&(it=dt.window===dt?dt:(it=dt.ownerDocument)?it.defaultView||it.parentWindow:window,lt?(Gt=r.relatedTarget||r.toElement,lt=et,Gt=Gt?Q(Gt):null,Gt!==null&&(Xe=c(Gt),ee=Gt.tag,Gt!==Xe||ee!==5&&ee!==27&&ee!==6)&&(Gt=null)):(lt=null,Gt=et),lt!==Gt)){if(ee=Pm,gt="onMouseLeave",J="onMouseEnter",X="mouse",(e==="pointerout"||e==="pointerover")&&(ee=Im,gt="onPointerLeave",J="onPointerEnter",X="pointer"),Xe=lt==null?it:rt(lt),tt=Gt==null?it:rt(Gt),it=new ee(gt,X+"leave",lt,r,dt),it.target=Xe,it.relatedTarget=tt,gt=null,Q(dt)===et&&(ee=new ee(J,X+"enter",Gt,r,dt),ee.target=tt,ee.relatedTarget=Xe,gt=ee),Xe=gt,lt&&Gt)e:{for(ee=EM,J=lt,X=Gt,tt=0,gt=J;gt;gt=ee(gt))tt++;gt=0;for(var Jt=X;Jt;Jt=ee(Jt))gt++;for(;0<tt-gt;)J=ee(J),tt--;for(;0<gt-tt;)X=ee(X),gt--;for(;tt--;){if(J===X||X!==null&&J===X.alternate){ee=J;break e}J=ee(J),X=ee(X)}ee=null}else ee=null;lt!==null&&R0(_t,it,lt,ee,!1),Gt!==null&&Xe!==null&&R0(_t,Xe,Gt,ee,!0)}}t:{if(it=et?rt(et):window,lt=it.nodeName&&it.nodeName.toLowerCase(),lt==="select"||lt==="input"&&it.type==="file")var Ne=jm;else if(km(it))if(qm)Ne=OS;else{Ne=NS;var Xt=US}else lt=it.nodeName,!lt||lt.toLowerCase()!=="input"||it.type!=="checkbox"&&it.type!=="radio"?et&&mf(et.elementType)&&(Ne=jm):Ne=LS;if(Ne&&(Ne=Ne(e,et))){Xm(_t,Ne,r,dt);break t}Xt&&Xt(e,it,et),e==="focusout"&&et&&it.type==="number"&&et.memoizedProps.value!=null&&yn(it,"number",it.value)}switch(Xt=et?rt(et):window,e){case"focusin":(km(Xt)||Xt.contentEditable==="true")&&(br=Xt,wf=et,il=null);break;case"focusout":il=wf=br=null;break;case"mousedown":Df=!0;break;case"contextmenu":case"mouseup":case"dragend":Df=!1,tg(_t,r,dt);break;case"selectionchange":if(zS)break;case"keydown":case"keyup":tg(_t,r,dt)}var ue;if(Tf)t:{switch(e){case"compositionstart":var Te="onCompositionStart";break t;case"compositionend":Te="onCompositionEnd";break t;case"compositionupdate":Te="onCompositionUpdate";break t}Te=void 0}else Er?Gm(e,r)&&(Te="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(Te="onCompositionStart");Te&&(Bm&&r.locale!=="ko"&&(Er||Te!=="onCompositionStart"?Te==="onCompositionEnd"&&Er&&(ue=Lm()):(Ba=dt,xf="value"in Ba?Ba.value:Ba.textContent,Er=!0)),Xt=ou(et,Te),0<Xt.length&&(Te=new zm(Te,e,null,r,dt),_t.push({event:Te,listeners:Xt}),ue?Te.data=ue:(ue=Vm(r),ue!==null&&(Te.data=ue)))),(ue=AS?CS(e,r):RS(e,r))&&(Te=ou(et,"onBeforeInput"),0<Te.length&&(Xt=new zm("onBeforeInput","beforeinput",null,r,dt),_t.push({event:Xt,listeners:Te}),Xt.data=ue)),yM(_t,e,et,r,dt)}A0(_t,i)})}function Rl(e,i,r){return{instance:e,listener:i,currentTarget:r}}function ou(e,i){for(var r=i+"Capture",o=[];e!==null;){var u=e,h=u.stateNode;if(u=u.tag,u!==5&&u!==26&&u!==27||h===null||(u=Qo(e,r),u!=null&&o.unshift(Rl(e,u,h)),u=Qo(e,i),u!=null&&o.push(Rl(e,u,h))),e.tag===3)return o;e=e.return}return[]}function EM(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function R0(e,i,r,o,u){for(var h=i._reactName,S=[];r!==null&&r!==o;){var T=r,B=T.alternate,et=T.stateNode;if(T=T.tag,B!==null&&B===o)break;T!==5&&T!==26&&T!==27||et===null||(B=et,u?(et=Qo(r,h),et!=null&&S.unshift(Rl(r,et,B))):u||(et=Qo(r,h),et!=null&&S.push(Rl(r,et,B)))),r=r.return}S.length!==0&&e.push({event:i,listeners:S})}var bM=/\r\n?/g,TM=/\u0000|\uFFFD/g;function w0(e){return(typeof e=="string"?e:""+e).replace(bM,`
`).replace(TM,"")}function D0(e,i){return i=w0(i),w0(e)===i}function ke(e,i,r,o,u,h){switch(r){case"children":typeof o=="string"?i==="body"||i==="textarea"&&o===""||xr(e,o):(typeof o=="number"||typeof o=="bigint")&&i!=="body"&&xr(e,""+o);break;case"className":We(e,"class",o);break;case"tabIndex":We(e,"tabindex",o);break;case"dir":case"role":case"viewBox":case"width":case"height":We(e,r,o);break;case"style":Dm(e,o,h);break;case"data":if(i!=="object"){We(e,"data",o);break}case"src":case"href":if(o===""&&(i!=="a"||r!=="href")){e.removeAttribute(r);break}if(o==null||typeof o=="function"||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(r);break}o=dc(""+o),e.setAttribute(r,o);break;case"action":case"formAction":if(typeof o=="function"){e.setAttribute(r,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof h=="function"&&(r==="formAction"?(i!=="input"&&ke(e,i,"name",u.name,u,null),ke(e,i,"formEncType",u.formEncType,u,null),ke(e,i,"formMethod",u.formMethod,u,null),ke(e,i,"formTarget",u.formTarget,u,null)):(ke(e,i,"encType",u.encType,u,null),ke(e,i,"method",u.method,u,null),ke(e,i,"target",u.target,u,null)));if(o==null||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(r);break}o=dc(""+o),e.setAttribute(r,o);break;case"onClick":o!=null&&(e.onclick=ia);break;case"onScroll":o!=null&&xe("scroll",e);break;case"onScrollEnd":o!=null&&xe("scrollend",e);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(a(61));if(r=o.__html,r!=null){if(u.children!=null)throw Error(a(60));e.innerHTML=r}}break;case"multiple":e.multiple=o&&typeof o!="function"&&typeof o!="symbol";break;case"muted":e.muted=o&&typeof o!="function"&&typeof o!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(o==null||typeof o=="function"||typeof o=="boolean"||typeof o=="symbol"){e.removeAttribute("xlink:href");break}r=dc(""+o),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",r);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,""+o):e.removeAttribute(r);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":o&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,""):e.removeAttribute(r);break;case"capture":case"download":o===!0?e.setAttribute(r,""):o!==!1&&o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,o):e.removeAttribute(r);break;case"cols":case"rows":case"size":case"span":o!=null&&typeof o!="function"&&typeof o!="symbol"&&!isNaN(o)&&1<=o?e.setAttribute(r,o):e.removeAttribute(r);break;case"rowSpan":case"start":o==null||typeof o=="function"||typeof o=="symbol"||isNaN(o)?e.removeAttribute(r):e.setAttribute(r,o);break;case"popover":xe("beforetoggle",e),xe("toggle",e),Qe(e,"popover",o);break;case"xlinkActuate":le(e,"http://www.w3.org/1999/xlink","xlink:actuate",o);break;case"xlinkArcrole":le(e,"http://www.w3.org/1999/xlink","xlink:arcrole",o);break;case"xlinkRole":le(e,"http://www.w3.org/1999/xlink","xlink:role",o);break;case"xlinkShow":le(e,"http://www.w3.org/1999/xlink","xlink:show",o);break;case"xlinkTitle":le(e,"http://www.w3.org/1999/xlink","xlink:title",o);break;case"xlinkType":le(e,"http://www.w3.org/1999/xlink","xlink:type",o);break;case"xmlBase":le(e,"http://www.w3.org/XML/1998/namespace","xml:base",o);break;case"xmlLang":le(e,"http://www.w3.org/XML/1998/namespace","xml:lang",o);break;case"xmlSpace":le(e,"http://www.w3.org/XML/1998/namespace","xml:space",o);break;case"is":Qe(e,"is",o);break;case"innerText":case"textContent":break;default:(!(2<r.length)||r[0]!=="o"&&r[0]!=="O"||r[1]!=="n"&&r[1]!=="N")&&(r=$x.get(r)||r,Qe(e,r,o))}}function ed(e,i,r,o,u,h){switch(r){case"style":Dm(e,o,h);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(a(61));if(r=o.__html,r!=null){if(u.children!=null)throw Error(a(60));e.innerHTML=r}}break;case"children":typeof o=="string"?xr(e,o):(typeof o=="number"||typeof o=="bigint")&&xr(e,""+o);break;case"onScroll":o!=null&&xe("scroll",e);break;case"onScrollEnd":o!=null&&xe("scrollend",e);break;case"onClick":o!=null&&(e.onclick=ia);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!It.hasOwnProperty(r))t:{if(r[0]==="o"&&r[1]==="n"&&(u=r.endsWith("Capture"),i=r.slice(2,u?r.length-7:void 0),h=e[wn]||null,h=h!=null?h[r]:null,typeof h=="function"&&e.removeEventListener(i,h,u),typeof o=="function")){typeof h!="function"&&h!==null&&(r in e?e[r]=null:e.hasAttribute(r)&&e.removeAttribute(r)),e.addEventListener(i,o,u);break t}r in e?e[r]=o:o===!0?e.setAttribute(r,""):Qe(e,r,o)}}}function Ln(e,i,r){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":xe("error",e),xe("load",e);var o=!1,u=!1,h;for(h in r)if(r.hasOwnProperty(h)){var S=r[h];if(S!=null)switch(h){case"src":o=!0;break;case"srcSet":u=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(a(137,i));default:ke(e,i,h,S,r,null)}}u&&ke(e,i,"srcSet",r.srcSet,r,null),o&&ke(e,i,"src",r.src,r,null);return;case"input":xe("invalid",e);var T=h=S=u=null,B=null,et=null;for(o in r)if(r.hasOwnProperty(o)){var dt=r[o];if(dt!=null)switch(o){case"name":u=dt;break;case"type":S=dt;break;case"checked":B=dt;break;case"defaultChecked":et=dt;break;case"value":h=dt;break;case"defaultValue":T=dt;break;case"children":case"dangerouslySetInnerHTML":if(dt!=null)throw Error(a(137,i));break;default:ke(e,i,o,dt,r,null)}}Vn(e,h,T,B,et,S,u,!1);return;case"select":xe("invalid",e),o=S=h=null;for(u in r)if(r.hasOwnProperty(u)&&(T=r[u],T!=null))switch(u){case"value":h=T;break;case"defaultValue":S=T;break;case"multiple":o=T;default:ke(e,i,u,T,r,null)}i=h,r=S,e.multiple=!!o,i!=null?cn(e,!!o,i,!1):r!=null&&cn(e,!!o,r,!0);return;case"textarea":xe("invalid",e),h=u=o=null;for(S in r)if(r.hasOwnProperty(S)&&(T=r[S],T!=null))switch(S){case"value":o=T;break;case"defaultValue":u=T;break;case"children":h=T;break;case"dangerouslySetInnerHTML":if(T!=null)throw Error(a(91));break;default:ke(e,i,S,T,r,null)}Xi(e,o,u,h);return;case"option":for(B in r)if(r.hasOwnProperty(B)&&(o=r[B],o!=null))switch(B){case"selected":e.selected=o&&typeof o!="function"&&typeof o!="symbol";break;default:ke(e,i,B,o,r,null)}return;case"dialog":xe("beforetoggle",e),xe("toggle",e),xe("cancel",e),xe("close",e);break;case"iframe":case"object":xe("load",e);break;case"video":case"audio":for(o=0;o<Cl.length;o++)xe(Cl[o],e);break;case"image":xe("error",e),xe("load",e);break;case"details":xe("toggle",e);break;case"embed":case"source":case"link":xe("error",e),xe("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in r)if(r.hasOwnProperty(et)&&(o=r[et],o!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(a(137,i));default:ke(e,i,et,o,r,null)}return;default:if(mf(i)){for(dt in r)r.hasOwnProperty(dt)&&(o=r[dt],o!==void 0&&ed(e,i,dt,o,r,void 0));return}}for(T in r)r.hasOwnProperty(T)&&(o=r[T],o!=null&&ke(e,i,T,o,r,null))}function AM(e,i,r,o){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var u=null,h=null,S=null,T=null,B=null,et=null,dt=null;for(lt in r){var _t=r[lt];if(r.hasOwnProperty(lt)&&_t!=null)switch(lt){case"checked":break;case"value":break;case"defaultValue":B=_t;default:o.hasOwnProperty(lt)||ke(e,i,lt,null,o,_t)}}for(var it in o){var lt=o[it];if(_t=r[it],o.hasOwnProperty(it)&&(lt!=null||_t!=null))switch(it){case"type":h=lt;break;case"name":u=lt;break;case"checked":et=lt;break;case"defaultChecked":dt=lt;break;case"value":S=lt;break;case"defaultValue":T=lt;break;case"children":case"dangerouslySetInnerHTML":if(lt!=null)throw Error(a(137,i));break;default:lt!==_t&&ke(e,i,it,lt,o,_t)}}zn(e,S,T,B,et,dt,h,u);return;case"select":lt=S=T=it=null;for(h in r)if(B=r[h],r.hasOwnProperty(h)&&B!=null)switch(h){case"value":break;case"multiple":lt=B;default:o.hasOwnProperty(h)||ke(e,i,h,null,o,B)}for(u in o)if(h=o[u],B=r[u],o.hasOwnProperty(u)&&(h!=null||B!=null))switch(u){case"value":it=h;break;case"defaultValue":T=h;break;case"multiple":S=h;default:h!==B&&ke(e,i,u,h,o,B)}i=T,r=S,o=lt,it!=null?cn(e,!!r,it,!1):!!o!=!!r&&(i!=null?cn(e,!!r,i,!0):cn(e,!!r,r?[]:"",!1));return;case"textarea":lt=it=null;for(T in r)if(u=r[T],r.hasOwnProperty(T)&&u!=null&&!o.hasOwnProperty(T))switch(T){case"value":break;case"children":break;default:ke(e,i,T,null,o,u)}for(S in o)if(u=o[S],h=r[S],o.hasOwnProperty(S)&&(u!=null||h!=null))switch(S){case"value":it=u;break;case"defaultValue":lt=u;break;case"children":break;case"dangerouslySetInnerHTML":if(u!=null)throw Error(a(91));break;default:u!==h&&ke(e,i,S,u,o,h)}yr(e,it,lt);return;case"option":for(var Gt in r)if(it=r[Gt],r.hasOwnProperty(Gt)&&it!=null&&!o.hasOwnProperty(Gt))switch(Gt){case"selected":e.selected=!1;break;default:ke(e,i,Gt,null,o,it)}for(B in o)if(it=o[B],lt=r[B],o.hasOwnProperty(B)&&it!==lt&&(it!=null||lt!=null))switch(B){case"selected":e.selected=it&&typeof it!="function"&&typeof it!="symbol";break;default:ke(e,i,B,it,o,lt)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var ee in r)it=r[ee],r.hasOwnProperty(ee)&&it!=null&&!o.hasOwnProperty(ee)&&ke(e,i,ee,null,o,it);for(et in o)if(it=o[et],lt=r[et],o.hasOwnProperty(et)&&it!==lt&&(it!=null||lt!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(it!=null)throw Error(a(137,i));break;default:ke(e,i,et,it,o,lt)}return;default:if(mf(i)){for(var Xe in r)it=r[Xe],r.hasOwnProperty(Xe)&&it!==void 0&&!o.hasOwnProperty(Xe)&&ed(e,i,Xe,void 0,o,it);for(dt in o)it=o[dt],lt=r[dt],!o.hasOwnProperty(dt)||it===lt||it===void 0&&lt===void 0||ed(e,i,dt,it,o,lt);return}}for(var J in r)it=r[J],r.hasOwnProperty(J)&&it!=null&&!o.hasOwnProperty(J)&&ke(e,i,J,null,o,it);for(_t in o)it=o[_t],lt=r[_t],!o.hasOwnProperty(_t)||it===lt||it==null&&lt==null||ke(e,i,_t,it,o,lt)}function U0(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function CM(){if(typeof performance.getEntriesByType=="function"){for(var e=0,i=0,r=performance.getEntriesByType("resource"),o=0;o<r.length;o++){var u=r[o],h=u.transferSize,S=u.initiatorType,T=u.duration;if(h&&T&&U0(S)){for(S=0,T=u.responseEnd,o+=1;o<r.length;o++){var B=r[o],et=B.startTime;if(et>T)break;var dt=B.transferSize,_t=B.initiatorType;dt&&U0(_t)&&(B=B.responseEnd,S+=dt*(B<T?1:(T-et)/(B-et)))}if(--o,i+=8*(h+S)/(u.duration/1e3),e++,10<e)break}}if(0<e)return i/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var nd=null,id=null;function lu(e){return e.nodeType===9?e:e.ownerDocument}function N0(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function L0(e,i){if(e===0)switch(i){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&i==="foreignObject"?0:e}function ad(e,i){return e==="textarea"||e==="noscript"||typeof i.children=="string"||typeof i.children=="number"||typeof i.children=="bigint"||typeof i.dangerouslySetInnerHTML=="object"&&i.dangerouslySetInnerHTML!==null&&i.dangerouslySetInnerHTML.__html!=null}var sd=null;function RM(){var e=window.event;return e&&e.type==="popstate"?e===sd?!1:(sd=e,!0):(sd=null,!1)}var O0=typeof setTimeout=="function"?setTimeout:void 0,wM=typeof clearTimeout=="function"?clearTimeout:void 0,P0=typeof Promise=="function"?Promise:void 0,DM=typeof queueMicrotask=="function"?queueMicrotask:typeof P0<"u"?function(e){return P0.resolve(null).then(e).catch(UM)}:O0;function UM(e){setTimeout(function(){throw e})}function es(e){return e==="head"}function z0(e,i){var r=i,o=0;do{var u=r.nextSibling;if(e.removeChild(r),u&&u.nodeType===8)if(r=u.data,r==="/$"||r==="/&"){if(o===0){e.removeChild(u),Kr(i);return}o--}else if(r==="$"||r==="$?"||r==="$~"||r==="$!"||r==="&")o++;else if(r==="html")wl(e.ownerDocument.documentElement);else if(r==="head"){r=e.ownerDocument.head,wl(r);for(var h=r.firstChild;h;){var S=h.nextSibling,T=h.nodeName;h[ws]||T==="SCRIPT"||T==="STYLE"||T==="LINK"&&h.rel.toLowerCase()==="stylesheet"||r.removeChild(h),h=S}}else r==="body"&&wl(e.ownerDocument.body);r=u}while(r);Kr(i)}function I0(e,i){var r=e;e=0;do{var o=r.nextSibling;if(r.nodeType===1?i?(r._stashedDisplay=r.style.display,r.style.display="none"):(r.style.display=r._stashedDisplay||"",r.getAttribute("style")===""&&r.removeAttribute("style")):r.nodeType===3&&(i?(r._stashedText=r.nodeValue,r.nodeValue=""):r.nodeValue=r._stashedText||""),o&&o.nodeType===8)if(r=o.data,r==="/$"){if(e===0)break;e--}else r!=="$"&&r!=="$?"&&r!=="$~"&&r!=="$!"||e++;r=o}while(r)}function rd(e){var i=e.firstChild;for(i&&i.nodeType===10&&(i=i.nextSibling);i;){var r=i;switch(i=i.nextSibling,r.nodeName){case"HTML":case"HEAD":case"BODY":rd(r),R(r);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(r.rel.toLowerCase()==="stylesheet")continue}e.removeChild(r)}}function NM(e,i,r,o){for(;e.nodeType===1;){var u=r;if(e.nodeName.toLowerCase()!==i.toLowerCase()){if(!o&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(o){if(!e[ws])switch(i){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(h=e.getAttribute("rel"),h==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(h!==u.rel||e.getAttribute("href")!==(u.href==null||u.href===""?null:u.href)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin)||e.getAttribute("title")!==(u.title==null?null:u.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(h=e.getAttribute("src"),(h!==(u.src==null?null:u.src)||e.getAttribute("type")!==(u.type==null?null:u.type)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin))&&h&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(i==="input"&&e.type==="hidden"){var h=u.name==null?null:""+u.name;if(u.type==="hidden"&&e.getAttribute("name")===h)return e}else return e;if(e=Ti(e.nextSibling),e===null)break}return null}function LM(e,i,r){if(i==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!r||(e=Ti(e.nextSibling),e===null))return null;return e}function B0(e,i){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!i||(e=Ti(e.nextSibling),e===null))return null;return e}function od(e){return e.data==="$?"||e.data==="$~"}function ld(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function OM(e,i){var r=e.ownerDocument;if(e.data==="$~")e._reactRetry=i;else if(e.data!=="$?"||r.readyState!=="loading")i();else{var o=function(){i(),r.removeEventListener("DOMContentLoaded",o)};r.addEventListener("DOMContentLoaded",o),e._reactRetry=o}}function Ti(e){for(;e!=null;e=e.nextSibling){var i=e.nodeType;if(i===1||i===3)break;if(i===8){if(i=e.data,i==="$"||i==="$!"||i==="$?"||i==="$~"||i==="&"||i==="F!"||i==="F")break;if(i==="/$"||i==="/&")return null}}return e}var cd=null;function F0(e){e=e.nextSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"||r==="/&"){if(i===0)return Ti(e.nextSibling);i--}else r!=="$"&&r!=="$!"&&r!=="$?"&&r!=="$~"&&r!=="&"||i++}e=e.nextSibling}return null}function H0(e){e=e.previousSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"||r==="$~"||r==="&"){if(i===0)return e;i--}else r!=="/$"&&r!=="/&"||i++}e=e.previousSibling}return null}function G0(e,i,r){switch(i=lu(r),e){case"html":if(e=i.documentElement,!e)throw Error(a(452));return e;case"head":if(e=i.head,!e)throw Error(a(453));return e;case"body":if(e=i.body,!e)throw Error(a(454));return e;default:throw Error(a(451))}}function wl(e){for(var i=e.attributes;i.length;)e.removeAttributeNode(i[0]);R(e)}var Ai=new Map,V0=new Set;function cu(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var ya=Z.d;Z.d={f:PM,r:zM,D:IM,C:BM,L:FM,m:HM,X:VM,S:GM,M:kM};function PM(){var e=ya.f(),i=tu();return e||i}function zM(e){var i=st(e);i!==null&&i.tag===5&&i.type==="form"?sv(i):ya.r(e)}var Yr=typeof document>"u"?null:document;function k0(e,i,r){var o=Yr;if(o&&typeof i=="string"&&i){var u=_e(i);u='link[rel="'+e+'"][href="'+u+'"]',typeof r=="string"&&(u+='[crossorigin="'+r+'"]'),V0.has(u)||(V0.add(u),e={rel:e,crossOrigin:r,href:i},o.querySelector(u)===null&&(i=o.createElement("link"),Ln(i,"link",e),xt(i),o.head.appendChild(i)))}}function IM(e){ya.D(e),k0("dns-prefetch",e,null)}function BM(e,i){ya.C(e,i),k0("preconnect",e,i)}function FM(e,i,r){ya.L(e,i,r);var o=Yr;if(o&&e&&i){var u='link[rel="preload"][as="'+_e(i)+'"]';i==="image"&&r&&r.imageSrcSet?(u+='[imagesrcset="'+_e(r.imageSrcSet)+'"]',typeof r.imageSizes=="string"&&(u+='[imagesizes="'+_e(r.imageSizes)+'"]')):u+='[href="'+_e(e)+'"]';var h=u;switch(i){case"style":h=Qr(e);break;case"script":h=Zr(e)}Ai.has(h)||(e=v({rel:"preload",href:i==="image"&&r&&r.imageSrcSet?void 0:e,as:i},r),Ai.set(h,e),o.querySelector(u)!==null||i==="style"&&o.querySelector(Dl(h))||i==="script"&&o.querySelector(Ul(h))||(i=o.createElement("link"),Ln(i,"link",e),xt(i),o.head.appendChild(i)))}}function HM(e,i){ya.m(e,i);var r=Yr;if(r&&e){var o=i&&typeof i.as=="string"?i.as:"script",u='link[rel="modulepreload"][as="'+_e(o)+'"][href="'+_e(e)+'"]',h=u;switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":h=Zr(e)}if(!Ai.has(h)&&(e=v({rel:"modulepreload",href:e},i),Ai.set(h,e),r.querySelector(u)===null)){switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(r.querySelector(Ul(h)))return}o=r.createElement("link"),Ln(o,"link",e),xt(o),r.head.appendChild(o)}}}function GM(e,i,r){ya.S(e,i,r);var o=Yr;if(o&&e){var u=K(o).hoistableStyles,h=Qr(e);i=i||"default";var S=u.get(h);if(!S){var T={loading:0,preload:null};if(S=o.querySelector(Dl(h)))T.loading=5;else{e=v({rel:"stylesheet",href:e,"data-precedence":i},r),(r=Ai.get(h))&&ud(e,r);var B=S=o.createElement("link");xt(B),Ln(B,"link",e),B._p=new Promise(function(et,dt){B.onload=et,B.onerror=dt}),B.addEventListener("load",function(){T.loading|=1}),B.addEventListener("error",function(){T.loading|=2}),T.loading|=4,uu(S,i,o)}S={type:"stylesheet",instance:S,count:1,state:T},u.set(h,S)}}}function VM(e,i){ya.X(e,i);var r=Yr;if(r&&e){var o=K(r).hoistableScripts,u=Zr(e),h=o.get(u);h||(h=r.querySelector(Ul(u)),h||(e=v({src:e,async:!0},i),(i=Ai.get(u))&&fd(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(u,h))}}function kM(e,i){ya.M(e,i);var r=Yr;if(r&&e){var o=K(r).hoistableScripts,u=Zr(e),h=o.get(u);h||(h=r.querySelector(Ul(u)),h||(e=v({src:e,async:!0,type:"module"},i),(i=Ai.get(u))&&fd(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(u,h))}}function X0(e,i,r,o){var u=(u=Tt.current)?cu(u):null;if(!u)throw Error(a(446));switch(e){case"meta":case"title":return null;case"style":return typeof r.precedence=="string"&&typeof r.href=="string"?(i=Qr(r.href),r=K(u).hoistableStyles,o=r.get(i),o||(o={type:"style",instance:null,count:0,state:null},r.set(i,o)),o):{type:"void",instance:null,count:0,state:null};case"link":if(r.rel==="stylesheet"&&typeof r.href=="string"&&typeof r.precedence=="string"){e=Qr(r.href);var h=K(u).hoistableStyles,S=h.get(e);if(S||(u=u.ownerDocument||u,S={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},h.set(e,S),(h=u.querySelector(Dl(e)))&&!h._p&&(S.instance=h,S.state.loading=5),Ai.has(e)||(r={rel:"preload",as:"style",href:r.href,crossOrigin:r.crossOrigin,integrity:r.integrity,media:r.media,hrefLang:r.hrefLang,referrerPolicy:r.referrerPolicy},Ai.set(e,r),h||XM(u,e,r,S.state))),i&&o===null)throw Error(a(528,""));return S}if(i&&o!==null)throw Error(a(529,""));return null;case"script":return i=r.async,r=r.src,typeof r=="string"&&i&&typeof i!="function"&&typeof i!="symbol"?(i=Zr(r),r=K(u).hoistableScripts,o=r.get(i),o||(o={type:"script",instance:null,count:0,state:null},r.set(i,o)),o):{type:"void",instance:null,count:0,state:null};default:throw Error(a(444,e))}}function Qr(e){return'href="'+_e(e)+'"'}function Dl(e){return'link[rel="stylesheet"]['+e+"]"}function j0(e){return v({},e,{"data-precedence":e.precedence,precedence:null})}function XM(e,i,r,o){e.querySelector('link[rel="preload"][as="style"]['+i+"]")?o.loading=1:(i=e.createElement("link"),o.preload=i,i.addEventListener("load",function(){return o.loading|=1}),i.addEventListener("error",function(){return o.loading|=2}),Ln(i,"link",r),xt(i),e.head.appendChild(i))}function Zr(e){return'[src="'+_e(e)+'"]'}function Ul(e){return"script[async]"+e}function q0(e,i,r){if(i.count++,i.instance===null)switch(i.type){case"style":var o=e.querySelector('style[data-href~="'+_e(r.href)+'"]');if(o)return i.instance=o,xt(o),o;var u=v({},r,{"data-href":r.href,"data-precedence":r.precedence,href:null,precedence:null});return o=(e.ownerDocument||e).createElement("style"),xt(o),Ln(o,"style",u),uu(o,r.precedence,e),i.instance=o;case"stylesheet":u=Qr(r.href);var h=e.querySelector(Dl(u));if(h)return i.state.loading|=4,i.instance=h,xt(h),h;o=j0(r),(u=Ai.get(u))&&ud(o,u),h=(e.ownerDocument||e).createElement("link"),xt(h);var S=h;return S._p=new Promise(function(T,B){S.onload=T,S.onerror=B}),Ln(h,"link",o),i.state.loading|=4,uu(h,r.precedence,e),i.instance=h;case"script":return h=Zr(r.src),(u=e.querySelector(Ul(h)))?(i.instance=u,xt(u),u):(o=r,(u=Ai.get(h))&&(o=v({},r),fd(o,u)),e=e.ownerDocument||e,u=e.createElement("script"),xt(u),Ln(u,"link",o),e.head.appendChild(u),i.instance=u);case"void":return null;default:throw Error(a(443,i.type))}else i.type==="stylesheet"&&(i.state.loading&4)===0&&(o=i.instance,i.state.loading|=4,uu(o,r.precedence,e));return i.instance}function uu(e,i,r){for(var o=r.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),u=o.length?o[o.length-1]:null,h=u,S=0;S<o.length;S++){var T=o[S];if(T.dataset.precedence===i)h=T;else if(h!==u)break}h?h.parentNode.insertBefore(e,h.nextSibling):(i=r.nodeType===9?r.head:r,i.insertBefore(e,i.firstChild))}function ud(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.title==null&&(e.title=i.title)}function fd(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.integrity==null&&(e.integrity=i.integrity)}var fu=null;function W0(e,i,r){if(fu===null){var o=new Map,u=fu=new Map;u.set(r,o)}else u=fu,o=u.get(r),o||(o=new Map,u.set(r,o));if(o.has(e))return o;for(o.set(e,null),r=r.getElementsByTagName(e),u=0;u<r.length;u++){var h=r[u];if(!(h[ws]||h[sn]||e==="link"&&h.getAttribute("rel")==="stylesheet")&&h.namespaceURI!=="http://www.w3.org/2000/svg"){var S=h.getAttribute(i)||"";S=e+S;var T=o.get(S);T?T.push(h):o.set(S,[h])}}return o}function Y0(e,i,r){e=e.ownerDocument||e,e.head.insertBefore(r,i==="title"?e.querySelector("head > title"):null)}function jM(e,i,r){if(r===1||i.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof i.precedence!="string"||typeof i.href!="string"||i.href==="")break;return!0;case"link":if(typeof i.rel!="string"||typeof i.href!="string"||i.href===""||i.onLoad||i.onError)break;switch(i.rel){case"stylesheet":return e=i.disabled,typeof i.precedence=="string"&&e==null;default:return!0}case"script":if(i.async&&typeof i.async!="function"&&typeof i.async!="symbol"&&!i.onLoad&&!i.onError&&i.src&&typeof i.src=="string")return!0}return!1}function Q0(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function qM(e,i,r,o){if(r.type==="stylesheet"&&(typeof o.media!="string"||matchMedia(o.media).matches!==!1)&&(r.state.loading&4)===0){if(r.instance===null){var u=Qr(o.href),h=i.querySelector(Dl(u));if(h){i=h._p,i!==null&&typeof i=="object"&&typeof i.then=="function"&&(e.count++,e=hu.bind(e),i.then(e,e)),r.state.loading|=4,r.instance=h,xt(h);return}h=i.ownerDocument||i,o=j0(o),(u=Ai.get(u))&&ud(o,u),h=h.createElement("link"),xt(h);var S=h;S._p=new Promise(function(T,B){S.onload=T,S.onerror=B}),Ln(h,"link",o),r.instance=h}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(r,i),(i=r.state.preload)&&(r.state.loading&3)===0&&(e.count++,r=hu.bind(e),i.addEventListener("load",r),i.addEventListener("error",r))}}var hd=0;function WM(e,i){return e.stylesheets&&e.count===0&&pu(e,e.stylesheets),0<e.count||0<e.imgCount?function(r){var o=setTimeout(function(){if(e.stylesheets&&pu(e,e.stylesheets),e.unsuspend){var h=e.unsuspend;e.unsuspend=null,h()}},6e4+i);0<e.imgBytes&&hd===0&&(hd=62500*CM());var u=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&pu(e,e.stylesheets),e.unsuspend)){var h=e.unsuspend;e.unsuspend=null,h()}},(e.imgBytes>hd?50:800)+i);return e.unsuspend=r,function(){e.unsuspend=null,clearTimeout(o),clearTimeout(u)}}:null}function hu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)pu(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var du=null;function pu(e,i){e.stylesheets=null,e.unsuspend!==null&&(e.count++,du=new Map,i.forEach(YM,e),du=null,hu.call(e))}function YM(e,i){if(!(i.state.loading&4)){var r=du.get(e);if(r)var o=r.get(null);else{r=new Map,du.set(e,r);for(var u=e.querySelectorAll("link[data-precedence],style[data-precedence]"),h=0;h<u.length;h++){var S=u[h];(S.nodeName==="LINK"||S.getAttribute("media")!=="not all")&&(r.set(S.dataset.precedence,S),o=S)}o&&r.set(null,o)}u=i.instance,S=u.getAttribute("data-precedence"),h=r.get(S)||o,h===o&&r.set(null,u),r.set(S,u),this.count++,o=hu.bind(this),u.addEventListener("load",o),u.addEventListener("error",o),h?h.parentNode.insertBefore(u,h.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(u,e.firstChild)),i.state.loading|=4}}var Nl={$$typeof:N,Provider:null,Consumer:null,_currentValue:$,_currentValue2:$,_threadCount:0};function QM(e,i,r,o,u,h,S,T,B){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=we(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=we(0),this.hiddenUpdates=we(null),this.identifierPrefix=o,this.onUncaughtError=u,this.onCaughtError=h,this.onRecoverableError=S,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=B,this.incompleteTransitions=new Map}function Z0(e,i,r,o,u,h,S,T,B,et,dt,_t){return e=new QM(e,i,r,S,B,et,dt,_t,T),i=1,h===!0&&(i|=24),h=oi(3,null,null,i),e.current=h,h.stateNode=e,i=jf(),i.refCount++,e.pooledCache=i,i.refCount++,h.memoizedState={element:o,isDehydrated:r,cache:i},Qf(h),e}function K0(e){return e?(e=Cr,e):Cr}function J0(e,i,r,o,u,h){u=K0(u),o.context===null?o.context=u:o.pendingContext=u,o=Xa(i),o.payload={element:r},h=h===void 0?null:h,h!==null&&(o.callback=h),r=ja(e,o,i),r!==null&&(ti(r,e,i),ul(r,e,i))}function $0(e,i){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<i?r:i}}function dd(e,i){$0(e,i),(e=e.alternate)&&$0(e,i)}function t_(e){if(e.tag===13||e.tag===31){var i=Os(e,67108864);i!==null&&ti(i,e,67108864),dd(e,67108864)}}function e_(e){if(e.tag===13||e.tag===31){var i=hi();i=Cs(i);var r=Os(e,i);r!==null&&ti(r,e,i),dd(e,i)}}var mu=!0;function ZM(e,i,r,o){var u=z.T;z.T=null;var h=Z.p;try{Z.p=2,pd(e,i,r,o)}finally{Z.p=h,z.T=u}}function KM(e,i,r,o){var u=z.T;z.T=null;var h=Z.p;try{Z.p=8,pd(e,i,r,o)}finally{Z.p=h,z.T=u}}function pd(e,i,r,o){if(mu){var u=md(o);if(u===null)td(e,i,o,gu,r),i_(e,o);else if($M(u,e,i,r,o))o.stopPropagation();else if(i_(e,o),i&4&&-1<JM.indexOf(e)){for(;u!==null;){var h=st(u);if(h!==null)switch(h.tag){case 3:if(h=h.stateNode,h.current.memoizedState.isDehydrated){var S=wt(h.pendingLanes);if(S!==0){var T=h;for(T.pendingLanes|=2,T.entangledLanes|=2;S;){var B=1<<31-ne(S);T.entanglements[1]|=B,S&=~B}Yi(h),(Pe&6)===0&&(Jc=pt()+500,Al(0))}}break;case 31:case 13:T=Os(h,2),T!==null&&ti(T,h,2),tu(),dd(h,2)}if(h=md(o),h===null&&td(e,i,o,gu,r),h===u)break;u=h}u!==null&&o.stopPropagation()}else td(e,i,o,null,r)}}function md(e){return e=vf(e),gd(e)}var gu=null;function gd(e){if(gu=null,e=Q(e),e!==null){var i=c(e);if(i===null)e=null;else{var r=i.tag;if(r===13){if(e=f(i),e!==null)return e;e=null}else if(r===31){if(e=d(i),e!==null)return e;e=null}else if(r===3){if(i.stateNode.current.memoizedState.isDehydrated)return i.tag===3?i.stateNode.containerInfo:null;e=null}else i!==e&&(e=null)}}return gu=e,null}function n_(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(bt()){case vt:return 2;case jt:return 8;case Dt:case Bt:return 32;case Me:return 268435456;default:return 32}default:return 32}}var vd=!1,ns=null,is=null,as=null,Ll=new Map,Ol=new Map,ss=[],JM="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function i_(e,i){switch(e){case"focusin":case"focusout":ns=null;break;case"dragenter":case"dragleave":is=null;break;case"mouseover":case"mouseout":as=null;break;case"pointerover":case"pointerout":Ll.delete(i.pointerId);break;case"gotpointercapture":case"lostpointercapture":Ol.delete(i.pointerId)}}function Pl(e,i,r,o,u,h){return e===null||e.nativeEvent!==h?(e={blockedOn:i,domEventName:r,eventSystemFlags:o,nativeEvent:h,targetContainers:[u]},i!==null&&(i=st(i),i!==null&&t_(i)),e):(e.eventSystemFlags|=o,i=e.targetContainers,u!==null&&i.indexOf(u)===-1&&i.push(u),e)}function $M(e,i,r,o,u){switch(i){case"focusin":return ns=Pl(ns,e,i,r,o,u),!0;case"dragenter":return is=Pl(is,e,i,r,o,u),!0;case"mouseover":return as=Pl(as,e,i,r,o,u),!0;case"pointerover":var h=u.pointerId;return Ll.set(h,Pl(Ll.get(h)||null,e,i,r,o,u)),!0;case"gotpointercapture":return h=u.pointerId,Ol.set(h,Pl(Ol.get(h)||null,e,i,r,o,u)),!0}return!1}function a_(e){var i=Q(e.target);if(i!==null){var r=c(i);if(r!==null){if(i=r.tag,i===13){if(i=f(r),i!==null){e.blockedOn=i,Rs(e.priority,function(){e_(r)});return}}else if(i===31){if(i=d(r),i!==null){e.blockedOn=i,Rs(e.priority,function(){e_(r)});return}}else if(i===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function vu(e){if(e.blockedOn!==null)return!1;for(var i=e.targetContainers;0<i.length;){var r=md(e.nativeEvent);if(r===null){r=e.nativeEvent;var o=new r.constructor(r.type,r);gf=o,r.target.dispatchEvent(o),gf=null}else return i=st(r),i!==null&&t_(i),e.blockedOn=r,!1;i.shift()}return!0}function s_(e,i,r){vu(e)&&r.delete(i)}function tE(){vd=!1,ns!==null&&vu(ns)&&(ns=null),is!==null&&vu(is)&&(is=null),as!==null&&vu(as)&&(as=null),Ll.forEach(s_),Ol.forEach(s_)}function _u(e,i){e.blockedOn===i&&(e.blockedOn=null,vd||(vd=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,tE)))}var yu=null;function r_(e){yu!==e&&(yu=e,s.unstable_scheduleCallback(s.unstable_NormalPriority,function(){yu===e&&(yu=null);for(var i=0;i<e.length;i+=3){var r=e[i],o=e[i+1],u=e[i+2];if(typeof o!="function"){if(gd(o||r)===null)continue;break}var h=st(r);h!==null&&(e.splice(i,3),i-=3,mh(h,{pending:!0,data:u,method:r.method,action:o},o,u))}}))}function Kr(e){function i(B){return _u(B,e)}ns!==null&&_u(ns,e),is!==null&&_u(is,e),as!==null&&_u(as,e),Ll.forEach(i),Ol.forEach(i);for(var r=0;r<ss.length;r++){var o=ss[r];o.blockedOn===e&&(o.blockedOn=null)}for(;0<ss.length&&(r=ss[0],r.blockedOn===null);)a_(r),r.blockedOn===null&&ss.shift();if(r=(e.ownerDocument||e).$$reactFormReplay,r!=null)for(o=0;o<r.length;o+=3){var u=r[o],h=r[o+1],S=u[wn]||null;if(typeof h=="function")S||r_(r);else if(S){var T=null;if(h&&h.hasAttribute("formAction")){if(u=h,S=h[wn]||null)T=S.formAction;else if(gd(u)!==null)continue}else T=S.action;typeof T=="function"?r[o+1]=T:(r.splice(o,3),o-=3),r_(r)}}}function o_(){function e(h){h.canIntercept&&h.info==="react-transition"&&h.intercept({handler:function(){return new Promise(function(S){return u=S})},focusReset:"manual",scroll:"manual"})}function i(){u!==null&&(u(),u=null),o||setTimeout(r,20)}function r(){if(!o&&!navigation.transition){var h=navigation.currentEntry;h&&h.url!=null&&navigation.navigate(h.url,{state:h.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var o=!1,u=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",i),navigation.addEventListener("navigateerror",i),setTimeout(r,100),function(){o=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",i),navigation.removeEventListener("navigateerror",i),u!==null&&(u(),u=null)}}}function _d(e){this._internalRoot=e}xu.prototype.render=_d.prototype.render=function(e){var i=this._internalRoot;if(i===null)throw Error(a(409));var r=i.current,o=hi();J0(r,o,e,i,null,null)},xu.prototype.unmount=_d.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var i=e.containerInfo;J0(e.current,2,null,e,null,null),tu(),i[ea]=null}};function xu(e){this._internalRoot=e}xu.prototype.unstable_scheduleHydration=function(e){if(e){var i=Wo();e={blockedOn:null,target:e,priority:i};for(var r=0;r<ss.length&&i!==0&&i<ss[r].priority;r++);ss.splice(r,0,e),r===0&&a_(e)}};var l_=t.version;if(l_!=="19.2.7")throw Error(a(527,l_,"19.2.7"));Z.findDOMNode=function(e){var i=e._reactInternals;if(i===void 0)throw typeof e.render=="function"?Error(a(188)):(e=Object.keys(e).join(","),Error(a(268,e)));return e=m(i),e=e!==null?g(e):null,e=e===null?null:e.stateNode,e};var eE={bundleType:0,version:"19.2.7",rendererPackageName:"react-dom",currentDispatcherRef:z,reconcilerVersion:"19.2.7"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Su=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Su.isDisabled&&Su.supportsFiber)try{Zt=Su.inject(eE),qt=Su}catch{}}return Il.createRoot=function(e,i){if(!l(e))throw Error(a(299));var r=!1,o="",u=mv,h=gv,S=vv;return i!=null&&(i.unstable_strictMode===!0&&(r=!0),i.identifierPrefix!==void 0&&(o=i.identifierPrefix),i.onUncaughtError!==void 0&&(u=i.onUncaughtError),i.onCaughtError!==void 0&&(h=i.onCaughtError),i.onRecoverableError!==void 0&&(S=i.onRecoverableError)),i=Z0(e,1,!1,null,null,r,o,null,u,h,S,o_),e[ea]=i.current,$h(e),new _d(i)},Il.hydrateRoot=function(e,i,r){if(!l(e))throw Error(a(299));var o=!1,u="",h=mv,S=gv,T=vv,B=null;return r!=null&&(r.unstable_strictMode===!0&&(o=!0),r.identifierPrefix!==void 0&&(u=r.identifierPrefix),r.onUncaughtError!==void 0&&(h=r.onUncaughtError),r.onCaughtError!==void 0&&(S=r.onCaughtError),r.onRecoverableError!==void 0&&(T=r.onRecoverableError),r.formState!==void 0&&(B=r.formState)),i=Z0(e,1,!0,i,r??null,o,u,B,h,S,T,o_),i.context=K0(null),r=i.current,o=hi(),o=Cs(o),u=Xa(o),u.callback=null,ja(r,u,o),r=o,i.current.lanes=r,Rn(i,r),Yi(i),e[ea]=i.current,$h(e),new xu(i)},Il.version="19.2.7",Il}var y_;function hE(){if(y_)return Md.exports;y_=1;function s(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(s)}catch(t){console.error(t)}}return s(),Md.exports=fE(),Md.exports}var dE=hE();const pE=ky(dE);var oc=class{constructor(){this.listeners=new Set,this.subscribe=this.subscribe.bind(this)}subscribe(s){return this.listeners.add(s),this.onSubscribe(),()=>{this.listeners.delete(s),this.onUnsubscribe()}}hasListeners(){return this.listeners.size>0}onSubscribe(){}onUnsubscribe(){}},or,gs,xo,Ly,mE=(Ly=class extends oc{constructor(){super();te(this,or);te(this,gs);te(this,xo);zt(this,xo,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t();return window.addEventListener("visibilitychange",n,!1),()=>{window.removeEventListener("visibilitychange",n)}}})}onSubscribe(){j(this,gs)||this.setEventListener(j(this,xo))}onUnsubscribe(){var t;this.hasListeners()||((t=j(this,gs))==null||t.call(this),zt(this,gs,void 0))}setEventListener(t){var n;zt(this,xo,t),(n=j(this,gs))==null||n.call(this),zt(this,gs,t(a=>{typeof a=="boolean"?this.setFocused(a):this.onFocus()}))}setFocused(t){j(this,or)!==t&&(zt(this,or,t),this.onFocus())}onFocus(){const t=this.isFocused();this.listeners.forEach(n=>{n(t)})}isFocused(){var t;return typeof j(this,or)=="boolean"?j(this,or):((t=globalThis.document)==null?void 0:t.visibilityState)!=="hidden"}},or=new WeakMap,gs=new WeakMap,xo=new WeakMap,Ly),fm=new mE,gE={setTimeout:(s,t)=>setTimeout(s,t),clearTimeout:s=>clearTimeout(s),setInterval:(s,t)=>setInterval(s,t),clearInterval:s=>clearInterval(s)},vs,cm,Oy,vE=(Oy=class{constructor(){te(this,vs,gE);te(this,cm,!1)}setTimeoutProvider(s){zt(this,vs,s)}setTimeout(s,t){return j(this,vs).setTimeout(s,t)}clearTimeout(s){j(this,vs).clearTimeout(s)}setInterval(s,t){return j(this,vs).setInterval(s,t)}clearInterval(s){j(this,vs).clearInterval(s)}},vs=new WeakMap,cm=new WeakMap,Oy),ir=new vE;function _E(s){setTimeout(s,0)}var yE=typeof window>"u"||"Deno"in globalThis;function ni(){}function xE(s,t){return typeof s=="function"?s(t):s}function rp(s){return typeof s=="number"&&s>=0&&s!==1/0}function Xy(s,t){return Math.max(s+(t||0)-Date.now(),0)}function bs(s,t){return typeof s=="function"?s(t):s}function gi(s,t){return typeof s=="function"?s(t):s}function x_(s,t){const{type:n="all",exact:a,fetchStatus:l,predicate:c,queryKey:f,stale:d}=s;if(f){if(a){if(t.queryHash!==hm(f,t.options))return!1}else if(!Jl(t.queryKey,f))return!1}if(n!=="all"){const p=t.isActive();if(n==="active"&&!p||n==="inactive"&&p)return!1}return!(typeof d=="boolean"&&t.isStale()!==d||l&&l!==t.state.fetchStatus||c&&!c(t))}function S_(s,t){const{exact:n,status:a,predicate:l,mutationKey:c}=s;if(c){if(!t.options.mutationKey)return!1;if(n){if(Kl(t.options.mutationKey)!==Kl(c))return!1}else if(!Jl(t.options.mutationKey,c))return!1}return!(a&&t.state.status!==a||l&&!l(t))}function hm(s,t){return((t==null?void 0:t.queryKeyHashFn)||Kl)(s)}function Kl(s){return JSON.stringify(s,(t,n)=>lp(n)?Object.keys(n).sort().reduce((a,l)=>(a[l]=n[l],a),{}):n)}function Jl(s,t){return s===t?!0:typeof s!=typeof t?!1:s&&t&&typeof s=="object"&&typeof t=="object"?Object.keys(t).every(n=>Jl(s[n],t[n])):!1}var SE=Object.prototype.hasOwnProperty;function jy(s,t,n=0){if(s===t)return s;if(n>500)return t;const a=M_(s)&&M_(t);if(!a&&!(lp(s)&&lp(t)))return t;const c=(a?s:Object.keys(s)).length,f=a?t:Object.keys(t),d=f.length,p=a?new Array(d):{};let m=0;for(let g=0;g<d;g++){const v=a?g:f[g],y=s[v],x=t[v];if(y===x){p[v]=y,(a?g<c:SE.call(s,v))&&m++;continue}if(y===null||x===null||typeof y!="object"||typeof x!="object"){p[v]=x;continue}const E=jy(y,x,n+1);p[v]=E,E===y&&m++}return c===d&&m===c?s:p}function op(s,t){if(!t||Object.keys(s).length!==Object.keys(t).length)return!1;for(const n in s)if(s[n]!==t[n])return!1;return!0}function M_(s){return Array.isArray(s)&&s.length===Object.keys(s).length}function lp(s){if(!E_(s))return!1;const t=s.constructor;if(t===void 0)return!0;const n=t.prototype;return!(!E_(n)||!n.hasOwnProperty("isPrototypeOf")||Object.getPrototypeOf(s)!==Object.prototype)}function E_(s){return Object.prototype.toString.call(s)==="[object Object]"}function ME(s){return new Promise(t=>{ir.setTimeout(t,s)})}function cp(s,t,n){return typeof n.structuralSharing=="function"?n.structuralSharing(s,t):n.structuralSharing!==!1?jy(s,t):t}function EE(s,t,n=0){const a=[...s,t];return n&&a.length>n?a.slice(1):a}function bE(s,t,n=0){const a=[t,...s];return n&&a.length>n?a.slice(0,-1):a}var dm=Symbol();function qy(s,t){return!s.queryFn&&(t!=null&&t.initialPromise)?()=>t.initialPromise:!s.queryFn||s.queryFn===dm?()=>Promise.reject(new Error(`Missing queryFn: '${s.queryHash}'`)):s.queryFn}function Wy(s,t){return typeof s=="function"?s(...t):!!s}function TE(s,t,n){let a=!1,l;return Object.defineProperty(s,"signal",{enumerable:!0,get:()=>(l??(l=t()),a||(a=!0,l.aborted?n():l.addEventListener("abort",n,{once:!0})),l)}),s}var $l=(()=>{let s=()=>yE;return{isServer(){return s()},setIsServer(t){s=t}}})();function up(){let s,t;const n=new Promise((l,c)=>{s=l,t=c});n.status="pending",n.catch(()=>{});function a(l){Object.assign(n,l),delete n.resolve,delete n.reject}return n.resolve=l=>{a({status:"fulfilled",value:l}),s(l)},n.reject=l=>{a({status:"rejected",reason:l}),t(l)},n}var AE=_E;function CE(){let s=[],t=0,n=d=>{d()},a=d=>{d()},l=AE;const c=d=>{t?s.push(d):l(()=>{n(d)})},f=()=>{const d=s;s=[],d.length&&l(()=>{a(()=>{d.forEach(p=>{n(p)})})})};return{batch:d=>{let p;t++;try{p=d()}finally{t--,t||f()}return p},batchCalls:d=>(...p)=>{c(()=>{d(...p)})},schedule:c,setNotifyFunction:d=>{n=d},setBatchNotifyFunction:d=>{a=d},setScheduler:d=>{l=d}}}var On=CE(),So,_s,Mo,Py,RE=(Py=class extends oc{constructor(){super();te(this,So,!0);te(this,_s);te(this,Mo);zt(this,Mo,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t(!0),a=()=>t(!1);return window.addEventListener("online",n,!1),window.addEventListener("offline",a,!1),()=>{window.removeEventListener("online",n),window.removeEventListener("offline",a)}}})}onSubscribe(){j(this,_s)||this.setEventListener(j(this,Mo))}onUnsubscribe(){var t;this.hasListeners()||((t=j(this,_s))==null||t.call(this),zt(this,_s,void 0))}setEventListener(t){var n;zt(this,Mo,t),(n=j(this,_s))==null||n.call(this),zt(this,_s,t(this.setOnline.bind(this)))}setOnline(t){j(this,So)!==t&&(zt(this,So,t),this.listeners.forEach(a=>{a(t)}))}isOnline(){return j(this,So)}},So=new WeakMap,_s=new WeakMap,Mo=new WeakMap,Py),tf=new RE;function wE(s){return Math.min(1e3*2**s,3e4)}function Yy(s){return(s??"online")==="online"?tf.isOnline():!0}var fp=class extends Error{constructor(s){super("CancelledError"),this.revert=s==null?void 0:s.revert,this.silent=s==null?void 0:s.silent}};function Qy(s){let t=!1,n=0,a;const l=up(),c=()=>l.status!=="pending",f=b=>{var M;if(!c()){const _=new fp(b);y(_),(M=s.onCancel)==null||M.call(s,_)}},d=()=>{t=!0},p=()=>{t=!1},m=()=>fm.isFocused()&&(s.networkMode==="always"||tf.isOnline())&&s.canRun(),g=()=>Yy(s.networkMode)&&s.canRun(),v=b=>{c()||(a==null||a(),l.resolve(b))},y=b=>{c()||(a==null||a(),l.reject(b))},x=()=>new Promise(b=>{var M;a=_=>{(c()||m())&&b(_)},(M=s.onPause)==null||M.call(s)}).then(()=>{var b;a=void 0,c()||(b=s.onContinue)==null||b.call(s)}),E=()=>{if(c())return;let b;const M=n===0?s.initialPromise:void 0;try{b=M??s.fn()}catch(_){b=Promise.reject(_)}Promise.resolve(b).then(v).catch(_=>{var F;if(c())return;const I=s.retry??($l.isServer()?0:3),N=s.retryDelay??wE,C=typeof N=="function"?N(n,_):N,V=I===!0||typeof I=="number"&&n<I||typeof I=="function"&&I(n,_);if(t||!V){y(_);return}n++,(F=s.onFail)==null||F.call(s,n,_),ME(C).then(()=>m()?void 0:x()).then(()=>{t?y(_):E()})})};return{promise:l,status:()=>l.status,cancel:f,continue:()=>(a==null||a(),l),cancelRetry:d,continueRetry:p,canStart:g,start:()=>(g()?E():x().then(E),l)}}var lr,zy,Zy=(zy=class{constructor(){te(this,lr)}destroy(){this.clearGcTimeout()}scheduleGc(){this.clearGcTimeout(),rp(this.gcTime)&&zt(this,lr,ir.setTimeout(()=>{this.optionalRemove()},this.gcTime))}updateGcTime(s){this.gcTime=Math.max(this.gcTime||0,s??($l.isServer()?1/0:300*1e3))}clearGcTimeout(){j(this,lr)!==void 0&&(ir.clearTimeout(j(this,lr)),zt(this,lr,void 0))}},lr=new WeakMap,zy);function DE(s){return{onFetch:(t,n)=>{var g,v,y,x,E;const a=t.options,l=(y=(v=(g=t.fetchOptions)==null?void 0:g.meta)==null?void 0:v.fetchMore)==null?void 0:y.direction,c=((x=t.state.data)==null?void 0:x.pages)||[],f=((E=t.state.data)==null?void 0:E.pageParams)||[];let d={pages:[],pageParams:[]},p=0;const m=async()=>{let b=!1;const M=N=>{TE(N,()=>t.signal,()=>b=!0)},_=qy(t.options,t.fetchOptions),I=async(N,C,V)=>{if(b)return Promise.reject(t.signal.reason);if(C==null&&N.pages.length)return Promise.resolve(N);const P=(()=>{const H={client:t.client,queryKey:t.queryKey,pageParam:C,direction:V?"backward":"forward",meta:t.options.meta};return M(H),H})(),G=await _(P),{maxPages:U}=t.options,w=V?bE:EE;return{pages:w(N.pages,G,U),pageParams:w(N.pageParams,C,U)}};if(l&&c.length){const N=l==="backward",C=N?UE:b_,V={pages:c,pageParams:f},F=C(a,V);d=await I(V,F,N)}else{const N=s??c.length;do{const C=p===0?f[0]??a.initialPageParam:b_(a,d);if(p>0&&C==null)break;d=await I(d,C),p++}while(p<N)}return d};t.options.persister?t.fetchFn=()=>{var b,M;return(M=(b=t.options).persister)==null?void 0:M.call(b,m,{client:t.client,queryKey:t.queryKey,meta:t.options.meta,signal:t.signal},n)}:t.fetchFn=m}}}function b_(s,{pages:t,pageParams:n}){const a=t.length-1;return t.length>0?s.getNextPageParam(t[a],t,n[a],n):void 0}function UE(s,{pages:t,pageParams:n}){var a;return t.length>0?(a=s.getPreviousPageParam)==null?void 0:a.call(s,t[0],t,n[0],n):void 0}var Eo,cr,bo,Ri,ur,An,nc,fr,mi,Ky,Ta,Iy,NE=(Iy=class extends Zy{constructor(t){super();te(this,mi);te(this,Eo);te(this,cr);te(this,bo);te(this,Ri);te(this,ur);te(this,An);te(this,nc);te(this,fr);zt(this,fr,!1),zt(this,nc,t.defaultOptions),this.setOptions(t.options),this.observers=[],zt(this,ur,t.client),zt(this,Ri,j(this,ur).getQueryCache()),this.queryKey=t.queryKey,this.queryHash=t.queryHash,zt(this,cr,A_(this.options)),this.state=t.state??j(this,cr),this.scheduleGc()}get meta(){return this.options.meta}get queryType(){return j(this,Eo)}get promise(){var t;return(t=j(this,An))==null?void 0:t.promise}setOptions(t){if(this.options={...j(this,nc),...t},t!=null&&t._type&&zt(this,Eo,t._type),this.updateGcTime(this.options.gcTime),this.state&&this.state.data===void 0){const n=A_(this.options);n.data!==void 0&&(this.setState(T_(n.data,n.dataUpdatedAt)),zt(this,cr,n))}}optionalRemove(){!this.observers.length&&this.state.fetchStatus==="idle"&&j(this,Ri).remove(this)}setData(t,n){const a=cp(this.state.data,t,this.options);return Ae(this,mi,Ta).call(this,{data:a,type:"success",dataUpdatedAt:n==null?void 0:n.updatedAt,manual:n==null?void 0:n.manual}),a}setState(t){Ae(this,mi,Ta).call(this,{type:"setState",state:t})}cancel(t){var a,l;const n=(a=j(this,An))==null?void 0:a.promise;return(l=j(this,An))==null||l.cancel(t),n?n.then(ni).catch(ni):Promise.resolve()}destroy(){super.destroy(),this.cancel({silent:!0})}get resetState(){return j(this,cr)}reset(){this.destroy(),this.setState(this.resetState)}isActive(){return this.observers.some(t=>gi(t.options.enabled,this)!==!1)}isDisabled(){return this.getObserversCount()>0?!this.isActive():this.options.queryFn===dm||!this.isFetched()}isFetched(){return this.state.dataUpdateCount+this.state.errorUpdateCount>0}isStatic(){return this.getObserversCount()>0?this.observers.some(t=>bs(t.options.staleTime,this)==="static"):!1}isStale(){return this.getObserversCount()>0?this.observers.some(t=>t.getCurrentResult().isStale):this.state.data===void 0||this.state.isInvalidated}isStaleByTime(t=0){return this.state.data===void 0?!0:t==="static"?!1:this.state.isInvalidated?!0:!Xy(this.state.dataUpdatedAt,t)}onFocus(){var n;const t=this.observers.find(a=>a.shouldFetchOnWindowFocus());t==null||t.refetch({cancelRefetch:!1}),(n=j(this,An))==null||n.continue()}onOnline(){var n;const t=this.observers.find(a=>a.shouldFetchOnReconnect());t==null||t.refetch({cancelRefetch:!1}),(n=j(this,An))==null||n.continue()}addObserver(t){this.observers.includes(t)||(this.observers.push(t),this.clearGcTimeout(),j(this,Ri).notify({type:"observerAdded",query:this,observer:t}))}removeObserver(t){this.observers.includes(t)&&(this.observers=this.observers.filter(n=>n!==t),this.observers.length||(j(this,An)&&(j(this,fr)||Ae(this,mi,Ky).call(this)?j(this,An).cancel({revert:!0}):j(this,An).cancelRetry()),this.scheduleGc()),j(this,Ri).notify({type:"observerRemoved",query:this,observer:t}))}getObserversCount(){return this.observers.length}invalidate(){this.state.isInvalidated||Ae(this,mi,Ta).call(this,{type:"invalidate"})}async fetch(t,n){var m,g,v,y,x,E,b,M,_,I,N;if(this.state.fetchStatus!=="idle"&&((m=j(this,An))==null?void 0:m.status())!=="rejected"){if(this.state.data!==void 0&&(n!=null&&n.cancelRefetch))this.cancel({silent:!0});else if(j(this,An))return j(this,An).continueRetry(),j(this,An).promise}if(t&&this.setOptions(t),!this.options.queryFn){const C=this.observers.find(V=>V.options.queryFn);C&&this.setOptions(C.options)}const a=new AbortController,l=C=>{Object.defineProperty(C,"signal",{enumerable:!0,get:()=>(zt(this,fr,!0),a.signal)})},c=()=>{const C=qy(this.options,n),F=(()=>{const P={client:j(this,ur),queryKey:this.queryKey,meta:this.meta};return l(P),P})();return zt(this,fr,!1),this.options.persister?this.options.persister(C,F,this):C(F)},d=(()=>{const C={fetchOptions:n,options:this.options,queryKey:this.queryKey,client:j(this,ur),state:this.state,fetchFn:c};return l(C),C})(),p=j(this,Eo)==="infinite"?DE(this.options.pages):this.options.behavior;p==null||p.onFetch(d,this),zt(this,bo,this.state),(this.state.fetchStatus==="idle"||this.state.fetchMeta!==((g=d.fetchOptions)==null?void 0:g.meta))&&Ae(this,mi,Ta).call(this,{type:"fetch",meta:(v=d.fetchOptions)==null?void 0:v.meta}),zt(this,An,Qy({initialPromise:n==null?void 0:n.initialPromise,fn:d.fetchFn,onCancel:C=>{C instanceof fp&&C.revert&&this.setState({...j(this,bo),fetchStatus:"idle"}),a.abort()},onFail:(C,V)=>{Ae(this,mi,Ta).call(this,{type:"failed",failureCount:C,error:V})},onPause:()=>{Ae(this,mi,Ta).call(this,{type:"pause"})},onContinue:()=>{Ae(this,mi,Ta).call(this,{type:"continue"})},retry:d.options.retry,retryDelay:d.options.retryDelay,networkMode:d.options.networkMode,canRun:()=>!0}));try{const C=await j(this,An).start();if(C===void 0)throw new Error(`${this.queryHash} data is undefined`);return this.setData(C),(x=(y=j(this,Ri).config).onSuccess)==null||x.call(y,C,this),(b=(E=j(this,Ri).config).onSettled)==null||b.call(E,C,this.state.error,this),C}catch(C){if(C instanceof fp){if(C.silent)return j(this,An).promise;if(C.revert){if(this.state.data===void 0)throw C;return this.state.data}}throw Ae(this,mi,Ta).call(this,{type:"error",error:C}),(_=(M=j(this,Ri).config).onError)==null||_.call(M,C,this),(N=(I=j(this,Ri).config).onSettled)==null||N.call(I,this.state.data,C,this),C}finally{this.scheduleGc()}}},Eo=new WeakMap,cr=new WeakMap,bo=new WeakMap,Ri=new WeakMap,ur=new WeakMap,An=new WeakMap,nc=new WeakMap,fr=new WeakMap,mi=new WeakSet,Ky=function(){return this.state.fetchStatus==="paused"&&this.state.status==="pending"},Ta=function(t){const n=a=>{switch(t.type){case"failed":return{...a,fetchFailureCount:t.failureCount,fetchFailureReason:t.error};case"pause":return{...a,fetchStatus:"paused"};case"continue":return{...a,fetchStatus:"fetching"};case"fetch":return{...a,...Jy(a.data,this.options),fetchMeta:t.meta??null};case"success":const l={...a,...T_(t.data,t.dataUpdatedAt),dataUpdateCount:a.dataUpdateCount+1,...!t.manual&&{fetchStatus:"idle",fetchFailureCount:0,fetchFailureReason:null}};return zt(this,bo,t.manual?l:void 0),l;case"error":const c=t.error;return{...a,error:c,errorUpdateCount:a.errorUpdateCount+1,errorUpdatedAt:Date.now(),fetchFailureCount:a.fetchFailureCount+1,fetchFailureReason:c,fetchStatus:"idle",status:"error",isInvalidated:!0};case"invalidate":return{...a,isInvalidated:!0};case"setState":return{...a,...t.state}}};this.state=n(this.state),On.batch(()=>{this.observers.forEach(a=>{a.onQueryUpdate()}),j(this,Ri).notify({query:this,type:"updated",action:t})})},Iy);function Jy(s,t){return{fetchFailureCount:0,fetchFailureReason:null,fetchStatus:Yy(t.networkMode)?"fetching":"paused",...s===void 0&&{error:null,status:"pending"}}}function T_(s,t){return{data:s,dataUpdatedAt:t??Date.now(),error:null,isInvalidated:!1,status:"success"}}function A_(s){const t=typeof s.initialData=="function"?s.initialData():s.initialData,n=t!==void 0,a=n?typeof s.initialDataUpdatedAt=="function"?s.initialDataUpdatedAt():s.initialDataUpdatedAt:0;return{data:t,dataUpdateCount:0,dataUpdatedAt:n?a??Date.now():0,error:null,errorUpdateCount:0,errorUpdatedAt:0,fetchFailureCount:0,fetchFailureReason:null,fetchMeta:null,isInvalidated:!1,status:n?"success":"pending",fetchStatus:"idle"}}var ei,Re,ic,qn,hr,To,Ca,ys,ac,Ao,Co,dr,pr,xs,Ro,ze,Xl,hp,dp,pp,mp,gp,vp,_p,$y,By,LE=(By=class extends oc{constructor(t,n){super();te(this,ze);te(this,ei);te(this,Re);te(this,ic);te(this,qn);te(this,hr);te(this,To);te(this,Ca);te(this,ys);te(this,ac);te(this,Ao);te(this,Co);te(this,dr);te(this,pr);te(this,xs);te(this,Ro,new Set);this.options=n,zt(this,ei,t),zt(this,ys,null),zt(this,Ca,up()),this.bindMethods(),this.setOptions(n)}bindMethods(){this.refetch=this.refetch.bind(this)}onSubscribe(){this.listeners.size===1&&(j(this,Re).addObserver(this),C_(j(this,Re),this.options)?Ae(this,ze,Xl).call(this):this.updateResult(),Ae(this,ze,mp).call(this))}onUnsubscribe(){this.hasListeners()||this.destroy()}shouldFetchOnReconnect(){return yp(j(this,Re),this.options,this.options.refetchOnReconnect)}shouldFetchOnWindowFocus(){return yp(j(this,Re),this.options,this.options.refetchOnWindowFocus)}destroy(){this.listeners=new Set,Ae(this,ze,gp).call(this),Ae(this,ze,vp).call(this),j(this,Re).removeObserver(this)}setOptions(t){const n=this.options,a=j(this,Re);if(this.options=j(this,ei).defaultQueryOptions(t),this.options.enabled!==void 0&&typeof this.options.enabled!="boolean"&&typeof this.options.enabled!="function"&&typeof gi(this.options.enabled,j(this,Re))!="boolean")throw new Error("Expected enabled to be a boolean or a callback that returns a boolean");Ae(this,ze,_p).call(this),j(this,Re).setOptions(this.options),n._defaulted&&!op(this.options,n)&&j(this,ei).getQueryCache().notify({type:"observerOptionsUpdated",query:j(this,Re),observer:this});const l=this.hasListeners();l&&R_(j(this,Re),a,this.options,n)&&Ae(this,ze,Xl).call(this),this.updateResult(),l&&(j(this,Re)!==a||gi(this.options.enabled,j(this,Re))!==gi(n.enabled,j(this,Re))||bs(this.options.staleTime,j(this,Re))!==bs(n.staleTime,j(this,Re)))&&Ae(this,ze,hp).call(this);const c=Ae(this,ze,dp).call(this);l&&(j(this,Re)!==a||gi(this.options.enabled,j(this,Re))!==gi(n.enabled,j(this,Re))||c!==j(this,xs))&&Ae(this,ze,pp).call(this,c)}getOptimisticResult(t){const n=j(this,ei).getQueryCache().build(j(this,ei),t),a=this.createResult(n,t);return PE(this,a)&&(zt(this,qn,a),zt(this,To,this.options),zt(this,hr,j(this,Re).state)),a}getCurrentResult(){return j(this,qn)}trackResult(t,n){return new Proxy(t,{get:(a,l)=>(this.trackProp(l),n==null||n(l),l==="promise"&&(this.trackProp("data"),!this.options.experimental_prefetchInRender&&j(this,Ca).status==="pending"&&j(this,Ca).reject(new Error("experimental_prefetchInRender feature flag is not enabled"))),Reflect.get(a,l))})}trackProp(t){j(this,Ro).add(t)}getCurrentQuery(){return j(this,Re)}refetch({...t}={}){return this.fetch({...t})}fetchOptimistic(t){const n=j(this,ei).defaultQueryOptions(t),a=j(this,ei).getQueryCache().build(j(this,ei),n);return a.fetch().then(()=>this.createResult(a,n))}fetch(t){return Ae(this,ze,Xl).call(this,{...t,cancelRefetch:t.cancelRefetch??!0}).then(()=>(this.updateResult(),j(this,qn)))}createResult(t,n){var U;const a=j(this,Re),l=this.options,c=j(this,qn),f=j(this,hr),d=j(this,To),m=t!==a?t.state:j(this,ic),{state:g}=t;let v={...g},y=!1,x;if(n._optimisticResults){const w=this.hasListeners(),H=!w&&C_(t,n),ut=w&&R_(t,a,n,l);(H||ut)&&(v={...v,...Jy(g.data,t.options)}),n._optimisticResults==="isRestoring"&&(v.fetchStatus="idle")}let{error:E,errorUpdatedAt:b,status:M}=v;x=v.data;let _=!1;if(n.placeholderData!==void 0&&x===void 0&&M==="pending"){let w;c!=null&&c.isPlaceholderData&&n.placeholderData===(d==null?void 0:d.placeholderData)?(w=c.data,_=!0):w=typeof n.placeholderData=="function"?n.placeholderData((U=j(this,Co))==null?void 0:U.state.data,j(this,Co)):n.placeholderData,w!==void 0&&(M="success",x=cp(c==null?void 0:c.data,w,n),y=!0)}if(n.select&&x!==void 0&&!_)if(c&&x===(f==null?void 0:f.data)&&n.select===j(this,ac))x=j(this,Ao);else try{zt(this,ac,n.select),x=n.select(x),x=cp(c==null?void 0:c.data,x,n),zt(this,Ao,x),zt(this,ys,null)}catch(w){zt(this,ys,w)}j(this,ys)&&(E=j(this,ys),x=j(this,Ao),b=Date.now(),M="error");const I=v.fetchStatus==="fetching",N=M==="pending",C=M==="error",V=N&&I,F=x!==void 0,G={status:M,fetchStatus:v.fetchStatus,isPending:N,isSuccess:M==="success",isError:C,isInitialLoading:V,isLoading:V,data:x,dataUpdatedAt:v.dataUpdatedAt,error:E,errorUpdatedAt:b,failureCount:v.fetchFailureCount,failureReason:v.fetchFailureReason,errorUpdateCount:v.errorUpdateCount,isFetched:t.isFetched(),isFetchedAfterMount:v.dataUpdateCount>m.dataUpdateCount||v.errorUpdateCount>m.errorUpdateCount,isFetching:I,isRefetching:I&&!N,isLoadingError:C&&!F,isPaused:v.fetchStatus==="paused",isPlaceholderData:y,isRefetchError:C&&F,isStale:pm(t,n),refetch:this.refetch,promise:j(this,Ca),isEnabled:gi(n.enabled,t)!==!1};if(this.options.experimental_prefetchInRender){const w=G.data!==void 0,H=G.status==="error"&&!w,ut=ct=>{H?ct.reject(G.error):w&&ct.resolve(G.data)},ot=()=>{const ct=zt(this,Ca,G.promise=up());ut(ct)},mt=j(this,Ca);switch(mt.status){case"pending":t.queryHash===a.queryHash&&ut(mt);break;case"fulfilled":(H||G.data!==mt.value)&&ot();break;case"rejected":(!H||G.error!==mt.reason)&&ot();break}}return G}updateResult(){const t=j(this,qn),n=this.createResult(j(this,Re),this.options);if(zt(this,hr,j(this,Re).state),zt(this,To,this.options),j(this,hr).data!==void 0&&zt(this,Co,j(this,Re)),op(n,t))return;zt(this,qn,n);const a=()=>{if(!t)return!0;const{notifyOnChangeProps:l}=this.options,c=typeof l=="function"?l():l;if(c==="all"||!c&&!j(this,Ro).size)return!0;const f=new Set(c??j(this,Ro));return this.options.throwOnError&&f.add("error"),Object.keys(j(this,qn)).some(d=>{const p=d;return j(this,qn)[p]!==t[p]&&f.has(p)})};Ae(this,ze,$y).call(this,{listeners:a()})}onQueryUpdate(){this.updateResult(),this.hasListeners()&&Ae(this,ze,mp).call(this)}},ei=new WeakMap,Re=new WeakMap,ic=new WeakMap,qn=new WeakMap,hr=new WeakMap,To=new WeakMap,Ca=new WeakMap,ys=new WeakMap,ac=new WeakMap,Ao=new WeakMap,Co=new WeakMap,dr=new WeakMap,pr=new WeakMap,xs=new WeakMap,Ro=new WeakMap,ze=new WeakSet,Xl=function(t){Ae(this,ze,_p).call(this);let n=j(this,Re).fetch(this.options,t);return t!=null&&t.throwOnError||(n=n.catch(ni)),n},hp=function(){Ae(this,ze,gp).call(this);const t=bs(this.options.staleTime,j(this,Re));if($l.isServer()||j(this,qn).isStale||!rp(t))return;const a=Xy(j(this,qn).dataUpdatedAt,t)+1;zt(this,dr,ir.setTimeout(()=>{j(this,qn).isStale||this.updateResult()},a))},dp=function(){return(typeof this.options.refetchInterval=="function"?this.options.refetchInterval(j(this,Re)):this.options.refetchInterval)??!1},pp=function(t){Ae(this,ze,vp).call(this),zt(this,xs,t),!($l.isServer()||gi(this.options.enabled,j(this,Re))===!1||!rp(j(this,xs))||j(this,xs)===0)&&zt(this,pr,ir.setInterval(()=>{(this.options.refetchIntervalInBackground||fm.isFocused())&&Ae(this,ze,Xl).call(this)},j(this,xs)))},mp=function(){Ae(this,ze,hp).call(this),Ae(this,ze,pp).call(this,Ae(this,ze,dp).call(this))},gp=function(){j(this,dr)!==void 0&&(ir.clearTimeout(j(this,dr)),zt(this,dr,void 0))},vp=function(){j(this,pr)!==void 0&&(ir.clearInterval(j(this,pr)),zt(this,pr,void 0))},_p=function(){const t=j(this,ei).getQueryCache().build(j(this,ei),this.options);if(t===j(this,Re))return;const n=j(this,Re);zt(this,Re,t),zt(this,ic,t.state),this.hasListeners()&&(n==null||n.removeObserver(this),t.addObserver(this))},$y=function(t){On.batch(()=>{t.listeners&&this.listeners.forEach(n=>{n(j(this,qn))}),j(this,ei).getQueryCache().notify({query:j(this,Re),type:"observerResultsUpdated"})})},By);function OE(s,t){return gi(t.enabled,s)!==!1&&s.state.data===void 0&&!(s.state.status==="error"&&gi(t.retryOnMount,s)===!1)}function C_(s,t){return OE(s,t)||s.state.data!==void 0&&yp(s,t,t.refetchOnMount)}function yp(s,t,n){if(gi(t.enabled,s)!==!1&&bs(t.staleTime,s)!=="static"){const a=typeof n=="function"?n(s):n;return a==="always"||a!==!1&&pm(s,t)}return!1}function R_(s,t,n,a){return(s!==t||gi(a.enabled,s)===!1)&&(!n.suspense||s.state.status!=="error")&&pm(s,n)}function pm(s,t){return gi(t.enabled,s)!==!1&&s.isStaleByTime(bs(t.staleTime,s))}function PE(s,t){return!op(s.getCurrentResult(),t)}var sc,Qi,Hn,mr,Zi,ps,Fy,zE=(Fy=class extends Zy{constructor(t){super();te(this,Zi);te(this,sc);te(this,Qi);te(this,Hn);te(this,mr);zt(this,sc,t.client),this.mutationId=t.mutationId,zt(this,Hn,t.mutationCache),zt(this,Qi,[]),this.state=t.state||IE(),this.setOptions(t.options),this.scheduleGc()}setOptions(t){this.options=t,this.updateGcTime(this.options.gcTime)}get meta(){return this.options.meta}addObserver(t){j(this,Qi).includes(t)||(j(this,Qi).push(t),this.clearGcTimeout(),j(this,Hn).notify({type:"observerAdded",mutation:this,observer:t}))}removeObserver(t){zt(this,Qi,j(this,Qi).filter(n=>n!==t)),this.scheduleGc(),j(this,Hn).notify({type:"observerRemoved",mutation:this,observer:t})}optionalRemove(){j(this,Qi).length||(this.state.status==="pending"?this.scheduleGc():j(this,Hn).remove(this))}continue(){var t;return((t=j(this,mr))==null?void 0:t.continue())??this.execute(this.state.variables)}async execute(t){var f,d,p,m,g,v,y,x,E,b,M,_,I,N,C,V,F,P;const n=()=>{Ae(this,Zi,ps).call(this,{type:"continue"})},a={client:j(this,sc),meta:this.options.meta,mutationKey:this.options.mutationKey};zt(this,mr,Qy({fn:()=>this.options.mutationFn?this.options.mutationFn(t,a):Promise.reject(new Error("No mutationFn found")),onFail:(G,U)=>{Ae(this,Zi,ps).call(this,{type:"failed",failureCount:G,error:U})},onPause:()=>{Ae(this,Zi,ps).call(this,{type:"pause"})},onContinue:n,retry:this.options.retry??0,retryDelay:this.options.retryDelay,networkMode:this.options.networkMode,canRun:()=>j(this,Hn).canRun(this)}));const l=this.state.status==="pending",c=!j(this,mr).canStart();try{if(l)n();else{Ae(this,Zi,ps).call(this,{type:"pending",variables:t,isPaused:c}),j(this,Hn).config.onMutate&&await j(this,Hn).config.onMutate(t,this,a);const U=await((d=(f=this.options).onMutate)==null?void 0:d.call(f,t,a));U!==this.state.context&&Ae(this,Zi,ps).call(this,{type:"pending",context:U,variables:t,isPaused:c})}const G=await j(this,mr).start();return await((m=(p=j(this,Hn).config).onSuccess)==null?void 0:m.call(p,G,t,this.state.context,this,a)),await((v=(g=this.options).onSuccess)==null?void 0:v.call(g,G,t,this.state.context,a)),await((x=(y=j(this,Hn).config).onSettled)==null?void 0:x.call(y,G,null,this.state.variables,this.state.context,this,a)),await((b=(E=this.options).onSettled)==null?void 0:b.call(E,G,null,t,this.state.context,a)),Ae(this,Zi,ps).call(this,{type:"success",data:G}),G}catch(G){try{await((_=(M=j(this,Hn).config).onError)==null?void 0:_.call(M,G,t,this.state.context,this,a))}catch(U){Promise.reject(U)}try{await((N=(I=this.options).onError)==null?void 0:N.call(I,G,t,this.state.context,a))}catch(U){Promise.reject(U)}try{await((V=(C=j(this,Hn).config).onSettled)==null?void 0:V.call(C,void 0,G,this.state.variables,this.state.context,this,a))}catch(U){Promise.reject(U)}try{await((P=(F=this.options).onSettled)==null?void 0:P.call(F,void 0,G,t,this.state.context,a))}catch(U){Promise.reject(U)}throw Ae(this,Zi,ps).call(this,{type:"error",error:G}),G}finally{j(this,Hn).runNext(this)}}},sc=new WeakMap,Qi=new WeakMap,Hn=new WeakMap,mr=new WeakMap,Zi=new WeakSet,ps=function(t){const n=a=>{switch(t.type){case"failed":return{...a,failureCount:t.failureCount,failureReason:t.error};case"pause":return{...a,isPaused:!0};case"continue":return{...a,isPaused:!1};case"pending":return{...a,context:t.context,data:void 0,failureCount:0,failureReason:null,error:null,isPaused:t.isPaused,status:"pending",variables:t.variables,submittedAt:Date.now()};case"success":return{...a,data:t.data,failureCount:0,failureReason:null,error:null,status:"success",isPaused:!1};case"error":return{...a,data:void 0,error:t.error,failureCount:a.failureCount+1,failureReason:t.error,isPaused:!1,status:"error"}}};this.state=n(this.state),On.batch(()=>{j(this,Qi).forEach(a=>{a.onMutationUpdate(t)}),j(this,Hn).notify({mutation:this,type:"updated",action:t})})},Fy);function IE(){return{context:void 0,data:void 0,error:null,failureCount:0,failureReason:null,isPaused:!1,status:"idle",variables:void 0,submittedAt:0}}var Ra,Ii,rc,Hy,BE=(Hy=class extends oc{constructor(t={}){super();te(this,Ra);te(this,Ii);te(this,rc);this.config=t,zt(this,Ra,new Set),zt(this,Ii,new Map),zt(this,rc,0)}build(t,n,a){const l=new zE({client:t,mutationCache:this,mutationId:++Mu(this,rc)._,options:t.defaultMutationOptions(n),state:a});return this.add(l),l}add(t){j(this,Ra).add(t);const n=Eu(t);if(typeof n=="string"){const a=j(this,Ii).get(n);a?a.push(t):j(this,Ii).set(n,[t])}this.notify({type:"added",mutation:t})}remove(t){if(j(this,Ra).delete(t)){const n=Eu(t);if(typeof n=="string"){const a=j(this,Ii).get(n);if(a)if(a.length>1){const l=a.indexOf(t);l!==-1&&a.splice(l,1)}else a[0]===t&&j(this,Ii).delete(n)}}this.notify({type:"removed",mutation:t})}canRun(t){const n=Eu(t);if(typeof n=="string"){const a=j(this,Ii).get(n),l=a==null?void 0:a.find(c=>c.state.status==="pending");return!l||l===t}else return!0}runNext(t){var a;const n=Eu(t);if(typeof n=="string"){const l=(a=j(this,Ii).get(n))==null?void 0:a.find(c=>c!==t&&c.state.isPaused);return(l==null?void 0:l.continue())??Promise.resolve()}else return Promise.resolve()}clear(){On.batch(()=>{j(this,Ra).forEach(t=>{this.notify({type:"removed",mutation:t})}),j(this,Ra).clear(),j(this,Ii).clear()})}getAll(){return Array.from(j(this,Ra))}find(t){const n={exact:!0,...t};return this.getAll().find(a=>S_(n,a))}findAll(t={}){return this.getAll().filter(n=>S_(t,n))}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}resumePausedMutations(){const t=this.getAll().filter(n=>n.state.isPaused);return On.batch(()=>Promise.all(t.map(n=>n.continue().catch(ni))))}},Ra=new WeakMap,Ii=new WeakMap,rc=new WeakMap,Hy);function Eu(s){var t;return(t=s.options.scope)==null?void 0:t.id}var Ki,Gy,FE=(Gy=class extends oc{constructor(t={}){super();te(this,Ki);this.config=t,zt(this,Ki,new Map)}build(t,n,a){const l=n.queryKey,c=n.queryHash??hm(l,n);let f=this.get(c);return f||(f=new NE({client:t,queryKey:l,queryHash:c,options:t.defaultQueryOptions(n),state:a,defaultOptions:t.getQueryDefaults(l)}),this.add(f)),f}add(t){j(this,Ki).has(t.queryHash)||(j(this,Ki).set(t.queryHash,t),this.notify({type:"added",query:t}))}remove(t){const n=j(this,Ki).get(t.queryHash);n&&(t.destroy(),n===t&&j(this,Ki).delete(t.queryHash),this.notify({type:"removed",query:t}))}clear(){On.batch(()=>{this.getAll().forEach(t=>{this.remove(t)})})}get(t){return j(this,Ki).get(t)}getAll(){return[...j(this,Ki).values()]}find(t){const n={exact:!0,...t};return this.getAll().find(a=>x_(n,a))}findAll(t={}){const n=this.getAll();return Object.keys(t).length>0?n.filter(a=>x_(t,a)):n}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}onFocus(){On.batch(()=>{this.getAll().forEach(t=>{t.onFocus()})})}onOnline(){On.batch(()=>{this.getAll().forEach(t=>{t.onOnline()})})}},Ki=new WeakMap,Gy),ln,Ss,Ms,wo,Do,Es,Uo,No,Vy,HE=(Vy=class{constructor(s={}){te(this,ln);te(this,Ss);te(this,Ms);te(this,wo);te(this,Do);te(this,Es);te(this,Uo);te(this,No);zt(this,ln,s.queryCache||new FE),zt(this,Ss,s.mutationCache||new BE),zt(this,Ms,s.defaultOptions||{}),zt(this,wo,new Map),zt(this,Do,new Map),zt(this,Es,0)}mount(){Mu(this,Es)._++,j(this,Es)===1&&(zt(this,Uo,fm.subscribe(async s=>{s&&(await this.resumePausedMutations(),j(this,ln).onFocus())})),zt(this,No,tf.subscribe(async s=>{s&&(await this.resumePausedMutations(),j(this,ln).onOnline())})))}unmount(){var s,t;Mu(this,Es)._--,j(this,Es)===0&&((s=j(this,Uo))==null||s.call(this),zt(this,Uo,void 0),(t=j(this,No))==null||t.call(this),zt(this,No,void 0))}isFetching(s){return j(this,ln).findAll({...s,fetchStatus:"fetching"}).length}isMutating(s){return j(this,Ss).findAll({...s,status:"pending"}).length}getQueryData(s){var n;const t=this.defaultQueryOptions({queryKey:s});return(n=j(this,ln).get(t.queryHash))==null?void 0:n.state.data}ensureQueryData(s){const t=this.defaultQueryOptions(s),n=j(this,ln).build(this,t),a=n.state.data;return a===void 0?this.fetchQuery(s):(s.revalidateIfStale&&n.isStaleByTime(bs(t.staleTime,n))&&this.prefetchQuery(t),Promise.resolve(a))}getQueriesData(s){return j(this,ln).findAll(s).map(({queryKey:t,state:n})=>{const a=n.data;return[t,a]})}setQueryData(s,t,n){const a=this.defaultQueryOptions({queryKey:s}),l=j(this,ln).get(a.queryHash),c=l==null?void 0:l.state.data,f=xE(t,c);if(f!==void 0)return j(this,ln).build(this,a).setData(f,{...n,manual:!0})}setQueriesData(s,t,n){return On.batch(()=>j(this,ln).findAll(s).map(({queryKey:a})=>[a,this.setQueryData(a,t,n)]))}getQueryState(s){var n;const t=this.defaultQueryOptions({queryKey:s});return(n=j(this,ln).get(t.queryHash))==null?void 0:n.state}removeQueries(s){const t=j(this,ln);On.batch(()=>{t.findAll(s).forEach(n=>{t.remove(n)})})}resetQueries(s,t){const n=j(this,ln);return On.batch(()=>(n.findAll(s).forEach(a=>{a.reset()}),this.refetchQueries({type:"active",...s},t)))}cancelQueries(s,t={}){const n={revert:!0,...t},a=On.batch(()=>j(this,ln).findAll(s).map(l=>l.cancel(n)));return Promise.all(a).then(ni).catch(ni)}invalidateQueries(s,t={}){return On.batch(()=>(j(this,ln).findAll(s).forEach(n=>{n.invalidate()}),(s==null?void 0:s.refetchType)==="none"?Promise.resolve():this.refetchQueries({...s,type:(s==null?void 0:s.refetchType)??(s==null?void 0:s.type)??"active"},t)))}refetchQueries(s,t={}){const n={...t,cancelRefetch:t.cancelRefetch??!0},a=On.batch(()=>j(this,ln).findAll(s).filter(l=>!l.isDisabled()&&!l.isStatic()).map(l=>{let c=l.fetch(void 0,n);return n.throwOnError||(c=c.catch(ni)),l.state.fetchStatus==="paused"?Promise.resolve():c}));return Promise.all(a).then(ni)}fetchQuery(s){const t=this.defaultQueryOptions(s);t.retry===void 0&&(t.retry=!1);const n=j(this,ln).build(this,t);return n.isStaleByTime(bs(t.staleTime,n))?n.fetch(t):Promise.resolve(n.state.data)}prefetchQuery(s){return this.fetchQuery(s).then(ni).catch(ni)}fetchInfiniteQuery(s){return s._type="infinite",this.fetchQuery(s)}prefetchInfiniteQuery(s){return this.fetchInfiniteQuery(s).then(ni).catch(ni)}ensureInfiniteQueryData(s){return s._type="infinite",this.ensureQueryData(s)}resumePausedMutations(){return tf.isOnline()?j(this,Ss).resumePausedMutations():Promise.resolve()}getQueryCache(){return j(this,ln)}getMutationCache(){return j(this,Ss)}getDefaultOptions(){return j(this,Ms)}setDefaultOptions(s){zt(this,Ms,s)}setQueryDefaults(s,t){j(this,wo).set(Kl(s),{queryKey:s,defaultOptions:t})}getQueryDefaults(s){const t=[...j(this,wo).values()],n={};return t.forEach(a=>{Jl(s,a.queryKey)&&Object.assign(n,a.defaultOptions)}),n}setMutationDefaults(s,t){j(this,Do).set(Kl(s),{mutationKey:s,defaultOptions:t})}getMutationDefaults(s){const t=[...j(this,Do).values()],n={};return t.forEach(a=>{Jl(s,a.mutationKey)&&Object.assign(n,a.defaultOptions)}),n}defaultQueryOptions(s){if(s._defaulted)return s;const t={...j(this,Ms).queries,...this.getQueryDefaults(s.queryKey),...s,_defaulted:!0};return t.queryHash||(t.queryHash=hm(t.queryKey,t)),t.refetchOnReconnect===void 0&&(t.refetchOnReconnect=t.networkMode!=="always"),t.throwOnError===void 0&&(t.throwOnError=!!t.suspense),!t.networkMode&&t.persister&&(t.networkMode="offlineFirst"),t.queryFn===dm&&(t.enabled=!1),t}defaultMutationOptions(s){return s!=null&&s._defaulted?s:{...j(this,Ms).mutations,...(s==null?void 0:s.mutationKey)&&this.getMutationDefaults(s.mutationKey),...s,_defaulted:!0}}clear(){j(this,ln).clear(),j(this,Ss).clear()}},ln=new WeakMap,Ss=new WeakMap,Ms=new WeakMap,wo=new WeakMap,Do=new WeakMap,Es=new WeakMap,Uo=new WeakMap,No=new WeakMap,Vy),tx=pe.createContext(void 0),ex=s=>{const t=pe.useContext(tx);if(!t)throw new Error("No QueryClient set, use QueryClientProvider to set one");return t},GE=({client:s,children:t})=>(pe.useEffect(()=>(s.mount(),()=>{s.unmount()}),[s]),D.jsx(tx.Provider,{value:s,children:t})),nx=pe.createContext(!1),VE=()=>pe.useContext(nx);nx.Provider;function kE(){let s=!1;return{clearReset:()=>{s=!1},reset:()=>{s=!0},isReset:()=>s}}var XE=pe.createContext(kE()),jE=()=>pe.useContext(XE),qE=(s,t,n)=>{const a=n!=null&&n.state.error&&typeof s.throwOnError=="function"?Wy(s.throwOnError,[n.state.error,n]):s.throwOnError;(s.suspense||s.experimental_prefetchInRender||a)&&(t.isReset()||(s.retryOnMount=!1))},WE=s=>{pe.useEffect(()=>{s.clearReset()},[s])},YE=({result:s,errorResetBoundary:t,throwOnError:n,query:a,suspense:l})=>s.isError&&!t.isReset()&&!s.isFetching&&a&&(l&&s.data===void 0||Wy(n,[s.error,a])),QE=s=>{if(s.suspense){const n=l=>l==="static"?l:Math.max(l??1e3,1e3),a=s.staleTime;s.staleTime=typeof a=="function"?(...l)=>n(a(...l)):n(a),typeof s.gcTime=="number"&&(s.gcTime=Math.max(s.gcTime,1e3))}},ZE=(s,t)=>s.isLoading&&s.isFetching&&!t,KE=(s,t)=>(s==null?void 0:s.suspense)&&t.isPending,w_=(s,t,n)=>t.fetchOptimistic(s).catch(()=>{n.clearReset()});function JE(s,t,n){var x,E,b,M;const a=VE(),l=jE(),c=ex(),f=c.defaultQueryOptions(s);(E=(x=c.getDefaultOptions().queries)==null?void 0:x._experimental_beforeQuery)==null||E.call(x,f);const d=c.getQueryCache().get(f.queryHash),p=s.subscribed!==!1;f._optimisticResults=a?"isRestoring":p?"optimistic":void 0,QE(f),qE(f,l,d),WE(l);const m=!c.getQueryCache().get(f.queryHash),[g]=pe.useState(()=>new t(c,f)),v=g.getOptimisticResult(f),y=!a&&p;if(pe.useSyncExternalStore(pe.useCallback(_=>{const I=y?g.subscribe(On.batchCalls(_)):ni;return g.updateResult(),I},[g,y]),()=>g.getCurrentResult(),()=>g.getCurrentResult()),pe.useEffect(()=>{g.setOptions(f)},[f,g]),KE(f,v))throw w_(f,g,l);if(YE({result:v,errorResetBoundary:l,throwOnError:f.throwOnError,query:d,suspense:f.suspense}))throw v.error;if((M=(b=c.getDefaultOptions().queries)==null?void 0:b._experimental_afterQuery)==null||M.call(b,f,v),f.experimental_prefetchInRender&&!$l.isServer()&&ZE(v,a)){const _=m?w_(f,g,l):d==null?void 0:d.promise;_==null||_.catch(ni).finally(()=>{g.updateResult()})}return f.notifyOnChangeProps?v:g.trackResult(v)}function $E(s,t){return JE(s,LE)}/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const t1=s=>s.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),ix=(...s)=>s.filter((t,n,a)=>!!t&&t.trim()!==""&&a.indexOf(t)===n).join(" ").trim();/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var e1={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const n1=pe.forwardRef(({color:s="currentColor",size:t=24,strokeWidth:n=2,absoluteStrokeWidth:a,className:l="",children:c,iconNode:f,...d},p)=>pe.createElement("svg",{ref:p,...e1,width:t,height:t,stroke:s,strokeWidth:a?Number(n)*24/Number(t):n,className:ix("lucide",l),...d},[...f.map(([m,g])=>pe.createElement(m,g)),...Array.isArray(c)?c:[c]]));/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const an=(s,t)=>{const n=pe.forwardRef(({className:a,...l},c)=>pe.createElement(n1,{ref:c,iconNode:t,className:ix(`lucide-${t1(s)}`,a),...l}));return n.displayName=`${s}`,n};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ax=an("Activity",[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const sx=an("Bell",[["path",{d:"M10.268 21a2 2 0 0 0 3.464 0",key:"vwvbt9"}],["path",{d:"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",key:"11g9vi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const i1=an("BrainCircuit",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M9 13a4.5 4.5 0 0 0 3-4",key:"10igwf"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M12 13h4",key:"1ku699"}],["path",{d:"M12 18h6a2 2 0 0 1 2 2v1",key:"105ag5"}],["path",{d:"M12 8h8",key:"1lhi5i"}],["path",{d:"M16 8V5a2 2 0 0 1 2-2",key:"u6izg6"}],["circle",{cx:"16",cy:"13",r:".5",key:"ry7gng"}],["circle",{cx:"18",cy:"3",r:".5",key:"1aiba7"}],["circle",{cx:"20",cy:"21",r:".5",key:"yhc1fs"}],["circle",{cx:"20",cy:"8",r:".5",key:"1e43v0"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const a1=an("Brain",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z",key:"ep3f8r"}],["path",{d:"M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4",key:"1p4c4q"}],["path",{d:"M17.599 6.5a3 3 0 0 0 .399-1.375",key:"tmeiqw"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M19.938 10.5a4 4 0 0 1 .585.396",key:"1qfode"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M19.967 17.484A4 4 0 0 1 18 18",key:"159ez6"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const s1=an("Check",[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const r1=an("CircleCheck",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const o1=an("CircleOff",[["path",{d:"m2 2 20 20",key:"1ooewy"}],["path",{d:"M8.35 2.69A10 10 0 0 1 21.3 15.65",key:"1pfsoa"}],["path",{d:"M19.08 19.08A10 10 0 1 1 4.92 4.92",key:"1ablyi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const l1=an("CirclePause",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"10",x2:"10",y1:"15",y2:"9",key:"c1nkhi"}],["line",{x1:"14",x2:"14",y1:"15",y2:"9",key:"h65svq"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const c1=an("ClipboardList",[["rect",{width:"8",height:"4",x:"8",y:"2",rx:"1",ry:"1",key:"tgr4d6"}],["path",{d:"M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",key:"116196"}],["path",{d:"M12 11h4",key:"1jrz19"}],["path",{d:"M12 16h4",key:"n85exb"}],["path",{d:"M8 11h.01",key:"1dfujw"}],["path",{d:"M8 16h.01",key:"18s6g9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const u1=an("Clock",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["polyline",{points:"12 6 12 12 16 14",key:"68esgv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const f1=an("Cpu",[["rect",{width:"16",height:"16",x:"4",y:"4",rx:"2",key:"14l7u7"}],["rect",{width:"6",height:"6",x:"9",y:"9",rx:"1",key:"5aljv4"}],["path",{d:"M15 2v2",key:"13l42r"}],["path",{d:"M15 20v2",key:"15mkzm"}],["path",{d:"M2 15h2",key:"1gxd5l"}],["path",{d:"M2 9h2",key:"1bbxkp"}],["path",{d:"M20 15h2",key:"19e6y8"}],["path",{d:"M20 9h2",key:"19tzq7"}],["path",{d:"M9 2v2",key:"165o2o"}],["path",{d:"M9 20v2",key:"i2bqo8"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const h1=an("House",[["path",{d:"M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8",key:"5wwlr5"}],["path",{d:"M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"1d0kgt"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const d1=an("KeyRound",[["path",{d:"M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",key:"1s6t7t"}],["circle",{cx:"16.5",cy:"7.5",r:".5",fill:"currentColor",key:"w0ekpg"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rx=an("MessageSquare",[["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",key:"1lielz"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const p1=an("MonitorCog",[["path",{d:"M12 17v4",key:"1riwvh"}],["path",{d:"m15.2 4.9-.9-.4",key:"12wd2u"}],["path",{d:"m15.2 7.1-.9.4",key:"1r2vl7"}],["path",{d:"m16.9 3.2-.4-.9",key:"3zbo91"}],["path",{d:"m16.9 8.8-.4.9",key:"1qr2dn"}],["path",{d:"m19.5 2.3-.4.9",key:"1rjrkq"}],["path",{d:"m19.5 9.7-.4-.9",key:"heryx5"}],["path",{d:"m21.7 4.5-.9.4",key:"17fqt1"}],["path",{d:"m21.7 7.5-.9-.4",key:"14zyni"}],["path",{d:"M22 13v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7",key:"1tnzv8"}],["path",{d:"M8 21h8",key:"1ev6f3"}],["circle",{cx:"18",cy:"6",r:"3",key:"1h7g24"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const m1=an("Send",[["path",{d:"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",key:"1ffxy3"}],["path",{d:"m21.854 2.147-10.94 10.939",key:"12cjpa"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const g1=an("Server",[["rect",{width:"20",height:"8",x:"2",y:"2",rx:"2",ry:"2",key:"ngkwjq"}],["rect",{width:"20",height:"8",x:"2",y:"14",rx:"2",ry:"2",key:"iecqi9"}],["line",{x1:"6",x2:"6.01",y1:"6",y2:"6",key:"16zg32"}],["line",{x1:"6",x2:"6.01",y1:"18",y2:"18",key:"nzw8ys"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const v1=an("Settings",[["path",{d:"M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",key:"1qme2f"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ox=an("ShieldAlert",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M12 16h.01",key:"1drbdi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lx=an("ShieldCheck",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _1=an("SlidersHorizontal",[["line",{x1:"21",x2:"14",y1:"4",y2:"4",key:"obuewd"}],["line",{x1:"10",x2:"3",y1:"4",y2:"4",key:"1q6298"}],["line",{x1:"21",x2:"12",y1:"12",y2:"12",key:"1iu8h1"}],["line",{x1:"8",x2:"3",y1:"12",y2:"12",key:"ntss68"}],["line",{x1:"21",x2:"16",y1:"20",y2:"20",key:"14d8ph"}],["line",{x1:"12",x2:"3",y1:"20",y2:"20",key:"m0wm8r"}],["line",{x1:"14",x2:"14",y1:"2",y2:"6",key:"14e1ph"}],["line",{x1:"8",x2:"8",y1:"10",y2:"14",key:"1i6ji0"}],["line",{x1:"16",x2:"16",y1:"18",y2:"22",key:"1lctlv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const cx=an("TriangleAlert",[["path",{d:"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",key:"wmoenq"}],["path",{d:"M12 9v4",key:"juzpu7"}],["path",{d:"M12 17h.01",key:"p32p05"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const y1=an("WifiOff",[["path",{d:"M12 20h.01",key:"zekei9"}],["path",{d:"M8.5 16.429a5 5 0 0 1 7 0",key:"1bycff"}],["path",{d:"M5 12.859a10 10 0 0 1 5.17-2.69",key:"1dl1wf"}],["path",{d:"M19 12.859a10 10 0 0 0-2.007-1.523",key:"4k23kn"}],["path",{d:"M2 8.82a15 15 0 0 1 4.177-2.643",key:"1grhjp"}],["path",{d:"M22 8.82a15 15 0 0 0-11.288-3.764",key:"z3jwby"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ux=an("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]);async function x1(s="dashboard"){const t=s==="display"?`/display/overview${fx()}`:"/api/ui/overview",n=await fetch(t,{credentials:"include"});if(!n.ok)throw new Error(`Overview request failed: ${n.status}`);return n.json()}function fx(){if(typeof window>"u")return"";const s=new URLSearchParams(window.location.search).get("display_token");return s?`?display_token=${encodeURIComponent(s)}`:""}async function S1(s){const t=await fetch("/api/chat/send",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:s})});if(!t.ok)throw new Error(`Chat request failed: ${t.status}`);return t.json()}async function M1(s,t){const a=await fetch(`/api/approvals/${s}/${t==="approve"?"approve":"reject"}`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({})});if(!a.ok)throw new Error(`Approval ${t} failed: ${a.status}`)}function hx(s,t=!0,n="dashboard"){pe.useEffect(()=>{if(!t||typeof EventSource>"u")return;const a=fx(),l=n==="display"?`/api/ui/stream?surface=display${a?`&${a.slice(1)}`:""}`:"/api/ui/stream",c=new EventSource(l,{withCredentials:!0}),f=d=>{try{s(JSON.parse(d.data))}catch{}};for(const d of["status.changed","task.updated","tool.execution.started","tool.execution.completed","tool.execution.failed","approval.created","approval.resolved","notification.created","chat.updated","permission.changed","connection.changed","activity.updated"])c.addEventListener(d,f);return c.addEventListener("ui.snapshot",f),()=>c.close()},[t,s,n])}function E1({open:s,onClose:t}){const[n,a]=pe.useState(""),[l,c]=pe.useState([]),[f,d]=pe.useState(!1);async function p(m){m.preventDefault();const g=n.trim();if(!(!g||f)){a(""),c(v=>[...v,{role:"user",text:g}]),d(!0);try{const v=await S1(g);c(y=>[...y,{role:"aegis",text:String(v.response||v.message||"Done.")}])}catch(v){c(y=>[...y,{role:"system",text:v instanceof Error?v.message:String(v)}])}finally{d(!1)}}}return D.jsxs("aside",{className:"chat-drawer","data-open":s,"aria-hidden":!s,children:[D.jsxs("div",{className:"panel__header",style:{padding:"16px",borderBottom:"1px solid var(--aegis-border)",margin:0},children:[D.jsxs("h2",{children:[D.jsx(rx,{size:18,"aria-hidden":"true"})," Chat"]}),D.jsx("button",{className:"icon-button",onClick:t,title:"Close chat",children:D.jsx(ux,{size:16,"aria-hidden":"true"})})]}),D.jsxs("div",{className:"chat-log",children:[l.length===0?D.jsx("div",{className:"muted",children:"Chat is ready. Messages are sent through the existing AEGIS chat API."}):null,l.map((m,g)=>D.jsx("div",{className:"list-row",style:{marginBottom:8},children:D.jsxs("div",{children:[D.jsx("strong",{children:m.role}),D.jsx("div",{children:m.text})]})},`${m.role}-${g}`))]}),D.jsxs("form",{className:"chat-form",onSubmit:p,children:[D.jsx("textarea",{value:n,onChange:m=>a(m.target.value),"aria-label":"Message"}),D.jsx("button",{className:"icon-button",title:"Send message",disabled:f,children:D.jsx(m1,{size:16,"aria-hidden":"true"})})]})]})}function ar({generatedAt:s,sourceUpdatedAt:t,stale:n=!1}){const a=Math.max(0,s-t),l=n?`STALE ${D_(a)}`:a<15e3?"LIVE":`${D_(a)} ago`;return D.jsx("span",{className:"freshness","data-stale":n,children:l})}function D_(s){const t=Math.round(s/1e3);if(t<60)return`${t}s`;const n=Math.round(t/60);return n<60?`${n}m`:`${Math.round(n/60)}h`}function Lo({status:s,detail:t}){const n=(s||"UNKNOWN").toUpperCase(),a=n==="ONLINE"?r1:n==="DISABLED"||n==="UNCONFIGURED"?l1:n==="OFFLINE"?o1:cx;return D.jsxs("span",{className:"status-badge","data-status":n,title:t||n,children:[D.jsx(a,{size:14,"aria-hidden":"true"}),n]})}function b1({overview:s,recentEvents:t=[]}){return D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsxs("div",{children:[D.jsx("h2",{children:"Activity"}),D.jsx("div",{className:"muted",children:"Normalized recent signals from the overview service."})]})}),D.jsxs("div",{className:"grid",children:[t.map(n=>D.jsxs("div",{className:"list-row",children:[D.jsxs("div",{children:[D.jsx("strong",{children:n.type}),D.jsx("div",{className:"muted",children:n.message||n.source_type})]}),D.jsx("span",{className:"mono muted",children:n.server_id||n.severity||"event"})]},`${n.type}-${n.source_updated_at}-${n.message}`)),t.length===0?(s.attention.data.items||[]).map(n=>D.jsxs("div",{className:"list-row",children:[D.jsxs("div",{children:[D.jsx("strong",{children:n.title}),D.jsx("div",{className:"muted",children:n.message})]}),D.jsx("span",{className:"mono muted",children:n.kind})]},n.id)):null]})]})}function T1({approval:s,readonly:t=!1}){const[n,a]=pe.useState(""),[l,c]=pe.useState("");async function f(d){a(d),c("");try{await M1(s.approval_id,d)}catch(p){c(p instanceof Error?p.message:String(p))}finally{a("")}}return D.jsxs("article",{className:"approval-card",children:[D.jsxs("div",{className:"panel__header",children:[D.jsxs("div",{children:[D.jsx("strong",{children:s.summary||s.tool_name||"Approval required"}),D.jsx("div",{className:"muted mono",children:s.approval_id})]}),D.jsxs("span",{className:"status-badge","data-status":"WAITING",children:[D.jsx(ox,{size:14,"aria-hidden":"true"}),s.risk||"risk"]})]}),D.jsx("div",{className:"muted",children:s.reason||"Review the requested action before allowing it to continue."}),D.jsxs("div",{className:"stat-grid",children:[D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"Capability"}),D.jsx("b",{className:"mono",style:{fontSize:14},children:s.capability_id})]}),D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"Target"}),D.jsx("b",{style:{fontSize:14},children:s.target||"Not specified"})]})]}),s.preview?D.jsx("pre",{className:"panel mono",style:{whiteSpace:"pre-wrap",margin:0},children:s.preview}):null,l?D.jsx("div",{className:"attention-item","data-severity":"critical",children:l}):null,t?null:D.jsxs("div",{className:"approval-card__actions",children:[D.jsxs("button",{className:"primary-button",onClick:()=>f("approve"),disabled:!!n,children:[D.jsx(s1,{size:16,"aria-hidden":"true"})," ",n==="approve"?"Approving":"Approve"]}),D.jsxs("button",{className:"danger-button",onClick:()=>f("reject"),disabled:!!n,children:[D.jsx(ux,{size:16,"aria-hidden":"true"})," ",n==="reject"?"Rejecting":"Reject"]})]})]})}function A1({overview:s}){const t=s.approvals.data.pending||[];return D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsxs("div",{children:[D.jsx("h2",{children:"Approvals"}),D.jsx("div",{className:"muted",children:"Pending, high-risk, and expiring action requests."})]}),D.jsx(ar,{generatedAt:s.approvals.generated_at,sourceUpdatedAt:s.approvals.source_updated_at,stale:s.approvals.stale})]}),D.jsxs("div",{className:"grid",children:[t.map(n=>D.jsx(T1,{approval:n},n.approval_id)),t.length?null:D.jsx("div",{className:"attention-item","data-severity":"normal",children:"No pending approvals."})]})]})}function C1({items:s}){return s.length?D.jsx("section",{className:"attention-strip","aria-label":"Attention",children:s.slice(0,6).map(t=>{const n=t.kind==="approval"?ox:t.kind==="server"?y1:cx;return D.jsxs("article",{className:"attention-item","data-severity":t.severity,children:[D.jsxs("div",{children:[D.jsx("strong",{children:t.title}),D.jsx("div",{className:"muted",children:t.message||t.recovery_hint||"Review this item."})]}),D.jsx(n,{size:20,"aria-label":t.severity})]},t.id)})}):D.jsx("section",{className:"attention-strip","aria-label":"Attention",children:D.jsxs("div",{className:"attention-item","data-severity":"normal",children:[D.jsxs("div",{children:[D.jsx("strong",{children:"No immediate attention required"}),D.jsx("div",{className:"muted",children:"All current UI signals are within normal bounds."})]}),D.jsx(sx,{size:18,"aria-hidden":"true"})]})})}/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const mm="171",R1=0,U_=1,w1=2,dx=1,D1=2,Aa=3,As=0,ii=1,wa=2,Na=0,vo=1,xp=2,N_=3,L_=4,U1=5,er=100,N1=101,L1=102,O1=103,P1=104,z1=200,I1=201,B1=202,F1=203,Sp=204,Mp=205,H1=206,G1=207,V1=208,k1=209,X1=210,j1=211,q1=212,W1=213,Y1=214,Ep=0,bp=1,Tp=2,Oo=3,Ap=4,Cp=5,Rp=6,wp=7,px=0,Q1=1,Z1=2,Ts=0,K1=1,J1=2,$1=3,tb=4,eb=5,nb=6,ib=7,mx=300,Po=301,zo=302,Dp=303,Up=304,lf=306,Np=1e3,sr=1001,Lp=1002,Hi=1003,ab=1004,bu=1005,$i=1006,Ad=1007,rr=1008,Pa=1009,gx=1010,vx=1011,tc=1012,gm=1013,gr=1014,Da=1015,La=1016,vm=1017,_m=1018,Io=1020,_x=35902,yx=1021,xx=1022,Fi=1023,Sx=1024,Mx=1025,_o=1026,Bo=1027,Ex=1028,ym=1029,bx=1030,xm=1031,Sm=1033,Yu=33776,Qu=33777,Zu=33778,Ku=33779,Op=35840,Pp=35841,zp=35842,Ip=35843,Bp=36196,Fp=37492,Hp=37496,Gp=37808,Vp=37809,kp=37810,Xp=37811,jp=37812,qp=37813,Wp=37814,Yp=37815,Qp=37816,Zp=37817,Kp=37818,Jp=37819,$p=37820,tm=37821,Ju=36492,em=36494,nm=36495,Tx=36283,im=36284,am=36285,sm=36286,sb=3200,rb=3201,ob=0,lb=1,ms="",vi="srgb",Fo="srgb-linear",ef="linear",je="srgb",Jr=7680,O_=519,cb=512,ub=513,fb=514,Ax=515,hb=516,db=517,pb=518,mb=519,P_=35044,z_="300 es",Ua=2e3,nf=2001;class Vo{addEventListener(t,n){this._listeners===void 0&&(this._listeners={});const a=this._listeners;a[t]===void 0&&(a[t]=[]),a[t].indexOf(n)===-1&&a[t].push(n)}hasEventListener(t,n){if(this._listeners===void 0)return!1;const a=this._listeners;return a[t]!==void 0&&a[t].indexOf(n)!==-1}removeEventListener(t,n){if(this._listeners===void 0)return;const l=this._listeners[t];if(l!==void 0){const c=l.indexOf(n);c!==-1&&l.splice(c,1)}}dispatchEvent(t){if(this._listeners===void 0)return;const a=this._listeners[t.type];if(a!==void 0){t.target=this;const l=a.slice(0);for(let c=0,f=l.length;c<f;c++)l[c].call(this,t);t.target=null}}}const Bn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let I_=1234567;const ql=Math.PI/180,ec=180/Math.PI;function ko(){const s=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0,a=Math.random()*4294967295|0;return(Bn[s&255]+Bn[s>>8&255]+Bn[s>>16&255]+Bn[s>>24&255]+"-"+Bn[t&255]+Bn[t>>8&255]+"-"+Bn[t>>16&15|64]+Bn[t>>24&255]+"-"+Bn[n&63|128]+Bn[n>>8&255]+"-"+Bn[n>>16&255]+Bn[n>>24&255]+Bn[a&255]+Bn[a>>8&255]+Bn[a>>16&255]+Bn[a>>24&255]).toLowerCase()}function ge(s,t,n){return Math.max(t,Math.min(n,s))}function Mm(s,t){return(s%t+t)%t}function gb(s,t,n,a,l){return a+(s-t)*(l-a)/(n-t)}function vb(s,t,n){return s!==t?(n-s)/(t-s):0}function Wl(s,t,n){return(1-n)*s+n*t}function _b(s,t,n,a){return Wl(s,t,1-Math.exp(-n*a))}function yb(s,t=1){return t-Math.abs(Mm(s,t*2)-t)}function xb(s,t,n){return s<=t?0:s>=n?1:(s=(s-t)/(n-t),s*s*(3-2*s))}function Sb(s,t,n){return s<=t?0:s>=n?1:(s=(s-t)/(n-t),s*s*s*(s*(s*6-15)+10))}function Mb(s,t){return s+Math.floor(Math.random()*(t-s+1))}function Eb(s,t){return s+Math.random()*(t-s)}function bb(s){return s*(.5-Math.random())}function Tb(s){s!==void 0&&(I_=s);let t=I_+=1831565813;return t=Math.imul(t^t>>>15,t|1),t^=t+Math.imul(t^t>>>7,t|61),((t^t>>>14)>>>0)/4294967296}function Ab(s){return s*ql}function Cb(s){return s*ec}function Rb(s){return(s&s-1)===0&&s!==0}function wb(s){return Math.pow(2,Math.ceil(Math.log(s)/Math.LN2))}function Db(s){return Math.pow(2,Math.floor(Math.log(s)/Math.LN2))}function Ub(s,t,n,a,l){const c=Math.cos,f=Math.sin,d=c(n/2),p=f(n/2),m=c((t+a)/2),g=f((t+a)/2),v=c((t-a)/2),y=f((t-a)/2),x=c((a-t)/2),E=f((a-t)/2);switch(l){case"XYX":s.set(d*g,p*v,p*y,d*m);break;case"YZY":s.set(p*y,d*g,p*v,d*m);break;case"ZXZ":s.set(p*v,p*y,d*g,d*m);break;case"XZX":s.set(d*g,p*E,p*x,d*m);break;case"YXY":s.set(p*x,d*g,p*E,d*m);break;case"ZYZ":s.set(p*E,p*x,d*g,d*m);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+l)}}function ho(s,t){switch(t.constructor){case Float32Array:return s;case Uint32Array:return s/4294967295;case Uint16Array:return s/65535;case Uint8Array:return s/255;case Int32Array:return Math.max(s/2147483647,-1);case Int16Array:return Math.max(s/32767,-1);case Int8Array:return Math.max(s/127,-1);default:throw new Error("Invalid component type.")}}function Xn(s,t){switch(t.constructor){case Float32Array:return s;case Uint32Array:return Math.round(s*4294967295);case Uint16Array:return Math.round(s*65535);case Uint8Array:return Math.round(s*255);case Int32Array:return Math.round(s*2147483647);case Int16Array:return Math.round(s*32767);case Int8Array:return Math.round(s*127);default:throw new Error("Invalid component type.")}}const os={DEG2RAD:ql,RAD2DEG:ec,generateUUID:ko,clamp:ge,euclideanModulo:Mm,mapLinear:gb,inverseLerp:vb,lerp:Wl,damp:_b,pingpong:yb,smoothstep:xb,smootherstep:Sb,randInt:Mb,randFloat:Eb,randFloatSpread:bb,seededRandom:Tb,degToRad:Ab,radToDeg:Cb,isPowerOfTwo:Rb,ceilPowerOfTwo:wb,floorPowerOfTwo:Db,setQuaternionFromProperEuler:Ub,normalize:Xn,denormalize:ho};class Wt{constructor(t=0,n=0){Wt.prototype.isVector2=!0,this.x=t,this.y=n}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,n){return this.x=t,this.y=n,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const n=this.x,a=this.y,l=t.elements;return this.x=l[0]*n+l[3]*a+l[6],this.y=l[1]*n+l[4]*a+l[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this}clampLength(t,n){const a=this.length();return this.divideScalar(a||1).multiplyScalar(ge(a,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const a=this.dot(t)/n;return Math.acos(ge(a,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,a=this.y-t.y;return n*n+a*a}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this}lerpVectors(t,n,a){return this.x=t.x+(n.x-t.x)*a,this.y=t.y+(n.y-t.y)*a,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this}rotateAround(t,n){const a=Math.cos(n),l=Math.sin(n),c=this.x-t.x,f=this.y-t.y;return this.x=c*a-f*l+t.x,this.y=c*l+f*a+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class fe{constructor(t,n,a,l,c,f,d,p,m){fe.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,n,a,l,c,f,d,p,m)}set(t,n,a,l,c,f,d,p,m){const g=this.elements;return g[0]=t,g[1]=l,g[2]=d,g[3]=n,g[4]=c,g[5]=p,g[6]=a,g[7]=f,g[8]=m,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const n=this.elements,a=t.elements;return n[0]=a[0],n[1]=a[1],n[2]=a[2],n[3]=a[3],n[4]=a[4],n[5]=a[5],n[6]=a[6],n[7]=a[7],n[8]=a[8],this}extractBasis(t,n,a){return t.setFromMatrix3Column(this,0),n.setFromMatrix3Column(this,1),a.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const n=t.elements;return this.set(n[0],n[4],n[8],n[1],n[5],n[9],n[2],n[6],n[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const a=t.elements,l=n.elements,c=this.elements,f=a[0],d=a[3],p=a[6],m=a[1],g=a[4],v=a[7],y=a[2],x=a[5],E=a[8],b=l[0],M=l[3],_=l[6],I=l[1],N=l[4],C=l[7],V=l[2],F=l[5],P=l[8];return c[0]=f*b+d*I+p*V,c[3]=f*M+d*N+p*F,c[6]=f*_+d*C+p*P,c[1]=m*b+g*I+v*V,c[4]=m*M+g*N+v*F,c[7]=m*_+g*C+v*P,c[2]=y*b+x*I+E*V,c[5]=y*M+x*N+E*F,c[8]=y*_+x*C+E*P,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[3]*=t,n[6]*=t,n[1]*=t,n[4]*=t,n[7]*=t,n[2]*=t,n[5]*=t,n[8]*=t,this}determinant(){const t=this.elements,n=t[0],a=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8];return n*f*g-n*d*m-a*c*g+a*d*p+l*c*m-l*f*p}invert(){const t=this.elements,n=t[0],a=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8],v=g*f-d*m,y=d*p-g*c,x=m*c-f*p,E=n*v+a*y+l*x;if(E===0)return this.set(0,0,0,0,0,0,0,0,0);const b=1/E;return t[0]=v*b,t[1]=(l*m-g*a)*b,t[2]=(d*a-l*f)*b,t[3]=y*b,t[4]=(g*n-l*p)*b,t[5]=(l*c-d*n)*b,t[6]=x*b,t[7]=(a*p-m*n)*b,t[8]=(f*n-a*c)*b,this}transpose(){let t;const n=this.elements;return t=n[1],n[1]=n[3],n[3]=t,t=n[2],n[2]=n[6],n[6]=t,t=n[5],n[5]=n[7],n[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const n=this.elements;return t[0]=n[0],t[1]=n[3],t[2]=n[6],t[3]=n[1],t[4]=n[4],t[5]=n[7],t[6]=n[2],t[7]=n[5],t[8]=n[8],this}setUvTransform(t,n,a,l,c,f,d){const p=Math.cos(c),m=Math.sin(c);return this.set(a*p,a*m,-a*(p*f+m*d)+f+t,-l*m,l*p,-l*(-m*f+p*d)+d+n,0,0,1),this}scale(t,n){return this.premultiply(Cd.makeScale(t,n)),this}rotate(t){return this.premultiply(Cd.makeRotation(-t)),this}translate(t,n){return this.premultiply(Cd.makeTranslation(t,n)),this}makeTranslation(t,n){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,n,0,0,1),this}makeRotation(t){const n=Math.cos(t),a=Math.sin(t);return this.set(n,-a,0,a,n,0,0,0,1),this}makeScale(t,n){return this.set(t,0,0,0,n,0,0,0,1),this}equals(t){const n=this.elements,a=t.elements;for(let l=0;l<9;l++)if(n[l]!==a[l])return!1;return!0}fromArray(t,n=0){for(let a=0;a<9;a++)this.elements[a]=t[a+n];return this}toArray(t=[],n=0){const a=this.elements;return t[n]=a[0],t[n+1]=a[1],t[n+2]=a[2],t[n+3]=a[3],t[n+4]=a[4],t[n+5]=a[5],t[n+6]=a[6],t[n+7]=a[7],t[n+8]=a[8],t}clone(){return new this.constructor().fromArray(this.elements)}}const Cd=new fe;function Cx(s){for(let t=s.length-1;t>=0;--t)if(s[t]>=65535)return!0;return!1}function af(s){return document.createElementNS("http://www.w3.org/1999/xhtml",s)}function Nb(){const s=af("canvas");return s.style.display="block",s}const B_={};function po(s){s in B_||(B_[s]=!0,console.warn(s))}function Lb(s,t,n){return new Promise(function(a,l){function c(){switch(s.clientWaitSync(t,s.SYNC_FLUSH_COMMANDS_BIT,0)){case s.WAIT_FAILED:l();break;case s.TIMEOUT_EXPIRED:setTimeout(c,n);break;default:a()}}setTimeout(c,n)})}function Ob(s){const t=s.elements;t[2]=.5*t[2]+.5*t[3],t[6]=.5*t[6]+.5*t[7],t[10]=.5*t[10]+.5*t[11],t[14]=.5*t[14]+.5*t[15]}function Pb(s){const t=s.elements;t[11]===-1?(t[10]=-t[10]-1,t[14]=-t[14]):(t[10]=-t[10],t[14]=-t[14]+1)}const F_=new fe().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),H_=new fe().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function zb(){const s={enabled:!0,workingColorSpace:Fo,spaces:{},convert:function(l,c,f){return this.enabled===!1||c===f||!c||!f||(this.spaces[c].transfer===je&&(l.r=Oa(l.r),l.g=Oa(l.g),l.b=Oa(l.b)),this.spaces[c].primaries!==this.spaces[f].primaries&&(l.applyMatrix3(this.spaces[c].toXYZ),l.applyMatrix3(this.spaces[f].fromXYZ)),this.spaces[f].transfer===je&&(l.r=yo(l.r),l.g=yo(l.g),l.b=yo(l.b))),l},fromWorkingColorSpace:function(l,c){return this.convert(l,this.workingColorSpace,c)},toWorkingColorSpace:function(l,c){return this.convert(l,c,this.workingColorSpace)},getPrimaries:function(l){return this.spaces[l].primaries},getTransfer:function(l){return l===ms?ef:this.spaces[l].transfer},getLuminanceCoefficients:function(l,c=this.workingColorSpace){return l.fromArray(this.spaces[c].luminanceCoefficients)},define:function(l){Object.assign(this.spaces,l)},_getMatrix:function(l,c,f){return l.copy(this.spaces[c].toXYZ).multiply(this.spaces[f].fromXYZ)},_getDrawingBufferColorSpace:function(l){return this.spaces[l].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(l=this.workingColorSpace){return this.spaces[l].workingColorSpaceConfig.unpackColorSpace}},t=[.64,.33,.3,.6,.15,.06],n=[.2126,.7152,.0722],a=[.3127,.329];return s.define({[Fo]:{primaries:t,whitePoint:a,transfer:ef,toXYZ:F_,fromXYZ:H_,luminanceCoefficients:n,workingColorSpaceConfig:{unpackColorSpace:vi},outputColorSpaceConfig:{drawingBufferColorSpace:vi}},[vi]:{primaries:t,whitePoint:a,transfer:je,toXYZ:F_,fromXYZ:H_,luminanceCoefficients:n,outputColorSpaceConfig:{drawingBufferColorSpace:vi}}}),s}const Oe=zb();function Oa(s){return s<.04045?s*.0773993808:Math.pow(s*.9478672986+.0521327014,2.4)}function yo(s){return s<.0031308?s*12.92:1.055*Math.pow(s,.41666)-.055}let $r;class Ib{static getDataURL(t){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let n;if(t instanceof HTMLCanvasElement)n=t;else{$r===void 0&&($r=af("canvas")),$r.width=t.width,$r.height=t.height;const a=$r.getContext("2d");t instanceof ImageData?a.putImageData(t,0,0):a.drawImage(t,0,0,t.width,t.height),n=$r}return n.width>2048||n.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",t),n.toDataURL("image/jpeg",.6)):n.toDataURL("image/png")}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const n=af("canvas");n.width=t.width,n.height=t.height;const a=n.getContext("2d");a.drawImage(t,0,0,t.width,t.height);const l=a.getImageData(0,0,t.width,t.height),c=l.data;for(let f=0;f<c.length;f++)c[f]=Oa(c[f]/255)*255;return a.putImageData(l,0,0),n}else if(t.data){const n=t.data.slice(0);for(let a=0;a<n.length;a++)n instanceof Uint8Array||n instanceof Uint8ClampedArray?n[a]=Math.floor(Oa(n[a]/255)*255):n[a]=Oa(n[a]);return{data:n,width:t.width,height:t.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let Bb=0;class Rx{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Bb++}),this.uuid=ko(),this.data=t,this.dataReady=!0,this.version=0}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const a={uuid:this.uuid,url:""},l=this.data;if(l!==null){let c;if(Array.isArray(l)){c=[];for(let f=0,d=l.length;f<d;f++)l[f].isDataTexture?c.push(Rd(l[f].image)):c.push(Rd(l[f]))}else c=Rd(l);a.url=c}return n||(t.images[this.uuid]=a),a}}function Rd(s){return typeof HTMLImageElement<"u"&&s instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&s instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&s instanceof ImageBitmap?Ib.getDataURL(s):s.data?{data:Array.from(s.data),width:s.width,height:s.height,type:s.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Fb=0;class ai extends Vo{constructor(t=ai.DEFAULT_IMAGE,n=ai.DEFAULT_MAPPING,a=sr,l=sr,c=$i,f=rr,d=Fi,p=Pa,m=ai.DEFAULT_ANISOTROPY,g=ms){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Fb++}),this.uuid=ko(),this.name="",this.source=new Rx(t),this.mipmaps=[],this.mapping=n,this.channel=0,this.wrapS=a,this.wrapT=l,this.magFilter=c,this.minFilter=f,this.anisotropy=m,this.format=d,this.internalFormat=null,this.type=p,this.offset=new Wt(0,0),this.repeat=new Wt(1,1),this.center=new Wt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new fe,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=g,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(t=null){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const a={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(a.userData=this.userData),n||(t.textures[this.uuid]=a),a}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==mx)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case Np:t.x=t.x-Math.floor(t.x);break;case sr:t.x=t.x<0?0:1;break;case Lp:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case Np:t.y=t.y-Math.floor(t.y);break;case sr:t.y=t.y<0?0:1;break;case Lp:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}ai.DEFAULT_IMAGE=null;ai.DEFAULT_MAPPING=mx;ai.DEFAULT_ANISOTROPY=1;class qe{constructor(t=0,n=0,a=0,l=1){qe.prototype.isVector4=!0,this.x=t,this.y=n,this.z=a,this.w=l}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,n,a,l){return this.x=t,this.y=n,this.z=a,this.w=l,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;case 3:this.w=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this.w=t.w+n.w,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this.w+=t.w*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this.w=t.w-n.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const n=this.x,a=this.y,l=this.z,c=this.w,f=t.elements;return this.x=f[0]*n+f[4]*a+f[8]*l+f[12]*c,this.y=f[1]*n+f[5]*a+f[9]*l+f[13]*c,this.z=f[2]*n+f[6]*a+f[10]*l+f[14]*c,this.w=f[3]*n+f[7]*a+f[11]*l+f[15]*c,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const n=Math.sqrt(1-t.w*t.w);return n<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/n,this.y=t.y/n,this.z=t.z/n),this}setAxisAngleFromRotationMatrix(t){let n,a,l,c;const p=t.elements,m=p[0],g=p[4],v=p[8],y=p[1],x=p[5],E=p[9],b=p[2],M=p[6],_=p[10];if(Math.abs(g-y)<.01&&Math.abs(v-b)<.01&&Math.abs(E-M)<.01){if(Math.abs(g+y)<.1&&Math.abs(v+b)<.1&&Math.abs(E+M)<.1&&Math.abs(m+x+_-3)<.1)return this.set(1,0,0,0),this;n=Math.PI;const N=(m+1)/2,C=(x+1)/2,V=(_+1)/2,F=(g+y)/4,P=(v+b)/4,G=(E+M)/4;return N>C&&N>V?N<.01?(a=0,l=.707106781,c=.707106781):(a=Math.sqrt(N),l=F/a,c=P/a):C>V?C<.01?(a=.707106781,l=0,c=.707106781):(l=Math.sqrt(C),a=F/l,c=G/l):V<.01?(a=.707106781,l=.707106781,c=0):(c=Math.sqrt(V),a=P/c,l=G/c),this.set(a,l,c,n),this}let I=Math.sqrt((M-E)*(M-E)+(v-b)*(v-b)+(y-g)*(y-g));return Math.abs(I)<.001&&(I=1),this.x=(M-E)/I,this.y=(v-b)/I,this.z=(y-g)/I,this.w=Math.acos((m+x+_-1)/2),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this.w=n[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this.w=ge(this.w,t.w,n.w),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this.w=ge(this.w,t,n),this}clampLength(t,n){const a=this.length();return this.divideScalar(a||1).multiplyScalar(ge(a,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this.w+=(t.w-this.w)*n,this}lerpVectors(t,n,a){return this.x=t.x+(n.x-t.x)*a,this.y=t.y+(n.y-t.y)*a,this.z=t.z+(n.z-t.z)*a,this.w=t.w+(n.w-t.w)*a,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this.w=t[n+3],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t[n+3]=this.w,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this.w=t.getW(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Hb extends Vo{constructor(t=1,n=1,a={}){super(),this.isRenderTarget=!0,this.width=t,this.height=n,this.depth=1,this.scissor=new qe(0,0,t,n),this.scissorTest=!1,this.viewport=new qe(0,0,t,n);const l={width:t,height:n,depth:1};a=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:$i,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},a);const c=new ai(l,a.mapping,a.wrapS,a.wrapT,a.magFilter,a.minFilter,a.format,a.type,a.anisotropy,a.colorSpace);c.flipY=!1,c.generateMipmaps=a.generateMipmaps,c.internalFormat=a.internalFormat,this.textures=[];const f=a.count;for(let d=0;d<f;d++)this.textures[d]=c.clone(),this.textures[d].isRenderTargetTexture=!0;this.depthBuffer=a.depthBuffer,this.stencilBuffer=a.stencilBuffer,this.resolveDepthBuffer=a.resolveDepthBuffer,this.resolveStencilBuffer=a.resolveStencilBuffer,this.depthTexture=a.depthTexture,this.samples=a.samples}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}setSize(t,n,a=1){if(this.width!==t||this.height!==n||this.depth!==a){this.width=t,this.height=n,this.depth=a;for(let l=0,c=this.textures.length;l<c;l++)this.textures[l].image.width=t,this.textures[l].image.height=n,this.textures[l].image.depth=a;this.dispose()}this.viewport.set(0,0,t,n),this.scissor.set(0,0,t,n)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let a=0,l=t.textures.length;a<l;a++)this.textures[a]=t.textures[a].clone(),this.textures[a].isRenderTargetTexture=!0;const n=Object.assign({},t.texture.image);return this.texture.source=new Rx(n),this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Gi extends Hb{constructor(t=1,n=1,a={}){super(t,n,a),this.isWebGLRenderTarget=!0}}class wx extends ai{constructor(t=null,n=1,a=1,l=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:n,height:a,depth:l},this.magFilter=Hi,this.minFilter=Hi,this.wrapR=sr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class Gb extends ai{constructor(t=null,n=1,a=1,l=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:n,height:a,depth:l},this.magFilter=Hi,this.minFilter=Hi,this.wrapR=sr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class lc{constructor(t=0,n=0,a=0,l=1){this.isQuaternion=!0,this._x=t,this._y=n,this._z=a,this._w=l}static slerpFlat(t,n,a,l,c,f,d){let p=a[l+0],m=a[l+1],g=a[l+2],v=a[l+3];const y=c[f+0],x=c[f+1],E=c[f+2],b=c[f+3];if(d===0){t[n+0]=p,t[n+1]=m,t[n+2]=g,t[n+3]=v;return}if(d===1){t[n+0]=y,t[n+1]=x,t[n+2]=E,t[n+3]=b;return}if(v!==b||p!==y||m!==x||g!==E){let M=1-d;const _=p*y+m*x+g*E+v*b,I=_>=0?1:-1,N=1-_*_;if(N>Number.EPSILON){const V=Math.sqrt(N),F=Math.atan2(V,_*I);M=Math.sin(M*F)/V,d=Math.sin(d*F)/V}const C=d*I;if(p=p*M+y*C,m=m*M+x*C,g=g*M+E*C,v=v*M+b*C,M===1-d){const V=1/Math.sqrt(p*p+m*m+g*g+v*v);p*=V,m*=V,g*=V,v*=V}}t[n]=p,t[n+1]=m,t[n+2]=g,t[n+3]=v}static multiplyQuaternionsFlat(t,n,a,l,c,f){const d=a[l],p=a[l+1],m=a[l+2],g=a[l+3],v=c[f],y=c[f+1],x=c[f+2],E=c[f+3];return t[n]=d*E+g*v+p*x-m*y,t[n+1]=p*E+g*y+m*v-d*x,t[n+2]=m*E+g*x+d*y-p*v,t[n+3]=g*E-d*v-p*y-m*x,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,n,a,l){return this._x=t,this._y=n,this._z=a,this._w=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,n=!0){const a=t._x,l=t._y,c=t._z,f=t._order,d=Math.cos,p=Math.sin,m=d(a/2),g=d(l/2),v=d(c/2),y=p(a/2),x=p(l/2),E=p(c/2);switch(f){case"XYZ":this._x=y*g*v+m*x*E,this._y=m*x*v-y*g*E,this._z=m*g*E+y*x*v,this._w=m*g*v-y*x*E;break;case"YXZ":this._x=y*g*v+m*x*E,this._y=m*x*v-y*g*E,this._z=m*g*E-y*x*v,this._w=m*g*v+y*x*E;break;case"ZXY":this._x=y*g*v-m*x*E,this._y=m*x*v+y*g*E,this._z=m*g*E+y*x*v,this._w=m*g*v-y*x*E;break;case"ZYX":this._x=y*g*v-m*x*E,this._y=m*x*v+y*g*E,this._z=m*g*E-y*x*v,this._w=m*g*v+y*x*E;break;case"YZX":this._x=y*g*v+m*x*E,this._y=m*x*v+y*g*E,this._z=m*g*E-y*x*v,this._w=m*g*v-y*x*E;break;case"XZY":this._x=y*g*v-m*x*E,this._y=m*x*v-y*g*E,this._z=m*g*E+y*x*v,this._w=m*g*v+y*x*E;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+f)}return n===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,n){const a=n/2,l=Math.sin(a);return this._x=t.x*l,this._y=t.y*l,this._z=t.z*l,this._w=Math.cos(a),this._onChangeCallback(),this}setFromRotationMatrix(t){const n=t.elements,a=n[0],l=n[4],c=n[8],f=n[1],d=n[5],p=n[9],m=n[2],g=n[6],v=n[10],y=a+d+v;if(y>0){const x=.5/Math.sqrt(y+1);this._w=.25/x,this._x=(g-p)*x,this._y=(c-m)*x,this._z=(f-l)*x}else if(a>d&&a>v){const x=2*Math.sqrt(1+a-d-v);this._w=(g-p)/x,this._x=.25*x,this._y=(l+f)/x,this._z=(c+m)/x}else if(d>v){const x=2*Math.sqrt(1+d-a-v);this._w=(c-m)/x,this._x=(l+f)/x,this._y=.25*x,this._z=(p+g)/x}else{const x=2*Math.sqrt(1+v-a-d);this._w=(f-l)/x,this._x=(c+m)/x,this._y=(p+g)/x,this._z=.25*x}return this._onChangeCallback(),this}setFromUnitVectors(t,n){let a=t.dot(n)+1;return a<Number.EPSILON?(a=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=a):(this._x=0,this._y=-t.z,this._z=t.y,this._w=a)):(this._x=t.y*n.z-t.z*n.y,this._y=t.z*n.x-t.x*n.z,this._z=t.x*n.y-t.y*n.x,this._w=a),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(ge(this.dot(t),-1,1)))}rotateTowards(t,n){const a=this.angleTo(t);if(a===0)return this;const l=Math.min(1,n/a);return this.slerp(t,l),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,n){const a=t._x,l=t._y,c=t._z,f=t._w,d=n._x,p=n._y,m=n._z,g=n._w;return this._x=a*g+f*d+l*m-c*p,this._y=l*g+f*p+c*d-a*m,this._z=c*g+f*m+a*p-l*d,this._w=f*g-a*d-l*p-c*m,this._onChangeCallback(),this}slerp(t,n){if(n===0)return this;if(n===1)return this.copy(t);const a=this._x,l=this._y,c=this._z,f=this._w;let d=f*t._w+a*t._x+l*t._y+c*t._z;if(d<0?(this._w=-t._w,this._x=-t._x,this._y=-t._y,this._z=-t._z,d=-d):this.copy(t),d>=1)return this._w=f,this._x=a,this._y=l,this._z=c,this;const p=1-d*d;if(p<=Number.EPSILON){const x=1-n;return this._w=x*f+n*this._w,this._x=x*a+n*this._x,this._y=x*l+n*this._y,this._z=x*c+n*this._z,this.normalize(),this}const m=Math.sqrt(p),g=Math.atan2(m,d),v=Math.sin((1-n)*g)/m,y=Math.sin(n*g)/m;return this._w=f*v+this._w*y,this._x=a*v+this._x*y,this._y=l*v+this._y*y,this._z=c*v+this._z*y,this._onChangeCallback(),this}slerpQuaternions(t,n,a){return this.copy(t).slerp(n,a)}random(){const t=2*Math.PI*Math.random(),n=2*Math.PI*Math.random(),a=Math.random(),l=Math.sqrt(1-a),c=Math.sqrt(a);return this.set(l*Math.sin(t),l*Math.cos(t),c*Math.sin(n),c*Math.cos(n))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,n=0){return this._x=t[n],this._y=t[n+1],this._z=t[n+2],this._w=t[n+3],this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._w,t}fromBufferAttribute(t,n){return this._x=t.getX(n),this._y=t.getY(n),this._z=t.getZ(n),this._w=t.getW(n),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class W{constructor(t=0,n=0,a=0){W.prototype.isVector3=!0,this.x=t,this.y=n,this.z=a}set(t,n,a){return a===void 0&&(a=this.z),this.x=t,this.y=n,this.z=a,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,n){return this.x=t.x*n.x,this.y=t.y*n.y,this.z=t.z*n.z,this}applyEuler(t){return this.applyQuaternion(G_.setFromEuler(t))}applyAxisAngle(t,n){return this.applyQuaternion(G_.setFromAxisAngle(t,n))}applyMatrix3(t){const n=this.x,a=this.y,l=this.z,c=t.elements;return this.x=c[0]*n+c[3]*a+c[6]*l,this.y=c[1]*n+c[4]*a+c[7]*l,this.z=c[2]*n+c[5]*a+c[8]*l,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const n=this.x,a=this.y,l=this.z,c=t.elements,f=1/(c[3]*n+c[7]*a+c[11]*l+c[15]);return this.x=(c[0]*n+c[4]*a+c[8]*l+c[12])*f,this.y=(c[1]*n+c[5]*a+c[9]*l+c[13])*f,this.z=(c[2]*n+c[6]*a+c[10]*l+c[14])*f,this}applyQuaternion(t){const n=this.x,a=this.y,l=this.z,c=t.x,f=t.y,d=t.z,p=t.w,m=2*(f*l-d*a),g=2*(d*n-c*l),v=2*(c*a-f*n);return this.x=n+p*m+f*v-d*g,this.y=a+p*g+d*m-c*v,this.z=l+p*v+c*g-f*m,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const n=this.x,a=this.y,l=this.z,c=t.elements;return this.x=c[0]*n+c[4]*a+c[8]*l,this.y=c[1]*n+c[5]*a+c[9]*l,this.z=c[2]*n+c[6]*a+c[10]*l,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this}clampLength(t,n){const a=this.length();return this.divideScalar(a||1).multiplyScalar(ge(a,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this}lerpVectors(t,n,a){return this.x=t.x+(n.x-t.x)*a,this.y=t.y+(n.y-t.y)*a,this.z=t.z+(n.z-t.z)*a,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,n){const a=t.x,l=t.y,c=t.z,f=n.x,d=n.y,p=n.z;return this.x=l*p-c*d,this.y=c*f-a*p,this.z=a*d-l*f,this}projectOnVector(t){const n=t.lengthSq();if(n===0)return this.set(0,0,0);const a=t.dot(this)/n;return this.copy(t).multiplyScalar(a)}projectOnPlane(t){return wd.copy(this).projectOnVector(t),this.sub(wd)}reflect(t){return this.sub(wd.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const a=this.dot(t)/n;return Math.acos(ge(a,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,a=this.y-t.y,l=this.z-t.z;return n*n+a*a+l*l}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,n,a){const l=Math.sin(n)*t;return this.x=l*Math.sin(a),this.y=Math.cos(n)*t,this.z=l*Math.cos(a),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,n,a){return this.x=t*Math.sin(n),this.y=a,this.z=t*Math.cos(n),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this}setFromMatrixScale(t){const n=this.setFromMatrixColumn(t,0).length(),a=this.setFromMatrixColumn(t,1).length(),l=this.setFromMatrixColumn(t,2).length();return this.x=n,this.y=a,this.z=l,this}setFromMatrixColumn(t,n){return this.fromArray(t.elements,n*4)}setFromMatrix3Column(t,n){return this.fromArray(t.elements,n*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,n=Math.random()*2-1,a=Math.sqrt(1-n*n);return this.x=a*Math.cos(t),this.y=n,this.z=a*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const wd=new W,G_=new lc;class cc{constructor(t=new W(1/0,1/0,1/0),n=new W(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=n}set(t,n){return this.min.copy(t),this.max.copy(n),this}setFromArray(t){this.makeEmpty();for(let n=0,a=t.length;n<a;n+=3)this.expandByPoint(Oi.fromArray(t,n));return this}setFromBufferAttribute(t){this.makeEmpty();for(let n=0,a=t.count;n<a;n++)this.expandByPoint(Oi.fromBufferAttribute(t,n));return this}setFromPoints(t){this.makeEmpty();for(let n=0,a=t.length;n<a;n++)this.expandByPoint(t[n]);return this}setFromCenterAndSize(t,n){const a=Oi.copy(n).multiplyScalar(.5);return this.min.copy(t).sub(a),this.max.copy(t).add(a),this}setFromObject(t,n=!1){return this.makeEmpty(),this.expandByObject(t,n)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,n=!1){t.updateWorldMatrix(!1,!1);const a=t.geometry;if(a!==void 0){const c=a.getAttribute("position");if(n===!0&&c!==void 0&&t.isInstancedMesh!==!0)for(let f=0,d=c.count;f<d;f++)t.isMesh===!0?t.getVertexPosition(f,Oi):Oi.fromBufferAttribute(c,f),Oi.applyMatrix4(t.matrixWorld),this.expandByPoint(Oi);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),Tu.copy(t.boundingBox)):(a.boundingBox===null&&a.computeBoundingBox(),Tu.copy(a.boundingBox)),Tu.applyMatrix4(t.matrixWorld),this.union(Tu)}const l=t.children;for(let c=0,f=l.length;c<f;c++)this.expandByObject(l[c],n);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,n){return n.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Oi),Oi.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let n,a;return t.normal.x>0?(n=t.normal.x*this.min.x,a=t.normal.x*this.max.x):(n=t.normal.x*this.max.x,a=t.normal.x*this.min.x),t.normal.y>0?(n+=t.normal.y*this.min.y,a+=t.normal.y*this.max.y):(n+=t.normal.y*this.max.y,a+=t.normal.y*this.min.y),t.normal.z>0?(n+=t.normal.z*this.min.z,a+=t.normal.z*this.max.z):(n+=t.normal.z*this.max.z,a+=t.normal.z*this.min.z),n<=-t.constant&&a>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Bl),Au.subVectors(this.max,Bl),to.subVectors(t.a,Bl),eo.subVectors(t.b,Bl),no.subVectors(t.c,Bl),ls.subVectors(eo,to),cs.subVectors(no,eo),Ws.subVectors(to,no);let n=[0,-ls.z,ls.y,0,-cs.z,cs.y,0,-Ws.z,Ws.y,ls.z,0,-ls.x,cs.z,0,-cs.x,Ws.z,0,-Ws.x,-ls.y,ls.x,0,-cs.y,cs.x,0,-Ws.y,Ws.x,0];return!Dd(n,to,eo,no,Au)||(n=[1,0,0,0,1,0,0,0,1],!Dd(n,to,eo,no,Au))?!1:(Cu.crossVectors(ls,cs),n=[Cu.x,Cu.y,Cu.z],Dd(n,to,eo,no,Au))}clampPoint(t,n){return n.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Oi).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Oi).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(xa[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),xa[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),xa[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),xa[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),xa[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),xa[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),xa[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),xa[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(xa),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}}const xa=[new W,new W,new W,new W,new W,new W,new W,new W],Oi=new W,Tu=new cc,to=new W,eo=new W,no=new W,ls=new W,cs=new W,Ws=new W,Bl=new W,Au=new W,Cu=new W,Ys=new W;function Dd(s,t,n,a,l){for(let c=0,f=s.length-3;c<=f;c+=3){Ys.fromArray(s,c);const d=l.x*Math.abs(Ys.x)+l.y*Math.abs(Ys.y)+l.z*Math.abs(Ys.z),p=t.dot(Ys),m=n.dot(Ys),g=a.dot(Ys);if(Math.max(-Math.max(p,m,g),Math.min(p,m,g))>d)return!1}return!0}const Vb=new cc,Fl=new W,Ud=new W;class Em{constructor(t=new W,n=-1){this.isSphere=!0,this.center=t,this.radius=n}set(t,n){return this.center.copy(t),this.radius=n,this}setFromPoints(t,n){const a=this.center;n!==void 0?a.copy(n):Vb.setFromPoints(t).getCenter(a);let l=0;for(let c=0,f=t.length;c<f;c++)l=Math.max(l,a.distanceToSquared(t[c]));return this.radius=Math.sqrt(l),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const n=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=n*n}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,n){const a=this.center.distanceToSquared(t);return n.copy(t),a>this.radius*this.radius&&(n.sub(this.center).normalize(),n.multiplyScalar(this.radius).add(this.center)),n}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Fl.subVectors(t,this.center);const n=Fl.lengthSq();if(n>this.radius*this.radius){const a=Math.sqrt(n),l=(a-this.radius)*.5;this.center.addScaledVector(Fl,l/a),this.radius+=l}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(Ud.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Fl.copy(t.center).add(Ud)),this.expandByPoint(Fl.copy(t.center).sub(Ud))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Sa=new W,Nd=new W,Ru=new W,us=new W,Ld=new W,wu=new W,Od=new W;class kb{constructor(t=new W,n=new W(0,0,-1)){this.origin=t,this.direction=n}set(t,n){return this.origin.copy(t),this.direction.copy(n),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,n){return n.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,Sa)),this}closestPointToPoint(t,n){n.subVectors(t,this.origin);const a=n.dot(this.direction);return a<0?n.copy(this.origin):n.copy(this.origin).addScaledVector(this.direction,a)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const n=Sa.subVectors(t,this.origin).dot(this.direction);return n<0?this.origin.distanceToSquared(t):(Sa.copy(this.origin).addScaledVector(this.direction,n),Sa.distanceToSquared(t))}distanceSqToSegment(t,n,a,l){Nd.copy(t).add(n).multiplyScalar(.5),Ru.copy(n).sub(t).normalize(),us.copy(this.origin).sub(Nd);const c=t.distanceTo(n)*.5,f=-this.direction.dot(Ru),d=us.dot(this.direction),p=-us.dot(Ru),m=us.lengthSq(),g=Math.abs(1-f*f);let v,y,x,E;if(g>0)if(v=f*p-d,y=f*d-p,E=c*g,v>=0)if(y>=-E)if(y<=E){const b=1/g;v*=b,y*=b,x=v*(v+f*y+2*d)+y*(f*v+y+2*p)+m}else y=c,v=Math.max(0,-(f*y+d)),x=-v*v+y*(y+2*p)+m;else y=-c,v=Math.max(0,-(f*y+d)),x=-v*v+y*(y+2*p)+m;else y<=-E?(v=Math.max(0,-(-f*c+d)),y=v>0?-c:Math.min(Math.max(-c,-p),c),x=-v*v+y*(y+2*p)+m):y<=E?(v=0,y=Math.min(Math.max(-c,-p),c),x=y*(y+2*p)+m):(v=Math.max(0,-(f*c+d)),y=v>0?c:Math.min(Math.max(-c,-p),c),x=-v*v+y*(y+2*p)+m);else y=f>0?-c:c,v=Math.max(0,-(f*y+d)),x=-v*v+y*(y+2*p)+m;return a&&a.copy(this.origin).addScaledVector(this.direction,v),l&&l.copy(Nd).addScaledVector(Ru,y),x}intersectSphere(t,n){Sa.subVectors(t.center,this.origin);const a=Sa.dot(this.direction),l=Sa.dot(Sa)-a*a,c=t.radius*t.radius;if(l>c)return null;const f=Math.sqrt(c-l),d=a-f,p=a+f;return p<0?null:d<0?this.at(p,n):this.at(d,n)}intersectsSphere(t){return this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const n=t.normal.dot(this.direction);if(n===0)return t.distanceToPoint(this.origin)===0?0:null;const a=-(this.origin.dot(t.normal)+t.constant)/n;return a>=0?a:null}intersectPlane(t,n){const a=this.distanceToPlane(t);return a===null?null:this.at(a,n)}intersectsPlane(t){const n=t.distanceToPoint(this.origin);return n===0||t.normal.dot(this.direction)*n<0}intersectBox(t,n){let a,l,c,f,d,p;const m=1/this.direction.x,g=1/this.direction.y,v=1/this.direction.z,y=this.origin;return m>=0?(a=(t.min.x-y.x)*m,l=(t.max.x-y.x)*m):(a=(t.max.x-y.x)*m,l=(t.min.x-y.x)*m),g>=0?(c=(t.min.y-y.y)*g,f=(t.max.y-y.y)*g):(c=(t.max.y-y.y)*g,f=(t.min.y-y.y)*g),a>f||c>l||((c>a||isNaN(a))&&(a=c),(f<l||isNaN(l))&&(l=f),v>=0?(d=(t.min.z-y.z)*v,p=(t.max.z-y.z)*v):(d=(t.max.z-y.z)*v,p=(t.min.z-y.z)*v),a>p||d>l)||((d>a||a!==a)&&(a=d),(p<l||l!==l)&&(l=p),l<0)?null:this.at(a>=0?a:l,n)}intersectsBox(t){return this.intersectBox(t,Sa)!==null}intersectTriangle(t,n,a,l,c){Ld.subVectors(n,t),wu.subVectors(a,t),Od.crossVectors(Ld,wu);let f=this.direction.dot(Od),d;if(f>0){if(l)return null;d=1}else if(f<0)d=-1,f=-f;else return null;us.subVectors(this.origin,t);const p=d*this.direction.dot(wu.crossVectors(us,wu));if(p<0)return null;const m=d*this.direction.dot(Ld.cross(us));if(m<0||p+m>f)return null;const g=-d*us.dot(Od);return g<0?null:this.at(g/f,c)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class nn{constructor(t,n,a,l,c,f,d,p,m,g,v,y,x,E,b,M){nn.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,n,a,l,c,f,d,p,m,g,v,y,x,E,b,M)}set(t,n,a,l,c,f,d,p,m,g,v,y,x,E,b,M){const _=this.elements;return _[0]=t,_[4]=n,_[8]=a,_[12]=l,_[1]=c,_[5]=f,_[9]=d,_[13]=p,_[2]=m,_[6]=g,_[10]=v,_[14]=y,_[3]=x,_[7]=E,_[11]=b,_[15]=M,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new nn().fromArray(this.elements)}copy(t){const n=this.elements,a=t.elements;return n[0]=a[0],n[1]=a[1],n[2]=a[2],n[3]=a[3],n[4]=a[4],n[5]=a[5],n[6]=a[6],n[7]=a[7],n[8]=a[8],n[9]=a[9],n[10]=a[10],n[11]=a[11],n[12]=a[12],n[13]=a[13],n[14]=a[14],n[15]=a[15],this}copyPosition(t){const n=this.elements,a=t.elements;return n[12]=a[12],n[13]=a[13],n[14]=a[14],this}setFromMatrix3(t){const n=t.elements;return this.set(n[0],n[3],n[6],0,n[1],n[4],n[7],0,n[2],n[5],n[8],0,0,0,0,1),this}extractBasis(t,n,a){return t.setFromMatrixColumn(this,0),n.setFromMatrixColumn(this,1),a.setFromMatrixColumn(this,2),this}makeBasis(t,n,a){return this.set(t.x,n.x,a.x,0,t.y,n.y,a.y,0,t.z,n.z,a.z,0,0,0,0,1),this}extractRotation(t){const n=this.elements,a=t.elements,l=1/io.setFromMatrixColumn(t,0).length(),c=1/io.setFromMatrixColumn(t,1).length(),f=1/io.setFromMatrixColumn(t,2).length();return n[0]=a[0]*l,n[1]=a[1]*l,n[2]=a[2]*l,n[3]=0,n[4]=a[4]*c,n[5]=a[5]*c,n[6]=a[6]*c,n[7]=0,n[8]=a[8]*f,n[9]=a[9]*f,n[10]=a[10]*f,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromEuler(t){const n=this.elements,a=t.x,l=t.y,c=t.z,f=Math.cos(a),d=Math.sin(a),p=Math.cos(l),m=Math.sin(l),g=Math.cos(c),v=Math.sin(c);if(t.order==="XYZ"){const y=f*g,x=f*v,E=d*g,b=d*v;n[0]=p*g,n[4]=-p*v,n[8]=m,n[1]=x+E*m,n[5]=y-b*m,n[9]=-d*p,n[2]=b-y*m,n[6]=E+x*m,n[10]=f*p}else if(t.order==="YXZ"){const y=p*g,x=p*v,E=m*g,b=m*v;n[0]=y+b*d,n[4]=E*d-x,n[8]=f*m,n[1]=f*v,n[5]=f*g,n[9]=-d,n[2]=x*d-E,n[6]=b+y*d,n[10]=f*p}else if(t.order==="ZXY"){const y=p*g,x=p*v,E=m*g,b=m*v;n[0]=y-b*d,n[4]=-f*v,n[8]=E+x*d,n[1]=x+E*d,n[5]=f*g,n[9]=b-y*d,n[2]=-f*m,n[6]=d,n[10]=f*p}else if(t.order==="ZYX"){const y=f*g,x=f*v,E=d*g,b=d*v;n[0]=p*g,n[4]=E*m-x,n[8]=y*m+b,n[1]=p*v,n[5]=b*m+y,n[9]=x*m-E,n[2]=-m,n[6]=d*p,n[10]=f*p}else if(t.order==="YZX"){const y=f*p,x=f*m,E=d*p,b=d*m;n[0]=p*g,n[4]=b-y*v,n[8]=E*v+x,n[1]=v,n[5]=f*g,n[9]=-d*g,n[2]=-m*g,n[6]=x*v+E,n[10]=y-b*v}else if(t.order==="XZY"){const y=f*p,x=f*m,E=d*p,b=d*m;n[0]=p*g,n[4]=-v,n[8]=m*g,n[1]=y*v+b,n[5]=f*g,n[9]=x*v-E,n[2]=E*v-x,n[6]=d*g,n[10]=b*v+y}return n[3]=0,n[7]=0,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromQuaternion(t){return this.compose(Xb,t,jb)}lookAt(t,n,a){const l=this.elements;return di.subVectors(t,n),di.lengthSq()===0&&(di.z=1),di.normalize(),fs.crossVectors(a,di),fs.lengthSq()===0&&(Math.abs(a.z)===1?di.x+=1e-4:di.z+=1e-4,di.normalize(),fs.crossVectors(a,di)),fs.normalize(),Du.crossVectors(di,fs),l[0]=fs.x,l[4]=Du.x,l[8]=di.x,l[1]=fs.y,l[5]=Du.y,l[9]=di.y,l[2]=fs.z,l[6]=Du.z,l[10]=di.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const a=t.elements,l=n.elements,c=this.elements,f=a[0],d=a[4],p=a[8],m=a[12],g=a[1],v=a[5],y=a[9],x=a[13],E=a[2],b=a[6],M=a[10],_=a[14],I=a[3],N=a[7],C=a[11],V=a[15],F=l[0],P=l[4],G=l[8],U=l[12],w=l[1],H=l[5],ut=l[9],ot=l[13],mt=l[2],ct=l[6],z=l[10],Z=l[14],$=l[3],Et=l[7],At=l[11],O=l[15];return c[0]=f*F+d*w+p*mt+m*$,c[4]=f*P+d*H+p*ct+m*Et,c[8]=f*G+d*ut+p*z+m*At,c[12]=f*U+d*ot+p*Z+m*O,c[1]=g*F+v*w+y*mt+x*$,c[5]=g*P+v*H+y*ct+x*Et,c[9]=g*G+v*ut+y*z+x*At,c[13]=g*U+v*ot+y*Z+x*O,c[2]=E*F+b*w+M*mt+_*$,c[6]=E*P+b*H+M*ct+_*Et,c[10]=E*G+b*ut+M*z+_*At,c[14]=E*U+b*ot+M*Z+_*O,c[3]=I*F+N*w+C*mt+V*$,c[7]=I*P+N*H+C*ct+V*Et,c[11]=I*G+N*ut+C*z+V*At,c[15]=I*U+N*ot+C*Z+V*O,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[4]*=t,n[8]*=t,n[12]*=t,n[1]*=t,n[5]*=t,n[9]*=t,n[13]*=t,n[2]*=t,n[6]*=t,n[10]*=t,n[14]*=t,n[3]*=t,n[7]*=t,n[11]*=t,n[15]*=t,this}determinant(){const t=this.elements,n=t[0],a=t[4],l=t[8],c=t[12],f=t[1],d=t[5],p=t[9],m=t[13],g=t[2],v=t[6],y=t[10],x=t[14],E=t[3],b=t[7],M=t[11],_=t[15];return E*(+c*p*v-l*m*v-c*d*y+a*m*y+l*d*x-a*p*x)+b*(+n*p*x-n*m*y+c*f*y-l*f*x+l*m*g-c*p*g)+M*(+n*m*v-n*d*x-c*f*v+a*f*x+c*d*g-a*m*g)+_*(-l*d*g-n*p*v+n*d*y+l*f*v-a*f*y+a*p*g)}transpose(){const t=this.elements;let n;return n=t[1],t[1]=t[4],t[4]=n,n=t[2],t[2]=t[8],t[8]=n,n=t[6],t[6]=t[9],t[9]=n,n=t[3],t[3]=t[12],t[12]=n,n=t[7],t[7]=t[13],t[13]=n,n=t[11],t[11]=t[14],t[14]=n,this}setPosition(t,n,a){const l=this.elements;return t.isVector3?(l[12]=t.x,l[13]=t.y,l[14]=t.z):(l[12]=t,l[13]=n,l[14]=a),this}invert(){const t=this.elements,n=t[0],a=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8],v=t[9],y=t[10],x=t[11],E=t[12],b=t[13],M=t[14],_=t[15],I=v*M*m-b*y*m+b*p*x-d*M*x-v*p*_+d*y*_,N=E*y*m-g*M*m-E*p*x+f*M*x+g*p*_-f*y*_,C=g*b*m-E*v*m+E*d*x-f*b*x-g*d*_+f*v*_,V=E*v*p-g*b*p-E*d*y+f*b*y+g*d*M-f*v*M,F=n*I+a*N+l*C+c*V;if(F===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/F;return t[0]=I*P,t[1]=(b*y*c-v*M*c-b*l*x+a*M*x+v*l*_-a*y*_)*P,t[2]=(d*M*c-b*p*c+b*l*m-a*M*m-d*l*_+a*p*_)*P,t[3]=(v*p*c-d*y*c-v*l*m+a*y*m+d*l*x-a*p*x)*P,t[4]=N*P,t[5]=(g*M*c-E*y*c+E*l*x-n*M*x-g*l*_+n*y*_)*P,t[6]=(E*p*c-f*M*c-E*l*m+n*M*m+f*l*_-n*p*_)*P,t[7]=(f*y*c-g*p*c+g*l*m-n*y*m-f*l*x+n*p*x)*P,t[8]=C*P,t[9]=(E*v*c-g*b*c-E*a*x+n*b*x+g*a*_-n*v*_)*P,t[10]=(f*b*c-E*d*c+E*a*m-n*b*m-f*a*_+n*d*_)*P,t[11]=(g*d*c-f*v*c-g*a*m+n*v*m+f*a*x-n*d*x)*P,t[12]=V*P,t[13]=(g*b*l-E*v*l+E*a*y-n*b*y-g*a*M+n*v*M)*P,t[14]=(E*d*l-f*b*l-E*a*p+n*b*p+f*a*M-n*d*M)*P,t[15]=(f*v*l-g*d*l+g*a*p-n*v*p-f*a*y+n*d*y)*P,this}scale(t){const n=this.elements,a=t.x,l=t.y,c=t.z;return n[0]*=a,n[4]*=l,n[8]*=c,n[1]*=a,n[5]*=l,n[9]*=c,n[2]*=a,n[6]*=l,n[10]*=c,n[3]*=a,n[7]*=l,n[11]*=c,this}getMaxScaleOnAxis(){const t=this.elements,n=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],a=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],l=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(n,a,l))}makeTranslation(t,n,a){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,n,0,0,1,a,0,0,0,1),this}makeRotationX(t){const n=Math.cos(t),a=Math.sin(t);return this.set(1,0,0,0,0,n,-a,0,0,a,n,0,0,0,0,1),this}makeRotationY(t){const n=Math.cos(t),a=Math.sin(t);return this.set(n,0,a,0,0,1,0,0,-a,0,n,0,0,0,0,1),this}makeRotationZ(t){const n=Math.cos(t),a=Math.sin(t);return this.set(n,-a,0,0,a,n,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,n){const a=Math.cos(n),l=Math.sin(n),c=1-a,f=t.x,d=t.y,p=t.z,m=c*f,g=c*d;return this.set(m*f+a,m*d-l*p,m*p+l*d,0,m*d+l*p,g*d+a,g*p-l*f,0,m*p-l*d,g*p+l*f,c*p*p+a,0,0,0,0,1),this}makeScale(t,n,a){return this.set(t,0,0,0,0,n,0,0,0,0,a,0,0,0,0,1),this}makeShear(t,n,a,l,c,f){return this.set(1,a,c,0,t,1,f,0,n,l,1,0,0,0,0,1),this}compose(t,n,a){const l=this.elements,c=n._x,f=n._y,d=n._z,p=n._w,m=c+c,g=f+f,v=d+d,y=c*m,x=c*g,E=c*v,b=f*g,M=f*v,_=d*v,I=p*m,N=p*g,C=p*v,V=a.x,F=a.y,P=a.z;return l[0]=(1-(b+_))*V,l[1]=(x+C)*V,l[2]=(E-N)*V,l[3]=0,l[4]=(x-C)*F,l[5]=(1-(y+_))*F,l[6]=(M+I)*F,l[7]=0,l[8]=(E+N)*P,l[9]=(M-I)*P,l[10]=(1-(y+b))*P,l[11]=0,l[12]=t.x,l[13]=t.y,l[14]=t.z,l[15]=1,this}decompose(t,n,a){const l=this.elements;let c=io.set(l[0],l[1],l[2]).length();const f=io.set(l[4],l[5],l[6]).length(),d=io.set(l[8],l[9],l[10]).length();this.determinant()<0&&(c=-c),t.x=l[12],t.y=l[13],t.z=l[14],Pi.copy(this);const m=1/c,g=1/f,v=1/d;return Pi.elements[0]*=m,Pi.elements[1]*=m,Pi.elements[2]*=m,Pi.elements[4]*=g,Pi.elements[5]*=g,Pi.elements[6]*=g,Pi.elements[8]*=v,Pi.elements[9]*=v,Pi.elements[10]*=v,n.setFromRotationMatrix(Pi),a.x=c,a.y=f,a.z=d,this}makePerspective(t,n,a,l,c,f,d=Ua){const p=this.elements,m=2*c/(n-t),g=2*c/(a-l),v=(n+t)/(n-t),y=(a+l)/(a-l);let x,E;if(d===Ua)x=-(f+c)/(f-c),E=-2*f*c/(f-c);else if(d===nf)x=-f/(f-c),E=-f*c/(f-c);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+d);return p[0]=m,p[4]=0,p[8]=v,p[12]=0,p[1]=0,p[5]=g,p[9]=y,p[13]=0,p[2]=0,p[6]=0,p[10]=x,p[14]=E,p[3]=0,p[7]=0,p[11]=-1,p[15]=0,this}makeOrthographic(t,n,a,l,c,f,d=Ua){const p=this.elements,m=1/(n-t),g=1/(a-l),v=1/(f-c),y=(n+t)*m,x=(a+l)*g;let E,b;if(d===Ua)E=(f+c)*v,b=-2*v;else if(d===nf)E=c*v,b=-1*v;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+d);return p[0]=2*m,p[4]=0,p[8]=0,p[12]=-y,p[1]=0,p[5]=2*g,p[9]=0,p[13]=-x,p[2]=0,p[6]=0,p[10]=b,p[14]=-E,p[3]=0,p[7]=0,p[11]=0,p[15]=1,this}equals(t){const n=this.elements,a=t.elements;for(let l=0;l<16;l++)if(n[l]!==a[l])return!1;return!0}fromArray(t,n=0){for(let a=0;a<16;a++)this.elements[a]=t[a+n];return this}toArray(t=[],n=0){const a=this.elements;return t[n]=a[0],t[n+1]=a[1],t[n+2]=a[2],t[n+3]=a[3],t[n+4]=a[4],t[n+5]=a[5],t[n+6]=a[6],t[n+7]=a[7],t[n+8]=a[8],t[n+9]=a[9],t[n+10]=a[10],t[n+11]=a[11],t[n+12]=a[12],t[n+13]=a[13],t[n+14]=a[14],t[n+15]=a[15],t}}const io=new W,Pi=new nn,Xb=new W(0,0,0),jb=new W(1,1,1),fs=new W,Du=new W,di=new W,V_=new nn,k_=new lc;class za{constructor(t=0,n=0,a=0,l=za.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=n,this._z=a,this._order=l}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,n,a,l=this._order){return this._x=t,this._y=n,this._z=a,this._order=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,n=this._order,a=!0){const l=t.elements,c=l[0],f=l[4],d=l[8],p=l[1],m=l[5],g=l[9],v=l[2],y=l[6],x=l[10];switch(n){case"XYZ":this._y=Math.asin(ge(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(-g,x),this._z=Math.atan2(-f,c)):(this._x=Math.atan2(y,m),this._z=0);break;case"YXZ":this._x=Math.asin(-ge(g,-1,1)),Math.abs(g)<.9999999?(this._y=Math.atan2(d,x),this._z=Math.atan2(p,m)):(this._y=Math.atan2(-v,c),this._z=0);break;case"ZXY":this._x=Math.asin(ge(y,-1,1)),Math.abs(y)<.9999999?(this._y=Math.atan2(-v,x),this._z=Math.atan2(-f,m)):(this._y=0,this._z=Math.atan2(p,c));break;case"ZYX":this._y=Math.asin(-ge(v,-1,1)),Math.abs(v)<.9999999?(this._x=Math.atan2(y,x),this._z=Math.atan2(p,c)):(this._x=0,this._z=Math.atan2(-f,m));break;case"YZX":this._z=Math.asin(ge(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-g,m),this._y=Math.atan2(-v,c)):(this._x=0,this._y=Math.atan2(d,x));break;case"XZY":this._z=Math.asin(-ge(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(y,m),this._y=Math.atan2(d,c)):(this._x=Math.atan2(-g,x),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+n)}return this._order=n,a===!0&&this._onChangeCallback(),this}setFromQuaternion(t,n,a){return V_.makeRotationFromQuaternion(t),this.setFromRotationMatrix(V_,n,a)}setFromVector3(t,n=this._order){return this.set(t.x,t.y,t.z,n)}reorder(t){return k_.setFromEuler(this),this.setFromQuaternion(k_,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}za.DEFAULT_ORDER="XYZ";class Dx{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let qb=0;const X_=new W,ao=new lc,Ma=new nn,Uu=new W,Hl=new W,Wb=new W,Yb=new lc,j_=new W(1,0,0),q_=new W(0,1,0),W_=new W(0,0,1),Y_={type:"added"},Qb={type:"removed"},so={type:"childadded",child:null},Pd={type:"childremoved",child:null};class si extends Vo{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:qb++}),this.uuid=ko(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=si.DEFAULT_UP.clone();const t=new W,n=new za,a=new lc,l=new W(1,1,1);function c(){a.setFromEuler(n,!1)}function f(){n.setFromQuaternion(a,void 0,!1)}n._onChange(c),a._onChange(f),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:n},quaternion:{configurable:!0,enumerable:!0,value:a},scale:{configurable:!0,enumerable:!0,value:l},modelViewMatrix:{value:new nn},normalMatrix:{value:new fe}}),this.matrix=new nn,this.matrixWorld=new nn,this.matrixAutoUpdate=si.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Dx,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,n){this.quaternion.setFromAxisAngle(t,n)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,n){return ao.setFromAxisAngle(t,n),this.quaternion.multiply(ao),this}rotateOnWorldAxis(t,n){return ao.setFromAxisAngle(t,n),this.quaternion.premultiply(ao),this}rotateX(t){return this.rotateOnAxis(j_,t)}rotateY(t){return this.rotateOnAxis(q_,t)}rotateZ(t){return this.rotateOnAxis(W_,t)}translateOnAxis(t,n){return X_.copy(t).applyQuaternion(this.quaternion),this.position.add(X_.multiplyScalar(n)),this}translateX(t){return this.translateOnAxis(j_,t)}translateY(t){return this.translateOnAxis(q_,t)}translateZ(t){return this.translateOnAxis(W_,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(Ma.copy(this.matrixWorld).invert())}lookAt(t,n,a){t.isVector3?Uu.copy(t):Uu.set(t,n,a);const l=this.parent;this.updateWorldMatrix(!0,!1),Hl.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ma.lookAt(Hl,Uu,this.up):Ma.lookAt(Uu,Hl,this.up),this.quaternion.setFromRotationMatrix(Ma),l&&(Ma.extractRotation(l.matrixWorld),ao.setFromRotationMatrix(Ma),this.quaternion.premultiply(ao.invert()))}add(t){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.add(arguments[n]);return this}return t===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(Y_),so.child=t,this.dispatchEvent(so),so.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let a=0;a<arguments.length;a++)this.remove(arguments[a]);return this}const n=this.children.indexOf(t);return n!==-1&&(t.parent=null,this.children.splice(n,1),t.dispatchEvent(Qb),Pd.child=t,this.dispatchEvent(Pd),Pd.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),Ma.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),Ma.multiply(t.parent.matrixWorld)),t.applyMatrix4(Ma),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(Y_),so.child=t,this.dispatchEvent(so),so.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,n){if(this[t]===n)return this;for(let a=0,l=this.children.length;a<l;a++){const f=this.children[a].getObjectByProperty(t,n);if(f!==void 0)return f}}getObjectsByProperty(t,n,a=[]){this[t]===n&&a.push(this);const l=this.children;for(let c=0,f=l.length;c<f;c++)l[c].getObjectsByProperty(t,n,a);return a}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Hl,t,Wb),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Hl,Yb,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const n=this.matrixWorld.elements;return t.set(n[8],n[9],n[10]).normalize()}raycast(){}traverse(t){t(this);const n=this.children;for(let a=0,l=n.length;a<l;a++)n[a].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const n=this.children;for(let a=0,l=n.length;a<l;a++)n[a].traverseVisible(t)}traverseAncestors(t){const n=this.parent;n!==null&&(t(n),n.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const n=this.children;for(let a=0,l=n.length;a<l;a++)n[a].updateMatrixWorld(t)}updateWorldMatrix(t,n){const a=this.parent;if(t===!0&&a!==null&&a.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),n===!0){const l=this.children;for(let c=0,f=l.length;c<f;c++)l[c].updateWorldMatrix(!1,!0)}}toJSON(t){const n=t===void 0||typeof t=="string",a={};n&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},a.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const l={};l.uuid=this.uuid,l.type=this.type,this.name!==""&&(l.name=this.name),this.castShadow===!0&&(l.castShadow=!0),this.receiveShadow===!0&&(l.receiveShadow=!0),this.visible===!1&&(l.visible=!1),this.frustumCulled===!1&&(l.frustumCulled=!1),this.renderOrder!==0&&(l.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(l.userData=this.userData),l.layers=this.layers.mask,l.matrix=this.matrix.toArray(),l.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(l.matrixAutoUpdate=!1),this.isInstancedMesh&&(l.type="InstancedMesh",l.count=this.count,l.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(l.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(l.type="BatchedMesh",l.perObjectFrustumCulled=this.perObjectFrustumCulled,l.sortObjects=this.sortObjects,l.drawRanges=this._drawRanges,l.reservedRanges=this._reservedRanges,l.visibility=this._visibility,l.active=this._active,l.bounds=this._bounds.map(d=>({boxInitialized:d.boxInitialized,boxMin:d.box.min.toArray(),boxMax:d.box.max.toArray(),sphereInitialized:d.sphereInitialized,sphereRadius:d.sphere.radius,sphereCenter:d.sphere.center.toArray()})),l.maxInstanceCount=this._maxInstanceCount,l.maxVertexCount=this._maxVertexCount,l.maxIndexCount=this._maxIndexCount,l.geometryInitialized=this._geometryInitialized,l.geometryCount=this._geometryCount,l.matricesTexture=this._matricesTexture.toJSON(t),this._colorsTexture!==null&&(l.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(l.boundingSphere={center:l.boundingSphere.center.toArray(),radius:l.boundingSphere.radius}),this.boundingBox!==null&&(l.boundingBox={min:l.boundingBox.min.toArray(),max:l.boundingBox.max.toArray()}));function c(d,p){return d[p.uuid]===void 0&&(d[p.uuid]=p.toJSON(t)),p.uuid}if(this.isScene)this.background&&(this.background.isColor?l.background=this.background.toJSON():this.background.isTexture&&(l.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(l.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){l.geometry=c(t.geometries,this.geometry);const d=this.geometry.parameters;if(d!==void 0&&d.shapes!==void 0){const p=d.shapes;if(Array.isArray(p))for(let m=0,g=p.length;m<g;m++){const v=p[m];c(t.shapes,v)}else c(t.shapes,p)}}if(this.isSkinnedMesh&&(l.bindMode=this.bindMode,l.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(c(t.skeletons,this.skeleton),l.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const d=[];for(let p=0,m=this.material.length;p<m;p++)d.push(c(t.materials,this.material[p]));l.material=d}else l.material=c(t.materials,this.material);if(this.children.length>0){l.children=[];for(let d=0;d<this.children.length;d++)l.children.push(this.children[d].toJSON(t).object)}if(this.animations.length>0){l.animations=[];for(let d=0;d<this.animations.length;d++){const p=this.animations[d];l.animations.push(c(t.animations,p))}}if(n){const d=f(t.geometries),p=f(t.materials),m=f(t.textures),g=f(t.images),v=f(t.shapes),y=f(t.skeletons),x=f(t.animations),E=f(t.nodes);d.length>0&&(a.geometries=d),p.length>0&&(a.materials=p),m.length>0&&(a.textures=m),g.length>0&&(a.images=g),v.length>0&&(a.shapes=v),y.length>0&&(a.skeletons=y),x.length>0&&(a.animations=x),E.length>0&&(a.nodes=E)}return a.object=l,a;function f(d){const p=[];for(const m in d){const g=d[m];delete g.metadata,p.push(g)}return p}}clone(t){return new this.constructor().copy(this,t)}copy(t,n=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),n===!0)for(let a=0;a<t.children.length;a++){const l=t.children[a];this.add(l.clone())}return this}}si.DEFAULT_UP=new W(0,1,0);si.DEFAULT_MATRIX_AUTO_UPDATE=!0;si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const zi=new W,Ea=new W,zd=new W,ba=new W,ro=new W,oo=new W,Q_=new W,Id=new W,Bd=new W,Fd=new W,Hd=new qe,Gd=new qe,Vd=new qe;class Bi{constructor(t=new W,n=new W,a=new W){this.a=t,this.b=n,this.c=a}static getNormal(t,n,a,l){l.subVectors(a,n),zi.subVectors(t,n),l.cross(zi);const c=l.lengthSq();return c>0?l.multiplyScalar(1/Math.sqrt(c)):l.set(0,0,0)}static getBarycoord(t,n,a,l,c){zi.subVectors(l,n),Ea.subVectors(a,n),zd.subVectors(t,n);const f=zi.dot(zi),d=zi.dot(Ea),p=zi.dot(zd),m=Ea.dot(Ea),g=Ea.dot(zd),v=f*m-d*d;if(v===0)return c.set(0,0,0),null;const y=1/v,x=(m*p-d*g)*y,E=(f*g-d*p)*y;return c.set(1-x-E,E,x)}static containsPoint(t,n,a,l){return this.getBarycoord(t,n,a,l,ba)===null?!1:ba.x>=0&&ba.y>=0&&ba.x+ba.y<=1}static getInterpolation(t,n,a,l,c,f,d,p){return this.getBarycoord(t,n,a,l,ba)===null?(p.x=0,p.y=0,"z"in p&&(p.z=0),"w"in p&&(p.w=0),null):(p.setScalar(0),p.addScaledVector(c,ba.x),p.addScaledVector(f,ba.y),p.addScaledVector(d,ba.z),p)}static getInterpolatedAttribute(t,n,a,l,c,f){return Hd.setScalar(0),Gd.setScalar(0),Vd.setScalar(0),Hd.fromBufferAttribute(t,n),Gd.fromBufferAttribute(t,a),Vd.fromBufferAttribute(t,l),f.setScalar(0),f.addScaledVector(Hd,c.x),f.addScaledVector(Gd,c.y),f.addScaledVector(Vd,c.z),f}static isFrontFacing(t,n,a,l){return zi.subVectors(a,n),Ea.subVectors(t,n),zi.cross(Ea).dot(l)<0}set(t,n,a){return this.a.copy(t),this.b.copy(n),this.c.copy(a),this}setFromPointsAndIndices(t,n,a,l){return this.a.copy(t[n]),this.b.copy(t[a]),this.c.copy(t[l]),this}setFromAttributeAndIndices(t,n,a,l){return this.a.fromBufferAttribute(t,n),this.b.fromBufferAttribute(t,a),this.c.fromBufferAttribute(t,l),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return zi.subVectors(this.c,this.b),Ea.subVectors(this.a,this.b),zi.cross(Ea).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return Bi.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,n){return Bi.getBarycoord(t,this.a,this.b,this.c,n)}getInterpolation(t,n,a,l,c){return Bi.getInterpolation(t,this.a,this.b,this.c,n,a,l,c)}containsPoint(t){return Bi.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return Bi.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,n){const a=this.a,l=this.b,c=this.c;let f,d;ro.subVectors(l,a),oo.subVectors(c,a),Id.subVectors(t,a);const p=ro.dot(Id),m=oo.dot(Id);if(p<=0&&m<=0)return n.copy(a);Bd.subVectors(t,l);const g=ro.dot(Bd),v=oo.dot(Bd);if(g>=0&&v<=g)return n.copy(l);const y=p*v-g*m;if(y<=0&&p>=0&&g<=0)return f=p/(p-g),n.copy(a).addScaledVector(ro,f);Fd.subVectors(t,c);const x=ro.dot(Fd),E=oo.dot(Fd);if(E>=0&&x<=E)return n.copy(c);const b=x*m-p*E;if(b<=0&&m>=0&&E<=0)return d=m/(m-E),n.copy(a).addScaledVector(oo,d);const M=g*E-x*v;if(M<=0&&v-g>=0&&x-E>=0)return Q_.subVectors(c,l),d=(v-g)/(v-g+(x-E)),n.copy(l).addScaledVector(Q_,d);const _=1/(M+b+y);return f=b*_,d=y*_,n.copy(a).addScaledVector(ro,f).addScaledVector(oo,d)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}const Ux={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},hs={h:0,s:0,l:0},Nu={h:0,s:0,l:0};function kd(s,t,n){return n<0&&(n+=1),n>1&&(n-=1),n<1/6?s+(t-s)*6*n:n<1/2?t:n<2/3?s+(t-s)*6*(2/3-n):s}class de{constructor(t,n,a){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,n,a)}set(t,n,a){if(n===void 0&&a===void 0){const l=t;l&&l.isColor?this.copy(l):typeof l=="number"?this.setHex(l):typeof l=="string"&&this.setStyle(l)}else this.setRGB(t,n,a);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,n=vi){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Oe.toWorkingColorSpace(this,n),this}setRGB(t,n,a,l=Oe.workingColorSpace){return this.r=t,this.g=n,this.b=a,Oe.toWorkingColorSpace(this,l),this}setHSL(t,n,a,l=Oe.workingColorSpace){if(t=Mm(t,1),n=ge(n,0,1),a=ge(a,0,1),n===0)this.r=this.g=this.b=a;else{const c=a<=.5?a*(1+n):a+n-a*n,f=2*a-c;this.r=kd(f,c,t+1/3),this.g=kd(f,c,t),this.b=kd(f,c,t-1/3)}return Oe.toWorkingColorSpace(this,l),this}setStyle(t,n=vi){function a(c){c!==void 0&&parseFloat(c)<1&&console.warn("THREE.Color: Alpha component of "+t+" will be ignored.")}let l;if(l=/^(\w+)\(([^\)]*)\)/.exec(t)){let c;const f=l[1],d=l[2];switch(f){case"rgb":case"rgba":if(c=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return a(c[4]),this.setRGB(Math.min(255,parseInt(c[1],10))/255,Math.min(255,parseInt(c[2],10))/255,Math.min(255,parseInt(c[3],10))/255,n);if(c=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return a(c[4]),this.setRGB(Math.min(100,parseInt(c[1],10))/100,Math.min(100,parseInt(c[2],10))/100,Math.min(100,parseInt(c[3],10))/100,n);break;case"hsl":case"hsla":if(c=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return a(c[4]),this.setHSL(parseFloat(c[1])/360,parseFloat(c[2])/100,parseFloat(c[3])/100,n);break;default:console.warn("THREE.Color: Unknown color model "+t)}}else if(l=/^\#([A-Fa-f\d]+)$/.exec(t)){const c=l[1],f=c.length;if(f===3)return this.setRGB(parseInt(c.charAt(0),16)/15,parseInt(c.charAt(1),16)/15,parseInt(c.charAt(2),16)/15,n);if(f===6)return this.setHex(parseInt(c,16),n);console.warn("THREE.Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,n);return this}setColorName(t,n=vi){const a=Ux[t.toLowerCase()];return a!==void 0?this.setHex(a,n):console.warn("THREE.Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=Oa(t.r),this.g=Oa(t.g),this.b=Oa(t.b),this}copyLinearToSRGB(t){return this.r=yo(t.r),this.g=yo(t.g),this.b=yo(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=vi){return Oe.fromWorkingColorSpace(Fn.copy(this),t),Math.round(ge(Fn.r*255,0,255))*65536+Math.round(ge(Fn.g*255,0,255))*256+Math.round(ge(Fn.b*255,0,255))}getHexString(t=vi){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,n=Oe.workingColorSpace){Oe.fromWorkingColorSpace(Fn.copy(this),n);const a=Fn.r,l=Fn.g,c=Fn.b,f=Math.max(a,l,c),d=Math.min(a,l,c);let p,m;const g=(d+f)/2;if(d===f)p=0,m=0;else{const v=f-d;switch(m=g<=.5?v/(f+d):v/(2-f-d),f){case a:p=(l-c)/v+(l<c?6:0);break;case l:p=(c-a)/v+2;break;case c:p=(a-l)/v+4;break}p/=6}return t.h=p,t.s=m,t.l=g,t}getRGB(t,n=Oe.workingColorSpace){return Oe.fromWorkingColorSpace(Fn.copy(this),n),t.r=Fn.r,t.g=Fn.g,t.b=Fn.b,t}getStyle(t=vi){Oe.fromWorkingColorSpace(Fn.copy(this),t);const n=Fn.r,a=Fn.g,l=Fn.b;return t!==vi?`color(${t} ${n.toFixed(3)} ${a.toFixed(3)} ${l.toFixed(3)})`:`rgb(${Math.round(n*255)},${Math.round(a*255)},${Math.round(l*255)})`}offsetHSL(t,n,a){return this.getHSL(hs),this.setHSL(hs.h+t,hs.s+n,hs.l+a)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,n){return this.r=t.r+n.r,this.g=t.g+n.g,this.b=t.b+n.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,n){return this.r+=(t.r-this.r)*n,this.g+=(t.g-this.g)*n,this.b+=(t.b-this.b)*n,this}lerpColors(t,n,a){return this.r=t.r+(n.r-t.r)*a,this.g=t.g+(n.g-t.g)*a,this.b=t.b+(n.b-t.b)*a,this}lerpHSL(t,n){this.getHSL(hs),t.getHSL(Nu);const a=Wl(hs.h,Nu.h,n),l=Wl(hs.s,Nu.s,n),c=Wl(hs.l,Nu.l,n);return this.setHSL(a,l,c),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const n=this.r,a=this.g,l=this.b,c=t.elements;return this.r=c[0]*n+c[3]*a+c[6]*l,this.g=c[1]*n+c[4]*a+c[7]*l,this.b=c[2]*n+c[5]*a+c[8]*l,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,n=0){return this.r=t[n],this.g=t[n+1],this.b=t[n+2],this}toArray(t=[],n=0){return t[n]=this.r,t[n+1]=this.g,t[n+2]=this.b,t}fromBufferAttribute(t,n){return this.r=t.getX(n),this.g=t.getY(n),this.b=t.getZ(n),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Fn=new de;de.NAMES=Ux;let Zb=0;class cf extends Vo{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Zb++}),this.uuid=ko(),this.name="",this.type="Material",this.blending=vo,this.side=As,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Sp,this.blendDst=Mp,this.blendEquation=er,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new de(0,0,0),this.blendAlpha=0,this.depthFunc=Oo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=O_,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Jr,this.stencilZFail=Jr,this.stencilZPass=Jr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const n in t){const a=t[n];if(a===void 0){console.warn(`THREE.Material: parameter '${n}' has value of undefined.`);continue}const l=this[n];if(l===void 0){console.warn(`THREE.Material: '${n}' is not a property of THREE.${this.type}.`);continue}l&&l.isColor?l.set(a):l&&l.isVector3&&a&&a.isVector3?l.copy(a):this[n]=a}}toJSON(t){const n=t===void 0||typeof t=="string";n&&(t={textures:{},images:{}});const a={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};a.uuid=this.uuid,a.type=this.type,this.name!==""&&(a.name=this.name),this.color&&this.color.isColor&&(a.color=this.color.getHex()),this.roughness!==void 0&&(a.roughness=this.roughness),this.metalness!==void 0&&(a.metalness=this.metalness),this.sheen!==void 0&&(a.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(a.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(a.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(a.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(a.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(a.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(a.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(a.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(a.shininess=this.shininess),this.clearcoat!==void 0&&(a.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(a.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(a.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(a.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(a.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,a.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(a.dispersion=this.dispersion),this.iridescence!==void 0&&(a.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(a.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(a.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(a.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(a.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(a.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(a.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(a.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(a.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(a.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(a.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(a.lightMap=this.lightMap.toJSON(t).uuid,a.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(a.aoMap=this.aoMap.toJSON(t).uuid,a.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(a.bumpMap=this.bumpMap.toJSON(t).uuid,a.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(a.normalMap=this.normalMap.toJSON(t).uuid,a.normalMapType=this.normalMapType,a.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(a.displacementMap=this.displacementMap.toJSON(t).uuid,a.displacementScale=this.displacementScale,a.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(a.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(a.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(a.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(a.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(a.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(a.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(a.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(a.combine=this.combine)),this.envMapRotation!==void 0&&(a.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(a.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(a.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(a.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(a.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(a.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(a.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(a.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(a.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(a.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(a.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(a.size=this.size),this.shadowSide!==null&&(a.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(a.sizeAttenuation=this.sizeAttenuation),this.blending!==vo&&(a.blending=this.blending),this.side!==As&&(a.side=this.side),this.vertexColors===!0&&(a.vertexColors=!0),this.opacity<1&&(a.opacity=this.opacity),this.transparent===!0&&(a.transparent=!0),this.blendSrc!==Sp&&(a.blendSrc=this.blendSrc),this.blendDst!==Mp&&(a.blendDst=this.blendDst),this.blendEquation!==er&&(a.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(a.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(a.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(a.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(a.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(a.blendAlpha=this.blendAlpha),this.depthFunc!==Oo&&(a.depthFunc=this.depthFunc),this.depthTest===!1&&(a.depthTest=this.depthTest),this.depthWrite===!1&&(a.depthWrite=this.depthWrite),this.colorWrite===!1&&(a.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(a.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==O_&&(a.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(a.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(a.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Jr&&(a.stencilFail=this.stencilFail),this.stencilZFail!==Jr&&(a.stencilZFail=this.stencilZFail),this.stencilZPass!==Jr&&(a.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(a.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(a.rotation=this.rotation),this.polygonOffset===!0&&(a.polygonOffset=!0),this.polygonOffsetFactor!==0&&(a.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(a.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(a.linewidth=this.linewidth),this.dashSize!==void 0&&(a.dashSize=this.dashSize),this.gapSize!==void 0&&(a.gapSize=this.gapSize),this.scale!==void 0&&(a.scale=this.scale),this.dithering===!0&&(a.dithering=!0),this.alphaTest>0&&(a.alphaTest=this.alphaTest),this.alphaHash===!0&&(a.alphaHash=!0),this.alphaToCoverage===!0&&(a.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(a.premultipliedAlpha=!0),this.forceSinglePass===!0&&(a.forceSinglePass=!0),this.wireframe===!0&&(a.wireframe=!0),this.wireframeLinewidth>1&&(a.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(a.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(a.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(a.flatShading=!0),this.visible===!1&&(a.visible=!1),this.toneMapped===!1&&(a.toneMapped=!1),this.fog===!1&&(a.fog=!1),Object.keys(this.userData).length>0&&(a.userData=this.userData);function l(c){const f=[];for(const d in c){const p=c[d];delete p.metadata,f.push(p)}return f}if(n){const c=l(t.textures),f=l(t.images);c.length>0&&(a.textures=c),f.length>0&&(a.images=f)}return a}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const n=t.clippingPlanes;let a=null;if(n!==null){const l=n.length;a=new Array(l);for(let c=0;c!==l;++c)a[c]=n[c].clone()}return this.clippingPlanes=a,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class vr extends cf{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new de(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new za,this.combine=px,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const vn=new W,Lu=new Wt;class ta{constructor(t,n,a=!1){if(Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=t,this.itemSize=n,this.count=t!==void 0?t.length/n:0,this.normalized=a,this.usage=P_,this.updateRanges=[],this.gpuType=Da,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,n){this.updateRanges.push({start:t,count:n})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,n,a){t*=this.itemSize,a*=n.itemSize;for(let l=0,c=this.itemSize;l<c;l++)this.array[t+l]=n.array[a+l];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let n=0,a=this.count;n<a;n++)Lu.fromBufferAttribute(this,n),Lu.applyMatrix3(t),this.setXY(n,Lu.x,Lu.y);else if(this.itemSize===3)for(let n=0,a=this.count;n<a;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix3(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyMatrix4(t){for(let n=0,a=this.count;n<a;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix4(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyNormalMatrix(t){for(let n=0,a=this.count;n<a;n++)vn.fromBufferAttribute(this,n),vn.applyNormalMatrix(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}transformDirection(t){for(let n=0,a=this.count;n<a;n++)vn.fromBufferAttribute(this,n),vn.transformDirection(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}set(t,n=0){return this.array.set(t,n),this}getComponent(t,n){let a=this.array[t*this.itemSize+n];return this.normalized&&(a=ho(a,this.array)),a}setComponent(t,n,a){return this.normalized&&(a=Xn(a,this.array)),this.array[t*this.itemSize+n]=a,this}getX(t){let n=this.array[t*this.itemSize];return this.normalized&&(n=ho(n,this.array)),n}setX(t,n){return this.normalized&&(n=Xn(n,this.array)),this.array[t*this.itemSize]=n,this}getY(t){let n=this.array[t*this.itemSize+1];return this.normalized&&(n=ho(n,this.array)),n}setY(t,n){return this.normalized&&(n=Xn(n,this.array)),this.array[t*this.itemSize+1]=n,this}getZ(t){let n=this.array[t*this.itemSize+2];return this.normalized&&(n=ho(n,this.array)),n}setZ(t,n){return this.normalized&&(n=Xn(n,this.array)),this.array[t*this.itemSize+2]=n,this}getW(t){let n=this.array[t*this.itemSize+3];return this.normalized&&(n=ho(n,this.array)),n}setW(t,n){return this.normalized&&(n=Xn(n,this.array)),this.array[t*this.itemSize+3]=n,this}setXY(t,n,a){return t*=this.itemSize,this.normalized&&(n=Xn(n,this.array),a=Xn(a,this.array)),this.array[t+0]=n,this.array[t+1]=a,this}setXYZ(t,n,a,l){return t*=this.itemSize,this.normalized&&(n=Xn(n,this.array),a=Xn(a,this.array),l=Xn(l,this.array)),this.array[t+0]=n,this.array[t+1]=a,this.array[t+2]=l,this}setXYZW(t,n,a,l,c){return t*=this.itemSize,this.normalized&&(n=Xn(n,this.array),a=Xn(a,this.array),l=Xn(l,this.array),c=Xn(c,this.array)),this.array[t+0]=n,this.array[t+1]=a,this.array[t+2]=l,this.array[t+3]=c,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==P_&&(t.usage=this.usage),t}}class Nx extends ta{constructor(t,n,a){super(new Uint16Array(t),n,a)}}class Lx extends ta{constructor(t,n,a){super(new Uint32Array(t),n,a)}}class Cn extends ta{constructor(t,n,a){super(new Float32Array(t),n,a)}}let Kb=0;const Ci=new nn,Xd=new si,lo=new W,pi=new cc,Gl=new cc,Tn=new W;class Vi extends Vo{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Kb++}),this.uuid=ko(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(Cx(t)?Lx:Nx)(t,1):this.index=t,this}setIndirect(t){return this.indirect=t,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,n){return this.attributes[t]=n,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,n,a=0){this.groups.push({start:t,count:n,materialIndex:a})}clearGroups(){this.groups=[]}setDrawRange(t,n){this.drawRange.start=t,this.drawRange.count=n}applyMatrix4(t){const n=this.attributes.position;n!==void 0&&(n.applyMatrix4(t),n.needsUpdate=!0);const a=this.attributes.normal;if(a!==void 0){const c=new fe().getNormalMatrix(t);a.applyNormalMatrix(c),a.needsUpdate=!0}const l=this.attributes.tangent;return l!==void 0&&(l.transformDirection(t),l.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return Ci.makeRotationFromQuaternion(t),this.applyMatrix4(Ci),this}rotateX(t){return Ci.makeRotationX(t),this.applyMatrix4(Ci),this}rotateY(t){return Ci.makeRotationY(t),this.applyMatrix4(Ci),this}rotateZ(t){return Ci.makeRotationZ(t),this.applyMatrix4(Ci),this}translate(t,n,a){return Ci.makeTranslation(t,n,a),this.applyMatrix4(Ci),this}scale(t,n,a){return Ci.makeScale(t,n,a),this.applyMatrix4(Ci),this}lookAt(t){return Xd.lookAt(t),Xd.updateMatrix(),this.applyMatrix4(Xd.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(lo).negate(),this.translate(lo.x,lo.y,lo.z),this}setFromPoints(t){const n=this.getAttribute("position");if(n===void 0){const a=[];for(let l=0,c=t.length;l<c;l++){const f=t[l];a.push(f.x,f.y,f.z||0)}this.setAttribute("position",new Cn(a,3))}else{const a=Math.min(t.length,n.count);for(let l=0;l<a;l++){const c=t[l];n.setXYZ(l,c.x,c.y,c.z||0)}t.length>n.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),n.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new cc);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new W(-1/0,-1/0,-1/0),new W(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),n)for(let a=0,l=n.length;a<l;a++){const c=n[a];pi.setFromBufferAttribute(c),this.morphTargetsRelative?(Tn.addVectors(this.boundingBox.min,pi.min),this.boundingBox.expandByPoint(Tn),Tn.addVectors(this.boundingBox.max,pi.max),this.boundingBox.expandByPoint(Tn)):(this.boundingBox.expandByPoint(pi.min),this.boundingBox.expandByPoint(pi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Em);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new W,1/0);return}if(t){const a=this.boundingSphere.center;if(pi.setFromBufferAttribute(t),n)for(let c=0,f=n.length;c<f;c++){const d=n[c];Gl.setFromBufferAttribute(d),this.morphTargetsRelative?(Tn.addVectors(pi.min,Gl.min),pi.expandByPoint(Tn),Tn.addVectors(pi.max,Gl.max),pi.expandByPoint(Tn)):(pi.expandByPoint(Gl.min),pi.expandByPoint(Gl.max))}pi.getCenter(a);let l=0;for(let c=0,f=t.count;c<f;c++)Tn.fromBufferAttribute(t,c),l=Math.max(l,a.distanceToSquared(Tn));if(n)for(let c=0,f=n.length;c<f;c++){const d=n[c],p=this.morphTargetsRelative;for(let m=0,g=d.count;m<g;m++)Tn.fromBufferAttribute(d,m),p&&(lo.fromBufferAttribute(t,m),Tn.add(lo)),l=Math.max(l,a.distanceToSquared(Tn))}this.boundingSphere.radius=Math.sqrt(l),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,n=this.attributes;if(t===null||n.position===void 0||n.normal===void 0||n.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const a=n.position,l=n.normal,c=n.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ta(new Float32Array(4*a.count),4));const f=this.getAttribute("tangent"),d=[],p=[];for(let G=0;G<a.count;G++)d[G]=new W,p[G]=new W;const m=new W,g=new W,v=new W,y=new Wt,x=new Wt,E=new Wt,b=new W,M=new W;function _(G,U,w){m.fromBufferAttribute(a,G),g.fromBufferAttribute(a,U),v.fromBufferAttribute(a,w),y.fromBufferAttribute(c,G),x.fromBufferAttribute(c,U),E.fromBufferAttribute(c,w),g.sub(m),v.sub(m),x.sub(y),E.sub(y);const H=1/(x.x*E.y-E.x*x.y);isFinite(H)&&(b.copy(g).multiplyScalar(E.y).addScaledVector(v,-x.y).multiplyScalar(H),M.copy(v).multiplyScalar(x.x).addScaledVector(g,-E.x).multiplyScalar(H),d[G].add(b),d[U].add(b),d[w].add(b),p[G].add(M),p[U].add(M),p[w].add(M))}let I=this.groups;I.length===0&&(I=[{start:0,count:t.count}]);for(let G=0,U=I.length;G<U;++G){const w=I[G],H=w.start,ut=w.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)_(t.getX(ot+0),t.getX(ot+1),t.getX(ot+2))}const N=new W,C=new W,V=new W,F=new W;function P(G){V.fromBufferAttribute(l,G),F.copy(V);const U=d[G];N.copy(U),N.sub(V.multiplyScalar(V.dot(U))).normalize(),C.crossVectors(F,U);const H=C.dot(p[G])<0?-1:1;f.setXYZW(G,N.x,N.y,N.z,H)}for(let G=0,U=I.length;G<U;++G){const w=I[G],H=w.start,ut=w.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)P(t.getX(ot+0)),P(t.getX(ot+1)),P(t.getX(ot+2))}}computeVertexNormals(){const t=this.index,n=this.getAttribute("position");if(n!==void 0){let a=this.getAttribute("normal");if(a===void 0)a=new ta(new Float32Array(n.count*3),3),this.setAttribute("normal",a);else for(let y=0,x=a.count;y<x;y++)a.setXYZ(y,0,0,0);const l=new W,c=new W,f=new W,d=new W,p=new W,m=new W,g=new W,v=new W;if(t)for(let y=0,x=t.count;y<x;y+=3){const E=t.getX(y+0),b=t.getX(y+1),M=t.getX(y+2);l.fromBufferAttribute(n,E),c.fromBufferAttribute(n,b),f.fromBufferAttribute(n,M),g.subVectors(f,c),v.subVectors(l,c),g.cross(v),d.fromBufferAttribute(a,E),p.fromBufferAttribute(a,b),m.fromBufferAttribute(a,M),d.add(g),p.add(g),m.add(g),a.setXYZ(E,d.x,d.y,d.z),a.setXYZ(b,p.x,p.y,p.z),a.setXYZ(M,m.x,m.y,m.z)}else for(let y=0,x=n.count;y<x;y+=3)l.fromBufferAttribute(n,y+0),c.fromBufferAttribute(n,y+1),f.fromBufferAttribute(n,y+2),g.subVectors(f,c),v.subVectors(l,c),g.cross(v),a.setXYZ(y+0,g.x,g.y,g.z),a.setXYZ(y+1,g.x,g.y,g.z),a.setXYZ(y+2,g.x,g.y,g.z);this.normalizeNormals(),a.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let n=0,a=t.count;n<a;n++)Tn.fromBufferAttribute(t,n),Tn.normalize(),t.setXYZ(n,Tn.x,Tn.y,Tn.z)}toNonIndexed(){function t(d,p){const m=d.array,g=d.itemSize,v=d.normalized,y=new m.constructor(p.length*g);let x=0,E=0;for(let b=0,M=p.length;b<M;b++){d.isInterleavedBufferAttribute?x=p[b]*d.data.stride+d.offset:x=p[b]*g;for(let _=0;_<g;_++)y[E++]=m[x++]}return new ta(y,g,v)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const n=new Vi,a=this.index.array,l=this.attributes;for(const d in l){const p=l[d],m=t(p,a);n.setAttribute(d,m)}const c=this.morphAttributes;for(const d in c){const p=[],m=c[d];for(let g=0,v=m.length;g<v;g++){const y=m[g],x=t(y,a);p.push(x)}n.morphAttributes[d]=p}n.morphTargetsRelative=this.morphTargetsRelative;const f=this.groups;for(let d=0,p=f.length;d<p;d++){const m=f[d];n.addGroup(m.start,m.count,m.materialIndex)}return n}toJSON(){const t={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const p=this.parameters;for(const m in p)p[m]!==void 0&&(t[m]=p[m]);return t}t.data={attributes:{}};const n=this.index;n!==null&&(t.data.index={type:n.array.constructor.name,array:Array.prototype.slice.call(n.array)});const a=this.attributes;for(const p in a){const m=a[p];t.data.attributes[p]=m.toJSON(t.data)}const l={};let c=!1;for(const p in this.morphAttributes){const m=this.morphAttributes[p],g=[];for(let v=0,y=m.length;v<y;v++){const x=m[v];g.push(x.toJSON(t.data))}g.length>0&&(l[p]=g,c=!0)}c&&(t.data.morphAttributes=l,t.data.morphTargetsRelative=this.morphTargetsRelative);const f=this.groups;f.length>0&&(t.data.groups=JSON.parse(JSON.stringify(f)));const d=this.boundingSphere;return d!==null&&(t.data.boundingSphere={center:d.center.toArray(),radius:d.radius}),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const n={};this.name=t.name;const a=t.index;a!==null&&this.setIndex(a.clone(n));const l=t.attributes;for(const m in l){const g=l[m];this.setAttribute(m,g.clone(n))}const c=t.morphAttributes;for(const m in c){const g=[],v=c[m];for(let y=0,x=v.length;y<x;y++)g.push(v[y].clone(n));this.morphAttributes[m]=g}this.morphTargetsRelative=t.morphTargetsRelative;const f=t.groups;for(let m=0,g=f.length;m<g;m++){const v=f[m];this.addGroup(v.start,v.count,v.materialIndex)}const d=t.boundingBox;d!==null&&(this.boundingBox=d.clone());const p=t.boundingSphere;return p!==null&&(this.boundingSphere=p.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Z_=new nn,Qs=new kb,Ou=new Em,K_=new W,Pu=new W,zu=new W,Iu=new W,jd=new W,Bu=new W,J_=new W,Fu=new W;class Wn extends si{constructor(t=new Vi,n=new vr){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=n,this.updateMorphTargets()}copy(t,n){return super.copy(t,n),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const n=this.geometry.morphAttributes,a=Object.keys(n);if(a.length>0){const l=n[a[0]];if(l!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,f=l.length;c<f;c++){const d=l[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}getVertexPosition(t,n){const a=this.geometry,l=a.attributes.position,c=a.morphAttributes.position,f=a.morphTargetsRelative;n.fromBufferAttribute(l,t);const d=this.morphTargetInfluences;if(c&&d){Bu.set(0,0,0);for(let p=0,m=c.length;p<m;p++){const g=d[p],v=c[p];g!==0&&(jd.fromBufferAttribute(v,t),f?Bu.addScaledVector(jd,g):Bu.addScaledVector(jd.sub(n),g))}n.add(Bu)}return n}raycast(t,n){const a=this.geometry,l=this.material,c=this.matrixWorld;l!==void 0&&(a.boundingSphere===null&&a.computeBoundingSphere(),Ou.copy(a.boundingSphere),Ou.applyMatrix4(c),Qs.copy(t.ray).recast(t.near),!(Ou.containsPoint(Qs.origin)===!1&&(Qs.intersectSphere(Ou,K_)===null||Qs.origin.distanceToSquared(K_)>(t.far-t.near)**2))&&(Z_.copy(c).invert(),Qs.copy(t.ray).applyMatrix4(Z_),!(a.boundingBox!==null&&Qs.intersectsBox(a.boundingBox)===!1)&&this._computeIntersections(t,n,Qs)))}_computeIntersections(t,n,a){let l;const c=this.geometry,f=this.material,d=c.index,p=c.attributes.position,m=c.attributes.uv,g=c.attributes.uv1,v=c.attributes.normal,y=c.groups,x=c.drawRange;if(d!==null)if(Array.isArray(f))for(let E=0,b=y.length;E<b;E++){const M=y[E],_=f[M.materialIndex],I=Math.max(M.start,x.start),N=Math.min(d.count,Math.min(M.start+M.count,x.start+x.count));for(let C=I,V=N;C<V;C+=3){const F=d.getX(C),P=d.getX(C+1),G=d.getX(C+2);l=Hu(this,_,t,a,m,g,v,F,P,G),l&&(l.faceIndex=Math.floor(C/3),l.face.materialIndex=M.materialIndex,n.push(l))}}else{const E=Math.max(0,x.start),b=Math.min(d.count,x.start+x.count);for(let M=E,_=b;M<_;M+=3){const I=d.getX(M),N=d.getX(M+1),C=d.getX(M+2);l=Hu(this,f,t,a,m,g,v,I,N,C),l&&(l.faceIndex=Math.floor(M/3),n.push(l))}}else if(p!==void 0)if(Array.isArray(f))for(let E=0,b=y.length;E<b;E++){const M=y[E],_=f[M.materialIndex],I=Math.max(M.start,x.start),N=Math.min(p.count,Math.min(M.start+M.count,x.start+x.count));for(let C=I,V=N;C<V;C+=3){const F=C,P=C+1,G=C+2;l=Hu(this,_,t,a,m,g,v,F,P,G),l&&(l.faceIndex=Math.floor(C/3),l.face.materialIndex=M.materialIndex,n.push(l))}}else{const E=Math.max(0,x.start),b=Math.min(p.count,x.start+x.count);for(let M=E,_=b;M<_;M+=3){const I=M,N=M+1,C=M+2;l=Hu(this,f,t,a,m,g,v,I,N,C),l&&(l.faceIndex=Math.floor(M/3),n.push(l))}}}}function Jb(s,t,n,a,l,c,f,d){let p;if(t.side===ii?p=a.intersectTriangle(f,c,l,!0,d):p=a.intersectTriangle(l,c,f,t.side===As,d),p===null)return null;Fu.copy(d),Fu.applyMatrix4(s.matrixWorld);const m=n.ray.origin.distanceTo(Fu);return m<n.near||m>n.far?null:{distance:m,point:Fu.clone(),object:s}}function Hu(s,t,n,a,l,c,f,d,p,m){s.getVertexPosition(d,Pu),s.getVertexPosition(p,zu),s.getVertexPosition(m,Iu);const g=Jb(s,t,n,a,Pu,zu,Iu,J_);if(g){const v=new W;Bi.getBarycoord(J_,Pu,zu,Iu,v),l&&(g.uv=Bi.getInterpolatedAttribute(l,d,p,m,v,new Wt)),c&&(g.uv1=Bi.getInterpolatedAttribute(c,d,p,m,v,new Wt)),f&&(g.normal=Bi.getInterpolatedAttribute(f,d,p,m,v,new W),g.normal.dot(a.direction)>0&&g.normal.multiplyScalar(-1));const y={a:d,b:p,c:m,normal:new W,materialIndex:0};Bi.getNormal(Pu,zu,Iu,y.normal),g.face=y,g.barycoord=v}return g}class uc extends Vi{constructor(t=1,n=1,a=1,l=1,c=1,f=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:n,depth:a,widthSegments:l,heightSegments:c,depthSegments:f};const d=this;l=Math.floor(l),c=Math.floor(c),f=Math.floor(f);const p=[],m=[],g=[],v=[];let y=0,x=0;E("z","y","x",-1,-1,a,n,t,f,c,0),E("z","y","x",1,-1,a,n,-t,f,c,1),E("x","z","y",1,1,t,a,n,l,f,2),E("x","z","y",1,-1,t,a,-n,l,f,3),E("x","y","z",1,-1,t,n,a,l,c,4),E("x","y","z",-1,-1,t,n,-a,l,c,5),this.setIndex(p),this.setAttribute("position",new Cn(m,3)),this.setAttribute("normal",new Cn(g,3)),this.setAttribute("uv",new Cn(v,2));function E(b,M,_,I,N,C,V,F,P,G,U){const w=C/P,H=V/G,ut=C/2,ot=V/2,mt=F/2,ct=P+1,z=G+1;let Z=0,$=0;const Et=new W;for(let At=0;At<z;At++){const O=At*H-ot;for(let nt=0;nt<ct;nt++){const St=nt*w-ut;Et[b]=St*I,Et[M]=O*N,Et[_]=mt,m.push(Et.x,Et.y,Et.z),Et[b]=0,Et[M]=0,Et[_]=F>0?1:-1,g.push(Et.x,Et.y,Et.z),v.push(nt/P),v.push(1-At/G),Z+=1}}for(let At=0;At<G;At++)for(let O=0;O<P;O++){const nt=y+O+ct*At,St=y+O+ct*(At+1),q=y+(O+1)+ct*(At+1),ft=y+(O+1)+ct*At;p.push(nt,St,ft),p.push(St,q,ft),$+=6}d.addGroup(x,$,U),x+=$,y+=Z}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new uc(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}function Ho(s){const t={};for(const n in s){t[n]={};for(const a in s[n]){const l=s[n][a];l&&(l.isColor||l.isMatrix3||l.isMatrix4||l.isVector2||l.isVector3||l.isVector4||l.isTexture||l.isQuaternion)?l.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[n][a]=null):t[n][a]=l.clone():Array.isArray(l)?t[n][a]=l.slice():t[n][a]=l}}return t}function jn(s){const t={};for(let n=0;n<s.length;n++){const a=Ho(s[n]);for(const l in a)t[l]=a[l]}return t}function $b(s){const t=[];for(let n=0;n<s.length;n++)t.push(s[n].clone());return t}function Ox(s){const t=s.getRenderTarget();return t===null?s.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Oe.workingColorSpace}const sf={clone:Ho,merge:jn};var tT=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,eT=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Yn extends cf{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=tT,this.fragmentShader=eT,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Ho(t.uniforms),this.uniformsGroups=$b(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this}toJSON(t){const n=super.toJSON(t);n.glslVersion=this.glslVersion,n.uniforms={};for(const l in this.uniforms){const f=this.uniforms[l].value;f&&f.isTexture?n.uniforms[l]={type:"t",value:f.toJSON(t).uuid}:f&&f.isColor?n.uniforms[l]={type:"c",value:f.getHex()}:f&&f.isVector2?n.uniforms[l]={type:"v2",value:f.toArray()}:f&&f.isVector3?n.uniforms[l]={type:"v3",value:f.toArray()}:f&&f.isVector4?n.uniforms[l]={type:"v4",value:f.toArray()}:f&&f.isMatrix3?n.uniforms[l]={type:"m3",value:f.toArray()}:f&&f.isMatrix4?n.uniforms[l]={type:"m4",value:f.toArray()}:n.uniforms[l]={value:f}}Object.keys(this.defines).length>0&&(n.defines=this.defines),n.vertexShader=this.vertexShader,n.fragmentShader=this.fragmentShader,n.lights=this.lights,n.clipping=this.clipping;const a={};for(const l in this.extensions)this.extensions[l]===!0&&(a[l]=!0);return Object.keys(a).length>0&&(n.extensions=a),n}}class Px extends si{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new nn,this.projectionMatrix=new nn,this.projectionMatrixInverse=new nn,this.coordinateSystem=Ua}copy(t,n){return super.copy(t,n),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(t,n){super.updateWorldMatrix(t,n),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ds=new W,$_=new Wt,ty=new Wt;class _i extends Px{constructor(t=50,n=1,a=.1,l=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=a,this.far=l,this.focus=10,this.aspect=n,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const n=.5*this.getFilmHeight()/t;this.fov=ec*2*Math.atan(n),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(ql*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return ec*2*Math.atan(Math.tan(ql*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,n,a){ds.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ds.x,ds.y).multiplyScalar(-t/ds.z),ds.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),a.set(ds.x,ds.y).multiplyScalar(-t/ds.z)}getViewSize(t,n){return this.getViewBounds(t,$_,ty),n.subVectors(ty,$_)}setViewOffset(t,n,a,l,c,f){this.aspect=t/n,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=a,this.view.offsetY=l,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let n=t*Math.tan(ql*.5*this.fov)/this.zoom,a=2*n,l=this.aspect*a,c=-.5*l;const f=this.view;if(this.view!==null&&this.view.enabled){const p=f.fullWidth,m=f.fullHeight;c+=f.offsetX*l/p,n-=f.offsetY*a/m,l*=f.width/p,a*=f.height/m}const d=this.filmOffset;d!==0&&(c+=t*d/this.getFilmWidth()),this.projectionMatrix.makePerspective(c,c+l,n,n-a,t,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.fov=this.fov,n.object.zoom=this.zoom,n.object.near=this.near,n.object.far=this.far,n.object.focus=this.focus,n.object.aspect=this.aspect,this.view!==null&&(n.object.view=Object.assign({},this.view)),n.object.filmGauge=this.filmGauge,n.object.filmOffset=this.filmOffset,n}}const co=-90,uo=1;class nT extends si{constructor(t,n,a){super(),this.type="CubeCamera",this.renderTarget=a,this.coordinateSystem=null,this.activeMipmapLevel=0;const l=new _i(co,uo,t,n);l.layers=this.layers,this.add(l);const c=new _i(co,uo,t,n);c.layers=this.layers,this.add(c);const f=new _i(co,uo,t,n);f.layers=this.layers,this.add(f);const d=new _i(co,uo,t,n);d.layers=this.layers,this.add(d);const p=new _i(co,uo,t,n);p.layers=this.layers,this.add(p);const m=new _i(co,uo,t,n);m.layers=this.layers,this.add(m)}updateCoordinateSystem(){const t=this.coordinateSystem,n=this.children.concat(),[a,l,c,f,d,p]=n;for(const m of n)this.remove(m);if(t===Ua)a.up.set(0,1,0),a.lookAt(1,0,0),l.up.set(0,1,0),l.lookAt(-1,0,0),c.up.set(0,0,-1),c.lookAt(0,1,0),f.up.set(0,0,1),f.lookAt(0,-1,0),d.up.set(0,1,0),d.lookAt(0,0,1),p.up.set(0,1,0),p.lookAt(0,0,-1);else if(t===nf)a.up.set(0,-1,0),a.lookAt(-1,0,0),l.up.set(0,-1,0),l.lookAt(1,0,0),c.up.set(0,0,1),c.lookAt(0,1,0),f.up.set(0,0,-1),f.lookAt(0,-1,0),d.up.set(0,-1,0),d.lookAt(0,0,1),p.up.set(0,-1,0),p.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const m of n)this.add(m),m.updateMatrixWorld()}update(t,n){this.parent===null&&this.updateMatrixWorld();const{renderTarget:a,activeMipmapLevel:l}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[c,f,d,p,m,g]=this.children,v=t.getRenderTarget(),y=t.getActiveCubeFace(),x=t.getActiveMipmapLevel(),E=t.xr.enabled;t.xr.enabled=!1;const b=a.texture.generateMipmaps;a.texture.generateMipmaps=!1,t.setRenderTarget(a,0,l),t.render(n,c),t.setRenderTarget(a,1,l),t.render(n,f),t.setRenderTarget(a,2,l),t.render(n,d),t.setRenderTarget(a,3,l),t.render(n,p),t.setRenderTarget(a,4,l),t.render(n,m),a.texture.generateMipmaps=b,t.setRenderTarget(a,5,l),t.render(n,g),t.setRenderTarget(v,y,x),t.xr.enabled=E,a.texture.needsPMREMUpdate=!0}}class zx extends ai{constructor(t,n,a,l,c,f,d,p,m,g){t=t!==void 0?t:[],n=n!==void 0?n:Po,super(t,n,a,l,c,f,d,p,m,g),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class iT extends Gi{constructor(t=1,n={}){super(t,t,n),this.isWebGLCubeRenderTarget=!0;const a={width:t,height:t,depth:1},l=[a,a,a,a,a,a];this.texture=new zx(l,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=n.generateMipmaps!==void 0?n.generateMipmaps:!1,this.texture.minFilter=n.minFilter!==void 0?n.minFilter:$i}fromEquirectangularTexture(t,n){this.texture.type=n.type,this.texture.colorSpace=n.colorSpace,this.texture.generateMipmaps=n.generateMipmaps,this.texture.minFilter=n.minFilter,this.texture.magFilter=n.magFilter;const a={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},l=new uc(5,5,5),c=new Yn({name:"CubemapFromEquirect",uniforms:Ho(a.uniforms),vertexShader:a.vertexShader,fragmentShader:a.fragmentShader,side:ii,blending:Na});c.uniforms.tEquirect.value=n;const f=new Wn(l,c),d=n.minFilter;return n.minFilter===rr&&(n.minFilter=$i),new nT(1,10,this).update(t,f),n.minFilter=d,f.geometry.dispose(),f.material.dispose(),this}clear(t,n,a,l){const c=t.getRenderTarget();for(let f=0;f<6;f++)t.setRenderTarget(this,f),t.clear(n,a,l);t.setRenderTarget(c)}}class aT extends si{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new za,this.environmentIntensity=1,this.environmentRotation=new za,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,n){return super.copy(t,n),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const n=super.toJSON(t);return this.fog!==null&&(n.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(n.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(n.object.backgroundIntensity=this.backgroundIntensity),n.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(n.object.environmentIntensity=this.environmentIntensity),n.object.environmentRotation=this.environmentRotation.toArray(),n}}const qd=new W,sT=new W,rT=new fe;class $s{constructor(t=new W(1,0,0),n=0){this.isPlane=!0,this.normal=t,this.constant=n}set(t,n){return this.normal.copy(t),this.constant=n,this}setComponents(t,n,a,l){return this.normal.set(t,n,a),this.constant=l,this}setFromNormalAndCoplanarPoint(t,n){return this.normal.copy(t),this.constant=-n.dot(this.normal),this}setFromCoplanarPoints(t,n,a){const l=qd.subVectors(a,n).cross(sT.subVectors(t,n)).normalize();return this.setFromNormalAndCoplanarPoint(l,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,n){return n.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,n){const a=t.delta(qd),l=this.normal.dot(a);if(l===0)return this.distanceToPoint(t.start)===0?n.copy(t.start):null;const c=-(t.start.dot(this.normal)+this.constant)/l;return c<0||c>1?null:n.copy(t.start).addScaledVector(a,c)}intersectsLine(t){const n=this.distanceToPoint(t.start),a=this.distanceToPoint(t.end);return n<0&&a>0||a<0&&n>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,n){const a=n||rT.getNormalMatrix(t),l=this.coplanarPoint(qd).applyMatrix4(t),c=this.normal.applyMatrix3(a).normalize();return this.constant=-l.dot(c),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Zs=new Em,Gu=new W;class bm{constructor(t=new $s,n=new $s,a=new $s,l=new $s,c=new $s,f=new $s){this.planes=[t,n,a,l,c,f]}set(t,n,a,l,c,f){const d=this.planes;return d[0].copy(t),d[1].copy(n),d[2].copy(a),d[3].copy(l),d[4].copy(c),d[5].copy(f),this}copy(t){const n=this.planes;for(let a=0;a<6;a++)n[a].copy(t.planes[a]);return this}setFromProjectionMatrix(t,n=Ua){const a=this.planes,l=t.elements,c=l[0],f=l[1],d=l[2],p=l[3],m=l[4],g=l[5],v=l[6],y=l[7],x=l[8],E=l[9],b=l[10],M=l[11],_=l[12],I=l[13],N=l[14],C=l[15];if(a[0].setComponents(p-c,y-m,M-x,C-_).normalize(),a[1].setComponents(p+c,y+m,M+x,C+_).normalize(),a[2].setComponents(p+f,y+g,M+E,C+I).normalize(),a[3].setComponents(p-f,y-g,M-E,C-I).normalize(),a[4].setComponents(p-d,y-v,M-b,C-N).normalize(),n===Ua)a[5].setComponents(p+d,y+v,M+b,C+N).normalize();else if(n===nf)a[5].setComponents(d,v,b,N).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+n);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),Zs.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const n=t.geometry;n.boundingSphere===null&&n.computeBoundingSphere(),Zs.copy(n.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(Zs)}intersectsSprite(t){return Zs.center.set(0,0,0),Zs.radius=.7071067811865476,Zs.applyMatrix4(t.matrixWorld),this.intersectsSphere(Zs)}intersectsSphere(t){const n=this.planes,a=t.center,l=-t.radius;for(let c=0;c<6;c++)if(n[c].distanceToPoint(a)<l)return!1;return!0}intersectsBox(t){const n=this.planes;for(let a=0;a<6;a++){const l=n[a];if(Gu.x=l.normal.x>0?t.max.x:t.min.x,Gu.y=l.normal.y>0?t.max.y:t.min.y,Gu.z=l.normal.z>0?t.max.z:t.min.z,l.distanceToPoint(Gu)<0)return!1}return!0}containsPoint(t){const n=this.planes;for(let a=0;a<6;a++)if(n[a].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class mo extends si{constructor(){super(),this.isGroup=!0,this.type="Group"}}class Ix extends ai{constructor(t,n,a,l,c,f,d,p,m,g=_o){if(g!==_o&&g!==Bo)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");a===void 0&&g===_o&&(a=gr),a===void 0&&g===Bo&&(a=Io),super(null,l,c,f,d,p,g,a,m),this.isDepthTexture=!0,this.image={width:t,height:n},this.magFilter=d!==void 0?d:Hi,this.minFilter=p!==void 0?p:Hi,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.compareFunction=t.compareFunction,this}toJSON(t){const n=super.toJSON(t);return this.compareFunction!==null&&(n.compareFunction=this.compareFunction),n}}class Ia{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(t,n){const a=this.getUtoTmapping(t);return this.getPoint(a,n)}getPoints(t=5){const n=[];for(let a=0;a<=t;a++)n.push(this.getPoint(a/t));return n}getSpacedPoints(t=5){const n=[];for(let a=0;a<=t;a++)n.push(this.getPointAt(a/t));return n}getLength(){const t=this.getLengths();return t[t.length-1]}getLengths(t=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===t+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const n=[];let a,l=this.getPoint(0),c=0;n.push(0);for(let f=1;f<=t;f++)a=this.getPoint(f/t),c+=a.distanceTo(l),n.push(c),l=a;return this.cacheArcLengths=n,n}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(t,n){const a=this.getLengths();let l=0;const c=a.length;let f;n?f=n:f=t*a[c-1];let d=0,p=c-1,m;for(;d<=p;)if(l=Math.floor(d+(p-d)/2),m=a[l]-f,m<0)d=l+1;else if(m>0)p=l-1;else{p=l;break}if(l=p,a[l]===f)return l/(c-1);const g=a[l],y=a[l+1]-g,x=(f-g)/y;return(l+x)/(c-1)}getTangent(t,n){let l=t-1e-4,c=t+1e-4;l<0&&(l=0),c>1&&(c=1);const f=this.getPoint(l),d=this.getPoint(c),p=n||(f.isVector2?new Wt:new W);return p.copy(d).sub(f).normalize(),p}getTangentAt(t,n){const a=this.getUtoTmapping(t);return this.getTangent(a,n)}computeFrenetFrames(t,n){const a=new W,l=[],c=[],f=[],d=new W,p=new nn;for(let x=0;x<=t;x++){const E=x/t;l[x]=this.getTangentAt(E,new W)}c[0]=new W,f[0]=new W;let m=Number.MAX_VALUE;const g=Math.abs(l[0].x),v=Math.abs(l[0].y),y=Math.abs(l[0].z);g<=m&&(m=g,a.set(1,0,0)),v<=m&&(m=v,a.set(0,1,0)),y<=m&&a.set(0,0,1),d.crossVectors(l[0],a).normalize(),c[0].crossVectors(l[0],d),f[0].crossVectors(l[0],c[0]);for(let x=1;x<=t;x++){if(c[x]=c[x-1].clone(),f[x]=f[x-1].clone(),d.crossVectors(l[x-1],l[x]),d.length()>Number.EPSILON){d.normalize();const E=Math.acos(ge(l[x-1].dot(l[x]),-1,1));c[x].applyMatrix4(p.makeRotationAxis(d,E))}f[x].crossVectors(l[x],c[x])}if(n===!0){let x=Math.acos(ge(c[0].dot(c[t]),-1,1));x/=t,l[0].dot(d.crossVectors(c[0],c[t]))>0&&(x=-x);for(let E=1;E<=t;E++)c[E].applyMatrix4(p.makeRotationAxis(l[E],x*E)),f[E].crossVectors(l[E],c[E])}return{tangents:l,normals:c,binormals:f}}clone(){return new this.constructor().copy(this)}copy(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}toJSON(){const t={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return t.arcLengthDivisions=this.arcLengthDivisions,t.type=this.type,t}fromJSON(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}}class Bx extends Ia{constructor(t=0,n=0,a=1,l=1,c=0,f=Math.PI*2,d=!1,p=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=t,this.aY=n,this.xRadius=a,this.yRadius=l,this.aStartAngle=c,this.aEndAngle=f,this.aClockwise=d,this.aRotation=p}getPoint(t,n=new Wt){const a=n,l=Math.PI*2;let c=this.aEndAngle-this.aStartAngle;const f=Math.abs(c)<Number.EPSILON;for(;c<0;)c+=l;for(;c>l;)c-=l;c<Number.EPSILON&&(f?c=0:c=l),this.aClockwise===!0&&!f&&(c===l?c=-l:c=c-l);const d=this.aStartAngle+t*c;let p=this.aX+this.xRadius*Math.cos(d),m=this.aY+this.yRadius*Math.sin(d);if(this.aRotation!==0){const g=Math.cos(this.aRotation),v=Math.sin(this.aRotation),y=p-this.aX,x=m-this.aY;p=y*g-x*v+this.aX,m=y*v+x*g+this.aY}return a.set(p,m)}copy(t){return super.copy(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}toJSON(){const t=super.toJSON();return t.aX=this.aX,t.aY=this.aY,t.xRadius=this.xRadius,t.yRadius=this.yRadius,t.aStartAngle=this.aStartAngle,t.aEndAngle=this.aEndAngle,t.aClockwise=this.aClockwise,t.aRotation=this.aRotation,t}fromJSON(t){return super.fromJSON(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}}class oT extends Bx{constructor(t,n,a,l,c,f){super(t,n,a,a,l,c,f),this.isArcCurve=!0,this.type="ArcCurve"}}function Tm(){let s=0,t=0,n=0,a=0;function l(c,f,d,p){s=c,t=d,n=-3*c+3*f-2*d-p,a=2*c-2*f+d+p}return{initCatmullRom:function(c,f,d,p,m){l(f,d,m*(d-c),m*(p-f))},initNonuniformCatmullRom:function(c,f,d,p,m,g,v){let y=(f-c)/m-(d-c)/(m+g)+(d-f)/g,x=(d-f)/g-(p-f)/(g+v)+(p-d)/v;y*=g,x*=g,l(f,d,y,x)},calc:function(c){const f=c*c,d=f*c;return s+t*c+n*f+a*d}}}const Vu=new W,Wd=new Tm,Yd=new Tm,Qd=new Tm;class Fx extends Ia{constructor(t=[],n=!1,a="centripetal",l=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=t,this.closed=n,this.curveType=a,this.tension=l}getPoint(t,n=new W){const a=n,l=this.points,c=l.length,f=(c-(this.closed?0:1))*t;let d=Math.floor(f),p=f-d;this.closed?d+=d>0?0:(Math.floor(Math.abs(d)/c)+1)*c:p===0&&d===c-1&&(d=c-2,p=1);let m,g;this.closed||d>0?m=l[(d-1)%c]:(Vu.subVectors(l[0],l[1]).add(l[0]),m=Vu);const v=l[d%c],y=l[(d+1)%c];if(this.closed||d+2<c?g=l[(d+2)%c]:(Vu.subVectors(l[c-1],l[c-2]).add(l[c-1]),g=Vu),this.curveType==="centripetal"||this.curveType==="chordal"){const x=this.curveType==="chordal"?.5:.25;let E=Math.pow(m.distanceToSquared(v),x),b=Math.pow(v.distanceToSquared(y),x),M=Math.pow(y.distanceToSquared(g),x);b<1e-4&&(b=1),E<1e-4&&(E=b),M<1e-4&&(M=b),Wd.initNonuniformCatmullRom(m.x,v.x,y.x,g.x,E,b,M),Yd.initNonuniformCatmullRom(m.y,v.y,y.y,g.y,E,b,M),Qd.initNonuniformCatmullRom(m.z,v.z,y.z,g.z,E,b,M)}else this.curveType==="catmullrom"&&(Wd.initCatmullRom(m.x,v.x,y.x,g.x,this.tension),Yd.initCatmullRom(m.y,v.y,y.y,g.y,this.tension),Qd.initCatmullRom(m.z,v.z,y.z,g.z,this.tension));return a.set(Wd.calc(p),Yd.calc(p),Qd.calc(p)),a}copy(t){super.copy(t),this.points=[];for(let n=0,a=t.points.length;n<a;n++){const l=t.points[n];this.points.push(l.clone())}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,a=this.points.length;n<a;n++){const l=this.points[n];t.points.push(l.toArray())}return t.closed=this.closed,t.curveType=this.curveType,t.tension=this.tension,t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,a=t.points.length;n<a;n++){const l=t.points[n];this.points.push(new W().fromArray(l))}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}}function ey(s,t,n,a,l){const c=(a-t)*.5,f=(l-n)*.5,d=s*s,p=s*d;return(2*n-2*a+c+f)*p+(-3*n+3*a-2*c-f)*d+c*s+n}function lT(s,t){const n=1-s;return n*n*t}function cT(s,t){return 2*(1-s)*s*t}function uT(s,t){return s*s*t}function Yl(s,t,n,a){return lT(s,t)+cT(s,n)+uT(s,a)}function fT(s,t){const n=1-s;return n*n*n*t}function hT(s,t){const n=1-s;return 3*n*n*s*t}function dT(s,t){return 3*(1-s)*s*s*t}function pT(s,t){return s*s*s*t}function Ql(s,t,n,a,l){return fT(s,t)+hT(s,n)+dT(s,a)+pT(s,l)}class mT extends Ia{constructor(t=new Wt,n=new Wt,a=new Wt,l=new Wt){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=t,this.v1=n,this.v2=a,this.v3=l}getPoint(t,n=new Wt){const a=n,l=this.v0,c=this.v1,f=this.v2,d=this.v3;return a.set(Ql(t,l.x,c.x,f.x,d.x),Ql(t,l.y,c.y,f.y,d.y)),a}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class gT extends Ia{constructor(t=new W,n=new W,a=new W,l=new W){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=t,this.v1=n,this.v2=a,this.v3=l}getPoint(t,n=new W){const a=n,l=this.v0,c=this.v1,f=this.v2,d=this.v3;return a.set(Ql(t,l.x,c.x,f.x,d.x),Ql(t,l.y,c.y,f.y,d.y),Ql(t,l.z,c.z,f.z,d.z)),a}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class vT extends Ia{constructor(t=new Wt,n=new Wt){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=t,this.v2=n}getPoint(t,n=new Wt){const a=n;return t===1?a.copy(this.v2):(a.copy(this.v2).sub(this.v1),a.multiplyScalar(t).add(this.v1)),a}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new Wt){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class _T extends Ia{constructor(t=new W,n=new W){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=t,this.v2=n}getPoint(t,n=new W){const a=n;return t===1?a.copy(this.v2):(a.copy(this.v2).sub(this.v1),a.multiplyScalar(t).add(this.v1)),a}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new W){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class yT extends Ia{constructor(t=new Wt,n=new Wt,a=new Wt){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=t,this.v1=n,this.v2=a}getPoint(t,n=new Wt){const a=n,l=this.v0,c=this.v1,f=this.v2;return a.set(Yl(t,l.x,c.x,f.x),Yl(t,l.y,c.y,f.y)),a}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class Hx extends Ia{constructor(t=new W,n=new W,a=new W){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=t,this.v1=n,this.v2=a}getPoint(t,n=new W){const a=n,l=this.v0,c=this.v1,f=this.v2;return a.set(Yl(t,l.x,c.x,f.x),Yl(t,l.y,c.y,f.y),Yl(t,l.z,c.z,f.z)),a}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class xT extends Ia{constructor(t=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=t}getPoint(t,n=new Wt){const a=n,l=this.points,c=(l.length-1)*t,f=Math.floor(c),d=c-f,p=l[f===0?f:f-1],m=l[f],g=l[f>l.length-2?l.length-1:f+1],v=l[f>l.length-3?l.length-1:f+2];return a.set(ey(d,p.x,m.x,g.x,v.x),ey(d,p.y,m.y,g.y,v.y)),a}copy(t){super.copy(t),this.points=[];for(let n=0,a=t.points.length;n<a;n++){const l=t.points[n];this.points.push(l.clone())}return this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,a=this.points.length;n<a;n++){const l=this.points[n];t.points.push(l.toArray())}return t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,a=t.points.length;n<a;n++){const l=t.points[n];this.points.push(new Wt().fromArray(l))}return this}}var ST=Object.freeze({__proto__:null,ArcCurve:oT,CatmullRomCurve3:Fx,CubicBezierCurve:mT,CubicBezierCurve3:gT,EllipseCurve:Bx,LineCurve:vT,LineCurve3:_T,QuadraticBezierCurve:yT,QuadraticBezierCurve3:Hx,SplineCurve:xT});class uf extends Vi{constructor(t=1,n=1,a=1,l=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:n,widthSegments:a,heightSegments:l};const c=t/2,f=n/2,d=Math.floor(a),p=Math.floor(l),m=d+1,g=p+1,v=t/d,y=n/p,x=[],E=[],b=[],M=[];for(let _=0;_<g;_++){const I=_*y-f;for(let N=0;N<m;N++){const C=N*v-c;E.push(C,-I,0),b.push(0,0,1),M.push(N/d),M.push(1-_/p)}}for(let _=0;_<p;_++)for(let I=0;I<d;I++){const N=I+m*_,C=I+m*(_+1),V=I+1+m*(_+1),F=I+1+m*_;x.push(N,C,F),x.push(C,V,F)}this.setIndex(x),this.setAttribute("position",new Cn(E,3)),this.setAttribute("normal",new Cn(b,3)),this.setAttribute("uv",new Cn(M,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new uf(t.width,t.height,t.widthSegments,t.heightSegments)}}class ff extends Vi{constructor(t=1,n=32,a=16,l=0,c=Math.PI*2,f=0,d=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:t,widthSegments:n,heightSegments:a,phiStart:l,phiLength:c,thetaStart:f,thetaLength:d},n=Math.max(3,Math.floor(n)),a=Math.max(2,Math.floor(a));const p=Math.min(f+d,Math.PI);let m=0;const g=[],v=new W,y=new W,x=[],E=[],b=[],M=[];for(let _=0;_<=a;_++){const I=[],N=_/a;let C=0;_===0&&f===0?C=.5/n:_===a&&p===Math.PI&&(C=-.5/n);for(let V=0;V<=n;V++){const F=V/n;v.x=-t*Math.cos(l+F*c)*Math.sin(f+N*d),v.y=t*Math.cos(f+N*d),v.z=t*Math.sin(l+F*c)*Math.sin(f+N*d),E.push(v.x,v.y,v.z),y.copy(v).normalize(),b.push(y.x,y.y,y.z),M.push(F+C,1-N),I.push(m++)}g.push(I)}for(let _=0;_<a;_++)for(let I=0;I<n;I++){const N=g[_][I+1],C=g[_][I],V=g[_+1][I],F=g[_+1][I+1];(_!==0||f>0)&&x.push(N,C,F),(_!==a-1||p<Math.PI)&&x.push(C,V,F)}this.setIndex(x),this.setAttribute("position",new Cn(E,3)),this.setAttribute("normal",new Cn(b,3)),this.setAttribute("uv",new Cn(M,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new ff(t.radius,t.widthSegments,t.heightSegments,t.phiStart,t.phiLength,t.thetaStart,t.thetaLength)}}class rf extends Vi{constructor(t=1,n=.4,a=12,l=48,c=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:t,tube:n,radialSegments:a,tubularSegments:l,arc:c},a=Math.floor(a),l=Math.floor(l);const f=[],d=[],p=[],m=[],g=new W,v=new W,y=new W;for(let x=0;x<=a;x++)for(let E=0;E<=l;E++){const b=E/l*c,M=x/a*Math.PI*2;v.x=(t+n*Math.cos(M))*Math.cos(b),v.y=(t+n*Math.cos(M))*Math.sin(b),v.z=n*Math.sin(M),d.push(v.x,v.y,v.z),g.x=t*Math.cos(b),g.y=t*Math.sin(b),y.subVectors(v,g).normalize(),p.push(y.x,y.y,y.z),m.push(E/l),m.push(x/a)}for(let x=1;x<=a;x++)for(let E=1;E<=l;E++){const b=(l+1)*x+E-1,M=(l+1)*(x-1)+E-1,_=(l+1)*(x-1)+E,I=(l+1)*x+E;f.push(b,M,I),f.push(M,_,I)}this.setIndex(f),this.setAttribute("position",new Cn(d,3)),this.setAttribute("normal",new Cn(p,3)),this.setAttribute("uv",new Cn(m,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new rf(t.radius,t.tube,t.radialSegments,t.tubularSegments,t.arc)}}class Am extends Vi{constructor(t=new Hx(new W(-1,-1,0),new W(-1,1,0),new W(1,1,0)),n=64,a=1,l=8,c=!1){super(),this.type="TubeGeometry",this.parameters={path:t,tubularSegments:n,radius:a,radialSegments:l,closed:c};const f=t.computeFrenetFrames(n,c);this.tangents=f.tangents,this.normals=f.normals,this.binormals=f.binormals;const d=new W,p=new W,m=new Wt;let g=new W;const v=[],y=[],x=[],E=[];b(),this.setIndex(E),this.setAttribute("position",new Cn(v,3)),this.setAttribute("normal",new Cn(y,3)),this.setAttribute("uv",new Cn(x,2));function b(){for(let N=0;N<n;N++)M(N);M(c===!1?n:0),I(),_()}function M(N){g=t.getPointAt(N/n,g);const C=f.normals[N],V=f.binormals[N];for(let F=0;F<=l;F++){const P=F/l*Math.PI*2,G=Math.sin(P),U=-Math.cos(P);p.x=U*C.x+G*V.x,p.y=U*C.y+G*V.y,p.z=U*C.z+G*V.z,p.normalize(),y.push(p.x,p.y,p.z),d.x=g.x+a*p.x,d.y=g.y+a*p.y,d.z=g.z+a*p.z,v.push(d.x,d.y,d.z)}}function _(){for(let N=1;N<=n;N++)for(let C=1;C<=l;C++){const V=(l+1)*(N-1)+(C-1),F=(l+1)*N+(C-1),P=(l+1)*N+C,G=(l+1)*(N-1)+C;E.push(V,F,G),E.push(F,P,G)}}function I(){for(let N=0;N<=n;N++)for(let C=0;C<=l;C++)m.x=N/n,m.y=C/l,x.push(m.x,m.y)}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}toJSON(){const t=super.toJSON();return t.path=this.parameters.path.toJSON(),t}static fromJSON(t){return new Am(new ST[t.path.type]().fromJSON(t.path),t.tubularSegments,t.radius,t.radialSegments,t.closed)}}class MT extends cf{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=sb,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class ET extends cf{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}class Gx extends si{constructor(t,n=1){super(),this.isLight=!0,this.type="Light",this.color=new de(t),this.intensity=n}dispose(){}copy(t,n){return super.copy(t,n),this.color.copy(t.color),this.intensity=t.intensity,this}toJSON(t){const n=super.toJSON(t);return n.object.color=this.color.getHex(),n.object.intensity=this.intensity,this.groundColor!==void 0&&(n.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(n.object.distance=this.distance),this.angle!==void 0&&(n.object.angle=this.angle),this.decay!==void 0&&(n.object.decay=this.decay),this.penumbra!==void 0&&(n.object.penumbra=this.penumbra),this.shadow!==void 0&&(n.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(n.object.target=this.target.uuid),n}}const Zd=new nn,ny=new W,iy=new W;class bT{constructor(t){this.camera=t,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Wt(512,512),this.map=null,this.mapPass=null,this.matrix=new nn,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new bm,this._frameExtents=new Wt(1,1),this._viewportCount=1,this._viewports=[new qe(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(t){const n=this.camera,a=this.matrix;ny.setFromMatrixPosition(t.matrixWorld),n.position.copy(ny),iy.setFromMatrixPosition(t.target.matrixWorld),n.lookAt(iy),n.updateMatrixWorld(),Zd.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Zd),a.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),a.multiply(Zd)}getViewport(t){return this._viewports[t]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(t){return this.camera=t.camera.clone(),this.intensity=t.intensity,this.bias=t.bias,this.radius=t.radius,this.mapSize.copy(t.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const t={};return this.intensity!==1&&(t.intensity=this.intensity),this.bias!==0&&(t.bias=this.bias),this.normalBias!==0&&(t.normalBias=this.normalBias),this.radius!==1&&(t.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(t.mapSize=this.mapSize.toArray()),t.camera=this.camera.toJSON(!1).object,delete t.camera.matrix,t}}const ay=new nn,Vl=new W,Kd=new W;class TT extends bT{constructor(){super(new _i(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Wt(4,2),this._viewportCount=6,this._viewports=[new qe(2,1,1,1),new qe(0,1,1,1),new qe(3,1,1,1),new qe(1,1,1,1),new qe(3,0,1,1),new qe(1,0,1,1)],this._cubeDirections=[new W(1,0,0),new W(-1,0,0),new W(0,0,1),new W(0,0,-1),new W(0,1,0),new W(0,-1,0)],this._cubeUps=[new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,0,1),new W(0,0,-1)]}updateMatrices(t,n=0){const a=this.camera,l=this.matrix,c=t.distance||a.far;c!==a.far&&(a.far=c,a.updateProjectionMatrix()),Vl.setFromMatrixPosition(t.matrixWorld),a.position.copy(Vl),Kd.copy(a.position),Kd.add(this._cubeDirections[n]),a.up.copy(this._cubeUps[n]),a.lookAt(Kd),a.updateMatrixWorld(),l.makeTranslation(-Vl.x,-Vl.y,-Vl.z),ay.multiplyMatrices(a.projectionMatrix,a.matrixWorldInverse),this._frustum.setFromProjectionMatrix(ay)}}class AT extends Gx{constructor(t,n,a=0,l=2){super(t,n),this.isPointLight=!0,this.type="PointLight",this.distance=a,this.decay=l,this.shadow=new TT}get power(){return this.intensity*4*Math.PI}set power(t){this.intensity=t/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(t,n){return super.copy(t,n),this.distance=t.distance,this.decay=t.decay,this.shadow=t.shadow.clone(),this}}class Vx extends Px{constructor(t=-1,n=1,a=1,l=-1,c=.1,f=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=n,this.top=a,this.bottom=l,this.near=c,this.far=f,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,n,a,l,c,f){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=a,this.view.offsetY=l,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),n=(this.top-this.bottom)/(2*this.zoom),a=(this.right+this.left)/2,l=(this.top+this.bottom)/2;let c=a-t,f=a+t,d=l+n,p=l-n;if(this.view!==null&&this.view.enabled){const m=(this.right-this.left)/this.view.fullWidth/this.zoom,g=(this.top-this.bottom)/this.view.fullHeight/this.zoom;c+=m*this.view.offsetX,f=c+m*this.view.width,d-=g*this.view.offsetY,p=d-g*this.view.height}this.projectionMatrix.makeOrthographic(c,f,d,p,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.zoom=this.zoom,n.object.left=this.left,n.object.right=this.right,n.object.top=this.top,n.object.bottom=this.bottom,n.object.near=this.near,n.object.far=this.far,this.view!==null&&(n.object.view=Object.assign({},this.view)),n}}class CT extends Gx{constructor(t,n){super(t,n),this.isAmbientLight=!0,this.type="AmbientLight"}}class RT extends _i{constructor(t=[]){super(),this.isArrayCamera=!0,this.cameras=t}}class kx{constructor(t=!0){this.autoStart=t,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=sy(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let t=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const n=sy();t=(n-this.oldTime)/1e3,this.oldTime=n,this.elapsedTime+=t}return t}}function sy(){return performance.now()}function ry(s,t,n,a){const l=wT(a);switch(n){case yx:return s*t;case Sx:return s*t;case Mx:return s*t*2;case Ex:return s*t/l.components*l.byteLength;case ym:return s*t/l.components*l.byteLength;case bx:return s*t*2/l.components*l.byteLength;case xm:return s*t*2/l.components*l.byteLength;case xx:return s*t*3/l.components*l.byteLength;case Fi:return s*t*4/l.components*l.byteLength;case Sm:return s*t*4/l.components*l.byteLength;case Yu:case Qu:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*8;case Zu:case Ku:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case Pp:case Ip:return Math.max(s,16)*Math.max(t,8)/4;case Op:case zp:return Math.max(s,8)*Math.max(t,8)/2;case Bp:case Fp:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*8;case Hp:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case Gp:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case Vp:return Math.floor((s+4)/5)*Math.floor((t+3)/4)*16;case kp:return Math.floor((s+4)/5)*Math.floor((t+4)/5)*16;case Xp:return Math.floor((s+5)/6)*Math.floor((t+4)/5)*16;case jp:return Math.floor((s+5)/6)*Math.floor((t+5)/6)*16;case qp:return Math.floor((s+7)/8)*Math.floor((t+4)/5)*16;case Wp:return Math.floor((s+7)/8)*Math.floor((t+5)/6)*16;case Yp:return Math.floor((s+7)/8)*Math.floor((t+7)/8)*16;case Qp:return Math.floor((s+9)/10)*Math.floor((t+4)/5)*16;case Zp:return Math.floor((s+9)/10)*Math.floor((t+5)/6)*16;case Kp:return Math.floor((s+9)/10)*Math.floor((t+7)/8)*16;case Jp:return Math.floor((s+9)/10)*Math.floor((t+9)/10)*16;case $p:return Math.floor((s+11)/12)*Math.floor((t+9)/10)*16;case tm:return Math.floor((s+11)/12)*Math.floor((t+11)/12)*16;case Ju:case em:case nm:return Math.ceil(s/4)*Math.ceil(t/4)*16;case Tx:case im:return Math.ceil(s/4)*Math.ceil(t/4)*8;case am:case sm:return Math.ceil(s/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${n} format.`)}function wT(s){switch(s){case Pa:case gx:return{byteLength:1,components:1};case tc:case vx:case La:return{byteLength:2,components:1};case vm:case _m:return{byteLength:2,components:4};case gr:case gm:case Da:return{byteLength:4,components:1};case _x:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${s}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:mm}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=mm);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function Xx(){let s=null,t=!1,n=null,a=null;function l(c,f){n(c,f),a=s.requestAnimationFrame(l)}return{start:function(){t!==!0&&n!==null&&(a=s.requestAnimationFrame(l),t=!0)},stop:function(){s.cancelAnimationFrame(a),t=!1},setAnimationLoop:function(c){n=c},setContext:function(c){s=c}}}function DT(s){const t=new WeakMap;function n(d,p){const m=d.array,g=d.usage,v=m.byteLength,y=s.createBuffer();s.bindBuffer(p,y),s.bufferData(p,m,g),d.onUploadCallback();let x;if(m instanceof Float32Array)x=s.FLOAT;else if(m instanceof Uint16Array)d.isFloat16BufferAttribute?x=s.HALF_FLOAT:x=s.UNSIGNED_SHORT;else if(m instanceof Int16Array)x=s.SHORT;else if(m instanceof Uint32Array)x=s.UNSIGNED_INT;else if(m instanceof Int32Array)x=s.INT;else if(m instanceof Int8Array)x=s.BYTE;else if(m instanceof Uint8Array)x=s.UNSIGNED_BYTE;else if(m instanceof Uint8ClampedArray)x=s.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+m);return{buffer:y,type:x,bytesPerElement:m.BYTES_PER_ELEMENT,version:d.version,size:v}}function a(d,p,m){const g=p.array,v=p.updateRanges;if(s.bindBuffer(m,d),v.length===0)s.bufferSubData(m,0,g);else{v.sort((x,E)=>x.start-E.start);let y=0;for(let x=1;x<v.length;x++){const E=v[y],b=v[x];b.start<=E.start+E.count+1?E.count=Math.max(E.count,b.start+b.count-E.start):(++y,v[y]=b)}v.length=y+1;for(let x=0,E=v.length;x<E;x++){const b=v[x];s.bufferSubData(m,b.start*g.BYTES_PER_ELEMENT,g,b.start,b.count)}p.clearUpdateRanges()}p.onUploadCallback()}function l(d){return d.isInterleavedBufferAttribute&&(d=d.data),t.get(d)}function c(d){d.isInterleavedBufferAttribute&&(d=d.data);const p=t.get(d);p&&(s.deleteBuffer(p.buffer),t.delete(d))}function f(d,p){if(d.isInterleavedBufferAttribute&&(d=d.data),d.isGLBufferAttribute){const g=t.get(d);(!g||g.version<d.version)&&t.set(d,{buffer:d.buffer,type:d.type,bytesPerElement:d.elementSize,version:d.version});return}const m=t.get(d);if(m===void 0)t.set(d,n(d,p));else if(m.version<d.version){if(m.size!==d.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");a(m.buffer,d,p),m.version=d.version}}return{get:l,remove:c,update:f}}var UT=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,NT=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,LT=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,OT=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,PT=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,zT=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,IT=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,BT=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,FT=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,HT=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,GT=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,VT=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,kT=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,XT=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,jT=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,qT=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,WT=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,YT=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,QT=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,ZT=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,KT=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,JT=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,$T=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,tA=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,eA=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,nA=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,iA=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,aA=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,sA=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,rA=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,oA="gl_FragColor = linearToOutputTexel( gl_FragColor );",lA=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,cA=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,uA=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,fA=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,hA=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,dA=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,pA=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,mA=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,gA=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,vA=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,_A=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,yA=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,xA=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,SA=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,MA=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,EA=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,bA=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,TA=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,AA=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,CA=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,RA=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,wA=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,DA=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,UA=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,NA=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,LA=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,OA=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,PA=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,zA=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,IA=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,BA=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,FA=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,HA=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,GA=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,VA=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,kA=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,XA=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,jA=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,qA=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,WA=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,YA=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,QA=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,ZA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,KA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,JA=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,$A=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,t2=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,e2=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,n2=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,i2=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,a2=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,s2=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,r2=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,o2=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,l2=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,c2=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,u2=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,f2=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,h2=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,d2=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,p2=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,m2=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,g2=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,v2=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,_2=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,y2=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,x2=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,S2=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,M2=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,E2=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,b2=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,T2=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
		
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
		
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		
		#else
		
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,A2=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,C2=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,R2=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,w2=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const D2=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,U2=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,N2=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,L2=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,O2=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,P2=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,z2=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,I2=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,B2=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,F2=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,H2=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,G2=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,V2=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,k2=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,X2=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,j2=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,q2=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,W2=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Y2=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,Q2=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Z2=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,K2=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,J2=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,$2=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,tC=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,eC=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,nC=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,iC=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,aC=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,sC=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,rC=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,oC=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,lC=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,cC=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,he={alphahash_fragment:UT,alphahash_pars_fragment:NT,alphamap_fragment:LT,alphamap_pars_fragment:OT,alphatest_fragment:PT,alphatest_pars_fragment:zT,aomap_fragment:IT,aomap_pars_fragment:BT,batching_pars_vertex:FT,batching_vertex:HT,begin_vertex:GT,beginnormal_vertex:VT,bsdfs:kT,iridescence_fragment:XT,bumpmap_pars_fragment:jT,clipping_planes_fragment:qT,clipping_planes_pars_fragment:WT,clipping_planes_pars_vertex:YT,clipping_planes_vertex:QT,color_fragment:ZT,color_pars_fragment:KT,color_pars_vertex:JT,color_vertex:$T,common:tA,cube_uv_reflection_fragment:eA,defaultnormal_vertex:nA,displacementmap_pars_vertex:iA,displacementmap_vertex:aA,emissivemap_fragment:sA,emissivemap_pars_fragment:rA,colorspace_fragment:oA,colorspace_pars_fragment:lA,envmap_fragment:cA,envmap_common_pars_fragment:uA,envmap_pars_fragment:fA,envmap_pars_vertex:hA,envmap_physical_pars_fragment:EA,envmap_vertex:dA,fog_vertex:pA,fog_pars_vertex:mA,fog_fragment:gA,fog_pars_fragment:vA,gradientmap_pars_fragment:_A,lightmap_pars_fragment:yA,lights_lambert_fragment:xA,lights_lambert_pars_fragment:SA,lights_pars_begin:MA,lights_toon_fragment:bA,lights_toon_pars_fragment:TA,lights_phong_fragment:AA,lights_phong_pars_fragment:CA,lights_physical_fragment:RA,lights_physical_pars_fragment:wA,lights_fragment_begin:DA,lights_fragment_maps:UA,lights_fragment_end:NA,logdepthbuf_fragment:LA,logdepthbuf_pars_fragment:OA,logdepthbuf_pars_vertex:PA,logdepthbuf_vertex:zA,map_fragment:IA,map_pars_fragment:BA,map_particle_fragment:FA,map_particle_pars_fragment:HA,metalnessmap_fragment:GA,metalnessmap_pars_fragment:VA,morphinstance_vertex:kA,morphcolor_vertex:XA,morphnormal_vertex:jA,morphtarget_pars_vertex:qA,morphtarget_vertex:WA,normal_fragment_begin:YA,normal_fragment_maps:QA,normal_pars_fragment:ZA,normal_pars_vertex:KA,normal_vertex:JA,normalmap_pars_fragment:$A,clearcoat_normal_fragment_begin:t2,clearcoat_normal_fragment_maps:e2,clearcoat_pars_fragment:n2,iridescence_pars_fragment:i2,opaque_fragment:a2,packing:s2,premultiplied_alpha_fragment:r2,project_vertex:o2,dithering_fragment:l2,dithering_pars_fragment:c2,roughnessmap_fragment:u2,roughnessmap_pars_fragment:f2,shadowmap_pars_fragment:h2,shadowmap_pars_vertex:d2,shadowmap_vertex:p2,shadowmask_pars_fragment:m2,skinbase_vertex:g2,skinning_pars_vertex:v2,skinning_vertex:_2,skinnormal_vertex:y2,specularmap_fragment:x2,specularmap_pars_fragment:S2,tonemapping_fragment:M2,tonemapping_pars_fragment:E2,transmission_fragment:b2,transmission_pars_fragment:T2,uv_pars_fragment:A2,uv_pars_vertex:C2,uv_vertex:R2,worldpos_vertex:w2,background_vert:D2,background_frag:U2,backgroundCube_vert:N2,backgroundCube_frag:L2,cube_vert:O2,cube_frag:P2,depth_vert:z2,depth_frag:I2,distanceRGBA_vert:B2,distanceRGBA_frag:F2,equirect_vert:H2,equirect_frag:G2,linedashed_vert:V2,linedashed_frag:k2,meshbasic_vert:X2,meshbasic_frag:j2,meshlambert_vert:q2,meshlambert_frag:W2,meshmatcap_vert:Y2,meshmatcap_frag:Q2,meshnormal_vert:Z2,meshnormal_frag:K2,meshphong_vert:J2,meshphong_frag:$2,meshphysical_vert:tC,meshphysical_frag:eC,meshtoon_vert:nC,meshtoon_frag:iC,points_vert:aC,points_frag:sC,shadow_vert:rC,shadow_frag:oC,sprite_vert:lC,sprite_frag:cC},Lt={common:{diffuse:{value:new de(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new fe},alphaMap:{value:null},alphaMapTransform:{value:new fe},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new fe}},envmap:{envMap:{value:null},envMapRotation:{value:new fe},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new fe}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new fe}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new fe},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new fe},normalScale:{value:new Wt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new fe},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new fe}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new fe}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new fe}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new de(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new de(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new fe},alphaTest:{value:0},uvTransform:{value:new fe}},sprite:{diffuse:{value:new de(16777215)},opacity:{value:1},center:{value:new Wt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new fe},alphaMap:{value:null},alphaMapTransform:{value:new fe},alphaTest:{value:0}}},Ji={basic:{uniforms:jn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.fog]),vertexShader:he.meshbasic_vert,fragmentShader:he.meshbasic_frag},lambert:{uniforms:jn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new de(0)}}]),vertexShader:he.meshlambert_vert,fragmentShader:he.meshlambert_frag},phong:{uniforms:jn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new de(0)},specular:{value:new de(1118481)},shininess:{value:30}}]),vertexShader:he.meshphong_vert,fragmentShader:he.meshphong_frag},standard:{uniforms:jn([Lt.common,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.roughnessmap,Lt.metalnessmap,Lt.fog,Lt.lights,{emissive:{value:new de(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag},toon:{uniforms:jn([Lt.common,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.gradientmap,Lt.fog,Lt.lights,{emissive:{value:new de(0)}}]),vertexShader:he.meshtoon_vert,fragmentShader:he.meshtoon_frag},matcap:{uniforms:jn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,{matcap:{value:null}}]),vertexShader:he.meshmatcap_vert,fragmentShader:he.meshmatcap_frag},points:{uniforms:jn([Lt.points,Lt.fog]),vertexShader:he.points_vert,fragmentShader:he.points_frag},dashed:{uniforms:jn([Lt.common,Lt.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:he.linedashed_vert,fragmentShader:he.linedashed_frag},depth:{uniforms:jn([Lt.common,Lt.displacementmap]),vertexShader:he.depth_vert,fragmentShader:he.depth_frag},normal:{uniforms:jn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,{opacity:{value:1}}]),vertexShader:he.meshnormal_vert,fragmentShader:he.meshnormal_frag},sprite:{uniforms:jn([Lt.sprite,Lt.fog]),vertexShader:he.sprite_vert,fragmentShader:he.sprite_frag},background:{uniforms:{uvTransform:{value:new fe},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:he.background_vert,fragmentShader:he.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new fe}},vertexShader:he.backgroundCube_vert,fragmentShader:he.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:he.cube_vert,fragmentShader:he.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:he.equirect_vert,fragmentShader:he.equirect_frag},distanceRGBA:{uniforms:jn([Lt.common,Lt.displacementmap,{referencePosition:{value:new W},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:he.distanceRGBA_vert,fragmentShader:he.distanceRGBA_frag},shadow:{uniforms:jn([Lt.lights,Lt.fog,{color:{value:new de(0)},opacity:{value:1}}]),vertexShader:he.shadow_vert,fragmentShader:he.shadow_frag}};Ji.physical={uniforms:jn([Ji.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new fe},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new fe},clearcoatNormalScale:{value:new Wt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new fe},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new fe},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new fe},sheen:{value:0},sheenColor:{value:new de(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new fe},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new fe},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new fe},transmissionSamplerSize:{value:new Wt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new fe},attenuationDistance:{value:0},attenuationColor:{value:new de(0)},specularColor:{value:new de(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new fe},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new fe},anisotropyVector:{value:new Wt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new fe}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag};const ku={r:0,b:0,g:0},Ks=new za,uC=new nn;function fC(s,t,n,a,l,c,f){const d=new de(0);let p=c===!0?0:1,m,g,v=null,y=0,x=null;function E(N){let C=N.isScene===!0?N.background:null;return C&&C.isTexture&&(C=(N.backgroundBlurriness>0?n:t).get(C)),C}function b(N){let C=!1;const V=E(N);V===null?_(d,p):V&&V.isColor&&(_(V,1),C=!0);const F=s.xr.getEnvironmentBlendMode();F==="additive"?a.buffers.color.setClear(0,0,0,1,f):F==="alpha-blend"&&a.buffers.color.setClear(0,0,0,0,f),(s.autoClear||C)&&(a.buffers.depth.setTest(!0),a.buffers.depth.setMask(!0),a.buffers.color.setMask(!0),s.clear(s.autoClearColor,s.autoClearDepth,s.autoClearStencil))}function M(N,C){const V=E(C);V&&(V.isCubeTexture||V.mapping===lf)?(g===void 0&&(g=new Wn(new uc(1,1,1),new Yn({name:"BackgroundCubeMaterial",uniforms:Ho(Ji.backgroundCube.uniforms),vertexShader:Ji.backgroundCube.vertexShader,fragmentShader:Ji.backgroundCube.fragmentShader,side:ii,depthTest:!1,depthWrite:!1,fog:!1})),g.geometry.deleteAttribute("normal"),g.geometry.deleteAttribute("uv"),g.onBeforeRender=function(F,P,G){this.matrixWorld.copyPosition(G.matrixWorld)},Object.defineProperty(g.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),l.update(g)),Ks.copy(C.backgroundRotation),Ks.x*=-1,Ks.y*=-1,Ks.z*=-1,V.isCubeTexture&&V.isRenderTargetTexture===!1&&(Ks.y*=-1,Ks.z*=-1),g.material.uniforms.envMap.value=V,g.material.uniforms.flipEnvMap.value=V.isCubeTexture&&V.isRenderTargetTexture===!1?-1:1,g.material.uniforms.backgroundBlurriness.value=C.backgroundBlurriness,g.material.uniforms.backgroundIntensity.value=C.backgroundIntensity,g.material.uniforms.backgroundRotation.value.setFromMatrix4(uC.makeRotationFromEuler(Ks)),g.material.toneMapped=Oe.getTransfer(V.colorSpace)!==je,(v!==V||y!==V.version||x!==s.toneMapping)&&(g.material.needsUpdate=!0,v=V,y=V.version,x=s.toneMapping),g.layers.enableAll(),N.unshift(g,g.geometry,g.material,0,0,null)):V&&V.isTexture&&(m===void 0&&(m=new Wn(new uf(2,2),new Yn({name:"BackgroundMaterial",uniforms:Ho(Ji.background.uniforms),vertexShader:Ji.background.vertexShader,fragmentShader:Ji.background.fragmentShader,side:As,depthTest:!1,depthWrite:!1,fog:!1})),m.geometry.deleteAttribute("normal"),Object.defineProperty(m.material,"map",{get:function(){return this.uniforms.t2D.value}}),l.update(m)),m.material.uniforms.t2D.value=V,m.material.uniforms.backgroundIntensity.value=C.backgroundIntensity,m.material.toneMapped=Oe.getTransfer(V.colorSpace)!==je,V.matrixAutoUpdate===!0&&V.updateMatrix(),m.material.uniforms.uvTransform.value.copy(V.matrix),(v!==V||y!==V.version||x!==s.toneMapping)&&(m.material.needsUpdate=!0,v=V,y=V.version,x=s.toneMapping),m.layers.enableAll(),N.unshift(m,m.geometry,m.material,0,0,null))}function _(N,C){N.getRGB(ku,Ox(s)),a.buffers.color.setClear(ku.r,ku.g,ku.b,C,f)}function I(){g!==void 0&&(g.geometry.dispose(),g.material.dispose()),m!==void 0&&(m.geometry.dispose(),m.material.dispose())}return{getClearColor:function(){return d},setClearColor:function(N,C=1){d.set(N),p=C,_(d,p)},getClearAlpha:function(){return p},setClearAlpha:function(N){p=N,_(d,p)},render:b,addToRenderList:M,dispose:I}}function hC(s,t){const n=s.getParameter(s.MAX_VERTEX_ATTRIBS),a={},l=y(null);let c=l,f=!1;function d(w,H,ut,ot,mt){let ct=!1;const z=v(ot,ut,H);c!==z&&(c=z,m(c.object)),ct=x(w,ot,ut,mt),ct&&E(w,ot,ut,mt),mt!==null&&t.update(mt,s.ELEMENT_ARRAY_BUFFER),(ct||f)&&(f=!1,C(w,H,ut,ot),mt!==null&&s.bindBuffer(s.ELEMENT_ARRAY_BUFFER,t.get(mt).buffer))}function p(){return s.createVertexArray()}function m(w){return s.bindVertexArray(w)}function g(w){return s.deleteVertexArray(w)}function v(w,H,ut){const ot=ut.wireframe===!0;let mt=a[w.id];mt===void 0&&(mt={},a[w.id]=mt);let ct=mt[H.id];ct===void 0&&(ct={},mt[H.id]=ct);let z=ct[ot];return z===void 0&&(z=y(p()),ct[ot]=z),z}function y(w){const H=[],ut=[],ot=[];for(let mt=0;mt<n;mt++)H[mt]=0,ut[mt]=0,ot[mt]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ut,attributeDivisors:ot,object:w,attributes:{},index:null}}function x(w,H,ut,ot){const mt=c.attributes,ct=H.attributes;let z=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){const At=mt[$];let O=ct[$];if(O===void 0&&($==="instanceMatrix"&&w.instanceMatrix&&(O=w.instanceMatrix),$==="instanceColor"&&w.instanceColor&&(O=w.instanceColor)),At===void 0||At.attribute!==O||O&&At.data!==O.data)return!0;z++}return c.attributesNum!==z||c.index!==ot}function E(w,H,ut,ot){const mt={},ct=H.attributes;let z=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){let At=ct[$];At===void 0&&($==="instanceMatrix"&&w.instanceMatrix&&(At=w.instanceMatrix),$==="instanceColor"&&w.instanceColor&&(At=w.instanceColor));const O={};O.attribute=At,At&&At.data&&(O.data=At.data),mt[$]=O,z++}c.attributes=mt,c.attributesNum=z,c.index=ot}function b(){const w=c.newAttributes;for(let H=0,ut=w.length;H<ut;H++)w[H]=0}function M(w){_(w,0)}function _(w,H){const ut=c.newAttributes,ot=c.enabledAttributes,mt=c.attributeDivisors;ut[w]=1,ot[w]===0&&(s.enableVertexAttribArray(w),ot[w]=1),mt[w]!==H&&(s.vertexAttribDivisor(w,H),mt[w]=H)}function I(){const w=c.newAttributes,H=c.enabledAttributes;for(let ut=0,ot=H.length;ut<ot;ut++)H[ut]!==w[ut]&&(s.disableVertexAttribArray(ut),H[ut]=0)}function N(w,H,ut,ot,mt,ct,z){z===!0?s.vertexAttribIPointer(w,H,ut,mt,ct):s.vertexAttribPointer(w,H,ut,ot,mt,ct)}function C(w,H,ut,ot){b();const mt=ot.attributes,ct=ut.getAttributes(),z=H.defaultAttributeValues;for(const Z in ct){const $=ct[Z];if($.location>=0){let Et=mt[Z];if(Et===void 0&&(Z==="instanceMatrix"&&w.instanceMatrix&&(Et=w.instanceMatrix),Z==="instanceColor"&&w.instanceColor&&(Et=w.instanceColor)),Et!==void 0){const At=Et.normalized,O=Et.itemSize,nt=t.get(Et);if(nt===void 0)continue;const St=nt.buffer,q=nt.type,ft=nt.bytesPerElement,Tt=q===s.INT||q===s.UNSIGNED_INT||Et.gpuType===gm;if(Et.isInterleavedBufferAttribute){const Mt=Et.data,Ft=Mt.stride,Vt=Et.offset;if(Mt.isInstancedInterleavedBuffer){for(let re=0;re<$.locationSize;re++)_($.location+re,Mt.meshPerAttribute);w.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Mt.meshPerAttribute*Mt.count)}else for(let re=0;re<$.locationSize;re++)M($.location+re);s.bindBuffer(s.ARRAY_BUFFER,St);for(let re=0;re<$.locationSize;re++)N($.location+re,O/$.locationSize,q,At,Ft*ft,(Vt+O/$.locationSize*re)*ft,Tt)}else{if(Et.isInstancedBufferAttribute){for(let Mt=0;Mt<$.locationSize;Mt++)_($.location+Mt,Et.meshPerAttribute);w.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Et.meshPerAttribute*Et.count)}else for(let Mt=0;Mt<$.locationSize;Mt++)M($.location+Mt);s.bindBuffer(s.ARRAY_BUFFER,St);for(let Mt=0;Mt<$.locationSize;Mt++)N($.location+Mt,O/$.locationSize,q,At,O*ft,O/$.locationSize*Mt*ft,Tt)}}else if(z!==void 0){const At=z[Z];if(At!==void 0)switch(At.length){case 2:s.vertexAttrib2fv($.location,At);break;case 3:s.vertexAttrib3fv($.location,At);break;case 4:s.vertexAttrib4fv($.location,At);break;default:s.vertexAttrib1fv($.location,At)}}}}I()}function V(){G();for(const w in a){const H=a[w];for(const ut in H){const ot=H[ut];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete H[ut]}delete a[w]}}function F(w){if(a[w.id]===void 0)return;const H=a[w.id];for(const ut in H){const ot=H[ut];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete H[ut]}delete a[w.id]}function P(w){for(const H in a){const ut=a[H];if(ut[w.id]===void 0)continue;const ot=ut[w.id];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete ut[w.id]}}function G(){U(),f=!0,c!==l&&(c=l,m(c.object))}function U(){l.geometry=null,l.program=null,l.wireframe=!1}return{setup:d,reset:G,resetDefaultState:U,dispose:V,releaseStatesOfGeometry:F,releaseStatesOfProgram:P,initAttributes:b,enableAttribute:M,disableUnusedAttributes:I}}function dC(s,t,n){let a;function l(m){a=m}function c(m,g){s.drawArrays(a,m,g),n.update(g,a,1)}function f(m,g,v){v!==0&&(s.drawArraysInstanced(a,m,g,v),n.update(g,a,v))}function d(m,g,v){if(v===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(a,m,0,g,0,v);let x=0;for(let E=0;E<v;E++)x+=g[E];n.update(x,a,1)}function p(m,g,v,y){if(v===0)return;const x=t.get("WEBGL_multi_draw");if(x===null)for(let E=0;E<m.length;E++)f(m[E],g[E],y[E]);else{x.multiDrawArraysInstancedWEBGL(a,m,0,g,0,y,0,v);let E=0;for(let b=0;b<v;b++)E+=g[b]*y[b];n.update(E,a,1)}}this.setMode=l,this.render=c,this.renderInstances=f,this.renderMultiDraw=d,this.renderMultiDrawInstances=p}function pC(s,t,n,a){let l;function c(){if(l!==void 0)return l;if(t.has("EXT_texture_filter_anisotropic")===!0){const P=t.get("EXT_texture_filter_anisotropic");l=s.getParameter(P.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else l=0;return l}function f(P){return!(P!==Fi&&a.convert(P)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_FORMAT))}function d(P){const G=P===La&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(P!==Pa&&a.convert(P)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_TYPE)&&P!==Da&&!G)}function p(P){if(P==="highp"){if(s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.HIGH_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.HIGH_FLOAT).precision>0)return"highp";P="mediump"}return P==="mediump"&&s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.MEDIUM_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let m=n.precision!==void 0?n.precision:"highp";const g=p(m);g!==m&&(console.warn("THREE.WebGLRenderer:",m,"not supported, using",g,"instead."),m=g);const v=n.logarithmicDepthBuffer===!0,y=n.reverseDepthBuffer===!0&&t.has("EXT_clip_control"),x=s.getParameter(s.MAX_TEXTURE_IMAGE_UNITS),E=s.getParameter(s.MAX_VERTEX_TEXTURE_IMAGE_UNITS),b=s.getParameter(s.MAX_TEXTURE_SIZE),M=s.getParameter(s.MAX_CUBE_MAP_TEXTURE_SIZE),_=s.getParameter(s.MAX_VERTEX_ATTRIBS),I=s.getParameter(s.MAX_VERTEX_UNIFORM_VECTORS),N=s.getParameter(s.MAX_VARYING_VECTORS),C=s.getParameter(s.MAX_FRAGMENT_UNIFORM_VECTORS),V=E>0,F=s.getParameter(s.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:c,getMaxPrecision:p,textureFormatReadable:f,textureTypeReadable:d,precision:m,logarithmicDepthBuffer:v,reverseDepthBuffer:y,maxTextures:x,maxVertexTextures:E,maxTextureSize:b,maxCubemapSize:M,maxAttributes:_,maxVertexUniforms:I,maxVaryings:N,maxFragmentUniforms:C,vertexTextures:V,maxSamples:F}}function mC(s){const t=this;let n=null,a=0,l=!1,c=!1;const f=new $s,d=new fe,p={value:null,needsUpdate:!1};this.uniform=p,this.numPlanes=0,this.numIntersection=0,this.init=function(v,y){const x=v.length!==0||y||a!==0||l;return l=y,a=v.length,x},this.beginShadows=function(){c=!0,g(null)},this.endShadows=function(){c=!1},this.setGlobalState=function(v,y){n=g(v,y,0)},this.setState=function(v,y,x){const E=v.clippingPlanes,b=v.clipIntersection,M=v.clipShadows,_=s.get(v);if(!l||E===null||E.length===0||c&&!M)c?g(null):m();else{const I=c?0:a,N=I*4;let C=_.clippingState||null;p.value=C,C=g(E,y,N,x);for(let V=0;V!==N;++V)C[V]=n[V];_.clippingState=C,this.numIntersection=b?this.numPlanes:0,this.numPlanes+=I}};function m(){p.value!==n&&(p.value=n,p.needsUpdate=a>0),t.numPlanes=a,t.numIntersection=0}function g(v,y,x,E){const b=v!==null?v.length:0;let M=null;if(b!==0){if(M=p.value,E!==!0||M===null){const _=x+b*4,I=y.matrixWorldInverse;d.getNormalMatrix(I),(M===null||M.length<_)&&(M=new Float32Array(_));for(let N=0,C=x;N!==b;++N,C+=4)f.copy(v[N]).applyMatrix4(I,d),f.normal.toArray(M,C),M[C+3]=f.constant}p.value=M,p.needsUpdate=!0}return t.numPlanes=b,t.numIntersection=0,M}}function gC(s){let t=new WeakMap;function n(f,d){return d===Dp?f.mapping=Po:d===Up&&(f.mapping=zo),f}function a(f){if(f&&f.isTexture){const d=f.mapping;if(d===Dp||d===Up)if(t.has(f)){const p=t.get(f).texture;return n(p,f.mapping)}else{const p=f.image;if(p&&p.height>0){const m=new iT(p.height);return m.fromEquirectangularTexture(s,f),t.set(f,m),f.addEventListener("dispose",l),n(m.texture,f.mapping)}else return null}}return f}function l(f){const d=f.target;d.removeEventListener("dispose",l);const p=t.get(d);p!==void 0&&(t.delete(d),p.dispose())}function c(){t=new WeakMap}return{get:a,dispose:c}}const go=4,oy=[.125,.215,.35,.446,.526,.582],nr=20,Jd=new Vx,ly=new de;let $d=null,tp=0,ep=0,np=!1;const tr=(1+Math.sqrt(5))/2,fo=1/tr,cy=[new W(-tr,fo,0),new W(tr,fo,0),new W(-fo,0,tr),new W(fo,0,tr),new W(0,tr,-fo),new W(0,tr,fo),new W(-1,1,-1),new W(1,1,-1),new W(-1,1,1),new W(1,1,1)];class uy{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(t,n=0,a=.1,l=100){$d=this._renderer.getRenderTarget(),tp=this._renderer.getActiveCubeFace(),ep=this._renderer.getActiveMipmapLevel(),np=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const c=this._allocateTargets();return c.depthBuffer=!0,this._sceneToCubeUV(t,a,l,c),n>0&&this._blur(c,0,0,n),this._applyPMREM(c),this._cleanup(c),c}fromEquirectangular(t,n=null){return this._fromTexture(t,n)}fromCubemap(t,n=null){return this._fromTexture(t,n)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=dy(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=hy(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodPlanes.length;t++)this._lodPlanes[t].dispose()}_cleanup(t){this._renderer.setRenderTarget($d,tp,ep),this._renderer.xr.enabled=np,t.scissorTest=!1,Xu(t,0,0,t.width,t.height)}_fromTexture(t,n){t.mapping===Po||t.mapping===zo?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),$d=this._renderer.getRenderTarget(),tp=this._renderer.getActiveCubeFace(),ep=this._renderer.getActiveMipmapLevel(),np=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const a=n||this._allocateTargets();return this._textureToCubeUV(t,a),this._applyPMREM(a),this._cleanup(a),a}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),n=4*this._cubeSize,a={magFilter:$i,minFilter:$i,generateMipmaps:!1,type:La,format:Fi,colorSpace:Fo,depthBuffer:!1},l=fy(t,n,a);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==n){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=fy(t,n,a);const{_lodMax:c}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=vC(c)),this._blurMaterial=_C(c,t,n)}return l}_compileMaterial(t){const n=new Wn(this._lodPlanes[0],t);this._renderer.compile(n,Jd)}_sceneToCubeUV(t,n,a,l){const d=new _i(90,1,n,a),p=[1,-1,1,1,1,1],m=[1,1,1,-1,-1,-1],g=this._renderer,v=g.autoClear,y=g.toneMapping;g.getClearColor(ly),g.toneMapping=Ts,g.autoClear=!1;const x=new vr({name:"PMREM.Background",side:ii,depthWrite:!1,depthTest:!1}),E=new Wn(new uc,x);let b=!1;const M=t.background;M?M.isColor&&(x.color.copy(M),t.background=null,b=!0):(x.color.copy(ly),b=!0);for(let _=0;_<6;_++){const I=_%3;I===0?(d.up.set(0,p[_],0),d.lookAt(m[_],0,0)):I===1?(d.up.set(0,0,p[_]),d.lookAt(0,m[_],0)):(d.up.set(0,p[_],0),d.lookAt(0,0,m[_]));const N=this._cubeSize;Xu(l,I*N,_>2?N:0,N,N),g.setRenderTarget(l),b&&g.render(E,d),g.render(t,d)}E.geometry.dispose(),E.material.dispose(),g.toneMapping=y,g.autoClear=v,t.background=M}_textureToCubeUV(t,n){const a=this._renderer,l=t.mapping===Po||t.mapping===zo;l?(this._cubemapMaterial===null&&(this._cubemapMaterial=dy()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=hy());const c=l?this._cubemapMaterial:this._equirectMaterial,f=new Wn(this._lodPlanes[0],c),d=c.uniforms;d.envMap.value=t;const p=this._cubeSize;Xu(n,0,0,3*p,2*p),a.setRenderTarget(n),a.render(f,Jd)}_applyPMREM(t){const n=this._renderer,a=n.autoClear;n.autoClear=!1;const l=this._lodPlanes.length;for(let c=1;c<l;c++){const f=Math.sqrt(this._sigmas[c]*this._sigmas[c]-this._sigmas[c-1]*this._sigmas[c-1]),d=cy[(l-c-1)%cy.length];this._blur(t,c-1,c,f,d)}n.autoClear=a}_blur(t,n,a,l,c){const f=this._pingPongRenderTarget;this._halfBlur(t,f,n,a,l,"latitudinal",c),this._halfBlur(f,t,a,a,l,"longitudinal",c)}_halfBlur(t,n,a,l,c,f,d){const p=this._renderer,m=this._blurMaterial;f!=="latitudinal"&&f!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const g=3,v=new Wn(this._lodPlanes[l],m),y=m.uniforms,x=this._sizeLods[a]-1,E=isFinite(c)?Math.PI/(2*x):2*Math.PI/(2*nr-1),b=c/E,M=isFinite(c)?1+Math.floor(g*b):nr;M>nr&&console.warn(`sigmaRadians, ${c}, is too large and will clip, as it requested ${M} samples when the maximum is set to ${nr}`);const _=[];let I=0;for(let P=0;P<nr;++P){const G=P/b,U=Math.exp(-G*G/2);_.push(U),P===0?I+=U:P<M&&(I+=2*U)}for(let P=0;P<_.length;P++)_[P]=_[P]/I;y.envMap.value=t.texture,y.samples.value=M,y.weights.value=_,y.latitudinal.value=f==="latitudinal",d&&(y.poleAxis.value=d);const{_lodMax:N}=this;y.dTheta.value=E,y.mipInt.value=N-a;const C=this._sizeLods[l],V=3*C*(l>N-go?l-N+go:0),F=4*(this._cubeSize-C);Xu(n,V,F,3*C,2*C),p.setRenderTarget(n),p.render(v,Jd)}}function vC(s){const t=[],n=[],a=[];let l=s;const c=s-go+1+oy.length;for(let f=0;f<c;f++){const d=Math.pow(2,l);n.push(d);let p=1/d;f>s-go?p=oy[f-s+go-1]:f===0&&(p=0),a.push(p);const m=1/(d-2),g=-m,v=1+m,y=[g,g,v,g,v,v,g,g,v,v,g,v],x=6,E=6,b=3,M=2,_=1,I=new Float32Array(b*E*x),N=new Float32Array(M*E*x),C=new Float32Array(_*E*x);for(let F=0;F<x;F++){const P=F%3*2/3-1,G=F>2?0:-1,U=[P,G,0,P+2/3,G,0,P+2/3,G+1,0,P,G,0,P+2/3,G+1,0,P,G+1,0];I.set(U,b*E*F),N.set(y,M*E*F);const w=[F,F,F,F,F,F];C.set(w,_*E*F)}const V=new Vi;V.setAttribute("position",new ta(I,b)),V.setAttribute("uv",new ta(N,M)),V.setAttribute("faceIndex",new ta(C,_)),t.push(V),l>go&&l--}return{lodPlanes:t,sizeLods:n,sigmas:a}}function fy(s,t,n){const a=new Gi(s,t,n);return a.texture.mapping=lf,a.texture.name="PMREM.cubeUv",a.scissorTest=!0,a}function Xu(s,t,n,a,l){s.viewport.set(t,n,a,l),s.scissor.set(t,n,a,l)}function _C(s,t,n){const a=new Float32Array(nr),l=new W(0,1,0);return new Yn({name:"SphericalGaussianBlur",defines:{n:nr,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:a},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:l}},vertexShader:Cm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Na,depthTest:!1,depthWrite:!1})}function hy(){return new Yn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Cm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Na,depthTest:!1,depthWrite:!1})}function dy(){return new Yn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Cm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Na,depthTest:!1,depthWrite:!1})}function Cm(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function yC(s){let t=new WeakMap,n=null;function a(d){if(d&&d.isTexture){const p=d.mapping,m=p===Dp||p===Up,g=p===Po||p===zo;if(m||g){let v=t.get(d);const y=v!==void 0?v.texture.pmremVersion:0;if(d.isRenderTargetTexture&&d.pmremVersion!==y)return n===null&&(n=new uy(s)),v=m?n.fromEquirectangular(d,v):n.fromCubemap(d,v),v.texture.pmremVersion=d.pmremVersion,t.set(d,v),v.texture;if(v!==void 0)return v.texture;{const x=d.image;return m&&x&&x.height>0||g&&x&&l(x)?(n===null&&(n=new uy(s)),v=m?n.fromEquirectangular(d):n.fromCubemap(d),v.texture.pmremVersion=d.pmremVersion,t.set(d,v),d.addEventListener("dispose",c),v.texture):null}}}return d}function l(d){let p=0;const m=6;for(let g=0;g<m;g++)d[g]!==void 0&&p++;return p===m}function c(d){const p=d.target;p.removeEventListener("dispose",c);const m=t.get(p);m!==void 0&&(t.delete(p),m.dispose())}function f(){t=new WeakMap,n!==null&&(n.dispose(),n=null)}return{get:a,dispose:f}}function xC(s){const t={};function n(a){if(t[a]!==void 0)return t[a];let l;switch(a){case"WEBGL_depth_texture":l=s.getExtension("WEBGL_depth_texture")||s.getExtension("MOZ_WEBGL_depth_texture")||s.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":l=s.getExtension("EXT_texture_filter_anisotropic")||s.getExtension("MOZ_EXT_texture_filter_anisotropic")||s.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":l=s.getExtension("WEBGL_compressed_texture_s3tc")||s.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||s.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":l=s.getExtension("WEBGL_compressed_texture_pvrtc")||s.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:l=s.getExtension(a)}return t[a]=l,l}return{has:function(a){return n(a)!==null},init:function(){n("EXT_color_buffer_float"),n("WEBGL_clip_cull_distance"),n("OES_texture_float_linear"),n("EXT_color_buffer_half_float"),n("WEBGL_multisampled_render_to_texture"),n("WEBGL_render_shared_exponent")},get:function(a){const l=n(a);return l===null&&po("THREE.WebGLRenderer: "+a+" extension not supported."),l}}}function SC(s,t,n,a){const l={},c=new WeakMap;function f(v){const y=v.target;y.index!==null&&t.remove(y.index);for(const E in y.attributes)t.remove(y.attributes[E]);y.removeEventListener("dispose",f),delete l[y.id];const x=c.get(y);x&&(t.remove(x),c.delete(y)),a.releaseStatesOfGeometry(y),y.isInstancedBufferGeometry===!0&&delete y._maxInstanceCount,n.memory.geometries--}function d(v,y){return l[y.id]===!0||(y.addEventListener("dispose",f),l[y.id]=!0,n.memory.geometries++),y}function p(v){const y=v.attributes;for(const x in y)t.update(y[x],s.ARRAY_BUFFER)}function m(v){const y=[],x=v.index,E=v.attributes.position;let b=0;if(x!==null){const I=x.array;b=x.version;for(let N=0,C=I.length;N<C;N+=3){const V=I[N+0],F=I[N+1],P=I[N+2];y.push(V,F,F,P,P,V)}}else if(E!==void 0){const I=E.array;b=E.version;for(let N=0,C=I.length/3-1;N<C;N+=3){const V=N+0,F=N+1,P=N+2;y.push(V,F,F,P,P,V)}}else return;const M=new(Cx(y)?Lx:Nx)(y,1);M.version=b;const _=c.get(v);_&&t.remove(_),c.set(v,M)}function g(v){const y=c.get(v);if(y){const x=v.index;x!==null&&y.version<x.version&&m(v)}else m(v);return c.get(v)}return{get:d,update:p,getWireframeAttribute:g}}function MC(s,t,n){let a;function l(y){a=y}let c,f;function d(y){c=y.type,f=y.bytesPerElement}function p(y,x){s.drawElements(a,x,c,y*f),n.update(x,a,1)}function m(y,x,E){E!==0&&(s.drawElementsInstanced(a,x,c,y*f,E),n.update(x,a,E))}function g(y,x,E){if(E===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(a,x,0,c,y,0,E);let M=0;for(let _=0;_<E;_++)M+=x[_];n.update(M,a,1)}function v(y,x,E,b){if(E===0)return;const M=t.get("WEBGL_multi_draw");if(M===null)for(let _=0;_<y.length;_++)m(y[_]/f,x[_],b[_]);else{M.multiDrawElementsInstancedWEBGL(a,x,0,c,y,0,b,0,E);let _=0;for(let I=0;I<E;I++)_+=x[I]*b[I];n.update(_,a,1)}}this.setMode=l,this.setIndex=d,this.render=p,this.renderInstances=m,this.renderMultiDraw=g,this.renderMultiDrawInstances=v}function EC(s){const t={geometries:0,textures:0},n={frame:0,calls:0,triangles:0,points:0,lines:0};function a(c,f,d){switch(n.calls++,f){case s.TRIANGLES:n.triangles+=d*(c/3);break;case s.LINES:n.lines+=d*(c/2);break;case s.LINE_STRIP:n.lines+=d*(c-1);break;case s.LINE_LOOP:n.lines+=d*c;break;case s.POINTS:n.points+=d*c;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",f);break}}function l(){n.calls=0,n.triangles=0,n.points=0,n.lines=0}return{memory:t,render:n,programs:null,autoReset:!0,reset:l,update:a}}function bC(s,t,n){const a=new WeakMap,l=new qe;function c(f,d,p){const m=f.morphTargetInfluences,g=d.morphAttributes.position||d.morphAttributes.normal||d.morphAttributes.color,v=g!==void 0?g.length:0;let y=a.get(d);if(y===void 0||y.count!==v){let w=function(){G.dispose(),a.delete(d),d.removeEventListener("dispose",w)};var x=w;y!==void 0&&y.texture.dispose();const E=d.morphAttributes.position!==void 0,b=d.morphAttributes.normal!==void 0,M=d.morphAttributes.color!==void 0,_=d.morphAttributes.position||[],I=d.morphAttributes.normal||[],N=d.morphAttributes.color||[];let C=0;E===!0&&(C=1),b===!0&&(C=2),M===!0&&(C=3);let V=d.attributes.position.count*C,F=1;V>t.maxTextureSize&&(F=Math.ceil(V/t.maxTextureSize),V=t.maxTextureSize);const P=new Float32Array(V*F*4*v),G=new wx(P,V,F,v);G.type=Da,G.needsUpdate=!0;const U=C*4;for(let H=0;H<v;H++){const ut=_[H],ot=I[H],mt=N[H],ct=V*F*4*H;for(let z=0;z<ut.count;z++){const Z=z*U;E===!0&&(l.fromBufferAttribute(ut,z),P[ct+Z+0]=l.x,P[ct+Z+1]=l.y,P[ct+Z+2]=l.z,P[ct+Z+3]=0),b===!0&&(l.fromBufferAttribute(ot,z),P[ct+Z+4]=l.x,P[ct+Z+5]=l.y,P[ct+Z+6]=l.z,P[ct+Z+7]=0),M===!0&&(l.fromBufferAttribute(mt,z),P[ct+Z+8]=l.x,P[ct+Z+9]=l.y,P[ct+Z+10]=l.z,P[ct+Z+11]=mt.itemSize===4?l.w:1)}}y={count:v,texture:G,size:new Wt(V,F)},a.set(d,y),d.addEventListener("dispose",w)}if(f.isInstancedMesh===!0&&f.morphTexture!==null)p.getUniforms().setValue(s,"morphTexture",f.morphTexture,n);else{let E=0;for(let M=0;M<m.length;M++)E+=m[M];const b=d.morphTargetsRelative?1:1-E;p.getUniforms().setValue(s,"morphTargetBaseInfluence",b),p.getUniforms().setValue(s,"morphTargetInfluences",m)}p.getUniforms().setValue(s,"morphTargetsTexture",y.texture,n),p.getUniforms().setValue(s,"morphTargetsTextureSize",y.size)}return{update:c}}function TC(s,t,n,a){let l=new WeakMap;function c(p){const m=a.render.frame,g=p.geometry,v=t.get(p,g);if(l.get(v)!==m&&(t.update(v),l.set(v,m)),p.isInstancedMesh&&(p.hasEventListener("dispose",d)===!1&&p.addEventListener("dispose",d),l.get(p)!==m&&(n.update(p.instanceMatrix,s.ARRAY_BUFFER),p.instanceColor!==null&&n.update(p.instanceColor,s.ARRAY_BUFFER),l.set(p,m))),p.isSkinnedMesh){const y=p.skeleton;l.get(y)!==m&&(y.update(),l.set(y,m))}return v}function f(){l=new WeakMap}function d(p){const m=p.target;m.removeEventListener("dispose",d),n.remove(m.instanceMatrix),m.instanceColor!==null&&n.remove(m.instanceColor)}return{update:c,dispose:f}}const jx=new ai,py=new Ix(1,1),qx=new wx,Wx=new Gb,Yx=new zx,my=[],gy=[],vy=new Float32Array(16),_y=new Float32Array(9),yy=new Float32Array(4);function Xo(s,t,n){const a=s[0];if(a<=0||a>0)return s;const l=t*n;let c=my[l];if(c===void 0&&(c=new Float32Array(l),my[l]=c),t!==0){a.toArray(c,0);for(let f=1,d=0;f!==t;++f)d+=n,s[f].toArray(c,d)}return c}function Sn(s,t){if(s.length!==t.length)return!1;for(let n=0,a=s.length;n<a;n++)if(s[n]!==t[n])return!1;return!0}function Mn(s,t){for(let n=0,a=t.length;n<a;n++)s[n]=t[n]}function hf(s,t){let n=gy[t];n===void 0&&(n=new Int32Array(t),gy[t]=n);for(let a=0;a!==t;++a)n[a]=s.allocateTextureUnit();return n}function AC(s,t){const n=this.cache;n[0]!==t&&(s.uniform1f(this.addr,t),n[0]=t)}function CC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(s.uniform2f(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;s.uniform2fv(this.addr,t),Mn(n,t)}}function RC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(s.uniform3f(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else if(t.r!==void 0)(n[0]!==t.r||n[1]!==t.g||n[2]!==t.b)&&(s.uniform3f(this.addr,t.r,t.g,t.b),n[0]=t.r,n[1]=t.g,n[2]=t.b);else{if(Sn(n,t))return;s.uniform3fv(this.addr,t),Mn(n,t)}}function wC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(s.uniform4f(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;s.uniform4fv(this.addr,t),Mn(n,t)}}function DC(s,t){const n=this.cache,a=t.elements;if(a===void 0){if(Sn(n,t))return;s.uniformMatrix2fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,a))return;yy.set(a),s.uniformMatrix2fv(this.addr,!1,yy),Mn(n,a)}}function UC(s,t){const n=this.cache,a=t.elements;if(a===void 0){if(Sn(n,t))return;s.uniformMatrix3fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,a))return;_y.set(a),s.uniformMatrix3fv(this.addr,!1,_y),Mn(n,a)}}function NC(s,t){const n=this.cache,a=t.elements;if(a===void 0){if(Sn(n,t))return;s.uniformMatrix4fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,a))return;vy.set(a),s.uniformMatrix4fv(this.addr,!1,vy),Mn(n,a)}}function LC(s,t){const n=this.cache;n[0]!==t&&(s.uniform1i(this.addr,t),n[0]=t)}function OC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(s.uniform2i(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;s.uniform2iv(this.addr,t),Mn(n,t)}}function PC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(s.uniform3i(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;s.uniform3iv(this.addr,t),Mn(n,t)}}function zC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(s.uniform4i(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;s.uniform4iv(this.addr,t),Mn(n,t)}}function IC(s,t){const n=this.cache;n[0]!==t&&(s.uniform1ui(this.addr,t),n[0]=t)}function BC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(s.uniform2ui(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;s.uniform2uiv(this.addr,t),Mn(n,t)}}function FC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(s.uniform3ui(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;s.uniform3uiv(this.addr,t),Mn(n,t)}}function HC(s,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(s.uniform4ui(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;s.uniform4uiv(this.addr,t),Mn(n,t)}}function GC(s,t,n){const a=this.cache,l=n.allocateTextureUnit();a[0]!==l&&(s.uniform1i(this.addr,l),a[0]=l);let c;this.type===s.SAMPLER_2D_SHADOW?(py.compareFunction=Ax,c=py):c=jx,n.setTexture2D(t||c,l)}function VC(s,t,n){const a=this.cache,l=n.allocateTextureUnit();a[0]!==l&&(s.uniform1i(this.addr,l),a[0]=l),n.setTexture3D(t||Wx,l)}function kC(s,t,n){const a=this.cache,l=n.allocateTextureUnit();a[0]!==l&&(s.uniform1i(this.addr,l),a[0]=l),n.setTextureCube(t||Yx,l)}function XC(s,t,n){const a=this.cache,l=n.allocateTextureUnit();a[0]!==l&&(s.uniform1i(this.addr,l),a[0]=l),n.setTexture2DArray(t||qx,l)}function jC(s){switch(s){case 5126:return AC;case 35664:return CC;case 35665:return RC;case 35666:return wC;case 35674:return DC;case 35675:return UC;case 35676:return NC;case 5124:case 35670:return LC;case 35667:case 35671:return OC;case 35668:case 35672:return PC;case 35669:case 35673:return zC;case 5125:return IC;case 36294:return BC;case 36295:return FC;case 36296:return HC;case 35678:case 36198:case 36298:case 36306:case 35682:return GC;case 35679:case 36299:case 36307:return VC;case 35680:case 36300:case 36308:case 36293:return kC;case 36289:case 36303:case 36311:case 36292:return XC}}function qC(s,t){s.uniform1fv(this.addr,t)}function WC(s,t){const n=Xo(t,this.size,2);s.uniform2fv(this.addr,n)}function YC(s,t){const n=Xo(t,this.size,3);s.uniform3fv(this.addr,n)}function QC(s,t){const n=Xo(t,this.size,4);s.uniform4fv(this.addr,n)}function ZC(s,t){const n=Xo(t,this.size,4);s.uniformMatrix2fv(this.addr,!1,n)}function KC(s,t){const n=Xo(t,this.size,9);s.uniformMatrix3fv(this.addr,!1,n)}function JC(s,t){const n=Xo(t,this.size,16);s.uniformMatrix4fv(this.addr,!1,n)}function $C(s,t){s.uniform1iv(this.addr,t)}function tR(s,t){s.uniform2iv(this.addr,t)}function eR(s,t){s.uniform3iv(this.addr,t)}function nR(s,t){s.uniform4iv(this.addr,t)}function iR(s,t){s.uniform1uiv(this.addr,t)}function aR(s,t){s.uniform2uiv(this.addr,t)}function sR(s,t){s.uniform3uiv(this.addr,t)}function rR(s,t){s.uniform4uiv(this.addr,t)}function oR(s,t,n){const a=this.cache,l=t.length,c=hf(n,l);Sn(a,c)||(s.uniform1iv(this.addr,c),Mn(a,c));for(let f=0;f!==l;++f)n.setTexture2D(t[f]||jx,c[f])}function lR(s,t,n){const a=this.cache,l=t.length,c=hf(n,l);Sn(a,c)||(s.uniform1iv(this.addr,c),Mn(a,c));for(let f=0;f!==l;++f)n.setTexture3D(t[f]||Wx,c[f])}function cR(s,t,n){const a=this.cache,l=t.length,c=hf(n,l);Sn(a,c)||(s.uniform1iv(this.addr,c),Mn(a,c));for(let f=0;f!==l;++f)n.setTextureCube(t[f]||Yx,c[f])}function uR(s,t,n){const a=this.cache,l=t.length,c=hf(n,l);Sn(a,c)||(s.uniform1iv(this.addr,c),Mn(a,c));for(let f=0;f!==l;++f)n.setTexture2DArray(t[f]||qx,c[f])}function fR(s){switch(s){case 5126:return qC;case 35664:return WC;case 35665:return YC;case 35666:return QC;case 35674:return ZC;case 35675:return KC;case 35676:return JC;case 5124:case 35670:return $C;case 35667:case 35671:return tR;case 35668:case 35672:return eR;case 35669:case 35673:return nR;case 5125:return iR;case 36294:return aR;case 36295:return sR;case 36296:return rR;case 35678:case 36198:case 36298:case 36306:case 35682:return oR;case 35679:case 36299:case 36307:return lR;case 35680:case 36300:case 36308:case 36293:return cR;case 36289:case 36303:case 36311:case 36292:return uR}}class hR{constructor(t,n,a){this.id=t,this.addr=a,this.cache=[],this.type=n.type,this.setValue=jC(n.type)}}class dR{constructor(t,n,a){this.id=t,this.addr=a,this.cache=[],this.type=n.type,this.size=n.size,this.setValue=fR(n.type)}}class pR{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,n,a){const l=this.seq;for(let c=0,f=l.length;c!==f;++c){const d=l[c];d.setValue(t,n[d.id],a)}}}const ip=/(\w+)(\])?(\[|\.)?/g;function xy(s,t){s.seq.push(t),s.map[t.id]=t}function mR(s,t,n){const a=s.name,l=a.length;for(ip.lastIndex=0;;){const c=ip.exec(a),f=ip.lastIndex;let d=c[1];const p=c[2]==="]",m=c[3];if(p&&(d=d|0),m===void 0||m==="["&&f+2===l){xy(n,m===void 0?new hR(d,s,t):new dR(d,s,t));break}else{let v=n.map[d];v===void 0&&(v=new pR(d),xy(n,v)),n=v}}}class $u{constructor(t,n){this.seq=[],this.map={};const a=t.getProgramParameter(n,t.ACTIVE_UNIFORMS);for(let l=0;l<a;++l){const c=t.getActiveUniform(n,l),f=t.getUniformLocation(n,c.name);mR(c,f,this)}}setValue(t,n,a,l){const c=this.map[n];c!==void 0&&c.setValue(t,a,l)}setOptional(t,n,a){const l=n[a];l!==void 0&&this.setValue(t,a,l)}static upload(t,n,a,l){for(let c=0,f=n.length;c!==f;++c){const d=n[c],p=a[d.id];p.needsUpdate!==!1&&d.setValue(t,p.value,l)}}static seqWithValue(t,n){const a=[];for(let l=0,c=t.length;l!==c;++l){const f=t[l];f.id in n&&a.push(f)}return a}}function Sy(s,t,n){const a=s.createShader(t);return s.shaderSource(a,n),s.compileShader(a),a}const gR=37297;let vR=0;function _R(s,t){const n=s.split(`
`),a=[],l=Math.max(t-6,0),c=Math.min(t+6,n.length);for(let f=l;f<c;f++){const d=f+1;a.push(`${d===t?">":" "} ${d}: ${n[f]}`)}return a.join(`
`)}const My=new fe;function yR(s){Oe._getMatrix(My,Oe.workingColorSpace,s);const t=`mat3( ${My.elements.map(n=>n.toFixed(4))} )`;switch(Oe.getTransfer(s)){case ef:return[t,"LinearTransferOETF"];case je:return[t,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",s),[t,"LinearTransferOETF"]}}function Ey(s,t,n){const a=s.getShaderParameter(t,s.COMPILE_STATUS),l=s.getShaderInfoLog(t).trim();if(a&&l==="")return"";const c=/ERROR: 0:(\d+)/.exec(l);if(c){const f=parseInt(c[1]);return n.toUpperCase()+`

`+l+`

`+_R(s.getShaderSource(t),f)}else return l}function xR(s,t){const n=yR(t);return[`vec4 ${s}( vec4 value ) {`,`	return ${n[1]}( vec4( value.rgb * ${n[0]}, value.a ) );`,"}"].join(`
`)}function SR(s,t){let n;switch(t){case K1:n="Linear";break;case J1:n="Reinhard";break;case $1:n="Cineon";break;case tb:n="ACESFilmic";break;case nb:n="AgX";break;case ib:n="Neutral";break;case eb:n="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",t),n="Linear"}return"vec3 "+s+"( vec3 color ) { return "+n+"ToneMapping( color ); }"}const ju=new W;function MR(){Oe.getLuminanceCoefficients(ju);const s=ju.x.toFixed(4),t=ju.y.toFixed(4),n=ju.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${s}, ${t}, ${n} );`,"	return dot( weights, rgb );","}"].join(`
`)}function ER(s){return[s.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",s.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(jl).join(`
`)}function bR(s){const t=[];for(const n in s){const a=s[n];a!==!1&&t.push("#define "+n+" "+a)}return t.join(`
`)}function TR(s,t){const n={},a=s.getProgramParameter(t,s.ACTIVE_ATTRIBUTES);for(let l=0;l<a;l++){const c=s.getActiveAttrib(t,l),f=c.name;let d=1;c.type===s.FLOAT_MAT2&&(d=2),c.type===s.FLOAT_MAT3&&(d=3),c.type===s.FLOAT_MAT4&&(d=4),n[f]={type:c.type,location:s.getAttribLocation(t,f),locationSize:d}}return n}function jl(s){return s!==""}function by(s,t){const n=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return s.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,n).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function Ty(s,t){return s.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const AR=/^[ \t]*#include +<([\w\d./]+)>/gm;function rm(s){return s.replace(AR,RR)}const CR=new Map;function RR(s,t){let n=he[t];if(n===void 0){const a=CR.get(t);if(a!==void 0)n=he[a],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,a);else throw new Error("Can not resolve #include <"+t+">")}return rm(n)}const wR=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Ay(s){return s.replace(wR,DR)}function DR(s,t,n,a){let l="";for(let c=parseInt(t);c<parseInt(n);c++)l+=a.replace(/\[\s*i\s*\]/g,"[ "+c+" ]").replace(/UNROLLED_LOOP_INDEX/g,c);return l}function Cy(s){let t=`precision ${s.precision} float;
	precision ${s.precision} int;
	precision ${s.precision} sampler2D;
	precision ${s.precision} samplerCube;
	precision ${s.precision} sampler3D;
	precision ${s.precision} sampler2DArray;
	precision ${s.precision} sampler2DShadow;
	precision ${s.precision} samplerCubeShadow;
	precision ${s.precision} sampler2DArrayShadow;
	precision ${s.precision} isampler2D;
	precision ${s.precision} isampler3D;
	precision ${s.precision} isamplerCube;
	precision ${s.precision} isampler2DArray;
	precision ${s.precision} usampler2D;
	precision ${s.precision} usampler3D;
	precision ${s.precision} usamplerCube;
	precision ${s.precision} usampler2DArray;
	`;return s.precision==="highp"?t+=`
#define HIGH_PRECISION`:s.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:s.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}function UR(s){let t="SHADOWMAP_TYPE_BASIC";return s.shadowMapType===dx?t="SHADOWMAP_TYPE_PCF":s.shadowMapType===D1?t="SHADOWMAP_TYPE_PCF_SOFT":s.shadowMapType===Aa&&(t="SHADOWMAP_TYPE_VSM"),t}function NR(s){let t="ENVMAP_TYPE_CUBE";if(s.envMap)switch(s.envMapMode){case Po:case zo:t="ENVMAP_TYPE_CUBE";break;case lf:t="ENVMAP_TYPE_CUBE_UV";break}return t}function LR(s){let t="ENVMAP_MODE_REFLECTION";if(s.envMap)switch(s.envMapMode){case zo:t="ENVMAP_MODE_REFRACTION";break}return t}function OR(s){let t="ENVMAP_BLENDING_NONE";if(s.envMap)switch(s.combine){case px:t="ENVMAP_BLENDING_MULTIPLY";break;case Q1:t="ENVMAP_BLENDING_MIX";break;case Z1:t="ENVMAP_BLENDING_ADD";break}return t}function PR(s){const t=s.envMapCubeUVHeight;if(t===null)return null;const n=Math.log2(t)-2,a=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,n),112)),texelHeight:a,maxMip:n}}function zR(s,t,n,a){const l=s.getContext(),c=n.defines;let f=n.vertexShader,d=n.fragmentShader;const p=UR(n),m=NR(n),g=LR(n),v=OR(n),y=PR(n),x=ER(n),E=bR(c),b=l.createProgram();let M,_,I=n.glslVersion?"#version "+n.glslVersion+`
`:"";n.isRawShaderMaterial?(M=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,E].filter(jl).join(`
`),M.length>0&&(M+=`
`),_=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,E].filter(jl).join(`
`),_.length>0&&(_+=`
`)):(M=[Cy(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,E,n.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",n.batching?"#define USE_BATCHING":"",n.batchingColor?"#define USE_BATCHING_COLOR":"",n.instancing?"#define USE_INSTANCING":"",n.instancingColor?"#define USE_INSTANCING_COLOR":"",n.instancingMorph?"#define USE_INSTANCING_MORPH":"",n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.map?"#define USE_MAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+g:"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.displacementMap?"#define USE_DISPLACEMENTMAP":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.mapUv?"#define MAP_UV "+n.mapUv:"",n.alphaMapUv?"#define ALPHAMAP_UV "+n.alphaMapUv:"",n.lightMapUv?"#define LIGHTMAP_UV "+n.lightMapUv:"",n.aoMapUv?"#define AOMAP_UV "+n.aoMapUv:"",n.emissiveMapUv?"#define EMISSIVEMAP_UV "+n.emissiveMapUv:"",n.bumpMapUv?"#define BUMPMAP_UV "+n.bumpMapUv:"",n.normalMapUv?"#define NORMALMAP_UV "+n.normalMapUv:"",n.displacementMapUv?"#define DISPLACEMENTMAP_UV "+n.displacementMapUv:"",n.metalnessMapUv?"#define METALNESSMAP_UV "+n.metalnessMapUv:"",n.roughnessMapUv?"#define ROUGHNESSMAP_UV "+n.roughnessMapUv:"",n.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+n.anisotropyMapUv:"",n.clearcoatMapUv?"#define CLEARCOATMAP_UV "+n.clearcoatMapUv:"",n.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+n.clearcoatNormalMapUv:"",n.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+n.clearcoatRoughnessMapUv:"",n.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+n.iridescenceMapUv:"",n.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+n.iridescenceThicknessMapUv:"",n.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+n.sheenColorMapUv:"",n.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+n.sheenRoughnessMapUv:"",n.specularMapUv?"#define SPECULARMAP_UV "+n.specularMapUv:"",n.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+n.specularColorMapUv:"",n.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+n.specularIntensityMapUv:"",n.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+n.transmissionMapUv:"",n.thicknessMapUv?"#define THICKNESSMAP_UV "+n.thicknessMapUv:"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.flatShading?"#define FLAT_SHADED":"",n.skinning?"#define USE_SKINNING":"",n.morphTargets?"#define USE_MORPHTARGETS":"",n.morphNormals&&n.flatShading===!1?"#define USE_MORPHNORMALS":"",n.morphColors?"#define USE_MORPHCOLORS":"",n.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+n.morphTextureStride:"",n.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+n.morphTargetsCount:"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.sizeAttenuation?"#define USE_SIZEATTENUATION":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(jl).join(`
`),_=[Cy(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,E,n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",n.map?"#define USE_MAP":"",n.matcap?"#define USE_MATCAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+m:"",n.envMap?"#define "+g:"",n.envMap?"#define "+v:"",y?"#define CUBEUV_TEXEL_WIDTH "+y.texelWidth:"",y?"#define CUBEUV_TEXEL_HEIGHT "+y.texelHeight:"",y?"#define CUBEUV_MAX_MIP "+y.maxMip+".0":"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoat?"#define USE_CLEARCOAT":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.dispersion?"#define USE_DISPERSION":"",n.iridescence?"#define USE_IRIDESCENCE":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaTest?"#define USE_ALPHATEST":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.sheen?"#define USE_SHEEN":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors||n.instancingColor||n.batchingColor?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.gradientMap?"#define USE_GRADIENTMAP":"",n.flatShading?"#define FLAT_SHADED":"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",n.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",n.toneMapping!==Ts?"#define TONE_MAPPING":"",n.toneMapping!==Ts?he.tonemapping_pars_fragment:"",n.toneMapping!==Ts?SR("toneMapping",n.toneMapping):"",n.dithering?"#define DITHERING":"",n.opaque?"#define OPAQUE":"",he.colorspace_pars_fragment,xR("linearToOutputTexel",n.outputColorSpace),MR(),n.useDepthPacking?"#define DEPTH_PACKING "+n.depthPacking:"",`
`].filter(jl).join(`
`)),f=rm(f),f=by(f,n),f=Ty(f,n),d=rm(d),d=by(d,n),d=Ty(d,n),f=Ay(f),d=Ay(d),n.isRawShaderMaterial!==!0&&(I=`#version 300 es
`,M=[x,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+M,_=["#define varying in",n.glslVersion===z_?"":"layout(location = 0) out highp vec4 pc_fragColor;",n.glslVersion===z_?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const N=I+M+f,C=I+_+d,V=Sy(l,l.VERTEX_SHADER,N),F=Sy(l,l.FRAGMENT_SHADER,C);l.attachShader(b,V),l.attachShader(b,F),n.index0AttributeName!==void 0?l.bindAttribLocation(b,0,n.index0AttributeName):n.morphTargets===!0&&l.bindAttribLocation(b,0,"position"),l.linkProgram(b);function P(H){if(s.debug.checkShaderErrors){const ut=l.getProgramInfoLog(b).trim(),ot=l.getShaderInfoLog(V).trim(),mt=l.getShaderInfoLog(F).trim();let ct=!0,z=!0;if(l.getProgramParameter(b,l.LINK_STATUS)===!1)if(ct=!1,typeof s.debug.onShaderError=="function")s.debug.onShaderError(l,b,V,F);else{const Z=Ey(l,V,"vertex"),$=Ey(l,F,"fragment");console.error("THREE.WebGLProgram: Shader Error "+l.getError()+" - VALIDATE_STATUS "+l.getProgramParameter(b,l.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ut+`
`+Z+`
`+$)}else ut!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ut):(ot===""||mt==="")&&(z=!1);z&&(H.diagnostics={runnable:ct,programLog:ut,vertexShader:{log:ot,prefix:M},fragmentShader:{log:mt,prefix:_}})}l.deleteShader(V),l.deleteShader(F),G=new $u(l,b),U=TR(l,b)}let G;this.getUniforms=function(){return G===void 0&&P(this),G};let U;this.getAttributes=function(){return U===void 0&&P(this),U};let w=n.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return w===!1&&(w=l.getProgramParameter(b,gR)),w},this.destroy=function(){a.releaseStatesOfProgram(this),l.deleteProgram(b),this.program=void 0},this.type=n.shaderType,this.name=n.shaderName,this.id=vR++,this.cacheKey=t,this.usedTimes=1,this.program=b,this.vertexShader=V,this.fragmentShader=F,this}let IR=0;class BR{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const n=t.vertexShader,a=t.fragmentShader,l=this._getShaderStage(n),c=this._getShaderStage(a),f=this._getShaderCacheForMaterial(t);return f.has(l)===!1&&(f.add(l),l.usedTimes++),f.has(c)===!1&&(f.add(c),c.usedTimes++),this}remove(t){const n=this.materialCache.get(t);for(const a of n)a.usedTimes--,a.usedTimes===0&&this.shaderCache.delete(a.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const n=this.materialCache;let a=n.get(t);return a===void 0&&(a=new Set,n.set(t,a)),a}_getShaderStage(t){const n=this.shaderCache;let a=n.get(t);return a===void 0&&(a=new FR(t),n.set(t,a)),a}}class FR{constructor(t){this.id=IR++,this.code=t,this.usedTimes=0}}function HR(s,t,n,a,l,c,f){const d=new Dx,p=new BR,m=new Set,g=[],v=l.logarithmicDepthBuffer,y=l.vertexTextures;let x=l.precision;const E={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function b(U){return m.add(U),U===0?"uv":`uv${U}`}function M(U,w,H,ut,ot){const mt=ut.fog,ct=ot.geometry,z=U.isMeshStandardMaterial?ut.environment:null,Z=(U.isMeshStandardMaterial?n:t).get(U.envMap||z),$=Z&&Z.mapping===lf?Z.image.height:null,Et=E[U.type];U.precision!==null&&(x=l.getMaxPrecision(U.precision),x!==U.precision&&console.warn("THREE.WebGLProgram.getParameters:",U.precision,"not supported, using",x,"instead."));const At=ct.morphAttributes.position||ct.morphAttributes.normal||ct.morphAttributes.color,O=At!==void 0?At.length:0;let nt=0;ct.morphAttributes.position!==void 0&&(nt=1),ct.morphAttributes.normal!==void 0&&(nt=2),ct.morphAttributes.color!==void 0&&(nt=3);let St,q,ft,Tt;if(Et){const we=Ji[Et];St=we.vertexShader,q=we.fragmentShader}else St=U.vertexShader,q=U.fragmentShader,p.update(U),ft=p.getVertexShaderID(U),Tt=p.getFragmentShaderID(U);const Mt=s.getRenderTarget(),Ft=s.state.buffers.depth.getReversed(),Vt=ot.isInstancedMesh===!0,re=ot.isBatchedMesh===!0,He=!!U.map,ve=!!U.matcap,Je=!!Z,k=!!U.aoMap,Pn=!!U.lightMap,me=!!U.bumpMap,Se=!!U.normalMap,Qt=!!U.displacementMap,Ie=!!U.emissiveMap,Yt=!!U.metalnessMap,L=!!U.roughnessMap,A=U.anisotropy>0,at=U.clearcoat>0,pt=U.dispersion>0,bt=U.iridescence>0,vt=U.sheen>0,jt=U.transmission>0,Dt=A&&!!U.anisotropyMap,Bt=at&&!!U.clearcoatMap,Me=at&&!!U.clearcoatNormalMap,Ct=at&&!!U.clearcoatRoughnessMap,Ht=bt&&!!U.iridescenceMap,Zt=bt&&!!U.iridescenceThicknessMap,qt=vt&&!!U.sheenColorMap,Ot=vt&&!!U.sheenRoughnessMap,ne=!!U.specularMap,oe=!!U.specularColorMap,Ge=!!U.specularIntensityMap,Y=jt&&!!U.transmissionMap,Rt=jt&&!!U.thicknessMap,ht=!!U.gradientMap,yt=!!U.alphaMap,wt=U.alphaTest>0,Ut=!!U.alphaHash,ie=!!U.extensions;let $e=Ts;U.toneMapped&&(Mt===null||Mt.isXRRenderTarget===!0)&&($e=s.toneMapping);const _n={shaderID:Et,shaderType:U.type,shaderName:U.name,vertexShader:St,fragmentShader:q,defines:U.defines,customVertexShaderID:ft,customFragmentShaderID:Tt,isRawShaderMaterial:U.isRawShaderMaterial===!0,glslVersion:U.glslVersion,precision:x,batching:re,batchingColor:re&&ot._colorsTexture!==null,instancing:Vt,instancingColor:Vt&&ot.instanceColor!==null,instancingMorph:Vt&&ot.morphTexture!==null,supportsVertexTextures:y,outputColorSpace:Mt===null?s.outputColorSpace:Mt.isXRRenderTarget===!0?Mt.texture.colorSpace:Fo,alphaToCoverage:!!U.alphaToCoverage,map:He,matcap:ve,envMap:Je,envMapMode:Je&&Z.mapping,envMapCubeUVHeight:$,aoMap:k,lightMap:Pn,bumpMap:me,normalMap:Se,displacementMap:y&&Qt,emissiveMap:Ie,normalMapObjectSpace:Se&&U.normalMapType===lb,normalMapTangentSpace:Se&&U.normalMapType===ob,metalnessMap:Yt,roughnessMap:L,anisotropy:A,anisotropyMap:Dt,clearcoat:at,clearcoatMap:Bt,clearcoatNormalMap:Me,clearcoatRoughnessMap:Ct,dispersion:pt,iridescence:bt,iridescenceMap:Ht,iridescenceThicknessMap:Zt,sheen:vt,sheenColorMap:qt,sheenRoughnessMap:Ot,specularMap:ne,specularColorMap:oe,specularIntensityMap:Ge,transmission:jt,transmissionMap:Y,thicknessMap:Rt,gradientMap:ht,opaque:U.transparent===!1&&U.blending===vo&&U.alphaToCoverage===!1,alphaMap:yt,alphaTest:wt,alphaHash:Ut,combine:U.combine,mapUv:He&&b(U.map.channel),aoMapUv:k&&b(U.aoMap.channel),lightMapUv:Pn&&b(U.lightMap.channel),bumpMapUv:me&&b(U.bumpMap.channel),normalMapUv:Se&&b(U.normalMap.channel),displacementMapUv:Qt&&b(U.displacementMap.channel),emissiveMapUv:Ie&&b(U.emissiveMap.channel),metalnessMapUv:Yt&&b(U.metalnessMap.channel),roughnessMapUv:L&&b(U.roughnessMap.channel),anisotropyMapUv:Dt&&b(U.anisotropyMap.channel),clearcoatMapUv:Bt&&b(U.clearcoatMap.channel),clearcoatNormalMapUv:Me&&b(U.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Ct&&b(U.clearcoatRoughnessMap.channel),iridescenceMapUv:Ht&&b(U.iridescenceMap.channel),iridescenceThicknessMapUv:Zt&&b(U.iridescenceThicknessMap.channel),sheenColorMapUv:qt&&b(U.sheenColorMap.channel),sheenRoughnessMapUv:Ot&&b(U.sheenRoughnessMap.channel),specularMapUv:ne&&b(U.specularMap.channel),specularColorMapUv:oe&&b(U.specularColorMap.channel),specularIntensityMapUv:Ge&&b(U.specularIntensityMap.channel),transmissionMapUv:Y&&b(U.transmissionMap.channel),thicknessMapUv:Rt&&b(U.thicknessMap.channel),alphaMapUv:yt&&b(U.alphaMap.channel),vertexTangents:!!ct.attributes.tangent&&(Se||A),vertexColors:U.vertexColors,vertexAlphas:U.vertexColors===!0&&!!ct.attributes.color&&ct.attributes.color.itemSize===4,pointsUvs:ot.isPoints===!0&&!!ct.attributes.uv&&(He||yt),fog:!!mt,useFog:U.fog===!0,fogExp2:!!mt&&mt.isFogExp2,flatShading:U.flatShading===!0,sizeAttenuation:U.sizeAttenuation===!0,logarithmicDepthBuffer:v,reverseDepthBuffer:Ft,skinning:ot.isSkinnedMesh===!0,morphTargets:ct.morphAttributes.position!==void 0,morphNormals:ct.morphAttributes.normal!==void 0,morphColors:ct.morphAttributes.color!==void 0,morphTargetsCount:O,morphTextureStride:nt,numDirLights:w.directional.length,numPointLights:w.point.length,numSpotLights:w.spot.length,numSpotLightMaps:w.spotLightMap.length,numRectAreaLights:w.rectArea.length,numHemiLights:w.hemi.length,numDirLightShadows:w.directionalShadowMap.length,numPointLightShadows:w.pointShadowMap.length,numSpotLightShadows:w.spotShadowMap.length,numSpotLightShadowsWithMaps:w.numSpotLightShadowsWithMaps,numLightProbes:w.numLightProbes,numClippingPlanes:f.numPlanes,numClipIntersection:f.numIntersection,dithering:U.dithering,shadowMapEnabled:s.shadowMap.enabled&&H.length>0,shadowMapType:s.shadowMap.type,toneMapping:$e,decodeVideoTexture:He&&U.map.isVideoTexture===!0&&Oe.getTransfer(U.map.colorSpace)===je,decodeVideoTextureEmissive:Ie&&U.emissiveMap.isVideoTexture===!0&&Oe.getTransfer(U.emissiveMap.colorSpace)===je,premultipliedAlpha:U.premultipliedAlpha,doubleSided:U.side===wa,flipSided:U.side===ii,useDepthPacking:U.depthPacking>=0,depthPacking:U.depthPacking||0,index0AttributeName:U.index0AttributeName,extensionClipCullDistance:ie&&U.extensions.clipCullDistance===!0&&a.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ie&&U.extensions.multiDraw===!0||re)&&a.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:a.has("KHR_parallel_shader_compile"),customProgramCacheKey:U.customProgramCacheKey()};return _n.vertexUv1s=m.has(1),_n.vertexUv2s=m.has(2),_n.vertexUv3s=m.has(3),m.clear(),_n}function _(U){const w=[];if(U.shaderID?w.push(U.shaderID):(w.push(U.customVertexShaderID),w.push(U.customFragmentShaderID)),U.defines!==void 0)for(const H in U.defines)w.push(H),w.push(U.defines[H]);return U.isRawShaderMaterial===!1&&(I(w,U),N(w,U),w.push(s.outputColorSpace)),w.push(U.customProgramCacheKey),w.join()}function I(U,w){U.push(w.precision),U.push(w.outputColorSpace),U.push(w.envMapMode),U.push(w.envMapCubeUVHeight),U.push(w.mapUv),U.push(w.alphaMapUv),U.push(w.lightMapUv),U.push(w.aoMapUv),U.push(w.bumpMapUv),U.push(w.normalMapUv),U.push(w.displacementMapUv),U.push(w.emissiveMapUv),U.push(w.metalnessMapUv),U.push(w.roughnessMapUv),U.push(w.anisotropyMapUv),U.push(w.clearcoatMapUv),U.push(w.clearcoatNormalMapUv),U.push(w.clearcoatRoughnessMapUv),U.push(w.iridescenceMapUv),U.push(w.iridescenceThicknessMapUv),U.push(w.sheenColorMapUv),U.push(w.sheenRoughnessMapUv),U.push(w.specularMapUv),U.push(w.specularColorMapUv),U.push(w.specularIntensityMapUv),U.push(w.transmissionMapUv),U.push(w.thicknessMapUv),U.push(w.combine),U.push(w.fogExp2),U.push(w.sizeAttenuation),U.push(w.morphTargetsCount),U.push(w.morphAttributeCount),U.push(w.numDirLights),U.push(w.numPointLights),U.push(w.numSpotLights),U.push(w.numSpotLightMaps),U.push(w.numHemiLights),U.push(w.numRectAreaLights),U.push(w.numDirLightShadows),U.push(w.numPointLightShadows),U.push(w.numSpotLightShadows),U.push(w.numSpotLightShadowsWithMaps),U.push(w.numLightProbes),U.push(w.shadowMapType),U.push(w.toneMapping),U.push(w.numClippingPlanes),U.push(w.numClipIntersection),U.push(w.depthPacking)}function N(U,w){d.disableAll(),w.supportsVertexTextures&&d.enable(0),w.instancing&&d.enable(1),w.instancingColor&&d.enable(2),w.instancingMorph&&d.enable(3),w.matcap&&d.enable(4),w.envMap&&d.enable(5),w.normalMapObjectSpace&&d.enable(6),w.normalMapTangentSpace&&d.enable(7),w.clearcoat&&d.enable(8),w.iridescence&&d.enable(9),w.alphaTest&&d.enable(10),w.vertexColors&&d.enable(11),w.vertexAlphas&&d.enable(12),w.vertexUv1s&&d.enable(13),w.vertexUv2s&&d.enable(14),w.vertexUv3s&&d.enable(15),w.vertexTangents&&d.enable(16),w.anisotropy&&d.enable(17),w.alphaHash&&d.enable(18),w.batching&&d.enable(19),w.dispersion&&d.enable(20),w.batchingColor&&d.enable(21),U.push(d.mask),d.disableAll(),w.fog&&d.enable(0),w.useFog&&d.enable(1),w.flatShading&&d.enable(2),w.logarithmicDepthBuffer&&d.enable(3),w.reverseDepthBuffer&&d.enable(4),w.skinning&&d.enable(5),w.morphTargets&&d.enable(6),w.morphNormals&&d.enable(7),w.morphColors&&d.enable(8),w.premultipliedAlpha&&d.enable(9),w.shadowMapEnabled&&d.enable(10),w.doubleSided&&d.enable(11),w.flipSided&&d.enable(12),w.useDepthPacking&&d.enable(13),w.dithering&&d.enable(14),w.transmission&&d.enable(15),w.sheen&&d.enable(16),w.opaque&&d.enable(17),w.pointsUvs&&d.enable(18),w.decodeVideoTexture&&d.enable(19),w.decodeVideoTextureEmissive&&d.enable(20),w.alphaToCoverage&&d.enable(21),U.push(d.mask)}function C(U){const w=E[U.type];let H;if(w){const ut=Ji[w];H=sf.clone(ut.uniforms)}else H=U.uniforms;return H}function V(U,w){let H;for(let ut=0,ot=g.length;ut<ot;ut++){const mt=g[ut];if(mt.cacheKey===w){H=mt,++H.usedTimes;break}}return H===void 0&&(H=new zR(s,w,U,c),g.push(H)),H}function F(U){if(--U.usedTimes===0){const w=g.indexOf(U);g[w]=g[g.length-1],g.pop(),U.destroy()}}function P(U){p.remove(U)}function G(){p.dispose()}return{getParameters:M,getProgramCacheKey:_,getUniforms:C,acquireProgram:V,releaseProgram:F,releaseShaderCache:P,programs:g,dispose:G}}function GR(){let s=new WeakMap;function t(f){return s.has(f)}function n(f){let d=s.get(f);return d===void 0&&(d={},s.set(f,d)),d}function a(f){s.delete(f)}function l(f,d,p){s.get(f)[d]=p}function c(){s=new WeakMap}return{has:t,get:n,remove:a,update:l,dispose:c}}function VR(s,t){return s.groupOrder!==t.groupOrder?s.groupOrder-t.groupOrder:s.renderOrder!==t.renderOrder?s.renderOrder-t.renderOrder:s.material.id!==t.material.id?s.material.id-t.material.id:s.z!==t.z?s.z-t.z:s.id-t.id}function Ry(s,t){return s.groupOrder!==t.groupOrder?s.groupOrder-t.groupOrder:s.renderOrder!==t.renderOrder?s.renderOrder-t.renderOrder:s.z!==t.z?t.z-s.z:s.id-t.id}function wy(){const s=[];let t=0;const n=[],a=[],l=[];function c(){t=0,n.length=0,a.length=0,l.length=0}function f(v,y,x,E,b,M){let _=s[t];return _===void 0?(_={id:v.id,object:v,geometry:y,material:x,groupOrder:E,renderOrder:v.renderOrder,z:b,group:M},s[t]=_):(_.id=v.id,_.object=v,_.geometry=y,_.material=x,_.groupOrder=E,_.renderOrder=v.renderOrder,_.z=b,_.group=M),t++,_}function d(v,y,x,E,b,M){const _=f(v,y,x,E,b,M);x.transmission>0?a.push(_):x.transparent===!0?l.push(_):n.push(_)}function p(v,y,x,E,b,M){const _=f(v,y,x,E,b,M);x.transmission>0?a.unshift(_):x.transparent===!0?l.unshift(_):n.unshift(_)}function m(v,y){n.length>1&&n.sort(v||VR),a.length>1&&a.sort(y||Ry),l.length>1&&l.sort(y||Ry)}function g(){for(let v=t,y=s.length;v<y;v++){const x=s[v];if(x.id===null)break;x.id=null,x.object=null,x.geometry=null,x.material=null,x.group=null}}return{opaque:n,transmissive:a,transparent:l,init:c,push:d,unshift:p,finish:g,sort:m}}function kR(){let s=new WeakMap;function t(a,l){const c=s.get(a);let f;return c===void 0?(f=new wy,s.set(a,[f])):l>=c.length?(f=new wy,c.push(f)):f=c[l],f}function n(){s=new WeakMap}return{get:t,dispose:n}}function XR(){const s={};return{get:function(t){if(s[t.id]!==void 0)return s[t.id];let n;switch(t.type){case"DirectionalLight":n={direction:new W,color:new de};break;case"SpotLight":n={position:new W,direction:new W,color:new de,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":n={position:new W,color:new de,distance:0,decay:0};break;case"HemisphereLight":n={direction:new W,skyColor:new de,groundColor:new de};break;case"RectAreaLight":n={color:new de,position:new W,halfWidth:new W,halfHeight:new W};break}return s[t.id]=n,n}}}function jR(){const s={};return{get:function(t){if(s[t.id]!==void 0)return s[t.id];let n;switch(t.type){case"DirectionalLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"SpotLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"PointLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt,shadowCameraNear:1,shadowCameraFar:1e3};break}return s[t.id]=n,n}}}let qR=0;function WR(s,t){return(t.castShadow?2:0)-(s.castShadow?2:0)+(t.map?1:0)-(s.map?1:0)}function YR(s){const t=new XR,n=jR(),a={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let m=0;m<9;m++)a.probe.push(new W);const l=new W,c=new nn,f=new nn;function d(m){let g=0,v=0,y=0;for(let U=0;U<9;U++)a.probe[U].set(0,0,0);let x=0,E=0,b=0,M=0,_=0,I=0,N=0,C=0,V=0,F=0,P=0;m.sort(WR);for(let U=0,w=m.length;U<w;U++){const H=m[U],ut=H.color,ot=H.intensity,mt=H.distance,ct=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)g+=ut.r*ot,v+=ut.g*ot,y+=ut.b*ot;else if(H.isLightProbe){for(let z=0;z<9;z++)a.probe[z].addScaledVector(H.sh.coefficients[z],ot);P++}else if(H.isDirectionalLight){const z=t.get(H);if(z.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,a.directionalShadow[x]=$,a.directionalShadowMap[x]=ct,a.directionalShadowMatrix[x]=H.shadow.matrix,I++}a.directional[x]=z,x++}else if(H.isSpotLight){const z=t.get(H);z.position.setFromMatrixPosition(H.matrixWorld),z.color.copy(ut).multiplyScalar(ot),z.distance=mt,z.coneCos=Math.cos(H.angle),z.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),z.decay=H.decay,a.spot[b]=z;const Z=H.shadow;if(H.map&&(a.spotLightMap[V]=H.map,V++,Z.updateMatrices(H),H.castShadow&&F++),a.spotLightMatrix[b]=Z.matrix,H.castShadow){const $=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,a.spotShadow[b]=$,a.spotShadowMap[b]=ct,C++}b++}else if(H.isRectAreaLight){const z=t.get(H);z.color.copy(ut).multiplyScalar(ot),z.halfWidth.set(H.width*.5,0,0),z.halfHeight.set(0,H.height*.5,0),a.rectArea[M]=z,M++}else if(H.isPointLight){const z=t.get(H);if(z.color.copy(H.color).multiplyScalar(H.intensity),z.distance=H.distance,z.decay=H.decay,H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,$.shadowCameraNear=Z.camera.near,$.shadowCameraFar=Z.camera.far,a.pointShadow[E]=$,a.pointShadowMap[E]=ct,a.pointShadowMatrix[E]=H.shadow.matrix,N++}a.point[E]=z,E++}else if(H.isHemisphereLight){const z=t.get(H);z.skyColor.copy(H.color).multiplyScalar(ot),z.groundColor.copy(H.groundColor).multiplyScalar(ot),a.hemi[_]=z,_++}}M>0&&(s.has("OES_texture_float_linear")===!0?(a.rectAreaLTC1=Lt.LTC_FLOAT_1,a.rectAreaLTC2=Lt.LTC_FLOAT_2):(a.rectAreaLTC1=Lt.LTC_HALF_1,a.rectAreaLTC2=Lt.LTC_HALF_2)),a.ambient[0]=g,a.ambient[1]=v,a.ambient[2]=y;const G=a.hash;(G.directionalLength!==x||G.pointLength!==E||G.spotLength!==b||G.rectAreaLength!==M||G.hemiLength!==_||G.numDirectionalShadows!==I||G.numPointShadows!==N||G.numSpotShadows!==C||G.numSpotMaps!==V||G.numLightProbes!==P)&&(a.directional.length=x,a.spot.length=b,a.rectArea.length=M,a.point.length=E,a.hemi.length=_,a.directionalShadow.length=I,a.directionalShadowMap.length=I,a.pointShadow.length=N,a.pointShadowMap.length=N,a.spotShadow.length=C,a.spotShadowMap.length=C,a.directionalShadowMatrix.length=I,a.pointShadowMatrix.length=N,a.spotLightMatrix.length=C+V-F,a.spotLightMap.length=V,a.numSpotLightShadowsWithMaps=F,a.numLightProbes=P,G.directionalLength=x,G.pointLength=E,G.spotLength=b,G.rectAreaLength=M,G.hemiLength=_,G.numDirectionalShadows=I,G.numPointShadows=N,G.numSpotShadows=C,G.numSpotMaps=V,G.numLightProbes=P,a.version=qR++)}function p(m,g){let v=0,y=0,x=0,E=0,b=0;const M=g.matrixWorldInverse;for(let _=0,I=m.length;_<I;_++){const N=m[_];if(N.isDirectionalLight){const C=a.directional[v];C.direction.setFromMatrixPosition(N.matrixWorld),l.setFromMatrixPosition(N.target.matrixWorld),C.direction.sub(l),C.direction.transformDirection(M),v++}else if(N.isSpotLight){const C=a.spot[x];C.position.setFromMatrixPosition(N.matrixWorld),C.position.applyMatrix4(M),C.direction.setFromMatrixPosition(N.matrixWorld),l.setFromMatrixPosition(N.target.matrixWorld),C.direction.sub(l),C.direction.transformDirection(M),x++}else if(N.isRectAreaLight){const C=a.rectArea[E];C.position.setFromMatrixPosition(N.matrixWorld),C.position.applyMatrix4(M),f.identity(),c.copy(N.matrixWorld),c.premultiply(M),f.extractRotation(c),C.halfWidth.set(N.width*.5,0,0),C.halfHeight.set(0,N.height*.5,0),C.halfWidth.applyMatrix4(f),C.halfHeight.applyMatrix4(f),E++}else if(N.isPointLight){const C=a.point[y];C.position.setFromMatrixPosition(N.matrixWorld),C.position.applyMatrix4(M),y++}else if(N.isHemisphereLight){const C=a.hemi[b];C.direction.setFromMatrixPosition(N.matrixWorld),C.direction.transformDirection(M),b++}}}return{setup:d,setupView:p,state:a}}function Dy(s){const t=new YR(s),n=[],a=[];function l(g){m.camera=g,n.length=0,a.length=0}function c(g){n.push(g)}function f(g){a.push(g)}function d(){t.setup(n)}function p(g){t.setupView(n,g)}const m={lightsArray:n,shadowsArray:a,camera:null,lights:t,transmissionRenderTarget:{}};return{init:l,state:m,setupLights:d,setupLightsView:p,pushLight:c,pushShadow:f}}function QR(s){let t=new WeakMap;function n(l,c=0){const f=t.get(l);let d;return f===void 0?(d=new Dy(s),t.set(l,[d])):c>=f.length?(d=new Dy(s),f.push(d)):d=f[c],d}function a(){t=new WeakMap}return{get:n,dispose:a}}const ZR=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,KR=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function JR(s,t,n){let a=new bm;const l=new Wt,c=new Wt,f=new qe,d=new MT({depthPacking:rb}),p=new ET,m={},g=n.maxTextureSize,v={[As]:ii,[ii]:As,[wa]:wa},y=new Yn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Wt},radius:{value:4}},vertexShader:ZR,fragmentShader:KR}),x=y.clone();x.defines.HORIZONTAL_PASS=1;const E=new Vi;E.setAttribute("position",new ta(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const b=new Wn(E,y),M=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=dx;let _=this.type;this.render=function(F,P,G){if(M.enabled===!1||M.autoUpdate===!1&&M.needsUpdate===!1||F.length===0)return;const U=s.getRenderTarget(),w=s.getActiveCubeFace(),H=s.getActiveMipmapLevel(),ut=s.state;ut.setBlending(Na),ut.buffers.color.setClear(1,1,1,1),ut.buffers.depth.setTest(!0),ut.setScissorTest(!1);const ot=_!==Aa&&this.type===Aa,mt=_===Aa&&this.type!==Aa;for(let ct=0,z=F.length;ct<z;ct++){const Z=F[ct],$=Z.shadow;if($===void 0){console.warn("THREE.WebGLShadowMap:",Z,"has no shadow.");continue}if($.autoUpdate===!1&&$.needsUpdate===!1)continue;l.copy($.mapSize);const Et=$.getFrameExtents();if(l.multiply(Et),c.copy($.mapSize),(l.x>g||l.y>g)&&(l.x>g&&(c.x=Math.floor(g/Et.x),l.x=c.x*Et.x,$.mapSize.x=c.x),l.y>g&&(c.y=Math.floor(g/Et.y),l.y=c.y*Et.y,$.mapSize.y=c.y)),$.map===null||ot===!0||mt===!0){const O=this.type!==Aa?{minFilter:Hi,magFilter:Hi}:{};$.map!==null&&$.map.dispose(),$.map=new Gi(l.x,l.y,O),$.map.texture.name=Z.name+".shadowMap",$.camera.updateProjectionMatrix()}s.setRenderTarget($.map),s.clear();const At=$.getViewportCount();for(let O=0;O<At;O++){const nt=$.getViewport(O);f.set(c.x*nt.x,c.y*nt.y,c.x*nt.z,c.y*nt.w),ut.viewport(f),$.updateMatrices(Z,O),a=$.getFrustum(),C(P,G,$.camera,Z,this.type)}$.isPointLightShadow!==!0&&this.type===Aa&&I($,G),$.needsUpdate=!1}_=this.type,M.needsUpdate=!1,s.setRenderTarget(U,w,H)};function I(F,P){const G=t.update(b);y.defines.VSM_SAMPLES!==F.blurSamples&&(y.defines.VSM_SAMPLES=F.blurSamples,x.defines.VSM_SAMPLES=F.blurSamples,y.needsUpdate=!0,x.needsUpdate=!0),F.mapPass===null&&(F.mapPass=new Gi(l.x,l.y)),y.uniforms.shadow_pass.value=F.map.texture,y.uniforms.resolution.value=F.mapSize,y.uniforms.radius.value=F.radius,s.setRenderTarget(F.mapPass),s.clear(),s.renderBufferDirect(P,null,G,y,b,null),x.uniforms.shadow_pass.value=F.mapPass.texture,x.uniforms.resolution.value=F.mapSize,x.uniforms.radius.value=F.radius,s.setRenderTarget(F.map),s.clear(),s.renderBufferDirect(P,null,G,x,b,null)}function N(F,P,G,U){let w=null;const H=G.isPointLight===!0?F.customDistanceMaterial:F.customDepthMaterial;if(H!==void 0)w=H;else if(w=G.isPointLight===!0?p:d,s.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const ut=w.uuid,ot=P.uuid;let mt=m[ut];mt===void 0&&(mt={},m[ut]=mt);let ct=mt[ot];ct===void 0&&(ct=w.clone(),mt[ot]=ct,P.addEventListener("dispose",V)),w=ct}if(w.visible=P.visible,w.wireframe=P.wireframe,U===Aa?w.side=P.shadowSide!==null?P.shadowSide:P.side:w.side=P.shadowSide!==null?P.shadowSide:v[P.side],w.alphaMap=P.alphaMap,w.alphaTest=P.alphaTest,w.map=P.map,w.clipShadows=P.clipShadows,w.clippingPlanes=P.clippingPlanes,w.clipIntersection=P.clipIntersection,w.displacementMap=P.displacementMap,w.displacementScale=P.displacementScale,w.displacementBias=P.displacementBias,w.wireframeLinewidth=P.wireframeLinewidth,w.linewidth=P.linewidth,G.isPointLight===!0&&w.isMeshDistanceMaterial===!0){const ut=s.properties.get(w);ut.light=G}return w}function C(F,P,G,U,w){if(F.visible===!1)return;if(F.layers.test(P.layers)&&(F.isMesh||F.isLine||F.isPoints)&&(F.castShadow||F.receiveShadow&&w===Aa)&&(!F.frustumCulled||a.intersectsObject(F))){F.modelViewMatrix.multiplyMatrices(G.matrixWorldInverse,F.matrixWorld);const ot=t.update(F),mt=F.material;if(Array.isArray(mt)){const ct=ot.groups;for(let z=0,Z=ct.length;z<Z;z++){const $=ct[z],Et=mt[$.materialIndex];if(Et&&Et.visible){const At=N(F,Et,U,w);F.onBeforeShadow(s,F,P,G,ot,At,$),s.renderBufferDirect(G,null,ot,At,F,$),F.onAfterShadow(s,F,P,G,ot,At,$)}}}else if(mt.visible){const ct=N(F,mt,U,w);F.onBeforeShadow(s,F,P,G,ot,ct,null),s.renderBufferDirect(G,null,ot,ct,F,null),F.onAfterShadow(s,F,P,G,ot,ct,null)}}const ut=F.children;for(let ot=0,mt=ut.length;ot<mt;ot++)C(ut[ot],P,G,U,w)}function V(F){F.target.removeEventListener("dispose",V);for(const G in m){const U=m[G],w=F.target.uuid;w in U&&(U[w].dispose(),delete U[w])}}}const $R={[Ep]:bp,[Tp]:Rp,[Ap]:wp,[Oo]:Cp,[bp]:Ep,[Rp]:Tp,[wp]:Ap,[Cp]:Oo};function tw(s,t){function n(){let Y=!1;const Rt=new qe;let ht=null;const yt=new qe(0,0,0,0);return{setMask:function(wt){ht!==wt&&!Y&&(s.colorMask(wt,wt,wt,wt),ht=wt)},setLocked:function(wt){Y=wt},setClear:function(wt,Ut,ie,$e,_n){_n===!0&&(wt*=$e,Ut*=$e,ie*=$e),Rt.set(wt,Ut,ie,$e),yt.equals(Rt)===!1&&(s.clearColor(wt,Ut,ie,$e),yt.copy(Rt))},reset:function(){Y=!1,ht=null,yt.set(-1,0,0,0)}}}function a(){let Y=!1,Rt=!1,ht=null,yt=null,wt=null;return{setReversed:function(Ut){if(Rt!==Ut){const ie=t.get("EXT_clip_control");Rt?ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.ZERO_TO_ONE_EXT):ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.NEGATIVE_ONE_TO_ONE_EXT);const $e=wt;wt=null,this.setClear($e)}Rt=Ut},getReversed:function(){return Rt},setTest:function(Ut){Ut?Mt(s.DEPTH_TEST):Ft(s.DEPTH_TEST)},setMask:function(Ut){ht!==Ut&&!Y&&(s.depthMask(Ut),ht=Ut)},setFunc:function(Ut){if(Rt&&(Ut=$R[Ut]),yt!==Ut){switch(Ut){case Ep:s.depthFunc(s.NEVER);break;case bp:s.depthFunc(s.ALWAYS);break;case Tp:s.depthFunc(s.LESS);break;case Oo:s.depthFunc(s.LEQUAL);break;case Ap:s.depthFunc(s.EQUAL);break;case Cp:s.depthFunc(s.GEQUAL);break;case Rp:s.depthFunc(s.GREATER);break;case wp:s.depthFunc(s.NOTEQUAL);break;default:s.depthFunc(s.LEQUAL)}yt=Ut}},setLocked:function(Ut){Y=Ut},setClear:function(Ut){wt!==Ut&&(Rt&&(Ut=1-Ut),s.clearDepth(Ut),wt=Ut)},reset:function(){Y=!1,ht=null,yt=null,wt=null,Rt=!1}}}function l(){let Y=!1,Rt=null,ht=null,yt=null,wt=null,Ut=null,ie=null,$e=null,_n=null;return{setTest:function(we){Y||(we?Mt(s.STENCIL_TEST):Ft(s.STENCIL_TEST))},setMask:function(we){Rt!==we&&!Y&&(s.stencilMask(we),Rt=we)},setFunc:function(we,Rn,wi){(ht!==we||yt!==Rn||wt!==wi)&&(s.stencilFunc(we,Rn,wi),ht=we,yt=Rn,wt=wi)},setOp:function(we,Rn,wi){(Ut!==we||ie!==Rn||$e!==wi)&&(s.stencilOp(we,Rn,wi),Ut=we,ie=Rn,$e=wi)},setLocked:function(we){Y=we},setClear:function(we){_n!==we&&(s.clearStencil(we),_n=we)},reset:function(){Y=!1,Rt=null,ht=null,yt=null,wt=null,Ut=null,ie=null,$e=null,_n=null}}}const c=new n,f=new a,d=new l,p=new WeakMap,m=new WeakMap;let g={},v={},y=new WeakMap,x=[],E=null,b=!1,M=null,_=null,I=null,N=null,C=null,V=null,F=null,P=new de(0,0,0),G=0,U=!1,w=null,H=null,ut=null,ot=null,mt=null;const ct=s.getParameter(s.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let z=!1,Z=0;const $=s.getParameter(s.VERSION);$.indexOf("WebGL")!==-1?(Z=parseFloat(/^WebGL (\d)/.exec($)[1]),z=Z>=1):$.indexOf("OpenGL ES")!==-1&&(Z=parseFloat(/^OpenGL ES (\d)/.exec($)[1]),z=Z>=2);let Et=null,At={};const O=s.getParameter(s.SCISSOR_BOX),nt=s.getParameter(s.VIEWPORT),St=new qe().fromArray(O),q=new qe().fromArray(nt);function ft(Y,Rt,ht,yt){const wt=new Uint8Array(4),Ut=s.createTexture();s.bindTexture(Y,Ut),s.texParameteri(Y,s.TEXTURE_MIN_FILTER,s.NEAREST),s.texParameteri(Y,s.TEXTURE_MAG_FILTER,s.NEAREST);for(let ie=0;ie<ht;ie++)Y===s.TEXTURE_3D||Y===s.TEXTURE_2D_ARRAY?s.texImage3D(Rt,0,s.RGBA,1,1,yt,0,s.RGBA,s.UNSIGNED_BYTE,wt):s.texImage2D(Rt+ie,0,s.RGBA,1,1,0,s.RGBA,s.UNSIGNED_BYTE,wt);return Ut}const Tt={};Tt[s.TEXTURE_2D]=ft(s.TEXTURE_2D,s.TEXTURE_2D,1),Tt[s.TEXTURE_CUBE_MAP]=ft(s.TEXTURE_CUBE_MAP,s.TEXTURE_CUBE_MAP_POSITIVE_X,6),Tt[s.TEXTURE_2D_ARRAY]=ft(s.TEXTURE_2D_ARRAY,s.TEXTURE_2D_ARRAY,1,1),Tt[s.TEXTURE_3D]=ft(s.TEXTURE_3D,s.TEXTURE_3D,1,1),c.setClear(0,0,0,1),f.setClear(1),d.setClear(0),Mt(s.DEPTH_TEST),f.setFunc(Oo),me(!1),Se(U_),Mt(s.CULL_FACE),k(Na);function Mt(Y){g[Y]!==!0&&(s.enable(Y),g[Y]=!0)}function Ft(Y){g[Y]!==!1&&(s.disable(Y),g[Y]=!1)}function Vt(Y,Rt){return v[Y]!==Rt?(s.bindFramebuffer(Y,Rt),v[Y]=Rt,Y===s.DRAW_FRAMEBUFFER&&(v[s.FRAMEBUFFER]=Rt),Y===s.FRAMEBUFFER&&(v[s.DRAW_FRAMEBUFFER]=Rt),!0):!1}function re(Y,Rt){let ht=x,yt=!1;if(Y){ht=y.get(Rt),ht===void 0&&(ht=[],y.set(Rt,ht));const wt=Y.textures;if(ht.length!==wt.length||ht[0]!==s.COLOR_ATTACHMENT0){for(let Ut=0,ie=wt.length;Ut<ie;Ut++)ht[Ut]=s.COLOR_ATTACHMENT0+Ut;ht.length=wt.length,yt=!0}}else ht[0]!==s.BACK&&(ht[0]=s.BACK,yt=!0);yt&&s.drawBuffers(ht)}function He(Y){return E!==Y?(s.useProgram(Y),E=Y,!0):!1}const ve={[er]:s.FUNC_ADD,[N1]:s.FUNC_SUBTRACT,[L1]:s.FUNC_REVERSE_SUBTRACT};ve[O1]=s.MIN,ve[P1]=s.MAX;const Je={[z1]:s.ZERO,[I1]:s.ONE,[B1]:s.SRC_COLOR,[Sp]:s.SRC_ALPHA,[X1]:s.SRC_ALPHA_SATURATE,[V1]:s.DST_COLOR,[H1]:s.DST_ALPHA,[F1]:s.ONE_MINUS_SRC_COLOR,[Mp]:s.ONE_MINUS_SRC_ALPHA,[k1]:s.ONE_MINUS_DST_COLOR,[G1]:s.ONE_MINUS_DST_ALPHA,[j1]:s.CONSTANT_COLOR,[q1]:s.ONE_MINUS_CONSTANT_COLOR,[W1]:s.CONSTANT_ALPHA,[Y1]:s.ONE_MINUS_CONSTANT_ALPHA};function k(Y,Rt,ht,yt,wt,Ut,ie,$e,_n,we){if(Y===Na){b===!0&&(Ft(s.BLEND),b=!1);return}if(b===!1&&(Mt(s.BLEND),b=!0),Y!==U1){if(Y!==M||we!==U){if((_!==er||C!==er)&&(s.blendEquation(s.FUNC_ADD),_=er,C=er),we)switch(Y){case vo:s.blendFuncSeparate(s.ONE,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case xp:s.blendFunc(s.ONE,s.ONE);break;case N_:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case L_:s.blendFuncSeparate(s.ZERO,s.SRC_COLOR,s.ZERO,s.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}else switch(Y){case vo:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case xp:s.blendFunc(s.SRC_ALPHA,s.ONE);break;case N_:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case L_:s.blendFunc(s.ZERO,s.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}I=null,N=null,V=null,F=null,P.set(0,0,0),G=0,M=Y,U=we}return}wt=wt||Rt,Ut=Ut||ht,ie=ie||yt,(Rt!==_||wt!==C)&&(s.blendEquationSeparate(ve[Rt],ve[wt]),_=Rt,C=wt),(ht!==I||yt!==N||Ut!==V||ie!==F)&&(s.blendFuncSeparate(Je[ht],Je[yt],Je[Ut],Je[ie]),I=ht,N=yt,V=Ut,F=ie),($e.equals(P)===!1||_n!==G)&&(s.blendColor($e.r,$e.g,$e.b,_n),P.copy($e),G=_n),M=Y,U=!1}function Pn(Y,Rt){Y.side===wa?Ft(s.CULL_FACE):Mt(s.CULL_FACE);let ht=Y.side===ii;Rt&&(ht=!ht),me(ht),Y.blending===vo&&Y.transparent===!1?k(Na):k(Y.blending,Y.blendEquation,Y.blendSrc,Y.blendDst,Y.blendEquationAlpha,Y.blendSrcAlpha,Y.blendDstAlpha,Y.blendColor,Y.blendAlpha,Y.premultipliedAlpha),f.setFunc(Y.depthFunc),f.setTest(Y.depthTest),f.setMask(Y.depthWrite),c.setMask(Y.colorWrite);const yt=Y.stencilWrite;d.setTest(yt),yt&&(d.setMask(Y.stencilWriteMask),d.setFunc(Y.stencilFunc,Y.stencilRef,Y.stencilFuncMask),d.setOp(Y.stencilFail,Y.stencilZFail,Y.stencilZPass)),Ie(Y.polygonOffset,Y.polygonOffsetFactor,Y.polygonOffsetUnits),Y.alphaToCoverage===!0?Mt(s.SAMPLE_ALPHA_TO_COVERAGE):Ft(s.SAMPLE_ALPHA_TO_COVERAGE)}function me(Y){w!==Y&&(Y?s.frontFace(s.CW):s.frontFace(s.CCW),w=Y)}function Se(Y){Y!==R1?(Mt(s.CULL_FACE),Y!==H&&(Y===U_?s.cullFace(s.BACK):Y===w1?s.cullFace(s.FRONT):s.cullFace(s.FRONT_AND_BACK))):Ft(s.CULL_FACE),H=Y}function Qt(Y){Y!==ut&&(z&&s.lineWidth(Y),ut=Y)}function Ie(Y,Rt,ht){Y?(Mt(s.POLYGON_OFFSET_FILL),(ot!==Rt||mt!==ht)&&(s.polygonOffset(Rt,ht),ot=Rt,mt=ht)):Ft(s.POLYGON_OFFSET_FILL)}function Yt(Y){Y?Mt(s.SCISSOR_TEST):Ft(s.SCISSOR_TEST)}function L(Y){Y===void 0&&(Y=s.TEXTURE0+ct-1),Et!==Y&&(s.activeTexture(Y),Et=Y)}function A(Y,Rt,ht){ht===void 0&&(Et===null?ht=s.TEXTURE0+ct-1:ht=Et);let yt=At[ht];yt===void 0&&(yt={type:void 0,texture:void 0},At[ht]=yt),(yt.type!==Y||yt.texture!==Rt)&&(Et!==ht&&(s.activeTexture(ht),Et=ht),s.bindTexture(Y,Rt||Tt[Y]),yt.type=Y,yt.texture=Rt)}function at(){const Y=At[Et];Y!==void 0&&Y.type!==void 0&&(s.bindTexture(Y.type,null),Y.type=void 0,Y.texture=void 0)}function pt(){try{s.compressedTexImage2D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function bt(){try{s.compressedTexImage3D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function vt(){try{s.texSubImage2D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function jt(){try{s.texSubImage3D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Dt(){try{s.compressedTexSubImage2D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Bt(){try{s.compressedTexSubImage3D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Me(){try{s.texStorage2D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ct(){try{s.texStorage3D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ht(){try{s.texImage2D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Zt(){try{s.texImage3D.apply(s,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function qt(Y){St.equals(Y)===!1&&(s.scissor(Y.x,Y.y,Y.z,Y.w),St.copy(Y))}function Ot(Y){q.equals(Y)===!1&&(s.viewport(Y.x,Y.y,Y.z,Y.w),q.copy(Y))}function ne(Y,Rt){let ht=m.get(Rt);ht===void 0&&(ht=new WeakMap,m.set(Rt,ht));let yt=ht.get(Y);yt===void 0&&(yt=s.getUniformBlockIndex(Rt,Y.name),ht.set(Y,yt))}function oe(Y,Rt){const yt=m.get(Rt).get(Y);p.get(Rt)!==yt&&(s.uniformBlockBinding(Rt,yt,Y.__bindingPointIndex),p.set(Rt,yt))}function Ge(){s.disable(s.BLEND),s.disable(s.CULL_FACE),s.disable(s.DEPTH_TEST),s.disable(s.POLYGON_OFFSET_FILL),s.disable(s.SCISSOR_TEST),s.disable(s.STENCIL_TEST),s.disable(s.SAMPLE_ALPHA_TO_COVERAGE),s.blendEquation(s.FUNC_ADD),s.blendFunc(s.ONE,s.ZERO),s.blendFuncSeparate(s.ONE,s.ZERO,s.ONE,s.ZERO),s.blendColor(0,0,0,0),s.colorMask(!0,!0,!0,!0),s.clearColor(0,0,0,0),s.depthMask(!0),s.depthFunc(s.LESS),f.setReversed(!1),s.clearDepth(1),s.stencilMask(4294967295),s.stencilFunc(s.ALWAYS,0,4294967295),s.stencilOp(s.KEEP,s.KEEP,s.KEEP),s.clearStencil(0),s.cullFace(s.BACK),s.frontFace(s.CCW),s.polygonOffset(0,0),s.activeTexture(s.TEXTURE0),s.bindFramebuffer(s.FRAMEBUFFER,null),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),s.bindFramebuffer(s.READ_FRAMEBUFFER,null),s.useProgram(null),s.lineWidth(1),s.scissor(0,0,s.canvas.width,s.canvas.height),s.viewport(0,0,s.canvas.width,s.canvas.height),g={},Et=null,At={},v={},y=new WeakMap,x=[],E=null,b=!1,M=null,_=null,I=null,N=null,C=null,V=null,F=null,P=new de(0,0,0),G=0,U=!1,w=null,H=null,ut=null,ot=null,mt=null,St.set(0,0,s.canvas.width,s.canvas.height),q.set(0,0,s.canvas.width,s.canvas.height),c.reset(),f.reset(),d.reset()}return{buffers:{color:c,depth:f,stencil:d},enable:Mt,disable:Ft,bindFramebuffer:Vt,drawBuffers:re,useProgram:He,setBlending:k,setMaterial:Pn,setFlipSided:me,setCullFace:Se,setLineWidth:Qt,setPolygonOffset:Ie,setScissorTest:Yt,activeTexture:L,bindTexture:A,unbindTexture:at,compressedTexImage2D:pt,compressedTexImage3D:bt,texImage2D:Ht,texImage3D:Zt,updateUBOMapping:ne,uniformBlockBinding:oe,texStorage2D:Me,texStorage3D:Ct,texSubImage2D:vt,texSubImage3D:jt,compressedTexSubImage2D:Dt,compressedTexSubImage3D:Bt,scissor:qt,viewport:Ot,reset:Ge}}function ew(s,t,n,a,l,c,f){const d=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),m=new Wt,g=new WeakMap;let v;const y=new WeakMap;let x=!1;try{x=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function E(L,A){return x?new OffscreenCanvas(L,A):af("canvas")}function b(L,A,at){let pt=1;const bt=Yt(L);if((bt.width>at||bt.height>at)&&(pt=at/Math.max(bt.width,bt.height)),pt<1)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap||typeof VideoFrame<"u"&&L instanceof VideoFrame){const vt=Math.floor(pt*bt.width),jt=Math.floor(pt*bt.height);v===void 0&&(v=E(vt,jt));const Dt=A?E(vt,jt):v;return Dt.width=vt,Dt.height=jt,Dt.getContext("2d").drawImage(L,0,0,vt,jt),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+bt.width+"x"+bt.height+") to ("+vt+"x"+jt+")."),Dt}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+bt.width+"x"+bt.height+")."),L;return L}function M(L){return L.generateMipmaps}function _(L){s.generateMipmap(L)}function I(L){return L.isWebGLCubeRenderTarget?s.TEXTURE_CUBE_MAP:L.isWebGL3DRenderTarget?s.TEXTURE_3D:L.isWebGLArrayRenderTarget||L.isCompressedArrayTexture?s.TEXTURE_2D_ARRAY:s.TEXTURE_2D}function N(L,A,at,pt,bt=!1){if(L!==null){if(s[L]!==void 0)return s[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let vt=A;if(A===s.RED&&(at===s.FLOAT&&(vt=s.R32F),at===s.HALF_FLOAT&&(vt=s.R16F),at===s.UNSIGNED_BYTE&&(vt=s.R8)),A===s.RED_INTEGER&&(at===s.UNSIGNED_BYTE&&(vt=s.R8UI),at===s.UNSIGNED_SHORT&&(vt=s.R16UI),at===s.UNSIGNED_INT&&(vt=s.R32UI),at===s.BYTE&&(vt=s.R8I),at===s.SHORT&&(vt=s.R16I),at===s.INT&&(vt=s.R32I)),A===s.RG&&(at===s.FLOAT&&(vt=s.RG32F),at===s.HALF_FLOAT&&(vt=s.RG16F),at===s.UNSIGNED_BYTE&&(vt=s.RG8)),A===s.RG_INTEGER&&(at===s.UNSIGNED_BYTE&&(vt=s.RG8UI),at===s.UNSIGNED_SHORT&&(vt=s.RG16UI),at===s.UNSIGNED_INT&&(vt=s.RG32UI),at===s.BYTE&&(vt=s.RG8I),at===s.SHORT&&(vt=s.RG16I),at===s.INT&&(vt=s.RG32I)),A===s.RGB_INTEGER&&(at===s.UNSIGNED_BYTE&&(vt=s.RGB8UI),at===s.UNSIGNED_SHORT&&(vt=s.RGB16UI),at===s.UNSIGNED_INT&&(vt=s.RGB32UI),at===s.BYTE&&(vt=s.RGB8I),at===s.SHORT&&(vt=s.RGB16I),at===s.INT&&(vt=s.RGB32I)),A===s.RGBA_INTEGER&&(at===s.UNSIGNED_BYTE&&(vt=s.RGBA8UI),at===s.UNSIGNED_SHORT&&(vt=s.RGBA16UI),at===s.UNSIGNED_INT&&(vt=s.RGBA32UI),at===s.BYTE&&(vt=s.RGBA8I),at===s.SHORT&&(vt=s.RGBA16I),at===s.INT&&(vt=s.RGBA32I)),A===s.RGB&&at===s.UNSIGNED_INT_5_9_9_9_REV&&(vt=s.RGB9_E5),A===s.RGBA){const jt=bt?ef:Oe.getTransfer(pt);at===s.FLOAT&&(vt=s.RGBA32F),at===s.HALF_FLOAT&&(vt=s.RGBA16F),at===s.UNSIGNED_BYTE&&(vt=jt===je?s.SRGB8_ALPHA8:s.RGBA8),at===s.UNSIGNED_SHORT_4_4_4_4&&(vt=s.RGBA4),at===s.UNSIGNED_SHORT_5_5_5_1&&(vt=s.RGB5_A1)}return(vt===s.R16F||vt===s.R32F||vt===s.RG16F||vt===s.RG32F||vt===s.RGBA16F||vt===s.RGBA32F)&&t.get("EXT_color_buffer_float"),vt}function C(L,A){let at;return L?A===null||A===gr||A===Io?at=s.DEPTH24_STENCIL8:A===Da?at=s.DEPTH32F_STENCIL8:A===tc&&(at=s.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):A===null||A===gr||A===Io?at=s.DEPTH_COMPONENT24:A===Da?at=s.DEPTH_COMPONENT32F:A===tc&&(at=s.DEPTH_COMPONENT16),at}function V(L,A){return M(L)===!0||L.isFramebufferTexture&&L.minFilter!==Hi&&L.minFilter!==$i?Math.log2(Math.max(A.width,A.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?A.mipmaps.length:1}function F(L){const A=L.target;A.removeEventListener("dispose",F),G(A),A.isVideoTexture&&g.delete(A)}function P(L){const A=L.target;A.removeEventListener("dispose",P),w(A)}function G(L){const A=a.get(L);if(A.__webglInit===void 0)return;const at=L.source,pt=y.get(at);if(pt){const bt=pt[A.__cacheKey];bt.usedTimes--,bt.usedTimes===0&&U(L),Object.keys(pt).length===0&&y.delete(at)}a.remove(L)}function U(L){const A=a.get(L);s.deleteTexture(A.__webglTexture);const at=L.source,pt=y.get(at);delete pt[A.__cacheKey],f.memory.textures--}function w(L){const A=a.get(L);if(L.depthTexture&&(L.depthTexture.dispose(),a.remove(L.depthTexture)),L.isWebGLCubeRenderTarget)for(let pt=0;pt<6;pt++){if(Array.isArray(A.__webglFramebuffer[pt]))for(let bt=0;bt<A.__webglFramebuffer[pt].length;bt++)s.deleteFramebuffer(A.__webglFramebuffer[pt][bt]);else s.deleteFramebuffer(A.__webglFramebuffer[pt]);A.__webglDepthbuffer&&s.deleteRenderbuffer(A.__webglDepthbuffer[pt])}else{if(Array.isArray(A.__webglFramebuffer))for(let pt=0;pt<A.__webglFramebuffer.length;pt++)s.deleteFramebuffer(A.__webglFramebuffer[pt]);else s.deleteFramebuffer(A.__webglFramebuffer);if(A.__webglDepthbuffer&&s.deleteRenderbuffer(A.__webglDepthbuffer),A.__webglMultisampledFramebuffer&&s.deleteFramebuffer(A.__webglMultisampledFramebuffer),A.__webglColorRenderbuffer)for(let pt=0;pt<A.__webglColorRenderbuffer.length;pt++)A.__webglColorRenderbuffer[pt]&&s.deleteRenderbuffer(A.__webglColorRenderbuffer[pt]);A.__webglDepthRenderbuffer&&s.deleteRenderbuffer(A.__webglDepthRenderbuffer)}const at=L.textures;for(let pt=0,bt=at.length;pt<bt;pt++){const vt=a.get(at[pt]);vt.__webglTexture&&(s.deleteTexture(vt.__webglTexture),f.memory.textures--),a.remove(at[pt])}a.remove(L)}let H=0;function ut(){H=0}function ot(){const L=H;return L>=l.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+l.maxTextures),H+=1,L}function mt(L){const A=[];return A.push(L.wrapS),A.push(L.wrapT),A.push(L.wrapR||0),A.push(L.magFilter),A.push(L.minFilter),A.push(L.anisotropy),A.push(L.internalFormat),A.push(L.format),A.push(L.type),A.push(L.generateMipmaps),A.push(L.premultiplyAlpha),A.push(L.flipY),A.push(L.unpackAlignment),A.push(L.colorSpace),A.join()}function ct(L,A){const at=a.get(L);if(L.isVideoTexture&&Qt(L),L.isRenderTargetTexture===!1&&L.version>0&&at.__version!==L.version){const pt=L.image;if(pt===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(pt.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{q(at,L,A);return}}n.bindTexture(s.TEXTURE_2D,at.__webglTexture,s.TEXTURE0+A)}function z(L,A){const at=a.get(L);if(L.version>0&&at.__version!==L.version){q(at,L,A);return}n.bindTexture(s.TEXTURE_2D_ARRAY,at.__webglTexture,s.TEXTURE0+A)}function Z(L,A){const at=a.get(L);if(L.version>0&&at.__version!==L.version){q(at,L,A);return}n.bindTexture(s.TEXTURE_3D,at.__webglTexture,s.TEXTURE0+A)}function $(L,A){const at=a.get(L);if(L.version>0&&at.__version!==L.version){ft(at,L,A);return}n.bindTexture(s.TEXTURE_CUBE_MAP,at.__webglTexture,s.TEXTURE0+A)}const Et={[Np]:s.REPEAT,[sr]:s.CLAMP_TO_EDGE,[Lp]:s.MIRRORED_REPEAT},At={[Hi]:s.NEAREST,[ab]:s.NEAREST_MIPMAP_NEAREST,[bu]:s.NEAREST_MIPMAP_LINEAR,[$i]:s.LINEAR,[Ad]:s.LINEAR_MIPMAP_NEAREST,[rr]:s.LINEAR_MIPMAP_LINEAR},O={[cb]:s.NEVER,[mb]:s.ALWAYS,[ub]:s.LESS,[Ax]:s.LEQUAL,[fb]:s.EQUAL,[pb]:s.GEQUAL,[hb]:s.GREATER,[db]:s.NOTEQUAL};function nt(L,A){if(A.type===Da&&t.has("OES_texture_float_linear")===!1&&(A.magFilter===$i||A.magFilter===Ad||A.magFilter===bu||A.magFilter===rr||A.minFilter===$i||A.minFilter===Ad||A.minFilter===bu||A.minFilter===rr)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),s.texParameteri(L,s.TEXTURE_WRAP_S,Et[A.wrapS]),s.texParameteri(L,s.TEXTURE_WRAP_T,Et[A.wrapT]),(L===s.TEXTURE_3D||L===s.TEXTURE_2D_ARRAY)&&s.texParameteri(L,s.TEXTURE_WRAP_R,Et[A.wrapR]),s.texParameteri(L,s.TEXTURE_MAG_FILTER,At[A.magFilter]),s.texParameteri(L,s.TEXTURE_MIN_FILTER,At[A.minFilter]),A.compareFunction&&(s.texParameteri(L,s.TEXTURE_COMPARE_MODE,s.COMPARE_REF_TO_TEXTURE),s.texParameteri(L,s.TEXTURE_COMPARE_FUNC,O[A.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(A.magFilter===Hi||A.minFilter!==bu&&A.minFilter!==rr||A.type===Da&&t.has("OES_texture_float_linear")===!1)return;if(A.anisotropy>1||a.get(A).__currentAnisotropy){const at=t.get("EXT_texture_filter_anisotropic");s.texParameterf(L,at.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(A.anisotropy,l.getMaxAnisotropy())),a.get(A).__currentAnisotropy=A.anisotropy}}}function St(L,A){let at=!1;L.__webglInit===void 0&&(L.__webglInit=!0,A.addEventListener("dispose",F));const pt=A.source;let bt=y.get(pt);bt===void 0&&(bt={},y.set(pt,bt));const vt=mt(A);if(vt!==L.__cacheKey){bt[vt]===void 0&&(bt[vt]={texture:s.createTexture(),usedTimes:0},f.memory.textures++,at=!0),bt[vt].usedTimes++;const jt=bt[L.__cacheKey];jt!==void 0&&(bt[L.__cacheKey].usedTimes--,jt.usedTimes===0&&U(A)),L.__cacheKey=vt,L.__webglTexture=bt[vt].texture}return at}function q(L,A,at){let pt=s.TEXTURE_2D;(A.isDataArrayTexture||A.isCompressedArrayTexture)&&(pt=s.TEXTURE_2D_ARRAY),A.isData3DTexture&&(pt=s.TEXTURE_3D);const bt=St(L,A),vt=A.source;n.bindTexture(pt,L.__webglTexture,s.TEXTURE0+at);const jt=a.get(vt);if(vt.version!==jt.__version||bt===!0){n.activeTexture(s.TEXTURE0+at);const Dt=Oe.getPrimaries(Oe.workingColorSpace),Bt=A.colorSpace===ms?null:Oe.getPrimaries(A.colorSpace),Me=A.colorSpace===ms||Dt===Bt?s.NONE:s.BROWSER_DEFAULT_WEBGL;s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,A.flipY),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,A.premultiplyAlpha),s.pixelStorei(s.UNPACK_ALIGNMENT,A.unpackAlignment),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,Me);let Ct=b(A.image,!1,l.maxTextureSize);Ct=Ie(A,Ct);const Ht=c.convert(A.format,A.colorSpace),Zt=c.convert(A.type);let qt=N(A.internalFormat,Ht,Zt,A.colorSpace,A.isVideoTexture);nt(pt,A);let Ot;const ne=A.mipmaps,oe=A.isVideoTexture!==!0,Ge=jt.__version===void 0||bt===!0,Y=vt.dataReady,Rt=V(A,Ct);if(A.isDepthTexture)qt=C(A.format===Bo,A.type),Ge&&(oe?n.texStorage2D(s.TEXTURE_2D,1,qt,Ct.width,Ct.height):n.texImage2D(s.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,null));else if(A.isDataTexture)if(ne.length>0){oe&&Ge&&n.texStorage2D(s.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let ht=0,yt=ne.length;ht<yt;ht++)Ot=ne[ht],oe?Y&&n.texSubImage2D(s.TEXTURE_2D,ht,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(s.TEXTURE_2D,ht,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data);A.generateMipmaps=!1}else oe?(Ge&&n.texStorage2D(s.TEXTURE_2D,Rt,qt,Ct.width,Ct.height),Y&&n.texSubImage2D(s.TEXTURE_2D,0,0,0,Ct.width,Ct.height,Ht,Zt,Ct.data)):n.texImage2D(s.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,Ct.data);else if(A.isCompressedTexture)if(A.isCompressedArrayTexture){oe&&Ge&&n.texStorage3D(s.TEXTURE_2D_ARRAY,Rt,qt,ne[0].width,ne[0].height,Ct.depth);for(let ht=0,yt=ne.length;ht<yt;ht++)if(Ot=ne[ht],A.format!==Fi)if(Ht!==null)if(oe){if(Y)if(A.layerUpdates.size>0){const wt=ry(Ot.width,Ot.height,A.format,A.type);for(const Ut of A.layerUpdates){const ie=Ot.data.subarray(Ut*wt/Ot.data.BYTES_PER_ELEMENT,(Ut+1)*wt/Ot.data.BYTES_PER_ELEMENT);n.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,ht,0,0,Ut,Ot.width,Ot.height,1,Ht,ie)}A.clearLayerUpdates()}else n.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,ht,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Ot.data)}else n.compressedTexImage3D(s.TEXTURE_2D_ARRAY,ht,qt,Ot.width,Ot.height,Ct.depth,0,Ot.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else oe?Y&&n.texSubImage3D(s.TEXTURE_2D_ARRAY,ht,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Zt,Ot.data):n.texImage3D(s.TEXTURE_2D_ARRAY,ht,qt,Ot.width,Ot.height,Ct.depth,0,Ht,Zt,Ot.data)}else{oe&&Ge&&n.texStorage2D(s.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let ht=0,yt=ne.length;ht<yt;ht++)Ot=ne[ht],A.format!==Fi?Ht!==null?oe?Y&&n.compressedTexSubImage2D(s.TEXTURE_2D,ht,0,0,Ot.width,Ot.height,Ht,Ot.data):n.compressedTexImage2D(s.TEXTURE_2D,ht,qt,Ot.width,Ot.height,0,Ot.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):oe?Y&&n.texSubImage2D(s.TEXTURE_2D,ht,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(s.TEXTURE_2D,ht,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data)}else if(A.isDataArrayTexture)if(oe){if(Ge&&n.texStorage3D(s.TEXTURE_2D_ARRAY,Rt,qt,Ct.width,Ct.height,Ct.depth),Y)if(A.layerUpdates.size>0){const ht=ry(Ct.width,Ct.height,A.format,A.type);for(const yt of A.layerUpdates){const wt=Ct.data.subarray(yt*ht/Ct.data.BYTES_PER_ELEMENT,(yt+1)*ht/Ct.data.BYTES_PER_ELEMENT);n.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,yt,Ct.width,Ct.height,1,Ht,Zt,wt)}A.clearLayerUpdates()}else n.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)}else n.texImage3D(s.TEXTURE_2D_ARRAY,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(A.isData3DTexture)oe?(Ge&&n.texStorage3D(s.TEXTURE_3D,Rt,qt,Ct.width,Ct.height,Ct.depth),Y&&n.texSubImage3D(s.TEXTURE_3D,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)):n.texImage3D(s.TEXTURE_3D,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(A.isFramebufferTexture){if(Ge)if(oe)n.texStorage2D(s.TEXTURE_2D,Rt,qt,Ct.width,Ct.height);else{let ht=Ct.width,yt=Ct.height;for(let wt=0;wt<Rt;wt++)n.texImage2D(s.TEXTURE_2D,wt,qt,ht,yt,0,Ht,Zt,null),ht>>=1,yt>>=1}}else if(ne.length>0){if(oe&&Ge){const ht=Yt(ne[0]);n.texStorage2D(s.TEXTURE_2D,Rt,qt,ht.width,ht.height)}for(let ht=0,yt=ne.length;ht<yt;ht++)Ot=ne[ht],oe?Y&&n.texSubImage2D(s.TEXTURE_2D,ht,0,0,Ht,Zt,Ot):n.texImage2D(s.TEXTURE_2D,ht,qt,Ht,Zt,Ot);A.generateMipmaps=!1}else if(oe){if(Ge){const ht=Yt(Ct);n.texStorage2D(s.TEXTURE_2D,Rt,qt,ht.width,ht.height)}Y&&n.texSubImage2D(s.TEXTURE_2D,0,0,0,Ht,Zt,Ct)}else n.texImage2D(s.TEXTURE_2D,0,qt,Ht,Zt,Ct);M(A)&&_(pt),jt.__version=vt.version,A.onUpdate&&A.onUpdate(A)}L.__version=A.version}function ft(L,A,at){if(A.image.length!==6)return;const pt=St(L,A),bt=A.source;n.bindTexture(s.TEXTURE_CUBE_MAP,L.__webglTexture,s.TEXTURE0+at);const vt=a.get(bt);if(bt.version!==vt.__version||pt===!0){n.activeTexture(s.TEXTURE0+at);const jt=Oe.getPrimaries(Oe.workingColorSpace),Dt=A.colorSpace===ms?null:Oe.getPrimaries(A.colorSpace),Bt=A.colorSpace===ms||jt===Dt?s.NONE:s.BROWSER_DEFAULT_WEBGL;s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,A.flipY),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,A.premultiplyAlpha),s.pixelStorei(s.UNPACK_ALIGNMENT,A.unpackAlignment),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,Bt);const Me=A.isCompressedTexture||A.image[0].isCompressedTexture,Ct=A.image[0]&&A.image[0].isDataTexture,Ht=[];for(let yt=0;yt<6;yt++)!Me&&!Ct?Ht[yt]=b(A.image[yt],!0,l.maxCubemapSize):Ht[yt]=Ct?A.image[yt].image:A.image[yt],Ht[yt]=Ie(A,Ht[yt]);const Zt=Ht[0],qt=c.convert(A.format,A.colorSpace),Ot=c.convert(A.type),ne=N(A.internalFormat,qt,Ot,A.colorSpace),oe=A.isVideoTexture!==!0,Ge=vt.__version===void 0||pt===!0,Y=bt.dataReady;let Rt=V(A,Zt);nt(s.TEXTURE_CUBE_MAP,A);let ht;if(Me){oe&&Ge&&n.texStorage2D(s.TEXTURE_CUBE_MAP,Rt,ne,Zt.width,Zt.height);for(let yt=0;yt<6;yt++){ht=Ht[yt].mipmaps;for(let wt=0;wt<ht.length;wt++){const Ut=ht[wt];A.format!==Fi?qt!==null?oe?Y&&n.compressedTexSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Ut.width,Ut.height,qt,Ut.data):n.compressedTexImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Ut.width,Ut.height,0,Ut.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):oe?Y&&n.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Ut.width,Ut.height,qt,Ot,Ut.data):n.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Ut.width,Ut.height,0,qt,Ot,Ut.data)}}}else{if(ht=A.mipmaps,oe&&Ge){ht.length>0&&Rt++;const yt=Yt(Ht[0]);n.texStorage2D(s.TEXTURE_CUBE_MAP,Rt,ne,yt.width,yt.height)}for(let yt=0;yt<6;yt++)if(Ct){oe?Y&&n.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,Ht[yt].width,Ht[yt].height,qt,Ot,Ht[yt].data):n.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,Ht[yt].width,Ht[yt].height,0,qt,Ot,Ht[yt].data);for(let wt=0;wt<ht.length;wt++){const ie=ht[wt].image[yt].image;oe?Y&&n.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,ie.width,ie.height,qt,Ot,ie.data):n.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,ie.width,ie.height,0,qt,Ot,ie.data)}}else{oe?Y&&n.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,qt,Ot,Ht[yt]):n.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,qt,Ot,Ht[yt]);for(let wt=0;wt<ht.length;wt++){const Ut=ht[wt];oe?Y&&n.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,qt,Ot,Ut.image[yt]):n.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,qt,Ot,Ut.image[yt])}}}M(A)&&_(s.TEXTURE_CUBE_MAP),vt.__version=bt.version,A.onUpdate&&A.onUpdate(A)}L.__version=A.version}function Tt(L,A,at,pt,bt,vt){const jt=c.convert(at.format,at.colorSpace),Dt=c.convert(at.type),Bt=N(at.internalFormat,jt,Dt,at.colorSpace),Me=a.get(A),Ct=a.get(at);if(Ct.__renderTarget=A,!Me.__hasExternalTextures){const Ht=Math.max(1,A.width>>vt),Zt=Math.max(1,A.height>>vt);bt===s.TEXTURE_3D||bt===s.TEXTURE_2D_ARRAY?n.texImage3D(bt,vt,Bt,Ht,Zt,A.depth,0,jt,Dt,null):n.texImage2D(bt,vt,Bt,Ht,Zt,0,jt,Dt,null)}n.bindFramebuffer(s.FRAMEBUFFER,L),Se(A)?d.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,pt,bt,Ct.__webglTexture,0,me(A)):(bt===s.TEXTURE_2D||bt>=s.TEXTURE_CUBE_MAP_POSITIVE_X&&bt<=s.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&s.framebufferTexture2D(s.FRAMEBUFFER,pt,bt,Ct.__webglTexture,vt),n.bindFramebuffer(s.FRAMEBUFFER,null)}function Mt(L,A,at){if(s.bindRenderbuffer(s.RENDERBUFFER,L),A.depthBuffer){const pt=A.depthTexture,bt=pt&&pt.isDepthTexture?pt.type:null,vt=C(A.stencilBuffer,bt),jt=A.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,Dt=me(A);Se(A)?d.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,Dt,vt,A.width,A.height):at?s.renderbufferStorageMultisample(s.RENDERBUFFER,Dt,vt,A.width,A.height):s.renderbufferStorage(s.RENDERBUFFER,vt,A.width,A.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,jt,s.RENDERBUFFER,L)}else{const pt=A.textures;for(let bt=0;bt<pt.length;bt++){const vt=pt[bt],jt=c.convert(vt.format,vt.colorSpace),Dt=c.convert(vt.type),Bt=N(vt.internalFormat,jt,Dt,vt.colorSpace),Me=me(A);at&&Se(A)===!1?s.renderbufferStorageMultisample(s.RENDERBUFFER,Me,Bt,A.width,A.height):Se(A)?d.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,Me,Bt,A.width,A.height):s.renderbufferStorage(s.RENDERBUFFER,Bt,A.width,A.height)}}s.bindRenderbuffer(s.RENDERBUFFER,null)}function Ft(L,A){if(A&&A.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(n.bindFramebuffer(s.FRAMEBUFFER,L),!(A.depthTexture&&A.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const pt=a.get(A.depthTexture);pt.__renderTarget=A,(!pt.__webglTexture||A.depthTexture.image.width!==A.width||A.depthTexture.image.height!==A.height)&&(A.depthTexture.image.width=A.width,A.depthTexture.image.height=A.height,A.depthTexture.needsUpdate=!0),ct(A.depthTexture,0);const bt=pt.__webglTexture,vt=me(A);if(A.depthTexture.format===_o)Se(A)?d.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,s.DEPTH_ATTACHMENT,s.TEXTURE_2D,bt,0,vt):s.framebufferTexture2D(s.FRAMEBUFFER,s.DEPTH_ATTACHMENT,s.TEXTURE_2D,bt,0);else if(A.depthTexture.format===Bo)Se(A)?d.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,s.DEPTH_STENCIL_ATTACHMENT,s.TEXTURE_2D,bt,0,vt):s.framebufferTexture2D(s.FRAMEBUFFER,s.DEPTH_STENCIL_ATTACHMENT,s.TEXTURE_2D,bt,0);else throw new Error("Unknown depthTexture format")}function Vt(L){const A=a.get(L),at=L.isWebGLCubeRenderTarget===!0;if(A.__boundDepthTexture!==L.depthTexture){const pt=L.depthTexture;if(A.__depthDisposeCallback&&A.__depthDisposeCallback(),pt){const bt=()=>{delete A.__boundDepthTexture,delete A.__depthDisposeCallback,pt.removeEventListener("dispose",bt)};pt.addEventListener("dispose",bt),A.__depthDisposeCallback=bt}A.__boundDepthTexture=pt}if(L.depthTexture&&!A.__autoAllocateDepthBuffer){if(at)throw new Error("target.depthTexture not supported in Cube render targets");Ft(A.__webglFramebuffer,L)}else if(at){A.__webglDepthbuffer=[];for(let pt=0;pt<6;pt++)if(n.bindFramebuffer(s.FRAMEBUFFER,A.__webglFramebuffer[pt]),A.__webglDepthbuffer[pt]===void 0)A.__webglDepthbuffer[pt]=s.createRenderbuffer(),Mt(A.__webglDepthbuffer[pt],L,!1);else{const bt=L.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,vt=A.__webglDepthbuffer[pt];s.bindRenderbuffer(s.RENDERBUFFER,vt),s.framebufferRenderbuffer(s.FRAMEBUFFER,bt,s.RENDERBUFFER,vt)}}else if(n.bindFramebuffer(s.FRAMEBUFFER,A.__webglFramebuffer),A.__webglDepthbuffer===void 0)A.__webglDepthbuffer=s.createRenderbuffer(),Mt(A.__webglDepthbuffer,L,!1);else{const pt=L.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,bt=A.__webglDepthbuffer;s.bindRenderbuffer(s.RENDERBUFFER,bt),s.framebufferRenderbuffer(s.FRAMEBUFFER,pt,s.RENDERBUFFER,bt)}n.bindFramebuffer(s.FRAMEBUFFER,null)}function re(L,A,at){const pt=a.get(L);A!==void 0&&Tt(pt.__webglFramebuffer,L,L.texture,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,0),at!==void 0&&Vt(L)}function He(L){const A=L.texture,at=a.get(L),pt=a.get(A);L.addEventListener("dispose",P);const bt=L.textures,vt=L.isWebGLCubeRenderTarget===!0,jt=bt.length>1;if(jt||(pt.__webglTexture===void 0&&(pt.__webglTexture=s.createTexture()),pt.__version=A.version,f.memory.textures++),vt){at.__webglFramebuffer=[];for(let Dt=0;Dt<6;Dt++)if(A.mipmaps&&A.mipmaps.length>0){at.__webglFramebuffer[Dt]=[];for(let Bt=0;Bt<A.mipmaps.length;Bt++)at.__webglFramebuffer[Dt][Bt]=s.createFramebuffer()}else at.__webglFramebuffer[Dt]=s.createFramebuffer()}else{if(A.mipmaps&&A.mipmaps.length>0){at.__webglFramebuffer=[];for(let Dt=0;Dt<A.mipmaps.length;Dt++)at.__webglFramebuffer[Dt]=s.createFramebuffer()}else at.__webglFramebuffer=s.createFramebuffer();if(jt)for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const Me=a.get(bt[Dt]);Me.__webglTexture===void 0&&(Me.__webglTexture=s.createTexture(),f.memory.textures++)}if(L.samples>0&&Se(L)===!1){at.__webglMultisampledFramebuffer=s.createFramebuffer(),at.__webglColorRenderbuffer=[],n.bindFramebuffer(s.FRAMEBUFFER,at.__webglMultisampledFramebuffer);for(let Dt=0;Dt<bt.length;Dt++){const Bt=bt[Dt];at.__webglColorRenderbuffer[Dt]=s.createRenderbuffer(),s.bindRenderbuffer(s.RENDERBUFFER,at.__webglColorRenderbuffer[Dt]);const Me=c.convert(Bt.format,Bt.colorSpace),Ct=c.convert(Bt.type),Ht=N(Bt.internalFormat,Me,Ct,Bt.colorSpace,L.isXRRenderTarget===!0),Zt=me(L);s.renderbufferStorageMultisample(s.RENDERBUFFER,Zt,Ht,L.width,L.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Dt,s.RENDERBUFFER,at.__webglColorRenderbuffer[Dt])}s.bindRenderbuffer(s.RENDERBUFFER,null),L.depthBuffer&&(at.__webglDepthRenderbuffer=s.createRenderbuffer(),Mt(at.__webglDepthRenderbuffer,L,!0)),n.bindFramebuffer(s.FRAMEBUFFER,null)}}if(vt){n.bindTexture(s.TEXTURE_CUBE_MAP,pt.__webglTexture),nt(s.TEXTURE_CUBE_MAP,A);for(let Dt=0;Dt<6;Dt++)if(A.mipmaps&&A.mipmaps.length>0)for(let Bt=0;Bt<A.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Dt][Bt],L,A,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,Bt);else Tt(at.__webglFramebuffer[Dt],L,A,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,0);M(A)&&_(s.TEXTURE_CUBE_MAP),n.unbindTexture()}else if(jt){for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const Me=bt[Dt],Ct=a.get(Me);n.bindTexture(s.TEXTURE_2D,Ct.__webglTexture),nt(s.TEXTURE_2D,Me),Tt(at.__webglFramebuffer,L,Me,s.COLOR_ATTACHMENT0+Dt,s.TEXTURE_2D,0),M(Me)&&_(s.TEXTURE_2D)}n.unbindTexture()}else{let Dt=s.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(Dt=L.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),n.bindTexture(Dt,pt.__webglTexture),nt(Dt,A),A.mipmaps&&A.mipmaps.length>0)for(let Bt=0;Bt<A.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Bt],L,A,s.COLOR_ATTACHMENT0,Dt,Bt);else Tt(at.__webglFramebuffer,L,A,s.COLOR_ATTACHMENT0,Dt,0);M(A)&&_(Dt),n.unbindTexture()}L.depthBuffer&&Vt(L)}function ve(L){const A=L.textures;for(let at=0,pt=A.length;at<pt;at++){const bt=A[at];if(M(bt)){const vt=I(L),jt=a.get(bt).__webglTexture;n.bindTexture(vt,jt),_(vt),n.unbindTexture()}}}const Je=[],k=[];function Pn(L){if(L.samples>0){if(Se(L)===!1){const A=L.textures,at=L.width,pt=L.height;let bt=s.COLOR_BUFFER_BIT;const vt=L.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,jt=a.get(L),Dt=A.length>1;if(Dt)for(let Bt=0;Bt<A.length;Bt++)n.bindFramebuffer(s.FRAMEBUFFER,jt.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Bt,s.RENDERBUFFER,null),n.bindFramebuffer(s.FRAMEBUFFER,jt.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Bt,s.TEXTURE_2D,null,0);n.bindFramebuffer(s.READ_FRAMEBUFFER,jt.__webglMultisampledFramebuffer),n.bindFramebuffer(s.DRAW_FRAMEBUFFER,jt.__webglFramebuffer);for(let Bt=0;Bt<A.length;Bt++){if(L.resolveDepthBuffer&&(L.depthBuffer&&(bt|=s.DEPTH_BUFFER_BIT),L.stencilBuffer&&L.resolveStencilBuffer&&(bt|=s.STENCIL_BUFFER_BIT)),Dt){s.framebufferRenderbuffer(s.READ_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.RENDERBUFFER,jt.__webglColorRenderbuffer[Bt]);const Me=a.get(A[Bt]).__webglTexture;s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,Me,0)}s.blitFramebuffer(0,0,at,pt,0,0,at,pt,bt,s.NEAREST),p===!0&&(Je.length=0,k.length=0,Je.push(s.COLOR_ATTACHMENT0+Bt),L.depthBuffer&&L.resolveDepthBuffer===!1&&(Je.push(vt),k.push(vt),s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,k)),s.invalidateFramebuffer(s.READ_FRAMEBUFFER,Je))}if(n.bindFramebuffer(s.READ_FRAMEBUFFER,null),n.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),Dt)for(let Bt=0;Bt<A.length;Bt++){n.bindFramebuffer(s.FRAMEBUFFER,jt.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+Bt,s.RENDERBUFFER,jt.__webglColorRenderbuffer[Bt]);const Me=a.get(A[Bt]).__webglTexture;n.bindFramebuffer(s.FRAMEBUFFER,jt.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+Bt,s.TEXTURE_2D,Me,0)}n.bindFramebuffer(s.DRAW_FRAMEBUFFER,jt.__webglMultisampledFramebuffer)}else if(L.depthBuffer&&L.resolveDepthBuffer===!1&&p){const A=L.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,[A])}}}function me(L){return Math.min(l.maxSamples,L.samples)}function Se(L){const A=a.get(L);return L.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&A.__useRenderToTexture!==!1}function Qt(L){const A=f.render.frame;g.get(L)!==A&&(g.set(L,A),L.update())}function Ie(L,A){const at=L.colorSpace,pt=L.format,bt=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||at!==Fo&&at!==ms&&(Oe.getTransfer(at)===je?(pt!==Fi||bt!==Pa)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",at)),A}function Yt(L){return typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement?(m.width=L.naturalWidth||L.width,m.height=L.naturalHeight||L.height):typeof VideoFrame<"u"&&L instanceof VideoFrame?(m.width=L.displayWidth,m.height=L.displayHeight):(m.width=L.width,m.height=L.height),m}this.allocateTextureUnit=ot,this.resetTextureUnits=ut,this.setTexture2D=ct,this.setTexture2DArray=z,this.setTexture3D=Z,this.setTextureCube=$,this.rebindTextures=re,this.setupRenderTarget=He,this.updateRenderTargetMipmap=ve,this.updateMultisampleRenderTarget=Pn,this.setupDepthRenderbuffer=Vt,this.setupFrameBufferTexture=Tt,this.useMultisampledRTT=Se}function nw(s,t){function n(a,l=ms){let c;const f=Oe.getTransfer(l);if(a===Pa)return s.UNSIGNED_BYTE;if(a===vm)return s.UNSIGNED_SHORT_4_4_4_4;if(a===_m)return s.UNSIGNED_SHORT_5_5_5_1;if(a===_x)return s.UNSIGNED_INT_5_9_9_9_REV;if(a===gx)return s.BYTE;if(a===vx)return s.SHORT;if(a===tc)return s.UNSIGNED_SHORT;if(a===gm)return s.INT;if(a===gr)return s.UNSIGNED_INT;if(a===Da)return s.FLOAT;if(a===La)return s.HALF_FLOAT;if(a===yx)return s.ALPHA;if(a===xx)return s.RGB;if(a===Fi)return s.RGBA;if(a===Sx)return s.LUMINANCE;if(a===Mx)return s.LUMINANCE_ALPHA;if(a===_o)return s.DEPTH_COMPONENT;if(a===Bo)return s.DEPTH_STENCIL;if(a===Ex)return s.RED;if(a===ym)return s.RED_INTEGER;if(a===bx)return s.RG;if(a===xm)return s.RG_INTEGER;if(a===Sm)return s.RGBA_INTEGER;if(a===Yu||a===Qu||a===Zu||a===Ku)if(f===je)if(c=t.get("WEBGL_compressed_texture_s3tc_srgb"),c!==null){if(a===Yu)return c.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(a===Qu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(a===Zu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(a===Ku)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(c=t.get("WEBGL_compressed_texture_s3tc"),c!==null){if(a===Yu)return c.COMPRESSED_RGB_S3TC_DXT1_EXT;if(a===Qu)return c.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(a===Zu)return c.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(a===Ku)return c.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(a===Op||a===Pp||a===zp||a===Ip)if(c=t.get("WEBGL_compressed_texture_pvrtc"),c!==null){if(a===Op)return c.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(a===Pp)return c.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(a===zp)return c.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(a===Ip)return c.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(a===Bp||a===Fp||a===Hp)if(c=t.get("WEBGL_compressed_texture_etc"),c!==null){if(a===Bp||a===Fp)return f===je?c.COMPRESSED_SRGB8_ETC2:c.COMPRESSED_RGB8_ETC2;if(a===Hp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:c.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(a===Gp||a===Vp||a===kp||a===Xp||a===jp||a===qp||a===Wp||a===Yp||a===Qp||a===Zp||a===Kp||a===Jp||a===$p||a===tm)if(c=t.get("WEBGL_compressed_texture_astc"),c!==null){if(a===Gp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:c.COMPRESSED_RGBA_ASTC_4x4_KHR;if(a===Vp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:c.COMPRESSED_RGBA_ASTC_5x4_KHR;if(a===kp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:c.COMPRESSED_RGBA_ASTC_5x5_KHR;if(a===Xp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:c.COMPRESSED_RGBA_ASTC_6x5_KHR;if(a===jp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:c.COMPRESSED_RGBA_ASTC_6x6_KHR;if(a===qp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:c.COMPRESSED_RGBA_ASTC_8x5_KHR;if(a===Wp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:c.COMPRESSED_RGBA_ASTC_8x6_KHR;if(a===Yp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:c.COMPRESSED_RGBA_ASTC_8x8_KHR;if(a===Qp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:c.COMPRESSED_RGBA_ASTC_10x5_KHR;if(a===Zp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:c.COMPRESSED_RGBA_ASTC_10x6_KHR;if(a===Kp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:c.COMPRESSED_RGBA_ASTC_10x8_KHR;if(a===Jp)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:c.COMPRESSED_RGBA_ASTC_10x10_KHR;if(a===$p)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:c.COMPRESSED_RGBA_ASTC_12x10_KHR;if(a===tm)return f===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:c.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(a===Ju||a===em||a===nm)if(c=t.get("EXT_texture_compression_bptc"),c!==null){if(a===Ju)return f===je?c.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:c.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(a===em)return c.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(a===nm)return c.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(a===Tx||a===im||a===am||a===sm)if(c=t.get("EXT_texture_compression_rgtc"),c!==null){if(a===Ju)return c.COMPRESSED_RED_RGTC1_EXT;if(a===im)return c.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(a===am)return c.COMPRESSED_RED_GREEN_RGTC2_EXT;if(a===sm)return c.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return a===Io?s.UNSIGNED_INT_24_8:s[a]!==void 0?s[a]:null}return{convert:n}}const iw={type:"move"};class ap{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new mo,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new mo,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new W,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new W),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new mo,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new W,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new W),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const n=this._hand;if(n)for(const a of t.hand.values())this._getHandJoint(n,a)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,n,a){let l=null,c=null,f=null;const d=this._targetRay,p=this._grip,m=this._hand;if(t&&n.session.visibilityState!=="visible-blurred"){if(m&&t.hand){f=!0;for(const b of t.hand.values()){const M=n.getJointPose(b,a),_=this._getHandJoint(m,b);M!==null&&(_.matrix.fromArray(M.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=M.radius),_.visible=M!==null}const g=m.joints["index-finger-tip"],v=m.joints["thumb-tip"],y=g.position.distanceTo(v.position),x=.02,E=.005;m.inputState.pinching&&y>x+E?(m.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!m.inputState.pinching&&y<=x-E&&(m.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else p!==null&&t.gripSpace&&(c=n.getPose(t.gripSpace,a),c!==null&&(p.matrix.fromArray(c.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,c.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(c.linearVelocity)):p.hasLinearVelocity=!1,c.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(c.angularVelocity)):p.hasAngularVelocity=!1));d!==null&&(l=n.getPose(t.targetRaySpace,a),l===null&&c!==null&&(l=c),l!==null&&(d.matrix.fromArray(l.transform.matrix),d.matrix.decompose(d.position,d.rotation,d.scale),d.matrixWorldNeedsUpdate=!0,l.linearVelocity?(d.hasLinearVelocity=!0,d.linearVelocity.copy(l.linearVelocity)):d.hasLinearVelocity=!1,l.angularVelocity?(d.hasAngularVelocity=!0,d.angularVelocity.copy(l.angularVelocity)):d.hasAngularVelocity=!1,this.dispatchEvent(iw)))}return d!==null&&(d.visible=l!==null),p!==null&&(p.visible=c!==null),m!==null&&(m.visible=f!==null),this}_getHandJoint(t,n){if(t.joints[n.jointName]===void 0){const a=new mo;a.matrixAutoUpdate=!1,a.visible=!1,t.joints[n.jointName]=a,t.add(a)}return t.joints[n.jointName]}}const aw=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,sw=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class rw{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,n,a){if(this.texture===null){const l=new ai,c=t.properties.get(l);c.__webglTexture=n.texture,(n.depthNear!=a.depthNear||n.depthFar!=a.depthFar)&&(this.depthNear=n.depthNear,this.depthFar=n.depthFar),this.texture=l}}getMesh(t){if(this.texture!==null&&this.mesh===null){const n=t.cameras[0].viewport,a=new Yn({vertexShader:aw,fragmentShader:sw,uniforms:{depthColor:{value:this.texture},depthWidth:{value:n.z},depthHeight:{value:n.w}}});this.mesh=new Wn(new uf(20,20),a)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class ow extends Vo{constructor(t,n){super();const a=this;let l=null,c=1,f=null,d="local-floor",p=1,m=null,g=null,v=null,y=null,x=null,E=null;const b=new rw,M=n.getContextAttributes();let _=null,I=null;const N=[],C=[],V=new Wt;let F=null;const P=new _i;P.viewport=new qe;const G=new _i;G.viewport=new qe;const U=[P,G],w=new RT;let H=null,ut=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(q){let ft=N[q];return ft===void 0&&(ft=new ap,N[q]=ft),ft.getTargetRaySpace()},this.getControllerGrip=function(q){let ft=N[q];return ft===void 0&&(ft=new ap,N[q]=ft),ft.getGripSpace()},this.getHand=function(q){let ft=N[q];return ft===void 0&&(ft=new ap,N[q]=ft),ft.getHandSpace()};function ot(q){const ft=C.indexOf(q.inputSource);if(ft===-1)return;const Tt=N[ft];Tt!==void 0&&(Tt.update(q.inputSource,q.frame,m||f),Tt.dispatchEvent({type:q.type,data:q.inputSource}))}function mt(){l.removeEventListener("select",ot),l.removeEventListener("selectstart",ot),l.removeEventListener("selectend",ot),l.removeEventListener("squeeze",ot),l.removeEventListener("squeezestart",ot),l.removeEventListener("squeezeend",ot),l.removeEventListener("end",mt),l.removeEventListener("inputsourceschange",ct);for(let q=0;q<N.length;q++){const ft=C[q];ft!==null&&(C[q]=null,N[q].disconnect(ft))}H=null,ut=null,b.reset(),t.setRenderTarget(_),x=null,y=null,v=null,l=null,I=null,St.stop(),a.isPresenting=!1,t.setPixelRatio(F),t.setSize(V.width,V.height,!1),a.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(q){c=q,a.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(q){d=q,a.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return m||f},this.setReferenceSpace=function(q){m=q},this.getBaseLayer=function(){return y!==null?y:x},this.getBinding=function(){return v},this.getFrame=function(){return E},this.getSession=function(){return l},this.setSession=async function(q){if(l=q,l!==null){if(_=t.getRenderTarget(),l.addEventListener("select",ot),l.addEventListener("selectstart",ot),l.addEventListener("selectend",ot),l.addEventListener("squeeze",ot),l.addEventListener("squeezestart",ot),l.addEventListener("squeezeend",ot),l.addEventListener("end",mt),l.addEventListener("inputsourceschange",ct),M.xrCompatible!==!0&&await n.makeXRCompatible(),F=t.getPixelRatio(),t.getSize(V),l.renderState.layers===void 0){const ft={antialias:M.antialias,alpha:!0,depth:M.depth,stencil:M.stencil,framebufferScaleFactor:c};x=new XRWebGLLayer(l,n,ft),l.updateRenderState({baseLayer:x}),t.setPixelRatio(1),t.setSize(x.framebufferWidth,x.framebufferHeight,!1),I=new Gi(x.framebufferWidth,x.framebufferHeight,{format:Fi,type:Pa,colorSpace:t.outputColorSpace,stencilBuffer:M.stencil})}else{let ft=null,Tt=null,Mt=null;M.depth&&(Mt=M.stencil?n.DEPTH24_STENCIL8:n.DEPTH_COMPONENT24,ft=M.stencil?Bo:_o,Tt=M.stencil?Io:gr);const Ft={colorFormat:n.RGBA8,depthFormat:Mt,scaleFactor:c};v=new XRWebGLBinding(l,n),y=v.createProjectionLayer(Ft),l.updateRenderState({layers:[y]}),t.setPixelRatio(1),t.setSize(y.textureWidth,y.textureHeight,!1),I=new Gi(y.textureWidth,y.textureHeight,{format:Fi,type:Pa,depthTexture:new Ix(y.textureWidth,y.textureHeight,Tt,void 0,void 0,void 0,void 0,void 0,void 0,ft),stencilBuffer:M.stencil,colorSpace:t.outputColorSpace,samples:M.antialias?4:0,resolveDepthBuffer:y.ignoreDepthValues===!1})}I.isXRRenderTarget=!0,this.setFoveation(p),m=null,f=await l.requestReferenceSpace(d),St.setContext(l),St.start(),a.isPresenting=!0,a.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(l!==null)return l.environmentBlendMode},this.getDepthTexture=function(){return b.getDepthTexture()};function ct(q){for(let ft=0;ft<q.removed.length;ft++){const Tt=q.removed[ft],Mt=C.indexOf(Tt);Mt>=0&&(C[Mt]=null,N[Mt].disconnect(Tt))}for(let ft=0;ft<q.added.length;ft++){const Tt=q.added[ft];let Mt=C.indexOf(Tt);if(Mt===-1){for(let Vt=0;Vt<N.length;Vt++)if(Vt>=C.length){C.push(Tt),Mt=Vt;break}else if(C[Vt]===null){C[Vt]=Tt,Mt=Vt;break}if(Mt===-1)break}const Ft=N[Mt];Ft&&Ft.connect(Tt)}}const z=new W,Z=new W;function $(q,ft,Tt){z.setFromMatrixPosition(ft.matrixWorld),Z.setFromMatrixPosition(Tt.matrixWorld);const Mt=z.distanceTo(Z),Ft=ft.projectionMatrix.elements,Vt=Tt.projectionMatrix.elements,re=Ft[14]/(Ft[10]-1),He=Ft[14]/(Ft[10]+1),ve=(Ft[9]+1)/Ft[5],Je=(Ft[9]-1)/Ft[5],k=(Ft[8]-1)/Ft[0],Pn=(Vt[8]+1)/Vt[0],me=re*k,Se=re*Pn,Qt=Mt/(-k+Pn),Ie=Qt*-k;if(ft.matrixWorld.decompose(q.position,q.quaternion,q.scale),q.translateX(Ie),q.translateZ(Qt),q.matrixWorld.compose(q.position,q.quaternion,q.scale),q.matrixWorldInverse.copy(q.matrixWorld).invert(),Ft[10]===-1)q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse);else{const Yt=re+Qt,L=He+Qt,A=me-Ie,at=Se+(Mt-Ie),pt=ve*He/L*Yt,bt=Je*He/L*Yt;q.projectionMatrix.makePerspective(A,at,pt,bt,Yt,L),q.projectionMatrixInverse.copy(q.projectionMatrix).invert()}}function Et(q,ft){ft===null?q.matrixWorld.copy(q.matrix):q.matrixWorld.multiplyMatrices(ft.matrixWorld,q.matrix),q.matrixWorldInverse.copy(q.matrixWorld).invert()}this.updateCamera=function(q){if(l===null)return;let ft=q.near,Tt=q.far;b.texture!==null&&(b.depthNear>0&&(ft=b.depthNear),b.depthFar>0&&(Tt=b.depthFar)),w.near=G.near=P.near=ft,w.far=G.far=P.far=Tt,(H!==w.near||ut!==w.far)&&(l.updateRenderState({depthNear:w.near,depthFar:w.far}),H=w.near,ut=w.far),P.layers.mask=q.layers.mask|2,G.layers.mask=q.layers.mask|4,w.layers.mask=P.layers.mask|G.layers.mask;const Mt=q.parent,Ft=w.cameras;Et(w,Mt);for(let Vt=0;Vt<Ft.length;Vt++)Et(Ft[Vt],Mt);Ft.length===2?$(w,P,G):w.projectionMatrix.copy(P.projectionMatrix),At(q,w,Mt)};function At(q,ft,Tt){Tt===null?q.matrix.copy(ft.matrixWorld):(q.matrix.copy(Tt.matrixWorld),q.matrix.invert(),q.matrix.multiply(ft.matrixWorld)),q.matrix.decompose(q.position,q.quaternion,q.scale),q.updateMatrixWorld(!0),q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse),q.isPerspectiveCamera&&(q.fov=ec*2*Math.atan(1/q.projectionMatrix.elements[5]),q.zoom=1)}this.getCamera=function(){return w},this.getFoveation=function(){if(!(y===null&&x===null))return p},this.setFoveation=function(q){p=q,y!==null&&(y.fixedFoveation=q),x!==null&&x.fixedFoveation!==void 0&&(x.fixedFoveation=q)},this.hasDepthSensing=function(){return b.texture!==null},this.getDepthSensingMesh=function(){return b.getMesh(w)};let O=null;function nt(q,ft){if(g=ft.getViewerPose(m||f),E=ft,g!==null){const Tt=g.views;x!==null&&(t.setRenderTargetFramebuffer(I,x.framebuffer),t.setRenderTarget(I));let Mt=!1;Tt.length!==w.cameras.length&&(w.cameras.length=0,Mt=!0);for(let Vt=0;Vt<Tt.length;Vt++){const re=Tt[Vt];let He=null;if(x!==null)He=x.getViewport(re);else{const Je=v.getViewSubImage(y,re);He=Je.viewport,Vt===0&&(t.setRenderTargetTextures(I,Je.colorTexture,y.ignoreDepthValues?void 0:Je.depthStencilTexture),t.setRenderTarget(I))}let ve=U[Vt];ve===void 0&&(ve=new _i,ve.layers.enable(Vt),ve.viewport=new qe,U[Vt]=ve),ve.matrix.fromArray(re.transform.matrix),ve.matrix.decompose(ve.position,ve.quaternion,ve.scale),ve.projectionMatrix.fromArray(re.projectionMatrix),ve.projectionMatrixInverse.copy(ve.projectionMatrix).invert(),ve.viewport.set(He.x,He.y,He.width,He.height),Vt===0&&(w.matrix.copy(ve.matrix),w.matrix.decompose(w.position,w.quaternion,w.scale)),Mt===!0&&w.cameras.push(ve)}const Ft=l.enabledFeatures;if(Ft&&Ft.includes("depth-sensing")){const Vt=v.getDepthInformation(Tt[0]);Vt&&Vt.isValid&&Vt.texture&&b.init(t,Vt,l.renderState)}}for(let Tt=0;Tt<N.length;Tt++){const Mt=C[Tt],Ft=N[Tt];Mt!==null&&Ft!==void 0&&Ft.update(Mt,ft,m||f)}O&&O(q,ft),ft.detectedPlanes&&a.dispatchEvent({type:"planesdetected",data:ft}),E=null}const St=new Xx;St.setAnimationLoop(nt),this.setAnimationLoop=function(q){O=q},this.dispose=function(){}}}const Js=new za,lw=new nn;function cw(s,t){function n(M,_){M.matrixAutoUpdate===!0&&M.updateMatrix(),_.value.copy(M.matrix)}function a(M,_){_.color.getRGB(M.fogColor.value,Ox(s)),_.isFog?(M.fogNear.value=_.near,M.fogFar.value=_.far):_.isFogExp2&&(M.fogDensity.value=_.density)}function l(M,_,I,N,C){_.isMeshBasicMaterial||_.isMeshLambertMaterial?c(M,_):_.isMeshToonMaterial?(c(M,_),v(M,_)):_.isMeshPhongMaterial?(c(M,_),g(M,_)):_.isMeshStandardMaterial?(c(M,_),y(M,_),_.isMeshPhysicalMaterial&&x(M,_,C)):_.isMeshMatcapMaterial?(c(M,_),E(M,_)):_.isMeshDepthMaterial?c(M,_):_.isMeshDistanceMaterial?(c(M,_),b(M,_)):_.isMeshNormalMaterial?c(M,_):_.isLineBasicMaterial?(f(M,_),_.isLineDashedMaterial&&d(M,_)):_.isPointsMaterial?p(M,_,I,N):_.isSpriteMaterial?m(M,_):_.isShadowMaterial?(M.color.value.copy(_.color),M.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function c(M,_){M.opacity.value=_.opacity,_.color&&M.diffuse.value.copy(_.color),_.emissive&&M.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(M.map.value=_.map,n(_.map,M.mapTransform)),_.alphaMap&&(M.alphaMap.value=_.alphaMap,n(_.alphaMap,M.alphaMapTransform)),_.bumpMap&&(M.bumpMap.value=_.bumpMap,n(_.bumpMap,M.bumpMapTransform),M.bumpScale.value=_.bumpScale,_.side===ii&&(M.bumpScale.value*=-1)),_.normalMap&&(M.normalMap.value=_.normalMap,n(_.normalMap,M.normalMapTransform),M.normalScale.value.copy(_.normalScale),_.side===ii&&M.normalScale.value.negate()),_.displacementMap&&(M.displacementMap.value=_.displacementMap,n(_.displacementMap,M.displacementMapTransform),M.displacementScale.value=_.displacementScale,M.displacementBias.value=_.displacementBias),_.emissiveMap&&(M.emissiveMap.value=_.emissiveMap,n(_.emissiveMap,M.emissiveMapTransform)),_.specularMap&&(M.specularMap.value=_.specularMap,n(_.specularMap,M.specularMapTransform)),_.alphaTest>0&&(M.alphaTest.value=_.alphaTest);const I=t.get(_),N=I.envMap,C=I.envMapRotation;N&&(M.envMap.value=N,Js.copy(C),Js.x*=-1,Js.y*=-1,Js.z*=-1,N.isCubeTexture&&N.isRenderTargetTexture===!1&&(Js.y*=-1,Js.z*=-1),M.envMapRotation.value.setFromMatrix4(lw.makeRotationFromEuler(Js)),M.flipEnvMap.value=N.isCubeTexture&&N.isRenderTargetTexture===!1?-1:1,M.reflectivity.value=_.reflectivity,M.ior.value=_.ior,M.refractionRatio.value=_.refractionRatio),_.lightMap&&(M.lightMap.value=_.lightMap,M.lightMapIntensity.value=_.lightMapIntensity,n(_.lightMap,M.lightMapTransform)),_.aoMap&&(M.aoMap.value=_.aoMap,M.aoMapIntensity.value=_.aoMapIntensity,n(_.aoMap,M.aoMapTransform))}function f(M,_){M.diffuse.value.copy(_.color),M.opacity.value=_.opacity,_.map&&(M.map.value=_.map,n(_.map,M.mapTransform))}function d(M,_){M.dashSize.value=_.dashSize,M.totalSize.value=_.dashSize+_.gapSize,M.scale.value=_.scale}function p(M,_,I,N){M.diffuse.value.copy(_.color),M.opacity.value=_.opacity,M.size.value=_.size*I,M.scale.value=N*.5,_.map&&(M.map.value=_.map,n(_.map,M.uvTransform)),_.alphaMap&&(M.alphaMap.value=_.alphaMap,n(_.alphaMap,M.alphaMapTransform)),_.alphaTest>0&&(M.alphaTest.value=_.alphaTest)}function m(M,_){M.diffuse.value.copy(_.color),M.opacity.value=_.opacity,M.rotation.value=_.rotation,_.map&&(M.map.value=_.map,n(_.map,M.mapTransform)),_.alphaMap&&(M.alphaMap.value=_.alphaMap,n(_.alphaMap,M.alphaMapTransform)),_.alphaTest>0&&(M.alphaTest.value=_.alphaTest)}function g(M,_){M.specular.value.copy(_.specular),M.shininess.value=Math.max(_.shininess,1e-4)}function v(M,_){_.gradientMap&&(M.gradientMap.value=_.gradientMap)}function y(M,_){M.metalness.value=_.metalness,_.metalnessMap&&(M.metalnessMap.value=_.metalnessMap,n(_.metalnessMap,M.metalnessMapTransform)),M.roughness.value=_.roughness,_.roughnessMap&&(M.roughnessMap.value=_.roughnessMap,n(_.roughnessMap,M.roughnessMapTransform)),_.envMap&&(M.envMapIntensity.value=_.envMapIntensity)}function x(M,_,I){M.ior.value=_.ior,_.sheen>0&&(M.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),M.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(M.sheenColorMap.value=_.sheenColorMap,n(_.sheenColorMap,M.sheenColorMapTransform)),_.sheenRoughnessMap&&(M.sheenRoughnessMap.value=_.sheenRoughnessMap,n(_.sheenRoughnessMap,M.sheenRoughnessMapTransform))),_.clearcoat>0&&(M.clearcoat.value=_.clearcoat,M.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(M.clearcoatMap.value=_.clearcoatMap,n(_.clearcoatMap,M.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(M.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,n(_.clearcoatRoughnessMap,M.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(M.clearcoatNormalMap.value=_.clearcoatNormalMap,n(_.clearcoatNormalMap,M.clearcoatNormalMapTransform),M.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===ii&&M.clearcoatNormalScale.value.negate())),_.dispersion>0&&(M.dispersion.value=_.dispersion),_.iridescence>0&&(M.iridescence.value=_.iridescence,M.iridescenceIOR.value=_.iridescenceIOR,M.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],M.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(M.iridescenceMap.value=_.iridescenceMap,n(_.iridescenceMap,M.iridescenceMapTransform)),_.iridescenceThicknessMap&&(M.iridescenceThicknessMap.value=_.iridescenceThicknessMap,n(_.iridescenceThicknessMap,M.iridescenceThicknessMapTransform))),_.transmission>0&&(M.transmission.value=_.transmission,M.transmissionSamplerMap.value=I.texture,M.transmissionSamplerSize.value.set(I.width,I.height),_.transmissionMap&&(M.transmissionMap.value=_.transmissionMap,n(_.transmissionMap,M.transmissionMapTransform)),M.thickness.value=_.thickness,_.thicknessMap&&(M.thicknessMap.value=_.thicknessMap,n(_.thicknessMap,M.thicknessMapTransform)),M.attenuationDistance.value=_.attenuationDistance,M.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(M.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(M.anisotropyMap.value=_.anisotropyMap,n(_.anisotropyMap,M.anisotropyMapTransform))),M.specularIntensity.value=_.specularIntensity,M.specularColor.value.copy(_.specularColor),_.specularColorMap&&(M.specularColorMap.value=_.specularColorMap,n(_.specularColorMap,M.specularColorMapTransform)),_.specularIntensityMap&&(M.specularIntensityMap.value=_.specularIntensityMap,n(_.specularIntensityMap,M.specularIntensityMapTransform))}function E(M,_){_.matcap&&(M.matcap.value=_.matcap)}function b(M,_){const I=t.get(_).light;M.referencePosition.value.setFromMatrixPosition(I.matrixWorld),M.nearDistance.value=I.shadow.camera.near,M.farDistance.value=I.shadow.camera.far}return{refreshFogUniforms:a,refreshMaterialUniforms:l}}function uw(s,t,n,a){let l={},c={},f=[];const d=s.getParameter(s.MAX_UNIFORM_BUFFER_BINDINGS);function p(I,N){const C=N.program;a.uniformBlockBinding(I,C)}function m(I,N){let C=l[I.id];C===void 0&&(E(I),C=g(I),l[I.id]=C,I.addEventListener("dispose",M));const V=N.program;a.updateUBOMapping(I,V);const F=t.render.frame;c[I.id]!==F&&(y(I),c[I.id]=F)}function g(I){const N=v();I.__bindingPointIndex=N;const C=s.createBuffer(),V=I.__size,F=I.usage;return s.bindBuffer(s.UNIFORM_BUFFER,C),s.bufferData(s.UNIFORM_BUFFER,V,F),s.bindBuffer(s.UNIFORM_BUFFER,null),s.bindBufferBase(s.UNIFORM_BUFFER,N,C),C}function v(){for(let I=0;I<d;I++)if(f.indexOf(I)===-1)return f.push(I),I;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function y(I){const N=l[I.id],C=I.uniforms,V=I.__cache;s.bindBuffer(s.UNIFORM_BUFFER,N);for(let F=0,P=C.length;F<P;F++){const G=Array.isArray(C[F])?C[F]:[C[F]];for(let U=0,w=G.length;U<w;U++){const H=G[U];if(x(H,F,U,V)===!0){const ut=H.__offset,ot=Array.isArray(H.value)?H.value:[H.value];let mt=0;for(let ct=0;ct<ot.length;ct++){const z=ot[ct],Z=b(z);typeof z=="number"||typeof z=="boolean"?(H.__data[0]=z,s.bufferSubData(s.UNIFORM_BUFFER,ut+mt,H.__data)):z.isMatrix3?(H.__data[0]=z.elements[0],H.__data[1]=z.elements[1],H.__data[2]=z.elements[2],H.__data[3]=0,H.__data[4]=z.elements[3],H.__data[5]=z.elements[4],H.__data[6]=z.elements[5],H.__data[7]=0,H.__data[8]=z.elements[6],H.__data[9]=z.elements[7],H.__data[10]=z.elements[8],H.__data[11]=0):(z.toArray(H.__data,mt),mt+=Z.storage/Float32Array.BYTES_PER_ELEMENT)}s.bufferSubData(s.UNIFORM_BUFFER,ut,H.__data)}}}s.bindBuffer(s.UNIFORM_BUFFER,null)}function x(I,N,C,V){const F=I.value,P=N+"_"+C;if(V[P]===void 0)return typeof F=="number"||typeof F=="boolean"?V[P]=F:V[P]=F.clone(),!0;{const G=V[P];if(typeof F=="number"||typeof F=="boolean"){if(G!==F)return V[P]=F,!0}else if(G.equals(F)===!1)return G.copy(F),!0}return!1}function E(I){const N=I.uniforms;let C=0;const V=16;for(let P=0,G=N.length;P<G;P++){const U=Array.isArray(N[P])?N[P]:[N[P]];for(let w=0,H=U.length;w<H;w++){const ut=U[w],ot=Array.isArray(ut.value)?ut.value:[ut.value];for(let mt=0,ct=ot.length;mt<ct;mt++){const z=ot[mt],Z=b(z),$=C%V,Et=$%Z.boundary,At=$+Et;C+=Et,At!==0&&V-At<Z.storage&&(C+=V-At),ut.__data=new Float32Array(Z.storage/Float32Array.BYTES_PER_ELEMENT),ut.__offset=C,C+=Z.storage}}}const F=C%V;return F>0&&(C+=V-F),I.__size=C,I.__cache={},this}function b(I){const N={boundary:0,storage:0};return typeof I=="number"||typeof I=="boolean"?(N.boundary=4,N.storage=4):I.isVector2?(N.boundary=8,N.storage=8):I.isVector3||I.isColor?(N.boundary=16,N.storage=12):I.isVector4?(N.boundary=16,N.storage=16):I.isMatrix3?(N.boundary=48,N.storage=48):I.isMatrix4?(N.boundary=64,N.storage=64):I.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",I),N}function M(I){const N=I.target;N.removeEventListener("dispose",M);const C=f.indexOf(N.__bindingPointIndex);f.splice(C,1),s.deleteBuffer(l[N.id]),delete l[N.id],delete c[N.id]}function _(){for(const I in l)s.deleteBuffer(l[I]);f=[],l={},c={}}return{bind:p,update:m,dispose:_}}class fw{constructor(t={}){const{canvas:n=Nb(),context:a=null,depth:l=!0,stencil:c=!1,alpha:f=!1,antialias:d=!1,premultipliedAlpha:p=!0,preserveDrawingBuffer:m=!1,powerPreference:g="default",failIfMajorPerformanceCaveat:v=!1,reverseDepthBuffer:y=!1}=t;this.isWebGLRenderer=!0;let x;if(a!==null){if(typeof WebGLRenderingContext<"u"&&a instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");x=a.getContextAttributes().alpha}else x=f;const E=new Uint32Array(4),b=new Int32Array(4);let M=null,_=null;const I=[],N=[];this.domElement=n,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=vi,this.toneMapping=Ts,this.toneMappingExposure=1;const C=this;let V=!1,F=0,P=0,G=null,U=-1,w=null;const H=new qe,ut=new qe;let ot=null;const mt=new de(0);let ct=0,z=n.width,Z=n.height,$=1,Et=null,At=null;const O=new qe(0,0,z,Z),nt=new qe(0,0,z,Z);let St=!1;const q=new bm;let ft=!1,Tt=!1;const Mt=new nn,Ft=new nn,Vt=new W,re=new qe,He={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ve=!1;function Je(){return G===null?$:1}let k=a;function Pn(R,Q){return n.getContext(R,Q)}try{const R={alpha:!0,depth:l,stencil:c,antialias:d,premultipliedAlpha:p,preserveDrawingBuffer:m,powerPreference:g,failIfMajorPerformanceCaveat:v};if("setAttribute"in n&&n.setAttribute("data-engine",`three.js r${mm}`),n.addEventListener("webglcontextlost",yt,!1),n.addEventListener("webglcontextrestored",wt,!1),n.addEventListener("webglcontextcreationerror",Ut,!1),k===null){const Q="webgl2";if(k=Pn(Q,R),k===null)throw Pn(Q)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(R){throw console.error("THREE.WebGLRenderer: "+R.message),R}let me,Se,Qt,Ie,Yt,L,A,at,pt,bt,vt,jt,Dt,Bt,Me,Ct,Ht,Zt,qt,Ot,ne,oe,Ge,Y;function Rt(){me=new xC(k),me.init(),oe=new nw(k,me),Se=new pC(k,me,t,oe),Qt=new tw(k,me),Se.reverseDepthBuffer&&y&&Qt.buffers.depth.setReversed(!0),Ie=new EC(k),Yt=new GR,L=new ew(k,me,Qt,Yt,Se,oe,Ie),A=new gC(C),at=new yC(C),pt=new DT(k),Ge=new hC(k,pt),bt=new SC(k,pt,Ie,Ge),vt=new TC(k,bt,pt,Ie),qt=new bC(k,Se,L),Ct=new mC(Yt),jt=new HR(C,A,at,me,Se,Ge,Ct),Dt=new cw(C,Yt),Bt=new kR,Me=new QR(me),Zt=new fC(C,A,at,Qt,vt,x,p),Ht=new JR(C,vt,Se),Y=new uw(k,Ie,Se,Qt),Ot=new dC(k,me,Ie),ne=new MC(k,me,Ie),Ie.programs=jt.programs,C.capabilities=Se,C.extensions=me,C.properties=Yt,C.renderLists=Bt,C.shadowMap=Ht,C.state=Qt,C.info=Ie}Rt();const ht=new ow(C,k);this.xr=ht,this.getContext=function(){return k},this.getContextAttributes=function(){return k.getContextAttributes()},this.forceContextLoss=function(){const R=me.get("WEBGL_lose_context");R&&R.loseContext()},this.forceContextRestore=function(){const R=me.get("WEBGL_lose_context");R&&R.restoreContext()},this.getPixelRatio=function(){return $},this.setPixelRatio=function(R){R!==void 0&&($=R,this.setSize(z,Z,!1))},this.getSize=function(R){return R.set(z,Z)},this.setSize=function(R,Q,st=!0){if(ht.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}z=R,Z=Q,n.width=Math.floor(R*$),n.height=Math.floor(Q*$),st===!0&&(n.style.width=R+"px",n.style.height=Q+"px"),this.setViewport(0,0,R,Q)},this.getDrawingBufferSize=function(R){return R.set(z*$,Z*$).floor()},this.setDrawingBufferSize=function(R,Q,st){z=R,Z=Q,$=st,n.width=Math.floor(R*st),n.height=Math.floor(Q*st),this.setViewport(0,0,R,Q)},this.getCurrentViewport=function(R){return R.copy(H)},this.getViewport=function(R){return R.copy(O)},this.setViewport=function(R,Q,st,rt){R.isVector4?O.set(R.x,R.y,R.z,R.w):O.set(R,Q,st,rt),Qt.viewport(H.copy(O).multiplyScalar($).round())},this.getScissor=function(R){return R.copy(nt)},this.setScissor=function(R,Q,st,rt){R.isVector4?nt.set(R.x,R.y,R.z,R.w):nt.set(R,Q,st,rt),Qt.scissor(ut.copy(nt).multiplyScalar($).round())},this.getScissorTest=function(){return St},this.setScissorTest=function(R){Qt.setScissorTest(St=R)},this.setOpaqueSort=function(R){Et=R},this.setTransparentSort=function(R){At=R},this.getClearColor=function(R){return R.copy(Zt.getClearColor())},this.setClearColor=function(){Zt.setClearColor.apply(Zt,arguments)},this.getClearAlpha=function(){return Zt.getClearAlpha()},this.setClearAlpha=function(){Zt.setClearAlpha.apply(Zt,arguments)},this.clear=function(R=!0,Q=!0,st=!0){let rt=0;if(R){let K=!1;if(G!==null){const xt=G.texture.format;K=xt===Sm||xt===xm||xt===ym}if(K){const xt=G.texture.type,Nt=xt===Pa||xt===gr||xt===tc||xt===Io||xt===vm||xt===_m,It=Zt.getClearColor(),Pt=Zt.getClearAlpha(),$t=It.r,ae=It.g,Kt=It.b;Nt?(E[0]=$t,E[1]=ae,E[2]=Kt,E[3]=Pt,k.clearBufferuiv(k.COLOR,0,E)):(b[0]=$t,b[1]=ae,b[2]=Kt,b[3]=Pt,k.clearBufferiv(k.COLOR,0,b))}else rt|=k.COLOR_BUFFER_BIT}Q&&(rt|=k.DEPTH_BUFFER_BIT),st&&(rt|=k.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),k.clear(rt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){n.removeEventListener("webglcontextlost",yt,!1),n.removeEventListener("webglcontextrestored",wt,!1),n.removeEventListener("webglcontextcreationerror",Ut,!1),Zt.dispose(),Bt.dispose(),Me.dispose(),Yt.dispose(),A.dispose(),at.dispose(),vt.dispose(),Ge.dispose(),Y.dispose(),jt.dispose(),ht.dispose(),ht.removeEventListener("sessionstart",jo),ht.removeEventListener("sessionend",qo),ki.stop()};function yt(R){R.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),V=!0}function wt(){console.log("THREE.WebGLRenderer: Context Restored."),V=!1;const R=Ie.autoReset,Q=Ht.enabled,st=Ht.autoUpdate,rt=Ht.needsUpdate,K=Ht.type;Rt(),Ie.autoReset=R,Ht.enabled=Q,Ht.autoUpdate=st,Ht.needsUpdate=rt,Ht.type=K}function Ut(R){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",R.statusMessage)}function ie(R){const Q=R.target;Q.removeEventListener("dispose",ie),$e(Q)}function $e(R){_n(R),Yt.remove(R)}function _n(R){const Q=Yt.get(R).programs;Q!==void 0&&(Q.forEach(function(st){jt.releaseProgram(st)}),R.isShaderMaterial&&jt.releaseShaderCache(R))}this.renderBufferDirect=function(R,Q,st,rt,K,xt){Q===null&&(Q=He);const Nt=K.isMesh&&K.matrixWorld.determinant()<0,It=Yo(R,Q,st,rt,K);Qt.setMaterial(rt,Nt);let Pt=st.index,$t=1;if(rt.wireframe===!0){if(Pt=bt.getWireframeAttribute(st),Pt===void 0)return;$t=2}const ae=st.drawRange,Kt=st.attributes.position;let Ee=ae.start*$t,De=(ae.start+ae.count)*$t;xt!==null&&(Ee=Math.max(Ee,xt.start*$t),De=Math.min(De,(xt.start+xt.count)*$t)),Pt!==null?(Ee=Math.max(Ee,0),De=Math.min(De,Pt.count)):Kt!=null&&(Ee=Math.max(Ee,0),De=Math.min(De,Kt.count));const Qe=De-Ee;if(Qe<0||Qe===1/0)return;Ge.setup(K,rt,It,st,Pt);let We,le=Ot;if(Pt!==null&&(We=pt.get(Pt),le=ne,le.setIndex(We)),K.isMesh)rt.wireframe===!0?(Qt.setLineWidth(rt.wireframeLinewidth*Je()),le.setMode(k.LINES)):le.setMode(k.TRIANGLES);else if(K.isLine){let kt=rt.linewidth;kt===void 0&&(kt=1),Qt.setLineWidth(kt*Je()),K.isLineSegments?le.setMode(k.LINES):K.isLineLoop?le.setMode(k.LINE_LOOP):le.setMode(k.LINE_STRIP)}else K.isPoints?le.setMode(k.POINTS):K.isSprite&&le.setMode(k.TRIANGLES);if(K.isBatchedMesh)if(K._multiDrawInstances!==null)le.renderMultiDrawInstances(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount,K._multiDrawInstances);else if(me.get("WEBGL_multi_draw"))le.renderMultiDraw(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount);else{const kt=K._multiDrawStarts,hn=K._multiDrawCounts,Ue=K._multiDrawCount,Gn=Pt?pt.get(Pt).bytesPerElement:1,na=Yt.get(rt).currentProgram.getUniforms();for(let En=0;En<Ue;En++)na.setValue(k,"_gl_DrawID",En),le.render(kt[En]/Gn,hn[En])}else if(K.isInstancedMesh)le.renderInstances(Ee,Qe,K.count);else if(st.isInstancedBufferGeometry){const kt=st._maxInstanceCount!==void 0?st._maxInstanceCount:1/0,hn=Math.min(st.instanceCount,kt);le.renderInstances(Ee,Qe,hn)}else le.render(Ee,Qe)};function we(R,Q,st){R.transparent===!0&&R.side===wa&&R.forceSinglePass===!1?(R.side=ii,R.needsUpdate=!0,sn(R,Q,st),R.side=As,R.needsUpdate=!0,sn(R,Q,st),R.side=wa):sn(R,Q,st)}this.compile=function(R,Q,st=null){st===null&&(st=R),_=Me.get(st),_.init(Q),N.push(_),st.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(_.pushLight(K),K.castShadow&&_.pushShadow(K))}),R!==st&&R.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(_.pushLight(K),K.castShadow&&_.pushShadow(K))}),_.setupLights();const rt=new Set;return R.traverse(function(K){if(!(K.isMesh||K.isPoints||K.isLine||K.isSprite))return;const xt=K.material;if(xt)if(Array.isArray(xt))for(let Nt=0;Nt<xt.length;Nt++){const It=xt[Nt];we(It,st,K),rt.add(It)}else we(xt,st,K),rt.add(xt)}),N.pop(),_=null,rt},this.compileAsync=function(R,Q,st=null){const rt=this.compile(R,Q,st);return new Promise(K=>{function xt(){if(rt.forEach(function(Nt){Yt.get(Nt).currentProgram.isReady()&&rt.delete(Nt)}),rt.size===0){K(R);return}setTimeout(xt,10)}me.get("KHR_parallel_shader_compile")!==null?xt():setTimeout(xt,10)})};let Rn=null;function wi(R){Rn&&Rn(R)}function jo(){ki.stop()}function qo(){ki.start()}const ki=new Xx;ki.setAnimationLoop(wi),typeof self<"u"&&ki.setContext(self),this.setAnimationLoop=function(R){Rn=R,ht.setAnimationLoop(R),R===null?ki.stop():ki.start()},ht.addEventListener("sessionstart",jo),ht.addEventListener("sessionend",qo),this.render=function(R,Q){if(Q!==void 0&&Q.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(V===!0)return;if(R.matrixWorldAutoUpdate===!0&&R.updateMatrixWorld(),Q.parent===null&&Q.matrixWorldAutoUpdate===!0&&Q.updateMatrixWorld(),ht.enabled===!0&&ht.isPresenting===!0&&(ht.cameraAutoUpdate===!0&&ht.updateCamera(Q),Q=ht.getCamera()),R.isScene===!0&&R.onBeforeRender(C,R,Q,G),_=Me.get(R,N.length),_.init(Q),N.push(_),Ft.multiplyMatrices(Q.projectionMatrix,Q.matrixWorldInverse),q.setFromProjectionMatrix(Ft),Tt=this.localClippingEnabled,ft=Ct.init(this.clippingPlanes,Tt),M=Bt.get(R,I.length),M.init(),I.push(M),ht.enabled===!0&&ht.isPresenting===!0){const xt=C.xr.getDepthSensingMesh();xt!==null&&Cs(xt,Q,-1/0,C.sortObjects)}Cs(R,Q,0,C.sortObjects),M.finish(),C.sortObjects===!0&&M.sort(Et,At),ve=ht.enabled===!1||ht.isPresenting===!1||ht.hasDepthSensing()===!1,ve&&Zt.addToRenderList(M,R),this.info.render.frame++,ft===!0&&Ct.beginShadows();const st=_.state.shadowsArray;Ht.render(st,R,Q),ft===!0&&Ct.endShadows(),this.info.autoReset===!0&&this.info.reset();const rt=M.opaque,K=M.transmissive;if(_.setupLights(),Q.isArrayCamera){const xt=Q.cameras;if(K.length>0)for(let Nt=0,It=xt.length;Nt<It;Nt++){const Pt=xt[Nt];Wo(rt,K,R,Pt)}ve&&Zt.render(R);for(let Nt=0,It=xt.length;Nt<It;Nt++){const Pt=xt[Nt];_r(M,R,Pt,Pt.viewport)}}else K.length>0&&Wo(rt,K,R,Q),ve&&Zt.render(R),_r(M,R,Q);G!==null&&(L.updateMultisampleRenderTarget(G),L.updateRenderTargetMipmap(G)),R.isScene===!0&&R.onAfterRender(C,R,Q),Ge.resetDefaultState(),U=-1,w=null,N.pop(),N.length>0?(_=N[N.length-1],ft===!0&&Ct.setGlobalState(C.clippingPlanes,_.state.camera)):_=null,I.pop(),I.length>0?M=I[I.length-1]:M=null};function Cs(R,Q,st,rt){if(R.visible===!1)return;if(R.layers.test(Q.layers)){if(R.isGroup)st=R.renderOrder;else if(R.isLOD)R.autoUpdate===!0&&R.update(Q);else if(R.isLight)_.pushLight(R),R.castShadow&&_.pushShadow(R);else if(R.isSprite){if(!R.frustumCulled||q.intersectsSprite(R)){rt&&re.setFromMatrixPosition(R.matrixWorld).applyMatrix4(Ft);const Nt=vt.update(R),It=R.material;It.visible&&M.push(R,Nt,It,st,re.z,null)}}else if((R.isMesh||R.isLine||R.isPoints)&&(!R.frustumCulled||q.intersectsObject(R))){const Nt=vt.update(R),It=R.material;if(rt&&(R.boundingSphere!==void 0?(R.boundingSphere===null&&R.computeBoundingSphere(),re.copy(R.boundingSphere.center)):(Nt.boundingSphere===null&&Nt.computeBoundingSphere(),re.copy(Nt.boundingSphere.center)),re.applyMatrix4(R.matrixWorld).applyMatrix4(Ft)),Array.isArray(It)){const Pt=Nt.groups;for(let $t=0,ae=Pt.length;$t<ae;$t++){const Kt=Pt[$t],Ee=It[Kt.materialIndex];Ee&&Ee.visible&&M.push(R,Nt,Ee,st,re.z,Kt)}}else It.visible&&M.push(R,Nt,It,st,re.z,null)}}const xt=R.children;for(let Nt=0,It=xt.length;Nt<It;Nt++)Cs(xt[Nt],Q,st,rt)}function _r(R,Q,st,rt){const K=R.opaque,xt=R.transmissive,Nt=R.transparent;_.setupLightsView(st),ft===!0&&Ct.setGlobalState(C.clippingPlanes,st),rt&&Qt.viewport(H.copy(rt)),K.length>0&&Rs(K,Q,st),xt.length>0&&Rs(xt,Q,st),Nt.length>0&&Rs(Nt,Q,st),Qt.buffers.depth.setTest(!0),Qt.buffers.depth.setMask(!0),Qt.buffers.color.setMask(!0),Qt.setPolygonOffset(!1)}function Wo(R,Q,st,rt){if((st.isScene===!0?st.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[rt.id]===void 0&&(_.state.transmissionRenderTarget[rt.id]=new Gi(1,1,{generateMipmaps:!0,type:me.has("EXT_color_buffer_half_float")||me.has("EXT_color_buffer_float")?La:Pa,minFilter:rr,samples:4,stencilBuffer:c,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Oe.workingColorSpace}));const xt=_.state.transmissionRenderTarget[rt.id],Nt=rt.viewport||H;xt.setSize(Nt.z,Nt.w);const It=C.getRenderTarget();C.setRenderTarget(xt),C.getClearColor(mt),ct=C.getClearAlpha(),ct<1&&C.setClearColor(16777215,.5),C.clear(),ve&&Zt.render(st);const Pt=C.toneMapping;C.toneMapping=Ts;const $t=rt.viewport;if(rt.viewport!==void 0&&(rt.viewport=void 0),_.setupLightsView(rt),ft===!0&&Ct.setGlobalState(C.clippingPlanes,rt),Rs(R,st,rt),L.updateMultisampleRenderTarget(xt),L.updateRenderTargetMipmap(xt),me.has("WEBGL_multisampled_render_to_texture")===!1){let ae=!1;for(let Kt=0,Ee=Q.length;Kt<Ee;Kt++){const De=Q[Kt],Qe=De.object,We=De.geometry,le=De.material,kt=De.group;if(le.side===wa&&Qe.layers.test(rt.layers)){const hn=le.side;le.side=ii,le.needsUpdate=!0,Di(Qe,st,rt,We,le,kt),le.side=hn,le.needsUpdate=!0,ae=!0}}ae===!0&&(L.updateMultisampleRenderTarget(xt),L.updateRenderTargetMipmap(xt))}C.setRenderTarget(It),C.setClearColor(mt,ct),$t!==void 0&&(rt.viewport=$t),C.toneMapping=Pt}function Rs(R,Q,st){const rt=Q.isScene===!0?Q.overrideMaterial:null;for(let K=0,xt=R.length;K<xt;K++){const Nt=R[K],It=Nt.object,Pt=Nt.geometry,$t=rt===null?Nt.material:rt,ae=Nt.group;It.layers.test(st.layers)&&Di(It,Q,st,Pt,$t,ae)}}function Di(R,Q,st,rt,K,xt){R.onBeforeRender(C,Q,st,rt,K,xt),R.modelViewMatrix.multiplyMatrices(st.matrixWorldInverse,R.matrixWorld),R.normalMatrix.getNormalMatrix(R.modelViewMatrix),K.onBeforeRender(C,Q,st,rt,R,xt),K.transparent===!0&&K.side===wa&&K.forceSinglePass===!1?(K.side=ii,K.needsUpdate=!0,C.renderBufferDirect(st,Q,rt,K,R,xt),K.side=As,K.needsUpdate=!0,C.renderBufferDirect(st,Q,rt,K,R,xt),K.side=wa):C.renderBufferDirect(st,Q,rt,K,R,xt),R.onAfterRender(C,Q,st,rt,K,xt)}function sn(R,Q,st){Q.isScene!==!0&&(Q=He);const rt=Yt.get(R),K=_.state.lights,xt=_.state.shadowsArray,Nt=K.state.version,It=jt.getParameters(R,K.state,xt,Q,st),Pt=jt.getProgramCacheKey(It);let $t=rt.programs;rt.environment=R.isMeshStandardMaterial?Q.environment:null,rt.fog=Q.fog,rt.envMap=(R.isMeshStandardMaterial?at:A).get(R.envMap||rt.environment),rt.envMapRotation=rt.environment!==null&&R.envMap===null?Q.environmentRotation:R.envMapRotation,$t===void 0&&(R.addEventListener("dispose",ie),$t=new Map,rt.programs=$t);let ae=$t.get(Pt);if(ae!==void 0){if(rt.currentProgram===ae&&rt.lightsStateVersion===Nt)return ea(R,It),ae}else It.uniforms=jt.getUniforms(R),R.onBeforeCompile(It,C),ae=jt.acquireProgram(It,Pt),$t.set(Pt,ae),rt.uniforms=It.uniforms;const Kt=rt.uniforms;return(!R.isShaderMaterial&&!R.isRawShaderMaterial||R.clipping===!0)&&(Kt.clippingPlanes=Ct.uniform),ea(R,It),rt.needsLights=pf(R),rt.lightsStateVersion=Nt,rt.needsLights&&(Kt.ambientLightColor.value=K.state.ambient,Kt.lightProbe.value=K.state.probe,Kt.directionalLights.value=K.state.directional,Kt.directionalLightShadows.value=K.state.directionalShadow,Kt.spotLights.value=K.state.spot,Kt.spotLightShadows.value=K.state.spotShadow,Kt.rectAreaLights.value=K.state.rectArea,Kt.ltc_1.value=K.state.rectAreaLTC1,Kt.ltc_2.value=K.state.rectAreaLTC2,Kt.pointLights.value=K.state.point,Kt.pointLightShadows.value=K.state.pointShadow,Kt.hemisphereLights.value=K.state.hemi,Kt.directionalShadowMap.value=K.state.directionalShadowMap,Kt.directionalShadowMatrix.value=K.state.directionalShadowMatrix,Kt.spotShadowMap.value=K.state.spotShadowMap,Kt.spotLightMatrix.value=K.state.spotLightMatrix,Kt.spotLightMap.value=K.state.spotLightMap,Kt.pointShadowMap.value=K.state.pointShadowMap,Kt.pointShadowMatrix.value=K.state.pointShadowMatrix),rt.currentProgram=ae,rt.uniformsList=null,ae}function wn(R){if(R.uniformsList===null){const Q=R.currentProgram.getUniforms();R.uniformsList=$u.seqWithValue(Q.seq,R.uniforms)}return R.uniformsList}function ea(R,Q){const st=Yt.get(R);st.outputColorSpace=Q.outputColorSpace,st.batching=Q.batching,st.batchingColor=Q.batchingColor,st.instancing=Q.instancing,st.instancingColor=Q.instancingColor,st.instancingMorph=Q.instancingMorph,st.skinning=Q.skinning,st.morphTargets=Q.morphTargets,st.morphNormals=Q.morphNormals,st.morphColors=Q.morphColors,st.morphTargetsCount=Q.morphTargetsCount,st.numClippingPlanes=Q.numClippingPlanes,st.numIntersection=Q.numClipIntersection,st.vertexAlphas=Q.vertexAlphas,st.vertexTangents=Q.vertexTangents,st.toneMapping=Q.toneMapping}function Yo(R,Q,st,rt,K){Q.isScene!==!0&&(Q=He),L.resetTextureUnits();const xt=Q.fog,Nt=rt.isMeshStandardMaterial?Q.environment:null,It=G===null?C.outputColorSpace:G.isXRRenderTarget===!0?G.texture.colorSpace:Fo,Pt=(rt.isMeshStandardMaterial?at:A).get(rt.envMap||Nt),$t=rt.vertexColors===!0&&!!st.attributes.color&&st.attributes.color.itemSize===4,ae=!!st.attributes.tangent&&(!!rt.normalMap||rt.anisotropy>0),Kt=!!st.morphAttributes.position,Ee=!!st.morphAttributes.normal,De=!!st.morphAttributes.color;let Qe=Ts;rt.toneMapped&&(G===null||G.isXRRenderTarget===!0)&&(Qe=C.toneMapping);const We=st.morphAttributes.position||st.morphAttributes.normal||st.morphAttributes.color,le=We!==void 0?We.length:0,kt=Yt.get(rt),hn=_.state.lights;if(ft===!0&&(Tt===!0||R!==w)){const yn=R===w&&rt.id===U;Ct.setState(rt,R,yn)}let Ue=!1;rt.version===kt.__version?(kt.needsLights&&kt.lightsStateVersion!==hn.state.version||kt.outputColorSpace!==It||K.isBatchedMesh&&kt.batching===!1||!K.isBatchedMesh&&kt.batching===!0||K.isBatchedMesh&&kt.batchingColor===!0&&K.colorTexture===null||K.isBatchedMesh&&kt.batchingColor===!1&&K.colorTexture!==null||K.isInstancedMesh&&kt.instancing===!1||!K.isInstancedMesh&&kt.instancing===!0||K.isSkinnedMesh&&kt.skinning===!1||!K.isSkinnedMesh&&kt.skinning===!0||K.isInstancedMesh&&kt.instancingColor===!0&&K.instanceColor===null||K.isInstancedMesh&&kt.instancingColor===!1&&K.instanceColor!==null||K.isInstancedMesh&&kt.instancingMorph===!0&&K.morphTexture===null||K.isInstancedMesh&&kt.instancingMorph===!1&&K.morphTexture!==null||kt.envMap!==Pt||rt.fog===!0&&kt.fog!==xt||kt.numClippingPlanes!==void 0&&(kt.numClippingPlanes!==Ct.numPlanes||kt.numIntersection!==Ct.numIntersection)||kt.vertexAlphas!==$t||kt.vertexTangents!==ae||kt.morphTargets!==Kt||kt.morphNormals!==Ee||kt.morphColors!==De||kt.toneMapping!==Qe||kt.morphTargetsCount!==le)&&(Ue=!0):(Ue=!0,kt.__version=rt.version);let Gn=kt.currentProgram;Ue===!0&&(Gn=sn(rt,Q,K));let na=!1,En=!1,Ds=!1;const _e=Gn.getUniforms(),zn=kt.uniforms;if(Qt.useProgram(Gn.program)&&(na=!0,En=!0,Ds=!0),rt.id!==U&&(U=rt.id,En=!0),na||w!==R){Qt.buffers.depth.getReversed()?(Mt.copy(R.projectionMatrix),Ob(Mt),Pb(Mt),_e.setValue(k,"projectionMatrix",Mt)):_e.setValue(k,"projectionMatrix",R.projectionMatrix),_e.setValue(k,"viewMatrix",R.matrixWorldInverse);const cn=_e.map.cameraPosition;cn!==void 0&&cn.setValue(k,Vt.setFromMatrixPosition(R.matrixWorld)),Se.logarithmicDepthBuffer&&_e.setValue(k,"logDepthBufFC",2/(Math.log(R.far+1)/Math.LN2)),(rt.isMeshPhongMaterial||rt.isMeshToonMaterial||rt.isMeshLambertMaterial||rt.isMeshBasicMaterial||rt.isMeshStandardMaterial||rt.isShaderMaterial)&&_e.setValue(k,"isOrthographic",R.isOrthographicCamera===!0),w!==R&&(w=R,En=!0,Ds=!0)}if(K.isSkinnedMesh){_e.setOptional(k,K,"bindMatrix"),_e.setOptional(k,K,"bindMatrixInverse");const yn=K.skeleton;yn&&(yn.boneTexture===null&&yn.computeBoneTexture(),_e.setValue(k,"boneTexture",yn.boneTexture,L))}K.isBatchedMesh&&(_e.setOptional(k,K,"batchingTexture"),_e.setValue(k,"batchingTexture",K._matricesTexture,L),_e.setOptional(k,K,"batchingIdTexture"),_e.setValue(k,"batchingIdTexture",K._indirectTexture,L),_e.setOptional(k,K,"batchingColorTexture"),K._colorsTexture!==null&&_e.setValue(k,"batchingColorTexture",K._colorsTexture,L));const Vn=st.morphAttributes;if((Vn.position!==void 0||Vn.normal!==void 0||Vn.color!==void 0)&&qt.update(K,st,Gn),(En||kt.receiveShadow!==K.receiveShadow)&&(kt.receiveShadow=K.receiveShadow,_e.setValue(k,"receiveShadow",K.receiveShadow)),rt.isMeshGouraudMaterial&&rt.envMap!==null&&(zn.envMap.value=Pt,zn.flipEnvMap.value=Pt.isCubeTexture&&Pt.isRenderTargetTexture===!1?-1:1),rt.isMeshStandardMaterial&&rt.envMap===null&&Q.environment!==null&&(zn.envMapIntensity.value=Q.environmentIntensity),En&&(_e.setValue(k,"toneMappingExposure",C.toneMappingExposure),kt.needsLights&&df(zn,Ds),xt&&rt.fog===!0&&Dt.refreshFogUniforms(zn,xt),Dt.refreshMaterialUniforms(zn,rt,$,Z,_.state.transmissionRenderTarget[R.id]),$u.upload(k,wn(kt),zn,L)),rt.isShaderMaterial&&rt.uniformsNeedUpdate===!0&&($u.upload(k,wn(kt),zn,L),rt.uniformsNeedUpdate=!1),rt.isSpriteMaterial&&_e.setValue(k,"center",K.center),_e.setValue(k,"modelViewMatrix",K.modelViewMatrix),_e.setValue(k,"normalMatrix",K.normalMatrix),_e.setValue(k,"modelMatrix",K.matrixWorld),rt.isShaderMaterial||rt.isRawShaderMaterial){const yn=rt.uniformsGroups;for(let cn=0,yr=yn.length;cn<yr;cn++){const Xi=yn[cn];Y.update(Xi,Gn),Y.bind(Xi,Gn)}}return Gn}function df(R,Q){R.ambientLightColor.needsUpdate=Q,R.lightProbe.needsUpdate=Q,R.directionalLights.needsUpdate=Q,R.directionalLightShadows.needsUpdate=Q,R.pointLights.needsUpdate=Q,R.pointLightShadows.needsUpdate=Q,R.spotLights.needsUpdate=Q,R.spotLightShadows.needsUpdate=Q,R.rectAreaLights.needsUpdate=Q,R.hemisphereLights.needsUpdate=Q}function pf(R){return R.isMeshLambertMaterial||R.isMeshToonMaterial||R.isMeshPhongMaterial||R.isMeshStandardMaterial||R.isShadowMaterial||R.isShaderMaterial&&R.lights===!0}this.getActiveCubeFace=function(){return F},this.getActiveMipmapLevel=function(){return P},this.getRenderTarget=function(){return G},this.setRenderTargetTextures=function(R,Q,st){Yt.get(R.texture).__webglTexture=Q,Yt.get(R.depthTexture).__webglTexture=st;const rt=Yt.get(R);rt.__hasExternalTextures=!0,rt.__autoAllocateDepthBuffer=st===void 0,rt.__autoAllocateDepthBuffer||me.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),rt.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(R,Q){const st=Yt.get(R);st.__webglFramebuffer=Q,st.__useDefaultFramebuffer=Q===void 0},this.setRenderTarget=function(R,Q=0,st=0){G=R,F=Q,P=st;let rt=!0,K=null,xt=!1,Nt=!1;if(R){const Pt=Yt.get(R);if(Pt.__useDefaultFramebuffer!==void 0)Qt.bindFramebuffer(k.FRAMEBUFFER,null),rt=!1;else if(Pt.__webglFramebuffer===void 0)L.setupRenderTarget(R);else if(Pt.__hasExternalTextures)L.rebindTextures(R,Yt.get(R.texture).__webglTexture,Yt.get(R.depthTexture).__webglTexture);else if(R.depthBuffer){const Kt=R.depthTexture;if(Pt.__boundDepthTexture!==Kt){if(Kt!==null&&Yt.has(Kt)&&(R.width!==Kt.image.width||R.height!==Kt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");L.setupDepthRenderbuffer(R)}}const $t=R.texture;($t.isData3DTexture||$t.isDataArrayTexture||$t.isCompressedArrayTexture)&&(Nt=!0);const ae=Yt.get(R).__webglFramebuffer;R.isWebGLCubeRenderTarget?(Array.isArray(ae[Q])?K=ae[Q][st]:K=ae[Q],xt=!0):R.samples>0&&L.useMultisampledRTT(R)===!1?K=Yt.get(R).__webglMultisampledFramebuffer:Array.isArray(ae)?K=ae[st]:K=ae,H.copy(R.viewport),ut.copy(R.scissor),ot=R.scissorTest}else H.copy(O).multiplyScalar($).floor(),ut.copy(nt).multiplyScalar($).floor(),ot=St;if(Qt.bindFramebuffer(k.FRAMEBUFFER,K)&&rt&&Qt.drawBuffers(R,K),Qt.viewport(H),Qt.scissor(ut),Qt.setScissorTest(ot),xt){const Pt=Yt.get(R.texture);k.framebufferTexture2D(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_CUBE_MAP_POSITIVE_X+Q,Pt.__webglTexture,st)}else if(Nt){const Pt=Yt.get(R.texture),$t=Q||0;k.framebufferTextureLayer(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,Pt.__webglTexture,st||0,$t)}U=-1},this.readRenderTargetPixels=function(R,Q,st,rt,K,xt,Nt){if(!(R&&R.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let It=Yt.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Nt!==void 0&&(It=It[Nt]),It){Qt.bindFramebuffer(k.FRAMEBUFFER,It);try{const Pt=R.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Se.textureTypeReadable(ae)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}Q>=0&&Q<=R.width-rt&&st>=0&&st<=R.height-K&&k.readPixels(Q,st,rt,K,oe.convert($t),oe.convert(ae),xt)}finally{const Pt=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(k.FRAMEBUFFER,Pt)}}},this.readRenderTargetPixelsAsync=async function(R,Q,st,rt,K,xt,Nt){if(!(R&&R.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let It=Yt.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Nt!==void 0&&(It=It[Nt]),It){const Pt=R.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Se.textureTypeReadable(ae))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(Q>=0&&Q<=R.width-rt&&st>=0&&st<=R.height-K){Qt.bindFramebuffer(k.FRAMEBUFFER,It);const Kt=k.createBuffer();k.bindBuffer(k.PIXEL_PACK_BUFFER,Kt),k.bufferData(k.PIXEL_PACK_BUFFER,xt.byteLength,k.STREAM_READ),k.readPixels(Q,st,rt,K,oe.convert($t),oe.convert(ae),0);const Ee=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(k.FRAMEBUFFER,Ee);const De=k.fenceSync(k.SYNC_GPU_COMMANDS_COMPLETE,0);return k.flush(),await Lb(k,De,4),k.bindBuffer(k.PIXEL_PACK_BUFFER,Kt),k.getBufferSubData(k.PIXEL_PACK_BUFFER,0,xt),k.deleteBuffer(Kt),k.deleteSync(De),xt}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(R,Q=null,st=0){R.isTexture!==!0&&(po("WebGLRenderer: copyFramebufferToTexture function signature has changed."),Q=arguments[0]||null,R=arguments[1]);const rt=Math.pow(2,-st),K=Math.floor(R.image.width*rt),xt=Math.floor(R.image.height*rt),Nt=Q!==null?Q.x:0,It=Q!==null?Q.y:0;L.setTexture2D(R,0),k.copyTexSubImage2D(k.TEXTURE_2D,st,0,0,Nt,It,K,xt),Qt.unbindTexture()};const hc=k.createFramebuffer(),ws=k.createFramebuffer();this.copyTextureToTexture=function(R,Q,st=null,rt=null,K=0,xt=null){R.isTexture!==!0&&(po("WebGLRenderer: copyTextureToTexture function signature has changed."),rt=arguments[0]||null,R=arguments[1],Q=arguments[2],xt=arguments[3]||0,st=null),xt===null&&(K!==0?(po("WebGLRenderer: copyTextureToTexture function signature has changed to support src and dst mipmap levels."),xt=K,K=0):xt=0);let Nt,It,Pt,$t,ae,Kt,Ee,De,Qe;const We=R.isCompressedTexture?R.mipmaps[xt]:R.image;if(st!==null)Nt=st.max.x-st.min.x,It=st.max.y-st.min.y,Pt=st.isBox3?st.max.z-st.min.z:1,$t=st.min.x,ae=st.min.y,Kt=st.isBox3?st.min.z:0;else{const Vn=Math.pow(2,-K);Nt=Math.floor(We.width*Vn),It=Math.floor(We.height*Vn),R.isDataArrayTexture?Pt=We.depth:R.isData3DTexture?Pt=Math.floor(We.depth*Vn):Pt=1,$t=0,ae=0,Kt=0}rt!==null?(Ee=rt.x,De=rt.y,Qe=rt.z):(Ee=0,De=0,Qe=0);const le=oe.convert(Q.format),kt=oe.convert(Q.type);let hn;Q.isData3DTexture?(L.setTexture3D(Q,0),hn=k.TEXTURE_3D):Q.isDataArrayTexture||Q.isCompressedArrayTexture?(L.setTexture2DArray(Q,0),hn=k.TEXTURE_2D_ARRAY):(L.setTexture2D(Q,0),hn=k.TEXTURE_2D),k.pixelStorei(k.UNPACK_FLIP_Y_WEBGL,Q.flipY),k.pixelStorei(k.UNPACK_PREMULTIPLY_ALPHA_WEBGL,Q.premultiplyAlpha),k.pixelStorei(k.UNPACK_ALIGNMENT,Q.unpackAlignment);const Ue=k.getParameter(k.UNPACK_ROW_LENGTH),Gn=k.getParameter(k.UNPACK_IMAGE_HEIGHT),na=k.getParameter(k.UNPACK_SKIP_PIXELS),En=k.getParameter(k.UNPACK_SKIP_ROWS),Ds=k.getParameter(k.UNPACK_SKIP_IMAGES);k.pixelStorei(k.UNPACK_ROW_LENGTH,We.width),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,We.height),k.pixelStorei(k.UNPACK_SKIP_PIXELS,$t),k.pixelStorei(k.UNPACK_SKIP_ROWS,ae),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Kt);const _e=R.isDataArrayTexture||R.isData3DTexture,zn=Q.isDataArrayTexture||Q.isData3DTexture;if(R.isDepthTexture){const Vn=Yt.get(R),yn=Yt.get(Q),cn=Yt.get(Vn.__renderTarget),yr=Yt.get(yn.__renderTarget);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,cn.__webglFramebuffer),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,yr.__webglFramebuffer);for(let Xi=0;Xi<Pt;Xi++)_e&&(k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Yt.get(R).__webglTexture,K,Kt+Xi),k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Yt.get(Q).__webglTexture,xt,Qe+Xi)),k.blitFramebuffer($t,ae,Nt,It,Ee,De,Nt,It,k.DEPTH_BUFFER_BIT,k.NEAREST);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else if(K!==0||R.isRenderTargetTexture||Yt.has(R)){const Vn=Yt.get(R),yn=Yt.get(Q);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,hc),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,ws);for(let cn=0;cn<Pt;cn++)_e?k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Vn.__webglTexture,K,Kt+cn):k.framebufferTexture2D(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,Vn.__webglTexture,K),zn?k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,yn.__webglTexture,xt,Qe+cn):k.framebufferTexture2D(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,yn.__webglTexture,xt),K!==0?k.blitFramebuffer($t,ae,Nt,It,Ee,De,Nt,It,k.COLOR_BUFFER_BIT,k.NEAREST):zn?k.copyTexSubImage3D(hn,xt,Ee,De,Qe+cn,$t,ae,Nt,It):k.copyTexSubImage2D(hn,xt,Ee,De,$t,ae,Nt,It);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else zn?R.isDataTexture||R.isData3DTexture?k.texSubImage3D(hn,xt,Ee,De,Qe,Nt,It,Pt,le,kt,We.data):Q.isCompressedArrayTexture?k.compressedTexSubImage3D(hn,xt,Ee,De,Qe,Nt,It,Pt,le,We.data):k.texSubImage3D(hn,xt,Ee,De,Qe,Nt,It,Pt,le,kt,We):R.isDataTexture?k.texSubImage2D(k.TEXTURE_2D,xt,Ee,De,Nt,It,le,kt,We.data):R.isCompressedTexture?k.compressedTexSubImage2D(k.TEXTURE_2D,xt,Ee,De,We.width,We.height,le,We.data):k.texSubImage2D(k.TEXTURE_2D,xt,Ee,De,Nt,It,le,kt,We);k.pixelStorei(k.UNPACK_ROW_LENGTH,Ue),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Gn),k.pixelStorei(k.UNPACK_SKIP_PIXELS,na),k.pixelStorei(k.UNPACK_SKIP_ROWS,En),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Ds),xt===0&&Q.generateMipmaps&&k.generateMipmap(hn),Qt.unbindTexture()},this.copyTextureToTexture3D=function(R,Q,st=null,rt=null,K=0){return R.isTexture!==!0&&(po("WebGLRenderer: copyTextureToTexture3D function signature has changed."),st=arguments[0]||null,rt=arguments[1]||null,R=arguments[2],Q=arguments[3],K=arguments[4]||0),po('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(R,Q,st,rt,K)},this.initRenderTarget=function(R){Yt.get(R).__webglFramebuffer===void 0&&L.setupRenderTarget(R)},this.initTexture=function(R){R.isCubeTexture?L.setTextureCube(R,0):R.isData3DTexture?L.setTexture3D(R,0):R.isDataArrayTexture||R.isCompressedArrayTexture?L.setTexture2DArray(R,0):L.setTexture2D(R,0),Qt.unbindTexture()},this.resetState=function(){F=0,P=0,G=null,Qt.reset(),Ge.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ua}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const n=this.getContext();n.drawingBufferColorspace=Oe._getDrawingBufferColorSpace(t),n.unpackColorSpace=Oe._getUnpackColorSpace()}}const Qx={name:"CopyShader",uniforms:{tDiffuse:{value:null},opacity:{value:1}},vertexShader:`

		varying vec2 vUv;

		void main() {

			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

		}`,fragmentShader:`

		uniform float opacity;

		uniform sampler2D tDiffuse;

		varying vec2 vUv;

		void main() {

			vec4 texel = texture2D( tDiffuse, vUv );
			gl_FragColor = opacity * texel;


		}`};class fc{constructor(){this.isPass=!0,this.enabled=!0,this.needsSwap=!0,this.clear=!1,this.renderToScreen=!1}setSize(){}render(){console.error("THREE.Pass: .render() must be implemented in derived pass.")}dispose(){}}const hw=new Vx(-1,1,1,-1,0,1);class dw extends Vi{constructor(){super(),this.setAttribute("position",new Cn([-1,3,0,-1,-1,0,3,-1,0],3)),this.setAttribute("uv",new Cn([0,2,0,0,2,0],2))}}const pw=new dw;class Zx{constructor(t){this._mesh=new Wn(pw,t)}dispose(){this._mesh.geometry.dispose()}render(t){t.render(this._mesh,hw)}get material(){return this._mesh.material}set material(t){this._mesh.material=t}}class mw extends fc{constructor(t,n){super(),this.textureID=n!==void 0?n:"tDiffuse",t instanceof Yn?(this.uniforms=t.uniforms,this.material=t):t&&(this.uniforms=sf.clone(t.uniforms),this.material=new Yn({name:t.name!==void 0?t.name:"unspecified",defines:Object.assign({},t.defines),uniforms:this.uniforms,vertexShader:t.vertexShader,fragmentShader:t.fragmentShader})),this.fsQuad=new Zx(this.material)}render(t,n,a){this.uniforms[this.textureID]&&(this.uniforms[this.textureID].value=a.texture),this.fsQuad.material=this.material,this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(n),this.clear&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),this.fsQuad.render(t))}dispose(){this.material.dispose(),this.fsQuad.dispose()}}class Uy extends fc{constructor(t,n){super(),this.scene=t,this.camera=n,this.clear=!0,this.needsSwap=!1,this.inverse=!1}render(t,n,a){const l=t.getContext(),c=t.state;c.buffers.color.setMask(!1),c.buffers.depth.setMask(!1),c.buffers.color.setLocked(!0),c.buffers.depth.setLocked(!0);let f,d;this.inverse?(f=0,d=1):(f=1,d=0),c.buffers.stencil.setTest(!0),c.buffers.stencil.setOp(l.REPLACE,l.REPLACE,l.REPLACE),c.buffers.stencil.setFunc(l.ALWAYS,f,4294967295),c.buffers.stencil.setClear(d),c.buffers.stencil.setLocked(!0),t.setRenderTarget(a),this.clear&&t.clear(),t.render(this.scene,this.camera),t.setRenderTarget(n),this.clear&&t.clear(),t.render(this.scene,this.camera),c.buffers.color.setLocked(!1),c.buffers.depth.setLocked(!1),c.buffers.color.setMask(!0),c.buffers.depth.setMask(!0),c.buffers.stencil.setLocked(!1),c.buffers.stencil.setFunc(l.EQUAL,1,4294967295),c.buffers.stencil.setOp(l.KEEP,l.KEEP,l.KEEP),c.buffers.stencil.setLocked(!0)}}class gw extends fc{constructor(){super(),this.needsSwap=!1}render(t){t.state.buffers.stencil.setLocked(!1),t.state.buffers.stencil.setTest(!1)}}class vw{constructor(t,n){if(this.renderer=t,this._pixelRatio=t.getPixelRatio(),n===void 0){const a=t.getSize(new Wt);this._width=a.width,this._height=a.height,n=new Gi(this._width*this._pixelRatio,this._height*this._pixelRatio,{type:La}),n.texture.name="EffectComposer.rt1"}else this._width=n.width,this._height=n.height;this.renderTarget1=n,this.renderTarget2=n.clone(),this.renderTarget2.texture.name="EffectComposer.rt2",this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2,this.renderToScreen=!0,this.passes=[],this.copyPass=new mw(Qx),this.copyPass.material.blending=Na,this.clock=new kx}swapBuffers(){const t=this.readBuffer;this.readBuffer=this.writeBuffer,this.writeBuffer=t}addPass(t){this.passes.push(t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}insertPass(t,n){this.passes.splice(n,0,t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}removePass(t){const n=this.passes.indexOf(t);n!==-1&&this.passes.splice(n,1)}isLastEnabledPass(t){for(let n=t+1;n<this.passes.length;n++)if(this.passes[n].enabled)return!1;return!0}render(t){t===void 0&&(t=this.clock.getDelta());const n=this.renderer.getRenderTarget();let a=!1;for(let l=0,c=this.passes.length;l<c;l++){const f=this.passes[l];if(f.enabled!==!1){if(f.renderToScreen=this.renderToScreen&&this.isLastEnabledPass(l),f.render(this.renderer,this.writeBuffer,this.readBuffer,t,a),f.needsSwap){if(a){const d=this.renderer.getContext(),p=this.renderer.state.buffers.stencil;p.setFunc(d.NOTEQUAL,1,4294967295),this.copyPass.render(this.renderer,this.writeBuffer,this.readBuffer,t),p.setFunc(d.EQUAL,1,4294967295)}this.swapBuffers()}Uy!==void 0&&(f instanceof Uy?a=!0:f instanceof gw&&(a=!1))}}this.renderer.setRenderTarget(n)}reset(t){if(t===void 0){const n=this.renderer.getSize(new Wt);this._pixelRatio=this.renderer.getPixelRatio(),this._width=n.width,this._height=n.height,t=this.renderTarget1.clone(),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.renderTarget1=t,this.renderTarget2=t.clone(),this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2}setSize(t,n){this._width=t,this._height=n;const a=this._width*this._pixelRatio,l=this._height*this._pixelRatio;this.renderTarget1.setSize(a,l),this.renderTarget2.setSize(a,l);for(let c=0;c<this.passes.length;c++)this.passes[c].setSize(a,l)}setPixelRatio(t){this._pixelRatio=t,this.setSize(this._width,this._height)}dispose(){this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.copyPass.dispose()}}class _w extends fc{constructor(t,n,a=null,l=null,c=null){super(),this.scene=t,this.camera=n,this.overrideMaterial=a,this.clearColor=l,this.clearAlpha=c,this.clear=!0,this.clearDepth=!1,this.needsSwap=!1,this._oldClearColor=new de}render(t,n,a){const l=t.autoClear;t.autoClear=!1;let c,f;this.overrideMaterial!==null&&(f=this.scene.overrideMaterial,this.scene.overrideMaterial=this.overrideMaterial),this.clearColor!==null&&(t.getClearColor(this._oldClearColor),t.setClearColor(this.clearColor,t.getClearAlpha())),this.clearAlpha!==null&&(c=t.getClearAlpha(),t.setClearAlpha(this.clearAlpha)),this.clearDepth==!0&&t.clearDepth(),t.setRenderTarget(this.renderToScreen?null:a),this.clear===!0&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),t.render(this.scene,this.camera),this.clearColor!==null&&t.setClearColor(this._oldClearColor),this.clearAlpha!==null&&t.setClearAlpha(c),this.overrideMaterial!==null&&(this.scene.overrideMaterial=f),t.autoClear=l}}const yw={uniforms:{tDiffuse:{value:null},luminosityThreshold:{value:1},smoothWidth:{value:1},defaultColor:{value:new de(0)},defaultOpacity:{value:0}},vertexShader:`

		varying vec2 vUv;

		void main() {

			vUv = uv;

			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

		}`,fragmentShader:`

		uniform sampler2D tDiffuse;
		uniform vec3 defaultColor;
		uniform float defaultOpacity;
		uniform float luminosityThreshold;
		uniform float smoothWidth;

		varying vec2 vUv;

		void main() {

			vec4 texel = texture2D( tDiffuse, vUv );

			float v = luminance( texel.xyz );

			vec4 outputColor = vec4( defaultColor.rgb, defaultOpacity );

			float alpha = smoothstep( luminosityThreshold, luminosityThreshold + smoothWidth, v );

			gl_FragColor = mix( outputColor, texel, alpha );

		}`};class Go extends fc{constructor(t,n,a,l){super(),this.strength=n!==void 0?n:1,this.radius=a,this.threshold=l,this.resolution=t!==void 0?new Wt(t.x,t.y):new Wt(256,256),this.clearColor=new de(0,0,0),this.renderTargetsHorizontal=[],this.renderTargetsVertical=[],this.nMips=5;let c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);this.renderTargetBright=new Gi(c,f,{type:La}),this.renderTargetBright.texture.name="UnrealBloomPass.bright",this.renderTargetBright.texture.generateMipmaps=!1;for(let v=0;v<this.nMips;v++){const y=new Gi(c,f,{type:La});y.texture.name="UnrealBloomPass.h"+v,y.texture.generateMipmaps=!1,this.renderTargetsHorizontal.push(y);const x=new Gi(c,f,{type:La});x.texture.name="UnrealBloomPass.v"+v,x.texture.generateMipmaps=!1,this.renderTargetsVertical.push(x),c=Math.round(c/2),f=Math.round(f/2)}const d=yw;this.highPassUniforms=sf.clone(d.uniforms),this.highPassUniforms.luminosityThreshold.value=l,this.highPassUniforms.smoothWidth.value=.01,this.materialHighPassFilter=new Yn({uniforms:this.highPassUniforms,vertexShader:d.vertexShader,fragmentShader:d.fragmentShader}),this.separableBlurMaterials=[];const p=[3,5,7,9,11];c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);for(let v=0;v<this.nMips;v++)this.separableBlurMaterials.push(this.getSeperableBlurMaterial(p[v])),this.separableBlurMaterials[v].uniforms.invSize.value=new Wt(1/c,1/f),c=Math.round(c/2),f=Math.round(f/2);this.compositeMaterial=this.getCompositeMaterial(this.nMips),this.compositeMaterial.uniforms.blurTexture1.value=this.renderTargetsVertical[0].texture,this.compositeMaterial.uniforms.blurTexture2.value=this.renderTargetsVertical[1].texture,this.compositeMaterial.uniforms.blurTexture3.value=this.renderTargetsVertical[2].texture,this.compositeMaterial.uniforms.blurTexture4.value=this.renderTargetsVertical[3].texture,this.compositeMaterial.uniforms.blurTexture5.value=this.renderTargetsVertical[4].texture,this.compositeMaterial.uniforms.bloomStrength.value=n,this.compositeMaterial.uniforms.bloomRadius.value=.1;const m=[1,.8,.6,.4,.2];this.compositeMaterial.uniforms.bloomFactors.value=m,this.bloomTintColors=[new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1)],this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors;const g=Qx;this.copyUniforms=sf.clone(g.uniforms),this.blendMaterial=new Yn({uniforms:this.copyUniforms,vertexShader:g.vertexShader,fragmentShader:g.fragmentShader,blending:xp,depthTest:!1,depthWrite:!1,transparent:!0}),this.enabled=!0,this.needsSwap=!1,this._oldClearColor=new de,this.oldClearAlpha=1,this.basic=new vr,this.fsQuad=new Zx(null)}dispose(){for(let t=0;t<this.renderTargetsHorizontal.length;t++)this.renderTargetsHorizontal[t].dispose();for(let t=0;t<this.renderTargetsVertical.length;t++)this.renderTargetsVertical[t].dispose();this.renderTargetBright.dispose();for(let t=0;t<this.separableBlurMaterials.length;t++)this.separableBlurMaterials[t].dispose();this.compositeMaterial.dispose(),this.blendMaterial.dispose(),this.basic.dispose(),this.fsQuad.dispose()}setSize(t,n){let a=Math.round(t/2),l=Math.round(n/2);this.renderTargetBright.setSize(a,l);for(let c=0;c<this.nMips;c++)this.renderTargetsHorizontal[c].setSize(a,l),this.renderTargetsVertical[c].setSize(a,l),this.separableBlurMaterials[c].uniforms.invSize.value=new Wt(1/a,1/l),a=Math.round(a/2),l=Math.round(l/2)}render(t,n,a,l,c){t.getClearColor(this._oldClearColor),this.oldClearAlpha=t.getClearAlpha();const f=t.autoClear;t.autoClear=!1,t.setClearColor(this.clearColor,0),c&&t.state.buffers.stencil.setTest(!1),this.renderToScreen&&(this.fsQuad.material=this.basic,this.basic.map=a.texture,t.setRenderTarget(null),t.clear(),this.fsQuad.render(t)),this.highPassUniforms.tDiffuse.value=a.texture,this.highPassUniforms.luminosityThreshold.value=this.threshold,this.fsQuad.material=this.materialHighPassFilter,t.setRenderTarget(this.renderTargetBright),t.clear(),this.fsQuad.render(t);let d=this.renderTargetBright;for(let p=0;p<this.nMips;p++)this.fsQuad.material=this.separableBlurMaterials[p],this.separableBlurMaterials[p].uniforms.colorTexture.value=d.texture,this.separableBlurMaterials[p].uniforms.direction.value=Go.BlurDirectionX,t.setRenderTarget(this.renderTargetsHorizontal[p]),t.clear(),this.fsQuad.render(t),this.separableBlurMaterials[p].uniforms.colorTexture.value=this.renderTargetsHorizontal[p].texture,this.separableBlurMaterials[p].uniforms.direction.value=Go.BlurDirectionY,t.setRenderTarget(this.renderTargetsVertical[p]),t.clear(),this.fsQuad.render(t),d=this.renderTargetsVertical[p];this.fsQuad.material=this.compositeMaterial,this.compositeMaterial.uniforms.bloomStrength.value=this.strength,this.compositeMaterial.uniforms.bloomRadius.value=this.radius,this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors,t.setRenderTarget(this.renderTargetsHorizontal[0]),t.clear(),this.fsQuad.render(t),this.fsQuad.material=this.blendMaterial,this.copyUniforms.tDiffuse.value=this.renderTargetsHorizontal[0].texture,c&&t.state.buffers.stencil.setTest(!0),this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(a),this.fsQuad.render(t)),t.setClearColor(this._oldClearColor,this.oldClearAlpha),t.autoClear=f}getSeperableBlurMaterial(t){const n=[];for(let a=0;a<t;a++)n.push(.39894*Math.exp(-.5*a*a/(t*t))/t);return new Yn({defines:{KERNEL_RADIUS:t},uniforms:{colorTexture:{value:null},invSize:{value:new Wt(.5,.5)},direction:{value:new Wt(.5,.5)},gaussianCoefficients:{value:n}},vertexShader:`varying vec2 vUv;
				void main() {
					vUv = uv;
					gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
				}`,fragmentShader:`#include <common>
				varying vec2 vUv;
				uniform sampler2D colorTexture;
				uniform vec2 invSize;
				uniform vec2 direction;
				uniform float gaussianCoefficients[KERNEL_RADIUS];

				void main() {
					float weightSum = gaussianCoefficients[0];
					vec3 diffuseSum = texture2D( colorTexture, vUv ).rgb * weightSum;
					for( int i = 1; i < KERNEL_RADIUS; i ++ ) {
						float x = float(i);
						float w = gaussianCoefficients[i];
						vec2 uvOffset = direction * invSize * x;
						vec3 sample1 = texture2D( colorTexture, vUv + uvOffset ).rgb;
						vec3 sample2 = texture2D( colorTexture, vUv - uvOffset ).rgb;
						diffuseSum += (sample1 + sample2) * w;
						weightSum += 2.0 * w;
					}
					gl_FragColor = vec4(diffuseSum/weightSum, 1.0);
				}`})}getCompositeMaterial(t){return new Yn({defines:{NUM_MIPS:t},uniforms:{blurTexture1:{value:null},blurTexture2:{value:null},blurTexture3:{value:null},blurTexture4:{value:null},blurTexture5:{value:null},bloomStrength:{value:1},bloomFactors:{value:null},bloomTintColors:{value:null},bloomRadius:{value:0}},vertexShader:`varying vec2 vUv;
				void main() {
					vUv = uv;
					gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
				}`,fragmentShader:`varying vec2 vUv;
				uniform sampler2D blurTexture1;
				uniform sampler2D blurTexture2;
				uniform sampler2D blurTexture3;
				uniform sampler2D blurTexture4;
				uniform sampler2D blurTexture5;
				uniform float bloomStrength;
				uniform float bloomRadius;
				uniform float bloomFactors[NUM_MIPS];
				uniform vec3 bloomTintColors[NUM_MIPS];

				float lerpBloomFactor(const in float factor) {
					float mirrorFactor = 1.2 - factor;
					return mix(factor, mirrorFactor, bloomRadius);
				}

				void main() {
					gl_FragColor = bloomStrength * ( lerpBloomFactor(bloomFactors[0]) * vec4(bloomTintColors[0], 1.0) * texture2D(blurTexture1, vUv) +
						lerpBloomFactor(bloomFactors[1]) * vec4(bloomTintColors[1], 1.0) * texture2D(blurTexture2, vUv) +
						lerpBloomFactor(bloomFactors[2]) * vec4(bloomTintColors[2], 1.0) * texture2D(blurTexture3, vUv) +
						lerpBloomFactor(bloomFactors[3]) * vec4(bloomTintColors[3], 1.0) * texture2D(blurTexture4, vUv) +
						lerpBloomFactor(bloomFactors[4]) * vec4(bloomTintColors[4], 1.0) * texture2D(blurTexture5, vUv) );
				}`})}}Go.BlurDirectionX=new Wt(1,0);Go.BlurDirectionY=new Wt(0,1);const of=["ai-server","pc-server","android-server","browser-server","room-server","dev-server"];function xw(s=""){const t=s.split(".",1)[0];return of.includes(t)?t:"ai-server"}function Zl(s){return{"ai-server":"AI","pc-server":"PC","android-server":"Android","browser-server":"Browser","room-server":"Room","dev-server":"Dev"}[s]||s.replace("-server","")}function om(s=""){return s.trim().toUpperCase()||"UNKNOWN"}function Rm(s,t=""){const n=om(s.status),a=`${s.status_detail||""} ${s.degraded_reason||""} ${s.recovery_hint||""}`.toLowerCase();return s.server_id===t||["DEGRADED","OFFLINE","UNCONFIGURED","DISABLED","RECOVERING"].includes(n)||a.includes("permission")||a.includes("missing")||a.includes("recover")}function Sw(s){const t=s.filter(n=>Rm(n));return{ok:Math.max(0,s.length-t.length),attention:t}}function Mw(s){var f,d;const t=s.type||s.source_type||"activity.updated",n=s.capability_id||String(((f=s.payload)==null?void 0:f.capability_id)||""),a=s.server_id||xw(n),l=String(s.status||((d=s.payload)==null?void 0:d.status)||"");let c="pulse";return t==="approval.created"?c="containment":t==="approval.resolved"?c="containment-resolved":t.includes("failed")||l.toLowerCase()==="failed"?c="fracture":t.includes("completed")?c="complete":(t.includes("status")||t.includes("connection"))&&(c=l.toLowerCase().includes("offline")?"disconnect":"recovery"),{id:`${s.type}-${s.source_updated_at}-${a}-${s.approval_id||""}`,type:t,effect:c,serverId:a,capabilityId:n,status:l,severity:s.severity||"info",message:s.message||t,createdAt:s.generated_at||Date.now(),expiresAt:(s.generated_at||Date.now())+4500}}function Ew(s){const t=s.approvals.data.pending||[],n=s.attention.data.items||[];return[...t.map(l=>({id:l.approval_id,kind:"approval",severity:"warning",title:"Approval required",message:l.summary||l.capability_id||"Review requested action",created_at:l.created_at,expires_at:l.expires_at})),...n.filter(l=>l.kind!=="approval")]}function bw(s){const t=s.core.data,n=s.current_task.data;return(s.approvals.data.pending_count||0)>0?"Waiting for Approval":String(t.health||"").toUpperCase()==="OFFLINE"?"Offline":String(t.health||"").toUpperCase()==="DEGRADED"?"Stabilizing":n.task_id||String(t.mode||"").toUpperCase()==="EXECUTING"?"Executing":"Idle"}function Tw(s){const t=s.mind_summary.data||{},n=s.core.data||{},a=sp(t.memory),l=sp(t.autonomy),c=sp(l.desires||l.pressures||l.desire_state),f=Aw(c);return{"Active goal":String(n.active_goal||"Not reported"),"Dominant desire":f||"Not reported","Context confidence":String(n.confidence||t.context_confidence||"Not reported"),"Memories used":Cw(a),"Last consolidation":String(a.last_consolidation||a.last_consolidated_at||a.last_sleep_at||"Not reported")}}function sp(s){return s&&typeof s=="object"&&!Array.isArray(s)?s:{}}function Aw(s){let t="",n=Number.NEGATIVE_INFINITY;for(const[a,l]of Object.entries(s)){const c=typeof l=="number"?l:Number(typeof l=="object"&&l?l.value||l.pressure:l);Number.isFinite(c)&&c>n&&(t=a,n=c)}return t}function Cw(s){const t=s.memories_used||s.used||s.context_items;if(t!==void 0)return String(t);const n=["episodic","semantic","procedural"].reduce((a,l)=>{const c=Number(s[l]||0);return Number.isFinite(c)?a+c:a},0);return n>0?String(n):"Not reported"}const en={cyan:new de("#29D3FF"),white:new de("#EAF2FF"),violet:new de("#8B7CFF"),amber:new de("#FFB84D"),red:new de("#FF5D73"),muted:new de("#8EA0B8"),recovery:new de("#2DD4A8")};function Kx({mode:s,health:t,activityLevel:n,confidence:a,servers:l,visualEvents:c,activeServerId:f="",nextServerId:d="",approvalServerIds:p=[]}){const m=pe.useRef(null),g=pe.useRef({mode:s,health:t,activityLevel:n,confidence:a,servers:l,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}),v=pe.useMemo(()=>of.map(y=>({id:y,label:Zl(y)})),[]);return pe.useEffect(()=>{g.current={mode:s,health:t,activityLevel:n,confidence:a,servers:l,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}},[s,t,n,a,l,c,f,d,p]),pe.useEffect(()=>{const y=m.current;if(!y)return;const x=window.matchMedia("(prefers-reduced-motion: reduce)").matches,E=new aT,b=new _i(44,1,.1,100);b.position.set(0,0,7.2);const M=new fw({antialias:!0,alpha:!0,powerPreference:"high-performance"});M.setPixelRatio(Math.min(window.devicePixelRatio,2)),M.outputColorSpace=vi,y.appendChild(M.domElement);const _=new vw(M);_.addPass(new _w(E,b));const I=new Go(new Wt(1,1),.38,.45,.86);_.addPass(I);const N=new mo;E.add(N);const C=new Yn({transparent:!0,depthWrite:!1,uniforms:{uTime:{value:0},uActivity:{value:.2},uColor:{value:en.cyan.clone()},uGlow:{value:.55}},vertexShader:`
        uniform float uTime;
        uniform float uActivity;
        varying vec3 vNormal;
        varying vec3 vView;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vec3 displaced = position + normal * (sin(position.x * 4.7 + uTime * 1.4) + sin(position.y * 5.1 - uTime)) * 0.025 * uActivity;
          vec4 mvPosition = modelViewMatrix * vec4(displaced, 1.0);
          vView = normalize(-mvPosition.xyz);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,fragmentShader:`
        uniform vec3 uColor;
        uniform float uGlow;
        varying vec3 vNormal;
        varying vec3 vView;
        void main() {
          float fresnel = pow(1.0 - max(dot(vNormal, vView), 0.0), 2.25);
          float core = 0.18 + fresnel * uGlow;
          gl_FragColor = vec4(uColor * core, 0.34 + fresnel * 0.42);
        }
      `}),V=new Wn(new ff(1.24,96,64),C);N.add(V);const F=new Wn(new rf(1.72,.018,12,160),new vr({color:en.amber,transparent:!0,opacity:0}));F.rotation.x=Math.PI/2.15,N.add(F);const P=new Wn(new rf(1.35,.015,12,160),new vr({color:en.recovery,transparent:!0,opacity:0}));P.rotation.x=Math.PI/2,N.add(P);const G=new Map;of.forEach((ct,z)=>{const Z=Rw(ct,z);G.set(ct,Z),N.add(Z.group)}),E.add(new CT(9347256,.55));const U=new AT(15397631,1.3);U.position.set(0,0,4.8),E.add(U);const w=new kx,H=()=>{const ct=Math.max(1,y.clientWidth),z=Math.max(1,y.clientHeight);b.aspect=ct/z,b.updateProjectionMatrix(),M.setSize(ct,z,!1),_.setSize(ct,z),I.resolution.set(ct,z)},ut=new ResizeObserver(H);ut.observe(y),H();let ot=0;const mt=()=>{ot=requestAnimationFrame(mt);const ct=Math.min(w.getDelta(),.05),z=performance.now(),Z=g.current,$=Math.min(Math.max(Number(Z.activityLevel||1),0),8)/8,Et=x?0:.08+$*.42;N.userData.rotationSpeed=os.damp(Number(N.userData.rotationSpeed||0),Et,2.6,ct),N.rotation.y+=Number(N.userData.rotationSpeed)*ct,V.rotation.x+=Number(N.userData.rotationSpeed)*ct*.42,C.uniforms.uTime.value+=ct,C.uniforms.uActivity.value=os.damp(C.uniforms.uActivity.value,.25+$,3.2,ct),C.uniforms.uGlow.value=os.damp(C.uniforms.uGlow.value,Z.health==="DEGRADED"?.9:Z.health==="OFFLINE"?.35:.62,2.5,ct),C.uniforms.uColor.value.lerp(Z.health==="OFFLINE"?en.red:Z.health==="DEGRADED"?en.amber:en.cyan,1-Math.exp(-ct*2.8));const At=x?1:1+Math.sin(z*.0016)*(.018+$*.018);V.scale.setScalar(At);const O=Z.events.filter(q=>q.expiresAt>Date.now());let nt=0,St=0;for(const q of G.values()){ww(q,Z,O,z),q.color.lerp(q.targetColor,1-Math.exp(-ct*5.5)),q.opacity=os.damp(q.opacity,q.targetOpacity,5.5,ct);for(const ft of[...q.segments,...q.filaments]){const Tt=ft.material;Tt.color.copy(q.color);const Mt=ft.userData.mid.clone();Mt.applyMatrix4(N.matrixWorld);const Ft=Mt.z>=0?1:.34;Tt.opacity=q.opacity*Ft*Number(ft.userData.opacityScale||1),ft.visible=!!ft.userData.enabled}q.marker.material.color.copy(q.color),q.marker.material.opacity=Math.min(1,q.opacity+.25),q.group.scale.setScalar(os.damp(q.group.scale.x,Number(q.group.userData.targetScale||1),8,ct)),q.group.userData.containment&&(nt=Math.max(nt,Number(q.group.userData.effectStrength||0))),q.group.userData.recovery&&(St=Math.max(St,Number(q.group.userData.effectStrength||0)))}F.material.opacity=os.damp(F.material.opacity,Math.min(.58,nt),6,ct),P.material.opacity=os.damp(P.material.opacity,Math.min(.72,St),5,ct),P.scale.setScalar(1+St*1.25),x||(P.rotation.z+=ct*1.2),b.position.z=os.damp(b.position.z,Z.mode==="EXECUTING"?6.6:7.25,1.8,ct),_.render()};return mt(),()=>{cancelAnimationFrame(ot),ut.disconnect(),_.dispose(),Dw(E),M.dispose(),M.domElement.remove()}},[]),D.jsxs("div",{className:"core-sphere","data-testid":"core-sphere","data-mode":s,"data-health":t,children:[D.jsx("div",{ref:m,className:"core-canvas",role:"img","aria-label":`AEGIS core sphere. Mode ${s}, health ${t}.`}),D.jsx("div",{className:"core-legend","aria-label":"Core server arcs",children:v.map(y=>D.jsxs("span",{className:"core-legend__item","data-server":y.id,children:[D.jsx("i",{"aria-hidden":"true"}),y.label]},y.id))}),D.jsxs("div",{className:"muted mono core-caption",children:["Mode: ",s," / Health: ",t," / Confidence: ",a]})]})}function Rw(s,t){const n=new mo;n.rotation.set(t*.37,t*.71,t*.23);const a=2.05,l=t/of.length*Math.PI,c=[kl(a,l+.1,l+Math.PI*.68,.018),kl(a,l+Math.PI*.78,l+Math.PI*1.34,.018),kl(a,l+Math.PI*1.46,l+Math.PI*2-.1,.018)],f=kl(a+.16,l+.25,l+Math.PI*1.75,.006),d=kl(a-.17,l+Math.PI*.08,l+Math.PI*1.92,.005);f.rotation.x=.18,d.rotation.y=-.14;const p=new Wn(new ff(.055,20,20),new vr({color:en.cyan,transparent:!0,opacity:.8}));p.position.copy(lm(a+.07,l+t*.24));for(const m of[...c,f,d,p])n.add(m);return{serverId:s,group:n,segments:c,filaments:[f,d],marker:p,color:en.cyan.clone(),targetColor:en.cyan.clone(),opacity:.42,targetOpacity:.42}}function kl(s,t,n,a){const l=[];for(let g=0;g<=64;g+=1){const v=t+(n-t)*g/64;l.push(lm(s,v))}const f=new Fx(l),d=new Am(f,72,a,8,!1),p=new vr({color:en.cyan,transparent:!0,opacity:.4,depthWrite:!1}),m=new Wn(d,p);return m.userData.mid=lm(s,(t+n)/2),m.userData.enabled=!0,m.userData.opacityScale=a<.01?.42:1,m}function lm(s,t){return new W(Math.cos(t)*s,Math.sin(t)*s,Math.sin(t*1.7)*.18)}function ww(s,t,n,a){const l=t.servers.find(p=>p.server_id===s.serverId),c=String((l==null?void 0:l.status)||"UNCONFIGURED").toUpperCase(),f=n.find(p=>p.serverId===s.serverId),d=f?Math.max(0,Math.min(1,(f.expiresAt-Date.now())/Math.max(1,f.expiresAt-f.createdAt))):0;s.group.userData.targetScale=1,s.group.userData.effectStrength=d,s.group.userData.containment=!1,s.group.userData.recovery=!1,s.targetColor.copy(en.cyan),s.targetOpacity=.5,s.segments.forEach(p=>{p.userData.enabled=!0}),(c==="UNCONFIGURED"||c==="DISABLED")&&(s.targetColor.copy(en.muted),s.targetOpacity=.22),c==="OFFLINE"&&(s.targetColor.copy(en.muted),s.targetOpacity=.26,s.segments[1].userData.enabled=!1),c==="DEGRADED"&&(s.targetColor.copy(en.amber),s.targetOpacity=.58+Math.sin(a*.018)*.08),t.nextServerIds.has(s.serverId)&&(s.targetColor.copy(en.violet),s.targetOpacity=.72),t.approvalServerIds.has(s.serverId)&&(s.targetColor.copy(en.amber),s.targetOpacity=.86,s.group.userData.containment=!0),t.activeServerId===s.serverId&&(s.targetColor.copy(en.white).lerp(en.cyan,.28),s.targetOpacity=.94,s.group.userData.targetScale=1.02),f&&(f.effect==="fracture"?(s.targetColor.copy(en.red),s.targetOpacity=.96,s.group.userData.targetScale=1+d*.04):f.effect==="containment"?(s.targetColor.copy(en.amber),s.group.userData.containment=!0,s.targetOpacity=.96):f.effect==="recovery"?(s.targetColor.copy(en.recovery),s.group.userData.recovery=!0,s.targetOpacity=.98):f.effect==="complete"||f.effect==="pulse"?(s.targetColor.copy(en.white).lerp(en.cyan,.2),s.targetOpacity=.86+d*.14,s.group.userData.targetScale=1+d*.035):f.effect==="disconnect"&&(s.segments[1].userData.enabled=!1,s.targetColor.copy(en.red),s.targetOpacity=.64))}function Dw(s){s.traverse(t=>{const n=t;n.geometry&&n.geometry.dispose();const a=n.material;Array.isArray(a)?a.forEach(l=>l.dispose()):a&&a.dispose()})}function Uw({overview:s,recentEvents:t}){const n=s.core.data,a=s.servers.data.items||[],l=s.current_task.data,c=s.usage.data,f=Sw(a),d=Tw(s),p=a.filter(m=>Rm(m));return D.jsxs(D.Fragment,{children:[D.jsxs("section",{className:"command-priority",children:[D.jsxs("section",{className:"panel command-operation",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"Current Operation"}),D.jsx(Lo,{status:String(n.mode||"IDLE")})]}),D.jsx("h3",{children:l.title||"No active task"}),D.jsx("p",{className:"muted",children:l.current_action||l.next_action||l.blocked_reason||"AEGIS is waiting for a meaningful signal or user request."}),D.jsxs("div",{className:"stat-grid",children:[D.jsx(qu,{icon:D.jsx(ax,{size:18}),label:"Activity",value:String(n.activity_level??0)}),D.jsx(qu,{icon:D.jsx(a1,{size:18}),label:"Confidence",value:String(n.confidence||"Not reported")}),D.jsx(qu,{icon:D.jsx(f1,{size:18}),label:"Approvals",value:String(n.pending_approval_count??0)}),D.jsx(qu,{icon:D.jsx(u1,{size:18}),label:"Freshness",value:s.freshness.stale?"STALE":"LIVE"})]})]}),D.jsx(C1,{items:s.attention.data.items||[]})]}),D.jsxs("div",{className:"grid grid--command",children:[D.jsx("section",{className:"panel core-card",children:D.jsx(Kx,{mode:String(n.mode||"IDLE"),health:String(n.health||"ONLINE"),activityLevel:Number(n.activity_level||1),confidence:String(n.confidence||"medium"),servers:a,visualEvents:[],activeServerId:String(l.capability_id||"").split(".",1)[0],nextServerId:"",approvalServerIds:(s.approvals.data.pending||[]).map(m=>String(m.capability_id||"").split(".",1)[0])})}),D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"AI State"}),D.jsx(ar,{...Wu(s.core)})]}),D.jsxs("div",{className:"grid",children:[D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"Active goal"}),D.jsx("b",{style:{fontSize:16},children:String(n.active_goal||"No active goal")})]}),D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"Attention level"}),D.jsx("b",{style:{fontSize:16},children:String(n.attention_level||"normal")})]}),D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"LLM usage"}),D.jsx("b",{style:{fontSize:16},children:String(c.summary||c.total_tokens||"Audit-backed")})]})]})]})]}),D.jsxs("div",{className:"grid grid--three",style:{marginTop:16},children:[D.jsxs("section",{className:"panel server-summary-card",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"Systems"}),D.jsx(ar,{...Wu(s.servers)})]}),D.jsxs("div",{className:"server-summary-line",children:[D.jsx(g1,{size:18}),D.jsxs("strong",{children:[f.ok," normal"]}),D.jsxs("span",{children:[f.attention.length," need attention"]})]}),D.jsx("div",{className:"grid",children:p.length?p.slice(0,4).map(m=>D.jsxs("div",{className:"list-row",children:[D.jsxs("div",{children:[D.jsx("strong",{children:Zl(m.server_id)}),D.jsx("div",{className:"muted",children:m.status_detail||m.degraded_reason||m.recovery_hint||"Review server status."})]}),D.jsx(Lo,{status:m.status,detail:m.recovery_hint})]},m.server_id)):D.jsx("p",{className:"muted",children:"All configured systems are operating normally."})})]}),D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"Recent Events"}),D.jsx(ar,{...Wu(s.notifications)})]}),D.jsxs("div",{className:"grid",children:[t.length?t.slice(0,5).map(m=>D.jsx("div",{className:"list-row",children:D.jsxs("div",{children:[D.jsx("strong",{children:m.type}),D.jsx("div",{className:"muted",children:m.message||m.source_type})]})},`${m.type}-${m.source_updated_at}-${m.message}`)):(s.notifications.data.recent||[]).slice(0,5).map((m,g)=>D.jsx("div",{className:"list-row",children:D.jsxs("div",{children:[D.jsx("strong",{children:String(m.title||"Notification")}),D.jsx("div",{className:"muted",children:String(m.message||m.severity||"")})]})},String(m.notification_id||m.id||g))),t.length===0&&(s.notifications.data.recent||[]).length===0?D.jsx("p",{className:"muted",children:"No recent events reported."}):null]})]}),D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"Memory & Mind"}),D.jsx(ar,{...Wu(s.mind_summary)})]}),D.jsx("div",{className:"grid",children:Object.entries(d).map(([m,g])=>D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:m}),D.jsx("b",{style:{fontSize:15},children:g})]},m))})]})]})]})}function qu({icon:s,label:t,value:n}){return D.jsxs("div",{className:"stat",children:[D.jsxs("span",{className:"muted",children:[s," ",t]}),D.jsx("b",{children:n})]})}function Wu(s){return{generatedAt:s.generated_at,sourceUpdatedAt:s.source_updated_at,stale:s.stale}}function Nw({overview:s}){const[t,n]=pe.useState(s),[a,l]=pe.useState([]),[c,f]=pe.useState([]);pe.useEffect(()=>n(s),[s]);const d=pe.useCallback(E=>{if("schema_version"in E){n(E);return}l(M=>[E,...M].slice(0,10));const b=Mw(E);f(M=>[b,...M.filter(_=>_.expiresAt>Date.now())].slice(0,12))},[]);hx(d,!0,"display");const p=t.core.data,m=t.servers.data.items||[],g=t.current_task.data,v=Ew(t),y=String(g.capability_id||"").split(".",1)[0],x=bw(t);return D.jsxs("main",{className:"display-shell","data-phase":x,"data-testid":"display-shell",children:[D.jsxs("header",{className:"display-top",children:[D.jsxs("section",{className:"display-card display-operation","aria-label":"Current Operation",children:[D.jsx("span",{className:"display-kicker",children:"Current Operation"}),D.jsx("h1",{children:g.title||"No active task"}),D.jsx("p",{children:g.current_action||g.next_action||g.blocked_reason||"Waiting for a meaningful signal."}),D.jsxs("div",{className:"display-meta",children:[D.jsx(Lo,{status:String(p.mode||"IDLE")}),D.jsx("span",{children:x})]})]}),v.length?D.jsxs("section",{className:"display-card display-attention","aria-label":"Attention",children:[D.jsx("span",{className:"display-kicker",children:"Attention"}),v.slice(0,4).map(E=>D.jsxs("article",{className:"display-attention__item","data-severity":E.severity,children:[D.jsx("strong",{children:E.title}),D.jsx("p",{children:E.message||E.recovery_hint||"Review this signal."})]},E.id))]}):null]}),D.jsx("section",{className:"display-core-stage","aria-label":"AEGIS core",children:D.jsx(Kx,{mode:String(p.mode||"IDLE"),health:String(p.health||"ONLINE"),activityLevel:Number(p.activity_level||1),confidence:String(p.confidence||"medium"),servers:m,visualEvents:c,activeServerId:y,nextServerId:Ow(g.steps),approvalServerIds:(t.approvals.data.pending||[]).map(E=>String(E.capability_id||"").split(".",1)[0])})}),D.jsxs("section",{className:"display-bottom",children:[D.jsxs("div",{className:"display-card display-phase",children:[D.jsx("span",{className:"display-kicker",children:"Mission Phase"}),D.jsx("strong",{children:x}),D.jsx("p",{children:String(p.active_goal||g.title||"Standing by.")})]}),D.jsxs("div",{className:"display-card display-events","aria-label":"Recent Events",children:[D.jsx("span",{className:"display-kicker",children:"Recent Events"}),a.length?a.slice(0,6).map(E=>D.jsxs("div",{className:"event-row","data-severity":E.severity||"info",children:[D.jsx("span",{children:E.type}),D.jsx("strong",{children:E.message||E.source_type})]},`${E.type}-${E.source_updated_at}-${E.message}`)):D.jsxs("div",{className:"event-row","data-severity":"normal",children:[D.jsx("span",{children:"stream"}),D.jsx("strong",{children:"Waiting for live events"})]})]})]}),D.jsx(Lw,{servers:m,activeServerId:y})]})}function Lw({servers:s,activeServerId:t}){const n=pe.useMemo(()=>[...s].sort((a,l)=>Zl(a.server_id).localeCompare(Zl(l.server_id))),[s]);return D.jsx("footer",{className:"server-rail","aria-label":"Server rail",children:n.map(a=>{const l=Rm(a,t);return D.jsxs("article",{className:"server-rail__item","data-status":om(a.status),"data-expanded":l,children:[D.jsx("span",{className:"server-dot","aria-hidden":"true"}),D.jsx("strong",{children:Zl(a.server_id)}),l?D.jsx("span",{className:"server-rail__detail",children:a.status_detail||a.degraded_reason||a.recovery_hint||om(a.status)}):null]},a.server_id)})})}function Ow(s){const t=(s||[]).find(a=>String(a.status||"").toLowerCase()==="pending"||String(a.status||"").toLowerCase()==="ready");return String((t==null?void 0:t.capability_id)||"").split(".",1)[0]||""}function Pw({overview:s}){return D.jsxs("div",{className:"grid grid--three",children:[D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsx("h2",{children:"Mind Summary"})}),D.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(s.mind_summary.data,null,2)})]}),D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsx("h2",{children:"User State"})}),D.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(s.user_state.data,null,2)})]}),D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsx("h2",{children:"Commitments"})}),D.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(s.commitments.data,null,2)})]})]})}function zw(){return D.jsxs("div",{className:"grid grid--three",children:[D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsxs("h2",{children:[D.jsx(lx,{size:18})," Security"]})}),D.jsx("p",{className:"muted",children:"Passkey-only sessions and fresh authentication are enforced by the backend middleware."}),D.jsxs("a",{className:"primary-button",href:"/dashboard/security/passkeys",children:[D.jsx(d1,{size:16})," Passkeys"]})]}),D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsxs("h2",{children:[D.jsx(_1,{size:18})," Existing Settings"]})}),D.jsx("p",{className:"muted",children:"Detailed legacy-compatible settings APIs remain available after authentication."}),D.jsx("a",{className:"ghost-button",href:"/api/settings",children:"Settings API"})]}),D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsx("h2",{children:"Display"})}),D.jsx("p",{className:"muted",children:"The dedicated display opens read-only status and presentation UI, not this admin dashboard."}),D.jsx("a",{className:"ghost-button",href:"/display",children:"Open Display"})]})]})}function Iw({overview:s}){const t=s.servers.data.items||[];return D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsxs("div",{children:[D.jsx("h2",{children:"Systems"}),D.jsx("div",{className:"muted",children:"AI, PC, Android, Browser, Room, and Dev status."})]}),D.jsx(ar,{generatedAt:s.servers.generated_at,sourceUpdatedAt:s.servers.source_updated_at,stale:s.servers.stale})]}),D.jsx("div",{className:"grid",children:t.map(n=>D.jsxs("article",{className:"list-row",children:[D.jsxs("div",{children:[D.jsx("strong",{children:n.server_id}),D.jsxs("div",{className:"muted",children:[n.server_type||"service"," / ",n.mode||"unknown"," / ",n.host||"host",":",n.port||"-"]}),D.jsx("div",{className:"muted",children:n.status_detail||n.degraded_reason||n.recovery_hint||"No recovery action needed."})]}),D.jsx(Lo,{status:n.status,detail:n.recovery_hint})]},n.server_id))})]})}function Bw({overview:s}){const t=s.current_task.data;return D.jsxs("section",{className:"panel",children:[D.jsx("div",{className:"panel__header",children:D.jsxs("div",{children:[D.jsx("h2",{children:"Work"}),D.jsx("div",{className:"muted",children:"Active task, waiting state, and execution phase."})]})}),D.jsxs("div",{className:"grid",children:[D.jsxs("div",{className:"stat",children:[D.jsx("span",{className:"muted",children:"Current task"}),D.jsx("b",{style:{fontSize:18},children:t.title}),D.jsx("p",{className:"muted",children:t.current_action||t.blocked_reason||"No active execution."})]}),(t.steps||[]).map((n,a)=>D.jsx("div",{className:"list-row",children:D.jsxs("div",{children:[D.jsx("strong",{children:String(n.description||n.capability_id||`Step ${a+1}`)}),D.jsx("div",{className:"muted",children:String(n.status||"unknown")})]})},String(n.step_id||a)))]})]})}const Ny=[{id:"command",label:"Command Center",icon:h1,path:"/dashboard"},{id:"work",label:"Work",icon:c1,path:"/dashboard/work"},{id:"approvals",label:"Approvals",icon:lx,path:"/dashboard/approvals"},{id:"systems",label:"Systems",icon:p1,path:"/dashboard/systems"},{id:"mind",label:"Mind & Memory",icon:i1,path:"/dashboard/mind"},{id:"activity",label:"Activity",icon:ax,path:"/dashboard/activity"},{id:"settings",label:"Settings",icon:v1,path:"/settings"}];function Fw(){var y;const s=window.location.pathname.startsWith("/display"),t=ex(),[n,a]=pe.useState(window.location.pathname==="/chat"),[l,c]=pe.useState([]),f=pe.useMemo(()=>Gw(window.location.pathname),[]),[d,p]=pe.useState(f),m=$E({queryKey:["ui-overview",s?"display":"dashboard"],queryFn:()=>x1(s?"display":"dashboard"),refetchInterval:s?15e3:3e4}),g=pe.useCallback(x=>{"schema_version"in x||c(E=>[x,...E].slice(0,10)),t.invalidateQueries({queryKey:["ui-overview"]})},[t]);if(hx(g,!s),m.isLoading)return D.jsx(Vw,{displayMode:s});if(m.isError||!m.data)return D.jsx(kw,{message:m.error instanceof Error?m.error.message:"Overview unavailable"});if(s)return D.jsx(Nw,{overview:m.data});const v=m.data;return D.jsxs("div",{className:"app-shell",children:[D.jsxs("aside",{className:"side-nav",children:[D.jsxs("div",{className:"brand",children:[D.jsx("span",{className:"brand__name",children:"AEGIS"}),D.jsx("span",{className:"brand__sub",children:"Operational Console"})]}),D.jsx("nav",{className:"nav-list","aria-label":"Primary",children:Ny.map(x=>{const E=x.icon;return D.jsxs("button",{className:"nav-button","aria-current":d===x.id?"page":void 0,onClick:()=>{p(x.id),window.history.pushState(null,"",x.path)},children:[D.jsx(E,{size:17,"aria-hidden":"true"}),x.label]},x.id)})})]}),D.jsxs("main",{className:"content",children:[D.jsxs("header",{className:"top-bar",children:[D.jsxs("div",{className:"page-title",children:[D.jsx("h1",{children:((y=Ny.find(x=>x.id===d))==null?void 0:y.label)||"AEGIS"}),D.jsx("p",{children:"Live overview generated by Runtime managers, Policy, Approval, and Status services."})]}),D.jsxs("div",{style:{display:"flex",gap:12,alignItems:"center"},children:[D.jsx(Lo,{status:String(v.core.data.health||"ONLINE")}),D.jsx(ar,{generatedAt:v.generated_at,sourceUpdatedAt:v.freshness.source_updated_at,stale:v.freshness.stale}),D.jsx("button",{className:"icon-button",onClick:()=>a(!0),title:"Open chat",children:D.jsx(rx,{size:17,"aria-hidden":"true"})})]})]}),D.jsx(Hw,{page:d,overview:v,recentEvents:l})]}),D.jsx(E1,{open:n,onClose:()=>a(!1)})]})}function Hw({page:s,overview:t,recentEvents:n}){return s==="work"?D.jsx(Bw,{overview:t}):s==="approvals"?D.jsx(A1,{overview:t}):s==="systems"?D.jsx(Iw,{overview:t}):s==="mind"?D.jsx(Pw,{overview:t}):s==="activity"?D.jsx(b1,{overview:t,recentEvents:n}):s==="settings"?D.jsx(zw,{}):D.jsx(Uw,{overview:t,recentEvents:n})}function Gw(s){return s.includes("/work")?"work":s.includes("/approvals")?"approvals":s.includes("/systems")||s.includes("/servers")?"systems":s.includes("/mind")||s.includes("/memory")?"mind":s.includes("/activity")||s.includes("/audit")?"activity":s.includes("/settings")?"settings":"command"}function Vw({displayMode:s}){return D.jsx("main",{className:s?"display-shell":"app-shell",style:{display:"grid",placeItems:"center"},children:D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"Loading AEGIS UI"}),D.jsx(sx,{size:18})]}),D.jsx("p",{className:"muted",children:"Waiting for the normalized overview service."})]})})}function kw({message:s}){return D.jsx("main",{className:"display-shell",style:{display:"grid",placeItems:"center"},children:D.jsxs("section",{className:"panel",children:[D.jsxs("div",{className:"panel__header",children:[D.jsx("h2",{children:"AEGIS UI unavailable"}),D.jsx(Lo,{status:"OFFLINE"})]}),D.jsx("p",{className:"muted",children:s})]})})}const Xw=new HE({defaultOptions:{queries:{retry:1,staleTime:1e4}}});pE.createRoot(document.getElementById("root")).render(D.jsx(rE.StrictMode,{children:D.jsx(GE,{client:Xw,children:D.jsx(Fw,{})})}));
