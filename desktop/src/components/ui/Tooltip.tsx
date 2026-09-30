import React, { useId, useState } from 'react';
import './ui.css';
export interface TooltipProps {content:string|React.ReactNode; side?:'top'|'right'|'bottom'|'left'; delay?:number; children:React.ReactNode;}
export function Tooltip({content,side='top',delay=300,children}:TooltipProps){const [show,setShow]=useState(false);const id=useId();let timer:number;const open=()=>{timer=window.setTimeout(()=>setShow(true),delay)};const close=()=>{window.clearTimeout(timer);setShow(false)};return <span className="ui-tooltip-wrap" onMouseEnter={open} onMouseLeave={close} onFocus={open} onBlur={close} aria-describedby={show?id:undefined}>{children}{show&&<span id={id} role="tooltip" className={`ui-tooltip ui-tooltip--${side}`}>{content}</span>}</span>;}
