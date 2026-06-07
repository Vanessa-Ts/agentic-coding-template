# OpenAPI Skill

**Trigger paths**: `openapi*.yml`, `openapi*.json`, `docs/api/**`
**Trigger keywords**: OpenAPI, swagger, API spec, generate code from spec, spec-first, contract-first

---

## OpenAPI 3.x — YAML structure

```yaml
openapi: "3.1.0"
info:
  title: My Service API
  version: "1.0.0"

paths:
  /items:
    post:
      operationId: createItem
      summary: Create a new item
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ItemCreate"
      responses:
        "201":
          description: Created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Item"
        "422":
          description: Validation error
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/HTTPValidationError"

components:
  schemas:
    ItemCreate:
      type: object
      required: [name]
      properties:
        name:
          type: string
          minLength: 1
        description:
          type: string
    Item:
      allOf:
        - $ref: "#/components/schemas/ItemCreate"
        - type: object
          required: [id, created_at]
          properties:
            id:
              type: string
              format: uuid
            created_at:
              type: string
              format: date-time
```

---

## Generating Pydantic models from a spec

Use `datamodel-code-generator` (uv add --dev datamodel-code-generator):

```bash
datamodel-codegen \
  --input openapi.yml \
  --input-file-type openapi \
  --output src/app/models/generated.py \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated \
  --use-field-description
```

Review generated output — it may need manual cleanup (remove `Optional` in favour of `X | None`, fix `model_config`).

---

## Generating FastAPI route stubs from a spec

Use `fastapi-codegen` (uv add --dev fastapi-codegen):

```bash
fastapi-codegen \
  --input openapi.yml \
  --output src/app/routes/generated/
```

Generated stubs are a starting point only — wire them into `main.py`, add `Depends()`, replace `pass` with real store calls.

---

## FastAPI auto-generates OpenAPI — leverage it

FastAPI produces `/openapi.json` automatically. To export:

```bash
python3 -c "
import json, sys
sys.path.insert(0, 'src')
from app.main import app
print(json.dumps(app.openapi(), indent=2))
" > openapi.json
```

Use this as the source of truth for client SDK generation.

---

## Extending an existing spec

1. Add new paths/components to the YAML — never delete existing ones without a deprecation cycle.
2. Re-run `datamodel-codegen` and diff against existing models.
3. Apply only the new models; keep hand-written extensions.
4. Validate with `openapi-spec-validator` (uv add --dev openapi-spec-validator):

```bash
python3 -m openapi_spec_validator openapi.yml
```

---

## Rules

- Every path must have at least one `4xx` response documented.
- `operationId` must be camelCase and unique across the spec.
- Reuse `$ref` components rather than inlining duplicate schemas.
- Commit `openapi.yml` alongside code — treat it as part of the API contract.
