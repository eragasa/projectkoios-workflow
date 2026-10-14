# `WorkflowPluginManifestProvider` schematic

## Responsibility

```text
package/version/wheel identity
+ entry-point identities
+ action/provider/schema descriptors
+ environment and capability digest
                 │
                 ▼
       WorkflowPluginManifest
```

The worker or exporter submits this record to the service. The service never imports the package to reconstruct it.
