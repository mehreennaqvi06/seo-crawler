# Graph Traversal Used in the Crawler

## Overview

The crawler models a website as a graph.

- Each webpage is treated as a node.
- Each hyperlink between pages is treated as an edge.

## Traversal Method

The crawler uses Breadth First Search (BFS).

Implementation details:

- A queue is used to store URLs waiting to be crawled.
- The first URL added to the queue is processed first.
- Newly discovered URLs are added to the end of the queue.
- Visited URLs are tracked to prevent revisiting the same page.

## Why BFS

BFS explores pages level by level starting from the seed URL.

For example:

Home
├── About
├── Blog
└── Contact

The crawler visits:

1. Home
2. About, Blog, Contact
3. Links discovered from those pages

This approach is commonly used in web crawling because it provides broad coverage of a site while avoiding deep traversal into a single path.