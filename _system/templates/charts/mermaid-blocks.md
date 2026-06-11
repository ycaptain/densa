# Mermaid skeletons (handDrawn header is mandatory)

Every Mermaid chart in this vault opens with the same config header.
Copy the relevant skeleton; replace placeholder nodes. Node labels
≤12 chars (`<br/>` to wrap); ≤8 nodes horizontally.

## Layered causal DAG (多因素 → 机制 → 现状)

The canonical shape for "multiple factors with hierarchy + causality".
Feedback edges (`<-->`) are the value — make loops visible.

````markdown
```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
flowchart TD
    subgraph distal["远端因素"]
        A["因素A"]
        B["因素B"]
    end
    subgraph mech["中介机制"]
        C["机制C"]
        D["机制D"]
    end
    subgraph now["现状"]
        E["现状E"]
    end
    A --> C
    B --> D
    C --> E
    D --> E
    C <--> D
```
````

For ≥6 nodes or crossing edges, add `%% elk %%` as the first line
inside the code block (Mermaid ELK Renderer plugin).

## Stage-arc timeline (阶段弧)

````markdown
```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
timeline
    title 弧线:<thread 名>
    section 阶段一
        2026-03 : 事件
    section 阶段二
        2026-04 : 事件 : 事件
```
````

## Quadrant (priority × proof, 或任意二维定位)

````markdown
```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
quadrantChart
    title 技能:优先级 × 证明强度
    x-axis 证明弱 --> 证明强
    y-axis 低优先 --> 高优先
    quadrant-1 主攻区
    quadrant-2 补证据
    quadrant-3 搁置
    quadrant-4 维持
    "技能A": [0.3, 0.8]
```
````
