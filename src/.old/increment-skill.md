@models:
  name: increment
  description: "Adds 1 to input x."
  inputs: { x: "number" }
  outputs: { result: "number" }
  implementation: "Scheme"

```mermaid
graph TD;
    A[Input x] --> B[Increment Function];
    B --> C[Output result];
```

```scheme
(define-skill increment
  (lambda (x)
    (+ x 1)))
```