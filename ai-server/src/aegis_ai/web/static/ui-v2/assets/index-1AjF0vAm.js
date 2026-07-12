var Q0=r=>{throw TypeError(r)};var ld=(r,t,i)=>t.has(r)||Q0("Cannot "+i);var j=(r,t,i)=>(ld(r,t,"read from private field"),i?i.call(r):t.get(r)),$t=(r,t,i)=>t.has(r)?Q0("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(r):t.set(r,i),zt=(r,t,i,s)=>(ld(r,t,"write to private field"),s?s.call(r,i):t.set(r,i),i),Ee=(r,t,i)=>(ld(r,t,"access private method"),i);var hu=(r,t,i,s)=>({set _(l){zt(r,t,l,i)},get _(){return j(r,t,s)}});(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const l of document.querySelectorAll('link[rel="modulepreload"]'))s(l);new MutationObserver(l=>{for(const c of l)if(c.type==="childList")for(const h of c.addedNodes)h.tagName==="LINK"&&h.rel==="modulepreload"&&s(h)}).observe(document,{childList:!0,subtree:!0});function i(l){const c={};return l.integrity&&(c.integrity=l.integrity),l.referrerPolicy&&(c.referrerPolicy=l.referrerPolicy),l.crossOrigin==="use-credentials"?c.credentials="include":l.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function s(l){if(l.ep)return;l.ep=!0;const c=i(l);fetch(l.href,c)}})();function wy(r){return r&&r.__esModule&&Object.prototype.hasOwnProperty.call(r,"default")?r.default:r}var cd={exports:{}},Cl={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var Z0;function OM(){if(Z0)return Cl;Z0=1;var r=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function i(s,l,c){var h=null;if(c!==void 0&&(h=""+c),l.key!==void 0&&(h=""+l.key),"key"in l){c={};for(var d in l)d!=="key"&&(c[d]=l[d])}else c=l;return l=c.ref,{$$typeof:r,type:s,key:h,ref:l!==void 0?l:null,props:c}}return Cl.Fragment=t,Cl.jsx=i,Cl.jsxs=i,Cl}var K0;function PM(){return K0||(K0=1,cd.exports=OM()),cd.exports}var N=PM(),ud={exports:{}},ae={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var J0;function zM(){if(J0)return ae;J0=1;var r=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),i=Symbol.for("react.fragment"),s=Symbol.for("react.strict_mode"),l=Symbol.for("react.profiler"),c=Symbol.for("react.consumer"),h=Symbol.for("react.context"),d=Symbol.for("react.forward_ref"),m=Symbol.for("react.suspense"),p=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),_=Symbol.for("react.activity"),x=Symbol.iterator;function S(z){return z===null||typeof z!="object"?null:(z=x&&z[x]||z["@@iterator"],typeof z=="function"?z:null)}var E={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},b=Object.assign,M={};function v(z,at,Mt){this.props=z,this.context=at,this.refs=M,this.updater=Mt||E}v.prototype.isReactComponent={},v.prototype.setState=function(z,at){if(typeof z!="object"&&typeof z!="function"&&z!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,z,at,"setState")},v.prototype.forceUpdate=function(z){this.updater.enqueueForceUpdate(this,z,"forceUpdate")};function L(){}L.prototype=v.prototype;function U(z,at,Mt){this.props=z,this.context=at,this.refs=M,this.updater=Mt||E}var T=U.prototype=new L;T.constructor=U,b(T,v.prototype),T.isPureReactComponent=!0;var V=Array.isArray;function I(){}var P={H:null,A:null,T:null,S:null},H=Object.prototype.hasOwnProperty;function D(z,at,Mt){var K=Mt.ref;return{$$typeof:r,type:z,key:at,ref:K!==void 0?K:null,props:Mt}}function C(z,at){return D(z.type,at,z.props)}function G(z){return typeof z=="object"&&z!==null&&z.$$typeof===r}function ot(z){var at={"=":"=0",":":"=2"};return"$"+z.replace(/[=:]/g,function(Mt){return at[Mt]})}var lt=/\/+/g;function mt(z,at){return typeof z=="object"&&z!==null&&z.key!=null?ot(""+z.key):at.toString(36)}function gt(z){switch(z.status){case"fulfilled":return z.value;case"rejected":throw z.reason;default:switch(typeof z.status=="string"?z.then(I,I):(z.status="pending",z.then(function(at){z.status==="pending"&&(z.status="fulfilled",z.value=at)},function(at){z.status==="pending"&&(z.status="rejected",z.reason=at)})),z.status){case"fulfilled":return z.value;case"rejected":throw z.reason}}throw z}function B(z,at,Mt,K,ft){var Tt=typeof z;(Tt==="undefined"||Tt==="boolean")&&(z=null);var St=!1;if(z===null)St=!0;else switch(Tt){case"bigint":case"string":case"number":St=!0;break;case"object":switch(z.$$typeof){case r:case t:St=!0;break;case g:return St=z._init,B(St(z._payload),at,Mt,K,ft)}}if(St)return ft=ft(z),St=K===""?"."+mt(z,0):K,V(ft)?(Mt="",St!=null&&(Mt=St.replace(lt,"$&/")+"/"),B(ft,at,Mt,"",function(se){return se})):ft!=null&&(G(ft)&&(ft=C(ft,Mt+(ft.key==null||z&&z.key===ft.key?"":(""+ft.key).replace(lt,"$&/")+"/")+St)),at.push(ft)),1;St=0;var kt=K===""?".":K+":";if(V(z))for(var Gt=0;Gt<z.length;Gt++)K=z[Gt],Tt=kt+mt(K,Gt),St+=B(K,at,Mt,Tt,ft);else if(Gt=S(z),typeof Gt=="function")for(z=Gt.call(z),Gt=0;!(K=z.next()).done;)K=K.value,Tt=kt+mt(K,Gt++),St+=B(K,at,Mt,Tt,ft);else if(Tt==="object"){if(typeof z.then=="function")return B(gt(z),at,Mt,K,ft);throw at=String(z),Error("Objects are not valid as a React child (found: "+(at==="[object Object]"?"object with keys {"+Object.keys(z).join(", ")+"}":at)+"). If you meant to render a collection of children, use an array instead.")}return St}function $(z,at,Mt){if(z==null)return z;var K=[],ft=0;return B(z,K,"","",function(Tt){return at.call(Mt,Tt,ft++)}),K}function J(z){if(z._status===-1){var at=z._result;at=at(),at.then(function(Mt){(z._status===0||z._status===-1)&&(z._status=1,z._result=Mt)},function(Mt){(z._status===0||z._status===-1)&&(z._status=2,z._result=Mt)}),z._status===-1&&(z._status=0,z._result=at)}if(z._status===1)return z._result.default;throw z._result}var Et=typeof reportError=="function"?reportError:function(z){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var at=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof z=="object"&&z!==null&&typeof z.message=="string"?String(z.message):String(z),error:z});if(!window.dispatchEvent(at))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",z);return}console.error(z)},At={map:$,forEach:function(z,at,Mt){$(z,function(){at.apply(this,arguments)},Mt)},count:function(z){var at=0;return $(z,function(){at++}),at},toArray:function(z){return $(z,function(at){return at})||[]},only:function(z){if(!G(z))throw Error("React.Children.only expected to receive a single React element child.");return z}};return ae.Activity=_,ae.Children=At,ae.Component=v,ae.Fragment=i,ae.Profiler=l,ae.PureComponent=U,ae.StrictMode=s,ae.Suspense=m,ae.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=P,ae.__COMPILER_RUNTIME={__proto__:null,c:function(z){return P.H.useMemoCache(z)}},ae.cache=function(z){return function(){return z.apply(null,arguments)}},ae.cacheSignal=function(){return null},ae.cloneElement=function(z,at,Mt){if(z==null)throw Error("The argument must be a React element, but you passed "+z+".");var K=b({},z.props),ft=z.key;if(at!=null)for(Tt in at.key!==void 0&&(ft=""+at.key),at)!H.call(at,Tt)||Tt==="key"||Tt==="__self"||Tt==="__source"||Tt==="ref"&&at.ref===void 0||(K[Tt]=at[Tt]);var Tt=arguments.length-2;if(Tt===1)K.children=Mt;else if(1<Tt){for(var St=Array(Tt),kt=0;kt<Tt;kt++)St[kt]=arguments[kt+2];K.children=St}return D(z.type,ft,K)},ae.createContext=function(z){return z={$$typeof:h,_currentValue:z,_currentValue2:z,_threadCount:0,Provider:null,Consumer:null},z.Provider=z,z.Consumer={$$typeof:c,_context:z},z},ae.createElement=function(z,at,Mt){var K,ft={},Tt=null;if(at!=null)for(K in at.key!==void 0&&(Tt=""+at.key),at)H.call(at,K)&&K!=="key"&&K!=="__self"&&K!=="__source"&&(ft[K]=at[K]);var St=arguments.length-2;if(St===1)ft.children=Mt;else if(1<St){for(var kt=Array(St),Gt=0;Gt<St;Gt++)kt[Gt]=arguments[Gt+2];ft.children=kt}if(z&&z.defaultProps)for(K in St=z.defaultProps,St)ft[K]===void 0&&(ft[K]=St[K]);return D(z,Tt,ft)},ae.createRef=function(){return{current:null}},ae.forwardRef=function(z){return{$$typeof:d,render:z}},ae.isValidElement=G,ae.lazy=function(z){return{$$typeof:g,_payload:{_status:-1,_result:z},_init:J}},ae.memo=function(z,at){return{$$typeof:p,type:z,compare:at===void 0?null:at}},ae.startTransition=function(z){var at=P.T,Mt={};P.T=Mt;try{var K=z(),ft=P.S;ft!==null&&ft(Mt,K),typeof K=="object"&&K!==null&&typeof K.then=="function"&&K.then(I,Et)}catch(Tt){Et(Tt)}finally{at!==null&&Mt.types!==null&&(at.types=Mt.types),P.T=at}},ae.unstable_useCacheRefresh=function(){return P.H.useCacheRefresh()},ae.use=function(z){return P.H.use(z)},ae.useActionState=function(z,at,Mt){return P.H.useActionState(z,at,Mt)},ae.useCallback=function(z,at){return P.H.useCallback(z,at)},ae.useContext=function(z){return P.H.useContext(z)},ae.useDebugValue=function(){},ae.useDeferredValue=function(z,at){return P.H.useDeferredValue(z,at)},ae.useEffect=function(z,at){return P.H.useEffect(z,at)},ae.useEffectEvent=function(z){return P.H.useEffectEvent(z)},ae.useId=function(){return P.H.useId()},ae.useImperativeHandle=function(z,at,Mt){return P.H.useImperativeHandle(z,at,Mt)},ae.useInsertionEffect=function(z,at){return P.H.useInsertionEffect(z,at)},ae.useLayoutEffect=function(z,at){return P.H.useLayoutEffect(z,at)},ae.useMemo=function(z,at){return P.H.useMemo(z,at)},ae.useOptimistic=function(z,at){return P.H.useOptimistic(z,at)},ae.useReducer=function(z,at,Mt){return P.H.useReducer(z,at,Mt)},ae.useRef=function(z){return P.H.useRef(z)},ae.useState=function(z){return P.H.useState(z)},ae.useSyncExternalStore=function(z,at,Mt){return P.H.useSyncExternalStore(z,at,Mt)},ae.useTransition=function(){return P.H.useTransition()},ae.version="19.2.7",ae}var $0;function Kp(){return $0||($0=1,ud.exports=zM()),ud.exports}var Pe=Kp();const IM=wy(Pe);var fd={exports:{}},wl={},hd={exports:{}},dd={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var tv;function BM(){return tv||(tv=1,(function(r){function t(B,$){var J=B.length;B.push($);t:for(;0<J;){var Et=J-1>>>1,At=B[Et];if(0<l(At,$))B[Et]=$,B[J]=At,J=Et;else break t}}function i(B){return B.length===0?null:B[0]}function s(B){if(B.length===0)return null;var $=B[0],J=B.pop();if(J!==$){B[0]=J;t:for(var Et=0,At=B.length,z=At>>>1;Et<z;){var at=2*(Et+1)-1,Mt=B[at],K=at+1,ft=B[K];if(0>l(Mt,J))K<At&&0>l(ft,Mt)?(B[Et]=ft,B[K]=J,Et=K):(B[Et]=Mt,B[at]=J,Et=at);else if(K<At&&0>l(ft,J))B[Et]=ft,B[K]=J,Et=K;else break t}}return $}function l(B,$){var J=B.sortIndex-$.sortIndex;return J!==0?J:B.id-$.id}if(r.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var c=performance;r.unstable_now=function(){return c.now()}}else{var h=Date,d=h.now();r.unstable_now=function(){return h.now()-d}}var m=[],p=[],g=1,_=null,x=3,S=!1,E=!1,b=!1,M=!1,v=typeof setTimeout=="function"?setTimeout:null,L=typeof clearTimeout=="function"?clearTimeout:null,U=typeof setImmediate<"u"?setImmediate:null;function T(B){for(var $=i(p);$!==null;){if($.callback===null)s(p);else if($.startTime<=B)s(p),$.sortIndex=$.expirationTime,t(m,$);else break;$=i(p)}}function V(B){if(b=!1,T(B),!E)if(i(m)!==null)E=!0,I||(I=!0,ot());else{var $=i(p);$!==null&&gt(V,$.startTime-B)}}var I=!1,P=-1,H=5,D=-1;function C(){return M?!0:!(r.unstable_now()-D<H)}function G(){if(M=!1,I){var B=r.unstable_now();D=B;var $=!0;try{t:{E=!1,b&&(b=!1,L(P),P=-1),S=!0;var J=x;try{e:{for(T(B),_=i(m);_!==null&&!(_.expirationTime>B&&C());){var Et=_.callback;if(typeof Et=="function"){_.callback=null,x=_.priorityLevel;var At=Et(_.expirationTime<=B);if(B=r.unstable_now(),typeof At=="function"){_.callback=At,T(B),$=!0;break e}_===i(m)&&s(m),T(B)}else s(m);_=i(m)}if(_!==null)$=!0;else{var z=i(p);z!==null&&gt(V,z.startTime-B),$=!1}}break t}finally{_=null,x=J,S=!1}$=void 0}}finally{$?ot():I=!1}}}var ot;if(typeof U=="function")ot=function(){U(G)};else if(typeof MessageChannel<"u"){var lt=new MessageChannel,mt=lt.port2;lt.port1.onmessage=G,ot=function(){mt.postMessage(null)}}else ot=function(){v(G,0)};function gt(B,$){P=v(function(){B(r.unstable_now())},$)}r.unstable_IdlePriority=5,r.unstable_ImmediatePriority=1,r.unstable_LowPriority=4,r.unstable_NormalPriority=3,r.unstable_Profiling=null,r.unstable_UserBlockingPriority=2,r.unstable_cancelCallback=function(B){B.callback=null},r.unstable_forceFrameRate=function(B){0>B||125<B?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):H=0<B?Math.floor(1e3/B):5},r.unstable_getCurrentPriorityLevel=function(){return x},r.unstable_next=function(B){switch(x){case 1:case 2:case 3:var $=3;break;default:$=x}var J=x;x=$;try{return B()}finally{x=J}},r.unstable_requestPaint=function(){M=!0},r.unstable_runWithPriority=function(B,$){switch(B){case 1:case 2:case 3:case 4:case 5:break;default:B=3}var J=x;x=B;try{return $()}finally{x=J}},r.unstable_scheduleCallback=function(B,$,J){var Et=r.unstable_now();switch(typeof J=="object"&&J!==null?(J=J.delay,J=typeof J=="number"&&0<J?Et+J:Et):J=Et,B){case 1:var At=-1;break;case 2:At=250;break;case 5:At=1073741823;break;case 4:At=1e4;break;default:At=5e3}return At=J+At,B={id:g++,callback:$,priorityLevel:B,startTime:J,expirationTime:At,sortIndex:-1},J>Et?(B.sortIndex=J,t(p,B),i(m)===null&&B===i(p)&&(b?(L(P),P=-1):b=!0,gt(V,J-Et))):(B.sortIndex=At,t(m,B),E||S||(E=!0,I||(I=!0,ot()))),B},r.unstable_shouldYield=C,r.unstable_wrapCallback=function(B){var $=x;return function(){var J=x;x=$;try{return B.apply(this,arguments)}finally{x=J}}}})(dd)),dd}var ev;function FM(){return ev||(ev=1,hd.exports=BM()),hd.exports}var pd={exports:{}},zn={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var nv;function HM(){if(nv)return zn;nv=1;var r=Kp();function t(m){var p="https://react.dev/errors/"+m;if(1<arguments.length){p+="?args[]="+encodeURIComponent(arguments[1]);for(var g=2;g<arguments.length;g++)p+="&args[]="+encodeURIComponent(arguments[g])}return"Minified React error #"+m+"; visit "+p+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function i(){}var s={d:{f:i,r:function(){throw Error(t(522))},D:i,C:i,L:i,m:i,X:i,S:i,M:i},p:0,findDOMNode:null},l=Symbol.for("react.portal");function c(m,p,g){var _=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:l,key:_==null?null:""+_,children:m,containerInfo:p,implementation:g}}var h=r.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function d(m,p){if(m==="font")return"";if(typeof p=="string")return p==="use-credentials"?p:""}return zn.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=s,zn.createPortal=function(m,p){var g=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!p||p.nodeType!==1&&p.nodeType!==9&&p.nodeType!==11)throw Error(t(299));return c(m,p,null,g)},zn.flushSync=function(m){var p=h.T,g=s.p;try{if(h.T=null,s.p=2,m)return m()}finally{h.T=p,s.p=g,s.d.f()}},zn.preconnect=function(m,p){typeof m=="string"&&(p?(p=p.crossOrigin,p=typeof p=="string"?p==="use-credentials"?p:"":void 0):p=null,s.d.C(m,p))},zn.prefetchDNS=function(m){typeof m=="string"&&s.d.D(m)},zn.preinit=function(m,p){if(typeof m=="string"&&p&&typeof p.as=="string"){var g=p.as,_=d(g,p.crossOrigin),x=typeof p.integrity=="string"?p.integrity:void 0,S=typeof p.fetchPriority=="string"?p.fetchPriority:void 0;g==="style"?s.d.S(m,typeof p.precedence=="string"?p.precedence:void 0,{crossOrigin:_,integrity:x,fetchPriority:S}):g==="script"&&s.d.X(m,{crossOrigin:_,integrity:x,fetchPriority:S,nonce:typeof p.nonce=="string"?p.nonce:void 0})}},zn.preinitModule=function(m,p){if(typeof m=="string")if(typeof p=="object"&&p!==null){if(p.as==null||p.as==="script"){var g=d(p.as,p.crossOrigin);s.d.M(m,{crossOrigin:g,integrity:typeof p.integrity=="string"?p.integrity:void 0,nonce:typeof p.nonce=="string"?p.nonce:void 0})}}else p==null&&s.d.M(m)},zn.preload=function(m,p){if(typeof m=="string"&&typeof p=="object"&&p!==null&&typeof p.as=="string"){var g=p.as,_=d(g,p.crossOrigin);s.d.L(m,g,{crossOrigin:_,integrity:typeof p.integrity=="string"?p.integrity:void 0,nonce:typeof p.nonce=="string"?p.nonce:void 0,type:typeof p.type=="string"?p.type:void 0,fetchPriority:typeof p.fetchPriority=="string"?p.fetchPriority:void 0,referrerPolicy:typeof p.referrerPolicy=="string"?p.referrerPolicy:void 0,imageSrcSet:typeof p.imageSrcSet=="string"?p.imageSrcSet:void 0,imageSizes:typeof p.imageSizes=="string"?p.imageSizes:void 0,media:typeof p.media=="string"?p.media:void 0})}},zn.preloadModule=function(m,p){if(typeof m=="string")if(p){var g=d(p.as,p.crossOrigin);s.d.m(m,{as:typeof p.as=="string"&&p.as!=="script"?p.as:void 0,crossOrigin:g,integrity:typeof p.integrity=="string"?p.integrity:void 0})}else s.d.m(m)},zn.requestFormReset=function(m){s.d.r(m)},zn.unstable_batchedUpdates=function(m,p){return m(p)},zn.useFormState=function(m,p,g){return h.H.useFormState(m,p,g)},zn.useFormStatus=function(){return h.H.useHostTransitionStatus()},zn.version="19.2.7",zn}var iv;function GM(){if(iv)return pd.exports;iv=1;function r(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(r)}catch(t){console.error(t)}}return r(),pd.exports=HM(),pd.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var av;function VM(){if(av)return wl;av=1;var r=FM(),t=Kp(),i=GM();function s(e){var n="https://react.dev/errors/"+e;if(1<arguments.length){n+="?args[]="+encodeURIComponent(arguments[1]);for(var a=2;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a])}return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function c(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function h(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function d(e){if(e.tag===31){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function m(e){if(c(e)!==e)throw Error(s(188))}function p(e){var n=e.alternate;if(!n){if(n=c(e),n===null)throw Error(s(188));return n!==e?null:e}for(var a=e,o=n;;){var u=a.return;if(u===null)break;var f=u.alternate;if(f===null){if(o=u.return,o!==null){a=o;continue}break}if(u.child===f.child){for(f=u.child;f;){if(f===a)return m(u),e;if(f===o)return m(u),n;f=f.sibling}throw Error(s(188))}if(a.return!==o.return)a=u,o=f;else{for(var y=!1,A=u.child;A;){if(A===a){y=!0,a=u,o=f;break}if(A===o){y=!0,o=u,a=f;break}A=A.sibling}if(!y){for(A=f.child;A;){if(A===a){y=!0,a=f,o=u;break}if(A===o){y=!0,o=f,a=u;break}A=A.sibling}if(!y)throw Error(s(189))}}if(a.alternate!==o)throw Error(s(190))}if(a.tag!==3)throw Error(s(188));return a.stateNode.current===a?e:n}function g(e){var n=e.tag;if(n===5||n===26||n===27||n===6)return e;for(e=e.child;e!==null;){if(n=g(e),n!==null)return n;e=e.sibling}return null}var _=Object.assign,x=Symbol.for("react.element"),S=Symbol.for("react.transitional.element"),E=Symbol.for("react.portal"),b=Symbol.for("react.fragment"),M=Symbol.for("react.strict_mode"),v=Symbol.for("react.profiler"),L=Symbol.for("react.consumer"),U=Symbol.for("react.context"),T=Symbol.for("react.forward_ref"),V=Symbol.for("react.suspense"),I=Symbol.for("react.suspense_list"),P=Symbol.for("react.memo"),H=Symbol.for("react.lazy"),D=Symbol.for("react.activity"),C=Symbol.for("react.memo_cache_sentinel"),G=Symbol.iterator;function ot(e){return e===null||typeof e!="object"?null:(e=G&&e[G]||e["@@iterator"],typeof e=="function"?e:null)}var lt=Symbol.for("react.client.reference");function mt(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===lt?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case b:return"Fragment";case v:return"Profiler";case M:return"StrictMode";case V:return"Suspense";case I:return"SuspenseList";case D:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case E:return"Portal";case U:return e.displayName||"Context";case L:return(e._context.displayName||"Context")+".Consumer";case T:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case P:return n=e.displayName||null,n!==null?n:mt(e.type)||"Memo";case H:n=e._payload,e=e._init;try{return mt(e(n))}catch{}}return null}var gt=Array.isArray,B=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,$=i.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,J={pending:!1,data:null,method:null,action:null},Et=[],At=-1;function z(e){return{current:e}}function at(e){0>At||(e.current=Et[At],Et[At]=null,At--)}function Mt(e,n){At++,Et[At]=e.current,e.current=n}var K=z(null),ft=z(null),Tt=z(null),St=z(null);function kt(e,n){switch(Mt(Tt,n),Mt(ft,e),Mt(K,null),n.nodeType){case 9:case 11:e=(e=n.documentElement)&&(e=e.namespaceURI)?v0(e):0;break;default:if(e=n.tagName,n=n.namespaceURI)n=v0(n),e=y0(n,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}at(K),Mt(K,e)}function Gt(){at(K),at(ft),at(Tt)}function se(e){e.memoizedState!==null&&Mt(St,e);var n=K.current,a=y0(n,e.type);n!==a&&(Mt(ft,e),Mt(K,a))}function He(e){ft.current===e&&(at(K),at(ft)),St.current===e&&(at(St),bl._currentValue=J)}var de,$e;function k(e){if(de===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);de=n&&n[1]||"",$e=-1<a.stack.indexOf(`
    at`)?" (<anonymous>)":-1<a.stack.indexOf("@")?"@unknown:0:0":""}return`
`+de+e+$e}var On=!1;function he(e,n){if(!e||On)return"";On=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var o={DetermineComponentFrameRoot:function(){try{if(n){var vt=function(){throw Error()};if(Object.defineProperty(vt.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(vt,[])}catch(ct){var nt=ct}Reflect.construct(e,[],vt)}else{try{vt.call()}catch(ct){nt=ct}e.call(vt.prototype)}}else{try{throw Error()}catch(ct){nt=ct}(vt=e())&&typeof vt.catch=="function"&&vt.catch(function(){})}}catch(ct){if(ct&&nt&&typeof ct.stack=="string")return[ct.stack,nt.stack]}return[null,null]}};o.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var u=Object.getOwnPropertyDescriptor(o.DetermineComponentFrameRoot,"name");u&&u.configurable&&Object.defineProperty(o.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var f=o.DetermineComponentFrameRoot(),y=f[0],A=f[1];if(y&&A){var F=y.split(`
`),et=A.split(`
`);for(u=o=0;o<F.length&&!F[o].includes("DetermineComponentFrameRoot");)o++;for(;u<et.length&&!et[u].includes("DetermineComponentFrameRoot");)u++;if(o===F.length||u===et.length)for(o=F.length-1,u=et.length-1;1<=o&&0<=u&&F[o]!==et[u];)u--;for(;1<=o&&0<=u;o--,u--)if(F[o]!==et[u]){if(o!==1||u!==1)do if(o--,u--,0>u||F[o]!==et[u]){var ht=`
`+F[o].replace(" at new "," at ");return e.displayName&&ht.includes("<anonymous>")&&(ht=ht.replace("<anonymous>",e.displayName)),ht}while(1<=o&&0<=u);break}}}finally{On=!1,Error.prepareStackTrace=a}return(a=e?e.displayName||e.name:"")?k(a):""}function ve(e,n){switch(e.tag){case 26:case 27:case 5:return k(e.type);case 16:return k("Lazy");case 13:return e.child!==n&&n!==null?k("Suspense Fallback"):k("Suspense");case 19:return k("SuspenseList");case 0:case 15:return he(e.type,!1);case 11:return he(e.type.render,!1);case 1:return he(e.type,!0);case 31:return k("Activity");default:return""}}function Yt(e){try{var n="",a=null;do n+=ve(e,a),a=e,e=e.return;while(e);return n}catch(o){return`
Error generating stack: `+o.message+`
`+o.stack}}var Ie=Object.prototype.hasOwnProperty,Wt=r.unstable_scheduleCallback,O=r.unstable_cancelCallback,R=r.unstable_shouldYield,it=r.unstable_requestPaint,dt=r.unstable_now,bt=r.unstable_getCurrentPriorityLevel,_t=r.unstable_ImmediatePriority,jt=r.unstable_UserBlockingPriority,Dt=r.unstable_NormalPriority,Bt=r.unstable_LowPriority,ye=r.unstable_IdlePriority,Rt=r.log,Ft=r.unstable_setDisableYieldValue,Qt=null,qt=null;function Ot(e){if(typeof Rt=="function"&&Ft(e),qt&&typeof qt.setStrictMode=="function")try{qt.setStrictMode(Qt,e)}catch{}}var ee=Math.clz32?Math.clz32:q,re=Math.log,Ge=Math.LN2;function q(e){return e>>>=0,e===0?32:31-(re(e)/Ge|0)|0}var Ct=256,ut=262144,yt=4194304;function wt(e){var n=e&42;if(n!==0)return n;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Ut(e,n,a){var o=e.pendingLanes;if(o===0)return 0;var u=0,f=e.suspendedLanes,y=e.pingedLanes;e=e.warmLanes;var A=o&134217727;return A!==0?(o=A&~f,o!==0?u=wt(o):(y&=A,y!==0?u=wt(y):a||(a=A&~e,a!==0&&(u=wt(a))))):(A=o&~f,A!==0?u=wt(A):y!==0?u=wt(y):a||(a=o&~e,a!==0&&(u=wt(a)))),u===0?0:n!==0&&n!==u&&(n&f)===0&&(f=u&-u,a=n&-n,f>=a||f===32&&(a&4194048)!==0)?n:u}function ne(e,n){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&n)===0}function tn(e,n){switch(e){case 1:case 2:case 4:case 8:case 64:return n+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function _n(){var e=yt;return yt<<=1,(yt&62914560)===0&&(yt=4194304),e}function Re(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function An(e,n){e.pendingLanes|=n,n!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function Ci(e,n,a,o,u,f){var y=e.pendingLanes;e.pendingLanes=a,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=a,e.entangledLanes&=a,e.errorRecoveryDisabledLanes&=a,e.shellSuspendCounter=0;var A=e.entanglements,F=e.expirationTimes,et=e.hiddenUpdates;for(a=y&~a;0<a;){var ht=31-ee(a),vt=1<<ht;A[ht]=0,F[ht]=-1;var nt=et[ht];if(nt!==null)for(et[ht]=null,ht=0;ht<nt.length;ht++){var ct=nt[ht];ct!==null&&(ct.lane&=-536870913)}a&=~vt}o!==0&&Io(e,o,0),f!==0&&u===0&&e.tag!==0&&(e.suspendedLanes|=f&~(y&~n))}function Io(e,n,a){e.pendingLanes|=n,e.suspendedLanes&=~n;var o=31-ee(n);e.entangledLanes|=n,e.entanglements[o]=e.entanglements[o]|1073741824|a&261930}function Bo(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var o=31-ee(a),u=1<<o;u&n|e[o]&n&&(e[o]|=n),a&=~u}}function Hi(e,n){var a=n&-n;return a=(a&42)!==0?1:Ms(a),(a&(e.suspendedLanes|n))!==0?0:a}function Ms(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function pr(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function Fo(){var e=$.p;return e!==0?e:(e=window.event,e===void 0?32:V0(e.type))}function Es(e,n){var a=$.p;try{return $.p=e,n()}finally{$.p=a}}var wi=Math.random().toString(36).slice(2),an="__reactFiber$"+wi,Rn="__reactProps$"+wi,Ji="__reactContainer$"+wi,Ho="__reactEvents$"+wi,ef="__reactListeners$"+wi,nf="__reactHandles$"+wi,nc="__reactResources$"+wi,bs="__reactMarker$"+wi;function w(e){delete e[an],delete e[Rn],delete e[Ho],delete e[ef],delete e[nf]}function W(e){var n=e[an];if(n)return n;for(var a=e.parentNode;a;){if(n=a[Ji]||a[an]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=A0(e);e!==null;){if(a=e[an])return a;e=A0(e)}return n}e=a,a=e.parentNode}return null}function st(e){if(e=e[an]||e[Ji]){var n=e.tag;if(n===5||n===6||n===13||n===31||n===26||n===27||n===3)return e}return null}function rt(e){var n=e.tag;if(n===5||n===26||n===27||n===6)return e.stateNode;throw Error(s(33))}function Q(e){var n=e[nc];return n||(n=e[nc]={hoistableStyles:new Map,hoistableScripts:new Map}),n}function xt(e){e[bs]=!0}var Nt=new Set,It={};function Pt(e,n){Jt(e,n),Jt(e+"Capture",n)}function Jt(e,n){for(It[e]=n,e=0;e<n.length;e++)Nt.add(n[e])}var ie=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Zt={},xe={};function Ce(e){return Ie.call(xe,e)?!0:Ie.call(Zt,e)?!1:ie.test(e)?xe[e]=!0:(Zt[e]=!0,!1)}function Qe(e,n,a){if(Ce(n))if(a===null)e.removeAttribute(n);else{switch(typeof a){case"undefined":case"function":case"symbol":e.removeAttribute(n);return;case"boolean":var o=n.toLowerCase().slice(0,5);if(o!=="data-"&&o!=="aria-"){e.removeAttribute(n);return}}e.setAttribute(n,""+a)}}function We(e,n,a){if(a===null)e.removeAttribute(n);else{switch(typeof a){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(n);return}e.setAttribute(n,""+a)}}function oe(e,n,a,o){if(o===null)e.removeAttribute(a);else{switch(typeof o){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(a);return}e.setAttributeNS(n,a,""+o)}}function Vt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function fn(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function we(e,n,a){var o=Object.getOwnPropertyDescriptor(e.constructor.prototype,n);if(!e.hasOwnProperty(n)&&typeof o<"u"&&typeof o.get=="function"&&typeof o.set=="function"){var u=o.get,f=o.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return u.call(this)},set:function(y){a=""+y,f.call(this,y)}}),Object.defineProperty(e,n,{enumerable:o.enumerable}),{getValue:function(){return a},setValue:function(y){a=""+y},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Hn(e){if(!e._valueTracker){var n=fn(e)?"checked":"value";e._valueTracker=we(e,n,""+e[n])}}function $i(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),o="";return e&&(o=fn(e)?e.checked?"true":"false":e.value),e=o,e!==a?(n.setValue(e),!0):!1}function Mn(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Ts=/[\n"\\]/g;function pe(e){return e.replace(Ts,function(n){return"\\"+n.charCodeAt(0).toString(16)+" "})}function Pn(e,n,a,o,u,f,y,A){e.name="",y!=null&&typeof y!="function"&&typeof y!="symbol"&&typeof y!="boolean"?e.type=y:e.removeAttribute("type"),n!=null?y==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+Vt(n)):e.value!==""+Vt(n)&&(e.value=""+Vt(n)):y!=="submit"&&y!=="reset"||e.removeAttribute("value"),n!=null?vn(e,y,Vt(n)):a!=null?vn(e,y,Vt(a)):o!=null&&e.removeAttribute("value"),u==null&&f!=null&&(e.defaultChecked=!!f),u!=null&&(e.checked=u&&typeof u!="function"&&typeof u!="symbol"),A!=null&&typeof A!="function"&&typeof A!="symbol"&&typeof A!="boolean"?e.name=""+Vt(A):e.removeAttribute("name")}function Gn(e,n,a,o,u,f,y,A){if(f!=null&&typeof f!="function"&&typeof f!="symbol"&&typeof f!="boolean"&&(e.type=f),n!=null||a!=null){if(!(f!=="submit"&&f!=="reset"||n!=null)){Hn(e);return}a=a!=null?""+Vt(a):"",n=n!=null?""+Vt(n):a,A||n===e.value||(e.value=n),e.defaultValue=n}o=o??u,o=typeof o!="function"&&typeof o!="symbol"&&!!o,e.checked=A?e.checked:!!o,e.defaultChecked=!!o,y!=null&&typeof y!="function"&&typeof y!="symbol"&&typeof y!="boolean"&&(e.name=y),Hn(e)}function vn(e,n,a){n==="number"&&Mn(e.ownerDocument)===e||e.defaultValue===""+a||(e.defaultValue=""+a)}function ln(e,n,a,o){if(e=e.options,n){n={};for(var u=0;u<a.length;u++)n["$"+a[u]]=!0;for(a=0;a<e.length;a++)u=n.hasOwnProperty("$"+e[a].value),e[a].selected!==u&&(e[a].selected=u),u&&o&&(e[a].defaultSelected=!0)}else{for(a=""+Vt(a),n=null,u=0;u<e.length;u++){if(e[u].value===a){e[u].selected=!0,o&&(e[u].defaultSelected=!0);return}n!==null||e[u].disabled||(n=e[u])}n!==null&&(n.selected=!0)}}function mr(e,n,a){if(n!=null&&(n=""+Vt(n),n!==e.value&&(e.value=n),a==null)){e.defaultValue!==n&&(e.defaultValue=n);return}e.defaultValue=a!=null?""+Vt(a):""}function Gi(e,n,a,o){if(n==null){if(o!=null){if(a!=null)throw Error(s(92));if(gt(o)){if(1<o.length)throw Error(s(93));o=o[0]}a=o}a==null&&(a=""),n=a}a=Vt(n),e.defaultValue=a,o=e.textContent,o===a&&o!==""&&o!==null&&(e.value=o),Hn(e)}function gr(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var wx=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function mm(e,n,a){var o=n.indexOf("--")===0;a==null||typeof a=="boolean"||a===""?o?e.setProperty(n,""):n==="float"?e.cssFloat="":e[n]="":o?e.setProperty(n,a):typeof a!="number"||a===0||wx.has(n)?n==="float"?e.cssFloat=a:e[n]=(""+a).trim():e[n]=a+"px"}function gm(e,n,a){if(n!=null&&typeof n!="object")throw Error(s(62));if(e=e.style,a!=null){for(var o in a)!a.hasOwnProperty(o)||n!=null&&n.hasOwnProperty(o)||(o.indexOf("--")===0?e.setProperty(o,""):o==="float"?e.cssFloat="":e[o]="");for(var u in n)o=n[u],n.hasOwnProperty(u)&&a[u]!==o&&mm(e,u,o)}else for(var f in n)n.hasOwnProperty(f)&&mm(e,f,n[f])}function af(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Dx=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),Ux=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function ic(e){return Ux.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function ta(){}var sf=null;function rf(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var _r=null,vr=null;function _m(e){var n=st(e);if(n&&(e=n.stateNode)){var a=e[Rn]||null;t:switch(e=n.stateNode,n.type){case"input":if(Pn(e,a.value,a.defaultValue,a.defaultValue,a.checked,a.defaultChecked,a.type,a.name),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll('input[name="'+pe(""+n)+'"][type="radio"]'),n=0;n<a.length;n++){var o=a[n];if(o!==e&&o.form===e.form){var u=o[Rn]||null;if(!u)throw Error(s(90));Pn(o,u.value,u.defaultValue,u.defaultValue,u.checked,u.defaultChecked,u.type,u.name)}}for(n=0;n<a.length;n++)o=a[n],o.form===e.form&&$i(o)}break t;case"textarea":mr(e,a.value,a.defaultValue);break t;case"select":n=a.value,n!=null&&ln(e,!!a.multiple,n,!1)}}}var of=!1;function vm(e,n,a){if(of)return e(n,a);of=!0;try{var o=e(n);return o}finally{if(of=!1,(_r!==null||vr!==null)&&(Xc(),_r&&(n=_r,e=vr,vr=_r=null,_m(n),e)))for(n=0;n<e.length;n++)_m(e[n])}}function Go(e,n){var a=e.stateNode;if(a===null)return null;var o=a[Rn]||null;if(o===null)return null;a=o[n];t:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(o=!o.disabled)||(e=e.type,o=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!o;break t;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(s(231,n,typeof a));return a}var ea=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),lf=!1;if(ea)try{var Vo={};Object.defineProperty(Vo,"passive",{get:function(){lf=!0}}),window.addEventListener("test",Vo,Vo),window.removeEventListener("test",Vo,Vo)}catch{lf=!1}var Na=null,cf=null,ac=null;function ym(){if(ac)return ac;var e,n=cf,a=n.length,o,u="value"in Na?Na.value:Na.textContent,f=u.length;for(e=0;e<a&&n[e]===u[e];e++);var y=a-e;for(o=1;o<=y&&n[a-o]===u[f-o];o++);return ac=u.slice(e,1<o?1-o:void 0)}function sc(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function rc(){return!0}function xm(){return!1}function qn(e){function n(a,o,u,f,y){this._reactName=a,this._targetInst=u,this.type=o,this.nativeEvent=f,this.target=y,this.currentTarget=null;for(var A in e)e.hasOwnProperty(A)&&(a=e[A],this[A]=a?a(f):f[A]);return this.isDefaultPrevented=(f.defaultPrevented!=null?f.defaultPrevented:f.returnValue===!1)?rc:xm,this.isPropagationStopped=xm,this}return _(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=rc)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=rc)},persist:function(){},isPersistent:rc}),n}var As={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},oc=qn(As),ko=_({},As,{view:0,detail:0}),Nx=qn(ko),uf,ff,Xo,lc=_({},ko,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:df,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==Xo&&(Xo&&e.type==="mousemove"?(uf=e.screenX-Xo.screenX,ff=e.screenY-Xo.screenY):ff=uf=0,Xo=e),uf)},movementY:function(e){return"movementY"in e?e.movementY:ff}}),Sm=qn(lc),Lx=_({},lc,{dataTransfer:0}),Ox=qn(Lx),Px=_({},ko,{relatedTarget:0}),hf=qn(Px),zx=_({},As,{animationName:0,elapsedTime:0,pseudoElement:0}),Ix=qn(zx),Bx=_({},As,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),Fx=qn(Bx),Hx=_({},As,{data:0}),Mm=qn(Hx),Gx={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Vx={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},kx={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Xx(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=kx[e])?!!n[e]:!1}function df(){return Xx}var jx=_({},ko,{key:function(e){if(e.key){var n=Gx[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=sc(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?Vx[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:df,charCode:function(e){return e.type==="keypress"?sc(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?sc(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),qx=qn(jx),Wx=_({},lc,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Em=qn(Wx),Yx=_({},ko,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:df}),Qx=qn(Yx),Zx=_({},As,{propertyName:0,elapsedTime:0,pseudoElement:0}),Kx=qn(Zx),Jx=_({},lc,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),$x=qn(Jx),tS=_({},As,{newState:0,oldState:0}),eS=qn(tS),nS=[9,13,27,32],pf=ea&&"CompositionEvent"in window,jo=null;ea&&"documentMode"in document&&(jo=document.documentMode);var iS=ea&&"TextEvent"in window&&!jo,bm=ea&&(!pf||jo&&8<jo&&11>=jo),Tm=" ",Am=!1;function Rm(e,n){switch(e){case"keyup":return nS.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Cm(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var yr=!1;function aS(e,n){switch(e){case"compositionend":return Cm(n);case"keypress":return n.which!==32?null:(Am=!0,Tm);case"textInput":return e=n.data,e===Tm&&Am?null:e;default:return null}}function sS(e,n){if(yr)return e==="compositionend"||!pf&&Rm(e,n)?(e=ym(),ac=cf=Na=null,yr=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return bm&&n.locale!=="ko"?null:n.data;default:return null}}var rS={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function wm(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!rS[e.type]:n==="textarea"}function Dm(e,n,a,o){_r?vr?vr.push(o):vr=[o]:_r=o,n=Kc(n,"onChange"),0<n.length&&(a=new oc("onChange","change",null,a,o),e.push({event:a,listeners:n}))}var qo=null,Wo=null;function oS(e){h0(e,0)}function cc(e){var n=rt(e);if($i(n))return e}function Um(e,n){if(e==="change")return n}var Nm=!1;if(ea){var mf;if(ea){var gf="oninput"in document;if(!gf){var Lm=document.createElement("div");Lm.setAttribute("oninput","return;"),gf=typeof Lm.oninput=="function"}mf=gf}else mf=!1;Nm=mf&&(!document.documentMode||9<document.documentMode)}function Om(){qo&&(qo.detachEvent("onpropertychange",Pm),Wo=qo=null)}function Pm(e){if(e.propertyName==="value"&&cc(Wo)){var n=[];Dm(n,Wo,e,rf(e)),vm(oS,n)}}function lS(e,n,a){e==="focusin"?(Om(),qo=n,Wo=a,qo.attachEvent("onpropertychange",Pm)):e==="focusout"&&Om()}function cS(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return cc(Wo)}function uS(e,n){if(e==="click")return cc(n)}function fS(e,n){if(e==="input"||e==="change")return cc(n)}function hS(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var ii=typeof Object.is=="function"?Object.is:hS;function Yo(e,n){if(ii(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),o=Object.keys(n);if(a.length!==o.length)return!1;for(o=0;o<a.length;o++){var u=a[o];if(!Ie.call(n,u)||!ii(e[u],n[u]))return!1}return!0}function zm(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Im(e,n){var a=zm(e);e=0;for(var o;a;){if(a.nodeType===3){if(o=e+a.textContent.length,e<=n&&o>=n)return{node:a,offset:n-e};e=o}t:{for(;a;){if(a.nextSibling){a=a.nextSibling;break t}a=a.parentNode}a=void 0}a=zm(a)}}function Bm(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?Bm(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function Fm(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var n=Mn(e.document);n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=Mn(e.document)}return n}function _f(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}var dS=ea&&"documentMode"in document&&11>=document.documentMode,xr=null,vf=null,Qo=null,yf=!1;function Hm(e,n,a){var o=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;yf||xr==null||xr!==Mn(o)||(o=xr,"selectionStart"in o&&_f(o)?o={start:o.selectionStart,end:o.selectionEnd}:(o=(o.ownerDocument&&o.ownerDocument.defaultView||window).getSelection(),o={anchorNode:o.anchorNode,anchorOffset:o.anchorOffset,focusNode:o.focusNode,focusOffset:o.focusOffset}),Qo&&Yo(Qo,o)||(Qo=o,o=Kc(vf,"onSelect"),0<o.length&&(n=new oc("onSelect","select",null,n,a),e.push({event:n,listeners:o}),n.target=xr)))}function Rs(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var Sr={animationend:Rs("Animation","AnimationEnd"),animationiteration:Rs("Animation","AnimationIteration"),animationstart:Rs("Animation","AnimationStart"),transitionrun:Rs("Transition","TransitionRun"),transitionstart:Rs("Transition","TransitionStart"),transitioncancel:Rs("Transition","TransitionCancel"),transitionend:Rs("Transition","TransitionEnd")},xf={},Gm={};ea&&(Gm=document.createElement("div").style,"AnimationEvent"in window||(delete Sr.animationend.animation,delete Sr.animationiteration.animation,delete Sr.animationstart.animation),"TransitionEvent"in window||delete Sr.transitionend.transition);function Cs(e){if(xf[e])return xf[e];if(!Sr[e])return e;var n=Sr[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in Gm)return xf[e]=n[a];return e}var Vm=Cs("animationend"),km=Cs("animationiteration"),Xm=Cs("animationstart"),pS=Cs("transitionrun"),mS=Cs("transitionstart"),gS=Cs("transitioncancel"),jm=Cs("transitionend"),qm=new Map,Sf="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Sf.push("scrollEnd");function Di(e,n){qm.set(e,n),Pt(n,[e])}var uc=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var n=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(n))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},gi=[],Mr=0,Mf=0;function fc(){for(var e=Mr,n=Mf=Mr=0;n<e;){var a=gi[n];gi[n++]=null;var o=gi[n];gi[n++]=null;var u=gi[n];gi[n++]=null;var f=gi[n];if(gi[n++]=null,o!==null&&u!==null){var y=o.pending;y===null?u.next=u:(u.next=y.next,y.next=u),o.pending=u}f!==0&&Wm(a,u,f)}}function hc(e,n,a,o){gi[Mr++]=e,gi[Mr++]=n,gi[Mr++]=a,gi[Mr++]=o,Mf|=o,e.lanes|=o,e=e.alternate,e!==null&&(e.lanes|=o)}function Ef(e,n,a,o){return hc(e,n,a,o),dc(e)}function ws(e,n){return hc(e,null,null,n),dc(e)}function Wm(e,n,a){e.lanes|=a;var o=e.alternate;o!==null&&(o.lanes|=a);for(var u=!1,f=e.return;f!==null;)f.childLanes|=a,o=f.alternate,o!==null&&(o.childLanes|=a),f.tag===22&&(e=f.stateNode,e===null||e._visibility&1||(u=!0)),e=f,f=f.return;return e.tag===3?(f=e.stateNode,u&&n!==null&&(u=31-ee(a),e=f.hiddenUpdates,o=e[u],o===null?e[u]=[n]:o.push(n),n.lane=a|536870912),f):null}function dc(e){if(50<_l)throw _l=0,Nh=null,Error(s(185));for(var n=e.return;n!==null;)e=n,n=e.return;return e.tag===3?e.stateNode:null}var Er={};function _S(e,n,a,o){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=o,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ai(e,n,a,o){return new _S(e,n,a,o)}function bf(e){return e=e.prototype,!(!e||!e.isReactComponent)}function na(e,n){var a=e.alternate;return a===null?(a=ai(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&65011712,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a.refCleanup=e.refCleanup,a}function Ym(e,n){e.flags&=65011714;var a=e.alternate;return a===null?(e.childLanes=0,e.lanes=n,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=a.childLanes,e.lanes=a.lanes,e.child=a.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=a.memoizedProps,e.memoizedState=a.memoizedState,e.updateQueue=a.updateQueue,e.type=a.type,n=a.dependencies,e.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext}),e}function pc(e,n,a,o,u,f){var y=0;if(o=e,typeof e=="function")bf(e)&&(y=1);else if(typeof e=="string")y=MM(e,a,K.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case D:return e=ai(31,a,n,u),e.elementType=D,e.lanes=f,e;case b:return Ds(a.children,u,f,n);case M:y=8,u|=24;break;case v:return e=ai(12,a,n,u|2),e.elementType=v,e.lanes=f,e;case V:return e=ai(13,a,n,u),e.elementType=V,e.lanes=f,e;case I:return e=ai(19,a,n,u),e.elementType=I,e.lanes=f,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case U:y=10;break t;case L:y=9;break t;case T:y=11;break t;case P:y=14;break t;case H:y=16,o=null;break t}y=29,a=Error(s(130,e===null?"null":typeof e,"")),o=null}return n=ai(y,a,n,u),n.elementType=e,n.type=o,n.lanes=f,n}function Ds(e,n,a,o){return e=ai(7,e,o,n),e.lanes=a,e}function Tf(e,n,a){return e=ai(6,e,null,n),e.lanes=a,e}function Qm(e){var n=ai(18,null,null,0);return n.stateNode=e,n}function Af(e,n,a){return n=ai(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}var Zm=new WeakMap;function _i(e,n){if(typeof e=="object"&&e!==null){var a=Zm.get(e);return a!==void 0?a:(n={value:e,source:n,stack:Yt(n)},Zm.set(e,n),n)}return{value:e,source:n,stack:Yt(n)}}var br=[],Tr=0,mc=null,Zo=0,vi=[],yi=0,La=null,Vi=1,ki="";function ia(e,n){br[Tr++]=Zo,br[Tr++]=mc,mc=e,Zo=n}function Km(e,n,a){vi[yi++]=Vi,vi[yi++]=ki,vi[yi++]=La,La=e;var o=Vi;e=ki;var u=32-ee(o)-1;o&=~(1<<u),a+=1;var f=32-ee(n)+u;if(30<f){var y=u-u%5;f=(o&(1<<y)-1).toString(32),o>>=y,u-=y,Vi=1<<32-ee(n)+u|a<<u|o,ki=f+e}else Vi=1<<f|a<<u|o,ki=e}function Rf(e){e.return!==null&&(ia(e,1),Km(e,1,0))}function Cf(e){for(;e===mc;)mc=br[--Tr],br[Tr]=null,Zo=br[--Tr],br[Tr]=null;for(;e===La;)La=vi[--yi],vi[yi]=null,ki=vi[--yi],vi[yi]=null,Vi=vi[--yi],vi[yi]=null}function Jm(e,n){vi[yi++]=Vi,vi[yi++]=ki,vi[yi++]=La,Vi=n.id,ki=n.overflow,La=e}var Cn=null,Ze=null,be=!1,Oa=null,xi=!1,wf=Error(s(519));function Pa(e){var n=Error(s(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw Ko(_i(n,e)),wf}function $m(e){var n=e.stateNode,a=e.type,o=e.memoizedProps;switch(n[an]=e,n[Rn]=o,a){case"dialog":ge("cancel",n),ge("close",n);break;case"iframe":case"object":case"embed":ge("load",n);break;case"video":case"audio":for(a=0;a<yl.length;a++)ge(yl[a],n);break;case"source":ge("error",n);break;case"img":case"image":case"link":ge("error",n),ge("load",n);break;case"details":ge("toggle",n);break;case"input":ge("invalid",n),Gn(n,o.value,o.defaultValue,o.checked,o.defaultChecked,o.type,o.name,!0);break;case"select":ge("invalid",n);break;case"textarea":ge("invalid",n),Gi(n,o.value,o.defaultValue,o.children)}a=o.children,typeof a!="string"&&typeof a!="number"&&typeof a!="bigint"||n.textContent===""+a||o.suppressHydrationWarning===!0||g0(n.textContent,a)?(o.popover!=null&&(ge("beforetoggle",n),ge("toggle",n)),o.onScroll!=null&&ge("scroll",n),o.onScrollEnd!=null&&ge("scrollend",n),o.onClick!=null&&(n.onclick=ta),n=!0):n=!1,n||Pa(e,!0)}function tg(e){for(Cn=e.return;Cn;)switch(Cn.tag){case 5:case 31:case 13:xi=!1;return;case 27:case 3:xi=!0;return;default:Cn=Cn.return}}function Ar(e){if(e!==Cn)return!1;if(!be)return tg(e),be=!0,!1;var n=e.tag,a;if((a=n!==3&&n!==27)&&((a=n===5)&&(a=e.type,a=!(a!=="form"&&a!=="button")||Wh(e.type,e.memoizedProps)),a=!a),a&&Ze&&Pa(e),tg(e),n===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ze=T0(e)}else if(n===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ze=T0(e)}else n===27?(n=Ze,Qa(e.type)?(e=Jh,Jh=null,Ze=e):Ze=n):Ze=Cn?Mi(e.stateNode.nextSibling):null;return!0}function Us(){Ze=Cn=null,be=!1}function Df(){var e=Oa;return e!==null&&(Zn===null?Zn=e:Zn.push.apply(Zn,e),Oa=null),e}function Ko(e){Oa===null?Oa=[e]:Oa.push(e)}var Uf=z(null),Ns=null,aa=null;function za(e,n,a){Mt(Uf,n._currentValue),n._currentValue=a}function sa(e){e._currentValue=Uf.current,at(Uf)}function Nf(e,n,a){for(;e!==null;){var o=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,o!==null&&(o.childLanes|=n)):o!==null&&(o.childLanes&n)!==n&&(o.childLanes|=n),e===a)break;e=e.return}}function Lf(e,n,a,o){var u=e.child;for(u!==null&&(u.return=e);u!==null;){var f=u.dependencies;if(f!==null){var y=u.child;f=f.firstContext;t:for(;f!==null;){var A=f;f=u;for(var F=0;F<n.length;F++)if(A.context===n[F]){f.lanes|=a,A=f.alternate,A!==null&&(A.lanes|=a),Nf(f.return,a,e),o||(y=null);break t}f=A.next}}else if(u.tag===18){if(y=u.return,y===null)throw Error(s(341));y.lanes|=a,f=y.alternate,f!==null&&(f.lanes|=a),Nf(y,a,e),y=null}else y=u.child;if(y!==null)y.return=u;else for(y=u;y!==null;){if(y===e){y=null;break}if(u=y.sibling,u!==null){u.return=y.return,y=u;break}y=y.return}u=y}}function Rr(e,n,a,o){e=null;for(var u=n,f=!1;u!==null;){if(!f){if((u.flags&524288)!==0)f=!0;else if((u.flags&262144)!==0)break}if(u.tag===10){var y=u.alternate;if(y===null)throw Error(s(387));if(y=y.memoizedProps,y!==null){var A=u.type;ii(u.pendingProps.value,y.value)||(e!==null?e.push(A):e=[A])}}else if(u===St.current){if(y=u.alternate,y===null)throw Error(s(387));y.memoizedState.memoizedState!==u.memoizedState.memoizedState&&(e!==null?e.push(bl):e=[bl])}u=u.return}e!==null&&Lf(n,e,a,o),n.flags|=262144}function gc(e){for(e=e.firstContext;e!==null;){if(!ii(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Ls(e){Ns=e,aa=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function wn(e){return eg(Ns,e)}function _c(e,n){return Ns===null&&Ls(e),eg(e,n)}function eg(e,n){var a=n._currentValue;if(n={context:n,memoizedValue:a,next:null},aa===null){if(e===null)throw Error(s(308));aa=n,e.dependencies={lanes:0,firstContext:n},e.flags|=524288}else aa=aa.next=n;return a}var vS=typeof AbortController<"u"?AbortController:function(){var e=[],n=this.signal={aborted:!1,addEventListener:function(a,o){e.push(o)}};this.abort=function(){n.aborted=!0,e.forEach(function(a){return a()})}},yS=r.unstable_scheduleCallback,xS=r.unstable_NormalPriority,hn={$$typeof:U,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Of(){return{controller:new vS,data:new Map,refCount:0}}function Jo(e){e.refCount--,e.refCount===0&&yS(xS,function(){e.controller.abort()})}var $o=null,Pf=0,Cr=0,wr=null;function SS(e,n){if($o===null){var a=$o=[];Pf=0,Cr=Bh(),wr={status:"pending",value:void 0,then:function(o){a.push(o)}}}return Pf++,n.then(ng,ng),n}function ng(){if(--Pf===0&&$o!==null){wr!==null&&(wr.status="fulfilled");var e=$o;$o=null,Cr=0,wr=null;for(var n=0;n<e.length;n++)(0,e[n])()}}function MS(e,n){var a=[],o={status:"pending",value:null,reason:null,then:function(u){a.push(u)}};return e.then(function(){o.status="fulfilled",o.value=n;for(var u=0;u<a.length;u++)(0,a[u])(n)},function(u){for(o.status="rejected",o.reason=u,u=0;u<a.length;u++)(0,a[u])(void 0)}),o}var ig=B.S;B.S=function(e,n){H_=dt(),typeof n=="object"&&n!==null&&typeof n.then=="function"&&SS(e,n),ig!==null&&ig(e,n)};var Os=z(null);function zf(){var e=Os.current;return e!==null?e:Ye.pooledCache}function vc(e,n){n===null?Mt(Os,Os.current):Mt(Os,n.pool)}function ag(){var e=zf();return e===null?null:{parent:hn._currentValue,pool:e}}var Dr=Error(s(460)),If=Error(s(474)),yc=Error(s(542)),xc={then:function(){}};function sg(e){return e=e.status,e==="fulfilled"||e==="rejected"}function rg(e,n,a){switch(a=e[a],a===void 0?e.push(n):a!==n&&(n.then(ta,ta),n=a),n.status){case"fulfilled":return n.value;case"rejected":throw e=n.reason,lg(e),e;default:if(typeof n.status=="string")n.then(ta,ta);else{if(e=Ye,e!==null&&100<e.shellSuspendCounter)throw Error(s(482));e=n,e.status="pending",e.then(function(o){if(n.status==="pending"){var u=n;u.status="fulfilled",u.value=o}},function(o){if(n.status==="pending"){var u=n;u.status="rejected",u.reason=o}})}switch(n.status){case"fulfilled":return n.value;case"rejected":throw e=n.reason,lg(e),e}throw zs=n,Dr}}function Ps(e){try{var n=e._init;return n(e._payload)}catch(a){throw a!==null&&typeof a=="object"&&typeof a.then=="function"?(zs=a,Dr):a}}var zs=null;function og(){if(zs===null)throw Error(s(459));var e=zs;return zs=null,e}function lg(e){if(e===Dr||e===yc)throw Error(s(483))}var Ur=null,tl=0;function Sc(e){var n=tl;return tl+=1,Ur===null&&(Ur=[]),rg(Ur,e,n)}function el(e,n){n=n.props.ref,e.ref=n!==void 0?n:null}function Mc(e,n){throw n.$$typeof===x?Error(s(525)):(e=Object.prototype.toString.call(n),Error(s(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e)))}function cg(e){function n(Z,X){if(e){var tt=Z.deletions;tt===null?(Z.deletions=[X],Z.flags|=16):tt.push(X)}}function a(Z,X){if(!e)return null;for(;X!==null;)n(Z,X),X=X.sibling;return null}function o(Z){for(var X=new Map;Z!==null;)Z.key!==null?X.set(Z.key,Z):X.set(Z.index,Z),Z=Z.sibling;return X}function u(Z,X){return Z=na(Z,X),Z.index=0,Z.sibling=null,Z}function f(Z,X,tt){return Z.index=tt,e?(tt=Z.alternate,tt!==null?(tt=tt.index,tt<X?(Z.flags|=67108866,X):tt):(Z.flags|=67108866,X)):(Z.flags|=1048576,X)}function y(Z){return e&&Z.alternate===null&&(Z.flags|=67108866),Z}function A(Z,X,tt,pt){return X===null||X.tag!==6?(X=Tf(tt,Z.mode,pt),X.return=Z,X):(X=u(X,tt),X.return=Z,X)}function F(Z,X,tt,pt){var Kt=tt.type;return Kt===b?ht(Z,X,tt.props.children,pt,tt.key):X!==null&&(X.elementType===Kt||typeof Kt=="object"&&Kt!==null&&Kt.$$typeof===H&&Ps(Kt)===X.type)?(X=u(X,tt.props),el(X,tt),X.return=Z,X):(X=pc(tt.type,tt.key,tt.props,null,Z.mode,pt),el(X,tt),X.return=Z,X)}function et(Z,X,tt,pt){return X===null||X.tag!==4||X.stateNode.containerInfo!==tt.containerInfo||X.stateNode.implementation!==tt.implementation?(X=Af(tt,Z.mode,pt),X.return=Z,X):(X=u(X,tt.children||[]),X.return=Z,X)}function ht(Z,X,tt,pt,Kt){return X===null||X.tag!==7?(X=Ds(tt,Z.mode,pt,Kt),X.return=Z,X):(X=u(X,tt),X.return=Z,X)}function vt(Z,X,tt){if(typeof X=="string"&&X!==""||typeof X=="number"||typeof X=="bigint")return X=Tf(""+X,Z.mode,tt),X.return=Z,X;if(typeof X=="object"&&X!==null){switch(X.$$typeof){case S:return tt=pc(X.type,X.key,X.props,null,Z.mode,tt),el(tt,X),tt.return=Z,tt;case E:return X=Af(X,Z.mode,tt),X.return=Z,X;case H:return X=Ps(X),vt(Z,X,tt)}if(gt(X)||ot(X))return X=Ds(X,Z.mode,tt,null),X.return=Z,X;if(typeof X.then=="function")return vt(Z,Sc(X),tt);if(X.$$typeof===U)return vt(Z,_c(Z,X),tt);Mc(Z,X)}return null}function nt(Z,X,tt,pt){var Kt=X!==null?X.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return Kt!==null?null:A(Z,X,""+tt,pt);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case S:return tt.key===Kt?F(Z,X,tt,pt):null;case E:return tt.key===Kt?et(Z,X,tt,pt):null;case H:return tt=Ps(tt),nt(Z,X,tt,pt)}if(gt(tt)||ot(tt))return Kt!==null?null:ht(Z,X,tt,pt,null);if(typeof tt.then=="function")return nt(Z,X,Sc(tt),pt);if(tt.$$typeof===U)return nt(Z,X,_c(Z,tt),pt);Mc(Z,tt)}return null}function ct(Z,X,tt,pt,Kt){if(typeof pt=="string"&&pt!==""||typeof pt=="number"||typeof pt=="bigint")return Z=Z.get(tt)||null,A(X,Z,""+pt,Kt);if(typeof pt=="object"&&pt!==null){switch(pt.$$typeof){case S:return Z=Z.get(pt.key===null?tt:pt.key)||null,F(X,Z,pt,Kt);case E:return Z=Z.get(pt.key===null?tt:pt.key)||null,et(X,Z,pt,Kt);case H:return pt=Ps(pt),ct(Z,X,tt,pt,Kt)}if(gt(pt)||ot(pt))return Z=Z.get(tt)||null,ht(X,Z,pt,Kt,null);if(typeof pt.then=="function")return ct(Z,X,tt,Sc(pt),Kt);if(pt.$$typeof===U)return ct(Z,X,tt,_c(X,pt),Kt);Mc(X,pt)}return null}function Ht(Z,X,tt,pt){for(var Kt=null,De=null,Xt=X,ce=X=0,Me=null;Xt!==null&&ce<tt.length;ce++){Xt.index>ce?(Me=Xt,Xt=null):Me=Xt.sibling;var Ue=nt(Z,Xt,tt[ce],pt);if(Ue===null){Xt===null&&(Xt=Me);break}e&&Xt&&Ue.alternate===null&&n(Z,Xt),X=f(Ue,X,ce),De===null?Kt=Ue:De.sibling=Ue,De=Ue,Xt=Me}if(ce===tt.length)return a(Z,Xt),be&&ia(Z,ce),Kt;if(Xt===null){for(;ce<tt.length;ce++)Xt=vt(Z,tt[ce],pt),Xt!==null&&(X=f(Xt,X,ce),De===null?Kt=Xt:De.sibling=Xt,De=Xt);return be&&ia(Z,ce),Kt}for(Xt=o(Xt);ce<tt.length;ce++)Me=ct(Xt,Z,ce,tt[ce],pt),Me!==null&&(e&&Me.alternate!==null&&Xt.delete(Me.key===null?ce:Me.key),X=f(Me,X,ce),De===null?Kt=Me:De.sibling=Me,De=Me);return e&&Xt.forEach(function(ts){return n(Z,ts)}),be&&ia(Z,ce),Kt}function te(Z,X,tt,pt){if(tt==null)throw Error(s(151));for(var Kt=null,De=null,Xt=X,ce=X=0,Me=null,Ue=tt.next();Xt!==null&&!Ue.done;ce++,Ue=tt.next()){Xt.index>ce?(Me=Xt,Xt=null):Me=Xt.sibling;var ts=nt(Z,Xt,Ue.value,pt);if(ts===null){Xt===null&&(Xt=Me);break}e&&Xt&&ts.alternate===null&&n(Z,Xt),X=f(ts,X,ce),De===null?Kt=ts:De.sibling=ts,De=ts,Xt=Me}if(Ue.done)return a(Z,Xt),be&&ia(Z,ce),Kt;if(Xt===null){for(;!Ue.done;ce++,Ue=tt.next())Ue=vt(Z,Ue.value,pt),Ue!==null&&(X=f(Ue,X,ce),De===null?Kt=Ue:De.sibling=Ue,De=Ue);return be&&ia(Z,ce),Kt}for(Xt=o(Xt);!Ue.done;ce++,Ue=tt.next())Ue=ct(Xt,Z,ce,Ue.value,pt),Ue!==null&&(e&&Ue.alternate!==null&&Xt.delete(Ue.key===null?ce:Ue.key),X=f(Ue,X,ce),De===null?Kt=Ue:De.sibling=Ue,De=Ue);return e&&Xt.forEach(function(LM){return n(Z,LM)}),be&&ia(Z,ce),Kt}function Xe(Z,X,tt,pt){if(typeof tt=="object"&&tt!==null&&tt.type===b&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case S:t:{for(var Kt=tt.key;X!==null;){if(X.key===Kt){if(Kt=tt.type,Kt===b){if(X.tag===7){a(Z,X.sibling),pt=u(X,tt.props.children),pt.return=Z,Z=pt;break t}}else if(X.elementType===Kt||typeof Kt=="object"&&Kt!==null&&Kt.$$typeof===H&&Ps(Kt)===X.type){a(Z,X.sibling),pt=u(X,tt.props),el(pt,tt),pt.return=Z,Z=pt;break t}a(Z,X);break}else n(Z,X);X=X.sibling}tt.type===b?(pt=Ds(tt.props.children,Z.mode,pt,tt.key),pt.return=Z,Z=pt):(pt=pc(tt.type,tt.key,tt.props,null,Z.mode,pt),el(pt,tt),pt.return=Z,Z=pt)}return y(Z);case E:t:{for(Kt=tt.key;X!==null;){if(X.key===Kt)if(X.tag===4&&X.stateNode.containerInfo===tt.containerInfo&&X.stateNode.implementation===tt.implementation){a(Z,X.sibling),pt=u(X,tt.children||[]),pt.return=Z,Z=pt;break t}else{a(Z,X);break}else n(Z,X);X=X.sibling}pt=Af(tt,Z.mode,pt),pt.return=Z,Z=pt}return y(Z);case H:return tt=Ps(tt),Xe(Z,X,tt,pt)}if(gt(tt))return Ht(Z,X,tt,pt);if(ot(tt)){if(Kt=ot(tt),typeof Kt!="function")throw Error(s(150));return tt=Kt.call(tt),te(Z,X,tt,pt)}if(typeof tt.then=="function")return Xe(Z,X,Sc(tt),pt);if(tt.$$typeof===U)return Xe(Z,X,_c(Z,tt),pt);Mc(Z,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,X!==null&&X.tag===6?(a(Z,X.sibling),pt=u(X,tt),pt.return=Z,Z=pt):(a(Z,X),pt=Tf(tt,Z.mode,pt),pt.return=Z,Z=pt),y(Z)):a(Z,X)}return function(Z,X,tt,pt){try{tl=0;var Kt=Xe(Z,X,tt,pt);return Ur=null,Kt}catch(Xt){if(Xt===Dr||Xt===yc)throw Xt;var De=ai(29,Xt,null,Z.mode);return De.lanes=pt,De.return=Z,De}finally{}}}var Is=cg(!0),ug=cg(!1),Ia=!1;function Bf(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Ff(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Ba(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function Fa(e,n,a){var o=e.updateQueue;if(o===null)return null;if(o=o.shared,(Le&2)!==0){var u=o.pending;return u===null?n.next=n:(n.next=u.next,u.next=n),o.pending=n,n=dc(e),Wm(e,null,a),n}return hc(e,o,n,a),dc(e)}function nl(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194048)!==0)){var o=n.lanes;o&=e.pendingLanes,a|=o,n.lanes=a,Bo(e,a)}}function Hf(e,n){var a=e.updateQueue,o=e.alternate;if(o!==null&&(o=o.updateQueue,a===o)){var u=null,f=null;if(a=a.firstBaseUpdate,a!==null){do{var y={lane:a.lane,tag:a.tag,payload:a.payload,callback:null,next:null};f===null?u=f=y:f=f.next=y,a=a.next}while(a!==null);f===null?u=f=n:f=f.next=n}else u=f=n;a={baseState:o.baseState,firstBaseUpdate:u,lastBaseUpdate:f,shared:o.shared,callbacks:o.callbacks},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}var Gf=!1;function il(){if(Gf){var e=wr;if(e!==null)throw e}}function al(e,n,a,o){Gf=!1;var u=e.updateQueue;Ia=!1;var f=u.firstBaseUpdate,y=u.lastBaseUpdate,A=u.shared.pending;if(A!==null){u.shared.pending=null;var F=A,et=F.next;F.next=null,y===null?f=et:y.next=et,y=F;var ht=e.alternate;ht!==null&&(ht=ht.updateQueue,A=ht.lastBaseUpdate,A!==y&&(A===null?ht.firstBaseUpdate=et:A.next=et,ht.lastBaseUpdate=F))}if(f!==null){var vt=u.baseState;y=0,ht=et=F=null,A=f;do{var nt=A.lane&-536870913,ct=nt!==A.lane;if(ct?(Se&nt)===nt:(o&nt)===nt){nt!==0&&nt===Cr&&(Gf=!0),ht!==null&&(ht=ht.next={lane:0,tag:A.tag,payload:A.payload,callback:null,next:null});t:{var Ht=e,te=A;nt=n;var Xe=a;switch(te.tag){case 1:if(Ht=te.payload,typeof Ht=="function"){vt=Ht.call(Xe,vt,nt);break t}vt=Ht;break t;case 3:Ht.flags=Ht.flags&-65537|128;case 0:if(Ht=te.payload,nt=typeof Ht=="function"?Ht.call(Xe,vt,nt):Ht,nt==null)break t;vt=_({},vt,nt);break t;case 2:Ia=!0}}nt=A.callback,nt!==null&&(e.flags|=64,ct&&(e.flags|=8192),ct=u.callbacks,ct===null?u.callbacks=[nt]:ct.push(nt))}else ct={lane:nt,tag:A.tag,payload:A.payload,callback:A.callback,next:null},ht===null?(et=ht=ct,F=vt):ht=ht.next=ct,y|=nt;if(A=A.next,A===null){if(A=u.shared.pending,A===null)break;ct=A,A=ct.next,ct.next=null,u.lastBaseUpdate=ct,u.shared.pending=null}}while(!0);ht===null&&(F=vt),u.baseState=F,u.firstBaseUpdate=et,u.lastBaseUpdate=ht,f===null&&(u.shared.lanes=0),Xa|=y,e.lanes=y,e.memoizedState=vt}}function fg(e,n){if(typeof e!="function")throw Error(s(191,e));e.call(n)}function hg(e,n){var a=e.callbacks;if(a!==null)for(e.callbacks=null,e=0;e<a.length;e++)fg(a[e],n)}var Nr=z(null),Ec=z(0);function dg(e,n){e=pa,Mt(Ec,e),Mt(Nr,n),pa=e|n.baseLanes}function Vf(){Mt(Ec,pa),Mt(Nr,Nr.current)}function kf(){pa=Ec.current,at(Nr),at(Ec)}var si=z(null),Si=null;function Ha(e){var n=e.alternate;Mt(cn,cn.current&1),Mt(si,e),Si===null&&(n===null||Nr.current!==null||n.memoizedState!==null)&&(Si=e)}function Xf(e){Mt(cn,cn.current),Mt(si,e),Si===null&&(Si=e)}function pg(e){e.tag===22?(Mt(cn,cn.current),Mt(si,e),Si===null&&(Si=e)):Ga()}function Ga(){Mt(cn,cn.current),Mt(si,si.current)}function ri(e){at(si),Si===e&&(Si=null),at(cn)}var cn=z(0);function bc(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||Zh(a)||Kh(a)))return n}else if(n.tag===19&&(n.memoizedProps.revealOrder==="forwards"||n.memoizedProps.revealOrder==="backwards"||n.memoizedProps.revealOrder==="unstable_legacy-backwards"||n.memoizedProps.revealOrder==="together")){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var ra=0,le=null,Ve=null,dn=null,Tc=!1,Lr=!1,Bs=!1,Ac=0,sl=0,Or=null,ES=0;function sn(){throw Error(s(321))}function jf(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!ii(e[a],n[a]))return!1;return!0}function qf(e,n,a,o,u,f){return ra=f,le=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,B.H=e===null||e.memoizedState===null?Kg:oh,Bs=!1,f=a(o,u),Bs=!1,Lr&&(f=gg(n,a,o,u)),mg(e),f}function mg(e){B.H=ll;var n=Ve!==null&&Ve.next!==null;if(ra=0,dn=Ve=le=null,Tc=!1,sl=0,Or=null,n)throw Error(s(300));e===null||pn||(e=e.dependencies,e!==null&&gc(e)&&(pn=!0))}function gg(e,n,a,o){le=e;var u=0;do{if(Lr&&(Or=null),sl=0,Lr=!1,25<=u)throw Error(s(301));if(u+=1,dn=Ve=null,e.updateQueue!=null){var f=e.updateQueue;f.lastEffect=null,f.events=null,f.stores=null,f.memoCache!=null&&(f.memoCache.index=0)}B.H=Jg,f=n(a,o)}while(Lr);return f}function bS(){var e=B.H,n=e.useState()[0];return n=typeof n.then=="function"?rl(n):n,e=e.useState()[0],(Ve!==null?Ve.memoizedState:null)!==e&&(le.flags|=1024),n}function Wf(){var e=Ac!==0;return Ac=0,e}function Yf(e,n,a){n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~a}function Qf(e){if(Tc){for(e=e.memoizedState;e!==null;){var n=e.queue;n!==null&&(n.pending=null),e=e.next}Tc=!1}ra=0,dn=Ve=le=null,Lr=!1,sl=Ac=0,Or=null}function Vn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return dn===null?le.memoizedState=dn=e:dn=dn.next=e,dn}function un(){if(Ve===null){var e=le.alternate;e=e!==null?e.memoizedState:null}else e=Ve.next;var n=dn===null?le.memoizedState:dn.next;if(n!==null)dn=n,Ve=e;else{if(e===null)throw le.alternate===null?Error(s(467)):Error(s(310));Ve=e,e={memoizedState:Ve.memoizedState,baseState:Ve.baseState,baseQueue:Ve.baseQueue,queue:Ve.queue,next:null},dn===null?le.memoizedState=dn=e:dn=dn.next=e}return dn}function Rc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function rl(e){var n=sl;return sl+=1,Or===null&&(Or=[]),e=rg(Or,e,n),n=le,(dn===null?n.memoizedState:dn.next)===null&&(n=n.alternate,B.H=n===null||n.memoizedState===null?Kg:oh),e}function Cc(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return rl(e);if(e.$$typeof===U)return wn(e)}throw Error(s(438,String(e)))}function Zf(e){var n=null,a=le.updateQueue;if(a!==null&&(n=a.memoCache),n==null){var o=le.alternate;o!==null&&(o=o.updateQueue,o!==null&&(o=o.memoCache,o!=null&&(n={data:o.data.map(function(u){return u.slice()}),index:0})))}if(n==null&&(n={data:[],index:0}),a===null&&(a=Rc(),le.updateQueue=a),a.memoCache=n,a=n.data[n.index],a===void 0)for(a=n.data[n.index]=Array(e),o=0;o<e;o++)a[o]=C;return n.index++,a}function oa(e,n){return typeof n=="function"?n(e):n}function wc(e){var n=un();return Kf(n,Ve,e)}function Kf(e,n,a){var o=e.queue;if(o===null)throw Error(s(311));o.lastRenderedReducer=a;var u=e.baseQueue,f=o.pending;if(f!==null){if(u!==null){var y=u.next;u.next=f.next,f.next=y}n.baseQueue=u=f,o.pending=null}if(f=e.baseState,u===null)e.memoizedState=f;else{n=u.next;var A=y=null,F=null,et=n,ht=!1;do{var vt=et.lane&-536870913;if(vt!==et.lane?(Se&vt)===vt:(ra&vt)===vt){var nt=et.revertLane;if(nt===0)F!==null&&(F=F.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),vt===Cr&&(ht=!0);else if((ra&nt)===nt){et=et.next,nt===Cr&&(ht=!0);continue}else vt={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},F===null?(A=F=vt,y=f):F=F.next=vt,le.lanes|=nt,Xa|=nt;vt=et.action,Bs&&a(f,vt),f=et.hasEagerState?et.eagerState:a(f,vt)}else nt={lane:vt,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},F===null?(A=F=nt,y=f):F=F.next=nt,le.lanes|=vt,Xa|=vt;et=et.next}while(et!==null&&et!==n);if(F===null?y=f:F.next=A,!ii(f,e.memoizedState)&&(pn=!0,ht&&(a=wr,a!==null)))throw a;e.memoizedState=f,e.baseState=y,e.baseQueue=F,o.lastRenderedState=f}return u===null&&(o.lanes=0),[e.memoizedState,o.dispatch]}function Jf(e){var n=un(),a=n.queue;if(a===null)throw Error(s(311));a.lastRenderedReducer=e;var o=a.dispatch,u=a.pending,f=n.memoizedState;if(u!==null){a.pending=null;var y=u=u.next;do f=e(f,y.action),y=y.next;while(y!==u);ii(f,n.memoizedState)||(pn=!0),n.memoizedState=f,n.baseQueue===null&&(n.baseState=f),a.lastRenderedState=f}return[f,o]}function _g(e,n,a){var o=le,u=un(),f=be;if(f){if(a===void 0)throw Error(s(407));a=a()}else a=n();var y=!ii((Ve||u).memoizedState,a);if(y&&(u.memoizedState=a,pn=!0),u=u.queue,eh(xg.bind(null,o,u,e),[e]),u.getSnapshot!==n||y||dn!==null&&dn.memoizedState.tag&1){if(o.flags|=2048,Pr(9,{destroy:void 0},yg.bind(null,o,u,a,n),null),Ye===null)throw Error(s(349));f||(ra&127)!==0||vg(o,n,a)}return a}function vg(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=le.updateQueue,n===null?(n=Rc(),le.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function yg(e,n,a,o){n.value=a,n.getSnapshot=o,Sg(n)&&Mg(e)}function xg(e,n,a){return a(function(){Sg(n)&&Mg(e)})}function Sg(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!ii(e,a)}catch{return!0}}function Mg(e){var n=ws(e,2);n!==null&&Kn(n,e,2)}function $f(e){var n=Vn();if(typeof e=="function"){var a=e;if(e=a(),Bs){Ot(!0);try{a()}finally{Ot(!1)}}}return n.memoizedState=n.baseState=e,n.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:e},n}function Eg(e,n,a,o){return e.baseState=a,Kf(e,Ve,typeof o=="function"?o:oa)}function TS(e,n,a,o,u){if(Nc(e))throw Error(s(485));if(e=n.action,e!==null){var f={payload:u,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(y){f.listeners.push(y)}};B.T!==null?a(!0):f.isTransition=!1,o(f),a=n.pending,a===null?(f.next=n.pending=f,bg(n,f)):(f.next=a.next,n.pending=a.next=f)}}function bg(e,n){var a=n.action,o=n.payload,u=e.state;if(n.isTransition){var f=B.T,y={};B.T=y;try{var A=a(u,o),F=B.S;F!==null&&F(y,A),Tg(e,n,A)}catch(et){th(e,n,et)}finally{f!==null&&y.types!==null&&(f.types=y.types),B.T=f}}else try{f=a(u,o),Tg(e,n,f)}catch(et){th(e,n,et)}}function Tg(e,n,a){a!==null&&typeof a=="object"&&typeof a.then=="function"?a.then(function(o){Ag(e,n,o)},function(o){return th(e,n,o)}):Ag(e,n,a)}function Ag(e,n,a){n.status="fulfilled",n.value=a,Rg(n),e.state=a,n=e.pending,n!==null&&(a=n.next,a===n?e.pending=null:(a=a.next,n.next=a,bg(e,a)))}function th(e,n,a){var o=e.pending;if(e.pending=null,o!==null){o=o.next;do n.status="rejected",n.reason=a,Rg(n),n=n.next;while(n!==o)}e.action=null}function Rg(e){e=e.listeners;for(var n=0;n<e.length;n++)(0,e[n])()}function Cg(e,n){return n}function wg(e,n){if(be){var a=Ye.formState;if(a!==null){t:{var o=le;if(be){if(Ze){e:{for(var u=Ze,f=xi;u.nodeType!==8;){if(!f){u=null;break e}if(u=Mi(u.nextSibling),u===null){u=null;break e}}f=u.data,u=f==="F!"||f==="F"?u:null}if(u){Ze=Mi(u.nextSibling),o=u.data==="F!";break t}}Pa(o)}o=!1}o&&(n=a[0])}}return a=Vn(),a.memoizedState=a.baseState=n,o={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Cg,lastRenderedState:n},a.queue=o,a=Yg.bind(null,le,o),o.dispatch=a,o=$f(!1),f=rh.bind(null,le,!1,o.queue),o=Vn(),u={state:n,dispatch:null,action:e,pending:null},o.queue=u,a=TS.bind(null,le,u,f,a),u.dispatch=a,o.memoizedState=e,[n,a,!1]}function Dg(e){var n=un();return Ug(n,Ve,e)}function Ug(e,n,a){if(n=Kf(e,n,Cg)[0],e=wc(oa)[0],typeof n=="object"&&n!==null&&typeof n.then=="function")try{var o=rl(n)}catch(y){throw y===Dr?yc:y}else o=n;n=un();var u=n.queue,f=u.dispatch;return a!==n.memoizedState&&(le.flags|=2048,Pr(9,{destroy:void 0},AS.bind(null,u,a),null)),[o,f,e]}function AS(e,n){e.action=n}function Ng(e){var n=un(),a=Ve;if(a!==null)return Ug(n,a,e);un(),n=n.memoizedState,a=un();var o=a.queue.dispatch;return a.memoizedState=e,[n,o,!1]}function Pr(e,n,a,o){return e={tag:e,create:a,deps:o,inst:n,next:null},n=le.updateQueue,n===null&&(n=Rc(),le.updateQueue=n),a=n.lastEffect,a===null?n.lastEffect=e.next=e:(o=a.next,a.next=e,e.next=o,n.lastEffect=e),e}function Lg(){return un().memoizedState}function Dc(e,n,a,o){var u=Vn();le.flags|=e,u.memoizedState=Pr(1|n,{destroy:void 0},a,o===void 0?null:o)}function Uc(e,n,a,o){var u=un();o=o===void 0?null:o;var f=u.memoizedState.inst;Ve!==null&&o!==null&&jf(o,Ve.memoizedState.deps)?u.memoizedState=Pr(n,f,a,o):(le.flags|=e,u.memoizedState=Pr(1|n,f,a,o))}function Og(e,n){Dc(8390656,8,e,n)}function eh(e,n){Uc(2048,8,e,n)}function RS(e){le.flags|=4;var n=le.updateQueue;if(n===null)n=Rc(),le.updateQueue=n,n.events=[e];else{var a=n.events;a===null?n.events=[e]:a.push(e)}}function Pg(e){var n=un().memoizedState;return RS({ref:n,nextImpl:e}),function(){if((Le&2)!==0)throw Error(s(440));return n.impl.apply(void 0,arguments)}}function zg(e,n){return Uc(4,2,e,n)}function Ig(e,n){return Uc(4,4,e,n)}function Bg(e,n){if(typeof n=="function"){e=e();var a=n(e);return function(){typeof a=="function"?a():n(null)}}if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function Fg(e,n,a){a=a!=null?a.concat([e]):null,Uc(4,4,Bg.bind(null,n,e),a)}function nh(){}function Hg(e,n){var a=un();n=n===void 0?null:n;var o=a.memoizedState;return n!==null&&jf(n,o[1])?o[0]:(a.memoizedState=[e,n],e)}function Gg(e,n){var a=un();n=n===void 0?null:n;var o=a.memoizedState;if(n!==null&&jf(n,o[1]))return o[0];if(o=e(),Bs){Ot(!0);try{e()}finally{Ot(!1)}}return a.memoizedState=[o,n],o}function ih(e,n,a){return a===void 0||(ra&1073741824)!==0&&(Se&261930)===0?e.memoizedState=n:(e.memoizedState=a,e=V_(),le.lanes|=e,Xa|=e,a)}function Vg(e,n,a,o){return ii(a,n)?a:Nr.current!==null?(e=ih(e,a,o),ii(e,n)||(pn=!0),e):(ra&42)===0||(ra&1073741824)!==0&&(Se&261930)===0?(pn=!0,e.memoizedState=a):(e=V_(),le.lanes|=e,Xa|=e,n)}function kg(e,n,a,o,u){var f=$.p;$.p=f!==0&&8>f?f:8;var y=B.T,A={};B.T=A,rh(e,!1,n,a);try{var F=u(),et=B.S;if(et!==null&&et(A,F),F!==null&&typeof F=="object"&&typeof F.then=="function"){var ht=MS(F,o);ol(e,n,ht,ci(e))}else ol(e,n,o,ci(e))}catch(vt){ol(e,n,{then:function(){},status:"rejected",reason:vt},ci())}finally{$.p=f,y!==null&&A.types!==null&&(y.types=A.types),B.T=y}}function CS(){}function ah(e,n,a,o){if(e.tag!==5)throw Error(s(476));var u=Xg(e).queue;kg(e,u,n,J,a===null?CS:function(){return jg(e),a(o)})}function Xg(e){var n=e.memoizedState;if(n!==null)return n;n={memoizedState:J,baseState:J,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:J},next:null};var a={};return n.next={memoizedState:a,baseState:a,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:a},next:null},e.memoizedState=n,e=e.alternate,e!==null&&(e.memoizedState=n),n}function jg(e){var n=Xg(e);n.next===null&&(n=e.alternate.memoizedState),ol(e,n.next.queue,{},ci())}function sh(){return wn(bl)}function qg(){return un().memoizedState}function Wg(){return un().memoizedState}function wS(e){for(var n=e.return;n!==null;){switch(n.tag){case 24:case 3:var a=ci();e=Ba(a);var o=Fa(n,e,a);o!==null&&(Kn(o,n,a),nl(o,n,a)),n={cache:Of()},e.payload=n;return}n=n.return}}function DS(e,n,a){var o=ci();a={lane:o,revertLane:0,gesture:null,action:a,hasEagerState:!1,eagerState:null,next:null},Nc(e)?Qg(n,a):(a=Ef(e,n,a,o),a!==null&&(Kn(a,e,o),Zg(a,n,o)))}function Yg(e,n,a){var o=ci();ol(e,n,a,o)}function ol(e,n,a,o){var u={lane:o,revertLane:0,gesture:null,action:a,hasEagerState:!1,eagerState:null,next:null};if(Nc(e))Qg(n,u);else{var f=e.alternate;if(e.lanes===0&&(f===null||f.lanes===0)&&(f=n.lastRenderedReducer,f!==null))try{var y=n.lastRenderedState,A=f(y,a);if(u.hasEagerState=!0,u.eagerState=A,ii(A,y))return hc(e,n,u,0),Ye===null&&fc(),!1}catch{}finally{}if(a=Ef(e,n,u,o),a!==null)return Kn(a,e,o),Zg(a,n,o),!0}return!1}function rh(e,n,a,o){if(o={lane:2,revertLane:Bh(),gesture:null,action:o,hasEagerState:!1,eagerState:null,next:null},Nc(e)){if(n)throw Error(s(479))}else n=Ef(e,a,o,2),n!==null&&Kn(n,e,2)}function Nc(e){var n=e.alternate;return e===le||n!==null&&n===le}function Qg(e,n){Lr=Tc=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function Zg(e,n,a){if((a&4194048)!==0){var o=n.lanes;o&=e.pendingLanes,a|=o,n.lanes=a,Bo(e,a)}}var ll={readContext:wn,use:Cc,useCallback:sn,useContext:sn,useEffect:sn,useImperativeHandle:sn,useLayoutEffect:sn,useInsertionEffect:sn,useMemo:sn,useReducer:sn,useRef:sn,useState:sn,useDebugValue:sn,useDeferredValue:sn,useTransition:sn,useSyncExternalStore:sn,useId:sn,useHostTransitionStatus:sn,useFormState:sn,useActionState:sn,useOptimistic:sn,useMemoCache:sn,useCacheRefresh:sn};ll.useEffectEvent=sn;var Kg={readContext:wn,use:Cc,useCallback:function(e,n){return Vn().memoizedState=[e,n===void 0?null:n],e},useContext:wn,useEffect:Og,useImperativeHandle:function(e,n,a){a=a!=null?a.concat([e]):null,Dc(4194308,4,Bg.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Dc(4194308,4,e,n)},useInsertionEffect:function(e,n){Dc(4,2,e,n)},useMemo:function(e,n){var a=Vn();n=n===void 0?null:n;var o=e();if(Bs){Ot(!0);try{e()}finally{Ot(!1)}}return a.memoizedState=[o,n],o},useReducer:function(e,n,a){var o=Vn();if(a!==void 0){var u=a(n);if(Bs){Ot(!0);try{a(n)}finally{Ot(!1)}}}else u=n;return o.memoizedState=o.baseState=u,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:u},o.queue=e,e=e.dispatch=DS.bind(null,le,e),[o.memoizedState,e]},useRef:function(e){var n=Vn();return e={current:e},n.memoizedState=e},useState:function(e){e=$f(e);var n=e.queue,a=Yg.bind(null,le,n);return n.dispatch=a,[e.memoizedState,a]},useDebugValue:nh,useDeferredValue:function(e,n){var a=Vn();return ih(a,e,n)},useTransition:function(){var e=$f(!1);return e=kg.bind(null,le,e.queue,!0,!1),Vn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,n,a){var o=le,u=Vn();if(be){if(a===void 0)throw Error(s(407));a=a()}else{if(a=n(),Ye===null)throw Error(s(349));(Se&127)!==0||vg(o,n,a)}u.memoizedState=a;var f={value:a,getSnapshot:n};return u.queue=f,Og(xg.bind(null,o,f,e),[e]),o.flags|=2048,Pr(9,{destroy:void 0},yg.bind(null,o,f,a,n),null),a},useId:function(){var e=Vn(),n=Ye.identifierPrefix;if(be){var a=ki,o=Vi;a=(o&~(1<<32-ee(o)-1)).toString(32)+a,n="_"+n+"R_"+a,a=Ac++,0<a&&(n+="H"+a.toString(32)),n+="_"}else a=ES++,n="_"+n+"r_"+a.toString(32)+"_";return e.memoizedState=n},useHostTransitionStatus:sh,useFormState:wg,useActionState:wg,useOptimistic:function(e){var n=Vn();n.memoizedState=n.baseState=e;var a={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return n.queue=a,n=rh.bind(null,le,!0,a),a.dispatch=n,[e,n]},useMemoCache:Zf,useCacheRefresh:function(){return Vn().memoizedState=wS.bind(null,le)},useEffectEvent:function(e){var n=Vn(),a={impl:e};return n.memoizedState=a,function(){if((Le&2)!==0)throw Error(s(440));return a.impl.apply(void 0,arguments)}}},oh={readContext:wn,use:Cc,useCallback:Hg,useContext:wn,useEffect:eh,useImperativeHandle:Fg,useInsertionEffect:zg,useLayoutEffect:Ig,useMemo:Gg,useReducer:wc,useRef:Lg,useState:function(){return wc(oa)},useDebugValue:nh,useDeferredValue:function(e,n){var a=un();return Vg(a,Ve.memoizedState,e,n)},useTransition:function(){var e=wc(oa)[0],n=un().memoizedState;return[typeof e=="boolean"?e:rl(e),n]},useSyncExternalStore:_g,useId:qg,useHostTransitionStatus:sh,useFormState:Dg,useActionState:Dg,useOptimistic:function(e,n){var a=un();return Eg(a,Ve,e,n)},useMemoCache:Zf,useCacheRefresh:Wg};oh.useEffectEvent=Pg;var Jg={readContext:wn,use:Cc,useCallback:Hg,useContext:wn,useEffect:eh,useImperativeHandle:Fg,useInsertionEffect:zg,useLayoutEffect:Ig,useMemo:Gg,useReducer:Jf,useRef:Lg,useState:function(){return Jf(oa)},useDebugValue:nh,useDeferredValue:function(e,n){var a=un();return Ve===null?ih(a,e,n):Vg(a,Ve.memoizedState,e,n)},useTransition:function(){var e=Jf(oa)[0],n=un().memoizedState;return[typeof e=="boolean"?e:rl(e),n]},useSyncExternalStore:_g,useId:qg,useHostTransitionStatus:sh,useFormState:Ng,useActionState:Ng,useOptimistic:function(e,n){var a=un();return Ve!==null?Eg(a,Ve,e,n):(a.baseState=e,[e,a.queue.dispatch])},useMemoCache:Zf,useCacheRefresh:Wg};Jg.useEffectEvent=Pg;function lh(e,n,a,o){n=e.memoizedState,a=a(o,n),a=a==null?n:_({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var ch={enqueueSetState:function(e,n,a){e=e._reactInternals;var o=ci(),u=Ba(o);u.payload=n,a!=null&&(u.callback=a),n=Fa(e,u,o),n!==null&&(Kn(n,e,o),nl(n,e,o))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var o=ci(),u=Ba(o);u.tag=1,u.payload=n,a!=null&&(u.callback=a),n=Fa(e,u,o),n!==null&&(Kn(n,e,o),nl(n,e,o))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=ci(),o=Ba(a);o.tag=2,n!=null&&(o.callback=n),n=Fa(e,o,a),n!==null&&(Kn(n,e,a),nl(n,e,a))}};function $g(e,n,a,o,u,f,y){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(o,f,y):n.prototype&&n.prototype.isPureReactComponent?!Yo(a,o)||!Yo(u,f):!0}function t_(e,n,a,o){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,o),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,o),n.state!==e&&ch.enqueueReplaceState(n,n.state,null)}function Fs(e,n){var a=n;if("ref"in n){a={};for(var o in n)o!=="ref"&&(a[o]=n[o])}if(e=e.defaultProps){a===n&&(a=_({},a));for(var u in e)a[u]===void 0&&(a[u]=e[u])}return a}function e_(e){uc(e)}function n_(e){console.error(e)}function i_(e){uc(e)}function Lc(e,n){try{var a=e.onUncaughtError;a(n.value,{componentStack:n.stack})}catch(o){setTimeout(function(){throw o})}}function a_(e,n,a){try{var o=e.onCaughtError;o(a.value,{componentStack:a.stack,errorBoundary:n.tag===1?n.stateNode:null})}catch(u){setTimeout(function(){throw u})}}function uh(e,n,a){return a=Ba(a),a.tag=3,a.payload={element:null},a.callback=function(){Lc(e,n)},a}function s_(e){return e=Ba(e),e.tag=3,e}function r_(e,n,a,o){var u=a.type.getDerivedStateFromError;if(typeof u=="function"){var f=o.value;e.payload=function(){return u(f)},e.callback=function(){a_(n,a,o)}}var y=a.stateNode;y!==null&&typeof y.componentDidCatch=="function"&&(e.callback=function(){a_(n,a,o),typeof u!="function"&&(ja===null?ja=new Set([this]):ja.add(this));var A=o.stack;this.componentDidCatch(o.value,{componentStack:A!==null?A:""})})}function US(e,n,a,o,u){if(a.flags|=32768,o!==null&&typeof o=="object"&&typeof o.then=="function"){if(n=a.alternate,n!==null&&Rr(n,a,u,!0),a=si.current,a!==null){switch(a.tag){case 31:case 13:return Si===null?jc():a.alternate===null&&rn===0&&(rn=3),a.flags&=-257,a.flags|=65536,a.lanes=u,o===xc?a.flags|=16384:(n=a.updateQueue,n===null?a.updateQueue=new Set([o]):n.add(o),Ph(e,o,u)),!1;case 22:return a.flags|=65536,o===xc?a.flags|=16384:(n=a.updateQueue,n===null?(n={transitions:null,markerInstances:null,retryQueue:new Set([o])},a.updateQueue=n):(a=n.retryQueue,a===null?n.retryQueue=new Set([o]):a.add(o)),Ph(e,o,u)),!1}throw Error(s(435,a.tag))}return Ph(e,o,u),jc(),!1}if(be)return n=si.current,n!==null?((n.flags&65536)===0&&(n.flags|=256),n.flags|=65536,n.lanes=u,o!==wf&&(e=Error(s(422),{cause:o}),Ko(_i(e,a)))):(o!==wf&&(n=Error(s(423),{cause:o}),Ko(_i(n,a))),e=e.current.alternate,e.flags|=65536,u&=-u,e.lanes|=u,o=_i(o,a),u=uh(e.stateNode,o,u),Hf(e,u),rn!==4&&(rn=2)),!1;var f=Error(s(520),{cause:o});if(f=_i(f,a),gl===null?gl=[f]:gl.push(f),rn!==4&&(rn=2),n===null)return!0;o=_i(o,a),a=n;do{switch(a.tag){case 3:return a.flags|=65536,e=u&-u,a.lanes|=e,e=uh(a.stateNode,o,e),Hf(a,e),!1;case 1:if(n=a.type,f=a.stateNode,(a.flags&128)===0&&(typeof n.getDerivedStateFromError=="function"||f!==null&&typeof f.componentDidCatch=="function"&&(ja===null||!ja.has(f))))return a.flags|=65536,u&=-u,a.lanes|=u,u=s_(u),r_(u,e,a,o),Hf(a,u),!1}a=a.return}while(a!==null);return!1}var fh=Error(s(461)),pn=!1;function Dn(e,n,a,o){n.child=e===null?ug(n,null,a,o):Is(n,e.child,a,o)}function o_(e,n,a,o,u){a=a.render;var f=n.ref;if("ref"in o){var y={};for(var A in o)A!=="ref"&&(y[A]=o[A])}else y=o;return Ls(n),o=qf(e,n,a,y,f,u),A=Wf(),e!==null&&!pn?(Yf(e,n,u),la(e,n,u)):(be&&A&&Rf(n),n.flags|=1,Dn(e,n,o,u),n.child)}function l_(e,n,a,o,u){if(e===null){var f=a.type;return typeof f=="function"&&!bf(f)&&f.defaultProps===void 0&&a.compare===null?(n.tag=15,n.type=f,c_(e,n,f,o,u)):(e=pc(a.type,null,o,n,n.mode,u),e.ref=n.ref,e.return=n,n.child=e)}if(f=e.child,!yh(e,u)){var y=f.memoizedProps;if(a=a.compare,a=a!==null?a:Yo,a(y,o)&&e.ref===n.ref)return la(e,n,u)}return n.flags|=1,e=na(f,o),e.ref=n.ref,e.return=n,n.child=e}function c_(e,n,a,o,u){if(e!==null){var f=e.memoizedProps;if(Yo(f,o)&&e.ref===n.ref)if(pn=!1,n.pendingProps=o=f,yh(e,u))(e.flags&131072)!==0&&(pn=!0);else return n.lanes=e.lanes,la(e,n,u)}return hh(e,n,a,o,u)}function u_(e,n,a,o){var u=o.children,f=e!==null?e.memoizedState:null;if(e===null&&n.stateNode===null&&(n.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),o.mode==="hidden"){if((n.flags&128)!==0){if(f=f!==null?f.baseLanes|a:a,e!==null){for(o=n.child=e.child,u=0;o!==null;)u=u|o.lanes|o.childLanes,o=o.sibling;o=u&~f}else o=0,n.child=null;return f_(e,n,f,a,o)}if((a&536870912)!==0)n.memoizedState={baseLanes:0,cachePool:null},e!==null&&vc(n,f!==null?f.cachePool:null),f!==null?dg(n,f):Vf(),pg(n);else return o=n.lanes=536870912,f_(e,n,f!==null?f.baseLanes|a:a,a,o)}else f!==null?(vc(n,f.cachePool),dg(n,f),Ga(),n.memoizedState=null):(e!==null&&vc(n,null),Vf(),Ga());return Dn(e,n,u,a),n.child}function cl(e,n){return e!==null&&e.tag===22||n.stateNode!==null||(n.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),n.sibling}function f_(e,n,a,o,u){var f=zf();return f=f===null?null:{parent:hn._currentValue,pool:f},n.memoizedState={baseLanes:a,cachePool:f},e!==null&&vc(n,null),Vf(),pg(n),e!==null&&Rr(e,n,o,!0),n.childLanes=u,null}function Oc(e,n){return n=zc({mode:n.mode,children:n.children},e.mode),n.ref=e.ref,e.child=n,n.return=e,n}function h_(e,n,a){return Is(n,e.child,null,a),e=Oc(n,n.pendingProps),e.flags|=2,ri(n),n.memoizedState=null,e}function NS(e,n,a){var o=n.pendingProps,u=(n.flags&128)!==0;if(n.flags&=-129,e===null){if(be){if(o.mode==="hidden")return e=Oc(n,o),n.lanes=536870912,cl(null,e);if(Xf(n),(e=Ze)?(e=b0(e,xi),e=e!==null&&e.data==="&"?e:null,e!==null&&(n.memoizedState={dehydrated:e,treeContext:La!==null?{id:Vi,overflow:ki}:null,retryLane:536870912,hydrationErrors:null},a=Qm(e),a.return=n,n.child=a,Cn=n,Ze=null)):e=null,e===null)throw Pa(n);return n.lanes=536870912,null}return Oc(n,o)}var f=e.memoizedState;if(f!==null){var y=f.dehydrated;if(Xf(n),u)if(n.flags&256)n.flags&=-257,n=h_(e,n,a);else if(n.memoizedState!==null)n.child=e.child,n.flags|=128,n=null;else throw Error(s(558));else if(pn||Rr(e,n,a,!1),u=(a&e.childLanes)!==0,pn||u){if(o=Ye,o!==null&&(y=Hi(o,a),y!==0&&y!==f.retryLane))throw f.retryLane=y,ws(e,y),Kn(o,e,y),fh;jc(),n=h_(e,n,a)}else e=f.treeContext,Ze=Mi(y.nextSibling),Cn=n,be=!0,Oa=null,xi=!1,e!==null&&Jm(n,e),n=Oc(n,o),n.flags|=4096;return n}return e=na(e.child,{mode:o.mode,children:o.children}),e.ref=n.ref,n.child=e,e.return=n,e}function Pc(e,n){var a=n.ref;if(a===null)e!==null&&e.ref!==null&&(n.flags|=4194816);else{if(typeof a!="function"&&typeof a!="object")throw Error(s(284));(e===null||e.ref!==a)&&(n.flags|=4194816)}}function hh(e,n,a,o,u){return Ls(n),a=qf(e,n,a,o,void 0,u),o=Wf(),e!==null&&!pn?(Yf(e,n,u),la(e,n,u)):(be&&o&&Rf(n),n.flags|=1,Dn(e,n,a,u),n.child)}function d_(e,n,a,o,u,f){return Ls(n),n.updateQueue=null,a=gg(n,o,a,u),mg(e),o=Wf(),e!==null&&!pn?(Yf(e,n,f),la(e,n,f)):(be&&o&&Rf(n),n.flags|=1,Dn(e,n,a,f),n.child)}function p_(e,n,a,o,u){if(Ls(n),n.stateNode===null){var f=Er,y=a.contextType;typeof y=="object"&&y!==null&&(f=wn(y)),f=new a(o,f),n.memoizedState=f.state!==null&&f.state!==void 0?f.state:null,f.updater=ch,n.stateNode=f,f._reactInternals=n,f=n.stateNode,f.props=o,f.state=n.memoizedState,f.refs={},Bf(n),y=a.contextType,f.context=typeof y=="object"&&y!==null?wn(y):Er,f.state=n.memoizedState,y=a.getDerivedStateFromProps,typeof y=="function"&&(lh(n,a,y,o),f.state=n.memoizedState),typeof a.getDerivedStateFromProps=="function"||typeof f.getSnapshotBeforeUpdate=="function"||typeof f.UNSAFE_componentWillMount!="function"&&typeof f.componentWillMount!="function"||(y=f.state,typeof f.componentWillMount=="function"&&f.componentWillMount(),typeof f.UNSAFE_componentWillMount=="function"&&f.UNSAFE_componentWillMount(),y!==f.state&&ch.enqueueReplaceState(f,f.state,null),al(n,o,f,u),il(),f.state=n.memoizedState),typeof f.componentDidMount=="function"&&(n.flags|=4194308),o=!0}else if(e===null){f=n.stateNode;var A=n.memoizedProps,F=Fs(a,A);f.props=F;var et=f.context,ht=a.contextType;y=Er,typeof ht=="object"&&ht!==null&&(y=wn(ht));var vt=a.getDerivedStateFromProps;ht=typeof vt=="function"||typeof f.getSnapshotBeforeUpdate=="function",A=n.pendingProps!==A,ht||typeof f.UNSAFE_componentWillReceiveProps!="function"&&typeof f.componentWillReceiveProps!="function"||(A||et!==y)&&t_(n,f,o,y),Ia=!1;var nt=n.memoizedState;f.state=nt,al(n,o,f,u),il(),et=n.memoizedState,A||nt!==et||Ia?(typeof vt=="function"&&(lh(n,a,vt,o),et=n.memoizedState),(F=Ia||$g(n,a,F,o,nt,et,y))?(ht||typeof f.UNSAFE_componentWillMount!="function"&&typeof f.componentWillMount!="function"||(typeof f.componentWillMount=="function"&&f.componentWillMount(),typeof f.UNSAFE_componentWillMount=="function"&&f.UNSAFE_componentWillMount()),typeof f.componentDidMount=="function"&&(n.flags|=4194308)):(typeof f.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=o,n.memoizedState=et),f.props=o,f.state=et,f.context=y,o=F):(typeof f.componentDidMount=="function"&&(n.flags|=4194308),o=!1)}else{f=n.stateNode,Ff(e,n),y=n.memoizedProps,ht=Fs(a,y),f.props=ht,vt=n.pendingProps,nt=f.context,et=a.contextType,F=Er,typeof et=="object"&&et!==null&&(F=wn(et)),A=a.getDerivedStateFromProps,(et=typeof A=="function"||typeof f.getSnapshotBeforeUpdate=="function")||typeof f.UNSAFE_componentWillReceiveProps!="function"&&typeof f.componentWillReceiveProps!="function"||(y!==vt||nt!==F)&&t_(n,f,o,F),Ia=!1,nt=n.memoizedState,f.state=nt,al(n,o,f,u),il();var ct=n.memoizedState;y!==vt||nt!==ct||Ia||e!==null&&e.dependencies!==null&&gc(e.dependencies)?(typeof A=="function"&&(lh(n,a,A,o),ct=n.memoizedState),(ht=Ia||$g(n,a,ht,o,nt,ct,F)||e!==null&&e.dependencies!==null&&gc(e.dependencies))?(et||typeof f.UNSAFE_componentWillUpdate!="function"&&typeof f.componentWillUpdate!="function"||(typeof f.componentWillUpdate=="function"&&f.componentWillUpdate(o,ct,F),typeof f.UNSAFE_componentWillUpdate=="function"&&f.UNSAFE_componentWillUpdate(o,ct,F)),typeof f.componentDidUpdate=="function"&&(n.flags|=4),typeof f.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof f.componentDidUpdate!="function"||y===e.memoizedProps&&nt===e.memoizedState||(n.flags|=4),typeof f.getSnapshotBeforeUpdate!="function"||y===e.memoizedProps&&nt===e.memoizedState||(n.flags|=1024),n.memoizedProps=o,n.memoizedState=ct),f.props=o,f.state=ct,f.context=F,o=ht):(typeof f.componentDidUpdate!="function"||y===e.memoizedProps&&nt===e.memoizedState||(n.flags|=4),typeof f.getSnapshotBeforeUpdate!="function"||y===e.memoizedProps&&nt===e.memoizedState||(n.flags|=1024),o=!1)}return f=o,Pc(e,n),o=(n.flags&128)!==0,f||o?(f=n.stateNode,a=o&&typeof a.getDerivedStateFromError!="function"?null:f.render(),n.flags|=1,e!==null&&o?(n.child=Is(n,e.child,null,u),n.child=Is(n,null,a,u)):Dn(e,n,a,u),n.memoizedState=f.state,e=n.child):e=la(e,n,u),e}function m_(e,n,a,o){return Us(),n.flags|=256,Dn(e,n,a,o),n.child}var dh={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function ph(e){return{baseLanes:e,cachePool:ag()}}function mh(e,n,a){return e=e!==null?e.childLanes&~a:0,n&&(e|=li),e}function g_(e,n,a){var o=n.pendingProps,u=!1,f=(n.flags&128)!==0,y;if((y=f)||(y=e!==null&&e.memoizedState===null?!1:(cn.current&2)!==0),y&&(u=!0,n.flags&=-129),y=(n.flags&32)!==0,n.flags&=-33,e===null){if(be){if(u?Ha(n):Ga(),(e=Ze)?(e=b0(e,xi),e=e!==null&&e.data!=="&"?e:null,e!==null&&(n.memoizedState={dehydrated:e,treeContext:La!==null?{id:Vi,overflow:ki}:null,retryLane:536870912,hydrationErrors:null},a=Qm(e),a.return=n,n.child=a,Cn=n,Ze=null)):e=null,e===null)throw Pa(n);return Kh(e)?n.lanes=32:n.lanes=536870912,null}var A=o.children;return o=o.fallback,u?(Ga(),u=n.mode,A=zc({mode:"hidden",children:A},u),o=Ds(o,u,a,null),A.return=n,o.return=n,A.sibling=o,n.child=A,o=n.child,o.memoizedState=ph(a),o.childLanes=mh(e,y,a),n.memoizedState=dh,cl(null,o)):(Ha(n),gh(n,A))}var F=e.memoizedState;if(F!==null&&(A=F.dehydrated,A!==null)){if(f)n.flags&256?(Ha(n),n.flags&=-257,n=_h(e,n,a)):n.memoizedState!==null?(Ga(),n.child=e.child,n.flags|=128,n=null):(Ga(),A=o.fallback,u=n.mode,o=zc({mode:"visible",children:o.children},u),A=Ds(A,u,a,null),A.flags|=2,o.return=n,A.return=n,o.sibling=A,n.child=o,Is(n,e.child,null,a),o=n.child,o.memoizedState=ph(a),o.childLanes=mh(e,y,a),n.memoizedState=dh,n=cl(null,o));else if(Ha(n),Kh(A)){if(y=A.nextSibling&&A.nextSibling.dataset,y)var et=y.dgst;y=et,o=Error(s(419)),o.stack="",o.digest=y,Ko({value:o,source:null,stack:null}),n=_h(e,n,a)}else if(pn||Rr(e,n,a,!1),y=(a&e.childLanes)!==0,pn||y){if(y=Ye,y!==null&&(o=Hi(y,a),o!==0&&o!==F.retryLane))throw F.retryLane=o,ws(e,o),Kn(y,e,o),fh;Zh(A)||jc(),n=_h(e,n,a)}else Zh(A)?(n.flags|=192,n.child=e.child,n=null):(e=F.treeContext,Ze=Mi(A.nextSibling),Cn=n,be=!0,Oa=null,xi=!1,e!==null&&Jm(n,e),n=gh(n,o.children),n.flags|=4096);return n}return u?(Ga(),A=o.fallback,u=n.mode,F=e.child,et=F.sibling,o=na(F,{mode:"hidden",children:o.children}),o.subtreeFlags=F.subtreeFlags&65011712,et!==null?A=na(et,A):(A=Ds(A,u,a,null),A.flags|=2),A.return=n,o.return=n,o.sibling=A,n.child=o,cl(null,o),o=n.child,A=e.child.memoizedState,A===null?A=ph(a):(u=A.cachePool,u!==null?(F=hn._currentValue,u=u.parent!==F?{parent:F,pool:F}:u):u=ag(),A={baseLanes:A.baseLanes|a,cachePool:u}),o.memoizedState=A,o.childLanes=mh(e,y,a),n.memoizedState=dh,cl(e.child,o)):(Ha(n),a=e.child,e=a.sibling,a=na(a,{mode:"visible",children:o.children}),a.return=n,a.sibling=null,e!==null&&(y=n.deletions,y===null?(n.deletions=[e],n.flags|=16):y.push(e)),n.child=a,n.memoizedState=null,a)}function gh(e,n){return n=zc({mode:"visible",children:n},e.mode),n.return=e,e.child=n}function zc(e,n){return e=ai(22,e,null,n),e.lanes=0,e}function _h(e,n,a){return Is(n,e.child,null,a),e=gh(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function __(e,n,a){e.lanes|=n;var o=e.alternate;o!==null&&(o.lanes|=n),Nf(e.return,n,a)}function vh(e,n,a,o,u,f){var y=e.memoizedState;y===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:o,tail:a,tailMode:u,treeForkCount:f}:(y.isBackwards=n,y.rendering=null,y.renderingStartTime=0,y.last=o,y.tail=a,y.tailMode=u,y.treeForkCount=f)}function v_(e,n,a){var o=n.pendingProps,u=o.revealOrder,f=o.tail;o=o.children;var y=cn.current,A=(y&2)!==0;if(A?(y=y&1|2,n.flags|=128):y&=1,Mt(cn,y),Dn(e,n,o,a),o=be?Zo:0,!A&&e!==null&&(e.flags&128)!==0)t:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&__(e,a,n);else if(e.tag===19)__(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break t;for(;e.sibling===null;){if(e.return===null||e.return===n)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(u){case"forwards":for(a=n.child,u=null;a!==null;)e=a.alternate,e!==null&&bc(e)===null&&(u=a),a=a.sibling;a=u,a===null?(u=n.child,n.child=null):(u=a.sibling,a.sibling=null),vh(n,!1,u,a,f,o);break;case"backwards":case"unstable_legacy-backwards":for(a=null,u=n.child,n.child=null;u!==null;){if(e=u.alternate,e!==null&&bc(e)===null){n.child=u;break}e=u.sibling,u.sibling=a,a=u,u=e}vh(n,!0,a,null,f,o);break;case"together":vh(n,!1,null,null,void 0,o);break;default:n.memoizedState=null}return n.child}function la(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),Xa|=n.lanes,(a&n.childLanes)===0)if(e!==null){if(Rr(e,n,a,!1),(a&n.childLanes)===0)return null}else return null;if(e!==null&&n.child!==e.child)throw Error(s(153));if(n.child!==null){for(e=n.child,a=na(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=na(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function yh(e,n){return(e.lanes&n)!==0?!0:(e=e.dependencies,!!(e!==null&&gc(e)))}function LS(e,n,a){switch(n.tag){case 3:kt(n,n.stateNode.containerInfo),za(n,hn,e.memoizedState.cache),Us();break;case 27:case 5:se(n);break;case 4:kt(n,n.stateNode.containerInfo);break;case 10:za(n,n.type,n.memoizedProps.value);break;case 31:if(n.memoizedState!==null)return n.flags|=128,Xf(n),null;break;case 13:var o=n.memoizedState;if(o!==null)return o.dehydrated!==null?(Ha(n),n.flags|=128,null):(a&n.child.childLanes)!==0?g_(e,n,a):(Ha(n),e=la(e,n,a),e!==null?e.sibling:null);Ha(n);break;case 19:var u=(e.flags&128)!==0;if(o=(a&n.childLanes)!==0,o||(Rr(e,n,a,!1),o=(a&n.childLanes)!==0),u){if(o)return v_(e,n,a);n.flags|=128}if(u=n.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),Mt(cn,cn.current),o)break;return null;case 22:return n.lanes=0,u_(e,n,a,n.pendingProps);case 24:za(n,hn,e.memoizedState.cache)}return la(e,n,a)}function y_(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps)pn=!0;else{if(!yh(e,a)&&(n.flags&128)===0)return pn=!1,LS(e,n,a);pn=(e.flags&131072)!==0}else pn=!1,be&&(n.flags&1048576)!==0&&Km(n,Zo,n.index);switch(n.lanes=0,n.tag){case 16:t:{var o=n.pendingProps;if(e=Ps(n.elementType),n.type=e,typeof e=="function")bf(e)?(o=Fs(e,o),n.tag=1,n=p_(null,n,e,o,a)):(n.tag=0,n=hh(null,n,e,o,a));else{if(e!=null){var u=e.$$typeof;if(u===T){n.tag=11,n=o_(null,n,e,o,a);break t}else if(u===P){n.tag=14,n=l_(null,n,e,o,a);break t}}throw n=mt(e)||e,Error(s(306,n,""))}}return n;case 0:return hh(e,n,n.type,n.pendingProps,a);case 1:return o=n.type,u=Fs(o,n.pendingProps),p_(e,n,o,u,a);case 3:t:{if(kt(n,n.stateNode.containerInfo),e===null)throw Error(s(387));o=n.pendingProps;var f=n.memoizedState;u=f.element,Ff(e,n),al(n,o,null,a);var y=n.memoizedState;if(o=y.cache,za(n,hn,o),o!==f.cache&&Lf(n,[hn],a,!0),il(),o=y.element,f.isDehydrated)if(f={element:o,isDehydrated:!1,cache:y.cache},n.updateQueue.baseState=f,n.memoizedState=f,n.flags&256){n=m_(e,n,o,a);break t}else if(o!==u){u=_i(Error(s(424)),n),Ko(u),n=m_(e,n,o,a);break t}else{switch(e=n.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Ze=Mi(e.firstChild),Cn=n,be=!0,Oa=null,xi=!0,a=ug(n,null,o,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling}else{if(Us(),o===u){n=la(e,n,a);break t}Dn(e,n,o,a)}n=n.child}return n;case 26:return Pc(e,n),e===null?(a=D0(n.type,null,n.pendingProps,null))?n.memoizedState=a:be||(a=n.type,e=n.pendingProps,o=Jc(Tt.current).createElement(a),o[an]=n,o[Rn]=e,Un(o,a,e),xt(o),n.stateNode=o):n.memoizedState=D0(n.type,e.memoizedProps,n.pendingProps,e.memoizedState),null;case 27:return se(n),e===null&&be&&(o=n.stateNode=R0(n.type,n.pendingProps,Tt.current),Cn=n,xi=!0,u=Ze,Qa(n.type)?(Jh=u,Ze=Mi(o.firstChild)):Ze=u),Dn(e,n,n.pendingProps.children,a),Pc(e,n),e===null&&(n.flags|=4194304),n.child;case 5:return e===null&&be&&((u=o=Ze)&&(o=cM(o,n.type,n.pendingProps,xi),o!==null?(n.stateNode=o,Cn=n,Ze=Mi(o.firstChild),xi=!1,u=!0):u=!1),u||Pa(n)),se(n),u=n.type,f=n.pendingProps,y=e!==null?e.memoizedProps:null,o=f.children,Wh(u,f)?o=null:y!==null&&Wh(u,y)&&(n.flags|=32),n.memoizedState!==null&&(u=qf(e,n,bS,null,null,a),bl._currentValue=u),Pc(e,n),Dn(e,n,o,a),n.child;case 6:return e===null&&be&&((e=a=Ze)&&(a=uM(a,n.pendingProps,xi),a!==null?(n.stateNode=a,Cn=n,Ze=null,e=!0):e=!1),e||Pa(n)),null;case 13:return g_(e,n,a);case 4:return kt(n,n.stateNode.containerInfo),o=n.pendingProps,e===null?n.child=Is(n,null,o,a):Dn(e,n,o,a),n.child;case 11:return o_(e,n,n.type,n.pendingProps,a);case 7:return Dn(e,n,n.pendingProps,a),n.child;case 8:return Dn(e,n,n.pendingProps.children,a),n.child;case 12:return Dn(e,n,n.pendingProps.children,a),n.child;case 10:return o=n.pendingProps,za(n,n.type,o.value),Dn(e,n,o.children,a),n.child;case 9:return u=n.type._context,o=n.pendingProps.children,Ls(n),u=wn(u),o=o(u),n.flags|=1,Dn(e,n,o,a),n.child;case 14:return l_(e,n,n.type,n.pendingProps,a);case 15:return c_(e,n,n.type,n.pendingProps,a);case 19:return v_(e,n,a);case 31:return NS(e,n,a);case 22:return u_(e,n,a,n.pendingProps);case 24:return Ls(n),o=wn(hn),e===null?(u=zf(),u===null&&(u=Ye,f=Of(),u.pooledCache=f,f.refCount++,f!==null&&(u.pooledCacheLanes|=a),u=f),n.memoizedState={parent:o,cache:u},Bf(n),za(n,hn,u)):((e.lanes&a)!==0&&(Ff(e,n),al(n,null,null,a),il()),u=e.memoizedState,f=n.memoizedState,u.parent!==o?(u={parent:o,cache:o},n.memoizedState=u,n.lanes===0&&(n.memoizedState=n.updateQueue.baseState=u),za(n,hn,o)):(o=f.cache,za(n,hn,o),o!==u.cache&&Lf(n,[hn],a,!0))),Dn(e,n,n.pendingProps.children,a),n.child;case 29:throw n.pendingProps}throw Error(s(156,n.tag))}function ca(e){e.flags|=4}function xh(e,n,a,o,u){if((n=(e.mode&32)!==0)&&(n=!1),n){if(e.flags|=16777216,(u&335544128)===u)if(e.stateNode.complete)e.flags|=8192;else if(q_())e.flags|=8192;else throw zs=xc,If}else e.flags&=-16777217}function x_(e,n){if(n.type!=="stylesheet"||(n.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!P0(n))if(q_())e.flags|=8192;else throw zs=xc,If}function Ic(e,n){n!==null&&(e.flags|=4),e.flags&16384&&(n=e.tag!==22?_n():536870912,e.lanes|=n,Fr|=n)}function ul(e,n){if(!be)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var o=null;a!==null;)a.alternate!==null&&(o=a),a=a.sibling;o===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:o.sibling=null}}function Ke(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,o=0;if(n)for(var u=e.child;u!==null;)a|=u.lanes|u.childLanes,o|=u.subtreeFlags&65011712,o|=u.flags&65011712,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)a|=u.lanes|u.childLanes,o|=u.subtreeFlags,o|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=o,e.childLanes=a,n}function OS(e,n,a){var o=n.pendingProps;switch(Cf(n),n.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Ke(n),null;case 1:return Ke(n),null;case 3:return a=n.stateNode,o=null,e!==null&&(o=e.memoizedState.cache),n.memoizedState.cache!==o&&(n.flags|=2048),sa(hn),Gt(),a.pendingContext&&(a.context=a.pendingContext,a.pendingContext=null),(e===null||e.child===null)&&(Ar(n)?ca(n):e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,Df())),Ke(n),null;case 26:var u=n.type,f=n.memoizedState;return e===null?(ca(n),f!==null?(Ke(n),x_(n,f)):(Ke(n),xh(n,u,null,o,a))):f?f!==e.memoizedState?(ca(n),Ke(n),x_(n,f)):(Ke(n),n.flags&=-16777217):(e=e.memoizedProps,e!==o&&ca(n),Ke(n),xh(n,u,e,o,a)),null;case 27:if(He(n),a=Tt.current,u=n.type,e!==null&&n.stateNode!=null)e.memoizedProps!==o&&ca(n);else{if(!o){if(n.stateNode===null)throw Error(s(166));return Ke(n),null}e=K.current,Ar(n)?$m(n):(e=R0(u,o,a),n.stateNode=e,ca(n))}return Ke(n),null;case 5:if(He(n),u=n.type,e!==null&&n.stateNode!=null)e.memoizedProps!==o&&ca(n);else{if(!o){if(n.stateNode===null)throw Error(s(166));return Ke(n),null}if(f=K.current,Ar(n))$m(n);else{var y=Jc(Tt.current);switch(f){case 1:f=y.createElementNS("http://www.w3.org/2000/svg",u);break;case 2:f=y.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;default:switch(u){case"svg":f=y.createElementNS("http://www.w3.org/2000/svg",u);break;case"math":f=y.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;case"script":f=y.createElement("div"),f.innerHTML="<script><\/script>",f=f.removeChild(f.firstChild);break;case"select":f=typeof o.is=="string"?y.createElement("select",{is:o.is}):y.createElement("select"),o.multiple?f.multiple=!0:o.size&&(f.size=o.size);break;default:f=typeof o.is=="string"?y.createElement(u,{is:o.is}):y.createElement(u)}}f[an]=n,f[Rn]=o;t:for(y=n.child;y!==null;){if(y.tag===5||y.tag===6)f.appendChild(y.stateNode);else if(y.tag!==4&&y.tag!==27&&y.child!==null){y.child.return=y,y=y.child;continue}if(y===n)break t;for(;y.sibling===null;){if(y.return===null||y.return===n)break t;y=y.return}y.sibling.return=y.return,y=y.sibling}n.stateNode=f;t:switch(Un(f,u,o),u){case"button":case"input":case"select":case"textarea":o=!!o.autoFocus;break t;case"img":o=!0;break t;default:o=!1}o&&ca(n)}}return Ke(n),xh(n,n.type,e===null?null:e.memoizedProps,n.pendingProps,a),null;case 6:if(e&&n.stateNode!=null)e.memoizedProps!==o&&ca(n);else{if(typeof o!="string"&&n.stateNode===null)throw Error(s(166));if(e=Tt.current,Ar(n)){if(e=n.stateNode,a=n.memoizedProps,o=null,u=Cn,u!==null)switch(u.tag){case 27:case 5:o=u.memoizedProps}e[an]=n,e=!!(e.nodeValue===a||o!==null&&o.suppressHydrationWarning===!0||g0(e.nodeValue,a)),e||Pa(n,!0)}else e=Jc(e).createTextNode(o),e[an]=n,n.stateNode=e}return Ke(n),null;case 31:if(a=n.memoizedState,e===null||e.memoizedState!==null){if(o=Ar(n),a!==null){if(e===null){if(!o)throw Error(s(318));if(e=n.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(557));e[an]=n}else Us(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Ke(n),e=!1}else a=Df(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=a),e=!0;if(!e)return n.flags&256?(ri(n),n):(ri(n),null);if((n.flags&128)!==0)throw Error(s(558))}return Ke(n),null;case 13:if(o=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(u=Ar(n),o!==null&&o.dehydrated!==null){if(e===null){if(!u)throw Error(s(318));if(u=n.memoizedState,u=u!==null?u.dehydrated:null,!u)throw Error(s(317));u[an]=n}else Us(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Ke(n),u=!1}else u=Df(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=u),u=!0;if(!u)return n.flags&256?(ri(n),n):(ri(n),null)}return ri(n),(n.flags&128)!==0?(n.lanes=a,n):(a=o!==null,e=e!==null&&e.memoizedState!==null,a&&(o=n.child,u=null,o.alternate!==null&&o.alternate.memoizedState!==null&&o.alternate.memoizedState.cachePool!==null&&(u=o.alternate.memoizedState.cachePool.pool),f=null,o.memoizedState!==null&&o.memoizedState.cachePool!==null&&(f=o.memoizedState.cachePool.pool),f!==u&&(o.flags|=2048)),a!==e&&a&&(n.child.flags|=8192),Ic(n,n.updateQueue),Ke(n),null);case 4:return Gt(),e===null&&Vh(n.stateNode.containerInfo),Ke(n),null;case 10:return sa(n.type),Ke(n),null;case 19:if(at(cn),o=n.memoizedState,o===null)return Ke(n),null;if(u=(n.flags&128)!==0,f=o.rendering,f===null)if(u)ul(o,!1);else{if(rn!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(f=bc(e),f!==null){for(n.flags|=128,ul(o,!1),e=f.updateQueue,n.updateQueue=e,Ic(n,e),n.subtreeFlags=0,e=a,a=n.child;a!==null;)Ym(a,e),a=a.sibling;return Mt(cn,cn.current&1|2),be&&ia(n,o.treeForkCount),n.child}e=e.sibling}o.tail!==null&&dt()>Vc&&(n.flags|=128,u=!0,ul(o,!1),n.lanes=4194304)}else{if(!u)if(e=bc(f),e!==null){if(n.flags|=128,u=!0,e=e.updateQueue,n.updateQueue=e,Ic(n,e),ul(o,!0),o.tail===null&&o.tailMode==="hidden"&&!f.alternate&&!be)return Ke(n),null}else 2*dt()-o.renderingStartTime>Vc&&a!==536870912&&(n.flags|=128,u=!0,ul(o,!1),n.lanes=4194304);o.isBackwards?(f.sibling=n.child,n.child=f):(e=o.last,e!==null?e.sibling=f:n.child=f,o.last=f)}return o.tail!==null?(e=o.tail,o.rendering=e,o.tail=e.sibling,o.renderingStartTime=dt(),e.sibling=null,a=cn.current,Mt(cn,u?a&1|2:a&1),be&&ia(n,o.treeForkCount),e):(Ke(n),null);case 22:case 23:return ri(n),kf(),o=n.memoizedState!==null,e!==null?e.memoizedState!==null!==o&&(n.flags|=8192):o&&(n.flags|=8192),o?(a&536870912)!==0&&(n.flags&128)===0&&(Ke(n),n.subtreeFlags&6&&(n.flags|=8192)):Ke(n),a=n.updateQueue,a!==null&&Ic(n,a.retryQueue),a=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(a=e.memoizedState.cachePool.pool),o=null,n.memoizedState!==null&&n.memoizedState.cachePool!==null&&(o=n.memoizedState.cachePool.pool),o!==a&&(n.flags|=2048),e!==null&&at(Os),null;case 24:return a=null,e!==null&&(a=e.memoizedState.cache),n.memoizedState.cache!==a&&(n.flags|=2048),sa(hn),Ke(n),null;case 25:return null;case 30:return null}throw Error(s(156,n.tag))}function PS(e,n){switch(Cf(n),n.tag){case 1:return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return sa(hn),Gt(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 26:case 27:case 5:return He(n),null;case 31:if(n.memoizedState!==null){if(ri(n),n.alternate===null)throw Error(s(340));Us()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 13:if(ri(n),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(s(340));Us()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return at(cn),null;case 4:return Gt(),null;case 10:return sa(n.type),null;case 22:case 23:return ri(n),kf(),e!==null&&at(Os),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 24:return sa(hn),null;case 25:return null;default:return null}}function S_(e,n){switch(Cf(n),n.tag){case 3:sa(hn),Gt();break;case 26:case 27:case 5:He(n);break;case 4:Gt();break;case 31:n.memoizedState!==null&&ri(n);break;case 13:ri(n);break;case 19:at(cn);break;case 10:sa(n.type);break;case 22:case 23:ri(n),kf(),e!==null&&at(Os);break;case 24:sa(hn)}}function fl(e,n){try{var a=n.updateQueue,o=a!==null?a.lastEffect:null;if(o!==null){var u=o.next;a=u;do{if((a.tag&e)===e){o=void 0;var f=a.create,y=a.inst;o=f(),y.destroy=o}a=a.next}while(a!==u)}}catch(A){Fe(n,n.return,A)}}function Va(e,n,a){try{var o=n.updateQueue,u=o!==null?o.lastEffect:null;if(u!==null){var f=u.next;o=f;do{if((o.tag&e)===e){var y=o.inst,A=y.destroy;if(A!==void 0){y.destroy=void 0,u=n;var F=a,et=A;try{et()}catch(ht){Fe(u,F,ht)}}}o=o.next}while(o!==f)}}catch(ht){Fe(n,n.return,ht)}}function M_(e){var n=e.updateQueue;if(n!==null){var a=e.stateNode;try{hg(n,a)}catch(o){Fe(e,e.return,o)}}}function E_(e,n,a){a.props=Fs(e.type,e.memoizedProps),a.state=e.memoizedState;try{a.componentWillUnmount()}catch(o){Fe(e,n,o)}}function hl(e,n){try{var a=e.ref;if(a!==null){switch(e.tag){case 26:case 27:case 5:var o=e.stateNode;break;case 30:o=e.stateNode;break;default:o=e.stateNode}typeof a=="function"?e.refCleanup=a(o):a.current=o}}catch(u){Fe(e,n,u)}}function Xi(e,n){var a=e.ref,o=e.refCleanup;if(a!==null)if(typeof o=="function")try{o()}catch(u){Fe(e,n,u)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof a=="function")try{a(null)}catch(u){Fe(e,n,u)}else a.current=null}function b_(e){var n=e.type,a=e.memoizedProps,o=e.stateNode;try{t:switch(n){case"button":case"input":case"select":case"textarea":a.autoFocus&&o.focus();break t;case"img":a.src?o.src=a.src:a.srcSet&&(o.srcset=a.srcSet)}}catch(u){Fe(e,e.return,u)}}function Sh(e,n,a){try{var o=e.stateNode;iM(o,e.type,a,n),o[Rn]=n}catch(u){Fe(e,e.return,u)}}function T_(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&Qa(e.type)||e.tag===4}function Mh(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||T_(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&Qa(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Eh(e,n,a){var o=e.tag;if(o===5||o===6)e=e.stateNode,n?(a.nodeType===9?a.body:a.nodeName==="HTML"?a.ownerDocument.body:a).insertBefore(e,n):(n=a.nodeType===9?a.body:a.nodeName==="HTML"?a.ownerDocument.body:a,n.appendChild(e),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=ta));else if(o!==4&&(o===27&&Qa(e.type)&&(a=e.stateNode,n=null),e=e.child,e!==null))for(Eh(e,n,a),e=e.sibling;e!==null;)Eh(e,n,a),e=e.sibling}function Bc(e,n,a){var o=e.tag;if(o===5||o===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(o!==4&&(o===27&&Qa(e.type)&&(a=e.stateNode),e=e.child,e!==null))for(Bc(e,n,a),e=e.sibling;e!==null;)Bc(e,n,a),e=e.sibling}function A_(e){var n=e.stateNode,a=e.memoizedProps;try{for(var o=e.type,u=n.attributes;u.length;)n.removeAttributeNode(u[0]);Un(n,o,a),n[an]=e,n[Rn]=a}catch(f){Fe(e,e.return,f)}}var ua=!1,mn=!1,bh=!1,R_=typeof WeakSet=="function"?WeakSet:Set,En=null;function zS(e,n){if(e=e.containerInfo,jh=su,e=Fm(e),_f(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else t:{a=(a=e.ownerDocument)&&a.defaultView||window;var o=a.getSelection&&a.getSelection();if(o&&o.rangeCount!==0){a=o.anchorNode;var u=o.anchorOffset,f=o.focusNode;o=o.focusOffset;try{a.nodeType,f.nodeType}catch{a=null;break t}var y=0,A=-1,F=-1,et=0,ht=0,vt=e,nt=null;e:for(;;){for(var ct;vt!==a||u!==0&&vt.nodeType!==3||(A=y+u),vt!==f||o!==0&&vt.nodeType!==3||(F=y+o),vt.nodeType===3&&(y+=vt.nodeValue.length),(ct=vt.firstChild)!==null;)nt=vt,vt=ct;for(;;){if(vt===e)break e;if(nt===a&&++et===u&&(A=y),nt===f&&++ht===o&&(F=y),(ct=vt.nextSibling)!==null)break;vt=nt,nt=vt.parentNode}vt=ct}a=A===-1||F===-1?null:{start:A,end:F}}else a=null}a=a||{start:0,end:0}}else a=null;for(qh={focusedElem:e,selectionRange:a},su=!1,En=n;En!==null;)if(n=En,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,En=e;else for(;En!==null;){switch(n=En,f=n.alternate,e=n.flags,n.tag){case 0:if((e&4)!==0&&(e=n.updateQueue,e=e!==null?e.events:null,e!==null))for(a=0;a<e.length;a++)u=e[a],u.ref.impl=u.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&f!==null){e=void 0,a=n,u=f.memoizedProps,f=f.memoizedState,o=a.stateNode;try{var Ht=Fs(a.type,u);e=o.getSnapshotBeforeUpdate(Ht,f),o.__reactInternalSnapshotBeforeUpdate=e}catch(te){Fe(a,a.return,te)}}break;case 3:if((e&1024)!==0){if(e=n.stateNode.containerInfo,a=e.nodeType,a===9)Qh(e);else if(a===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":Qh(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(s(163))}if(e=n.sibling,e!==null){e.return=n.return,En=e;break}En=n.return}}function C_(e,n,a){var o=a.flags;switch(a.tag){case 0:case 11:case 15:ha(e,a),o&4&&fl(5,a);break;case 1:if(ha(e,a),o&4)if(e=a.stateNode,n===null)try{e.componentDidMount()}catch(y){Fe(a,a.return,y)}else{var u=Fs(a.type,n.memoizedProps);n=n.memoizedState;try{e.componentDidUpdate(u,n,e.__reactInternalSnapshotBeforeUpdate)}catch(y){Fe(a,a.return,y)}}o&64&&M_(a),o&512&&hl(a,a.return);break;case 3:if(ha(e,a),o&64&&(e=a.updateQueue,e!==null)){if(n=null,a.child!==null)switch(a.child.tag){case 27:case 5:n=a.child.stateNode;break;case 1:n=a.child.stateNode}try{hg(e,n)}catch(y){Fe(a,a.return,y)}}break;case 27:n===null&&o&4&&A_(a);case 26:case 5:ha(e,a),n===null&&o&4&&b_(a),o&512&&hl(a,a.return);break;case 12:ha(e,a);break;case 31:ha(e,a),o&4&&U_(e,a);break;case 13:ha(e,a),o&4&&N_(e,a),o&64&&(e=a.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(a=jS.bind(null,a),fM(e,a))));break;case 22:if(o=a.memoizedState!==null||ua,!o){n=n!==null&&n.memoizedState!==null||mn,u=ua;var f=mn;ua=o,(mn=n)&&!f?da(e,a,(a.subtreeFlags&8772)!==0):ha(e,a),ua=u,mn=f}break;case 30:break;default:ha(e,a)}}function w_(e){var n=e.alternate;n!==null&&(e.alternate=null,w_(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&w(n)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var en=null,Wn=!1;function fa(e,n,a){for(a=a.child;a!==null;)D_(e,n,a),a=a.sibling}function D_(e,n,a){if(qt&&typeof qt.onCommitFiberUnmount=="function")try{qt.onCommitFiberUnmount(Qt,a)}catch{}switch(a.tag){case 26:mn||Xi(a,n),fa(e,n,a),a.memoizedState?a.memoizedState.count--:a.stateNode&&(a=a.stateNode,a.parentNode.removeChild(a));break;case 27:mn||Xi(a,n);var o=en,u=Wn;Qa(a.type)&&(en=a.stateNode,Wn=!1),fa(e,n,a),Sl(a.stateNode),en=o,Wn=u;break;case 5:mn||Xi(a,n);case 6:if(o=en,u=Wn,en=null,fa(e,n,a),en=o,Wn=u,en!==null)if(Wn)try{(en.nodeType===9?en.body:en.nodeName==="HTML"?en.ownerDocument.body:en).removeChild(a.stateNode)}catch(f){Fe(a,n,f)}else try{en.removeChild(a.stateNode)}catch(f){Fe(a,n,f)}break;case 18:en!==null&&(Wn?(e=en,M0(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,a.stateNode),Wr(e)):M0(en,a.stateNode));break;case 4:o=en,u=Wn,en=a.stateNode.containerInfo,Wn=!0,fa(e,n,a),en=o,Wn=u;break;case 0:case 11:case 14:case 15:Va(2,a,n),mn||Va(4,a,n),fa(e,n,a);break;case 1:mn||(Xi(a,n),o=a.stateNode,typeof o.componentWillUnmount=="function"&&E_(a,n,o)),fa(e,n,a);break;case 21:fa(e,n,a);break;case 22:mn=(o=mn)||a.memoizedState!==null,fa(e,n,a),mn=o;break;default:fa(e,n,a)}}function U_(e,n){if(n.memoizedState===null&&(e=n.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{Wr(e)}catch(a){Fe(n,n.return,a)}}}function N_(e,n){if(n.memoizedState===null&&(e=n.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Wr(e)}catch(a){Fe(n,n.return,a)}}function IS(e){switch(e.tag){case 31:case 13:case 19:var n=e.stateNode;return n===null&&(n=e.stateNode=new R_),n;case 22:return e=e.stateNode,n=e._retryCache,n===null&&(n=e._retryCache=new R_),n;default:throw Error(s(435,e.tag))}}function Fc(e,n){var a=IS(e);n.forEach(function(o){if(!a.has(o)){a.add(o);var u=qS.bind(null,e,o);o.then(u,u)}})}function Yn(e,n){var a=n.deletions;if(a!==null)for(var o=0;o<a.length;o++){var u=a[o],f=e,y=n,A=y;t:for(;A!==null;){switch(A.tag){case 27:if(Qa(A.type)){en=A.stateNode,Wn=!1;break t}break;case 5:en=A.stateNode,Wn=!1;break t;case 3:case 4:en=A.stateNode.containerInfo,Wn=!0;break t}A=A.return}if(en===null)throw Error(s(160));D_(f,y,u),en=null,Wn=!1,f=u.alternate,f!==null&&(f.return=null),u.return=null}if(n.subtreeFlags&13886)for(n=n.child;n!==null;)L_(n,e),n=n.sibling}var Ui=null;function L_(e,n){var a=e.alternate,o=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Yn(n,e),Qn(e),o&4&&(Va(3,e,e.return),fl(3,e),Va(5,e,e.return));break;case 1:Yn(n,e),Qn(e),o&512&&(mn||a===null||Xi(a,a.return)),o&64&&ua&&(e=e.updateQueue,e!==null&&(o=e.callbacks,o!==null&&(a=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=a===null?o:a.concat(o))));break;case 26:var u=Ui;if(Yn(n,e),Qn(e),o&512&&(mn||a===null||Xi(a,a.return)),o&4){var f=a!==null?a.memoizedState:null;if(o=e.memoizedState,a===null)if(o===null)if(e.stateNode===null){t:{o=e.type,a=e.memoizedProps,u=u.ownerDocument||u;e:switch(o){case"title":f=u.getElementsByTagName("title")[0],(!f||f[bs]||f[an]||f.namespaceURI==="http://www.w3.org/2000/svg"||f.hasAttribute("itemprop"))&&(f=u.createElement(o),u.head.insertBefore(f,u.querySelector("head > title"))),Un(f,o,a),f[an]=e,xt(f),o=f;break t;case"link":var y=L0("link","href",u).get(o+(a.href||""));if(y){for(var A=0;A<y.length;A++)if(f=y[A],f.getAttribute("href")===(a.href==null||a.href===""?null:a.href)&&f.getAttribute("rel")===(a.rel==null?null:a.rel)&&f.getAttribute("title")===(a.title==null?null:a.title)&&f.getAttribute("crossorigin")===(a.crossOrigin==null?null:a.crossOrigin)){y.splice(A,1);break e}}f=u.createElement(o),Un(f,o,a),u.head.appendChild(f);break;case"meta":if(y=L0("meta","content",u).get(o+(a.content||""))){for(A=0;A<y.length;A++)if(f=y[A],f.getAttribute("content")===(a.content==null?null:""+a.content)&&f.getAttribute("name")===(a.name==null?null:a.name)&&f.getAttribute("property")===(a.property==null?null:a.property)&&f.getAttribute("http-equiv")===(a.httpEquiv==null?null:a.httpEquiv)&&f.getAttribute("charset")===(a.charSet==null?null:a.charSet)){y.splice(A,1);break e}}f=u.createElement(o),Un(f,o,a),u.head.appendChild(f);break;default:throw Error(s(468,o))}f[an]=e,xt(f),o=f}e.stateNode=o}else O0(u,e.type,e.stateNode);else e.stateNode=N0(u,o,e.memoizedProps);else f!==o?(f===null?a.stateNode!==null&&(a=a.stateNode,a.parentNode.removeChild(a)):f.count--,o===null?O0(u,e.type,e.stateNode):N0(u,o,e.memoizedProps)):o===null&&e.stateNode!==null&&Sh(e,e.memoizedProps,a.memoizedProps)}break;case 27:Yn(n,e),Qn(e),o&512&&(mn||a===null||Xi(a,a.return)),a!==null&&o&4&&Sh(e,e.memoizedProps,a.memoizedProps);break;case 5:if(Yn(n,e),Qn(e),o&512&&(mn||a===null||Xi(a,a.return)),e.flags&32){u=e.stateNode;try{gr(u,"")}catch(Ht){Fe(e,e.return,Ht)}}o&4&&e.stateNode!=null&&(u=e.memoizedProps,Sh(e,u,a!==null?a.memoizedProps:u)),o&1024&&(bh=!0);break;case 6:if(Yn(n,e),Qn(e),o&4){if(e.stateNode===null)throw Error(s(162));o=e.memoizedProps,a=e.stateNode;try{a.nodeValue=o}catch(Ht){Fe(e,e.return,Ht)}}break;case 3:if(eu=null,u=Ui,Ui=$c(n.containerInfo),Yn(n,e),Ui=u,Qn(e),o&4&&a!==null&&a.memoizedState.isDehydrated)try{Wr(n.containerInfo)}catch(Ht){Fe(e,e.return,Ht)}bh&&(bh=!1,O_(e));break;case 4:o=Ui,Ui=$c(e.stateNode.containerInfo),Yn(n,e),Qn(e),Ui=o;break;case 12:Yn(n,e),Qn(e);break;case 31:Yn(n,e),Qn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Fc(e,o)));break;case 13:Yn(n,e),Qn(e),e.child.flags&8192&&e.memoizedState!==null!=(a!==null&&a.memoizedState!==null)&&(Gc=dt()),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Fc(e,o)));break;case 22:u=e.memoizedState!==null;var F=a!==null&&a.memoizedState!==null,et=ua,ht=mn;if(ua=et||u,mn=ht||F,Yn(n,e),mn=ht,ua=et,Qn(e),o&8192)t:for(n=e.stateNode,n._visibility=u?n._visibility&-2:n._visibility|1,u&&(a===null||F||ua||mn||Hs(e)),a=null,n=e;;){if(n.tag===5||n.tag===26){if(a===null){F=a=n;try{if(f=F.stateNode,u)y=f.style,typeof y.setProperty=="function"?y.setProperty("display","none","important"):y.display="none";else{A=F.stateNode;var vt=F.memoizedProps.style,nt=vt!=null&&vt.hasOwnProperty("display")?vt.display:null;A.style.display=nt==null||typeof nt=="boolean"?"":(""+nt).trim()}}catch(Ht){Fe(F,F.return,Ht)}}}else if(n.tag===6){if(a===null){F=n;try{F.stateNode.nodeValue=u?"":F.memoizedProps}catch(Ht){Fe(F,F.return,Ht)}}}else if(n.tag===18){if(a===null){F=n;try{var ct=F.stateNode;u?E0(ct,!0):E0(F.stateNode,!1)}catch(Ht){Fe(F,F.return,Ht)}}}else if((n.tag!==22&&n.tag!==23||n.memoizedState===null||n===e)&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break t;for(;n.sibling===null;){if(n.return===null||n.return===e)break t;a===n&&(a=null),n=n.return}a===n&&(a=null),n.sibling.return=n.return,n=n.sibling}o&4&&(o=e.updateQueue,o!==null&&(a=o.retryQueue,a!==null&&(o.retryQueue=null,Fc(e,a))));break;case 19:Yn(n,e),Qn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Fc(e,o)));break;case 30:break;case 21:break;default:Yn(n,e),Qn(e)}}function Qn(e){var n=e.flags;if(n&2){try{for(var a,o=e.return;o!==null;){if(T_(o)){a=o;break}o=o.return}if(a==null)throw Error(s(160));switch(a.tag){case 27:var u=a.stateNode,f=Mh(e);Bc(e,f,u);break;case 5:var y=a.stateNode;a.flags&32&&(gr(y,""),a.flags&=-33);var A=Mh(e);Bc(e,A,y);break;case 3:case 4:var F=a.stateNode.containerInfo,et=Mh(e);Eh(e,et,F);break;default:throw Error(s(161))}}catch(ht){Fe(e,e.return,ht)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function O_(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var n=e;O_(n),n.tag===5&&n.flags&1024&&n.stateNode.reset(),e=e.sibling}}function ha(e,n){if(n.subtreeFlags&8772)for(n=n.child;n!==null;)C_(e,n.alternate,n),n=n.sibling}function Hs(e){for(e=e.child;e!==null;){var n=e;switch(n.tag){case 0:case 11:case 14:case 15:Va(4,n,n.return),Hs(n);break;case 1:Xi(n,n.return);var a=n.stateNode;typeof a.componentWillUnmount=="function"&&E_(n,n.return,a),Hs(n);break;case 27:Sl(n.stateNode);case 26:case 5:Xi(n,n.return),Hs(n);break;case 22:n.memoizedState===null&&Hs(n);break;case 30:Hs(n);break;default:Hs(n)}e=e.sibling}}function da(e,n,a){for(a=a&&(n.subtreeFlags&8772)!==0,n=n.child;n!==null;){var o=n.alternate,u=e,f=n,y=f.flags;switch(f.tag){case 0:case 11:case 15:da(u,f,a),fl(4,f);break;case 1:if(da(u,f,a),o=f,u=o.stateNode,typeof u.componentDidMount=="function")try{u.componentDidMount()}catch(et){Fe(o,o.return,et)}if(o=f,u=o.updateQueue,u!==null){var A=o.stateNode;try{var F=u.shared.hiddenCallbacks;if(F!==null)for(u.shared.hiddenCallbacks=null,u=0;u<F.length;u++)fg(F[u],A)}catch(et){Fe(o,o.return,et)}}a&&y&64&&M_(f),hl(f,f.return);break;case 27:A_(f);case 26:case 5:da(u,f,a),a&&o===null&&y&4&&b_(f),hl(f,f.return);break;case 12:da(u,f,a);break;case 31:da(u,f,a),a&&y&4&&U_(u,f);break;case 13:da(u,f,a),a&&y&4&&N_(u,f);break;case 22:f.memoizedState===null&&da(u,f,a),hl(f,f.return);break;case 30:break;default:da(u,f,a)}n=n.sibling}}function Th(e,n){var a=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(a=e.memoizedState.cachePool.pool),e=null,n.memoizedState!==null&&n.memoizedState.cachePool!==null&&(e=n.memoizedState.cachePool.pool),e!==a&&(e!=null&&e.refCount++,a!=null&&Jo(a))}function Ah(e,n){e=null,n.alternate!==null&&(e=n.alternate.memoizedState.cache),n=n.memoizedState.cache,n!==e&&(n.refCount++,e!=null&&Jo(e))}function Ni(e,n,a,o){if(n.subtreeFlags&10256)for(n=n.child;n!==null;)P_(e,n,a,o),n=n.sibling}function P_(e,n,a,o){var u=n.flags;switch(n.tag){case 0:case 11:case 15:Ni(e,n,a,o),u&2048&&fl(9,n);break;case 1:Ni(e,n,a,o);break;case 3:Ni(e,n,a,o),u&2048&&(e=null,n.alternate!==null&&(e=n.alternate.memoizedState.cache),n=n.memoizedState.cache,n!==e&&(n.refCount++,e!=null&&Jo(e)));break;case 12:if(u&2048){Ni(e,n,a,o),e=n.stateNode;try{var f=n.memoizedProps,y=f.id,A=f.onPostCommit;typeof A=="function"&&A(y,n.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(F){Fe(n,n.return,F)}}else Ni(e,n,a,o);break;case 31:Ni(e,n,a,o);break;case 13:Ni(e,n,a,o);break;case 23:break;case 22:f=n.stateNode,y=n.alternate,n.memoizedState!==null?f._visibility&2?Ni(e,n,a,o):dl(e,n):f._visibility&2?Ni(e,n,a,o):(f._visibility|=2,zr(e,n,a,o,(n.subtreeFlags&10256)!==0||!1)),u&2048&&Th(y,n);break;case 24:Ni(e,n,a,o),u&2048&&Ah(n.alternate,n);break;default:Ni(e,n,a,o)}}function zr(e,n,a,o,u){for(u=u&&((n.subtreeFlags&10256)!==0||!1),n=n.child;n!==null;){var f=e,y=n,A=a,F=o,et=y.flags;switch(y.tag){case 0:case 11:case 15:zr(f,y,A,F,u),fl(8,y);break;case 23:break;case 22:var ht=y.stateNode;y.memoizedState!==null?ht._visibility&2?zr(f,y,A,F,u):dl(f,y):(ht._visibility|=2,zr(f,y,A,F,u)),u&&et&2048&&Th(y.alternate,y);break;case 24:zr(f,y,A,F,u),u&&et&2048&&Ah(y.alternate,y);break;default:zr(f,y,A,F,u)}n=n.sibling}}function dl(e,n){if(n.subtreeFlags&10256)for(n=n.child;n!==null;){var a=e,o=n,u=o.flags;switch(o.tag){case 22:dl(a,o),u&2048&&Th(o.alternate,o);break;case 24:dl(a,o),u&2048&&Ah(o.alternate,o);break;default:dl(a,o)}n=n.sibling}}var pl=8192;function Ir(e,n,a){if(e.subtreeFlags&pl)for(e=e.child;e!==null;)z_(e,n,a),e=e.sibling}function z_(e,n,a){switch(e.tag){case 26:Ir(e,n,a),e.flags&pl&&e.memoizedState!==null&&EM(a,Ui,e.memoizedState,e.memoizedProps);break;case 5:Ir(e,n,a);break;case 3:case 4:var o=Ui;Ui=$c(e.stateNode.containerInfo),Ir(e,n,a),Ui=o;break;case 22:e.memoizedState===null&&(o=e.alternate,o!==null&&o.memoizedState!==null?(o=pl,pl=16777216,Ir(e,n,a),pl=o):Ir(e,n,a));break;default:Ir(e,n,a)}}function I_(e){var n=e.alternate;if(n!==null&&(e=n.child,e!==null)){n.child=null;do n=e.sibling,e.sibling=null,e=n;while(e!==null)}}function ml(e){var n=e.deletions;if((e.flags&16)!==0){if(n!==null)for(var a=0;a<n.length;a++){var o=n[a];En=o,F_(o,e)}I_(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)B_(e),e=e.sibling}function B_(e){switch(e.tag){case 0:case 11:case 15:ml(e),e.flags&2048&&Va(9,e,e.return);break;case 3:ml(e);break;case 12:ml(e);break;case 22:var n=e.stateNode;e.memoizedState!==null&&n._visibility&2&&(e.return===null||e.return.tag!==13)?(n._visibility&=-3,Hc(e)):ml(e);break;default:ml(e)}}function Hc(e){var n=e.deletions;if((e.flags&16)!==0){if(n!==null)for(var a=0;a<n.length;a++){var o=n[a];En=o,F_(o,e)}I_(e)}for(e=e.child;e!==null;){switch(n=e,n.tag){case 0:case 11:case 15:Va(8,n,n.return),Hc(n);break;case 22:a=n.stateNode,a._visibility&2&&(a._visibility&=-3,Hc(n));break;default:Hc(n)}e=e.sibling}}function F_(e,n){for(;En!==null;){var a=En;switch(a.tag){case 0:case 11:case 15:Va(8,a,n);break;case 23:case 22:if(a.memoizedState!==null&&a.memoizedState.cachePool!==null){var o=a.memoizedState.cachePool.pool;o!=null&&o.refCount++}break;case 24:Jo(a.memoizedState.cache)}if(o=a.child,o!==null)o.return=a,En=o;else t:for(a=e;En!==null;){o=En;var u=o.sibling,f=o.return;if(w_(o),o===a){En=null;break t}if(u!==null){u.return=f,En=u;break t}En=f}}}var BS={getCacheForType:function(e){var n=wn(hn),a=n.data.get(e);return a===void 0&&(a=e(),n.data.set(e,a)),a},cacheSignal:function(){return wn(hn).controller.signal}},FS=typeof WeakMap=="function"?WeakMap:Map,Le=0,Ye=null,me=null,Se=0,Be=0,oi=null,ka=!1,Br=!1,Rh=!1,pa=0,rn=0,Xa=0,Gs=0,Ch=0,li=0,Fr=0,gl=null,Zn=null,wh=!1,Gc=0,H_=0,Vc=1/0,kc=null,ja=null,yn=0,qa=null,Hr=null,ma=0,Dh=0,Uh=null,G_=null,_l=0,Nh=null;function ci(){return(Le&2)!==0&&Se!==0?Se&-Se:B.T!==null?Bh():Fo()}function V_(){if(li===0)if((Se&536870912)===0||be){var e=ut;ut<<=1,(ut&3932160)===0&&(ut=262144),li=e}else li=536870912;return e=si.current,e!==null&&(e.flags|=32),li}function Kn(e,n,a){(e===Ye&&(Be===2||Be===9)||e.cancelPendingCommit!==null)&&(Gr(e,0),Wa(e,Se,li,!1)),An(e,a),((Le&2)===0||e!==Ye)&&(e===Ye&&((Le&2)===0&&(Gs|=a),rn===4&&Wa(e,Se,li,!1)),ji(e))}function k_(e,n,a){if((Le&6)!==0)throw Error(s(327));var o=!a&&(n&127)===0&&(n&e.expiredLanes)===0||ne(e,n),u=o?VS(e,n):Oh(e,n,!0),f=o;do{if(u===0){Br&&!o&&Wa(e,n,0,!1);break}else{if(a=e.current.alternate,f&&!HS(a)){u=Oh(e,n,!1),f=!1;continue}if(u===2){if(f=n,e.errorRecoveryDisabledLanes&f)var y=0;else y=e.pendingLanes&-536870913,y=y!==0?y:y&536870912?536870912:0;if(y!==0){n=y;t:{var A=e;u=gl;var F=A.current.memoizedState.isDehydrated;if(F&&(Gr(A,y).flags|=256),y=Oh(A,y,!1),y!==2){if(Rh&&!F){A.errorRecoveryDisabledLanes|=f,Gs|=f,u=4;break t}f=Zn,Zn=u,f!==null&&(Zn===null?Zn=f:Zn.push.apply(Zn,f))}u=y}if(f=!1,u!==2)continue}}if(u===1){Gr(e,0),Wa(e,n,0,!0);break}t:{switch(o=e,f=u,f){case 0:case 1:throw Error(s(345));case 4:if((n&4194048)!==n)break;case 6:Wa(o,n,li,!ka);break t;case 2:Zn=null;break;case 3:case 5:break;default:throw Error(s(329))}if((n&62914560)===n&&(u=Gc+300-dt(),10<u)){if(Wa(o,n,li,!ka),Ut(o,0,!0)!==0)break t;ma=n,o.timeoutHandle=x0(X_.bind(null,o,a,Zn,kc,wh,n,li,Gs,Fr,ka,f,"Throttled",-0,0),u);break t}X_(o,a,Zn,kc,wh,n,li,Gs,Fr,ka,f,null,-0,0)}}break}while(!0);ji(e)}function X_(e,n,a,o,u,f,y,A,F,et,ht,vt,nt,ct){if(e.timeoutHandle=-1,vt=n.subtreeFlags,vt&8192||(vt&16785408)===16785408){vt={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:ta},z_(n,f,vt);var Ht=(f&62914560)===f?Gc-dt():(f&4194048)===f?H_-dt():0;if(Ht=bM(vt,Ht),Ht!==null){ma=f,e.cancelPendingCommit=Ht(J_.bind(null,e,n,f,a,o,u,y,A,F,ht,vt,null,nt,ct)),Wa(e,f,y,!et);return}}J_(e,n,f,a,o,u,y,A,F)}function HS(e){for(var n=e;;){var a=n.tag;if((a===0||a===11||a===15)&&n.flags&16384&&(a=n.updateQueue,a!==null&&(a=a.stores,a!==null)))for(var o=0;o<a.length;o++){var u=a[o],f=u.getSnapshot;u=u.value;try{if(!ii(f(),u))return!1}catch{return!1}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Wa(e,n,a,o){n&=~Ch,n&=~Gs,e.suspendedLanes|=n,e.pingedLanes&=~n,o&&(e.warmLanes|=n),o=e.expirationTimes;for(var u=n;0<u;){var f=31-ee(u),y=1<<f;o[f]=-1,u&=~y}a!==0&&Io(e,a,n)}function Xc(){return(Le&6)===0?(vl(0),!1):!0}function Lh(){if(me!==null){if(Be===0)var e=me.return;else e=me,aa=Ns=null,Qf(e),Ur=null,tl=0,e=me;for(;e!==null;)S_(e.alternate,e),e=e.return;me=null}}function Gr(e,n){var a=e.timeoutHandle;a!==-1&&(e.timeoutHandle=-1,rM(a)),a=e.cancelPendingCommit,a!==null&&(e.cancelPendingCommit=null,a()),ma=0,Lh(),Ye=e,me=a=na(e.current,null),Se=n,Be=0,oi=null,ka=!1,Br=ne(e,n),Rh=!1,Fr=li=Ch=Gs=Xa=rn=0,Zn=gl=null,wh=!1,(n&8)!==0&&(n|=n&32);var o=e.entangledLanes;if(o!==0)for(e=e.entanglements,o&=n;0<o;){var u=31-ee(o),f=1<<u;n|=e[u],o&=~f}return pa=n,fc(),a}function j_(e,n){le=null,B.H=ll,n===Dr||n===yc?(n=og(),Be=3):n===If?(n=og(),Be=4):Be=n===fh?8:n!==null&&typeof n=="object"&&typeof n.then=="function"?6:1,oi=n,me===null&&(rn=1,Lc(e,_i(n,e.current)))}function q_(){var e=si.current;return e===null?!0:(Se&4194048)===Se?Si===null:(Se&62914560)===Se||(Se&536870912)!==0?e===Si:!1}function W_(){var e=B.H;return B.H=ll,e===null?ll:e}function Y_(){var e=B.A;return B.A=BS,e}function jc(){rn=4,ka||(Se&4194048)!==Se&&si.current!==null||(Br=!0),(Xa&134217727)===0&&(Gs&134217727)===0||Ye===null||Wa(Ye,Se,li,!1)}function Oh(e,n,a){var o=Le;Le|=2;var u=W_(),f=Y_();(Ye!==e||Se!==n)&&(kc=null,Gr(e,n)),n=!1;var y=rn;t:do try{if(Be!==0&&me!==null){var A=me,F=oi;switch(Be){case 8:Lh(),y=6;break t;case 3:case 2:case 9:case 6:si.current===null&&(n=!0);var et=Be;if(Be=0,oi=null,Vr(e,A,F,et),a&&Br){y=0;break t}break;default:et=Be,Be=0,oi=null,Vr(e,A,F,et)}}GS(),y=rn;break}catch(ht){j_(e,ht)}while(!0);return n&&e.shellSuspendCounter++,aa=Ns=null,Le=o,B.H=u,B.A=f,me===null&&(Ye=null,Se=0,fc()),y}function GS(){for(;me!==null;)Q_(me)}function VS(e,n){var a=Le;Le|=2;var o=W_(),u=Y_();Ye!==e||Se!==n?(kc=null,Vc=dt()+500,Gr(e,n)):Br=ne(e,n);t:do try{if(Be!==0&&me!==null){n=me;var f=oi;e:switch(Be){case 1:Be=0,oi=null,Vr(e,n,f,1);break;case 2:case 9:if(sg(f)){Be=0,oi=null,Z_(n);break}n=function(){Be!==2&&Be!==9||Ye!==e||(Be=7),ji(e)},f.then(n,n);break t;case 3:Be=7;break t;case 4:Be=5;break t;case 7:sg(f)?(Be=0,oi=null,Z_(n)):(Be=0,oi=null,Vr(e,n,f,7));break;case 5:var y=null;switch(me.tag){case 26:y=me.memoizedState;case 5:case 27:var A=me;if(y?P0(y):A.stateNode.complete){Be=0,oi=null;var F=A.sibling;if(F!==null)me=F;else{var et=A.return;et!==null?(me=et,qc(et)):me=null}break e}}Be=0,oi=null,Vr(e,n,f,5);break;case 6:Be=0,oi=null,Vr(e,n,f,6);break;case 8:Lh(),rn=6;break t;default:throw Error(s(462))}}kS();break}catch(ht){j_(e,ht)}while(!0);return aa=Ns=null,B.H=o,B.A=u,Le=a,me!==null?0:(Ye=null,Se=0,fc(),rn)}function kS(){for(;me!==null&&!R();)Q_(me)}function Q_(e){var n=y_(e.alternate,e,pa);e.memoizedProps=e.pendingProps,n===null?qc(e):me=n}function Z_(e){var n=e,a=n.alternate;switch(n.tag){case 15:case 0:n=d_(a,n,n.pendingProps,n.type,void 0,Se);break;case 11:n=d_(a,n,n.pendingProps,n.type.render,n.ref,Se);break;case 5:Qf(n);default:S_(a,n),n=me=Ym(n,pa),n=y_(a,n,pa)}e.memoizedProps=e.pendingProps,n===null?qc(e):me=n}function Vr(e,n,a,o){aa=Ns=null,Qf(n),Ur=null,tl=0;var u=n.return;try{if(US(e,u,n,a,Se)){rn=1,Lc(e,_i(a,e.current)),me=null;return}}catch(f){if(u!==null)throw me=u,f;rn=1,Lc(e,_i(a,e.current)),me=null;return}n.flags&32768?(be||o===1?e=!0:Br||(Se&536870912)!==0?e=!1:(ka=e=!0,(o===2||o===9||o===3||o===6)&&(o=si.current,o!==null&&o.tag===13&&(o.flags|=16384))),K_(n,e)):qc(n)}function qc(e){var n=e;do{if((n.flags&32768)!==0){K_(n,ka);return}e=n.return;var a=OS(n.alternate,n,pa);if(a!==null){me=a;return}if(n=n.sibling,n!==null){me=n;return}me=n=e}while(n!==null);rn===0&&(rn=5)}function K_(e,n){do{var a=PS(e.alternate,e);if(a!==null){a.flags&=32767,me=a;return}if(a=e.return,a!==null&&(a.flags|=32768,a.subtreeFlags=0,a.deletions=null),!n&&(e=e.sibling,e!==null)){me=e;return}me=e=a}while(e!==null);rn=6,me=null}function J_(e,n,a,o,u,f,y,A,F){e.cancelPendingCommit=null;do Wc();while(yn!==0);if((Le&6)!==0)throw Error(s(327));if(n!==null){if(n===e.current)throw Error(s(177));if(f=n.lanes|n.childLanes,f|=Mf,Ci(e,a,f,y,A,F),e===Ye&&(me=Ye=null,Se=0),Hr=n,qa=e,ma=a,Dh=f,Uh=u,G_=o,(n.subtreeFlags&10256)!==0||(n.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,WS(Dt,function(){return i0(),null})):(e.callbackNode=null,e.callbackPriority=0),o=(n.flags&13878)!==0,(n.subtreeFlags&13878)!==0||o){o=B.T,B.T=null,u=$.p,$.p=2,y=Le,Le|=4;try{zS(e,n,a)}finally{Le=y,$.p=u,B.T=o}}yn=1,$_(),t0(),e0()}}function $_(){if(yn===1){yn=0;var e=qa,n=Hr,a=(n.flags&13878)!==0;if((n.subtreeFlags&13878)!==0||a){a=B.T,B.T=null;var o=$.p;$.p=2;var u=Le;Le|=4;try{L_(n,e);var f=qh,y=Fm(e.containerInfo),A=f.focusedElem,F=f.selectionRange;if(y!==A&&A&&A.ownerDocument&&Bm(A.ownerDocument.documentElement,A)){if(F!==null&&_f(A)){var et=F.start,ht=F.end;if(ht===void 0&&(ht=et),"selectionStart"in A)A.selectionStart=et,A.selectionEnd=Math.min(ht,A.value.length);else{var vt=A.ownerDocument||document,nt=vt&&vt.defaultView||window;if(nt.getSelection){var ct=nt.getSelection(),Ht=A.textContent.length,te=Math.min(F.start,Ht),Xe=F.end===void 0?te:Math.min(F.end,Ht);!ct.extend&&te>Xe&&(y=Xe,Xe=te,te=y);var Z=Im(A,te),X=Im(A,Xe);if(Z&&X&&(ct.rangeCount!==1||ct.anchorNode!==Z.node||ct.anchorOffset!==Z.offset||ct.focusNode!==X.node||ct.focusOffset!==X.offset)){var tt=vt.createRange();tt.setStart(Z.node,Z.offset),ct.removeAllRanges(),te>Xe?(ct.addRange(tt),ct.extend(X.node,X.offset)):(tt.setEnd(X.node,X.offset),ct.addRange(tt))}}}}for(vt=[],ct=A;ct=ct.parentNode;)ct.nodeType===1&&vt.push({element:ct,left:ct.scrollLeft,top:ct.scrollTop});for(typeof A.focus=="function"&&A.focus(),A=0;A<vt.length;A++){var pt=vt[A];pt.element.scrollLeft=pt.left,pt.element.scrollTop=pt.top}}su=!!jh,qh=jh=null}finally{Le=u,$.p=o,B.T=a}}e.current=n,yn=2}}function t0(){if(yn===2){yn=0;var e=qa,n=Hr,a=(n.flags&8772)!==0;if((n.subtreeFlags&8772)!==0||a){a=B.T,B.T=null;var o=$.p;$.p=2;var u=Le;Le|=4;try{C_(e,n.alternate,n)}finally{Le=u,$.p=o,B.T=a}}yn=3}}function e0(){if(yn===4||yn===3){yn=0,it();var e=qa,n=Hr,a=ma,o=G_;(n.subtreeFlags&10256)!==0||(n.flags&10256)!==0?yn=5:(yn=0,Hr=qa=null,n0(e,e.pendingLanes));var u=e.pendingLanes;if(u===0&&(ja=null),pr(a),n=n.stateNode,qt&&typeof qt.onCommitFiberRoot=="function")try{qt.onCommitFiberRoot(Qt,n,void 0,(n.current.flags&128)===128)}catch{}if(o!==null){n=B.T,u=$.p,$.p=2,B.T=null;try{for(var f=e.onRecoverableError,y=0;y<o.length;y++){var A=o[y];f(A.value,{componentStack:A.stack})}}finally{B.T=n,$.p=u}}(ma&3)!==0&&Wc(),ji(e),u=e.pendingLanes,(a&261930)!==0&&(u&42)!==0?e===Nh?_l++:(_l=0,Nh=e):_l=0,vl(0)}}function n0(e,n){(e.pooledCacheLanes&=n)===0&&(n=e.pooledCache,n!=null&&(e.pooledCache=null,Jo(n)))}function Wc(){return $_(),t0(),e0(),i0()}function i0(){if(yn!==5)return!1;var e=qa,n=Dh;Dh=0;var a=pr(ma),o=B.T,u=$.p;try{$.p=32>a?32:a,B.T=null,a=Uh,Uh=null;var f=qa,y=ma;if(yn=0,Hr=qa=null,ma=0,(Le&6)!==0)throw Error(s(331));var A=Le;if(Le|=4,B_(f.current),P_(f,f.current,y,a),Le=A,vl(0,!1),qt&&typeof qt.onPostCommitFiberRoot=="function")try{qt.onPostCommitFiberRoot(Qt,f)}catch{}return!0}finally{$.p=u,B.T=o,n0(e,n)}}function a0(e,n,a){n=_i(a,n),n=uh(e.stateNode,n,2),e=Fa(e,n,2),e!==null&&(An(e,2),ji(e))}function Fe(e,n,a){if(e.tag===3)a0(e,e,a);else for(;n!==null;){if(n.tag===3){a0(n,e,a);break}else if(n.tag===1){var o=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof o.componentDidCatch=="function"&&(ja===null||!ja.has(o))){e=_i(a,e),a=s_(2),o=Fa(n,a,2),o!==null&&(r_(a,o,n,e),An(o,2),ji(o));break}}n=n.return}}function Ph(e,n,a){var o=e.pingCache;if(o===null){o=e.pingCache=new FS;var u=new Set;o.set(n,u)}else u=o.get(n),u===void 0&&(u=new Set,o.set(n,u));u.has(a)||(Rh=!0,u.add(a),e=XS.bind(null,e,n,a),n.then(e,e))}function XS(e,n,a){var o=e.pingCache;o!==null&&o.delete(n),e.pingedLanes|=e.suspendedLanes&a,e.warmLanes&=~a,Ye===e&&(Se&a)===a&&(rn===4||rn===3&&(Se&62914560)===Se&&300>dt()-Gc?(Le&2)===0&&Gr(e,0):Ch|=a,Fr===Se&&(Fr=0)),ji(e)}function s0(e,n){n===0&&(n=_n()),e=ws(e,n),e!==null&&(An(e,n),ji(e))}function jS(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),s0(e,a)}function qS(e,n){var a=0;switch(e.tag){case 31:case 13:var o=e.stateNode,u=e.memoizedState;u!==null&&(a=u.retryLane);break;case 19:o=e.stateNode;break;case 22:o=e.stateNode._retryCache;break;default:throw Error(s(314))}o!==null&&o.delete(n),s0(e,a)}function WS(e,n){return Wt(e,n)}var Yc=null,kr=null,zh=!1,Qc=!1,Ih=!1,Ya=0;function ji(e){e!==kr&&e.next===null&&(kr===null?Yc=kr=e:kr=kr.next=e),Qc=!0,zh||(zh=!0,QS())}function vl(e,n){if(!Ih&&Qc){Ih=!0;do for(var a=!1,o=Yc;o!==null;){if(e!==0){var u=o.pendingLanes;if(u===0)var f=0;else{var y=o.suspendedLanes,A=o.pingedLanes;f=(1<<31-ee(42|e)+1)-1,f&=u&~(y&~A),f=f&201326741?f&201326741|1:f?f|2:0}f!==0&&(a=!0,c0(o,f))}else f=Se,f=Ut(o,o===Ye?f:0,o.cancelPendingCommit!==null||o.timeoutHandle!==-1),(f&3)===0||ne(o,f)||(a=!0,c0(o,f));o=o.next}while(a);Ih=!1}}function YS(){r0()}function r0(){Qc=zh=!1;var e=0;Ya!==0&&sM()&&(e=Ya);for(var n=dt(),a=null,o=Yc;o!==null;){var u=o.next,f=o0(o,n);f===0?(o.next=null,a===null?Yc=u:a.next=u,u===null&&(kr=a)):(a=o,(e!==0||(f&3)!==0)&&(Qc=!0)),o=u}yn!==0&&yn!==5||vl(e),Ya!==0&&(Ya=0)}function o0(e,n){for(var a=e.suspendedLanes,o=e.pingedLanes,u=e.expirationTimes,f=e.pendingLanes&-62914561;0<f;){var y=31-ee(f),A=1<<y,F=u[y];F===-1?((A&a)===0||(A&o)!==0)&&(u[y]=tn(A,n)):F<=n&&(e.expiredLanes|=A),f&=~A}if(n=Ye,a=Se,a=Ut(e,e===n?a:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o=e.callbackNode,a===0||e===n&&(Be===2||Be===9)||e.cancelPendingCommit!==null)return o!==null&&o!==null&&O(o),e.callbackNode=null,e.callbackPriority=0;if((a&3)===0||ne(e,a)){if(n=a&-a,n===e.callbackPriority)return n;switch(o!==null&&O(o),pr(a)){case 2:case 8:a=jt;break;case 32:a=Dt;break;case 268435456:a=ye;break;default:a=Dt}return o=l0.bind(null,e),a=Wt(a,o),e.callbackPriority=n,e.callbackNode=a,n}return o!==null&&o!==null&&O(o),e.callbackPriority=2,e.callbackNode=null,2}function l0(e,n){if(yn!==0&&yn!==5)return e.callbackNode=null,e.callbackPriority=0,null;var a=e.callbackNode;if(Wc()&&e.callbackNode!==a)return null;var o=Se;return o=Ut(e,e===Ye?o:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o===0?null:(k_(e,o,n),o0(e,dt()),e.callbackNode!=null&&e.callbackNode===a?l0.bind(null,e):null)}function c0(e,n){if(Wc())return null;k_(e,n,!0)}function QS(){oM(function(){(Le&6)!==0?Wt(_t,YS):r0()})}function Bh(){if(Ya===0){var e=Cr;e===0&&(e=Ct,Ct<<=1,(Ct&261888)===0&&(Ct=256)),Ya=e}return Ya}function u0(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:ic(""+e)}function f0(e,n){var a=n.ownerDocument.createElement("input");return a.name=n.name,a.value=n.value,e.id&&a.setAttribute("form",e.id),n.parentNode.insertBefore(a,n),e=new FormData(e),a.parentNode.removeChild(a),e}function ZS(e,n,a,o,u){if(n==="submit"&&a&&a.stateNode===u){var f=u0((u[Rn]||null).action),y=o.submitter;y&&(n=(n=y[Rn]||null)?u0(n.formAction):y.getAttribute("formAction"),n!==null&&(f=n,y=null));var A=new oc("action","action",null,o,u);e.push({event:A,listeners:[{instance:null,listener:function(){if(o.defaultPrevented){if(Ya!==0){var F=y?f0(u,y):new FormData(u);ah(a,{pending:!0,data:F,method:u.method,action:f},null,F)}}else typeof f=="function"&&(A.preventDefault(),F=y?f0(u,y):new FormData(u),ah(a,{pending:!0,data:F,method:u.method,action:f},f,F))},currentTarget:u}]})}}for(var Fh=0;Fh<Sf.length;Fh++){var Hh=Sf[Fh],KS=Hh.toLowerCase(),JS=Hh[0].toUpperCase()+Hh.slice(1);Di(KS,"on"+JS)}Di(Vm,"onAnimationEnd"),Di(km,"onAnimationIteration"),Di(Xm,"onAnimationStart"),Di("dblclick","onDoubleClick"),Di("focusin","onFocus"),Di("focusout","onBlur"),Di(pS,"onTransitionRun"),Di(mS,"onTransitionStart"),Di(gS,"onTransitionCancel"),Di(jm,"onTransitionEnd"),Jt("onMouseEnter",["mouseout","mouseover"]),Jt("onMouseLeave",["mouseout","mouseover"]),Jt("onPointerEnter",["pointerout","pointerover"]),Jt("onPointerLeave",["pointerout","pointerover"]),Pt("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),Pt("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),Pt("onBeforeInput",["compositionend","keypress","textInput","paste"]),Pt("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var yl="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),$S=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(yl));function h0(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var o=e[a],u=o.event;o=o.listeners;t:{var f=void 0;if(n)for(var y=o.length-1;0<=y;y--){var A=o[y],F=A.instance,et=A.currentTarget;if(A=A.listener,F!==f&&u.isPropagationStopped())break t;f=A,u.currentTarget=et;try{f(u)}catch(ht){uc(ht)}u.currentTarget=null,f=F}else for(y=0;y<o.length;y++){if(A=o[y],F=A.instance,et=A.currentTarget,A=A.listener,F!==f&&u.isPropagationStopped())break t;f=A,u.currentTarget=et;try{f(u)}catch(ht){uc(ht)}u.currentTarget=null,f=F}}}}function ge(e,n){var a=n[Ho];a===void 0&&(a=n[Ho]=new Set);var o=e+"__bubble";a.has(o)||(d0(n,e,2,!1),a.add(o))}function Gh(e,n,a){var o=0;n&&(o|=4),d0(a,e,o,n)}var Zc="_reactListening"+Math.random().toString(36).slice(2);function Vh(e){if(!e[Zc]){e[Zc]=!0,Nt.forEach(function(a){a!=="selectionchange"&&($S.has(a)||Gh(a,!1,e),Gh(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[Zc]||(n[Zc]=!0,Gh("selectionchange",!1,n))}}function d0(e,n,a,o){switch(V0(n)){case 2:var u=RM;break;case 8:u=CM;break;default:u=id}a=u.bind(null,n,a,e),u=void 0,!lf||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(u=!0),o?u!==void 0?e.addEventListener(n,a,{capture:!0,passive:u}):e.addEventListener(n,a,!0):u!==void 0?e.addEventListener(n,a,{passive:u}):e.addEventListener(n,a,!1)}function kh(e,n,a,o,u){var f=o;if((n&1)===0&&(n&2)===0&&o!==null)t:for(;;){if(o===null)return;var y=o.tag;if(y===3||y===4){var A=o.stateNode.containerInfo;if(A===u)break;if(y===4)for(y=o.return;y!==null;){var F=y.tag;if((F===3||F===4)&&y.stateNode.containerInfo===u)return;y=y.return}for(;A!==null;){if(y=W(A),y===null)return;if(F=y.tag,F===5||F===6||F===26||F===27){o=f=y;continue t}A=A.parentNode}}o=o.return}vm(function(){var et=f,ht=rf(a),vt=[];t:{var nt=qm.get(e);if(nt!==void 0){var ct=oc,Ht=e;switch(e){case"keypress":if(sc(a)===0)break t;case"keydown":case"keyup":ct=qx;break;case"focusin":Ht="focus",ct=hf;break;case"focusout":Ht="blur",ct=hf;break;case"beforeblur":case"afterblur":ct=hf;break;case"click":if(a.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":ct=Sm;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":ct=Ox;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":ct=Qx;break;case Vm:case km:case Xm:ct=Ix;break;case jm:ct=Kx;break;case"scroll":case"scrollend":ct=Nx;break;case"wheel":ct=$x;break;case"copy":case"cut":case"paste":ct=Fx;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":ct=Em;break;case"toggle":case"beforetoggle":ct=eS}var te=(n&4)!==0,Xe=!te&&(e==="scroll"||e==="scrollend"),Z=te?nt!==null?nt+"Capture":null:nt;te=[];for(var X=et,tt;X!==null;){var pt=X;if(tt=pt.stateNode,pt=pt.tag,pt!==5&&pt!==26&&pt!==27||tt===null||Z===null||(pt=Go(X,Z),pt!=null&&te.push(xl(X,pt,tt))),Xe)break;X=X.return}0<te.length&&(nt=new ct(nt,Ht,null,a,ht),vt.push({event:nt,listeners:te}))}}if((n&7)===0){t:{if(nt=e==="mouseover"||e==="pointerover",ct=e==="mouseout"||e==="pointerout",nt&&a!==sf&&(Ht=a.relatedTarget||a.fromElement)&&(W(Ht)||Ht[Ji]))break t;if((ct||nt)&&(nt=ht.window===ht?ht:(nt=ht.ownerDocument)?nt.defaultView||nt.parentWindow:window,ct?(Ht=a.relatedTarget||a.toElement,ct=et,Ht=Ht?W(Ht):null,Ht!==null&&(Xe=c(Ht),te=Ht.tag,Ht!==Xe||te!==5&&te!==27&&te!==6)&&(Ht=null)):(ct=null,Ht=et),ct!==Ht)){if(te=Sm,pt="onMouseLeave",Z="onMouseEnter",X="mouse",(e==="pointerout"||e==="pointerover")&&(te=Em,pt="onPointerLeave",Z="onPointerEnter",X="pointer"),Xe=ct==null?nt:rt(ct),tt=Ht==null?nt:rt(Ht),nt=new te(pt,X+"leave",ct,a,ht),nt.target=Xe,nt.relatedTarget=tt,pt=null,W(ht)===et&&(te=new te(Z,X+"enter",Ht,a,ht),te.target=tt,te.relatedTarget=Xe,pt=te),Xe=pt,ct&&Ht)e:{for(te=tM,Z=ct,X=Ht,tt=0,pt=Z;pt;pt=te(pt))tt++;pt=0;for(var Kt=X;Kt;Kt=te(Kt))pt++;for(;0<tt-pt;)Z=te(Z),tt--;for(;0<pt-tt;)X=te(X),pt--;for(;tt--;){if(Z===X||X!==null&&Z===X.alternate){te=Z;break e}Z=te(Z),X=te(X)}te=null}else te=null;ct!==null&&p0(vt,nt,ct,te,!1),Ht!==null&&Xe!==null&&p0(vt,Xe,Ht,te,!0)}}t:{if(nt=et?rt(et):window,ct=nt.nodeName&&nt.nodeName.toLowerCase(),ct==="select"||ct==="input"&&nt.type==="file")var De=Um;else if(wm(nt))if(Nm)De=fS;else{De=cS;var Xt=lS}else ct=nt.nodeName,!ct||ct.toLowerCase()!=="input"||nt.type!=="checkbox"&&nt.type!=="radio"?et&&af(et.elementType)&&(De=Um):De=uS;if(De&&(De=De(e,et))){Dm(vt,De,a,ht);break t}Xt&&Xt(e,nt,et),e==="focusout"&&et&&nt.type==="number"&&et.memoizedProps.value!=null&&vn(nt,"number",nt.value)}switch(Xt=et?rt(et):window,e){case"focusin":(wm(Xt)||Xt.contentEditable==="true")&&(xr=Xt,vf=et,Qo=null);break;case"focusout":Qo=vf=xr=null;break;case"mousedown":yf=!0;break;case"contextmenu":case"mouseup":case"dragend":yf=!1,Hm(vt,a,ht);break;case"selectionchange":if(dS)break;case"keydown":case"keyup":Hm(vt,a,ht)}var ce;if(pf)t:{switch(e){case"compositionstart":var Me="onCompositionStart";break t;case"compositionend":Me="onCompositionEnd";break t;case"compositionupdate":Me="onCompositionUpdate";break t}Me=void 0}else yr?Rm(e,a)&&(Me="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(Me="onCompositionStart");Me&&(bm&&a.locale!=="ko"&&(yr||Me!=="onCompositionStart"?Me==="onCompositionEnd"&&yr&&(ce=ym()):(Na=ht,cf="value"in Na?Na.value:Na.textContent,yr=!0)),Xt=Kc(et,Me),0<Xt.length&&(Me=new Mm(Me,e,null,a,ht),vt.push({event:Me,listeners:Xt}),ce?Me.data=ce:(ce=Cm(a),ce!==null&&(Me.data=ce)))),(ce=iS?aS(e,a):sS(e,a))&&(Me=Kc(et,"onBeforeInput"),0<Me.length&&(Xt=new Mm("onBeforeInput","beforeinput",null,a,ht),vt.push({event:Xt,listeners:Me}),Xt.data=ce)),ZS(vt,e,et,a,ht)}h0(vt,n)})}function xl(e,n,a){return{instance:e,listener:n,currentTarget:a}}function Kc(e,n){for(var a=n+"Capture",o=[];e!==null;){var u=e,f=u.stateNode;if(u=u.tag,u!==5&&u!==26&&u!==27||f===null||(u=Go(e,a),u!=null&&o.unshift(xl(e,u,f)),u=Go(e,n),u!=null&&o.push(xl(e,u,f))),e.tag===3)return o;e=e.return}return[]}function tM(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function p0(e,n,a,o,u){for(var f=n._reactName,y=[];a!==null&&a!==o;){var A=a,F=A.alternate,et=A.stateNode;if(A=A.tag,F!==null&&F===o)break;A!==5&&A!==26&&A!==27||et===null||(F=et,u?(et=Go(a,f),et!=null&&y.unshift(xl(a,et,F))):u||(et=Go(a,f),et!=null&&y.push(xl(a,et,F)))),a=a.return}y.length!==0&&e.push({event:n,listeners:y})}var eM=/\r\n?/g,nM=/\u0000|\uFFFD/g;function m0(e){return(typeof e=="string"?e:""+e).replace(eM,`
`).replace(nM,"")}function g0(e,n){return n=m0(n),m0(e)===n}function ke(e,n,a,o,u,f){switch(a){case"children":typeof o=="string"?n==="body"||n==="textarea"&&o===""||gr(e,o):(typeof o=="number"||typeof o=="bigint")&&n!=="body"&&gr(e,""+o);break;case"className":We(e,"class",o);break;case"tabIndex":We(e,"tabindex",o);break;case"dir":case"role":case"viewBox":case"width":case"height":We(e,a,o);break;case"style":gm(e,o,f);break;case"data":if(n!=="object"){We(e,"data",o);break}case"src":case"href":if(o===""&&(n!=="a"||a!=="href")){e.removeAttribute(a);break}if(o==null||typeof o=="function"||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(a);break}o=ic(""+o),e.setAttribute(a,o);break;case"action":case"formAction":if(typeof o=="function"){e.setAttribute(a,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof f=="function"&&(a==="formAction"?(n!=="input"&&ke(e,n,"name",u.name,u,null),ke(e,n,"formEncType",u.formEncType,u,null),ke(e,n,"formMethod",u.formMethod,u,null),ke(e,n,"formTarget",u.formTarget,u,null)):(ke(e,n,"encType",u.encType,u,null),ke(e,n,"method",u.method,u,null),ke(e,n,"target",u.target,u,null)));if(o==null||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(a);break}o=ic(""+o),e.setAttribute(a,o);break;case"onClick":o!=null&&(e.onclick=ta);break;case"onScroll":o!=null&&ge("scroll",e);break;case"onScrollEnd":o!=null&&ge("scrollend",e);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(s(61));if(a=o.__html,a!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=a}}break;case"multiple":e.multiple=o&&typeof o!="function"&&typeof o!="symbol";break;case"muted":e.muted=o&&typeof o!="function"&&typeof o!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(o==null||typeof o=="function"||typeof o=="boolean"||typeof o=="symbol"){e.removeAttribute("xlink:href");break}a=ic(""+o),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",a);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,""+o):e.removeAttribute(a);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":o&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,""):e.removeAttribute(a);break;case"capture":case"download":o===!0?e.setAttribute(a,""):o!==!1&&o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,o):e.removeAttribute(a);break;case"cols":case"rows":case"size":case"span":o!=null&&typeof o!="function"&&typeof o!="symbol"&&!isNaN(o)&&1<=o?e.setAttribute(a,o):e.removeAttribute(a);break;case"rowSpan":case"start":o==null||typeof o=="function"||typeof o=="symbol"||isNaN(o)?e.removeAttribute(a):e.setAttribute(a,o);break;case"popover":ge("beforetoggle",e),ge("toggle",e),Qe(e,"popover",o);break;case"xlinkActuate":oe(e,"http://www.w3.org/1999/xlink","xlink:actuate",o);break;case"xlinkArcrole":oe(e,"http://www.w3.org/1999/xlink","xlink:arcrole",o);break;case"xlinkRole":oe(e,"http://www.w3.org/1999/xlink","xlink:role",o);break;case"xlinkShow":oe(e,"http://www.w3.org/1999/xlink","xlink:show",o);break;case"xlinkTitle":oe(e,"http://www.w3.org/1999/xlink","xlink:title",o);break;case"xlinkType":oe(e,"http://www.w3.org/1999/xlink","xlink:type",o);break;case"xmlBase":oe(e,"http://www.w3.org/XML/1998/namespace","xml:base",o);break;case"xmlLang":oe(e,"http://www.w3.org/XML/1998/namespace","xml:lang",o);break;case"xmlSpace":oe(e,"http://www.w3.org/XML/1998/namespace","xml:space",o);break;case"is":Qe(e,"is",o);break;case"innerText":case"textContent":break;default:(!(2<a.length)||a[0]!=="o"&&a[0]!=="O"||a[1]!=="n"&&a[1]!=="N")&&(a=Dx.get(a)||a,Qe(e,a,o))}}function Xh(e,n,a,o,u,f){switch(a){case"style":gm(e,o,f);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(s(61));if(a=o.__html,a!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=a}}break;case"children":typeof o=="string"?gr(e,o):(typeof o=="number"||typeof o=="bigint")&&gr(e,""+o);break;case"onScroll":o!=null&&ge("scroll",e);break;case"onScrollEnd":o!=null&&ge("scrollend",e);break;case"onClick":o!=null&&(e.onclick=ta);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!It.hasOwnProperty(a))t:{if(a[0]==="o"&&a[1]==="n"&&(u=a.endsWith("Capture"),n=a.slice(2,u?a.length-7:void 0),f=e[Rn]||null,f=f!=null?f[a]:null,typeof f=="function"&&e.removeEventListener(n,f,u),typeof o=="function")){typeof f!="function"&&f!==null&&(a in e?e[a]=null:e.hasAttribute(a)&&e.removeAttribute(a)),e.addEventListener(n,o,u);break t}a in e?e[a]=o:o===!0?e.setAttribute(a,""):Qe(e,a,o)}}}function Un(e,n,a){switch(n){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":ge("error",e),ge("load",e);var o=!1,u=!1,f;for(f in a)if(a.hasOwnProperty(f)){var y=a[f];if(y!=null)switch(f){case"src":o=!0;break;case"srcSet":u=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(s(137,n));default:ke(e,n,f,y,a,null)}}u&&ke(e,n,"srcSet",a.srcSet,a,null),o&&ke(e,n,"src",a.src,a,null);return;case"input":ge("invalid",e);var A=f=y=u=null,F=null,et=null;for(o in a)if(a.hasOwnProperty(o)){var ht=a[o];if(ht!=null)switch(o){case"name":u=ht;break;case"type":y=ht;break;case"checked":F=ht;break;case"defaultChecked":et=ht;break;case"value":f=ht;break;case"defaultValue":A=ht;break;case"children":case"dangerouslySetInnerHTML":if(ht!=null)throw Error(s(137,n));break;default:ke(e,n,o,ht,a,null)}}Gn(e,f,A,F,et,y,u,!1);return;case"select":ge("invalid",e),o=y=f=null;for(u in a)if(a.hasOwnProperty(u)&&(A=a[u],A!=null))switch(u){case"value":f=A;break;case"defaultValue":y=A;break;case"multiple":o=A;default:ke(e,n,u,A,a,null)}n=f,a=y,e.multiple=!!o,n!=null?ln(e,!!o,n,!1):a!=null&&ln(e,!!o,a,!0);return;case"textarea":ge("invalid",e),f=u=o=null;for(y in a)if(a.hasOwnProperty(y)&&(A=a[y],A!=null))switch(y){case"value":o=A;break;case"defaultValue":u=A;break;case"children":f=A;break;case"dangerouslySetInnerHTML":if(A!=null)throw Error(s(91));break;default:ke(e,n,y,A,a,null)}Gi(e,o,u,f);return;case"option":for(F in a)if(a.hasOwnProperty(F)&&(o=a[F],o!=null))switch(F){case"selected":e.selected=o&&typeof o!="function"&&typeof o!="symbol";break;default:ke(e,n,F,o,a,null)}return;case"dialog":ge("beforetoggle",e),ge("toggle",e),ge("cancel",e),ge("close",e);break;case"iframe":case"object":ge("load",e);break;case"video":case"audio":for(o=0;o<yl.length;o++)ge(yl[o],e);break;case"image":ge("error",e),ge("load",e);break;case"details":ge("toggle",e);break;case"embed":case"source":case"link":ge("error",e),ge("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in a)if(a.hasOwnProperty(et)&&(o=a[et],o!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(s(137,n));default:ke(e,n,et,o,a,null)}return;default:if(af(n)){for(ht in a)a.hasOwnProperty(ht)&&(o=a[ht],o!==void 0&&Xh(e,n,ht,o,a,void 0));return}}for(A in a)a.hasOwnProperty(A)&&(o=a[A],o!=null&&ke(e,n,A,o,a,null))}function iM(e,n,a,o){switch(n){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var u=null,f=null,y=null,A=null,F=null,et=null,ht=null;for(ct in a){var vt=a[ct];if(a.hasOwnProperty(ct)&&vt!=null)switch(ct){case"checked":break;case"value":break;case"defaultValue":F=vt;default:o.hasOwnProperty(ct)||ke(e,n,ct,null,o,vt)}}for(var nt in o){var ct=o[nt];if(vt=a[nt],o.hasOwnProperty(nt)&&(ct!=null||vt!=null))switch(nt){case"type":f=ct;break;case"name":u=ct;break;case"checked":et=ct;break;case"defaultChecked":ht=ct;break;case"value":y=ct;break;case"defaultValue":A=ct;break;case"children":case"dangerouslySetInnerHTML":if(ct!=null)throw Error(s(137,n));break;default:ct!==vt&&ke(e,n,nt,ct,o,vt)}}Pn(e,y,A,F,et,ht,f,u);return;case"select":ct=y=A=nt=null;for(f in a)if(F=a[f],a.hasOwnProperty(f)&&F!=null)switch(f){case"value":break;case"multiple":ct=F;default:o.hasOwnProperty(f)||ke(e,n,f,null,o,F)}for(u in o)if(f=o[u],F=a[u],o.hasOwnProperty(u)&&(f!=null||F!=null))switch(u){case"value":nt=f;break;case"defaultValue":A=f;break;case"multiple":y=f;default:f!==F&&ke(e,n,u,f,o,F)}n=A,a=y,o=ct,nt!=null?ln(e,!!a,nt,!1):!!o!=!!a&&(n!=null?ln(e,!!a,n,!0):ln(e,!!a,a?[]:"",!1));return;case"textarea":ct=nt=null;for(A in a)if(u=a[A],a.hasOwnProperty(A)&&u!=null&&!o.hasOwnProperty(A))switch(A){case"value":break;case"children":break;default:ke(e,n,A,null,o,u)}for(y in o)if(u=o[y],f=a[y],o.hasOwnProperty(y)&&(u!=null||f!=null))switch(y){case"value":nt=u;break;case"defaultValue":ct=u;break;case"children":break;case"dangerouslySetInnerHTML":if(u!=null)throw Error(s(91));break;default:u!==f&&ke(e,n,y,u,o,f)}mr(e,nt,ct);return;case"option":for(var Ht in a)if(nt=a[Ht],a.hasOwnProperty(Ht)&&nt!=null&&!o.hasOwnProperty(Ht))switch(Ht){case"selected":e.selected=!1;break;default:ke(e,n,Ht,null,o,nt)}for(F in o)if(nt=o[F],ct=a[F],o.hasOwnProperty(F)&&nt!==ct&&(nt!=null||ct!=null))switch(F){case"selected":e.selected=nt&&typeof nt!="function"&&typeof nt!="symbol";break;default:ke(e,n,F,nt,o,ct)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var te in a)nt=a[te],a.hasOwnProperty(te)&&nt!=null&&!o.hasOwnProperty(te)&&ke(e,n,te,null,o,nt);for(et in o)if(nt=o[et],ct=a[et],o.hasOwnProperty(et)&&nt!==ct&&(nt!=null||ct!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(nt!=null)throw Error(s(137,n));break;default:ke(e,n,et,nt,o,ct)}return;default:if(af(n)){for(var Xe in a)nt=a[Xe],a.hasOwnProperty(Xe)&&nt!==void 0&&!o.hasOwnProperty(Xe)&&Xh(e,n,Xe,void 0,o,nt);for(ht in o)nt=o[ht],ct=a[ht],!o.hasOwnProperty(ht)||nt===ct||nt===void 0&&ct===void 0||Xh(e,n,ht,nt,o,ct);return}}for(var Z in a)nt=a[Z],a.hasOwnProperty(Z)&&nt!=null&&!o.hasOwnProperty(Z)&&ke(e,n,Z,null,o,nt);for(vt in o)nt=o[vt],ct=a[vt],!o.hasOwnProperty(vt)||nt===ct||nt==null&&ct==null||ke(e,n,vt,nt,o,ct)}function _0(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function aM(){if(typeof performance.getEntriesByType=="function"){for(var e=0,n=0,a=performance.getEntriesByType("resource"),o=0;o<a.length;o++){var u=a[o],f=u.transferSize,y=u.initiatorType,A=u.duration;if(f&&A&&_0(y)){for(y=0,A=u.responseEnd,o+=1;o<a.length;o++){var F=a[o],et=F.startTime;if(et>A)break;var ht=F.transferSize,vt=F.initiatorType;ht&&_0(vt)&&(F=F.responseEnd,y+=ht*(F<A?1:(A-et)/(F-et)))}if(--o,n+=8*(f+y)/(u.duration/1e3),e++,10<e)break}}if(0<e)return n/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var jh=null,qh=null;function Jc(e){return e.nodeType===9?e:e.ownerDocument}function v0(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function y0(e,n){if(e===0)switch(n){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&n==="foreignObject"?0:e}function Wh(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.children=="bigint"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Yh=null;function sM(){var e=window.event;return e&&e.type==="popstate"?e===Yh?!1:(Yh=e,!0):(Yh=null,!1)}var x0=typeof setTimeout=="function"?setTimeout:void 0,rM=typeof clearTimeout=="function"?clearTimeout:void 0,S0=typeof Promise=="function"?Promise:void 0,oM=typeof queueMicrotask=="function"?queueMicrotask:typeof S0<"u"?function(e){return S0.resolve(null).then(e).catch(lM)}:x0;function lM(e){setTimeout(function(){throw e})}function Qa(e){return e==="head"}function M0(e,n){var a=n,o=0;do{var u=a.nextSibling;if(e.removeChild(a),u&&u.nodeType===8)if(a=u.data,a==="/$"||a==="/&"){if(o===0){e.removeChild(u),Wr(n);return}o--}else if(a==="$"||a==="$?"||a==="$~"||a==="$!"||a==="&")o++;else if(a==="html")Sl(e.ownerDocument.documentElement);else if(a==="head"){a=e.ownerDocument.head,Sl(a);for(var f=a.firstChild;f;){var y=f.nextSibling,A=f.nodeName;f[bs]||A==="SCRIPT"||A==="STYLE"||A==="LINK"&&f.rel.toLowerCase()==="stylesheet"||a.removeChild(f),f=y}}else a==="body"&&Sl(e.ownerDocument.body);a=u}while(a);Wr(n)}function E0(e,n){var a=e;e=0;do{var o=a.nextSibling;if(a.nodeType===1?n?(a._stashedDisplay=a.style.display,a.style.display="none"):(a.style.display=a._stashedDisplay||"",a.getAttribute("style")===""&&a.removeAttribute("style")):a.nodeType===3&&(n?(a._stashedText=a.nodeValue,a.nodeValue=""):a.nodeValue=a._stashedText||""),o&&o.nodeType===8)if(a=o.data,a==="/$"){if(e===0)break;e--}else a!=="$"&&a!=="$?"&&a!=="$~"&&a!=="$!"||e++;a=o}while(a)}function Qh(e){var n=e.firstChild;for(n&&n.nodeType===10&&(n=n.nextSibling);n;){var a=n;switch(n=n.nextSibling,a.nodeName){case"HTML":case"HEAD":case"BODY":Qh(a),w(a);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(a.rel.toLowerCase()==="stylesheet")continue}e.removeChild(a)}}function cM(e,n,a,o){for(;e.nodeType===1;){var u=a;if(e.nodeName.toLowerCase()!==n.toLowerCase()){if(!o&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(o){if(!e[bs])switch(n){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(f=e.getAttribute("rel"),f==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(f!==u.rel||e.getAttribute("href")!==(u.href==null||u.href===""?null:u.href)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin)||e.getAttribute("title")!==(u.title==null?null:u.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(f=e.getAttribute("src"),(f!==(u.src==null?null:u.src)||e.getAttribute("type")!==(u.type==null?null:u.type)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin))&&f&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(n==="input"&&e.type==="hidden"){var f=u.name==null?null:""+u.name;if(u.type==="hidden"&&e.getAttribute("name")===f)return e}else return e;if(e=Mi(e.nextSibling),e===null)break}return null}function uM(e,n,a){if(n==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!a||(e=Mi(e.nextSibling),e===null))return null;return e}function b0(e,n){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!n||(e=Mi(e.nextSibling),e===null))return null;return e}function Zh(e){return e.data==="$?"||e.data==="$~"}function Kh(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function fM(e,n){var a=e.ownerDocument;if(e.data==="$~")e._reactRetry=n;else if(e.data!=="$?"||a.readyState!=="loading")n();else{var o=function(){n(),a.removeEventListener("DOMContentLoaded",o)};a.addEventListener("DOMContentLoaded",o),e._reactRetry=o}}function Mi(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?"||n==="$~"||n==="&"||n==="F!"||n==="F")break;if(n==="/$"||n==="/&")return null}}return e}var Jh=null;function T0(e){e=e.nextSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"||a==="/&"){if(n===0)return Mi(e.nextSibling);n--}else a!=="$"&&a!=="$!"&&a!=="$?"&&a!=="$~"&&a!=="&"||n++}e=e.nextSibling}return null}function A0(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"||a==="$~"||a==="&"){if(n===0)return e;n--}else a!=="/$"&&a!=="/&"||n++}e=e.previousSibling}return null}function R0(e,n,a){switch(n=Jc(a),e){case"html":if(e=n.documentElement,!e)throw Error(s(452));return e;case"head":if(e=n.head,!e)throw Error(s(453));return e;case"body":if(e=n.body,!e)throw Error(s(454));return e;default:throw Error(s(451))}}function Sl(e){for(var n=e.attributes;n.length;)e.removeAttributeNode(n[0]);w(e)}var Ei=new Map,C0=new Set;function $c(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var ga=$.d;$.d={f:hM,r:dM,D:pM,C:mM,L:gM,m:_M,X:yM,S:vM,M:xM};function hM(){var e=ga.f(),n=Xc();return e||n}function dM(e){var n=st(e);n!==null&&n.tag===5&&n.type==="form"?jg(n):ga.r(e)}var Xr=typeof document>"u"?null:document;function w0(e,n,a){var o=Xr;if(o&&typeof n=="string"&&n){var u=pe(n);u='link[rel="'+e+'"][href="'+u+'"]',typeof a=="string"&&(u+='[crossorigin="'+a+'"]'),C0.has(u)||(C0.add(u),e={rel:e,crossOrigin:a,href:n},o.querySelector(u)===null&&(n=o.createElement("link"),Un(n,"link",e),xt(n),o.head.appendChild(n)))}}function pM(e){ga.D(e),w0("dns-prefetch",e,null)}function mM(e,n){ga.C(e,n),w0("preconnect",e,n)}function gM(e,n,a){ga.L(e,n,a);var o=Xr;if(o&&e&&n){var u='link[rel="preload"][as="'+pe(n)+'"]';n==="image"&&a&&a.imageSrcSet?(u+='[imagesrcset="'+pe(a.imageSrcSet)+'"]',typeof a.imageSizes=="string"&&(u+='[imagesizes="'+pe(a.imageSizes)+'"]')):u+='[href="'+pe(e)+'"]';var f=u;switch(n){case"style":f=jr(e);break;case"script":f=qr(e)}Ei.has(f)||(e=_({rel:"preload",href:n==="image"&&a&&a.imageSrcSet?void 0:e,as:n},a),Ei.set(f,e),o.querySelector(u)!==null||n==="style"&&o.querySelector(Ml(f))||n==="script"&&o.querySelector(El(f))||(n=o.createElement("link"),Un(n,"link",e),xt(n),o.head.appendChild(n)))}}function _M(e,n){ga.m(e,n);var a=Xr;if(a&&e){var o=n&&typeof n.as=="string"?n.as:"script",u='link[rel="modulepreload"][as="'+pe(o)+'"][href="'+pe(e)+'"]',f=u;switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":f=qr(e)}if(!Ei.has(f)&&(e=_({rel:"modulepreload",href:e},n),Ei.set(f,e),a.querySelector(u)===null)){switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(a.querySelector(El(f)))return}o=a.createElement("link"),Un(o,"link",e),xt(o),a.head.appendChild(o)}}}function vM(e,n,a){ga.S(e,n,a);var o=Xr;if(o&&e){var u=Q(o).hoistableStyles,f=jr(e);n=n||"default";var y=u.get(f);if(!y){var A={loading:0,preload:null};if(y=o.querySelector(Ml(f)))A.loading=5;else{e=_({rel:"stylesheet",href:e,"data-precedence":n},a),(a=Ei.get(f))&&$h(e,a);var F=y=o.createElement("link");xt(F),Un(F,"link",e),F._p=new Promise(function(et,ht){F.onload=et,F.onerror=ht}),F.addEventListener("load",function(){A.loading|=1}),F.addEventListener("error",function(){A.loading|=2}),A.loading|=4,tu(y,n,o)}y={type:"stylesheet",instance:y,count:1,state:A},u.set(f,y)}}}function yM(e,n){ga.X(e,n);var a=Xr;if(a&&e){var o=Q(a).hoistableScripts,u=qr(e),f=o.get(u);f||(f=a.querySelector(El(u)),f||(e=_({src:e,async:!0},n),(n=Ei.get(u))&&td(e,n),f=a.createElement("script"),xt(f),Un(f,"link",e),a.head.appendChild(f)),f={type:"script",instance:f,count:1,state:null},o.set(u,f))}}function xM(e,n){ga.M(e,n);var a=Xr;if(a&&e){var o=Q(a).hoistableScripts,u=qr(e),f=o.get(u);f||(f=a.querySelector(El(u)),f||(e=_({src:e,async:!0,type:"module"},n),(n=Ei.get(u))&&td(e,n),f=a.createElement("script"),xt(f),Un(f,"link",e),a.head.appendChild(f)),f={type:"script",instance:f,count:1,state:null},o.set(u,f))}}function D0(e,n,a,o){var u=(u=Tt.current)?$c(u):null;if(!u)throw Error(s(446));switch(e){case"meta":case"title":return null;case"style":return typeof a.precedence=="string"&&typeof a.href=="string"?(n=jr(a.href),a=Q(u).hoistableStyles,o=a.get(n),o||(o={type:"style",instance:null,count:0,state:null},a.set(n,o)),o):{type:"void",instance:null,count:0,state:null};case"link":if(a.rel==="stylesheet"&&typeof a.href=="string"&&typeof a.precedence=="string"){e=jr(a.href);var f=Q(u).hoistableStyles,y=f.get(e);if(y||(u=u.ownerDocument||u,y={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},f.set(e,y),(f=u.querySelector(Ml(e)))&&!f._p&&(y.instance=f,y.state.loading=5),Ei.has(e)||(a={rel:"preload",as:"style",href:a.href,crossOrigin:a.crossOrigin,integrity:a.integrity,media:a.media,hrefLang:a.hrefLang,referrerPolicy:a.referrerPolicy},Ei.set(e,a),f||SM(u,e,a,y.state))),n&&o===null)throw Error(s(528,""));return y}if(n&&o!==null)throw Error(s(529,""));return null;case"script":return n=a.async,a=a.src,typeof a=="string"&&n&&typeof n!="function"&&typeof n!="symbol"?(n=qr(a),a=Q(u).hoistableScripts,o=a.get(n),o||(o={type:"script",instance:null,count:0,state:null},a.set(n,o)),o):{type:"void",instance:null,count:0,state:null};default:throw Error(s(444,e))}}function jr(e){return'href="'+pe(e)+'"'}function Ml(e){return'link[rel="stylesheet"]['+e+"]"}function U0(e){return _({},e,{"data-precedence":e.precedence,precedence:null})}function SM(e,n,a,o){e.querySelector('link[rel="preload"][as="style"]['+n+"]")?o.loading=1:(n=e.createElement("link"),o.preload=n,n.addEventListener("load",function(){return o.loading|=1}),n.addEventListener("error",function(){return o.loading|=2}),Un(n,"link",a),xt(n),e.head.appendChild(n))}function qr(e){return'[src="'+pe(e)+'"]'}function El(e){return"script[async]"+e}function N0(e,n,a){if(n.count++,n.instance===null)switch(n.type){case"style":var o=e.querySelector('style[data-href~="'+pe(a.href)+'"]');if(o)return n.instance=o,xt(o),o;var u=_({},a,{"data-href":a.href,"data-precedence":a.precedence,href:null,precedence:null});return o=(e.ownerDocument||e).createElement("style"),xt(o),Un(o,"style",u),tu(o,a.precedence,e),n.instance=o;case"stylesheet":u=jr(a.href);var f=e.querySelector(Ml(u));if(f)return n.state.loading|=4,n.instance=f,xt(f),f;o=U0(a),(u=Ei.get(u))&&$h(o,u),f=(e.ownerDocument||e).createElement("link"),xt(f);var y=f;return y._p=new Promise(function(A,F){y.onload=A,y.onerror=F}),Un(f,"link",o),n.state.loading|=4,tu(f,a.precedence,e),n.instance=f;case"script":return f=qr(a.src),(u=e.querySelector(El(f)))?(n.instance=u,xt(u),u):(o=a,(u=Ei.get(f))&&(o=_({},a),td(o,u)),e=e.ownerDocument||e,u=e.createElement("script"),xt(u),Un(u,"link",o),e.head.appendChild(u),n.instance=u);case"void":return null;default:throw Error(s(443,n.type))}else n.type==="stylesheet"&&(n.state.loading&4)===0&&(o=n.instance,n.state.loading|=4,tu(o,a.precedence,e));return n.instance}function tu(e,n,a){for(var o=a.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),u=o.length?o[o.length-1]:null,f=u,y=0;y<o.length;y++){var A=o[y];if(A.dataset.precedence===n)f=A;else if(f!==u)break}f?f.parentNode.insertBefore(e,f.nextSibling):(n=a.nodeType===9?a.head:a,n.insertBefore(e,n.firstChild))}function $h(e,n){e.crossOrigin==null&&(e.crossOrigin=n.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=n.referrerPolicy),e.title==null&&(e.title=n.title)}function td(e,n){e.crossOrigin==null&&(e.crossOrigin=n.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=n.referrerPolicy),e.integrity==null&&(e.integrity=n.integrity)}var eu=null;function L0(e,n,a){if(eu===null){var o=new Map,u=eu=new Map;u.set(a,o)}else u=eu,o=u.get(a),o||(o=new Map,u.set(a,o));if(o.has(e))return o;for(o.set(e,null),a=a.getElementsByTagName(e),u=0;u<a.length;u++){var f=a[u];if(!(f[bs]||f[an]||e==="link"&&f.getAttribute("rel")==="stylesheet")&&f.namespaceURI!=="http://www.w3.org/2000/svg"){var y=f.getAttribute(n)||"";y=e+y;var A=o.get(y);A?A.push(f):o.set(y,[f])}}return o}function O0(e,n,a){e=e.ownerDocument||e,e.head.insertBefore(a,n==="title"?e.querySelector("head > title"):null)}function MM(e,n,a){if(a===1||n.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof n.precedence!="string"||typeof n.href!="string"||n.href==="")break;return!0;case"link":if(typeof n.rel!="string"||typeof n.href!="string"||n.href===""||n.onLoad||n.onError)break;switch(n.rel){case"stylesheet":return e=n.disabled,typeof n.precedence=="string"&&e==null;default:return!0}case"script":if(n.async&&typeof n.async!="function"&&typeof n.async!="symbol"&&!n.onLoad&&!n.onError&&n.src&&typeof n.src=="string")return!0}return!1}function P0(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function EM(e,n,a,o){if(a.type==="stylesheet"&&(typeof o.media!="string"||matchMedia(o.media).matches!==!1)&&(a.state.loading&4)===0){if(a.instance===null){var u=jr(o.href),f=n.querySelector(Ml(u));if(f){n=f._p,n!==null&&typeof n=="object"&&typeof n.then=="function"&&(e.count++,e=nu.bind(e),n.then(e,e)),a.state.loading|=4,a.instance=f,xt(f);return}f=n.ownerDocument||n,o=U0(o),(u=Ei.get(u))&&$h(o,u),f=f.createElement("link"),xt(f);var y=f;y._p=new Promise(function(A,F){y.onload=A,y.onerror=F}),Un(f,"link",o),a.instance=f}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(a,n),(n=a.state.preload)&&(a.state.loading&3)===0&&(e.count++,a=nu.bind(e),n.addEventListener("load",a),n.addEventListener("error",a))}}var ed=0;function bM(e,n){return e.stylesheets&&e.count===0&&au(e,e.stylesheets),0<e.count||0<e.imgCount?function(a){var o=setTimeout(function(){if(e.stylesheets&&au(e,e.stylesheets),e.unsuspend){var f=e.unsuspend;e.unsuspend=null,f()}},6e4+n);0<e.imgBytes&&ed===0&&(ed=62500*aM());var u=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&au(e,e.stylesheets),e.unsuspend)){var f=e.unsuspend;e.unsuspend=null,f()}},(e.imgBytes>ed?50:800)+n);return e.unsuspend=a,function(){e.unsuspend=null,clearTimeout(o),clearTimeout(u)}}:null}function nu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)au(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var iu=null;function au(e,n){e.stylesheets=null,e.unsuspend!==null&&(e.count++,iu=new Map,n.forEach(TM,e),iu=null,nu.call(e))}function TM(e,n){if(!(n.state.loading&4)){var a=iu.get(e);if(a)var o=a.get(null);else{a=new Map,iu.set(e,a);for(var u=e.querySelectorAll("link[data-precedence],style[data-precedence]"),f=0;f<u.length;f++){var y=u[f];(y.nodeName==="LINK"||y.getAttribute("media")!=="not all")&&(a.set(y.dataset.precedence,y),o=y)}o&&a.set(null,o)}u=n.instance,y=u.getAttribute("data-precedence"),f=a.get(y)||o,f===o&&a.set(null,u),a.set(y,u),this.count++,o=nu.bind(this),u.addEventListener("load",o),u.addEventListener("error",o),f?f.parentNode.insertBefore(u,f.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(u,e.firstChild)),n.state.loading|=4}}var bl={$$typeof:U,Provider:null,Consumer:null,_currentValue:J,_currentValue2:J,_threadCount:0};function AM(e,n,a,o,u,f,y,A,F){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Re(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Re(0),this.hiddenUpdates=Re(null),this.identifierPrefix=o,this.onUncaughtError=u,this.onCaughtError=f,this.onRecoverableError=y,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=F,this.incompleteTransitions=new Map}function z0(e,n,a,o,u,f,y,A,F,et,ht,vt){return e=new AM(e,n,a,y,F,et,ht,vt,A),n=1,f===!0&&(n|=24),f=ai(3,null,null,n),e.current=f,f.stateNode=e,n=Of(),n.refCount++,e.pooledCache=n,n.refCount++,f.memoizedState={element:o,isDehydrated:a,cache:n},Bf(f),e}function I0(e){return e?(e=Er,e):Er}function B0(e,n,a,o,u,f){u=I0(u),o.context===null?o.context=u:o.pendingContext=u,o=Ba(n),o.payload={element:a},f=f===void 0?null:f,f!==null&&(o.callback=f),a=Fa(e,o,n),a!==null&&(Kn(a,e,n),nl(a,e,n))}function F0(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function nd(e,n){F0(e,n),(e=e.alternate)&&F0(e,n)}function H0(e){if(e.tag===13||e.tag===31){var n=ws(e,67108864);n!==null&&Kn(n,e,67108864),nd(e,67108864)}}function G0(e){if(e.tag===13||e.tag===31){var n=ci();n=Ms(n);var a=ws(e,n);a!==null&&Kn(a,e,n),nd(e,n)}}var su=!0;function RM(e,n,a,o){var u=B.T;B.T=null;var f=$.p;try{$.p=2,id(e,n,a,o)}finally{$.p=f,B.T=u}}function CM(e,n,a,o){var u=B.T;B.T=null;var f=$.p;try{$.p=8,id(e,n,a,o)}finally{$.p=f,B.T=u}}function id(e,n,a,o){if(su){var u=ad(o);if(u===null)kh(e,n,o,ru,a),k0(e,o);else if(DM(u,e,n,a,o))o.stopPropagation();else if(k0(e,o),n&4&&-1<wM.indexOf(e)){for(;u!==null;){var f=st(u);if(f!==null)switch(f.tag){case 3:if(f=f.stateNode,f.current.memoizedState.isDehydrated){var y=wt(f.pendingLanes);if(y!==0){var A=f;for(A.pendingLanes|=2,A.entangledLanes|=2;y;){var F=1<<31-ee(y);A.entanglements[1]|=F,y&=~F}ji(f),(Le&6)===0&&(Vc=dt()+500,vl(0))}}break;case 31:case 13:A=ws(f,2),A!==null&&Kn(A,f,2),Xc(),nd(f,2)}if(f=ad(o),f===null&&kh(e,n,o,ru,a),f===u)break;u=f}u!==null&&o.stopPropagation()}else kh(e,n,o,null,a)}}function ad(e){return e=rf(e),sd(e)}var ru=null;function sd(e){if(ru=null,e=W(e),e!==null){var n=c(e);if(n===null)e=null;else{var a=n.tag;if(a===13){if(e=h(n),e!==null)return e;e=null}else if(a===31){if(e=d(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null)}}return ru=e,null}function V0(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(bt()){case _t:return 2;case jt:return 8;case Dt:case Bt:return 32;case ye:return 268435456;default:return 32}default:return 32}}var rd=!1,Za=null,Ka=null,Ja=null,Tl=new Map,Al=new Map,$a=[],wM="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function k0(e,n){switch(e){case"focusin":case"focusout":Za=null;break;case"dragenter":case"dragleave":Ka=null;break;case"mouseover":case"mouseout":Ja=null;break;case"pointerover":case"pointerout":Tl.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Al.delete(n.pointerId)}}function Rl(e,n,a,o,u,f){return e===null||e.nativeEvent!==f?(e={blockedOn:n,domEventName:a,eventSystemFlags:o,nativeEvent:f,targetContainers:[u]},n!==null&&(n=st(n),n!==null&&H0(n)),e):(e.eventSystemFlags|=o,n=e.targetContainers,u!==null&&n.indexOf(u)===-1&&n.push(u),e)}function DM(e,n,a,o,u){switch(n){case"focusin":return Za=Rl(Za,e,n,a,o,u),!0;case"dragenter":return Ka=Rl(Ka,e,n,a,o,u),!0;case"mouseover":return Ja=Rl(Ja,e,n,a,o,u),!0;case"pointerover":var f=u.pointerId;return Tl.set(f,Rl(Tl.get(f)||null,e,n,a,o,u)),!0;case"gotpointercapture":return f=u.pointerId,Al.set(f,Rl(Al.get(f)||null,e,n,a,o,u)),!0}return!1}function X0(e){var n=W(e.target);if(n!==null){var a=c(n);if(a!==null){if(n=a.tag,n===13){if(n=h(a),n!==null){e.blockedOn=n,Es(e.priority,function(){G0(a)});return}}else if(n===31){if(n=d(a),n!==null){e.blockedOn=n,Es(e.priority,function(){G0(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function ou(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=ad(e.nativeEvent);if(a===null){a=e.nativeEvent;var o=new a.constructor(a.type,a);sf=o,a.target.dispatchEvent(o),sf=null}else return n=st(a),n!==null&&H0(n),e.blockedOn=a,!1;n.shift()}return!0}function j0(e,n,a){ou(e)&&a.delete(n)}function UM(){rd=!1,Za!==null&&ou(Za)&&(Za=null),Ka!==null&&ou(Ka)&&(Ka=null),Ja!==null&&ou(Ja)&&(Ja=null),Tl.forEach(j0),Al.forEach(j0)}function lu(e,n){e.blockedOn===n&&(e.blockedOn=null,rd||(rd=!0,r.unstable_scheduleCallback(r.unstable_NormalPriority,UM)))}var cu=null;function q0(e){cu!==e&&(cu=e,r.unstable_scheduleCallback(r.unstable_NormalPriority,function(){cu===e&&(cu=null);for(var n=0;n<e.length;n+=3){var a=e[n],o=e[n+1],u=e[n+2];if(typeof o!="function"){if(sd(o||a)===null)continue;break}var f=st(a);f!==null&&(e.splice(n,3),n-=3,ah(f,{pending:!0,data:u,method:a.method,action:o},o,u))}}))}function Wr(e){function n(F){return lu(F,e)}Za!==null&&lu(Za,e),Ka!==null&&lu(Ka,e),Ja!==null&&lu(Ja,e),Tl.forEach(n),Al.forEach(n);for(var a=0;a<$a.length;a++){var o=$a[a];o.blockedOn===e&&(o.blockedOn=null)}for(;0<$a.length&&(a=$a[0],a.blockedOn===null);)X0(a),a.blockedOn===null&&$a.shift();if(a=(e.ownerDocument||e).$$reactFormReplay,a!=null)for(o=0;o<a.length;o+=3){var u=a[o],f=a[o+1],y=u[Rn]||null;if(typeof f=="function")y||q0(a);else if(y){var A=null;if(f&&f.hasAttribute("formAction")){if(u=f,y=f[Rn]||null)A=y.formAction;else if(sd(u)!==null)continue}else A=y.action;typeof A=="function"?a[o+1]=A:(a.splice(o,3),o-=3),q0(a)}}}function W0(){function e(f){f.canIntercept&&f.info==="react-transition"&&f.intercept({handler:function(){return new Promise(function(y){return u=y})},focusReset:"manual",scroll:"manual"})}function n(){u!==null&&(u(),u=null),o||setTimeout(a,20)}function a(){if(!o&&!navigation.transition){var f=navigation.currentEntry;f&&f.url!=null&&navigation.navigate(f.url,{state:f.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var o=!1,u=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",n),navigation.addEventListener("navigateerror",n),setTimeout(a,100),function(){o=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",n),navigation.removeEventListener("navigateerror",n),u!==null&&(u(),u=null)}}}function od(e){this._internalRoot=e}uu.prototype.render=od.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(s(409));var a=n.current,o=ci();B0(a,o,e,n,null,null)},uu.prototype.unmount=od.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;B0(e.current,2,null,e,null,null),Xc(),n[Ji]=null}};function uu(e){this._internalRoot=e}uu.prototype.unstable_scheduleHydration=function(e){if(e){var n=Fo();e={blockedOn:null,target:e,priority:n};for(var a=0;a<$a.length&&n!==0&&n<$a[a].priority;a++);$a.splice(a,0,e),a===0&&X0(e)}};var Y0=t.version;if(Y0!=="19.2.7")throw Error(s(527,Y0,"19.2.7"));$.findDOMNode=function(e){var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(s(188)):(e=Object.keys(e).join(","),Error(s(268,e)));return e=p(n),e=e!==null?g(e):null,e=e===null?null:e.stateNode,e};var NM={bundleType:0,version:"19.2.7",rendererPackageName:"react-dom",currentDispatcherRef:B,reconcilerVersion:"19.2.7"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var fu=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!fu.isDisabled&&fu.supportsFiber)try{Qt=fu.inject(NM),qt=fu}catch{}}return wl.createRoot=function(e,n){if(!l(e))throw Error(s(299));var a=!1,o="",u=e_,f=n_,y=i_;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(o=n.identifierPrefix),n.onUncaughtError!==void 0&&(u=n.onUncaughtError),n.onCaughtError!==void 0&&(f=n.onCaughtError),n.onRecoverableError!==void 0&&(y=n.onRecoverableError)),n=z0(e,1,!1,null,null,a,o,null,u,f,y,W0),e[Ji]=n.current,Vh(e),new od(n)},wl.hydrateRoot=function(e,n,a){if(!l(e))throw Error(s(299));var o=!1,u="",f=e_,y=n_,A=i_,F=null;return a!=null&&(a.unstable_strictMode===!0&&(o=!0),a.identifierPrefix!==void 0&&(u=a.identifierPrefix),a.onUncaughtError!==void 0&&(f=a.onUncaughtError),a.onCaughtError!==void 0&&(y=a.onCaughtError),a.onRecoverableError!==void 0&&(A=a.onRecoverableError),a.formState!==void 0&&(F=a.formState)),n=z0(e,1,!0,n,a??null,o,u,F,f,y,A,W0),n.context=I0(null),a=n.current,o=ci(),o=Ms(o),u=Ba(o),u.callback=null,Fa(a,u,o),a=o,n.current.lanes=a,An(n,a),ji(n),e[Ji]=n.current,Vh(e),new uu(n)},wl.version="19.2.7",wl}var sv;function kM(){if(sv)return fd.exports;sv=1;function r(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(r)}catch(t){console.error(t)}}return r(),fd.exports=VM(),fd.exports}var XM=kM();const jM=wy(XM);var Ql=class{constructor(){this.listeners=new Set,this.subscribe=this.subscribe.bind(this)}subscribe(r){return this.listeners.add(r),this.onSubscribe(),()=>{this.listeners.delete(r),this.onUnsubscribe()}}hasListeners(){return this.listeners.size>0}onSubscribe(){}onUnsubscribe(){}},nr,cs,mo,yy,qM=(yy=class extends Ql{constructor(){super();$t(this,nr);$t(this,cs);$t(this,mo);zt(this,mo,t=>{if(typeof window<"u"&&window.addEventListener){const i=()=>t();return window.addEventListener("visibilitychange",i,!1),()=>{window.removeEventListener("visibilitychange",i)}}})}onSubscribe(){j(this,cs)||this.setEventListener(j(this,mo))}onUnsubscribe(){var t;this.hasListeners()||((t=j(this,cs))==null||t.call(this),zt(this,cs,void 0))}setEventListener(t){var i;zt(this,mo,t),(i=j(this,cs))==null||i.call(this),zt(this,cs,t(s=>{typeof s=="boolean"?this.setFocused(s):this.onFocus()}))}setFocused(t){j(this,nr)!==t&&(zt(this,nr,t),this.onFocus())}onFocus(){const t=this.isFocused();this.listeners.forEach(i=>{i(t)})}isFocused(){var t;return typeof j(this,nr)=="boolean"?j(this,nr):((t=globalThis.document)==null?void 0:t.visibilityState)!=="hidden"}},nr=new WeakMap,cs=new WeakMap,mo=new WeakMap,yy),Jp=new qM,WM={setTimeout:(r,t)=>setTimeout(r,t),clearTimeout:r=>clearTimeout(r),setInterval:(r,t)=>setInterval(r,t),clearInterval:r=>clearInterval(r)},us,Zp,xy,YM=(xy=class{constructor(){$t(this,us,WM);$t(this,Zp,!1)}setTimeoutProvider(r){zt(this,us,r)}setTimeout(r,t){return j(this,us).setTimeout(r,t)}clearTimeout(r){j(this,us).clearTimeout(r)}setInterval(r,t){return j(this,us).setInterval(r,t)}clearInterval(r){j(this,us).clearInterval(r)}},us=new WeakMap,Zp=new WeakMap,xy),Js=new YM;function QM(r){setTimeout(r,0)}var ZM=typeof window>"u"||"Deno"in globalThis;function ti(){}function KM(r,t){return typeof r=="function"?r(t):r}function Yd(r){return typeof r=="number"&&r>=0&&r!==1/0}function Dy(r,t){return Math.max(r+(t||0)-Date.now(),0)}function _s(r,t){return typeof r=="function"?r(t):r}function di(r,t){return typeof r=="function"?r(t):r}function rv(r,t){const{type:i="all",exact:s,fetchStatus:l,predicate:c,queryKey:h,stale:d}=r;if(h){if(s){if(t.queryHash!==$p(h,t.options))return!1}else if(!Gl(t.queryKey,h))return!1}if(i!=="all"){const m=t.isActive();if(i==="active"&&!m||i==="inactive"&&m)return!1}return!(typeof d=="boolean"&&t.isStale()!==d||l&&l!==t.state.fetchStatus||c&&!c(t))}function ov(r,t){const{exact:i,status:s,predicate:l,mutationKey:c}=r;if(c){if(!t.options.mutationKey)return!1;if(i){if(Hl(t.options.mutationKey)!==Hl(c))return!1}else if(!Gl(t.options.mutationKey,c))return!1}return!(s&&t.state.status!==s||l&&!l(t))}function $p(r,t){return((t==null?void 0:t.queryKeyHashFn)||Hl)(r)}function Hl(r){return JSON.stringify(r,(t,i)=>Zd(i)?Object.keys(i).sort().reduce((s,l)=>(s[l]=i[l],s),{}):i)}function Gl(r,t){return r===t?!0:typeof r!=typeof t?!1:r&&t&&typeof r=="object"&&typeof t=="object"?Object.keys(t).every(i=>Gl(r[i],t[i])):!1}var JM=Object.prototype.hasOwnProperty;function Uy(r,t,i=0){if(r===t)return r;if(i>500)return t;const s=lv(r)&&lv(t);if(!s&&!(Zd(r)&&Zd(t)))return t;const c=(s?r:Object.keys(r)).length,h=s?t:Object.keys(t),d=h.length,m=s?new Array(d):{};let p=0;for(let g=0;g<d;g++){const _=s?g:h[g],x=r[_],S=t[_];if(x===S){m[_]=x,(s?g<c:JM.call(r,_))&&p++;continue}if(x===null||S===null||typeof x!="object"||typeof S!="object"){m[_]=S;continue}const E=Uy(x,S,i+1);m[_]=E,E===x&&p++}return c===d&&p===c?r:m}function Qd(r,t){if(!t||Object.keys(r).length!==Object.keys(t).length)return!1;for(const i in r)if(r[i]!==t[i])return!1;return!0}function lv(r){return Array.isArray(r)&&r.length===Object.keys(r).length}function Zd(r){if(!cv(r))return!1;const t=r.constructor;if(t===void 0)return!0;const i=t.prototype;return!(!cv(i)||!i.hasOwnProperty("isPrototypeOf")||Object.getPrototypeOf(r)!==Object.prototype)}function cv(r){return Object.prototype.toString.call(r)==="[object Object]"}function $M(r){return new Promise(t=>{Js.setTimeout(t,r)})}function Kd(r,t,i){return typeof i.structuralSharing=="function"?i.structuralSharing(r,t):i.structuralSharing!==!1?Uy(r,t):t}function tE(r,t,i=0){const s=[...r,t];return i&&s.length>i?s.slice(1):s}function eE(r,t,i=0){const s=[t,...r];return i&&s.length>i?s.slice(0,-1):s}var tm=Symbol();function Ny(r,t){return!r.queryFn&&(t!=null&&t.initialPromise)?()=>t.initialPromise:!r.queryFn||r.queryFn===tm?()=>Promise.reject(new Error(`Missing queryFn: '${r.queryHash}'`)):r.queryFn}function Ly(r,t){return typeof r=="function"?r(...t):!!r}function nE(r,t,i){let s=!1,l;return Object.defineProperty(r,"signal",{enumerable:!0,get:()=>(l??(l=t()),s||(s=!0,l.aborted?i():l.addEventListener("abort",i,{once:!0})),l)}),r}var Vl=(()=>{let r=()=>ZM;return{isServer(){return r()},setIsServer(t){r=t}}})();function Jd(){let r,t;const i=new Promise((l,c)=>{r=l,t=c});i.status="pending",i.catch(()=>{});function s(l){Object.assign(i,l),delete i.resolve,delete i.reject}return i.resolve=l=>{s({status:"fulfilled",value:l}),r(l)},i.reject=l=>{s({status:"rejected",reason:l}),t(l)},i}var iE=QM;function aE(){let r=[],t=0,i=d=>{d()},s=d=>{d()},l=iE;const c=d=>{t?r.push(d):l(()=>{i(d)})},h=()=>{const d=r;r=[],d.length&&l(()=>{s(()=>{d.forEach(m=>{i(m)})})})};return{batch:d=>{let m;t++;try{m=d()}finally{t--,t||h()}return m},batchCalls:d=>(...m)=>{c(()=>{d(...m)})},schedule:c,setNotifyFunction:d=>{i=d},setBatchNotifyFunction:d=>{s=d},setScheduler:d=>{l=d}}}var Nn=aE(),go,fs,_o,Sy,sE=(Sy=class extends Ql{constructor(){super();$t(this,go,!0);$t(this,fs);$t(this,_o);zt(this,_o,t=>{if(typeof window<"u"&&window.addEventListener){const i=()=>t(!0),s=()=>t(!1);return window.addEventListener("online",i,!1),window.addEventListener("offline",s,!1),()=>{window.removeEventListener("online",i),window.removeEventListener("offline",s)}}})}onSubscribe(){j(this,fs)||this.setEventListener(j(this,_o))}onUnsubscribe(){var t;this.hasListeners()||((t=j(this,fs))==null||t.call(this),zt(this,fs,void 0))}setEventListener(t){var i;zt(this,_o,t),(i=j(this,fs))==null||i.call(this),zt(this,fs,t(this.setOnline.bind(this)))}setOnline(t){j(this,go)!==t&&(zt(this,go,t),this.listeners.forEach(s=>{s(t)}))}isOnline(){return j(this,go)}},go=new WeakMap,fs=new WeakMap,_o=new WeakMap,Sy),ju=new sE;function rE(r){return Math.min(1e3*2**r,3e4)}function Oy(r){return(r??"online")==="online"?ju.isOnline():!0}var $d=class extends Error{constructor(r){super("CancelledError"),this.revert=r==null?void 0:r.revert,this.silent=r==null?void 0:r.silent}};function Py(r){let t=!1,i=0,s;const l=Jd(),c=()=>l.status!=="pending",h=b=>{var M;if(!c()){const v=new $d(b);x(v),(M=r.onCancel)==null||M.call(r,v)}},d=()=>{t=!0},m=()=>{t=!1},p=()=>Jp.isFocused()&&(r.networkMode==="always"||ju.isOnline())&&r.canRun(),g=()=>Oy(r.networkMode)&&r.canRun(),_=b=>{c()||(s==null||s(),l.resolve(b))},x=b=>{c()||(s==null||s(),l.reject(b))},S=()=>new Promise(b=>{var M;s=v=>{(c()||p())&&b(v)},(M=r.onPause)==null||M.call(r)}).then(()=>{var b;s=void 0,c()||(b=r.onContinue)==null||b.call(r)}),E=()=>{if(c())return;let b;const M=i===0?r.initialPromise:void 0;try{b=M??r.fn()}catch(v){b=Promise.reject(v)}Promise.resolve(b).then(_).catch(v=>{var I;if(c())return;const L=r.retry??(Vl.isServer()?0:3),U=r.retryDelay??rE,T=typeof U=="function"?U(i,v):U,V=L===!0||typeof L=="number"&&i<L||typeof L=="function"&&L(i,v);if(t||!V){x(v);return}i++,(I=r.onFail)==null||I.call(r,i,v),$M(T).then(()=>p()?void 0:S()).then(()=>{t?x(v):E()})})};return{promise:l,status:()=>l.status,cancel:h,continue:()=>(s==null||s(),l),cancelRetry:d,continueRetry:m,canStart:g,start:()=>(g()?E():S().then(E),l)}}var ir,My,zy=(My=class{constructor(){$t(this,ir)}destroy(){this.clearGcTimeout()}scheduleGc(){this.clearGcTimeout(),Yd(this.gcTime)&&zt(this,ir,Js.setTimeout(()=>{this.optionalRemove()},this.gcTime))}updateGcTime(r){this.gcTime=Math.max(this.gcTime||0,r??(Vl.isServer()?1/0:300*1e3))}clearGcTimeout(){j(this,ir)!==void 0&&(Js.clearTimeout(j(this,ir)),zt(this,ir,void 0))}},ir=new WeakMap,My);function oE(r){return{onFetch:(t,i)=>{var g,_,x,S,E;const s=t.options,l=(x=(_=(g=t.fetchOptions)==null?void 0:g.meta)==null?void 0:_.fetchMore)==null?void 0:x.direction,c=((S=t.state.data)==null?void 0:S.pages)||[],h=((E=t.state.data)==null?void 0:E.pageParams)||[];let d={pages:[],pageParams:[]},m=0;const p=async()=>{let b=!1;const M=U=>{nE(U,()=>t.signal,()=>b=!0)},v=Ny(t.options,t.fetchOptions),L=async(U,T,V)=>{if(b)return Promise.reject(t.signal.reason);if(T==null&&U.pages.length)return Promise.resolve(U);const P=(()=>{const G={client:t.client,queryKey:t.queryKey,pageParam:T,direction:V?"backward":"forward",meta:t.options.meta};return M(G),G})(),H=await v(P),{maxPages:D}=t.options,C=V?eE:tE;return{pages:C(U.pages,H,D),pageParams:C(U.pageParams,T,D)}};if(l&&c.length){const U=l==="backward",T=U?lE:uv,V={pages:c,pageParams:h},I=T(s,V);d=await L(V,I,U)}else{const U=r??c.length;do{const T=m===0?h[0]??s.initialPageParam:uv(s,d);if(m>0&&T==null)break;d=await L(d,T),m++}while(m<U)}return d};t.options.persister?t.fetchFn=()=>{var b,M;return(M=(b=t.options).persister)==null?void 0:M.call(b,p,{client:t.client,queryKey:t.queryKey,meta:t.options.meta,signal:t.signal},i)}:t.fetchFn=p}}}function uv(r,{pages:t,pageParams:i}){const s=t.length-1;return t.length>0?r.getNextPageParam(t[s],t,i[s],i):void 0}function lE(r,{pages:t,pageParams:i}){var s;return t.length>0?(s=r.getPreviousPageParam)==null?void 0:s.call(r,t[0],t,i[0],i):void 0}var vo,ar,yo,Ti,sr,Tn,Xl,rr,hi,Iy,Ma,Ey,cE=(Ey=class extends zy{constructor(t){super();$t(this,hi);$t(this,vo);$t(this,ar);$t(this,yo);$t(this,Ti);$t(this,sr);$t(this,Tn);$t(this,Xl);$t(this,rr);zt(this,rr,!1),zt(this,Xl,t.defaultOptions),this.setOptions(t.options),this.observers=[],zt(this,sr,t.client),zt(this,Ti,j(this,sr).getQueryCache()),this.queryKey=t.queryKey,this.queryHash=t.queryHash,zt(this,ar,hv(this.options)),this.state=t.state??j(this,ar),this.scheduleGc()}get meta(){return this.options.meta}get queryType(){return j(this,vo)}get promise(){var t;return(t=j(this,Tn))==null?void 0:t.promise}setOptions(t){if(this.options={...j(this,Xl),...t},t!=null&&t._type&&zt(this,vo,t._type),this.updateGcTime(this.options.gcTime),this.state&&this.state.data===void 0){const i=hv(this.options);i.data!==void 0&&(this.setState(fv(i.data,i.dataUpdatedAt)),zt(this,ar,i))}}optionalRemove(){!this.observers.length&&this.state.fetchStatus==="idle"&&j(this,Ti).remove(this)}setData(t,i){const s=Kd(this.state.data,t,this.options);return Ee(this,hi,Ma).call(this,{data:s,type:"success",dataUpdatedAt:i==null?void 0:i.updatedAt,manual:i==null?void 0:i.manual}),s}setState(t){Ee(this,hi,Ma).call(this,{type:"setState",state:t})}cancel(t){var s,l;const i=(s=j(this,Tn))==null?void 0:s.promise;return(l=j(this,Tn))==null||l.cancel(t),i?i.then(ti).catch(ti):Promise.resolve()}destroy(){super.destroy(),this.cancel({silent:!0})}get resetState(){return j(this,ar)}reset(){this.destroy(),this.setState(this.resetState)}isActive(){return this.observers.some(t=>di(t.options.enabled,this)!==!1)}isDisabled(){return this.getObserversCount()>0?!this.isActive():this.options.queryFn===tm||!this.isFetched()}isFetched(){return this.state.dataUpdateCount+this.state.errorUpdateCount>0}isStatic(){return this.getObserversCount()>0?this.observers.some(t=>_s(t.options.staleTime,this)==="static"):!1}isStale(){return this.getObserversCount()>0?this.observers.some(t=>t.getCurrentResult().isStale):this.state.data===void 0||this.state.isInvalidated}isStaleByTime(t=0){return this.state.data===void 0?!0:t==="static"?!1:this.state.isInvalidated?!0:!Dy(this.state.dataUpdatedAt,t)}onFocus(){var i;const t=this.observers.find(s=>s.shouldFetchOnWindowFocus());t==null||t.refetch({cancelRefetch:!1}),(i=j(this,Tn))==null||i.continue()}onOnline(){var i;const t=this.observers.find(s=>s.shouldFetchOnReconnect());t==null||t.refetch({cancelRefetch:!1}),(i=j(this,Tn))==null||i.continue()}addObserver(t){this.observers.includes(t)||(this.observers.push(t),this.clearGcTimeout(),j(this,Ti).notify({type:"observerAdded",query:this,observer:t}))}removeObserver(t){this.observers.includes(t)&&(this.observers=this.observers.filter(i=>i!==t),this.observers.length||(j(this,Tn)&&(j(this,rr)||Ee(this,hi,Iy).call(this)?j(this,Tn).cancel({revert:!0}):j(this,Tn).cancelRetry()),this.scheduleGc()),j(this,Ti).notify({type:"observerRemoved",query:this,observer:t}))}getObserversCount(){return this.observers.length}invalidate(){this.state.isInvalidated||Ee(this,hi,Ma).call(this,{type:"invalidate"})}async fetch(t,i){var p,g,_,x,S,E,b,M,v,L,U;if(this.state.fetchStatus!=="idle"&&((p=j(this,Tn))==null?void 0:p.status())!=="rejected"){if(this.state.data!==void 0&&(i!=null&&i.cancelRefetch))this.cancel({silent:!0});else if(j(this,Tn))return j(this,Tn).continueRetry(),j(this,Tn).promise}if(t&&this.setOptions(t),!this.options.queryFn){const T=this.observers.find(V=>V.options.queryFn);T&&this.setOptions(T.options)}const s=new AbortController,l=T=>{Object.defineProperty(T,"signal",{enumerable:!0,get:()=>(zt(this,rr,!0),s.signal)})},c=()=>{const T=Ny(this.options,i),I=(()=>{const P={client:j(this,sr),queryKey:this.queryKey,meta:this.meta};return l(P),P})();return zt(this,rr,!1),this.options.persister?this.options.persister(T,I,this):T(I)},d=(()=>{const T={fetchOptions:i,options:this.options,queryKey:this.queryKey,client:j(this,sr),state:this.state,fetchFn:c};return l(T),T})(),m=j(this,vo)==="infinite"?oE(this.options.pages):this.options.behavior;m==null||m.onFetch(d,this),zt(this,yo,this.state),(this.state.fetchStatus==="idle"||this.state.fetchMeta!==((g=d.fetchOptions)==null?void 0:g.meta))&&Ee(this,hi,Ma).call(this,{type:"fetch",meta:(_=d.fetchOptions)==null?void 0:_.meta}),zt(this,Tn,Py({initialPromise:i==null?void 0:i.initialPromise,fn:d.fetchFn,onCancel:T=>{T instanceof $d&&T.revert&&this.setState({...j(this,yo),fetchStatus:"idle"}),s.abort()},onFail:(T,V)=>{Ee(this,hi,Ma).call(this,{type:"failed",failureCount:T,error:V})},onPause:()=>{Ee(this,hi,Ma).call(this,{type:"pause"})},onContinue:()=>{Ee(this,hi,Ma).call(this,{type:"continue"})},retry:d.options.retry,retryDelay:d.options.retryDelay,networkMode:d.options.networkMode,canRun:()=>!0}));try{const T=await j(this,Tn).start();if(T===void 0)throw new Error(`${this.queryHash} data is undefined`);return this.setData(T),(S=(x=j(this,Ti).config).onSuccess)==null||S.call(x,T,this),(b=(E=j(this,Ti).config).onSettled)==null||b.call(E,T,this.state.error,this),T}catch(T){if(T instanceof $d){if(T.silent)return j(this,Tn).promise;if(T.revert){if(this.state.data===void 0)throw T;return this.state.data}}throw Ee(this,hi,Ma).call(this,{type:"error",error:T}),(v=(M=j(this,Ti).config).onError)==null||v.call(M,T,this),(U=(L=j(this,Ti).config).onSettled)==null||U.call(L,this.state.data,T,this),T}finally{this.scheduleGc()}}},vo=new WeakMap,ar=new WeakMap,yo=new WeakMap,Ti=new WeakMap,sr=new WeakMap,Tn=new WeakMap,Xl=new WeakMap,rr=new WeakMap,hi=new WeakSet,Iy=function(){return this.state.fetchStatus==="paused"&&this.state.status==="pending"},Ma=function(t){const i=s=>{switch(t.type){case"failed":return{...s,fetchFailureCount:t.failureCount,fetchFailureReason:t.error};case"pause":return{...s,fetchStatus:"paused"};case"continue":return{...s,fetchStatus:"fetching"};case"fetch":return{...s,...By(s.data,this.options),fetchMeta:t.meta??null};case"success":const l={...s,...fv(t.data,t.dataUpdatedAt),dataUpdateCount:s.dataUpdateCount+1,...!t.manual&&{fetchStatus:"idle",fetchFailureCount:0,fetchFailureReason:null}};return zt(this,yo,t.manual?l:void 0),l;case"error":const c=t.error;return{...s,error:c,errorUpdateCount:s.errorUpdateCount+1,errorUpdatedAt:Date.now(),fetchFailureCount:s.fetchFailureCount+1,fetchFailureReason:c,fetchStatus:"idle",status:"error",isInvalidated:!0};case"invalidate":return{...s,isInvalidated:!0};case"setState":return{...s,...t.state}}};this.state=i(this.state),Nn.batch(()=>{this.observers.forEach(s=>{s.onQueryUpdate()}),j(this,Ti).notify({query:this,type:"updated",action:t})})},Ey);function By(r,t){return{fetchFailureCount:0,fetchFailureReason:null,fetchStatus:Oy(t.networkMode)?"fetching":"paused",...r===void 0&&{error:null,status:"pending"}}}function fv(r,t){return{data:r,dataUpdatedAt:t??Date.now(),error:null,isInvalidated:!1,status:"success"}}function hv(r){const t=typeof r.initialData=="function"?r.initialData():r.initialData,i=t!==void 0,s=i?typeof r.initialDataUpdatedAt=="function"?r.initialDataUpdatedAt():r.initialDataUpdatedAt:0;return{data:t,dataUpdateCount:0,dataUpdatedAt:i?s??Date.now():0,error:null,errorUpdateCount:0,errorUpdatedAt:0,fetchFailureCount:0,fetchFailureReason:null,fetchMeta:null,isInvalidated:!1,status:i?"success":"pending",fetchStatus:"idle"}}var $n,Te,jl,Xn,or,xo,ba,hs,ql,So,Mo,lr,cr,ds,Eo,ze,Il,tp,ep,np,ip,ap,sp,rp,Fy,by,uE=(by=class extends Ql{constructor(t,i){super();$t(this,ze);$t(this,$n);$t(this,Te);$t(this,jl);$t(this,Xn);$t(this,or);$t(this,xo);$t(this,ba);$t(this,hs);$t(this,ql);$t(this,So);$t(this,Mo);$t(this,lr);$t(this,cr);$t(this,ds);$t(this,Eo,new Set);this.options=i,zt(this,$n,t),zt(this,hs,null),zt(this,ba,Jd()),this.bindMethods(),this.setOptions(i)}bindMethods(){this.refetch=this.refetch.bind(this)}onSubscribe(){this.listeners.size===1&&(j(this,Te).addObserver(this),dv(j(this,Te),this.options)?Ee(this,ze,Il).call(this):this.updateResult(),Ee(this,ze,ip).call(this))}onUnsubscribe(){this.hasListeners()||this.destroy()}shouldFetchOnReconnect(){return op(j(this,Te),this.options,this.options.refetchOnReconnect)}shouldFetchOnWindowFocus(){return op(j(this,Te),this.options,this.options.refetchOnWindowFocus)}destroy(){this.listeners=new Set,Ee(this,ze,ap).call(this),Ee(this,ze,sp).call(this),j(this,Te).removeObserver(this)}setOptions(t){const i=this.options,s=j(this,Te);if(this.options=j(this,$n).defaultQueryOptions(t),this.options.enabled!==void 0&&typeof this.options.enabled!="boolean"&&typeof this.options.enabled!="function"&&typeof di(this.options.enabled,j(this,Te))!="boolean")throw new Error("Expected enabled to be a boolean or a callback that returns a boolean");Ee(this,ze,rp).call(this),j(this,Te).setOptions(this.options),i._defaulted&&!Qd(this.options,i)&&j(this,$n).getQueryCache().notify({type:"observerOptionsUpdated",query:j(this,Te),observer:this});const l=this.hasListeners();l&&pv(j(this,Te),s,this.options,i)&&Ee(this,ze,Il).call(this),this.updateResult(),l&&(j(this,Te)!==s||di(this.options.enabled,j(this,Te))!==di(i.enabled,j(this,Te))||_s(this.options.staleTime,j(this,Te))!==_s(i.staleTime,j(this,Te)))&&Ee(this,ze,tp).call(this);const c=Ee(this,ze,ep).call(this);l&&(j(this,Te)!==s||di(this.options.enabled,j(this,Te))!==di(i.enabled,j(this,Te))||c!==j(this,ds))&&Ee(this,ze,np).call(this,c)}getOptimisticResult(t){const i=j(this,$n).getQueryCache().build(j(this,$n),t),s=this.createResult(i,t);return hE(this,s)&&(zt(this,Xn,s),zt(this,xo,this.options),zt(this,or,j(this,Te).state)),s}getCurrentResult(){return j(this,Xn)}trackResult(t,i){return new Proxy(t,{get:(s,l)=>(this.trackProp(l),i==null||i(l),l==="promise"&&(this.trackProp("data"),!this.options.experimental_prefetchInRender&&j(this,ba).status==="pending"&&j(this,ba).reject(new Error("experimental_prefetchInRender feature flag is not enabled"))),Reflect.get(s,l))})}trackProp(t){j(this,Eo).add(t)}getCurrentQuery(){return j(this,Te)}refetch({...t}={}){return this.fetch({...t})}fetchOptimistic(t){const i=j(this,$n).defaultQueryOptions(t),s=j(this,$n).getQueryCache().build(j(this,$n),i);return s.fetch().then(()=>this.createResult(s,i))}fetch(t){return Ee(this,ze,Il).call(this,{...t,cancelRefetch:t.cancelRefetch??!0}).then(()=>(this.updateResult(),j(this,Xn)))}createResult(t,i){var D;const s=j(this,Te),l=this.options,c=j(this,Xn),h=j(this,or),d=j(this,xo),p=t!==s?t.state:j(this,jl),{state:g}=t;let _={...g},x=!1,S;if(i._optimisticResults){const C=this.hasListeners(),G=!C&&dv(t,i),ot=C&&pv(t,s,i,l);(G||ot)&&(_={..._,...By(g.data,t.options)}),i._optimisticResults==="isRestoring"&&(_.fetchStatus="idle")}let{error:E,errorUpdatedAt:b,status:M}=_;S=_.data;let v=!1;if(i.placeholderData!==void 0&&S===void 0&&M==="pending"){let C;c!=null&&c.isPlaceholderData&&i.placeholderData===(d==null?void 0:d.placeholderData)?(C=c.data,v=!0):C=typeof i.placeholderData=="function"?i.placeholderData((D=j(this,Mo))==null?void 0:D.state.data,j(this,Mo)):i.placeholderData,C!==void 0&&(M="success",S=Kd(c==null?void 0:c.data,C,i),x=!0)}if(i.select&&S!==void 0&&!v)if(c&&S===(h==null?void 0:h.data)&&i.select===j(this,ql))S=j(this,So);else try{zt(this,ql,i.select),S=i.select(S),S=Kd(c==null?void 0:c.data,S,i),zt(this,So,S),zt(this,hs,null)}catch(C){zt(this,hs,C)}j(this,hs)&&(E=j(this,hs),S=j(this,So),b=Date.now(),M="error");const L=_.fetchStatus==="fetching",U=M==="pending",T=M==="error",V=U&&L,I=S!==void 0,H={status:M,fetchStatus:_.fetchStatus,isPending:U,isSuccess:M==="success",isError:T,isInitialLoading:V,isLoading:V,data:S,dataUpdatedAt:_.dataUpdatedAt,error:E,errorUpdatedAt:b,failureCount:_.fetchFailureCount,failureReason:_.fetchFailureReason,errorUpdateCount:_.errorUpdateCount,isFetched:t.isFetched(),isFetchedAfterMount:_.dataUpdateCount>p.dataUpdateCount||_.errorUpdateCount>p.errorUpdateCount,isFetching:L,isRefetching:L&&!U,isLoadingError:T&&!I,isPaused:_.fetchStatus==="paused",isPlaceholderData:x,isRefetchError:T&&I,isStale:em(t,i),refetch:this.refetch,promise:j(this,ba),isEnabled:di(i.enabled,t)!==!1};if(this.options.experimental_prefetchInRender){const C=H.data!==void 0,G=H.status==="error"&&!C,ot=gt=>{G?gt.reject(H.error):C&&gt.resolve(H.data)},lt=()=>{const gt=zt(this,ba,H.promise=Jd());ot(gt)},mt=j(this,ba);switch(mt.status){case"pending":t.queryHash===s.queryHash&&ot(mt);break;case"fulfilled":(G||H.data!==mt.value)&&lt();break;case"rejected":(!G||H.error!==mt.reason)&&lt();break}}return H}updateResult(){const t=j(this,Xn),i=this.createResult(j(this,Te),this.options);if(zt(this,or,j(this,Te).state),zt(this,xo,this.options),j(this,or).data!==void 0&&zt(this,Mo,j(this,Te)),Qd(i,t))return;zt(this,Xn,i);const s=()=>{if(!t)return!0;const{notifyOnChangeProps:l}=this.options,c=typeof l=="function"?l():l;if(c==="all"||!c&&!j(this,Eo).size)return!0;const h=new Set(c??j(this,Eo));return this.options.throwOnError&&h.add("error"),Object.keys(j(this,Xn)).some(d=>{const m=d;return j(this,Xn)[m]!==t[m]&&h.has(m)})};Ee(this,ze,Fy).call(this,{listeners:s()})}onQueryUpdate(){this.updateResult(),this.hasListeners()&&Ee(this,ze,ip).call(this)}},$n=new WeakMap,Te=new WeakMap,jl=new WeakMap,Xn=new WeakMap,or=new WeakMap,xo=new WeakMap,ba=new WeakMap,hs=new WeakMap,ql=new WeakMap,So=new WeakMap,Mo=new WeakMap,lr=new WeakMap,cr=new WeakMap,ds=new WeakMap,Eo=new WeakMap,ze=new WeakSet,Il=function(t){Ee(this,ze,rp).call(this);let i=j(this,Te).fetch(this.options,t);return t!=null&&t.throwOnError||(i=i.catch(ti)),i},tp=function(){Ee(this,ze,ap).call(this);const t=_s(this.options.staleTime,j(this,Te));if(Vl.isServer()||j(this,Xn).isStale||!Yd(t))return;const s=Dy(j(this,Xn).dataUpdatedAt,t)+1;zt(this,lr,Js.setTimeout(()=>{j(this,Xn).isStale||this.updateResult()},s))},ep=function(){return(typeof this.options.refetchInterval=="function"?this.options.refetchInterval(j(this,Te)):this.options.refetchInterval)??!1},np=function(t){Ee(this,ze,sp).call(this),zt(this,ds,t),!(Vl.isServer()||di(this.options.enabled,j(this,Te))===!1||!Yd(j(this,ds))||j(this,ds)===0)&&zt(this,cr,Js.setInterval(()=>{(this.options.refetchIntervalInBackground||Jp.isFocused())&&Ee(this,ze,Il).call(this)},j(this,ds)))},ip=function(){Ee(this,ze,tp).call(this),Ee(this,ze,np).call(this,Ee(this,ze,ep).call(this))},ap=function(){j(this,lr)!==void 0&&(Js.clearTimeout(j(this,lr)),zt(this,lr,void 0))},sp=function(){j(this,cr)!==void 0&&(Js.clearInterval(j(this,cr)),zt(this,cr,void 0))},rp=function(){const t=j(this,$n).getQueryCache().build(j(this,$n),this.options);if(t===j(this,Te))return;const i=j(this,Te);zt(this,Te,t),zt(this,jl,t.state),this.hasListeners()&&(i==null||i.removeObserver(this),t.addObserver(this))},Fy=function(t){Nn.batch(()=>{t.listeners&&this.listeners.forEach(i=>{i(j(this,Xn))}),j(this,$n).getQueryCache().notify({query:j(this,Te),type:"observerResultsUpdated"})})},by);function fE(r,t){return di(t.enabled,r)!==!1&&r.state.data===void 0&&!(r.state.status==="error"&&di(t.retryOnMount,r)===!1)}function dv(r,t){return fE(r,t)||r.state.data!==void 0&&op(r,t,t.refetchOnMount)}function op(r,t,i){if(di(t.enabled,r)!==!1&&_s(t.staleTime,r)!=="static"){const s=typeof i=="function"?i(r):i;return s==="always"||s!==!1&&em(r,t)}return!1}function pv(r,t,i,s){return(r!==t||di(s.enabled,r)===!1)&&(!i.suspense||r.state.status!=="error")&&em(r,i)}function em(r,t){return di(t.enabled,r)!==!1&&r.isStaleByTime(_s(t.staleTime,r))}function hE(r,t){return!Qd(r.getCurrentResult(),t)}var Wl,qi,Fn,ur,Wi,os,Ty,dE=(Ty=class extends zy{constructor(t){super();$t(this,Wi);$t(this,Wl);$t(this,qi);$t(this,Fn);$t(this,ur);zt(this,Wl,t.client),this.mutationId=t.mutationId,zt(this,Fn,t.mutationCache),zt(this,qi,[]),this.state=t.state||pE(),this.setOptions(t.options),this.scheduleGc()}setOptions(t){this.options=t,this.updateGcTime(this.options.gcTime)}get meta(){return this.options.meta}addObserver(t){j(this,qi).includes(t)||(j(this,qi).push(t),this.clearGcTimeout(),j(this,Fn).notify({type:"observerAdded",mutation:this,observer:t}))}removeObserver(t){zt(this,qi,j(this,qi).filter(i=>i!==t)),this.scheduleGc(),j(this,Fn).notify({type:"observerRemoved",mutation:this,observer:t})}optionalRemove(){j(this,qi).length||(this.state.status==="pending"?this.scheduleGc():j(this,Fn).remove(this))}continue(){var t;return((t=j(this,ur))==null?void 0:t.continue())??this.execute(this.state.variables)}async execute(t){var h,d,m,p,g,_,x,S,E,b,M,v,L,U,T,V,I,P;const i=()=>{Ee(this,Wi,os).call(this,{type:"continue"})},s={client:j(this,Wl),meta:this.options.meta,mutationKey:this.options.mutationKey};zt(this,ur,Py({fn:()=>this.options.mutationFn?this.options.mutationFn(t,s):Promise.reject(new Error("No mutationFn found")),onFail:(H,D)=>{Ee(this,Wi,os).call(this,{type:"failed",failureCount:H,error:D})},onPause:()=>{Ee(this,Wi,os).call(this,{type:"pause"})},onContinue:i,retry:this.options.retry??0,retryDelay:this.options.retryDelay,networkMode:this.options.networkMode,canRun:()=>j(this,Fn).canRun(this)}));const l=this.state.status==="pending",c=!j(this,ur).canStart();try{if(l)i();else{Ee(this,Wi,os).call(this,{type:"pending",variables:t,isPaused:c}),j(this,Fn).config.onMutate&&await j(this,Fn).config.onMutate(t,this,s);const D=await((d=(h=this.options).onMutate)==null?void 0:d.call(h,t,s));D!==this.state.context&&Ee(this,Wi,os).call(this,{type:"pending",context:D,variables:t,isPaused:c})}const H=await j(this,ur).start();return await((p=(m=j(this,Fn).config).onSuccess)==null?void 0:p.call(m,H,t,this.state.context,this,s)),await((_=(g=this.options).onSuccess)==null?void 0:_.call(g,H,t,this.state.context,s)),await((S=(x=j(this,Fn).config).onSettled)==null?void 0:S.call(x,H,null,this.state.variables,this.state.context,this,s)),await((b=(E=this.options).onSettled)==null?void 0:b.call(E,H,null,t,this.state.context,s)),Ee(this,Wi,os).call(this,{type:"success",data:H}),H}catch(H){try{await((v=(M=j(this,Fn).config).onError)==null?void 0:v.call(M,H,t,this.state.context,this,s))}catch(D){Promise.reject(D)}try{await((U=(L=this.options).onError)==null?void 0:U.call(L,H,t,this.state.context,s))}catch(D){Promise.reject(D)}try{await((V=(T=j(this,Fn).config).onSettled)==null?void 0:V.call(T,void 0,H,this.state.variables,this.state.context,this,s))}catch(D){Promise.reject(D)}try{await((P=(I=this.options).onSettled)==null?void 0:P.call(I,void 0,H,t,this.state.context,s))}catch(D){Promise.reject(D)}throw Ee(this,Wi,os).call(this,{type:"error",error:H}),H}finally{j(this,Fn).runNext(this)}}},Wl=new WeakMap,qi=new WeakMap,Fn=new WeakMap,ur=new WeakMap,Wi=new WeakSet,os=function(t){const i=s=>{switch(t.type){case"failed":return{...s,failureCount:t.failureCount,failureReason:t.error};case"pause":return{...s,isPaused:!0};case"continue":return{...s,isPaused:!1};case"pending":return{...s,context:t.context,data:void 0,failureCount:0,failureReason:null,error:null,isPaused:t.isPaused,status:"pending",variables:t.variables,submittedAt:Date.now()};case"success":return{...s,data:t.data,failureCount:0,failureReason:null,error:null,status:"success",isPaused:!1};case"error":return{...s,data:void 0,error:t.error,failureCount:s.failureCount+1,failureReason:t.error,isPaused:!1,status:"error"}}};this.state=i(this.state),Nn.batch(()=>{j(this,qi).forEach(s=>{s.onMutationUpdate(t)}),j(this,Fn).notify({mutation:this,type:"updated",action:t})})},Ty);function pE(){return{context:void 0,data:void 0,error:null,failureCount:0,failureReason:null,isPaused:!1,status:"idle",variables:void 0,submittedAt:0}}var Ta,zi,Yl,Ay,mE=(Ay=class extends Ql{constructor(t={}){super();$t(this,Ta);$t(this,zi);$t(this,Yl);this.config=t,zt(this,Ta,new Set),zt(this,zi,new Map),zt(this,Yl,0)}build(t,i,s){const l=new dE({client:t,mutationCache:this,mutationId:++hu(this,Yl)._,options:t.defaultMutationOptions(i),state:s});return this.add(l),l}add(t){j(this,Ta).add(t);const i=du(t);if(typeof i=="string"){const s=j(this,zi).get(i);s?s.push(t):j(this,zi).set(i,[t])}this.notify({type:"added",mutation:t})}remove(t){if(j(this,Ta).delete(t)){const i=du(t);if(typeof i=="string"){const s=j(this,zi).get(i);if(s)if(s.length>1){const l=s.indexOf(t);l!==-1&&s.splice(l,1)}else s[0]===t&&j(this,zi).delete(i)}}this.notify({type:"removed",mutation:t})}canRun(t){const i=du(t);if(typeof i=="string"){const s=j(this,zi).get(i),l=s==null?void 0:s.find(c=>c.state.status==="pending");return!l||l===t}else return!0}runNext(t){var s;const i=du(t);if(typeof i=="string"){const l=(s=j(this,zi).get(i))==null?void 0:s.find(c=>c!==t&&c.state.isPaused);return(l==null?void 0:l.continue())??Promise.resolve()}else return Promise.resolve()}clear(){Nn.batch(()=>{j(this,Ta).forEach(t=>{this.notify({type:"removed",mutation:t})}),j(this,Ta).clear(),j(this,zi).clear()})}getAll(){return Array.from(j(this,Ta))}find(t){const i={exact:!0,...t};return this.getAll().find(s=>ov(i,s))}findAll(t={}){return this.getAll().filter(i=>ov(t,i))}notify(t){Nn.batch(()=>{this.listeners.forEach(i=>{i(t)})})}resumePausedMutations(){const t=this.getAll().filter(i=>i.state.isPaused);return Nn.batch(()=>Promise.all(t.map(i=>i.continue().catch(ti))))}},Ta=new WeakMap,zi=new WeakMap,Yl=new WeakMap,Ay);function du(r){var t;return(t=r.options.scope)==null?void 0:t.id}var Yi,Ry,gE=(Ry=class extends Ql{constructor(t={}){super();$t(this,Yi);this.config=t,zt(this,Yi,new Map)}build(t,i,s){const l=i.queryKey,c=i.queryHash??$p(l,i);let h=this.get(c);return h||(h=new cE({client:t,queryKey:l,queryHash:c,options:t.defaultQueryOptions(i),state:s,defaultOptions:t.getQueryDefaults(l)}),this.add(h)),h}add(t){j(this,Yi).has(t.queryHash)||(j(this,Yi).set(t.queryHash,t),this.notify({type:"added",query:t}))}remove(t){const i=j(this,Yi).get(t.queryHash);i&&(t.destroy(),i===t&&j(this,Yi).delete(t.queryHash),this.notify({type:"removed",query:t}))}clear(){Nn.batch(()=>{this.getAll().forEach(t=>{this.remove(t)})})}get(t){return j(this,Yi).get(t)}getAll(){return[...j(this,Yi).values()]}find(t){const i={exact:!0,...t};return this.getAll().find(s=>rv(i,s))}findAll(t={}){const i=this.getAll();return Object.keys(t).length>0?i.filter(s=>rv(t,s)):i}notify(t){Nn.batch(()=>{this.listeners.forEach(i=>{i(t)})})}onFocus(){Nn.batch(()=>{this.getAll().forEach(t=>{t.onFocus()})})}onOnline(){Nn.batch(()=>{this.getAll().forEach(t=>{t.onOnline()})})}},Yi=new WeakMap,Ry),on,ps,ms,bo,To,gs,Ao,Ro,Cy,_E=(Cy=class{constructor(r={}){$t(this,on);$t(this,ps);$t(this,ms);$t(this,bo);$t(this,To);$t(this,gs);$t(this,Ao);$t(this,Ro);zt(this,on,r.queryCache||new gE),zt(this,ps,r.mutationCache||new mE),zt(this,ms,r.defaultOptions||{}),zt(this,bo,new Map),zt(this,To,new Map),zt(this,gs,0)}mount(){hu(this,gs)._++,j(this,gs)===1&&(zt(this,Ao,Jp.subscribe(async r=>{r&&(await this.resumePausedMutations(),j(this,on).onFocus())})),zt(this,Ro,ju.subscribe(async r=>{r&&(await this.resumePausedMutations(),j(this,on).onOnline())})))}unmount(){var r,t;hu(this,gs)._--,j(this,gs)===0&&((r=j(this,Ao))==null||r.call(this),zt(this,Ao,void 0),(t=j(this,Ro))==null||t.call(this),zt(this,Ro,void 0))}isFetching(r){return j(this,on).findAll({...r,fetchStatus:"fetching"}).length}isMutating(r){return j(this,ps).findAll({...r,status:"pending"}).length}getQueryData(r){var i;const t=this.defaultQueryOptions({queryKey:r});return(i=j(this,on).get(t.queryHash))==null?void 0:i.state.data}ensureQueryData(r){const t=this.defaultQueryOptions(r),i=j(this,on).build(this,t),s=i.state.data;return s===void 0?this.fetchQuery(r):(r.revalidateIfStale&&i.isStaleByTime(_s(t.staleTime,i))&&this.prefetchQuery(t),Promise.resolve(s))}getQueriesData(r){return j(this,on).findAll(r).map(({queryKey:t,state:i})=>{const s=i.data;return[t,s]})}setQueryData(r,t,i){const s=this.defaultQueryOptions({queryKey:r}),l=j(this,on).get(s.queryHash),c=l==null?void 0:l.state.data,h=KM(t,c);if(h!==void 0)return j(this,on).build(this,s).setData(h,{...i,manual:!0})}setQueriesData(r,t,i){return Nn.batch(()=>j(this,on).findAll(r).map(({queryKey:s})=>[s,this.setQueryData(s,t,i)]))}getQueryState(r){var i;const t=this.defaultQueryOptions({queryKey:r});return(i=j(this,on).get(t.queryHash))==null?void 0:i.state}removeQueries(r){const t=j(this,on);Nn.batch(()=>{t.findAll(r).forEach(i=>{t.remove(i)})})}resetQueries(r,t){const i=j(this,on);return Nn.batch(()=>(i.findAll(r).forEach(s=>{s.reset()}),this.refetchQueries({type:"active",...r},t)))}cancelQueries(r,t={}){const i={revert:!0,...t},s=Nn.batch(()=>j(this,on).findAll(r).map(l=>l.cancel(i)));return Promise.all(s).then(ti).catch(ti)}invalidateQueries(r,t={}){return Nn.batch(()=>(j(this,on).findAll(r).forEach(i=>{i.invalidate()}),(r==null?void 0:r.refetchType)==="none"?Promise.resolve():this.refetchQueries({...r,type:(r==null?void 0:r.refetchType)??(r==null?void 0:r.type)??"active"},t)))}refetchQueries(r,t={}){const i={...t,cancelRefetch:t.cancelRefetch??!0},s=Nn.batch(()=>j(this,on).findAll(r).filter(l=>!l.isDisabled()&&!l.isStatic()).map(l=>{let c=l.fetch(void 0,i);return i.throwOnError||(c=c.catch(ti)),l.state.fetchStatus==="paused"?Promise.resolve():c}));return Promise.all(s).then(ti)}fetchQuery(r){const t=this.defaultQueryOptions(r);t.retry===void 0&&(t.retry=!1);const i=j(this,on).build(this,t);return i.isStaleByTime(_s(t.staleTime,i))?i.fetch(t):Promise.resolve(i.state.data)}prefetchQuery(r){return this.fetchQuery(r).then(ti).catch(ti)}fetchInfiniteQuery(r){return r._type="infinite",this.fetchQuery(r)}prefetchInfiniteQuery(r){return this.fetchInfiniteQuery(r).then(ti).catch(ti)}ensureInfiniteQueryData(r){return r._type="infinite",this.ensureQueryData(r)}resumePausedMutations(){return ju.isOnline()?j(this,ps).resumePausedMutations():Promise.resolve()}getQueryCache(){return j(this,on)}getMutationCache(){return j(this,ps)}getDefaultOptions(){return j(this,ms)}setDefaultOptions(r){zt(this,ms,r)}setQueryDefaults(r,t){j(this,bo).set(Hl(r),{queryKey:r,defaultOptions:t})}getQueryDefaults(r){const t=[...j(this,bo).values()],i={};return t.forEach(s=>{Gl(r,s.queryKey)&&Object.assign(i,s.defaultOptions)}),i}setMutationDefaults(r,t){j(this,To).set(Hl(r),{mutationKey:r,defaultOptions:t})}getMutationDefaults(r){const t=[...j(this,To).values()],i={};return t.forEach(s=>{Gl(r,s.mutationKey)&&Object.assign(i,s.defaultOptions)}),i}defaultQueryOptions(r){if(r._defaulted)return r;const t={...j(this,ms).queries,...this.getQueryDefaults(r.queryKey),...r,_defaulted:!0};return t.queryHash||(t.queryHash=$p(t.queryKey,t)),t.refetchOnReconnect===void 0&&(t.refetchOnReconnect=t.networkMode!=="always"),t.throwOnError===void 0&&(t.throwOnError=!!t.suspense),!t.networkMode&&t.persister&&(t.networkMode="offlineFirst"),t.queryFn===tm&&(t.enabled=!1),t}defaultMutationOptions(r){return r!=null&&r._defaulted?r:{...j(this,ms).mutations,...(r==null?void 0:r.mutationKey)&&this.getMutationDefaults(r.mutationKey),...r,_defaulted:!0}}clear(){j(this,on).clear(),j(this,ps).clear()}},on=new WeakMap,ps=new WeakMap,ms=new WeakMap,bo=new WeakMap,To=new WeakMap,gs=new WeakMap,Ao=new WeakMap,Ro=new WeakMap,Cy),Hy=Pe.createContext(void 0),Gy=r=>{const t=Pe.useContext(Hy);if(!t)throw new Error("No QueryClient set, use QueryClientProvider to set one");return t},vE=({client:r,children:t})=>(Pe.useEffect(()=>(r.mount(),()=>{r.unmount()}),[r]),N.jsx(Hy.Provider,{value:r,children:t})),Vy=Pe.createContext(!1),yE=()=>Pe.useContext(Vy);Vy.Provider;function xE(){let r=!1;return{clearReset:()=>{r=!1},reset:()=>{r=!0},isReset:()=>r}}var SE=Pe.createContext(xE()),ME=()=>Pe.useContext(SE),EE=(r,t,i)=>{const s=i!=null&&i.state.error&&typeof r.throwOnError=="function"?Ly(r.throwOnError,[i.state.error,i]):r.throwOnError;(r.suspense||r.experimental_prefetchInRender||s)&&(t.isReset()||(r.retryOnMount=!1))},bE=r=>{Pe.useEffect(()=>{r.clearReset()},[r])},TE=({result:r,errorResetBoundary:t,throwOnError:i,query:s,suspense:l})=>r.isError&&!t.isReset()&&!r.isFetching&&s&&(l&&r.data===void 0||Ly(i,[r.error,s])),AE=r=>{if(r.suspense){const i=l=>l==="static"?l:Math.max(l??1e3,1e3),s=r.staleTime;r.staleTime=typeof s=="function"?(...l)=>i(s(...l)):i(s),typeof r.gcTime=="number"&&(r.gcTime=Math.max(r.gcTime,1e3))}},RE=(r,t)=>r.isLoading&&r.isFetching&&!t,CE=(r,t)=>(r==null?void 0:r.suspense)&&t.isPending,mv=(r,t,i)=>t.fetchOptimistic(r).catch(()=>{i.clearReset()});function wE(r,t,i){var S,E,b,M;const s=yE(),l=ME(),c=Gy(),h=c.defaultQueryOptions(r);(E=(S=c.getDefaultOptions().queries)==null?void 0:S._experimental_beforeQuery)==null||E.call(S,h);const d=c.getQueryCache().get(h.queryHash),m=r.subscribed!==!1;h._optimisticResults=s?"isRestoring":m?"optimistic":void 0,AE(h),EE(h,l,d),bE(l);const p=!c.getQueryCache().get(h.queryHash),[g]=Pe.useState(()=>new t(c,h)),_=g.getOptimisticResult(h),x=!s&&m;if(Pe.useSyncExternalStore(Pe.useCallback(v=>{const L=x?g.subscribe(Nn.batchCalls(v)):ti;return g.updateResult(),L},[g,x]),()=>g.getCurrentResult(),()=>g.getCurrentResult()),Pe.useEffect(()=>{g.setOptions(h)},[h,g]),CE(h,_))throw mv(h,g,l);if(TE({result:_,errorResetBoundary:l,throwOnError:h.throwOnError,query:d,suspense:h.suspense}))throw _.error;if((M=(b=c.getDefaultOptions().queries)==null?void 0:b._experimental_afterQuery)==null||M.call(b,h,_),h.experimental_prefetchInRender&&!Vl.isServer()&&RE(_,s)){const v=p?mv(h,g,l):d==null?void 0:d.promise;v==null||v.catch(ti).finally(()=>{g.updateResult()})}return h.notifyOnChangeProps?_:g.trackResult(_)}function DE(r,t){return wE(r,uE)}/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const UE=r=>r.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),ky=(...r)=>r.filter((t,i,s)=>!!t&&t.trim()!==""&&s.indexOf(t)===i).join(" ").trim();/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var NE={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const LE=Pe.forwardRef(({color:r="currentColor",size:t=24,strokeWidth:i=2,absoluteStrokeWidth:s,className:l="",children:c,iconNode:h,...d},m)=>Pe.createElement("svg",{ref:m,...NE,width:t,height:t,stroke:r,strokeWidth:s?Number(i)*24/Number(t):i,className:ky("lucide",l),...d},[...h.map(([p,g])=>Pe.createElement(p,g)),...Array.isArray(c)?c:[c]]));/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const nn=(r,t)=>{const i=Pe.forwardRef(({className:s,...l},c)=>Pe.createElement(LE,{ref:c,iconNode:t,className:ky(`lucide-${UE(r)}`,s),...l}));return i.displayName=`${r}`,i};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Xy=nn("Activity",[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jy=nn("Bell",[["path",{d:"M10.268 21a2 2 0 0 0 3.464 0",key:"vwvbt9"}],["path",{d:"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",key:"11g9vi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const OE=nn("BrainCircuit",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M9 13a4.5 4.5 0 0 0 3-4",key:"10igwf"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M12 13h4",key:"1ku699"}],["path",{d:"M12 18h6a2 2 0 0 1 2 2v1",key:"105ag5"}],["path",{d:"M12 8h8",key:"1lhi5i"}],["path",{d:"M16 8V5a2 2 0 0 1 2-2",key:"u6izg6"}],["circle",{cx:"16",cy:"13",r:".5",key:"ry7gng"}],["circle",{cx:"18",cy:"3",r:".5",key:"1aiba7"}],["circle",{cx:"20",cy:"21",r:".5",key:"yhc1fs"}],["circle",{cx:"20",cy:"8",r:".5",key:"1e43v0"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const PE=nn("Brain",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z",key:"ep3f8r"}],["path",{d:"M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4",key:"1p4c4q"}],["path",{d:"M17.599 6.5a3 3 0 0 0 .399-1.375",key:"tmeiqw"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M19.938 10.5a4 4 0 0 1 .585.396",key:"1qfode"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M19.967 17.484A4 4 0 0 1 18 18",key:"159ez6"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zE=nn("Check",[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const IE=nn("CircleCheck",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const BE=nn("CircleOff",[["path",{d:"m2 2 20 20",key:"1ooewy"}],["path",{d:"M8.35 2.69A10 10 0 0 1 21.3 15.65",key:"1pfsoa"}],["path",{d:"M19.08 19.08A10 10 0 1 1 4.92 4.92",key:"1ablyi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const FE=nn("CirclePause",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"10",x2:"10",y1:"15",y2:"9",key:"c1nkhi"}],["line",{x1:"14",x2:"14",y1:"15",y2:"9",key:"h65svq"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const HE=nn("ClipboardList",[["rect",{width:"8",height:"4",x:"8",y:"2",rx:"1",ry:"1",key:"tgr4d6"}],["path",{d:"M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",key:"116196"}],["path",{d:"M12 11h4",key:"1jrz19"}],["path",{d:"M12 16h4",key:"n85exb"}],["path",{d:"M8 11h.01",key:"1dfujw"}],["path",{d:"M8 16h.01",key:"18s6g9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const GE=nn("Clock",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["polyline",{points:"12 6 12 12 16 14",key:"68esgv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const VE=nn("Cpu",[["rect",{width:"16",height:"16",x:"4",y:"4",rx:"2",key:"14l7u7"}],["rect",{width:"6",height:"6",x:"9",y:"9",rx:"1",key:"5aljv4"}],["path",{d:"M15 2v2",key:"13l42r"}],["path",{d:"M15 20v2",key:"15mkzm"}],["path",{d:"M2 15h2",key:"1gxd5l"}],["path",{d:"M2 9h2",key:"1bbxkp"}],["path",{d:"M20 15h2",key:"19e6y8"}],["path",{d:"M20 9h2",key:"19tzq7"}],["path",{d:"M9 2v2",key:"165o2o"}],["path",{d:"M9 20v2",key:"i2bqo8"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const kE=nn("House",[["path",{d:"M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8",key:"5wwlr5"}],["path",{d:"M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"1d0kgt"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const XE=nn("KeyRound",[["path",{d:"M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",key:"1s6t7t"}],["circle",{cx:"16.5",cy:"7.5",r:".5",fill:"currentColor",key:"w0ekpg"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qy=nn("MessageSquare",[["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",key:"1lielz"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const jE=nn("MonitorCog",[["path",{d:"M12 17v4",key:"1riwvh"}],["path",{d:"m15.2 4.9-.9-.4",key:"12wd2u"}],["path",{d:"m15.2 7.1-.9.4",key:"1r2vl7"}],["path",{d:"m16.9 3.2-.4-.9",key:"3zbo91"}],["path",{d:"m16.9 8.8-.4.9",key:"1qr2dn"}],["path",{d:"m19.5 2.3-.4.9",key:"1rjrkq"}],["path",{d:"m19.5 9.7-.4-.9",key:"heryx5"}],["path",{d:"m21.7 4.5-.9.4",key:"17fqt1"}],["path",{d:"m21.7 7.5-.9-.4",key:"14zyni"}],["path",{d:"M22 13v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7",key:"1tnzv8"}],["path",{d:"M8 21h8",key:"1ev6f3"}],["circle",{cx:"18",cy:"6",r:"3",key:"1h7g24"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const qE=nn("Send",[["path",{d:"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",key:"1ffxy3"}],["path",{d:"m21.854 2.147-10.94 10.939",key:"12cjpa"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const WE=nn("Settings",[["path",{d:"M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",key:"1qme2f"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Wy=nn("ShieldAlert",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M12 16h.01",key:"1drbdi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Yy=nn("ShieldCheck",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const YE=nn("SlidersHorizontal",[["line",{x1:"21",x2:"14",y1:"4",y2:"4",key:"obuewd"}],["line",{x1:"10",x2:"3",y1:"4",y2:"4",key:"1q6298"}],["line",{x1:"21",x2:"12",y1:"12",y2:"12",key:"1iu8h1"}],["line",{x1:"8",x2:"3",y1:"12",y2:"12",key:"ntss68"}],["line",{x1:"21",x2:"16",y1:"20",y2:"20",key:"14d8ph"}],["line",{x1:"12",x2:"3",y1:"20",y2:"20",key:"m0wm8r"}],["line",{x1:"14",x2:"14",y1:"2",y2:"6",key:"14e1ph"}],["line",{x1:"8",x2:"8",y1:"10",y2:"14",key:"1i6ji0"}],["line",{x1:"16",x2:"16",y1:"18",y2:"22",key:"1lctlv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Qy=nn("TriangleAlert",[["path",{d:"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",key:"wmoenq"}],["path",{d:"M12 9v4",key:"juzpu7"}],["path",{d:"M12 17h.01",key:"p32p05"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const QE=nn("WifiOff",[["path",{d:"M12 20h.01",key:"zekei9"}],["path",{d:"M8.5 16.429a5 5 0 0 1 7 0",key:"1bycff"}],["path",{d:"M5 12.859a10 10 0 0 1 5.17-2.69",key:"1dl1wf"}],["path",{d:"M19 12.859a10 10 0 0 0-2.007-1.523",key:"4k23kn"}],["path",{d:"M2 8.82a15 15 0 0 1 4.177-2.643",key:"1grhjp"}],["path",{d:"M22 8.82a15 15 0 0 0-11.288-3.764",key:"z3jwby"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Zy=nn("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]);async function ZE(r="dashboard"){const i=await fetch(r==="display"?"/display/overview":"/api/ui/overview",{credentials:"include"});if(!i.ok)throw new Error(`Overview request failed: ${i.status}`);return i.json()}async function KE(r){const t=await fetch("/api/chat/send",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:r})});if(!t.ok)throw new Error(`Chat request failed: ${t.status}`);return t.json()}async function JE(r,t){const s=await fetch(`/api/approvals/${r}/${t==="approve"?"approve":"reject"}`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({})});if(!s.ok)throw new Error(`Approval ${t} failed: ${s.status}`)}function $E(r,t=!0){Pe.useEffect(()=>{if(!t||typeof EventSource>"u")return;const i=new EventSource("/api/ui/stream",{withCredentials:!0}),s=l=>{try{r(JSON.parse(l.data))}catch{}};for(const l of["status.changed","task.updated","approval.created","approval.resolved","notification.created","chat.updated","permission.changed","connection.changed","activity.updated"])i.addEventListener(l,s);return i.addEventListener("ui.snapshot",s),()=>i.close()},[t,r])}function t1({open:r,onClose:t}){const[i,s]=Pe.useState(""),[l,c]=Pe.useState([]),[h,d]=Pe.useState(!1);async function m(p){p.preventDefault();const g=i.trim();if(!(!g||h)){s(""),c(_=>[..._,{role:"user",text:g}]),d(!0);try{const _=await KE(g);c(x=>[...x,{role:"aegis",text:String(_.response||_.message||"Done.")}])}catch(_){c(x=>[...x,{role:"system",text:_ instanceof Error?_.message:String(_)}])}finally{d(!1)}}}return N.jsxs("aside",{className:"chat-drawer","data-open":r,"aria-hidden":!r,children:[N.jsxs("div",{className:"panel__header",style:{padding:"16px",borderBottom:"1px solid var(--aegis-border)",margin:0},children:[N.jsxs("h2",{children:[N.jsx(qy,{size:18,"aria-hidden":"true"})," Chat"]}),N.jsx("button",{className:"icon-button",onClick:t,title:"Close chat",children:N.jsx(Zy,{size:16,"aria-hidden":"true"})})]}),N.jsxs("div",{className:"chat-log",children:[l.length===0?N.jsx("div",{className:"muted",children:"Chat is ready. Messages are sent through the existing AEGIS chat API."}):null,l.map((p,g)=>N.jsx("div",{className:"list-row",style:{marginBottom:8},children:N.jsxs("div",{children:[N.jsx("strong",{children:p.role}),N.jsx("div",{children:p.text})]})},`${p.role}-${g}`))]}),N.jsxs("form",{className:"chat-form",onSubmit:m,children:[N.jsx("textarea",{value:i,onChange:p=>s(p.target.value),"aria-label":"Message"}),N.jsx("button",{className:"icon-button",title:"Send message",disabled:h,children:N.jsx(qE,{size:16,"aria-hidden":"true"})})]})]})}function $s({generatedAt:r,sourceUpdatedAt:t,stale:i=!1}){const s=Math.max(0,r-t),l=i?`STALE ${gv(s)}`:s<15e3?"LIVE":`${gv(s)} ago`;return N.jsx("span",{className:"freshness","data-stale":i,children:l})}function gv(r){const t=Math.round(r/1e3);if(t<60)return`${t}s`;const i=Math.round(t/60);return i<60?`${i}m`:`${Math.round(i/60)}h`}function fr({status:r,detail:t}){const i=(r||"UNKNOWN").toUpperCase(),s=i==="ONLINE"?IE:i==="DISABLED"||i==="UNCONFIGURED"?FE:i==="OFFLINE"?BE:Qy;return N.jsxs("span",{className:"status-badge","data-status":i,title:t||i,children:[N.jsx(s,{size:14,"aria-hidden":"true"}),i]})}function e1({overview:r}){return N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsxs("div",{children:[N.jsx("h2",{children:"Activity"}),N.jsx("div",{className:"muted",children:"Normalized recent signals from the overview service."})]})}),N.jsx("div",{className:"grid",children:(r.attention.data.items||[]).map(t=>N.jsxs("div",{className:"list-row",children:[N.jsxs("div",{children:[N.jsx("strong",{children:t.title}),N.jsx("div",{className:"muted",children:t.message})]}),N.jsx("span",{className:"mono muted",children:t.kind})]},t.id))})]})}function n1({approval:r,readonly:t=!1}){const[i,s]=Pe.useState(""),[l,c]=Pe.useState("");async function h(d){s(d),c("");try{await JE(r.approval_id,d)}catch(m){c(m instanceof Error?m.message:String(m))}finally{s("")}}return N.jsxs("article",{className:"approval-card",children:[N.jsxs("div",{className:"panel__header",children:[N.jsxs("div",{children:[N.jsx("strong",{children:r.summary||r.tool_name||"Approval required"}),N.jsx("div",{className:"muted mono",children:r.approval_id})]}),N.jsxs("span",{className:"status-badge","data-status":"WAITING",children:[N.jsx(Wy,{size:14,"aria-hidden":"true"}),r.risk||"risk"]})]}),N.jsx("div",{className:"muted",children:r.reason||"Review the requested action before allowing it to continue."}),N.jsxs("div",{className:"stat-grid",children:[N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Capability"}),N.jsx("b",{className:"mono",style:{fontSize:14},children:r.capability_id})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Target"}),N.jsx("b",{style:{fontSize:14},children:r.target||"Not specified"})]})]}),r.preview?N.jsx("pre",{className:"panel mono",style:{whiteSpace:"pre-wrap",margin:0},children:r.preview}):null,l?N.jsx("div",{className:"attention-item","data-severity":"critical",children:l}):null,t?null:N.jsxs("div",{className:"approval-card__actions",children:[N.jsxs("button",{className:"primary-button",onClick:()=>h("approve"),disabled:!!i,children:[N.jsx(zE,{size:16,"aria-hidden":"true"})," ",i==="approve"?"Approving":"Approve"]}),N.jsxs("button",{className:"danger-button",onClick:()=>h("reject"),disabled:!!i,children:[N.jsx(Zy,{size:16,"aria-hidden":"true"})," ",i==="reject"?"Rejecting":"Reject"]})]})]})}function i1({overview:r}){const t=r.approvals.data.pending||[];return N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsxs("div",{children:[N.jsx("h2",{children:"Approvals"}),N.jsx("div",{className:"muted",children:"Pending, high-risk, and expiring action requests."})]}),N.jsx($s,{generatedAt:r.approvals.generated_at,sourceUpdatedAt:r.approvals.source_updated_at,stale:r.approvals.stale})]}),N.jsxs("div",{className:"grid",children:[t.map(i=>N.jsx(n1,{approval:i},i.approval_id)),t.length?null:N.jsx("div",{className:"attention-item","data-severity":"normal",children:"No pending approvals."})]})]})}function a1({items:r}){return r.length?N.jsx("section",{className:"attention-strip","aria-label":"Attention",children:r.slice(0,6).map(t=>{const i=t.kind==="approval"?Wy:t.kind==="server"?QE:Qy;return N.jsxs("article",{className:"attention-item","data-severity":t.severity,children:[N.jsxs("div",{children:[N.jsx("strong",{children:t.title}),N.jsx("div",{className:"muted",children:t.message||t.recovery_hint||"Review this item."})]}),N.jsx(i,{size:20,"aria-label":t.severity})]},t.id)})}):N.jsx("section",{className:"attention-strip","aria-label":"Attention",children:N.jsxs("div",{className:"attention-item","data-severity":"normal",children:[N.jsxs("div",{children:[N.jsx("strong",{children:"No immediate attention required"}),N.jsx("div",{className:"muted",children:"All current UI signals are within normal bounds."})]}),N.jsx(jy,{size:18,"aria-hidden":"true"})]})})}/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const nm="171",s1=0,_v=1,r1=2,Ky=1,o1=2,Ea=3,xs=0,ei=1,Aa=2,vs=0,fo=1,vv=2,yv=3,xv=4,l1=5,Zs=100,c1=101,u1=102,f1=103,h1=104,d1=200,p1=201,m1=202,g1=203,lp=204,cp=205,_1=206,v1=207,y1=208,x1=209,S1=210,M1=211,E1=212,b1=213,T1=214,up=0,fp=1,hp=2,Co=3,dp=4,pp=5,mp=6,gp=7,Jy=0,A1=1,R1=2,ys=0,C1=1,w1=2,D1=3,U1=4,N1=5,L1=6,O1=7,$y=300,wo=301,Do=302,_p=303,vp=304,Ku=306,yp=1e3,tr=1001,xp=1002,Fi=1003,P1=1004,pu=1005,Zi=1006,md=1007,er=1008,Da=1009,tx=1010,ex=1011,kl=1012,im=1013,hr=1014,Ra=1015,Zl=1016,am=1017,sm=1018,Uo=1020,nx=35902,ix=1021,ax=1022,Bi=1023,sx=1024,rx=1025,ho=1026,No=1027,ox=1028,rm=1029,lx=1030,om=1031,lm=1033,Fu=33776,Hu=33777,Gu=33778,Vu=33779,Sp=35840,Mp=35841,Ep=35842,bp=35843,Tp=36196,Ap=37492,Rp=37496,Cp=37808,wp=37809,Dp=37810,Up=37811,Np=37812,Lp=37813,Op=37814,Pp=37815,zp=37816,Ip=37817,Bp=37818,Fp=37819,Hp=37820,Gp=37821,ku=36492,Vp=36494,kp=36495,cx=36283,Xp=36284,jp=36285,qp=36286,z1=3200,I1=3201,B1=0,F1=1,ls="",Ai="srgb",Lo="srgb-linear",qu="linear",je="srgb",Yr=7680,Sv=519,H1=512,G1=513,V1=514,ux=515,k1=516,X1=517,j1=518,q1=519,Mv=35044,Ev="300 es",Ca=2e3,Wu=2001;class Po{addEventListener(t,i){this._listeners===void 0&&(this._listeners={});const s=this._listeners;s[t]===void 0&&(s[t]=[]),s[t].indexOf(i)===-1&&s[t].push(i)}hasEventListener(t,i){if(this._listeners===void 0)return!1;const s=this._listeners;return s[t]!==void 0&&s[t].indexOf(i)!==-1}removeEventListener(t,i){if(this._listeners===void 0)return;const l=this._listeners[t];if(l!==void 0){const c=l.indexOf(i);c!==-1&&l.splice(c,1)}}dispatchEvent(t){if(this._listeners===void 0)return;const s=this._listeners[t.type];if(s!==void 0){t.target=this;const l=s.slice(0);for(let c=0,h=l.length;c<h;c++)l[c].call(this,t);t.target=null}}}const In=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],gd=Math.PI/180,Wp=180/Math.PI;function Kl(){const r=Math.random()*4294967295|0,t=Math.random()*4294967295|0,i=Math.random()*4294967295|0,s=Math.random()*4294967295|0;return(In[r&255]+In[r>>8&255]+In[r>>16&255]+In[r>>24&255]+"-"+In[t&255]+In[t>>8&255]+"-"+In[t>>16&15|64]+In[t>>24&255]+"-"+In[i&63|128]+In[i>>8&255]+"-"+In[i>>16&255]+In[i>>24&255]+In[s&255]+In[s>>8&255]+In[s>>16&255]+In[s>>24&255]).toLowerCase()}function _e(r,t,i){return Math.max(t,Math.min(i,r))}function W1(r,t){return(r%t+t)%t}function _d(r,t,i){return(1-i)*r+i*t}function Dl(r,t){switch(t.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function Jn(r,t){switch(t.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}class Ae{constructor(t=0,i=0){Ae.prototype.isVector2=!0,this.x=t,this.y=i}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,i){return this.x=t,this.y=i,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const i=this.x,s=this.y,l=t.elements;return this.x=l[0]*i+l[3]*s+l[6],this.y=l[1]*i+l[4]*s+l[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,i){return this.x=_e(this.x,t.x,i.x),this.y=_e(this.y,t.y,i.y),this}clampScalar(t,i){return this.x=_e(this.x,t,i),this.y=_e(this.y,t,i),this}clampLength(t,i){const s=this.length();return this.divideScalar(s||1).multiplyScalar(_e(s,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const i=Math.sqrt(this.lengthSq()*t.lengthSq());if(i===0)return Math.PI/2;const s=this.dot(t)/i;return Math.acos(_e(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const i=this.x-t.x,s=this.y-t.y;return i*i+s*s}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this}lerpVectors(t,i,s){return this.x=t.x+(i.x-t.x)*s,this.y=t.y+(i.y-t.y)*s,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this}rotateAround(t,i){const s=Math.cos(i),l=Math.sin(i),c=this.x-t.x,h=this.y-t.y;return this.x=c*s-h*l+t.x,this.y=c*l+h*s+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class ue{constructor(t,i,s,l,c,h,d,m,p){ue.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,i,s,l,c,h,d,m,p)}set(t,i,s,l,c,h,d,m,p){const g=this.elements;return g[0]=t,g[1]=l,g[2]=d,g[3]=i,g[4]=c,g[5]=m,g[6]=s,g[7]=h,g[8]=p,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const i=this.elements,s=t.elements;return i[0]=s[0],i[1]=s[1],i[2]=s[2],i[3]=s[3],i[4]=s[4],i[5]=s[5],i[6]=s[6],i[7]=s[7],i[8]=s[8],this}extractBasis(t,i,s){return t.setFromMatrix3Column(this,0),i.setFromMatrix3Column(this,1),s.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const i=t.elements;return this.set(i[0],i[4],i[8],i[1],i[5],i[9],i[2],i[6],i[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,i){const s=t.elements,l=i.elements,c=this.elements,h=s[0],d=s[3],m=s[6],p=s[1],g=s[4],_=s[7],x=s[2],S=s[5],E=s[8],b=l[0],M=l[3],v=l[6],L=l[1],U=l[4],T=l[7],V=l[2],I=l[5],P=l[8];return c[0]=h*b+d*L+m*V,c[3]=h*M+d*U+m*I,c[6]=h*v+d*T+m*P,c[1]=p*b+g*L+_*V,c[4]=p*M+g*U+_*I,c[7]=p*v+g*T+_*P,c[2]=x*b+S*L+E*V,c[5]=x*M+S*U+E*I,c[8]=x*v+S*T+E*P,this}multiplyScalar(t){const i=this.elements;return i[0]*=t,i[3]*=t,i[6]*=t,i[1]*=t,i[4]*=t,i[7]*=t,i[2]*=t,i[5]*=t,i[8]*=t,this}determinant(){const t=this.elements,i=t[0],s=t[1],l=t[2],c=t[3],h=t[4],d=t[5],m=t[6],p=t[7],g=t[8];return i*h*g-i*d*p-s*c*g+s*d*m+l*c*p-l*h*m}invert(){const t=this.elements,i=t[0],s=t[1],l=t[2],c=t[3],h=t[4],d=t[5],m=t[6],p=t[7],g=t[8],_=g*h-d*p,x=d*m-g*c,S=p*c-h*m,E=i*_+s*x+l*S;if(E===0)return this.set(0,0,0,0,0,0,0,0,0);const b=1/E;return t[0]=_*b,t[1]=(l*p-g*s)*b,t[2]=(d*s-l*h)*b,t[3]=x*b,t[4]=(g*i-l*m)*b,t[5]=(l*c-d*i)*b,t[6]=S*b,t[7]=(s*m-p*i)*b,t[8]=(h*i-s*c)*b,this}transpose(){let t;const i=this.elements;return t=i[1],i[1]=i[3],i[3]=t,t=i[2],i[2]=i[6],i[6]=t,t=i[5],i[5]=i[7],i[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const i=this.elements;return t[0]=i[0],t[1]=i[3],t[2]=i[6],t[3]=i[1],t[4]=i[4],t[5]=i[7],t[6]=i[2],t[7]=i[5],t[8]=i[8],this}setUvTransform(t,i,s,l,c,h,d){const m=Math.cos(c),p=Math.sin(c);return this.set(s*m,s*p,-s*(m*h+p*d)+h+t,-l*p,l*m,-l*(-p*h+m*d)+d+i,0,0,1),this}scale(t,i){return this.premultiply(vd.makeScale(t,i)),this}rotate(t){return this.premultiply(vd.makeRotation(-t)),this}translate(t,i){return this.premultiply(vd.makeTranslation(t,i)),this}makeTranslation(t,i){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,i,0,0,1),this}makeRotation(t){const i=Math.cos(t),s=Math.sin(t);return this.set(i,-s,0,s,i,0,0,0,1),this}makeScale(t,i){return this.set(t,0,0,0,i,0,0,0,1),this}equals(t){const i=this.elements,s=t.elements;for(let l=0;l<9;l++)if(i[l]!==s[l])return!1;return!0}fromArray(t,i=0){for(let s=0;s<9;s++)this.elements[s]=t[s+i];return this}toArray(t=[],i=0){const s=this.elements;return t[i]=s[0],t[i+1]=s[1],t[i+2]=s[2],t[i+3]=s[3],t[i+4]=s[4],t[i+5]=s[5],t[i+6]=s[6],t[i+7]=s[7],t[i+8]=s[8],t}clone(){return new this.constructor().fromArray(this.elements)}}const vd=new ue;function fx(r){for(let t=r.length-1;t>=0;--t)if(r[t]>=65535)return!0;return!1}function Yu(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function Y1(){const r=Yu("canvas");return r.style.display="block",r}const bv={};function lo(r){r in bv||(bv[r]=!0,console.warn(r))}function Q1(r,t,i){return new Promise(function(s,l){function c(){switch(r.clientWaitSync(t,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:l();break;case r.TIMEOUT_EXPIRED:setTimeout(c,i);break;default:s()}}setTimeout(c,i)})}function Z1(r){const t=r.elements;t[2]=.5*t[2]+.5*t[3],t[6]=.5*t[6]+.5*t[7],t[10]=.5*t[10]+.5*t[11],t[14]=.5*t[14]+.5*t[15]}function K1(r){const t=r.elements;t[11]===-1?(t[10]=-t[10]-1,t[14]=-t[14]):(t[10]=-t[10],t[14]=-t[14]+1)}const Tv=new ue().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Av=new ue().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function J1(){const r={enabled:!0,workingColorSpace:Lo,spaces:{},convert:function(l,c,h){return this.enabled===!1||c===h||!c||!h||(this.spaces[c].transfer===je&&(l.r=wa(l.r),l.g=wa(l.g),l.b=wa(l.b)),this.spaces[c].primaries!==this.spaces[h].primaries&&(l.applyMatrix3(this.spaces[c].toXYZ),l.applyMatrix3(this.spaces[h].fromXYZ)),this.spaces[h].transfer===je&&(l.r=po(l.r),l.g=po(l.g),l.b=po(l.b))),l},fromWorkingColorSpace:function(l,c){return this.convert(l,this.workingColorSpace,c)},toWorkingColorSpace:function(l,c){return this.convert(l,c,this.workingColorSpace)},getPrimaries:function(l){return this.spaces[l].primaries},getTransfer:function(l){return l===ls?qu:this.spaces[l].transfer},getLuminanceCoefficients:function(l,c=this.workingColorSpace){return l.fromArray(this.spaces[c].luminanceCoefficients)},define:function(l){Object.assign(this.spaces,l)},_getMatrix:function(l,c,h){return l.copy(this.spaces[c].toXYZ).multiply(this.spaces[h].fromXYZ)},_getDrawingBufferColorSpace:function(l){return this.spaces[l].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(l=this.workingColorSpace){return this.spaces[l].workingColorSpaceConfig.unpackColorSpace}},t=[.64,.33,.3,.6,.15,.06],i=[.2126,.7152,.0722],s=[.3127,.329];return r.define({[Lo]:{primaries:t,whitePoint:s,transfer:qu,toXYZ:Tv,fromXYZ:Av,luminanceCoefficients:i,workingColorSpaceConfig:{unpackColorSpace:Ai},outputColorSpaceConfig:{drawingBufferColorSpace:Ai}},[Ai]:{primaries:t,whitePoint:s,transfer:je,toXYZ:Tv,fromXYZ:Av,luminanceCoefficients:i,outputColorSpaceConfig:{drawingBufferColorSpace:Ai}}}),r}const Ne=J1();function wa(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function po(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}let Qr;class $1{static getDataURL(t){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let i;if(t instanceof HTMLCanvasElement)i=t;else{Qr===void 0&&(Qr=Yu("canvas")),Qr.width=t.width,Qr.height=t.height;const s=Qr.getContext("2d");t instanceof ImageData?s.putImageData(t,0,0):s.drawImage(t,0,0,t.width,t.height),i=Qr}return i.width>2048||i.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",t),i.toDataURL("image/jpeg",.6)):i.toDataURL("image/png")}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const i=Yu("canvas");i.width=t.width,i.height=t.height;const s=i.getContext("2d");s.drawImage(t,0,0,t.width,t.height);const l=s.getImageData(0,0,t.width,t.height),c=l.data;for(let h=0;h<c.length;h++)c[h]=wa(c[h]/255)*255;return s.putImageData(l,0,0),i}else if(t.data){const i=t.data.slice(0);for(let s=0;s<i.length;s++)i instanceof Uint8Array||i instanceof Uint8ClampedArray?i[s]=Math.floor(wa(i[s]/255)*255):i[s]=wa(i[s]);return{data:i,width:t.width,height:t.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let tb=0;class hx{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:tb++}),this.uuid=Kl(),this.data=t,this.dataReady=!0,this.version=0}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const i=t===void 0||typeof t=="string";if(!i&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const s={uuid:this.uuid,url:""},l=this.data;if(l!==null){let c;if(Array.isArray(l)){c=[];for(let h=0,d=l.length;h<d;h++)l[h].isDataTexture?c.push(yd(l[h].image)):c.push(yd(l[h]))}else c=yd(l);s.url=c}return i||(t.images[this.uuid]=s),s}}function yd(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?$1.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let eb=0;class ni extends Po{constructor(t=ni.DEFAULT_IMAGE,i=ni.DEFAULT_MAPPING,s=tr,l=tr,c=Zi,h=er,d=Bi,m=Da,p=ni.DEFAULT_ANISOTROPY,g=ls){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:eb++}),this.uuid=Kl(),this.name="",this.source=new hx(t),this.mipmaps=[],this.mapping=i,this.channel=0,this.wrapS=s,this.wrapT=l,this.magFilter=c,this.minFilter=h,this.anisotropy=p,this.format=d,this.internalFormat=null,this.type=m,this.offset=new Ae(0,0),this.repeat=new Ae(1,1),this.center=new Ae(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ue,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=g,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(t=null){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}toJSON(t){const i=t===void 0||typeof t=="string";if(!i&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const s={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(s.userData=this.userData),i||(t.textures[this.uuid]=s),s}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==$y)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case yp:t.x=t.x-Math.floor(t.x);break;case tr:t.x=t.x<0?0:1;break;case xp:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case yp:t.y=t.y-Math.floor(t.y);break;case tr:t.y=t.y<0?0:1;break;case xp:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}ni.DEFAULT_IMAGE=null;ni.DEFAULT_MAPPING=$y;ni.DEFAULT_ANISOTROPY=1;class qe{constructor(t=0,i=0,s=0,l=1){qe.prototype.isVector4=!0,this.x=t,this.y=i,this.z=s,this.w=l}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,i,s,l){return this.x=t,this.y=i,this.z=s,this.w=l,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;case 2:this.z=i;break;case 3:this.w=i;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this.z=t.z+i.z,this.w=t.w+i.w,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this.z+=t.z*i,this.w+=t.w*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this.z=t.z-i.z,this.w=t.w-i.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const i=this.x,s=this.y,l=this.z,c=this.w,h=t.elements;return this.x=h[0]*i+h[4]*s+h[8]*l+h[12]*c,this.y=h[1]*i+h[5]*s+h[9]*l+h[13]*c,this.z=h[2]*i+h[6]*s+h[10]*l+h[14]*c,this.w=h[3]*i+h[7]*s+h[11]*l+h[15]*c,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const i=Math.sqrt(1-t.w*t.w);return i<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/i,this.y=t.y/i,this.z=t.z/i),this}setAxisAngleFromRotationMatrix(t){let i,s,l,c;const m=t.elements,p=m[0],g=m[4],_=m[8],x=m[1],S=m[5],E=m[9],b=m[2],M=m[6],v=m[10];if(Math.abs(g-x)<.01&&Math.abs(_-b)<.01&&Math.abs(E-M)<.01){if(Math.abs(g+x)<.1&&Math.abs(_+b)<.1&&Math.abs(E+M)<.1&&Math.abs(p+S+v-3)<.1)return this.set(1,0,0,0),this;i=Math.PI;const U=(p+1)/2,T=(S+1)/2,V=(v+1)/2,I=(g+x)/4,P=(_+b)/4,H=(E+M)/4;return U>T&&U>V?U<.01?(s=0,l=.707106781,c=.707106781):(s=Math.sqrt(U),l=I/s,c=P/s):T>V?T<.01?(s=.707106781,l=0,c=.707106781):(l=Math.sqrt(T),s=I/l,c=H/l):V<.01?(s=.707106781,l=.707106781,c=0):(c=Math.sqrt(V),s=P/c,l=H/c),this.set(s,l,c,i),this}let L=Math.sqrt((M-E)*(M-E)+(_-b)*(_-b)+(x-g)*(x-g));return Math.abs(L)<.001&&(L=1),this.x=(M-E)/L,this.y=(_-b)/L,this.z=(x-g)/L,this.w=Math.acos((p+S+v-1)/2),this}setFromMatrixPosition(t){const i=t.elements;return this.x=i[12],this.y=i[13],this.z=i[14],this.w=i[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,i){return this.x=_e(this.x,t.x,i.x),this.y=_e(this.y,t.y,i.y),this.z=_e(this.z,t.z,i.z),this.w=_e(this.w,t.w,i.w),this}clampScalar(t,i){return this.x=_e(this.x,t,i),this.y=_e(this.y,t,i),this.z=_e(this.z,t,i),this.w=_e(this.w,t,i),this}clampLength(t,i){const s=this.length();return this.divideScalar(s||1).multiplyScalar(_e(s,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this.z+=(t.z-this.z)*i,this.w+=(t.w-this.w)*i,this}lerpVectors(t,i,s){return this.x=t.x+(i.x-t.x)*s,this.y=t.y+(i.y-t.y)*s,this.z=t.z+(i.z-t.z)*s,this.w=t.w+(i.w-t.w)*s,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this.z=t[i+2],this.w=t[i+3],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t[i+2]=this.z,t[i+3]=this.w,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this.z=t.getZ(i),this.w=t.getW(i),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class nb extends Po{constructor(t=1,i=1,s={}){super(),this.isRenderTarget=!0,this.width=t,this.height=i,this.depth=1,this.scissor=new qe(0,0,t,i),this.scissorTest=!1,this.viewport=new qe(0,0,t,i);const l={width:t,height:i,depth:1};s=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Zi,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},s);const c=new ni(l,s.mapping,s.wrapS,s.wrapT,s.magFilter,s.minFilter,s.format,s.type,s.anisotropy,s.colorSpace);c.flipY=!1,c.generateMipmaps=s.generateMipmaps,c.internalFormat=s.internalFormat,this.textures=[];const h=s.count;for(let d=0;d<h;d++)this.textures[d]=c.clone(),this.textures[d].isRenderTargetTexture=!0;this.depthBuffer=s.depthBuffer,this.stencilBuffer=s.stencilBuffer,this.resolveDepthBuffer=s.resolveDepthBuffer,this.resolveStencilBuffer=s.resolveStencilBuffer,this.depthTexture=s.depthTexture,this.samples=s.samples}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}setSize(t,i,s=1){if(this.width!==t||this.height!==i||this.depth!==s){this.width=t,this.height=i,this.depth=s;for(let l=0,c=this.textures.length;l<c;l++)this.textures[l].image.width=t,this.textures[l].image.height=i,this.textures[l].image.depth=s;this.dispose()}this.viewport.set(0,0,t,i),this.scissor.set(0,0,t,i)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let s=0,l=t.textures.length;s<l;s++)this.textures[s]=t.textures[s].clone(),this.textures[s].isRenderTargetTexture=!0;const i=Object.assign({},t.texture.image);return this.texture.source=new hx(i),this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class dr extends nb{constructor(t=1,i=1,s={}){super(t,i,s),this.isWebGLRenderTarget=!0}}class dx extends ni{constructor(t=null,i=1,s=1,l=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:i,height:s,depth:l},this.magFilter=Fi,this.minFilter=Fi,this.wrapR=tr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class ib extends ni{constructor(t=null,i=1,s=1,l=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:i,height:s,depth:l},this.magFilter=Fi,this.minFilter=Fi,this.wrapR=tr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Jl{constructor(t=0,i=0,s=0,l=1){this.isQuaternion=!0,this._x=t,this._y=i,this._z=s,this._w=l}static slerpFlat(t,i,s,l,c,h,d){let m=s[l+0],p=s[l+1],g=s[l+2],_=s[l+3];const x=c[h+0],S=c[h+1],E=c[h+2],b=c[h+3];if(d===0){t[i+0]=m,t[i+1]=p,t[i+2]=g,t[i+3]=_;return}if(d===1){t[i+0]=x,t[i+1]=S,t[i+2]=E,t[i+3]=b;return}if(_!==b||m!==x||p!==S||g!==E){let M=1-d;const v=m*x+p*S+g*E+_*b,L=v>=0?1:-1,U=1-v*v;if(U>Number.EPSILON){const V=Math.sqrt(U),I=Math.atan2(V,v*L);M=Math.sin(M*I)/V,d=Math.sin(d*I)/V}const T=d*L;if(m=m*M+x*T,p=p*M+S*T,g=g*M+E*T,_=_*M+b*T,M===1-d){const V=1/Math.sqrt(m*m+p*p+g*g+_*_);m*=V,p*=V,g*=V,_*=V}}t[i]=m,t[i+1]=p,t[i+2]=g,t[i+3]=_}static multiplyQuaternionsFlat(t,i,s,l,c,h){const d=s[l],m=s[l+1],p=s[l+2],g=s[l+3],_=c[h],x=c[h+1],S=c[h+2],E=c[h+3];return t[i]=d*E+g*_+m*S-p*x,t[i+1]=m*E+g*x+p*_-d*S,t[i+2]=p*E+g*S+d*x-m*_,t[i+3]=g*E-d*_-m*x-p*S,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,i,s,l){return this._x=t,this._y=i,this._z=s,this._w=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,i=!0){const s=t._x,l=t._y,c=t._z,h=t._order,d=Math.cos,m=Math.sin,p=d(s/2),g=d(l/2),_=d(c/2),x=m(s/2),S=m(l/2),E=m(c/2);switch(h){case"XYZ":this._x=x*g*_+p*S*E,this._y=p*S*_-x*g*E,this._z=p*g*E+x*S*_,this._w=p*g*_-x*S*E;break;case"YXZ":this._x=x*g*_+p*S*E,this._y=p*S*_-x*g*E,this._z=p*g*E-x*S*_,this._w=p*g*_+x*S*E;break;case"ZXY":this._x=x*g*_-p*S*E,this._y=p*S*_+x*g*E,this._z=p*g*E+x*S*_,this._w=p*g*_-x*S*E;break;case"ZYX":this._x=x*g*_-p*S*E,this._y=p*S*_+x*g*E,this._z=p*g*E-x*S*_,this._w=p*g*_+x*S*E;break;case"YZX":this._x=x*g*_+p*S*E,this._y=p*S*_+x*g*E,this._z=p*g*E-x*S*_,this._w=p*g*_-x*S*E;break;case"XZY":this._x=x*g*_-p*S*E,this._y=p*S*_-x*g*E,this._z=p*g*E+x*S*_,this._w=p*g*_+x*S*E;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+h)}return i===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,i){const s=i/2,l=Math.sin(s);return this._x=t.x*l,this._y=t.y*l,this._z=t.z*l,this._w=Math.cos(s),this._onChangeCallback(),this}setFromRotationMatrix(t){const i=t.elements,s=i[0],l=i[4],c=i[8],h=i[1],d=i[5],m=i[9],p=i[2],g=i[6],_=i[10],x=s+d+_;if(x>0){const S=.5/Math.sqrt(x+1);this._w=.25/S,this._x=(g-m)*S,this._y=(c-p)*S,this._z=(h-l)*S}else if(s>d&&s>_){const S=2*Math.sqrt(1+s-d-_);this._w=(g-m)/S,this._x=.25*S,this._y=(l+h)/S,this._z=(c+p)/S}else if(d>_){const S=2*Math.sqrt(1+d-s-_);this._w=(c-p)/S,this._x=(l+h)/S,this._y=.25*S,this._z=(m+g)/S}else{const S=2*Math.sqrt(1+_-s-d);this._w=(h-l)/S,this._x=(c+p)/S,this._y=(m+g)/S,this._z=.25*S}return this._onChangeCallback(),this}setFromUnitVectors(t,i){let s=t.dot(i)+1;return s<Number.EPSILON?(s=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=s):(this._x=0,this._y=-t.z,this._z=t.y,this._w=s)):(this._x=t.y*i.z-t.z*i.y,this._y=t.z*i.x-t.x*i.z,this._z=t.x*i.y-t.y*i.x,this._w=s),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(_e(this.dot(t),-1,1)))}rotateTowards(t,i){const s=this.angleTo(t);if(s===0)return this;const l=Math.min(1,i/s);return this.slerp(t,l),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,i){const s=t._x,l=t._y,c=t._z,h=t._w,d=i._x,m=i._y,p=i._z,g=i._w;return this._x=s*g+h*d+l*p-c*m,this._y=l*g+h*m+c*d-s*p,this._z=c*g+h*p+s*m-l*d,this._w=h*g-s*d-l*m-c*p,this._onChangeCallback(),this}slerp(t,i){if(i===0)return this;if(i===1)return this.copy(t);const s=this._x,l=this._y,c=this._z,h=this._w;let d=h*t._w+s*t._x+l*t._y+c*t._z;if(d<0?(this._w=-t._w,this._x=-t._x,this._y=-t._y,this._z=-t._z,d=-d):this.copy(t),d>=1)return this._w=h,this._x=s,this._y=l,this._z=c,this;const m=1-d*d;if(m<=Number.EPSILON){const S=1-i;return this._w=S*h+i*this._w,this._x=S*s+i*this._x,this._y=S*l+i*this._y,this._z=S*c+i*this._z,this.normalize(),this}const p=Math.sqrt(m),g=Math.atan2(p,d),_=Math.sin((1-i)*g)/p,x=Math.sin(i*g)/p;return this._w=h*_+this._w*x,this._x=s*_+this._x*x,this._y=l*_+this._y*x,this._z=c*_+this._z*x,this._onChangeCallback(),this}slerpQuaternions(t,i,s){return this.copy(t).slerp(i,s)}random(){const t=2*Math.PI*Math.random(),i=2*Math.PI*Math.random(),s=Math.random(),l=Math.sqrt(1-s),c=Math.sqrt(s);return this.set(l*Math.sin(t),l*Math.cos(t),c*Math.sin(i),c*Math.cos(i))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,i=0){return this._x=t[i],this._y=t[i+1],this._z=t[i+2],this._w=t[i+3],this._onChangeCallback(),this}toArray(t=[],i=0){return t[i]=this._x,t[i+1]=this._y,t[i+2]=this._z,t[i+3]=this._w,t}fromBufferAttribute(t,i){return this._x=t.getX(i),this._y=t.getY(i),this._z=t.getZ(i),this._w=t.getW(i),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class Y{constructor(t=0,i=0,s=0){Y.prototype.isVector3=!0,this.x=t,this.y=i,this.z=s}set(t,i,s){return s===void 0&&(s=this.z),this.x=t,this.y=i,this.z=s,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;case 2:this.z=i;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this.z=t.z+i.z,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this.z+=t.z*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this.z=t.z-i.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,i){return this.x=t.x*i.x,this.y=t.y*i.y,this.z=t.z*i.z,this}applyEuler(t){return this.applyQuaternion(Rv.setFromEuler(t))}applyAxisAngle(t,i){return this.applyQuaternion(Rv.setFromAxisAngle(t,i))}applyMatrix3(t){const i=this.x,s=this.y,l=this.z,c=t.elements;return this.x=c[0]*i+c[3]*s+c[6]*l,this.y=c[1]*i+c[4]*s+c[7]*l,this.z=c[2]*i+c[5]*s+c[8]*l,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const i=this.x,s=this.y,l=this.z,c=t.elements,h=1/(c[3]*i+c[7]*s+c[11]*l+c[15]);return this.x=(c[0]*i+c[4]*s+c[8]*l+c[12])*h,this.y=(c[1]*i+c[5]*s+c[9]*l+c[13])*h,this.z=(c[2]*i+c[6]*s+c[10]*l+c[14])*h,this}applyQuaternion(t){const i=this.x,s=this.y,l=this.z,c=t.x,h=t.y,d=t.z,m=t.w,p=2*(h*l-d*s),g=2*(d*i-c*l),_=2*(c*s-h*i);return this.x=i+m*p+h*_-d*g,this.y=s+m*g+d*p-c*_,this.z=l+m*_+c*g-h*p,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const i=this.x,s=this.y,l=this.z,c=t.elements;return this.x=c[0]*i+c[4]*s+c[8]*l,this.y=c[1]*i+c[5]*s+c[9]*l,this.z=c[2]*i+c[6]*s+c[10]*l,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,i){return this.x=_e(this.x,t.x,i.x),this.y=_e(this.y,t.y,i.y),this.z=_e(this.z,t.z,i.z),this}clampScalar(t,i){return this.x=_e(this.x,t,i),this.y=_e(this.y,t,i),this.z=_e(this.z,t,i),this}clampLength(t,i){const s=this.length();return this.divideScalar(s||1).multiplyScalar(_e(s,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this.z+=(t.z-this.z)*i,this}lerpVectors(t,i,s){return this.x=t.x+(i.x-t.x)*s,this.y=t.y+(i.y-t.y)*s,this.z=t.z+(i.z-t.z)*s,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,i){const s=t.x,l=t.y,c=t.z,h=i.x,d=i.y,m=i.z;return this.x=l*m-c*d,this.y=c*h-s*m,this.z=s*d-l*h,this}projectOnVector(t){const i=t.lengthSq();if(i===0)return this.set(0,0,0);const s=t.dot(this)/i;return this.copy(t).multiplyScalar(s)}projectOnPlane(t){return xd.copy(this).projectOnVector(t),this.sub(xd)}reflect(t){return this.sub(xd.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const i=Math.sqrt(this.lengthSq()*t.lengthSq());if(i===0)return Math.PI/2;const s=this.dot(t)/i;return Math.acos(_e(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const i=this.x-t.x,s=this.y-t.y,l=this.z-t.z;return i*i+s*s+l*l}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,i,s){const l=Math.sin(i)*t;return this.x=l*Math.sin(s),this.y=Math.cos(i)*t,this.z=l*Math.cos(s),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,i,s){return this.x=t*Math.sin(i),this.y=s,this.z=t*Math.cos(i),this}setFromMatrixPosition(t){const i=t.elements;return this.x=i[12],this.y=i[13],this.z=i[14],this}setFromMatrixScale(t){const i=this.setFromMatrixColumn(t,0).length(),s=this.setFromMatrixColumn(t,1).length(),l=this.setFromMatrixColumn(t,2).length();return this.x=i,this.y=s,this.z=l,this}setFromMatrixColumn(t,i){return this.fromArray(t.elements,i*4)}setFromMatrix3Column(t,i){return this.fromArray(t.elements,i*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this.z=t[i+2],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t[i+2]=this.z,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this.z=t.getZ(i),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,i=Math.random()*2-1,s=Math.sqrt(1-i*i);return this.x=s*Math.cos(t),this.y=i,this.z=s*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const xd=new Y,Rv=new Jl;class $l{constructor(t=new Y(1/0,1/0,1/0),i=new Y(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=i}set(t,i){return this.min.copy(t),this.max.copy(i),this}setFromArray(t){this.makeEmpty();for(let i=0,s=t.length;i<s;i+=3)this.expandByPoint(Li.fromArray(t,i));return this}setFromBufferAttribute(t){this.makeEmpty();for(let i=0,s=t.count;i<s;i++)this.expandByPoint(Li.fromBufferAttribute(t,i));return this}setFromPoints(t){this.makeEmpty();for(let i=0,s=t.length;i<s;i++)this.expandByPoint(t[i]);return this}setFromCenterAndSize(t,i){const s=Li.copy(i).multiplyScalar(.5);return this.min.copy(t).sub(s),this.max.copy(t).add(s),this}setFromObject(t,i=!1){return this.makeEmpty(),this.expandByObject(t,i)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,i=!1){t.updateWorldMatrix(!1,!1);const s=t.geometry;if(s!==void 0){const c=s.getAttribute("position");if(i===!0&&c!==void 0&&t.isInstancedMesh!==!0)for(let h=0,d=c.count;h<d;h++)t.isMesh===!0?t.getVertexPosition(h,Li):Li.fromBufferAttribute(c,h),Li.applyMatrix4(t.matrixWorld),this.expandByPoint(Li);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),mu.copy(t.boundingBox)):(s.boundingBox===null&&s.computeBoundingBox(),mu.copy(s.boundingBox)),mu.applyMatrix4(t.matrixWorld),this.union(mu)}const l=t.children;for(let c=0,h=l.length;c<h;c++)this.expandByObject(l[c],i);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,i){return i.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Li),Li.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let i,s;return t.normal.x>0?(i=t.normal.x*this.min.x,s=t.normal.x*this.max.x):(i=t.normal.x*this.max.x,s=t.normal.x*this.min.x),t.normal.y>0?(i+=t.normal.y*this.min.y,s+=t.normal.y*this.max.y):(i+=t.normal.y*this.max.y,s+=t.normal.y*this.min.y),t.normal.z>0?(i+=t.normal.z*this.min.z,s+=t.normal.z*this.max.z):(i+=t.normal.z*this.max.z,s+=t.normal.z*this.min.z),i<=-t.constant&&s>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Ul),gu.subVectors(this.max,Ul),Zr.subVectors(t.a,Ul),Kr.subVectors(t.b,Ul),Jr.subVectors(t.c,Ul),es.subVectors(Kr,Zr),ns.subVectors(Jr,Kr),Vs.subVectors(Zr,Jr);let i=[0,-es.z,es.y,0,-ns.z,ns.y,0,-Vs.z,Vs.y,es.z,0,-es.x,ns.z,0,-ns.x,Vs.z,0,-Vs.x,-es.y,es.x,0,-ns.y,ns.x,0,-Vs.y,Vs.x,0];return!Sd(i,Zr,Kr,Jr,gu)||(i=[1,0,0,0,1,0,0,0,1],!Sd(i,Zr,Kr,Jr,gu))?!1:(_u.crossVectors(es,ns),i=[_u.x,_u.y,_u.z],Sd(i,Zr,Kr,Jr,gu))}clampPoint(t,i){return i.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Li).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Li).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(_a[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),_a[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),_a[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),_a[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),_a[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),_a[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),_a[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),_a[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(_a),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}}const _a=[new Y,new Y,new Y,new Y,new Y,new Y,new Y,new Y],Li=new Y,mu=new $l,Zr=new Y,Kr=new Y,Jr=new Y,es=new Y,ns=new Y,Vs=new Y,Ul=new Y,gu=new Y,_u=new Y,ks=new Y;function Sd(r,t,i,s,l){for(let c=0,h=r.length-3;c<=h;c+=3){ks.fromArray(r,c);const d=l.x*Math.abs(ks.x)+l.y*Math.abs(ks.y)+l.z*Math.abs(ks.z),m=t.dot(ks),p=i.dot(ks),g=s.dot(ks);if(Math.max(-Math.max(m,p,g),Math.min(m,p,g))>d)return!1}return!0}const ab=new $l,Nl=new Y,Md=new Y;class Ju{constructor(t=new Y,i=-1){this.isSphere=!0,this.center=t,this.radius=i}set(t,i){return this.center.copy(t),this.radius=i,this}setFromPoints(t,i){const s=this.center;i!==void 0?s.copy(i):ab.setFromPoints(t).getCenter(s);let l=0;for(let c=0,h=t.length;c<h;c++)l=Math.max(l,s.distanceToSquared(t[c]));return this.radius=Math.sqrt(l),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const i=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=i*i}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,i){const s=this.center.distanceToSquared(t);return i.copy(t),s>this.radius*this.radius&&(i.sub(this.center).normalize(),i.multiplyScalar(this.radius).add(this.center)),i}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Nl.subVectors(t,this.center);const i=Nl.lengthSq();if(i>this.radius*this.radius){const s=Math.sqrt(i),l=(s-this.radius)*.5;this.center.addScaledVector(Nl,l/s),this.radius+=l}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(Md.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Nl.copy(t.center).add(Md)),this.expandByPoint(Nl.copy(t.center).sub(Md))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}}const va=new Y,Ed=new Y,vu=new Y,is=new Y,bd=new Y,yu=new Y,Td=new Y;class px{constructor(t=new Y,i=new Y(0,0,-1)){this.origin=t,this.direction=i}set(t,i){return this.origin.copy(t),this.direction.copy(i),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,i){return i.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,va)),this}closestPointToPoint(t,i){i.subVectors(t,this.origin);const s=i.dot(this.direction);return s<0?i.copy(this.origin):i.copy(this.origin).addScaledVector(this.direction,s)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const i=va.subVectors(t,this.origin).dot(this.direction);return i<0?this.origin.distanceToSquared(t):(va.copy(this.origin).addScaledVector(this.direction,i),va.distanceToSquared(t))}distanceSqToSegment(t,i,s,l){Ed.copy(t).add(i).multiplyScalar(.5),vu.copy(i).sub(t).normalize(),is.copy(this.origin).sub(Ed);const c=t.distanceTo(i)*.5,h=-this.direction.dot(vu),d=is.dot(this.direction),m=-is.dot(vu),p=is.lengthSq(),g=Math.abs(1-h*h);let _,x,S,E;if(g>0)if(_=h*m-d,x=h*d-m,E=c*g,_>=0)if(x>=-E)if(x<=E){const b=1/g;_*=b,x*=b,S=_*(_+h*x+2*d)+x*(h*_+x+2*m)+p}else x=c,_=Math.max(0,-(h*x+d)),S=-_*_+x*(x+2*m)+p;else x=-c,_=Math.max(0,-(h*x+d)),S=-_*_+x*(x+2*m)+p;else x<=-E?(_=Math.max(0,-(-h*c+d)),x=_>0?-c:Math.min(Math.max(-c,-m),c),S=-_*_+x*(x+2*m)+p):x<=E?(_=0,x=Math.min(Math.max(-c,-m),c),S=x*(x+2*m)+p):(_=Math.max(0,-(h*c+d)),x=_>0?c:Math.min(Math.max(-c,-m),c),S=-_*_+x*(x+2*m)+p);else x=h>0?-c:c,_=Math.max(0,-(h*x+d)),S=-_*_+x*(x+2*m)+p;return s&&s.copy(this.origin).addScaledVector(this.direction,_),l&&l.copy(Ed).addScaledVector(vu,x),S}intersectSphere(t,i){va.subVectors(t.center,this.origin);const s=va.dot(this.direction),l=va.dot(va)-s*s,c=t.radius*t.radius;if(l>c)return null;const h=Math.sqrt(c-l),d=s-h,m=s+h;return m<0?null:d<0?this.at(m,i):this.at(d,i)}intersectsSphere(t){return this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const i=t.normal.dot(this.direction);if(i===0)return t.distanceToPoint(this.origin)===0?0:null;const s=-(this.origin.dot(t.normal)+t.constant)/i;return s>=0?s:null}intersectPlane(t,i){const s=this.distanceToPlane(t);return s===null?null:this.at(s,i)}intersectsPlane(t){const i=t.distanceToPoint(this.origin);return i===0||t.normal.dot(this.direction)*i<0}intersectBox(t,i){let s,l,c,h,d,m;const p=1/this.direction.x,g=1/this.direction.y,_=1/this.direction.z,x=this.origin;return p>=0?(s=(t.min.x-x.x)*p,l=(t.max.x-x.x)*p):(s=(t.max.x-x.x)*p,l=(t.min.x-x.x)*p),g>=0?(c=(t.min.y-x.y)*g,h=(t.max.y-x.y)*g):(c=(t.max.y-x.y)*g,h=(t.min.y-x.y)*g),s>h||c>l||((c>s||isNaN(s))&&(s=c),(h<l||isNaN(l))&&(l=h),_>=0?(d=(t.min.z-x.z)*_,m=(t.max.z-x.z)*_):(d=(t.max.z-x.z)*_,m=(t.min.z-x.z)*_),s>m||d>l)||((d>s||s!==s)&&(s=d),(m<l||l!==l)&&(l=m),l<0)?null:this.at(s>=0?s:l,i)}intersectsBox(t){return this.intersectBox(t,va)!==null}intersectTriangle(t,i,s,l,c){bd.subVectors(i,t),yu.subVectors(s,t),Td.crossVectors(bd,yu);let h=this.direction.dot(Td),d;if(h>0){if(l)return null;d=1}else if(h<0)d=-1,h=-h;else return null;is.subVectors(this.origin,t);const m=d*this.direction.dot(yu.crossVectors(is,yu));if(m<0)return null;const p=d*this.direction.dot(bd.cross(is));if(p<0||m+p>h)return null;const g=-d*is.dot(Td);return g<0?null:this.at(g/h,c)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Je{constructor(t,i,s,l,c,h,d,m,p,g,_,x,S,E,b,M){Je.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,i,s,l,c,h,d,m,p,g,_,x,S,E,b,M)}set(t,i,s,l,c,h,d,m,p,g,_,x,S,E,b,M){const v=this.elements;return v[0]=t,v[4]=i,v[8]=s,v[12]=l,v[1]=c,v[5]=h,v[9]=d,v[13]=m,v[2]=p,v[6]=g,v[10]=_,v[14]=x,v[3]=S,v[7]=E,v[11]=b,v[15]=M,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Je().fromArray(this.elements)}copy(t){const i=this.elements,s=t.elements;return i[0]=s[0],i[1]=s[1],i[2]=s[2],i[3]=s[3],i[4]=s[4],i[5]=s[5],i[6]=s[6],i[7]=s[7],i[8]=s[8],i[9]=s[9],i[10]=s[10],i[11]=s[11],i[12]=s[12],i[13]=s[13],i[14]=s[14],i[15]=s[15],this}copyPosition(t){const i=this.elements,s=t.elements;return i[12]=s[12],i[13]=s[13],i[14]=s[14],this}setFromMatrix3(t){const i=t.elements;return this.set(i[0],i[3],i[6],0,i[1],i[4],i[7],0,i[2],i[5],i[8],0,0,0,0,1),this}extractBasis(t,i,s){return t.setFromMatrixColumn(this,0),i.setFromMatrixColumn(this,1),s.setFromMatrixColumn(this,2),this}makeBasis(t,i,s){return this.set(t.x,i.x,s.x,0,t.y,i.y,s.y,0,t.z,i.z,s.z,0,0,0,0,1),this}extractRotation(t){const i=this.elements,s=t.elements,l=1/$r.setFromMatrixColumn(t,0).length(),c=1/$r.setFromMatrixColumn(t,1).length(),h=1/$r.setFromMatrixColumn(t,2).length();return i[0]=s[0]*l,i[1]=s[1]*l,i[2]=s[2]*l,i[3]=0,i[4]=s[4]*c,i[5]=s[5]*c,i[6]=s[6]*c,i[7]=0,i[8]=s[8]*h,i[9]=s[9]*h,i[10]=s[10]*h,i[11]=0,i[12]=0,i[13]=0,i[14]=0,i[15]=1,this}makeRotationFromEuler(t){const i=this.elements,s=t.x,l=t.y,c=t.z,h=Math.cos(s),d=Math.sin(s),m=Math.cos(l),p=Math.sin(l),g=Math.cos(c),_=Math.sin(c);if(t.order==="XYZ"){const x=h*g,S=h*_,E=d*g,b=d*_;i[0]=m*g,i[4]=-m*_,i[8]=p,i[1]=S+E*p,i[5]=x-b*p,i[9]=-d*m,i[2]=b-x*p,i[6]=E+S*p,i[10]=h*m}else if(t.order==="YXZ"){const x=m*g,S=m*_,E=p*g,b=p*_;i[0]=x+b*d,i[4]=E*d-S,i[8]=h*p,i[1]=h*_,i[5]=h*g,i[9]=-d,i[2]=S*d-E,i[6]=b+x*d,i[10]=h*m}else if(t.order==="ZXY"){const x=m*g,S=m*_,E=p*g,b=p*_;i[0]=x-b*d,i[4]=-h*_,i[8]=E+S*d,i[1]=S+E*d,i[5]=h*g,i[9]=b-x*d,i[2]=-h*p,i[6]=d,i[10]=h*m}else if(t.order==="ZYX"){const x=h*g,S=h*_,E=d*g,b=d*_;i[0]=m*g,i[4]=E*p-S,i[8]=x*p+b,i[1]=m*_,i[5]=b*p+x,i[9]=S*p-E,i[2]=-p,i[6]=d*m,i[10]=h*m}else if(t.order==="YZX"){const x=h*m,S=h*p,E=d*m,b=d*p;i[0]=m*g,i[4]=b-x*_,i[8]=E*_+S,i[1]=_,i[5]=h*g,i[9]=-d*g,i[2]=-p*g,i[6]=S*_+E,i[10]=x-b*_}else if(t.order==="XZY"){const x=h*m,S=h*p,E=d*m,b=d*p;i[0]=m*g,i[4]=-_,i[8]=p*g,i[1]=x*_+b,i[5]=h*g,i[9]=S*_-E,i[2]=E*_-S,i[6]=d*g,i[10]=b*_+x}return i[3]=0,i[7]=0,i[11]=0,i[12]=0,i[13]=0,i[14]=0,i[15]=1,this}makeRotationFromQuaternion(t){return this.compose(sb,t,rb)}lookAt(t,i,s){const l=this.elements;return ui.subVectors(t,i),ui.lengthSq()===0&&(ui.z=1),ui.normalize(),as.crossVectors(s,ui),as.lengthSq()===0&&(Math.abs(s.z)===1?ui.x+=1e-4:ui.z+=1e-4,ui.normalize(),as.crossVectors(s,ui)),as.normalize(),xu.crossVectors(ui,as),l[0]=as.x,l[4]=xu.x,l[8]=ui.x,l[1]=as.y,l[5]=xu.y,l[9]=ui.y,l[2]=as.z,l[6]=xu.z,l[10]=ui.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,i){const s=t.elements,l=i.elements,c=this.elements,h=s[0],d=s[4],m=s[8],p=s[12],g=s[1],_=s[5],x=s[9],S=s[13],E=s[2],b=s[6],M=s[10],v=s[14],L=s[3],U=s[7],T=s[11],V=s[15],I=l[0],P=l[4],H=l[8],D=l[12],C=l[1],G=l[5],ot=l[9],lt=l[13],mt=l[2],gt=l[6],B=l[10],$=l[14],J=l[3],Et=l[7],At=l[11],z=l[15];return c[0]=h*I+d*C+m*mt+p*J,c[4]=h*P+d*G+m*gt+p*Et,c[8]=h*H+d*ot+m*B+p*At,c[12]=h*D+d*lt+m*$+p*z,c[1]=g*I+_*C+x*mt+S*J,c[5]=g*P+_*G+x*gt+S*Et,c[9]=g*H+_*ot+x*B+S*At,c[13]=g*D+_*lt+x*$+S*z,c[2]=E*I+b*C+M*mt+v*J,c[6]=E*P+b*G+M*gt+v*Et,c[10]=E*H+b*ot+M*B+v*At,c[14]=E*D+b*lt+M*$+v*z,c[3]=L*I+U*C+T*mt+V*J,c[7]=L*P+U*G+T*gt+V*Et,c[11]=L*H+U*ot+T*B+V*At,c[15]=L*D+U*lt+T*$+V*z,this}multiplyScalar(t){const i=this.elements;return i[0]*=t,i[4]*=t,i[8]*=t,i[12]*=t,i[1]*=t,i[5]*=t,i[9]*=t,i[13]*=t,i[2]*=t,i[6]*=t,i[10]*=t,i[14]*=t,i[3]*=t,i[7]*=t,i[11]*=t,i[15]*=t,this}determinant(){const t=this.elements,i=t[0],s=t[4],l=t[8],c=t[12],h=t[1],d=t[5],m=t[9],p=t[13],g=t[2],_=t[6],x=t[10],S=t[14],E=t[3],b=t[7],M=t[11],v=t[15];return E*(+c*m*_-l*p*_-c*d*x+s*p*x+l*d*S-s*m*S)+b*(+i*m*S-i*p*x+c*h*x-l*h*S+l*p*g-c*m*g)+M*(+i*p*_-i*d*S-c*h*_+s*h*S+c*d*g-s*p*g)+v*(-l*d*g-i*m*_+i*d*x+l*h*_-s*h*x+s*m*g)}transpose(){const t=this.elements;let i;return i=t[1],t[1]=t[4],t[4]=i,i=t[2],t[2]=t[8],t[8]=i,i=t[6],t[6]=t[9],t[9]=i,i=t[3],t[3]=t[12],t[12]=i,i=t[7],t[7]=t[13],t[13]=i,i=t[11],t[11]=t[14],t[14]=i,this}setPosition(t,i,s){const l=this.elements;return t.isVector3?(l[12]=t.x,l[13]=t.y,l[14]=t.z):(l[12]=t,l[13]=i,l[14]=s),this}invert(){const t=this.elements,i=t[0],s=t[1],l=t[2],c=t[3],h=t[4],d=t[5],m=t[6],p=t[7],g=t[8],_=t[9],x=t[10],S=t[11],E=t[12],b=t[13],M=t[14],v=t[15],L=_*M*p-b*x*p+b*m*S-d*M*S-_*m*v+d*x*v,U=E*x*p-g*M*p-E*m*S+h*M*S+g*m*v-h*x*v,T=g*b*p-E*_*p+E*d*S-h*b*S-g*d*v+h*_*v,V=E*_*m-g*b*m-E*d*x+h*b*x+g*d*M-h*_*M,I=i*L+s*U+l*T+c*V;if(I===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/I;return t[0]=L*P,t[1]=(b*x*c-_*M*c-b*l*S+s*M*S+_*l*v-s*x*v)*P,t[2]=(d*M*c-b*m*c+b*l*p-s*M*p-d*l*v+s*m*v)*P,t[3]=(_*m*c-d*x*c-_*l*p+s*x*p+d*l*S-s*m*S)*P,t[4]=U*P,t[5]=(g*M*c-E*x*c+E*l*S-i*M*S-g*l*v+i*x*v)*P,t[6]=(E*m*c-h*M*c-E*l*p+i*M*p+h*l*v-i*m*v)*P,t[7]=(h*x*c-g*m*c+g*l*p-i*x*p-h*l*S+i*m*S)*P,t[8]=T*P,t[9]=(E*_*c-g*b*c-E*s*S+i*b*S+g*s*v-i*_*v)*P,t[10]=(h*b*c-E*d*c+E*s*p-i*b*p-h*s*v+i*d*v)*P,t[11]=(g*d*c-h*_*c-g*s*p+i*_*p+h*s*S-i*d*S)*P,t[12]=V*P,t[13]=(g*b*l-E*_*l+E*s*x-i*b*x-g*s*M+i*_*M)*P,t[14]=(E*d*l-h*b*l-E*s*m+i*b*m+h*s*M-i*d*M)*P,t[15]=(h*_*l-g*d*l+g*s*m-i*_*m-h*s*x+i*d*x)*P,this}scale(t){const i=this.elements,s=t.x,l=t.y,c=t.z;return i[0]*=s,i[4]*=l,i[8]*=c,i[1]*=s,i[5]*=l,i[9]*=c,i[2]*=s,i[6]*=l,i[10]*=c,i[3]*=s,i[7]*=l,i[11]*=c,this}getMaxScaleOnAxis(){const t=this.elements,i=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],s=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],l=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(i,s,l))}makeTranslation(t,i,s){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,i,0,0,1,s,0,0,0,1),this}makeRotationX(t){const i=Math.cos(t),s=Math.sin(t);return this.set(1,0,0,0,0,i,-s,0,0,s,i,0,0,0,0,1),this}makeRotationY(t){const i=Math.cos(t),s=Math.sin(t);return this.set(i,0,s,0,0,1,0,0,-s,0,i,0,0,0,0,1),this}makeRotationZ(t){const i=Math.cos(t),s=Math.sin(t);return this.set(i,-s,0,0,s,i,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,i){const s=Math.cos(i),l=Math.sin(i),c=1-s,h=t.x,d=t.y,m=t.z,p=c*h,g=c*d;return this.set(p*h+s,p*d-l*m,p*m+l*d,0,p*d+l*m,g*d+s,g*m-l*h,0,p*m-l*d,g*m+l*h,c*m*m+s,0,0,0,0,1),this}makeScale(t,i,s){return this.set(t,0,0,0,0,i,0,0,0,0,s,0,0,0,0,1),this}makeShear(t,i,s,l,c,h){return this.set(1,s,c,0,t,1,h,0,i,l,1,0,0,0,0,1),this}compose(t,i,s){const l=this.elements,c=i._x,h=i._y,d=i._z,m=i._w,p=c+c,g=h+h,_=d+d,x=c*p,S=c*g,E=c*_,b=h*g,M=h*_,v=d*_,L=m*p,U=m*g,T=m*_,V=s.x,I=s.y,P=s.z;return l[0]=(1-(b+v))*V,l[1]=(S+T)*V,l[2]=(E-U)*V,l[3]=0,l[4]=(S-T)*I,l[5]=(1-(x+v))*I,l[6]=(M+L)*I,l[7]=0,l[8]=(E+U)*P,l[9]=(M-L)*P,l[10]=(1-(x+b))*P,l[11]=0,l[12]=t.x,l[13]=t.y,l[14]=t.z,l[15]=1,this}decompose(t,i,s){const l=this.elements;let c=$r.set(l[0],l[1],l[2]).length();const h=$r.set(l[4],l[5],l[6]).length(),d=$r.set(l[8],l[9],l[10]).length();this.determinant()<0&&(c=-c),t.x=l[12],t.y=l[13],t.z=l[14],Oi.copy(this);const p=1/c,g=1/h,_=1/d;return Oi.elements[0]*=p,Oi.elements[1]*=p,Oi.elements[2]*=p,Oi.elements[4]*=g,Oi.elements[5]*=g,Oi.elements[6]*=g,Oi.elements[8]*=_,Oi.elements[9]*=_,Oi.elements[10]*=_,i.setFromRotationMatrix(Oi),s.x=c,s.y=h,s.z=d,this}makePerspective(t,i,s,l,c,h,d=Ca){const m=this.elements,p=2*c/(i-t),g=2*c/(s-l),_=(i+t)/(i-t),x=(s+l)/(s-l);let S,E;if(d===Ca)S=-(h+c)/(h-c),E=-2*h*c/(h-c);else if(d===Wu)S=-h/(h-c),E=-h*c/(h-c);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+d);return m[0]=p,m[4]=0,m[8]=_,m[12]=0,m[1]=0,m[5]=g,m[9]=x,m[13]=0,m[2]=0,m[6]=0,m[10]=S,m[14]=E,m[3]=0,m[7]=0,m[11]=-1,m[15]=0,this}makeOrthographic(t,i,s,l,c,h,d=Ca){const m=this.elements,p=1/(i-t),g=1/(s-l),_=1/(h-c),x=(i+t)*p,S=(s+l)*g;let E,b;if(d===Ca)E=(h+c)*_,b=-2*_;else if(d===Wu)E=c*_,b=-1*_;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+d);return m[0]=2*p,m[4]=0,m[8]=0,m[12]=-x,m[1]=0,m[5]=2*g,m[9]=0,m[13]=-S,m[2]=0,m[6]=0,m[10]=b,m[14]=-E,m[3]=0,m[7]=0,m[11]=0,m[15]=1,this}equals(t){const i=this.elements,s=t.elements;for(let l=0;l<16;l++)if(i[l]!==s[l])return!1;return!0}fromArray(t,i=0){for(let s=0;s<16;s++)this.elements[s]=t[s+i];return this}toArray(t=[],i=0){const s=this.elements;return t[i]=s[0],t[i+1]=s[1],t[i+2]=s[2],t[i+3]=s[3],t[i+4]=s[4],t[i+5]=s[5],t[i+6]=s[6],t[i+7]=s[7],t[i+8]=s[8],t[i+9]=s[9],t[i+10]=s[10],t[i+11]=s[11],t[i+12]=s[12],t[i+13]=s[13],t[i+14]=s[14],t[i+15]=s[15],t}}const $r=new Y,Oi=new Je,sb=new Y(0,0,0),rb=new Y(1,1,1),as=new Y,xu=new Y,ui=new Y,Cv=new Je,wv=new Jl;class Ua{constructor(t=0,i=0,s=0,l=Ua.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=i,this._z=s,this._order=l}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,i,s,l=this._order){return this._x=t,this._y=i,this._z=s,this._order=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,i=this._order,s=!0){const l=t.elements,c=l[0],h=l[4],d=l[8],m=l[1],p=l[5],g=l[9],_=l[2],x=l[6],S=l[10];switch(i){case"XYZ":this._y=Math.asin(_e(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(-g,S),this._z=Math.atan2(-h,c)):(this._x=Math.atan2(x,p),this._z=0);break;case"YXZ":this._x=Math.asin(-_e(g,-1,1)),Math.abs(g)<.9999999?(this._y=Math.atan2(d,S),this._z=Math.atan2(m,p)):(this._y=Math.atan2(-_,c),this._z=0);break;case"ZXY":this._x=Math.asin(_e(x,-1,1)),Math.abs(x)<.9999999?(this._y=Math.atan2(-_,S),this._z=Math.atan2(-h,p)):(this._y=0,this._z=Math.atan2(m,c));break;case"ZYX":this._y=Math.asin(-_e(_,-1,1)),Math.abs(_)<.9999999?(this._x=Math.atan2(x,S),this._z=Math.atan2(m,c)):(this._x=0,this._z=Math.atan2(-h,p));break;case"YZX":this._z=Math.asin(_e(m,-1,1)),Math.abs(m)<.9999999?(this._x=Math.atan2(-g,p),this._y=Math.atan2(-_,c)):(this._x=0,this._y=Math.atan2(d,S));break;case"XZY":this._z=Math.asin(-_e(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(x,p),this._y=Math.atan2(d,c)):(this._x=Math.atan2(-g,S),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+i)}return this._order=i,s===!0&&this._onChangeCallback(),this}setFromQuaternion(t,i,s){return Cv.makeRotationFromQuaternion(t),this.setFromRotationMatrix(Cv,i,s)}setFromVector3(t,i=this._order){return this.set(t.x,t.y,t.z,i)}reorder(t){return wv.setFromEuler(this),this.setFromQuaternion(wv,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],i=0){return t[i]=this._x,t[i+1]=this._y,t[i+2]=this._z,t[i+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ua.DEFAULT_ORDER="XYZ";class mx{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let ob=0;const Dv=new Y,to=new Jl,ya=new Je,Su=new Y,Ll=new Y,lb=new Y,cb=new Jl,Uv=new Y(1,0,0),Nv=new Y(0,1,0),Lv=new Y(0,0,1),Ov={type:"added"},ub={type:"removed"},eo={type:"childadded",child:null},Ad={type:"childremoved",child:null};class jn extends Po{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:ob++}),this.uuid=Kl(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=jn.DEFAULT_UP.clone();const t=new Y,i=new Ua,s=new Jl,l=new Y(1,1,1);function c(){s.setFromEuler(i,!1)}function h(){i.setFromQuaternion(s,void 0,!1)}i._onChange(c),s._onChange(h),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:i},quaternion:{configurable:!0,enumerable:!0,value:s},scale:{configurable:!0,enumerable:!0,value:l},modelViewMatrix:{value:new Je},normalMatrix:{value:new ue}}),this.matrix=new Je,this.matrixWorld=new Je,this.matrixAutoUpdate=jn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=jn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new mx,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,i){this.quaternion.setFromAxisAngle(t,i)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,i){return to.setFromAxisAngle(t,i),this.quaternion.multiply(to),this}rotateOnWorldAxis(t,i){return to.setFromAxisAngle(t,i),this.quaternion.premultiply(to),this}rotateX(t){return this.rotateOnAxis(Uv,t)}rotateY(t){return this.rotateOnAxis(Nv,t)}rotateZ(t){return this.rotateOnAxis(Lv,t)}translateOnAxis(t,i){return Dv.copy(t).applyQuaternion(this.quaternion),this.position.add(Dv.multiplyScalar(i)),this}translateX(t){return this.translateOnAxis(Uv,t)}translateY(t){return this.translateOnAxis(Nv,t)}translateZ(t){return this.translateOnAxis(Lv,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(ya.copy(this.matrixWorld).invert())}lookAt(t,i,s){t.isVector3?Su.copy(t):Su.set(t,i,s);const l=this.parent;this.updateWorldMatrix(!0,!1),Ll.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?ya.lookAt(Ll,Su,this.up):ya.lookAt(Su,Ll,this.up),this.quaternion.setFromRotationMatrix(ya),l&&(ya.extractRotation(l.matrixWorld),to.setFromRotationMatrix(ya),this.quaternion.premultiply(to.invert()))}add(t){if(arguments.length>1){for(let i=0;i<arguments.length;i++)this.add(arguments[i]);return this}return t===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(Ov),eo.child=t,this.dispatchEvent(eo),eo.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let s=0;s<arguments.length;s++)this.remove(arguments[s]);return this}const i=this.children.indexOf(t);return i!==-1&&(t.parent=null,this.children.splice(i,1),t.dispatchEvent(ub),Ad.child=t,this.dispatchEvent(Ad),Ad.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),ya.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),ya.multiply(t.parent.matrixWorld)),t.applyMatrix4(ya),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(Ov),eo.child=t,this.dispatchEvent(eo),eo.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,i){if(this[t]===i)return this;for(let s=0,l=this.children.length;s<l;s++){const h=this.children[s].getObjectByProperty(t,i);if(h!==void 0)return h}}getObjectsByProperty(t,i,s=[]){this[t]===i&&s.push(this);const l=this.children;for(let c=0,h=l.length;c<h;c++)l[c].getObjectsByProperty(t,i,s);return s}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ll,t,lb),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Ll,cb,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const i=this.matrixWorld.elements;return t.set(i[8],i[9],i[10]).normalize()}raycast(){}traverse(t){t(this);const i=this.children;for(let s=0,l=i.length;s<l;s++)i[s].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const i=this.children;for(let s=0,l=i.length;s<l;s++)i[s].traverseVisible(t)}traverseAncestors(t){const i=this.parent;i!==null&&(t(i),i.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const i=this.children;for(let s=0,l=i.length;s<l;s++)i[s].updateMatrixWorld(t)}updateWorldMatrix(t,i){const s=this.parent;if(t===!0&&s!==null&&s.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),i===!0){const l=this.children;for(let c=0,h=l.length;c<h;c++)l[c].updateWorldMatrix(!1,!0)}}toJSON(t){const i=t===void 0||typeof t=="string",s={};i&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},s.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const l={};l.uuid=this.uuid,l.type=this.type,this.name!==""&&(l.name=this.name),this.castShadow===!0&&(l.castShadow=!0),this.receiveShadow===!0&&(l.receiveShadow=!0),this.visible===!1&&(l.visible=!1),this.frustumCulled===!1&&(l.frustumCulled=!1),this.renderOrder!==0&&(l.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(l.userData=this.userData),l.layers=this.layers.mask,l.matrix=this.matrix.toArray(),l.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(l.matrixAutoUpdate=!1),this.isInstancedMesh&&(l.type="InstancedMesh",l.count=this.count,l.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(l.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(l.type="BatchedMesh",l.perObjectFrustumCulled=this.perObjectFrustumCulled,l.sortObjects=this.sortObjects,l.drawRanges=this._drawRanges,l.reservedRanges=this._reservedRanges,l.visibility=this._visibility,l.active=this._active,l.bounds=this._bounds.map(d=>({boxInitialized:d.boxInitialized,boxMin:d.box.min.toArray(),boxMax:d.box.max.toArray(),sphereInitialized:d.sphereInitialized,sphereRadius:d.sphere.radius,sphereCenter:d.sphere.center.toArray()})),l.maxInstanceCount=this._maxInstanceCount,l.maxVertexCount=this._maxVertexCount,l.maxIndexCount=this._maxIndexCount,l.geometryInitialized=this._geometryInitialized,l.geometryCount=this._geometryCount,l.matricesTexture=this._matricesTexture.toJSON(t),this._colorsTexture!==null&&(l.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(l.boundingSphere={center:l.boundingSphere.center.toArray(),radius:l.boundingSphere.radius}),this.boundingBox!==null&&(l.boundingBox={min:l.boundingBox.min.toArray(),max:l.boundingBox.max.toArray()}));function c(d,m){return d[m.uuid]===void 0&&(d[m.uuid]=m.toJSON(t)),m.uuid}if(this.isScene)this.background&&(this.background.isColor?l.background=this.background.toJSON():this.background.isTexture&&(l.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(l.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){l.geometry=c(t.geometries,this.geometry);const d=this.geometry.parameters;if(d!==void 0&&d.shapes!==void 0){const m=d.shapes;if(Array.isArray(m))for(let p=0,g=m.length;p<g;p++){const _=m[p];c(t.shapes,_)}else c(t.shapes,m)}}if(this.isSkinnedMesh&&(l.bindMode=this.bindMode,l.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(c(t.skeletons,this.skeleton),l.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const d=[];for(let m=0,p=this.material.length;m<p;m++)d.push(c(t.materials,this.material[m]));l.material=d}else l.material=c(t.materials,this.material);if(this.children.length>0){l.children=[];for(let d=0;d<this.children.length;d++)l.children.push(this.children[d].toJSON(t).object)}if(this.animations.length>0){l.animations=[];for(let d=0;d<this.animations.length;d++){const m=this.animations[d];l.animations.push(c(t.animations,m))}}if(i){const d=h(t.geometries),m=h(t.materials),p=h(t.textures),g=h(t.images),_=h(t.shapes),x=h(t.skeletons),S=h(t.animations),E=h(t.nodes);d.length>0&&(s.geometries=d),m.length>0&&(s.materials=m),p.length>0&&(s.textures=p),g.length>0&&(s.images=g),_.length>0&&(s.shapes=_),x.length>0&&(s.skeletons=x),S.length>0&&(s.animations=S),E.length>0&&(s.nodes=E)}return s.object=l,s;function h(d){const m=[];for(const p in d){const g=d[p];delete g.metadata,m.push(g)}return m}}clone(t){return new this.constructor().copy(this,t)}copy(t,i=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),i===!0)for(let s=0;s<t.children.length;s++){const l=t.children[s];this.add(l.clone())}return this}}jn.DEFAULT_UP=new Y(0,1,0);jn.DEFAULT_MATRIX_AUTO_UPDATE=!0;jn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Pi=new Y,xa=new Y,Rd=new Y,Sa=new Y,no=new Y,io=new Y,Pv=new Y,Cd=new Y,wd=new Y,Dd=new Y,Ud=new qe,Nd=new qe,Ld=new qe;class Ii{constructor(t=new Y,i=new Y,s=new Y){this.a=t,this.b=i,this.c=s}static getNormal(t,i,s,l){l.subVectors(s,i),Pi.subVectors(t,i),l.cross(Pi);const c=l.lengthSq();return c>0?l.multiplyScalar(1/Math.sqrt(c)):l.set(0,0,0)}static getBarycoord(t,i,s,l,c){Pi.subVectors(l,i),xa.subVectors(s,i),Rd.subVectors(t,i);const h=Pi.dot(Pi),d=Pi.dot(xa),m=Pi.dot(Rd),p=xa.dot(xa),g=xa.dot(Rd),_=h*p-d*d;if(_===0)return c.set(0,0,0),null;const x=1/_,S=(p*m-d*g)*x,E=(h*g-d*m)*x;return c.set(1-S-E,E,S)}static containsPoint(t,i,s,l){return this.getBarycoord(t,i,s,l,Sa)===null?!1:Sa.x>=0&&Sa.y>=0&&Sa.x+Sa.y<=1}static getInterpolation(t,i,s,l,c,h,d,m){return this.getBarycoord(t,i,s,l,Sa)===null?(m.x=0,m.y=0,"z"in m&&(m.z=0),"w"in m&&(m.w=0),null):(m.setScalar(0),m.addScaledVector(c,Sa.x),m.addScaledVector(h,Sa.y),m.addScaledVector(d,Sa.z),m)}static getInterpolatedAttribute(t,i,s,l,c,h){return Ud.setScalar(0),Nd.setScalar(0),Ld.setScalar(0),Ud.fromBufferAttribute(t,i),Nd.fromBufferAttribute(t,s),Ld.fromBufferAttribute(t,l),h.setScalar(0),h.addScaledVector(Ud,c.x),h.addScaledVector(Nd,c.y),h.addScaledVector(Ld,c.z),h}static isFrontFacing(t,i,s,l){return Pi.subVectors(s,i),xa.subVectors(t,i),Pi.cross(xa).dot(l)<0}set(t,i,s){return this.a.copy(t),this.b.copy(i),this.c.copy(s),this}setFromPointsAndIndices(t,i,s,l){return this.a.copy(t[i]),this.b.copy(t[s]),this.c.copy(t[l]),this}setFromAttributeAndIndices(t,i,s,l){return this.a.fromBufferAttribute(t,i),this.b.fromBufferAttribute(t,s),this.c.fromBufferAttribute(t,l),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return Pi.subVectors(this.c,this.b),xa.subVectors(this.a,this.b),Pi.cross(xa).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return Ii.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,i){return Ii.getBarycoord(t,this.a,this.b,this.c,i)}getInterpolation(t,i,s,l,c){return Ii.getInterpolation(t,this.a,this.b,this.c,i,s,l,c)}containsPoint(t){return Ii.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return Ii.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,i){const s=this.a,l=this.b,c=this.c;let h,d;no.subVectors(l,s),io.subVectors(c,s),Cd.subVectors(t,s);const m=no.dot(Cd),p=io.dot(Cd);if(m<=0&&p<=0)return i.copy(s);wd.subVectors(t,l);const g=no.dot(wd),_=io.dot(wd);if(g>=0&&_<=g)return i.copy(l);const x=m*_-g*p;if(x<=0&&m>=0&&g<=0)return h=m/(m-g),i.copy(s).addScaledVector(no,h);Dd.subVectors(t,c);const S=no.dot(Dd),E=io.dot(Dd);if(E>=0&&S<=E)return i.copy(c);const b=S*p-m*E;if(b<=0&&p>=0&&E<=0)return d=p/(p-E),i.copy(s).addScaledVector(io,d);const M=g*E-S*_;if(M<=0&&_-g>=0&&S-E>=0)return Pv.subVectors(c,l),d=(_-g)/(_-g+(S-E)),i.copy(l).addScaledVector(Pv,d);const v=1/(M+b+x);return h=b*v,d=x*v,i.copy(s).addScaledVector(no,h).addScaledVector(io,d)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}const gx={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ss={h:0,s:0,l:0},Mu={h:0,s:0,l:0};function Od(r,t,i){return i<0&&(i+=1),i>1&&(i-=1),i<1/6?r+(t-r)*6*i:i<1/2?t:i<2/3?r+(t-r)*6*(2/3-i):r}class Oe{constructor(t,i,s){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,i,s)}set(t,i,s){if(i===void 0&&s===void 0){const l=t;l&&l.isColor?this.copy(l):typeof l=="number"?this.setHex(l):typeof l=="string"&&this.setStyle(l)}else this.setRGB(t,i,s);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,i=Ai){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Ne.toWorkingColorSpace(this,i),this}setRGB(t,i,s,l=Ne.workingColorSpace){return this.r=t,this.g=i,this.b=s,Ne.toWorkingColorSpace(this,l),this}setHSL(t,i,s,l=Ne.workingColorSpace){if(t=W1(t,1),i=_e(i,0,1),s=_e(s,0,1),i===0)this.r=this.g=this.b=s;else{const c=s<=.5?s*(1+i):s+i-s*i,h=2*s-c;this.r=Od(h,c,t+1/3),this.g=Od(h,c,t),this.b=Od(h,c,t-1/3)}return Ne.toWorkingColorSpace(this,l),this}setStyle(t,i=Ai){function s(c){c!==void 0&&parseFloat(c)<1&&console.warn("THREE.Color: Alpha component of "+t+" will be ignored.")}let l;if(l=/^(\w+)\(([^\)]*)\)/.exec(t)){let c;const h=l[1],d=l[2];switch(h){case"rgb":case"rgba":if(c=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(255,parseInt(c[1],10))/255,Math.min(255,parseInt(c[2],10))/255,Math.min(255,parseInt(c[3],10))/255,i);if(c=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(100,parseInt(c[1],10))/100,Math.min(100,parseInt(c[2],10))/100,Math.min(100,parseInt(c[3],10))/100,i);break;case"hsl":case"hsla":if(c=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setHSL(parseFloat(c[1])/360,parseFloat(c[2])/100,parseFloat(c[3])/100,i);break;default:console.warn("THREE.Color: Unknown color model "+t)}}else if(l=/^\#([A-Fa-f\d]+)$/.exec(t)){const c=l[1],h=c.length;if(h===3)return this.setRGB(parseInt(c.charAt(0),16)/15,parseInt(c.charAt(1),16)/15,parseInt(c.charAt(2),16)/15,i);if(h===6)return this.setHex(parseInt(c,16),i);console.warn("THREE.Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,i);return this}setColorName(t,i=Ai){const s=gx[t.toLowerCase()];return s!==void 0?this.setHex(s,i):console.warn("THREE.Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=wa(t.r),this.g=wa(t.g),this.b=wa(t.b),this}copyLinearToSRGB(t){return this.r=po(t.r),this.g=po(t.g),this.b=po(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=Ai){return Ne.fromWorkingColorSpace(Bn.copy(this),t),Math.round(_e(Bn.r*255,0,255))*65536+Math.round(_e(Bn.g*255,0,255))*256+Math.round(_e(Bn.b*255,0,255))}getHexString(t=Ai){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,i=Ne.workingColorSpace){Ne.fromWorkingColorSpace(Bn.copy(this),i);const s=Bn.r,l=Bn.g,c=Bn.b,h=Math.max(s,l,c),d=Math.min(s,l,c);let m,p;const g=(d+h)/2;if(d===h)m=0,p=0;else{const _=h-d;switch(p=g<=.5?_/(h+d):_/(2-h-d),h){case s:m=(l-c)/_+(l<c?6:0);break;case l:m=(c-s)/_+2;break;case c:m=(s-l)/_+4;break}m/=6}return t.h=m,t.s=p,t.l=g,t}getRGB(t,i=Ne.workingColorSpace){return Ne.fromWorkingColorSpace(Bn.copy(this),i),t.r=Bn.r,t.g=Bn.g,t.b=Bn.b,t}getStyle(t=Ai){Ne.fromWorkingColorSpace(Bn.copy(this),t);const i=Bn.r,s=Bn.g,l=Bn.b;return t!==Ai?`color(${t} ${i.toFixed(3)} ${s.toFixed(3)} ${l.toFixed(3)})`:`rgb(${Math.round(i*255)},${Math.round(s*255)},${Math.round(l*255)})`}offsetHSL(t,i,s){return this.getHSL(ss),this.setHSL(ss.h+t,ss.s+i,ss.l+s)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,i){return this.r=t.r+i.r,this.g=t.g+i.g,this.b=t.b+i.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,i){return this.r+=(t.r-this.r)*i,this.g+=(t.g-this.g)*i,this.b+=(t.b-this.b)*i,this}lerpColors(t,i,s){return this.r=t.r+(i.r-t.r)*s,this.g=t.g+(i.g-t.g)*s,this.b=t.b+(i.b-t.b)*s,this}lerpHSL(t,i){this.getHSL(ss),t.getHSL(Mu);const s=_d(ss.h,Mu.h,i),l=_d(ss.s,Mu.s,i),c=_d(ss.l,Mu.l,i);return this.setHSL(s,l,c),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const i=this.r,s=this.g,l=this.b,c=t.elements;return this.r=c[0]*i+c[3]*s+c[6]*l,this.g=c[1]*i+c[4]*s+c[7]*l,this.b=c[2]*i+c[5]*s+c[8]*l,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,i=0){return this.r=t[i],this.g=t[i+1],this.b=t[i+2],this}toArray(t=[],i=0){return t[i]=this.r,t[i+1]=this.g,t[i+2]=this.b,t}fromBufferAttribute(t,i){return this.r=t.getX(i),this.g=t.getY(i),this.b=t.getZ(i),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Bn=new Oe;Oe.NAMES=gx;let fb=0;class tc extends Po{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:fb++}),this.uuid=Kl(),this.name="",this.type="Material",this.blending=fo,this.side=xs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=lp,this.blendDst=cp,this.blendEquation=Zs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Oe(0,0,0),this.blendAlpha=0,this.depthFunc=Co,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Sv,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Yr,this.stencilZFail=Yr,this.stencilZPass=Yr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const i in t){const s=t[i];if(s===void 0){console.warn(`THREE.Material: parameter '${i}' has value of undefined.`);continue}const l=this[i];if(l===void 0){console.warn(`THREE.Material: '${i}' is not a property of THREE.${this.type}.`);continue}l&&l.isColor?l.set(s):l&&l.isVector3&&s&&s.isVector3?l.copy(s):this[i]=s}}toJSON(t){const i=t===void 0||typeof t=="string";i&&(t={textures:{},images:{}});const s={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.color&&this.color.isColor&&(s.color=this.color.getHex()),this.roughness!==void 0&&(s.roughness=this.roughness),this.metalness!==void 0&&(s.metalness=this.metalness),this.sheen!==void 0&&(s.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(s.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(s.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(s.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(s.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(s.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(s.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(s.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(s.shininess=this.shininess),this.clearcoat!==void 0&&(s.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(s.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(s.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(s.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(s.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,s.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(s.dispersion=this.dispersion),this.iridescence!==void 0&&(s.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(s.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(s.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(s.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(s.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(s.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(s.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(s.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(s.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(s.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(s.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(s.lightMap=this.lightMap.toJSON(t).uuid,s.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(s.aoMap=this.aoMap.toJSON(t).uuid,s.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(s.bumpMap=this.bumpMap.toJSON(t).uuid,s.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(s.normalMap=this.normalMap.toJSON(t).uuid,s.normalMapType=this.normalMapType,s.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(s.displacementMap=this.displacementMap.toJSON(t).uuid,s.displacementScale=this.displacementScale,s.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(s.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(s.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(s.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(s.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(s.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(s.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(s.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(s.combine=this.combine)),this.envMapRotation!==void 0&&(s.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(s.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(s.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(s.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(s.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(s.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(s.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(s.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(s.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(s.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(s.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(s.size=this.size),this.shadowSide!==null&&(s.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(s.sizeAttenuation=this.sizeAttenuation),this.blending!==fo&&(s.blending=this.blending),this.side!==xs&&(s.side=this.side),this.vertexColors===!0&&(s.vertexColors=!0),this.opacity<1&&(s.opacity=this.opacity),this.transparent===!0&&(s.transparent=!0),this.blendSrc!==lp&&(s.blendSrc=this.blendSrc),this.blendDst!==cp&&(s.blendDst=this.blendDst),this.blendEquation!==Zs&&(s.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(s.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(s.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(s.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(s.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(s.blendAlpha=this.blendAlpha),this.depthFunc!==Co&&(s.depthFunc=this.depthFunc),this.depthTest===!1&&(s.depthTest=this.depthTest),this.depthWrite===!1&&(s.depthWrite=this.depthWrite),this.colorWrite===!1&&(s.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(s.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Sv&&(s.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(s.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(s.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Yr&&(s.stencilFail=this.stencilFail),this.stencilZFail!==Yr&&(s.stencilZFail=this.stencilZFail),this.stencilZPass!==Yr&&(s.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(s.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(s.rotation=this.rotation),this.polygonOffset===!0&&(s.polygonOffset=!0),this.polygonOffsetFactor!==0&&(s.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(s.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(s.linewidth=this.linewidth),this.dashSize!==void 0&&(s.dashSize=this.dashSize),this.gapSize!==void 0&&(s.gapSize=this.gapSize),this.scale!==void 0&&(s.scale=this.scale),this.dithering===!0&&(s.dithering=!0),this.alphaTest>0&&(s.alphaTest=this.alphaTest),this.alphaHash===!0&&(s.alphaHash=!0),this.alphaToCoverage===!0&&(s.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(s.premultipliedAlpha=!0),this.forceSinglePass===!0&&(s.forceSinglePass=!0),this.wireframe===!0&&(s.wireframe=!0),this.wireframeLinewidth>1&&(s.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(s.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(s.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(s.flatShading=!0),this.visible===!1&&(s.visible=!1),this.toneMapped===!1&&(s.toneMapped=!1),this.fog===!1&&(s.fog=!1),Object.keys(this.userData).length>0&&(s.userData=this.userData);function l(c){const h=[];for(const d in c){const m=c[d];delete m.metadata,h.push(m)}return h}if(i){const c=l(t.textures),h=l(t.images);c.length>0&&(s.textures=c),h.length>0&&(s.images=h)}return s}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const i=t.clippingPlanes;let s=null;if(i!==null){const l=i.length;s=new Array(l);for(let c=0;c!==l;++c)s[c]=i[c].clone()}return this.clippingPlanes=s,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Fl extends tc{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Oe(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ua,this.combine=Jy,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const gn=new Y,Eu=new Ae;class Ki{constructor(t,i,s=!1){if(Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=t,this.itemSize=i,this.count=t!==void 0?t.length/i:0,this.normalized=s,this.usage=Mv,this.updateRanges=[],this.gpuType=Ra,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,i){this.updateRanges.push({start:t,count:i})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,i,s){t*=this.itemSize,s*=i.itemSize;for(let l=0,c=this.itemSize;l<c;l++)this.array[t+l]=i.array[s+l];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let i=0,s=this.count;i<s;i++)Eu.fromBufferAttribute(this,i),Eu.applyMatrix3(t),this.setXY(i,Eu.x,Eu.y);else if(this.itemSize===3)for(let i=0,s=this.count;i<s;i++)gn.fromBufferAttribute(this,i),gn.applyMatrix3(t),this.setXYZ(i,gn.x,gn.y,gn.z);return this}applyMatrix4(t){for(let i=0,s=this.count;i<s;i++)gn.fromBufferAttribute(this,i),gn.applyMatrix4(t),this.setXYZ(i,gn.x,gn.y,gn.z);return this}applyNormalMatrix(t){for(let i=0,s=this.count;i<s;i++)gn.fromBufferAttribute(this,i),gn.applyNormalMatrix(t),this.setXYZ(i,gn.x,gn.y,gn.z);return this}transformDirection(t){for(let i=0,s=this.count;i<s;i++)gn.fromBufferAttribute(this,i),gn.transformDirection(t),this.setXYZ(i,gn.x,gn.y,gn.z);return this}set(t,i=0){return this.array.set(t,i),this}getComponent(t,i){let s=this.array[t*this.itemSize+i];return this.normalized&&(s=Dl(s,this.array)),s}setComponent(t,i,s){return this.normalized&&(s=Jn(s,this.array)),this.array[t*this.itemSize+i]=s,this}getX(t){let i=this.array[t*this.itemSize];return this.normalized&&(i=Dl(i,this.array)),i}setX(t,i){return this.normalized&&(i=Jn(i,this.array)),this.array[t*this.itemSize]=i,this}getY(t){let i=this.array[t*this.itemSize+1];return this.normalized&&(i=Dl(i,this.array)),i}setY(t,i){return this.normalized&&(i=Jn(i,this.array)),this.array[t*this.itemSize+1]=i,this}getZ(t){let i=this.array[t*this.itemSize+2];return this.normalized&&(i=Dl(i,this.array)),i}setZ(t,i){return this.normalized&&(i=Jn(i,this.array)),this.array[t*this.itemSize+2]=i,this}getW(t){let i=this.array[t*this.itemSize+3];return this.normalized&&(i=Dl(i,this.array)),i}setW(t,i){return this.normalized&&(i=Jn(i,this.array)),this.array[t*this.itemSize+3]=i,this}setXY(t,i,s){return t*=this.itemSize,this.normalized&&(i=Jn(i,this.array),s=Jn(s,this.array)),this.array[t+0]=i,this.array[t+1]=s,this}setXYZ(t,i,s,l){return t*=this.itemSize,this.normalized&&(i=Jn(i,this.array),s=Jn(s,this.array),l=Jn(l,this.array)),this.array[t+0]=i,this.array[t+1]=s,this.array[t+2]=l,this}setXYZW(t,i,s,l,c){return t*=this.itemSize,this.normalized&&(i=Jn(i,this.array),s=Jn(s,this.array),l=Jn(l,this.array),c=Jn(c,this.array)),this.array[t+0]=i,this.array[t+1]=s,this.array[t+2]=l,this.array[t+3]=c,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==Mv&&(t.usage=this.usage),t}}class _x extends Ki{constructor(t,i,s){super(new Uint16Array(t),i,s)}}class vx extends Ki{constructor(t,i,s){super(new Uint32Array(t),i,s)}}class Ln extends Ki{constructor(t,i,s){super(new Float32Array(t),i,s)}}let hb=0;const bi=new Je,Pd=new jn,ao=new Y,fi=new $l,Ol=new $l,bn=new Y;class mi extends Po{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:hb++}),this.uuid=Kl(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(fx(t)?vx:_x)(t,1):this.index=t,this}setIndirect(t){return this.indirect=t,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,i){return this.attributes[t]=i,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,i,s=0){this.groups.push({start:t,count:i,materialIndex:s})}clearGroups(){this.groups=[]}setDrawRange(t,i){this.drawRange.start=t,this.drawRange.count=i}applyMatrix4(t){const i=this.attributes.position;i!==void 0&&(i.applyMatrix4(t),i.needsUpdate=!0);const s=this.attributes.normal;if(s!==void 0){const c=new ue().getNormalMatrix(t);s.applyNormalMatrix(c),s.needsUpdate=!0}const l=this.attributes.tangent;return l!==void 0&&(l.transformDirection(t),l.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return bi.makeRotationFromQuaternion(t),this.applyMatrix4(bi),this}rotateX(t){return bi.makeRotationX(t),this.applyMatrix4(bi),this}rotateY(t){return bi.makeRotationY(t),this.applyMatrix4(bi),this}rotateZ(t){return bi.makeRotationZ(t),this.applyMatrix4(bi),this}translate(t,i,s){return bi.makeTranslation(t,i,s),this.applyMatrix4(bi),this}scale(t,i,s){return bi.makeScale(t,i,s),this.applyMatrix4(bi),this}lookAt(t){return Pd.lookAt(t),Pd.updateMatrix(),this.applyMatrix4(Pd.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(ao).negate(),this.translate(ao.x,ao.y,ao.z),this}setFromPoints(t){const i=this.getAttribute("position");if(i===void 0){const s=[];for(let l=0,c=t.length;l<c;l++){const h=t[l];s.push(h.x,h.y,h.z||0)}this.setAttribute("position",new Ln(s,3))}else{const s=Math.min(t.length,i.count);for(let l=0;l<s;l++){const c=t[l];i.setXYZ(l,c.x,c.y,c.z||0)}t.length>i.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),i.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new $l);const t=this.attributes.position,i=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new Y(-1/0,-1/0,-1/0),new Y(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),i)for(let s=0,l=i.length;s<l;s++){const c=i[s];fi.setFromBufferAttribute(c),this.morphTargetsRelative?(bn.addVectors(this.boundingBox.min,fi.min),this.boundingBox.expandByPoint(bn),bn.addVectors(this.boundingBox.max,fi.max),this.boundingBox.expandByPoint(bn)):(this.boundingBox.expandByPoint(fi.min),this.boundingBox.expandByPoint(fi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Ju);const t=this.attributes.position,i=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new Y,1/0);return}if(t){const s=this.boundingSphere.center;if(fi.setFromBufferAttribute(t),i)for(let c=0,h=i.length;c<h;c++){const d=i[c];Ol.setFromBufferAttribute(d),this.morphTargetsRelative?(bn.addVectors(fi.min,Ol.min),fi.expandByPoint(bn),bn.addVectors(fi.max,Ol.max),fi.expandByPoint(bn)):(fi.expandByPoint(Ol.min),fi.expandByPoint(Ol.max))}fi.getCenter(s);let l=0;for(let c=0,h=t.count;c<h;c++)bn.fromBufferAttribute(t,c),l=Math.max(l,s.distanceToSquared(bn));if(i)for(let c=0,h=i.length;c<h;c++){const d=i[c],m=this.morphTargetsRelative;for(let p=0,g=d.count;p<g;p++)bn.fromBufferAttribute(d,p),m&&(ao.fromBufferAttribute(t,p),bn.add(ao)),l=Math.max(l,s.distanceToSquared(bn))}this.boundingSphere.radius=Math.sqrt(l),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,i=this.attributes;if(t===null||i.position===void 0||i.normal===void 0||i.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const s=i.position,l=i.normal,c=i.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Ki(new Float32Array(4*s.count),4));const h=this.getAttribute("tangent"),d=[],m=[];for(let H=0;H<s.count;H++)d[H]=new Y,m[H]=new Y;const p=new Y,g=new Y,_=new Y,x=new Ae,S=new Ae,E=new Ae,b=new Y,M=new Y;function v(H,D,C){p.fromBufferAttribute(s,H),g.fromBufferAttribute(s,D),_.fromBufferAttribute(s,C),x.fromBufferAttribute(c,H),S.fromBufferAttribute(c,D),E.fromBufferAttribute(c,C),g.sub(p),_.sub(p),S.sub(x),E.sub(x);const G=1/(S.x*E.y-E.x*S.y);isFinite(G)&&(b.copy(g).multiplyScalar(E.y).addScaledVector(_,-S.y).multiplyScalar(G),M.copy(_).multiplyScalar(S.x).addScaledVector(g,-E.x).multiplyScalar(G),d[H].add(b),d[D].add(b),d[C].add(b),m[H].add(M),m[D].add(M),m[C].add(M))}let L=this.groups;L.length===0&&(L=[{start:0,count:t.count}]);for(let H=0,D=L.length;H<D;++H){const C=L[H],G=C.start,ot=C.count;for(let lt=G,mt=G+ot;lt<mt;lt+=3)v(t.getX(lt+0),t.getX(lt+1),t.getX(lt+2))}const U=new Y,T=new Y,V=new Y,I=new Y;function P(H){V.fromBufferAttribute(l,H),I.copy(V);const D=d[H];U.copy(D),U.sub(V.multiplyScalar(V.dot(D))).normalize(),T.crossVectors(I,D);const G=T.dot(m[H])<0?-1:1;h.setXYZW(H,U.x,U.y,U.z,G)}for(let H=0,D=L.length;H<D;++H){const C=L[H],G=C.start,ot=C.count;for(let lt=G,mt=G+ot;lt<mt;lt+=3)P(t.getX(lt+0)),P(t.getX(lt+1)),P(t.getX(lt+2))}}computeVertexNormals(){const t=this.index,i=this.getAttribute("position");if(i!==void 0){let s=this.getAttribute("normal");if(s===void 0)s=new Ki(new Float32Array(i.count*3),3),this.setAttribute("normal",s);else for(let x=0,S=s.count;x<S;x++)s.setXYZ(x,0,0,0);const l=new Y,c=new Y,h=new Y,d=new Y,m=new Y,p=new Y,g=new Y,_=new Y;if(t)for(let x=0,S=t.count;x<S;x+=3){const E=t.getX(x+0),b=t.getX(x+1),M=t.getX(x+2);l.fromBufferAttribute(i,E),c.fromBufferAttribute(i,b),h.fromBufferAttribute(i,M),g.subVectors(h,c),_.subVectors(l,c),g.cross(_),d.fromBufferAttribute(s,E),m.fromBufferAttribute(s,b),p.fromBufferAttribute(s,M),d.add(g),m.add(g),p.add(g),s.setXYZ(E,d.x,d.y,d.z),s.setXYZ(b,m.x,m.y,m.z),s.setXYZ(M,p.x,p.y,p.z)}else for(let x=0,S=i.count;x<S;x+=3)l.fromBufferAttribute(i,x+0),c.fromBufferAttribute(i,x+1),h.fromBufferAttribute(i,x+2),g.subVectors(h,c),_.subVectors(l,c),g.cross(_),s.setXYZ(x+0,g.x,g.y,g.z),s.setXYZ(x+1,g.x,g.y,g.z),s.setXYZ(x+2,g.x,g.y,g.z);this.normalizeNormals(),s.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let i=0,s=t.count;i<s;i++)bn.fromBufferAttribute(t,i),bn.normalize(),t.setXYZ(i,bn.x,bn.y,bn.z)}toNonIndexed(){function t(d,m){const p=d.array,g=d.itemSize,_=d.normalized,x=new p.constructor(m.length*g);let S=0,E=0;for(let b=0,M=m.length;b<M;b++){d.isInterleavedBufferAttribute?S=m[b]*d.data.stride+d.offset:S=m[b]*g;for(let v=0;v<g;v++)x[E++]=p[S++]}return new Ki(x,g,_)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const i=new mi,s=this.index.array,l=this.attributes;for(const d in l){const m=l[d],p=t(m,s);i.setAttribute(d,p)}const c=this.morphAttributes;for(const d in c){const m=[],p=c[d];for(let g=0,_=p.length;g<_;g++){const x=p[g],S=t(x,s);m.push(S)}i.morphAttributes[d]=m}i.morphTargetsRelative=this.morphTargetsRelative;const h=this.groups;for(let d=0,m=h.length;d<m;d++){const p=h[d];i.addGroup(p.start,p.count,p.materialIndex)}return i}toJSON(){const t={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const m=this.parameters;for(const p in m)m[p]!==void 0&&(t[p]=m[p]);return t}t.data={attributes:{}};const i=this.index;i!==null&&(t.data.index={type:i.array.constructor.name,array:Array.prototype.slice.call(i.array)});const s=this.attributes;for(const m in s){const p=s[m];t.data.attributes[m]=p.toJSON(t.data)}const l={};let c=!1;for(const m in this.morphAttributes){const p=this.morphAttributes[m],g=[];for(let _=0,x=p.length;_<x;_++){const S=p[_];g.push(S.toJSON(t.data))}g.length>0&&(l[m]=g,c=!0)}c&&(t.data.morphAttributes=l,t.data.morphTargetsRelative=this.morphTargetsRelative);const h=this.groups;h.length>0&&(t.data.groups=JSON.parse(JSON.stringify(h)));const d=this.boundingSphere;return d!==null&&(t.data.boundingSphere={center:d.center.toArray(),radius:d.radius}),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const i={};this.name=t.name;const s=t.index;s!==null&&this.setIndex(s.clone(i));const l=t.attributes;for(const p in l){const g=l[p];this.setAttribute(p,g.clone(i))}const c=t.morphAttributes;for(const p in c){const g=[],_=c[p];for(let x=0,S=_.length;x<S;x++)g.push(_[x].clone(i));this.morphAttributes[p]=g}this.morphTargetsRelative=t.morphTargetsRelative;const h=t.groups;for(let p=0,g=h.length;p<g;p++){const _=h[p];this.addGroup(_.start,_.count,_.materialIndex)}const d=t.boundingBox;d!==null&&(this.boundingBox=d.clone());const m=t.boundingSphere;return m!==null&&(this.boundingSphere=m.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const zv=new Je,Xs=new px,bu=new Ju,Iv=new Y,Tu=new Y,Au=new Y,Ru=new Y,zd=new Y,Cu=new Y,Bv=new Y,wu=new Y;class Ri extends jn{constructor(t=new mi,i=new Fl){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=i,this.updateMorphTargets()}copy(t,i){return super.copy(t,i),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const i=this.geometry.morphAttributes,s=Object.keys(i);if(s.length>0){const l=i[s[0]];if(l!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,h=l.length;c<h;c++){const d=l[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}getVertexPosition(t,i){const s=this.geometry,l=s.attributes.position,c=s.morphAttributes.position,h=s.morphTargetsRelative;i.fromBufferAttribute(l,t);const d=this.morphTargetInfluences;if(c&&d){Cu.set(0,0,0);for(let m=0,p=c.length;m<p;m++){const g=d[m],_=c[m];g!==0&&(zd.fromBufferAttribute(_,t),h?Cu.addScaledVector(zd,g):Cu.addScaledVector(zd.sub(i),g))}i.add(Cu)}return i}raycast(t,i){const s=this.geometry,l=this.material,c=this.matrixWorld;l!==void 0&&(s.boundingSphere===null&&s.computeBoundingSphere(),bu.copy(s.boundingSphere),bu.applyMatrix4(c),Xs.copy(t.ray).recast(t.near),!(bu.containsPoint(Xs.origin)===!1&&(Xs.intersectSphere(bu,Iv)===null||Xs.origin.distanceToSquared(Iv)>(t.far-t.near)**2))&&(zv.copy(c).invert(),Xs.copy(t.ray).applyMatrix4(zv),!(s.boundingBox!==null&&Xs.intersectsBox(s.boundingBox)===!1)&&this._computeIntersections(t,i,Xs)))}_computeIntersections(t,i,s){let l;const c=this.geometry,h=this.material,d=c.index,m=c.attributes.position,p=c.attributes.uv,g=c.attributes.uv1,_=c.attributes.normal,x=c.groups,S=c.drawRange;if(d!==null)if(Array.isArray(h))for(let E=0,b=x.length;E<b;E++){const M=x[E],v=h[M.materialIndex],L=Math.max(M.start,S.start),U=Math.min(d.count,Math.min(M.start+M.count,S.start+S.count));for(let T=L,V=U;T<V;T+=3){const I=d.getX(T),P=d.getX(T+1),H=d.getX(T+2);l=Du(this,v,t,s,p,g,_,I,P,H),l&&(l.faceIndex=Math.floor(T/3),l.face.materialIndex=M.materialIndex,i.push(l))}}else{const E=Math.max(0,S.start),b=Math.min(d.count,S.start+S.count);for(let M=E,v=b;M<v;M+=3){const L=d.getX(M),U=d.getX(M+1),T=d.getX(M+2);l=Du(this,h,t,s,p,g,_,L,U,T),l&&(l.faceIndex=Math.floor(M/3),i.push(l))}}else if(m!==void 0)if(Array.isArray(h))for(let E=0,b=x.length;E<b;E++){const M=x[E],v=h[M.materialIndex],L=Math.max(M.start,S.start),U=Math.min(m.count,Math.min(M.start+M.count,S.start+S.count));for(let T=L,V=U;T<V;T+=3){const I=T,P=T+1,H=T+2;l=Du(this,v,t,s,p,g,_,I,P,H),l&&(l.faceIndex=Math.floor(T/3),l.face.materialIndex=M.materialIndex,i.push(l))}}else{const E=Math.max(0,S.start),b=Math.min(m.count,S.start+S.count);for(let M=E,v=b;M<v;M+=3){const L=M,U=M+1,T=M+2;l=Du(this,h,t,s,p,g,_,L,U,T),l&&(l.faceIndex=Math.floor(M/3),i.push(l))}}}}function db(r,t,i,s,l,c,h,d){let m;if(t.side===ei?m=s.intersectTriangle(h,c,l,!0,d):m=s.intersectTriangle(l,c,h,t.side===xs,d),m===null)return null;wu.copy(d),wu.applyMatrix4(r.matrixWorld);const p=i.ray.origin.distanceTo(wu);return p<i.near||p>i.far?null:{distance:p,point:wu.clone(),object:r}}function Du(r,t,i,s,l,c,h,d,m,p){r.getVertexPosition(d,Tu),r.getVertexPosition(m,Au),r.getVertexPosition(p,Ru);const g=db(r,t,i,s,Tu,Au,Ru,Bv);if(g){const _=new Y;Ii.getBarycoord(Bv,Tu,Au,Ru,_),l&&(g.uv=Ii.getInterpolatedAttribute(l,d,m,p,_,new Ae)),c&&(g.uv1=Ii.getInterpolatedAttribute(c,d,m,p,_,new Ae)),h&&(g.normal=Ii.getInterpolatedAttribute(h,d,m,p,_,new Y),g.normal.dot(s.direction)>0&&g.normal.multiplyScalar(-1));const x={a:d,b:m,c:p,normal:new Y,materialIndex:0};Ii.getNormal(Tu,Au,Ru,x.normal),g.face=x,g.barycoord=_}return g}class ec extends mi{constructor(t=1,i=1,s=1,l=1,c=1,h=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:i,depth:s,widthSegments:l,heightSegments:c,depthSegments:h};const d=this;l=Math.floor(l),c=Math.floor(c),h=Math.floor(h);const m=[],p=[],g=[],_=[];let x=0,S=0;E("z","y","x",-1,-1,s,i,t,h,c,0),E("z","y","x",1,-1,s,i,-t,h,c,1),E("x","z","y",1,1,t,s,i,l,h,2),E("x","z","y",1,-1,t,s,-i,l,h,3),E("x","y","z",1,-1,t,i,s,l,c,4),E("x","y","z",-1,-1,t,i,-s,l,c,5),this.setIndex(m),this.setAttribute("position",new Ln(p,3)),this.setAttribute("normal",new Ln(g,3)),this.setAttribute("uv",new Ln(_,2));function E(b,M,v,L,U,T,V,I,P,H,D){const C=T/P,G=V/H,ot=T/2,lt=V/2,mt=I/2,gt=P+1,B=H+1;let $=0,J=0;const Et=new Y;for(let At=0;At<B;At++){const z=At*G-lt;for(let at=0;at<gt;at++){const Mt=at*C-ot;Et[b]=Mt*L,Et[M]=z*U,Et[v]=mt,p.push(Et.x,Et.y,Et.z),Et[b]=0,Et[M]=0,Et[v]=I>0?1:-1,g.push(Et.x,Et.y,Et.z),_.push(at/P),_.push(1-At/H),$+=1}}for(let At=0;At<H;At++)for(let z=0;z<P;z++){const at=x+z+gt*At,Mt=x+z+gt*(At+1),K=x+(z+1)+gt*(At+1),ft=x+(z+1)+gt*At;m.push(at,Mt,ft),m.push(Mt,K,ft),J+=6}d.addGroup(S,J,D),S+=J,x+=$}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new ec(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}function Oo(r){const t={};for(const i in r){t[i]={};for(const s in r[i]){const l=r[i][s];l&&(l.isColor||l.isMatrix3||l.isMatrix4||l.isVector2||l.isVector3||l.isVector4||l.isTexture||l.isQuaternion)?l.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[i][s]=null):t[i][s]=l.clone():Array.isArray(l)?t[i][s]=l.slice():t[i][s]=l}}return t}function kn(r){const t={};for(let i=0;i<r.length;i++){const s=Oo(r[i]);for(const l in s)t[l]=s[l]}return t}function pb(r){const t=[];for(let i=0;i<r.length;i++)t.push(r[i].clone());return t}function yx(r){const t=r.getRenderTarget();return t===null?r.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Ne.workingColorSpace}const mb={clone:Oo,merge:kn};var gb=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,_b=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Ss extends tc{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=gb,this.fragmentShader=_b,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Oo(t.uniforms),this.uniformsGroups=pb(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this}toJSON(t){const i=super.toJSON(t);i.glslVersion=this.glslVersion,i.uniforms={};for(const l in this.uniforms){const h=this.uniforms[l].value;h&&h.isTexture?i.uniforms[l]={type:"t",value:h.toJSON(t).uuid}:h&&h.isColor?i.uniforms[l]={type:"c",value:h.getHex()}:h&&h.isVector2?i.uniforms[l]={type:"v2",value:h.toArray()}:h&&h.isVector3?i.uniforms[l]={type:"v3",value:h.toArray()}:h&&h.isVector4?i.uniforms[l]={type:"v4",value:h.toArray()}:h&&h.isMatrix3?i.uniforms[l]={type:"m3",value:h.toArray()}:h&&h.isMatrix4?i.uniforms[l]={type:"m4",value:h.toArray()}:i.uniforms[l]={value:h}}Object.keys(this.defines).length>0&&(i.defines=this.defines),i.vertexShader=this.vertexShader,i.fragmentShader=this.fragmentShader,i.lights=this.lights,i.clipping=this.clipping;const s={};for(const l in this.extensions)this.extensions[l]===!0&&(s[l]=!0);return Object.keys(s).length>0&&(i.extensions=s),i}}class xx extends jn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Je,this.projectionMatrix=new Je,this.projectionMatrixInverse=new Je,this.coordinateSystem=Ca}copy(t,i){return super.copy(t,i),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(t,i){super.updateWorldMatrix(t,i),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const rs=new Y,Fv=new Ae,Hv=new Ae;class pi extends xx{constructor(t=50,i=1,s=.1,l=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=s,this.far=l,this.focus=10,this.aspect=i,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,i){return super.copy(t,i),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const i=.5*this.getFilmHeight()/t;this.fov=Wp*2*Math.atan(i),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(gd*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return Wp*2*Math.atan(Math.tan(gd*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,i,s){rs.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),i.set(rs.x,rs.y).multiplyScalar(-t/rs.z),rs.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),s.set(rs.x,rs.y).multiplyScalar(-t/rs.z)}getViewSize(t,i){return this.getViewBounds(t,Fv,Hv),i.subVectors(Hv,Fv)}setViewOffset(t,i,s,l,c,h){this.aspect=t/i,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=i,this.view.offsetX=s,this.view.offsetY=l,this.view.width=c,this.view.height=h,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let i=t*Math.tan(gd*.5*this.fov)/this.zoom,s=2*i,l=this.aspect*s,c=-.5*l;const h=this.view;if(this.view!==null&&this.view.enabled){const m=h.fullWidth,p=h.fullHeight;c+=h.offsetX*l/m,i-=h.offsetY*s/p,l*=h.width/m,s*=h.height/p}const d=this.filmOffset;d!==0&&(c+=t*d/this.getFilmWidth()),this.projectionMatrix.makePerspective(c,c+l,i,i-s,t,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const i=super.toJSON(t);return i.object.fov=this.fov,i.object.zoom=this.zoom,i.object.near=this.near,i.object.far=this.far,i.object.focus=this.focus,i.object.aspect=this.aspect,this.view!==null&&(i.object.view=Object.assign({},this.view)),i.object.filmGauge=this.filmGauge,i.object.filmOffset=this.filmOffset,i}}const so=-90,ro=1;class vb extends jn{constructor(t,i,s){super(),this.type="CubeCamera",this.renderTarget=s,this.coordinateSystem=null,this.activeMipmapLevel=0;const l=new pi(so,ro,t,i);l.layers=this.layers,this.add(l);const c=new pi(so,ro,t,i);c.layers=this.layers,this.add(c);const h=new pi(so,ro,t,i);h.layers=this.layers,this.add(h);const d=new pi(so,ro,t,i);d.layers=this.layers,this.add(d);const m=new pi(so,ro,t,i);m.layers=this.layers,this.add(m);const p=new pi(so,ro,t,i);p.layers=this.layers,this.add(p)}updateCoordinateSystem(){const t=this.coordinateSystem,i=this.children.concat(),[s,l,c,h,d,m]=i;for(const p of i)this.remove(p);if(t===Ca)s.up.set(0,1,0),s.lookAt(1,0,0),l.up.set(0,1,0),l.lookAt(-1,0,0),c.up.set(0,0,-1),c.lookAt(0,1,0),h.up.set(0,0,1),h.lookAt(0,-1,0),d.up.set(0,1,0),d.lookAt(0,0,1),m.up.set(0,1,0),m.lookAt(0,0,-1);else if(t===Wu)s.up.set(0,-1,0),s.lookAt(-1,0,0),l.up.set(0,-1,0),l.lookAt(1,0,0),c.up.set(0,0,1),c.lookAt(0,1,0),h.up.set(0,0,-1),h.lookAt(0,-1,0),d.up.set(0,-1,0),d.lookAt(0,0,1),m.up.set(0,-1,0),m.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const p of i)this.add(p),p.updateMatrixWorld()}update(t,i){this.parent===null&&this.updateMatrixWorld();const{renderTarget:s,activeMipmapLevel:l}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[c,h,d,m,p,g]=this.children,_=t.getRenderTarget(),x=t.getActiveCubeFace(),S=t.getActiveMipmapLevel(),E=t.xr.enabled;t.xr.enabled=!1;const b=s.texture.generateMipmaps;s.texture.generateMipmaps=!1,t.setRenderTarget(s,0,l),t.render(i,c),t.setRenderTarget(s,1,l),t.render(i,h),t.setRenderTarget(s,2,l),t.render(i,d),t.setRenderTarget(s,3,l),t.render(i,m),t.setRenderTarget(s,4,l),t.render(i,p),s.texture.generateMipmaps=b,t.setRenderTarget(s,5,l),t.render(i,g),t.setRenderTarget(_,x,S),t.xr.enabled=E,s.texture.needsPMREMUpdate=!0}}class Sx extends ni{constructor(t,i,s,l,c,h,d,m,p,g){t=t!==void 0?t:[],i=i!==void 0?i:wo,super(t,i,s,l,c,h,d,m,p,g),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class yb extends dr{constructor(t=1,i={}){super(t,t,i),this.isWebGLCubeRenderTarget=!0;const s={width:t,height:t,depth:1},l=[s,s,s,s,s,s];this.texture=new Sx(l,i.mapping,i.wrapS,i.wrapT,i.magFilter,i.minFilter,i.format,i.type,i.anisotropy,i.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=i.generateMipmaps!==void 0?i.generateMipmaps:!1,this.texture.minFilter=i.minFilter!==void 0?i.minFilter:Zi}fromEquirectangularTexture(t,i){this.texture.type=i.type,this.texture.colorSpace=i.colorSpace,this.texture.generateMipmaps=i.generateMipmaps,this.texture.minFilter=i.minFilter,this.texture.magFilter=i.magFilter;const s={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},l=new ec(5,5,5),c=new Ss({name:"CubemapFromEquirect",uniforms:Oo(s.uniforms),vertexShader:s.vertexShader,fragmentShader:s.fragmentShader,side:ei,blending:vs});c.uniforms.tEquirect.value=i;const h=new Ri(l,c),d=i.minFilter;return i.minFilter===er&&(i.minFilter=Zi),new vb(1,10,this).update(t,h),i.minFilter=d,h.geometry.dispose(),h.material.dispose(),this}clear(t,i,s,l){const c=t.getRenderTarget();for(let h=0;h<6;h++)t.setRenderTarget(this,h),t.clear(i,s,l);t.setRenderTarget(c)}}class xb extends jn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ua,this.environmentIntensity=1,this.environmentRotation=new Ua,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,i){return super.copy(t,i),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const i=super.toJSON(t);return this.fog!==null&&(i.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(i.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(i.object.backgroundIntensity=this.backgroundIntensity),i.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(i.object.environmentIntensity=this.environmentIntensity),i.object.environmentRotation=this.environmentRotation.toArray(),i}}const Id=new Y,Sb=new Y,Mb=new ue;class Ys{constructor(t=new Y(1,0,0),i=0){this.isPlane=!0,this.normal=t,this.constant=i}set(t,i){return this.normal.copy(t),this.constant=i,this}setComponents(t,i,s,l){return this.normal.set(t,i,s),this.constant=l,this}setFromNormalAndCoplanarPoint(t,i){return this.normal.copy(t),this.constant=-i.dot(this.normal),this}setFromCoplanarPoints(t,i,s){const l=Id.subVectors(s,i).cross(Sb.subVectors(t,i)).normalize();return this.setFromNormalAndCoplanarPoint(l,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,i){return i.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,i){const s=t.delta(Id),l=this.normal.dot(s);if(l===0)return this.distanceToPoint(t.start)===0?i.copy(t.start):null;const c=-(t.start.dot(this.normal)+this.constant)/l;return c<0||c>1?null:i.copy(t.start).addScaledVector(s,c)}intersectsLine(t){const i=this.distanceToPoint(t.start),s=this.distanceToPoint(t.end);return i<0&&s>0||s<0&&i>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,i){const s=i||Mb.getNormalMatrix(t),l=this.coplanarPoint(Id).applyMatrix4(t),c=this.normal.applyMatrix3(s).normalize();return this.constant=-l.dot(c),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const js=new Ju,Uu=new Y;class cm{constructor(t=new Ys,i=new Ys,s=new Ys,l=new Ys,c=new Ys,h=new Ys){this.planes=[t,i,s,l,c,h]}set(t,i,s,l,c,h){const d=this.planes;return d[0].copy(t),d[1].copy(i),d[2].copy(s),d[3].copy(l),d[4].copy(c),d[5].copy(h),this}copy(t){const i=this.planes;for(let s=0;s<6;s++)i[s].copy(t.planes[s]);return this}setFromProjectionMatrix(t,i=Ca){const s=this.planes,l=t.elements,c=l[0],h=l[1],d=l[2],m=l[3],p=l[4],g=l[5],_=l[6],x=l[7],S=l[8],E=l[9],b=l[10],M=l[11],v=l[12],L=l[13],U=l[14],T=l[15];if(s[0].setComponents(m-c,x-p,M-S,T-v).normalize(),s[1].setComponents(m+c,x+p,M+S,T+v).normalize(),s[2].setComponents(m+h,x+g,M+E,T+L).normalize(),s[3].setComponents(m-h,x-g,M-E,T-L).normalize(),s[4].setComponents(m-d,x-_,M-b,T-U).normalize(),i===Ca)s[5].setComponents(m+d,x+_,M+b,T+U).normalize();else if(i===Wu)s[5].setComponents(d,_,b,U).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+i);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),js.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const i=t.geometry;i.boundingSphere===null&&i.computeBoundingSphere(),js.copy(i.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(js)}intersectsSprite(t){return js.center.set(0,0,0),js.radius=.7071067811865476,js.applyMatrix4(t.matrixWorld),this.intersectsSphere(js)}intersectsSphere(t){const i=this.planes,s=t.center,l=-t.radius;for(let c=0;c<6;c++)if(i[c].distanceToPoint(s)<l)return!1;return!0}intersectsBox(t){const i=this.planes;for(let s=0;s<6;s++){const l=i[s];if(Uu.x=l.normal.x>0?t.max.x:t.min.x,Uu.y=l.normal.y>0?t.max.y:t.min.y,Uu.z=l.normal.z>0?t.max.z:t.min.z,l.distanceToPoint(Uu)<0)return!1}return!0}containsPoint(t){const i=this.planes;for(let s=0;s<6;s++)if(i[s].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class Yp extends tc{constructor(t){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new Oe(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.linewidth=t.linewidth,this.linecap=t.linecap,this.linejoin=t.linejoin,this.fog=t.fog,this}}const Qu=new Y,Zu=new Y,Gv=new Je,Pl=new px,Nu=new Ju,Bd=new Y,Vv=new Y;class kv extends jn{constructor(t=new mi,i=new Yp){super(),this.isLine=!0,this.type="Line",this.geometry=t,this.material=i,this.updateMorphTargets()}copy(t,i){return super.copy(t,i),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}computeLineDistances(){const t=this.geometry;if(t.index===null){const i=t.attributes.position,s=[0];for(let l=1,c=i.count;l<c;l++)Qu.fromBufferAttribute(i,l-1),Zu.fromBufferAttribute(i,l),s[l]=s[l-1],s[l]+=Qu.distanceTo(Zu);t.setAttribute("lineDistance",new Ln(s,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(t,i){const s=this.geometry,l=this.matrixWorld,c=t.params.Line.threshold,h=s.drawRange;if(s.boundingSphere===null&&s.computeBoundingSphere(),Nu.copy(s.boundingSphere),Nu.applyMatrix4(l),Nu.radius+=c,t.ray.intersectsSphere(Nu)===!1)return;Gv.copy(l).invert(),Pl.copy(t.ray).applyMatrix4(Gv);const d=c/((this.scale.x+this.scale.y+this.scale.z)/3),m=d*d,p=this.isLineSegments?2:1,g=s.index,x=s.attributes.position;if(g!==null){const S=Math.max(0,h.start),E=Math.min(g.count,h.start+h.count);for(let b=S,M=E-1;b<M;b+=p){const v=g.getX(b),L=g.getX(b+1),U=Lu(this,t,Pl,m,v,L);U&&i.push(U)}if(this.isLineLoop){const b=g.getX(E-1),M=g.getX(S),v=Lu(this,t,Pl,m,b,M);v&&i.push(v)}}else{const S=Math.max(0,h.start),E=Math.min(x.count,h.start+h.count);for(let b=S,M=E-1;b<M;b+=p){const v=Lu(this,t,Pl,m,b,b+1);v&&i.push(v)}if(this.isLineLoop){const b=Lu(this,t,Pl,m,E-1,S);b&&i.push(b)}}}updateMorphTargets(){const i=this.geometry.morphAttributes,s=Object.keys(i);if(s.length>0){const l=i[s[0]];if(l!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,h=l.length;c<h;c++){const d=l[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}}function Lu(r,t,i,s,l,c){const h=r.geometry.attributes.position;if(Qu.fromBufferAttribute(h,l),Zu.fromBufferAttribute(h,c),i.distanceSqToSegment(Qu,Zu,Bd,Vv)>s)return;Bd.applyMatrix4(r.matrixWorld);const m=t.ray.origin.distanceTo(Bd);if(!(m<t.near||m>t.far))return{distance:m,point:Vv.clone().applyMatrix4(r.matrixWorld),index:l,face:null,faceIndex:null,barycoord:null,object:r}}class co extends jn{constructor(){super(),this.isGroup=!0,this.type="Group"}}class Mx extends ni{constructor(t,i,s,l,c,h,d,m,p,g=ho){if(g!==ho&&g!==No)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");s===void 0&&g===ho&&(s=hr),s===void 0&&g===No&&(s=Uo),super(null,l,c,h,d,m,g,s,p),this.isDepthTexture=!0,this.image={width:t,height:i},this.magFilter=d!==void 0?d:Fi,this.minFilter=m!==void 0?m:Fi,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.compareFunction=t.compareFunction,this}toJSON(t){const i=super.toJSON(t);return this.compareFunction!==null&&(i.compareFunction=this.compareFunction),i}}class Eb{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(t,i){const s=this.getUtoTmapping(t);return this.getPoint(s,i)}getPoints(t=5){const i=[];for(let s=0;s<=t;s++)i.push(this.getPoint(s/t));return i}getSpacedPoints(t=5){const i=[];for(let s=0;s<=t;s++)i.push(this.getPointAt(s/t));return i}getLength(){const t=this.getLengths();return t[t.length-1]}getLengths(t=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===t+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const i=[];let s,l=this.getPoint(0),c=0;i.push(0);for(let h=1;h<=t;h++)s=this.getPoint(h/t),c+=s.distanceTo(l),i.push(c),l=s;return this.cacheArcLengths=i,i}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(t,i){const s=this.getLengths();let l=0;const c=s.length;let h;i?h=i:h=t*s[c-1];let d=0,m=c-1,p;for(;d<=m;)if(l=Math.floor(d+(m-d)/2),p=s[l]-h,p<0)d=l+1;else if(p>0)m=l-1;else{m=l;break}if(l=m,s[l]===h)return l/(c-1);const g=s[l],x=s[l+1]-g,S=(h-g)/x;return(l+S)/(c-1)}getTangent(t,i){let l=t-1e-4,c=t+1e-4;l<0&&(l=0),c>1&&(c=1);const h=this.getPoint(l),d=this.getPoint(c),m=i||(h.isVector2?new Ae:new Y);return m.copy(d).sub(h).normalize(),m}getTangentAt(t,i){const s=this.getUtoTmapping(t);return this.getTangent(s,i)}computeFrenetFrames(t,i){const s=new Y,l=[],c=[],h=[],d=new Y,m=new Je;for(let S=0;S<=t;S++){const E=S/t;l[S]=this.getTangentAt(E,new Y)}c[0]=new Y,h[0]=new Y;let p=Number.MAX_VALUE;const g=Math.abs(l[0].x),_=Math.abs(l[0].y),x=Math.abs(l[0].z);g<=p&&(p=g,s.set(1,0,0)),_<=p&&(p=_,s.set(0,1,0)),x<=p&&s.set(0,0,1),d.crossVectors(l[0],s).normalize(),c[0].crossVectors(l[0],d),h[0].crossVectors(l[0],c[0]);for(let S=1;S<=t;S++){if(c[S]=c[S-1].clone(),h[S]=h[S-1].clone(),d.crossVectors(l[S-1],l[S]),d.length()>Number.EPSILON){d.normalize();const E=Math.acos(_e(l[S-1].dot(l[S]),-1,1));c[S].applyMatrix4(m.makeRotationAxis(d,E))}h[S].crossVectors(l[S],c[S])}if(i===!0){let S=Math.acos(_e(c[0].dot(c[t]),-1,1));S/=t,l[0].dot(d.crossVectors(c[0],c[t]))>0&&(S=-S);for(let E=1;E<=t;E++)c[E].applyMatrix4(m.makeRotationAxis(l[E],S*E)),h[E].crossVectors(l[E],c[E])}return{tangents:l,normals:c,binormals:h}}clone(){return new this.constructor().copy(this)}copy(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}toJSON(){const t={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return t.arcLengthDivisions=this.arcLengthDivisions,t.type=this.type,t}fromJSON(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}}class bb extends Eb{constructor(t=0,i=0,s=1,l=1,c=0,h=Math.PI*2,d=!1,m=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=t,this.aY=i,this.xRadius=s,this.yRadius=l,this.aStartAngle=c,this.aEndAngle=h,this.aClockwise=d,this.aRotation=m}getPoint(t,i=new Ae){const s=i,l=Math.PI*2;let c=this.aEndAngle-this.aStartAngle;const h=Math.abs(c)<Number.EPSILON;for(;c<0;)c+=l;for(;c>l;)c-=l;c<Number.EPSILON&&(h?c=0:c=l),this.aClockwise===!0&&!h&&(c===l?c=-l:c=c-l);const d=this.aStartAngle+t*c;let m=this.aX+this.xRadius*Math.cos(d),p=this.aY+this.yRadius*Math.sin(d);if(this.aRotation!==0){const g=Math.cos(this.aRotation),_=Math.sin(this.aRotation),x=m-this.aX,S=p-this.aY;m=x*g-S*_+this.aX,p=x*_+S*g+this.aY}return s.set(m,p)}copy(t){return super.copy(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}toJSON(){const t=super.toJSON();return t.aX=this.aX,t.aY=this.aY,t.xRadius=this.xRadius,t.yRadius=this.yRadius,t.aStartAngle=this.aStartAngle,t.aEndAngle=this.aEndAngle,t.aClockwise=this.aClockwise,t.aRotation=this.aRotation,t}fromJSON(t){return super.fromJSON(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}}class um extends mi{constructor(t=[],i=[],s=1,l=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:t,indices:i,radius:s,detail:l};const c=[],h=[];d(l),p(s),g(),this.setAttribute("position",new Ln(c,3)),this.setAttribute("normal",new Ln(c.slice(),3)),this.setAttribute("uv",new Ln(h,2)),l===0?this.computeVertexNormals():this.normalizeNormals();function d(L){const U=new Y,T=new Y,V=new Y;for(let I=0;I<i.length;I+=3)S(i[I+0],U),S(i[I+1],T),S(i[I+2],V),m(U,T,V,L)}function m(L,U,T,V){const I=V+1,P=[];for(let H=0;H<=I;H++){P[H]=[];const D=L.clone().lerp(T,H/I),C=U.clone().lerp(T,H/I),G=I-H;for(let ot=0;ot<=G;ot++)ot===0&&H===I?P[H][ot]=D:P[H][ot]=D.clone().lerp(C,ot/G)}for(let H=0;H<I;H++)for(let D=0;D<2*(I-H)-1;D++){const C=Math.floor(D/2);D%2===0?(x(P[H][C+1]),x(P[H+1][C]),x(P[H][C])):(x(P[H][C+1]),x(P[H+1][C+1]),x(P[H+1][C]))}}function p(L){const U=new Y;for(let T=0;T<c.length;T+=3)U.x=c[T+0],U.y=c[T+1],U.z=c[T+2],U.normalize().multiplyScalar(L),c[T+0]=U.x,c[T+1]=U.y,c[T+2]=U.z}function g(){const L=new Y;for(let U=0;U<c.length;U+=3){L.x=c[U+0],L.y=c[U+1],L.z=c[U+2];const T=M(L)/2/Math.PI+.5,V=v(L)/Math.PI+.5;h.push(T,1-V)}E(),_()}function _(){for(let L=0;L<h.length;L+=6){const U=h[L+0],T=h[L+2],V=h[L+4],I=Math.max(U,T,V),P=Math.min(U,T,V);I>.9&&P<.1&&(U<.2&&(h[L+0]+=1),T<.2&&(h[L+2]+=1),V<.2&&(h[L+4]+=1))}}function x(L){c.push(L.x,L.y,L.z)}function S(L,U){const T=L*3;U.x=t[T+0],U.y=t[T+1],U.z=t[T+2]}function E(){const L=new Y,U=new Y,T=new Y,V=new Y,I=new Ae,P=new Ae,H=new Ae;for(let D=0,C=0;D<c.length;D+=9,C+=6){L.set(c[D+0],c[D+1],c[D+2]),U.set(c[D+3],c[D+4],c[D+5]),T.set(c[D+6],c[D+7],c[D+8]),I.set(h[C+0],h[C+1]),P.set(h[C+2],h[C+3]),H.set(h[C+4],h[C+5]),V.copy(L).add(U).add(T).divideScalar(3);const G=M(V);b(I,C+0,L,G),b(P,C+2,U,G),b(H,C+4,T,G)}}function b(L,U,T,V){V<0&&L.x===1&&(h[U]=L.x-1),T.x===0&&T.z===0&&(h[U]=V/2/Math.PI+.5)}function M(L){return Math.atan2(L.z,-L.x)}function v(L){return Math.atan2(-L.y,Math.sqrt(L.x*L.x+L.z*L.z))}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new um(t.vertices,t.indices,t.radius,t.details)}}class fm extends um{constructor(t=1,i=0){const s=(1+Math.sqrt(5))/2,l=[-1,s,0,1,s,0,-1,-s,0,1,-s,0,0,-1,s,0,1,s,0,-1,-s,0,1,-s,s,0,-1,s,0,1,-s,0,-1,-s,0,1],c=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(l,c,t,i),this.type="IcosahedronGeometry",this.parameters={radius:t,detail:i}}static fromJSON(t){return new fm(t.radius,t.detail)}}class $u extends mi{constructor(t=1,i=1,s=1,l=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:i,widthSegments:s,heightSegments:l};const c=t/2,h=i/2,d=Math.floor(s),m=Math.floor(l),p=d+1,g=m+1,_=t/d,x=i/m,S=[],E=[],b=[],M=[];for(let v=0;v<g;v++){const L=v*x-h;for(let U=0;U<p;U++){const T=U*_-c;E.push(T,-L,0),b.push(0,0,1),M.push(U/d),M.push(1-v/m)}}for(let v=0;v<m;v++)for(let L=0;L<d;L++){const U=L+p*v,T=L+p*(v+1),V=L+1+p*(v+1),I=L+1+p*v;S.push(U,T,I),S.push(T,V,I)}this.setIndex(S),this.setAttribute("position",new Ln(E,3)),this.setAttribute("normal",new Ln(b,3)),this.setAttribute("uv",new Ln(M,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new $u(t.width,t.height,t.widthSegments,t.heightSegments)}}class hm extends mi{constructor(t=1,i=32,s=16,l=0,c=Math.PI*2,h=0,d=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:t,widthSegments:i,heightSegments:s,phiStart:l,phiLength:c,thetaStart:h,thetaLength:d},i=Math.max(3,Math.floor(i)),s=Math.max(2,Math.floor(s));const m=Math.min(h+d,Math.PI);let p=0;const g=[],_=new Y,x=new Y,S=[],E=[],b=[],M=[];for(let v=0;v<=s;v++){const L=[],U=v/s;let T=0;v===0&&h===0?T=.5/i:v===s&&m===Math.PI&&(T=-.5/i);for(let V=0;V<=i;V++){const I=V/i;_.x=-t*Math.cos(l+I*c)*Math.sin(h+U*d),_.y=t*Math.cos(h+U*d),_.z=t*Math.sin(l+I*c)*Math.sin(h+U*d),E.push(_.x,_.y,_.z),x.copy(_).normalize(),b.push(x.x,x.y,x.z),M.push(I+T,1-U),L.push(p++)}g.push(L)}for(let v=0;v<s;v++)for(let L=0;L<i;L++){const U=g[v][L+1],T=g[v][L],V=g[v+1][L],I=g[v+1][L+1];(v!==0||h>0)&&S.push(U,T,I),(v!==s-1||m<Math.PI)&&S.push(T,V,I)}this.setIndex(S),this.setAttribute("position",new Ln(E,3)),this.setAttribute("normal",new Ln(b,3)),this.setAttribute("uv",new Ln(M,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new hm(t.radius,t.widthSegments,t.heightSegments,t.phiStart,t.phiLength,t.thetaStart,t.thetaLength)}}class dm extends mi{constructor(t=1,i=.4,s=12,l=48,c=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:t,tube:i,radialSegments:s,tubularSegments:l,arc:c},s=Math.floor(s),l=Math.floor(l);const h=[],d=[],m=[],p=[],g=new Y,_=new Y,x=new Y;for(let S=0;S<=s;S++)for(let E=0;E<=l;E++){const b=E/l*c,M=S/s*Math.PI*2;_.x=(t+i*Math.cos(M))*Math.cos(b),_.y=(t+i*Math.cos(M))*Math.sin(b),_.z=i*Math.sin(M),d.push(_.x,_.y,_.z),g.x=t*Math.cos(b),g.y=t*Math.sin(b),x.subVectors(_,g).normalize(),m.push(x.x,x.y,x.z),p.push(E/l),p.push(S/s)}for(let S=1;S<=s;S++)for(let E=1;E<=l;E++){const b=(l+1)*S+E-1,M=(l+1)*(S-1)+E-1,v=(l+1)*(S-1)+E,L=(l+1)*S+E;h.push(b,M,L),h.push(M,v,L)}this.setIndex(h),this.setAttribute("position",new Ln(d,3)),this.setAttribute("normal",new Ln(m,3)),this.setAttribute("uv",new Ln(p,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new dm(t.radius,t.tube,t.radialSegments,t.tubularSegments,t.arc)}}class Tb extends tc{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=z1,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class Ab extends tc{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}class Rb extends jn{constructor(t,i=1){super(),this.isLight=!0,this.type="Light",this.color=new Oe(t),this.intensity=i}dispose(){}copy(t,i){return super.copy(t,i),this.color.copy(t.color),this.intensity=t.intensity,this}toJSON(t){const i=super.toJSON(t);return i.object.color=this.color.getHex(),i.object.intensity=this.intensity,this.groundColor!==void 0&&(i.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(i.object.distance=this.distance),this.angle!==void 0&&(i.object.angle=this.angle),this.decay!==void 0&&(i.object.decay=this.decay),this.penumbra!==void 0&&(i.object.penumbra=this.penumbra),this.shadow!==void 0&&(i.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(i.object.target=this.target.uuid),i}}const Fd=new Je,Xv=new Y,jv=new Y;class Cb{constructor(t){this.camera=t,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Ae(512,512),this.map=null,this.mapPass=null,this.matrix=new Je,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new cm,this._frameExtents=new Ae(1,1),this._viewportCount=1,this._viewports=[new qe(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(t){const i=this.camera,s=this.matrix;Xv.setFromMatrixPosition(t.matrixWorld),i.position.copy(Xv),jv.setFromMatrixPosition(t.target.matrixWorld),i.lookAt(jv),i.updateMatrixWorld(),Fd.multiplyMatrices(i.projectionMatrix,i.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Fd),s.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),s.multiply(Fd)}getViewport(t){return this._viewports[t]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(t){return this.camera=t.camera.clone(),this.intensity=t.intensity,this.bias=t.bias,this.radius=t.radius,this.mapSize.copy(t.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const t={};return this.intensity!==1&&(t.intensity=this.intensity),this.bias!==0&&(t.bias=this.bias),this.normalBias!==0&&(t.normalBias=this.normalBias),this.radius!==1&&(t.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(t.mapSize=this.mapSize.toArray()),t.camera=this.camera.toJSON(!1).object,delete t.camera.matrix,t}}const qv=new Je,zl=new Y,Hd=new Y;class wb extends Cb{constructor(){super(new pi(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Ae(4,2),this._viewportCount=6,this._viewports=[new qe(2,1,1,1),new qe(0,1,1,1),new qe(3,1,1,1),new qe(1,1,1,1),new qe(3,0,1,1),new qe(1,0,1,1)],this._cubeDirections=[new Y(1,0,0),new Y(-1,0,0),new Y(0,0,1),new Y(0,0,-1),new Y(0,1,0),new Y(0,-1,0)],this._cubeUps=[new Y(0,1,0),new Y(0,1,0),new Y(0,1,0),new Y(0,1,0),new Y(0,0,1),new Y(0,0,-1)]}updateMatrices(t,i=0){const s=this.camera,l=this.matrix,c=t.distance||s.far;c!==s.far&&(s.far=c,s.updateProjectionMatrix()),zl.setFromMatrixPosition(t.matrixWorld),s.position.copy(zl),Hd.copy(s.position),Hd.add(this._cubeDirections[i]),s.up.copy(this._cubeUps[i]),s.lookAt(Hd),s.updateMatrixWorld(),l.makeTranslation(-zl.x,-zl.y,-zl.z),qv.multiplyMatrices(s.projectionMatrix,s.matrixWorldInverse),this._frustum.setFromProjectionMatrix(qv)}}class Db extends Rb{constructor(t,i,s=0,l=2){super(t,i),this.isPointLight=!0,this.type="PointLight",this.distance=s,this.decay=l,this.shadow=new wb}get power(){return this.intensity*4*Math.PI}set power(t){this.intensity=t/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(t,i){return super.copy(t,i),this.distance=t.distance,this.decay=t.decay,this.shadow=t.shadow.clone(),this}}class Ub extends xx{constructor(t=-1,i=1,s=1,l=-1,c=.1,h=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=i,this.top=s,this.bottom=l,this.near=c,this.far=h,this.updateProjectionMatrix()}copy(t,i){return super.copy(t,i),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,i,s,l,c,h){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=i,this.view.offsetX=s,this.view.offsetY=l,this.view.width=c,this.view.height=h,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),i=(this.top-this.bottom)/(2*this.zoom),s=(this.right+this.left)/2,l=(this.top+this.bottom)/2;let c=s-t,h=s+t,d=l+i,m=l-i;if(this.view!==null&&this.view.enabled){const p=(this.right-this.left)/this.view.fullWidth/this.zoom,g=(this.top-this.bottom)/this.view.fullHeight/this.zoom;c+=p*this.view.offsetX,h=c+p*this.view.width,d-=g*this.view.offsetY,m=d-g*this.view.height}this.projectionMatrix.makeOrthographic(c,h,d,m,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const i=super.toJSON(t);return i.object.zoom=this.zoom,i.object.left=this.left,i.object.right=this.right,i.object.top=this.top,i.object.bottom=this.bottom,i.object.near=this.near,i.object.far=this.far,this.view!==null&&(i.object.view=Object.assign({},this.view)),i}}class Nb extends pi{constructor(t=[]){super(),this.isArrayCamera=!0,this.cameras=t}}function Wv(r,t,i,s){const l=Lb(s);switch(i){case ix:return r*t;case sx:return r*t;case rx:return r*t*2;case ox:return r*t/l.components*l.byteLength;case rm:return r*t/l.components*l.byteLength;case lx:return r*t*2/l.components*l.byteLength;case om:return r*t*2/l.components*l.byteLength;case ax:return r*t*3/l.components*l.byteLength;case Bi:return r*t*4/l.components*l.byteLength;case lm:return r*t*4/l.components*l.byteLength;case Fu:case Hu:return Math.floor((r+3)/4)*Math.floor((t+3)/4)*8;case Gu:case Vu:return Math.floor((r+3)/4)*Math.floor((t+3)/4)*16;case Mp:case bp:return Math.max(r,16)*Math.max(t,8)/4;case Sp:case Ep:return Math.max(r,8)*Math.max(t,8)/2;case Tp:case Ap:return Math.floor((r+3)/4)*Math.floor((t+3)/4)*8;case Rp:return Math.floor((r+3)/4)*Math.floor((t+3)/4)*16;case Cp:return Math.floor((r+3)/4)*Math.floor((t+3)/4)*16;case wp:return Math.floor((r+4)/5)*Math.floor((t+3)/4)*16;case Dp:return Math.floor((r+4)/5)*Math.floor((t+4)/5)*16;case Up:return Math.floor((r+5)/6)*Math.floor((t+4)/5)*16;case Np:return Math.floor((r+5)/6)*Math.floor((t+5)/6)*16;case Lp:return Math.floor((r+7)/8)*Math.floor((t+4)/5)*16;case Op:return Math.floor((r+7)/8)*Math.floor((t+5)/6)*16;case Pp:return Math.floor((r+7)/8)*Math.floor((t+7)/8)*16;case zp:return Math.floor((r+9)/10)*Math.floor((t+4)/5)*16;case Ip:return Math.floor((r+9)/10)*Math.floor((t+5)/6)*16;case Bp:return Math.floor((r+9)/10)*Math.floor((t+7)/8)*16;case Fp:return Math.floor((r+9)/10)*Math.floor((t+9)/10)*16;case Hp:return Math.floor((r+11)/12)*Math.floor((t+9)/10)*16;case Gp:return Math.floor((r+11)/12)*Math.floor((t+11)/12)*16;case ku:case Vp:case kp:return Math.ceil(r/4)*Math.ceil(t/4)*16;case cx:case Xp:return Math.ceil(r/4)*Math.ceil(t/4)*8;case jp:case qp:return Math.ceil(r/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${i} format.`)}function Lb(r){switch(r){case Da:case tx:return{byteLength:1,components:1};case kl:case ex:case Zl:return{byteLength:2,components:1};case am:case sm:return{byteLength:2,components:4};case hr:case im:case Ra:return{byteLength:4,components:1};case nx:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:nm}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=nm);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function Ex(){let r=null,t=!1,i=null,s=null;function l(c,h){i(c,h),s=r.requestAnimationFrame(l)}return{start:function(){t!==!0&&i!==null&&(s=r.requestAnimationFrame(l),t=!0)},stop:function(){r.cancelAnimationFrame(s),t=!1},setAnimationLoop:function(c){i=c},setContext:function(c){r=c}}}function Ob(r){const t=new WeakMap;function i(d,m){const p=d.array,g=d.usage,_=p.byteLength,x=r.createBuffer();r.bindBuffer(m,x),r.bufferData(m,p,g),d.onUploadCallback();let S;if(p instanceof Float32Array)S=r.FLOAT;else if(p instanceof Uint16Array)d.isFloat16BufferAttribute?S=r.HALF_FLOAT:S=r.UNSIGNED_SHORT;else if(p instanceof Int16Array)S=r.SHORT;else if(p instanceof Uint32Array)S=r.UNSIGNED_INT;else if(p instanceof Int32Array)S=r.INT;else if(p instanceof Int8Array)S=r.BYTE;else if(p instanceof Uint8Array)S=r.UNSIGNED_BYTE;else if(p instanceof Uint8ClampedArray)S=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+p);return{buffer:x,type:S,bytesPerElement:p.BYTES_PER_ELEMENT,version:d.version,size:_}}function s(d,m,p){const g=m.array,_=m.updateRanges;if(r.bindBuffer(p,d),_.length===0)r.bufferSubData(p,0,g);else{_.sort((S,E)=>S.start-E.start);let x=0;for(let S=1;S<_.length;S++){const E=_[x],b=_[S];b.start<=E.start+E.count+1?E.count=Math.max(E.count,b.start+b.count-E.start):(++x,_[x]=b)}_.length=x+1;for(let S=0,E=_.length;S<E;S++){const b=_[S];r.bufferSubData(p,b.start*g.BYTES_PER_ELEMENT,g,b.start,b.count)}m.clearUpdateRanges()}m.onUploadCallback()}function l(d){return d.isInterleavedBufferAttribute&&(d=d.data),t.get(d)}function c(d){d.isInterleavedBufferAttribute&&(d=d.data);const m=t.get(d);m&&(r.deleteBuffer(m.buffer),t.delete(d))}function h(d,m){if(d.isInterleavedBufferAttribute&&(d=d.data),d.isGLBufferAttribute){const g=t.get(d);(!g||g.version<d.version)&&t.set(d,{buffer:d.buffer,type:d.type,bytesPerElement:d.elementSize,version:d.version});return}const p=t.get(d);if(p===void 0)t.set(d,i(d,m));else if(p.version<d.version){if(p.size!==d.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");s(p.buffer,d,m),p.version=d.version}}return{get:l,remove:c,update:h}}var Pb=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,zb=`#ifdef USE_ALPHAHASH
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
#endif`,Ib=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,Bb=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Fb=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,Hb=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,Gb=`#ifdef USE_AOMAP
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
#endif`,Vb=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,kb=`#ifdef USE_BATCHING
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
#endif`,Xb=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,jb=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,qb=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Wb=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,Yb=`#ifdef USE_IRIDESCENCE
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
#endif`,Qb=`#ifdef USE_BUMPMAP
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
#endif`,Zb=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,Kb=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Jb=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,$b=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,tT=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,eT=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,nT=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,iT=`#if defined( USE_COLOR_ALPHA )
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
#endif`,aT=`#define PI 3.141592653589793
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
} // validated`,sT=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,rT=`vec3 transformedNormal = objectNormal;
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
#endif`,oT=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,lT=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,cT=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,uT=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,fT="gl_FragColor = linearToOutputTexel( gl_FragColor );",hT=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,dT=`#ifdef USE_ENVMAP
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
#endif`,pT=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,mT=`#ifdef USE_ENVMAP
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
#endif`,gT=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,_T=`#ifdef USE_ENVMAP
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
#endif`,vT=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,yT=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,xT=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,ST=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,MT=`#ifdef USE_GRADIENTMAP
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
}`,ET=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,bT=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,TT=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,AT=`uniform bool receiveShadow;
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
#endif`,RT=`#ifdef USE_ENVMAP
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
#endif`,CT=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,wT=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,DT=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,UT=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,NT=`PhysicalMaterial material;
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
#endif`,LT=`struct PhysicalMaterial {
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
}`,OT=`
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
#endif`,PT=`#if defined( RE_IndirectDiffuse )
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
#endif`,zT=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,IT=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,BT=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,FT=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,HT=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,GT=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,VT=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,kT=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,XT=`#if defined( USE_POINTS_UV )
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
#endif`,jT=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,qT=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,WT=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,YT=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,QT=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,ZT=`#ifdef USE_MORPHTARGETS
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
#endif`,KT=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,JT=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,$T=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,tA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,eA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,nA=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,iA=`#ifdef USE_NORMALMAP
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
#endif`,aA=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,sA=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,rA=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,oA=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,lA=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,cA=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,uA=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,fA=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,hA=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,dA=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,pA=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,mA=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,gA=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,_A=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,vA=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,yA=`float getShadowMask() {
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
}`,xA=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,SA=`#ifdef USE_SKINNING
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
#endif`,MA=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,EA=`#ifdef USE_SKINNING
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
#endif`,bA=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,TA=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,AA=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,RA=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,CA=`#ifdef USE_TRANSMISSION
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
#endif`,wA=`#ifdef USE_TRANSMISSION
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
#endif`,DA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,UA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,NA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,LA=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const OA=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,PA=`uniform sampler2D t2D;
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
}`,zA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,IA=`#ifdef ENVMAP_TYPE_CUBE
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
}`,BA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,FA=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,HA=`#include <common>
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
}`,GA=`#if DEPTH_PACKING == 3200
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
}`,VA=`#define DISTANCE
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
}`,kA=`#define DISTANCE
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
}`,XA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,jA=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,qA=`uniform float scale;
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
}`,WA=`uniform vec3 diffuse;
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
}`,YA=`#include <common>
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
}`,QA=`uniform vec3 diffuse;
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
}`,ZA=`#define LAMBERT
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
}`,KA=`#define LAMBERT
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
}`,JA=`#define MATCAP
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
}`,$A=`#define MATCAP
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
}`,t2=`#define NORMAL
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
}`,e2=`#define NORMAL
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
}`,n2=`#define PHONG
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
}`,i2=`#define PHONG
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
}`,a2=`#define STANDARD
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
}`,s2=`#define STANDARD
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
}`,r2=`#define TOON
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
}`,o2=`#define TOON
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
}`,l2=`uniform float size;
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
}`,c2=`uniform vec3 diffuse;
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
}`,u2=`#include <common>
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
}`,f2=`uniform vec3 color;
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
}`,h2=`uniform float rotation;
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
}`,d2=`uniform vec3 diffuse;
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
}`,fe={alphahash_fragment:Pb,alphahash_pars_fragment:zb,alphamap_fragment:Ib,alphamap_pars_fragment:Bb,alphatest_fragment:Fb,alphatest_pars_fragment:Hb,aomap_fragment:Gb,aomap_pars_fragment:Vb,batching_pars_vertex:kb,batching_vertex:Xb,begin_vertex:jb,beginnormal_vertex:qb,bsdfs:Wb,iridescence_fragment:Yb,bumpmap_pars_fragment:Qb,clipping_planes_fragment:Zb,clipping_planes_pars_fragment:Kb,clipping_planes_pars_vertex:Jb,clipping_planes_vertex:$b,color_fragment:tT,color_pars_fragment:eT,color_pars_vertex:nT,color_vertex:iT,common:aT,cube_uv_reflection_fragment:sT,defaultnormal_vertex:rT,displacementmap_pars_vertex:oT,displacementmap_vertex:lT,emissivemap_fragment:cT,emissivemap_pars_fragment:uT,colorspace_fragment:fT,colorspace_pars_fragment:hT,envmap_fragment:dT,envmap_common_pars_fragment:pT,envmap_pars_fragment:mT,envmap_pars_vertex:gT,envmap_physical_pars_fragment:RT,envmap_vertex:_T,fog_vertex:vT,fog_pars_vertex:yT,fog_fragment:xT,fog_pars_fragment:ST,gradientmap_pars_fragment:MT,lightmap_pars_fragment:ET,lights_lambert_fragment:bT,lights_lambert_pars_fragment:TT,lights_pars_begin:AT,lights_toon_fragment:CT,lights_toon_pars_fragment:wT,lights_phong_fragment:DT,lights_phong_pars_fragment:UT,lights_physical_fragment:NT,lights_physical_pars_fragment:LT,lights_fragment_begin:OT,lights_fragment_maps:PT,lights_fragment_end:zT,logdepthbuf_fragment:IT,logdepthbuf_pars_fragment:BT,logdepthbuf_pars_vertex:FT,logdepthbuf_vertex:HT,map_fragment:GT,map_pars_fragment:VT,map_particle_fragment:kT,map_particle_pars_fragment:XT,metalnessmap_fragment:jT,metalnessmap_pars_fragment:qT,morphinstance_vertex:WT,morphcolor_vertex:YT,morphnormal_vertex:QT,morphtarget_pars_vertex:ZT,morphtarget_vertex:KT,normal_fragment_begin:JT,normal_fragment_maps:$T,normal_pars_fragment:tA,normal_pars_vertex:eA,normal_vertex:nA,normalmap_pars_fragment:iA,clearcoat_normal_fragment_begin:aA,clearcoat_normal_fragment_maps:sA,clearcoat_pars_fragment:rA,iridescence_pars_fragment:oA,opaque_fragment:lA,packing:cA,premultiplied_alpha_fragment:uA,project_vertex:fA,dithering_fragment:hA,dithering_pars_fragment:dA,roughnessmap_fragment:pA,roughnessmap_pars_fragment:mA,shadowmap_pars_fragment:gA,shadowmap_pars_vertex:_A,shadowmap_vertex:vA,shadowmask_pars_fragment:yA,skinbase_vertex:xA,skinning_pars_vertex:SA,skinning_vertex:MA,skinnormal_vertex:EA,specularmap_fragment:bA,specularmap_pars_fragment:TA,tonemapping_fragment:AA,tonemapping_pars_fragment:RA,transmission_fragment:CA,transmission_pars_fragment:wA,uv_pars_fragment:DA,uv_pars_vertex:UA,uv_vertex:NA,worldpos_vertex:LA,background_vert:OA,background_frag:PA,backgroundCube_vert:zA,backgroundCube_frag:IA,cube_vert:BA,cube_frag:FA,depth_vert:HA,depth_frag:GA,distanceRGBA_vert:VA,distanceRGBA_frag:kA,equirect_vert:XA,equirect_frag:jA,linedashed_vert:qA,linedashed_frag:WA,meshbasic_vert:YA,meshbasic_frag:QA,meshlambert_vert:ZA,meshlambert_frag:KA,meshmatcap_vert:JA,meshmatcap_frag:$A,meshnormal_vert:t2,meshnormal_frag:e2,meshphong_vert:n2,meshphong_frag:i2,meshphysical_vert:a2,meshphysical_frag:s2,meshtoon_vert:r2,meshtoon_frag:o2,points_vert:l2,points_frag:c2,shadow_vert:u2,shadow_frag:f2,sprite_vert:h2,sprite_frag:d2},Lt={common:{diffuse:{value:new Oe(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ue},alphaMap:{value:null},alphaMapTransform:{value:new ue},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ue}},envmap:{envMap:{value:null},envMapRotation:{value:new ue},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ue}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ue}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ue},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ue},normalScale:{value:new Ae(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ue},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ue}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ue}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ue}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Oe(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Oe(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ue},alphaTest:{value:0},uvTransform:{value:new ue}},sprite:{diffuse:{value:new Oe(16777215)},opacity:{value:1},center:{value:new Ae(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ue},alphaMap:{value:null},alphaMapTransform:{value:new ue},alphaTest:{value:0}}},Qi={basic:{uniforms:kn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.fog]),vertexShader:fe.meshbasic_vert,fragmentShader:fe.meshbasic_frag},lambert:{uniforms:kn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new Oe(0)}}]),vertexShader:fe.meshlambert_vert,fragmentShader:fe.meshlambert_frag},phong:{uniforms:kn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new Oe(0)},specular:{value:new Oe(1118481)},shininess:{value:30}}]),vertexShader:fe.meshphong_vert,fragmentShader:fe.meshphong_frag},standard:{uniforms:kn([Lt.common,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.roughnessmap,Lt.metalnessmap,Lt.fog,Lt.lights,{emissive:{value:new Oe(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:fe.meshphysical_vert,fragmentShader:fe.meshphysical_frag},toon:{uniforms:kn([Lt.common,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.gradientmap,Lt.fog,Lt.lights,{emissive:{value:new Oe(0)}}]),vertexShader:fe.meshtoon_vert,fragmentShader:fe.meshtoon_frag},matcap:{uniforms:kn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,{matcap:{value:null}}]),vertexShader:fe.meshmatcap_vert,fragmentShader:fe.meshmatcap_frag},points:{uniforms:kn([Lt.points,Lt.fog]),vertexShader:fe.points_vert,fragmentShader:fe.points_frag},dashed:{uniforms:kn([Lt.common,Lt.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:fe.linedashed_vert,fragmentShader:fe.linedashed_frag},depth:{uniforms:kn([Lt.common,Lt.displacementmap]),vertexShader:fe.depth_vert,fragmentShader:fe.depth_frag},normal:{uniforms:kn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,{opacity:{value:1}}]),vertexShader:fe.meshnormal_vert,fragmentShader:fe.meshnormal_frag},sprite:{uniforms:kn([Lt.sprite,Lt.fog]),vertexShader:fe.sprite_vert,fragmentShader:fe.sprite_frag},background:{uniforms:{uvTransform:{value:new ue},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:fe.background_vert,fragmentShader:fe.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ue}},vertexShader:fe.backgroundCube_vert,fragmentShader:fe.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:fe.cube_vert,fragmentShader:fe.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:fe.equirect_vert,fragmentShader:fe.equirect_frag},distanceRGBA:{uniforms:kn([Lt.common,Lt.displacementmap,{referencePosition:{value:new Y},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:fe.distanceRGBA_vert,fragmentShader:fe.distanceRGBA_frag},shadow:{uniforms:kn([Lt.lights,Lt.fog,{color:{value:new Oe(0)},opacity:{value:1}}]),vertexShader:fe.shadow_vert,fragmentShader:fe.shadow_frag}};Qi.physical={uniforms:kn([Qi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ue},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ue},clearcoatNormalScale:{value:new Ae(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ue},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ue},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ue},sheen:{value:0},sheenColor:{value:new Oe(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ue},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ue},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ue},transmissionSamplerSize:{value:new Ae},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ue},attenuationDistance:{value:0},attenuationColor:{value:new Oe(0)},specularColor:{value:new Oe(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ue},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ue},anisotropyVector:{value:new Ae},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ue}}]),vertexShader:fe.meshphysical_vert,fragmentShader:fe.meshphysical_frag};const Ou={r:0,b:0,g:0},qs=new Ua,p2=new Je;function m2(r,t,i,s,l,c,h){const d=new Oe(0);let m=c===!0?0:1,p,g,_=null,x=0,S=null;function E(U){let T=U.isScene===!0?U.background:null;return T&&T.isTexture&&(T=(U.backgroundBlurriness>0?i:t).get(T)),T}function b(U){let T=!1;const V=E(U);V===null?v(d,m):V&&V.isColor&&(v(V,1),T=!0);const I=r.xr.getEnvironmentBlendMode();I==="additive"?s.buffers.color.setClear(0,0,0,1,h):I==="alpha-blend"&&s.buffers.color.setClear(0,0,0,0,h),(r.autoClear||T)&&(s.buffers.depth.setTest(!0),s.buffers.depth.setMask(!0),s.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function M(U,T){const V=E(T);V&&(V.isCubeTexture||V.mapping===Ku)?(g===void 0&&(g=new Ri(new ec(1,1,1),new Ss({name:"BackgroundCubeMaterial",uniforms:Oo(Qi.backgroundCube.uniforms),vertexShader:Qi.backgroundCube.vertexShader,fragmentShader:Qi.backgroundCube.fragmentShader,side:ei,depthTest:!1,depthWrite:!1,fog:!1})),g.geometry.deleteAttribute("normal"),g.geometry.deleteAttribute("uv"),g.onBeforeRender=function(I,P,H){this.matrixWorld.copyPosition(H.matrixWorld)},Object.defineProperty(g.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),l.update(g)),qs.copy(T.backgroundRotation),qs.x*=-1,qs.y*=-1,qs.z*=-1,V.isCubeTexture&&V.isRenderTargetTexture===!1&&(qs.y*=-1,qs.z*=-1),g.material.uniforms.envMap.value=V,g.material.uniforms.flipEnvMap.value=V.isCubeTexture&&V.isRenderTargetTexture===!1?-1:1,g.material.uniforms.backgroundBlurriness.value=T.backgroundBlurriness,g.material.uniforms.backgroundIntensity.value=T.backgroundIntensity,g.material.uniforms.backgroundRotation.value.setFromMatrix4(p2.makeRotationFromEuler(qs)),g.material.toneMapped=Ne.getTransfer(V.colorSpace)!==je,(_!==V||x!==V.version||S!==r.toneMapping)&&(g.material.needsUpdate=!0,_=V,x=V.version,S=r.toneMapping),g.layers.enableAll(),U.unshift(g,g.geometry,g.material,0,0,null)):V&&V.isTexture&&(p===void 0&&(p=new Ri(new $u(2,2),new Ss({name:"BackgroundMaterial",uniforms:Oo(Qi.background.uniforms),vertexShader:Qi.background.vertexShader,fragmentShader:Qi.background.fragmentShader,side:xs,depthTest:!1,depthWrite:!1,fog:!1})),p.geometry.deleteAttribute("normal"),Object.defineProperty(p.material,"map",{get:function(){return this.uniforms.t2D.value}}),l.update(p)),p.material.uniforms.t2D.value=V,p.material.uniforms.backgroundIntensity.value=T.backgroundIntensity,p.material.toneMapped=Ne.getTransfer(V.colorSpace)!==je,V.matrixAutoUpdate===!0&&V.updateMatrix(),p.material.uniforms.uvTransform.value.copy(V.matrix),(_!==V||x!==V.version||S!==r.toneMapping)&&(p.material.needsUpdate=!0,_=V,x=V.version,S=r.toneMapping),p.layers.enableAll(),U.unshift(p,p.geometry,p.material,0,0,null))}function v(U,T){U.getRGB(Ou,yx(r)),s.buffers.color.setClear(Ou.r,Ou.g,Ou.b,T,h)}function L(){g!==void 0&&(g.geometry.dispose(),g.material.dispose()),p!==void 0&&(p.geometry.dispose(),p.material.dispose())}return{getClearColor:function(){return d},setClearColor:function(U,T=1){d.set(U),m=T,v(d,m)},getClearAlpha:function(){return m},setClearAlpha:function(U){m=U,v(d,m)},render:b,addToRenderList:M,dispose:L}}function g2(r,t){const i=r.getParameter(r.MAX_VERTEX_ATTRIBS),s={},l=x(null);let c=l,h=!1;function d(C,G,ot,lt,mt){let gt=!1;const B=_(lt,ot,G);c!==B&&(c=B,p(c.object)),gt=S(C,lt,ot,mt),gt&&E(C,lt,ot,mt),mt!==null&&t.update(mt,r.ELEMENT_ARRAY_BUFFER),(gt||h)&&(h=!1,T(C,G,ot,lt),mt!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,t.get(mt).buffer))}function m(){return r.createVertexArray()}function p(C){return r.bindVertexArray(C)}function g(C){return r.deleteVertexArray(C)}function _(C,G,ot){const lt=ot.wireframe===!0;let mt=s[C.id];mt===void 0&&(mt={},s[C.id]=mt);let gt=mt[G.id];gt===void 0&&(gt={},mt[G.id]=gt);let B=gt[lt];return B===void 0&&(B=x(m()),gt[lt]=B),B}function x(C){const G=[],ot=[],lt=[];for(let mt=0;mt<i;mt++)G[mt]=0,ot[mt]=0,lt[mt]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:G,enabledAttributes:ot,attributeDivisors:lt,object:C,attributes:{},index:null}}function S(C,G,ot,lt){const mt=c.attributes,gt=G.attributes;let B=0;const $=ot.getAttributes();for(const J in $)if($[J].location>=0){const At=mt[J];let z=gt[J];if(z===void 0&&(J==="instanceMatrix"&&C.instanceMatrix&&(z=C.instanceMatrix),J==="instanceColor"&&C.instanceColor&&(z=C.instanceColor)),At===void 0||At.attribute!==z||z&&At.data!==z.data)return!0;B++}return c.attributesNum!==B||c.index!==lt}function E(C,G,ot,lt){const mt={},gt=G.attributes;let B=0;const $=ot.getAttributes();for(const J in $)if($[J].location>=0){let At=gt[J];At===void 0&&(J==="instanceMatrix"&&C.instanceMatrix&&(At=C.instanceMatrix),J==="instanceColor"&&C.instanceColor&&(At=C.instanceColor));const z={};z.attribute=At,At&&At.data&&(z.data=At.data),mt[J]=z,B++}c.attributes=mt,c.attributesNum=B,c.index=lt}function b(){const C=c.newAttributes;for(let G=0,ot=C.length;G<ot;G++)C[G]=0}function M(C){v(C,0)}function v(C,G){const ot=c.newAttributes,lt=c.enabledAttributes,mt=c.attributeDivisors;ot[C]=1,lt[C]===0&&(r.enableVertexAttribArray(C),lt[C]=1),mt[C]!==G&&(r.vertexAttribDivisor(C,G),mt[C]=G)}function L(){const C=c.newAttributes,G=c.enabledAttributes;for(let ot=0,lt=G.length;ot<lt;ot++)G[ot]!==C[ot]&&(r.disableVertexAttribArray(ot),G[ot]=0)}function U(C,G,ot,lt,mt,gt,B){B===!0?r.vertexAttribIPointer(C,G,ot,mt,gt):r.vertexAttribPointer(C,G,ot,lt,mt,gt)}function T(C,G,ot,lt){b();const mt=lt.attributes,gt=ot.getAttributes(),B=G.defaultAttributeValues;for(const $ in gt){const J=gt[$];if(J.location>=0){let Et=mt[$];if(Et===void 0&&($==="instanceMatrix"&&C.instanceMatrix&&(Et=C.instanceMatrix),$==="instanceColor"&&C.instanceColor&&(Et=C.instanceColor)),Et!==void 0){const At=Et.normalized,z=Et.itemSize,at=t.get(Et);if(at===void 0)continue;const Mt=at.buffer,K=at.type,ft=at.bytesPerElement,Tt=K===r.INT||K===r.UNSIGNED_INT||Et.gpuType===im;if(Et.isInterleavedBufferAttribute){const St=Et.data,kt=St.stride,Gt=Et.offset;if(St.isInstancedInterleavedBuffer){for(let se=0;se<J.locationSize;se++)v(J.location+se,St.meshPerAttribute);C.isInstancedMesh!==!0&&lt._maxInstanceCount===void 0&&(lt._maxInstanceCount=St.meshPerAttribute*St.count)}else for(let se=0;se<J.locationSize;se++)M(J.location+se);r.bindBuffer(r.ARRAY_BUFFER,Mt);for(let se=0;se<J.locationSize;se++)U(J.location+se,z/J.locationSize,K,At,kt*ft,(Gt+z/J.locationSize*se)*ft,Tt)}else{if(Et.isInstancedBufferAttribute){for(let St=0;St<J.locationSize;St++)v(J.location+St,Et.meshPerAttribute);C.isInstancedMesh!==!0&&lt._maxInstanceCount===void 0&&(lt._maxInstanceCount=Et.meshPerAttribute*Et.count)}else for(let St=0;St<J.locationSize;St++)M(J.location+St);r.bindBuffer(r.ARRAY_BUFFER,Mt);for(let St=0;St<J.locationSize;St++)U(J.location+St,z/J.locationSize,K,At,z*ft,z/J.locationSize*St*ft,Tt)}}else if(B!==void 0){const At=B[$];if(At!==void 0)switch(At.length){case 2:r.vertexAttrib2fv(J.location,At);break;case 3:r.vertexAttrib3fv(J.location,At);break;case 4:r.vertexAttrib4fv(J.location,At);break;default:r.vertexAttrib1fv(J.location,At)}}}}L()}function V(){H();for(const C in s){const G=s[C];for(const ot in G){const lt=G[ot];for(const mt in lt)g(lt[mt].object),delete lt[mt];delete G[ot]}delete s[C]}}function I(C){if(s[C.id]===void 0)return;const G=s[C.id];for(const ot in G){const lt=G[ot];for(const mt in lt)g(lt[mt].object),delete lt[mt];delete G[ot]}delete s[C.id]}function P(C){for(const G in s){const ot=s[G];if(ot[C.id]===void 0)continue;const lt=ot[C.id];for(const mt in lt)g(lt[mt].object),delete lt[mt];delete ot[C.id]}}function H(){D(),h=!0,c!==l&&(c=l,p(c.object))}function D(){l.geometry=null,l.program=null,l.wireframe=!1}return{setup:d,reset:H,resetDefaultState:D,dispose:V,releaseStatesOfGeometry:I,releaseStatesOfProgram:P,initAttributes:b,enableAttribute:M,disableUnusedAttributes:L}}function _2(r,t,i){let s;function l(p){s=p}function c(p,g){r.drawArrays(s,p,g),i.update(g,s,1)}function h(p,g,_){_!==0&&(r.drawArraysInstanced(s,p,g,_),i.update(g,s,_))}function d(p,g,_){if(_===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(s,p,0,g,0,_);let S=0;for(let E=0;E<_;E++)S+=g[E];i.update(S,s,1)}function m(p,g,_,x){if(_===0)return;const S=t.get("WEBGL_multi_draw");if(S===null)for(let E=0;E<p.length;E++)h(p[E],g[E],x[E]);else{S.multiDrawArraysInstancedWEBGL(s,p,0,g,0,x,0,_);let E=0;for(let b=0;b<_;b++)E+=g[b]*x[b];i.update(E,s,1)}}this.setMode=l,this.render=c,this.renderInstances=h,this.renderMultiDraw=d,this.renderMultiDrawInstances=m}function v2(r,t,i,s){let l;function c(){if(l!==void 0)return l;if(t.has("EXT_texture_filter_anisotropic")===!0){const P=t.get("EXT_texture_filter_anisotropic");l=r.getParameter(P.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else l=0;return l}function h(P){return!(P!==Bi&&s.convert(P)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function d(P){const H=P===Zl&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(P!==Da&&s.convert(P)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&P!==Ra&&!H)}function m(P){if(P==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";P="mediump"}return P==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let p=i.precision!==void 0?i.precision:"highp";const g=m(p);g!==p&&(console.warn("THREE.WebGLRenderer:",p,"not supported, using",g,"instead."),p=g);const _=i.logarithmicDepthBuffer===!0,x=i.reverseDepthBuffer===!0&&t.has("EXT_clip_control"),S=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),E=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),b=r.getParameter(r.MAX_TEXTURE_SIZE),M=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),v=r.getParameter(r.MAX_VERTEX_ATTRIBS),L=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),U=r.getParameter(r.MAX_VARYING_VECTORS),T=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),V=E>0,I=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:c,getMaxPrecision:m,textureFormatReadable:h,textureTypeReadable:d,precision:p,logarithmicDepthBuffer:_,reverseDepthBuffer:x,maxTextures:S,maxVertexTextures:E,maxTextureSize:b,maxCubemapSize:M,maxAttributes:v,maxVertexUniforms:L,maxVaryings:U,maxFragmentUniforms:T,vertexTextures:V,maxSamples:I}}function y2(r){const t=this;let i=null,s=0,l=!1,c=!1;const h=new Ys,d=new ue,m={value:null,needsUpdate:!1};this.uniform=m,this.numPlanes=0,this.numIntersection=0,this.init=function(_,x){const S=_.length!==0||x||s!==0||l;return l=x,s=_.length,S},this.beginShadows=function(){c=!0,g(null)},this.endShadows=function(){c=!1},this.setGlobalState=function(_,x){i=g(_,x,0)},this.setState=function(_,x,S){const E=_.clippingPlanes,b=_.clipIntersection,M=_.clipShadows,v=r.get(_);if(!l||E===null||E.length===0||c&&!M)c?g(null):p();else{const L=c?0:s,U=L*4;let T=v.clippingState||null;m.value=T,T=g(E,x,U,S);for(let V=0;V!==U;++V)T[V]=i[V];v.clippingState=T,this.numIntersection=b?this.numPlanes:0,this.numPlanes+=L}};function p(){m.value!==i&&(m.value=i,m.needsUpdate=s>0),t.numPlanes=s,t.numIntersection=0}function g(_,x,S,E){const b=_!==null?_.length:0;let M=null;if(b!==0){if(M=m.value,E!==!0||M===null){const v=S+b*4,L=x.matrixWorldInverse;d.getNormalMatrix(L),(M===null||M.length<v)&&(M=new Float32Array(v));for(let U=0,T=S;U!==b;++U,T+=4)h.copy(_[U]).applyMatrix4(L,d),h.normal.toArray(M,T),M[T+3]=h.constant}m.value=M,m.needsUpdate=!0}return t.numPlanes=b,t.numIntersection=0,M}}function x2(r){let t=new WeakMap;function i(h,d){return d===_p?h.mapping=wo:d===vp&&(h.mapping=Do),h}function s(h){if(h&&h.isTexture){const d=h.mapping;if(d===_p||d===vp)if(t.has(h)){const m=t.get(h).texture;return i(m,h.mapping)}else{const m=h.image;if(m&&m.height>0){const p=new yb(m.height);return p.fromEquirectangularTexture(r,h),t.set(h,p),h.addEventListener("dispose",l),i(p.texture,h.mapping)}else return null}}return h}function l(h){const d=h.target;d.removeEventListener("dispose",l);const m=t.get(d);m!==void 0&&(t.delete(d),m.dispose())}function c(){t=new WeakMap}return{get:s,dispose:c}}const uo=4,Yv=[.125,.215,.35,.446,.526,.582],Ks=20,Gd=new Ub,Qv=new Oe;let Vd=null,kd=0,Xd=0,jd=!1;const Qs=(1+Math.sqrt(5))/2,oo=1/Qs,Zv=[new Y(-Qs,oo,0),new Y(Qs,oo,0),new Y(-oo,0,Qs),new Y(oo,0,Qs),new Y(0,Qs,-oo),new Y(0,Qs,oo),new Y(-1,1,-1),new Y(1,1,-1),new Y(-1,1,1),new Y(1,1,1)];class Kv{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(t,i=0,s=.1,l=100){Vd=this._renderer.getRenderTarget(),kd=this._renderer.getActiveCubeFace(),Xd=this._renderer.getActiveMipmapLevel(),jd=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const c=this._allocateTargets();return c.depthBuffer=!0,this._sceneToCubeUV(t,s,l,c),i>0&&this._blur(c,0,0,i),this._applyPMREM(c),this._cleanup(c),c}fromEquirectangular(t,i=null){return this._fromTexture(t,i)}fromCubemap(t,i=null){return this._fromTexture(t,i)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=ty(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=$v(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodPlanes.length;t++)this._lodPlanes[t].dispose()}_cleanup(t){this._renderer.setRenderTarget(Vd,kd,Xd),this._renderer.xr.enabled=jd,t.scissorTest=!1,Pu(t,0,0,t.width,t.height)}_fromTexture(t,i){t.mapping===wo||t.mapping===Do?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),Vd=this._renderer.getRenderTarget(),kd=this._renderer.getActiveCubeFace(),Xd=this._renderer.getActiveMipmapLevel(),jd=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const s=i||this._allocateTargets();return this._textureToCubeUV(t,s),this._applyPMREM(s),this._cleanup(s),s}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),i=4*this._cubeSize,s={magFilter:Zi,minFilter:Zi,generateMipmaps:!1,type:Zl,format:Bi,colorSpace:Lo,depthBuffer:!1},l=Jv(t,i,s);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==i){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Jv(t,i,s);const{_lodMax:c}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=S2(c)),this._blurMaterial=M2(c,t,i)}return l}_compileMaterial(t){const i=new Ri(this._lodPlanes[0],t);this._renderer.compile(i,Gd)}_sceneToCubeUV(t,i,s,l){const d=new pi(90,1,i,s),m=[1,-1,1,1,1,1],p=[1,1,1,-1,-1,-1],g=this._renderer,_=g.autoClear,x=g.toneMapping;g.getClearColor(Qv),g.toneMapping=ys,g.autoClear=!1;const S=new Fl({name:"PMREM.Background",side:ei,depthWrite:!1,depthTest:!1}),E=new Ri(new ec,S);let b=!1;const M=t.background;M?M.isColor&&(S.color.copy(M),t.background=null,b=!0):(S.color.copy(Qv),b=!0);for(let v=0;v<6;v++){const L=v%3;L===0?(d.up.set(0,m[v],0),d.lookAt(p[v],0,0)):L===1?(d.up.set(0,0,m[v]),d.lookAt(0,p[v],0)):(d.up.set(0,m[v],0),d.lookAt(0,0,p[v]));const U=this._cubeSize;Pu(l,L*U,v>2?U:0,U,U),g.setRenderTarget(l),b&&g.render(E,d),g.render(t,d)}E.geometry.dispose(),E.material.dispose(),g.toneMapping=x,g.autoClear=_,t.background=M}_textureToCubeUV(t,i){const s=this._renderer,l=t.mapping===wo||t.mapping===Do;l?(this._cubemapMaterial===null&&(this._cubemapMaterial=ty()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=$v());const c=l?this._cubemapMaterial:this._equirectMaterial,h=new Ri(this._lodPlanes[0],c),d=c.uniforms;d.envMap.value=t;const m=this._cubeSize;Pu(i,0,0,3*m,2*m),s.setRenderTarget(i),s.render(h,Gd)}_applyPMREM(t){const i=this._renderer,s=i.autoClear;i.autoClear=!1;const l=this._lodPlanes.length;for(let c=1;c<l;c++){const h=Math.sqrt(this._sigmas[c]*this._sigmas[c]-this._sigmas[c-1]*this._sigmas[c-1]),d=Zv[(l-c-1)%Zv.length];this._blur(t,c-1,c,h,d)}i.autoClear=s}_blur(t,i,s,l,c){const h=this._pingPongRenderTarget;this._halfBlur(t,h,i,s,l,"latitudinal",c),this._halfBlur(h,t,s,s,l,"longitudinal",c)}_halfBlur(t,i,s,l,c,h,d){const m=this._renderer,p=this._blurMaterial;h!=="latitudinal"&&h!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const g=3,_=new Ri(this._lodPlanes[l],p),x=p.uniforms,S=this._sizeLods[s]-1,E=isFinite(c)?Math.PI/(2*S):2*Math.PI/(2*Ks-1),b=c/E,M=isFinite(c)?1+Math.floor(g*b):Ks;M>Ks&&console.warn(`sigmaRadians, ${c}, is too large and will clip, as it requested ${M} samples when the maximum is set to ${Ks}`);const v=[];let L=0;for(let P=0;P<Ks;++P){const H=P/b,D=Math.exp(-H*H/2);v.push(D),P===0?L+=D:P<M&&(L+=2*D)}for(let P=0;P<v.length;P++)v[P]=v[P]/L;x.envMap.value=t.texture,x.samples.value=M,x.weights.value=v,x.latitudinal.value=h==="latitudinal",d&&(x.poleAxis.value=d);const{_lodMax:U}=this;x.dTheta.value=E,x.mipInt.value=U-s;const T=this._sizeLods[l],V=3*T*(l>U-uo?l-U+uo:0),I=4*(this._cubeSize-T);Pu(i,V,I,3*T,2*T),m.setRenderTarget(i),m.render(_,Gd)}}function S2(r){const t=[],i=[],s=[];let l=r;const c=r-uo+1+Yv.length;for(let h=0;h<c;h++){const d=Math.pow(2,l);i.push(d);let m=1/d;h>r-uo?m=Yv[h-r+uo-1]:h===0&&(m=0),s.push(m);const p=1/(d-2),g=-p,_=1+p,x=[g,g,_,g,_,_,g,g,_,_,g,_],S=6,E=6,b=3,M=2,v=1,L=new Float32Array(b*E*S),U=new Float32Array(M*E*S),T=new Float32Array(v*E*S);for(let I=0;I<S;I++){const P=I%3*2/3-1,H=I>2?0:-1,D=[P,H,0,P+2/3,H,0,P+2/3,H+1,0,P,H,0,P+2/3,H+1,0,P,H+1,0];L.set(D,b*E*I),U.set(x,M*E*I);const C=[I,I,I,I,I,I];T.set(C,v*E*I)}const V=new mi;V.setAttribute("position",new Ki(L,b)),V.setAttribute("uv",new Ki(U,M)),V.setAttribute("faceIndex",new Ki(T,v)),t.push(V),l>uo&&l--}return{lodPlanes:t,sizeLods:i,sigmas:s}}function Jv(r,t,i){const s=new dr(r,t,i);return s.texture.mapping=Ku,s.texture.name="PMREM.cubeUv",s.scissorTest=!0,s}function Pu(r,t,i,s,l){r.viewport.set(t,i,s,l),r.scissor.set(t,i,s,l)}function M2(r,t,i){const s=new Float32Array(Ks),l=new Y(0,1,0);return new Ss({name:"SphericalGaussianBlur",defines:{n:Ks,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/i,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:s},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:l}},vertexShader:pm(),fragmentShader:`

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
		`,blending:vs,depthTest:!1,depthWrite:!1})}function $v(){return new Ss({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:pm(),fragmentShader:`

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
		`,blending:vs,depthTest:!1,depthWrite:!1})}function ty(){return new Ss({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:pm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:vs,depthTest:!1,depthWrite:!1})}function pm(){return`

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
	`}function E2(r){let t=new WeakMap,i=null;function s(d){if(d&&d.isTexture){const m=d.mapping,p=m===_p||m===vp,g=m===wo||m===Do;if(p||g){let _=t.get(d);const x=_!==void 0?_.texture.pmremVersion:0;if(d.isRenderTargetTexture&&d.pmremVersion!==x)return i===null&&(i=new Kv(r)),_=p?i.fromEquirectangular(d,_):i.fromCubemap(d,_),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),_.texture;if(_!==void 0)return _.texture;{const S=d.image;return p&&S&&S.height>0||g&&S&&l(S)?(i===null&&(i=new Kv(r)),_=p?i.fromEquirectangular(d):i.fromCubemap(d),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),d.addEventListener("dispose",c),_.texture):null}}}return d}function l(d){let m=0;const p=6;for(let g=0;g<p;g++)d[g]!==void 0&&m++;return m===p}function c(d){const m=d.target;m.removeEventListener("dispose",c);const p=t.get(m);p!==void 0&&(t.delete(m),p.dispose())}function h(){t=new WeakMap,i!==null&&(i.dispose(),i=null)}return{get:s,dispose:h}}function b2(r){const t={};function i(s){if(t[s]!==void 0)return t[s];let l;switch(s){case"WEBGL_depth_texture":l=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":l=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":l=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":l=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:l=r.getExtension(s)}return t[s]=l,l}return{has:function(s){return i(s)!==null},init:function(){i("EXT_color_buffer_float"),i("WEBGL_clip_cull_distance"),i("OES_texture_float_linear"),i("EXT_color_buffer_half_float"),i("WEBGL_multisampled_render_to_texture"),i("WEBGL_render_shared_exponent")},get:function(s){const l=i(s);return l===null&&lo("THREE.WebGLRenderer: "+s+" extension not supported."),l}}}function T2(r,t,i,s){const l={},c=new WeakMap;function h(_){const x=_.target;x.index!==null&&t.remove(x.index);for(const E in x.attributes)t.remove(x.attributes[E]);x.removeEventListener("dispose",h),delete l[x.id];const S=c.get(x);S&&(t.remove(S),c.delete(x)),s.releaseStatesOfGeometry(x),x.isInstancedBufferGeometry===!0&&delete x._maxInstanceCount,i.memory.geometries--}function d(_,x){return l[x.id]===!0||(x.addEventListener("dispose",h),l[x.id]=!0,i.memory.geometries++),x}function m(_){const x=_.attributes;for(const S in x)t.update(x[S],r.ARRAY_BUFFER)}function p(_){const x=[],S=_.index,E=_.attributes.position;let b=0;if(S!==null){const L=S.array;b=S.version;for(let U=0,T=L.length;U<T;U+=3){const V=L[U+0],I=L[U+1],P=L[U+2];x.push(V,I,I,P,P,V)}}else if(E!==void 0){const L=E.array;b=E.version;for(let U=0,T=L.length/3-1;U<T;U+=3){const V=U+0,I=U+1,P=U+2;x.push(V,I,I,P,P,V)}}else return;const M=new(fx(x)?vx:_x)(x,1);M.version=b;const v=c.get(_);v&&t.remove(v),c.set(_,M)}function g(_){const x=c.get(_);if(x){const S=_.index;S!==null&&x.version<S.version&&p(_)}else p(_);return c.get(_)}return{get:d,update:m,getWireframeAttribute:g}}function A2(r,t,i){let s;function l(x){s=x}let c,h;function d(x){c=x.type,h=x.bytesPerElement}function m(x,S){r.drawElements(s,S,c,x*h),i.update(S,s,1)}function p(x,S,E){E!==0&&(r.drawElementsInstanced(s,S,c,x*h,E),i.update(S,s,E))}function g(x,S,E){if(E===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(s,S,0,c,x,0,E);let M=0;for(let v=0;v<E;v++)M+=S[v];i.update(M,s,1)}function _(x,S,E,b){if(E===0)return;const M=t.get("WEBGL_multi_draw");if(M===null)for(let v=0;v<x.length;v++)p(x[v]/h,S[v],b[v]);else{M.multiDrawElementsInstancedWEBGL(s,S,0,c,x,0,b,0,E);let v=0;for(let L=0;L<E;L++)v+=S[L]*b[L];i.update(v,s,1)}}this.setMode=l,this.setIndex=d,this.render=m,this.renderInstances=p,this.renderMultiDraw=g,this.renderMultiDrawInstances=_}function R2(r){const t={geometries:0,textures:0},i={frame:0,calls:0,triangles:0,points:0,lines:0};function s(c,h,d){switch(i.calls++,h){case r.TRIANGLES:i.triangles+=d*(c/3);break;case r.LINES:i.lines+=d*(c/2);break;case r.LINE_STRIP:i.lines+=d*(c-1);break;case r.LINE_LOOP:i.lines+=d*c;break;case r.POINTS:i.points+=d*c;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",h);break}}function l(){i.calls=0,i.triangles=0,i.points=0,i.lines=0}return{memory:t,render:i,programs:null,autoReset:!0,reset:l,update:s}}function C2(r,t,i){const s=new WeakMap,l=new qe;function c(h,d,m){const p=h.morphTargetInfluences,g=d.morphAttributes.position||d.morphAttributes.normal||d.morphAttributes.color,_=g!==void 0?g.length:0;let x=s.get(d);if(x===void 0||x.count!==_){let C=function(){H.dispose(),s.delete(d),d.removeEventListener("dispose",C)};var S=C;x!==void 0&&x.texture.dispose();const E=d.morphAttributes.position!==void 0,b=d.morphAttributes.normal!==void 0,M=d.morphAttributes.color!==void 0,v=d.morphAttributes.position||[],L=d.morphAttributes.normal||[],U=d.morphAttributes.color||[];let T=0;E===!0&&(T=1),b===!0&&(T=2),M===!0&&(T=3);let V=d.attributes.position.count*T,I=1;V>t.maxTextureSize&&(I=Math.ceil(V/t.maxTextureSize),V=t.maxTextureSize);const P=new Float32Array(V*I*4*_),H=new dx(P,V,I,_);H.type=Ra,H.needsUpdate=!0;const D=T*4;for(let G=0;G<_;G++){const ot=v[G],lt=L[G],mt=U[G],gt=V*I*4*G;for(let B=0;B<ot.count;B++){const $=B*D;E===!0&&(l.fromBufferAttribute(ot,B),P[gt+$+0]=l.x,P[gt+$+1]=l.y,P[gt+$+2]=l.z,P[gt+$+3]=0),b===!0&&(l.fromBufferAttribute(lt,B),P[gt+$+4]=l.x,P[gt+$+5]=l.y,P[gt+$+6]=l.z,P[gt+$+7]=0),M===!0&&(l.fromBufferAttribute(mt,B),P[gt+$+8]=l.x,P[gt+$+9]=l.y,P[gt+$+10]=l.z,P[gt+$+11]=mt.itemSize===4?l.w:1)}}x={count:_,texture:H,size:new Ae(V,I)},s.set(d,x),d.addEventListener("dispose",C)}if(h.isInstancedMesh===!0&&h.morphTexture!==null)m.getUniforms().setValue(r,"morphTexture",h.morphTexture,i);else{let E=0;for(let M=0;M<p.length;M++)E+=p[M];const b=d.morphTargetsRelative?1:1-E;m.getUniforms().setValue(r,"morphTargetBaseInfluence",b),m.getUniforms().setValue(r,"morphTargetInfluences",p)}m.getUniforms().setValue(r,"morphTargetsTexture",x.texture,i),m.getUniforms().setValue(r,"morphTargetsTextureSize",x.size)}return{update:c}}function w2(r,t,i,s){let l=new WeakMap;function c(m){const p=s.render.frame,g=m.geometry,_=t.get(m,g);if(l.get(_)!==p&&(t.update(_),l.set(_,p)),m.isInstancedMesh&&(m.hasEventListener("dispose",d)===!1&&m.addEventListener("dispose",d),l.get(m)!==p&&(i.update(m.instanceMatrix,r.ARRAY_BUFFER),m.instanceColor!==null&&i.update(m.instanceColor,r.ARRAY_BUFFER),l.set(m,p))),m.isSkinnedMesh){const x=m.skeleton;l.get(x)!==p&&(x.update(),l.set(x,p))}return _}function h(){l=new WeakMap}function d(m){const p=m.target;p.removeEventListener("dispose",d),i.remove(p.instanceMatrix),p.instanceColor!==null&&i.remove(p.instanceColor)}return{update:c,dispose:h}}const bx=new ni,ey=new Mx(1,1),Tx=new dx,Ax=new ib,Rx=new Sx,ny=[],iy=[],ay=new Float32Array(16),sy=new Float32Array(9),ry=new Float32Array(4);function zo(r,t,i){const s=r[0];if(s<=0||s>0)return r;const l=t*i;let c=ny[l];if(c===void 0&&(c=new Float32Array(l),ny[l]=c),t!==0){s.toArray(c,0);for(let h=1,d=0;h!==t;++h)d+=i,r[h].toArray(c,d)}return c}function xn(r,t){if(r.length!==t.length)return!1;for(let i=0,s=r.length;i<s;i++)if(r[i]!==t[i])return!1;return!0}function Sn(r,t){for(let i=0,s=t.length;i<s;i++)r[i]=t[i]}function tf(r,t){let i=iy[t];i===void 0&&(i=new Int32Array(t),iy[t]=i);for(let s=0;s!==t;++s)i[s]=r.allocateTextureUnit();return i}function D2(r,t){const i=this.cache;i[0]!==t&&(r.uniform1f(this.addr,t),i[0]=t)}function U2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(r.uniform2f(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(xn(i,t))return;r.uniform2fv(this.addr,t),Sn(i,t)}}function N2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(r.uniform3f(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else if(t.r!==void 0)(i[0]!==t.r||i[1]!==t.g||i[2]!==t.b)&&(r.uniform3f(this.addr,t.r,t.g,t.b),i[0]=t.r,i[1]=t.g,i[2]=t.b);else{if(xn(i,t))return;r.uniform3fv(this.addr,t),Sn(i,t)}}function L2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(r.uniform4f(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(xn(i,t))return;r.uniform4fv(this.addr,t),Sn(i,t)}}function O2(r,t){const i=this.cache,s=t.elements;if(s===void 0){if(xn(i,t))return;r.uniformMatrix2fv(this.addr,!1,t),Sn(i,t)}else{if(xn(i,s))return;ry.set(s),r.uniformMatrix2fv(this.addr,!1,ry),Sn(i,s)}}function P2(r,t){const i=this.cache,s=t.elements;if(s===void 0){if(xn(i,t))return;r.uniformMatrix3fv(this.addr,!1,t),Sn(i,t)}else{if(xn(i,s))return;sy.set(s),r.uniformMatrix3fv(this.addr,!1,sy),Sn(i,s)}}function z2(r,t){const i=this.cache,s=t.elements;if(s===void 0){if(xn(i,t))return;r.uniformMatrix4fv(this.addr,!1,t),Sn(i,t)}else{if(xn(i,s))return;ay.set(s),r.uniformMatrix4fv(this.addr,!1,ay),Sn(i,s)}}function I2(r,t){const i=this.cache;i[0]!==t&&(r.uniform1i(this.addr,t),i[0]=t)}function B2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(r.uniform2i(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(xn(i,t))return;r.uniform2iv(this.addr,t),Sn(i,t)}}function F2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(r.uniform3i(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else{if(xn(i,t))return;r.uniform3iv(this.addr,t),Sn(i,t)}}function H2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(r.uniform4i(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(xn(i,t))return;r.uniform4iv(this.addr,t),Sn(i,t)}}function G2(r,t){const i=this.cache;i[0]!==t&&(r.uniform1ui(this.addr,t),i[0]=t)}function V2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(r.uniform2ui(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(xn(i,t))return;r.uniform2uiv(this.addr,t),Sn(i,t)}}function k2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(r.uniform3ui(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else{if(xn(i,t))return;r.uniform3uiv(this.addr,t),Sn(i,t)}}function X2(r,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(r.uniform4ui(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(xn(i,t))return;r.uniform4uiv(this.addr,t),Sn(i,t)}}function j2(r,t,i){const s=this.cache,l=i.allocateTextureUnit();s[0]!==l&&(r.uniform1i(this.addr,l),s[0]=l);let c;this.type===r.SAMPLER_2D_SHADOW?(ey.compareFunction=ux,c=ey):c=bx,i.setTexture2D(t||c,l)}function q2(r,t,i){const s=this.cache,l=i.allocateTextureUnit();s[0]!==l&&(r.uniform1i(this.addr,l),s[0]=l),i.setTexture3D(t||Ax,l)}function W2(r,t,i){const s=this.cache,l=i.allocateTextureUnit();s[0]!==l&&(r.uniform1i(this.addr,l),s[0]=l),i.setTextureCube(t||Rx,l)}function Y2(r,t,i){const s=this.cache,l=i.allocateTextureUnit();s[0]!==l&&(r.uniform1i(this.addr,l),s[0]=l),i.setTexture2DArray(t||Tx,l)}function Q2(r){switch(r){case 5126:return D2;case 35664:return U2;case 35665:return N2;case 35666:return L2;case 35674:return O2;case 35675:return P2;case 35676:return z2;case 5124:case 35670:return I2;case 35667:case 35671:return B2;case 35668:case 35672:return F2;case 35669:case 35673:return H2;case 5125:return G2;case 36294:return V2;case 36295:return k2;case 36296:return X2;case 35678:case 36198:case 36298:case 36306:case 35682:return j2;case 35679:case 36299:case 36307:return q2;case 35680:case 36300:case 36308:case 36293:return W2;case 36289:case 36303:case 36311:case 36292:return Y2}}function Z2(r,t){r.uniform1fv(this.addr,t)}function K2(r,t){const i=zo(t,this.size,2);r.uniform2fv(this.addr,i)}function J2(r,t){const i=zo(t,this.size,3);r.uniform3fv(this.addr,i)}function $2(r,t){const i=zo(t,this.size,4);r.uniform4fv(this.addr,i)}function tR(r,t){const i=zo(t,this.size,4);r.uniformMatrix2fv(this.addr,!1,i)}function eR(r,t){const i=zo(t,this.size,9);r.uniformMatrix3fv(this.addr,!1,i)}function nR(r,t){const i=zo(t,this.size,16);r.uniformMatrix4fv(this.addr,!1,i)}function iR(r,t){r.uniform1iv(this.addr,t)}function aR(r,t){r.uniform2iv(this.addr,t)}function sR(r,t){r.uniform3iv(this.addr,t)}function rR(r,t){r.uniform4iv(this.addr,t)}function oR(r,t){r.uniform1uiv(this.addr,t)}function lR(r,t){r.uniform2uiv(this.addr,t)}function cR(r,t){r.uniform3uiv(this.addr,t)}function uR(r,t){r.uniform4uiv(this.addr,t)}function fR(r,t,i){const s=this.cache,l=t.length,c=tf(i,l);xn(s,c)||(r.uniform1iv(this.addr,c),Sn(s,c));for(let h=0;h!==l;++h)i.setTexture2D(t[h]||bx,c[h])}function hR(r,t,i){const s=this.cache,l=t.length,c=tf(i,l);xn(s,c)||(r.uniform1iv(this.addr,c),Sn(s,c));for(let h=0;h!==l;++h)i.setTexture3D(t[h]||Ax,c[h])}function dR(r,t,i){const s=this.cache,l=t.length,c=tf(i,l);xn(s,c)||(r.uniform1iv(this.addr,c),Sn(s,c));for(let h=0;h!==l;++h)i.setTextureCube(t[h]||Rx,c[h])}function pR(r,t,i){const s=this.cache,l=t.length,c=tf(i,l);xn(s,c)||(r.uniform1iv(this.addr,c),Sn(s,c));for(let h=0;h!==l;++h)i.setTexture2DArray(t[h]||Tx,c[h])}function mR(r){switch(r){case 5126:return Z2;case 35664:return K2;case 35665:return J2;case 35666:return $2;case 35674:return tR;case 35675:return eR;case 35676:return nR;case 5124:case 35670:return iR;case 35667:case 35671:return aR;case 35668:case 35672:return sR;case 35669:case 35673:return rR;case 5125:return oR;case 36294:return lR;case 36295:return cR;case 36296:return uR;case 35678:case 36198:case 36298:case 36306:case 35682:return fR;case 35679:case 36299:case 36307:return hR;case 35680:case 36300:case 36308:case 36293:return dR;case 36289:case 36303:case 36311:case 36292:return pR}}class gR{constructor(t,i,s){this.id=t,this.addr=s,this.cache=[],this.type=i.type,this.setValue=Q2(i.type)}}class _R{constructor(t,i,s){this.id=t,this.addr=s,this.cache=[],this.type=i.type,this.size=i.size,this.setValue=mR(i.type)}}class vR{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,i,s){const l=this.seq;for(let c=0,h=l.length;c!==h;++c){const d=l[c];d.setValue(t,i[d.id],s)}}}const qd=/(\w+)(\])?(\[|\.)?/g;function oy(r,t){r.seq.push(t),r.map[t.id]=t}function yR(r,t,i){const s=r.name,l=s.length;for(qd.lastIndex=0;;){const c=qd.exec(s),h=qd.lastIndex;let d=c[1];const m=c[2]==="]",p=c[3];if(m&&(d=d|0),p===void 0||p==="["&&h+2===l){oy(i,p===void 0?new gR(d,r,t):new _R(d,r,t));break}else{let _=i.map[d];_===void 0&&(_=new vR(d),oy(i,_)),i=_}}}class Xu{constructor(t,i){this.seq=[],this.map={};const s=t.getProgramParameter(i,t.ACTIVE_UNIFORMS);for(let l=0;l<s;++l){const c=t.getActiveUniform(i,l),h=t.getUniformLocation(i,c.name);yR(c,h,this)}}setValue(t,i,s,l){const c=this.map[i];c!==void 0&&c.setValue(t,s,l)}setOptional(t,i,s){const l=i[s];l!==void 0&&this.setValue(t,s,l)}static upload(t,i,s,l){for(let c=0,h=i.length;c!==h;++c){const d=i[c],m=s[d.id];m.needsUpdate!==!1&&d.setValue(t,m.value,l)}}static seqWithValue(t,i){const s=[];for(let l=0,c=t.length;l!==c;++l){const h=t[l];h.id in i&&s.push(h)}return s}}function ly(r,t,i){const s=r.createShader(t);return r.shaderSource(s,i),r.compileShader(s),s}const xR=37297;let SR=0;function MR(r,t){const i=r.split(`
`),s=[],l=Math.max(t-6,0),c=Math.min(t+6,i.length);for(let h=l;h<c;h++){const d=h+1;s.push(`${d===t?">":" "} ${d}: ${i[h]}`)}return s.join(`
`)}const cy=new ue;function ER(r){Ne._getMatrix(cy,Ne.workingColorSpace,r);const t=`mat3( ${cy.elements.map(i=>i.toFixed(4))} )`;switch(Ne.getTransfer(r)){case qu:return[t,"LinearTransferOETF"];case je:return[t,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[t,"LinearTransferOETF"]}}function uy(r,t,i){const s=r.getShaderParameter(t,r.COMPILE_STATUS),l=r.getShaderInfoLog(t).trim();if(s&&l==="")return"";const c=/ERROR: 0:(\d+)/.exec(l);if(c){const h=parseInt(c[1]);return i.toUpperCase()+`

`+l+`

`+MR(r.getShaderSource(t),h)}else return l}function bR(r,t){const i=ER(t);return[`vec4 ${r}( vec4 value ) {`,`	return ${i[1]}( vec4( value.rgb * ${i[0]}, value.a ) );`,"}"].join(`
`)}function TR(r,t){let i;switch(t){case C1:i="Linear";break;case w1:i="Reinhard";break;case D1:i="Cineon";break;case U1:i="ACESFilmic";break;case L1:i="AgX";break;case O1:i="Neutral";break;case N1:i="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",t),i="Linear"}return"vec3 "+r+"( vec3 color ) { return "+i+"ToneMapping( color ); }"}const zu=new Y;function AR(){Ne.getLuminanceCoefficients(zu);const r=zu.x.toFixed(4),t=zu.y.toFixed(4),i=zu.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${t}, ${i} );`,"	return dot( weights, rgb );","}"].join(`
`)}function RR(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Bl).join(`
`)}function CR(r){const t=[];for(const i in r){const s=r[i];s!==!1&&t.push("#define "+i+" "+s)}return t.join(`
`)}function wR(r,t){const i={},s=r.getProgramParameter(t,r.ACTIVE_ATTRIBUTES);for(let l=0;l<s;l++){const c=r.getActiveAttrib(t,l),h=c.name;let d=1;c.type===r.FLOAT_MAT2&&(d=2),c.type===r.FLOAT_MAT3&&(d=3),c.type===r.FLOAT_MAT4&&(d=4),i[h]={type:c.type,location:r.getAttribLocation(t,h),locationSize:d}}return i}function Bl(r){return r!==""}function fy(r,t){const i=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,i).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function hy(r,t){return r.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const DR=/^[ \t]*#include +<([\w\d./]+)>/gm;function Qp(r){return r.replace(DR,NR)}const UR=new Map;function NR(r,t){let i=fe[t];if(i===void 0){const s=UR.get(t);if(s!==void 0)i=fe[s],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,s);else throw new Error("Can not resolve #include <"+t+">")}return Qp(i)}const LR=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function dy(r){return r.replace(LR,OR)}function OR(r,t,i,s){let l="";for(let c=parseInt(t);c<parseInt(i);c++)l+=s.replace(/\[\s*i\s*\]/g,"[ "+c+" ]").replace(/UNROLLED_LOOP_INDEX/g,c);return l}function py(r){let t=`precision ${r.precision} float;
	precision ${r.precision} int;
	precision ${r.precision} sampler2D;
	precision ${r.precision} samplerCube;
	precision ${r.precision} sampler3D;
	precision ${r.precision} sampler2DArray;
	precision ${r.precision} sampler2DShadow;
	precision ${r.precision} samplerCubeShadow;
	precision ${r.precision} sampler2DArrayShadow;
	precision ${r.precision} isampler2D;
	precision ${r.precision} isampler3D;
	precision ${r.precision} isamplerCube;
	precision ${r.precision} isampler2DArray;
	precision ${r.precision} usampler2D;
	precision ${r.precision} usampler3D;
	precision ${r.precision} usamplerCube;
	precision ${r.precision} usampler2DArray;
	`;return r.precision==="highp"?t+=`
#define HIGH_PRECISION`:r.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:r.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}function PR(r){let t="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===Ky?t="SHADOWMAP_TYPE_PCF":r.shadowMapType===o1?t="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Ea&&(t="SHADOWMAP_TYPE_VSM"),t}function zR(r){let t="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case wo:case Do:t="ENVMAP_TYPE_CUBE";break;case Ku:t="ENVMAP_TYPE_CUBE_UV";break}return t}function IR(r){let t="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Do:t="ENVMAP_MODE_REFRACTION";break}return t}function BR(r){let t="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case Jy:t="ENVMAP_BLENDING_MULTIPLY";break;case A1:t="ENVMAP_BLENDING_MIX";break;case R1:t="ENVMAP_BLENDING_ADD";break}return t}function FR(r){const t=r.envMapCubeUVHeight;if(t===null)return null;const i=Math.log2(t)-2,s=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,i),112)),texelHeight:s,maxMip:i}}function HR(r,t,i,s){const l=r.getContext(),c=i.defines;let h=i.vertexShader,d=i.fragmentShader;const m=PR(i),p=zR(i),g=IR(i),_=BR(i),x=FR(i),S=RR(i),E=CR(c),b=l.createProgram();let M,v,L=i.glslVersion?"#version "+i.glslVersion+`
`:"";i.isRawShaderMaterial?(M=["#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,E].filter(Bl).join(`
`),M.length>0&&(M+=`
`),v=["#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,E].filter(Bl).join(`
`),v.length>0&&(v+=`
`)):(M=[py(i),"#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,E,i.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",i.batching?"#define USE_BATCHING":"",i.batchingColor?"#define USE_BATCHING_COLOR":"",i.instancing?"#define USE_INSTANCING":"",i.instancingColor?"#define USE_INSTANCING_COLOR":"",i.instancingMorph?"#define USE_INSTANCING_MORPH":"",i.useFog&&i.fog?"#define USE_FOG":"",i.useFog&&i.fogExp2?"#define FOG_EXP2":"",i.map?"#define USE_MAP":"",i.envMap?"#define USE_ENVMAP":"",i.envMap?"#define "+g:"",i.lightMap?"#define USE_LIGHTMAP":"",i.aoMap?"#define USE_AOMAP":"",i.bumpMap?"#define USE_BUMPMAP":"",i.normalMap?"#define USE_NORMALMAP":"",i.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",i.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",i.displacementMap?"#define USE_DISPLACEMENTMAP":"",i.emissiveMap?"#define USE_EMISSIVEMAP":"",i.anisotropy?"#define USE_ANISOTROPY":"",i.anisotropyMap?"#define USE_ANISOTROPYMAP":"",i.clearcoatMap?"#define USE_CLEARCOATMAP":"",i.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",i.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",i.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",i.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",i.specularMap?"#define USE_SPECULARMAP":"",i.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",i.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",i.roughnessMap?"#define USE_ROUGHNESSMAP":"",i.metalnessMap?"#define USE_METALNESSMAP":"",i.alphaMap?"#define USE_ALPHAMAP":"",i.alphaHash?"#define USE_ALPHAHASH":"",i.transmission?"#define USE_TRANSMISSION":"",i.transmissionMap?"#define USE_TRANSMISSIONMAP":"",i.thicknessMap?"#define USE_THICKNESSMAP":"",i.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",i.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",i.mapUv?"#define MAP_UV "+i.mapUv:"",i.alphaMapUv?"#define ALPHAMAP_UV "+i.alphaMapUv:"",i.lightMapUv?"#define LIGHTMAP_UV "+i.lightMapUv:"",i.aoMapUv?"#define AOMAP_UV "+i.aoMapUv:"",i.emissiveMapUv?"#define EMISSIVEMAP_UV "+i.emissiveMapUv:"",i.bumpMapUv?"#define BUMPMAP_UV "+i.bumpMapUv:"",i.normalMapUv?"#define NORMALMAP_UV "+i.normalMapUv:"",i.displacementMapUv?"#define DISPLACEMENTMAP_UV "+i.displacementMapUv:"",i.metalnessMapUv?"#define METALNESSMAP_UV "+i.metalnessMapUv:"",i.roughnessMapUv?"#define ROUGHNESSMAP_UV "+i.roughnessMapUv:"",i.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+i.anisotropyMapUv:"",i.clearcoatMapUv?"#define CLEARCOATMAP_UV "+i.clearcoatMapUv:"",i.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+i.clearcoatNormalMapUv:"",i.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+i.clearcoatRoughnessMapUv:"",i.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+i.iridescenceMapUv:"",i.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+i.iridescenceThicknessMapUv:"",i.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+i.sheenColorMapUv:"",i.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+i.sheenRoughnessMapUv:"",i.specularMapUv?"#define SPECULARMAP_UV "+i.specularMapUv:"",i.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+i.specularColorMapUv:"",i.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+i.specularIntensityMapUv:"",i.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+i.transmissionMapUv:"",i.thicknessMapUv?"#define THICKNESSMAP_UV "+i.thicknessMapUv:"",i.vertexTangents&&i.flatShading===!1?"#define USE_TANGENT":"",i.vertexColors?"#define USE_COLOR":"",i.vertexAlphas?"#define USE_COLOR_ALPHA":"",i.vertexUv1s?"#define USE_UV1":"",i.vertexUv2s?"#define USE_UV2":"",i.vertexUv3s?"#define USE_UV3":"",i.pointsUvs?"#define USE_POINTS_UV":"",i.flatShading?"#define FLAT_SHADED":"",i.skinning?"#define USE_SKINNING":"",i.morphTargets?"#define USE_MORPHTARGETS":"",i.morphNormals&&i.flatShading===!1?"#define USE_MORPHNORMALS":"",i.morphColors?"#define USE_MORPHCOLORS":"",i.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+i.morphTextureStride:"",i.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+i.morphTargetsCount:"",i.doubleSided?"#define DOUBLE_SIDED":"",i.flipSided?"#define FLIP_SIDED":"",i.shadowMapEnabled?"#define USE_SHADOWMAP":"",i.shadowMapEnabled?"#define "+m:"",i.sizeAttenuation?"#define USE_SIZEATTENUATION":"",i.numLightProbes>0?"#define USE_LIGHT_PROBES":"",i.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",i.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Bl).join(`
`),v=[py(i),"#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,E,i.useFog&&i.fog?"#define USE_FOG":"",i.useFog&&i.fogExp2?"#define FOG_EXP2":"",i.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",i.map?"#define USE_MAP":"",i.matcap?"#define USE_MATCAP":"",i.envMap?"#define USE_ENVMAP":"",i.envMap?"#define "+p:"",i.envMap?"#define "+g:"",i.envMap?"#define "+_:"",x?"#define CUBEUV_TEXEL_WIDTH "+x.texelWidth:"",x?"#define CUBEUV_TEXEL_HEIGHT "+x.texelHeight:"",x?"#define CUBEUV_MAX_MIP "+x.maxMip+".0":"",i.lightMap?"#define USE_LIGHTMAP":"",i.aoMap?"#define USE_AOMAP":"",i.bumpMap?"#define USE_BUMPMAP":"",i.normalMap?"#define USE_NORMALMAP":"",i.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",i.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",i.emissiveMap?"#define USE_EMISSIVEMAP":"",i.anisotropy?"#define USE_ANISOTROPY":"",i.anisotropyMap?"#define USE_ANISOTROPYMAP":"",i.clearcoat?"#define USE_CLEARCOAT":"",i.clearcoatMap?"#define USE_CLEARCOATMAP":"",i.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",i.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",i.dispersion?"#define USE_DISPERSION":"",i.iridescence?"#define USE_IRIDESCENCE":"",i.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",i.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",i.specularMap?"#define USE_SPECULARMAP":"",i.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",i.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",i.roughnessMap?"#define USE_ROUGHNESSMAP":"",i.metalnessMap?"#define USE_METALNESSMAP":"",i.alphaMap?"#define USE_ALPHAMAP":"",i.alphaTest?"#define USE_ALPHATEST":"",i.alphaHash?"#define USE_ALPHAHASH":"",i.sheen?"#define USE_SHEEN":"",i.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",i.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",i.transmission?"#define USE_TRANSMISSION":"",i.transmissionMap?"#define USE_TRANSMISSIONMAP":"",i.thicknessMap?"#define USE_THICKNESSMAP":"",i.vertexTangents&&i.flatShading===!1?"#define USE_TANGENT":"",i.vertexColors||i.instancingColor||i.batchingColor?"#define USE_COLOR":"",i.vertexAlphas?"#define USE_COLOR_ALPHA":"",i.vertexUv1s?"#define USE_UV1":"",i.vertexUv2s?"#define USE_UV2":"",i.vertexUv3s?"#define USE_UV3":"",i.pointsUvs?"#define USE_POINTS_UV":"",i.gradientMap?"#define USE_GRADIENTMAP":"",i.flatShading?"#define FLAT_SHADED":"",i.doubleSided?"#define DOUBLE_SIDED":"",i.flipSided?"#define FLIP_SIDED":"",i.shadowMapEnabled?"#define USE_SHADOWMAP":"",i.shadowMapEnabled?"#define "+m:"",i.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",i.numLightProbes>0?"#define USE_LIGHT_PROBES":"",i.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",i.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",i.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",i.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",i.toneMapping!==ys?"#define TONE_MAPPING":"",i.toneMapping!==ys?fe.tonemapping_pars_fragment:"",i.toneMapping!==ys?TR("toneMapping",i.toneMapping):"",i.dithering?"#define DITHERING":"",i.opaque?"#define OPAQUE":"",fe.colorspace_pars_fragment,bR("linearToOutputTexel",i.outputColorSpace),AR(),i.useDepthPacking?"#define DEPTH_PACKING "+i.depthPacking:"",`
`].filter(Bl).join(`
`)),h=Qp(h),h=fy(h,i),h=hy(h,i),d=Qp(d),d=fy(d,i),d=hy(d,i),h=dy(h),d=dy(d),i.isRawShaderMaterial!==!0&&(L=`#version 300 es
`,M=[S,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+M,v=["#define varying in",i.glslVersion===Ev?"":"layout(location = 0) out highp vec4 pc_fragColor;",i.glslVersion===Ev?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+v);const U=L+M+h,T=L+v+d,V=ly(l,l.VERTEX_SHADER,U),I=ly(l,l.FRAGMENT_SHADER,T);l.attachShader(b,V),l.attachShader(b,I),i.index0AttributeName!==void 0?l.bindAttribLocation(b,0,i.index0AttributeName):i.morphTargets===!0&&l.bindAttribLocation(b,0,"position"),l.linkProgram(b);function P(G){if(r.debug.checkShaderErrors){const ot=l.getProgramInfoLog(b).trim(),lt=l.getShaderInfoLog(V).trim(),mt=l.getShaderInfoLog(I).trim();let gt=!0,B=!0;if(l.getProgramParameter(b,l.LINK_STATUS)===!1)if(gt=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(l,b,V,I);else{const $=uy(l,V,"vertex"),J=uy(l,I,"fragment");console.error("THREE.WebGLProgram: Shader Error "+l.getError()+" - VALIDATE_STATUS "+l.getProgramParameter(b,l.VALIDATE_STATUS)+`

Material Name: `+G.name+`
Material Type: `+G.type+`

Program Info Log: `+ot+`
`+$+`
`+J)}else ot!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ot):(lt===""||mt==="")&&(B=!1);B&&(G.diagnostics={runnable:gt,programLog:ot,vertexShader:{log:lt,prefix:M},fragmentShader:{log:mt,prefix:v}})}l.deleteShader(V),l.deleteShader(I),H=new Xu(l,b),D=wR(l,b)}let H;this.getUniforms=function(){return H===void 0&&P(this),H};let D;this.getAttributes=function(){return D===void 0&&P(this),D};let C=i.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return C===!1&&(C=l.getProgramParameter(b,xR)),C},this.destroy=function(){s.releaseStatesOfProgram(this),l.deleteProgram(b),this.program=void 0},this.type=i.shaderType,this.name=i.shaderName,this.id=SR++,this.cacheKey=t,this.usedTimes=1,this.program=b,this.vertexShader=V,this.fragmentShader=I,this}let GR=0;class VR{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const i=t.vertexShader,s=t.fragmentShader,l=this._getShaderStage(i),c=this._getShaderStage(s),h=this._getShaderCacheForMaterial(t);return h.has(l)===!1&&(h.add(l),l.usedTimes++),h.has(c)===!1&&(h.add(c),c.usedTimes++),this}remove(t){const i=this.materialCache.get(t);for(const s of i)s.usedTimes--,s.usedTimes===0&&this.shaderCache.delete(s.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const i=this.materialCache;let s=i.get(t);return s===void 0&&(s=new Set,i.set(t,s)),s}_getShaderStage(t){const i=this.shaderCache;let s=i.get(t);return s===void 0&&(s=new kR(t),i.set(t,s)),s}}class kR{constructor(t){this.id=GR++,this.code=t,this.usedTimes=0}}function XR(r,t,i,s,l,c,h){const d=new mx,m=new VR,p=new Set,g=[],_=l.logarithmicDepthBuffer,x=l.vertexTextures;let S=l.precision;const E={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function b(D){return p.add(D),D===0?"uv":`uv${D}`}function M(D,C,G,ot,lt){const mt=ot.fog,gt=lt.geometry,B=D.isMeshStandardMaterial?ot.environment:null,$=(D.isMeshStandardMaterial?i:t).get(D.envMap||B),J=$&&$.mapping===Ku?$.image.height:null,Et=E[D.type];D.precision!==null&&(S=l.getMaxPrecision(D.precision),S!==D.precision&&console.warn("THREE.WebGLProgram.getParameters:",D.precision,"not supported, using",S,"instead."));const At=gt.morphAttributes.position||gt.morphAttributes.normal||gt.morphAttributes.color,z=At!==void 0?At.length:0;let at=0;gt.morphAttributes.position!==void 0&&(at=1),gt.morphAttributes.normal!==void 0&&(at=2),gt.morphAttributes.color!==void 0&&(at=3);let Mt,K,ft,Tt;if(Et){const Re=Qi[Et];Mt=Re.vertexShader,K=Re.fragmentShader}else Mt=D.vertexShader,K=D.fragmentShader,m.update(D),ft=m.getVertexShaderID(D),Tt=m.getFragmentShaderID(D);const St=r.getRenderTarget(),kt=r.state.buffers.depth.getReversed(),Gt=lt.isInstancedMesh===!0,se=lt.isBatchedMesh===!0,He=!!D.map,de=!!D.matcap,$e=!!$,k=!!D.aoMap,On=!!D.lightMap,he=!!D.bumpMap,ve=!!D.normalMap,Yt=!!D.displacementMap,Ie=!!D.emissiveMap,Wt=!!D.metalnessMap,O=!!D.roughnessMap,R=D.anisotropy>0,it=D.clearcoat>0,dt=D.dispersion>0,bt=D.iridescence>0,_t=D.sheen>0,jt=D.transmission>0,Dt=R&&!!D.anisotropyMap,Bt=it&&!!D.clearcoatMap,ye=it&&!!D.clearcoatNormalMap,Rt=it&&!!D.clearcoatRoughnessMap,Ft=bt&&!!D.iridescenceMap,Qt=bt&&!!D.iridescenceThicknessMap,qt=_t&&!!D.sheenColorMap,Ot=_t&&!!D.sheenRoughnessMap,ee=!!D.specularMap,re=!!D.specularColorMap,Ge=!!D.specularIntensityMap,q=jt&&!!D.transmissionMap,Ct=jt&&!!D.thicknessMap,ut=!!D.gradientMap,yt=!!D.alphaMap,wt=D.alphaTest>0,Ut=!!D.alphaHash,ne=!!D.extensions;let tn=ys;D.toneMapped&&(St===null||St.isXRRenderTarget===!0)&&(tn=r.toneMapping);const _n={shaderID:Et,shaderType:D.type,shaderName:D.name,vertexShader:Mt,fragmentShader:K,defines:D.defines,customVertexShaderID:ft,customFragmentShaderID:Tt,isRawShaderMaterial:D.isRawShaderMaterial===!0,glslVersion:D.glslVersion,precision:S,batching:se,batchingColor:se&&lt._colorsTexture!==null,instancing:Gt,instancingColor:Gt&&lt.instanceColor!==null,instancingMorph:Gt&&lt.morphTexture!==null,supportsVertexTextures:x,outputColorSpace:St===null?r.outputColorSpace:St.isXRRenderTarget===!0?St.texture.colorSpace:Lo,alphaToCoverage:!!D.alphaToCoverage,map:He,matcap:de,envMap:$e,envMapMode:$e&&$.mapping,envMapCubeUVHeight:J,aoMap:k,lightMap:On,bumpMap:he,normalMap:ve,displacementMap:x&&Yt,emissiveMap:Ie,normalMapObjectSpace:ve&&D.normalMapType===F1,normalMapTangentSpace:ve&&D.normalMapType===B1,metalnessMap:Wt,roughnessMap:O,anisotropy:R,anisotropyMap:Dt,clearcoat:it,clearcoatMap:Bt,clearcoatNormalMap:ye,clearcoatRoughnessMap:Rt,dispersion:dt,iridescence:bt,iridescenceMap:Ft,iridescenceThicknessMap:Qt,sheen:_t,sheenColorMap:qt,sheenRoughnessMap:Ot,specularMap:ee,specularColorMap:re,specularIntensityMap:Ge,transmission:jt,transmissionMap:q,thicknessMap:Ct,gradientMap:ut,opaque:D.transparent===!1&&D.blending===fo&&D.alphaToCoverage===!1,alphaMap:yt,alphaTest:wt,alphaHash:Ut,combine:D.combine,mapUv:He&&b(D.map.channel),aoMapUv:k&&b(D.aoMap.channel),lightMapUv:On&&b(D.lightMap.channel),bumpMapUv:he&&b(D.bumpMap.channel),normalMapUv:ve&&b(D.normalMap.channel),displacementMapUv:Yt&&b(D.displacementMap.channel),emissiveMapUv:Ie&&b(D.emissiveMap.channel),metalnessMapUv:Wt&&b(D.metalnessMap.channel),roughnessMapUv:O&&b(D.roughnessMap.channel),anisotropyMapUv:Dt&&b(D.anisotropyMap.channel),clearcoatMapUv:Bt&&b(D.clearcoatMap.channel),clearcoatNormalMapUv:ye&&b(D.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Rt&&b(D.clearcoatRoughnessMap.channel),iridescenceMapUv:Ft&&b(D.iridescenceMap.channel),iridescenceThicknessMapUv:Qt&&b(D.iridescenceThicknessMap.channel),sheenColorMapUv:qt&&b(D.sheenColorMap.channel),sheenRoughnessMapUv:Ot&&b(D.sheenRoughnessMap.channel),specularMapUv:ee&&b(D.specularMap.channel),specularColorMapUv:re&&b(D.specularColorMap.channel),specularIntensityMapUv:Ge&&b(D.specularIntensityMap.channel),transmissionMapUv:q&&b(D.transmissionMap.channel),thicknessMapUv:Ct&&b(D.thicknessMap.channel),alphaMapUv:yt&&b(D.alphaMap.channel),vertexTangents:!!gt.attributes.tangent&&(ve||R),vertexColors:D.vertexColors,vertexAlphas:D.vertexColors===!0&&!!gt.attributes.color&&gt.attributes.color.itemSize===4,pointsUvs:lt.isPoints===!0&&!!gt.attributes.uv&&(He||yt),fog:!!mt,useFog:D.fog===!0,fogExp2:!!mt&&mt.isFogExp2,flatShading:D.flatShading===!0,sizeAttenuation:D.sizeAttenuation===!0,logarithmicDepthBuffer:_,reverseDepthBuffer:kt,skinning:lt.isSkinnedMesh===!0,morphTargets:gt.morphAttributes.position!==void 0,morphNormals:gt.morphAttributes.normal!==void 0,morphColors:gt.morphAttributes.color!==void 0,morphTargetsCount:z,morphTextureStride:at,numDirLights:C.directional.length,numPointLights:C.point.length,numSpotLights:C.spot.length,numSpotLightMaps:C.spotLightMap.length,numRectAreaLights:C.rectArea.length,numHemiLights:C.hemi.length,numDirLightShadows:C.directionalShadowMap.length,numPointLightShadows:C.pointShadowMap.length,numSpotLightShadows:C.spotShadowMap.length,numSpotLightShadowsWithMaps:C.numSpotLightShadowsWithMaps,numLightProbes:C.numLightProbes,numClippingPlanes:h.numPlanes,numClipIntersection:h.numIntersection,dithering:D.dithering,shadowMapEnabled:r.shadowMap.enabled&&G.length>0,shadowMapType:r.shadowMap.type,toneMapping:tn,decodeVideoTexture:He&&D.map.isVideoTexture===!0&&Ne.getTransfer(D.map.colorSpace)===je,decodeVideoTextureEmissive:Ie&&D.emissiveMap.isVideoTexture===!0&&Ne.getTransfer(D.emissiveMap.colorSpace)===je,premultipliedAlpha:D.premultipliedAlpha,doubleSided:D.side===Aa,flipSided:D.side===ei,useDepthPacking:D.depthPacking>=0,depthPacking:D.depthPacking||0,index0AttributeName:D.index0AttributeName,extensionClipCullDistance:ne&&D.extensions.clipCullDistance===!0&&s.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ne&&D.extensions.multiDraw===!0||se)&&s.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:s.has("KHR_parallel_shader_compile"),customProgramCacheKey:D.customProgramCacheKey()};return _n.vertexUv1s=p.has(1),_n.vertexUv2s=p.has(2),_n.vertexUv3s=p.has(3),p.clear(),_n}function v(D){const C=[];if(D.shaderID?C.push(D.shaderID):(C.push(D.customVertexShaderID),C.push(D.customFragmentShaderID)),D.defines!==void 0)for(const G in D.defines)C.push(G),C.push(D.defines[G]);return D.isRawShaderMaterial===!1&&(L(C,D),U(C,D),C.push(r.outputColorSpace)),C.push(D.customProgramCacheKey),C.join()}function L(D,C){D.push(C.precision),D.push(C.outputColorSpace),D.push(C.envMapMode),D.push(C.envMapCubeUVHeight),D.push(C.mapUv),D.push(C.alphaMapUv),D.push(C.lightMapUv),D.push(C.aoMapUv),D.push(C.bumpMapUv),D.push(C.normalMapUv),D.push(C.displacementMapUv),D.push(C.emissiveMapUv),D.push(C.metalnessMapUv),D.push(C.roughnessMapUv),D.push(C.anisotropyMapUv),D.push(C.clearcoatMapUv),D.push(C.clearcoatNormalMapUv),D.push(C.clearcoatRoughnessMapUv),D.push(C.iridescenceMapUv),D.push(C.iridescenceThicknessMapUv),D.push(C.sheenColorMapUv),D.push(C.sheenRoughnessMapUv),D.push(C.specularMapUv),D.push(C.specularColorMapUv),D.push(C.specularIntensityMapUv),D.push(C.transmissionMapUv),D.push(C.thicknessMapUv),D.push(C.combine),D.push(C.fogExp2),D.push(C.sizeAttenuation),D.push(C.morphTargetsCount),D.push(C.morphAttributeCount),D.push(C.numDirLights),D.push(C.numPointLights),D.push(C.numSpotLights),D.push(C.numSpotLightMaps),D.push(C.numHemiLights),D.push(C.numRectAreaLights),D.push(C.numDirLightShadows),D.push(C.numPointLightShadows),D.push(C.numSpotLightShadows),D.push(C.numSpotLightShadowsWithMaps),D.push(C.numLightProbes),D.push(C.shadowMapType),D.push(C.toneMapping),D.push(C.numClippingPlanes),D.push(C.numClipIntersection),D.push(C.depthPacking)}function U(D,C){d.disableAll(),C.supportsVertexTextures&&d.enable(0),C.instancing&&d.enable(1),C.instancingColor&&d.enable(2),C.instancingMorph&&d.enable(3),C.matcap&&d.enable(4),C.envMap&&d.enable(5),C.normalMapObjectSpace&&d.enable(6),C.normalMapTangentSpace&&d.enable(7),C.clearcoat&&d.enable(8),C.iridescence&&d.enable(9),C.alphaTest&&d.enable(10),C.vertexColors&&d.enable(11),C.vertexAlphas&&d.enable(12),C.vertexUv1s&&d.enable(13),C.vertexUv2s&&d.enable(14),C.vertexUv3s&&d.enable(15),C.vertexTangents&&d.enable(16),C.anisotropy&&d.enable(17),C.alphaHash&&d.enable(18),C.batching&&d.enable(19),C.dispersion&&d.enable(20),C.batchingColor&&d.enable(21),D.push(d.mask),d.disableAll(),C.fog&&d.enable(0),C.useFog&&d.enable(1),C.flatShading&&d.enable(2),C.logarithmicDepthBuffer&&d.enable(3),C.reverseDepthBuffer&&d.enable(4),C.skinning&&d.enable(5),C.morphTargets&&d.enable(6),C.morphNormals&&d.enable(7),C.morphColors&&d.enable(8),C.premultipliedAlpha&&d.enable(9),C.shadowMapEnabled&&d.enable(10),C.doubleSided&&d.enable(11),C.flipSided&&d.enable(12),C.useDepthPacking&&d.enable(13),C.dithering&&d.enable(14),C.transmission&&d.enable(15),C.sheen&&d.enable(16),C.opaque&&d.enable(17),C.pointsUvs&&d.enable(18),C.decodeVideoTexture&&d.enable(19),C.decodeVideoTextureEmissive&&d.enable(20),C.alphaToCoverage&&d.enable(21),D.push(d.mask)}function T(D){const C=E[D.type];let G;if(C){const ot=Qi[C];G=mb.clone(ot.uniforms)}else G=D.uniforms;return G}function V(D,C){let G;for(let ot=0,lt=g.length;ot<lt;ot++){const mt=g[ot];if(mt.cacheKey===C){G=mt,++G.usedTimes;break}}return G===void 0&&(G=new HR(r,C,D,c),g.push(G)),G}function I(D){if(--D.usedTimes===0){const C=g.indexOf(D);g[C]=g[g.length-1],g.pop(),D.destroy()}}function P(D){m.remove(D)}function H(){m.dispose()}return{getParameters:M,getProgramCacheKey:v,getUniforms:T,acquireProgram:V,releaseProgram:I,releaseShaderCache:P,programs:g,dispose:H}}function jR(){let r=new WeakMap;function t(h){return r.has(h)}function i(h){let d=r.get(h);return d===void 0&&(d={},r.set(h,d)),d}function s(h){r.delete(h)}function l(h,d,m){r.get(h)[d]=m}function c(){r=new WeakMap}return{has:t,get:i,remove:s,update:l,dispose:c}}function qR(r,t){return r.groupOrder!==t.groupOrder?r.groupOrder-t.groupOrder:r.renderOrder!==t.renderOrder?r.renderOrder-t.renderOrder:r.material.id!==t.material.id?r.material.id-t.material.id:r.z!==t.z?r.z-t.z:r.id-t.id}function my(r,t){return r.groupOrder!==t.groupOrder?r.groupOrder-t.groupOrder:r.renderOrder!==t.renderOrder?r.renderOrder-t.renderOrder:r.z!==t.z?t.z-r.z:r.id-t.id}function gy(){const r=[];let t=0;const i=[],s=[],l=[];function c(){t=0,i.length=0,s.length=0,l.length=0}function h(_,x,S,E,b,M){let v=r[t];return v===void 0?(v={id:_.id,object:_,geometry:x,material:S,groupOrder:E,renderOrder:_.renderOrder,z:b,group:M},r[t]=v):(v.id=_.id,v.object=_,v.geometry=x,v.material=S,v.groupOrder=E,v.renderOrder=_.renderOrder,v.z=b,v.group=M),t++,v}function d(_,x,S,E,b,M){const v=h(_,x,S,E,b,M);S.transmission>0?s.push(v):S.transparent===!0?l.push(v):i.push(v)}function m(_,x,S,E,b,M){const v=h(_,x,S,E,b,M);S.transmission>0?s.unshift(v):S.transparent===!0?l.unshift(v):i.unshift(v)}function p(_,x){i.length>1&&i.sort(_||qR),s.length>1&&s.sort(x||my),l.length>1&&l.sort(x||my)}function g(){for(let _=t,x=r.length;_<x;_++){const S=r[_];if(S.id===null)break;S.id=null,S.object=null,S.geometry=null,S.material=null,S.group=null}}return{opaque:i,transmissive:s,transparent:l,init:c,push:d,unshift:m,finish:g,sort:p}}function WR(){let r=new WeakMap;function t(s,l){const c=r.get(s);let h;return c===void 0?(h=new gy,r.set(s,[h])):l>=c.length?(h=new gy,c.push(h)):h=c[l],h}function i(){r=new WeakMap}return{get:t,dispose:i}}function YR(){const r={};return{get:function(t){if(r[t.id]!==void 0)return r[t.id];let i;switch(t.type){case"DirectionalLight":i={direction:new Y,color:new Oe};break;case"SpotLight":i={position:new Y,direction:new Y,color:new Oe,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":i={position:new Y,color:new Oe,distance:0,decay:0};break;case"HemisphereLight":i={direction:new Y,skyColor:new Oe,groundColor:new Oe};break;case"RectAreaLight":i={color:new Oe,position:new Y,halfWidth:new Y,halfHeight:new Y};break}return r[t.id]=i,i}}}function QR(){const r={};return{get:function(t){if(r[t.id]!==void 0)return r[t.id];let i;switch(t.type){case"DirectionalLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Ae};break;case"SpotLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Ae};break;case"PointLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Ae,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[t.id]=i,i}}}let ZR=0;function KR(r,t){return(t.castShadow?2:0)-(r.castShadow?2:0)+(t.map?1:0)-(r.map?1:0)}function JR(r){const t=new YR,i=QR(),s={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let p=0;p<9;p++)s.probe.push(new Y);const l=new Y,c=new Je,h=new Je;function d(p){let g=0,_=0,x=0;for(let D=0;D<9;D++)s.probe[D].set(0,0,0);let S=0,E=0,b=0,M=0,v=0,L=0,U=0,T=0,V=0,I=0,P=0;p.sort(KR);for(let D=0,C=p.length;D<C;D++){const G=p[D],ot=G.color,lt=G.intensity,mt=G.distance,gt=G.shadow&&G.shadow.map?G.shadow.map.texture:null;if(G.isAmbientLight)g+=ot.r*lt,_+=ot.g*lt,x+=ot.b*lt;else if(G.isLightProbe){for(let B=0;B<9;B++)s.probe[B].addScaledVector(G.sh.coefficients[B],lt);P++}else if(G.isDirectionalLight){const B=t.get(G);if(B.color.copy(G.color).multiplyScalar(G.intensity),G.castShadow){const $=G.shadow,J=i.get(G);J.shadowIntensity=$.intensity,J.shadowBias=$.bias,J.shadowNormalBias=$.normalBias,J.shadowRadius=$.radius,J.shadowMapSize=$.mapSize,s.directionalShadow[S]=J,s.directionalShadowMap[S]=gt,s.directionalShadowMatrix[S]=G.shadow.matrix,L++}s.directional[S]=B,S++}else if(G.isSpotLight){const B=t.get(G);B.position.setFromMatrixPosition(G.matrixWorld),B.color.copy(ot).multiplyScalar(lt),B.distance=mt,B.coneCos=Math.cos(G.angle),B.penumbraCos=Math.cos(G.angle*(1-G.penumbra)),B.decay=G.decay,s.spot[b]=B;const $=G.shadow;if(G.map&&(s.spotLightMap[V]=G.map,V++,$.updateMatrices(G),G.castShadow&&I++),s.spotLightMatrix[b]=$.matrix,G.castShadow){const J=i.get(G);J.shadowIntensity=$.intensity,J.shadowBias=$.bias,J.shadowNormalBias=$.normalBias,J.shadowRadius=$.radius,J.shadowMapSize=$.mapSize,s.spotShadow[b]=J,s.spotShadowMap[b]=gt,T++}b++}else if(G.isRectAreaLight){const B=t.get(G);B.color.copy(ot).multiplyScalar(lt),B.halfWidth.set(G.width*.5,0,0),B.halfHeight.set(0,G.height*.5,0),s.rectArea[M]=B,M++}else if(G.isPointLight){const B=t.get(G);if(B.color.copy(G.color).multiplyScalar(G.intensity),B.distance=G.distance,B.decay=G.decay,G.castShadow){const $=G.shadow,J=i.get(G);J.shadowIntensity=$.intensity,J.shadowBias=$.bias,J.shadowNormalBias=$.normalBias,J.shadowRadius=$.radius,J.shadowMapSize=$.mapSize,J.shadowCameraNear=$.camera.near,J.shadowCameraFar=$.camera.far,s.pointShadow[E]=J,s.pointShadowMap[E]=gt,s.pointShadowMatrix[E]=G.shadow.matrix,U++}s.point[E]=B,E++}else if(G.isHemisphereLight){const B=t.get(G);B.skyColor.copy(G.color).multiplyScalar(lt),B.groundColor.copy(G.groundColor).multiplyScalar(lt),s.hemi[v]=B,v++}}M>0&&(r.has("OES_texture_float_linear")===!0?(s.rectAreaLTC1=Lt.LTC_FLOAT_1,s.rectAreaLTC2=Lt.LTC_FLOAT_2):(s.rectAreaLTC1=Lt.LTC_HALF_1,s.rectAreaLTC2=Lt.LTC_HALF_2)),s.ambient[0]=g,s.ambient[1]=_,s.ambient[2]=x;const H=s.hash;(H.directionalLength!==S||H.pointLength!==E||H.spotLength!==b||H.rectAreaLength!==M||H.hemiLength!==v||H.numDirectionalShadows!==L||H.numPointShadows!==U||H.numSpotShadows!==T||H.numSpotMaps!==V||H.numLightProbes!==P)&&(s.directional.length=S,s.spot.length=b,s.rectArea.length=M,s.point.length=E,s.hemi.length=v,s.directionalShadow.length=L,s.directionalShadowMap.length=L,s.pointShadow.length=U,s.pointShadowMap.length=U,s.spotShadow.length=T,s.spotShadowMap.length=T,s.directionalShadowMatrix.length=L,s.pointShadowMatrix.length=U,s.spotLightMatrix.length=T+V-I,s.spotLightMap.length=V,s.numSpotLightShadowsWithMaps=I,s.numLightProbes=P,H.directionalLength=S,H.pointLength=E,H.spotLength=b,H.rectAreaLength=M,H.hemiLength=v,H.numDirectionalShadows=L,H.numPointShadows=U,H.numSpotShadows=T,H.numSpotMaps=V,H.numLightProbes=P,s.version=ZR++)}function m(p,g){let _=0,x=0,S=0,E=0,b=0;const M=g.matrixWorldInverse;for(let v=0,L=p.length;v<L;v++){const U=p[v];if(U.isDirectionalLight){const T=s.directional[_];T.direction.setFromMatrixPosition(U.matrixWorld),l.setFromMatrixPosition(U.target.matrixWorld),T.direction.sub(l),T.direction.transformDirection(M),_++}else if(U.isSpotLight){const T=s.spot[S];T.position.setFromMatrixPosition(U.matrixWorld),T.position.applyMatrix4(M),T.direction.setFromMatrixPosition(U.matrixWorld),l.setFromMatrixPosition(U.target.matrixWorld),T.direction.sub(l),T.direction.transformDirection(M),S++}else if(U.isRectAreaLight){const T=s.rectArea[E];T.position.setFromMatrixPosition(U.matrixWorld),T.position.applyMatrix4(M),h.identity(),c.copy(U.matrixWorld),c.premultiply(M),h.extractRotation(c),T.halfWidth.set(U.width*.5,0,0),T.halfHeight.set(0,U.height*.5,0),T.halfWidth.applyMatrix4(h),T.halfHeight.applyMatrix4(h),E++}else if(U.isPointLight){const T=s.point[x];T.position.setFromMatrixPosition(U.matrixWorld),T.position.applyMatrix4(M),x++}else if(U.isHemisphereLight){const T=s.hemi[b];T.direction.setFromMatrixPosition(U.matrixWorld),T.direction.transformDirection(M),b++}}}return{setup:d,setupView:m,state:s}}function _y(r){const t=new JR(r),i=[],s=[];function l(g){p.camera=g,i.length=0,s.length=0}function c(g){i.push(g)}function h(g){s.push(g)}function d(){t.setup(i)}function m(g){t.setupView(i,g)}const p={lightsArray:i,shadowsArray:s,camera:null,lights:t,transmissionRenderTarget:{}};return{init:l,state:p,setupLights:d,setupLightsView:m,pushLight:c,pushShadow:h}}function $R(r){let t=new WeakMap;function i(l,c=0){const h=t.get(l);let d;return h===void 0?(d=new _y(r),t.set(l,[d])):c>=h.length?(d=new _y(r),h.push(d)):d=h[c],d}function s(){t=new WeakMap}return{get:i,dispose:s}}const tC=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,eC=`uniform sampler2D shadow_pass;
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
}`;function nC(r,t,i){let s=new cm;const l=new Ae,c=new Ae,h=new qe,d=new Tb({depthPacking:I1}),m=new Ab,p={},g=i.maxTextureSize,_={[xs]:ei,[ei]:xs,[Aa]:Aa},x=new Ss({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Ae},radius:{value:4}},vertexShader:tC,fragmentShader:eC}),S=x.clone();S.defines.HORIZONTAL_PASS=1;const E=new mi;E.setAttribute("position",new Ki(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const b=new Ri(E,x),M=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Ky;let v=this.type;this.render=function(I,P,H){if(M.enabled===!1||M.autoUpdate===!1&&M.needsUpdate===!1||I.length===0)return;const D=r.getRenderTarget(),C=r.getActiveCubeFace(),G=r.getActiveMipmapLevel(),ot=r.state;ot.setBlending(vs),ot.buffers.color.setClear(1,1,1,1),ot.buffers.depth.setTest(!0),ot.setScissorTest(!1);const lt=v!==Ea&&this.type===Ea,mt=v===Ea&&this.type!==Ea;for(let gt=0,B=I.length;gt<B;gt++){const $=I[gt],J=$.shadow;if(J===void 0){console.warn("THREE.WebGLShadowMap:",$,"has no shadow.");continue}if(J.autoUpdate===!1&&J.needsUpdate===!1)continue;l.copy(J.mapSize);const Et=J.getFrameExtents();if(l.multiply(Et),c.copy(J.mapSize),(l.x>g||l.y>g)&&(l.x>g&&(c.x=Math.floor(g/Et.x),l.x=c.x*Et.x,J.mapSize.x=c.x),l.y>g&&(c.y=Math.floor(g/Et.y),l.y=c.y*Et.y,J.mapSize.y=c.y)),J.map===null||lt===!0||mt===!0){const z=this.type!==Ea?{minFilter:Fi,magFilter:Fi}:{};J.map!==null&&J.map.dispose(),J.map=new dr(l.x,l.y,z),J.map.texture.name=$.name+".shadowMap",J.camera.updateProjectionMatrix()}r.setRenderTarget(J.map),r.clear();const At=J.getViewportCount();for(let z=0;z<At;z++){const at=J.getViewport(z);h.set(c.x*at.x,c.y*at.y,c.x*at.z,c.y*at.w),ot.viewport(h),J.updateMatrices($,z),s=J.getFrustum(),T(P,H,J.camera,$,this.type)}J.isPointLightShadow!==!0&&this.type===Ea&&L(J,H),J.needsUpdate=!1}v=this.type,M.needsUpdate=!1,r.setRenderTarget(D,C,G)};function L(I,P){const H=t.update(b);x.defines.VSM_SAMPLES!==I.blurSamples&&(x.defines.VSM_SAMPLES=I.blurSamples,S.defines.VSM_SAMPLES=I.blurSamples,x.needsUpdate=!0,S.needsUpdate=!0),I.mapPass===null&&(I.mapPass=new dr(l.x,l.y)),x.uniforms.shadow_pass.value=I.map.texture,x.uniforms.resolution.value=I.mapSize,x.uniforms.radius.value=I.radius,r.setRenderTarget(I.mapPass),r.clear(),r.renderBufferDirect(P,null,H,x,b,null),S.uniforms.shadow_pass.value=I.mapPass.texture,S.uniforms.resolution.value=I.mapSize,S.uniforms.radius.value=I.radius,r.setRenderTarget(I.map),r.clear(),r.renderBufferDirect(P,null,H,S,b,null)}function U(I,P,H,D){let C=null;const G=H.isPointLight===!0?I.customDistanceMaterial:I.customDepthMaterial;if(G!==void 0)C=G;else if(C=H.isPointLight===!0?m:d,r.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const ot=C.uuid,lt=P.uuid;let mt=p[ot];mt===void 0&&(mt={},p[ot]=mt);let gt=mt[lt];gt===void 0&&(gt=C.clone(),mt[lt]=gt,P.addEventListener("dispose",V)),C=gt}if(C.visible=P.visible,C.wireframe=P.wireframe,D===Ea?C.side=P.shadowSide!==null?P.shadowSide:P.side:C.side=P.shadowSide!==null?P.shadowSide:_[P.side],C.alphaMap=P.alphaMap,C.alphaTest=P.alphaTest,C.map=P.map,C.clipShadows=P.clipShadows,C.clippingPlanes=P.clippingPlanes,C.clipIntersection=P.clipIntersection,C.displacementMap=P.displacementMap,C.displacementScale=P.displacementScale,C.displacementBias=P.displacementBias,C.wireframeLinewidth=P.wireframeLinewidth,C.linewidth=P.linewidth,H.isPointLight===!0&&C.isMeshDistanceMaterial===!0){const ot=r.properties.get(C);ot.light=H}return C}function T(I,P,H,D,C){if(I.visible===!1)return;if(I.layers.test(P.layers)&&(I.isMesh||I.isLine||I.isPoints)&&(I.castShadow||I.receiveShadow&&C===Ea)&&(!I.frustumCulled||s.intersectsObject(I))){I.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,I.matrixWorld);const lt=t.update(I),mt=I.material;if(Array.isArray(mt)){const gt=lt.groups;for(let B=0,$=gt.length;B<$;B++){const J=gt[B],Et=mt[J.materialIndex];if(Et&&Et.visible){const At=U(I,Et,D,C);I.onBeforeShadow(r,I,P,H,lt,At,J),r.renderBufferDirect(H,null,lt,At,I,J),I.onAfterShadow(r,I,P,H,lt,At,J)}}}else if(mt.visible){const gt=U(I,mt,D,C);I.onBeforeShadow(r,I,P,H,lt,gt,null),r.renderBufferDirect(H,null,lt,gt,I,null),I.onAfterShadow(r,I,P,H,lt,gt,null)}}const ot=I.children;for(let lt=0,mt=ot.length;lt<mt;lt++)T(ot[lt],P,H,D,C)}function V(I){I.target.removeEventListener("dispose",V);for(const H in p){const D=p[H],C=I.target.uuid;C in D&&(D[C].dispose(),delete D[C])}}}const iC={[up]:fp,[hp]:mp,[dp]:gp,[Co]:pp,[fp]:up,[mp]:hp,[gp]:dp,[pp]:Co};function aC(r,t){function i(){let q=!1;const Ct=new qe;let ut=null;const yt=new qe(0,0,0,0);return{setMask:function(wt){ut!==wt&&!q&&(r.colorMask(wt,wt,wt,wt),ut=wt)},setLocked:function(wt){q=wt},setClear:function(wt,Ut,ne,tn,_n){_n===!0&&(wt*=tn,Ut*=tn,ne*=tn),Ct.set(wt,Ut,ne,tn),yt.equals(Ct)===!1&&(r.clearColor(wt,Ut,ne,tn),yt.copy(Ct))},reset:function(){q=!1,ut=null,yt.set(-1,0,0,0)}}}function s(){let q=!1,Ct=!1,ut=null,yt=null,wt=null;return{setReversed:function(Ut){if(Ct!==Ut){const ne=t.get("EXT_clip_control");Ct?ne.clipControlEXT(ne.LOWER_LEFT_EXT,ne.ZERO_TO_ONE_EXT):ne.clipControlEXT(ne.LOWER_LEFT_EXT,ne.NEGATIVE_ONE_TO_ONE_EXT);const tn=wt;wt=null,this.setClear(tn)}Ct=Ut},getReversed:function(){return Ct},setTest:function(Ut){Ut?St(r.DEPTH_TEST):kt(r.DEPTH_TEST)},setMask:function(Ut){ut!==Ut&&!q&&(r.depthMask(Ut),ut=Ut)},setFunc:function(Ut){if(Ct&&(Ut=iC[Ut]),yt!==Ut){switch(Ut){case up:r.depthFunc(r.NEVER);break;case fp:r.depthFunc(r.ALWAYS);break;case hp:r.depthFunc(r.LESS);break;case Co:r.depthFunc(r.LEQUAL);break;case dp:r.depthFunc(r.EQUAL);break;case pp:r.depthFunc(r.GEQUAL);break;case mp:r.depthFunc(r.GREATER);break;case gp:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}yt=Ut}},setLocked:function(Ut){q=Ut},setClear:function(Ut){wt!==Ut&&(Ct&&(Ut=1-Ut),r.clearDepth(Ut),wt=Ut)},reset:function(){q=!1,ut=null,yt=null,wt=null,Ct=!1}}}function l(){let q=!1,Ct=null,ut=null,yt=null,wt=null,Ut=null,ne=null,tn=null,_n=null;return{setTest:function(Re){q||(Re?St(r.STENCIL_TEST):kt(r.STENCIL_TEST))},setMask:function(Re){Ct!==Re&&!q&&(r.stencilMask(Re),Ct=Re)},setFunc:function(Re,An,Ci){(ut!==Re||yt!==An||wt!==Ci)&&(r.stencilFunc(Re,An,Ci),ut=Re,yt=An,wt=Ci)},setOp:function(Re,An,Ci){(Ut!==Re||ne!==An||tn!==Ci)&&(r.stencilOp(Re,An,Ci),Ut=Re,ne=An,tn=Ci)},setLocked:function(Re){q=Re},setClear:function(Re){_n!==Re&&(r.clearStencil(Re),_n=Re)},reset:function(){q=!1,Ct=null,ut=null,yt=null,wt=null,Ut=null,ne=null,tn=null,_n=null}}}const c=new i,h=new s,d=new l,m=new WeakMap,p=new WeakMap;let g={},_={},x=new WeakMap,S=[],E=null,b=!1,M=null,v=null,L=null,U=null,T=null,V=null,I=null,P=new Oe(0,0,0),H=0,D=!1,C=null,G=null,ot=null,lt=null,mt=null;const gt=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let B=!1,$=0;const J=r.getParameter(r.VERSION);J.indexOf("WebGL")!==-1?($=parseFloat(/^WebGL (\d)/.exec(J)[1]),B=$>=1):J.indexOf("OpenGL ES")!==-1&&($=parseFloat(/^OpenGL ES (\d)/.exec(J)[1]),B=$>=2);let Et=null,At={};const z=r.getParameter(r.SCISSOR_BOX),at=r.getParameter(r.VIEWPORT),Mt=new qe().fromArray(z),K=new qe().fromArray(at);function ft(q,Ct,ut,yt){const wt=new Uint8Array(4),Ut=r.createTexture();r.bindTexture(q,Ut),r.texParameteri(q,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(q,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let ne=0;ne<ut;ne++)q===r.TEXTURE_3D||q===r.TEXTURE_2D_ARRAY?r.texImage3D(Ct,0,r.RGBA,1,1,yt,0,r.RGBA,r.UNSIGNED_BYTE,wt):r.texImage2D(Ct+ne,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,wt);return Ut}const Tt={};Tt[r.TEXTURE_2D]=ft(r.TEXTURE_2D,r.TEXTURE_2D,1),Tt[r.TEXTURE_CUBE_MAP]=ft(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Tt[r.TEXTURE_2D_ARRAY]=ft(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Tt[r.TEXTURE_3D]=ft(r.TEXTURE_3D,r.TEXTURE_3D,1,1),c.setClear(0,0,0,1),h.setClear(1),d.setClear(0),St(r.DEPTH_TEST),h.setFunc(Co),he(!1),ve(_v),St(r.CULL_FACE),k(vs);function St(q){g[q]!==!0&&(r.enable(q),g[q]=!0)}function kt(q){g[q]!==!1&&(r.disable(q),g[q]=!1)}function Gt(q,Ct){return _[q]!==Ct?(r.bindFramebuffer(q,Ct),_[q]=Ct,q===r.DRAW_FRAMEBUFFER&&(_[r.FRAMEBUFFER]=Ct),q===r.FRAMEBUFFER&&(_[r.DRAW_FRAMEBUFFER]=Ct),!0):!1}function se(q,Ct){let ut=S,yt=!1;if(q){ut=x.get(Ct),ut===void 0&&(ut=[],x.set(Ct,ut));const wt=q.textures;if(ut.length!==wt.length||ut[0]!==r.COLOR_ATTACHMENT0){for(let Ut=0,ne=wt.length;Ut<ne;Ut++)ut[Ut]=r.COLOR_ATTACHMENT0+Ut;ut.length=wt.length,yt=!0}}else ut[0]!==r.BACK&&(ut[0]=r.BACK,yt=!0);yt&&r.drawBuffers(ut)}function He(q){return E!==q?(r.useProgram(q),E=q,!0):!1}const de={[Zs]:r.FUNC_ADD,[c1]:r.FUNC_SUBTRACT,[u1]:r.FUNC_REVERSE_SUBTRACT};de[f1]=r.MIN,de[h1]=r.MAX;const $e={[d1]:r.ZERO,[p1]:r.ONE,[m1]:r.SRC_COLOR,[lp]:r.SRC_ALPHA,[S1]:r.SRC_ALPHA_SATURATE,[y1]:r.DST_COLOR,[_1]:r.DST_ALPHA,[g1]:r.ONE_MINUS_SRC_COLOR,[cp]:r.ONE_MINUS_SRC_ALPHA,[x1]:r.ONE_MINUS_DST_COLOR,[v1]:r.ONE_MINUS_DST_ALPHA,[M1]:r.CONSTANT_COLOR,[E1]:r.ONE_MINUS_CONSTANT_COLOR,[b1]:r.CONSTANT_ALPHA,[T1]:r.ONE_MINUS_CONSTANT_ALPHA};function k(q,Ct,ut,yt,wt,Ut,ne,tn,_n,Re){if(q===vs){b===!0&&(kt(r.BLEND),b=!1);return}if(b===!1&&(St(r.BLEND),b=!0),q!==l1){if(q!==M||Re!==D){if((v!==Zs||T!==Zs)&&(r.blendEquation(r.FUNC_ADD),v=Zs,T=Zs),Re)switch(q){case fo:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case vv:r.blendFunc(r.ONE,r.ONE);break;case yv:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case xv:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",q);break}else switch(q){case fo:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case vv:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case yv:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case xv:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",q);break}L=null,U=null,V=null,I=null,P.set(0,0,0),H=0,M=q,D=Re}return}wt=wt||Ct,Ut=Ut||ut,ne=ne||yt,(Ct!==v||wt!==T)&&(r.blendEquationSeparate(de[Ct],de[wt]),v=Ct,T=wt),(ut!==L||yt!==U||Ut!==V||ne!==I)&&(r.blendFuncSeparate($e[ut],$e[yt],$e[Ut],$e[ne]),L=ut,U=yt,V=Ut,I=ne),(tn.equals(P)===!1||_n!==H)&&(r.blendColor(tn.r,tn.g,tn.b,_n),P.copy(tn),H=_n),M=q,D=!1}function On(q,Ct){q.side===Aa?kt(r.CULL_FACE):St(r.CULL_FACE);let ut=q.side===ei;Ct&&(ut=!ut),he(ut),q.blending===fo&&q.transparent===!1?k(vs):k(q.blending,q.blendEquation,q.blendSrc,q.blendDst,q.blendEquationAlpha,q.blendSrcAlpha,q.blendDstAlpha,q.blendColor,q.blendAlpha,q.premultipliedAlpha),h.setFunc(q.depthFunc),h.setTest(q.depthTest),h.setMask(q.depthWrite),c.setMask(q.colorWrite);const yt=q.stencilWrite;d.setTest(yt),yt&&(d.setMask(q.stencilWriteMask),d.setFunc(q.stencilFunc,q.stencilRef,q.stencilFuncMask),d.setOp(q.stencilFail,q.stencilZFail,q.stencilZPass)),Ie(q.polygonOffset,q.polygonOffsetFactor,q.polygonOffsetUnits),q.alphaToCoverage===!0?St(r.SAMPLE_ALPHA_TO_COVERAGE):kt(r.SAMPLE_ALPHA_TO_COVERAGE)}function he(q){C!==q&&(q?r.frontFace(r.CW):r.frontFace(r.CCW),C=q)}function ve(q){q!==s1?(St(r.CULL_FACE),q!==G&&(q===_v?r.cullFace(r.BACK):q===r1?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):kt(r.CULL_FACE),G=q}function Yt(q){q!==ot&&(B&&r.lineWidth(q),ot=q)}function Ie(q,Ct,ut){q?(St(r.POLYGON_OFFSET_FILL),(lt!==Ct||mt!==ut)&&(r.polygonOffset(Ct,ut),lt=Ct,mt=ut)):kt(r.POLYGON_OFFSET_FILL)}function Wt(q){q?St(r.SCISSOR_TEST):kt(r.SCISSOR_TEST)}function O(q){q===void 0&&(q=r.TEXTURE0+gt-1),Et!==q&&(r.activeTexture(q),Et=q)}function R(q,Ct,ut){ut===void 0&&(Et===null?ut=r.TEXTURE0+gt-1:ut=Et);let yt=At[ut];yt===void 0&&(yt={type:void 0,texture:void 0},At[ut]=yt),(yt.type!==q||yt.texture!==Ct)&&(Et!==ut&&(r.activeTexture(ut),Et=ut),r.bindTexture(q,Ct||Tt[q]),yt.type=q,yt.texture=Ct)}function it(){const q=At[Et];q!==void 0&&q.type!==void 0&&(r.bindTexture(q.type,null),q.type=void 0,q.texture=void 0)}function dt(){try{r.compressedTexImage2D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function bt(){try{r.compressedTexImage3D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function _t(){try{r.texSubImage2D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function jt(){try{r.texSubImage3D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function Dt(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function Bt(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function ye(){try{r.texStorage2D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function Rt(){try{r.texStorage3D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function Ft(){try{r.texImage2D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function Qt(){try{r.texImage3D.apply(r,arguments)}catch(q){console.error("THREE.WebGLState:",q)}}function qt(q){Mt.equals(q)===!1&&(r.scissor(q.x,q.y,q.z,q.w),Mt.copy(q))}function Ot(q){K.equals(q)===!1&&(r.viewport(q.x,q.y,q.z,q.w),K.copy(q))}function ee(q,Ct){let ut=p.get(Ct);ut===void 0&&(ut=new WeakMap,p.set(Ct,ut));let yt=ut.get(q);yt===void 0&&(yt=r.getUniformBlockIndex(Ct,q.name),ut.set(q,yt))}function re(q,Ct){const yt=p.get(Ct).get(q);m.get(Ct)!==yt&&(r.uniformBlockBinding(Ct,yt,q.__bindingPointIndex),m.set(Ct,yt))}function Ge(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),h.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),g={},Et=null,At={},_={},x=new WeakMap,S=[],E=null,b=!1,M=null,v=null,L=null,U=null,T=null,V=null,I=null,P=new Oe(0,0,0),H=0,D=!1,C=null,G=null,ot=null,lt=null,mt=null,Mt.set(0,0,r.canvas.width,r.canvas.height),K.set(0,0,r.canvas.width,r.canvas.height),c.reset(),h.reset(),d.reset()}return{buffers:{color:c,depth:h,stencil:d},enable:St,disable:kt,bindFramebuffer:Gt,drawBuffers:se,useProgram:He,setBlending:k,setMaterial:On,setFlipSided:he,setCullFace:ve,setLineWidth:Yt,setPolygonOffset:Ie,setScissorTest:Wt,activeTexture:O,bindTexture:R,unbindTexture:it,compressedTexImage2D:dt,compressedTexImage3D:bt,texImage2D:Ft,texImage3D:Qt,updateUBOMapping:ee,uniformBlockBinding:re,texStorage2D:ye,texStorage3D:Rt,texSubImage2D:_t,texSubImage3D:jt,compressedTexSubImage2D:Dt,compressedTexSubImage3D:Bt,scissor:qt,viewport:Ot,reset:Ge}}function sC(r,t,i,s,l,c,h){const d=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,m=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),p=new Ae,g=new WeakMap;let _;const x=new WeakMap;let S=!1;try{S=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function E(O,R){return S?new OffscreenCanvas(O,R):Yu("canvas")}function b(O,R,it){let dt=1;const bt=Wt(O);if((bt.width>it||bt.height>it)&&(dt=it/Math.max(bt.width,bt.height)),dt<1)if(typeof HTMLImageElement<"u"&&O instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&O instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&O instanceof ImageBitmap||typeof VideoFrame<"u"&&O instanceof VideoFrame){const _t=Math.floor(dt*bt.width),jt=Math.floor(dt*bt.height);_===void 0&&(_=E(_t,jt));const Dt=R?E(_t,jt):_;return Dt.width=_t,Dt.height=jt,Dt.getContext("2d").drawImage(O,0,0,_t,jt),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+bt.width+"x"+bt.height+") to ("+_t+"x"+jt+")."),Dt}else return"data"in O&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+bt.width+"x"+bt.height+")."),O;return O}function M(O){return O.generateMipmaps}function v(O){r.generateMipmap(O)}function L(O){return O.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:O.isWebGL3DRenderTarget?r.TEXTURE_3D:O.isWebGLArrayRenderTarget||O.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function U(O,R,it,dt,bt=!1){if(O!==null){if(r[O]!==void 0)return r[O];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+O+"'")}let _t=R;if(R===r.RED&&(it===r.FLOAT&&(_t=r.R32F),it===r.HALF_FLOAT&&(_t=r.R16F),it===r.UNSIGNED_BYTE&&(_t=r.R8)),R===r.RED_INTEGER&&(it===r.UNSIGNED_BYTE&&(_t=r.R8UI),it===r.UNSIGNED_SHORT&&(_t=r.R16UI),it===r.UNSIGNED_INT&&(_t=r.R32UI),it===r.BYTE&&(_t=r.R8I),it===r.SHORT&&(_t=r.R16I),it===r.INT&&(_t=r.R32I)),R===r.RG&&(it===r.FLOAT&&(_t=r.RG32F),it===r.HALF_FLOAT&&(_t=r.RG16F),it===r.UNSIGNED_BYTE&&(_t=r.RG8)),R===r.RG_INTEGER&&(it===r.UNSIGNED_BYTE&&(_t=r.RG8UI),it===r.UNSIGNED_SHORT&&(_t=r.RG16UI),it===r.UNSIGNED_INT&&(_t=r.RG32UI),it===r.BYTE&&(_t=r.RG8I),it===r.SHORT&&(_t=r.RG16I),it===r.INT&&(_t=r.RG32I)),R===r.RGB_INTEGER&&(it===r.UNSIGNED_BYTE&&(_t=r.RGB8UI),it===r.UNSIGNED_SHORT&&(_t=r.RGB16UI),it===r.UNSIGNED_INT&&(_t=r.RGB32UI),it===r.BYTE&&(_t=r.RGB8I),it===r.SHORT&&(_t=r.RGB16I),it===r.INT&&(_t=r.RGB32I)),R===r.RGBA_INTEGER&&(it===r.UNSIGNED_BYTE&&(_t=r.RGBA8UI),it===r.UNSIGNED_SHORT&&(_t=r.RGBA16UI),it===r.UNSIGNED_INT&&(_t=r.RGBA32UI),it===r.BYTE&&(_t=r.RGBA8I),it===r.SHORT&&(_t=r.RGBA16I),it===r.INT&&(_t=r.RGBA32I)),R===r.RGB&&it===r.UNSIGNED_INT_5_9_9_9_REV&&(_t=r.RGB9_E5),R===r.RGBA){const jt=bt?qu:Ne.getTransfer(dt);it===r.FLOAT&&(_t=r.RGBA32F),it===r.HALF_FLOAT&&(_t=r.RGBA16F),it===r.UNSIGNED_BYTE&&(_t=jt===je?r.SRGB8_ALPHA8:r.RGBA8),it===r.UNSIGNED_SHORT_4_4_4_4&&(_t=r.RGBA4),it===r.UNSIGNED_SHORT_5_5_5_1&&(_t=r.RGB5_A1)}return(_t===r.R16F||_t===r.R32F||_t===r.RG16F||_t===r.RG32F||_t===r.RGBA16F||_t===r.RGBA32F)&&t.get("EXT_color_buffer_float"),_t}function T(O,R){let it;return O?R===null||R===hr||R===Uo?it=r.DEPTH24_STENCIL8:R===Ra?it=r.DEPTH32F_STENCIL8:R===kl&&(it=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):R===null||R===hr||R===Uo?it=r.DEPTH_COMPONENT24:R===Ra?it=r.DEPTH_COMPONENT32F:R===kl&&(it=r.DEPTH_COMPONENT16),it}function V(O,R){return M(O)===!0||O.isFramebufferTexture&&O.minFilter!==Fi&&O.minFilter!==Zi?Math.log2(Math.max(R.width,R.height))+1:O.mipmaps!==void 0&&O.mipmaps.length>0?O.mipmaps.length:O.isCompressedTexture&&Array.isArray(O.image)?R.mipmaps.length:1}function I(O){const R=O.target;R.removeEventListener("dispose",I),H(R),R.isVideoTexture&&g.delete(R)}function P(O){const R=O.target;R.removeEventListener("dispose",P),C(R)}function H(O){const R=s.get(O);if(R.__webglInit===void 0)return;const it=O.source,dt=x.get(it);if(dt){const bt=dt[R.__cacheKey];bt.usedTimes--,bt.usedTimes===0&&D(O),Object.keys(dt).length===0&&x.delete(it)}s.remove(O)}function D(O){const R=s.get(O);r.deleteTexture(R.__webglTexture);const it=O.source,dt=x.get(it);delete dt[R.__cacheKey],h.memory.textures--}function C(O){const R=s.get(O);if(O.depthTexture&&(O.depthTexture.dispose(),s.remove(O.depthTexture)),O.isWebGLCubeRenderTarget)for(let dt=0;dt<6;dt++){if(Array.isArray(R.__webglFramebuffer[dt]))for(let bt=0;bt<R.__webglFramebuffer[dt].length;bt++)r.deleteFramebuffer(R.__webglFramebuffer[dt][bt]);else r.deleteFramebuffer(R.__webglFramebuffer[dt]);R.__webglDepthbuffer&&r.deleteRenderbuffer(R.__webglDepthbuffer[dt])}else{if(Array.isArray(R.__webglFramebuffer))for(let dt=0;dt<R.__webglFramebuffer.length;dt++)r.deleteFramebuffer(R.__webglFramebuffer[dt]);else r.deleteFramebuffer(R.__webglFramebuffer);if(R.__webglDepthbuffer&&r.deleteRenderbuffer(R.__webglDepthbuffer),R.__webglMultisampledFramebuffer&&r.deleteFramebuffer(R.__webglMultisampledFramebuffer),R.__webglColorRenderbuffer)for(let dt=0;dt<R.__webglColorRenderbuffer.length;dt++)R.__webglColorRenderbuffer[dt]&&r.deleteRenderbuffer(R.__webglColorRenderbuffer[dt]);R.__webglDepthRenderbuffer&&r.deleteRenderbuffer(R.__webglDepthRenderbuffer)}const it=O.textures;for(let dt=0,bt=it.length;dt<bt;dt++){const _t=s.get(it[dt]);_t.__webglTexture&&(r.deleteTexture(_t.__webglTexture),h.memory.textures--),s.remove(it[dt])}s.remove(O)}let G=0;function ot(){G=0}function lt(){const O=G;return O>=l.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+O+" texture units while this GPU supports only "+l.maxTextures),G+=1,O}function mt(O){const R=[];return R.push(O.wrapS),R.push(O.wrapT),R.push(O.wrapR||0),R.push(O.magFilter),R.push(O.minFilter),R.push(O.anisotropy),R.push(O.internalFormat),R.push(O.format),R.push(O.type),R.push(O.generateMipmaps),R.push(O.premultiplyAlpha),R.push(O.flipY),R.push(O.unpackAlignment),R.push(O.colorSpace),R.join()}function gt(O,R){const it=s.get(O);if(O.isVideoTexture&&Yt(O),O.isRenderTargetTexture===!1&&O.version>0&&it.__version!==O.version){const dt=O.image;if(dt===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(dt.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{K(it,O,R);return}}i.bindTexture(r.TEXTURE_2D,it.__webglTexture,r.TEXTURE0+R)}function B(O,R){const it=s.get(O);if(O.version>0&&it.__version!==O.version){K(it,O,R);return}i.bindTexture(r.TEXTURE_2D_ARRAY,it.__webglTexture,r.TEXTURE0+R)}function $(O,R){const it=s.get(O);if(O.version>0&&it.__version!==O.version){K(it,O,R);return}i.bindTexture(r.TEXTURE_3D,it.__webglTexture,r.TEXTURE0+R)}function J(O,R){const it=s.get(O);if(O.version>0&&it.__version!==O.version){ft(it,O,R);return}i.bindTexture(r.TEXTURE_CUBE_MAP,it.__webglTexture,r.TEXTURE0+R)}const Et={[yp]:r.REPEAT,[tr]:r.CLAMP_TO_EDGE,[xp]:r.MIRRORED_REPEAT},At={[Fi]:r.NEAREST,[P1]:r.NEAREST_MIPMAP_NEAREST,[pu]:r.NEAREST_MIPMAP_LINEAR,[Zi]:r.LINEAR,[md]:r.LINEAR_MIPMAP_NEAREST,[er]:r.LINEAR_MIPMAP_LINEAR},z={[H1]:r.NEVER,[q1]:r.ALWAYS,[G1]:r.LESS,[ux]:r.LEQUAL,[V1]:r.EQUAL,[j1]:r.GEQUAL,[k1]:r.GREATER,[X1]:r.NOTEQUAL};function at(O,R){if(R.type===Ra&&t.has("OES_texture_float_linear")===!1&&(R.magFilter===Zi||R.magFilter===md||R.magFilter===pu||R.magFilter===er||R.minFilter===Zi||R.minFilter===md||R.minFilter===pu||R.minFilter===er)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(O,r.TEXTURE_WRAP_S,Et[R.wrapS]),r.texParameteri(O,r.TEXTURE_WRAP_T,Et[R.wrapT]),(O===r.TEXTURE_3D||O===r.TEXTURE_2D_ARRAY)&&r.texParameteri(O,r.TEXTURE_WRAP_R,Et[R.wrapR]),r.texParameteri(O,r.TEXTURE_MAG_FILTER,At[R.magFilter]),r.texParameteri(O,r.TEXTURE_MIN_FILTER,At[R.minFilter]),R.compareFunction&&(r.texParameteri(O,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(O,r.TEXTURE_COMPARE_FUNC,z[R.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(R.magFilter===Fi||R.minFilter!==pu&&R.minFilter!==er||R.type===Ra&&t.has("OES_texture_float_linear")===!1)return;if(R.anisotropy>1||s.get(R).__currentAnisotropy){const it=t.get("EXT_texture_filter_anisotropic");r.texParameterf(O,it.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(R.anisotropy,l.getMaxAnisotropy())),s.get(R).__currentAnisotropy=R.anisotropy}}}function Mt(O,R){let it=!1;O.__webglInit===void 0&&(O.__webglInit=!0,R.addEventListener("dispose",I));const dt=R.source;let bt=x.get(dt);bt===void 0&&(bt={},x.set(dt,bt));const _t=mt(R);if(_t!==O.__cacheKey){bt[_t]===void 0&&(bt[_t]={texture:r.createTexture(),usedTimes:0},h.memory.textures++,it=!0),bt[_t].usedTimes++;const jt=bt[O.__cacheKey];jt!==void 0&&(bt[O.__cacheKey].usedTimes--,jt.usedTimes===0&&D(R)),O.__cacheKey=_t,O.__webglTexture=bt[_t].texture}return it}function K(O,R,it){let dt=r.TEXTURE_2D;(R.isDataArrayTexture||R.isCompressedArrayTexture)&&(dt=r.TEXTURE_2D_ARRAY),R.isData3DTexture&&(dt=r.TEXTURE_3D);const bt=Mt(O,R),_t=R.source;i.bindTexture(dt,O.__webglTexture,r.TEXTURE0+it);const jt=s.get(_t);if(_t.version!==jt.__version||bt===!0){i.activeTexture(r.TEXTURE0+it);const Dt=Ne.getPrimaries(Ne.workingColorSpace),Bt=R.colorSpace===ls?null:Ne.getPrimaries(R.colorSpace),ye=R.colorSpace===ls||Dt===Bt?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,R.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,R.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,R.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,ye);let Rt=b(R.image,!1,l.maxTextureSize);Rt=Ie(R,Rt);const Ft=c.convert(R.format,R.colorSpace),Qt=c.convert(R.type);let qt=U(R.internalFormat,Ft,Qt,R.colorSpace,R.isVideoTexture);at(dt,R);let Ot;const ee=R.mipmaps,re=R.isVideoTexture!==!0,Ge=jt.__version===void 0||bt===!0,q=_t.dataReady,Ct=V(R,Rt);if(R.isDepthTexture)qt=T(R.format===No,R.type),Ge&&(re?i.texStorage2D(r.TEXTURE_2D,1,qt,Rt.width,Rt.height):i.texImage2D(r.TEXTURE_2D,0,qt,Rt.width,Rt.height,0,Ft,Qt,null));else if(R.isDataTexture)if(ee.length>0){re&&Ge&&i.texStorage2D(r.TEXTURE_2D,Ct,qt,ee[0].width,ee[0].height);for(let ut=0,yt=ee.length;ut<yt;ut++)Ot=ee[ut],re?q&&i.texSubImage2D(r.TEXTURE_2D,ut,0,0,Ot.width,Ot.height,Ft,Qt,Ot.data):i.texImage2D(r.TEXTURE_2D,ut,qt,Ot.width,Ot.height,0,Ft,Qt,Ot.data);R.generateMipmaps=!1}else re?(Ge&&i.texStorage2D(r.TEXTURE_2D,Ct,qt,Rt.width,Rt.height),q&&i.texSubImage2D(r.TEXTURE_2D,0,0,0,Rt.width,Rt.height,Ft,Qt,Rt.data)):i.texImage2D(r.TEXTURE_2D,0,qt,Rt.width,Rt.height,0,Ft,Qt,Rt.data);else if(R.isCompressedTexture)if(R.isCompressedArrayTexture){re&&Ge&&i.texStorage3D(r.TEXTURE_2D_ARRAY,Ct,qt,ee[0].width,ee[0].height,Rt.depth);for(let ut=0,yt=ee.length;ut<yt;ut++)if(Ot=ee[ut],R.format!==Bi)if(Ft!==null)if(re){if(q)if(R.layerUpdates.size>0){const wt=Wv(Ot.width,Ot.height,R.format,R.type);for(const Ut of R.layerUpdates){const ne=Ot.data.subarray(Ut*wt/Ot.data.BYTES_PER_ELEMENT,(Ut+1)*wt/Ot.data.BYTES_PER_ELEMENT);i.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ut,0,0,Ut,Ot.width,Ot.height,1,Ft,ne)}R.clearLayerUpdates()}else i.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ut,0,0,0,Ot.width,Ot.height,Rt.depth,Ft,Ot.data)}else i.compressedTexImage3D(r.TEXTURE_2D_ARRAY,ut,qt,Ot.width,Ot.height,Rt.depth,0,Ot.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else re?q&&i.texSubImage3D(r.TEXTURE_2D_ARRAY,ut,0,0,0,Ot.width,Ot.height,Rt.depth,Ft,Qt,Ot.data):i.texImage3D(r.TEXTURE_2D_ARRAY,ut,qt,Ot.width,Ot.height,Rt.depth,0,Ft,Qt,Ot.data)}else{re&&Ge&&i.texStorage2D(r.TEXTURE_2D,Ct,qt,ee[0].width,ee[0].height);for(let ut=0,yt=ee.length;ut<yt;ut++)Ot=ee[ut],R.format!==Bi?Ft!==null?re?q&&i.compressedTexSubImage2D(r.TEXTURE_2D,ut,0,0,Ot.width,Ot.height,Ft,Ot.data):i.compressedTexImage2D(r.TEXTURE_2D,ut,qt,Ot.width,Ot.height,0,Ot.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):re?q&&i.texSubImage2D(r.TEXTURE_2D,ut,0,0,Ot.width,Ot.height,Ft,Qt,Ot.data):i.texImage2D(r.TEXTURE_2D,ut,qt,Ot.width,Ot.height,0,Ft,Qt,Ot.data)}else if(R.isDataArrayTexture)if(re){if(Ge&&i.texStorage3D(r.TEXTURE_2D_ARRAY,Ct,qt,Rt.width,Rt.height,Rt.depth),q)if(R.layerUpdates.size>0){const ut=Wv(Rt.width,Rt.height,R.format,R.type);for(const yt of R.layerUpdates){const wt=Rt.data.subarray(yt*ut/Rt.data.BYTES_PER_ELEMENT,(yt+1)*ut/Rt.data.BYTES_PER_ELEMENT);i.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,yt,Rt.width,Rt.height,1,Ft,Qt,wt)}R.clearLayerUpdates()}else i.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,Rt.width,Rt.height,Rt.depth,Ft,Qt,Rt.data)}else i.texImage3D(r.TEXTURE_2D_ARRAY,0,qt,Rt.width,Rt.height,Rt.depth,0,Ft,Qt,Rt.data);else if(R.isData3DTexture)re?(Ge&&i.texStorage3D(r.TEXTURE_3D,Ct,qt,Rt.width,Rt.height,Rt.depth),q&&i.texSubImage3D(r.TEXTURE_3D,0,0,0,0,Rt.width,Rt.height,Rt.depth,Ft,Qt,Rt.data)):i.texImage3D(r.TEXTURE_3D,0,qt,Rt.width,Rt.height,Rt.depth,0,Ft,Qt,Rt.data);else if(R.isFramebufferTexture){if(Ge)if(re)i.texStorage2D(r.TEXTURE_2D,Ct,qt,Rt.width,Rt.height);else{let ut=Rt.width,yt=Rt.height;for(let wt=0;wt<Ct;wt++)i.texImage2D(r.TEXTURE_2D,wt,qt,ut,yt,0,Ft,Qt,null),ut>>=1,yt>>=1}}else if(ee.length>0){if(re&&Ge){const ut=Wt(ee[0]);i.texStorage2D(r.TEXTURE_2D,Ct,qt,ut.width,ut.height)}for(let ut=0,yt=ee.length;ut<yt;ut++)Ot=ee[ut],re?q&&i.texSubImage2D(r.TEXTURE_2D,ut,0,0,Ft,Qt,Ot):i.texImage2D(r.TEXTURE_2D,ut,qt,Ft,Qt,Ot);R.generateMipmaps=!1}else if(re){if(Ge){const ut=Wt(Rt);i.texStorage2D(r.TEXTURE_2D,Ct,qt,ut.width,ut.height)}q&&i.texSubImage2D(r.TEXTURE_2D,0,0,0,Ft,Qt,Rt)}else i.texImage2D(r.TEXTURE_2D,0,qt,Ft,Qt,Rt);M(R)&&v(dt),jt.__version=_t.version,R.onUpdate&&R.onUpdate(R)}O.__version=R.version}function ft(O,R,it){if(R.image.length!==6)return;const dt=Mt(O,R),bt=R.source;i.bindTexture(r.TEXTURE_CUBE_MAP,O.__webglTexture,r.TEXTURE0+it);const _t=s.get(bt);if(bt.version!==_t.__version||dt===!0){i.activeTexture(r.TEXTURE0+it);const jt=Ne.getPrimaries(Ne.workingColorSpace),Dt=R.colorSpace===ls?null:Ne.getPrimaries(R.colorSpace),Bt=R.colorSpace===ls||jt===Dt?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,R.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,R.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,R.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Bt);const ye=R.isCompressedTexture||R.image[0].isCompressedTexture,Rt=R.image[0]&&R.image[0].isDataTexture,Ft=[];for(let yt=0;yt<6;yt++)!ye&&!Rt?Ft[yt]=b(R.image[yt],!0,l.maxCubemapSize):Ft[yt]=Rt?R.image[yt].image:R.image[yt],Ft[yt]=Ie(R,Ft[yt]);const Qt=Ft[0],qt=c.convert(R.format,R.colorSpace),Ot=c.convert(R.type),ee=U(R.internalFormat,qt,Ot,R.colorSpace),re=R.isVideoTexture!==!0,Ge=_t.__version===void 0||dt===!0,q=bt.dataReady;let Ct=V(R,Qt);at(r.TEXTURE_CUBE_MAP,R);let ut;if(ye){re&&Ge&&i.texStorage2D(r.TEXTURE_CUBE_MAP,Ct,ee,Qt.width,Qt.height);for(let yt=0;yt<6;yt++){ut=Ft[yt].mipmaps;for(let wt=0;wt<ut.length;wt++){const Ut=ut[wt];R.format!==Bi?qt!==null?re?q&&i.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Ut.width,Ut.height,qt,Ut.data):i.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ee,Ut.width,Ut.height,0,Ut.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):re?q&&i.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Ut.width,Ut.height,qt,Ot,Ut.data):i.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ee,Ut.width,Ut.height,0,qt,Ot,Ut.data)}}}else{if(ut=R.mipmaps,re&&Ge){ut.length>0&&Ct++;const yt=Wt(Ft[0]);i.texStorage2D(r.TEXTURE_CUBE_MAP,Ct,ee,yt.width,yt.height)}for(let yt=0;yt<6;yt++)if(Rt){re?q&&i.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,Ft[yt].width,Ft[yt].height,qt,Ot,Ft[yt].data):i.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ee,Ft[yt].width,Ft[yt].height,0,qt,Ot,Ft[yt].data);for(let wt=0;wt<ut.length;wt++){const ne=ut[wt].image[yt].image;re?q&&i.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,ne.width,ne.height,qt,Ot,ne.data):i.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ee,ne.width,ne.height,0,qt,Ot,ne.data)}}else{re?q&&i.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,qt,Ot,Ft[yt]):i.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ee,qt,Ot,Ft[yt]);for(let wt=0;wt<ut.length;wt++){const Ut=ut[wt];re?q&&i.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,qt,Ot,Ut.image[yt]):i.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ee,qt,Ot,Ut.image[yt])}}}M(R)&&v(r.TEXTURE_CUBE_MAP),_t.__version=bt.version,R.onUpdate&&R.onUpdate(R)}O.__version=R.version}function Tt(O,R,it,dt,bt,_t){const jt=c.convert(it.format,it.colorSpace),Dt=c.convert(it.type),Bt=U(it.internalFormat,jt,Dt,it.colorSpace),ye=s.get(R),Rt=s.get(it);if(Rt.__renderTarget=R,!ye.__hasExternalTextures){const Ft=Math.max(1,R.width>>_t),Qt=Math.max(1,R.height>>_t);bt===r.TEXTURE_3D||bt===r.TEXTURE_2D_ARRAY?i.texImage3D(bt,_t,Bt,Ft,Qt,R.depth,0,jt,Dt,null):i.texImage2D(bt,_t,Bt,Ft,Qt,0,jt,Dt,null)}i.bindFramebuffer(r.FRAMEBUFFER,O),ve(R)?d.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,dt,bt,Rt.__webglTexture,0,he(R)):(bt===r.TEXTURE_2D||bt>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&bt<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,dt,bt,Rt.__webglTexture,_t),i.bindFramebuffer(r.FRAMEBUFFER,null)}function St(O,R,it){if(r.bindRenderbuffer(r.RENDERBUFFER,O),R.depthBuffer){const dt=R.depthTexture,bt=dt&&dt.isDepthTexture?dt.type:null,_t=T(R.stencilBuffer,bt),jt=R.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Dt=he(R);ve(R)?d.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Dt,_t,R.width,R.height):it?r.renderbufferStorageMultisample(r.RENDERBUFFER,Dt,_t,R.width,R.height):r.renderbufferStorage(r.RENDERBUFFER,_t,R.width,R.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,jt,r.RENDERBUFFER,O)}else{const dt=R.textures;for(let bt=0;bt<dt.length;bt++){const _t=dt[bt],jt=c.convert(_t.format,_t.colorSpace),Dt=c.convert(_t.type),Bt=U(_t.internalFormat,jt,Dt,_t.colorSpace),ye=he(R);it&&ve(R)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,ye,Bt,R.width,R.height):ve(R)?d.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,ye,Bt,R.width,R.height):r.renderbufferStorage(r.RENDERBUFFER,Bt,R.width,R.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function kt(O,R){if(R&&R.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(i.bindFramebuffer(r.FRAMEBUFFER,O),!(R.depthTexture&&R.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const dt=s.get(R.depthTexture);dt.__renderTarget=R,(!dt.__webglTexture||R.depthTexture.image.width!==R.width||R.depthTexture.image.height!==R.height)&&(R.depthTexture.image.width=R.width,R.depthTexture.image.height=R.height,R.depthTexture.needsUpdate=!0),gt(R.depthTexture,0);const bt=dt.__webglTexture,_t=he(R);if(R.depthTexture.format===ho)ve(R)?d.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,bt,0,_t):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,bt,0);else if(R.depthTexture.format===No)ve(R)?d.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,bt,0,_t):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,bt,0);else throw new Error("Unknown depthTexture format")}function Gt(O){const R=s.get(O),it=O.isWebGLCubeRenderTarget===!0;if(R.__boundDepthTexture!==O.depthTexture){const dt=O.depthTexture;if(R.__depthDisposeCallback&&R.__depthDisposeCallback(),dt){const bt=()=>{delete R.__boundDepthTexture,delete R.__depthDisposeCallback,dt.removeEventListener("dispose",bt)};dt.addEventListener("dispose",bt),R.__depthDisposeCallback=bt}R.__boundDepthTexture=dt}if(O.depthTexture&&!R.__autoAllocateDepthBuffer){if(it)throw new Error("target.depthTexture not supported in Cube render targets");kt(R.__webglFramebuffer,O)}else if(it){R.__webglDepthbuffer=[];for(let dt=0;dt<6;dt++)if(i.bindFramebuffer(r.FRAMEBUFFER,R.__webglFramebuffer[dt]),R.__webglDepthbuffer[dt]===void 0)R.__webglDepthbuffer[dt]=r.createRenderbuffer(),St(R.__webglDepthbuffer[dt],O,!1);else{const bt=O.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,_t=R.__webglDepthbuffer[dt];r.bindRenderbuffer(r.RENDERBUFFER,_t),r.framebufferRenderbuffer(r.FRAMEBUFFER,bt,r.RENDERBUFFER,_t)}}else if(i.bindFramebuffer(r.FRAMEBUFFER,R.__webglFramebuffer),R.__webglDepthbuffer===void 0)R.__webglDepthbuffer=r.createRenderbuffer(),St(R.__webglDepthbuffer,O,!1);else{const dt=O.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,bt=R.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,bt),r.framebufferRenderbuffer(r.FRAMEBUFFER,dt,r.RENDERBUFFER,bt)}i.bindFramebuffer(r.FRAMEBUFFER,null)}function se(O,R,it){const dt=s.get(O);R!==void 0&&Tt(dt.__webglFramebuffer,O,O.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),it!==void 0&&Gt(O)}function He(O){const R=O.texture,it=s.get(O),dt=s.get(R);O.addEventListener("dispose",P);const bt=O.textures,_t=O.isWebGLCubeRenderTarget===!0,jt=bt.length>1;if(jt||(dt.__webglTexture===void 0&&(dt.__webglTexture=r.createTexture()),dt.__version=R.version,h.memory.textures++),_t){it.__webglFramebuffer=[];for(let Dt=0;Dt<6;Dt++)if(R.mipmaps&&R.mipmaps.length>0){it.__webglFramebuffer[Dt]=[];for(let Bt=0;Bt<R.mipmaps.length;Bt++)it.__webglFramebuffer[Dt][Bt]=r.createFramebuffer()}else it.__webglFramebuffer[Dt]=r.createFramebuffer()}else{if(R.mipmaps&&R.mipmaps.length>0){it.__webglFramebuffer=[];for(let Dt=0;Dt<R.mipmaps.length;Dt++)it.__webglFramebuffer[Dt]=r.createFramebuffer()}else it.__webglFramebuffer=r.createFramebuffer();if(jt)for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const ye=s.get(bt[Dt]);ye.__webglTexture===void 0&&(ye.__webglTexture=r.createTexture(),h.memory.textures++)}if(O.samples>0&&ve(O)===!1){it.__webglMultisampledFramebuffer=r.createFramebuffer(),it.__webglColorRenderbuffer=[],i.bindFramebuffer(r.FRAMEBUFFER,it.__webglMultisampledFramebuffer);for(let Dt=0;Dt<bt.length;Dt++){const Bt=bt[Dt];it.__webglColorRenderbuffer[Dt]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,it.__webglColorRenderbuffer[Dt]);const ye=c.convert(Bt.format,Bt.colorSpace),Rt=c.convert(Bt.type),Ft=U(Bt.internalFormat,ye,Rt,Bt.colorSpace,O.isXRRenderTarget===!0),Qt=he(O);r.renderbufferStorageMultisample(r.RENDERBUFFER,Qt,Ft,O.width,O.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Dt,r.RENDERBUFFER,it.__webglColorRenderbuffer[Dt])}r.bindRenderbuffer(r.RENDERBUFFER,null),O.depthBuffer&&(it.__webglDepthRenderbuffer=r.createRenderbuffer(),St(it.__webglDepthRenderbuffer,O,!0)),i.bindFramebuffer(r.FRAMEBUFFER,null)}}if(_t){i.bindTexture(r.TEXTURE_CUBE_MAP,dt.__webglTexture),at(r.TEXTURE_CUBE_MAP,R);for(let Dt=0;Dt<6;Dt++)if(R.mipmaps&&R.mipmaps.length>0)for(let Bt=0;Bt<R.mipmaps.length;Bt++)Tt(it.__webglFramebuffer[Dt][Bt],O,R,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,Bt);else Tt(it.__webglFramebuffer[Dt],O,R,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,0);M(R)&&v(r.TEXTURE_CUBE_MAP),i.unbindTexture()}else if(jt){for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const ye=bt[Dt],Rt=s.get(ye);i.bindTexture(r.TEXTURE_2D,Rt.__webglTexture),at(r.TEXTURE_2D,ye),Tt(it.__webglFramebuffer,O,ye,r.COLOR_ATTACHMENT0+Dt,r.TEXTURE_2D,0),M(ye)&&v(r.TEXTURE_2D)}i.unbindTexture()}else{let Dt=r.TEXTURE_2D;if((O.isWebGL3DRenderTarget||O.isWebGLArrayRenderTarget)&&(Dt=O.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),i.bindTexture(Dt,dt.__webglTexture),at(Dt,R),R.mipmaps&&R.mipmaps.length>0)for(let Bt=0;Bt<R.mipmaps.length;Bt++)Tt(it.__webglFramebuffer[Bt],O,R,r.COLOR_ATTACHMENT0,Dt,Bt);else Tt(it.__webglFramebuffer,O,R,r.COLOR_ATTACHMENT0,Dt,0);M(R)&&v(Dt),i.unbindTexture()}O.depthBuffer&&Gt(O)}function de(O){const R=O.textures;for(let it=0,dt=R.length;it<dt;it++){const bt=R[it];if(M(bt)){const _t=L(O),jt=s.get(bt).__webglTexture;i.bindTexture(_t,jt),v(_t),i.unbindTexture()}}}const $e=[],k=[];function On(O){if(O.samples>0){if(ve(O)===!1){const R=O.textures,it=O.width,dt=O.height;let bt=r.COLOR_BUFFER_BIT;const _t=O.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,jt=s.get(O),Dt=R.length>1;if(Dt)for(let Bt=0;Bt<R.length;Bt++)i.bindFramebuffer(r.FRAMEBUFFER,jt.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Bt,r.RENDERBUFFER,null),i.bindFramebuffer(r.FRAMEBUFFER,jt.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Bt,r.TEXTURE_2D,null,0);i.bindFramebuffer(r.READ_FRAMEBUFFER,jt.__webglMultisampledFramebuffer),i.bindFramebuffer(r.DRAW_FRAMEBUFFER,jt.__webglFramebuffer);for(let Bt=0;Bt<R.length;Bt++){if(O.resolveDepthBuffer&&(O.depthBuffer&&(bt|=r.DEPTH_BUFFER_BIT),O.stencilBuffer&&O.resolveStencilBuffer&&(bt|=r.STENCIL_BUFFER_BIT)),Dt){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,jt.__webglColorRenderbuffer[Bt]);const ye=s.get(R[Bt]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,ye,0)}r.blitFramebuffer(0,0,it,dt,0,0,it,dt,bt,r.NEAREST),m===!0&&($e.length=0,k.length=0,$e.push(r.COLOR_ATTACHMENT0+Bt),O.depthBuffer&&O.resolveDepthBuffer===!1&&($e.push(_t),k.push(_t),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,k)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,$e))}if(i.bindFramebuffer(r.READ_FRAMEBUFFER,null),i.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),Dt)for(let Bt=0;Bt<R.length;Bt++){i.bindFramebuffer(r.FRAMEBUFFER,jt.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Bt,r.RENDERBUFFER,jt.__webglColorRenderbuffer[Bt]);const ye=s.get(R[Bt]).__webglTexture;i.bindFramebuffer(r.FRAMEBUFFER,jt.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Bt,r.TEXTURE_2D,ye,0)}i.bindFramebuffer(r.DRAW_FRAMEBUFFER,jt.__webglMultisampledFramebuffer)}else if(O.depthBuffer&&O.resolveDepthBuffer===!1&&m){const R=O.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[R])}}}function he(O){return Math.min(l.maxSamples,O.samples)}function ve(O){const R=s.get(O);return O.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&R.__useRenderToTexture!==!1}function Yt(O){const R=h.render.frame;g.get(O)!==R&&(g.set(O,R),O.update())}function Ie(O,R){const it=O.colorSpace,dt=O.format,bt=O.type;return O.isCompressedTexture===!0||O.isVideoTexture===!0||it!==Lo&&it!==ls&&(Ne.getTransfer(it)===je?(dt!==Bi||bt!==Da)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",it)),R}function Wt(O){return typeof HTMLImageElement<"u"&&O instanceof HTMLImageElement?(p.width=O.naturalWidth||O.width,p.height=O.naturalHeight||O.height):typeof VideoFrame<"u"&&O instanceof VideoFrame?(p.width=O.displayWidth,p.height=O.displayHeight):(p.width=O.width,p.height=O.height),p}this.allocateTextureUnit=lt,this.resetTextureUnits=ot,this.setTexture2D=gt,this.setTexture2DArray=B,this.setTexture3D=$,this.setTextureCube=J,this.rebindTextures=se,this.setupRenderTarget=He,this.updateRenderTargetMipmap=de,this.updateMultisampleRenderTarget=On,this.setupDepthRenderbuffer=Gt,this.setupFrameBufferTexture=Tt,this.useMultisampledRTT=ve}function rC(r,t){function i(s,l=ls){let c;const h=Ne.getTransfer(l);if(s===Da)return r.UNSIGNED_BYTE;if(s===am)return r.UNSIGNED_SHORT_4_4_4_4;if(s===sm)return r.UNSIGNED_SHORT_5_5_5_1;if(s===nx)return r.UNSIGNED_INT_5_9_9_9_REV;if(s===tx)return r.BYTE;if(s===ex)return r.SHORT;if(s===kl)return r.UNSIGNED_SHORT;if(s===im)return r.INT;if(s===hr)return r.UNSIGNED_INT;if(s===Ra)return r.FLOAT;if(s===Zl)return r.HALF_FLOAT;if(s===ix)return r.ALPHA;if(s===ax)return r.RGB;if(s===Bi)return r.RGBA;if(s===sx)return r.LUMINANCE;if(s===rx)return r.LUMINANCE_ALPHA;if(s===ho)return r.DEPTH_COMPONENT;if(s===No)return r.DEPTH_STENCIL;if(s===ox)return r.RED;if(s===rm)return r.RED_INTEGER;if(s===lx)return r.RG;if(s===om)return r.RG_INTEGER;if(s===lm)return r.RGBA_INTEGER;if(s===Fu||s===Hu||s===Gu||s===Vu)if(h===je)if(c=t.get("WEBGL_compressed_texture_s3tc_srgb"),c!==null){if(s===Fu)return c.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===Hu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===Gu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===Vu)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(c=t.get("WEBGL_compressed_texture_s3tc"),c!==null){if(s===Fu)return c.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===Hu)return c.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===Gu)return c.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===Vu)return c.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===Sp||s===Mp||s===Ep||s===bp)if(c=t.get("WEBGL_compressed_texture_pvrtc"),c!==null){if(s===Sp)return c.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===Mp)return c.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===Ep)return c.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===bp)return c.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===Tp||s===Ap||s===Rp)if(c=t.get("WEBGL_compressed_texture_etc"),c!==null){if(s===Tp||s===Ap)return h===je?c.COMPRESSED_SRGB8_ETC2:c.COMPRESSED_RGB8_ETC2;if(s===Rp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:c.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(s===Cp||s===wp||s===Dp||s===Up||s===Np||s===Lp||s===Op||s===Pp||s===zp||s===Ip||s===Bp||s===Fp||s===Hp||s===Gp)if(c=t.get("WEBGL_compressed_texture_astc"),c!==null){if(s===Cp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:c.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===wp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:c.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===Dp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:c.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===Up)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:c.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===Np)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:c.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===Lp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:c.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===Op)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:c.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===Pp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:c.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===zp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:c.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===Ip)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:c.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===Bp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:c.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===Fp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:c.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===Hp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:c.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===Gp)return h===je?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:c.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===ku||s===Vp||s===kp)if(c=t.get("EXT_texture_compression_bptc"),c!==null){if(s===ku)return h===je?c.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:c.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(s===Vp)return c.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(s===kp)return c.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(s===cx||s===Xp||s===jp||s===qp)if(c=t.get("EXT_texture_compression_rgtc"),c!==null){if(s===ku)return c.COMPRESSED_RED_RGTC1_EXT;if(s===Xp)return c.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===jp)return c.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===qp)return c.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===Uo?r.UNSIGNED_INT_24_8:r[s]!==void 0?r[s]:null}return{convert:i}}const oC={type:"move"};class Wd{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new co,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new co,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new Y,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new Y),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new co,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new Y,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new Y),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const i=this._hand;if(i)for(const s of t.hand.values())this._getHandJoint(i,s)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,i,s){let l=null,c=null,h=null;const d=this._targetRay,m=this._grip,p=this._hand;if(t&&i.session.visibilityState!=="visible-blurred"){if(p&&t.hand){h=!0;for(const b of t.hand.values()){const M=i.getJointPose(b,s),v=this._getHandJoint(p,b);M!==null&&(v.matrix.fromArray(M.transform.matrix),v.matrix.decompose(v.position,v.rotation,v.scale),v.matrixWorldNeedsUpdate=!0,v.jointRadius=M.radius),v.visible=M!==null}const g=p.joints["index-finger-tip"],_=p.joints["thumb-tip"],x=g.position.distanceTo(_.position),S=.02,E=.005;p.inputState.pinching&&x>S+E?(p.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!p.inputState.pinching&&x<=S-E&&(p.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else m!==null&&t.gripSpace&&(c=i.getPose(t.gripSpace,s),c!==null&&(m.matrix.fromArray(c.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,c.linearVelocity?(m.hasLinearVelocity=!0,m.linearVelocity.copy(c.linearVelocity)):m.hasLinearVelocity=!1,c.angularVelocity?(m.hasAngularVelocity=!0,m.angularVelocity.copy(c.angularVelocity)):m.hasAngularVelocity=!1));d!==null&&(l=i.getPose(t.targetRaySpace,s),l===null&&c!==null&&(l=c),l!==null&&(d.matrix.fromArray(l.transform.matrix),d.matrix.decompose(d.position,d.rotation,d.scale),d.matrixWorldNeedsUpdate=!0,l.linearVelocity?(d.hasLinearVelocity=!0,d.linearVelocity.copy(l.linearVelocity)):d.hasLinearVelocity=!1,l.angularVelocity?(d.hasAngularVelocity=!0,d.angularVelocity.copy(l.angularVelocity)):d.hasAngularVelocity=!1,this.dispatchEvent(oC)))}return d!==null&&(d.visible=l!==null),m!==null&&(m.visible=c!==null),p!==null&&(p.visible=h!==null),this}_getHandJoint(t,i){if(t.joints[i.jointName]===void 0){const s=new co;s.matrixAutoUpdate=!1,s.visible=!1,t.joints[i.jointName]=s,t.add(s)}return t.joints[i.jointName]}}const lC=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,cC=`
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

}`;class uC{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,i,s){if(this.texture===null){const l=new ni,c=t.properties.get(l);c.__webglTexture=i.texture,(i.depthNear!=s.depthNear||i.depthFar!=s.depthFar)&&(this.depthNear=i.depthNear,this.depthFar=i.depthFar),this.texture=l}}getMesh(t){if(this.texture!==null&&this.mesh===null){const i=t.cameras[0].viewport,s=new Ss({vertexShader:lC,fragmentShader:cC,uniforms:{depthColor:{value:this.texture},depthWidth:{value:i.z},depthHeight:{value:i.w}}});this.mesh=new Ri(new $u(20,20),s)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class fC extends Po{constructor(t,i){super();const s=this;let l=null,c=1,h=null,d="local-floor",m=1,p=null,g=null,_=null,x=null,S=null,E=null;const b=new uC,M=i.getContextAttributes();let v=null,L=null;const U=[],T=[],V=new Ae;let I=null;const P=new pi;P.viewport=new qe;const H=new pi;H.viewport=new qe;const D=[P,H],C=new Nb;let G=null,ot=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(K){let ft=U[K];return ft===void 0&&(ft=new Wd,U[K]=ft),ft.getTargetRaySpace()},this.getControllerGrip=function(K){let ft=U[K];return ft===void 0&&(ft=new Wd,U[K]=ft),ft.getGripSpace()},this.getHand=function(K){let ft=U[K];return ft===void 0&&(ft=new Wd,U[K]=ft),ft.getHandSpace()};function lt(K){const ft=T.indexOf(K.inputSource);if(ft===-1)return;const Tt=U[ft];Tt!==void 0&&(Tt.update(K.inputSource,K.frame,p||h),Tt.dispatchEvent({type:K.type,data:K.inputSource}))}function mt(){l.removeEventListener("select",lt),l.removeEventListener("selectstart",lt),l.removeEventListener("selectend",lt),l.removeEventListener("squeeze",lt),l.removeEventListener("squeezestart",lt),l.removeEventListener("squeezeend",lt),l.removeEventListener("end",mt),l.removeEventListener("inputsourceschange",gt);for(let K=0;K<U.length;K++){const ft=T[K];ft!==null&&(T[K]=null,U[K].disconnect(ft))}G=null,ot=null,b.reset(),t.setRenderTarget(v),S=null,x=null,_=null,l=null,L=null,Mt.stop(),s.isPresenting=!1,t.setPixelRatio(I),t.setSize(V.width,V.height,!1),s.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(K){c=K,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(K){d=K,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return p||h},this.setReferenceSpace=function(K){p=K},this.getBaseLayer=function(){return x!==null?x:S},this.getBinding=function(){return _},this.getFrame=function(){return E},this.getSession=function(){return l},this.setSession=async function(K){if(l=K,l!==null){if(v=t.getRenderTarget(),l.addEventListener("select",lt),l.addEventListener("selectstart",lt),l.addEventListener("selectend",lt),l.addEventListener("squeeze",lt),l.addEventListener("squeezestart",lt),l.addEventListener("squeezeend",lt),l.addEventListener("end",mt),l.addEventListener("inputsourceschange",gt),M.xrCompatible!==!0&&await i.makeXRCompatible(),I=t.getPixelRatio(),t.getSize(V),l.renderState.layers===void 0){const ft={antialias:M.antialias,alpha:!0,depth:M.depth,stencil:M.stencil,framebufferScaleFactor:c};S=new XRWebGLLayer(l,i,ft),l.updateRenderState({baseLayer:S}),t.setPixelRatio(1),t.setSize(S.framebufferWidth,S.framebufferHeight,!1),L=new dr(S.framebufferWidth,S.framebufferHeight,{format:Bi,type:Da,colorSpace:t.outputColorSpace,stencilBuffer:M.stencil})}else{let ft=null,Tt=null,St=null;M.depth&&(St=M.stencil?i.DEPTH24_STENCIL8:i.DEPTH_COMPONENT24,ft=M.stencil?No:ho,Tt=M.stencil?Uo:hr);const kt={colorFormat:i.RGBA8,depthFormat:St,scaleFactor:c};_=new XRWebGLBinding(l,i),x=_.createProjectionLayer(kt),l.updateRenderState({layers:[x]}),t.setPixelRatio(1),t.setSize(x.textureWidth,x.textureHeight,!1),L=new dr(x.textureWidth,x.textureHeight,{format:Bi,type:Da,depthTexture:new Mx(x.textureWidth,x.textureHeight,Tt,void 0,void 0,void 0,void 0,void 0,void 0,ft),stencilBuffer:M.stencil,colorSpace:t.outputColorSpace,samples:M.antialias?4:0,resolveDepthBuffer:x.ignoreDepthValues===!1})}L.isXRRenderTarget=!0,this.setFoveation(m),p=null,h=await l.requestReferenceSpace(d),Mt.setContext(l),Mt.start(),s.isPresenting=!0,s.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(l!==null)return l.environmentBlendMode},this.getDepthTexture=function(){return b.getDepthTexture()};function gt(K){for(let ft=0;ft<K.removed.length;ft++){const Tt=K.removed[ft],St=T.indexOf(Tt);St>=0&&(T[St]=null,U[St].disconnect(Tt))}for(let ft=0;ft<K.added.length;ft++){const Tt=K.added[ft];let St=T.indexOf(Tt);if(St===-1){for(let Gt=0;Gt<U.length;Gt++)if(Gt>=T.length){T.push(Tt),St=Gt;break}else if(T[Gt]===null){T[Gt]=Tt,St=Gt;break}if(St===-1)break}const kt=U[St];kt&&kt.connect(Tt)}}const B=new Y,$=new Y;function J(K,ft,Tt){B.setFromMatrixPosition(ft.matrixWorld),$.setFromMatrixPosition(Tt.matrixWorld);const St=B.distanceTo($),kt=ft.projectionMatrix.elements,Gt=Tt.projectionMatrix.elements,se=kt[14]/(kt[10]-1),He=kt[14]/(kt[10]+1),de=(kt[9]+1)/kt[5],$e=(kt[9]-1)/kt[5],k=(kt[8]-1)/kt[0],On=(Gt[8]+1)/Gt[0],he=se*k,ve=se*On,Yt=St/(-k+On),Ie=Yt*-k;if(ft.matrixWorld.decompose(K.position,K.quaternion,K.scale),K.translateX(Ie),K.translateZ(Yt),K.matrixWorld.compose(K.position,K.quaternion,K.scale),K.matrixWorldInverse.copy(K.matrixWorld).invert(),kt[10]===-1)K.projectionMatrix.copy(ft.projectionMatrix),K.projectionMatrixInverse.copy(ft.projectionMatrixInverse);else{const Wt=se+Yt,O=He+Yt,R=he-Ie,it=ve+(St-Ie),dt=de*He/O*Wt,bt=$e*He/O*Wt;K.projectionMatrix.makePerspective(R,it,dt,bt,Wt,O),K.projectionMatrixInverse.copy(K.projectionMatrix).invert()}}function Et(K,ft){ft===null?K.matrixWorld.copy(K.matrix):K.matrixWorld.multiplyMatrices(ft.matrixWorld,K.matrix),K.matrixWorldInverse.copy(K.matrixWorld).invert()}this.updateCamera=function(K){if(l===null)return;let ft=K.near,Tt=K.far;b.texture!==null&&(b.depthNear>0&&(ft=b.depthNear),b.depthFar>0&&(Tt=b.depthFar)),C.near=H.near=P.near=ft,C.far=H.far=P.far=Tt,(G!==C.near||ot!==C.far)&&(l.updateRenderState({depthNear:C.near,depthFar:C.far}),G=C.near,ot=C.far),P.layers.mask=K.layers.mask|2,H.layers.mask=K.layers.mask|4,C.layers.mask=P.layers.mask|H.layers.mask;const St=K.parent,kt=C.cameras;Et(C,St);for(let Gt=0;Gt<kt.length;Gt++)Et(kt[Gt],St);kt.length===2?J(C,P,H):C.projectionMatrix.copy(P.projectionMatrix),At(K,C,St)};function At(K,ft,Tt){Tt===null?K.matrix.copy(ft.matrixWorld):(K.matrix.copy(Tt.matrixWorld),K.matrix.invert(),K.matrix.multiply(ft.matrixWorld)),K.matrix.decompose(K.position,K.quaternion,K.scale),K.updateMatrixWorld(!0),K.projectionMatrix.copy(ft.projectionMatrix),K.projectionMatrixInverse.copy(ft.projectionMatrixInverse),K.isPerspectiveCamera&&(K.fov=Wp*2*Math.atan(1/K.projectionMatrix.elements[5]),K.zoom=1)}this.getCamera=function(){return C},this.getFoveation=function(){if(!(x===null&&S===null))return m},this.setFoveation=function(K){m=K,x!==null&&(x.fixedFoveation=K),S!==null&&S.fixedFoveation!==void 0&&(S.fixedFoveation=K)},this.hasDepthSensing=function(){return b.texture!==null},this.getDepthSensingMesh=function(){return b.getMesh(C)};let z=null;function at(K,ft){if(g=ft.getViewerPose(p||h),E=ft,g!==null){const Tt=g.views;S!==null&&(t.setRenderTargetFramebuffer(L,S.framebuffer),t.setRenderTarget(L));let St=!1;Tt.length!==C.cameras.length&&(C.cameras.length=0,St=!0);for(let Gt=0;Gt<Tt.length;Gt++){const se=Tt[Gt];let He=null;if(S!==null)He=S.getViewport(se);else{const $e=_.getViewSubImage(x,se);He=$e.viewport,Gt===0&&(t.setRenderTargetTextures(L,$e.colorTexture,x.ignoreDepthValues?void 0:$e.depthStencilTexture),t.setRenderTarget(L))}let de=D[Gt];de===void 0&&(de=new pi,de.layers.enable(Gt),de.viewport=new qe,D[Gt]=de),de.matrix.fromArray(se.transform.matrix),de.matrix.decompose(de.position,de.quaternion,de.scale),de.projectionMatrix.fromArray(se.projectionMatrix),de.projectionMatrixInverse.copy(de.projectionMatrix).invert(),de.viewport.set(He.x,He.y,He.width,He.height),Gt===0&&(C.matrix.copy(de.matrix),C.matrix.decompose(C.position,C.quaternion,C.scale)),St===!0&&C.cameras.push(de)}const kt=l.enabledFeatures;if(kt&&kt.includes("depth-sensing")){const Gt=_.getDepthInformation(Tt[0]);Gt&&Gt.isValid&&Gt.texture&&b.init(t,Gt,l.renderState)}}for(let Tt=0;Tt<U.length;Tt++){const St=T[Tt],kt=U[Tt];St!==null&&kt!==void 0&&kt.update(St,ft,p||h)}z&&z(K,ft),ft.detectedPlanes&&s.dispatchEvent({type:"planesdetected",data:ft}),E=null}const Mt=new Ex;Mt.setAnimationLoop(at),this.setAnimationLoop=function(K){z=K},this.dispose=function(){}}}const Ws=new Ua,hC=new Je;function dC(r,t){function i(M,v){M.matrixAutoUpdate===!0&&M.updateMatrix(),v.value.copy(M.matrix)}function s(M,v){v.color.getRGB(M.fogColor.value,yx(r)),v.isFog?(M.fogNear.value=v.near,M.fogFar.value=v.far):v.isFogExp2&&(M.fogDensity.value=v.density)}function l(M,v,L,U,T){v.isMeshBasicMaterial||v.isMeshLambertMaterial?c(M,v):v.isMeshToonMaterial?(c(M,v),_(M,v)):v.isMeshPhongMaterial?(c(M,v),g(M,v)):v.isMeshStandardMaterial?(c(M,v),x(M,v),v.isMeshPhysicalMaterial&&S(M,v,T)):v.isMeshMatcapMaterial?(c(M,v),E(M,v)):v.isMeshDepthMaterial?c(M,v):v.isMeshDistanceMaterial?(c(M,v),b(M,v)):v.isMeshNormalMaterial?c(M,v):v.isLineBasicMaterial?(h(M,v),v.isLineDashedMaterial&&d(M,v)):v.isPointsMaterial?m(M,v,L,U):v.isSpriteMaterial?p(M,v):v.isShadowMaterial?(M.color.value.copy(v.color),M.opacity.value=v.opacity):v.isShaderMaterial&&(v.uniformsNeedUpdate=!1)}function c(M,v){M.opacity.value=v.opacity,v.color&&M.diffuse.value.copy(v.color),v.emissive&&M.emissive.value.copy(v.emissive).multiplyScalar(v.emissiveIntensity),v.map&&(M.map.value=v.map,i(v.map,M.mapTransform)),v.alphaMap&&(M.alphaMap.value=v.alphaMap,i(v.alphaMap,M.alphaMapTransform)),v.bumpMap&&(M.bumpMap.value=v.bumpMap,i(v.bumpMap,M.bumpMapTransform),M.bumpScale.value=v.bumpScale,v.side===ei&&(M.bumpScale.value*=-1)),v.normalMap&&(M.normalMap.value=v.normalMap,i(v.normalMap,M.normalMapTransform),M.normalScale.value.copy(v.normalScale),v.side===ei&&M.normalScale.value.negate()),v.displacementMap&&(M.displacementMap.value=v.displacementMap,i(v.displacementMap,M.displacementMapTransform),M.displacementScale.value=v.displacementScale,M.displacementBias.value=v.displacementBias),v.emissiveMap&&(M.emissiveMap.value=v.emissiveMap,i(v.emissiveMap,M.emissiveMapTransform)),v.specularMap&&(M.specularMap.value=v.specularMap,i(v.specularMap,M.specularMapTransform)),v.alphaTest>0&&(M.alphaTest.value=v.alphaTest);const L=t.get(v),U=L.envMap,T=L.envMapRotation;U&&(M.envMap.value=U,Ws.copy(T),Ws.x*=-1,Ws.y*=-1,Ws.z*=-1,U.isCubeTexture&&U.isRenderTargetTexture===!1&&(Ws.y*=-1,Ws.z*=-1),M.envMapRotation.value.setFromMatrix4(hC.makeRotationFromEuler(Ws)),M.flipEnvMap.value=U.isCubeTexture&&U.isRenderTargetTexture===!1?-1:1,M.reflectivity.value=v.reflectivity,M.ior.value=v.ior,M.refractionRatio.value=v.refractionRatio),v.lightMap&&(M.lightMap.value=v.lightMap,M.lightMapIntensity.value=v.lightMapIntensity,i(v.lightMap,M.lightMapTransform)),v.aoMap&&(M.aoMap.value=v.aoMap,M.aoMapIntensity.value=v.aoMapIntensity,i(v.aoMap,M.aoMapTransform))}function h(M,v){M.diffuse.value.copy(v.color),M.opacity.value=v.opacity,v.map&&(M.map.value=v.map,i(v.map,M.mapTransform))}function d(M,v){M.dashSize.value=v.dashSize,M.totalSize.value=v.dashSize+v.gapSize,M.scale.value=v.scale}function m(M,v,L,U){M.diffuse.value.copy(v.color),M.opacity.value=v.opacity,M.size.value=v.size*L,M.scale.value=U*.5,v.map&&(M.map.value=v.map,i(v.map,M.uvTransform)),v.alphaMap&&(M.alphaMap.value=v.alphaMap,i(v.alphaMap,M.alphaMapTransform)),v.alphaTest>0&&(M.alphaTest.value=v.alphaTest)}function p(M,v){M.diffuse.value.copy(v.color),M.opacity.value=v.opacity,M.rotation.value=v.rotation,v.map&&(M.map.value=v.map,i(v.map,M.mapTransform)),v.alphaMap&&(M.alphaMap.value=v.alphaMap,i(v.alphaMap,M.alphaMapTransform)),v.alphaTest>0&&(M.alphaTest.value=v.alphaTest)}function g(M,v){M.specular.value.copy(v.specular),M.shininess.value=Math.max(v.shininess,1e-4)}function _(M,v){v.gradientMap&&(M.gradientMap.value=v.gradientMap)}function x(M,v){M.metalness.value=v.metalness,v.metalnessMap&&(M.metalnessMap.value=v.metalnessMap,i(v.metalnessMap,M.metalnessMapTransform)),M.roughness.value=v.roughness,v.roughnessMap&&(M.roughnessMap.value=v.roughnessMap,i(v.roughnessMap,M.roughnessMapTransform)),v.envMap&&(M.envMapIntensity.value=v.envMapIntensity)}function S(M,v,L){M.ior.value=v.ior,v.sheen>0&&(M.sheenColor.value.copy(v.sheenColor).multiplyScalar(v.sheen),M.sheenRoughness.value=v.sheenRoughness,v.sheenColorMap&&(M.sheenColorMap.value=v.sheenColorMap,i(v.sheenColorMap,M.sheenColorMapTransform)),v.sheenRoughnessMap&&(M.sheenRoughnessMap.value=v.sheenRoughnessMap,i(v.sheenRoughnessMap,M.sheenRoughnessMapTransform))),v.clearcoat>0&&(M.clearcoat.value=v.clearcoat,M.clearcoatRoughness.value=v.clearcoatRoughness,v.clearcoatMap&&(M.clearcoatMap.value=v.clearcoatMap,i(v.clearcoatMap,M.clearcoatMapTransform)),v.clearcoatRoughnessMap&&(M.clearcoatRoughnessMap.value=v.clearcoatRoughnessMap,i(v.clearcoatRoughnessMap,M.clearcoatRoughnessMapTransform)),v.clearcoatNormalMap&&(M.clearcoatNormalMap.value=v.clearcoatNormalMap,i(v.clearcoatNormalMap,M.clearcoatNormalMapTransform),M.clearcoatNormalScale.value.copy(v.clearcoatNormalScale),v.side===ei&&M.clearcoatNormalScale.value.negate())),v.dispersion>0&&(M.dispersion.value=v.dispersion),v.iridescence>0&&(M.iridescence.value=v.iridescence,M.iridescenceIOR.value=v.iridescenceIOR,M.iridescenceThicknessMinimum.value=v.iridescenceThicknessRange[0],M.iridescenceThicknessMaximum.value=v.iridescenceThicknessRange[1],v.iridescenceMap&&(M.iridescenceMap.value=v.iridescenceMap,i(v.iridescenceMap,M.iridescenceMapTransform)),v.iridescenceThicknessMap&&(M.iridescenceThicknessMap.value=v.iridescenceThicknessMap,i(v.iridescenceThicknessMap,M.iridescenceThicknessMapTransform))),v.transmission>0&&(M.transmission.value=v.transmission,M.transmissionSamplerMap.value=L.texture,M.transmissionSamplerSize.value.set(L.width,L.height),v.transmissionMap&&(M.transmissionMap.value=v.transmissionMap,i(v.transmissionMap,M.transmissionMapTransform)),M.thickness.value=v.thickness,v.thicknessMap&&(M.thicknessMap.value=v.thicknessMap,i(v.thicknessMap,M.thicknessMapTransform)),M.attenuationDistance.value=v.attenuationDistance,M.attenuationColor.value.copy(v.attenuationColor)),v.anisotropy>0&&(M.anisotropyVector.value.set(v.anisotropy*Math.cos(v.anisotropyRotation),v.anisotropy*Math.sin(v.anisotropyRotation)),v.anisotropyMap&&(M.anisotropyMap.value=v.anisotropyMap,i(v.anisotropyMap,M.anisotropyMapTransform))),M.specularIntensity.value=v.specularIntensity,M.specularColor.value.copy(v.specularColor),v.specularColorMap&&(M.specularColorMap.value=v.specularColorMap,i(v.specularColorMap,M.specularColorMapTransform)),v.specularIntensityMap&&(M.specularIntensityMap.value=v.specularIntensityMap,i(v.specularIntensityMap,M.specularIntensityMapTransform))}function E(M,v){v.matcap&&(M.matcap.value=v.matcap)}function b(M,v){const L=t.get(v).light;M.referencePosition.value.setFromMatrixPosition(L.matrixWorld),M.nearDistance.value=L.shadow.camera.near,M.farDistance.value=L.shadow.camera.far}return{refreshFogUniforms:s,refreshMaterialUniforms:l}}function pC(r,t,i,s){let l={},c={},h=[];const d=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function m(L,U){const T=U.program;s.uniformBlockBinding(L,T)}function p(L,U){let T=l[L.id];T===void 0&&(E(L),T=g(L),l[L.id]=T,L.addEventListener("dispose",M));const V=U.program;s.updateUBOMapping(L,V);const I=t.render.frame;c[L.id]!==I&&(x(L),c[L.id]=I)}function g(L){const U=_();L.__bindingPointIndex=U;const T=r.createBuffer(),V=L.__size,I=L.usage;return r.bindBuffer(r.UNIFORM_BUFFER,T),r.bufferData(r.UNIFORM_BUFFER,V,I),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,U,T),T}function _(){for(let L=0;L<d;L++)if(h.indexOf(L)===-1)return h.push(L),L;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function x(L){const U=l[L.id],T=L.uniforms,V=L.__cache;r.bindBuffer(r.UNIFORM_BUFFER,U);for(let I=0,P=T.length;I<P;I++){const H=Array.isArray(T[I])?T[I]:[T[I]];for(let D=0,C=H.length;D<C;D++){const G=H[D];if(S(G,I,D,V)===!0){const ot=G.__offset,lt=Array.isArray(G.value)?G.value:[G.value];let mt=0;for(let gt=0;gt<lt.length;gt++){const B=lt[gt],$=b(B);typeof B=="number"||typeof B=="boolean"?(G.__data[0]=B,r.bufferSubData(r.UNIFORM_BUFFER,ot+mt,G.__data)):B.isMatrix3?(G.__data[0]=B.elements[0],G.__data[1]=B.elements[1],G.__data[2]=B.elements[2],G.__data[3]=0,G.__data[4]=B.elements[3],G.__data[5]=B.elements[4],G.__data[6]=B.elements[5],G.__data[7]=0,G.__data[8]=B.elements[6],G.__data[9]=B.elements[7],G.__data[10]=B.elements[8],G.__data[11]=0):(B.toArray(G.__data,mt),mt+=$.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,ot,G.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function S(L,U,T,V){const I=L.value,P=U+"_"+T;if(V[P]===void 0)return typeof I=="number"||typeof I=="boolean"?V[P]=I:V[P]=I.clone(),!0;{const H=V[P];if(typeof I=="number"||typeof I=="boolean"){if(H!==I)return V[P]=I,!0}else if(H.equals(I)===!1)return H.copy(I),!0}return!1}function E(L){const U=L.uniforms;let T=0;const V=16;for(let P=0,H=U.length;P<H;P++){const D=Array.isArray(U[P])?U[P]:[U[P]];for(let C=0,G=D.length;C<G;C++){const ot=D[C],lt=Array.isArray(ot.value)?ot.value:[ot.value];for(let mt=0,gt=lt.length;mt<gt;mt++){const B=lt[mt],$=b(B),J=T%V,Et=J%$.boundary,At=J+Et;T+=Et,At!==0&&V-At<$.storage&&(T+=V-At),ot.__data=new Float32Array($.storage/Float32Array.BYTES_PER_ELEMENT),ot.__offset=T,T+=$.storage}}}const I=T%V;return I>0&&(T+=V-I),L.__size=T,L.__cache={},this}function b(L){const U={boundary:0,storage:0};return typeof L=="number"||typeof L=="boolean"?(U.boundary=4,U.storage=4):L.isVector2?(U.boundary=8,U.storage=8):L.isVector3||L.isColor?(U.boundary=16,U.storage=12):L.isVector4?(U.boundary=16,U.storage=16):L.isMatrix3?(U.boundary=48,U.storage=48):L.isMatrix4?(U.boundary=64,U.storage=64):L.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",L),U}function M(L){const U=L.target;U.removeEventListener("dispose",M);const T=h.indexOf(U.__bindingPointIndex);h.splice(T,1),r.deleteBuffer(l[U.id]),delete l[U.id],delete c[U.id]}function v(){for(const L in l)r.deleteBuffer(l[L]);h=[],l={},c={}}return{bind:m,update:p,dispose:v}}class mC{constructor(t={}){const{canvas:i=Y1(),context:s=null,depth:l=!0,stencil:c=!1,alpha:h=!1,antialias:d=!1,premultipliedAlpha:m=!0,preserveDrawingBuffer:p=!1,powerPreference:g="default",failIfMajorPerformanceCaveat:_=!1,reverseDepthBuffer:x=!1}=t;this.isWebGLRenderer=!0;let S;if(s!==null){if(typeof WebGLRenderingContext<"u"&&s instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");S=s.getContextAttributes().alpha}else S=h;const E=new Uint32Array(4),b=new Int32Array(4);let M=null,v=null;const L=[],U=[];this.domElement=i,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Ai,this.toneMapping=ys,this.toneMappingExposure=1;const T=this;let V=!1,I=0,P=0,H=null,D=-1,C=null;const G=new qe,ot=new qe;let lt=null;const mt=new Oe(0);let gt=0,B=i.width,$=i.height,J=1,Et=null,At=null;const z=new qe(0,0,B,$),at=new qe(0,0,B,$);let Mt=!1;const K=new cm;let ft=!1,Tt=!1;const St=new Je,kt=new Je,Gt=new Y,se=new qe,He={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let de=!1;function $e(){return H===null?J:1}let k=s;function On(w,W){return i.getContext(w,W)}try{const w={alpha:!0,depth:l,stencil:c,antialias:d,premultipliedAlpha:m,preserveDrawingBuffer:p,powerPreference:g,failIfMajorPerformanceCaveat:_};if("setAttribute"in i&&i.setAttribute("data-engine",`three.js r${nm}`),i.addEventListener("webglcontextlost",yt,!1),i.addEventListener("webglcontextrestored",wt,!1),i.addEventListener("webglcontextcreationerror",Ut,!1),k===null){const W="webgl2";if(k=On(W,w),k===null)throw On(W)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(w){throw console.error("THREE.WebGLRenderer: "+w.message),w}let he,ve,Yt,Ie,Wt,O,R,it,dt,bt,_t,jt,Dt,Bt,ye,Rt,Ft,Qt,qt,Ot,ee,re,Ge,q;function Ct(){he=new b2(k),he.init(),re=new rC(k,he),ve=new v2(k,he,t,re),Yt=new aC(k,he),ve.reverseDepthBuffer&&x&&Yt.buffers.depth.setReversed(!0),Ie=new R2(k),Wt=new jR,O=new sC(k,he,Yt,Wt,ve,re,Ie),R=new x2(T),it=new E2(T),dt=new Ob(k),Ge=new g2(k,dt),bt=new T2(k,dt,Ie,Ge),_t=new w2(k,bt,dt,Ie),qt=new C2(k,ve,O),Rt=new y2(Wt),jt=new XR(T,R,it,he,ve,Ge,Rt),Dt=new dC(T,Wt),Bt=new WR,ye=new $R(he),Qt=new m2(T,R,it,Yt,_t,S,m),Ft=new nC(T,_t,ve),q=new pC(k,Ie,ve,Yt),Ot=new _2(k,he,Ie),ee=new A2(k,he,Ie),Ie.programs=jt.programs,T.capabilities=ve,T.extensions=he,T.properties=Wt,T.renderLists=Bt,T.shadowMap=Ft,T.state=Yt,T.info=Ie}Ct();const ut=new fC(T,k);this.xr=ut,this.getContext=function(){return k},this.getContextAttributes=function(){return k.getContextAttributes()},this.forceContextLoss=function(){const w=he.get("WEBGL_lose_context");w&&w.loseContext()},this.forceContextRestore=function(){const w=he.get("WEBGL_lose_context");w&&w.restoreContext()},this.getPixelRatio=function(){return J},this.setPixelRatio=function(w){w!==void 0&&(J=w,this.setSize(B,$,!1))},this.getSize=function(w){return w.set(B,$)},this.setSize=function(w,W,st=!0){if(ut.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}B=w,$=W,i.width=Math.floor(w*J),i.height=Math.floor(W*J),st===!0&&(i.style.width=w+"px",i.style.height=W+"px"),this.setViewport(0,0,w,W)},this.getDrawingBufferSize=function(w){return w.set(B*J,$*J).floor()},this.setDrawingBufferSize=function(w,W,st){B=w,$=W,J=st,i.width=Math.floor(w*st),i.height=Math.floor(W*st),this.setViewport(0,0,w,W)},this.getCurrentViewport=function(w){return w.copy(G)},this.getViewport=function(w){return w.copy(z)},this.setViewport=function(w,W,st,rt){w.isVector4?z.set(w.x,w.y,w.z,w.w):z.set(w,W,st,rt),Yt.viewport(G.copy(z).multiplyScalar(J).round())},this.getScissor=function(w){return w.copy(at)},this.setScissor=function(w,W,st,rt){w.isVector4?at.set(w.x,w.y,w.z,w.w):at.set(w,W,st,rt),Yt.scissor(ot.copy(at).multiplyScalar(J).round())},this.getScissorTest=function(){return Mt},this.setScissorTest=function(w){Yt.setScissorTest(Mt=w)},this.setOpaqueSort=function(w){Et=w},this.setTransparentSort=function(w){At=w},this.getClearColor=function(w){return w.copy(Qt.getClearColor())},this.setClearColor=function(){Qt.setClearColor.apply(Qt,arguments)},this.getClearAlpha=function(){return Qt.getClearAlpha()},this.setClearAlpha=function(){Qt.setClearAlpha.apply(Qt,arguments)},this.clear=function(w=!0,W=!0,st=!0){let rt=0;if(w){let Q=!1;if(H!==null){const xt=H.texture.format;Q=xt===lm||xt===om||xt===rm}if(Q){const xt=H.texture.type,Nt=xt===Da||xt===hr||xt===kl||xt===Uo||xt===am||xt===sm,It=Qt.getClearColor(),Pt=Qt.getClearAlpha(),Jt=It.r,ie=It.g,Zt=It.b;Nt?(E[0]=Jt,E[1]=ie,E[2]=Zt,E[3]=Pt,k.clearBufferuiv(k.COLOR,0,E)):(b[0]=Jt,b[1]=ie,b[2]=Zt,b[3]=Pt,k.clearBufferiv(k.COLOR,0,b))}else rt|=k.COLOR_BUFFER_BIT}W&&(rt|=k.DEPTH_BUFFER_BIT),st&&(rt|=k.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),k.clear(rt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){i.removeEventListener("webglcontextlost",yt,!1),i.removeEventListener("webglcontextrestored",wt,!1),i.removeEventListener("webglcontextcreationerror",Ut,!1),Qt.dispose(),Bt.dispose(),ye.dispose(),Wt.dispose(),R.dispose(),it.dispose(),_t.dispose(),Ge.dispose(),q.dispose(),jt.dispose(),ut.dispose(),ut.removeEventListener("sessionstart",Io),ut.removeEventListener("sessionend",Bo),Hi.stop()};function yt(w){w.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),V=!0}function wt(){console.log("THREE.WebGLRenderer: Context Restored."),V=!1;const w=Ie.autoReset,W=Ft.enabled,st=Ft.autoUpdate,rt=Ft.needsUpdate,Q=Ft.type;Ct(),Ie.autoReset=w,Ft.enabled=W,Ft.autoUpdate=st,Ft.needsUpdate=rt,Ft.type=Q}function Ut(w){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",w.statusMessage)}function ne(w){const W=w.target;W.removeEventListener("dispose",ne),tn(W)}function tn(w){_n(w),Wt.remove(w)}function _n(w){const W=Wt.get(w).programs;W!==void 0&&(W.forEach(function(st){jt.releaseProgram(st)}),w.isShaderMaterial&&jt.releaseShaderCache(w))}this.renderBufferDirect=function(w,W,st,rt,Q,xt){W===null&&(W=He);const Nt=Q.isMesh&&Q.matrixWorld.determinant()<0,It=Ho(w,W,st,rt,Q);Yt.setMaterial(rt,Nt);let Pt=st.index,Jt=1;if(rt.wireframe===!0){if(Pt=bt.getWireframeAttribute(st),Pt===void 0)return;Jt=2}const ie=st.drawRange,Zt=st.attributes.position;let xe=ie.start*Jt,Ce=(ie.start+ie.count)*Jt;xt!==null&&(xe=Math.max(xe,xt.start*Jt),Ce=Math.min(Ce,(xt.start+xt.count)*Jt)),Pt!==null?(xe=Math.max(xe,0),Ce=Math.min(Ce,Pt.count)):Zt!=null&&(xe=Math.max(xe,0),Ce=Math.min(Ce,Zt.count));const Qe=Ce-xe;if(Qe<0||Qe===1/0)return;Ge.setup(Q,rt,It,st,Pt);let We,oe=Ot;if(Pt!==null&&(We=dt.get(Pt),oe=ee,oe.setIndex(We)),Q.isMesh)rt.wireframe===!0?(Yt.setLineWidth(rt.wireframeLinewidth*$e()),oe.setMode(k.LINES)):oe.setMode(k.TRIANGLES);else if(Q.isLine){let Vt=rt.linewidth;Vt===void 0&&(Vt=1),Yt.setLineWidth(Vt*$e()),Q.isLineSegments?oe.setMode(k.LINES):Q.isLineLoop?oe.setMode(k.LINE_LOOP):oe.setMode(k.LINE_STRIP)}else Q.isPoints?oe.setMode(k.POINTS):Q.isSprite&&oe.setMode(k.TRIANGLES);if(Q.isBatchedMesh)if(Q._multiDrawInstances!==null)oe.renderMultiDrawInstances(Q._multiDrawStarts,Q._multiDrawCounts,Q._multiDrawCount,Q._multiDrawInstances);else if(he.get("WEBGL_multi_draw"))oe.renderMultiDraw(Q._multiDrawStarts,Q._multiDrawCounts,Q._multiDrawCount);else{const Vt=Q._multiDrawStarts,fn=Q._multiDrawCounts,we=Q._multiDrawCount,Hn=Pt?dt.get(Pt).bytesPerElement:1,$i=Wt.get(rt).currentProgram.getUniforms();for(let Mn=0;Mn<we;Mn++)$i.setValue(k,"_gl_DrawID",Mn),oe.render(Vt[Mn]/Hn,fn[Mn])}else if(Q.isInstancedMesh)oe.renderInstances(xe,Qe,Q.count);else if(st.isInstancedBufferGeometry){const Vt=st._maxInstanceCount!==void 0?st._maxInstanceCount:1/0,fn=Math.min(st.instanceCount,Vt);oe.renderInstances(xe,Qe,fn)}else oe.render(xe,Qe)};function Re(w,W,st){w.transparent===!0&&w.side===Aa&&w.forceSinglePass===!1?(w.side=ei,w.needsUpdate=!0,an(w,W,st),w.side=xs,w.needsUpdate=!0,an(w,W,st),w.side=Aa):an(w,W,st)}this.compile=function(w,W,st=null){st===null&&(st=w),v=ye.get(st),v.init(W),U.push(v),st.traverseVisible(function(Q){Q.isLight&&Q.layers.test(W.layers)&&(v.pushLight(Q),Q.castShadow&&v.pushShadow(Q))}),w!==st&&w.traverseVisible(function(Q){Q.isLight&&Q.layers.test(W.layers)&&(v.pushLight(Q),Q.castShadow&&v.pushShadow(Q))}),v.setupLights();const rt=new Set;return w.traverse(function(Q){if(!(Q.isMesh||Q.isPoints||Q.isLine||Q.isSprite))return;const xt=Q.material;if(xt)if(Array.isArray(xt))for(let Nt=0;Nt<xt.length;Nt++){const It=xt[Nt];Re(It,st,Q),rt.add(It)}else Re(xt,st,Q),rt.add(xt)}),U.pop(),v=null,rt},this.compileAsync=function(w,W,st=null){const rt=this.compile(w,W,st);return new Promise(Q=>{function xt(){if(rt.forEach(function(Nt){Wt.get(Nt).currentProgram.isReady()&&rt.delete(Nt)}),rt.size===0){Q(w);return}setTimeout(xt,10)}he.get("KHR_parallel_shader_compile")!==null?xt():setTimeout(xt,10)})};let An=null;function Ci(w){An&&An(w)}function Io(){Hi.stop()}function Bo(){Hi.start()}const Hi=new Ex;Hi.setAnimationLoop(Ci),typeof self<"u"&&Hi.setContext(self),this.setAnimationLoop=function(w){An=w,ut.setAnimationLoop(w),w===null?Hi.stop():Hi.start()},ut.addEventListener("sessionstart",Io),ut.addEventListener("sessionend",Bo),this.render=function(w,W){if(W!==void 0&&W.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(V===!0)return;if(w.matrixWorldAutoUpdate===!0&&w.updateMatrixWorld(),W.parent===null&&W.matrixWorldAutoUpdate===!0&&W.updateMatrixWorld(),ut.enabled===!0&&ut.isPresenting===!0&&(ut.cameraAutoUpdate===!0&&ut.updateCamera(W),W=ut.getCamera()),w.isScene===!0&&w.onBeforeRender(T,w,W,H),v=ye.get(w,U.length),v.init(W),U.push(v),kt.multiplyMatrices(W.projectionMatrix,W.matrixWorldInverse),K.setFromProjectionMatrix(kt),Tt=this.localClippingEnabled,ft=Rt.init(this.clippingPlanes,Tt),M=Bt.get(w,L.length),M.init(),L.push(M),ut.enabled===!0&&ut.isPresenting===!0){const xt=T.xr.getDepthSensingMesh();xt!==null&&Ms(xt,W,-1/0,T.sortObjects)}Ms(w,W,0,T.sortObjects),M.finish(),T.sortObjects===!0&&M.sort(Et,At),de=ut.enabled===!1||ut.isPresenting===!1||ut.hasDepthSensing()===!1,de&&Qt.addToRenderList(M,w),this.info.render.frame++,ft===!0&&Rt.beginShadows();const st=v.state.shadowsArray;Ft.render(st,w,W),ft===!0&&Rt.endShadows(),this.info.autoReset===!0&&this.info.reset();const rt=M.opaque,Q=M.transmissive;if(v.setupLights(),W.isArrayCamera){const xt=W.cameras;if(Q.length>0)for(let Nt=0,It=xt.length;Nt<It;Nt++){const Pt=xt[Nt];Fo(rt,Q,w,Pt)}de&&Qt.render(w);for(let Nt=0,It=xt.length;Nt<It;Nt++){const Pt=xt[Nt];pr(M,w,Pt,Pt.viewport)}}else Q.length>0&&Fo(rt,Q,w,W),de&&Qt.render(w),pr(M,w,W);H!==null&&(O.updateMultisampleRenderTarget(H),O.updateRenderTargetMipmap(H)),w.isScene===!0&&w.onAfterRender(T,w,W),Ge.resetDefaultState(),D=-1,C=null,U.pop(),U.length>0?(v=U[U.length-1],ft===!0&&Rt.setGlobalState(T.clippingPlanes,v.state.camera)):v=null,L.pop(),L.length>0?M=L[L.length-1]:M=null};function Ms(w,W,st,rt){if(w.visible===!1)return;if(w.layers.test(W.layers)){if(w.isGroup)st=w.renderOrder;else if(w.isLOD)w.autoUpdate===!0&&w.update(W);else if(w.isLight)v.pushLight(w),w.castShadow&&v.pushShadow(w);else if(w.isSprite){if(!w.frustumCulled||K.intersectsSprite(w)){rt&&se.setFromMatrixPosition(w.matrixWorld).applyMatrix4(kt);const Nt=_t.update(w),It=w.material;It.visible&&M.push(w,Nt,It,st,se.z,null)}}else if((w.isMesh||w.isLine||w.isPoints)&&(!w.frustumCulled||K.intersectsObject(w))){const Nt=_t.update(w),It=w.material;if(rt&&(w.boundingSphere!==void 0?(w.boundingSphere===null&&w.computeBoundingSphere(),se.copy(w.boundingSphere.center)):(Nt.boundingSphere===null&&Nt.computeBoundingSphere(),se.copy(Nt.boundingSphere.center)),se.applyMatrix4(w.matrixWorld).applyMatrix4(kt)),Array.isArray(It)){const Pt=Nt.groups;for(let Jt=0,ie=Pt.length;Jt<ie;Jt++){const Zt=Pt[Jt],xe=It[Zt.materialIndex];xe&&xe.visible&&M.push(w,Nt,xe,st,se.z,Zt)}}else It.visible&&M.push(w,Nt,It,st,se.z,null)}}const xt=w.children;for(let Nt=0,It=xt.length;Nt<It;Nt++)Ms(xt[Nt],W,st,rt)}function pr(w,W,st,rt){const Q=w.opaque,xt=w.transmissive,Nt=w.transparent;v.setupLightsView(st),ft===!0&&Rt.setGlobalState(T.clippingPlanes,st),rt&&Yt.viewport(G.copy(rt)),Q.length>0&&Es(Q,W,st),xt.length>0&&Es(xt,W,st),Nt.length>0&&Es(Nt,W,st),Yt.buffers.depth.setTest(!0),Yt.buffers.depth.setMask(!0),Yt.buffers.color.setMask(!0),Yt.setPolygonOffset(!1)}function Fo(w,W,st,rt){if((st.isScene===!0?st.overrideMaterial:null)!==null)return;v.state.transmissionRenderTarget[rt.id]===void 0&&(v.state.transmissionRenderTarget[rt.id]=new dr(1,1,{generateMipmaps:!0,type:he.has("EXT_color_buffer_half_float")||he.has("EXT_color_buffer_float")?Zl:Da,minFilter:er,samples:4,stencilBuffer:c,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Ne.workingColorSpace}));const xt=v.state.transmissionRenderTarget[rt.id],Nt=rt.viewport||G;xt.setSize(Nt.z,Nt.w);const It=T.getRenderTarget();T.setRenderTarget(xt),T.getClearColor(mt),gt=T.getClearAlpha(),gt<1&&T.setClearColor(16777215,.5),T.clear(),de&&Qt.render(st);const Pt=T.toneMapping;T.toneMapping=ys;const Jt=rt.viewport;if(rt.viewport!==void 0&&(rt.viewport=void 0),v.setupLightsView(rt),ft===!0&&Rt.setGlobalState(T.clippingPlanes,rt),Es(w,st,rt),O.updateMultisampleRenderTarget(xt),O.updateRenderTargetMipmap(xt),he.has("WEBGL_multisampled_render_to_texture")===!1){let ie=!1;for(let Zt=0,xe=W.length;Zt<xe;Zt++){const Ce=W[Zt],Qe=Ce.object,We=Ce.geometry,oe=Ce.material,Vt=Ce.group;if(oe.side===Aa&&Qe.layers.test(rt.layers)){const fn=oe.side;oe.side=ei,oe.needsUpdate=!0,wi(Qe,st,rt,We,oe,Vt),oe.side=fn,oe.needsUpdate=!0,ie=!0}}ie===!0&&(O.updateMultisampleRenderTarget(xt),O.updateRenderTargetMipmap(xt))}T.setRenderTarget(It),T.setClearColor(mt,gt),Jt!==void 0&&(rt.viewport=Jt),T.toneMapping=Pt}function Es(w,W,st){const rt=W.isScene===!0?W.overrideMaterial:null;for(let Q=0,xt=w.length;Q<xt;Q++){const Nt=w[Q],It=Nt.object,Pt=Nt.geometry,Jt=rt===null?Nt.material:rt,ie=Nt.group;It.layers.test(st.layers)&&wi(It,W,st,Pt,Jt,ie)}}function wi(w,W,st,rt,Q,xt){w.onBeforeRender(T,W,st,rt,Q,xt),w.modelViewMatrix.multiplyMatrices(st.matrixWorldInverse,w.matrixWorld),w.normalMatrix.getNormalMatrix(w.modelViewMatrix),Q.onBeforeRender(T,W,st,rt,w,xt),Q.transparent===!0&&Q.side===Aa&&Q.forceSinglePass===!1?(Q.side=ei,Q.needsUpdate=!0,T.renderBufferDirect(st,W,rt,Q,w,xt),Q.side=xs,Q.needsUpdate=!0,T.renderBufferDirect(st,W,rt,Q,w,xt),Q.side=Aa):T.renderBufferDirect(st,W,rt,Q,w,xt),w.onAfterRender(T,W,st,rt,Q,xt)}function an(w,W,st){W.isScene!==!0&&(W=He);const rt=Wt.get(w),Q=v.state.lights,xt=v.state.shadowsArray,Nt=Q.state.version,It=jt.getParameters(w,Q.state,xt,W,st),Pt=jt.getProgramCacheKey(It);let Jt=rt.programs;rt.environment=w.isMeshStandardMaterial?W.environment:null,rt.fog=W.fog,rt.envMap=(w.isMeshStandardMaterial?it:R).get(w.envMap||rt.environment),rt.envMapRotation=rt.environment!==null&&w.envMap===null?W.environmentRotation:w.envMapRotation,Jt===void 0&&(w.addEventListener("dispose",ne),Jt=new Map,rt.programs=Jt);let ie=Jt.get(Pt);if(ie!==void 0){if(rt.currentProgram===ie&&rt.lightsStateVersion===Nt)return Ji(w,It),ie}else It.uniforms=jt.getUniforms(w),w.onBeforeCompile(It,T),ie=jt.acquireProgram(It,Pt),Jt.set(Pt,ie),rt.uniforms=It.uniforms;const Zt=rt.uniforms;return(!w.isShaderMaterial&&!w.isRawShaderMaterial||w.clipping===!0)&&(Zt.clippingPlanes=Rt.uniform),Ji(w,It),rt.needsLights=nf(w),rt.lightsStateVersion=Nt,rt.needsLights&&(Zt.ambientLightColor.value=Q.state.ambient,Zt.lightProbe.value=Q.state.probe,Zt.directionalLights.value=Q.state.directional,Zt.directionalLightShadows.value=Q.state.directionalShadow,Zt.spotLights.value=Q.state.spot,Zt.spotLightShadows.value=Q.state.spotShadow,Zt.rectAreaLights.value=Q.state.rectArea,Zt.ltc_1.value=Q.state.rectAreaLTC1,Zt.ltc_2.value=Q.state.rectAreaLTC2,Zt.pointLights.value=Q.state.point,Zt.pointLightShadows.value=Q.state.pointShadow,Zt.hemisphereLights.value=Q.state.hemi,Zt.directionalShadowMap.value=Q.state.directionalShadowMap,Zt.directionalShadowMatrix.value=Q.state.directionalShadowMatrix,Zt.spotShadowMap.value=Q.state.spotShadowMap,Zt.spotLightMatrix.value=Q.state.spotLightMatrix,Zt.spotLightMap.value=Q.state.spotLightMap,Zt.pointShadowMap.value=Q.state.pointShadowMap,Zt.pointShadowMatrix.value=Q.state.pointShadowMatrix),rt.currentProgram=ie,rt.uniformsList=null,ie}function Rn(w){if(w.uniformsList===null){const W=w.currentProgram.getUniforms();w.uniformsList=Xu.seqWithValue(W.seq,w.uniforms)}return w.uniformsList}function Ji(w,W){const st=Wt.get(w);st.outputColorSpace=W.outputColorSpace,st.batching=W.batching,st.batchingColor=W.batchingColor,st.instancing=W.instancing,st.instancingColor=W.instancingColor,st.instancingMorph=W.instancingMorph,st.skinning=W.skinning,st.morphTargets=W.morphTargets,st.morphNormals=W.morphNormals,st.morphColors=W.morphColors,st.morphTargetsCount=W.morphTargetsCount,st.numClippingPlanes=W.numClippingPlanes,st.numIntersection=W.numClipIntersection,st.vertexAlphas=W.vertexAlphas,st.vertexTangents=W.vertexTangents,st.toneMapping=W.toneMapping}function Ho(w,W,st,rt,Q){W.isScene!==!0&&(W=He),O.resetTextureUnits();const xt=W.fog,Nt=rt.isMeshStandardMaterial?W.environment:null,It=H===null?T.outputColorSpace:H.isXRRenderTarget===!0?H.texture.colorSpace:Lo,Pt=(rt.isMeshStandardMaterial?it:R).get(rt.envMap||Nt),Jt=rt.vertexColors===!0&&!!st.attributes.color&&st.attributes.color.itemSize===4,ie=!!st.attributes.tangent&&(!!rt.normalMap||rt.anisotropy>0),Zt=!!st.morphAttributes.position,xe=!!st.morphAttributes.normal,Ce=!!st.morphAttributes.color;let Qe=ys;rt.toneMapped&&(H===null||H.isXRRenderTarget===!0)&&(Qe=T.toneMapping);const We=st.morphAttributes.position||st.morphAttributes.normal||st.morphAttributes.color,oe=We!==void 0?We.length:0,Vt=Wt.get(rt),fn=v.state.lights;if(ft===!0&&(Tt===!0||w!==C)){const vn=w===C&&rt.id===D;Rt.setState(rt,w,vn)}let we=!1;rt.version===Vt.__version?(Vt.needsLights&&Vt.lightsStateVersion!==fn.state.version||Vt.outputColorSpace!==It||Q.isBatchedMesh&&Vt.batching===!1||!Q.isBatchedMesh&&Vt.batching===!0||Q.isBatchedMesh&&Vt.batchingColor===!0&&Q.colorTexture===null||Q.isBatchedMesh&&Vt.batchingColor===!1&&Q.colorTexture!==null||Q.isInstancedMesh&&Vt.instancing===!1||!Q.isInstancedMesh&&Vt.instancing===!0||Q.isSkinnedMesh&&Vt.skinning===!1||!Q.isSkinnedMesh&&Vt.skinning===!0||Q.isInstancedMesh&&Vt.instancingColor===!0&&Q.instanceColor===null||Q.isInstancedMesh&&Vt.instancingColor===!1&&Q.instanceColor!==null||Q.isInstancedMesh&&Vt.instancingMorph===!0&&Q.morphTexture===null||Q.isInstancedMesh&&Vt.instancingMorph===!1&&Q.morphTexture!==null||Vt.envMap!==Pt||rt.fog===!0&&Vt.fog!==xt||Vt.numClippingPlanes!==void 0&&(Vt.numClippingPlanes!==Rt.numPlanes||Vt.numIntersection!==Rt.numIntersection)||Vt.vertexAlphas!==Jt||Vt.vertexTangents!==ie||Vt.morphTargets!==Zt||Vt.morphNormals!==xe||Vt.morphColors!==Ce||Vt.toneMapping!==Qe||Vt.morphTargetsCount!==oe)&&(we=!0):(we=!0,Vt.__version=rt.version);let Hn=Vt.currentProgram;we===!0&&(Hn=an(rt,W,Q));let $i=!1,Mn=!1,Ts=!1;const pe=Hn.getUniforms(),Pn=Vt.uniforms;if(Yt.useProgram(Hn.program)&&($i=!0,Mn=!0,Ts=!0),rt.id!==D&&(D=rt.id,Mn=!0),$i||C!==w){Yt.buffers.depth.getReversed()?(St.copy(w.projectionMatrix),Z1(St),K1(St),pe.setValue(k,"projectionMatrix",St)):pe.setValue(k,"projectionMatrix",w.projectionMatrix),pe.setValue(k,"viewMatrix",w.matrixWorldInverse);const ln=pe.map.cameraPosition;ln!==void 0&&ln.setValue(k,Gt.setFromMatrixPosition(w.matrixWorld)),ve.logarithmicDepthBuffer&&pe.setValue(k,"logDepthBufFC",2/(Math.log(w.far+1)/Math.LN2)),(rt.isMeshPhongMaterial||rt.isMeshToonMaterial||rt.isMeshLambertMaterial||rt.isMeshBasicMaterial||rt.isMeshStandardMaterial||rt.isShaderMaterial)&&pe.setValue(k,"isOrthographic",w.isOrthographicCamera===!0),C!==w&&(C=w,Mn=!0,Ts=!0)}if(Q.isSkinnedMesh){pe.setOptional(k,Q,"bindMatrix"),pe.setOptional(k,Q,"bindMatrixInverse");const vn=Q.skeleton;vn&&(vn.boneTexture===null&&vn.computeBoneTexture(),pe.setValue(k,"boneTexture",vn.boneTexture,O))}Q.isBatchedMesh&&(pe.setOptional(k,Q,"batchingTexture"),pe.setValue(k,"batchingTexture",Q._matricesTexture,O),pe.setOptional(k,Q,"batchingIdTexture"),pe.setValue(k,"batchingIdTexture",Q._indirectTexture,O),pe.setOptional(k,Q,"batchingColorTexture"),Q._colorsTexture!==null&&pe.setValue(k,"batchingColorTexture",Q._colorsTexture,O));const Gn=st.morphAttributes;if((Gn.position!==void 0||Gn.normal!==void 0||Gn.color!==void 0)&&qt.update(Q,st,Hn),(Mn||Vt.receiveShadow!==Q.receiveShadow)&&(Vt.receiveShadow=Q.receiveShadow,pe.setValue(k,"receiveShadow",Q.receiveShadow)),rt.isMeshGouraudMaterial&&rt.envMap!==null&&(Pn.envMap.value=Pt,Pn.flipEnvMap.value=Pt.isCubeTexture&&Pt.isRenderTargetTexture===!1?-1:1),rt.isMeshStandardMaterial&&rt.envMap===null&&W.environment!==null&&(Pn.envMapIntensity.value=W.environmentIntensity),Mn&&(pe.setValue(k,"toneMappingExposure",T.toneMappingExposure),Vt.needsLights&&ef(Pn,Ts),xt&&rt.fog===!0&&Dt.refreshFogUniforms(Pn,xt),Dt.refreshMaterialUniforms(Pn,rt,J,$,v.state.transmissionRenderTarget[w.id]),Xu.upload(k,Rn(Vt),Pn,O)),rt.isShaderMaterial&&rt.uniformsNeedUpdate===!0&&(Xu.upload(k,Rn(Vt),Pn,O),rt.uniformsNeedUpdate=!1),rt.isSpriteMaterial&&pe.setValue(k,"center",Q.center),pe.setValue(k,"modelViewMatrix",Q.modelViewMatrix),pe.setValue(k,"normalMatrix",Q.normalMatrix),pe.setValue(k,"modelMatrix",Q.matrixWorld),rt.isShaderMaterial||rt.isRawShaderMaterial){const vn=rt.uniformsGroups;for(let ln=0,mr=vn.length;ln<mr;ln++){const Gi=vn[ln];q.update(Gi,Hn),q.bind(Gi,Hn)}}return Hn}function ef(w,W){w.ambientLightColor.needsUpdate=W,w.lightProbe.needsUpdate=W,w.directionalLights.needsUpdate=W,w.directionalLightShadows.needsUpdate=W,w.pointLights.needsUpdate=W,w.pointLightShadows.needsUpdate=W,w.spotLights.needsUpdate=W,w.spotLightShadows.needsUpdate=W,w.rectAreaLights.needsUpdate=W,w.hemisphereLights.needsUpdate=W}function nf(w){return w.isMeshLambertMaterial||w.isMeshToonMaterial||w.isMeshPhongMaterial||w.isMeshStandardMaterial||w.isShadowMaterial||w.isShaderMaterial&&w.lights===!0}this.getActiveCubeFace=function(){return I},this.getActiveMipmapLevel=function(){return P},this.getRenderTarget=function(){return H},this.setRenderTargetTextures=function(w,W,st){Wt.get(w.texture).__webglTexture=W,Wt.get(w.depthTexture).__webglTexture=st;const rt=Wt.get(w);rt.__hasExternalTextures=!0,rt.__autoAllocateDepthBuffer=st===void 0,rt.__autoAllocateDepthBuffer||he.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),rt.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(w,W){const st=Wt.get(w);st.__webglFramebuffer=W,st.__useDefaultFramebuffer=W===void 0},this.setRenderTarget=function(w,W=0,st=0){H=w,I=W,P=st;let rt=!0,Q=null,xt=!1,Nt=!1;if(w){const Pt=Wt.get(w);if(Pt.__useDefaultFramebuffer!==void 0)Yt.bindFramebuffer(k.FRAMEBUFFER,null),rt=!1;else if(Pt.__webglFramebuffer===void 0)O.setupRenderTarget(w);else if(Pt.__hasExternalTextures)O.rebindTextures(w,Wt.get(w.texture).__webglTexture,Wt.get(w.depthTexture).__webglTexture);else if(w.depthBuffer){const Zt=w.depthTexture;if(Pt.__boundDepthTexture!==Zt){if(Zt!==null&&Wt.has(Zt)&&(w.width!==Zt.image.width||w.height!==Zt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");O.setupDepthRenderbuffer(w)}}const Jt=w.texture;(Jt.isData3DTexture||Jt.isDataArrayTexture||Jt.isCompressedArrayTexture)&&(Nt=!0);const ie=Wt.get(w).__webglFramebuffer;w.isWebGLCubeRenderTarget?(Array.isArray(ie[W])?Q=ie[W][st]:Q=ie[W],xt=!0):w.samples>0&&O.useMultisampledRTT(w)===!1?Q=Wt.get(w).__webglMultisampledFramebuffer:Array.isArray(ie)?Q=ie[st]:Q=ie,G.copy(w.viewport),ot.copy(w.scissor),lt=w.scissorTest}else G.copy(z).multiplyScalar(J).floor(),ot.copy(at).multiplyScalar(J).floor(),lt=Mt;if(Yt.bindFramebuffer(k.FRAMEBUFFER,Q)&&rt&&Yt.drawBuffers(w,Q),Yt.viewport(G),Yt.scissor(ot),Yt.setScissorTest(lt),xt){const Pt=Wt.get(w.texture);k.framebufferTexture2D(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_CUBE_MAP_POSITIVE_X+W,Pt.__webglTexture,st)}else if(Nt){const Pt=Wt.get(w.texture),Jt=W||0;k.framebufferTextureLayer(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,Pt.__webglTexture,st||0,Jt)}D=-1},this.readRenderTargetPixels=function(w,W,st,rt,Q,xt,Nt){if(!(w&&w.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let It=Wt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Nt!==void 0&&(It=It[Nt]),It){Yt.bindFramebuffer(k.FRAMEBUFFER,It);try{const Pt=w.texture,Jt=Pt.format,ie=Pt.type;if(!ve.textureFormatReadable(Jt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ve.textureTypeReadable(ie)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}W>=0&&W<=w.width-rt&&st>=0&&st<=w.height-Q&&k.readPixels(W,st,rt,Q,re.convert(Jt),re.convert(ie),xt)}finally{const Pt=H!==null?Wt.get(H).__webglFramebuffer:null;Yt.bindFramebuffer(k.FRAMEBUFFER,Pt)}}},this.readRenderTargetPixelsAsync=async function(w,W,st,rt,Q,xt,Nt){if(!(w&&w.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let It=Wt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Nt!==void 0&&(It=It[Nt]),It){const Pt=w.texture,Jt=Pt.format,ie=Pt.type;if(!ve.textureFormatReadable(Jt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ve.textureTypeReadable(ie))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(W>=0&&W<=w.width-rt&&st>=0&&st<=w.height-Q){Yt.bindFramebuffer(k.FRAMEBUFFER,It);const Zt=k.createBuffer();k.bindBuffer(k.PIXEL_PACK_BUFFER,Zt),k.bufferData(k.PIXEL_PACK_BUFFER,xt.byteLength,k.STREAM_READ),k.readPixels(W,st,rt,Q,re.convert(Jt),re.convert(ie),0);const xe=H!==null?Wt.get(H).__webglFramebuffer:null;Yt.bindFramebuffer(k.FRAMEBUFFER,xe);const Ce=k.fenceSync(k.SYNC_GPU_COMMANDS_COMPLETE,0);return k.flush(),await Q1(k,Ce,4),k.bindBuffer(k.PIXEL_PACK_BUFFER,Zt),k.getBufferSubData(k.PIXEL_PACK_BUFFER,0,xt),k.deleteBuffer(Zt),k.deleteSync(Ce),xt}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(w,W=null,st=0){w.isTexture!==!0&&(lo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),W=arguments[0]||null,w=arguments[1]);const rt=Math.pow(2,-st),Q=Math.floor(w.image.width*rt),xt=Math.floor(w.image.height*rt),Nt=W!==null?W.x:0,It=W!==null?W.y:0;O.setTexture2D(w,0),k.copyTexSubImage2D(k.TEXTURE_2D,st,0,0,Nt,It,Q,xt),Yt.unbindTexture()};const nc=k.createFramebuffer(),bs=k.createFramebuffer();this.copyTextureToTexture=function(w,W,st=null,rt=null,Q=0,xt=null){w.isTexture!==!0&&(lo("WebGLRenderer: copyTextureToTexture function signature has changed."),rt=arguments[0]||null,w=arguments[1],W=arguments[2],xt=arguments[3]||0,st=null),xt===null&&(Q!==0?(lo("WebGLRenderer: copyTextureToTexture function signature has changed to support src and dst mipmap levels."),xt=Q,Q=0):xt=0);let Nt,It,Pt,Jt,ie,Zt,xe,Ce,Qe;const We=w.isCompressedTexture?w.mipmaps[xt]:w.image;if(st!==null)Nt=st.max.x-st.min.x,It=st.max.y-st.min.y,Pt=st.isBox3?st.max.z-st.min.z:1,Jt=st.min.x,ie=st.min.y,Zt=st.isBox3?st.min.z:0;else{const Gn=Math.pow(2,-Q);Nt=Math.floor(We.width*Gn),It=Math.floor(We.height*Gn),w.isDataArrayTexture?Pt=We.depth:w.isData3DTexture?Pt=Math.floor(We.depth*Gn):Pt=1,Jt=0,ie=0,Zt=0}rt!==null?(xe=rt.x,Ce=rt.y,Qe=rt.z):(xe=0,Ce=0,Qe=0);const oe=re.convert(W.format),Vt=re.convert(W.type);let fn;W.isData3DTexture?(O.setTexture3D(W,0),fn=k.TEXTURE_3D):W.isDataArrayTexture||W.isCompressedArrayTexture?(O.setTexture2DArray(W,0),fn=k.TEXTURE_2D_ARRAY):(O.setTexture2D(W,0),fn=k.TEXTURE_2D),k.pixelStorei(k.UNPACK_FLIP_Y_WEBGL,W.flipY),k.pixelStorei(k.UNPACK_PREMULTIPLY_ALPHA_WEBGL,W.premultiplyAlpha),k.pixelStorei(k.UNPACK_ALIGNMENT,W.unpackAlignment);const we=k.getParameter(k.UNPACK_ROW_LENGTH),Hn=k.getParameter(k.UNPACK_IMAGE_HEIGHT),$i=k.getParameter(k.UNPACK_SKIP_PIXELS),Mn=k.getParameter(k.UNPACK_SKIP_ROWS),Ts=k.getParameter(k.UNPACK_SKIP_IMAGES);k.pixelStorei(k.UNPACK_ROW_LENGTH,We.width),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,We.height),k.pixelStorei(k.UNPACK_SKIP_PIXELS,Jt),k.pixelStorei(k.UNPACK_SKIP_ROWS,ie),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Zt);const pe=w.isDataArrayTexture||w.isData3DTexture,Pn=W.isDataArrayTexture||W.isData3DTexture;if(w.isDepthTexture){const Gn=Wt.get(w),vn=Wt.get(W),ln=Wt.get(Gn.__renderTarget),mr=Wt.get(vn.__renderTarget);Yt.bindFramebuffer(k.READ_FRAMEBUFFER,ln.__webglFramebuffer),Yt.bindFramebuffer(k.DRAW_FRAMEBUFFER,mr.__webglFramebuffer);for(let Gi=0;Gi<Pt;Gi++)pe&&(k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Wt.get(w).__webglTexture,Q,Zt+Gi),k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Wt.get(W).__webglTexture,xt,Qe+Gi)),k.blitFramebuffer(Jt,ie,Nt,It,xe,Ce,Nt,It,k.DEPTH_BUFFER_BIT,k.NEAREST);Yt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Yt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else if(Q!==0||w.isRenderTargetTexture||Wt.has(w)){const Gn=Wt.get(w),vn=Wt.get(W);Yt.bindFramebuffer(k.READ_FRAMEBUFFER,nc),Yt.bindFramebuffer(k.DRAW_FRAMEBUFFER,bs);for(let ln=0;ln<Pt;ln++)pe?k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Gn.__webglTexture,Q,Zt+ln):k.framebufferTexture2D(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,Gn.__webglTexture,Q),Pn?k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,vn.__webglTexture,xt,Qe+ln):k.framebufferTexture2D(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,vn.__webglTexture,xt),Q!==0?k.blitFramebuffer(Jt,ie,Nt,It,xe,Ce,Nt,It,k.COLOR_BUFFER_BIT,k.NEAREST):Pn?k.copyTexSubImage3D(fn,xt,xe,Ce,Qe+ln,Jt,ie,Nt,It):k.copyTexSubImage2D(fn,xt,xe,Ce,Jt,ie,Nt,It);Yt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Yt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else Pn?w.isDataTexture||w.isData3DTexture?k.texSubImage3D(fn,xt,xe,Ce,Qe,Nt,It,Pt,oe,Vt,We.data):W.isCompressedArrayTexture?k.compressedTexSubImage3D(fn,xt,xe,Ce,Qe,Nt,It,Pt,oe,We.data):k.texSubImage3D(fn,xt,xe,Ce,Qe,Nt,It,Pt,oe,Vt,We):w.isDataTexture?k.texSubImage2D(k.TEXTURE_2D,xt,xe,Ce,Nt,It,oe,Vt,We.data):w.isCompressedTexture?k.compressedTexSubImage2D(k.TEXTURE_2D,xt,xe,Ce,We.width,We.height,oe,We.data):k.texSubImage2D(k.TEXTURE_2D,xt,xe,Ce,Nt,It,oe,Vt,We);k.pixelStorei(k.UNPACK_ROW_LENGTH,we),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Hn),k.pixelStorei(k.UNPACK_SKIP_PIXELS,$i),k.pixelStorei(k.UNPACK_SKIP_ROWS,Mn),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Ts),xt===0&&W.generateMipmaps&&k.generateMipmap(fn),Yt.unbindTexture()},this.copyTextureToTexture3D=function(w,W,st=null,rt=null,Q=0){return w.isTexture!==!0&&(lo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),st=arguments[0]||null,rt=arguments[1]||null,w=arguments[2],W=arguments[3],Q=arguments[4]||0),lo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(w,W,st,rt,Q)},this.initRenderTarget=function(w){Wt.get(w).__webglFramebuffer===void 0&&O.setupRenderTarget(w)},this.initTexture=function(w){w.isCubeTexture?O.setTextureCube(w,0):w.isData3DTexture?O.setTexture3D(w,0):w.isDataArrayTexture||w.isCompressedArrayTexture?O.setTexture2DArray(w,0):O.setTexture2D(w,0),Yt.unbindTexture()},this.resetState=function(){I=0,P=0,H=null,Yt.reset(),Ge.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ca}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const i=this.getContext();i.drawingBufferColorspace=Ne._getDrawingBufferColorSpace(t),i.unpackColorSpace=Ne._getUnpackColorSpace()}}function Cx({mode:r,health:t,activityLevel:i,confidence:s,servers:l}){const c=Pe.useRef(null);return Pe.useEffect(()=>{const h=c.current;if(!h)return;const d=window.matchMedia("(prefers-reduced-motion: reduce)").matches,m=new xb,p=new pi(42,h.clientWidth/h.clientHeight,.1,100);p.position.set(0,0,7.4);const g=new mC({antialias:!0,alpha:!0});g.setPixelRatio(Math.min(window.devicePixelRatio,2)),g.setSize(h.clientWidth,h.clientHeight),h.appendChild(g.domElement);const _=t==="OFFLINE"?16735603:t==="DEGRADED"?16758861:2741247,x=new co;m.add(x);const S=new Ri(new fm(1.25,4),new Fl({color:_,wireframe:!0,transparent:!0,opacity:.55}));x.add(S);const E=new Ri(new dm(1.7,s==="low"?.012:.018,12,128),new Fl({color:s==="low"?16758861:9141503,transparent:!0,opacity:.78}));E.rotation.x=Math.PI/2.4,x.add(E);const b=new Yp({color:9347256,transparent:!0,opacity:.32});for(let I=0;I<3;I+=1){const H=new bb(0,0,2.05+I*.34,1.08+I*.22,0,Math.PI*2).getPoints(96).map(C=>new Y(C.x,C.y,0)),D=new kv(new mi().setFromPoints(H),b);D.rotation.x=Math.PI/(2.6+I*.35),D.rotation.y=I*.58,x.add(D)}const M=new co,v=l.slice(0,8);v.forEach((I,P)=>{const H=P/Math.max(v.length,1)*Math.PI*2,D=2.9,C=I.status==="ONLINE"?3003560:I.status==="DEGRADED"?16758861:16735603,G=new Ri(new hm(.07,16,16),new Fl({color:C}));G.position.set(Math.cos(H)*D,Math.sin(H)*1.2,Math.sin(H)*D*.3),M.add(G);const ot=new kv(new mi().setFromPoints([new Y(0,0,0),G.position.clone()]),new Yp({color:C,transparent:!0,opacity:.28}));M.add(ot)}),x.add(M);const L=new Db(16777215,1.1);L.position.set(0,0,4),m.add(L);let U=0;const T=()=>{if(U=requestAnimationFrame(T),!d){const I=.002+Math.min(i,4)*.0013;x.rotation.y+=I,S.rotation.x+=I*.65,E.rotation.z+=I*.45}g.render(m,p)};T();const V=()=>{h&&(p.aspect=h.clientWidth/h.clientHeight,p.updateProjectionMatrix(),g.setSize(h.clientWidth,h.clientHeight))};return window.addEventListener("resize",V),()=>{cancelAnimationFrame(U),window.removeEventListener("resize",V),g.dispose(),h.removeChild(g.domElement)}},[i,s,t,l]),N.jsxs("div",{children:[N.jsx("div",{ref:c,className:"core-canvas",role:"img","aria-label":`AEGIS core sphere. Mode ${r}, health ${t}.`}),N.jsxs("div",{className:"muted mono",style:{marginTop:8},children:["Mode: ",r," / Health: ",t," / Confidence: ",s]})]})}function gC({overview:r}){const t=r.core.data,i=r.servers.data.items||[],s=r.current_task.data,l=r.usage.data;return N.jsxs(N.Fragment,{children:[N.jsx(a1,{items:r.attention.data.items||[]}),N.jsxs("div",{className:"grid grid--command",children:[N.jsxs("section",{className:"panel core-card",children:[N.jsx(Cx,{mode:String(t.mode||"IDLE"),health:String(t.health||"ONLINE"),activityLevel:Number(t.activity_level||1),confidence:String(t.confidence||"medium"),servers:i}),N.jsxs("div",{className:"grid",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"Current Operation"}),N.jsx(fr,{status:String(t.mode||"IDLE")})]}),N.jsxs("div",{children:[N.jsx("h3",{children:s.title}),N.jsx("p",{className:"muted",children:s.current_action||s.next_action||"AEGIS is waiting for a meaningful signal or user request."})]}),N.jsxs("div",{className:"stat-grid",children:[N.jsx(Iu,{icon:N.jsx(Xy,{size:18}),label:"Activity",value:String(t.activity_level??0)}),N.jsx(Iu,{icon:N.jsx(PE,{size:18}),label:"Confidence",value:String(t.confidence||"unknown")}),N.jsx(Iu,{icon:N.jsx(VE,{size:18}),label:"Approvals",value:String(t.pending_approval_count??0)}),N.jsx(Iu,{icon:N.jsx(GE,{size:18}),label:"Freshness",value:r.freshness.stale?"STALE":"LIVE"})]})]})]}),N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"AI State"}),N.jsx($s,{...Bu(r.core)})]}),N.jsxs("div",{className:"grid",children:[N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Active goal"}),N.jsx("b",{style:{fontSize:16},children:String(t.active_goal||"No active goal")})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Attention level"}),N.jsx("b",{style:{fontSize:16},children:String(t.attention_level||"normal")})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"LLM usage"}),N.jsx("b",{style:{fontSize:16},children:String(l.summary||l.total_tokens||"Audit-backed")})]})]})]})]}),N.jsxs("div",{className:"grid grid--three",style:{marginTop:16},children:[N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"Server Health"}),N.jsx($s,{...Bu(r.servers)})]}),N.jsx("div",{className:"grid",children:i.slice(0,6).map(c=>N.jsxs("div",{className:"list-row",children:[N.jsxs("div",{children:[N.jsx("strong",{children:c.server_id}),N.jsx("div",{className:"muted",children:c.status_detail||c.mode||"No detail"})]}),N.jsx(fr,{status:c.status,detail:c.recovery_hint})]},c.server_id))})]}),N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"Notifications"}),N.jsx($s,{...Bu(r.notifications)})]}),N.jsxs("div",{className:"grid",children:[(r.notifications.data.recent||[]).slice(0,5).map((c,h)=>N.jsx("div",{className:"list-row",children:N.jsxs("div",{children:[N.jsx("strong",{children:String(c.title||"Notification")}),N.jsx("div",{className:"muted",children:String(c.message||c.severity||"")})]})},String(c.notification_id||c.id||h))),(r.notifications.data.recent||[]).length===0?N.jsx("p",{className:"muted",children:"No recent notifications."}):null]})]}),N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"Memory & Mind"}),N.jsx($s,{...Bu(r.mind_summary)})]}),N.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap",margin:0},children:JSON.stringify(r.mind_summary.data,null,2).slice(0,900)})]})]})]})}function Iu({icon:r,label:t,value:i}){return N.jsxs("div",{className:"stat",children:[N.jsxs("span",{className:"muted",children:[r," ",t]}),N.jsx("b",{children:i})]})}function Bu(r){return{generatedAt:r.generated_at,sourceUpdatedAt:r.source_updated_at,stale:r.stale}}function _C({overview:r}){const t=r.core.data,i=r.servers.data.items||[],s=r.current_task.data,l=r.approvals.data.pending||[];return N.jsxs("main",{className:"display-shell",children:[N.jsxs("header",{className:"top-bar",children:[N.jsxs("div",{className:"brand",children:[N.jsx("span",{className:"brand__name",children:"AEGIS"}),N.jsx("span",{className:"brand__sub",children:"Dedicated Display / Read Only"})]}),N.jsx(fr,{status:String(t.health||"ONLINE")})]}),N.jsxs("section",{className:"display-grid",children:[N.jsxs("aside",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"AI State"})}),N.jsxs("div",{className:"grid",children:[N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Mode"}),N.jsx("b",{children:String(t.mode||"IDLE")})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Goal"}),N.jsx("b",{style:{fontSize:16},children:String(t.active_goal||"No active goal")})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Confidence"}),N.jsx("b",{children:String(t.confidence||"medium")})]}),N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Task"}),N.jsx("b",{style:{fontSize:16},children:s.title})]})]})]}),N.jsx("section",{className:"display-core",children:N.jsx(Cx,{mode:String(t.mode||"IDLE"),health:String(t.health||"ONLINE"),activityLevel:Number(t.activity_level||1),confidence:String(t.confidence||"medium"),servers:i})}),N.jsxs("aside",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"Attention"})}),N.jsxs("div",{className:"grid",children:[l.slice(0,3).map(c=>N.jsx("div",{className:"attention-item","data-severity":"warning",children:N.jsxs("div",{children:[N.jsx("strong",{children:"Approval"}),N.jsx("div",{className:"muted",children:c.summary||c.capability_id})]})},c.approval_id)),(r.attention.data.items||[]).filter(c=>c.kind!=="approval").slice(0,5).map(c=>N.jsx("div",{className:"attention-item","data-severity":c.severity,children:N.jsxs("div",{children:[N.jsx("strong",{children:c.title}),N.jsx("div",{className:"muted",children:c.message})]})},c.id)),l.length===0&&(r.attention.data.items||[]).length===0?N.jsx("div",{className:"muted",children:"No immediate attention required."}):null]})]})]}),N.jsx("footer",{className:"panel",style:{marginTop:24},children:N.jsx("div",{className:"grid grid--three",children:i.slice(0,6).map(c=>N.jsxs("div",{className:"list-row",children:[N.jsxs("div",{children:[N.jsx("strong",{children:c.server_id}),N.jsx("div",{className:"muted",children:c.status_detail||c.recovery_hint||c.mode})]}),N.jsx(fr,{status:c.status})]},c.server_id))})})]})}function vC({overview:r}){return N.jsxs("div",{className:"grid grid--three",children:[N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"Mind Summary"})}),N.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(r.mind_summary.data,null,2)})]}),N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"User State"})}),N.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(r.user_state.data,null,2)})]}),N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"Commitments"})}),N.jsx("pre",{className:"mono muted",style:{whiteSpace:"pre-wrap"},children:JSON.stringify(r.commitments.data,null,2)})]})]})}function yC(){return N.jsxs("div",{className:"grid grid--three",children:[N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsxs("h2",{children:[N.jsx(Yy,{size:18})," Security"]})}),N.jsx("p",{className:"muted",children:"Passkey-only sessions and fresh authentication are enforced by the backend middleware."}),N.jsxs("a",{className:"primary-button",href:"/dashboard/security/passkeys",children:[N.jsx(XE,{size:16})," Passkeys"]})]}),N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsxs("h2",{children:[N.jsx(YE,{size:18})," Existing Settings"]})}),N.jsx("p",{className:"muted",children:"Detailed legacy-compatible settings APIs remain available after authentication."}),N.jsx("a",{className:"ghost-button",href:"/api/settings",children:"Settings API"})]}),N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsx("h2",{children:"Display"})}),N.jsx("p",{className:"muted",children:"The dedicated display opens read-only status and presentation UI, not this admin dashboard."}),N.jsx("a",{className:"ghost-button",href:"/display",children:"Open Display"})]})]})}function xC({overview:r}){const t=r.servers.data.items||[];return N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsxs("div",{children:[N.jsx("h2",{children:"Systems"}),N.jsx("div",{className:"muted",children:"AI, PC, Android, Browser, Room, and Dev status."})]}),N.jsx($s,{generatedAt:r.servers.generated_at,sourceUpdatedAt:r.servers.source_updated_at,stale:r.servers.stale})]}),N.jsx("div",{className:"grid",children:t.map(i=>N.jsxs("article",{className:"list-row",children:[N.jsxs("div",{children:[N.jsx("strong",{children:i.server_id}),N.jsxs("div",{className:"muted",children:[i.server_type||"service"," / ",i.mode||"unknown"," / ",i.host||"host",":",i.port||"-"]}),N.jsx("div",{className:"muted",children:i.status_detail||i.degraded_reason||i.recovery_hint||"No recovery action needed."})]}),N.jsx(fr,{status:i.status,detail:i.recovery_hint})]},i.server_id))})]})}function SC({overview:r}){const t=r.current_task.data;return N.jsxs("section",{className:"panel",children:[N.jsx("div",{className:"panel__header",children:N.jsxs("div",{children:[N.jsx("h2",{children:"Work"}),N.jsx("div",{className:"muted",children:"Active task, waiting state, and execution phase."})]})}),N.jsxs("div",{className:"grid",children:[N.jsxs("div",{className:"stat",children:[N.jsx("span",{className:"muted",children:"Current task"}),N.jsx("b",{style:{fontSize:18},children:t.title}),N.jsx("p",{className:"muted",children:t.current_action||t.blocked_reason||"No active execution."})]}),(t.steps||[]).map((i,s)=>N.jsx("div",{className:"list-row",children:N.jsxs("div",{children:[N.jsx("strong",{children:String(i.description||i.capability_id||`Step ${s+1}`)}),N.jsx("div",{className:"muted",children:String(i.status||"unknown")})]})},String(i.step_id||s)))]})]})}const vy=[{id:"command",label:"Command Center",icon:kE,path:"/dashboard"},{id:"work",label:"Work",icon:HE,path:"/dashboard/work"},{id:"approvals",label:"Approvals",icon:Yy,path:"/dashboard/approvals"},{id:"systems",label:"Systems",icon:jE,path:"/dashboard/systems"},{id:"mind",label:"Mind & Memory",icon:OE,path:"/dashboard/mind"},{id:"activity",label:"Activity",icon:Xy,path:"/dashboard/activity"},{id:"settings",label:"Settings",icon:WE,path:"/settings"}];function MC(){var g;const r=window.location.pathname.startsWith("/display"),t=Gy(),[i,s]=Pe.useState(window.location.pathname==="/chat"),l=Pe.useMemo(()=>bC(window.location.pathname),[]),[c,h]=Pe.useState(l),d=DE({queryKey:["ui-overview",r?"display":"dashboard"],queryFn:()=>ZE(r?"display":"dashboard"),refetchInterval:r?15e3:3e4}),m=Pe.useCallback(()=>{t.invalidateQueries({queryKey:["ui-overview"]})},[t]);if($E(m,!r),d.isLoading)return N.jsx(TC,{displayMode:r});if(d.isError||!d.data)return N.jsx(AC,{message:d.error instanceof Error?d.error.message:"Overview unavailable"});if(r)return N.jsx(_C,{overview:d.data});const p=d.data;return N.jsxs("div",{className:"app-shell",children:[N.jsxs("aside",{className:"side-nav",children:[N.jsxs("div",{className:"brand",children:[N.jsx("span",{className:"brand__name",children:"AEGIS"}),N.jsx("span",{className:"brand__sub",children:"Operational Console"})]}),N.jsx("nav",{className:"nav-list","aria-label":"Primary",children:vy.map(_=>{const x=_.icon;return N.jsxs("button",{className:"nav-button","aria-current":c===_.id?"page":void 0,onClick:()=>{h(_.id),window.history.pushState(null,"",_.path)},children:[N.jsx(x,{size:17,"aria-hidden":"true"}),_.label]},_.id)})})]}),N.jsxs("main",{className:"content",children:[N.jsxs("header",{className:"top-bar",children:[N.jsxs("div",{className:"page-title",children:[N.jsx("h1",{children:((g=vy.find(_=>_.id===c))==null?void 0:g.label)||"AEGIS"}),N.jsx("p",{children:"Live overview generated by Runtime managers, Policy, Approval, and Status services."})]}),N.jsxs("div",{style:{display:"flex",gap:12,alignItems:"center"},children:[N.jsx(fr,{status:String(p.core.data.health||"ONLINE")}),N.jsx($s,{generatedAt:p.generated_at,sourceUpdatedAt:p.freshness.source_updated_at,stale:p.freshness.stale}),N.jsx("button",{className:"icon-button",onClick:()=>s(!0),title:"Open chat",children:N.jsx(qy,{size:17,"aria-hidden":"true"})})]})]}),N.jsx(EC,{page:c,overview:p})]}),N.jsx(t1,{open:i,onClose:()=>s(!1)})]})}function EC({page:r,overview:t}){return r==="work"?N.jsx(SC,{overview:t}):r==="approvals"?N.jsx(i1,{overview:t}):r==="systems"?N.jsx(xC,{overview:t}):r==="mind"?N.jsx(vC,{overview:t}):r==="activity"?N.jsx(e1,{overview:t}):r==="settings"?N.jsx(yC,{}):N.jsx(gC,{overview:t})}function bC(r){return r.includes("/work")?"work":r.includes("/approvals")?"approvals":r.includes("/systems")||r.includes("/servers")?"systems":r.includes("/mind")||r.includes("/memory")?"mind":r.includes("/activity")||r.includes("/audit")?"activity":r.includes("/settings")?"settings":"command"}function TC({displayMode:r}){return N.jsx("main",{className:r?"display-shell":"app-shell",style:{display:"grid",placeItems:"center"},children:N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"Loading AEGIS UI"}),N.jsx(jy,{size:18})]}),N.jsx("p",{className:"muted",children:"Waiting for the normalized overview service."})]})})}function AC({message:r}){return N.jsx("main",{className:"display-shell",style:{display:"grid",placeItems:"center"},children:N.jsxs("section",{className:"panel",children:[N.jsxs("div",{className:"panel__header",children:[N.jsx("h2",{children:"AEGIS UI unavailable"}),N.jsx(fr,{status:"OFFLINE"})]}),N.jsx("p",{className:"muted",children:r})]})})}const RC=new _E({defaultOptions:{queries:{retry:1,staleTime:1e4}}});jM.createRoot(document.getElementById("root")).render(N.jsx(IM.StrictMode,{children:N.jsx(vE,{client:RC,children:N.jsx(MC,{})})}));
