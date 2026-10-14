# `projectkoios.workflow.registry` implementation

## Responsibility

Use content-addressed immutable rows plus explicit namespace/name/version uniqueness. The same name/version with different content is a conflict. Deprecation is metadata and cannot invalidate retained plans.

Compatibility ranges may help installation planning, but compilation and run start pin exact descriptor digests. Registration, resolution, and availability queries are typed action operations with separate administrative scopes.
