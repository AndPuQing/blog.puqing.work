import React from 'react';
// Import the original mapper
import MDXComponents from '@theme-original/MDXComponents';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import CodeBlock from '@theme/CodeBlock';
import Highlight from '@site/src/components/Highlight';

export default {
    // Re-use the default mapping
    ...MDXComponents,
    // Map the "<Highlight>" tag to our Highlight component
    // `Highlight` will receive all props that were passed to `<Highlight>` in MDX
    Highlight,
    // Map the "<Tabs>" tag to our Tabs component
    Tabs,
    // Map the "<TabItem>" tag to our TabItem component
    TabItem,
    // Map the "<CodeBlock>" tag to our CodeBlock component
    CodeBlock,
};