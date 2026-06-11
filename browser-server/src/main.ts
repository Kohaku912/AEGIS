/**
 * Browser Server — entry point.
 *
 * Starts the gRPC server, initializes the Playwright browser,
 * registers capabilities with AEGIS Core, and handles graceful shutdown.
 */

import { loadConfig } from "./config.js";
import { startGrpcServer, shutdownGrpcServer } from "./grpc_server.js";
import { initBrowser, shutdownBrowser } from "./browser_context.js";
import { registerCapabilities } from "./capability_registration.js";
import { logger, setLogLevel } from "./logging.js";

async function main(): Promise<void> {
  const config = loadConfig();
  setLogLevel(config.logLevel as Parameters<typeof setLogLevel>[0]);

  logger.info("AEGIS Browser Server starting...");
  logger.info(`gRPC: ${config.host}:${config.port}`);
  logger.info(`AEGIS Core: ${config.aegisCoreAddress}`);

  // Initialize Playwright browser
  try {
    await initBrowser(config);
  } catch (err) {
    logger.error(`Failed to initialize browser: ${String(err)}`);
    logger.warn("Continuing without browser — observe/action RPCs will fail.");
  }

  // Start gRPC server
  startGrpcServer(config);

  // Register capabilities with AEGIS Core (non-blocking)
  registerCapabilities(config).catch((err) => {
    logger.warn(`Capability registration failed: ${String(err)}`);
  });

  // Graceful shutdown
  const shutdown = async () => {
    logger.info("Shutting down...");
    await shutdownGrpcServer();
    await shutdownBrowser();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);

  logger.info("Browser Server ready.");
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
