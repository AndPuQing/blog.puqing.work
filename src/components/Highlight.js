import React from 'react';

export default function Highlight({ children, color }) {
    color = color ? color : '#ffec99';
    return (
        <span
            style={{
                backgroundColor: color,
                borderRadius: '6px',
                padding: '0.2rem',
            }}>
            {children}
        </span>
    );
}