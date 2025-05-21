@models:
  name: PLN
  description: "Executes probabilistic inference over hypergraph patterns."
  inputs:
    - premises: "Hypergraph assertions"
    - query: "Inference target"
  outputs:
    - result: "Probabilistic inference result"
  implementation: "Scheme"

```mermaid
flowchart TD
    A[Premises] --> B[PLN Inference Engine]
    D[Query] --> B
    B --> C[Inference Result]
```

```scheme
(define-skill PLN
  (lambda (premises query)
    (pln-infer premises query)))
```