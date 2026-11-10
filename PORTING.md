# GTNH 2.9.0-beta-3 port notes

## Dependency changes relevant to RemoteOC

| Component | GTNH 2.8.0 | GTNH 2.9.0-beta-3 |
| --- | --- | --- |
| Applied Energistics 2 | `rv3-beta-690-GTNH` | `rv3-beta-1050-GTNH` |
| AE2 Fluid Crafting | `1.4.115-gtnh` | `1.5.106-gtnh` |
| OpenComputers | `1.11.19-GTNH` | `1.12.61-GTNH` |

Sources: [2.8.0 manifest](https://github.com/GTNewHorizons/DreamAssemblerXXL/blob/master/releases/manifests/2.8.0.json), [2.9.0-beta-3 manifest](https://github.com/GTNewHorizons/DreamAssemblerXXL/blob/master/releases/manifests/2.9.0-beta-3.json), and the [official beta 3 release](https://github.com/GTNewHorizons/GT-New-Horizons-Modpack/releases/tag/2.9.0-beta-3).

## Breaking API changes handled here

OpenComputers' AE2 integration adopted AE2's stack API between the versions above. The changes that affect this project are:

- Craftables now represent multiple AE2 stack types, including native fluids.
- `getCraftable(details, type)` was added for an exact typed lookup.
- A craftable's output method changed from `getItemStack()` to `getStack()`.
- Crafting amounts changed from 32-bit integers to long values.
- Native fluid entries now expose `name`, `label`, `amount`, `size`, and `isCraftable`.

The upstream implementation is in OpenComputers' [`NetworkControl.scala`](https://github.com/GTNewHorizons/OpenComputers/blob/1.12.61-GTNH/src/main/scala/li/cil/oc/integration/appeng/NetworkControl.scala); the initial stack API integration is [commit `6782e15`](https://github.com/GTNewHorizons/OpenComputers/commit/6782e15f3).

## Port behavior

- `ae.getAllItems()` and the legacy-named `ae.getAllSilempleItems()` return both items and native fluids with a `stackType` discriminator when no filter is supplied. With an item filter, they return only matching items.
- `ae.requestItem()` performs a typed item lookup unless a label is supplied. Label-sensitive requests use `getCraftables(filter)` to distinguish NBT-backed items such as different `fluid_drop` recipes sharing the same name and damage.
- `ae.requestFluid()` performs a typed native-fluid lookup and takes an amount in mB.
- The web UI displays, filters, selects, and orders native fluids.
- Automation actions persist `stack_type` and route native-fluid orders correctly.
- Docker Compose builds the checked-out source instead of pulling the old 2.8 images.

The bundled 2.8 metadata database remains an optional name/icon lookup. Live AE data is authoritative, so new 2.9 entries still work and fall back to their in-game label/default icon when no old metadata exists.
