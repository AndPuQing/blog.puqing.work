import React from 'react';
// Import the original mapper
import MDXComponents from '@theme-original/MDXComponents';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import Highlight from '@site/src/components/Highlight';
import Geogebra from '@site/src/components/Geogebra';

export default {
    // Re-use the default mapping
    ...MDXComponents,
    // Map the "<Highlight>" tag to our Highlight component
    // `Highlight` will receive all props that were passed to `<Highlight>` in MDX
    Highlight,
    // Map the "<Geogebra>" tag to our Geogebra component
    Geogebra,
    // Map the "<Tabs>" tag to our Tabs component
    Tabs,
    // Map the "<TabItem>" tag to our TabItem component
    TabItem,
};