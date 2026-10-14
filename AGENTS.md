# projectkoios-workflow

This repo owns workflow execution and process/state orchestration.

Repository routing is documented in `projectkoios-bootstrap/maps/repositories.md`.
This repo does not own cross-repo routing or product architecture policy.

## Runtime interfaces

Do not recommend `typing.Protocol` in place of abstract base classes for runtime-enforced interfaces. Protocols are static structural-typing aids and do not enforce implementation contracts at runtime. Prefer nominal ABCs when the boundary requires runtime validation or enforcement.
