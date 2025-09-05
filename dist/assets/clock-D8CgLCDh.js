import{i as M,u as T,r as k,c as m,a as w,b as o,g as j,p as f,t as b,C as U,h as B,j as L,D as g}from"./index-XUB9a-8Y.js";const E={class:"relative"},$={class:"bg-brutal-cyan border-4 border-blue-600 shadow-brutal p-2 hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"},D={key:0,class:"h-8 w-8 overflow-hidden"},N=["src","alt"],H={key:1,class:"h-8 w-8 flex items-center justify-center"},I={class:"text-blue-600 font-black text-lg uppercase"},S={class:"bg-brutal-yellow p-4 border-b-4 border-blue-600"},V={class:"font-black text-gray-800 text-lg uppercase truncate"},z={class:"font-bold text-gray-600 text-sm truncate"},G={__name:"UserAvatar",setup(t){const r=M(),e=T(),s=k(!1),i=k(!1);let a=null;const n=()=>e.user?e.user.name&&e.user.name!==e.user.email?e.user.name:e.user.email?e.user.email.split("@")[0]:"未知用户":"未知用户",v=()=>{const h=n();if(h==="未知用户")return"?";const l=h.trim().split(/\s+/);return l.length>=2?(l[0][0]+l[1][0]).toUpperCase():h[0].toUpperCase()},u=()=>{a&&(clearTimeout(a),a=null),s.value=!0},d=()=>{a=setTimeout(()=>{s.value=!1},100)},p=()=>{a&&(clearTimeout(a),a=null)},C=()=>{s.value=!1},A=async()=>{s.value=!1,e.logout(),await r.push("/login")};return(h,l)=>(w(),m("div",E,[o("div",{onMouseenter:u,onMouseleave:d,class:"cursor-pointer"},[o("div",$,[f(e).user?.avatar_url?(w(),m("div",D,[o("img",{src:f(e).user.avatar_url,alt:n(),class:"h-8 w-8 object-cover",onError:l[0]||(l[0]=R=>i.value=!0)},null,40,N)])):(w(),m("div",H,[o("span",I,b(v()),1)]))])],32),j(o("div",{onMouseenter:p,onMouseleave:C,class:L(["absolute right-0 z-10 mt-2 w-64 bg-white border-4 border-blue-600 shadow-brutal-lg transform transition-all duration-200",s.value?"opacity-100 scale-100":"opacity-0 scale-95 pointer-events-none"])},[o("div",S,[o("div",V,b(n()),1),o("div",z,b(f(e).user?.email||"未设置邮箱"),1)]),o("div",{class:"p-2"},[o("button",{onClick:A,class:"w-full bg-brutal-red border-4 border-blue-600 shadow-brutal-sm p-3 font-black text-gray-800 uppercase text-sm hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center"},[...l[1]||(l[1]=[o("svg",{class:"w-4 h-4 mr-2",fill:"none",stroke:"currentColor",viewBox:"0 0 24 24"},[o("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"})],-1),B(" 退出登录 ",-1)])])])],34),[[U,s.value]])]))}};/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const y=t=>t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),Z=t=>t.replace(/^([A-Z])|[\s-_]+(\w)/g,(r,e,s)=>s?s.toUpperCase():e.toLowerCase()),F=t=>{const r=Z(t);return r.charAt(0).toUpperCase()+r.slice(1)},O=(...t)=>t.filter((r,e,s)=>!!r&&r.trim()!==""&&s.indexOf(r)===e).join(" ").trim(),_=t=>t==="";/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var c={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const P=({name:t,iconNode:r,absoluteStrokeWidth:e,"absolute-stroke-width":s,strokeWidth:i,"stroke-width":a,size:n=c.width,color:v=c.stroke,...u},{slots:d})=>g("svg",{...c,...u,width:n,height:n,stroke:v,"stroke-width":_(e)||_(s)||e===!0||s===!0?Number(i||a||c["stroke-width"])*24/Number(n):i||a||c["stroke-width"],class:O("lucide",u.class,...t?[`lucide-${y(F(t))}-icon`,`lucide-${y(t)}`]:["lucide-icon"])},[...r.map(p=>g(...p)),...d.default?[d.default()]:[]]);/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const x=(t,r)=>(e,{slots:s,attrs:i})=>g(P,{...i,...e,iconNode:r,name:t},s);/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J=x("activity",[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]]);/**
 * @license lucide-vue-next v0.542.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Q=x("clock",[["path",{d:"M12 6v6l4 2",key:"mmk7yg"}],["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}]]);export{J as A,Q as C,G as _,x as c};
