# External Data — User-Managed, Read-Only

Files in this directory are original external inputs, typically copied as-is from customers or uploaded by users. They are not project files or project-generated output.

- Agents and project tooling may read these files, but must never edit, overwrite, rename, move, delete, format, normalize, or otherwise modify them.
- Only users may add, replace, organize, or modify files in this directory, and only through direct user action.
- Do not generate outputs, temporary files, caches, metadata, or sidecar files anywhere in this directory.
- Write project-generated and reproducible artifacts under `data/processed/` instead.
- Preserve every external input exactly. If a task would require changing anything here, stop and ask the user to make the change directly.

