# Use Case Tree Mindmap Diagram Rules

## Rules

1. Each use case page must display a mindmap diagram centered on the
   current use case.

2. The central node must show the current use case title with a link
   to its page. The central node is the only node that is boxed.

3. The left side must show parent use case(s) and grandparent use
   case(s), if any exist. If a use case has multiple parents, all
   parents must be shown, with secondary parents connected with a
   dotted line. Grandparents must be shown to provide context. If a
   node does not have a parent, nothing must be shown on the left
   side.

4. The right side must show direct children and grandchildren of the
   current use case, but not great-grandchildren.

5. Children must be sorted alphabetically by title.

6. There is no such thing as a single root node. Every use case in a
   direct subdirectory of `docs/use-case` is a root node in itself
   (such as `client-360`). Do not ever show a parent to the left of
   such a node.

7. For each direct parent of the central node, all of that parent's
   direct children must be shown (siblings of the central node),
   providing context about related use cases at the same level.

