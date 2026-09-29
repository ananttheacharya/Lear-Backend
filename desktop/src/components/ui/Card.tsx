import React from 'react';
import './ui.css';
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> { variant?: 'default'|'elevated'|'outlined'|'glass'; padding?: 'none'|'sm'|'md'|'lg'; hoverable?: boolean; clickable?: boolean; }
export function Card({variant='default',padding='md',hoverable=false,clickable=false,className='',children,...props}: CardProps) { return <div className={`ui-card ui-card--${variant} ui-card--p-${padding} ${hoverable?'ui-card--hoverable':''} ${clickable?'ui-card--clickable':''} ${className}`} {...props}>{children}</div>; }
