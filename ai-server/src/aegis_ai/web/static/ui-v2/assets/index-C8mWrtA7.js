var b0=a=>{throw TypeError(a)};var Dh=(a,t,n)=>t.has(a)||b0("Cannot "+n);var X=(a,t,n)=>(Dh(a,t,"read from private field"),n?n.call(a):t.get(a)),te=(a,t,n)=>t.has(a)?b0("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(a):t.set(a,n),zt=(a,t,n,s)=>(Dh(a,t,"write to private field"),s?s.call(a,n):t.set(a,n),n),Ae=(a,t,n)=>(Dh(a,t,"access private method"),n);var Nu=(a,t,n,s)=>({set _(o){zt(a,t,o,n)},get _(){return X(a,t,s)}});(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const o of document.querySelectorAll('link[rel="modulepreload"]'))s(o);new MutationObserver(o=>{for(const c of o)if(c.type==="childList")for(const f of c.addedNodes)f.tagName==="LINK"&&f.rel==="modulepreload"&&s(f)}).observe(document,{childList:!0,subtree:!0});function n(o){const c={};return o.integrity&&(c.integrity=o.integrity),o.referrerPolicy&&(c.referrerPolicy=o.referrerPolicy),o.crossOrigin==="use-credentials"?c.credentials="include":o.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function s(o){if(o.ep)return;o.ep=!0;const c=n(o);fetch(o.href,c)}})();function fx(a){return a&&a.__esModule&&Object.prototype.hasOwnProperty.call(a,"default")?a.default:a}var Uh={exports:{}},Gl={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var T0;function N1(){if(T0)return Gl;T0=1;var a=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function n(s,o,c){var f=null;if(c!==void 0&&(f=""+c),o.key!==void 0&&(f=""+o.key),"key"in o){c={};for(var d in o)d!=="key"&&(c[d]=o[d])}else c=o;return o=c.ref,{$$typeof:a,type:s,key:f,ref:o!==void 0?o:null,props:c}}return Gl.Fragment=t,Gl.jsx=n,Gl.jsxs=n,Gl}var A0;function D1(){return A0||(A0=1,Uh.exports=N1()),Uh.exports}var g=D1(),Lh={exports:{}},re={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var C0;function U1(){if(C0)return re;C0=1;var a=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),n=Symbol.for("react.fragment"),s=Symbol.for("react.strict_mode"),o=Symbol.for("react.profiler"),c=Symbol.for("react.consumer"),f=Symbol.for("react.context"),d=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),m=Symbol.for("react.memo"),v=Symbol.for("react.lazy"),_=Symbol.for("react.activity"),x=Symbol.iterator;function E(z){return z===null||typeof z!="object"?null:(z=x&&z[x]||z["@@iterator"],typeof z=="function"?z:null)}var M={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},T=Object.assign,S={};function y(z,nt,St){this.props=z,this.context=nt,this.refs=S,this.updater=St||M}y.prototype.isReactComponent={},y.prototype.setState=function(z,nt){if(typeof z!="object"&&typeof z!="function"&&z!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,z,nt,"setState")},y.prototype.forceUpdate=function(z){this.updater.enqueueForceUpdate(this,z,"forceUpdate")};function I(){}I.prototype=y.prototype;function D(z,nt,St){this.props=z,this.context=nt,this.refs=S,this.updater=St||M}var C=D.prototype=new I;C.constructor=D,T(C,y.prototype),C.isPureReactComponent=!0;var V=Array.isArray;function L(){}var P={H:null,A:null,T:null,S:null},G=Object.prototype.hasOwnProperty;function U(z,nt,St){var q=St.ref;return{$$typeof:a,type:z,key:nt,ref:q!==void 0?q:null,props:St}}function N(z,nt){return U(z.type,nt,z.props)}function H(z){return typeof z=="object"&&z!==null&&z.$$typeof===a}function ut(z){var nt={"=":"=0",":":"=2"};return"$"+z.replace(/[=:]/g,function(St){return nt[St]})}var ot=/\/+/g;function mt(z,nt){return typeof z=="object"&&z!==null&&z.key!=null?ut(""+z.key):nt.toString(36)}function ct(z){switch(z.status){case"fulfilled":return z.value;case"rejected":throw z.reason;default:switch(typeof z.status=="string"?z.then(L,L):(z.status="pending",z.then(function(nt){z.status==="pending"&&(z.status="fulfilled",z.value=nt)},function(nt){z.status==="pending"&&(z.status="rejected",z.reason=nt)})),z.status){case"fulfilled":return z.value;case"rejected":throw z.reason}}throw z}function B(z,nt,St,q,ft){var Tt=typeof z;(Tt==="undefined"||Tt==="boolean")&&(z=null);var Mt=!1;if(z===null)Mt=!0;else switch(Tt){case"bigint":case"string":case"number":Mt=!0;break;case"object":switch(z.$$typeof){case a:case t:Mt=!0;break;case v:return Mt=z._init,B(Mt(z._payload),nt,St,q,ft)}}if(Mt)return ft=ft(z),Mt=q===""?"."+mt(z,0):q,V(ft)?(St="",Mt!=null&&(St=Mt.replace(ot,"$&/")+"/"),B(ft,nt,St,"",function(oe){return oe})):ft!=null&&(H(ft)&&(ft=N(ft,St+(ft.key==null||z&&z.key===ft.key?"":(""+ft.key).replace(ot,"$&/")+"/")+Mt)),nt.push(ft)),1;Mt=0;var Ft=q===""?".":q+":";if(V(z))for(var Vt=0;Vt<z.length;Vt++)q=z[Vt],Tt=Ft+mt(q,Vt),Mt+=B(q,nt,St,Tt,ft);else if(Vt=E(z),typeof Vt=="function")for(z=Vt.call(z),Vt=0;!(q=z.next()).done;)q=q.value,Tt=Ft+mt(q,Vt++),Mt+=B(q,nt,St,Tt,ft);else if(Tt==="object"){if(typeof z.then=="function")return B(ct(z),nt,St,q,ft);throw nt=String(z),Error("Objects are not valid as a React child (found: "+(nt==="[object Object]"?"object with keys {"+Object.keys(z).join(", ")+"}":nt)+"). If you meant to render a collection of children, use an array instead.")}return Mt}function Z(z,nt,St){if(z==null)return z;var q=[],ft=0;return B(z,q,"","",function(Tt){return nt.call(St,Tt,ft++)}),q}function $(z){if(z._status===-1){var nt=z._result;nt=nt(),nt.then(function(St){(z._status===0||z._status===-1)&&(z._status=1,z._result=St)},function(St){(z._status===0||z._status===-1)&&(z._status=2,z._result=St)}),z._status===-1&&(z._status=0,z._result=nt)}if(z._status===1)return z._result.default;throw z._result}var Et=typeof reportError=="function"?reportError:function(z){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var nt=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof z=="object"&&z!==null&&typeof z.message=="string"?String(z.message):String(z),error:z});if(!window.dispatchEvent(nt))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",z);return}console.error(z)},At={map:Z,forEach:function(z,nt,St){Z(z,function(){nt.apply(this,arguments)},St)},count:function(z){var nt=0;return Z(z,function(){nt++}),nt},toArray:function(z){return Z(z,function(nt){return nt})||[]},only:function(z){if(!H(z))throw Error("React.Children.only expected to receive a single React element child.");return z}};return re.Activity=_,re.Children=At,re.Component=y,re.Fragment=n,re.Profiler=o,re.PureComponent=D,re.StrictMode=s,re.Suspense=p,re.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=P,re.__COMPILER_RUNTIME={__proto__:null,c:function(z){return P.H.useMemoCache(z)}},re.cache=function(z){return function(){return z.apply(null,arguments)}},re.cacheSignal=function(){return null},re.cloneElement=function(z,nt,St){if(z==null)throw Error("The argument must be a React element, but you passed "+z+".");var q=T({},z.props),ft=z.key;if(nt!=null)for(Tt in nt.key!==void 0&&(ft=""+nt.key),nt)!G.call(nt,Tt)||Tt==="key"||Tt==="__self"||Tt==="__source"||Tt==="ref"&&nt.ref===void 0||(q[Tt]=nt[Tt]);var Tt=arguments.length-2;if(Tt===1)q.children=St;else if(1<Tt){for(var Mt=Array(Tt),Ft=0;Ft<Tt;Ft++)Mt[Ft]=arguments[Ft+2];q.children=Mt}return U(z.type,ft,q)},re.createContext=function(z){return z={$$typeof:f,_currentValue:z,_currentValue2:z,_threadCount:0,Provider:null,Consumer:null},z.Provider=z,z.Consumer={$$typeof:c,_context:z},z},re.createElement=function(z,nt,St){var q,ft={},Tt=null;if(nt!=null)for(q in nt.key!==void 0&&(Tt=""+nt.key),nt)G.call(nt,q)&&q!=="key"&&q!=="__self"&&q!=="__source"&&(ft[q]=nt[q]);var Mt=arguments.length-2;if(Mt===1)ft.children=St;else if(1<Mt){for(var Ft=Array(Mt),Vt=0;Vt<Mt;Vt++)Ft[Vt]=arguments[Vt+2];ft.children=Ft}if(z&&z.defaultProps)for(q in Mt=z.defaultProps,Mt)ft[q]===void 0&&(ft[q]=Mt[q]);return U(z,Tt,ft)},re.createRef=function(){return{current:null}},re.forwardRef=function(z){return{$$typeof:d,render:z}},re.isValidElement=H,re.lazy=function(z){return{$$typeof:v,_payload:{_status:-1,_result:z},_init:$}},re.memo=function(z,nt){return{$$typeof:m,type:z,compare:nt===void 0?null:nt}},re.startTransition=function(z){var nt=P.T,St={};P.T=St;try{var q=z(),ft=P.S;ft!==null&&ft(St,q),typeof q=="object"&&q!==null&&typeof q.then=="function"&&q.then(L,Et)}catch(Tt){Et(Tt)}finally{nt!==null&&St.types!==null&&(nt.types=St.types),P.T=nt}},re.unstable_useCacheRefresh=function(){return P.H.useCacheRefresh()},re.use=function(z){return P.H.use(z)},re.useActionState=function(z,nt,St){return P.H.useActionState(z,nt,St)},re.useCallback=function(z,nt){return P.H.useCallback(z,nt)},re.useContext=function(z){return P.H.useContext(z)},re.useDebugValue=function(){},re.useDeferredValue=function(z,nt){return P.H.useDeferredValue(z,nt)},re.useEffect=function(z,nt){return P.H.useEffect(z,nt)},re.useEffectEvent=function(z){return P.H.useEffectEvent(z)},re.useId=function(){return P.H.useId()},re.useImperativeHandle=function(z,nt,St){return P.H.useImperativeHandle(z,nt,St)},re.useInsertionEffect=function(z,nt){return P.H.useInsertionEffect(z,nt)},re.useLayoutEffect=function(z,nt){return P.H.useLayoutEffect(z,nt)},re.useMemo=function(z,nt){return P.H.useMemo(z,nt)},re.useOptimistic=function(z,nt){return P.H.useOptimistic(z,nt)},re.useReducer=function(z,nt,St){return P.H.useReducer(z,nt,St)},re.useRef=function(z){return P.H.useRef(z)},re.useState=function(z){return P.H.useState(z)},re.useSyncExternalStore=function(z,nt,St){return P.H.useSyncExternalStore(z,nt,St)},re.useTransition=function(){return P.H.useTransition()},re.version="19.2.7",re}var R0;function Mm(){return R0||(R0=1,Lh.exports=U1()),Lh.exports}var se=Mm();const L1=fx(se);var Oh={exports:{}},Vl={},Ph={exports:{}},zh={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var w0;function O1(){return w0||(w0=1,(function(a){function t(B,Z){var $=B.length;B.push(Z);t:for(;0<$;){var Et=$-1>>>1,At=B[Et];if(0<o(At,Z))B[Et]=Z,B[$]=At,$=Et;else break t}}function n(B){return B.length===0?null:B[0]}function s(B){if(B.length===0)return null;var Z=B[0],$=B.pop();if($!==Z){B[0]=$;t:for(var Et=0,At=B.length,z=At>>>1;Et<z;){var nt=2*(Et+1)-1,St=B[nt],q=nt+1,ft=B[q];if(0>o(St,$))q<At&&0>o(ft,St)?(B[Et]=ft,B[q]=$,Et=q):(B[Et]=St,B[nt]=$,Et=nt);else if(q<At&&0>o(ft,$))B[Et]=ft,B[q]=$,Et=q;else break t}}return Z}function o(B,Z){var $=B.sortIndex-Z.sortIndex;return $!==0?$:B.id-Z.id}if(a.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var c=performance;a.unstable_now=function(){return c.now()}}else{var f=Date,d=f.now();a.unstable_now=function(){return f.now()-d}}var p=[],m=[],v=1,_=null,x=3,E=!1,M=!1,T=!1,S=!1,y=typeof setTimeout=="function"?setTimeout:null,I=typeof clearTimeout=="function"?clearTimeout:null,D=typeof setImmediate<"u"?setImmediate:null;function C(B){for(var Z=n(m);Z!==null;){if(Z.callback===null)s(m);else if(Z.startTime<=B)s(m),Z.sortIndex=Z.expirationTime,t(p,Z);else break;Z=n(m)}}function V(B){if(T=!1,C(B),!M)if(n(p)!==null)M=!0,L||(L=!0,ut());else{var Z=n(m);Z!==null&&ct(V,Z.startTime-B)}}var L=!1,P=-1,G=5,U=-1;function N(){return S?!0:!(a.unstable_now()-U<G)}function H(){if(S=!1,L){var B=a.unstable_now();U=B;var Z=!0;try{t:{M=!1,T&&(T=!1,I(P),P=-1),E=!0;var $=x;try{e:{for(C(B),_=n(p);_!==null&&!(_.expirationTime>B&&N());){var Et=_.callback;if(typeof Et=="function"){_.callback=null,x=_.priorityLevel;var At=Et(_.expirationTime<=B);if(B=a.unstable_now(),typeof At=="function"){_.callback=At,C(B),Z=!0;break e}_===n(p)&&s(p),C(B)}else s(p);_=n(p)}if(_!==null)Z=!0;else{var z=n(m);z!==null&&ct(V,z.startTime-B),Z=!1}}break t}finally{_=null,x=$,E=!1}Z=void 0}}finally{Z?ut():L=!1}}}var ut;if(typeof D=="function")ut=function(){D(H)};else if(typeof MessageChannel<"u"){var ot=new MessageChannel,mt=ot.port2;ot.port1.onmessage=H,ut=function(){mt.postMessage(null)}}else ut=function(){y(H,0)};function ct(B,Z){P=y(function(){B(a.unstable_now())},Z)}a.unstable_IdlePriority=5,a.unstable_ImmediatePriority=1,a.unstable_LowPriority=4,a.unstable_NormalPriority=3,a.unstable_Profiling=null,a.unstable_UserBlockingPriority=2,a.unstable_cancelCallback=function(B){B.callback=null},a.unstable_forceFrameRate=function(B){0>B||125<B?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):G=0<B?Math.floor(1e3/B):5},a.unstable_getCurrentPriorityLevel=function(){return x},a.unstable_next=function(B){switch(x){case 1:case 2:case 3:var Z=3;break;default:Z=x}var $=x;x=Z;try{return B()}finally{x=$}},a.unstable_requestPaint=function(){S=!0},a.unstable_runWithPriority=function(B,Z){switch(B){case 1:case 2:case 3:case 4:case 5:break;default:B=3}var $=x;x=B;try{return Z()}finally{x=$}},a.unstable_scheduleCallback=function(B,Z,$){var Et=a.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?Et+$:Et):$=Et,B){case 1:var At=-1;break;case 2:At=250;break;case 5:At=1073741823;break;case 4:At=1e4;break;default:At=5e3}return At=$+At,B={id:v++,callback:Z,priorityLevel:B,startTime:$,expirationTime:At,sortIndex:-1},$>Et?(B.sortIndex=$,t(m,B),n(p)===null&&B===n(m)&&(T?(I(P),P=-1):T=!0,ct(V,$-Et))):(B.sortIndex=At,t(p,B),M||E||(M=!0,L||(L=!0,ut()))),B},a.unstable_shouldYield=N,a.unstable_wrapCallback=function(B){var Z=x;return function(){var $=x;x=Z;try{return B.apply(this,arguments)}finally{x=$}}}})(zh)),zh}var N0;function P1(){return N0||(N0=1,Ph.exports=O1()),Ph.exports}var Ih={exports:{}},In={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var D0;function z1(){if(D0)return In;D0=1;var a=Mm();function t(p){var m="https://react.dev/errors/"+p;if(1<arguments.length){m+="?args[]="+encodeURIComponent(arguments[1]);for(var v=2;v<arguments.length;v++)m+="&args[]="+encodeURIComponent(arguments[v])}return"Minified React error #"+p+"; visit "+m+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function n(){}var s={d:{f:n,r:function(){throw Error(t(522))},D:n,C:n,L:n,m:n,X:n,S:n,M:n},p:0,findDOMNode:null},o=Symbol.for("react.portal");function c(p,m,v){var _=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:o,key:_==null?null:""+_,children:p,containerInfo:m,implementation:v}}var f=a.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function d(p,m){if(p==="font")return"";if(typeof m=="string")return m==="use-credentials"?m:""}return In.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=s,In.createPortal=function(p,m){var v=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!m||m.nodeType!==1&&m.nodeType!==9&&m.nodeType!==11)throw Error(t(299));return c(p,m,null,v)},In.flushSync=function(p){var m=f.T,v=s.p;try{if(f.T=null,s.p=2,p)return p()}finally{f.T=m,s.p=v,s.d.f()}},In.preconnect=function(p,m){typeof p=="string"&&(m?(m=m.crossOrigin,m=typeof m=="string"?m==="use-credentials"?m:"":void 0):m=null,s.d.C(p,m))},In.prefetchDNS=function(p){typeof p=="string"&&s.d.D(p)},In.preinit=function(p,m){if(typeof p=="string"&&m&&typeof m.as=="string"){var v=m.as,_=d(v,m.crossOrigin),x=typeof m.integrity=="string"?m.integrity:void 0,E=typeof m.fetchPriority=="string"?m.fetchPriority:void 0;v==="style"?s.d.S(p,typeof m.precedence=="string"?m.precedence:void 0,{crossOrigin:_,integrity:x,fetchPriority:E}):v==="script"&&s.d.X(p,{crossOrigin:_,integrity:x,fetchPriority:E,nonce:typeof m.nonce=="string"?m.nonce:void 0})}},In.preinitModule=function(p,m){if(typeof p=="string")if(typeof m=="object"&&m!==null){if(m.as==null||m.as==="script"){var v=d(m.as,m.crossOrigin);s.d.M(p,{crossOrigin:v,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0})}}else m==null&&s.d.M(p)},In.preload=function(p,m){if(typeof p=="string"&&typeof m=="object"&&m!==null&&typeof m.as=="string"){var v=m.as,_=d(v,m.crossOrigin);s.d.L(p,v,{crossOrigin:_,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0,type:typeof m.type=="string"?m.type:void 0,fetchPriority:typeof m.fetchPriority=="string"?m.fetchPriority:void 0,referrerPolicy:typeof m.referrerPolicy=="string"?m.referrerPolicy:void 0,imageSrcSet:typeof m.imageSrcSet=="string"?m.imageSrcSet:void 0,imageSizes:typeof m.imageSizes=="string"?m.imageSizes:void 0,media:typeof m.media=="string"?m.media:void 0})}},In.preloadModule=function(p,m){if(typeof p=="string")if(m){var v=d(m.as,m.crossOrigin);s.d.m(p,{as:typeof m.as=="string"&&m.as!=="script"?m.as:void 0,crossOrigin:v,integrity:typeof m.integrity=="string"?m.integrity:void 0})}else s.d.m(p)},In.requestFormReset=function(p){s.d.r(p)},In.unstable_batchedUpdates=function(p,m){return p(m)},In.useFormState=function(p,m,v){return f.H.useFormState(p,m,v)},In.useFormStatus=function(){return f.H.useHostTransitionStatus()},In.version="19.2.7",In}var U0;function I1(){if(U0)return Ih.exports;U0=1;function a(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(a)}catch(t){console.error(t)}}return a(),Ih.exports=z1(),Ih.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var L0;function B1(){if(L0)return Vl;L0=1;var a=P1(),t=Mm(),n=I1();function s(e){var i="https://react.dev/errors/"+e;if(1<arguments.length){i+="?args[]="+encodeURIComponent(arguments[1]);for(var r=2;r<arguments.length;r++)i+="&args[]="+encodeURIComponent(arguments[r])}return"Minified React error #"+e+"; visit "+i+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function o(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function c(e){var i=e,r=e;if(e.alternate)for(;i.return;)i=i.return;else{e=i;do i=e,(i.flags&4098)!==0&&(r=i.return),e=i.return;while(e)}return i.tag===3?r:null}function f(e){if(e.tag===13){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function d(e){if(e.tag===31){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function p(e){if(c(e)!==e)throw Error(s(188))}function m(e){var i=e.alternate;if(!i){if(i=c(e),i===null)throw Error(s(188));return i!==e?null:e}for(var r=e,l=i;;){var u=r.return;if(u===null)break;var h=u.alternate;if(h===null){if(l=u.return,l!==null){r=l;continue}break}if(u.child===h.child){for(h=u.child;h;){if(h===r)return p(u),e;if(h===l)return p(u),i;h=h.sibling}throw Error(s(188))}if(r.return!==l.return)r=u,l=h;else{for(var b=!1,A=u.child;A;){if(A===r){b=!0,r=u,l=h;break}if(A===l){b=!0,l=u,r=h;break}A=A.sibling}if(!b){for(A=h.child;A;){if(A===r){b=!0,r=h,l=u;break}if(A===l){b=!0,l=h,r=u;break}A=A.sibling}if(!b)throw Error(s(189))}}if(r.alternate!==l)throw Error(s(190))}if(r.tag!==3)throw Error(s(188));return r.stateNode.current===r?e:i}function v(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e;for(e=e.child;e!==null;){if(i=v(e),i!==null)return i;e=e.sibling}return null}var _=Object.assign,x=Symbol.for("react.element"),E=Symbol.for("react.transitional.element"),M=Symbol.for("react.portal"),T=Symbol.for("react.fragment"),S=Symbol.for("react.strict_mode"),y=Symbol.for("react.profiler"),I=Symbol.for("react.consumer"),D=Symbol.for("react.context"),C=Symbol.for("react.forward_ref"),V=Symbol.for("react.suspense"),L=Symbol.for("react.suspense_list"),P=Symbol.for("react.memo"),G=Symbol.for("react.lazy"),U=Symbol.for("react.activity"),N=Symbol.for("react.memo_cache_sentinel"),H=Symbol.iterator;function ut(e){return e===null||typeof e!="object"?null:(e=H&&e[H]||e["@@iterator"],typeof e=="function"?e:null)}var ot=Symbol.for("react.client.reference");function mt(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===ot?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case T:return"Fragment";case y:return"Profiler";case S:return"StrictMode";case V:return"Suspense";case L:return"SuspenseList";case U:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case M:return"Portal";case D:return e.displayName||"Context";case I:return(e._context.displayName||"Context")+".Consumer";case C:var i=e.render;return e=e.displayName,e||(e=i.displayName||i.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case P:return i=e.displayName||null,i!==null?i:mt(e.type)||"Memo";case G:i=e._payload,e=e._init;try{return mt(e(i))}catch{}}return null}var ct=Array.isArray,B=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,Z=n.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,$={pending:!1,data:null,method:null,action:null},Et=[],At=-1;function z(e){return{current:e}}function nt(e){0>At||(e.current=Et[At],Et[At]=null,At--)}function St(e,i){At++,Et[At]=e.current,e.current=i}var q=z(null),ft=z(null),Tt=z(null),Mt=z(null);function Ft(e,i){switch(St(Tt,i),St(ft,e),St(q,null),i.nodeType){case 9:case 11:e=(e=i.documentElement)&&(e=e.namespaceURI)?W_(e):0;break;default:if(e=i.tagName,i=i.namespaceURI)i=W_(i),e=Y_(i,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}nt(q),St(q,e)}function Vt(){nt(q),nt(ft),nt(Tt)}function oe(e){e.memoizedState!==null&&St(Mt,e);var i=q.current,r=Y_(i,e.type);i!==r&&(St(ft,e),St(q,r))}function Ge(e){ft.current===e&&(nt(q),nt(ft)),Mt.current===e&&(nt(Mt),Il._currentValue=$)}var ve,$e;function j(e){if(ve===void 0)try{throw Error()}catch(r){var i=r.stack.trim().match(/\n( *(at )?)/);ve=i&&i[1]||"",$e=-1<r.stack.indexOf(`
    at`)?" (<anonymous>)":-1<r.stack.indexOf("@")?"@unknown:0:0":""}return`
`+ve+e+$e}var Pn=!1;function me(e,i){if(!e||Pn)return"";Pn=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var l={DetermineComponentFrameRoot:function(){try{if(i){var _t=function(){throw Error()};if(Object.defineProperty(_t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(_t,[])}catch(lt){var it=lt}Reflect.construct(e,[],_t)}else{try{_t.call()}catch(lt){it=lt}e.call(_t.prototype)}}else{try{throw Error()}catch(lt){it=lt}(_t=e())&&typeof _t.catch=="function"&&_t.catch(function(){})}}catch(lt){if(lt&&it&&typeof lt.stack=="string")return[lt.stack,it.stack]}return[null,null]}};l.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var u=Object.getOwnPropertyDescriptor(l.DetermineComponentFrameRoot,"name");u&&u.configurable&&Object.defineProperty(l.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var h=l.DetermineComponentFrameRoot(),b=h[0],A=h[1];if(b&&A){var F=b.split(`
`),et=A.split(`
`);for(u=l=0;l<F.length&&!F[l].includes("DetermineComponentFrameRoot");)l++;for(;u<et.length&&!et[u].includes("DetermineComponentFrameRoot");)u++;if(l===F.length||u===et.length)for(l=F.length-1,u=et.length-1;1<=l&&0<=u&&F[l]!==et[u];)u--;for(;1<=l&&0<=u;l--,u--)if(F[l]!==et[u]){if(l!==1||u!==1)do if(l--,u--,0>u||F[l]!==et[u]){var ht=`
`+F[l].replace(" at new "," at ");return e.displayName&&ht.includes("<anonymous>")&&(ht=ht.replace("<anonymous>",e.displayName)),ht}while(1<=l&&0<=u);break}}}finally{Pn=!1,Error.prepareStackTrace=r}return(r=e?e.displayName||e.name:"")?j(r):""}function Se(e,i){switch(e.tag){case 26:case 27:case 5:return j(e.type);case 16:return j("Lazy");case 13:return e.child!==i&&i!==null?j("Suspense Fallback"):j("Suspense");case 19:return j("SuspenseList");case 0:case 15:return me(e.type,!1);case 11:return me(e.type.render,!1);case 1:return me(e.type,!0);case 31:return j("Activity");default:return""}}function Qt(e){try{var i="",r=null;do i+=Se(e,r),r=e,e=e.return;while(e);return i}catch(l){return`
Error generating stack: `+l.message+`
`+l.stack}}var Be=Object.prototype.hasOwnProperty,Yt=a.unstable_scheduleCallback,O=a.unstable_cancelCallback,R=a.unstable_shouldYield,at=a.unstable_requestPaint,pt=a.unstable_now,bt=a.unstable_getCurrentPriorityLevel,vt=a.unstable_ImmediatePriority,Xt=a.unstable_UserBlockingPriority,Nt=a.unstable_NormalPriority,Bt=a.unstable_LowPriority,Me=a.unstable_IdlePriority,Ct=a.log,Ht=a.unstable_setDisableYieldValue,Zt=null,qt=null;function Ot(e){if(typeof Ct=="function"&&Ht(e),qt&&typeof qt.setStrictMode=="function")try{qt.setStrictMode(Zt,e)}catch{}}var ne=Math.clz32?Math.clz32:Y,le=Math.log,Ve=Math.LN2;function Y(e){return e>>>=0,e===0?32:31-(le(e)/Ve|0)|0}var Rt=256,dt=262144,yt=4194304;function wt(e){var i=e&42;if(i!==0)return i;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Dt(e,i,r){var l=e.pendingLanes;if(l===0)return 0;var u=0,h=e.suspendedLanes,b=e.pingedLanes;e=e.warmLanes;var A=l&134217727;return A!==0?(l=A&~h,l!==0?u=wt(l):(b&=A,b!==0?u=wt(b):r||(r=A&~e,r!==0&&(u=wt(r))))):(A=l&~h,A!==0?u=wt(A):b!==0?u=wt(b):r||(r=l&~e,r!==0&&(u=wt(r)))),u===0?0:i!==0&&i!==u&&(i&h)===0&&(h=u&-u,r=i&-i,h>=r||h===32&&(r&4194048)!==0)?i:u}function ie(e,i){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&i)===0}function tn(e,i){switch(e){case 1:case 2:case 4:case 8:case 64:return i+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return i+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function _n(){var e=yt;return yt<<=1,(yt&62914560)===0&&(yt=4194304),e}function Ne(e){for(var i=[],r=0;31>r;r++)i.push(e);return i}function Rn(e,i){e.pendingLanes|=i,i!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function wi(e,i,r,l,u,h){var b=e.pendingLanes;e.pendingLanes=r,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=r,e.entangledLanes&=r,e.errorRecoveryDisabledLanes&=r,e.shellSuspendCounter=0;var A=e.entanglements,F=e.expirationTimes,et=e.hiddenUpdates;for(r=b&~r;0<r;){var ht=31-ne(r),_t=1<<ht;A[ht]=0,F[ht]=-1;var it=et[ht];if(it!==null)for(et[ht]=null,ht=0;ht<it.length;ht++){var lt=it[ht];lt!==null&&(lt.lane&=-536870913)}r&=~_t}l!==0&&Zo(e,l,0),h!==0&&u===0&&e.tag!==0&&(e.suspendedLanes|=h&~(b&~i))}function Zo(e,i,r){e.pendingLanes|=i,e.suspendedLanes&=~i;var l=31-ne(i);e.entangledLanes|=i,e.entanglements[l]=e.entanglements[l]|1073741824|r&261930}function Ko(e,i){var r=e.entangledLanes|=i;for(e=e.entanglements;r;){var l=31-ne(r),u=1<<l;u&i|e[l]&i&&(e[l]|=i),r&=~u}}function ji(e,i){var r=i&-i;return r=(r&42)!==0?1:ws(r),(r&(e.suspendedLanes|i))!==0?0:r}function ws(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function Mr(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function Jo(){var e=Z.p;return e!==0?e:(e=window.event,e===void 0?32:v0(e.type))}function Ns(e,i){var r=Z.p;try{return Z.p=e,i()}finally{Z.p=r}}var Ni=Math.random().toString(36).slice(2),sn="__reactFiber$"+Ni,wn="__reactProps$"+Ni,na="__reactContainer$"+Ni,$o="__reactEvents$"+Ni,Tf="__reactListeners$"+Ni,Af="__reactHandles$"+Ni,xc="__reactResources$"+Ni,Ds="__reactMarker$"+Ni;function w(e){delete e[sn],delete e[wn],delete e[$o],delete e[Tf],delete e[Af]}function Q(e){var i=e[sn];if(i)return i;for(var r=e.parentNode;r;){if(i=r[na]||r[sn]){if(r=i.alternate,i.child!==null||r!==null&&r.child!==null)for(e=e0(e);e!==null;){if(r=e[sn])return r;e=e0(e)}return i}e=r,r=e.parentNode}return null}function st(e){if(e=e[sn]||e[na]){var i=e.tag;if(i===5||i===6||i===13||i===31||i===26||i===27||i===3)return e}return null}function rt(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e.stateNode;throw Error(s(33))}function K(e){var i=e[xc];return i||(i=e[xc]={hoistableStyles:new Map,hoistableScripts:new Map}),i}function xt(e){e[Ds]=!0}var Ut=new Set,It={};function Pt(e,i){$t(e,i),$t(e+"Capture",i)}function $t(e,i){for(It[e]=i,e=0;e<i.length;e++)Ut.add(i[e])}var ae=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Kt={},Ee={};function De(e){return Be.call(Ee,e)?!0:Be.call(Kt,e)?!1:ae.test(e)?Ee[e]=!0:(Kt[e]=!0,!1)}function Ze(e,i,r){if(De(i))if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":e.removeAttribute(i);return;case"boolean":var l=i.toLowerCase().slice(0,5);if(l!=="data-"&&l!=="aria-"){e.removeAttribute(i);return}}e.setAttribute(i,""+r)}}function Ye(e,i,r){if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(i);return}e.setAttribute(i,""+r)}}function ce(e,i,r,l){if(l===null)e.removeAttribute(r);else{switch(typeof l){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(r);return}e.setAttributeNS(i,r,""+l)}}function jt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function dn(e){var i=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(i==="checkbox"||i==="radio")}function Ue(e,i,r){var l=Object.getOwnPropertyDescriptor(e.constructor.prototype,i);if(!e.hasOwnProperty(i)&&typeof l<"u"&&typeof l.get=="function"&&typeof l.set=="function"){var u=l.get,h=l.set;return Object.defineProperty(e,i,{configurable:!0,get:function(){return u.call(this)},set:function(b){r=""+b,h.call(this,b)}}),Object.defineProperty(e,i,{enumerable:l.enumerable}),{getValue:function(){return r},setValue:function(b){r=""+b},stopTracking:function(){e._valueTracker=null,delete e[i]}}}}function Gn(e){if(!e._valueTracker){var i=dn(e)?"checked":"value";e._valueTracker=Ue(e,i,""+e[i])}}function ia(e){if(!e)return!1;var i=e._valueTracker;if(!i)return!0;var r=i.getValue(),l="";return e&&(l=dn(e)?e.checked?"true":"false":e.value),e=l,e!==r?(i.setValue(e),!0):!1}function En(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Us=/[\n"\\]/g;function _e(e){return e.replace(Us,function(i){return"\\"+i.charCodeAt(0).toString(16)+" "})}function zn(e,i,r,l,u,h,b,A){e.name="",b!=null&&typeof b!="function"&&typeof b!="symbol"&&typeof b!="boolean"?e.type=b:e.removeAttribute("type"),i!=null?b==="number"?(i===0&&e.value===""||e.value!=i)&&(e.value=""+jt(i)):e.value!==""+jt(i)&&(e.value=""+jt(i)):b!=="submit"&&b!=="reset"||e.removeAttribute("value"),i!=null?yn(e,b,jt(i)):r!=null?yn(e,b,jt(r)):l!=null&&e.removeAttribute("value"),u==null&&h!=null&&(e.defaultChecked=!!h),u!=null&&(e.checked=u&&typeof u!="function"&&typeof u!="symbol"),A!=null&&typeof A!="function"&&typeof A!="symbol"&&typeof A!="boolean"?e.name=""+jt(A):e.removeAttribute("name")}function Vn(e,i,r,l,u,h,b,A){if(h!=null&&typeof h!="function"&&typeof h!="symbol"&&typeof h!="boolean"&&(e.type=h),i!=null||r!=null){if(!(h!=="submit"&&h!=="reset"||i!=null)){Gn(e);return}r=r!=null?""+jt(r):"",i=i!=null?""+jt(i):r,A||i===e.value||(e.value=i),e.defaultValue=i}l=l??u,l=typeof l!="function"&&typeof l!="symbol"&&!!l,e.checked=A?e.checked:!!l,e.defaultChecked=!!l,b!=null&&typeof b!="function"&&typeof b!="symbol"&&typeof b!="boolean"&&(e.name=b),Gn(e)}function yn(e,i,r){i==="number"&&En(e.ownerDocument)===e||e.defaultValue===""+r||(e.defaultValue=""+r)}function cn(e,i,r,l){if(e=e.options,i){i={};for(var u=0;u<r.length;u++)i["$"+r[u]]=!0;for(r=0;r<e.length;r++)u=i.hasOwnProperty("$"+e[r].value),e[r].selected!==u&&(e[r].selected=u),u&&l&&(e[r].defaultSelected=!0)}else{for(r=""+jt(r),i=null,u=0;u<e.length;u++){if(e[u].value===r){e[u].selected=!0,l&&(e[u].defaultSelected=!0);return}i!==null||e[u].disabled||(i=e[u])}i!==null&&(i.selected=!0)}}function Er(e,i,r){if(i!=null&&(i=""+jt(i),i!==e.value&&(e.value=i),r==null)){e.defaultValue!==i&&(e.defaultValue=i);return}e.defaultValue=r!=null?""+jt(r):""}function ki(e,i,r,l){if(i==null){if(l!=null){if(r!=null)throw Error(s(92));if(ct(l)){if(1<l.length)throw Error(s(93));l=l[0]}r=l}r==null&&(r=""),i=r}r=jt(i),e.defaultValue=r,l=e.textContent,l===r&&l!==""&&l!==null&&(e.value=l),Gn(e)}function br(e,i){if(i){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=i;return}}e.textContent=i}var TS=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function km(e,i,r){var l=i.indexOf("--")===0;r==null||typeof r=="boolean"||r===""?l?e.setProperty(i,""):i==="float"?e.cssFloat="":e[i]="":l?e.setProperty(i,r):typeof r!="number"||r===0||TS.has(i)?i==="float"?e.cssFloat=r:e[i]=(""+r).trim():e[i]=r+"px"}function Xm(e,i,r){if(i!=null&&typeof i!="object")throw Error(s(62));if(e=e.style,r!=null){for(var l in r)!r.hasOwnProperty(l)||i!=null&&i.hasOwnProperty(l)||(l.indexOf("--")===0?e.setProperty(l,""):l==="float"?e.cssFloat="":e[l]="");for(var u in i)l=i[u],i.hasOwnProperty(u)&&r[u]!==l&&km(e,u,l)}else for(var h in i)i.hasOwnProperty(h)&&km(e,h,i[h])}function Cf(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var AS=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),CS=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function Sc(e){return CS.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function aa(){}var Rf=null;function wf(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Tr=null,Ar=null;function qm(e){var i=st(e);if(i&&(e=i.stateNode)){var r=e[wn]||null;t:switch(e=i.stateNode,i.type){case"input":if(zn(e,r.value,r.defaultValue,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name),i=r.name,r.type==="radio"&&i!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll('input[name="'+_e(""+i)+'"][type="radio"]'),i=0;i<r.length;i++){var l=r[i];if(l!==e&&l.form===e.form){var u=l[wn]||null;if(!u)throw Error(s(90));zn(l,u.value,u.defaultValue,u.defaultValue,u.checked,u.defaultChecked,u.type,u.name)}}for(i=0;i<r.length;i++)l=r[i],l.form===e.form&&ia(l)}break t;case"textarea":Er(e,r.value,r.defaultValue);break t;case"select":i=r.value,i!=null&&cn(e,!!r.multiple,i,!1)}}}var Nf=!1;function Wm(e,i,r){if(Nf)return e(i,r);Nf=!0;try{var l=e(i);return l}finally{if(Nf=!1,(Tr!==null||Ar!==null)&&(lu(),Tr&&(i=Tr,e=Ar,Ar=Tr=null,qm(i),e)))for(i=0;i<e.length;i++)qm(e[i])}}function tl(e,i){var r=e.stateNode;if(r===null)return null;var l=r[wn]||null;if(l===null)return null;r=l[i];t:switch(i){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(l=!l.disabled)||(e=e.type,l=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!l;break t;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(s(231,i,typeof r));return r}var sa=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Df=!1;if(sa)try{var el={};Object.defineProperty(el,"passive",{get:function(){Df=!0}}),window.addEventListener("test",el,el),window.removeEventListener("test",el,el)}catch{Df=!1}var Ha=null,Uf=null,Mc=null;function Ym(){if(Mc)return Mc;var e,i=Uf,r=i.length,l,u="value"in Ha?Ha.value:Ha.textContent,h=u.length;for(e=0;e<r&&i[e]===u[e];e++);var b=r-e;for(l=1;l<=b&&i[r-l]===u[h-l];l++);return Mc=u.slice(e,1<l?1-l:void 0)}function Ec(e){var i=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&i===13&&(e=13)):e=i,e===10&&(e=13),32<=e||e===13?e:0}function bc(){return!0}function Qm(){return!1}function Qn(e){function i(r,l,u,h,b){this._reactName=r,this._targetInst=u,this.type=l,this.nativeEvent=h,this.target=b,this.currentTarget=null;for(var A in e)e.hasOwnProperty(A)&&(r=e[A],this[A]=r?r(h):h[A]);return this.isDefaultPrevented=(h.defaultPrevented!=null?h.defaultPrevented:h.returnValue===!1)?bc:Qm,this.isPropagationStopped=Qm,this}return _(i.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=bc)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=bc)},persist:function(){},isPersistent:bc}),i}var Ls={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},Tc=Qn(Ls),nl=_({},Ls,{view:0,detail:0}),RS=Qn(nl),Lf,Of,il,Ac=_({},nl,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:zf,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==il&&(il&&e.type==="mousemove"?(Lf=e.screenX-il.screenX,Of=e.screenY-il.screenY):Of=Lf=0,il=e),Lf)},movementY:function(e){return"movementY"in e?e.movementY:Of}}),Zm=Qn(Ac),wS=_({},Ac,{dataTransfer:0}),NS=Qn(wS),DS=_({},nl,{relatedTarget:0}),Pf=Qn(DS),US=_({},Ls,{animationName:0,elapsedTime:0,pseudoElement:0}),LS=Qn(US),OS=_({},Ls,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),PS=Qn(OS),zS=_({},Ls,{data:0}),Km=Qn(zS),IS={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},BS={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},FS={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function HS(e){var i=this.nativeEvent;return i.getModifierState?i.getModifierState(e):(e=FS[e])?!!i[e]:!1}function zf(){return HS}var GS=_({},nl,{key:function(e){if(e.key){var i=IS[e.key]||e.key;if(i!=="Unidentified")return i}return e.type==="keypress"?(e=Ec(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?BS[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:zf,charCode:function(e){return e.type==="keypress"?Ec(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?Ec(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),VS=Qn(GS),jS=_({},Ac,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Jm=Qn(jS),kS=_({},nl,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:zf}),XS=Qn(kS),qS=_({},Ls,{propertyName:0,elapsedTime:0,pseudoElement:0}),WS=Qn(qS),YS=_({},Ac,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),QS=Qn(YS),ZS=_({},Ls,{newState:0,oldState:0}),KS=Qn(ZS),JS=[9,13,27,32],If=sa&&"CompositionEvent"in window,al=null;sa&&"documentMode"in document&&(al=document.documentMode);var $S=sa&&"TextEvent"in window&&!al,$m=sa&&(!If||al&&8<al&&11>=al),tg=" ",eg=!1;function ng(e,i){switch(e){case"keyup":return JS.indexOf(i.keyCode)!==-1;case"keydown":return i.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function ig(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Cr=!1;function tM(e,i){switch(e){case"compositionend":return ig(i);case"keypress":return i.which!==32?null:(eg=!0,tg);case"textInput":return e=i.data,e===tg&&eg?null:e;default:return null}}function eM(e,i){if(Cr)return e==="compositionend"||!If&&ng(e,i)?(e=Ym(),Mc=Uf=Ha=null,Cr=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(i.ctrlKey||i.altKey||i.metaKey)||i.ctrlKey&&i.altKey){if(i.char&&1<i.char.length)return i.char;if(i.which)return String.fromCharCode(i.which)}return null;case"compositionend":return $m&&i.locale!=="ko"?null:i.data;default:return null}}var nM={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function ag(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i==="input"?!!nM[e.type]:i==="textarea"}function sg(e,i,r,l){Tr?Ar?Ar.push(l):Ar=[l]:Tr=l,i=mu(i,"onChange"),0<i.length&&(r=new Tc("onChange","change",null,r,l),e.push({event:r,listeners:i}))}var sl=null,rl=null;function iM(e){G_(e,0)}function Cc(e){var i=rt(e);if(ia(i))return e}function rg(e,i){if(e==="change")return i}var og=!1;if(sa){var Bf;if(sa){var Ff="oninput"in document;if(!Ff){var lg=document.createElement("div");lg.setAttribute("oninput","return;"),Ff=typeof lg.oninput=="function"}Bf=Ff}else Bf=!1;og=Bf&&(!document.documentMode||9<document.documentMode)}function cg(){sl&&(sl.detachEvent("onpropertychange",ug),rl=sl=null)}function ug(e){if(e.propertyName==="value"&&Cc(rl)){var i=[];sg(i,rl,e,wf(e)),Wm(iM,i)}}function aM(e,i,r){e==="focusin"?(cg(),sl=i,rl=r,sl.attachEvent("onpropertychange",ug)):e==="focusout"&&cg()}function sM(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Cc(rl)}function rM(e,i){if(e==="click")return Cc(i)}function oM(e,i){if(e==="input"||e==="change")return Cc(i)}function lM(e,i){return e===i&&(e!==0||1/e===1/i)||e!==e&&i!==i}var ri=typeof Object.is=="function"?Object.is:lM;function ol(e,i){if(ri(e,i))return!0;if(typeof e!="object"||e===null||typeof i!="object"||i===null)return!1;var r=Object.keys(e),l=Object.keys(i);if(r.length!==l.length)return!1;for(l=0;l<r.length;l++){var u=r[l];if(!Be.call(i,u)||!ri(e[u],i[u]))return!1}return!0}function fg(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function dg(e,i){var r=fg(e);e=0;for(var l;r;){if(r.nodeType===3){if(l=e+r.textContent.length,e<=i&&l>=i)return{node:r,offset:i-e};e=l}t:{for(;r;){if(r.nextSibling){r=r.nextSibling;break t}r=r.parentNode}r=void 0}r=fg(r)}}function hg(e,i){return e&&i?e===i?!0:e&&e.nodeType===3?!1:i&&i.nodeType===3?hg(e,i.parentNode):"contains"in e?e.contains(i):e.compareDocumentPosition?!!(e.compareDocumentPosition(i)&16):!1:!1}function pg(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var i=En(e.document);i instanceof e.HTMLIFrameElement;){try{var r=typeof i.contentWindow.location.href=="string"}catch{r=!1}if(r)e=i.contentWindow;else break;i=En(e.document)}return i}function Hf(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i&&(i==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||i==="textarea"||e.contentEditable==="true")}var cM=sa&&"documentMode"in document&&11>=document.documentMode,Rr=null,Gf=null,ll=null,Vf=!1;function mg(e,i,r){var l=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;Vf||Rr==null||Rr!==En(l)||(l=Rr,"selectionStart"in l&&Hf(l)?l={start:l.selectionStart,end:l.selectionEnd}:(l=(l.ownerDocument&&l.ownerDocument.defaultView||window).getSelection(),l={anchorNode:l.anchorNode,anchorOffset:l.anchorOffset,focusNode:l.focusNode,focusOffset:l.focusOffset}),ll&&ol(ll,l)||(ll=l,l=mu(Gf,"onSelect"),0<l.length&&(i=new Tc("onSelect","select",null,i,r),e.push({event:i,listeners:l}),i.target=Rr)))}function Os(e,i){var r={};return r[e.toLowerCase()]=i.toLowerCase(),r["Webkit"+e]="webkit"+i,r["Moz"+e]="moz"+i,r}var wr={animationend:Os("Animation","AnimationEnd"),animationiteration:Os("Animation","AnimationIteration"),animationstart:Os("Animation","AnimationStart"),transitionrun:Os("Transition","TransitionRun"),transitionstart:Os("Transition","TransitionStart"),transitioncancel:Os("Transition","TransitionCancel"),transitionend:Os("Transition","TransitionEnd")},jf={},gg={};sa&&(gg=document.createElement("div").style,"AnimationEvent"in window||(delete wr.animationend.animation,delete wr.animationiteration.animation,delete wr.animationstart.animation),"TransitionEvent"in window||delete wr.transitionend.transition);function Ps(e){if(jf[e])return jf[e];if(!wr[e])return e;var i=wr[e],r;for(r in i)if(i.hasOwnProperty(r)&&r in gg)return jf[e]=i[r];return e}var vg=Ps("animationend"),_g=Ps("animationiteration"),yg=Ps("animationstart"),uM=Ps("transitionrun"),fM=Ps("transitionstart"),dM=Ps("transitioncancel"),xg=Ps("transitionend"),Sg=new Map,kf="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");kf.push("scrollEnd");function Di(e,i){Sg.set(e,i),Pt(i,[e])}var Rc=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var i=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(i))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},yi=[],Nr=0,Xf=0;function wc(){for(var e=Nr,i=Xf=Nr=0;i<e;){var r=yi[i];yi[i++]=null;var l=yi[i];yi[i++]=null;var u=yi[i];yi[i++]=null;var h=yi[i];if(yi[i++]=null,l!==null&&u!==null){var b=l.pending;b===null?u.next=u:(u.next=b.next,b.next=u),l.pending=u}h!==0&&Mg(r,u,h)}}function Nc(e,i,r,l){yi[Nr++]=e,yi[Nr++]=i,yi[Nr++]=r,yi[Nr++]=l,Xf|=l,e.lanes|=l,e=e.alternate,e!==null&&(e.lanes|=l)}function qf(e,i,r,l){return Nc(e,i,r,l),Dc(e)}function zs(e,i){return Nc(e,null,null,i),Dc(e)}function Mg(e,i,r){e.lanes|=r;var l=e.alternate;l!==null&&(l.lanes|=r);for(var u=!1,h=e.return;h!==null;)h.childLanes|=r,l=h.alternate,l!==null&&(l.childLanes|=r),h.tag===22&&(e=h.stateNode,e===null||e._visibility&1||(u=!0)),e=h,h=h.return;return e.tag===3?(h=e.stateNode,u&&i!==null&&(u=31-ne(r),e=h.hiddenUpdates,l=e[u],l===null?e[u]=[i]:l.push(i),i.lane=r|536870912),h):null}function Dc(e){if(50<Nl)throw Nl=0,eh=null,Error(s(185));for(var i=e.return;i!==null;)e=i,i=e.return;return e.tag===3?e.stateNode:null}var Dr={};function hM(e,i,r,l){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=i,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=l,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function oi(e,i,r,l){return new hM(e,i,r,l)}function Wf(e){return e=e.prototype,!(!e||!e.isReactComponent)}function ra(e,i){var r=e.alternate;return r===null?(r=oi(e.tag,i,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=i,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&65011712,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,i=e.dependencies,r.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r.refCleanup=e.refCleanup,r}function Eg(e,i){e.flags&=65011714;var r=e.alternate;return r===null?(e.childLanes=0,e.lanes=i,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=r.childLanes,e.lanes=r.lanes,e.child=r.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=r.memoizedProps,e.memoizedState=r.memoizedState,e.updateQueue=r.updateQueue,e.type=r.type,i=r.dependencies,e.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext}),e}function Uc(e,i,r,l,u,h){var b=0;if(l=e,typeof e=="function")Wf(e)&&(b=1);else if(typeof e=="string")b=_1(e,r,q.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case U:return e=oi(31,r,i,u),e.elementType=U,e.lanes=h,e;case T:return Is(r.children,u,h,i);case S:b=8,u|=24;break;case y:return e=oi(12,r,i,u|2),e.elementType=y,e.lanes=h,e;case V:return e=oi(13,r,i,u),e.elementType=V,e.lanes=h,e;case L:return e=oi(19,r,i,u),e.elementType=L,e.lanes=h,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case D:b=10;break t;case I:b=9;break t;case C:b=11;break t;case P:b=14;break t;case G:b=16,l=null;break t}b=29,r=Error(s(130,e===null?"null":typeof e,"")),l=null}return i=oi(b,r,i,u),i.elementType=e,i.type=l,i.lanes=h,i}function Is(e,i,r,l){return e=oi(7,e,l,i),e.lanes=r,e}function Yf(e,i,r){return e=oi(6,e,null,i),e.lanes=r,e}function bg(e){var i=oi(18,null,null,0);return i.stateNode=e,i}function Qf(e,i,r){return i=oi(4,e.children!==null?e.children:[],e.key,i),i.lanes=r,i.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},i}var Tg=new WeakMap;function xi(e,i){if(typeof e=="object"&&e!==null){var r=Tg.get(e);return r!==void 0?r:(i={value:e,source:i,stack:Qt(i)},Tg.set(e,i),i)}return{value:e,source:i,stack:Qt(i)}}var Ur=[],Lr=0,Lc=null,cl=0,Si=[],Mi=0,Ga=null,Xi=1,qi="";function oa(e,i){Ur[Lr++]=cl,Ur[Lr++]=Lc,Lc=e,cl=i}function Ag(e,i,r){Si[Mi++]=Xi,Si[Mi++]=qi,Si[Mi++]=Ga,Ga=e;var l=Xi;e=qi;var u=32-ne(l)-1;l&=~(1<<u),r+=1;var h=32-ne(i)+u;if(30<h){var b=u-u%5;h=(l&(1<<b)-1).toString(32),l>>=b,u-=b,Xi=1<<32-ne(i)+u|r<<u|l,qi=h+e}else Xi=1<<h|r<<u|l,qi=e}function Zf(e){e.return!==null&&(oa(e,1),Ag(e,1,0))}function Kf(e){for(;e===Lc;)Lc=Ur[--Lr],Ur[Lr]=null,cl=Ur[--Lr],Ur[Lr]=null;for(;e===Ga;)Ga=Si[--Mi],Si[Mi]=null,qi=Si[--Mi],Si[Mi]=null,Xi=Si[--Mi],Si[Mi]=null}function Cg(e,i){Si[Mi++]=Xi,Si[Mi++]=qi,Si[Mi++]=Ga,Xi=i.id,qi=i.overflow,Ga=e}var Nn=null,Ke=null,Ce=!1,Va=null,Ei=!1,Jf=Error(s(519));function ja(e){var i=Error(s(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw ul(xi(i,e)),Jf}function Rg(e){var i=e.stateNode,r=e.type,l=e.memoizedProps;switch(i[sn]=e,i[wn]=l,r){case"dialog":xe("cancel",i),xe("close",i);break;case"iframe":case"object":case"embed":xe("load",i);break;case"video":case"audio":for(r=0;r<Ul.length;r++)xe(Ul[r],i);break;case"source":xe("error",i);break;case"img":case"image":case"link":xe("error",i),xe("load",i);break;case"details":xe("toggle",i);break;case"input":xe("invalid",i),Vn(i,l.value,l.defaultValue,l.checked,l.defaultChecked,l.type,l.name,!0);break;case"select":xe("invalid",i);break;case"textarea":xe("invalid",i),ki(i,l.value,l.defaultValue,l.children)}r=l.children,typeof r!="string"&&typeof r!="number"&&typeof r!="bigint"||i.textContent===""+r||l.suppressHydrationWarning===!0||X_(i.textContent,r)?(l.popover!=null&&(xe("beforetoggle",i),xe("toggle",i)),l.onScroll!=null&&xe("scroll",i),l.onScrollEnd!=null&&xe("scrollend",i),l.onClick!=null&&(i.onclick=aa),i=!0):i=!1,i||ja(e,!0)}function wg(e){for(Nn=e.return;Nn;)switch(Nn.tag){case 5:case 31:case 13:Ei=!1;return;case 27:case 3:Ei=!0;return;default:Nn=Nn.return}}function Or(e){if(e!==Nn)return!1;if(!Ce)return wg(e),Ce=!0,!1;var i=e.tag,r;if((r=i!==3&&i!==27)&&((r=i===5)&&(r=e.type,r=!(r!=="form"&&r!=="button")||gh(e.type,e.memoizedProps)),r=!r),r&&Ke&&ja(e),wg(e),i===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ke=t0(e)}else if(i===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ke=t0(e)}else i===27?(i=Ke,is(e.type)?(e=Sh,Sh=null,Ke=e):Ke=i):Ke=Nn?Ti(e.stateNode.nextSibling):null;return!0}function Bs(){Ke=Nn=null,Ce=!1}function $f(){var e=Va;return e!==null&&($n===null?$n=e:$n.push.apply($n,e),Va=null),e}function ul(e){Va===null?Va=[e]:Va.push(e)}var td=z(null),Fs=null,la=null;function ka(e,i,r){St(td,i._currentValue),i._currentValue=r}function ca(e){e._currentValue=td.current,nt(td)}function ed(e,i,r){for(;e!==null;){var l=e.alternate;if((e.childLanes&i)!==i?(e.childLanes|=i,l!==null&&(l.childLanes|=i)):l!==null&&(l.childLanes&i)!==i&&(l.childLanes|=i),e===r)break;e=e.return}}function nd(e,i,r,l){var u=e.child;for(u!==null&&(u.return=e);u!==null;){var h=u.dependencies;if(h!==null){var b=u.child;h=h.firstContext;t:for(;h!==null;){var A=h;h=u;for(var F=0;F<i.length;F++)if(A.context===i[F]){h.lanes|=r,A=h.alternate,A!==null&&(A.lanes|=r),ed(h.return,r,e),l||(b=null);break t}h=A.next}}else if(u.tag===18){if(b=u.return,b===null)throw Error(s(341));b.lanes|=r,h=b.alternate,h!==null&&(h.lanes|=r),ed(b,r,e),b=null}else b=u.child;if(b!==null)b.return=u;else for(b=u;b!==null;){if(b===e){b=null;break}if(u=b.sibling,u!==null){u.return=b.return,b=u;break}b=b.return}u=b}}function Pr(e,i,r,l){e=null;for(var u=i,h=!1;u!==null;){if(!h){if((u.flags&524288)!==0)h=!0;else if((u.flags&262144)!==0)break}if(u.tag===10){var b=u.alternate;if(b===null)throw Error(s(387));if(b=b.memoizedProps,b!==null){var A=u.type;ri(u.pendingProps.value,b.value)||(e!==null?e.push(A):e=[A])}}else if(u===Mt.current){if(b=u.alternate,b===null)throw Error(s(387));b.memoizedState.memoizedState!==u.memoizedState.memoizedState&&(e!==null?e.push(Il):e=[Il])}u=u.return}e!==null&&nd(i,e,r,l),i.flags|=262144}function Oc(e){for(e=e.firstContext;e!==null;){if(!ri(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Hs(e){Fs=e,la=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Dn(e){return Ng(Fs,e)}function Pc(e,i){return Fs===null&&Hs(e),Ng(e,i)}function Ng(e,i){var r=i._currentValue;if(i={context:i,memoizedValue:r,next:null},la===null){if(e===null)throw Error(s(308));la=i,e.dependencies={lanes:0,firstContext:i},e.flags|=524288}else la=la.next=i;return r}var pM=typeof AbortController<"u"?AbortController:function(){var e=[],i=this.signal={aborted:!1,addEventListener:function(r,l){e.push(l)}};this.abort=function(){i.aborted=!0,e.forEach(function(r){return r()})}},mM=a.unstable_scheduleCallback,gM=a.unstable_NormalPriority,hn={$$typeof:D,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function id(){return{controller:new pM,data:new Map,refCount:0}}function fl(e){e.refCount--,e.refCount===0&&mM(gM,function(){e.controller.abort()})}var dl=null,ad=0,zr=0,Ir=null;function vM(e,i){if(dl===null){var r=dl=[];ad=0,zr=oh(),Ir={status:"pending",value:void 0,then:function(l){r.push(l)}}}return ad++,i.then(Dg,Dg),i}function Dg(){if(--ad===0&&dl!==null){Ir!==null&&(Ir.status="fulfilled");var e=dl;dl=null,zr=0,Ir=null;for(var i=0;i<e.length;i++)(0,e[i])()}}function _M(e,i){var r=[],l={status:"pending",value:null,reason:null,then:function(u){r.push(u)}};return e.then(function(){l.status="fulfilled",l.value=i;for(var u=0;u<r.length;u++)(0,r[u])(i)},function(u){for(l.status="rejected",l.reason=u,u=0;u<r.length;u++)(0,r[u])(void 0)}),l}var Ug=B.S;B.S=function(e,i){m_=pt(),typeof i=="object"&&i!==null&&typeof i.then=="function"&&vM(e,i),Ug!==null&&Ug(e,i)};var Gs=z(null);function sd(){var e=Gs.current;return e!==null?e:Qe.pooledCache}function zc(e,i){i===null?St(Gs,Gs.current):St(Gs,i.pool)}function Lg(){var e=sd();return e===null?null:{parent:hn._currentValue,pool:e}}var Br=Error(s(460)),rd=Error(s(474)),Ic=Error(s(542)),Bc={then:function(){}};function Og(e){return e=e.status,e==="fulfilled"||e==="rejected"}function Pg(e,i,r){switch(r=e[r],r===void 0?e.push(i):r!==i&&(i.then(aa,aa),i=r),i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Ig(e),e;default:if(typeof i.status=="string")i.then(aa,aa);else{if(e=Qe,e!==null&&100<e.shellSuspendCounter)throw Error(s(482));e=i,e.status="pending",e.then(function(l){if(i.status==="pending"){var u=i;u.status="fulfilled",u.value=l}},function(l){if(i.status==="pending"){var u=i;u.status="rejected",u.reason=l}})}switch(i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Ig(e),e}throw js=i,Br}}function Vs(e){try{var i=e._init;return i(e._payload)}catch(r){throw r!==null&&typeof r=="object"&&typeof r.then=="function"?(js=r,Br):r}}var js=null;function zg(){if(js===null)throw Error(s(459));var e=js;return js=null,e}function Ig(e){if(e===Br||e===Ic)throw Error(s(483))}var Fr=null,hl=0;function Fc(e){var i=hl;return hl+=1,Fr===null&&(Fr=[]),Pg(Fr,e,i)}function pl(e,i){i=i.props.ref,e.ref=i!==void 0?i:null}function Hc(e,i){throw i.$$typeof===x?Error(s(525)):(e=Object.prototype.toString.call(i),Error(s(31,e==="[object Object]"?"object with keys {"+Object.keys(i).join(", ")+"}":e)))}function Bg(e){function i(J,k){if(e){var tt=J.deletions;tt===null?(J.deletions=[k],J.flags|=16):tt.push(k)}}function r(J,k){if(!e)return null;for(;k!==null;)i(J,k),k=k.sibling;return null}function l(J){for(var k=new Map;J!==null;)J.key!==null?k.set(J.key,J):k.set(J.index,J),J=J.sibling;return k}function u(J,k){return J=ra(J,k),J.index=0,J.sibling=null,J}function h(J,k,tt){return J.index=tt,e?(tt=J.alternate,tt!==null?(tt=tt.index,tt<k?(J.flags|=67108866,k):tt):(J.flags|=67108866,k)):(J.flags|=1048576,k)}function b(J){return e&&J.alternate===null&&(J.flags|=67108866),J}function A(J,k,tt,gt){return k===null||k.tag!==6?(k=Yf(tt,J.mode,gt),k.return=J,k):(k=u(k,tt),k.return=J,k)}function F(J,k,tt,gt){var Jt=tt.type;return Jt===T?ht(J,k,tt.props.children,gt,tt.key):k!==null&&(k.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Vs(Jt)===k.type)?(k=u(k,tt.props),pl(k,tt),k.return=J,k):(k=Uc(tt.type,tt.key,tt.props,null,J.mode,gt),pl(k,tt),k.return=J,k)}function et(J,k,tt,gt){return k===null||k.tag!==4||k.stateNode.containerInfo!==tt.containerInfo||k.stateNode.implementation!==tt.implementation?(k=Qf(tt,J.mode,gt),k.return=J,k):(k=u(k,tt.children||[]),k.return=J,k)}function ht(J,k,tt,gt,Jt){return k===null||k.tag!==7?(k=Is(tt,J.mode,gt,Jt),k.return=J,k):(k=u(k,tt),k.return=J,k)}function _t(J,k,tt){if(typeof k=="string"&&k!==""||typeof k=="number"||typeof k=="bigint")return k=Yf(""+k,J.mode,tt),k.return=J,k;if(typeof k=="object"&&k!==null){switch(k.$$typeof){case E:return tt=Uc(k.type,k.key,k.props,null,J.mode,tt),pl(tt,k),tt.return=J,tt;case M:return k=Qf(k,J.mode,tt),k.return=J,k;case G:return k=Vs(k),_t(J,k,tt)}if(ct(k)||ut(k))return k=Is(k,J.mode,tt,null),k.return=J,k;if(typeof k.then=="function")return _t(J,Fc(k),tt);if(k.$$typeof===D)return _t(J,Pc(J,k),tt);Hc(J,k)}return null}function it(J,k,tt,gt){var Jt=k!==null?k.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return Jt!==null?null:A(J,k,""+tt,gt);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case E:return tt.key===Jt?F(J,k,tt,gt):null;case M:return tt.key===Jt?et(J,k,tt,gt):null;case G:return tt=Vs(tt),it(J,k,tt,gt)}if(ct(tt)||ut(tt))return Jt!==null?null:ht(J,k,tt,gt,null);if(typeof tt.then=="function")return it(J,k,Fc(tt),gt);if(tt.$$typeof===D)return it(J,k,Pc(J,tt),gt);Hc(J,tt)}return null}function lt(J,k,tt,gt,Jt){if(typeof gt=="string"&&gt!==""||typeof gt=="number"||typeof gt=="bigint")return J=J.get(tt)||null,A(k,J,""+gt,Jt);if(typeof gt=="object"&&gt!==null){switch(gt.$$typeof){case E:return J=J.get(gt.key===null?tt:gt.key)||null,F(k,J,gt,Jt);case M:return J=J.get(gt.key===null?tt:gt.key)||null,et(k,J,gt,Jt);case G:return gt=Vs(gt),lt(J,k,tt,gt,Jt)}if(ct(gt)||ut(gt))return J=J.get(tt)||null,ht(k,J,gt,Jt,null);if(typeof gt.then=="function")return lt(J,k,tt,Fc(gt),Jt);if(gt.$$typeof===D)return lt(J,k,tt,Pc(k,gt),Jt);Hc(k,gt)}return null}function Gt(J,k,tt,gt){for(var Jt=null,Le=null,kt=k,fe=k=0,Te=null;kt!==null&&fe<tt.length;fe++){kt.index>fe?(Te=kt,kt=null):Te=kt.sibling;var Oe=it(J,kt,tt[fe],gt);if(Oe===null){kt===null&&(kt=Te);break}e&&kt&&Oe.alternate===null&&i(J,kt),k=h(Oe,k,fe),Le===null?Jt=Oe:Le.sibling=Oe,Le=Oe,kt=Te}if(fe===tt.length)return r(J,kt),Ce&&oa(J,fe),Jt;if(kt===null){for(;fe<tt.length;fe++)kt=_t(J,tt[fe],gt),kt!==null&&(k=h(kt,k,fe),Le===null?Jt=kt:Le.sibling=kt,Le=kt);return Ce&&oa(J,fe),Jt}for(kt=l(kt);fe<tt.length;fe++)Te=lt(kt,J,fe,tt[fe],gt),Te!==null&&(e&&Te.alternate!==null&&kt.delete(Te.key===null?fe:Te.key),k=h(Te,k,fe),Le===null?Jt=Te:Le.sibling=Te,Le=Te);return e&&kt.forEach(function(ls){return i(J,ls)}),Ce&&oa(J,fe),Jt}function ee(J,k,tt,gt){if(tt==null)throw Error(s(151));for(var Jt=null,Le=null,kt=k,fe=k=0,Te=null,Oe=tt.next();kt!==null&&!Oe.done;fe++,Oe=tt.next()){kt.index>fe?(Te=kt,kt=null):Te=kt.sibling;var ls=it(J,kt,Oe.value,gt);if(ls===null){kt===null&&(kt=Te);break}e&&kt&&ls.alternate===null&&i(J,kt),k=h(ls,k,fe),Le===null?Jt=ls:Le.sibling=ls,Le=ls,kt=Te}if(Oe.done)return r(J,kt),Ce&&oa(J,fe),Jt;if(kt===null){for(;!Oe.done;fe++,Oe=tt.next())Oe=_t(J,Oe.value,gt),Oe!==null&&(k=h(Oe,k,fe),Le===null?Jt=Oe:Le.sibling=Oe,Le=Oe);return Ce&&oa(J,fe),Jt}for(kt=l(kt);!Oe.done;fe++,Oe=tt.next())Oe=lt(kt,J,fe,Oe.value,gt),Oe!==null&&(e&&Oe.alternate!==null&&kt.delete(Oe.key===null?fe:Oe.key),k=h(Oe,k,fe),Le===null?Jt=Oe:Le.sibling=Oe,Le=Oe);return e&&kt.forEach(function(w1){return i(J,w1)}),Ce&&oa(J,fe),Jt}function Xe(J,k,tt,gt){if(typeof tt=="object"&&tt!==null&&tt.type===T&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case E:t:{for(var Jt=tt.key;k!==null;){if(k.key===Jt){if(Jt=tt.type,Jt===T){if(k.tag===7){r(J,k.sibling),gt=u(k,tt.props.children),gt.return=J,J=gt;break t}}else if(k.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Vs(Jt)===k.type){r(J,k.sibling),gt=u(k,tt.props),pl(gt,tt),gt.return=J,J=gt;break t}r(J,k);break}else i(J,k);k=k.sibling}tt.type===T?(gt=Is(tt.props.children,J.mode,gt,tt.key),gt.return=J,J=gt):(gt=Uc(tt.type,tt.key,tt.props,null,J.mode,gt),pl(gt,tt),gt.return=J,J=gt)}return b(J);case M:t:{for(Jt=tt.key;k!==null;){if(k.key===Jt)if(k.tag===4&&k.stateNode.containerInfo===tt.containerInfo&&k.stateNode.implementation===tt.implementation){r(J,k.sibling),gt=u(k,tt.children||[]),gt.return=J,J=gt;break t}else{r(J,k);break}else i(J,k);k=k.sibling}gt=Qf(tt,J.mode,gt),gt.return=J,J=gt}return b(J);case G:return tt=Vs(tt),Xe(J,k,tt,gt)}if(ct(tt))return Gt(J,k,tt,gt);if(ut(tt)){if(Jt=ut(tt),typeof Jt!="function")throw Error(s(150));return tt=Jt.call(tt),ee(J,k,tt,gt)}if(typeof tt.then=="function")return Xe(J,k,Fc(tt),gt);if(tt.$$typeof===D)return Xe(J,k,Pc(J,tt),gt);Hc(J,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,k!==null&&k.tag===6?(r(J,k.sibling),gt=u(k,tt),gt.return=J,J=gt):(r(J,k),gt=Yf(tt,J.mode,gt),gt.return=J,J=gt),b(J)):r(J,k)}return function(J,k,tt,gt){try{hl=0;var Jt=Xe(J,k,tt,gt);return Fr=null,Jt}catch(kt){if(kt===Br||kt===Ic)throw kt;var Le=oi(29,kt,null,J.mode);return Le.lanes=gt,Le.return=J,Le}finally{}}}var ks=Bg(!0),Fg=Bg(!1),Xa=!1;function od(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function ld(e,i){e=e.updateQueue,i.updateQueue===e&&(i.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function qa(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function Wa(e,i,r){var l=e.updateQueue;if(l===null)return null;if(l=l.shared,(ze&2)!==0){var u=l.pending;return u===null?i.next=i:(i.next=u.next,u.next=i),l.pending=i,i=Dc(e),Mg(e,null,r),i}return Nc(e,l,i,r),Dc(e)}function ml(e,i,r){if(i=i.updateQueue,i!==null&&(i=i.shared,(r&4194048)!==0)){var l=i.lanes;l&=e.pendingLanes,r|=l,i.lanes=r,Ko(e,r)}}function cd(e,i){var r=e.updateQueue,l=e.alternate;if(l!==null&&(l=l.updateQueue,r===l)){var u=null,h=null;if(r=r.firstBaseUpdate,r!==null){do{var b={lane:r.lane,tag:r.tag,payload:r.payload,callback:null,next:null};h===null?u=h=b:h=h.next=b,r=r.next}while(r!==null);h===null?u=h=i:h=h.next=i}else u=h=i;r={baseState:l.baseState,firstBaseUpdate:u,lastBaseUpdate:h,shared:l.shared,callbacks:l.callbacks},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=i:e.next=i,r.lastBaseUpdate=i}var ud=!1;function gl(){if(ud){var e=Ir;if(e!==null)throw e}}function vl(e,i,r,l){ud=!1;var u=e.updateQueue;Xa=!1;var h=u.firstBaseUpdate,b=u.lastBaseUpdate,A=u.shared.pending;if(A!==null){u.shared.pending=null;var F=A,et=F.next;F.next=null,b===null?h=et:b.next=et,b=F;var ht=e.alternate;ht!==null&&(ht=ht.updateQueue,A=ht.lastBaseUpdate,A!==b&&(A===null?ht.firstBaseUpdate=et:A.next=et,ht.lastBaseUpdate=F))}if(h!==null){var _t=u.baseState;b=0,ht=et=F=null,A=h;do{var it=A.lane&-536870913,lt=it!==A.lane;if(lt?(be&it)===it:(l&it)===it){it!==0&&it===zr&&(ud=!0),ht!==null&&(ht=ht.next={lane:0,tag:A.tag,payload:A.payload,callback:null,next:null});t:{var Gt=e,ee=A;it=i;var Xe=r;switch(ee.tag){case 1:if(Gt=ee.payload,typeof Gt=="function"){_t=Gt.call(Xe,_t,it);break t}_t=Gt;break t;case 3:Gt.flags=Gt.flags&-65537|128;case 0:if(Gt=ee.payload,it=typeof Gt=="function"?Gt.call(Xe,_t,it):Gt,it==null)break t;_t=_({},_t,it);break t;case 2:Xa=!0}}it=A.callback,it!==null&&(e.flags|=64,lt&&(e.flags|=8192),lt=u.callbacks,lt===null?u.callbacks=[it]:lt.push(it))}else lt={lane:it,tag:A.tag,payload:A.payload,callback:A.callback,next:null},ht===null?(et=ht=lt,F=_t):ht=ht.next=lt,b|=it;if(A=A.next,A===null){if(A=u.shared.pending,A===null)break;lt=A,A=lt.next,lt.next=null,u.lastBaseUpdate=lt,u.shared.pending=null}}while(!0);ht===null&&(F=_t),u.baseState=F,u.firstBaseUpdate=et,u.lastBaseUpdate=ht,h===null&&(u.shared.lanes=0),Ja|=b,e.lanes=b,e.memoizedState=_t}}function Hg(e,i){if(typeof e!="function")throw Error(s(191,e));e.call(i)}function Gg(e,i){var r=e.callbacks;if(r!==null)for(e.callbacks=null,e=0;e<r.length;e++)Hg(r[e],i)}var Hr=z(null),Gc=z(0);function Vg(e,i){e=_a,St(Gc,e),St(Hr,i),_a=e|i.baseLanes}function fd(){St(Gc,_a),St(Hr,Hr.current)}function dd(){_a=Gc.current,nt(Hr),nt(Gc)}var li=z(null),bi=null;function Ya(e){var i=e.alternate;St(un,un.current&1),St(li,e),bi===null&&(i===null||Hr.current!==null||i.memoizedState!==null)&&(bi=e)}function hd(e){St(un,un.current),St(li,e),bi===null&&(bi=e)}function jg(e){e.tag===22?(St(un,un.current),St(li,e),bi===null&&(bi=e)):Qa()}function Qa(){St(un,un.current),St(li,li.current)}function ci(e){nt(li),bi===e&&(bi=null),nt(un)}var un=z(0);function Vc(e){for(var i=e;i!==null;){if(i.tag===13){var r=i.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||yh(r)||xh(r)))return i}else if(i.tag===19&&(i.memoizedProps.revealOrder==="forwards"||i.memoizedProps.revealOrder==="backwards"||i.memoizedProps.revealOrder==="unstable_legacy-backwards"||i.memoizedProps.revealOrder==="together")){if((i.flags&128)!==0)return i}else if(i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return null;i=i.return}i.sibling.return=i.return,i=i.sibling}return null}var ua=0,ue=null,je=null,pn=null,jc=!1,Gr=!1,Xs=!1,kc=0,_l=0,Vr=null,yM=0;function rn(){throw Error(s(321))}function pd(e,i){if(i===null)return!1;for(var r=0;r<i.length&&r<e.length;r++)if(!ri(e[r],i[r]))return!1;return!0}function md(e,i,r,l,u,h){return ua=h,ue=i,i.memoizedState=null,i.updateQueue=null,i.lanes=0,B.H=e===null||e.memoizedState===null?Av:Nd,Xs=!1,h=r(l,u),Xs=!1,Gr&&(h=Xg(i,r,l,u)),kg(e),h}function kg(e){B.H=Sl;var i=je!==null&&je.next!==null;if(ua=0,pn=je=ue=null,jc=!1,_l=0,Vr=null,i)throw Error(s(300));e===null||mn||(e=e.dependencies,e!==null&&Oc(e)&&(mn=!0))}function Xg(e,i,r,l){ue=e;var u=0;do{if(Gr&&(Vr=null),_l=0,Gr=!1,25<=u)throw Error(s(301));if(u+=1,pn=je=null,e.updateQueue!=null){var h=e.updateQueue;h.lastEffect=null,h.events=null,h.stores=null,h.memoCache!=null&&(h.memoCache.index=0)}B.H=Cv,h=i(r,l)}while(Gr);return h}function xM(){var e=B.H,i=e.useState()[0];return i=typeof i.then=="function"?yl(i):i,e=e.useState()[0],(je!==null?je.memoizedState:null)!==e&&(ue.flags|=1024),i}function gd(){var e=kc!==0;return kc=0,e}function vd(e,i,r){i.updateQueue=e.updateQueue,i.flags&=-2053,e.lanes&=~r}function _d(e){if(jc){for(e=e.memoizedState;e!==null;){var i=e.queue;i!==null&&(i.pending=null),e=e.next}jc=!1}ua=0,pn=je=ue=null,Gr=!1,_l=kc=0,Vr=null}function jn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return pn===null?ue.memoizedState=pn=e:pn=pn.next=e,pn}function fn(){if(je===null){var e=ue.alternate;e=e!==null?e.memoizedState:null}else e=je.next;var i=pn===null?ue.memoizedState:pn.next;if(i!==null)pn=i,je=e;else{if(e===null)throw ue.alternate===null?Error(s(467)):Error(s(310));je=e,e={memoizedState:je.memoizedState,baseState:je.baseState,baseQueue:je.baseQueue,queue:je.queue,next:null},pn===null?ue.memoizedState=pn=e:pn=pn.next=e}return pn}function Xc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function yl(e){var i=_l;return _l+=1,Vr===null&&(Vr=[]),e=Pg(Vr,e,i),i=ue,(pn===null?i.memoizedState:pn.next)===null&&(i=i.alternate,B.H=i===null||i.memoizedState===null?Av:Nd),e}function qc(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return yl(e);if(e.$$typeof===D)return Dn(e)}throw Error(s(438,String(e)))}function yd(e){var i=null,r=ue.updateQueue;if(r!==null&&(i=r.memoCache),i==null){var l=ue.alternate;l!==null&&(l=l.updateQueue,l!==null&&(l=l.memoCache,l!=null&&(i={data:l.data.map(function(u){return u.slice()}),index:0})))}if(i==null&&(i={data:[],index:0}),r===null&&(r=Xc(),ue.updateQueue=r),r.memoCache=i,r=i.data[i.index],r===void 0)for(r=i.data[i.index]=Array(e),l=0;l<e;l++)r[l]=N;return i.index++,r}function fa(e,i){return typeof i=="function"?i(e):i}function Wc(e){var i=fn();return xd(i,je,e)}function xd(e,i,r){var l=e.queue;if(l===null)throw Error(s(311));l.lastRenderedReducer=r;var u=e.baseQueue,h=l.pending;if(h!==null){if(u!==null){var b=u.next;u.next=h.next,h.next=b}i.baseQueue=u=h,l.pending=null}if(h=e.baseState,u===null)e.memoizedState=h;else{i=u.next;var A=b=null,F=null,et=i,ht=!1;do{var _t=et.lane&-536870913;if(_t!==et.lane?(be&_t)===_t:(ua&_t)===_t){var it=et.revertLane;if(it===0)F!==null&&(F=F.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),_t===zr&&(ht=!0);else if((ua&it)===it){et=et.next,it===zr&&(ht=!0);continue}else _t={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},F===null?(A=F=_t,b=h):F=F.next=_t,ue.lanes|=it,Ja|=it;_t=et.action,Xs&&r(h,_t),h=et.hasEagerState?et.eagerState:r(h,_t)}else it={lane:_t,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},F===null?(A=F=it,b=h):F=F.next=it,ue.lanes|=_t,Ja|=_t;et=et.next}while(et!==null&&et!==i);if(F===null?b=h:F.next=A,!ri(h,e.memoizedState)&&(mn=!0,ht&&(r=Ir,r!==null)))throw r;e.memoizedState=h,e.baseState=b,e.baseQueue=F,l.lastRenderedState=h}return u===null&&(l.lanes=0),[e.memoizedState,l.dispatch]}function Sd(e){var i=fn(),r=i.queue;if(r===null)throw Error(s(311));r.lastRenderedReducer=e;var l=r.dispatch,u=r.pending,h=i.memoizedState;if(u!==null){r.pending=null;var b=u=u.next;do h=e(h,b.action),b=b.next;while(b!==u);ri(h,i.memoizedState)||(mn=!0),i.memoizedState=h,i.baseQueue===null&&(i.baseState=h),r.lastRenderedState=h}return[h,l]}function qg(e,i,r){var l=ue,u=fn(),h=Ce;if(h){if(r===void 0)throw Error(s(407));r=r()}else r=i();var b=!ri((je||u).memoizedState,r);if(b&&(u.memoizedState=r,mn=!0),u=u.queue,bd(Qg.bind(null,l,u,e),[e]),u.getSnapshot!==i||b||pn!==null&&pn.memoizedState.tag&1){if(l.flags|=2048,jr(9,{destroy:void 0},Yg.bind(null,l,u,r,i),null),Qe===null)throw Error(s(349));h||(ua&127)!==0||Wg(l,i,r)}return r}function Wg(e,i,r){e.flags|=16384,e={getSnapshot:i,value:r},i=ue.updateQueue,i===null?(i=Xc(),ue.updateQueue=i,i.stores=[e]):(r=i.stores,r===null?i.stores=[e]:r.push(e))}function Yg(e,i,r,l){i.value=r,i.getSnapshot=l,Zg(i)&&Kg(e)}function Qg(e,i,r){return r(function(){Zg(i)&&Kg(e)})}function Zg(e){var i=e.getSnapshot;e=e.value;try{var r=i();return!ri(e,r)}catch{return!0}}function Kg(e){var i=zs(e,2);i!==null&&ti(i,e,2)}function Md(e){var i=jn();if(typeof e=="function"){var r=e;if(e=r(),Xs){Ot(!0);try{r()}finally{Ot(!1)}}}return i.memoizedState=i.baseState=e,i.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:e},i}function Jg(e,i,r,l){return e.baseState=r,xd(e,je,typeof l=="function"?l:fa)}function SM(e,i,r,l,u){if(Zc(e))throw Error(s(485));if(e=i.action,e!==null){var h={payload:u,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(b){h.listeners.push(b)}};B.T!==null?r(!0):h.isTransition=!1,l(h),r=i.pending,r===null?(h.next=i.pending=h,$g(i,h)):(h.next=r.next,i.pending=r.next=h)}}function $g(e,i){var r=i.action,l=i.payload,u=e.state;if(i.isTransition){var h=B.T,b={};B.T=b;try{var A=r(u,l),F=B.S;F!==null&&F(b,A),tv(e,i,A)}catch(et){Ed(e,i,et)}finally{h!==null&&b.types!==null&&(h.types=b.types),B.T=h}}else try{h=r(u,l),tv(e,i,h)}catch(et){Ed(e,i,et)}}function tv(e,i,r){r!==null&&typeof r=="object"&&typeof r.then=="function"?r.then(function(l){ev(e,i,l)},function(l){return Ed(e,i,l)}):ev(e,i,r)}function ev(e,i,r){i.status="fulfilled",i.value=r,nv(i),e.state=r,i=e.pending,i!==null&&(r=i.next,r===i?e.pending=null:(r=r.next,i.next=r,$g(e,r)))}function Ed(e,i,r){var l=e.pending;if(e.pending=null,l!==null){l=l.next;do i.status="rejected",i.reason=r,nv(i),i=i.next;while(i!==l)}e.action=null}function nv(e){e=e.listeners;for(var i=0;i<e.length;i++)(0,e[i])()}function iv(e,i){return i}function av(e,i){if(Ce){var r=Qe.formState;if(r!==null){t:{var l=ue;if(Ce){if(Ke){e:{for(var u=Ke,h=Ei;u.nodeType!==8;){if(!h){u=null;break e}if(u=Ti(u.nextSibling),u===null){u=null;break e}}h=u.data,u=h==="F!"||h==="F"?u:null}if(u){Ke=Ti(u.nextSibling),l=u.data==="F!";break t}}ja(l)}l=!1}l&&(i=r[0])}}return r=jn(),r.memoizedState=r.baseState=i,l={pending:null,lanes:0,dispatch:null,lastRenderedReducer:iv,lastRenderedState:i},r.queue=l,r=Ev.bind(null,ue,l),l.dispatch=r,l=Md(!1),h=wd.bind(null,ue,!1,l.queue),l=jn(),u={state:i,dispatch:null,action:e,pending:null},l.queue=u,r=SM.bind(null,ue,u,h,r),u.dispatch=r,l.memoizedState=e,[i,r,!1]}function sv(e){var i=fn();return rv(i,je,e)}function rv(e,i,r){if(i=xd(e,i,iv)[0],e=Wc(fa)[0],typeof i=="object"&&i!==null&&typeof i.then=="function")try{var l=yl(i)}catch(b){throw b===Br?Ic:b}else l=i;i=fn();var u=i.queue,h=u.dispatch;return r!==i.memoizedState&&(ue.flags|=2048,jr(9,{destroy:void 0},MM.bind(null,u,r),null)),[l,h,e]}function MM(e,i){e.action=i}function ov(e){var i=fn(),r=je;if(r!==null)return rv(i,r,e);fn(),i=i.memoizedState,r=fn();var l=r.queue.dispatch;return r.memoizedState=e,[i,l,!1]}function jr(e,i,r,l){return e={tag:e,create:r,deps:l,inst:i,next:null},i=ue.updateQueue,i===null&&(i=Xc(),ue.updateQueue=i),r=i.lastEffect,r===null?i.lastEffect=e.next=e:(l=r.next,r.next=e,e.next=l,i.lastEffect=e),e}function lv(){return fn().memoizedState}function Yc(e,i,r,l){var u=jn();ue.flags|=e,u.memoizedState=jr(1|i,{destroy:void 0},r,l===void 0?null:l)}function Qc(e,i,r,l){var u=fn();l=l===void 0?null:l;var h=u.memoizedState.inst;je!==null&&l!==null&&pd(l,je.memoizedState.deps)?u.memoizedState=jr(i,h,r,l):(ue.flags|=e,u.memoizedState=jr(1|i,h,r,l))}function cv(e,i){Yc(8390656,8,e,i)}function bd(e,i){Qc(2048,8,e,i)}function EM(e){ue.flags|=4;var i=ue.updateQueue;if(i===null)i=Xc(),ue.updateQueue=i,i.events=[e];else{var r=i.events;r===null?i.events=[e]:r.push(e)}}function uv(e){var i=fn().memoizedState;return EM({ref:i,nextImpl:e}),function(){if((ze&2)!==0)throw Error(s(440));return i.impl.apply(void 0,arguments)}}function fv(e,i){return Qc(4,2,e,i)}function dv(e,i){return Qc(4,4,e,i)}function hv(e,i){if(typeof i=="function"){e=e();var r=i(e);return function(){typeof r=="function"?r():i(null)}}if(i!=null)return e=e(),i.current=e,function(){i.current=null}}function pv(e,i,r){r=r!=null?r.concat([e]):null,Qc(4,4,hv.bind(null,i,e),r)}function Td(){}function mv(e,i){var r=fn();i=i===void 0?null:i;var l=r.memoizedState;return i!==null&&pd(i,l[1])?l[0]:(r.memoizedState=[e,i],e)}function gv(e,i){var r=fn();i=i===void 0?null:i;var l=r.memoizedState;if(i!==null&&pd(i,l[1]))return l[0];if(l=e(),Xs){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[l,i],l}function Ad(e,i,r){return r===void 0||(ua&1073741824)!==0&&(be&261930)===0?e.memoizedState=i:(e.memoizedState=r,e=v_(),ue.lanes|=e,Ja|=e,r)}function vv(e,i,r,l){return ri(r,i)?r:Hr.current!==null?(e=Ad(e,r,l),ri(e,i)||(mn=!0),e):(ua&42)===0||(ua&1073741824)!==0&&(be&261930)===0?(mn=!0,e.memoizedState=r):(e=v_(),ue.lanes|=e,Ja|=e,i)}function _v(e,i,r,l,u){var h=Z.p;Z.p=h!==0&&8>h?h:8;var b=B.T,A={};B.T=A,wd(e,!1,i,r);try{var F=u(),et=B.S;if(et!==null&&et(A,F),F!==null&&typeof F=="object"&&typeof F.then=="function"){var ht=_M(F,l);xl(e,i,ht,di(e))}else xl(e,i,l,di(e))}catch(_t){xl(e,i,{then:function(){},status:"rejected",reason:_t},di())}finally{Z.p=h,b!==null&&A.types!==null&&(b.types=A.types),B.T=b}}function bM(){}function Cd(e,i,r,l){if(e.tag!==5)throw Error(s(476));var u=yv(e).queue;_v(e,u,i,$,r===null?bM:function(){return xv(e),r(l)})}function yv(e){var i=e.memoizedState;if(i!==null)return i;i={memoizedState:$,baseState:$,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:$},next:null};var r={};return i.next={memoizedState:r,baseState:r,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:r},next:null},e.memoizedState=i,e=e.alternate,e!==null&&(e.memoizedState=i),i}function xv(e){var i=yv(e);i.next===null&&(i=e.alternate.memoizedState),xl(e,i.next.queue,{},di())}function Rd(){return Dn(Il)}function Sv(){return fn().memoizedState}function Mv(){return fn().memoizedState}function TM(e){for(var i=e.return;i!==null;){switch(i.tag){case 24:case 3:var r=di();e=qa(r);var l=Wa(i,e,r);l!==null&&(ti(l,i,r),ml(l,i,r)),i={cache:id()},e.payload=i;return}i=i.return}}function AM(e,i,r){var l=di();r={lane:l,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},Zc(e)?bv(i,r):(r=qf(e,i,r,l),r!==null&&(ti(r,e,l),Tv(r,i,l)))}function Ev(e,i,r){var l=di();xl(e,i,r,l)}function xl(e,i,r,l){var u={lane:l,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null};if(Zc(e))bv(i,u);else{var h=e.alternate;if(e.lanes===0&&(h===null||h.lanes===0)&&(h=i.lastRenderedReducer,h!==null))try{var b=i.lastRenderedState,A=h(b,r);if(u.hasEagerState=!0,u.eagerState=A,ri(A,b))return Nc(e,i,u,0),Qe===null&&wc(),!1}catch{}finally{}if(r=qf(e,i,u,l),r!==null)return ti(r,e,l),Tv(r,i,l),!0}return!1}function wd(e,i,r,l){if(l={lane:2,revertLane:oh(),gesture:null,action:l,hasEagerState:!1,eagerState:null,next:null},Zc(e)){if(i)throw Error(s(479))}else i=qf(e,r,l,2),i!==null&&ti(i,e,2)}function Zc(e){var i=e.alternate;return e===ue||i!==null&&i===ue}function bv(e,i){Gr=jc=!0;var r=e.pending;r===null?i.next=i:(i.next=r.next,r.next=i),e.pending=i}function Tv(e,i,r){if((r&4194048)!==0){var l=i.lanes;l&=e.pendingLanes,r|=l,i.lanes=r,Ko(e,r)}}var Sl={readContext:Dn,use:qc,useCallback:rn,useContext:rn,useEffect:rn,useImperativeHandle:rn,useLayoutEffect:rn,useInsertionEffect:rn,useMemo:rn,useReducer:rn,useRef:rn,useState:rn,useDebugValue:rn,useDeferredValue:rn,useTransition:rn,useSyncExternalStore:rn,useId:rn,useHostTransitionStatus:rn,useFormState:rn,useActionState:rn,useOptimistic:rn,useMemoCache:rn,useCacheRefresh:rn};Sl.useEffectEvent=rn;var Av={readContext:Dn,use:qc,useCallback:function(e,i){return jn().memoizedState=[e,i===void 0?null:i],e},useContext:Dn,useEffect:cv,useImperativeHandle:function(e,i,r){r=r!=null?r.concat([e]):null,Yc(4194308,4,hv.bind(null,i,e),r)},useLayoutEffect:function(e,i){return Yc(4194308,4,e,i)},useInsertionEffect:function(e,i){Yc(4,2,e,i)},useMemo:function(e,i){var r=jn();i=i===void 0?null:i;var l=e();if(Xs){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[l,i],l},useReducer:function(e,i,r){var l=jn();if(r!==void 0){var u=r(i);if(Xs){Ot(!0);try{r(i)}finally{Ot(!1)}}}else u=i;return l.memoizedState=l.baseState=u,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:u},l.queue=e,e=e.dispatch=AM.bind(null,ue,e),[l.memoizedState,e]},useRef:function(e){var i=jn();return e={current:e},i.memoizedState=e},useState:function(e){e=Md(e);var i=e.queue,r=Ev.bind(null,ue,i);return i.dispatch=r,[e.memoizedState,r]},useDebugValue:Td,useDeferredValue:function(e,i){var r=jn();return Ad(r,e,i)},useTransition:function(){var e=Md(!1);return e=_v.bind(null,ue,e.queue,!0,!1),jn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,i,r){var l=ue,u=jn();if(Ce){if(r===void 0)throw Error(s(407));r=r()}else{if(r=i(),Qe===null)throw Error(s(349));(be&127)!==0||Wg(l,i,r)}u.memoizedState=r;var h={value:r,getSnapshot:i};return u.queue=h,cv(Qg.bind(null,l,h,e),[e]),l.flags|=2048,jr(9,{destroy:void 0},Yg.bind(null,l,h,r,i),null),r},useId:function(){var e=jn(),i=Qe.identifierPrefix;if(Ce){var r=qi,l=Xi;r=(l&~(1<<32-ne(l)-1)).toString(32)+r,i="_"+i+"R_"+r,r=kc++,0<r&&(i+="H"+r.toString(32)),i+="_"}else r=yM++,i="_"+i+"r_"+r.toString(32)+"_";return e.memoizedState=i},useHostTransitionStatus:Rd,useFormState:av,useActionState:av,useOptimistic:function(e){var i=jn();i.memoizedState=i.baseState=e;var r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return i.queue=r,i=wd.bind(null,ue,!0,r),r.dispatch=i,[e,i]},useMemoCache:yd,useCacheRefresh:function(){return jn().memoizedState=TM.bind(null,ue)},useEffectEvent:function(e){var i=jn(),r={impl:e};return i.memoizedState=r,function(){if((ze&2)!==0)throw Error(s(440));return r.impl.apply(void 0,arguments)}}},Nd={readContext:Dn,use:qc,useCallback:mv,useContext:Dn,useEffect:bd,useImperativeHandle:pv,useInsertionEffect:fv,useLayoutEffect:dv,useMemo:gv,useReducer:Wc,useRef:lv,useState:function(){return Wc(fa)},useDebugValue:Td,useDeferredValue:function(e,i){var r=fn();return vv(r,je.memoizedState,e,i)},useTransition:function(){var e=Wc(fa)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:yl(e),i]},useSyncExternalStore:qg,useId:Sv,useHostTransitionStatus:Rd,useFormState:sv,useActionState:sv,useOptimistic:function(e,i){var r=fn();return Jg(r,je,e,i)},useMemoCache:yd,useCacheRefresh:Mv};Nd.useEffectEvent=uv;var Cv={readContext:Dn,use:qc,useCallback:mv,useContext:Dn,useEffect:bd,useImperativeHandle:pv,useInsertionEffect:fv,useLayoutEffect:dv,useMemo:gv,useReducer:Sd,useRef:lv,useState:function(){return Sd(fa)},useDebugValue:Td,useDeferredValue:function(e,i){var r=fn();return je===null?Ad(r,e,i):vv(r,je.memoizedState,e,i)},useTransition:function(){var e=Sd(fa)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:yl(e),i]},useSyncExternalStore:qg,useId:Sv,useHostTransitionStatus:Rd,useFormState:ov,useActionState:ov,useOptimistic:function(e,i){var r=fn();return je!==null?Jg(r,je,e,i):(r.baseState=e,[e,r.queue.dispatch])},useMemoCache:yd,useCacheRefresh:Mv};Cv.useEffectEvent=uv;function Dd(e,i,r,l){i=e.memoizedState,r=r(l,i),r=r==null?i:_({},i,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var Ud={enqueueSetState:function(e,i,r){e=e._reactInternals;var l=di(),u=qa(l);u.payload=i,r!=null&&(u.callback=r),i=Wa(e,u,l),i!==null&&(ti(i,e,l),ml(i,e,l))},enqueueReplaceState:function(e,i,r){e=e._reactInternals;var l=di(),u=qa(l);u.tag=1,u.payload=i,r!=null&&(u.callback=r),i=Wa(e,u,l),i!==null&&(ti(i,e,l),ml(i,e,l))},enqueueForceUpdate:function(e,i){e=e._reactInternals;var r=di(),l=qa(r);l.tag=2,i!=null&&(l.callback=i),i=Wa(e,l,r),i!==null&&(ti(i,e,r),ml(i,e,r))}};function Rv(e,i,r,l,u,h,b){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(l,h,b):i.prototype&&i.prototype.isPureReactComponent?!ol(r,l)||!ol(u,h):!0}function wv(e,i,r,l){e=i.state,typeof i.componentWillReceiveProps=="function"&&i.componentWillReceiveProps(r,l),typeof i.UNSAFE_componentWillReceiveProps=="function"&&i.UNSAFE_componentWillReceiveProps(r,l),i.state!==e&&Ud.enqueueReplaceState(i,i.state,null)}function qs(e,i){var r=i;if("ref"in i){r={};for(var l in i)l!=="ref"&&(r[l]=i[l])}if(e=e.defaultProps){r===i&&(r=_({},r));for(var u in e)r[u]===void 0&&(r[u]=e[u])}return r}function Nv(e){Rc(e)}function Dv(e){console.error(e)}function Uv(e){Rc(e)}function Kc(e,i){try{var r=e.onUncaughtError;r(i.value,{componentStack:i.stack})}catch(l){setTimeout(function(){throw l})}}function Lv(e,i,r){try{var l=e.onCaughtError;l(r.value,{componentStack:r.stack,errorBoundary:i.tag===1?i.stateNode:null})}catch(u){setTimeout(function(){throw u})}}function Ld(e,i,r){return r=qa(r),r.tag=3,r.payload={element:null},r.callback=function(){Kc(e,i)},r}function Ov(e){return e=qa(e),e.tag=3,e}function Pv(e,i,r,l){var u=r.type.getDerivedStateFromError;if(typeof u=="function"){var h=l.value;e.payload=function(){return u(h)},e.callback=function(){Lv(i,r,l)}}var b=r.stateNode;b!==null&&typeof b.componentDidCatch=="function"&&(e.callback=function(){Lv(i,r,l),typeof u!="function"&&($a===null?$a=new Set([this]):$a.add(this));var A=l.stack;this.componentDidCatch(l.value,{componentStack:A!==null?A:""})})}function CM(e,i,r,l,u){if(r.flags|=32768,l!==null&&typeof l=="object"&&typeof l.then=="function"){if(i=r.alternate,i!==null&&Pr(i,r,u,!0),r=li.current,r!==null){switch(r.tag){case 31:case 13:return bi===null?cu():r.alternate===null&&on===0&&(on=3),r.flags&=-257,r.flags|=65536,r.lanes=u,l===Bc?r.flags|=16384:(i=r.updateQueue,i===null?r.updateQueue=new Set([l]):i.add(l),ah(e,l,u)),!1;case 22:return r.flags|=65536,l===Bc?r.flags|=16384:(i=r.updateQueue,i===null?(i={transitions:null,markerInstances:null,retryQueue:new Set([l])},r.updateQueue=i):(r=i.retryQueue,r===null?i.retryQueue=new Set([l]):r.add(l)),ah(e,l,u)),!1}throw Error(s(435,r.tag))}return ah(e,l,u),cu(),!1}if(Ce)return i=li.current,i!==null?((i.flags&65536)===0&&(i.flags|=256),i.flags|=65536,i.lanes=u,l!==Jf&&(e=Error(s(422),{cause:l}),ul(xi(e,r)))):(l!==Jf&&(i=Error(s(423),{cause:l}),ul(xi(i,r))),e=e.current.alternate,e.flags|=65536,u&=-u,e.lanes|=u,l=xi(l,r),u=Ld(e.stateNode,l,u),cd(e,u),on!==4&&(on=2)),!1;var h=Error(s(520),{cause:l});if(h=xi(h,r),wl===null?wl=[h]:wl.push(h),on!==4&&(on=2),i===null)return!0;l=xi(l,r),r=i;do{switch(r.tag){case 3:return r.flags|=65536,e=u&-u,r.lanes|=e,e=Ld(r.stateNode,l,e),cd(r,e),!1;case 1:if(i=r.type,h=r.stateNode,(r.flags&128)===0&&(typeof i.getDerivedStateFromError=="function"||h!==null&&typeof h.componentDidCatch=="function"&&($a===null||!$a.has(h))))return r.flags|=65536,u&=-u,r.lanes|=u,u=Ov(u),Pv(u,e,r,l),cd(r,u),!1}r=r.return}while(r!==null);return!1}var Od=Error(s(461)),mn=!1;function Un(e,i,r,l){i.child=e===null?Fg(i,null,r,l):ks(i,e.child,r,l)}function zv(e,i,r,l,u){r=r.render;var h=i.ref;if("ref"in l){var b={};for(var A in l)A!=="ref"&&(b[A]=l[A])}else b=l;return Hs(i),l=md(e,i,r,b,h,u),A=gd(),e!==null&&!mn?(vd(e,i,u),da(e,i,u)):(Ce&&A&&Zf(i),i.flags|=1,Un(e,i,l,u),i.child)}function Iv(e,i,r,l,u){if(e===null){var h=r.type;return typeof h=="function"&&!Wf(h)&&h.defaultProps===void 0&&r.compare===null?(i.tag=15,i.type=h,Bv(e,i,h,l,u)):(e=Uc(r.type,null,l,i,i.mode,u),e.ref=i.ref,e.return=i,i.child=e)}if(h=e.child,!Vd(e,u)){var b=h.memoizedProps;if(r=r.compare,r=r!==null?r:ol,r(b,l)&&e.ref===i.ref)return da(e,i,u)}return i.flags|=1,e=ra(h,l),e.ref=i.ref,e.return=i,i.child=e}function Bv(e,i,r,l,u){if(e!==null){var h=e.memoizedProps;if(ol(h,l)&&e.ref===i.ref)if(mn=!1,i.pendingProps=l=h,Vd(e,u))(e.flags&131072)!==0&&(mn=!0);else return i.lanes=e.lanes,da(e,i,u)}return Pd(e,i,r,l,u)}function Fv(e,i,r,l){var u=l.children,h=e!==null?e.memoizedState:null;if(e===null&&i.stateNode===null&&(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),l.mode==="hidden"){if((i.flags&128)!==0){if(h=h!==null?h.baseLanes|r:r,e!==null){for(l=i.child=e.child,u=0;l!==null;)u=u|l.lanes|l.childLanes,l=l.sibling;l=u&~h}else l=0,i.child=null;return Hv(e,i,h,r,l)}if((r&536870912)!==0)i.memoizedState={baseLanes:0,cachePool:null},e!==null&&zc(i,h!==null?h.cachePool:null),h!==null?Vg(i,h):fd(),jg(i);else return l=i.lanes=536870912,Hv(e,i,h!==null?h.baseLanes|r:r,r,l)}else h!==null?(zc(i,h.cachePool),Vg(i,h),Qa(),i.memoizedState=null):(e!==null&&zc(i,null),fd(),Qa());return Un(e,i,u,r),i.child}function Ml(e,i){return e!==null&&e.tag===22||i.stateNode!==null||(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),i.sibling}function Hv(e,i,r,l,u){var h=sd();return h=h===null?null:{parent:hn._currentValue,pool:h},i.memoizedState={baseLanes:r,cachePool:h},e!==null&&zc(i,null),fd(),jg(i),e!==null&&Pr(e,i,l,!0),i.childLanes=u,null}function Jc(e,i){return i=tu({mode:i.mode,children:i.children},e.mode),i.ref=e.ref,e.child=i,i.return=e,i}function Gv(e,i,r){return ks(i,e.child,null,r),e=Jc(i,i.pendingProps),e.flags|=2,ci(i),i.memoizedState=null,e}function RM(e,i,r){var l=i.pendingProps,u=(i.flags&128)!==0;if(i.flags&=-129,e===null){if(Ce){if(l.mode==="hidden")return e=Jc(i,l),i.lanes=536870912,Ml(null,e);if(hd(i),(e=Ke)?(e=$_(e,Ei),e=e!==null&&e.data==="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Ga!==null?{id:Xi,overflow:qi}:null,retryLane:536870912,hydrationErrors:null},r=bg(e),r.return=i,i.child=r,Nn=i,Ke=null)):e=null,e===null)throw ja(i);return i.lanes=536870912,null}return Jc(i,l)}var h=e.memoizedState;if(h!==null){var b=h.dehydrated;if(hd(i),u)if(i.flags&256)i.flags&=-257,i=Gv(e,i,r);else if(i.memoizedState!==null)i.child=e.child,i.flags|=128,i=null;else throw Error(s(558));else if(mn||Pr(e,i,r,!1),u=(r&e.childLanes)!==0,mn||u){if(l=Qe,l!==null&&(b=ji(l,r),b!==0&&b!==h.retryLane))throw h.retryLane=b,zs(e,b),ti(l,e,b),Od;cu(),i=Gv(e,i,r)}else e=h.treeContext,Ke=Ti(b.nextSibling),Nn=i,Ce=!0,Va=null,Ei=!1,e!==null&&Cg(i,e),i=Jc(i,l),i.flags|=4096;return i}return e=ra(e.child,{mode:l.mode,children:l.children}),e.ref=i.ref,i.child=e,e.return=i,e}function $c(e,i){var r=i.ref;if(r===null)e!==null&&e.ref!==null&&(i.flags|=4194816);else{if(typeof r!="function"&&typeof r!="object")throw Error(s(284));(e===null||e.ref!==r)&&(i.flags|=4194816)}}function Pd(e,i,r,l,u){return Hs(i),r=md(e,i,r,l,void 0,u),l=gd(),e!==null&&!mn?(vd(e,i,u),da(e,i,u)):(Ce&&l&&Zf(i),i.flags|=1,Un(e,i,r,u),i.child)}function Vv(e,i,r,l,u,h){return Hs(i),i.updateQueue=null,r=Xg(i,l,r,u),kg(e),l=gd(),e!==null&&!mn?(vd(e,i,h),da(e,i,h)):(Ce&&l&&Zf(i),i.flags|=1,Un(e,i,r,h),i.child)}function jv(e,i,r,l,u){if(Hs(i),i.stateNode===null){var h=Dr,b=r.contextType;typeof b=="object"&&b!==null&&(h=Dn(b)),h=new r(l,h),i.memoizedState=h.state!==null&&h.state!==void 0?h.state:null,h.updater=Ud,i.stateNode=h,h._reactInternals=i,h=i.stateNode,h.props=l,h.state=i.memoizedState,h.refs={},od(i),b=r.contextType,h.context=typeof b=="object"&&b!==null?Dn(b):Dr,h.state=i.memoizedState,b=r.getDerivedStateFromProps,typeof b=="function"&&(Dd(i,r,b,l),h.state=i.memoizedState),typeof r.getDerivedStateFromProps=="function"||typeof h.getSnapshotBeforeUpdate=="function"||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(b=h.state,typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount(),b!==h.state&&Ud.enqueueReplaceState(h,h.state,null),vl(i,l,h,u),gl(),h.state=i.memoizedState),typeof h.componentDidMount=="function"&&(i.flags|=4194308),l=!0}else if(e===null){h=i.stateNode;var A=i.memoizedProps,F=qs(r,A);h.props=F;var et=h.context,ht=r.contextType;b=Dr,typeof ht=="object"&&ht!==null&&(b=Dn(ht));var _t=r.getDerivedStateFromProps;ht=typeof _t=="function"||typeof h.getSnapshotBeforeUpdate=="function",A=i.pendingProps!==A,ht||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(A||et!==b)&&wv(i,h,l,b),Xa=!1;var it=i.memoizedState;h.state=it,vl(i,l,h,u),gl(),et=i.memoizedState,A||it!==et||Xa?(typeof _t=="function"&&(Dd(i,r,_t,l),et=i.memoizedState),(F=Xa||Rv(i,r,F,l,it,et,b))?(ht||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount()),typeof h.componentDidMount=="function"&&(i.flags|=4194308)):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),i.memoizedProps=l,i.memoizedState=et),h.props=l,h.state=et,h.context=b,l=F):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),l=!1)}else{h=i.stateNode,ld(e,i),b=i.memoizedProps,ht=qs(r,b),h.props=ht,_t=i.pendingProps,it=h.context,et=r.contextType,F=Dr,typeof et=="object"&&et!==null&&(F=Dn(et)),A=r.getDerivedStateFromProps,(et=typeof A=="function"||typeof h.getSnapshotBeforeUpdate=="function")||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(b!==_t||it!==F)&&wv(i,h,l,F),Xa=!1,it=i.memoizedState,h.state=it,vl(i,l,h,u),gl();var lt=i.memoizedState;b!==_t||it!==lt||Xa||e!==null&&e.dependencies!==null&&Oc(e.dependencies)?(typeof A=="function"&&(Dd(i,r,A,l),lt=i.memoizedState),(ht=Xa||Rv(i,r,ht,l,it,lt,F)||e!==null&&e.dependencies!==null&&Oc(e.dependencies))?(et||typeof h.UNSAFE_componentWillUpdate!="function"&&typeof h.componentWillUpdate!="function"||(typeof h.componentWillUpdate=="function"&&h.componentWillUpdate(l,lt,F),typeof h.UNSAFE_componentWillUpdate=="function"&&h.UNSAFE_componentWillUpdate(l,lt,F)),typeof h.componentDidUpdate=="function"&&(i.flags|=4),typeof h.getSnapshotBeforeUpdate=="function"&&(i.flags|=1024)):(typeof h.componentDidUpdate!="function"||b===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),i.memoizedProps=l,i.memoizedState=lt),h.props=l,h.state=lt,h.context=F,l=ht):(typeof h.componentDidUpdate!="function"||b===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||b===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),l=!1)}return h=l,$c(e,i),l=(i.flags&128)!==0,h||l?(h=i.stateNode,r=l&&typeof r.getDerivedStateFromError!="function"?null:h.render(),i.flags|=1,e!==null&&l?(i.child=ks(i,e.child,null,u),i.child=ks(i,null,r,u)):Un(e,i,r,u),i.memoizedState=h.state,e=i.child):e=da(e,i,u),e}function kv(e,i,r,l){return Bs(),i.flags|=256,Un(e,i,r,l),i.child}var zd={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function Id(e){return{baseLanes:e,cachePool:Lg()}}function Bd(e,i,r){return e=e!==null?e.childLanes&~r:0,i&&(e|=fi),e}function Xv(e,i,r){var l=i.pendingProps,u=!1,h=(i.flags&128)!==0,b;if((b=h)||(b=e!==null&&e.memoizedState===null?!1:(un.current&2)!==0),b&&(u=!0,i.flags&=-129),b=(i.flags&32)!==0,i.flags&=-33,e===null){if(Ce){if(u?Ya(i):Qa(),(e=Ke)?(e=$_(e,Ei),e=e!==null&&e.data!=="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Ga!==null?{id:Xi,overflow:qi}:null,retryLane:536870912,hydrationErrors:null},r=bg(e),r.return=i,i.child=r,Nn=i,Ke=null)):e=null,e===null)throw ja(i);return xh(e)?i.lanes=32:i.lanes=536870912,null}var A=l.children;return l=l.fallback,u?(Qa(),u=i.mode,A=tu({mode:"hidden",children:A},u),l=Is(l,u,r,null),A.return=i,l.return=i,A.sibling=l,i.child=A,l=i.child,l.memoizedState=Id(r),l.childLanes=Bd(e,b,r),i.memoizedState=zd,Ml(null,l)):(Ya(i),Fd(i,A))}var F=e.memoizedState;if(F!==null&&(A=F.dehydrated,A!==null)){if(h)i.flags&256?(Ya(i),i.flags&=-257,i=Hd(e,i,r)):i.memoizedState!==null?(Qa(),i.child=e.child,i.flags|=128,i=null):(Qa(),A=l.fallback,u=i.mode,l=tu({mode:"visible",children:l.children},u),A=Is(A,u,r,null),A.flags|=2,l.return=i,A.return=i,l.sibling=A,i.child=l,ks(i,e.child,null,r),l=i.child,l.memoizedState=Id(r),l.childLanes=Bd(e,b,r),i.memoizedState=zd,i=Ml(null,l));else if(Ya(i),xh(A)){if(b=A.nextSibling&&A.nextSibling.dataset,b)var et=b.dgst;b=et,l=Error(s(419)),l.stack="",l.digest=b,ul({value:l,source:null,stack:null}),i=Hd(e,i,r)}else if(mn||Pr(e,i,r,!1),b=(r&e.childLanes)!==0,mn||b){if(b=Qe,b!==null&&(l=ji(b,r),l!==0&&l!==F.retryLane))throw F.retryLane=l,zs(e,l),ti(b,e,l),Od;yh(A)||cu(),i=Hd(e,i,r)}else yh(A)?(i.flags|=192,i.child=e.child,i=null):(e=F.treeContext,Ke=Ti(A.nextSibling),Nn=i,Ce=!0,Va=null,Ei=!1,e!==null&&Cg(i,e),i=Fd(i,l.children),i.flags|=4096);return i}return u?(Qa(),A=l.fallback,u=i.mode,F=e.child,et=F.sibling,l=ra(F,{mode:"hidden",children:l.children}),l.subtreeFlags=F.subtreeFlags&65011712,et!==null?A=ra(et,A):(A=Is(A,u,r,null),A.flags|=2),A.return=i,l.return=i,l.sibling=A,i.child=l,Ml(null,l),l=i.child,A=e.child.memoizedState,A===null?A=Id(r):(u=A.cachePool,u!==null?(F=hn._currentValue,u=u.parent!==F?{parent:F,pool:F}:u):u=Lg(),A={baseLanes:A.baseLanes|r,cachePool:u}),l.memoizedState=A,l.childLanes=Bd(e,b,r),i.memoizedState=zd,Ml(e.child,l)):(Ya(i),r=e.child,e=r.sibling,r=ra(r,{mode:"visible",children:l.children}),r.return=i,r.sibling=null,e!==null&&(b=i.deletions,b===null?(i.deletions=[e],i.flags|=16):b.push(e)),i.child=r,i.memoizedState=null,r)}function Fd(e,i){return i=tu({mode:"visible",children:i},e.mode),i.return=e,e.child=i}function tu(e,i){return e=oi(22,e,null,i),e.lanes=0,e}function Hd(e,i,r){return ks(i,e.child,null,r),e=Fd(i,i.pendingProps.children),e.flags|=2,i.memoizedState=null,e}function qv(e,i,r){e.lanes|=i;var l=e.alternate;l!==null&&(l.lanes|=i),ed(e.return,i,r)}function Gd(e,i,r,l,u,h){var b=e.memoizedState;b===null?e.memoizedState={isBackwards:i,rendering:null,renderingStartTime:0,last:l,tail:r,tailMode:u,treeForkCount:h}:(b.isBackwards=i,b.rendering=null,b.renderingStartTime=0,b.last=l,b.tail=r,b.tailMode=u,b.treeForkCount=h)}function Wv(e,i,r){var l=i.pendingProps,u=l.revealOrder,h=l.tail;l=l.children;var b=un.current,A=(b&2)!==0;if(A?(b=b&1|2,i.flags|=128):b&=1,St(un,b),Un(e,i,l,r),l=Ce?cl:0,!A&&e!==null&&(e.flags&128)!==0)t:for(e=i.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&qv(e,r,i);else if(e.tag===19)qv(e,r,i);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===i)break t;for(;e.sibling===null;){if(e.return===null||e.return===i)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(u){case"forwards":for(r=i.child,u=null;r!==null;)e=r.alternate,e!==null&&Vc(e)===null&&(u=r),r=r.sibling;r=u,r===null?(u=i.child,i.child=null):(u=r.sibling,r.sibling=null),Gd(i,!1,u,r,h,l);break;case"backwards":case"unstable_legacy-backwards":for(r=null,u=i.child,i.child=null;u!==null;){if(e=u.alternate,e!==null&&Vc(e)===null){i.child=u;break}e=u.sibling,u.sibling=r,r=u,u=e}Gd(i,!0,r,null,h,l);break;case"together":Gd(i,!1,null,null,void 0,l);break;default:i.memoizedState=null}return i.child}function da(e,i,r){if(e!==null&&(i.dependencies=e.dependencies),Ja|=i.lanes,(r&i.childLanes)===0)if(e!==null){if(Pr(e,i,r,!1),(r&i.childLanes)===0)return null}else return null;if(e!==null&&i.child!==e.child)throw Error(s(153));if(i.child!==null){for(e=i.child,r=ra(e,e.pendingProps),i.child=r,r.return=i;e.sibling!==null;)e=e.sibling,r=r.sibling=ra(e,e.pendingProps),r.return=i;r.sibling=null}return i.child}function Vd(e,i){return(e.lanes&i)!==0?!0:(e=e.dependencies,!!(e!==null&&Oc(e)))}function wM(e,i,r){switch(i.tag){case 3:Ft(i,i.stateNode.containerInfo),ka(i,hn,e.memoizedState.cache),Bs();break;case 27:case 5:oe(i);break;case 4:Ft(i,i.stateNode.containerInfo);break;case 10:ka(i,i.type,i.memoizedProps.value);break;case 31:if(i.memoizedState!==null)return i.flags|=128,hd(i),null;break;case 13:var l=i.memoizedState;if(l!==null)return l.dehydrated!==null?(Ya(i),i.flags|=128,null):(r&i.child.childLanes)!==0?Xv(e,i,r):(Ya(i),e=da(e,i,r),e!==null?e.sibling:null);Ya(i);break;case 19:var u=(e.flags&128)!==0;if(l=(r&i.childLanes)!==0,l||(Pr(e,i,r,!1),l=(r&i.childLanes)!==0),u){if(l)return Wv(e,i,r);i.flags|=128}if(u=i.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),St(un,un.current),l)break;return null;case 22:return i.lanes=0,Fv(e,i,r,i.pendingProps);case 24:ka(i,hn,e.memoizedState.cache)}return da(e,i,r)}function Yv(e,i,r){if(e!==null)if(e.memoizedProps!==i.pendingProps)mn=!0;else{if(!Vd(e,r)&&(i.flags&128)===0)return mn=!1,wM(e,i,r);mn=(e.flags&131072)!==0}else mn=!1,Ce&&(i.flags&1048576)!==0&&Ag(i,cl,i.index);switch(i.lanes=0,i.tag){case 16:t:{var l=i.pendingProps;if(e=Vs(i.elementType),i.type=e,typeof e=="function")Wf(e)?(l=qs(e,l),i.tag=1,i=jv(null,i,e,l,r)):(i.tag=0,i=Pd(null,i,e,l,r));else{if(e!=null){var u=e.$$typeof;if(u===C){i.tag=11,i=zv(null,i,e,l,r);break t}else if(u===P){i.tag=14,i=Iv(null,i,e,l,r);break t}}throw i=mt(e)||e,Error(s(306,i,""))}}return i;case 0:return Pd(e,i,i.type,i.pendingProps,r);case 1:return l=i.type,u=qs(l,i.pendingProps),jv(e,i,l,u,r);case 3:t:{if(Ft(i,i.stateNode.containerInfo),e===null)throw Error(s(387));l=i.pendingProps;var h=i.memoizedState;u=h.element,ld(e,i),vl(i,l,null,r);var b=i.memoizedState;if(l=b.cache,ka(i,hn,l),l!==h.cache&&nd(i,[hn],r,!0),gl(),l=b.element,h.isDehydrated)if(h={element:l,isDehydrated:!1,cache:b.cache},i.updateQueue.baseState=h,i.memoizedState=h,i.flags&256){i=kv(e,i,l,r);break t}else if(l!==u){u=xi(Error(s(424)),i),ul(u),i=kv(e,i,l,r);break t}else{switch(e=i.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Ke=Ti(e.firstChild),Nn=i,Ce=!0,Va=null,Ei=!0,r=Fg(i,null,l,r),i.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling}else{if(Bs(),l===u){i=da(e,i,r);break t}Un(e,i,l,r)}i=i.child}return i;case 26:return $c(e,i),e===null?(r=s0(i.type,null,i.pendingProps,null))?i.memoizedState=r:Ce||(r=i.type,e=i.pendingProps,l=gu(Tt.current).createElement(r),l[sn]=i,l[wn]=e,Ln(l,r,e),xt(l),i.stateNode=l):i.memoizedState=s0(i.type,e.memoizedProps,i.pendingProps,e.memoizedState),null;case 27:return oe(i),e===null&&Ce&&(l=i.stateNode=n0(i.type,i.pendingProps,Tt.current),Nn=i,Ei=!0,u=Ke,is(i.type)?(Sh=u,Ke=Ti(l.firstChild)):Ke=u),Un(e,i,i.pendingProps.children,r),$c(e,i),e===null&&(i.flags|=4194304),i.child;case 5:return e===null&&Ce&&((u=l=Ke)&&(l=s1(l,i.type,i.pendingProps,Ei),l!==null?(i.stateNode=l,Nn=i,Ke=Ti(l.firstChild),Ei=!1,u=!0):u=!1),u||ja(i)),oe(i),u=i.type,h=i.pendingProps,b=e!==null?e.memoizedProps:null,l=h.children,gh(u,h)?l=null:b!==null&&gh(u,b)&&(i.flags|=32),i.memoizedState!==null&&(u=md(e,i,xM,null,null,r),Il._currentValue=u),$c(e,i),Un(e,i,l,r),i.child;case 6:return e===null&&Ce&&((e=r=Ke)&&(r=r1(r,i.pendingProps,Ei),r!==null?(i.stateNode=r,Nn=i,Ke=null,e=!0):e=!1),e||ja(i)),null;case 13:return Xv(e,i,r);case 4:return Ft(i,i.stateNode.containerInfo),l=i.pendingProps,e===null?i.child=ks(i,null,l,r):Un(e,i,l,r),i.child;case 11:return zv(e,i,i.type,i.pendingProps,r);case 7:return Un(e,i,i.pendingProps,r),i.child;case 8:return Un(e,i,i.pendingProps.children,r),i.child;case 12:return Un(e,i,i.pendingProps.children,r),i.child;case 10:return l=i.pendingProps,ka(i,i.type,l.value),Un(e,i,l.children,r),i.child;case 9:return u=i.type._context,l=i.pendingProps.children,Hs(i),u=Dn(u),l=l(u),i.flags|=1,Un(e,i,l,r),i.child;case 14:return Iv(e,i,i.type,i.pendingProps,r);case 15:return Bv(e,i,i.type,i.pendingProps,r);case 19:return Wv(e,i,r);case 31:return RM(e,i,r);case 22:return Fv(e,i,r,i.pendingProps);case 24:return Hs(i),l=Dn(hn),e===null?(u=sd(),u===null&&(u=Qe,h=id(),u.pooledCache=h,h.refCount++,h!==null&&(u.pooledCacheLanes|=r),u=h),i.memoizedState={parent:l,cache:u},od(i),ka(i,hn,u)):((e.lanes&r)!==0&&(ld(e,i),vl(i,null,null,r),gl()),u=e.memoizedState,h=i.memoizedState,u.parent!==l?(u={parent:l,cache:l},i.memoizedState=u,i.lanes===0&&(i.memoizedState=i.updateQueue.baseState=u),ka(i,hn,l)):(l=h.cache,ka(i,hn,l),l!==u.cache&&nd(i,[hn],r,!0))),Un(e,i,i.pendingProps.children,r),i.child;case 29:throw i.pendingProps}throw Error(s(156,i.tag))}function ha(e){e.flags|=4}function jd(e,i,r,l,u){if((i=(e.mode&32)!==0)&&(i=!1),i){if(e.flags|=16777216,(u&335544128)===u)if(e.stateNode.complete)e.flags|=8192;else if(S_())e.flags|=8192;else throw js=Bc,rd}else e.flags&=-16777217}function Qv(e,i){if(i.type!=="stylesheet"||(i.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!u0(i))if(S_())e.flags|=8192;else throw js=Bc,rd}function eu(e,i){i!==null&&(e.flags|=4),e.flags&16384&&(i=e.tag!==22?_n():536870912,e.lanes|=i,Wr|=i)}function El(e,i){if(!Ce)switch(e.tailMode){case"hidden":i=e.tail;for(var r=null;i!==null;)i.alternate!==null&&(r=i),i=i.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var l=null;r!==null;)r.alternate!==null&&(l=r),r=r.sibling;l===null?i||e.tail===null?e.tail=null:e.tail.sibling=null:l.sibling=null}}function Je(e){var i=e.alternate!==null&&e.alternate.child===e.child,r=0,l=0;if(i)for(var u=e.child;u!==null;)r|=u.lanes|u.childLanes,l|=u.subtreeFlags&65011712,l|=u.flags&65011712,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)r|=u.lanes|u.childLanes,l|=u.subtreeFlags,l|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=l,e.childLanes=r,i}function NM(e,i,r){var l=i.pendingProps;switch(Kf(i),i.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Je(i),null;case 1:return Je(i),null;case 3:return r=i.stateNode,l=null,e!==null&&(l=e.memoizedState.cache),i.memoizedState.cache!==l&&(i.flags|=2048),ca(hn),Vt(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(Or(i)?ha(i):e===null||e.memoizedState.isDehydrated&&(i.flags&256)===0||(i.flags|=1024,$f())),Je(i),null;case 26:var u=i.type,h=i.memoizedState;return e===null?(ha(i),h!==null?(Je(i),Qv(i,h)):(Je(i),jd(i,u,null,l,r))):h?h!==e.memoizedState?(ha(i),Je(i),Qv(i,h)):(Je(i),i.flags&=-16777217):(e=e.memoizedProps,e!==l&&ha(i),Je(i),jd(i,u,e,l,r)),null;case 27:if(Ge(i),r=Tt.current,u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==l&&ha(i);else{if(!l){if(i.stateNode===null)throw Error(s(166));return Je(i),null}e=q.current,Or(i)?Rg(i):(e=n0(u,l,r),i.stateNode=e,ha(i))}return Je(i),null;case 5:if(Ge(i),u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==l&&ha(i);else{if(!l){if(i.stateNode===null)throw Error(s(166));return Je(i),null}if(h=q.current,Or(i))Rg(i);else{var b=gu(Tt.current);switch(h){case 1:h=b.createElementNS("http://www.w3.org/2000/svg",u);break;case 2:h=b.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;default:switch(u){case"svg":h=b.createElementNS("http://www.w3.org/2000/svg",u);break;case"math":h=b.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;case"script":h=b.createElement("div"),h.innerHTML="<script><\/script>",h=h.removeChild(h.firstChild);break;case"select":h=typeof l.is=="string"?b.createElement("select",{is:l.is}):b.createElement("select"),l.multiple?h.multiple=!0:l.size&&(h.size=l.size);break;default:h=typeof l.is=="string"?b.createElement(u,{is:l.is}):b.createElement(u)}}h[sn]=i,h[wn]=l;t:for(b=i.child;b!==null;){if(b.tag===5||b.tag===6)h.appendChild(b.stateNode);else if(b.tag!==4&&b.tag!==27&&b.child!==null){b.child.return=b,b=b.child;continue}if(b===i)break t;for(;b.sibling===null;){if(b.return===null||b.return===i)break t;b=b.return}b.sibling.return=b.return,b=b.sibling}i.stateNode=h;t:switch(Ln(h,u,l),u){case"button":case"input":case"select":case"textarea":l=!!l.autoFocus;break t;case"img":l=!0;break t;default:l=!1}l&&ha(i)}}return Je(i),jd(i,i.type,e===null?null:e.memoizedProps,i.pendingProps,r),null;case 6:if(e&&i.stateNode!=null)e.memoizedProps!==l&&ha(i);else{if(typeof l!="string"&&i.stateNode===null)throw Error(s(166));if(e=Tt.current,Or(i)){if(e=i.stateNode,r=i.memoizedProps,l=null,u=Nn,u!==null)switch(u.tag){case 27:case 5:l=u.memoizedProps}e[sn]=i,e=!!(e.nodeValue===r||l!==null&&l.suppressHydrationWarning===!0||X_(e.nodeValue,r)),e||ja(i,!0)}else e=gu(e).createTextNode(l),e[sn]=i,i.stateNode=e}return Je(i),null;case 31:if(r=i.memoizedState,e===null||e.memoizedState!==null){if(l=Or(i),r!==null){if(e===null){if(!l)throw Error(s(318));if(e=i.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(557));e[sn]=i}else Bs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Je(i),e=!1}else r=$f(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=r),e=!0;if(!e)return i.flags&256?(ci(i),i):(ci(i),null);if((i.flags&128)!==0)throw Error(s(558))}return Je(i),null;case 13:if(l=i.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(u=Or(i),l!==null&&l.dehydrated!==null){if(e===null){if(!u)throw Error(s(318));if(u=i.memoizedState,u=u!==null?u.dehydrated:null,!u)throw Error(s(317));u[sn]=i}else Bs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Je(i),u=!1}else u=$f(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=u),u=!0;if(!u)return i.flags&256?(ci(i),i):(ci(i),null)}return ci(i),(i.flags&128)!==0?(i.lanes=r,i):(r=l!==null,e=e!==null&&e.memoizedState!==null,r&&(l=i.child,u=null,l.alternate!==null&&l.alternate.memoizedState!==null&&l.alternate.memoizedState.cachePool!==null&&(u=l.alternate.memoizedState.cachePool.pool),h=null,l.memoizedState!==null&&l.memoizedState.cachePool!==null&&(h=l.memoizedState.cachePool.pool),h!==u&&(l.flags|=2048)),r!==e&&r&&(i.child.flags|=8192),eu(i,i.updateQueue),Je(i),null);case 4:return Vt(),e===null&&fh(i.stateNode.containerInfo),Je(i),null;case 10:return ca(i.type),Je(i),null;case 19:if(nt(un),l=i.memoizedState,l===null)return Je(i),null;if(u=(i.flags&128)!==0,h=l.rendering,h===null)if(u)El(l,!1);else{if(on!==0||e!==null&&(e.flags&128)!==0)for(e=i.child;e!==null;){if(h=Vc(e),h!==null){for(i.flags|=128,El(l,!1),e=h.updateQueue,i.updateQueue=e,eu(i,e),i.subtreeFlags=0,e=r,r=i.child;r!==null;)Eg(r,e),r=r.sibling;return St(un,un.current&1|2),Ce&&oa(i,l.treeForkCount),i.child}e=e.sibling}l.tail!==null&&pt()>ru&&(i.flags|=128,u=!0,El(l,!1),i.lanes=4194304)}else{if(!u)if(e=Vc(h),e!==null){if(i.flags|=128,u=!0,e=e.updateQueue,i.updateQueue=e,eu(i,e),El(l,!0),l.tail===null&&l.tailMode==="hidden"&&!h.alternate&&!Ce)return Je(i),null}else 2*pt()-l.renderingStartTime>ru&&r!==536870912&&(i.flags|=128,u=!0,El(l,!1),i.lanes=4194304);l.isBackwards?(h.sibling=i.child,i.child=h):(e=l.last,e!==null?e.sibling=h:i.child=h,l.last=h)}return l.tail!==null?(e=l.tail,l.rendering=e,l.tail=e.sibling,l.renderingStartTime=pt(),e.sibling=null,r=un.current,St(un,u?r&1|2:r&1),Ce&&oa(i,l.treeForkCount),e):(Je(i),null);case 22:case 23:return ci(i),dd(),l=i.memoizedState!==null,e!==null?e.memoizedState!==null!==l&&(i.flags|=8192):l&&(i.flags|=8192),l?(r&536870912)!==0&&(i.flags&128)===0&&(Je(i),i.subtreeFlags&6&&(i.flags|=8192)):Je(i),r=i.updateQueue,r!==null&&eu(i,r.retryQueue),r=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),l=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(l=i.memoizedState.cachePool.pool),l!==r&&(i.flags|=2048),e!==null&&nt(Gs),null;case 24:return r=null,e!==null&&(r=e.memoizedState.cache),i.memoizedState.cache!==r&&(i.flags|=2048),ca(hn),Je(i),null;case 25:return null;case 30:return null}throw Error(s(156,i.tag))}function DM(e,i){switch(Kf(i),i.tag){case 1:return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 3:return ca(hn),Vt(),e=i.flags,(e&65536)!==0&&(e&128)===0?(i.flags=e&-65537|128,i):null;case 26:case 27:case 5:return Ge(i),null;case 31:if(i.memoizedState!==null){if(ci(i),i.alternate===null)throw Error(s(340));Bs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 13:if(ci(i),e=i.memoizedState,e!==null&&e.dehydrated!==null){if(i.alternate===null)throw Error(s(340));Bs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 19:return nt(un),null;case 4:return Vt(),null;case 10:return ca(i.type),null;case 22:case 23:return ci(i),dd(),e!==null&&nt(Gs),e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 24:return ca(hn),null;case 25:return null;default:return null}}function Zv(e,i){switch(Kf(i),i.tag){case 3:ca(hn),Vt();break;case 26:case 27:case 5:Ge(i);break;case 4:Vt();break;case 31:i.memoizedState!==null&&ci(i);break;case 13:ci(i);break;case 19:nt(un);break;case 10:ca(i.type);break;case 22:case 23:ci(i),dd(),e!==null&&nt(Gs);break;case 24:ca(hn)}}function bl(e,i){try{var r=i.updateQueue,l=r!==null?r.lastEffect:null;if(l!==null){var u=l.next;r=u;do{if((r.tag&e)===e){l=void 0;var h=r.create,b=r.inst;l=h(),b.destroy=l}r=r.next}while(r!==u)}}catch(A){He(i,i.return,A)}}function Za(e,i,r){try{var l=i.updateQueue,u=l!==null?l.lastEffect:null;if(u!==null){var h=u.next;l=h;do{if((l.tag&e)===e){var b=l.inst,A=b.destroy;if(A!==void 0){b.destroy=void 0,u=i;var F=r,et=A;try{et()}catch(ht){He(u,F,ht)}}}l=l.next}while(l!==h)}}catch(ht){He(i,i.return,ht)}}function Kv(e){var i=e.updateQueue;if(i!==null){var r=e.stateNode;try{Gg(i,r)}catch(l){He(e,e.return,l)}}}function Jv(e,i,r){r.props=qs(e.type,e.memoizedProps),r.state=e.memoizedState;try{r.componentWillUnmount()}catch(l){He(e,i,l)}}function Tl(e,i){try{var r=e.ref;if(r!==null){switch(e.tag){case 26:case 27:case 5:var l=e.stateNode;break;case 30:l=e.stateNode;break;default:l=e.stateNode}typeof r=="function"?e.refCleanup=r(l):r.current=l}}catch(u){He(e,i,u)}}function Wi(e,i){var r=e.ref,l=e.refCleanup;if(r!==null)if(typeof l=="function")try{l()}catch(u){He(e,i,u)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof r=="function")try{r(null)}catch(u){He(e,i,u)}else r.current=null}function $v(e){var i=e.type,r=e.memoizedProps,l=e.stateNode;try{t:switch(i){case"button":case"input":case"select":case"textarea":r.autoFocus&&l.focus();break t;case"img":r.src?l.src=r.src:r.srcSet&&(l.srcset=r.srcSet)}}catch(u){He(e,e.return,u)}}function kd(e,i,r){try{var l=e.stateNode;$M(l,e.type,r,i),l[wn]=i}catch(u){He(e,e.return,u)}}function t_(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&is(e.type)||e.tag===4}function Xd(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||t_(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&is(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function qd(e,i,r){var l=e.tag;if(l===5||l===6)e=e.stateNode,i?(r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r).insertBefore(e,i):(i=r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r,i.appendChild(e),r=r._reactRootContainer,r!=null||i.onclick!==null||(i.onclick=aa));else if(l!==4&&(l===27&&is(e.type)&&(r=e.stateNode,i=null),e=e.child,e!==null))for(qd(e,i,r),e=e.sibling;e!==null;)qd(e,i,r),e=e.sibling}function nu(e,i,r){var l=e.tag;if(l===5||l===6)e=e.stateNode,i?r.insertBefore(e,i):r.appendChild(e);else if(l!==4&&(l===27&&is(e.type)&&(r=e.stateNode),e=e.child,e!==null))for(nu(e,i,r),e=e.sibling;e!==null;)nu(e,i,r),e=e.sibling}function e_(e){var i=e.stateNode,r=e.memoizedProps;try{for(var l=e.type,u=i.attributes;u.length;)i.removeAttributeNode(u[0]);Ln(i,l,r),i[sn]=e,i[wn]=r}catch(h){He(e,e.return,h)}}var pa=!1,gn=!1,Wd=!1,n_=typeof WeakSet=="function"?WeakSet:Set,bn=null;function UM(e,i){if(e=e.containerInfo,ph=Eu,e=pg(e),Hf(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else t:{r=(r=e.ownerDocument)&&r.defaultView||window;var l=r.getSelection&&r.getSelection();if(l&&l.rangeCount!==0){r=l.anchorNode;var u=l.anchorOffset,h=l.focusNode;l=l.focusOffset;try{r.nodeType,h.nodeType}catch{r=null;break t}var b=0,A=-1,F=-1,et=0,ht=0,_t=e,it=null;e:for(;;){for(var lt;_t!==r||u!==0&&_t.nodeType!==3||(A=b+u),_t!==h||l!==0&&_t.nodeType!==3||(F=b+l),_t.nodeType===3&&(b+=_t.nodeValue.length),(lt=_t.firstChild)!==null;)it=_t,_t=lt;for(;;){if(_t===e)break e;if(it===r&&++et===u&&(A=b),it===h&&++ht===l&&(F=b),(lt=_t.nextSibling)!==null)break;_t=it,it=_t.parentNode}_t=lt}r=A===-1||F===-1?null:{start:A,end:F}}else r=null}r=r||{start:0,end:0}}else r=null;for(mh={focusedElem:e,selectionRange:r},Eu=!1,bn=i;bn!==null;)if(i=bn,e=i.child,(i.subtreeFlags&1028)!==0&&e!==null)e.return=i,bn=e;else for(;bn!==null;){switch(i=bn,h=i.alternate,e=i.flags,i.tag){case 0:if((e&4)!==0&&(e=i.updateQueue,e=e!==null?e.events:null,e!==null))for(r=0;r<e.length;r++)u=e[r],u.ref.impl=u.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&h!==null){e=void 0,r=i,u=h.memoizedProps,h=h.memoizedState,l=r.stateNode;try{var Gt=qs(r.type,u);e=l.getSnapshotBeforeUpdate(Gt,h),l.__reactInternalSnapshotBeforeUpdate=e}catch(ee){He(r,r.return,ee)}}break;case 3:if((e&1024)!==0){if(e=i.stateNode.containerInfo,r=e.nodeType,r===9)_h(e);else if(r===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":_h(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(s(163))}if(e=i.sibling,e!==null){e.return=i.return,bn=e;break}bn=i.return}}function i_(e,i,r){var l=r.flags;switch(r.tag){case 0:case 11:case 15:ga(e,r),l&4&&bl(5,r);break;case 1:if(ga(e,r),l&4)if(e=r.stateNode,i===null)try{e.componentDidMount()}catch(b){He(r,r.return,b)}else{var u=qs(r.type,i.memoizedProps);i=i.memoizedState;try{e.componentDidUpdate(u,i,e.__reactInternalSnapshotBeforeUpdate)}catch(b){He(r,r.return,b)}}l&64&&Kv(r),l&512&&Tl(r,r.return);break;case 3:if(ga(e,r),l&64&&(e=r.updateQueue,e!==null)){if(i=null,r.child!==null)switch(r.child.tag){case 27:case 5:i=r.child.stateNode;break;case 1:i=r.child.stateNode}try{Gg(e,i)}catch(b){He(r,r.return,b)}}break;case 27:i===null&&l&4&&e_(r);case 26:case 5:ga(e,r),i===null&&l&4&&$v(r),l&512&&Tl(r,r.return);break;case 12:ga(e,r);break;case 31:ga(e,r),l&4&&r_(e,r);break;case 13:ga(e,r),l&4&&o_(e,r),l&64&&(e=r.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(r=GM.bind(null,r),o1(e,r))));break;case 22:if(l=r.memoizedState!==null||pa,!l){i=i!==null&&i.memoizedState!==null||gn,u=pa;var h=gn;pa=l,(gn=i)&&!h?va(e,r,(r.subtreeFlags&8772)!==0):ga(e,r),pa=u,gn=h}break;case 30:break;default:ga(e,r)}}function a_(e){var i=e.alternate;i!==null&&(e.alternate=null,a_(i)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(i=e.stateNode,i!==null&&w(i)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var en=null,Zn=!1;function ma(e,i,r){for(r=r.child;r!==null;)s_(e,i,r),r=r.sibling}function s_(e,i,r){if(qt&&typeof qt.onCommitFiberUnmount=="function")try{qt.onCommitFiberUnmount(Zt,r)}catch{}switch(r.tag){case 26:gn||Wi(r,i),ma(e,i,r),r.memoizedState?r.memoizedState.count--:r.stateNode&&(r=r.stateNode,r.parentNode.removeChild(r));break;case 27:gn||Wi(r,i);var l=en,u=Zn;is(r.type)&&(en=r.stateNode,Zn=!1),ma(e,i,r),Ol(r.stateNode),en=l,Zn=u;break;case 5:gn||Wi(r,i);case 6:if(l=en,u=Zn,en=null,ma(e,i,r),en=l,Zn=u,en!==null)if(Zn)try{(en.nodeType===9?en.body:en.nodeName==="HTML"?en.ownerDocument.body:en).removeChild(r.stateNode)}catch(h){He(r,i,h)}else try{en.removeChild(r.stateNode)}catch(h){He(r,i,h)}break;case 18:en!==null&&(Zn?(e=en,K_(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,r.stateNode),eo(e)):K_(en,r.stateNode));break;case 4:l=en,u=Zn,en=r.stateNode.containerInfo,Zn=!0,ma(e,i,r),en=l,Zn=u;break;case 0:case 11:case 14:case 15:Za(2,r,i),gn||Za(4,r,i),ma(e,i,r);break;case 1:gn||(Wi(r,i),l=r.stateNode,typeof l.componentWillUnmount=="function"&&Jv(r,i,l)),ma(e,i,r);break;case 21:ma(e,i,r);break;case 22:gn=(l=gn)||r.memoizedState!==null,ma(e,i,r),gn=l;break;default:ma(e,i,r)}}function r_(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{eo(e)}catch(r){He(i,i.return,r)}}}function o_(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{eo(e)}catch(r){He(i,i.return,r)}}function LM(e){switch(e.tag){case 31:case 13:case 19:var i=e.stateNode;return i===null&&(i=e.stateNode=new n_),i;case 22:return e=e.stateNode,i=e._retryCache,i===null&&(i=e._retryCache=new n_),i;default:throw Error(s(435,e.tag))}}function iu(e,i){var r=LM(e);i.forEach(function(l){if(!r.has(l)){r.add(l);var u=VM.bind(null,e,l);l.then(u,u)}})}function Kn(e,i){var r=i.deletions;if(r!==null)for(var l=0;l<r.length;l++){var u=r[l],h=e,b=i,A=b;t:for(;A!==null;){switch(A.tag){case 27:if(is(A.type)){en=A.stateNode,Zn=!1;break t}break;case 5:en=A.stateNode,Zn=!1;break t;case 3:case 4:en=A.stateNode.containerInfo,Zn=!0;break t}A=A.return}if(en===null)throw Error(s(160));s_(h,b,u),en=null,Zn=!1,h=u.alternate,h!==null&&(h.return=null),u.return=null}if(i.subtreeFlags&13886)for(i=i.child;i!==null;)l_(i,e),i=i.sibling}var Ui=null;function l_(e,i){var r=e.alternate,l=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Kn(i,e),Jn(e),l&4&&(Za(3,e,e.return),bl(3,e),Za(5,e,e.return));break;case 1:Kn(i,e),Jn(e),l&512&&(gn||r===null||Wi(r,r.return)),l&64&&pa&&(e=e.updateQueue,e!==null&&(l=e.callbacks,l!==null&&(r=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=r===null?l:r.concat(l))));break;case 26:var u=Ui;if(Kn(i,e),Jn(e),l&512&&(gn||r===null||Wi(r,r.return)),l&4){var h=r!==null?r.memoizedState:null;if(l=e.memoizedState,r===null)if(l===null)if(e.stateNode===null){t:{l=e.type,r=e.memoizedProps,u=u.ownerDocument||u;e:switch(l){case"title":h=u.getElementsByTagName("title")[0],(!h||h[Ds]||h[sn]||h.namespaceURI==="http://www.w3.org/2000/svg"||h.hasAttribute("itemprop"))&&(h=u.createElement(l),u.head.insertBefore(h,u.querySelector("head > title"))),Ln(h,l,r),h[sn]=e,xt(h),l=h;break t;case"link":var b=l0("link","href",u).get(l+(r.href||""));if(b){for(var A=0;A<b.length;A++)if(h=b[A],h.getAttribute("href")===(r.href==null||r.href===""?null:r.href)&&h.getAttribute("rel")===(r.rel==null?null:r.rel)&&h.getAttribute("title")===(r.title==null?null:r.title)&&h.getAttribute("crossorigin")===(r.crossOrigin==null?null:r.crossOrigin)){b.splice(A,1);break e}}h=u.createElement(l),Ln(h,l,r),u.head.appendChild(h);break;case"meta":if(b=l0("meta","content",u).get(l+(r.content||""))){for(A=0;A<b.length;A++)if(h=b[A],h.getAttribute("content")===(r.content==null?null:""+r.content)&&h.getAttribute("name")===(r.name==null?null:r.name)&&h.getAttribute("property")===(r.property==null?null:r.property)&&h.getAttribute("http-equiv")===(r.httpEquiv==null?null:r.httpEquiv)&&h.getAttribute("charset")===(r.charSet==null?null:r.charSet)){b.splice(A,1);break e}}h=u.createElement(l),Ln(h,l,r),u.head.appendChild(h);break;default:throw Error(s(468,l))}h[sn]=e,xt(h),l=h}e.stateNode=l}else c0(u,e.type,e.stateNode);else e.stateNode=o0(u,l,e.memoizedProps);else h!==l?(h===null?r.stateNode!==null&&(r=r.stateNode,r.parentNode.removeChild(r)):h.count--,l===null?c0(u,e.type,e.stateNode):o0(u,l,e.memoizedProps)):l===null&&e.stateNode!==null&&kd(e,e.memoizedProps,r.memoizedProps)}break;case 27:Kn(i,e),Jn(e),l&512&&(gn||r===null||Wi(r,r.return)),r!==null&&l&4&&kd(e,e.memoizedProps,r.memoizedProps);break;case 5:if(Kn(i,e),Jn(e),l&512&&(gn||r===null||Wi(r,r.return)),e.flags&32){u=e.stateNode;try{br(u,"")}catch(Gt){He(e,e.return,Gt)}}l&4&&e.stateNode!=null&&(u=e.memoizedProps,kd(e,u,r!==null?r.memoizedProps:u)),l&1024&&(Wd=!0);break;case 6:if(Kn(i,e),Jn(e),l&4){if(e.stateNode===null)throw Error(s(162));l=e.memoizedProps,r=e.stateNode;try{r.nodeValue=l}catch(Gt){He(e,e.return,Gt)}}break;case 3:if(yu=null,u=Ui,Ui=vu(i.containerInfo),Kn(i,e),Ui=u,Jn(e),l&4&&r!==null&&r.memoizedState.isDehydrated)try{eo(i.containerInfo)}catch(Gt){He(e,e.return,Gt)}Wd&&(Wd=!1,c_(e));break;case 4:l=Ui,Ui=vu(e.stateNode.containerInfo),Kn(i,e),Jn(e),Ui=l;break;case 12:Kn(i,e),Jn(e);break;case 31:Kn(i,e),Jn(e),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,iu(e,l)));break;case 13:Kn(i,e),Jn(e),e.child.flags&8192&&e.memoizedState!==null!=(r!==null&&r.memoizedState!==null)&&(su=pt()),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,iu(e,l)));break;case 22:u=e.memoizedState!==null;var F=r!==null&&r.memoizedState!==null,et=pa,ht=gn;if(pa=et||u,gn=ht||F,Kn(i,e),gn=ht,pa=et,Jn(e),l&8192)t:for(i=e.stateNode,i._visibility=u?i._visibility&-2:i._visibility|1,u&&(r===null||F||pa||gn||Ws(e)),r=null,i=e;;){if(i.tag===5||i.tag===26){if(r===null){F=r=i;try{if(h=F.stateNode,u)b=h.style,typeof b.setProperty=="function"?b.setProperty("display","none","important"):b.display="none";else{A=F.stateNode;var _t=F.memoizedProps.style,it=_t!=null&&_t.hasOwnProperty("display")?_t.display:null;A.style.display=it==null||typeof it=="boolean"?"":(""+it).trim()}}catch(Gt){He(F,F.return,Gt)}}}else if(i.tag===6){if(r===null){F=i;try{F.stateNode.nodeValue=u?"":F.memoizedProps}catch(Gt){He(F,F.return,Gt)}}}else if(i.tag===18){if(r===null){F=i;try{var lt=F.stateNode;u?J_(lt,!0):J_(F.stateNode,!1)}catch(Gt){He(F,F.return,Gt)}}}else if((i.tag!==22&&i.tag!==23||i.memoizedState===null||i===e)&&i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break t;for(;i.sibling===null;){if(i.return===null||i.return===e)break t;r===i&&(r=null),i=i.return}r===i&&(r=null),i.sibling.return=i.return,i=i.sibling}l&4&&(l=e.updateQueue,l!==null&&(r=l.retryQueue,r!==null&&(l.retryQueue=null,iu(e,r))));break;case 19:Kn(i,e),Jn(e),l&4&&(l=e.updateQueue,l!==null&&(e.updateQueue=null,iu(e,l)));break;case 30:break;case 21:break;default:Kn(i,e),Jn(e)}}function Jn(e){var i=e.flags;if(i&2){try{for(var r,l=e.return;l!==null;){if(t_(l)){r=l;break}l=l.return}if(r==null)throw Error(s(160));switch(r.tag){case 27:var u=r.stateNode,h=Xd(e);nu(e,h,u);break;case 5:var b=r.stateNode;r.flags&32&&(br(b,""),r.flags&=-33);var A=Xd(e);nu(e,A,b);break;case 3:case 4:var F=r.stateNode.containerInfo,et=Xd(e);qd(e,et,F);break;default:throw Error(s(161))}}catch(ht){He(e,e.return,ht)}e.flags&=-3}i&4096&&(e.flags&=-4097)}function c_(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var i=e;c_(i),i.tag===5&&i.flags&1024&&i.stateNode.reset(),e=e.sibling}}function ga(e,i){if(i.subtreeFlags&8772)for(i=i.child;i!==null;)i_(e,i.alternate,i),i=i.sibling}function Ws(e){for(e=e.child;e!==null;){var i=e;switch(i.tag){case 0:case 11:case 14:case 15:Za(4,i,i.return),Ws(i);break;case 1:Wi(i,i.return);var r=i.stateNode;typeof r.componentWillUnmount=="function"&&Jv(i,i.return,r),Ws(i);break;case 27:Ol(i.stateNode);case 26:case 5:Wi(i,i.return),Ws(i);break;case 22:i.memoizedState===null&&Ws(i);break;case 30:Ws(i);break;default:Ws(i)}e=e.sibling}}function va(e,i,r){for(r=r&&(i.subtreeFlags&8772)!==0,i=i.child;i!==null;){var l=i.alternate,u=e,h=i,b=h.flags;switch(h.tag){case 0:case 11:case 15:va(u,h,r),bl(4,h);break;case 1:if(va(u,h,r),l=h,u=l.stateNode,typeof u.componentDidMount=="function")try{u.componentDidMount()}catch(et){He(l,l.return,et)}if(l=h,u=l.updateQueue,u!==null){var A=l.stateNode;try{var F=u.shared.hiddenCallbacks;if(F!==null)for(u.shared.hiddenCallbacks=null,u=0;u<F.length;u++)Hg(F[u],A)}catch(et){He(l,l.return,et)}}r&&b&64&&Kv(h),Tl(h,h.return);break;case 27:e_(h);case 26:case 5:va(u,h,r),r&&l===null&&b&4&&$v(h),Tl(h,h.return);break;case 12:va(u,h,r);break;case 31:va(u,h,r),r&&b&4&&r_(u,h);break;case 13:va(u,h,r),r&&b&4&&o_(u,h);break;case 22:h.memoizedState===null&&va(u,h,r),Tl(h,h.return);break;case 30:break;default:va(u,h,r)}i=i.sibling}}function Yd(e,i){var r=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),e=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(e=i.memoizedState.cachePool.pool),e!==r&&(e!=null&&e.refCount++,r!=null&&fl(r))}function Qd(e,i){e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&fl(e))}function Li(e,i,r,l){if(i.subtreeFlags&10256)for(i=i.child;i!==null;)u_(e,i,r,l),i=i.sibling}function u_(e,i,r,l){var u=i.flags;switch(i.tag){case 0:case 11:case 15:Li(e,i,r,l),u&2048&&bl(9,i);break;case 1:Li(e,i,r,l);break;case 3:Li(e,i,r,l),u&2048&&(e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&fl(e)));break;case 12:if(u&2048){Li(e,i,r,l),e=i.stateNode;try{var h=i.memoizedProps,b=h.id,A=h.onPostCommit;typeof A=="function"&&A(b,i.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(F){He(i,i.return,F)}}else Li(e,i,r,l);break;case 31:Li(e,i,r,l);break;case 13:Li(e,i,r,l);break;case 23:break;case 22:h=i.stateNode,b=i.alternate,i.memoizedState!==null?h._visibility&2?Li(e,i,r,l):Al(e,i):h._visibility&2?Li(e,i,r,l):(h._visibility|=2,kr(e,i,r,l,(i.subtreeFlags&10256)!==0||!1)),u&2048&&Yd(b,i);break;case 24:Li(e,i,r,l),u&2048&&Qd(i.alternate,i);break;default:Li(e,i,r,l)}}function kr(e,i,r,l,u){for(u=u&&((i.subtreeFlags&10256)!==0||!1),i=i.child;i!==null;){var h=e,b=i,A=r,F=l,et=b.flags;switch(b.tag){case 0:case 11:case 15:kr(h,b,A,F,u),bl(8,b);break;case 23:break;case 22:var ht=b.stateNode;b.memoizedState!==null?ht._visibility&2?kr(h,b,A,F,u):Al(h,b):(ht._visibility|=2,kr(h,b,A,F,u)),u&&et&2048&&Yd(b.alternate,b);break;case 24:kr(h,b,A,F,u),u&&et&2048&&Qd(b.alternate,b);break;default:kr(h,b,A,F,u)}i=i.sibling}}function Al(e,i){if(i.subtreeFlags&10256)for(i=i.child;i!==null;){var r=e,l=i,u=l.flags;switch(l.tag){case 22:Al(r,l),u&2048&&Yd(l.alternate,l);break;case 24:Al(r,l),u&2048&&Qd(l.alternate,l);break;default:Al(r,l)}i=i.sibling}}var Cl=8192;function Xr(e,i,r){if(e.subtreeFlags&Cl)for(e=e.child;e!==null;)f_(e,i,r),e=e.sibling}function f_(e,i,r){switch(e.tag){case 26:Xr(e,i,r),e.flags&Cl&&e.memoizedState!==null&&y1(r,Ui,e.memoizedState,e.memoizedProps);break;case 5:Xr(e,i,r);break;case 3:case 4:var l=Ui;Ui=vu(e.stateNode.containerInfo),Xr(e,i,r),Ui=l;break;case 22:e.memoizedState===null&&(l=e.alternate,l!==null&&l.memoizedState!==null?(l=Cl,Cl=16777216,Xr(e,i,r),Cl=l):Xr(e,i,r));break;default:Xr(e,i,r)}}function d_(e){var i=e.alternate;if(i!==null&&(e=i.child,e!==null)){i.child=null;do i=e.sibling,e.sibling=null,e=i;while(e!==null)}}function Rl(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var l=i[r];bn=l,p_(l,e)}d_(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)h_(e),e=e.sibling}function h_(e){switch(e.tag){case 0:case 11:case 15:Rl(e),e.flags&2048&&Za(9,e,e.return);break;case 3:Rl(e);break;case 12:Rl(e);break;case 22:var i=e.stateNode;e.memoizedState!==null&&i._visibility&2&&(e.return===null||e.return.tag!==13)?(i._visibility&=-3,au(e)):Rl(e);break;default:Rl(e)}}function au(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var l=i[r];bn=l,p_(l,e)}d_(e)}for(e=e.child;e!==null;){switch(i=e,i.tag){case 0:case 11:case 15:Za(8,i,i.return),au(i);break;case 22:r=i.stateNode,r._visibility&2&&(r._visibility&=-3,au(i));break;default:au(i)}e=e.sibling}}function p_(e,i){for(;bn!==null;){var r=bn;switch(r.tag){case 0:case 11:case 15:Za(8,r,i);break;case 23:case 22:if(r.memoizedState!==null&&r.memoizedState.cachePool!==null){var l=r.memoizedState.cachePool.pool;l!=null&&l.refCount++}break;case 24:fl(r.memoizedState.cache)}if(l=r.child,l!==null)l.return=r,bn=l;else t:for(r=e;bn!==null;){l=bn;var u=l.sibling,h=l.return;if(a_(l),l===r){bn=null;break t}if(u!==null){u.return=h,bn=u;break t}bn=h}}}var OM={getCacheForType:function(e){var i=Dn(hn),r=i.data.get(e);return r===void 0&&(r=e(),i.data.set(e,r)),r},cacheSignal:function(){return Dn(hn).controller.signal}},PM=typeof WeakMap=="function"?WeakMap:Map,ze=0,Qe=null,ye=null,be=0,Fe=0,ui=null,Ka=!1,qr=!1,Zd=!1,_a=0,on=0,Ja=0,Ys=0,Kd=0,fi=0,Wr=0,wl=null,$n=null,Jd=!1,su=0,m_=0,ru=1/0,ou=null,$a=null,xn=0,ts=null,Yr=null,ya=0,$d=0,th=null,g_=null,Nl=0,eh=null;function di(){return(ze&2)!==0&&be!==0?be&-be:B.T!==null?oh():Jo()}function v_(){if(fi===0)if((be&536870912)===0||Ce){var e=dt;dt<<=1,(dt&3932160)===0&&(dt=262144),fi=e}else fi=536870912;return e=li.current,e!==null&&(e.flags|=32),fi}function ti(e,i,r){(e===Qe&&(Fe===2||Fe===9)||e.cancelPendingCommit!==null)&&(Qr(e,0),es(e,be,fi,!1)),Rn(e,r),((ze&2)===0||e!==Qe)&&(e===Qe&&((ze&2)===0&&(Ys|=r),on===4&&es(e,be,fi,!1)),Yi(e))}function __(e,i,r){if((ze&6)!==0)throw Error(s(327));var l=!r&&(i&127)===0&&(i&e.expiredLanes)===0||ie(e,i),u=l?BM(e,i):ih(e,i,!0),h=l;do{if(u===0){qr&&!l&&es(e,i,0,!1);break}else{if(r=e.current.alternate,h&&!zM(r)){u=ih(e,i,!1),h=!1;continue}if(u===2){if(h=i,e.errorRecoveryDisabledLanes&h)var b=0;else b=e.pendingLanes&-536870913,b=b!==0?b:b&536870912?536870912:0;if(b!==0){i=b;t:{var A=e;u=wl;var F=A.current.memoizedState.isDehydrated;if(F&&(Qr(A,b).flags|=256),b=ih(A,b,!1),b!==2){if(Zd&&!F){A.errorRecoveryDisabledLanes|=h,Ys|=h,u=4;break t}h=$n,$n=u,h!==null&&($n===null?$n=h:$n.push.apply($n,h))}u=b}if(h=!1,u!==2)continue}}if(u===1){Qr(e,0),es(e,i,0,!0);break}t:{switch(l=e,h=u,h){case 0:case 1:throw Error(s(345));case 4:if((i&4194048)!==i)break;case 6:es(l,i,fi,!Ka);break t;case 2:$n=null;break;case 3:case 5:break;default:throw Error(s(329))}if((i&62914560)===i&&(u=su+300-pt(),10<u)){if(es(l,i,fi,!Ka),Dt(l,0,!0)!==0)break t;ya=i,l.timeoutHandle=Q_(y_.bind(null,l,r,$n,ou,Jd,i,fi,Ys,Wr,Ka,h,"Throttled",-0,0),u);break t}y_(l,r,$n,ou,Jd,i,fi,Ys,Wr,Ka,h,null,-0,0)}}break}while(!0);Yi(e)}function y_(e,i,r,l,u,h,b,A,F,et,ht,_t,it,lt){if(e.timeoutHandle=-1,_t=i.subtreeFlags,_t&8192||(_t&16785408)===16785408){_t={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:aa},f_(i,h,_t);var Gt=(h&62914560)===h?su-pt():(h&4194048)===h?m_-pt():0;if(Gt=x1(_t,Gt),Gt!==null){ya=h,e.cancelPendingCommit=Gt(C_.bind(null,e,i,h,r,l,u,b,A,F,ht,_t,null,it,lt)),es(e,h,b,!et);return}}C_(e,i,h,r,l,u,b,A,F)}function zM(e){for(var i=e;;){var r=i.tag;if((r===0||r===11||r===15)&&i.flags&16384&&(r=i.updateQueue,r!==null&&(r=r.stores,r!==null)))for(var l=0;l<r.length;l++){var u=r[l],h=u.getSnapshot;u=u.value;try{if(!ri(h(),u))return!1}catch{return!1}}if(r=i.child,i.subtreeFlags&16384&&r!==null)r.return=i,i=r;else{if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return!0;i=i.return}i.sibling.return=i.return,i=i.sibling}}return!0}function es(e,i,r,l){i&=~Kd,i&=~Ys,e.suspendedLanes|=i,e.pingedLanes&=~i,l&&(e.warmLanes|=i),l=e.expirationTimes;for(var u=i;0<u;){var h=31-ne(u),b=1<<h;l[h]=-1,u&=~b}r!==0&&Zo(e,r,i)}function lu(){return(ze&6)===0?(Dl(0),!1):!0}function nh(){if(ye!==null){if(Fe===0)var e=ye.return;else e=ye,la=Fs=null,_d(e),Fr=null,hl=0,e=ye;for(;e!==null;)Zv(e.alternate,e),e=e.return;ye=null}}function Qr(e,i){var r=e.timeoutHandle;r!==-1&&(e.timeoutHandle=-1,n1(r)),r=e.cancelPendingCommit,r!==null&&(e.cancelPendingCommit=null,r()),ya=0,nh(),Qe=e,ye=r=ra(e.current,null),be=i,Fe=0,ui=null,Ka=!1,qr=ie(e,i),Zd=!1,Wr=fi=Kd=Ys=Ja=on=0,$n=wl=null,Jd=!1,(i&8)!==0&&(i|=i&32);var l=e.entangledLanes;if(l!==0)for(e=e.entanglements,l&=i;0<l;){var u=31-ne(l),h=1<<u;i|=e[u],l&=~h}return _a=i,wc(),r}function x_(e,i){ue=null,B.H=Sl,i===Br||i===Ic?(i=zg(),Fe=3):i===rd?(i=zg(),Fe=4):Fe=i===Od?8:i!==null&&typeof i=="object"&&typeof i.then=="function"?6:1,ui=i,ye===null&&(on=1,Kc(e,xi(i,e.current)))}function S_(){var e=li.current;return e===null?!0:(be&4194048)===be?bi===null:(be&62914560)===be||(be&536870912)!==0?e===bi:!1}function M_(){var e=B.H;return B.H=Sl,e===null?Sl:e}function E_(){var e=B.A;return B.A=OM,e}function cu(){on=4,Ka||(be&4194048)!==be&&li.current!==null||(qr=!0),(Ja&134217727)===0&&(Ys&134217727)===0||Qe===null||es(Qe,be,fi,!1)}function ih(e,i,r){var l=ze;ze|=2;var u=M_(),h=E_();(Qe!==e||be!==i)&&(ou=null,Qr(e,i)),i=!1;var b=on;t:do try{if(Fe!==0&&ye!==null){var A=ye,F=ui;switch(Fe){case 8:nh(),b=6;break t;case 3:case 2:case 9:case 6:li.current===null&&(i=!0);var et=Fe;if(Fe=0,ui=null,Zr(e,A,F,et),r&&qr){b=0;break t}break;default:et=Fe,Fe=0,ui=null,Zr(e,A,F,et)}}IM(),b=on;break}catch(ht){x_(e,ht)}while(!0);return i&&e.shellSuspendCounter++,la=Fs=null,ze=l,B.H=u,B.A=h,ye===null&&(Qe=null,be=0,wc()),b}function IM(){for(;ye!==null;)b_(ye)}function BM(e,i){var r=ze;ze|=2;var l=M_(),u=E_();Qe!==e||be!==i?(ou=null,ru=pt()+500,Qr(e,i)):qr=ie(e,i);t:do try{if(Fe!==0&&ye!==null){i=ye;var h=ui;e:switch(Fe){case 1:Fe=0,ui=null,Zr(e,i,h,1);break;case 2:case 9:if(Og(h)){Fe=0,ui=null,T_(i);break}i=function(){Fe!==2&&Fe!==9||Qe!==e||(Fe=7),Yi(e)},h.then(i,i);break t;case 3:Fe=7;break t;case 4:Fe=5;break t;case 7:Og(h)?(Fe=0,ui=null,T_(i)):(Fe=0,ui=null,Zr(e,i,h,7));break;case 5:var b=null;switch(ye.tag){case 26:b=ye.memoizedState;case 5:case 27:var A=ye;if(b?u0(b):A.stateNode.complete){Fe=0,ui=null;var F=A.sibling;if(F!==null)ye=F;else{var et=A.return;et!==null?(ye=et,uu(et)):ye=null}break e}}Fe=0,ui=null,Zr(e,i,h,5);break;case 6:Fe=0,ui=null,Zr(e,i,h,6);break;case 8:nh(),on=6;break t;default:throw Error(s(462))}}FM();break}catch(ht){x_(e,ht)}while(!0);return la=Fs=null,B.H=l,B.A=u,ze=r,ye!==null?0:(Qe=null,be=0,wc(),on)}function FM(){for(;ye!==null&&!R();)b_(ye)}function b_(e){var i=Yv(e.alternate,e,_a);e.memoizedProps=e.pendingProps,i===null?uu(e):ye=i}function T_(e){var i=e,r=i.alternate;switch(i.tag){case 15:case 0:i=Vv(r,i,i.pendingProps,i.type,void 0,be);break;case 11:i=Vv(r,i,i.pendingProps,i.type.render,i.ref,be);break;case 5:_d(i);default:Zv(r,i),i=ye=Eg(i,_a),i=Yv(r,i,_a)}e.memoizedProps=e.pendingProps,i===null?uu(e):ye=i}function Zr(e,i,r,l){la=Fs=null,_d(i),Fr=null,hl=0;var u=i.return;try{if(CM(e,u,i,r,be)){on=1,Kc(e,xi(r,e.current)),ye=null;return}}catch(h){if(u!==null)throw ye=u,h;on=1,Kc(e,xi(r,e.current)),ye=null;return}i.flags&32768?(Ce||l===1?e=!0:qr||(be&536870912)!==0?e=!1:(Ka=e=!0,(l===2||l===9||l===3||l===6)&&(l=li.current,l!==null&&l.tag===13&&(l.flags|=16384))),A_(i,e)):uu(i)}function uu(e){var i=e;do{if((i.flags&32768)!==0){A_(i,Ka);return}e=i.return;var r=NM(i.alternate,i,_a);if(r!==null){ye=r;return}if(i=i.sibling,i!==null){ye=i;return}ye=i=e}while(i!==null);on===0&&(on=5)}function A_(e,i){do{var r=DM(e.alternate,e);if(r!==null){r.flags&=32767,ye=r;return}if(r=e.return,r!==null&&(r.flags|=32768,r.subtreeFlags=0,r.deletions=null),!i&&(e=e.sibling,e!==null)){ye=e;return}ye=e=r}while(e!==null);on=6,ye=null}function C_(e,i,r,l,u,h,b,A,F){e.cancelPendingCommit=null;do fu();while(xn!==0);if((ze&6)!==0)throw Error(s(327));if(i!==null){if(i===e.current)throw Error(s(177));if(h=i.lanes|i.childLanes,h|=Xf,wi(e,r,h,b,A,F),e===Qe&&(ye=Qe=null,be=0),Yr=i,ts=e,ya=r,$d=h,th=u,g_=l,(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,jM(Nt,function(){return U_(),null})):(e.callbackNode=null,e.callbackPriority=0),l=(i.flags&13878)!==0,(i.subtreeFlags&13878)!==0||l){l=B.T,B.T=null,u=Z.p,Z.p=2,b=ze,ze|=4;try{UM(e,i,r)}finally{ze=b,Z.p=u,B.T=l}}xn=1,R_(),w_(),N_()}}function R_(){if(xn===1){xn=0;var e=ts,i=Yr,r=(i.flags&13878)!==0;if((i.subtreeFlags&13878)!==0||r){r=B.T,B.T=null;var l=Z.p;Z.p=2;var u=ze;ze|=4;try{l_(i,e);var h=mh,b=pg(e.containerInfo),A=h.focusedElem,F=h.selectionRange;if(b!==A&&A&&A.ownerDocument&&hg(A.ownerDocument.documentElement,A)){if(F!==null&&Hf(A)){var et=F.start,ht=F.end;if(ht===void 0&&(ht=et),"selectionStart"in A)A.selectionStart=et,A.selectionEnd=Math.min(ht,A.value.length);else{var _t=A.ownerDocument||document,it=_t&&_t.defaultView||window;if(it.getSelection){var lt=it.getSelection(),Gt=A.textContent.length,ee=Math.min(F.start,Gt),Xe=F.end===void 0?ee:Math.min(F.end,Gt);!lt.extend&&ee>Xe&&(b=Xe,Xe=ee,ee=b);var J=dg(A,ee),k=dg(A,Xe);if(J&&k&&(lt.rangeCount!==1||lt.anchorNode!==J.node||lt.anchorOffset!==J.offset||lt.focusNode!==k.node||lt.focusOffset!==k.offset)){var tt=_t.createRange();tt.setStart(J.node,J.offset),lt.removeAllRanges(),ee>Xe?(lt.addRange(tt),lt.extend(k.node,k.offset)):(tt.setEnd(k.node,k.offset),lt.addRange(tt))}}}}for(_t=[],lt=A;lt=lt.parentNode;)lt.nodeType===1&&_t.push({element:lt,left:lt.scrollLeft,top:lt.scrollTop});for(typeof A.focus=="function"&&A.focus(),A=0;A<_t.length;A++){var gt=_t[A];gt.element.scrollLeft=gt.left,gt.element.scrollTop=gt.top}}Eu=!!ph,mh=ph=null}finally{ze=u,Z.p=l,B.T=r}}e.current=i,xn=2}}function w_(){if(xn===2){xn=0;var e=ts,i=Yr,r=(i.flags&8772)!==0;if((i.subtreeFlags&8772)!==0||r){r=B.T,B.T=null;var l=Z.p;Z.p=2;var u=ze;ze|=4;try{i_(e,i.alternate,i)}finally{ze=u,Z.p=l,B.T=r}}xn=3}}function N_(){if(xn===4||xn===3){xn=0,at();var e=ts,i=Yr,r=ya,l=g_;(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?xn=5:(xn=0,Yr=ts=null,D_(e,e.pendingLanes));var u=e.pendingLanes;if(u===0&&($a=null),Mr(r),i=i.stateNode,qt&&typeof qt.onCommitFiberRoot=="function")try{qt.onCommitFiberRoot(Zt,i,void 0,(i.current.flags&128)===128)}catch{}if(l!==null){i=B.T,u=Z.p,Z.p=2,B.T=null;try{for(var h=e.onRecoverableError,b=0;b<l.length;b++){var A=l[b];h(A.value,{componentStack:A.stack})}}finally{B.T=i,Z.p=u}}(ya&3)!==0&&fu(),Yi(e),u=e.pendingLanes,(r&261930)!==0&&(u&42)!==0?e===eh?Nl++:(Nl=0,eh=e):Nl=0,Dl(0)}}function D_(e,i){(e.pooledCacheLanes&=i)===0&&(i=e.pooledCache,i!=null&&(e.pooledCache=null,fl(i)))}function fu(){return R_(),w_(),N_(),U_()}function U_(){if(xn!==5)return!1;var e=ts,i=$d;$d=0;var r=Mr(ya),l=B.T,u=Z.p;try{Z.p=32>r?32:r,B.T=null,r=th,th=null;var h=ts,b=ya;if(xn=0,Yr=ts=null,ya=0,(ze&6)!==0)throw Error(s(331));var A=ze;if(ze|=4,h_(h.current),u_(h,h.current,b,r),ze=A,Dl(0,!1),qt&&typeof qt.onPostCommitFiberRoot=="function")try{qt.onPostCommitFiberRoot(Zt,h)}catch{}return!0}finally{Z.p=u,B.T=l,D_(e,i)}}function L_(e,i,r){i=xi(r,i),i=Ld(e.stateNode,i,2),e=Wa(e,i,2),e!==null&&(Rn(e,2),Yi(e))}function He(e,i,r){if(e.tag===3)L_(e,e,r);else for(;i!==null;){if(i.tag===3){L_(i,e,r);break}else if(i.tag===1){var l=i.stateNode;if(typeof i.type.getDerivedStateFromError=="function"||typeof l.componentDidCatch=="function"&&($a===null||!$a.has(l))){e=xi(r,e),r=Ov(2),l=Wa(i,r,2),l!==null&&(Pv(r,l,i,e),Rn(l,2),Yi(l));break}}i=i.return}}function ah(e,i,r){var l=e.pingCache;if(l===null){l=e.pingCache=new PM;var u=new Set;l.set(i,u)}else u=l.get(i),u===void 0&&(u=new Set,l.set(i,u));u.has(r)||(Zd=!0,u.add(r),e=HM.bind(null,e,i,r),i.then(e,e))}function HM(e,i,r){var l=e.pingCache;l!==null&&l.delete(i),e.pingedLanes|=e.suspendedLanes&r,e.warmLanes&=~r,Qe===e&&(be&r)===r&&(on===4||on===3&&(be&62914560)===be&&300>pt()-su?(ze&2)===0&&Qr(e,0):Kd|=r,Wr===be&&(Wr=0)),Yi(e)}function O_(e,i){i===0&&(i=_n()),e=zs(e,i),e!==null&&(Rn(e,i),Yi(e))}function GM(e){var i=e.memoizedState,r=0;i!==null&&(r=i.retryLane),O_(e,r)}function VM(e,i){var r=0;switch(e.tag){case 31:case 13:var l=e.stateNode,u=e.memoizedState;u!==null&&(r=u.retryLane);break;case 19:l=e.stateNode;break;case 22:l=e.stateNode._retryCache;break;default:throw Error(s(314))}l!==null&&l.delete(i),O_(e,r)}function jM(e,i){return Yt(e,i)}var du=null,Kr=null,sh=!1,hu=!1,rh=!1,ns=0;function Yi(e){e!==Kr&&e.next===null&&(Kr===null?du=Kr=e:Kr=Kr.next=e),hu=!0,sh||(sh=!0,XM())}function Dl(e,i){if(!rh&&hu){rh=!0;do for(var r=!1,l=du;l!==null;){if(e!==0){var u=l.pendingLanes;if(u===0)var h=0;else{var b=l.suspendedLanes,A=l.pingedLanes;h=(1<<31-ne(42|e)+1)-1,h&=u&~(b&~A),h=h&201326741?h&201326741|1:h?h|2:0}h!==0&&(r=!0,B_(l,h))}else h=be,h=Dt(l,l===Qe?h:0,l.cancelPendingCommit!==null||l.timeoutHandle!==-1),(h&3)===0||ie(l,h)||(r=!0,B_(l,h));l=l.next}while(r);rh=!1}}function kM(){P_()}function P_(){hu=sh=!1;var e=0;ns!==0&&e1()&&(e=ns);for(var i=pt(),r=null,l=du;l!==null;){var u=l.next,h=z_(l,i);h===0?(l.next=null,r===null?du=u:r.next=u,u===null&&(Kr=r)):(r=l,(e!==0||(h&3)!==0)&&(hu=!0)),l=u}xn!==0&&xn!==5||Dl(e),ns!==0&&(ns=0)}function z_(e,i){for(var r=e.suspendedLanes,l=e.pingedLanes,u=e.expirationTimes,h=e.pendingLanes&-62914561;0<h;){var b=31-ne(h),A=1<<b,F=u[b];F===-1?((A&r)===0||(A&l)!==0)&&(u[b]=tn(A,i)):F<=i&&(e.expiredLanes|=A),h&=~A}if(i=Qe,r=be,r=Dt(e,e===i?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),l=e.callbackNode,r===0||e===i&&(Fe===2||Fe===9)||e.cancelPendingCommit!==null)return l!==null&&l!==null&&O(l),e.callbackNode=null,e.callbackPriority=0;if((r&3)===0||ie(e,r)){if(i=r&-r,i===e.callbackPriority)return i;switch(l!==null&&O(l),Mr(r)){case 2:case 8:r=Xt;break;case 32:r=Nt;break;case 268435456:r=Me;break;default:r=Nt}return l=I_.bind(null,e),r=Yt(r,l),e.callbackPriority=i,e.callbackNode=r,i}return l!==null&&l!==null&&O(l),e.callbackPriority=2,e.callbackNode=null,2}function I_(e,i){if(xn!==0&&xn!==5)return e.callbackNode=null,e.callbackPriority=0,null;var r=e.callbackNode;if(fu()&&e.callbackNode!==r)return null;var l=be;return l=Dt(e,e===Qe?l:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),l===0?null:(__(e,l,i),z_(e,pt()),e.callbackNode!=null&&e.callbackNode===r?I_.bind(null,e):null)}function B_(e,i){if(fu())return null;__(e,i,!0)}function XM(){i1(function(){(ze&6)!==0?Yt(vt,kM):P_()})}function oh(){if(ns===0){var e=zr;e===0&&(e=Rt,Rt<<=1,(Rt&261888)===0&&(Rt=256)),ns=e}return ns}function F_(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:Sc(""+e)}function H_(e,i){var r=i.ownerDocument.createElement("input");return r.name=i.name,r.value=i.value,e.id&&r.setAttribute("form",e.id),i.parentNode.insertBefore(r,i),e=new FormData(e),r.parentNode.removeChild(r),e}function qM(e,i,r,l,u){if(i==="submit"&&r&&r.stateNode===u){var h=F_((u[wn]||null).action),b=l.submitter;b&&(i=(i=b[wn]||null)?F_(i.formAction):b.getAttribute("formAction"),i!==null&&(h=i,b=null));var A=new Tc("action","action",null,l,u);e.push({event:A,listeners:[{instance:null,listener:function(){if(l.defaultPrevented){if(ns!==0){var F=b?H_(u,b):new FormData(u);Cd(r,{pending:!0,data:F,method:u.method,action:h},null,F)}}else typeof h=="function"&&(A.preventDefault(),F=b?H_(u,b):new FormData(u),Cd(r,{pending:!0,data:F,method:u.method,action:h},h,F))},currentTarget:u}]})}}for(var lh=0;lh<kf.length;lh++){var ch=kf[lh],WM=ch.toLowerCase(),YM=ch[0].toUpperCase()+ch.slice(1);Di(WM,"on"+YM)}Di(vg,"onAnimationEnd"),Di(_g,"onAnimationIteration"),Di(yg,"onAnimationStart"),Di("dblclick","onDoubleClick"),Di("focusin","onFocus"),Di("focusout","onBlur"),Di(uM,"onTransitionRun"),Di(fM,"onTransitionStart"),Di(dM,"onTransitionCancel"),Di(xg,"onTransitionEnd"),$t("onMouseEnter",["mouseout","mouseover"]),$t("onMouseLeave",["mouseout","mouseover"]),$t("onPointerEnter",["pointerout","pointerover"]),$t("onPointerLeave",["pointerout","pointerover"]),Pt("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),Pt("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),Pt("onBeforeInput",["compositionend","keypress","textInput","paste"]),Pt("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Ul="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),QM=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(Ul));function G_(e,i){i=(i&4)!==0;for(var r=0;r<e.length;r++){var l=e[r],u=l.event;l=l.listeners;t:{var h=void 0;if(i)for(var b=l.length-1;0<=b;b--){var A=l[b],F=A.instance,et=A.currentTarget;if(A=A.listener,F!==h&&u.isPropagationStopped())break t;h=A,u.currentTarget=et;try{h(u)}catch(ht){Rc(ht)}u.currentTarget=null,h=F}else for(b=0;b<l.length;b++){if(A=l[b],F=A.instance,et=A.currentTarget,A=A.listener,F!==h&&u.isPropagationStopped())break t;h=A,u.currentTarget=et;try{h(u)}catch(ht){Rc(ht)}u.currentTarget=null,h=F}}}}function xe(e,i){var r=i[$o];r===void 0&&(r=i[$o]=new Set);var l=e+"__bubble";r.has(l)||(V_(i,e,2,!1),r.add(l))}function uh(e,i,r){var l=0;i&&(l|=4),V_(r,e,l,i)}var pu="_reactListening"+Math.random().toString(36).slice(2);function fh(e){if(!e[pu]){e[pu]=!0,Ut.forEach(function(r){r!=="selectionchange"&&(QM.has(r)||uh(r,!1,e),uh(r,!0,e))});var i=e.nodeType===9?e:e.ownerDocument;i===null||i[pu]||(i[pu]=!0,uh("selectionchange",!1,i))}}function V_(e,i,r,l){switch(v0(i)){case 2:var u=E1;break;case 8:u=b1;break;default:u=Ah}r=u.bind(null,i,r,e),u=void 0,!Df||i!=="touchstart"&&i!=="touchmove"&&i!=="wheel"||(u=!0),l?u!==void 0?e.addEventListener(i,r,{capture:!0,passive:u}):e.addEventListener(i,r,!0):u!==void 0?e.addEventListener(i,r,{passive:u}):e.addEventListener(i,r,!1)}function dh(e,i,r,l,u){var h=l;if((i&1)===0&&(i&2)===0&&l!==null)t:for(;;){if(l===null)return;var b=l.tag;if(b===3||b===4){var A=l.stateNode.containerInfo;if(A===u)break;if(b===4)for(b=l.return;b!==null;){var F=b.tag;if((F===3||F===4)&&b.stateNode.containerInfo===u)return;b=b.return}for(;A!==null;){if(b=Q(A),b===null)return;if(F=b.tag,F===5||F===6||F===26||F===27){l=h=b;continue t}A=A.parentNode}}l=l.return}Wm(function(){var et=h,ht=wf(r),_t=[];t:{var it=Sg.get(e);if(it!==void 0){var lt=Tc,Gt=e;switch(e){case"keypress":if(Ec(r)===0)break t;case"keydown":case"keyup":lt=VS;break;case"focusin":Gt="focus",lt=Pf;break;case"focusout":Gt="blur",lt=Pf;break;case"beforeblur":case"afterblur":lt=Pf;break;case"click":if(r.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":lt=Zm;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":lt=NS;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":lt=XS;break;case vg:case _g:case yg:lt=LS;break;case xg:lt=WS;break;case"scroll":case"scrollend":lt=RS;break;case"wheel":lt=QS;break;case"copy":case"cut":case"paste":lt=PS;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":lt=Jm;break;case"toggle":case"beforetoggle":lt=KS}var ee=(i&4)!==0,Xe=!ee&&(e==="scroll"||e==="scrollend"),J=ee?it!==null?it+"Capture":null:it;ee=[];for(var k=et,tt;k!==null;){var gt=k;if(tt=gt.stateNode,gt=gt.tag,gt!==5&&gt!==26&&gt!==27||tt===null||J===null||(gt=tl(k,J),gt!=null&&ee.push(Ll(k,gt,tt))),Xe)break;k=k.return}0<ee.length&&(it=new lt(it,Gt,null,r,ht),_t.push({event:it,listeners:ee}))}}if((i&7)===0){t:{if(it=e==="mouseover"||e==="pointerover",lt=e==="mouseout"||e==="pointerout",it&&r!==Rf&&(Gt=r.relatedTarget||r.fromElement)&&(Q(Gt)||Gt[na]))break t;if((lt||it)&&(it=ht.window===ht?ht:(it=ht.ownerDocument)?it.defaultView||it.parentWindow:window,lt?(Gt=r.relatedTarget||r.toElement,lt=et,Gt=Gt?Q(Gt):null,Gt!==null&&(Xe=c(Gt),ee=Gt.tag,Gt!==Xe||ee!==5&&ee!==27&&ee!==6)&&(Gt=null)):(lt=null,Gt=et),lt!==Gt)){if(ee=Zm,gt="onMouseLeave",J="onMouseEnter",k="mouse",(e==="pointerout"||e==="pointerover")&&(ee=Jm,gt="onPointerLeave",J="onPointerEnter",k="pointer"),Xe=lt==null?it:rt(lt),tt=Gt==null?it:rt(Gt),it=new ee(gt,k+"leave",lt,r,ht),it.target=Xe,it.relatedTarget=tt,gt=null,Q(ht)===et&&(ee=new ee(J,k+"enter",Gt,r,ht),ee.target=tt,ee.relatedTarget=Xe,gt=ee),Xe=gt,lt&&Gt)e:{for(ee=ZM,J=lt,k=Gt,tt=0,gt=J;gt;gt=ee(gt))tt++;gt=0;for(var Jt=k;Jt;Jt=ee(Jt))gt++;for(;0<tt-gt;)J=ee(J),tt--;for(;0<gt-tt;)k=ee(k),gt--;for(;tt--;){if(J===k||k!==null&&J===k.alternate){ee=J;break e}J=ee(J),k=ee(k)}ee=null}else ee=null;lt!==null&&j_(_t,it,lt,ee,!1),Gt!==null&&Xe!==null&&j_(_t,Xe,Gt,ee,!0)}}t:{if(it=et?rt(et):window,lt=it.nodeName&&it.nodeName.toLowerCase(),lt==="select"||lt==="input"&&it.type==="file")var Le=rg;else if(ag(it))if(og)Le=oM;else{Le=sM;var kt=aM}else lt=it.nodeName,!lt||lt.toLowerCase()!=="input"||it.type!=="checkbox"&&it.type!=="radio"?et&&Cf(et.elementType)&&(Le=rg):Le=rM;if(Le&&(Le=Le(e,et))){sg(_t,Le,r,ht);break t}kt&&kt(e,it,et),e==="focusout"&&et&&it.type==="number"&&et.memoizedProps.value!=null&&yn(it,"number",it.value)}switch(kt=et?rt(et):window,e){case"focusin":(ag(kt)||kt.contentEditable==="true")&&(Rr=kt,Gf=et,ll=null);break;case"focusout":ll=Gf=Rr=null;break;case"mousedown":Vf=!0;break;case"contextmenu":case"mouseup":case"dragend":Vf=!1,mg(_t,r,ht);break;case"selectionchange":if(cM)break;case"keydown":case"keyup":mg(_t,r,ht)}var fe;if(If)t:{switch(e){case"compositionstart":var Te="onCompositionStart";break t;case"compositionend":Te="onCompositionEnd";break t;case"compositionupdate":Te="onCompositionUpdate";break t}Te=void 0}else Cr?ng(e,r)&&(Te="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(Te="onCompositionStart");Te&&($m&&r.locale!=="ko"&&(Cr||Te!=="onCompositionStart"?Te==="onCompositionEnd"&&Cr&&(fe=Ym()):(Ha=ht,Uf="value"in Ha?Ha.value:Ha.textContent,Cr=!0)),kt=mu(et,Te),0<kt.length&&(Te=new Km(Te,e,null,r,ht),_t.push({event:Te,listeners:kt}),fe?Te.data=fe:(fe=ig(r),fe!==null&&(Te.data=fe)))),(fe=$S?tM(e,r):eM(e,r))&&(Te=mu(et,"onBeforeInput"),0<Te.length&&(kt=new Km("onBeforeInput","beforeinput",null,r,ht),_t.push({event:kt,listeners:Te}),kt.data=fe)),qM(_t,e,et,r,ht)}G_(_t,i)})}function Ll(e,i,r){return{instance:e,listener:i,currentTarget:r}}function mu(e,i){for(var r=i+"Capture",l=[];e!==null;){var u=e,h=u.stateNode;if(u=u.tag,u!==5&&u!==26&&u!==27||h===null||(u=tl(e,r),u!=null&&l.unshift(Ll(e,u,h)),u=tl(e,i),u!=null&&l.push(Ll(e,u,h))),e.tag===3)return l;e=e.return}return[]}function ZM(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function j_(e,i,r,l,u){for(var h=i._reactName,b=[];r!==null&&r!==l;){var A=r,F=A.alternate,et=A.stateNode;if(A=A.tag,F!==null&&F===l)break;A!==5&&A!==26&&A!==27||et===null||(F=et,u?(et=tl(r,h),et!=null&&b.unshift(Ll(r,et,F))):u||(et=tl(r,h),et!=null&&b.push(Ll(r,et,F)))),r=r.return}b.length!==0&&e.push({event:i,listeners:b})}var KM=/\r\n?/g,JM=/\u0000|\uFFFD/g;function k_(e){return(typeof e=="string"?e:""+e).replace(KM,`
`).replace(JM,"")}function X_(e,i){return i=k_(i),k_(e)===i}function ke(e,i,r,l,u,h){switch(r){case"children":typeof l=="string"?i==="body"||i==="textarea"&&l===""||br(e,l):(typeof l=="number"||typeof l=="bigint")&&i!=="body"&&br(e,""+l);break;case"className":Ye(e,"class",l);break;case"tabIndex":Ye(e,"tabindex",l);break;case"dir":case"role":case"viewBox":case"width":case"height":Ye(e,r,l);break;case"style":Xm(e,l,h);break;case"data":if(i!=="object"){Ye(e,"data",l);break}case"src":case"href":if(l===""&&(i!=="a"||r!=="href")){e.removeAttribute(r);break}if(l==null||typeof l=="function"||typeof l=="symbol"||typeof l=="boolean"){e.removeAttribute(r);break}l=Sc(""+l),e.setAttribute(r,l);break;case"action":case"formAction":if(typeof l=="function"){e.setAttribute(r,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof h=="function"&&(r==="formAction"?(i!=="input"&&ke(e,i,"name",u.name,u,null),ke(e,i,"formEncType",u.formEncType,u,null),ke(e,i,"formMethod",u.formMethod,u,null),ke(e,i,"formTarget",u.formTarget,u,null)):(ke(e,i,"encType",u.encType,u,null),ke(e,i,"method",u.method,u,null),ke(e,i,"target",u.target,u,null)));if(l==null||typeof l=="symbol"||typeof l=="boolean"){e.removeAttribute(r);break}l=Sc(""+l),e.setAttribute(r,l);break;case"onClick":l!=null&&(e.onclick=aa);break;case"onScroll":l!=null&&xe("scroll",e);break;case"onScrollEnd":l!=null&&xe("scrollend",e);break;case"dangerouslySetInnerHTML":if(l!=null){if(typeof l!="object"||!("__html"in l))throw Error(s(61));if(r=l.__html,r!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"multiple":e.multiple=l&&typeof l!="function"&&typeof l!="symbol";break;case"muted":e.muted=l&&typeof l!="function"&&typeof l!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(l==null||typeof l=="function"||typeof l=="boolean"||typeof l=="symbol"){e.removeAttribute("xlink:href");break}r=Sc(""+l),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",r);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":l!=null&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,""+l):e.removeAttribute(r);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":l&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,""):e.removeAttribute(r);break;case"capture":case"download":l===!0?e.setAttribute(r,""):l!==!1&&l!=null&&typeof l!="function"&&typeof l!="symbol"?e.setAttribute(r,l):e.removeAttribute(r);break;case"cols":case"rows":case"size":case"span":l!=null&&typeof l!="function"&&typeof l!="symbol"&&!isNaN(l)&&1<=l?e.setAttribute(r,l):e.removeAttribute(r);break;case"rowSpan":case"start":l==null||typeof l=="function"||typeof l=="symbol"||isNaN(l)?e.removeAttribute(r):e.setAttribute(r,l);break;case"popover":xe("beforetoggle",e),xe("toggle",e),Ze(e,"popover",l);break;case"xlinkActuate":ce(e,"http://www.w3.org/1999/xlink","xlink:actuate",l);break;case"xlinkArcrole":ce(e,"http://www.w3.org/1999/xlink","xlink:arcrole",l);break;case"xlinkRole":ce(e,"http://www.w3.org/1999/xlink","xlink:role",l);break;case"xlinkShow":ce(e,"http://www.w3.org/1999/xlink","xlink:show",l);break;case"xlinkTitle":ce(e,"http://www.w3.org/1999/xlink","xlink:title",l);break;case"xlinkType":ce(e,"http://www.w3.org/1999/xlink","xlink:type",l);break;case"xmlBase":ce(e,"http://www.w3.org/XML/1998/namespace","xml:base",l);break;case"xmlLang":ce(e,"http://www.w3.org/XML/1998/namespace","xml:lang",l);break;case"xmlSpace":ce(e,"http://www.w3.org/XML/1998/namespace","xml:space",l);break;case"is":Ze(e,"is",l);break;case"innerText":case"textContent":break;default:(!(2<r.length)||r[0]!=="o"&&r[0]!=="O"||r[1]!=="n"&&r[1]!=="N")&&(r=AS.get(r)||r,Ze(e,r,l))}}function hh(e,i,r,l,u,h){switch(r){case"style":Xm(e,l,h);break;case"dangerouslySetInnerHTML":if(l!=null){if(typeof l!="object"||!("__html"in l))throw Error(s(61));if(r=l.__html,r!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"children":typeof l=="string"?br(e,l):(typeof l=="number"||typeof l=="bigint")&&br(e,""+l);break;case"onScroll":l!=null&&xe("scroll",e);break;case"onScrollEnd":l!=null&&xe("scrollend",e);break;case"onClick":l!=null&&(e.onclick=aa);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!It.hasOwnProperty(r))t:{if(r[0]==="o"&&r[1]==="n"&&(u=r.endsWith("Capture"),i=r.slice(2,u?r.length-7:void 0),h=e[wn]||null,h=h!=null?h[r]:null,typeof h=="function"&&e.removeEventListener(i,h,u),typeof l=="function")){typeof h!="function"&&h!==null&&(r in e?e[r]=null:e.hasAttribute(r)&&e.removeAttribute(r)),e.addEventListener(i,l,u);break t}r in e?e[r]=l:l===!0?e.setAttribute(r,""):Ze(e,r,l)}}}function Ln(e,i,r){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":xe("error",e),xe("load",e);var l=!1,u=!1,h;for(h in r)if(r.hasOwnProperty(h)){var b=r[h];if(b!=null)switch(h){case"src":l=!0;break;case"srcSet":u=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(s(137,i));default:ke(e,i,h,b,r,null)}}u&&ke(e,i,"srcSet",r.srcSet,r,null),l&&ke(e,i,"src",r.src,r,null);return;case"input":xe("invalid",e);var A=h=b=u=null,F=null,et=null;for(l in r)if(r.hasOwnProperty(l)){var ht=r[l];if(ht!=null)switch(l){case"name":u=ht;break;case"type":b=ht;break;case"checked":F=ht;break;case"defaultChecked":et=ht;break;case"value":h=ht;break;case"defaultValue":A=ht;break;case"children":case"dangerouslySetInnerHTML":if(ht!=null)throw Error(s(137,i));break;default:ke(e,i,l,ht,r,null)}}Vn(e,h,A,F,et,b,u,!1);return;case"select":xe("invalid",e),l=b=h=null;for(u in r)if(r.hasOwnProperty(u)&&(A=r[u],A!=null))switch(u){case"value":h=A;break;case"defaultValue":b=A;break;case"multiple":l=A;default:ke(e,i,u,A,r,null)}i=h,r=b,e.multiple=!!l,i!=null?cn(e,!!l,i,!1):r!=null&&cn(e,!!l,r,!0);return;case"textarea":xe("invalid",e),h=u=l=null;for(b in r)if(r.hasOwnProperty(b)&&(A=r[b],A!=null))switch(b){case"value":l=A;break;case"defaultValue":u=A;break;case"children":h=A;break;case"dangerouslySetInnerHTML":if(A!=null)throw Error(s(91));break;default:ke(e,i,b,A,r,null)}ki(e,l,u,h);return;case"option":for(F in r)if(r.hasOwnProperty(F)&&(l=r[F],l!=null))switch(F){case"selected":e.selected=l&&typeof l!="function"&&typeof l!="symbol";break;default:ke(e,i,F,l,r,null)}return;case"dialog":xe("beforetoggle",e),xe("toggle",e),xe("cancel",e),xe("close",e);break;case"iframe":case"object":xe("load",e);break;case"video":case"audio":for(l=0;l<Ul.length;l++)xe(Ul[l],e);break;case"image":xe("error",e),xe("load",e);break;case"details":xe("toggle",e);break;case"embed":case"source":case"link":xe("error",e),xe("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in r)if(r.hasOwnProperty(et)&&(l=r[et],l!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(s(137,i));default:ke(e,i,et,l,r,null)}return;default:if(Cf(i)){for(ht in r)r.hasOwnProperty(ht)&&(l=r[ht],l!==void 0&&hh(e,i,ht,l,r,void 0));return}}for(A in r)r.hasOwnProperty(A)&&(l=r[A],l!=null&&ke(e,i,A,l,r,null))}function $M(e,i,r,l){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var u=null,h=null,b=null,A=null,F=null,et=null,ht=null;for(lt in r){var _t=r[lt];if(r.hasOwnProperty(lt)&&_t!=null)switch(lt){case"checked":break;case"value":break;case"defaultValue":F=_t;default:l.hasOwnProperty(lt)||ke(e,i,lt,null,l,_t)}}for(var it in l){var lt=l[it];if(_t=r[it],l.hasOwnProperty(it)&&(lt!=null||_t!=null))switch(it){case"type":h=lt;break;case"name":u=lt;break;case"checked":et=lt;break;case"defaultChecked":ht=lt;break;case"value":b=lt;break;case"defaultValue":A=lt;break;case"children":case"dangerouslySetInnerHTML":if(lt!=null)throw Error(s(137,i));break;default:lt!==_t&&ke(e,i,it,lt,l,_t)}}zn(e,b,A,F,et,ht,h,u);return;case"select":lt=b=A=it=null;for(h in r)if(F=r[h],r.hasOwnProperty(h)&&F!=null)switch(h){case"value":break;case"multiple":lt=F;default:l.hasOwnProperty(h)||ke(e,i,h,null,l,F)}for(u in l)if(h=l[u],F=r[u],l.hasOwnProperty(u)&&(h!=null||F!=null))switch(u){case"value":it=h;break;case"defaultValue":A=h;break;case"multiple":b=h;default:h!==F&&ke(e,i,u,h,l,F)}i=A,r=b,l=lt,it!=null?cn(e,!!r,it,!1):!!l!=!!r&&(i!=null?cn(e,!!r,i,!0):cn(e,!!r,r?[]:"",!1));return;case"textarea":lt=it=null;for(A in r)if(u=r[A],r.hasOwnProperty(A)&&u!=null&&!l.hasOwnProperty(A))switch(A){case"value":break;case"children":break;default:ke(e,i,A,null,l,u)}for(b in l)if(u=l[b],h=r[b],l.hasOwnProperty(b)&&(u!=null||h!=null))switch(b){case"value":it=u;break;case"defaultValue":lt=u;break;case"children":break;case"dangerouslySetInnerHTML":if(u!=null)throw Error(s(91));break;default:u!==h&&ke(e,i,b,u,l,h)}Er(e,it,lt);return;case"option":for(var Gt in r)if(it=r[Gt],r.hasOwnProperty(Gt)&&it!=null&&!l.hasOwnProperty(Gt))switch(Gt){case"selected":e.selected=!1;break;default:ke(e,i,Gt,null,l,it)}for(F in l)if(it=l[F],lt=r[F],l.hasOwnProperty(F)&&it!==lt&&(it!=null||lt!=null))switch(F){case"selected":e.selected=it&&typeof it!="function"&&typeof it!="symbol";break;default:ke(e,i,F,it,l,lt)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var ee in r)it=r[ee],r.hasOwnProperty(ee)&&it!=null&&!l.hasOwnProperty(ee)&&ke(e,i,ee,null,l,it);for(et in l)if(it=l[et],lt=r[et],l.hasOwnProperty(et)&&it!==lt&&(it!=null||lt!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(it!=null)throw Error(s(137,i));break;default:ke(e,i,et,it,l,lt)}return;default:if(Cf(i)){for(var Xe in r)it=r[Xe],r.hasOwnProperty(Xe)&&it!==void 0&&!l.hasOwnProperty(Xe)&&hh(e,i,Xe,void 0,l,it);for(ht in l)it=l[ht],lt=r[ht],!l.hasOwnProperty(ht)||it===lt||it===void 0&&lt===void 0||hh(e,i,ht,it,l,lt);return}}for(var J in r)it=r[J],r.hasOwnProperty(J)&&it!=null&&!l.hasOwnProperty(J)&&ke(e,i,J,null,l,it);for(_t in l)it=l[_t],lt=r[_t],!l.hasOwnProperty(_t)||it===lt||it==null&&lt==null||ke(e,i,_t,it,l,lt)}function q_(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function t1(){if(typeof performance.getEntriesByType=="function"){for(var e=0,i=0,r=performance.getEntriesByType("resource"),l=0;l<r.length;l++){var u=r[l],h=u.transferSize,b=u.initiatorType,A=u.duration;if(h&&A&&q_(b)){for(b=0,A=u.responseEnd,l+=1;l<r.length;l++){var F=r[l],et=F.startTime;if(et>A)break;var ht=F.transferSize,_t=F.initiatorType;ht&&q_(_t)&&(F=F.responseEnd,b+=ht*(F<A?1:(A-et)/(F-et)))}if(--l,i+=8*(h+b)/(u.duration/1e3),e++,10<e)break}}if(0<e)return i/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var ph=null,mh=null;function gu(e){return e.nodeType===9?e:e.ownerDocument}function W_(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function Y_(e,i){if(e===0)switch(i){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&i==="foreignObject"?0:e}function gh(e,i){return e==="textarea"||e==="noscript"||typeof i.children=="string"||typeof i.children=="number"||typeof i.children=="bigint"||typeof i.dangerouslySetInnerHTML=="object"&&i.dangerouslySetInnerHTML!==null&&i.dangerouslySetInnerHTML.__html!=null}var vh=null;function e1(){var e=window.event;return e&&e.type==="popstate"?e===vh?!1:(vh=e,!0):(vh=null,!1)}var Q_=typeof setTimeout=="function"?setTimeout:void 0,n1=typeof clearTimeout=="function"?clearTimeout:void 0,Z_=typeof Promise=="function"?Promise:void 0,i1=typeof queueMicrotask=="function"?queueMicrotask:typeof Z_<"u"?function(e){return Z_.resolve(null).then(e).catch(a1)}:Q_;function a1(e){setTimeout(function(){throw e})}function is(e){return e==="head"}function K_(e,i){var r=i,l=0;do{var u=r.nextSibling;if(e.removeChild(r),u&&u.nodeType===8)if(r=u.data,r==="/$"||r==="/&"){if(l===0){e.removeChild(u),eo(i);return}l--}else if(r==="$"||r==="$?"||r==="$~"||r==="$!"||r==="&")l++;else if(r==="html")Ol(e.ownerDocument.documentElement);else if(r==="head"){r=e.ownerDocument.head,Ol(r);for(var h=r.firstChild;h;){var b=h.nextSibling,A=h.nodeName;h[Ds]||A==="SCRIPT"||A==="STYLE"||A==="LINK"&&h.rel.toLowerCase()==="stylesheet"||r.removeChild(h),h=b}}else r==="body"&&Ol(e.ownerDocument.body);r=u}while(r);eo(i)}function J_(e,i){var r=e;e=0;do{var l=r.nextSibling;if(r.nodeType===1?i?(r._stashedDisplay=r.style.display,r.style.display="none"):(r.style.display=r._stashedDisplay||"",r.getAttribute("style")===""&&r.removeAttribute("style")):r.nodeType===3&&(i?(r._stashedText=r.nodeValue,r.nodeValue=""):r.nodeValue=r._stashedText||""),l&&l.nodeType===8)if(r=l.data,r==="/$"){if(e===0)break;e--}else r!=="$"&&r!=="$?"&&r!=="$~"&&r!=="$!"||e++;r=l}while(r)}function _h(e){var i=e.firstChild;for(i&&i.nodeType===10&&(i=i.nextSibling);i;){var r=i;switch(i=i.nextSibling,r.nodeName){case"HTML":case"HEAD":case"BODY":_h(r),w(r);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(r.rel.toLowerCase()==="stylesheet")continue}e.removeChild(r)}}function s1(e,i,r,l){for(;e.nodeType===1;){var u=r;if(e.nodeName.toLowerCase()!==i.toLowerCase()){if(!l&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(l){if(!e[Ds])switch(i){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(h=e.getAttribute("rel"),h==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(h!==u.rel||e.getAttribute("href")!==(u.href==null||u.href===""?null:u.href)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin)||e.getAttribute("title")!==(u.title==null?null:u.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(h=e.getAttribute("src"),(h!==(u.src==null?null:u.src)||e.getAttribute("type")!==(u.type==null?null:u.type)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin))&&h&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(i==="input"&&e.type==="hidden"){var h=u.name==null?null:""+u.name;if(u.type==="hidden"&&e.getAttribute("name")===h)return e}else return e;if(e=Ti(e.nextSibling),e===null)break}return null}function r1(e,i,r){if(i==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!r||(e=Ti(e.nextSibling),e===null))return null;return e}function $_(e,i){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!i||(e=Ti(e.nextSibling),e===null))return null;return e}function yh(e){return e.data==="$?"||e.data==="$~"}function xh(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function o1(e,i){var r=e.ownerDocument;if(e.data==="$~")e._reactRetry=i;else if(e.data!=="$?"||r.readyState!=="loading")i();else{var l=function(){i(),r.removeEventListener("DOMContentLoaded",l)};r.addEventListener("DOMContentLoaded",l),e._reactRetry=l}}function Ti(e){for(;e!=null;e=e.nextSibling){var i=e.nodeType;if(i===1||i===3)break;if(i===8){if(i=e.data,i==="$"||i==="$!"||i==="$?"||i==="$~"||i==="&"||i==="F!"||i==="F")break;if(i==="/$"||i==="/&")return null}}return e}var Sh=null;function t0(e){e=e.nextSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"||r==="/&"){if(i===0)return Ti(e.nextSibling);i--}else r!=="$"&&r!=="$!"&&r!=="$?"&&r!=="$~"&&r!=="&"||i++}e=e.nextSibling}return null}function e0(e){e=e.previousSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"||r==="$~"||r==="&"){if(i===0)return e;i--}else r!=="/$"&&r!=="/&"||i++}e=e.previousSibling}return null}function n0(e,i,r){switch(i=gu(r),e){case"html":if(e=i.documentElement,!e)throw Error(s(452));return e;case"head":if(e=i.head,!e)throw Error(s(453));return e;case"body":if(e=i.body,!e)throw Error(s(454));return e;default:throw Error(s(451))}}function Ol(e){for(var i=e.attributes;i.length;)e.removeAttributeNode(i[0]);w(e)}var Ai=new Map,i0=new Set;function vu(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var xa=Z.d;Z.d={f:l1,r:c1,D:u1,C:f1,L:d1,m:h1,X:m1,S:p1,M:g1};function l1(){var e=xa.f(),i=lu();return e||i}function c1(e){var i=st(e);i!==null&&i.tag===5&&i.type==="form"?xv(i):xa.r(e)}var Jr=typeof document>"u"?null:document;function a0(e,i,r){var l=Jr;if(l&&typeof i=="string"&&i){var u=_e(i);u='link[rel="'+e+'"][href="'+u+'"]',typeof r=="string"&&(u+='[crossorigin="'+r+'"]'),i0.has(u)||(i0.add(u),e={rel:e,crossOrigin:r,href:i},l.querySelector(u)===null&&(i=l.createElement("link"),Ln(i,"link",e),xt(i),l.head.appendChild(i)))}}function u1(e){xa.D(e),a0("dns-prefetch",e,null)}function f1(e,i){xa.C(e,i),a0("preconnect",e,i)}function d1(e,i,r){xa.L(e,i,r);var l=Jr;if(l&&e&&i){var u='link[rel="preload"][as="'+_e(i)+'"]';i==="image"&&r&&r.imageSrcSet?(u+='[imagesrcset="'+_e(r.imageSrcSet)+'"]',typeof r.imageSizes=="string"&&(u+='[imagesizes="'+_e(r.imageSizes)+'"]')):u+='[href="'+_e(e)+'"]';var h=u;switch(i){case"style":h=$r(e);break;case"script":h=to(e)}Ai.has(h)||(e=_({rel:"preload",href:i==="image"&&r&&r.imageSrcSet?void 0:e,as:i},r),Ai.set(h,e),l.querySelector(u)!==null||i==="style"&&l.querySelector(Pl(h))||i==="script"&&l.querySelector(zl(h))||(i=l.createElement("link"),Ln(i,"link",e),xt(i),l.head.appendChild(i)))}}function h1(e,i){xa.m(e,i);var r=Jr;if(r&&e){var l=i&&typeof i.as=="string"?i.as:"script",u='link[rel="modulepreload"][as="'+_e(l)+'"][href="'+_e(e)+'"]',h=u;switch(l){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":h=to(e)}if(!Ai.has(h)&&(e=_({rel:"modulepreload",href:e},i),Ai.set(h,e),r.querySelector(u)===null)){switch(l){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(r.querySelector(zl(h)))return}l=r.createElement("link"),Ln(l,"link",e),xt(l),r.head.appendChild(l)}}}function p1(e,i,r){xa.S(e,i,r);var l=Jr;if(l&&e){var u=K(l).hoistableStyles,h=$r(e);i=i||"default";var b=u.get(h);if(!b){var A={loading:0,preload:null};if(b=l.querySelector(Pl(h)))A.loading=5;else{e=_({rel:"stylesheet",href:e,"data-precedence":i},r),(r=Ai.get(h))&&Mh(e,r);var F=b=l.createElement("link");xt(F),Ln(F,"link",e),F._p=new Promise(function(et,ht){F.onload=et,F.onerror=ht}),F.addEventListener("load",function(){A.loading|=1}),F.addEventListener("error",function(){A.loading|=2}),A.loading|=4,_u(b,i,l)}b={type:"stylesheet",instance:b,count:1,state:A},u.set(h,b)}}}function m1(e,i){xa.X(e,i);var r=Jr;if(r&&e){var l=K(r).hoistableScripts,u=to(e),h=l.get(u);h||(h=r.querySelector(zl(u)),h||(e=_({src:e,async:!0},i),(i=Ai.get(u))&&Eh(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},l.set(u,h))}}function g1(e,i){xa.M(e,i);var r=Jr;if(r&&e){var l=K(r).hoistableScripts,u=to(e),h=l.get(u);h||(h=r.querySelector(zl(u)),h||(e=_({src:e,async:!0,type:"module"},i),(i=Ai.get(u))&&Eh(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},l.set(u,h))}}function s0(e,i,r,l){var u=(u=Tt.current)?vu(u):null;if(!u)throw Error(s(446));switch(e){case"meta":case"title":return null;case"style":return typeof r.precedence=="string"&&typeof r.href=="string"?(i=$r(r.href),r=K(u).hoistableStyles,l=r.get(i),l||(l={type:"style",instance:null,count:0,state:null},r.set(i,l)),l):{type:"void",instance:null,count:0,state:null};case"link":if(r.rel==="stylesheet"&&typeof r.href=="string"&&typeof r.precedence=="string"){e=$r(r.href);var h=K(u).hoistableStyles,b=h.get(e);if(b||(u=u.ownerDocument||u,b={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},h.set(e,b),(h=u.querySelector(Pl(e)))&&!h._p&&(b.instance=h,b.state.loading=5),Ai.has(e)||(r={rel:"preload",as:"style",href:r.href,crossOrigin:r.crossOrigin,integrity:r.integrity,media:r.media,hrefLang:r.hrefLang,referrerPolicy:r.referrerPolicy},Ai.set(e,r),h||v1(u,e,r,b.state))),i&&l===null)throw Error(s(528,""));return b}if(i&&l!==null)throw Error(s(529,""));return null;case"script":return i=r.async,r=r.src,typeof r=="string"&&i&&typeof i!="function"&&typeof i!="symbol"?(i=to(r),r=K(u).hoistableScripts,l=r.get(i),l||(l={type:"script",instance:null,count:0,state:null},r.set(i,l)),l):{type:"void",instance:null,count:0,state:null};default:throw Error(s(444,e))}}function $r(e){return'href="'+_e(e)+'"'}function Pl(e){return'link[rel="stylesheet"]['+e+"]"}function r0(e){return _({},e,{"data-precedence":e.precedence,precedence:null})}function v1(e,i,r,l){e.querySelector('link[rel="preload"][as="style"]['+i+"]")?l.loading=1:(i=e.createElement("link"),l.preload=i,i.addEventListener("load",function(){return l.loading|=1}),i.addEventListener("error",function(){return l.loading|=2}),Ln(i,"link",r),xt(i),e.head.appendChild(i))}function to(e){return'[src="'+_e(e)+'"]'}function zl(e){return"script[async]"+e}function o0(e,i,r){if(i.count++,i.instance===null)switch(i.type){case"style":var l=e.querySelector('style[data-href~="'+_e(r.href)+'"]');if(l)return i.instance=l,xt(l),l;var u=_({},r,{"data-href":r.href,"data-precedence":r.precedence,href:null,precedence:null});return l=(e.ownerDocument||e).createElement("style"),xt(l),Ln(l,"style",u),_u(l,r.precedence,e),i.instance=l;case"stylesheet":u=$r(r.href);var h=e.querySelector(Pl(u));if(h)return i.state.loading|=4,i.instance=h,xt(h),h;l=r0(r),(u=Ai.get(u))&&Mh(l,u),h=(e.ownerDocument||e).createElement("link"),xt(h);var b=h;return b._p=new Promise(function(A,F){b.onload=A,b.onerror=F}),Ln(h,"link",l),i.state.loading|=4,_u(h,r.precedence,e),i.instance=h;case"script":return h=to(r.src),(u=e.querySelector(zl(h)))?(i.instance=u,xt(u),u):(l=r,(u=Ai.get(h))&&(l=_({},r),Eh(l,u)),e=e.ownerDocument||e,u=e.createElement("script"),xt(u),Ln(u,"link",l),e.head.appendChild(u),i.instance=u);case"void":return null;default:throw Error(s(443,i.type))}else i.type==="stylesheet"&&(i.state.loading&4)===0&&(l=i.instance,i.state.loading|=4,_u(l,r.precedence,e));return i.instance}function _u(e,i,r){for(var l=r.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),u=l.length?l[l.length-1]:null,h=u,b=0;b<l.length;b++){var A=l[b];if(A.dataset.precedence===i)h=A;else if(h!==u)break}h?h.parentNode.insertBefore(e,h.nextSibling):(i=r.nodeType===9?r.head:r,i.insertBefore(e,i.firstChild))}function Mh(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.title==null&&(e.title=i.title)}function Eh(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.integrity==null&&(e.integrity=i.integrity)}var yu=null;function l0(e,i,r){if(yu===null){var l=new Map,u=yu=new Map;u.set(r,l)}else u=yu,l=u.get(r),l||(l=new Map,u.set(r,l));if(l.has(e))return l;for(l.set(e,null),r=r.getElementsByTagName(e),u=0;u<r.length;u++){var h=r[u];if(!(h[Ds]||h[sn]||e==="link"&&h.getAttribute("rel")==="stylesheet")&&h.namespaceURI!=="http://www.w3.org/2000/svg"){var b=h.getAttribute(i)||"";b=e+b;var A=l.get(b);A?A.push(h):l.set(b,[h])}}return l}function c0(e,i,r){e=e.ownerDocument||e,e.head.insertBefore(r,i==="title"?e.querySelector("head > title"):null)}function _1(e,i,r){if(r===1||i.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof i.precedence!="string"||typeof i.href!="string"||i.href==="")break;return!0;case"link":if(typeof i.rel!="string"||typeof i.href!="string"||i.href===""||i.onLoad||i.onError)break;switch(i.rel){case"stylesheet":return e=i.disabled,typeof i.precedence=="string"&&e==null;default:return!0}case"script":if(i.async&&typeof i.async!="function"&&typeof i.async!="symbol"&&!i.onLoad&&!i.onError&&i.src&&typeof i.src=="string")return!0}return!1}function u0(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function y1(e,i,r,l){if(r.type==="stylesheet"&&(typeof l.media!="string"||matchMedia(l.media).matches!==!1)&&(r.state.loading&4)===0){if(r.instance===null){var u=$r(l.href),h=i.querySelector(Pl(u));if(h){i=h._p,i!==null&&typeof i=="object"&&typeof i.then=="function"&&(e.count++,e=xu.bind(e),i.then(e,e)),r.state.loading|=4,r.instance=h,xt(h);return}h=i.ownerDocument||i,l=r0(l),(u=Ai.get(u))&&Mh(l,u),h=h.createElement("link"),xt(h);var b=h;b._p=new Promise(function(A,F){b.onload=A,b.onerror=F}),Ln(h,"link",l),r.instance=h}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(r,i),(i=r.state.preload)&&(r.state.loading&3)===0&&(e.count++,r=xu.bind(e),i.addEventListener("load",r),i.addEventListener("error",r))}}var bh=0;function x1(e,i){return e.stylesheets&&e.count===0&&Mu(e,e.stylesheets),0<e.count||0<e.imgCount?function(r){var l=setTimeout(function(){if(e.stylesheets&&Mu(e,e.stylesheets),e.unsuspend){var h=e.unsuspend;e.unsuspend=null,h()}},6e4+i);0<e.imgBytes&&bh===0&&(bh=62500*t1());var u=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&Mu(e,e.stylesheets),e.unsuspend)){var h=e.unsuspend;e.unsuspend=null,h()}},(e.imgBytes>bh?50:800)+i);return e.unsuspend=r,function(){e.unsuspend=null,clearTimeout(l),clearTimeout(u)}}:null}function xu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)Mu(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var Su=null;function Mu(e,i){e.stylesheets=null,e.unsuspend!==null&&(e.count++,Su=new Map,i.forEach(S1,e),Su=null,xu.call(e))}function S1(e,i){if(!(i.state.loading&4)){var r=Su.get(e);if(r)var l=r.get(null);else{r=new Map,Su.set(e,r);for(var u=e.querySelectorAll("link[data-precedence],style[data-precedence]"),h=0;h<u.length;h++){var b=u[h];(b.nodeName==="LINK"||b.getAttribute("media")!=="not all")&&(r.set(b.dataset.precedence,b),l=b)}l&&r.set(null,l)}u=i.instance,b=u.getAttribute("data-precedence"),h=r.get(b)||l,h===l&&r.set(null,u),r.set(b,u),this.count++,l=xu.bind(this),u.addEventListener("load",l),u.addEventListener("error",l),h?h.parentNode.insertBefore(u,h.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(u,e.firstChild)),i.state.loading|=4}}var Il={$$typeof:D,Provider:null,Consumer:null,_currentValue:$,_currentValue2:$,_threadCount:0};function M1(e,i,r,l,u,h,b,A,F){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Ne(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Ne(0),this.hiddenUpdates=Ne(null),this.identifierPrefix=l,this.onUncaughtError=u,this.onCaughtError=h,this.onRecoverableError=b,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=F,this.incompleteTransitions=new Map}function f0(e,i,r,l,u,h,b,A,F,et,ht,_t){return e=new M1(e,i,r,b,F,et,ht,_t,A),i=1,h===!0&&(i|=24),h=oi(3,null,null,i),e.current=h,h.stateNode=e,i=id(),i.refCount++,e.pooledCache=i,i.refCount++,h.memoizedState={element:l,isDehydrated:r,cache:i},od(h),e}function d0(e){return e?(e=Dr,e):Dr}function h0(e,i,r,l,u,h){u=d0(u),l.context===null?l.context=u:l.pendingContext=u,l=qa(i),l.payload={element:r},h=h===void 0?null:h,h!==null&&(l.callback=h),r=Wa(e,l,i),r!==null&&(ti(r,e,i),ml(r,e,i))}function p0(e,i){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<i?r:i}}function Th(e,i){p0(e,i),(e=e.alternate)&&p0(e,i)}function m0(e){if(e.tag===13||e.tag===31){var i=zs(e,67108864);i!==null&&ti(i,e,67108864),Th(e,67108864)}}function g0(e){if(e.tag===13||e.tag===31){var i=di();i=ws(i);var r=zs(e,i);r!==null&&ti(r,e,i),Th(e,i)}}var Eu=!0;function E1(e,i,r,l){var u=B.T;B.T=null;var h=Z.p;try{Z.p=2,Ah(e,i,r,l)}finally{Z.p=h,B.T=u}}function b1(e,i,r,l){var u=B.T;B.T=null;var h=Z.p;try{Z.p=8,Ah(e,i,r,l)}finally{Z.p=h,B.T=u}}function Ah(e,i,r,l){if(Eu){var u=Ch(l);if(u===null)dh(e,i,l,bu,r),_0(e,l);else if(A1(u,e,i,r,l))l.stopPropagation();else if(_0(e,l),i&4&&-1<T1.indexOf(e)){for(;u!==null;){var h=st(u);if(h!==null)switch(h.tag){case 3:if(h=h.stateNode,h.current.memoizedState.isDehydrated){var b=wt(h.pendingLanes);if(b!==0){var A=h;for(A.pendingLanes|=2,A.entangledLanes|=2;b;){var F=1<<31-ne(b);A.entanglements[1]|=F,b&=~F}Yi(h),(ze&6)===0&&(ru=pt()+500,Dl(0))}}break;case 31:case 13:A=zs(h,2),A!==null&&ti(A,h,2),lu(),Th(h,2)}if(h=Ch(l),h===null&&dh(e,i,l,bu,r),h===u)break;u=h}u!==null&&l.stopPropagation()}else dh(e,i,l,null,r)}}function Ch(e){return e=wf(e),Rh(e)}var bu=null;function Rh(e){if(bu=null,e=Q(e),e!==null){var i=c(e);if(i===null)e=null;else{var r=i.tag;if(r===13){if(e=f(i),e!==null)return e;e=null}else if(r===31){if(e=d(i),e!==null)return e;e=null}else if(r===3){if(i.stateNode.current.memoizedState.isDehydrated)return i.tag===3?i.stateNode.containerInfo:null;e=null}else i!==e&&(e=null)}}return bu=e,null}function v0(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(bt()){case vt:return 2;case Xt:return 8;case Nt:case Bt:return 32;case Me:return 268435456;default:return 32}default:return 32}}var wh=!1,as=null,ss=null,rs=null,Bl=new Map,Fl=new Map,os=[],T1="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function _0(e,i){switch(e){case"focusin":case"focusout":as=null;break;case"dragenter":case"dragleave":ss=null;break;case"mouseover":case"mouseout":rs=null;break;case"pointerover":case"pointerout":Bl.delete(i.pointerId);break;case"gotpointercapture":case"lostpointercapture":Fl.delete(i.pointerId)}}function Hl(e,i,r,l,u,h){return e===null||e.nativeEvent!==h?(e={blockedOn:i,domEventName:r,eventSystemFlags:l,nativeEvent:h,targetContainers:[u]},i!==null&&(i=st(i),i!==null&&m0(i)),e):(e.eventSystemFlags|=l,i=e.targetContainers,u!==null&&i.indexOf(u)===-1&&i.push(u),e)}function A1(e,i,r,l,u){switch(i){case"focusin":return as=Hl(as,e,i,r,l,u),!0;case"dragenter":return ss=Hl(ss,e,i,r,l,u),!0;case"mouseover":return rs=Hl(rs,e,i,r,l,u),!0;case"pointerover":var h=u.pointerId;return Bl.set(h,Hl(Bl.get(h)||null,e,i,r,l,u)),!0;case"gotpointercapture":return h=u.pointerId,Fl.set(h,Hl(Fl.get(h)||null,e,i,r,l,u)),!0}return!1}function y0(e){var i=Q(e.target);if(i!==null){var r=c(i);if(r!==null){if(i=r.tag,i===13){if(i=f(r),i!==null){e.blockedOn=i,Ns(e.priority,function(){g0(r)});return}}else if(i===31){if(i=d(r),i!==null){e.blockedOn=i,Ns(e.priority,function(){g0(r)});return}}else if(i===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Tu(e){if(e.blockedOn!==null)return!1;for(var i=e.targetContainers;0<i.length;){var r=Ch(e.nativeEvent);if(r===null){r=e.nativeEvent;var l=new r.constructor(r.type,r);Rf=l,r.target.dispatchEvent(l),Rf=null}else return i=st(r),i!==null&&m0(i),e.blockedOn=r,!1;i.shift()}return!0}function x0(e,i,r){Tu(e)&&r.delete(i)}function C1(){wh=!1,as!==null&&Tu(as)&&(as=null),ss!==null&&Tu(ss)&&(ss=null),rs!==null&&Tu(rs)&&(rs=null),Bl.forEach(x0),Fl.forEach(x0)}function Au(e,i){e.blockedOn===i&&(e.blockedOn=null,wh||(wh=!0,a.unstable_scheduleCallback(a.unstable_NormalPriority,C1)))}var Cu=null;function S0(e){Cu!==e&&(Cu=e,a.unstable_scheduleCallback(a.unstable_NormalPriority,function(){Cu===e&&(Cu=null);for(var i=0;i<e.length;i+=3){var r=e[i],l=e[i+1],u=e[i+2];if(typeof l!="function"){if(Rh(l||r)===null)continue;break}var h=st(r);h!==null&&(e.splice(i,3),i-=3,Cd(h,{pending:!0,data:u,method:r.method,action:l},l,u))}}))}function eo(e){function i(F){return Au(F,e)}as!==null&&Au(as,e),ss!==null&&Au(ss,e),rs!==null&&Au(rs,e),Bl.forEach(i),Fl.forEach(i);for(var r=0;r<os.length;r++){var l=os[r];l.blockedOn===e&&(l.blockedOn=null)}for(;0<os.length&&(r=os[0],r.blockedOn===null);)y0(r),r.blockedOn===null&&os.shift();if(r=(e.ownerDocument||e).$$reactFormReplay,r!=null)for(l=0;l<r.length;l+=3){var u=r[l],h=r[l+1],b=u[wn]||null;if(typeof h=="function")b||S0(r);else if(b){var A=null;if(h&&h.hasAttribute("formAction")){if(u=h,b=h[wn]||null)A=b.formAction;else if(Rh(u)!==null)continue}else A=b.action;typeof A=="function"?r[l+1]=A:(r.splice(l,3),l-=3),S0(r)}}}function M0(){function e(h){h.canIntercept&&h.info==="react-transition"&&h.intercept({handler:function(){return new Promise(function(b){return u=b})},focusReset:"manual",scroll:"manual"})}function i(){u!==null&&(u(),u=null),l||setTimeout(r,20)}function r(){if(!l&&!navigation.transition){var h=navigation.currentEntry;h&&h.url!=null&&navigation.navigate(h.url,{state:h.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var l=!1,u=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",i),navigation.addEventListener("navigateerror",i),setTimeout(r,100),function(){l=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",i),navigation.removeEventListener("navigateerror",i),u!==null&&(u(),u=null)}}}function Nh(e){this._internalRoot=e}Ru.prototype.render=Nh.prototype.render=function(e){var i=this._internalRoot;if(i===null)throw Error(s(409));var r=i.current,l=di();h0(r,l,e,i,null,null)},Ru.prototype.unmount=Nh.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var i=e.containerInfo;h0(e.current,2,null,e,null,null),lu(),i[na]=null}};function Ru(e){this._internalRoot=e}Ru.prototype.unstable_scheduleHydration=function(e){if(e){var i=Jo();e={blockedOn:null,target:e,priority:i};for(var r=0;r<os.length&&i!==0&&i<os[r].priority;r++);os.splice(r,0,e),r===0&&y0(e)}};var E0=t.version;if(E0!=="19.2.7")throw Error(s(527,E0,"19.2.7"));Z.findDOMNode=function(e){var i=e._reactInternals;if(i===void 0)throw typeof e.render=="function"?Error(s(188)):(e=Object.keys(e).join(","),Error(s(268,e)));return e=m(i),e=e!==null?v(e):null,e=e===null?null:e.stateNode,e};var R1={bundleType:0,version:"19.2.7",rendererPackageName:"react-dom",currentDispatcherRef:B,reconcilerVersion:"19.2.7"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var wu=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!wu.isDisabled&&wu.supportsFiber)try{Zt=wu.inject(R1),qt=wu}catch{}}return Vl.createRoot=function(e,i){if(!o(e))throw Error(s(299));var r=!1,l="",u=Nv,h=Dv,b=Uv;return i!=null&&(i.unstable_strictMode===!0&&(r=!0),i.identifierPrefix!==void 0&&(l=i.identifierPrefix),i.onUncaughtError!==void 0&&(u=i.onUncaughtError),i.onCaughtError!==void 0&&(h=i.onCaughtError),i.onRecoverableError!==void 0&&(b=i.onRecoverableError)),i=f0(e,1,!1,null,null,r,l,null,u,h,b,M0),e[na]=i.current,fh(e),new Nh(i)},Vl.hydrateRoot=function(e,i,r){if(!o(e))throw Error(s(299));var l=!1,u="",h=Nv,b=Dv,A=Uv,F=null;return r!=null&&(r.unstable_strictMode===!0&&(l=!0),r.identifierPrefix!==void 0&&(u=r.identifierPrefix),r.onUncaughtError!==void 0&&(h=r.onUncaughtError),r.onCaughtError!==void 0&&(b=r.onCaughtError),r.onRecoverableError!==void 0&&(A=r.onRecoverableError),r.formState!==void 0&&(F=r.formState)),i=f0(e,1,!0,i,r??null,l,u,F,h,b,A,M0),i.context=d0(null),r=i.current,l=di(),l=ws(l),u=qa(l),u.callback=null,Wa(r,u,l),r=l,i.current.lanes=r,Rn(i,r),Yi(i),e[na]=i.current,fh(e),new Ru(i)},Vl.version="19.2.7",Vl}var O0;function F1(){if(O0)return Oh.exports;O0=1;function a(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(a)}catch(t){console.error(t)}}return a(),Oh.exports=B1(),Oh.exports}var H1=F1();const G1=fx(H1);var mc=class{constructor(){this.listeners=new Set,this.subscribe=this.subscribe.bind(this)}subscribe(a){return this.listeners.add(a),this.onSubscribe(),()=>{this.listeners.delete(a),this.onUnsubscribe()}}hasListeners(){return this.listeners.size>0}onSubscribe(){}onUnsubscribe(){}},fr,_s,Ao,ex,V1=(ex=class extends mc{constructor(){super();te(this,fr);te(this,_s);te(this,Ao);zt(this,Ao,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t();return window.addEventListener("visibilitychange",n,!1),()=>{window.removeEventListener("visibilitychange",n)}}})}onSubscribe(){X(this,_s)||this.setEventListener(X(this,Ao))}onUnsubscribe(){var t;this.hasListeners()||((t=X(this,_s))==null||t.call(this),zt(this,_s,void 0))}setEventListener(t){var n;zt(this,Ao,t),(n=X(this,_s))==null||n.call(this),zt(this,_s,t(s=>{typeof s=="boolean"?this.setFocused(s):this.onFocus()}))}setFocused(t){X(this,fr)!==t&&(zt(this,fr,t),this.onFocus())}onFocus(){const t=this.isFocused();this.listeners.forEach(n=>{n(t)})}isFocused(){var t;return typeof X(this,fr)=="boolean"?X(this,fr):((t=globalThis.document)==null?void 0:t.visibilityState)!=="hidden"}},fr=new WeakMap,_s=new WeakMap,Ao=new WeakMap,ex),Em=new V1,j1={setTimeout:(a,t)=>setTimeout(a,t),clearTimeout:a=>clearTimeout(a),setInterval:(a,t)=>setInterval(a,t),clearInterval:a=>clearInterval(a)},ys,Sm,nx,k1=(nx=class{constructor(){te(this,ys,j1);te(this,Sm,!1)}setTimeoutProvider(a){zt(this,ys,a)}setTimeout(a,t){return X(this,ys).setTimeout(a,t)}clearTimeout(a){X(this,ys).clearTimeout(a)}setInterval(a,t){return X(this,ys).setInterval(a,t)}clearInterval(a){X(this,ys).clearInterval(a)}},ys=new WeakMap,Sm=new WeakMap,nx),or=new k1;function X1(a){setTimeout(a,0)}var q1=typeof window>"u"||"Deno"in globalThis;function ni(){}function W1(a,t){return typeof a=="function"?a(t):a}function _p(a){return typeof a=="number"&&a>=0&&a!==1/0}function dx(a,t){return Math.max(a+(t||0)-Date.now(),0)}function As(a,t){return typeof a=="function"?a(t):a}function gi(a,t){return typeof a=="function"?a(t):a}function P0(a,t){const{type:n="all",exact:s,fetchStatus:o,predicate:c,queryKey:f,stale:d}=a;if(f){if(s){if(t.queryHash!==bm(f,t.options))return!1}else if(!ac(t.queryKey,f))return!1}if(n!=="all"){const p=t.isActive();if(n==="active"&&!p||n==="inactive"&&p)return!1}return!(typeof d=="boolean"&&t.isStale()!==d||o&&o!==t.state.fetchStatus||c&&!c(t))}function z0(a,t){const{exact:n,status:s,predicate:o,mutationKey:c}=a;if(c){if(!t.options.mutationKey)return!1;if(n){if(ic(t.options.mutationKey)!==ic(c))return!1}else if(!ac(t.options.mutationKey,c))return!1}return!(s&&t.state.status!==s||o&&!o(t))}function bm(a,t){return((t==null?void 0:t.queryKeyHashFn)||ic)(a)}function ic(a){return JSON.stringify(a,(t,n)=>xp(n)?Object.keys(n).sort().reduce((s,o)=>(s[o]=n[o],s),{}):n)}function ac(a,t){return a===t?!0:typeof a!=typeof t?!1:a&&t&&typeof a=="object"&&typeof t=="object"?Object.keys(t).every(n=>ac(a[n],t[n])):!1}var Y1=Object.prototype.hasOwnProperty;function hx(a,t,n=0){if(a===t)return a;if(n>500)return t;const s=I0(a)&&I0(t);if(!s&&!(xp(a)&&xp(t)))return t;const c=(s?a:Object.keys(a)).length,f=s?t:Object.keys(t),d=f.length,p=s?new Array(d):{};let m=0;for(let v=0;v<d;v++){const _=s?v:f[v],x=a[_],E=t[_];if(x===E){p[_]=x,(s?v<c:Y1.call(a,_))&&m++;continue}if(x===null||E===null||typeof x!="object"||typeof E!="object"){p[_]=E;continue}const M=hx(x,E,n+1);p[_]=M,M===x&&m++}return c===d&&m===c?a:p}function yp(a,t){if(!t||Object.keys(a).length!==Object.keys(t).length)return!1;for(const n in a)if(a[n]!==t[n])return!1;return!0}function I0(a){return Array.isArray(a)&&a.length===Object.keys(a).length}function xp(a){if(!B0(a))return!1;const t=a.constructor;if(t===void 0)return!0;const n=t.prototype;return!(!B0(n)||!n.hasOwnProperty("isPrototypeOf")||Object.getPrototypeOf(a)!==Object.prototype)}function B0(a){return Object.prototype.toString.call(a)==="[object Object]"}function Q1(a){return new Promise(t=>{or.setTimeout(t,a)})}function Sp(a,t,n){return typeof n.structuralSharing=="function"?n.structuralSharing(a,t):n.structuralSharing!==!1?hx(a,t):t}function Z1(a,t,n=0){const s=[...a,t];return n&&s.length>n?s.slice(1):s}function K1(a,t,n=0){const s=[t,...a];return n&&s.length>n?s.slice(0,-1):s}var Tm=Symbol();function px(a,t){return!a.queryFn&&(t!=null&&t.initialPromise)?()=>t.initialPromise:!a.queryFn||a.queryFn===Tm?()=>Promise.reject(new Error(`Missing queryFn: '${a.queryHash}'`)):a.queryFn}function mx(a,t){return typeof a=="function"?a(...t):!!a}function J1(a,t,n){let s=!1,o;return Object.defineProperty(a,"signal",{enumerable:!0,get:()=>(o??(o=t()),s||(s=!0,o.aborted?n():o.addEventListener("abort",n,{once:!0})),o)}),a}var sc=(()=>{let a=()=>q1;return{isServer(){return a()},setIsServer(t){a=t}}})();function Mp(){let a,t;const n=new Promise((o,c)=>{a=o,t=c});n.status="pending",n.catch(()=>{});function s(o){Object.assign(n,o),delete n.resolve,delete n.reject}return n.resolve=o=>{s({status:"fulfilled",value:o}),a(o)},n.reject=o=>{s({status:"rejected",reason:o}),t(o)},n}var $1=X1;function tE(){let a=[],t=0,n=d=>{d()},s=d=>{d()},o=$1;const c=d=>{t?a.push(d):o(()=>{n(d)})},f=()=>{const d=a;a=[],d.length&&o(()=>{s(()=>{d.forEach(p=>{n(p)})})})};return{batch:d=>{let p;t++;try{p=d()}finally{t--,t||f()}return p},batchCalls:d=>(...p)=>{c(()=>{d(...p)})},schedule:c,setNotifyFunction:d=>{n=d},setBatchNotifyFunction:d=>{s=d},setScheduler:d=>{o=d}}}var On=tE(),Co,xs,Ro,ix,eE=(ix=class extends mc{constructor(){super();te(this,Co,!0);te(this,xs);te(this,Ro);zt(this,Ro,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t(!0),s=()=>t(!1);return window.addEventListener("online",n,!1),window.addEventListener("offline",s,!1),()=>{window.removeEventListener("online",n),window.removeEventListener("offline",s)}}})}onSubscribe(){X(this,xs)||this.setEventListener(X(this,Ro))}onUnsubscribe(){var t;this.hasListeners()||((t=X(this,xs))==null||t.call(this),zt(this,xs,void 0))}setEventListener(t){var n;zt(this,Ro,t),(n=X(this,xs))==null||n.call(this),zt(this,xs,t(this.setOnline.bind(this)))}setOnline(t){X(this,Co)!==t&&(zt(this,Co,t),this.listeners.forEach(s=>{s(t)}))}isOnline(){return X(this,Co)}},Co=new WeakMap,xs=new WeakMap,Ro=new WeakMap,ix),ff=new eE;function nE(a){return Math.min(1e3*2**a,3e4)}function gx(a){return(a??"online")==="online"?ff.isOnline():!0}var Ep=class extends Error{constructor(a){super("CancelledError"),this.revert=a==null?void 0:a.revert,this.silent=a==null?void 0:a.silent}};function vx(a){let t=!1,n=0,s;const o=Mp(),c=()=>o.status!=="pending",f=T=>{var S;if(!c()){const y=new Ep(T);x(y),(S=a.onCancel)==null||S.call(a,y)}},d=()=>{t=!0},p=()=>{t=!1},m=()=>Em.isFocused()&&(a.networkMode==="always"||ff.isOnline())&&a.canRun(),v=()=>gx(a.networkMode)&&a.canRun(),_=T=>{c()||(s==null||s(),o.resolve(T))},x=T=>{c()||(s==null||s(),o.reject(T))},E=()=>new Promise(T=>{var S;s=y=>{(c()||m())&&T(y)},(S=a.onPause)==null||S.call(a)}).then(()=>{var T;s=void 0,c()||(T=a.onContinue)==null||T.call(a)}),M=()=>{if(c())return;let T;const S=n===0?a.initialPromise:void 0;try{T=S??a.fn()}catch(y){T=Promise.reject(y)}Promise.resolve(T).then(_).catch(y=>{var L;if(c())return;const I=a.retry??(sc.isServer()?0:3),D=a.retryDelay??nE,C=typeof D=="function"?D(n,y):D,V=I===!0||typeof I=="number"&&n<I||typeof I=="function"&&I(n,y);if(t||!V){x(y);return}n++,(L=a.onFail)==null||L.call(a,n,y),Q1(C).then(()=>m()?void 0:E()).then(()=>{t?x(y):M()})})};return{promise:o,status:()=>o.status,cancel:f,continue:()=>(s==null||s(),o),cancelRetry:d,continueRetry:p,canStart:v,start:()=>(v()?M():E().then(M),o)}}var dr,ax,_x=(ax=class{constructor(){te(this,dr)}destroy(){this.clearGcTimeout()}scheduleGc(){this.clearGcTimeout(),_p(this.gcTime)&&zt(this,dr,or.setTimeout(()=>{this.optionalRemove()},this.gcTime))}updateGcTime(a){this.gcTime=Math.max(this.gcTime||0,a??(sc.isServer()?1/0:300*1e3))}clearGcTimeout(){X(this,dr)!==void 0&&(or.clearTimeout(X(this,dr)),zt(this,dr,void 0))}},dr=new WeakMap,ax);function iE(a){return{onFetch:(t,n)=>{var v,_,x,E,M;const s=t.options,o=(x=(_=(v=t.fetchOptions)==null?void 0:v.meta)==null?void 0:_.fetchMore)==null?void 0:x.direction,c=((E=t.state.data)==null?void 0:E.pages)||[],f=((M=t.state.data)==null?void 0:M.pageParams)||[];let d={pages:[],pageParams:[]},p=0;const m=async()=>{let T=!1;const S=D=>{J1(D,()=>t.signal,()=>T=!0)},y=px(t.options,t.fetchOptions),I=async(D,C,V)=>{if(T)return Promise.reject(t.signal.reason);if(C==null&&D.pages.length)return Promise.resolve(D);const P=(()=>{const H={client:t.client,queryKey:t.queryKey,pageParam:C,direction:V?"backward":"forward",meta:t.options.meta};return S(H),H})(),G=await y(P),{maxPages:U}=t.options,N=V?K1:Z1;return{pages:N(D.pages,G,U),pageParams:N(D.pageParams,C,U)}};if(o&&c.length){const D=o==="backward",C=D?aE:F0,V={pages:c,pageParams:f},L=C(s,V);d=await I(V,L,D)}else{const D=a??c.length;do{const C=p===0?f[0]??s.initialPageParam:F0(s,d);if(p>0&&C==null)break;d=await I(d,C),p++}while(p<D)}return d};t.options.persister?t.fetchFn=()=>{var T,S;return(S=(T=t.options).persister)==null?void 0:S.call(T,m,{client:t.client,queryKey:t.queryKey,meta:t.options.meta,signal:t.signal},n)}:t.fetchFn=m}}}function F0(a,{pages:t,pageParams:n}){const s=t.length-1;return t.length>0?a.getNextPageParam(t[s],t,n[s],n):void 0}function aE(a,{pages:t,pageParams:n}){var s;return t.length>0?(s=a.getPreviousPageParam)==null?void 0:s.call(a,t[0],t,n[0],n):void 0}var wo,hr,No,Ri,pr,An,uc,mr,mi,yx,Aa,sx,sE=(sx=class extends _x{constructor(t){super();te(this,mi);te(this,wo);te(this,hr);te(this,No);te(this,Ri);te(this,pr);te(this,An);te(this,uc);te(this,mr);zt(this,mr,!1),zt(this,uc,t.defaultOptions),this.setOptions(t.options),this.observers=[],zt(this,pr,t.client),zt(this,Ri,X(this,pr).getQueryCache()),this.queryKey=t.queryKey,this.queryHash=t.queryHash,zt(this,hr,G0(this.options)),this.state=t.state??X(this,hr),this.scheduleGc()}get meta(){return this.options.meta}get queryType(){return X(this,wo)}get promise(){var t;return(t=X(this,An))==null?void 0:t.promise}setOptions(t){if(this.options={...X(this,uc),...t},t!=null&&t._type&&zt(this,wo,t._type),this.updateGcTime(this.options.gcTime),this.state&&this.state.data===void 0){const n=G0(this.options);n.data!==void 0&&(this.setState(H0(n.data,n.dataUpdatedAt)),zt(this,hr,n))}}optionalRemove(){!this.observers.length&&this.state.fetchStatus==="idle"&&X(this,Ri).remove(this)}setData(t,n){const s=Sp(this.state.data,t,this.options);return Ae(this,mi,Aa).call(this,{data:s,type:"success",dataUpdatedAt:n==null?void 0:n.updatedAt,manual:n==null?void 0:n.manual}),s}setState(t){Ae(this,mi,Aa).call(this,{type:"setState",state:t})}cancel(t){var s,o;const n=(s=X(this,An))==null?void 0:s.promise;return(o=X(this,An))==null||o.cancel(t),n?n.then(ni).catch(ni):Promise.resolve()}destroy(){super.destroy(),this.cancel({silent:!0})}get resetState(){return X(this,hr)}reset(){this.destroy(),this.setState(this.resetState)}isActive(){return this.observers.some(t=>gi(t.options.enabled,this)!==!1)}isDisabled(){return this.getObserversCount()>0?!this.isActive():this.options.queryFn===Tm||!this.isFetched()}isFetched(){return this.state.dataUpdateCount+this.state.errorUpdateCount>0}isStatic(){return this.getObserversCount()>0?this.observers.some(t=>As(t.options.staleTime,this)==="static"):!1}isStale(){return this.getObserversCount()>0?this.observers.some(t=>t.getCurrentResult().isStale):this.state.data===void 0||this.state.isInvalidated}isStaleByTime(t=0){return this.state.data===void 0?!0:t==="static"?!1:this.state.isInvalidated?!0:!dx(this.state.dataUpdatedAt,t)}onFocus(){var n;const t=this.observers.find(s=>s.shouldFetchOnWindowFocus());t==null||t.refetch({cancelRefetch:!1}),(n=X(this,An))==null||n.continue()}onOnline(){var n;const t=this.observers.find(s=>s.shouldFetchOnReconnect());t==null||t.refetch({cancelRefetch:!1}),(n=X(this,An))==null||n.continue()}addObserver(t){this.observers.includes(t)||(this.observers.push(t),this.clearGcTimeout(),X(this,Ri).notify({type:"observerAdded",query:this,observer:t}))}removeObserver(t){this.observers.includes(t)&&(this.observers=this.observers.filter(n=>n!==t),this.observers.length||(X(this,An)&&(X(this,mr)||Ae(this,mi,yx).call(this)?X(this,An).cancel({revert:!0}):X(this,An).cancelRetry()),this.scheduleGc()),X(this,Ri).notify({type:"observerRemoved",query:this,observer:t}))}getObserversCount(){return this.observers.length}invalidate(){this.state.isInvalidated||Ae(this,mi,Aa).call(this,{type:"invalidate"})}async fetch(t,n){var m,v,_,x,E,M,T,S,y,I,D;if(this.state.fetchStatus!=="idle"&&((m=X(this,An))==null?void 0:m.status())!=="rejected"){if(this.state.data!==void 0&&(n!=null&&n.cancelRefetch))this.cancel({silent:!0});else if(X(this,An))return X(this,An).continueRetry(),X(this,An).promise}if(t&&this.setOptions(t),!this.options.queryFn){const C=this.observers.find(V=>V.options.queryFn);C&&this.setOptions(C.options)}const s=new AbortController,o=C=>{Object.defineProperty(C,"signal",{enumerable:!0,get:()=>(zt(this,mr,!0),s.signal)})},c=()=>{const C=px(this.options,n),L=(()=>{const P={client:X(this,pr),queryKey:this.queryKey,meta:this.meta};return o(P),P})();return zt(this,mr,!1),this.options.persister?this.options.persister(C,L,this):C(L)},d=(()=>{const C={fetchOptions:n,options:this.options,queryKey:this.queryKey,client:X(this,pr),state:this.state,fetchFn:c};return o(C),C})(),p=X(this,wo)==="infinite"?iE(this.options.pages):this.options.behavior;p==null||p.onFetch(d,this),zt(this,No,this.state),(this.state.fetchStatus==="idle"||this.state.fetchMeta!==((v=d.fetchOptions)==null?void 0:v.meta))&&Ae(this,mi,Aa).call(this,{type:"fetch",meta:(_=d.fetchOptions)==null?void 0:_.meta}),zt(this,An,vx({initialPromise:n==null?void 0:n.initialPromise,fn:d.fetchFn,onCancel:C=>{C instanceof Ep&&C.revert&&this.setState({...X(this,No),fetchStatus:"idle"}),s.abort()},onFail:(C,V)=>{Ae(this,mi,Aa).call(this,{type:"failed",failureCount:C,error:V})},onPause:()=>{Ae(this,mi,Aa).call(this,{type:"pause"})},onContinue:()=>{Ae(this,mi,Aa).call(this,{type:"continue"})},retry:d.options.retry,retryDelay:d.options.retryDelay,networkMode:d.options.networkMode,canRun:()=>!0}));try{const C=await X(this,An).start();if(C===void 0)throw new Error(`${this.queryHash} data is undefined`);return this.setData(C),(E=(x=X(this,Ri).config).onSuccess)==null||E.call(x,C,this),(T=(M=X(this,Ri).config).onSettled)==null||T.call(M,C,this.state.error,this),C}catch(C){if(C instanceof Ep){if(C.silent)return X(this,An).promise;if(C.revert){if(this.state.data===void 0)throw C;return this.state.data}}throw Ae(this,mi,Aa).call(this,{type:"error",error:C}),(y=(S=X(this,Ri).config).onError)==null||y.call(S,C,this),(D=(I=X(this,Ri).config).onSettled)==null||D.call(I,this.state.data,C,this),C}finally{this.scheduleGc()}}},wo=new WeakMap,hr=new WeakMap,No=new WeakMap,Ri=new WeakMap,pr=new WeakMap,An=new WeakMap,uc=new WeakMap,mr=new WeakMap,mi=new WeakSet,yx=function(){return this.state.fetchStatus==="paused"&&this.state.status==="pending"},Aa=function(t){const n=s=>{switch(t.type){case"failed":return{...s,fetchFailureCount:t.failureCount,fetchFailureReason:t.error};case"pause":return{...s,fetchStatus:"paused"};case"continue":return{...s,fetchStatus:"fetching"};case"fetch":return{...s,...xx(s.data,this.options),fetchMeta:t.meta??null};case"success":const o={...s,...H0(t.data,t.dataUpdatedAt),dataUpdateCount:s.dataUpdateCount+1,...!t.manual&&{fetchStatus:"idle",fetchFailureCount:0,fetchFailureReason:null}};return zt(this,No,t.manual?o:void 0),o;case"error":const c=t.error;return{...s,error:c,errorUpdateCount:s.errorUpdateCount+1,errorUpdatedAt:Date.now(),fetchFailureCount:s.fetchFailureCount+1,fetchFailureReason:c,fetchStatus:"idle",status:"error",isInvalidated:!0};case"invalidate":return{...s,isInvalidated:!0};case"setState":return{...s,...t.state}}};this.state=n(this.state),On.batch(()=>{this.observers.forEach(s=>{s.onQueryUpdate()}),X(this,Ri).notify({query:this,type:"updated",action:t})})},sx);function xx(a,t){return{fetchFailureCount:0,fetchFailureReason:null,fetchStatus:gx(t.networkMode)?"fetching":"paused",...a===void 0&&{error:null,status:"pending"}}}function H0(a,t){return{data:a,dataUpdatedAt:t??Date.now(),error:null,isInvalidated:!1,status:"success"}}function G0(a){const t=typeof a.initialData=="function"?a.initialData():a.initialData,n=t!==void 0,s=n?typeof a.initialDataUpdatedAt=="function"?a.initialDataUpdatedAt():a.initialDataUpdatedAt:0;return{data:t,dataUpdateCount:0,dataUpdatedAt:n?s??Date.now():0,error:null,errorUpdateCount:0,errorUpdatedAt:0,fetchFailureCount:0,fetchFailureReason:null,fetchMeta:null,isInvalidated:!1,status:n?"success":"pending",fetchStatus:"idle"}}var ei,Re,fc,qn,gr,Do,Ra,Ss,dc,Uo,Lo,vr,_r,Ms,Oo,Ie,Zl,bp,Tp,Ap,Cp,Rp,wp,Np,Sx,rx,rE=(rx=class extends mc{constructor(t,n){super();te(this,Ie);te(this,ei);te(this,Re);te(this,fc);te(this,qn);te(this,gr);te(this,Do);te(this,Ra);te(this,Ss);te(this,dc);te(this,Uo);te(this,Lo);te(this,vr);te(this,_r);te(this,Ms);te(this,Oo,new Set);this.options=n,zt(this,ei,t),zt(this,Ss,null),zt(this,Ra,Mp()),this.bindMethods(),this.setOptions(n)}bindMethods(){this.refetch=this.refetch.bind(this)}onSubscribe(){this.listeners.size===1&&(X(this,Re).addObserver(this),V0(X(this,Re),this.options)?Ae(this,Ie,Zl).call(this):this.updateResult(),Ae(this,Ie,Cp).call(this))}onUnsubscribe(){this.hasListeners()||this.destroy()}shouldFetchOnReconnect(){return Dp(X(this,Re),this.options,this.options.refetchOnReconnect)}shouldFetchOnWindowFocus(){return Dp(X(this,Re),this.options,this.options.refetchOnWindowFocus)}destroy(){this.listeners=new Set,Ae(this,Ie,Rp).call(this),Ae(this,Ie,wp).call(this),X(this,Re).removeObserver(this)}setOptions(t){const n=this.options,s=X(this,Re);if(this.options=X(this,ei).defaultQueryOptions(t),this.options.enabled!==void 0&&typeof this.options.enabled!="boolean"&&typeof this.options.enabled!="function"&&typeof gi(this.options.enabled,X(this,Re))!="boolean")throw new Error("Expected enabled to be a boolean or a callback that returns a boolean");Ae(this,Ie,Np).call(this),X(this,Re).setOptions(this.options),n._defaulted&&!yp(this.options,n)&&X(this,ei).getQueryCache().notify({type:"observerOptionsUpdated",query:X(this,Re),observer:this});const o=this.hasListeners();o&&j0(X(this,Re),s,this.options,n)&&Ae(this,Ie,Zl).call(this),this.updateResult(),o&&(X(this,Re)!==s||gi(this.options.enabled,X(this,Re))!==gi(n.enabled,X(this,Re))||As(this.options.staleTime,X(this,Re))!==As(n.staleTime,X(this,Re)))&&Ae(this,Ie,bp).call(this);const c=Ae(this,Ie,Tp).call(this);o&&(X(this,Re)!==s||gi(this.options.enabled,X(this,Re))!==gi(n.enabled,X(this,Re))||c!==X(this,Ms))&&Ae(this,Ie,Ap).call(this,c)}getOptimisticResult(t){const n=X(this,ei).getQueryCache().build(X(this,ei),t),s=this.createResult(n,t);return lE(this,s)&&(zt(this,qn,s),zt(this,Do,this.options),zt(this,gr,X(this,Re).state)),s}getCurrentResult(){return X(this,qn)}trackResult(t,n){return new Proxy(t,{get:(s,o)=>(this.trackProp(o),n==null||n(o),o==="promise"&&(this.trackProp("data"),!this.options.experimental_prefetchInRender&&X(this,Ra).status==="pending"&&X(this,Ra).reject(new Error("experimental_prefetchInRender feature flag is not enabled"))),Reflect.get(s,o))})}trackProp(t){X(this,Oo).add(t)}getCurrentQuery(){return X(this,Re)}refetch({...t}={}){return this.fetch({...t})}fetchOptimistic(t){const n=X(this,ei).defaultQueryOptions(t),s=X(this,ei).getQueryCache().build(X(this,ei),n);return s.fetch().then(()=>this.createResult(s,n))}fetch(t){return Ae(this,Ie,Zl).call(this,{...t,cancelRefetch:t.cancelRefetch??!0}).then(()=>(this.updateResult(),X(this,qn)))}createResult(t,n){var U;const s=X(this,Re),o=this.options,c=X(this,qn),f=X(this,gr),d=X(this,Do),m=t!==s?t.state:X(this,fc),{state:v}=t;let _={...v},x=!1,E;if(n._optimisticResults){const N=this.hasListeners(),H=!N&&V0(t,n),ut=N&&j0(t,s,n,o);(H||ut)&&(_={..._,...xx(v.data,t.options)}),n._optimisticResults==="isRestoring"&&(_.fetchStatus="idle")}let{error:M,errorUpdatedAt:T,status:S}=_;E=_.data;let y=!1;if(n.placeholderData!==void 0&&E===void 0&&S==="pending"){let N;c!=null&&c.isPlaceholderData&&n.placeholderData===(d==null?void 0:d.placeholderData)?(N=c.data,y=!0):N=typeof n.placeholderData=="function"?n.placeholderData((U=X(this,Lo))==null?void 0:U.state.data,X(this,Lo)):n.placeholderData,N!==void 0&&(S="success",E=Sp(c==null?void 0:c.data,N,n),x=!0)}if(n.select&&E!==void 0&&!y)if(c&&E===(f==null?void 0:f.data)&&n.select===X(this,dc))E=X(this,Uo);else try{zt(this,dc,n.select),E=n.select(E),E=Sp(c==null?void 0:c.data,E,n),zt(this,Uo,E),zt(this,Ss,null)}catch(N){zt(this,Ss,N)}X(this,Ss)&&(M=X(this,Ss),E=X(this,Uo),T=Date.now(),S="error");const I=_.fetchStatus==="fetching",D=S==="pending",C=S==="error",V=D&&I,L=E!==void 0,G={status:S,fetchStatus:_.fetchStatus,isPending:D,isSuccess:S==="success",isError:C,isInitialLoading:V,isLoading:V,data:E,dataUpdatedAt:_.dataUpdatedAt,error:M,errorUpdatedAt:T,failureCount:_.fetchFailureCount,failureReason:_.fetchFailureReason,errorUpdateCount:_.errorUpdateCount,isFetched:t.isFetched(),isFetchedAfterMount:_.dataUpdateCount>m.dataUpdateCount||_.errorUpdateCount>m.errorUpdateCount,isFetching:I,isRefetching:I&&!D,isLoadingError:C&&!L,isPaused:_.fetchStatus==="paused",isPlaceholderData:x,isRefetchError:C&&L,isStale:Am(t,n),refetch:this.refetch,promise:X(this,Ra),isEnabled:gi(n.enabled,t)!==!1};if(this.options.experimental_prefetchInRender){const N=G.data!==void 0,H=G.status==="error"&&!N,ut=ct=>{H?ct.reject(G.error):N&&ct.resolve(G.data)},ot=()=>{const ct=zt(this,Ra,G.promise=Mp());ut(ct)},mt=X(this,Ra);switch(mt.status){case"pending":t.queryHash===s.queryHash&&ut(mt);break;case"fulfilled":(H||G.data!==mt.value)&&ot();break;case"rejected":(!H||G.error!==mt.reason)&&ot();break}}return G}updateResult(){const t=X(this,qn),n=this.createResult(X(this,Re),this.options);if(zt(this,gr,X(this,Re).state),zt(this,Do,this.options),X(this,gr).data!==void 0&&zt(this,Lo,X(this,Re)),yp(n,t))return;zt(this,qn,n);const s=()=>{if(!t)return!0;const{notifyOnChangeProps:o}=this.options,c=typeof o=="function"?o():o;if(c==="all"||!c&&!X(this,Oo).size)return!0;const f=new Set(c??X(this,Oo));return this.options.throwOnError&&f.add("error"),Object.keys(X(this,qn)).some(d=>{const p=d;return X(this,qn)[p]!==t[p]&&f.has(p)})};Ae(this,Ie,Sx).call(this,{listeners:s()})}onQueryUpdate(){this.updateResult(),this.hasListeners()&&Ae(this,Ie,Cp).call(this)}},ei=new WeakMap,Re=new WeakMap,fc=new WeakMap,qn=new WeakMap,gr=new WeakMap,Do=new WeakMap,Ra=new WeakMap,Ss=new WeakMap,dc=new WeakMap,Uo=new WeakMap,Lo=new WeakMap,vr=new WeakMap,_r=new WeakMap,Ms=new WeakMap,Oo=new WeakMap,Ie=new WeakSet,Zl=function(t){Ae(this,Ie,Np).call(this);let n=X(this,Re).fetch(this.options,t);return t!=null&&t.throwOnError||(n=n.catch(ni)),n},bp=function(){Ae(this,Ie,Rp).call(this);const t=As(this.options.staleTime,X(this,Re));if(sc.isServer()||X(this,qn).isStale||!_p(t))return;const s=dx(X(this,qn).dataUpdatedAt,t)+1;zt(this,vr,or.setTimeout(()=>{X(this,qn).isStale||this.updateResult()},s))},Tp=function(){return(typeof this.options.refetchInterval=="function"?this.options.refetchInterval(X(this,Re)):this.options.refetchInterval)??!1},Ap=function(t){Ae(this,Ie,wp).call(this),zt(this,Ms,t),!(sc.isServer()||gi(this.options.enabled,X(this,Re))===!1||!_p(X(this,Ms))||X(this,Ms)===0)&&zt(this,_r,or.setInterval(()=>{(this.options.refetchIntervalInBackground||Em.isFocused())&&Ae(this,Ie,Zl).call(this)},X(this,Ms)))},Cp=function(){Ae(this,Ie,bp).call(this),Ae(this,Ie,Ap).call(this,Ae(this,Ie,Tp).call(this))},Rp=function(){X(this,vr)!==void 0&&(or.clearTimeout(X(this,vr)),zt(this,vr,void 0))},wp=function(){X(this,_r)!==void 0&&(or.clearInterval(X(this,_r)),zt(this,_r,void 0))},Np=function(){const t=X(this,ei).getQueryCache().build(X(this,ei),this.options);if(t===X(this,Re))return;const n=X(this,Re);zt(this,Re,t),zt(this,fc,t.state),this.hasListeners()&&(n==null||n.removeObserver(this),t.addObserver(this))},Sx=function(t){On.batch(()=>{t.listeners&&this.listeners.forEach(n=>{n(X(this,qn))}),X(this,ei).getQueryCache().notify({query:X(this,Re),type:"observerResultsUpdated"})})},rx);function oE(a,t){return gi(t.enabled,a)!==!1&&a.state.data===void 0&&!(a.state.status==="error"&&gi(t.retryOnMount,a)===!1)}function V0(a,t){return oE(a,t)||a.state.data!==void 0&&Dp(a,t,t.refetchOnMount)}function Dp(a,t,n){if(gi(t.enabled,a)!==!1&&As(t.staleTime,a)!=="static"){const s=typeof n=="function"?n(a):n;return s==="always"||s!==!1&&Am(a,t)}return!1}function j0(a,t,n,s){return(a!==t||gi(s.enabled,a)===!1)&&(!n.suspense||a.state.status!=="error")&&Am(a,n)}function Am(a,t){return gi(t.enabled,a)!==!1&&a.isStaleByTime(As(t.staleTime,a))}function lE(a,t){return!yp(a.getCurrentResult(),t)}var hc,Qi,Hn,yr,Zi,gs,ox,cE=(ox=class extends _x{constructor(t){super();te(this,Zi);te(this,hc);te(this,Qi);te(this,Hn);te(this,yr);zt(this,hc,t.client),this.mutationId=t.mutationId,zt(this,Hn,t.mutationCache),zt(this,Qi,[]),this.state=t.state||uE(),this.setOptions(t.options),this.scheduleGc()}setOptions(t){this.options=t,this.updateGcTime(this.options.gcTime)}get meta(){return this.options.meta}addObserver(t){X(this,Qi).includes(t)||(X(this,Qi).push(t),this.clearGcTimeout(),X(this,Hn).notify({type:"observerAdded",mutation:this,observer:t}))}removeObserver(t){zt(this,Qi,X(this,Qi).filter(n=>n!==t)),this.scheduleGc(),X(this,Hn).notify({type:"observerRemoved",mutation:this,observer:t})}optionalRemove(){X(this,Qi).length||(this.state.status==="pending"?this.scheduleGc():X(this,Hn).remove(this))}continue(){var t;return((t=X(this,yr))==null?void 0:t.continue())??this.execute(this.state.variables)}async execute(t){var f,d,p,m,v,_,x,E,M,T,S,y,I,D,C,V,L,P;const n=()=>{Ae(this,Zi,gs).call(this,{type:"continue"})},s={client:X(this,hc),meta:this.options.meta,mutationKey:this.options.mutationKey};zt(this,yr,vx({fn:()=>this.options.mutationFn?this.options.mutationFn(t,s):Promise.reject(new Error("No mutationFn found")),onFail:(G,U)=>{Ae(this,Zi,gs).call(this,{type:"failed",failureCount:G,error:U})},onPause:()=>{Ae(this,Zi,gs).call(this,{type:"pause"})},onContinue:n,retry:this.options.retry??0,retryDelay:this.options.retryDelay,networkMode:this.options.networkMode,canRun:()=>X(this,Hn).canRun(this)}));const o=this.state.status==="pending",c=!X(this,yr).canStart();try{if(o)n();else{Ae(this,Zi,gs).call(this,{type:"pending",variables:t,isPaused:c}),X(this,Hn).config.onMutate&&await X(this,Hn).config.onMutate(t,this,s);const U=await((d=(f=this.options).onMutate)==null?void 0:d.call(f,t,s));U!==this.state.context&&Ae(this,Zi,gs).call(this,{type:"pending",context:U,variables:t,isPaused:c})}const G=await X(this,yr).start();return await((m=(p=X(this,Hn).config).onSuccess)==null?void 0:m.call(p,G,t,this.state.context,this,s)),await((_=(v=this.options).onSuccess)==null?void 0:_.call(v,G,t,this.state.context,s)),await((E=(x=X(this,Hn).config).onSettled)==null?void 0:E.call(x,G,null,this.state.variables,this.state.context,this,s)),await((T=(M=this.options).onSettled)==null?void 0:T.call(M,G,null,t,this.state.context,s)),Ae(this,Zi,gs).call(this,{type:"success",data:G}),G}catch(G){try{await((y=(S=X(this,Hn).config).onError)==null?void 0:y.call(S,G,t,this.state.context,this,s))}catch(U){Promise.reject(U)}try{await((D=(I=this.options).onError)==null?void 0:D.call(I,G,t,this.state.context,s))}catch(U){Promise.reject(U)}try{await((V=(C=X(this,Hn).config).onSettled)==null?void 0:V.call(C,void 0,G,this.state.variables,this.state.context,this,s))}catch(U){Promise.reject(U)}try{await((P=(L=this.options).onSettled)==null?void 0:P.call(L,void 0,G,t,this.state.context,s))}catch(U){Promise.reject(U)}throw Ae(this,Zi,gs).call(this,{type:"error",error:G}),G}finally{X(this,Hn).runNext(this)}}},hc=new WeakMap,Qi=new WeakMap,Hn=new WeakMap,yr=new WeakMap,Zi=new WeakSet,gs=function(t){const n=s=>{switch(t.type){case"failed":return{...s,failureCount:t.failureCount,failureReason:t.error};case"pause":return{...s,isPaused:!0};case"continue":return{...s,isPaused:!1};case"pending":return{...s,context:t.context,data:void 0,failureCount:0,failureReason:null,error:null,isPaused:t.isPaused,status:"pending",variables:t.variables,submittedAt:Date.now()};case"success":return{...s,data:t.data,failureCount:0,failureReason:null,error:null,status:"success",isPaused:!1};case"error":return{...s,data:void 0,error:t.error,failureCount:s.failureCount+1,failureReason:t.error,isPaused:!1,status:"error"}}};this.state=n(this.state),On.batch(()=>{X(this,Qi).forEach(s=>{s.onMutationUpdate(t)}),X(this,Hn).notify({mutation:this,type:"updated",action:t})})},ox);function uE(){return{context:void 0,data:void 0,error:null,failureCount:0,failureReason:null,isPaused:!1,status:"idle",variables:void 0,submittedAt:0}}var wa,Ii,pc,lx,fE=(lx=class extends mc{constructor(t={}){super();te(this,wa);te(this,Ii);te(this,pc);this.config=t,zt(this,wa,new Set),zt(this,Ii,new Map),zt(this,pc,0)}build(t,n,s){const o=new cE({client:t,mutationCache:this,mutationId:++Nu(this,pc)._,options:t.defaultMutationOptions(n),state:s});return this.add(o),o}add(t){X(this,wa).add(t);const n=Du(t);if(typeof n=="string"){const s=X(this,Ii).get(n);s?s.push(t):X(this,Ii).set(n,[t])}this.notify({type:"added",mutation:t})}remove(t){if(X(this,wa).delete(t)){const n=Du(t);if(typeof n=="string"){const s=X(this,Ii).get(n);if(s)if(s.length>1){const o=s.indexOf(t);o!==-1&&s.splice(o,1)}else s[0]===t&&X(this,Ii).delete(n)}}this.notify({type:"removed",mutation:t})}canRun(t){const n=Du(t);if(typeof n=="string"){const s=X(this,Ii).get(n),o=s==null?void 0:s.find(c=>c.state.status==="pending");return!o||o===t}else return!0}runNext(t){var s;const n=Du(t);if(typeof n=="string"){const o=(s=X(this,Ii).get(n))==null?void 0:s.find(c=>c!==t&&c.state.isPaused);return(o==null?void 0:o.continue())??Promise.resolve()}else return Promise.resolve()}clear(){On.batch(()=>{X(this,wa).forEach(t=>{this.notify({type:"removed",mutation:t})}),X(this,wa).clear(),X(this,Ii).clear()})}getAll(){return Array.from(X(this,wa))}find(t){const n={exact:!0,...t};return this.getAll().find(s=>z0(n,s))}findAll(t={}){return this.getAll().filter(n=>z0(t,n))}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}resumePausedMutations(){const t=this.getAll().filter(n=>n.state.isPaused);return On.batch(()=>Promise.all(t.map(n=>n.continue().catch(ni))))}},wa=new WeakMap,Ii=new WeakMap,pc=new WeakMap,lx);function Du(a){var t;return(t=a.options.scope)==null?void 0:t.id}var Ki,cx,dE=(cx=class extends mc{constructor(t={}){super();te(this,Ki);this.config=t,zt(this,Ki,new Map)}build(t,n,s){const o=n.queryKey,c=n.queryHash??bm(o,n);let f=this.get(c);return f||(f=new sE({client:t,queryKey:o,queryHash:c,options:t.defaultQueryOptions(n),state:s,defaultOptions:t.getQueryDefaults(o)}),this.add(f)),f}add(t){X(this,Ki).has(t.queryHash)||(X(this,Ki).set(t.queryHash,t),this.notify({type:"added",query:t}))}remove(t){const n=X(this,Ki).get(t.queryHash);n&&(t.destroy(),n===t&&X(this,Ki).delete(t.queryHash),this.notify({type:"removed",query:t}))}clear(){On.batch(()=>{this.getAll().forEach(t=>{this.remove(t)})})}get(t){return X(this,Ki).get(t)}getAll(){return[...X(this,Ki).values()]}find(t){const n={exact:!0,...t};return this.getAll().find(s=>P0(n,s))}findAll(t={}){const n=this.getAll();return Object.keys(t).length>0?n.filter(s=>P0(t,s)):n}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}onFocus(){On.batch(()=>{this.getAll().forEach(t=>{t.onFocus()})})}onOnline(){On.batch(()=>{this.getAll().forEach(t=>{t.onOnline()})})}},Ki=new WeakMap,cx),ln,Es,bs,Po,zo,Ts,Io,Bo,ux,hE=(ux=class{constructor(a={}){te(this,ln);te(this,Es);te(this,bs);te(this,Po);te(this,zo);te(this,Ts);te(this,Io);te(this,Bo);zt(this,ln,a.queryCache||new dE),zt(this,Es,a.mutationCache||new fE),zt(this,bs,a.defaultOptions||{}),zt(this,Po,new Map),zt(this,zo,new Map),zt(this,Ts,0)}mount(){Nu(this,Ts)._++,X(this,Ts)===1&&(zt(this,Io,Em.subscribe(async a=>{a&&(await this.resumePausedMutations(),X(this,ln).onFocus())})),zt(this,Bo,ff.subscribe(async a=>{a&&(await this.resumePausedMutations(),X(this,ln).onOnline())})))}unmount(){var a,t;Nu(this,Ts)._--,X(this,Ts)===0&&((a=X(this,Io))==null||a.call(this),zt(this,Io,void 0),(t=X(this,Bo))==null||t.call(this),zt(this,Bo,void 0))}isFetching(a){return X(this,ln).findAll({...a,fetchStatus:"fetching"}).length}isMutating(a){return X(this,Es).findAll({...a,status:"pending"}).length}getQueryData(a){var n;const t=this.defaultQueryOptions({queryKey:a});return(n=X(this,ln).get(t.queryHash))==null?void 0:n.state.data}ensureQueryData(a){const t=this.defaultQueryOptions(a),n=X(this,ln).build(this,t),s=n.state.data;return s===void 0?this.fetchQuery(a):(a.revalidateIfStale&&n.isStaleByTime(As(t.staleTime,n))&&this.prefetchQuery(t),Promise.resolve(s))}getQueriesData(a){return X(this,ln).findAll(a).map(({queryKey:t,state:n})=>{const s=n.data;return[t,s]})}setQueryData(a,t,n){const s=this.defaultQueryOptions({queryKey:a}),o=X(this,ln).get(s.queryHash),c=o==null?void 0:o.state.data,f=W1(t,c);if(f!==void 0)return X(this,ln).build(this,s).setData(f,{...n,manual:!0})}setQueriesData(a,t,n){return On.batch(()=>X(this,ln).findAll(a).map(({queryKey:s})=>[s,this.setQueryData(s,t,n)]))}getQueryState(a){var n;const t=this.defaultQueryOptions({queryKey:a});return(n=X(this,ln).get(t.queryHash))==null?void 0:n.state}removeQueries(a){const t=X(this,ln);On.batch(()=>{t.findAll(a).forEach(n=>{t.remove(n)})})}resetQueries(a,t){const n=X(this,ln);return On.batch(()=>(n.findAll(a).forEach(s=>{s.reset()}),this.refetchQueries({type:"active",...a},t)))}cancelQueries(a,t={}){const n={revert:!0,...t},s=On.batch(()=>X(this,ln).findAll(a).map(o=>o.cancel(n)));return Promise.all(s).then(ni).catch(ni)}invalidateQueries(a,t={}){return On.batch(()=>(X(this,ln).findAll(a).forEach(n=>{n.invalidate()}),(a==null?void 0:a.refetchType)==="none"?Promise.resolve():this.refetchQueries({...a,type:(a==null?void 0:a.refetchType)??(a==null?void 0:a.type)??"active"},t)))}refetchQueries(a,t={}){const n={...t,cancelRefetch:t.cancelRefetch??!0},s=On.batch(()=>X(this,ln).findAll(a).filter(o=>!o.isDisabled()&&!o.isStatic()).map(o=>{let c=o.fetch(void 0,n);return n.throwOnError||(c=c.catch(ni)),o.state.fetchStatus==="paused"?Promise.resolve():c}));return Promise.all(s).then(ni)}fetchQuery(a){const t=this.defaultQueryOptions(a);t.retry===void 0&&(t.retry=!1);const n=X(this,ln).build(this,t);return n.isStaleByTime(As(t.staleTime,n))?n.fetch(t):Promise.resolve(n.state.data)}prefetchQuery(a){return this.fetchQuery(a).then(ni).catch(ni)}fetchInfiniteQuery(a){return a._type="infinite",this.fetchQuery(a)}prefetchInfiniteQuery(a){return this.fetchInfiniteQuery(a).then(ni).catch(ni)}ensureInfiniteQueryData(a){return a._type="infinite",this.ensureQueryData(a)}resumePausedMutations(){return ff.isOnline()?X(this,Es).resumePausedMutations():Promise.resolve()}getQueryCache(){return X(this,ln)}getMutationCache(){return X(this,Es)}getDefaultOptions(){return X(this,bs)}setDefaultOptions(a){zt(this,bs,a)}setQueryDefaults(a,t){X(this,Po).set(ic(a),{queryKey:a,defaultOptions:t})}getQueryDefaults(a){const t=[...X(this,Po).values()],n={};return t.forEach(s=>{ac(a,s.queryKey)&&Object.assign(n,s.defaultOptions)}),n}setMutationDefaults(a,t){X(this,zo).set(ic(a),{mutationKey:a,defaultOptions:t})}getMutationDefaults(a){const t=[...X(this,zo).values()],n={};return t.forEach(s=>{ac(a,s.mutationKey)&&Object.assign(n,s.defaultOptions)}),n}defaultQueryOptions(a){if(a._defaulted)return a;const t={...X(this,bs).queries,...this.getQueryDefaults(a.queryKey),...a,_defaulted:!0};return t.queryHash||(t.queryHash=bm(t.queryKey,t)),t.refetchOnReconnect===void 0&&(t.refetchOnReconnect=t.networkMode!=="always"),t.throwOnError===void 0&&(t.throwOnError=!!t.suspense),!t.networkMode&&t.persister&&(t.networkMode="offlineFirst"),t.queryFn===Tm&&(t.enabled=!1),t}defaultMutationOptions(a){return a!=null&&a._defaulted?a:{...X(this,bs).mutations,...(a==null?void 0:a.mutationKey)&&this.getMutationDefaults(a.mutationKey),...a,_defaulted:!0}}clear(){X(this,ln).clear(),X(this,Es).clear()}},ln=new WeakMap,Es=new WeakMap,bs=new WeakMap,Po=new WeakMap,zo=new WeakMap,Ts=new WeakMap,Io=new WeakMap,Bo=new WeakMap,ux),Mx=se.createContext(void 0),Ex=a=>{const t=se.useContext(Mx);if(!t)throw new Error("No QueryClient set, use QueryClientProvider to set one");return t},pE=({client:a,children:t})=>(se.useEffect(()=>(a.mount(),()=>{a.unmount()}),[a]),g.jsx(Mx.Provider,{value:a,children:t})),bx=se.createContext(!1),mE=()=>se.useContext(bx);bx.Provider;function gE(){let a=!1;return{clearReset:()=>{a=!1},reset:()=>{a=!0},isReset:()=>a}}var vE=se.createContext(gE()),_E=()=>se.useContext(vE),yE=(a,t,n)=>{const s=n!=null&&n.state.error&&typeof a.throwOnError=="function"?mx(a.throwOnError,[n.state.error,n]):a.throwOnError;(a.suspense||a.experimental_prefetchInRender||s)&&(t.isReset()||(a.retryOnMount=!1))},xE=a=>{se.useEffect(()=>{a.clearReset()},[a])},SE=({result:a,errorResetBoundary:t,throwOnError:n,query:s,suspense:o})=>a.isError&&!t.isReset()&&!a.isFetching&&s&&(o&&a.data===void 0||mx(n,[a.error,s])),ME=a=>{if(a.suspense){const n=o=>o==="static"?o:Math.max(o??1e3,1e3),s=a.staleTime;a.staleTime=typeof s=="function"?(...o)=>n(s(...o)):n(s),typeof a.gcTime=="number"&&(a.gcTime=Math.max(a.gcTime,1e3))}},EE=(a,t)=>a.isLoading&&a.isFetching&&!t,bE=(a,t)=>(a==null?void 0:a.suspense)&&t.isPending,k0=(a,t,n)=>t.fetchOptimistic(a).catch(()=>{n.clearReset()});function TE(a,t,n){var E,M,T,S;const s=mE(),o=_E(),c=Ex(),f=c.defaultQueryOptions(a);(M=(E=c.getDefaultOptions().queries)==null?void 0:E._experimental_beforeQuery)==null||M.call(E,f);const d=c.getQueryCache().get(f.queryHash),p=a.subscribed!==!1;f._optimisticResults=s?"isRestoring":p?"optimistic":void 0,ME(f),yE(f,o,d),xE(o);const m=!c.getQueryCache().get(f.queryHash),[v]=se.useState(()=>new t(c,f)),_=v.getOptimisticResult(f),x=!s&&p;if(se.useSyncExternalStore(se.useCallback(y=>{const I=x?v.subscribe(On.batchCalls(y)):ni;return v.updateResult(),I},[v,x]),()=>v.getCurrentResult(),()=>v.getCurrentResult()),se.useEffect(()=>{v.setOptions(f)},[f,v]),bE(f,_))throw k0(f,v,o);if(SE({result:_,errorResetBoundary:o,throwOnError:f.throwOnError,query:d,suspense:f.suspense}))throw _.error;if((S=(T=c.getDefaultOptions().queries)==null?void 0:T._experimental_afterQuery)==null||S.call(T,f,_),f.experimental_prefetchInRender&&!sc.isServer()&&EE(_,s)){const y=m?k0(f,v,o):d==null?void 0:d.promise;y==null||y.catch(ni).finally(()=>{v.updateResult()})}return f.notifyOnChangeProps?_:v.trackResult(_)}function AE(a,t){return TE(a,rE)}/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const CE=a=>a.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),Tx=(...a)=>a.filter((t,n,s)=>!!t&&t.trim()!==""&&s.indexOf(t)===n).join(" ").trim();/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var RE={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wE=se.forwardRef(({color:a="currentColor",size:t=24,strokeWidth:n=2,absoluteStrokeWidth:s,className:o="",children:c,iconNode:f,...d},p)=>se.createElement("svg",{ref:p,...RE,width:t,height:t,stroke:a,strokeWidth:s?Number(n)*24/Number(t):n,className:Tx("lucide",o),...d},[...f.map(([m,v])=>se.createElement(m,v)),...Array.isArray(c)?c:[c]]));/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const we=(a,t)=>{const n=se.forwardRef(({className:s,...o},c)=>se.createElement(wE,{ref:c,iconNode:t,className:Tx(`lucide-${CE(a)}`,s),...o}));return n.displayName=`${a}`,n};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Up=we("Activity",[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const NE=we("Archive",[["rect",{width:"20",height:"5",x:"2",y:"3",rx:"1",key:"1wp1u1"}],["path",{d:"M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8",key:"1s80jp"}],["path",{d:"M10 12h4",key:"a56b0p"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ax=we("Bell",[["path",{d:"M10.268 21a2 2 0 0 0 3.464 0",key:"vwvbt9"}],["path",{d:"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",key:"11g9vi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Cx=we("BrainCircuit",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M9 13a4.5 4.5 0 0 0 3-4",key:"10igwf"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M12 13h4",key:"1ku699"}],["path",{d:"M12 18h6a2 2 0 0 1 2 2v1",key:"105ag5"}],["path",{d:"M12 8h8",key:"1lhi5i"}],["path",{d:"M16 8V5a2 2 0 0 1 2-2",key:"u6izg6"}],["circle",{cx:"16",cy:"13",r:".5",key:"ry7gng"}],["circle",{cx:"18",cy:"3",r:".5",key:"1aiba7"}],["circle",{cx:"20",cy:"21",r:".5",key:"yhc1fs"}],["circle",{cx:"20",cy:"8",r:".5",key:"1e43v0"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const X0=we("Brain",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z",key:"ep3f8r"}],["path",{d:"M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4",key:"1p4c4q"}],["path",{d:"M17.599 6.5a3 3 0 0 0 .399-1.375",key:"tmeiqw"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M19.938 10.5a4 4 0 0 1 .585.396",key:"1qfode"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M19.967 17.484A4 4 0 0 1 18 18",key:"159ez6"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const DE=we("Check",[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const UE=we("CircleCheck",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const LE=we("CircleOff",[["path",{d:"m2 2 20 20",key:"1ooewy"}],["path",{d:"M8.35 2.69A10 10 0 0 1 21.3 15.65",key:"1pfsoa"}],["path",{d:"M19.08 19.08A10 10 0 1 1 4.92 4.92",key:"1ablyi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const OE=we("CirclePause",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"10",x2:"10",y1:"15",y2:"9",key:"c1nkhi"}],["line",{x1:"14",x2:"14",y1:"15",y2:"9",key:"h65svq"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const PE=we("ClipboardList",[["rect",{width:"8",height:"4",x:"8",y:"2",rx:"1",ry:"1",key:"tgr4d6"}],["path",{d:"M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",key:"116196"}],["path",{d:"M12 11h4",key:"1jrz19"}],["path",{d:"M12 16h4",key:"n85exb"}],["path",{d:"M8 11h.01",key:"1dfujw"}],["path",{d:"M8 16h.01",key:"18s6g9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zE=we("Clock",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["polyline",{points:"12 6 12 12 16 14",key:"68esgv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const IE=we("CodeXml",[["path",{d:"m18 16 4-4-4-4",key:"1inbqp"}],["path",{d:"m6 8-4 4 4 4",key:"15zrgr"}],["path",{d:"m14.5 4-5 16",key:"e7oirm"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const BE=we("Cpu",[["rect",{width:"16",height:"16",x:"4",y:"4",rx:"2",key:"14l7u7"}],["rect",{width:"6",height:"6",x:"9",y:"9",rx:"1",key:"5aljv4"}],["path",{d:"M15 2v2",key:"13l42r"}],["path",{d:"M15 20v2",key:"15mkzm"}],["path",{d:"M2 15h2",key:"1gxd5l"}],["path",{d:"M2 9h2",key:"1bbxkp"}],["path",{d:"M20 15h2",key:"19e6y8"}],["path",{d:"M20 9h2",key:"19tzq7"}],["path",{d:"M9 2v2",key:"165o2o"}],["path",{d:"M9 20v2",key:"i2bqo8"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const FE=we("DatabaseBackup",[["ellipse",{cx:"12",cy:"5",rx:"9",ry:"3",key:"msslwz"}],["path",{d:"M3 12a9 3 0 0 0 5 2.69",key:"1ui2ym"}],["path",{d:"M21 9.3V5",key:"6k6cib"}],["path",{d:"M3 5v14a9 3 0 0 0 6.47 2.88",key:"i62tjy"}],["path",{d:"M12 12v4h4",key:"1bxaet"}],["path",{d:"M13 20a5 5 0 0 0 9-3 4.5 4.5 0 0 0-4.5-4.5c-1.33 0-2.54.54-3.41 1.41L12 16",key:"1f4ei9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const HE=we("Eye",[["path",{d:"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",key:"1nclc0"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const GE=we("House",[["path",{d:"M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8",key:"5wwlr5"}],["path",{d:"M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"1d0kgt"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const VE=we("KeyRound",[["path",{d:"M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",key:"1s6t7t"}],["circle",{cx:"16.5",cy:"7.5",r:".5",fill:"currentColor",key:"w0ekpg"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q0=we("LockKeyhole",[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jE=we("Lock",[["rect",{width:"18",height:"11",x:"3",y:"11",rx:"2",ry:"2",key:"1w4ew1"}],["path",{d:"M7 11V7a5 5 0 0 1 10 0v4",key:"fwvmzm"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Rx=we("MessageSquare",[["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",key:"1lielz"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wx=we("MonitorCog",[["path",{d:"M12 17v4",key:"1riwvh"}],["path",{d:"m15.2 4.9-.9-.4",key:"12wd2u"}],["path",{d:"m15.2 7.1-.9.4",key:"1r2vl7"}],["path",{d:"m16.9 3.2-.4-.9",key:"3zbo91"}],["path",{d:"m16.9 8.8-.4.9",key:"1qr2dn"}],["path",{d:"m19.5 2.3-.4.9",key:"1rjrkq"}],["path",{d:"m19.5 9.7-.4-.9",key:"heryx5"}],["path",{d:"m21.7 4.5-.9.4",key:"17fqt1"}],["path",{d:"m21.7 7.5-.9-.4",key:"14zyni"}],["path",{d:"M22 13v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7",key:"1tnzv8"}],["path",{d:"M8 21h8",key:"1ev6f3"}],["circle",{cx:"18",cy:"6",r:"3",key:"1h7g24"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kE=we("Radio",[["path",{d:"M4.9 19.1C1 15.2 1 8.8 4.9 4.9",key:"1vaf9d"}],["path",{d:"M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5",key:"u1ii0m"}],["circle",{cx:"12",cy:"12",r:"2",key:"1c9p78"}],["path",{d:"M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5",key:"1j5fej"}],["path",{d:"M19.1 4.9C23 8.8 23 15.1 19.1 19",key:"10b0cb"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const XE=we("RefreshCw",[["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",key:"v9h5vc"}],["path",{d:"M21 3v5h-5",key:"1q7to0"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",key:"3uifl3"}],["path",{d:"M8 16H3v5",key:"1cv678"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qE=we("Send",[["path",{d:"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",key:"1ffxy3"}],["path",{d:"m21.854 2.147-10.94 10.939",key:"12cjpa"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const WE=we("ServerCog",[["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}],["path",{d:"M4.5 10H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-.5",key:"tn8das"}],["path",{d:"M4.5 14H4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2h-.5",key:"1g2pve"}],["path",{d:"M6 6h.01",key:"1utrut"}],["path",{d:"M6 18h.01",key:"uhywen"}],["path",{d:"m15.7 13.4-.9-.3",key:"1jwmzr"}],["path",{d:"m9.2 10.9-.9-.3",key:"qapnim"}],["path",{d:"m10.6 15.7.3-.9",key:"quwk0k"}],["path",{d:"m13.6 15.7-.4-1",key:"cb9xp7"}],["path",{d:"m10.8 9.3-.4-1",key:"1uaiz5"}],["path",{d:"m8.3 13.6 1-.4",key:"s6srou"}],["path",{d:"m14.7 10.8 1-.4",key:"4d31cq"}],["path",{d:"m13.4 8.3-.3.9",key:"1bm987"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const W0=we("Server",[["rect",{width:"20",height:"8",x:"2",y:"2",rx:"2",ry:"2",key:"ngkwjq"}],["rect",{width:"20",height:"8",x:"2",y:"14",rx:"2",ry:"2",key:"iecqi9"}],["line",{x1:"6",x2:"6.01",y1:"6",y2:"6",key:"16zg32"}],["line",{x1:"6",x2:"6.01",y1:"18",y2:"18",key:"nzw8ys"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const YE=we("Settings",[["path",{d:"M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",key:"1qme2f"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rc=we("ShieldAlert",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M12 16h.01",key:"1drbdi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Nx=we("ShieldCheck",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Y0=we("SlidersHorizontal",[["line",{x1:"21",x2:"14",y1:"4",y2:"4",key:"obuewd"}],["line",{x1:"10",x2:"3",y1:"4",y2:"4",key:"1q6298"}],["line",{x1:"21",x2:"12",y1:"12",y2:"12",key:"1iu8h1"}],["line",{x1:"8",x2:"3",y1:"12",y2:"12",key:"ntss68"}],["line",{x1:"21",x2:"16",y1:"20",y2:"20",key:"14d8ph"}],["line",{x1:"12",x2:"3",y1:"20",y2:"20",key:"m0wm8r"}],["line",{x1:"14",x2:"14",y1:"2",y2:"6",key:"14e1ph"}],["line",{x1:"8",x2:"8",y1:"10",y2:"14",key:"1i6ji0"}],["line",{x1:"16",x2:"16",y1:"18",y2:"22",key:"1lctlv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ar=we("TriangleAlert",[["path",{d:"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",key:"wmoenq"}],["path",{d:"M12 9v4",key:"juzpu7"}],["path",{d:"M12 17h.01",key:"p32p05"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const QE=we("UserRound",[["circle",{cx:"12",cy:"8",r:"5",key:"1hypcn"}],["path",{d:"M20 21a8 8 0 0 0-16 0",key:"rfgkzh"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ZE=we("WifiOff",[["path",{d:"M12 20h.01",key:"zekei9"}],["path",{d:"M8.5 16.429a5 5 0 0 1 7 0",key:"1bycff"}],["path",{d:"M5 12.859a10 10 0 0 1 5.17-2.69",key:"1dl1wf"}],["path",{d:"M19 12.859a10 10 0 0 0-2.007-1.523",key:"4k23kn"}],["path",{d:"M2 8.82a15 15 0 0 1 4.177-2.643",key:"1grhjp"}],["path",{d:"M22 8.82a15 15 0 0 0-11.288-3.764",key:"z3jwby"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Dx=we("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]);async function KE(a="dashboard"){const t=a==="display"?`/display/overview${Ux()}`:"/api/ui/overview",n=await fetch(t,{credentials:"include"});if(!n.ok)throw new Error(`Overview request failed: ${n.status}`);return n.json()}function Ux(){if(typeof window>"u")return"";const a=new URLSearchParams(window.location.search).get("display_token");return a?`?display_token=${encodeURIComponent(a)}`:""}async function JE(a){const t=await fetch("/api/chat/send",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:a})});if(!t.ok)throw new Error(`Chat request failed: ${t.status}`);return t.json()}async function $E(a,t){const s=await fetch(`/api/approvals/${a}/${t==="approve"?"approve":"reject"}`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({})});if(!s.ok)throw new Error(`Approval ${t} failed: ${s.status}`)}async function Lx(){const a=await fetch("/auth/me",{credentials:"include"});if(!a.ok)throw new Error(`Auth session request failed: ${a.status}`);return a.json()}async function Bh(){const a=await fetch("/api/settings",{credentials:"include"});if(!a.ok)throw new Error(`Settings request failed: ${a.status}`);return a.json()}async function tb(a,t,n){const s=String((await Lx()).csrf_token||""),o=await fetch("/api/settings",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json","X-CSRF-Token":s},body:JSON.stringify({section:a,key:t,value:n})}),c=await o.json().catch(()=>({}));if(!o.ok){const f=String(c.error||(Array.isArray(c.errors)?c.errors.join(", "):"")||o.status);throw new Error(f)}return c}async function eb(){const a=String((await Lx()).csrf_token||""),t=await fetch("/api/settings/reset",{method:"POST",credentials:"include",headers:{"X-CSRF-Token":a}}),n=await t.json().catch(()=>({}));if(!t.ok)throw new Error(String(n.error||t.status));return n}const Q0={};function Ox(a,t=!0,n="dashboard"){se.useEffect(()=>{if(!t||typeof EventSource>"u")return;const s=Ux(),o=Q0[n]||nb(n),c=o?`last_event_id=${encodeURIComponent(o)}`:"",f=[n==="display"?"surface=display":"",s?s.slice(1):"",c].filter(Boolean).join("&"),d=n==="display"?`/api/ui/stream${f?`?${f}`:""}`:`/api/ui/stream${f?`?${f}`:""}`,p=new EventSource(d,{withCredentials:!0}),m=v=>{try{const _=JSON.parse(v.data),x=v.lastEventId||_.event_id||"";x&&(Q0[n]=x,ib(n,x)),a(_)}catch{}};for(const v of["status.changed","task.updated","tool.execution.started","tool.execution.completed","tool.execution.failed","approval.created","approval.resolved","notification.created","chat.updated","permission.changed","connection.changed","activity.updated"])p.addEventListener(v,m);return p.addEventListener("ui.snapshot",m),()=>p.close()},[t,a,n])}function nb(a){try{return window.sessionStorage.getItem(Px(a))||""}catch{return""}}function ib(a,t){try{window.sessionStorage.setItem(Px(a),t)}catch{}}function Px(a){return`aegis.ui.lastEventId.${a}`}function ab({open:a,onClose:t}){const[n,s]=se.useState(""),[o,c]=se.useState([]),[f,d]=se.useState(!1);async function p(m){m.preventDefault();const v=n.trim();if(!(!v||f)){s(""),c(_=>[..._,{role:"user",text:v}]),d(!0);try{const _=await JE(v);c(x=>[...x,{role:"aegis",text:String(_.response||_.message||"Done.")}])}catch(_){c(x=>[...x,{role:"system",text:_ instanceof Error?_.message:String(_)}])}finally{d(!1)}}}return g.jsxs("aside",{className:"chat-drawer","data-open":a,"aria-hidden":!a,children:[g.jsxs("div",{className:"chat-drawer__header",children:[g.jsxs("h2",{children:[g.jsx(Rx,{size:18,"aria-hidden":"true"})," Chat"]}),g.jsx("button",{className:"icon-button",onClick:t,title:"Close chat",children:g.jsx(Dx,{size:16,"aria-hidden":"true"})})]}),g.jsxs("div",{className:"chat-log",children:[o.length===0?g.jsx("div",{className:"muted",children:"Chat is ready. Messages are sent through the existing AEGIS chat API."}):null,o.map((m,v)=>g.jsx("div",{className:"list-row chat-log__item",children:g.jsxs("div",{children:[g.jsx("strong",{children:m.role}),g.jsx("div",{children:m.text})]})},`${m.role}-${v}`))]}),g.jsxs("form",{className:"chat-form",onSubmit:p,children:[g.jsx("textarea",{value:n,onChange:m=>s(m.target.value),"aria-label":"Message"}),g.jsx("button",{className:"icon-button",title:"Send message",disabled:f,children:g.jsx(qE,{size:16,"aria-hidden":"true"})})]})]})}function lr({generatedAt:a,sourceUpdatedAt:t,stale:n=!1}){const s=Math.max(0,a-t),o=n?`STALE ${Z0(s)}`:s<15e3?"LIVE":`${Z0(s)} ago`;return g.jsx("span",{className:"freshness","data-stale":n,children:o})}function Z0(a){const t=Math.round(a/1e3);if(t<60)return`${t}s`;const n=Math.round(t/60);return n<60?`${n}m`:`${Math.round(n/60)}h`}function oc({status:a,detail:t}){const n=(a||"UNKNOWN").toUpperCase(),s=n==="ONLINE"?UE:n==="DISABLED"||n==="UNCONFIGURED"?OE:n==="OFFLINE"?LE:ar;return g.jsxs("span",{className:"status-badge","data-status":n,title:t||n,children:[g.jsx(s,{size:14,"aria-hidden":"true"}),n]})}const sb={loading:XE,empty:ar,stale:ar,permission:rc,unauthorized:q0,"fresh-auth":q0,error:ar,partial:ar,disconnected:ar};function Jl({kind:a,title:t,message:n,actionLabel:s,actionHref:o}){const c=sb[a];return g.jsxs("section",{className:"ui-state","data-kind":a,children:[g.jsx(c,{size:20,"aria-hidden":"true"}),g.jsxs("div",{children:[g.jsx("strong",{children:t}),g.jsx("p",{children:n})]}),s&&o?g.jsx("a",{className:"ghost-button",href:o,children:s}):null]})}function rb({stale:a,error:t,empty:n,label:s}){return t?g.jsx(Jl,{kind:"error",title:`${s} unavailable`,message:t}):a?g.jsx(Jl,{kind:"stale",title:`${s} is stale`,message:"Showing the last known value while AEGIS waits for a fresh update."}):n?g.jsx(Jl,{kind:"empty",title:`No ${s.toLowerCase()} reported`,message:"AEGIS has no current data for this section."}):null}function ob({overview:a,recentEvents:t=[]}){var d,p,m,v,_,x,E;const n=(((d=a.activity)==null?void 0:d.data.recent)||[]).map(M=>{var T,S,y;return{type:String(M.type||M.event_type||"activity.updated"),message:String(((T=M.presentation_event)==null?void 0:T.summary)||M.message||M.title||""),source_type:String(M.event_type||M.type||"activity"),server_id:String(M.server_id||""),severity:String(M.severity||""),source_updated_at:Number(M.occurred_at||0),scene_type:String(((S=M.presentation_event)==null?void 0:S.scene_type)||M.scene_type||"event"),recommended_surfaces:Array.isArray((y=M.presentation_event)==null?void 0:y.recommended_surfaces)?M.presentation_event.recommended_surfaces:[]}}),o=[...t.map(M=>{var T,S,y;return{type:M.type,message:((T=M.presentation_event)==null?void 0:T.summary)||M.message||M.safe_message||"",source_type:M.source_type,server_id:M.server_id||"",severity:M.severity||"",source_updated_at:M.source_updated_at,scene_type:((S=M.presentation_event)==null?void 0:S.scene_type)||M.scene_type||"event",recommended_surfaces:((y=M.presentation_event)==null?void 0:y.recommended_surfaces)||M.recommended_surfaces||[]}}),...n].slice(0,80),c=((p=a.activity)==null?void 0:p.data.groups)||[],f=(((m=a.presentation_events)==null?void 0:m.data.items)||[]).slice(0,18);return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel operational-replay",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Operational Replay"}),g.jsx("div",{className:"muted",children:"PresentationEvent timeline shared by Web, Display, mobile, overlay, room, and developer console."})]}),g.jsx("span",{className:"freshness","data-stale":((v=a.presentation_events)==null?void 0:v.stale)||!1,children:((_=a.presentation_events)==null?void 0:_.data.source)||"presentation_surface_contract"})]}),g.jsx("div",{className:"replay-river",children:f.length?f.map(M=>g.jsxs("article",{className:"replay-step","data-priority":M.priority,"data-scene":M.scene_type,children:[g.jsx("span",{className:"replay-step__scene",children:M.scene_type}),g.jsx("strong",{children:M.title}),g.jsx("p",{children:M.summary||M.detail||"No summary reported."}),g.jsxs("div",{className:"replay-step__meta",children:[g.jsx("span",{children:M.priority}),g.jsx("span",{children:M.source}),g.jsx("span",{children:M.recommended_surfaces.slice(0,4).join(" / ")||"no surface"})]})]},M.event_id)):g.jsx("div",{className:"muted",children:"No replayable presentation events have been reported yet."})})]}),g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Activity"}),g.jsx("div",{className:"muted",children:"Persisted EventManager history grouped into operational activity."})]}),g.jsx("span",{className:"freshness","data-stale":((x=a.activity)==null?void 0:x.stale)||!1,children:((E=a.activity)==null?void 0:E.data.source)||"event_manager"})]}),g.jsx("div",{className:"grid",children:c.length?c.slice(0,12).map(M=>{var T;return g.jsxs("div",{className:"list-row list-row--with-drawer",children:[g.jsxs("div",{children:[g.jsx("strong",{children:String(M.title||M.group_id||"Activity")}),g.jsxs("div",{className:"muted",children:[String(M.status||M.severity||"updated")," / ",Number(((T=M.events)==null?void 0:T.length)||0)," event(s)"]})]}),g.jsx("span",{className:"mono muted",children:String(M.server_id||M.capability_id||M.task_id||"event")}),g.jsxs("details",{className:"inline-drawer",children:[g.jsx("summary",{children:"Developer trace"}),g.jsx("pre",{children:JSON.stringify(M,null,2)})]})]},String(M.group_id||M.title))}):g.jsx("div",{className:"muted",children:"No persisted activity has been reported yet."})})]}),g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Recent Events"})}),g.jsxs("div",{className:"grid",children:[o.map(M=>g.jsxs("div",{className:"list-row list-row--with-drawer",children:[g.jsxs("div",{children:[g.jsx("strong",{children:M.type}),g.jsx("div",{className:"muted",children:M.message||M.source_type})]}),g.jsx("span",{className:"mono muted",children:M.server_id||M.severity||"event"}),g.jsxs("details",{className:"inline-drawer",children:[g.jsx("summary",{children:"Developer trace"}),g.jsx("pre",{children:JSON.stringify(M,null,2)})]})]},`${M.type}-${M.source_updated_at}-${M.message}`)),o.length===0?(a.attention.data.items||[]).map(M=>g.jsxs("div",{className:"list-row",children:[g.jsxs("div",{children:[g.jsx("strong",{children:M.title}),g.jsx("div",{className:"muted",children:M.message})]}),g.jsx("span",{className:"mono muted",children:M.kind})]},M.id)):null]})]})]})}function lb({approval:a,readonly:t=!1}){const[n,s]=se.useState(""),[o,c]=se.useState("");async function f(d){s(d),c("");try{await $E(a.approval_id,d)}catch(p){c(p instanceof Error?p.message:String(p))}finally{s("")}}return g.jsxs("article",{className:"approval-card",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("strong",{children:a.summary||a.tool_name||"Approval required"}),g.jsx("div",{className:"muted mono",children:a.approval_id})]}),g.jsxs("span",{className:"status-badge","data-status":"WAITING",children:[g.jsx(rc,{size:14,"aria-hidden":"true"}),a.risk||"risk"]})]}),g.jsx("div",{className:"muted",children:a.reason||"Review the requested action before allowing it to continue."}),g.jsxs("div",{className:"stat-grid",children:[g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Capability"}),g.jsx("b",{className:"mono stat__value--small",children:a.capability_id})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Target"}),g.jsx("b",{className:"stat__value--small",children:a.target||"Not specified"})]})]}),g.jsxs("div",{className:"approval-detail-grid",children:[g.jsx(no,{label:"Side effects",value:a.side_effects}),g.jsx(no,{label:"Previous action",value:a.previous_action}),g.jsx(no,{label:"Similar history",value:a.similar_action_summary}),g.jsx(no,{label:"Expected effect",value:a.expected_effect}),g.jsx(no,{label:"Fresh auth",value:a.fresh_auth_required?"Required":"Not required for this request"}),g.jsx(no,{label:"Task",value:a.task_id||"Not linked"})]}),a.preview?g.jsx("pre",{className:"approval-preview mono",children:a.preview}):null,o?g.jsx("div",{className:"attention-item","data-severity":"critical",children:o}):null,t?null:g.jsxs("div",{className:"approval-card__actions",children:[g.jsxs("button",{className:"primary-button",onClick:()=>f("approve"),disabled:!!n,children:[g.jsx(DE,{size:16,"aria-hidden":"true"})," ",n==="approve"?"Approving":"Approve"]}),g.jsxs("button",{className:"danger-button",onClick:()=>f("reject"),disabled:!!n,children:[g.jsx(Dx,{size:16,"aria-hidden":"true"})," ",n==="reject"?"Rejecting":"Reject"]})]})]})}function no({label:a,value:t}){const n=Array.isArray(t)?t.join(", "):String(t||"No data yet");return g.jsxs("div",{className:"approval-detail",children:[g.jsx("span",{children:a}),g.jsx("strong",{children:n})]})}const df=["ai-server","pc-server","android-server","browser-server","room-server","dev-server"];function Cm(a=""){const t=a.split(".",1)[0];return df.includes(t)?t:"ai-server"}function ta(a){return{"ai-server":"AI","pc-server":"PC","android-server":"Android","browser-server":"Browser","room-server":"Room","dev-server":"Dev"}[a]||a.replace("-server","")}function hf(a=""){return a.trim().toUpperCase()||"UNKNOWN"}function Rm(a,t=""){const n=hf(a.status),s=`${a.status_detail||""} ${a.degraded_reason||""} ${a.recovery_hint||""}`.toLowerCase();return a.server_id===t||["DEGRADED","OFFLINE","UNCONFIGURED","DISABLED","RECOVERING"].includes(n)||s.includes("permission")||s.includes("missing")||s.includes("recover")}function cb(a){const t=a.filter(n=>Rm(n));return{ok:Math.max(0,a.length-t.length),attention:t}}function zx(a){var v,_,x,E,M;const t=a.type||a.source_type||"activity.updated",n=a.capability_id||String(((v=a.payload)==null?void 0:v.capability_id)||""),s=((_=a.visual_hint)==null?void 0:_.arc)||a.server_id||Cm(n),o=String(a.status||((x=a.payload)==null?void 0:x.status)||"");let c="pulse";const f=Fx((E=a.visual_hint)==null?void 0:E.effect);f?c=f:t==="approval.created"?c="containment":t==="approval.resolved"?c="containment-resolved":t.includes("failed")||o.toLowerCase()==="failed"?c="fracture":t.includes("completed")?c="complete":(t.includes("status")||t.includes("connection"))&&(c=o.toLowerCase().includes("offline")?"disconnect":"recovery");const d=Date.now(),p=a.received_at||a.generated_at||d,m=Number(((M=a.visual_hint)==null?void 0:M.duration_ms)||4500);return{id:a.event_id||`${a.type}-${a.source_updated_at}-${s}-${a.approval_id||""}`,type:t,effect:c,serverId:s,capabilityId:n,status:o,severity:a.severity||"info",message:a.safe_message||a.message||t,createdAt:p,expiresAt:a.expires_at||p+m}}function ub(a,t,n=[]){var E;const s=La((E=a.display_scene)==null?void 0:E.data),o=Date.now(),c=La(s.takeover),f=xb(t.map(M=>mb(M)).filter(Boolean)),d=yb(a),p=Ix(a).map(M=>gb(M)),m=_b(a),v=[...d,...f,...p,...m].filter(M=>!M.expiresAt||M.expiresAt>o||M.persistence==="until_resolved").sort(Sb),x=(c.active?{id:String(c.source_id||"display-scene-takeover"),priority:String(c.priority||"P1"),severity:String(c.severity||"warning"),title:String(c.title||"Attention required"),message:String(c.message||"Review AEGIS on phone or web."),persistence:"until_resolved",createdAt:a.generated_at,expiresAt:Number(c.expires_at||0),affectedServers:[]}:void 0)||v.find(M=>["P0","P1"].includes(String(M.priority)));return{sceneMode:String(s.phase||s.mode||wm(a)),privacyMode:!!s.privacy_mode,offline:!!(s.offline||String(a.core.data.health||"").toUpperCase()==="OFFLINE"),stale:!!(a.freshness.stale||s.stale),takeover:x,overlays:v.filter(M=>M.id!==(x==null?void 0:x.id)&&String(M.priority)==="P2").slice(0,3),dock:v.filter(M=>M.id!==(x==null?void 0:x.id)&&M.persistence!=="ephemeral").slice(0,6),ambient:[...v.filter(M=>M.id!==(x==null?void 0:x.id)&&M.persistence==="ephemeral"),...n.map(M=>vb(M))].slice(0,8)}}function Ix(a){const t=a.approvals.data.pending||[],n=a.attention.data.items||[];return[...t.map(o=>({id:o.approval_id,kind:"approval",severity:"warning",title:"Approval required",message:o.summary||o.capability_id||"Review requested action",created_at:o.created_at,expires_at:o.expires_at})),...n.filter(o=>o.kind!=="approval")]}function wm(a){var c,f;const t=(f=(c=a.display_scene)==null?void 0:c.data)==null?void 0:f.phase;if(t)return String(t);const n=a.core.data,s=a.current_task.data;return(a.approvals.data.pending_count||0)>0?"Waiting for Approval":String(n.health||"").toUpperCase()==="OFFLINE"?"Offline":String(n.health||"").toUpperCase()==="DEGRADED"?"Stabilizing":s.task_id||String(n.mode||"").toUpperCase()==="EXECUTING"?"Executing":"Idle"}function Nm(a){const t=a.mind_summary.data||{},n=a.core.data||{},s=La(t.memory),o=La(t.autonomy),c=La(o.desires||o.pressures||o.desire_state),f=Mb(c);return{"Active goal":String(n.active_goal||"No data yet"),"Dominant desire":f||"No data yet","Context confidence":String(n.confidence||t.context_confidence||"No data yet"),"Memories used":Eb(s),"Last consolidation":String(s.last_consolidation||s.last_consolidated_at||s.last_sleep_at||"No data yet")}}function fb(a){var d,p,m,v;const t=a.current_task.data,n=(d=a.tasks)==null?void 0:d.data,s=a.commitments.data.items||[],o=!!(t.task_id||t.title),c=(p=n==null?void 0:n.active)!=null&&p.length?n.active:o?[t]:[],f=(m=n==null?void 0:n.waiting)!=null&&m.length?n.waiting:o&&(a.approvals.data.pending_count>0||t.blocked_reason)?[t]:[];return[{id:"active",label:"Active",count:c.length,items:c},{id:"waiting",label:"Waiting",count:f.length,items:f},{id:"scheduled",label:"Scheduled",count:((v=n==null?void 0:n.scheduled)==null?void 0:v.length)||0,items:(n==null?void 0:n.scheduled)||[]},{id:"research",label:"Research",count:Lu(t,"browser-server")?c.length:0,items:Lu(t,"browser-server")?c:[]},{id:"self-development",label:"Self-development",count:Lu(t,"dev-server")?c.length:0,items:Lu(t,"dev-server")?c:[]},{id:"commitments",label:"Commitments",count:s.length,items:s},{id:"delegated",label:"Delegated",count:((n==null?void 0:n.recent)||[]).filter(_=>!!(_.server_id||_.assignee||_.delegated_to)).length,items:((n==null?void 0:n.recent)||[]).filter(_=>!!(_.server_id||_.assignee||_.delegated_to))},{id:"completed",label:"Completed",count:((n==null?void 0:n.recent)||[]).filter(_=>String(_.status||"").toLowerCase()==="completed").length||K0(t,"completed"),items:[]},{id:"failed",label:"Failed",count:((n==null?void 0:n.recent)||[]).filter(_=>String(_.status||"").toLowerCase()==="failed").length||K0(t,"failed"),items:[]}]}function db(a){const t=Date.now();return[{id:"pending",label:"Pending",items:a.filter(n=>Uu(n)==="PENDING")},{id:"expiring",label:"Expiring",items:a.filter(n=>n.expires_at&&n.expires_at-t<600*1e3)},{id:"high-risk",label:"High risk",items:a.filter(n=>["HIGH","CRITICAL","FORBIDDEN"].includes(String(n.risk||"").toUpperCase()))},{id:"resolved",label:"Resolved",items:a.filter(n=>["APPROVED","RESOLVED"].includes(Uu(n)))},{id:"expired",label:"Expired",items:a.filter(n=>Uu(n)==="EXPIRED")},{id:"failed",label:"Failed after approval",items:a.filter(n=>Uu(n).includes("FAILED"))}]}function hb(a){var s,o,c;const t=(a==null?void 0:a.approvals.data.pending_count)||0,n=a?Nm(a):{};return[{id:"autonomy",label:"Autonomy",summary:"Loop cadence, profile, and autonomous execution guardrails.",status:(s=a==null?void 0:a.mind_summary.data)!=null&&s.autonomy?"Configured":"No data yet"},{id:"permissions",label:"Permissions",summary:"Capability risk, approval requirements, PC/Android operation limits.",status:t?`${t} approval pending`:"Guarded"},{id:"servers",label:"Servers",summary:"AI, PC, Android, Browser, Room, and Dev endpoints.",status:`${((o=a==null?void 0:a.servers.data.items)==null?void 0:o.length)||0} known`},{id:"privacy",label:"Privacy",summary:"Display privacy mode, redaction, local-only surfaces.",status:"Local-first"},{id:"notifications",label:"Notifications",summary:"Attention routing, persistent warnings, and quiet states.",status:`${(a==null?void 0:a.notifications.data.unread_count)||0} unread`},{id:"models",label:"Models",summary:"LLM profiles, provider routing, and fresh-auth protected changes.",status:"Fresh auth required"},{id:"budgets",label:"Budgets",summary:"LLM usage, cost ceilings, and autonomous suppression.",status:String(((c=a==null?void 0:a.usage.data)==null?void 0:c.summary)||"Audit-backed")},{id:"memory",label:"Memory",summary:"Episodic, semantic, procedural retrieval and consolidation.",status:n["Memories used"]||"No data yet"},{id:"display",label:"Display",summary:"Read-only dedicated display, token, kiosk, privacy and power behavior.",status:"Read-only"},{id:"developer",label:"Developer",summary:"Debug drawers, raw JSON, audit traces, and dev server writes.",status:"Restricted"},{id:"backup",label:"Backup",summary:"Data volume, auth credentials, audit, memory, and override backups.",status:"Manual check"}]}function pb(a){const t=La(a.dependencies),n=Object.entries(t);if(!n.length)return"No dependencies reported";const s=n.filter(([,o])=>o===!1||o==="false"||o==="missing").map(([o])=>o);return s.length?`${s.length} dependency issue(s): ${s.slice(0,3).join(", ")}`:`${n.length} dependencies reported`}function mb(a){const t=zx(a),n=a.presentation_event,s=(n==null?void 0:n.priority)||a.priority||Bx(a.severity||t.severity||"info");return{id:a.dedupe_key||a.event_id||t.id,priority:s,severity:(n==null?void 0:n.severity)||a.severity||t.severity||"info",title:(n==null?void 0:n.title)||a.safe_title||a.type||"AEGIS event",message:(n==null?void 0:n.summary)||a.safe_message||a.message||a.source_type||"AEGIS event",persistence:(n==null?void 0:n.persistence)||a.persistence||(s==="P0"||s==="P1"?"until_resolved":s==="P2"?"attention_dock":"ephemeral"),createdAt:a.occurred_at||a.source_updated_at||a.generated_at||Date.now(),expiresAt:(n==null?void 0:n.expires_at)||a.expires_at||t.expiresAt,affectedServers:a.affected_servers||(a.server_id?[a.server_id]:[]),visualEvent:t}}function gb(a){const t=a.kind==="approval"?"P1":Bx(a.severity);return{id:a.id,priority:t,severity:a.severity||"info",title:a.title,message:a.message||a.recovery_hint||"Review this signal.",persistence:t==="P0"||t==="P1"?"until_resolved":"attention_dock",createdAt:a.created_at||Date.now(),expiresAt:a.expires_at||0,affectedServers:[]}}function vb(a){return{id:a.id,priority:a.effect==="fracture"||a.effect==="disconnect"?"P2":"P3",severity:a.severity||"info",title:a.type,message:a.message,persistence:"ephemeral",createdAt:a.createdAt,expiresAt:a.expiresAt,affectedServers:a.serverId?[a.serverId]:[],visualEvent:a}}function _b(a){var s;const t=(s=a.presentations)==null?void 0:s.data;return t?[["P0","until_resolved",t.takeover],["P2","attention_dock",t.overlays],["P2","until_resolved",t.persistent],["P3","ephemeral",t.ambient]].flatMap(([o,c,f])=>(f||[]).map(d=>({id:String(d.presentation_id||d.id||`${o}-${d.title||"presentation"}`),priority:o,severity:o==="P0"?"critical":o==="P2"?"warning":"info",title:String(d.title||"Presentation"),message:String(d.summary||d.status||"Presentation update"),persistence:c,createdAt:Number(d.created_at||a.generated_at),expiresAt:Number(d.expires_at||0),affectedServers:[]}))):[]}function yb(a){var n,s;return(((s=(n=a.display_queue)==null?void 0:n.data)==null?void 0:s.items)||[]).map(o=>{const c=La(o),f=La(c.presentation_event),d=String(c.priority||"P3"),p=La(c.visual_hint);return{id:String(c.id||c.event_id||c.title||"display-queue-item"),priority:String(f.priority||d),severity:String(f.severity||c.severity||"info"),title:String(f.title||c.title||"AEGIS signal"),message:String(f.summary||c.message||c.title||"AEGIS signal"),persistence:String(f.persistence||c.persistence||(d==="P0"||d==="P1"?"until_resolved":"attention_dock")),createdAt:Number(c.created_at||c.updated_at||Date.now()),expiresAt:Number(f.expires_at||c.expires_at||0),affectedServers:Array.isArray(c.affected_servers)?c.affected_servers.map(String):[],visualEvent:p.effect?{id:String(c.event_id||c.id||`${c.title||"queue"}-visual`),type:String(c.title||"display.queue"),effect:Fx(p.effect)||"pulse",serverId:String(p.arc||(Array.isArray(c.affected_servers)?c.affected_servers[0]:"")||"ai-server"),status:String(c.status||""),severity:String(c.severity||"info"),message:String(c.message||c.title||"AEGIS signal"),createdAt:Number(c.created_at||Date.now()),expiresAt:Number(c.expires_at||Date.now()+Number(p.duration_ms||4500))}:void 0}})}function xb(a){const t=new Map;for(const n of a){const s=t.get(n.id);(!s||n.createdAt>=s.createdAt||pf(n.priority)<pf(s.priority))&&t.set(n.id,n)}return[...t.values()]}function Sb(a,t){return pf(a.priority)-pf(t.priority)||t.createdAt-a.createdAt}function Bx(a="info"){const t=a.toLowerCase();return t==="critical"?"P0":t==="warning"?"P2":"P3"}function pf(a){return{P0:0,P1:1,P2:2,P3:3}[a]??4}function Fx(a){const t=String(a||"");return["pulse","complete","fracture","containment","containment-resolved","disconnect","recovery"].includes(t)?t:""}function Uu(a){return String(a.status||"pending").toUpperCase()}function Lu(a,t){return String(a.capability_id||"").includes(t)?!0:!!(a.steps||[]).some(n=>String(n.capability_id||n.name||"").includes(t))}function K0(a,t){return(a.steps||[]).filter(n=>String(n.status||"").toLowerCase()===t).length}function La(a){return a&&typeof a=="object"&&!Array.isArray(a)?a:{}}function Mb(a){let t="",n=Number.NEGATIVE_INFINITY;for(const[s,o]of Object.entries(a)){const c=typeof o=="number"?o:Number(typeof o=="object"&&o?o.value||o.pressure:o);Number.isFinite(c)&&c>n&&(t=s,n=c)}return t}function Eb(a){const t=a.memories_used||a.used||a.context_items;if(t!==void 0)return String(t);const n=["episodic","semantic","procedural"].reduce((s,o)=>{const c=Number(a[o]||0);return Number.isFinite(c)?s+c:s},0);return n>0?String(n):"No data yet"}function bb({overview:a}){var c,f,d,p;const t=a.approvals.data.pending||[],n=t[0],s=db(t),o=(((c=a.activity)==null?void 0:c.data.recent)||[]).filter(m=>n?String(m.approval_id||m.task_id||m.capability_id||"").includes(n.approval_id)||String(m.task_id||"")===n.task_id||String(m.capability_id||"")===n.capability_id:!1);return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Approvals"}),g.jsx("div",{className:"muted",children:"Every approval is shown with risk, target, reason, preview, and task context."})]}),g.jsx(lr,{generatedAt:a.approvals.generated_at,sourceUpdatedAt:a.approvals.source_updated_at,stale:a.approvals.stale})]}),g.jsx("div",{className:"tab-strip",role:"tablist","aria-label":"Approval filters",children:s.map(m=>g.jsxs("button",{className:"tab-chip",type:"button","aria-selected":m.id==="pending",children:[g.jsx("span",{children:m.label}),g.jsx("strong",{children:m.items.length})]},m.id))})]}),g.jsxs("section",{className:"approval-layout",children:[g.jsxs("aside",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Queue"})}),g.jsxs("div",{className:"grid",children:[t.map(m=>g.jsxs("article",{className:"list-row","data-selected":m.approval_id===(n==null?void 0:n.approval_id),children:[g.jsxs("div",{children:[g.jsx("strong",{children:m.summary||m.capability_id}),g.jsx("div",{className:"muted mono",children:m.approval_id})]}),g.jsx("span",{className:"status-badge","data-status":"WAITING",children:m.risk||"risk"})]},m.approval_id)),t.length?null:g.jsx("div",{className:"attention-item","data-severity":"normal",children:"No pending approvals."})]})]}),g.jsx("main",{children:n?g.jsx(lb,{approval:n}):g.jsx("section",{className:"panel",children:g.jsx("div",{className:"attention-item","data-severity":"normal",children:"No action is waiting for approval."})})}),g.jsxs("aside",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Context"})}),n?g.jsxs("div",{className:"metric-list",children:[g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Related task"}),g.jsx("strong",{className:"mono",children:n.task_id||a.current_task.data.task_id||"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Target server"}),g.jsx("strong",{children:ta(Cm(n.capability_id))})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Risk rationale"}),g.jsx("strong",{children:n.reason||"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Side effects"}),g.jsx("strong",{children:Tb(n.side_effects)})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Previous action"}),g.jsx("strong",{children:String(n.previous_action||((f=o[0])==null?void 0:f.message)||((d=o[0])==null?void 0:d.title)||"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Similar past action"}),g.jsx("strong",{children:String(n.similar_action_summary||((p=o[1])==null?void 0:p.message)||"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Fresh auth"}),g.jsx("strong",{children:n.fresh_auth_required?"Required":"Not required"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Post-approval effect"}),g.jsx("strong",{children:String(n.expected_effect||"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Audit"}),g.jsx("strong",{children:n.request_id||n.step_id||"No data yet"})]}),g.jsx("div",{className:"approval-safety-note",children:"Bulk approval is not available. Each high-risk action must be reviewed independently with fresh authentication when required."})]}):g.jsx("p",{className:"muted",children:"Approval context appears here when an action is pending."})]})]})]})}function Tb(a){return Array.isArray(a)?a.length?a.join(", "):"None reported":String(a||"No data yet")}function Ab({items:a}){return a.length?g.jsx("section",{className:"attention-strip","aria-label":"Attention",children:a.slice(0,6).map(t=>{const n=t.kind==="approval"?rc:t.kind==="server"?ZE:ar;return g.jsxs("article",{className:"attention-item","data-severity":t.severity,children:[g.jsxs("div",{children:[g.jsx("strong",{children:t.title}),g.jsx("div",{className:"muted",children:t.message||t.recovery_hint||"Review this item."})]}),g.jsx(n,{size:20,"aria-label":t.severity})]},t.id)})}):g.jsx("section",{className:"attention-strip","aria-label":"Attention",children:g.jsxs("div",{className:"attention-item","data-severity":"normal",children:[g.jsxs("div",{children:[g.jsx("strong",{children:"No immediate attention required"}),g.jsx("div",{className:"muted",children:"All current UI signals are within normal bounds."})]}),g.jsx(Ax,{size:18,"aria-hidden":"true"})]})})}/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Dm="171",Cb=0,J0=1,Rb=2,Hx=1,wb=2,Ca=3,Rs=0,ii=1,Na=2,Oa=0,Eo=1,Lp=2,$0=3,ty=4,Nb=5,sr=100,Db=101,Ub=102,Lb=103,Ob=104,Pb=200,zb=201,Ib=202,Bb=203,Op=204,Pp=205,Fb=206,Hb=207,Gb=208,Vb=209,jb=210,kb=211,Xb=212,qb=213,Wb=214,zp=0,Ip=1,Bp=2,Fo=3,Fp=4,Hp=5,Gp=6,Vp=7,Gx=0,Yb=1,Qb=2,Cs=0,Zb=1,Kb=2,Jb=3,$b=4,tT=5,eT=6,nT=7,Vx=300,Ho=301,Go=302,jp=303,kp=304,xf=306,Xp=1e3,cr=1001,qp=1002,Hi=1003,iT=1004,Ou=1005,$i=1006,Fh=1007,ur=1008,Ia=1009,jx=1010,kx=1011,lc=1012,Um=1013,xr=1014,Da=1015,Pa=1016,Lm=1017,Om=1018,Vo=1020,Xx=35902,qx=1021,Wx=1022,Fi=1023,Yx=1024,Qx=1025,bo=1026,jo=1027,Zx=1028,Pm=1029,Kx=1030,zm=1031,Im=1033,sf=33776,rf=33777,of=33778,lf=33779,Wp=35840,Yp=35841,Qp=35842,Zp=35843,Kp=36196,Jp=37492,$p=37496,tm=37808,em=37809,nm=37810,im=37811,am=37812,sm=37813,rm=37814,om=37815,lm=37816,cm=37817,um=37818,fm=37819,dm=37820,hm=37821,cf=36492,pm=36494,mm=36495,Jx=36283,gm=36284,vm=36285,_m=36286,aT=3200,sT=3201,rT=0,oT=1,vs="",vi="srgb",ko="srgb-linear",mf="linear",qe="srgb",io=7680,ey=519,lT=512,cT=513,uT=514,$x=515,fT=516,dT=517,hT=518,pT=519,ny=35044,iy="300 es",Ua=2e3,gf=2001;class Wo{addEventListener(t,n){this._listeners===void 0&&(this._listeners={});const s=this._listeners;s[t]===void 0&&(s[t]=[]),s[t].indexOf(n)===-1&&s[t].push(n)}hasEventListener(t,n){if(this._listeners===void 0)return!1;const s=this._listeners;return s[t]!==void 0&&s[t].indexOf(n)!==-1}removeEventListener(t,n){if(this._listeners===void 0)return;const o=this._listeners[t];if(o!==void 0){const c=o.indexOf(n);c!==-1&&o.splice(c,1)}}dispatchEvent(t){if(this._listeners===void 0)return;const s=this._listeners[t.type];if(s!==void 0){t.target=this;const o=s.slice(0);for(let c=0,f=o.length;c<f;c++)o[c].call(this,t);t.target=null}}}const Bn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let ay=1234567;const $l=Math.PI/180,cc=180/Math.PI;function Yo(){const a=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0,s=Math.random()*4294967295|0;return(Bn[a&255]+Bn[a>>8&255]+Bn[a>>16&255]+Bn[a>>24&255]+"-"+Bn[t&255]+Bn[t>>8&255]+"-"+Bn[t>>16&15|64]+Bn[t>>24&255]+"-"+Bn[n&63|128]+Bn[n>>8&255]+"-"+Bn[n>>16&255]+Bn[n>>24&255]+Bn[s&255]+Bn[s>>8&255]+Bn[s>>16&255]+Bn[s>>24&255]).toLowerCase()}function ge(a,t,n){return Math.max(t,Math.min(n,a))}function Bm(a,t){return(a%t+t)%t}function mT(a,t,n,s,o){return s+(a-t)*(o-s)/(n-t)}function gT(a,t,n){return a!==t?(n-a)/(t-a):0}function tc(a,t,n){return(1-n)*a+n*t}function vT(a,t,n,s){return tc(a,t,1-Math.exp(-n*s))}function _T(a,t=1){return t-Math.abs(Bm(a,t*2)-t)}function yT(a,t,n){return a<=t?0:a>=n?1:(a=(a-t)/(n-t),a*a*(3-2*a))}function xT(a,t,n){return a<=t?0:a>=n?1:(a=(a-t)/(n-t),a*a*a*(a*(a*6-15)+10))}function ST(a,t){return a+Math.floor(Math.random()*(t-a+1))}function MT(a,t){return a+Math.random()*(t-a)}function ET(a){return a*(.5-Math.random())}function bT(a){a!==void 0&&(ay=a);let t=ay+=1831565813;return t=Math.imul(t^t>>>15,t|1),t^=t+Math.imul(t^t>>>7,t|61),((t^t>>>14)>>>0)/4294967296}function TT(a){return a*$l}function AT(a){return a*cc}function CT(a){return(a&a-1)===0&&a!==0}function RT(a){return Math.pow(2,Math.ceil(Math.log(a)/Math.LN2))}function wT(a){return Math.pow(2,Math.floor(Math.log(a)/Math.LN2))}function NT(a,t,n,s,o){const c=Math.cos,f=Math.sin,d=c(n/2),p=f(n/2),m=c((t+s)/2),v=f((t+s)/2),_=c((t-s)/2),x=f((t-s)/2),E=c((s-t)/2),M=f((s-t)/2);switch(o){case"XYX":a.set(d*v,p*_,p*x,d*m);break;case"YZY":a.set(p*x,d*v,p*_,d*m);break;case"ZXZ":a.set(p*_,p*x,d*v,d*m);break;case"XZX":a.set(d*v,p*M,p*E,d*m);break;case"YXY":a.set(p*E,d*v,p*M,d*m);break;case"ZYZ":a.set(p*M,p*E,d*v,d*m);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+o)}}function yo(a,t){switch(t.constructor){case Float32Array:return a;case Uint32Array:return a/4294967295;case Uint16Array:return a/65535;case Uint8Array:return a/255;case Int32Array:return Math.max(a/2147483647,-1);case Int16Array:return Math.max(a/32767,-1);case Int8Array:return Math.max(a/127,-1);default:throw new Error("Invalid component type.")}}function kn(a,t){switch(t.constructor){case Float32Array:return a;case Uint32Array:return Math.round(a*4294967295);case Uint16Array:return Math.round(a*65535);case Uint8Array:return Math.round(a*255);case Int32Array:return Math.round(a*2147483647);case Int16Array:return Math.round(a*32767);case Int8Array:return Math.round(a*127);default:throw new Error("Invalid component type.")}}const cs={DEG2RAD:$l,RAD2DEG:cc,generateUUID:Yo,clamp:ge,euclideanModulo:Bm,mapLinear:mT,inverseLerp:gT,lerp:tc,damp:vT,pingpong:_T,smoothstep:yT,smootherstep:xT,randInt:ST,randFloat:MT,randFloatSpread:ET,seededRandom:bT,degToRad:TT,radToDeg:AT,isPowerOfTwo:CT,ceilPowerOfTwo:RT,floorPowerOfTwo:wT,setQuaternionFromProperEuler:NT,normalize:kn,denormalize:yo};class Wt{constructor(t=0,n=0){Wt.prototype.isVector2=!0,this.x=t,this.y=n}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,n){return this.x=t,this.y=n,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const n=this.x,s=this.y,o=t.elements;return this.x=o[0]*n+o[3]*s+o[6],this.y=o[1]*n+o[4]*s+o[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(ge(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y;return n*n+s*s}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this}rotateAround(t,n){const s=Math.cos(n),o=Math.sin(n),c=this.x-t.x,f=this.y-t.y;return this.x=c*s-f*o+t.x,this.y=c*o+f*s+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class de{constructor(t,n,s,o,c,f,d,p,m){de.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,n,s,o,c,f,d,p,m)}set(t,n,s,o,c,f,d,p,m){const v=this.elements;return v[0]=t,v[1]=o,v[2]=d,v[3]=n,v[4]=c,v[5]=p,v[6]=s,v[7]=f,v[8]=m,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],this}extractBasis(t,n,s){return t.setFromMatrix3Column(this,0),n.setFromMatrix3Column(this,1),s.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const n=t.elements;return this.set(n[0],n[4],n[8],n[1],n[5],n[9],n[2],n[6],n[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,o=n.elements,c=this.elements,f=s[0],d=s[3],p=s[6],m=s[1],v=s[4],_=s[7],x=s[2],E=s[5],M=s[8],T=o[0],S=o[3],y=o[6],I=o[1],D=o[4],C=o[7],V=o[2],L=o[5],P=o[8];return c[0]=f*T+d*I+p*V,c[3]=f*S+d*D+p*L,c[6]=f*y+d*C+p*P,c[1]=m*T+v*I+_*V,c[4]=m*S+v*D+_*L,c[7]=m*y+v*C+_*P,c[2]=x*T+E*I+M*V,c[5]=x*S+E*D+M*L,c[8]=x*y+E*C+M*P,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[3]*=t,n[6]*=t,n[1]*=t,n[4]*=t,n[7]*=t,n[2]*=t,n[5]*=t,n[8]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],v=t[8];return n*f*v-n*d*m-s*c*v+s*d*p+o*c*m-o*f*p}invert(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],v=t[8],_=v*f-d*m,x=d*p-v*c,E=m*c-f*p,M=n*_+s*x+o*E;if(M===0)return this.set(0,0,0,0,0,0,0,0,0);const T=1/M;return t[0]=_*T,t[1]=(o*m-v*s)*T,t[2]=(d*s-o*f)*T,t[3]=x*T,t[4]=(v*n-o*p)*T,t[5]=(o*c-d*n)*T,t[6]=E*T,t[7]=(s*p-m*n)*T,t[8]=(f*n-s*c)*T,this}transpose(){let t;const n=this.elements;return t=n[1],n[1]=n[3],n[3]=t,t=n[2],n[2]=n[6],n[6]=t,t=n[5],n[5]=n[7],n[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const n=this.elements;return t[0]=n[0],t[1]=n[3],t[2]=n[6],t[3]=n[1],t[4]=n[4],t[5]=n[7],t[6]=n[2],t[7]=n[5],t[8]=n[8],this}setUvTransform(t,n,s,o,c,f,d){const p=Math.cos(c),m=Math.sin(c);return this.set(s*p,s*m,-s*(p*f+m*d)+f+t,-o*m,o*p,-o*(-m*f+p*d)+d+n,0,0,1),this}scale(t,n){return this.premultiply(Hh.makeScale(t,n)),this}rotate(t){return this.premultiply(Hh.makeRotation(-t)),this}translate(t,n){return this.premultiply(Hh.makeTranslation(t,n)),this}makeTranslation(t,n){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,n,0,0,1),this}makeRotation(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,s,n,0,0,0,1),this}makeScale(t,n){return this.set(t,0,0,0,n,0,0,0,1),this}equals(t){const n=this.elements,s=t.elements;for(let o=0;o<9;o++)if(n[o]!==s[o])return!1;return!0}fromArray(t,n=0){for(let s=0;s<9;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t}clone(){return new this.constructor().fromArray(this.elements)}}const Hh=new de;function tS(a){for(let t=a.length-1;t>=0;--t)if(a[t]>=65535)return!0;return!1}function vf(a){return document.createElementNS("http://www.w3.org/1999/xhtml",a)}function DT(){const a=vf("canvas");return a.style.display="block",a}const sy={};function xo(a){a in sy||(sy[a]=!0,console.warn(a))}function UT(a,t,n){return new Promise(function(s,o){function c(){switch(a.clientWaitSync(t,a.SYNC_FLUSH_COMMANDS_BIT,0)){case a.WAIT_FAILED:o();break;case a.TIMEOUT_EXPIRED:setTimeout(c,n);break;default:s()}}setTimeout(c,n)})}function LT(a){const t=a.elements;t[2]=.5*t[2]+.5*t[3],t[6]=.5*t[6]+.5*t[7],t[10]=.5*t[10]+.5*t[11],t[14]=.5*t[14]+.5*t[15]}function OT(a){const t=a.elements;t[11]===-1?(t[10]=-t[10]-1,t[14]=-t[14]):(t[10]=-t[10],t[14]=-t[14]+1)}const ry=new de().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),oy=new de().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function PT(){const a={enabled:!0,workingColorSpace:ko,spaces:{},convert:function(o,c,f){return this.enabled===!1||c===f||!c||!f||(this.spaces[c].transfer===qe&&(o.r=za(o.r),o.g=za(o.g),o.b=za(o.b)),this.spaces[c].primaries!==this.spaces[f].primaries&&(o.applyMatrix3(this.spaces[c].toXYZ),o.applyMatrix3(this.spaces[f].fromXYZ)),this.spaces[f].transfer===qe&&(o.r=To(o.r),o.g=To(o.g),o.b=To(o.b))),o},fromWorkingColorSpace:function(o,c){return this.convert(o,this.workingColorSpace,c)},toWorkingColorSpace:function(o,c){return this.convert(o,c,this.workingColorSpace)},getPrimaries:function(o){return this.spaces[o].primaries},getTransfer:function(o){return o===vs?mf:this.spaces[o].transfer},getLuminanceCoefficients:function(o,c=this.workingColorSpace){return o.fromArray(this.spaces[c].luminanceCoefficients)},define:function(o){Object.assign(this.spaces,o)},_getMatrix:function(o,c,f){return o.copy(this.spaces[c].toXYZ).multiply(this.spaces[f].fromXYZ)},_getDrawingBufferColorSpace:function(o){return this.spaces[o].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(o=this.workingColorSpace){return this.spaces[o].workingColorSpaceConfig.unpackColorSpace}},t=[.64,.33,.3,.6,.15,.06],n=[.2126,.7152,.0722],s=[.3127,.329];return a.define({[ko]:{primaries:t,whitePoint:s,transfer:mf,toXYZ:ry,fromXYZ:oy,luminanceCoefficients:n,workingColorSpaceConfig:{unpackColorSpace:vi},outputColorSpaceConfig:{drawingBufferColorSpace:vi}},[vi]:{primaries:t,whitePoint:s,transfer:qe,toXYZ:ry,fromXYZ:oy,luminanceCoefficients:n,outputColorSpaceConfig:{drawingBufferColorSpace:vi}}}),a}const Pe=PT();function za(a){return a<.04045?a*.0773993808:Math.pow(a*.9478672986+.0521327014,2.4)}function To(a){return a<.0031308?a*12.92:1.055*Math.pow(a,.41666)-.055}let ao;class zT{static getDataURL(t){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let n;if(t instanceof HTMLCanvasElement)n=t;else{ao===void 0&&(ao=vf("canvas")),ao.width=t.width,ao.height=t.height;const s=ao.getContext("2d");t instanceof ImageData?s.putImageData(t,0,0):s.drawImage(t,0,0,t.width,t.height),n=ao}return n.width>2048||n.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",t),n.toDataURL("image/jpeg",.6)):n.toDataURL("image/png")}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const n=vf("canvas");n.width=t.width,n.height=t.height;const s=n.getContext("2d");s.drawImage(t,0,0,t.width,t.height);const o=s.getImageData(0,0,t.width,t.height),c=o.data;for(let f=0;f<c.length;f++)c[f]=za(c[f]/255)*255;return s.putImageData(o,0,0),n}else if(t.data){const n=t.data.slice(0);for(let s=0;s<n.length;s++)n instanceof Uint8Array||n instanceof Uint8ClampedArray?n[s]=Math.floor(za(n[s]/255)*255):n[s]=za(n[s]);return{data:n,width:t.width,height:t.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let IT=0;class eS{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:IT++}),this.uuid=Yo(),this.data=t,this.dataReady=!0,this.version=0}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const s={uuid:this.uuid,url:""},o=this.data;if(o!==null){let c;if(Array.isArray(o)){c=[];for(let f=0,d=o.length;f<d;f++)o[f].isDataTexture?c.push(Gh(o[f].image)):c.push(Gh(o[f]))}else c=Gh(o);s.url=c}return n||(t.images[this.uuid]=s),s}}function Gh(a){return typeof HTMLImageElement<"u"&&a instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&a instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&a instanceof ImageBitmap?zT.getDataURL(a):a.data?{data:Array.from(a.data),width:a.width,height:a.height,type:a.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let BT=0;class ai extends Wo{constructor(t=ai.DEFAULT_IMAGE,n=ai.DEFAULT_MAPPING,s=cr,o=cr,c=$i,f=ur,d=Fi,p=Ia,m=ai.DEFAULT_ANISOTROPY,v=vs){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:BT++}),this.uuid=Yo(),this.name="",this.source=new eS(t),this.mipmaps=[],this.mapping=n,this.channel=0,this.wrapS=s,this.wrapT=o,this.magFilter=c,this.minFilter=f,this.anisotropy=m,this.format=d,this.internalFormat=null,this.type=p,this.offset=new Wt(0,0),this.repeat=new Wt(1,1),this.center=new Wt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new de,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=v,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(t=null){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const s={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(s.userData=this.userData),n||(t.textures[this.uuid]=s),s}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==Vx)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case Xp:t.x=t.x-Math.floor(t.x);break;case cr:t.x=t.x<0?0:1;break;case qp:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case Xp:t.y=t.y-Math.floor(t.y);break;case cr:t.y=t.y<0?0:1;break;case qp:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}ai.DEFAULT_IMAGE=null;ai.DEFAULT_MAPPING=Vx;ai.DEFAULT_ANISOTROPY=1;class We{constructor(t=0,n=0,s=0,o=1){We.prototype.isVector4=!0,this.x=t,this.y=n,this.z=s,this.w=o}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,n,s,o){return this.x=t,this.y=n,this.z=s,this.w=o,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;case 3:this.w=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this.w=t.w+n.w,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this.w+=t.w*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this.w=t.w-n.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const n=this.x,s=this.y,o=this.z,c=this.w,f=t.elements;return this.x=f[0]*n+f[4]*s+f[8]*o+f[12]*c,this.y=f[1]*n+f[5]*s+f[9]*o+f[13]*c,this.z=f[2]*n+f[6]*s+f[10]*o+f[14]*c,this.w=f[3]*n+f[7]*s+f[11]*o+f[15]*c,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const n=Math.sqrt(1-t.w*t.w);return n<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/n,this.y=t.y/n,this.z=t.z/n),this}setAxisAngleFromRotationMatrix(t){let n,s,o,c;const p=t.elements,m=p[0],v=p[4],_=p[8],x=p[1],E=p[5],M=p[9],T=p[2],S=p[6],y=p[10];if(Math.abs(v-x)<.01&&Math.abs(_-T)<.01&&Math.abs(M-S)<.01){if(Math.abs(v+x)<.1&&Math.abs(_+T)<.1&&Math.abs(M+S)<.1&&Math.abs(m+E+y-3)<.1)return this.set(1,0,0,0),this;n=Math.PI;const D=(m+1)/2,C=(E+1)/2,V=(y+1)/2,L=(v+x)/4,P=(_+T)/4,G=(M+S)/4;return D>C&&D>V?D<.01?(s=0,o=.707106781,c=.707106781):(s=Math.sqrt(D),o=L/s,c=P/s):C>V?C<.01?(s=.707106781,o=0,c=.707106781):(o=Math.sqrt(C),s=L/o,c=G/o):V<.01?(s=.707106781,o=.707106781,c=0):(c=Math.sqrt(V),s=P/c,o=G/c),this.set(s,o,c,n),this}let I=Math.sqrt((S-M)*(S-M)+(_-T)*(_-T)+(x-v)*(x-v));return Math.abs(I)<.001&&(I=1),this.x=(S-M)/I,this.y=(_-T)/I,this.z=(x-v)/I,this.w=Math.acos((m+E+y-1)/2),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this.w=n[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this.w=ge(this.w,t.w,n.w),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this.w=ge(this.w,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this.w+=(t.w-this.w)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this.w=t.w+(n.w-t.w)*s,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this.w=t[n+3],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t[n+3]=this.w,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this.w=t.getW(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class FT extends Wo{constructor(t=1,n=1,s={}){super(),this.isRenderTarget=!0,this.width=t,this.height=n,this.depth=1,this.scissor=new We(0,0,t,n),this.scissorTest=!1,this.viewport=new We(0,0,t,n);const o={width:t,height:n,depth:1};s=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:$i,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},s);const c=new ai(o,s.mapping,s.wrapS,s.wrapT,s.magFilter,s.minFilter,s.format,s.type,s.anisotropy,s.colorSpace);c.flipY=!1,c.generateMipmaps=s.generateMipmaps,c.internalFormat=s.internalFormat,this.textures=[];const f=s.count;for(let d=0;d<f;d++)this.textures[d]=c.clone(),this.textures[d].isRenderTargetTexture=!0;this.depthBuffer=s.depthBuffer,this.stencilBuffer=s.stencilBuffer,this.resolveDepthBuffer=s.resolveDepthBuffer,this.resolveStencilBuffer=s.resolveStencilBuffer,this.depthTexture=s.depthTexture,this.samples=s.samples}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}setSize(t,n,s=1){if(this.width!==t||this.height!==n||this.depth!==s){this.width=t,this.height=n,this.depth=s;for(let o=0,c=this.textures.length;o<c;o++)this.textures[o].image.width=t,this.textures[o].image.height=n,this.textures[o].image.depth=s;this.dispose()}this.viewport.set(0,0,t,n),this.scissor.set(0,0,t,n)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let s=0,o=t.textures.length;s<o;s++)this.textures[s]=t.textures[s].clone(),this.textures[s].isRenderTargetTexture=!0;const n=Object.assign({},t.texture.image);return this.texture.source=new eS(n),this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Gi extends FT{constructor(t=1,n=1,s={}){super(t,n,s),this.isWebGLRenderTarget=!0}}class nS extends ai{constructor(t=null,n=1,s=1,o=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:n,height:s,depth:o},this.magFilter=Hi,this.minFilter=Hi,this.wrapR=cr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class HT extends ai{constructor(t=null,n=1,s=1,o=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:n,height:s,depth:o},this.magFilter=Hi,this.minFilter=Hi,this.wrapR=cr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class gc{constructor(t=0,n=0,s=0,o=1){this.isQuaternion=!0,this._x=t,this._y=n,this._z=s,this._w=o}static slerpFlat(t,n,s,o,c,f,d){let p=s[o+0],m=s[o+1],v=s[o+2],_=s[o+3];const x=c[f+0],E=c[f+1],M=c[f+2],T=c[f+3];if(d===0){t[n+0]=p,t[n+1]=m,t[n+2]=v,t[n+3]=_;return}if(d===1){t[n+0]=x,t[n+1]=E,t[n+2]=M,t[n+3]=T;return}if(_!==T||p!==x||m!==E||v!==M){let S=1-d;const y=p*x+m*E+v*M+_*T,I=y>=0?1:-1,D=1-y*y;if(D>Number.EPSILON){const V=Math.sqrt(D),L=Math.atan2(V,y*I);S=Math.sin(S*L)/V,d=Math.sin(d*L)/V}const C=d*I;if(p=p*S+x*C,m=m*S+E*C,v=v*S+M*C,_=_*S+T*C,S===1-d){const V=1/Math.sqrt(p*p+m*m+v*v+_*_);p*=V,m*=V,v*=V,_*=V}}t[n]=p,t[n+1]=m,t[n+2]=v,t[n+3]=_}static multiplyQuaternionsFlat(t,n,s,o,c,f){const d=s[o],p=s[o+1],m=s[o+2],v=s[o+3],_=c[f],x=c[f+1],E=c[f+2],M=c[f+3];return t[n]=d*M+v*_+p*E-m*x,t[n+1]=p*M+v*x+m*_-d*E,t[n+2]=m*M+v*E+d*x-p*_,t[n+3]=v*M-d*_-p*x-m*E,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,n,s,o){return this._x=t,this._y=n,this._z=s,this._w=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,n=!0){const s=t._x,o=t._y,c=t._z,f=t._order,d=Math.cos,p=Math.sin,m=d(s/2),v=d(o/2),_=d(c/2),x=p(s/2),E=p(o/2),M=p(c/2);switch(f){case"XYZ":this._x=x*v*_+m*E*M,this._y=m*E*_-x*v*M,this._z=m*v*M+x*E*_,this._w=m*v*_-x*E*M;break;case"YXZ":this._x=x*v*_+m*E*M,this._y=m*E*_-x*v*M,this._z=m*v*M-x*E*_,this._w=m*v*_+x*E*M;break;case"ZXY":this._x=x*v*_-m*E*M,this._y=m*E*_+x*v*M,this._z=m*v*M+x*E*_,this._w=m*v*_-x*E*M;break;case"ZYX":this._x=x*v*_-m*E*M,this._y=m*E*_+x*v*M,this._z=m*v*M-x*E*_,this._w=m*v*_+x*E*M;break;case"YZX":this._x=x*v*_+m*E*M,this._y=m*E*_+x*v*M,this._z=m*v*M-x*E*_,this._w=m*v*_-x*E*M;break;case"XZY":this._x=x*v*_-m*E*M,this._y=m*E*_-x*v*M,this._z=m*v*M+x*E*_,this._w=m*v*_+x*E*M;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+f)}return n===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,n){const s=n/2,o=Math.sin(s);return this._x=t.x*o,this._y=t.y*o,this._z=t.z*o,this._w=Math.cos(s),this._onChangeCallback(),this}setFromRotationMatrix(t){const n=t.elements,s=n[0],o=n[4],c=n[8],f=n[1],d=n[5],p=n[9],m=n[2],v=n[6],_=n[10],x=s+d+_;if(x>0){const E=.5/Math.sqrt(x+1);this._w=.25/E,this._x=(v-p)*E,this._y=(c-m)*E,this._z=(f-o)*E}else if(s>d&&s>_){const E=2*Math.sqrt(1+s-d-_);this._w=(v-p)/E,this._x=.25*E,this._y=(o+f)/E,this._z=(c+m)/E}else if(d>_){const E=2*Math.sqrt(1+d-s-_);this._w=(c-m)/E,this._x=(o+f)/E,this._y=.25*E,this._z=(p+v)/E}else{const E=2*Math.sqrt(1+_-s-d);this._w=(f-o)/E,this._x=(c+m)/E,this._y=(p+v)/E,this._z=.25*E}return this._onChangeCallback(),this}setFromUnitVectors(t,n){let s=t.dot(n)+1;return s<Number.EPSILON?(s=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=s):(this._x=0,this._y=-t.z,this._z=t.y,this._w=s)):(this._x=t.y*n.z-t.z*n.y,this._y=t.z*n.x-t.x*n.z,this._z=t.x*n.y-t.y*n.x,this._w=s),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(ge(this.dot(t),-1,1)))}rotateTowards(t,n){const s=this.angleTo(t);if(s===0)return this;const o=Math.min(1,n/s);return this.slerp(t,o),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,n){const s=t._x,o=t._y,c=t._z,f=t._w,d=n._x,p=n._y,m=n._z,v=n._w;return this._x=s*v+f*d+o*m-c*p,this._y=o*v+f*p+c*d-s*m,this._z=c*v+f*m+s*p-o*d,this._w=f*v-s*d-o*p-c*m,this._onChangeCallback(),this}slerp(t,n){if(n===0)return this;if(n===1)return this.copy(t);const s=this._x,o=this._y,c=this._z,f=this._w;let d=f*t._w+s*t._x+o*t._y+c*t._z;if(d<0?(this._w=-t._w,this._x=-t._x,this._y=-t._y,this._z=-t._z,d=-d):this.copy(t),d>=1)return this._w=f,this._x=s,this._y=o,this._z=c,this;const p=1-d*d;if(p<=Number.EPSILON){const E=1-n;return this._w=E*f+n*this._w,this._x=E*s+n*this._x,this._y=E*o+n*this._y,this._z=E*c+n*this._z,this.normalize(),this}const m=Math.sqrt(p),v=Math.atan2(m,d),_=Math.sin((1-n)*v)/m,x=Math.sin(n*v)/m;return this._w=f*_+this._w*x,this._x=s*_+this._x*x,this._y=o*_+this._y*x,this._z=c*_+this._z*x,this._onChangeCallback(),this}slerpQuaternions(t,n,s){return this.copy(t).slerp(n,s)}random(){const t=2*Math.PI*Math.random(),n=2*Math.PI*Math.random(),s=Math.random(),o=Math.sqrt(1-s),c=Math.sqrt(s);return this.set(o*Math.sin(t),o*Math.cos(t),c*Math.sin(n),c*Math.cos(n))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,n=0){return this._x=t[n],this._y=t[n+1],this._z=t[n+2],this._w=t[n+3],this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._w,t}fromBufferAttribute(t,n){return this._x=t.getX(n),this._y=t.getY(n),this._z=t.getZ(n),this._w=t.getW(n),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class W{constructor(t=0,n=0,s=0){W.prototype.isVector3=!0,this.x=t,this.y=n,this.z=s}set(t,n,s){return s===void 0&&(s=this.z),this.x=t,this.y=n,this.z=s,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,n){return this.x=t.x*n.x,this.y=t.y*n.y,this.z=t.z*n.z,this}applyEuler(t){return this.applyQuaternion(ly.setFromEuler(t))}applyAxisAngle(t,n){return this.applyQuaternion(ly.setFromAxisAngle(t,n))}applyMatrix3(t){const n=this.x,s=this.y,o=this.z,c=t.elements;return this.x=c[0]*n+c[3]*s+c[6]*o,this.y=c[1]*n+c[4]*s+c[7]*o,this.z=c[2]*n+c[5]*s+c[8]*o,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const n=this.x,s=this.y,o=this.z,c=t.elements,f=1/(c[3]*n+c[7]*s+c[11]*o+c[15]);return this.x=(c[0]*n+c[4]*s+c[8]*o+c[12])*f,this.y=(c[1]*n+c[5]*s+c[9]*o+c[13])*f,this.z=(c[2]*n+c[6]*s+c[10]*o+c[14])*f,this}applyQuaternion(t){const n=this.x,s=this.y,o=this.z,c=t.x,f=t.y,d=t.z,p=t.w,m=2*(f*o-d*s),v=2*(d*n-c*o),_=2*(c*s-f*n);return this.x=n+p*m+f*_-d*v,this.y=s+p*v+d*m-c*_,this.z=o+p*_+c*v-f*m,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const n=this.x,s=this.y,o=this.z,c=t.elements;return this.x=c[0]*n+c[4]*s+c[8]*o,this.y=c[1]*n+c[5]*s+c[9]*o,this.z=c[2]*n+c[6]*s+c[10]*o,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,n){const s=t.x,o=t.y,c=t.z,f=n.x,d=n.y,p=n.z;return this.x=o*p-c*d,this.y=c*f-s*p,this.z=s*d-o*f,this}projectOnVector(t){const n=t.lengthSq();if(n===0)return this.set(0,0,0);const s=t.dot(this)/n;return this.copy(t).multiplyScalar(s)}projectOnPlane(t){return Vh.copy(this).projectOnVector(t),this.sub(Vh)}reflect(t){return this.sub(Vh.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(ge(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y,o=this.z-t.z;return n*n+s*s+o*o}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,n,s){const o=Math.sin(n)*t;return this.x=o*Math.sin(s),this.y=Math.cos(n)*t,this.z=o*Math.cos(s),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,n,s){return this.x=t*Math.sin(n),this.y=s,this.z=t*Math.cos(n),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this}setFromMatrixScale(t){const n=this.setFromMatrixColumn(t,0).length(),s=this.setFromMatrixColumn(t,1).length(),o=this.setFromMatrixColumn(t,2).length();return this.x=n,this.y=s,this.z=o,this}setFromMatrixColumn(t,n){return this.fromArray(t.elements,n*4)}setFromMatrix3Column(t,n){return this.fromArray(t.elements,n*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,n=Math.random()*2-1,s=Math.sqrt(1-n*n);return this.x=s*Math.cos(t),this.y=n,this.z=s*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Vh=new W,ly=new gc;class vc{constructor(t=new W(1/0,1/0,1/0),n=new W(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=n}set(t,n){return this.min.copy(t),this.max.copy(n),this}setFromArray(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n+=3)this.expandByPoint(Oi.fromArray(t,n));return this}setFromBufferAttribute(t){this.makeEmpty();for(let n=0,s=t.count;n<s;n++)this.expandByPoint(Oi.fromBufferAttribute(t,n));return this}setFromPoints(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n++)this.expandByPoint(t[n]);return this}setFromCenterAndSize(t,n){const s=Oi.copy(n).multiplyScalar(.5);return this.min.copy(t).sub(s),this.max.copy(t).add(s),this}setFromObject(t,n=!1){return this.makeEmpty(),this.expandByObject(t,n)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,n=!1){t.updateWorldMatrix(!1,!1);const s=t.geometry;if(s!==void 0){const c=s.getAttribute("position");if(n===!0&&c!==void 0&&t.isInstancedMesh!==!0)for(let f=0,d=c.count;f<d;f++)t.isMesh===!0?t.getVertexPosition(f,Oi):Oi.fromBufferAttribute(c,f),Oi.applyMatrix4(t.matrixWorld),this.expandByPoint(Oi);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),Pu.copy(t.boundingBox)):(s.boundingBox===null&&s.computeBoundingBox(),Pu.copy(s.boundingBox)),Pu.applyMatrix4(t.matrixWorld),this.union(Pu)}const o=t.children;for(let c=0,f=o.length;c<f;c++)this.expandByObject(o[c],n);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,n){return n.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Oi),Oi.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let n,s;return t.normal.x>0?(n=t.normal.x*this.min.x,s=t.normal.x*this.max.x):(n=t.normal.x*this.max.x,s=t.normal.x*this.min.x),t.normal.y>0?(n+=t.normal.y*this.min.y,s+=t.normal.y*this.max.y):(n+=t.normal.y*this.max.y,s+=t.normal.y*this.min.y),t.normal.z>0?(n+=t.normal.z*this.min.z,s+=t.normal.z*this.max.z):(n+=t.normal.z*this.max.z,s+=t.normal.z*this.min.z),n<=-t.constant&&s>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(jl),zu.subVectors(this.max,jl),so.subVectors(t.a,jl),ro.subVectors(t.b,jl),oo.subVectors(t.c,jl),us.subVectors(ro,so),fs.subVectors(oo,ro),Qs.subVectors(so,oo);let n=[0,-us.z,us.y,0,-fs.z,fs.y,0,-Qs.z,Qs.y,us.z,0,-us.x,fs.z,0,-fs.x,Qs.z,0,-Qs.x,-us.y,us.x,0,-fs.y,fs.x,0,-Qs.y,Qs.x,0];return!jh(n,so,ro,oo,zu)||(n=[1,0,0,0,1,0,0,0,1],!jh(n,so,ro,oo,zu))?!1:(Iu.crossVectors(us,fs),n=[Iu.x,Iu.y,Iu.z],jh(n,so,ro,oo,zu))}clampPoint(t,n){return n.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Oi).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Oi).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(Sa[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),Sa[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),Sa[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),Sa[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),Sa[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),Sa[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),Sa[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),Sa[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(Sa),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}}const Sa=[new W,new W,new W,new W,new W,new W,new W,new W],Oi=new W,Pu=new vc,so=new W,ro=new W,oo=new W,us=new W,fs=new W,Qs=new W,jl=new W,zu=new W,Iu=new W,Zs=new W;function jh(a,t,n,s,o){for(let c=0,f=a.length-3;c<=f;c+=3){Zs.fromArray(a,c);const d=o.x*Math.abs(Zs.x)+o.y*Math.abs(Zs.y)+o.z*Math.abs(Zs.z),p=t.dot(Zs),m=n.dot(Zs),v=s.dot(Zs);if(Math.max(-Math.max(p,m,v),Math.min(p,m,v))>d)return!1}return!0}const GT=new vc,kl=new W,kh=new W;class Fm{constructor(t=new W,n=-1){this.isSphere=!0,this.center=t,this.radius=n}set(t,n){return this.center.copy(t),this.radius=n,this}setFromPoints(t,n){const s=this.center;n!==void 0?s.copy(n):GT.setFromPoints(t).getCenter(s);let o=0;for(let c=0,f=t.length;c<f;c++)o=Math.max(o,s.distanceToSquared(t[c]));return this.radius=Math.sqrt(o),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const n=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=n*n}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,n){const s=this.center.distanceToSquared(t);return n.copy(t),s>this.radius*this.radius&&(n.sub(this.center).normalize(),n.multiplyScalar(this.radius).add(this.center)),n}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;kl.subVectors(t,this.center);const n=kl.lengthSq();if(n>this.radius*this.radius){const s=Math.sqrt(n),o=(s-this.radius)*.5;this.center.addScaledVector(kl,o/s),this.radius+=o}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(kh.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(kl.copy(t.center).add(kh)),this.expandByPoint(kl.copy(t.center).sub(kh))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ma=new W,Xh=new W,Bu=new W,ds=new W,qh=new W,Fu=new W,Wh=new W;class VT{constructor(t=new W,n=new W(0,0,-1)){this.origin=t,this.direction=n}set(t,n){return this.origin.copy(t),this.direction.copy(n),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,n){return n.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,Ma)),this}closestPointToPoint(t,n){n.subVectors(t,this.origin);const s=n.dot(this.direction);return s<0?n.copy(this.origin):n.copy(this.origin).addScaledVector(this.direction,s)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const n=Ma.subVectors(t,this.origin).dot(this.direction);return n<0?this.origin.distanceToSquared(t):(Ma.copy(this.origin).addScaledVector(this.direction,n),Ma.distanceToSquared(t))}distanceSqToSegment(t,n,s,o){Xh.copy(t).add(n).multiplyScalar(.5),Bu.copy(n).sub(t).normalize(),ds.copy(this.origin).sub(Xh);const c=t.distanceTo(n)*.5,f=-this.direction.dot(Bu),d=ds.dot(this.direction),p=-ds.dot(Bu),m=ds.lengthSq(),v=Math.abs(1-f*f);let _,x,E,M;if(v>0)if(_=f*p-d,x=f*d-p,M=c*v,_>=0)if(x>=-M)if(x<=M){const T=1/v;_*=T,x*=T,E=_*(_+f*x+2*d)+x*(f*_+x+2*p)+m}else x=c,_=Math.max(0,-(f*x+d)),E=-_*_+x*(x+2*p)+m;else x=-c,_=Math.max(0,-(f*x+d)),E=-_*_+x*(x+2*p)+m;else x<=-M?(_=Math.max(0,-(-f*c+d)),x=_>0?-c:Math.min(Math.max(-c,-p),c),E=-_*_+x*(x+2*p)+m):x<=M?(_=0,x=Math.min(Math.max(-c,-p),c),E=x*(x+2*p)+m):(_=Math.max(0,-(f*c+d)),x=_>0?c:Math.min(Math.max(-c,-p),c),E=-_*_+x*(x+2*p)+m);else x=f>0?-c:c,_=Math.max(0,-(f*x+d)),E=-_*_+x*(x+2*p)+m;return s&&s.copy(this.origin).addScaledVector(this.direction,_),o&&o.copy(Xh).addScaledVector(Bu,x),E}intersectSphere(t,n){Ma.subVectors(t.center,this.origin);const s=Ma.dot(this.direction),o=Ma.dot(Ma)-s*s,c=t.radius*t.radius;if(o>c)return null;const f=Math.sqrt(c-o),d=s-f,p=s+f;return p<0?null:d<0?this.at(p,n):this.at(d,n)}intersectsSphere(t){return this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const n=t.normal.dot(this.direction);if(n===0)return t.distanceToPoint(this.origin)===0?0:null;const s=-(this.origin.dot(t.normal)+t.constant)/n;return s>=0?s:null}intersectPlane(t,n){const s=this.distanceToPlane(t);return s===null?null:this.at(s,n)}intersectsPlane(t){const n=t.distanceToPoint(this.origin);return n===0||t.normal.dot(this.direction)*n<0}intersectBox(t,n){let s,o,c,f,d,p;const m=1/this.direction.x,v=1/this.direction.y,_=1/this.direction.z,x=this.origin;return m>=0?(s=(t.min.x-x.x)*m,o=(t.max.x-x.x)*m):(s=(t.max.x-x.x)*m,o=(t.min.x-x.x)*m),v>=0?(c=(t.min.y-x.y)*v,f=(t.max.y-x.y)*v):(c=(t.max.y-x.y)*v,f=(t.min.y-x.y)*v),s>f||c>o||((c>s||isNaN(s))&&(s=c),(f<o||isNaN(o))&&(o=f),_>=0?(d=(t.min.z-x.z)*_,p=(t.max.z-x.z)*_):(d=(t.max.z-x.z)*_,p=(t.min.z-x.z)*_),s>p||d>o)||((d>s||s!==s)&&(s=d),(p<o||o!==o)&&(o=p),o<0)?null:this.at(s>=0?s:o,n)}intersectsBox(t){return this.intersectBox(t,Ma)!==null}intersectTriangle(t,n,s,o,c){qh.subVectors(n,t),Fu.subVectors(s,t),Wh.crossVectors(qh,Fu);let f=this.direction.dot(Wh),d;if(f>0){if(o)return null;d=1}else if(f<0)d=-1,f=-f;else return null;ds.subVectors(this.origin,t);const p=d*this.direction.dot(Fu.crossVectors(ds,Fu));if(p<0)return null;const m=d*this.direction.dot(qh.cross(ds));if(m<0||p+m>f)return null;const v=-d*ds.dot(Wh);return v<0?null:this.at(v/f,c)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class an{constructor(t,n,s,o,c,f,d,p,m,v,_,x,E,M,T,S){an.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,n,s,o,c,f,d,p,m,v,_,x,E,M,T,S)}set(t,n,s,o,c,f,d,p,m,v,_,x,E,M,T,S){const y=this.elements;return y[0]=t,y[4]=n,y[8]=s,y[12]=o,y[1]=c,y[5]=f,y[9]=d,y[13]=p,y[2]=m,y[6]=v,y[10]=_,y[14]=x,y[3]=E,y[7]=M,y[11]=T,y[15]=S,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new an().fromArray(this.elements)}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],n[9]=s[9],n[10]=s[10],n[11]=s[11],n[12]=s[12],n[13]=s[13],n[14]=s[14],n[15]=s[15],this}copyPosition(t){const n=this.elements,s=t.elements;return n[12]=s[12],n[13]=s[13],n[14]=s[14],this}setFromMatrix3(t){const n=t.elements;return this.set(n[0],n[3],n[6],0,n[1],n[4],n[7],0,n[2],n[5],n[8],0,0,0,0,1),this}extractBasis(t,n,s){return t.setFromMatrixColumn(this,0),n.setFromMatrixColumn(this,1),s.setFromMatrixColumn(this,2),this}makeBasis(t,n,s){return this.set(t.x,n.x,s.x,0,t.y,n.y,s.y,0,t.z,n.z,s.z,0,0,0,0,1),this}extractRotation(t){const n=this.elements,s=t.elements,o=1/lo.setFromMatrixColumn(t,0).length(),c=1/lo.setFromMatrixColumn(t,1).length(),f=1/lo.setFromMatrixColumn(t,2).length();return n[0]=s[0]*o,n[1]=s[1]*o,n[2]=s[2]*o,n[3]=0,n[4]=s[4]*c,n[5]=s[5]*c,n[6]=s[6]*c,n[7]=0,n[8]=s[8]*f,n[9]=s[9]*f,n[10]=s[10]*f,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromEuler(t){const n=this.elements,s=t.x,o=t.y,c=t.z,f=Math.cos(s),d=Math.sin(s),p=Math.cos(o),m=Math.sin(o),v=Math.cos(c),_=Math.sin(c);if(t.order==="XYZ"){const x=f*v,E=f*_,M=d*v,T=d*_;n[0]=p*v,n[4]=-p*_,n[8]=m,n[1]=E+M*m,n[5]=x-T*m,n[9]=-d*p,n[2]=T-x*m,n[6]=M+E*m,n[10]=f*p}else if(t.order==="YXZ"){const x=p*v,E=p*_,M=m*v,T=m*_;n[0]=x+T*d,n[4]=M*d-E,n[8]=f*m,n[1]=f*_,n[5]=f*v,n[9]=-d,n[2]=E*d-M,n[6]=T+x*d,n[10]=f*p}else if(t.order==="ZXY"){const x=p*v,E=p*_,M=m*v,T=m*_;n[0]=x-T*d,n[4]=-f*_,n[8]=M+E*d,n[1]=E+M*d,n[5]=f*v,n[9]=T-x*d,n[2]=-f*m,n[6]=d,n[10]=f*p}else if(t.order==="ZYX"){const x=f*v,E=f*_,M=d*v,T=d*_;n[0]=p*v,n[4]=M*m-E,n[8]=x*m+T,n[1]=p*_,n[5]=T*m+x,n[9]=E*m-M,n[2]=-m,n[6]=d*p,n[10]=f*p}else if(t.order==="YZX"){const x=f*p,E=f*m,M=d*p,T=d*m;n[0]=p*v,n[4]=T-x*_,n[8]=M*_+E,n[1]=_,n[5]=f*v,n[9]=-d*v,n[2]=-m*v,n[6]=E*_+M,n[10]=x-T*_}else if(t.order==="XZY"){const x=f*p,E=f*m,M=d*p,T=d*m;n[0]=p*v,n[4]=-_,n[8]=m*v,n[1]=x*_+T,n[5]=f*v,n[9]=E*_-M,n[2]=M*_-E,n[6]=d*v,n[10]=T*_+x}return n[3]=0,n[7]=0,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromQuaternion(t){return this.compose(jT,t,kT)}lookAt(t,n,s){const o=this.elements;return hi.subVectors(t,n),hi.lengthSq()===0&&(hi.z=1),hi.normalize(),hs.crossVectors(s,hi),hs.lengthSq()===0&&(Math.abs(s.z)===1?hi.x+=1e-4:hi.z+=1e-4,hi.normalize(),hs.crossVectors(s,hi)),hs.normalize(),Hu.crossVectors(hi,hs),o[0]=hs.x,o[4]=Hu.x,o[8]=hi.x,o[1]=hs.y,o[5]=Hu.y,o[9]=hi.y,o[2]=hs.z,o[6]=Hu.z,o[10]=hi.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,o=n.elements,c=this.elements,f=s[0],d=s[4],p=s[8],m=s[12],v=s[1],_=s[5],x=s[9],E=s[13],M=s[2],T=s[6],S=s[10],y=s[14],I=s[3],D=s[7],C=s[11],V=s[15],L=o[0],P=o[4],G=o[8],U=o[12],N=o[1],H=o[5],ut=o[9],ot=o[13],mt=o[2],ct=o[6],B=o[10],Z=o[14],$=o[3],Et=o[7],At=o[11],z=o[15];return c[0]=f*L+d*N+p*mt+m*$,c[4]=f*P+d*H+p*ct+m*Et,c[8]=f*G+d*ut+p*B+m*At,c[12]=f*U+d*ot+p*Z+m*z,c[1]=v*L+_*N+x*mt+E*$,c[5]=v*P+_*H+x*ct+E*Et,c[9]=v*G+_*ut+x*B+E*At,c[13]=v*U+_*ot+x*Z+E*z,c[2]=M*L+T*N+S*mt+y*$,c[6]=M*P+T*H+S*ct+y*Et,c[10]=M*G+T*ut+S*B+y*At,c[14]=M*U+T*ot+S*Z+y*z,c[3]=I*L+D*N+C*mt+V*$,c[7]=I*P+D*H+C*ct+V*Et,c[11]=I*G+D*ut+C*B+V*At,c[15]=I*U+D*ot+C*Z+V*z,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[4]*=t,n[8]*=t,n[12]*=t,n[1]*=t,n[5]*=t,n[9]*=t,n[13]*=t,n[2]*=t,n[6]*=t,n[10]*=t,n[14]*=t,n[3]*=t,n[7]*=t,n[11]*=t,n[15]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[4],o=t[8],c=t[12],f=t[1],d=t[5],p=t[9],m=t[13],v=t[2],_=t[6],x=t[10],E=t[14],M=t[3],T=t[7],S=t[11],y=t[15];return M*(+c*p*_-o*m*_-c*d*x+s*m*x+o*d*E-s*p*E)+T*(+n*p*E-n*m*x+c*f*x-o*f*E+o*m*v-c*p*v)+S*(+n*m*_-n*d*E-c*f*_+s*f*E+c*d*v-s*m*v)+y*(-o*d*v-n*p*_+n*d*x+o*f*_-s*f*x+s*p*v)}transpose(){const t=this.elements;let n;return n=t[1],t[1]=t[4],t[4]=n,n=t[2],t[2]=t[8],t[8]=n,n=t[6],t[6]=t[9],t[9]=n,n=t[3],t[3]=t[12],t[12]=n,n=t[7],t[7]=t[13],t[13]=n,n=t[11],t[11]=t[14],t[14]=n,this}setPosition(t,n,s){const o=this.elements;return t.isVector3?(o[12]=t.x,o[13]=t.y,o[14]=t.z):(o[12]=t,o[13]=n,o[14]=s),this}invert(){const t=this.elements,n=t[0],s=t[1],o=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],v=t[8],_=t[9],x=t[10],E=t[11],M=t[12],T=t[13],S=t[14],y=t[15],I=_*S*m-T*x*m+T*p*E-d*S*E-_*p*y+d*x*y,D=M*x*m-v*S*m-M*p*E+f*S*E+v*p*y-f*x*y,C=v*T*m-M*_*m+M*d*E-f*T*E-v*d*y+f*_*y,V=M*_*p-v*T*p-M*d*x+f*T*x+v*d*S-f*_*S,L=n*I+s*D+o*C+c*V;if(L===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/L;return t[0]=I*P,t[1]=(T*x*c-_*S*c-T*o*E+s*S*E+_*o*y-s*x*y)*P,t[2]=(d*S*c-T*p*c+T*o*m-s*S*m-d*o*y+s*p*y)*P,t[3]=(_*p*c-d*x*c-_*o*m+s*x*m+d*o*E-s*p*E)*P,t[4]=D*P,t[5]=(v*S*c-M*x*c+M*o*E-n*S*E-v*o*y+n*x*y)*P,t[6]=(M*p*c-f*S*c-M*o*m+n*S*m+f*o*y-n*p*y)*P,t[7]=(f*x*c-v*p*c+v*o*m-n*x*m-f*o*E+n*p*E)*P,t[8]=C*P,t[9]=(M*_*c-v*T*c-M*s*E+n*T*E+v*s*y-n*_*y)*P,t[10]=(f*T*c-M*d*c+M*s*m-n*T*m-f*s*y+n*d*y)*P,t[11]=(v*d*c-f*_*c-v*s*m+n*_*m+f*s*E-n*d*E)*P,t[12]=V*P,t[13]=(v*T*o-M*_*o+M*s*x-n*T*x-v*s*S+n*_*S)*P,t[14]=(M*d*o-f*T*o-M*s*p+n*T*p+f*s*S-n*d*S)*P,t[15]=(f*_*o-v*d*o+v*s*p-n*_*p-f*s*x+n*d*x)*P,this}scale(t){const n=this.elements,s=t.x,o=t.y,c=t.z;return n[0]*=s,n[4]*=o,n[8]*=c,n[1]*=s,n[5]*=o,n[9]*=c,n[2]*=s,n[6]*=o,n[10]*=c,n[3]*=s,n[7]*=o,n[11]*=c,this}getMaxScaleOnAxis(){const t=this.elements,n=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],s=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],o=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(n,s,o))}makeTranslation(t,n,s){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,n,0,0,1,s,0,0,0,1),this}makeRotationX(t){const n=Math.cos(t),s=Math.sin(t);return this.set(1,0,0,0,0,n,-s,0,0,s,n,0,0,0,0,1),this}makeRotationY(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,0,s,0,0,1,0,0,-s,0,n,0,0,0,0,1),this}makeRotationZ(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,0,s,n,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,n){const s=Math.cos(n),o=Math.sin(n),c=1-s,f=t.x,d=t.y,p=t.z,m=c*f,v=c*d;return this.set(m*f+s,m*d-o*p,m*p+o*d,0,m*d+o*p,v*d+s,v*p-o*f,0,m*p-o*d,v*p+o*f,c*p*p+s,0,0,0,0,1),this}makeScale(t,n,s){return this.set(t,0,0,0,0,n,0,0,0,0,s,0,0,0,0,1),this}makeShear(t,n,s,o,c,f){return this.set(1,s,c,0,t,1,f,0,n,o,1,0,0,0,0,1),this}compose(t,n,s){const o=this.elements,c=n._x,f=n._y,d=n._z,p=n._w,m=c+c,v=f+f,_=d+d,x=c*m,E=c*v,M=c*_,T=f*v,S=f*_,y=d*_,I=p*m,D=p*v,C=p*_,V=s.x,L=s.y,P=s.z;return o[0]=(1-(T+y))*V,o[1]=(E+C)*V,o[2]=(M-D)*V,o[3]=0,o[4]=(E-C)*L,o[5]=(1-(x+y))*L,o[6]=(S+I)*L,o[7]=0,o[8]=(M+D)*P,o[9]=(S-I)*P,o[10]=(1-(x+T))*P,o[11]=0,o[12]=t.x,o[13]=t.y,o[14]=t.z,o[15]=1,this}decompose(t,n,s){const o=this.elements;let c=lo.set(o[0],o[1],o[2]).length();const f=lo.set(o[4],o[5],o[6]).length(),d=lo.set(o[8],o[9],o[10]).length();this.determinant()<0&&(c=-c),t.x=o[12],t.y=o[13],t.z=o[14],Pi.copy(this);const m=1/c,v=1/f,_=1/d;return Pi.elements[0]*=m,Pi.elements[1]*=m,Pi.elements[2]*=m,Pi.elements[4]*=v,Pi.elements[5]*=v,Pi.elements[6]*=v,Pi.elements[8]*=_,Pi.elements[9]*=_,Pi.elements[10]*=_,n.setFromRotationMatrix(Pi),s.x=c,s.y=f,s.z=d,this}makePerspective(t,n,s,o,c,f,d=Ua){const p=this.elements,m=2*c/(n-t),v=2*c/(s-o),_=(n+t)/(n-t),x=(s+o)/(s-o);let E,M;if(d===Ua)E=-(f+c)/(f-c),M=-2*f*c/(f-c);else if(d===gf)E=-f/(f-c),M=-f*c/(f-c);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+d);return p[0]=m,p[4]=0,p[8]=_,p[12]=0,p[1]=0,p[5]=v,p[9]=x,p[13]=0,p[2]=0,p[6]=0,p[10]=E,p[14]=M,p[3]=0,p[7]=0,p[11]=-1,p[15]=0,this}makeOrthographic(t,n,s,o,c,f,d=Ua){const p=this.elements,m=1/(n-t),v=1/(s-o),_=1/(f-c),x=(n+t)*m,E=(s+o)*v;let M,T;if(d===Ua)M=(f+c)*_,T=-2*_;else if(d===gf)M=c*_,T=-1*_;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+d);return p[0]=2*m,p[4]=0,p[8]=0,p[12]=-x,p[1]=0,p[5]=2*v,p[9]=0,p[13]=-E,p[2]=0,p[6]=0,p[10]=T,p[14]=-M,p[3]=0,p[7]=0,p[11]=0,p[15]=1,this}equals(t){const n=this.elements,s=t.elements;for(let o=0;o<16;o++)if(n[o]!==s[o])return!1;return!0}fromArray(t,n=0){for(let s=0;s<16;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t[n+9]=s[9],t[n+10]=s[10],t[n+11]=s[11],t[n+12]=s[12],t[n+13]=s[13],t[n+14]=s[14],t[n+15]=s[15],t}}const lo=new W,Pi=new an,jT=new W(0,0,0),kT=new W(1,1,1),hs=new W,Hu=new W,hi=new W,cy=new an,uy=new gc;class Ba{constructor(t=0,n=0,s=0,o=Ba.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=n,this._z=s,this._order=o}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,n,s,o=this._order){return this._x=t,this._y=n,this._z=s,this._order=o,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,n=this._order,s=!0){const o=t.elements,c=o[0],f=o[4],d=o[8],p=o[1],m=o[5],v=o[9],_=o[2],x=o[6],E=o[10];switch(n){case"XYZ":this._y=Math.asin(ge(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(-v,E),this._z=Math.atan2(-f,c)):(this._x=Math.atan2(x,m),this._z=0);break;case"YXZ":this._x=Math.asin(-ge(v,-1,1)),Math.abs(v)<.9999999?(this._y=Math.atan2(d,E),this._z=Math.atan2(p,m)):(this._y=Math.atan2(-_,c),this._z=0);break;case"ZXY":this._x=Math.asin(ge(x,-1,1)),Math.abs(x)<.9999999?(this._y=Math.atan2(-_,E),this._z=Math.atan2(-f,m)):(this._y=0,this._z=Math.atan2(p,c));break;case"ZYX":this._y=Math.asin(-ge(_,-1,1)),Math.abs(_)<.9999999?(this._x=Math.atan2(x,E),this._z=Math.atan2(p,c)):(this._x=0,this._z=Math.atan2(-f,m));break;case"YZX":this._z=Math.asin(ge(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-v,m),this._y=Math.atan2(-_,c)):(this._x=0,this._y=Math.atan2(d,E));break;case"XZY":this._z=Math.asin(-ge(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(x,m),this._y=Math.atan2(d,c)):(this._x=Math.atan2(-v,E),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+n)}return this._order=n,s===!0&&this._onChangeCallback(),this}setFromQuaternion(t,n,s){return cy.makeRotationFromQuaternion(t),this.setFromRotationMatrix(cy,n,s)}setFromVector3(t,n=this._order){return this.set(t.x,t.y,t.z,n)}reorder(t){return uy.setFromEuler(this),this.setFromQuaternion(uy,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ba.DEFAULT_ORDER="XYZ";class iS{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let XT=0;const fy=new W,co=new gc,Ea=new an,Gu=new W,Xl=new W,qT=new W,WT=new gc,dy=new W(1,0,0),hy=new W(0,1,0),py=new W(0,0,1),my={type:"added"},YT={type:"removed"},uo={type:"childadded",child:null},Yh={type:"childremoved",child:null};class si extends Wo{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:XT++}),this.uuid=Yo(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=si.DEFAULT_UP.clone();const t=new W,n=new Ba,s=new gc,o=new W(1,1,1);function c(){s.setFromEuler(n,!1)}function f(){n.setFromQuaternion(s,void 0,!1)}n._onChange(c),s._onChange(f),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:n},quaternion:{configurable:!0,enumerable:!0,value:s},scale:{configurable:!0,enumerable:!0,value:o},modelViewMatrix:{value:new an},normalMatrix:{value:new de}}),this.matrix=new an,this.matrixWorld=new an,this.matrixAutoUpdate=si.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new iS,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,n){this.quaternion.setFromAxisAngle(t,n)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,n){return co.setFromAxisAngle(t,n),this.quaternion.multiply(co),this}rotateOnWorldAxis(t,n){return co.setFromAxisAngle(t,n),this.quaternion.premultiply(co),this}rotateX(t){return this.rotateOnAxis(dy,t)}rotateY(t){return this.rotateOnAxis(hy,t)}rotateZ(t){return this.rotateOnAxis(py,t)}translateOnAxis(t,n){return fy.copy(t).applyQuaternion(this.quaternion),this.position.add(fy.multiplyScalar(n)),this}translateX(t){return this.translateOnAxis(dy,t)}translateY(t){return this.translateOnAxis(hy,t)}translateZ(t){return this.translateOnAxis(py,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(Ea.copy(this.matrixWorld).invert())}lookAt(t,n,s){t.isVector3?Gu.copy(t):Gu.set(t,n,s);const o=this.parent;this.updateWorldMatrix(!0,!1),Xl.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ea.lookAt(Xl,Gu,this.up):Ea.lookAt(Gu,Xl,this.up),this.quaternion.setFromRotationMatrix(Ea),o&&(Ea.extractRotation(o.matrixWorld),co.setFromRotationMatrix(Ea),this.quaternion.premultiply(co.invert()))}add(t){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.add(arguments[n]);return this}return t===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(my),uo.child=t,this.dispatchEvent(uo),uo.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let s=0;s<arguments.length;s++)this.remove(arguments[s]);return this}const n=this.children.indexOf(t);return n!==-1&&(t.parent=null,this.children.splice(n,1),t.dispatchEvent(YT),Yh.child=t,this.dispatchEvent(Yh),Yh.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),Ea.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),Ea.multiply(t.parent.matrixWorld)),t.applyMatrix4(Ea),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(my),uo.child=t,this.dispatchEvent(uo),uo.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,n){if(this[t]===n)return this;for(let s=0,o=this.children.length;s<o;s++){const f=this.children[s].getObjectByProperty(t,n);if(f!==void 0)return f}}getObjectsByProperty(t,n,s=[]){this[t]===n&&s.push(this);const o=this.children;for(let c=0,f=o.length;c<f;c++)o[c].getObjectsByProperty(t,n,s);return s}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Xl,t,qT),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Xl,WT,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const n=this.matrixWorld.elements;return t.set(n[8],n[9],n[10]).normalize()}raycast(){}traverse(t){t(this);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].traverseVisible(t)}traverseAncestors(t){const n=this.parent;n!==null&&(t(n),n.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const n=this.children;for(let s=0,o=n.length;s<o;s++)n[s].updateMatrixWorld(t)}updateWorldMatrix(t,n){const s=this.parent;if(t===!0&&s!==null&&s.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),n===!0){const o=this.children;for(let c=0,f=o.length;c<f;c++)o[c].updateWorldMatrix(!1,!0)}}toJSON(t){const n=t===void 0||typeof t=="string",s={};n&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},s.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const o={};o.uuid=this.uuid,o.type=this.type,this.name!==""&&(o.name=this.name),this.castShadow===!0&&(o.castShadow=!0),this.receiveShadow===!0&&(o.receiveShadow=!0),this.visible===!1&&(o.visible=!1),this.frustumCulled===!1&&(o.frustumCulled=!1),this.renderOrder!==0&&(o.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(o.userData=this.userData),o.layers=this.layers.mask,o.matrix=this.matrix.toArray(),o.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(o.matrixAutoUpdate=!1),this.isInstancedMesh&&(o.type="InstancedMesh",o.count=this.count,o.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(o.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(o.type="BatchedMesh",o.perObjectFrustumCulled=this.perObjectFrustumCulled,o.sortObjects=this.sortObjects,o.drawRanges=this._drawRanges,o.reservedRanges=this._reservedRanges,o.visibility=this._visibility,o.active=this._active,o.bounds=this._bounds.map(d=>({boxInitialized:d.boxInitialized,boxMin:d.box.min.toArray(),boxMax:d.box.max.toArray(),sphereInitialized:d.sphereInitialized,sphereRadius:d.sphere.radius,sphereCenter:d.sphere.center.toArray()})),o.maxInstanceCount=this._maxInstanceCount,o.maxVertexCount=this._maxVertexCount,o.maxIndexCount=this._maxIndexCount,o.geometryInitialized=this._geometryInitialized,o.geometryCount=this._geometryCount,o.matricesTexture=this._matricesTexture.toJSON(t),this._colorsTexture!==null&&(o.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(o.boundingSphere={center:o.boundingSphere.center.toArray(),radius:o.boundingSphere.radius}),this.boundingBox!==null&&(o.boundingBox={min:o.boundingBox.min.toArray(),max:o.boundingBox.max.toArray()}));function c(d,p){return d[p.uuid]===void 0&&(d[p.uuid]=p.toJSON(t)),p.uuid}if(this.isScene)this.background&&(this.background.isColor?o.background=this.background.toJSON():this.background.isTexture&&(o.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(o.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){o.geometry=c(t.geometries,this.geometry);const d=this.geometry.parameters;if(d!==void 0&&d.shapes!==void 0){const p=d.shapes;if(Array.isArray(p))for(let m=0,v=p.length;m<v;m++){const _=p[m];c(t.shapes,_)}else c(t.shapes,p)}}if(this.isSkinnedMesh&&(o.bindMode=this.bindMode,o.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(c(t.skeletons,this.skeleton),o.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const d=[];for(let p=0,m=this.material.length;p<m;p++)d.push(c(t.materials,this.material[p]));o.material=d}else o.material=c(t.materials,this.material);if(this.children.length>0){o.children=[];for(let d=0;d<this.children.length;d++)o.children.push(this.children[d].toJSON(t).object)}if(this.animations.length>0){o.animations=[];for(let d=0;d<this.animations.length;d++){const p=this.animations[d];o.animations.push(c(t.animations,p))}}if(n){const d=f(t.geometries),p=f(t.materials),m=f(t.textures),v=f(t.images),_=f(t.shapes),x=f(t.skeletons),E=f(t.animations),M=f(t.nodes);d.length>0&&(s.geometries=d),p.length>0&&(s.materials=p),m.length>0&&(s.textures=m),v.length>0&&(s.images=v),_.length>0&&(s.shapes=_),x.length>0&&(s.skeletons=x),E.length>0&&(s.animations=E),M.length>0&&(s.nodes=M)}return s.object=o,s;function f(d){const p=[];for(const m in d){const v=d[m];delete v.metadata,p.push(v)}return p}}clone(t){return new this.constructor().copy(this,t)}copy(t,n=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),n===!0)for(let s=0;s<t.children.length;s++){const o=t.children[s];this.add(o.clone())}return this}}si.DEFAULT_UP=new W(0,1,0);si.DEFAULT_MATRIX_AUTO_UPDATE=!0;si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const zi=new W,ba=new W,Qh=new W,Ta=new W,fo=new W,ho=new W,gy=new W,Zh=new W,Kh=new W,Jh=new W,$h=new We,tp=new We,ep=new We;class Bi{constructor(t=new W,n=new W,s=new W){this.a=t,this.b=n,this.c=s}static getNormal(t,n,s,o){o.subVectors(s,n),zi.subVectors(t,n),o.cross(zi);const c=o.lengthSq();return c>0?o.multiplyScalar(1/Math.sqrt(c)):o.set(0,0,0)}static getBarycoord(t,n,s,o,c){zi.subVectors(o,n),ba.subVectors(s,n),Qh.subVectors(t,n);const f=zi.dot(zi),d=zi.dot(ba),p=zi.dot(Qh),m=ba.dot(ba),v=ba.dot(Qh),_=f*m-d*d;if(_===0)return c.set(0,0,0),null;const x=1/_,E=(m*p-d*v)*x,M=(f*v-d*p)*x;return c.set(1-E-M,M,E)}static containsPoint(t,n,s,o){return this.getBarycoord(t,n,s,o,Ta)===null?!1:Ta.x>=0&&Ta.y>=0&&Ta.x+Ta.y<=1}static getInterpolation(t,n,s,o,c,f,d,p){return this.getBarycoord(t,n,s,o,Ta)===null?(p.x=0,p.y=0,"z"in p&&(p.z=0),"w"in p&&(p.w=0),null):(p.setScalar(0),p.addScaledVector(c,Ta.x),p.addScaledVector(f,Ta.y),p.addScaledVector(d,Ta.z),p)}static getInterpolatedAttribute(t,n,s,o,c,f){return $h.setScalar(0),tp.setScalar(0),ep.setScalar(0),$h.fromBufferAttribute(t,n),tp.fromBufferAttribute(t,s),ep.fromBufferAttribute(t,o),f.setScalar(0),f.addScaledVector($h,c.x),f.addScaledVector(tp,c.y),f.addScaledVector(ep,c.z),f}static isFrontFacing(t,n,s,o){return zi.subVectors(s,n),ba.subVectors(t,n),zi.cross(ba).dot(o)<0}set(t,n,s){return this.a.copy(t),this.b.copy(n),this.c.copy(s),this}setFromPointsAndIndices(t,n,s,o){return this.a.copy(t[n]),this.b.copy(t[s]),this.c.copy(t[o]),this}setFromAttributeAndIndices(t,n,s,o){return this.a.fromBufferAttribute(t,n),this.b.fromBufferAttribute(t,s),this.c.fromBufferAttribute(t,o),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return zi.subVectors(this.c,this.b),ba.subVectors(this.a,this.b),zi.cross(ba).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return Bi.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,n){return Bi.getBarycoord(t,this.a,this.b,this.c,n)}getInterpolation(t,n,s,o,c){return Bi.getInterpolation(t,this.a,this.b,this.c,n,s,o,c)}containsPoint(t){return Bi.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return Bi.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,n){const s=this.a,o=this.b,c=this.c;let f,d;fo.subVectors(o,s),ho.subVectors(c,s),Zh.subVectors(t,s);const p=fo.dot(Zh),m=ho.dot(Zh);if(p<=0&&m<=0)return n.copy(s);Kh.subVectors(t,o);const v=fo.dot(Kh),_=ho.dot(Kh);if(v>=0&&_<=v)return n.copy(o);const x=p*_-v*m;if(x<=0&&p>=0&&v<=0)return f=p/(p-v),n.copy(s).addScaledVector(fo,f);Jh.subVectors(t,c);const E=fo.dot(Jh),M=ho.dot(Jh);if(M>=0&&E<=M)return n.copy(c);const T=E*m-p*M;if(T<=0&&m>=0&&M<=0)return d=m/(m-M),n.copy(s).addScaledVector(ho,d);const S=v*M-E*_;if(S<=0&&_-v>=0&&E-M>=0)return gy.subVectors(c,o),d=(_-v)/(_-v+(E-M)),n.copy(o).addScaledVector(gy,d);const y=1/(S+T+x);return f=T*y,d=x*y,n.copy(s).addScaledVector(fo,f).addScaledVector(ho,d)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}const aS={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ps={h:0,s:0,l:0},Vu={h:0,s:0,l:0};function np(a,t,n){return n<0&&(n+=1),n>1&&(n-=1),n<1/6?a+(t-a)*6*n:n<1/2?t:n<2/3?a+(t-a)*6*(2/3-n):a}class pe{constructor(t,n,s){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,n,s)}set(t,n,s){if(n===void 0&&s===void 0){const o=t;o&&o.isColor?this.copy(o):typeof o=="number"?this.setHex(o):typeof o=="string"&&this.setStyle(o)}else this.setRGB(t,n,s);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,n=vi){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Pe.toWorkingColorSpace(this,n),this}setRGB(t,n,s,o=Pe.workingColorSpace){return this.r=t,this.g=n,this.b=s,Pe.toWorkingColorSpace(this,o),this}setHSL(t,n,s,o=Pe.workingColorSpace){if(t=Bm(t,1),n=ge(n,0,1),s=ge(s,0,1),n===0)this.r=this.g=this.b=s;else{const c=s<=.5?s*(1+n):s+n-s*n,f=2*s-c;this.r=np(f,c,t+1/3),this.g=np(f,c,t),this.b=np(f,c,t-1/3)}return Pe.toWorkingColorSpace(this,o),this}setStyle(t,n=vi){function s(c){c!==void 0&&parseFloat(c)<1&&console.warn("THREE.Color: Alpha component of "+t+" will be ignored.")}let o;if(o=/^(\w+)\(([^\)]*)\)/.exec(t)){let c;const f=o[1],d=o[2];switch(f){case"rgb":case"rgba":if(c=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(255,parseInt(c[1],10))/255,Math.min(255,parseInt(c[2],10))/255,Math.min(255,parseInt(c[3],10))/255,n);if(c=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(100,parseInt(c[1],10))/100,Math.min(100,parseInt(c[2],10))/100,Math.min(100,parseInt(c[3],10))/100,n);break;case"hsl":case"hsla":if(c=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setHSL(parseFloat(c[1])/360,parseFloat(c[2])/100,parseFloat(c[3])/100,n);break;default:console.warn("THREE.Color: Unknown color model "+t)}}else if(o=/^\#([A-Fa-f\d]+)$/.exec(t)){const c=o[1],f=c.length;if(f===3)return this.setRGB(parseInt(c.charAt(0),16)/15,parseInt(c.charAt(1),16)/15,parseInt(c.charAt(2),16)/15,n);if(f===6)return this.setHex(parseInt(c,16),n);console.warn("THREE.Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,n);return this}setColorName(t,n=vi){const s=aS[t.toLowerCase()];return s!==void 0?this.setHex(s,n):console.warn("THREE.Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=za(t.r),this.g=za(t.g),this.b=za(t.b),this}copyLinearToSRGB(t){return this.r=To(t.r),this.g=To(t.g),this.b=To(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=vi){return Pe.fromWorkingColorSpace(Fn.copy(this),t),Math.round(ge(Fn.r*255,0,255))*65536+Math.round(ge(Fn.g*255,0,255))*256+Math.round(ge(Fn.b*255,0,255))}getHexString(t=vi){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,n=Pe.workingColorSpace){Pe.fromWorkingColorSpace(Fn.copy(this),n);const s=Fn.r,o=Fn.g,c=Fn.b,f=Math.max(s,o,c),d=Math.min(s,o,c);let p,m;const v=(d+f)/2;if(d===f)p=0,m=0;else{const _=f-d;switch(m=v<=.5?_/(f+d):_/(2-f-d),f){case s:p=(o-c)/_+(o<c?6:0);break;case o:p=(c-s)/_+2;break;case c:p=(s-o)/_+4;break}p/=6}return t.h=p,t.s=m,t.l=v,t}getRGB(t,n=Pe.workingColorSpace){return Pe.fromWorkingColorSpace(Fn.copy(this),n),t.r=Fn.r,t.g=Fn.g,t.b=Fn.b,t}getStyle(t=vi){Pe.fromWorkingColorSpace(Fn.copy(this),t);const n=Fn.r,s=Fn.g,o=Fn.b;return t!==vi?`color(${t} ${n.toFixed(3)} ${s.toFixed(3)} ${o.toFixed(3)})`:`rgb(${Math.round(n*255)},${Math.round(s*255)},${Math.round(o*255)})`}offsetHSL(t,n,s){return this.getHSL(ps),this.setHSL(ps.h+t,ps.s+n,ps.l+s)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,n){return this.r=t.r+n.r,this.g=t.g+n.g,this.b=t.b+n.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,n){return this.r+=(t.r-this.r)*n,this.g+=(t.g-this.g)*n,this.b+=(t.b-this.b)*n,this}lerpColors(t,n,s){return this.r=t.r+(n.r-t.r)*s,this.g=t.g+(n.g-t.g)*s,this.b=t.b+(n.b-t.b)*s,this}lerpHSL(t,n){this.getHSL(ps),t.getHSL(Vu);const s=tc(ps.h,Vu.h,n),o=tc(ps.s,Vu.s,n),c=tc(ps.l,Vu.l,n);return this.setHSL(s,o,c),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const n=this.r,s=this.g,o=this.b,c=t.elements;return this.r=c[0]*n+c[3]*s+c[6]*o,this.g=c[1]*n+c[4]*s+c[7]*o,this.b=c[2]*n+c[5]*s+c[8]*o,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,n=0){return this.r=t[n],this.g=t[n+1],this.b=t[n+2],this}toArray(t=[],n=0){return t[n]=this.r,t[n+1]=this.g,t[n+2]=this.b,t}fromBufferAttribute(t,n){return this.r=t.getX(n),this.g=t.getY(n),this.b=t.getZ(n),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Fn=new pe;pe.NAMES=aS;let QT=0;class Sf extends Wo{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:QT++}),this.uuid=Yo(),this.name="",this.type="Material",this.blending=Eo,this.side=Rs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Op,this.blendDst=Pp,this.blendEquation=sr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new pe(0,0,0),this.blendAlpha=0,this.depthFunc=Fo,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=ey,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=io,this.stencilZFail=io,this.stencilZPass=io,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const n in t){const s=t[n];if(s===void 0){console.warn(`THREE.Material: parameter '${n}' has value of undefined.`);continue}const o=this[n];if(o===void 0){console.warn(`THREE.Material: '${n}' is not a property of THREE.${this.type}.`);continue}o&&o.isColor?o.set(s):o&&o.isVector3&&s&&s.isVector3?o.copy(s):this[n]=s}}toJSON(t){const n=t===void 0||typeof t=="string";n&&(t={textures:{},images:{}});const s={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.color&&this.color.isColor&&(s.color=this.color.getHex()),this.roughness!==void 0&&(s.roughness=this.roughness),this.metalness!==void 0&&(s.metalness=this.metalness),this.sheen!==void 0&&(s.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(s.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(s.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(s.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(s.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(s.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(s.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(s.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(s.shininess=this.shininess),this.clearcoat!==void 0&&(s.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(s.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(s.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(s.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(s.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,s.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(s.dispersion=this.dispersion),this.iridescence!==void 0&&(s.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(s.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(s.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(s.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(s.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(s.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(s.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(s.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(s.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(s.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(s.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(s.lightMap=this.lightMap.toJSON(t).uuid,s.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(s.aoMap=this.aoMap.toJSON(t).uuid,s.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(s.bumpMap=this.bumpMap.toJSON(t).uuid,s.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(s.normalMap=this.normalMap.toJSON(t).uuid,s.normalMapType=this.normalMapType,s.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(s.displacementMap=this.displacementMap.toJSON(t).uuid,s.displacementScale=this.displacementScale,s.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(s.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(s.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(s.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(s.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(s.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(s.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(s.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(s.combine=this.combine)),this.envMapRotation!==void 0&&(s.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(s.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(s.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(s.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(s.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(s.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(s.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(s.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(s.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(s.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(s.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(s.size=this.size),this.shadowSide!==null&&(s.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(s.sizeAttenuation=this.sizeAttenuation),this.blending!==Eo&&(s.blending=this.blending),this.side!==Rs&&(s.side=this.side),this.vertexColors===!0&&(s.vertexColors=!0),this.opacity<1&&(s.opacity=this.opacity),this.transparent===!0&&(s.transparent=!0),this.blendSrc!==Op&&(s.blendSrc=this.blendSrc),this.blendDst!==Pp&&(s.blendDst=this.blendDst),this.blendEquation!==sr&&(s.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(s.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(s.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(s.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(s.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(s.blendAlpha=this.blendAlpha),this.depthFunc!==Fo&&(s.depthFunc=this.depthFunc),this.depthTest===!1&&(s.depthTest=this.depthTest),this.depthWrite===!1&&(s.depthWrite=this.depthWrite),this.colorWrite===!1&&(s.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(s.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==ey&&(s.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(s.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(s.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==io&&(s.stencilFail=this.stencilFail),this.stencilZFail!==io&&(s.stencilZFail=this.stencilZFail),this.stencilZPass!==io&&(s.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(s.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(s.rotation=this.rotation),this.polygonOffset===!0&&(s.polygonOffset=!0),this.polygonOffsetFactor!==0&&(s.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(s.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(s.linewidth=this.linewidth),this.dashSize!==void 0&&(s.dashSize=this.dashSize),this.gapSize!==void 0&&(s.gapSize=this.gapSize),this.scale!==void 0&&(s.scale=this.scale),this.dithering===!0&&(s.dithering=!0),this.alphaTest>0&&(s.alphaTest=this.alphaTest),this.alphaHash===!0&&(s.alphaHash=!0),this.alphaToCoverage===!0&&(s.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(s.premultipliedAlpha=!0),this.forceSinglePass===!0&&(s.forceSinglePass=!0),this.wireframe===!0&&(s.wireframe=!0),this.wireframeLinewidth>1&&(s.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(s.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(s.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(s.flatShading=!0),this.visible===!1&&(s.visible=!1),this.toneMapped===!1&&(s.toneMapped=!1),this.fog===!1&&(s.fog=!1),Object.keys(this.userData).length>0&&(s.userData=this.userData);function o(c){const f=[];for(const d in c){const p=c[d];delete p.metadata,f.push(p)}return f}if(n){const c=o(t.textures),f=o(t.images);c.length>0&&(s.textures=c),f.length>0&&(s.images=f)}return s}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const n=t.clippingPlanes;let s=null;if(n!==null){const o=n.length;s=new Array(o);for(let c=0;c!==o;++c)s[c]=n[c].clone()}return this.clippingPlanes=s,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Sr extends Sf{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new pe(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ba,this.combine=Gx,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const vn=new W,ju=new Wt;class ea{constructor(t,n,s=!1){if(Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=t,this.itemSize=n,this.count=t!==void 0?t.length/n:0,this.normalized=s,this.usage=ny,this.updateRanges=[],this.gpuType=Da,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,n){this.updateRanges.push({start:t,count:n})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,n,s){t*=this.itemSize,s*=n.itemSize;for(let o=0,c=this.itemSize;o<c;o++)this.array[t+o]=n.array[s+o];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let n=0,s=this.count;n<s;n++)ju.fromBufferAttribute(this,n),ju.applyMatrix3(t),this.setXY(n,ju.x,ju.y);else if(this.itemSize===3)for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix3(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyMatrix4(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix4(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyNormalMatrix(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyNormalMatrix(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}transformDirection(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.transformDirection(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}set(t,n=0){return this.array.set(t,n),this}getComponent(t,n){let s=this.array[t*this.itemSize+n];return this.normalized&&(s=yo(s,this.array)),s}setComponent(t,n,s){return this.normalized&&(s=kn(s,this.array)),this.array[t*this.itemSize+n]=s,this}getX(t){let n=this.array[t*this.itemSize];return this.normalized&&(n=yo(n,this.array)),n}setX(t,n){return this.normalized&&(n=kn(n,this.array)),this.array[t*this.itemSize]=n,this}getY(t){let n=this.array[t*this.itemSize+1];return this.normalized&&(n=yo(n,this.array)),n}setY(t,n){return this.normalized&&(n=kn(n,this.array)),this.array[t*this.itemSize+1]=n,this}getZ(t){let n=this.array[t*this.itemSize+2];return this.normalized&&(n=yo(n,this.array)),n}setZ(t,n){return this.normalized&&(n=kn(n,this.array)),this.array[t*this.itemSize+2]=n,this}getW(t){let n=this.array[t*this.itemSize+3];return this.normalized&&(n=yo(n,this.array)),n}setW(t,n){return this.normalized&&(n=kn(n,this.array)),this.array[t*this.itemSize+3]=n,this}setXY(t,n,s){return t*=this.itemSize,this.normalized&&(n=kn(n,this.array),s=kn(s,this.array)),this.array[t+0]=n,this.array[t+1]=s,this}setXYZ(t,n,s,o){return t*=this.itemSize,this.normalized&&(n=kn(n,this.array),s=kn(s,this.array),o=kn(o,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=o,this}setXYZW(t,n,s,o,c){return t*=this.itemSize,this.normalized&&(n=kn(n,this.array),s=kn(s,this.array),o=kn(o,this.array),c=kn(c,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=o,this.array[t+3]=c,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==ny&&(t.usage=this.usage),t}}class sS extends ea{constructor(t,n,s){super(new Uint16Array(t),n,s)}}class rS extends ea{constructor(t,n,s){super(new Uint32Array(t),n,s)}}class Cn extends ea{constructor(t,n,s){super(new Float32Array(t),n,s)}}let ZT=0;const Ci=new an,ip=new si,po=new W,pi=new vc,ql=new vc,Tn=new W;class Vi extends Wo{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:ZT++}),this.uuid=Yo(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(tS(t)?rS:sS)(t,1):this.index=t,this}setIndirect(t){return this.indirect=t,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,n){return this.attributes[t]=n,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,n,s=0){this.groups.push({start:t,count:n,materialIndex:s})}clearGroups(){this.groups=[]}setDrawRange(t,n){this.drawRange.start=t,this.drawRange.count=n}applyMatrix4(t){const n=this.attributes.position;n!==void 0&&(n.applyMatrix4(t),n.needsUpdate=!0);const s=this.attributes.normal;if(s!==void 0){const c=new de().getNormalMatrix(t);s.applyNormalMatrix(c),s.needsUpdate=!0}const o=this.attributes.tangent;return o!==void 0&&(o.transformDirection(t),o.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return Ci.makeRotationFromQuaternion(t),this.applyMatrix4(Ci),this}rotateX(t){return Ci.makeRotationX(t),this.applyMatrix4(Ci),this}rotateY(t){return Ci.makeRotationY(t),this.applyMatrix4(Ci),this}rotateZ(t){return Ci.makeRotationZ(t),this.applyMatrix4(Ci),this}translate(t,n,s){return Ci.makeTranslation(t,n,s),this.applyMatrix4(Ci),this}scale(t,n,s){return Ci.makeScale(t,n,s),this.applyMatrix4(Ci),this}lookAt(t){return ip.lookAt(t),ip.updateMatrix(),this.applyMatrix4(ip.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(po).negate(),this.translate(po.x,po.y,po.z),this}setFromPoints(t){const n=this.getAttribute("position");if(n===void 0){const s=[];for(let o=0,c=t.length;o<c;o++){const f=t[o];s.push(f.x,f.y,f.z||0)}this.setAttribute("position",new Cn(s,3))}else{const s=Math.min(t.length,n.count);for(let o=0;o<s;o++){const c=t[o];n.setXYZ(o,c.x,c.y,c.z||0)}t.length>n.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),n.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new vc);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new W(-1/0,-1/0,-1/0),new W(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),n)for(let s=0,o=n.length;s<o;s++){const c=n[s];pi.setFromBufferAttribute(c),this.morphTargetsRelative?(Tn.addVectors(this.boundingBox.min,pi.min),this.boundingBox.expandByPoint(Tn),Tn.addVectors(this.boundingBox.max,pi.max),this.boundingBox.expandByPoint(Tn)):(this.boundingBox.expandByPoint(pi.min),this.boundingBox.expandByPoint(pi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Fm);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new W,1/0);return}if(t){const s=this.boundingSphere.center;if(pi.setFromBufferAttribute(t),n)for(let c=0,f=n.length;c<f;c++){const d=n[c];ql.setFromBufferAttribute(d),this.morphTargetsRelative?(Tn.addVectors(pi.min,ql.min),pi.expandByPoint(Tn),Tn.addVectors(pi.max,ql.max),pi.expandByPoint(Tn)):(pi.expandByPoint(ql.min),pi.expandByPoint(ql.max))}pi.getCenter(s);let o=0;for(let c=0,f=t.count;c<f;c++)Tn.fromBufferAttribute(t,c),o=Math.max(o,s.distanceToSquared(Tn));if(n)for(let c=0,f=n.length;c<f;c++){const d=n[c],p=this.morphTargetsRelative;for(let m=0,v=d.count;m<v;m++)Tn.fromBufferAttribute(d,m),p&&(po.fromBufferAttribute(t,m),Tn.add(po)),o=Math.max(o,s.distanceToSquared(Tn))}this.boundingSphere.radius=Math.sqrt(o),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,n=this.attributes;if(t===null||n.position===void 0||n.normal===void 0||n.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const s=n.position,o=n.normal,c=n.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ea(new Float32Array(4*s.count),4));const f=this.getAttribute("tangent"),d=[],p=[];for(let G=0;G<s.count;G++)d[G]=new W,p[G]=new W;const m=new W,v=new W,_=new W,x=new Wt,E=new Wt,M=new Wt,T=new W,S=new W;function y(G,U,N){m.fromBufferAttribute(s,G),v.fromBufferAttribute(s,U),_.fromBufferAttribute(s,N),x.fromBufferAttribute(c,G),E.fromBufferAttribute(c,U),M.fromBufferAttribute(c,N),v.sub(m),_.sub(m),E.sub(x),M.sub(x);const H=1/(E.x*M.y-M.x*E.y);isFinite(H)&&(T.copy(v).multiplyScalar(M.y).addScaledVector(_,-E.y).multiplyScalar(H),S.copy(_).multiplyScalar(E.x).addScaledVector(v,-M.x).multiplyScalar(H),d[G].add(T),d[U].add(T),d[N].add(T),p[G].add(S),p[U].add(S),p[N].add(S))}let I=this.groups;I.length===0&&(I=[{start:0,count:t.count}]);for(let G=0,U=I.length;G<U;++G){const N=I[G],H=N.start,ut=N.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)y(t.getX(ot+0),t.getX(ot+1),t.getX(ot+2))}const D=new W,C=new W,V=new W,L=new W;function P(G){V.fromBufferAttribute(o,G),L.copy(V);const U=d[G];D.copy(U),D.sub(V.multiplyScalar(V.dot(U))).normalize(),C.crossVectors(L,U);const H=C.dot(p[G])<0?-1:1;f.setXYZW(G,D.x,D.y,D.z,H)}for(let G=0,U=I.length;G<U;++G){const N=I[G],H=N.start,ut=N.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)P(t.getX(ot+0)),P(t.getX(ot+1)),P(t.getX(ot+2))}}computeVertexNormals(){const t=this.index,n=this.getAttribute("position");if(n!==void 0){let s=this.getAttribute("normal");if(s===void 0)s=new ea(new Float32Array(n.count*3),3),this.setAttribute("normal",s);else for(let x=0,E=s.count;x<E;x++)s.setXYZ(x,0,0,0);const o=new W,c=new W,f=new W,d=new W,p=new W,m=new W,v=new W,_=new W;if(t)for(let x=0,E=t.count;x<E;x+=3){const M=t.getX(x+0),T=t.getX(x+1),S=t.getX(x+2);o.fromBufferAttribute(n,M),c.fromBufferAttribute(n,T),f.fromBufferAttribute(n,S),v.subVectors(f,c),_.subVectors(o,c),v.cross(_),d.fromBufferAttribute(s,M),p.fromBufferAttribute(s,T),m.fromBufferAttribute(s,S),d.add(v),p.add(v),m.add(v),s.setXYZ(M,d.x,d.y,d.z),s.setXYZ(T,p.x,p.y,p.z),s.setXYZ(S,m.x,m.y,m.z)}else for(let x=0,E=n.count;x<E;x+=3)o.fromBufferAttribute(n,x+0),c.fromBufferAttribute(n,x+1),f.fromBufferAttribute(n,x+2),v.subVectors(f,c),_.subVectors(o,c),v.cross(_),s.setXYZ(x+0,v.x,v.y,v.z),s.setXYZ(x+1,v.x,v.y,v.z),s.setXYZ(x+2,v.x,v.y,v.z);this.normalizeNormals(),s.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let n=0,s=t.count;n<s;n++)Tn.fromBufferAttribute(t,n),Tn.normalize(),t.setXYZ(n,Tn.x,Tn.y,Tn.z)}toNonIndexed(){function t(d,p){const m=d.array,v=d.itemSize,_=d.normalized,x=new m.constructor(p.length*v);let E=0,M=0;for(let T=0,S=p.length;T<S;T++){d.isInterleavedBufferAttribute?E=p[T]*d.data.stride+d.offset:E=p[T]*v;for(let y=0;y<v;y++)x[M++]=m[E++]}return new ea(x,v,_)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const n=new Vi,s=this.index.array,o=this.attributes;for(const d in o){const p=o[d],m=t(p,s);n.setAttribute(d,m)}const c=this.morphAttributes;for(const d in c){const p=[],m=c[d];for(let v=0,_=m.length;v<_;v++){const x=m[v],E=t(x,s);p.push(E)}n.morphAttributes[d]=p}n.morphTargetsRelative=this.morphTargetsRelative;const f=this.groups;for(let d=0,p=f.length;d<p;d++){const m=f[d];n.addGroup(m.start,m.count,m.materialIndex)}return n}toJSON(){const t={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const p=this.parameters;for(const m in p)p[m]!==void 0&&(t[m]=p[m]);return t}t.data={attributes:{}};const n=this.index;n!==null&&(t.data.index={type:n.array.constructor.name,array:Array.prototype.slice.call(n.array)});const s=this.attributes;for(const p in s){const m=s[p];t.data.attributes[p]=m.toJSON(t.data)}const o={};let c=!1;for(const p in this.morphAttributes){const m=this.morphAttributes[p],v=[];for(let _=0,x=m.length;_<x;_++){const E=m[_];v.push(E.toJSON(t.data))}v.length>0&&(o[p]=v,c=!0)}c&&(t.data.morphAttributes=o,t.data.morphTargetsRelative=this.morphTargetsRelative);const f=this.groups;f.length>0&&(t.data.groups=JSON.parse(JSON.stringify(f)));const d=this.boundingSphere;return d!==null&&(t.data.boundingSphere={center:d.center.toArray(),radius:d.radius}),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const n={};this.name=t.name;const s=t.index;s!==null&&this.setIndex(s.clone(n));const o=t.attributes;for(const m in o){const v=o[m];this.setAttribute(m,v.clone(n))}const c=t.morphAttributes;for(const m in c){const v=[],_=c[m];for(let x=0,E=_.length;x<E;x++)v.push(_[x].clone(n));this.morphAttributes[m]=v}this.morphTargetsRelative=t.morphTargetsRelative;const f=t.groups;for(let m=0,v=f.length;m<v;m++){const _=f[m];this.addGroup(_.start,_.count,_.materialIndex)}const d=t.boundingBox;d!==null&&(this.boundingBox=d.clone());const p=t.boundingSphere;return p!==null&&(this.boundingSphere=p.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const vy=new an,Ks=new VT,ku=new Fm,_y=new W,Xu=new W,qu=new W,Wu=new W,ap=new W,Yu=new W,yy=new W,Qu=new W;class Wn extends si{constructor(t=new Vi,n=new Sr){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=n,this.updateMorphTargets()}copy(t,n){return super.copy(t,n),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const n=this.geometry.morphAttributes,s=Object.keys(n);if(s.length>0){const o=n[s[0]];if(o!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,f=o.length;c<f;c++){const d=o[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}getVertexPosition(t,n){const s=this.geometry,o=s.attributes.position,c=s.morphAttributes.position,f=s.morphTargetsRelative;n.fromBufferAttribute(o,t);const d=this.morphTargetInfluences;if(c&&d){Yu.set(0,0,0);for(let p=0,m=c.length;p<m;p++){const v=d[p],_=c[p];v!==0&&(ap.fromBufferAttribute(_,t),f?Yu.addScaledVector(ap,v):Yu.addScaledVector(ap.sub(n),v))}n.add(Yu)}return n}raycast(t,n){const s=this.geometry,o=this.material,c=this.matrixWorld;o!==void 0&&(s.boundingSphere===null&&s.computeBoundingSphere(),ku.copy(s.boundingSphere),ku.applyMatrix4(c),Ks.copy(t.ray).recast(t.near),!(ku.containsPoint(Ks.origin)===!1&&(Ks.intersectSphere(ku,_y)===null||Ks.origin.distanceToSquared(_y)>(t.far-t.near)**2))&&(vy.copy(c).invert(),Ks.copy(t.ray).applyMatrix4(vy),!(s.boundingBox!==null&&Ks.intersectsBox(s.boundingBox)===!1)&&this._computeIntersections(t,n,Ks)))}_computeIntersections(t,n,s){let o;const c=this.geometry,f=this.material,d=c.index,p=c.attributes.position,m=c.attributes.uv,v=c.attributes.uv1,_=c.attributes.normal,x=c.groups,E=c.drawRange;if(d!==null)if(Array.isArray(f))for(let M=0,T=x.length;M<T;M++){const S=x[M],y=f[S.materialIndex],I=Math.max(S.start,E.start),D=Math.min(d.count,Math.min(S.start+S.count,E.start+E.count));for(let C=I,V=D;C<V;C+=3){const L=d.getX(C),P=d.getX(C+1),G=d.getX(C+2);o=Zu(this,y,t,s,m,v,_,L,P,G),o&&(o.faceIndex=Math.floor(C/3),o.face.materialIndex=S.materialIndex,n.push(o))}}else{const M=Math.max(0,E.start),T=Math.min(d.count,E.start+E.count);for(let S=M,y=T;S<y;S+=3){const I=d.getX(S),D=d.getX(S+1),C=d.getX(S+2);o=Zu(this,f,t,s,m,v,_,I,D,C),o&&(o.faceIndex=Math.floor(S/3),n.push(o))}}else if(p!==void 0)if(Array.isArray(f))for(let M=0,T=x.length;M<T;M++){const S=x[M],y=f[S.materialIndex],I=Math.max(S.start,E.start),D=Math.min(p.count,Math.min(S.start+S.count,E.start+E.count));for(let C=I,V=D;C<V;C+=3){const L=C,P=C+1,G=C+2;o=Zu(this,y,t,s,m,v,_,L,P,G),o&&(o.faceIndex=Math.floor(C/3),o.face.materialIndex=S.materialIndex,n.push(o))}}else{const M=Math.max(0,E.start),T=Math.min(p.count,E.start+E.count);for(let S=M,y=T;S<y;S+=3){const I=S,D=S+1,C=S+2;o=Zu(this,f,t,s,m,v,_,I,D,C),o&&(o.faceIndex=Math.floor(S/3),n.push(o))}}}}function KT(a,t,n,s,o,c,f,d){let p;if(t.side===ii?p=s.intersectTriangle(f,c,o,!0,d):p=s.intersectTriangle(o,c,f,t.side===Rs,d),p===null)return null;Qu.copy(d),Qu.applyMatrix4(a.matrixWorld);const m=n.ray.origin.distanceTo(Qu);return m<n.near||m>n.far?null:{distance:m,point:Qu.clone(),object:a}}function Zu(a,t,n,s,o,c,f,d,p,m){a.getVertexPosition(d,Xu),a.getVertexPosition(p,qu),a.getVertexPosition(m,Wu);const v=KT(a,t,n,s,Xu,qu,Wu,yy);if(v){const _=new W;Bi.getBarycoord(yy,Xu,qu,Wu,_),o&&(v.uv=Bi.getInterpolatedAttribute(o,d,p,m,_,new Wt)),c&&(v.uv1=Bi.getInterpolatedAttribute(c,d,p,m,_,new Wt)),f&&(v.normal=Bi.getInterpolatedAttribute(f,d,p,m,_,new W),v.normal.dot(s.direction)>0&&v.normal.multiplyScalar(-1));const x={a:d,b:p,c:m,normal:new W,materialIndex:0};Bi.getNormal(Xu,qu,Wu,x.normal),v.face=x,v.barycoord=_}return v}class _c extends Vi{constructor(t=1,n=1,s=1,o=1,c=1,f=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:n,depth:s,widthSegments:o,heightSegments:c,depthSegments:f};const d=this;o=Math.floor(o),c=Math.floor(c),f=Math.floor(f);const p=[],m=[],v=[],_=[];let x=0,E=0;M("z","y","x",-1,-1,s,n,t,f,c,0),M("z","y","x",1,-1,s,n,-t,f,c,1),M("x","z","y",1,1,t,s,n,o,f,2),M("x","z","y",1,-1,t,s,-n,o,f,3),M("x","y","z",1,-1,t,n,s,o,c,4),M("x","y","z",-1,-1,t,n,-s,o,c,5),this.setIndex(p),this.setAttribute("position",new Cn(m,3)),this.setAttribute("normal",new Cn(v,3)),this.setAttribute("uv",new Cn(_,2));function M(T,S,y,I,D,C,V,L,P,G,U){const N=C/P,H=V/G,ut=C/2,ot=V/2,mt=L/2,ct=P+1,B=G+1;let Z=0,$=0;const Et=new W;for(let At=0;At<B;At++){const z=At*H-ot;for(let nt=0;nt<ct;nt++){const St=nt*N-ut;Et[T]=St*I,Et[S]=z*D,Et[y]=mt,m.push(Et.x,Et.y,Et.z),Et[T]=0,Et[S]=0,Et[y]=L>0?1:-1,v.push(Et.x,Et.y,Et.z),_.push(nt/P),_.push(1-At/G),Z+=1}}for(let At=0;At<G;At++)for(let z=0;z<P;z++){const nt=x+z+ct*At,St=x+z+ct*(At+1),q=x+(z+1)+ct*(At+1),ft=x+(z+1)+ct*At;p.push(nt,St,ft),p.push(St,q,ft),$+=6}d.addGroup(E,$,U),E+=$,x+=Z}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new _c(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}function Xo(a){const t={};for(const n in a){t[n]={};for(const s in a[n]){const o=a[n][s];o&&(o.isColor||o.isMatrix3||o.isMatrix4||o.isVector2||o.isVector3||o.isVector4||o.isTexture||o.isQuaternion)?o.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[n][s]=null):t[n][s]=o.clone():Array.isArray(o)?t[n][s]=o.slice():t[n][s]=o}}return t}function Xn(a){const t={};for(let n=0;n<a.length;n++){const s=Xo(a[n]);for(const o in s)t[o]=s[o]}return t}function JT(a){const t=[];for(let n=0;n<a.length;n++)t.push(a[n].clone());return t}function oS(a){const t=a.getRenderTarget();return t===null?a.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Pe.workingColorSpace}const _f={clone:Xo,merge:Xn};var $T=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,tA=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Yn extends Sf{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=$T,this.fragmentShader=tA,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Xo(t.uniforms),this.uniformsGroups=JT(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this}toJSON(t){const n=super.toJSON(t);n.glslVersion=this.glslVersion,n.uniforms={};for(const o in this.uniforms){const f=this.uniforms[o].value;f&&f.isTexture?n.uniforms[o]={type:"t",value:f.toJSON(t).uuid}:f&&f.isColor?n.uniforms[o]={type:"c",value:f.getHex()}:f&&f.isVector2?n.uniforms[o]={type:"v2",value:f.toArray()}:f&&f.isVector3?n.uniforms[o]={type:"v3",value:f.toArray()}:f&&f.isVector4?n.uniforms[o]={type:"v4",value:f.toArray()}:f&&f.isMatrix3?n.uniforms[o]={type:"m3",value:f.toArray()}:f&&f.isMatrix4?n.uniforms[o]={type:"m4",value:f.toArray()}:n.uniforms[o]={value:f}}Object.keys(this.defines).length>0&&(n.defines=this.defines),n.vertexShader=this.vertexShader,n.fragmentShader=this.fragmentShader,n.lights=this.lights,n.clipping=this.clipping;const s={};for(const o in this.extensions)this.extensions[o]===!0&&(s[o]=!0);return Object.keys(s).length>0&&(n.extensions=s),n}}class lS extends si{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new an,this.projectionMatrix=new an,this.projectionMatrixInverse=new an,this.coordinateSystem=Ua}copy(t,n){return super.copy(t,n),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(t,n){super.updateWorldMatrix(t,n),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ms=new W,xy=new Wt,Sy=new Wt;class _i extends lS{constructor(t=50,n=1,s=.1,o=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=s,this.far=o,this.focus=10,this.aspect=n,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const n=.5*this.getFilmHeight()/t;this.fov=cc*2*Math.atan(n),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan($l*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return cc*2*Math.atan(Math.tan($l*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,n,s){ms.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ms.x,ms.y).multiplyScalar(-t/ms.z),ms.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),s.set(ms.x,ms.y).multiplyScalar(-t/ms.z)}getViewSize(t,n){return this.getViewBounds(t,xy,Sy),n.subVectors(Sy,xy)}setViewOffset(t,n,s,o,c,f){this.aspect=t/n,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=o,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let n=t*Math.tan($l*.5*this.fov)/this.zoom,s=2*n,o=this.aspect*s,c=-.5*o;const f=this.view;if(this.view!==null&&this.view.enabled){const p=f.fullWidth,m=f.fullHeight;c+=f.offsetX*o/p,n-=f.offsetY*s/m,o*=f.width/p,s*=f.height/m}const d=this.filmOffset;d!==0&&(c+=t*d/this.getFilmWidth()),this.projectionMatrix.makePerspective(c,c+o,n,n-s,t,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.fov=this.fov,n.object.zoom=this.zoom,n.object.near=this.near,n.object.far=this.far,n.object.focus=this.focus,n.object.aspect=this.aspect,this.view!==null&&(n.object.view=Object.assign({},this.view)),n.object.filmGauge=this.filmGauge,n.object.filmOffset=this.filmOffset,n}}const mo=-90,go=1;class eA extends si{constructor(t,n,s){super(),this.type="CubeCamera",this.renderTarget=s,this.coordinateSystem=null,this.activeMipmapLevel=0;const o=new _i(mo,go,t,n);o.layers=this.layers,this.add(o);const c=new _i(mo,go,t,n);c.layers=this.layers,this.add(c);const f=new _i(mo,go,t,n);f.layers=this.layers,this.add(f);const d=new _i(mo,go,t,n);d.layers=this.layers,this.add(d);const p=new _i(mo,go,t,n);p.layers=this.layers,this.add(p);const m=new _i(mo,go,t,n);m.layers=this.layers,this.add(m)}updateCoordinateSystem(){const t=this.coordinateSystem,n=this.children.concat(),[s,o,c,f,d,p]=n;for(const m of n)this.remove(m);if(t===Ua)s.up.set(0,1,0),s.lookAt(1,0,0),o.up.set(0,1,0),o.lookAt(-1,0,0),c.up.set(0,0,-1),c.lookAt(0,1,0),f.up.set(0,0,1),f.lookAt(0,-1,0),d.up.set(0,1,0),d.lookAt(0,0,1),p.up.set(0,1,0),p.lookAt(0,0,-1);else if(t===gf)s.up.set(0,-1,0),s.lookAt(-1,0,0),o.up.set(0,-1,0),o.lookAt(1,0,0),c.up.set(0,0,1),c.lookAt(0,1,0),f.up.set(0,0,-1),f.lookAt(0,-1,0),d.up.set(0,-1,0),d.lookAt(0,0,1),p.up.set(0,-1,0),p.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const m of n)this.add(m),m.updateMatrixWorld()}update(t,n){this.parent===null&&this.updateMatrixWorld();const{renderTarget:s,activeMipmapLevel:o}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[c,f,d,p,m,v]=this.children,_=t.getRenderTarget(),x=t.getActiveCubeFace(),E=t.getActiveMipmapLevel(),M=t.xr.enabled;t.xr.enabled=!1;const T=s.texture.generateMipmaps;s.texture.generateMipmaps=!1,t.setRenderTarget(s,0,o),t.render(n,c),t.setRenderTarget(s,1,o),t.render(n,f),t.setRenderTarget(s,2,o),t.render(n,d),t.setRenderTarget(s,3,o),t.render(n,p),t.setRenderTarget(s,4,o),t.render(n,m),s.texture.generateMipmaps=T,t.setRenderTarget(s,5,o),t.render(n,v),t.setRenderTarget(_,x,E),t.xr.enabled=M,s.texture.needsPMREMUpdate=!0}}class cS extends ai{constructor(t,n,s,o,c,f,d,p,m,v){t=t!==void 0?t:[],n=n!==void 0?n:Ho,super(t,n,s,o,c,f,d,p,m,v),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class nA extends Gi{constructor(t=1,n={}){super(t,t,n),this.isWebGLCubeRenderTarget=!0;const s={width:t,height:t,depth:1},o=[s,s,s,s,s,s];this.texture=new cS(o,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=n.generateMipmaps!==void 0?n.generateMipmaps:!1,this.texture.minFilter=n.minFilter!==void 0?n.minFilter:$i}fromEquirectangularTexture(t,n){this.texture.type=n.type,this.texture.colorSpace=n.colorSpace,this.texture.generateMipmaps=n.generateMipmaps,this.texture.minFilter=n.minFilter,this.texture.magFilter=n.magFilter;const s={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},o=new _c(5,5,5),c=new Yn({name:"CubemapFromEquirect",uniforms:Xo(s.uniforms),vertexShader:s.vertexShader,fragmentShader:s.fragmentShader,side:ii,blending:Oa});c.uniforms.tEquirect.value=n;const f=new Wn(o,c),d=n.minFilter;return n.minFilter===ur&&(n.minFilter=$i),new eA(1,10,this).update(t,f),n.minFilter=d,f.geometry.dispose(),f.material.dispose(),this}clear(t,n,s,o){const c=t.getRenderTarget();for(let f=0;f<6;f++)t.setRenderTarget(this,f),t.clear(n,s,o);t.setRenderTarget(c)}}class iA extends si{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ba,this.environmentIntensity=1,this.environmentRotation=new Ba,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,n){return super.copy(t,n),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const n=super.toJSON(t);return this.fog!==null&&(n.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(n.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(n.object.backgroundIntensity=this.backgroundIntensity),n.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(n.object.environmentIntensity=this.environmentIntensity),n.object.environmentRotation=this.environmentRotation.toArray(),n}}const sp=new W,aA=new W,sA=new de;class nr{constructor(t=new W(1,0,0),n=0){this.isPlane=!0,this.normal=t,this.constant=n}set(t,n){return this.normal.copy(t),this.constant=n,this}setComponents(t,n,s,o){return this.normal.set(t,n,s),this.constant=o,this}setFromNormalAndCoplanarPoint(t,n){return this.normal.copy(t),this.constant=-n.dot(this.normal),this}setFromCoplanarPoints(t,n,s){const o=sp.subVectors(s,n).cross(aA.subVectors(t,n)).normalize();return this.setFromNormalAndCoplanarPoint(o,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,n){return n.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,n){const s=t.delta(sp),o=this.normal.dot(s);if(o===0)return this.distanceToPoint(t.start)===0?n.copy(t.start):null;const c=-(t.start.dot(this.normal)+this.constant)/o;return c<0||c>1?null:n.copy(t.start).addScaledVector(s,c)}intersectsLine(t){const n=this.distanceToPoint(t.start),s=this.distanceToPoint(t.end);return n<0&&s>0||s<0&&n>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,n){const s=n||sA.getNormalMatrix(t),o=this.coplanarPoint(sp).applyMatrix4(t),c=this.normal.applyMatrix3(s).normalize();return this.constant=-o.dot(c),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Js=new Fm,Ku=new W;class Hm{constructor(t=new nr,n=new nr,s=new nr,o=new nr,c=new nr,f=new nr){this.planes=[t,n,s,o,c,f]}set(t,n,s,o,c,f){const d=this.planes;return d[0].copy(t),d[1].copy(n),d[2].copy(s),d[3].copy(o),d[4].copy(c),d[5].copy(f),this}copy(t){const n=this.planes;for(let s=0;s<6;s++)n[s].copy(t.planes[s]);return this}setFromProjectionMatrix(t,n=Ua){const s=this.planes,o=t.elements,c=o[0],f=o[1],d=o[2],p=o[3],m=o[4],v=o[5],_=o[6],x=o[7],E=o[8],M=o[9],T=o[10],S=o[11],y=o[12],I=o[13],D=o[14],C=o[15];if(s[0].setComponents(p-c,x-m,S-E,C-y).normalize(),s[1].setComponents(p+c,x+m,S+E,C+y).normalize(),s[2].setComponents(p+f,x+v,S+M,C+I).normalize(),s[3].setComponents(p-f,x-v,S-M,C-I).normalize(),s[4].setComponents(p-d,x-_,S-T,C-D).normalize(),n===Ua)s[5].setComponents(p+d,x+_,S+T,C+D).normalize();else if(n===gf)s[5].setComponents(d,_,T,D).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+n);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),Js.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const n=t.geometry;n.boundingSphere===null&&n.computeBoundingSphere(),Js.copy(n.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(Js)}intersectsSprite(t){return Js.center.set(0,0,0),Js.radius=.7071067811865476,Js.applyMatrix4(t.matrixWorld),this.intersectsSphere(Js)}intersectsSphere(t){const n=this.planes,s=t.center,o=-t.radius;for(let c=0;c<6;c++)if(n[c].distanceToPoint(s)<o)return!1;return!0}intersectsBox(t){const n=this.planes;for(let s=0;s<6;s++){const o=n[s];if(Ku.x=o.normal.x>0?t.max.x:t.min.x,Ku.y=o.normal.y>0?t.max.y:t.min.y,Ku.z=o.normal.z>0?t.max.z:t.min.z,o.distanceToPoint(Ku)<0)return!1}return!0}containsPoint(t){const n=this.planes;for(let s=0;s<6;s++)if(n[s].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class So extends si{constructor(){super(),this.isGroup=!0,this.type="Group"}}class uS extends ai{constructor(t,n,s,o,c,f,d,p,m,v=bo){if(v!==bo&&v!==jo)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");s===void 0&&v===bo&&(s=xr),s===void 0&&v===jo&&(s=Vo),super(null,o,c,f,d,p,v,s,m),this.isDepthTexture=!0,this.image={width:t,height:n},this.magFilter=d!==void 0?d:Hi,this.minFilter=p!==void 0?p:Hi,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.compareFunction=t.compareFunction,this}toJSON(t){const n=super.toJSON(t);return this.compareFunction!==null&&(n.compareFunction=this.compareFunction),n}}class Fa{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(t,n){const s=this.getUtoTmapping(t);return this.getPoint(s,n)}getPoints(t=5){const n=[];for(let s=0;s<=t;s++)n.push(this.getPoint(s/t));return n}getSpacedPoints(t=5){const n=[];for(let s=0;s<=t;s++)n.push(this.getPointAt(s/t));return n}getLength(){const t=this.getLengths();return t[t.length-1]}getLengths(t=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===t+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const n=[];let s,o=this.getPoint(0),c=0;n.push(0);for(let f=1;f<=t;f++)s=this.getPoint(f/t),c+=s.distanceTo(o),n.push(c),o=s;return this.cacheArcLengths=n,n}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(t,n){const s=this.getLengths();let o=0;const c=s.length;let f;n?f=n:f=t*s[c-1];let d=0,p=c-1,m;for(;d<=p;)if(o=Math.floor(d+(p-d)/2),m=s[o]-f,m<0)d=o+1;else if(m>0)p=o-1;else{p=o;break}if(o=p,s[o]===f)return o/(c-1);const v=s[o],x=s[o+1]-v,E=(f-v)/x;return(o+E)/(c-1)}getTangent(t,n){let o=t-1e-4,c=t+1e-4;o<0&&(o=0),c>1&&(c=1);const f=this.getPoint(o),d=this.getPoint(c),p=n||(f.isVector2?new Wt:new W);return p.copy(d).sub(f).normalize(),p}getTangentAt(t,n){const s=this.getUtoTmapping(t);return this.getTangent(s,n)}computeFrenetFrames(t,n){const s=new W,o=[],c=[],f=[],d=new W,p=new an;for(let E=0;E<=t;E++){const M=E/t;o[E]=this.getTangentAt(M,new W)}c[0]=new W,f[0]=new W;let m=Number.MAX_VALUE;const v=Math.abs(o[0].x),_=Math.abs(o[0].y),x=Math.abs(o[0].z);v<=m&&(m=v,s.set(1,0,0)),_<=m&&(m=_,s.set(0,1,0)),x<=m&&s.set(0,0,1),d.crossVectors(o[0],s).normalize(),c[0].crossVectors(o[0],d),f[0].crossVectors(o[0],c[0]);for(let E=1;E<=t;E++){if(c[E]=c[E-1].clone(),f[E]=f[E-1].clone(),d.crossVectors(o[E-1],o[E]),d.length()>Number.EPSILON){d.normalize();const M=Math.acos(ge(o[E-1].dot(o[E]),-1,1));c[E].applyMatrix4(p.makeRotationAxis(d,M))}f[E].crossVectors(o[E],c[E])}if(n===!0){let E=Math.acos(ge(c[0].dot(c[t]),-1,1));E/=t,o[0].dot(d.crossVectors(c[0],c[t]))>0&&(E=-E);for(let M=1;M<=t;M++)c[M].applyMatrix4(p.makeRotationAxis(o[M],E*M)),f[M].crossVectors(o[M],c[M])}return{tangents:o,normals:c,binormals:f}}clone(){return new this.constructor().copy(this)}copy(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}toJSON(){const t={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return t.arcLengthDivisions=this.arcLengthDivisions,t.type=this.type,t}fromJSON(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}}class fS extends Fa{constructor(t=0,n=0,s=1,o=1,c=0,f=Math.PI*2,d=!1,p=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=t,this.aY=n,this.xRadius=s,this.yRadius=o,this.aStartAngle=c,this.aEndAngle=f,this.aClockwise=d,this.aRotation=p}getPoint(t,n=new Wt){const s=n,o=Math.PI*2;let c=this.aEndAngle-this.aStartAngle;const f=Math.abs(c)<Number.EPSILON;for(;c<0;)c+=o;for(;c>o;)c-=o;c<Number.EPSILON&&(f?c=0:c=o),this.aClockwise===!0&&!f&&(c===o?c=-o:c=c-o);const d=this.aStartAngle+t*c;let p=this.aX+this.xRadius*Math.cos(d),m=this.aY+this.yRadius*Math.sin(d);if(this.aRotation!==0){const v=Math.cos(this.aRotation),_=Math.sin(this.aRotation),x=p-this.aX,E=m-this.aY;p=x*v-E*_+this.aX,m=x*_+E*v+this.aY}return s.set(p,m)}copy(t){return super.copy(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}toJSON(){const t=super.toJSON();return t.aX=this.aX,t.aY=this.aY,t.xRadius=this.xRadius,t.yRadius=this.yRadius,t.aStartAngle=this.aStartAngle,t.aEndAngle=this.aEndAngle,t.aClockwise=this.aClockwise,t.aRotation=this.aRotation,t}fromJSON(t){return super.fromJSON(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}}class rA extends fS{constructor(t,n,s,o,c,f){super(t,n,s,s,o,c,f),this.isArcCurve=!0,this.type="ArcCurve"}}function Gm(){let a=0,t=0,n=0,s=0;function o(c,f,d,p){a=c,t=d,n=-3*c+3*f-2*d-p,s=2*c-2*f+d+p}return{initCatmullRom:function(c,f,d,p,m){o(f,d,m*(d-c),m*(p-f))},initNonuniformCatmullRom:function(c,f,d,p,m,v,_){let x=(f-c)/m-(d-c)/(m+v)+(d-f)/v,E=(d-f)/v-(p-f)/(v+_)+(p-d)/_;x*=v,E*=v,o(f,d,x,E)},calc:function(c){const f=c*c,d=f*c;return a+t*c+n*f+s*d}}}const Ju=new W,rp=new Gm,op=new Gm,lp=new Gm;class dS extends Fa{constructor(t=[],n=!1,s="centripetal",o=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=t,this.closed=n,this.curveType=s,this.tension=o}getPoint(t,n=new W){const s=n,o=this.points,c=o.length,f=(c-(this.closed?0:1))*t;let d=Math.floor(f),p=f-d;this.closed?d+=d>0?0:(Math.floor(Math.abs(d)/c)+1)*c:p===0&&d===c-1&&(d=c-2,p=1);let m,v;this.closed||d>0?m=o[(d-1)%c]:(Ju.subVectors(o[0],o[1]).add(o[0]),m=Ju);const _=o[d%c],x=o[(d+1)%c];if(this.closed||d+2<c?v=o[(d+2)%c]:(Ju.subVectors(o[c-1],o[c-2]).add(o[c-1]),v=Ju),this.curveType==="centripetal"||this.curveType==="chordal"){const E=this.curveType==="chordal"?.5:.25;let M=Math.pow(m.distanceToSquared(_),E),T=Math.pow(_.distanceToSquared(x),E),S=Math.pow(x.distanceToSquared(v),E);T<1e-4&&(T=1),M<1e-4&&(M=T),S<1e-4&&(S=T),rp.initNonuniformCatmullRom(m.x,_.x,x.x,v.x,M,T,S),op.initNonuniformCatmullRom(m.y,_.y,x.y,v.y,M,T,S),lp.initNonuniformCatmullRom(m.z,_.z,x.z,v.z,M,T,S)}else this.curveType==="catmullrom"&&(rp.initCatmullRom(m.x,_.x,x.x,v.x,this.tension),op.initCatmullRom(m.y,_.y,x.y,v.y,this.tension),lp.initCatmullRom(m.z,_.z,x.z,v.z,this.tension));return s.set(rp.calc(p),op.calc(p),lp.calc(p)),s}copy(t){super.copy(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const o=t.points[n];this.points.push(o.clone())}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,s=this.points.length;n<s;n++){const o=this.points[n];t.points.push(o.toArray())}return t.closed=this.closed,t.curveType=this.curveType,t.tension=this.tension,t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const o=t.points[n];this.points.push(new W().fromArray(o))}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}}function My(a,t,n,s,o){const c=(s-t)*.5,f=(o-n)*.5,d=a*a,p=a*d;return(2*n-2*s+c+f)*p+(-3*n+3*s-2*c-f)*d+c*a+n}function oA(a,t){const n=1-a;return n*n*t}function lA(a,t){return 2*(1-a)*a*t}function cA(a,t){return a*a*t}function ec(a,t,n,s){return oA(a,t)+lA(a,n)+cA(a,s)}function uA(a,t){const n=1-a;return n*n*n*t}function fA(a,t){const n=1-a;return 3*n*n*a*t}function dA(a,t){return 3*(1-a)*a*a*t}function hA(a,t){return a*a*a*t}function nc(a,t,n,s,o){return uA(a,t)+fA(a,n)+dA(a,s)+hA(a,o)}class pA extends Fa{constructor(t=new Wt,n=new Wt,s=new Wt,o=new Wt){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=t,this.v1=n,this.v2=s,this.v3=o}getPoint(t,n=new Wt){const s=n,o=this.v0,c=this.v1,f=this.v2,d=this.v3;return s.set(nc(t,o.x,c.x,f.x,d.x),nc(t,o.y,c.y,f.y,d.y)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class mA extends Fa{constructor(t=new W,n=new W,s=new W,o=new W){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=t,this.v1=n,this.v2=s,this.v3=o}getPoint(t,n=new W){const s=n,o=this.v0,c=this.v1,f=this.v2,d=this.v3;return s.set(nc(t,o.x,c.x,f.x,d.x),nc(t,o.y,c.y,f.y,d.y),nc(t,o.z,c.z,f.z,d.z)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class gA extends Fa{constructor(t=new Wt,n=new Wt){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=t,this.v2=n}getPoint(t,n=new Wt){const s=n;return t===1?s.copy(this.v2):(s.copy(this.v2).sub(this.v1),s.multiplyScalar(t).add(this.v1)),s}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new Wt){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class vA extends Fa{constructor(t=new W,n=new W){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=t,this.v2=n}getPoint(t,n=new W){const s=n;return t===1?s.copy(this.v2):(s.copy(this.v2).sub(this.v1),s.multiplyScalar(t).add(this.v1)),s}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new W){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class _A extends Fa{constructor(t=new Wt,n=new Wt,s=new Wt){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=t,this.v1=n,this.v2=s}getPoint(t,n=new Wt){const s=n,o=this.v0,c=this.v1,f=this.v2;return s.set(ec(t,o.x,c.x,f.x),ec(t,o.y,c.y,f.y)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class hS extends Fa{constructor(t=new W,n=new W,s=new W){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=t,this.v1=n,this.v2=s}getPoint(t,n=new W){const s=n,o=this.v0,c=this.v1,f=this.v2;return s.set(ec(t,o.x,c.x,f.x),ec(t,o.y,c.y,f.y),ec(t,o.z,c.z,f.z)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class yA extends Fa{constructor(t=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=t}getPoint(t,n=new Wt){const s=n,o=this.points,c=(o.length-1)*t,f=Math.floor(c),d=c-f,p=o[f===0?f:f-1],m=o[f],v=o[f>o.length-2?o.length-1:f+1],_=o[f>o.length-3?o.length-1:f+2];return s.set(My(d,p.x,m.x,v.x,_.x),My(d,p.y,m.y,v.y,_.y)),s}copy(t){super.copy(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const o=t.points[n];this.points.push(o.clone())}return this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,s=this.points.length;n<s;n++){const o=this.points[n];t.points.push(o.toArray())}return t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const o=t.points[n];this.points.push(new Wt().fromArray(o))}return this}}var xA=Object.freeze({__proto__:null,ArcCurve:rA,CatmullRomCurve3:dS,CubicBezierCurve:pA,CubicBezierCurve3:mA,EllipseCurve:fS,LineCurve:gA,LineCurve3:vA,QuadraticBezierCurve:_A,QuadraticBezierCurve3:hS,SplineCurve:yA});class Mf extends Vi{constructor(t=1,n=1,s=1,o=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:n,widthSegments:s,heightSegments:o};const c=t/2,f=n/2,d=Math.floor(s),p=Math.floor(o),m=d+1,v=p+1,_=t/d,x=n/p,E=[],M=[],T=[],S=[];for(let y=0;y<v;y++){const I=y*x-f;for(let D=0;D<m;D++){const C=D*_-c;M.push(C,-I,0),T.push(0,0,1),S.push(D/d),S.push(1-y/p)}}for(let y=0;y<p;y++)for(let I=0;I<d;I++){const D=I+m*y,C=I+m*(y+1),V=I+1+m*(y+1),L=I+1+m*y;E.push(D,C,L),E.push(C,V,L)}this.setIndex(E),this.setAttribute("position",new Cn(M,3)),this.setAttribute("normal",new Cn(T,3)),this.setAttribute("uv",new Cn(S,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new Mf(t.width,t.height,t.widthSegments,t.heightSegments)}}class Ef extends Vi{constructor(t=1,n=32,s=16,o=0,c=Math.PI*2,f=0,d=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:t,widthSegments:n,heightSegments:s,phiStart:o,phiLength:c,thetaStart:f,thetaLength:d},n=Math.max(3,Math.floor(n)),s=Math.max(2,Math.floor(s));const p=Math.min(f+d,Math.PI);let m=0;const v=[],_=new W,x=new W,E=[],M=[],T=[],S=[];for(let y=0;y<=s;y++){const I=[],D=y/s;let C=0;y===0&&f===0?C=.5/n:y===s&&p===Math.PI&&(C=-.5/n);for(let V=0;V<=n;V++){const L=V/n;_.x=-t*Math.cos(o+L*c)*Math.sin(f+D*d),_.y=t*Math.cos(f+D*d),_.z=t*Math.sin(o+L*c)*Math.sin(f+D*d),M.push(_.x,_.y,_.z),x.copy(_).normalize(),T.push(x.x,x.y,x.z),S.push(L+C,1-D),I.push(m++)}v.push(I)}for(let y=0;y<s;y++)for(let I=0;I<n;I++){const D=v[y][I+1],C=v[y][I],V=v[y+1][I],L=v[y+1][I+1];(y!==0||f>0)&&E.push(D,C,L),(y!==s-1||p<Math.PI)&&E.push(C,V,L)}this.setIndex(E),this.setAttribute("position",new Cn(M,3)),this.setAttribute("normal",new Cn(T,3)),this.setAttribute("uv",new Cn(S,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new Ef(t.radius,t.widthSegments,t.heightSegments,t.phiStart,t.phiLength,t.thetaStart,t.thetaLength)}}class yf extends Vi{constructor(t=1,n=.4,s=12,o=48,c=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:t,tube:n,radialSegments:s,tubularSegments:o,arc:c},s=Math.floor(s),o=Math.floor(o);const f=[],d=[],p=[],m=[],v=new W,_=new W,x=new W;for(let E=0;E<=s;E++)for(let M=0;M<=o;M++){const T=M/o*c,S=E/s*Math.PI*2;_.x=(t+n*Math.cos(S))*Math.cos(T),_.y=(t+n*Math.cos(S))*Math.sin(T),_.z=n*Math.sin(S),d.push(_.x,_.y,_.z),v.x=t*Math.cos(T),v.y=t*Math.sin(T),x.subVectors(_,v).normalize(),p.push(x.x,x.y,x.z),m.push(M/o),m.push(E/s)}for(let E=1;E<=s;E++)for(let M=1;M<=o;M++){const T=(o+1)*E+M-1,S=(o+1)*(E-1)+M-1,y=(o+1)*(E-1)+M,I=(o+1)*E+M;f.push(T,S,I),f.push(S,y,I)}this.setIndex(f),this.setAttribute("position",new Cn(d,3)),this.setAttribute("normal",new Cn(p,3)),this.setAttribute("uv",new Cn(m,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new yf(t.radius,t.tube,t.radialSegments,t.tubularSegments,t.arc)}}class Vm extends Vi{constructor(t=new hS(new W(-1,-1,0),new W(-1,1,0),new W(1,1,0)),n=64,s=1,o=8,c=!1){super(),this.type="TubeGeometry",this.parameters={path:t,tubularSegments:n,radius:s,radialSegments:o,closed:c};const f=t.computeFrenetFrames(n,c);this.tangents=f.tangents,this.normals=f.normals,this.binormals=f.binormals;const d=new W,p=new W,m=new Wt;let v=new W;const _=[],x=[],E=[],M=[];T(),this.setIndex(M),this.setAttribute("position",new Cn(_,3)),this.setAttribute("normal",new Cn(x,3)),this.setAttribute("uv",new Cn(E,2));function T(){for(let D=0;D<n;D++)S(D);S(c===!1?n:0),I(),y()}function S(D){v=t.getPointAt(D/n,v);const C=f.normals[D],V=f.binormals[D];for(let L=0;L<=o;L++){const P=L/o*Math.PI*2,G=Math.sin(P),U=-Math.cos(P);p.x=U*C.x+G*V.x,p.y=U*C.y+G*V.y,p.z=U*C.z+G*V.z,p.normalize(),x.push(p.x,p.y,p.z),d.x=v.x+s*p.x,d.y=v.y+s*p.y,d.z=v.z+s*p.z,_.push(d.x,d.y,d.z)}}function y(){for(let D=1;D<=n;D++)for(let C=1;C<=o;C++){const V=(o+1)*(D-1)+(C-1),L=(o+1)*D+(C-1),P=(o+1)*D+C,G=(o+1)*(D-1)+C;M.push(V,L,G),M.push(L,P,G)}}function I(){for(let D=0;D<=n;D++)for(let C=0;C<=o;C++)m.x=D/n,m.y=C/o,E.push(m.x,m.y)}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}toJSON(){const t=super.toJSON();return t.path=this.parameters.path.toJSON(),t}static fromJSON(t){return new Vm(new xA[t.path.type]().fromJSON(t.path),t.tubularSegments,t.radius,t.radialSegments,t.closed)}}class SA extends Sf{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=aT,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class MA extends Sf{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}class pS extends si{constructor(t,n=1){super(),this.isLight=!0,this.type="Light",this.color=new pe(t),this.intensity=n}dispose(){}copy(t,n){return super.copy(t,n),this.color.copy(t.color),this.intensity=t.intensity,this}toJSON(t){const n=super.toJSON(t);return n.object.color=this.color.getHex(),n.object.intensity=this.intensity,this.groundColor!==void 0&&(n.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(n.object.distance=this.distance),this.angle!==void 0&&(n.object.angle=this.angle),this.decay!==void 0&&(n.object.decay=this.decay),this.penumbra!==void 0&&(n.object.penumbra=this.penumbra),this.shadow!==void 0&&(n.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(n.object.target=this.target.uuid),n}}const cp=new an,Ey=new W,by=new W;class EA{constructor(t){this.camera=t,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Wt(512,512),this.map=null,this.mapPass=null,this.matrix=new an,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Hm,this._frameExtents=new Wt(1,1),this._viewportCount=1,this._viewports=[new We(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(t){const n=this.camera,s=this.matrix;Ey.setFromMatrixPosition(t.matrixWorld),n.position.copy(Ey),by.setFromMatrixPosition(t.target.matrixWorld),n.lookAt(by),n.updateMatrixWorld(),cp.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(cp),s.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),s.multiply(cp)}getViewport(t){return this._viewports[t]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(t){return this.camera=t.camera.clone(),this.intensity=t.intensity,this.bias=t.bias,this.radius=t.radius,this.mapSize.copy(t.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const t={};return this.intensity!==1&&(t.intensity=this.intensity),this.bias!==0&&(t.bias=this.bias),this.normalBias!==0&&(t.normalBias=this.normalBias),this.radius!==1&&(t.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(t.mapSize=this.mapSize.toArray()),t.camera=this.camera.toJSON(!1).object,delete t.camera.matrix,t}}const Ty=new an,Wl=new W,up=new W;class bA extends EA{constructor(){super(new _i(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Wt(4,2),this._viewportCount=6,this._viewports=[new We(2,1,1,1),new We(0,1,1,1),new We(3,1,1,1),new We(1,1,1,1),new We(3,0,1,1),new We(1,0,1,1)],this._cubeDirections=[new W(1,0,0),new W(-1,0,0),new W(0,0,1),new W(0,0,-1),new W(0,1,0),new W(0,-1,0)],this._cubeUps=[new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,0,1),new W(0,0,-1)]}updateMatrices(t,n=0){const s=this.camera,o=this.matrix,c=t.distance||s.far;c!==s.far&&(s.far=c,s.updateProjectionMatrix()),Wl.setFromMatrixPosition(t.matrixWorld),s.position.copy(Wl),up.copy(s.position),up.add(this._cubeDirections[n]),s.up.copy(this._cubeUps[n]),s.lookAt(up),s.updateMatrixWorld(),o.makeTranslation(-Wl.x,-Wl.y,-Wl.z),Ty.multiplyMatrices(s.projectionMatrix,s.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Ty)}}class TA extends pS{constructor(t,n,s=0,o=2){super(t,n),this.isPointLight=!0,this.type="PointLight",this.distance=s,this.decay=o,this.shadow=new bA}get power(){return this.intensity*4*Math.PI}set power(t){this.intensity=t/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(t,n){return super.copy(t,n),this.distance=t.distance,this.decay=t.decay,this.shadow=t.shadow.clone(),this}}class mS extends lS{constructor(t=-1,n=1,s=1,o=-1,c=.1,f=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=n,this.top=s,this.bottom=o,this.near=c,this.far=f,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,n,s,o,c,f){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=o,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),n=(this.top-this.bottom)/(2*this.zoom),s=(this.right+this.left)/2,o=(this.top+this.bottom)/2;let c=s-t,f=s+t,d=o+n,p=o-n;if(this.view!==null&&this.view.enabled){const m=(this.right-this.left)/this.view.fullWidth/this.zoom,v=(this.top-this.bottom)/this.view.fullHeight/this.zoom;c+=m*this.view.offsetX,f=c+m*this.view.width,d-=v*this.view.offsetY,p=d-v*this.view.height}this.projectionMatrix.makeOrthographic(c,f,d,p,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.zoom=this.zoom,n.object.left=this.left,n.object.right=this.right,n.object.top=this.top,n.object.bottom=this.bottom,n.object.near=this.near,n.object.far=this.far,this.view!==null&&(n.object.view=Object.assign({},this.view)),n}}class AA extends pS{constructor(t,n){super(t,n),this.isAmbientLight=!0,this.type="AmbientLight"}}class CA extends _i{constructor(t=[]){super(),this.isArrayCamera=!0,this.cameras=t}}class gS{constructor(t=!0){this.autoStart=t,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Ay(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let t=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const n=Ay();t=(n-this.oldTime)/1e3,this.oldTime=n,this.elapsedTime+=t}return t}}function Ay(){return performance.now()}function Cy(a,t,n,s){const o=RA(s);switch(n){case qx:return a*t;case Yx:return a*t;case Qx:return a*t*2;case Zx:return a*t/o.components*o.byteLength;case Pm:return a*t/o.components*o.byteLength;case Kx:return a*t*2/o.components*o.byteLength;case zm:return a*t*2/o.components*o.byteLength;case Wx:return a*t*3/o.components*o.byteLength;case Fi:return a*t*4/o.components*o.byteLength;case Im:return a*t*4/o.components*o.byteLength;case sf:case rf:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*8;case of:case lf:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case Yp:case Zp:return Math.max(a,16)*Math.max(t,8)/4;case Wp:case Qp:return Math.max(a,8)*Math.max(t,8)/2;case Kp:case Jp:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*8;case $p:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case tm:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case em:return Math.floor((a+4)/5)*Math.floor((t+3)/4)*16;case nm:return Math.floor((a+4)/5)*Math.floor((t+4)/5)*16;case im:return Math.floor((a+5)/6)*Math.floor((t+4)/5)*16;case am:return Math.floor((a+5)/6)*Math.floor((t+5)/6)*16;case sm:return Math.floor((a+7)/8)*Math.floor((t+4)/5)*16;case rm:return Math.floor((a+7)/8)*Math.floor((t+5)/6)*16;case om:return Math.floor((a+7)/8)*Math.floor((t+7)/8)*16;case lm:return Math.floor((a+9)/10)*Math.floor((t+4)/5)*16;case cm:return Math.floor((a+9)/10)*Math.floor((t+5)/6)*16;case um:return Math.floor((a+9)/10)*Math.floor((t+7)/8)*16;case fm:return Math.floor((a+9)/10)*Math.floor((t+9)/10)*16;case dm:return Math.floor((a+11)/12)*Math.floor((t+9)/10)*16;case hm:return Math.floor((a+11)/12)*Math.floor((t+11)/12)*16;case cf:case pm:case mm:return Math.ceil(a/4)*Math.ceil(t/4)*16;case Jx:case gm:return Math.ceil(a/4)*Math.ceil(t/4)*8;case vm:case _m:return Math.ceil(a/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${n} format.`)}function RA(a){switch(a){case Ia:case jx:return{byteLength:1,components:1};case lc:case kx:case Pa:return{byteLength:2,components:1};case Lm:case Om:return{byteLength:2,components:4};case xr:case Um:case Da:return{byteLength:4,components:1};case Xx:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${a}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Dm}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Dm);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function vS(){let a=null,t=!1,n=null,s=null;function o(c,f){n(c,f),s=a.requestAnimationFrame(o)}return{start:function(){t!==!0&&n!==null&&(s=a.requestAnimationFrame(o),t=!0)},stop:function(){a.cancelAnimationFrame(s),t=!1},setAnimationLoop:function(c){n=c},setContext:function(c){a=c}}}function wA(a){const t=new WeakMap;function n(d,p){const m=d.array,v=d.usage,_=m.byteLength,x=a.createBuffer();a.bindBuffer(p,x),a.bufferData(p,m,v),d.onUploadCallback();let E;if(m instanceof Float32Array)E=a.FLOAT;else if(m instanceof Uint16Array)d.isFloat16BufferAttribute?E=a.HALF_FLOAT:E=a.UNSIGNED_SHORT;else if(m instanceof Int16Array)E=a.SHORT;else if(m instanceof Uint32Array)E=a.UNSIGNED_INT;else if(m instanceof Int32Array)E=a.INT;else if(m instanceof Int8Array)E=a.BYTE;else if(m instanceof Uint8Array)E=a.UNSIGNED_BYTE;else if(m instanceof Uint8ClampedArray)E=a.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+m);return{buffer:x,type:E,bytesPerElement:m.BYTES_PER_ELEMENT,version:d.version,size:_}}function s(d,p,m){const v=p.array,_=p.updateRanges;if(a.bindBuffer(m,d),_.length===0)a.bufferSubData(m,0,v);else{_.sort((E,M)=>E.start-M.start);let x=0;for(let E=1;E<_.length;E++){const M=_[x],T=_[E];T.start<=M.start+M.count+1?M.count=Math.max(M.count,T.start+T.count-M.start):(++x,_[x]=T)}_.length=x+1;for(let E=0,M=_.length;E<M;E++){const T=_[E];a.bufferSubData(m,T.start*v.BYTES_PER_ELEMENT,v,T.start,T.count)}p.clearUpdateRanges()}p.onUploadCallback()}function o(d){return d.isInterleavedBufferAttribute&&(d=d.data),t.get(d)}function c(d){d.isInterleavedBufferAttribute&&(d=d.data);const p=t.get(d);p&&(a.deleteBuffer(p.buffer),t.delete(d))}function f(d,p){if(d.isInterleavedBufferAttribute&&(d=d.data),d.isGLBufferAttribute){const v=t.get(d);(!v||v.version<d.version)&&t.set(d,{buffer:d.buffer,type:d.type,bytesPerElement:d.elementSize,version:d.version});return}const m=t.get(d);if(m===void 0)t.set(d,n(d,p));else if(m.version<d.version){if(m.size!==d.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");s(m.buffer,d,p),m.version=d.version}}return{get:o,remove:c,update:f}}var NA=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,DA=`#ifdef USE_ALPHAHASH
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
#endif`,UA=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,LA=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,OA=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,PA=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,zA=`#ifdef USE_AOMAP
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
#endif`,IA=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,BA=`#ifdef USE_BATCHING
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
#endif`,FA=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,HA=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,GA=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,VA=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,jA=`#ifdef USE_IRIDESCENCE
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
#endif`,kA=`#ifdef USE_BUMPMAP
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
#endif`,XA=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,qA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,WA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,YA=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,QA=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,ZA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,KA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,JA=`#if defined( USE_COLOR_ALPHA )
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
#endif`,$A=`#define PI 3.141592653589793
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
} // validated`,t2=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,e2=`vec3 transformedNormal = objectNormal;
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
#endif`,n2=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,i2=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,a2=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,s2=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,r2="gl_FragColor = linearToOutputTexel( gl_FragColor );",o2=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,l2=`#ifdef USE_ENVMAP
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
#endif`,c2=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,u2=`#ifdef USE_ENVMAP
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
#endif`,f2=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,d2=`#ifdef USE_ENVMAP
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
#endif`,h2=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,p2=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,m2=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,g2=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,v2=`#ifdef USE_GRADIENTMAP
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
}`,_2=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,y2=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,x2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,S2=`uniform bool receiveShadow;
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
#endif`,M2=`#ifdef USE_ENVMAP
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
#endif`,E2=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,b2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,T2=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,A2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,C2=`PhysicalMaterial material;
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
#endif`,R2=`struct PhysicalMaterial {
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
}`,w2=`
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
#endif`,N2=`#if defined( RE_IndirectDiffuse )
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
#endif`,D2=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,U2=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,L2=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,O2=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,P2=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,z2=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,I2=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,B2=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,F2=`#if defined( USE_POINTS_UV )
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
#endif`,H2=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,G2=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,V2=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,j2=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,k2=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,X2=`#ifdef USE_MORPHTARGETS
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
#endif`,q2=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,W2=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,Y2=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,Q2=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Z2=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,K2=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,J2=`#ifdef USE_NORMALMAP
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
#endif`,$2=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,tC=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,eC=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,nC=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,iC=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,aC=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,sC=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,rC=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,oC=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,lC=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,cC=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,uC=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,fC=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,dC=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,hC=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,pC=`float getShadowMask() {
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
}`,mC=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,gC=`#ifdef USE_SKINNING
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
#endif`,vC=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,_C=`#ifdef USE_SKINNING
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
#endif`,yC=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,xC=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,SC=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,MC=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,EC=`#ifdef USE_TRANSMISSION
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
#endif`,bC=`#ifdef USE_TRANSMISSION
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
#endif`,TC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,AC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,CC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,RC=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const wC=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,NC=`uniform sampler2D t2D;
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
}`,DC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,UC=`#ifdef ENVMAP_TYPE_CUBE
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
}`,LC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,OC=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,PC=`#include <common>
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
}`,zC=`#if DEPTH_PACKING == 3200
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
}`,IC=`#define DISTANCE
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
}`,BC=`#define DISTANCE
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
}`,FC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,HC=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,GC=`uniform float scale;
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
}`,VC=`uniform vec3 diffuse;
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
}`,jC=`#include <common>
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
}`,kC=`uniform vec3 diffuse;
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
}`,XC=`#define LAMBERT
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
}`,qC=`#define LAMBERT
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
}`,WC=`#define MATCAP
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
}`,YC=`#define MATCAP
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
}`,QC=`#define NORMAL
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
}`,ZC=`#define NORMAL
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
}`,KC=`#define PHONG
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
}`,JC=`#define PHONG
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
}`,$C=`#define STANDARD
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
}`,tR=`#define STANDARD
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
}`,eR=`#define TOON
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
}`,nR=`#define TOON
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
}`,iR=`uniform float size;
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
}`,aR=`uniform vec3 diffuse;
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
}`,sR=`#include <common>
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
}`,rR=`uniform vec3 color;
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
}`,oR=`uniform float rotation;
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
}`,lR=`uniform vec3 diffuse;
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
}`,he={alphahash_fragment:NA,alphahash_pars_fragment:DA,alphamap_fragment:UA,alphamap_pars_fragment:LA,alphatest_fragment:OA,alphatest_pars_fragment:PA,aomap_fragment:zA,aomap_pars_fragment:IA,batching_pars_vertex:BA,batching_vertex:FA,begin_vertex:HA,beginnormal_vertex:GA,bsdfs:VA,iridescence_fragment:jA,bumpmap_pars_fragment:kA,clipping_planes_fragment:XA,clipping_planes_pars_fragment:qA,clipping_planes_pars_vertex:WA,clipping_planes_vertex:YA,color_fragment:QA,color_pars_fragment:ZA,color_pars_vertex:KA,color_vertex:JA,common:$A,cube_uv_reflection_fragment:t2,defaultnormal_vertex:e2,displacementmap_pars_vertex:n2,displacementmap_vertex:i2,emissivemap_fragment:a2,emissivemap_pars_fragment:s2,colorspace_fragment:r2,colorspace_pars_fragment:o2,envmap_fragment:l2,envmap_common_pars_fragment:c2,envmap_pars_fragment:u2,envmap_pars_vertex:f2,envmap_physical_pars_fragment:M2,envmap_vertex:d2,fog_vertex:h2,fog_pars_vertex:p2,fog_fragment:m2,fog_pars_fragment:g2,gradientmap_pars_fragment:v2,lightmap_pars_fragment:_2,lights_lambert_fragment:y2,lights_lambert_pars_fragment:x2,lights_pars_begin:S2,lights_toon_fragment:E2,lights_toon_pars_fragment:b2,lights_phong_fragment:T2,lights_phong_pars_fragment:A2,lights_physical_fragment:C2,lights_physical_pars_fragment:R2,lights_fragment_begin:w2,lights_fragment_maps:N2,lights_fragment_end:D2,logdepthbuf_fragment:U2,logdepthbuf_pars_fragment:L2,logdepthbuf_pars_vertex:O2,logdepthbuf_vertex:P2,map_fragment:z2,map_pars_fragment:I2,map_particle_fragment:B2,map_particle_pars_fragment:F2,metalnessmap_fragment:H2,metalnessmap_pars_fragment:G2,morphinstance_vertex:V2,morphcolor_vertex:j2,morphnormal_vertex:k2,morphtarget_pars_vertex:X2,morphtarget_vertex:q2,normal_fragment_begin:W2,normal_fragment_maps:Y2,normal_pars_fragment:Q2,normal_pars_vertex:Z2,normal_vertex:K2,normalmap_pars_fragment:J2,clearcoat_normal_fragment_begin:$2,clearcoat_normal_fragment_maps:tC,clearcoat_pars_fragment:eC,iridescence_pars_fragment:nC,opaque_fragment:iC,packing:aC,premultiplied_alpha_fragment:sC,project_vertex:rC,dithering_fragment:oC,dithering_pars_fragment:lC,roughnessmap_fragment:cC,roughnessmap_pars_fragment:uC,shadowmap_pars_fragment:fC,shadowmap_pars_vertex:dC,shadowmap_vertex:hC,shadowmask_pars_fragment:pC,skinbase_vertex:mC,skinning_pars_vertex:gC,skinning_vertex:vC,skinnormal_vertex:_C,specularmap_fragment:yC,specularmap_pars_fragment:xC,tonemapping_fragment:SC,tonemapping_pars_fragment:MC,transmission_fragment:EC,transmission_pars_fragment:bC,uv_pars_fragment:TC,uv_pars_vertex:AC,uv_vertex:CC,worldpos_vertex:RC,background_vert:wC,background_frag:NC,backgroundCube_vert:DC,backgroundCube_frag:UC,cube_vert:LC,cube_frag:OC,depth_vert:PC,depth_frag:zC,distanceRGBA_vert:IC,distanceRGBA_frag:BC,equirect_vert:FC,equirect_frag:HC,linedashed_vert:GC,linedashed_frag:VC,meshbasic_vert:jC,meshbasic_frag:kC,meshlambert_vert:XC,meshlambert_frag:qC,meshmatcap_vert:WC,meshmatcap_frag:YC,meshnormal_vert:QC,meshnormal_frag:ZC,meshphong_vert:KC,meshphong_frag:JC,meshphysical_vert:$C,meshphysical_frag:tR,meshtoon_vert:eR,meshtoon_frag:nR,points_vert:iR,points_frag:aR,shadow_vert:sR,shadow_frag:rR,sprite_vert:oR,sprite_frag:lR},Lt={common:{diffuse:{value:new pe(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new de},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new de}},envmap:{envMap:{value:null},envMapRotation:{value:new de},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new de}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new de}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new de},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new de},normalScale:{value:new Wt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new de},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new de}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new de}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new de}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new pe(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new pe(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0},uvTransform:{value:new de}},sprite:{diffuse:{value:new pe(16777215)},opacity:{value:1},center:{value:new Wt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new de},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0}}},Ji={basic:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.fog]),vertexShader:he.meshbasic_vert,fragmentShader:he.meshbasic_frag},lambert:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)}}]),vertexShader:he.meshlambert_vert,fragmentShader:he.meshlambert_frag},phong:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)},specular:{value:new pe(1118481)},shininess:{value:30}}]),vertexShader:he.meshphong_vert,fragmentShader:he.meshphong_frag},standard:{uniforms:Xn([Lt.common,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.roughnessmap,Lt.metalnessmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag},toon:{uniforms:Xn([Lt.common,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.gradientmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)}}]),vertexShader:he.meshtoon_vert,fragmentShader:he.meshtoon_frag},matcap:{uniforms:Xn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,{matcap:{value:null}}]),vertexShader:he.meshmatcap_vert,fragmentShader:he.meshmatcap_frag},points:{uniforms:Xn([Lt.points,Lt.fog]),vertexShader:he.points_vert,fragmentShader:he.points_frag},dashed:{uniforms:Xn([Lt.common,Lt.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:he.linedashed_vert,fragmentShader:he.linedashed_frag},depth:{uniforms:Xn([Lt.common,Lt.displacementmap]),vertexShader:he.depth_vert,fragmentShader:he.depth_frag},normal:{uniforms:Xn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,{opacity:{value:1}}]),vertexShader:he.meshnormal_vert,fragmentShader:he.meshnormal_frag},sprite:{uniforms:Xn([Lt.sprite,Lt.fog]),vertexShader:he.sprite_vert,fragmentShader:he.sprite_frag},background:{uniforms:{uvTransform:{value:new de},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:he.background_vert,fragmentShader:he.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new de}},vertexShader:he.backgroundCube_vert,fragmentShader:he.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:he.cube_vert,fragmentShader:he.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:he.equirect_vert,fragmentShader:he.equirect_frag},distanceRGBA:{uniforms:Xn([Lt.common,Lt.displacementmap,{referencePosition:{value:new W},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:he.distanceRGBA_vert,fragmentShader:he.distanceRGBA_frag},shadow:{uniforms:Xn([Lt.lights,Lt.fog,{color:{value:new pe(0)},opacity:{value:1}}]),vertexShader:he.shadow_vert,fragmentShader:he.shadow_frag}};Ji.physical={uniforms:Xn([Ji.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new de},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new de},clearcoatNormalScale:{value:new Wt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new de},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new de},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new de},sheen:{value:0},sheenColor:{value:new pe(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new de},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new de},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new de},transmissionSamplerSize:{value:new Wt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new de},attenuationDistance:{value:0},attenuationColor:{value:new pe(0)},specularColor:{value:new pe(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new de},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new de},anisotropyVector:{value:new Wt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new de}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag};const $u={r:0,b:0,g:0},$s=new Ba,cR=new an;function uR(a,t,n,s,o,c,f){const d=new pe(0);let p=c===!0?0:1,m,v,_=null,x=0,E=null;function M(D){let C=D.isScene===!0?D.background:null;return C&&C.isTexture&&(C=(D.backgroundBlurriness>0?n:t).get(C)),C}function T(D){let C=!1;const V=M(D);V===null?y(d,p):V&&V.isColor&&(y(V,1),C=!0);const L=a.xr.getEnvironmentBlendMode();L==="additive"?s.buffers.color.setClear(0,0,0,1,f):L==="alpha-blend"&&s.buffers.color.setClear(0,0,0,0,f),(a.autoClear||C)&&(s.buffers.depth.setTest(!0),s.buffers.depth.setMask(!0),s.buffers.color.setMask(!0),a.clear(a.autoClearColor,a.autoClearDepth,a.autoClearStencil))}function S(D,C){const V=M(C);V&&(V.isCubeTexture||V.mapping===xf)?(v===void 0&&(v=new Wn(new _c(1,1,1),new Yn({name:"BackgroundCubeMaterial",uniforms:Xo(Ji.backgroundCube.uniforms),vertexShader:Ji.backgroundCube.vertexShader,fragmentShader:Ji.backgroundCube.fragmentShader,side:ii,depthTest:!1,depthWrite:!1,fog:!1})),v.geometry.deleteAttribute("normal"),v.geometry.deleteAttribute("uv"),v.onBeforeRender=function(L,P,G){this.matrixWorld.copyPosition(G.matrixWorld)},Object.defineProperty(v.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),o.update(v)),$s.copy(C.backgroundRotation),$s.x*=-1,$s.y*=-1,$s.z*=-1,V.isCubeTexture&&V.isRenderTargetTexture===!1&&($s.y*=-1,$s.z*=-1),v.material.uniforms.envMap.value=V,v.material.uniforms.flipEnvMap.value=V.isCubeTexture&&V.isRenderTargetTexture===!1?-1:1,v.material.uniforms.backgroundBlurriness.value=C.backgroundBlurriness,v.material.uniforms.backgroundIntensity.value=C.backgroundIntensity,v.material.uniforms.backgroundRotation.value.setFromMatrix4(cR.makeRotationFromEuler($s)),v.material.toneMapped=Pe.getTransfer(V.colorSpace)!==qe,(_!==V||x!==V.version||E!==a.toneMapping)&&(v.material.needsUpdate=!0,_=V,x=V.version,E=a.toneMapping),v.layers.enableAll(),D.unshift(v,v.geometry,v.material,0,0,null)):V&&V.isTexture&&(m===void 0&&(m=new Wn(new Mf(2,2),new Yn({name:"BackgroundMaterial",uniforms:Xo(Ji.background.uniforms),vertexShader:Ji.background.vertexShader,fragmentShader:Ji.background.fragmentShader,side:Rs,depthTest:!1,depthWrite:!1,fog:!1})),m.geometry.deleteAttribute("normal"),Object.defineProperty(m.material,"map",{get:function(){return this.uniforms.t2D.value}}),o.update(m)),m.material.uniforms.t2D.value=V,m.material.uniforms.backgroundIntensity.value=C.backgroundIntensity,m.material.toneMapped=Pe.getTransfer(V.colorSpace)!==qe,V.matrixAutoUpdate===!0&&V.updateMatrix(),m.material.uniforms.uvTransform.value.copy(V.matrix),(_!==V||x!==V.version||E!==a.toneMapping)&&(m.material.needsUpdate=!0,_=V,x=V.version,E=a.toneMapping),m.layers.enableAll(),D.unshift(m,m.geometry,m.material,0,0,null))}function y(D,C){D.getRGB($u,oS(a)),s.buffers.color.setClear($u.r,$u.g,$u.b,C,f)}function I(){v!==void 0&&(v.geometry.dispose(),v.material.dispose()),m!==void 0&&(m.geometry.dispose(),m.material.dispose())}return{getClearColor:function(){return d},setClearColor:function(D,C=1){d.set(D),p=C,y(d,p)},getClearAlpha:function(){return p},setClearAlpha:function(D){p=D,y(d,p)},render:T,addToRenderList:S,dispose:I}}function fR(a,t){const n=a.getParameter(a.MAX_VERTEX_ATTRIBS),s={},o=x(null);let c=o,f=!1;function d(N,H,ut,ot,mt){let ct=!1;const B=_(ot,ut,H);c!==B&&(c=B,m(c.object)),ct=E(N,ot,ut,mt),ct&&M(N,ot,ut,mt),mt!==null&&t.update(mt,a.ELEMENT_ARRAY_BUFFER),(ct||f)&&(f=!1,C(N,H,ut,ot),mt!==null&&a.bindBuffer(a.ELEMENT_ARRAY_BUFFER,t.get(mt).buffer))}function p(){return a.createVertexArray()}function m(N){return a.bindVertexArray(N)}function v(N){return a.deleteVertexArray(N)}function _(N,H,ut){const ot=ut.wireframe===!0;let mt=s[N.id];mt===void 0&&(mt={},s[N.id]=mt);let ct=mt[H.id];ct===void 0&&(ct={},mt[H.id]=ct);let B=ct[ot];return B===void 0&&(B=x(p()),ct[ot]=B),B}function x(N){const H=[],ut=[],ot=[];for(let mt=0;mt<n;mt++)H[mt]=0,ut[mt]=0,ot[mt]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ut,attributeDivisors:ot,object:N,attributes:{},index:null}}function E(N,H,ut,ot){const mt=c.attributes,ct=H.attributes;let B=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){const At=mt[$];let z=ct[$];if(z===void 0&&($==="instanceMatrix"&&N.instanceMatrix&&(z=N.instanceMatrix),$==="instanceColor"&&N.instanceColor&&(z=N.instanceColor)),At===void 0||At.attribute!==z||z&&At.data!==z.data)return!0;B++}return c.attributesNum!==B||c.index!==ot}function M(N,H,ut,ot){const mt={},ct=H.attributes;let B=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){let At=ct[$];At===void 0&&($==="instanceMatrix"&&N.instanceMatrix&&(At=N.instanceMatrix),$==="instanceColor"&&N.instanceColor&&(At=N.instanceColor));const z={};z.attribute=At,At&&At.data&&(z.data=At.data),mt[$]=z,B++}c.attributes=mt,c.attributesNum=B,c.index=ot}function T(){const N=c.newAttributes;for(let H=0,ut=N.length;H<ut;H++)N[H]=0}function S(N){y(N,0)}function y(N,H){const ut=c.newAttributes,ot=c.enabledAttributes,mt=c.attributeDivisors;ut[N]=1,ot[N]===0&&(a.enableVertexAttribArray(N),ot[N]=1),mt[N]!==H&&(a.vertexAttribDivisor(N,H),mt[N]=H)}function I(){const N=c.newAttributes,H=c.enabledAttributes;for(let ut=0,ot=H.length;ut<ot;ut++)H[ut]!==N[ut]&&(a.disableVertexAttribArray(ut),H[ut]=0)}function D(N,H,ut,ot,mt,ct,B){B===!0?a.vertexAttribIPointer(N,H,ut,mt,ct):a.vertexAttribPointer(N,H,ut,ot,mt,ct)}function C(N,H,ut,ot){T();const mt=ot.attributes,ct=ut.getAttributes(),B=H.defaultAttributeValues;for(const Z in ct){const $=ct[Z];if($.location>=0){let Et=mt[Z];if(Et===void 0&&(Z==="instanceMatrix"&&N.instanceMatrix&&(Et=N.instanceMatrix),Z==="instanceColor"&&N.instanceColor&&(Et=N.instanceColor)),Et!==void 0){const At=Et.normalized,z=Et.itemSize,nt=t.get(Et);if(nt===void 0)continue;const St=nt.buffer,q=nt.type,ft=nt.bytesPerElement,Tt=q===a.INT||q===a.UNSIGNED_INT||Et.gpuType===Um;if(Et.isInterleavedBufferAttribute){const Mt=Et.data,Ft=Mt.stride,Vt=Et.offset;if(Mt.isInstancedInterleavedBuffer){for(let oe=0;oe<$.locationSize;oe++)y($.location+oe,Mt.meshPerAttribute);N.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Mt.meshPerAttribute*Mt.count)}else for(let oe=0;oe<$.locationSize;oe++)S($.location+oe);a.bindBuffer(a.ARRAY_BUFFER,St);for(let oe=0;oe<$.locationSize;oe++)D($.location+oe,z/$.locationSize,q,At,Ft*ft,(Vt+z/$.locationSize*oe)*ft,Tt)}else{if(Et.isInstancedBufferAttribute){for(let Mt=0;Mt<$.locationSize;Mt++)y($.location+Mt,Et.meshPerAttribute);N.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Et.meshPerAttribute*Et.count)}else for(let Mt=0;Mt<$.locationSize;Mt++)S($.location+Mt);a.bindBuffer(a.ARRAY_BUFFER,St);for(let Mt=0;Mt<$.locationSize;Mt++)D($.location+Mt,z/$.locationSize,q,At,z*ft,z/$.locationSize*Mt*ft,Tt)}}else if(B!==void 0){const At=B[Z];if(At!==void 0)switch(At.length){case 2:a.vertexAttrib2fv($.location,At);break;case 3:a.vertexAttrib3fv($.location,At);break;case 4:a.vertexAttrib4fv($.location,At);break;default:a.vertexAttrib1fv($.location,At)}}}}I()}function V(){G();for(const N in s){const H=s[N];for(const ut in H){const ot=H[ut];for(const mt in ot)v(ot[mt].object),delete ot[mt];delete H[ut]}delete s[N]}}function L(N){if(s[N.id]===void 0)return;const H=s[N.id];for(const ut in H){const ot=H[ut];for(const mt in ot)v(ot[mt].object),delete ot[mt];delete H[ut]}delete s[N.id]}function P(N){for(const H in s){const ut=s[H];if(ut[N.id]===void 0)continue;const ot=ut[N.id];for(const mt in ot)v(ot[mt].object),delete ot[mt];delete ut[N.id]}}function G(){U(),f=!0,c!==o&&(c=o,m(c.object))}function U(){o.geometry=null,o.program=null,o.wireframe=!1}return{setup:d,reset:G,resetDefaultState:U,dispose:V,releaseStatesOfGeometry:L,releaseStatesOfProgram:P,initAttributes:T,enableAttribute:S,disableUnusedAttributes:I}}function dR(a,t,n){let s;function o(m){s=m}function c(m,v){a.drawArrays(s,m,v),n.update(v,s,1)}function f(m,v,_){_!==0&&(a.drawArraysInstanced(s,m,v,_),n.update(v,s,_))}function d(m,v,_){if(_===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(s,m,0,v,0,_);let E=0;for(let M=0;M<_;M++)E+=v[M];n.update(E,s,1)}function p(m,v,_,x){if(_===0)return;const E=t.get("WEBGL_multi_draw");if(E===null)for(let M=0;M<m.length;M++)f(m[M],v[M],x[M]);else{E.multiDrawArraysInstancedWEBGL(s,m,0,v,0,x,0,_);let M=0;for(let T=0;T<_;T++)M+=v[T]*x[T];n.update(M,s,1)}}this.setMode=o,this.render=c,this.renderInstances=f,this.renderMultiDraw=d,this.renderMultiDrawInstances=p}function hR(a,t,n,s){let o;function c(){if(o!==void 0)return o;if(t.has("EXT_texture_filter_anisotropic")===!0){const P=t.get("EXT_texture_filter_anisotropic");o=a.getParameter(P.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else o=0;return o}function f(P){return!(P!==Fi&&s.convert(P)!==a.getParameter(a.IMPLEMENTATION_COLOR_READ_FORMAT))}function d(P){const G=P===Pa&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(P!==Ia&&s.convert(P)!==a.getParameter(a.IMPLEMENTATION_COLOR_READ_TYPE)&&P!==Da&&!G)}function p(P){if(P==="highp"){if(a.getShaderPrecisionFormat(a.VERTEX_SHADER,a.HIGH_FLOAT).precision>0&&a.getShaderPrecisionFormat(a.FRAGMENT_SHADER,a.HIGH_FLOAT).precision>0)return"highp";P="mediump"}return P==="mediump"&&a.getShaderPrecisionFormat(a.VERTEX_SHADER,a.MEDIUM_FLOAT).precision>0&&a.getShaderPrecisionFormat(a.FRAGMENT_SHADER,a.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let m=n.precision!==void 0?n.precision:"highp";const v=p(m);v!==m&&(console.warn("THREE.WebGLRenderer:",m,"not supported, using",v,"instead."),m=v);const _=n.logarithmicDepthBuffer===!0,x=n.reverseDepthBuffer===!0&&t.has("EXT_clip_control"),E=a.getParameter(a.MAX_TEXTURE_IMAGE_UNITS),M=a.getParameter(a.MAX_VERTEX_TEXTURE_IMAGE_UNITS),T=a.getParameter(a.MAX_TEXTURE_SIZE),S=a.getParameter(a.MAX_CUBE_MAP_TEXTURE_SIZE),y=a.getParameter(a.MAX_VERTEX_ATTRIBS),I=a.getParameter(a.MAX_VERTEX_UNIFORM_VECTORS),D=a.getParameter(a.MAX_VARYING_VECTORS),C=a.getParameter(a.MAX_FRAGMENT_UNIFORM_VECTORS),V=M>0,L=a.getParameter(a.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:c,getMaxPrecision:p,textureFormatReadable:f,textureTypeReadable:d,precision:m,logarithmicDepthBuffer:_,reverseDepthBuffer:x,maxTextures:E,maxVertexTextures:M,maxTextureSize:T,maxCubemapSize:S,maxAttributes:y,maxVertexUniforms:I,maxVaryings:D,maxFragmentUniforms:C,vertexTextures:V,maxSamples:L}}function pR(a){const t=this;let n=null,s=0,o=!1,c=!1;const f=new nr,d=new de,p={value:null,needsUpdate:!1};this.uniform=p,this.numPlanes=0,this.numIntersection=0,this.init=function(_,x){const E=_.length!==0||x||s!==0||o;return o=x,s=_.length,E},this.beginShadows=function(){c=!0,v(null)},this.endShadows=function(){c=!1},this.setGlobalState=function(_,x){n=v(_,x,0)},this.setState=function(_,x,E){const M=_.clippingPlanes,T=_.clipIntersection,S=_.clipShadows,y=a.get(_);if(!o||M===null||M.length===0||c&&!S)c?v(null):m();else{const I=c?0:s,D=I*4;let C=y.clippingState||null;p.value=C,C=v(M,x,D,E);for(let V=0;V!==D;++V)C[V]=n[V];y.clippingState=C,this.numIntersection=T?this.numPlanes:0,this.numPlanes+=I}};function m(){p.value!==n&&(p.value=n,p.needsUpdate=s>0),t.numPlanes=s,t.numIntersection=0}function v(_,x,E,M){const T=_!==null?_.length:0;let S=null;if(T!==0){if(S=p.value,M!==!0||S===null){const y=E+T*4,I=x.matrixWorldInverse;d.getNormalMatrix(I),(S===null||S.length<y)&&(S=new Float32Array(y));for(let D=0,C=E;D!==T;++D,C+=4)f.copy(_[D]).applyMatrix4(I,d),f.normal.toArray(S,C),S[C+3]=f.constant}p.value=S,p.needsUpdate=!0}return t.numPlanes=T,t.numIntersection=0,S}}function mR(a){let t=new WeakMap;function n(f,d){return d===jp?f.mapping=Ho:d===kp&&(f.mapping=Go),f}function s(f){if(f&&f.isTexture){const d=f.mapping;if(d===jp||d===kp)if(t.has(f)){const p=t.get(f).texture;return n(p,f.mapping)}else{const p=f.image;if(p&&p.height>0){const m=new nA(p.height);return m.fromEquirectangularTexture(a,f),t.set(f,m),f.addEventListener("dispose",o),n(m.texture,f.mapping)}else return null}}return f}function o(f){const d=f.target;d.removeEventListener("dispose",o);const p=t.get(d);p!==void 0&&(t.delete(d),p.dispose())}function c(){t=new WeakMap}return{get:s,dispose:c}}const Mo=4,Ry=[.125,.215,.35,.446,.526,.582],rr=20,fp=new mS,wy=new pe;let dp=null,hp=0,pp=0,mp=!1;const ir=(1+Math.sqrt(5))/2,vo=1/ir,Ny=[new W(-ir,vo,0),new W(ir,vo,0),new W(-vo,0,ir),new W(vo,0,ir),new W(0,ir,-vo),new W(0,ir,vo),new W(-1,1,-1),new W(1,1,-1),new W(-1,1,1),new W(1,1,1)];class Dy{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(t,n=0,s=.1,o=100){dp=this._renderer.getRenderTarget(),hp=this._renderer.getActiveCubeFace(),pp=this._renderer.getActiveMipmapLevel(),mp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const c=this._allocateTargets();return c.depthBuffer=!0,this._sceneToCubeUV(t,s,o,c),n>0&&this._blur(c,0,0,n),this._applyPMREM(c),this._cleanup(c),c}fromEquirectangular(t,n=null){return this._fromTexture(t,n)}fromCubemap(t,n=null){return this._fromTexture(t,n)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Oy(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Ly(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodPlanes.length;t++)this._lodPlanes[t].dispose()}_cleanup(t){this._renderer.setRenderTarget(dp,hp,pp),this._renderer.xr.enabled=mp,t.scissorTest=!1,tf(t,0,0,t.width,t.height)}_fromTexture(t,n){t.mapping===Ho||t.mapping===Go?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),dp=this._renderer.getRenderTarget(),hp=this._renderer.getActiveCubeFace(),pp=this._renderer.getActiveMipmapLevel(),mp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const s=n||this._allocateTargets();return this._textureToCubeUV(t,s),this._applyPMREM(s),this._cleanup(s),s}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),n=4*this._cubeSize,s={magFilter:$i,minFilter:$i,generateMipmaps:!1,type:Pa,format:Fi,colorSpace:ko,depthBuffer:!1},o=Uy(t,n,s);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==n){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Uy(t,n,s);const{_lodMax:c}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=gR(c)),this._blurMaterial=vR(c,t,n)}return o}_compileMaterial(t){const n=new Wn(this._lodPlanes[0],t);this._renderer.compile(n,fp)}_sceneToCubeUV(t,n,s,o){const d=new _i(90,1,n,s),p=[1,-1,1,1,1,1],m=[1,1,1,-1,-1,-1],v=this._renderer,_=v.autoClear,x=v.toneMapping;v.getClearColor(wy),v.toneMapping=Cs,v.autoClear=!1;const E=new Sr({name:"PMREM.Background",side:ii,depthWrite:!1,depthTest:!1}),M=new Wn(new _c,E);let T=!1;const S=t.background;S?S.isColor&&(E.color.copy(S),t.background=null,T=!0):(E.color.copy(wy),T=!0);for(let y=0;y<6;y++){const I=y%3;I===0?(d.up.set(0,p[y],0),d.lookAt(m[y],0,0)):I===1?(d.up.set(0,0,p[y]),d.lookAt(0,m[y],0)):(d.up.set(0,p[y],0),d.lookAt(0,0,m[y]));const D=this._cubeSize;tf(o,I*D,y>2?D:0,D,D),v.setRenderTarget(o),T&&v.render(M,d),v.render(t,d)}M.geometry.dispose(),M.material.dispose(),v.toneMapping=x,v.autoClear=_,t.background=S}_textureToCubeUV(t,n){const s=this._renderer,o=t.mapping===Ho||t.mapping===Go;o?(this._cubemapMaterial===null&&(this._cubemapMaterial=Oy()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Ly());const c=o?this._cubemapMaterial:this._equirectMaterial,f=new Wn(this._lodPlanes[0],c),d=c.uniforms;d.envMap.value=t;const p=this._cubeSize;tf(n,0,0,3*p,2*p),s.setRenderTarget(n),s.render(f,fp)}_applyPMREM(t){const n=this._renderer,s=n.autoClear;n.autoClear=!1;const o=this._lodPlanes.length;for(let c=1;c<o;c++){const f=Math.sqrt(this._sigmas[c]*this._sigmas[c]-this._sigmas[c-1]*this._sigmas[c-1]),d=Ny[(o-c-1)%Ny.length];this._blur(t,c-1,c,f,d)}n.autoClear=s}_blur(t,n,s,o,c){const f=this._pingPongRenderTarget;this._halfBlur(t,f,n,s,o,"latitudinal",c),this._halfBlur(f,t,s,s,o,"longitudinal",c)}_halfBlur(t,n,s,o,c,f,d){const p=this._renderer,m=this._blurMaterial;f!=="latitudinal"&&f!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const v=3,_=new Wn(this._lodPlanes[o],m),x=m.uniforms,E=this._sizeLods[s]-1,M=isFinite(c)?Math.PI/(2*E):2*Math.PI/(2*rr-1),T=c/M,S=isFinite(c)?1+Math.floor(v*T):rr;S>rr&&console.warn(`sigmaRadians, ${c}, is too large and will clip, as it requested ${S} samples when the maximum is set to ${rr}`);const y=[];let I=0;for(let P=0;P<rr;++P){const G=P/T,U=Math.exp(-G*G/2);y.push(U),P===0?I+=U:P<S&&(I+=2*U)}for(let P=0;P<y.length;P++)y[P]=y[P]/I;x.envMap.value=t.texture,x.samples.value=S,x.weights.value=y,x.latitudinal.value=f==="latitudinal",d&&(x.poleAxis.value=d);const{_lodMax:D}=this;x.dTheta.value=M,x.mipInt.value=D-s;const C=this._sizeLods[o],V=3*C*(o>D-Mo?o-D+Mo:0),L=4*(this._cubeSize-C);tf(n,V,L,3*C,2*C),p.setRenderTarget(n),p.render(_,fp)}}function gR(a){const t=[],n=[],s=[];let o=a;const c=a-Mo+1+Ry.length;for(let f=0;f<c;f++){const d=Math.pow(2,o);n.push(d);let p=1/d;f>a-Mo?p=Ry[f-a+Mo-1]:f===0&&(p=0),s.push(p);const m=1/(d-2),v=-m,_=1+m,x=[v,v,_,v,_,_,v,v,_,_,v,_],E=6,M=6,T=3,S=2,y=1,I=new Float32Array(T*M*E),D=new Float32Array(S*M*E),C=new Float32Array(y*M*E);for(let L=0;L<E;L++){const P=L%3*2/3-1,G=L>2?0:-1,U=[P,G,0,P+2/3,G,0,P+2/3,G+1,0,P,G,0,P+2/3,G+1,0,P,G+1,0];I.set(U,T*M*L),D.set(x,S*M*L);const N=[L,L,L,L,L,L];C.set(N,y*M*L)}const V=new Vi;V.setAttribute("position",new ea(I,T)),V.setAttribute("uv",new ea(D,S)),V.setAttribute("faceIndex",new ea(C,y)),t.push(V),o>Mo&&o--}return{lodPlanes:t,sizeLods:n,sigmas:s}}function Uy(a,t,n){const s=new Gi(a,t,n);return s.texture.mapping=xf,s.texture.name="PMREM.cubeUv",s.scissorTest=!0,s}function tf(a,t,n,s,o){a.viewport.set(t,n,s,o),a.scissor.set(t,n,s,o)}function vR(a,t,n){const s=new Float32Array(rr),o=new W(0,1,0);return new Yn({name:"SphericalGaussianBlur",defines:{n:rr,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${a}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:s},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:o}},vertexShader:jm(),fragmentShader:`

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
		`,blending:Oa,depthTest:!1,depthWrite:!1})}function Ly(){return new Yn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:jm(),fragmentShader:`

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
		`,blending:Oa,depthTest:!1,depthWrite:!1})}function Oy(){return new Yn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:jm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Oa,depthTest:!1,depthWrite:!1})}function jm(){return`

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
	`}function _R(a){let t=new WeakMap,n=null;function s(d){if(d&&d.isTexture){const p=d.mapping,m=p===jp||p===kp,v=p===Ho||p===Go;if(m||v){let _=t.get(d);const x=_!==void 0?_.texture.pmremVersion:0;if(d.isRenderTargetTexture&&d.pmremVersion!==x)return n===null&&(n=new Dy(a)),_=m?n.fromEquirectangular(d,_):n.fromCubemap(d,_),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),_.texture;if(_!==void 0)return _.texture;{const E=d.image;return m&&E&&E.height>0||v&&E&&o(E)?(n===null&&(n=new Dy(a)),_=m?n.fromEquirectangular(d):n.fromCubemap(d),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),d.addEventListener("dispose",c),_.texture):null}}}return d}function o(d){let p=0;const m=6;for(let v=0;v<m;v++)d[v]!==void 0&&p++;return p===m}function c(d){const p=d.target;p.removeEventListener("dispose",c);const m=t.get(p);m!==void 0&&(t.delete(p),m.dispose())}function f(){t=new WeakMap,n!==null&&(n.dispose(),n=null)}return{get:s,dispose:f}}function yR(a){const t={};function n(s){if(t[s]!==void 0)return t[s];let o;switch(s){case"WEBGL_depth_texture":o=a.getExtension("WEBGL_depth_texture")||a.getExtension("MOZ_WEBGL_depth_texture")||a.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":o=a.getExtension("EXT_texture_filter_anisotropic")||a.getExtension("MOZ_EXT_texture_filter_anisotropic")||a.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":o=a.getExtension("WEBGL_compressed_texture_s3tc")||a.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||a.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":o=a.getExtension("WEBGL_compressed_texture_pvrtc")||a.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:o=a.getExtension(s)}return t[s]=o,o}return{has:function(s){return n(s)!==null},init:function(){n("EXT_color_buffer_float"),n("WEBGL_clip_cull_distance"),n("OES_texture_float_linear"),n("EXT_color_buffer_half_float"),n("WEBGL_multisampled_render_to_texture"),n("WEBGL_render_shared_exponent")},get:function(s){const o=n(s);return o===null&&xo("THREE.WebGLRenderer: "+s+" extension not supported."),o}}}function xR(a,t,n,s){const o={},c=new WeakMap;function f(_){const x=_.target;x.index!==null&&t.remove(x.index);for(const M in x.attributes)t.remove(x.attributes[M]);x.removeEventListener("dispose",f),delete o[x.id];const E=c.get(x);E&&(t.remove(E),c.delete(x)),s.releaseStatesOfGeometry(x),x.isInstancedBufferGeometry===!0&&delete x._maxInstanceCount,n.memory.geometries--}function d(_,x){return o[x.id]===!0||(x.addEventListener("dispose",f),o[x.id]=!0,n.memory.geometries++),x}function p(_){const x=_.attributes;for(const E in x)t.update(x[E],a.ARRAY_BUFFER)}function m(_){const x=[],E=_.index,M=_.attributes.position;let T=0;if(E!==null){const I=E.array;T=E.version;for(let D=0,C=I.length;D<C;D+=3){const V=I[D+0],L=I[D+1],P=I[D+2];x.push(V,L,L,P,P,V)}}else if(M!==void 0){const I=M.array;T=M.version;for(let D=0,C=I.length/3-1;D<C;D+=3){const V=D+0,L=D+1,P=D+2;x.push(V,L,L,P,P,V)}}else return;const S=new(tS(x)?rS:sS)(x,1);S.version=T;const y=c.get(_);y&&t.remove(y),c.set(_,S)}function v(_){const x=c.get(_);if(x){const E=_.index;E!==null&&x.version<E.version&&m(_)}else m(_);return c.get(_)}return{get:d,update:p,getWireframeAttribute:v}}function SR(a,t,n){let s;function o(x){s=x}let c,f;function d(x){c=x.type,f=x.bytesPerElement}function p(x,E){a.drawElements(s,E,c,x*f),n.update(E,s,1)}function m(x,E,M){M!==0&&(a.drawElementsInstanced(s,E,c,x*f,M),n.update(E,s,M))}function v(x,E,M){if(M===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(s,E,0,c,x,0,M);let S=0;for(let y=0;y<M;y++)S+=E[y];n.update(S,s,1)}function _(x,E,M,T){if(M===0)return;const S=t.get("WEBGL_multi_draw");if(S===null)for(let y=0;y<x.length;y++)m(x[y]/f,E[y],T[y]);else{S.multiDrawElementsInstancedWEBGL(s,E,0,c,x,0,T,0,M);let y=0;for(let I=0;I<M;I++)y+=E[I]*T[I];n.update(y,s,1)}}this.setMode=o,this.setIndex=d,this.render=p,this.renderInstances=m,this.renderMultiDraw=v,this.renderMultiDrawInstances=_}function MR(a){const t={geometries:0,textures:0},n={frame:0,calls:0,triangles:0,points:0,lines:0};function s(c,f,d){switch(n.calls++,f){case a.TRIANGLES:n.triangles+=d*(c/3);break;case a.LINES:n.lines+=d*(c/2);break;case a.LINE_STRIP:n.lines+=d*(c-1);break;case a.LINE_LOOP:n.lines+=d*c;break;case a.POINTS:n.points+=d*c;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",f);break}}function o(){n.calls=0,n.triangles=0,n.points=0,n.lines=0}return{memory:t,render:n,programs:null,autoReset:!0,reset:o,update:s}}function ER(a,t,n){const s=new WeakMap,o=new We;function c(f,d,p){const m=f.morphTargetInfluences,v=d.morphAttributes.position||d.morphAttributes.normal||d.morphAttributes.color,_=v!==void 0?v.length:0;let x=s.get(d);if(x===void 0||x.count!==_){let N=function(){G.dispose(),s.delete(d),d.removeEventListener("dispose",N)};var E=N;x!==void 0&&x.texture.dispose();const M=d.morphAttributes.position!==void 0,T=d.morphAttributes.normal!==void 0,S=d.morphAttributes.color!==void 0,y=d.morphAttributes.position||[],I=d.morphAttributes.normal||[],D=d.morphAttributes.color||[];let C=0;M===!0&&(C=1),T===!0&&(C=2),S===!0&&(C=3);let V=d.attributes.position.count*C,L=1;V>t.maxTextureSize&&(L=Math.ceil(V/t.maxTextureSize),V=t.maxTextureSize);const P=new Float32Array(V*L*4*_),G=new nS(P,V,L,_);G.type=Da,G.needsUpdate=!0;const U=C*4;for(let H=0;H<_;H++){const ut=y[H],ot=I[H],mt=D[H],ct=V*L*4*H;for(let B=0;B<ut.count;B++){const Z=B*U;M===!0&&(o.fromBufferAttribute(ut,B),P[ct+Z+0]=o.x,P[ct+Z+1]=o.y,P[ct+Z+2]=o.z,P[ct+Z+3]=0),T===!0&&(o.fromBufferAttribute(ot,B),P[ct+Z+4]=o.x,P[ct+Z+5]=o.y,P[ct+Z+6]=o.z,P[ct+Z+7]=0),S===!0&&(o.fromBufferAttribute(mt,B),P[ct+Z+8]=o.x,P[ct+Z+9]=o.y,P[ct+Z+10]=o.z,P[ct+Z+11]=mt.itemSize===4?o.w:1)}}x={count:_,texture:G,size:new Wt(V,L)},s.set(d,x),d.addEventListener("dispose",N)}if(f.isInstancedMesh===!0&&f.morphTexture!==null)p.getUniforms().setValue(a,"morphTexture",f.morphTexture,n);else{let M=0;for(let S=0;S<m.length;S++)M+=m[S];const T=d.morphTargetsRelative?1:1-M;p.getUniforms().setValue(a,"morphTargetBaseInfluence",T),p.getUniforms().setValue(a,"morphTargetInfluences",m)}p.getUniforms().setValue(a,"morphTargetsTexture",x.texture,n),p.getUniforms().setValue(a,"morphTargetsTextureSize",x.size)}return{update:c}}function bR(a,t,n,s){let o=new WeakMap;function c(p){const m=s.render.frame,v=p.geometry,_=t.get(p,v);if(o.get(_)!==m&&(t.update(_),o.set(_,m)),p.isInstancedMesh&&(p.hasEventListener("dispose",d)===!1&&p.addEventListener("dispose",d),o.get(p)!==m&&(n.update(p.instanceMatrix,a.ARRAY_BUFFER),p.instanceColor!==null&&n.update(p.instanceColor,a.ARRAY_BUFFER),o.set(p,m))),p.isSkinnedMesh){const x=p.skeleton;o.get(x)!==m&&(x.update(),o.set(x,m))}return _}function f(){o=new WeakMap}function d(p){const m=p.target;m.removeEventListener("dispose",d),n.remove(m.instanceMatrix),m.instanceColor!==null&&n.remove(m.instanceColor)}return{update:c,dispose:f}}const _S=new ai,Py=new uS(1,1),yS=new nS,xS=new HT,SS=new cS,zy=[],Iy=[],By=new Float32Array(16),Fy=new Float32Array(9),Hy=new Float32Array(4);function Qo(a,t,n){const s=a[0];if(s<=0||s>0)return a;const o=t*n;let c=zy[o];if(c===void 0&&(c=new Float32Array(o),zy[o]=c),t!==0){s.toArray(c,0);for(let f=1,d=0;f!==t;++f)d+=n,a[f].toArray(c,d)}return c}function Sn(a,t){if(a.length!==t.length)return!1;for(let n=0,s=a.length;n<s;n++)if(a[n]!==t[n])return!1;return!0}function Mn(a,t){for(let n=0,s=t.length;n<s;n++)a[n]=t[n]}function bf(a,t){let n=Iy[t];n===void 0&&(n=new Int32Array(t),Iy[t]=n);for(let s=0;s!==t;++s)n[s]=a.allocateTextureUnit();return n}function TR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1f(this.addr,t),n[0]=t)}function AR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2f(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2fv(this.addr,t),Mn(n,t)}}function CR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3f(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else if(t.r!==void 0)(n[0]!==t.r||n[1]!==t.g||n[2]!==t.b)&&(a.uniform3f(this.addr,t.r,t.g,t.b),n[0]=t.r,n[1]=t.g,n[2]=t.b);else{if(Sn(n,t))return;a.uniform3fv(this.addr,t),Mn(n,t)}}function RR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4f(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4fv(this.addr,t),Mn(n,t)}}function wR(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix2fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;Hy.set(s),a.uniformMatrix2fv(this.addr,!1,Hy),Mn(n,s)}}function NR(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix3fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;Fy.set(s),a.uniformMatrix3fv(this.addr,!1,Fy),Mn(n,s)}}function DR(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix4fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;By.set(s),a.uniformMatrix4fv(this.addr,!1,By),Mn(n,s)}}function UR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1i(this.addr,t),n[0]=t)}function LR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2i(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2iv(this.addr,t),Mn(n,t)}}function OR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3i(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;a.uniform3iv(this.addr,t),Mn(n,t)}}function PR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4i(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4iv(this.addr,t),Mn(n,t)}}function zR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1ui(this.addr,t),n[0]=t)}function IR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2ui(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2uiv(this.addr,t),Mn(n,t)}}function BR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3ui(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;a.uniform3uiv(this.addr,t),Mn(n,t)}}function FR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4ui(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4uiv(this.addr,t),Mn(n,t)}}function HR(a,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(a.uniform1i(this.addr,o),s[0]=o);let c;this.type===a.SAMPLER_2D_SHADOW?(Py.compareFunction=$x,c=Py):c=_S,n.setTexture2D(t||c,o)}function GR(a,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(a.uniform1i(this.addr,o),s[0]=o),n.setTexture3D(t||xS,o)}function VR(a,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(a.uniform1i(this.addr,o),s[0]=o),n.setTextureCube(t||SS,o)}function jR(a,t,n){const s=this.cache,o=n.allocateTextureUnit();s[0]!==o&&(a.uniform1i(this.addr,o),s[0]=o),n.setTexture2DArray(t||yS,o)}function kR(a){switch(a){case 5126:return TR;case 35664:return AR;case 35665:return CR;case 35666:return RR;case 35674:return wR;case 35675:return NR;case 35676:return DR;case 5124:case 35670:return UR;case 35667:case 35671:return LR;case 35668:case 35672:return OR;case 35669:case 35673:return PR;case 5125:return zR;case 36294:return IR;case 36295:return BR;case 36296:return FR;case 35678:case 36198:case 36298:case 36306:case 35682:return HR;case 35679:case 36299:case 36307:return GR;case 35680:case 36300:case 36308:case 36293:return VR;case 36289:case 36303:case 36311:case 36292:return jR}}function XR(a,t){a.uniform1fv(this.addr,t)}function qR(a,t){const n=Qo(t,this.size,2);a.uniform2fv(this.addr,n)}function WR(a,t){const n=Qo(t,this.size,3);a.uniform3fv(this.addr,n)}function YR(a,t){const n=Qo(t,this.size,4);a.uniform4fv(this.addr,n)}function QR(a,t){const n=Qo(t,this.size,4);a.uniformMatrix2fv(this.addr,!1,n)}function ZR(a,t){const n=Qo(t,this.size,9);a.uniformMatrix3fv(this.addr,!1,n)}function KR(a,t){const n=Qo(t,this.size,16);a.uniformMatrix4fv(this.addr,!1,n)}function JR(a,t){a.uniform1iv(this.addr,t)}function $R(a,t){a.uniform2iv(this.addr,t)}function tw(a,t){a.uniform3iv(this.addr,t)}function ew(a,t){a.uniform4iv(this.addr,t)}function nw(a,t){a.uniform1uiv(this.addr,t)}function iw(a,t){a.uniform2uiv(this.addr,t)}function aw(a,t){a.uniform3uiv(this.addr,t)}function sw(a,t){a.uniform4uiv(this.addr,t)}function rw(a,t,n){const s=this.cache,o=t.length,c=bf(n,o);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==o;++f)n.setTexture2D(t[f]||_S,c[f])}function ow(a,t,n){const s=this.cache,o=t.length,c=bf(n,o);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==o;++f)n.setTexture3D(t[f]||xS,c[f])}function lw(a,t,n){const s=this.cache,o=t.length,c=bf(n,o);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==o;++f)n.setTextureCube(t[f]||SS,c[f])}function cw(a,t,n){const s=this.cache,o=t.length,c=bf(n,o);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==o;++f)n.setTexture2DArray(t[f]||yS,c[f])}function uw(a){switch(a){case 5126:return XR;case 35664:return qR;case 35665:return WR;case 35666:return YR;case 35674:return QR;case 35675:return ZR;case 35676:return KR;case 5124:case 35670:return JR;case 35667:case 35671:return $R;case 35668:case 35672:return tw;case 35669:case 35673:return ew;case 5125:return nw;case 36294:return iw;case 36295:return aw;case 36296:return sw;case 35678:case 36198:case 36298:case 36306:case 35682:return rw;case 35679:case 36299:case 36307:return ow;case 35680:case 36300:case 36308:case 36293:return lw;case 36289:case 36303:case 36311:case 36292:return cw}}class fw{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.setValue=kR(n.type)}}class dw{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.size=n.size,this.setValue=uw(n.type)}}class hw{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,n,s){const o=this.seq;for(let c=0,f=o.length;c!==f;++c){const d=o[c];d.setValue(t,n[d.id],s)}}}const gp=/(\w+)(\])?(\[|\.)?/g;function Gy(a,t){a.seq.push(t),a.map[t.id]=t}function pw(a,t,n){const s=a.name,o=s.length;for(gp.lastIndex=0;;){const c=gp.exec(s),f=gp.lastIndex;let d=c[1];const p=c[2]==="]",m=c[3];if(p&&(d=d|0),m===void 0||m==="["&&f+2===o){Gy(n,m===void 0?new fw(d,a,t):new dw(d,a,t));break}else{let _=n.map[d];_===void 0&&(_=new hw(d),Gy(n,_)),n=_}}}class uf{constructor(t,n){this.seq=[],this.map={};const s=t.getProgramParameter(n,t.ACTIVE_UNIFORMS);for(let o=0;o<s;++o){const c=t.getActiveUniform(n,o),f=t.getUniformLocation(n,c.name);pw(c,f,this)}}setValue(t,n,s,o){const c=this.map[n];c!==void 0&&c.setValue(t,s,o)}setOptional(t,n,s){const o=n[s];o!==void 0&&this.setValue(t,s,o)}static upload(t,n,s,o){for(let c=0,f=n.length;c!==f;++c){const d=n[c],p=s[d.id];p.needsUpdate!==!1&&d.setValue(t,p.value,o)}}static seqWithValue(t,n){const s=[];for(let o=0,c=t.length;o!==c;++o){const f=t[o];f.id in n&&s.push(f)}return s}}function Vy(a,t,n){const s=a.createShader(t);return a.shaderSource(s,n),a.compileShader(s),s}const mw=37297;let gw=0;function vw(a,t){const n=a.split(`
`),s=[],o=Math.max(t-6,0),c=Math.min(t+6,n.length);for(let f=o;f<c;f++){const d=f+1;s.push(`${d===t?">":" "} ${d}: ${n[f]}`)}return s.join(`
`)}const jy=new de;function _w(a){Pe._getMatrix(jy,Pe.workingColorSpace,a);const t=`mat3( ${jy.elements.map(n=>n.toFixed(4))} )`;switch(Pe.getTransfer(a)){case mf:return[t,"LinearTransferOETF"];case qe:return[t,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",a),[t,"LinearTransferOETF"]}}function ky(a,t,n){const s=a.getShaderParameter(t,a.COMPILE_STATUS),o=a.getShaderInfoLog(t).trim();if(s&&o==="")return"";const c=/ERROR: 0:(\d+)/.exec(o);if(c){const f=parseInt(c[1]);return n.toUpperCase()+`

`+o+`

`+vw(a.getShaderSource(t),f)}else return o}function yw(a,t){const n=_w(t);return[`vec4 ${a}( vec4 value ) {`,`	return ${n[1]}( vec4( value.rgb * ${n[0]}, value.a ) );`,"}"].join(`
`)}function xw(a,t){let n;switch(t){case Zb:n="Linear";break;case Kb:n="Reinhard";break;case Jb:n="Cineon";break;case $b:n="ACESFilmic";break;case eT:n="AgX";break;case nT:n="Neutral";break;case tT:n="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",t),n="Linear"}return"vec3 "+a+"( vec3 color ) { return "+n+"ToneMapping( color ); }"}const ef=new W;function Sw(){Pe.getLuminanceCoefficients(ef);const a=ef.x.toFixed(4),t=ef.y.toFixed(4),n=ef.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${a}, ${t}, ${n} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Mw(a){return[a.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",a.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Kl).join(`
`)}function Ew(a){const t=[];for(const n in a){const s=a[n];s!==!1&&t.push("#define "+n+" "+s)}return t.join(`
`)}function bw(a,t){const n={},s=a.getProgramParameter(t,a.ACTIVE_ATTRIBUTES);for(let o=0;o<s;o++){const c=a.getActiveAttrib(t,o),f=c.name;let d=1;c.type===a.FLOAT_MAT2&&(d=2),c.type===a.FLOAT_MAT3&&(d=3),c.type===a.FLOAT_MAT4&&(d=4),n[f]={type:c.type,location:a.getAttribLocation(t,f),locationSize:d}}return n}function Kl(a){return a!==""}function Xy(a,t){const n=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return a.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,n).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function qy(a,t){return a.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const Tw=/^[ \t]*#include +<([\w\d./]+)>/gm;function ym(a){return a.replace(Tw,Cw)}const Aw=new Map;function Cw(a,t){let n=he[t];if(n===void 0){const s=Aw.get(t);if(s!==void 0)n=he[s],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,s);else throw new Error("Can not resolve #include <"+t+">")}return ym(n)}const Rw=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Wy(a){return a.replace(Rw,ww)}function ww(a,t,n,s){let o="";for(let c=parseInt(t);c<parseInt(n);c++)o+=s.replace(/\[\s*i\s*\]/g,"[ "+c+" ]").replace(/UNROLLED_LOOP_INDEX/g,c);return o}function Yy(a){let t=`precision ${a.precision} float;
	precision ${a.precision} int;
	precision ${a.precision} sampler2D;
	precision ${a.precision} samplerCube;
	precision ${a.precision} sampler3D;
	precision ${a.precision} sampler2DArray;
	precision ${a.precision} sampler2DShadow;
	precision ${a.precision} samplerCubeShadow;
	precision ${a.precision} sampler2DArrayShadow;
	precision ${a.precision} isampler2D;
	precision ${a.precision} isampler3D;
	precision ${a.precision} isamplerCube;
	precision ${a.precision} isampler2DArray;
	precision ${a.precision} usampler2D;
	precision ${a.precision} usampler3D;
	precision ${a.precision} usamplerCube;
	precision ${a.precision} usampler2DArray;
	`;return a.precision==="highp"?t+=`
#define HIGH_PRECISION`:a.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:a.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}function Nw(a){let t="SHADOWMAP_TYPE_BASIC";return a.shadowMapType===Hx?t="SHADOWMAP_TYPE_PCF":a.shadowMapType===wb?t="SHADOWMAP_TYPE_PCF_SOFT":a.shadowMapType===Ca&&(t="SHADOWMAP_TYPE_VSM"),t}function Dw(a){let t="ENVMAP_TYPE_CUBE";if(a.envMap)switch(a.envMapMode){case Ho:case Go:t="ENVMAP_TYPE_CUBE";break;case xf:t="ENVMAP_TYPE_CUBE_UV";break}return t}function Uw(a){let t="ENVMAP_MODE_REFLECTION";if(a.envMap)switch(a.envMapMode){case Go:t="ENVMAP_MODE_REFRACTION";break}return t}function Lw(a){let t="ENVMAP_BLENDING_NONE";if(a.envMap)switch(a.combine){case Gx:t="ENVMAP_BLENDING_MULTIPLY";break;case Yb:t="ENVMAP_BLENDING_MIX";break;case Qb:t="ENVMAP_BLENDING_ADD";break}return t}function Ow(a){const t=a.envMapCubeUVHeight;if(t===null)return null;const n=Math.log2(t)-2,s=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,n),112)),texelHeight:s,maxMip:n}}function Pw(a,t,n,s){const o=a.getContext(),c=n.defines;let f=n.vertexShader,d=n.fragmentShader;const p=Nw(n),m=Dw(n),v=Uw(n),_=Lw(n),x=Ow(n),E=Mw(n),M=Ew(c),T=o.createProgram();let S,y,I=n.glslVersion?"#version "+n.glslVersion+`
`:"";n.isRawShaderMaterial?(S=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,M].filter(Kl).join(`
`),S.length>0&&(S+=`
`),y=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,M].filter(Kl).join(`
`),y.length>0&&(y+=`
`)):(S=[Yy(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,M,n.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",n.batching?"#define USE_BATCHING":"",n.batchingColor?"#define USE_BATCHING_COLOR":"",n.instancing?"#define USE_INSTANCING":"",n.instancingColor?"#define USE_INSTANCING_COLOR":"",n.instancingMorph?"#define USE_INSTANCING_MORPH":"",n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.map?"#define USE_MAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+v:"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.displacementMap?"#define USE_DISPLACEMENTMAP":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.mapUv?"#define MAP_UV "+n.mapUv:"",n.alphaMapUv?"#define ALPHAMAP_UV "+n.alphaMapUv:"",n.lightMapUv?"#define LIGHTMAP_UV "+n.lightMapUv:"",n.aoMapUv?"#define AOMAP_UV "+n.aoMapUv:"",n.emissiveMapUv?"#define EMISSIVEMAP_UV "+n.emissiveMapUv:"",n.bumpMapUv?"#define BUMPMAP_UV "+n.bumpMapUv:"",n.normalMapUv?"#define NORMALMAP_UV "+n.normalMapUv:"",n.displacementMapUv?"#define DISPLACEMENTMAP_UV "+n.displacementMapUv:"",n.metalnessMapUv?"#define METALNESSMAP_UV "+n.metalnessMapUv:"",n.roughnessMapUv?"#define ROUGHNESSMAP_UV "+n.roughnessMapUv:"",n.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+n.anisotropyMapUv:"",n.clearcoatMapUv?"#define CLEARCOATMAP_UV "+n.clearcoatMapUv:"",n.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+n.clearcoatNormalMapUv:"",n.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+n.clearcoatRoughnessMapUv:"",n.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+n.iridescenceMapUv:"",n.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+n.iridescenceThicknessMapUv:"",n.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+n.sheenColorMapUv:"",n.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+n.sheenRoughnessMapUv:"",n.specularMapUv?"#define SPECULARMAP_UV "+n.specularMapUv:"",n.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+n.specularColorMapUv:"",n.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+n.specularIntensityMapUv:"",n.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+n.transmissionMapUv:"",n.thicknessMapUv?"#define THICKNESSMAP_UV "+n.thicknessMapUv:"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.flatShading?"#define FLAT_SHADED":"",n.skinning?"#define USE_SKINNING":"",n.morphTargets?"#define USE_MORPHTARGETS":"",n.morphNormals&&n.flatShading===!1?"#define USE_MORPHNORMALS":"",n.morphColors?"#define USE_MORPHCOLORS":"",n.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+n.morphTextureStride:"",n.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+n.morphTargetsCount:"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.sizeAttenuation?"#define USE_SIZEATTENUATION":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Kl).join(`
`),y=[Yy(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,M,n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",n.map?"#define USE_MAP":"",n.matcap?"#define USE_MATCAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+m:"",n.envMap?"#define "+v:"",n.envMap?"#define "+_:"",x?"#define CUBEUV_TEXEL_WIDTH "+x.texelWidth:"",x?"#define CUBEUV_TEXEL_HEIGHT "+x.texelHeight:"",x?"#define CUBEUV_MAX_MIP "+x.maxMip+".0":"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoat?"#define USE_CLEARCOAT":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.dispersion?"#define USE_DISPERSION":"",n.iridescence?"#define USE_IRIDESCENCE":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaTest?"#define USE_ALPHATEST":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.sheen?"#define USE_SHEEN":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors||n.instancingColor||n.batchingColor?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.gradientMap?"#define USE_GRADIENTMAP":"",n.flatShading?"#define FLAT_SHADED":"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",n.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",n.toneMapping!==Cs?"#define TONE_MAPPING":"",n.toneMapping!==Cs?he.tonemapping_pars_fragment:"",n.toneMapping!==Cs?xw("toneMapping",n.toneMapping):"",n.dithering?"#define DITHERING":"",n.opaque?"#define OPAQUE":"",he.colorspace_pars_fragment,yw("linearToOutputTexel",n.outputColorSpace),Sw(),n.useDepthPacking?"#define DEPTH_PACKING "+n.depthPacking:"",`
`].filter(Kl).join(`
`)),f=ym(f),f=Xy(f,n),f=qy(f,n),d=ym(d),d=Xy(d,n),d=qy(d,n),f=Wy(f),d=Wy(d),n.isRawShaderMaterial!==!0&&(I=`#version 300 es
`,S=[E,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+S,y=["#define varying in",n.glslVersion===iy?"":"layout(location = 0) out highp vec4 pc_fragColor;",n.glslVersion===iy?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+y);const D=I+S+f,C=I+y+d,V=Vy(o,o.VERTEX_SHADER,D),L=Vy(o,o.FRAGMENT_SHADER,C);o.attachShader(T,V),o.attachShader(T,L),n.index0AttributeName!==void 0?o.bindAttribLocation(T,0,n.index0AttributeName):n.morphTargets===!0&&o.bindAttribLocation(T,0,"position"),o.linkProgram(T);function P(H){if(a.debug.checkShaderErrors){const ut=o.getProgramInfoLog(T).trim(),ot=o.getShaderInfoLog(V).trim(),mt=o.getShaderInfoLog(L).trim();let ct=!0,B=!0;if(o.getProgramParameter(T,o.LINK_STATUS)===!1)if(ct=!1,typeof a.debug.onShaderError=="function")a.debug.onShaderError(o,T,V,L);else{const Z=ky(o,V,"vertex"),$=ky(o,L,"fragment");console.error("THREE.WebGLProgram: Shader Error "+o.getError()+" - VALIDATE_STATUS "+o.getProgramParameter(T,o.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ut+`
`+Z+`
`+$)}else ut!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ut):(ot===""||mt==="")&&(B=!1);B&&(H.diagnostics={runnable:ct,programLog:ut,vertexShader:{log:ot,prefix:S},fragmentShader:{log:mt,prefix:y}})}o.deleteShader(V),o.deleteShader(L),G=new uf(o,T),U=bw(o,T)}let G;this.getUniforms=function(){return G===void 0&&P(this),G};let U;this.getAttributes=function(){return U===void 0&&P(this),U};let N=n.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return N===!1&&(N=o.getProgramParameter(T,mw)),N},this.destroy=function(){s.releaseStatesOfProgram(this),o.deleteProgram(T),this.program=void 0},this.type=n.shaderType,this.name=n.shaderName,this.id=gw++,this.cacheKey=t,this.usedTimes=1,this.program=T,this.vertexShader=V,this.fragmentShader=L,this}let zw=0;class Iw{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const n=t.vertexShader,s=t.fragmentShader,o=this._getShaderStage(n),c=this._getShaderStage(s),f=this._getShaderCacheForMaterial(t);return f.has(o)===!1&&(f.add(o),o.usedTimes++),f.has(c)===!1&&(f.add(c),c.usedTimes++),this}remove(t){const n=this.materialCache.get(t);for(const s of n)s.usedTimes--,s.usedTimes===0&&this.shaderCache.delete(s.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const n=this.materialCache;let s=n.get(t);return s===void 0&&(s=new Set,n.set(t,s)),s}_getShaderStage(t){const n=this.shaderCache;let s=n.get(t);return s===void 0&&(s=new Bw(t),n.set(t,s)),s}}class Bw{constructor(t){this.id=zw++,this.code=t,this.usedTimes=0}}function Fw(a,t,n,s,o,c,f){const d=new iS,p=new Iw,m=new Set,v=[],_=o.logarithmicDepthBuffer,x=o.vertexTextures;let E=o.precision;const M={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function T(U){return m.add(U),U===0?"uv":`uv${U}`}function S(U,N,H,ut,ot){const mt=ut.fog,ct=ot.geometry,B=U.isMeshStandardMaterial?ut.environment:null,Z=(U.isMeshStandardMaterial?n:t).get(U.envMap||B),$=Z&&Z.mapping===xf?Z.image.height:null,Et=M[U.type];U.precision!==null&&(E=o.getMaxPrecision(U.precision),E!==U.precision&&console.warn("THREE.WebGLProgram.getParameters:",U.precision,"not supported, using",E,"instead."));const At=ct.morphAttributes.position||ct.morphAttributes.normal||ct.morphAttributes.color,z=At!==void 0?At.length:0;let nt=0;ct.morphAttributes.position!==void 0&&(nt=1),ct.morphAttributes.normal!==void 0&&(nt=2),ct.morphAttributes.color!==void 0&&(nt=3);let St,q,ft,Tt;if(Et){const Ne=Ji[Et];St=Ne.vertexShader,q=Ne.fragmentShader}else St=U.vertexShader,q=U.fragmentShader,p.update(U),ft=p.getVertexShaderID(U),Tt=p.getFragmentShaderID(U);const Mt=a.getRenderTarget(),Ft=a.state.buffers.depth.getReversed(),Vt=ot.isInstancedMesh===!0,oe=ot.isBatchedMesh===!0,Ge=!!U.map,ve=!!U.matcap,$e=!!Z,j=!!U.aoMap,Pn=!!U.lightMap,me=!!U.bumpMap,Se=!!U.normalMap,Qt=!!U.displacementMap,Be=!!U.emissiveMap,Yt=!!U.metalnessMap,O=!!U.roughnessMap,R=U.anisotropy>0,at=U.clearcoat>0,pt=U.dispersion>0,bt=U.iridescence>0,vt=U.sheen>0,Xt=U.transmission>0,Nt=R&&!!U.anisotropyMap,Bt=at&&!!U.clearcoatMap,Me=at&&!!U.clearcoatNormalMap,Ct=at&&!!U.clearcoatRoughnessMap,Ht=bt&&!!U.iridescenceMap,Zt=bt&&!!U.iridescenceThicknessMap,qt=vt&&!!U.sheenColorMap,Ot=vt&&!!U.sheenRoughnessMap,ne=!!U.specularMap,le=!!U.specularColorMap,Ve=!!U.specularIntensityMap,Y=Xt&&!!U.transmissionMap,Rt=Xt&&!!U.thicknessMap,dt=!!U.gradientMap,yt=!!U.alphaMap,wt=U.alphaTest>0,Dt=!!U.alphaHash,ie=!!U.extensions;let tn=Cs;U.toneMapped&&(Mt===null||Mt.isXRRenderTarget===!0)&&(tn=a.toneMapping);const _n={shaderID:Et,shaderType:U.type,shaderName:U.name,vertexShader:St,fragmentShader:q,defines:U.defines,customVertexShaderID:ft,customFragmentShaderID:Tt,isRawShaderMaterial:U.isRawShaderMaterial===!0,glslVersion:U.glslVersion,precision:E,batching:oe,batchingColor:oe&&ot._colorsTexture!==null,instancing:Vt,instancingColor:Vt&&ot.instanceColor!==null,instancingMorph:Vt&&ot.morphTexture!==null,supportsVertexTextures:x,outputColorSpace:Mt===null?a.outputColorSpace:Mt.isXRRenderTarget===!0?Mt.texture.colorSpace:ko,alphaToCoverage:!!U.alphaToCoverage,map:Ge,matcap:ve,envMap:$e,envMapMode:$e&&Z.mapping,envMapCubeUVHeight:$,aoMap:j,lightMap:Pn,bumpMap:me,normalMap:Se,displacementMap:x&&Qt,emissiveMap:Be,normalMapObjectSpace:Se&&U.normalMapType===oT,normalMapTangentSpace:Se&&U.normalMapType===rT,metalnessMap:Yt,roughnessMap:O,anisotropy:R,anisotropyMap:Nt,clearcoat:at,clearcoatMap:Bt,clearcoatNormalMap:Me,clearcoatRoughnessMap:Ct,dispersion:pt,iridescence:bt,iridescenceMap:Ht,iridescenceThicknessMap:Zt,sheen:vt,sheenColorMap:qt,sheenRoughnessMap:Ot,specularMap:ne,specularColorMap:le,specularIntensityMap:Ve,transmission:Xt,transmissionMap:Y,thicknessMap:Rt,gradientMap:dt,opaque:U.transparent===!1&&U.blending===Eo&&U.alphaToCoverage===!1,alphaMap:yt,alphaTest:wt,alphaHash:Dt,combine:U.combine,mapUv:Ge&&T(U.map.channel),aoMapUv:j&&T(U.aoMap.channel),lightMapUv:Pn&&T(U.lightMap.channel),bumpMapUv:me&&T(U.bumpMap.channel),normalMapUv:Se&&T(U.normalMap.channel),displacementMapUv:Qt&&T(U.displacementMap.channel),emissiveMapUv:Be&&T(U.emissiveMap.channel),metalnessMapUv:Yt&&T(U.metalnessMap.channel),roughnessMapUv:O&&T(U.roughnessMap.channel),anisotropyMapUv:Nt&&T(U.anisotropyMap.channel),clearcoatMapUv:Bt&&T(U.clearcoatMap.channel),clearcoatNormalMapUv:Me&&T(U.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Ct&&T(U.clearcoatRoughnessMap.channel),iridescenceMapUv:Ht&&T(U.iridescenceMap.channel),iridescenceThicknessMapUv:Zt&&T(U.iridescenceThicknessMap.channel),sheenColorMapUv:qt&&T(U.sheenColorMap.channel),sheenRoughnessMapUv:Ot&&T(U.sheenRoughnessMap.channel),specularMapUv:ne&&T(U.specularMap.channel),specularColorMapUv:le&&T(U.specularColorMap.channel),specularIntensityMapUv:Ve&&T(U.specularIntensityMap.channel),transmissionMapUv:Y&&T(U.transmissionMap.channel),thicknessMapUv:Rt&&T(U.thicknessMap.channel),alphaMapUv:yt&&T(U.alphaMap.channel),vertexTangents:!!ct.attributes.tangent&&(Se||R),vertexColors:U.vertexColors,vertexAlphas:U.vertexColors===!0&&!!ct.attributes.color&&ct.attributes.color.itemSize===4,pointsUvs:ot.isPoints===!0&&!!ct.attributes.uv&&(Ge||yt),fog:!!mt,useFog:U.fog===!0,fogExp2:!!mt&&mt.isFogExp2,flatShading:U.flatShading===!0,sizeAttenuation:U.sizeAttenuation===!0,logarithmicDepthBuffer:_,reverseDepthBuffer:Ft,skinning:ot.isSkinnedMesh===!0,morphTargets:ct.morphAttributes.position!==void 0,morphNormals:ct.morphAttributes.normal!==void 0,morphColors:ct.morphAttributes.color!==void 0,morphTargetsCount:z,morphTextureStride:nt,numDirLights:N.directional.length,numPointLights:N.point.length,numSpotLights:N.spot.length,numSpotLightMaps:N.spotLightMap.length,numRectAreaLights:N.rectArea.length,numHemiLights:N.hemi.length,numDirLightShadows:N.directionalShadowMap.length,numPointLightShadows:N.pointShadowMap.length,numSpotLightShadows:N.spotShadowMap.length,numSpotLightShadowsWithMaps:N.numSpotLightShadowsWithMaps,numLightProbes:N.numLightProbes,numClippingPlanes:f.numPlanes,numClipIntersection:f.numIntersection,dithering:U.dithering,shadowMapEnabled:a.shadowMap.enabled&&H.length>0,shadowMapType:a.shadowMap.type,toneMapping:tn,decodeVideoTexture:Ge&&U.map.isVideoTexture===!0&&Pe.getTransfer(U.map.colorSpace)===qe,decodeVideoTextureEmissive:Be&&U.emissiveMap.isVideoTexture===!0&&Pe.getTransfer(U.emissiveMap.colorSpace)===qe,premultipliedAlpha:U.premultipliedAlpha,doubleSided:U.side===Na,flipSided:U.side===ii,useDepthPacking:U.depthPacking>=0,depthPacking:U.depthPacking||0,index0AttributeName:U.index0AttributeName,extensionClipCullDistance:ie&&U.extensions.clipCullDistance===!0&&s.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ie&&U.extensions.multiDraw===!0||oe)&&s.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:s.has("KHR_parallel_shader_compile"),customProgramCacheKey:U.customProgramCacheKey()};return _n.vertexUv1s=m.has(1),_n.vertexUv2s=m.has(2),_n.vertexUv3s=m.has(3),m.clear(),_n}function y(U){const N=[];if(U.shaderID?N.push(U.shaderID):(N.push(U.customVertexShaderID),N.push(U.customFragmentShaderID)),U.defines!==void 0)for(const H in U.defines)N.push(H),N.push(U.defines[H]);return U.isRawShaderMaterial===!1&&(I(N,U),D(N,U),N.push(a.outputColorSpace)),N.push(U.customProgramCacheKey),N.join()}function I(U,N){U.push(N.precision),U.push(N.outputColorSpace),U.push(N.envMapMode),U.push(N.envMapCubeUVHeight),U.push(N.mapUv),U.push(N.alphaMapUv),U.push(N.lightMapUv),U.push(N.aoMapUv),U.push(N.bumpMapUv),U.push(N.normalMapUv),U.push(N.displacementMapUv),U.push(N.emissiveMapUv),U.push(N.metalnessMapUv),U.push(N.roughnessMapUv),U.push(N.anisotropyMapUv),U.push(N.clearcoatMapUv),U.push(N.clearcoatNormalMapUv),U.push(N.clearcoatRoughnessMapUv),U.push(N.iridescenceMapUv),U.push(N.iridescenceThicknessMapUv),U.push(N.sheenColorMapUv),U.push(N.sheenRoughnessMapUv),U.push(N.specularMapUv),U.push(N.specularColorMapUv),U.push(N.specularIntensityMapUv),U.push(N.transmissionMapUv),U.push(N.thicknessMapUv),U.push(N.combine),U.push(N.fogExp2),U.push(N.sizeAttenuation),U.push(N.morphTargetsCount),U.push(N.morphAttributeCount),U.push(N.numDirLights),U.push(N.numPointLights),U.push(N.numSpotLights),U.push(N.numSpotLightMaps),U.push(N.numHemiLights),U.push(N.numRectAreaLights),U.push(N.numDirLightShadows),U.push(N.numPointLightShadows),U.push(N.numSpotLightShadows),U.push(N.numSpotLightShadowsWithMaps),U.push(N.numLightProbes),U.push(N.shadowMapType),U.push(N.toneMapping),U.push(N.numClippingPlanes),U.push(N.numClipIntersection),U.push(N.depthPacking)}function D(U,N){d.disableAll(),N.supportsVertexTextures&&d.enable(0),N.instancing&&d.enable(1),N.instancingColor&&d.enable(2),N.instancingMorph&&d.enable(3),N.matcap&&d.enable(4),N.envMap&&d.enable(5),N.normalMapObjectSpace&&d.enable(6),N.normalMapTangentSpace&&d.enable(7),N.clearcoat&&d.enable(8),N.iridescence&&d.enable(9),N.alphaTest&&d.enable(10),N.vertexColors&&d.enable(11),N.vertexAlphas&&d.enable(12),N.vertexUv1s&&d.enable(13),N.vertexUv2s&&d.enable(14),N.vertexUv3s&&d.enable(15),N.vertexTangents&&d.enable(16),N.anisotropy&&d.enable(17),N.alphaHash&&d.enable(18),N.batching&&d.enable(19),N.dispersion&&d.enable(20),N.batchingColor&&d.enable(21),U.push(d.mask),d.disableAll(),N.fog&&d.enable(0),N.useFog&&d.enable(1),N.flatShading&&d.enable(2),N.logarithmicDepthBuffer&&d.enable(3),N.reverseDepthBuffer&&d.enable(4),N.skinning&&d.enable(5),N.morphTargets&&d.enable(6),N.morphNormals&&d.enable(7),N.morphColors&&d.enable(8),N.premultipliedAlpha&&d.enable(9),N.shadowMapEnabled&&d.enable(10),N.doubleSided&&d.enable(11),N.flipSided&&d.enable(12),N.useDepthPacking&&d.enable(13),N.dithering&&d.enable(14),N.transmission&&d.enable(15),N.sheen&&d.enable(16),N.opaque&&d.enable(17),N.pointsUvs&&d.enable(18),N.decodeVideoTexture&&d.enable(19),N.decodeVideoTextureEmissive&&d.enable(20),N.alphaToCoverage&&d.enable(21),U.push(d.mask)}function C(U){const N=M[U.type];let H;if(N){const ut=Ji[N];H=_f.clone(ut.uniforms)}else H=U.uniforms;return H}function V(U,N){let H;for(let ut=0,ot=v.length;ut<ot;ut++){const mt=v[ut];if(mt.cacheKey===N){H=mt,++H.usedTimes;break}}return H===void 0&&(H=new Pw(a,N,U,c),v.push(H)),H}function L(U){if(--U.usedTimes===0){const N=v.indexOf(U);v[N]=v[v.length-1],v.pop(),U.destroy()}}function P(U){p.remove(U)}function G(){p.dispose()}return{getParameters:S,getProgramCacheKey:y,getUniforms:C,acquireProgram:V,releaseProgram:L,releaseShaderCache:P,programs:v,dispose:G}}function Hw(){let a=new WeakMap;function t(f){return a.has(f)}function n(f){let d=a.get(f);return d===void 0&&(d={},a.set(f,d)),d}function s(f){a.delete(f)}function o(f,d,p){a.get(f)[d]=p}function c(){a=new WeakMap}return{has:t,get:n,remove:s,update:o,dispose:c}}function Gw(a,t){return a.groupOrder!==t.groupOrder?a.groupOrder-t.groupOrder:a.renderOrder!==t.renderOrder?a.renderOrder-t.renderOrder:a.material.id!==t.material.id?a.material.id-t.material.id:a.z!==t.z?a.z-t.z:a.id-t.id}function Qy(a,t){return a.groupOrder!==t.groupOrder?a.groupOrder-t.groupOrder:a.renderOrder!==t.renderOrder?a.renderOrder-t.renderOrder:a.z!==t.z?t.z-a.z:a.id-t.id}function Zy(){const a=[];let t=0;const n=[],s=[],o=[];function c(){t=0,n.length=0,s.length=0,o.length=0}function f(_,x,E,M,T,S){let y=a[t];return y===void 0?(y={id:_.id,object:_,geometry:x,material:E,groupOrder:M,renderOrder:_.renderOrder,z:T,group:S},a[t]=y):(y.id=_.id,y.object=_,y.geometry=x,y.material=E,y.groupOrder=M,y.renderOrder=_.renderOrder,y.z=T,y.group=S),t++,y}function d(_,x,E,M,T,S){const y=f(_,x,E,M,T,S);E.transmission>0?s.push(y):E.transparent===!0?o.push(y):n.push(y)}function p(_,x,E,M,T,S){const y=f(_,x,E,M,T,S);E.transmission>0?s.unshift(y):E.transparent===!0?o.unshift(y):n.unshift(y)}function m(_,x){n.length>1&&n.sort(_||Gw),s.length>1&&s.sort(x||Qy),o.length>1&&o.sort(x||Qy)}function v(){for(let _=t,x=a.length;_<x;_++){const E=a[_];if(E.id===null)break;E.id=null,E.object=null,E.geometry=null,E.material=null,E.group=null}}return{opaque:n,transmissive:s,transparent:o,init:c,push:d,unshift:p,finish:v,sort:m}}function Vw(){let a=new WeakMap;function t(s,o){const c=a.get(s);let f;return c===void 0?(f=new Zy,a.set(s,[f])):o>=c.length?(f=new Zy,c.push(f)):f=c[o],f}function n(){a=new WeakMap}return{get:t,dispose:n}}function jw(){const a={};return{get:function(t){if(a[t.id]!==void 0)return a[t.id];let n;switch(t.type){case"DirectionalLight":n={direction:new W,color:new pe};break;case"SpotLight":n={position:new W,direction:new W,color:new pe,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":n={position:new W,color:new pe,distance:0,decay:0};break;case"HemisphereLight":n={direction:new W,skyColor:new pe,groundColor:new pe};break;case"RectAreaLight":n={color:new pe,position:new W,halfWidth:new W,halfHeight:new W};break}return a[t.id]=n,n}}}function kw(){const a={};return{get:function(t){if(a[t.id]!==void 0)return a[t.id];let n;switch(t.type){case"DirectionalLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"SpotLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"PointLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt,shadowCameraNear:1,shadowCameraFar:1e3};break}return a[t.id]=n,n}}}let Xw=0;function qw(a,t){return(t.castShadow?2:0)-(a.castShadow?2:0)+(t.map?1:0)-(a.map?1:0)}function Ww(a){const t=new jw,n=kw(),s={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let m=0;m<9;m++)s.probe.push(new W);const o=new W,c=new an,f=new an;function d(m){let v=0,_=0,x=0;for(let U=0;U<9;U++)s.probe[U].set(0,0,0);let E=0,M=0,T=0,S=0,y=0,I=0,D=0,C=0,V=0,L=0,P=0;m.sort(qw);for(let U=0,N=m.length;U<N;U++){const H=m[U],ut=H.color,ot=H.intensity,mt=H.distance,ct=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)v+=ut.r*ot,_+=ut.g*ot,x+=ut.b*ot;else if(H.isLightProbe){for(let B=0;B<9;B++)s.probe[B].addScaledVector(H.sh.coefficients[B],ot);P++}else if(H.isDirectionalLight){const B=t.get(H);if(B.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,s.directionalShadow[E]=$,s.directionalShadowMap[E]=ct,s.directionalShadowMatrix[E]=H.shadow.matrix,I++}s.directional[E]=B,E++}else if(H.isSpotLight){const B=t.get(H);B.position.setFromMatrixPosition(H.matrixWorld),B.color.copy(ut).multiplyScalar(ot),B.distance=mt,B.coneCos=Math.cos(H.angle),B.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),B.decay=H.decay,s.spot[T]=B;const Z=H.shadow;if(H.map&&(s.spotLightMap[V]=H.map,V++,Z.updateMatrices(H),H.castShadow&&L++),s.spotLightMatrix[T]=Z.matrix,H.castShadow){const $=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,s.spotShadow[T]=$,s.spotShadowMap[T]=ct,C++}T++}else if(H.isRectAreaLight){const B=t.get(H);B.color.copy(ut).multiplyScalar(ot),B.halfWidth.set(H.width*.5,0,0),B.halfHeight.set(0,H.height*.5,0),s.rectArea[S]=B,S++}else if(H.isPointLight){const B=t.get(H);if(B.color.copy(H.color).multiplyScalar(H.intensity),B.distance=H.distance,B.decay=H.decay,H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,$.shadowCameraNear=Z.camera.near,$.shadowCameraFar=Z.camera.far,s.pointShadow[M]=$,s.pointShadowMap[M]=ct,s.pointShadowMatrix[M]=H.shadow.matrix,D++}s.point[M]=B,M++}else if(H.isHemisphereLight){const B=t.get(H);B.skyColor.copy(H.color).multiplyScalar(ot),B.groundColor.copy(H.groundColor).multiplyScalar(ot),s.hemi[y]=B,y++}}S>0&&(a.has("OES_texture_float_linear")===!0?(s.rectAreaLTC1=Lt.LTC_FLOAT_1,s.rectAreaLTC2=Lt.LTC_FLOAT_2):(s.rectAreaLTC1=Lt.LTC_HALF_1,s.rectAreaLTC2=Lt.LTC_HALF_2)),s.ambient[0]=v,s.ambient[1]=_,s.ambient[2]=x;const G=s.hash;(G.directionalLength!==E||G.pointLength!==M||G.spotLength!==T||G.rectAreaLength!==S||G.hemiLength!==y||G.numDirectionalShadows!==I||G.numPointShadows!==D||G.numSpotShadows!==C||G.numSpotMaps!==V||G.numLightProbes!==P)&&(s.directional.length=E,s.spot.length=T,s.rectArea.length=S,s.point.length=M,s.hemi.length=y,s.directionalShadow.length=I,s.directionalShadowMap.length=I,s.pointShadow.length=D,s.pointShadowMap.length=D,s.spotShadow.length=C,s.spotShadowMap.length=C,s.directionalShadowMatrix.length=I,s.pointShadowMatrix.length=D,s.spotLightMatrix.length=C+V-L,s.spotLightMap.length=V,s.numSpotLightShadowsWithMaps=L,s.numLightProbes=P,G.directionalLength=E,G.pointLength=M,G.spotLength=T,G.rectAreaLength=S,G.hemiLength=y,G.numDirectionalShadows=I,G.numPointShadows=D,G.numSpotShadows=C,G.numSpotMaps=V,G.numLightProbes=P,s.version=Xw++)}function p(m,v){let _=0,x=0,E=0,M=0,T=0;const S=v.matrixWorldInverse;for(let y=0,I=m.length;y<I;y++){const D=m[y];if(D.isDirectionalLight){const C=s.directional[_];C.direction.setFromMatrixPosition(D.matrixWorld),o.setFromMatrixPosition(D.target.matrixWorld),C.direction.sub(o),C.direction.transformDirection(S),_++}else if(D.isSpotLight){const C=s.spot[E];C.position.setFromMatrixPosition(D.matrixWorld),C.position.applyMatrix4(S),C.direction.setFromMatrixPosition(D.matrixWorld),o.setFromMatrixPosition(D.target.matrixWorld),C.direction.sub(o),C.direction.transformDirection(S),E++}else if(D.isRectAreaLight){const C=s.rectArea[M];C.position.setFromMatrixPosition(D.matrixWorld),C.position.applyMatrix4(S),f.identity(),c.copy(D.matrixWorld),c.premultiply(S),f.extractRotation(c),C.halfWidth.set(D.width*.5,0,0),C.halfHeight.set(0,D.height*.5,0),C.halfWidth.applyMatrix4(f),C.halfHeight.applyMatrix4(f),M++}else if(D.isPointLight){const C=s.point[x];C.position.setFromMatrixPosition(D.matrixWorld),C.position.applyMatrix4(S),x++}else if(D.isHemisphereLight){const C=s.hemi[T];C.direction.setFromMatrixPosition(D.matrixWorld),C.direction.transformDirection(S),T++}}}return{setup:d,setupView:p,state:s}}function Ky(a){const t=new Ww(a),n=[],s=[];function o(v){m.camera=v,n.length=0,s.length=0}function c(v){n.push(v)}function f(v){s.push(v)}function d(){t.setup(n)}function p(v){t.setupView(n,v)}const m={lightsArray:n,shadowsArray:s,camera:null,lights:t,transmissionRenderTarget:{}};return{init:o,state:m,setupLights:d,setupLightsView:p,pushLight:c,pushShadow:f}}function Yw(a){let t=new WeakMap;function n(o,c=0){const f=t.get(o);let d;return f===void 0?(d=new Ky(a),t.set(o,[d])):c>=f.length?(d=new Ky(a),f.push(d)):d=f[c],d}function s(){t=new WeakMap}return{get:n,dispose:s}}const Qw=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Zw=`uniform sampler2D shadow_pass;
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
}`;function Kw(a,t,n){let s=new Hm;const o=new Wt,c=new Wt,f=new We,d=new SA({depthPacking:sT}),p=new MA,m={},v=n.maxTextureSize,_={[Rs]:ii,[ii]:Rs,[Na]:Na},x=new Yn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Wt},radius:{value:4}},vertexShader:Qw,fragmentShader:Zw}),E=x.clone();E.defines.HORIZONTAL_PASS=1;const M=new Vi;M.setAttribute("position",new ea(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const T=new Wn(M,x),S=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Hx;let y=this.type;this.render=function(L,P,G){if(S.enabled===!1||S.autoUpdate===!1&&S.needsUpdate===!1||L.length===0)return;const U=a.getRenderTarget(),N=a.getActiveCubeFace(),H=a.getActiveMipmapLevel(),ut=a.state;ut.setBlending(Oa),ut.buffers.color.setClear(1,1,1,1),ut.buffers.depth.setTest(!0),ut.setScissorTest(!1);const ot=y!==Ca&&this.type===Ca,mt=y===Ca&&this.type!==Ca;for(let ct=0,B=L.length;ct<B;ct++){const Z=L[ct],$=Z.shadow;if($===void 0){console.warn("THREE.WebGLShadowMap:",Z,"has no shadow.");continue}if($.autoUpdate===!1&&$.needsUpdate===!1)continue;o.copy($.mapSize);const Et=$.getFrameExtents();if(o.multiply(Et),c.copy($.mapSize),(o.x>v||o.y>v)&&(o.x>v&&(c.x=Math.floor(v/Et.x),o.x=c.x*Et.x,$.mapSize.x=c.x),o.y>v&&(c.y=Math.floor(v/Et.y),o.y=c.y*Et.y,$.mapSize.y=c.y)),$.map===null||ot===!0||mt===!0){const z=this.type!==Ca?{minFilter:Hi,magFilter:Hi}:{};$.map!==null&&$.map.dispose(),$.map=new Gi(o.x,o.y,z),$.map.texture.name=Z.name+".shadowMap",$.camera.updateProjectionMatrix()}a.setRenderTarget($.map),a.clear();const At=$.getViewportCount();for(let z=0;z<At;z++){const nt=$.getViewport(z);f.set(c.x*nt.x,c.y*nt.y,c.x*nt.z,c.y*nt.w),ut.viewport(f),$.updateMatrices(Z,z),s=$.getFrustum(),C(P,G,$.camera,Z,this.type)}$.isPointLightShadow!==!0&&this.type===Ca&&I($,G),$.needsUpdate=!1}y=this.type,S.needsUpdate=!1,a.setRenderTarget(U,N,H)};function I(L,P){const G=t.update(T);x.defines.VSM_SAMPLES!==L.blurSamples&&(x.defines.VSM_SAMPLES=L.blurSamples,E.defines.VSM_SAMPLES=L.blurSamples,x.needsUpdate=!0,E.needsUpdate=!0),L.mapPass===null&&(L.mapPass=new Gi(o.x,o.y)),x.uniforms.shadow_pass.value=L.map.texture,x.uniforms.resolution.value=L.mapSize,x.uniforms.radius.value=L.radius,a.setRenderTarget(L.mapPass),a.clear(),a.renderBufferDirect(P,null,G,x,T,null),E.uniforms.shadow_pass.value=L.mapPass.texture,E.uniforms.resolution.value=L.mapSize,E.uniforms.radius.value=L.radius,a.setRenderTarget(L.map),a.clear(),a.renderBufferDirect(P,null,G,E,T,null)}function D(L,P,G,U){let N=null;const H=G.isPointLight===!0?L.customDistanceMaterial:L.customDepthMaterial;if(H!==void 0)N=H;else if(N=G.isPointLight===!0?p:d,a.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const ut=N.uuid,ot=P.uuid;let mt=m[ut];mt===void 0&&(mt={},m[ut]=mt);let ct=mt[ot];ct===void 0&&(ct=N.clone(),mt[ot]=ct,P.addEventListener("dispose",V)),N=ct}if(N.visible=P.visible,N.wireframe=P.wireframe,U===Ca?N.side=P.shadowSide!==null?P.shadowSide:P.side:N.side=P.shadowSide!==null?P.shadowSide:_[P.side],N.alphaMap=P.alphaMap,N.alphaTest=P.alphaTest,N.map=P.map,N.clipShadows=P.clipShadows,N.clippingPlanes=P.clippingPlanes,N.clipIntersection=P.clipIntersection,N.displacementMap=P.displacementMap,N.displacementScale=P.displacementScale,N.displacementBias=P.displacementBias,N.wireframeLinewidth=P.wireframeLinewidth,N.linewidth=P.linewidth,G.isPointLight===!0&&N.isMeshDistanceMaterial===!0){const ut=a.properties.get(N);ut.light=G}return N}function C(L,P,G,U,N){if(L.visible===!1)return;if(L.layers.test(P.layers)&&(L.isMesh||L.isLine||L.isPoints)&&(L.castShadow||L.receiveShadow&&N===Ca)&&(!L.frustumCulled||s.intersectsObject(L))){L.modelViewMatrix.multiplyMatrices(G.matrixWorldInverse,L.matrixWorld);const ot=t.update(L),mt=L.material;if(Array.isArray(mt)){const ct=ot.groups;for(let B=0,Z=ct.length;B<Z;B++){const $=ct[B],Et=mt[$.materialIndex];if(Et&&Et.visible){const At=D(L,Et,U,N);L.onBeforeShadow(a,L,P,G,ot,At,$),a.renderBufferDirect(G,null,ot,At,L,$),L.onAfterShadow(a,L,P,G,ot,At,$)}}}else if(mt.visible){const ct=D(L,mt,U,N);L.onBeforeShadow(a,L,P,G,ot,ct,null),a.renderBufferDirect(G,null,ot,ct,L,null),L.onAfterShadow(a,L,P,G,ot,ct,null)}}const ut=L.children;for(let ot=0,mt=ut.length;ot<mt;ot++)C(ut[ot],P,G,U,N)}function V(L){L.target.removeEventListener("dispose",V);for(const G in m){const U=m[G],N=L.target.uuid;N in U&&(U[N].dispose(),delete U[N])}}}const Jw={[zp]:Ip,[Bp]:Gp,[Fp]:Vp,[Fo]:Hp,[Ip]:zp,[Gp]:Bp,[Vp]:Fp,[Hp]:Fo};function $w(a,t){function n(){let Y=!1;const Rt=new We;let dt=null;const yt=new We(0,0,0,0);return{setMask:function(wt){dt!==wt&&!Y&&(a.colorMask(wt,wt,wt,wt),dt=wt)},setLocked:function(wt){Y=wt},setClear:function(wt,Dt,ie,tn,_n){_n===!0&&(wt*=tn,Dt*=tn,ie*=tn),Rt.set(wt,Dt,ie,tn),yt.equals(Rt)===!1&&(a.clearColor(wt,Dt,ie,tn),yt.copy(Rt))},reset:function(){Y=!1,dt=null,yt.set(-1,0,0,0)}}}function s(){let Y=!1,Rt=!1,dt=null,yt=null,wt=null;return{setReversed:function(Dt){if(Rt!==Dt){const ie=t.get("EXT_clip_control");Rt?ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.ZERO_TO_ONE_EXT):ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.NEGATIVE_ONE_TO_ONE_EXT);const tn=wt;wt=null,this.setClear(tn)}Rt=Dt},getReversed:function(){return Rt},setTest:function(Dt){Dt?Mt(a.DEPTH_TEST):Ft(a.DEPTH_TEST)},setMask:function(Dt){dt!==Dt&&!Y&&(a.depthMask(Dt),dt=Dt)},setFunc:function(Dt){if(Rt&&(Dt=Jw[Dt]),yt!==Dt){switch(Dt){case zp:a.depthFunc(a.NEVER);break;case Ip:a.depthFunc(a.ALWAYS);break;case Bp:a.depthFunc(a.LESS);break;case Fo:a.depthFunc(a.LEQUAL);break;case Fp:a.depthFunc(a.EQUAL);break;case Hp:a.depthFunc(a.GEQUAL);break;case Gp:a.depthFunc(a.GREATER);break;case Vp:a.depthFunc(a.NOTEQUAL);break;default:a.depthFunc(a.LEQUAL)}yt=Dt}},setLocked:function(Dt){Y=Dt},setClear:function(Dt){wt!==Dt&&(Rt&&(Dt=1-Dt),a.clearDepth(Dt),wt=Dt)},reset:function(){Y=!1,dt=null,yt=null,wt=null,Rt=!1}}}function o(){let Y=!1,Rt=null,dt=null,yt=null,wt=null,Dt=null,ie=null,tn=null,_n=null;return{setTest:function(Ne){Y||(Ne?Mt(a.STENCIL_TEST):Ft(a.STENCIL_TEST))},setMask:function(Ne){Rt!==Ne&&!Y&&(a.stencilMask(Ne),Rt=Ne)},setFunc:function(Ne,Rn,wi){(dt!==Ne||yt!==Rn||wt!==wi)&&(a.stencilFunc(Ne,Rn,wi),dt=Ne,yt=Rn,wt=wi)},setOp:function(Ne,Rn,wi){(Dt!==Ne||ie!==Rn||tn!==wi)&&(a.stencilOp(Ne,Rn,wi),Dt=Ne,ie=Rn,tn=wi)},setLocked:function(Ne){Y=Ne},setClear:function(Ne){_n!==Ne&&(a.clearStencil(Ne),_n=Ne)},reset:function(){Y=!1,Rt=null,dt=null,yt=null,wt=null,Dt=null,ie=null,tn=null,_n=null}}}const c=new n,f=new s,d=new o,p=new WeakMap,m=new WeakMap;let v={},_={},x=new WeakMap,E=[],M=null,T=!1,S=null,y=null,I=null,D=null,C=null,V=null,L=null,P=new pe(0,0,0),G=0,U=!1,N=null,H=null,ut=null,ot=null,mt=null;const ct=a.getParameter(a.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let B=!1,Z=0;const $=a.getParameter(a.VERSION);$.indexOf("WebGL")!==-1?(Z=parseFloat(/^WebGL (\d)/.exec($)[1]),B=Z>=1):$.indexOf("OpenGL ES")!==-1&&(Z=parseFloat(/^OpenGL ES (\d)/.exec($)[1]),B=Z>=2);let Et=null,At={};const z=a.getParameter(a.SCISSOR_BOX),nt=a.getParameter(a.VIEWPORT),St=new We().fromArray(z),q=new We().fromArray(nt);function ft(Y,Rt,dt,yt){const wt=new Uint8Array(4),Dt=a.createTexture();a.bindTexture(Y,Dt),a.texParameteri(Y,a.TEXTURE_MIN_FILTER,a.NEAREST),a.texParameteri(Y,a.TEXTURE_MAG_FILTER,a.NEAREST);for(let ie=0;ie<dt;ie++)Y===a.TEXTURE_3D||Y===a.TEXTURE_2D_ARRAY?a.texImage3D(Rt,0,a.RGBA,1,1,yt,0,a.RGBA,a.UNSIGNED_BYTE,wt):a.texImage2D(Rt+ie,0,a.RGBA,1,1,0,a.RGBA,a.UNSIGNED_BYTE,wt);return Dt}const Tt={};Tt[a.TEXTURE_2D]=ft(a.TEXTURE_2D,a.TEXTURE_2D,1),Tt[a.TEXTURE_CUBE_MAP]=ft(a.TEXTURE_CUBE_MAP,a.TEXTURE_CUBE_MAP_POSITIVE_X,6),Tt[a.TEXTURE_2D_ARRAY]=ft(a.TEXTURE_2D_ARRAY,a.TEXTURE_2D_ARRAY,1,1),Tt[a.TEXTURE_3D]=ft(a.TEXTURE_3D,a.TEXTURE_3D,1,1),c.setClear(0,0,0,1),f.setClear(1),d.setClear(0),Mt(a.DEPTH_TEST),f.setFunc(Fo),me(!1),Se(J0),Mt(a.CULL_FACE),j(Oa);function Mt(Y){v[Y]!==!0&&(a.enable(Y),v[Y]=!0)}function Ft(Y){v[Y]!==!1&&(a.disable(Y),v[Y]=!1)}function Vt(Y,Rt){return _[Y]!==Rt?(a.bindFramebuffer(Y,Rt),_[Y]=Rt,Y===a.DRAW_FRAMEBUFFER&&(_[a.FRAMEBUFFER]=Rt),Y===a.FRAMEBUFFER&&(_[a.DRAW_FRAMEBUFFER]=Rt),!0):!1}function oe(Y,Rt){let dt=E,yt=!1;if(Y){dt=x.get(Rt),dt===void 0&&(dt=[],x.set(Rt,dt));const wt=Y.textures;if(dt.length!==wt.length||dt[0]!==a.COLOR_ATTACHMENT0){for(let Dt=0,ie=wt.length;Dt<ie;Dt++)dt[Dt]=a.COLOR_ATTACHMENT0+Dt;dt.length=wt.length,yt=!0}}else dt[0]!==a.BACK&&(dt[0]=a.BACK,yt=!0);yt&&a.drawBuffers(dt)}function Ge(Y){return M!==Y?(a.useProgram(Y),M=Y,!0):!1}const ve={[sr]:a.FUNC_ADD,[Db]:a.FUNC_SUBTRACT,[Ub]:a.FUNC_REVERSE_SUBTRACT};ve[Lb]=a.MIN,ve[Ob]=a.MAX;const $e={[Pb]:a.ZERO,[zb]:a.ONE,[Ib]:a.SRC_COLOR,[Op]:a.SRC_ALPHA,[jb]:a.SRC_ALPHA_SATURATE,[Gb]:a.DST_COLOR,[Fb]:a.DST_ALPHA,[Bb]:a.ONE_MINUS_SRC_COLOR,[Pp]:a.ONE_MINUS_SRC_ALPHA,[Vb]:a.ONE_MINUS_DST_COLOR,[Hb]:a.ONE_MINUS_DST_ALPHA,[kb]:a.CONSTANT_COLOR,[Xb]:a.ONE_MINUS_CONSTANT_COLOR,[qb]:a.CONSTANT_ALPHA,[Wb]:a.ONE_MINUS_CONSTANT_ALPHA};function j(Y,Rt,dt,yt,wt,Dt,ie,tn,_n,Ne){if(Y===Oa){T===!0&&(Ft(a.BLEND),T=!1);return}if(T===!1&&(Mt(a.BLEND),T=!0),Y!==Nb){if(Y!==S||Ne!==U){if((y!==sr||C!==sr)&&(a.blendEquation(a.FUNC_ADD),y=sr,C=sr),Ne)switch(Y){case Eo:a.blendFuncSeparate(a.ONE,a.ONE_MINUS_SRC_ALPHA,a.ONE,a.ONE_MINUS_SRC_ALPHA);break;case Lp:a.blendFunc(a.ONE,a.ONE);break;case $0:a.blendFuncSeparate(a.ZERO,a.ONE_MINUS_SRC_COLOR,a.ZERO,a.ONE);break;case ty:a.blendFuncSeparate(a.ZERO,a.SRC_COLOR,a.ZERO,a.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}else switch(Y){case Eo:a.blendFuncSeparate(a.SRC_ALPHA,a.ONE_MINUS_SRC_ALPHA,a.ONE,a.ONE_MINUS_SRC_ALPHA);break;case Lp:a.blendFunc(a.SRC_ALPHA,a.ONE);break;case $0:a.blendFuncSeparate(a.ZERO,a.ONE_MINUS_SRC_COLOR,a.ZERO,a.ONE);break;case ty:a.blendFunc(a.ZERO,a.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}I=null,D=null,V=null,L=null,P.set(0,0,0),G=0,S=Y,U=Ne}return}wt=wt||Rt,Dt=Dt||dt,ie=ie||yt,(Rt!==y||wt!==C)&&(a.blendEquationSeparate(ve[Rt],ve[wt]),y=Rt,C=wt),(dt!==I||yt!==D||Dt!==V||ie!==L)&&(a.blendFuncSeparate($e[dt],$e[yt],$e[Dt],$e[ie]),I=dt,D=yt,V=Dt,L=ie),(tn.equals(P)===!1||_n!==G)&&(a.blendColor(tn.r,tn.g,tn.b,_n),P.copy(tn),G=_n),S=Y,U=!1}function Pn(Y,Rt){Y.side===Na?Ft(a.CULL_FACE):Mt(a.CULL_FACE);let dt=Y.side===ii;Rt&&(dt=!dt),me(dt),Y.blending===Eo&&Y.transparent===!1?j(Oa):j(Y.blending,Y.blendEquation,Y.blendSrc,Y.blendDst,Y.blendEquationAlpha,Y.blendSrcAlpha,Y.blendDstAlpha,Y.blendColor,Y.blendAlpha,Y.premultipliedAlpha),f.setFunc(Y.depthFunc),f.setTest(Y.depthTest),f.setMask(Y.depthWrite),c.setMask(Y.colorWrite);const yt=Y.stencilWrite;d.setTest(yt),yt&&(d.setMask(Y.stencilWriteMask),d.setFunc(Y.stencilFunc,Y.stencilRef,Y.stencilFuncMask),d.setOp(Y.stencilFail,Y.stencilZFail,Y.stencilZPass)),Be(Y.polygonOffset,Y.polygonOffsetFactor,Y.polygonOffsetUnits),Y.alphaToCoverage===!0?Mt(a.SAMPLE_ALPHA_TO_COVERAGE):Ft(a.SAMPLE_ALPHA_TO_COVERAGE)}function me(Y){N!==Y&&(Y?a.frontFace(a.CW):a.frontFace(a.CCW),N=Y)}function Se(Y){Y!==Cb?(Mt(a.CULL_FACE),Y!==H&&(Y===J0?a.cullFace(a.BACK):Y===Rb?a.cullFace(a.FRONT):a.cullFace(a.FRONT_AND_BACK))):Ft(a.CULL_FACE),H=Y}function Qt(Y){Y!==ut&&(B&&a.lineWidth(Y),ut=Y)}function Be(Y,Rt,dt){Y?(Mt(a.POLYGON_OFFSET_FILL),(ot!==Rt||mt!==dt)&&(a.polygonOffset(Rt,dt),ot=Rt,mt=dt)):Ft(a.POLYGON_OFFSET_FILL)}function Yt(Y){Y?Mt(a.SCISSOR_TEST):Ft(a.SCISSOR_TEST)}function O(Y){Y===void 0&&(Y=a.TEXTURE0+ct-1),Et!==Y&&(a.activeTexture(Y),Et=Y)}function R(Y,Rt,dt){dt===void 0&&(Et===null?dt=a.TEXTURE0+ct-1:dt=Et);let yt=At[dt];yt===void 0&&(yt={type:void 0,texture:void 0},At[dt]=yt),(yt.type!==Y||yt.texture!==Rt)&&(Et!==dt&&(a.activeTexture(dt),Et=dt),a.bindTexture(Y,Rt||Tt[Y]),yt.type=Y,yt.texture=Rt)}function at(){const Y=At[Et];Y!==void 0&&Y.type!==void 0&&(a.bindTexture(Y.type,null),Y.type=void 0,Y.texture=void 0)}function pt(){try{a.compressedTexImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function bt(){try{a.compressedTexImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function vt(){try{a.texSubImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Xt(){try{a.texSubImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Nt(){try{a.compressedTexSubImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Bt(){try{a.compressedTexSubImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Me(){try{a.texStorage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ct(){try{a.texStorage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ht(){try{a.texImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Zt(){try{a.texImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function qt(Y){St.equals(Y)===!1&&(a.scissor(Y.x,Y.y,Y.z,Y.w),St.copy(Y))}function Ot(Y){q.equals(Y)===!1&&(a.viewport(Y.x,Y.y,Y.z,Y.w),q.copy(Y))}function ne(Y,Rt){let dt=m.get(Rt);dt===void 0&&(dt=new WeakMap,m.set(Rt,dt));let yt=dt.get(Y);yt===void 0&&(yt=a.getUniformBlockIndex(Rt,Y.name),dt.set(Y,yt))}function le(Y,Rt){const yt=m.get(Rt).get(Y);p.get(Rt)!==yt&&(a.uniformBlockBinding(Rt,yt,Y.__bindingPointIndex),p.set(Rt,yt))}function Ve(){a.disable(a.BLEND),a.disable(a.CULL_FACE),a.disable(a.DEPTH_TEST),a.disable(a.POLYGON_OFFSET_FILL),a.disable(a.SCISSOR_TEST),a.disable(a.STENCIL_TEST),a.disable(a.SAMPLE_ALPHA_TO_COVERAGE),a.blendEquation(a.FUNC_ADD),a.blendFunc(a.ONE,a.ZERO),a.blendFuncSeparate(a.ONE,a.ZERO,a.ONE,a.ZERO),a.blendColor(0,0,0,0),a.colorMask(!0,!0,!0,!0),a.clearColor(0,0,0,0),a.depthMask(!0),a.depthFunc(a.LESS),f.setReversed(!1),a.clearDepth(1),a.stencilMask(4294967295),a.stencilFunc(a.ALWAYS,0,4294967295),a.stencilOp(a.KEEP,a.KEEP,a.KEEP),a.clearStencil(0),a.cullFace(a.BACK),a.frontFace(a.CCW),a.polygonOffset(0,0),a.activeTexture(a.TEXTURE0),a.bindFramebuffer(a.FRAMEBUFFER,null),a.bindFramebuffer(a.DRAW_FRAMEBUFFER,null),a.bindFramebuffer(a.READ_FRAMEBUFFER,null),a.useProgram(null),a.lineWidth(1),a.scissor(0,0,a.canvas.width,a.canvas.height),a.viewport(0,0,a.canvas.width,a.canvas.height),v={},Et=null,At={},_={},x=new WeakMap,E=[],M=null,T=!1,S=null,y=null,I=null,D=null,C=null,V=null,L=null,P=new pe(0,0,0),G=0,U=!1,N=null,H=null,ut=null,ot=null,mt=null,St.set(0,0,a.canvas.width,a.canvas.height),q.set(0,0,a.canvas.width,a.canvas.height),c.reset(),f.reset(),d.reset()}return{buffers:{color:c,depth:f,stencil:d},enable:Mt,disable:Ft,bindFramebuffer:Vt,drawBuffers:oe,useProgram:Ge,setBlending:j,setMaterial:Pn,setFlipSided:me,setCullFace:Se,setLineWidth:Qt,setPolygonOffset:Be,setScissorTest:Yt,activeTexture:O,bindTexture:R,unbindTexture:at,compressedTexImage2D:pt,compressedTexImage3D:bt,texImage2D:Ht,texImage3D:Zt,updateUBOMapping:ne,uniformBlockBinding:le,texStorage2D:Me,texStorage3D:Ct,texSubImage2D:vt,texSubImage3D:Xt,compressedTexSubImage2D:Nt,compressedTexSubImage3D:Bt,scissor:qt,viewport:Ot,reset:Ve}}function tN(a,t,n,s,o,c,f){const d=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),m=new Wt,v=new WeakMap;let _;const x=new WeakMap;let E=!1;try{E=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function M(O,R){return E?new OffscreenCanvas(O,R):vf("canvas")}function T(O,R,at){let pt=1;const bt=Yt(O);if((bt.width>at||bt.height>at)&&(pt=at/Math.max(bt.width,bt.height)),pt<1)if(typeof HTMLImageElement<"u"&&O instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&O instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&O instanceof ImageBitmap||typeof VideoFrame<"u"&&O instanceof VideoFrame){const vt=Math.floor(pt*bt.width),Xt=Math.floor(pt*bt.height);_===void 0&&(_=M(vt,Xt));const Nt=R?M(vt,Xt):_;return Nt.width=vt,Nt.height=Xt,Nt.getContext("2d").drawImage(O,0,0,vt,Xt),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+bt.width+"x"+bt.height+") to ("+vt+"x"+Xt+")."),Nt}else return"data"in O&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+bt.width+"x"+bt.height+")."),O;return O}function S(O){return O.generateMipmaps}function y(O){a.generateMipmap(O)}function I(O){return O.isWebGLCubeRenderTarget?a.TEXTURE_CUBE_MAP:O.isWebGL3DRenderTarget?a.TEXTURE_3D:O.isWebGLArrayRenderTarget||O.isCompressedArrayTexture?a.TEXTURE_2D_ARRAY:a.TEXTURE_2D}function D(O,R,at,pt,bt=!1){if(O!==null){if(a[O]!==void 0)return a[O];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+O+"'")}let vt=R;if(R===a.RED&&(at===a.FLOAT&&(vt=a.R32F),at===a.HALF_FLOAT&&(vt=a.R16F),at===a.UNSIGNED_BYTE&&(vt=a.R8)),R===a.RED_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.R8UI),at===a.UNSIGNED_SHORT&&(vt=a.R16UI),at===a.UNSIGNED_INT&&(vt=a.R32UI),at===a.BYTE&&(vt=a.R8I),at===a.SHORT&&(vt=a.R16I),at===a.INT&&(vt=a.R32I)),R===a.RG&&(at===a.FLOAT&&(vt=a.RG32F),at===a.HALF_FLOAT&&(vt=a.RG16F),at===a.UNSIGNED_BYTE&&(vt=a.RG8)),R===a.RG_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RG8UI),at===a.UNSIGNED_SHORT&&(vt=a.RG16UI),at===a.UNSIGNED_INT&&(vt=a.RG32UI),at===a.BYTE&&(vt=a.RG8I),at===a.SHORT&&(vt=a.RG16I),at===a.INT&&(vt=a.RG32I)),R===a.RGB_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RGB8UI),at===a.UNSIGNED_SHORT&&(vt=a.RGB16UI),at===a.UNSIGNED_INT&&(vt=a.RGB32UI),at===a.BYTE&&(vt=a.RGB8I),at===a.SHORT&&(vt=a.RGB16I),at===a.INT&&(vt=a.RGB32I)),R===a.RGBA_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RGBA8UI),at===a.UNSIGNED_SHORT&&(vt=a.RGBA16UI),at===a.UNSIGNED_INT&&(vt=a.RGBA32UI),at===a.BYTE&&(vt=a.RGBA8I),at===a.SHORT&&(vt=a.RGBA16I),at===a.INT&&(vt=a.RGBA32I)),R===a.RGB&&at===a.UNSIGNED_INT_5_9_9_9_REV&&(vt=a.RGB9_E5),R===a.RGBA){const Xt=bt?mf:Pe.getTransfer(pt);at===a.FLOAT&&(vt=a.RGBA32F),at===a.HALF_FLOAT&&(vt=a.RGBA16F),at===a.UNSIGNED_BYTE&&(vt=Xt===qe?a.SRGB8_ALPHA8:a.RGBA8),at===a.UNSIGNED_SHORT_4_4_4_4&&(vt=a.RGBA4),at===a.UNSIGNED_SHORT_5_5_5_1&&(vt=a.RGB5_A1)}return(vt===a.R16F||vt===a.R32F||vt===a.RG16F||vt===a.RG32F||vt===a.RGBA16F||vt===a.RGBA32F)&&t.get("EXT_color_buffer_float"),vt}function C(O,R){let at;return O?R===null||R===xr||R===Vo?at=a.DEPTH24_STENCIL8:R===Da?at=a.DEPTH32F_STENCIL8:R===lc&&(at=a.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):R===null||R===xr||R===Vo?at=a.DEPTH_COMPONENT24:R===Da?at=a.DEPTH_COMPONENT32F:R===lc&&(at=a.DEPTH_COMPONENT16),at}function V(O,R){return S(O)===!0||O.isFramebufferTexture&&O.minFilter!==Hi&&O.minFilter!==$i?Math.log2(Math.max(R.width,R.height))+1:O.mipmaps!==void 0&&O.mipmaps.length>0?O.mipmaps.length:O.isCompressedTexture&&Array.isArray(O.image)?R.mipmaps.length:1}function L(O){const R=O.target;R.removeEventListener("dispose",L),G(R),R.isVideoTexture&&v.delete(R)}function P(O){const R=O.target;R.removeEventListener("dispose",P),N(R)}function G(O){const R=s.get(O);if(R.__webglInit===void 0)return;const at=O.source,pt=x.get(at);if(pt){const bt=pt[R.__cacheKey];bt.usedTimes--,bt.usedTimes===0&&U(O),Object.keys(pt).length===0&&x.delete(at)}s.remove(O)}function U(O){const R=s.get(O);a.deleteTexture(R.__webglTexture);const at=O.source,pt=x.get(at);delete pt[R.__cacheKey],f.memory.textures--}function N(O){const R=s.get(O);if(O.depthTexture&&(O.depthTexture.dispose(),s.remove(O.depthTexture)),O.isWebGLCubeRenderTarget)for(let pt=0;pt<6;pt++){if(Array.isArray(R.__webglFramebuffer[pt]))for(let bt=0;bt<R.__webglFramebuffer[pt].length;bt++)a.deleteFramebuffer(R.__webglFramebuffer[pt][bt]);else a.deleteFramebuffer(R.__webglFramebuffer[pt]);R.__webglDepthbuffer&&a.deleteRenderbuffer(R.__webglDepthbuffer[pt])}else{if(Array.isArray(R.__webglFramebuffer))for(let pt=0;pt<R.__webglFramebuffer.length;pt++)a.deleteFramebuffer(R.__webglFramebuffer[pt]);else a.deleteFramebuffer(R.__webglFramebuffer);if(R.__webglDepthbuffer&&a.deleteRenderbuffer(R.__webglDepthbuffer),R.__webglMultisampledFramebuffer&&a.deleteFramebuffer(R.__webglMultisampledFramebuffer),R.__webglColorRenderbuffer)for(let pt=0;pt<R.__webglColorRenderbuffer.length;pt++)R.__webglColorRenderbuffer[pt]&&a.deleteRenderbuffer(R.__webglColorRenderbuffer[pt]);R.__webglDepthRenderbuffer&&a.deleteRenderbuffer(R.__webglDepthRenderbuffer)}const at=O.textures;for(let pt=0,bt=at.length;pt<bt;pt++){const vt=s.get(at[pt]);vt.__webglTexture&&(a.deleteTexture(vt.__webglTexture),f.memory.textures--),s.remove(at[pt])}s.remove(O)}let H=0;function ut(){H=0}function ot(){const O=H;return O>=o.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+O+" texture units while this GPU supports only "+o.maxTextures),H+=1,O}function mt(O){const R=[];return R.push(O.wrapS),R.push(O.wrapT),R.push(O.wrapR||0),R.push(O.magFilter),R.push(O.minFilter),R.push(O.anisotropy),R.push(O.internalFormat),R.push(O.format),R.push(O.type),R.push(O.generateMipmaps),R.push(O.premultiplyAlpha),R.push(O.flipY),R.push(O.unpackAlignment),R.push(O.colorSpace),R.join()}function ct(O,R){const at=s.get(O);if(O.isVideoTexture&&Qt(O),O.isRenderTargetTexture===!1&&O.version>0&&at.__version!==O.version){const pt=O.image;if(pt===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(pt.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{q(at,O,R);return}}n.bindTexture(a.TEXTURE_2D,at.__webglTexture,a.TEXTURE0+R)}function B(O,R){const at=s.get(O);if(O.version>0&&at.__version!==O.version){q(at,O,R);return}n.bindTexture(a.TEXTURE_2D_ARRAY,at.__webglTexture,a.TEXTURE0+R)}function Z(O,R){const at=s.get(O);if(O.version>0&&at.__version!==O.version){q(at,O,R);return}n.bindTexture(a.TEXTURE_3D,at.__webglTexture,a.TEXTURE0+R)}function $(O,R){const at=s.get(O);if(O.version>0&&at.__version!==O.version){ft(at,O,R);return}n.bindTexture(a.TEXTURE_CUBE_MAP,at.__webglTexture,a.TEXTURE0+R)}const Et={[Xp]:a.REPEAT,[cr]:a.CLAMP_TO_EDGE,[qp]:a.MIRRORED_REPEAT},At={[Hi]:a.NEAREST,[iT]:a.NEAREST_MIPMAP_NEAREST,[Ou]:a.NEAREST_MIPMAP_LINEAR,[$i]:a.LINEAR,[Fh]:a.LINEAR_MIPMAP_NEAREST,[ur]:a.LINEAR_MIPMAP_LINEAR},z={[lT]:a.NEVER,[pT]:a.ALWAYS,[cT]:a.LESS,[$x]:a.LEQUAL,[uT]:a.EQUAL,[hT]:a.GEQUAL,[fT]:a.GREATER,[dT]:a.NOTEQUAL};function nt(O,R){if(R.type===Da&&t.has("OES_texture_float_linear")===!1&&(R.magFilter===$i||R.magFilter===Fh||R.magFilter===Ou||R.magFilter===ur||R.minFilter===$i||R.minFilter===Fh||R.minFilter===Ou||R.minFilter===ur)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),a.texParameteri(O,a.TEXTURE_WRAP_S,Et[R.wrapS]),a.texParameteri(O,a.TEXTURE_WRAP_T,Et[R.wrapT]),(O===a.TEXTURE_3D||O===a.TEXTURE_2D_ARRAY)&&a.texParameteri(O,a.TEXTURE_WRAP_R,Et[R.wrapR]),a.texParameteri(O,a.TEXTURE_MAG_FILTER,At[R.magFilter]),a.texParameteri(O,a.TEXTURE_MIN_FILTER,At[R.minFilter]),R.compareFunction&&(a.texParameteri(O,a.TEXTURE_COMPARE_MODE,a.COMPARE_REF_TO_TEXTURE),a.texParameteri(O,a.TEXTURE_COMPARE_FUNC,z[R.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(R.magFilter===Hi||R.minFilter!==Ou&&R.minFilter!==ur||R.type===Da&&t.has("OES_texture_float_linear")===!1)return;if(R.anisotropy>1||s.get(R).__currentAnisotropy){const at=t.get("EXT_texture_filter_anisotropic");a.texParameterf(O,at.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(R.anisotropy,o.getMaxAnisotropy())),s.get(R).__currentAnisotropy=R.anisotropy}}}function St(O,R){let at=!1;O.__webglInit===void 0&&(O.__webglInit=!0,R.addEventListener("dispose",L));const pt=R.source;let bt=x.get(pt);bt===void 0&&(bt={},x.set(pt,bt));const vt=mt(R);if(vt!==O.__cacheKey){bt[vt]===void 0&&(bt[vt]={texture:a.createTexture(),usedTimes:0},f.memory.textures++,at=!0),bt[vt].usedTimes++;const Xt=bt[O.__cacheKey];Xt!==void 0&&(bt[O.__cacheKey].usedTimes--,Xt.usedTimes===0&&U(R)),O.__cacheKey=vt,O.__webglTexture=bt[vt].texture}return at}function q(O,R,at){let pt=a.TEXTURE_2D;(R.isDataArrayTexture||R.isCompressedArrayTexture)&&(pt=a.TEXTURE_2D_ARRAY),R.isData3DTexture&&(pt=a.TEXTURE_3D);const bt=St(O,R),vt=R.source;n.bindTexture(pt,O.__webglTexture,a.TEXTURE0+at);const Xt=s.get(vt);if(vt.version!==Xt.__version||bt===!0){n.activeTexture(a.TEXTURE0+at);const Nt=Pe.getPrimaries(Pe.workingColorSpace),Bt=R.colorSpace===vs?null:Pe.getPrimaries(R.colorSpace),Me=R.colorSpace===vs||Nt===Bt?a.NONE:a.BROWSER_DEFAULT_WEBGL;a.pixelStorei(a.UNPACK_FLIP_Y_WEBGL,R.flipY),a.pixelStorei(a.UNPACK_PREMULTIPLY_ALPHA_WEBGL,R.premultiplyAlpha),a.pixelStorei(a.UNPACK_ALIGNMENT,R.unpackAlignment),a.pixelStorei(a.UNPACK_COLORSPACE_CONVERSION_WEBGL,Me);let Ct=T(R.image,!1,o.maxTextureSize);Ct=Be(R,Ct);const Ht=c.convert(R.format,R.colorSpace),Zt=c.convert(R.type);let qt=D(R.internalFormat,Ht,Zt,R.colorSpace,R.isVideoTexture);nt(pt,R);let Ot;const ne=R.mipmaps,le=R.isVideoTexture!==!0,Ve=Xt.__version===void 0||bt===!0,Y=vt.dataReady,Rt=V(R,Ct);if(R.isDepthTexture)qt=C(R.format===jo,R.type),Ve&&(le?n.texStorage2D(a.TEXTURE_2D,1,qt,Ct.width,Ct.height):n.texImage2D(a.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,null));else if(R.isDataTexture)if(ne.length>0){le&&Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data);R.generateMipmaps=!1}else le?(Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,Ct.width,Ct.height),Y&&n.texSubImage2D(a.TEXTURE_2D,0,0,0,Ct.width,Ct.height,Ht,Zt,Ct.data)):n.texImage2D(a.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,Ct.data);else if(R.isCompressedTexture)if(R.isCompressedArrayTexture){le&&Ve&&n.texStorage3D(a.TEXTURE_2D_ARRAY,Rt,qt,ne[0].width,ne[0].height,Ct.depth);for(let dt=0,yt=ne.length;dt<yt;dt++)if(Ot=ne[dt],R.format!==Fi)if(Ht!==null)if(le){if(Y)if(R.layerUpdates.size>0){const wt=Cy(Ot.width,Ot.height,R.format,R.type);for(const Dt of R.layerUpdates){const ie=Ot.data.subarray(Dt*wt/Ot.data.BYTES_PER_ELEMENT,(Dt+1)*wt/Ot.data.BYTES_PER_ELEMENT);n.compressedTexSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,Dt,Ot.width,Ot.height,1,Ht,ie)}R.clearLayerUpdates()}else n.compressedTexSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Ot.data)}else n.compressedTexImage3D(a.TEXTURE_2D_ARRAY,dt,qt,Ot.width,Ot.height,Ct.depth,0,Ot.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else le?Y&&n.texSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Zt,Ot.data):n.texImage3D(a.TEXTURE_2D_ARRAY,dt,qt,Ot.width,Ot.height,Ct.depth,0,Ht,Zt,Ot.data)}else{le&&Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],R.format!==Fi?Ht!==null?le?Y&&n.compressedTexSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Ot.data):n.compressedTexImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ot.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data)}else if(R.isDataArrayTexture)if(le){if(Ve&&n.texStorage3D(a.TEXTURE_2D_ARRAY,Rt,qt,Ct.width,Ct.height,Ct.depth),Y)if(R.layerUpdates.size>0){const dt=Cy(Ct.width,Ct.height,R.format,R.type);for(const yt of R.layerUpdates){const wt=Ct.data.subarray(yt*dt/Ct.data.BYTES_PER_ELEMENT,(yt+1)*dt/Ct.data.BYTES_PER_ELEMENT);n.texSubImage3D(a.TEXTURE_2D_ARRAY,0,0,0,yt,Ct.width,Ct.height,1,Ht,Zt,wt)}R.clearLayerUpdates()}else n.texSubImage3D(a.TEXTURE_2D_ARRAY,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)}else n.texImage3D(a.TEXTURE_2D_ARRAY,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(R.isData3DTexture)le?(Ve&&n.texStorage3D(a.TEXTURE_3D,Rt,qt,Ct.width,Ct.height,Ct.depth),Y&&n.texSubImage3D(a.TEXTURE_3D,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)):n.texImage3D(a.TEXTURE_3D,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(R.isFramebufferTexture){if(Ve)if(le)n.texStorage2D(a.TEXTURE_2D,Rt,qt,Ct.width,Ct.height);else{let dt=Ct.width,yt=Ct.height;for(let wt=0;wt<Rt;wt++)n.texImage2D(a.TEXTURE_2D,wt,qt,dt,yt,0,Ht,Zt,null),dt>>=1,yt>>=1}}else if(ne.length>0){if(le&&Ve){const dt=Yt(ne[0]);n.texStorage2D(a.TEXTURE_2D,Rt,qt,dt.width,dt.height)}for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ht,Zt,Ot):n.texImage2D(a.TEXTURE_2D,dt,qt,Ht,Zt,Ot);R.generateMipmaps=!1}else if(le){if(Ve){const dt=Yt(Ct);n.texStorage2D(a.TEXTURE_2D,Rt,qt,dt.width,dt.height)}Y&&n.texSubImage2D(a.TEXTURE_2D,0,0,0,Ht,Zt,Ct)}else n.texImage2D(a.TEXTURE_2D,0,qt,Ht,Zt,Ct);S(R)&&y(pt),Xt.__version=vt.version,R.onUpdate&&R.onUpdate(R)}O.__version=R.version}function ft(O,R,at){if(R.image.length!==6)return;const pt=St(O,R),bt=R.source;n.bindTexture(a.TEXTURE_CUBE_MAP,O.__webglTexture,a.TEXTURE0+at);const vt=s.get(bt);if(bt.version!==vt.__version||pt===!0){n.activeTexture(a.TEXTURE0+at);const Xt=Pe.getPrimaries(Pe.workingColorSpace),Nt=R.colorSpace===vs?null:Pe.getPrimaries(R.colorSpace),Bt=R.colorSpace===vs||Xt===Nt?a.NONE:a.BROWSER_DEFAULT_WEBGL;a.pixelStorei(a.UNPACK_FLIP_Y_WEBGL,R.flipY),a.pixelStorei(a.UNPACK_PREMULTIPLY_ALPHA_WEBGL,R.premultiplyAlpha),a.pixelStorei(a.UNPACK_ALIGNMENT,R.unpackAlignment),a.pixelStorei(a.UNPACK_COLORSPACE_CONVERSION_WEBGL,Bt);const Me=R.isCompressedTexture||R.image[0].isCompressedTexture,Ct=R.image[0]&&R.image[0].isDataTexture,Ht=[];for(let yt=0;yt<6;yt++)!Me&&!Ct?Ht[yt]=T(R.image[yt],!0,o.maxCubemapSize):Ht[yt]=Ct?R.image[yt].image:R.image[yt],Ht[yt]=Be(R,Ht[yt]);const Zt=Ht[0],qt=c.convert(R.format,R.colorSpace),Ot=c.convert(R.type),ne=D(R.internalFormat,qt,Ot,R.colorSpace),le=R.isVideoTexture!==!0,Ve=vt.__version===void 0||pt===!0,Y=bt.dataReady;let Rt=V(R,Zt);nt(a.TEXTURE_CUBE_MAP,R);let dt;if(Me){le&&Ve&&n.texStorage2D(a.TEXTURE_CUBE_MAP,Rt,ne,Zt.width,Zt.height);for(let yt=0;yt<6;yt++){dt=Ht[yt].mipmaps;for(let wt=0;wt<dt.length;wt++){const Dt=dt[wt];R.format!==Fi?qt!==null?le?Y&&n.compressedTexSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Dt.width,Dt.height,qt,Dt.data):n.compressedTexImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Dt.width,Dt.height,0,Dt.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Dt.width,Dt.height,qt,Ot,Dt.data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Dt.width,Dt.height,0,qt,Ot,Dt.data)}}}else{if(dt=R.mipmaps,le&&Ve){dt.length>0&&Rt++;const yt=Yt(Ht[0]);n.texStorage2D(a.TEXTURE_CUBE_MAP,Rt,ne,yt.width,yt.height)}for(let yt=0;yt<6;yt++)if(Ct){le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,Ht[yt].width,Ht[yt].height,qt,Ot,Ht[yt].data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,Ht[yt].width,Ht[yt].height,0,qt,Ot,Ht[yt].data);for(let wt=0;wt<dt.length;wt++){const ie=dt[wt].image[yt].image;le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,ie.width,ie.height,qt,Ot,ie.data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,ie.width,ie.height,0,qt,Ot,ie.data)}}else{le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,qt,Ot,Ht[yt]):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,qt,Ot,Ht[yt]);for(let wt=0;wt<dt.length;wt++){const Dt=dt[wt];le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,qt,Ot,Dt.image[yt]):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,qt,Ot,Dt.image[yt])}}}S(R)&&y(a.TEXTURE_CUBE_MAP),vt.__version=bt.version,R.onUpdate&&R.onUpdate(R)}O.__version=R.version}function Tt(O,R,at,pt,bt,vt){const Xt=c.convert(at.format,at.colorSpace),Nt=c.convert(at.type),Bt=D(at.internalFormat,Xt,Nt,at.colorSpace),Me=s.get(R),Ct=s.get(at);if(Ct.__renderTarget=R,!Me.__hasExternalTextures){const Ht=Math.max(1,R.width>>vt),Zt=Math.max(1,R.height>>vt);bt===a.TEXTURE_3D||bt===a.TEXTURE_2D_ARRAY?n.texImage3D(bt,vt,Bt,Ht,Zt,R.depth,0,Xt,Nt,null):n.texImage2D(bt,vt,Bt,Ht,Zt,0,Xt,Nt,null)}n.bindFramebuffer(a.FRAMEBUFFER,O),Se(R)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,pt,bt,Ct.__webglTexture,0,me(R)):(bt===a.TEXTURE_2D||bt>=a.TEXTURE_CUBE_MAP_POSITIVE_X&&bt<=a.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&a.framebufferTexture2D(a.FRAMEBUFFER,pt,bt,Ct.__webglTexture,vt),n.bindFramebuffer(a.FRAMEBUFFER,null)}function Mt(O,R,at){if(a.bindRenderbuffer(a.RENDERBUFFER,O),R.depthBuffer){const pt=R.depthTexture,bt=pt&&pt.isDepthTexture?pt.type:null,vt=C(R.stencilBuffer,bt),Xt=R.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,Nt=me(R);Se(R)?d.renderbufferStorageMultisampleEXT(a.RENDERBUFFER,Nt,vt,R.width,R.height):at?a.renderbufferStorageMultisample(a.RENDERBUFFER,Nt,vt,R.width,R.height):a.renderbufferStorage(a.RENDERBUFFER,vt,R.width,R.height),a.framebufferRenderbuffer(a.FRAMEBUFFER,Xt,a.RENDERBUFFER,O)}else{const pt=R.textures;for(let bt=0;bt<pt.length;bt++){const vt=pt[bt],Xt=c.convert(vt.format,vt.colorSpace),Nt=c.convert(vt.type),Bt=D(vt.internalFormat,Xt,Nt,vt.colorSpace),Me=me(R);at&&Se(R)===!1?a.renderbufferStorageMultisample(a.RENDERBUFFER,Me,Bt,R.width,R.height):Se(R)?d.renderbufferStorageMultisampleEXT(a.RENDERBUFFER,Me,Bt,R.width,R.height):a.renderbufferStorage(a.RENDERBUFFER,Bt,R.width,R.height)}}a.bindRenderbuffer(a.RENDERBUFFER,null)}function Ft(O,R){if(R&&R.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(n.bindFramebuffer(a.FRAMEBUFFER,O),!(R.depthTexture&&R.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const pt=s.get(R.depthTexture);pt.__renderTarget=R,(!pt.__webglTexture||R.depthTexture.image.width!==R.width||R.depthTexture.image.height!==R.height)&&(R.depthTexture.image.width=R.width,R.depthTexture.image.height=R.height,R.depthTexture.needsUpdate=!0),ct(R.depthTexture,0);const bt=pt.__webglTexture,vt=me(R);if(R.depthTexture.format===bo)Se(R)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,a.DEPTH_ATTACHMENT,a.TEXTURE_2D,bt,0,vt):a.framebufferTexture2D(a.FRAMEBUFFER,a.DEPTH_ATTACHMENT,a.TEXTURE_2D,bt,0);else if(R.depthTexture.format===jo)Se(R)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,a.DEPTH_STENCIL_ATTACHMENT,a.TEXTURE_2D,bt,0,vt):a.framebufferTexture2D(a.FRAMEBUFFER,a.DEPTH_STENCIL_ATTACHMENT,a.TEXTURE_2D,bt,0);else throw new Error("Unknown depthTexture format")}function Vt(O){const R=s.get(O),at=O.isWebGLCubeRenderTarget===!0;if(R.__boundDepthTexture!==O.depthTexture){const pt=O.depthTexture;if(R.__depthDisposeCallback&&R.__depthDisposeCallback(),pt){const bt=()=>{delete R.__boundDepthTexture,delete R.__depthDisposeCallback,pt.removeEventListener("dispose",bt)};pt.addEventListener("dispose",bt),R.__depthDisposeCallback=bt}R.__boundDepthTexture=pt}if(O.depthTexture&&!R.__autoAllocateDepthBuffer){if(at)throw new Error("target.depthTexture not supported in Cube render targets");Ft(R.__webglFramebuffer,O)}else if(at){R.__webglDepthbuffer=[];for(let pt=0;pt<6;pt++)if(n.bindFramebuffer(a.FRAMEBUFFER,R.__webglFramebuffer[pt]),R.__webglDepthbuffer[pt]===void 0)R.__webglDepthbuffer[pt]=a.createRenderbuffer(),Mt(R.__webglDepthbuffer[pt],O,!1);else{const bt=O.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,vt=R.__webglDepthbuffer[pt];a.bindRenderbuffer(a.RENDERBUFFER,vt),a.framebufferRenderbuffer(a.FRAMEBUFFER,bt,a.RENDERBUFFER,vt)}}else if(n.bindFramebuffer(a.FRAMEBUFFER,R.__webglFramebuffer),R.__webglDepthbuffer===void 0)R.__webglDepthbuffer=a.createRenderbuffer(),Mt(R.__webglDepthbuffer,O,!1);else{const pt=O.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,bt=R.__webglDepthbuffer;a.bindRenderbuffer(a.RENDERBUFFER,bt),a.framebufferRenderbuffer(a.FRAMEBUFFER,pt,a.RENDERBUFFER,bt)}n.bindFramebuffer(a.FRAMEBUFFER,null)}function oe(O,R,at){const pt=s.get(O);R!==void 0&&Tt(pt.__webglFramebuffer,O,O.texture,a.COLOR_ATTACHMENT0,a.TEXTURE_2D,0),at!==void 0&&Vt(O)}function Ge(O){const R=O.texture,at=s.get(O),pt=s.get(R);O.addEventListener("dispose",P);const bt=O.textures,vt=O.isWebGLCubeRenderTarget===!0,Xt=bt.length>1;if(Xt||(pt.__webglTexture===void 0&&(pt.__webglTexture=a.createTexture()),pt.__version=R.version,f.memory.textures++),vt){at.__webglFramebuffer=[];for(let Nt=0;Nt<6;Nt++)if(R.mipmaps&&R.mipmaps.length>0){at.__webglFramebuffer[Nt]=[];for(let Bt=0;Bt<R.mipmaps.length;Bt++)at.__webglFramebuffer[Nt][Bt]=a.createFramebuffer()}else at.__webglFramebuffer[Nt]=a.createFramebuffer()}else{if(R.mipmaps&&R.mipmaps.length>0){at.__webglFramebuffer=[];for(let Nt=0;Nt<R.mipmaps.length;Nt++)at.__webglFramebuffer[Nt]=a.createFramebuffer()}else at.__webglFramebuffer=a.createFramebuffer();if(Xt)for(let Nt=0,Bt=bt.length;Nt<Bt;Nt++){const Me=s.get(bt[Nt]);Me.__webglTexture===void 0&&(Me.__webglTexture=a.createTexture(),f.memory.textures++)}if(O.samples>0&&Se(O)===!1){at.__webglMultisampledFramebuffer=a.createFramebuffer(),at.__webglColorRenderbuffer=[],n.bindFramebuffer(a.FRAMEBUFFER,at.__webglMultisampledFramebuffer);for(let Nt=0;Nt<bt.length;Nt++){const Bt=bt[Nt];at.__webglColorRenderbuffer[Nt]=a.createRenderbuffer(),a.bindRenderbuffer(a.RENDERBUFFER,at.__webglColorRenderbuffer[Nt]);const Me=c.convert(Bt.format,Bt.colorSpace),Ct=c.convert(Bt.type),Ht=D(Bt.internalFormat,Me,Ct,Bt.colorSpace,O.isXRRenderTarget===!0),Zt=me(O);a.renderbufferStorageMultisample(a.RENDERBUFFER,Zt,Ht,O.width,O.height),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Nt,a.RENDERBUFFER,at.__webglColorRenderbuffer[Nt])}a.bindRenderbuffer(a.RENDERBUFFER,null),O.depthBuffer&&(at.__webglDepthRenderbuffer=a.createRenderbuffer(),Mt(at.__webglDepthRenderbuffer,O,!0)),n.bindFramebuffer(a.FRAMEBUFFER,null)}}if(vt){n.bindTexture(a.TEXTURE_CUBE_MAP,pt.__webglTexture),nt(a.TEXTURE_CUBE_MAP,R);for(let Nt=0;Nt<6;Nt++)if(R.mipmaps&&R.mipmaps.length>0)for(let Bt=0;Bt<R.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Nt][Bt],O,R,a.COLOR_ATTACHMENT0,a.TEXTURE_CUBE_MAP_POSITIVE_X+Nt,Bt);else Tt(at.__webglFramebuffer[Nt],O,R,a.COLOR_ATTACHMENT0,a.TEXTURE_CUBE_MAP_POSITIVE_X+Nt,0);S(R)&&y(a.TEXTURE_CUBE_MAP),n.unbindTexture()}else if(Xt){for(let Nt=0,Bt=bt.length;Nt<Bt;Nt++){const Me=bt[Nt],Ct=s.get(Me);n.bindTexture(a.TEXTURE_2D,Ct.__webglTexture),nt(a.TEXTURE_2D,Me),Tt(at.__webglFramebuffer,O,Me,a.COLOR_ATTACHMENT0+Nt,a.TEXTURE_2D,0),S(Me)&&y(a.TEXTURE_2D)}n.unbindTexture()}else{let Nt=a.TEXTURE_2D;if((O.isWebGL3DRenderTarget||O.isWebGLArrayRenderTarget)&&(Nt=O.isWebGL3DRenderTarget?a.TEXTURE_3D:a.TEXTURE_2D_ARRAY),n.bindTexture(Nt,pt.__webglTexture),nt(Nt,R),R.mipmaps&&R.mipmaps.length>0)for(let Bt=0;Bt<R.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Bt],O,R,a.COLOR_ATTACHMENT0,Nt,Bt);else Tt(at.__webglFramebuffer,O,R,a.COLOR_ATTACHMENT0,Nt,0);S(R)&&y(Nt),n.unbindTexture()}O.depthBuffer&&Vt(O)}function ve(O){const R=O.textures;for(let at=0,pt=R.length;at<pt;at++){const bt=R[at];if(S(bt)){const vt=I(O),Xt=s.get(bt).__webglTexture;n.bindTexture(vt,Xt),y(vt),n.unbindTexture()}}}const $e=[],j=[];function Pn(O){if(O.samples>0){if(Se(O)===!1){const R=O.textures,at=O.width,pt=O.height;let bt=a.COLOR_BUFFER_BIT;const vt=O.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,Xt=s.get(O),Nt=R.length>1;if(Nt)for(let Bt=0;Bt<R.length;Bt++)n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.RENDERBUFFER,null),n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglFramebuffer),a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.TEXTURE_2D,null,0);n.bindFramebuffer(a.READ_FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),n.bindFramebuffer(a.DRAW_FRAMEBUFFER,Xt.__webglFramebuffer);for(let Bt=0;Bt<R.length;Bt++){if(O.resolveDepthBuffer&&(O.depthBuffer&&(bt|=a.DEPTH_BUFFER_BIT),O.stencilBuffer&&O.resolveStencilBuffer&&(bt|=a.STENCIL_BUFFER_BIT)),Nt){a.framebufferRenderbuffer(a.READ_FRAMEBUFFER,a.COLOR_ATTACHMENT0,a.RENDERBUFFER,Xt.__webglColorRenderbuffer[Bt]);const Me=s.get(R[Bt]).__webglTexture;a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0,a.TEXTURE_2D,Me,0)}a.blitFramebuffer(0,0,at,pt,0,0,at,pt,bt,a.NEAREST),p===!0&&($e.length=0,j.length=0,$e.push(a.COLOR_ATTACHMENT0+Bt),O.depthBuffer&&O.resolveDepthBuffer===!1&&($e.push(vt),j.push(vt),a.invalidateFramebuffer(a.DRAW_FRAMEBUFFER,j)),a.invalidateFramebuffer(a.READ_FRAMEBUFFER,$e))}if(n.bindFramebuffer(a.READ_FRAMEBUFFER,null),n.bindFramebuffer(a.DRAW_FRAMEBUFFER,null),Nt)for(let Bt=0;Bt<R.length;Bt++){n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.RENDERBUFFER,Xt.__webglColorRenderbuffer[Bt]);const Me=s.get(R[Bt]).__webglTexture;n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglFramebuffer),a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.TEXTURE_2D,Me,0)}n.bindFramebuffer(a.DRAW_FRAMEBUFFER,Xt.__webglMultisampledFramebuffer)}else if(O.depthBuffer&&O.resolveDepthBuffer===!1&&p){const R=O.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT;a.invalidateFramebuffer(a.DRAW_FRAMEBUFFER,[R])}}}function me(O){return Math.min(o.maxSamples,O.samples)}function Se(O){const R=s.get(O);return O.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&R.__useRenderToTexture!==!1}function Qt(O){const R=f.render.frame;v.get(O)!==R&&(v.set(O,R),O.update())}function Be(O,R){const at=O.colorSpace,pt=O.format,bt=O.type;return O.isCompressedTexture===!0||O.isVideoTexture===!0||at!==ko&&at!==vs&&(Pe.getTransfer(at)===qe?(pt!==Fi||bt!==Ia)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",at)),R}function Yt(O){return typeof HTMLImageElement<"u"&&O instanceof HTMLImageElement?(m.width=O.naturalWidth||O.width,m.height=O.naturalHeight||O.height):typeof VideoFrame<"u"&&O instanceof VideoFrame?(m.width=O.displayWidth,m.height=O.displayHeight):(m.width=O.width,m.height=O.height),m}this.allocateTextureUnit=ot,this.resetTextureUnits=ut,this.setTexture2D=ct,this.setTexture2DArray=B,this.setTexture3D=Z,this.setTextureCube=$,this.rebindTextures=oe,this.setupRenderTarget=Ge,this.updateRenderTargetMipmap=ve,this.updateMultisampleRenderTarget=Pn,this.setupDepthRenderbuffer=Vt,this.setupFrameBufferTexture=Tt,this.useMultisampledRTT=Se}function eN(a,t){function n(s,o=vs){let c;const f=Pe.getTransfer(o);if(s===Ia)return a.UNSIGNED_BYTE;if(s===Lm)return a.UNSIGNED_SHORT_4_4_4_4;if(s===Om)return a.UNSIGNED_SHORT_5_5_5_1;if(s===Xx)return a.UNSIGNED_INT_5_9_9_9_REV;if(s===jx)return a.BYTE;if(s===kx)return a.SHORT;if(s===lc)return a.UNSIGNED_SHORT;if(s===Um)return a.INT;if(s===xr)return a.UNSIGNED_INT;if(s===Da)return a.FLOAT;if(s===Pa)return a.HALF_FLOAT;if(s===qx)return a.ALPHA;if(s===Wx)return a.RGB;if(s===Fi)return a.RGBA;if(s===Yx)return a.LUMINANCE;if(s===Qx)return a.LUMINANCE_ALPHA;if(s===bo)return a.DEPTH_COMPONENT;if(s===jo)return a.DEPTH_STENCIL;if(s===Zx)return a.RED;if(s===Pm)return a.RED_INTEGER;if(s===Kx)return a.RG;if(s===zm)return a.RG_INTEGER;if(s===Im)return a.RGBA_INTEGER;if(s===sf||s===rf||s===of||s===lf)if(f===qe)if(c=t.get("WEBGL_compressed_texture_s3tc_srgb"),c!==null){if(s===sf)return c.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===rf)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===of)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===lf)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(c=t.get("WEBGL_compressed_texture_s3tc"),c!==null){if(s===sf)return c.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===rf)return c.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===of)return c.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===lf)return c.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===Wp||s===Yp||s===Qp||s===Zp)if(c=t.get("WEBGL_compressed_texture_pvrtc"),c!==null){if(s===Wp)return c.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===Yp)return c.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===Qp)return c.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===Zp)return c.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===Kp||s===Jp||s===$p)if(c=t.get("WEBGL_compressed_texture_etc"),c!==null){if(s===Kp||s===Jp)return f===qe?c.COMPRESSED_SRGB8_ETC2:c.COMPRESSED_RGB8_ETC2;if(s===$p)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:c.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(s===tm||s===em||s===nm||s===im||s===am||s===sm||s===rm||s===om||s===lm||s===cm||s===um||s===fm||s===dm||s===hm)if(c=t.get("WEBGL_compressed_texture_astc"),c!==null){if(s===tm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:c.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===em)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:c.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===nm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:c.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===im)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:c.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===am)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:c.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===sm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:c.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===rm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:c.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===om)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:c.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===lm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:c.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===cm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:c.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===um)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:c.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===fm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:c.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===dm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:c.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===hm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:c.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===cf||s===pm||s===mm)if(c=t.get("EXT_texture_compression_bptc"),c!==null){if(s===cf)return f===qe?c.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:c.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(s===pm)return c.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(s===mm)return c.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(s===Jx||s===gm||s===vm||s===_m)if(c=t.get("EXT_texture_compression_rgtc"),c!==null){if(s===cf)return c.COMPRESSED_RED_RGTC1_EXT;if(s===gm)return c.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===vm)return c.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===_m)return c.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===Vo?a.UNSIGNED_INT_24_8:a[s]!==void 0?a[s]:null}return{convert:n}}const nN={type:"move"};class vp{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new So,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new So,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new W,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new W),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new So,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new W,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new W),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const n=this._hand;if(n)for(const s of t.hand.values())this._getHandJoint(n,s)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,n,s){let o=null,c=null,f=null;const d=this._targetRay,p=this._grip,m=this._hand;if(t&&n.session.visibilityState!=="visible-blurred"){if(m&&t.hand){f=!0;for(const T of t.hand.values()){const S=n.getJointPose(T,s),y=this._getHandJoint(m,T);S!==null&&(y.matrix.fromArray(S.transform.matrix),y.matrix.decompose(y.position,y.rotation,y.scale),y.matrixWorldNeedsUpdate=!0,y.jointRadius=S.radius),y.visible=S!==null}const v=m.joints["index-finger-tip"],_=m.joints["thumb-tip"],x=v.position.distanceTo(_.position),E=.02,M=.005;m.inputState.pinching&&x>E+M?(m.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!m.inputState.pinching&&x<=E-M&&(m.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else p!==null&&t.gripSpace&&(c=n.getPose(t.gripSpace,s),c!==null&&(p.matrix.fromArray(c.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,c.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(c.linearVelocity)):p.hasLinearVelocity=!1,c.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(c.angularVelocity)):p.hasAngularVelocity=!1));d!==null&&(o=n.getPose(t.targetRaySpace,s),o===null&&c!==null&&(o=c),o!==null&&(d.matrix.fromArray(o.transform.matrix),d.matrix.decompose(d.position,d.rotation,d.scale),d.matrixWorldNeedsUpdate=!0,o.linearVelocity?(d.hasLinearVelocity=!0,d.linearVelocity.copy(o.linearVelocity)):d.hasLinearVelocity=!1,o.angularVelocity?(d.hasAngularVelocity=!0,d.angularVelocity.copy(o.angularVelocity)):d.hasAngularVelocity=!1,this.dispatchEvent(nN)))}return d!==null&&(d.visible=o!==null),p!==null&&(p.visible=c!==null),m!==null&&(m.visible=f!==null),this}_getHandJoint(t,n){if(t.joints[n.jointName]===void 0){const s=new So;s.matrixAutoUpdate=!1,s.visible=!1,t.joints[n.jointName]=s,t.add(s)}return t.joints[n.jointName]}}const iN=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,aN=`
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

}`;class sN{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,n,s){if(this.texture===null){const o=new ai,c=t.properties.get(o);c.__webglTexture=n.texture,(n.depthNear!=s.depthNear||n.depthFar!=s.depthFar)&&(this.depthNear=n.depthNear,this.depthFar=n.depthFar),this.texture=o}}getMesh(t){if(this.texture!==null&&this.mesh===null){const n=t.cameras[0].viewport,s=new Yn({vertexShader:iN,fragmentShader:aN,uniforms:{depthColor:{value:this.texture},depthWidth:{value:n.z},depthHeight:{value:n.w}}});this.mesh=new Wn(new Mf(20,20),s)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class rN extends Wo{constructor(t,n){super();const s=this;let o=null,c=1,f=null,d="local-floor",p=1,m=null,v=null,_=null,x=null,E=null,M=null;const T=new sN,S=n.getContextAttributes();let y=null,I=null;const D=[],C=[],V=new Wt;let L=null;const P=new _i;P.viewport=new We;const G=new _i;G.viewport=new We;const U=[P,G],N=new CA;let H=null,ut=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(q){let ft=D[q];return ft===void 0&&(ft=new vp,D[q]=ft),ft.getTargetRaySpace()},this.getControllerGrip=function(q){let ft=D[q];return ft===void 0&&(ft=new vp,D[q]=ft),ft.getGripSpace()},this.getHand=function(q){let ft=D[q];return ft===void 0&&(ft=new vp,D[q]=ft),ft.getHandSpace()};function ot(q){const ft=C.indexOf(q.inputSource);if(ft===-1)return;const Tt=D[ft];Tt!==void 0&&(Tt.update(q.inputSource,q.frame,m||f),Tt.dispatchEvent({type:q.type,data:q.inputSource}))}function mt(){o.removeEventListener("select",ot),o.removeEventListener("selectstart",ot),o.removeEventListener("selectend",ot),o.removeEventListener("squeeze",ot),o.removeEventListener("squeezestart",ot),o.removeEventListener("squeezeend",ot),o.removeEventListener("end",mt),o.removeEventListener("inputsourceschange",ct);for(let q=0;q<D.length;q++){const ft=C[q];ft!==null&&(C[q]=null,D[q].disconnect(ft))}H=null,ut=null,T.reset(),t.setRenderTarget(y),E=null,x=null,_=null,o=null,I=null,St.stop(),s.isPresenting=!1,t.setPixelRatio(L),t.setSize(V.width,V.height,!1),s.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(q){c=q,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(q){d=q,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return m||f},this.setReferenceSpace=function(q){m=q},this.getBaseLayer=function(){return x!==null?x:E},this.getBinding=function(){return _},this.getFrame=function(){return M},this.getSession=function(){return o},this.setSession=async function(q){if(o=q,o!==null){if(y=t.getRenderTarget(),o.addEventListener("select",ot),o.addEventListener("selectstart",ot),o.addEventListener("selectend",ot),o.addEventListener("squeeze",ot),o.addEventListener("squeezestart",ot),o.addEventListener("squeezeend",ot),o.addEventListener("end",mt),o.addEventListener("inputsourceschange",ct),S.xrCompatible!==!0&&await n.makeXRCompatible(),L=t.getPixelRatio(),t.getSize(V),o.renderState.layers===void 0){const ft={antialias:S.antialias,alpha:!0,depth:S.depth,stencil:S.stencil,framebufferScaleFactor:c};E=new XRWebGLLayer(o,n,ft),o.updateRenderState({baseLayer:E}),t.setPixelRatio(1),t.setSize(E.framebufferWidth,E.framebufferHeight,!1),I=new Gi(E.framebufferWidth,E.framebufferHeight,{format:Fi,type:Ia,colorSpace:t.outputColorSpace,stencilBuffer:S.stencil})}else{let ft=null,Tt=null,Mt=null;S.depth&&(Mt=S.stencil?n.DEPTH24_STENCIL8:n.DEPTH_COMPONENT24,ft=S.stencil?jo:bo,Tt=S.stencil?Vo:xr);const Ft={colorFormat:n.RGBA8,depthFormat:Mt,scaleFactor:c};_=new XRWebGLBinding(o,n),x=_.createProjectionLayer(Ft),o.updateRenderState({layers:[x]}),t.setPixelRatio(1),t.setSize(x.textureWidth,x.textureHeight,!1),I=new Gi(x.textureWidth,x.textureHeight,{format:Fi,type:Ia,depthTexture:new uS(x.textureWidth,x.textureHeight,Tt,void 0,void 0,void 0,void 0,void 0,void 0,ft),stencilBuffer:S.stencil,colorSpace:t.outputColorSpace,samples:S.antialias?4:0,resolveDepthBuffer:x.ignoreDepthValues===!1})}I.isXRRenderTarget=!0,this.setFoveation(p),m=null,f=await o.requestReferenceSpace(d),St.setContext(o),St.start(),s.isPresenting=!0,s.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(o!==null)return o.environmentBlendMode},this.getDepthTexture=function(){return T.getDepthTexture()};function ct(q){for(let ft=0;ft<q.removed.length;ft++){const Tt=q.removed[ft],Mt=C.indexOf(Tt);Mt>=0&&(C[Mt]=null,D[Mt].disconnect(Tt))}for(let ft=0;ft<q.added.length;ft++){const Tt=q.added[ft];let Mt=C.indexOf(Tt);if(Mt===-1){for(let Vt=0;Vt<D.length;Vt++)if(Vt>=C.length){C.push(Tt),Mt=Vt;break}else if(C[Vt]===null){C[Vt]=Tt,Mt=Vt;break}if(Mt===-1)break}const Ft=D[Mt];Ft&&Ft.connect(Tt)}}const B=new W,Z=new W;function $(q,ft,Tt){B.setFromMatrixPosition(ft.matrixWorld),Z.setFromMatrixPosition(Tt.matrixWorld);const Mt=B.distanceTo(Z),Ft=ft.projectionMatrix.elements,Vt=Tt.projectionMatrix.elements,oe=Ft[14]/(Ft[10]-1),Ge=Ft[14]/(Ft[10]+1),ve=(Ft[9]+1)/Ft[5],$e=(Ft[9]-1)/Ft[5],j=(Ft[8]-1)/Ft[0],Pn=(Vt[8]+1)/Vt[0],me=oe*j,Se=oe*Pn,Qt=Mt/(-j+Pn),Be=Qt*-j;if(ft.matrixWorld.decompose(q.position,q.quaternion,q.scale),q.translateX(Be),q.translateZ(Qt),q.matrixWorld.compose(q.position,q.quaternion,q.scale),q.matrixWorldInverse.copy(q.matrixWorld).invert(),Ft[10]===-1)q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse);else{const Yt=oe+Qt,O=Ge+Qt,R=me-Be,at=Se+(Mt-Be),pt=ve*Ge/O*Yt,bt=$e*Ge/O*Yt;q.projectionMatrix.makePerspective(R,at,pt,bt,Yt,O),q.projectionMatrixInverse.copy(q.projectionMatrix).invert()}}function Et(q,ft){ft===null?q.matrixWorld.copy(q.matrix):q.matrixWorld.multiplyMatrices(ft.matrixWorld,q.matrix),q.matrixWorldInverse.copy(q.matrixWorld).invert()}this.updateCamera=function(q){if(o===null)return;let ft=q.near,Tt=q.far;T.texture!==null&&(T.depthNear>0&&(ft=T.depthNear),T.depthFar>0&&(Tt=T.depthFar)),N.near=G.near=P.near=ft,N.far=G.far=P.far=Tt,(H!==N.near||ut!==N.far)&&(o.updateRenderState({depthNear:N.near,depthFar:N.far}),H=N.near,ut=N.far),P.layers.mask=q.layers.mask|2,G.layers.mask=q.layers.mask|4,N.layers.mask=P.layers.mask|G.layers.mask;const Mt=q.parent,Ft=N.cameras;Et(N,Mt);for(let Vt=0;Vt<Ft.length;Vt++)Et(Ft[Vt],Mt);Ft.length===2?$(N,P,G):N.projectionMatrix.copy(P.projectionMatrix),At(q,N,Mt)};function At(q,ft,Tt){Tt===null?q.matrix.copy(ft.matrixWorld):(q.matrix.copy(Tt.matrixWorld),q.matrix.invert(),q.matrix.multiply(ft.matrixWorld)),q.matrix.decompose(q.position,q.quaternion,q.scale),q.updateMatrixWorld(!0),q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse),q.isPerspectiveCamera&&(q.fov=cc*2*Math.atan(1/q.projectionMatrix.elements[5]),q.zoom=1)}this.getCamera=function(){return N},this.getFoveation=function(){if(!(x===null&&E===null))return p},this.setFoveation=function(q){p=q,x!==null&&(x.fixedFoveation=q),E!==null&&E.fixedFoveation!==void 0&&(E.fixedFoveation=q)},this.hasDepthSensing=function(){return T.texture!==null},this.getDepthSensingMesh=function(){return T.getMesh(N)};let z=null;function nt(q,ft){if(v=ft.getViewerPose(m||f),M=ft,v!==null){const Tt=v.views;E!==null&&(t.setRenderTargetFramebuffer(I,E.framebuffer),t.setRenderTarget(I));let Mt=!1;Tt.length!==N.cameras.length&&(N.cameras.length=0,Mt=!0);for(let Vt=0;Vt<Tt.length;Vt++){const oe=Tt[Vt];let Ge=null;if(E!==null)Ge=E.getViewport(oe);else{const $e=_.getViewSubImage(x,oe);Ge=$e.viewport,Vt===0&&(t.setRenderTargetTextures(I,$e.colorTexture,x.ignoreDepthValues?void 0:$e.depthStencilTexture),t.setRenderTarget(I))}let ve=U[Vt];ve===void 0&&(ve=new _i,ve.layers.enable(Vt),ve.viewport=new We,U[Vt]=ve),ve.matrix.fromArray(oe.transform.matrix),ve.matrix.decompose(ve.position,ve.quaternion,ve.scale),ve.projectionMatrix.fromArray(oe.projectionMatrix),ve.projectionMatrixInverse.copy(ve.projectionMatrix).invert(),ve.viewport.set(Ge.x,Ge.y,Ge.width,Ge.height),Vt===0&&(N.matrix.copy(ve.matrix),N.matrix.decompose(N.position,N.quaternion,N.scale)),Mt===!0&&N.cameras.push(ve)}const Ft=o.enabledFeatures;if(Ft&&Ft.includes("depth-sensing")){const Vt=_.getDepthInformation(Tt[0]);Vt&&Vt.isValid&&Vt.texture&&T.init(t,Vt,o.renderState)}}for(let Tt=0;Tt<D.length;Tt++){const Mt=C[Tt],Ft=D[Tt];Mt!==null&&Ft!==void 0&&Ft.update(Mt,ft,m||f)}z&&z(q,ft),ft.detectedPlanes&&s.dispatchEvent({type:"planesdetected",data:ft}),M=null}const St=new vS;St.setAnimationLoop(nt),this.setAnimationLoop=function(q){z=q},this.dispose=function(){}}}const tr=new Ba,oN=new an;function lN(a,t){function n(S,y){S.matrixAutoUpdate===!0&&S.updateMatrix(),y.value.copy(S.matrix)}function s(S,y){y.color.getRGB(S.fogColor.value,oS(a)),y.isFog?(S.fogNear.value=y.near,S.fogFar.value=y.far):y.isFogExp2&&(S.fogDensity.value=y.density)}function o(S,y,I,D,C){y.isMeshBasicMaterial||y.isMeshLambertMaterial?c(S,y):y.isMeshToonMaterial?(c(S,y),_(S,y)):y.isMeshPhongMaterial?(c(S,y),v(S,y)):y.isMeshStandardMaterial?(c(S,y),x(S,y),y.isMeshPhysicalMaterial&&E(S,y,C)):y.isMeshMatcapMaterial?(c(S,y),M(S,y)):y.isMeshDepthMaterial?c(S,y):y.isMeshDistanceMaterial?(c(S,y),T(S,y)):y.isMeshNormalMaterial?c(S,y):y.isLineBasicMaterial?(f(S,y),y.isLineDashedMaterial&&d(S,y)):y.isPointsMaterial?p(S,y,I,D):y.isSpriteMaterial?m(S,y):y.isShadowMaterial?(S.color.value.copy(y.color),S.opacity.value=y.opacity):y.isShaderMaterial&&(y.uniformsNeedUpdate=!1)}function c(S,y){S.opacity.value=y.opacity,y.color&&S.diffuse.value.copy(y.color),y.emissive&&S.emissive.value.copy(y.emissive).multiplyScalar(y.emissiveIntensity),y.map&&(S.map.value=y.map,n(y.map,S.mapTransform)),y.alphaMap&&(S.alphaMap.value=y.alphaMap,n(y.alphaMap,S.alphaMapTransform)),y.bumpMap&&(S.bumpMap.value=y.bumpMap,n(y.bumpMap,S.bumpMapTransform),S.bumpScale.value=y.bumpScale,y.side===ii&&(S.bumpScale.value*=-1)),y.normalMap&&(S.normalMap.value=y.normalMap,n(y.normalMap,S.normalMapTransform),S.normalScale.value.copy(y.normalScale),y.side===ii&&S.normalScale.value.negate()),y.displacementMap&&(S.displacementMap.value=y.displacementMap,n(y.displacementMap,S.displacementMapTransform),S.displacementScale.value=y.displacementScale,S.displacementBias.value=y.displacementBias),y.emissiveMap&&(S.emissiveMap.value=y.emissiveMap,n(y.emissiveMap,S.emissiveMapTransform)),y.specularMap&&(S.specularMap.value=y.specularMap,n(y.specularMap,S.specularMapTransform)),y.alphaTest>0&&(S.alphaTest.value=y.alphaTest);const I=t.get(y),D=I.envMap,C=I.envMapRotation;D&&(S.envMap.value=D,tr.copy(C),tr.x*=-1,tr.y*=-1,tr.z*=-1,D.isCubeTexture&&D.isRenderTargetTexture===!1&&(tr.y*=-1,tr.z*=-1),S.envMapRotation.value.setFromMatrix4(oN.makeRotationFromEuler(tr)),S.flipEnvMap.value=D.isCubeTexture&&D.isRenderTargetTexture===!1?-1:1,S.reflectivity.value=y.reflectivity,S.ior.value=y.ior,S.refractionRatio.value=y.refractionRatio),y.lightMap&&(S.lightMap.value=y.lightMap,S.lightMapIntensity.value=y.lightMapIntensity,n(y.lightMap,S.lightMapTransform)),y.aoMap&&(S.aoMap.value=y.aoMap,S.aoMapIntensity.value=y.aoMapIntensity,n(y.aoMap,S.aoMapTransform))}function f(S,y){S.diffuse.value.copy(y.color),S.opacity.value=y.opacity,y.map&&(S.map.value=y.map,n(y.map,S.mapTransform))}function d(S,y){S.dashSize.value=y.dashSize,S.totalSize.value=y.dashSize+y.gapSize,S.scale.value=y.scale}function p(S,y,I,D){S.diffuse.value.copy(y.color),S.opacity.value=y.opacity,S.size.value=y.size*I,S.scale.value=D*.5,y.map&&(S.map.value=y.map,n(y.map,S.uvTransform)),y.alphaMap&&(S.alphaMap.value=y.alphaMap,n(y.alphaMap,S.alphaMapTransform)),y.alphaTest>0&&(S.alphaTest.value=y.alphaTest)}function m(S,y){S.diffuse.value.copy(y.color),S.opacity.value=y.opacity,S.rotation.value=y.rotation,y.map&&(S.map.value=y.map,n(y.map,S.mapTransform)),y.alphaMap&&(S.alphaMap.value=y.alphaMap,n(y.alphaMap,S.alphaMapTransform)),y.alphaTest>0&&(S.alphaTest.value=y.alphaTest)}function v(S,y){S.specular.value.copy(y.specular),S.shininess.value=Math.max(y.shininess,1e-4)}function _(S,y){y.gradientMap&&(S.gradientMap.value=y.gradientMap)}function x(S,y){S.metalness.value=y.metalness,y.metalnessMap&&(S.metalnessMap.value=y.metalnessMap,n(y.metalnessMap,S.metalnessMapTransform)),S.roughness.value=y.roughness,y.roughnessMap&&(S.roughnessMap.value=y.roughnessMap,n(y.roughnessMap,S.roughnessMapTransform)),y.envMap&&(S.envMapIntensity.value=y.envMapIntensity)}function E(S,y,I){S.ior.value=y.ior,y.sheen>0&&(S.sheenColor.value.copy(y.sheenColor).multiplyScalar(y.sheen),S.sheenRoughness.value=y.sheenRoughness,y.sheenColorMap&&(S.sheenColorMap.value=y.sheenColorMap,n(y.sheenColorMap,S.sheenColorMapTransform)),y.sheenRoughnessMap&&(S.sheenRoughnessMap.value=y.sheenRoughnessMap,n(y.sheenRoughnessMap,S.sheenRoughnessMapTransform))),y.clearcoat>0&&(S.clearcoat.value=y.clearcoat,S.clearcoatRoughness.value=y.clearcoatRoughness,y.clearcoatMap&&(S.clearcoatMap.value=y.clearcoatMap,n(y.clearcoatMap,S.clearcoatMapTransform)),y.clearcoatRoughnessMap&&(S.clearcoatRoughnessMap.value=y.clearcoatRoughnessMap,n(y.clearcoatRoughnessMap,S.clearcoatRoughnessMapTransform)),y.clearcoatNormalMap&&(S.clearcoatNormalMap.value=y.clearcoatNormalMap,n(y.clearcoatNormalMap,S.clearcoatNormalMapTransform),S.clearcoatNormalScale.value.copy(y.clearcoatNormalScale),y.side===ii&&S.clearcoatNormalScale.value.negate())),y.dispersion>0&&(S.dispersion.value=y.dispersion),y.iridescence>0&&(S.iridescence.value=y.iridescence,S.iridescenceIOR.value=y.iridescenceIOR,S.iridescenceThicknessMinimum.value=y.iridescenceThicknessRange[0],S.iridescenceThicknessMaximum.value=y.iridescenceThicknessRange[1],y.iridescenceMap&&(S.iridescenceMap.value=y.iridescenceMap,n(y.iridescenceMap,S.iridescenceMapTransform)),y.iridescenceThicknessMap&&(S.iridescenceThicknessMap.value=y.iridescenceThicknessMap,n(y.iridescenceThicknessMap,S.iridescenceThicknessMapTransform))),y.transmission>0&&(S.transmission.value=y.transmission,S.transmissionSamplerMap.value=I.texture,S.transmissionSamplerSize.value.set(I.width,I.height),y.transmissionMap&&(S.transmissionMap.value=y.transmissionMap,n(y.transmissionMap,S.transmissionMapTransform)),S.thickness.value=y.thickness,y.thicknessMap&&(S.thicknessMap.value=y.thicknessMap,n(y.thicknessMap,S.thicknessMapTransform)),S.attenuationDistance.value=y.attenuationDistance,S.attenuationColor.value.copy(y.attenuationColor)),y.anisotropy>0&&(S.anisotropyVector.value.set(y.anisotropy*Math.cos(y.anisotropyRotation),y.anisotropy*Math.sin(y.anisotropyRotation)),y.anisotropyMap&&(S.anisotropyMap.value=y.anisotropyMap,n(y.anisotropyMap,S.anisotropyMapTransform))),S.specularIntensity.value=y.specularIntensity,S.specularColor.value.copy(y.specularColor),y.specularColorMap&&(S.specularColorMap.value=y.specularColorMap,n(y.specularColorMap,S.specularColorMapTransform)),y.specularIntensityMap&&(S.specularIntensityMap.value=y.specularIntensityMap,n(y.specularIntensityMap,S.specularIntensityMapTransform))}function M(S,y){y.matcap&&(S.matcap.value=y.matcap)}function T(S,y){const I=t.get(y).light;S.referencePosition.value.setFromMatrixPosition(I.matrixWorld),S.nearDistance.value=I.shadow.camera.near,S.farDistance.value=I.shadow.camera.far}return{refreshFogUniforms:s,refreshMaterialUniforms:o}}function cN(a,t,n,s){let o={},c={},f=[];const d=a.getParameter(a.MAX_UNIFORM_BUFFER_BINDINGS);function p(I,D){const C=D.program;s.uniformBlockBinding(I,C)}function m(I,D){let C=o[I.id];C===void 0&&(M(I),C=v(I),o[I.id]=C,I.addEventListener("dispose",S));const V=D.program;s.updateUBOMapping(I,V);const L=t.render.frame;c[I.id]!==L&&(x(I),c[I.id]=L)}function v(I){const D=_();I.__bindingPointIndex=D;const C=a.createBuffer(),V=I.__size,L=I.usage;return a.bindBuffer(a.UNIFORM_BUFFER,C),a.bufferData(a.UNIFORM_BUFFER,V,L),a.bindBuffer(a.UNIFORM_BUFFER,null),a.bindBufferBase(a.UNIFORM_BUFFER,D,C),C}function _(){for(let I=0;I<d;I++)if(f.indexOf(I)===-1)return f.push(I),I;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function x(I){const D=o[I.id],C=I.uniforms,V=I.__cache;a.bindBuffer(a.UNIFORM_BUFFER,D);for(let L=0,P=C.length;L<P;L++){const G=Array.isArray(C[L])?C[L]:[C[L]];for(let U=0,N=G.length;U<N;U++){const H=G[U];if(E(H,L,U,V)===!0){const ut=H.__offset,ot=Array.isArray(H.value)?H.value:[H.value];let mt=0;for(let ct=0;ct<ot.length;ct++){const B=ot[ct],Z=T(B);typeof B=="number"||typeof B=="boolean"?(H.__data[0]=B,a.bufferSubData(a.UNIFORM_BUFFER,ut+mt,H.__data)):B.isMatrix3?(H.__data[0]=B.elements[0],H.__data[1]=B.elements[1],H.__data[2]=B.elements[2],H.__data[3]=0,H.__data[4]=B.elements[3],H.__data[5]=B.elements[4],H.__data[6]=B.elements[5],H.__data[7]=0,H.__data[8]=B.elements[6],H.__data[9]=B.elements[7],H.__data[10]=B.elements[8],H.__data[11]=0):(B.toArray(H.__data,mt),mt+=Z.storage/Float32Array.BYTES_PER_ELEMENT)}a.bufferSubData(a.UNIFORM_BUFFER,ut,H.__data)}}}a.bindBuffer(a.UNIFORM_BUFFER,null)}function E(I,D,C,V){const L=I.value,P=D+"_"+C;if(V[P]===void 0)return typeof L=="number"||typeof L=="boolean"?V[P]=L:V[P]=L.clone(),!0;{const G=V[P];if(typeof L=="number"||typeof L=="boolean"){if(G!==L)return V[P]=L,!0}else if(G.equals(L)===!1)return G.copy(L),!0}return!1}function M(I){const D=I.uniforms;let C=0;const V=16;for(let P=0,G=D.length;P<G;P++){const U=Array.isArray(D[P])?D[P]:[D[P]];for(let N=0,H=U.length;N<H;N++){const ut=U[N],ot=Array.isArray(ut.value)?ut.value:[ut.value];for(let mt=0,ct=ot.length;mt<ct;mt++){const B=ot[mt],Z=T(B),$=C%V,Et=$%Z.boundary,At=$+Et;C+=Et,At!==0&&V-At<Z.storage&&(C+=V-At),ut.__data=new Float32Array(Z.storage/Float32Array.BYTES_PER_ELEMENT),ut.__offset=C,C+=Z.storage}}}const L=C%V;return L>0&&(C+=V-L),I.__size=C,I.__cache={},this}function T(I){const D={boundary:0,storage:0};return typeof I=="number"||typeof I=="boolean"?(D.boundary=4,D.storage=4):I.isVector2?(D.boundary=8,D.storage=8):I.isVector3||I.isColor?(D.boundary=16,D.storage=12):I.isVector4?(D.boundary=16,D.storage=16):I.isMatrix3?(D.boundary=48,D.storage=48):I.isMatrix4?(D.boundary=64,D.storage=64):I.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",I),D}function S(I){const D=I.target;D.removeEventListener("dispose",S);const C=f.indexOf(D.__bindingPointIndex);f.splice(C,1),a.deleteBuffer(o[D.id]),delete o[D.id],delete c[D.id]}function y(){for(const I in o)a.deleteBuffer(o[I]);f=[],o={},c={}}return{bind:p,update:m,dispose:y}}class uN{constructor(t={}){const{canvas:n=DT(),context:s=null,depth:o=!0,stencil:c=!1,alpha:f=!1,antialias:d=!1,premultipliedAlpha:p=!0,preserveDrawingBuffer:m=!1,powerPreference:v="default",failIfMajorPerformanceCaveat:_=!1,reverseDepthBuffer:x=!1}=t;this.isWebGLRenderer=!0;let E;if(s!==null){if(typeof WebGLRenderingContext<"u"&&s instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");E=s.getContextAttributes().alpha}else E=f;const M=new Uint32Array(4),T=new Int32Array(4);let S=null,y=null;const I=[],D=[];this.domElement=n,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=vi,this.toneMapping=Cs,this.toneMappingExposure=1;const C=this;let V=!1,L=0,P=0,G=null,U=-1,N=null;const H=new We,ut=new We;let ot=null;const mt=new pe(0);let ct=0,B=n.width,Z=n.height,$=1,Et=null,At=null;const z=new We(0,0,B,Z),nt=new We(0,0,B,Z);let St=!1;const q=new Hm;let ft=!1,Tt=!1;const Mt=new an,Ft=new an,Vt=new W,oe=new We,Ge={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ve=!1;function $e(){return G===null?$:1}let j=s;function Pn(w,Q){return n.getContext(w,Q)}try{const w={alpha:!0,depth:o,stencil:c,antialias:d,premultipliedAlpha:p,preserveDrawingBuffer:m,powerPreference:v,failIfMajorPerformanceCaveat:_};if("setAttribute"in n&&n.setAttribute("data-engine",`three.js r${Dm}`),n.addEventListener("webglcontextlost",yt,!1),n.addEventListener("webglcontextrestored",wt,!1),n.addEventListener("webglcontextcreationerror",Dt,!1),j===null){const Q="webgl2";if(j=Pn(Q,w),j===null)throw Pn(Q)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(w){throw console.error("THREE.WebGLRenderer: "+w.message),w}let me,Se,Qt,Be,Yt,O,R,at,pt,bt,vt,Xt,Nt,Bt,Me,Ct,Ht,Zt,qt,Ot,ne,le,Ve,Y;function Rt(){me=new yR(j),me.init(),le=new eN(j,me),Se=new hR(j,me,t,le),Qt=new $w(j,me),Se.reverseDepthBuffer&&x&&Qt.buffers.depth.setReversed(!0),Be=new MR(j),Yt=new Hw,O=new tN(j,me,Qt,Yt,Se,le,Be),R=new mR(C),at=new _R(C),pt=new wA(j),Ve=new fR(j,pt),bt=new xR(j,pt,Be,Ve),vt=new bR(j,bt,pt,Be),qt=new ER(j,Se,O),Ct=new pR(Yt),Xt=new Fw(C,R,at,me,Se,Ve,Ct),Nt=new lN(C,Yt),Bt=new Vw,Me=new Yw(me),Zt=new uR(C,R,at,Qt,vt,E,p),Ht=new Kw(C,vt,Se),Y=new cN(j,Be,Se,Qt),Ot=new dR(j,me,Be),ne=new SR(j,me,Be),Be.programs=Xt.programs,C.capabilities=Se,C.extensions=me,C.properties=Yt,C.renderLists=Bt,C.shadowMap=Ht,C.state=Qt,C.info=Be}Rt();const dt=new rN(C,j);this.xr=dt,this.getContext=function(){return j},this.getContextAttributes=function(){return j.getContextAttributes()},this.forceContextLoss=function(){const w=me.get("WEBGL_lose_context");w&&w.loseContext()},this.forceContextRestore=function(){const w=me.get("WEBGL_lose_context");w&&w.restoreContext()},this.getPixelRatio=function(){return $},this.setPixelRatio=function(w){w!==void 0&&($=w,this.setSize(B,Z,!1))},this.getSize=function(w){return w.set(B,Z)},this.setSize=function(w,Q,st=!0){if(dt.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}B=w,Z=Q,n.width=Math.floor(w*$),n.height=Math.floor(Q*$),st===!0&&(n.style.width=w+"px",n.style.height=Q+"px"),this.setViewport(0,0,w,Q)},this.getDrawingBufferSize=function(w){return w.set(B*$,Z*$).floor()},this.setDrawingBufferSize=function(w,Q,st){B=w,Z=Q,$=st,n.width=Math.floor(w*st),n.height=Math.floor(Q*st),this.setViewport(0,0,w,Q)},this.getCurrentViewport=function(w){return w.copy(H)},this.getViewport=function(w){return w.copy(z)},this.setViewport=function(w,Q,st,rt){w.isVector4?z.set(w.x,w.y,w.z,w.w):z.set(w,Q,st,rt),Qt.viewport(H.copy(z).multiplyScalar($).round())},this.getScissor=function(w){return w.copy(nt)},this.setScissor=function(w,Q,st,rt){w.isVector4?nt.set(w.x,w.y,w.z,w.w):nt.set(w,Q,st,rt),Qt.scissor(ut.copy(nt).multiplyScalar($).round())},this.getScissorTest=function(){return St},this.setScissorTest=function(w){Qt.setScissorTest(St=w)},this.setOpaqueSort=function(w){Et=w},this.setTransparentSort=function(w){At=w},this.getClearColor=function(w){return w.copy(Zt.getClearColor())},this.setClearColor=function(){Zt.setClearColor.apply(Zt,arguments)},this.getClearAlpha=function(){return Zt.getClearAlpha()},this.setClearAlpha=function(){Zt.setClearAlpha.apply(Zt,arguments)},this.clear=function(w=!0,Q=!0,st=!0){let rt=0;if(w){let K=!1;if(G!==null){const xt=G.texture.format;K=xt===Im||xt===zm||xt===Pm}if(K){const xt=G.texture.type,Ut=xt===Ia||xt===xr||xt===lc||xt===Vo||xt===Lm||xt===Om,It=Zt.getClearColor(),Pt=Zt.getClearAlpha(),$t=It.r,ae=It.g,Kt=It.b;Ut?(M[0]=$t,M[1]=ae,M[2]=Kt,M[3]=Pt,j.clearBufferuiv(j.COLOR,0,M)):(T[0]=$t,T[1]=ae,T[2]=Kt,T[3]=Pt,j.clearBufferiv(j.COLOR,0,T))}else rt|=j.COLOR_BUFFER_BIT}Q&&(rt|=j.DEPTH_BUFFER_BIT),st&&(rt|=j.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),j.clear(rt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){n.removeEventListener("webglcontextlost",yt,!1),n.removeEventListener("webglcontextrestored",wt,!1),n.removeEventListener("webglcontextcreationerror",Dt,!1),Zt.dispose(),Bt.dispose(),Me.dispose(),Yt.dispose(),R.dispose(),at.dispose(),vt.dispose(),Ve.dispose(),Y.dispose(),Xt.dispose(),dt.dispose(),dt.removeEventListener("sessionstart",Zo),dt.removeEventListener("sessionend",Ko),ji.stop()};function yt(w){w.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),V=!0}function wt(){console.log("THREE.WebGLRenderer: Context Restored."),V=!1;const w=Be.autoReset,Q=Ht.enabled,st=Ht.autoUpdate,rt=Ht.needsUpdate,K=Ht.type;Rt(),Be.autoReset=w,Ht.enabled=Q,Ht.autoUpdate=st,Ht.needsUpdate=rt,Ht.type=K}function Dt(w){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",w.statusMessage)}function ie(w){const Q=w.target;Q.removeEventListener("dispose",ie),tn(Q)}function tn(w){_n(w),Yt.remove(w)}function _n(w){const Q=Yt.get(w).programs;Q!==void 0&&(Q.forEach(function(st){Xt.releaseProgram(st)}),w.isShaderMaterial&&Xt.releaseShaderCache(w))}this.renderBufferDirect=function(w,Q,st,rt,K,xt){Q===null&&(Q=Ge);const Ut=K.isMesh&&K.matrixWorld.determinant()<0,It=$o(w,Q,st,rt,K);Qt.setMaterial(rt,Ut);let Pt=st.index,$t=1;if(rt.wireframe===!0){if(Pt=bt.getWireframeAttribute(st),Pt===void 0)return;$t=2}const ae=st.drawRange,Kt=st.attributes.position;let Ee=ae.start*$t,De=(ae.start+ae.count)*$t;xt!==null&&(Ee=Math.max(Ee,xt.start*$t),De=Math.min(De,(xt.start+xt.count)*$t)),Pt!==null?(Ee=Math.max(Ee,0),De=Math.min(De,Pt.count)):Kt!=null&&(Ee=Math.max(Ee,0),De=Math.min(De,Kt.count));const Ze=De-Ee;if(Ze<0||Ze===1/0)return;Ve.setup(K,rt,It,st,Pt);let Ye,ce=Ot;if(Pt!==null&&(Ye=pt.get(Pt),ce=ne,ce.setIndex(Ye)),K.isMesh)rt.wireframe===!0?(Qt.setLineWidth(rt.wireframeLinewidth*$e()),ce.setMode(j.LINES)):ce.setMode(j.TRIANGLES);else if(K.isLine){let jt=rt.linewidth;jt===void 0&&(jt=1),Qt.setLineWidth(jt*$e()),K.isLineSegments?ce.setMode(j.LINES):K.isLineLoop?ce.setMode(j.LINE_LOOP):ce.setMode(j.LINE_STRIP)}else K.isPoints?ce.setMode(j.POINTS):K.isSprite&&ce.setMode(j.TRIANGLES);if(K.isBatchedMesh)if(K._multiDrawInstances!==null)ce.renderMultiDrawInstances(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount,K._multiDrawInstances);else if(me.get("WEBGL_multi_draw"))ce.renderMultiDraw(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount);else{const jt=K._multiDrawStarts,dn=K._multiDrawCounts,Ue=K._multiDrawCount,Gn=Pt?pt.get(Pt).bytesPerElement:1,ia=Yt.get(rt).currentProgram.getUniforms();for(let En=0;En<Ue;En++)ia.setValue(j,"_gl_DrawID",En),ce.render(jt[En]/Gn,dn[En])}else if(K.isInstancedMesh)ce.renderInstances(Ee,Ze,K.count);else if(st.isInstancedBufferGeometry){const jt=st._maxInstanceCount!==void 0?st._maxInstanceCount:1/0,dn=Math.min(st.instanceCount,jt);ce.renderInstances(Ee,Ze,dn)}else ce.render(Ee,Ze)};function Ne(w,Q,st){w.transparent===!0&&w.side===Na&&w.forceSinglePass===!1?(w.side=ii,w.needsUpdate=!0,sn(w,Q,st),w.side=Rs,w.needsUpdate=!0,sn(w,Q,st),w.side=Na):sn(w,Q,st)}this.compile=function(w,Q,st=null){st===null&&(st=w),y=Me.get(st),y.init(Q),D.push(y),st.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(y.pushLight(K),K.castShadow&&y.pushShadow(K))}),w!==st&&w.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(y.pushLight(K),K.castShadow&&y.pushShadow(K))}),y.setupLights();const rt=new Set;return w.traverse(function(K){if(!(K.isMesh||K.isPoints||K.isLine||K.isSprite))return;const xt=K.material;if(xt)if(Array.isArray(xt))for(let Ut=0;Ut<xt.length;Ut++){const It=xt[Ut];Ne(It,st,K),rt.add(It)}else Ne(xt,st,K),rt.add(xt)}),D.pop(),y=null,rt},this.compileAsync=function(w,Q,st=null){const rt=this.compile(w,Q,st);return new Promise(K=>{function xt(){if(rt.forEach(function(Ut){Yt.get(Ut).currentProgram.isReady()&&rt.delete(Ut)}),rt.size===0){K(w);return}setTimeout(xt,10)}me.get("KHR_parallel_shader_compile")!==null?xt():setTimeout(xt,10)})};let Rn=null;function wi(w){Rn&&Rn(w)}function Zo(){ji.stop()}function Ko(){ji.start()}const ji=new vS;ji.setAnimationLoop(wi),typeof self<"u"&&ji.setContext(self),this.setAnimationLoop=function(w){Rn=w,dt.setAnimationLoop(w),w===null?ji.stop():ji.start()},dt.addEventListener("sessionstart",Zo),dt.addEventListener("sessionend",Ko),this.render=function(w,Q){if(Q!==void 0&&Q.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(V===!0)return;if(w.matrixWorldAutoUpdate===!0&&w.updateMatrixWorld(),Q.parent===null&&Q.matrixWorldAutoUpdate===!0&&Q.updateMatrixWorld(),dt.enabled===!0&&dt.isPresenting===!0&&(dt.cameraAutoUpdate===!0&&dt.updateCamera(Q),Q=dt.getCamera()),w.isScene===!0&&w.onBeforeRender(C,w,Q,G),y=Me.get(w,D.length),y.init(Q),D.push(y),Ft.multiplyMatrices(Q.projectionMatrix,Q.matrixWorldInverse),q.setFromProjectionMatrix(Ft),Tt=this.localClippingEnabled,ft=Ct.init(this.clippingPlanes,Tt),S=Bt.get(w,I.length),S.init(),I.push(S),dt.enabled===!0&&dt.isPresenting===!0){const xt=C.xr.getDepthSensingMesh();xt!==null&&ws(xt,Q,-1/0,C.sortObjects)}ws(w,Q,0,C.sortObjects),S.finish(),C.sortObjects===!0&&S.sort(Et,At),ve=dt.enabled===!1||dt.isPresenting===!1||dt.hasDepthSensing()===!1,ve&&Zt.addToRenderList(S,w),this.info.render.frame++,ft===!0&&Ct.beginShadows();const st=y.state.shadowsArray;Ht.render(st,w,Q),ft===!0&&Ct.endShadows(),this.info.autoReset===!0&&this.info.reset();const rt=S.opaque,K=S.transmissive;if(y.setupLights(),Q.isArrayCamera){const xt=Q.cameras;if(K.length>0)for(let Ut=0,It=xt.length;Ut<It;Ut++){const Pt=xt[Ut];Jo(rt,K,w,Pt)}ve&&Zt.render(w);for(let Ut=0,It=xt.length;Ut<It;Ut++){const Pt=xt[Ut];Mr(S,w,Pt,Pt.viewport)}}else K.length>0&&Jo(rt,K,w,Q),ve&&Zt.render(w),Mr(S,w,Q);G!==null&&(O.updateMultisampleRenderTarget(G),O.updateRenderTargetMipmap(G)),w.isScene===!0&&w.onAfterRender(C,w,Q),Ve.resetDefaultState(),U=-1,N=null,D.pop(),D.length>0?(y=D[D.length-1],ft===!0&&Ct.setGlobalState(C.clippingPlanes,y.state.camera)):y=null,I.pop(),I.length>0?S=I[I.length-1]:S=null};function ws(w,Q,st,rt){if(w.visible===!1)return;if(w.layers.test(Q.layers)){if(w.isGroup)st=w.renderOrder;else if(w.isLOD)w.autoUpdate===!0&&w.update(Q);else if(w.isLight)y.pushLight(w),w.castShadow&&y.pushShadow(w);else if(w.isSprite){if(!w.frustumCulled||q.intersectsSprite(w)){rt&&oe.setFromMatrixPosition(w.matrixWorld).applyMatrix4(Ft);const Ut=vt.update(w),It=w.material;It.visible&&S.push(w,Ut,It,st,oe.z,null)}}else if((w.isMesh||w.isLine||w.isPoints)&&(!w.frustumCulled||q.intersectsObject(w))){const Ut=vt.update(w),It=w.material;if(rt&&(w.boundingSphere!==void 0?(w.boundingSphere===null&&w.computeBoundingSphere(),oe.copy(w.boundingSphere.center)):(Ut.boundingSphere===null&&Ut.computeBoundingSphere(),oe.copy(Ut.boundingSphere.center)),oe.applyMatrix4(w.matrixWorld).applyMatrix4(Ft)),Array.isArray(It)){const Pt=Ut.groups;for(let $t=0,ae=Pt.length;$t<ae;$t++){const Kt=Pt[$t],Ee=It[Kt.materialIndex];Ee&&Ee.visible&&S.push(w,Ut,Ee,st,oe.z,Kt)}}else It.visible&&S.push(w,Ut,It,st,oe.z,null)}}const xt=w.children;for(let Ut=0,It=xt.length;Ut<It;Ut++)ws(xt[Ut],Q,st,rt)}function Mr(w,Q,st,rt){const K=w.opaque,xt=w.transmissive,Ut=w.transparent;y.setupLightsView(st),ft===!0&&Ct.setGlobalState(C.clippingPlanes,st),rt&&Qt.viewport(H.copy(rt)),K.length>0&&Ns(K,Q,st),xt.length>0&&Ns(xt,Q,st),Ut.length>0&&Ns(Ut,Q,st),Qt.buffers.depth.setTest(!0),Qt.buffers.depth.setMask(!0),Qt.buffers.color.setMask(!0),Qt.setPolygonOffset(!1)}function Jo(w,Q,st,rt){if((st.isScene===!0?st.overrideMaterial:null)!==null)return;y.state.transmissionRenderTarget[rt.id]===void 0&&(y.state.transmissionRenderTarget[rt.id]=new Gi(1,1,{generateMipmaps:!0,type:me.has("EXT_color_buffer_half_float")||me.has("EXT_color_buffer_float")?Pa:Ia,minFilter:ur,samples:4,stencilBuffer:c,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Pe.workingColorSpace}));const xt=y.state.transmissionRenderTarget[rt.id],Ut=rt.viewport||H;xt.setSize(Ut.z,Ut.w);const It=C.getRenderTarget();C.setRenderTarget(xt),C.getClearColor(mt),ct=C.getClearAlpha(),ct<1&&C.setClearColor(16777215,.5),C.clear(),ve&&Zt.render(st);const Pt=C.toneMapping;C.toneMapping=Cs;const $t=rt.viewport;if(rt.viewport!==void 0&&(rt.viewport=void 0),y.setupLightsView(rt),ft===!0&&Ct.setGlobalState(C.clippingPlanes,rt),Ns(w,st,rt),O.updateMultisampleRenderTarget(xt),O.updateRenderTargetMipmap(xt),me.has("WEBGL_multisampled_render_to_texture")===!1){let ae=!1;for(let Kt=0,Ee=Q.length;Kt<Ee;Kt++){const De=Q[Kt],Ze=De.object,Ye=De.geometry,ce=De.material,jt=De.group;if(ce.side===Na&&Ze.layers.test(rt.layers)){const dn=ce.side;ce.side=ii,ce.needsUpdate=!0,Ni(Ze,st,rt,Ye,ce,jt),ce.side=dn,ce.needsUpdate=!0,ae=!0}}ae===!0&&(O.updateMultisampleRenderTarget(xt),O.updateRenderTargetMipmap(xt))}C.setRenderTarget(It),C.setClearColor(mt,ct),$t!==void 0&&(rt.viewport=$t),C.toneMapping=Pt}function Ns(w,Q,st){const rt=Q.isScene===!0?Q.overrideMaterial:null;for(let K=0,xt=w.length;K<xt;K++){const Ut=w[K],It=Ut.object,Pt=Ut.geometry,$t=rt===null?Ut.material:rt,ae=Ut.group;It.layers.test(st.layers)&&Ni(It,Q,st,Pt,$t,ae)}}function Ni(w,Q,st,rt,K,xt){w.onBeforeRender(C,Q,st,rt,K,xt),w.modelViewMatrix.multiplyMatrices(st.matrixWorldInverse,w.matrixWorld),w.normalMatrix.getNormalMatrix(w.modelViewMatrix),K.onBeforeRender(C,Q,st,rt,w,xt),K.transparent===!0&&K.side===Na&&K.forceSinglePass===!1?(K.side=ii,K.needsUpdate=!0,C.renderBufferDirect(st,Q,rt,K,w,xt),K.side=Rs,K.needsUpdate=!0,C.renderBufferDirect(st,Q,rt,K,w,xt),K.side=Na):C.renderBufferDirect(st,Q,rt,K,w,xt),w.onAfterRender(C,Q,st,rt,K,xt)}function sn(w,Q,st){Q.isScene!==!0&&(Q=Ge);const rt=Yt.get(w),K=y.state.lights,xt=y.state.shadowsArray,Ut=K.state.version,It=Xt.getParameters(w,K.state,xt,Q,st),Pt=Xt.getProgramCacheKey(It);let $t=rt.programs;rt.environment=w.isMeshStandardMaterial?Q.environment:null,rt.fog=Q.fog,rt.envMap=(w.isMeshStandardMaterial?at:R).get(w.envMap||rt.environment),rt.envMapRotation=rt.environment!==null&&w.envMap===null?Q.environmentRotation:w.envMapRotation,$t===void 0&&(w.addEventListener("dispose",ie),$t=new Map,rt.programs=$t);let ae=$t.get(Pt);if(ae!==void 0){if(rt.currentProgram===ae&&rt.lightsStateVersion===Ut)return na(w,It),ae}else It.uniforms=Xt.getUniforms(w),w.onBeforeCompile(It,C),ae=Xt.acquireProgram(It,Pt),$t.set(Pt,ae),rt.uniforms=It.uniforms;const Kt=rt.uniforms;return(!w.isShaderMaterial&&!w.isRawShaderMaterial||w.clipping===!0)&&(Kt.clippingPlanes=Ct.uniform),na(w,It),rt.needsLights=Af(w),rt.lightsStateVersion=Ut,rt.needsLights&&(Kt.ambientLightColor.value=K.state.ambient,Kt.lightProbe.value=K.state.probe,Kt.directionalLights.value=K.state.directional,Kt.directionalLightShadows.value=K.state.directionalShadow,Kt.spotLights.value=K.state.spot,Kt.spotLightShadows.value=K.state.spotShadow,Kt.rectAreaLights.value=K.state.rectArea,Kt.ltc_1.value=K.state.rectAreaLTC1,Kt.ltc_2.value=K.state.rectAreaLTC2,Kt.pointLights.value=K.state.point,Kt.pointLightShadows.value=K.state.pointShadow,Kt.hemisphereLights.value=K.state.hemi,Kt.directionalShadowMap.value=K.state.directionalShadowMap,Kt.directionalShadowMatrix.value=K.state.directionalShadowMatrix,Kt.spotShadowMap.value=K.state.spotShadowMap,Kt.spotLightMatrix.value=K.state.spotLightMatrix,Kt.spotLightMap.value=K.state.spotLightMap,Kt.pointShadowMap.value=K.state.pointShadowMap,Kt.pointShadowMatrix.value=K.state.pointShadowMatrix),rt.currentProgram=ae,rt.uniformsList=null,ae}function wn(w){if(w.uniformsList===null){const Q=w.currentProgram.getUniforms();w.uniformsList=uf.seqWithValue(Q.seq,w.uniforms)}return w.uniformsList}function na(w,Q){const st=Yt.get(w);st.outputColorSpace=Q.outputColorSpace,st.batching=Q.batching,st.batchingColor=Q.batchingColor,st.instancing=Q.instancing,st.instancingColor=Q.instancingColor,st.instancingMorph=Q.instancingMorph,st.skinning=Q.skinning,st.morphTargets=Q.morphTargets,st.morphNormals=Q.morphNormals,st.morphColors=Q.morphColors,st.morphTargetsCount=Q.morphTargetsCount,st.numClippingPlanes=Q.numClippingPlanes,st.numIntersection=Q.numClipIntersection,st.vertexAlphas=Q.vertexAlphas,st.vertexTangents=Q.vertexTangents,st.toneMapping=Q.toneMapping}function $o(w,Q,st,rt,K){Q.isScene!==!0&&(Q=Ge),O.resetTextureUnits();const xt=Q.fog,Ut=rt.isMeshStandardMaterial?Q.environment:null,It=G===null?C.outputColorSpace:G.isXRRenderTarget===!0?G.texture.colorSpace:ko,Pt=(rt.isMeshStandardMaterial?at:R).get(rt.envMap||Ut),$t=rt.vertexColors===!0&&!!st.attributes.color&&st.attributes.color.itemSize===4,ae=!!st.attributes.tangent&&(!!rt.normalMap||rt.anisotropy>0),Kt=!!st.morphAttributes.position,Ee=!!st.morphAttributes.normal,De=!!st.morphAttributes.color;let Ze=Cs;rt.toneMapped&&(G===null||G.isXRRenderTarget===!0)&&(Ze=C.toneMapping);const Ye=st.morphAttributes.position||st.morphAttributes.normal||st.morphAttributes.color,ce=Ye!==void 0?Ye.length:0,jt=Yt.get(rt),dn=y.state.lights;if(ft===!0&&(Tt===!0||w!==N)){const yn=w===N&&rt.id===U;Ct.setState(rt,w,yn)}let Ue=!1;rt.version===jt.__version?(jt.needsLights&&jt.lightsStateVersion!==dn.state.version||jt.outputColorSpace!==It||K.isBatchedMesh&&jt.batching===!1||!K.isBatchedMesh&&jt.batching===!0||K.isBatchedMesh&&jt.batchingColor===!0&&K.colorTexture===null||K.isBatchedMesh&&jt.batchingColor===!1&&K.colorTexture!==null||K.isInstancedMesh&&jt.instancing===!1||!K.isInstancedMesh&&jt.instancing===!0||K.isSkinnedMesh&&jt.skinning===!1||!K.isSkinnedMesh&&jt.skinning===!0||K.isInstancedMesh&&jt.instancingColor===!0&&K.instanceColor===null||K.isInstancedMesh&&jt.instancingColor===!1&&K.instanceColor!==null||K.isInstancedMesh&&jt.instancingMorph===!0&&K.morphTexture===null||K.isInstancedMesh&&jt.instancingMorph===!1&&K.morphTexture!==null||jt.envMap!==Pt||rt.fog===!0&&jt.fog!==xt||jt.numClippingPlanes!==void 0&&(jt.numClippingPlanes!==Ct.numPlanes||jt.numIntersection!==Ct.numIntersection)||jt.vertexAlphas!==$t||jt.vertexTangents!==ae||jt.morphTargets!==Kt||jt.morphNormals!==Ee||jt.morphColors!==De||jt.toneMapping!==Ze||jt.morphTargetsCount!==ce)&&(Ue=!0):(Ue=!0,jt.__version=rt.version);let Gn=jt.currentProgram;Ue===!0&&(Gn=sn(rt,Q,K));let ia=!1,En=!1,Us=!1;const _e=Gn.getUniforms(),zn=jt.uniforms;if(Qt.useProgram(Gn.program)&&(ia=!0,En=!0,Us=!0),rt.id!==U&&(U=rt.id,En=!0),ia||N!==w){Qt.buffers.depth.getReversed()?(Mt.copy(w.projectionMatrix),LT(Mt),OT(Mt),_e.setValue(j,"projectionMatrix",Mt)):_e.setValue(j,"projectionMatrix",w.projectionMatrix),_e.setValue(j,"viewMatrix",w.matrixWorldInverse);const cn=_e.map.cameraPosition;cn!==void 0&&cn.setValue(j,Vt.setFromMatrixPosition(w.matrixWorld)),Se.logarithmicDepthBuffer&&_e.setValue(j,"logDepthBufFC",2/(Math.log(w.far+1)/Math.LN2)),(rt.isMeshPhongMaterial||rt.isMeshToonMaterial||rt.isMeshLambertMaterial||rt.isMeshBasicMaterial||rt.isMeshStandardMaterial||rt.isShaderMaterial)&&_e.setValue(j,"isOrthographic",w.isOrthographicCamera===!0),N!==w&&(N=w,En=!0,Us=!0)}if(K.isSkinnedMesh){_e.setOptional(j,K,"bindMatrix"),_e.setOptional(j,K,"bindMatrixInverse");const yn=K.skeleton;yn&&(yn.boneTexture===null&&yn.computeBoneTexture(),_e.setValue(j,"boneTexture",yn.boneTexture,O))}K.isBatchedMesh&&(_e.setOptional(j,K,"batchingTexture"),_e.setValue(j,"batchingTexture",K._matricesTexture,O),_e.setOptional(j,K,"batchingIdTexture"),_e.setValue(j,"batchingIdTexture",K._indirectTexture,O),_e.setOptional(j,K,"batchingColorTexture"),K._colorsTexture!==null&&_e.setValue(j,"batchingColorTexture",K._colorsTexture,O));const Vn=st.morphAttributes;if((Vn.position!==void 0||Vn.normal!==void 0||Vn.color!==void 0)&&qt.update(K,st,Gn),(En||jt.receiveShadow!==K.receiveShadow)&&(jt.receiveShadow=K.receiveShadow,_e.setValue(j,"receiveShadow",K.receiveShadow)),rt.isMeshGouraudMaterial&&rt.envMap!==null&&(zn.envMap.value=Pt,zn.flipEnvMap.value=Pt.isCubeTexture&&Pt.isRenderTargetTexture===!1?-1:1),rt.isMeshStandardMaterial&&rt.envMap===null&&Q.environment!==null&&(zn.envMapIntensity.value=Q.environmentIntensity),En&&(_e.setValue(j,"toneMappingExposure",C.toneMappingExposure),jt.needsLights&&Tf(zn,Us),xt&&rt.fog===!0&&Nt.refreshFogUniforms(zn,xt),Nt.refreshMaterialUniforms(zn,rt,$,Z,y.state.transmissionRenderTarget[w.id]),uf.upload(j,wn(jt),zn,O)),rt.isShaderMaterial&&rt.uniformsNeedUpdate===!0&&(uf.upload(j,wn(jt),zn,O),rt.uniformsNeedUpdate=!1),rt.isSpriteMaterial&&_e.setValue(j,"center",K.center),_e.setValue(j,"modelViewMatrix",K.modelViewMatrix),_e.setValue(j,"normalMatrix",K.normalMatrix),_e.setValue(j,"modelMatrix",K.matrixWorld),rt.isShaderMaterial||rt.isRawShaderMaterial){const yn=rt.uniformsGroups;for(let cn=0,Er=yn.length;cn<Er;cn++){const ki=yn[cn];Y.update(ki,Gn),Y.bind(ki,Gn)}}return Gn}function Tf(w,Q){w.ambientLightColor.needsUpdate=Q,w.lightProbe.needsUpdate=Q,w.directionalLights.needsUpdate=Q,w.directionalLightShadows.needsUpdate=Q,w.pointLights.needsUpdate=Q,w.pointLightShadows.needsUpdate=Q,w.spotLights.needsUpdate=Q,w.spotLightShadows.needsUpdate=Q,w.rectAreaLights.needsUpdate=Q,w.hemisphereLights.needsUpdate=Q}function Af(w){return w.isMeshLambertMaterial||w.isMeshToonMaterial||w.isMeshPhongMaterial||w.isMeshStandardMaterial||w.isShadowMaterial||w.isShaderMaterial&&w.lights===!0}this.getActiveCubeFace=function(){return L},this.getActiveMipmapLevel=function(){return P},this.getRenderTarget=function(){return G},this.setRenderTargetTextures=function(w,Q,st){Yt.get(w.texture).__webglTexture=Q,Yt.get(w.depthTexture).__webglTexture=st;const rt=Yt.get(w);rt.__hasExternalTextures=!0,rt.__autoAllocateDepthBuffer=st===void 0,rt.__autoAllocateDepthBuffer||me.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),rt.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(w,Q){const st=Yt.get(w);st.__webglFramebuffer=Q,st.__useDefaultFramebuffer=Q===void 0},this.setRenderTarget=function(w,Q=0,st=0){G=w,L=Q,P=st;let rt=!0,K=null,xt=!1,Ut=!1;if(w){const Pt=Yt.get(w);if(Pt.__useDefaultFramebuffer!==void 0)Qt.bindFramebuffer(j.FRAMEBUFFER,null),rt=!1;else if(Pt.__webglFramebuffer===void 0)O.setupRenderTarget(w);else if(Pt.__hasExternalTextures)O.rebindTextures(w,Yt.get(w.texture).__webglTexture,Yt.get(w.depthTexture).__webglTexture);else if(w.depthBuffer){const Kt=w.depthTexture;if(Pt.__boundDepthTexture!==Kt){if(Kt!==null&&Yt.has(Kt)&&(w.width!==Kt.image.width||w.height!==Kt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");O.setupDepthRenderbuffer(w)}}const $t=w.texture;($t.isData3DTexture||$t.isDataArrayTexture||$t.isCompressedArrayTexture)&&(Ut=!0);const ae=Yt.get(w).__webglFramebuffer;w.isWebGLCubeRenderTarget?(Array.isArray(ae[Q])?K=ae[Q][st]:K=ae[Q],xt=!0):w.samples>0&&O.useMultisampledRTT(w)===!1?K=Yt.get(w).__webglMultisampledFramebuffer:Array.isArray(ae)?K=ae[st]:K=ae,H.copy(w.viewport),ut.copy(w.scissor),ot=w.scissorTest}else H.copy(z).multiplyScalar($).floor(),ut.copy(nt).multiplyScalar($).floor(),ot=St;if(Qt.bindFramebuffer(j.FRAMEBUFFER,K)&&rt&&Qt.drawBuffers(w,K),Qt.viewport(H),Qt.scissor(ut),Qt.setScissorTest(ot),xt){const Pt=Yt.get(w.texture);j.framebufferTexture2D(j.FRAMEBUFFER,j.COLOR_ATTACHMENT0,j.TEXTURE_CUBE_MAP_POSITIVE_X+Q,Pt.__webglTexture,st)}else if(Ut){const Pt=Yt.get(w.texture),$t=Q||0;j.framebufferTextureLayer(j.FRAMEBUFFER,j.COLOR_ATTACHMENT0,Pt.__webglTexture,st||0,$t)}U=-1},this.readRenderTargetPixels=function(w,Q,st,rt,K,xt,Ut){if(!(w&&w.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let It=Yt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Ut!==void 0&&(It=It[Ut]),It){Qt.bindFramebuffer(j.FRAMEBUFFER,It);try{const Pt=w.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Se.textureTypeReadable(ae)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}Q>=0&&Q<=w.width-rt&&st>=0&&st<=w.height-K&&j.readPixels(Q,st,rt,K,le.convert($t),le.convert(ae),xt)}finally{const Pt=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(j.FRAMEBUFFER,Pt)}}},this.readRenderTargetPixelsAsync=async function(w,Q,st,rt,K,xt,Ut){if(!(w&&w.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let It=Yt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Ut!==void 0&&(It=It[Ut]),It){const Pt=w.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Se.textureTypeReadable(ae))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(Q>=0&&Q<=w.width-rt&&st>=0&&st<=w.height-K){Qt.bindFramebuffer(j.FRAMEBUFFER,It);const Kt=j.createBuffer();j.bindBuffer(j.PIXEL_PACK_BUFFER,Kt),j.bufferData(j.PIXEL_PACK_BUFFER,xt.byteLength,j.STREAM_READ),j.readPixels(Q,st,rt,K,le.convert($t),le.convert(ae),0);const Ee=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(j.FRAMEBUFFER,Ee);const De=j.fenceSync(j.SYNC_GPU_COMMANDS_COMPLETE,0);return j.flush(),await UT(j,De,4),j.bindBuffer(j.PIXEL_PACK_BUFFER,Kt),j.getBufferSubData(j.PIXEL_PACK_BUFFER,0,xt),j.deleteBuffer(Kt),j.deleteSync(De),xt}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(w,Q=null,st=0){w.isTexture!==!0&&(xo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),Q=arguments[0]||null,w=arguments[1]);const rt=Math.pow(2,-st),K=Math.floor(w.image.width*rt),xt=Math.floor(w.image.height*rt),Ut=Q!==null?Q.x:0,It=Q!==null?Q.y:0;O.setTexture2D(w,0),j.copyTexSubImage2D(j.TEXTURE_2D,st,0,0,Ut,It,K,xt),Qt.unbindTexture()};const xc=j.createFramebuffer(),Ds=j.createFramebuffer();this.copyTextureToTexture=function(w,Q,st=null,rt=null,K=0,xt=null){w.isTexture!==!0&&(xo("WebGLRenderer: copyTextureToTexture function signature has changed."),rt=arguments[0]||null,w=arguments[1],Q=arguments[2],xt=arguments[3]||0,st=null),xt===null&&(K!==0?(xo("WebGLRenderer: copyTextureToTexture function signature has changed to support src and dst mipmap levels."),xt=K,K=0):xt=0);let Ut,It,Pt,$t,ae,Kt,Ee,De,Ze;const Ye=w.isCompressedTexture?w.mipmaps[xt]:w.image;if(st!==null)Ut=st.max.x-st.min.x,It=st.max.y-st.min.y,Pt=st.isBox3?st.max.z-st.min.z:1,$t=st.min.x,ae=st.min.y,Kt=st.isBox3?st.min.z:0;else{const Vn=Math.pow(2,-K);Ut=Math.floor(Ye.width*Vn),It=Math.floor(Ye.height*Vn),w.isDataArrayTexture?Pt=Ye.depth:w.isData3DTexture?Pt=Math.floor(Ye.depth*Vn):Pt=1,$t=0,ae=0,Kt=0}rt!==null?(Ee=rt.x,De=rt.y,Ze=rt.z):(Ee=0,De=0,Ze=0);const ce=le.convert(Q.format),jt=le.convert(Q.type);let dn;Q.isData3DTexture?(O.setTexture3D(Q,0),dn=j.TEXTURE_3D):Q.isDataArrayTexture||Q.isCompressedArrayTexture?(O.setTexture2DArray(Q,0),dn=j.TEXTURE_2D_ARRAY):(O.setTexture2D(Q,0),dn=j.TEXTURE_2D),j.pixelStorei(j.UNPACK_FLIP_Y_WEBGL,Q.flipY),j.pixelStorei(j.UNPACK_PREMULTIPLY_ALPHA_WEBGL,Q.premultiplyAlpha),j.pixelStorei(j.UNPACK_ALIGNMENT,Q.unpackAlignment);const Ue=j.getParameter(j.UNPACK_ROW_LENGTH),Gn=j.getParameter(j.UNPACK_IMAGE_HEIGHT),ia=j.getParameter(j.UNPACK_SKIP_PIXELS),En=j.getParameter(j.UNPACK_SKIP_ROWS),Us=j.getParameter(j.UNPACK_SKIP_IMAGES);j.pixelStorei(j.UNPACK_ROW_LENGTH,Ye.width),j.pixelStorei(j.UNPACK_IMAGE_HEIGHT,Ye.height),j.pixelStorei(j.UNPACK_SKIP_PIXELS,$t),j.pixelStorei(j.UNPACK_SKIP_ROWS,ae),j.pixelStorei(j.UNPACK_SKIP_IMAGES,Kt);const _e=w.isDataArrayTexture||w.isData3DTexture,zn=Q.isDataArrayTexture||Q.isData3DTexture;if(w.isDepthTexture){const Vn=Yt.get(w),yn=Yt.get(Q),cn=Yt.get(Vn.__renderTarget),Er=Yt.get(yn.__renderTarget);Qt.bindFramebuffer(j.READ_FRAMEBUFFER,cn.__webglFramebuffer),Qt.bindFramebuffer(j.DRAW_FRAMEBUFFER,Er.__webglFramebuffer);for(let ki=0;ki<Pt;ki++)_e&&(j.framebufferTextureLayer(j.READ_FRAMEBUFFER,j.COLOR_ATTACHMENT0,Yt.get(w).__webglTexture,K,Kt+ki),j.framebufferTextureLayer(j.DRAW_FRAMEBUFFER,j.COLOR_ATTACHMENT0,Yt.get(Q).__webglTexture,xt,Ze+ki)),j.blitFramebuffer($t,ae,Ut,It,Ee,De,Ut,It,j.DEPTH_BUFFER_BIT,j.NEAREST);Qt.bindFramebuffer(j.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(j.DRAW_FRAMEBUFFER,null)}else if(K!==0||w.isRenderTargetTexture||Yt.has(w)){const Vn=Yt.get(w),yn=Yt.get(Q);Qt.bindFramebuffer(j.READ_FRAMEBUFFER,xc),Qt.bindFramebuffer(j.DRAW_FRAMEBUFFER,Ds);for(let cn=0;cn<Pt;cn++)_e?j.framebufferTextureLayer(j.READ_FRAMEBUFFER,j.COLOR_ATTACHMENT0,Vn.__webglTexture,K,Kt+cn):j.framebufferTexture2D(j.READ_FRAMEBUFFER,j.COLOR_ATTACHMENT0,j.TEXTURE_2D,Vn.__webglTexture,K),zn?j.framebufferTextureLayer(j.DRAW_FRAMEBUFFER,j.COLOR_ATTACHMENT0,yn.__webglTexture,xt,Ze+cn):j.framebufferTexture2D(j.DRAW_FRAMEBUFFER,j.COLOR_ATTACHMENT0,j.TEXTURE_2D,yn.__webglTexture,xt),K!==0?j.blitFramebuffer($t,ae,Ut,It,Ee,De,Ut,It,j.COLOR_BUFFER_BIT,j.NEAREST):zn?j.copyTexSubImage3D(dn,xt,Ee,De,Ze+cn,$t,ae,Ut,It):j.copyTexSubImage2D(dn,xt,Ee,De,$t,ae,Ut,It);Qt.bindFramebuffer(j.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(j.DRAW_FRAMEBUFFER,null)}else zn?w.isDataTexture||w.isData3DTexture?j.texSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,jt,Ye.data):Q.isCompressedArrayTexture?j.compressedTexSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,Ye.data):j.texSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,jt,Ye):w.isDataTexture?j.texSubImage2D(j.TEXTURE_2D,xt,Ee,De,Ut,It,ce,jt,Ye.data):w.isCompressedTexture?j.compressedTexSubImage2D(j.TEXTURE_2D,xt,Ee,De,Ye.width,Ye.height,ce,Ye.data):j.texSubImage2D(j.TEXTURE_2D,xt,Ee,De,Ut,It,ce,jt,Ye);j.pixelStorei(j.UNPACK_ROW_LENGTH,Ue),j.pixelStorei(j.UNPACK_IMAGE_HEIGHT,Gn),j.pixelStorei(j.UNPACK_SKIP_PIXELS,ia),j.pixelStorei(j.UNPACK_SKIP_ROWS,En),j.pixelStorei(j.UNPACK_SKIP_IMAGES,Us),xt===0&&Q.generateMipmaps&&j.generateMipmap(dn),Qt.unbindTexture()},this.copyTextureToTexture3D=function(w,Q,st=null,rt=null,K=0){return w.isTexture!==!0&&(xo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),st=arguments[0]||null,rt=arguments[1]||null,w=arguments[2],Q=arguments[3],K=arguments[4]||0),xo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(w,Q,st,rt,K)},this.initRenderTarget=function(w){Yt.get(w).__webglFramebuffer===void 0&&O.setupRenderTarget(w)},this.initTexture=function(w){w.isCubeTexture?O.setTextureCube(w,0):w.isData3DTexture?O.setTexture3D(w,0):w.isDataArrayTexture||w.isCompressedArrayTexture?O.setTexture2DArray(w,0):O.setTexture2D(w,0),Qt.unbindTexture()},this.resetState=function(){L=0,P=0,G=null,Qt.reset(),Ve.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ua}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const n=this.getContext();n.drawingBufferColorspace=Pe._getDrawingBufferColorSpace(t),n.unpackColorSpace=Pe._getUnpackColorSpace()}}const MS={name:"CopyShader",uniforms:{tDiffuse:{value:null},opacity:{value:1}},vertexShader:`

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


		}`};class yc{constructor(){this.isPass=!0,this.enabled=!0,this.needsSwap=!0,this.clear=!1,this.renderToScreen=!1}setSize(){}render(){console.error("THREE.Pass: .render() must be implemented in derived pass.")}dispose(){}}const fN=new mS(-1,1,1,-1,0,1);class dN extends Vi{constructor(){super(),this.setAttribute("position",new Cn([-1,3,0,-1,-1,0,3,-1,0],3)),this.setAttribute("uv",new Cn([0,2,0,0,2,0],2))}}const hN=new dN;class ES{constructor(t){this._mesh=new Wn(hN,t)}dispose(){this._mesh.geometry.dispose()}render(t){t.render(this._mesh,fN)}get material(){return this._mesh.material}set material(t){this._mesh.material=t}}class pN extends yc{constructor(t,n){super(),this.textureID=n!==void 0?n:"tDiffuse",t instanceof Yn?(this.uniforms=t.uniforms,this.material=t):t&&(this.uniforms=_f.clone(t.uniforms),this.material=new Yn({name:t.name!==void 0?t.name:"unspecified",defines:Object.assign({},t.defines),uniforms:this.uniforms,vertexShader:t.vertexShader,fragmentShader:t.fragmentShader})),this.fsQuad=new ES(this.material)}render(t,n,s){this.uniforms[this.textureID]&&(this.uniforms[this.textureID].value=s.texture),this.fsQuad.material=this.material,this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(n),this.clear&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),this.fsQuad.render(t))}dispose(){this.material.dispose(),this.fsQuad.dispose()}}class Jy extends yc{constructor(t,n){super(),this.scene=t,this.camera=n,this.clear=!0,this.needsSwap=!1,this.inverse=!1}render(t,n,s){const o=t.getContext(),c=t.state;c.buffers.color.setMask(!1),c.buffers.depth.setMask(!1),c.buffers.color.setLocked(!0),c.buffers.depth.setLocked(!0);let f,d;this.inverse?(f=0,d=1):(f=1,d=0),c.buffers.stencil.setTest(!0),c.buffers.stencil.setOp(o.REPLACE,o.REPLACE,o.REPLACE),c.buffers.stencil.setFunc(o.ALWAYS,f,4294967295),c.buffers.stencil.setClear(d),c.buffers.stencil.setLocked(!0),t.setRenderTarget(s),this.clear&&t.clear(),t.render(this.scene,this.camera),t.setRenderTarget(n),this.clear&&t.clear(),t.render(this.scene,this.camera),c.buffers.color.setLocked(!1),c.buffers.depth.setLocked(!1),c.buffers.color.setMask(!0),c.buffers.depth.setMask(!0),c.buffers.stencil.setLocked(!1),c.buffers.stencil.setFunc(o.EQUAL,1,4294967295),c.buffers.stencil.setOp(o.KEEP,o.KEEP,o.KEEP),c.buffers.stencil.setLocked(!0)}}class mN extends yc{constructor(){super(),this.needsSwap=!1}render(t){t.state.buffers.stencil.setLocked(!1),t.state.buffers.stencil.setTest(!1)}}class gN{constructor(t,n){if(this.renderer=t,this._pixelRatio=t.getPixelRatio(),n===void 0){const s=t.getSize(new Wt);this._width=s.width,this._height=s.height,n=new Gi(this._width*this._pixelRatio,this._height*this._pixelRatio,{type:Pa}),n.texture.name="EffectComposer.rt1"}else this._width=n.width,this._height=n.height;this.renderTarget1=n,this.renderTarget2=n.clone(),this.renderTarget2.texture.name="EffectComposer.rt2",this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2,this.renderToScreen=!0,this.passes=[],this.copyPass=new pN(MS),this.copyPass.material.blending=Oa,this.clock=new gS}swapBuffers(){const t=this.readBuffer;this.readBuffer=this.writeBuffer,this.writeBuffer=t}addPass(t){this.passes.push(t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}insertPass(t,n){this.passes.splice(n,0,t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}removePass(t){const n=this.passes.indexOf(t);n!==-1&&this.passes.splice(n,1)}isLastEnabledPass(t){for(let n=t+1;n<this.passes.length;n++)if(this.passes[n].enabled)return!1;return!0}render(t){t===void 0&&(t=this.clock.getDelta());const n=this.renderer.getRenderTarget();let s=!1;for(let o=0,c=this.passes.length;o<c;o++){const f=this.passes[o];if(f.enabled!==!1){if(f.renderToScreen=this.renderToScreen&&this.isLastEnabledPass(o),f.render(this.renderer,this.writeBuffer,this.readBuffer,t,s),f.needsSwap){if(s){const d=this.renderer.getContext(),p=this.renderer.state.buffers.stencil;p.setFunc(d.NOTEQUAL,1,4294967295),this.copyPass.render(this.renderer,this.writeBuffer,this.readBuffer,t),p.setFunc(d.EQUAL,1,4294967295)}this.swapBuffers()}Jy!==void 0&&(f instanceof Jy?s=!0:f instanceof mN&&(s=!1))}}this.renderer.setRenderTarget(n)}reset(t){if(t===void 0){const n=this.renderer.getSize(new Wt);this._pixelRatio=this.renderer.getPixelRatio(),this._width=n.width,this._height=n.height,t=this.renderTarget1.clone(),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.renderTarget1=t,this.renderTarget2=t.clone(),this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2}setSize(t,n){this._width=t,this._height=n;const s=this._width*this._pixelRatio,o=this._height*this._pixelRatio;this.renderTarget1.setSize(s,o),this.renderTarget2.setSize(s,o);for(let c=0;c<this.passes.length;c++)this.passes[c].setSize(s,o)}setPixelRatio(t){this._pixelRatio=t,this.setSize(this._width,this._height)}dispose(){this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.copyPass.dispose()}}class vN extends yc{constructor(t,n,s=null,o=null,c=null){super(),this.scene=t,this.camera=n,this.overrideMaterial=s,this.clearColor=o,this.clearAlpha=c,this.clear=!0,this.clearDepth=!1,this.needsSwap=!1,this._oldClearColor=new pe}render(t,n,s){const o=t.autoClear;t.autoClear=!1;let c,f;this.overrideMaterial!==null&&(f=this.scene.overrideMaterial,this.scene.overrideMaterial=this.overrideMaterial),this.clearColor!==null&&(t.getClearColor(this._oldClearColor),t.setClearColor(this.clearColor,t.getClearAlpha())),this.clearAlpha!==null&&(c=t.getClearAlpha(),t.setClearAlpha(this.clearAlpha)),this.clearDepth==!0&&t.clearDepth(),t.setRenderTarget(this.renderToScreen?null:s),this.clear===!0&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),t.render(this.scene,this.camera),this.clearColor!==null&&t.setClearColor(this._oldClearColor),this.clearAlpha!==null&&t.setClearAlpha(c),this.overrideMaterial!==null&&(this.scene.overrideMaterial=f),t.autoClear=o}}const _N={uniforms:{tDiffuse:{value:null},luminosityThreshold:{value:1},smoothWidth:{value:1},defaultColor:{value:new pe(0)},defaultOpacity:{value:0}},vertexShader:`

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

		}`};class qo extends yc{constructor(t,n,s,o){super(),this.strength=n!==void 0?n:1,this.radius=s,this.threshold=o,this.resolution=t!==void 0?new Wt(t.x,t.y):new Wt(256,256),this.clearColor=new pe(0,0,0),this.renderTargetsHorizontal=[],this.renderTargetsVertical=[],this.nMips=5;let c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);this.renderTargetBright=new Gi(c,f,{type:Pa}),this.renderTargetBright.texture.name="UnrealBloomPass.bright",this.renderTargetBright.texture.generateMipmaps=!1;for(let _=0;_<this.nMips;_++){const x=new Gi(c,f,{type:Pa});x.texture.name="UnrealBloomPass.h"+_,x.texture.generateMipmaps=!1,this.renderTargetsHorizontal.push(x);const E=new Gi(c,f,{type:Pa});E.texture.name="UnrealBloomPass.v"+_,E.texture.generateMipmaps=!1,this.renderTargetsVertical.push(E),c=Math.round(c/2),f=Math.round(f/2)}const d=_N;this.highPassUniforms=_f.clone(d.uniforms),this.highPassUniforms.luminosityThreshold.value=o,this.highPassUniforms.smoothWidth.value=.01,this.materialHighPassFilter=new Yn({uniforms:this.highPassUniforms,vertexShader:d.vertexShader,fragmentShader:d.fragmentShader}),this.separableBlurMaterials=[];const p=[3,5,7,9,11];c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);for(let _=0;_<this.nMips;_++)this.separableBlurMaterials.push(this.getSeperableBlurMaterial(p[_])),this.separableBlurMaterials[_].uniforms.invSize.value=new Wt(1/c,1/f),c=Math.round(c/2),f=Math.round(f/2);this.compositeMaterial=this.getCompositeMaterial(this.nMips),this.compositeMaterial.uniforms.blurTexture1.value=this.renderTargetsVertical[0].texture,this.compositeMaterial.uniforms.blurTexture2.value=this.renderTargetsVertical[1].texture,this.compositeMaterial.uniforms.blurTexture3.value=this.renderTargetsVertical[2].texture,this.compositeMaterial.uniforms.blurTexture4.value=this.renderTargetsVertical[3].texture,this.compositeMaterial.uniforms.blurTexture5.value=this.renderTargetsVertical[4].texture,this.compositeMaterial.uniforms.bloomStrength.value=n,this.compositeMaterial.uniforms.bloomRadius.value=.1;const m=[1,.8,.6,.4,.2];this.compositeMaterial.uniforms.bloomFactors.value=m,this.bloomTintColors=[new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1)],this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors;const v=MS;this.copyUniforms=_f.clone(v.uniforms),this.blendMaterial=new Yn({uniforms:this.copyUniforms,vertexShader:v.vertexShader,fragmentShader:v.fragmentShader,blending:Lp,depthTest:!1,depthWrite:!1,transparent:!0}),this.enabled=!0,this.needsSwap=!1,this._oldClearColor=new pe,this.oldClearAlpha=1,this.basic=new Sr,this.fsQuad=new ES(null)}dispose(){for(let t=0;t<this.renderTargetsHorizontal.length;t++)this.renderTargetsHorizontal[t].dispose();for(let t=0;t<this.renderTargetsVertical.length;t++)this.renderTargetsVertical[t].dispose();this.renderTargetBright.dispose();for(let t=0;t<this.separableBlurMaterials.length;t++)this.separableBlurMaterials[t].dispose();this.compositeMaterial.dispose(),this.blendMaterial.dispose(),this.basic.dispose(),this.fsQuad.dispose()}setSize(t,n){let s=Math.round(t/2),o=Math.round(n/2);this.renderTargetBright.setSize(s,o);for(let c=0;c<this.nMips;c++)this.renderTargetsHorizontal[c].setSize(s,o),this.renderTargetsVertical[c].setSize(s,o),this.separableBlurMaterials[c].uniforms.invSize.value=new Wt(1/s,1/o),s=Math.round(s/2),o=Math.round(o/2)}render(t,n,s,o,c){t.getClearColor(this._oldClearColor),this.oldClearAlpha=t.getClearAlpha();const f=t.autoClear;t.autoClear=!1,t.setClearColor(this.clearColor,0),c&&t.state.buffers.stencil.setTest(!1),this.renderToScreen&&(this.fsQuad.material=this.basic,this.basic.map=s.texture,t.setRenderTarget(null),t.clear(),this.fsQuad.render(t)),this.highPassUniforms.tDiffuse.value=s.texture,this.highPassUniforms.luminosityThreshold.value=this.threshold,this.fsQuad.material=this.materialHighPassFilter,t.setRenderTarget(this.renderTargetBright),t.clear(),this.fsQuad.render(t);let d=this.renderTargetBright;for(let p=0;p<this.nMips;p++)this.fsQuad.material=this.separableBlurMaterials[p],this.separableBlurMaterials[p].uniforms.colorTexture.value=d.texture,this.separableBlurMaterials[p].uniforms.direction.value=qo.BlurDirectionX,t.setRenderTarget(this.renderTargetsHorizontal[p]),t.clear(),this.fsQuad.render(t),this.separableBlurMaterials[p].uniforms.colorTexture.value=this.renderTargetsHorizontal[p].texture,this.separableBlurMaterials[p].uniforms.direction.value=qo.BlurDirectionY,t.setRenderTarget(this.renderTargetsVertical[p]),t.clear(),this.fsQuad.render(t),d=this.renderTargetsVertical[p];this.fsQuad.material=this.compositeMaterial,this.compositeMaterial.uniforms.bloomStrength.value=this.strength,this.compositeMaterial.uniforms.bloomRadius.value=this.radius,this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors,t.setRenderTarget(this.renderTargetsHorizontal[0]),t.clear(),this.fsQuad.render(t),this.fsQuad.material=this.blendMaterial,this.copyUniforms.tDiffuse.value=this.renderTargetsHorizontal[0].texture,c&&t.state.buffers.stencil.setTest(!0),this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(s),this.fsQuad.render(t)),t.setClearColor(this._oldClearColor,this.oldClearAlpha),t.autoClear=f}getSeperableBlurMaterial(t){const n=[];for(let s=0;s<t;s++)n.push(.39894*Math.exp(-.5*s*s/(t*t))/t);return new Yn({defines:{KERNEL_RADIUS:t},uniforms:{colorTexture:{value:null},invSize:{value:new Wt(.5,.5)},direction:{value:new Wt(.5,.5)},gaussianCoefficients:{value:n}},vertexShader:`varying vec2 vUv;
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
				}`})}}qo.BlurDirectionX=new Wt(1,0);qo.BlurDirectionY=new Wt(0,1);const nn={cyan:new pe("#29D3FF"),white:new pe("#EAF2FF"),violet:new pe("#8B7CFF"),amber:new pe("#FFB84D"),red:new pe("#FF5D73"),muted:new pe("#8EA0B8"),recovery:new pe("#2DD4A8")};function bS({mode:a,health:t,activityLevel:n,confidence:s,servers:o,visualEvents:c,activeServerId:f="",nextServerId:d="",approvalServerIds:p=[]}){const m=se.useRef(null),v=se.useRef({mode:a,health:t,activityLevel:n,confidence:s,servers:o,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}),_=se.useMemo(()=>df.map(x=>({id:x,label:ta(x)})),[]);return se.useEffect(()=>{v.current={mode:a,health:t,activityLevel:n,confidence:s,servers:o,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}},[a,t,n,s,o,c,f,d,p]),se.useEffect(()=>{const x=m.current;if(!x)return;const E=window.matchMedia("(prefers-reduced-motion: reduce)").matches,M=new iA,T=new _i(44,1,.1,100);T.position.set(0,0,7.2);const S=new uN({antialias:!0,alpha:!0,powerPreference:"high-performance"});S.setPixelRatio(Math.min(window.devicePixelRatio,2)),S.outputColorSpace=vi,x.appendChild(S.domElement);const y=new gN(S);y.addPass(new vN(M,T));const I=new qo(new Wt(1,1),.38,.45,.86);y.addPass(I);const D=new So;M.add(D);const C=new Yn({transparent:!0,depthWrite:!1,uniforms:{uTime:{value:0},uActivity:{value:.2},uColor:{value:nn.cyan.clone()},uGlow:{value:.55}},vertexShader:`
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
      `}),V=new Wn(new Ef(1.24,96,64),C);D.add(V);const L=new Wn(new yf(1.72,.018,12,160),new Sr({color:nn.amber,transparent:!0,opacity:0}));L.rotation.x=Math.PI/2.15,D.add(L);const P=new Wn(new yf(1.35,.015,12,160),new Sr({color:nn.recovery,transparent:!0,opacity:0}));P.rotation.x=Math.PI/2,D.add(P);const G=new Map;df.forEach((ct,B)=>{const Z=yN(ct,B);G.set(ct,Z),D.add(Z.group)}),M.add(new AA(9347256,.55));const U=new TA(15397631,1.3);U.position.set(0,0,4.8),M.add(U);const N=new gS,H=()=>{const ct=Math.max(1,x.clientWidth),B=Math.max(1,x.clientHeight);T.aspect=ct/B,T.updateProjectionMatrix(),S.setSize(ct,B,!1),y.setSize(ct,B),I.resolution.set(ct,B)},ut=new ResizeObserver(H);ut.observe(x),H();let ot=0;const mt=()=>{ot=requestAnimationFrame(mt);const ct=Math.min(N.getDelta(),.05),B=performance.now(),Z=v.current,$=Math.min(Math.max(Number(Z.activityLevel||1),0),8)/8,Et=E?0:.08+$*.42;D.userData.rotationSpeed=cs.damp(Number(D.userData.rotationSpeed||0),Et,2.6,ct),D.rotation.y+=Number(D.userData.rotationSpeed)*ct,V.rotation.x+=Number(D.userData.rotationSpeed)*ct*.42,C.uniforms.uTime.value+=ct,C.uniforms.uActivity.value=cs.damp(C.uniforms.uActivity.value,.25+$,3.2,ct),C.uniforms.uGlow.value=cs.damp(C.uniforms.uGlow.value,Z.health==="DEGRADED"?.9:Z.health==="OFFLINE"?.35:.62,2.5,ct),C.uniforms.uColor.value.lerp(Z.health==="OFFLINE"?nn.red:Z.health==="DEGRADED"?nn.amber:nn.cyan,1-Math.exp(-ct*2.8));const At=E?1:1+Math.sin(B*.0016)*(.018+$*.018);V.scale.setScalar(At);const z=Z.events.filter(q=>q.expiresAt>Date.now());let nt=0,St=0;for(const q of G.values()){xN(q,Z,z,B),q.color.lerp(q.targetColor,1-Math.exp(-ct*5.5)),q.opacity=cs.damp(q.opacity,q.targetOpacity,5.5,ct);for(const ft of[...q.segments,...q.filaments]){const Tt=ft.material;Tt.color.copy(q.color);const Mt=ft.userData.mid.clone();Mt.applyMatrix4(D.matrixWorld);const Ft=Mt.z>=0?1:.34;Tt.opacity=q.opacity*Ft*Number(ft.userData.opacityScale||1),ft.visible=!!ft.userData.enabled}q.marker.material.color.copy(q.color),q.marker.material.opacity=Math.min(1,q.opacity+.25),q.group.scale.setScalar(cs.damp(q.group.scale.x,Number(q.group.userData.targetScale||1),8,ct)),q.group.userData.containment&&(nt=Math.max(nt,Number(q.group.userData.effectStrength||0))),q.group.userData.recovery&&(St=Math.max(St,Number(q.group.userData.effectStrength||0)))}L.material.opacity=cs.damp(L.material.opacity,Math.min(.58,nt),6,ct),P.material.opacity=cs.damp(P.material.opacity,Math.min(.72,St),5,ct),P.scale.setScalar(1+St*1.25),E||(P.rotation.z+=ct*1.2),T.position.z=cs.damp(T.position.z,Z.mode==="EXECUTING"?6.6:7.25,1.8,ct),y.render()};return mt(),()=>{cancelAnimationFrame(ot),ut.disconnect(),y.dispose(),SN(M),S.dispose(),S.domElement.remove()}},[]),g.jsxs("div",{className:"core-sphere","data-testid":"core-sphere","data-mode":a,"data-health":t,children:[g.jsx("div",{ref:m,className:"core-canvas",role:"img","aria-label":`AEGIS core sphere. Mode ${a}, health ${t}.`}),g.jsx("div",{className:"core-legend","aria-label":"Core server arcs",children:_.map(x=>g.jsxs("span",{className:"core-legend__item","data-server":x.id,children:[g.jsx("i",{"aria-hidden":"true"}),x.label]},x.id))}),g.jsxs("div",{className:"muted mono core-caption",children:["Mode: ",a," / Health: ",t," / Confidence: ",s]})]})}function yN(a,t){const n=new So;n.rotation.set(t*.37,t*.71,t*.23);const s=2.05,o=t/df.length*Math.PI,c=[Yl(s,o+.1,o+Math.PI*.68,.018),Yl(s,o+Math.PI*.78,o+Math.PI*1.34,.018),Yl(s,o+Math.PI*1.46,o+Math.PI*2-.1,.018)],f=Yl(s+.16,o+.25,o+Math.PI*1.75,.006),d=Yl(s-.17,o+Math.PI*.08,o+Math.PI*1.92,.005);f.rotation.x=.18,d.rotation.y=-.14;const p=new Wn(new Ef(.055,20,20),new Sr({color:nn.cyan,transparent:!0,opacity:.8}));p.position.copy(xm(s+.07,o+t*.24));for(const m of[...c,f,d,p])n.add(m);return{serverId:a,group:n,segments:c,filaments:[f,d],marker:p,color:nn.cyan.clone(),targetColor:nn.cyan.clone(),opacity:.42,targetOpacity:.42}}function Yl(a,t,n,s){const o=[];for(let v=0;v<=64;v+=1){const _=t+(n-t)*v/64;o.push(xm(a,_))}const f=new dS(o),d=new Vm(f,72,s,8,!1),p=new Sr({color:nn.cyan,transparent:!0,opacity:.4,depthWrite:!1}),m=new Wn(d,p);return m.userData.mid=xm(a,(t+n)/2),m.userData.enabled=!0,m.userData.opacityScale=s<.01?.42:1,m}function xm(a,t){return new W(Math.cos(t)*a,Math.sin(t)*a,Math.sin(t*1.7)*.18)}function xN(a,t,n,s){const o=t.servers.find(p=>p.server_id===a.serverId),c=String((o==null?void 0:o.status)||"UNCONFIGURED").toUpperCase(),f=n.find(p=>p.serverId===a.serverId),d=f?Math.max(0,Math.min(1,(f.expiresAt-Date.now())/Math.max(1,f.expiresAt-f.createdAt))):0;a.group.userData.targetScale=1,a.group.userData.effectStrength=d,a.group.userData.containment=!1,a.group.userData.recovery=!1,a.targetColor.copy(nn.cyan),a.targetOpacity=.5,a.segments.forEach(p=>{p.userData.enabled=!0}),(c==="UNCONFIGURED"||c==="DISABLED")&&(a.targetColor.copy(nn.muted),a.targetOpacity=.22),c==="OFFLINE"&&(a.targetColor.copy(nn.muted),a.targetOpacity=.26,a.segments[1].userData.enabled=!1),c==="DEGRADED"&&(a.targetColor.copy(nn.amber),a.targetOpacity=.58+Math.sin(s*.018)*.08),t.nextServerIds.has(a.serverId)&&(a.targetColor.copy(nn.violet),a.targetOpacity=.72),t.approvalServerIds.has(a.serverId)&&(a.targetColor.copy(nn.amber),a.targetOpacity=.86,a.group.userData.containment=!0),t.activeServerId===a.serverId&&(a.targetColor.copy(nn.white).lerp(nn.cyan,.28),a.targetOpacity=.94,a.group.userData.targetScale=1.02),f&&(f.effect==="fracture"?(a.targetColor.copy(nn.red),a.targetOpacity=.96,a.group.userData.targetScale=1+d*.04):f.effect==="containment"?(a.targetColor.copy(nn.amber),a.group.userData.containment=!0,a.targetOpacity=.96):f.effect==="recovery"?(a.targetColor.copy(nn.recovery),a.group.userData.recovery=!0,a.targetOpacity=.98):f.effect==="complete"||f.effect==="pulse"?(a.targetColor.copy(nn.white).lerp(nn.cyan,.2),a.targetOpacity=.86+d*.14,a.group.userData.targetScale=1+d*.035):f.effect==="disconnect"&&(a.segments[1].userData.enabled=!1,a.targetColor.copy(nn.red),a.targetOpacity=.64))}function SN(a){a.traverse(t=>{const n=t;n.geometry&&n.geometry.dispose();const s=n.material;Array.isArray(s)?s.forEach(o=>o.dispose()):s&&s.dispose()})}function MN({overview:a,recentEvents:t}){var S,y,I,D,C,V;const n=a.core.data,s=a.servers.data.items||[],o=a.current_task.data,c=a.usage.data,f=((S=a.user_situation)==null?void 0:S.data)||a.user_state.data||{},d=a.commitments.data.items||[],p=((y=a.errors)==null?void 0:y.data.items)||[],m=((I=a.connection)==null?void 0:I.data)||{},v=cb(s),_=Nm(a),x=s.filter(L=>Rm(L)),E=wm(a),M=[...a.attention.data.items||[],...p].filter(L=>String(L.severity||"").toLowerCase()==="critical").length,T=[...t.map(L=>({id:L.event_id||`${L.type}-${L.source_updated_at}`,title:L.safe_title||L.type,message:L.safe_message||L.message||L.source_type,priority:L.priority||"P3"})),...(((D=a.activity)==null?void 0:D.data.recent)||[]).map((L,P)=>({id:String(L.event_id||P),title:String(L.title||L.type||"Activity"),message:String(L.message||L.event_type||""),priority:String(L.priority||"P3")})),...(a.notifications.data.recent||[]).map((L,P)=>({id:String(L.notification_id||L.id||P),title:String(L.title||"Notification"),message:String(L.message||L.severity||""),priority:"P3"}))].slice(0,8);return g.jsxs("div",{className:"command-center",children:[g.jsxs("section",{className:"command-hud","aria-label":"Command HUD",children:[g.jsx(_o,{icon:g.jsx(kE,{size:16}),label:"Core",value:`${String(n.mode||"IDLE")} / ${String(n.health||"ONLINE")}`}),g.jsx(_o,{icon:g.jsx(Up,{size:16}),label:"Phase",value:E}),g.jsx(_o,{icon:g.jsx(W0,{size:16}),label:"Connection",value:`${m.online_count??v.ok}/${m.total_count??s.length} online`}),g.jsx(_o,{icon:g.jsx(rc,{size:16}),label:"Approvals",value:String(n.pending_approval_count??a.approvals.data.pending_count??0)}),g.jsx(_o,{icon:g.jsx(X0,{size:16}),label:"Profile",value:String(((C=a.mind_summary.data.autonomy)==null?void 0:C.profile)||n.attention_level||"normal")}),g.jsx(_o,{icon:g.jsx(zE,{size:16}),label:"Freshness",value:a.freshness.stale?"STALE":"LIVE"})]}),g.jsxs("section",{className:"command-attention",children:[g.jsx(Ab,{items:a.attention.data.items||[]}),g.jsx(rb,{stale:a.attention.stale,error:a.attention.error,empty:(a.attention.data.items||[]).length===0&&M>0,label:"Attention"})]}),g.jsxs("section",{className:"command-grid-12",children:[g.jsxs("article",{className:"panel command-operation command-span-8",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Current Operation"}),g.jsx("div",{className:"muted mono",children:o.task_id||"no active task id"})]}),g.jsx(oc,{status:String(n.mode||"IDLE")})]}),g.jsx("h3",{children:o.title||"No active task"}),g.jsx("p",{className:"command-operation__action",children:o.current_action||o.next_action||o.blocked_reason||"AEGIS is waiting for a meaningful signal or user request."}),g.jsxs("div",{className:"operation-map","aria-label":"Operation map",children:[g.jsx("span",{"data-active":"true",children:"Observe"}),g.jsx("span",{"data-active":E==="Planning",children:"Plan"}),g.jsx("span",{"data-active":E==="Executing",children:"Execute"}),g.jsx("span",{"data-active":!!o.verification_summary,children:"Verify"}),g.jsx("span",{"data-active":String(o.phase).toLowerCase()==="completed",children:"Complete"})]}),g.jsxs("div",{className:"mission-strip","aria-label":"Mission context",children:[g.jsxs("span",{children:["Next: ",g.jsx("strong",{children:o.next_action||"No data yet"})]}),g.jsxs("span",{children:["Capability: ",g.jsx("strong",{children:o.capability_id||"No data yet"})]}),g.jsxs("span",{children:["Verification: ",g.jsx("strong",{children:o.verification_summary||"No data yet"})]}),g.jsxs("span",{children:["Blocked: ",g.jsx("strong",{children:o.blocked_reason||"No"})]})]})]}),g.jsxs("article",{className:"panel command-ai-state command-span-4",children:[g.jsxs("div",{className:"panel__header",children:[g.jsx("h2",{children:"AI State"}),g.jsx(lr,{...af(a.core)})]}),g.jsx(nf,{icon:g.jsx(X0,{size:18}),label:"Active goal",value:String(n.active_goal||"No active goal"),compact:!0}),g.jsx(nf,{icon:g.jsx(Up,{size:18}),label:"Confidence",value:String(n.confidence||"No data yet"),compact:!0}),g.jsx(nf,{icon:g.jsx(BE,{size:18}),label:"LLM budget",value:String(c.budget_state||c.autonomous_suppression||c.cost_state||"No data yet"),compact:!0}),g.jsx(nf,{icon:g.jsx(rc,{size:18}),label:"Critical",value:String(M),compact:!0})]}),g.jsx("section",{className:"panel core-card command-span-8",children:g.jsx(bS,{mode:String(n.mode||"IDLE"),health:String(n.health||"ONLINE"),activityLevel:Number(n.activity_level||1),confidence:String(n.confidence||"medium"),servers:s,visualEvents:[],activeServerId:String(o.capability_id||"").split(".",1)[0],nextServerId:EN(o),approvalServerIds:(a.approvals.data.pending||[]).map(L=>String(L.capability_id||"").split(".",1)[0])})}),g.jsxs("section",{className:"panel command-situation command-span-4",children:[g.jsxs("div",{className:"panel__header",children:[g.jsx("h2",{children:"Situation"}),g.jsx(QE,{size:16})]}),g.jsxs("div",{className:"metric-list",children:[g.jsx(Ql,{label:"User",value:String(f.summary||f.availability||"No data yet")}),g.jsx(Ql,{label:"Commitments",value:a.commitments.data.summary||`${d.length} active`}),g.jsx(Ql,{label:"Usage",value:String(c.summary||c.total_tokens||"Audit-backed")}),g.jsx(Ql,{label:"Open issues",value:String(p.length||((V=a.errors)==null?void 0:V.data.count)||0)})]})]}),g.jsxs("section",{className:"panel command-span-4 server-summary-card",children:[g.jsxs("div",{className:"panel__header",children:[g.jsx("h2",{children:"Systems"}),g.jsx(lr,{...af(a.servers)})]}),g.jsxs("div",{className:"server-summary-line",children:[g.jsx(W0,{size:18}),g.jsxs("strong",{children:[v.ok," normal"]}),g.jsxs("span",{children:[v.attention.length," need attention"]})]}),g.jsx("div",{className:"compact-list",children:x.length?x.slice(0,4).map(L=>g.jsxs("div",{className:"list-row",children:[g.jsxs("div",{children:[g.jsx("strong",{children:ta(L.server_id)}),g.jsx("div",{className:"muted",children:L.status_detail||L.degraded_reason||L.recovery_hint||"Review server status."})]}),g.jsx(oc,{status:L.status,detail:L.recovery_hint})]},L.server_id)):g.jsx("p",{className:"muted",children:"All configured systems are operating normally."})})]}),g.jsxs("section",{className:"panel command-span-4",children:[g.jsxs("div",{className:"panel__header",children:[g.jsx("h2",{children:"Memory & Mind"}),g.jsx(lr,{...af(a.mind_summary)})]}),g.jsx("div",{className:"metric-list",children:Object.entries(_).map(([L,P])=>g.jsx(Ql,{label:L,value:P},L))})]}),g.jsxs("section",{className:"panel command-span-4",children:[g.jsxs("div",{className:"panel__header",children:[g.jsx("h2",{children:"Recent Operation Timeline"}),g.jsx(lr,{...af(a.activity||a.notifications)})]}),g.jsx("div",{className:"timeline-list",children:T.length?T.map(L=>g.jsxs("div",{className:"timeline-item","data-priority":L.priority,children:[g.jsx("span",{children:L.priority}),g.jsxs("div",{children:[g.jsx("strong",{children:L.title}),g.jsx("p",{children:L.message})]})]},L.id)):g.jsx("p",{className:"muted",children:"No recent events reported."})})]})]})]})}function _o({icon:a,label:t,value:n}){return g.jsxs("div",{className:"hud-metric",children:[g.jsxs("span",{children:[a,t]}),g.jsx("strong",{children:n})]})}function nf({icon:a,label:t,value:n,compact:s=!1}){return g.jsxs("div",{className:s?"stat stat--compact":"stat",children:[g.jsxs("span",{className:"muted",children:[a," ",t]}),g.jsx("b",{children:n})]})}function Ql({label:a,value:t}){return g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:a}),g.jsx("strong",{children:t})]})}function EN(a){const t=(a.steps||[]).find(n=>["pending","ready"].includes(String(n.status||"").toLowerCase()));return String((t==null?void 0:t.capability_id)||"").split(".",1)[0]||""}function af(a){return{generatedAt:a.generated_at,sourceUpdatedAt:a.source_updated_at,stale:a.stale}}function bN({overview:a}){var T;const[t,n]=se.useState(a),[s,o]=se.useState([]),[c,f]=se.useState([]);se.useEffect(()=>n(a),[a]);const d=se.useCallback(S=>{if("schema_version"in S){n(S);return}o(I=>[S,...I].slice(0,10));const y=zx(S);f(I=>[y,...I.filter(D=>D.expiresAt>Date.now())].slice(0,12))},[]);Ox(d,!0,"display");const p=t.core.data,m=t.servers.data.items||[],v=t.current_task.data,_=Ix(t),x=String(v.capability_id||"").split(".",1)[0],E=wm(t),M=ub(t,s,c);return g.jsxs("main",{className:"display-shell","data-phase":E,"data-testid":"display-shell","data-priority":((T=M.takeover)==null?void 0:T.priority)||"P3","data-offline":M.offline,"data-stale":M.stale,"data-privacy":M.privacyMode,children:[g.jsxs("div",{className:"display-state-ribbon","aria-label":"Display state",children:[g.jsx("span",{children:M.offline?"OFFLINE SNAPSHOT":M.stale?"STALE SNAPSHOT":"LIVE DISPLAY"}),M.privacyMode?g.jsx("span",{children:"PRIVACY MODE"}):null]}),g.jsxs("div",{className:"display-global-hud","aria-label":"Display HUD",children:[g.jsx("strong",{children:"AEGIS"}),g.jsx("span",{children:E}),g.jsxs("span",{children:[m.filter(S=>hf(S.status)==="ONLINE").length,"/",m.length||0," online"]})]}),M.takeover?g.jsxs("section",{className:"display-takeover","data-priority":M.takeover.priority,"aria-label":"Display takeover",children:[g.jsxs("span",{className:"display-kicker",children:[M.takeover.priority," / ",M.takeover.severity]}),g.jsx("strong",{children:er(M.takeover.title,M.privacyMode)}),g.jsx("p",{children:M.privacyMode?"Private information hidden.":M.takeover.message})]}):null,M.overlays.length?g.jsx("aside",{className:"display-overlay-stack","aria-label":"Important overlays",children:M.overlays.map(S=>g.jsxs("article",{className:"display-overlay","data-priority":S.priority,"data-severity":S.severity,children:[g.jsx("span",{children:S.priority}),g.jsx("strong",{children:S.title}),g.jsx("p",{children:S.message})]},S.id))}):null,g.jsxs("header",{className:"display-top",children:[g.jsxs("section",{className:"display-card display-operation","aria-label":"Current Operation",children:[g.jsx("span",{className:"display-kicker",children:"Current Operation"}),g.jsx("h1",{children:er(v.title||"No active task",M.privacyMode)}),g.jsx("p",{children:er(v.current_action||v.next_action||v.blocked_reason||"Waiting for a meaningful signal.",M.privacyMode)}),g.jsxs("div",{className:"display-meta",children:[g.jsx(oc,{status:String(p.mode||"IDLE")}),g.jsx("span",{children:E})]})]}),_.length?g.jsxs("section",{className:"display-card display-attention","aria-label":"Attention",children:[g.jsx("span",{className:"display-kicker",children:"Attention"}),_.slice(0,4).map(S=>g.jsxs("article",{className:"display-attention__item","data-severity":S.severity,children:[g.jsx("strong",{children:er(S.title,M.privacyMode)}),g.jsx("p",{children:er(S.message||S.recovery_hint||"Review this signal.",M.privacyMode)})]},S.id))]}):null]}),g.jsx("section",{className:"display-core-stage","aria-label":"AEGIS core",children:g.jsx(bS,{mode:String(p.mode||"IDLE"),health:String(p.health||"ONLINE"),activityLevel:Number(p.activity_level||1),confidence:String(p.confidence||"medium"),servers:m,visualEvents:c,activeServerId:x,nextServerId:AN(v.steps),approvalServerIds:(t.approvals.data.pending||[]).map(S=>String(S.capability_id||"").split(".",1)[0])})}),g.jsxs("section",{className:"display-bottom",children:[g.jsxs("div",{className:"display-card display-phase",children:[g.jsx("span",{className:"display-kicker",children:"Mission Phase"}),g.jsx("strong",{children:E}),g.jsx("p",{children:er(String(p.active_goal||v.title||"Standing by."),M.privacyMode)})]}),g.jsxs("div",{className:"display-card display-events","aria-label":"Recent Events",children:[g.jsx("span",{className:"display-kicker",children:"Recent Events"}),M.dock.length||M.ambient.length?[...M.dock,...M.ambient].slice(0,6).map(S=>g.jsxs("div",{className:"event-row","data-severity":S.severity||"info","data-priority":S.priority,children:[g.jsx("span",{children:S.priority}),g.jsx("strong",{children:er(S.message||S.title,M.privacyMode)})]},S.id)):g.jsxs("div",{className:"event-row","data-severity":M.offline||M.stale?"warning":"normal",children:[g.jsx("span",{children:M.offline?"offline":M.stale?"stale":"stream"}),g.jsx("strong",{children:M.offline?"Showing last known snapshot":M.stale?"Waiting for fresh events":"Waiting for live events"})]})]})]}),g.jsx(TN,{servers:m,activeServerId:x})]})}function TN({servers:a,activeServerId:t}){const n=se.useMemo(()=>[...a].sort((s,o)=>ta(s.server_id).localeCompare(ta(o.server_id))),[a]);return g.jsx("footer",{className:"server-rail","aria-label":"Server rail",children:n.map(s=>{const o=Rm(s,t);return g.jsxs("article",{className:"server-rail__item","data-status":hf(s.status),"data-expanded":o,children:[g.jsx("span",{className:"server-dot","aria-hidden":"true"}),g.jsx("strong",{children:ta(s.server_id)}),o?g.jsx("span",{className:"server-rail__detail",children:s.status_detail||s.degraded_reason||s.recovery_hint||hf(s.status)}):null]},s.server_id)})})}function AN(a){const t=(a||[]).find(s=>String(s.status||"").toLowerCase()==="pending"||String(s.status||"").toLowerCase()==="ready");return String((t==null?void 0:t.capability_id)||"").split(".",1)[0]||""}function er(a,t){return t?"Private information hidden":a}function CN({overview:a}){var c,f;const t=Nm(a),n=a.mind_summary.data.memory,s=a.user_state.data,o=a.commitments.data.items||[];return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsxs("div",{children:[g.jsx("h2",{children:"Mind & Memory"}),g.jsx("div",{className:"muted",children:"Operational summary, not raw internal state."})]})}),g.jsx("div",{className:"stat-grid",children:Object.entries(t).map(([d,p])=>g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:d}),g.jsx("b",{className:"stat__value",children:p})]},d))})]}),g.jsxs("div",{className:"grid grid--three",children:[g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Memory Stores"})}),g.jsx("div",{className:"metric-list",children:["advanced","episodic","semantic","procedural","skill","lesson","workflow","experiential"].map(d=>g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:d}),g.jsx("strong",{children:RN((n||{})[d])})]},d))})]}),g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"User Situation"})}),g.jsxs("div",{className:"metric-list",children:[g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Status"}),g.jsx("strong",{children:String(s.summary||s.status||"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Available"}),g.jsx("strong",{children:String(s.available??"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Updated"}),g.jsx("strong",{children:a.user_state.stale?"STALE":"LIVE"})]})]})]}),g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Commitments"})}),g.jsxs("div",{className:"metric-list",children:[g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Open commitments"}),g.jsx("strong",{children:o.length})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Next commitment"}),g.jsx("strong",{children:String(((c=o[0])==null?void 0:c.title)||((f=o[0])==null?void 0:f.summary)||"No data yet")})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Summary"}),g.jsx("strong",{children:a.commitments.data.summary||"No data yet"})]})]})]})]}),g.jsxs("details",{className:"developer-drawer",children:[g.jsx("summary",{children:"Developer raw state"}),g.jsx("pre",{className:"mono muted",children:JSON.stringify({mind_summary:a.mind_summary.data,user_state:a.user_state.data,commitments:a.commitments.data},null,2)})]})]})}function RN(a){if(a==null)return"No data yet";if(typeof a=="number"||typeof a!="object")return String(a);const t=a,n=t.total||t.total_entries||t.total_episodes||t.entities||t.facts||t.active;if(n!==void 0)return String(n);const s=Object.keys(t);return s.length?`${s.length} fields`:"Empty"}function wN({overview:a}){var x,E,M,T;const t=hb(a),[n,s]=se.useState({}),[o,c]=se.useState(!0),[f,d]=se.useState(""),p=se.useMemo(()=>NN(n),[n]);se.useEffect(()=>{let S=!1;return c(!0),Bh().then(y=>{S||s(y)}).catch(y=>{S||d(y instanceof Error?y.message:"Settings unavailable")}).finally(()=>{S||c(!1)}),()=>{S=!0}},[]);const m=async(S,y,I)=>{d("Saving...");try{await tb(S,y,I),s(await Bh()),d("Saved. Effective settings updated through SettingsStore.")}catch(D){const C=D instanceof Error?D.message:"Save failed";d(C.includes("fresh_passkey_required")?"Fresh passkey authentication required. Reopen login, authenticate, then retry.":C)}},v=async()=>{d("Resetting...");try{await eb(),s(await Bh()),d("Settings reset to defaults.")}catch(S){d(S instanceof Error?S.message:"Reset failed")}},_={autonomy:Y0,permissions:Nx,servers:WE,privacy:jE,notifications:Ax,models:Cx,budgets:NE,memory:FE,display:wx,developer:IE,backup:HE};return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Settings"}),g.jsx("div",{className:"muted",children:"V2 settings surface. Sensitive changes remain protected by passkey fresh auth and CSRF."})]}),g.jsxs("a",{className:"primary-button",href:"/dashboard/security/passkeys",children:[g.jsx(VE,{size:16})," Passkeys"]})]}),g.jsx("div",{className:"settings-grid",children:t.map(S=>{const y=_[S.id]||Y0;return g.jsxs("article",{className:"settings-tile",children:[g.jsx("div",{className:"settings-tile__icon",children:g.jsx(y,{size:18,"aria-hidden":"true"})}),g.jsxs("div",{children:[g.jsx("strong",{children:S.label}),g.jsx("p",{children:S.summary}),g.jsx("span",{className:"muted",children:S.status})]})]},S.id)})})]}),g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Operational Settings"}),g.jsx("div",{className:"muted",children:"Loaded from SettingsStore. POST changes use CSRF and fresh passkey protection."})]}),g.jsxs("div",{className:"settings-actions",children:[g.jsx("a",{className:"secondary-button",href:"/api/settings/export",children:"Export"}),g.jsx("button",{className:"danger-button",onClick:v,type:"button",children:"Reset"})]})]}),f?g.jsx("div",{className:"attention-item","data-severity":f.includes("required")||f.includes("failed")?"warning":"info",children:f}):null,o?g.jsx("div",{className:"muted",children:"Loading settings..."}):null,g.jsxs("div",{className:"settings-editor",children:[p.map(S=>g.jsxs("label",{className:"settings-control",children:[g.jsxs("span",{children:[g.jsx("strong",{children:S.label}),g.jsxs("small",{children:[S.section,".",S.key]})]}),typeof S.value=="boolean"?g.jsx("input",{type:"checkbox",checked:S.value,onChange:y=>void m(S.section,S.key,y.currentTarget.checked)}):typeof S.value=="number"?g.jsx("input",{type:"number",value:S.value,onChange:y=>void m(S.section,S.key,Number(y.currentTarget.value))}):g.jsx("input",{value:String(S.value??""),onChange:y=>void m(S.section,S.key,y.currentTarget.value)})]},`${S.section}.${S.key}`)),!p.length&&!o?g.jsx("div",{className:"muted",children:"No simple editable settings were reported."}):null]})]}),g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Surface Roles"}),g.jsx("div",{className:"muted",children:"PresentationEvent routing contract. Each device renders the same event with its own limits."})]}),g.jsx("span",{className:"freshness","data-stale":((x=a.surface_roles)==null?void 0:x.stale)||!1,children:((E=a.surface_roles)==null?void 0:E.data.source)||"surface contract"})]}),g.jsxs("div",{className:"surface-role-grid",children:[(((M=a.surface_roles)==null?void 0:M.data.items)||[]).map(S=>g.jsxs("article",{className:"surface-role","data-interactive":S.interactive,children:[g.jsxs("div",{children:[g.jsx("strong",{children:S.surface_id.replace(/_/g," ")}),g.jsx("p",{children:S.role})]}),g.jsxs("div",{className:"surface-role__meta",children:[g.jsx("span",{children:S.interactive?"interactive":"read-only"}),g.jsx("span",{children:S.priorities.join("/")}),g.jsx("span",{children:S.privacy_levels.join("/")})]}),g.jsx("div",{className:"surface-role__scenes",children:S.scenes.slice(0,8).join(" / ")})]},S.surface_id)),(((T=a.surface_roles)==null?void 0:T.data.items)||[]).length?null:g.jsx("div",{className:"muted",children:"Surface role contract is not reported."})]})]}),g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Guardrails"})}),g.jsxs("div",{className:"metric-list",children:[g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Authentication"}),g.jsx("strong",{children:"Passkey-only in production"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Fresh auth"}),g.jsx("strong",{children:"Required for risk, approval, secrets, LLM, and dangerous operations"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Policy direction"}),g.jsx("strong",{children:"Settings can add restrictions; PolicyEngine must not be weakened by UI"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Legacy API"}),g.jsx("strong",{children:g.jsx("a",{href:"/api/settings",children:"Available for compatibility"})})]})]})]})]})}function NN(a){const t=new Set(["autonomous_loop_enabled","support_agent_enabled","self_dev_proposal_enabled","pc_server_enabled","android_server_enabled","browser_server_enabled","room_server_enabled","dev_server_enabled","clipboard_capture_enabled","camera_snapshot_enabled","display_privacy_mode","notifications_enabled","daily_budget_usd","monthly_budget_usd","memory_budget_tokens"]),n=[];for(const[s,o]of Object.entries(a))if(!(!o||typeof o!="object"||Array.isArray(o)))for(const[c,f]of Object.entries(o))!t.has(c)&&n.length>=24||(typeof f=="boolean"||typeof f=="number"||typeof f=="string")&&n.push({section:s,key:c,label:DN(c),value:f});return n.sort((s,o)=>Number(t.has(o.key))-Number(t.has(s.key))).slice(0,32)}function DN(a){return a.replace(/_/g," ").replace(/\b\w/g,t=>t.toUpperCase())}function UN({overview:a}){const t=a.servers.data.items||[],n=t.find(s=>s.server_id==="android-server");return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:"Systems"}),g.jsx("div",{className:"muted",children:"AI, PC, Android, Browser, Room, and Dev status with dependencies and recovery hints."})]}),g.jsx(lr,{generatedAt:a.servers.generated_at,sourceUpdatedAt:a.servers.source_updated_at,stale:a.servers.stale})]}),g.jsx("div",{className:"topology-row","aria-label":"Server topology",children:t.map((s,o)=>g.jsxs("div",{className:"topology-node","data-status":String(s.status||"").toUpperCase(),children:[g.jsx("strong",{children:ta(s.server_id)}),g.jsx("span",{children:s.mode||"unknown"}),o<t.length-1?g.jsx("i",{"aria-hidden":"true"}):null]},s.server_id))}),g.jsx("div",{className:"dependency-map","aria-label":"Server dependency map",children:t.map(s=>g.jsxs("div",{className:"dependency-map__row",children:[g.jsx("strong",{children:ta(s.server_id)}),g.jsx("span",{children:LN(s).join(" / ")||"No dependencies reported"})]},`${s.server_id}-deps`))})]}),g.jsx("section",{className:"systems-grid",children:t.map(s=>g.jsxs("article",{className:"panel system-card",children:[g.jsxs("div",{className:"panel__header",children:[g.jsxs("div",{children:[g.jsx("h2",{children:ta(s.server_id)}),g.jsx("div",{className:"muted mono",children:s.server_id})]}),g.jsx(oc,{status:s.status,detail:s.recovery_hint})]}),g.jsxs("div",{className:"metric-list",children:[g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Endpoint"}),g.jsxs("strong",{children:[s.host||"host",":",s.port||"-"]})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Mode"}),g.jsx("strong",{children:s.mode||"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Capabilities"}),g.jsx("strong",{children:s.registered_capabilities||"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Capability health"}),g.jsx("strong",{children:IN(s.capability_health)})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Latency"}),g.jsx("strong",{children:PN(s.latency_ms)})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Heartbeat age"}),g.jsx("strong",{children:s.heartbeat_age_seconds??"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Last healthy"}),g.jsx("strong",{children:ON(s)})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Active task"}),g.jsx("strong",{className:"mono",children:s.active_task_id||"No active task"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Permissions"}),g.jsx("strong",{children:zN(s.permission_missing)})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Version"}),g.jsx("strong",{children:s.version||"No data yet"})]}),g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Dependencies"}),g.jsx("strong",{children:pb(s)})]})]}),g.jsxs("div",{children:[g.jsx("div",{className:"muted",children:s.status_detail||s.degraded_reason||"No active issue reported."}),s.recovery_hint?g.jsx("div",{className:"recovery-hint",children:s.recovery_hint}):null]})]},s.server_id))}),g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Android Detail"})}),n?g.jsx(BN,{server:n}):g.jsx("p",{className:"muted",children:"Android status is not reported."})]})]})}function LN(a){const t=a.dependencies||{};return Object.entries(t).filter(([,n])=>typeof n=="boolean"||typeof n=="string"||typeof n=="number").slice(0,4).map(([n,s])=>`${n}:${String(s)}`)}function ON(a){const t=a.dependencies||{};return String(a.last_healthy_at||t.last_healthy_at||t.last_online_at||a.health_checked_at||t.last_seen||"No data yet")}function PN(a){return typeof a!="number"||Number.isNaN(a)?"No data yet":`${Math.round(a)} ms`}function zN(a){return a===!0?"Missing permission reported":a===!1||!a||!a.length?"None reported":a.join(", ")}function IN(a){if(!a||!Object.keys(a).length)return"No data yet";const t=Number(a.ok??a.available??0),n=Number(a.degraded??0),s=Number(a.unavailable??a.failed??0),o=[];return t&&o.push(`${t} ok`),n&&o.push(`${n} degraded`),s&&o.push(`${s} unavailable`),o.join(" / ")||Object.entries(a).slice(0,3).map(([c,f])=>`${c}:${String(f)}`).join(" / ")}function BN({server:a}){const t=a.dependencies||{},n=t.capability_availability||{},s=t.permission_status||{};return g.jsxs("div",{className:"android-detail",children:[g.jsxs("div",{className:"stat-grid",children:[g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Device"}),g.jsx("b",{children:String(t.device_model||"No data yet")})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Connection"}),g.jsx("b",{children:String(a.mode||t.connection_mode||"No data yet")})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Last seen"}),g.jsx("b",{children:String(t.last_seen||"No data yet")})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Active approvals"}),g.jsx("b",{children:Array.isArray(t.active_approvals)?t.active_approvals.length:0})]})]}),g.jsxs("div",{className:"grid grid--three",children:[g.jsxs("div",{children:[g.jsx("h3",{children:"Permissions"}),g.jsx("div",{className:"metric-list",children:Object.entries(s).length?Object.entries(s).map(([o,c])=>g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:o}),g.jsx("strong",{children:String(c)})]},o)):g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Status"}),g.jsx("strong",{children:"No data yet"})]})})]}),g.jsxs("div",{children:[g.jsx("h3",{children:"Capabilities"}),g.jsxs("div",{className:"metric-list",children:[Object.entries(n).slice(0,8).map(([o,c])=>g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{className:"mono",children:o.replace("android-server.","")}),g.jsx("strong",{children:String(c.available??"unknown")})]},o)),Object.entries(n).length?null:g.jsxs("div",{className:"metric-row",children:[g.jsx("span",{children:"Status"}),g.jsx("strong",{children:"No data yet"})]})]})]}),g.jsxs("div",{children:[g.jsx("h3",{children:"Recovery"}),g.jsx("p",{className:"muted",children:a.recovery_hint||"No recovery action needed."})]})]})]})}function FN({overview:a}){var v,_,x,E;const t=a.current_task.data,n=fb(a),s=t.steps||[],o=t.capability_id||String(((v=s.find(M=>String(M.status||"").toLowerCase()==="running"))==null?void 0:v.capability_id)||""),c=(a.approvals.data.pending||[]).filter(M=>M.task_id===t.task_id||M.capability_id===o),f=((x=(_=a.memory)==null?void 0:_.data)==null?void 0:x.summary)||((E=a.mind_summary.data)==null?void 0:E.memory)||{},d=a.usage.data||{},p=[...s].reverse().map(M=>HN(M)).find(Boolean),m=t.dependency_edges||[];return g.jsxs("div",{className:"grid",children:[g.jsxs("section",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsxs("div",{children:[g.jsx("h2",{children:"Work"}),g.jsx("div",{className:"muted",children:"Tasks grouped by operational state. Active task detail is shown on the right."})]})}),g.jsx("div",{className:"tab-strip",role:"tablist","aria-label":"Work queues",children:n.map(M=>g.jsxs("button",{className:"tab-chip",type:"button","aria-selected":M.id==="active",children:[g.jsx("span",{children:M.label}),g.jsx("strong",{children:M.count})]},M.id))})]}),g.jsxs("section",{className:"work-layout",children:[g.jsxs("div",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsx("h2",{children:"Task List"})}),g.jsx("div",{className:"grid",children:t.task_id||t.title?g.jsxs("article",{className:"list-row","data-selected":"true",children:[g.jsxs("div",{children:[g.jsx("strong",{children:t.title||"Untitled task"}),g.jsxs("div",{className:"muted",children:[t.phase||"unknown"," / ",s.length," step(s)"]})]}),g.jsx("span",{className:"status-badge","data-status":String(t.phase||"ACTIVE").toUpperCase(),children:t.phase||"active"})]}):g.jsx("div",{className:"attention-item","data-severity":"normal",children:"No active task. Scheduled and historical queues will appear here when reported by Overview v3."})})]}),g.jsxs("div",{className:"panel",children:[g.jsx("div",{className:"panel__header",children:g.jsxs("div",{children:[g.jsx("h2",{children:"Task Detail"}),g.jsx("div",{className:"muted mono",children:t.task_id||"No task id"})]})}),g.jsxs("div",{className:"stat-grid",children:[g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Objective"}),g.jsx("b",{children:t.title||"No data yet"})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Phase"}),g.jsx("b",{children:t.phase||"No data yet"})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Current capability"}),g.jsx("b",{className:"mono",children:o||"No data yet"})]}),g.jsxs("div",{className:"stat",children:[g.jsx("span",{className:"muted",children:"Execution server"}),g.jsx("b",{children:o?ta(Cm(o)):"No data yet"})]})]}),g.jsxs("div",{className:"task-narrative",children:[g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"Original instruction"}),g.jsx("strong",{children:String(t.original_instruction||t.title||t.task_id||"No data yet")})]}),g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"AI plan"}),g.jsx("strong",{children:String(t.plan_summary||"No data yet")})]}),g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"Current action"}),g.jsx("strong",{children:t.current_action||"No data yet"})]}),g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"Next action"}),g.jsx("strong",{children:t.next_action||"No data yet"})]}),g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"Blocked reason"}),g.jsx("strong",{children:t.blocked_reason||"Not blocked"})]}),g.jsxs("div",{children:[g.jsx("span",{className:"muted",children:"Latest result"}),g.jsx("strong",{children:p||"No data yet"})]})]}),g.jsxs("div",{className:"work-insight-grid","aria-label":"Task operational context",children:[g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Plan / Dependency"}),g.jsx("p",{className:"muted",children:s.length?`${s.length} step plan, ${m.length} dependency edge(s).`:"No step plan reported."})]}),g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Approvals"}),g.jsx("p",{className:"muted",children:c.length?`${c.length} approval waiting for this task.`:"No approval currently blocks this task."})]}),g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Memories Used"}),g.jsx("p",{className:"muted",children:VN(f)})]}),g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Model / Cost"}),g.jsx("p",{className:"muted",children:String(t.cost_summary||d.summary||d.total_tokens||d.cost||"No data yet")})]}),g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Completion / Verification"}),g.jsx("p",{className:"muted",children:t.verification_summary||GN(s)||"No verification result reported."})]}),g.jsxs("div",{className:"mini-panel",children:[g.jsx("h3",{children:"Audit / Output"}),g.jsxs("p",{className:"muted",children:[t.audit_group_id?`Audit ${t.audit_group_id}. `:"",String(t.final_output||t.result||"No data yet")]})]})]}),m.length?g.jsx("div",{className:"dependency-chain","aria-label":"Task dependency graph",children:m.slice(0,12).map((M,T)=>g.jsxs("span",{children:[String(M.from)," ","->"," ",String(M.to)]},`${String(M.from)}-${String(M.to)}-${T}`))}):null,g.jsxs("div",{className:"step-list",children:[s.map((M,T)=>g.jsxs("article",{className:"step-row",children:[g.jsx("span",{className:"step-index",children:T+1}),g.jsxs("div",{children:[g.jsx("strong",{children:String(M.description||M.capability_id||M.name||`Step ${T+1}`)}),g.jsx("div",{className:"muted mono",children:String(M.capability_id||M.name||"No capability reported")})]}),g.jsx("span",{className:"status-badge","data-status":String(M.status||"UNKNOWN").toUpperCase(),children:String(M.status||"unknown")})]},String(M.step_id||T))),s.length?null:g.jsx("div",{className:"attention-item","data-severity":"normal",children:"No step history reported."})]})]})]})]})}function HN(a){const t=a.result;if(!t)return"";if(typeof t=="string")return t.slice(0,160);if(typeof t=="object"){const n=t;return String(n.summary||n.status||n.message||JSON.stringify(n).slice(0,160))}return String(t)}function GN(a){const t=[...a].reverse().map(n=>n.verification||n.completion||n.postcondition).find(Boolean);if(!t)return"";if(typeof t=="string")return t;if(typeof t=="object"){const n=t;return String(n.status||n.summary||n.message||JSON.stringify(n).slice(0,140))}return String(t)}function VN(a){if(!a||typeof a!="object")return"No data yet";const t=a,n=["episodic","semantic","procedural","advanced"].map(s=>{const o=t[s];if(typeof o=="number"||typeof o=="string")return`${s}: ${o}`;if(o&&typeof o=="object"){const c=o;return`${s}: ${c.total||c.count||c.total_entries||c.total_episodes||"reported"}`}return""}).filter(Boolean);return n.length?n.join(", "):"No data yet"}const $y=[{id:"command",label:"Command Center",icon:GE,path:"/dashboard"},{id:"work",label:"Work",icon:PE,path:"/dashboard/work"},{id:"approvals",label:"Approvals",icon:Nx,path:"/dashboard/approvals"},{id:"systems",label:"Systems",icon:wx,path:"/dashboard/systems"},{id:"mind",label:"Mind & Memory",icon:Cx,path:"/dashboard/mind"},{id:"activity",label:"Activity",icon:Up,path:"/dashboard/activity"},{id:"settings",label:"Settings",icon:YE,path:"/settings"}];function jN(){var x;const a=window.location.pathname.startsWith("/display"),t=Ex(),[n,s]=se.useState(window.location.pathname==="/chat"),[o,c]=se.useState([]),f=se.useMemo(()=>tx(window.location.pathname),[]),[d,p]=se.useState(f),m=AE({queryKey:["ui-overview",a?"display":"dashboard"],queryFn:()=>KE(a?"display":"dashboard"),refetchInterval:a?15e3:3e4}),v=se.useCallback(E=>{"schema_version"in E||c(M=>[E,...M].slice(0,10)),t.invalidateQueries({queryKey:["ui-overview"]})},[t]);if(Ox(v,!a),se.useEffect(()=>{const E=()=>{p(tx(window.location.pathname)),s(window.location.pathname==="/chat")};return window.addEventListener("popstate",E),()=>window.removeEventListener("popstate",E)},[]),m.isLoading)return g.jsx(XN,{displayMode:a});if(m.isError||!m.data)return g.jsx(qN,{message:m.error instanceof Error?m.error.message:"Overview unavailable"});if(a)return g.jsx(bN,{overview:m.data});const _=m.data;return g.jsxs("div",{className:"app-shell",children:[g.jsxs("aside",{className:"side-nav",children:[g.jsxs("div",{className:"brand",children:[g.jsx("span",{className:"brand__name",children:"AEGIS"}),g.jsx("span",{className:"brand__sub",children:"Operational Console"})]}),g.jsx("nav",{className:"nav-list","aria-label":"Primary",children:$y.map(E=>{const M=E.icon;return g.jsxs("button",{className:"nav-button","aria-current":d===E.id?"page":void 0,onClick:()=>{p(E.id),window.history.pushState(null,"",E.path)},children:[g.jsx(M,{size:17,"aria-hidden":"true"}),E.label]},E.id)})})]}),g.jsxs("main",{className:"content",children:[g.jsxs("header",{className:"top-bar",children:[g.jsxs("div",{className:"page-title",children:[g.jsx("h1",{children:((x=$y.find(E=>E.id===d))==null?void 0:x.label)||"AEGIS"}),g.jsx("p",{children:"Live overview generated by Runtime managers, Policy, Approval, and Status services."})]}),g.jsxs("div",{className:"top-actions",children:[g.jsx(oc,{status:String(_.core.data.health||"ONLINE")}),g.jsx(lr,{generatedAt:_.generated_at,sourceUpdatedAt:_.freshness.source_updated_at,stale:_.freshness.stale}),g.jsx("button",{className:"icon-button",onClick:()=>s(!0),title:"Open chat",children:g.jsx(Rx,{size:17,"aria-hidden":"true"})})]})]}),g.jsx(kN,{page:d,overview:_,recentEvents:o})]}),g.jsx(ab,{open:n,onClose:()=>s(!1)})]})}function kN({page:a,overview:t,recentEvents:n}){return a==="work"?g.jsx(FN,{overview:t}):a==="approvals"?g.jsx(bb,{overview:t}):a==="systems"?g.jsx(UN,{overview:t}):a==="mind"?g.jsx(CN,{overview:t}):a==="activity"?g.jsx(ob,{overview:t,recentEvents:n}):a==="settings"?g.jsx(wN,{overview:t}):g.jsx(MN,{overview:t,recentEvents:n})}function tx(a){return a.includes("/work")?"work":a.includes("/approvals")?"approvals":a.includes("/systems")||a.includes("/servers")?"systems":a.includes("/mind")||a.includes("/memory")?"mind":a.includes("/activity")||a.includes("/audit")?"activity":a.includes("/settings")?"settings":"command"}function XN({displayMode:a}){return g.jsx("main",{className:a?"display-shell center-shell":"app-shell center-shell",children:g.jsx(Jl,{kind:"loading",title:"Loading AEGIS UI",message:"Waiting for the normalized overview service."})})}function qN({message:a}){const t=a.toLowerCase(),n=t.includes("401")||t.includes("unauthorized")?"unauthorized":t.includes("403")||t.includes("forbidden")?"permission":t.includes("fresh")?"fresh-auth":"error",s=n==="unauthorized"||n==="fresh-auth"?{label:"Open login",href:"/auth/login"}:void 0;return g.jsx("main",{className:"display-shell center-shell",children:g.jsx(Jl,{kind:n,title:n==="fresh-auth"?"Fresh passkey authentication required":"AEGIS UI unavailable",message:a,actionLabel:s==null?void 0:s.label,actionHref:s==null?void 0:s.href})})}const WN=new hE({defaultOptions:{queries:{retry:1,staleTime:1e4}}});G1.createRoot(document.getElementById("root")).render(g.jsx(L1.StrictMode,{children:g.jsx(pE,{client:WN,children:g.jsx(jN,{})})}));
