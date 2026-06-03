# Graph Traversal Used

## Approach

The crawler uses Breadth First Search (BFS) to traverse pages within a website.

Each page is treated as a node in a graph.
Each hyperlink between pages is treated as an edge.

A queue is used to maintain the BFS traversal order.

## Why BFS?

BFS explores pages level by level from the starting URL.

Advantages:

- Finds nearby pages first.
- Prevents deep traversal into a single section.
- Easy to enforce page limits.
- Commonly used by search engine crawlers.

## Algorithm

1. Add starting URL to queue.
2. Pop URL from queue.
3. Visit page and extract links.
4. Add unvisited internal links to queue.
5. Repeat until queue is empty or page limit reached.

## Time Complexity

O(V + E)

Where:
- V = number of pages
- E = number of links

## Data Structures

- Queue
- Visited Set
- Results List