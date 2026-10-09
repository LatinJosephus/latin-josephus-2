# Initial preparation attempts

The first baseline archive extraction reached the existing assignment-owned runtime directory, but Python's Windows realpath check under the filesystem sandbox returned WinError5. This was a tool permission failure, not a missing source or baseline archive. Preparation was resumed with the same commit and paths in an approved execution context.

The first Docker attempt was started before the preparation failure was handled. Its integration build completed, but the empty baseline mount caused the baseline dependency step to fail with `Could not locate Gemfile`; the container exited1 and removed itself. A later stop call found no container. This attempt is not counted as certification. Its disposable output is preserved in the owned runtime `build-attempt-1`, and a new complete two-source build was started after successful archive extraction. No worker's container or server was stopped.

A helper-copy attempt also stopped at PowerShell argument parsing before executing Python. The helper was subsequently copied with native literal-path operations and its two local path changes were applied directly. No certified source file or production code was changed by either preparation correction.
