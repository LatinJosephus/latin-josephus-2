/** Serialize an artifact's repository-relative path without changing its target. */
import path from 'node:path';

export function repositoryRelativeReportPath(root, artifact, filesystemPath = path) {
  return filesystemPath.relative(root, artifact).split(filesystemPath.sep).join('/');
}
