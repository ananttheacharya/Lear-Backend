import React from 'react';
import './ui.css';
export interface BadgeProps { variant?: 'default'|'success'|'warning'|'error'|'info'|'brand'; size?: 'sm'|'md'; dot?: boolean; children: React.ReactNode; }
export function Badge({variant='default',size='md',dot=false,children}: BadgeProps) { return <span className={`ui-badge ui-badge--${variant} ui-badge--${size}`}>{dot&&<span className="ui-badge__dot"/>}{children}</span>; }
