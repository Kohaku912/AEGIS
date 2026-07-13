var v0=a=>{throw TypeError(a)};var Th=(a,t,n)=>t.has(a)||v0("Cannot "+n);var X=(a,t,n)=>(Th(a,t,"read from private field"),n?n.call(a):t.get(a)),te=(a,t,n)=>t.has(a)?v0("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(a):t.set(a,n),zt=(a,t,n,s)=>(Th(a,t,"write to private field"),s?s.call(a,n):t.set(a,n),n),Ae=(a,t,n)=>(Th(a,t,"access private method"),n);var bu=(a,t,n,s)=>({set _(l){zt(a,t,l,n)},get _(){return X(a,t,s)}});(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const l of document.querySelectorAll('link[rel="modulepreload"]'))s(l);new MutationObserver(l=>{for(const c of l)if(c.type==="childList")for(const f of c.addedNodes)f.tagName==="LINK"&&f.rel==="modulepreload"&&s(f)}).observe(document,{childList:!0,subtree:!0});function n(l){const c={};return l.integrity&&(c.integrity=l.integrity),l.referrerPolicy&&(c.referrerPolicy=l.referrerPolicy),l.crossOrigin==="use-credentials"?c.credentials="include":l.crossOrigin==="anonymous"?c.credentials="omit":c.credentials="same-origin",c}function s(l){if(l.ep)return;l.ep=!0;const c=n(l);fetch(l.href,c)}})();function tx(a){return a&&a.__esModule&&Object.prototype.hasOwnProperty.call(a,"default")?a.default:a}var Ah={exports:{}},Fl={};/**
 * @license React
 * react-jsx-runtime.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var _0;function M1(){if(_0)return Fl;_0=1;var a=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function n(s,l,c){var f=null;if(c!==void 0&&(f=""+c),l.key!==void 0&&(f=""+l.key),"key"in l){c={};for(var d in l)d!=="key"&&(c[d]=l[d])}else c=l;return l=c.ref,{$$typeof:a,type:s,key:f,ref:l!==void 0?l:null,props:c}}return Fl.Fragment=t,Fl.jsx=n,Fl.jsxs=n,Fl}var y0;function E1(){return y0||(y0=1,Ah.exports=M1()),Ah.exports}var v=E1(),Ch={exports:{}},re={};/**
 * @license React
 * react.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var x0;function b1(){if(x0)return re;x0=1;var a=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),n=Symbol.for("react.fragment"),s=Symbol.for("react.strict_mode"),l=Symbol.for("react.profiler"),c=Symbol.for("react.consumer"),f=Symbol.for("react.context"),d=Symbol.for("react.forward_ref"),p=Symbol.for("react.suspense"),m=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),_=Symbol.for("react.activity"),y=Symbol.iterator;function S(O){return O===null||typeof O!="object"?null:(O=y&&O[y]||O["@@iterator"],typeof O=="function"?O:null)}var b={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},T=Object.assign,E={};function x(O,nt,St){this.props=O,this.context=nt,this.refs=E,this.updater=St||b}x.prototype.isReactComponent={},x.prototype.setState=function(O,nt){if(typeof O!="object"&&typeof O!="function"&&O!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,O,nt,"setState")},x.prototype.forceUpdate=function(O){this.updater.enqueueForceUpdate(this,O,"forceUpdate")};function P(){}P.prototype=x.prototype;function N(O,nt,St){this.props=O,this.context=nt,this.refs=E,this.updater=St||b}var R=N.prototype=new P;R.constructor=N,T(R,x.prototype),R.isPureReactComponent=!0;var V=Array.isArray;function F(){}var z={H:null,A:null,T:null,S:null},G=Object.prototype.hasOwnProperty;function U(O,nt,St){var q=St.ref;return{$$typeof:a,type:O,key:nt,ref:q!==void 0?q:null,props:St}}function D(O,nt){return U(O.type,nt,O.props)}function H(O){return typeof O=="object"&&O!==null&&O.$$typeof===a}function ut(O){var nt={"=":"=0",":":"=2"};return"$"+O.replace(/[=:]/g,function(St){return nt[St]})}var ot=/\/+/g;function mt(O,nt){return typeof O=="object"&&O!==null&&O.key!=null?ut(""+O.key):nt.toString(36)}function ct(O){switch(O.status){case"fulfilled":return O.value;case"rejected":throw O.reason;default:switch(typeof O.status=="string"?O.then(F,F):(O.status="pending",O.then(function(nt){O.status==="pending"&&(O.status="fulfilled",O.value=nt)},function(nt){O.status==="pending"&&(O.status="rejected",O.reason=nt)})),O.status){case"fulfilled":return O.value;case"rejected":throw O.reason}}throw O}function I(O,nt,St,q,ft){var Tt=typeof O;(Tt==="undefined"||Tt==="boolean")&&(O=null);var Mt=!1;if(O===null)Mt=!0;else switch(Tt){case"bigint":case"string":case"number":Mt=!0;break;case"object":switch(O.$$typeof){case a:case t:Mt=!0;break;case g:return Mt=O._init,I(Mt(O._payload),nt,St,q,ft)}}if(Mt)return ft=ft(O),Mt=q===""?"."+mt(O,0):q,V(ft)?(St="",Mt!=null&&(St=Mt.replace(ot,"$&/")+"/"),I(ft,nt,St,"",function(oe){return oe})):ft!=null&&(H(ft)&&(ft=D(ft,St+(ft.key==null||O&&O.key===ft.key?"":(""+ft.key).replace(ot,"$&/")+"/")+Mt)),nt.push(ft)),1;Mt=0;var Ft=q===""?".":q+":";if(V(O))for(var Vt=0;Vt<O.length;Vt++)q=O[Vt],Tt=Ft+mt(q,Vt),Mt+=I(q,nt,St,Tt,ft);else if(Vt=S(O),typeof Vt=="function")for(O=Vt.call(O),Vt=0;!(q=O.next()).done;)q=q.value,Tt=Ft+mt(q,Vt++),Mt+=I(q,nt,St,Tt,ft);else if(Tt==="object"){if(typeof O.then=="function")return I(ct(O),nt,St,q,ft);throw nt=String(O),Error("Objects are not valid as a React child (found: "+(nt==="[object Object]"?"object with keys {"+Object.keys(O).join(", ")+"}":nt)+"). If you meant to render a collection of children, use an array instead.")}return Mt}function Z(O,nt,St){if(O==null)return O;var q=[],ft=0;return I(O,q,"","",function(Tt){return nt.call(St,Tt,ft++)}),q}function $(O){if(O._status===-1){var nt=O._result;nt=nt(),nt.then(function(St){(O._status===0||O._status===-1)&&(O._status=1,O._result=St)},function(St){(O._status===0||O._status===-1)&&(O._status=2,O._result=St)}),O._status===-1&&(O._status=0,O._result=nt)}if(O._status===1)return O._result.default;throw O._result}var Et=typeof reportError=="function"?reportError:function(O){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var nt=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof O=="object"&&O!==null&&typeof O.message=="string"?String(O.message):String(O),error:O});if(!window.dispatchEvent(nt))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",O);return}console.error(O)},At={map:Z,forEach:function(O,nt,St){Z(O,function(){nt.apply(this,arguments)},St)},count:function(O){var nt=0;return Z(O,function(){nt++}),nt},toArray:function(O){return Z(O,function(nt){return nt})||[]},only:function(O){if(!H(O))throw Error("React.Children.only expected to receive a single React element child.");return O}};return re.Activity=_,re.Children=At,re.Component=x,re.Fragment=n,re.Profiler=l,re.PureComponent=N,re.StrictMode=s,re.Suspense=p,re.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=z,re.__COMPILER_RUNTIME={__proto__:null,c:function(O){return z.H.useMemoCache(O)}},re.cache=function(O){return function(){return O.apply(null,arguments)}},re.cacheSignal=function(){return null},re.cloneElement=function(O,nt,St){if(O==null)throw Error("The argument must be a React element, but you passed "+O+".");var q=T({},O.props),ft=O.key;if(nt!=null)for(Tt in nt.key!==void 0&&(ft=""+nt.key),nt)!G.call(nt,Tt)||Tt==="key"||Tt==="__self"||Tt==="__source"||Tt==="ref"&&nt.ref===void 0||(q[Tt]=nt[Tt]);var Tt=arguments.length-2;if(Tt===1)q.children=St;else if(1<Tt){for(var Mt=Array(Tt),Ft=0;Ft<Tt;Ft++)Mt[Ft]=arguments[Ft+2];q.children=Mt}return U(O.type,ft,q)},re.createContext=function(O){return O={$$typeof:f,_currentValue:O,_currentValue2:O,_threadCount:0,Provider:null,Consumer:null},O.Provider=O,O.Consumer={$$typeof:c,_context:O},O},re.createElement=function(O,nt,St){var q,ft={},Tt=null;if(nt!=null)for(q in nt.key!==void 0&&(Tt=""+nt.key),nt)G.call(nt,q)&&q!=="key"&&q!=="__self"&&q!=="__source"&&(ft[q]=nt[q]);var Mt=arguments.length-2;if(Mt===1)ft.children=St;else if(1<Mt){for(var Ft=Array(Mt),Vt=0;Vt<Mt;Vt++)Ft[Vt]=arguments[Vt+2];ft.children=Ft}if(O&&O.defaultProps)for(q in Mt=O.defaultProps,Mt)ft[q]===void 0&&(ft[q]=Mt[q]);return U(O,Tt,ft)},re.createRef=function(){return{current:null}},re.forwardRef=function(O){return{$$typeof:d,render:O}},re.isValidElement=H,re.lazy=function(O){return{$$typeof:g,_payload:{_status:-1,_result:O},_init:$}},re.memo=function(O,nt){return{$$typeof:m,type:O,compare:nt===void 0?null:nt}},re.startTransition=function(O){var nt=z.T,St={};z.T=St;try{var q=O(),ft=z.S;ft!==null&&ft(St,q),typeof q=="object"&&q!==null&&typeof q.then=="function"&&q.then(F,Et)}catch(Tt){Et(Tt)}finally{nt!==null&&St.types!==null&&(nt.types=St.types),z.T=nt}},re.unstable_useCacheRefresh=function(){return z.H.useCacheRefresh()},re.use=function(O){return z.H.use(O)},re.useActionState=function(O,nt,St){return z.H.useActionState(O,nt,St)},re.useCallback=function(O,nt){return z.H.useCallback(O,nt)},re.useContext=function(O){return z.H.useContext(O)},re.useDebugValue=function(){},re.useDeferredValue=function(O,nt){return z.H.useDeferredValue(O,nt)},re.useEffect=function(O,nt){return z.H.useEffect(O,nt)},re.useEffectEvent=function(O){return z.H.useEffectEvent(O)},re.useId=function(){return z.H.useId()},re.useImperativeHandle=function(O,nt,St){return z.H.useImperativeHandle(O,nt,St)},re.useInsertionEffect=function(O,nt){return z.H.useInsertionEffect(O,nt)},re.useLayoutEffect=function(O,nt){return z.H.useLayoutEffect(O,nt)},re.useMemo=function(O,nt){return z.H.useMemo(O,nt)},re.useOptimistic=function(O,nt){return z.H.useOptimistic(O,nt)},re.useReducer=function(O,nt,St){return z.H.useReducer(O,nt,St)},re.useRef=function(O){return z.H.useRef(O)},re.useState=function(O){return z.H.useState(O)},re.useSyncExternalStore=function(O,nt,St){return z.H.useSyncExternalStore(O,nt,St)},re.useTransition=function(){return z.H.useTransition()},re.version="19.2.7",re}var S0;function gm(){return S0||(S0=1,Ch.exports=b1()),Ch.exports}var se=gm();const T1=tx(se);var Rh={exports:{}},Hl={},wh={exports:{}},Dh={};/**
 * @license React
 * scheduler.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var M0;function A1(){return M0||(M0=1,(function(a){function t(I,Z){var $=I.length;I.push(Z);t:for(;0<$;){var Et=$-1>>>1,At=I[Et];if(0<l(At,Z))I[Et]=Z,I[$]=At,$=Et;else break t}}function n(I){return I.length===0?null:I[0]}function s(I){if(I.length===0)return null;var Z=I[0],$=I.pop();if($!==Z){I[0]=$;t:for(var Et=0,At=I.length,O=At>>>1;Et<O;){var nt=2*(Et+1)-1,St=I[nt],q=nt+1,ft=I[q];if(0>l(St,$))q<At&&0>l(ft,St)?(I[Et]=ft,I[q]=$,Et=q):(I[Et]=St,I[nt]=$,Et=nt);else if(q<At&&0>l(ft,$))I[Et]=ft,I[q]=$,Et=q;else break t}}return Z}function l(I,Z){var $=I.sortIndex-Z.sortIndex;return $!==0?$:I.id-Z.id}if(a.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var c=performance;a.unstable_now=function(){return c.now()}}else{var f=Date,d=f.now();a.unstable_now=function(){return f.now()-d}}var p=[],m=[],g=1,_=null,y=3,S=!1,b=!1,T=!1,E=!1,x=typeof setTimeout=="function"?setTimeout:null,P=typeof clearTimeout=="function"?clearTimeout:null,N=typeof setImmediate<"u"?setImmediate:null;function R(I){for(var Z=n(m);Z!==null;){if(Z.callback===null)s(m);else if(Z.startTime<=I)s(m),Z.sortIndex=Z.expirationTime,t(p,Z);else break;Z=n(m)}}function V(I){if(T=!1,R(I),!b)if(n(p)!==null)b=!0,F||(F=!0,ut());else{var Z=n(m);Z!==null&&ct(V,Z.startTime-I)}}var F=!1,z=-1,G=5,U=-1;function D(){return E?!0:!(a.unstable_now()-U<G)}function H(){if(E=!1,F){var I=a.unstable_now();U=I;var Z=!0;try{t:{b=!1,T&&(T=!1,P(z),z=-1),S=!0;var $=y;try{e:{for(R(I),_=n(p);_!==null&&!(_.expirationTime>I&&D());){var Et=_.callback;if(typeof Et=="function"){_.callback=null,y=_.priorityLevel;var At=Et(_.expirationTime<=I);if(I=a.unstable_now(),typeof At=="function"){_.callback=At,R(I),Z=!0;break e}_===n(p)&&s(p),R(I)}else s(p);_=n(p)}if(_!==null)Z=!0;else{var O=n(m);O!==null&&ct(V,O.startTime-I),Z=!1}}break t}finally{_=null,y=$,S=!1}Z=void 0}}finally{Z?ut():F=!1}}}var ut;if(typeof N=="function")ut=function(){N(H)};else if(typeof MessageChannel<"u"){var ot=new MessageChannel,mt=ot.port2;ot.port1.onmessage=H,ut=function(){mt.postMessage(null)}}else ut=function(){x(H,0)};function ct(I,Z){z=x(function(){I(a.unstable_now())},Z)}a.unstable_IdlePriority=5,a.unstable_ImmediatePriority=1,a.unstable_LowPriority=4,a.unstable_NormalPriority=3,a.unstable_Profiling=null,a.unstable_UserBlockingPriority=2,a.unstable_cancelCallback=function(I){I.callback=null},a.unstable_forceFrameRate=function(I){0>I||125<I?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):G=0<I?Math.floor(1e3/I):5},a.unstable_getCurrentPriorityLevel=function(){return y},a.unstable_next=function(I){switch(y){case 1:case 2:case 3:var Z=3;break;default:Z=y}var $=y;y=Z;try{return I()}finally{y=$}},a.unstable_requestPaint=function(){E=!0},a.unstable_runWithPriority=function(I,Z){switch(I){case 1:case 2:case 3:case 4:case 5:break;default:I=3}var $=y;y=I;try{return Z()}finally{y=$}},a.unstable_scheduleCallback=function(I,Z,$){var Et=a.unstable_now();switch(typeof $=="object"&&$!==null?($=$.delay,$=typeof $=="number"&&0<$?Et+$:Et):$=Et,I){case 1:var At=-1;break;case 2:At=250;break;case 5:At=1073741823;break;case 4:At=1e4;break;default:At=5e3}return At=$+At,I={id:g++,callback:Z,priorityLevel:I,startTime:$,expirationTime:At,sortIndex:-1},$>Et?(I.sortIndex=$,t(m,I),n(p)===null&&I===n(m)&&(T?(P(z),z=-1):T=!0,ct(V,$-Et))):(I.sortIndex=At,t(p,I),b||S||(b=!0,F||(F=!0,ut()))),I},a.unstable_shouldYield=D,a.unstable_wrapCallback=function(I){var Z=y;return function(){var $=y;y=Z;try{return I.apply(this,arguments)}finally{y=$}}}})(Dh)),Dh}var E0;function C1(){return E0||(E0=1,wh.exports=A1()),wh.exports}var Nh={exports:{}},In={};/**
 * @license React
 * react-dom.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var b0;function R1(){if(b0)return In;b0=1;var a=gm();function t(p){var m="https://react.dev/errors/"+p;if(1<arguments.length){m+="?args[]="+encodeURIComponent(arguments[1]);for(var g=2;g<arguments.length;g++)m+="&args[]="+encodeURIComponent(arguments[g])}return"Minified React error #"+p+"; visit "+m+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function n(){}var s={d:{f:n,r:function(){throw Error(t(522))},D:n,C:n,L:n,m:n,X:n,S:n,M:n},p:0,findDOMNode:null},l=Symbol.for("react.portal");function c(p,m,g){var _=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:l,key:_==null?null:""+_,children:p,containerInfo:m,implementation:g}}var f=a.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function d(p,m){if(p==="font")return"";if(typeof m=="string")return m==="use-credentials"?m:""}return In.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=s,In.createPortal=function(p,m){var g=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!m||m.nodeType!==1&&m.nodeType!==9&&m.nodeType!==11)throw Error(t(299));return c(p,m,null,g)},In.flushSync=function(p){var m=f.T,g=s.p;try{if(f.T=null,s.p=2,p)return p()}finally{f.T=m,s.p=g,s.d.f()}},In.preconnect=function(p,m){typeof p=="string"&&(m?(m=m.crossOrigin,m=typeof m=="string"?m==="use-credentials"?m:"":void 0):m=null,s.d.C(p,m))},In.prefetchDNS=function(p){typeof p=="string"&&s.d.D(p)},In.preinit=function(p,m){if(typeof p=="string"&&m&&typeof m.as=="string"){var g=m.as,_=d(g,m.crossOrigin),y=typeof m.integrity=="string"?m.integrity:void 0,S=typeof m.fetchPriority=="string"?m.fetchPriority:void 0;g==="style"?s.d.S(p,typeof m.precedence=="string"?m.precedence:void 0,{crossOrigin:_,integrity:y,fetchPriority:S}):g==="script"&&s.d.X(p,{crossOrigin:_,integrity:y,fetchPriority:S,nonce:typeof m.nonce=="string"?m.nonce:void 0})}},In.preinitModule=function(p,m){if(typeof p=="string")if(typeof m=="object"&&m!==null){if(m.as==null||m.as==="script"){var g=d(m.as,m.crossOrigin);s.d.M(p,{crossOrigin:g,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0})}}else m==null&&s.d.M(p)},In.preload=function(p,m){if(typeof p=="string"&&typeof m=="object"&&m!==null&&typeof m.as=="string"){var g=m.as,_=d(g,m.crossOrigin);s.d.L(p,g,{crossOrigin:_,integrity:typeof m.integrity=="string"?m.integrity:void 0,nonce:typeof m.nonce=="string"?m.nonce:void 0,type:typeof m.type=="string"?m.type:void 0,fetchPriority:typeof m.fetchPriority=="string"?m.fetchPriority:void 0,referrerPolicy:typeof m.referrerPolicy=="string"?m.referrerPolicy:void 0,imageSrcSet:typeof m.imageSrcSet=="string"?m.imageSrcSet:void 0,imageSizes:typeof m.imageSizes=="string"?m.imageSizes:void 0,media:typeof m.media=="string"?m.media:void 0})}},In.preloadModule=function(p,m){if(typeof p=="string")if(m){var g=d(m.as,m.crossOrigin);s.d.m(p,{as:typeof m.as=="string"&&m.as!=="script"?m.as:void 0,crossOrigin:g,integrity:typeof m.integrity=="string"?m.integrity:void 0})}else s.d.m(p)},In.requestFormReset=function(p){s.d.r(p)},In.unstable_batchedUpdates=function(p,m){return p(m)},In.useFormState=function(p,m,g){return f.H.useFormState(p,m,g)},In.useFormStatus=function(){return f.H.useHostTransitionStatus()},In.version="19.2.7",In}var T0;function w1(){if(T0)return Nh.exports;T0=1;function a(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(a)}catch(t){console.error(t)}}return a(),Nh.exports=R1(),Nh.exports}/**
 * @license React
 * react-dom-client.production.js
 *
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var A0;function D1(){if(A0)return Hl;A0=1;var a=C1(),t=gm(),n=w1();function s(e){var i="https://react.dev/errors/"+e;if(1<arguments.length){i+="?args[]="+encodeURIComponent(arguments[1]);for(var r=2;r<arguments.length;r++)i+="&args[]="+encodeURIComponent(arguments[r])}return"Minified React error #"+e+"; visit "+i+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function c(e){var i=e,r=e;if(e.alternate)for(;i.return;)i=i.return;else{e=i;do i=e,(i.flags&4098)!==0&&(r=i.return),e=i.return;while(e)}return i.tag===3?r:null}function f(e){if(e.tag===13){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function d(e){if(e.tag===31){var i=e.memoizedState;if(i===null&&(e=e.alternate,e!==null&&(i=e.memoizedState)),i!==null)return i.dehydrated}return null}function p(e){if(c(e)!==e)throw Error(s(188))}function m(e){var i=e.alternate;if(!i){if(i=c(e),i===null)throw Error(s(188));return i!==e?null:e}for(var r=e,o=i;;){var u=r.return;if(u===null)break;var h=u.alternate;if(h===null){if(o=u.return,o!==null){r=o;continue}break}if(u.child===h.child){for(h=u.child;h;){if(h===r)return p(u),e;if(h===o)return p(u),i;h=h.sibling}throw Error(s(188))}if(r.return!==o.return)r=u,o=h;else{for(var M=!1,A=u.child;A;){if(A===r){M=!0,r=u,o=h;break}if(A===o){M=!0,o=u,r=h;break}A=A.sibling}if(!M){for(A=h.child;A;){if(A===r){M=!0,r=h,o=u;break}if(A===o){M=!0,o=h,r=u;break}A=A.sibling}if(!M)throw Error(s(189))}}if(r.alternate!==o)throw Error(s(190))}if(r.tag!==3)throw Error(s(188));return r.stateNode.current===r?e:i}function g(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e;for(e=e.child;e!==null;){if(i=g(e),i!==null)return i;e=e.sibling}return null}var _=Object.assign,y=Symbol.for("react.element"),S=Symbol.for("react.transitional.element"),b=Symbol.for("react.portal"),T=Symbol.for("react.fragment"),E=Symbol.for("react.strict_mode"),x=Symbol.for("react.profiler"),P=Symbol.for("react.consumer"),N=Symbol.for("react.context"),R=Symbol.for("react.forward_ref"),V=Symbol.for("react.suspense"),F=Symbol.for("react.suspense_list"),z=Symbol.for("react.memo"),G=Symbol.for("react.lazy"),U=Symbol.for("react.activity"),D=Symbol.for("react.memo_cache_sentinel"),H=Symbol.iterator;function ut(e){return e===null||typeof e!="object"?null:(e=H&&e[H]||e["@@iterator"],typeof e=="function"?e:null)}var ot=Symbol.for("react.client.reference");function mt(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===ot?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case T:return"Fragment";case x:return"Profiler";case E:return"StrictMode";case V:return"Suspense";case F:return"SuspenseList";case U:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case b:return"Portal";case N:return e.displayName||"Context";case P:return(e._context.displayName||"Context")+".Consumer";case R:var i=e.render;return e=e.displayName,e||(e=i.displayName||i.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case z:return i=e.displayName||null,i!==null?i:mt(e.type)||"Memo";case G:i=e._payload,e=e._init;try{return mt(e(i))}catch{}}return null}var ct=Array.isArray,I=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,Z=n.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,$={pending:!1,data:null,method:null,action:null},Et=[],At=-1;function O(e){return{current:e}}function nt(e){0>At||(e.current=Et[At],Et[At]=null,At--)}function St(e,i){At++,Et[At]=e.current,e.current=i}var q=O(null),ft=O(null),Tt=O(null),Mt=O(null);function Ft(e,i){switch(St(Tt,i),St(ft,e),St(q,null),i.nodeType){case 9:case 11:e=(e=i.documentElement)&&(e=e.namespaceURI)?H_(e):0;break;default:if(e=i.tagName,i=i.namespaceURI)i=H_(i),e=G_(i,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}nt(q),St(q,e)}function Vt(){nt(q),nt(ft),nt(Tt)}function oe(e){e.memoizedState!==null&&St(Mt,e);var i=q.current,r=G_(i,e.type);i!==r&&(St(ft,e),St(q,r))}function Ge(e){ft.current===e&&(nt(q),nt(ft)),Mt.current===e&&(nt(Mt),Pl._currentValue=$)}var ve,$e;function k(e){if(ve===void 0)try{throw Error()}catch(r){var i=r.stack.trim().match(/\n( *(at )?)/);ve=i&&i[1]||"",$e=-1<r.stack.indexOf(`
    at`)?" (<anonymous>)":-1<r.stack.indexOf("@")?"@unknown:0:0":""}return`
`+ve+e+$e}var Pn=!1;function me(e,i){if(!e||Pn)return"";Pn=!0;var r=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var o={DetermineComponentFrameRoot:function(){try{if(i){var _t=function(){throw Error()};if(Object.defineProperty(_t.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(_t,[])}catch(lt){var it=lt}Reflect.construct(e,[],_t)}else{try{_t.call()}catch(lt){it=lt}e.call(_t.prototype)}}else{try{throw Error()}catch(lt){it=lt}(_t=e())&&typeof _t.catch=="function"&&_t.catch(function(){})}}catch(lt){if(lt&&it&&typeof lt.stack=="string")return[lt.stack,it.stack]}return[null,null]}};o.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var u=Object.getOwnPropertyDescriptor(o.DetermineComponentFrameRoot,"name");u&&u.configurable&&Object.defineProperty(o.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var h=o.DetermineComponentFrameRoot(),M=h[0],A=h[1];if(M&&A){var B=M.split(`
`),et=A.split(`
`);for(u=o=0;o<B.length&&!B[o].includes("DetermineComponentFrameRoot");)o++;for(;u<et.length&&!et[u].includes("DetermineComponentFrameRoot");)u++;if(o===B.length||u===et.length)for(o=B.length-1,u=et.length-1;1<=o&&0<=u&&B[o]!==et[u];)u--;for(;1<=o&&0<=u;o--,u--)if(B[o]!==et[u]){if(o!==1||u!==1)do if(o--,u--,0>u||B[o]!==et[u]){var ht=`
`+B[o].replace(" at new "," at ");return e.displayName&&ht.includes("<anonymous>")&&(ht=ht.replace("<anonymous>",e.displayName)),ht}while(1<=o&&0<=u);break}}}finally{Pn=!1,Error.prepareStackTrace=r}return(r=e?e.displayName||e.name:"")?k(r):""}function Se(e,i){switch(e.tag){case 26:case 27:case 5:return k(e.type);case 16:return k("Lazy");case 13:return e.child!==i&&i!==null?k("Suspense Fallback"):k("Suspense");case 19:return k("SuspenseList");case 0:case 15:return me(e.type,!1);case 11:return me(e.type.render,!1);case 1:return me(e.type,!0);case 31:return k("Activity");default:return""}}function Qt(e){try{var i="",r=null;do i+=Se(e,r),r=e,e=e.return;while(e);return i}catch(o){return`
Error generating stack: `+o.message+`
`+o.stack}}var Be=Object.prototype.hasOwnProperty,Yt=a.unstable_scheduleCallback,L=a.unstable_cancelCallback,C=a.unstable_shouldYield,at=a.unstable_requestPaint,pt=a.unstable_now,bt=a.unstable_getCurrentPriorityLevel,vt=a.unstable_ImmediatePriority,Xt=a.unstable_UserBlockingPriority,Dt=a.unstable_NormalPriority,Bt=a.unstable_LowPriority,Me=a.unstable_IdlePriority,Ct=a.log,Ht=a.unstable_setDisableYieldValue,Zt=null,qt=null;function Ot(e){if(typeof Ct=="function"&&Ht(e),qt&&typeof qt.setStrictMode=="function")try{qt.setStrictMode(Zt,e)}catch{}}var ne=Math.clz32?Math.clz32:Y,le=Math.log,Ve=Math.LN2;function Y(e){return e>>>=0,e===0?32:31-(le(e)/Ve|0)|0}var Rt=256,dt=262144,yt=4194304;function wt(e){var i=e&42;if(i!==0)return i;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function Nt(e,i,r){var o=e.pendingLanes;if(o===0)return 0;var u=0,h=e.suspendedLanes,M=e.pingedLanes;e=e.warmLanes;var A=o&134217727;return A!==0?(o=A&~h,o!==0?u=wt(o):(M&=A,M!==0?u=wt(M):r||(r=A&~e,r!==0&&(u=wt(r))))):(A=o&~h,A!==0?u=wt(A):M!==0?u=wt(M):r||(r=o&~e,r!==0&&(u=wt(r)))),u===0?0:i!==0&&i!==u&&(i&h)===0&&(h=u&-u,r=i&-i,h>=r||h===32&&(r&4194048)!==0)?i:u}function ie(e,i){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&i)===0}function tn(e,i){switch(e){case 1:case 2:case 4:case 8:case 64:return i+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return i+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function _n(){var e=yt;return yt<<=1,(yt&62914560)===0&&(yt=4194304),e}function we(e){for(var i=[],r=0;31>r;r++)i.push(e);return i}function Rn(e,i){e.pendingLanes|=i,i!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function wi(e,i,r,o,u,h){var M=e.pendingLanes;e.pendingLanes=r,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=r,e.entangledLanes&=r,e.errorRecoveryDisabledLanes&=r,e.shellSuspendCounter=0;var A=e.entanglements,B=e.expirationTimes,et=e.hiddenUpdates;for(r=M&~r;0<r;){var ht=31-ne(r),_t=1<<ht;A[ht]=0,B[ht]=-1;var it=et[ht];if(it!==null)for(et[ht]=null,ht=0;ht<it.length;ht++){var lt=it[ht];lt!==null&&(lt.lane&=-536870913)}r&=~_t}o!==0&&Yo(e,o,0),h!==0&&u===0&&e.tag!==0&&(e.suspendedLanes|=h&~(M&~i))}function Yo(e,i,r){e.pendingLanes|=i,e.suspendedLanes&=~i;var o=31-ne(i);e.entangledLanes|=i,e.entanglements[o]=e.entanglements[o]|1073741824|r&261930}function Qo(e,i){var r=e.entangledLanes|=i;for(e=e.entanglements;r;){var o=31-ne(r),u=1<<o;u&i|e[o]&i&&(e[o]|=i),r&=~u}}function ji(e,i){var r=i&-i;return r=(r&42)!==0?1:ws(r),(r&(e.suspendedLanes|i))!==0?0:r}function ws(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function Sr(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function Zo(){var e=Z.p;return e!==0?e:(e=window.event,e===void 0?32:u0(e.type))}function Ds(e,i){var r=Z.p;try{return Z.p=e,i()}finally{Z.p=r}}var Di=Math.random().toString(36).slice(2),sn="__reactFiber$"+Di,wn="__reactProps$"+Di,na="__reactContainer$"+Di,Ko="__reactEvents$"+Di,yf="__reactListeners$"+Di,xf="__reactHandles$"+Di,pc="__reactResources$"+Di,Ns="__reactMarker$"+Di;function w(e){delete e[sn],delete e[wn],delete e[Ko],delete e[yf],delete e[xf]}function Q(e){var i=e[sn];if(i)return i;for(var r=e.parentNode;r;){if(i=r[na]||r[sn]){if(r=i.alternate,i.child!==null||r!==null&&r.child!==null)for(e=Y_(e);e!==null;){if(r=e[sn])return r;e=Y_(e)}return i}e=r,r=e.parentNode}return null}function st(e){if(e=e[sn]||e[na]){var i=e.tag;if(i===5||i===6||i===13||i===31||i===26||i===27||i===3)return e}return null}function rt(e){var i=e.tag;if(i===5||i===26||i===27||i===6)return e.stateNode;throw Error(s(33))}function K(e){var i=e[pc];return i||(i=e[pc]={hoistableStyles:new Map,hoistableScripts:new Map}),i}function xt(e){e[Ns]=!0}var Ut=new Set,It={};function Pt(e,i){$t(e,i),$t(e+"Capture",i)}function $t(e,i){for(It[e]=i,e=0;e<i.length;e++)Ut.add(i[e])}var ae=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),Kt={},Ee={};function De(e){return Be.call(Ee,e)?!0:Be.call(Kt,e)?!1:ae.test(e)?Ee[e]=!0:(Kt[e]=!0,!1)}function Ze(e,i,r){if(De(i))if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":e.removeAttribute(i);return;case"boolean":var o=i.toLowerCase().slice(0,5);if(o!=="data-"&&o!=="aria-"){e.removeAttribute(i);return}}e.setAttribute(i,""+r)}}function Ye(e,i,r){if(r===null)e.removeAttribute(i);else{switch(typeof r){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(i);return}e.setAttribute(i,""+r)}}function ce(e,i,r,o){if(o===null)e.removeAttribute(r);else{switch(typeof o){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(r);return}e.setAttributeNS(i,r,""+o)}}function kt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function dn(e){var i=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(i==="checkbox"||i==="radio")}function Ne(e,i,r){var o=Object.getOwnPropertyDescriptor(e.constructor.prototype,i);if(!e.hasOwnProperty(i)&&typeof o<"u"&&typeof o.get=="function"&&typeof o.set=="function"){var u=o.get,h=o.set;return Object.defineProperty(e,i,{configurable:!0,get:function(){return u.call(this)},set:function(M){r=""+M,h.call(this,M)}}),Object.defineProperty(e,i,{enumerable:o.enumerable}),{getValue:function(){return r},setValue:function(M){r=""+M},stopTracking:function(){e._valueTracker=null,delete e[i]}}}}function Gn(e){if(!e._valueTracker){var i=dn(e)?"checked":"value";e._valueTracker=Ne(e,i,""+e[i])}}function ia(e){if(!e)return!1;var i=e._valueTracker;if(!i)return!0;var r=i.getValue(),o="";return e&&(o=dn(e)?e.checked?"true":"false":e.value),e=o,e!==r?(i.setValue(e),!0):!1}function En(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Us=/[\n"\\]/g;function _e(e){return e.replace(Us,function(i){return"\\"+i.charCodeAt(0).toString(16)+" "})}function zn(e,i,r,o,u,h,M,A){e.name="",M!=null&&typeof M!="function"&&typeof M!="symbol"&&typeof M!="boolean"?e.type=M:e.removeAttribute("type"),i!=null?M==="number"?(i===0&&e.value===""||e.value!=i)&&(e.value=""+kt(i)):e.value!==""+kt(i)&&(e.value=""+kt(i)):M!=="submit"&&M!=="reset"||e.removeAttribute("value"),i!=null?yn(e,M,kt(i)):r!=null?yn(e,M,kt(r)):o!=null&&e.removeAttribute("value"),u==null&&h!=null&&(e.defaultChecked=!!h),u!=null&&(e.checked=u&&typeof u!="function"&&typeof u!="symbol"),A!=null&&typeof A!="function"&&typeof A!="symbol"&&typeof A!="boolean"?e.name=""+kt(A):e.removeAttribute("name")}function Vn(e,i,r,o,u,h,M,A){if(h!=null&&typeof h!="function"&&typeof h!="symbol"&&typeof h!="boolean"&&(e.type=h),i!=null||r!=null){if(!(h!=="submit"&&h!=="reset"||i!=null)){Gn(e);return}r=r!=null?""+kt(r):"",i=i!=null?""+kt(i):r,A||i===e.value||(e.value=i),e.defaultValue=i}o=o??u,o=typeof o!="function"&&typeof o!="symbol"&&!!o,e.checked=A?e.checked:!!o,e.defaultChecked=!!o,M!=null&&typeof M!="function"&&typeof M!="symbol"&&typeof M!="boolean"&&(e.name=M),Gn(e)}function yn(e,i,r){i==="number"&&En(e.ownerDocument)===e||e.defaultValue===""+r||(e.defaultValue=""+r)}function cn(e,i,r,o){if(e=e.options,i){i={};for(var u=0;u<r.length;u++)i["$"+r[u]]=!0;for(r=0;r<e.length;r++)u=i.hasOwnProperty("$"+e[r].value),e[r].selected!==u&&(e[r].selected=u),u&&o&&(e[r].defaultSelected=!0)}else{for(r=""+kt(r),i=null,u=0;u<e.length;u++){if(e[u].value===r){e[u].selected=!0,o&&(e[u].defaultSelected=!0);return}i!==null||e[u].disabled||(i=e[u])}i!==null&&(i.selected=!0)}}function Mr(e,i,r){if(i!=null&&(i=""+kt(i),i!==e.value&&(e.value=i),r==null)){e.defaultValue!==i&&(e.defaultValue=i);return}e.defaultValue=r!=null?""+kt(r):""}function Xi(e,i,r,o){if(i==null){if(o!=null){if(r!=null)throw Error(s(92));if(ct(o)){if(1<o.length)throw Error(s(93));o=o[0]}r=o}r==null&&(r=""),i=r}r=kt(i),e.defaultValue=r,o=e.textContent,o===r&&o!==""&&o!==null&&(e.value=o),Gn(e)}function Er(e,i){if(i){var r=e.firstChild;if(r&&r===e.lastChild&&r.nodeType===3){r.nodeValue=i;return}}e.textContent=i}var vS=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function Im(e,i,r){var o=i.indexOf("--")===0;r==null||typeof r=="boolean"||r===""?o?e.setProperty(i,""):i==="float"?e.cssFloat="":e[i]="":o?e.setProperty(i,r):typeof r!="number"||r===0||vS.has(i)?i==="float"?e.cssFloat=r:e[i]=(""+r).trim():e[i]=r+"px"}function Bm(e,i,r){if(i!=null&&typeof i!="object")throw Error(s(62));if(e=e.style,r!=null){for(var o in r)!r.hasOwnProperty(o)||i!=null&&i.hasOwnProperty(o)||(o.indexOf("--")===0?e.setProperty(o,""):o==="float"?e.cssFloat="":e[o]="");for(var u in i)o=i[u],i.hasOwnProperty(u)&&r[u]!==o&&Im(e,u,o)}else for(var h in i)i.hasOwnProperty(h)&&Im(e,h,i[h])}function Sf(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var _S=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),yS=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function mc(e){return yS.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function aa(){}var Mf=null;function Ef(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var br=null,Tr=null;function Fm(e){var i=st(e);if(i&&(e=i.stateNode)){var r=e[wn]||null;t:switch(e=i.stateNode,i.type){case"input":if(zn(e,r.value,r.defaultValue,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name),i=r.name,r.type==="radio"&&i!=null){for(r=e;r.parentNode;)r=r.parentNode;for(r=r.querySelectorAll('input[name="'+_e(""+i)+'"][type="radio"]'),i=0;i<r.length;i++){var o=r[i];if(o!==e&&o.form===e.form){var u=o[wn]||null;if(!u)throw Error(s(90));zn(o,u.value,u.defaultValue,u.defaultValue,u.checked,u.defaultChecked,u.type,u.name)}}for(i=0;i<r.length;i++)o=r[i],o.form===e.form&&ia(o)}break t;case"textarea":Mr(e,r.value,r.defaultValue);break t;case"select":i=r.value,i!=null&&cn(e,!!r.multiple,i,!1)}}}var bf=!1;function Hm(e,i,r){if(bf)return e(i,r);bf=!0;try{var o=e(i);return o}finally{if(bf=!1,(br!==null||Tr!==null)&&(nu(),br&&(i=br,e=Tr,Tr=br=null,Fm(i),e)))for(i=0;i<e.length;i++)Fm(e[i])}}function Jo(e,i){var r=e.stateNode;if(r===null)return null;var o=r[wn]||null;if(o===null)return null;r=o[i];t:switch(i){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(o=!o.disabled)||(e=e.type,o=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!o;break t;default:e=!1}if(e)return null;if(r&&typeof r!="function")throw Error(s(231,i,typeof r));return r}var sa=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),Tf=!1;if(sa)try{var $o={};Object.defineProperty($o,"passive",{get:function(){Tf=!0}}),window.addEventListener("test",$o,$o),window.removeEventListener("test",$o,$o)}catch{Tf=!1}var Fa=null,Af=null,gc=null;function Gm(){if(gc)return gc;var e,i=Af,r=i.length,o,u="value"in Fa?Fa.value:Fa.textContent,h=u.length;for(e=0;e<r&&i[e]===u[e];e++);var M=r-e;for(o=1;o<=M&&i[r-o]===u[h-o];o++);return gc=u.slice(e,1<o?1-o:void 0)}function vc(e){var i=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&i===13&&(e=13)):e=i,e===10&&(e=13),32<=e||e===13?e:0}function _c(){return!0}function Vm(){return!1}function Qn(e){function i(r,o,u,h,M){this._reactName=r,this._targetInst=u,this.type=o,this.nativeEvent=h,this.target=M,this.currentTarget=null;for(var A in e)e.hasOwnProperty(A)&&(r=e[A],this[A]=r?r(h):h[A]);return this.isDefaultPrevented=(h.defaultPrevented!=null?h.defaultPrevented:h.returnValue===!1)?_c:Vm,this.isPropagationStopped=Vm,this}return _(i.prototype,{preventDefault:function(){this.defaultPrevented=!0;var r=this.nativeEvent;r&&(r.preventDefault?r.preventDefault():typeof r.returnValue!="unknown"&&(r.returnValue=!1),this.isDefaultPrevented=_c)},stopPropagation:function(){var r=this.nativeEvent;r&&(r.stopPropagation?r.stopPropagation():typeof r.cancelBubble!="unknown"&&(r.cancelBubble=!0),this.isPropagationStopped=_c)},persist:function(){},isPersistent:_c}),i}var Ls={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},yc=Qn(Ls),tl=_({},Ls,{view:0,detail:0}),xS=Qn(tl),Cf,Rf,el,xc=_({},tl,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:Df,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==el&&(el&&e.type==="mousemove"?(Cf=e.screenX-el.screenX,Rf=e.screenY-el.screenY):Rf=Cf=0,el=e),Cf)},movementY:function(e){return"movementY"in e?e.movementY:Rf}}),km=Qn(xc),SS=_({},xc,{dataTransfer:0}),MS=Qn(SS),ES=_({},tl,{relatedTarget:0}),wf=Qn(ES),bS=_({},Ls,{animationName:0,elapsedTime:0,pseudoElement:0}),TS=Qn(bS),AS=_({},Ls,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),CS=Qn(AS),RS=_({},Ls,{data:0}),jm=Qn(RS),wS={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},DS={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},NS={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function US(e){var i=this.nativeEvent;return i.getModifierState?i.getModifierState(e):(e=NS[e])?!!i[e]:!1}function Df(){return US}var LS=_({},tl,{key:function(e){if(e.key){var i=wS[e.key]||e.key;if(i!=="Unidentified")return i}return e.type==="keypress"?(e=vc(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?DS[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:Df,charCode:function(e){return e.type==="keypress"?vc(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?vc(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),OS=Qn(LS),PS=_({},xc,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Xm=Qn(PS),zS=_({},tl,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:Df}),IS=Qn(zS),BS=_({},Ls,{propertyName:0,elapsedTime:0,pseudoElement:0}),FS=Qn(BS),HS=_({},xc,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),GS=Qn(HS),VS=_({},Ls,{newState:0,oldState:0}),kS=Qn(VS),jS=[9,13,27,32],Nf=sa&&"CompositionEvent"in window,nl=null;sa&&"documentMode"in document&&(nl=document.documentMode);var XS=sa&&"TextEvent"in window&&!nl,qm=sa&&(!Nf||nl&&8<nl&&11>=nl),Wm=" ",Ym=!1;function Qm(e,i){switch(e){case"keyup":return jS.indexOf(i.keyCode)!==-1;case"keydown":return i.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Zm(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var Ar=!1;function qS(e,i){switch(e){case"compositionend":return Zm(i);case"keypress":return i.which!==32?null:(Ym=!0,Wm);case"textInput":return e=i.data,e===Wm&&Ym?null:e;default:return null}}function WS(e,i){if(Ar)return e==="compositionend"||!Nf&&Qm(e,i)?(e=Gm(),gc=Af=Fa=null,Ar=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(i.ctrlKey||i.altKey||i.metaKey)||i.ctrlKey&&i.altKey){if(i.char&&1<i.char.length)return i.char;if(i.which)return String.fromCharCode(i.which)}return null;case"compositionend":return qm&&i.locale!=="ko"?null:i.data;default:return null}}var YS={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Km(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i==="input"?!!YS[e.type]:i==="textarea"}function Jm(e,i,r,o){br?Tr?Tr.push(o):Tr=[o]:br=o,i=cu(i,"onChange"),0<i.length&&(r=new yc("onChange","change",null,r,o),e.push({event:r,listeners:i}))}var il=null,al=null;function QS(e){O_(e,0)}function Sc(e){var i=rt(e);if(ia(i))return e}function $m(e,i){if(e==="change")return i}var tg=!1;if(sa){var Uf;if(sa){var Lf="oninput"in document;if(!Lf){var eg=document.createElement("div");eg.setAttribute("oninput","return;"),Lf=typeof eg.oninput=="function"}Uf=Lf}else Uf=!1;tg=Uf&&(!document.documentMode||9<document.documentMode)}function ng(){il&&(il.detachEvent("onpropertychange",ig),al=il=null)}function ig(e){if(e.propertyName==="value"&&Sc(al)){var i=[];Jm(i,al,e,Ef(e)),Hm(QS,i)}}function ZS(e,i,r){e==="focusin"?(ng(),il=i,al=r,il.attachEvent("onpropertychange",ig)):e==="focusout"&&ng()}function KS(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return Sc(al)}function JS(e,i){if(e==="click")return Sc(i)}function $S(e,i){if(e==="input"||e==="change")return Sc(i)}function tM(e,i){return e===i&&(e!==0||1/e===1/i)||e!==e&&i!==i}var ri=typeof Object.is=="function"?Object.is:tM;function sl(e,i){if(ri(e,i))return!0;if(typeof e!="object"||e===null||typeof i!="object"||i===null)return!1;var r=Object.keys(e),o=Object.keys(i);if(r.length!==o.length)return!1;for(o=0;o<r.length;o++){var u=r[o];if(!Be.call(i,u)||!ri(e[u],i[u]))return!1}return!0}function ag(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function sg(e,i){var r=ag(e);e=0;for(var o;r;){if(r.nodeType===3){if(o=e+r.textContent.length,e<=i&&o>=i)return{node:r,offset:i-e};e=o}t:{for(;r;){if(r.nextSibling){r=r.nextSibling;break t}r=r.parentNode}r=void 0}r=ag(r)}}function rg(e,i){return e&&i?e===i?!0:e&&e.nodeType===3?!1:i&&i.nodeType===3?rg(e,i.parentNode):"contains"in e?e.contains(i):e.compareDocumentPosition?!!(e.compareDocumentPosition(i)&16):!1:!1}function og(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var i=En(e.document);i instanceof e.HTMLIFrameElement;){try{var r=typeof i.contentWindow.location.href=="string"}catch{r=!1}if(r)e=i.contentWindow;else break;i=En(e.document)}return i}function Of(e){var i=e&&e.nodeName&&e.nodeName.toLowerCase();return i&&(i==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||i==="textarea"||e.contentEditable==="true")}var eM=sa&&"documentMode"in document&&11>=document.documentMode,Cr=null,Pf=null,rl=null,zf=!1;function lg(e,i,r){var o=r.window===r?r.document:r.nodeType===9?r:r.ownerDocument;zf||Cr==null||Cr!==En(o)||(o=Cr,"selectionStart"in o&&Of(o)?o={start:o.selectionStart,end:o.selectionEnd}:(o=(o.ownerDocument&&o.ownerDocument.defaultView||window).getSelection(),o={anchorNode:o.anchorNode,anchorOffset:o.anchorOffset,focusNode:o.focusNode,focusOffset:o.focusOffset}),rl&&sl(rl,o)||(rl=o,o=cu(Pf,"onSelect"),0<o.length&&(i=new yc("onSelect","select",null,i,r),e.push({event:i,listeners:o}),i.target=Cr)))}function Os(e,i){var r={};return r[e.toLowerCase()]=i.toLowerCase(),r["Webkit"+e]="webkit"+i,r["Moz"+e]="moz"+i,r}var Rr={animationend:Os("Animation","AnimationEnd"),animationiteration:Os("Animation","AnimationIteration"),animationstart:Os("Animation","AnimationStart"),transitionrun:Os("Transition","TransitionRun"),transitionstart:Os("Transition","TransitionStart"),transitioncancel:Os("Transition","TransitionCancel"),transitionend:Os("Transition","TransitionEnd")},If={},cg={};sa&&(cg=document.createElement("div").style,"AnimationEvent"in window||(delete Rr.animationend.animation,delete Rr.animationiteration.animation,delete Rr.animationstart.animation),"TransitionEvent"in window||delete Rr.transitionend.transition);function Ps(e){if(If[e])return If[e];if(!Rr[e])return e;var i=Rr[e],r;for(r in i)if(i.hasOwnProperty(r)&&r in cg)return If[e]=i[r];return e}var ug=Ps("animationend"),fg=Ps("animationiteration"),dg=Ps("animationstart"),nM=Ps("transitionrun"),iM=Ps("transitionstart"),aM=Ps("transitioncancel"),hg=Ps("transitionend"),pg=new Map,Bf="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Bf.push("scrollEnd");function Ni(e,i){pg.set(e,i),Pt(i,[e])}var Mc=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var i=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(i))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},yi=[],wr=0,Ff=0;function Ec(){for(var e=wr,i=Ff=wr=0;i<e;){var r=yi[i];yi[i++]=null;var o=yi[i];yi[i++]=null;var u=yi[i];yi[i++]=null;var h=yi[i];if(yi[i++]=null,o!==null&&u!==null){var M=o.pending;M===null?u.next=u:(u.next=M.next,M.next=u),o.pending=u}h!==0&&mg(r,u,h)}}function bc(e,i,r,o){yi[wr++]=e,yi[wr++]=i,yi[wr++]=r,yi[wr++]=o,Ff|=o,e.lanes|=o,e=e.alternate,e!==null&&(e.lanes|=o)}function Hf(e,i,r,o){return bc(e,i,r,o),Tc(e)}function zs(e,i){return bc(e,null,null,i),Tc(e)}function mg(e,i,r){e.lanes|=r;var o=e.alternate;o!==null&&(o.lanes|=r);for(var u=!1,h=e.return;h!==null;)h.childLanes|=r,o=h.alternate,o!==null&&(o.childLanes|=r),h.tag===22&&(e=h.stateNode,e===null||e._visibility&1||(u=!0)),e=h,h=h.return;return e.tag===3?(h=e.stateNode,u&&i!==null&&(u=31-ne(r),e=h.hiddenUpdates,o=e[u],o===null?e[u]=[i]:o.push(i),i.lane=r|536870912),h):null}function Tc(e){if(50<Rl)throw Rl=0,Qd=null,Error(s(185));for(var i=e.return;i!==null;)e=i,i=e.return;return e.tag===3?e.stateNode:null}var Dr={};function sM(e,i,r,o){this.tag=e,this.key=r,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=i,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=o,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function oi(e,i,r,o){return new sM(e,i,r,o)}function Gf(e){return e=e.prototype,!(!e||!e.isReactComponent)}function ra(e,i){var r=e.alternate;return r===null?(r=oi(e.tag,i,e.key,e.mode),r.elementType=e.elementType,r.type=e.type,r.stateNode=e.stateNode,r.alternate=e,e.alternate=r):(r.pendingProps=i,r.type=e.type,r.flags=0,r.subtreeFlags=0,r.deletions=null),r.flags=e.flags&65011712,r.childLanes=e.childLanes,r.lanes=e.lanes,r.child=e.child,r.memoizedProps=e.memoizedProps,r.memoizedState=e.memoizedState,r.updateQueue=e.updateQueue,i=e.dependencies,r.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext},r.sibling=e.sibling,r.index=e.index,r.ref=e.ref,r.refCleanup=e.refCleanup,r}function gg(e,i){e.flags&=65011714;var r=e.alternate;return r===null?(e.childLanes=0,e.lanes=i,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=r.childLanes,e.lanes=r.lanes,e.child=r.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=r.memoizedProps,e.memoizedState=r.memoizedState,e.updateQueue=r.updateQueue,e.type=r.type,i=r.dependencies,e.dependencies=i===null?null:{lanes:i.lanes,firstContext:i.firstContext}),e}function Ac(e,i,r,o,u,h){var M=0;if(o=e,typeof e=="function")Gf(e)&&(M=1);else if(typeof e=="string")M=u1(e,r,q.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case U:return e=oi(31,r,i,u),e.elementType=U,e.lanes=h,e;case T:return Is(r.children,u,h,i);case E:M=8,u|=24;break;case x:return e=oi(12,r,i,u|2),e.elementType=x,e.lanes=h,e;case V:return e=oi(13,r,i,u),e.elementType=V,e.lanes=h,e;case F:return e=oi(19,r,i,u),e.elementType=F,e.lanes=h,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case N:M=10;break t;case P:M=9;break t;case R:M=11;break t;case z:M=14;break t;case G:M=16,o=null;break t}M=29,r=Error(s(130,e===null?"null":typeof e,"")),o=null}return i=oi(M,r,i,u),i.elementType=e,i.type=o,i.lanes=h,i}function Is(e,i,r,o){return e=oi(7,e,o,i),e.lanes=r,e}function Vf(e,i,r){return e=oi(6,e,null,i),e.lanes=r,e}function vg(e){var i=oi(18,null,null,0);return i.stateNode=e,i}function kf(e,i,r){return i=oi(4,e.children!==null?e.children:[],e.key,i),i.lanes=r,i.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},i}var _g=new WeakMap;function xi(e,i){if(typeof e=="object"&&e!==null){var r=_g.get(e);return r!==void 0?r:(i={value:e,source:i,stack:Qt(i)},_g.set(e,i),i)}return{value:e,source:i,stack:Qt(i)}}var Nr=[],Ur=0,Cc=null,ol=0,Si=[],Mi=0,Ha=null,qi=1,Wi="";function oa(e,i){Nr[Ur++]=ol,Nr[Ur++]=Cc,Cc=e,ol=i}function yg(e,i,r){Si[Mi++]=qi,Si[Mi++]=Wi,Si[Mi++]=Ha,Ha=e;var o=qi;e=Wi;var u=32-ne(o)-1;o&=~(1<<u),r+=1;var h=32-ne(i)+u;if(30<h){var M=u-u%5;h=(o&(1<<M)-1).toString(32),o>>=M,u-=M,qi=1<<32-ne(i)+u|r<<u|o,Wi=h+e}else qi=1<<h|r<<u|o,Wi=e}function jf(e){e.return!==null&&(oa(e,1),yg(e,1,0))}function Xf(e){for(;e===Cc;)Cc=Nr[--Ur],Nr[Ur]=null,ol=Nr[--Ur],Nr[Ur]=null;for(;e===Ha;)Ha=Si[--Mi],Si[Mi]=null,Wi=Si[--Mi],Si[Mi]=null,qi=Si[--Mi],Si[Mi]=null}function xg(e,i){Si[Mi++]=qi,Si[Mi++]=Wi,Si[Mi++]=Ha,qi=i.id,Wi=i.overflow,Ha=e}var Dn=null,Ke=null,Ce=!1,Ga=null,Ei=!1,qf=Error(s(519));function Va(e){var i=Error(s(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw ll(xi(i,e)),qf}function Sg(e){var i=e.stateNode,r=e.type,o=e.memoizedProps;switch(i[sn]=e,i[wn]=o,r){case"dialog":xe("cancel",i),xe("close",i);break;case"iframe":case"object":case"embed":xe("load",i);break;case"video":case"audio":for(r=0;r<Dl.length;r++)xe(Dl[r],i);break;case"source":xe("error",i);break;case"img":case"image":case"link":xe("error",i),xe("load",i);break;case"details":xe("toggle",i);break;case"input":xe("invalid",i),Vn(i,o.value,o.defaultValue,o.checked,o.defaultChecked,o.type,o.name,!0);break;case"select":xe("invalid",i);break;case"textarea":xe("invalid",i),Xi(i,o.value,o.defaultValue,o.children)}r=o.children,typeof r!="string"&&typeof r!="number"&&typeof r!="bigint"||i.textContent===""+r||o.suppressHydrationWarning===!0||B_(i.textContent,r)?(o.popover!=null&&(xe("beforetoggle",i),xe("toggle",i)),o.onScroll!=null&&xe("scroll",i),o.onScrollEnd!=null&&xe("scrollend",i),o.onClick!=null&&(i.onclick=aa),i=!0):i=!1,i||Va(e,!0)}function Mg(e){for(Dn=e.return;Dn;)switch(Dn.tag){case 5:case 31:case 13:Ei=!1;return;case 27:case 3:Ei=!0;return;default:Dn=Dn.return}}function Lr(e){if(e!==Dn)return!1;if(!Ce)return Mg(e),Ce=!0,!1;var i=e.tag,r;if((r=i!==3&&i!==27)&&((r=i===5)&&(r=e.type,r=!(r!=="form"&&r!=="button")||uh(e.type,e.memoizedProps)),r=!r),r&&Ke&&Va(e),Mg(e),i===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ke=W_(e)}else if(i===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(317));Ke=W_(e)}else i===27?(i=Ke,ns(e.type)?(e=mh,mh=null,Ke=e):Ke=i):Ke=Dn?Ti(e.stateNode.nextSibling):null;return!0}function Bs(){Ke=Dn=null,Ce=!1}function Wf(){var e=Ga;return e!==null&&($n===null?$n=e:$n.push.apply($n,e),Ga=null),e}function ll(e){Ga===null?Ga=[e]:Ga.push(e)}var Yf=O(null),Fs=null,la=null;function ka(e,i,r){St(Yf,i._currentValue),i._currentValue=r}function ca(e){e._currentValue=Yf.current,nt(Yf)}function Qf(e,i,r){for(;e!==null;){var o=e.alternate;if((e.childLanes&i)!==i?(e.childLanes|=i,o!==null&&(o.childLanes|=i)):o!==null&&(o.childLanes&i)!==i&&(o.childLanes|=i),e===r)break;e=e.return}}function Zf(e,i,r,o){var u=e.child;for(u!==null&&(u.return=e);u!==null;){var h=u.dependencies;if(h!==null){var M=u.child;h=h.firstContext;t:for(;h!==null;){var A=h;h=u;for(var B=0;B<i.length;B++)if(A.context===i[B]){h.lanes|=r,A=h.alternate,A!==null&&(A.lanes|=r),Qf(h.return,r,e),o||(M=null);break t}h=A.next}}else if(u.tag===18){if(M=u.return,M===null)throw Error(s(341));M.lanes|=r,h=M.alternate,h!==null&&(h.lanes|=r),Qf(M,r,e),M=null}else M=u.child;if(M!==null)M.return=u;else for(M=u;M!==null;){if(M===e){M=null;break}if(u=M.sibling,u!==null){u.return=M.return,M=u;break}M=M.return}u=M}}function Or(e,i,r,o){e=null;for(var u=i,h=!1;u!==null;){if(!h){if((u.flags&524288)!==0)h=!0;else if((u.flags&262144)!==0)break}if(u.tag===10){var M=u.alternate;if(M===null)throw Error(s(387));if(M=M.memoizedProps,M!==null){var A=u.type;ri(u.pendingProps.value,M.value)||(e!==null?e.push(A):e=[A])}}else if(u===Mt.current){if(M=u.alternate,M===null)throw Error(s(387));M.memoizedState.memoizedState!==u.memoizedState.memoizedState&&(e!==null?e.push(Pl):e=[Pl])}u=u.return}e!==null&&Zf(i,e,r,o),i.flags|=262144}function Rc(e){for(e=e.firstContext;e!==null;){if(!ri(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Hs(e){Fs=e,la=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Nn(e){return Eg(Fs,e)}function wc(e,i){return Fs===null&&Hs(e),Eg(e,i)}function Eg(e,i){var r=i._currentValue;if(i={context:i,memoizedValue:r,next:null},la===null){if(e===null)throw Error(s(308));la=i,e.dependencies={lanes:0,firstContext:i},e.flags|=524288}else la=la.next=i;return r}var rM=typeof AbortController<"u"?AbortController:function(){var e=[],i=this.signal={aborted:!1,addEventListener:function(r,o){e.push(o)}};this.abort=function(){i.aborted=!0,e.forEach(function(r){return r()})}},oM=a.unstable_scheduleCallback,lM=a.unstable_NormalPriority,hn={$$typeof:N,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Kf(){return{controller:new rM,data:new Map,refCount:0}}function cl(e){e.refCount--,e.refCount===0&&oM(lM,function(){e.controller.abort()})}var ul=null,Jf=0,Pr=0,zr=null;function cM(e,i){if(ul===null){var r=ul=[];Jf=0,Pr=eh(),zr={status:"pending",value:void 0,then:function(o){r.push(o)}}}return Jf++,i.then(bg,bg),i}function bg(){if(--Jf===0&&ul!==null){zr!==null&&(zr.status="fulfilled");var e=ul;ul=null,Pr=0,zr=null;for(var i=0;i<e.length;i++)(0,e[i])()}}function uM(e,i){var r=[],o={status:"pending",value:null,reason:null,then:function(u){r.push(u)}};return e.then(function(){o.status="fulfilled",o.value=i;for(var u=0;u<r.length;u++)(0,r[u])(i)},function(u){for(o.status="rejected",o.reason=u,u=0;u<r.length;u++)(0,r[u])(void 0)}),o}var Tg=I.S;I.S=function(e,i){l_=pt(),typeof i=="object"&&i!==null&&typeof i.then=="function"&&cM(e,i),Tg!==null&&Tg(e,i)};var Gs=O(null);function $f(){var e=Gs.current;return e!==null?e:Qe.pooledCache}function Dc(e,i){i===null?St(Gs,Gs.current):St(Gs,i.pool)}function Ag(){var e=$f();return e===null?null:{parent:hn._currentValue,pool:e}}var Ir=Error(s(460)),td=Error(s(474)),Nc=Error(s(542)),Uc={then:function(){}};function Cg(e){return e=e.status,e==="fulfilled"||e==="rejected"}function Rg(e,i,r){switch(r=e[r],r===void 0?e.push(i):r!==i&&(i.then(aa,aa),i=r),i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Dg(e),e;default:if(typeof i.status=="string")i.then(aa,aa);else{if(e=Qe,e!==null&&100<e.shellSuspendCounter)throw Error(s(482));e=i,e.status="pending",e.then(function(o){if(i.status==="pending"){var u=i;u.status="fulfilled",u.value=o}},function(o){if(i.status==="pending"){var u=i;u.status="rejected",u.reason=o}})}switch(i.status){case"fulfilled":return i.value;case"rejected":throw e=i.reason,Dg(e),e}throw ks=i,Ir}}function Vs(e){try{var i=e._init;return i(e._payload)}catch(r){throw r!==null&&typeof r=="object"&&typeof r.then=="function"?(ks=r,Ir):r}}var ks=null;function wg(){if(ks===null)throw Error(s(459));var e=ks;return ks=null,e}function Dg(e){if(e===Ir||e===Nc)throw Error(s(483))}var Br=null,fl=0;function Lc(e){var i=fl;return fl+=1,Br===null&&(Br=[]),Rg(Br,e,i)}function dl(e,i){i=i.props.ref,e.ref=i!==void 0?i:null}function Oc(e,i){throw i.$$typeof===y?Error(s(525)):(e=Object.prototype.toString.call(i),Error(s(31,e==="[object Object]"?"object with keys {"+Object.keys(i).join(", ")+"}":e)))}function Ng(e){function i(J,j){if(e){var tt=J.deletions;tt===null?(J.deletions=[j],J.flags|=16):tt.push(j)}}function r(J,j){if(!e)return null;for(;j!==null;)i(J,j),j=j.sibling;return null}function o(J){for(var j=new Map;J!==null;)J.key!==null?j.set(J.key,J):j.set(J.index,J),J=J.sibling;return j}function u(J,j){return J=ra(J,j),J.index=0,J.sibling=null,J}function h(J,j,tt){return J.index=tt,e?(tt=J.alternate,tt!==null?(tt=tt.index,tt<j?(J.flags|=67108866,j):tt):(J.flags|=67108866,j)):(J.flags|=1048576,j)}function M(J){return e&&J.alternate===null&&(J.flags|=67108866),J}function A(J,j,tt,gt){return j===null||j.tag!==6?(j=Vf(tt,J.mode,gt),j.return=J,j):(j=u(j,tt),j.return=J,j)}function B(J,j,tt,gt){var Jt=tt.type;return Jt===T?ht(J,j,tt.props.children,gt,tt.key):j!==null&&(j.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Vs(Jt)===j.type)?(j=u(j,tt.props),dl(j,tt),j.return=J,j):(j=Ac(tt.type,tt.key,tt.props,null,J.mode,gt),dl(j,tt),j.return=J,j)}function et(J,j,tt,gt){return j===null||j.tag!==4||j.stateNode.containerInfo!==tt.containerInfo||j.stateNode.implementation!==tt.implementation?(j=kf(tt,J.mode,gt),j.return=J,j):(j=u(j,tt.children||[]),j.return=J,j)}function ht(J,j,tt,gt,Jt){return j===null||j.tag!==7?(j=Is(tt,J.mode,gt,Jt),j.return=J,j):(j=u(j,tt),j.return=J,j)}function _t(J,j,tt){if(typeof j=="string"&&j!==""||typeof j=="number"||typeof j=="bigint")return j=Vf(""+j,J.mode,tt),j.return=J,j;if(typeof j=="object"&&j!==null){switch(j.$$typeof){case S:return tt=Ac(j.type,j.key,j.props,null,J.mode,tt),dl(tt,j),tt.return=J,tt;case b:return j=kf(j,J.mode,tt),j.return=J,j;case G:return j=Vs(j),_t(J,j,tt)}if(ct(j)||ut(j))return j=Is(j,J.mode,tt,null),j.return=J,j;if(typeof j.then=="function")return _t(J,Lc(j),tt);if(j.$$typeof===N)return _t(J,wc(J,j),tt);Oc(J,j)}return null}function it(J,j,tt,gt){var Jt=j!==null?j.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return Jt!==null?null:A(J,j,""+tt,gt);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case S:return tt.key===Jt?B(J,j,tt,gt):null;case b:return tt.key===Jt?et(J,j,tt,gt):null;case G:return tt=Vs(tt),it(J,j,tt,gt)}if(ct(tt)||ut(tt))return Jt!==null?null:ht(J,j,tt,gt,null);if(typeof tt.then=="function")return it(J,j,Lc(tt),gt);if(tt.$$typeof===N)return it(J,j,wc(J,tt),gt);Oc(J,tt)}return null}function lt(J,j,tt,gt,Jt){if(typeof gt=="string"&&gt!==""||typeof gt=="number"||typeof gt=="bigint")return J=J.get(tt)||null,A(j,J,""+gt,Jt);if(typeof gt=="object"&&gt!==null){switch(gt.$$typeof){case S:return J=J.get(gt.key===null?tt:gt.key)||null,B(j,J,gt,Jt);case b:return J=J.get(gt.key===null?tt:gt.key)||null,et(j,J,gt,Jt);case G:return gt=Vs(gt),lt(J,j,tt,gt,Jt)}if(ct(gt)||ut(gt))return J=J.get(tt)||null,ht(j,J,gt,Jt,null);if(typeof gt.then=="function")return lt(J,j,tt,Lc(gt),Jt);if(gt.$$typeof===N)return lt(J,j,tt,wc(j,gt),Jt);Oc(j,gt)}return null}function Gt(J,j,tt,gt){for(var Jt=null,Ue=null,jt=j,fe=j=0,Te=null;jt!==null&&fe<tt.length;fe++){jt.index>fe?(Te=jt,jt=null):Te=jt.sibling;var Le=it(J,jt,tt[fe],gt);if(Le===null){jt===null&&(jt=Te);break}e&&jt&&Le.alternate===null&&i(J,jt),j=h(Le,j,fe),Ue===null?Jt=Le:Ue.sibling=Le,Ue=Le,jt=Te}if(fe===tt.length)return r(J,jt),Ce&&oa(J,fe),Jt;if(jt===null){for(;fe<tt.length;fe++)jt=_t(J,tt[fe],gt),jt!==null&&(j=h(jt,j,fe),Ue===null?Jt=jt:Ue.sibling=jt,Ue=jt);return Ce&&oa(J,fe),Jt}for(jt=o(jt);fe<tt.length;fe++)Te=lt(jt,J,fe,tt[fe],gt),Te!==null&&(e&&Te.alternate!==null&&jt.delete(Te.key===null?fe:Te.key),j=h(Te,j,fe),Ue===null?Jt=Te:Ue.sibling=Te,Ue=Te);return e&&jt.forEach(function(os){return i(J,os)}),Ce&&oa(J,fe),Jt}function ee(J,j,tt,gt){if(tt==null)throw Error(s(151));for(var Jt=null,Ue=null,jt=j,fe=j=0,Te=null,Le=tt.next();jt!==null&&!Le.done;fe++,Le=tt.next()){jt.index>fe?(Te=jt,jt=null):Te=jt.sibling;var os=it(J,jt,Le.value,gt);if(os===null){jt===null&&(jt=Te);break}e&&jt&&os.alternate===null&&i(J,jt),j=h(os,j,fe),Ue===null?Jt=os:Ue.sibling=os,Ue=os,jt=Te}if(Le.done)return r(J,jt),Ce&&oa(J,fe),Jt;if(jt===null){for(;!Le.done;fe++,Le=tt.next())Le=_t(J,Le.value,gt),Le!==null&&(j=h(Le,j,fe),Ue===null?Jt=Le:Ue.sibling=Le,Ue=Le);return Ce&&oa(J,fe),Jt}for(jt=o(jt);!Le.done;fe++,Le=tt.next())Le=lt(jt,J,fe,Le.value,gt),Le!==null&&(e&&Le.alternate!==null&&jt.delete(Le.key===null?fe:Le.key),j=h(Le,j,fe),Ue===null?Jt=Le:Ue.sibling=Le,Ue=Le);return e&&jt.forEach(function(S1){return i(J,S1)}),Ce&&oa(J,fe),Jt}function Xe(J,j,tt,gt){if(typeof tt=="object"&&tt!==null&&tt.type===T&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case S:t:{for(var Jt=tt.key;j!==null;){if(j.key===Jt){if(Jt=tt.type,Jt===T){if(j.tag===7){r(J,j.sibling),gt=u(j,tt.props.children),gt.return=J,J=gt;break t}}else if(j.elementType===Jt||typeof Jt=="object"&&Jt!==null&&Jt.$$typeof===G&&Vs(Jt)===j.type){r(J,j.sibling),gt=u(j,tt.props),dl(gt,tt),gt.return=J,J=gt;break t}r(J,j);break}else i(J,j);j=j.sibling}tt.type===T?(gt=Is(tt.props.children,J.mode,gt,tt.key),gt.return=J,J=gt):(gt=Ac(tt.type,tt.key,tt.props,null,J.mode,gt),dl(gt,tt),gt.return=J,J=gt)}return M(J);case b:t:{for(Jt=tt.key;j!==null;){if(j.key===Jt)if(j.tag===4&&j.stateNode.containerInfo===tt.containerInfo&&j.stateNode.implementation===tt.implementation){r(J,j.sibling),gt=u(j,tt.children||[]),gt.return=J,J=gt;break t}else{r(J,j);break}else i(J,j);j=j.sibling}gt=kf(tt,J.mode,gt),gt.return=J,J=gt}return M(J);case G:return tt=Vs(tt),Xe(J,j,tt,gt)}if(ct(tt))return Gt(J,j,tt,gt);if(ut(tt)){if(Jt=ut(tt),typeof Jt!="function")throw Error(s(150));return tt=Jt.call(tt),ee(J,j,tt,gt)}if(typeof tt.then=="function")return Xe(J,j,Lc(tt),gt);if(tt.$$typeof===N)return Xe(J,j,wc(J,tt),gt);Oc(J,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,j!==null&&j.tag===6?(r(J,j.sibling),gt=u(j,tt),gt.return=J,J=gt):(r(J,j),gt=Vf(tt,J.mode,gt),gt.return=J,J=gt),M(J)):r(J,j)}return function(J,j,tt,gt){try{fl=0;var Jt=Xe(J,j,tt,gt);return Br=null,Jt}catch(jt){if(jt===Ir||jt===Nc)throw jt;var Ue=oi(29,jt,null,J.mode);return Ue.lanes=gt,Ue.return=J,Ue}finally{}}}var js=Ng(!0),Ug=Ng(!1),ja=!1;function ed(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function nd(e,i){e=e.updateQueue,i.updateQueue===e&&(i.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Xa(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function qa(e,i,r){var o=e.updateQueue;if(o===null)return null;if(o=o.shared,(Pe&2)!==0){var u=o.pending;return u===null?i.next=i:(i.next=u.next,u.next=i),o.pending=i,i=Tc(e),mg(e,null,r),i}return bc(e,o,i,r),Tc(e)}function hl(e,i,r){if(i=i.updateQueue,i!==null&&(i=i.shared,(r&4194048)!==0)){var o=i.lanes;o&=e.pendingLanes,r|=o,i.lanes=r,Qo(e,r)}}function id(e,i){var r=e.updateQueue,o=e.alternate;if(o!==null&&(o=o.updateQueue,r===o)){var u=null,h=null;if(r=r.firstBaseUpdate,r!==null){do{var M={lane:r.lane,tag:r.tag,payload:r.payload,callback:null,next:null};h===null?u=h=M:h=h.next=M,r=r.next}while(r!==null);h===null?u=h=i:h=h.next=i}else u=h=i;r={baseState:o.baseState,firstBaseUpdate:u,lastBaseUpdate:h,shared:o.shared,callbacks:o.callbacks},e.updateQueue=r;return}e=r.lastBaseUpdate,e===null?r.firstBaseUpdate=i:e.next=i,r.lastBaseUpdate=i}var ad=!1;function pl(){if(ad){var e=zr;if(e!==null)throw e}}function ml(e,i,r,o){ad=!1;var u=e.updateQueue;ja=!1;var h=u.firstBaseUpdate,M=u.lastBaseUpdate,A=u.shared.pending;if(A!==null){u.shared.pending=null;var B=A,et=B.next;B.next=null,M===null?h=et:M.next=et,M=B;var ht=e.alternate;ht!==null&&(ht=ht.updateQueue,A=ht.lastBaseUpdate,A!==M&&(A===null?ht.firstBaseUpdate=et:A.next=et,ht.lastBaseUpdate=B))}if(h!==null){var _t=u.baseState;M=0,ht=et=B=null,A=h;do{var it=A.lane&-536870913,lt=it!==A.lane;if(lt?(be&it)===it:(o&it)===it){it!==0&&it===Pr&&(ad=!0),ht!==null&&(ht=ht.next={lane:0,tag:A.tag,payload:A.payload,callback:null,next:null});t:{var Gt=e,ee=A;it=i;var Xe=r;switch(ee.tag){case 1:if(Gt=ee.payload,typeof Gt=="function"){_t=Gt.call(Xe,_t,it);break t}_t=Gt;break t;case 3:Gt.flags=Gt.flags&-65537|128;case 0:if(Gt=ee.payload,it=typeof Gt=="function"?Gt.call(Xe,_t,it):Gt,it==null)break t;_t=_({},_t,it);break t;case 2:ja=!0}}it=A.callback,it!==null&&(e.flags|=64,lt&&(e.flags|=8192),lt=u.callbacks,lt===null?u.callbacks=[it]:lt.push(it))}else lt={lane:it,tag:A.tag,payload:A.payload,callback:A.callback,next:null},ht===null?(et=ht=lt,B=_t):ht=ht.next=lt,M|=it;if(A=A.next,A===null){if(A=u.shared.pending,A===null)break;lt=A,A=lt.next,lt.next=null,u.lastBaseUpdate=lt,u.shared.pending=null}}while(!0);ht===null&&(B=_t),u.baseState=B,u.firstBaseUpdate=et,u.lastBaseUpdate=ht,h===null&&(u.shared.lanes=0),Ka|=M,e.lanes=M,e.memoizedState=_t}}function Lg(e,i){if(typeof e!="function")throw Error(s(191,e));e.call(i)}function Og(e,i){var r=e.callbacks;if(r!==null)for(e.callbacks=null,e=0;e<r.length;e++)Lg(r[e],i)}var Fr=O(null),Pc=O(0);function Pg(e,i){e=_a,St(Pc,e),St(Fr,i),_a=e|i.baseLanes}function sd(){St(Pc,_a),St(Fr,Fr.current)}function rd(){_a=Pc.current,nt(Fr),nt(Pc)}var li=O(null),bi=null;function Wa(e){var i=e.alternate;St(un,un.current&1),St(li,e),bi===null&&(i===null||Fr.current!==null||i.memoizedState!==null)&&(bi=e)}function od(e){St(un,un.current),St(li,e),bi===null&&(bi=e)}function zg(e){e.tag===22?(St(un,un.current),St(li,e),bi===null&&(bi=e)):Ya()}function Ya(){St(un,un.current),St(li,li.current)}function ci(e){nt(li),bi===e&&(bi=null),nt(un)}var un=O(0);function zc(e){for(var i=e;i!==null;){if(i.tag===13){var r=i.memoizedState;if(r!==null&&(r=r.dehydrated,r===null||hh(r)||ph(r)))return i}else if(i.tag===19&&(i.memoizedProps.revealOrder==="forwards"||i.memoizedProps.revealOrder==="backwards"||i.memoizedProps.revealOrder==="unstable_legacy-backwards"||i.memoizedProps.revealOrder==="together")){if((i.flags&128)!==0)return i}else if(i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return null;i=i.return}i.sibling.return=i.return,i=i.sibling}return null}var ua=0,ue=null,ke=null,pn=null,Ic=!1,Hr=!1,Xs=!1,Bc=0,gl=0,Gr=null,fM=0;function rn(){throw Error(s(321))}function ld(e,i){if(i===null)return!1;for(var r=0;r<i.length&&r<e.length;r++)if(!ri(e[r],i[r]))return!1;return!0}function cd(e,i,r,o,u,h){return ua=h,ue=i,i.memoizedState=null,i.updateQueue=null,i.lanes=0,I.H=e===null||e.memoizedState===null?yv:bd,Xs=!1,h=r(o,u),Xs=!1,Hr&&(h=Bg(i,r,o,u)),Ig(e),h}function Ig(e){I.H=yl;var i=ke!==null&&ke.next!==null;if(ua=0,pn=ke=ue=null,Ic=!1,gl=0,Gr=null,i)throw Error(s(300));e===null||mn||(e=e.dependencies,e!==null&&Rc(e)&&(mn=!0))}function Bg(e,i,r,o){ue=e;var u=0;do{if(Hr&&(Gr=null),gl=0,Hr=!1,25<=u)throw Error(s(301));if(u+=1,pn=ke=null,e.updateQueue!=null){var h=e.updateQueue;h.lastEffect=null,h.events=null,h.stores=null,h.memoCache!=null&&(h.memoCache.index=0)}I.H=xv,h=i(r,o)}while(Hr);return h}function dM(){var e=I.H,i=e.useState()[0];return i=typeof i.then=="function"?vl(i):i,e=e.useState()[0],(ke!==null?ke.memoizedState:null)!==e&&(ue.flags|=1024),i}function ud(){var e=Bc!==0;return Bc=0,e}function fd(e,i,r){i.updateQueue=e.updateQueue,i.flags&=-2053,e.lanes&=~r}function dd(e){if(Ic){for(e=e.memoizedState;e!==null;){var i=e.queue;i!==null&&(i.pending=null),e=e.next}Ic=!1}ua=0,pn=ke=ue=null,Hr=!1,gl=Bc=0,Gr=null}function kn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return pn===null?ue.memoizedState=pn=e:pn=pn.next=e,pn}function fn(){if(ke===null){var e=ue.alternate;e=e!==null?e.memoizedState:null}else e=ke.next;var i=pn===null?ue.memoizedState:pn.next;if(i!==null)pn=i,ke=e;else{if(e===null)throw ue.alternate===null?Error(s(467)):Error(s(310));ke=e,e={memoizedState:ke.memoizedState,baseState:ke.baseState,baseQueue:ke.baseQueue,queue:ke.queue,next:null},pn===null?ue.memoizedState=pn=e:pn=pn.next=e}return pn}function Fc(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function vl(e){var i=gl;return gl+=1,Gr===null&&(Gr=[]),e=Rg(Gr,e,i),i=ue,(pn===null?i.memoizedState:pn.next)===null&&(i=i.alternate,I.H=i===null||i.memoizedState===null?yv:bd),e}function Hc(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return vl(e);if(e.$$typeof===N)return Nn(e)}throw Error(s(438,String(e)))}function hd(e){var i=null,r=ue.updateQueue;if(r!==null&&(i=r.memoCache),i==null){var o=ue.alternate;o!==null&&(o=o.updateQueue,o!==null&&(o=o.memoCache,o!=null&&(i={data:o.data.map(function(u){return u.slice()}),index:0})))}if(i==null&&(i={data:[],index:0}),r===null&&(r=Fc(),ue.updateQueue=r),r.memoCache=i,r=i.data[i.index],r===void 0)for(r=i.data[i.index]=Array(e),o=0;o<e;o++)r[o]=D;return i.index++,r}function fa(e,i){return typeof i=="function"?i(e):i}function Gc(e){var i=fn();return pd(i,ke,e)}function pd(e,i,r){var o=e.queue;if(o===null)throw Error(s(311));o.lastRenderedReducer=r;var u=e.baseQueue,h=o.pending;if(h!==null){if(u!==null){var M=u.next;u.next=h.next,h.next=M}i.baseQueue=u=h,o.pending=null}if(h=e.baseState,u===null)e.memoizedState=h;else{i=u.next;var A=M=null,B=null,et=i,ht=!1;do{var _t=et.lane&-536870913;if(_t!==et.lane?(be&_t)===_t:(ua&_t)===_t){var it=et.revertLane;if(it===0)B!==null&&(B=B.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),_t===Pr&&(ht=!0);else if((ua&it)===it){et=et.next,it===Pr&&(ht=!0);continue}else _t={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(A=B=_t,M=h):B=B.next=_t,ue.lanes|=it,Ka|=it;_t=et.action,Xs&&r(h,_t),h=et.hasEagerState?et.eagerState:r(h,_t)}else it={lane:_t,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(A=B=it,M=h):B=B.next=it,ue.lanes|=_t,Ka|=_t;et=et.next}while(et!==null&&et!==i);if(B===null?M=h:B.next=A,!ri(h,e.memoizedState)&&(mn=!0,ht&&(r=zr,r!==null)))throw r;e.memoizedState=h,e.baseState=M,e.baseQueue=B,o.lastRenderedState=h}return u===null&&(o.lanes=0),[e.memoizedState,o.dispatch]}function md(e){var i=fn(),r=i.queue;if(r===null)throw Error(s(311));r.lastRenderedReducer=e;var o=r.dispatch,u=r.pending,h=i.memoizedState;if(u!==null){r.pending=null;var M=u=u.next;do h=e(h,M.action),M=M.next;while(M!==u);ri(h,i.memoizedState)||(mn=!0),i.memoizedState=h,i.baseQueue===null&&(i.baseState=h),r.lastRenderedState=h}return[h,o]}function Fg(e,i,r){var o=ue,u=fn(),h=Ce;if(h){if(r===void 0)throw Error(s(407));r=r()}else r=i();var M=!ri((ke||u).memoizedState,r);if(M&&(u.memoizedState=r,mn=!0),u=u.queue,_d(Vg.bind(null,o,u,e),[e]),u.getSnapshot!==i||M||pn!==null&&pn.memoizedState.tag&1){if(o.flags|=2048,Vr(9,{destroy:void 0},Gg.bind(null,o,u,r,i),null),Qe===null)throw Error(s(349));h||(ua&127)!==0||Hg(o,i,r)}return r}function Hg(e,i,r){e.flags|=16384,e={getSnapshot:i,value:r},i=ue.updateQueue,i===null?(i=Fc(),ue.updateQueue=i,i.stores=[e]):(r=i.stores,r===null?i.stores=[e]:r.push(e))}function Gg(e,i,r,o){i.value=r,i.getSnapshot=o,kg(i)&&jg(e)}function Vg(e,i,r){return r(function(){kg(i)&&jg(e)})}function kg(e){var i=e.getSnapshot;e=e.value;try{var r=i();return!ri(e,r)}catch{return!0}}function jg(e){var i=zs(e,2);i!==null&&ti(i,e,2)}function gd(e){var i=kn();if(typeof e=="function"){var r=e;if(e=r(),Xs){Ot(!0);try{r()}finally{Ot(!1)}}}return i.memoizedState=i.baseState=e,i.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:e},i}function Xg(e,i,r,o){return e.baseState=r,pd(e,ke,typeof o=="function"?o:fa)}function hM(e,i,r,o,u){if(jc(e))throw Error(s(485));if(e=i.action,e!==null){var h={payload:u,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(M){h.listeners.push(M)}};I.T!==null?r(!0):h.isTransition=!1,o(h),r=i.pending,r===null?(h.next=i.pending=h,qg(i,h)):(h.next=r.next,i.pending=r.next=h)}}function qg(e,i){var r=i.action,o=i.payload,u=e.state;if(i.isTransition){var h=I.T,M={};I.T=M;try{var A=r(u,o),B=I.S;B!==null&&B(M,A),Wg(e,i,A)}catch(et){vd(e,i,et)}finally{h!==null&&M.types!==null&&(h.types=M.types),I.T=h}}else try{h=r(u,o),Wg(e,i,h)}catch(et){vd(e,i,et)}}function Wg(e,i,r){r!==null&&typeof r=="object"&&typeof r.then=="function"?r.then(function(o){Yg(e,i,o)},function(o){return vd(e,i,o)}):Yg(e,i,r)}function Yg(e,i,r){i.status="fulfilled",i.value=r,Qg(i),e.state=r,i=e.pending,i!==null&&(r=i.next,r===i?e.pending=null:(r=r.next,i.next=r,qg(e,r)))}function vd(e,i,r){var o=e.pending;if(e.pending=null,o!==null){o=o.next;do i.status="rejected",i.reason=r,Qg(i),i=i.next;while(i!==o)}e.action=null}function Qg(e){e=e.listeners;for(var i=0;i<e.length;i++)(0,e[i])()}function Zg(e,i){return i}function Kg(e,i){if(Ce){var r=Qe.formState;if(r!==null){t:{var o=ue;if(Ce){if(Ke){e:{for(var u=Ke,h=Ei;u.nodeType!==8;){if(!h){u=null;break e}if(u=Ti(u.nextSibling),u===null){u=null;break e}}h=u.data,u=h==="F!"||h==="F"?u:null}if(u){Ke=Ti(u.nextSibling),o=u.data==="F!";break t}}Va(o)}o=!1}o&&(i=r[0])}}return r=kn(),r.memoizedState=r.baseState=i,o={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Zg,lastRenderedState:i},r.queue=o,r=gv.bind(null,ue,o),o.dispatch=r,o=gd(!1),h=Ed.bind(null,ue,!1,o.queue),o=kn(),u={state:i,dispatch:null,action:e,pending:null},o.queue=u,r=hM.bind(null,ue,u,h,r),u.dispatch=r,o.memoizedState=e,[i,r,!1]}function Jg(e){var i=fn();return $g(i,ke,e)}function $g(e,i,r){if(i=pd(e,i,Zg)[0],e=Gc(fa)[0],typeof i=="object"&&i!==null&&typeof i.then=="function")try{var o=vl(i)}catch(M){throw M===Ir?Nc:M}else o=i;i=fn();var u=i.queue,h=u.dispatch;return r!==i.memoizedState&&(ue.flags|=2048,Vr(9,{destroy:void 0},pM.bind(null,u,r),null)),[o,h,e]}function pM(e,i){e.action=i}function tv(e){var i=fn(),r=ke;if(r!==null)return $g(i,r,e);fn(),i=i.memoizedState,r=fn();var o=r.queue.dispatch;return r.memoizedState=e,[i,o,!1]}function Vr(e,i,r,o){return e={tag:e,create:r,deps:o,inst:i,next:null},i=ue.updateQueue,i===null&&(i=Fc(),ue.updateQueue=i),r=i.lastEffect,r===null?i.lastEffect=e.next=e:(o=r.next,r.next=e,e.next=o,i.lastEffect=e),e}function ev(){return fn().memoizedState}function Vc(e,i,r,o){var u=kn();ue.flags|=e,u.memoizedState=Vr(1|i,{destroy:void 0},r,o===void 0?null:o)}function kc(e,i,r,o){var u=fn();o=o===void 0?null:o;var h=u.memoizedState.inst;ke!==null&&o!==null&&ld(o,ke.memoizedState.deps)?u.memoizedState=Vr(i,h,r,o):(ue.flags|=e,u.memoizedState=Vr(1|i,h,r,o))}function nv(e,i){Vc(8390656,8,e,i)}function _d(e,i){kc(2048,8,e,i)}function mM(e){ue.flags|=4;var i=ue.updateQueue;if(i===null)i=Fc(),ue.updateQueue=i,i.events=[e];else{var r=i.events;r===null?i.events=[e]:r.push(e)}}function iv(e){var i=fn().memoizedState;return mM({ref:i,nextImpl:e}),function(){if((Pe&2)!==0)throw Error(s(440));return i.impl.apply(void 0,arguments)}}function av(e,i){return kc(4,2,e,i)}function sv(e,i){return kc(4,4,e,i)}function rv(e,i){if(typeof i=="function"){e=e();var r=i(e);return function(){typeof r=="function"?r():i(null)}}if(i!=null)return e=e(),i.current=e,function(){i.current=null}}function ov(e,i,r){r=r!=null?r.concat([e]):null,kc(4,4,rv.bind(null,i,e),r)}function yd(){}function lv(e,i){var r=fn();i=i===void 0?null:i;var o=r.memoizedState;return i!==null&&ld(i,o[1])?o[0]:(r.memoizedState=[e,i],e)}function cv(e,i){var r=fn();i=i===void 0?null:i;var o=r.memoizedState;if(i!==null&&ld(i,o[1]))return o[0];if(o=e(),Xs){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[o,i],o}function xd(e,i,r){return r===void 0||(ua&1073741824)!==0&&(be&261930)===0?e.memoizedState=i:(e.memoizedState=r,e=u_(),ue.lanes|=e,Ka|=e,r)}function uv(e,i,r,o){return ri(r,i)?r:Fr.current!==null?(e=xd(e,r,o),ri(e,i)||(mn=!0),e):(ua&42)===0||(ua&1073741824)!==0&&(be&261930)===0?(mn=!0,e.memoizedState=r):(e=u_(),ue.lanes|=e,Ka|=e,i)}function fv(e,i,r,o,u){var h=Z.p;Z.p=h!==0&&8>h?h:8;var M=I.T,A={};I.T=A,Ed(e,!1,i,r);try{var B=u(),et=I.S;if(et!==null&&et(A,B),B!==null&&typeof B=="object"&&typeof B.then=="function"){var ht=uM(B,o);_l(e,i,ht,di(e))}else _l(e,i,o,di(e))}catch(_t){_l(e,i,{then:function(){},status:"rejected",reason:_t},di())}finally{Z.p=h,M!==null&&A.types!==null&&(M.types=A.types),I.T=M}}function gM(){}function Sd(e,i,r,o){if(e.tag!==5)throw Error(s(476));var u=dv(e).queue;fv(e,u,i,$,r===null?gM:function(){return hv(e),r(o)})}function dv(e){var i=e.memoizedState;if(i!==null)return i;i={memoizedState:$,baseState:$,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:$},next:null};var r={};return i.next={memoizedState:r,baseState:r,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:fa,lastRenderedState:r},next:null},e.memoizedState=i,e=e.alternate,e!==null&&(e.memoizedState=i),i}function hv(e){var i=dv(e);i.next===null&&(i=e.alternate.memoizedState),_l(e,i.next.queue,{},di())}function Md(){return Nn(Pl)}function pv(){return fn().memoizedState}function mv(){return fn().memoizedState}function vM(e){for(var i=e.return;i!==null;){switch(i.tag){case 24:case 3:var r=di();e=Xa(r);var o=qa(i,e,r);o!==null&&(ti(o,i,r),hl(o,i,r)),i={cache:Kf()},e.payload=i;return}i=i.return}}function _M(e,i,r){var o=di();r={lane:o,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},jc(e)?vv(i,r):(r=Hf(e,i,r,o),r!==null&&(ti(r,e,o),_v(r,i,o)))}function gv(e,i,r){var o=di();_l(e,i,r,o)}function _l(e,i,r,o){var u={lane:o,revertLane:0,gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null};if(jc(e))vv(i,u);else{var h=e.alternate;if(e.lanes===0&&(h===null||h.lanes===0)&&(h=i.lastRenderedReducer,h!==null))try{var M=i.lastRenderedState,A=h(M,r);if(u.hasEagerState=!0,u.eagerState=A,ri(A,M))return bc(e,i,u,0),Qe===null&&Ec(),!1}catch{}finally{}if(r=Hf(e,i,u,o),r!==null)return ti(r,e,o),_v(r,i,o),!0}return!1}function Ed(e,i,r,o){if(o={lane:2,revertLane:eh(),gesture:null,action:o,hasEagerState:!1,eagerState:null,next:null},jc(e)){if(i)throw Error(s(479))}else i=Hf(e,r,o,2),i!==null&&ti(i,e,2)}function jc(e){var i=e.alternate;return e===ue||i!==null&&i===ue}function vv(e,i){Hr=Ic=!0;var r=e.pending;r===null?i.next=i:(i.next=r.next,r.next=i),e.pending=i}function _v(e,i,r){if((r&4194048)!==0){var o=i.lanes;o&=e.pendingLanes,r|=o,i.lanes=r,Qo(e,r)}}var yl={readContext:Nn,use:Hc,useCallback:rn,useContext:rn,useEffect:rn,useImperativeHandle:rn,useLayoutEffect:rn,useInsertionEffect:rn,useMemo:rn,useReducer:rn,useRef:rn,useState:rn,useDebugValue:rn,useDeferredValue:rn,useTransition:rn,useSyncExternalStore:rn,useId:rn,useHostTransitionStatus:rn,useFormState:rn,useActionState:rn,useOptimistic:rn,useMemoCache:rn,useCacheRefresh:rn};yl.useEffectEvent=rn;var yv={readContext:Nn,use:Hc,useCallback:function(e,i){return kn().memoizedState=[e,i===void 0?null:i],e},useContext:Nn,useEffect:nv,useImperativeHandle:function(e,i,r){r=r!=null?r.concat([e]):null,Vc(4194308,4,rv.bind(null,i,e),r)},useLayoutEffect:function(e,i){return Vc(4194308,4,e,i)},useInsertionEffect:function(e,i){Vc(4,2,e,i)},useMemo:function(e,i){var r=kn();i=i===void 0?null:i;var o=e();if(Xs){Ot(!0);try{e()}finally{Ot(!1)}}return r.memoizedState=[o,i],o},useReducer:function(e,i,r){var o=kn();if(r!==void 0){var u=r(i);if(Xs){Ot(!0);try{r(i)}finally{Ot(!1)}}}else u=i;return o.memoizedState=o.baseState=u,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:u},o.queue=e,e=e.dispatch=_M.bind(null,ue,e),[o.memoizedState,e]},useRef:function(e){var i=kn();return e={current:e},i.memoizedState=e},useState:function(e){e=gd(e);var i=e.queue,r=gv.bind(null,ue,i);return i.dispatch=r,[e.memoizedState,r]},useDebugValue:yd,useDeferredValue:function(e,i){var r=kn();return xd(r,e,i)},useTransition:function(){var e=gd(!1);return e=fv.bind(null,ue,e.queue,!0,!1),kn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,i,r){var o=ue,u=kn();if(Ce){if(r===void 0)throw Error(s(407));r=r()}else{if(r=i(),Qe===null)throw Error(s(349));(be&127)!==0||Hg(o,i,r)}u.memoizedState=r;var h={value:r,getSnapshot:i};return u.queue=h,nv(Vg.bind(null,o,h,e),[e]),o.flags|=2048,Vr(9,{destroy:void 0},Gg.bind(null,o,h,r,i),null),r},useId:function(){var e=kn(),i=Qe.identifierPrefix;if(Ce){var r=Wi,o=qi;r=(o&~(1<<32-ne(o)-1)).toString(32)+r,i="_"+i+"R_"+r,r=Bc++,0<r&&(i+="H"+r.toString(32)),i+="_"}else r=fM++,i="_"+i+"r_"+r.toString(32)+"_";return e.memoizedState=i},useHostTransitionStatus:Md,useFormState:Kg,useActionState:Kg,useOptimistic:function(e){var i=kn();i.memoizedState=i.baseState=e;var r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return i.queue=r,i=Ed.bind(null,ue,!0,r),r.dispatch=i,[e,i]},useMemoCache:hd,useCacheRefresh:function(){return kn().memoizedState=vM.bind(null,ue)},useEffectEvent:function(e){var i=kn(),r={impl:e};return i.memoizedState=r,function(){if((Pe&2)!==0)throw Error(s(440));return r.impl.apply(void 0,arguments)}}},bd={readContext:Nn,use:Hc,useCallback:lv,useContext:Nn,useEffect:_d,useImperativeHandle:ov,useInsertionEffect:av,useLayoutEffect:sv,useMemo:cv,useReducer:Gc,useRef:ev,useState:function(){return Gc(fa)},useDebugValue:yd,useDeferredValue:function(e,i){var r=fn();return uv(r,ke.memoizedState,e,i)},useTransition:function(){var e=Gc(fa)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:vl(e),i]},useSyncExternalStore:Fg,useId:pv,useHostTransitionStatus:Md,useFormState:Jg,useActionState:Jg,useOptimistic:function(e,i){var r=fn();return Xg(r,ke,e,i)},useMemoCache:hd,useCacheRefresh:mv};bd.useEffectEvent=iv;var xv={readContext:Nn,use:Hc,useCallback:lv,useContext:Nn,useEffect:_d,useImperativeHandle:ov,useInsertionEffect:av,useLayoutEffect:sv,useMemo:cv,useReducer:md,useRef:ev,useState:function(){return md(fa)},useDebugValue:yd,useDeferredValue:function(e,i){var r=fn();return ke===null?xd(r,e,i):uv(r,ke.memoizedState,e,i)},useTransition:function(){var e=md(fa)[0],i=fn().memoizedState;return[typeof e=="boolean"?e:vl(e),i]},useSyncExternalStore:Fg,useId:pv,useHostTransitionStatus:Md,useFormState:tv,useActionState:tv,useOptimistic:function(e,i){var r=fn();return ke!==null?Xg(r,ke,e,i):(r.baseState=e,[e,r.queue.dispatch])},useMemoCache:hd,useCacheRefresh:mv};xv.useEffectEvent=iv;function Td(e,i,r,o){i=e.memoizedState,r=r(o,i),r=r==null?i:_({},i,r),e.memoizedState=r,e.lanes===0&&(e.updateQueue.baseState=r)}var Ad={enqueueSetState:function(e,i,r){e=e._reactInternals;var o=di(),u=Xa(o);u.payload=i,r!=null&&(u.callback=r),i=qa(e,u,o),i!==null&&(ti(i,e,o),hl(i,e,o))},enqueueReplaceState:function(e,i,r){e=e._reactInternals;var o=di(),u=Xa(o);u.tag=1,u.payload=i,r!=null&&(u.callback=r),i=qa(e,u,o),i!==null&&(ti(i,e,o),hl(i,e,o))},enqueueForceUpdate:function(e,i){e=e._reactInternals;var r=di(),o=Xa(r);o.tag=2,i!=null&&(o.callback=i),i=qa(e,o,r),i!==null&&(ti(i,e,r),hl(i,e,r))}};function Sv(e,i,r,o,u,h,M){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(o,h,M):i.prototype&&i.prototype.isPureReactComponent?!sl(r,o)||!sl(u,h):!0}function Mv(e,i,r,o){e=i.state,typeof i.componentWillReceiveProps=="function"&&i.componentWillReceiveProps(r,o),typeof i.UNSAFE_componentWillReceiveProps=="function"&&i.UNSAFE_componentWillReceiveProps(r,o),i.state!==e&&Ad.enqueueReplaceState(i,i.state,null)}function qs(e,i){var r=i;if("ref"in i){r={};for(var o in i)o!=="ref"&&(r[o]=i[o])}if(e=e.defaultProps){r===i&&(r=_({},r));for(var u in e)r[u]===void 0&&(r[u]=e[u])}return r}function Ev(e){Mc(e)}function bv(e){console.error(e)}function Tv(e){Mc(e)}function Xc(e,i){try{var r=e.onUncaughtError;r(i.value,{componentStack:i.stack})}catch(o){setTimeout(function(){throw o})}}function Av(e,i,r){try{var o=e.onCaughtError;o(r.value,{componentStack:r.stack,errorBoundary:i.tag===1?i.stateNode:null})}catch(u){setTimeout(function(){throw u})}}function Cd(e,i,r){return r=Xa(r),r.tag=3,r.payload={element:null},r.callback=function(){Xc(e,i)},r}function Cv(e){return e=Xa(e),e.tag=3,e}function Rv(e,i,r,o){var u=r.type.getDerivedStateFromError;if(typeof u=="function"){var h=o.value;e.payload=function(){return u(h)},e.callback=function(){Av(i,r,o)}}var M=r.stateNode;M!==null&&typeof M.componentDidCatch=="function"&&(e.callback=function(){Av(i,r,o),typeof u!="function"&&(Ja===null?Ja=new Set([this]):Ja.add(this));var A=o.stack;this.componentDidCatch(o.value,{componentStack:A!==null?A:""})})}function yM(e,i,r,o,u){if(r.flags|=32768,o!==null&&typeof o=="object"&&typeof o.then=="function"){if(i=r.alternate,i!==null&&Or(i,r,u,!0),r=li.current,r!==null){switch(r.tag){case 31:case 13:return bi===null?iu():r.alternate===null&&on===0&&(on=3),r.flags&=-257,r.flags|=65536,r.lanes=u,o===Uc?r.flags|=16384:(i=r.updateQueue,i===null?r.updateQueue=new Set([o]):i.add(o),Jd(e,o,u)),!1;case 22:return r.flags|=65536,o===Uc?r.flags|=16384:(i=r.updateQueue,i===null?(i={transitions:null,markerInstances:null,retryQueue:new Set([o])},r.updateQueue=i):(r=i.retryQueue,r===null?i.retryQueue=new Set([o]):r.add(o)),Jd(e,o,u)),!1}throw Error(s(435,r.tag))}return Jd(e,o,u),iu(),!1}if(Ce)return i=li.current,i!==null?((i.flags&65536)===0&&(i.flags|=256),i.flags|=65536,i.lanes=u,o!==qf&&(e=Error(s(422),{cause:o}),ll(xi(e,r)))):(o!==qf&&(i=Error(s(423),{cause:o}),ll(xi(i,r))),e=e.current.alternate,e.flags|=65536,u&=-u,e.lanes|=u,o=xi(o,r),u=Cd(e.stateNode,o,u),id(e,u),on!==4&&(on=2)),!1;var h=Error(s(520),{cause:o});if(h=xi(h,r),Cl===null?Cl=[h]:Cl.push(h),on!==4&&(on=2),i===null)return!0;o=xi(o,r),r=i;do{switch(r.tag){case 3:return r.flags|=65536,e=u&-u,r.lanes|=e,e=Cd(r.stateNode,o,e),id(r,e),!1;case 1:if(i=r.type,h=r.stateNode,(r.flags&128)===0&&(typeof i.getDerivedStateFromError=="function"||h!==null&&typeof h.componentDidCatch=="function"&&(Ja===null||!Ja.has(h))))return r.flags|=65536,u&=-u,r.lanes|=u,u=Cv(u),Rv(u,e,r,o),id(r,u),!1}r=r.return}while(r!==null);return!1}var Rd=Error(s(461)),mn=!1;function Un(e,i,r,o){i.child=e===null?Ug(i,null,r,o):js(i,e.child,r,o)}function wv(e,i,r,o,u){r=r.render;var h=i.ref;if("ref"in o){var M={};for(var A in o)A!=="ref"&&(M[A]=o[A])}else M=o;return Hs(i),o=cd(e,i,r,M,h,u),A=ud(),e!==null&&!mn?(fd(e,i,u),da(e,i,u)):(Ce&&A&&jf(i),i.flags|=1,Un(e,i,o,u),i.child)}function Dv(e,i,r,o,u){if(e===null){var h=r.type;return typeof h=="function"&&!Gf(h)&&h.defaultProps===void 0&&r.compare===null?(i.tag=15,i.type=h,Nv(e,i,h,o,u)):(e=Ac(r.type,null,o,i,i.mode,u),e.ref=i.ref,e.return=i,i.child=e)}if(h=e.child,!zd(e,u)){var M=h.memoizedProps;if(r=r.compare,r=r!==null?r:sl,r(M,o)&&e.ref===i.ref)return da(e,i,u)}return i.flags|=1,e=ra(h,o),e.ref=i.ref,e.return=i,i.child=e}function Nv(e,i,r,o,u){if(e!==null){var h=e.memoizedProps;if(sl(h,o)&&e.ref===i.ref)if(mn=!1,i.pendingProps=o=h,zd(e,u))(e.flags&131072)!==0&&(mn=!0);else return i.lanes=e.lanes,da(e,i,u)}return wd(e,i,r,o,u)}function Uv(e,i,r,o){var u=o.children,h=e!==null?e.memoizedState:null;if(e===null&&i.stateNode===null&&(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),o.mode==="hidden"){if((i.flags&128)!==0){if(h=h!==null?h.baseLanes|r:r,e!==null){for(o=i.child=e.child,u=0;o!==null;)u=u|o.lanes|o.childLanes,o=o.sibling;o=u&~h}else o=0,i.child=null;return Lv(e,i,h,r,o)}if((r&536870912)!==0)i.memoizedState={baseLanes:0,cachePool:null},e!==null&&Dc(i,h!==null?h.cachePool:null),h!==null?Pg(i,h):sd(),zg(i);else return o=i.lanes=536870912,Lv(e,i,h!==null?h.baseLanes|r:r,r,o)}else h!==null?(Dc(i,h.cachePool),Pg(i,h),Ya(),i.memoizedState=null):(e!==null&&Dc(i,null),sd(),Ya());return Un(e,i,u,r),i.child}function xl(e,i){return e!==null&&e.tag===22||i.stateNode!==null||(i.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),i.sibling}function Lv(e,i,r,o,u){var h=$f();return h=h===null?null:{parent:hn._currentValue,pool:h},i.memoizedState={baseLanes:r,cachePool:h},e!==null&&Dc(i,null),sd(),zg(i),e!==null&&Or(e,i,o,!0),i.childLanes=u,null}function qc(e,i){return i=Yc({mode:i.mode,children:i.children},e.mode),i.ref=e.ref,e.child=i,i.return=e,i}function Ov(e,i,r){return js(i,e.child,null,r),e=qc(i,i.pendingProps),e.flags|=2,ci(i),i.memoizedState=null,e}function xM(e,i,r){var o=i.pendingProps,u=(i.flags&128)!==0;if(i.flags&=-129,e===null){if(Ce){if(o.mode==="hidden")return e=qc(i,o),i.lanes=536870912,xl(null,e);if(od(i),(e=Ke)?(e=q_(e,Ei),e=e!==null&&e.data==="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Ha!==null?{id:qi,overflow:Wi}:null,retryLane:536870912,hydrationErrors:null},r=vg(e),r.return=i,i.child=r,Dn=i,Ke=null)):e=null,e===null)throw Va(i);return i.lanes=536870912,null}return qc(i,o)}var h=e.memoizedState;if(h!==null){var M=h.dehydrated;if(od(i),u)if(i.flags&256)i.flags&=-257,i=Ov(e,i,r);else if(i.memoizedState!==null)i.child=e.child,i.flags|=128,i=null;else throw Error(s(558));else if(mn||Or(e,i,r,!1),u=(r&e.childLanes)!==0,mn||u){if(o=Qe,o!==null&&(M=ji(o,r),M!==0&&M!==h.retryLane))throw h.retryLane=M,zs(e,M),ti(o,e,M),Rd;iu(),i=Ov(e,i,r)}else e=h.treeContext,Ke=Ti(M.nextSibling),Dn=i,Ce=!0,Ga=null,Ei=!1,e!==null&&xg(i,e),i=qc(i,o),i.flags|=4096;return i}return e=ra(e.child,{mode:o.mode,children:o.children}),e.ref=i.ref,i.child=e,e.return=i,e}function Wc(e,i){var r=i.ref;if(r===null)e!==null&&e.ref!==null&&(i.flags|=4194816);else{if(typeof r!="function"&&typeof r!="object")throw Error(s(284));(e===null||e.ref!==r)&&(i.flags|=4194816)}}function wd(e,i,r,o,u){return Hs(i),r=cd(e,i,r,o,void 0,u),o=ud(),e!==null&&!mn?(fd(e,i,u),da(e,i,u)):(Ce&&o&&jf(i),i.flags|=1,Un(e,i,r,u),i.child)}function Pv(e,i,r,o,u,h){return Hs(i),i.updateQueue=null,r=Bg(i,o,r,u),Ig(e),o=ud(),e!==null&&!mn?(fd(e,i,h),da(e,i,h)):(Ce&&o&&jf(i),i.flags|=1,Un(e,i,r,h),i.child)}function zv(e,i,r,o,u){if(Hs(i),i.stateNode===null){var h=Dr,M=r.contextType;typeof M=="object"&&M!==null&&(h=Nn(M)),h=new r(o,h),i.memoizedState=h.state!==null&&h.state!==void 0?h.state:null,h.updater=Ad,i.stateNode=h,h._reactInternals=i,h=i.stateNode,h.props=o,h.state=i.memoizedState,h.refs={},ed(i),M=r.contextType,h.context=typeof M=="object"&&M!==null?Nn(M):Dr,h.state=i.memoizedState,M=r.getDerivedStateFromProps,typeof M=="function"&&(Td(i,r,M,o),h.state=i.memoizedState),typeof r.getDerivedStateFromProps=="function"||typeof h.getSnapshotBeforeUpdate=="function"||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(M=h.state,typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount(),M!==h.state&&Ad.enqueueReplaceState(h,h.state,null),ml(i,o,h,u),pl(),h.state=i.memoizedState),typeof h.componentDidMount=="function"&&(i.flags|=4194308),o=!0}else if(e===null){h=i.stateNode;var A=i.memoizedProps,B=qs(r,A);h.props=B;var et=h.context,ht=r.contextType;M=Dr,typeof ht=="object"&&ht!==null&&(M=Nn(ht));var _t=r.getDerivedStateFromProps;ht=typeof _t=="function"||typeof h.getSnapshotBeforeUpdate=="function",A=i.pendingProps!==A,ht||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(A||et!==M)&&Mv(i,h,o,M),ja=!1;var it=i.memoizedState;h.state=it,ml(i,o,h,u),pl(),et=i.memoizedState,A||it!==et||ja?(typeof _t=="function"&&(Td(i,r,_t,o),et=i.memoizedState),(B=ja||Sv(i,r,B,o,it,et,M))?(ht||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount()),typeof h.componentDidMount=="function"&&(i.flags|=4194308)):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),i.memoizedProps=o,i.memoizedState=et),h.props=o,h.state=et,h.context=M,o=B):(typeof h.componentDidMount=="function"&&(i.flags|=4194308),o=!1)}else{h=i.stateNode,nd(e,i),M=i.memoizedProps,ht=qs(r,M),h.props=ht,_t=i.pendingProps,it=h.context,et=r.contextType,B=Dr,typeof et=="object"&&et!==null&&(B=Nn(et)),A=r.getDerivedStateFromProps,(et=typeof A=="function"||typeof h.getSnapshotBeforeUpdate=="function")||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(M!==_t||it!==B)&&Mv(i,h,o,B),ja=!1,it=i.memoizedState,h.state=it,ml(i,o,h,u),pl();var lt=i.memoizedState;M!==_t||it!==lt||ja||e!==null&&e.dependencies!==null&&Rc(e.dependencies)?(typeof A=="function"&&(Td(i,r,A,o),lt=i.memoizedState),(ht=ja||Sv(i,r,ht,o,it,lt,B)||e!==null&&e.dependencies!==null&&Rc(e.dependencies))?(et||typeof h.UNSAFE_componentWillUpdate!="function"&&typeof h.componentWillUpdate!="function"||(typeof h.componentWillUpdate=="function"&&h.componentWillUpdate(o,lt,B),typeof h.UNSAFE_componentWillUpdate=="function"&&h.UNSAFE_componentWillUpdate(o,lt,B)),typeof h.componentDidUpdate=="function"&&(i.flags|=4),typeof h.getSnapshotBeforeUpdate=="function"&&(i.flags|=1024)):(typeof h.componentDidUpdate!="function"||M===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||M===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),i.memoizedProps=o,i.memoizedState=lt),h.props=o,h.state=lt,h.context=B,o=ht):(typeof h.componentDidUpdate!="function"||M===e.memoizedProps&&it===e.memoizedState||(i.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||M===e.memoizedProps&&it===e.memoizedState||(i.flags|=1024),o=!1)}return h=o,Wc(e,i),o=(i.flags&128)!==0,h||o?(h=i.stateNode,r=o&&typeof r.getDerivedStateFromError!="function"?null:h.render(),i.flags|=1,e!==null&&o?(i.child=js(i,e.child,null,u),i.child=js(i,null,r,u)):Un(e,i,r,u),i.memoizedState=h.state,e=i.child):e=da(e,i,u),e}function Iv(e,i,r,o){return Bs(),i.flags|=256,Un(e,i,r,o),i.child}var Dd={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function Nd(e){return{baseLanes:e,cachePool:Ag()}}function Ud(e,i,r){return e=e!==null?e.childLanes&~r:0,i&&(e|=fi),e}function Bv(e,i,r){var o=i.pendingProps,u=!1,h=(i.flags&128)!==0,M;if((M=h)||(M=e!==null&&e.memoizedState===null?!1:(un.current&2)!==0),M&&(u=!0,i.flags&=-129),M=(i.flags&32)!==0,i.flags&=-33,e===null){if(Ce){if(u?Wa(i):Ya(),(e=Ke)?(e=q_(e,Ei),e=e!==null&&e.data!=="&"?e:null,e!==null&&(i.memoizedState={dehydrated:e,treeContext:Ha!==null?{id:qi,overflow:Wi}:null,retryLane:536870912,hydrationErrors:null},r=vg(e),r.return=i,i.child=r,Dn=i,Ke=null)):e=null,e===null)throw Va(i);return ph(e)?i.lanes=32:i.lanes=536870912,null}var A=o.children;return o=o.fallback,u?(Ya(),u=i.mode,A=Yc({mode:"hidden",children:A},u),o=Is(o,u,r,null),A.return=i,o.return=i,A.sibling=o,i.child=A,o=i.child,o.memoizedState=Nd(r),o.childLanes=Ud(e,M,r),i.memoizedState=Dd,xl(null,o)):(Wa(i),Ld(i,A))}var B=e.memoizedState;if(B!==null&&(A=B.dehydrated,A!==null)){if(h)i.flags&256?(Wa(i),i.flags&=-257,i=Od(e,i,r)):i.memoizedState!==null?(Ya(),i.child=e.child,i.flags|=128,i=null):(Ya(),A=o.fallback,u=i.mode,o=Yc({mode:"visible",children:o.children},u),A=Is(A,u,r,null),A.flags|=2,o.return=i,A.return=i,o.sibling=A,i.child=o,js(i,e.child,null,r),o=i.child,o.memoizedState=Nd(r),o.childLanes=Ud(e,M,r),i.memoizedState=Dd,i=xl(null,o));else if(Wa(i),ph(A)){if(M=A.nextSibling&&A.nextSibling.dataset,M)var et=M.dgst;M=et,o=Error(s(419)),o.stack="",o.digest=M,ll({value:o,source:null,stack:null}),i=Od(e,i,r)}else if(mn||Or(e,i,r,!1),M=(r&e.childLanes)!==0,mn||M){if(M=Qe,M!==null&&(o=ji(M,r),o!==0&&o!==B.retryLane))throw B.retryLane=o,zs(e,o),ti(M,e,o),Rd;hh(A)||iu(),i=Od(e,i,r)}else hh(A)?(i.flags|=192,i.child=e.child,i=null):(e=B.treeContext,Ke=Ti(A.nextSibling),Dn=i,Ce=!0,Ga=null,Ei=!1,e!==null&&xg(i,e),i=Ld(i,o.children),i.flags|=4096);return i}return u?(Ya(),A=o.fallback,u=i.mode,B=e.child,et=B.sibling,o=ra(B,{mode:"hidden",children:o.children}),o.subtreeFlags=B.subtreeFlags&65011712,et!==null?A=ra(et,A):(A=Is(A,u,r,null),A.flags|=2),A.return=i,o.return=i,o.sibling=A,i.child=o,xl(null,o),o=i.child,A=e.child.memoizedState,A===null?A=Nd(r):(u=A.cachePool,u!==null?(B=hn._currentValue,u=u.parent!==B?{parent:B,pool:B}:u):u=Ag(),A={baseLanes:A.baseLanes|r,cachePool:u}),o.memoizedState=A,o.childLanes=Ud(e,M,r),i.memoizedState=Dd,xl(e.child,o)):(Wa(i),r=e.child,e=r.sibling,r=ra(r,{mode:"visible",children:o.children}),r.return=i,r.sibling=null,e!==null&&(M=i.deletions,M===null?(i.deletions=[e],i.flags|=16):M.push(e)),i.child=r,i.memoizedState=null,r)}function Ld(e,i){return i=Yc({mode:"visible",children:i},e.mode),i.return=e,e.child=i}function Yc(e,i){return e=oi(22,e,null,i),e.lanes=0,e}function Od(e,i,r){return js(i,e.child,null,r),e=Ld(i,i.pendingProps.children),e.flags|=2,i.memoizedState=null,e}function Fv(e,i,r){e.lanes|=i;var o=e.alternate;o!==null&&(o.lanes|=i),Qf(e.return,i,r)}function Pd(e,i,r,o,u,h){var M=e.memoizedState;M===null?e.memoizedState={isBackwards:i,rendering:null,renderingStartTime:0,last:o,tail:r,tailMode:u,treeForkCount:h}:(M.isBackwards=i,M.rendering=null,M.renderingStartTime=0,M.last=o,M.tail=r,M.tailMode=u,M.treeForkCount=h)}function Hv(e,i,r){var o=i.pendingProps,u=o.revealOrder,h=o.tail;o=o.children;var M=un.current,A=(M&2)!==0;if(A?(M=M&1|2,i.flags|=128):M&=1,St(un,M),Un(e,i,o,r),o=Ce?ol:0,!A&&e!==null&&(e.flags&128)!==0)t:for(e=i.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Fv(e,r,i);else if(e.tag===19)Fv(e,r,i);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===i)break t;for(;e.sibling===null;){if(e.return===null||e.return===i)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(u){case"forwards":for(r=i.child,u=null;r!==null;)e=r.alternate,e!==null&&zc(e)===null&&(u=r),r=r.sibling;r=u,r===null?(u=i.child,i.child=null):(u=r.sibling,r.sibling=null),Pd(i,!1,u,r,h,o);break;case"backwards":case"unstable_legacy-backwards":for(r=null,u=i.child,i.child=null;u!==null;){if(e=u.alternate,e!==null&&zc(e)===null){i.child=u;break}e=u.sibling,u.sibling=r,r=u,u=e}Pd(i,!0,r,null,h,o);break;case"together":Pd(i,!1,null,null,void 0,o);break;default:i.memoizedState=null}return i.child}function da(e,i,r){if(e!==null&&(i.dependencies=e.dependencies),Ka|=i.lanes,(r&i.childLanes)===0)if(e!==null){if(Or(e,i,r,!1),(r&i.childLanes)===0)return null}else return null;if(e!==null&&i.child!==e.child)throw Error(s(153));if(i.child!==null){for(e=i.child,r=ra(e,e.pendingProps),i.child=r,r.return=i;e.sibling!==null;)e=e.sibling,r=r.sibling=ra(e,e.pendingProps),r.return=i;r.sibling=null}return i.child}function zd(e,i){return(e.lanes&i)!==0?!0:(e=e.dependencies,!!(e!==null&&Rc(e)))}function SM(e,i,r){switch(i.tag){case 3:Ft(i,i.stateNode.containerInfo),ka(i,hn,e.memoizedState.cache),Bs();break;case 27:case 5:oe(i);break;case 4:Ft(i,i.stateNode.containerInfo);break;case 10:ka(i,i.type,i.memoizedProps.value);break;case 31:if(i.memoizedState!==null)return i.flags|=128,od(i),null;break;case 13:var o=i.memoizedState;if(o!==null)return o.dehydrated!==null?(Wa(i),i.flags|=128,null):(r&i.child.childLanes)!==0?Bv(e,i,r):(Wa(i),e=da(e,i,r),e!==null?e.sibling:null);Wa(i);break;case 19:var u=(e.flags&128)!==0;if(o=(r&i.childLanes)!==0,o||(Or(e,i,r,!1),o=(r&i.childLanes)!==0),u){if(o)return Hv(e,i,r);i.flags|=128}if(u=i.memoizedState,u!==null&&(u.rendering=null,u.tail=null,u.lastEffect=null),St(un,un.current),o)break;return null;case 22:return i.lanes=0,Uv(e,i,r,i.pendingProps);case 24:ka(i,hn,e.memoizedState.cache)}return da(e,i,r)}function Gv(e,i,r){if(e!==null)if(e.memoizedProps!==i.pendingProps)mn=!0;else{if(!zd(e,r)&&(i.flags&128)===0)return mn=!1,SM(e,i,r);mn=(e.flags&131072)!==0}else mn=!1,Ce&&(i.flags&1048576)!==0&&yg(i,ol,i.index);switch(i.lanes=0,i.tag){case 16:t:{var o=i.pendingProps;if(e=Vs(i.elementType),i.type=e,typeof e=="function")Gf(e)?(o=qs(e,o),i.tag=1,i=zv(null,i,e,o,r)):(i.tag=0,i=wd(null,i,e,o,r));else{if(e!=null){var u=e.$$typeof;if(u===R){i.tag=11,i=wv(null,i,e,o,r);break t}else if(u===z){i.tag=14,i=Dv(null,i,e,o,r);break t}}throw i=mt(e)||e,Error(s(306,i,""))}}return i;case 0:return wd(e,i,i.type,i.pendingProps,r);case 1:return o=i.type,u=qs(o,i.pendingProps),zv(e,i,o,u,r);case 3:t:{if(Ft(i,i.stateNode.containerInfo),e===null)throw Error(s(387));o=i.pendingProps;var h=i.memoizedState;u=h.element,nd(e,i),ml(i,o,null,r);var M=i.memoizedState;if(o=M.cache,ka(i,hn,o),o!==h.cache&&Zf(i,[hn],r,!0),pl(),o=M.element,h.isDehydrated)if(h={element:o,isDehydrated:!1,cache:M.cache},i.updateQueue.baseState=h,i.memoizedState=h,i.flags&256){i=Iv(e,i,o,r);break t}else if(o!==u){u=xi(Error(s(424)),i),ll(u),i=Iv(e,i,o,r);break t}else{switch(e=i.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName==="HTML"?e.ownerDocument.body:e}for(Ke=Ti(e.firstChild),Dn=i,Ce=!0,Ga=null,Ei=!0,r=Ug(i,null,o,r),i.child=r;r;)r.flags=r.flags&-3|4096,r=r.sibling}else{if(Bs(),o===u){i=da(e,i,r);break t}Un(e,i,o,r)}i=i.child}return i;case 26:return Wc(e,i),e===null?(r=J_(i.type,null,i.pendingProps,null))?i.memoizedState=r:Ce||(r=i.type,e=i.pendingProps,o=uu(Tt.current).createElement(r),o[sn]=i,o[wn]=e,Ln(o,r,e),xt(o),i.stateNode=o):i.memoizedState=J_(i.type,e.memoizedProps,i.pendingProps,e.memoizedState),null;case 27:return oe(i),e===null&&Ce&&(o=i.stateNode=Q_(i.type,i.pendingProps,Tt.current),Dn=i,Ei=!0,u=Ke,ns(i.type)?(mh=u,Ke=Ti(o.firstChild)):Ke=u),Un(e,i,i.pendingProps.children,r),Wc(e,i),e===null&&(i.flags|=4194304),i.child;case 5:return e===null&&Ce&&((u=o=Ke)&&(o=KM(o,i.type,i.pendingProps,Ei),o!==null?(i.stateNode=o,Dn=i,Ke=Ti(o.firstChild),Ei=!1,u=!0):u=!1),u||Va(i)),oe(i),u=i.type,h=i.pendingProps,M=e!==null?e.memoizedProps:null,o=h.children,uh(u,h)?o=null:M!==null&&uh(u,M)&&(i.flags|=32),i.memoizedState!==null&&(u=cd(e,i,dM,null,null,r),Pl._currentValue=u),Wc(e,i),Un(e,i,o,r),i.child;case 6:return e===null&&Ce&&((e=r=Ke)&&(r=JM(r,i.pendingProps,Ei),r!==null?(i.stateNode=r,Dn=i,Ke=null,e=!0):e=!1),e||Va(i)),null;case 13:return Bv(e,i,r);case 4:return Ft(i,i.stateNode.containerInfo),o=i.pendingProps,e===null?i.child=js(i,null,o,r):Un(e,i,o,r),i.child;case 11:return wv(e,i,i.type,i.pendingProps,r);case 7:return Un(e,i,i.pendingProps,r),i.child;case 8:return Un(e,i,i.pendingProps.children,r),i.child;case 12:return Un(e,i,i.pendingProps.children,r),i.child;case 10:return o=i.pendingProps,ka(i,i.type,o.value),Un(e,i,o.children,r),i.child;case 9:return u=i.type._context,o=i.pendingProps.children,Hs(i),u=Nn(u),o=o(u),i.flags|=1,Un(e,i,o,r),i.child;case 14:return Dv(e,i,i.type,i.pendingProps,r);case 15:return Nv(e,i,i.type,i.pendingProps,r);case 19:return Hv(e,i,r);case 31:return xM(e,i,r);case 22:return Uv(e,i,r,i.pendingProps);case 24:return Hs(i),o=Nn(hn),e===null?(u=$f(),u===null&&(u=Qe,h=Kf(),u.pooledCache=h,h.refCount++,h!==null&&(u.pooledCacheLanes|=r),u=h),i.memoizedState={parent:o,cache:u},ed(i),ka(i,hn,u)):((e.lanes&r)!==0&&(nd(e,i),ml(i,null,null,r),pl()),u=e.memoizedState,h=i.memoizedState,u.parent!==o?(u={parent:o,cache:o},i.memoizedState=u,i.lanes===0&&(i.memoizedState=i.updateQueue.baseState=u),ka(i,hn,o)):(o=h.cache,ka(i,hn,o),o!==u.cache&&Zf(i,[hn],r,!0))),Un(e,i,i.pendingProps.children,r),i.child;case 29:throw i.pendingProps}throw Error(s(156,i.tag))}function ha(e){e.flags|=4}function Id(e,i,r,o,u){if((i=(e.mode&32)!==0)&&(i=!1),i){if(e.flags|=16777216,(u&335544128)===u)if(e.stateNode.complete)e.flags|=8192;else if(p_())e.flags|=8192;else throw ks=Uc,td}else e.flags&=-16777217}function Vv(e,i){if(i.type!=="stylesheet"||(i.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!i0(i))if(p_())e.flags|=8192;else throw ks=Uc,td}function Qc(e,i){i!==null&&(e.flags|=4),e.flags&16384&&(i=e.tag!==22?_n():536870912,e.lanes|=i,qr|=i)}function Sl(e,i){if(!Ce)switch(e.tailMode){case"hidden":i=e.tail;for(var r=null;i!==null;)i.alternate!==null&&(r=i),i=i.sibling;r===null?e.tail=null:r.sibling=null;break;case"collapsed":r=e.tail;for(var o=null;r!==null;)r.alternate!==null&&(o=r),r=r.sibling;o===null?i||e.tail===null?e.tail=null:e.tail.sibling=null:o.sibling=null}}function Je(e){var i=e.alternate!==null&&e.alternate.child===e.child,r=0,o=0;if(i)for(var u=e.child;u!==null;)r|=u.lanes|u.childLanes,o|=u.subtreeFlags&65011712,o|=u.flags&65011712,u.return=e,u=u.sibling;else for(u=e.child;u!==null;)r|=u.lanes|u.childLanes,o|=u.subtreeFlags,o|=u.flags,u.return=e,u=u.sibling;return e.subtreeFlags|=o,e.childLanes=r,i}function MM(e,i,r){var o=i.pendingProps;switch(Xf(i),i.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Je(i),null;case 1:return Je(i),null;case 3:return r=i.stateNode,o=null,e!==null&&(o=e.memoizedState.cache),i.memoizedState.cache!==o&&(i.flags|=2048),ca(hn),Vt(),r.pendingContext&&(r.context=r.pendingContext,r.pendingContext=null),(e===null||e.child===null)&&(Lr(i)?ha(i):e===null||e.memoizedState.isDehydrated&&(i.flags&256)===0||(i.flags|=1024,Wf())),Je(i),null;case 26:var u=i.type,h=i.memoizedState;return e===null?(ha(i),h!==null?(Je(i),Vv(i,h)):(Je(i),Id(i,u,null,o,r))):h?h!==e.memoizedState?(ha(i),Je(i),Vv(i,h)):(Je(i),i.flags&=-16777217):(e=e.memoizedProps,e!==o&&ha(i),Je(i),Id(i,u,e,o,r)),null;case 27:if(Ge(i),r=Tt.current,u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(!o){if(i.stateNode===null)throw Error(s(166));return Je(i),null}e=q.current,Lr(i)?Sg(i):(e=Q_(u,o,r),i.stateNode=e,ha(i))}return Je(i),null;case 5:if(Ge(i),u=i.type,e!==null&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(!o){if(i.stateNode===null)throw Error(s(166));return Je(i),null}if(h=q.current,Lr(i))Sg(i);else{var M=uu(Tt.current);switch(h){case 1:h=M.createElementNS("http://www.w3.org/2000/svg",u);break;case 2:h=M.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;default:switch(u){case"svg":h=M.createElementNS("http://www.w3.org/2000/svg",u);break;case"math":h=M.createElementNS("http://www.w3.org/1998/Math/MathML",u);break;case"script":h=M.createElement("div"),h.innerHTML="<script><\/script>",h=h.removeChild(h.firstChild);break;case"select":h=typeof o.is=="string"?M.createElement("select",{is:o.is}):M.createElement("select"),o.multiple?h.multiple=!0:o.size&&(h.size=o.size);break;default:h=typeof o.is=="string"?M.createElement(u,{is:o.is}):M.createElement(u)}}h[sn]=i,h[wn]=o;t:for(M=i.child;M!==null;){if(M.tag===5||M.tag===6)h.appendChild(M.stateNode);else if(M.tag!==4&&M.tag!==27&&M.child!==null){M.child.return=M,M=M.child;continue}if(M===i)break t;for(;M.sibling===null;){if(M.return===null||M.return===i)break t;M=M.return}M.sibling.return=M.return,M=M.sibling}i.stateNode=h;t:switch(Ln(h,u,o),u){case"button":case"input":case"select":case"textarea":o=!!o.autoFocus;break t;case"img":o=!0;break t;default:o=!1}o&&ha(i)}}return Je(i),Id(i,i.type,e===null?null:e.memoizedProps,i.pendingProps,r),null;case 6:if(e&&i.stateNode!=null)e.memoizedProps!==o&&ha(i);else{if(typeof o!="string"&&i.stateNode===null)throw Error(s(166));if(e=Tt.current,Lr(i)){if(e=i.stateNode,r=i.memoizedProps,o=null,u=Dn,u!==null)switch(u.tag){case 27:case 5:o=u.memoizedProps}e[sn]=i,e=!!(e.nodeValue===r||o!==null&&o.suppressHydrationWarning===!0||B_(e.nodeValue,r)),e||Va(i,!0)}else e=uu(e).createTextNode(o),e[sn]=i,i.stateNode=e}return Je(i),null;case 31:if(r=i.memoizedState,e===null||e.memoizedState!==null){if(o=Lr(i),r!==null){if(e===null){if(!o)throw Error(s(318));if(e=i.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(s(557));e[sn]=i}else Bs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Je(i),e=!1}else r=Wf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=r),e=!0;if(!e)return i.flags&256?(ci(i),i):(ci(i),null);if((i.flags&128)!==0)throw Error(s(558))}return Je(i),null;case 13:if(o=i.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(u=Lr(i),o!==null&&o.dehydrated!==null){if(e===null){if(!u)throw Error(s(318));if(u=i.memoizedState,u=u!==null?u.dehydrated:null,!u)throw Error(s(317));u[sn]=i}else Bs(),(i.flags&128)===0&&(i.memoizedState=null),i.flags|=4;Je(i),u=!1}else u=Wf(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=u),u=!0;if(!u)return i.flags&256?(ci(i),i):(ci(i),null)}return ci(i),(i.flags&128)!==0?(i.lanes=r,i):(r=o!==null,e=e!==null&&e.memoizedState!==null,r&&(o=i.child,u=null,o.alternate!==null&&o.alternate.memoizedState!==null&&o.alternate.memoizedState.cachePool!==null&&(u=o.alternate.memoizedState.cachePool.pool),h=null,o.memoizedState!==null&&o.memoizedState.cachePool!==null&&(h=o.memoizedState.cachePool.pool),h!==u&&(o.flags|=2048)),r!==e&&r&&(i.child.flags|=8192),Qc(i,i.updateQueue),Je(i),null);case 4:return Vt(),e===null&&sh(i.stateNode.containerInfo),Je(i),null;case 10:return ca(i.type),Je(i),null;case 19:if(nt(un),o=i.memoizedState,o===null)return Je(i),null;if(u=(i.flags&128)!==0,h=o.rendering,h===null)if(u)Sl(o,!1);else{if(on!==0||e!==null&&(e.flags&128)!==0)for(e=i.child;e!==null;){if(h=zc(e),h!==null){for(i.flags|=128,Sl(o,!1),e=h.updateQueue,i.updateQueue=e,Qc(i,e),i.subtreeFlags=0,e=r,r=i.child;r!==null;)gg(r,e),r=r.sibling;return St(un,un.current&1|2),Ce&&oa(i,o.treeForkCount),i.child}e=e.sibling}o.tail!==null&&pt()>tu&&(i.flags|=128,u=!0,Sl(o,!1),i.lanes=4194304)}else{if(!u)if(e=zc(h),e!==null){if(i.flags|=128,u=!0,e=e.updateQueue,i.updateQueue=e,Qc(i,e),Sl(o,!0),o.tail===null&&o.tailMode==="hidden"&&!h.alternate&&!Ce)return Je(i),null}else 2*pt()-o.renderingStartTime>tu&&r!==536870912&&(i.flags|=128,u=!0,Sl(o,!1),i.lanes=4194304);o.isBackwards?(h.sibling=i.child,i.child=h):(e=o.last,e!==null?e.sibling=h:i.child=h,o.last=h)}return o.tail!==null?(e=o.tail,o.rendering=e,o.tail=e.sibling,o.renderingStartTime=pt(),e.sibling=null,r=un.current,St(un,u?r&1|2:r&1),Ce&&oa(i,o.treeForkCount),e):(Je(i),null);case 22:case 23:return ci(i),rd(),o=i.memoizedState!==null,e!==null?e.memoizedState!==null!==o&&(i.flags|=8192):o&&(i.flags|=8192),o?(r&536870912)!==0&&(i.flags&128)===0&&(Je(i),i.subtreeFlags&6&&(i.flags|=8192)):Je(i),r=i.updateQueue,r!==null&&Qc(i,r.retryQueue),r=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),o=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(o=i.memoizedState.cachePool.pool),o!==r&&(i.flags|=2048),e!==null&&nt(Gs),null;case 24:return r=null,e!==null&&(r=e.memoizedState.cache),i.memoizedState.cache!==r&&(i.flags|=2048),ca(hn),Je(i),null;case 25:return null;case 30:return null}throw Error(s(156,i.tag))}function EM(e,i){switch(Xf(i),i.tag){case 1:return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 3:return ca(hn),Vt(),e=i.flags,(e&65536)!==0&&(e&128)===0?(i.flags=e&-65537|128,i):null;case 26:case 27:case 5:return Ge(i),null;case 31:if(i.memoizedState!==null){if(ci(i),i.alternate===null)throw Error(s(340));Bs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 13:if(ci(i),e=i.memoizedState,e!==null&&e.dehydrated!==null){if(i.alternate===null)throw Error(s(340));Bs()}return e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 19:return nt(un),null;case 4:return Vt(),null;case 10:return ca(i.type),null;case 22:case 23:return ci(i),rd(),e!==null&&nt(Gs),e=i.flags,e&65536?(i.flags=e&-65537|128,i):null;case 24:return ca(hn),null;case 25:return null;default:return null}}function kv(e,i){switch(Xf(i),i.tag){case 3:ca(hn),Vt();break;case 26:case 27:case 5:Ge(i);break;case 4:Vt();break;case 31:i.memoizedState!==null&&ci(i);break;case 13:ci(i);break;case 19:nt(un);break;case 10:ca(i.type);break;case 22:case 23:ci(i),rd(),e!==null&&nt(Gs);break;case 24:ca(hn)}}function Ml(e,i){try{var r=i.updateQueue,o=r!==null?r.lastEffect:null;if(o!==null){var u=o.next;r=u;do{if((r.tag&e)===e){o=void 0;var h=r.create,M=r.inst;o=h(),M.destroy=o}r=r.next}while(r!==u)}}catch(A){He(i,i.return,A)}}function Qa(e,i,r){try{var o=i.updateQueue,u=o!==null?o.lastEffect:null;if(u!==null){var h=u.next;o=h;do{if((o.tag&e)===e){var M=o.inst,A=M.destroy;if(A!==void 0){M.destroy=void 0,u=i;var B=r,et=A;try{et()}catch(ht){He(u,B,ht)}}}o=o.next}while(o!==h)}}catch(ht){He(i,i.return,ht)}}function jv(e){var i=e.updateQueue;if(i!==null){var r=e.stateNode;try{Og(i,r)}catch(o){He(e,e.return,o)}}}function Xv(e,i,r){r.props=qs(e.type,e.memoizedProps),r.state=e.memoizedState;try{r.componentWillUnmount()}catch(o){He(e,i,o)}}function El(e,i){try{var r=e.ref;if(r!==null){switch(e.tag){case 26:case 27:case 5:var o=e.stateNode;break;case 30:o=e.stateNode;break;default:o=e.stateNode}typeof r=="function"?e.refCleanup=r(o):r.current=o}}catch(u){He(e,i,u)}}function Yi(e,i){var r=e.ref,o=e.refCleanup;if(r!==null)if(typeof o=="function")try{o()}catch(u){He(e,i,u)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof r=="function")try{r(null)}catch(u){He(e,i,u)}else r.current=null}function qv(e){var i=e.type,r=e.memoizedProps,o=e.stateNode;try{t:switch(i){case"button":case"input":case"select":case"textarea":r.autoFocus&&o.focus();break t;case"img":r.src?o.src=r.src:r.srcSet&&(o.srcset=r.srcSet)}}catch(u){He(e,e.return,u)}}function Bd(e,i,r){try{var o=e.stateNode;XM(o,e.type,r,i),o[wn]=i}catch(u){He(e,e.return,u)}}function Wv(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&ns(e.type)||e.tag===4}function Fd(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||Wv(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&ns(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Hd(e,i,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,i?(r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r).insertBefore(e,i):(i=r.nodeType===9?r.body:r.nodeName==="HTML"?r.ownerDocument.body:r,i.appendChild(e),r=r._reactRootContainer,r!=null||i.onclick!==null||(i.onclick=aa));else if(o!==4&&(o===27&&ns(e.type)&&(r=e.stateNode,i=null),e=e.child,e!==null))for(Hd(e,i,r),e=e.sibling;e!==null;)Hd(e,i,r),e=e.sibling}function Zc(e,i,r){var o=e.tag;if(o===5||o===6)e=e.stateNode,i?r.insertBefore(e,i):r.appendChild(e);else if(o!==4&&(o===27&&ns(e.type)&&(r=e.stateNode),e=e.child,e!==null))for(Zc(e,i,r),e=e.sibling;e!==null;)Zc(e,i,r),e=e.sibling}function Yv(e){var i=e.stateNode,r=e.memoizedProps;try{for(var o=e.type,u=i.attributes;u.length;)i.removeAttributeNode(u[0]);Ln(i,o,r),i[sn]=e,i[wn]=r}catch(h){He(e,e.return,h)}}var pa=!1,gn=!1,Gd=!1,Qv=typeof WeakSet=="function"?WeakSet:Set,bn=null;function bM(e,i){if(e=e.containerInfo,lh=vu,e=og(e),Of(e)){if("selectionStart"in e)var r={start:e.selectionStart,end:e.selectionEnd};else t:{r=(r=e.ownerDocument)&&r.defaultView||window;var o=r.getSelection&&r.getSelection();if(o&&o.rangeCount!==0){r=o.anchorNode;var u=o.anchorOffset,h=o.focusNode;o=o.focusOffset;try{r.nodeType,h.nodeType}catch{r=null;break t}var M=0,A=-1,B=-1,et=0,ht=0,_t=e,it=null;e:for(;;){for(var lt;_t!==r||u!==0&&_t.nodeType!==3||(A=M+u),_t!==h||o!==0&&_t.nodeType!==3||(B=M+o),_t.nodeType===3&&(M+=_t.nodeValue.length),(lt=_t.firstChild)!==null;)it=_t,_t=lt;for(;;){if(_t===e)break e;if(it===r&&++et===u&&(A=M),it===h&&++ht===o&&(B=M),(lt=_t.nextSibling)!==null)break;_t=it,it=_t.parentNode}_t=lt}r=A===-1||B===-1?null:{start:A,end:B}}else r=null}r=r||{start:0,end:0}}else r=null;for(ch={focusedElem:e,selectionRange:r},vu=!1,bn=i;bn!==null;)if(i=bn,e=i.child,(i.subtreeFlags&1028)!==0&&e!==null)e.return=i,bn=e;else for(;bn!==null;){switch(i=bn,h=i.alternate,e=i.flags,i.tag){case 0:if((e&4)!==0&&(e=i.updateQueue,e=e!==null?e.events:null,e!==null))for(r=0;r<e.length;r++)u=e[r],u.ref.impl=u.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&h!==null){e=void 0,r=i,u=h.memoizedProps,h=h.memoizedState,o=r.stateNode;try{var Gt=qs(r.type,u);e=o.getSnapshotBeforeUpdate(Gt,h),o.__reactInternalSnapshotBeforeUpdate=e}catch(ee){He(r,r.return,ee)}}break;case 3:if((e&1024)!==0){if(e=i.stateNode.containerInfo,r=e.nodeType,r===9)dh(e);else if(r===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":dh(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(s(163))}if(e=i.sibling,e!==null){e.return=i.return,bn=e;break}bn=i.return}}function Zv(e,i,r){var o=r.flags;switch(r.tag){case 0:case 11:case 15:ga(e,r),o&4&&Ml(5,r);break;case 1:if(ga(e,r),o&4)if(e=r.stateNode,i===null)try{e.componentDidMount()}catch(M){He(r,r.return,M)}else{var u=qs(r.type,i.memoizedProps);i=i.memoizedState;try{e.componentDidUpdate(u,i,e.__reactInternalSnapshotBeforeUpdate)}catch(M){He(r,r.return,M)}}o&64&&jv(r),o&512&&El(r,r.return);break;case 3:if(ga(e,r),o&64&&(e=r.updateQueue,e!==null)){if(i=null,r.child!==null)switch(r.child.tag){case 27:case 5:i=r.child.stateNode;break;case 1:i=r.child.stateNode}try{Og(e,i)}catch(M){He(r,r.return,M)}}break;case 27:i===null&&o&4&&Yv(r);case 26:case 5:ga(e,r),i===null&&o&4&&qv(r),o&512&&El(r,r.return);break;case 12:ga(e,r);break;case 31:ga(e,r),o&4&&$v(e,r);break;case 13:ga(e,r),o&4&&t_(e,r),o&64&&(e=r.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(r=LM.bind(null,r),$M(e,r))));break;case 22:if(o=r.memoizedState!==null||pa,!o){i=i!==null&&i.memoizedState!==null||gn,u=pa;var h=gn;pa=o,(gn=i)&&!h?va(e,r,(r.subtreeFlags&8772)!==0):ga(e,r),pa=u,gn=h}break;case 30:break;default:ga(e,r)}}function Kv(e){var i=e.alternate;i!==null&&(e.alternate=null,Kv(i)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(i=e.stateNode,i!==null&&w(i)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var en=null,Zn=!1;function ma(e,i,r){for(r=r.child;r!==null;)Jv(e,i,r),r=r.sibling}function Jv(e,i,r){if(qt&&typeof qt.onCommitFiberUnmount=="function")try{qt.onCommitFiberUnmount(Zt,r)}catch{}switch(r.tag){case 26:gn||Yi(r,i),ma(e,i,r),r.memoizedState?r.memoizedState.count--:r.stateNode&&(r=r.stateNode,r.parentNode.removeChild(r));break;case 27:gn||Yi(r,i);var o=en,u=Zn;ns(r.type)&&(en=r.stateNode,Zn=!1),ma(e,i,r),Ul(r.stateNode),en=o,Zn=u;break;case 5:gn||Yi(r,i);case 6:if(o=en,u=Zn,en=null,ma(e,i,r),en=o,Zn=u,en!==null)if(Zn)try{(en.nodeType===9?en.body:en.nodeName==="HTML"?en.ownerDocument.body:en).removeChild(r.stateNode)}catch(h){He(r,i,h)}else try{en.removeChild(r.stateNode)}catch(h){He(r,i,h)}break;case 18:en!==null&&(Zn?(e=en,j_(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,r.stateNode),to(e)):j_(en,r.stateNode));break;case 4:o=en,u=Zn,en=r.stateNode.containerInfo,Zn=!0,ma(e,i,r),en=o,Zn=u;break;case 0:case 11:case 14:case 15:Qa(2,r,i),gn||Qa(4,r,i),ma(e,i,r);break;case 1:gn||(Yi(r,i),o=r.stateNode,typeof o.componentWillUnmount=="function"&&Xv(r,i,o)),ma(e,i,r);break;case 21:ma(e,i,r);break;case 22:gn=(o=gn)||r.memoizedState!==null,ma(e,i,r),gn=o;break;default:ma(e,i,r)}}function $v(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{to(e)}catch(r){He(i,i.return,r)}}}function t_(e,i){if(i.memoizedState===null&&(e=i.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{to(e)}catch(r){He(i,i.return,r)}}function TM(e){switch(e.tag){case 31:case 13:case 19:var i=e.stateNode;return i===null&&(i=e.stateNode=new Qv),i;case 22:return e=e.stateNode,i=e._retryCache,i===null&&(i=e._retryCache=new Qv),i;default:throw Error(s(435,e.tag))}}function Kc(e,i){var r=TM(e);i.forEach(function(o){if(!r.has(o)){r.add(o);var u=OM.bind(null,e,o);o.then(u,u)}})}function Kn(e,i){var r=i.deletions;if(r!==null)for(var o=0;o<r.length;o++){var u=r[o],h=e,M=i,A=M;t:for(;A!==null;){switch(A.tag){case 27:if(ns(A.type)){en=A.stateNode,Zn=!1;break t}break;case 5:en=A.stateNode,Zn=!1;break t;case 3:case 4:en=A.stateNode.containerInfo,Zn=!0;break t}A=A.return}if(en===null)throw Error(s(160));Jv(h,M,u),en=null,Zn=!1,h=u.alternate,h!==null&&(h.return=null),u.return=null}if(i.subtreeFlags&13886)for(i=i.child;i!==null;)e_(i,e),i=i.sibling}var Ui=null;function e_(e,i){var r=e.alternate,o=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Kn(i,e),Jn(e),o&4&&(Qa(3,e,e.return),Ml(3,e),Qa(5,e,e.return));break;case 1:Kn(i,e),Jn(e),o&512&&(gn||r===null||Yi(r,r.return)),o&64&&pa&&(e=e.updateQueue,e!==null&&(o=e.callbacks,o!==null&&(r=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=r===null?o:r.concat(o))));break;case 26:var u=Ui;if(Kn(i,e),Jn(e),o&512&&(gn||r===null||Yi(r,r.return)),o&4){var h=r!==null?r.memoizedState:null;if(o=e.memoizedState,r===null)if(o===null)if(e.stateNode===null){t:{o=e.type,r=e.memoizedProps,u=u.ownerDocument||u;e:switch(o){case"title":h=u.getElementsByTagName("title")[0],(!h||h[Ns]||h[sn]||h.namespaceURI==="http://www.w3.org/2000/svg"||h.hasAttribute("itemprop"))&&(h=u.createElement(o),u.head.insertBefore(h,u.querySelector("head > title"))),Ln(h,o,r),h[sn]=e,xt(h),o=h;break t;case"link":var M=e0("link","href",u).get(o+(r.href||""));if(M){for(var A=0;A<M.length;A++)if(h=M[A],h.getAttribute("href")===(r.href==null||r.href===""?null:r.href)&&h.getAttribute("rel")===(r.rel==null?null:r.rel)&&h.getAttribute("title")===(r.title==null?null:r.title)&&h.getAttribute("crossorigin")===(r.crossOrigin==null?null:r.crossOrigin)){M.splice(A,1);break e}}h=u.createElement(o),Ln(h,o,r),u.head.appendChild(h);break;case"meta":if(M=e0("meta","content",u).get(o+(r.content||""))){for(A=0;A<M.length;A++)if(h=M[A],h.getAttribute("content")===(r.content==null?null:""+r.content)&&h.getAttribute("name")===(r.name==null?null:r.name)&&h.getAttribute("property")===(r.property==null?null:r.property)&&h.getAttribute("http-equiv")===(r.httpEquiv==null?null:r.httpEquiv)&&h.getAttribute("charset")===(r.charSet==null?null:r.charSet)){M.splice(A,1);break e}}h=u.createElement(o),Ln(h,o,r),u.head.appendChild(h);break;default:throw Error(s(468,o))}h[sn]=e,xt(h),o=h}e.stateNode=o}else n0(u,e.type,e.stateNode);else e.stateNode=t0(u,o,e.memoizedProps);else h!==o?(h===null?r.stateNode!==null&&(r=r.stateNode,r.parentNode.removeChild(r)):h.count--,o===null?n0(u,e.type,e.stateNode):t0(u,o,e.memoizedProps)):o===null&&e.stateNode!==null&&Bd(e,e.memoizedProps,r.memoizedProps)}break;case 27:Kn(i,e),Jn(e),o&512&&(gn||r===null||Yi(r,r.return)),r!==null&&o&4&&Bd(e,e.memoizedProps,r.memoizedProps);break;case 5:if(Kn(i,e),Jn(e),o&512&&(gn||r===null||Yi(r,r.return)),e.flags&32){u=e.stateNode;try{Er(u,"")}catch(Gt){He(e,e.return,Gt)}}o&4&&e.stateNode!=null&&(u=e.memoizedProps,Bd(e,u,r!==null?r.memoizedProps:u)),o&1024&&(Gd=!0);break;case 6:if(Kn(i,e),Jn(e),o&4){if(e.stateNode===null)throw Error(s(162));o=e.memoizedProps,r=e.stateNode;try{r.nodeValue=o}catch(Gt){He(e,e.return,Gt)}}break;case 3:if(hu=null,u=Ui,Ui=fu(i.containerInfo),Kn(i,e),Ui=u,Jn(e),o&4&&r!==null&&r.memoizedState.isDehydrated)try{to(i.containerInfo)}catch(Gt){He(e,e.return,Gt)}Gd&&(Gd=!1,n_(e));break;case 4:o=Ui,Ui=fu(e.stateNode.containerInfo),Kn(i,e),Jn(e),Ui=o;break;case 12:Kn(i,e),Jn(e);break;case 31:Kn(i,e),Jn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Kc(e,o)));break;case 13:Kn(i,e),Jn(e),e.child.flags&8192&&e.memoizedState!==null!=(r!==null&&r.memoizedState!==null)&&($c=pt()),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Kc(e,o)));break;case 22:u=e.memoizedState!==null;var B=r!==null&&r.memoizedState!==null,et=pa,ht=gn;if(pa=et||u,gn=ht||B,Kn(i,e),gn=ht,pa=et,Jn(e),o&8192)t:for(i=e.stateNode,i._visibility=u?i._visibility&-2:i._visibility|1,u&&(r===null||B||pa||gn||Ws(e)),r=null,i=e;;){if(i.tag===5||i.tag===26){if(r===null){B=r=i;try{if(h=B.stateNode,u)M=h.style,typeof M.setProperty=="function"?M.setProperty("display","none","important"):M.display="none";else{A=B.stateNode;var _t=B.memoizedProps.style,it=_t!=null&&_t.hasOwnProperty("display")?_t.display:null;A.style.display=it==null||typeof it=="boolean"?"":(""+it).trim()}}catch(Gt){He(B,B.return,Gt)}}}else if(i.tag===6){if(r===null){B=i;try{B.stateNode.nodeValue=u?"":B.memoizedProps}catch(Gt){He(B,B.return,Gt)}}}else if(i.tag===18){if(r===null){B=i;try{var lt=B.stateNode;u?X_(lt,!0):X_(B.stateNode,!1)}catch(Gt){He(B,B.return,Gt)}}}else if((i.tag!==22&&i.tag!==23||i.memoizedState===null||i===e)&&i.child!==null){i.child.return=i,i=i.child;continue}if(i===e)break t;for(;i.sibling===null;){if(i.return===null||i.return===e)break t;r===i&&(r=null),i=i.return}r===i&&(r=null),i.sibling.return=i.return,i=i.sibling}o&4&&(o=e.updateQueue,o!==null&&(r=o.retryQueue,r!==null&&(o.retryQueue=null,Kc(e,r))));break;case 19:Kn(i,e),Jn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,Kc(e,o)));break;case 30:break;case 21:break;default:Kn(i,e),Jn(e)}}function Jn(e){var i=e.flags;if(i&2){try{for(var r,o=e.return;o!==null;){if(Wv(o)){r=o;break}o=o.return}if(r==null)throw Error(s(160));switch(r.tag){case 27:var u=r.stateNode,h=Fd(e);Zc(e,h,u);break;case 5:var M=r.stateNode;r.flags&32&&(Er(M,""),r.flags&=-33);var A=Fd(e);Zc(e,A,M);break;case 3:case 4:var B=r.stateNode.containerInfo,et=Fd(e);Hd(e,et,B);break;default:throw Error(s(161))}}catch(ht){He(e,e.return,ht)}e.flags&=-3}i&4096&&(e.flags&=-4097)}function n_(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var i=e;n_(i),i.tag===5&&i.flags&1024&&i.stateNode.reset(),e=e.sibling}}function ga(e,i){if(i.subtreeFlags&8772)for(i=i.child;i!==null;)Zv(e,i.alternate,i),i=i.sibling}function Ws(e){for(e=e.child;e!==null;){var i=e;switch(i.tag){case 0:case 11:case 14:case 15:Qa(4,i,i.return),Ws(i);break;case 1:Yi(i,i.return);var r=i.stateNode;typeof r.componentWillUnmount=="function"&&Xv(i,i.return,r),Ws(i);break;case 27:Ul(i.stateNode);case 26:case 5:Yi(i,i.return),Ws(i);break;case 22:i.memoizedState===null&&Ws(i);break;case 30:Ws(i);break;default:Ws(i)}e=e.sibling}}function va(e,i,r){for(r=r&&(i.subtreeFlags&8772)!==0,i=i.child;i!==null;){var o=i.alternate,u=e,h=i,M=h.flags;switch(h.tag){case 0:case 11:case 15:va(u,h,r),Ml(4,h);break;case 1:if(va(u,h,r),o=h,u=o.stateNode,typeof u.componentDidMount=="function")try{u.componentDidMount()}catch(et){He(o,o.return,et)}if(o=h,u=o.updateQueue,u!==null){var A=o.stateNode;try{var B=u.shared.hiddenCallbacks;if(B!==null)for(u.shared.hiddenCallbacks=null,u=0;u<B.length;u++)Lg(B[u],A)}catch(et){He(o,o.return,et)}}r&&M&64&&jv(h),El(h,h.return);break;case 27:Yv(h);case 26:case 5:va(u,h,r),r&&o===null&&M&4&&qv(h),El(h,h.return);break;case 12:va(u,h,r);break;case 31:va(u,h,r),r&&M&4&&$v(u,h);break;case 13:va(u,h,r),r&&M&4&&t_(u,h);break;case 22:h.memoizedState===null&&va(u,h,r),El(h,h.return);break;case 30:break;default:va(u,h,r)}i=i.sibling}}function Vd(e,i){var r=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(r=e.memoizedState.cachePool.pool),e=null,i.memoizedState!==null&&i.memoizedState.cachePool!==null&&(e=i.memoizedState.cachePool.pool),e!==r&&(e!=null&&e.refCount++,r!=null&&cl(r))}function kd(e,i){e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&cl(e))}function Li(e,i,r,o){if(i.subtreeFlags&10256)for(i=i.child;i!==null;)i_(e,i,r,o),i=i.sibling}function i_(e,i,r,o){var u=i.flags;switch(i.tag){case 0:case 11:case 15:Li(e,i,r,o),u&2048&&Ml(9,i);break;case 1:Li(e,i,r,o);break;case 3:Li(e,i,r,o),u&2048&&(e=null,i.alternate!==null&&(e=i.alternate.memoizedState.cache),i=i.memoizedState.cache,i!==e&&(i.refCount++,e!=null&&cl(e)));break;case 12:if(u&2048){Li(e,i,r,o),e=i.stateNode;try{var h=i.memoizedProps,M=h.id,A=h.onPostCommit;typeof A=="function"&&A(M,i.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(B){He(i,i.return,B)}}else Li(e,i,r,o);break;case 31:Li(e,i,r,o);break;case 13:Li(e,i,r,o);break;case 23:break;case 22:h=i.stateNode,M=i.alternate,i.memoizedState!==null?h._visibility&2?Li(e,i,r,o):bl(e,i):h._visibility&2?Li(e,i,r,o):(h._visibility|=2,kr(e,i,r,o,(i.subtreeFlags&10256)!==0||!1)),u&2048&&Vd(M,i);break;case 24:Li(e,i,r,o),u&2048&&kd(i.alternate,i);break;default:Li(e,i,r,o)}}function kr(e,i,r,o,u){for(u=u&&((i.subtreeFlags&10256)!==0||!1),i=i.child;i!==null;){var h=e,M=i,A=r,B=o,et=M.flags;switch(M.tag){case 0:case 11:case 15:kr(h,M,A,B,u),Ml(8,M);break;case 23:break;case 22:var ht=M.stateNode;M.memoizedState!==null?ht._visibility&2?kr(h,M,A,B,u):bl(h,M):(ht._visibility|=2,kr(h,M,A,B,u)),u&&et&2048&&Vd(M.alternate,M);break;case 24:kr(h,M,A,B,u),u&&et&2048&&kd(M.alternate,M);break;default:kr(h,M,A,B,u)}i=i.sibling}}function bl(e,i){if(i.subtreeFlags&10256)for(i=i.child;i!==null;){var r=e,o=i,u=o.flags;switch(o.tag){case 22:bl(r,o),u&2048&&Vd(o.alternate,o);break;case 24:bl(r,o),u&2048&&kd(o.alternate,o);break;default:bl(r,o)}i=i.sibling}}var Tl=8192;function jr(e,i,r){if(e.subtreeFlags&Tl)for(e=e.child;e!==null;)a_(e,i,r),e=e.sibling}function a_(e,i,r){switch(e.tag){case 26:jr(e,i,r),e.flags&Tl&&e.memoizedState!==null&&f1(r,Ui,e.memoizedState,e.memoizedProps);break;case 5:jr(e,i,r);break;case 3:case 4:var o=Ui;Ui=fu(e.stateNode.containerInfo),jr(e,i,r),Ui=o;break;case 22:e.memoizedState===null&&(o=e.alternate,o!==null&&o.memoizedState!==null?(o=Tl,Tl=16777216,jr(e,i,r),Tl=o):jr(e,i,r));break;default:jr(e,i,r)}}function s_(e){var i=e.alternate;if(i!==null&&(e=i.child,e!==null)){i.child=null;do i=e.sibling,e.sibling=null,e=i;while(e!==null)}}function Al(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var o=i[r];bn=o,o_(o,e)}s_(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)r_(e),e=e.sibling}function r_(e){switch(e.tag){case 0:case 11:case 15:Al(e),e.flags&2048&&Qa(9,e,e.return);break;case 3:Al(e);break;case 12:Al(e);break;case 22:var i=e.stateNode;e.memoizedState!==null&&i._visibility&2&&(e.return===null||e.return.tag!==13)?(i._visibility&=-3,Jc(e)):Al(e);break;default:Al(e)}}function Jc(e){var i=e.deletions;if((e.flags&16)!==0){if(i!==null)for(var r=0;r<i.length;r++){var o=i[r];bn=o,o_(o,e)}s_(e)}for(e=e.child;e!==null;){switch(i=e,i.tag){case 0:case 11:case 15:Qa(8,i,i.return),Jc(i);break;case 22:r=i.stateNode,r._visibility&2&&(r._visibility&=-3,Jc(i));break;default:Jc(i)}e=e.sibling}}function o_(e,i){for(;bn!==null;){var r=bn;switch(r.tag){case 0:case 11:case 15:Qa(8,r,i);break;case 23:case 22:if(r.memoizedState!==null&&r.memoizedState.cachePool!==null){var o=r.memoizedState.cachePool.pool;o!=null&&o.refCount++}break;case 24:cl(r.memoizedState.cache)}if(o=r.child,o!==null)o.return=r,bn=o;else t:for(r=e;bn!==null;){o=bn;var u=o.sibling,h=o.return;if(Kv(o),o===r){bn=null;break t}if(u!==null){u.return=h,bn=u;break t}bn=h}}}var AM={getCacheForType:function(e){var i=Nn(hn),r=i.data.get(e);return r===void 0&&(r=e(),i.data.set(e,r)),r},cacheSignal:function(){return Nn(hn).controller.signal}},CM=typeof WeakMap=="function"?WeakMap:Map,Pe=0,Qe=null,ye=null,be=0,Fe=0,ui=null,Za=!1,Xr=!1,jd=!1,_a=0,on=0,Ka=0,Ys=0,Xd=0,fi=0,qr=0,Cl=null,$n=null,qd=!1,$c=0,l_=0,tu=1/0,eu=null,Ja=null,xn=0,$a=null,Wr=null,ya=0,Wd=0,Yd=null,c_=null,Rl=0,Qd=null;function di(){return(Pe&2)!==0&&be!==0?be&-be:I.T!==null?eh():Zo()}function u_(){if(fi===0)if((be&536870912)===0||Ce){var e=dt;dt<<=1,(dt&3932160)===0&&(dt=262144),fi=e}else fi=536870912;return e=li.current,e!==null&&(e.flags|=32),fi}function ti(e,i,r){(e===Qe&&(Fe===2||Fe===9)||e.cancelPendingCommit!==null)&&(Yr(e,0),ts(e,be,fi,!1)),Rn(e,r),((Pe&2)===0||e!==Qe)&&(e===Qe&&((Pe&2)===0&&(Ys|=r),on===4&&ts(e,be,fi,!1)),Qi(e))}function f_(e,i,r){if((Pe&6)!==0)throw Error(s(327));var o=!r&&(i&127)===0&&(i&e.expiredLanes)===0||ie(e,i),u=o?DM(e,i):Kd(e,i,!0),h=o;do{if(u===0){Xr&&!o&&ts(e,i,0,!1);break}else{if(r=e.current.alternate,h&&!RM(r)){u=Kd(e,i,!1),h=!1;continue}if(u===2){if(h=i,e.errorRecoveryDisabledLanes&h)var M=0;else M=e.pendingLanes&-536870913,M=M!==0?M:M&536870912?536870912:0;if(M!==0){i=M;t:{var A=e;u=Cl;var B=A.current.memoizedState.isDehydrated;if(B&&(Yr(A,M).flags|=256),M=Kd(A,M,!1),M!==2){if(jd&&!B){A.errorRecoveryDisabledLanes|=h,Ys|=h,u=4;break t}h=$n,$n=u,h!==null&&($n===null?$n=h:$n.push.apply($n,h))}u=M}if(h=!1,u!==2)continue}}if(u===1){Yr(e,0),ts(e,i,0,!0);break}t:{switch(o=e,h=u,h){case 0:case 1:throw Error(s(345));case 4:if((i&4194048)!==i)break;case 6:ts(o,i,fi,!Za);break t;case 2:$n=null;break;case 3:case 5:break;default:throw Error(s(329))}if((i&62914560)===i&&(u=$c+300-pt(),10<u)){if(ts(o,i,fi,!Za),Nt(o,0,!0)!==0)break t;ya=i,o.timeoutHandle=V_(d_.bind(null,o,r,$n,eu,qd,i,fi,Ys,qr,Za,h,"Throttled",-0,0),u);break t}d_(o,r,$n,eu,qd,i,fi,Ys,qr,Za,h,null,-0,0)}}break}while(!0);Qi(e)}function d_(e,i,r,o,u,h,M,A,B,et,ht,_t,it,lt){if(e.timeoutHandle=-1,_t=i.subtreeFlags,_t&8192||(_t&16785408)===16785408){_t={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:aa},a_(i,h,_t);var Gt=(h&62914560)===h?$c-pt():(h&4194048)===h?l_-pt():0;if(Gt=d1(_t,Gt),Gt!==null){ya=h,e.cancelPendingCommit=Gt(x_.bind(null,e,i,h,r,o,u,M,A,B,ht,_t,null,it,lt)),ts(e,h,M,!et);return}}x_(e,i,h,r,o,u,M,A,B)}function RM(e){for(var i=e;;){var r=i.tag;if((r===0||r===11||r===15)&&i.flags&16384&&(r=i.updateQueue,r!==null&&(r=r.stores,r!==null)))for(var o=0;o<r.length;o++){var u=r[o],h=u.getSnapshot;u=u.value;try{if(!ri(h(),u))return!1}catch{return!1}}if(r=i.child,i.subtreeFlags&16384&&r!==null)r.return=i,i=r;else{if(i===e)break;for(;i.sibling===null;){if(i.return===null||i.return===e)return!0;i=i.return}i.sibling.return=i.return,i=i.sibling}}return!0}function ts(e,i,r,o){i&=~Xd,i&=~Ys,e.suspendedLanes|=i,e.pingedLanes&=~i,o&&(e.warmLanes|=i),o=e.expirationTimes;for(var u=i;0<u;){var h=31-ne(u),M=1<<h;o[h]=-1,u&=~M}r!==0&&Yo(e,r,i)}function nu(){return(Pe&6)===0?(wl(0),!1):!0}function Zd(){if(ye!==null){if(Fe===0)var e=ye.return;else e=ye,la=Fs=null,dd(e),Br=null,fl=0,e=ye;for(;e!==null;)kv(e.alternate,e),e=e.return;ye=null}}function Yr(e,i){var r=e.timeoutHandle;r!==-1&&(e.timeoutHandle=-1,YM(r)),r=e.cancelPendingCommit,r!==null&&(e.cancelPendingCommit=null,r()),ya=0,Zd(),Qe=e,ye=r=ra(e.current,null),be=i,Fe=0,ui=null,Za=!1,Xr=ie(e,i),jd=!1,qr=fi=Xd=Ys=Ka=on=0,$n=Cl=null,qd=!1,(i&8)!==0&&(i|=i&32);var o=e.entangledLanes;if(o!==0)for(e=e.entanglements,o&=i;0<o;){var u=31-ne(o),h=1<<u;i|=e[u],o&=~h}return _a=i,Ec(),r}function h_(e,i){ue=null,I.H=yl,i===Ir||i===Nc?(i=wg(),Fe=3):i===td?(i=wg(),Fe=4):Fe=i===Rd?8:i!==null&&typeof i=="object"&&typeof i.then=="function"?6:1,ui=i,ye===null&&(on=1,Xc(e,xi(i,e.current)))}function p_(){var e=li.current;return e===null?!0:(be&4194048)===be?bi===null:(be&62914560)===be||(be&536870912)!==0?e===bi:!1}function m_(){var e=I.H;return I.H=yl,e===null?yl:e}function g_(){var e=I.A;return I.A=AM,e}function iu(){on=4,Za||(be&4194048)!==be&&li.current!==null||(Xr=!0),(Ka&134217727)===0&&(Ys&134217727)===0||Qe===null||ts(Qe,be,fi,!1)}function Kd(e,i,r){var o=Pe;Pe|=2;var u=m_(),h=g_();(Qe!==e||be!==i)&&(eu=null,Yr(e,i)),i=!1;var M=on;t:do try{if(Fe!==0&&ye!==null){var A=ye,B=ui;switch(Fe){case 8:Zd(),M=6;break t;case 3:case 2:case 9:case 6:li.current===null&&(i=!0);var et=Fe;if(Fe=0,ui=null,Qr(e,A,B,et),r&&Xr){M=0;break t}break;default:et=Fe,Fe=0,ui=null,Qr(e,A,B,et)}}wM(),M=on;break}catch(ht){h_(e,ht)}while(!0);return i&&e.shellSuspendCounter++,la=Fs=null,Pe=o,I.H=u,I.A=h,ye===null&&(Qe=null,be=0,Ec()),M}function wM(){for(;ye!==null;)v_(ye)}function DM(e,i){var r=Pe;Pe|=2;var o=m_(),u=g_();Qe!==e||be!==i?(eu=null,tu=pt()+500,Yr(e,i)):Xr=ie(e,i);t:do try{if(Fe!==0&&ye!==null){i=ye;var h=ui;e:switch(Fe){case 1:Fe=0,ui=null,Qr(e,i,h,1);break;case 2:case 9:if(Cg(h)){Fe=0,ui=null,__(i);break}i=function(){Fe!==2&&Fe!==9||Qe!==e||(Fe=7),Qi(e)},h.then(i,i);break t;case 3:Fe=7;break t;case 4:Fe=5;break t;case 7:Cg(h)?(Fe=0,ui=null,__(i)):(Fe=0,ui=null,Qr(e,i,h,7));break;case 5:var M=null;switch(ye.tag){case 26:M=ye.memoizedState;case 5:case 27:var A=ye;if(M?i0(M):A.stateNode.complete){Fe=0,ui=null;var B=A.sibling;if(B!==null)ye=B;else{var et=A.return;et!==null?(ye=et,au(et)):ye=null}break e}}Fe=0,ui=null,Qr(e,i,h,5);break;case 6:Fe=0,ui=null,Qr(e,i,h,6);break;case 8:Zd(),on=6;break t;default:throw Error(s(462))}}NM();break}catch(ht){h_(e,ht)}while(!0);return la=Fs=null,I.H=o,I.A=u,Pe=r,ye!==null?0:(Qe=null,be=0,Ec(),on)}function NM(){for(;ye!==null&&!C();)v_(ye)}function v_(e){var i=Gv(e.alternate,e,_a);e.memoizedProps=e.pendingProps,i===null?au(e):ye=i}function __(e){var i=e,r=i.alternate;switch(i.tag){case 15:case 0:i=Pv(r,i,i.pendingProps,i.type,void 0,be);break;case 11:i=Pv(r,i,i.pendingProps,i.type.render,i.ref,be);break;case 5:dd(i);default:kv(r,i),i=ye=gg(i,_a),i=Gv(r,i,_a)}e.memoizedProps=e.pendingProps,i===null?au(e):ye=i}function Qr(e,i,r,o){la=Fs=null,dd(i),Br=null,fl=0;var u=i.return;try{if(yM(e,u,i,r,be)){on=1,Xc(e,xi(r,e.current)),ye=null;return}}catch(h){if(u!==null)throw ye=u,h;on=1,Xc(e,xi(r,e.current)),ye=null;return}i.flags&32768?(Ce||o===1?e=!0:Xr||(be&536870912)!==0?e=!1:(Za=e=!0,(o===2||o===9||o===3||o===6)&&(o=li.current,o!==null&&o.tag===13&&(o.flags|=16384))),y_(i,e)):au(i)}function au(e){var i=e;do{if((i.flags&32768)!==0){y_(i,Za);return}e=i.return;var r=MM(i.alternate,i,_a);if(r!==null){ye=r;return}if(i=i.sibling,i!==null){ye=i;return}ye=i=e}while(i!==null);on===0&&(on=5)}function y_(e,i){do{var r=EM(e.alternate,e);if(r!==null){r.flags&=32767,ye=r;return}if(r=e.return,r!==null&&(r.flags|=32768,r.subtreeFlags=0,r.deletions=null),!i&&(e=e.sibling,e!==null)){ye=e;return}ye=e=r}while(e!==null);on=6,ye=null}function x_(e,i,r,o,u,h,M,A,B){e.cancelPendingCommit=null;do su();while(xn!==0);if((Pe&6)!==0)throw Error(s(327));if(i!==null){if(i===e.current)throw Error(s(177));if(h=i.lanes|i.childLanes,h|=Ff,wi(e,r,h,M,A,B),e===Qe&&(ye=Qe=null,be=0),Wr=i,$a=e,ya=r,Wd=h,Yd=u,c_=o,(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,PM(Dt,function(){return T_(),null})):(e.callbackNode=null,e.callbackPriority=0),o=(i.flags&13878)!==0,(i.subtreeFlags&13878)!==0||o){o=I.T,I.T=null,u=Z.p,Z.p=2,M=Pe,Pe|=4;try{bM(e,i,r)}finally{Pe=M,Z.p=u,I.T=o}}xn=1,S_(),M_(),E_()}}function S_(){if(xn===1){xn=0;var e=$a,i=Wr,r=(i.flags&13878)!==0;if((i.subtreeFlags&13878)!==0||r){r=I.T,I.T=null;var o=Z.p;Z.p=2;var u=Pe;Pe|=4;try{e_(i,e);var h=ch,M=og(e.containerInfo),A=h.focusedElem,B=h.selectionRange;if(M!==A&&A&&A.ownerDocument&&rg(A.ownerDocument.documentElement,A)){if(B!==null&&Of(A)){var et=B.start,ht=B.end;if(ht===void 0&&(ht=et),"selectionStart"in A)A.selectionStart=et,A.selectionEnd=Math.min(ht,A.value.length);else{var _t=A.ownerDocument||document,it=_t&&_t.defaultView||window;if(it.getSelection){var lt=it.getSelection(),Gt=A.textContent.length,ee=Math.min(B.start,Gt),Xe=B.end===void 0?ee:Math.min(B.end,Gt);!lt.extend&&ee>Xe&&(M=Xe,Xe=ee,ee=M);var J=sg(A,ee),j=sg(A,Xe);if(J&&j&&(lt.rangeCount!==1||lt.anchorNode!==J.node||lt.anchorOffset!==J.offset||lt.focusNode!==j.node||lt.focusOffset!==j.offset)){var tt=_t.createRange();tt.setStart(J.node,J.offset),lt.removeAllRanges(),ee>Xe?(lt.addRange(tt),lt.extend(j.node,j.offset)):(tt.setEnd(j.node,j.offset),lt.addRange(tt))}}}}for(_t=[],lt=A;lt=lt.parentNode;)lt.nodeType===1&&_t.push({element:lt,left:lt.scrollLeft,top:lt.scrollTop});for(typeof A.focus=="function"&&A.focus(),A=0;A<_t.length;A++){var gt=_t[A];gt.element.scrollLeft=gt.left,gt.element.scrollTop=gt.top}}vu=!!lh,ch=lh=null}finally{Pe=u,Z.p=o,I.T=r}}e.current=i,xn=2}}function M_(){if(xn===2){xn=0;var e=$a,i=Wr,r=(i.flags&8772)!==0;if((i.subtreeFlags&8772)!==0||r){r=I.T,I.T=null;var o=Z.p;Z.p=2;var u=Pe;Pe|=4;try{Zv(e,i.alternate,i)}finally{Pe=u,Z.p=o,I.T=r}}xn=3}}function E_(){if(xn===4||xn===3){xn=0,at();var e=$a,i=Wr,r=ya,o=c_;(i.subtreeFlags&10256)!==0||(i.flags&10256)!==0?xn=5:(xn=0,Wr=$a=null,b_(e,e.pendingLanes));var u=e.pendingLanes;if(u===0&&(Ja=null),Sr(r),i=i.stateNode,qt&&typeof qt.onCommitFiberRoot=="function")try{qt.onCommitFiberRoot(Zt,i,void 0,(i.current.flags&128)===128)}catch{}if(o!==null){i=I.T,u=Z.p,Z.p=2,I.T=null;try{for(var h=e.onRecoverableError,M=0;M<o.length;M++){var A=o[M];h(A.value,{componentStack:A.stack})}}finally{I.T=i,Z.p=u}}(ya&3)!==0&&su(),Qi(e),u=e.pendingLanes,(r&261930)!==0&&(u&42)!==0?e===Qd?Rl++:(Rl=0,Qd=e):Rl=0,wl(0)}}function b_(e,i){(e.pooledCacheLanes&=i)===0&&(i=e.pooledCache,i!=null&&(e.pooledCache=null,cl(i)))}function su(){return S_(),M_(),E_(),T_()}function T_(){if(xn!==5)return!1;var e=$a,i=Wd;Wd=0;var r=Sr(ya),o=I.T,u=Z.p;try{Z.p=32>r?32:r,I.T=null,r=Yd,Yd=null;var h=$a,M=ya;if(xn=0,Wr=$a=null,ya=0,(Pe&6)!==0)throw Error(s(331));var A=Pe;if(Pe|=4,r_(h.current),i_(h,h.current,M,r),Pe=A,wl(0,!1),qt&&typeof qt.onPostCommitFiberRoot=="function")try{qt.onPostCommitFiberRoot(Zt,h)}catch{}return!0}finally{Z.p=u,I.T=o,b_(e,i)}}function A_(e,i,r){i=xi(r,i),i=Cd(e.stateNode,i,2),e=qa(e,i,2),e!==null&&(Rn(e,2),Qi(e))}function He(e,i,r){if(e.tag===3)A_(e,e,r);else for(;i!==null;){if(i.tag===3){A_(i,e,r);break}else if(i.tag===1){var o=i.stateNode;if(typeof i.type.getDerivedStateFromError=="function"||typeof o.componentDidCatch=="function"&&(Ja===null||!Ja.has(o))){e=xi(r,e),r=Cv(2),o=qa(i,r,2),o!==null&&(Rv(r,o,i,e),Rn(o,2),Qi(o));break}}i=i.return}}function Jd(e,i,r){var o=e.pingCache;if(o===null){o=e.pingCache=new CM;var u=new Set;o.set(i,u)}else u=o.get(i),u===void 0&&(u=new Set,o.set(i,u));u.has(r)||(jd=!0,u.add(r),e=UM.bind(null,e,i,r),i.then(e,e))}function UM(e,i,r){var o=e.pingCache;o!==null&&o.delete(i),e.pingedLanes|=e.suspendedLanes&r,e.warmLanes&=~r,Qe===e&&(be&r)===r&&(on===4||on===3&&(be&62914560)===be&&300>pt()-$c?(Pe&2)===0&&Yr(e,0):Xd|=r,qr===be&&(qr=0)),Qi(e)}function C_(e,i){i===0&&(i=_n()),e=zs(e,i),e!==null&&(Rn(e,i),Qi(e))}function LM(e){var i=e.memoizedState,r=0;i!==null&&(r=i.retryLane),C_(e,r)}function OM(e,i){var r=0;switch(e.tag){case 31:case 13:var o=e.stateNode,u=e.memoizedState;u!==null&&(r=u.retryLane);break;case 19:o=e.stateNode;break;case 22:o=e.stateNode._retryCache;break;default:throw Error(s(314))}o!==null&&o.delete(i),C_(e,r)}function PM(e,i){return Yt(e,i)}var ru=null,Zr=null,$d=!1,ou=!1,th=!1,es=0;function Qi(e){e!==Zr&&e.next===null&&(Zr===null?ru=Zr=e:Zr=Zr.next=e),ou=!0,$d||($d=!0,IM())}function wl(e,i){if(!th&&ou){th=!0;do for(var r=!1,o=ru;o!==null;){if(e!==0){var u=o.pendingLanes;if(u===0)var h=0;else{var M=o.suspendedLanes,A=o.pingedLanes;h=(1<<31-ne(42|e)+1)-1,h&=u&~(M&~A),h=h&201326741?h&201326741|1:h?h|2:0}h!==0&&(r=!0,N_(o,h))}else h=be,h=Nt(o,o===Qe?h:0,o.cancelPendingCommit!==null||o.timeoutHandle!==-1),(h&3)===0||ie(o,h)||(r=!0,N_(o,h));o=o.next}while(r);th=!1}}function zM(){R_()}function R_(){ou=$d=!1;var e=0;es!==0&&WM()&&(e=es);for(var i=pt(),r=null,o=ru;o!==null;){var u=o.next,h=w_(o,i);h===0?(o.next=null,r===null?ru=u:r.next=u,u===null&&(Zr=r)):(r=o,(e!==0||(h&3)!==0)&&(ou=!0)),o=u}xn!==0&&xn!==5||wl(e),es!==0&&(es=0)}function w_(e,i){for(var r=e.suspendedLanes,o=e.pingedLanes,u=e.expirationTimes,h=e.pendingLanes&-62914561;0<h;){var M=31-ne(h),A=1<<M,B=u[M];B===-1?((A&r)===0||(A&o)!==0)&&(u[M]=tn(A,i)):B<=i&&(e.expiredLanes|=A),h&=~A}if(i=Qe,r=be,r=Nt(e,e===i?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o=e.callbackNode,r===0||e===i&&(Fe===2||Fe===9)||e.cancelPendingCommit!==null)return o!==null&&o!==null&&L(o),e.callbackNode=null,e.callbackPriority=0;if((r&3)===0||ie(e,r)){if(i=r&-r,i===e.callbackPriority)return i;switch(o!==null&&L(o),Sr(r)){case 2:case 8:r=Xt;break;case 32:r=Dt;break;case 268435456:r=Me;break;default:r=Dt}return o=D_.bind(null,e),r=Yt(r,o),e.callbackPriority=i,e.callbackNode=r,i}return o!==null&&o!==null&&L(o),e.callbackPriority=2,e.callbackNode=null,2}function D_(e,i){if(xn!==0&&xn!==5)return e.callbackNode=null,e.callbackPriority=0,null;var r=e.callbackNode;if(su()&&e.callbackNode!==r)return null;var o=be;return o=Nt(e,e===Qe?o:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o===0?null:(f_(e,o,i),w_(e,pt()),e.callbackNode!=null&&e.callbackNode===r?D_.bind(null,e):null)}function N_(e,i){if(su())return null;f_(e,i,!0)}function IM(){QM(function(){(Pe&6)!==0?Yt(vt,zM):R_()})}function eh(){if(es===0){var e=Pr;e===0&&(e=Rt,Rt<<=1,(Rt&261888)===0&&(Rt=256)),es=e}return es}function U_(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:mc(""+e)}function L_(e,i){var r=i.ownerDocument.createElement("input");return r.name=i.name,r.value=i.value,e.id&&r.setAttribute("form",e.id),i.parentNode.insertBefore(r,i),e=new FormData(e),r.parentNode.removeChild(r),e}function BM(e,i,r,o,u){if(i==="submit"&&r&&r.stateNode===u){var h=U_((u[wn]||null).action),M=o.submitter;M&&(i=(i=M[wn]||null)?U_(i.formAction):M.getAttribute("formAction"),i!==null&&(h=i,M=null));var A=new yc("action","action",null,o,u);e.push({event:A,listeners:[{instance:null,listener:function(){if(o.defaultPrevented){if(es!==0){var B=M?L_(u,M):new FormData(u);Sd(r,{pending:!0,data:B,method:u.method,action:h},null,B)}}else typeof h=="function"&&(A.preventDefault(),B=M?L_(u,M):new FormData(u),Sd(r,{pending:!0,data:B,method:u.method,action:h},h,B))},currentTarget:u}]})}}for(var nh=0;nh<Bf.length;nh++){var ih=Bf[nh],FM=ih.toLowerCase(),HM=ih[0].toUpperCase()+ih.slice(1);Ni(FM,"on"+HM)}Ni(ug,"onAnimationEnd"),Ni(fg,"onAnimationIteration"),Ni(dg,"onAnimationStart"),Ni("dblclick","onDoubleClick"),Ni("focusin","onFocus"),Ni("focusout","onBlur"),Ni(nM,"onTransitionRun"),Ni(iM,"onTransitionStart"),Ni(aM,"onTransitionCancel"),Ni(hg,"onTransitionEnd"),$t("onMouseEnter",["mouseout","mouseover"]),$t("onMouseLeave",["mouseout","mouseover"]),$t("onPointerEnter",["pointerout","pointerover"]),$t("onPointerLeave",["pointerout","pointerover"]),Pt("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),Pt("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),Pt("onBeforeInput",["compositionend","keypress","textInput","paste"]),Pt("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),Pt("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Dl="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),GM=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(Dl));function O_(e,i){i=(i&4)!==0;for(var r=0;r<e.length;r++){var o=e[r],u=o.event;o=o.listeners;t:{var h=void 0;if(i)for(var M=o.length-1;0<=M;M--){var A=o[M],B=A.instance,et=A.currentTarget;if(A=A.listener,B!==h&&u.isPropagationStopped())break t;h=A,u.currentTarget=et;try{h(u)}catch(ht){Mc(ht)}u.currentTarget=null,h=B}else for(M=0;M<o.length;M++){if(A=o[M],B=A.instance,et=A.currentTarget,A=A.listener,B!==h&&u.isPropagationStopped())break t;h=A,u.currentTarget=et;try{h(u)}catch(ht){Mc(ht)}u.currentTarget=null,h=B}}}}function xe(e,i){var r=i[Ko];r===void 0&&(r=i[Ko]=new Set);var o=e+"__bubble";r.has(o)||(P_(i,e,2,!1),r.add(o))}function ah(e,i,r){var o=0;i&&(o|=4),P_(r,e,o,i)}var lu="_reactListening"+Math.random().toString(36).slice(2);function sh(e){if(!e[lu]){e[lu]=!0,Ut.forEach(function(r){r!=="selectionchange"&&(GM.has(r)||ah(r,!1,e),ah(r,!0,e))});var i=e.nodeType===9?e:e.ownerDocument;i===null||i[lu]||(i[lu]=!0,ah("selectionchange",!1,i))}}function P_(e,i,r,o){switch(u0(i)){case 2:var u=m1;break;case 8:u=g1;break;default:u=xh}r=u.bind(null,i,r,e),u=void 0,!Tf||i!=="touchstart"&&i!=="touchmove"&&i!=="wheel"||(u=!0),o?u!==void 0?e.addEventListener(i,r,{capture:!0,passive:u}):e.addEventListener(i,r,!0):u!==void 0?e.addEventListener(i,r,{passive:u}):e.addEventListener(i,r,!1)}function rh(e,i,r,o,u){var h=o;if((i&1)===0&&(i&2)===0&&o!==null)t:for(;;){if(o===null)return;var M=o.tag;if(M===3||M===4){var A=o.stateNode.containerInfo;if(A===u)break;if(M===4)for(M=o.return;M!==null;){var B=M.tag;if((B===3||B===4)&&M.stateNode.containerInfo===u)return;M=M.return}for(;A!==null;){if(M=Q(A),M===null)return;if(B=M.tag,B===5||B===6||B===26||B===27){o=h=M;continue t}A=A.parentNode}}o=o.return}Hm(function(){var et=h,ht=Ef(r),_t=[];t:{var it=pg.get(e);if(it!==void 0){var lt=yc,Gt=e;switch(e){case"keypress":if(vc(r)===0)break t;case"keydown":case"keyup":lt=OS;break;case"focusin":Gt="focus",lt=wf;break;case"focusout":Gt="blur",lt=wf;break;case"beforeblur":case"afterblur":lt=wf;break;case"click":if(r.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":lt=km;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":lt=MS;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":lt=IS;break;case ug:case fg:case dg:lt=TS;break;case hg:lt=FS;break;case"scroll":case"scrollend":lt=xS;break;case"wheel":lt=GS;break;case"copy":case"cut":case"paste":lt=CS;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":lt=Xm;break;case"toggle":case"beforetoggle":lt=kS}var ee=(i&4)!==0,Xe=!ee&&(e==="scroll"||e==="scrollend"),J=ee?it!==null?it+"Capture":null:it;ee=[];for(var j=et,tt;j!==null;){var gt=j;if(tt=gt.stateNode,gt=gt.tag,gt!==5&&gt!==26&&gt!==27||tt===null||J===null||(gt=Jo(j,J),gt!=null&&ee.push(Nl(j,gt,tt))),Xe)break;j=j.return}0<ee.length&&(it=new lt(it,Gt,null,r,ht),_t.push({event:it,listeners:ee}))}}if((i&7)===0){t:{if(it=e==="mouseover"||e==="pointerover",lt=e==="mouseout"||e==="pointerout",it&&r!==Mf&&(Gt=r.relatedTarget||r.fromElement)&&(Q(Gt)||Gt[na]))break t;if((lt||it)&&(it=ht.window===ht?ht:(it=ht.ownerDocument)?it.defaultView||it.parentWindow:window,lt?(Gt=r.relatedTarget||r.toElement,lt=et,Gt=Gt?Q(Gt):null,Gt!==null&&(Xe=c(Gt),ee=Gt.tag,Gt!==Xe||ee!==5&&ee!==27&&ee!==6)&&(Gt=null)):(lt=null,Gt=et),lt!==Gt)){if(ee=km,gt="onMouseLeave",J="onMouseEnter",j="mouse",(e==="pointerout"||e==="pointerover")&&(ee=Xm,gt="onPointerLeave",J="onPointerEnter",j="pointer"),Xe=lt==null?it:rt(lt),tt=Gt==null?it:rt(Gt),it=new ee(gt,j+"leave",lt,r,ht),it.target=Xe,it.relatedTarget=tt,gt=null,Q(ht)===et&&(ee=new ee(J,j+"enter",Gt,r,ht),ee.target=tt,ee.relatedTarget=Xe,gt=ee),Xe=gt,lt&&Gt)e:{for(ee=VM,J=lt,j=Gt,tt=0,gt=J;gt;gt=ee(gt))tt++;gt=0;for(var Jt=j;Jt;Jt=ee(Jt))gt++;for(;0<tt-gt;)J=ee(J),tt--;for(;0<gt-tt;)j=ee(j),gt--;for(;tt--;){if(J===j||j!==null&&J===j.alternate){ee=J;break e}J=ee(J),j=ee(j)}ee=null}else ee=null;lt!==null&&z_(_t,it,lt,ee,!1),Gt!==null&&Xe!==null&&z_(_t,Xe,Gt,ee,!0)}}t:{if(it=et?rt(et):window,lt=it.nodeName&&it.nodeName.toLowerCase(),lt==="select"||lt==="input"&&it.type==="file")var Ue=$m;else if(Km(it))if(tg)Ue=$S;else{Ue=KS;var jt=ZS}else lt=it.nodeName,!lt||lt.toLowerCase()!=="input"||it.type!=="checkbox"&&it.type!=="radio"?et&&Sf(et.elementType)&&(Ue=$m):Ue=JS;if(Ue&&(Ue=Ue(e,et))){Jm(_t,Ue,r,ht);break t}jt&&jt(e,it,et),e==="focusout"&&et&&it.type==="number"&&et.memoizedProps.value!=null&&yn(it,"number",it.value)}switch(jt=et?rt(et):window,e){case"focusin":(Km(jt)||jt.contentEditable==="true")&&(Cr=jt,Pf=et,rl=null);break;case"focusout":rl=Pf=Cr=null;break;case"mousedown":zf=!0;break;case"contextmenu":case"mouseup":case"dragend":zf=!1,lg(_t,r,ht);break;case"selectionchange":if(eM)break;case"keydown":case"keyup":lg(_t,r,ht)}var fe;if(Nf)t:{switch(e){case"compositionstart":var Te="onCompositionStart";break t;case"compositionend":Te="onCompositionEnd";break t;case"compositionupdate":Te="onCompositionUpdate";break t}Te=void 0}else Ar?Qm(e,r)&&(Te="onCompositionEnd"):e==="keydown"&&r.keyCode===229&&(Te="onCompositionStart");Te&&(qm&&r.locale!=="ko"&&(Ar||Te!=="onCompositionStart"?Te==="onCompositionEnd"&&Ar&&(fe=Gm()):(Fa=ht,Af="value"in Fa?Fa.value:Fa.textContent,Ar=!0)),jt=cu(et,Te),0<jt.length&&(Te=new jm(Te,e,null,r,ht),_t.push({event:Te,listeners:jt}),fe?Te.data=fe:(fe=Zm(r),fe!==null&&(Te.data=fe)))),(fe=XS?qS(e,r):WS(e,r))&&(Te=cu(et,"onBeforeInput"),0<Te.length&&(jt=new jm("onBeforeInput","beforeinput",null,r,ht),_t.push({event:jt,listeners:Te}),jt.data=fe)),BM(_t,e,et,r,ht)}O_(_t,i)})}function Nl(e,i,r){return{instance:e,listener:i,currentTarget:r}}function cu(e,i){for(var r=i+"Capture",o=[];e!==null;){var u=e,h=u.stateNode;if(u=u.tag,u!==5&&u!==26&&u!==27||h===null||(u=Jo(e,r),u!=null&&o.unshift(Nl(e,u,h)),u=Jo(e,i),u!=null&&o.push(Nl(e,u,h))),e.tag===3)return o;e=e.return}return[]}function VM(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function z_(e,i,r,o,u){for(var h=i._reactName,M=[];r!==null&&r!==o;){var A=r,B=A.alternate,et=A.stateNode;if(A=A.tag,B!==null&&B===o)break;A!==5&&A!==26&&A!==27||et===null||(B=et,u?(et=Jo(r,h),et!=null&&M.unshift(Nl(r,et,B))):u||(et=Jo(r,h),et!=null&&M.push(Nl(r,et,B)))),r=r.return}M.length!==0&&e.push({event:i,listeners:M})}var kM=/\r\n?/g,jM=/\u0000|\uFFFD/g;function I_(e){return(typeof e=="string"?e:""+e).replace(kM,`
`).replace(jM,"")}function B_(e,i){return i=I_(i),I_(e)===i}function je(e,i,r,o,u,h){switch(r){case"children":typeof o=="string"?i==="body"||i==="textarea"&&o===""||Er(e,o):(typeof o=="number"||typeof o=="bigint")&&i!=="body"&&Er(e,""+o);break;case"className":Ye(e,"class",o);break;case"tabIndex":Ye(e,"tabindex",o);break;case"dir":case"role":case"viewBox":case"width":case"height":Ye(e,r,o);break;case"style":Bm(e,o,h);break;case"data":if(i!=="object"){Ye(e,"data",o);break}case"src":case"href":if(o===""&&(i!=="a"||r!=="href")){e.removeAttribute(r);break}if(o==null||typeof o=="function"||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(r);break}o=mc(""+o),e.setAttribute(r,o);break;case"action":case"formAction":if(typeof o=="function"){e.setAttribute(r,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof h=="function"&&(r==="formAction"?(i!=="input"&&je(e,i,"name",u.name,u,null),je(e,i,"formEncType",u.formEncType,u,null),je(e,i,"formMethod",u.formMethod,u,null),je(e,i,"formTarget",u.formTarget,u,null)):(je(e,i,"encType",u.encType,u,null),je(e,i,"method",u.method,u,null),je(e,i,"target",u.target,u,null)));if(o==null||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(r);break}o=mc(""+o),e.setAttribute(r,o);break;case"onClick":o!=null&&(e.onclick=aa);break;case"onScroll":o!=null&&xe("scroll",e);break;case"onScrollEnd":o!=null&&xe("scrollend",e);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(s(61));if(r=o.__html,r!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"multiple":e.multiple=o&&typeof o!="function"&&typeof o!="symbol";break;case"muted":e.muted=o&&typeof o!="function"&&typeof o!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(o==null||typeof o=="function"||typeof o=="boolean"||typeof o=="symbol"){e.removeAttribute("xlink:href");break}r=mc(""+o),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",r);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,""+o):e.removeAttribute(r);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":o&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,""):e.removeAttribute(r);break;case"capture":case"download":o===!0?e.setAttribute(r,""):o!==!1&&o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(r,o):e.removeAttribute(r);break;case"cols":case"rows":case"size":case"span":o!=null&&typeof o!="function"&&typeof o!="symbol"&&!isNaN(o)&&1<=o?e.setAttribute(r,o):e.removeAttribute(r);break;case"rowSpan":case"start":o==null||typeof o=="function"||typeof o=="symbol"||isNaN(o)?e.removeAttribute(r):e.setAttribute(r,o);break;case"popover":xe("beforetoggle",e),xe("toggle",e),Ze(e,"popover",o);break;case"xlinkActuate":ce(e,"http://www.w3.org/1999/xlink","xlink:actuate",o);break;case"xlinkArcrole":ce(e,"http://www.w3.org/1999/xlink","xlink:arcrole",o);break;case"xlinkRole":ce(e,"http://www.w3.org/1999/xlink","xlink:role",o);break;case"xlinkShow":ce(e,"http://www.w3.org/1999/xlink","xlink:show",o);break;case"xlinkTitle":ce(e,"http://www.w3.org/1999/xlink","xlink:title",o);break;case"xlinkType":ce(e,"http://www.w3.org/1999/xlink","xlink:type",o);break;case"xmlBase":ce(e,"http://www.w3.org/XML/1998/namespace","xml:base",o);break;case"xmlLang":ce(e,"http://www.w3.org/XML/1998/namespace","xml:lang",o);break;case"xmlSpace":ce(e,"http://www.w3.org/XML/1998/namespace","xml:space",o);break;case"is":Ze(e,"is",o);break;case"innerText":case"textContent":break;default:(!(2<r.length)||r[0]!=="o"&&r[0]!=="O"||r[1]!=="n"&&r[1]!=="N")&&(r=_S.get(r)||r,Ze(e,r,o))}}function oh(e,i,r,o,u,h){switch(r){case"style":Bm(e,o,h);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(s(61));if(r=o.__html,r!=null){if(u.children!=null)throw Error(s(60));e.innerHTML=r}}break;case"children":typeof o=="string"?Er(e,o):(typeof o=="number"||typeof o=="bigint")&&Er(e,""+o);break;case"onScroll":o!=null&&xe("scroll",e);break;case"onScrollEnd":o!=null&&xe("scrollend",e);break;case"onClick":o!=null&&(e.onclick=aa);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!It.hasOwnProperty(r))t:{if(r[0]==="o"&&r[1]==="n"&&(u=r.endsWith("Capture"),i=r.slice(2,u?r.length-7:void 0),h=e[wn]||null,h=h!=null?h[r]:null,typeof h=="function"&&e.removeEventListener(i,h,u),typeof o=="function")){typeof h!="function"&&h!==null&&(r in e?e[r]=null:e.hasAttribute(r)&&e.removeAttribute(r)),e.addEventListener(i,o,u);break t}r in e?e[r]=o:o===!0?e.setAttribute(r,""):Ze(e,r,o)}}}function Ln(e,i,r){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":xe("error",e),xe("load",e);var o=!1,u=!1,h;for(h in r)if(r.hasOwnProperty(h)){var M=r[h];if(M!=null)switch(h){case"src":o=!0;break;case"srcSet":u=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(s(137,i));default:je(e,i,h,M,r,null)}}u&&je(e,i,"srcSet",r.srcSet,r,null),o&&je(e,i,"src",r.src,r,null);return;case"input":xe("invalid",e);var A=h=M=u=null,B=null,et=null;for(o in r)if(r.hasOwnProperty(o)){var ht=r[o];if(ht!=null)switch(o){case"name":u=ht;break;case"type":M=ht;break;case"checked":B=ht;break;case"defaultChecked":et=ht;break;case"value":h=ht;break;case"defaultValue":A=ht;break;case"children":case"dangerouslySetInnerHTML":if(ht!=null)throw Error(s(137,i));break;default:je(e,i,o,ht,r,null)}}Vn(e,h,A,B,et,M,u,!1);return;case"select":xe("invalid",e),o=M=h=null;for(u in r)if(r.hasOwnProperty(u)&&(A=r[u],A!=null))switch(u){case"value":h=A;break;case"defaultValue":M=A;break;case"multiple":o=A;default:je(e,i,u,A,r,null)}i=h,r=M,e.multiple=!!o,i!=null?cn(e,!!o,i,!1):r!=null&&cn(e,!!o,r,!0);return;case"textarea":xe("invalid",e),h=u=o=null;for(M in r)if(r.hasOwnProperty(M)&&(A=r[M],A!=null))switch(M){case"value":o=A;break;case"defaultValue":u=A;break;case"children":h=A;break;case"dangerouslySetInnerHTML":if(A!=null)throw Error(s(91));break;default:je(e,i,M,A,r,null)}Xi(e,o,u,h);return;case"option":for(B in r)if(r.hasOwnProperty(B)&&(o=r[B],o!=null))switch(B){case"selected":e.selected=o&&typeof o!="function"&&typeof o!="symbol";break;default:je(e,i,B,o,r,null)}return;case"dialog":xe("beforetoggle",e),xe("toggle",e),xe("cancel",e),xe("close",e);break;case"iframe":case"object":xe("load",e);break;case"video":case"audio":for(o=0;o<Dl.length;o++)xe(Dl[o],e);break;case"image":xe("error",e),xe("load",e);break;case"details":xe("toggle",e);break;case"embed":case"source":case"link":xe("error",e),xe("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in r)if(r.hasOwnProperty(et)&&(o=r[et],o!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(s(137,i));default:je(e,i,et,o,r,null)}return;default:if(Sf(i)){for(ht in r)r.hasOwnProperty(ht)&&(o=r[ht],o!==void 0&&oh(e,i,ht,o,r,void 0));return}}for(A in r)r.hasOwnProperty(A)&&(o=r[A],o!=null&&je(e,i,A,o,r,null))}function XM(e,i,r,o){switch(i){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var u=null,h=null,M=null,A=null,B=null,et=null,ht=null;for(lt in r){var _t=r[lt];if(r.hasOwnProperty(lt)&&_t!=null)switch(lt){case"checked":break;case"value":break;case"defaultValue":B=_t;default:o.hasOwnProperty(lt)||je(e,i,lt,null,o,_t)}}for(var it in o){var lt=o[it];if(_t=r[it],o.hasOwnProperty(it)&&(lt!=null||_t!=null))switch(it){case"type":h=lt;break;case"name":u=lt;break;case"checked":et=lt;break;case"defaultChecked":ht=lt;break;case"value":M=lt;break;case"defaultValue":A=lt;break;case"children":case"dangerouslySetInnerHTML":if(lt!=null)throw Error(s(137,i));break;default:lt!==_t&&je(e,i,it,lt,o,_t)}}zn(e,M,A,B,et,ht,h,u);return;case"select":lt=M=A=it=null;for(h in r)if(B=r[h],r.hasOwnProperty(h)&&B!=null)switch(h){case"value":break;case"multiple":lt=B;default:o.hasOwnProperty(h)||je(e,i,h,null,o,B)}for(u in o)if(h=o[u],B=r[u],o.hasOwnProperty(u)&&(h!=null||B!=null))switch(u){case"value":it=h;break;case"defaultValue":A=h;break;case"multiple":M=h;default:h!==B&&je(e,i,u,h,o,B)}i=A,r=M,o=lt,it!=null?cn(e,!!r,it,!1):!!o!=!!r&&(i!=null?cn(e,!!r,i,!0):cn(e,!!r,r?[]:"",!1));return;case"textarea":lt=it=null;for(A in r)if(u=r[A],r.hasOwnProperty(A)&&u!=null&&!o.hasOwnProperty(A))switch(A){case"value":break;case"children":break;default:je(e,i,A,null,o,u)}for(M in o)if(u=o[M],h=r[M],o.hasOwnProperty(M)&&(u!=null||h!=null))switch(M){case"value":it=u;break;case"defaultValue":lt=u;break;case"children":break;case"dangerouslySetInnerHTML":if(u!=null)throw Error(s(91));break;default:u!==h&&je(e,i,M,u,o,h)}Mr(e,it,lt);return;case"option":for(var Gt in r)if(it=r[Gt],r.hasOwnProperty(Gt)&&it!=null&&!o.hasOwnProperty(Gt))switch(Gt){case"selected":e.selected=!1;break;default:je(e,i,Gt,null,o,it)}for(B in o)if(it=o[B],lt=r[B],o.hasOwnProperty(B)&&it!==lt&&(it!=null||lt!=null))switch(B){case"selected":e.selected=it&&typeof it!="function"&&typeof it!="symbol";break;default:je(e,i,B,it,o,lt)}return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var ee in r)it=r[ee],r.hasOwnProperty(ee)&&it!=null&&!o.hasOwnProperty(ee)&&je(e,i,ee,null,o,it);for(et in o)if(it=o[et],lt=r[et],o.hasOwnProperty(et)&&it!==lt&&(it!=null||lt!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(it!=null)throw Error(s(137,i));break;default:je(e,i,et,it,o,lt)}return;default:if(Sf(i)){for(var Xe in r)it=r[Xe],r.hasOwnProperty(Xe)&&it!==void 0&&!o.hasOwnProperty(Xe)&&oh(e,i,Xe,void 0,o,it);for(ht in o)it=o[ht],lt=r[ht],!o.hasOwnProperty(ht)||it===lt||it===void 0&&lt===void 0||oh(e,i,ht,it,o,lt);return}}for(var J in r)it=r[J],r.hasOwnProperty(J)&&it!=null&&!o.hasOwnProperty(J)&&je(e,i,J,null,o,it);for(_t in o)it=o[_t],lt=r[_t],!o.hasOwnProperty(_t)||it===lt||it==null&&lt==null||je(e,i,_t,it,o,lt)}function F_(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function qM(){if(typeof performance.getEntriesByType=="function"){for(var e=0,i=0,r=performance.getEntriesByType("resource"),o=0;o<r.length;o++){var u=r[o],h=u.transferSize,M=u.initiatorType,A=u.duration;if(h&&A&&F_(M)){for(M=0,A=u.responseEnd,o+=1;o<r.length;o++){var B=r[o],et=B.startTime;if(et>A)break;var ht=B.transferSize,_t=B.initiatorType;ht&&F_(_t)&&(B=B.responseEnd,M+=ht*(B<A?1:(A-et)/(B-et)))}if(--o,i+=8*(h+M)/(u.duration/1e3),e++,10<e)break}}if(0<e)return i/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var lh=null,ch=null;function uu(e){return e.nodeType===9?e:e.ownerDocument}function H_(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function G_(e,i){if(e===0)switch(i){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&i==="foreignObject"?0:e}function uh(e,i){return e==="textarea"||e==="noscript"||typeof i.children=="string"||typeof i.children=="number"||typeof i.children=="bigint"||typeof i.dangerouslySetInnerHTML=="object"&&i.dangerouslySetInnerHTML!==null&&i.dangerouslySetInnerHTML.__html!=null}var fh=null;function WM(){var e=window.event;return e&&e.type==="popstate"?e===fh?!1:(fh=e,!0):(fh=null,!1)}var V_=typeof setTimeout=="function"?setTimeout:void 0,YM=typeof clearTimeout=="function"?clearTimeout:void 0,k_=typeof Promise=="function"?Promise:void 0,QM=typeof queueMicrotask=="function"?queueMicrotask:typeof k_<"u"?function(e){return k_.resolve(null).then(e).catch(ZM)}:V_;function ZM(e){setTimeout(function(){throw e})}function ns(e){return e==="head"}function j_(e,i){var r=i,o=0;do{var u=r.nextSibling;if(e.removeChild(r),u&&u.nodeType===8)if(r=u.data,r==="/$"||r==="/&"){if(o===0){e.removeChild(u),to(i);return}o--}else if(r==="$"||r==="$?"||r==="$~"||r==="$!"||r==="&")o++;else if(r==="html")Ul(e.ownerDocument.documentElement);else if(r==="head"){r=e.ownerDocument.head,Ul(r);for(var h=r.firstChild;h;){var M=h.nextSibling,A=h.nodeName;h[Ns]||A==="SCRIPT"||A==="STYLE"||A==="LINK"&&h.rel.toLowerCase()==="stylesheet"||r.removeChild(h),h=M}}else r==="body"&&Ul(e.ownerDocument.body);r=u}while(r);to(i)}function X_(e,i){var r=e;e=0;do{var o=r.nextSibling;if(r.nodeType===1?i?(r._stashedDisplay=r.style.display,r.style.display="none"):(r.style.display=r._stashedDisplay||"",r.getAttribute("style")===""&&r.removeAttribute("style")):r.nodeType===3&&(i?(r._stashedText=r.nodeValue,r.nodeValue=""):r.nodeValue=r._stashedText||""),o&&o.nodeType===8)if(r=o.data,r==="/$"){if(e===0)break;e--}else r!=="$"&&r!=="$?"&&r!=="$~"&&r!=="$!"||e++;r=o}while(r)}function dh(e){var i=e.firstChild;for(i&&i.nodeType===10&&(i=i.nextSibling);i;){var r=i;switch(i=i.nextSibling,r.nodeName){case"HTML":case"HEAD":case"BODY":dh(r),w(r);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(r.rel.toLowerCase()==="stylesheet")continue}e.removeChild(r)}}function KM(e,i,r,o){for(;e.nodeType===1;){var u=r;if(e.nodeName.toLowerCase()!==i.toLowerCase()){if(!o&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(o){if(!e[Ns])switch(i){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(h=e.getAttribute("rel"),h==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(h!==u.rel||e.getAttribute("href")!==(u.href==null||u.href===""?null:u.href)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin)||e.getAttribute("title")!==(u.title==null?null:u.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(h=e.getAttribute("src"),(h!==(u.src==null?null:u.src)||e.getAttribute("type")!==(u.type==null?null:u.type)||e.getAttribute("crossorigin")!==(u.crossOrigin==null?null:u.crossOrigin))&&h&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(i==="input"&&e.type==="hidden"){var h=u.name==null?null:""+u.name;if(u.type==="hidden"&&e.getAttribute("name")===h)return e}else return e;if(e=Ti(e.nextSibling),e===null)break}return null}function JM(e,i,r){if(i==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!r||(e=Ti(e.nextSibling),e===null))return null;return e}function q_(e,i){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!i||(e=Ti(e.nextSibling),e===null))return null;return e}function hh(e){return e.data==="$?"||e.data==="$~"}function ph(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function $M(e,i){var r=e.ownerDocument;if(e.data==="$~")e._reactRetry=i;else if(e.data!=="$?"||r.readyState!=="loading")i();else{var o=function(){i(),r.removeEventListener("DOMContentLoaded",o)};r.addEventListener("DOMContentLoaded",o),e._reactRetry=o}}function Ti(e){for(;e!=null;e=e.nextSibling){var i=e.nodeType;if(i===1||i===3)break;if(i===8){if(i=e.data,i==="$"||i==="$!"||i==="$?"||i==="$~"||i==="&"||i==="F!"||i==="F")break;if(i==="/$"||i==="/&")return null}}return e}var mh=null;function W_(e){e=e.nextSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="/$"||r==="/&"){if(i===0)return Ti(e.nextSibling);i--}else r!=="$"&&r!=="$!"&&r!=="$?"&&r!=="$~"&&r!=="&"||i++}e=e.nextSibling}return null}function Y_(e){e=e.previousSibling;for(var i=0;e;){if(e.nodeType===8){var r=e.data;if(r==="$"||r==="$!"||r==="$?"||r==="$~"||r==="&"){if(i===0)return e;i--}else r!=="/$"&&r!=="/&"||i++}e=e.previousSibling}return null}function Q_(e,i,r){switch(i=uu(r),e){case"html":if(e=i.documentElement,!e)throw Error(s(452));return e;case"head":if(e=i.head,!e)throw Error(s(453));return e;case"body":if(e=i.body,!e)throw Error(s(454));return e;default:throw Error(s(451))}}function Ul(e){for(var i=e.attributes;i.length;)e.removeAttributeNode(i[0]);w(e)}var Ai=new Map,Z_=new Set;function fu(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var xa=Z.d;Z.d={f:t1,r:e1,D:n1,C:i1,L:a1,m:s1,X:o1,S:r1,M:l1};function t1(){var e=xa.f(),i=nu();return e||i}function e1(e){var i=st(e);i!==null&&i.tag===5&&i.type==="form"?hv(i):xa.r(e)}var Kr=typeof document>"u"?null:document;function K_(e,i,r){var o=Kr;if(o&&typeof i=="string"&&i){var u=_e(i);u='link[rel="'+e+'"][href="'+u+'"]',typeof r=="string"&&(u+='[crossorigin="'+r+'"]'),Z_.has(u)||(Z_.add(u),e={rel:e,crossOrigin:r,href:i},o.querySelector(u)===null&&(i=o.createElement("link"),Ln(i,"link",e),xt(i),o.head.appendChild(i)))}}function n1(e){xa.D(e),K_("dns-prefetch",e,null)}function i1(e,i){xa.C(e,i),K_("preconnect",e,i)}function a1(e,i,r){xa.L(e,i,r);var o=Kr;if(o&&e&&i){var u='link[rel="preload"][as="'+_e(i)+'"]';i==="image"&&r&&r.imageSrcSet?(u+='[imagesrcset="'+_e(r.imageSrcSet)+'"]',typeof r.imageSizes=="string"&&(u+='[imagesizes="'+_e(r.imageSizes)+'"]')):u+='[href="'+_e(e)+'"]';var h=u;switch(i){case"style":h=Jr(e);break;case"script":h=$r(e)}Ai.has(h)||(e=_({rel:"preload",href:i==="image"&&r&&r.imageSrcSet?void 0:e,as:i},r),Ai.set(h,e),o.querySelector(u)!==null||i==="style"&&o.querySelector(Ll(h))||i==="script"&&o.querySelector(Ol(h))||(i=o.createElement("link"),Ln(i,"link",e),xt(i),o.head.appendChild(i)))}}function s1(e,i){xa.m(e,i);var r=Kr;if(r&&e){var o=i&&typeof i.as=="string"?i.as:"script",u='link[rel="modulepreload"][as="'+_e(o)+'"][href="'+_e(e)+'"]',h=u;switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":h=$r(e)}if(!Ai.has(h)&&(e=_({rel:"modulepreload",href:e},i),Ai.set(h,e),r.querySelector(u)===null)){switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(r.querySelector(Ol(h)))return}o=r.createElement("link"),Ln(o,"link",e),xt(o),r.head.appendChild(o)}}}function r1(e,i,r){xa.S(e,i,r);var o=Kr;if(o&&e){var u=K(o).hoistableStyles,h=Jr(e);i=i||"default";var M=u.get(h);if(!M){var A={loading:0,preload:null};if(M=o.querySelector(Ll(h)))A.loading=5;else{e=_({rel:"stylesheet",href:e,"data-precedence":i},r),(r=Ai.get(h))&&gh(e,r);var B=M=o.createElement("link");xt(B),Ln(B,"link",e),B._p=new Promise(function(et,ht){B.onload=et,B.onerror=ht}),B.addEventListener("load",function(){A.loading|=1}),B.addEventListener("error",function(){A.loading|=2}),A.loading|=4,du(M,i,o)}M={type:"stylesheet",instance:M,count:1,state:A},u.set(h,M)}}}function o1(e,i){xa.X(e,i);var r=Kr;if(r&&e){var o=K(r).hoistableScripts,u=$r(e),h=o.get(u);h||(h=r.querySelector(Ol(u)),h||(e=_({src:e,async:!0},i),(i=Ai.get(u))&&vh(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(u,h))}}function l1(e,i){xa.M(e,i);var r=Kr;if(r&&e){var o=K(r).hoistableScripts,u=$r(e),h=o.get(u);h||(h=r.querySelector(Ol(u)),h||(e=_({src:e,async:!0,type:"module"},i),(i=Ai.get(u))&&vh(e,i),h=r.createElement("script"),xt(h),Ln(h,"link",e),r.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(u,h))}}function J_(e,i,r,o){var u=(u=Tt.current)?fu(u):null;if(!u)throw Error(s(446));switch(e){case"meta":case"title":return null;case"style":return typeof r.precedence=="string"&&typeof r.href=="string"?(i=Jr(r.href),r=K(u).hoistableStyles,o=r.get(i),o||(o={type:"style",instance:null,count:0,state:null},r.set(i,o)),o):{type:"void",instance:null,count:0,state:null};case"link":if(r.rel==="stylesheet"&&typeof r.href=="string"&&typeof r.precedence=="string"){e=Jr(r.href);var h=K(u).hoistableStyles,M=h.get(e);if(M||(u=u.ownerDocument||u,M={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},h.set(e,M),(h=u.querySelector(Ll(e)))&&!h._p&&(M.instance=h,M.state.loading=5),Ai.has(e)||(r={rel:"preload",as:"style",href:r.href,crossOrigin:r.crossOrigin,integrity:r.integrity,media:r.media,hrefLang:r.hrefLang,referrerPolicy:r.referrerPolicy},Ai.set(e,r),h||c1(u,e,r,M.state))),i&&o===null)throw Error(s(528,""));return M}if(i&&o!==null)throw Error(s(529,""));return null;case"script":return i=r.async,r=r.src,typeof r=="string"&&i&&typeof i!="function"&&typeof i!="symbol"?(i=$r(r),r=K(u).hoistableScripts,o=r.get(i),o||(o={type:"script",instance:null,count:0,state:null},r.set(i,o)),o):{type:"void",instance:null,count:0,state:null};default:throw Error(s(444,e))}}function Jr(e){return'href="'+_e(e)+'"'}function Ll(e){return'link[rel="stylesheet"]['+e+"]"}function $_(e){return _({},e,{"data-precedence":e.precedence,precedence:null})}function c1(e,i,r,o){e.querySelector('link[rel="preload"][as="style"]['+i+"]")?o.loading=1:(i=e.createElement("link"),o.preload=i,i.addEventListener("load",function(){return o.loading|=1}),i.addEventListener("error",function(){return o.loading|=2}),Ln(i,"link",r),xt(i),e.head.appendChild(i))}function $r(e){return'[src="'+_e(e)+'"]'}function Ol(e){return"script[async]"+e}function t0(e,i,r){if(i.count++,i.instance===null)switch(i.type){case"style":var o=e.querySelector('style[data-href~="'+_e(r.href)+'"]');if(o)return i.instance=o,xt(o),o;var u=_({},r,{"data-href":r.href,"data-precedence":r.precedence,href:null,precedence:null});return o=(e.ownerDocument||e).createElement("style"),xt(o),Ln(o,"style",u),du(o,r.precedence,e),i.instance=o;case"stylesheet":u=Jr(r.href);var h=e.querySelector(Ll(u));if(h)return i.state.loading|=4,i.instance=h,xt(h),h;o=$_(r),(u=Ai.get(u))&&gh(o,u),h=(e.ownerDocument||e).createElement("link"),xt(h);var M=h;return M._p=new Promise(function(A,B){M.onload=A,M.onerror=B}),Ln(h,"link",o),i.state.loading|=4,du(h,r.precedence,e),i.instance=h;case"script":return h=$r(r.src),(u=e.querySelector(Ol(h)))?(i.instance=u,xt(u),u):(o=r,(u=Ai.get(h))&&(o=_({},r),vh(o,u)),e=e.ownerDocument||e,u=e.createElement("script"),xt(u),Ln(u,"link",o),e.head.appendChild(u),i.instance=u);case"void":return null;default:throw Error(s(443,i.type))}else i.type==="stylesheet"&&(i.state.loading&4)===0&&(o=i.instance,i.state.loading|=4,du(o,r.precedence,e));return i.instance}function du(e,i,r){for(var o=r.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),u=o.length?o[o.length-1]:null,h=u,M=0;M<o.length;M++){var A=o[M];if(A.dataset.precedence===i)h=A;else if(h!==u)break}h?h.parentNode.insertBefore(e,h.nextSibling):(i=r.nodeType===9?r.head:r,i.insertBefore(e,i.firstChild))}function gh(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.title==null&&(e.title=i.title)}function vh(e,i){e.crossOrigin==null&&(e.crossOrigin=i.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=i.referrerPolicy),e.integrity==null&&(e.integrity=i.integrity)}var hu=null;function e0(e,i,r){if(hu===null){var o=new Map,u=hu=new Map;u.set(r,o)}else u=hu,o=u.get(r),o||(o=new Map,u.set(r,o));if(o.has(e))return o;for(o.set(e,null),r=r.getElementsByTagName(e),u=0;u<r.length;u++){var h=r[u];if(!(h[Ns]||h[sn]||e==="link"&&h.getAttribute("rel")==="stylesheet")&&h.namespaceURI!=="http://www.w3.org/2000/svg"){var M=h.getAttribute(i)||"";M=e+M;var A=o.get(M);A?A.push(h):o.set(M,[h])}}return o}function n0(e,i,r){e=e.ownerDocument||e,e.head.insertBefore(r,i==="title"?e.querySelector("head > title"):null)}function u1(e,i,r){if(r===1||i.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof i.precedence!="string"||typeof i.href!="string"||i.href==="")break;return!0;case"link":if(typeof i.rel!="string"||typeof i.href!="string"||i.href===""||i.onLoad||i.onError)break;switch(i.rel){case"stylesheet":return e=i.disabled,typeof i.precedence=="string"&&e==null;default:return!0}case"script":if(i.async&&typeof i.async!="function"&&typeof i.async!="symbol"&&!i.onLoad&&!i.onError&&i.src&&typeof i.src=="string")return!0}return!1}function i0(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function f1(e,i,r,o){if(r.type==="stylesheet"&&(typeof o.media!="string"||matchMedia(o.media).matches!==!1)&&(r.state.loading&4)===0){if(r.instance===null){var u=Jr(o.href),h=i.querySelector(Ll(u));if(h){i=h._p,i!==null&&typeof i=="object"&&typeof i.then=="function"&&(e.count++,e=pu.bind(e),i.then(e,e)),r.state.loading|=4,r.instance=h,xt(h);return}h=i.ownerDocument||i,o=$_(o),(u=Ai.get(u))&&gh(o,u),h=h.createElement("link"),xt(h);var M=h;M._p=new Promise(function(A,B){M.onload=A,M.onerror=B}),Ln(h,"link",o),r.instance=h}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(r,i),(i=r.state.preload)&&(r.state.loading&3)===0&&(e.count++,r=pu.bind(e),i.addEventListener("load",r),i.addEventListener("error",r))}}var _h=0;function d1(e,i){return e.stylesheets&&e.count===0&&gu(e,e.stylesheets),0<e.count||0<e.imgCount?function(r){var o=setTimeout(function(){if(e.stylesheets&&gu(e,e.stylesheets),e.unsuspend){var h=e.unsuspend;e.unsuspend=null,h()}},6e4+i);0<e.imgBytes&&_h===0&&(_h=62500*qM());var u=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&gu(e,e.stylesheets),e.unsuspend)){var h=e.unsuspend;e.unsuspend=null,h()}},(e.imgBytes>_h?50:800)+i);return e.unsuspend=r,function(){e.unsuspend=null,clearTimeout(o),clearTimeout(u)}}:null}function pu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)gu(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var mu=null;function gu(e,i){e.stylesheets=null,e.unsuspend!==null&&(e.count++,mu=new Map,i.forEach(h1,e),mu=null,pu.call(e))}function h1(e,i){if(!(i.state.loading&4)){var r=mu.get(e);if(r)var o=r.get(null);else{r=new Map,mu.set(e,r);for(var u=e.querySelectorAll("link[data-precedence],style[data-precedence]"),h=0;h<u.length;h++){var M=u[h];(M.nodeName==="LINK"||M.getAttribute("media")!=="not all")&&(r.set(M.dataset.precedence,M),o=M)}o&&r.set(null,o)}u=i.instance,M=u.getAttribute("data-precedence"),h=r.get(M)||o,h===o&&r.set(null,u),r.set(M,u),this.count++,o=pu.bind(this),u.addEventListener("load",o),u.addEventListener("error",o),h?h.parentNode.insertBefore(u,h.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(u,e.firstChild)),i.state.loading|=4}}var Pl={$$typeof:N,Provider:null,Consumer:null,_currentValue:$,_currentValue2:$,_threadCount:0};function p1(e,i,r,o,u,h,M,A,B){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=we(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=we(0),this.hiddenUpdates=we(null),this.identifierPrefix=o,this.onUncaughtError=u,this.onCaughtError=h,this.onRecoverableError=M,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=B,this.incompleteTransitions=new Map}function a0(e,i,r,o,u,h,M,A,B,et,ht,_t){return e=new p1(e,i,r,M,B,et,ht,_t,A),i=1,h===!0&&(i|=24),h=oi(3,null,null,i),e.current=h,h.stateNode=e,i=Kf(),i.refCount++,e.pooledCache=i,i.refCount++,h.memoizedState={element:o,isDehydrated:r,cache:i},ed(h),e}function s0(e){return e?(e=Dr,e):Dr}function r0(e,i,r,o,u,h){u=s0(u),o.context===null?o.context=u:o.pendingContext=u,o=Xa(i),o.payload={element:r},h=h===void 0?null:h,h!==null&&(o.callback=h),r=qa(e,o,i),r!==null&&(ti(r,e,i),hl(r,e,i))}function o0(e,i){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var r=e.retryLane;e.retryLane=r!==0&&r<i?r:i}}function yh(e,i){o0(e,i),(e=e.alternate)&&o0(e,i)}function l0(e){if(e.tag===13||e.tag===31){var i=zs(e,67108864);i!==null&&ti(i,e,67108864),yh(e,67108864)}}function c0(e){if(e.tag===13||e.tag===31){var i=di();i=ws(i);var r=zs(e,i);r!==null&&ti(r,e,i),yh(e,i)}}var vu=!0;function m1(e,i,r,o){var u=I.T;I.T=null;var h=Z.p;try{Z.p=2,xh(e,i,r,o)}finally{Z.p=h,I.T=u}}function g1(e,i,r,o){var u=I.T;I.T=null;var h=Z.p;try{Z.p=8,xh(e,i,r,o)}finally{Z.p=h,I.T=u}}function xh(e,i,r,o){if(vu){var u=Sh(o);if(u===null)rh(e,i,o,_u,r),f0(e,o);else if(_1(u,e,i,r,o))o.stopPropagation();else if(f0(e,o),i&4&&-1<v1.indexOf(e)){for(;u!==null;){var h=st(u);if(h!==null)switch(h.tag){case 3:if(h=h.stateNode,h.current.memoizedState.isDehydrated){var M=wt(h.pendingLanes);if(M!==0){var A=h;for(A.pendingLanes|=2,A.entangledLanes|=2;M;){var B=1<<31-ne(M);A.entanglements[1]|=B,M&=~B}Qi(h),(Pe&6)===0&&(tu=pt()+500,wl(0))}}break;case 31:case 13:A=zs(h,2),A!==null&&ti(A,h,2),nu(),yh(h,2)}if(h=Sh(o),h===null&&rh(e,i,o,_u,r),h===u)break;u=h}u!==null&&o.stopPropagation()}else rh(e,i,o,null,r)}}function Sh(e){return e=Ef(e),Mh(e)}var _u=null;function Mh(e){if(_u=null,e=Q(e),e!==null){var i=c(e);if(i===null)e=null;else{var r=i.tag;if(r===13){if(e=f(i),e!==null)return e;e=null}else if(r===31){if(e=d(i),e!==null)return e;e=null}else if(r===3){if(i.stateNode.current.memoizedState.isDehydrated)return i.tag===3?i.stateNode.containerInfo:null;e=null}else i!==e&&(e=null)}}return _u=e,null}function u0(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(bt()){case vt:return 2;case Xt:return 8;case Dt:case Bt:return 32;case Me:return 268435456;default:return 32}default:return 32}}var Eh=!1,is=null,as=null,ss=null,zl=new Map,Il=new Map,rs=[],v1="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function f0(e,i){switch(e){case"focusin":case"focusout":is=null;break;case"dragenter":case"dragleave":as=null;break;case"mouseover":case"mouseout":ss=null;break;case"pointerover":case"pointerout":zl.delete(i.pointerId);break;case"gotpointercapture":case"lostpointercapture":Il.delete(i.pointerId)}}function Bl(e,i,r,o,u,h){return e===null||e.nativeEvent!==h?(e={blockedOn:i,domEventName:r,eventSystemFlags:o,nativeEvent:h,targetContainers:[u]},i!==null&&(i=st(i),i!==null&&l0(i)),e):(e.eventSystemFlags|=o,i=e.targetContainers,u!==null&&i.indexOf(u)===-1&&i.push(u),e)}function _1(e,i,r,o,u){switch(i){case"focusin":return is=Bl(is,e,i,r,o,u),!0;case"dragenter":return as=Bl(as,e,i,r,o,u),!0;case"mouseover":return ss=Bl(ss,e,i,r,o,u),!0;case"pointerover":var h=u.pointerId;return zl.set(h,Bl(zl.get(h)||null,e,i,r,o,u)),!0;case"gotpointercapture":return h=u.pointerId,Il.set(h,Bl(Il.get(h)||null,e,i,r,o,u)),!0}return!1}function d0(e){var i=Q(e.target);if(i!==null){var r=c(i);if(r!==null){if(i=r.tag,i===13){if(i=f(r),i!==null){e.blockedOn=i,Ds(e.priority,function(){c0(r)});return}}else if(i===31){if(i=d(r),i!==null){e.blockedOn=i,Ds(e.priority,function(){c0(r)});return}}else if(i===3&&r.stateNode.current.memoizedState.isDehydrated){e.blockedOn=r.tag===3?r.stateNode.containerInfo:null;return}}}e.blockedOn=null}function yu(e){if(e.blockedOn!==null)return!1;for(var i=e.targetContainers;0<i.length;){var r=Sh(e.nativeEvent);if(r===null){r=e.nativeEvent;var o=new r.constructor(r.type,r);Mf=o,r.target.dispatchEvent(o),Mf=null}else return i=st(r),i!==null&&l0(i),e.blockedOn=r,!1;i.shift()}return!0}function h0(e,i,r){yu(e)&&r.delete(i)}function y1(){Eh=!1,is!==null&&yu(is)&&(is=null),as!==null&&yu(as)&&(as=null),ss!==null&&yu(ss)&&(ss=null),zl.forEach(h0),Il.forEach(h0)}function xu(e,i){e.blockedOn===i&&(e.blockedOn=null,Eh||(Eh=!0,a.unstable_scheduleCallback(a.unstable_NormalPriority,y1)))}var Su=null;function p0(e){Su!==e&&(Su=e,a.unstable_scheduleCallback(a.unstable_NormalPriority,function(){Su===e&&(Su=null);for(var i=0;i<e.length;i+=3){var r=e[i],o=e[i+1],u=e[i+2];if(typeof o!="function"){if(Mh(o||r)===null)continue;break}var h=st(r);h!==null&&(e.splice(i,3),i-=3,Sd(h,{pending:!0,data:u,method:r.method,action:o},o,u))}}))}function to(e){function i(B){return xu(B,e)}is!==null&&xu(is,e),as!==null&&xu(as,e),ss!==null&&xu(ss,e),zl.forEach(i),Il.forEach(i);for(var r=0;r<rs.length;r++){var o=rs[r];o.blockedOn===e&&(o.blockedOn=null)}for(;0<rs.length&&(r=rs[0],r.blockedOn===null);)d0(r),r.blockedOn===null&&rs.shift();if(r=(e.ownerDocument||e).$$reactFormReplay,r!=null)for(o=0;o<r.length;o+=3){var u=r[o],h=r[o+1],M=u[wn]||null;if(typeof h=="function")M||p0(r);else if(M){var A=null;if(h&&h.hasAttribute("formAction")){if(u=h,M=h[wn]||null)A=M.formAction;else if(Mh(u)!==null)continue}else A=M.action;typeof A=="function"?r[o+1]=A:(r.splice(o,3),o-=3),p0(r)}}}function m0(){function e(h){h.canIntercept&&h.info==="react-transition"&&h.intercept({handler:function(){return new Promise(function(M){return u=M})},focusReset:"manual",scroll:"manual"})}function i(){u!==null&&(u(),u=null),o||setTimeout(r,20)}function r(){if(!o&&!navigation.transition){var h=navigation.currentEntry;h&&h.url!=null&&navigation.navigate(h.url,{state:h.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var o=!1,u=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",i),navigation.addEventListener("navigateerror",i),setTimeout(r,100),function(){o=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",i),navigation.removeEventListener("navigateerror",i),u!==null&&(u(),u=null)}}}function bh(e){this._internalRoot=e}Mu.prototype.render=bh.prototype.render=function(e){var i=this._internalRoot;if(i===null)throw Error(s(409));var r=i.current,o=di();r0(r,o,e,i,null,null)},Mu.prototype.unmount=bh.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var i=e.containerInfo;r0(e.current,2,null,e,null,null),nu(),i[na]=null}};function Mu(e){this._internalRoot=e}Mu.prototype.unstable_scheduleHydration=function(e){if(e){var i=Zo();e={blockedOn:null,target:e,priority:i};for(var r=0;r<rs.length&&i!==0&&i<rs[r].priority;r++);rs.splice(r,0,e),r===0&&d0(e)}};var g0=t.version;if(g0!=="19.2.7")throw Error(s(527,g0,"19.2.7"));Z.findDOMNode=function(e){var i=e._reactInternals;if(i===void 0)throw typeof e.render=="function"?Error(s(188)):(e=Object.keys(e).join(","),Error(s(268,e)));return e=m(i),e=e!==null?g(e):null,e=e===null?null:e.stateNode,e};var x1={bundleType:0,version:"19.2.7",rendererPackageName:"react-dom",currentDispatcherRef:I,reconcilerVersion:"19.2.7"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var Eu=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!Eu.isDisabled&&Eu.supportsFiber)try{Zt=Eu.inject(x1),qt=Eu}catch{}}return Hl.createRoot=function(e,i){if(!l(e))throw Error(s(299));var r=!1,o="",u=Ev,h=bv,M=Tv;return i!=null&&(i.unstable_strictMode===!0&&(r=!0),i.identifierPrefix!==void 0&&(o=i.identifierPrefix),i.onUncaughtError!==void 0&&(u=i.onUncaughtError),i.onCaughtError!==void 0&&(h=i.onCaughtError),i.onRecoverableError!==void 0&&(M=i.onRecoverableError)),i=a0(e,1,!1,null,null,r,o,null,u,h,M,m0),e[na]=i.current,sh(e),new bh(i)},Hl.hydrateRoot=function(e,i,r){if(!l(e))throw Error(s(299));var o=!1,u="",h=Ev,M=bv,A=Tv,B=null;return r!=null&&(r.unstable_strictMode===!0&&(o=!0),r.identifierPrefix!==void 0&&(u=r.identifierPrefix),r.onUncaughtError!==void 0&&(h=r.onUncaughtError),r.onCaughtError!==void 0&&(M=r.onCaughtError),r.onRecoverableError!==void 0&&(A=r.onRecoverableError),r.formState!==void 0&&(B=r.formState)),i=a0(e,1,!0,i,r??null,o,u,B,h,M,A,m0),i.context=s0(null),r=i.current,o=di(),o=ws(o),u=Xa(o),u.callback=null,qa(r,u,o),r=o,i.current.lanes=r,Rn(i,r),Qi(i),e[na]=i.current,sh(e),new Mu(i)},Hl.version="19.2.7",Hl}var C0;function N1(){if(C0)return Rh.exports;C0=1;function a(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(a)}catch(t){console.error(t)}}return a(),Rh.exports=D1(),Rh.exports}var U1=N1();const L1=tx(U1);var cc=class{constructor(){this.listeners=new Set,this.subscribe=this.subscribe.bind(this)}subscribe(a){return this.listeners.add(a),this.onSubscribe(),()=>{this.listeners.delete(a),this.onUnsubscribe()}}hasListeners(){return this.listeners.size>0}onSubscribe(){}onUnsubscribe(){}},ur,vs,Eo,jy,O1=(jy=class extends cc{constructor(){super();te(this,ur);te(this,vs);te(this,Eo);zt(this,Eo,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t();return window.addEventListener("visibilitychange",n,!1),()=>{window.removeEventListener("visibilitychange",n)}}})}onSubscribe(){X(this,vs)||this.setEventListener(X(this,Eo))}onUnsubscribe(){var t;this.hasListeners()||((t=X(this,vs))==null||t.call(this),zt(this,vs,void 0))}setEventListener(t){var n;zt(this,Eo,t),(n=X(this,vs))==null||n.call(this),zt(this,vs,t(s=>{typeof s=="boolean"?this.setFocused(s):this.onFocus()}))}setFocused(t){X(this,ur)!==t&&(zt(this,ur,t),this.onFocus())}onFocus(){const t=this.isFocused();this.listeners.forEach(n=>{n(t)})}isFocused(){var t;return typeof X(this,ur)=="boolean"?X(this,ur):((t=globalThis.document)==null?void 0:t.visibilityState)!=="hidden"}},ur=new WeakMap,vs=new WeakMap,Eo=new WeakMap,jy),vm=new O1,P1={setTimeout:(a,t)=>setTimeout(a,t),clearTimeout:a=>clearTimeout(a),setInterval:(a,t)=>setInterval(a,t),clearInterval:a=>clearInterval(a)},_s,mm,Xy,z1=(Xy=class{constructor(){te(this,_s,P1);te(this,mm,!1)}setTimeoutProvider(a){zt(this,_s,a)}setTimeout(a,t){return X(this,_s).setTimeout(a,t)}clearTimeout(a){X(this,_s).clearTimeout(a)}setInterval(a,t){return X(this,_s).setInterval(a,t)}clearInterval(a){X(this,_s).clearInterval(a)}},_s=new WeakMap,mm=new WeakMap,Xy),rr=new z1;function I1(a){setTimeout(a,0)}var B1=typeof window>"u"||"Deno"in globalThis;function ni(){}function F1(a,t){return typeof a=="function"?a(t):a}function dp(a){return typeof a=="number"&&a>=0&&a!==1/0}function ex(a,t){return Math.max(a+(t||0)-Date.now(),0)}function Ts(a,t){return typeof a=="function"?a(t):a}function gi(a,t){return typeof a=="function"?a(t):a}function R0(a,t){const{type:n="all",exact:s,fetchStatus:l,predicate:c,queryKey:f,stale:d}=a;if(f){if(s){if(t.queryHash!==_m(f,t.options))return!1}else if(!tc(t.queryKey,f))return!1}if(n!=="all"){const p=t.isActive();if(n==="active"&&!p||n==="inactive"&&p)return!1}return!(typeof d=="boolean"&&t.isStale()!==d||l&&l!==t.state.fetchStatus||c&&!c(t))}function w0(a,t){const{exact:n,status:s,predicate:l,mutationKey:c}=a;if(c){if(!t.options.mutationKey)return!1;if(n){if($l(t.options.mutationKey)!==$l(c))return!1}else if(!tc(t.options.mutationKey,c))return!1}return!(s&&t.state.status!==s||l&&!l(t))}function _m(a,t){return((t==null?void 0:t.queryKeyHashFn)||$l)(a)}function $l(a){return JSON.stringify(a,(t,n)=>pp(n)?Object.keys(n).sort().reduce((s,l)=>(s[l]=n[l],s),{}):n)}function tc(a,t){return a===t?!0:typeof a!=typeof t?!1:a&&t&&typeof a=="object"&&typeof t=="object"?Object.keys(t).every(n=>tc(a[n],t[n])):!1}var H1=Object.prototype.hasOwnProperty;function nx(a,t,n=0){if(a===t)return a;if(n>500)return t;const s=D0(a)&&D0(t);if(!s&&!(pp(a)&&pp(t)))return t;const c=(s?a:Object.keys(a)).length,f=s?t:Object.keys(t),d=f.length,p=s?new Array(d):{};let m=0;for(let g=0;g<d;g++){const _=s?g:f[g],y=a[_],S=t[_];if(y===S){p[_]=y,(s?g<c:H1.call(a,_))&&m++;continue}if(y===null||S===null||typeof y!="object"||typeof S!="object"){p[_]=S;continue}const b=nx(y,S,n+1);p[_]=b,b===y&&m++}return c===d&&m===c?a:p}function hp(a,t){if(!t||Object.keys(a).length!==Object.keys(t).length)return!1;for(const n in a)if(a[n]!==t[n])return!1;return!0}function D0(a){return Array.isArray(a)&&a.length===Object.keys(a).length}function pp(a){if(!N0(a))return!1;const t=a.constructor;if(t===void 0)return!0;const n=t.prototype;return!(!N0(n)||!n.hasOwnProperty("isPrototypeOf")||Object.getPrototypeOf(a)!==Object.prototype)}function N0(a){return Object.prototype.toString.call(a)==="[object Object]"}function G1(a){return new Promise(t=>{rr.setTimeout(t,a)})}function mp(a,t,n){return typeof n.structuralSharing=="function"?n.structuralSharing(a,t):n.structuralSharing!==!1?nx(a,t):t}function V1(a,t,n=0){const s=[...a,t];return n&&s.length>n?s.slice(1):s}function k1(a,t,n=0){const s=[t,...a];return n&&s.length>n?s.slice(0,-1):s}var ym=Symbol();function ix(a,t){return!a.queryFn&&(t!=null&&t.initialPromise)?()=>t.initialPromise:!a.queryFn||a.queryFn===ym?()=>Promise.reject(new Error(`Missing queryFn: '${a.queryHash}'`)):a.queryFn}function ax(a,t){return typeof a=="function"?a(...t):!!a}function j1(a,t,n){let s=!1,l;return Object.defineProperty(a,"signal",{enumerable:!0,get:()=>(l??(l=t()),s||(s=!0,l.aborted?n():l.addEventListener("abort",n,{once:!0})),l)}),a}var ec=(()=>{let a=()=>B1;return{isServer(){return a()},setIsServer(t){a=t}}})();function gp(){let a,t;const n=new Promise((l,c)=>{a=l,t=c});n.status="pending",n.catch(()=>{});function s(l){Object.assign(n,l),delete n.resolve,delete n.reject}return n.resolve=l=>{s({status:"fulfilled",value:l}),a(l)},n.reject=l=>{s({status:"rejected",reason:l}),t(l)},n}var X1=I1;function q1(){let a=[],t=0,n=d=>{d()},s=d=>{d()},l=X1;const c=d=>{t?a.push(d):l(()=>{n(d)})},f=()=>{const d=a;a=[],d.length&&l(()=>{s(()=>{d.forEach(p=>{n(p)})})})};return{batch:d=>{let p;t++;try{p=d()}finally{t--,t||f()}return p},batchCalls:d=>(...p)=>{c(()=>{d(...p)})},schedule:c,setNotifyFunction:d=>{n=d},setBatchNotifyFunction:d=>{s=d},setScheduler:d=>{l=d}}}var On=q1(),bo,ys,To,qy,W1=(qy=class extends cc{constructor(){super();te(this,bo,!0);te(this,ys);te(this,To);zt(this,To,t=>{if(typeof window<"u"&&window.addEventListener){const n=()=>t(!0),s=()=>t(!1);return window.addEventListener("online",n,!1),window.addEventListener("offline",s,!1),()=>{window.removeEventListener("online",n),window.removeEventListener("offline",s)}}})}onSubscribe(){X(this,ys)||this.setEventListener(X(this,To))}onUnsubscribe(){var t;this.hasListeners()||((t=X(this,ys))==null||t.call(this),zt(this,ys,void 0))}setEventListener(t){var n;zt(this,To,t),(n=X(this,ys))==null||n.call(this),zt(this,ys,t(this.setOnline.bind(this)))}setOnline(t){X(this,bo)!==t&&(zt(this,bo,t),this.listeners.forEach(s=>{s(t)}))}isOnline(){return X(this,bo)}},bo=new WeakMap,ys=new WeakMap,To=new WeakMap,qy),sf=new W1;function Y1(a){return Math.min(1e3*2**a,3e4)}function sx(a){return(a??"online")==="online"?sf.isOnline():!0}var vp=class extends Error{constructor(a){super("CancelledError"),this.revert=a==null?void 0:a.revert,this.silent=a==null?void 0:a.silent}};function rx(a){let t=!1,n=0,s;const l=gp(),c=()=>l.status!=="pending",f=T=>{var E;if(!c()){const x=new vp(T);y(x),(E=a.onCancel)==null||E.call(a,x)}},d=()=>{t=!0},p=()=>{t=!1},m=()=>vm.isFocused()&&(a.networkMode==="always"||sf.isOnline())&&a.canRun(),g=()=>sx(a.networkMode)&&a.canRun(),_=T=>{c()||(s==null||s(),l.resolve(T))},y=T=>{c()||(s==null||s(),l.reject(T))},S=()=>new Promise(T=>{var E;s=x=>{(c()||m())&&T(x)},(E=a.onPause)==null||E.call(a)}).then(()=>{var T;s=void 0,c()||(T=a.onContinue)==null||T.call(a)}),b=()=>{if(c())return;let T;const E=n===0?a.initialPromise:void 0;try{T=E??a.fn()}catch(x){T=Promise.reject(x)}Promise.resolve(T).then(_).catch(x=>{var F;if(c())return;const P=a.retry??(ec.isServer()?0:3),N=a.retryDelay??Y1,R=typeof N=="function"?N(n,x):N,V=P===!0||typeof P=="number"&&n<P||typeof P=="function"&&P(n,x);if(t||!V){y(x);return}n++,(F=a.onFail)==null||F.call(a,n,x),G1(R).then(()=>m()?void 0:S()).then(()=>{t?y(x):b()})})};return{promise:l,status:()=>l.status,cancel:f,continue:()=>(s==null||s(),l),cancelRetry:d,continueRetry:p,canStart:g,start:()=>(g()?b():S().then(b),l)}}var fr,Wy,ox=(Wy=class{constructor(){te(this,fr)}destroy(){this.clearGcTimeout()}scheduleGc(){this.clearGcTimeout(),dp(this.gcTime)&&zt(this,fr,rr.setTimeout(()=>{this.optionalRemove()},this.gcTime))}updateGcTime(a){this.gcTime=Math.max(this.gcTime||0,a??(ec.isServer()?1/0:300*1e3))}clearGcTimeout(){X(this,fr)!==void 0&&(rr.clearTimeout(X(this,fr)),zt(this,fr,void 0))}},fr=new WeakMap,Wy);function Q1(a){return{onFetch:(t,n)=>{var g,_,y,S,b;const s=t.options,l=(y=(_=(g=t.fetchOptions)==null?void 0:g.meta)==null?void 0:_.fetchMore)==null?void 0:y.direction,c=((S=t.state.data)==null?void 0:S.pages)||[],f=((b=t.state.data)==null?void 0:b.pageParams)||[];let d={pages:[],pageParams:[]},p=0;const m=async()=>{let T=!1;const E=N=>{j1(N,()=>t.signal,()=>T=!0)},x=ix(t.options,t.fetchOptions),P=async(N,R,V)=>{if(T)return Promise.reject(t.signal.reason);if(R==null&&N.pages.length)return Promise.resolve(N);const z=(()=>{const H={client:t.client,queryKey:t.queryKey,pageParam:R,direction:V?"backward":"forward",meta:t.options.meta};return E(H),H})(),G=await x(z),{maxPages:U}=t.options,D=V?k1:V1;return{pages:D(N.pages,G,U),pageParams:D(N.pageParams,R,U)}};if(l&&c.length){const N=l==="backward",R=N?Z1:U0,V={pages:c,pageParams:f},F=R(s,V);d=await P(V,F,N)}else{const N=a??c.length;do{const R=p===0?f[0]??s.initialPageParam:U0(s,d);if(p>0&&R==null)break;d=await P(d,R),p++}while(p<N)}return d};t.options.persister?t.fetchFn=()=>{var T,E;return(E=(T=t.options).persister)==null?void 0:E.call(T,m,{client:t.client,queryKey:t.queryKey,meta:t.options.meta,signal:t.signal},n)}:t.fetchFn=m}}}function U0(a,{pages:t,pageParams:n}){const s=t.length-1;return t.length>0?a.getNextPageParam(t[s],t,n[s],n):void 0}function Z1(a,{pages:t,pageParams:n}){var s;return t.length>0?(s=a.getPreviousPageParam)==null?void 0:s.call(a,t[0],t,n[0],n):void 0}var Ao,dr,Co,Ri,hr,An,ac,pr,mi,lx,Aa,Yy,K1=(Yy=class extends ox{constructor(t){super();te(this,mi);te(this,Ao);te(this,dr);te(this,Co);te(this,Ri);te(this,hr);te(this,An);te(this,ac);te(this,pr);zt(this,pr,!1),zt(this,ac,t.defaultOptions),this.setOptions(t.options),this.observers=[],zt(this,hr,t.client),zt(this,Ri,X(this,hr).getQueryCache()),this.queryKey=t.queryKey,this.queryHash=t.queryHash,zt(this,dr,O0(this.options)),this.state=t.state??X(this,dr),this.scheduleGc()}get meta(){return this.options.meta}get queryType(){return X(this,Ao)}get promise(){var t;return(t=X(this,An))==null?void 0:t.promise}setOptions(t){if(this.options={...X(this,ac),...t},t!=null&&t._type&&zt(this,Ao,t._type),this.updateGcTime(this.options.gcTime),this.state&&this.state.data===void 0){const n=O0(this.options);n.data!==void 0&&(this.setState(L0(n.data,n.dataUpdatedAt)),zt(this,dr,n))}}optionalRemove(){!this.observers.length&&this.state.fetchStatus==="idle"&&X(this,Ri).remove(this)}setData(t,n){const s=mp(this.state.data,t,this.options);return Ae(this,mi,Aa).call(this,{data:s,type:"success",dataUpdatedAt:n==null?void 0:n.updatedAt,manual:n==null?void 0:n.manual}),s}setState(t){Ae(this,mi,Aa).call(this,{type:"setState",state:t})}cancel(t){var s,l;const n=(s=X(this,An))==null?void 0:s.promise;return(l=X(this,An))==null||l.cancel(t),n?n.then(ni).catch(ni):Promise.resolve()}destroy(){super.destroy(),this.cancel({silent:!0})}get resetState(){return X(this,dr)}reset(){this.destroy(),this.setState(this.resetState)}isActive(){return this.observers.some(t=>gi(t.options.enabled,this)!==!1)}isDisabled(){return this.getObserversCount()>0?!this.isActive():this.options.queryFn===ym||!this.isFetched()}isFetched(){return this.state.dataUpdateCount+this.state.errorUpdateCount>0}isStatic(){return this.getObserversCount()>0?this.observers.some(t=>Ts(t.options.staleTime,this)==="static"):!1}isStale(){return this.getObserversCount()>0?this.observers.some(t=>t.getCurrentResult().isStale):this.state.data===void 0||this.state.isInvalidated}isStaleByTime(t=0){return this.state.data===void 0?!0:t==="static"?!1:this.state.isInvalidated?!0:!ex(this.state.dataUpdatedAt,t)}onFocus(){var n;const t=this.observers.find(s=>s.shouldFetchOnWindowFocus());t==null||t.refetch({cancelRefetch:!1}),(n=X(this,An))==null||n.continue()}onOnline(){var n;const t=this.observers.find(s=>s.shouldFetchOnReconnect());t==null||t.refetch({cancelRefetch:!1}),(n=X(this,An))==null||n.continue()}addObserver(t){this.observers.includes(t)||(this.observers.push(t),this.clearGcTimeout(),X(this,Ri).notify({type:"observerAdded",query:this,observer:t}))}removeObserver(t){this.observers.includes(t)&&(this.observers=this.observers.filter(n=>n!==t),this.observers.length||(X(this,An)&&(X(this,pr)||Ae(this,mi,lx).call(this)?X(this,An).cancel({revert:!0}):X(this,An).cancelRetry()),this.scheduleGc()),X(this,Ri).notify({type:"observerRemoved",query:this,observer:t}))}getObserversCount(){return this.observers.length}invalidate(){this.state.isInvalidated||Ae(this,mi,Aa).call(this,{type:"invalidate"})}async fetch(t,n){var m,g,_,y,S,b,T,E,x,P,N;if(this.state.fetchStatus!=="idle"&&((m=X(this,An))==null?void 0:m.status())!=="rejected"){if(this.state.data!==void 0&&(n!=null&&n.cancelRefetch))this.cancel({silent:!0});else if(X(this,An))return X(this,An).continueRetry(),X(this,An).promise}if(t&&this.setOptions(t),!this.options.queryFn){const R=this.observers.find(V=>V.options.queryFn);R&&this.setOptions(R.options)}const s=new AbortController,l=R=>{Object.defineProperty(R,"signal",{enumerable:!0,get:()=>(zt(this,pr,!0),s.signal)})},c=()=>{const R=ix(this.options,n),F=(()=>{const z={client:X(this,hr),queryKey:this.queryKey,meta:this.meta};return l(z),z})();return zt(this,pr,!1),this.options.persister?this.options.persister(R,F,this):R(F)},d=(()=>{const R={fetchOptions:n,options:this.options,queryKey:this.queryKey,client:X(this,hr),state:this.state,fetchFn:c};return l(R),R})(),p=X(this,Ao)==="infinite"?Q1(this.options.pages):this.options.behavior;p==null||p.onFetch(d,this),zt(this,Co,this.state),(this.state.fetchStatus==="idle"||this.state.fetchMeta!==((g=d.fetchOptions)==null?void 0:g.meta))&&Ae(this,mi,Aa).call(this,{type:"fetch",meta:(_=d.fetchOptions)==null?void 0:_.meta}),zt(this,An,rx({initialPromise:n==null?void 0:n.initialPromise,fn:d.fetchFn,onCancel:R=>{R instanceof vp&&R.revert&&this.setState({...X(this,Co),fetchStatus:"idle"}),s.abort()},onFail:(R,V)=>{Ae(this,mi,Aa).call(this,{type:"failed",failureCount:R,error:V})},onPause:()=>{Ae(this,mi,Aa).call(this,{type:"pause"})},onContinue:()=>{Ae(this,mi,Aa).call(this,{type:"continue"})},retry:d.options.retry,retryDelay:d.options.retryDelay,networkMode:d.options.networkMode,canRun:()=>!0}));try{const R=await X(this,An).start();if(R===void 0)throw new Error(`${this.queryHash} data is undefined`);return this.setData(R),(S=(y=X(this,Ri).config).onSuccess)==null||S.call(y,R,this),(T=(b=X(this,Ri).config).onSettled)==null||T.call(b,R,this.state.error,this),R}catch(R){if(R instanceof vp){if(R.silent)return X(this,An).promise;if(R.revert){if(this.state.data===void 0)throw R;return this.state.data}}throw Ae(this,mi,Aa).call(this,{type:"error",error:R}),(x=(E=X(this,Ri).config).onError)==null||x.call(E,R,this),(N=(P=X(this,Ri).config).onSettled)==null||N.call(P,this.state.data,R,this),R}finally{this.scheduleGc()}}},Ao=new WeakMap,dr=new WeakMap,Co=new WeakMap,Ri=new WeakMap,hr=new WeakMap,An=new WeakMap,ac=new WeakMap,pr=new WeakMap,mi=new WeakSet,lx=function(){return this.state.fetchStatus==="paused"&&this.state.status==="pending"},Aa=function(t){const n=s=>{switch(t.type){case"failed":return{...s,fetchFailureCount:t.failureCount,fetchFailureReason:t.error};case"pause":return{...s,fetchStatus:"paused"};case"continue":return{...s,fetchStatus:"fetching"};case"fetch":return{...s,...cx(s.data,this.options),fetchMeta:t.meta??null};case"success":const l={...s,...L0(t.data,t.dataUpdatedAt),dataUpdateCount:s.dataUpdateCount+1,...!t.manual&&{fetchStatus:"idle",fetchFailureCount:0,fetchFailureReason:null}};return zt(this,Co,t.manual?l:void 0),l;case"error":const c=t.error;return{...s,error:c,errorUpdateCount:s.errorUpdateCount+1,errorUpdatedAt:Date.now(),fetchFailureCount:s.fetchFailureCount+1,fetchFailureReason:c,fetchStatus:"idle",status:"error",isInvalidated:!0};case"invalidate":return{...s,isInvalidated:!0};case"setState":return{...s,...t.state}}};this.state=n(this.state),On.batch(()=>{this.observers.forEach(s=>{s.onQueryUpdate()}),X(this,Ri).notify({query:this,type:"updated",action:t})})},Yy);function cx(a,t){return{fetchFailureCount:0,fetchFailureReason:null,fetchStatus:sx(t.networkMode)?"fetching":"paused",...a===void 0&&{error:null,status:"pending"}}}function L0(a,t){return{data:a,dataUpdatedAt:t??Date.now(),error:null,isInvalidated:!1,status:"success"}}function O0(a){const t=typeof a.initialData=="function"?a.initialData():a.initialData,n=t!==void 0,s=n?typeof a.initialDataUpdatedAt=="function"?a.initialDataUpdatedAt():a.initialDataUpdatedAt:0;return{data:t,dataUpdateCount:0,dataUpdatedAt:n?s??Date.now():0,error:null,errorUpdateCount:0,errorUpdatedAt:0,fetchFailureCount:0,fetchFailureReason:null,fetchMeta:null,isInvalidated:!1,status:n?"success":"pending",fetchStatus:"idle"}}var ei,Re,sc,qn,mr,Ro,Ra,xs,rc,wo,Do,gr,vr,Ss,No,ze,Wl,_p,yp,xp,Sp,Mp,Ep,bp,ux,Qy,J1=(Qy=class extends cc{constructor(t,n){super();te(this,ze);te(this,ei);te(this,Re);te(this,sc);te(this,qn);te(this,mr);te(this,Ro);te(this,Ra);te(this,xs);te(this,rc);te(this,wo);te(this,Do);te(this,gr);te(this,vr);te(this,Ss);te(this,No,new Set);this.options=n,zt(this,ei,t),zt(this,xs,null),zt(this,Ra,gp()),this.bindMethods(),this.setOptions(n)}bindMethods(){this.refetch=this.refetch.bind(this)}onSubscribe(){this.listeners.size===1&&(X(this,Re).addObserver(this),P0(X(this,Re),this.options)?Ae(this,ze,Wl).call(this):this.updateResult(),Ae(this,ze,Sp).call(this))}onUnsubscribe(){this.hasListeners()||this.destroy()}shouldFetchOnReconnect(){return Tp(X(this,Re),this.options,this.options.refetchOnReconnect)}shouldFetchOnWindowFocus(){return Tp(X(this,Re),this.options,this.options.refetchOnWindowFocus)}destroy(){this.listeners=new Set,Ae(this,ze,Mp).call(this),Ae(this,ze,Ep).call(this),X(this,Re).removeObserver(this)}setOptions(t){const n=this.options,s=X(this,Re);if(this.options=X(this,ei).defaultQueryOptions(t),this.options.enabled!==void 0&&typeof this.options.enabled!="boolean"&&typeof this.options.enabled!="function"&&typeof gi(this.options.enabled,X(this,Re))!="boolean")throw new Error("Expected enabled to be a boolean or a callback that returns a boolean");Ae(this,ze,bp).call(this),X(this,Re).setOptions(this.options),n._defaulted&&!hp(this.options,n)&&X(this,ei).getQueryCache().notify({type:"observerOptionsUpdated",query:X(this,Re),observer:this});const l=this.hasListeners();l&&z0(X(this,Re),s,this.options,n)&&Ae(this,ze,Wl).call(this),this.updateResult(),l&&(X(this,Re)!==s||gi(this.options.enabled,X(this,Re))!==gi(n.enabled,X(this,Re))||Ts(this.options.staleTime,X(this,Re))!==Ts(n.staleTime,X(this,Re)))&&Ae(this,ze,_p).call(this);const c=Ae(this,ze,yp).call(this);l&&(X(this,Re)!==s||gi(this.options.enabled,X(this,Re))!==gi(n.enabled,X(this,Re))||c!==X(this,Ss))&&Ae(this,ze,xp).call(this,c)}getOptimisticResult(t){const n=X(this,ei).getQueryCache().build(X(this,ei),t),s=this.createResult(n,t);return tE(this,s)&&(zt(this,qn,s),zt(this,Ro,this.options),zt(this,mr,X(this,Re).state)),s}getCurrentResult(){return X(this,qn)}trackResult(t,n){return new Proxy(t,{get:(s,l)=>(this.trackProp(l),n==null||n(l),l==="promise"&&(this.trackProp("data"),!this.options.experimental_prefetchInRender&&X(this,Ra).status==="pending"&&X(this,Ra).reject(new Error("experimental_prefetchInRender feature flag is not enabled"))),Reflect.get(s,l))})}trackProp(t){X(this,No).add(t)}getCurrentQuery(){return X(this,Re)}refetch({...t}={}){return this.fetch({...t})}fetchOptimistic(t){const n=X(this,ei).defaultQueryOptions(t),s=X(this,ei).getQueryCache().build(X(this,ei),n);return s.fetch().then(()=>this.createResult(s,n))}fetch(t){return Ae(this,ze,Wl).call(this,{...t,cancelRefetch:t.cancelRefetch??!0}).then(()=>(this.updateResult(),X(this,qn)))}createResult(t,n){var U;const s=X(this,Re),l=this.options,c=X(this,qn),f=X(this,mr),d=X(this,Ro),m=t!==s?t.state:X(this,sc),{state:g}=t;let _={...g},y=!1,S;if(n._optimisticResults){const D=this.hasListeners(),H=!D&&P0(t,n),ut=D&&z0(t,s,n,l);(H||ut)&&(_={..._,...cx(g.data,t.options)}),n._optimisticResults==="isRestoring"&&(_.fetchStatus="idle")}let{error:b,errorUpdatedAt:T,status:E}=_;S=_.data;let x=!1;if(n.placeholderData!==void 0&&S===void 0&&E==="pending"){let D;c!=null&&c.isPlaceholderData&&n.placeholderData===(d==null?void 0:d.placeholderData)?(D=c.data,x=!0):D=typeof n.placeholderData=="function"?n.placeholderData((U=X(this,Do))==null?void 0:U.state.data,X(this,Do)):n.placeholderData,D!==void 0&&(E="success",S=mp(c==null?void 0:c.data,D,n),y=!0)}if(n.select&&S!==void 0&&!x)if(c&&S===(f==null?void 0:f.data)&&n.select===X(this,rc))S=X(this,wo);else try{zt(this,rc,n.select),S=n.select(S),S=mp(c==null?void 0:c.data,S,n),zt(this,wo,S),zt(this,xs,null)}catch(D){zt(this,xs,D)}X(this,xs)&&(b=X(this,xs),S=X(this,wo),T=Date.now(),E="error");const P=_.fetchStatus==="fetching",N=E==="pending",R=E==="error",V=N&&P,F=S!==void 0,G={status:E,fetchStatus:_.fetchStatus,isPending:N,isSuccess:E==="success",isError:R,isInitialLoading:V,isLoading:V,data:S,dataUpdatedAt:_.dataUpdatedAt,error:b,errorUpdatedAt:T,failureCount:_.fetchFailureCount,failureReason:_.fetchFailureReason,errorUpdateCount:_.errorUpdateCount,isFetched:t.isFetched(),isFetchedAfterMount:_.dataUpdateCount>m.dataUpdateCount||_.errorUpdateCount>m.errorUpdateCount,isFetching:P,isRefetching:P&&!N,isLoadingError:R&&!F,isPaused:_.fetchStatus==="paused",isPlaceholderData:y,isRefetchError:R&&F,isStale:xm(t,n),refetch:this.refetch,promise:X(this,Ra),isEnabled:gi(n.enabled,t)!==!1};if(this.options.experimental_prefetchInRender){const D=G.data!==void 0,H=G.status==="error"&&!D,ut=ct=>{H?ct.reject(G.error):D&&ct.resolve(G.data)},ot=()=>{const ct=zt(this,Ra,G.promise=gp());ut(ct)},mt=X(this,Ra);switch(mt.status){case"pending":t.queryHash===s.queryHash&&ut(mt);break;case"fulfilled":(H||G.data!==mt.value)&&ot();break;case"rejected":(!H||G.error!==mt.reason)&&ot();break}}return G}updateResult(){const t=X(this,qn),n=this.createResult(X(this,Re),this.options);if(zt(this,mr,X(this,Re).state),zt(this,Ro,this.options),X(this,mr).data!==void 0&&zt(this,Do,X(this,Re)),hp(n,t))return;zt(this,qn,n);const s=()=>{if(!t)return!0;const{notifyOnChangeProps:l}=this.options,c=typeof l=="function"?l():l;if(c==="all"||!c&&!X(this,No).size)return!0;const f=new Set(c??X(this,No));return this.options.throwOnError&&f.add("error"),Object.keys(X(this,qn)).some(d=>{const p=d;return X(this,qn)[p]!==t[p]&&f.has(p)})};Ae(this,ze,ux).call(this,{listeners:s()})}onQueryUpdate(){this.updateResult(),this.hasListeners()&&Ae(this,ze,Sp).call(this)}},ei=new WeakMap,Re=new WeakMap,sc=new WeakMap,qn=new WeakMap,mr=new WeakMap,Ro=new WeakMap,Ra=new WeakMap,xs=new WeakMap,rc=new WeakMap,wo=new WeakMap,Do=new WeakMap,gr=new WeakMap,vr=new WeakMap,Ss=new WeakMap,No=new WeakMap,ze=new WeakSet,Wl=function(t){Ae(this,ze,bp).call(this);let n=X(this,Re).fetch(this.options,t);return t!=null&&t.throwOnError||(n=n.catch(ni)),n},_p=function(){Ae(this,ze,Mp).call(this);const t=Ts(this.options.staleTime,X(this,Re));if(ec.isServer()||X(this,qn).isStale||!dp(t))return;const s=ex(X(this,qn).dataUpdatedAt,t)+1;zt(this,gr,rr.setTimeout(()=>{X(this,qn).isStale||this.updateResult()},s))},yp=function(){return(typeof this.options.refetchInterval=="function"?this.options.refetchInterval(X(this,Re)):this.options.refetchInterval)??!1},xp=function(t){Ae(this,ze,Ep).call(this),zt(this,Ss,t),!(ec.isServer()||gi(this.options.enabled,X(this,Re))===!1||!dp(X(this,Ss))||X(this,Ss)===0)&&zt(this,vr,rr.setInterval(()=>{(this.options.refetchIntervalInBackground||vm.isFocused())&&Ae(this,ze,Wl).call(this)},X(this,Ss)))},Sp=function(){Ae(this,ze,_p).call(this),Ae(this,ze,xp).call(this,Ae(this,ze,yp).call(this))},Mp=function(){X(this,gr)!==void 0&&(rr.clearTimeout(X(this,gr)),zt(this,gr,void 0))},Ep=function(){X(this,vr)!==void 0&&(rr.clearInterval(X(this,vr)),zt(this,vr,void 0))},bp=function(){const t=X(this,ei).getQueryCache().build(X(this,ei),this.options);if(t===X(this,Re))return;const n=X(this,Re);zt(this,Re,t),zt(this,sc,t.state),this.hasListeners()&&(n==null||n.removeObserver(this),t.addObserver(this))},ux=function(t){On.batch(()=>{t.listeners&&this.listeners.forEach(n=>{n(X(this,qn))}),X(this,ei).getQueryCache().notify({query:X(this,Re),type:"observerResultsUpdated"})})},Qy);function $1(a,t){return gi(t.enabled,a)!==!1&&a.state.data===void 0&&!(a.state.status==="error"&&gi(t.retryOnMount,a)===!1)}function P0(a,t){return $1(a,t)||a.state.data!==void 0&&Tp(a,t,t.refetchOnMount)}function Tp(a,t,n){if(gi(t.enabled,a)!==!1&&Ts(t.staleTime,a)!=="static"){const s=typeof n=="function"?n(a):n;return s==="always"||s!==!1&&xm(a,t)}return!1}function z0(a,t,n,s){return(a!==t||gi(s.enabled,a)===!1)&&(!n.suspense||a.state.status!=="error")&&xm(a,n)}function xm(a,t){return gi(t.enabled,a)!==!1&&a.isStaleByTime(Ts(t.staleTime,a))}function tE(a,t){return!hp(a.getCurrentResult(),t)}var oc,Zi,Hn,_r,Ki,ms,Zy,eE=(Zy=class extends ox{constructor(t){super();te(this,Ki);te(this,oc);te(this,Zi);te(this,Hn);te(this,_r);zt(this,oc,t.client),this.mutationId=t.mutationId,zt(this,Hn,t.mutationCache),zt(this,Zi,[]),this.state=t.state||nE(),this.setOptions(t.options),this.scheduleGc()}setOptions(t){this.options=t,this.updateGcTime(this.options.gcTime)}get meta(){return this.options.meta}addObserver(t){X(this,Zi).includes(t)||(X(this,Zi).push(t),this.clearGcTimeout(),X(this,Hn).notify({type:"observerAdded",mutation:this,observer:t}))}removeObserver(t){zt(this,Zi,X(this,Zi).filter(n=>n!==t)),this.scheduleGc(),X(this,Hn).notify({type:"observerRemoved",mutation:this,observer:t})}optionalRemove(){X(this,Zi).length||(this.state.status==="pending"?this.scheduleGc():X(this,Hn).remove(this))}continue(){var t;return((t=X(this,_r))==null?void 0:t.continue())??this.execute(this.state.variables)}async execute(t){var f,d,p,m,g,_,y,S,b,T,E,x,P,N,R,V,F,z;const n=()=>{Ae(this,Ki,ms).call(this,{type:"continue"})},s={client:X(this,oc),meta:this.options.meta,mutationKey:this.options.mutationKey};zt(this,_r,rx({fn:()=>this.options.mutationFn?this.options.mutationFn(t,s):Promise.reject(new Error("No mutationFn found")),onFail:(G,U)=>{Ae(this,Ki,ms).call(this,{type:"failed",failureCount:G,error:U})},onPause:()=>{Ae(this,Ki,ms).call(this,{type:"pause"})},onContinue:n,retry:this.options.retry??0,retryDelay:this.options.retryDelay,networkMode:this.options.networkMode,canRun:()=>X(this,Hn).canRun(this)}));const l=this.state.status==="pending",c=!X(this,_r).canStart();try{if(l)n();else{Ae(this,Ki,ms).call(this,{type:"pending",variables:t,isPaused:c}),X(this,Hn).config.onMutate&&await X(this,Hn).config.onMutate(t,this,s);const U=await((d=(f=this.options).onMutate)==null?void 0:d.call(f,t,s));U!==this.state.context&&Ae(this,Ki,ms).call(this,{type:"pending",context:U,variables:t,isPaused:c})}const G=await X(this,_r).start();return await((m=(p=X(this,Hn).config).onSuccess)==null?void 0:m.call(p,G,t,this.state.context,this,s)),await((_=(g=this.options).onSuccess)==null?void 0:_.call(g,G,t,this.state.context,s)),await((S=(y=X(this,Hn).config).onSettled)==null?void 0:S.call(y,G,null,this.state.variables,this.state.context,this,s)),await((T=(b=this.options).onSettled)==null?void 0:T.call(b,G,null,t,this.state.context,s)),Ae(this,Ki,ms).call(this,{type:"success",data:G}),G}catch(G){try{await((x=(E=X(this,Hn).config).onError)==null?void 0:x.call(E,G,t,this.state.context,this,s))}catch(U){Promise.reject(U)}try{await((N=(P=this.options).onError)==null?void 0:N.call(P,G,t,this.state.context,s))}catch(U){Promise.reject(U)}try{await((V=(R=X(this,Hn).config).onSettled)==null?void 0:V.call(R,void 0,G,this.state.variables,this.state.context,this,s))}catch(U){Promise.reject(U)}try{await((z=(F=this.options).onSettled)==null?void 0:z.call(F,void 0,G,t,this.state.context,s))}catch(U){Promise.reject(U)}throw Ae(this,Ki,ms).call(this,{type:"error",error:G}),G}finally{X(this,Hn).runNext(this)}}},oc=new WeakMap,Zi=new WeakMap,Hn=new WeakMap,_r=new WeakMap,Ki=new WeakSet,ms=function(t){const n=s=>{switch(t.type){case"failed":return{...s,failureCount:t.failureCount,failureReason:t.error};case"pause":return{...s,isPaused:!0};case"continue":return{...s,isPaused:!1};case"pending":return{...s,context:t.context,data:void 0,failureCount:0,failureReason:null,error:null,isPaused:t.isPaused,status:"pending",variables:t.variables,submittedAt:Date.now()};case"success":return{...s,data:t.data,failureCount:0,failureReason:null,error:null,status:"success",isPaused:!1};case"error":return{...s,data:void 0,error:t.error,failureCount:s.failureCount+1,failureReason:t.error,isPaused:!1,status:"error"}}};this.state=n(this.state),On.batch(()=>{X(this,Zi).forEach(s=>{s.onMutationUpdate(t)}),X(this,Hn).notify({mutation:this,type:"updated",action:t})})},Zy);function nE(){return{context:void 0,data:void 0,error:null,failureCount:0,failureReason:null,isPaused:!1,status:"idle",variables:void 0,submittedAt:0}}var wa,Ii,lc,Ky,iE=(Ky=class extends cc{constructor(t={}){super();te(this,wa);te(this,Ii);te(this,lc);this.config=t,zt(this,wa,new Set),zt(this,Ii,new Map),zt(this,lc,0)}build(t,n,s){const l=new eE({client:t,mutationCache:this,mutationId:++bu(this,lc)._,options:t.defaultMutationOptions(n),state:s});return this.add(l),l}add(t){X(this,wa).add(t);const n=Tu(t);if(typeof n=="string"){const s=X(this,Ii).get(n);s?s.push(t):X(this,Ii).set(n,[t])}this.notify({type:"added",mutation:t})}remove(t){if(X(this,wa).delete(t)){const n=Tu(t);if(typeof n=="string"){const s=X(this,Ii).get(n);if(s)if(s.length>1){const l=s.indexOf(t);l!==-1&&s.splice(l,1)}else s[0]===t&&X(this,Ii).delete(n)}}this.notify({type:"removed",mutation:t})}canRun(t){const n=Tu(t);if(typeof n=="string"){const s=X(this,Ii).get(n),l=s==null?void 0:s.find(c=>c.state.status==="pending");return!l||l===t}else return!0}runNext(t){var s;const n=Tu(t);if(typeof n=="string"){const l=(s=X(this,Ii).get(n))==null?void 0:s.find(c=>c!==t&&c.state.isPaused);return(l==null?void 0:l.continue())??Promise.resolve()}else return Promise.resolve()}clear(){On.batch(()=>{X(this,wa).forEach(t=>{this.notify({type:"removed",mutation:t})}),X(this,wa).clear(),X(this,Ii).clear()})}getAll(){return Array.from(X(this,wa))}find(t){const n={exact:!0,...t};return this.getAll().find(s=>w0(n,s))}findAll(t={}){return this.getAll().filter(n=>w0(t,n))}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}resumePausedMutations(){const t=this.getAll().filter(n=>n.state.isPaused);return On.batch(()=>Promise.all(t.map(n=>n.continue().catch(ni))))}},wa=new WeakMap,Ii=new WeakMap,lc=new WeakMap,Ky);function Tu(a){var t;return(t=a.options.scope)==null?void 0:t.id}var Ji,Jy,aE=(Jy=class extends cc{constructor(t={}){super();te(this,Ji);this.config=t,zt(this,Ji,new Map)}build(t,n,s){const l=n.queryKey,c=n.queryHash??_m(l,n);let f=this.get(c);return f||(f=new K1({client:t,queryKey:l,queryHash:c,options:t.defaultQueryOptions(n),state:s,defaultOptions:t.getQueryDefaults(l)}),this.add(f)),f}add(t){X(this,Ji).has(t.queryHash)||(X(this,Ji).set(t.queryHash,t),this.notify({type:"added",query:t}))}remove(t){const n=X(this,Ji).get(t.queryHash);n&&(t.destroy(),n===t&&X(this,Ji).delete(t.queryHash),this.notify({type:"removed",query:t}))}clear(){On.batch(()=>{this.getAll().forEach(t=>{this.remove(t)})})}get(t){return X(this,Ji).get(t)}getAll(){return[...X(this,Ji).values()]}find(t){const n={exact:!0,...t};return this.getAll().find(s=>R0(n,s))}findAll(t={}){const n=this.getAll();return Object.keys(t).length>0?n.filter(s=>R0(t,s)):n}notify(t){On.batch(()=>{this.listeners.forEach(n=>{n(t)})})}onFocus(){On.batch(()=>{this.getAll().forEach(t=>{t.onFocus()})})}onOnline(){On.batch(()=>{this.getAll().forEach(t=>{t.onOnline()})})}},Ji=new WeakMap,Jy),ln,Ms,Es,Uo,Lo,bs,Oo,Po,$y,sE=($y=class{constructor(a={}){te(this,ln);te(this,Ms);te(this,Es);te(this,Uo);te(this,Lo);te(this,bs);te(this,Oo);te(this,Po);zt(this,ln,a.queryCache||new aE),zt(this,Ms,a.mutationCache||new iE),zt(this,Es,a.defaultOptions||{}),zt(this,Uo,new Map),zt(this,Lo,new Map),zt(this,bs,0)}mount(){bu(this,bs)._++,X(this,bs)===1&&(zt(this,Oo,vm.subscribe(async a=>{a&&(await this.resumePausedMutations(),X(this,ln).onFocus())})),zt(this,Po,sf.subscribe(async a=>{a&&(await this.resumePausedMutations(),X(this,ln).onOnline())})))}unmount(){var a,t;bu(this,bs)._--,X(this,bs)===0&&((a=X(this,Oo))==null||a.call(this),zt(this,Oo,void 0),(t=X(this,Po))==null||t.call(this),zt(this,Po,void 0))}isFetching(a){return X(this,ln).findAll({...a,fetchStatus:"fetching"}).length}isMutating(a){return X(this,Ms).findAll({...a,status:"pending"}).length}getQueryData(a){var n;const t=this.defaultQueryOptions({queryKey:a});return(n=X(this,ln).get(t.queryHash))==null?void 0:n.state.data}ensureQueryData(a){const t=this.defaultQueryOptions(a),n=X(this,ln).build(this,t),s=n.state.data;return s===void 0?this.fetchQuery(a):(a.revalidateIfStale&&n.isStaleByTime(Ts(t.staleTime,n))&&this.prefetchQuery(t),Promise.resolve(s))}getQueriesData(a){return X(this,ln).findAll(a).map(({queryKey:t,state:n})=>{const s=n.data;return[t,s]})}setQueryData(a,t,n){const s=this.defaultQueryOptions({queryKey:a}),l=X(this,ln).get(s.queryHash),c=l==null?void 0:l.state.data,f=F1(t,c);if(f!==void 0)return X(this,ln).build(this,s).setData(f,{...n,manual:!0})}setQueriesData(a,t,n){return On.batch(()=>X(this,ln).findAll(a).map(({queryKey:s})=>[s,this.setQueryData(s,t,n)]))}getQueryState(a){var n;const t=this.defaultQueryOptions({queryKey:a});return(n=X(this,ln).get(t.queryHash))==null?void 0:n.state}removeQueries(a){const t=X(this,ln);On.batch(()=>{t.findAll(a).forEach(n=>{t.remove(n)})})}resetQueries(a,t){const n=X(this,ln);return On.batch(()=>(n.findAll(a).forEach(s=>{s.reset()}),this.refetchQueries({type:"active",...a},t)))}cancelQueries(a,t={}){const n={revert:!0,...t},s=On.batch(()=>X(this,ln).findAll(a).map(l=>l.cancel(n)));return Promise.all(s).then(ni).catch(ni)}invalidateQueries(a,t={}){return On.batch(()=>(X(this,ln).findAll(a).forEach(n=>{n.invalidate()}),(a==null?void 0:a.refetchType)==="none"?Promise.resolve():this.refetchQueries({...a,type:(a==null?void 0:a.refetchType)??(a==null?void 0:a.type)??"active"},t)))}refetchQueries(a,t={}){const n={...t,cancelRefetch:t.cancelRefetch??!0},s=On.batch(()=>X(this,ln).findAll(a).filter(l=>!l.isDisabled()&&!l.isStatic()).map(l=>{let c=l.fetch(void 0,n);return n.throwOnError||(c=c.catch(ni)),l.state.fetchStatus==="paused"?Promise.resolve():c}));return Promise.all(s).then(ni)}fetchQuery(a){const t=this.defaultQueryOptions(a);t.retry===void 0&&(t.retry=!1);const n=X(this,ln).build(this,t);return n.isStaleByTime(Ts(t.staleTime,n))?n.fetch(t):Promise.resolve(n.state.data)}prefetchQuery(a){return this.fetchQuery(a).then(ni).catch(ni)}fetchInfiniteQuery(a){return a._type="infinite",this.fetchQuery(a)}prefetchInfiniteQuery(a){return this.fetchInfiniteQuery(a).then(ni).catch(ni)}ensureInfiniteQueryData(a){return a._type="infinite",this.ensureQueryData(a)}resumePausedMutations(){return sf.isOnline()?X(this,Ms).resumePausedMutations():Promise.resolve()}getQueryCache(){return X(this,ln)}getMutationCache(){return X(this,Ms)}getDefaultOptions(){return X(this,Es)}setDefaultOptions(a){zt(this,Es,a)}setQueryDefaults(a,t){X(this,Uo).set($l(a),{queryKey:a,defaultOptions:t})}getQueryDefaults(a){const t=[...X(this,Uo).values()],n={};return t.forEach(s=>{tc(a,s.queryKey)&&Object.assign(n,s.defaultOptions)}),n}setMutationDefaults(a,t){X(this,Lo).set($l(a),{mutationKey:a,defaultOptions:t})}getMutationDefaults(a){const t=[...X(this,Lo).values()],n={};return t.forEach(s=>{tc(a,s.mutationKey)&&Object.assign(n,s.defaultOptions)}),n}defaultQueryOptions(a){if(a._defaulted)return a;const t={...X(this,Es).queries,...this.getQueryDefaults(a.queryKey),...a,_defaulted:!0};return t.queryHash||(t.queryHash=_m(t.queryKey,t)),t.refetchOnReconnect===void 0&&(t.refetchOnReconnect=t.networkMode!=="always"),t.throwOnError===void 0&&(t.throwOnError=!!t.suspense),!t.networkMode&&t.persister&&(t.networkMode="offlineFirst"),t.queryFn===ym&&(t.enabled=!1),t}defaultMutationOptions(a){return a!=null&&a._defaulted?a:{...X(this,Es).mutations,...(a==null?void 0:a.mutationKey)&&this.getMutationDefaults(a.mutationKey),...a,_defaulted:!0}}clear(){X(this,ln).clear(),X(this,Ms).clear()}},ln=new WeakMap,Ms=new WeakMap,Es=new WeakMap,Uo=new WeakMap,Lo=new WeakMap,bs=new WeakMap,Oo=new WeakMap,Po=new WeakMap,$y),fx=se.createContext(void 0),dx=a=>{const t=se.useContext(fx);if(!t)throw new Error("No QueryClient set, use QueryClientProvider to set one");return t},rE=({client:a,children:t})=>(se.useEffect(()=>(a.mount(),()=>{a.unmount()}),[a]),v.jsx(fx.Provider,{value:a,children:t})),hx=se.createContext(!1),oE=()=>se.useContext(hx);hx.Provider;function lE(){let a=!1;return{clearReset:()=>{a=!1},reset:()=>{a=!0},isReset:()=>a}}var cE=se.createContext(lE()),uE=()=>se.useContext(cE),fE=(a,t,n)=>{const s=n!=null&&n.state.error&&typeof a.throwOnError=="function"?ax(a.throwOnError,[n.state.error,n]):a.throwOnError;(a.suspense||a.experimental_prefetchInRender||s)&&(t.isReset()||(a.retryOnMount=!1))},dE=a=>{se.useEffect(()=>{a.clearReset()},[a])},hE=({result:a,errorResetBoundary:t,throwOnError:n,query:s,suspense:l})=>a.isError&&!t.isReset()&&!a.isFetching&&s&&(l&&a.data===void 0||ax(n,[a.error,s])),pE=a=>{if(a.suspense){const n=l=>l==="static"?l:Math.max(l??1e3,1e3),s=a.staleTime;a.staleTime=typeof s=="function"?(...l)=>n(s(...l)):n(s),typeof a.gcTime=="number"&&(a.gcTime=Math.max(a.gcTime,1e3))}},mE=(a,t)=>a.isLoading&&a.isFetching&&!t,gE=(a,t)=>(a==null?void 0:a.suspense)&&t.isPending,I0=(a,t,n)=>t.fetchOptimistic(a).catch(()=>{n.clearReset()});function vE(a,t,n){var S,b,T,E;const s=oE(),l=uE(),c=dx(),f=c.defaultQueryOptions(a);(b=(S=c.getDefaultOptions().queries)==null?void 0:S._experimental_beforeQuery)==null||b.call(S,f);const d=c.getQueryCache().get(f.queryHash),p=a.subscribed!==!1;f._optimisticResults=s?"isRestoring":p?"optimistic":void 0,pE(f),fE(f,l,d),dE(l);const m=!c.getQueryCache().get(f.queryHash),[g]=se.useState(()=>new t(c,f)),_=g.getOptimisticResult(f),y=!s&&p;if(se.useSyncExternalStore(se.useCallback(x=>{const P=y?g.subscribe(On.batchCalls(x)):ni;return g.updateResult(),P},[g,y]),()=>g.getCurrentResult(),()=>g.getCurrentResult()),se.useEffect(()=>{g.setOptions(f)},[f,g]),gE(f,_))throw I0(f,g,l);if(hE({result:_,errorResetBoundary:l,throwOnError:f.throwOnError,query:d,suspense:f.suspense}))throw _.error;if((E=(T=c.getDefaultOptions().queries)==null?void 0:T._experimental_afterQuery)==null||E.call(T,f,_),f.experimental_prefetchInRender&&!ec.isServer()&&mE(_,s)){const x=m?I0(f,g,l):d==null?void 0:d.promise;x==null||x.catch(ni).finally(()=>{g.updateResult()})}return f.notifyOnChangeProps?_:g.trackResult(_)}function _E(a,t){return vE(a,J1)}/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yE=a=>a.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),px=(...a)=>a.filter((t,n,s)=>!!t&&t.trim()!==""&&s.indexOf(t)===n).join(" ").trim();/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var xE={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const SE=se.forwardRef(({color:a="currentColor",size:t=24,strokeWidth:n=2,absoluteStrokeWidth:s,className:l="",children:c,iconNode:f,...d},p)=>se.createElement("svg",{ref:p,...xE,width:t,height:t,stroke:a,strokeWidth:s?Number(n)*24/Number(t):n,className:px("lucide",l),...d},[...f.map(([m,g])=>se.createElement(m,g)),...Array.isArray(c)?c:[c]]));/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Ie=(a,t)=>{const n=se.forwardRef(({className:s,...l},c)=>se.createElement(SE,{ref:c,iconNode:t,className:px(`lucide-${yE(a)}`,s),...l}));return n.displayName=`${a}`,n};/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const mx=Ie("Activity",[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ME=Ie("Archive",[["rect",{width:"20",height:"5",x:"2",y:"3",rx:"1",key:"1wp1u1"}],["path",{d:"M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8",key:"1s80jp"}],["path",{d:"M10 12h4",key:"a56b0p"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sm=Ie("Bell",[["path",{d:"M10.268 21a2 2 0 0 0 3.464 0",key:"vwvbt9"}],["path",{d:"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",key:"11g9vi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const gx=Ie("BrainCircuit",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M9 13a4.5 4.5 0 0 0 3-4",key:"10igwf"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M12 13h4",key:"1ku699"}],["path",{d:"M12 18h6a2 2 0 0 1 2 2v1",key:"105ag5"}],["path",{d:"M12 8h8",key:"1lhi5i"}],["path",{d:"M16 8V5a2 2 0 0 1 2-2",key:"u6izg6"}],["circle",{cx:"16",cy:"13",r:".5",key:"ry7gng"}],["circle",{cx:"18",cy:"3",r:".5",key:"1aiba7"}],["circle",{cx:"20",cy:"21",r:".5",key:"yhc1fs"}],["circle",{cx:"20",cy:"8",r:".5",key:"1e43v0"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const EE=Ie("Brain",[["path",{d:"M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z",key:"l5xja"}],["path",{d:"M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z",key:"ep3f8r"}],["path",{d:"M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4",key:"1p4c4q"}],["path",{d:"M17.599 6.5a3 3 0 0 0 .399-1.375",key:"tmeiqw"}],["path",{d:"M6.003 5.125A3 3 0 0 0 6.401 6.5",key:"105sqy"}],["path",{d:"M3.477 10.896a4 4 0 0 1 .585-.396",key:"ql3yin"}],["path",{d:"M19.938 10.5a4 4 0 0 1 .585.396",key:"1qfode"}],["path",{d:"M6 18a4 4 0 0 1-1.967-.516",key:"2e4loj"}],["path",{d:"M19.967 17.484A4 4 0 0 1 18 18",key:"159ez6"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const bE=Ie("Check",[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const TE=Ie("CircleCheck",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const AE=Ie("CircleOff",[["path",{d:"m2 2 20 20",key:"1ooewy"}],["path",{d:"M8.35 2.69A10 10 0 0 1 21.3 15.65",key:"1pfsoa"}],["path",{d:"M19.08 19.08A10 10 0 1 1 4.92 4.92",key:"1ablyi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const CE=Ie("CirclePause",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"10",x2:"10",y1:"15",y2:"9",key:"c1nkhi"}],["line",{x1:"14",x2:"14",y1:"15",y2:"9",key:"h65svq"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const RE=Ie("ClipboardList",[["rect",{width:"8",height:"4",x:"8",y:"2",rx:"1",ry:"1",key:"tgr4d6"}],["path",{d:"M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2",key:"116196"}],["path",{d:"M12 11h4",key:"1jrz19"}],["path",{d:"M12 16h4",key:"n85exb"}],["path",{d:"M8 11h.01",key:"1dfujw"}],["path",{d:"M8 16h.01",key:"18s6g9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const wE=Ie("Clock",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["polyline",{points:"12 6 12 12 16 14",key:"68esgv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const DE=Ie("CodeXml",[["path",{d:"m18 16 4-4-4-4",key:"1inbqp"}],["path",{d:"m6 8-4 4 4 4",key:"15zrgr"}],["path",{d:"m14.5 4-5 16",key:"e7oirm"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const NE=Ie("Cpu",[["rect",{width:"16",height:"16",x:"4",y:"4",rx:"2",key:"14l7u7"}],["rect",{width:"6",height:"6",x:"9",y:"9",rx:"1",key:"5aljv4"}],["path",{d:"M15 2v2",key:"13l42r"}],["path",{d:"M15 20v2",key:"15mkzm"}],["path",{d:"M2 15h2",key:"1gxd5l"}],["path",{d:"M2 9h2",key:"1bbxkp"}],["path",{d:"M20 15h2",key:"19e6y8"}],["path",{d:"M20 9h2",key:"19tzq7"}],["path",{d:"M9 2v2",key:"165o2o"}],["path",{d:"M9 20v2",key:"i2bqo8"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const UE=Ie("DatabaseBackup",[["ellipse",{cx:"12",cy:"5",rx:"9",ry:"3",key:"msslwz"}],["path",{d:"M3 12a9 3 0 0 0 5 2.69",key:"1ui2ym"}],["path",{d:"M21 9.3V5",key:"6k6cib"}],["path",{d:"M3 5v14a9 3 0 0 0 6.47 2.88",key:"i62tjy"}],["path",{d:"M12 12v4h4",key:"1bxaet"}],["path",{d:"M13 20a5 5 0 0 0 9-3 4.5 4.5 0 0 0-4.5-4.5c-1.33 0-2.54.54-3.41 1.41L12 16",key:"1f4ei9"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const LE=Ie("Eye",[["path",{d:"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",key:"1nclc0"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const OE=Ie("House",[["path",{d:"M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8",key:"5wwlr5"}],["path",{d:"M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"1d0kgt"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const PE=Ie("KeyRound",[["path",{d:"M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",key:"1s6t7t"}],["circle",{cx:"16.5",cy:"7.5",r:".5",fill:"currentColor",key:"w0ekpg"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const zE=Ie("Lock",[["rect",{width:"18",height:"11",x:"3",y:"11",rx:"2",ry:"2",key:"1w4ew1"}],["path",{d:"M7 11V7a5 5 0 0 1 10 0v4",key:"fwvmzm"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const vx=Ie("MessageSquare",[["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",key:"1lielz"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _x=Ie("MonitorCog",[["path",{d:"M12 17v4",key:"1riwvh"}],["path",{d:"m15.2 4.9-.9-.4",key:"12wd2u"}],["path",{d:"m15.2 7.1-.9.4",key:"1r2vl7"}],["path",{d:"m16.9 3.2-.4-.9",key:"3zbo91"}],["path",{d:"m16.9 8.8-.4.9",key:"1qr2dn"}],["path",{d:"m19.5 2.3-.4.9",key:"1rjrkq"}],["path",{d:"m19.5 9.7-.4-.9",key:"heryx5"}],["path",{d:"m21.7 4.5-.9.4",key:"17fqt1"}],["path",{d:"m21.7 7.5-.9-.4",key:"14zyni"}],["path",{d:"M22 13v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7",key:"1tnzv8"}],["path",{d:"M8 21h8",key:"1ev6f3"}],["circle",{cx:"18",cy:"6",r:"3",key:"1h7g24"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const IE=Ie("Send",[["path",{d:"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",key:"1ffxy3"}],["path",{d:"m21.854 2.147-10.94 10.939",key:"12cjpa"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const BE=Ie("ServerCog",[["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}],["path",{d:"M4.5 10H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-.5",key:"tn8das"}],["path",{d:"M4.5 14H4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2h-.5",key:"1g2pve"}],["path",{d:"M6 6h.01",key:"1utrut"}],["path",{d:"M6 18h.01",key:"uhywen"}],["path",{d:"m15.7 13.4-.9-.3",key:"1jwmzr"}],["path",{d:"m9.2 10.9-.9-.3",key:"qapnim"}],["path",{d:"m10.6 15.7.3-.9",key:"quwk0k"}],["path",{d:"m13.6 15.7-.4-1",key:"cb9xp7"}],["path",{d:"m10.8 9.3-.4-1",key:"1uaiz5"}],["path",{d:"m8.3 13.6 1-.4",key:"s6srou"}],["path",{d:"m14.7 10.8 1-.4",key:"4d31cq"}],["path",{d:"m13.4 8.3-.3.9",key:"1bm987"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const FE=Ie("Server",[["rect",{width:"20",height:"8",x:"2",y:"2",rx:"2",ry:"2",key:"ngkwjq"}],["rect",{width:"20",height:"8",x:"2",y:"14",rx:"2",ry:"2",key:"iecqi9"}],["line",{x1:"6",x2:"6.01",y1:"6",y2:"6",key:"16zg32"}],["line",{x1:"6",x2:"6.01",y1:"18",y2:"18",key:"nzw8ys"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const HE=Ie("Settings",[["path",{d:"M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",key:"1qme2f"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const yx=Ie("ShieldAlert",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"M12 8v4",key:"1got3b"}],["path",{d:"M12 16h.01",key:"1drbdi"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xx=Ie("ShieldCheck",[["path",{d:"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",key:"oel41y"}],["path",{d:"m9 12 2 2 4-4",key:"dzmm74"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const B0=Ie("SlidersHorizontal",[["line",{x1:"21",x2:"14",y1:"4",y2:"4",key:"obuewd"}],["line",{x1:"10",x2:"3",y1:"4",y2:"4",key:"1q6298"}],["line",{x1:"21",x2:"12",y1:"12",y2:"12",key:"1iu8h1"}],["line",{x1:"8",x2:"3",y1:"12",y2:"12",key:"ntss68"}],["line",{x1:"21",x2:"16",y1:"20",y2:"20",key:"14d8ph"}],["line",{x1:"12",x2:"3",y1:"20",y2:"20",key:"m0wm8r"}],["line",{x1:"14",x2:"14",y1:"2",y2:"6",key:"14e1ph"}],["line",{x1:"8",x2:"8",y1:"10",y2:"14",key:"1i6ji0"}],["line",{x1:"16",x2:"16",y1:"18",y2:"22",key:"1lctlv"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Sx=Ie("TriangleAlert",[["path",{d:"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",key:"wmoenq"}],["path",{d:"M12 9v4",key:"juzpu7"}],["path",{d:"M12 17h.01",key:"p32p05"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const GE=Ie("WifiOff",[["path",{d:"M12 20h.01",key:"zekei9"}],["path",{d:"M8.5 16.429a5 5 0 0 1 7 0",key:"1bycff"}],["path",{d:"M5 12.859a10 10 0 0 1 5.17-2.69",key:"1dl1wf"}],["path",{d:"M19 12.859a10 10 0 0 0-2.007-1.523",key:"4k23kn"}],["path",{d:"M2 8.82a15 15 0 0 1 4.177-2.643",key:"1grhjp"}],["path",{d:"M22 8.82a15 15 0 0 0-11.288-3.764",key:"z3jwby"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Mx=Ie("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]);async function VE(a="dashboard"){const t=a==="display"?`/display/overview${Ex()}`:"/api/ui/overview",n=await fetch(t,{credentials:"include"});if(!n.ok)throw new Error(`Overview request failed: ${n.status}`);return n.json()}function Ex(){if(typeof window>"u")return"";const a=new URLSearchParams(window.location.search).get("display_token");return a?`?display_token=${encodeURIComponent(a)}`:""}async function kE(a){const t=await fetch("/api/chat/send",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:a})});if(!t.ok)throw new Error(`Chat request failed: ${t.status}`);return t.json()}async function jE(a,t){const s=await fetch(`/api/approvals/${a}/${t==="approve"?"approve":"reject"}`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify({})});if(!s.ok)throw new Error(`Approval ${t} failed: ${s.status}`)}async function bx(){const a=await fetch("/auth/me",{credentials:"include"});if(!a.ok)throw new Error(`Auth session request failed: ${a.status}`);return a.json()}async function Uh(){const a=await fetch("/api/settings",{credentials:"include"});if(!a.ok)throw new Error(`Settings request failed: ${a.status}`);return a.json()}async function XE(a,t,n){const s=String((await bx()).csrf_token||""),l=await fetch("/api/settings",{method:"POST",credentials:"include",headers:{"Content-Type":"application/json","X-CSRF-Token":s},body:JSON.stringify({section:a,key:t,value:n})}),c=await l.json().catch(()=>({}));if(!l.ok){const f=String(c.error||(Array.isArray(c.errors)?c.errors.join(", "):"")||l.status);throw new Error(f)}return c}async function qE(){const a=String((await bx()).csrf_token||""),t=await fetch("/api/settings/reset",{method:"POST",credentials:"include",headers:{"X-CSRF-Token":a}}),n=await t.json().catch(()=>({}));if(!t.ok)throw new Error(String(n.error||t.status));return n}const F0={};function Tx(a,t=!0,n="dashboard"){se.useEffect(()=>{if(!t||typeof EventSource>"u")return;const s=Ex(),l=F0[n]||WE(n),c=l?`last_event_id=${encodeURIComponent(l)}`:"",f=[n==="display"?"surface=display":"",s?s.slice(1):"",c].filter(Boolean).join("&"),d=n==="display"?`/api/ui/stream${f?`?${f}`:""}`:`/api/ui/stream${f?`?${f}`:""}`,p=new EventSource(d,{withCredentials:!0}),m=g=>{try{const _=JSON.parse(g.data),y=g.lastEventId||_.event_id||"";y&&(F0[n]=y,YE(n,y)),a(_)}catch{}};for(const g of["status.changed","task.updated","tool.execution.started","tool.execution.completed","tool.execution.failed","approval.created","approval.resolved","notification.created","chat.updated","permission.changed","connection.changed","activity.updated"])p.addEventListener(g,m);return p.addEventListener("ui.snapshot",m),()=>p.close()},[t,a,n])}function WE(a){try{return window.sessionStorage.getItem(Ax(a))||""}catch{return""}}function YE(a,t){try{window.sessionStorage.setItem(Ax(a),t)}catch{}}function Ax(a){return`aegis.ui.lastEventId.${a}`}function QE({open:a,onClose:t}){const[n,s]=se.useState(""),[l,c]=se.useState([]),[f,d]=se.useState(!1);async function p(m){m.preventDefault();const g=n.trim();if(!(!g||f)){s(""),c(_=>[..._,{role:"user",text:g}]),d(!0);try{const _=await kE(g);c(y=>[...y,{role:"aegis",text:String(_.response||_.message||"Done.")}])}catch(_){c(y=>[...y,{role:"system",text:_ instanceof Error?_.message:String(_)}])}finally{d(!1)}}}return v.jsxs("aside",{className:"chat-drawer","data-open":a,"aria-hidden":!a,children:[v.jsxs("div",{className:"panel__header",style:{padding:"16px",borderBottom:"1px solid var(--aegis-border)",margin:0},children:[v.jsxs("h2",{children:[v.jsx(vx,{size:18,"aria-hidden":"true"})," Chat"]}),v.jsx("button",{className:"icon-button",onClick:t,title:"Close chat",children:v.jsx(Mx,{size:16,"aria-hidden":"true"})})]}),v.jsxs("div",{className:"chat-log",children:[l.length===0?v.jsx("div",{className:"muted",children:"Chat is ready. Messages are sent through the existing AEGIS chat API."}):null,l.map((m,g)=>v.jsx("div",{className:"list-row",style:{marginBottom:8},children:v.jsxs("div",{children:[v.jsx("strong",{children:m.role}),v.jsx("div",{children:m.text})]})},`${m.role}-${g}`))]}),v.jsxs("form",{className:"chat-form",onSubmit:p,children:[v.jsx("textarea",{value:n,onChange:m=>s(m.target.value),"aria-label":"Message"}),v.jsx("button",{className:"icon-button",title:"Send message",disabled:f,children:v.jsx(IE,{size:16,"aria-hidden":"true"})})]})]})}function or({generatedAt:a,sourceUpdatedAt:t,stale:n=!1}){const s=Math.max(0,a-t),l=n?`STALE ${H0(s)}`:s<15e3?"LIVE":`${H0(s)} ago`;return v.jsx("span",{className:"freshness","data-stale":n,children:l})}function H0(a){const t=Math.round(a/1e3);if(t<60)return`${t}s`;const n=Math.round(t/60);return n<60?`${n}m`:`${Math.round(n/60)}h`}function zo({status:a,detail:t}){const n=(a||"UNKNOWN").toUpperCase(),s=n==="ONLINE"?TE:n==="DISABLED"||n==="UNCONFIGURED"?CE:n==="OFFLINE"?AE:Sx;return v.jsxs("span",{className:"status-badge","data-status":n,title:t||n,children:[v.jsx(s,{size:14,"aria-hidden":"true"}),n]})}function ZE({overview:a,recentEvents:t=[]}){var f,d,p,m;const n=(((f=a.activity)==null?void 0:f.data.recent)||[]).map(g=>({type:String(g.type||g.event_type||"activity.updated"),message:String(g.message||g.title||""),source_type:String(g.event_type||g.type||"activity"),server_id:String(g.server_id||""),severity:String(g.severity||""),source_updated_at:Number(g.occurred_at||0)})),l=[...t.map(g=>({type:g.type,message:g.message||g.safe_message||"",source_type:g.source_type,server_id:g.server_id||"",severity:g.severity||"",source_updated_at:g.source_updated_at})),...n].slice(0,80),c=((d=a.activity)==null?void 0:d.data.groups)||[];return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:"Activity"}),v.jsx("div",{className:"muted",children:"Persisted EventManager history grouped into operational activity."})]}),v.jsx("span",{className:"freshness","data-stale":((p=a.activity)==null?void 0:p.stale)||!1,children:((m=a.activity)==null?void 0:m.data.source)||"event_manager"})]}),v.jsx("div",{className:"grid",children:c.length?c.slice(0,12).map(g=>{var _;return v.jsxs("div",{className:"list-row list-row--with-drawer",children:[v.jsxs("div",{children:[v.jsx("strong",{children:String(g.title||g.group_id||"Activity")}),v.jsxs("div",{className:"muted",children:[String(g.status||g.severity||"updated")," / ",Number(((_=g.events)==null?void 0:_.length)||0)," event(s)"]})]}),v.jsx("span",{className:"mono muted",children:String(g.server_id||g.capability_id||g.task_id||"event")}),v.jsxs("details",{className:"inline-drawer",children:[v.jsx("summary",{children:"Details"}),v.jsx("pre",{children:JSON.stringify(g,null,2)})]})]},String(g.group_id||g.title))}):v.jsx("div",{className:"muted",children:"No persisted activity has been reported yet."})})]}),v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Recent Events"})}),v.jsxs("div",{className:"grid",children:[l.map(g=>v.jsxs("div",{className:"list-row list-row--with-drawer",children:[v.jsxs("div",{children:[v.jsx("strong",{children:g.type}),v.jsx("div",{className:"muted",children:g.message||g.source_type})]}),v.jsx("span",{className:"mono muted",children:g.server_id||g.severity||"event"}),v.jsxs("details",{className:"inline-drawer",children:[v.jsx("summary",{children:"Trace"}),v.jsx("pre",{children:JSON.stringify(g,null,2)})]})]},`${g.type}-${g.source_updated_at}-${g.message}`)),l.length===0?(a.attention.data.items||[]).map(g=>v.jsxs("div",{className:"list-row",children:[v.jsxs("div",{children:[v.jsx("strong",{children:g.title}),v.jsx("div",{className:"muted",children:g.message})]}),v.jsx("span",{className:"mono muted",children:g.kind})]},g.id)):null]})]})]})}function KE({approval:a,readonly:t=!1}){const[n,s]=se.useState(""),[l,c]=se.useState("");async function f(d){s(d),c("");try{await jE(a.approval_id,d)}catch(p){c(p instanceof Error?p.message:String(p))}finally{s("")}}return v.jsxs("article",{className:"approval-card",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("strong",{children:a.summary||a.tool_name||"Approval required"}),v.jsx("div",{className:"muted mono",children:a.approval_id})]}),v.jsxs("span",{className:"status-badge","data-status":"WAITING",children:[v.jsx(yx,{size:14,"aria-hidden":"true"}),a.risk||"risk"]})]}),v.jsx("div",{className:"muted",children:a.reason||"Review the requested action before allowing it to continue."}),v.jsxs("div",{className:"stat-grid",children:[v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Capability"}),v.jsx("b",{className:"mono",style:{fontSize:14},children:a.capability_id})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Target"}),v.jsx("b",{style:{fontSize:14},children:a.target||"Not specified"})]})]}),a.preview?v.jsx("pre",{className:"panel mono",style:{whiteSpace:"pre-wrap",margin:0},children:a.preview}):null,l?v.jsx("div",{className:"attention-item","data-severity":"critical",children:l}):null,t?null:v.jsxs("div",{className:"approval-card__actions",children:[v.jsxs("button",{className:"primary-button",onClick:()=>f("approve"),disabled:!!n,children:[v.jsx(bE,{size:16,"aria-hidden":"true"})," ",n==="approve"?"Approving":"Approve"]}),v.jsxs("button",{className:"danger-button",onClick:()=>f("reject"),disabled:!!n,children:[v.jsx(Mx,{size:16,"aria-hidden":"true"})," ",n==="reject"?"Rejecting":"Reject"]})]})]})}const rf=["ai-server","pc-server","android-server","browser-server","room-server","dev-server"];function of(a=""){const t=a.split(".",1)[0];return rf.includes(t)?t:"ai-server"}function Hi(a){return{"ai-server":"AI","pc-server":"PC","android-server":"Android","browser-server":"Browser","room-server":"Room","dev-server":"Dev"}[a]||a.replace("-server","")}function Ap(a=""){return a.trim().toUpperCase()||"UNKNOWN"}function Mm(a,t=""){const n=Ap(a.status),s=`${a.status_detail||""} ${a.degraded_reason||""} ${a.recovery_hint||""}`.toLowerCase();return a.server_id===t||["DEGRADED","OFFLINE","UNCONFIGURED","DISABLED","RECOVERING"].includes(n)||s.includes("permission")||s.includes("missing")||s.includes("recover")}function JE(a){const t=a.filter(n=>Mm(n));return{ok:Math.max(0,a.length-t.length),attention:t}}function Cx(a){var g,_,y,S,b;const t=a.type||a.source_type||"activity.updated",n=a.capability_id||String(((g=a.payload)==null?void 0:g.capability_id)||""),s=((_=a.visual_hint)==null?void 0:_.arc)||a.server_id||of(n),l=String(a.status||((y=a.payload)==null?void 0:y.status)||"");let c="pulse";const f=Nx((S=a.visual_hint)==null?void 0:S.effect);f?c=f:t==="approval.created"?c="containment":t==="approval.resolved"?c="containment-resolved":t.includes("failed")||l.toLowerCase()==="failed"?c="fracture":t.includes("completed")?c="complete":(t.includes("status")||t.includes("connection"))&&(c=l.toLowerCase().includes("offline")?"disconnect":"recovery");const d=Date.now(),p=a.received_at||a.generated_at||d,m=Number(((b=a.visual_hint)==null?void 0:b.duration_ms)||4500);return{id:a.event_id||`${a.type}-${a.source_updated_at}-${s}-${a.approval_id||""}`,type:t,effect:c,serverId:s,capabilityId:n,status:l,severity:a.severity||"info",message:a.safe_message||a.message||t,createdAt:p,expiresAt:a.expires_at||p+m}}function $E(a,t,n=[]){var S;const s=As((S=a.display_scene)==null?void 0:S.data),l=Date.now(),c=As(s.takeover),f=cb(t.map(b=>ab(b)).filter(Boolean)),d=lb(a),p=Rx(a).map(b=>sb(b)),m=ob(a),g=[...d,...f,...p,...m].filter(b=>!b.expiresAt||b.expiresAt>l||b.persistence==="until_resolved").sort(ub),y=(c.active?{id:String(c.source_id||"display-scene-takeover"),priority:String(c.priority||"P1"),severity:String(c.severity||"warning"),title:String(c.title||"Attention required"),message:String(c.message||"Review AEGIS on phone or web."),persistence:"until_resolved",createdAt:a.generated_at,expiresAt:Number(c.expires_at||0),affectedServers:[]}:void 0)||g.find(b=>["P0","P1"].includes(String(b.priority)));return{sceneMode:String(s.phase||s.mode||wx(a)),privacyMode:!!s.privacy_mode,offline:!!(s.offline||String(a.core.data.health||"").toUpperCase()==="OFFLINE"),stale:!!(a.freshness.stale||s.stale),takeover:y,overlays:g.filter(b=>b.id!==(y==null?void 0:y.id)&&String(b.priority)==="P2").slice(0,3),dock:g.filter(b=>b.id!==(y==null?void 0:y.id)&&b.persistence!=="ephemeral").slice(0,6),ambient:[...g.filter(b=>b.id!==(y==null?void 0:y.id)&&b.persistence==="ephemeral"),...n.map(b=>rb(b))].slice(0,8)}}function Rx(a){const t=a.approvals.data.pending||[],n=a.attention.data.items||[];return[...t.map(l=>({id:l.approval_id,kind:"approval",severity:"warning",title:"Approval required",message:l.summary||l.capability_id||"Review requested action",created_at:l.created_at,expires_at:l.expires_at})),...n.filter(l=>l.kind!=="approval")]}function wx(a){var c,f;const t=(f=(c=a.display_scene)==null?void 0:c.data)==null?void 0:f.phase;if(t)return String(t);const n=a.core.data,s=a.current_task.data;return(a.approvals.data.pending_count||0)>0?"Waiting for Approval":String(n.health||"").toUpperCase()==="OFFLINE"?"Offline":String(n.health||"").toUpperCase()==="DEGRADED"?"Stabilizing":s.task_id||String(n.mode||"").toUpperCase()==="EXECUTING"?"Executing":"Idle"}function Em(a){const t=a.mind_summary.data||{},n=a.core.data||{},s=As(t.memory),l=As(t.autonomy),c=As(l.desires||l.pressures||l.desire_state),f=fb(c);return{"Active goal":String(n.active_goal||"Not reported"),"Dominant desire":f||"Not reported","Context confidence":String(n.confidence||t.context_confidence||"Not reported"),"Memories used":db(s),"Last consolidation":String(s.last_consolidation||s.last_consolidated_at||s.last_sleep_at||"Not reported")}}function tb(a){var d,p,m,g;const t=a.current_task.data,n=(d=a.tasks)==null?void 0:d.data,s=a.commitments.data.items||[],l=!!(t.task_id||t.title),c=(p=n==null?void 0:n.active)!=null&&p.length?n.active:l?[t]:[],f=(m=n==null?void 0:n.waiting)!=null&&m.length?n.waiting:l&&(a.approvals.data.pending_count>0||t.blocked_reason)?[t]:[];return[{id:"active",label:"Active",count:c.length,items:c},{id:"waiting",label:"Waiting",count:f.length,items:f},{id:"scheduled",label:"Scheduled",count:((g=n==null?void 0:n.scheduled)==null?void 0:g.length)||0,items:(n==null?void 0:n.scheduled)||[]},{id:"research",label:"Research",count:Cu(t,"browser-server")?c.length:0,items:Cu(t,"browser-server")?c:[]},{id:"self-development",label:"Self-development",count:Cu(t,"dev-server")?c.length:0,items:Cu(t,"dev-server")?c:[]},{id:"commitments",label:"Commitments",count:s.length,items:s},{id:"completed",label:"Completed",count:((n==null?void 0:n.recent)||[]).filter(_=>String(_.status||"").toLowerCase()==="completed").length||G0(t,"completed"),items:[]},{id:"failed",label:"Failed",count:((n==null?void 0:n.recent)||[]).filter(_=>String(_.status||"").toLowerCase()==="failed").length||G0(t,"failed"),items:[]}]}function eb(a){const t=Date.now();return[{id:"pending",label:"Pending",items:a.filter(n=>Au(n)==="PENDING")},{id:"expiring",label:"Expiring",items:a.filter(n=>n.expires_at&&n.expires_at-t<600*1e3)},{id:"high-risk",label:"High risk",items:a.filter(n=>["HIGH","CRITICAL","FORBIDDEN"].includes(String(n.risk||"").toUpperCase()))},{id:"resolved",label:"Resolved",items:a.filter(n=>["APPROVED","RESOLVED"].includes(Au(n)))},{id:"expired",label:"Expired",items:a.filter(n=>Au(n)==="EXPIRED")},{id:"failed",label:"Failed after approval",items:a.filter(n=>Au(n).includes("FAILED"))}]}function nb(a){var s,l,c;const t=(a==null?void 0:a.approvals.data.pending_count)||0,n=a?Em(a):{};return[{id:"autonomy",label:"Autonomy",summary:"Loop cadence, profile, and autonomous execution guardrails.",status:(s=a==null?void 0:a.mind_summary.data)!=null&&s.autonomy?"Configured":"Not reported"},{id:"permissions",label:"Permissions",summary:"Capability risk, approval requirements, PC/Android operation limits.",status:t?`${t} approval pending`:"Guarded"},{id:"servers",label:"Servers",summary:"AI, PC, Android, Browser, Room, and Dev endpoints.",status:`${((l=a==null?void 0:a.servers.data.items)==null?void 0:l.length)||0} known`},{id:"privacy",label:"Privacy",summary:"Display privacy mode, redaction, local-only surfaces.",status:"Local-first"},{id:"notifications",label:"Notifications",summary:"Attention routing, persistent warnings, and quiet states.",status:`${(a==null?void 0:a.notifications.data.unread_count)||0} unread`},{id:"models",label:"Models",summary:"LLM profiles, provider routing, and fresh-auth protected changes.",status:"Fresh auth required"},{id:"budgets",label:"Budgets",summary:"LLM usage, cost ceilings, and autonomous suppression.",status:String(((c=a==null?void 0:a.usage.data)==null?void 0:c.summary)||"Audit-backed")},{id:"memory",label:"Memory",summary:"Episodic, semantic, procedural retrieval and consolidation.",status:n["Memories used"]||"Not reported"},{id:"display",label:"Display",summary:"Read-only dedicated display, token, kiosk, privacy and power behavior.",status:"Read-only"},{id:"developer",label:"Developer",summary:"Debug drawers, raw JSON, audit traces, and dev server writes.",status:"Restricted"},{id:"backup",label:"Backup",summary:"Data volume, auth credentials, audit, memory, and override backups.",status:"Manual check"}]}function ib(a){const t=As(a.dependencies),n=Object.entries(t);if(!n.length)return"No dependencies reported";const s=n.filter(([,l])=>l===!1||l==="false"||l==="missing").map(([l])=>l);return s.length?`${s.length} dependency issue(s): ${s.slice(0,3).join(", ")}`:`${n.length} dependencies reported`}function ab(a){const t=Cx(a),n=a.priority||Dx(a.severity||t.severity||"info");return{id:a.dedupe_key||a.event_id||t.id,priority:n,severity:a.severity||t.severity||"info",title:a.safe_title||a.type||"AEGIS event",message:a.safe_message||a.message||a.source_type||"AEGIS event",persistence:a.persistence||(n==="P0"||n==="P1"?"until_resolved":n==="P2"?"attention_dock":"ephemeral"),createdAt:a.occurred_at||a.source_updated_at||a.generated_at||Date.now(),expiresAt:a.expires_at||t.expiresAt,affectedServers:a.affected_servers||(a.server_id?[a.server_id]:[]),visualEvent:t}}function sb(a){const t=a.kind==="approval"?"P1":Dx(a.severity);return{id:a.id,priority:t,severity:a.severity||"info",title:a.title,message:a.message||a.recovery_hint||"Review this signal.",persistence:t==="P0"||t==="P1"?"until_resolved":"attention_dock",createdAt:a.created_at||Date.now(),expiresAt:a.expires_at||0,affectedServers:[]}}function rb(a){return{id:a.id,priority:a.effect==="fracture"||a.effect==="disconnect"?"P2":"P3",severity:a.severity||"info",title:a.type,message:a.message,persistence:"ephemeral",createdAt:a.createdAt,expiresAt:a.expiresAt,affectedServers:a.serverId?[a.serverId]:[],visualEvent:a}}function ob(a){var s;const t=(s=a.presentations)==null?void 0:s.data;return t?[["P0","until_resolved",t.takeover],["P2","attention_dock",t.overlays],["P2","until_resolved",t.persistent],["P3","ephemeral",t.ambient]].flatMap(([l,c,f])=>(f||[]).map(d=>({id:String(d.presentation_id||d.id||`${l}-${d.title||"presentation"}`),priority:l,severity:l==="P0"?"critical":l==="P2"?"warning":"info",title:String(d.title||"Presentation"),message:String(d.summary||d.status||"Presentation update"),persistence:c,createdAt:Number(d.created_at||a.generated_at),expiresAt:Number(d.expires_at||0),affectedServers:[]}))):[]}function lb(a){var n,s;return(((s=(n=a.display_queue)==null?void 0:n.data)==null?void 0:s.items)||[]).map(l=>{const c=As(l),f=String(c.priority||"P3"),d=As(c.visual_hint);return{id:String(c.id||c.event_id||c.title||"display-queue-item"),priority:f,severity:String(c.severity||"info"),title:String(c.title||"AEGIS signal"),message:String(c.message||c.title||"AEGIS signal"),persistence:String(c.persistence||(f==="P0"||f==="P1"?"until_resolved":"attention_dock")),createdAt:Number(c.created_at||c.updated_at||Date.now()),expiresAt:Number(c.expires_at||0),affectedServers:Array.isArray(c.affected_servers)?c.affected_servers.map(String):[],visualEvent:d.effect?{id:String(c.event_id||c.id||`${c.title||"queue"}-visual`),type:String(c.title||"display.queue"),effect:Nx(d.effect)||"pulse",serverId:String(d.arc||(Array.isArray(c.affected_servers)?c.affected_servers[0]:"")||"ai-server"),status:String(c.status||""),severity:String(c.severity||"info"),message:String(c.message||c.title||"AEGIS signal"),createdAt:Number(c.created_at||Date.now()),expiresAt:Number(c.expires_at||Date.now()+Number(d.duration_ms||4500))}:void 0}})}function cb(a){const t=new Map;for(const n of a){const s=t.get(n.id);(!s||n.createdAt>=s.createdAt||lf(n.priority)<lf(s.priority))&&t.set(n.id,n)}return[...t.values()]}function ub(a,t){return lf(a.priority)-lf(t.priority)||t.createdAt-a.createdAt}function Dx(a="info"){const t=a.toLowerCase();return t==="critical"?"P0":t==="warning"?"P2":"P3"}function lf(a){return{P0:0,P1:1,P2:2,P3:3}[a]??4}function Nx(a){const t=String(a||"");return["pulse","complete","fracture","containment","containment-resolved","disconnect","recovery"].includes(t)?t:""}function Au(a){return String(a.status||"pending").toUpperCase()}function Cu(a,t){return String(a.capability_id||"").includes(t)?!0:!!(a.steps||[]).some(n=>String(n.capability_id||n.name||"").includes(t))}function G0(a,t){return(a.steps||[]).filter(n=>String(n.status||"").toLowerCase()===t).length}function As(a){return a&&typeof a=="object"&&!Array.isArray(a)?a:{}}function fb(a){let t="",n=Number.NEGATIVE_INFINITY;for(const[s,l]of Object.entries(a)){const c=typeof l=="number"?l:Number(typeof l=="object"&&l?l.value||l.pressure:l);Number.isFinite(c)&&c>n&&(t=s,n=c)}return t}function db(a){const t=a.memories_used||a.used||a.context_items;if(t!==void 0)return String(t);const n=["episodic","semantic","procedural"].reduce((s,l)=>{const c=Number(a[l]||0);return Number.isFinite(c)?s+c:s},0);return n>0?String(n):"Not reported"}function hb({overview:a}){var c,f,d,p;const t=a.approvals.data.pending||[],n=t[0],s=eb(t),l=(((c=a.activity)==null?void 0:c.data.recent)||[]).filter(m=>n?String(m.approval_id||m.task_id||m.capability_id||"").includes(n.approval_id)||String(m.task_id||"")===n.task_id||String(m.capability_id||"")===n.capability_id:!1);return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:"Approvals"}),v.jsx("div",{className:"muted",children:"Every approval is shown with risk, target, reason, preview, and task context."})]}),v.jsx(or,{generatedAt:a.approvals.generated_at,sourceUpdatedAt:a.approvals.source_updated_at,stale:a.approvals.stale})]}),v.jsx("div",{className:"tab-strip",role:"tablist","aria-label":"Approval filters",children:s.map(m=>v.jsxs("button",{className:"tab-chip",type:"button","aria-selected":m.id==="pending",children:[v.jsx("span",{children:m.label}),v.jsx("strong",{children:m.items.length})]},m.id))})]}),v.jsxs("section",{className:"approval-layout",children:[v.jsxs("aside",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Queue"})}),v.jsxs("div",{className:"grid",children:[t.map(m=>v.jsxs("article",{className:"list-row","data-selected":m.approval_id===(n==null?void 0:n.approval_id),children:[v.jsxs("div",{children:[v.jsx("strong",{children:m.summary||m.capability_id}),v.jsx("div",{className:"muted mono",children:m.approval_id})]}),v.jsx("span",{className:"status-badge","data-status":"WAITING",children:m.risk||"risk"})]},m.approval_id)),t.length?null:v.jsx("div",{className:"attention-item","data-severity":"normal",children:"No pending approvals."})]})]}),v.jsx("main",{children:n?v.jsx(KE,{approval:n}):v.jsx("section",{className:"panel",children:v.jsx("div",{className:"attention-item","data-severity":"normal",children:"No action is waiting for approval."})})}),v.jsxs("aside",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Context"})}),n?v.jsxs("div",{className:"metric-list",children:[v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Related task"}),v.jsx("strong",{className:"mono",children:n.task_id||a.current_task.data.task_id||"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Target server"}),v.jsx("strong",{children:Hi(of(n.capability_id))})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Risk rationale"}),v.jsx("strong",{children:n.reason||"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Previous action"}),v.jsx("strong",{children:String(n.previous_action||((f=l[0])==null?void 0:f.message)||((d=l[0])==null?void 0:d.title)||"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Similar past action"}),v.jsx("strong",{children:String(n.similar_past_action||((p=l[1])==null?void 0:p.message)||"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"After approval"}),v.jsx("strong",{children:"Execution resumes through ApprovalManager and TaskExecutionEngine."})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Post-approval effect"}),v.jsx("strong",{children:String(n.expected_effect||"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Audit"}),v.jsx("strong",{children:n.request_id||n.step_id||"Not reported"})]}),v.jsx("div",{className:"approval-safety-note",children:"Bulk approval is not available. Each high-risk action must be reviewed independently with fresh authentication when required."})]}):v.jsx("p",{className:"muted",children:"Approval context appears here when an action is pending."})]})]})]})}function pb({items:a}){return a.length?v.jsx("section",{className:"attention-strip","aria-label":"Attention",children:a.slice(0,6).map(t=>{const n=t.kind==="approval"?yx:t.kind==="server"?GE:Sx;return v.jsxs("article",{className:"attention-item","data-severity":t.severity,children:[v.jsxs("div",{children:[v.jsx("strong",{children:t.title}),v.jsx("div",{className:"muted",children:t.message||t.recovery_hint||"Review this item."})]}),v.jsx(n,{size:20,"aria-label":t.severity})]},t.id)})}):v.jsx("section",{className:"attention-strip","aria-label":"Attention",children:v.jsxs("div",{className:"attention-item","data-severity":"normal",children:[v.jsxs("div",{children:[v.jsx("strong",{children:"No immediate attention required"}),v.jsx("div",{className:"muted",children:"All current UI signals are within normal bounds."})]}),v.jsx(Sm,{size:18,"aria-hidden":"true"})]})})}/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const bm="171",mb=0,V0=1,gb=2,Ux=1,vb=2,Ca=3,Rs=0,ii=1,Da=2,La=0,xo=1,Cp=2,k0=3,j0=4,_b=5,ar=100,yb=101,xb=102,Sb=103,Mb=104,Eb=200,bb=201,Tb=202,Ab=203,Rp=204,wp=205,Cb=206,Rb=207,wb=208,Db=209,Nb=210,Ub=211,Lb=212,Ob=213,Pb=214,Dp=0,Np=1,Up=2,Io=3,Lp=4,Op=5,Pp=6,zp=7,Lx=0,zb=1,Ib=2,Cs=0,Bb=1,Fb=2,Hb=3,Gb=4,Vb=5,kb=6,jb=7,Ox=300,Bo=301,Fo=302,Ip=303,Bp=304,pf=306,Fp=1e3,lr=1001,Hp=1002,Gi=1003,Xb=1004,Ru=1005,ta=1006,Lh=1007,cr=1008,za=1009,Px=1010,zx=1011,nc=1012,Tm=1013,yr=1014,Na=1015,Oa=1016,Am=1017,Cm=1018,Ho=1020,Ix=35902,Bx=1021,Fx=1022,Fi=1023,Hx=1024,Gx=1025,So=1026,Go=1027,Vx=1028,Rm=1029,kx=1030,wm=1031,Dm=1033,Ju=33776,$u=33777,tf=33778,ef=33779,Gp=35840,Vp=35841,kp=35842,jp=35843,Xp=36196,qp=37492,Wp=37496,Yp=37808,Qp=37809,Zp=37810,Kp=37811,Jp=37812,$p=37813,tm=37814,em=37815,nm=37816,im=37817,am=37818,sm=37819,rm=37820,om=37821,nf=36492,lm=36494,cm=36495,jx=36283,um=36284,fm=36285,dm=36286,qb=3200,Wb=3201,Yb=0,Qb=1,gs="",vi="srgb",Vo="srgb-linear",cf="linear",qe="srgb",eo=7680,X0=519,Zb=512,Kb=513,Jb=514,Xx=515,$b=516,tT=517,eT=518,nT=519,q0=35044,W0="300 es",Ua=2e3,uf=2001;class Xo{addEventListener(t,n){this._listeners===void 0&&(this._listeners={});const s=this._listeners;s[t]===void 0&&(s[t]=[]),s[t].indexOf(n)===-1&&s[t].push(n)}hasEventListener(t,n){if(this._listeners===void 0)return!1;const s=this._listeners;return s[t]!==void 0&&s[t].indexOf(n)!==-1}removeEventListener(t,n){if(this._listeners===void 0)return;const l=this._listeners[t];if(l!==void 0){const c=l.indexOf(n);c!==-1&&l.splice(c,1)}}dispatchEvent(t){if(this._listeners===void 0)return;const s=this._listeners[t.type];if(s!==void 0){t.target=this;const l=s.slice(0);for(let c=0,f=l.length;c<f;c++)l[c].call(this,t);t.target=null}}}const Bn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Y0=1234567;const Ql=Math.PI/180,ic=180/Math.PI;function qo(){const a=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0,s=Math.random()*4294967295|0;return(Bn[a&255]+Bn[a>>8&255]+Bn[a>>16&255]+Bn[a>>24&255]+"-"+Bn[t&255]+Bn[t>>8&255]+"-"+Bn[t>>16&15|64]+Bn[t>>24&255]+"-"+Bn[n&63|128]+Bn[n>>8&255]+"-"+Bn[n>>16&255]+Bn[n>>24&255]+Bn[s&255]+Bn[s>>8&255]+Bn[s>>16&255]+Bn[s>>24&255]).toLowerCase()}function ge(a,t,n){return Math.max(t,Math.min(n,a))}function Nm(a,t){return(a%t+t)%t}function iT(a,t,n,s,l){return s+(a-t)*(l-s)/(n-t)}function aT(a,t,n){return a!==t?(n-a)/(t-a):0}function Zl(a,t,n){return(1-n)*a+n*t}function sT(a,t,n,s){return Zl(a,t,1-Math.exp(-n*s))}function rT(a,t=1){return t-Math.abs(Nm(a,t*2)-t)}function oT(a,t,n){return a<=t?0:a>=n?1:(a=(a-t)/(n-t),a*a*(3-2*a))}function lT(a,t,n){return a<=t?0:a>=n?1:(a=(a-t)/(n-t),a*a*a*(a*(a*6-15)+10))}function cT(a,t){return a+Math.floor(Math.random()*(t-a+1))}function uT(a,t){return a+Math.random()*(t-a)}function fT(a){return a*(.5-Math.random())}function dT(a){a!==void 0&&(Y0=a);let t=Y0+=1831565813;return t=Math.imul(t^t>>>15,t|1),t^=t+Math.imul(t^t>>>7,t|61),((t^t>>>14)>>>0)/4294967296}function hT(a){return a*Ql}function pT(a){return a*ic}function mT(a){return(a&a-1)===0&&a!==0}function gT(a){return Math.pow(2,Math.ceil(Math.log(a)/Math.LN2))}function vT(a){return Math.pow(2,Math.floor(Math.log(a)/Math.LN2))}function _T(a,t,n,s,l){const c=Math.cos,f=Math.sin,d=c(n/2),p=f(n/2),m=c((t+s)/2),g=f((t+s)/2),_=c((t-s)/2),y=f((t-s)/2),S=c((s-t)/2),b=f((s-t)/2);switch(l){case"XYX":a.set(d*g,p*_,p*y,d*m);break;case"YZY":a.set(p*y,d*g,p*_,d*m);break;case"ZXZ":a.set(p*_,p*y,d*g,d*m);break;case"XZX":a.set(d*g,p*b,p*S,d*m);break;case"YXY":a.set(p*S,d*g,p*b,d*m);break;case"ZYZ":a.set(p*b,p*S,d*g,d*m);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+l)}}function go(a,t){switch(t.constructor){case Float32Array:return a;case Uint32Array:return a/4294967295;case Uint16Array:return a/65535;case Uint8Array:return a/255;case Int32Array:return Math.max(a/2147483647,-1);case Int16Array:return Math.max(a/32767,-1);case Int8Array:return Math.max(a/127,-1);default:throw new Error("Invalid component type.")}}function jn(a,t){switch(t.constructor){case Float32Array:return a;case Uint32Array:return Math.round(a*4294967295);case Uint16Array:return Math.round(a*65535);case Uint8Array:return Math.round(a*255);case Int32Array:return Math.round(a*2147483647);case Int16Array:return Math.round(a*32767);case Int8Array:return Math.round(a*127);default:throw new Error("Invalid component type.")}}const ls={DEG2RAD:Ql,RAD2DEG:ic,generateUUID:qo,clamp:ge,euclideanModulo:Nm,mapLinear:iT,inverseLerp:aT,lerp:Zl,damp:sT,pingpong:rT,smoothstep:oT,smootherstep:lT,randInt:cT,randFloat:uT,randFloatSpread:fT,seededRandom:dT,degToRad:hT,radToDeg:pT,isPowerOfTwo:mT,ceilPowerOfTwo:gT,floorPowerOfTwo:vT,setQuaternionFromProperEuler:_T,normalize:jn,denormalize:go};class Wt{constructor(t=0,n=0){Wt.prototype.isVector2=!0,this.x=t,this.y=n}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,n){return this.x=t,this.y=n,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const n=this.x,s=this.y,l=t.elements;return this.x=l[0]*n+l[3]*s+l[6],this.y=l[1]*n+l[4]*s+l[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(ge(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y;return n*n+s*s}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this}rotateAround(t,n){const s=Math.cos(n),l=Math.sin(n),c=this.x-t.x,f=this.y-t.y;return this.x=c*s-f*l+t.x,this.y=c*l+f*s+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class de{constructor(t,n,s,l,c,f,d,p,m){de.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,n,s,l,c,f,d,p,m)}set(t,n,s,l,c,f,d,p,m){const g=this.elements;return g[0]=t,g[1]=l,g[2]=d,g[3]=n,g[4]=c,g[5]=p,g[6]=s,g[7]=f,g[8]=m,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],this}extractBasis(t,n,s){return t.setFromMatrix3Column(this,0),n.setFromMatrix3Column(this,1),s.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const n=t.elements;return this.set(n[0],n[4],n[8],n[1],n[5],n[9],n[2],n[6],n[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,l=n.elements,c=this.elements,f=s[0],d=s[3],p=s[6],m=s[1],g=s[4],_=s[7],y=s[2],S=s[5],b=s[8],T=l[0],E=l[3],x=l[6],P=l[1],N=l[4],R=l[7],V=l[2],F=l[5],z=l[8];return c[0]=f*T+d*P+p*V,c[3]=f*E+d*N+p*F,c[6]=f*x+d*R+p*z,c[1]=m*T+g*P+_*V,c[4]=m*E+g*N+_*F,c[7]=m*x+g*R+_*z,c[2]=y*T+S*P+b*V,c[5]=y*E+S*N+b*F,c[8]=y*x+S*R+b*z,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[3]*=t,n[6]*=t,n[1]*=t,n[4]*=t,n[7]*=t,n[2]*=t,n[5]*=t,n[8]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8];return n*f*g-n*d*m-s*c*g+s*d*p+l*c*m-l*f*p}invert(){const t=this.elements,n=t[0],s=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8],_=g*f-d*m,y=d*p-g*c,S=m*c-f*p,b=n*_+s*y+l*S;if(b===0)return this.set(0,0,0,0,0,0,0,0,0);const T=1/b;return t[0]=_*T,t[1]=(l*m-g*s)*T,t[2]=(d*s-l*f)*T,t[3]=y*T,t[4]=(g*n-l*p)*T,t[5]=(l*c-d*n)*T,t[6]=S*T,t[7]=(s*p-m*n)*T,t[8]=(f*n-s*c)*T,this}transpose(){let t;const n=this.elements;return t=n[1],n[1]=n[3],n[3]=t,t=n[2],n[2]=n[6],n[6]=t,t=n[5],n[5]=n[7],n[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const n=this.elements;return t[0]=n[0],t[1]=n[3],t[2]=n[6],t[3]=n[1],t[4]=n[4],t[5]=n[7],t[6]=n[2],t[7]=n[5],t[8]=n[8],this}setUvTransform(t,n,s,l,c,f,d){const p=Math.cos(c),m=Math.sin(c);return this.set(s*p,s*m,-s*(p*f+m*d)+f+t,-l*m,l*p,-l*(-m*f+p*d)+d+n,0,0,1),this}scale(t,n){return this.premultiply(Oh.makeScale(t,n)),this}rotate(t){return this.premultiply(Oh.makeRotation(-t)),this}translate(t,n){return this.premultiply(Oh.makeTranslation(t,n)),this}makeTranslation(t,n){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,n,0,0,1),this}makeRotation(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,s,n,0,0,0,1),this}makeScale(t,n){return this.set(t,0,0,0,n,0,0,0,1),this}equals(t){const n=this.elements,s=t.elements;for(let l=0;l<9;l++)if(n[l]!==s[l])return!1;return!0}fromArray(t,n=0){for(let s=0;s<9;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t}clone(){return new this.constructor().fromArray(this.elements)}}const Oh=new de;function qx(a){for(let t=a.length-1;t>=0;--t)if(a[t]>=65535)return!0;return!1}function ff(a){return document.createElementNS("http://www.w3.org/1999/xhtml",a)}function yT(){const a=ff("canvas");return a.style.display="block",a}const Q0={};function vo(a){a in Q0||(Q0[a]=!0,console.warn(a))}function xT(a,t,n){return new Promise(function(s,l){function c(){switch(a.clientWaitSync(t,a.SYNC_FLUSH_COMMANDS_BIT,0)){case a.WAIT_FAILED:l();break;case a.TIMEOUT_EXPIRED:setTimeout(c,n);break;default:s()}}setTimeout(c,n)})}function ST(a){const t=a.elements;t[2]=.5*t[2]+.5*t[3],t[6]=.5*t[6]+.5*t[7],t[10]=.5*t[10]+.5*t[11],t[14]=.5*t[14]+.5*t[15]}function MT(a){const t=a.elements;t[11]===-1?(t[10]=-t[10]-1,t[14]=-t[14]):(t[10]=-t[10],t[14]=-t[14]+1)}const Z0=new de().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),K0=new de().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function ET(){const a={enabled:!0,workingColorSpace:Vo,spaces:{},convert:function(l,c,f){return this.enabled===!1||c===f||!c||!f||(this.spaces[c].transfer===qe&&(l.r=Pa(l.r),l.g=Pa(l.g),l.b=Pa(l.b)),this.spaces[c].primaries!==this.spaces[f].primaries&&(l.applyMatrix3(this.spaces[c].toXYZ),l.applyMatrix3(this.spaces[f].fromXYZ)),this.spaces[f].transfer===qe&&(l.r=Mo(l.r),l.g=Mo(l.g),l.b=Mo(l.b))),l},fromWorkingColorSpace:function(l,c){return this.convert(l,this.workingColorSpace,c)},toWorkingColorSpace:function(l,c){return this.convert(l,c,this.workingColorSpace)},getPrimaries:function(l){return this.spaces[l].primaries},getTransfer:function(l){return l===gs?cf:this.spaces[l].transfer},getLuminanceCoefficients:function(l,c=this.workingColorSpace){return l.fromArray(this.spaces[c].luminanceCoefficients)},define:function(l){Object.assign(this.spaces,l)},_getMatrix:function(l,c,f){return l.copy(this.spaces[c].toXYZ).multiply(this.spaces[f].fromXYZ)},_getDrawingBufferColorSpace:function(l){return this.spaces[l].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(l=this.workingColorSpace){return this.spaces[l].workingColorSpaceConfig.unpackColorSpace}},t=[.64,.33,.3,.6,.15,.06],n=[.2126,.7152,.0722],s=[.3127,.329];return a.define({[Vo]:{primaries:t,whitePoint:s,transfer:cf,toXYZ:Z0,fromXYZ:K0,luminanceCoefficients:n,workingColorSpaceConfig:{unpackColorSpace:vi},outputColorSpaceConfig:{drawingBufferColorSpace:vi}},[vi]:{primaries:t,whitePoint:s,transfer:qe,toXYZ:Z0,fromXYZ:K0,luminanceCoefficients:n,outputColorSpaceConfig:{drawingBufferColorSpace:vi}}}),a}const Oe=ET();function Pa(a){return a<.04045?a*.0773993808:Math.pow(a*.9478672986+.0521327014,2.4)}function Mo(a){return a<.0031308?a*12.92:1.055*Math.pow(a,.41666)-.055}let no;class bT{static getDataURL(t){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let n;if(t instanceof HTMLCanvasElement)n=t;else{no===void 0&&(no=ff("canvas")),no.width=t.width,no.height=t.height;const s=no.getContext("2d");t instanceof ImageData?s.putImageData(t,0,0):s.drawImage(t,0,0,t.width,t.height),n=no}return n.width>2048||n.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",t),n.toDataURL("image/jpeg",.6)):n.toDataURL("image/png")}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const n=ff("canvas");n.width=t.width,n.height=t.height;const s=n.getContext("2d");s.drawImage(t,0,0,t.width,t.height);const l=s.getImageData(0,0,t.width,t.height),c=l.data;for(let f=0;f<c.length;f++)c[f]=Pa(c[f]/255)*255;return s.putImageData(l,0,0),n}else if(t.data){const n=t.data.slice(0);for(let s=0;s<n.length;s++)n instanceof Uint8Array||n instanceof Uint8ClampedArray?n[s]=Math.floor(Pa(n[s]/255)*255):n[s]=Pa(n[s]);return{data:n,width:t.width,height:t.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let TT=0;class Wx{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:TT++}),this.uuid=qo(),this.data=t,this.dataReady=!0,this.version=0}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const s={uuid:this.uuid,url:""},l=this.data;if(l!==null){let c;if(Array.isArray(l)){c=[];for(let f=0,d=l.length;f<d;f++)l[f].isDataTexture?c.push(Ph(l[f].image)):c.push(Ph(l[f]))}else c=Ph(l);s.url=c}return n||(t.images[this.uuid]=s),s}}function Ph(a){return typeof HTMLImageElement<"u"&&a instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&a instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&a instanceof ImageBitmap?bT.getDataURL(a):a.data?{data:Array.from(a.data),width:a.width,height:a.height,type:a.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let AT=0;class ai extends Xo{constructor(t=ai.DEFAULT_IMAGE,n=ai.DEFAULT_MAPPING,s=lr,l=lr,c=ta,f=cr,d=Fi,p=za,m=ai.DEFAULT_ANISOTROPY,g=gs){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:AT++}),this.uuid=qo(),this.name="",this.source=new Wx(t),this.mipmaps=[],this.mapping=n,this.channel=0,this.wrapS=s,this.wrapT=l,this.magFilter=c,this.minFilter=f,this.anisotropy=m,this.format=d,this.internalFormat=null,this.type=p,this.offset=new Wt(0,0),this.repeat=new Wt(1,1),this.center=new Wt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new de,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=g,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(t=null){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}toJSON(t){const n=t===void 0||typeof t=="string";if(!n&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const s={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(s.userData=this.userData),n||(t.textures[this.uuid]=s),s}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==Ox)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case Fp:t.x=t.x-Math.floor(t.x);break;case lr:t.x=t.x<0?0:1;break;case Hp:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case Fp:t.y=t.y-Math.floor(t.y);break;case lr:t.y=t.y<0?0:1;break;case Hp:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}ai.DEFAULT_IMAGE=null;ai.DEFAULT_MAPPING=Ox;ai.DEFAULT_ANISOTROPY=1;class We{constructor(t=0,n=0,s=0,l=1){We.prototype.isVector4=!0,this.x=t,this.y=n,this.z=s,this.w=l}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,n,s,l){return this.x=t,this.y=n,this.z=s,this.w=l,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;case 3:this.w=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this.w=t.w+n.w,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this.w+=t.w*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this.w=t.w-n.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const n=this.x,s=this.y,l=this.z,c=this.w,f=t.elements;return this.x=f[0]*n+f[4]*s+f[8]*l+f[12]*c,this.y=f[1]*n+f[5]*s+f[9]*l+f[13]*c,this.z=f[2]*n+f[6]*s+f[10]*l+f[14]*c,this.w=f[3]*n+f[7]*s+f[11]*l+f[15]*c,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const n=Math.sqrt(1-t.w*t.w);return n<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/n,this.y=t.y/n,this.z=t.z/n),this}setAxisAngleFromRotationMatrix(t){let n,s,l,c;const p=t.elements,m=p[0],g=p[4],_=p[8],y=p[1],S=p[5],b=p[9],T=p[2],E=p[6],x=p[10];if(Math.abs(g-y)<.01&&Math.abs(_-T)<.01&&Math.abs(b-E)<.01){if(Math.abs(g+y)<.1&&Math.abs(_+T)<.1&&Math.abs(b+E)<.1&&Math.abs(m+S+x-3)<.1)return this.set(1,0,0,0),this;n=Math.PI;const N=(m+1)/2,R=(S+1)/2,V=(x+1)/2,F=(g+y)/4,z=(_+T)/4,G=(b+E)/4;return N>R&&N>V?N<.01?(s=0,l=.707106781,c=.707106781):(s=Math.sqrt(N),l=F/s,c=z/s):R>V?R<.01?(s=.707106781,l=0,c=.707106781):(l=Math.sqrt(R),s=F/l,c=G/l):V<.01?(s=.707106781,l=.707106781,c=0):(c=Math.sqrt(V),s=z/c,l=G/c),this.set(s,l,c,n),this}let P=Math.sqrt((E-b)*(E-b)+(_-T)*(_-T)+(y-g)*(y-g));return Math.abs(P)<.001&&(P=1),this.x=(E-b)/P,this.y=(_-T)/P,this.z=(y-g)/P,this.w=Math.acos((m+S+x-1)/2),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this.w=n[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this.w=ge(this.w,t.w,n.w),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this.w=ge(this.w,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this.w+=(t.w-this.w)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this.w=t.w+(n.w-t.w)*s,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this.w=t[n+3],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t[n+3]=this.w,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this.w=t.getW(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class CT extends Xo{constructor(t=1,n=1,s={}){super(),this.isRenderTarget=!0,this.width=t,this.height=n,this.depth=1,this.scissor=new We(0,0,t,n),this.scissorTest=!1,this.viewport=new We(0,0,t,n);const l={width:t,height:n,depth:1};s=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ta,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},s);const c=new ai(l,s.mapping,s.wrapS,s.wrapT,s.magFilter,s.minFilter,s.format,s.type,s.anisotropy,s.colorSpace);c.flipY=!1,c.generateMipmaps=s.generateMipmaps,c.internalFormat=s.internalFormat,this.textures=[];const f=s.count;for(let d=0;d<f;d++)this.textures[d]=c.clone(),this.textures[d].isRenderTargetTexture=!0;this.depthBuffer=s.depthBuffer,this.stencilBuffer=s.stencilBuffer,this.resolveDepthBuffer=s.resolveDepthBuffer,this.resolveStencilBuffer=s.resolveStencilBuffer,this.depthTexture=s.depthTexture,this.samples=s.samples}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}setSize(t,n,s=1){if(this.width!==t||this.height!==n||this.depth!==s){this.width=t,this.height=n,this.depth=s;for(let l=0,c=this.textures.length;l<c;l++)this.textures[l].image.width=t,this.textures[l].image.height=n,this.textures[l].image.depth=s;this.dispose()}this.viewport.set(0,0,t,n),this.scissor.set(0,0,t,n)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let s=0,l=t.textures.length;s<l;s++)this.textures[s]=t.textures[s].clone(),this.textures[s].isRenderTargetTexture=!0;const n=Object.assign({},t.texture.image);return this.texture.source=new Wx(n),this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Vi extends CT{constructor(t=1,n=1,s={}){super(t,n,s),this.isWebGLRenderTarget=!0}}class Yx extends ai{constructor(t=null,n=1,s=1,l=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:n,height:s,depth:l},this.magFilter=Gi,this.minFilter=Gi,this.wrapR=lr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class RT extends ai{constructor(t=null,n=1,s=1,l=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:n,height:s,depth:l},this.magFilter=Gi,this.minFilter=Gi,this.wrapR=lr,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class uc{constructor(t=0,n=0,s=0,l=1){this.isQuaternion=!0,this._x=t,this._y=n,this._z=s,this._w=l}static slerpFlat(t,n,s,l,c,f,d){let p=s[l+0],m=s[l+1],g=s[l+2],_=s[l+3];const y=c[f+0],S=c[f+1],b=c[f+2],T=c[f+3];if(d===0){t[n+0]=p,t[n+1]=m,t[n+2]=g,t[n+3]=_;return}if(d===1){t[n+0]=y,t[n+1]=S,t[n+2]=b,t[n+3]=T;return}if(_!==T||p!==y||m!==S||g!==b){let E=1-d;const x=p*y+m*S+g*b+_*T,P=x>=0?1:-1,N=1-x*x;if(N>Number.EPSILON){const V=Math.sqrt(N),F=Math.atan2(V,x*P);E=Math.sin(E*F)/V,d=Math.sin(d*F)/V}const R=d*P;if(p=p*E+y*R,m=m*E+S*R,g=g*E+b*R,_=_*E+T*R,E===1-d){const V=1/Math.sqrt(p*p+m*m+g*g+_*_);p*=V,m*=V,g*=V,_*=V}}t[n]=p,t[n+1]=m,t[n+2]=g,t[n+3]=_}static multiplyQuaternionsFlat(t,n,s,l,c,f){const d=s[l],p=s[l+1],m=s[l+2],g=s[l+3],_=c[f],y=c[f+1],S=c[f+2],b=c[f+3];return t[n]=d*b+g*_+p*S-m*y,t[n+1]=p*b+g*y+m*_-d*S,t[n+2]=m*b+g*S+d*y-p*_,t[n+3]=g*b-d*_-p*y-m*S,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,n,s,l){return this._x=t,this._y=n,this._z=s,this._w=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,n=!0){const s=t._x,l=t._y,c=t._z,f=t._order,d=Math.cos,p=Math.sin,m=d(s/2),g=d(l/2),_=d(c/2),y=p(s/2),S=p(l/2),b=p(c/2);switch(f){case"XYZ":this._x=y*g*_+m*S*b,this._y=m*S*_-y*g*b,this._z=m*g*b+y*S*_,this._w=m*g*_-y*S*b;break;case"YXZ":this._x=y*g*_+m*S*b,this._y=m*S*_-y*g*b,this._z=m*g*b-y*S*_,this._w=m*g*_+y*S*b;break;case"ZXY":this._x=y*g*_-m*S*b,this._y=m*S*_+y*g*b,this._z=m*g*b+y*S*_,this._w=m*g*_-y*S*b;break;case"ZYX":this._x=y*g*_-m*S*b,this._y=m*S*_+y*g*b,this._z=m*g*b-y*S*_,this._w=m*g*_+y*S*b;break;case"YZX":this._x=y*g*_+m*S*b,this._y=m*S*_+y*g*b,this._z=m*g*b-y*S*_,this._w=m*g*_-y*S*b;break;case"XZY":this._x=y*g*_-m*S*b,this._y=m*S*_-y*g*b,this._z=m*g*b+y*S*_,this._w=m*g*_+y*S*b;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+f)}return n===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,n){const s=n/2,l=Math.sin(s);return this._x=t.x*l,this._y=t.y*l,this._z=t.z*l,this._w=Math.cos(s),this._onChangeCallback(),this}setFromRotationMatrix(t){const n=t.elements,s=n[0],l=n[4],c=n[8],f=n[1],d=n[5],p=n[9],m=n[2],g=n[6],_=n[10],y=s+d+_;if(y>0){const S=.5/Math.sqrt(y+1);this._w=.25/S,this._x=(g-p)*S,this._y=(c-m)*S,this._z=(f-l)*S}else if(s>d&&s>_){const S=2*Math.sqrt(1+s-d-_);this._w=(g-p)/S,this._x=.25*S,this._y=(l+f)/S,this._z=(c+m)/S}else if(d>_){const S=2*Math.sqrt(1+d-s-_);this._w=(c-m)/S,this._x=(l+f)/S,this._y=.25*S,this._z=(p+g)/S}else{const S=2*Math.sqrt(1+_-s-d);this._w=(f-l)/S,this._x=(c+m)/S,this._y=(p+g)/S,this._z=.25*S}return this._onChangeCallback(),this}setFromUnitVectors(t,n){let s=t.dot(n)+1;return s<Number.EPSILON?(s=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=s):(this._x=0,this._y=-t.z,this._z=t.y,this._w=s)):(this._x=t.y*n.z-t.z*n.y,this._y=t.z*n.x-t.x*n.z,this._z=t.x*n.y-t.y*n.x,this._w=s),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(ge(this.dot(t),-1,1)))}rotateTowards(t,n){const s=this.angleTo(t);if(s===0)return this;const l=Math.min(1,n/s);return this.slerp(t,l),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,n){const s=t._x,l=t._y,c=t._z,f=t._w,d=n._x,p=n._y,m=n._z,g=n._w;return this._x=s*g+f*d+l*m-c*p,this._y=l*g+f*p+c*d-s*m,this._z=c*g+f*m+s*p-l*d,this._w=f*g-s*d-l*p-c*m,this._onChangeCallback(),this}slerp(t,n){if(n===0)return this;if(n===1)return this.copy(t);const s=this._x,l=this._y,c=this._z,f=this._w;let d=f*t._w+s*t._x+l*t._y+c*t._z;if(d<0?(this._w=-t._w,this._x=-t._x,this._y=-t._y,this._z=-t._z,d=-d):this.copy(t),d>=1)return this._w=f,this._x=s,this._y=l,this._z=c,this;const p=1-d*d;if(p<=Number.EPSILON){const S=1-n;return this._w=S*f+n*this._w,this._x=S*s+n*this._x,this._y=S*l+n*this._y,this._z=S*c+n*this._z,this.normalize(),this}const m=Math.sqrt(p),g=Math.atan2(m,d),_=Math.sin((1-n)*g)/m,y=Math.sin(n*g)/m;return this._w=f*_+this._w*y,this._x=s*_+this._x*y,this._y=l*_+this._y*y,this._z=c*_+this._z*y,this._onChangeCallback(),this}slerpQuaternions(t,n,s){return this.copy(t).slerp(n,s)}random(){const t=2*Math.PI*Math.random(),n=2*Math.PI*Math.random(),s=Math.random(),l=Math.sqrt(1-s),c=Math.sqrt(s);return this.set(l*Math.sin(t),l*Math.cos(t),c*Math.sin(n),c*Math.cos(n))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,n=0){return this._x=t[n],this._y=t[n+1],this._z=t[n+2],this._w=t[n+3],this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._w,t}fromBufferAttribute(t,n){return this._x=t.getX(n),this._y=t.getY(n),this._z=t.getZ(n),this._w=t.getW(n),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class W{constructor(t=0,n=0,s=0){W.prototype.isVector3=!0,this.x=t,this.y=n,this.z=s}set(t,n,s){return s===void 0&&(s=this.z),this.x=t,this.y=n,this.z=s,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,n){switch(t){case 0:this.x=n;break;case 1:this.y=n;break;case 2:this.z=n;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,n){return this.x=t.x+n.x,this.y=t.y+n.y,this.z=t.z+n.z,this}addScaledVector(t,n){return this.x+=t.x*n,this.y+=t.y*n,this.z+=t.z*n,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,n){return this.x=t.x-n.x,this.y=t.y-n.y,this.z=t.z-n.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,n){return this.x=t.x*n.x,this.y=t.y*n.y,this.z=t.z*n.z,this}applyEuler(t){return this.applyQuaternion(J0.setFromEuler(t))}applyAxisAngle(t,n){return this.applyQuaternion(J0.setFromAxisAngle(t,n))}applyMatrix3(t){const n=this.x,s=this.y,l=this.z,c=t.elements;return this.x=c[0]*n+c[3]*s+c[6]*l,this.y=c[1]*n+c[4]*s+c[7]*l,this.z=c[2]*n+c[5]*s+c[8]*l,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const n=this.x,s=this.y,l=this.z,c=t.elements,f=1/(c[3]*n+c[7]*s+c[11]*l+c[15]);return this.x=(c[0]*n+c[4]*s+c[8]*l+c[12])*f,this.y=(c[1]*n+c[5]*s+c[9]*l+c[13])*f,this.z=(c[2]*n+c[6]*s+c[10]*l+c[14])*f,this}applyQuaternion(t){const n=this.x,s=this.y,l=this.z,c=t.x,f=t.y,d=t.z,p=t.w,m=2*(f*l-d*s),g=2*(d*n-c*l),_=2*(c*s-f*n);return this.x=n+p*m+f*_-d*g,this.y=s+p*g+d*m-c*_,this.z=l+p*_+c*g-f*m,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const n=this.x,s=this.y,l=this.z,c=t.elements;return this.x=c[0]*n+c[4]*s+c[8]*l,this.y=c[1]*n+c[5]*s+c[9]*l,this.z=c[2]*n+c[6]*s+c[10]*l,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,n){return this.x=ge(this.x,t.x,n.x),this.y=ge(this.y,t.y,n.y),this.z=ge(this.z,t.z,n.z),this}clampScalar(t,n){return this.x=ge(this.x,t,n),this.y=ge(this.y,t,n),this.z=ge(this.z,t,n),this}clampLength(t,n){const s=this.length();return this.divideScalar(s||1).multiplyScalar(ge(s,t,n))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,n){return this.x+=(t.x-this.x)*n,this.y+=(t.y-this.y)*n,this.z+=(t.z-this.z)*n,this}lerpVectors(t,n,s){return this.x=t.x+(n.x-t.x)*s,this.y=t.y+(n.y-t.y)*s,this.z=t.z+(n.z-t.z)*s,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,n){const s=t.x,l=t.y,c=t.z,f=n.x,d=n.y,p=n.z;return this.x=l*p-c*d,this.y=c*f-s*p,this.z=s*d-l*f,this}projectOnVector(t){const n=t.lengthSq();if(n===0)return this.set(0,0,0);const s=t.dot(this)/n;return this.copy(t).multiplyScalar(s)}projectOnPlane(t){return zh.copy(this).projectOnVector(t),this.sub(zh)}reflect(t){return this.sub(zh.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const n=Math.sqrt(this.lengthSq()*t.lengthSq());if(n===0)return Math.PI/2;const s=this.dot(t)/n;return Math.acos(ge(s,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const n=this.x-t.x,s=this.y-t.y,l=this.z-t.z;return n*n+s*s+l*l}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,n,s){const l=Math.sin(n)*t;return this.x=l*Math.sin(s),this.y=Math.cos(n)*t,this.z=l*Math.cos(s),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,n,s){return this.x=t*Math.sin(n),this.y=s,this.z=t*Math.cos(n),this}setFromMatrixPosition(t){const n=t.elements;return this.x=n[12],this.y=n[13],this.z=n[14],this}setFromMatrixScale(t){const n=this.setFromMatrixColumn(t,0).length(),s=this.setFromMatrixColumn(t,1).length(),l=this.setFromMatrixColumn(t,2).length();return this.x=n,this.y=s,this.z=l,this}setFromMatrixColumn(t,n){return this.fromArray(t.elements,n*4)}setFromMatrix3Column(t,n){return this.fromArray(t.elements,n*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,n=0){return this.x=t[n],this.y=t[n+1],this.z=t[n+2],this}toArray(t=[],n=0){return t[n]=this.x,t[n+1]=this.y,t[n+2]=this.z,t}fromBufferAttribute(t,n){return this.x=t.getX(n),this.y=t.getY(n),this.z=t.getZ(n),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,n=Math.random()*2-1,s=Math.sqrt(1-n*n);return this.x=s*Math.cos(t),this.y=n,this.z=s*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const zh=new W,J0=new uc;class fc{constructor(t=new W(1/0,1/0,1/0),n=new W(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=n}set(t,n){return this.min.copy(t),this.max.copy(n),this}setFromArray(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n+=3)this.expandByPoint(Oi.fromArray(t,n));return this}setFromBufferAttribute(t){this.makeEmpty();for(let n=0,s=t.count;n<s;n++)this.expandByPoint(Oi.fromBufferAttribute(t,n));return this}setFromPoints(t){this.makeEmpty();for(let n=0,s=t.length;n<s;n++)this.expandByPoint(t[n]);return this}setFromCenterAndSize(t,n){const s=Oi.copy(n).multiplyScalar(.5);return this.min.copy(t).sub(s),this.max.copy(t).add(s),this}setFromObject(t,n=!1){return this.makeEmpty(),this.expandByObject(t,n)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,n=!1){t.updateWorldMatrix(!1,!1);const s=t.geometry;if(s!==void 0){const c=s.getAttribute("position");if(n===!0&&c!==void 0&&t.isInstancedMesh!==!0)for(let f=0,d=c.count;f<d;f++)t.isMesh===!0?t.getVertexPosition(f,Oi):Oi.fromBufferAttribute(c,f),Oi.applyMatrix4(t.matrixWorld),this.expandByPoint(Oi);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),wu.copy(t.boundingBox)):(s.boundingBox===null&&s.computeBoundingBox(),wu.copy(s.boundingBox)),wu.applyMatrix4(t.matrixWorld),this.union(wu)}const l=t.children;for(let c=0,f=l.length;c<f;c++)this.expandByObject(l[c],n);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,n){return n.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Oi),Oi.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let n,s;return t.normal.x>0?(n=t.normal.x*this.min.x,s=t.normal.x*this.max.x):(n=t.normal.x*this.max.x,s=t.normal.x*this.min.x),t.normal.y>0?(n+=t.normal.y*this.min.y,s+=t.normal.y*this.max.y):(n+=t.normal.y*this.max.y,s+=t.normal.y*this.min.y),t.normal.z>0?(n+=t.normal.z*this.min.z,s+=t.normal.z*this.max.z):(n+=t.normal.z*this.max.z,s+=t.normal.z*this.min.z),n<=-t.constant&&s>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Gl),Du.subVectors(this.max,Gl),io.subVectors(t.a,Gl),ao.subVectors(t.b,Gl),so.subVectors(t.c,Gl),cs.subVectors(ao,io),us.subVectors(so,ao),Qs.subVectors(io,so);let n=[0,-cs.z,cs.y,0,-us.z,us.y,0,-Qs.z,Qs.y,cs.z,0,-cs.x,us.z,0,-us.x,Qs.z,0,-Qs.x,-cs.y,cs.x,0,-us.y,us.x,0,-Qs.y,Qs.x,0];return!Ih(n,io,ao,so,Du)||(n=[1,0,0,0,1,0,0,0,1],!Ih(n,io,ao,so,Du))?!1:(Nu.crossVectors(cs,us),n=[Nu.x,Nu.y,Nu.z],Ih(n,io,ao,so,Du))}clampPoint(t,n){return n.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Oi).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Oi).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(Sa[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),Sa[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),Sa[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),Sa[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),Sa[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),Sa[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),Sa[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),Sa[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(Sa),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}}const Sa=[new W,new W,new W,new W,new W,new W,new W,new W],Oi=new W,wu=new fc,io=new W,ao=new W,so=new W,cs=new W,us=new W,Qs=new W,Gl=new W,Du=new W,Nu=new W,Zs=new W;function Ih(a,t,n,s,l){for(let c=0,f=a.length-3;c<=f;c+=3){Zs.fromArray(a,c);const d=l.x*Math.abs(Zs.x)+l.y*Math.abs(Zs.y)+l.z*Math.abs(Zs.z),p=t.dot(Zs),m=n.dot(Zs),g=s.dot(Zs);if(Math.max(-Math.max(p,m,g),Math.min(p,m,g))>d)return!1}return!0}const wT=new fc,Vl=new W,Bh=new W;class Um{constructor(t=new W,n=-1){this.isSphere=!0,this.center=t,this.radius=n}set(t,n){return this.center.copy(t),this.radius=n,this}setFromPoints(t,n){const s=this.center;n!==void 0?s.copy(n):wT.setFromPoints(t).getCenter(s);let l=0;for(let c=0,f=t.length;c<f;c++)l=Math.max(l,s.distanceToSquared(t[c]));return this.radius=Math.sqrt(l),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const n=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=n*n}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,n){const s=this.center.distanceToSquared(t);return n.copy(t),s>this.radius*this.radius&&(n.sub(this.center).normalize(),n.multiplyScalar(this.radius).add(this.center)),n}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Vl.subVectors(t,this.center);const n=Vl.lengthSq();if(n>this.radius*this.radius){const s=Math.sqrt(n),l=(s-this.radius)*.5;this.center.addScaledVector(Vl,l/s),this.radius+=l}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(Bh.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Vl.copy(t.center).add(Bh)),this.expandByPoint(Vl.copy(t.center).sub(Bh))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ma=new W,Fh=new W,Uu=new W,fs=new W,Hh=new W,Lu=new W,Gh=new W;class DT{constructor(t=new W,n=new W(0,0,-1)){this.origin=t,this.direction=n}set(t,n){return this.origin.copy(t),this.direction.copy(n),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,n){return n.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,Ma)),this}closestPointToPoint(t,n){n.subVectors(t,this.origin);const s=n.dot(this.direction);return s<0?n.copy(this.origin):n.copy(this.origin).addScaledVector(this.direction,s)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const n=Ma.subVectors(t,this.origin).dot(this.direction);return n<0?this.origin.distanceToSquared(t):(Ma.copy(this.origin).addScaledVector(this.direction,n),Ma.distanceToSquared(t))}distanceSqToSegment(t,n,s,l){Fh.copy(t).add(n).multiplyScalar(.5),Uu.copy(n).sub(t).normalize(),fs.copy(this.origin).sub(Fh);const c=t.distanceTo(n)*.5,f=-this.direction.dot(Uu),d=fs.dot(this.direction),p=-fs.dot(Uu),m=fs.lengthSq(),g=Math.abs(1-f*f);let _,y,S,b;if(g>0)if(_=f*p-d,y=f*d-p,b=c*g,_>=0)if(y>=-b)if(y<=b){const T=1/g;_*=T,y*=T,S=_*(_+f*y+2*d)+y*(f*_+y+2*p)+m}else y=c,_=Math.max(0,-(f*y+d)),S=-_*_+y*(y+2*p)+m;else y=-c,_=Math.max(0,-(f*y+d)),S=-_*_+y*(y+2*p)+m;else y<=-b?(_=Math.max(0,-(-f*c+d)),y=_>0?-c:Math.min(Math.max(-c,-p),c),S=-_*_+y*(y+2*p)+m):y<=b?(_=0,y=Math.min(Math.max(-c,-p),c),S=y*(y+2*p)+m):(_=Math.max(0,-(f*c+d)),y=_>0?c:Math.min(Math.max(-c,-p),c),S=-_*_+y*(y+2*p)+m);else y=f>0?-c:c,_=Math.max(0,-(f*y+d)),S=-_*_+y*(y+2*p)+m;return s&&s.copy(this.origin).addScaledVector(this.direction,_),l&&l.copy(Fh).addScaledVector(Uu,y),S}intersectSphere(t,n){Ma.subVectors(t.center,this.origin);const s=Ma.dot(this.direction),l=Ma.dot(Ma)-s*s,c=t.radius*t.radius;if(l>c)return null;const f=Math.sqrt(c-l),d=s-f,p=s+f;return p<0?null:d<0?this.at(p,n):this.at(d,n)}intersectsSphere(t){return this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const n=t.normal.dot(this.direction);if(n===0)return t.distanceToPoint(this.origin)===0?0:null;const s=-(this.origin.dot(t.normal)+t.constant)/n;return s>=0?s:null}intersectPlane(t,n){const s=this.distanceToPlane(t);return s===null?null:this.at(s,n)}intersectsPlane(t){const n=t.distanceToPoint(this.origin);return n===0||t.normal.dot(this.direction)*n<0}intersectBox(t,n){let s,l,c,f,d,p;const m=1/this.direction.x,g=1/this.direction.y,_=1/this.direction.z,y=this.origin;return m>=0?(s=(t.min.x-y.x)*m,l=(t.max.x-y.x)*m):(s=(t.max.x-y.x)*m,l=(t.min.x-y.x)*m),g>=0?(c=(t.min.y-y.y)*g,f=(t.max.y-y.y)*g):(c=(t.max.y-y.y)*g,f=(t.min.y-y.y)*g),s>f||c>l||((c>s||isNaN(s))&&(s=c),(f<l||isNaN(l))&&(l=f),_>=0?(d=(t.min.z-y.z)*_,p=(t.max.z-y.z)*_):(d=(t.max.z-y.z)*_,p=(t.min.z-y.z)*_),s>p||d>l)||((d>s||s!==s)&&(s=d),(p<l||l!==l)&&(l=p),l<0)?null:this.at(s>=0?s:l,n)}intersectsBox(t){return this.intersectBox(t,Ma)!==null}intersectTriangle(t,n,s,l,c){Hh.subVectors(n,t),Lu.subVectors(s,t),Gh.crossVectors(Hh,Lu);let f=this.direction.dot(Gh),d;if(f>0){if(l)return null;d=1}else if(f<0)d=-1,f=-f;else return null;fs.subVectors(this.origin,t);const p=d*this.direction.dot(Lu.crossVectors(fs,Lu));if(p<0)return null;const m=d*this.direction.dot(Hh.cross(fs));if(m<0||p+m>f)return null;const g=-d*fs.dot(Gh);return g<0?null:this.at(g/f,c)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class an{constructor(t,n,s,l,c,f,d,p,m,g,_,y,S,b,T,E){an.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,n,s,l,c,f,d,p,m,g,_,y,S,b,T,E)}set(t,n,s,l,c,f,d,p,m,g,_,y,S,b,T,E){const x=this.elements;return x[0]=t,x[4]=n,x[8]=s,x[12]=l,x[1]=c,x[5]=f,x[9]=d,x[13]=p,x[2]=m,x[6]=g,x[10]=_,x[14]=y,x[3]=S,x[7]=b,x[11]=T,x[15]=E,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new an().fromArray(this.elements)}copy(t){const n=this.elements,s=t.elements;return n[0]=s[0],n[1]=s[1],n[2]=s[2],n[3]=s[3],n[4]=s[4],n[5]=s[5],n[6]=s[6],n[7]=s[7],n[8]=s[8],n[9]=s[9],n[10]=s[10],n[11]=s[11],n[12]=s[12],n[13]=s[13],n[14]=s[14],n[15]=s[15],this}copyPosition(t){const n=this.elements,s=t.elements;return n[12]=s[12],n[13]=s[13],n[14]=s[14],this}setFromMatrix3(t){const n=t.elements;return this.set(n[0],n[3],n[6],0,n[1],n[4],n[7],0,n[2],n[5],n[8],0,0,0,0,1),this}extractBasis(t,n,s){return t.setFromMatrixColumn(this,0),n.setFromMatrixColumn(this,1),s.setFromMatrixColumn(this,2),this}makeBasis(t,n,s){return this.set(t.x,n.x,s.x,0,t.y,n.y,s.y,0,t.z,n.z,s.z,0,0,0,0,1),this}extractRotation(t){const n=this.elements,s=t.elements,l=1/ro.setFromMatrixColumn(t,0).length(),c=1/ro.setFromMatrixColumn(t,1).length(),f=1/ro.setFromMatrixColumn(t,2).length();return n[0]=s[0]*l,n[1]=s[1]*l,n[2]=s[2]*l,n[3]=0,n[4]=s[4]*c,n[5]=s[5]*c,n[6]=s[6]*c,n[7]=0,n[8]=s[8]*f,n[9]=s[9]*f,n[10]=s[10]*f,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromEuler(t){const n=this.elements,s=t.x,l=t.y,c=t.z,f=Math.cos(s),d=Math.sin(s),p=Math.cos(l),m=Math.sin(l),g=Math.cos(c),_=Math.sin(c);if(t.order==="XYZ"){const y=f*g,S=f*_,b=d*g,T=d*_;n[0]=p*g,n[4]=-p*_,n[8]=m,n[1]=S+b*m,n[5]=y-T*m,n[9]=-d*p,n[2]=T-y*m,n[6]=b+S*m,n[10]=f*p}else if(t.order==="YXZ"){const y=p*g,S=p*_,b=m*g,T=m*_;n[0]=y+T*d,n[4]=b*d-S,n[8]=f*m,n[1]=f*_,n[5]=f*g,n[9]=-d,n[2]=S*d-b,n[6]=T+y*d,n[10]=f*p}else if(t.order==="ZXY"){const y=p*g,S=p*_,b=m*g,T=m*_;n[0]=y-T*d,n[4]=-f*_,n[8]=b+S*d,n[1]=S+b*d,n[5]=f*g,n[9]=T-y*d,n[2]=-f*m,n[6]=d,n[10]=f*p}else if(t.order==="ZYX"){const y=f*g,S=f*_,b=d*g,T=d*_;n[0]=p*g,n[4]=b*m-S,n[8]=y*m+T,n[1]=p*_,n[5]=T*m+y,n[9]=S*m-b,n[2]=-m,n[6]=d*p,n[10]=f*p}else if(t.order==="YZX"){const y=f*p,S=f*m,b=d*p,T=d*m;n[0]=p*g,n[4]=T-y*_,n[8]=b*_+S,n[1]=_,n[5]=f*g,n[9]=-d*g,n[2]=-m*g,n[6]=S*_+b,n[10]=y-T*_}else if(t.order==="XZY"){const y=f*p,S=f*m,b=d*p,T=d*m;n[0]=p*g,n[4]=-_,n[8]=m*g,n[1]=y*_+T,n[5]=f*g,n[9]=S*_-b,n[2]=b*_-S,n[6]=d*g,n[10]=T*_+y}return n[3]=0,n[7]=0,n[11]=0,n[12]=0,n[13]=0,n[14]=0,n[15]=1,this}makeRotationFromQuaternion(t){return this.compose(NT,t,UT)}lookAt(t,n,s){const l=this.elements;return hi.subVectors(t,n),hi.lengthSq()===0&&(hi.z=1),hi.normalize(),ds.crossVectors(s,hi),ds.lengthSq()===0&&(Math.abs(s.z)===1?hi.x+=1e-4:hi.z+=1e-4,hi.normalize(),ds.crossVectors(s,hi)),ds.normalize(),Ou.crossVectors(hi,ds),l[0]=ds.x,l[4]=Ou.x,l[8]=hi.x,l[1]=ds.y,l[5]=Ou.y,l[9]=hi.y,l[2]=ds.z,l[6]=Ou.z,l[10]=hi.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,n){const s=t.elements,l=n.elements,c=this.elements,f=s[0],d=s[4],p=s[8],m=s[12],g=s[1],_=s[5],y=s[9],S=s[13],b=s[2],T=s[6],E=s[10],x=s[14],P=s[3],N=s[7],R=s[11],V=s[15],F=l[0],z=l[4],G=l[8],U=l[12],D=l[1],H=l[5],ut=l[9],ot=l[13],mt=l[2],ct=l[6],I=l[10],Z=l[14],$=l[3],Et=l[7],At=l[11],O=l[15];return c[0]=f*F+d*D+p*mt+m*$,c[4]=f*z+d*H+p*ct+m*Et,c[8]=f*G+d*ut+p*I+m*At,c[12]=f*U+d*ot+p*Z+m*O,c[1]=g*F+_*D+y*mt+S*$,c[5]=g*z+_*H+y*ct+S*Et,c[9]=g*G+_*ut+y*I+S*At,c[13]=g*U+_*ot+y*Z+S*O,c[2]=b*F+T*D+E*mt+x*$,c[6]=b*z+T*H+E*ct+x*Et,c[10]=b*G+T*ut+E*I+x*At,c[14]=b*U+T*ot+E*Z+x*O,c[3]=P*F+N*D+R*mt+V*$,c[7]=P*z+N*H+R*ct+V*Et,c[11]=P*G+N*ut+R*I+V*At,c[15]=P*U+N*ot+R*Z+V*O,this}multiplyScalar(t){const n=this.elements;return n[0]*=t,n[4]*=t,n[8]*=t,n[12]*=t,n[1]*=t,n[5]*=t,n[9]*=t,n[13]*=t,n[2]*=t,n[6]*=t,n[10]*=t,n[14]*=t,n[3]*=t,n[7]*=t,n[11]*=t,n[15]*=t,this}determinant(){const t=this.elements,n=t[0],s=t[4],l=t[8],c=t[12],f=t[1],d=t[5],p=t[9],m=t[13],g=t[2],_=t[6],y=t[10],S=t[14],b=t[3],T=t[7],E=t[11],x=t[15];return b*(+c*p*_-l*m*_-c*d*y+s*m*y+l*d*S-s*p*S)+T*(+n*p*S-n*m*y+c*f*y-l*f*S+l*m*g-c*p*g)+E*(+n*m*_-n*d*S-c*f*_+s*f*S+c*d*g-s*m*g)+x*(-l*d*g-n*p*_+n*d*y+l*f*_-s*f*y+s*p*g)}transpose(){const t=this.elements;let n;return n=t[1],t[1]=t[4],t[4]=n,n=t[2],t[2]=t[8],t[8]=n,n=t[6],t[6]=t[9],t[9]=n,n=t[3],t[3]=t[12],t[12]=n,n=t[7],t[7]=t[13],t[13]=n,n=t[11],t[11]=t[14],t[14]=n,this}setPosition(t,n,s){const l=this.elements;return t.isVector3?(l[12]=t.x,l[13]=t.y,l[14]=t.z):(l[12]=t,l[13]=n,l[14]=s),this}invert(){const t=this.elements,n=t[0],s=t[1],l=t[2],c=t[3],f=t[4],d=t[5],p=t[6],m=t[7],g=t[8],_=t[9],y=t[10],S=t[11],b=t[12],T=t[13],E=t[14],x=t[15],P=_*E*m-T*y*m+T*p*S-d*E*S-_*p*x+d*y*x,N=b*y*m-g*E*m-b*p*S+f*E*S+g*p*x-f*y*x,R=g*T*m-b*_*m+b*d*S-f*T*S-g*d*x+f*_*x,V=b*_*p-g*T*p-b*d*y+f*T*y+g*d*E-f*_*E,F=n*P+s*N+l*R+c*V;if(F===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const z=1/F;return t[0]=P*z,t[1]=(T*y*c-_*E*c-T*l*S+s*E*S+_*l*x-s*y*x)*z,t[2]=(d*E*c-T*p*c+T*l*m-s*E*m-d*l*x+s*p*x)*z,t[3]=(_*p*c-d*y*c-_*l*m+s*y*m+d*l*S-s*p*S)*z,t[4]=N*z,t[5]=(g*E*c-b*y*c+b*l*S-n*E*S-g*l*x+n*y*x)*z,t[6]=(b*p*c-f*E*c-b*l*m+n*E*m+f*l*x-n*p*x)*z,t[7]=(f*y*c-g*p*c+g*l*m-n*y*m-f*l*S+n*p*S)*z,t[8]=R*z,t[9]=(b*_*c-g*T*c-b*s*S+n*T*S+g*s*x-n*_*x)*z,t[10]=(f*T*c-b*d*c+b*s*m-n*T*m-f*s*x+n*d*x)*z,t[11]=(g*d*c-f*_*c-g*s*m+n*_*m+f*s*S-n*d*S)*z,t[12]=V*z,t[13]=(g*T*l-b*_*l+b*s*y-n*T*y-g*s*E+n*_*E)*z,t[14]=(b*d*l-f*T*l-b*s*p+n*T*p+f*s*E-n*d*E)*z,t[15]=(f*_*l-g*d*l+g*s*p-n*_*p-f*s*y+n*d*y)*z,this}scale(t){const n=this.elements,s=t.x,l=t.y,c=t.z;return n[0]*=s,n[4]*=l,n[8]*=c,n[1]*=s,n[5]*=l,n[9]*=c,n[2]*=s,n[6]*=l,n[10]*=c,n[3]*=s,n[7]*=l,n[11]*=c,this}getMaxScaleOnAxis(){const t=this.elements,n=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],s=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],l=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(n,s,l))}makeTranslation(t,n,s){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,n,0,0,1,s,0,0,0,1),this}makeRotationX(t){const n=Math.cos(t),s=Math.sin(t);return this.set(1,0,0,0,0,n,-s,0,0,s,n,0,0,0,0,1),this}makeRotationY(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,0,s,0,0,1,0,0,-s,0,n,0,0,0,0,1),this}makeRotationZ(t){const n=Math.cos(t),s=Math.sin(t);return this.set(n,-s,0,0,s,n,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,n){const s=Math.cos(n),l=Math.sin(n),c=1-s,f=t.x,d=t.y,p=t.z,m=c*f,g=c*d;return this.set(m*f+s,m*d-l*p,m*p+l*d,0,m*d+l*p,g*d+s,g*p-l*f,0,m*p-l*d,g*p+l*f,c*p*p+s,0,0,0,0,1),this}makeScale(t,n,s){return this.set(t,0,0,0,0,n,0,0,0,0,s,0,0,0,0,1),this}makeShear(t,n,s,l,c,f){return this.set(1,s,c,0,t,1,f,0,n,l,1,0,0,0,0,1),this}compose(t,n,s){const l=this.elements,c=n._x,f=n._y,d=n._z,p=n._w,m=c+c,g=f+f,_=d+d,y=c*m,S=c*g,b=c*_,T=f*g,E=f*_,x=d*_,P=p*m,N=p*g,R=p*_,V=s.x,F=s.y,z=s.z;return l[0]=(1-(T+x))*V,l[1]=(S+R)*V,l[2]=(b-N)*V,l[3]=0,l[4]=(S-R)*F,l[5]=(1-(y+x))*F,l[6]=(E+P)*F,l[7]=0,l[8]=(b+N)*z,l[9]=(E-P)*z,l[10]=(1-(y+T))*z,l[11]=0,l[12]=t.x,l[13]=t.y,l[14]=t.z,l[15]=1,this}decompose(t,n,s){const l=this.elements;let c=ro.set(l[0],l[1],l[2]).length();const f=ro.set(l[4],l[5],l[6]).length(),d=ro.set(l[8],l[9],l[10]).length();this.determinant()<0&&(c=-c),t.x=l[12],t.y=l[13],t.z=l[14],Pi.copy(this);const m=1/c,g=1/f,_=1/d;return Pi.elements[0]*=m,Pi.elements[1]*=m,Pi.elements[2]*=m,Pi.elements[4]*=g,Pi.elements[5]*=g,Pi.elements[6]*=g,Pi.elements[8]*=_,Pi.elements[9]*=_,Pi.elements[10]*=_,n.setFromRotationMatrix(Pi),s.x=c,s.y=f,s.z=d,this}makePerspective(t,n,s,l,c,f,d=Ua){const p=this.elements,m=2*c/(n-t),g=2*c/(s-l),_=(n+t)/(n-t),y=(s+l)/(s-l);let S,b;if(d===Ua)S=-(f+c)/(f-c),b=-2*f*c/(f-c);else if(d===uf)S=-f/(f-c),b=-f*c/(f-c);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+d);return p[0]=m,p[4]=0,p[8]=_,p[12]=0,p[1]=0,p[5]=g,p[9]=y,p[13]=0,p[2]=0,p[6]=0,p[10]=S,p[14]=b,p[3]=0,p[7]=0,p[11]=-1,p[15]=0,this}makeOrthographic(t,n,s,l,c,f,d=Ua){const p=this.elements,m=1/(n-t),g=1/(s-l),_=1/(f-c),y=(n+t)*m,S=(s+l)*g;let b,T;if(d===Ua)b=(f+c)*_,T=-2*_;else if(d===uf)b=c*_,T=-1*_;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+d);return p[0]=2*m,p[4]=0,p[8]=0,p[12]=-y,p[1]=0,p[5]=2*g,p[9]=0,p[13]=-S,p[2]=0,p[6]=0,p[10]=T,p[14]=-b,p[3]=0,p[7]=0,p[11]=0,p[15]=1,this}equals(t){const n=this.elements,s=t.elements;for(let l=0;l<16;l++)if(n[l]!==s[l])return!1;return!0}fromArray(t,n=0){for(let s=0;s<16;s++)this.elements[s]=t[s+n];return this}toArray(t=[],n=0){const s=this.elements;return t[n]=s[0],t[n+1]=s[1],t[n+2]=s[2],t[n+3]=s[3],t[n+4]=s[4],t[n+5]=s[5],t[n+6]=s[6],t[n+7]=s[7],t[n+8]=s[8],t[n+9]=s[9],t[n+10]=s[10],t[n+11]=s[11],t[n+12]=s[12],t[n+13]=s[13],t[n+14]=s[14],t[n+15]=s[15],t}}const ro=new W,Pi=new an,NT=new W(0,0,0),UT=new W(1,1,1),ds=new W,Ou=new W,hi=new W,$0=new an,ty=new uc;class Ia{constructor(t=0,n=0,s=0,l=Ia.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=n,this._z=s,this._order=l}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,n,s,l=this._order){return this._x=t,this._y=n,this._z=s,this._order=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,n=this._order,s=!0){const l=t.elements,c=l[0],f=l[4],d=l[8],p=l[1],m=l[5],g=l[9],_=l[2],y=l[6],S=l[10];switch(n){case"XYZ":this._y=Math.asin(ge(d,-1,1)),Math.abs(d)<.9999999?(this._x=Math.atan2(-g,S),this._z=Math.atan2(-f,c)):(this._x=Math.atan2(y,m),this._z=0);break;case"YXZ":this._x=Math.asin(-ge(g,-1,1)),Math.abs(g)<.9999999?(this._y=Math.atan2(d,S),this._z=Math.atan2(p,m)):(this._y=Math.atan2(-_,c),this._z=0);break;case"ZXY":this._x=Math.asin(ge(y,-1,1)),Math.abs(y)<.9999999?(this._y=Math.atan2(-_,S),this._z=Math.atan2(-f,m)):(this._y=0,this._z=Math.atan2(p,c));break;case"ZYX":this._y=Math.asin(-ge(_,-1,1)),Math.abs(_)<.9999999?(this._x=Math.atan2(y,S),this._z=Math.atan2(p,c)):(this._x=0,this._z=Math.atan2(-f,m));break;case"YZX":this._z=Math.asin(ge(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-g,m),this._y=Math.atan2(-_,c)):(this._x=0,this._y=Math.atan2(d,S));break;case"XZY":this._z=Math.asin(-ge(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(y,m),this._y=Math.atan2(d,c)):(this._x=Math.atan2(-g,S),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+n)}return this._order=n,s===!0&&this._onChangeCallback(),this}setFromQuaternion(t,n,s){return $0.makeRotationFromQuaternion(t),this.setFromRotationMatrix($0,n,s)}setFromVector3(t,n=this._order){return this.set(t.x,t.y,t.z,n)}reorder(t){return ty.setFromEuler(this),this.setFromQuaternion(ty,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],n=0){return t[n]=this._x,t[n+1]=this._y,t[n+2]=this._z,t[n+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ia.DEFAULT_ORDER="XYZ";class Qx{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let LT=0;const ey=new W,oo=new uc,Ea=new an,Pu=new W,kl=new W,OT=new W,PT=new uc,ny=new W(1,0,0),iy=new W(0,1,0),ay=new W(0,0,1),sy={type:"added"},zT={type:"removed"},lo={type:"childadded",child:null},Vh={type:"childremoved",child:null};class si extends Xo{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:LT++}),this.uuid=qo(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=si.DEFAULT_UP.clone();const t=new W,n=new Ia,s=new uc,l=new W(1,1,1);function c(){s.setFromEuler(n,!1)}function f(){n.setFromQuaternion(s,void 0,!1)}n._onChange(c),s._onChange(f),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:n},quaternion:{configurable:!0,enumerable:!0,value:s},scale:{configurable:!0,enumerable:!0,value:l},modelViewMatrix:{value:new an},normalMatrix:{value:new de}}),this.matrix=new an,this.matrixWorld=new an,this.matrixAutoUpdate=si.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Qx,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,n){this.quaternion.setFromAxisAngle(t,n)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,n){return oo.setFromAxisAngle(t,n),this.quaternion.multiply(oo),this}rotateOnWorldAxis(t,n){return oo.setFromAxisAngle(t,n),this.quaternion.premultiply(oo),this}rotateX(t){return this.rotateOnAxis(ny,t)}rotateY(t){return this.rotateOnAxis(iy,t)}rotateZ(t){return this.rotateOnAxis(ay,t)}translateOnAxis(t,n){return ey.copy(t).applyQuaternion(this.quaternion),this.position.add(ey.multiplyScalar(n)),this}translateX(t){return this.translateOnAxis(ny,t)}translateY(t){return this.translateOnAxis(iy,t)}translateZ(t){return this.translateOnAxis(ay,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(Ea.copy(this.matrixWorld).invert())}lookAt(t,n,s){t.isVector3?Pu.copy(t):Pu.set(t,n,s);const l=this.parent;this.updateWorldMatrix(!0,!1),kl.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ea.lookAt(kl,Pu,this.up):Ea.lookAt(Pu,kl,this.up),this.quaternion.setFromRotationMatrix(Ea),l&&(Ea.extractRotation(l.matrixWorld),oo.setFromRotationMatrix(Ea),this.quaternion.premultiply(oo.invert()))}add(t){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.add(arguments[n]);return this}return t===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(sy),lo.child=t,this.dispatchEvent(lo),lo.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let s=0;s<arguments.length;s++)this.remove(arguments[s]);return this}const n=this.children.indexOf(t);return n!==-1&&(t.parent=null,this.children.splice(n,1),t.dispatchEvent(zT),Vh.child=t,this.dispatchEvent(Vh),Vh.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),Ea.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),Ea.multiply(t.parent.matrixWorld)),t.applyMatrix4(Ea),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(sy),lo.child=t,this.dispatchEvent(lo),lo.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,n){if(this[t]===n)return this;for(let s=0,l=this.children.length;s<l;s++){const f=this.children[s].getObjectByProperty(t,n);if(f!==void 0)return f}}getObjectsByProperty(t,n,s=[]){this[t]===n&&s.push(this);const l=this.children;for(let c=0,f=l.length;c<f;c++)l[c].getObjectsByProperty(t,n,s);return s}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(kl,t,OT),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(kl,PT,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const n=this.matrixWorld.elements;return t.set(n[8],n[9],n[10]).normalize()}raycast(){}traverse(t){t(this);const n=this.children;for(let s=0,l=n.length;s<l;s++)n[s].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const n=this.children;for(let s=0,l=n.length;s<l;s++)n[s].traverseVisible(t)}traverseAncestors(t){const n=this.parent;n!==null&&(t(n),n.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const n=this.children;for(let s=0,l=n.length;s<l;s++)n[s].updateMatrixWorld(t)}updateWorldMatrix(t,n){const s=this.parent;if(t===!0&&s!==null&&s.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),n===!0){const l=this.children;for(let c=0,f=l.length;c<f;c++)l[c].updateWorldMatrix(!1,!0)}}toJSON(t){const n=t===void 0||typeof t=="string",s={};n&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},s.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const l={};l.uuid=this.uuid,l.type=this.type,this.name!==""&&(l.name=this.name),this.castShadow===!0&&(l.castShadow=!0),this.receiveShadow===!0&&(l.receiveShadow=!0),this.visible===!1&&(l.visible=!1),this.frustumCulled===!1&&(l.frustumCulled=!1),this.renderOrder!==0&&(l.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(l.userData=this.userData),l.layers=this.layers.mask,l.matrix=this.matrix.toArray(),l.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(l.matrixAutoUpdate=!1),this.isInstancedMesh&&(l.type="InstancedMesh",l.count=this.count,l.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(l.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(l.type="BatchedMesh",l.perObjectFrustumCulled=this.perObjectFrustumCulled,l.sortObjects=this.sortObjects,l.drawRanges=this._drawRanges,l.reservedRanges=this._reservedRanges,l.visibility=this._visibility,l.active=this._active,l.bounds=this._bounds.map(d=>({boxInitialized:d.boxInitialized,boxMin:d.box.min.toArray(),boxMax:d.box.max.toArray(),sphereInitialized:d.sphereInitialized,sphereRadius:d.sphere.radius,sphereCenter:d.sphere.center.toArray()})),l.maxInstanceCount=this._maxInstanceCount,l.maxVertexCount=this._maxVertexCount,l.maxIndexCount=this._maxIndexCount,l.geometryInitialized=this._geometryInitialized,l.geometryCount=this._geometryCount,l.matricesTexture=this._matricesTexture.toJSON(t),this._colorsTexture!==null&&(l.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(l.boundingSphere={center:l.boundingSphere.center.toArray(),radius:l.boundingSphere.radius}),this.boundingBox!==null&&(l.boundingBox={min:l.boundingBox.min.toArray(),max:l.boundingBox.max.toArray()}));function c(d,p){return d[p.uuid]===void 0&&(d[p.uuid]=p.toJSON(t)),p.uuid}if(this.isScene)this.background&&(this.background.isColor?l.background=this.background.toJSON():this.background.isTexture&&(l.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(l.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){l.geometry=c(t.geometries,this.geometry);const d=this.geometry.parameters;if(d!==void 0&&d.shapes!==void 0){const p=d.shapes;if(Array.isArray(p))for(let m=0,g=p.length;m<g;m++){const _=p[m];c(t.shapes,_)}else c(t.shapes,p)}}if(this.isSkinnedMesh&&(l.bindMode=this.bindMode,l.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(c(t.skeletons,this.skeleton),l.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const d=[];for(let p=0,m=this.material.length;p<m;p++)d.push(c(t.materials,this.material[p]));l.material=d}else l.material=c(t.materials,this.material);if(this.children.length>0){l.children=[];for(let d=0;d<this.children.length;d++)l.children.push(this.children[d].toJSON(t).object)}if(this.animations.length>0){l.animations=[];for(let d=0;d<this.animations.length;d++){const p=this.animations[d];l.animations.push(c(t.animations,p))}}if(n){const d=f(t.geometries),p=f(t.materials),m=f(t.textures),g=f(t.images),_=f(t.shapes),y=f(t.skeletons),S=f(t.animations),b=f(t.nodes);d.length>0&&(s.geometries=d),p.length>0&&(s.materials=p),m.length>0&&(s.textures=m),g.length>0&&(s.images=g),_.length>0&&(s.shapes=_),y.length>0&&(s.skeletons=y),S.length>0&&(s.animations=S),b.length>0&&(s.nodes=b)}return s.object=l,s;function f(d){const p=[];for(const m in d){const g=d[m];delete g.metadata,p.push(g)}return p}}clone(t){return new this.constructor().copy(this,t)}copy(t,n=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),n===!0)for(let s=0;s<t.children.length;s++){const l=t.children[s];this.add(l.clone())}return this}}si.DEFAULT_UP=new W(0,1,0);si.DEFAULT_MATRIX_AUTO_UPDATE=!0;si.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const zi=new W,ba=new W,kh=new W,Ta=new W,co=new W,uo=new W,ry=new W,jh=new W,Xh=new W,qh=new W,Wh=new We,Yh=new We,Qh=new We;class Bi{constructor(t=new W,n=new W,s=new W){this.a=t,this.b=n,this.c=s}static getNormal(t,n,s,l){l.subVectors(s,n),zi.subVectors(t,n),l.cross(zi);const c=l.lengthSq();return c>0?l.multiplyScalar(1/Math.sqrt(c)):l.set(0,0,0)}static getBarycoord(t,n,s,l,c){zi.subVectors(l,n),ba.subVectors(s,n),kh.subVectors(t,n);const f=zi.dot(zi),d=zi.dot(ba),p=zi.dot(kh),m=ba.dot(ba),g=ba.dot(kh),_=f*m-d*d;if(_===0)return c.set(0,0,0),null;const y=1/_,S=(m*p-d*g)*y,b=(f*g-d*p)*y;return c.set(1-S-b,b,S)}static containsPoint(t,n,s,l){return this.getBarycoord(t,n,s,l,Ta)===null?!1:Ta.x>=0&&Ta.y>=0&&Ta.x+Ta.y<=1}static getInterpolation(t,n,s,l,c,f,d,p){return this.getBarycoord(t,n,s,l,Ta)===null?(p.x=0,p.y=0,"z"in p&&(p.z=0),"w"in p&&(p.w=0),null):(p.setScalar(0),p.addScaledVector(c,Ta.x),p.addScaledVector(f,Ta.y),p.addScaledVector(d,Ta.z),p)}static getInterpolatedAttribute(t,n,s,l,c,f){return Wh.setScalar(0),Yh.setScalar(0),Qh.setScalar(0),Wh.fromBufferAttribute(t,n),Yh.fromBufferAttribute(t,s),Qh.fromBufferAttribute(t,l),f.setScalar(0),f.addScaledVector(Wh,c.x),f.addScaledVector(Yh,c.y),f.addScaledVector(Qh,c.z),f}static isFrontFacing(t,n,s,l){return zi.subVectors(s,n),ba.subVectors(t,n),zi.cross(ba).dot(l)<0}set(t,n,s){return this.a.copy(t),this.b.copy(n),this.c.copy(s),this}setFromPointsAndIndices(t,n,s,l){return this.a.copy(t[n]),this.b.copy(t[s]),this.c.copy(t[l]),this}setFromAttributeAndIndices(t,n,s,l){return this.a.fromBufferAttribute(t,n),this.b.fromBufferAttribute(t,s),this.c.fromBufferAttribute(t,l),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return zi.subVectors(this.c,this.b),ba.subVectors(this.a,this.b),zi.cross(ba).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return Bi.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,n){return Bi.getBarycoord(t,this.a,this.b,this.c,n)}getInterpolation(t,n,s,l,c){return Bi.getInterpolation(t,this.a,this.b,this.c,n,s,l,c)}containsPoint(t){return Bi.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return Bi.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,n){const s=this.a,l=this.b,c=this.c;let f,d;co.subVectors(l,s),uo.subVectors(c,s),jh.subVectors(t,s);const p=co.dot(jh),m=uo.dot(jh);if(p<=0&&m<=0)return n.copy(s);Xh.subVectors(t,l);const g=co.dot(Xh),_=uo.dot(Xh);if(g>=0&&_<=g)return n.copy(l);const y=p*_-g*m;if(y<=0&&p>=0&&g<=0)return f=p/(p-g),n.copy(s).addScaledVector(co,f);qh.subVectors(t,c);const S=co.dot(qh),b=uo.dot(qh);if(b>=0&&S<=b)return n.copy(c);const T=S*m-p*b;if(T<=0&&m>=0&&b<=0)return d=m/(m-b),n.copy(s).addScaledVector(uo,d);const E=g*b-S*_;if(E<=0&&_-g>=0&&S-b>=0)return ry.subVectors(c,l),d=(_-g)/(_-g+(S-b)),n.copy(l).addScaledVector(ry,d);const x=1/(E+T+y);return f=T*x,d=y*x,n.copy(s).addScaledVector(co,f).addScaledVector(uo,d)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}const Zx={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},hs={h:0,s:0,l:0},zu={h:0,s:0,l:0};function Zh(a,t,n){return n<0&&(n+=1),n>1&&(n-=1),n<1/6?a+(t-a)*6*n:n<1/2?t:n<2/3?a+(t-a)*6*(2/3-n):a}class pe{constructor(t,n,s){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,n,s)}set(t,n,s){if(n===void 0&&s===void 0){const l=t;l&&l.isColor?this.copy(l):typeof l=="number"?this.setHex(l):typeof l=="string"&&this.setStyle(l)}else this.setRGB(t,n,s);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,n=vi){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Oe.toWorkingColorSpace(this,n),this}setRGB(t,n,s,l=Oe.workingColorSpace){return this.r=t,this.g=n,this.b=s,Oe.toWorkingColorSpace(this,l),this}setHSL(t,n,s,l=Oe.workingColorSpace){if(t=Nm(t,1),n=ge(n,0,1),s=ge(s,0,1),n===0)this.r=this.g=this.b=s;else{const c=s<=.5?s*(1+n):s+n-s*n,f=2*s-c;this.r=Zh(f,c,t+1/3),this.g=Zh(f,c,t),this.b=Zh(f,c,t-1/3)}return Oe.toWorkingColorSpace(this,l),this}setStyle(t,n=vi){function s(c){c!==void 0&&parseFloat(c)<1&&console.warn("THREE.Color: Alpha component of "+t+" will be ignored.")}let l;if(l=/^(\w+)\(([^\)]*)\)/.exec(t)){let c;const f=l[1],d=l[2];switch(f){case"rgb":case"rgba":if(c=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(255,parseInt(c[1],10))/255,Math.min(255,parseInt(c[2],10))/255,Math.min(255,parseInt(c[3],10))/255,n);if(c=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setRGB(Math.min(100,parseInt(c[1],10))/100,Math.min(100,parseInt(c[2],10))/100,Math.min(100,parseInt(c[3],10))/100,n);break;case"hsl":case"hsla":if(c=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(d))return s(c[4]),this.setHSL(parseFloat(c[1])/360,parseFloat(c[2])/100,parseFloat(c[3])/100,n);break;default:console.warn("THREE.Color: Unknown color model "+t)}}else if(l=/^\#([A-Fa-f\d]+)$/.exec(t)){const c=l[1],f=c.length;if(f===3)return this.setRGB(parseInt(c.charAt(0),16)/15,parseInt(c.charAt(1),16)/15,parseInt(c.charAt(2),16)/15,n);if(f===6)return this.setHex(parseInt(c,16),n);console.warn("THREE.Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,n);return this}setColorName(t,n=vi){const s=Zx[t.toLowerCase()];return s!==void 0?this.setHex(s,n):console.warn("THREE.Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=Pa(t.r),this.g=Pa(t.g),this.b=Pa(t.b),this}copyLinearToSRGB(t){return this.r=Mo(t.r),this.g=Mo(t.g),this.b=Mo(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=vi){return Oe.fromWorkingColorSpace(Fn.copy(this),t),Math.round(ge(Fn.r*255,0,255))*65536+Math.round(ge(Fn.g*255,0,255))*256+Math.round(ge(Fn.b*255,0,255))}getHexString(t=vi){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,n=Oe.workingColorSpace){Oe.fromWorkingColorSpace(Fn.copy(this),n);const s=Fn.r,l=Fn.g,c=Fn.b,f=Math.max(s,l,c),d=Math.min(s,l,c);let p,m;const g=(d+f)/2;if(d===f)p=0,m=0;else{const _=f-d;switch(m=g<=.5?_/(f+d):_/(2-f-d),f){case s:p=(l-c)/_+(l<c?6:0);break;case l:p=(c-s)/_+2;break;case c:p=(s-l)/_+4;break}p/=6}return t.h=p,t.s=m,t.l=g,t}getRGB(t,n=Oe.workingColorSpace){return Oe.fromWorkingColorSpace(Fn.copy(this),n),t.r=Fn.r,t.g=Fn.g,t.b=Fn.b,t}getStyle(t=vi){Oe.fromWorkingColorSpace(Fn.copy(this),t);const n=Fn.r,s=Fn.g,l=Fn.b;return t!==vi?`color(${t} ${n.toFixed(3)} ${s.toFixed(3)} ${l.toFixed(3)})`:`rgb(${Math.round(n*255)},${Math.round(s*255)},${Math.round(l*255)})`}offsetHSL(t,n,s){return this.getHSL(hs),this.setHSL(hs.h+t,hs.s+n,hs.l+s)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,n){return this.r=t.r+n.r,this.g=t.g+n.g,this.b=t.b+n.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,n){return this.r+=(t.r-this.r)*n,this.g+=(t.g-this.g)*n,this.b+=(t.b-this.b)*n,this}lerpColors(t,n,s){return this.r=t.r+(n.r-t.r)*s,this.g=t.g+(n.g-t.g)*s,this.b=t.b+(n.b-t.b)*s,this}lerpHSL(t,n){this.getHSL(hs),t.getHSL(zu);const s=Zl(hs.h,zu.h,n),l=Zl(hs.s,zu.s,n),c=Zl(hs.l,zu.l,n);return this.setHSL(s,l,c),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const n=this.r,s=this.g,l=this.b,c=t.elements;return this.r=c[0]*n+c[3]*s+c[6]*l,this.g=c[1]*n+c[4]*s+c[7]*l,this.b=c[2]*n+c[5]*s+c[8]*l,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,n=0){return this.r=t[n],this.g=t[n+1],this.b=t[n+2],this}toArray(t=[],n=0){return t[n]=this.r,t[n+1]=this.g,t[n+2]=this.b,t}fromBufferAttribute(t,n){return this.r=t.getX(n),this.g=t.getY(n),this.b=t.getZ(n),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Fn=new pe;pe.NAMES=Zx;let IT=0;class mf extends Xo{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:IT++}),this.uuid=qo(),this.name="",this.type="Material",this.blending=xo,this.side=Rs,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Rp,this.blendDst=wp,this.blendEquation=ar,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new pe(0,0,0),this.blendAlpha=0,this.depthFunc=Io,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=X0,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=eo,this.stencilZFail=eo,this.stencilZPass=eo,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const n in t){const s=t[n];if(s===void 0){console.warn(`THREE.Material: parameter '${n}' has value of undefined.`);continue}const l=this[n];if(l===void 0){console.warn(`THREE.Material: '${n}' is not a property of THREE.${this.type}.`);continue}l&&l.isColor?l.set(s):l&&l.isVector3&&s&&s.isVector3?l.copy(s):this[n]=s}}toJSON(t){const n=t===void 0||typeof t=="string";n&&(t={textures:{},images:{}});const s={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.color&&this.color.isColor&&(s.color=this.color.getHex()),this.roughness!==void 0&&(s.roughness=this.roughness),this.metalness!==void 0&&(s.metalness=this.metalness),this.sheen!==void 0&&(s.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(s.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(s.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(s.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(s.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(s.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(s.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(s.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(s.shininess=this.shininess),this.clearcoat!==void 0&&(s.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(s.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(s.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(s.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(s.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,s.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(s.dispersion=this.dispersion),this.iridescence!==void 0&&(s.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(s.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(s.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(s.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(s.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(s.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(s.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(s.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(s.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(s.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(s.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(s.lightMap=this.lightMap.toJSON(t).uuid,s.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(s.aoMap=this.aoMap.toJSON(t).uuid,s.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(s.bumpMap=this.bumpMap.toJSON(t).uuid,s.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(s.normalMap=this.normalMap.toJSON(t).uuid,s.normalMapType=this.normalMapType,s.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(s.displacementMap=this.displacementMap.toJSON(t).uuid,s.displacementScale=this.displacementScale,s.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(s.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(s.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(s.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(s.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(s.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(s.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(s.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(s.combine=this.combine)),this.envMapRotation!==void 0&&(s.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(s.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(s.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(s.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(s.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(s.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(s.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(s.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(s.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(s.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(s.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(s.size=this.size),this.shadowSide!==null&&(s.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(s.sizeAttenuation=this.sizeAttenuation),this.blending!==xo&&(s.blending=this.blending),this.side!==Rs&&(s.side=this.side),this.vertexColors===!0&&(s.vertexColors=!0),this.opacity<1&&(s.opacity=this.opacity),this.transparent===!0&&(s.transparent=!0),this.blendSrc!==Rp&&(s.blendSrc=this.blendSrc),this.blendDst!==wp&&(s.blendDst=this.blendDst),this.blendEquation!==ar&&(s.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(s.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(s.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(s.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(s.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(s.blendAlpha=this.blendAlpha),this.depthFunc!==Io&&(s.depthFunc=this.depthFunc),this.depthTest===!1&&(s.depthTest=this.depthTest),this.depthWrite===!1&&(s.depthWrite=this.depthWrite),this.colorWrite===!1&&(s.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(s.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==X0&&(s.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(s.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(s.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==eo&&(s.stencilFail=this.stencilFail),this.stencilZFail!==eo&&(s.stencilZFail=this.stencilZFail),this.stencilZPass!==eo&&(s.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(s.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(s.rotation=this.rotation),this.polygonOffset===!0&&(s.polygonOffset=!0),this.polygonOffsetFactor!==0&&(s.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(s.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(s.linewidth=this.linewidth),this.dashSize!==void 0&&(s.dashSize=this.dashSize),this.gapSize!==void 0&&(s.gapSize=this.gapSize),this.scale!==void 0&&(s.scale=this.scale),this.dithering===!0&&(s.dithering=!0),this.alphaTest>0&&(s.alphaTest=this.alphaTest),this.alphaHash===!0&&(s.alphaHash=!0),this.alphaToCoverage===!0&&(s.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(s.premultipliedAlpha=!0),this.forceSinglePass===!0&&(s.forceSinglePass=!0),this.wireframe===!0&&(s.wireframe=!0),this.wireframeLinewidth>1&&(s.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(s.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(s.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(s.flatShading=!0),this.visible===!1&&(s.visible=!1),this.toneMapped===!1&&(s.toneMapped=!1),this.fog===!1&&(s.fog=!1),Object.keys(this.userData).length>0&&(s.userData=this.userData);function l(c){const f=[];for(const d in c){const p=c[d];delete p.metadata,f.push(p)}return f}if(n){const c=l(t.textures),f=l(t.images);c.length>0&&(s.textures=c),f.length>0&&(s.images=f)}return s}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const n=t.clippingPlanes;let s=null;if(n!==null){const l=n.length;s=new Array(l);for(let c=0;c!==l;++c)s[c]=n[c].clone()}return this.clippingPlanes=s,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class xr extends mf{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new pe(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ia,this.combine=Lx,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const vn=new W,Iu=new Wt;class ea{constructor(t,n,s=!1){if(Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=t,this.itemSize=n,this.count=t!==void 0?t.length/n:0,this.normalized=s,this.usage=q0,this.updateRanges=[],this.gpuType=Na,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,n){this.updateRanges.push({start:t,count:n})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,n,s){t*=this.itemSize,s*=n.itemSize;for(let l=0,c=this.itemSize;l<c;l++)this.array[t+l]=n.array[s+l];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let n=0,s=this.count;n<s;n++)Iu.fromBufferAttribute(this,n),Iu.applyMatrix3(t),this.setXY(n,Iu.x,Iu.y);else if(this.itemSize===3)for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix3(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyMatrix4(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyMatrix4(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}applyNormalMatrix(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.applyNormalMatrix(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}transformDirection(t){for(let n=0,s=this.count;n<s;n++)vn.fromBufferAttribute(this,n),vn.transformDirection(t),this.setXYZ(n,vn.x,vn.y,vn.z);return this}set(t,n=0){return this.array.set(t,n),this}getComponent(t,n){let s=this.array[t*this.itemSize+n];return this.normalized&&(s=go(s,this.array)),s}setComponent(t,n,s){return this.normalized&&(s=jn(s,this.array)),this.array[t*this.itemSize+n]=s,this}getX(t){let n=this.array[t*this.itemSize];return this.normalized&&(n=go(n,this.array)),n}setX(t,n){return this.normalized&&(n=jn(n,this.array)),this.array[t*this.itemSize]=n,this}getY(t){let n=this.array[t*this.itemSize+1];return this.normalized&&(n=go(n,this.array)),n}setY(t,n){return this.normalized&&(n=jn(n,this.array)),this.array[t*this.itemSize+1]=n,this}getZ(t){let n=this.array[t*this.itemSize+2];return this.normalized&&(n=go(n,this.array)),n}setZ(t,n){return this.normalized&&(n=jn(n,this.array)),this.array[t*this.itemSize+2]=n,this}getW(t){let n=this.array[t*this.itemSize+3];return this.normalized&&(n=go(n,this.array)),n}setW(t,n){return this.normalized&&(n=jn(n,this.array)),this.array[t*this.itemSize+3]=n,this}setXY(t,n,s){return t*=this.itemSize,this.normalized&&(n=jn(n,this.array),s=jn(s,this.array)),this.array[t+0]=n,this.array[t+1]=s,this}setXYZ(t,n,s,l){return t*=this.itemSize,this.normalized&&(n=jn(n,this.array),s=jn(s,this.array),l=jn(l,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=l,this}setXYZW(t,n,s,l,c){return t*=this.itemSize,this.normalized&&(n=jn(n,this.array),s=jn(s,this.array),l=jn(l,this.array),c=jn(c,this.array)),this.array[t+0]=n,this.array[t+1]=s,this.array[t+2]=l,this.array[t+3]=c,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==q0&&(t.usage=this.usage),t}}class Kx extends ea{constructor(t,n,s){super(new Uint16Array(t),n,s)}}class Jx extends ea{constructor(t,n,s){super(new Uint32Array(t),n,s)}}class Cn extends ea{constructor(t,n,s){super(new Float32Array(t),n,s)}}let BT=0;const Ci=new an,Kh=new si,fo=new W,pi=new fc,jl=new fc,Tn=new W;class ki extends Xo{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:BT++}),this.uuid=qo(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(qx(t)?Jx:Kx)(t,1):this.index=t,this}setIndirect(t){return this.indirect=t,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,n){return this.attributes[t]=n,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,n,s=0){this.groups.push({start:t,count:n,materialIndex:s})}clearGroups(){this.groups=[]}setDrawRange(t,n){this.drawRange.start=t,this.drawRange.count=n}applyMatrix4(t){const n=this.attributes.position;n!==void 0&&(n.applyMatrix4(t),n.needsUpdate=!0);const s=this.attributes.normal;if(s!==void 0){const c=new de().getNormalMatrix(t);s.applyNormalMatrix(c),s.needsUpdate=!0}const l=this.attributes.tangent;return l!==void 0&&(l.transformDirection(t),l.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return Ci.makeRotationFromQuaternion(t),this.applyMatrix4(Ci),this}rotateX(t){return Ci.makeRotationX(t),this.applyMatrix4(Ci),this}rotateY(t){return Ci.makeRotationY(t),this.applyMatrix4(Ci),this}rotateZ(t){return Ci.makeRotationZ(t),this.applyMatrix4(Ci),this}translate(t,n,s){return Ci.makeTranslation(t,n,s),this.applyMatrix4(Ci),this}scale(t,n,s){return Ci.makeScale(t,n,s),this.applyMatrix4(Ci),this}lookAt(t){return Kh.lookAt(t),Kh.updateMatrix(),this.applyMatrix4(Kh.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(fo).negate(),this.translate(fo.x,fo.y,fo.z),this}setFromPoints(t){const n=this.getAttribute("position");if(n===void 0){const s=[];for(let l=0,c=t.length;l<c;l++){const f=t[l];s.push(f.x,f.y,f.z||0)}this.setAttribute("position",new Cn(s,3))}else{const s=Math.min(t.length,n.count);for(let l=0;l<s;l++){const c=t[l];n.setXYZ(l,c.x,c.y,c.z||0)}t.length>n.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),n.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new fc);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new W(-1/0,-1/0,-1/0),new W(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),n)for(let s=0,l=n.length;s<l;s++){const c=n[s];pi.setFromBufferAttribute(c),this.morphTargetsRelative?(Tn.addVectors(this.boundingBox.min,pi.min),this.boundingBox.expandByPoint(Tn),Tn.addVectors(this.boundingBox.max,pi.max),this.boundingBox.expandByPoint(Tn)):(this.boundingBox.expandByPoint(pi.min),this.boundingBox.expandByPoint(pi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Um);const t=this.attributes.position,n=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new W,1/0);return}if(t){const s=this.boundingSphere.center;if(pi.setFromBufferAttribute(t),n)for(let c=0,f=n.length;c<f;c++){const d=n[c];jl.setFromBufferAttribute(d),this.morphTargetsRelative?(Tn.addVectors(pi.min,jl.min),pi.expandByPoint(Tn),Tn.addVectors(pi.max,jl.max),pi.expandByPoint(Tn)):(pi.expandByPoint(jl.min),pi.expandByPoint(jl.max))}pi.getCenter(s);let l=0;for(let c=0,f=t.count;c<f;c++)Tn.fromBufferAttribute(t,c),l=Math.max(l,s.distanceToSquared(Tn));if(n)for(let c=0,f=n.length;c<f;c++){const d=n[c],p=this.morphTargetsRelative;for(let m=0,g=d.count;m<g;m++)Tn.fromBufferAttribute(d,m),p&&(fo.fromBufferAttribute(t,m),Tn.add(fo)),l=Math.max(l,s.distanceToSquared(Tn))}this.boundingSphere.radius=Math.sqrt(l),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,n=this.attributes;if(t===null||n.position===void 0||n.normal===void 0||n.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const s=n.position,l=n.normal,c=n.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ea(new Float32Array(4*s.count),4));const f=this.getAttribute("tangent"),d=[],p=[];for(let G=0;G<s.count;G++)d[G]=new W,p[G]=new W;const m=new W,g=new W,_=new W,y=new Wt,S=new Wt,b=new Wt,T=new W,E=new W;function x(G,U,D){m.fromBufferAttribute(s,G),g.fromBufferAttribute(s,U),_.fromBufferAttribute(s,D),y.fromBufferAttribute(c,G),S.fromBufferAttribute(c,U),b.fromBufferAttribute(c,D),g.sub(m),_.sub(m),S.sub(y),b.sub(y);const H=1/(S.x*b.y-b.x*S.y);isFinite(H)&&(T.copy(g).multiplyScalar(b.y).addScaledVector(_,-S.y).multiplyScalar(H),E.copy(_).multiplyScalar(S.x).addScaledVector(g,-b.x).multiplyScalar(H),d[G].add(T),d[U].add(T),d[D].add(T),p[G].add(E),p[U].add(E),p[D].add(E))}let P=this.groups;P.length===0&&(P=[{start:0,count:t.count}]);for(let G=0,U=P.length;G<U;++G){const D=P[G],H=D.start,ut=D.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)x(t.getX(ot+0),t.getX(ot+1),t.getX(ot+2))}const N=new W,R=new W,V=new W,F=new W;function z(G){V.fromBufferAttribute(l,G),F.copy(V);const U=d[G];N.copy(U),N.sub(V.multiplyScalar(V.dot(U))).normalize(),R.crossVectors(F,U);const H=R.dot(p[G])<0?-1:1;f.setXYZW(G,N.x,N.y,N.z,H)}for(let G=0,U=P.length;G<U;++G){const D=P[G],H=D.start,ut=D.count;for(let ot=H,mt=H+ut;ot<mt;ot+=3)z(t.getX(ot+0)),z(t.getX(ot+1)),z(t.getX(ot+2))}}computeVertexNormals(){const t=this.index,n=this.getAttribute("position");if(n!==void 0){let s=this.getAttribute("normal");if(s===void 0)s=new ea(new Float32Array(n.count*3),3),this.setAttribute("normal",s);else for(let y=0,S=s.count;y<S;y++)s.setXYZ(y,0,0,0);const l=new W,c=new W,f=new W,d=new W,p=new W,m=new W,g=new W,_=new W;if(t)for(let y=0,S=t.count;y<S;y+=3){const b=t.getX(y+0),T=t.getX(y+1),E=t.getX(y+2);l.fromBufferAttribute(n,b),c.fromBufferAttribute(n,T),f.fromBufferAttribute(n,E),g.subVectors(f,c),_.subVectors(l,c),g.cross(_),d.fromBufferAttribute(s,b),p.fromBufferAttribute(s,T),m.fromBufferAttribute(s,E),d.add(g),p.add(g),m.add(g),s.setXYZ(b,d.x,d.y,d.z),s.setXYZ(T,p.x,p.y,p.z),s.setXYZ(E,m.x,m.y,m.z)}else for(let y=0,S=n.count;y<S;y+=3)l.fromBufferAttribute(n,y+0),c.fromBufferAttribute(n,y+1),f.fromBufferAttribute(n,y+2),g.subVectors(f,c),_.subVectors(l,c),g.cross(_),s.setXYZ(y+0,g.x,g.y,g.z),s.setXYZ(y+1,g.x,g.y,g.z),s.setXYZ(y+2,g.x,g.y,g.z);this.normalizeNormals(),s.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let n=0,s=t.count;n<s;n++)Tn.fromBufferAttribute(t,n),Tn.normalize(),t.setXYZ(n,Tn.x,Tn.y,Tn.z)}toNonIndexed(){function t(d,p){const m=d.array,g=d.itemSize,_=d.normalized,y=new m.constructor(p.length*g);let S=0,b=0;for(let T=0,E=p.length;T<E;T++){d.isInterleavedBufferAttribute?S=p[T]*d.data.stride+d.offset:S=p[T]*g;for(let x=0;x<g;x++)y[b++]=m[S++]}return new ea(y,g,_)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const n=new ki,s=this.index.array,l=this.attributes;for(const d in l){const p=l[d],m=t(p,s);n.setAttribute(d,m)}const c=this.morphAttributes;for(const d in c){const p=[],m=c[d];for(let g=0,_=m.length;g<_;g++){const y=m[g],S=t(y,s);p.push(S)}n.morphAttributes[d]=p}n.morphTargetsRelative=this.morphTargetsRelative;const f=this.groups;for(let d=0,p=f.length;d<p;d++){const m=f[d];n.addGroup(m.start,m.count,m.materialIndex)}return n}toJSON(){const t={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const p=this.parameters;for(const m in p)p[m]!==void 0&&(t[m]=p[m]);return t}t.data={attributes:{}};const n=this.index;n!==null&&(t.data.index={type:n.array.constructor.name,array:Array.prototype.slice.call(n.array)});const s=this.attributes;for(const p in s){const m=s[p];t.data.attributes[p]=m.toJSON(t.data)}const l={};let c=!1;for(const p in this.morphAttributes){const m=this.morphAttributes[p],g=[];for(let _=0,y=m.length;_<y;_++){const S=m[_];g.push(S.toJSON(t.data))}g.length>0&&(l[p]=g,c=!0)}c&&(t.data.morphAttributes=l,t.data.morphTargetsRelative=this.morphTargetsRelative);const f=this.groups;f.length>0&&(t.data.groups=JSON.parse(JSON.stringify(f)));const d=this.boundingSphere;return d!==null&&(t.data.boundingSphere={center:d.center.toArray(),radius:d.radius}),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const n={};this.name=t.name;const s=t.index;s!==null&&this.setIndex(s.clone(n));const l=t.attributes;for(const m in l){const g=l[m];this.setAttribute(m,g.clone(n))}const c=t.morphAttributes;for(const m in c){const g=[],_=c[m];for(let y=0,S=_.length;y<S;y++)g.push(_[y].clone(n));this.morphAttributes[m]=g}this.morphTargetsRelative=t.morphTargetsRelative;const f=t.groups;for(let m=0,g=f.length;m<g;m++){const _=f[m];this.addGroup(_.start,_.count,_.materialIndex)}const d=t.boundingBox;d!==null&&(this.boundingBox=d.clone());const p=t.boundingSphere;return p!==null&&(this.boundingSphere=p.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const oy=new an,Ks=new DT,Bu=new Um,ly=new W,Fu=new W,Hu=new W,Gu=new W,Jh=new W,Vu=new W,cy=new W,ku=new W;class Wn extends si{constructor(t=new ki,n=new xr){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=n,this.updateMorphTargets()}copy(t,n){return super.copy(t,n),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const n=this.geometry.morphAttributes,s=Object.keys(n);if(s.length>0){const l=n[s[0]];if(l!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let c=0,f=l.length;c<f;c++){const d=l[c].name||String(c);this.morphTargetInfluences.push(0),this.morphTargetDictionary[d]=c}}}}getVertexPosition(t,n){const s=this.geometry,l=s.attributes.position,c=s.morphAttributes.position,f=s.morphTargetsRelative;n.fromBufferAttribute(l,t);const d=this.morphTargetInfluences;if(c&&d){Vu.set(0,0,0);for(let p=0,m=c.length;p<m;p++){const g=d[p],_=c[p];g!==0&&(Jh.fromBufferAttribute(_,t),f?Vu.addScaledVector(Jh,g):Vu.addScaledVector(Jh.sub(n),g))}n.add(Vu)}return n}raycast(t,n){const s=this.geometry,l=this.material,c=this.matrixWorld;l!==void 0&&(s.boundingSphere===null&&s.computeBoundingSphere(),Bu.copy(s.boundingSphere),Bu.applyMatrix4(c),Ks.copy(t.ray).recast(t.near),!(Bu.containsPoint(Ks.origin)===!1&&(Ks.intersectSphere(Bu,ly)===null||Ks.origin.distanceToSquared(ly)>(t.far-t.near)**2))&&(oy.copy(c).invert(),Ks.copy(t.ray).applyMatrix4(oy),!(s.boundingBox!==null&&Ks.intersectsBox(s.boundingBox)===!1)&&this._computeIntersections(t,n,Ks)))}_computeIntersections(t,n,s){let l;const c=this.geometry,f=this.material,d=c.index,p=c.attributes.position,m=c.attributes.uv,g=c.attributes.uv1,_=c.attributes.normal,y=c.groups,S=c.drawRange;if(d!==null)if(Array.isArray(f))for(let b=0,T=y.length;b<T;b++){const E=y[b],x=f[E.materialIndex],P=Math.max(E.start,S.start),N=Math.min(d.count,Math.min(E.start+E.count,S.start+S.count));for(let R=P,V=N;R<V;R+=3){const F=d.getX(R),z=d.getX(R+1),G=d.getX(R+2);l=ju(this,x,t,s,m,g,_,F,z,G),l&&(l.faceIndex=Math.floor(R/3),l.face.materialIndex=E.materialIndex,n.push(l))}}else{const b=Math.max(0,S.start),T=Math.min(d.count,S.start+S.count);for(let E=b,x=T;E<x;E+=3){const P=d.getX(E),N=d.getX(E+1),R=d.getX(E+2);l=ju(this,f,t,s,m,g,_,P,N,R),l&&(l.faceIndex=Math.floor(E/3),n.push(l))}}else if(p!==void 0)if(Array.isArray(f))for(let b=0,T=y.length;b<T;b++){const E=y[b],x=f[E.materialIndex],P=Math.max(E.start,S.start),N=Math.min(p.count,Math.min(E.start+E.count,S.start+S.count));for(let R=P,V=N;R<V;R+=3){const F=R,z=R+1,G=R+2;l=ju(this,x,t,s,m,g,_,F,z,G),l&&(l.faceIndex=Math.floor(R/3),l.face.materialIndex=E.materialIndex,n.push(l))}}else{const b=Math.max(0,S.start),T=Math.min(p.count,S.start+S.count);for(let E=b,x=T;E<x;E+=3){const P=E,N=E+1,R=E+2;l=ju(this,f,t,s,m,g,_,P,N,R),l&&(l.faceIndex=Math.floor(E/3),n.push(l))}}}}function FT(a,t,n,s,l,c,f,d){let p;if(t.side===ii?p=s.intersectTriangle(f,c,l,!0,d):p=s.intersectTriangle(l,c,f,t.side===Rs,d),p===null)return null;ku.copy(d),ku.applyMatrix4(a.matrixWorld);const m=n.ray.origin.distanceTo(ku);return m<n.near||m>n.far?null:{distance:m,point:ku.clone(),object:a}}function ju(a,t,n,s,l,c,f,d,p,m){a.getVertexPosition(d,Fu),a.getVertexPosition(p,Hu),a.getVertexPosition(m,Gu);const g=FT(a,t,n,s,Fu,Hu,Gu,cy);if(g){const _=new W;Bi.getBarycoord(cy,Fu,Hu,Gu,_),l&&(g.uv=Bi.getInterpolatedAttribute(l,d,p,m,_,new Wt)),c&&(g.uv1=Bi.getInterpolatedAttribute(c,d,p,m,_,new Wt)),f&&(g.normal=Bi.getInterpolatedAttribute(f,d,p,m,_,new W),g.normal.dot(s.direction)>0&&g.normal.multiplyScalar(-1));const y={a:d,b:p,c:m,normal:new W,materialIndex:0};Bi.getNormal(Fu,Hu,Gu,y.normal),g.face=y,g.barycoord=_}return g}class dc extends ki{constructor(t=1,n=1,s=1,l=1,c=1,f=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:n,depth:s,widthSegments:l,heightSegments:c,depthSegments:f};const d=this;l=Math.floor(l),c=Math.floor(c),f=Math.floor(f);const p=[],m=[],g=[],_=[];let y=0,S=0;b("z","y","x",-1,-1,s,n,t,f,c,0),b("z","y","x",1,-1,s,n,-t,f,c,1),b("x","z","y",1,1,t,s,n,l,f,2),b("x","z","y",1,-1,t,s,-n,l,f,3),b("x","y","z",1,-1,t,n,s,l,c,4),b("x","y","z",-1,-1,t,n,-s,l,c,5),this.setIndex(p),this.setAttribute("position",new Cn(m,3)),this.setAttribute("normal",new Cn(g,3)),this.setAttribute("uv",new Cn(_,2));function b(T,E,x,P,N,R,V,F,z,G,U){const D=R/z,H=V/G,ut=R/2,ot=V/2,mt=F/2,ct=z+1,I=G+1;let Z=0,$=0;const Et=new W;for(let At=0;At<I;At++){const O=At*H-ot;for(let nt=0;nt<ct;nt++){const St=nt*D-ut;Et[T]=St*P,Et[E]=O*N,Et[x]=mt,m.push(Et.x,Et.y,Et.z),Et[T]=0,Et[E]=0,Et[x]=F>0?1:-1,g.push(Et.x,Et.y,Et.z),_.push(nt/z),_.push(1-At/G),Z+=1}}for(let At=0;At<G;At++)for(let O=0;O<z;O++){const nt=y+O+ct*At,St=y+O+ct*(At+1),q=y+(O+1)+ct*(At+1),ft=y+(O+1)+ct*At;p.push(nt,St,ft),p.push(St,q,ft),$+=6}d.addGroup(S,$,U),S+=$,y+=Z}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new dc(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}function ko(a){const t={};for(const n in a){t[n]={};for(const s in a[n]){const l=a[n][s];l&&(l.isColor||l.isMatrix3||l.isMatrix4||l.isVector2||l.isVector3||l.isVector4||l.isTexture||l.isQuaternion)?l.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[n][s]=null):t[n][s]=l.clone():Array.isArray(l)?t[n][s]=l.slice():t[n][s]=l}}return t}function Xn(a){const t={};for(let n=0;n<a.length;n++){const s=ko(a[n]);for(const l in s)t[l]=s[l]}return t}function HT(a){const t=[];for(let n=0;n<a.length;n++)t.push(a[n].clone());return t}function $x(a){const t=a.getRenderTarget();return t===null?a.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Oe.workingColorSpace}const df={clone:ko,merge:Xn};var GT=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,VT=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Yn extends mf{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=GT,this.fragmentShader=VT,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=ko(t.uniforms),this.uniformsGroups=HT(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this}toJSON(t){const n=super.toJSON(t);n.glslVersion=this.glslVersion,n.uniforms={};for(const l in this.uniforms){const f=this.uniforms[l].value;f&&f.isTexture?n.uniforms[l]={type:"t",value:f.toJSON(t).uuid}:f&&f.isColor?n.uniforms[l]={type:"c",value:f.getHex()}:f&&f.isVector2?n.uniforms[l]={type:"v2",value:f.toArray()}:f&&f.isVector3?n.uniforms[l]={type:"v3",value:f.toArray()}:f&&f.isVector4?n.uniforms[l]={type:"v4",value:f.toArray()}:f&&f.isMatrix3?n.uniforms[l]={type:"m3",value:f.toArray()}:f&&f.isMatrix4?n.uniforms[l]={type:"m4",value:f.toArray()}:n.uniforms[l]={value:f}}Object.keys(this.defines).length>0&&(n.defines=this.defines),n.vertexShader=this.vertexShader,n.fragmentShader=this.fragmentShader,n.lights=this.lights,n.clipping=this.clipping;const s={};for(const l in this.extensions)this.extensions[l]===!0&&(s[l]=!0);return Object.keys(s).length>0&&(n.extensions=s),n}}class tS extends si{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new an,this.projectionMatrix=new an,this.projectionMatrixInverse=new an,this.coordinateSystem=Ua}copy(t,n){return super.copy(t,n),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(t,n){super.updateWorldMatrix(t,n),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const ps=new W,uy=new Wt,fy=new Wt;class _i extends tS{constructor(t=50,n=1,s=.1,l=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=s,this.far=l,this.focus=10,this.aspect=n,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const n=.5*this.getFilmHeight()/t;this.fov=ic*2*Math.atan(n),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(Ql*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return ic*2*Math.atan(Math.tan(Ql*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,n,s){ps.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(ps.x,ps.y).multiplyScalar(-t/ps.z),ps.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),s.set(ps.x,ps.y).multiplyScalar(-t/ps.z)}getViewSize(t,n){return this.getViewBounds(t,uy,fy),n.subVectors(fy,uy)}setViewOffset(t,n,s,l,c,f){this.aspect=t/n,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=l,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let n=t*Math.tan(Ql*.5*this.fov)/this.zoom,s=2*n,l=this.aspect*s,c=-.5*l;const f=this.view;if(this.view!==null&&this.view.enabled){const p=f.fullWidth,m=f.fullHeight;c+=f.offsetX*l/p,n-=f.offsetY*s/m,l*=f.width/p,s*=f.height/m}const d=this.filmOffset;d!==0&&(c+=t*d/this.getFilmWidth()),this.projectionMatrix.makePerspective(c,c+l,n,n-s,t,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.fov=this.fov,n.object.zoom=this.zoom,n.object.near=this.near,n.object.far=this.far,n.object.focus=this.focus,n.object.aspect=this.aspect,this.view!==null&&(n.object.view=Object.assign({},this.view)),n.object.filmGauge=this.filmGauge,n.object.filmOffset=this.filmOffset,n}}const ho=-90,po=1;class kT extends si{constructor(t,n,s){super(),this.type="CubeCamera",this.renderTarget=s,this.coordinateSystem=null,this.activeMipmapLevel=0;const l=new _i(ho,po,t,n);l.layers=this.layers,this.add(l);const c=new _i(ho,po,t,n);c.layers=this.layers,this.add(c);const f=new _i(ho,po,t,n);f.layers=this.layers,this.add(f);const d=new _i(ho,po,t,n);d.layers=this.layers,this.add(d);const p=new _i(ho,po,t,n);p.layers=this.layers,this.add(p);const m=new _i(ho,po,t,n);m.layers=this.layers,this.add(m)}updateCoordinateSystem(){const t=this.coordinateSystem,n=this.children.concat(),[s,l,c,f,d,p]=n;for(const m of n)this.remove(m);if(t===Ua)s.up.set(0,1,0),s.lookAt(1,0,0),l.up.set(0,1,0),l.lookAt(-1,0,0),c.up.set(0,0,-1),c.lookAt(0,1,0),f.up.set(0,0,1),f.lookAt(0,-1,0),d.up.set(0,1,0),d.lookAt(0,0,1),p.up.set(0,1,0),p.lookAt(0,0,-1);else if(t===uf)s.up.set(0,-1,0),s.lookAt(-1,0,0),l.up.set(0,-1,0),l.lookAt(1,0,0),c.up.set(0,0,1),c.lookAt(0,1,0),f.up.set(0,0,-1),f.lookAt(0,-1,0),d.up.set(0,-1,0),d.lookAt(0,0,1),p.up.set(0,-1,0),p.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const m of n)this.add(m),m.updateMatrixWorld()}update(t,n){this.parent===null&&this.updateMatrixWorld();const{renderTarget:s,activeMipmapLevel:l}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[c,f,d,p,m,g]=this.children,_=t.getRenderTarget(),y=t.getActiveCubeFace(),S=t.getActiveMipmapLevel(),b=t.xr.enabled;t.xr.enabled=!1;const T=s.texture.generateMipmaps;s.texture.generateMipmaps=!1,t.setRenderTarget(s,0,l),t.render(n,c),t.setRenderTarget(s,1,l),t.render(n,f),t.setRenderTarget(s,2,l),t.render(n,d),t.setRenderTarget(s,3,l),t.render(n,p),t.setRenderTarget(s,4,l),t.render(n,m),s.texture.generateMipmaps=T,t.setRenderTarget(s,5,l),t.render(n,g),t.setRenderTarget(_,y,S),t.xr.enabled=b,s.texture.needsPMREMUpdate=!0}}class eS extends ai{constructor(t,n,s,l,c,f,d,p,m,g){t=t!==void 0?t:[],n=n!==void 0?n:Bo,super(t,n,s,l,c,f,d,p,m,g),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class jT extends Vi{constructor(t=1,n={}){super(t,t,n),this.isWebGLCubeRenderTarget=!0;const s={width:t,height:t,depth:1},l=[s,s,s,s,s,s];this.texture=new eS(l,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=n.generateMipmaps!==void 0?n.generateMipmaps:!1,this.texture.minFilter=n.minFilter!==void 0?n.minFilter:ta}fromEquirectangularTexture(t,n){this.texture.type=n.type,this.texture.colorSpace=n.colorSpace,this.texture.generateMipmaps=n.generateMipmaps,this.texture.minFilter=n.minFilter,this.texture.magFilter=n.magFilter;const s={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},l=new dc(5,5,5),c=new Yn({name:"CubemapFromEquirect",uniforms:ko(s.uniforms),vertexShader:s.vertexShader,fragmentShader:s.fragmentShader,side:ii,blending:La});c.uniforms.tEquirect.value=n;const f=new Wn(l,c),d=n.minFilter;return n.minFilter===cr&&(n.minFilter=ta),new kT(1,10,this).update(t,f),n.minFilter=d,f.geometry.dispose(),f.material.dispose(),this}clear(t,n,s,l){const c=t.getRenderTarget();for(let f=0;f<6;f++)t.setRenderTarget(this,f),t.clear(n,s,l);t.setRenderTarget(c)}}class XT extends si{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ia,this.environmentIntensity=1,this.environmentRotation=new Ia,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,n){return super.copy(t,n),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const n=super.toJSON(t);return this.fog!==null&&(n.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(n.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(n.object.backgroundIntensity=this.backgroundIntensity),n.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(n.object.environmentIntensity=this.environmentIntensity),n.object.environmentRotation=this.environmentRotation.toArray(),n}}const $h=new W,qT=new W,WT=new de;class nr{constructor(t=new W(1,0,0),n=0){this.isPlane=!0,this.normal=t,this.constant=n}set(t,n){return this.normal.copy(t),this.constant=n,this}setComponents(t,n,s,l){return this.normal.set(t,n,s),this.constant=l,this}setFromNormalAndCoplanarPoint(t,n){return this.normal.copy(t),this.constant=-n.dot(this.normal),this}setFromCoplanarPoints(t,n,s){const l=$h.subVectors(s,n).cross(qT.subVectors(t,n)).normalize();return this.setFromNormalAndCoplanarPoint(l,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,n){return n.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,n){const s=t.delta($h),l=this.normal.dot(s);if(l===0)return this.distanceToPoint(t.start)===0?n.copy(t.start):null;const c=-(t.start.dot(this.normal)+this.constant)/l;return c<0||c>1?null:n.copy(t.start).addScaledVector(s,c)}intersectsLine(t){const n=this.distanceToPoint(t.start),s=this.distanceToPoint(t.end);return n<0&&s>0||s<0&&n>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,n){const s=n||WT.getNormalMatrix(t),l=this.coplanarPoint($h).applyMatrix4(t),c=this.normal.applyMatrix3(s).normalize();return this.constant=-l.dot(c),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Js=new Um,Xu=new W;class Lm{constructor(t=new nr,n=new nr,s=new nr,l=new nr,c=new nr,f=new nr){this.planes=[t,n,s,l,c,f]}set(t,n,s,l,c,f){const d=this.planes;return d[0].copy(t),d[1].copy(n),d[2].copy(s),d[3].copy(l),d[4].copy(c),d[5].copy(f),this}copy(t){const n=this.planes;for(let s=0;s<6;s++)n[s].copy(t.planes[s]);return this}setFromProjectionMatrix(t,n=Ua){const s=this.planes,l=t.elements,c=l[0],f=l[1],d=l[2],p=l[3],m=l[4],g=l[5],_=l[6],y=l[7],S=l[8],b=l[9],T=l[10],E=l[11],x=l[12],P=l[13],N=l[14],R=l[15];if(s[0].setComponents(p-c,y-m,E-S,R-x).normalize(),s[1].setComponents(p+c,y+m,E+S,R+x).normalize(),s[2].setComponents(p+f,y+g,E+b,R+P).normalize(),s[3].setComponents(p-f,y-g,E-b,R-P).normalize(),s[4].setComponents(p-d,y-_,E-T,R-N).normalize(),n===Ua)s[5].setComponents(p+d,y+_,E+T,R+N).normalize();else if(n===uf)s[5].setComponents(d,_,T,N).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+n);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),Js.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const n=t.geometry;n.boundingSphere===null&&n.computeBoundingSphere(),Js.copy(n.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(Js)}intersectsSprite(t){return Js.center.set(0,0,0),Js.radius=.7071067811865476,Js.applyMatrix4(t.matrixWorld),this.intersectsSphere(Js)}intersectsSphere(t){const n=this.planes,s=t.center,l=-t.radius;for(let c=0;c<6;c++)if(n[c].distanceToPoint(s)<l)return!1;return!0}intersectsBox(t){const n=this.planes;for(let s=0;s<6;s++){const l=n[s];if(Xu.x=l.normal.x>0?t.max.x:t.min.x,Xu.y=l.normal.y>0?t.max.y:t.min.y,Xu.z=l.normal.z>0?t.max.z:t.min.z,l.distanceToPoint(Xu)<0)return!1}return!0}containsPoint(t){const n=this.planes;for(let s=0;s<6;s++)if(n[s].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class _o extends si{constructor(){super(),this.isGroup=!0,this.type="Group"}}class nS extends ai{constructor(t,n,s,l,c,f,d,p,m,g=So){if(g!==So&&g!==Go)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");s===void 0&&g===So&&(s=yr),s===void 0&&g===Go&&(s=Ho),super(null,l,c,f,d,p,g,s,m),this.isDepthTexture=!0,this.image={width:t,height:n},this.magFilter=d!==void 0?d:Gi,this.minFilter=p!==void 0?p:Gi,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.compareFunction=t.compareFunction,this}toJSON(t){const n=super.toJSON(t);return this.compareFunction!==null&&(n.compareFunction=this.compareFunction),n}}class Ba{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(t,n){const s=this.getUtoTmapping(t);return this.getPoint(s,n)}getPoints(t=5){const n=[];for(let s=0;s<=t;s++)n.push(this.getPoint(s/t));return n}getSpacedPoints(t=5){const n=[];for(let s=0;s<=t;s++)n.push(this.getPointAt(s/t));return n}getLength(){const t=this.getLengths();return t[t.length-1]}getLengths(t=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===t+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const n=[];let s,l=this.getPoint(0),c=0;n.push(0);for(let f=1;f<=t;f++)s=this.getPoint(f/t),c+=s.distanceTo(l),n.push(c),l=s;return this.cacheArcLengths=n,n}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(t,n){const s=this.getLengths();let l=0;const c=s.length;let f;n?f=n:f=t*s[c-1];let d=0,p=c-1,m;for(;d<=p;)if(l=Math.floor(d+(p-d)/2),m=s[l]-f,m<0)d=l+1;else if(m>0)p=l-1;else{p=l;break}if(l=p,s[l]===f)return l/(c-1);const g=s[l],y=s[l+1]-g,S=(f-g)/y;return(l+S)/(c-1)}getTangent(t,n){let l=t-1e-4,c=t+1e-4;l<0&&(l=0),c>1&&(c=1);const f=this.getPoint(l),d=this.getPoint(c),p=n||(f.isVector2?new Wt:new W);return p.copy(d).sub(f).normalize(),p}getTangentAt(t,n){const s=this.getUtoTmapping(t);return this.getTangent(s,n)}computeFrenetFrames(t,n){const s=new W,l=[],c=[],f=[],d=new W,p=new an;for(let S=0;S<=t;S++){const b=S/t;l[S]=this.getTangentAt(b,new W)}c[0]=new W,f[0]=new W;let m=Number.MAX_VALUE;const g=Math.abs(l[0].x),_=Math.abs(l[0].y),y=Math.abs(l[0].z);g<=m&&(m=g,s.set(1,0,0)),_<=m&&(m=_,s.set(0,1,0)),y<=m&&s.set(0,0,1),d.crossVectors(l[0],s).normalize(),c[0].crossVectors(l[0],d),f[0].crossVectors(l[0],c[0]);for(let S=1;S<=t;S++){if(c[S]=c[S-1].clone(),f[S]=f[S-1].clone(),d.crossVectors(l[S-1],l[S]),d.length()>Number.EPSILON){d.normalize();const b=Math.acos(ge(l[S-1].dot(l[S]),-1,1));c[S].applyMatrix4(p.makeRotationAxis(d,b))}f[S].crossVectors(l[S],c[S])}if(n===!0){let S=Math.acos(ge(c[0].dot(c[t]),-1,1));S/=t,l[0].dot(d.crossVectors(c[0],c[t]))>0&&(S=-S);for(let b=1;b<=t;b++)c[b].applyMatrix4(p.makeRotationAxis(l[b],S*b)),f[b].crossVectors(l[b],c[b])}return{tangents:l,normals:c,binormals:f}}clone(){return new this.constructor().copy(this)}copy(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}toJSON(){const t={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return t.arcLengthDivisions=this.arcLengthDivisions,t.type=this.type,t}fromJSON(t){return this.arcLengthDivisions=t.arcLengthDivisions,this}}class iS extends Ba{constructor(t=0,n=0,s=1,l=1,c=0,f=Math.PI*2,d=!1,p=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=t,this.aY=n,this.xRadius=s,this.yRadius=l,this.aStartAngle=c,this.aEndAngle=f,this.aClockwise=d,this.aRotation=p}getPoint(t,n=new Wt){const s=n,l=Math.PI*2;let c=this.aEndAngle-this.aStartAngle;const f=Math.abs(c)<Number.EPSILON;for(;c<0;)c+=l;for(;c>l;)c-=l;c<Number.EPSILON&&(f?c=0:c=l),this.aClockwise===!0&&!f&&(c===l?c=-l:c=c-l);const d=this.aStartAngle+t*c;let p=this.aX+this.xRadius*Math.cos(d),m=this.aY+this.yRadius*Math.sin(d);if(this.aRotation!==0){const g=Math.cos(this.aRotation),_=Math.sin(this.aRotation),y=p-this.aX,S=m-this.aY;p=y*g-S*_+this.aX,m=y*_+S*g+this.aY}return s.set(p,m)}copy(t){return super.copy(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}toJSON(){const t=super.toJSON();return t.aX=this.aX,t.aY=this.aY,t.xRadius=this.xRadius,t.yRadius=this.yRadius,t.aStartAngle=this.aStartAngle,t.aEndAngle=this.aEndAngle,t.aClockwise=this.aClockwise,t.aRotation=this.aRotation,t}fromJSON(t){return super.fromJSON(t),this.aX=t.aX,this.aY=t.aY,this.xRadius=t.xRadius,this.yRadius=t.yRadius,this.aStartAngle=t.aStartAngle,this.aEndAngle=t.aEndAngle,this.aClockwise=t.aClockwise,this.aRotation=t.aRotation,this}}class YT extends iS{constructor(t,n,s,l,c,f){super(t,n,s,s,l,c,f),this.isArcCurve=!0,this.type="ArcCurve"}}function Om(){let a=0,t=0,n=0,s=0;function l(c,f,d,p){a=c,t=d,n=-3*c+3*f-2*d-p,s=2*c-2*f+d+p}return{initCatmullRom:function(c,f,d,p,m){l(f,d,m*(d-c),m*(p-f))},initNonuniformCatmullRom:function(c,f,d,p,m,g,_){let y=(f-c)/m-(d-c)/(m+g)+(d-f)/g,S=(d-f)/g-(p-f)/(g+_)+(p-d)/_;y*=g,S*=g,l(f,d,y,S)},calc:function(c){const f=c*c,d=f*c;return a+t*c+n*f+s*d}}}const qu=new W,tp=new Om,ep=new Om,np=new Om;class aS extends Ba{constructor(t=[],n=!1,s="centripetal",l=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=t,this.closed=n,this.curveType=s,this.tension=l}getPoint(t,n=new W){const s=n,l=this.points,c=l.length,f=(c-(this.closed?0:1))*t;let d=Math.floor(f),p=f-d;this.closed?d+=d>0?0:(Math.floor(Math.abs(d)/c)+1)*c:p===0&&d===c-1&&(d=c-2,p=1);let m,g;this.closed||d>0?m=l[(d-1)%c]:(qu.subVectors(l[0],l[1]).add(l[0]),m=qu);const _=l[d%c],y=l[(d+1)%c];if(this.closed||d+2<c?g=l[(d+2)%c]:(qu.subVectors(l[c-1],l[c-2]).add(l[c-1]),g=qu),this.curveType==="centripetal"||this.curveType==="chordal"){const S=this.curveType==="chordal"?.5:.25;let b=Math.pow(m.distanceToSquared(_),S),T=Math.pow(_.distanceToSquared(y),S),E=Math.pow(y.distanceToSquared(g),S);T<1e-4&&(T=1),b<1e-4&&(b=T),E<1e-4&&(E=T),tp.initNonuniformCatmullRom(m.x,_.x,y.x,g.x,b,T,E),ep.initNonuniformCatmullRom(m.y,_.y,y.y,g.y,b,T,E),np.initNonuniformCatmullRom(m.z,_.z,y.z,g.z,b,T,E)}else this.curveType==="catmullrom"&&(tp.initCatmullRom(m.x,_.x,y.x,g.x,this.tension),ep.initCatmullRom(m.y,_.y,y.y,g.y,this.tension),np.initCatmullRom(m.z,_.z,y.z,g.z,this.tension));return s.set(tp.calc(p),ep.calc(p),np.calc(p)),s}copy(t){super.copy(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const l=t.points[n];this.points.push(l.clone())}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,s=this.points.length;n<s;n++){const l=this.points[n];t.points.push(l.toArray())}return t.closed=this.closed,t.curveType=this.curveType,t.tension=this.tension,t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const l=t.points[n];this.points.push(new W().fromArray(l))}return this.closed=t.closed,this.curveType=t.curveType,this.tension=t.tension,this}}function dy(a,t,n,s,l){const c=(s-t)*.5,f=(l-n)*.5,d=a*a,p=a*d;return(2*n-2*s+c+f)*p+(-3*n+3*s-2*c-f)*d+c*a+n}function QT(a,t){const n=1-a;return n*n*t}function ZT(a,t){return 2*(1-a)*a*t}function KT(a,t){return a*a*t}function Kl(a,t,n,s){return QT(a,t)+ZT(a,n)+KT(a,s)}function JT(a,t){const n=1-a;return n*n*n*t}function $T(a,t){const n=1-a;return 3*n*n*a*t}function tA(a,t){return 3*(1-a)*a*a*t}function eA(a,t){return a*a*a*t}function Jl(a,t,n,s,l){return JT(a,t)+$T(a,n)+tA(a,s)+eA(a,l)}class nA extends Ba{constructor(t=new Wt,n=new Wt,s=new Wt,l=new Wt){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=t,this.v1=n,this.v2=s,this.v3=l}getPoint(t,n=new Wt){const s=n,l=this.v0,c=this.v1,f=this.v2,d=this.v3;return s.set(Jl(t,l.x,c.x,f.x,d.x),Jl(t,l.y,c.y,f.y,d.y)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class iA extends Ba{constructor(t=new W,n=new W,s=new W,l=new W){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=t,this.v1=n,this.v2=s,this.v3=l}getPoint(t,n=new W){const s=n,l=this.v0,c=this.v1,f=this.v2,d=this.v3;return s.set(Jl(t,l.x,c.x,f.x,d.x),Jl(t,l.y,c.y,f.y,d.y),Jl(t,l.z,c.z,f.z,d.z)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this.v3.copy(t.v3),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t.v3=this.v3.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this.v3.fromArray(t.v3),this}}class aA extends Ba{constructor(t=new Wt,n=new Wt){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=t,this.v2=n}getPoint(t,n=new Wt){const s=n;return t===1?s.copy(this.v2):(s.copy(this.v2).sub(this.v1),s.multiplyScalar(t).add(this.v1)),s}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new Wt){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class sA extends Ba{constructor(t=new W,n=new W){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=t,this.v2=n}getPoint(t,n=new W){const s=n;return t===1?s.copy(this.v2):(s.copy(this.v2).sub(this.v1),s.multiplyScalar(t).add(this.v1)),s}getPointAt(t,n){return this.getPoint(t,n)}getTangent(t,n=new W){return n.subVectors(this.v2,this.v1).normalize()}getTangentAt(t,n){return this.getTangent(t,n)}copy(t){return super.copy(t),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class rA extends Ba{constructor(t=new Wt,n=new Wt,s=new Wt){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=t,this.v1=n,this.v2=s}getPoint(t,n=new Wt){const s=n,l=this.v0,c=this.v1,f=this.v2;return s.set(Kl(t,l.x,c.x,f.x),Kl(t,l.y,c.y,f.y)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class sS extends Ba{constructor(t=new W,n=new W,s=new W){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=t,this.v1=n,this.v2=s}getPoint(t,n=new W){const s=n,l=this.v0,c=this.v1,f=this.v2;return s.set(Kl(t,l.x,c.x,f.x),Kl(t,l.y,c.y,f.y),Kl(t,l.z,c.z,f.z)),s}copy(t){return super.copy(t),this.v0.copy(t.v0),this.v1.copy(t.v1),this.v2.copy(t.v2),this}toJSON(){const t=super.toJSON();return t.v0=this.v0.toArray(),t.v1=this.v1.toArray(),t.v2=this.v2.toArray(),t}fromJSON(t){return super.fromJSON(t),this.v0.fromArray(t.v0),this.v1.fromArray(t.v1),this.v2.fromArray(t.v2),this}}class oA extends Ba{constructor(t=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=t}getPoint(t,n=new Wt){const s=n,l=this.points,c=(l.length-1)*t,f=Math.floor(c),d=c-f,p=l[f===0?f:f-1],m=l[f],g=l[f>l.length-2?l.length-1:f+1],_=l[f>l.length-3?l.length-1:f+2];return s.set(dy(d,p.x,m.x,g.x,_.x),dy(d,p.y,m.y,g.y,_.y)),s}copy(t){super.copy(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const l=t.points[n];this.points.push(l.clone())}return this}toJSON(){const t=super.toJSON();t.points=[];for(let n=0,s=this.points.length;n<s;n++){const l=this.points[n];t.points.push(l.toArray())}return t}fromJSON(t){super.fromJSON(t),this.points=[];for(let n=0,s=t.points.length;n<s;n++){const l=t.points[n];this.points.push(new Wt().fromArray(l))}return this}}var lA=Object.freeze({__proto__:null,ArcCurve:YT,CatmullRomCurve3:aS,CubicBezierCurve:nA,CubicBezierCurve3:iA,EllipseCurve:iS,LineCurve:aA,LineCurve3:sA,QuadraticBezierCurve:rA,QuadraticBezierCurve3:sS,SplineCurve:oA});class gf extends ki{constructor(t=1,n=1,s=1,l=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:n,widthSegments:s,heightSegments:l};const c=t/2,f=n/2,d=Math.floor(s),p=Math.floor(l),m=d+1,g=p+1,_=t/d,y=n/p,S=[],b=[],T=[],E=[];for(let x=0;x<g;x++){const P=x*y-f;for(let N=0;N<m;N++){const R=N*_-c;b.push(R,-P,0),T.push(0,0,1),E.push(N/d),E.push(1-x/p)}}for(let x=0;x<p;x++)for(let P=0;P<d;P++){const N=P+m*x,R=P+m*(x+1),V=P+1+m*(x+1),F=P+1+m*x;S.push(N,R,F),S.push(R,V,F)}this.setIndex(S),this.setAttribute("position",new Cn(b,3)),this.setAttribute("normal",new Cn(T,3)),this.setAttribute("uv",new Cn(E,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new gf(t.width,t.height,t.widthSegments,t.heightSegments)}}class vf extends ki{constructor(t=1,n=32,s=16,l=0,c=Math.PI*2,f=0,d=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:t,widthSegments:n,heightSegments:s,phiStart:l,phiLength:c,thetaStart:f,thetaLength:d},n=Math.max(3,Math.floor(n)),s=Math.max(2,Math.floor(s));const p=Math.min(f+d,Math.PI);let m=0;const g=[],_=new W,y=new W,S=[],b=[],T=[],E=[];for(let x=0;x<=s;x++){const P=[],N=x/s;let R=0;x===0&&f===0?R=.5/n:x===s&&p===Math.PI&&(R=-.5/n);for(let V=0;V<=n;V++){const F=V/n;_.x=-t*Math.cos(l+F*c)*Math.sin(f+N*d),_.y=t*Math.cos(f+N*d),_.z=t*Math.sin(l+F*c)*Math.sin(f+N*d),b.push(_.x,_.y,_.z),y.copy(_).normalize(),T.push(y.x,y.y,y.z),E.push(F+R,1-N),P.push(m++)}g.push(P)}for(let x=0;x<s;x++)for(let P=0;P<n;P++){const N=g[x][P+1],R=g[x][P],V=g[x+1][P],F=g[x+1][P+1];(x!==0||f>0)&&S.push(N,R,F),(x!==s-1||p<Math.PI)&&S.push(R,V,F)}this.setIndex(S),this.setAttribute("position",new Cn(b,3)),this.setAttribute("normal",new Cn(T,3)),this.setAttribute("uv",new Cn(E,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new vf(t.radius,t.widthSegments,t.heightSegments,t.phiStart,t.phiLength,t.thetaStart,t.thetaLength)}}class hf extends ki{constructor(t=1,n=.4,s=12,l=48,c=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:t,tube:n,radialSegments:s,tubularSegments:l,arc:c},s=Math.floor(s),l=Math.floor(l);const f=[],d=[],p=[],m=[],g=new W,_=new W,y=new W;for(let S=0;S<=s;S++)for(let b=0;b<=l;b++){const T=b/l*c,E=S/s*Math.PI*2;_.x=(t+n*Math.cos(E))*Math.cos(T),_.y=(t+n*Math.cos(E))*Math.sin(T),_.z=n*Math.sin(E),d.push(_.x,_.y,_.z),g.x=t*Math.cos(T),g.y=t*Math.sin(T),y.subVectors(_,g).normalize(),p.push(y.x,y.y,y.z),m.push(b/l),m.push(S/s)}for(let S=1;S<=s;S++)for(let b=1;b<=l;b++){const T=(l+1)*S+b-1,E=(l+1)*(S-1)+b-1,x=(l+1)*(S-1)+b,P=(l+1)*S+b;f.push(T,E,P),f.push(E,x,P)}this.setIndex(f),this.setAttribute("position",new Cn(d,3)),this.setAttribute("normal",new Cn(p,3)),this.setAttribute("uv",new Cn(m,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new hf(t.radius,t.tube,t.radialSegments,t.tubularSegments,t.arc)}}class Pm extends ki{constructor(t=new sS(new W(-1,-1,0),new W(-1,1,0),new W(1,1,0)),n=64,s=1,l=8,c=!1){super(),this.type="TubeGeometry",this.parameters={path:t,tubularSegments:n,radius:s,radialSegments:l,closed:c};const f=t.computeFrenetFrames(n,c);this.tangents=f.tangents,this.normals=f.normals,this.binormals=f.binormals;const d=new W,p=new W,m=new Wt;let g=new W;const _=[],y=[],S=[],b=[];T(),this.setIndex(b),this.setAttribute("position",new Cn(_,3)),this.setAttribute("normal",new Cn(y,3)),this.setAttribute("uv",new Cn(S,2));function T(){for(let N=0;N<n;N++)E(N);E(c===!1?n:0),P(),x()}function E(N){g=t.getPointAt(N/n,g);const R=f.normals[N],V=f.binormals[N];for(let F=0;F<=l;F++){const z=F/l*Math.PI*2,G=Math.sin(z),U=-Math.cos(z);p.x=U*R.x+G*V.x,p.y=U*R.y+G*V.y,p.z=U*R.z+G*V.z,p.normalize(),y.push(p.x,p.y,p.z),d.x=g.x+s*p.x,d.y=g.y+s*p.y,d.z=g.z+s*p.z,_.push(d.x,d.y,d.z)}}function x(){for(let N=1;N<=n;N++)for(let R=1;R<=l;R++){const V=(l+1)*(N-1)+(R-1),F=(l+1)*N+(R-1),z=(l+1)*N+R,G=(l+1)*(N-1)+R;b.push(V,F,G),b.push(F,z,G)}}function P(){for(let N=0;N<=n;N++)for(let R=0;R<=l;R++)m.x=N/n,m.y=R/l,S.push(m.x,m.y)}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}toJSON(){const t=super.toJSON();return t.path=this.parameters.path.toJSON(),t}static fromJSON(t){return new Pm(new lA[t.path.type]().fromJSON(t.path),t.tubularSegments,t.radius,t.radialSegments,t.closed)}}class cA extends mf{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=qb,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class uA extends mf{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}class rS extends si{constructor(t,n=1){super(),this.isLight=!0,this.type="Light",this.color=new pe(t),this.intensity=n}dispose(){}copy(t,n){return super.copy(t,n),this.color.copy(t.color),this.intensity=t.intensity,this}toJSON(t){const n=super.toJSON(t);return n.object.color=this.color.getHex(),n.object.intensity=this.intensity,this.groundColor!==void 0&&(n.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(n.object.distance=this.distance),this.angle!==void 0&&(n.object.angle=this.angle),this.decay!==void 0&&(n.object.decay=this.decay),this.penumbra!==void 0&&(n.object.penumbra=this.penumbra),this.shadow!==void 0&&(n.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(n.object.target=this.target.uuid),n}}const ip=new an,hy=new W,py=new W;class fA{constructor(t){this.camera=t,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Wt(512,512),this.map=null,this.mapPass=null,this.matrix=new an,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Lm,this._frameExtents=new Wt(1,1),this._viewportCount=1,this._viewports=[new We(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(t){const n=this.camera,s=this.matrix;hy.setFromMatrixPosition(t.matrixWorld),n.position.copy(hy),py.setFromMatrixPosition(t.target.matrixWorld),n.lookAt(py),n.updateMatrixWorld(),ip.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(ip),s.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),s.multiply(ip)}getViewport(t){return this._viewports[t]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(t){return this.camera=t.camera.clone(),this.intensity=t.intensity,this.bias=t.bias,this.radius=t.radius,this.mapSize.copy(t.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const t={};return this.intensity!==1&&(t.intensity=this.intensity),this.bias!==0&&(t.bias=this.bias),this.normalBias!==0&&(t.normalBias=this.normalBias),this.radius!==1&&(t.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(t.mapSize=this.mapSize.toArray()),t.camera=this.camera.toJSON(!1).object,delete t.camera.matrix,t}}const my=new an,Xl=new W,ap=new W;class dA extends fA{constructor(){super(new _i(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Wt(4,2),this._viewportCount=6,this._viewports=[new We(2,1,1,1),new We(0,1,1,1),new We(3,1,1,1),new We(1,1,1,1),new We(3,0,1,1),new We(1,0,1,1)],this._cubeDirections=[new W(1,0,0),new W(-1,0,0),new W(0,0,1),new W(0,0,-1),new W(0,1,0),new W(0,-1,0)],this._cubeUps=[new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,1,0),new W(0,0,1),new W(0,0,-1)]}updateMatrices(t,n=0){const s=this.camera,l=this.matrix,c=t.distance||s.far;c!==s.far&&(s.far=c,s.updateProjectionMatrix()),Xl.setFromMatrixPosition(t.matrixWorld),s.position.copy(Xl),ap.copy(s.position),ap.add(this._cubeDirections[n]),s.up.copy(this._cubeUps[n]),s.lookAt(ap),s.updateMatrixWorld(),l.makeTranslation(-Xl.x,-Xl.y,-Xl.z),my.multiplyMatrices(s.projectionMatrix,s.matrixWorldInverse),this._frustum.setFromProjectionMatrix(my)}}class hA extends rS{constructor(t,n,s=0,l=2){super(t,n),this.isPointLight=!0,this.type="PointLight",this.distance=s,this.decay=l,this.shadow=new dA}get power(){return this.intensity*4*Math.PI}set power(t){this.intensity=t/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(t,n){return super.copy(t,n),this.distance=t.distance,this.decay=t.decay,this.shadow=t.shadow.clone(),this}}class oS extends tS{constructor(t=-1,n=1,s=1,l=-1,c=.1,f=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=n,this.top=s,this.bottom=l,this.near=c,this.far=f,this.updateProjectionMatrix()}copy(t,n){return super.copy(t,n),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,n,s,l,c,f){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=n,this.view.offsetX=s,this.view.offsetY=l,this.view.width=c,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),n=(this.top-this.bottom)/(2*this.zoom),s=(this.right+this.left)/2,l=(this.top+this.bottom)/2;let c=s-t,f=s+t,d=l+n,p=l-n;if(this.view!==null&&this.view.enabled){const m=(this.right-this.left)/this.view.fullWidth/this.zoom,g=(this.top-this.bottom)/this.view.fullHeight/this.zoom;c+=m*this.view.offsetX,f=c+m*this.view.width,d-=g*this.view.offsetY,p=d-g*this.view.height}this.projectionMatrix.makeOrthographic(c,f,d,p,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const n=super.toJSON(t);return n.object.zoom=this.zoom,n.object.left=this.left,n.object.right=this.right,n.object.top=this.top,n.object.bottom=this.bottom,n.object.near=this.near,n.object.far=this.far,this.view!==null&&(n.object.view=Object.assign({},this.view)),n}}class pA extends rS{constructor(t,n){super(t,n),this.isAmbientLight=!0,this.type="AmbientLight"}}class mA extends _i{constructor(t=[]){super(),this.isArrayCamera=!0,this.cameras=t}}class lS{constructor(t=!0){this.autoStart=t,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=gy(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let t=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const n=gy();t=(n-this.oldTime)/1e3,this.oldTime=n,this.elapsedTime+=t}return t}}function gy(){return performance.now()}function vy(a,t,n,s){const l=gA(s);switch(n){case Bx:return a*t;case Hx:return a*t;case Gx:return a*t*2;case Vx:return a*t/l.components*l.byteLength;case Rm:return a*t/l.components*l.byteLength;case kx:return a*t*2/l.components*l.byteLength;case wm:return a*t*2/l.components*l.byteLength;case Fx:return a*t*3/l.components*l.byteLength;case Fi:return a*t*4/l.components*l.byteLength;case Dm:return a*t*4/l.components*l.byteLength;case Ju:case $u:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*8;case tf:case ef:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case Vp:case jp:return Math.max(a,16)*Math.max(t,8)/4;case Gp:case kp:return Math.max(a,8)*Math.max(t,8)/2;case Xp:case qp:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*8;case Wp:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case Yp:return Math.floor((a+3)/4)*Math.floor((t+3)/4)*16;case Qp:return Math.floor((a+4)/5)*Math.floor((t+3)/4)*16;case Zp:return Math.floor((a+4)/5)*Math.floor((t+4)/5)*16;case Kp:return Math.floor((a+5)/6)*Math.floor((t+4)/5)*16;case Jp:return Math.floor((a+5)/6)*Math.floor((t+5)/6)*16;case $p:return Math.floor((a+7)/8)*Math.floor((t+4)/5)*16;case tm:return Math.floor((a+7)/8)*Math.floor((t+5)/6)*16;case em:return Math.floor((a+7)/8)*Math.floor((t+7)/8)*16;case nm:return Math.floor((a+9)/10)*Math.floor((t+4)/5)*16;case im:return Math.floor((a+9)/10)*Math.floor((t+5)/6)*16;case am:return Math.floor((a+9)/10)*Math.floor((t+7)/8)*16;case sm:return Math.floor((a+9)/10)*Math.floor((t+9)/10)*16;case rm:return Math.floor((a+11)/12)*Math.floor((t+9)/10)*16;case om:return Math.floor((a+11)/12)*Math.floor((t+11)/12)*16;case nf:case lm:case cm:return Math.ceil(a/4)*Math.ceil(t/4)*16;case jx:case um:return Math.ceil(a/4)*Math.ceil(t/4)*8;case fm:case dm:return Math.ceil(a/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${n} format.`)}function gA(a){switch(a){case za:case Px:return{byteLength:1,components:1};case nc:case zx:case Oa:return{byteLength:2,components:1};case Am:case Cm:return{byteLength:2,components:4};case yr:case Tm:case Na:return{byteLength:4,components:1};case Ix:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${a}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:bm}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=bm);/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function cS(){let a=null,t=!1,n=null,s=null;function l(c,f){n(c,f),s=a.requestAnimationFrame(l)}return{start:function(){t!==!0&&n!==null&&(s=a.requestAnimationFrame(l),t=!0)},stop:function(){a.cancelAnimationFrame(s),t=!1},setAnimationLoop:function(c){n=c},setContext:function(c){a=c}}}function vA(a){const t=new WeakMap;function n(d,p){const m=d.array,g=d.usage,_=m.byteLength,y=a.createBuffer();a.bindBuffer(p,y),a.bufferData(p,m,g),d.onUploadCallback();let S;if(m instanceof Float32Array)S=a.FLOAT;else if(m instanceof Uint16Array)d.isFloat16BufferAttribute?S=a.HALF_FLOAT:S=a.UNSIGNED_SHORT;else if(m instanceof Int16Array)S=a.SHORT;else if(m instanceof Uint32Array)S=a.UNSIGNED_INT;else if(m instanceof Int32Array)S=a.INT;else if(m instanceof Int8Array)S=a.BYTE;else if(m instanceof Uint8Array)S=a.UNSIGNED_BYTE;else if(m instanceof Uint8ClampedArray)S=a.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+m);return{buffer:y,type:S,bytesPerElement:m.BYTES_PER_ELEMENT,version:d.version,size:_}}function s(d,p,m){const g=p.array,_=p.updateRanges;if(a.bindBuffer(m,d),_.length===0)a.bufferSubData(m,0,g);else{_.sort((S,b)=>S.start-b.start);let y=0;for(let S=1;S<_.length;S++){const b=_[y],T=_[S];T.start<=b.start+b.count+1?b.count=Math.max(b.count,T.start+T.count-b.start):(++y,_[y]=T)}_.length=y+1;for(let S=0,b=_.length;S<b;S++){const T=_[S];a.bufferSubData(m,T.start*g.BYTES_PER_ELEMENT,g,T.start,T.count)}p.clearUpdateRanges()}p.onUploadCallback()}function l(d){return d.isInterleavedBufferAttribute&&(d=d.data),t.get(d)}function c(d){d.isInterleavedBufferAttribute&&(d=d.data);const p=t.get(d);p&&(a.deleteBuffer(p.buffer),t.delete(d))}function f(d,p){if(d.isInterleavedBufferAttribute&&(d=d.data),d.isGLBufferAttribute){const g=t.get(d);(!g||g.version<d.version)&&t.set(d,{buffer:d.buffer,type:d.type,bytesPerElement:d.elementSize,version:d.version});return}const m=t.get(d);if(m===void 0)t.set(d,n(d,p));else if(m.version<d.version){if(m.size!==d.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");s(m.buffer,d,p),m.version=d.version}}return{get:l,remove:c,update:f}}var _A=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,yA=`#ifdef USE_ALPHAHASH
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
#endif`,xA=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,SA=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,MA=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,EA=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,bA=`#ifdef USE_AOMAP
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
#endif`,TA=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,AA=`#ifdef USE_BATCHING
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
#endif`,CA=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,RA=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,wA=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,DA=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,NA=`#ifdef USE_IRIDESCENCE
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
#endif`,UA=`#ifdef USE_BUMPMAP
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
#endif`,LA=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,OA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,PA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,zA=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,IA=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,BA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,FA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,HA=`#if defined( USE_COLOR_ALPHA )
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
#endif`,GA=`#define PI 3.141592653589793
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
} // validated`,VA=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,kA=`vec3 transformedNormal = objectNormal;
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
#endif`,jA=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,XA=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,qA=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,WA=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,YA="gl_FragColor = linearToOutputTexel( gl_FragColor );",QA=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,ZA=`#ifdef USE_ENVMAP
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
#endif`,KA=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,JA=`#ifdef USE_ENVMAP
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
#endif`,$A=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,t2=`#ifdef USE_ENVMAP
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
#endif`,e2=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,n2=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,i2=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,a2=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,s2=`#ifdef USE_GRADIENTMAP
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
}`,r2=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,o2=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,l2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,c2=`uniform bool receiveShadow;
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
#endif`,u2=`#ifdef USE_ENVMAP
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
#endif`,f2=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,d2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,h2=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,p2=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,m2=`PhysicalMaterial material;
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
#endif`,g2=`struct PhysicalMaterial {
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
}`,v2=`
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
#endif`,_2=`#if defined( RE_IndirectDiffuse )
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
#endif`,y2=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,x2=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,S2=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,M2=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,E2=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,b2=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,T2=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,A2=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,C2=`#if defined( USE_POINTS_UV )
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
#endif`,R2=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,w2=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,D2=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,N2=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,U2=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,L2=`#ifdef USE_MORPHTARGETS
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
#endif`,O2=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,P2=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,z2=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,I2=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,B2=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,F2=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,H2=`#ifdef USE_NORMALMAP
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
#endif`,G2=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,V2=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,k2=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,j2=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,X2=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,q2=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,W2=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Y2=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,Q2=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,Z2=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,K2=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,J2=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,$2=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,tC=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,eC=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,nC=`float getShadowMask() {
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
}`,iC=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,aC=`#ifdef USE_SKINNING
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
#endif`,sC=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,rC=`#ifdef USE_SKINNING
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
#endif`,oC=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,lC=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,cC=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,uC=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,fC=`#ifdef USE_TRANSMISSION
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
#endif`,dC=`#ifdef USE_TRANSMISSION
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
#endif`,hC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,pC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,mC=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,gC=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const vC=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,_C=`uniform sampler2D t2D;
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
}`,yC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,xC=`#ifdef ENVMAP_TYPE_CUBE
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
}`,SC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,MC=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,EC=`#include <common>
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
}`,bC=`#if DEPTH_PACKING == 3200
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
}`,TC=`#define DISTANCE
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
}`,AC=`#define DISTANCE
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
}`,CC=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,RC=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,wC=`uniform float scale;
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
}`,DC=`uniform vec3 diffuse;
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
}`,NC=`#include <common>
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
}`,UC=`uniform vec3 diffuse;
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
}`,LC=`#define LAMBERT
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
}`,OC=`#define LAMBERT
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
}`,PC=`#define MATCAP
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
}`,zC=`#define MATCAP
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
}`,IC=`#define NORMAL
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
}`,BC=`#define NORMAL
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
}`,FC=`#define PHONG
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
}`,HC=`#define PHONG
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
}`,GC=`#define STANDARD
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
}`,VC=`#define STANDARD
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
}`,kC=`#define TOON
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
}`,jC=`#define TOON
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
}`,XC=`uniform float size;
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
}`,qC=`uniform vec3 diffuse;
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
}`,WC=`#include <common>
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
}`,YC=`uniform vec3 color;
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
}`,QC=`uniform float rotation;
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
}`,ZC=`uniform vec3 diffuse;
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
}`,he={alphahash_fragment:_A,alphahash_pars_fragment:yA,alphamap_fragment:xA,alphamap_pars_fragment:SA,alphatest_fragment:MA,alphatest_pars_fragment:EA,aomap_fragment:bA,aomap_pars_fragment:TA,batching_pars_vertex:AA,batching_vertex:CA,begin_vertex:RA,beginnormal_vertex:wA,bsdfs:DA,iridescence_fragment:NA,bumpmap_pars_fragment:UA,clipping_planes_fragment:LA,clipping_planes_pars_fragment:OA,clipping_planes_pars_vertex:PA,clipping_planes_vertex:zA,color_fragment:IA,color_pars_fragment:BA,color_pars_vertex:FA,color_vertex:HA,common:GA,cube_uv_reflection_fragment:VA,defaultnormal_vertex:kA,displacementmap_pars_vertex:jA,displacementmap_vertex:XA,emissivemap_fragment:qA,emissivemap_pars_fragment:WA,colorspace_fragment:YA,colorspace_pars_fragment:QA,envmap_fragment:ZA,envmap_common_pars_fragment:KA,envmap_pars_fragment:JA,envmap_pars_vertex:$A,envmap_physical_pars_fragment:u2,envmap_vertex:t2,fog_vertex:e2,fog_pars_vertex:n2,fog_fragment:i2,fog_pars_fragment:a2,gradientmap_pars_fragment:s2,lightmap_pars_fragment:r2,lights_lambert_fragment:o2,lights_lambert_pars_fragment:l2,lights_pars_begin:c2,lights_toon_fragment:f2,lights_toon_pars_fragment:d2,lights_phong_fragment:h2,lights_phong_pars_fragment:p2,lights_physical_fragment:m2,lights_physical_pars_fragment:g2,lights_fragment_begin:v2,lights_fragment_maps:_2,lights_fragment_end:y2,logdepthbuf_fragment:x2,logdepthbuf_pars_fragment:S2,logdepthbuf_pars_vertex:M2,logdepthbuf_vertex:E2,map_fragment:b2,map_pars_fragment:T2,map_particle_fragment:A2,map_particle_pars_fragment:C2,metalnessmap_fragment:R2,metalnessmap_pars_fragment:w2,morphinstance_vertex:D2,morphcolor_vertex:N2,morphnormal_vertex:U2,morphtarget_pars_vertex:L2,morphtarget_vertex:O2,normal_fragment_begin:P2,normal_fragment_maps:z2,normal_pars_fragment:I2,normal_pars_vertex:B2,normal_vertex:F2,normalmap_pars_fragment:H2,clearcoat_normal_fragment_begin:G2,clearcoat_normal_fragment_maps:V2,clearcoat_pars_fragment:k2,iridescence_pars_fragment:j2,opaque_fragment:X2,packing:q2,premultiplied_alpha_fragment:W2,project_vertex:Y2,dithering_fragment:Q2,dithering_pars_fragment:Z2,roughnessmap_fragment:K2,roughnessmap_pars_fragment:J2,shadowmap_pars_fragment:$2,shadowmap_pars_vertex:tC,shadowmap_vertex:eC,shadowmask_pars_fragment:nC,skinbase_vertex:iC,skinning_pars_vertex:aC,skinning_vertex:sC,skinnormal_vertex:rC,specularmap_fragment:oC,specularmap_pars_fragment:lC,tonemapping_fragment:cC,tonemapping_pars_fragment:uC,transmission_fragment:fC,transmission_pars_fragment:dC,uv_pars_fragment:hC,uv_pars_vertex:pC,uv_vertex:mC,worldpos_vertex:gC,background_vert:vC,background_frag:_C,backgroundCube_vert:yC,backgroundCube_frag:xC,cube_vert:SC,cube_frag:MC,depth_vert:EC,depth_frag:bC,distanceRGBA_vert:TC,distanceRGBA_frag:AC,equirect_vert:CC,equirect_frag:RC,linedashed_vert:wC,linedashed_frag:DC,meshbasic_vert:NC,meshbasic_frag:UC,meshlambert_vert:LC,meshlambert_frag:OC,meshmatcap_vert:PC,meshmatcap_frag:zC,meshnormal_vert:IC,meshnormal_frag:BC,meshphong_vert:FC,meshphong_frag:HC,meshphysical_vert:GC,meshphysical_frag:VC,meshtoon_vert:kC,meshtoon_frag:jC,points_vert:XC,points_frag:qC,shadow_vert:WC,shadow_frag:YC,sprite_vert:QC,sprite_frag:ZC},Lt={common:{diffuse:{value:new pe(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new de},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new de}},envmap:{envMap:{value:null},envMapRotation:{value:new de},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new de}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new de}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new de},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new de},normalScale:{value:new Wt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new de},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new de}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new de}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new de}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new pe(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new pe(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0},uvTransform:{value:new de}},sprite:{diffuse:{value:new pe(16777215)},opacity:{value:1},center:{value:new Wt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new de},alphaMap:{value:null},alphaMapTransform:{value:new de},alphaTest:{value:0}}},$i={basic:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.fog]),vertexShader:he.meshbasic_vert,fragmentShader:he.meshbasic_frag},lambert:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)}}]),vertexShader:he.meshlambert_vert,fragmentShader:he.meshlambert_frag},phong:{uniforms:Xn([Lt.common,Lt.specularmap,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)},specular:{value:new pe(1118481)},shininess:{value:30}}]),vertexShader:he.meshphong_vert,fragmentShader:he.meshphong_frag},standard:{uniforms:Xn([Lt.common,Lt.envmap,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.roughnessmap,Lt.metalnessmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag},toon:{uniforms:Xn([Lt.common,Lt.aomap,Lt.lightmap,Lt.emissivemap,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.gradientmap,Lt.fog,Lt.lights,{emissive:{value:new pe(0)}}]),vertexShader:he.meshtoon_vert,fragmentShader:he.meshtoon_frag},matcap:{uniforms:Xn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,Lt.fog,{matcap:{value:null}}]),vertexShader:he.meshmatcap_vert,fragmentShader:he.meshmatcap_frag},points:{uniforms:Xn([Lt.points,Lt.fog]),vertexShader:he.points_vert,fragmentShader:he.points_frag},dashed:{uniforms:Xn([Lt.common,Lt.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:he.linedashed_vert,fragmentShader:he.linedashed_frag},depth:{uniforms:Xn([Lt.common,Lt.displacementmap]),vertexShader:he.depth_vert,fragmentShader:he.depth_frag},normal:{uniforms:Xn([Lt.common,Lt.bumpmap,Lt.normalmap,Lt.displacementmap,{opacity:{value:1}}]),vertexShader:he.meshnormal_vert,fragmentShader:he.meshnormal_frag},sprite:{uniforms:Xn([Lt.sprite,Lt.fog]),vertexShader:he.sprite_vert,fragmentShader:he.sprite_frag},background:{uniforms:{uvTransform:{value:new de},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:he.background_vert,fragmentShader:he.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new de}},vertexShader:he.backgroundCube_vert,fragmentShader:he.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:he.cube_vert,fragmentShader:he.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:he.equirect_vert,fragmentShader:he.equirect_frag},distanceRGBA:{uniforms:Xn([Lt.common,Lt.displacementmap,{referencePosition:{value:new W},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:he.distanceRGBA_vert,fragmentShader:he.distanceRGBA_frag},shadow:{uniforms:Xn([Lt.lights,Lt.fog,{color:{value:new pe(0)},opacity:{value:1}}]),vertexShader:he.shadow_vert,fragmentShader:he.shadow_frag}};$i.physical={uniforms:Xn([$i.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new de},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new de},clearcoatNormalScale:{value:new Wt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new de},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new de},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new de},sheen:{value:0},sheenColor:{value:new pe(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new de},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new de},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new de},transmissionSamplerSize:{value:new Wt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new de},attenuationDistance:{value:0},attenuationColor:{value:new pe(0)},specularColor:{value:new pe(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new de},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new de},anisotropyVector:{value:new Wt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new de}}]),vertexShader:he.meshphysical_vert,fragmentShader:he.meshphysical_frag};const Wu={r:0,b:0,g:0},$s=new Ia,KC=new an;function JC(a,t,n,s,l,c,f){const d=new pe(0);let p=c===!0?0:1,m,g,_=null,y=0,S=null;function b(N){let R=N.isScene===!0?N.background:null;return R&&R.isTexture&&(R=(N.backgroundBlurriness>0?n:t).get(R)),R}function T(N){let R=!1;const V=b(N);V===null?x(d,p):V&&V.isColor&&(x(V,1),R=!0);const F=a.xr.getEnvironmentBlendMode();F==="additive"?s.buffers.color.setClear(0,0,0,1,f):F==="alpha-blend"&&s.buffers.color.setClear(0,0,0,0,f),(a.autoClear||R)&&(s.buffers.depth.setTest(!0),s.buffers.depth.setMask(!0),s.buffers.color.setMask(!0),a.clear(a.autoClearColor,a.autoClearDepth,a.autoClearStencil))}function E(N,R){const V=b(R);V&&(V.isCubeTexture||V.mapping===pf)?(g===void 0&&(g=new Wn(new dc(1,1,1),new Yn({name:"BackgroundCubeMaterial",uniforms:ko($i.backgroundCube.uniforms),vertexShader:$i.backgroundCube.vertexShader,fragmentShader:$i.backgroundCube.fragmentShader,side:ii,depthTest:!1,depthWrite:!1,fog:!1})),g.geometry.deleteAttribute("normal"),g.geometry.deleteAttribute("uv"),g.onBeforeRender=function(F,z,G){this.matrixWorld.copyPosition(G.matrixWorld)},Object.defineProperty(g.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),l.update(g)),$s.copy(R.backgroundRotation),$s.x*=-1,$s.y*=-1,$s.z*=-1,V.isCubeTexture&&V.isRenderTargetTexture===!1&&($s.y*=-1,$s.z*=-1),g.material.uniforms.envMap.value=V,g.material.uniforms.flipEnvMap.value=V.isCubeTexture&&V.isRenderTargetTexture===!1?-1:1,g.material.uniforms.backgroundBlurriness.value=R.backgroundBlurriness,g.material.uniforms.backgroundIntensity.value=R.backgroundIntensity,g.material.uniforms.backgroundRotation.value.setFromMatrix4(KC.makeRotationFromEuler($s)),g.material.toneMapped=Oe.getTransfer(V.colorSpace)!==qe,(_!==V||y!==V.version||S!==a.toneMapping)&&(g.material.needsUpdate=!0,_=V,y=V.version,S=a.toneMapping),g.layers.enableAll(),N.unshift(g,g.geometry,g.material,0,0,null)):V&&V.isTexture&&(m===void 0&&(m=new Wn(new gf(2,2),new Yn({name:"BackgroundMaterial",uniforms:ko($i.background.uniforms),vertexShader:$i.background.vertexShader,fragmentShader:$i.background.fragmentShader,side:Rs,depthTest:!1,depthWrite:!1,fog:!1})),m.geometry.deleteAttribute("normal"),Object.defineProperty(m.material,"map",{get:function(){return this.uniforms.t2D.value}}),l.update(m)),m.material.uniforms.t2D.value=V,m.material.uniforms.backgroundIntensity.value=R.backgroundIntensity,m.material.toneMapped=Oe.getTransfer(V.colorSpace)!==qe,V.matrixAutoUpdate===!0&&V.updateMatrix(),m.material.uniforms.uvTransform.value.copy(V.matrix),(_!==V||y!==V.version||S!==a.toneMapping)&&(m.material.needsUpdate=!0,_=V,y=V.version,S=a.toneMapping),m.layers.enableAll(),N.unshift(m,m.geometry,m.material,0,0,null))}function x(N,R){N.getRGB(Wu,$x(a)),s.buffers.color.setClear(Wu.r,Wu.g,Wu.b,R,f)}function P(){g!==void 0&&(g.geometry.dispose(),g.material.dispose()),m!==void 0&&(m.geometry.dispose(),m.material.dispose())}return{getClearColor:function(){return d},setClearColor:function(N,R=1){d.set(N),p=R,x(d,p)},getClearAlpha:function(){return p},setClearAlpha:function(N){p=N,x(d,p)},render:T,addToRenderList:E,dispose:P}}function $C(a,t){const n=a.getParameter(a.MAX_VERTEX_ATTRIBS),s={},l=y(null);let c=l,f=!1;function d(D,H,ut,ot,mt){let ct=!1;const I=_(ot,ut,H);c!==I&&(c=I,m(c.object)),ct=S(D,ot,ut,mt),ct&&b(D,ot,ut,mt),mt!==null&&t.update(mt,a.ELEMENT_ARRAY_BUFFER),(ct||f)&&(f=!1,R(D,H,ut,ot),mt!==null&&a.bindBuffer(a.ELEMENT_ARRAY_BUFFER,t.get(mt).buffer))}function p(){return a.createVertexArray()}function m(D){return a.bindVertexArray(D)}function g(D){return a.deleteVertexArray(D)}function _(D,H,ut){const ot=ut.wireframe===!0;let mt=s[D.id];mt===void 0&&(mt={},s[D.id]=mt);let ct=mt[H.id];ct===void 0&&(ct={},mt[H.id]=ct);let I=ct[ot];return I===void 0&&(I=y(p()),ct[ot]=I),I}function y(D){const H=[],ut=[],ot=[];for(let mt=0;mt<n;mt++)H[mt]=0,ut[mt]=0,ot[mt]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ut,attributeDivisors:ot,object:D,attributes:{},index:null}}function S(D,H,ut,ot){const mt=c.attributes,ct=H.attributes;let I=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){const At=mt[$];let O=ct[$];if(O===void 0&&($==="instanceMatrix"&&D.instanceMatrix&&(O=D.instanceMatrix),$==="instanceColor"&&D.instanceColor&&(O=D.instanceColor)),At===void 0||At.attribute!==O||O&&At.data!==O.data)return!0;I++}return c.attributesNum!==I||c.index!==ot}function b(D,H,ut,ot){const mt={},ct=H.attributes;let I=0;const Z=ut.getAttributes();for(const $ in Z)if(Z[$].location>=0){let At=ct[$];At===void 0&&($==="instanceMatrix"&&D.instanceMatrix&&(At=D.instanceMatrix),$==="instanceColor"&&D.instanceColor&&(At=D.instanceColor));const O={};O.attribute=At,At&&At.data&&(O.data=At.data),mt[$]=O,I++}c.attributes=mt,c.attributesNum=I,c.index=ot}function T(){const D=c.newAttributes;for(let H=0,ut=D.length;H<ut;H++)D[H]=0}function E(D){x(D,0)}function x(D,H){const ut=c.newAttributes,ot=c.enabledAttributes,mt=c.attributeDivisors;ut[D]=1,ot[D]===0&&(a.enableVertexAttribArray(D),ot[D]=1),mt[D]!==H&&(a.vertexAttribDivisor(D,H),mt[D]=H)}function P(){const D=c.newAttributes,H=c.enabledAttributes;for(let ut=0,ot=H.length;ut<ot;ut++)H[ut]!==D[ut]&&(a.disableVertexAttribArray(ut),H[ut]=0)}function N(D,H,ut,ot,mt,ct,I){I===!0?a.vertexAttribIPointer(D,H,ut,mt,ct):a.vertexAttribPointer(D,H,ut,ot,mt,ct)}function R(D,H,ut,ot){T();const mt=ot.attributes,ct=ut.getAttributes(),I=H.defaultAttributeValues;for(const Z in ct){const $=ct[Z];if($.location>=0){let Et=mt[Z];if(Et===void 0&&(Z==="instanceMatrix"&&D.instanceMatrix&&(Et=D.instanceMatrix),Z==="instanceColor"&&D.instanceColor&&(Et=D.instanceColor)),Et!==void 0){const At=Et.normalized,O=Et.itemSize,nt=t.get(Et);if(nt===void 0)continue;const St=nt.buffer,q=nt.type,ft=nt.bytesPerElement,Tt=q===a.INT||q===a.UNSIGNED_INT||Et.gpuType===Tm;if(Et.isInterleavedBufferAttribute){const Mt=Et.data,Ft=Mt.stride,Vt=Et.offset;if(Mt.isInstancedInterleavedBuffer){for(let oe=0;oe<$.locationSize;oe++)x($.location+oe,Mt.meshPerAttribute);D.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Mt.meshPerAttribute*Mt.count)}else for(let oe=0;oe<$.locationSize;oe++)E($.location+oe);a.bindBuffer(a.ARRAY_BUFFER,St);for(let oe=0;oe<$.locationSize;oe++)N($.location+oe,O/$.locationSize,q,At,Ft*ft,(Vt+O/$.locationSize*oe)*ft,Tt)}else{if(Et.isInstancedBufferAttribute){for(let Mt=0;Mt<$.locationSize;Mt++)x($.location+Mt,Et.meshPerAttribute);D.isInstancedMesh!==!0&&ot._maxInstanceCount===void 0&&(ot._maxInstanceCount=Et.meshPerAttribute*Et.count)}else for(let Mt=0;Mt<$.locationSize;Mt++)E($.location+Mt);a.bindBuffer(a.ARRAY_BUFFER,St);for(let Mt=0;Mt<$.locationSize;Mt++)N($.location+Mt,O/$.locationSize,q,At,O*ft,O/$.locationSize*Mt*ft,Tt)}}else if(I!==void 0){const At=I[Z];if(At!==void 0)switch(At.length){case 2:a.vertexAttrib2fv($.location,At);break;case 3:a.vertexAttrib3fv($.location,At);break;case 4:a.vertexAttrib4fv($.location,At);break;default:a.vertexAttrib1fv($.location,At)}}}}P()}function V(){G();for(const D in s){const H=s[D];for(const ut in H){const ot=H[ut];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete H[ut]}delete s[D]}}function F(D){if(s[D.id]===void 0)return;const H=s[D.id];for(const ut in H){const ot=H[ut];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete H[ut]}delete s[D.id]}function z(D){for(const H in s){const ut=s[H];if(ut[D.id]===void 0)continue;const ot=ut[D.id];for(const mt in ot)g(ot[mt].object),delete ot[mt];delete ut[D.id]}}function G(){U(),f=!0,c!==l&&(c=l,m(c.object))}function U(){l.geometry=null,l.program=null,l.wireframe=!1}return{setup:d,reset:G,resetDefaultState:U,dispose:V,releaseStatesOfGeometry:F,releaseStatesOfProgram:z,initAttributes:T,enableAttribute:E,disableUnusedAttributes:P}}function tR(a,t,n){let s;function l(m){s=m}function c(m,g){a.drawArrays(s,m,g),n.update(g,s,1)}function f(m,g,_){_!==0&&(a.drawArraysInstanced(s,m,g,_),n.update(g,s,_))}function d(m,g,_){if(_===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(s,m,0,g,0,_);let S=0;for(let b=0;b<_;b++)S+=g[b];n.update(S,s,1)}function p(m,g,_,y){if(_===0)return;const S=t.get("WEBGL_multi_draw");if(S===null)for(let b=0;b<m.length;b++)f(m[b],g[b],y[b]);else{S.multiDrawArraysInstancedWEBGL(s,m,0,g,0,y,0,_);let b=0;for(let T=0;T<_;T++)b+=g[T]*y[T];n.update(b,s,1)}}this.setMode=l,this.render=c,this.renderInstances=f,this.renderMultiDraw=d,this.renderMultiDrawInstances=p}function eR(a,t,n,s){let l;function c(){if(l!==void 0)return l;if(t.has("EXT_texture_filter_anisotropic")===!0){const z=t.get("EXT_texture_filter_anisotropic");l=a.getParameter(z.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else l=0;return l}function f(z){return!(z!==Fi&&s.convert(z)!==a.getParameter(a.IMPLEMENTATION_COLOR_READ_FORMAT))}function d(z){const G=z===Oa&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(z!==za&&s.convert(z)!==a.getParameter(a.IMPLEMENTATION_COLOR_READ_TYPE)&&z!==Na&&!G)}function p(z){if(z==="highp"){if(a.getShaderPrecisionFormat(a.VERTEX_SHADER,a.HIGH_FLOAT).precision>0&&a.getShaderPrecisionFormat(a.FRAGMENT_SHADER,a.HIGH_FLOAT).precision>0)return"highp";z="mediump"}return z==="mediump"&&a.getShaderPrecisionFormat(a.VERTEX_SHADER,a.MEDIUM_FLOAT).precision>0&&a.getShaderPrecisionFormat(a.FRAGMENT_SHADER,a.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let m=n.precision!==void 0?n.precision:"highp";const g=p(m);g!==m&&(console.warn("THREE.WebGLRenderer:",m,"not supported, using",g,"instead."),m=g);const _=n.logarithmicDepthBuffer===!0,y=n.reverseDepthBuffer===!0&&t.has("EXT_clip_control"),S=a.getParameter(a.MAX_TEXTURE_IMAGE_UNITS),b=a.getParameter(a.MAX_VERTEX_TEXTURE_IMAGE_UNITS),T=a.getParameter(a.MAX_TEXTURE_SIZE),E=a.getParameter(a.MAX_CUBE_MAP_TEXTURE_SIZE),x=a.getParameter(a.MAX_VERTEX_ATTRIBS),P=a.getParameter(a.MAX_VERTEX_UNIFORM_VECTORS),N=a.getParameter(a.MAX_VARYING_VECTORS),R=a.getParameter(a.MAX_FRAGMENT_UNIFORM_VECTORS),V=b>0,F=a.getParameter(a.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:c,getMaxPrecision:p,textureFormatReadable:f,textureTypeReadable:d,precision:m,logarithmicDepthBuffer:_,reverseDepthBuffer:y,maxTextures:S,maxVertexTextures:b,maxTextureSize:T,maxCubemapSize:E,maxAttributes:x,maxVertexUniforms:P,maxVaryings:N,maxFragmentUniforms:R,vertexTextures:V,maxSamples:F}}function nR(a){const t=this;let n=null,s=0,l=!1,c=!1;const f=new nr,d=new de,p={value:null,needsUpdate:!1};this.uniform=p,this.numPlanes=0,this.numIntersection=0,this.init=function(_,y){const S=_.length!==0||y||s!==0||l;return l=y,s=_.length,S},this.beginShadows=function(){c=!0,g(null)},this.endShadows=function(){c=!1},this.setGlobalState=function(_,y){n=g(_,y,0)},this.setState=function(_,y,S){const b=_.clippingPlanes,T=_.clipIntersection,E=_.clipShadows,x=a.get(_);if(!l||b===null||b.length===0||c&&!E)c?g(null):m();else{const P=c?0:s,N=P*4;let R=x.clippingState||null;p.value=R,R=g(b,y,N,S);for(let V=0;V!==N;++V)R[V]=n[V];x.clippingState=R,this.numIntersection=T?this.numPlanes:0,this.numPlanes+=P}};function m(){p.value!==n&&(p.value=n,p.needsUpdate=s>0),t.numPlanes=s,t.numIntersection=0}function g(_,y,S,b){const T=_!==null?_.length:0;let E=null;if(T!==0){if(E=p.value,b!==!0||E===null){const x=S+T*4,P=y.matrixWorldInverse;d.getNormalMatrix(P),(E===null||E.length<x)&&(E=new Float32Array(x));for(let N=0,R=S;N!==T;++N,R+=4)f.copy(_[N]).applyMatrix4(P,d),f.normal.toArray(E,R),E[R+3]=f.constant}p.value=E,p.needsUpdate=!0}return t.numPlanes=T,t.numIntersection=0,E}}function iR(a){let t=new WeakMap;function n(f,d){return d===Ip?f.mapping=Bo:d===Bp&&(f.mapping=Fo),f}function s(f){if(f&&f.isTexture){const d=f.mapping;if(d===Ip||d===Bp)if(t.has(f)){const p=t.get(f).texture;return n(p,f.mapping)}else{const p=f.image;if(p&&p.height>0){const m=new jT(p.height);return m.fromEquirectangularTexture(a,f),t.set(f,m),f.addEventListener("dispose",l),n(m.texture,f.mapping)}else return null}}return f}function l(f){const d=f.target;d.removeEventListener("dispose",l);const p=t.get(d);p!==void 0&&(t.delete(d),p.dispose())}function c(){t=new WeakMap}return{get:s,dispose:c}}const yo=4,_y=[.125,.215,.35,.446,.526,.582],sr=20,sp=new oS,yy=new pe;let rp=null,op=0,lp=0,cp=!1;const ir=(1+Math.sqrt(5))/2,mo=1/ir,xy=[new W(-ir,mo,0),new W(ir,mo,0),new W(-mo,0,ir),new W(mo,0,ir),new W(0,ir,-mo),new W(0,ir,mo),new W(-1,1,-1),new W(1,1,-1),new W(-1,1,1),new W(1,1,1)];class Sy{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(t,n=0,s=.1,l=100){rp=this._renderer.getRenderTarget(),op=this._renderer.getActiveCubeFace(),lp=this._renderer.getActiveMipmapLevel(),cp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const c=this._allocateTargets();return c.depthBuffer=!0,this._sceneToCubeUV(t,s,l,c),n>0&&this._blur(c,0,0,n),this._applyPMREM(c),this._cleanup(c),c}fromEquirectangular(t,n=null){return this._fromTexture(t,n)}fromCubemap(t,n=null){return this._fromTexture(t,n)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=by(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Ey(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodPlanes.length;t++)this._lodPlanes[t].dispose()}_cleanup(t){this._renderer.setRenderTarget(rp,op,lp),this._renderer.xr.enabled=cp,t.scissorTest=!1,Yu(t,0,0,t.width,t.height)}_fromTexture(t,n){t.mapping===Bo||t.mapping===Fo?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),rp=this._renderer.getRenderTarget(),op=this._renderer.getActiveCubeFace(),lp=this._renderer.getActiveMipmapLevel(),cp=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const s=n||this._allocateTargets();return this._textureToCubeUV(t,s),this._applyPMREM(s),this._cleanup(s),s}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),n=4*this._cubeSize,s={magFilter:ta,minFilter:ta,generateMipmaps:!1,type:Oa,format:Fi,colorSpace:Vo,depthBuffer:!1},l=My(t,n,s);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==n){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=My(t,n,s);const{_lodMax:c}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=aR(c)),this._blurMaterial=sR(c,t,n)}return l}_compileMaterial(t){const n=new Wn(this._lodPlanes[0],t);this._renderer.compile(n,sp)}_sceneToCubeUV(t,n,s,l){const d=new _i(90,1,n,s),p=[1,-1,1,1,1,1],m=[1,1,1,-1,-1,-1],g=this._renderer,_=g.autoClear,y=g.toneMapping;g.getClearColor(yy),g.toneMapping=Cs,g.autoClear=!1;const S=new xr({name:"PMREM.Background",side:ii,depthWrite:!1,depthTest:!1}),b=new Wn(new dc,S);let T=!1;const E=t.background;E?E.isColor&&(S.color.copy(E),t.background=null,T=!0):(S.color.copy(yy),T=!0);for(let x=0;x<6;x++){const P=x%3;P===0?(d.up.set(0,p[x],0),d.lookAt(m[x],0,0)):P===1?(d.up.set(0,0,p[x]),d.lookAt(0,m[x],0)):(d.up.set(0,p[x],0),d.lookAt(0,0,m[x]));const N=this._cubeSize;Yu(l,P*N,x>2?N:0,N,N),g.setRenderTarget(l),T&&g.render(b,d),g.render(t,d)}b.geometry.dispose(),b.material.dispose(),g.toneMapping=y,g.autoClear=_,t.background=E}_textureToCubeUV(t,n){const s=this._renderer,l=t.mapping===Bo||t.mapping===Fo;l?(this._cubemapMaterial===null&&(this._cubemapMaterial=by()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Ey());const c=l?this._cubemapMaterial:this._equirectMaterial,f=new Wn(this._lodPlanes[0],c),d=c.uniforms;d.envMap.value=t;const p=this._cubeSize;Yu(n,0,0,3*p,2*p),s.setRenderTarget(n),s.render(f,sp)}_applyPMREM(t){const n=this._renderer,s=n.autoClear;n.autoClear=!1;const l=this._lodPlanes.length;for(let c=1;c<l;c++){const f=Math.sqrt(this._sigmas[c]*this._sigmas[c]-this._sigmas[c-1]*this._sigmas[c-1]),d=xy[(l-c-1)%xy.length];this._blur(t,c-1,c,f,d)}n.autoClear=s}_blur(t,n,s,l,c){const f=this._pingPongRenderTarget;this._halfBlur(t,f,n,s,l,"latitudinal",c),this._halfBlur(f,t,s,s,l,"longitudinal",c)}_halfBlur(t,n,s,l,c,f,d){const p=this._renderer,m=this._blurMaterial;f!=="latitudinal"&&f!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const g=3,_=new Wn(this._lodPlanes[l],m),y=m.uniforms,S=this._sizeLods[s]-1,b=isFinite(c)?Math.PI/(2*S):2*Math.PI/(2*sr-1),T=c/b,E=isFinite(c)?1+Math.floor(g*T):sr;E>sr&&console.warn(`sigmaRadians, ${c}, is too large and will clip, as it requested ${E} samples when the maximum is set to ${sr}`);const x=[];let P=0;for(let z=0;z<sr;++z){const G=z/T,U=Math.exp(-G*G/2);x.push(U),z===0?P+=U:z<E&&(P+=2*U)}for(let z=0;z<x.length;z++)x[z]=x[z]/P;y.envMap.value=t.texture,y.samples.value=E,y.weights.value=x,y.latitudinal.value=f==="latitudinal",d&&(y.poleAxis.value=d);const{_lodMax:N}=this;y.dTheta.value=b,y.mipInt.value=N-s;const R=this._sizeLods[l],V=3*R*(l>N-yo?l-N+yo:0),F=4*(this._cubeSize-R);Yu(n,V,F,3*R,2*R),p.setRenderTarget(n),p.render(_,sp)}}function aR(a){const t=[],n=[],s=[];let l=a;const c=a-yo+1+_y.length;for(let f=0;f<c;f++){const d=Math.pow(2,l);n.push(d);let p=1/d;f>a-yo?p=_y[f-a+yo-1]:f===0&&(p=0),s.push(p);const m=1/(d-2),g=-m,_=1+m,y=[g,g,_,g,_,_,g,g,_,_,g,_],S=6,b=6,T=3,E=2,x=1,P=new Float32Array(T*b*S),N=new Float32Array(E*b*S),R=new Float32Array(x*b*S);for(let F=0;F<S;F++){const z=F%3*2/3-1,G=F>2?0:-1,U=[z,G,0,z+2/3,G,0,z+2/3,G+1,0,z,G,0,z+2/3,G+1,0,z,G+1,0];P.set(U,T*b*F),N.set(y,E*b*F);const D=[F,F,F,F,F,F];R.set(D,x*b*F)}const V=new ki;V.setAttribute("position",new ea(P,T)),V.setAttribute("uv",new ea(N,E)),V.setAttribute("faceIndex",new ea(R,x)),t.push(V),l>yo&&l--}return{lodPlanes:t,sizeLods:n,sigmas:s}}function My(a,t,n){const s=new Vi(a,t,n);return s.texture.mapping=pf,s.texture.name="PMREM.cubeUv",s.scissorTest=!0,s}function Yu(a,t,n,s,l){a.viewport.set(t,n,s,l),a.scissor.set(t,n,s,l)}function sR(a,t,n){const s=new Float32Array(sr),l=new W(0,1,0);return new Yn({name:"SphericalGaussianBlur",defines:{n:sr,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/n,CUBEUV_MAX_MIP:`${a}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:s},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:l}},vertexShader:zm(),fragmentShader:`

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
		`,blending:La,depthTest:!1,depthWrite:!1})}function Ey(){return new Yn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:zm(),fragmentShader:`

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
		`,blending:La,depthTest:!1,depthWrite:!1})}function by(){return new Yn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:zm(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:La,depthTest:!1,depthWrite:!1})}function zm(){return`

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
	`}function rR(a){let t=new WeakMap,n=null;function s(d){if(d&&d.isTexture){const p=d.mapping,m=p===Ip||p===Bp,g=p===Bo||p===Fo;if(m||g){let _=t.get(d);const y=_!==void 0?_.texture.pmremVersion:0;if(d.isRenderTargetTexture&&d.pmremVersion!==y)return n===null&&(n=new Sy(a)),_=m?n.fromEquirectangular(d,_):n.fromCubemap(d,_),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),_.texture;if(_!==void 0)return _.texture;{const S=d.image;return m&&S&&S.height>0||g&&S&&l(S)?(n===null&&(n=new Sy(a)),_=m?n.fromEquirectangular(d):n.fromCubemap(d),_.texture.pmremVersion=d.pmremVersion,t.set(d,_),d.addEventListener("dispose",c),_.texture):null}}}return d}function l(d){let p=0;const m=6;for(let g=0;g<m;g++)d[g]!==void 0&&p++;return p===m}function c(d){const p=d.target;p.removeEventListener("dispose",c);const m=t.get(p);m!==void 0&&(t.delete(p),m.dispose())}function f(){t=new WeakMap,n!==null&&(n.dispose(),n=null)}return{get:s,dispose:f}}function oR(a){const t={};function n(s){if(t[s]!==void 0)return t[s];let l;switch(s){case"WEBGL_depth_texture":l=a.getExtension("WEBGL_depth_texture")||a.getExtension("MOZ_WEBGL_depth_texture")||a.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":l=a.getExtension("EXT_texture_filter_anisotropic")||a.getExtension("MOZ_EXT_texture_filter_anisotropic")||a.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":l=a.getExtension("WEBGL_compressed_texture_s3tc")||a.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||a.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":l=a.getExtension("WEBGL_compressed_texture_pvrtc")||a.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:l=a.getExtension(s)}return t[s]=l,l}return{has:function(s){return n(s)!==null},init:function(){n("EXT_color_buffer_float"),n("WEBGL_clip_cull_distance"),n("OES_texture_float_linear"),n("EXT_color_buffer_half_float"),n("WEBGL_multisampled_render_to_texture"),n("WEBGL_render_shared_exponent")},get:function(s){const l=n(s);return l===null&&vo("THREE.WebGLRenderer: "+s+" extension not supported."),l}}}function lR(a,t,n,s){const l={},c=new WeakMap;function f(_){const y=_.target;y.index!==null&&t.remove(y.index);for(const b in y.attributes)t.remove(y.attributes[b]);y.removeEventListener("dispose",f),delete l[y.id];const S=c.get(y);S&&(t.remove(S),c.delete(y)),s.releaseStatesOfGeometry(y),y.isInstancedBufferGeometry===!0&&delete y._maxInstanceCount,n.memory.geometries--}function d(_,y){return l[y.id]===!0||(y.addEventListener("dispose",f),l[y.id]=!0,n.memory.geometries++),y}function p(_){const y=_.attributes;for(const S in y)t.update(y[S],a.ARRAY_BUFFER)}function m(_){const y=[],S=_.index,b=_.attributes.position;let T=0;if(S!==null){const P=S.array;T=S.version;for(let N=0,R=P.length;N<R;N+=3){const V=P[N+0],F=P[N+1],z=P[N+2];y.push(V,F,F,z,z,V)}}else if(b!==void 0){const P=b.array;T=b.version;for(let N=0,R=P.length/3-1;N<R;N+=3){const V=N+0,F=N+1,z=N+2;y.push(V,F,F,z,z,V)}}else return;const E=new(qx(y)?Jx:Kx)(y,1);E.version=T;const x=c.get(_);x&&t.remove(x),c.set(_,E)}function g(_){const y=c.get(_);if(y){const S=_.index;S!==null&&y.version<S.version&&m(_)}else m(_);return c.get(_)}return{get:d,update:p,getWireframeAttribute:g}}function cR(a,t,n){let s;function l(y){s=y}let c,f;function d(y){c=y.type,f=y.bytesPerElement}function p(y,S){a.drawElements(s,S,c,y*f),n.update(S,s,1)}function m(y,S,b){b!==0&&(a.drawElementsInstanced(s,S,c,y*f,b),n.update(S,s,b))}function g(y,S,b){if(b===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(s,S,0,c,y,0,b);let E=0;for(let x=0;x<b;x++)E+=S[x];n.update(E,s,1)}function _(y,S,b,T){if(b===0)return;const E=t.get("WEBGL_multi_draw");if(E===null)for(let x=0;x<y.length;x++)m(y[x]/f,S[x],T[x]);else{E.multiDrawElementsInstancedWEBGL(s,S,0,c,y,0,T,0,b);let x=0;for(let P=0;P<b;P++)x+=S[P]*T[P];n.update(x,s,1)}}this.setMode=l,this.setIndex=d,this.render=p,this.renderInstances=m,this.renderMultiDraw=g,this.renderMultiDrawInstances=_}function uR(a){const t={geometries:0,textures:0},n={frame:0,calls:0,triangles:0,points:0,lines:0};function s(c,f,d){switch(n.calls++,f){case a.TRIANGLES:n.triangles+=d*(c/3);break;case a.LINES:n.lines+=d*(c/2);break;case a.LINE_STRIP:n.lines+=d*(c-1);break;case a.LINE_LOOP:n.lines+=d*c;break;case a.POINTS:n.points+=d*c;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",f);break}}function l(){n.calls=0,n.triangles=0,n.points=0,n.lines=0}return{memory:t,render:n,programs:null,autoReset:!0,reset:l,update:s}}function fR(a,t,n){const s=new WeakMap,l=new We;function c(f,d,p){const m=f.morphTargetInfluences,g=d.morphAttributes.position||d.morphAttributes.normal||d.morphAttributes.color,_=g!==void 0?g.length:0;let y=s.get(d);if(y===void 0||y.count!==_){let D=function(){G.dispose(),s.delete(d),d.removeEventListener("dispose",D)};var S=D;y!==void 0&&y.texture.dispose();const b=d.morphAttributes.position!==void 0,T=d.morphAttributes.normal!==void 0,E=d.morphAttributes.color!==void 0,x=d.morphAttributes.position||[],P=d.morphAttributes.normal||[],N=d.morphAttributes.color||[];let R=0;b===!0&&(R=1),T===!0&&(R=2),E===!0&&(R=3);let V=d.attributes.position.count*R,F=1;V>t.maxTextureSize&&(F=Math.ceil(V/t.maxTextureSize),V=t.maxTextureSize);const z=new Float32Array(V*F*4*_),G=new Yx(z,V,F,_);G.type=Na,G.needsUpdate=!0;const U=R*4;for(let H=0;H<_;H++){const ut=x[H],ot=P[H],mt=N[H],ct=V*F*4*H;for(let I=0;I<ut.count;I++){const Z=I*U;b===!0&&(l.fromBufferAttribute(ut,I),z[ct+Z+0]=l.x,z[ct+Z+1]=l.y,z[ct+Z+2]=l.z,z[ct+Z+3]=0),T===!0&&(l.fromBufferAttribute(ot,I),z[ct+Z+4]=l.x,z[ct+Z+5]=l.y,z[ct+Z+6]=l.z,z[ct+Z+7]=0),E===!0&&(l.fromBufferAttribute(mt,I),z[ct+Z+8]=l.x,z[ct+Z+9]=l.y,z[ct+Z+10]=l.z,z[ct+Z+11]=mt.itemSize===4?l.w:1)}}y={count:_,texture:G,size:new Wt(V,F)},s.set(d,y),d.addEventListener("dispose",D)}if(f.isInstancedMesh===!0&&f.morphTexture!==null)p.getUniforms().setValue(a,"morphTexture",f.morphTexture,n);else{let b=0;for(let E=0;E<m.length;E++)b+=m[E];const T=d.morphTargetsRelative?1:1-b;p.getUniforms().setValue(a,"morphTargetBaseInfluence",T),p.getUniforms().setValue(a,"morphTargetInfluences",m)}p.getUniforms().setValue(a,"morphTargetsTexture",y.texture,n),p.getUniforms().setValue(a,"morphTargetsTextureSize",y.size)}return{update:c}}function dR(a,t,n,s){let l=new WeakMap;function c(p){const m=s.render.frame,g=p.geometry,_=t.get(p,g);if(l.get(_)!==m&&(t.update(_),l.set(_,m)),p.isInstancedMesh&&(p.hasEventListener("dispose",d)===!1&&p.addEventListener("dispose",d),l.get(p)!==m&&(n.update(p.instanceMatrix,a.ARRAY_BUFFER),p.instanceColor!==null&&n.update(p.instanceColor,a.ARRAY_BUFFER),l.set(p,m))),p.isSkinnedMesh){const y=p.skeleton;l.get(y)!==m&&(y.update(),l.set(y,m))}return _}function f(){l=new WeakMap}function d(p){const m=p.target;m.removeEventListener("dispose",d),n.remove(m.instanceMatrix),m.instanceColor!==null&&n.remove(m.instanceColor)}return{update:c,dispose:f}}const uS=new ai,Ty=new nS(1,1),fS=new Yx,dS=new RT,hS=new eS,Ay=[],Cy=[],Ry=new Float32Array(16),wy=new Float32Array(9),Dy=new Float32Array(4);function Wo(a,t,n){const s=a[0];if(s<=0||s>0)return a;const l=t*n;let c=Ay[l];if(c===void 0&&(c=new Float32Array(l),Ay[l]=c),t!==0){s.toArray(c,0);for(let f=1,d=0;f!==t;++f)d+=n,a[f].toArray(c,d)}return c}function Sn(a,t){if(a.length!==t.length)return!1;for(let n=0,s=a.length;n<s;n++)if(a[n]!==t[n])return!1;return!0}function Mn(a,t){for(let n=0,s=t.length;n<s;n++)a[n]=t[n]}function _f(a,t){let n=Cy[t];n===void 0&&(n=new Int32Array(t),Cy[t]=n);for(let s=0;s!==t;++s)n[s]=a.allocateTextureUnit();return n}function hR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1f(this.addr,t),n[0]=t)}function pR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2f(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2fv(this.addr,t),Mn(n,t)}}function mR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3f(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else if(t.r!==void 0)(n[0]!==t.r||n[1]!==t.g||n[2]!==t.b)&&(a.uniform3f(this.addr,t.r,t.g,t.b),n[0]=t.r,n[1]=t.g,n[2]=t.b);else{if(Sn(n,t))return;a.uniform3fv(this.addr,t),Mn(n,t)}}function gR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4f(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4fv(this.addr,t),Mn(n,t)}}function vR(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix2fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;Dy.set(s),a.uniformMatrix2fv(this.addr,!1,Dy),Mn(n,s)}}function _R(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix3fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;wy.set(s),a.uniformMatrix3fv(this.addr,!1,wy),Mn(n,s)}}function yR(a,t){const n=this.cache,s=t.elements;if(s===void 0){if(Sn(n,t))return;a.uniformMatrix4fv(this.addr,!1,t),Mn(n,t)}else{if(Sn(n,s))return;Ry.set(s),a.uniformMatrix4fv(this.addr,!1,Ry),Mn(n,s)}}function xR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1i(this.addr,t),n[0]=t)}function SR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2i(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2iv(this.addr,t),Mn(n,t)}}function MR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3i(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;a.uniform3iv(this.addr,t),Mn(n,t)}}function ER(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4i(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4iv(this.addr,t),Mn(n,t)}}function bR(a,t){const n=this.cache;n[0]!==t&&(a.uniform1ui(this.addr,t),n[0]=t)}function TR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y)&&(a.uniform2ui(this.addr,t.x,t.y),n[0]=t.x,n[1]=t.y);else{if(Sn(n,t))return;a.uniform2uiv(this.addr,t),Mn(n,t)}}function AR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z)&&(a.uniform3ui(this.addr,t.x,t.y,t.z),n[0]=t.x,n[1]=t.y,n[2]=t.z);else{if(Sn(n,t))return;a.uniform3uiv(this.addr,t),Mn(n,t)}}function CR(a,t){const n=this.cache;if(t.x!==void 0)(n[0]!==t.x||n[1]!==t.y||n[2]!==t.z||n[3]!==t.w)&&(a.uniform4ui(this.addr,t.x,t.y,t.z,t.w),n[0]=t.x,n[1]=t.y,n[2]=t.z,n[3]=t.w);else{if(Sn(n,t))return;a.uniform4uiv(this.addr,t),Mn(n,t)}}function RR(a,t,n){const s=this.cache,l=n.allocateTextureUnit();s[0]!==l&&(a.uniform1i(this.addr,l),s[0]=l);let c;this.type===a.SAMPLER_2D_SHADOW?(Ty.compareFunction=Xx,c=Ty):c=uS,n.setTexture2D(t||c,l)}function wR(a,t,n){const s=this.cache,l=n.allocateTextureUnit();s[0]!==l&&(a.uniform1i(this.addr,l),s[0]=l),n.setTexture3D(t||dS,l)}function DR(a,t,n){const s=this.cache,l=n.allocateTextureUnit();s[0]!==l&&(a.uniform1i(this.addr,l),s[0]=l),n.setTextureCube(t||hS,l)}function NR(a,t,n){const s=this.cache,l=n.allocateTextureUnit();s[0]!==l&&(a.uniform1i(this.addr,l),s[0]=l),n.setTexture2DArray(t||fS,l)}function UR(a){switch(a){case 5126:return hR;case 35664:return pR;case 35665:return mR;case 35666:return gR;case 35674:return vR;case 35675:return _R;case 35676:return yR;case 5124:case 35670:return xR;case 35667:case 35671:return SR;case 35668:case 35672:return MR;case 35669:case 35673:return ER;case 5125:return bR;case 36294:return TR;case 36295:return AR;case 36296:return CR;case 35678:case 36198:case 36298:case 36306:case 35682:return RR;case 35679:case 36299:case 36307:return wR;case 35680:case 36300:case 36308:case 36293:return DR;case 36289:case 36303:case 36311:case 36292:return NR}}function LR(a,t){a.uniform1fv(this.addr,t)}function OR(a,t){const n=Wo(t,this.size,2);a.uniform2fv(this.addr,n)}function PR(a,t){const n=Wo(t,this.size,3);a.uniform3fv(this.addr,n)}function zR(a,t){const n=Wo(t,this.size,4);a.uniform4fv(this.addr,n)}function IR(a,t){const n=Wo(t,this.size,4);a.uniformMatrix2fv(this.addr,!1,n)}function BR(a,t){const n=Wo(t,this.size,9);a.uniformMatrix3fv(this.addr,!1,n)}function FR(a,t){const n=Wo(t,this.size,16);a.uniformMatrix4fv(this.addr,!1,n)}function HR(a,t){a.uniform1iv(this.addr,t)}function GR(a,t){a.uniform2iv(this.addr,t)}function VR(a,t){a.uniform3iv(this.addr,t)}function kR(a,t){a.uniform4iv(this.addr,t)}function jR(a,t){a.uniform1uiv(this.addr,t)}function XR(a,t){a.uniform2uiv(this.addr,t)}function qR(a,t){a.uniform3uiv(this.addr,t)}function WR(a,t){a.uniform4uiv(this.addr,t)}function YR(a,t,n){const s=this.cache,l=t.length,c=_f(n,l);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==l;++f)n.setTexture2D(t[f]||uS,c[f])}function QR(a,t,n){const s=this.cache,l=t.length,c=_f(n,l);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==l;++f)n.setTexture3D(t[f]||dS,c[f])}function ZR(a,t,n){const s=this.cache,l=t.length,c=_f(n,l);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==l;++f)n.setTextureCube(t[f]||hS,c[f])}function KR(a,t,n){const s=this.cache,l=t.length,c=_f(n,l);Sn(s,c)||(a.uniform1iv(this.addr,c),Mn(s,c));for(let f=0;f!==l;++f)n.setTexture2DArray(t[f]||fS,c[f])}function JR(a){switch(a){case 5126:return LR;case 35664:return OR;case 35665:return PR;case 35666:return zR;case 35674:return IR;case 35675:return BR;case 35676:return FR;case 5124:case 35670:return HR;case 35667:case 35671:return GR;case 35668:case 35672:return VR;case 35669:case 35673:return kR;case 5125:return jR;case 36294:return XR;case 36295:return qR;case 36296:return WR;case 35678:case 36198:case 36298:case 36306:case 35682:return YR;case 35679:case 36299:case 36307:return QR;case 35680:case 36300:case 36308:case 36293:return ZR;case 36289:case 36303:case 36311:case 36292:return KR}}class $R{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.setValue=UR(n.type)}}class tw{constructor(t,n,s){this.id=t,this.addr=s,this.cache=[],this.type=n.type,this.size=n.size,this.setValue=JR(n.type)}}class ew{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,n,s){const l=this.seq;for(let c=0,f=l.length;c!==f;++c){const d=l[c];d.setValue(t,n[d.id],s)}}}const up=/(\w+)(\])?(\[|\.)?/g;function Ny(a,t){a.seq.push(t),a.map[t.id]=t}function nw(a,t,n){const s=a.name,l=s.length;for(up.lastIndex=0;;){const c=up.exec(s),f=up.lastIndex;let d=c[1];const p=c[2]==="]",m=c[3];if(p&&(d=d|0),m===void 0||m==="["&&f+2===l){Ny(n,m===void 0?new $R(d,a,t):new tw(d,a,t));break}else{let _=n.map[d];_===void 0&&(_=new ew(d),Ny(n,_)),n=_}}}class af{constructor(t,n){this.seq=[],this.map={};const s=t.getProgramParameter(n,t.ACTIVE_UNIFORMS);for(let l=0;l<s;++l){const c=t.getActiveUniform(n,l),f=t.getUniformLocation(n,c.name);nw(c,f,this)}}setValue(t,n,s,l){const c=this.map[n];c!==void 0&&c.setValue(t,s,l)}setOptional(t,n,s){const l=n[s];l!==void 0&&this.setValue(t,s,l)}static upload(t,n,s,l){for(let c=0,f=n.length;c!==f;++c){const d=n[c],p=s[d.id];p.needsUpdate!==!1&&d.setValue(t,p.value,l)}}static seqWithValue(t,n){const s=[];for(let l=0,c=t.length;l!==c;++l){const f=t[l];f.id in n&&s.push(f)}return s}}function Uy(a,t,n){const s=a.createShader(t);return a.shaderSource(s,n),a.compileShader(s),s}const iw=37297;let aw=0;function sw(a,t){const n=a.split(`
`),s=[],l=Math.max(t-6,0),c=Math.min(t+6,n.length);for(let f=l;f<c;f++){const d=f+1;s.push(`${d===t?">":" "} ${d}: ${n[f]}`)}return s.join(`
`)}const Ly=new de;function rw(a){Oe._getMatrix(Ly,Oe.workingColorSpace,a);const t=`mat3( ${Ly.elements.map(n=>n.toFixed(4))} )`;switch(Oe.getTransfer(a)){case cf:return[t,"LinearTransferOETF"];case qe:return[t,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",a),[t,"LinearTransferOETF"]}}function Oy(a,t,n){const s=a.getShaderParameter(t,a.COMPILE_STATUS),l=a.getShaderInfoLog(t).trim();if(s&&l==="")return"";const c=/ERROR: 0:(\d+)/.exec(l);if(c){const f=parseInt(c[1]);return n.toUpperCase()+`

`+l+`

`+sw(a.getShaderSource(t),f)}else return l}function ow(a,t){const n=rw(t);return[`vec4 ${a}( vec4 value ) {`,`	return ${n[1]}( vec4( value.rgb * ${n[0]}, value.a ) );`,"}"].join(`
`)}function lw(a,t){let n;switch(t){case Bb:n="Linear";break;case Fb:n="Reinhard";break;case Hb:n="Cineon";break;case Gb:n="ACESFilmic";break;case kb:n="AgX";break;case jb:n="Neutral";break;case Vb:n="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",t),n="Linear"}return"vec3 "+a+"( vec3 color ) { return "+n+"ToneMapping( color ); }"}const Qu=new W;function cw(){Oe.getLuminanceCoefficients(Qu);const a=Qu.x.toFixed(4),t=Qu.y.toFixed(4),n=Qu.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${a}, ${t}, ${n} );`,"	return dot( weights, rgb );","}"].join(`
`)}function uw(a){return[a.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",a.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Yl).join(`
`)}function fw(a){const t=[];for(const n in a){const s=a[n];s!==!1&&t.push("#define "+n+" "+s)}return t.join(`
`)}function dw(a,t){const n={},s=a.getProgramParameter(t,a.ACTIVE_ATTRIBUTES);for(let l=0;l<s;l++){const c=a.getActiveAttrib(t,l),f=c.name;let d=1;c.type===a.FLOAT_MAT2&&(d=2),c.type===a.FLOAT_MAT3&&(d=3),c.type===a.FLOAT_MAT4&&(d=4),n[f]={type:c.type,location:a.getAttribLocation(t,f),locationSize:d}}return n}function Yl(a){return a!==""}function Py(a,t){const n=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return a.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,n).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function zy(a,t){return a.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const hw=/^[ \t]*#include +<([\w\d./]+)>/gm;function hm(a){return a.replace(hw,mw)}const pw=new Map;function mw(a,t){let n=he[t];if(n===void 0){const s=pw.get(t);if(s!==void 0)n=he[s],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,s);else throw new Error("Can not resolve #include <"+t+">")}return hm(n)}const gw=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Iy(a){return a.replace(gw,vw)}function vw(a,t,n,s){let l="";for(let c=parseInt(t);c<parseInt(n);c++)l+=s.replace(/\[\s*i\s*\]/g,"[ "+c+" ]").replace(/UNROLLED_LOOP_INDEX/g,c);return l}function By(a){let t=`precision ${a.precision} float;
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
#define LOW_PRECISION`),t}function _w(a){let t="SHADOWMAP_TYPE_BASIC";return a.shadowMapType===Ux?t="SHADOWMAP_TYPE_PCF":a.shadowMapType===vb?t="SHADOWMAP_TYPE_PCF_SOFT":a.shadowMapType===Ca&&(t="SHADOWMAP_TYPE_VSM"),t}function yw(a){let t="ENVMAP_TYPE_CUBE";if(a.envMap)switch(a.envMapMode){case Bo:case Fo:t="ENVMAP_TYPE_CUBE";break;case pf:t="ENVMAP_TYPE_CUBE_UV";break}return t}function xw(a){let t="ENVMAP_MODE_REFLECTION";if(a.envMap)switch(a.envMapMode){case Fo:t="ENVMAP_MODE_REFRACTION";break}return t}function Sw(a){let t="ENVMAP_BLENDING_NONE";if(a.envMap)switch(a.combine){case Lx:t="ENVMAP_BLENDING_MULTIPLY";break;case zb:t="ENVMAP_BLENDING_MIX";break;case Ib:t="ENVMAP_BLENDING_ADD";break}return t}function Mw(a){const t=a.envMapCubeUVHeight;if(t===null)return null;const n=Math.log2(t)-2,s=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,n),112)),texelHeight:s,maxMip:n}}function Ew(a,t,n,s){const l=a.getContext(),c=n.defines;let f=n.vertexShader,d=n.fragmentShader;const p=_w(n),m=yw(n),g=xw(n),_=Sw(n),y=Mw(n),S=uw(n),b=fw(c),T=l.createProgram();let E,x,P=n.glslVersion?"#version "+n.glslVersion+`
`:"";n.isRawShaderMaterial?(E=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b].filter(Yl).join(`
`),E.length>0&&(E+=`
`),x=["#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b].filter(Yl).join(`
`),x.length>0&&(x+=`
`)):(E=[By(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b,n.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",n.batching?"#define USE_BATCHING":"",n.batchingColor?"#define USE_BATCHING_COLOR":"",n.instancing?"#define USE_INSTANCING":"",n.instancingColor?"#define USE_INSTANCING_COLOR":"",n.instancingMorph?"#define USE_INSTANCING_MORPH":"",n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.map?"#define USE_MAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+g:"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.displacementMap?"#define USE_DISPLACEMENTMAP":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.mapUv?"#define MAP_UV "+n.mapUv:"",n.alphaMapUv?"#define ALPHAMAP_UV "+n.alphaMapUv:"",n.lightMapUv?"#define LIGHTMAP_UV "+n.lightMapUv:"",n.aoMapUv?"#define AOMAP_UV "+n.aoMapUv:"",n.emissiveMapUv?"#define EMISSIVEMAP_UV "+n.emissiveMapUv:"",n.bumpMapUv?"#define BUMPMAP_UV "+n.bumpMapUv:"",n.normalMapUv?"#define NORMALMAP_UV "+n.normalMapUv:"",n.displacementMapUv?"#define DISPLACEMENTMAP_UV "+n.displacementMapUv:"",n.metalnessMapUv?"#define METALNESSMAP_UV "+n.metalnessMapUv:"",n.roughnessMapUv?"#define ROUGHNESSMAP_UV "+n.roughnessMapUv:"",n.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+n.anisotropyMapUv:"",n.clearcoatMapUv?"#define CLEARCOATMAP_UV "+n.clearcoatMapUv:"",n.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+n.clearcoatNormalMapUv:"",n.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+n.clearcoatRoughnessMapUv:"",n.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+n.iridescenceMapUv:"",n.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+n.iridescenceThicknessMapUv:"",n.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+n.sheenColorMapUv:"",n.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+n.sheenRoughnessMapUv:"",n.specularMapUv?"#define SPECULARMAP_UV "+n.specularMapUv:"",n.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+n.specularColorMapUv:"",n.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+n.specularIntensityMapUv:"",n.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+n.transmissionMapUv:"",n.thicknessMapUv?"#define THICKNESSMAP_UV "+n.thicknessMapUv:"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.flatShading?"#define FLAT_SHADED":"",n.skinning?"#define USE_SKINNING":"",n.morphTargets?"#define USE_MORPHTARGETS":"",n.morphNormals&&n.flatShading===!1?"#define USE_MORPHNORMALS":"",n.morphColors?"#define USE_MORPHCOLORS":"",n.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+n.morphTextureStride:"",n.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+n.morphTargetsCount:"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.sizeAttenuation?"#define USE_SIZEATTENUATION":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Yl).join(`
`),x=[By(n),"#define SHADER_TYPE "+n.shaderType,"#define SHADER_NAME "+n.shaderName,b,n.useFog&&n.fog?"#define USE_FOG":"",n.useFog&&n.fogExp2?"#define FOG_EXP2":"",n.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",n.map?"#define USE_MAP":"",n.matcap?"#define USE_MATCAP":"",n.envMap?"#define USE_ENVMAP":"",n.envMap?"#define "+m:"",n.envMap?"#define "+g:"",n.envMap?"#define "+_:"",y?"#define CUBEUV_TEXEL_WIDTH "+y.texelWidth:"",y?"#define CUBEUV_TEXEL_HEIGHT "+y.texelHeight:"",y?"#define CUBEUV_MAX_MIP "+y.maxMip+".0":"",n.lightMap?"#define USE_LIGHTMAP":"",n.aoMap?"#define USE_AOMAP":"",n.bumpMap?"#define USE_BUMPMAP":"",n.normalMap?"#define USE_NORMALMAP":"",n.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",n.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",n.emissiveMap?"#define USE_EMISSIVEMAP":"",n.anisotropy?"#define USE_ANISOTROPY":"",n.anisotropyMap?"#define USE_ANISOTROPYMAP":"",n.clearcoat?"#define USE_CLEARCOAT":"",n.clearcoatMap?"#define USE_CLEARCOATMAP":"",n.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",n.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",n.dispersion?"#define USE_DISPERSION":"",n.iridescence?"#define USE_IRIDESCENCE":"",n.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",n.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",n.specularMap?"#define USE_SPECULARMAP":"",n.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",n.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",n.roughnessMap?"#define USE_ROUGHNESSMAP":"",n.metalnessMap?"#define USE_METALNESSMAP":"",n.alphaMap?"#define USE_ALPHAMAP":"",n.alphaTest?"#define USE_ALPHATEST":"",n.alphaHash?"#define USE_ALPHAHASH":"",n.sheen?"#define USE_SHEEN":"",n.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",n.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",n.transmission?"#define USE_TRANSMISSION":"",n.transmissionMap?"#define USE_TRANSMISSIONMAP":"",n.thicknessMap?"#define USE_THICKNESSMAP":"",n.vertexTangents&&n.flatShading===!1?"#define USE_TANGENT":"",n.vertexColors||n.instancingColor||n.batchingColor?"#define USE_COLOR":"",n.vertexAlphas?"#define USE_COLOR_ALPHA":"",n.vertexUv1s?"#define USE_UV1":"",n.vertexUv2s?"#define USE_UV2":"",n.vertexUv3s?"#define USE_UV3":"",n.pointsUvs?"#define USE_POINTS_UV":"",n.gradientMap?"#define USE_GRADIENTMAP":"",n.flatShading?"#define FLAT_SHADED":"",n.doubleSided?"#define DOUBLE_SIDED":"",n.flipSided?"#define FLIP_SIDED":"",n.shadowMapEnabled?"#define USE_SHADOWMAP":"",n.shadowMapEnabled?"#define "+p:"",n.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",n.numLightProbes>0?"#define USE_LIGHT_PROBES":"",n.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",n.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",n.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",n.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",n.toneMapping!==Cs?"#define TONE_MAPPING":"",n.toneMapping!==Cs?he.tonemapping_pars_fragment:"",n.toneMapping!==Cs?lw("toneMapping",n.toneMapping):"",n.dithering?"#define DITHERING":"",n.opaque?"#define OPAQUE":"",he.colorspace_pars_fragment,ow("linearToOutputTexel",n.outputColorSpace),cw(),n.useDepthPacking?"#define DEPTH_PACKING "+n.depthPacking:"",`
`].filter(Yl).join(`
`)),f=hm(f),f=Py(f,n),f=zy(f,n),d=hm(d),d=Py(d,n),d=zy(d,n),f=Iy(f),d=Iy(d),n.isRawShaderMaterial!==!0&&(P=`#version 300 es
`,E=[S,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+E,x=["#define varying in",n.glslVersion===W0?"":"layout(location = 0) out highp vec4 pc_fragColor;",n.glslVersion===W0?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+x);const N=P+E+f,R=P+x+d,V=Uy(l,l.VERTEX_SHADER,N),F=Uy(l,l.FRAGMENT_SHADER,R);l.attachShader(T,V),l.attachShader(T,F),n.index0AttributeName!==void 0?l.bindAttribLocation(T,0,n.index0AttributeName):n.morphTargets===!0&&l.bindAttribLocation(T,0,"position"),l.linkProgram(T);function z(H){if(a.debug.checkShaderErrors){const ut=l.getProgramInfoLog(T).trim(),ot=l.getShaderInfoLog(V).trim(),mt=l.getShaderInfoLog(F).trim();let ct=!0,I=!0;if(l.getProgramParameter(T,l.LINK_STATUS)===!1)if(ct=!1,typeof a.debug.onShaderError=="function")a.debug.onShaderError(l,T,V,F);else{const Z=Oy(l,V,"vertex"),$=Oy(l,F,"fragment");console.error("THREE.WebGLProgram: Shader Error "+l.getError()+" - VALIDATE_STATUS "+l.getProgramParameter(T,l.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ut+`
`+Z+`
`+$)}else ut!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ut):(ot===""||mt==="")&&(I=!1);I&&(H.diagnostics={runnable:ct,programLog:ut,vertexShader:{log:ot,prefix:E},fragmentShader:{log:mt,prefix:x}})}l.deleteShader(V),l.deleteShader(F),G=new af(l,T),U=dw(l,T)}let G;this.getUniforms=function(){return G===void 0&&z(this),G};let U;this.getAttributes=function(){return U===void 0&&z(this),U};let D=n.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return D===!1&&(D=l.getProgramParameter(T,iw)),D},this.destroy=function(){s.releaseStatesOfProgram(this),l.deleteProgram(T),this.program=void 0},this.type=n.shaderType,this.name=n.shaderName,this.id=aw++,this.cacheKey=t,this.usedTimes=1,this.program=T,this.vertexShader=V,this.fragmentShader=F,this}let bw=0;class Tw{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const n=t.vertexShader,s=t.fragmentShader,l=this._getShaderStage(n),c=this._getShaderStage(s),f=this._getShaderCacheForMaterial(t);return f.has(l)===!1&&(f.add(l),l.usedTimes++),f.has(c)===!1&&(f.add(c),c.usedTimes++),this}remove(t){const n=this.materialCache.get(t);for(const s of n)s.usedTimes--,s.usedTimes===0&&this.shaderCache.delete(s.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const n=this.materialCache;let s=n.get(t);return s===void 0&&(s=new Set,n.set(t,s)),s}_getShaderStage(t){const n=this.shaderCache;let s=n.get(t);return s===void 0&&(s=new Aw(t),n.set(t,s)),s}}class Aw{constructor(t){this.id=bw++,this.code=t,this.usedTimes=0}}function Cw(a,t,n,s,l,c,f){const d=new Qx,p=new Tw,m=new Set,g=[],_=l.logarithmicDepthBuffer,y=l.vertexTextures;let S=l.precision;const b={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function T(U){return m.add(U),U===0?"uv":`uv${U}`}function E(U,D,H,ut,ot){const mt=ut.fog,ct=ot.geometry,I=U.isMeshStandardMaterial?ut.environment:null,Z=(U.isMeshStandardMaterial?n:t).get(U.envMap||I),$=Z&&Z.mapping===pf?Z.image.height:null,Et=b[U.type];U.precision!==null&&(S=l.getMaxPrecision(U.precision),S!==U.precision&&console.warn("THREE.WebGLProgram.getParameters:",U.precision,"not supported, using",S,"instead."));const At=ct.morphAttributes.position||ct.morphAttributes.normal||ct.morphAttributes.color,O=At!==void 0?At.length:0;let nt=0;ct.morphAttributes.position!==void 0&&(nt=1),ct.morphAttributes.normal!==void 0&&(nt=2),ct.morphAttributes.color!==void 0&&(nt=3);let St,q,ft,Tt;if(Et){const we=$i[Et];St=we.vertexShader,q=we.fragmentShader}else St=U.vertexShader,q=U.fragmentShader,p.update(U),ft=p.getVertexShaderID(U),Tt=p.getFragmentShaderID(U);const Mt=a.getRenderTarget(),Ft=a.state.buffers.depth.getReversed(),Vt=ot.isInstancedMesh===!0,oe=ot.isBatchedMesh===!0,Ge=!!U.map,ve=!!U.matcap,$e=!!Z,k=!!U.aoMap,Pn=!!U.lightMap,me=!!U.bumpMap,Se=!!U.normalMap,Qt=!!U.displacementMap,Be=!!U.emissiveMap,Yt=!!U.metalnessMap,L=!!U.roughnessMap,C=U.anisotropy>0,at=U.clearcoat>0,pt=U.dispersion>0,bt=U.iridescence>0,vt=U.sheen>0,Xt=U.transmission>0,Dt=C&&!!U.anisotropyMap,Bt=at&&!!U.clearcoatMap,Me=at&&!!U.clearcoatNormalMap,Ct=at&&!!U.clearcoatRoughnessMap,Ht=bt&&!!U.iridescenceMap,Zt=bt&&!!U.iridescenceThicknessMap,qt=vt&&!!U.sheenColorMap,Ot=vt&&!!U.sheenRoughnessMap,ne=!!U.specularMap,le=!!U.specularColorMap,Ve=!!U.specularIntensityMap,Y=Xt&&!!U.transmissionMap,Rt=Xt&&!!U.thicknessMap,dt=!!U.gradientMap,yt=!!U.alphaMap,wt=U.alphaTest>0,Nt=!!U.alphaHash,ie=!!U.extensions;let tn=Cs;U.toneMapped&&(Mt===null||Mt.isXRRenderTarget===!0)&&(tn=a.toneMapping);const _n={shaderID:Et,shaderType:U.type,shaderName:U.name,vertexShader:St,fragmentShader:q,defines:U.defines,customVertexShaderID:ft,customFragmentShaderID:Tt,isRawShaderMaterial:U.isRawShaderMaterial===!0,glslVersion:U.glslVersion,precision:S,batching:oe,batchingColor:oe&&ot._colorsTexture!==null,instancing:Vt,instancingColor:Vt&&ot.instanceColor!==null,instancingMorph:Vt&&ot.morphTexture!==null,supportsVertexTextures:y,outputColorSpace:Mt===null?a.outputColorSpace:Mt.isXRRenderTarget===!0?Mt.texture.colorSpace:Vo,alphaToCoverage:!!U.alphaToCoverage,map:Ge,matcap:ve,envMap:$e,envMapMode:$e&&Z.mapping,envMapCubeUVHeight:$,aoMap:k,lightMap:Pn,bumpMap:me,normalMap:Se,displacementMap:y&&Qt,emissiveMap:Be,normalMapObjectSpace:Se&&U.normalMapType===Qb,normalMapTangentSpace:Se&&U.normalMapType===Yb,metalnessMap:Yt,roughnessMap:L,anisotropy:C,anisotropyMap:Dt,clearcoat:at,clearcoatMap:Bt,clearcoatNormalMap:Me,clearcoatRoughnessMap:Ct,dispersion:pt,iridescence:bt,iridescenceMap:Ht,iridescenceThicknessMap:Zt,sheen:vt,sheenColorMap:qt,sheenRoughnessMap:Ot,specularMap:ne,specularColorMap:le,specularIntensityMap:Ve,transmission:Xt,transmissionMap:Y,thicknessMap:Rt,gradientMap:dt,opaque:U.transparent===!1&&U.blending===xo&&U.alphaToCoverage===!1,alphaMap:yt,alphaTest:wt,alphaHash:Nt,combine:U.combine,mapUv:Ge&&T(U.map.channel),aoMapUv:k&&T(U.aoMap.channel),lightMapUv:Pn&&T(U.lightMap.channel),bumpMapUv:me&&T(U.bumpMap.channel),normalMapUv:Se&&T(U.normalMap.channel),displacementMapUv:Qt&&T(U.displacementMap.channel),emissiveMapUv:Be&&T(U.emissiveMap.channel),metalnessMapUv:Yt&&T(U.metalnessMap.channel),roughnessMapUv:L&&T(U.roughnessMap.channel),anisotropyMapUv:Dt&&T(U.anisotropyMap.channel),clearcoatMapUv:Bt&&T(U.clearcoatMap.channel),clearcoatNormalMapUv:Me&&T(U.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Ct&&T(U.clearcoatRoughnessMap.channel),iridescenceMapUv:Ht&&T(U.iridescenceMap.channel),iridescenceThicknessMapUv:Zt&&T(U.iridescenceThicknessMap.channel),sheenColorMapUv:qt&&T(U.sheenColorMap.channel),sheenRoughnessMapUv:Ot&&T(U.sheenRoughnessMap.channel),specularMapUv:ne&&T(U.specularMap.channel),specularColorMapUv:le&&T(U.specularColorMap.channel),specularIntensityMapUv:Ve&&T(U.specularIntensityMap.channel),transmissionMapUv:Y&&T(U.transmissionMap.channel),thicknessMapUv:Rt&&T(U.thicknessMap.channel),alphaMapUv:yt&&T(U.alphaMap.channel),vertexTangents:!!ct.attributes.tangent&&(Se||C),vertexColors:U.vertexColors,vertexAlphas:U.vertexColors===!0&&!!ct.attributes.color&&ct.attributes.color.itemSize===4,pointsUvs:ot.isPoints===!0&&!!ct.attributes.uv&&(Ge||yt),fog:!!mt,useFog:U.fog===!0,fogExp2:!!mt&&mt.isFogExp2,flatShading:U.flatShading===!0,sizeAttenuation:U.sizeAttenuation===!0,logarithmicDepthBuffer:_,reverseDepthBuffer:Ft,skinning:ot.isSkinnedMesh===!0,morphTargets:ct.morphAttributes.position!==void 0,morphNormals:ct.morphAttributes.normal!==void 0,morphColors:ct.morphAttributes.color!==void 0,morphTargetsCount:O,morphTextureStride:nt,numDirLights:D.directional.length,numPointLights:D.point.length,numSpotLights:D.spot.length,numSpotLightMaps:D.spotLightMap.length,numRectAreaLights:D.rectArea.length,numHemiLights:D.hemi.length,numDirLightShadows:D.directionalShadowMap.length,numPointLightShadows:D.pointShadowMap.length,numSpotLightShadows:D.spotShadowMap.length,numSpotLightShadowsWithMaps:D.numSpotLightShadowsWithMaps,numLightProbes:D.numLightProbes,numClippingPlanes:f.numPlanes,numClipIntersection:f.numIntersection,dithering:U.dithering,shadowMapEnabled:a.shadowMap.enabled&&H.length>0,shadowMapType:a.shadowMap.type,toneMapping:tn,decodeVideoTexture:Ge&&U.map.isVideoTexture===!0&&Oe.getTransfer(U.map.colorSpace)===qe,decodeVideoTextureEmissive:Be&&U.emissiveMap.isVideoTexture===!0&&Oe.getTransfer(U.emissiveMap.colorSpace)===qe,premultipliedAlpha:U.premultipliedAlpha,doubleSided:U.side===Da,flipSided:U.side===ii,useDepthPacking:U.depthPacking>=0,depthPacking:U.depthPacking||0,index0AttributeName:U.index0AttributeName,extensionClipCullDistance:ie&&U.extensions.clipCullDistance===!0&&s.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ie&&U.extensions.multiDraw===!0||oe)&&s.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:s.has("KHR_parallel_shader_compile"),customProgramCacheKey:U.customProgramCacheKey()};return _n.vertexUv1s=m.has(1),_n.vertexUv2s=m.has(2),_n.vertexUv3s=m.has(3),m.clear(),_n}function x(U){const D=[];if(U.shaderID?D.push(U.shaderID):(D.push(U.customVertexShaderID),D.push(U.customFragmentShaderID)),U.defines!==void 0)for(const H in U.defines)D.push(H),D.push(U.defines[H]);return U.isRawShaderMaterial===!1&&(P(D,U),N(D,U),D.push(a.outputColorSpace)),D.push(U.customProgramCacheKey),D.join()}function P(U,D){U.push(D.precision),U.push(D.outputColorSpace),U.push(D.envMapMode),U.push(D.envMapCubeUVHeight),U.push(D.mapUv),U.push(D.alphaMapUv),U.push(D.lightMapUv),U.push(D.aoMapUv),U.push(D.bumpMapUv),U.push(D.normalMapUv),U.push(D.displacementMapUv),U.push(D.emissiveMapUv),U.push(D.metalnessMapUv),U.push(D.roughnessMapUv),U.push(D.anisotropyMapUv),U.push(D.clearcoatMapUv),U.push(D.clearcoatNormalMapUv),U.push(D.clearcoatRoughnessMapUv),U.push(D.iridescenceMapUv),U.push(D.iridescenceThicknessMapUv),U.push(D.sheenColorMapUv),U.push(D.sheenRoughnessMapUv),U.push(D.specularMapUv),U.push(D.specularColorMapUv),U.push(D.specularIntensityMapUv),U.push(D.transmissionMapUv),U.push(D.thicknessMapUv),U.push(D.combine),U.push(D.fogExp2),U.push(D.sizeAttenuation),U.push(D.morphTargetsCount),U.push(D.morphAttributeCount),U.push(D.numDirLights),U.push(D.numPointLights),U.push(D.numSpotLights),U.push(D.numSpotLightMaps),U.push(D.numHemiLights),U.push(D.numRectAreaLights),U.push(D.numDirLightShadows),U.push(D.numPointLightShadows),U.push(D.numSpotLightShadows),U.push(D.numSpotLightShadowsWithMaps),U.push(D.numLightProbes),U.push(D.shadowMapType),U.push(D.toneMapping),U.push(D.numClippingPlanes),U.push(D.numClipIntersection),U.push(D.depthPacking)}function N(U,D){d.disableAll(),D.supportsVertexTextures&&d.enable(0),D.instancing&&d.enable(1),D.instancingColor&&d.enable(2),D.instancingMorph&&d.enable(3),D.matcap&&d.enable(4),D.envMap&&d.enable(5),D.normalMapObjectSpace&&d.enable(6),D.normalMapTangentSpace&&d.enable(7),D.clearcoat&&d.enable(8),D.iridescence&&d.enable(9),D.alphaTest&&d.enable(10),D.vertexColors&&d.enable(11),D.vertexAlphas&&d.enable(12),D.vertexUv1s&&d.enable(13),D.vertexUv2s&&d.enable(14),D.vertexUv3s&&d.enable(15),D.vertexTangents&&d.enable(16),D.anisotropy&&d.enable(17),D.alphaHash&&d.enable(18),D.batching&&d.enable(19),D.dispersion&&d.enable(20),D.batchingColor&&d.enable(21),U.push(d.mask),d.disableAll(),D.fog&&d.enable(0),D.useFog&&d.enable(1),D.flatShading&&d.enable(2),D.logarithmicDepthBuffer&&d.enable(3),D.reverseDepthBuffer&&d.enable(4),D.skinning&&d.enable(5),D.morphTargets&&d.enable(6),D.morphNormals&&d.enable(7),D.morphColors&&d.enable(8),D.premultipliedAlpha&&d.enable(9),D.shadowMapEnabled&&d.enable(10),D.doubleSided&&d.enable(11),D.flipSided&&d.enable(12),D.useDepthPacking&&d.enable(13),D.dithering&&d.enable(14),D.transmission&&d.enable(15),D.sheen&&d.enable(16),D.opaque&&d.enable(17),D.pointsUvs&&d.enable(18),D.decodeVideoTexture&&d.enable(19),D.decodeVideoTextureEmissive&&d.enable(20),D.alphaToCoverage&&d.enable(21),U.push(d.mask)}function R(U){const D=b[U.type];let H;if(D){const ut=$i[D];H=df.clone(ut.uniforms)}else H=U.uniforms;return H}function V(U,D){let H;for(let ut=0,ot=g.length;ut<ot;ut++){const mt=g[ut];if(mt.cacheKey===D){H=mt,++H.usedTimes;break}}return H===void 0&&(H=new Ew(a,D,U,c),g.push(H)),H}function F(U){if(--U.usedTimes===0){const D=g.indexOf(U);g[D]=g[g.length-1],g.pop(),U.destroy()}}function z(U){p.remove(U)}function G(){p.dispose()}return{getParameters:E,getProgramCacheKey:x,getUniforms:R,acquireProgram:V,releaseProgram:F,releaseShaderCache:z,programs:g,dispose:G}}function Rw(){let a=new WeakMap;function t(f){return a.has(f)}function n(f){let d=a.get(f);return d===void 0&&(d={},a.set(f,d)),d}function s(f){a.delete(f)}function l(f,d,p){a.get(f)[d]=p}function c(){a=new WeakMap}return{has:t,get:n,remove:s,update:l,dispose:c}}function ww(a,t){return a.groupOrder!==t.groupOrder?a.groupOrder-t.groupOrder:a.renderOrder!==t.renderOrder?a.renderOrder-t.renderOrder:a.material.id!==t.material.id?a.material.id-t.material.id:a.z!==t.z?a.z-t.z:a.id-t.id}function Fy(a,t){return a.groupOrder!==t.groupOrder?a.groupOrder-t.groupOrder:a.renderOrder!==t.renderOrder?a.renderOrder-t.renderOrder:a.z!==t.z?t.z-a.z:a.id-t.id}function Hy(){const a=[];let t=0;const n=[],s=[],l=[];function c(){t=0,n.length=0,s.length=0,l.length=0}function f(_,y,S,b,T,E){let x=a[t];return x===void 0?(x={id:_.id,object:_,geometry:y,material:S,groupOrder:b,renderOrder:_.renderOrder,z:T,group:E},a[t]=x):(x.id=_.id,x.object=_,x.geometry=y,x.material=S,x.groupOrder=b,x.renderOrder=_.renderOrder,x.z=T,x.group=E),t++,x}function d(_,y,S,b,T,E){const x=f(_,y,S,b,T,E);S.transmission>0?s.push(x):S.transparent===!0?l.push(x):n.push(x)}function p(_,y,S,b,T,E){const x=f(_,y,S,b,T,E);S.transmission>0?s.unshift(x):S.transparent===!0?l.unshift(x):n.unshift(x)}function m(_,y){n.length>1&&n.sort(_||ww),s.length>1&&s.sort(y||Fy),l.length>1&&l.sort(y||Fy)}function g(){for(let _=t,y=a.length;_<y;_++){const S=a[_];if(S.id===null)break;S.id=null,S.object=null,S.geometry=null,S.material=null,S.group=null}}return{opaque:n,transmissive:s,transparent:l,init:c,push:d,unshift:p,finish:g,sort:m}}function Dw(){let a=new WeakMap;function t(s,l){const c=a.get(s);let f;return c===void 0?(f=new Hy,a.set(s,[f])):l>=c.length?(f=new Hy,c.push(f)):f=c[l],f}function n(){a=new WeakMap}return{get:t,dispose:n}}function Nw(){const a={};return{get:function(t){if(a[t.id]!==void 0)return a[t.id];let n;switch(t.type){case"DirectionalLight":n={direction:new W,color:new pe};break;case"SpotLight":n={position:new W,direction:new W,color:new pe,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":n={position:new W,color:new pe,distance:0,decay:0};break;case"HemisphereLight":n={direction:new W,skyColor:new pe,groundColor:new pe};break;case"RectAreaLight":n={color:new pe,position:new W,halfWidth:new W,halfHeight:new W};break}return a[t.id]=n,n}}}function Uw(){const a={};return{get:function(t){if(a[t.id]!==void 0)return a[t.id];let n;switch(t.type){case"DirectionalLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"SpotLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt};break;case"PointLight":n={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Wt,shadowCameraNear:1,shadowCameraFar:1e3};break}return a[t.id]=n,n}}}let Lw=0;function Ow(a,t){return(t.castShadow?2:0)-(a.castShadow?2:0)+(t.map?1:0)-(a.map?1:0)}function Pw(a){const t=new Nw,n=Uw(),s={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let m=0;m<9;m++)s.probe.push(new W);const l=new W,c=new an,f=new an;function d(m){let g=0,_=0,y=0;for(let U=0;U<9;U++)s.probe[U].set(0,0,0);let S=0,b=0,T=0,E=0,x=0,P=0,N=0,R=0,V=0,F=0,z=0;m.sort(Ow);for(let U=0,D=m.length;U<D;U++){const H=m[U],ut=H.color,ot=H.intensity,mt=H.distance,ct=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)g+=ut.r*ot,_+=ut.g*ot,y+=ut.b*ot;else if(H.isLightProbe){for(let I=0;I<9;I++)s.probe[I].addScaledVector(H.sh.coefficients[I],ot);z++}else if(H.isDirectionalLight){const I=t.get(H);if(I.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,s.directionalShadow[S]=$,s.directionalShadowMap[S]=ct,s.directionalShadowMatrix[S]=H.shadow.matrix,P++}s.directional[S]=I,S++}else if(H.isSpotLight){const I=t.get(H);I.position.setFromMatrixPosition(H.matrixWorld),I.color.copy(ut).multiplyScalar(ot),I.distance=mt,I.coneCos=Math.cos(H.angle),I.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),I.decay=H.decay,s.spot[T]=I;const Z=H.shadow;if(H.map&&(s.spotLightMap[V]=H.map,V++,Z.updateMatrices(H),H.castShadow&&F++),s.spotLightMatrix[T]=Z.matrix,H.castShadow){const $=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,s.spotShadow[T]=$,s.spotShadowMap[T]=ct,R++}T++}else if(H.isRectAreaLight){const I=t.get(H);I.color.copy(ut).multiplyScalar(ot),I.halfWidth.set(H.width*.5,0,0),I.halfHeight.set(0,H.height*.5,0),s.rectArea[E]=I,E++}else if(H.isPointLight){const I=t.get(H);if(I.color.copy(H.color).multiplyScalar(H.intensity),I.distance=H.distance,I.decay=H.decay,H.castShadow){const Z=H.shadow,$=n.get(H);$.shadowIntensity=Z.intensity,$.shadowBias=Z.bias,$.shadowNormalBias=Z.normalBias,$.shadowRadius=Z.radius,$.shadowMapSize=Z.mapSize,$.shadowCameraNear=Z.camera.near,$.shadowCameraFar=Z.camera.far,s.pointShadow[b]=$,s.pointShadowMap[b]=ct,s.pointShadowMatrix[b]=H.shadow.matrix,N++}s.point[b]=I,b++}else if(H.isHemisphereLight){const I=t.get(H);I.skyColor.copy(H.color).multiplyScalar(ot),I.groundColor.copy(H.groundColor).multiplyScalar(ot),s.hemi[x]=I,x++}}E>0&&(a.has("OES_texture_float_linear")===!0?(s.rectAreaLTC1=Lt.LTC_FLOAT_1,s.rectAreaLTC2=Lt.LTC_FLOAT_2):(s.rectAreaLTC1=Lt.LTC_HALF_1,s.rectAreaLTC2=Lt.LTC_HALF_2)),s.ambient[0]=g,s.ambient[1]=_,s.ambient[2]=y;const G=s.hash;(G.directionalLength!==S||G.pointLength!==b||G.spotLength!==T||G.rectAreaLength!==E||G.hemiLength!==x||G.numDirectionalShadows!==P||G.numPointShadows!==N||G.numSpotShadows!==R||G.numSpotMaps!==V||G.numLightProbes!==z)&&(s.directional.length=S,s.spot.length=T,s.rectArea.length=E,s.point.length=b,s.hemi.length=x,s.directionalShadow.length=P,s.directionalShadowMap.length=P,s.pointShadow.length=N,s.pointShadowMap.length=N,s.spotShadow.length=R,s.spotShadowMap.length=R,s.directionalShadowMatrix.length=P,s.pointShadowMatrix.length=N,s.spotLightMatrix.length=R+V-F,s.spotLightMap.length=V,s.numSpotLightShadowsWithMaps=F,s.numLightProbes=z,G.directionalLength=S,G.pointLength=b,G.spotLength=T,G.rectAreaLength=E,G.hemiLength=x,G.numDirectionalShadows=P,G.numPointShadows=N,G.numSpotShadows=R,G.numSpotMaps=V,G.numLightProbes=z,s.version=Lw++)}function p(m,g){let _=0,y=0,S=0,b=0,T=0;const E=g.matrixWorldInverse;for(let x=0,P=m.length;x<P;x++){const N=m[x];if(N.isDirectionalLight){const R=s.directional[_];R.direction.setFromMatrixPosition(N.matrixWorld),l.setFromMatrixPosition(N.target.matrixWorld),R.direction.sub(l),R.direction.transformDirection(E),_++}else if(N.isSpotLight){const R=s.spot[S];R.position.setFromMatrixPosition(N.matrixWorld),R.position.applyMatrix4(E),R.direction.setFromMatrixPosition(N.matrixWorld),l.setFromMatrixPosition(N.target.matrixWorld),R.direction.sub(l),R.direction.transformDirection(E),S++}else if(N.isRectAreaLight){const R=s.rectArea[b];R.position.setFromMatrixPosition(N.matrixWorld),R.position.applyMatrix4(E),f.identity(),c.copy(N.matrixWorld),c.premultiply(E),f.extractRotation(c),R.halfWidth.set(N.width*.5,0,0),R.halfHeight.set(0,N.height*.5,0),R.halfWidth.applyMatrix4(f),R.halfHeight.applyMatrix4(f),b++}else if(N.isPointLight){const R=s.point[y];R.position.setFromMatrixPosition(N.matrixWorld),R.position.applyMatrix4(E),y++}else if(N.isHemisphereLight){const R=s.hemi[T];R.direction.setFromMatrixPosition(N.matrixWorld),R.direction.transformDirection(E),T++}}}return{setup:d,setupView:p,state:s}}function Gy(a){const t=new Pw(a),n=[],s=[];function l(g){m.camera=g,n.length=0,s.length=0}function c(g){n.push(g)}function f(g){s.push(g)}function d(){t.setup(n)}function p(g){t.setupView(n,g)}const m={lightsArray:n,shadowsArray:s,camera:null,lights:t,transmissionRenderTarget:{}};return{init:l,state:m,setupLights:d,setupLightsView:p,pushLight:c,pushShadow:f}}function zw(a){let t=new WeakMap;function n(l,c=0){const f=t.get(l);let d;return f===void 0?(d=new Gy(a),t.set(l,[d])):c>=f.length?(d=new Gy(a),f.push(d)):d=f[c],d}function s(){t=new WeakMap}return{get:n,dispose:s}}const Iw=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Bw=`uniform sampler2D shadow_pass;
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
}`;function Fw(a,t,n){let s=new Lm;const l=new Wt,c=new Wt,f=new We,d=new cA({depthPacking:Wb}),p=new uA,m={},g=n.maxTextureSize,_={[Rs]:ii,[ii]:Rs,[Da]:Da},y=new Yn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Wt},radius:{value:4}},vertexShader:Iw,fragmentShader:Bw}),S=y.clone();S.defines.HORIZONTAL_PASS=1;const b=new ki;b.setAttribute("position",new ea(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const T=new Wn(b,y),E=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Ux;let x=this.type;this.render=function(F,z,G){if(E.enabled===!1||E.autoUpdate===!1&&E.needsUpdate===!1||F.length===0)return;const U=a.getRenderTarget(),D=a.getActiveCubeFace(),H=a.getActiveMipmapLevel(),ut=a.state;ut.setBlending(La),ut.buffers.color.setClear(1,1,1,1),ut.buffers.depth.setTest(!0),ut.setScissorTest(!1);const ot=x!==Ca&&this.type===Ca,mt=x===Ca&&this.type!==Ca;for(let ct=0,I=F.length;ct<I;ct++){const Z=F[ct],$=Z.shadow;if($===void 0){console.warn("THREE.WebGLShadowMap:",Z,"has no shadow.");continue}if($.autoUpdate===!1&&$.needsUpdate===!1)continue;l.copy($.mapSize);const Et=$.getFrameExtents();if(l.multiply(Et),c.copy($.mapSize),(l.x>g||l.y>g)&&(l.x>g&&(c.x=Math.floor(g/Et.x),l.x=c.x*Et.x,$.mapSize.x=c.x),l.y>g&&(c.y=Math.floor(g/Et.y),l.y=c.y*Et.y,$.mapSize.y=c.y)),$.map===null||ot===!0||mt===!0){const O=this.type!==Ca?{minFilter:Gi,magFilter:Gi}:{};$.map!==null&&$.map.dispose(),$.map=new Vi(l.x,l.y,O),$.map.texture.name=Z.name+".shadowMap",$.camera.updateProjectionMatrix()}a.setRenderTarget($.map),a.clear();const At=$.getViewportCount();for(let O=0;O<At;O++){const nt=$.getViewport(O);f.set(c.x*nt.x,c.y*nt.y,c.x*nt.z,c.y*nt.w),ut.viewport(f),$.updateMatrices(Z,O),s=$.getFrustum(),R(z,G,$.camera,Z,this.type)}$.isPointLightShadow!==!0&&this.type===Ca&&P($,G),$.needsUpdate=!1}x=this.type,E.needsUpdate=!1,a.setRenderTarget(U,D,H)};function P(F,z){const G=t.update(T);y.defines.VSM_SAMPLES!==F.blurSamples&&(y.defines.VSM_SAMPLES=F.blurSamples,S.defines.VSM_SAMPLES=F.blurSamples,y.needsUpdate=!0,S.needsUpdate=!0),F.mapPass===null&&(F.mapPass=new Vi(l.x,l.y)),y.uniforms.shadow_pass.value=F.map.texture,y.uniforms.resolution.value=F.mapSize,y.uniforms.radius.value=F.radius,a.setRenderTarget(F.mapPass),a.clear(),a.renderBufferDirect(z,null,G,y,T,null),S.uniforms.shadow_pass.value=F.mapPass.texture,S.uniforms.resolution.value=F.mapSize,S.uniforms.radius.value=F.radius,a.setRenderTarget(F.map),a.clear(),a.renderBufferDirect(z,null,G,S,T,null)}function N(F,z,G,U){let D=null;const H=G.isPointLight===!0?F.customDistanceMaterial:F.customDepthMaterial;if(H!==void 0)D=H;else if(D=G.isPointLight===!0?p:d,a.localClippingEnabled&&z.clipShadows===!0&&Array.isArray(z.clippingPlanes)&&z.clippingPlanes.length!==0||z.displacementMap&&z.displacementScale!==0||z.alphaMap&&z.alphaTest>0||z.map&&z.alphaTest>0){const ut=D.uuid,ot=z.uuid;let mt=m[ut];mt===void 0&&(mt={},m[ut]=mt);let ct=mt[ot];ct===void 0&&(ct=D.clone(),mt[ot]=ct,z.addEventListener("dispose",V)),D=ct}if(D.visible=z.visible,D.wireframe=z.wireframe,U===Ca?D.side=z.shadowSide!==null?z.shadowSide:z.side:D.side=z.shadowSide!==null?z.shadowSide:_[z.side],D.alphaMap=z.alphaMap,D.alphaTest=z.alphaTest,D.map=z.map,D.clipShadows=z.clipShadows,D.clippingPlanes=z.clippingPlanes,D.clipIntersection=z.clipIntersection,D.displacementMap=z.displacementMap,D.displacementScale=z.displacementScale,D.displacementBias=z.displacementBias,D.wireframeLinewidth=z.wireframeLinewidth,D.linewidth=z.linewidth,G.isPointLight===!0&&D.isMeshDistanceMaterial===!0){const ut=a.properties.get(D);ut.light=G}return D}function R(F,z,G,U,D){if(F.visible===!1)return;if(F.layers.test(z.layers)&&(F.isMesh||F.isLine||F.isPoints)&&(F.castShadow||F.receiveShadow&&D===Ca)&&(!F.frustumCulled||s.intersectsObject(F))){F.modelViewMatrix.multiplyMatrices(G.matrixWorldInverse,F.matrixWorld);const ot=t.update(F),mt=F.material;if(Array.isArray(mt)){const ct=ot.groups;for(let I=0,Z=ct.length;I<Z;I++){const $=ct[I],Et=mt[$.materialIndex];if(Et&&Et.visible){const At=N(F,Et,U,D);F.onBeforeShadow(a,F,z,G,ot,At,$),a.renderBufferDirect(G,null,ot,At,F,$),F.onAfterShadow(a,F,z,G,ot,At,$)}}}else if(mt.visible){const ct=N(F,mt,U,D);F.onBeforeShadow(a,F,z,G,ot,ct,null),a.renderBufferDirect(G,null,ot,ct,F,null),F.onAfterShadow(a,F,z,G,ot,ct,null)}}const ut=F.children;for(let ot=0,mt=ut.length;ot<mt;ot++)R(ut[ot],z,G,U,D)}function V(F){F.target.removeEventListener("dispose",V);for(const G in m){const U=m[G],D=F.target.uuid;D in U&&(U[D].dispose(),delete U[D])}}}const Hw={[Dp]:Np,[Up]:Pp,[Lp]:zp,[Io]:Op,[Np]:Dp,[Pp]:Up,[zp]:Lp,[Op]:Io};function Gw(a,t){function n(){let Y=!1;const Rt=new We;let dt=null;const yt=new We(0,0,0,0);return{setMask:function(wt){dt!==wt&&!Y&&(a.colorMask(wt,wt,wt,wt),dt=wt)},setLocked:function(wt){Y=wt},setClear:function(wt,Nt,ie,tn,_n){_n===!0&&(wt*=tn,Nt*=tn,ie*=tn),Rt.set(wt,Nt,ie,tn),yt.equals(Rt)===!1&&(a.clearColor(wt,Nt,ie,tn),yt.copy(Rt))},reset:function(){Y=!1,dt=null,yt.set(-1,0,0,0)}}}function s(){let Y=!1,Rt=!1,dt=null,yt=null,wt=null;return{setReversed:function(Nt){if(Rt!==Nt){const ie=t.get("EXT_clip_control");Rt?ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.ZERO_TO_ONE_EXT):ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.NEGATIVE_ONE_TO_ONE_EXT);const tn=wt;wt=null,this.setClear(tn)}Rt=Nt},getReversed:function(){return Rt},setTest:function(Nt){Nt?Mt(a.DEPTH_TEST):Ft(a.DEPTH_TEST)},setMask:function(Nt){dt!==Nt&&!Y&&(a.depthMask(Nt),dt=Nt)},setFunc:function(Nt){if(Rt&&(Nt=Hw[Nt]),yt!==Nt){switch(Nt){case Dp:a.depthFunc(a.NEVER);break;case Np:a.depthFunc(a.ALWAYS);break;case Up:a.depthFunc(a.LESS);break;case Io:a.depthFunc(a.LEQUAL);break;case Lp:a.depthFunc(a.EQUAL);break;case Op:a.depthFunc(a.GEQUAL);break;case Pp:a.depthFunc(a.GREATER);break;case zp:a.depthFunc(a.NOTEQUAL);break;default:a.depthFunc(a.LEQUAL)}yt=Nt}},setLocked:function(Nt){Y=Nt},setClear:function(Nt){wt!==Nt&&(Rt&&(Nt=1-Nt),a.clearDepth(Nt),wt=Nt)},reset:function(){Y=!1,dt=null,yt=null,wt=null,Rt=!1}}}function l(){let Y=!1,Rt=null,dt=null,yt=null,wt=null,Nt=null,ie=null,tn=null,_n=null;return{setTest:function(we){Y||(we?Mt(a.STENCIL_TEST):Ft(a.STENCIL_TEST))},setMask:function(we){Rt!==we&&!Y&&(a.stencilMask(we),Rt=we)},setFunc:function(we,Rn,wi){(dt!==we||yt!==Rn||wt!==wi)&&(a.stencilFunc(we,Rn,wi),dt=we,yt=Rn,wt=wi)},setOp:function(we,Rn,wi){(Nt!==we||ie!==Rn||tn!==wi)&&(a.stencilOp(we,Rn,wi),Nt=we,ie=Rn,tn=wi)},setLocked:function(we){Y=we},setClear:function(we){_n!==we&&(a.clearStencil(we),_n=we)},reset:function(){Y=!1,Rt=null,dt=null,yt=null,wt=null,Nt=null,ie=null,tn=null,_n=null}}}const c=new n,f=new s,d=new l,p=new WeakMap,m=new WeakMap;let g={},_={},y=new WeakMap,S=[],b=null,T=!1,E=null,x=null,P=null,N=null,R=null,V=null,F=null,z=new pe(0,0,0),G=0,U=!1,D=null,H=null,ut=null,ot=null,mt=null;const ct=a.getParameter(a.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let I=!1,Z=0;const $=a.getParameter(a.VERSION);$.indexOf("WebGL")!==-1?(Z=parseFloat(/^WebGL (\d)/.exec($)[1]),I=Z>=1):$.indexOf("OpenGL ES")!==-1&&(Z=parseFloat(/^OpenGL ES (\d)/.exec($)[1]),I=Z>=2);let Et=null,At={};const O=a.getParameter(a.SCISSOR_BOX),nt=a.getParameter(a.VIEWPORT),St=new We().fromArray(O),q=new We().fromArray(nt);function ft(Y,Rt,dt,yt){const wt=new Uint8Array(4),Nt=a.createTexture();a.bindTexture(Y,Nt),a.texParameteri(Y,a.TEXTURE_MIN_FILTER,a.NEAREST),a.texParameteri(Y,a.TEXTURE_MAG_FILTER,a.NEAREST);for(let ie=0;ie<dt;ie++)Y===a.TEXTURE_3D||Y===a.TEXTURE_2D_ARRAY?a.texImage3D(Rt,0,a.RGBA,1,1,yt,0,a.RGBA,a.UNSIGNED_BYTE,wt):a.texImage2D(Rt+ie,0,a.RGBA,1,1,0,a.RGBA,a.UNSIGNED_BYTE,wt);return Nt}const Tt={};Tt[a.TEXTURE_2D]=ft(a.TEXTURE_2D,a.TEXTURE_2D,1),Tt[a.TEXTURE_CUBE_MAP]=ft(a.TEXTURE_CUBE_MAP,a.TEXTURE_CUBE_MAP_POSITIVE_X,6),Tt[a.TEXTURE_2D_ARRAY]=ft(a.TEXTURE_2D_ARRAY,a.TEXTURE_2D_ARRAY,1,1),Tt[a.TEXTURE_3D]=ft(a.TEXTURE_3D,a.TEXTURE_3D,1,1),c.setClear(0,0,0,1),f.setClear(1),d.setClear(0),Mt(a.DEPTH_TEST),f.setFunc(Io),me(!1),Se(V0),Mt(a.CULL_FACE),k(La);function Mt(Y){g[Y]!==!0&&(a.enable(Y),g[Y]=!0)}function Ft(Y){g[Y]!==!1&&(a.disable(Y),g[Y]=!1)}function Vt(Y,Rt){return _[Y]!==Rt?(a.bindFramebuffer(Y,Rt),_[Y]=Rt,Y===a.DRAW_FRAMEBUFFER&&(_[a.FRAMEBUFFER]=Rt),Y===a.FRAMEBUFFER&&(_[a.DRAW_FRAMEBUFFER]=Rt),!0):!1}function oe(Y,Rt){let dt=S,yt=!1;if(Y){dt=y.get(Rt),dt===void 0&&(dt=[],y.set(Rt,dt));const wt=Y.textures;if(dt.length!==wt.length||dt[0]!==a.COLOR_ATTACHMENT0){for(let Nt=0,ie=wt.length;Nt<ie;Nt++)dt[Nt]=a.COLOR_ATTACHMENT0+Nt;dt.length=wt.length,yt=!0}}else dt[0]!==a.BACK&&(dt[0]=a.BACK,yt=!0);yt&&a.drawBuffers(dt)}function Ge(Y){return b!==Y?(a.useProgram(Y),b=Y,!0):!1}const ve={[ar]:a.FUNC_ADD,[yb]:a.FUNC_SUBTRACT,[xb]:a.FUNC_REVERSE_SUBTRACT};ve[Sb]=a.MIN,ve[Mb]=a.MAX;const $e={[Eb]:a.ZERO,[bb]:a.ONE,[Tb]:a.SRC_COLOR,[Rp]:a.SRC_ALPHA,[Nb]:a.SRC_ALPHA_SATURATE,[wb]:a.DST_COLOR,[Cb]:a.DST_ALPHA,[Ab]:a.ONE_MINUS_SRC_COLOR,[wp]:a.ONE_MINUS_SRC_ALPHA,[Db]:a.ONE_MINUS_DST_COLOR,[Rb]:a.ONE_MINUS_DST_ALPHA,[Ub]:a.CONSTANT_COLOR,[Lb]:a.ONE_MINUS_CONSTANT_COLOR,[Ob]:a.CONSTANT_ALPHA,[Pb]:a.ONE_MINUS_CONSTANT_ALPHA};function k(Y,Rt,dt,yt,wt,Nt,ie,tn,_n,we){if(Y===La){T===!0&&(Ft(a.BLEND),T=!1);return}if(T===!1&&(Mt(a.BLEND),T=!0),Y!==_b){if(Y!==E||we!==U){if((x!==ar||R!==ar)&&(a.blendEquation(a.FUNC_ADD),x=ar,R=ar),we)switch(Y){case xo:a.blendFuncSeparate(a.ONE,a.ONE_MINUS_SRC_ALPHA,a.ONE,a.ONE_MINUS_SRC_ALPHA);break;case Cp:a.blendFunc(a.ONE,a.ONE);break;case k0:a.blendFuncSeparate(a.ZERO,a.ONE_MINUS_SRC_COLOR,a.ZERO,a.ONE);break;case j0:a.blendFuncSeparate(a.ZERO,a.SRC_COLOR,a.ZERO,a.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}else switch(Y){case xo:a.blendFuncSeparate(a.SRC_ALPHA,a.ONE_MINUS_SRC_ALPHA,a.ONE,a.ONE_MINUS_SRC_ALPHA);break;case Cp:a.blendFunc(a.SRC_ALPHA,a.ONE);break;case k0:a.blendFuncSeparate(a.ZERO,a.ONE_MINUS_SRC_COLOR,a.ZERO,a.ONE);break;case j0:a.blendFunc(a.ZERO,a.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",Y);break}P=null,N=null,V=null,F=null,z.set(0,0,0),G=0,E=Y,U=we}return}wt=wt||Rt,Nt=Nt||dt,ie=ie||yt,(Rt!==x||wt!==R)&&(a.blendEquationSeparate(ve[Rt],ve[wt]),x=Rt,R=wt),(dt!==P||yt!==N||Nt!==V||ie!==F)&&(a.blendFuncSeparate($e[dt],$e[yt],$e[Nt],$e[ie]),P=dt,N=yt,V=Nt,F=ie),(tn.equals(z)===!1||_n!==G)&&(a.blendColor(tn.r,tn.g,tn.b,_n),z.copy(tn),G=_n),E=Y,U=!1}function Pn(Y,Rt){Y.side===Da?Ft(a.CULL_FACE):Mt(a.CULL_FACE);let dt=Y.side===ii;Rt&&(dt=!dt),me(dt),Y.blending===xo&&Y.transparent===!1?k(La):k(Y.blending,Y.blendEquation,Y.blendSrc,Y.blendDst,Y.blendEquationAlpha,Y.blendSrcAlpha,Y.blendDstAlpha,Y.blendColor,Y.blendAlpha,Y.premultipliedAlpha),f.setFunc(Y.depthFunc),f.setTest(Y.depthTest),f.setMask(Y.depthWrite),c.setMask(Y.colorWrite);const yt=Y.stencilWrite;d.setTest(yt),yt&&(d.setMask(Y.stencilWriteMask),d.setFunc(Y.stencilFunc,Y.stencilRef,Y.stencilFuncMask),d.setOp(Y.stencilFail,Y.stencilZFail,Y.stencilZPass)),Be(Y.polygonOffset,Y.polygonOffsetFactor,Y.polygonOffsetUnits),Y.alphaToCoverage===!0?Mt(a.SAMPLE_ALPHA_TO_COVERAGE):Ft(a.SAMPLE_ALPHA_TO_COVERAGE)}function me(Y){D!==Y&&(Y?a.frontFace(a.CW):a.frontFace(a.CCW),D=Y)}function Se(Y){Y!==mb?(Mt(a.CULL_FACE),Y!==H&&(Y===V0?a.cullFace(a.BACK):Y===gb?a.cullFace(a.FRONT):a.cullFace(a.FRONT_AND_BACK))):Ft(a.CULL_FACE),H=Y}function Qt(Y){Y!==ut&&(I&&a.lineWidth(Y),ut=Y)}function Be(Y,Rt,dt){Y?(Mt(a.POLYGON_OFFSET_FILL),(ot!==Rt||mt!==dt)&&(a.polygonOffset(Rt,dt),ot=Rt,mt=dt)):Ft(a.POLYGON_OFFSET_FILL)}function Yt(Y){Y?Mt(a.SCISSOR_TEST):Ft(a.SCISSOR_TEST)}function L(Y){Y===void 0&&(Y=a.TEXTURE0+ct-1),Et!==Y&&(a.activeTexture(Y),Et=Y)}function C(Y,Rt,dt){dt===void 0&&(Et===null?dt=a.TEXTURE0+ct-1:dt=Et);let yt=At[dt];yt===void 0&&(yt={type:void 0,texture:void 0},At[dt]=yt),(yt.type!==Y||yt.texture!==Rt)&&(Et!==dt&&(a.activeTexture(dt),Et=dt),a.bindTexture(Y,Rt||Tt[Y]),yt.type=Y,yt.texture=Rt)}function at(){const Y=At[Et];Y!==void 0&&Y.type!==void 0&&(a.bindTexture(Y.type,null),Y.type=void 0,Y.texture=void 0)}function pt(){try{a.compressedTexImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function bt(){try{a.compressedTexImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function vt(){try{a.texSubImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Xt(){try{a.texSubImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Dt(){try{a.compressedTexSubImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Bt(){try{a.compressedTexSubImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Me(){try{a.texStorage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ct(){try{a.texStorage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Ht(){try{a.texImage2D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function Zt(){try{a.texImage3D.apply(a,arguments)}catch(Y){console.error("THREE.WebGLState:",Y)}}function qt(Y){St.equals(Y)===!1&&(a.scissor(Y.x,Y.y,Y.z,Y.w),St.copy(Y))}function Ot(Y){q.equals(Y)===!1&&(a.viewport(Y.x,Y.y,Y.z,Y.w),q.copy(Y))}function ne(Y,Rt){let dt=m.get(Rt);dt===void 0&&(dt=new WeakMap,m.set(Rt,dt));let yt=dt.get(Y);yt===void 0&&(yt=a.getUniformBlockIndex(Rt,Y.name),dt.set(Y,yt))}function le(Y,Rt){const yt=m.get(Rt).get(Y);p.get(Rt)!==yt&&(a.uniformBlockBinding(Rt,yt,Y.__bindingPointIndex),p.set(Rt,yt))}function Ve(){a.disable(a.BLEND),a.disable(a.CULL_FACE),a.disable(a.DEPTH_TEST),a.disable(a.POLYGON_OFFSET_FILL),a.disable(a.SCISSOR_TEST),a.disable(a.STENCIL_TEST),a.disable(a.SAMPLE_ALPHA_TO_COVERAGE),a.blendEquation(a.FUNC_ADD),a.blendFunc(a.ONE,a.ZERO),a.blendFuncSeparate(a.ONE,a.ZERO,a.ONE,a.ZERO),a.blendColor(0,0,0,0),a.colorMask(!0,!0,!0,!0),a.clearColor(0,0,0,0),a.depthMask(!0),a.depthFunc(a.LESS),f.setReversed(!1),a.clearDepth(1),a.stencilMask(4294967295),a.stencilFunc(a.ALWAYS,0,4294967295),a.stencilOp(a.KEEP,a.KEEP,a.KEEP),a.clearStencil(0),a.cullFace(a.BACK),a.frontFace(a.CCW),a.polygonOffset(0,0),a.activeTexture(a.TEXTURE0),a.bindFramebuffer(a.FRAMEBUFFER,null),a.bindFramebuffer(a.DRAW_FRAMEBUFFER,null),a.bindFramebuffer(a.READ_FRAMEBUFFER,null),a.useProgram(null),a.lineWidth(1),a.scissor(0,0,a.canvas.width,a.canvas.height),a.viewport(0,0,a.canvas.width,a.canvas.height),g={},Et=null,At={},_={},y=new WeakMap,S=[],b=null,T=!1,E=null,x=null,P=null,N=null,R=null,V=null,F=null,z=new pe(0,0,0),G=0,U=!1,D=null,H=null,ut=null,ot=null,mt=null,St.set(0,0,a.canvas.width,a.canvas.height),q.set(0,0,a.canvas.width,a.canvas.height),c.reset(),f.reset(),d.reset()}return{buffers:{color:c,depth:f,stencil:d},enable:Mt,disable:Ft,bindFramebuffer:Vt,drawBuffers:oe,useProgram:Ge,setBlending:k,setMaterial:Pn,setFlipSided:me,setCullFace:Se,setLineWidth:Qt,setPolygonOffset:Be,setScissorTest:Yt,activeTexture:L,bindTexture:C,unbindTexture:at,compressedTexImage2D:pt,compressedTexImage3D:bt,texImage2D:Ht,texImage3D:Zt,updateUBOMapping:ne,uniformBlockBinding:le,texStorage2D:Me,texStorage3D:Ct,texSubImage2D:vt,texSubImage3D:Xt,compressedTexSubImage2D:Dt,compressedTexSubImage3D:Bt,scissor:qt,viewport:Ot,reset:Ve}}function Vw(a,t,n,s,l,c,f){const d=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),m=new Wt,g=new WeakMap;let _;const y=new WeakMap;let S=!1;try{S=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function b(L,C){return S?new OffscreenCanvas(L,C):ff("canvas")}function T(L,C,at){let pt=1;const bt=Yt(L);if((bt.width>at||bt.height>at)&&(pt=at/Math.max(bt.width,bt.height)),pt<1)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap||typeof VideoFrame<"u"&&L instanceof VideoFrame){const vt=Math.floor(pt*bt.width),Xt=Math.floor(pt*bt.height);_===void 0&&(_=b(vt,Xt));const Dt=C?b(vt,Xt):_;return Dt.width=vt,Dt.height=Xt,Dt.getContext("2d").drawImage(L,0,0,vt,Xt),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+bt.width+"x"+bt.height+") to ("+vt+"x"+Xt+")."),Dt}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+bt.width+"x"+bt.height+")."),L;return L}function E(L){return L.generateMipmaps}function x(L){a.generateMipmap(L)}function P(L){return L.isWebGLCubeRenderTarget?a.TEXTURE_CUBE_MAP:L.isWebGL3DRenderTarget?a.TEXTURE_3D:L.isWebGLArrayRenderTarget||L.isCompressedArrayTexture?a.TEXTURE_2D_ARRAY:a.TEXTURE_2D}function N(L,C,at,pt,bt=!1){if(L!==null){if(a[L]!==void 0)return a[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let vt=C;if(C===a.RED&&(at===a.FLOAT&&(vt=a.R32F),at===a.HALF_FLOAT&&(vt=a.R16F),at===a.UNSIGNED_BYTE&&(vt=a.R8)),C===a.RED_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.R8UI),at===a.UNSIGNED_SHORT&&(vt=a.R16UI),at===a.UNSIGNED_INT&&(vt=a.R32UI),at===a.BYTE&&(vt=a.R8I),at===a.SHORT&&(vt=a.R16I),at===a.INT&&(vt=a.R32I)),C===a.RG&&(at===a.FLOAT&&(vt=a.RG32F),at===a.HALF_FLOAT&&(vt=a.RG16F),at===a.UNSIGNED_BYTE&&(vt=a.RG8)),C===a.RG_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RG8UI),at===a.UNSIGNED_SHORT&&(vt=a.RG16UI),at===a.UNSIGNED_INT&&(vt=a.RG32UI),at===a.BYTE&&(vt=a.RG8I),at===a.SHORT&&(vt=a.RG16I),at===a.INT&&(vt=a.RG32I)),C===a.RGB_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RGB8UI),at===a.UNSIGNED_SHORT&&(vt=a.RGB16UI),at===a.UNSIGNED_INT&&(vt=a.RGB32UI),at===a.BYTE&&(vt=a.RGB8I),at===a.SHORT&&(vt=a.RGB16I),at===a.INT&&(vt=a.RGB32I)),C===a.RGBA_INTEGER&&(at===a.UNSIGNED_BYTE&&(vt=a.RGBA8UI),at===a.UNSIGNED_SHORT&&(vt=a.RGBA16UI),at===a.UNSIGNED_INT&&(vt=a.RGBA32UI),at===a.BYTE&&(vt=a.RGBA8I),at===a.SHORT&&(vt=a.RGBA16I),at===a.INT&&(vt=a.RGBA32I)),C===a.RGB&&at===a.UNSIGNED_INT_5_9_9_9_REV&&(vt=a.RGB9_E5),C===a.RGBA){const Xt=bt?cf:Oe.getTransfer(pt);at===a.FLOAT&&(vt=a.RGBA32F),at===a.HALF_FLOAT&&(vt=a.RGBA16F),at===a.UNSIGNED_BYTE&&(vt=Xt===qe?a.SRGB8_ALPHA8:a.RGBA8),at===a.UNSIGNED_SHORT_4_4_4_4&&(vt=a.RGBA4),at===a.UNSIGNED_SHORT_5_5_5_1&&(vt=a.RGB5_A1)}return(vt===a.R16F||vt===a.R32F||vt===a.RG16F||vt===a.RG32F||vt===a.RGBA16F||vt===a.RGBA32F)&&t.get("EXT_color_buffer_float"),vt}function R(L,C){let at;return L?C===null||C===yr||C===Ho?at=a.DEPTH24_STENCIL8:C===Na?at=a.DEPTH32F_STENCIL8:C===nc&&(at=a.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):C===null||C===yr||C===Ho?at=a.DEPTH_COMPONENT24:C===Na?at=a.DEPTH_COMPONENT32F:C===nc&&(at=a.DEPTH_COMPONENT16),at}function V(L,C){return E(L)===!0||L.isFramebufferTexture&&L.minFilter!==Gi&&L.minFilter!==ta?Math.log2(Math.max(C.width,C.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?C.mipmaps.length:1}function F(L){const C=L.target;C.removeEventListener("dispose",F),G(C),C.isVideoTexture&&g.delete(C)}function z(L){const C=L.target;C.removeEventListener("dispose",z),D(C)}function G(L){const C=s.get(L);if(C.__webglInit===void 0)return;const at=L.source,pt=y.get(at);if(pt){const bt=pt[C.__cacheKey];bt.usedTimes--,bt.usedTimes===0&&U(L),Object.keys(pt).length===0&&y.delete(at)}s.remove(L)}function U(L){const C=s.get(L);a.deleteTexture(C.__webglTexture);const at=L.source,pt=y.get(at);delete pt[C.__cacheKey],f.memory.textures--}function D(L){const C=s.get(L);if(L.depthTexture&&(L.depthTexture.dispose(),s.remove(L.depthTexture)),L.isWebGLCubeRenderTarget)for(let pt=0;pt<6;pt++){if(Array.isArray(C.__webglFramebuffer[pt]))for(let bt=0;bt<C.__webglFramebuffer[pt].length;bt++)a.deleteFramebuffer(C.__webglFramebuffer[pt][bt]);else a.deleteFramebuffer(C.__webglFramebuffer[pt]);C.__webglDepthbuffer&&a.deleteRenderbuffer(C.__webglDepthbuffer[pt])}else{if(Array.isArray(C.__webglFramebuffer))for(let pt=0;pt<C.__webglFramebuffer.length;pt++)a.deleteFramebuffer(C.__webglFramebuffer[pt]);else a.deleteFramebuffer(C.__webglFramebuffer);if(C.__webglDepthbuffer&&a.deleteRenderbuffer(C.__webglDepthbuffer),C.__webglMultisampledFramebuffer&&a.deleteFramebuffer(C.__webglMultisampledFramebuffer),C.__webglColorRenderbuffer)for(let pt=0;pt<C.__webglColorRenderbuffer.length;pt++)C.__webglColorRenderbuffer[pt]&&a.deleteRenderbuffer(C.__webglColorRenderbuffer[pt]);C.__webglDepthRenderbuffer&&a.deleteRenderbuffer(C.__webglDepthRenderbuffer)}const at=L.textures;for(let pt=0,bt=at.length;pt<bt;pt++){const vt=s.get(at[pt]);vt.__webglTexture&&(a.deleteTexture(vt.__webglTexture),f.memory.textures--),s.remove(at[pt])}s.remove(L)}let H=0;function ut(){H=0}function ot(){const L=H;return L>=l.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+l.maxTextures),H+=1,L}function mt(L){const C=[];return C.push(L.wrapS),C.push(L.wrapT),C.push(L.wrapR||0),C.push(L.magFilter),C.push(L.minFilter),C.push(L.anisotropy),C.push(L.internalFormat),C.push(L.format),C.push(L.type),C.push(L.generateMipmaps),C.push(L.premultiplyAlpha),C.push(L.flipY),C.push(L.unpackAlignment),C.push(L.colorSpace),C.join()}function ct(L,C){const at=s.get(L);if(L.isVideoTexture&&Qt(L),L.isRenderTargetTexture===!1&&L.version>0&&at.__version!==L.version){const pt=L.image;if(pt===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(pt.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{q(at,L,C);return}}n.bindTexture(a.TEXTURE_2D,at.__webglTexture,a.TEXTURE0+C)}function I(L,C){const at=s.get(L);if(L.version>0&&at.__version!==L.version){q(at,L,C);return}n.bindTexture(a.TEXTURE_2D_ARRAY,at.__webglTexture,a.TEXTURE0+C)}function Z(L,C){const at=s.get(L);if(L.version>0&&at.__version!==L.version){q(at,L,C);return}n.bindTexture(a.TEXTURE_3D,at.__webglTexture,a.TEXTURE0+C)}function $(L,C){const at=s.get(L);if(L.version>0&&at.__version!==L.version){ft(at,L,C);return}n.bindTexture(a.TEXTURE_CUBE_MAP,at.__webglTexture,a.TEXTURE0+C)}const Et={[Fp]:a.REPEAT,[lr]:a.CLAMP_TO_EDGE,[Hp]:a.MIRRORED_REPEAT},At={[Gi]:a.NEAREST,[Xb]:a.NEAREST_MIPMAP_NEAREST,[Ru]:a.NEAREST_MIPMAP_LINEAR,[ta]:a.LINEAR,[Lh]:a.LINEAR_MIPMAP_NEAREST,[cr]:a.LINEAR_MIPMAP_LINEAR},O={[Zb]:a.NEVER,[nT]:a.ALWAYS,[Kb]:a.LESS,[Xx]:a.LEQUAL,[Jb]:a.EQUAL,[eT]:a.GEQUAL,[$b]:a.GREATER,[tT]:a.NOTEQUAL};function nt(L,C){if(C.type===Na&&t.has("OES_texture_float_linear")===!1&&(C.magFilter===ta||C.magFilter===Lh||C.magFilter===Ru||C.magFilter===cr||C.minFilter===ta||C.minFilter===Lh||C.minFilter===Ru||C.minFilter===cr)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),a.texParameteri(L,a.TEXTURE_WRAP_S,Et[C.wrapS]),a.texParameteri(L,a.TEXTURE_WRAP_T,Et[C.wrapT]),(L===a.TEXTURE_3D||L===a.TEXTURE_2D_ARRAY)&&a.texParameteri(L,a.TEXTURE_WRAP_R,Et[C.wrapR]),a.texParameteri(L,a.TEXTURE_MAG_FILTER,At[C.magFilter]),a.texParameteri(L,a.TEXTURE_MIN_FILTER,At[C.minFilter]),C.compareFunction&&(a.texParameteri(L,a.TEXTURE_COMPARE_MODE,a.COMPARE_REF_TO_TEXTURE),a.texParameteri(L,a.TEXTURE_COMPARE_FUNC,O[C.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(C.magFilter===Gi||C.minFilter!==Ru&&C.minFilter!==cr||C.type===Na&&t.has("OES_texture_float_linear")===!1)return;if(C.anisotropy>1||s.get(C).__currentAnisotropy){const at=t.get("EXT_texture_filter_anisotropic");a.texParameterf(L,at.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(C.anisotropy,l.getMaxAnisotropy())),s.get(C).__currentAnisotropy=C.anisotropy}}}function St(L,C){let at=!1;L.__webglInit===void 0&&(L.__webglInit=!0,C.addEventListener("dispose",F));const pt=C.source;let bt=y.get(pt);bt===void 0&&(bt={},y.set(pt,bt));const vt=mt(C);if(vt!==L.__cacheKey){bt[vt]===void 0&&(bt[vt]={texture:a.createTexture(),usedTimes:0},f.memory.textures++,at=!0),bt[vt].usedTimes++;const Xt=bt[L.__cacheKey];Xt!==void 0&&(bt[L.__cacheKey].usedTimes--,Xt.usedTimes===0&&U(C)),L.__cacheKey=vt,L.__webglTexture=bt[vt].texture}return at}function q(L,C,at){let pt=a.TEXTURE_2D;(C.isDataArrayTexture||C.isCompressedArrayTexture)&&(pt=a.TEXTURE_2D_ARRAY),C.isData3DTexture&&(pt=a.TEXTURE_3D);const bt=St(L,C),vt=C.source;n.bindTexture(pt,L.__webglTexture,a.TEXTURE0+at);const Xt=s.get(vt);if(vt.version!==Xt.__version||bt===!0){n.activeTexture(a.TEXTURE0+at);const Dt=Oe.getPrimaries(Oe.workingColorSpace),Bt=C.colorSpace===gs?null:Oe.getPrimaries(C.colorSpace),Me=C.colorSpace===gs||Dt===Bt?a.NONE:a.BROWSER_DEFAULT_WEBGL;a.pixelStorei(a.UNPACK_FLIP_Y_WEBGL,C.flipY),a.pixelStorei(a.UNPACK_PREMULTIPLY_ALPHA_WEBGL,C.premultiplyAlpha),a.pixelStorei(a.UNPACK_ALIGNMENT,C.unpackAlignment),a.pixelStorei(a.UNPACK_COLORSPACE_CONVERSION_WEBGL,Me);let Ct=T(C.image,!1,l.maxTextureSize);Ct=Be(C,Ct);const Ht=c.convert(C.format,C.colorSpace),Zt=c.convert(C.type);let qt=N(C.internalFormat,Ht,Zt,C.colorSpace,C.isVideoTexture);nt(pt,C);let Ot;const ne=C.mipmaps,le=C.isVideoTexture!==!0,Ve=Xt.__version===void 0||bt===!0,Y=vt.dataReady,Rt=V(C,Ct);if(C.isDepthTexture)qt=R(C.format===Go,C.type),Ve&&(le?n.texStorage2D(a.TEXTURE_2D,1,qt,Ct.width,Ct.height):n.texImage2D(a.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,null));else if(C.isDataTexture)if(ne.length>0){le&&Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data);C.generateMipmaps=!1}else le?(Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,Ct.width,Ct.height),Y&&n.texSubImage2D(a.TEXTURE_2D,0,0,0,Ct.width,Ct.height,Ht,Zt,Ct.data)):n.texImage2D(a.TEXTURE_2D,0,qt,Ct.width,Ct.height,0,Ht,Zt,Ct.data);else if(C.isCompressedTexture)if(C.isCompressedArrayTexture){le&&Ve&&n.texStorage3D(a.TEXTURE_2D_ARRAY,Rt,qt,ne[0].width,ne[0].height,Ct.depth);for(let dt=0,yt=ne.length;dt<yt;dt++)if(Ot=ne[dt],C.format!==Fi)if(Ht!==null)if(le){if(Y)if(C.layerUpdates.size>0){const wt=vy(Ot.width,Ot.height,C.format,C.type);for(const Nt of C.layerUpdates){const ie=Ot.data.subarray(Nt*wt/Ot.data.BYTES_PER_ELEMENT,(Nt+1)*wt/Ot.data.BYTES_PER_ELEMENT);n.compressedTexSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,Nt,Ot.width,Ot.height,1,Ht,ie)}C.clearLayerUpdates()}else n.compressedTexSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Ot.data)}else n.compressedTexImage3D(a.TEXTURE_2D_ARRAY,dt,qt,Ot.width,Ot.height,Ct.depth,0,Ot.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else le?Y&&n.texSubImage3D(a.TEXTURE_2D_ARRAY,dt,0,0,0,Ot.width,Ot.height,Ct.depth,Ht,Zt,Ot.data):n.texImage3D(a.TEXTURE_2D_ARRAY,dt,qt,Ot.width,Ot.height,Ct.depth,0,Ht,Zt,Ot.data)}else{le&&Ve&&n.texStorage2D(a.TEXTURE_2D,Rt,qt,ne[0].width,ne[0].height);for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],C.format!==Fi?Ht!==null?le?Y&&n.compressedTexSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Ot.data):n.compressedTexImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ot.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ot.width,Ot.height,Ht,Zt,Ot.data):n.texImage2D(a.TEXTURE_2D,dt,qt,Ot.width,Ot.height,0,Ht,Zt,Ot.data)}else if(C.isDataArrayTexture)if(le){if(Ve&&n.texStorage3D(a.TEXTURE_2D_ARRAY,Rt,qt,Ct.width,Ct.height,Ct.depth),Y)if(C.layerUpdates.size>0){const dt=vy(Ct.width,Ct.height,C.format,C.type);for(const yt of C.layerUpdates){const wt=Ct.data.subarray(yt*dt/Ct.data.BYTES_PER_ELEMENT,(yt+1)*dt/Ct.data.BYTES_PER_ELEMENT);n.texSubImage3D(a.TEXTURE_2D_ARRAY,0,0,0,yt,Ct.width,Ct.height,1,Ht,Zt,wt)}C.clearLayerUpdates()}else n.texSubImage3D(a.TEXTURE_2D_ARRAY,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)}else n.texImage3D(a.TEXTURE_2D_ARRAY,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(C.isData3DTexture)le?(Ve&&n.texStorage3D(a.TEXTURE_3D,Rt,qt,Ct.width,Ct.height,Ct.depth),Y&&n.texSubImage3D(a.TEXTURE_3D,0,0,0,0,Ct.width,Ct.height,Ct.depth,Ht,Zt,Ct.data)):n.texImage3D(a.TEXTURE_3D,0,qt,Ct.width,Ct.height,Ct.depth,0,Ht,Zt,Ct.data);else if(C.isFramebufferTexture){if(Ve)if(le)n.texStorage2D(a.TEXTURE_2D,Rt,qt,Ct.width,Ct.height);else{let dt=Ct.width,yt=Ct.height;for(let wt=0;wt<Rt;wt++)n.texImage2D(a.TEXTURE_2D,wt,qt,dt,yt,0,Ht,Zt,null),dt>>=1,yt>>=1}}else if(ne.length>0){if(le&&Ve){const dt=Yt(ne[0]);n.texStorage2D(a.TEXTURE_2D,Rt,qt,dt.width,dt.height)}for(let dt=0,yt=ne.length;dt<yt;dt++)Ot=ne[dt],le?Y&&n.texSubImage2D(a.TEXTURE_2D,dt,0,0,Ht,Zt,Ot):n.texImage2D(a.TEXTURE_2D,dt,qt,Ht,Zt,Ot);C.generateMipmaps=!1}else if(le){if(Ve){const dt=Yt(Ct);n.texStorage2D(a.TEXTURE_2D,Rt,qt,dt.width,dt.height)}Y&&n.texSubImage2D(a.TEXTURE_2D,0,0,0,Ht,Zt,Ct)}else n.texImage2D(a.TEXTURE_2D,0,qt,Ht,Zt,Ct);E(C)&&x(pt),Xt.__version=vt.version,C.onUpdate&&C.onUpdate(C)}L.__version=C.version}function ft(L,C,at){if(C.image.length!==6)return;const pt=St(L,C),bt=C.source;n.bindTexture(a.TEXTURE_CUBE_MAP,L.__webglTexture,a.TEXTURE0+at);const vt=s.get(bt);if(bt.version!==vt.__version||pt===!0){n.activeTexture(a.TEXTURE0+at);const Xt=Oe.getPrimaries(Oe.workingColorSpace),Dt=C.colorSpace===gs?null:Oe.getPrimaries(C.colorSpace),Bt=C.colorSpace===gs||Xt===Dt?a.NONE:a.BROWSER_DEFAULT_WEBGL;a.pixelStorei(a.UNPACK_FLIP_Y_WEBGL,C.flipY),a.pixelStorei(a.UNPACK_PREMULTIPLY_ALPHA_WEBGL,C.premultiplyAlpha),a.pixelStorei(a.UNPACK_ALIGNMENT,C.unpackAlignment),a.pixelStorei(a.UNPACK_COLORSPACE_CONVERSION_WEBGL,Bt);const Me=C.isCompressedTexture||C.image[0].isCompressedTexture,Ct=C.image[0]&&C.image[0].isDataTexture,Ht=[];for(let yt=0;yt<6;yt++)!Me&&!Ct?Ht[yt]=T(C.image[yt],!0,l.maxCubemapSize):Ht[yt]=Ct?C.image[yt].image:C.image[yt],Ht[yt]=Be(C,Ht[yt]);const Zt=Ht[0],qt=c.convert(C.format,C.colorSpace),Ot=c.convert(C.type),ne=N(C.internalFormat,qt,Ot,C.colorSpace),le=C.isVideoTexture!==!0,Ve=vt.__version===void 0||pt===!0,Y=bt.dataReady;let Rt=V(C,Zt);nt(a.TEXTURE_CUBE_MAP,C);let dt;if(Me){le&&Ve&&n.texStorage2D(a.TEXTURE_CUBE_MAP,Rt,ne,Zt.width,Zt.height);for(let yt=0;yt<6;yt++){dt=Ht[yt].mipmaps;for(let wt=0;wt<dt.length;wt++){const Nt=dt[wt];C.format!==Fi?qt!==null?le?Y&&n.compressedTexSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Nt.width,Nt.height,qt,Nt.data):n.compressedTexImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Nt.width,Nt.height,0,Nt.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,0,0,Nt.width,Nt.height,qt,Ot,Nt.data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt,ne,Nt.width,Nt.height,0,qt,Ot,Nt.data)}}}else{if(dt=C.mipmaps,le&&Ve){dt.length>0&&Rt++;const yt=Yt(Ht[0]);n.texStorage2D(a.TEXTURE_CUBE_MAP,Rt,ne,yt.width,yt.height)}for(let yt=0;yt<6;yt++)if(Ct){le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,Ht[yt].width,Ht[yt].height,qt,Ot,Ht[yt].data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,Ht[yt].width,Ht[yt].height,0,qt,Ot,Ht[yt].data);for(let wt=0;wt<dt.length;wt++){const ie=dt[wt].image[yt].image;le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,ie.width,ie.height,qt,Ot,ie.data):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,ie.width,ie.height,0,qt,Ot,ie.data)}}else{le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,0,0,qt,Ot,Ht[yt]):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,0,ne,qt,Ot,Ht[yt]);for(let wt=0;wt<dt.length;wt++){const Nt=dt[wt];le?Y&&n.texSubImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,0,0,qt,Ot,Nt.image[yt]):n.texImage2D(a.TEXTURE_CUBE_MAP_POSITIVE_X+yt,wt+1,ne,qt,Ot,Nt.image[yt])}}}E(C)&&x(a.TEXTURE_CUBE_MAP),vt.__version=bt.version,C.onUpdate&&C.onUpdate(C)}L.__version=C.version}function Tt(L,C,at,pt,bt,vt){const Xt=c.convert(at.format,at.colorSpace),Dt=c.convert(at.type),Bt=N(at.internalFormat,Xt,Dt,at.colorSpace),Me=s.get(C),Ct=s.get(at);if(Ct.__renderTarget=C,!Me.__hasExternalTextures){const Ht=Math.max(1,C.width>>vt),Zt=Math.max(1,C.height>>vt);bt===a.TEXTURE_3D||bt===a.TEXTURE_2D_ARRAY?n.texImage3D(bt,vt,Bt,Ht,Zt,C.depth,0,Xt,Dt,null):n.texImage2D(bt,vt,Bt,Ht,Zt,0,Xt,Dt,null)}n.bindFramebuffer(a.FRAMEBUFFER,L),Se(C)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,pt,bt,Ct.__webglTexture,0,me(C)):(bt===a.TEXTURE_2D||bt>=a.TEXTURE_CUBE_MAP_POSITIVE_X&&bt<=a.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&a.framebufferTexture2D(a.FRAMEBUFFER,pt,bt,Ct.__webglTexture,vt),n.bindFramebuffer(a.FRAMEBUFFER,null)}function Mt(L,C,at){if(a.bindRenderbuffer(a.RENDERBUFFER,L),C.depthBuffer){const pt=C.depthTexture,bt=pt&&pt.isDepthTexture?pt.type:null,vt=R(C.stencilBuffer,bt),Xt=C.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,Dt=me(C);Se(C)?d.renderbufferStorageMultisampleEXT(a.RENDERBUFFER,Dt,vt,C.width,C.height):at?a.renderbufferStorageMultisample(a.RENDERBUFFER,Dt,vt,C.width,C.height):a.renderbufferStorage(a.RENDERBUFFER,vt,C.width,C.height),a.framebufferRenderbuffer(a.FRAMEBUFFER,Xt,a.RENDERBUFFER,L)}else{const pt=C.textures;for(let bt=0;bt<pt.length;bt++){const vt=pt[bt],Xt=c.convert(vt.format,vt.colorSpace),Dt=c.convert(vt.type),Bt=N(vt.internalFormat,Xt,Dt,vt.colorSpace),Me=me(C);at&&Se(C)===!1?a.renderbufferStorageMultisample(a.RENDERBUFFER,Me,Bt,C.width,C.height):Se(C)?d.renderbufferStorageMultisampleEXT(a.RENDERBUFFER,Me,Bt,C.width,C.height):a.renderbufferStorage(a.RENDERBUFFER,Bt,C.width,C.height)}}a.bindRenderbuffer(a.RENDERBUFFER,null)}function Ft(L,C){if(C&&C.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(n.bindFramebuffer(a.FRAMEBUFFER,L),!(C.depthTexture&&C.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const pt=s.get(C.depthTexture);pt.__renderTarget=C,(!pt.__webglTexture||C.depthTexture.image.width!==C.width||C.depthTexture.image.height!==C.height)&&(C.depthTexture.image.width=C.width,C.depthTexture.image.height=C.height,C.depthTexture.needsUpdate=!0),ct(C.depthTexture,0);const bt=pt.__webglTexture,vt=me(C);if(C.depthTexture.format===So)Se(C)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,a.DEPTH_ATTACHMENT,a.TEXTURE_2D,bt,0,vt):a.framebufferTexture2D(a.FRAMEBUFFER,a.DEPTH_ATTACHMENT,a.TEXTURE_2D,bt,0);else if(C.depthTexture.format===Go)Se(C)?d.framebufferTexture2DMultisampleEXT(a.FRAMEBUFFER,a.DEPTH_STENCIL_ATTACHMENT,a.TEXTURE_2D,bt,0,vt):a.framebufferTexture2D(a.FRAMEBUFFER,a.DEPTH_STENCIL_ATTACHMENT,a.TEXTURE_2D,bt,0);else throw new Error("Unknown depthTexture format")}function Vt(L){const C=s.get(L),at=L.isWebGLCubeRenderTarget===!0;if(C.__boundDepthTexture!==L.depthTexture){const pt=L.depthTexture;if(C.__depthDisposeCallback&&C.__depthDisposeCallback(),pt){const bt=()=>{delete C.__boundDepthTexture,delete C.__depthDisposeCallback,pt.removeEventListener("dispose",bt)};pt.addEventListener("dispose",bt),C.__depthDisposeCallback=bt}C.__boundDepthTexture=pt}if(L.depthTexture&&!C.__autoAllocateDepthBuffer){if(at)throw new Error("target.depthTexture not supported in Cube render targets");Ft(C.__webglFramebuffer,L)}else if(at){C.__webglDepthbuffer=[];for(let pt=0;pt<6;pt++)if(n.bindFramebuffer(a.FRAMEBUFFER,C.__webglFramebuffer[pt]),C.__webglDepthbuffer[pt]===void 0)C.__webglDepthbuffer[pt]=a.createRenderbuffer(),Mt(C.__webglDepthbuffer[pt],L,!1);else{const bt=L.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,vt=C.__webglDepthbuffer[pt];a.bindRenderbuffer(a.RENDERBUFFER,vt),a.framebufferRenderbuffer(a.FRAMEBUFFER,bt,a.RENDERBUFFER,vt)}}else if(n.bindFramebuffer(a.FRAMEBUFFER,C.__webglFramebuffer),C.__webglDepthbuffer===void 0)C.__webglDepthbuffer=a.createRenderbuffer(),Mt(C.__webglDepthbuffer,L,!1);else{const pt=L.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,bt=C.__webglDepthbuffer;a.bindRenderbuffer(a.RENDERBUFFER,bt),a.framebufferRenderbuffer(a.FRAMEBUFFER,pt,a.RENDERBUFFER,bt)}n.bindFramebuffer(a.FRAMEBUFFER,null)}function oe(L,C,at){const pt=s.get(L);C!==void 0&&Tt(pt.__webglFramebuffer,L,L.texture,a.COLOR_ATTACHMENT0,a.TEXTURE_2D,0),at!==void 0&&Vt(L)}function Ge(L){const C=L.texture,at=s.get(L),pt=s.get(C);L.addEventListener("dispose",z);const bt=L.textures,vt=L.isWebGLCubeRenderTarget===!0,Xt=bt.length>1;if(Xt||(pt.__webglTexture===void 0&&(pt.__webglTexture=a.createTexture()),pt.__version=C.version,f.memory.textures++),vt){at.__webglFramebuffer=[];for(let Dt=0;Dt<6;Dt++)if(C.mipmaps&&C.mipmaps.length>0){at.__webglFramebuffer[Dt]=[];for(let Bt=0;Bt<C.mipmaps.length;Bt++)at.__webglFramebuffer[Dt][Bt]=a.createFramebuffer()}else at.__webglFramebuffer[Dt]=a.createFramebuffer()}else{if(C.mipmaps&&C.mipmaps.length>0){at.__webglFramebuffer=[];for(let Dt=0;Dt<C.mipmaps.length;Dt++)at.__webglFramebuffer[Dt]=a.createFramebuffer()}else at.__webglFramebuffer=a.createFramebuffer();if(Xt)for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const Me=s.get(bt[Dt]);Me.__webglTexture===void 0&&(Me.__webglTexture=a.createTexture(),f.memory.textures++)}if(L.samples>0&&Se(L)===!1){at.__webglMultisampledFramebuffer=a.createFramebuffer(),at.__webglColorRenderbuffer=[],n.bindFramebuffer(a.FRAMEBUFFER,at.__webglMultisampledFramebuffer);for(let Dt=0;Dt<bt.length;Dt++){const Bt=bt[Dt];at.__webglColorRenderbuffer[Dt]=a.createRenderbuffer(),a.bindRenderbuffer(a.RENDERBUFFER,at.__webglColorRenderbuffer[Dt]);const Me=c.convert(Bt.format,Bt.colorSpace),Ct=c.convert(Bt.type),Ht=N(Bt.internalFormat,Me,Ct,Bt.colorSpace,L.isXRRenderTarget===!0),Zt=me(L);a.renderbufferStorageMultisample(a.RENDERBUFFER,Zt,Ht,L.width,L.height),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Dt,a.RENDERBUFFER,at.__webglColorRenderbuffer[Dt])}a.bindRenderbuffer(a.RENDERBUFFER,null),L.depthBuffer&&(at.__webglDepthRenderbuffer=a.createRenderbuffer(),Mt(at.__webglDepthRenderbuffer,L,!0)),n.bindFramebuffer(a.FRAMEBUFFER,null)}}if(vt){n.bindTexture(a.TEXTURE_CUBE_MAP,pt.__webglTexture),nt(a.TEXTURE_CUBE_MAP,C);for(let Dt=0;Dt<6;Dt++)if(C.mipmaps&&C.mipmaps.length>0)for(let Bt=0;Bt<C.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Dt][Bt],L,C,a.COLOR_ATTACHMENT0,a.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,Bt);else Tt(at.__webglFramebuffer[Dt],L,C,a.COLOR_ATTACHMENT0,a.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,0);E(C)&&x(a.TEXTURE_CUBE_MAP),n.unbindTexture()}else if(Xt){for(let Dt=0,Bt=bt.length;Dt<Bt;Dt++){const Me=bt[Dt],Ct=s.get(Me);n.bindTexture(a.TEXTURE_2D,Ct.__webglTexture),nt(a.TEXTURE_2D,Me),Tt(at.__webglFramebuffer,L,Me,a.COLOR_ATTACHMENT0+Dt,a.TEXTURE_2D,0),E(Me)&&x(a.TEXTURE_2D)}n.unbindTexture()}else{let Dt=a.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(Dt=L.isWebGL3DRenderTarget?a.TEXTURE_3D:a.TEXTURE_2D_ARRAY),n.bindTexture(Dt,pt.__webglTexture),nt(Dt,C),C.mipmaps&&C.mipmaps.length>0)for(let Bt=0;Bt<C.mipmaps.length;Bt++)Tt(at.__webglFramebuffer[Bt],L,C,a.COLOR_ATTACHMENT0,Dt,Bt);else Tt(at.__webglFramebuffer,L,C,a.COLOR_ATTACHMENT0,Dt,0);E(C)&&x(Dt),n.unbindTexture()}L.depthBuffer&&Vt(L)}function ve(L){const C=L.textures;for(let at=0,pt=C.length;at<pt;at++){const bt=C[at];if(E(bt)){const vt=P(L),Xt=s.get(bt).__webglTexture;n.bindTexture(vt,Xt),x(vt),n.unbindTexture()}}}const $e=[],k=[];function Pn(L){if(L.samples>0){if(Se(L)===!1){const C=L.textures,at=L.width,pt=L.height;let bt=a.COLOR_BUFFER_BIT;const vt=L.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT,Xt=s.get(L),Dt=C.length>1;if(Dt)for(let Bt=0;Bt<C.length;Bt++)n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.RENDERBUFFER,null),n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglFramebuffer),a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.TEXTURE_2D,null,0);n.bindFramebuffer(a.READ_FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),n.bindFramebuffer(a.DRAW_FRAMEBUFFER,Xt.__webglFramebuffer);for(let Bt=0;Bt<C.length;Bt++){if(L.resolveDepthBuffer&&(L.depthBuffer&&(bt|=a.DEPTH_BUFFER_BIT),L.stencilBuffer&&L.resolveStencilBuffer&&(bt|=a.STENCIL_BUFFER_BIT)),Dt){a.framebufferRenderbuffer(a.READ_FRAMEBUFFER,a.COLOR_ATTACHMENT0,a.RENDERBUFFER,Xt.__webglColorRenderbuffer[Bt]);const Me=s.get(C[Bt]).__webglTexture;a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0,a.TEXTURE_2D,Me,0)}a.blitFramebuffer(0,0,at,pt,0,0,at,pt,bt,a.NEAREST),p===!0&&($e.length=0,k.length=0,$e.push(a.COLOR_ATTACHMENT0+Bt),L.depthBuffer&&L.resolveDepthBuffer===!1&&($e.push(vt),k.push(vt),a.invalidateFramebuffer(a.DRAW_FRAMEBUFFER,k)),a.invalidateFramebuffer(a.READ_FRAMEBUFFER,$e))}if(n.bindFramebuffer(a.READ_FRAMEBUFFER,null),n.bindFramebuffer(a.DRAW_FRAMEBUFFER,null),Dt)for(let Bt=0;Bt<C.length;Bt++){n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglMultisampledFramebuffer),a.framebufferRenderbuffer(a.FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.RENDERBUFFER,Xt.__webglColorRenderbuffer[Bt]);const Me=s.get(C[Bt]).__webglTexture;n.bindFramebuffer(a.FRAMEBUFFER,Xt.__webglFramebuffer),a.framebufferTexture2D(a.DRAW_FRAMEBUFFER,a.COLOR_ATTACHMENT0+Bt,a.TEXTURE_2D,Me,0)}n.bindFramebuffer(a.DRAW_FRAMEBUFFER,Xt.__webglMultisampledFramebuffer)}else if(L.depthBuffer&&L.resolveDepthBuffer===!1&&p){const C=L.stencilBuffer?a.DEPTH_STENCIL_ATTACHMENT:a.DEPTH_ATTACHMENT;a.invalidateFramebuffer(a.DRAW_FRAMEBUFFER,[C])}}}function me(L){return Math.min(l.maxSamples,L.samples)}function Se(L){const C=s.get(L);return L.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&C.__useRenderToTexture!==!1}function Qt(L){const C=f.render.frame;g.get(L)!==C&&(g.set(L,C),L.update())}function Be(L,C){const at=L.colorSpace,pt=L.format,bt=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||at!==Vo&&at!==gs&&(Oe.getTransfer(at)===qe?(pt!==Fi||bt!==za)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",at)),C}function Yt(L){return typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement?(m.width=L.naturalWidth||L.width,m.height=L.naturalHeight||L.height):typeof VideoFrame<"u"&&L instanceof VideoFrame?(m.width=L.displayWidth,m.height=L.displayHeight):(m.width=L.width,m.height=L.height),m}this.allocateTextureUnit=ot,this.resetTextureUnits=ut,this.setTexture2D=ct,this.setTexture2DArray=I,this.setTexture3D=Z,this.setTextureCube=$,this.rebindTextures=oe,this.setupRenderTarget=Ge,this.updateRenderTargetMipmap=ve,this.updateMultisampleRenderTarget=Pn,this.setupDepthRenderbuffer=Vt,this.setupFrameBufferTexture=Tt,this.useMultisampledRTT=Se}function kw(a,t){function n(s,l=gs){let c;const f=Oe.getTransfer(l);if(s===za)return a.UNSIGNED_BYTE;if(s===Am)return a.UNSIGNED_SHORT_4_4_4_4;if(s===Cm)return a.UNSIGNED_SHORT_5_5_5_1;if(s===Ix)return a.UNSIGNED_INT_5_9_9_9_REV;if(s===Px)return a.BYTE;if(s===zx)return a.SHORT;if(s===nc)return a.UNSIGNED_SHORT;if(s===Tm)return a.INT;if(s===yr)return a.UNSIGNED_INT;if(s===Na)return a.FLOAT;if(s===Oa)return a.HALF_FLOAT;if(s===Bx)return a.ALPHA;if(s===Fx)return a.RGB;if(s===Fi)return a.RGBA;if(s===Hx)return a.LUMINANCE;if(s===Gx)return a.LUMINANCE_ALPHA;if(s===So)return a.DEPTH_COMPONENT;if(s===Go)return a.DEPTH_STENCIL;if(s===Vx)return a.RED;if(s===Rm)return a.RED_INTEGER;if(s===kx)return a.RG;if(s===wm)return a.RG_INTEGER;if(s===Dm)return a.RGBA_INTEGER;if(s===Ju||s===$u||s===tf||s===ef)if(f===qe)if(c=t.get("WEBGL_compressed_texture_s3tc_srgb"),c!==null){if(s===Ju)return c.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===$u)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===tf)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===ef)return c.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(c=t.get("WEBGL_compressed_texture_s3tc"),c!==null){if(s===Ju)return c.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===$u)return c.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===tf)return c.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===ef)return c.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===Gp||s===Vp||s===kp||s===jp)if(c=t.get("WEBGL_compressed_texture_pvrtc"),c!==null){if(s===Gp)return c.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===Vp)return c.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===kp)return c.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===jp)return c.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===Xp||s===qp||s===Wp)if(c=t.get("WEBGL_compressed_texture_etc"),c!==null){if(s===Xp||s===qp)return f===qe?c.COMPRESSED_SRGB8_ETC2:c.COMPRESSED_RGB8_ETC2;if(s===Wp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:c.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(s===Yp||s===Qp||s===Zp||s===Kp||s===Jp||s===$p||s===tm||s===em||s===nm||s===im||s===am||s===sm||s===rm||s===om)if(c=t.get("WEBGL_compressed_texture_astc"),c!==null){if(s===Yp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:c.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===Qp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:c.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===Zp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:c.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===Kp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:c.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===Jp)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:c.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===$p)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:c.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===tm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:c.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===em)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:c.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===nm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:c.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===im)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:c.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===am)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:c.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===sm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:c.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===rm)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:c.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===om)return f===qe?c.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:c.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===nf||s===lm||s===cm)if(c=t.get("EXT_texture_compression_bptc"),c!==null){if(s===nf)return f===qe?c.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:c.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(s===lm)return c.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(s===cm)return c.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(s===jx||s===um||s===fm||s===dm)if(c=t.get("EXT_texture_compression_rgtc"),c!==null){if(s===nf)return c.COMPRESSED_RED_RGTC1_EXT;if(s===um)return c.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===fm)return c.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===dm)return c.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===Ho?a.UNSIGNED_INT_24_8:a[s]!==void 0?a[s]:null}return{convert:n}}const jw={type:"move"};class fp{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new _o,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new _o,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new W,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new W),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new _o,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new W,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new W),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const n=this._hand;if(n)for(const s of t.hand.values())this._getHandJoint(n,s)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,n,s){let l=null,c=null,f=null;const d=this._targetRay,p=this._grip,m=this._hand;if(t&&n.session.visibilityState!=="visible-blurred"){if(m&&t.hand){f=!0;for(const T of t.hand.values()){const E=n.getJointPose(T,s),x=this._getHandJoint(m,T);E!==null&&(x.matrix.fromArray(E.transform.matrix),x.matrix.decompose(x.position,x.rotation,x.scale),x.matrixWorldNeedsUpdate=!0,x.jointRadius=E.radius),x.visible=E!==null}const g=m.joints["index-finger-tip"],_=m.joints["thumb-tip"],y=g.position.distanceTo(_.position),S=.02,b=.005;m.inputState.pinching&&y>S+b?(m.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!m.inputState.pinching&&y<=S-b&&(m.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else p!==null&&t.gripSpace&&(c=n.getPose(t.gripSpace,s),c!==null&&(p.matrix.fromArray(c.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,c.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(c.linearVelocity)):p.hasLinearVelocity=!1,c.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(c.angularVelocity)):p.hasAngularVelocity=!1));d!==null&&(l=n.getPose(t.targetRaySpace,s),l===null&&c!==null&&(l=c),l!==null&&(d.matrix.fromArray(l.transform.matrix),d.matrix.decompose(d.position,d.rotation,d.scale),d.matrixWorldNeedsUpdate=!0,l.linearVelocity?(d.hasLinearVelocity=!0,d.linearVelocity.copy(l.linearVelocity)):d.hasLinearVelocity=!1,l.angularVelocity?(d.hasAngularVelocity=!0,d.angularVelocity.copy(l.angularVelocity)):d.hasAngularVelocity=!1,this.dispatchEvent(jw)))}return d!==null&&(d.visible=l!==null),p!==null&&(p.visible=c!==null),m!==null&&(m.visible=f!==null),this}_getHandJoint(t,n){if(t.joints[n.jointName]===void 0){const s=new _o;s.matrixAutoUpdate=!1,s.visible=!1,t.joints[n.jointName]=s,t.add(s)}return t.joints[n.jointName]}}const Xw=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,qw=`
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

}`;class Ww{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,n,s){if(this.texture===null){const l=new ai,c=t.properties.get(l);c.__webglTexture=n.texture,(n.depthNear!=s.depthNear||n.depthFar!=s.depthFar)&&(this.depthNear=n.depthNear,this.depthFar=n.depthFar),this.texture=l}}getMesh(t){if(this.texture!==null&&this.mesh===null){const n=t.cameras[0].viewport,s=new Yn({vertexShader:Xw,fragmentShader:qw,uniforms:{depthColor:{value:this.texture},depthWidth:{value:n.z},depthHeight:{value:n.w}}});this.mesh=new Wn(new gf(20,20),s)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Yw extends Xo{constructor(t,n){super();const s=this;let l=null,c=1,f=null,d="local-floor",p=1,m=null,g=null,_=null,y=null,S=null,b=null;const T=new Ww,E=n.getContextAttributes();let x=null,P=null;const N=[],R=[],V=new Wt;let F=null;const z=new _i;z.viewport=new We;const G=new _i;G.viewport=new We;const U=[z,G],D=new mA;let H=null,ut=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(q){let ft=N[q];return ft===void 0&&(ft=new fp,N[q]=ft),ft.getTargetRaySpace()},this.getControllerGrip=function(q){let ft=N[q];return ft===void 0&&(ft=new fp,N[q]=ft),ft.getGripSpace()},this.getHand=function(q){let ft=N[q];return ft===void 0&&(ft=new fp,N[q]=ft),ft.getHandSpace()};function ot(q){const ft=R.indexOf(q.inputSource);if(ft===-1)return;const Tt=N[ft];Tt!==void 0&&(Tt.update(q.inputSource,q.frame,m||f),Tt.dispatchEvent({type:q.type,data:q.inputSource}))}function mt(){l.removeEventListener("select",ot),l.removeEventListener("selectstart",ot),l.removeEventListener("selectend",ot),l.removeEventListener("squeeze",ot),l.removeEventListener("squeezestart",ot),l.removeEventListener("squeezeend",ot),l.removeEventListener("end",mt),l.removeEventListener("inputsourceschange",ct);for(let q=0;q<N.length;q++){const ft=R[q];ft!==null&&(R[q]=null,N[q].disconnect(ft))}H=null,ut=null,T.reset(),t.setRenderTarget(x),S=null,y=null,_=null,l=null,P=null,St.stop(),s.isPresenting=!1,t.setPixelRatio(F),t.setSize(V.width,V.height,!1),s.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(q){c=q,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(q){d=q,s.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return m||f},this.setReferenceSpace=function(q){m=q},this.getBaseLayer=function(){return y!==null?y:S},this.getBinding=function(){return _},this.getFrame=function(){return b},this.getSession=function(){return l},this.setSession=async function(q){if(l=q,l!==null){if(x=t.getRenderTarget(),l.addEventListener("select",ot),l.addEventListener("selectstart",ot),l.addEventListener("selectend",ot),l.addEventListener("squeeze",ot),l.addEventListener("squeezestart",ot),l.addEventListener("squeezeend",ot),l.addEventListener("end",mt),l.addEventListener("inputsourceschange",ct),E.xrCompatible!==!0&&await n.makeXRCompatible(),F=t.getPixelRatio(),t.getSize(V),l.renderState.layers===void 0){const ft={antialias:E.antialias,alpha:!0,depth:E.depth,stencil:E.stencil,framebufferScaleFactor:c};S=new XRWebGLLayer(l,n,ft),l.updateRenderState({baseLayer:S}),t.setPixelRatio(1),t.setSize(S.framebufferWidth,S.framebufferHeight,!1),P=new Vi(S.framebufferWidth,S.framebufferHeight,{format:Fi,type:za,colorSpace:t.outputColorSpace,stencilBuffer:E.stencil})}else{let ft=null,Tt=null,Mt=null;E.depth&&(Mt=E.stencil?n.DEPTH24_STENCIL8:n.DEPTH_COMPONENT24,ft=E.stencil?Go:So,Tt=E.stencil?Ho:yr);const Ft={colorFormat:n.RGBA8,depthFormat:Mt,scaleFactor:c};_=new XRWebGLBinding(l,n),y=_.createProjectionLayer(Ft),l.updateRenderState({layers:[y]}),t.setPixelRatio(1),t.setSize(y.textureWidth,y.textureHeight,!1),P=new Vi(y.textureWidth,y.textureHeight,{format:Fi,type:za,depthTexture:new nS(y.textureWidth,y.textureHeight,Tt,void 0,void 0,void 0,void 0,void 0,void 0,ft),stencilBuffer:E.stencil,colorSpace:t.outputColorSpace,samples:E.antialias?4:0,resolveDepthBuffer:y.ignoreDepthValues===!1})}P.isXRRenderTarget=!0,this.setFoveation(p),m=null,f=await l.requestReferenceSpace(d),St.setContext(l),St.start(),s.isPresenting=!0,s.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(l!==null)return l.environmentBlendMode},this.getDepthTexture=function(){return T.getDepthTexture()};function ct(q){for(let ft=0;ft<q.removed.length;ft++){const Tt=q.removed[ft],Mt=R.indexOf(Tt);Mt>=0&&(R[Mt]=null,N[Mt].disconnect(Tt))}for(let ft=0;ft<q.added.length;ft++){const Tt=q.added[ft];let Mt=R.indexOf(Tt);if(Mt===-1){for(let Vt=0;Vt<N.length;Vt++)if(Vt>=R.length){R.push(Tt),Mt=Vt;break}else if(R[Vt]===null){R[Vt]=Tt,Mt=Vt;break}if(Mt===-1)break}const Ft=N[Mt];Ft&&Ft.connect(Tt)}}const I=new W,Z=new W;function $(q,ft,Tt){I.setFromMatrixPosition(ft.matrixWorld),Z.setFromMatrixPosition(Tt.matrixWorld);const Mt=I.distanceTo(Z),Ft=ft.projectionMatrix.elements,Vt=Tt.projectionMatrix.elements,oe=Ft[14]/(Ft[10]-1),Ge=Ft[14]/(Ft[10]+1),ve=(Ft[9]+1)/Ft[5],$e=(Ft[9]-1)/Ft[5],k=(Ft[8]-1)/Ft[0],Pn=(Vt[8]+1)/Vt[0],me=oe*k,Se=oe*Pn,Qt=Mt/(-k+Pn),Be=Qt*-k;if(ft.matrixWorld.decompose(q.position,q.quaternion,q.scale),q.translateX(Be),q.translateZ(Qt),q.matrixWorld.compose(q.position,q.quaternion,q.scale),q.matrixWorldInverse.copy(q.matrixWorld).invert(),Ft[10]===-1)q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse);else{const Yt=oe+Qt,L=Ge+Qt,C=me-Be,at=Se+(Mt-Be),pt=ve*Ge/L*Yt,bt=$e*Ge/L*Yt;q.projectionMatrix.makePerspective(C,at,pt,bt,Yt,L),q.projectionMatrixInverse.copy(q.projectionMatrix).invert()}}function Et(q,ft){ft===null?q.matrixWorld.copy(q.matrix):q.matrixWorld.multiplyMatrices(ft.matrixWorld,q.matrix),q.matrixWorldInverse.copy(q.matrixWorld).invert()}this.updateCamera=function(q){if(l===null)return;let ft=q.near,Tt=q.far;T.texture!==null&&(T.depthNear>0&&(ft=T.depthNear),T.depthFar>0&&(Tt=T.depthFar)),D.near=G.near=z.near=ft,D.far=G.far=z.far=Tt,(H!==D.near||ut!==D.far)&&(l.updateRenderState({depthNear:D.near,depthFar:D.far}),H=D.near,ut=D.far),z.layers.mask=q.layers.mask|2,G.layers.mask=q.layers.mask|4,D.layers.mask=z.layers.mask|G.layers.mask;const Mt=q.parent,Ft=D.cameras;Et(D,Mt);for(let Vt=0;Vt<Ft.length;Vt++)Et(Ft[Vt],Mt);Ft.length===2?$(D,z,G):D.projectionMatrix.copy(z.projectionMatrix),At(q,D,Mt)};function At(q,ft,Tt){Tt===null?q.matrix.copy(ft.matrixWorld):(q.matrix.copy(Tt.matrixWorld),q.matrix.invert(),q.matrix.multiply(ft.matrixWorld)),q.matrix.decompose(q.position,q.quaternion,q.scale),q.updateMatrixWorld(!0),q.projectionMatrix.copy(ft.projectionMatrix),q.projectionMatrixInverse.copy(ft.projectionMatrixInverse),q.isPerspectiveCamera&&(q.fov=ic*2*Math.atan(1/q.projectionMatrix.elements[5]),q.zoom=1)}this.getCamera=function(){return D},this.getFoveation=function(){if(!(y===null&&S===null))return p},this.setFoveation=function(q){p=q,y!==null&&(y.fixedFoveation=q),S!==null&&S.fixedFoveation!==void 0&&(S.fixedFoveation=q)},this.hasDepthSensing=function(){return T.texture!==null},this.getDepthSensingMesh=function(){return T.getMesh(D)};let O=null;function nt(q,ft){if(g=ft.getViewerPose(m||f),b=ft,g!==null){const Tt=g.views;S!==null&&(t.setRenderTargetFramebuffer(P,S.framebuffer),t.setRenderTarget(P));let Mt=!1;Tt.length!==D.cameras.length&&(D.cameras.length=0,Mt=!0);for(let Vt=0;Vt<Tt.length;Vt++){const oe=Tt[Vt];let Ge=null;if(S!==null)Ge=S.getViewport(oe);else{const $e=_.getViewSubImage(y,oe);Ge=$e.viewport,Vt===0&&(t.setRenderTargetTextures(P,$e.colorTexture,y.ignoreDepthValues?void 0:$e.depthStencilTexture),t.setRenderTarget(P))}let ve=U[Vt];ve===void 0&&(ve=new _i,ve.layers.enable(Vt),ve.viewport=new We,U[Vt]=ve),ve.matrix.fromArray(oe.transform.matrix),ve.matrix.decompose(ve.position,ve.quaternion,ve.scale),ve.projectionMatrix.fromArray(oe.projectionMatrix),ve.projectionMatrixInverse.copy(ve.projectionMatrix).invert(),ve.viewport.set(Ge.x,Ge.y,Ge.width,Ge.height),Vt===0&&(D.matrix.copy(ve.matrix),D.matrix.decompose(D.position,D.quaternion,D.scale)),Mt===!0&&D.cameras.push(ve)}const Ft=l.enabledFeatures;if(Ft&&Ft.includes("depth-sensing")){const Vt=_.getDepthInformation(Tt[0]);Vt&&Vt.isValid&&Vt.texture&&T.init(t,Vt,l.renderState)}}for(let Tt=0;Tt<N.length;Tt++){const Mt=R[Tt],Ft=N[Tt];Mt!==null&&Ft!==void 0&&Ft.update(Mt,ft,m||f)}O&&O(q,ft),ft.detectedPlanes&&s.dispatchEvent({type:"planesdetected",data:ft}),b=null}const St=new cS;St.setAnimationLoop(nt),this.setAnimationLoop=function(q){O=q},this.dispose=function(){}}}const tr=new Ia,Qw=new an;function Zw(a,t){function n(E,x){E.matrixAutoUpdate===!0&&E.updateMatrix(),x.value.copy(E.matrix)}function s(E,x){x.color.getRGB(E.fogColor.value,$x(a)),x.isFog?(E.fogNear.value=x.near,E.fogFar.value=x.far):x.isFogExp2&&(E.fogDensity.value=x.density)}function l(E,x,P,N,R){x.isMeshBasicMaterial||x.isMeshLambertMaterial?c(E,x):x.isMeshToonMaterial?(c(E,x),_(E,x)):x.isMeshPhongMaterial?(c(E,x),g(E,x)):x.isMeshStandardMaterial?(c(E,x),y(E,x),x.isMeshPhysicalMaterial&&S(E,x,R)):x.isMeshMatcapMaterial?(c(E,x),b(E,x)):x.isMeshDepthMaterial?c(E,x):x.isMeshDistanceMaterial?(c(E,x),T(E,x)):x.isMeshNormalMaterial?c(E,x):x.isLineBasicMaterial?(f(E,x),x.isLineDashedMaterial&&d(E,x)):x.isPointsMaterial?p(E,x,P,N):x.isSpriteMaterial?m(E,x):x.isShadowMaterial?(E.color.value.copy(x.color),E.opacity.value=x.opacity):x.isShaderMaterial&&(x.uniformsNeedUpdate=!1)}function c(E,x){E.opacity.value=x.opacity,x.color&&E.diffuse.value.copy(x.color),x.emissive&&E.emissive.value.copy(x.emissive).multiplyScalar(x.emissiveIntensity),x.map&&(E.map.value=x.map,n(x.map,E.mapTransform)),x.alphaMap&&(E.alphaMap.value=x.alphaMap,n(x.alphaMap,E.alphaMapTransform)),x.bumpMap&&(E.bumpMap.value=x.bumpMap,n(x.bumpMap,E.bumpMapTransform),E.bumpScale.value=x.bumpScale,x.side===ii&&(E.bumpScale.value*=-1)),x.normalMap&&(E.normalMap.value=x.normalMap,n(x.normalMap,E.normalMapTransform),E.normalScale.value.copy(x.normalScale),x.side===ii&&E.normalScale.value.negate()),x.displacementMap&&(E.displacementMap.value=x.displacementMap,n(x.displacementMap,E.displacementMapTransform),E.displacementScale.value=x.displacementScale,E.displacementBias.value=x.displacementBias),x.emissiveMap&&(E.emissiveMap.value=x.emissiveMap,n(x.emissiveMap,E.emissiveMapTransform)),x.specularMap&&(E.specularMap.value=x.specularMap,n(x.specularMap,E.specularMapTransform)),x.alphaTest>0&&(E.alphaTest.value=x.alphaTest);const P=t.get(x),N=P.envMap,R=P.envMapRotation;N&&(E.envMap.value=N,tr.copy(R),tr.x*=-1,tr.y*=-1,tr.z*=-1,N.isCubeTexture&&N.isRenderTargetTexture===!1&&(tr.y*=-1,tr.z*=-1),E.envMapRotation.value.setFromMatrix4(Qw.makeRotationFromEuler(tr)),E.flipEnvMap.value=N.isCubeTexture&&N.isRenderTargetTexture===!1?-1:1,E.reflectivity.value=x.reflectivity,E.ior.value=x.ior,E.refractionRatio.value=x.refractionRatio),x.lightMap&&(E.lightMap.value=x.lightMap,E.lightMapIntensity.value=x.lightMapIntensity,n(x.lightMap,E.lightMapTransform)),x.aoMap&&(E.aoMap.value=x.aoMap,E.aoMapIntensity.value=x.aoMapIntensity,n(x.aoMap,E.aoMapTransform))}function f(E,x){E.diffuse.value.copy(x.color),E.opacity.value=x.opacity,x.map&&(E.map.value=x.map,n(x.map,E.mapTransform))}function d(E,x){E.dashSize.value=x.dashSize,E.totalSize.value=x.dashSize+x.gapSize,E.scale.value=x.scale}function p(E,x,P,N){E.diffuse.value.copy(x.color),E.opacity.value=x.opacity,E.size.value=x.size*P,E.scale.value=N*.5,x.map&&(E.map.value=x.map,n(x.map,E.uvTransform)),x.alphaMap&&(E.alphaMap.value=x.alphaMap,n(x.alphaMap,E.alphaMapTransform)),x.alphaTest>0&&(E.alphaTest.value=x.alphaTest)}function m(E,x){E.diffuse.value.copy(x.color),E.opacity.value=x.opacity,E.rotation.value=x.rotation,x.map&&(E.map.value=x.map,n(x.map,E.mapTransform)),x.alphaMap&&(E.alphaMap.value=x.alphaMap,n(x.alphaMap,E.alphaMapTransform)),x.alphaTest>0&&(E.alphaTest.value=x.alphaTest)}function g(E,x){E.specular.value.copy(x.specular),E.shininess.value=Math.max(x.shininess,1e-4)}function _(E,x){x.gradientMap&&(E.gradientMap.value=x.gradientMap)}function y(E,x){E.metalness.value=x.metalness,x.metalnessMap&&(E.metalnessMap.value=x.metalnessMap,n(x.metalnessMap,E.metalnessMapTransform)),E.roughness.value=x.roughness,x.roughnessMap&&(E.roughnessMap.value=x.roughnessMap,n(x.roughnessMap,E.roughnessMapTransform)),x.envMap&&(E.envMapIntensity.value=x.envMapIntensity)}function S(E,x,P){E.ior.value=x.ior,x.sheen>0&&(E.sheenColor.value.copy(x.sheenColor).multiplyScalar(x.sheen),E.sheenRoughness.value=x.sheenRoughness,x.sheenColorMap&&(E.sheenColorMap.value=x.sheenColorMap,n(x.sheenColorMap,E.sheenColorMapTransform)),x.sheenRoughnessMap&&(E.sheenRoughnessMap.value=x.sheenRoughnessMap,n(x.sheenRoughnessMap,E.sheenRoughnessMapTransform))),x.clearcoat>0&&(E.clearcoat.value=x.clearcoat,E.clearcoatRoughness.value=x.clearcoatRoughness,x.clearcoatMap&&(E.clearcoatMap.value=x.clearcoatMap,n(x.clearcoatMap,E.clearcoatMapTransform)),x.clearcoatRoughnessMap&&(E.clearcoatRoughnessMap.value=x.clearcoatRoughnessMap,n(x.clearcoatRoughnessMap,E.clearcoatRoughnessMapTransform)),x.clearcoatNormalMap&&(E.clearcoatNormalMap.value=x.clearcoatNormalMap,n(x.clearcoatNormalMap,E.clearcoatNormalMapTransform),E.clearcoatNormalScale.value.copy(x.clearcoatNormalScale),x.side===ii&&E.clearcoatNormalScale.value.negate())),x.dispersion>0&&(E.dispersion.value=x.dispersion),x.iridescence>0&&(E.iridescence.value=x.iridescence,E.iridescenceIOR.value=x.iridescenceIOR,E.iridescenceThicknessMinimum.value=x.iridescenceThicknessRange[0],E.iridescenceThicknessMaximum.value=x.iridescenceThicknessRange[1],x.iridescenceMap&&(E.iridescenceMap.value=x.iridescenceMap,n(x.iridescenceMap,E.iridescenceMapTransform)),x.iridescenceThicknessMap&&(E.iridescenceThicknessMap.value=x.iridescenceThicknessMap,n(x.iridescenceThicknessMap,E.iridescenceThicknessMapTransform))),x.transmission>0&&(E.transmission.value=x.transmission,E.transmissionSamplerMap.value=P.texture,E.transmissionSamplerSize.value.set(P.width,P.height),x.transmissionMap&&(E.transmissionMap.value=x.transmissionMap,n(x.transmissionMap,E.transmissionMapTransform)),E.thickness.value=x.thickness,x.thicknessMap&&(E.thicknessMap.value=x.thicknessMap,n(x.thicknessMap,E.thicknessMapTransform)),E.attenuationDistance.value=x.attenuationDistance,E.attenuationColor.value.copy(x.attenuationColor)),x.anisotropy>0&&(E.anisotropyVector.value.set(x.anisotropy*Math.cos(x.anisotropyRotation),x.anisotropy*Math.sin(x.anisotropyRotation)),x.anisotropyMap&&(E.anisotropyMap.value=x.anisotropyMap,n(x.anisotropyMap,E.anisotropyMapTransform))),E.specularIntensity.value=x.specularIntensity,E.specularColor.value.copy(x.specularColor),x.specularColorMap&&(E.specularColorMap.value=x.specularColorMap,n(x.specularColorMap,E.specularColorMapTransform)),x.specularIntensityMap&&(E.specularIntensityMap.value=x.specularIntensityMap,n(x.specularIntensityMap,E.specularIntensityMapTransform))}function b(E,x){x.matcap&&(E.matcap.value=x.matcap)}function T(E,x){const P=t.get(x).light;E.referencePosition.value.setFromMatrixPosition(P.matrixWorld),E.nearDistance.value=P.shadow.camera.near,E.farDistance.value=P.shadow.camera.far}return{refreshFogUniforms:s,refreshMaterialUniforms:l}}function Kw(a,t,n,s){let l={},c={},f=[];const d=a.getParameter(a.MAX_UNIFORM_BUFFER_BINDINGS);function p(P,N){const R=N.program;s.uniformBlockBinding(P,R)}function m(P,N){let R=l[P.id];R===void 0&&(b(P),R=g(P),l[P.id]=R,P.addEventListener("dispose",E));const V=N.program;s.updateUBOMapping(P,V);const F=t.render.frame;c[P.id]!==F&&(y(P),c[P.id]=F)}function g(P){const N=_();P.__bindingPointIndex=N;const R=a.createBuffer(),V=P.__size,F=P.usage;return a.bindBuffer(a.UNIFORM_BUFFER,R),a.bufferData(a.UNIFORM_BUFFER,V,F),a.bindBuffer(a.UNIFORM_BUFFER,null),a.bindBufferBase(a.UNIFORM_BUFFER,N,R),R}function _(){for(let P=0;P<d;P++)if(f.indexOf(P)===-1)return f.push(P),P;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function y(P){const N=l[P.id],R=P.uniforms,V=P.__cache;a.bindBuffer(a.UNIFORM_BUFFER,N);for(let F=0,z=R.length;F<z;F++){const G=Array.isArray(R[F])?R[F]:[R[F]];for(let U=0,D=G.length;U<D;U++){const H=G[U];if(S(H,F,U,V)===!0){const ut=H.__offset,ot=Array.isArray(H.value)?H.value:[H.value];let mt=0;for(let ct=0;ct<ot.length;ct++){const I=ot[ct],Z=T(I);typeof I=="number"||typeof I=="boolean"?(H.__data[0]=I,a.bufferSubData(a.UNIFORM_BUFFER,ut+mt,H.__data)):I.isMatrix3?(H.__data[0]=I.elements[0],H.__data[1]=I.elements[1],H.__data[2]=I.elements[2],H.__data[3]=0,H.__data[4]=I.elements[3],H.__data[5]=I.elements[4],H.__data[6]=I.elements[5],H.__data[7]=0,H.__data[8]=I.elements[6],H.__data[9]=I.elements[7],H.__data[10]=I.elements[8],H.__data[11]=0):(I.toArray(H.__data,mt),mt+=Z.storage/Float32Array.BYTES_PER_ELEMENT)}a.bufferSubData(a.UNIFORM_BUFFER,ut,H.__data)}}}a.bindBuffer(a.UNIFORM_BUFFER,null)}function S(P,N,R,V){const F=P.value,z=N+"_"+R;if(V[z]===void 0)return typeof F=="number"||typeof F=="boolean"?V[z]=F:V[z]=F.clone(),!0;{const G=V[z];if(typeof F=="number"||typeof F=="boolean"){if(G!==F)return V[z]=F,!0}else if(G.equals(F)===!1)return G.copy(F),!0}return!1}function b(P){const N=P.uniforms;let R=0;const V=16;for(let z=0,G=N.length;z<G;z++){const U=Array.isArray(N[z])?N[z]:[N[z]];for(let D=0,H=U.length;D<H;D++){const ut=U[D],ot=Array.isArray(ut.value)?ut.value:[ut.value];for(let mt=0,ct=ot.length;mt<ct;mt++){const I=ot[mt],Z=T(I),$=R%V,Et=$%Z.boundary,At=$+Et;R+=Et,At!==0&&V-At<Z.storage&&(R+=V-At),ut.__data=new Float32Array(Z.storage/Float32Array.BYTES_PER_ELEMENT),ut.__offset=R,R+=Z.storage}}}const F=R%V;return F>0&&(R+=V-F),P.__size=R,P.__cache={},this}function T(P){const N={boundary:0,storage:0};return typeof P=="number"||typeof P=="boolean"?(N.boundary=4,N.storage=4):P.isVector2?(N.boundary=8,N.storage=8):P.isVector3||P.isColor?(N.boundary=16,N.storage=12):P.isVector4?(N.boundary=16,N.storage=16):P.isMatrix3?(N.boundary=48,N.storage=48):P.isMatrix4?(N.boundary=64,N.storage=64):P.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",P),N}function E(P){const N=P.target;N.removeEventListener("dispose",E);const R=f.indexOf(N.__bindingPointIndex);f.splice(R,1),a.deleteBuffer(l[N.id]),delete l[N.id],delete c[N.id]}function x(){for(const P in l)a.deleteBuffer(l[P]);f=[],l={},c={}}return{bind:p,update:m,dispose:x}}class Jw{constructor(t={}){const{canvas:n=yT(),context:s=null,depth:l=!0,stencil:c=!1,alpha:f=!1,antialias:d=!1,premultipliedAlpha:p=!0,preserveDrawingBuffer:m=!1,powerPreference:g="default",failIfMajorPerformanceCaveat:_=!1,reverseDepthBuffer:y=!1}=t;this.isWebGLRenderer=!0;let S;if(s!==null){if(typeof WebGLRenderingContext<"u"&&s instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");S=s.getContextAttributes().alpha}else S=f;const b=new Uint32Array(4),T=new Int32Array(4);let E=null,x=null;const P=[],N=[];this.domElement=n,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=vi,this.toneMapping=Cs,this.toneMappingExposure=1;const R=this;let V=!1,F=0,z=0,G=null,U=-1,D=null;const H=new We,ut=new We;let ot=null;const mt=new pe(0);let ct=0,I=n.width,Z=n.height,$=1,Et=null,At=null;const O=new We(0,0,I,Z),nt=new We(0,0,I,Z);let St=!1;const q=new Lm;let ft=!1,Tt=!1;const Mt=new an,Ft=new an,Vt=new W,oe=new We,Ge={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ve=!1;function $e(){return G===null?$:1}let k=s;function Pn(w,Q){return n.getContext(w,Q)}try{const w={alpha:!0,depth:l,stencil:c,antialias:d,premultipliedAlpha:p,preserveDrawingBuffer:m,powerPreference:g,failIfMajorPerformanceCaveat:_};if("setAttribute"in n&&n.setAttribute("data-engine",`three.js r${bm}`),n.addEventListener("webglcontextlost",yt,!1),n.addEventListener("webglcontextrestored",wt,!1),n.addEventListener("webglcontextcreationerror",Nt,!1),k===null){const Q="webgl2";if(k=Pn(Q,w),k===null)throw Pn(Q)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(w){throw console.error("THREE.WebGLRenderer: "+w.message),w}let me,Se,Qt,Be,Yt,L,C,at,pt,bt,vt,Xt,Dt,Bt,Me,Ct,Ht,Zt,qt,Ot,ne,le,Ve,Y;function Rt(){me=new oR(k),me.init(),le=new kw(k,me),Se=new eR(k,me,t,le),Qt=new Gw(k,me),Se.reverseDepthBuffer&&y&&Qt.buffers.depth.setReversed(!0),Be=new uR(k),Yt=new Rw,L=new Vw(k,me,Qt,Yt,Se,le,Be),C=new iR(R),at=new rR(R),pt=new vA(k),Ve=new $C(k,pt),bt=new lR(k,pt,Be,Ve),vt=new dR(k,bt,pt,Be),qt=new fR(k,Se,L),Ct=new nR(Yt),Xt=new Cw(R,C,at,me,Se,Ve,Ct),Dt=new Zw(R,Yt),Bt=new Dw,Me=new zw(me),Zt=new JC(R,C,at,Qt,vt,S,p),Ht=new Fw(R,vt,Se),Y=new Kw(k,Be,Se,Qt),Ot=new tR(k,me,Be),ne=new cR(k,me,Be),Be.programs=Xt.programs,R.capabilities=Se,R.extensions=me,R.properties=Yt,R.renderLists=Bt,R.shadowMap=Ht,R.state=Qt,R.info=Be}Rt();const dt=new Yw(R,k);this.xr=dt,this.getContext=function(){return k},this.getContextAttributes=function(){return k.getContextAttributes()},this.forceContextLoss=function(){const w=me.get("WEBGL_lose_context");w&&w.loseContext()},this.forceContextRestore=function(){const w=me.get("WEBGL_lose_context");w&&w.restoreContext()},this.getPixelRatio=function(){return $},this.setPixelRatio=function(w){w!==void 0&&($=w,this.setSize(I,Z,!1))},this.getSize=function(w){return w.set(I,Z)},this.setSize=function(w,Q,st=!0){if(dt.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}I=w,Z=Q,n.width=Math.floor(w*$),n.height=Math.floor(Q*$),st===!0&&(n.style.width=w+"px",n.style.height=Q+"px"),this.setViewport(0,0,w,Q)},this.getDrawingBufferSize=function(w){return w.set(I*$,Z*$).floor()},this.setDrawingBufferSize=function(w,Q,st){I=w,Z=Q,$=st,n.width=Math.floor(w*st),n.height=Math.floor(Q*st),this.setViewport(0,0,w,Q)},this.getCurrentViewport=function(w){return w.copy(H)},this.getViewport=function(w){return w.copy(O)},this.setViewport=function(w,Q,st,rt){w.isVector4?O.set(w.x,w.y,w.z,w.w):O.set(w,Q,st,rt),Qt.viewport(H.copy(O).multiplyScalar($).round())},this.getScissor=function(w){return w.copy(nt)},this.setScissor=function(w,Q,st,rt){w.isVector4?nt.set(w.x,w.y,w.z,w.w):nt.set(w,Q,st,rt),Qt.scissor(ut.copy(nt).multiplyScalar($).round())},this.getScissorTest=function(){return St},this.setScissorTest=function(w){Qt.setScissorTest(St=w)},this.setOpaqueSort=function(w){Et=w},this.setTransparentSort=function(w){At=w},this.getClearColor=function(w){return w.copy(Zt.getClearColor())},this.setClearColor=function(){Zt.setClearColor.apply(Zt,arguments)},this.getClearAlpha=function(){return Zt.getClearAlpha()},this.setClearAlpha=function(){Zt.setClearAlpha.apply(Zt,arguments)},this.clear=function(w=!0,Q=!0,st=!0){let rt=0;if(w){let K=!1;if(G!==null){const xt=G.texture.format;K=xt===Dm||xt===wm||xt===Rm}if(K){const xt=G.texture.type,Ut=xt===za||xt===yr||xt===nc||xt===Ho||xt===Am||xt===Cm,It=Zt.getClearColor(),Pt=Zt.getClearAlpha(),$t=It.r,ae=It.g,Kt=It.b;Ut?(b[0]=$t,b[1]=ae,b[2]=Kt,b[3]=Pt,k.clearBufferuiv(k.COLOR,0,b)):(T[0]=$t,T[1]=ae,T[2]=Kt,T[3]=Pt,k.clearBufferiv(k.COLOR,0,T))}else rt|=k.COLOR_BUFFER_BIT}Q&&(rt|=k.DEPTH_BUFFER_BIT),st&&(rt|=k.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),k.clear(rt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){n.removeEventListener("webglcontextlost",yt,!1),n.removeEventListener("webglcontextrestored",wt,!1),n.removeEventListener("webglcontextcreationerror",Nt,!1),Zt.dispose(),Bt.dispose(),Me.dispose(),Yt.dispose(),C.dispose(),at.dispose(),vt.dispose(),Ve.dispose(),Y.dispose(),Xt.dispose(),dt.dispose(),dt.removeEventListener("sessionstart",Yo),dt.removeEventListener("sessionend",Qo),ji.stop()};function yt(w){w.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),V=!0}function wt(){console.log("THREE.WebGLRenderer: Context Restored."),V=!1;const w=Be.autoReset,Q=Ht.enabled,st=Ht.autoUpdate,rt=Ht.needsUpdate,K=Ht.type;Rt(),Be.autoReset=w,Ht.enabled=Q,Ht.autoUpdate=st,Ht.needsUpdate=rt,Ht.type=K}function Nt(w){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",w.statusMessage)}function ie(w){const Q=w.target;Q.removeEventListener("dispose",ie),tn(Q)}function tn(w){_n(w),Yt.remove(w)}function _n(w){const Q=Yt.get(w).programs;Q!==void 0&&(Q.forEach(function(st){Xt.releaseProgram(st)}),w.isShaderMaterial&&Xt.releaseShaderCache(w))}this.renderBufferDirect=function(w,Q,st,rt,K,xt){Q===null&&(Q=Ge);const Ut=K.isMesh&&K.matrixWorld.determinant()<0,It=Ko(w,Q,st,rt,K);Qt.setMaterial(rt,Ut);let Pt=st.index,$t=1;if(rt.wireframe===!0){if(Pt=bt.getWireframeAttribute(st),Pt===void 0)return;$t=2}const ae=st.drawRange,Kt=st.attributes.position;let Ee=ae.start*$t,De=(ae.start+ae.count)*$t;xt!==null&&(Ee=Math.max(Ee,xt.start*$t),De=Math.min(De,(xt.start+xt.count)*$t)),Pt!==null?(Ee=Math.max(Ee,0),De=Math.min(De,Pt.count)):Kt!=null&&(Ee=Math.max(Ee,0),De=Math.min(De,Kt.count));const Ze=De-Ee;if(Ze<0||Ze===1/0)return;Ve.setup(K,rt,It,st,Pt);let Ye,ce=Ot;if(Pt!==null&&(Ye=pt.get(Pt),ce=ne,ce.setIndex(Ye)),K.isMesh)rt.wireframe===!0?(Qt.setLineWidth(rt.wireframeLinewidth*$e()),ce.setMode(k.LINES)):ce.setMode(k.TRIANGLES);else if(K.isLine){let kt=rt.linewidth;kt===void 0&&(kt=1),Qt.setLineWidth(kt*$e()),K.isLineSegments?ce.setMode(k.LINES):K.isLineLoop?ce.setMode(k.LINE_LOOP):ce.setMode(k.LINE_STRIP)}else K.isPoints?ce.setMode(k.POINTS):K.isSprite&&ce.setMode(k.TRIANGLES);if(K.isBatchedMesh)if(K._multiDrawInstances!==null)ce.renderMultiDrawInstances(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount,K._multiDrawInstances);else if(me.get("WEBGL_multi_draw"))ce.renderMultiDraw(K._multiDrawStarts,K._multiDrawCounts,K._multiDrawCount);else{const kt=K._multiDrawStarts,dn=K._multiDrawCounts,Ne=K._multiDrawCount,Gn=Pt?pt.get(Pt).bytesPerElement:1,ia=Yt.get(rt).currentProgram.getUniforms();for(let En=0;En<Ne;En++)ia.setValue(k,"_gl_DrawID",En),ce.render(kt[En]/Gn,dn[En])}else if(K.isInstancedMesh)ce.renderInstances(Ee,Ze,K.count);else if(st.isInstancedBufferGeometry){const kt=st._maxInstanceCount!==void 0?st._maxInstanceCount:1/0,dn=Math.min(st.instanceCount,kt);ce.renderInstances(Ee,Ze,dn)}else ce.render(Ee,Ze)};function we(w,Q,st){w.transparent===!0&&w.side===Da&&w.forceSinglePass===!1?(w.side=ii,w.needsUpdate=!0,sn(w,Q,st),w.side=Rs,w.needsUpdate=!0,sn(w,Q,st),w.side=Da):sn(w,Q,st)}this.compile=function(w,Q,st=null){st===null&&(st=w),x=Me.get(st),x.init(Q),N.push(x),st.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(x.pushLight(K),K.castShadow&&x.pushShadow(K))}),w!==st&&w.traverseVisible(function(K){K.isLight&&K.layers.test(Q.layers)&&(x.pushLight(K),K.castShadow&&x.pushShadow(K))}),x.setupLights();const rt=new Set;return w.traverse(function(K){if(!(K.isMesh||K.isPoints||K.isLine||K.isSprite))return;const xt=K.material;if(xt)if(Array.isArray(xt))for(let Ut=0;Ut<xt.length;Ut++){const It=xt[Ut];we(It,st,K),rt.add(It)}else we(xt,st,K),rt.add(xt)}),N.pop(),x=null,rt},this.compileAsync=function(w,Q,st=null){const rt=this.compile(w,Q,st);return new Promise(K=>{function xt(){if(rt.forEach(function(Ut){Yt.get(Ut).currentProgram.isReady()&&rt.delete(Ut)}),rt.size===0){K(w);return}setTimeout(xt,10)}me.get("KHR_parallel_shader_compile")!==null?xt():setTimeout(xt,10)})};let Rn=null;function wi(w){Rn&&Rn(w)}function Yo(){ji.stop()}function Qo(){ji.start()}const ji=new cS;ji.setAnimationLoop(wi),typeof self<"u"&&ji.setContext(self),this.setAnimationLoop=function(w){Rn=w,dt.setAnimationLoop(w),w===null?ji.stop():ji.start()},dt.addEventListener("sessionstart",Yo),dt.addEventListener("sessionend",Qo),this.render=function(w,Q){if(Q!==void 0&&Q.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(V===!0)return;if(w.matrixWorldAutoUpdate===!0&&w.updateMatrixWorld(),Q.parent===null&&Q.matrixWorldAutoUpdate===!0&&Q.updateMatrixWorld(),dt.enabled===!0&&dt.isPresenting===!0&&(dt.cameraAutoUpdate===!0&&dt.updateCamera(Q),Q=dt.getCamera()),w.isScene===!0&&w.onBeforeRender(R,w,Q,G),x=Me.get(w,N.length),x.init(Q),N.push(x),Ft.multiplyMatrices(Q.projectionMatrix,Q.matrixWorldInverse),q.setFromProjectionMatrix(Ft),Tt=this.localClippingEnabled,ft=Ct.init(this.clippingPlanes,Tt),E=Bt.get(w,P.length),E.init(),P.push(E),dt.enabled===!0&&dt.isPresenting===!0){const xt=R.xr.getDepthSensingMesh();xt!==null&&ws(xt,Q,-1/0,R.sortObjects)}ws(w,Q,0,R.sortObjects),E.finish(),R.sortObjects===!0&&E.sort(Et,At),ve=dt.enabled===!1||dt.isPresenting===!1||dt.hasDepthSensing()===!1,ve&&Zt.addToRenderList(E,w),this.info.render.frame++,ft===!0&&Ct.beginShadows();const st=x.state.shadowsArray;Ht.render(st,w,Q),ft===!0&&Ct.endShadows(),this.info.autoReset===!0&&this.info.reset();const rt=E.opaque,K=E.transmissive;if(x.setupLights(),Q.isArrayCamera){const xt=Q.cameras;if(K.length>0)for(let Ut=0,It=xt.length;Ut<It;Ut++){const Pt=xt[Ut];Zo(rt,K,w,Pt)}ve&&Zt.render(w);for(let Ut=0,It=xt.length;Ut<It;Ut++){const Pt=xt[Ut];Sr(E,w,Pt,Pt.viewport)}}else K.length>0&&Zo(rt,K,w,Q),ve&&Zt.render(w),Sr(E,w,Q);G!==null&&(L.updateMultisampleRenderTarget(G),L.updateRenderTargetMipmap(G)),w.isScene===!0&&w.onAfterRender(R,w,Q),Ve.resetDefaultState(),U=-1,D=null,N.pop(),N.length>0?(x=N[N.length-1],ft===!0&&Ct.setGlobalState(R.clippingPlanes,x.state.camera)):x=null,P.pop(),P.length>0?E=P[P.length-1]:E=null};function ws(w,Q,st,rt){if(w.visible===!1)return;if(w.layers.test(Q.layers)){if(w.isGroup)st=w.renderOrder;else if(w.isLOD)w.autoUpdate===!0&&w.update(Q);else if(w.isLight)x.pushLight(w),w.castShadow&&x.pushShadow(w);else if(w.isSprite){if(!w.frustumCulled||q.intersectsSprite(w)){rt&&oe.setFromMatrixPosition(w.matrixWorld).applyMatrix4(Ft);const Ut=vt.update(w),It=w.material;It.visible&&E.push(w,Ut,It,st,oe.z,null)}}else if((w.isMesh||w.isLine||w.isPoints)&&(!w.frustumCulled||q.intersectsObject(w))){const Ut=vt.update(w),It=w.material;if(rt&&(w.boundingSphere!==void 0?(w.boundingSphere===null&&w.computeBoundingSphere(),oe.copy(w.boundingSphere.center)):(Ut.boundingSphere===null&&Ut.computeBoundingSphere(),oe.copy(Ut.boundingSphere.center)),oe.applyMatrix4(w.matrixWorld).applyMatrix4(Ft)),Array.isArray(It)){const Pt=Ut.groups;for(let $t=0,ae=Pt.length;$t<ae;$t++){const Kt=Pt[$t],Ee=It[Kt.materialIndex];Ee&&Ee.visible&&E.push(w,Ut,Ee,st,oe.z,Kt)}}else It.visible&&E.push(w,Ut,It,st,oe.z,null)}}const xt=w.children;for(let Ut=0,It=xt.length;Ut<It;Ut++)ws(xt[Ut],Q,st,rt)}function Sr(w,Q,st,rt){const K=w.opaque,xt=w.transmissive,Ut=w.transparent;x.setupLightsView(st),ft===!0&&Ct.setGlobalState(R.clippingPlanes,st),rt&&Qt.viewport(H.copy(rt)),K.length>0&&Ds(K,Q,st),xt.length>0&&Ds(xt,Q,st),Ut.length>0&&Ds(Ut,Q,st),Qt.buffers.depth.setTest(!0),Qt.buffers.depth.setMask(!0),Qt.buffers.color.setMask(!0),Qt.setPolygonOffset(!1)}function Zo(w,Q,st,rt){if((st.isScene===!0?st.overrideMaterial:null)!==null)return;x.state.transmissionRenderTarget[rt.id]===void 0&&(x.state.transmissionRenderTarget[rt.id]=new Vi(1,1,{generateMipmaps:!0,type:me.has("EXT_color_buffer_half_float")||me.has("EXT_color_buffer_float")?Oa:za,minFilter:cr,samples:4,stencilBuffer:c,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Oe.workingColorSpace}));const xt=x.state.transmissionRenderTarget[rt.id],Ut=rt.viewport||H;xt.setSize(Ut.z,Ut.w);const It=R.getRenderTarget();R.setRenderTarget(xt),R.getClearColor(mt),ct=R.getClearAlpha(),ct<1&&R.setClearColor(16777215,.5),R.clear(),ve&&Zt.render(st);const Pt=R.toneMapping;R.toneMapping=Cs;const $t=rt.viewport;if(rt.viewport!==void 0&&(rt.viewport=void 0),x.setupLightsView(rt),ft===!0&&Ct.setGlobalState(R.clippingPlanes,rt),Ds(w,st,rt),L.updateMultisampleRenderTarget(xt),L.updateRenderTargetMipmap(xt),me.has("WEBGL_multisampled_render_to_texture")===!1){let ae=!1;for(let Kt=0,Ee=Q.length;Kt<Ee;Kt++){const De=Q[Kt],Ze=De.object,Ye=De.geometry,ce=De.material,kt=De.group;if(ce.side===Da&&Ze.layers.test(rt.layers)){const dn=ce.side;ce.side=ii,ce.needsUpdate=!0,Di(Ze,st,rt,Ye,ce,kt),ce.side=dn,ce.needsUpdate=!0,ae=!0}}ae===!0&&(L.updateMultisampleRenderTarget(xt),L.updateRenderTargetMipmap(xt))}R.setRenderTarget(It),R.setClearColor(mt,ct),$t!==void 0&&(rt.viewport=$t),R.toneMapping=Pt}function Ds(w,Q,st){const rt=Q.isScene===!0?Q.overrideMaterial:null;for(let K=0,xt=w.length;K<xt;K++){const Ut=w[K],It=Ut.object,Pt=Ut.geometry,$t=rt===null?Ut.material:rt,ae=Ut.group;It.layers.test(st.layers)&&Di(It,Q,st,Pt,$t,ae)}}function Di(w,Q,st,rt,K,xt){w.onBeforeRender(R,Q,st,rt,K,xt),w.modelViewMatrix.multiplyMatrices(st.matrixWorldInverse,w.matrixWorld),w.normalMatrix.getNormalMatrix(w.modelViewMatrix),K.onBeforeRender(R,Q,st,rt,w,xt),K.transparent===!0&&K.side===Da&&K.forceSinglePass===!1?(K.side=ii,K.needsUpdate=!0,R.renderBufferDirect(st,Q,rt,K,w,xt),K.side=Rs,K.needsUpdate=!0,R.renderBufferDirect(st,Q,rt,K,w,xt),K.side=Da):R.renderBufferDirect(st,Q,rt,K,w,xt),w.onAfterRender(R,Q,st,rt,K,xt)}function sn(w,Q,st){Q.isScene!==!0&&(Q=Ge);const rt=Yt.get(w),K=x.state.lights,xt=x.state.shadowsArray,Ut=K.state.version,It=Xt.getParameters(w,K.state,xt,Q,st),Pt=Xt.getProgramCacheKey(It);let $t=rt.programs;rt.environment=w.isMeshStandardMaterial?Q.environment:null,rt.fog=Q.fog,rt.envMap=(w.isMeshStandardMaterial?at:C).get(w.envMap||rt.environment),rt.envMapRotation=rt.environment!==null&&w.envMap===null?Q.environmentRotation:w.envMapRotation,$t===void 0&&(w.addEventListener("dispose",ie),$t=new Map,rt.programs=$t);let ae=$t.get(Pt);if(ae!==void 0){if(rt.currentProgram===ae&&rt.lightsStateVersion===Ut)return na(w,It),ae}else It.uniforms=Xt.getUniforms(w),w.onBeforeCompile(It,R),ae=Xt.acquireProgram(It,Pt),$t.set(Pt,ae),rt.uniforms=It.uniforms;const Kt=rt.uniforms;return(!w.isShaderMaterial&&!w.isRawShaderMaterial||w.clipping===!0)&&(Kt.clippingPlanes=Ct.uniform),na(w,It),rt.needsLights=xf(w),rt.lightsStateVersion=Ut,rt.needsLights&&(Kt.ambientLightColor.value=K.state.ambient,Kt.lightProbe.value=K.state.probe,Kt.directionalLights.value=K.state.directional,Kt.directionalLightShadows.value=K.state.directionalShadow,Kt.spotLights.value=K.state.spot,Kt.spotLightShadows.value=K.state.spotShadow,Kt.rectAreaLights.value=K.state.rectArea,Kt.ltc_1.value=K.state.rectAreaLTC1,Kt.ltc_2.value=K.state.rectAreaLTC2,Kt.pointLights.value=K.state.point,Kt.pointLightShadows.value=K.state.pointShadow,Kt.hemisphereLights.value=K.state.hemi,Kt.directionalShadowMap.value=K.state.directionalShadowMap,Kt.directionalShadowMatrix.value=K.state.directionalShadowMatrix,Kt.spotShadowMap.value=K.state.spotShadowMap,Kt.spotLightMatrix.value=K.state.spotLightMatrix,Kt.spotLightMap.value=K.state.spotLightMap,Kt.pointShadowMap.value=K.state.pointShadowMap,Kt.pointShadowMatrix.value=K.state.pointShadowMatrix),rt.currentProgram=ae,rt.uniformsList=null,ae}function wn(w){if(w.uniformsList===null){const Q=w.currentProgram.getUniforms();w.uniformsList=af.seqWithValue(Q.seq,w.uniforms)}return w.uniformsList}function na(w,Q){const st=Yt.get(w);st.outputColorSpace=Q.outputColorSpace,st.batching=Q.batching,st.batchingColor=Q.batchingColor,st.instancing=Q.instancing,st.instancingColor=Q.instancingColor,st.instancingMorph=Q.instancingMorph,st.skinning=Q.skinning,st.morphTargets=Q.morphTargets,st.morphNormals=Q.morphNormals,st.morphColors=Q.morphColors,st.morphTargetsCount=Q.morphTargetsCount,st.numClippingPlanes=Q.numClippingPlanes,st.numIntersection=Q.numClipIntersection,st.vertexAlphas=Q.vertexAlphas,st.vertexTangents=Q.vertexTangents,st.toneMapping=Q.toneMapping}function Ko(w,Q,st,rt,K){Q.isScene!==!0&&(Q=Ge),L.resetTextureUnits();const xt=Q.fog,Ut=rt.isMeshStandardMaterial?Q.environment:null,It=G===null?R.outputColorSpace:G.isXRRenderTarget===!0?G.texture.colorSpace:Vo,Pt=(rt.isMeshStandardMaterial?at:C).get(rt.envMap||Ut),$t=rt.vertexColors===!0&&!!st.attributes.color&&st.attributes.color.itemSize===4,ae=!!st.attributes.tangent&&(!!rt.normalMap||rt.anisotropy>0),Kt=!!st.morphAttributes.position,Ee=!!st.morphAttributes.normal,De=!!st.morphAttributes.color;let Ze=Cs;rt.toneMapped&&(G===null||G.isXRRenderTarget===!0)&&(Ze=R.toneMapping);const Ye=st.morphAttributes.position||st.morphAttributes.normal||st.morphAttributes.color,ce=Ye!==void 0?Ye.length:0,kt=Yt.get(rt),dn=x.state.lights;if(ft===!0&&(Tt===!0||w!==D)){const yn=w===D&&rt.id===U;Ct.setState(rt,w,yn)}let Ne=!1;rt.version===kt.__version?(kt.needsLights&&kt.lightsStateVersion!==dn.state.version||kt.outputColorSpace!==It||K.isBatchedMesh&&kt.batching===!1||!K.isBatchedMesh&&kt.batching===!0||K.isBatchedMesh&&kt.batchingColor===!0&&K.colorTexture===null||K.isBatchedMesh&&kt.batchingColor===!1&&K.colorTexture!==null||K.isInstancedMesh&&kt.instancing===!1||!K.isInstancedMesh&&kt.instancing===!0||K.isSkinnedMesh&&kt.skinning===!1||!K.isSkinnedMesh&&kt.skinning===!0||K.isInstancedMesh&&kt.instancingColor===!0&&K.instanceColor===null||K.isInstancedMesh&&kt.instancingColor===!1&&K.instanceColor!==null||K.isInstancedMesh&&kt.instancingMorph===!0&&K.morphTexture===null||K.isInstancedMesh&&kt.instancingMorph===!1&&K.morphTexture!==null||kt.envMap!==Pt||rt.fog===!0&&kt.fog!==xt||kt.numClippingPlanes!==void 0&&(kt.numClippingPlanes!==Ct.numPlanes||kt.numIntersection!==Ct.numIntersection)||kt.vertexAlphas!==$t||kt.vertexTangents!==ae||kt.morphTargets!==Kt||kt.morphNormals!==Ee||kt.morphColors!==De||kt.toneMapping!==Ze||kt.morphTargetsCount!==ce)&&(Ne=!0):(Ne=!0,kt.__version=rt.version);let Gn=kt.currentProgram;Ne===!0&&(Gn=sn(rt,Q,K));let ia=!1,En=!1,Us=!1;const _e=Gn.getUniforms(),zn=kt.uniforms;if(Qt.useProgram(Gn.program)&&(ia=!0,En=!0,Us=!0),rt.id!==U&&(U=rt.id,En=!0),ia||D!==w){Qt.buffers.depth.getReversed()?(Mt.copy(w.projectionMatrix),ST(Mt),MT(Mt),_e.setValue(k,"projectionMatrix",Mt)):_e.setValue(k,"projectionMatrix",w.projectionMatrix),_e.setValue(k,"viewMatrix",w.matrixWorldInverse);const cn=_e.map.cameraPosition;cn!==void 0&&cn.setValue(k,Vt.setFromMatrixPosition(w.matrixWorld)),Se.logarithmicDepthBuffer&&_e.setValue(k,"logDepthBufFC",2/(Math.log(w.far+1)/Math.LN2)),(rt.isMeshPhongMaterial||rt.isMeshToonMaterial||rt.isMeshLambertMaterial||rt.isMeshBasicMaterial||rt.isMeshStandardMaterial||rt.isShaderMaterial)&&_e.setValue(k,"isOrthographic",w.isOrthographicCamera===!0),D!==w&&(D=w,En=!0,Us=!0)}if(K.isSkinnedMesh){_e.setOptional(k,K,"bindMatrix"),_e.setOptional(k,K,"bindMatrixInverse");const yn=K.skeleton;yn&&(yn.boneTexture===null&&yn.computeBoneTexture(),_e.setValue(k,"boneTexture",yn.boneTexture,L))}K.isBatchedMesh&&(_e.setOptional(k,K,"batchingTexture"),_e.setValue(k,"batchingTexture",K._matricesTexture,L),_e.setOptional(k,K,"batchingIdTexture"),_e.setValue(k,"batchingIdTexture",K._indirectTexture,L),_e.setOptional(k,K,"batchingColorTexture"),K._colorsTexture!==null&&_e.setValue(k,"batchingColorTexture",K._colorsTexture,L));const Vn=st.morphAttributes;if((Vn.position!==void 0||Vn.normal!==void 0||Vn.color!==void 0)&&qt.update(K,st,Gn),(En||kt.receiveShadow!==K.receiveShadow)&&(kt.receiveShadow=K.receiveShadow,_e.setValue(k,"receiveShadow",K.receiveShadow)),rt.isMeshGouraudMaterial&&rt.envMap!==null&&(zn.envMap.value=Pt,zn.flipEnvMap.value=Pt.isCubeTexture&&Pt.isRenderTargetTexture===!1?-1:1),rt.isMeshStandardMaterial&&rt.envMap===null&&Q.environment!==null&&(zn.envMapIntensity.value=Q.environmentIntensity),En&&(_e.setValue(k,"toneMappingExposure",R.toneMappingExposure),kt.needsLights&&yf(zn,Us),xt&&rt.fog===!0&&Dt.refreshFogUniforms(zn,xt),Dt.refreshMaterialUniforms(zn,rt,$,Z,x.state.transmissionRenderTarget[w.id]),af.upload(k,wn(kt),zn,L)),rt.isShaderMaterial&&rt.uniformsNeedUpdate===!0&&(af.upload(k,wn(kt),zn,L),rt.uniformsNeedUpdate=!1),rt.isSpriteMaterial&&_e.setValue(k,"center",K.center),_e.setValue(k,"modelViewMatrix",K.modelViewMatrix),_e.setValue(k,"normalMatrix",K.normalMatrix),_e.setValue(k,"modelMatrix",K.matrixWorld),rt.isShaderMaterial||rt.isRawShaderMaterial){const yn=rt.uniformsGroups;for(let cn=0,Mr=yn.length;cn<Mr;cn++){const Xi=yn[cn];Y.update(Xi,Gn),Y.bind(Xi,Gn)}}return Gn}function yf(w,Q){w.ambientLightColor.needsUpdate=Q,w.lightProbe.needsUpdate=Q,w.directionalLights.needsUpdate=Q,w.directionalLightShadows.needsUpdate=Q,w.pointLights.needsUpdate=Q,w.pointLightShadows.needsUpdate=Q,w.spotLights.needsUpdate=Q,w.spotLightShadows.needsUpdate=Q,w.rectAreaLights.needsUpdate=Q,w.hemisphereLights.needsUpdate=Q}function xf(w){return w.isMeshLambertMaterial||w.isMeshToonMaterial||w.isMeshPhongMaterial||w.isMeshStandardMaterial||w.isShadowMaterial||w.isShaderMaterial&&w.lights===!0}this.getActiveCubeFace=function(){return F},this.getActiveMipmapLevel=function(){return z},this.getRenderTarget=function(){return G},this.setRenderTargetTextures=function(w,Q,st){Yt.get(w.texture).__webglTexture=Q,Yt.get(w.depthTexture).__webglTexture=st;const rt=Yt.get(w);rt.__hasExternalTextures=!0,rt.__autoAllocateDepthBuffer=st===void 0,rt.__autoAllocateDepthBuffer||me.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),rt.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(w,Q){const st=Yt.get(w);st.__webglFramebuffer=Q,st.__useDefaultFramebuffer=Q===void 0},this.setRenderTarget=function(w,Q=0,st=0){G=w,F=Q,z=st;let rt=!0,K=null,xt=!1,Ut=!1;if(w){const Pt=Yt.get(w);if(Pt.__useDefaultFramebuffer!==void 0)Qt.bindFramebuffer(k.FRAMEBUFFER,null),rt=!1;else if(Pt.__webglFramebuffer===void 0)L.setupRenderTarget(w);else if(Pt.__hasExternalTextures)L.rebindTextures(w,Yt.get(w.texture).__webglTexture,Yt.get(w.depthTexture).__webglTexture);else if(w.depthBuffer){const Kt=w.depthTexture;if(Pt.__boundDepthTexture!==Kt){if(Kt!==null&&Yt.has(Kt)&&(w.width!==Kt.image.width||w.height!==Kt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");L.setupDepthRenderbuffer(w)}}const $t=w.texture;($t.isData3DTexture||$t.isDataArrayTexture||$t.isCompressedArrayTexture)&&(Ut=!0);const ae=Yt.get(w).__webglFramebuffer;w.isWebGLCubeRenderTarget?(Array.isArray(ae[Q])?K=ae[Q][st]:K=ae[Q],xt=!0):w.samples>0&&L.useMultisampledRTT(w)===!1?K=Yt.get(w).__webglMultisampledFramebuffer:Array.isArray(ae)?K=ae[st]:K=ae,H.copy(w.viewport),ut.copy(w.scissor),ot=w.scissorTest}else H.copy(O).multiplyScalar($).floor(),ut.copy(nt).multiplyScalar($).floor(),ot=St;if(Qt.bindFramebuffer(k.FRAMEBUFFER,K)&&rt&&Qt.drawBuffers(w,K),Qt.viewport(H),Qt.scissor(ut),Qt.setScissorTest(ot),xt){const Pt=Yt.get(w.texture);k.framebufferTexture2D(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_CUBE_MAP_POSITIVE_X+Q,Pt.__webglTexture,st)}else if(Ut){const Pt=Yt.get(w.texture),$t=Q||0;k.framebufferTextureLayer(k.FRAMEBUFFER,k.COLOR_ATTACHMENT0,Pt.__webglTexture,st||0,$t)}U=-1},this.readRenderTargetPixels=function(w,Q,st,rt,K,xt,Ut){if(!(w&&w.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let It=Yt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Ut!==void 0&&(It=It[Ut]),It){Qt.bindFramebuffer(k.FRAMEBUFFER,It);try{const Pt=w.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Se.textureTypeReadable(ae)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}Q>=0&&Q<=w.width-rt&&st>=0&&st<=w.height-K&&k.readPixels(Q,st,rt,K,le.convert($t),le.convert(ae),xt)}finally{const Pt=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(k.FRAMEBUFFER,Pt)}}},this.readRenderTargetPixelsAsync=async function(w,Q,st,rt,K,xt,Ut){if(!(w&&w.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let It=Yt.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Ut!==void 0&&(It=It[Ut]),It){const Pt=w.texture,$t=Pt.format,ae=Pt.type;if(!Se.textureFormatReadable($t))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Se.textureTypeReadable(ae))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(Q>=0&&Q<=w.width-rt&&st>=0&&st<=w.height-K){Qt.bindFramebuffer(k.FRAMEBUFFER,It);const Kt=k.createBuffer();k.bindBuffer(k.PIXEL_PACK_BUFFER,Kt),k.bufferData(k.PIXEL_PACK_BUFFER,xt.byteLength,k.STREAM_READ),k.readPixels(Q,st,rt,K,le.convert($t),le.convert(ae),0);const Ee=G!==null?Yt.get(G).__webglFramebuffer:null;Qt.bindFramebuffer(k.FRAMEBUFFER,Ee);const De=k.fenceSync(k.SYNC_GPU_COMMANDS_COMPLETE,0);return k.flush(),await xT(k,De,4),k.bindBuffer(k.PIXEL_PACK_BUFFER,Kt),k.getBufferSubData(k.PIXEL_PACK_BUFFER,0,xt),k.deleteBuffer(Kt),k.deleteSync(De),xt}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(w,Q=null,st=0){w.isTexture!==!0&&(vo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),Q=arguments[0]||null,w=arguments[1]);const rt=Math.pow(2,-st),K=Math.floor(w.image.width*rt),xt=Math.floor(w.image.height*rt),Ut=Q!==null?Q.x:0,It=Q!==null?Q.y:0;L.setTexture2D(w,0),k.copyTexSubImage2D(k.TEXTURE_2D,st,0,0,Ut,It,K,xt),Qt.unbindTexture()};const pc=k.createFramebuffer(),Ns=k.createFramebuffer();this.copyTextureToTexture=function(w,Q,st=null,rt=null,K=0,xt=null){w.isTexture!==!0&&(vo("WebGLRenderer: copyTextureToTexture function signature has changed."),rt=arguments[0]||null,w=arguments[1],Q=arguments[2],xt=arguments[3]||0,st=null),xt===null&&(K!==0?(vo("WebGLRenderer: copyTextureToTexture function signature has changed to support src and dst mipmap levels."),xt=K,K=0):xt=0);let Ut,It,Pt,$t,ae,Kt,Ee,De,Ze;const Ye=w.isCompressedTexture?w.mipmaps[xt]:w.image;if(st!==null)Ut=st.max.x-st.min.x,It=st.max.y-st.min.y,Pt=st.isBox3?st.max.z-st.min.z:1,$t=st.min.x,ae=st.min.y,Kt=st.isBox3?st.min.z:0;else{const Vn=Math.pow(2,-K);Ut=Math.floor(Ye.width*Vn),It=Math.floor(Ye.height*Vn),w.isDataArrayTexture?Pt=Ye.depth:w.isData3DTexture?Pt=Math.floor(Ye.depth*Vn):Pt=1,$t=0,ae=0,Kt=0}rt!==null?(Ee=rt.x,De=rt.y,Ze=rt.z):(Ee=0,De=0,Ze=0);const ce=le.convert(Q.format),kt=le.convert(Q.type);let dn;Q.isData3DTexture?(L.setTexture3D(Q,0),dn=k.TEXTURE_3D):Q.isDataArrayTexture||Q.isCompressedArrayTexture?(L.setTexture2DArray(Q,0),dn=k.TEXTURE_2D_ARRAY):(L.setTexture2D(Q,0),dn=k.TEXTURE_2D),k.pixelStorei(k.UNPACK_FLIP_Y_WEBGL,Q.flipY),k.pixelStorei(k.UNPACK_PREMULTIPLY_ALPHA_WEBGL,Q.premultiplyAlpha),k.pixelStorei(k.UNPACK_ALIGNMENT,Q.unpackAlignment);const Ne=k.getParameter(k.UNPACK_ROW_LENGTH),Gn=k.getParameter(k.UNPACK_IMAGE_HEIGHT),ia=k.getParameter(k.UNPACK_SKIP_PIXELS),En=k.getParameter(k.UNPACK_SKIP_ROWS),Us=k.getParameter(k.UNPACK_SKIP_IMAGES);k.pixelStorei(k.UNPACK_ROW_LENGTH,Ye.width),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Ye.height),k.pixelStorei(k.UNPACK_SKIP_PIXELS,$t),k.pixelStorei(k.UNPACK_SKIP_ROWS,ae),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Kt);const _e=w.isDataArrayTexture||w.isData3DTexture,zn=Q.isDataArrayTexture||Q.isData3DTexture;if(w.isDepthTexture){const Vn=Yt.get(w),yn=Yt.get(Q),cn=Yt.get(Vn.__renderTarget),Mr=Yt.get(yn.__renderTarget);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,cn.__webglFramebuffer),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,Mr.__webglFramebuffer);for(let Xi=0;Xi<Pt;Xi++)_e&&(k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Yt.get(w).__webglTexture,K,Kt+Xi),k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Yt.get(Q).__webglTexture,xt,Ze+Xi)),k.blitFramebuffer($t,ae,Ut,It,Ee,De,Ut,It,k.DEPTH_BUFFER_BIT,k.NEAREST);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else if(K!==0||w.isRenderTargetTexture||Yt.has(w)){const Vn=Yt.get(w),yn=Yt.get(Q);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,pc),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,Ns);for(let cn=0;cn<Pt;cn++)_e?k.framebufferTextureLayer(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,Vn.__webglTexture,K,Kt+cn):k.framebufferTexture2D(k.READ_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,Vn.__webglTexture,K),zn?k.framebufferTextureLayer(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,yn.__webglTexture,xt,Ze+cn):k.framebufferTexture2D(k.DRAW_FRAMEBUFFER,k.COLOR_ATTACHMENT0,k.TEXTURE_2D,yn.__webglTexture,xt),K!==0?k.blitFramebuffer($t,ae,Ut,It,Ee,De,Ut,It,k.COLOR_BUFFER_BIT,k.NEAREST):zn?k.copyTexSubImage3D(dn,xt,Ee,De,Ze+cn,$t,ae,Ut,It):k.copyTexSubImage2D(dn,xt,Ee,De,$t,ae,Ut,It);Qt.bindFramebuffer(k.READ_FRAMEBUFFER,null),Qt.bindFramebuffer(k.DRAW_FRAMEBUFFER,null)}else zn?w.isDataTexture||w.isData3DTexture?k.texSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,kt,Ye.data):Q.isCompressedArrayTexture?k.compressedTexSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,Ye.data):k.texSubImage3D(dn,xt,Ee,De,Ze,Ut,It,Pt,ce,kt,Ye):w.isDataTexture?k.texSubImage2D(k.TEXTURE_2D,xt,Ee,De,Ut,It,ce,kt,Ye.data):w.isCompressedTexture?k.compressedTexSubImage2D(k.TEXTURE_2D,xt,Ee,De,Ye.width,Ye.height,ce,Ye.data):k.texSubImage2D(k.TEXTURE_2D,xt,Ee,De,Ut,It,ce,kt,Ye);k.pixelStorei(k.UNPACK_ROW_LENGTH,Ne),k.pixelStorei(k.UNPACK_IMAGE_HEIGHT,Gn),k.pixelStorei(k.UNPACK_SKIP_PIXELS,ia),k.pixelStorei(k.UNPACK_SKIP_ROWS,En),k.pixelStorei(k.UNPACK_SKIP_IMAGES,Us),xt===0&&Q.generateMipmaps&&k.generateMipmap(dn),Qt.unbindTexture()},this.copyTextureToTexture3D=function(w,Q,st=null,rt=null,K=0){return w.isTexture!==!0&&(vo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),st=arguments[0]||null,rt=arguments[1]||null,w=arguments[2],Q=arguments[3],K=arguments[4]||0),vo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(w,Q,st,rt,K)},this.initRenderTarget=function(w){Yt.get(w).__webglFramebuffer===void 0&&L.setupRenderTarget(w)},this.initTexture=function(w){w.isCubeTexture?L.setTextureCube(w,0):w.isData3DTexture?L.setTexture3D(w,0):w.isDataArrayTexture||w.isCompressedArrayTexture?L.setTexture2DArray(w,0):L.setTexture2D(w,0),Qt.unbindTexture()},this.resetState=function(){F=0,z=0,G=null,Qt.reset(),Ve.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ua}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const n=this.getContext();n.drawingBufferColorspace=Oe._getDrawingBufferColorSpace(t),n.unpackColorSpace=Oe._getUnpackColorSpace()}}const pS={name:"CopyShader",uniforms:{tDiffuse:{value:null},opacity:{value:1}},vertexShader:`

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


		}`};class hc{constructor(){this.isPass=!0,this.enabled=!0,this.needsSwap=!0,this.clear=!1,this.renderToScreen=!1}setSize(){}render(){console.error("THREE.Pass: .render() must be implemented in derived pass.")}dispose(){}}const $w=new oS(-1,1,1,-1,0,1);class t3 extends ki{constructor(){super(),this.setAttribute("position",new Cn([-1,3,0,-1,-1,0,3,-1,0],3)),this.setAttribute("uv",new Cn([0,2,0,0,2,0],2))}}const e3=new t3;class mS{constructor(t){this._mesh=new Wn(e3,t)}dispose(){this._mesh.geometry.dispose()}render(t){t.render(this._mesh,$w)}get material(){return this._mesh.material}set material(t){this._mesh.material=t}}class n3 extends hc{constructor(t,n){super(),this.textureID=n!==void 0?n:"tDiffuse",t instanceof Yn?(this.uniforms=t.uniforms,this.material=t):t&&(this.uniforms=df.clone(t.uniforms),this.material=new Yn({name:t.name!==void 0?t.name:"unspecified",defines:Object.assign({},t.defines),uniforms:this.uniforms,vertexShader:t.vertexShader,fragmentShader:t.fragmentShader})),this.fsQuad=new mS(this.material)}render(t,n,s){this.uniforms[this.textureID]&&(this.uniforms[this.textureID].value=s.texture),this.fsQuad.material=this.material,this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(n),this.clear&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),this.fsQuad.render(t))}dispose(){this.material.dispose(),this.fsQuad.dispose()}}class Vy extends hc{constructor(t,n){super(),this.scene=t,this.camera=n,this.clear=!0,this.needsSwap=!1,this.inverse=!1}render(t,n,s){const l=t.getContext(),c=t.state;c.buffers.color.setMask(!1),c.buffers.depth.setMask(!1),c.buffers.color.setLocked(!0),c.buffers.depth.setLocked(!0);let f,d;this.inverse?(f=0,d=1):(f=1,d=0),c.buffers.stencil.setTest(!0),c.buffers.stencil.setOp(l.REPLACE,l.REPLACE,l.REPLACE),c.buffers.stencil.setFunc(l.ALWAYS,f,4294967295),c.buffers.stencil.setClear(d),c.buffers.stencil.setLocked(!0),t.setRenderTarget(s),this.clear&&t.clear(),t.render(this.scene,this.camera),t.setRenderTarget(n),this.clear&&t.clear(),t.render(this.scene,this.camera),c.buffers.color.setLocked(!1),c.buffers.depth.setLocked(!1),c.buffers.color.setMask(!0),c.buffers.depth.setMask(!0),c.buffers.stencil.setLocked(!1),c.buffers.stencil.setFunc(l.EQUAL,1,4294967295),c.buffers.stencil.setOp(l.KEEP,l.KEEP,l.KEEP),c.buffers.stencil.setLocked(!0)}}class i3 extends hc{constructor(){super(),this.needsSwap=!1}render(t){t.state.buffers.stencil.setLocked(!1),t.state.buffers.stencil.setTest(!1)}}class a3{constructor(t,n){if(this.renderer=t,this._pixelRatio=t.getPixelRatio(),n===void 0){const s=t.getSize(new Wt);this._width=s.width,this._height=s.height,n=new Vi(this._width*this._pixelRatio,this._height*this._pixelRatio,{type:Oa}),n.texture.name="EffectComposer.rt1"}else this._width=n.width,this._height=n.height;this.renderTarget1=n,this.renderTarget2=n.clone(),this.renderTarget2.texture.name="EffectComposer.rt2",this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2,this.renderToScreen=!0,this.passes=[],this.copyPass=new n3(pS),this.copyPass.material.blending=La,this.clock=new lS}swapBuffers(){const t=this.readBuffer;this.readBuffer=this.writeBuffer,this.writeBuffer=t}addPass(t){this.passes.push(t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}insertPass(t,n){this.passes.splice(n,0,t),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}removePass(t){const n=this.passes.indexOf(t);n!==-1&&this.passes.splice(n,1)}isLastEnabledPass(t){for(let n=t+1;n<this.passes.length;n++)if(this.passes[n].enabled)return!1;return!0}render(t){t===void 0&&(t=this.clock.getDelta());const n=this.renderer.getRenderTarget();let s=!1;for(let l=0,c=this.passes.length;l<c;l++){const f=this.passes[l];if(f.enabled!==!1){if(f.renderToScreen=this.renderToScreen&&this.isLastEnabledPass(l),f.render(this.renderer,this.writeBuffer,this.readBuffer,t,s),f.needsSwap){if(s){const d=this.renderer.getContext(),p=this.renderer.state.buffers.stencil;p.setFunc(d.NOTEQUAL,1,4294967295),this.copyPass.render(this.renderer,this.writeBuffer,this.readBuffer,t),p.setFunc(d.EQUAL,1,4294967295)}this.swapBuffers()}Vy!==void 0&&(f instanceof Vy?s=!0:f instanceof i3&&(s=!1))}}this.renderer.setRenderTarget(n)}reset(t){if(t===void 0){const n=this.renderer.getSize(new Wt);this._pixelRatio=this.renderer.getPixelRatio(),this._width=n.width,this._height=n.height,t=this.renderTarget1.clone(),t.setSize(this._width*this._pixelRatio,this._height*this._pixelRatio)}this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.renderTarget1=t,this.renderTarget2=t.clone(),this.writeBuffer=this.renderTarget1,this.readBuffer=this.renderTarget2}setSize(t,n){this._width=t,this._height=n;const s=this._width*this._pixelRatio,l=this._height*this._pixelRatio;this.renderTarget1.setSize(s,l),this.renderTarget2.setSize(s,l);for(let c=0;c<this.passes.length;c++)this.passes[c].setSize(s,l)}setPixelRatio(t){this._pixelRatio=t,this.setSize(this._width,this._height)}dispose(){this.renderTarget1.dispose(),this.renderTarget2.dispose(),this.copyPass.dispose()}}class s3 extends hc{constructor(t,n,s=null,l=null,c=null){super(),this.scene=t,this.camera=n,this.overrideMaterial=s,this.clearColor=l,this.clearAlpha=c,this.clear=!0,this.clearDepth=!1,this.needsSwap=!1,this._oldClearColor=new pe}render(t,n,s){const l=t.autoClear;t.autoClear=!1;let c,f;this.overrideMaterial!==null&&(f=this.scene.overrideMaterial,this.scene.overrideMaterial=this.overrideMaterial),this.clearColor!==null&&(t.getClearColor(this._oldClearColor),t.setClearColor(this.clearColor,t.getClearAlpha())),this.clearAlpha!==null&&(c=t.getClearAlpha(),t.setClearAlpha(this.clearAlpha)),this.clearDepth==!0&&t.clearDepth(),t.setRenderTarget(this.renderToScreen?null:s),this.clear===!0&&t.clear(t.autoClearColor,t.autoClearDepth,t.autoClearStencil),t.render(this.scene,this.camera),this.clearColor!==null&&t.setClearColor(this._oldClearColor),this.clearAlpha!==null&&t.setClearAlpha(c),this.overrideMaterial!==null&&(this.scene.overrideMaterial=f),t.autoClear=l}}const r3={uniforms:{tDiffuse:{value:null},luminosityThreshold:{value:1},smoothWidth:{value:1},defaultColor:{value:new pe(0)},defaultOpacity:{value:0}},vertexShader:`

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

		}`};class jo extends hc{constructor(t,n,s,l){super(),this.strength=n!==void 0?n:1,this.radius=s,this.threshold=l,this.resolution=t!==void 0?new Wt(t.x,t.y):new Wt(256,256),this.clearColor=new pe(0,0,0),this.renderTargetsHorizontal=[],this.renderTargetsVertical=[],this.nMips=5;let c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);this.renderTargetBright=new Vi(c,f,{type:Oa}),this.renderTargetBright.texture.name="UnrealBloomPass.bright",this.renderTargetBright.texture.generateMipmaps=!1;for(let _=0;_<this.nMips;_++){const y=new Vi(c,f,{type:Oa});y.texture.name="UnrealBloomPass.h"+_,y.texture.generateMipmaps=!1,this.renderTargetsHorizontal.push(y);const S=new Vi(c,f,{type:Oa});S.texture.name="UnrealBloomPass.v"+_,S.texture.generateMipmaps=!1,this.renderTargetsVertical.push(S),c=Math.round(c/2),f=Math.round(f/2)}const d=r3;this.highPassUniforms=df.clone(d.uniforms),this.highPassUniforms.luminosityThreshold.value=l,this.highPassUniforms.smoothWidth.value=.01,this.materialHighPassFilter=new Yn({uniforms:this.highPassUniforms,vertexShader:d.vertexShader,fragmentShader:d.fragmentShader}),this.separableBlurMaterials=[];const p=[3,5,7,9,11];c=Math.round(this.resolution.x/2),f=Math.round(this.resolution.y/2);for(let _=0;_<this.nMips;_++)this.separableBlurMaterials.push(this.getSeperableBlurMaterial(p[_])),this.separableBlurMaterials[_].uniforms.invSize.value=new Wt(1/c,1/f),c=Math.round(c/2),f=Math.round(f/2);this.compositeMaterial=this.getCompositeMaterial(this.nMips),this.compositeMaterial.uniforms.blurTexture1.value=this.renderTargetsVertical[0].texture,this.compositeMaterial.uniforms.blurTexture2.value=this.renderTargetsVertical[1].texture,this.compositeMaterial.uniforms.blurTexture3.value=this.renderTargetsVertical[2].texture,this.compositeMaterial.uniforms.blurTexture4.value=this.renderTargetsVertical[3].texture,this.compositeMaterial.uniforms.blurTexture5.value=this.renderTargetsVertical[4].texture,this.compositeMaterial.uniforms.bloomStrength.value=n,this.compositeMaterial.uniforms.bloomRadius.value=.1;const m=[1,.8,.6,.4,.2];this.compositeMaterial.uniforms.bloomFactors.value=m,this.bloomTintColors=[new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1),new W(1,1,1)],this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors;const g=pS;this.copyUniforms=df.clone(g.uniforms),this.blendMaterial=new Yn({uniforms:this.copyUniforms,vertexShader:g.vertexShader,fragmentShader:g.fragmentShader,blending:Cp,depthTest:!1,depthWrite:!1,transparent:!0}),this.enabled=!0,this.needsSwap=!1,this._oldClearColor=new pe,this.oldClearAlpha=1,this.basic=new xr,this.fsQuad=new mS(null)}dispose(){for(let t=0;t<this.renderTargetsHorizontal.length;t++)this.renderTargetsHorizontal[t].dispose();for(let t=0;t<this.renderTargetsVertical.length;t++)this.renderTargetsVertical[t].dispose();this.renderTargetBright.dispose();for(let t=0;t<this.separableBlurMaterials.length;t++)this.separableBlurMaterials[t].dispose();this.compositeMaterial.dispose(),this.blendMaterial.dispose(),this.basic.dispose(),this.fsQuad.dispose()}setSize(t,n){let s=Math.round(t/2),l=Math.round(n/2);this.renderTargetBright.setSize(s,l);for(let c=0;c<this.nMips;c++)this.renderTargetsHorizontal[c].setSize(s,l),this.renderTargetsVertical[c].setSize(s,l),this.separableBlurMaterials[c].uniforms.invSize.value=new Wt(1/s,1/l),s=Math.round(s/2),l=Math.round(l/2)}render(t,n,s,l,c){t.getClearColor(this._oldClearColor),this.oldClearAlpha=t.getClearAlpha();const f=t.autoClear;t.autoClear=!1,t.setClearColor(this.clearColor,0),c&&t.state.buffers.stencil.setTest(!1),this.renderToScreen&&(this.fsQuad.material=this.basic,this.basic.map=s.texture,t.setRenderTarget(null),t.clear(),this.fsQuad.render(t)),this.highPassUniforms.tDiffuse.value=s.texture,this.highPassUniforms.luminosityThreshold.value=this.threshold,this.fsQuad.material=this.materialHighPassFilter,t.setRenderTarget(this.renderTargetBright),t.clear(),this.fsQuad.render(t);let d=this.renderTargetBright;for(let p=0;p<this.nMips;p++)this.fsQuad.material=this.separableBlurMaterials[p],this.separableBlurMaterials[p].uniforms.colorTexture.value=d.texture,this.separableBlurMaterials[p].uniforms.direction.value=jo.BlurDirectionX,t.setRenderTarget(this.renderTargetsHorizontal[p]),t.clear(),this.fsQuad.render(t),this.separableBlurMaterials[p].uniforms.colorTexture.value=this.renderTargetsHorizontal[p].texture,this.separableBlurMaterials[p].uniforms.direction.value=jo.BlurDirectionY,t.setRenderTarget(this.renderTargetsVertical[p]),t.clear(),this.fsQuad.render(t),d=this.renderTargetsVertical[p];this.fsQuad.material=this.compositeMaterial,this.compositeMaterial.uniforms.bloomStrength.value=this.strength,this.compositeMaterial.uniforms.bloomRadius.value=this.radius,this.compositeMaterial.uniforms.bloomTintColors.value=this.bloomTintColors,t.setRenderTarget(this.renderTargetsHorizontal[0]),t.clear(),this.fsQuad.render(t),this.fsQuad.material=this.blendMaterial,this.copyUniforms.tDiffuse.value=this.renderTargetsHorizontal[0].texture,c&&t.state.buffers.stencil.setTest(!0),this.renderToScreen?(t.setRenderTarget(null),this.fsQuad.render(t)):(t.setRenderTarget(s),this.fsQuad.render(t)),t.setClearColor(this._oldClearColor,this.oldClearAlpha),t.autoClear=f}getSeperableBlurMaterial(t){const n=[];for(let s=0;s<t;s++)n.push(.39894*Math.exp(-.5*s*s/(t*t))/t);return new Yn({defines:{KERNEL_RADIUS:t},uniforms:{colorTexture:{value:null},invSize:{value:new Wt(.5,.5)},direction:{value:new Wt(.5,.5)},gaussianCoefficients:{value:n}},vertexShader:`varying vec2 vUv;
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
				}`})}}jo.BlurDirectionX=new Wt(1,0);jo.BlurDirectionY=new Wt(0,1);const nn={cyan:new pe("#29D3FF"),white:new pe("#EAF2FF"),violet:new pe("#8B7CFF"),amber:new pe("#FFB84D"),red:new pe("#FF5D73"),muted:new pe("#8EA0B8"),recovery:new pe("#2DD4A8")};function gS({mode:a,health:t,activityLevel:n,confidence:s,servers:l,visualEvents:c,activeServerId:f="",nextServerId:d="",approvalServerIds:p=[]}){const m=se.useRef(null),g=se.useRef({mode:a,health:t,activityLevel:n,confidence:s,servers:l,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}),_=se.useMemo(()=>rf.map(y=>({id:y,label:Hi(y)})),[]);return se.useEffect(()=>{g.current={mode:a,health:t,activityLevel:n,confidence:s,servers:l,events:c,activeServerId:f,nextServerIds:new Set(d?[d]:[]),approvalServerIds:new Set(p)}},[a,t,n,s,l,c,f,d,p]),se.useEffect(()=>{const y=m.current;if(!y)return;const S=window.matchMedia("(prefers-reduced-motion: reduce)").matches,b=new XT,T=new _i(44,1,.1,100);T.position.set(0,0,7.2);const E=new Jw({antialias:!0,alpha:!0,powerPreference:"high-performance"});E.setPixelRatio(Math.min(window.devicePixelRatio,2)),E.outputColorSpace=vi,y.appendChild(E.domElement);const x=new a3(E);x.addPass(new s3(b,T));const P=new jo(new Wt(1,1),.38,.45,.86);x.addPass(P);const N=new _o;b.add(N);const R=new Yn({transparent:!0,depthWrite:!1,uniforms:{uTime:{value:0},uActivity:{value:.2},uColor:{value:nn.cyan.clone()},uGlow:{value:.55}},vertexShader:`
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
      `}),V=new Wn(new vf(1.24,96,64),R);N.add(V);const F=new Wn(new hf(1.72,.018,12,160),new xr({color:nn.amber,transparent:!0,opacity:0}));F.rotation.x=Math.PI/2.15,N.add(F);const z=new Wn(new hf(1.35,.015,12,160),new xr({color:nn.recovery,transparent:!0,opacity:0}));z.rotation.x=Math.PI/2,N.add(z);const G=new Map;rf.forEach((ct,I)=>{const Z=o3(ct,I);G.set(ct,Z),N.add(Z.group)}),b.add(new pA(9347256,.55));const U=new hA(15397631,1.3);U.position.set(0,0,4.8),b.add(U);const D=new lS,H=()=>{const ct=Math.max(1,y.clientWidth),I=Math.max(1,y.clientHeight);T.aspect=ct/I,T.updateProjectionMatrix(),E.setSize(ct,I,!1),x.setSize(ct,I),P.resolution.set(ct,I)},ut=new ResizeObserver(H);ut.observe(y),H();let ot=0;const mt=()=>{ot=requestAnimationFrame(mt);const ct=Math.min(D.getDelta(),.05),I=performance.now(),Z=g.current,$=Math.min(Math.max(Number(Z.activityLevel||1),0),8)/8,Et=S?0:.08+$*.42;N.userData.rotationSpeed=ls.damp(Number(N.userData.rotationSpeed||0),Et,2.6,ct),N.rotation.y+=Number(N.userData.rotationSpeed)*ct,V.rotation.x+=Number(N.userData.rotationSpeed)*ct*.42,R.uniforms.uTime.value+=ct,R.uniforms.uActivity.value=ls.damp(R.uniforms.uActivity.value,.25+$,3.2,ct),R.uniforms.uGlow.value=ls.damp(R.uniforms.uGlow.value,Z.health==="DEGRADED"?.9:Z.health==="OFFLINE"?.35:.62,2.5,ct),R.uniforms.uColor.value.lerp(Z.health==="OFFLINE"?nn.red:Z.health==="DEGRADED"?nn.amber:nn.cyan,1-Math.exp(-ct*2.8));const At=S?1:1+Math.sin(I*.0016)*(.018+$*.018);V.scale.setScalar(At);const O=Z.events.filter(q=>q.expiresAt>Date.now());let nt=0,St=0;for(const q of G.values()){l3(q,Z,O,I),q.color.lerp(q.targetColor,1-Math.exp(-ct*5.5)),q.opacity=ls.damp(q.opacity,q.targetOpacity,5.5,ct);for(const ft of[...q.segments,...q.filaments]){const Tt=ft.material;Tt.color.copy(q.color);const Mt=ft.userData.mid.clone();Mt.applyMatrix4(N.matrixWorld);const Ft=Mt.z>=0?1:.34;Tt.opacity=q.opacity*Ft*Number(ft.userData.opacityScale||1),ft.visible=!!ft.userData.enabled}q.marker.material.color.copy(q.color),q.marker.material.opacity=Math.min(1,q.opacity+.25),q.group.scale.setScalar(ls.damp(q.group.scale.x,Number(q.group.userData.targetScale||1),8,ct)),q.group.userData.containment&&(nt=Math.max(nt,Number(q.group.userData.effectStrength||0))),q.group.userData.recovery&&(St=Math.max(St,Number(q.group.userData.effectStrength||0)))}F.material.opacity=ls.damp(F.material.opacity,Math.min(.58,nt),6,ct),z.material.opacity=ls.damp(z.material.opacity,Math.min(.72,St),5,ct),z.scale.setScalar(1+St*1.25),S||(z.rotation.z+=ct*1.2),T.position.z=ls.damp(T.position.z,Z.mode==="EXECUTING"?6.6:7.25,1.8,ct),x.render()};return mt(),()=>{cancelAnimationFrame(ot),ut.disconnect(),x.dispose(),c3(b),E.dispose(),E.domElement.remove()}},[]),v.jsxs("div",{className:"core-sphere","data-testid":"core-sphere","data-mode":a,"data-health":t,children:[v.jsx("div",{ref:m,className:"core-canvas",role:"img","aria-label":`AEGIS core sphere. Mode ${a}, health ${t}.`}),v.jsx("div",{className:"core-legend","aria-label":"Core server arcs",children:_.map(y=>v.jsxs("span",{className:"core-legend__item","data-server":y.id,children:[v.jsx("i",{"aria-hidden":"true"}),y.label]},y.id))}),v.jsxs("div",{className:"muted mono core-caption",children:["Mode: ",a," / Health: ",t," / Confidence: ",s]})]})}function o3(a,t){const n=new _o;n.rotation.set(t*.37,t*.71,t*.23);const s=2.05,l=t/rf.length*Math.PI,c=[ql(s,l+.1,l+Math.PI*.68,.018),ql(s,l+Math.PI*.78,l+Math.PI*1.34,.018),ql(s,l+Math.PI*1.46,l+Math.PI*2-.1,.018)],f=ql(s+.16,l+.25,l+Math.PI*1.75,.006),d=ql(s-.17,l+Math.PI*.08,l+Math.PI*1.92,.005);f.rotation.x=.18,d.rotation.y=-.14;const p=new Wn(new vf(.055,20,20),new xr({color:nn.cyan,transparent:!0,opacity:.8}));p.position.copy(pm(s+.07,l+t*.24));for(const m of[...c,f,d,p])n.add(m);return{serverId:a,group:n,segments:c,filaments:[f,d],marker:p,color:nn.cyan.clone(),targetColor:nn.cyan.clone(),opacity:.42,targetOpacity:.42}}function ql(a,t,n,s){const l=[];for(let g=0;g<=64;g+=1){const _=t+(n-t)*g/64;l.push(pm(a,_))}const f=new aS(l),d=new Pm(f,72,s,8,!1),p=new xr({color:nn.cyan,transparent:!0,opacity:.4,depthWrite:!1}),m=new Wn(d,p);return m.userData.mid=pm(a,(t+n)/2),m.userData.enabled=!0,m.userData.opacityScale=s<.01?.42:1,m}function pm(a,t){return new W(Math.cos(t)*a,Math.sin(t)*a,Math.sin(t*1.7)*.18)}function l3(a,t,n,s){const l=t.servers.find(p=>p.server_id===a.serverId),c=String((l==null?void 0:l.status)||"UNCONFIGURED").toUpperCase(),f=n.find(p=>p.serverId===a.serverId),d=f?Math.max(0,Math.min(1,(f.expiresAt-Date.now())/Math.max(1,f.expiresAt-f.createdAt))):0;a.group.userData.targetScale=1,a.group.userData.effectStrength=d,a.group.userData.containment=!1,a.group.userData.recovery=!1,a.targetColor.copy(nn.cyan),a.targetOpacity=.5,a.segments.forEach(p=>{p.userData.enabled=!0}),(c==="UNCONFIGURED"||c==="DISABLED")&&(a.targetColor.copy(nn.muted),a.targetOpacity=.22),c==="OFFLINE"&&(a.targetColor.copy(nn.muted),a.targetOpacity=.26,a.segments[1].userData.enabled=!1),c==="DEGRADED"&&(a.targetColor.copy(nn.amber),a.targetOpacity=.58+Math.sin(s*.018)*.08),t.nextServerIds.has(a.serverId)&&(a.targetColor.copy(nn.violet),a.targetOpacity=.72),t.approvalServerIds.has(a.serverId)&&(a.targetColor.copy(nn.amber),a.targetOpacity=.86,a.group.userData.containment=!0),t.activeServerId===a.serverId&&(a.targetColor.copy(nn.white).lerp(nn.cyan,.28),a.targetOpacity=.94,a.group.userData.targetScale=1.02),f&&(f.effect==="fracture"?(a.targetColor.copy(nn.red),a.targetOpacity=.96,a.group.userData.targetScale=1+d*.04):f.effect==="containment"?(a.targetColor.copy(nn.amber),a.group.userData.containment=!0,a.targetOpacity=.96):f.effect==="recovery"?(a.targetColor.copy(nn.recovery),a.group.userData.recovery=!0,a.targetOpacity=.98):f.effect==="complete"||f.effect==="pulse"?(a.targetColor.copy(nn.white).lerp(nn.cyan,.2),a.targetOpacity=.86+d*.14,a.group.userData.targetScale=1+d*.035):f.effect==="disconnect"&&(a.segments[1].userData.enabled=!1,a.targetColor.copy(nn.red),a.targetOpacity=.64))}function c3(a){a.traverse(t=>{const n=t;n.geometry&&n.geometry.dispose();const s=n.material;Array.isArray(s)?s.forEach(l=>l.dispose()):s&&s.dispose()})}function u3({overview:a,recentEvents:t}){var S,b,T,E;const n=a.core.data,s=a.servers.data.items||[],l=a.current_task.data,c=a.usage.data,f=((S=a.user_situation)==null?void 0:S.data)||a.user_state.data||{},d=a.commitments.data.items||[],p=((b=a.errors)==null?void 0:b.data.items)||[],m=((T=a.connection)==null?void 0:T.data)||{},g=JE(s),_=Em(a),y=s.filter(x=>Mm(x));return v.jsxs(v.Fragment,{children:[v.jsxs("section",{className:"command-priority",children:[v.jsxs("section",{className:"panel command-operation",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"Current Operation"}),v.jsx(zo,{status:String(n.mode||"IDLE")})]}),v.jsx("h3",{children:l.title||"No active task"}),v.jsx("p",{className:"muted",children:l.current_action||l.next_action||l.blocked_reason||"AEGIS is waiting for a meaningful signal or user request."}),v.jsxs("div",{className:"stat-grid",children:[v.jsx(Zu,{icon:v.jsx(mx,{size:18}),label:"Activity",value:String(n.activity_level??0)}),v.jsx(Zu,{icon:v.jsx(EE,{size:18}),label:"Confidence",value:String(n.confidence||"Not reported")}),v.jsx(Zu,{icon:v.jsx(NE,{size:18}),label:"Approvals",value:String(n.pending_approval_count??0)}),v.jsx(Zu,{icon:v.jsx(wE,{size:18}),label:"Freshness",value:a.freshness.stale?"STALE":"LIVE"})]}),v.jsxs("div",{className:"mission-strip","aria-label":"Mission context",children:[v.jsxs("span",{children:["Next: ",v.jsx("strong",{children:l.next_action||"Not reported"})]}),v.jsxs("span",{children:["User: ",v.jsx("strong",{children:String(f.summary||f.availability||"Not reported")})]}),v.jsxs("span",{children:["Connection: ",v.jsx("strong",{children:String(m.quality||m.status||"Not reported")})]}),v.jsxs("span",{children:["Commitments: ",v.jsx("strong",{children:d.length})]})]})]}),v.jsx(pb,{items:a.attention.data.items||[]})]}),v.jsxs("div",{className:"grid grid--command",children:[v.jsx("section",{className:"panel core-card",children:v.jsx(gS,{mode:String(n.mode||"IDLE"),health:String(n.health||"ONLINE"),activityLevel:Number(n.activity_level||1),confidence:String(n.confidence||"medium"),servers:s,visualEvents:[],activeServerId:String(l.capability_id||"").split(".",1)[0],nextServerId:"",approvalServerIds:(a.approvals.data.pending||[]).map(x=>String(x.capability_id||"").split(".",1)[0])})}),v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"AI State"}),v.jsx(or,{...Ku(a.core)})]}),v.jsxs("div",{className:"grid",children:[v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Active goal"}),v.jsx("b",{style:{fontSize:16},children:String(n.active_goal||"No active goal")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Attention level"}),v.jsx("b",{style:{fontSize:16},children:String(n.attention_level||"normal")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"LLM usage"}),v.jsx("b",{style:{fontSize:16},children:String(c.summary||c.total_tokens||"Audit-backed")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"LLM budget"}),v.jsx("b",{style:{fontSize:16},children:String(c.budget_state||c.autonomous_suppression||c.cost_state||"Not reported")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Open issues"}),v.jsx("b",{style:{fontSize:16},children:String(p.length||((E=a.errors)==null?void 0:E.data.count)||0)})]})]})]})]}),v.jsxs("div",{className:"grid grid--three",style:{marginTop:16},children:[v.jsxs("section",{className:"panel server-summary-card",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"Systems"}),v.jsx(or,{...Ku(a.servers)})]}),v.jsxs("div",{className:"server-summary-line",children:[v.jsx(FE,{size:18}),v.jsxs("strong",{children:[g.ok," normal"]}),v.jsxs("span",{children:[g.attention.length," need attention"]})]}),v.jsx("div",{className:"grid",children:y.length?y.slice(0,4).map(x=>v.jsxs("div",{className:"list-row",children:[v.jsxs("div",{children:[v.jsx("strong",{children:Hi(x.server_id)}),v.jsx("div",{className:"muted",children:x.status_detail||x.degraded_reason||x.recovery_hint||"Review server status."})]}),v.jsx(zo,{status:x.status,detail:x.recovery_hint})]},x.server_id)):v.jsx("p",{className:"muted",children:"All configured systems are operating normally."})})]}),v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"Recent Events"}),v.jsx(or,{...Ku(a.notifications)})]}),v.jsxs("div",{className:"grid",children:[t.length?t.slice(0,5).map(x=>v.jsx("div",{className:"list-row",children:v.jsxs("div",{children:[v.jsx("strong",{children:x.type}),v.jsx("div",{className:"muted",children:x.message||x.source_type})]})},`${x.type}-${x.source_updated_at}-${x.message}`)):(a.notifications.data.recent||[]).slice(0,5).map((x,P)=>v.jsx("div",{className:"list-row",children:v.jsxs("div",{children:[v.jsx("strong",{children:String(x.title||"Notification")}),v.jsx("div",{className:"muted",children:String(x.message||x.severity||"")})]})},String(x.notification_id||x.id||P))),t.length===0&&(a.notifications.data.recent||[]).length===0?v.jsx("p",{className:"muted",children:"No recent events reported."}):null]})]}),v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"Memory & Mind"}),v.jsx(or,{...Ku(a.mind_summary)})]}),v.jsx("div",{className:"grid",children:Object.entries(_).map(([x,P])=>v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:x}),v.jsx("b",{style:{fontSize:15},children:P})]},x))})]})]})]})}function Zu({icon:a,label:t,value:n}){return v.jsxs("div",{className:"stat",children:[v.jsxs("span",{className:"muted",children:[a," ",t]}),v.jsx("b",{children:n})]})}function Ku(a){return{generatedAt:a.generated_at,sourceUpdatedAt:a.source_updated_at,stale:a.stale}}function f3({overview:a}){var T;const[t,n]=se.useState(a),[s,l]=se.useState([]),[c,f]=se.useState([]);se.useEffect(()=>n(a),[a]);const d=se.useCallback(E=>{if("schema_version"in E){n(E);return}l(P=>[E,...P].slice(0,10));const x=Cx(E);f(P=>[x,...P.filter(N=>N.expiresAt>Date.now())].slice(0,12))},[]);Tx(d,!0,"display");const p=t.core.data,m=t.servers.data.items||[],g=t.current_task.data,_=Rx(t),y=String(g.capability_id||"").split(".",1)[0],S=wx(t),b=$E(t,s,c);return v.jsxs("main",{className:"display-shell","data-phase":S,"data-testid":"display-shell","data-priority":((T=b.takeover)==null?void 0:T.priority)||"P3","data-offline":b.offline,"data-stale":b.stale,"data-privacy":b.privacyMode,children:[v.jsxs("div",{className:"display-state-ribbon","aria-label":"Display state",children:[v.jsx("span",{children:b.offline?"OFFLINE SNAPSHOT":b.stale?"STALE SNAPSHOT":"LIVE DISPLAY"}),b.privacyMode?v.jsx("span",{children:"PRIVACY MODE"}):null]}),b.takeover?v.jsxs("section",{className:"display-takeover","data-priority":b.takeover.priority,"aria-label":"Display takeover",children:[v.jsxs("span",{className:"display-kicker",children:[b.takeover.priority," / ",b.takeover.severity]}),v.jsx("strong",{children:er(b.takeover.title,b.privacyMode)}),v.jsx("p",{children:b.privacyMode?"Private information hidden.":b.takeover.message})]}):null,b.overlays.length?v.jsx("aside",{className:"display-overlay-stack","aria-label":"Important overlays",children:b.overlays.map(E=>v.jsxs("article",{className:"display-overlay","data-priority":E.priority,"data-severity":E.severity,children:[v.jsx("span",{children:E.priority}),v.jsx("strong",{children:E.title}),v.jsx("p",{children:E.message})]},E.id))}):null,v.jsxs("header",{className:"display-top",children:[v.jsxs("section",{className:"display-card display-operation","aria-label":"Current Operation",children:[v.jsx("span",{className:"display-kicker",children:"Current Operation"}),v.jsx("h1",{children:er(g.title||"No active task",b.privacyMode)}),v.jsx("p",{children:er(g.current_action||g.next_action||g.blocked_reason||"Waiting for a meaningful signal.",b.privacyMode)}),v.jsxs("div",{className:"display-meta",children:[v.jsx(zo,{status:String(p.mode||"IDLE")}),v.jsx("span",{children:S})]})]}),_.length?v.jsxs("section",{className:"display-card display-attention","aria-label":"Attention",children:[v.jsx("span",{className:"display-kicker",children:"Attention"}),_.slice(0,4).map(E=>v.jsxs("article",{className:"display-attention__item","data-severity":E.severity,children:[v.jsx("strong",{children:er(E.title,b.privacyMode)}),v.jsx("p",{children:er(E.message||E.recovery_hint||"Review this signal.",b.privacyMode)})]},E.id))]}):null]}),v.jsx("section",{className:"display-core-stage","aria-label":"AEGIS core",children:v.jsx(gS,{mode:String(p.mode||"IDLE"),health:String(p.health||"ONLINE"),activityLevel:Number(p.activity_level||1),confidence:String(p.confidence||"medium"),servers:m,visualEvents:c,activeServerId:y,nextServerId:h3(g.steps),approvalServerIds:(t.approvals.data.pending||[]).map(E=>String(E.capability_id||"").split(".",1)[0])})}),v.jsxs("section",{className:"display-bottom",children:[v.jsxs("div",{className:"display-card display-phase",children:[v.jsx("span",{className:"display-kicker",children:"Mission Phase"}),v.jsx("strong",{children:S}),v.jsx("p",{children:er(String(p.active_goal||g.title||"Standing by."),b.privacyMode)})]}),v.jsxs("div",{className:"display-card display-events","aria-label":"Recent Events",children:[v.jsx("span",{className:"display-kicker",children:"Recent Events"}),b.dock.length||b.ambient.length?[...b.dock,...b.ambient].slice(0,6).map(E=>v.jsxs("div",{className:"event-row","data-severity":E.severity||"info","data-priority":E.priority,children:[v.jsx("span",{children:E.priority}),v.jsx("strong",{children:er(E.message||E.title,b.privacyMode)})]},E.id)):v.jsxs("div",{className:"event-row","data-severity":b.offline||b.stale?"warning":"normal",children:[v.jsx("span",{children:b.offline?"offline":b.stale?"stale":"stream"}),v.jsx("strong",{children:b.offline?"Showing last known snapshot":b.stale?"Waiting for fresh events":"Waiting for live events"})]})]})]}),v.jsx(d3,{servers:m,activeServerId:y})]})}function d3({servers:a,activeServerId:t}){const n=se.useMemo(()=>[...a].sort((s,l)=>Hi(s.server_id).localeCompare(Hi(l.server_id))),[a]);return v.jsx("footer",{className:"server-rail","aria-label":"Server rail",children:n.map(s=>{const l=Mm(s,t);return v.jsxs("article",{className:"server-rail__item","data-status":Ap(s.status),"data-expanded":l,children:[v.jsx("span",{className:"server-dot","aria-hidden":"true"}),v.jsx("strong",{children:Hi(s.server_id)}),l?v.jsx("span",{className:"server-rail__detail",children:s.status_detail||s.degraded_reason||s.recovery_hint||Ap(s.status)}):null]},s.server_id)})})}function h3(a){const t=(a||[]).find(s=>String(s.status||"").toLowerCase()==="pending"||String(s.status||"").toLowerCase()==="ready");return String((t==null?void 0:t.capability_id)||"").split(".",1)[0]||""}function er(a,t){return t?"Private information hidden":a}function p3({overview:a}){var c,f;const t=Em(a),n=a.mind_summary.data.memory,s=a.user_state.data,l=a.commitments.data.items||[];return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsxs("div",{children:[v.jsx("h2",{children:"Mind & Memory"}),v.jsx("div",{className:"muted",children:"Operational summary, not raw internal state."})]})}),v.jsx("div",{className:"stat-grid",children:Object.entries(t).map(([d,p])=>v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:d}),v.jsx("b",{style:{fontSize:16},children:p})]},d))})]}),v.jsxs("div",{className:"grid grid--three",children:[v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Memory Stores"})}),v.jsx("div",{className:"metric-list",children:["advanced","episodic","semantic","procedural","skill","lesson","workflow","experiential"].map(d=>v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:d}),v.jsx("strong",{children:m3((n||{})[d])})]},d))})]}),v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"User Situation"})}),v.jsxs("div",{className:"metric-list",children:[v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Status"}),v.jsx("strong",{children:String(s.summary||s.status||"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Available"}),v.jsx("strong",{children:String(s.available??"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Updated"}),v.jsx("strong",{children:a.user_state.stale?"STALE":"LIVE"})]})]})]}),v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Commitments"})}),v.jsxs("div",{className:"metric-list",children:[v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Open commitments"}),v.jsx("strong",{children:l.length})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Next commitment"}),v.jsx("strong",{children:String(((c=l[0])==null?void 0:c.title)||((f=l[0])==null?void 0:f.summary)||"Not reported")})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Summary"}),v.jsx("strong",{children:a.commitments.data.summary||"Not reported"})]})]})]})]}),v.jsxs("details",{className:"developer-drawer",children:[v.jsx("summary",{children:"Developer raw state"}),v.jsx("pre",{className:"mono muted",children:JSON.stringify({mind_summary:a.mind_summary.data,user_state:a.user_state.data,commitments:a.commitments.data},null,2)})]})]})}function m3(a){if(a==null)return"Not reported";if(typeof a=="number"||typeof a!="object")return String(a);const t=a,n=t.total||t.total_entries||t.total_episodes||t.entities||t.facts||t.active;if(n!==void 0)return String(n);const s=Object.keys(t);return s.length?`${s.length} fields`:"Empty"}function g3({overview:a}){const t=nb(a),[n,s]=se.useState({}),[l,c]=se.useState(!0),[f,d]=se.useState(""),p=se.useMemo(()=>v3(n),[n]);se.useEffect(()=>{let y=!1;return c(!0),Uh().then(S=>{y||s(S)}).catch(S=>{y||d(S instanceof Error?S.message:"Settings unavailable")}).finally(()=>{y||c(!1)}),()=>{y=!0}},[]);const m=async(y,S,b)=>{d("Saving...");try{await XE(y,S,b),s(await Uh()),d("Saved. Effective settings updated through SettingsStore.")}catch(T){const E=T instanceof Error?T.message:"Save failed";d(E.includes("fresh_passkey_required")?"Fresh passkey authentication required. Reopen login, authenticate, then retry.":E)}},g=async()=>{d("Resetting...");try{await qE(),s(await Uh()),d("Settings reset to defaults.")}catch(y){d(y instanceof Error?y.message:"Reset failed")}},_={autonomy:B0,permissions:xx,servers:BE,privacy:zE,notifications:Sm,models:gx,budgets:ME,memory:UE,display:_x,developer:DE,backup:LE};return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:"Settings"}),v.jsx("div",{className:"muted",children:"V2 settings surface. Sensitive changes remain protected by passkey fresh auth and CSRF."})]}),v.jsxs("a",{className:"primary-button",href:"/dashboard/security/passkeys",children:[v.jsx(PE,{size:16})," Passkeys"]})]}),v.jsx("div",{className:"settings-grid",children:t.map(y=>{const S=_[y.id]||B0;return v.jsxs("article",{className:"settings-tile",children:[v.jsx("div",{className:"settings-tile__icon",children:v.jsx(S,{size:18,"aria-hidden":"true"})}),v.jsxs("div",{children:[v.jsx("strong",{children:y.label}),v.jsx("p",{children:y.summary}),v.jsx("span",{className:"muted",children:y.status})]})]},y.id)})})]}),v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:"Operational Settings"}),v.jsx("div",{className:"muted",children:"Loaded from SettingsStore. POST changes use CSRF and fresh passkey protection."})]}),v.jsxs("div",{style:{display:"flex",gap:8},children:[v.jsx("a",{className:"secondary-button",href:"/api/settings/export",children:"Export"}),v.jsx("button",{className:"danger-button",onClick:g,type:"button",children:"Reset"})]})]}),f?v.jsx("div",{className:"attention-item","data-severity":f.includes("required")||f.includes("failed")?"warning":"info",children:f}):null,l?v.jsx("div",{className:"muted",children:"Loading settings..."}):null,v.jsxs("div",{className:"settings-editor",children:[p.map(y=>v.jsxs("label",{className:"settings-control",children:[v.jsxs("span",{children:[v.jsx("strong",{children:y.label}),v.jsxs("small",{children:[y.section,".",y.key]})]}),typeof y.value=="boolean"?v.jsx("input",{type:"checkbox",checked:y.value,onChange:S=>void m(y.section,y.key,S.currentTarget.checked)}):typeof y.value=="number"?v.jsx("input",{type:"number",value:y.value,onChange:S=>void m(y.section,y.key,Number(S.currentTarget.value))}):v.jsx("input",{value:String(y.value??""),onChange:S=>void m(y.section,y.key,S.currentTarget.value)})]},`${y.section}.${y.key}`)),!p.length&&!l?v.jsx("div",{className:"muted",children:"No simple editable settings were reported."}):null]})]}),v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Guardrails"})}),v.jsxs("div",{className:"metric-list",children:[v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Authentication"}),v.jsx("strong",{children:"Passkey-only in production"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Fresh auth"}),v.jsx("strong",{children:"Required for risk, approval, secrets, LLM, and dangerous operations"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Policy direction"}),v.jsx("strong",{children:"Settings can add restrictions; PolicyEngine must not be weakened by UI"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Legacy API"}),v.jsx("strong",{children:v.jsx("a",{href:"/api/settings",children:"Available for compatibility"})})]})]})]})]})}function v3(a){const t=new Set(["autonomous_loop_enabled","support_agent_enabled","self_dev_proposal_enabled","pc_server_enabled","android_server_enabled","browser_server_enabled","room_server_enabled","dev_server_enabled","clipboard_capture_enabled","camera_snapshot_enabled","display_privacy_mode","notifications_enabled","daily_budget_usd","monthly_budget_usd","memory_budget_tokens"]),n=[];for(const[s,l]of Object.entries(a))if(!(!l||typeof l!="object"||Array.isArray(l)))for(const[c,f]of Object.entries(l))!t.has(c)&&n.length>=24||(typeof f=="boolean"||typeof f=="number"||typeof f=="string")&&n.push({section:s,key:c,label:_3(c),value:f});return n.sort((s,l)=>Number(t.has(l.key))-Number(t.has(s.key))).slice(0,32)}function _3(a){return a.replace(/_/g," ").replace(/\b\w/g,t=>t.toUpperCase())}function y3({overview:a}){const t=a.servers.data.items||[],n=t.find(s=>s.server_id==="android-server");return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:"Systems"}),v.jsx("div",{className:"muted",children:"AI, PC, Android, Browser, Room, and Dev status with dependencies and recovery hints."})]}),v.jsx(or,{generatedAt:a.servers.generated_at,sourceUpdatedAt:a.servers.source_updated_at,stale:a.servers.stale})]}),v.jsx("div",{className:"topology-row","aria-label":"Server topology",children:t.map((s,l)=>v.jsxs("div",{className:"topology-node","data-status":String(s.status||"").toUpperCase(),children:[v.jsx("strong",{children:Hi(s.server_id)}),v.jsx("span",{children:s.mode||"unknown"}),l<t.length-1?v.jsx("i",{"aria-hidden":"true"}):null]},s.server_id))}),v.jsx("div",{className:"dependency-map","aria-label":"Server dependency map",children:t.map(s=>v.jsxs("div",{className:"dependency-map__row",children:[v.jsx("strong",{children:Hi(s.server_id)}),v.jsx("span",{children:x3(s).join(" / ")||"No dependencies reported"})]},`${s.server_id}-deps`))})]}),v.jsx("section",{className:"systems-grid",children:t.map(s=>v.jsxs("article",{className:"panel system-card",children:[v.jsxs("div",{className:"panel__header",children:[v.jsxs("div",{children:[v.jsx("h2",{children:Hi(s.server_id)}),v.jsx("div",{className:"muted mono",children:s.server_id})]}),v.jsx(zo,{status:s.status,detail:s.recovery_hint})]}),v.jsxs("div",{className:"metric-list",children:[v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Endpoint"}),v.jsxs("strong",{children:[s.host||"host",":",s.port||"-"]})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Mode"}),v.jsx("strong",{children:s.mode||"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Capabilities"}),v.jsx("strong",{children:s.registered_capabilities||"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Heartbeat age"}),v.jsx("strong",{children:s.heartbeat_age_seconds??"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Last healthy"}),v.jsx("strong",{children:S3(s)})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Version"}),v.jsx("strong",{children:s.version||"Not reported"})]}),v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Dependencies"}),v.jsx("strong",{children:ib(s)})]})]}),v.jsxs("div",{children:[v.jsx("div",{className:"muted",children:s.status_detail||s.degraded_reason||"No active issue reported."}),s.recovery_hint?v.jsx("div",{className:"recovery-hint",children:s.recovery_hint}):null]})]},s.server_id))}),v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Android Detail"})}),n?v.jsx(M3,{server:n}):v.jsx("p",{className:"muted",children:"Android status is not reported."})]})]})}function x3(a){const t=a.dependencies||{};return Object.entries(t).filter(([,n])=>typeof n=="boolean"||typeof n=="string"||typeof n=="number").slice(0,4).map(([n,s])=>`${n}:${String(s)}`)}function S3(a){const t=a.dependencies||{};return String(t.last_healthy_at||t.last_online_at||a.health_checked_at||t.last_seen||"Not reported")}function M3({server:a}){const t=a.dependencies||{},n=t.capability_availability||{},s=t.permission_status||{};return v.jsxs("div",{className:"android-detail",children:[v.jsxs("div",{className:"stat-grid",children:[v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Device"}),v.jsx("b",{children:String(t.device_model||"Not reported")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Connection"}),v.jsx("b",{children:String(a.mode||t.connection_mode||"Not reported")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Last seen"}),v.jsx("b",{children:String(t.last_seen||"Not reported")})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Active approvals"}),v.jsx("b",{children:Array.isArray(t.active_approvals)?t.active_approvals.length:0})]})]}),v.jsxs("div",{className:"grid grid--three",children:[v.jsxs("div",{children:[v.jsx("h3",{children:"Permissions"}),v.jsx("div",{className:"metric-list",children:Object.entries(s).length?Object.entries(s).map(([l,c])=>v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:l}),v.jsx("strong",{children:String(c)})]},l)):v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Status"}),v.jsx("strong",{children:"Not reported"})]})})]}),v.jsxs("div",{children:[v.jsx("h3",{children:"Capabilities"}),v.jsxs("div",{className:"metric-list",children:[Object.entries(n).slice(0,8).map(([l,c])=>v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{className:"mono",children:l.replace("android-server.","")}),v.jsx("strong",{children:String(c.available??"unknown")})]},l)),Object.entries(n).length?null:v.jsxs("div",{className:"metric-row",children:[v.jsx("span",{children:"Status"}),v.jsx("strong",{children:"Not reported"})]})]})]}),v.jsxs("div",{children:[v.jsx("h3",{children:"Recovery"}),v.jsx("p",{className:"muted",children:a.recovery_hint||"No recovery action needed."})]})]})]})}function E3({overview:a}){var m,g,_,y;const t=a.current_task.data,n=tb(a),s=t.steps||[],l=t.capability_id||String(((m=s.find(S=>String(S.status||"").toLowerCase()==="running"))==null?void 0:m.capability_id)||""),c=(a.approvals.data.pending||[]).filter(S=>S.task_id===t.task_id||S.capability_id===l),f=((_=(g=a.memory)==null?void 0:g.data)==null?void 0:_.summary)||((y=a.mind_summary.data)==null?void 0:y.memory)||{},d=a.usage.data||{},p=[...s].reverse().map(S=>b3(S)).find(Boolean);return v.jsxs("div",{className:"grid",children:[v.jsxs("section",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsxs("div",{children:[v.jsx("h2",{children:"Work"}),v.jsx("div",{className:"muted",children:"Tasks grouped by operational state. Active task detail is shown on the right."})]})}),v.jsx("div",{className:"tab-strip",role:"tablist","aria-label":"Work queues",children:n.map(S=>v.jsxs("button",{className:"tab-chip",type:"button","aria-selected":S.id==="active",children:[v.jsx("span",{children:S.label}),v.jsx("strong",{children:S.count})]},S.id))})]}),v.jsxs("section",{className:"work-layout",children:[v.jsxs("div",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsx("h2",{children:"Task List"})}),v.jsx("div",{className:"grid",children:t.task_id||t.title?v.jsxs("article",{className:"list-row","data-selected":"true",children:[v.jsxs("div",{children:[v.jsx("strong",{children:t.title||"Untitled task"}),v.jsxs("div",{className:"muted",children:[t.phase||"unknown"," / ",s.length," step(s)"]})]}),v.jsx("span",{className:"status-badge","data-status":String(t.phase||"ACTIVE").toUpperCase(),children:t.phase||"active"})]}):v.jsx("div",{className:"attention-item","data-severity":"normal",children:"No active task. Scheduled and historical queues will appear here when reported by Overview v3."})})]}),v.jsxs("div",{className:"panel",children:[v.jsx("div",{className:"panel__header",children:v.jsxs("div",{children:[v.jsx("h2",{children:"Task Detail"}),v.jsx("div",{className:"muted mono",children:t.task_id||"No task id"})]})}),v.jsxs("div",{className:"stat-grid",children:[v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Objective"}),v.jsx("b",{style:{fontSize:16},children:t.title||"Not reported"})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Phase"}),v.jsx("b",{children:t.phase||"Not reported"})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Current capability"}),v.jsx("b",{className:"mono",style:{fontSize:14},children:l||"Not reported"})]}),v.jsxs("div",{className:"stat",children:[v.jsx("span",{className:"muted",children:"Execution server"}),v.jsx("b",{children:l?Hi(of(l)):"Not reported"})]})]}),v.jsxs("div",{className:"task-narrative",children:[v.jsxs("div",{children:[v.jsx("span",{className:"muted",children:"Original instruction"}),v.jsx("strong",{children:String(t.title||t.task_id||"Not reported")})]}),v.jsxs("div",{children:[v.jsx("span",{className:"muted",children:"Current action"}),v.jsx("strong",{children:t.current_action||"Not reported"})]}),v.jsxs("div",{children:[v.jsx("span",{className:"muted",children:"Next action"}),v.jsx("strong",{children:t.next_action||"Not reported"})]}),v.jsxs("div",{children:[v.jsx("span",{className:"muted",children:"Blocked reason"}),v.jsx("strong",{children:t.blocked_reason||"Not blocked"})]}),v.jsxs("div",{children:[v.jsx("span",{className:"muted",children:"Latest result"}),v.jsx("strong",{children:p||"Not reported"})]})]}),v.jsxs("div",{className:"work-insight-grid","aria-label":"Task operational context",children:[v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Plan / Dependency"}),v.jsx("p",{className:"muted",children:s.length?`${s.length} step plan, executed through ${l?Hi(of(l)):"reported server"}.`:"No step plan reported."})]}),v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Approvals"}),v.jsx("p",{className:"muted",children:c.length?`${c.length} approval waiting for this task.`:"No approval currently blocks this task."})]}),v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Memories Used"}),v.jsx("p",{className:"muted",children:A3(f)})]}),v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Model / Cost"}),v.jsx("p",{className:"muted",children:String(d.summary||d.total_tokens||d.cost||"Not reported")})]}),v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Completion / Verification"}),v.jsx("p",{className:"muted",children:T3(s)||"No verification result reported."})]}),v.jsxs("div",{className:"mini-panel",children:[v.jsx("h3",{children:"Final Output"}),v.jsx("p",{className:"muted",children:String(t.final_output||t.result||"Not reported")})]})]}),v.jsxs("div",{className:"step-list",children:[s.map((S,b)=>v.jsxs("article",{className:"step-row",children:[v.jsx("span",{className:"step-index",children:b+1}),v.jsxs("div",{children:[v.jsx("strong",{children:String(S.description||S.capability_id||S.name||`Step ${b+1}`)}),v.jsx("div",{className:"muted mono",children:String(S.capability_id||S.name||"No capability reported")})]}),v.jsx("span",{className:"status-badge","data-status":String(S.status||"UNKNOWN").toUpperCase(),children:String(S.status||"unknown")})]},String(S.step_id||b))),s.length?null:v.jsx("div",{className:"attention-item","data-severity":"normal",children:"No step history reported."})]})]})]})]})}function b3(a){const t=a.result;if(!t)return"";if(typeof t=="string")return t.slice(0,160);if(typeof t=="object"){const n=t;return String(n.summary||n.status||n.message||JSON.stringify(n).slice(0,160))}return String(t)}function T3(a){const t=[...a].reverse().map(n=>n.verification||n.completion||n.postcondition).find(Boolean);if(!t)return"";if(typeof t=="string")return t;if(typeof t=="object"){const n=t;return String(n.status||n.summary||n.message||JSON.stringify(n).slice(0,140))}return String(t)}function A3(a){if(!a||typeof a!="object")return"Not reported";const t=a,n=["episodic","semantic","procedural","advanced"].map(s=>{const l=t[s];if(typeof l=="number"||typeof l=="string")return`${s}: ${l}`;if(l&&typeof l=="object"){const c=l;return`${s}: ${c.total||c.count||c.total_entries||c.total_episodes||"reported"}`}return""}).filter(Boolean);return n.length?n.join(", "):"Not reported"}const ky=[{id:"command",label:"Command Center",icon:OE,path:"/dashboard"},{id:"work",label:"Work",icon:RE,path:"/dashboard/work"},{id:"approvals",label:"Approvals",icon:xx,path:"/dashboard/approvals"},{id:"systems",label:"Systems",icon:_x,path:"/dashboard/systems"},{id:"mind",label:"Mind & Memory",icon:gx,path:"/dashboard/mind"},{id:"activity",label:"Activity",icon:mx,path:"/dashboard/activity"},{id:"settings",label:"Settings",icon:HE,path:"/settings"}];function C3(){var y;const a=window.location.pathname.startsWith("/display"),t=dx(),[n,s]=se.useState(window.location.pathname==="/chat"),[l,c]=se.useState([]),f=se.useMemo(()=>w3(window.location.pathname),[]),[d,p]=se.useState(f),m=_E({queryKey:["ui-overview",a?"display":"dashboard"],queryFn:()=>VE(a?"display":"dashboard"),refetchInterval:a?15e3:3e4}),g=se.useCallback(S=>{"schema_version"in S||c(b=>[S,...b].slice(0,10)),t.invalidateQueries({queryKey:["ui-overview"]})},[t]);if(Tx(g,!a),m.isLoading)return v.jsx(D3,{displayMode:a});if(m.isError||!m.data)return v.jsx(N3,{message:m.error instanceof Error?m.error.message:"Overview unavailable"});if(a)return v.jsx(f3,{overview:m.data});const _=m.data;return v.jsxs("div",{className:"app-shell",children:[v.jsxs("aside",{className:"side-nav",children:[v.jsxs("div",{className:"brand",children:[v.jsx("span",{className:"brand__name",children:"AEGIS"}),v.jsx("span",{className:"brand__sub",children:"Operational Console"})]}),v.jsx("nav",{className:"nav-list","aria-label":"Primary",children:ky.map(S=>{const b=S.icon;return v.jsxs("button",{className:"nav-button","aria-current":d===S.id?"page":void 0,onClick:()=>{p(S.id),window.history.pushState(null,"",S.path)},children:[v.jsx(b,{size:17,"aria-hidden":"true"}),S.label]},S.id)})})]}),v.jsxs("main",{className:"content",children:[v.jsxs("header",{className:"top-bar",children:[v.jsxs("div",{className:"page-title",children:[v.jsx("h1",{children:((y=ky.find(S=>S.id===d))==null?void 0:y.label)||"AEGIS"}),v.jsx("p",{children:"Live overview generated by Runtime managers, Policy, Approval, and Status services."})]}),v.jsxs("div",{style:{display:"flex",gap:12,alignItems:"center"},children:[v.jsx(zo,{status:String(_.core.data.health||"ONLINE")}),v.jsx(or,{generatedAt:_.generated_at,sourceUpdatedAt:_.freshness.source_updated_at,stale:_.freshness.stale}),v.jsx("button",{className:"icon-button",onClick:()=>s(!0),title:"Open chat",children:v.jsx(vx,{size:17,"aria-hidden":"true"})})]})]}),v.jsx(R3,{page:d,overview:_,recentEvents:l})]}),v.jsx(QE,{open:n,onClose:()=>s(!1)})]})}function R3({page:a,overview:t,recentEvents:n}){return a==="work"?v.jsx(E3,{overview:t}):a==="approvals"?v.jsx(hb,{overview:t}):a==="systems"?v.jsx(y3,{overview:t}):a==="mind"?v.jsx(p3,{overview:t}):a==="activity"?v.jsx(ZE,{overview:t,recentEvents:n}):a==="settings"?v.jsx(g3,{overview:t}):v.jsx(u3,{overview:t,recentEvents:n})}function w3(a){return a.includes("/work")?"work":a.includes("/approvals")?"approvals":a.includes("/systems")||a.includes("/servers")?"systems":a.includes("/mind")||a.includes("/memory")?"mind":a.includes("/activity")||a.includes("/audit")?"activity":a.includes("/settings")?"settings":"command"}function D3({displayMode:a}){return v.jsx("main",{className:a?"display-shell":"app-shell",style:{display:"grid",placeItems:"center"},children:v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"Loading AEGIS UI"}),v.jsx(Sm,{size:18})]}),v.jsx("p",{className:"muted",children:"Waiting for the normalized overview service."})]})})}function N3({message:a}){return v.jsx("main",{className:"display-shell",style:{display:"grid",placeItems:"center"},children:v.jsxs("section",{className:"panel",children:[v.jsxs("div",{className:"panel__header",children:[v.jsx("h2",{children:"AEGIS UI unavailable"}),v.jsx(zo,{status:"OFFLINE"})]}),v.jsx("p",{className:"muted",children:a})]})})}const U3=new sE({defaultOptions:{queries:{retry:1,staleTime:1e4}}});L1.createRoot(document.getElementById("root")).render(v.jsx(T1.StrictMode,{children:v.jsx(rE,{client:U3,children:v.jsx(C3,{})})}));
