import React, { useEffect } from 'react'
import ReactECharts from 'echarts-for-react';
import { useColorMode } from "@docusaurus/theme-common";

interface GraphCategory {
    name: string;
    keyword: string;
    base: string;
}

interface GraphNode {
    name: string;
    value: number;
    category: number; // index of category 0 = page, other = tag
    permalink: string;
}

interface GraphLink {
    source: number;
    target: number;
}

interface Graph {
    categories: GraphCategory[];
    nodes: GraphNode[];
    links: GraphLink[];
}

function getGraph(blogPosts: readonly []) {
    const graph: Graph = {
        categories: [],
        nodes: [],
        links: []
    };
    const page_nodes = blogPosts.map((post, index) => {
        return {
            name: post.metadata.title,
            value: 1,
            category: 0,
            permalink: post.metadata.permalink,
            symbolSize: 5,
        }
    }
    );
    var tag_nodes = blogPosts.map((post, index) => {
        return post.metadata.tags.map((tag, index) => {
            return {
                name: tag.label,
                value: 1,
                category: 1,
                permalink: tag.permalink
            }
        }
        );
    }
    );
    const tag_nodes_flat = [].concat.apply([], tag_nodes);
    const tag_nodes_flat_unique = [...new Set(tag_nodes_flat.map(v => JSON.stringify(v)))].map(v => JSON.parse(v));
    const tag_nodes_index = tag_nodes_flat_unique.map((tag, index) => {
        return {
            name: tag.name,
            symbolSize: 5 + tag_nodes_flat.filter((tag_node) => tag_node.name === tag.name).length, // count
            category: 1 + index,
            permalink: tag.permalink,
        }
    }
    );
    const nodes = page_nodes.concat(tag_nodes_index); // page nodes + tag nodes
    // for each nodes add id
    nodes.forEach((node, index) => {
        node['id'] = index;
    });
    const links = [].concat.apply([], blogPosts.map((post, index: number) => {
        return post.metadata.tags.map((tag, _: number) => {
            return {
                source: index,
                target: page_nodes.length + tag_nodes_flat_unique.findIndex((tag_node) => tag_node.name === tag.label),
            }
        }
        );
    }
    ));
    const categories = [
        ...tag_nodes_index.map((tag, index) => {
            return {
                name: tag.name,
                keyword: tag.name,
                base: 'tag',
            }
        }
        )
    ];
    graph.categories = categories;
    graph.nodes = nodes;
    graph.links = links;
    return graph;
}

export default function GraphCharts(props) {
    const isDarkTheme = useColorMode().colorMode === 'dark';
    const graph = getGraph(props.blogPosts);
    const chartRef = React.useRef(null);
    console.log(graph);
    const option = {
        animationDuration: 1500,
        animationEasingUpdate: 'quinticInOut',
        series: [
            {
                name: 'Graph',
                type: 'graph',
                layout: 'force',
                data: graph.nodes,
                links: graph.links,
                categories: graph.categories,
                roam: true,
                draggable: true,
                label: {
                    position: 'right',
                    formatter: '{b}'
                },
                force: {
                    repulsion: 100
                },
            }
        ]
    };
    useEffect(() => {
        window.addEventListener('resize', () => {
            chartRef.current.getEchartsInstance().resize();
        }
        );
        chartRef.current.getEchartsInstance().setOption(option);
    }, [graph]
    );

    return (
        <div style={{ height: '800px', width: '90%', margin: 'auto' }}
        ><ReactECharts
                ref={chartRef}
                option={option}
                notMerge={true}
                lazyUpdate={true}
                theme={isDarkTheme ? 'dark' : 'light'}
                opts={{ renderer: 'svg' }}
                style={{ height: '100%', width: '100%' }}
            // onChartReady={this.onChartReadyCallback}
            /></div>
    )
}
