import React from 'react';
import { Button } from './Button';
import './ui.css';
export interface EmptyStateProps {icon:React.ReactNode; title:string; description:string; action?:{label:string;onClick:()=>void};}
export function EmptyState({icon,title,description,action}:EmptyStateProps){return <div className="ui-empty"><div className="ui-empty__icon">{icon}</div><h3>{title}</h3><p>{description}</p>{action&&<Button variant="primary" size="sm" onClick={action.onClick}>{action.label}</Button>}</div>;}
