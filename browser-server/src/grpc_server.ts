/**
 * gRPC Server — serves the BrowserServer service.
 *
 * Phase 2.1: Skeleton with HealthCheck only.
 * Other RPCs return UNIMPLEMENTED.
 * Full implementation in Phase 2.2+.
 */

import {
  type Server,
  type ServerCredentials,
  Server as GrpcServer,
  ServerCredentials as GrpcServerCredentials,
  loadPackageDefinition,
} from "@grpc/grpc-js";
import { loadSync } from "@grpc/proto-loader";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import type { BrowserServerConfig } from "./config.js";
import { logger } from "./logging.js";
import { isBrowserAlive } from "./browser_context.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let server: Server | null = null;

export interface HealthCheckResponse {
  status: { code: number; message: string };
  serverStatus: number;
  uptimeMs: number;
  version: string;
}

const startTime = Date.now();

/** Start the gRPC server. */
export function startGrpcServer(config: BrowserServerConfig): Server {
  const protoPath = join(__dirname, "..", "..", "protos", "aegis");

  const packageDefinition = loadSync(
    [join(protoPath, "common.proto"), join(protoPath, "browser_server.proto")],
    {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true,
    },
  );

  const proto = loadPackageDefinition(packageDefinition) as Record<string, unknown>;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const aegisProto = proto["aegis"] as any;
  const serviceDefinition = aegisProto.BrowserServer.service;

  server = new GrpcServer();

  const implementation = {
    HealthCheck: (
      _call: unknown,
      callback: (err: null, response: HealthCheckResponse) => void,
    ) => {
      callback(null, {
        status: { code: 0, message: "ok" },
        serverStatus: isBrowserAlive() ? 1 : 2,
        uptimeMs: Date.now() - startTime,
        version: "0.1.0",
      });
    },

    OpenPage: unimplemented("OpenPage"),
    GetDomSnapshot: unimplemented("GetDomSnapshot"),
    GetScreenshot: unimplemented("GetScreenshot"),
    ExtractPageText: unimplemented("ExtractPageText"),
    GetNetworkLog: unimplemented("GetNetworkLog"),
    Click: unimplemented("Click"),
    FillForm: unimplemented("FillForm"),
    DownloadFile: unimplemented("DownloadFile"),
  };

  server.addService(serviceDefinition, implementation);

  const address = `${config.host}:${config.port}`;
  server.bindAsync(
    address,
    GrpcServerCredentials.createInsecure(),
    (err: Error | null, port: number) => {
      if (err) {
        logger.error(`Failed to bind gRPC server: ${err.message}`);
        return;
      }
      logger.info(`gRPC server listening on ${config.host}:${port}`);
    },
  );

  return server;
}

/** Gracefully shut down the gRPC server. */
export function shutdownGrpcServer(): Promise<void> {
  return new Promise((resolve) => {
    if (!server) {
      resolve();
      return;
    }
    server.tryShutdown(() => {
      logger.info("gRPC server stopped.");
      resolve();
    });
  });
}

function unimplemented(name: string) {
  return (
    _call: unknown,
    callback: (err: { code: number; message: string }) => void,
  ) => {
    callback({
      code: 12, // UNIMPLEMENTED
      message: `${name} not yet implemented`,
    });
  };
}
