import React from 'react';
import { useColorMode } from "@docusaurus/theme-common";

export default function Highlight({ children, color }) {
    const isDarkTheme = useColorMode().colorMode === 'dark';
    color = color ? color : '#ffec99';
    if (isDarkTheme) {
        color = '#ff9c00';
    }
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